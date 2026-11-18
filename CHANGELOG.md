# Changelog

All notable changes to this dataset and its scripts are recorded here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/). Versions follow
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html); the rules are in `CONTRIBUTING.md`.

## [Unreleased]

## [1.0.0] - 2026-11-18

First public release. Not yet deposited; the DOI will be added in a later commit.

### Added

- `source/index.html`, the published page, with `source/SHA256SUMS` and `source/SOURCE.json` (artifact version `1794905101-55af`).
- `scripts/build_dataset.py`: extracts the records from the page and writes the CSV files.
- `scripts/measure.py`: descriptive tables in `results/`.
- `scripts/common.py`: UTC conversion, SemVer parsing and comparison, licence classification.
- `scripts/release.py`: writes and checks `release.json`.
- `scripts/collect.py`: collects evidence (GitHub API and documentation pages) into `evidence/`. Records every attempt, including failures.
- `scripts/run_compare_from_evidence.py`: offline comparison of the dataset with the evidence; lists every missing, unavailable and mismatching item and supports `--strict`.
- `evidence/`: 297 evidence files (one per record), collected 2026-11-18 between 09:11 and 09:50 UTC. Documentation pages: 180 of 210 fetched. GitHub repositories: 214 of 221 read over git (`--repo-source git`); in an earlier attempt the GitHub API route returned HTTP 403 from the collection environment; the stored evidence records the git route only.
- `collect.py --repo-source git`: repository facts over git (`ls-remote` for tags and the default branch, a shallow blobless clone for the last commit date and the `LICENSE` file). `--skip-docs` and `--skip-repo` re-collect one part and keep the other.
- `scripts/common.py`: `latest_stable_tag` (SemVer precedence, stable tags first) and `detect_licence_text` (MIT, Apache-2.0, BSD, ISC, MPL-2.0, GPL, CC0 from licence text).
- `scripts/corrections.py` and `data/corrections.csv`: 280 evidence-based corrections (repository last-push dates: 82 filled, 25 corrected; licence: 69 filled, 3 corrected; version: 90 filled, 11 corrected). Each correction keeps the old value in the record's note. The file is append-only. Open items are in `results/open_items.md`.
- `VERSION`, `release.json` and `scripts/release.py`: release identity, manifest with data checksums, and a consistency check.
- `source/SOURCE.json`: page version used (artifact version `1794905101-55af`).
- `scripts/collect_package.py` and `evidence/package/`: the version of each package, read from its `package.json` files over git (214 of 221 repositories; 7 without git access).
- 90 tests in `tests/` for all scripts, including UTC conversion, SemVer, URL quality, the git route, package versions and corrections.
- `README.md`, `CONTRIBUTING.md` (contribution and changelog rules, SemVer rules), `SECURITY.md` (reporting and script guarantees), `LICENSE` (MIT for code and documentation), `LICENSE-DATA` (CC BY 4.0 for dataset content).

### Known issues

- ID 28 keeps `docs_url` = `http://style.buildit.digital/`. The collector refuses `http://` by design, so the https address was not tried and this record has no documentation evidence.
- Open items (not corrected, 83): licence for IDs 150 and 275, which the author decides; version for 81 records, where the repository has placeholder versions (0.0.x), several packages and no root version, or a package name that the repository does not have. The archived flag is not in the evidence.
- ID 28 (`http://style.buildit.digital/`): http is refused by the collector, and a manual recheck on 18 November 2026 gave HTTP 403 over http and a connection reset over https.
- Seven repositories (IDs 11, 14, 25, 38, 51, 79, 126) could not be read over git. GitHub asked for credentials, so the repository is private, renamed or removed; git cannot tell these apart.
- Four records have `repo_url` = `not stated`, the dataset's placeholder for "the source does not say".

### Changed

- The meaning of `version` is the version of the package (author's decision, 18 November 2026). Earlier git-tag comparisons were replaced by a comparison with the package.json files.
- Normalised `repo_archived` values `ne` to `no` and `da` to `yes` in the cleaned file. The raw file keeps the original values.

### Removed

- 5 duplicate records (IDs 94, 114, 132, 140, 207). Each refers to the same repository or product as a kept record. Rows, kept IDs and reasons are in `data/removed_duplicates.csv`.

### Fixed

- Documentation URLs for IDs 16, 96, 98 and 157 changed from `http://` to `https://` where the https address answered HTTP 200 (ID 96 and 157 redirect to `www.`). ID 63: the redirect note moved from `docs_url` into `note`. IDs 57 and 107: text in `repo_url` moved into `note`, and `repo_url` is empty. Old values are kept in `note`. See README "Corrections and known data issues".
- CMS design system: record 150 keeps `sample=yes` and the documentation links; its empty repository fields are filled from record 207.
