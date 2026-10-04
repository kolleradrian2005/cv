import unittest

import pymupdf

from scripts.check_cv import ROOT, check_layout, check_spatial_text, check_text


class CVChecksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf = (ROOT / "cv.pdf").read_bytes()
        with pymupdf.open(stream=cls.pdf, filetype="pdf") as document:
            cls.text = document[0].get_text()

    def test_current_text(self):
        self.assertEqual(check_text(self.text), [])

    def test_letterspaced_name_is_rejected(self):
        text = self.text.replace("Adri\u00e1n Koller", "A D R I A N K O L L E R")
        self.assertTrue(any("full name" in error for error in check_text(text)))

    def test_contact_details_cannot_move_to_another_section(self):
        text = self.text.replace("akoller@tcd.ie", "") + "\nakoller@tcd.ie"
        self.assertTrue(any("CONTACT:" in error for error in check_text(text)))

    def test_missing_employer_is_rejected(self):
        text = self.text.replace("One Identity Hungary", "")
        self.assertTrue(any("WORK EXPERIENCE:" in error for error in check_text(text)))

    def test_icon_noise_in_headings_is_rejected(self):
        text = self.text.replace("CONTACT", "\u01fc CONTACT", 1)
        self.assertTrue(any("clean CONTACT heading" in error for error in check_text(text)))

    def test_changed_graduation_date_is_rejected(self):
        text = self.text.replace("Sep 2026 \u2013 Sep 2027", "Sep 2026 \u2013 Sep 2028")
        self.assertTrue(any("EDUCATION:" in error for error in check_text(text)))

    def test_reordered_sections_are_rejected(self):
        text = self.text.replace("TECHNICAL SKILLS", "TEMPORARY HEADING", 1)
        text = text.replace("TOOLS & PLATFORMS", "TECHNICAL SKILLS", 1)
        text = text.replace("TEMPORARY HEADING", "TOOLS & PLATFORMS", 1)
        self.assertIn("Section reading order has changed", check_text(text))

    def test_missing_visible_url_is_rejected(self):
        text = self.text.replace("github.com/kolleradrian2005", "kolleradrian2005")
        self.assertTrue(any("visible URL" in error for error in check_text(text)))

    def test_spatial_reordering_is_distinguished_from_text_loss(self):
        text = "\n".join(reversed(self.text.splitlines()))
        self.assertEqual(check_spatial_text(self.text, text), [])
        self.assertTrue(check_text(text))

    def test_spatial_text_loss_is_rejected(self):
        text = self.text.replace("One Identity Hungary", "")
        self.assertTrue(check_spatial_text(self.text, text))

    def test_tiny_hidden_text_is_rejected(self):
        with pymupdf.open(stream=self.pdf, filetype="pdf") as document:
            document[0].insert_text((10, 10), "hidden name", fontsize=1)
            self.assertTrue(any("below 6pt" in error for error in check_layout(document)))

    def test_extra_page_is_rejected(self):
        with pymupdf.open(stream=self.pdf, filetype="pdf") as document:
            document.new_page()
            self.assertTrue(any("Expected one page" in error for error in check_layout(document)))

    def test_off_page_text_is_rejected(self):
        with pymupdf.open(stream=self.pdf, filetype="pdf") as document:
            document[0].insert_text((610, 100), "off-page content", fontsize=10)
            self.assertTrue(any("outside the page" in error for error in check_layout(document)))


if __name__ == "__main__":
    unittest.main()
