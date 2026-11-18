"""Tests for UTC conversion and SemVer handling (scripts/common.py). Standard library only."""
import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import common  # noqa: E402
from common import (  # noqa: E402
    compare_semver, format_utc, is_valid_semver, loose_version, parse_checked_date,
    parse_iso_to_utc, parse_last_push, parse_semver, to_utc,
)

UTC = dt.timezone.utc
BELGRADE = dt.timezone(dt.timedelta(hours=1))  # CET; the dataset's local zone in winter


class UtcTests(unittest.TestCase):
    def test_offset_is_converted_to_utc(self):
        value = dt.datetime(2026, 11, 18, 10, 0, tzinfo=BELGRADE)
        self.assertEqual(to_utc(value), dt.datetime(2026, 11, 18, 9, 0, tzinfo=UTC))

    def test_conversion_can_cross_midnight(self):
        value = dt.datetime(2026, 11, 18, 0, 30, tzinfo=BELGRADE)
        self.assertEqual(format_utc(value), "2026-11-17T23:30:00Z")

    def test_naive_datetime_is_rejected(self):
        with self.assertRaises(ValueError):
            to_utc(dt.datetime(2026, 11, 18, 10, 0))

    def test_parse_iso_with_offset(self):
        self.assertEqual(format_utc(parse_iso_to_utc("2026-11-16T10:00:00+01:00")), "2026-11-16T09:00:00Z")

    def test_parse_iso_with_z(self):
        self.assertEqual(format_utc(parse_iso_to_utc("2026-11-16T10:00:00Z")), "2026-11-16T10:00:00Z")

    def test_parse_iso_rejects_missing_offset_as_naive(self):
        with self.assertRaises(ValueError):
            parse_iso_to_utc("2026-11-16T10:00:00")

    def test_parse_iso_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_iso_to_utc("16.11.2026")
        with self.assertRaises(ValueError):
            parse_iso_to_utc("")

    def test_checked_date_is_dd_mm_yyyy(self):
        self.assertEqual(parse_checked_date("17.11.2026"), dt.date(2026, 11, 17))
        with self.assertRaises(ValueError):
            parse_checked_date("2026-11-17")
        with self.assertRaises(ValueError):
            parse_checked_date("31.02.2026")

    def test_last_push_takes_the_commit_date_as_utc_date(self):
        self.assertEqual(parse_last_push("2026-11-16 (last commit date)"), dt.date(2026, 11, 16))
        self.assertEqual(parse_last_push("2026-11-17"), dt.date(2026, 11, 17))
        self.assertIsNone(parse_last_push(""))
        with self.assertRaises(ValueError):
            parse_last_push("16.11.2026")


class SemverTests(unittest.TestCase):
    def test_valid_versions(self):
        for text in ["0.0.0", "1.2.3", "10.20.30", "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0+build.5", "1.0.0-rc.1+sha.9"]:
            self.assertTrue(is_valid_semver(text), text)

    def test_invalid_versions(self):
        for text in ["1.2", "v1.2.3", "01.2.3", "1.02.3", "1.2.3.4", "1.0.0-", "not stated", "", "4.10"]:
            self.assertFalse(is_valid_semver(text), text)

    def test_precedence_follows_the_spec(self):
        ordered = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta",
                   "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0", "2.0.0", "2.1.0", "2.1.1"]
        for lower, higher in zip(ordered, ordered[1:]):
            self.assertEqual(compare_semver(lower, higher), -1, (lower, higher))
            self.assertEqual(compare_semver(higher, lower), 1, (higher, lower))

    def test_numeric_parts_compare_as_numbers(self):
        self.assertEqual(compare_semver("4.10.0", "4.9.0"), 1)

    def test_build_metadata_is_ignored_for_precedence(self):
        self.assertEqual(compare_semver("1.0.0+a", "1.0.0+b"), 0)

    def test_equal_versions(self):
        self.assertEqual(compare_semver("18.2.0", "18.2.0"), 0)

    def test_parse_rejects_invalid(self):
        with self.assertRaises(ValueError):
            parse_semver("v4.10.1")

    def test_loose_version_extracts_from_free_text(self):
        cases = {
            "v4.10.1 (latest tag seen)": ("4.10.1", "full"),
            "@cmsgov/ds-medicare-gov@18.2.0 (latest tag seen)": ("18.2.0", "full"),
            "6.7.1": ("6.7.1", "full"),
            "@artsy/palette@46.11.0 (latest tag seen)": ("46.11.0", "full"),
            "v3.0 (mentioned on site)": ("3.0.0", "minor"),
            "3.0 (mentioned on site)": ("3.0.0", "minor"),
        }
        for text, (expected, precision) in cases.items():
            found = loose_version(text)
            self.assertIsNotNone(found, text)
            version, got_precision = found
            self.assertEqual(version.render(), expected, text)
            self.assertEqual(got_precision, precision, text)

    def test_loose_version_returns_none_when_no_version(self):
        for text in ["not stated", "NOVA", "", None, "not stated (Docusaurus site)"]:
            self.assertIsNone(loose_version(text), text)

    def test_date_is_not_a_version(self):
        self.assertIsNone(loose_version("16.11.2026"))
        self.assertIsNone(loose_version("dataset 17.11.2026 note"))

    def test_two_part_version_is_never_presented_as_full(self):
        _, precision = loose_version("3.0 (mentioned on site)")
        self.assertEqual(precision, "minor")


class LicenceTests(unittest.TestCase):
    def test_classes(self):
        self.assertEqual(common.licence_class("MIT (LICENSE)"), "permissive")
        self.assertEqual(common.licence_class("Apache-2.0"), "permissive")
        self.assertEqual(common.licence_class("MPL-2.0 (LICENSE)"), "copyleft")
        self.assertEqual(common.licence_class("not identified"), "none or not identified")
        self.assertEqual(common.licence_class(""), "no repository licence read")


if __name__ == "__main__":
    unittest.main()
