# Design System Documentation Dataset

A dataset of publicly documented design systems, UI libraries and style guidelines. For each entry it records the documentation and repository facts as coded by the author: licence, repository, release, last-push data, archive status, and a verification status.

- **Release:** 1.0.0 (see `VERSION`, `release.json`, `CHANGELOG.md`).
- **Records:** 297 cleaned (302 extracted; 5 duplicates removed). The published page lists the 302 extracted entries, so its counts (for example 254 checked and 157 with a licence) are before duplicate removal. The counts in this README are for the 297 cleaned entries.
- **Checked:** 17 November 2026 (list from the awesome-design-systems list on GitHub, web search and documentation). **Evidence collected:** 18 November 2026 (documentation pages and repositories).
- **Evidence:** documentation pages were fetched for 180 of 210 documentation URLs. Repository facts were read over git for 214 of 221 GitHub repositories.
- **Corrections:** 280 field values were corrected from the evidence (179 repository, 101 version), as recorded in `data/corrections.csv` (see "Corrections"). The differences that remain are listed in `results/open_items.md`.
- **DOI:** to be added after deposit on Zenodo.

## Contents

| Path | What it is |
|---|---|
| `source/index.html` | The published page. Its `DATA` array is the single source of the records. |
| `source/SOURCE.json`, `source/SHA256SUMS` | Which page version was used (artifact version `1794905101-55af`) and its checksum. |
| `data/design_systems.csv` | The cleaned dataset (297 rows). Use this file for analysis. |
| `data/design_systems_raw.csv` | All 302 records as extracted, before cleaning. |
| `data/removed_duplicates.csv` | The 5 removed records, with the kept ID and the reason. |
| `evidence/` | One JSON file per record: what the collector got from GitHub and from the documentation page. See `evidence/README.md`. |
| `results/` | Descriptive tables (`summary.md`, `summary.json`, CSVs) and the comparison report (`compare_report.md`, `compare_report.json`). |
| `scripts/build_dataset.py` | Builds the CSV files from `source/index.html`. |
| `scripts/measure.py` | Writes the descriptive tables to `results/`. |
| `scripts/collect.py` | Collects evidence into `evidence/`. Needs network access. |
| `scripts/run_compare_from_evidence.py` | Compares the dataset with `evidence/`. Offline. |
| `scripts/release.py` | Writes and checks `release.json`. |
| `scripts/corrections.py` | Proposes evidence-based corrections (`propose`) and applies them to the page data (`apply`). |
| `data/corrections.csv` | Every correction: record, field, old value, new value, basis, evidence timestamp. |
| `results/open_items.md` | Differences that were not corrected automatically, with the reason. |
| `evidence/package/` | Package versions from each repository: the root `package.json` and the other `package.json` files, over git. Written by `scripts/collect_package.py`. |
| `scripts/common.py` | UTC conversion, SemVer parsing and comparison, licence classes. |
| `tests/` | 90 tests for all scripts. Standard library only. |
| `VERSION`, `release.json`, `CHANGELOG.md` | Release identity, release manifest, change history. |
| `CONTRIBUTING.md` | How to report and propose corrections; changelog and versioning rules. |
| `CITATION.cff` | Citation metadata for GitHub and Zenodo. |
| `.github/workflows/tests.yml` | Runs the unit tests and the release check on each push and pull request. |
| `SECURITY.md` | How to report a vulnerability; what the scripts guarantee. |
| `LICENSE`, `LICENSE-DATA` | MIT for code and documentation; CC BY 4.0 for the dataset content. |

## Quick start

Requires Python 3.8 or newer. No third-party packages.

```bash
python3 -m unittest discover -s tests -v   # run all tests (no network)
python3 scripts/build_dataset.py           # rebuild data/*.csv from source/index.html
python3 scripts/measure.py                 # rebuild results/ tables
python3 scripts/run_compare_from_evidence.py   # compare the dataset with evidence/ (offline)
python3 scripts/release.py check           # verify release.json, VERSION, CHANGELOG, checksums
```

`build_dataset.py` is deterministic. The test `test_rebuild_is_byte_identical` rebuilds the CSV files in a temporary folder and compares them with the committed files.

## Collecting evidence (needs network)

```bash
python3 scripts/collect.py --dry-run                      # list what would be fetched; no requests
GITHUB_TOKEN=... python3 scripts/collect.py               # API route for repositories, and documentation
python3 scripts/collect.py --repo-source git --skip-docs  # repositories over git, keep documentation evidence
python3 scripts/collect.py --ids 55,94                    # re-collect selected records
```

- `--repo-source api` uses the GitHub REST API. It needs access to `api.github.com`. Without a token, GitHub's unauthenticated rate limit applies. The token is read from the environment, sent only as an `Authorization` header, and never written to a file.
- `--repo-source git` uses git over HTTPS. `git ls-remote` gives the tags and the default branch. A shallow, blobless clone gives the date of the latest commit and the `LICENSE` file. Archived status cannot be read this way and is recorded as `null`.
- `--skip-docs` and `--skip-repo` keep the existing section of each evidence file, so one part can be re-collected without repeating the other.
- `--delay` sets the wait between requests (default 0).
- Every attempt is recorded, including failures. A record is never left out.

Then run `python3 scripts/run_compare_from_evidence.py --strict` to list every missing, unavailable or mismatching item. Exit status 1 means at least one such item remains.

## Evidence coverage in release 1.0.0

Collected on 18 November 2026, between 09:11 and 09:50 UTC. The documentation pages were fetched first. The repository facts were then collected again with the git route.

| Source | Attempted | Fetched | Unavailable |
|---|---|---|---|
| Documentation pages (HTTP) | 210 | 180 | 30 |
| GitHub repositories, API route (`api.github.com`) | not recorded | not recorded | in an earlier attempt, requests returned HTTP 403; the evidence files record the git route only |
| GitHub repositories, package.json files (git route, `scripts/collect_package.py`) | 221 | 214 | 7 (the same repositories as in "Repository failures" below) |
| GitHub repositories, git route (`git ls-remote`, shallow clone) | 221 | 214 | 7 |

- **Documentation failures (30):** HTTP 403 (18), HTTP 404 (2), refused because the URL is `http://` (1, record 28), connection or TLS errors (9), including one certificate that the site presented as expired. The 18 HTTP 403 responses may be bot protection; the cause was not confirmed. The collector does not try to get around them.
- **Repository failures (7):** git asked for credentials, which means the repository is private, renamed or removed; git cannot tell these apart. The dataset's `repo_url` is kept as published.
- **Evidence status per record:** `ok` for 263 records, `partial` for 23, `failed` for 11. `failed` means that no source answered. It is not a judgement of the entry.

## Corrections

Corrections are evidence-based changes to the dataset fields. They are made by `scripts/corrections.py`, and every change is listed in `data/corrections.csv` with its old value, new value, basis, and evidence timestamp. The file is append-only: a later run adds rows and never removes earlier ones.

- `propose` reads `evidence/` and `evidence/package/`, adds the new corrections to `data/corrections.csv`, and writes `results/open_items.md`.
- `apply` writes the changes into the `DATA` array of `source/index.html`. A change is applied only if the record still holds the old value. A record that already holds the new value is skipped. Any other value stops the run, and nothing is written. The record's `note` gets a dated line with the old value.

Applied to release 1.0.0 (18 November 2026):

| Field | Change | Count | Basis |
|---|---|---|---|
| `repo_last_push` | filled (was empty or `not checked`) | 82 | commit date of the default branch, from git |
| `repo_last_push` | corrected, newer commits on the default branch | 20 | coded date older than the newest commit |
| `repo_last_push` | corrected, contradiction | 5 | coded date later than the newest commit (IDs 6, 9, 12, 19, 21) |
| `repo_licence` | filled (was empty) | 69 | licence text in `LICENSE` |
| `repo_licence` | corrected (was "none or not identified") | 3 | licence text in `LICENSE` (IDs 172, 179, 201) |
| `version` | filled (was "not stated" or had no version number) | 90 | version in the root `package.json` of the repository |
| `version` | corrected | 11 | the package.json version differs from the coded number |

**Rules.**

- `repo_last_push` is corrected only when the coded date differs from the evidence by more than one calendar day (UTC), because GitHub shows dates in the viewer's time zone.
- `repo_licence` is never overwritten when the coded class is "other or custom". The licence is identified from the text of the first licence file at the repository root, so the match is a heuristic. It is recorded as a text match, not as a licence the repository declares.
- `version` is the version of the package (the author's definition, 18 November 2026). The package is taken from `package.json` in the default branch, and not from a git tag. If the coded value names a package (for example `@artsy/palette@46.11.0`), that package is used. Otherwise the root `package.json` is used, or the only package with a version. In a monorepo with several versioned packages and no root version, the case is an open item. A version of `0.0.x` is treated as a placeholder and is an open item, not a correction.
- `archived` is never changed, because git cannot read it.

## Comparison results

After the corrections, `scripts/run_compare_from_evidence.py` gives these results, over all findings:

| Check | match | mismatch | not recorded | not comparable |
|---|---|---|---|---|
| last push (commit date) | 214 | 0 | 0 | 0 |
| licence class (from `LICENSE` text) | 182 | 2 | 0 | 30 |
| version (against `package.json` in the repository) | 128 | 14 | 71 | 1 |
| archived | 0 | 0 | 106 | 108 |

The comparison shows where the dataset and the evidence still differ. These rows are not corrections:

- **Licence, 2 mismatches (IDs 150 and 275).** ID 150 (CMS) is "mixed", and ID 275 (PrimeNG) has its own terms. The author decides these two licence values.
- **Version, 14 mismatches.** The coded value is not the version of any package in the repository. In most cases the coded value names a package that the repository does not have under that name, or several packages are candidates and none is the root. They are listed as open items with the reason.
- **Version, 71 not recorded.** The coded value has no version number, and the repository has no package version to fill it from, or the value is kept as the placeholder `not stated`.
- **Archived** cannot be read over git, so it is not compared.

## Comparison results

After the corrections, `scripts/run_compare_from_evidence.py` gives these results, over all findings:

| Check | match | mismatch | not recorded | not comparable |
|---|---|---|---|---|
| last push (commit date) | 214 | 0 | 0 | 0 |
| licence class (from `LICENSE` text) | 182 | 2 | 0 | 30 |
| version (against newest stable tag) | 50 | 44 | 68 | 52 |
| archived | 0 | 0 | 106 | 108 |

The comparison shows where the dataset and the evidence still differ, so these rows are not corrections. Their reasons are:

- **Licence, 2 mismatches (IDs 150 and 275).** ID 150 (CMS) is "mixed", and ID 275 (PrimeNG) has its own terms. The repository's first licence file says MIT, but that is not the whole picture. These need a decision by the author.
- **Version, 44 mismatches.** The `version` field often names a package or a major version. The evidence gives the newest stable tag of the whole repository, which is often a different package. A mismatch here does not show that the coded version is wrong. Changing the field would change its meaning, so this is an open question about the field's definition, not a correction. `results/open_items.md` lists all 163 version rows. 51 of them have `not stated`, which is kept as the placeholder.
- **Archived** cannot be read over git, so it is not compared.

## Columns

Each row is one entry. Columns in `design_systems.csv` (and `design_systems_raw.csv`):

- `id`: record ID from the page (unique).
- `name`, `type`, `sector`: the entry, its kind (Design system, UI library, Design system (government), Guidelines) and its sector.
- `status`: verification status as coded. Free text; starts with `checked` when the entry was verified.
- `checked`: collection date, dd.mm.yyyy, author's local time zone (Europe/Belgrade).
- `docs_url`, `repo_url`, `changelog`, `contributing`, `accessibility`, `governance`: links, or `not stated`.
- `licence`: licence of the documentation or site, as stated there.
- `repo_licence`: licence file found in the repository. Empty means no repository was read, not that no licence exists.
- `version`: version of the package, as corrected in release 1.0.0 (see "Corrections"). For a package that is not in the repository's `package.json` files, the coded value is kept.
- `repo_last_push`: date of the latest commit on the default branch (a commit date, compared as a UTC date).
- `repo_archived`: `yes`, `no`, or empty (not read).
- `sample`: `yes` or `no`, as coded by the author. The page does not define this column further.
- `source`, `case_study`, `note`: provenance and free-text notes. Some are in the source language.

## Cleaning rules

1. **Duplicates.** A record is removed when another record refers to the same repository or product. The kept record is the one whose repository was read. The decisions are in `DUPLICATE_DECISIONS` in `scripts/build_dataset.py`, and the removed rows are in `data/removed_duplicates.csv`.
   - CMS design system (IDs 150 and 207): record 150 is kept, because it has `sample=yes` and the documentation links. Its empty repository fields are filled from record 207. This is the only field-level merge (the fill list for ID 207 in `DUPLICATE_DECISIONS`, `scripts/build_dataset.py`).
2. **Value normalisation.** `repo_archived` values `ne` and `da` (Serbian for no and yes) become `no` and `yes`. The raw file keeps the original values.
3. **No other values are changed.** Licence text, notes and status strings keep the coder's wording.

## Known data issues in 1.0.0

Before the first commit, the URL problems found during collection were corrected in the `DATA` array of `source/index.html`. The old values are kept in each record's `note`, so no information is lost.

Corrected by hand:

- Documentation URLs that were `http://` now use `https://`, where the https address answered HTTP 200 on 18.11.2026: IDs 16, 96, 98 and 157. For ID 96 and ID 157 the https address redirects to a `www.` host, and the final address is recorded.
- ID 63: the redirect note `(redirected from material.io)` was moved out of `docs_url` into `note`. The URL is `https://m3.material.io/`, which answered HTTP 200.
- ID 57 and ID 107: `repo_url` held text, not a URL. The text `(not public)` and `(release notes only)` moved into `note`, and `repo_url` is empty.

Open:

- **ID 28** (`http://style.buildit.digital/`). The collector refuses `http://` by design, and the evidence says so (`refused: not https`), so this record has no documentation evidence. A manual recheck on 18 November 2026, outside the collector, gave HTTP 403 for `http://style.buildit.digital/`, and the connection was reset for `https://style.buildit.digital/`. The record is kept as published. Decide, with a different network, whether the address should change.
- The 7 repositories that git could not read (IDs 11, 14, 25, 38, 51, 79, 126) are kept, with their coded repository facts unverified. The evidence records that GitHub asked for credentials. That means the repository is private, renamed, or removed, and git cannot tell these apart.
- Four records have `repo_url` = `not stated`. This is the placeholder the dataset uses for "the source does not say". It is kept as is.
- The `sample` column has no definition on the page.
- One `repo_archived` value keeps its long form on purpose: `ne (README statement, not GitHub archive flag)`.
- The open items in `results/open_items.md` (83 rows: 2 licence and 81 version) need a decision by the author. The two licence rows (IDs 150 and 275) are the author's decision.

The tests `UrlQualityTests` enforce the URL rules. `CorrectionsTests` cover the correction rules, the package-version rules and the conflict stop. `PackageCollectTests` cover the package collector with a fake git runner. `test_repository_corrections_file_matches_the_dataset` checks that every correction is in the dataset.

## Measures

`scripts/measure.py` writes these heuristic classes. The rules are documented here so they can be checked.

- **Licence class** (from `repo_licence`, by keyword): *permissive* (MIT, Apache, BSD, ISC, CC0); *copyleft* (GPL, MPL, EUPL, CC BY-SA); *other or custom*; *none or not identified* (text such as "not stated"); *no repository licence read* (empty).
- **Verification** (from `status`): *checked* if the status starts with "checked"; otherwise *not checked or unavailable*.
- **Last push year**: the four-digit year at the start of `repo_last_push`.

Counts on the 297 cleaned records:

- Type: Design system 233, UI library 33, Design system (government) 19, Guidelines 12.
- Verification: checked 251, not checked or unavailable 46.
- Repository licence class: permissive 117, copyleft 4, other or custom 3, none or not identified 21, no repository licence read 152.

## Time zones and dates

- `checked` is a calendar date in Europe/Belgrade. It is not converted.
- Evidence timestamps are UTC, written `yyyy-mm-ddThh:mm:ssZ`.
- `repo_last_push` is a commit date and is compared as a UTC calendar date.
- `scripts/common.py` converts offsets to UTC and rejects naive timestamps. Tests cover offsets, midnight crossings and `Z` suffixes.
- Last push: the comparison treats a difference of one calendar day as a match. GitHub shows dates in the viewer's time zone, so a commit close to midnight can fall on the adjacent UTC day. A difference of more than one day is a mismatch, and the detail says whether the coded date is later (contradiction) or earlier (newer commits after coding).

## Versions

The version in `VERSION` is a SemVer 2.0.0 string. `scripts/common.py` implements precedence as the specification defines it.

The dataset's `version` field is the version of the package. The evidence for it is in `evidence/package/`, written by `scripts/collect_package.py`, which reads every `package.json` of the default branch over git. A coded value counts as matching when some `package.json` in the repository has that version. A date such as `16.11.2026` is never read as a version, and a version without a full three-part number (for example `v4.10`) is recorded as not recorded.

The rules for when to bump MAJOR, MINOR and PATCH are in `CONTRIBUTING.md`.

## Limitations

- **Discovery is not exhaustive.** Entries come from the awesome-design-systems list on GitHub and from web search, collected on one day. Systems that are not on that list and did not show up in those searches are not in the dataset. The dataset does not claim to cover all public design systems.
- **One coder.** The author coded the entries. An independent coder check of a sample is planned and has not been done, so inter-coder agreement is not measured.
- **Repository facts are corrected from git where the evidence is clear, and open items remain.** 214 of 221 repositories were read over git. The open items are in `results/open_items.md`.
- **One collection date.** Documentation and repositories change. Use `checked` and `repo_last_push` to judge how current an entry is.
- **Not all sites could be read.** 46 entries have a status that does not start with "checked". They are included but not verified. `not stated` means the source does not say; it does not mean that nothing exists.
- **Inclusion** is limited to design systems, component libraries and style guidelines with public documentation or a repository. Entries with a last commit before 2024 are kept.
- **Mixed language.** Some notes and licence texts are in the source language.

## Licence

- **Code** (`scripts/`, `tests/`) and documentation (this README and the other Markdown files): MIT License, see `LICENSE`.
- **Dataset content** (`data/`, `results/`, `evidence/`, and the data array in `source/index.html`): CC BY 4.0, see `LICENSE-DATA`.

The records describe third-party projects. Their licence fields describe the licences of those projects, not the licence of this dataset.

## Citation

Aleksić, S. B. (2026). *Design System Documentation Dataset* (v1.0.0) [Data set]. DOI: to be added.

Repository: https://github.com/stefanbaleksic/design-systems-documentation-dataset. The same metadata is in `CITATION.cff`, which GitHub and Zenodo read. The DOI is added to `CITATION.cff` and to this section after deposit.
