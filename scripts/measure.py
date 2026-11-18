#!/usr/bin/env python3
"""Descriptive measures for the cleaned dataset.

Reads  data/design_systems.csv
Writes results/summary.json   all counts, machine-readable
       results/summary.md     the same counts as Markdown tables
       results/by_type.csv, by_sector.csv, by_licence_class.csv, by_verification.csv

Classification rules are heuristics documented in README.md (section "Measures"):
  licence class   from the `repo_licence` field, matched by keyword
  verification    from the `status` field: starts with "checked" -> checked, otherwise not checked
  last push year  first four digits of `repo_last_push`

Standard library only.
"""
import csv
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import licence_class  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "data", "design_systems.csv")
OUT = os.path.join(ROOT, "results")

def verification(status):
    return "checked" if (status or "").strip().lower().startswith("checked") else "not checked or unavailable"


def last_push_year(value):
    match = re.match(r"\s*(\d{4})", value or "")
    return match.group(1) if match else "none"


def read_version():
    with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as fh:
        return fh.read().strip()


def load(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def tally(rows, key_fn):
    return Counter(key_fn(r) for r in rows)


def write_table(path, header, counter):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        for key, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
            writer.writerow([key, count])


def md_table(title, header, counter):
    lines = ["## " + title, "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for key, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append("| %s | %d |" % (key, count))
    lines.append("")
    return "\n".join(lines)


def main():
    rows = load(SOURCE)
    n = len(rows)

    by_type = tally(rows, lambda r: r["type"])
    by_sector = tally(rows, lambda r: r["sector"])
    by_licence = tally(rows, lambda r: licence_class(r["repo_licence"]))
    by_verif = tally(rows, lambda r: verification(r["status"]))
    by_sample = tally(rows, lambda r: r["sample"])
    by_archived = tally(rows, lambda r: r["repo_archived"] or "empty")
    by_push_year = tally(rows, lambda r: last_push_year(r["repo_last_push"]))

    version = read_version()
    summary = {
        "release": version,
        "records": n,
        "by_type": dict(by_type),
        "by_sector": dict(by_sector),
        "by_licence_class": dict(by_licence),
        "by_verification": dict(by_verif),
        "by_sample": dict(by_sample),
        "by_repo_archived": dict(by_archived),
        "by_last_push_year": dict(by_push_year),
    }

    # Internal consistency: every grouping must add up to the number of records.
    for name in ["by_type", "by_sector", "by_licence_class", "by_verification", "by_sample"]:
        total = sum(summary[name].values())
        if total != n:
            sys.exit("error: %s sums to %d, expected %d" % (name, total, n))

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")

    write_table(os.path.join(OUT, "by_type.csv"), ["type", "count"], by_type)
    write_table(os.path.join(OUT, "by_sector.csv"), ["sector", "count"], by_sector)
    write_table(os.path.join(OUT, "by_licence_class.csv"), ["licence_class", "count"], by_licence)
    write_table(os.path.join(OUT, "by_verification.csv"), ["verification", "count"], by_verif)

    md = ["# Summary of data/design_systems.csv", "", "Release: %s" % version, "", "Records: %d" % n, ""]
    md.append(md_table("By type", ["type", "count"], by_type))
    md.append(md_table("By sector", ["sector", "count"], by_sector))
    md.append(md_table("By repository licence class", ["class", "count"], by_licence))
    md.append(md_table("By verification status", ["status", "count"], by_verif))
    md.append(md_table("Sample flag", ["sample", "count"], by_sample))
    md.append(md_table("Repository archived", ["value", "count"], by_archived))
    md.append(md_table("Year of last repository push", ["year", "count"], by_push_year))
    with open(os.path.join(OUT, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))

    print("release %s | records: %d | summary written to %s" % (version, n, os.path.relpath(OUT, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
