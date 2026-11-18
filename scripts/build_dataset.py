#!/usr/bin/env python3
"""Rebuild the dataset CSV files from the published page source.

Input:  source/index.html  (the page; its embedded `const DATA = [...]` array is the record set)
Output: data/design_systems_raw.csv   every record exactly as extracted (302 rows)
        data/design_systems.csv       cleaned records (duplicates removed, ne/da normalised)
        data/removed_duplicates.csv   every removed record, with the id of the record kept

Standard library only. Output is deterministic: running the script twice gives identical bytes,
which tests/test_dataset.py checks.

Usage:
    python3 scripts/build_dataset.py [--source source/index.html] [--out data]
"""
import argparse
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Duplicate decisions. Each removed record refers to the same repository (or the same product name)
# as the record kept. The kept record is the one whose repository was read (LICENSE, README).
# Keys: removed id -> (kept id, reason). Reasons are copied into data/removed_duplicates.csv.
DUPLICATE_DECISIONS = {
    "94": ("55", "Same repository (microsoft/fluentui). Record 94 was redirected to fluent2.microsoft.design and has no licence or release data.", []),
    "114": ("225", "Same product name and repository (porsche-design-system). Record 225 has the repository LICENSE read and the repository licence recorded; record 114 has no repository licence data.", []),
    "132": ("205", "Same repository (Shopify/polaris). Record 132 was redirected to shopify.dev and not opened; record 205 has the repository LICENSE read.", []),
    "140": ("204", "Same repository (Telefonica/mistica). Record 140 was redirected to a brand site and not rendered; record 204 has the repository read.", []),
    "207": ("150", "Same product (CMS design system; same documentation URL https://design.cms.gov/ and same version 18.2.0). Record 150 keeps its sample flag and documentation links. The empty repository fields of record 150 are filled from record 207 (see MERGE_FIELDS).", ["repo_url", "repo_licence", "repo_last_push", "repo_archived"]),
}

# Values that are normalised in the cleaned file. Raw values are kept in design_systems_raw.csv.
VALUE_NORMALISATION = {
    "repo_archived": {"ne": "no", "da": "yes"},
}

PAGE_DATA_RE = re.compile(r"const DATA = (\[.*?\]);\n", re.S)


def load_records(source_path):
    with open(source_path, encoding="utf-8") as fh:
        html = fh.read()
    match = PAGE_DATA_RE.search(html)
    if not match:
        sys.exit("error: no `const DATA = [...]` array found in %s" % source_path)
    records = json.loads(match.group(1))
    return records


def columns_of(records):
    cols = []
    for rec in records:
        for key in rec:
            if key not in cols:
                cols.append(key)
    return cols


def write_csv(path, rows, columns):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def clean(records):
    """Return (kept_records, removed_rows) following DUPLICATE_DECISIONS and VALUE_NORMALISATION.

    For a decision with a fill list, empty fields of the kept record are filled from the removed
    record. Non-empty fields of the kept record are never overwritten.
    """
    ids = {r["id"] for r in records}
    for removed, (kept, _, _) in DUPLICATE_DECISIONS.items():
        if removed not in ids or kept not in ids:
            sys.exit("error: duplicate decision refers to a missing id: %s -> %s" % (removed, kept))

    by_id = {r["id"]: dict(r) for r in records}
    removed_rows = []
    for removed_id, (kept_id, reason, fill_fields) in DUPLICATE_DECISIONS.items():
        removed_rec = by_id[removed_id]
        kept_rec = by_id[kept_id]
        for field in fill_fields:
            if not kept_rec.get(field) and removed_rec.get(field):
                kept_rec[field] = removed_rec[field]
        row = dict(removed_rec)
        row["removed_id"] = removed_id
        row["kept_id"] = kept_id
        row["kept_name"] = kept_rec["name"]
        row["reason"] = reason
        removed_rows.append(row)
    removed_rows.sort(key=lambda r: int(r["removed_id"]))

    kept = []
    for rec in records:
        if rec["id"] in DUPLICATE_DECISIONS:
            continue
        new = by_id[rec["id"]]
        for field, mapping in VALUE_NORMALISATION.items():
            if field in new and new[field] in mapping:
                new[field] = mapping[new[field]]
        kept.append(new)
    return kept, removed_rows


def build(source, out_dir):
    records = load_records(source)
    cols = columns_of(records)

    write_csv(os.path.join(out_dir, "design_systems_raw.csv"), records, cols)

    cleaned, removed = clean(records)
    write_csv(os.path.join(out_dir, "design_systems.csv"), cleaned, cols)

    removed_cols = ["removed_id", "kept_id", "kept_name", "name", "type", "repo_url", "status", "reason"]
    write_csv(os.path.join(out_dir, "removed_duplicates.csv"), removed, removed_cols)

    return len(records), len(cleaned), len(removed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", default=os.path.join(ROOT, "source", "index.html"))
    parser.add_argument("--out", default=os.path.join(ROOT, "data"))
    args = parser.parse_args(argv)
    raw, clean_n, removed_n = build(args.source, args.out)
    print("raw records: %d | cleaned: %d | removed duplicates: %d" % (raw, clean_n, removed_n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
