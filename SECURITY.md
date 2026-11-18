# Security policy

## Supported versions

Only the latest release listed in `CHANGELOG.md` receives fixes.

| Version | Supported |
|---|---|
| 1.0.x | yes |

## Reporting a vulnerability

Do not open a public issue for a security problem.

Report privately with GitHub's private vulnerability reporting (the "Security" tab, "Report a vulnerability"). The maintainer replies as soon as practical. An accepted fix is published with a `CHANGELOG.md` entry under **Security**, with credit to the reporter if they want it.

## What counts as a security issue here

- Code in `scripts/` that executes, evaluates or writes fetched content as code or to paths outside the repository.
- Any credential, token or private data committed to the repository or written to `evidence/`.
- A script that sends data to a host other than the ones named in the README.

A wrong fact in a record is a data error, not a security issue. Report it as described in `CONTRIBUTING.md`.

## Rules the scripts follow

- `collect.py` makes requests only over HTTPS. Plain HTTP is refused and recorded.
- The git route runs `git` with `GIT_TERMINAL_PROMPT=0`, so git never waits for a password. It clones only `https://github.com/` repositories, with `--filter=blob:none --no-checkout --depth 1`. Nothing is checked out and no file from the repository is executed. Clones are deleted after reading.
- `GITHUB_TOKEN`, if set, is read from the environment, sent only as an `Authorization` header to `api.github.com`, and never written to a file, log or report. The test `test_token_is_sent_as_header_and_never_stored` checks this.
- Fetched pages are not executed. Only a SHA-256 of the first 2 MiB of the body is stored.
- The collector does not try to get around access controls. A site that refuses a request is recorded as refused, and the request is not repeated with changed headers.
- Evidence files contain URLs, status codes, timestamps and hashes. Do not add response bodies, cookies or headers to them.
- The scripts use the standard library only, so there is no third-party dependency to audit.

## Known limits

- Evidence files record what a server returned at one time. They are not proof that the content is authentic.
- Dependencies of the page itself (for example Google Fonts loaded by `source/index.html`) are not vendored. Loading them sends the visitor's address to the font provider. The page is for reading the data, not for production use.
