# Contributing

Thank you for checking the data. There are three kinds of contribution.

## 1. Report a wrong or outdated fact

Open an issue with: record ID (the `id` column), the field, the value in the dataset, the value you found, the URL you checked, and the date you checked it (dd.mm.yyyy). Do not edit the CSV files in the issue; that is done by the maintainer or in a pull request.

## 2. Propose a correction (pull request)

The single source of the data is the `DATA` array inside `source/index.html`. The CSV files are generated from it. Do not edit the CSV files by hand.

1. Edit the record in the `DATA` array of `source/index.html`. Keep the JSON valid and keep the record `id` unique.
2. Update the checksum: `sha256sum source/index.html > source/SHA256SUMS`.
3. Run the checks (below). They must pass.
4. Add an entry under `## [Unreleased]` in `CHANGELOG.md` using the categories in "Changelog rules".
5. Do not change `release.json` or `VERSION` in a pull request. The maintainer does that at release time.

A duplicate removal is a decision in `DUPLICATE_DECISIONS` in `scripts/build_dataset.py`, with a reason. Add it there, not by deleting the record silently.

## Checks

```bash
python3 scripts/build_dataset.py
python3 scripts/measure.py
python3 -m unittest discover -s tests -v
python3 scripts/release.py check
```

`release.py check` fails after a data change until the maintainer runs `python3 scripts/release.py manifest` and updates the version. That is intended: a data change is not a release until it is versioned.

## Changelog rules

The changelog follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

- Every user-visible change gets an entry under `## [Unreleased]`, in one of these sections: **Added**, **Changed**, **Deprecated**, **Removed**, **Fixed**, **Security**.
- Write one line per change, in the past tense, with the record IDs where relevant.
- A fact correction is **Fixed** (or **Changed** if the meaning of a field changes).
- A new record is **Added**. A removed record is **Removed** and must name the kept record and the reason (see `data/removed_duplicates.csv`).
- Never delete or rewrite a released section. Corrections go into a new version.
- The date in a release heading is the release date in UTC (`yyyy-mm-dd`). The test that checks the heading is in `scripts/release.py`.

## Versioning rules (SemVer 2.0.0)

The version in `VERSION` describes the dataset and the scripts together.

- **MAJOR** (2.0.0): a column is removed or renamed; the meaning of a column changes; the ID scheme changes; or a script changes its output format in a way that breaks existing reproduction.
- **MINOR** (1.1.0): records are added; a column is added; a new script or command is added.
- **PATCH** (1.0.1): values are corrected; notes are fixed; a script is fixed without changing its output format.

Pre-release versions (for example `2.0.0-rc.1`) are used when a change needs review before it is final.

## Dates and time zones

- The `checked` field is a date in dd.mm.yyyy, in the author's local time zone (Europe/Belgrade).
- Timestamps in evidence files are UTC, written as `yyyy-mm-ddThh:mm:ssZ`.
- `repo_last_push` is a commit date. The scripts compare it as a UTC calendar date.
- Convert with `scripts/common.py` (`parse_iso_to_utc`, `format_utc`), not by hand. Tests cover conversion across midnight and across offsets.

## Code style

- Standard library only. Do not add a dependency without a discussion in an issue.
- Every script has a `--help` text that describes what it reads and writes.
- Every behaviour change has a test in `tests/`.
