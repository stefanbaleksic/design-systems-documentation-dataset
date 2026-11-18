#!/usr/bin/env python3
"""Release bookkeeping: write and check release.json.

release.json ties one release together:
  * the version (VERSION file, SemVer),
  * the page snapshot it was built from (source/SOURCE.json and source/index.html checksum),
  * the checksums of the data files,
  * the record counts.

Commands:
    python3 scripts/release.py manifest   write release.json from the current files
    python3 scripts/release.py check      verify that release.json, VERSION, CHANGELOG.md and the
                                          files agree; exit 1 with the list of problems otherwise
"""
import csv
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import is_valid_semver  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILES = ["design_systems.csv", "design_systems_raw.csv", "removed_duplicates.csv", "corrections.csv"]


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def count_rows(path):
    """Number of data rows in a CSV file with a header line."""
    with open(path, encoding="utf-8", newline="") as fh:
        return max(sum(1 for _ in csv.reader(fh)) - 1, 0)


def read_text(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def build_manifest(root=ROOT):
    version = read_text(root, "VERSION").strip()
    source_meta = json.loads(read_text(root, "source/SOURCE.json"))
    raw_count = count_rows(os.path.join(root, "data", "design_systems_raw.csv"))
    clean_count = count_rows(os.path.join(root, "data", "design_systems.csv"))
    removed_count = count_rows(os.path.join(root, "data", "removed_duplicates.csv"))
    return {
        "version": version,
        "artifact": {k: source_meta[k] for k in ["artifact_url", "artifact_version_id", "retrieved_on_local_date", "retrieved_time_zone"]},
        "source": {"file": "source/index.html", "sha256": sha256(os.path.join(root, "source", "index.html"))},
        "records": {"raw": raw_count, "clean": clean_count, "removed_duplicates": removed_count},
        "data_sha256": {name: sha256(os.path.join(root, "data", name)) for name in DATA_FILES},
    }


def write_manifest(root=ROOT):
    manifest = build_manifest(root)
    with open(os.path.join(root, "release.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    return manifest


def check(root=ROOT):
    """Return a list of problems. An empty list means the release is consistent."""
    problems = []
    try:
        version = read_text(root, "VERSION").strip()
    except OSError:
        return ["VERSION file is missing"]
    if not is_valid_semver(version):
        problems.append("VERSION is not a valid SemVer: %r" % version)

    try:
        stored = json.loads(read_text(root, "release.json"))
    except (OSError, ValueError):
        return problems + ["release.json is missing or not valid JSON; run `release.py manifest`"]

    current = build_manifest(root)
    if stored.get("version") != version:
        problems.append("release.json version %r differs from VERSION %r" % (stored.get("version"), version))
    for key in ["artifact", "source", "records", "data_sha256"]:
        if stored.get(key) != current.get(key):
            problems.append("release.json field %r does not match the files on disk" % key)

    changelog = read_text(root, "CHANGELOG.md")
    if not re.search(r"^## \[%s\] - \d{4}-\d{2}-\d{2}$" % re.escape(version), changelog, re.M):
        problems.append("CHANGELOG.md has no heading '## [%s] - yyyy-mm-dd'" % version)

    source_meta = json.loads(read_text(root, "source/SOURCE.json"))
    if source_meta.get("file") != "index.html":
        problems.append("source/SOURCE.json points at an unexpected file")
    recorded = {}
    with open(os.path.join(root, "source", "SHA256SUMS"), encoding="utf-8") as fh:
        for line in fh:
            digest, name = line.split()
            recorded[name] = digest
    if recorded.get("index.html") != sha256(os.path.join(root, "source", "index.html")):
        problems.append("source/index.html does not match source/SHA256SUMS")
    return problems


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["manifest"]:
        manifest = write_manifest()
        print("wrote release.json for version %s" % manifest["version"])
        return 0
    if argv == ["check"]:
        problems = check()
        if problems:
            for p in problems:
                print("problem: " + p)
            return 1
        print("release consistent")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
