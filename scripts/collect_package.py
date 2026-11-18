#!/usr/bin/env python3
"""Collect the package version from each GitHub repository over git.

The dataset field `version` means the version of the package (the design system's
npm package or equivalent). For each GitHub record this script reads the package.json
files of the default branch and writes evidence/package/<id>.json:

  root        the package.json at the repository root: name, version (or null)
  paths       every package.json in the tree (monorepos have several)
  error       what went wrong, if anything

It uses the same git route as collect.py: `git ls-remote` for the default branch, a
shallow blobless clone for the tree, and `git show HEAD:<path>` for the file contents.
GIT_TERMINAL_PROMPT=0, so no credentials are asked for or stored.

Usage:
  python3 scripts/collect_package.py [--ids 5,10] [--delay 0.5] [--out evidence/package]
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect import git_run, github_repo_of, read_rows, _git_error  # noqa: E402
from common import format_utc  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV = os.path.join(ROOT, "data", "design_systems.csv")
OUT_DIR = os.path.join(ROOT, "evidence", "package")
MAX_PACKAGE_JSON_BYTES = 512 * 1024
MAX_OTHER_PACKAGES = 50


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def collect_one(rec_id, owner, repo, git=git_run, timeout=120.0, clock=now_utc):
    """Return the evidence dict for one repository. Never raises for git failures."""
    url = "https://github.com/%s/%s" % (owner, repo)
    evidence = {"id": rec_id, "repo_url": url, "collected_at_utc": format_utc(clock()),
                "method": "git", "root": None, "paths": [], "others": [], "error": None}
    tmp = tempfile.mkdtemp(prefix="collect-pkg-")
    try:
        try:
            head = git(["ls-remote", "--symref", url, "HEAD"], timeout=timeout)
            match = re.search(r"ref: refs/heads/(\S+)\s+HEAD", head)
            if not match:
                evidence["error"] = "no default branch found"
                return evidence
            branch = match.group(1)
            clone = os.path.join(tmp, "repo")
            git(["clone", "--quiet", "--filter=blob:none", "--no-checkout", "--depth", "1",
                 "--branch", branch, url, clone], timeout=timeout * 10)
            listing = git(["ls-tree", "-r", "--name-only", "HEAD"], cwd=clone, timeout=timeout)
            paths = sorted(p for p in listing.splitlines() if p == "package.json" or p.endswith("/package.json"))
            evidence["paths"] = paths
            if "package.json" in paths:
                text = git(["show", "HEAD:package.json"], cwd=clone, timeout=timeout)
                evidence["root"] = parse_package_json(text)
            # monorepo members: name and version of each other package.json (capped)
            others = []
            for path in [p for p in paths if p != "package.json"][:MAX_OTHER_PACKAGES]:
                text = git(["show", "HEAD:%s" % path], cwd=clone, timeout=timeout)
                parsed = parse_package_json(text)
                others.append({"path": path, "name": parsed["name"], "version": parsed["version"],
                               "error": parsed["error"]})
            evidence["others"] = others
        except Exception as exc:  # noqa: BLE001 - recorded, not raised
            evidence["error"] = _git_error(exc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return evidence


def parse_package_json(text):
    """Return {name, version} from package.json text. Missing keys are None."""
    if len(text.encode("utf-8")) > MAX_PACKAGE_JSON_BYTES:
        return {"name": None, "version": None, "error": "package.json larger than 512 KiB; not parsed"}
    try:
        data = json.loads(text)
    except ValueError as exc:
        return {"name": None, "version": None, "error": "not valid JSON: %s" % exc}
    if not isinstance(data, dict):
        return {"name": None, "version": None, "error": "not a JSON object"}
    name = data.get("name") if isinstance(data.get("name"), str) else None
    version = data.get("version") if isinstance(data.get("version"), str) else None
    return {"name": name, "version": version, "error": None}


def main(argv=None, git=git_run, rows=None, out_dir=OUT_DIR, delay=0.0, clock=now_utc):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ids", help="comma-separated record IDs")
    parser.add_argument("--delay", type=float, default=delay)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--out", default=out_dir)
    args = parser.parse_args(argv)
    rows = rows if rows is not None else read_rows(DATA_CSV)
    wanted = set(args.ids.split(",")) if args.ids else None
    os.makedirs(args.out, exist_ok=True)
    done = 0
    import time
    for row in rows:
        if wanted and row["id"] not in wanted:
            continue
        gh = github_repo_of(row.get("repo_url"))
        if not gh:
            continue
        evidence = collect_one(row["id"], gh[0], gh[1], git=git, timeout=args.timeout, clock=clock)
        with open(os.path.join(args.out, "%s.json" % row["id"]), "w", encoding="utf-8") as fh:
            json.dump(evidence, fh, indent=2, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        done += 1
        if args.delay:
            time.sleep(args.delay)
    print("package evidence written for %d repositories" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
