"""Shared helpers: UTC conversion, SemVer parsing and comparison, licence classification.

Standard library only. Imported by the other scripts (run from the scripts/ directory or
with scripts/ on sys.path).

Conventions
-----------
* All instants are UTC. `to_utc` converts an aware datetime to UTC; naive values are rejected.
* Dates in the dataset are calendar dates. `checked` is written dd.mm.yyyy in Belgrade local
  time (the author's time zone). `repo_last_push` is a commit date; it is kept as a UTC date
  because GitHub reports commit times in UTC.
* SemVer means semver.org 2.0.0. `loose_version` extracts a best-effort version from free text
  such as "v4.10.1 (latest tag seen)" and says how precise it was.
"""
import datetime as dt
import re

UTC = dt.timezone.utc

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)
DATE_LIKE_RE = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b")
LOOSE_RE = re.compile(r"(?:^|[@\s/])v?(\d+)\.(\d+)(?:\.(\d+))?(?:-([0-9A-Za-z.-]+))?")


class Semver:
    """Parsed SemVer 2.0.0 version. Build metadata is ignored for precedence (as the spec says)."""

    __slots__ = ("major", "minor", "patch", "prerelease", "text")

    def __init__(self, major, minor, patch, prerelease=None, text=None):
        self.major, self.minor, self.patch = int(major), int(minor), int(patch)
        self.prerelease = prerelease or None
        self.text = text or self.render()

    def render(self):
        base = "%d.%d.%d" % (self.major, self.minor, self.patch)
        return base + ("-" + self.prerelease if self.prerelease else "")

    def key(self):
        """Sort key implementing SemVer precedence."""
        if self.prerelease is None:
            pre = (1,)
        else:
            ids = []
            for part in self.prerelease.split("."):
                if part.isdigit():
                    ids.append((0, int(part), ""))
                else:
                    ids.append((1, 0, part))
            pre = (0, tuple(ids))
        return (self.major, self.minor, self.patch, pre)

    def __eq__(self, other):
        return isinstance(other, Semver) and self.key() == other.key()

    def __lt__(self, other):
        return self.key() < other.key()

    def __hash__(self):
        return hash(self.key())

    def __repr__(self):
        return "Semver(%r)" % self.text


def parse_semver(text):
    """Parse a strict SemVer 2.0.0 string. Raises ValueError if it is not valid."""
    if not isinstance(text, str):
        raise ValueError("version must be a string")
    match = SEMVER_RE.match(text.strip())
    if not match:
        raise ValueError("not a valid semantic version: %r" % text)
    major, minor, patch, pre, _build = match.groups()
    return Semver(major, minor, patch, pre, text.strip())


def is_valid_semver(text):
    try:
        parse_semver(text)
        return True
    except ValueError:
        return False


def compare_semver(a, b):
    """Return -1, 0 or 1 comparing two Semver objects or strings."""
    a = a if isinstance(a, Semver) else parse_semver(a)
    b = b if isinstance(b, Semver) else parse_semver(b)
    if a.key() < b.key():
        return -1
    if a.key() > b.key():
        return 1
    return 0


def loose_version(text):
    """Best-effort version from free text. Returns (Semver, precision) or None.

    precision is "full" (X.Y.Z), or "minor" (X.Y, patch taken as 0). A two-part version is
    never presented as a full one.
    """
    if not text:
        return None
    if DATE_LIKE_RE.search(text):
        # dd.mm.yyyy is a date, not a version number
        return None
    match = LOOSE_RE.search(text)
    if not match:
        return None
    major, minor, patch, pre = match.groups()
    if patch is None:
        return Semver(major, minor, 0, pre), "minor"
    return Semver(major, minor, patch, pre), "full"


def to_utc(value):
    """Convert an aware datetime to a UTC datetime. Naive datetimes are rejected."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("naive datetime has no time zone: %r" % (value,))
    return value.astimezone(UTC)


def parse_iso_to_utc(text):
    """Parse an ISO 8601 timestamp with an explicit offset or 'Z' and return a UTC datetime."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("empty timestamp")
    raw = text.strip()
    if raw.endswith("Z") or raw.endswith("z"):
        raw = raw[:-1] + "+00:00"
    try:
        value = dt.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError("not an ISO 8601 timestamp: %r" % text) from exc
    return to_utc(value)


def format_utc(value):
    """Format a UTC datetime as YYYY-MM-DDTHH:MM:SSZ."""
    return to_utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_checked_date(text):
    """Parse the dataset's `checked` field (dd.mm.yyyy) into a calendar date."""
    match = re.fullmatch(r"\s*(\d{2})\.(\d{2})\.(\d{4})\s*", text or "")
    if not match:
        raise ValueError("checked date must be dd.mm.yyyy: %r" % text)
    day, month, year = (int(g) for g in match.groups())
    return dt.date(year, month, day)


def parse_last_push(text):
    """Parse `repo_last_push` ('2026-11-16 (last commit date)' or '2026-11-16') to a UTC date.

    Returns None for an empty value. A commit date has no time of day in the dataset, so the
    UTC calendar date is returned.
    """
    if text is None or not text.strip():
        return None
    match = re.match(r"\s*(\d{4})-(\d{2})-(\d{2})", text)
    if not match:
        raise ValueError("repo_last_push must start with yyyy-mm-dd: %r" % text)
    year, month, day = (int(g) for g in match.groups())
    return dt.date(year, month, day)


def licence_class(value):
    """Map a repository licence string to a class. Heuristic; see README "Measures"."""
    value = (value or "").strip()
    if value == "":
        return "no repository licence read"
    if NONE_PATTERN.search(value):
        return "none or not identified"
    if PERMISSIVE_PATTERN.search(value):
        return "permissive"
    if COPYLEFT_PATTERN.search(value):
        return "copyleft"
    return "other or custom"


NONE_PATTERN = re.compile(
    r"^$|not stated|not identified|not found|no licence|no open licence|^none|copyright|"
    r"not open-sourced|^not confirmed",
    re.I,
)
PERMISSIVE_PATTERN = re.compile(r"\b(MIT|Apache|BSD|ISC|CC0)", re.I)
COPYLEFT_PATTERN = re.compile(r"\b(GPL|MPL|EUPL)|CC BY-SA", re.I)


def latest_stable_tag(tag_names):
    """Pick the latest tag by SemVer precedence, preferring stable releases.

    Tags may carry a leading 'v'. Tags that are not valid SemVer are ignored. A stable release
    (no pre-release part) wins over any pre-release. Returns (tag_name, Semver) or None.
    """
    parsed = []
    for name in tag_names:
        bare = name[1:] if name[:1] in ("v", "V") else name
        if is_valid_semver(bare):
            parsed.append((name, parse_semver(bare)))
    if not parsed:
        return None
    stable = [p for p in parsed if p[1].prerelease is None]
    pool = stable or parsed
    return max(pool, key=lambda p: p[1].key())


LICENCE_TEXT_RULES = [
    ("MIT", ["permission is hereby granted, free of charge"]),
    ("Apache-2.0", ["apache license", "version 2.0"]),
    ("BSD-3-Clause", ["redistribution and use in source and binary forms", "neither the name"]),
    ("BSD-2-Clause", ["redistribution and use in source and binary forms"]),
    ("ISC", ["permission to use, copy, modify, and/or distribute this software"]),
    ("MPL-2.0", ["mozilla public license version 2.0"]),
    ("GPL-3.0", ["gnu general public license", "version 3"]),
    ("GPL-2.0", ["gnu general public license", "version 2"]),
    ("CC0-1.0", ["creative commons legal code", "cc0"]),
]


def detect_licence_text(text):
    """Identify a licence from the text of its licence file. Returns an SPDX-like id or None.

    Text matching is a heuristic. The result is recorded as 'detected from text', not as a
    licence declared by the repository.
    """
    if not text:
        return None
    lowered = " ".join(text.lower().split())
    for spdx, needles in LICENCE_TEXT_RULES:
        if all(n in lowered for n in needles):
            return spdx
    return None
