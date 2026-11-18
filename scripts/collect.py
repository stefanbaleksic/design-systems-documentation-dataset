#!/usr/bin/env python3
"""Collect evidence for each dataset record into evidence/<id>.json.

For every record in data/design_systems.csv:
  * repo_url on github.com: GitHub REST API. Records the repository's pushed_at (UTC), archived
    flag, SPDX licence id and the newest tag name.
  * docs_url: the page is fetched (redirects followed). Records the final URL, HTTP status and a
    SHA-256 of the first MAX_BODY_BYTES of the body. The body itself is not stored.

Every attempt is written, including failures, so no record is silently left out. A failed request
is stored with its error text; the record's status becomes "failed" or "partial".

Credentials: GITHUB_TOKEN, if set, is read from the environment and used only as an
Authorization header. It is never written to a file, log or report.

Usage:
    python3 scripts/collect.py                   collect all records
    python3 scripts/collect.py --ids 55,94       collect only these record IDs
    python3 scripts/collect.py --dry-run         list what would be fetched; no requests, no files
    python3 scripts/collect.py --delay 1.0       seconds to wait between requests

Standard library only.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import detect_licence_text, format_utc, latest_stable_tag, parse_iso_to_utc, to_utc  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "design_systems.csv")
EVIDENCE_DIR = os.path.join(ROOT, "evidence")
MAX_BODY_BYTES = 2 * 1024 * 1024
USER_AGENT = "design-systems-dataset-collector/1.0 (+https://github.com/)"
GITHUB_REPO_RE = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$")
SCHEMA = "evidence/1"


def now_utc():
    return to_utc(dt.datetime.now(dt.timezone.utc))


def http_fetch(url, headers, timeout):
    """Fetch a URL. Returns (status, body_bytes, final_url, content_type). Raises on network error."""
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (https only, checked by caller)
        body = response.read(MAX_BODY_BYTES)
        return response.status, body, response.geturl(), response.headers.get("Content-Type", "")


def github_repo_of(repo_url):
    """Return (owner, repo) for a github.com repository URL, or None."""
    match = GITHUB_REPO_RE.match((repo_url or "").strip())
    return (match.group(1), match.group(2)) if match else None


def _git_error(exc):
    """Short, credential-free description of a git failure."""
    if isinstance(exc, subprocess.CalledProcessError):
        first = (exc.stderr or b"").decode("utf-8", "replace").strip().splitlines()
        return "git exit %d: %s" % (exc.returncode, first[0][:200] if first else "no output")
    if isinstance(exc, subprocess.TimeoutExpired):
        return "git timed out"
    return "%s: %s" % (type(exc).__name__, str(exc)[:200])


def is_https(url):
    return url.lower().startswith("https://")


def git_run(args, cwd=None, timeout=120):
    """Run git and return stdout. Raises CalledProcessError or TimeoutExpired."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(["git"] + args, cwd=cwd, env=env, timeout=timeout,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return result.stdout.decode("utf-8", "replace")


class Collector:
    def __init__(self, fetch=http_fetch, delay=0.0, timeout=20.0, token=None, clock=now_utc,
                 repo_source="api", git=git_run):
        self.fetch = fetch
        self.delay = delay
        self.timeout = timeout
        self.token = token
        self.clock = clock
        self.requests_made = 0
        self.repo_source = repo_source
        self.git = git

    def collect_repo_git(self, owner, repo):
        """Repository facts over git. The URL is never given credentials."""
        url = "https://github.com/%s/%s" % (owner, repo)
        result = {"api": {"error": None, "method": "git", "fetched_at_utc": format_utc(self.clock())},
                  "tags_api": {"error": None, "method": "git"},
                  "pushed_at_utc": None, "archived": None, "spdx_licence": None, "licence_file": None,
                  "licence_detection": None, "default_branch": None, "latest_tag": None, "tag_count": 0}
        tmp = tempfile.mkdtemp(prefix="collect-git-")
        try:
            try:
                head = self.git(["ls-remote", "--symref", url, "HEAD"], timeout=self.timeout * 3)
                match = re.search(r"ref: refs/heads/(\S+)\s+HEAD", head)
                branch = match.group(1) if match else None
                result["default_branch"] = branch
            except Exception as exc:
                result["api"]["error"] = _git_error(exc)
                return result
            try:
                tags_out = self.git(["ls-remote", "--tags", "--refs", url], timeout=self.timeout * 3)
                names = [line.split("refs/tags/", 1)[1] for line in tags_out.splitlines() if "refs/tags/" in line]
                result["tag_count"] = len(names)
                latest = latest_stable_tag(names)
                result["latest_tag"] = latest[0] if latest else None
            except Exception as exc:
                result["tags_api"]["error"] = _git_error(exc)
            try:
                clone = os.path.join(tmp, "repo")
                args = ["clone", "--quiet", "--filter=blob:none", "--no-checkout", "--depth", "1"]
                if branch:
                    args += ["--branch", branch]
                self.git(args + [url, clone], timeout=self.timeout * 30)
                committed = self.git(["-C", clone, "log", "-1", "--format=%cI", "HEAD"], timeout=self.timeout * 3)
                result["pushed_at_utc"] = format_utc(parse_iso_to_utc(committed.strip()))
                files = self.git(["-C", clone, "ls-tree", "--name-only", "HEAD"], timeout=self.timeout * 3).splitlines()
                licence_names = [f for f in files if re.match(r"(?i)^(LICEN[CS]E|COPYING)", f)]
                if licence_names:
                    text = self.git(["-C", clone, "show", "HEAD:" + licence_names[0]], timeout=self.timeout * 3)
                    result["licence_file"] = licence_names[0]
                    result["spdx_licence"] = detect_licence_text(text[:200000])
                    result["licence_detection"] = "text match" if result["spdx_licence"] else "no known licence text"
                else:
                    result["licence_detection"] = "no licence file at repository root"
            except Exception as exc:
                result["api"]["error"] = _git_error(exc)
            return result
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _headers(self, github=False):
        headers = {"User-Agent": USER_AGENT}
        if github:
            headers["Accept"] = "application/vnd.github+json"
            headers["X-GitHub-Api-Version"] = "2022-11-28"
            if self.token:
                headers["Authorization"] = "Bearer " + self.token
        return headers

    def _request(self, url, github=False):
        """One request. Returns (record_dict, parsed_body_or_None). Never raises for network errors."""
        if not is_https(url):
            return {"url": url, "fetched_at_utc": format_utc(self.clock()), "error": "refused: not https"}, None
        if self.requests_made and self.delay:
            time.sleep(self.delay)
        self.requests_made += 1
        fetched = format_utc(self.clock())
        try:
            status, body, final_url, ctype = self.fetch(url, self._headers(github), self.timeout)
        except urllib.error.HTTPError as exc:
            return {"url": url, "fetched_at_utc": fetched, "http_status": exc.code, "error": "HTTP %d" % exc.code}, None
        except Exception as exc:  # network failures are evidence too; record and continue
            return {"url": url, "fetched_at_utc": fetched, "error": "%s: %s" % (type(exc).__name__, exc)}, None
        record = {
            "url": url,
            "final_url": final_url,
            "fetched_at_utc": fetched,
            "http_status": status,
            "content_type": ctype,
            "error": None,
        }
        if github:
            try:
                return record, json.loads(body.decode("utf-8"))
            except ValueError as exc:
                record["error"] = "invalid JSON from API: %s" % exc
                return record, None
        record["body_sha256"] = hashlib.sha256(body).hexdigest()
        record["body_bytes_hashed"] = len(body)
        return record, None

    def collect_repo(self, owner, repo):
        base = "https://api.github.com/repos/%s/%s" % (owner, repo)
        meta, data = self._request(base, github=True)
        result = {"api": meta, "pushed_at_utc": None, "archived": None, "spdx_licence": None,
                  "default_branch": None, "latest_tag": None}
        if data is not None:
            pushed = data.get("pushed_at")
            result["pushed_at_utc"] = format_utc(parse_iso_to_utc(pushed)) if pushed else None
            result["archived"] = bool(data.get("archived"))
            licence = data.get("license") or {}
            result["spdx_licence"] = licence.get("spdx_id") if licence.get("spdx_id") not in (None, "NOASSERTION") else None
            result["default_branch"] = data.get("default_branch")
        tags_meta, tags = self._request(base + "/tags?per_page=1", github=True)
        result["tags_api"] = tags_meta
        if isinstance(tags, list) and tags:
            result["latest_tag"] = tags[0].get("name")
        return result

    def collect_docs(self, url):
        meta, _ = self._request(url)
        return meta

    def collect_record(self, row, want_repo=True, want_docs=True):
        rec_id = row["id"]
        repo = github_repo_of(row.get("repo_url"))
        has_docs = bool(row.get("docs_url")) and row["docs_url"] != "not stated"
        evidence = {
            "schema": SCHEMA,
            "id": rec_id,
            "name": row["name"],
            "collected_at_utc": format_utc(self.clock()),
            "repo": None,
            "docs": None,
            "status": None,
            "notes": [],
        }
        if repo and want_repo:
            if self.repo_source == "git":
                if self.delay:
                    time.sleep(self.delay)
                evidence["repo"] = self.collect_repo_git(*repo)
            else:
                evidence["repo"] = self.collect_repo(*repo)
        elif row.get("repo_url") and row["repo_url"] != "not stated":
            evidence["notes"].append("repository is not on github.com; not collected")
        if has_docs and want_docs:
            evidence["docs"] = self.collect_docs(row["docs_url"])
        elif row.get("docs_url") in (None, "", "not stated"):
            evidence["notes"].append("no documentation URL in the dataset; not collected")

        evidence["status"] = status_of(evidence)
        return evidence


def status_of(evidence):
    """ok, partial, failed or no_sources, from the repo and docs sections of one evidence record."""
    outcomes = []
    if evidence.get("repo"):
        outcomes.append(evidence["repo"]["api"]["error"] is None and evidence["repo"]["tags_api"]["error"] is None)
    if evidence.get("docs"):
        outcomes.append(evidence["docs"]["error"] is None)
    if not outcomes:
        return "no_sources"
    if all(outcomes):
        return "ok"
    if any(outcomes):
        return "partial"
    return "failed"


def read_rows(path=DATA):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def read_existing(out_dir, rec_id):
    path = os.path.join(out_dir, "%s.json" % rec_id)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_evidence(evidence, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "%s.json" % evidence["id"])
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    return path


def main(argv=None, fetch=http_fetch, clock=now_utc, rows=None, out_dir=EVIDENCE_DIR):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ids", help="comma-separated record IDs to collect")
    parser.add_argument("--dry-run", action="store_true", help="print the plan; make no requests and write nothing")
    parser.add_argument("--delay", type=float, default=0.0, help="seconds between requests")
    parser.add_argument("--timeout", type=float, default=20.0, help="seconds per request")
    parser.add_argument("--repo-source", choices=["api", "git"], default="api",
                        help="repository facts from the GitHub API (default) or over git")
    parser.add_argument("--skip-docs", action="store_true", help="keep the existing documentation section")
    parser.add_argument("--skip-repo", action="store_true", help="keep the existing repository section")
    args = parser.parse_args(argv)

    rows = read_rows() if rows is None else rows
    wanted = set(args.ids.split(",")) if args.ids else None
    selected = [r for r in rows if wanted is None or r["id"] in wanted]
    if wanted and len(selected) != len(wanted):
        missing = wanted - {r["id"] for r in selected}
        print("error: unknown record IDs: %s" % ", ".join(sorted(missing)))
        return 2

    if args.dry_run:
        for row in selected:
            repo = github_repo_of(row.get("repo_url"))
            docs = row.get("docs_url") not in (None, "", "not stated")
            print("%s\t%s\trepo=%s\tdocs=%s" % (row["id"], row["name"], "yes" if repo else "no", "yes" if docs else "no"))
        print("dry run: %d records; no requests made, nothing written" % len(selected))
        return 0

    collector = Collector(fetch=fetch, delay=args.delay, timeout=args.timeout,
                          token=os.environ.get("GITHUB_TOKEN") or None, clock=clock,
                          repo_source=args.repo_source)
    counts = {}
    for row in selected:
        existing = read_existing(out_dir, row["id"])
        evidence = collector.collect_record(row, want_repo=not args.skip_repo, want_docs=not args.skip_docs)
        if args.skip_docs and existing.get("docs") is not None:
            evidence["docs"] = existing["docs"]
        if args.skip_repo and existing.get("repo") is not None:
            evidence["repo"] = existing["repo"]
        evidence["status"] = status_of(evidence)
        write_evidence(evidence, out_dir)
        counts[evidence["status"]] = counts.get(evidence["status"], 0) + 1
    print("evidence written for %d records: %s" % (len(selected), ", ".join("%s=%d" % kv for kv in sorted(counts.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
