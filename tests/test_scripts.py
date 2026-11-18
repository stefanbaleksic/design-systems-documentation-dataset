"""Tests for collect.py, run_compare_from_evidence.py and release.py. Standard library only.

No test makes a network request: the collector gets a fake fetch function.
"""
import csv
import datetime as dt
import io
import json
import re
import os
import shutil
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import collect  # noqa: E402
import release  # noqa: E402
import run_compare_from_evidence as compare_mod  # noqa: E402

UTC = dt.timezone.utc
FIXED = dt.datetime(2026, 11, 18, 9, 0, tzinfo=UTC)


def clock():
    return FIXED


def row(**kw):
    base = {"id": "1", "name": "Example", "type": "Design system", "sector": "Software & tech",
            "status": "checked", "checked": "17.11.2026", "docs_url": "https://docs.example.org/",
            "repo_url": "https://github.com/example/ds", "licence": "not stated",
            "repo_licence": "MIT (LICENSE)", "version": "1.2.3", "repo_last_push": "2026-11-16 (last commit date)",
            "repo_archived": "no", "sample": "no", "note": ""}
    base.update(kw)
    return base


class FakeFetch:
    """Stands in for collect.http_fetch. `routes` maps a URL prefix to a response or exception."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []
        self.headers_seen = []

    def __call__(self, url, headers, timeout):
        self.calls.append(url)
        self.headers_seen.append(headers)
        for prefix, outcome in self.routes.items():
            if url.startswith(prefix):
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome
        raise urllib.error.URLError("no route for %s" % url)


def api_repo(pushed="2026-11-16T10:00:00Z", archived=False, spdx="MIT"):
    body = {"pushed_at": pushed, "archived": archived, "default_branch": "main",
            "license": {"spdx_id": spdx} if spdx else None}
    return 200, json.dumps(body).encode("utf-8"), "https://api.github.com/repos/example/ds", "application/json"


def api_tags(name="v1.2.3"):
    return 200, json.dumps([{"name": name}]).encode("utf-8"), "https://api.github.com/x", "application/json"


class CollectTests(unittest.TestCase):
    def test_records_github_and_docs_evidence(self):
        fetch = FakeFetch({
            "https://api.github.com/repos/example/ds/tags": api_tags("v1.2.3"),
            "https://api.github.com/repos/example/ds": api_repo(),
            "https://docs.example.org/": (200, b"<html>docs</html>", "https://docs.example.org/", "text/html"),
        })
        c = collect.Collector(fetch=fetch, clock=clock, token=None)
        ev = c.collect_record(row())
        self.assertEqual(ev["status"], "ok")
        self.assertEqual(ev["repo"]["pushed_at_utc"], "2026-11-16T10:00:00Z")
        self.assertEqual(ev["repo"]["spdx_licence"], "MIT")
        self.assertEqual(ev["repo"]["latest_tag"], "v1.2.3")
        self.assertFalse(ev["repo"]["archived"])
        self.assertEqual(ev["docs"]["http_status"], 200)
        self.assertEqual(len(ev["docs"]["body_sha256"]), 64)
        self.assertEqual(ev["docs"]["body_bytes_hashed"], len(b"<html>docs</html>"))

    def test_failures_are_recorded_not_raised(self):
        fetch = FakeFetch({
            "https://api.github.com/repos/example/ds": urllib.error.HTTPError("u", 403, "Forbidden", {}, None),
            "https://api.github.com/repos/example/ds/tags": urllib.error.HTTPError("u", 403, "Forbidden", {}, None),
            "https://docs.example.org/": OSError("connection reset"),
        })
        c = collect.Collector(fetch=fetch, clock=clock)
        ev = c.collect_record(row())
        self.assertEqual(ev["status"], "failed")
        self.assertEqual(ev["repo"]["api"]["error"], "HTTP 403")
        self.assertIn("connection reset", ev["docs"]["error"])

    def test_partial_when_only_one_source_works(self):
        fetch = FakeFetch({
            "https://api.github.com/": urllib.error.HTTPError("u", 403, "Forbidden", {}, None),
            "https://docs.example.org/": (200, b"ok", "https://docs.example.org/", "text/html"),
        })
        ev = collect.Collector(fetch=fetch, clock=clock).collect_record(row())
        self.assertEqual(ev["status"], "partial")

    def test_non_github_repo_and_no_docs_are_noted_not_dropped(self):
        fetch = FakeFetch({})
        ev = collect.Collector(fetch=fetch, clock=clock).collect_record(
            row(repo_url="https://gitlab.com/x/y", docs_url="not stated"))
        self.assertEqual(ev["status"], "no_sources")
        self.assertEqual(fetch.calls, [])
        self.assertTrue(any("not on github.com" in n for n in ev["notes"]))
        self.assertTrue(any("no documentation URL" in n for n in ev["notes"]))

    def test_non_https_is_refused_without_a_request(self):
        fetch = FakeFetch({})
        ev = collect.Collector(fetch=fetch, clock=clock).collect_record(row(docs_url="http://docs.example.org/"))
        self.assertFalse(any(u.startswith("http://") for u in fetch.calls))
        self.assertIn("not https", ev["docs"]["error"])

    def test_token_is_sent_as_header_and_never_stored(self):
        fetch = FakeFetch({
            "https://api.github.com/repos/example/ds/tags": api_tags(),
            "https://api.github.com/repos/example/ds": api_repo(),
            "https://docs.example.org/": (200, b"x", "https://docs.example.org/", "text/html"),
        })
        secret = "ghp_TESTSECRETVALUE123"
        c = collect.Collector(fetch=fetch, clock=clock, token=secret)
        ev = c.collect_record(row())
        self.assertTrue(any(h.get("Authorization") == "Bearer " + secret for h in fetch.headers_seen))
        self.assertNotIn(secret, json.dumps(ev))

    def test_main_writes_one_file_per_record_and_dry_run_writes_none(self):
        tmp = tempfile.mkdtemp()
        try:
            rows = [row(id="1"), row(id="2", name="Second", repo_url="", docs_url="not stated")]
            fetch = FakeFetch({"https://docs.example.org/": (200, b"x", "https://docs.example.org/", "text/html")})
            out = io.StringIO()
            with redirect_stdout(out):
                rc = collect.main([], fetch=fetch, clock=clock, rows=rows, out_dir=tmp)
            self.assertEqual(rc, 0)
            self.assertEqual(sorted(os.listdir(tmp)), ["1.json", "2.json"])

            dry_dir = os.path.join(tmp, "dry")
            with redirect_stdout(io.StringIO()):
                collect.main(["--dry-run"], fetch=fetch, clock=clock, rows=rows, out_dir=dry_dir)
            self.assertFalse(os.path.exists(dry_dir))
        finally:
            shutil.rmtree(tmp)

    def test_unknown_id_is_an_error(self):
        with redirect_stdout(io.StringIO()):
            rc = collect.main(["--ids", "999"], fetch=FakeFetch({}), clock=clock, rows=[row()], out_dir=tempfile.gettempdir())
        self.assertEqual(rc, 2)


class FakeGit:
    """Stands in for collect.git_run. Maps the git subcommand to a canned output."""

    def __init__(self, fail=None, mit=True):
        self.fail = fail or set()
        self.mit = mit
        self.calls = []

    def __call__(self, args, cwd=None, timeout=None):
        self.calls.append(args)
        if "ls-remote" in args and "--symref" in args:
            if "symref" in self.fail:
                raise collect.subprocess.CalledProcessError(128, ["git"], stderr=b"fatal: could not read Username")
            return "ref: refs/heads/main\tHEAD\nabc\tHEAD\n"
        if "ls-remote" in args and "--tags" in args:
            return "a\trefs/tags/v1.9.0\nb\trefs/tags/v2.0.0-beta.1\nc\trefs/tags/v1.10.0\nd\trefs/tags/nightly\n"
        if "clone" in args:
            return ""
        if "log" in args:
            return "2026-11-16T11:10:38+01:00\n"
        if "ls-tree" in args:
            return "README.md\nLICENSE\nsrc\n"
        if "show" in args:
            return ("MIT License\n\nPermission is hereby granted, free of charge, to any person" if self.mit
                    else "Custom terms: all rights reserved.")
        raise AssertionError("unexpected git call: %r" % (args,))


class GitRouteTests(unittest.TestCase):
    def test_repo_facts_over_git(self):
        git = FakeGit()
        c = collect.Collector(clock=clock, repo_source="git", git=git)
        result = c.collect_repo_git("example", "ds")
        self.assertEqual(result["default_branch"], "main")
        self.assertEqual(result["latest_tag"], "v1.10.0")  # stable and highest: 1.10.0 > 1.9.0
        self.assertEqual(result["tag_count"], 4)
        self.assertEqual(result["pushed_at_utc"], "2026-11-16T10:10:38Z")  # +01:00 converted to UTC
        self.assertEqual(result["spdx_licence"], "MIT")
        self.assertEqual(result["licence_file"], "LICENSE")
        self.assertIsNone(result["archived"])  # not available over git
        self.assertIsNone(result["api"]["error"])

    def test_no_credentials_in_git_urls(self):
        git = FakeGit()
        collect.Collector(clock=clock, repo_source="git", git=git, token="ghp_SECRET_X").collect_repo_git("example", "ds")
        joined = " ".join(" ".join(a) for a in git.calls)
        self.assertNotIn("ghp_SECRET_X", joined)
        self.assertTrue(all("https://github.com/" in " ".join(a) for a in git.calls if "ls-remote" in a or "clone" in a))

    def test_unknown_licence_text_is_recorded_as_such(self):
        result = collect.Collector(clock=clock, repo_source="git", git=FakeGit(mit=False)).collect_repo_git("e", "d")
        self.assertIsNone(result["spdx_licence"])
        self.assertEqual(result["licence_detection"], "no known licence text")

    def test_git_failure_is_recorded_not_raised(self):
        result = collect.Collector(clock=clock, repo_source="git", git=FakeGit(fail={"symref"})).collect_repo_git("e", "d")
        self.assertIn("git exit 128", result["api"]["error"])
        self.assertIsNone(result["pushed_at_utc"])

    def test_git_route_is_used_by_collect_record(self):
        git = FakeGit()
        c = collect.Collector(fetch=FakeFetch({}), clock=clock, repo_source="git", git=git)
        ev = c.collect_record(row(docs_url="not stated"))
        self.assertEqual(ev["repo"]["latest_tag"], "v1.10.0")
        self.assertEqual(ev["status"], "ok")


def write_evidence(directory, ev):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, "%s.json" % ev["id"]), "w", encoding="utf-8") as fh:
        json.dump(ev, fh)


def good_evidence(rec_id="1", **repo_overrides):
    repo = {"api": {"error": None}, "tags_api": {"error": None}, "pushed_at_utc": "2026-11-16T10:00:00Z",
            "archived": False, "spdx_licence": "MIT", "latest_tag": "v1.2.3"}
    repo.update(repo_overrides)
    return {"id": rec_id, "status": "ok", "repo": repo,
            "docs": {"error": None, "http_status": 200, "body_sha256": "ab" * 32}}


def package_evidence(root=None, others=(), rec_id="1"):
    """Evidence for evidence/package/<id>.json. root = version of the root package.json, or None."""
    return {"id": rec_id, "repo_url": "https://github.com/example/ds", "collected_at_utc": "2026-11-18T09:00:00Z",
            "method": "git", "error": None, "paths": [],
            "root": {"name": "example-ds", "version": root, "error": None} if root else None,
            "others": list(others)}


class CompareTests(unittest.TestCase):
    def outcomes(self, report):
        return {f["check"]: f["outcome"] for f in report[0]["findings"]}

    def test_all_match(self):
        report = compare_mod.compare([row()], {"1": good_evidence()}, {"1": package_evidence(root="1.2.3")})
        self.assertEqual(self.outcomes(report), {"last_push": "match", "archived": "match", "licence": "match",
                                                 "version": "match", "docs": "fetched"})

    def test_last_push_compares_utc_dates(self):
        # 2026-11-19T00:10Z is 2026-11-19 in UTC, three days after the dataset date: a mismatch
        report = compare_mod.compare([row()], {"1": good_evidence(pushed_at_utc="2026-11-19T00:10:00Z")})
        self.assertEqual(self.outcomes(report)["last_push"], "mismatch")

    def test_last_push_direction_is_explained(self):
        newer = compare_mod.compare([row(repo_last_push="2026-11-10")], {"1": good_evidence()})
        self.assertIn("newer commits", [f for f in newer[0]["findings"] if f["check"] == "last_push"][0]["detail"])
        later = compare_mod.compare([row(repo_last_push="2026-11-20")], {"1": good_evidence()})
        self.assertIn("contradiction", [f for f in later[0]["findings"] if f["check"] == "last_push"][0]["detail"])

    def test_one_day_difference_is_a_time_zone_match(self):
        one = compare_mod.compare([row(repo_last_push="2026-11-16")], {"1": good_evidence(pushed_at_utc="2026-11-17T00:10:00Z")})
        self.assertEqual(self.outcomes(one)["last_push"], "match")
        two = compare_mod.compare([row(repo_last_push="2026-11-14")], {"1": good_evidence(pushed_at_utc="2026-11-17T00:10:00Z")})
        self.assertEqual(self.outcomes(two)["last_push"], "mismatch")

    def test_non_date_last_push_is_not_recorded_not_a_crash(self):
        report = compare_mod.compare([row(repo_last_push="not checked")], {"1": good_evidence()})
        self.assertEqual(self.outcomes(report)["last_push"], "not_recorded")

    def test_archived_and_licence_mismatch(self):
        report = compare_mod.compare([row()], {"1": good_evidence(archived=True, spdx_licence="GPL-3.0-only")})
        out = self.outcomes(report)
        self.assertEqual(out["archived"], "mismatch")
        self.assertEqual(out["licence"], "mismatch")

    def test_version_is_compared_with_package_not_git_tag(self):
        # the newest git tag is 1.2.3 but the package says 1.4.0: the dataset value 1.2.3 is still a
        # version a package carries only if some package.json says so
        report = compare_mod.compare([row(version="1.2.3")], {"1": good_evidence(latest_tag="v1.2.3")},
                                     {"1": package_evidence(root="1.4.0")})
        self.assertEqual(self.outcomes(report)["version"], "mismatch")

    def test_version_found_in_monorepo_member_is_a_match(self):
        others = [{"path": "packages/x/package.json", "name": "x", "version": "2.1.0", "error": None}]
        report = compare_mod.compare([row(version="2.1.0")], {"1": good_evidence()},
                                     {"1": package_evidence(root="1.9.0", others=others)})
        self.assertEqual(self.outcomes(report)["version"], "match")

    def test_placeholder_root_version_is_not_comparable(self):
        report = compare_mod.compare([row(version="3.0.0")], {"1": good_evidence()},
                                     {"1": package_evidence(root="0.0.0")})
        self.assertEqual(self.outcomes(report)["version"], "not_comparable")

    def test_version_without_full_semver_is_not_recorded(self):
        report = compare_mod.compare([row(version="v4.10")], {"1": good_evidence()},
                                     {"1": package_evidence(root="4.10.1")})
        self.assertEqual(self.outcomes(report)["version"], "not_recorded")

    def test_missing_evidence_is_reported_not_skipped(self):
        report = compare_mod.compare([row()], {})
        out = self.outcomes(report)
        self.assertEqual(out["repo"], "missing_evidence")
        self.assertEqual(out["docs"], "missing_evidence")

    def test_failed_evidence_is_unavailable(self):
        ev = {"id": "1", "status": "failed",
              "repo": {"api": {"error": "HTTP 403"}, "tags_api": {"error": "HTTP 403"}},
              "docs": {"error": "timeout", "http_status": None}}
        report = compare_mod.compare([row()], {"1": ev})
        out = self.outcomes(report)
        self.assertEqual(out["repo"], "unavailable")
        self.assertEqual(out["docs"], "unavailable")

    def test_any_2xx_counts_as_fetched(self):
        ev = good_evidence()
        ev["docs"]["http_status"] = 204
        report = compare_mod.compare([row()], {"1": ev})
        self.assertEqual(self.outcomes(report)["docs"], "fetched")

    def test_non_2xx_is_unavailable(self):
        ev = good_evidence()
        ev["docs"]["http_status"] = 404
        report = compare_mod.compare([row()], {"1": ev})
        self.assertEqual(self.outcomes(report)["docs"], "unavailable")

    def test_record_without_sources_is_listed(self):
        report = compare_mod.compare([row(repo_url="", docs_url="not stated")], {})
        self.assertEqual(self.outcomes(report), {"sources": "no_source"})

    def test_strict_exit_status(self):
        tmp = tempfile.mkdtemp()
        try:
            with redirect_stdout(io.StringIO()):
                ok = compare_mod.main(["--strict"], rows=[row()], evidence={"1": good_evidence()}, out_dir=tmp)
                lenient = compare_mod.main([], rows=[row()], evidence={}, out_dir=tmp)
                strict = compare_mod.main(["--strict"], rows=[row()], evidence={}, out_dir=tmp)
            self.assertEqual(ok, 0)
            self.assertEqual(lenient, 0)
            self.assertEqual(strict, 1)
            # the last run wrote the report: it must list the missing evidence, not skip it
            with open(os.path.join(tmp, "compare_report.md"), encoding="utf-8") as fh:
                self.assertIn("missing_evidence", fh.read())
        finally:
            shutil.rmtree(tmp)


import corrections as corr_mod  # noqa: E402


def page_row(**kw):
    base = {"id": "1", "name": "Example", "repo_url": "https://github.com/example/ds", "docs_url": "not stated",
            "repo_licence": "", "repo_last_push": "", "version": "1.2.3", "repo_archived": "no"}
    base.update(kw)
    return base


def git_evidence(pushed="2026-11-17T08:00:00Z", spdx="MIT", licence_file="LICENSE", tag="v1.2.3"):
    return {"id": "1", "name": "Example", "collected_at_utc": "2026-11-18T09:00:00Z",
            "repo": {"api": {"error": None}, "tags_api": {"error": None}, "pushed_at_utc": pushed,
                     "spdx_licence": spdx, "licence_file": licence_file, "latest_tag": tag, "archived": None}}


class PackageCollectTests(unittest.TestCase):
    def test_parse_package_json_handles_bad_input(self):
        import collect_package as cp
        self.assertEqual(cp.parse_package_json('{"name": "x", "version": "1.2.3"}')["version"], "1.2.3")
        self.assertIsNotNone(cp.parse_package_json("{not json")["error"])
        self.assertIsNotNone(cp.parse_package_json("[1, 2]")["error"])

    def test_collect_one_reads_root_and_members_with_fake_git(self):
        import collect_package as cp
        files = {"HEAD:package.json": '{"name": "root", "version": "3.0.0"}',
                 "HEAD:packages/a/package.json": '{"name": "a", "version": "1.1.0"}'}

        def fake_git(args, cwd=None, timeout=120):
            if args[:2] == ["ls-remote", "--symref"]:
                return "ref: refs/heads/main\tHEAD\n"
            if args[:1] == ["clone"]:
                return ""
            if args[:2] == ["ls-tree", "-r"]:
                return "package.json\npackages/a/package.json\nREADME.md\n"
            if args[:1] == ["show"]:
                return files[args[1]]
            raise AssertionError(args)

        ev = cp.collect_one("7", "org", "repo", git=fake_git, clock=lambda: dt.datetime(2026, 11, 18, tzinfo=dt.timezone.utc))
        self.assertEqual(ev["root"]["version"], "3.0.0")
        self.assertEqual([o["version"] for o in ev["others"]], ["1.1.0"])
        self.assertIsNone(ev["error"])

    def test_git_failure_is_recorded_not_raised(self):
        import collect_package as cp

        def failing(args, cwd=None, timeout=120):
            raise RuntimeError("git exit 128: fatal: could not read Username")

        ev = cp.collect_one("8", "org", "gone", git=failing)
        self.assertIn("could not read Username", ev["error"])


class CorrectionsTests(unittest.TestCase):
    def test_empty_last_push_is_filled(self):
        c, _ = corr_mod.propose([page_row()], {"1": git_evidence()}, {"1": page_row()})
        fill = [x for x in c if x["field"] == "repo_last_push"][0]
        self.assertEqual(fill["new_value"], "2026-11-17 (last commit date)")
        self.assertEqual(fill["old_value"], "")

    def test_one_day_difference_is_not_corrected(self):
        row = page_row(repo_last_push="2026-11-16 (last commit date)")
        c, _ = corr_mod.propose([row], {"1": git_evidence(pushed="2026-11-17T08:00:00Z")}, {"1": row})
        self.assertFalse([x for x in c if x["field"] == "repo_last_push"])

    def test_newer_commits_and_contradictions_are_both_corrected_with_reason(self):
        newer = page_row(repo_last_push="2026-11-10 (last commit date)")
        c, _ = corr_mod.propose([newer], {"1": git_evidence()}, {"1": newer})
        self.assertIn("newer commits", c[0]["basis"])
        later = page_row(repo_last_push="2026-11-25 (last commit date)")
        c, _ = corr_mod.propose([later], {"1": git_evidence()}, {"1": later})
        self.assertIn("later than", c[0]["basis"])

    def test_licence_none_is_corrected_other_or_custom_is_open(self):
        none = page_row(repo_licence="not identified")
        c, open_items = corr_mod.propose([none], {"1": git_evidence()}, {"1": none})
        self.assertEqual([x["new_value"] for x in c if x["field"] == "repo_licence"], ["MIT (LICENSE)"])
        custom = page_row(repo_licence="PrimeNG community licence (LICENSE.md; custom terms)")
        c, open_items = corr_mod.propose([custom], {"1": git_evidence()}, {"1": custom})
        self.assertFalse([x for x in c if x["field"] == "repo_licence"])
        self.assertTrue([i for i in open_items if i["field"] == "repo_licence"])

    def test_version_is_filled_from_root_package(self):
        page = {"1": page_row(version="not stated")}
        c, _ = corr_mod.propose_version([page_row(version="not stated")], {"1": package_evidence(root="1.4.0")}, page)
        self.assertEqual([(x["old_value"], x["new_value"]) for x in c], [("not stated", "1.4.0")])

    def test_named_package_is_used_when_the_value_names_it(self):
        others = [{"path": "packages/palette/package.json", "name": "palette", "version": "46.11.0", "error": None},
                  {"path": "packages/tokens/package.json", "name": "tokens", "version": "7.3.0", "error": None}]
        ev = {"1": package_evidence(root=None, others=others)}
        page = {"1": page_row(version="@artsy/palette@45.0.0 (latest tag seen)")}
        c, _ = corr_mod.propose_version([page_row(version="@artsy/palette@45.0.0 (latest tag seen)")], ev, page)
        self.assertEqual(c[0]["new_value"], "46.11.0")
        self.assertIn("palette", c[0]["basis"])

    def test_placeholder_and_ambiguous_versions_are_open_items(self):
        page = {"1": page_row(version="not stated")}
        _, open_items = corr_mod.propose_version([page_row(version="not stated")],
                                                 {"1": package_evidence(root="0.0.1")}, page)
        self.assertTrue([i for i in open_items if "placeholder" in i["detail"]])
        others = [{"path": "a/package.json", "name": "a", "version": "1.0.0", "error": None},
                  {"path": "b/package.json", "name": "b", "version": "2.0.0", "error": None}]
        c, open_items = corr_mod.propose_version([page_row(version="not stated")],
                                                 {"1": package_evidence(root=None, others=others)}, page)
        self.assertFalse(c)
        self.assertTrue([i for i in open_items if "none at the root" in i["detail"]])

    def test_corrections_history_is_append_only(self):
        old = [{"id": "1", "field": "repo_licence", "new_value": "MIT (LICENSE)"}]
        merged = corr_mod.merge_corrections(old, [{"id": "1", "field": "repo_licence", "new_value": "MIT (LICENSE)"},
                                                  {"id": "1", "field": "version", "new_value": "1.4.0"}])
        self.assertEqual(len(merged), 2)

    def test_apply_writes_note_and_is_idempotent(self):
        tmp = tempfile.mkdtemp()
        try:
            page = os.path.join(tmp, "index.html")
            data = [{"id": "1", "name": "Example", "repo_last_push": "", "repo_licence": "", "note": "kept"}]
            with open(page, "w", encoding="utf-8") as fh:
                fh.write("<script>\nconst DATA = %s;\n</script>\n" % json.dumps(data))
            corrections = [{"id": "1", "name": "Example", "field": "repo_last_push", "old_value": "",
                            "new_value": "2026-11-17 (last commit date)", "basis": "filled",
                            "evidence_collected_utc": "2026-11-18T09:00:00Z", "evidence_source": "x"}]
            self.assertEqual(corr_mod.apply(corrections, page=page), (1, 0))
            self.assertEqual(corr_mod.apply(corrections, page=page), (0, 1))
            with open(page, encoding="utf-8") as fh:
                text = fh.read()
            self.assertIn("Corrected 18.11.2026 from evidence (filled)", text)
            self.assertIn("kept", text)
        finally:
            shutil.rmtree(tmp)

    def test_apply_stops_on_conflict(self):
        tmp = tempfile.mkdtemp()
        try:
            page = os.path.join(tmp, "index.html")
            with open(page, "w", encoding="utf-8") as fh:
                fh.write('<script>\nconst DATA = [{"id": "1", "repo_last_push": "2026-01-01 (x)", "note": ""}];\n</script>\n')
            bad = [{"id": "1", "name": "E", "field": "repo_last_push", "old_value": "2025-01-01",
                    "new_value": "2026-11-17", "basis": "b", "evidence_collected_utc": "2026-11-18T00:00:00Z",
                    "evidence_source": "x"}]
            with self.assertRaises(SystemExit):
                corr_mod.apply(bad, page=page)
            with open(page, encoding="utf-8") as fh:
                self.assertIn("2026-01-01 (x)", fh.read())  # nothing written
        finally:
            shutil.rmtree(tmp)

    def test_repository_corrections_file_matches_the_dataset(self):
        rows = {r["id"]: r for r in corr_mod.load_rows()}
        for c in corr_mod.load_corrections():
            self.assertIn(c["id"], rows)
            self.assertEqual(rows[c["id"]][c["field"]], c["new_value"], (c["id"], c["field"]))


class CitationTests(unittest.TestCase):
    """CITATION.cff is read with the standard library only (no PyYAML on the CI runner)."""

    def read_field(self, text, key):
        match = re.search(r"^%s:\s*\"?([^\"\n]+?)\"?\s*$" % re.escape(key), text, re.M)
        return match.group(1) if match else None

    def test_citation_matches_version_and_release_date(self):
        with open(os.path.join(ROOT, "CITATION.cff"), encoding="utf-8") as fh:
            cff = fh.read()
        with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as fh:
            version = fh.read().strip()
        self.assertEqual(self.read_field(cff, "version"), version)
        self.assertEqual(self.read_field(cff, "date-released"), "2026-11-18")  # the CHANGELOG heading for 1.0.0
        self.assertIn("orcid: \"https://orcid.org/0009-0009-1537-296X\"", cff)


class ReleaseTests(unittest.TestCase):
    def test_repository_release_is_consistent(self):
        self.assertEqual(release.check(ROOT), [])

    def test_detects_a_changed_data_file(self):
        tmp = tempfile.mkdtemp()
        try:
            for rel in ["VERSION", "release.json", "CHANGELOG.md", "source/index.html", "source/SHA256SUMS",
                        "source/SOURCE.json", "data/design_systems.csv", "data/design_systems_raw.csv",
                        "data/removed_duplicates.csv", "data/corrections.csv"]:
                os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
                shutil.copy(os.path.join(ROOT, rel), os.path.join(tmp, rel))
            self.assertEqual(release.check(tmp), [])
            with open(os.path.join(tmp, "data", "design_systems.csv"), "a", encoding="utf-8") as fh:
                fh.write("tampered line\n")
            problems = release.check(tmp)
            self.assertTrue(any("data_sha256" in p for p in problems), problems)
        finally:
            shutil.rmtree(tmp)

    def test_detects_missing_changelog_heading(self):
        tmp = tempfile.mkdtemp()
        try:
            for rel in ["VERSION", "release.json", "CHANGELOG.md", "source/index.html", "source/SHA256SUMS",
                        "source/SOURCE.json", "data/design_systems.csv", "data/design_systems_raw.csv",
                        "data/removed_duplicates.csv", "data/corrections.csv"]:
                os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
                shutil.copy(os.path.join(ROOT, rel), os.path.join(tmp, rel))
            with open(os.path.join(tmp, "CHANGELOG.md"), "w", encoding="utf-8") as fh:
                fh.write("# Changelog\n")
            self.assertTrue(any("CHANGELOG" in p for p in release.check(tmp)))
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
