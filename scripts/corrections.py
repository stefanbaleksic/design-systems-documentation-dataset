#!/usr/bin/env python3
"""Evidence-based corrections to the repository fields of the dataset.

Two commands:

  propose   read evidence/ and data/design_systems.csv and write data/corrections.csv
            (one row per field change, with the basis and the evidence timestamp).
            Also writes results/open_items.md: the differences that are NOT corrected, with reasons.

  apply     apply data/corrections.csv to the DATA array in source/index.html.
            Each change is applied only if the record still holds the old value; a record that
            already holds the new value is skipped; anything else is a conflict and stops the run.
            Each changed record gets a dated note with the old value.

Rules for what is corrected (see README, "Corrections"):
  repo_last_push  set to the evidence date when the coded date differs by more than one day
                  (UTC), and fill it when it is empty or not a date.
  repo_licence    fill it when empty, or correct it when it says "none or not identified" and the
                  evidence names a licence. A coded class of "other or custom" is never overwritten
                  automatically: those cases go to the open items.
  version         never changed automatically. The field names a package or a version, and the
                  evidence names the repository's newest stable tag. Those are different things.
  archived        not in the evidence (git cannot read it). Never changed.

Standard library only.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import licence_class, parse_last_push  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "source", "index.html")
DATA_CSV = os.path.join(ROOT, "data", "design_systems.csv")
CORRECTIONS = os.path.join(ROOT, "data", "corrections.csv")
EVIDENCE = os.path.join(ROOT, "evidence")
OPEN_ITEMS = os.path.join(ROOT, "results", "open_items.md")
PAGE_DATA_RE = re.compile(r"const DATA = (\[.*?\]);\n", re.S)
FIELDS = ["id", "name", "field", "old_value", "new_value", "basis", "evidence_collected_utc", "evidence_source"]
UNCHANGED_CLASSES = {"none or not identified", "no repository licence read"}


def load_rows(path=DATA_CSV):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_evidence(directory=EVIDENCE):
    found = {}
    for name in os.listdir(directory):
        if name.endswith(".json"):
            with open(os.path.join(directory, name), encoding="utf-8") as fh:
                data = json.load(fh)
            found[str(data["id"])] = data
    return found


def propose(rows, evidence, page_by_id=None):
    """Return (corrections, open_items). Pure function: no files are read or written here.

    `page_by_id` gives the values as they stand in source/index.html. The old value of a
    correction is taken from there, because that is what apply() checks. For a merged record
    (ID 150) the cleaned row takes values from another record, so the two can differ.
    """
    corrections, open_items = [], []
    page_by_id = page_by_id or {}
    for row in rows:
        rec_id = row["id"]
        page = page_by_id.get(rec_id, row)
        repo = (evidence.get(rec_id) or {}).get("repo")
        if not repo or repo.get("api", {}).get("error"):
            continue
        collected = evidence[rec_id]["collected_at_utc"]
        source = row["repo_url"]

        # repo_last_push
        fetched = repo.get("pushed_at_utc")
        if fetched:
            fetched_date = dt.date.fromisoformat(fetched[:10])
            try:
                coded = parse_last_push(row["repo_last_push"])
            except ValueError:
                coded = None
            new = "%s (last commit date)" % fetched_date.isoformat()
            if coded is None:
                corrections.append(make(row, "repo_last_push", page["repo_last_push"], new,
                                        "empty or not a date; filled from the default branch", collected, source))
            elif abs((coded - fetched_date).days) > 1:
                why = ("newer commits on the default branch after coding" if coded < fetched_date
                       else "coded date is later than the newest commit on the default branch")
                corrections.append(make(row, "repo_last_push", page["repo_last_push"], new, why, collected, source))

        # repo_licence
        spdx = repo.get("spdx_licence")
        licence_file = repo.get("licence_file")
        if spdx and licence_file:
            value = "%s (%s)" % (spdx, licence_file)
            current_class = licence_class(row["repo_licence"])
            if current_class in UNCHANGED_CLASSES:
                basis = "coded as missing or not identified; licence text in the repository matches %s" % spdx
                corrections.append(make(row, "repo_licence", page["repo_licence"], value, basis, collected, source))
            elif current_class != licence_class(value):
                open_items.append({"id": rec_id, "name": row["name"], "field": "repo_licence",
                                   "detail": "coded %r (%s), evidence %s from %s; not changed automatically"
                                             % (row["repo_licence"], current_class, spdx, licence_file)})

        # version: decided by propose_version() against package.json, not against git tags
    return corrections, open_items


def propose_version(rows, package_evidence, page_by_id):
    """Version = version of the package (author's definition, 2026-11-18).

    `package_evidence` maps id -> evidence/package/<id>.json content. The candidate
    package.json is chosen as follows:
      * if the coded value names a package (for example "@artsy/palette@46.11.0"), the
        package.json with that name is used; no match is an open item;
      * otherwise the root package.json is used when it has a version;
      * otherwise the only package.json with a version is used;
      * otherwise (several candidates, none at the root) it is an open item.
    A coded value that differs from the chosen version is corrected to that version.
    An empty value or a value without a version number ("not stated", "NOVA") is filled
    from the chosen version. The package name goes into the basis, not the value.
    """
    corrections, open_items = [], []
    for row in rows:
        rec_id = row["id"]
        ev = package_evidence.get(rec_id)
        if not ev or ev.get("error"):
            continue
        page = page_by_id.get(rec_id, row)
        coded_raw = page.get("version", "")
        coded_version = parse_field_version(coded_raw)[1]
        status, chosen = choose_package(coded_raw, ev)
        if status == "open":
            open_items.append({"id": rec_id, "name": row["name"], "field": "version", "detail": chosen})
            continue
        if status == "none":
            continue  # no package version in the repository; nothing to compare
        path, name, version = chosen
        if version.startswith("0.0."):
            # 0.0.x is usually a placeholder in private or monorepo root manifests; not filled automatically
            open_items.append({"id": rec_id, "name": row["name"], "field": "version",
                               "detail": "package.json (%s) has version %s, probably a placeholder; not changed" % (path, version)})
            continue
        if coded_version == version:
            continue
        basis = "package version from %s%s" % (path, " (%s)" % name if name else "")
        if coded_version:
            basis = "coded %s differs from %s" % (coded_version, basis)
        else:
            basis = "coded value has no version number; filled from %s" % basis
        corrections.append(make(row, "version", coded_raw, version, basis,
                                ev["collected_at_utc"], ev.get("repo_url", "")))
    return corrections, open_items


def choose_package(coded_raw, ev):
    """Pick the package.json whose version is the package version.

    Returns ("chosen", (path, name, version)), ("open", reason) or ("none", None).
    Used by propose_version() and by run_compare_from_evidence.py, so both agree.
    """
    coded_name, _ = parse_field_version(coded_raw)
    candidates = []
    if ev.get("root") and ev["root"].get("version"):
        candidates.append(("root", ev["root"].get("name"), ev["root"]["version"]))
    for entry in usable_others(ev):
        candidates.append((entry["path"], entry.get("name"), entry["version"]))
    if coded_name:
        named = [c for c in candidates if c[1] and _same_package(c[1], coded_name)]
        if len(named) == 1:
            return "chosen", named[0]
        return "open", "coded package %r; %d package.json with that name and a version; not changed" % (coded_name, len(named))
    if not candidates:
        return "none", None
    roots = [c for c in candidates if c[0] == "root"]
    if roots:
        return "chosen", roots[0]
    if len(candidates) == 1:
        return "chosen", candidates[0]
    return "open", "%d packages with versions and none at the root; not changed" % len(candidates)


def usable_others(ev):
    """Monorepo member manifests with a version, excluding vendored dependencies."""
    return [o for o in ev.get("others", []) if o.get("version") and "node_modules/" not in o["path"]]


def _same_package(found, coded):
    if found == coded:
        return True
    return found.split("/")[-1] == coded.split("/")[-1] and ("/" not in found or "/" not in coded or found.split("/")[0] == coded.split("/")[0])


def parse_field_version(value):
    """Return (package_name or None, version or None) from a coded version field."""
    value = (value or "").strip()
    match = re.match(r"^(?:(@?[^@\s()]+(?:/[^@\s()]+)?)@)?(\d+\.\d+\.\d+[0-9A-Za-z.\-+]*)", value)
    if not match:
        return None, None
    return match.group(1), match.group(2)


def merge_corrections(existing, new):
    """Append-only: keep every existing row, add new rows that are not already present."""
    seen = {(r["id"], r["field"], r["new_value"]) for r in existing}
    return existing + [r for r in new if (r["id"], r["field"], r["new_value"]) not in seen]


def read_corrections_file(path=CORRECTIONS):
    if not os.path.exists(path):
        return []
    return load_corrections(path)


def make(row, field, old, new, basis, collected, source):
    return {"id": row["id"], "name": row["name"], "field": field, "old_value": old, "new_value": new,
            "basis": basis, "evidence_collected_utc": collected, "evidence_source": source}


def write_corrections(corrections, path=CORRECTIONS):
    corrections = sorted(corrections, key=lambda c: (int(c["id"]), c["field"]))
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(corrections)


def write_open_items(open_items, path=OPEN_ITEMS):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ["# Open items", "", "Differences between the coded dataset and the evidence that were not corrected automatically.", ""]
    for item in sorted(open_items, key=lambda i: (int(i["id"]), i["field"])):
        lines.append("- %s %s (%s): %s" % (item["id"], item["name"], item["field"], item["detail"]))
    lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def apply(corrections, page=PAGE):
    """Apply corrections to the DATA array. Returns (applied, skipped). Raises on conflict."""
    with open(page, encoding="utf-8") as fh:
        text = fh.read()
    match = PAGE_DATA_RE.search(text)
    if not match:
        raise SystemExit("error: no DATA array in %s" % page)
    data = json.loads(match.group(1))
    by_id = {}
    for rec in data:
        by_id.setdefault(rec["id"], rec)

    applied = skipped = 0
    for c in corrections:
        rec = by_id.get(c["id"])
        if rec is None:
            raise SystemExit("error: correction refers to unknown record %s" % c["id"])
        current = rec.get(c["field"], "")
        if current == c["new_value"]:
            skipped += 1
            continue
        if current != c["old_value"]:
            raise SystemExit("error: record %s %s is %r, expected %r: conflict, nothing written"
                             % (c["id"], c["field"], current, c["old_value"]))
        rec[c["field"]] = c["new_value"]
        day = c["evidence_collected_utc"][:10]
        note = "Corrected %s from evidence (%s): %s was %r, now %r." % (
            "%s.%s.%s" % (day[8:10], day[5:7], day[:4]), c["basis"], c["field"], c["old_value"], c["new_value"])
        rec["note"] = (rec["note"] + " " if rec["note"] else "") + note
        applied += 1

    new_text = text[:match.start(1)] + json.dumps(data, ensure_ascii=False) + text[match.end(1):]
    with open(page, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    return applied, skipped


def page_records(page=PAGE):
    """Records as they stand in the page (before cleaning), by id."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_dataset  # noqa: E402
    return {r["id"]: r for r in build_dataset.load_records(page)}


def load_corrections(path=CORRECTIONS):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_package_evidence(directory=os.path.join(ROOT, "evidence", "package")):
    found = {}
    if not os.path.isdir(directory):
        return found
    for name in os.listdir(directory):
        if name.endswith(".json"):
            with open(os.path.join(directory, name), encoding="utf-8") as fh:
                data = json.load(fh)
            found[str(data["id"])] = data
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["propose", "apply"])
    args = parser.parse_args(argv)
    if args.command == "apply":
        applied, skipped = apply(load_corrections())
        print("applied: %d | already applied: %d" % (applied, skipped))
        return 0
    rows, pages = load_rows(), page_records()
    licence, licence_open = propose(rows, load_evidence(), pages)
    version, version_open = propose_version(rows, load_package_evidence(), pages)
    existing = read_corrections_file()
    merged = merge_corrections(existing, licence + version)
    write_corrections(merged)
    write_open_items(licence_open + version_open)
    print("new corrections: %d (licence and last push: %d, version: %d) | open items: %d"
          % (len(merged) - len(existing), len(licence), len(version), len(licence_open) + len(version_open)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
