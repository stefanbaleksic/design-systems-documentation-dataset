"""Tests for the dataset. Standard library only.

Run from the repository root:
    python3 -m unittest discover -s tests -v
"""
import csv
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SCRIPTS = os.path.join(ROOT, "scripts")
REQUIRED_COLUMNS = {
    "id", "name", "type", "sector", "status", "checked", "docs_url", "repo_url", "licence",
    "repo_licence", "version", "repo_last_push", "repo_archived", "sample", "note",
}
EXPECTED_REMOVED = {"94", "114", "132", "140", "207"}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class RawDataTests(unittest.TestCase):
    def setUp(self):
        self.raw = read_csv(os.path.join(DATA, "design_systems_raw.csv"))

    def test_raw_row_count(self):
        self.assertEqual(len(self.raw), 302)

    def test_raw_ids_unique(self):
        ids = [r["id"] for r in self.raw]
        self.assertEqual(len(ids), len(set(ids)))

    def test_required_columns_present(self):
        self.assertTrue(REQUIRED_COLUMNS.issubset(self.raw[0].keys()))

    def test_source_checksum_matches(self):
        recorded = {}
        with open(os.path.join(ROOT, "source", "SHA256SUMS"), encoding="utf-8") as fh:
            for line in fh:
                digest, name = line.split()
                recorded[name] = digest
        self.assertEqual(sha256(os.path.join(ROOT, "source", "index.html")), recorded["index.html"])


class CleanedDataTests(unittest.TestCase):
    def setUp(self):
        self.raw = read_csv(os.path.join(DATA, "design_systems_raw.csv"))
        self.clean = read_csv(os.path.join(DATA, "design_systems.csv"))
        self.removed = read_csv(os.path.join(DATA, "removed_duplicates.csv"))

    def test_removed_ids_are_the_documented_duplicates(self):
        self.assertEqual({r["removed_id"] for r in self.removed}, EXPECTED_REMOVED)

    def test_raw_minus_removed_equals_clean(self):
        self.assertEqual(len(self.clean), 297)
        self.assertEqual(len(self.clean), len(self.raw) - len(self.removed))
        clean_ids = {r["id"] for r in self.clean}
        self.assertTrue(EXPECTED_REMOVED.isdisjoint(clean_ids))

    def test_every_kept_record_is_in_clean_file(self):
        clean_ids = {r["id"] for r in self.clean}
        for row in self.removed:
            self.assertIn(row["kept_id"], clean_ids)

    def test_no_duplicate_names(self):
        names = [r["name"] for r in self.clean]
        self.assertEqual(len(names), len(set(names)), "duplicate display names remain")

    def test_no_duplicate_repository_urls(self):
        urls = [r["repo_url"] for r in self.clean if r["repo_url"] and r["repo_url"] != "not stated"]
        self.assertEqual(len(urls), len(set(urls)), "same repository listed twice")

    def test_no_duplicate_documentation_urls(self):
        urls = [r["docs_url"] for r in self.clean if r["docs_url"] and r["docs_url"] != "not stated"]
        self.assertEqual(len(urls), len(set(urls)), "same documentation site listed twice")

    def test_cms_merge_keeps_sample_flag_and_fills_repository(self):
        rec = {r["id"]: r for r in self.clean}["150"]
        raw207 = {r["id"]: r for r in self.raw}["207"]
        self.assertEqual(rec["sample"], "yes")
        for field in ["repo_url", "repo_licence", "repo_last_push"]:
            self.assertEqual(rec[field], raw207[field], field)
        self.assertEqual(rec["repo_archived"], "no")

    def test_repo_archived_normalised(self):
        values = {r["repo_archived"] for r in self.clean}
        self.assertNotIn("ne", values)
        self.assertNotIn("da", values)

    def test_sample_values(self):
        self.assertTrue({r["sample"] for r in self.clean} <= {"yes", "no"})

    def test_removed_rows_have_reason(self):
        for row in self.removed:
            self.assertTrue(row["reason"].strip())


# Documented exceptions to the https-only rule for documentation URLs (see README "Known data issues").
KNOWN_HTTP_DOCS = {"28"}
CORRECTED_DOCS = {"16": "https://overdrive.autoguru.io/", "96": "https://www.mongodb.design/",
                  "98": "https://designsystem.morningstar.com/", "157": "https://www.welcome-ui.com/",
                  "63": "https://m3.material.io/"}


class UrlQualityTests(unittest.TestCase):
    def setUp(self):
        self.clean = read_csv(os.path.join(DATA, "design_systems.csv"))

    def test_documentation_urls_are_https_except_documented_exceptions(self):
        for r in self.clean:
            url = r["docs_url"]
            if url in ("", "not stated"):
                continue
            if r["id"] in KNOWN_HTTP_DOCS:
                self.assertTrue(url.startswith("http://"), r["id"])
                self.assertIn("18.11.2026", r["note"], "exception must be explained in note")
            else:
                self.assertTrue(url.startswith("https://"), (r["id"], url))

    def test_documentation_urls_are_clean_urls(self):
        for r in self.clean:
            url = r["docs_url"]
            if url in ("", "not stated"):
                continue
            self.assertRegex(url, r"^https?://\S+$", (r["id"], url))

    def test_corrected_documentation_urls(self):
        by_id = {r["id"]: r for r in self.clean}
        for rec_id, url in CORRECTED_DOCS.items():
            self.assertEqual(by_id[rec_id]["docs_url"], url, rec_id)

    def test_repository_urls_are_urls_or_placeholder(self):
        for r in self.clean:
            url = r["repo_url"]
            self.assertTrue(url in ("", "not stated") or url.startswith("https://"), (r["id"], url))

    def test_text_moved_out_of_url_fields_is_kept_in_note(self):
        by_id = {r["id"]: r for r in self.clean}
        self.assertIn("(not public)", by_id["57"]["note"])
        self.assertIn("(release notes only)", by_id["107"]["note"])
        self.assertIn("redirected from material.io", by_id["63"]["note"])


class ReproducibilityTests(unittest.TestCase):
    def test_rebuild_is_byte_identical(self):
        tmp = tempfile.mkdtemp()
        try:
            subprocess.run(
                [sys.executable, "-I", os.path.join(SCRIPTS, "build_dataset.py"),
                 "--source", os.path.join(ROOT, "source", "index.html"), "--out", tmp],
                check=True, stdout=subprocess.DEVNULL,
            )
            for name in ["design_systems.csv", "design_systems_raw.csv", "removed_duplicates.csv"]:
                self.assertEqual(sha256(os.path.join(tmp, name)), sha256(os.path.join(DATA, name)), name)
        finally:
            shutil.rmtree(tmp)


class MeasureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.measure = load_module("measure", os.path.join(SCRIPTS, "measure.py"))

    def test_licence_classes(self):
        f = self.measure.licence_class
        self.assertEqual(f("MIT (LICENSE)"), "permissive")
        self.assertEqual(f("Apache-2.0 (LICENSE.md)"), "permissive")
        self.assertEqual(f("GPL-2.0-or-later (project LICENSE.md)"), "copyleft")
        self.assertEqual(f("PrimeNG community licence (LICENSE.md; custom terms)"), "other or custom")
        self.assertEqual(f("not stated: no licence file at repository root"), "none or not identified")
        self.assertEqual(f(""), "no repository licence read")

    def test_verification_classes(self):
        f = self.measure.verification
        self.assertEqual(f("checked 17.11.2026"), "checked")
        self.assertEqual(f("not accessible: HTTP 403"), "not checked or unavailable")

    def test_groupings_add_up(self):
        rows = read_csv(os.path.join(DATA, "design_systems.csv"))
        counts = self.measure.tally(rows, lambda r: r["type"])
        self.assertEqual(sum(counts.values()), len(rows))


if __name__ == "__main__":
    unittest.main()
