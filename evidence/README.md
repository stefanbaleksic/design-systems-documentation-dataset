# Evidence

One JSON file per record (`<id>.json`), written by `scripts/collect.py` and read by `scripts/run_compare_from_evidence.py`.

## What is in a file

- `schema`: `evidence/1`.
- `id`, `name`: the record.
- `collected_at_utc`: when the collection of this record started, in UTC.
- `repo`: repository facts for `repo_url`: `pushed_at_utc`, `archived`, `spdx_licence`, `latest_tag`, `default_branch`, `tag_count`, and for the git route `licence_file` and `licence_detection`. `api.method` is `git` for the git route; for the API route the request record of each call (`url`, `http_status`, `error`, `fetched_at_utc`) is kept.
- The git route cannot read `archived`; it is `null`.
- `docs`: the request record for `docs_url`, with `final_url`, `http_status`, `content_type` and `body_sha256` of the first 2 MiB of the body.
- `status`: `ok` (all sources answered), `partial` (some answered), `failed` (none answered), `no_sources`.
- `notes`: why a source was not collected.

A request that failed keeps its record with an `error` field. Nothing is removed on failure.

## What is not in a file

No response bodies, cookies, headers or tokens. The collector does not write `GITHUB_TOKEN`. The git route never puts a token in a URL.

## Re-running

`python3 scripts/collect.py` overwrites the files. Keep the old version under version control so the change is visible. `python3 scripts/run_compare_from_evidence.py` reads the files without network access.
