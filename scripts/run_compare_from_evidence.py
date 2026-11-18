#!/usr/bin/env python3
"""Compare the dataset with the collected evidence. Offline: makes no network requests.

For each record the script checks what the evidence can support and reports every outcome:

  repo (repo_url on github.com)
    last_push      record's repo_last_push date vs evidence pushed_at (UTC date). A difference of one
                   day counts as a match: GitHub shows dates in the viewer's time zone.
    archived       record's repo_archived (yes/no) vs evidence archived flag
    licence        licence class of record's repo_licence vs class of the SPDX id in evidence
    version        record's version vs newest tag in evidence (SemVer comparison, when both parse)
  docs (docs_url)
    fetch          evidence shows the page answered with a 2xx status and a hash was recorded. This is a
                   reachability check only; the page content is not compared with the dataset.

  Outcomes: match, fetched, mismatch, missing_evidence, unavailable, not_comparable,
  not_recorded, no_source. A record with no sources is listed, not dropped.

Writes results/compare_report.md and results/compare_report.json and prints a summary.

Exit status: 0 normally. With --strict, 1 if anything is missing, unavailable, or mismatching.

Usage:
    python3 scripts/run_compare_from_evidence.py [--strict]
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import compare_semver, licence_class, parse_last_push, parse_semver  # noqa: E402
from corrections import parse_field_version, load_package_evidence, usable_others  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "design_systems.csv")
EVIDENCE = os.path.join(ROOT, "evidence")
RESULTS = os.path.join(ROOT, "results")

PROBLEM_OUTCOMES = {"mismatch", "missing_evidence", "unavailable"}


def github_source(row):
    url = (row.get("repo_url") or "").strip()
    return url.startswith("https://github.com/")


def docs_source(row):
    url = (row.get("docs_url") or "").strip()
    return bool(url) and url != "not stated"


def load_rows(path=DATA):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_evidence(directory=EVIDENCE):
    found = {}
    if not os.path.isdir(directory):
        return found
    for name in os.listdir(directory):
        if name.endswith(".json"):
            with open(os.path.join(directory, name), encoding="utf-8") as fh:
                data = json.load(fh)
            found[str(data["id"])] = data
    return found


def finding(check, outcome, detail=""):
    return {"check": check, "outcome": outcome, "detail": detail}


def _semver_or_none(text):
    try:
        return parse_semver(text)
    except ValueError:
        return None


def compare_repo(row, ev, pkg_ev=None):
    """Findings for the repository source of one record."""
    out = []
    if ev is None:
        return [finding("repo", "missing_evidence", "no evidence file for %s" % row["repo_url"])]
    repo = ev.get("repo")
    if repo is None:
        return [finding("repo", "missing_evidence", "evidence file has no repository section")]
    api_error = repo.get("api", {}).get("error")
    if api_error:
        return [finding("repo", "unavailable", "GitHub API: %s" % api_error)]

    # last push: compare UTC calendar dates
    try:
        recorded = parse_last_push(row.get("repo_last_push"))
    except ValueError:
        recorded = None
        out.append(finding("last_push", "not_recorded", "repo_last_push is %r, not a date" % row.get("repo_last_push")))
    fetched = repo.get("pushed_at_utc")
    if recorded is None and not any(f["check"] == "last_push" for f in out):
        out.append(finding("last_push", "not_recorded", "repo_last_push empty in dataset"))
    elif recorded is None:
        pass
    elif not fetched:
        out.append(finding("last_push", "not_comparable", "no pushed_at in evidence"))
    else:
        fetched_date = fetched[:10]
        delta = (recorded - dt.date.fromisoformat(fetched_date)).days
        if delta == 0:
            out.append(finding("last_push", "match", fetched_date))
        elif abs(delta) == 1:
            # GitHub shows dates in the viewer's time zone; a commit near midnight can fall on the adjacent UTC day
            out.append(finding("last_push", "match", "%s, evidence %s (UTC): one day apart, within the time zone tolerance" % (recorded.isoformat(), fetched_date)))
        elif delta > 0:
            # the dataset names a commit that the default branch does not show: likely a coding error or a different branch
            out.append(finding("last_push", "mismatch", "dataset %s is later than evidence %s (UTC): contradiction" % (recorded.isoformat(), fetched_date)))
        else:
            # the default branch has newer commits than the dataset: consistent with changes after coding on 17.11.2026
            out.append(finding("last_push", "mismatch", "dataset %s, evidence %s (UTC): newer commits after coding" % (recorded.isoformat(), fetched_date)))

    # archived
    recorded_arch = (row.get("repo_archived") or "").strip().lower()
    fetched_arch = repo.get("archived")
    if recorded_arch not in ("yes", "no"):
        out.append(finding("archived", "not_recorded", "repo_archived is %r" % row.get("repo_archived")))
    elif fetched_arch is None:
        out.append(finding("archived", "not_comparable", "no archived flag in evidence"))
    elif (recorded_arch == "yes") == bool(fetched_arch):
        out.append(finding("archived", "match", recorded_arch))
    else:
        out.append(finding("archived", "mismatch", "dataset %s, evidence archived=%s" % (recorded_arch, fetched_arch)))

    # licence class
    spdx = repo.get("spdx_licence")
    recorded_class = licence_class(row.get("repo_licence"))
    if spdx is None:
        out.append(finding("licence", "not_comparable", "no SPDX licence id in evidence"))
    else:
        evidence_class = licence_class(spdx)
        if recorded_class == "no repository licence read":
            out.append(finding("licence", "not_recorded", "repo_licence empty; evidence says %s" % spdx))
        elif recorded_class == evidence_class:
            out.append(finding("licence", "match", "%s (%s)" % (spdx, evidence_class)))
        else:
            out.append(finding("licence", "mismatch", "dataset class %r, evidence %s (%s)" % (recorded_class, spdx, evidence_class)))

    # version = version of a package in the repository (author's definition, 2026-11-18).
    # A corrected value carries no package name, so the check asks whether some package.json
    # of the repository has this version: the root first, then the monorepo members.
    recorded = (row.get("version") or "").strip()
    coded = parse_field_version(recorded)[1]
    if pkg_ev is None or pkg_ev.get("error"):
        out.append(finding("version", "not_comparable", "no package evidence (repository not read)"))
    elif coded is None:
        out.append(finding("version", "not_recorded", "dataset version %r has no version number" % recorded))
    else:
        packages = []
        if pkg_ev.get("root") and pkg_ev["root"].get("version"):
            packages.append(("root", pkg_ev["root"]["version"]))
        packages += [(o["path"], o["version"]) for o in usable_others(pkg_ev)]
        real = [(p, v) for p, v in packages if not v.startswith("0.0.")]
        same = [p for p, v in real if v == coded]
        if same:
            out.append(finding("version", "match", "%s found in %s" % (coded, same[0])))
        elif not real:
            out.append(finding("version", "not_comparable", "only placeholder versions (0.0.x) in the repository"))
        else:
            out.append(finding("version", "mismatch", "dataset %s, no package.json has it (packages: %s)"
                               % (coded, ", ".join("%s %s" % (p, v) for p, v in real[:4]))))
    return out


def compare_docs(row, ev):
    if ev is None:
        return [finding("docs", "missing_evidence", "no evidence file for %s" % row["docs_url"])]
    docs = ev.get("docs")
    if docs is None:
        return [finding("docs", "missing_evidence", "evidence file has no documentation section")]
    if docs.get("error"):
        return [finding("docs", "unavailable", str(docs.get("error")))]
    status = docs.get("http_status")
    if isinstance(status, int) and 200 <= status < 300 and docs.get("body_sha256"):
        # reachability only: the page content is not compared with anything in the dataset
        return [finding("docs", "fetched", "HTTP %d, body hash recorded" % status)]
    return [finding("docs", "unavailable", "HTTP %s" % status)]


def compare(rows, evidence, package_evidence=None):
    package_evidence = package_evidence or {}
    report = []
    for row in rows:
        ev = evidence.get(row["id"])
        findings = []
        if github_source(row):
            findings += compare_repo(row, ev, package_evidence.get(row["id"]))
        if docs_source(row):
            findings += compare_docs(row, ev)
        if not findings:
            findings.append(finding("sources", "no_source", "no repository or documentation URL in dataset"))
        status = ev.get("status") if ev else None
        report.append({"id": row["id"], "name": row["name"], "evidence_status": status, "findings": findings})
    return report


def summarise(report):
    counts = Counter()
    for entry in report:
        for f in entry["findings"]:
            counts[f["outcome"]] += 1
    return counts


def write_reports(report, counts, out_dir=RESULTS):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "compare_report.json"), "w", encoding="utf-8") as fh:
        json.dump({"counts": dict(counts), "records": report}, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")

    lines = ["# Comparison of the dataset with the evidence", "",
             "Offline comparison (`scripts/run_compare_from_evidence.py`). Every record is listed.", "",
             "## Counts by outcome", "", "| outcome | count |", "|---|---|"]
    for key in sorted(counts):
        lines.append("| %s | %d |" % (key, counts[key]))
    lines += ["", "## Records with a problem (missing, unavailable or mismatch)", ""]
    problem_entries = [e for e in report if any(f["outcome"] in PROBLEM_OUTCOMES for f in e["findings"])]
    if not problem_entries:
        lines.append("None.")
    for entry in problem_entries:
        lines.append("### %s - %s" % (entry["id"], entry["name"]))
        for f in entry["findings"]:
            if f["outcome"] in PROBLEM_OUTCOMES:
                lines.append("- %s: **%s** - %s" % (f["check"], f["outcome"], f["detail"]))
        lines.append("")
    lines += ["## All records", "", "| id | name | evidence | findings |", "|---|---|---|---|"]
    for entry in report:
        summary = "; ".join("%s=%s" % (f["check"], f["outcome"]) for f in entry["findings"])
        lines.append("| %s | %s | %s | %s |" % (entry["id"], entry["name"], entry["evidence_status"] or "none", summary))
    with open(os.path.join(out_dir, "compare_report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv=None, rows=None, evidence=None, out_dir=RESULTS):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="exit 1 on any missing, unavailable or mismatch")
    args = parser.parse_args(argv)

    rows = load_rows() if rows is None else rows
    evidence = load_evidence() if evidence is None else evidence
    report = compare(rows, evidence, load_package_evidence())
    counts = summarise(report)
    write_reports(report, counts, out_dir)

    total_records = len(rows)
    print("records: %d | evidence files: %d" % (total_records, len(evidence)))
    print(", ".join("%s=%d" % kv for kv in sorted(counts.items())))
    problems = sum(counts[k] for k in PROBLEM_OUTCOMES)
    if args.strict and problems:
        print("strict: %d problem findings" % problems)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
