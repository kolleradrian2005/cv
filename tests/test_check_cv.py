import unittest

import pymupdf

from scripts.check_cv import check_pdf


class PDFChecksTest(unittest.TestCase):
    def setUp(self):
        self.document = pymupdf.open()
        self.addCleanup(self.document.close)
        self.page = self.document.new_page()

    def test_arbitrary_content_is_allowed(self):
        self.page.insert_text((40, 40), "Any name, employer, skills, or graduation date.")
        self.assertEqual(check_pdf(self.document), [])
        self.page.insert_text((40, 70), "New content requires no changes to these checks.")
        self.assertEqual(check_pdf(self.document), [])

    def test_blank_page_is_rejected(self):
        self.assertTrue(any("no extractable text" in error for error in check_pdf(self.document)))

    def test_tiny_text_is_rejected(self):
        self.page.insert_text((40, 40), "tiny text", fontsize=1)
        self.assertTrue(any("below 6pt" in error for error in check_pdf(self.document)))

    def test_off_page_text_is_rejected(self):
        self.page.insert_text((610, 100), "off-page content", fontsize=10)
        self.assertTrue(any("outside the page" in error for error in check_pdf(self.document)))

    def test_extra_page_is_rejected(self):
        self.document.new_page()
        self.assertTrue(any("Expected one page" in error for error in check_pdf(self.document)))

    def test_wrong_paper_size_is_rejected(self):
        with pymupdf.open() as document:
            document.new_page(width=400, height=400)
            self.assertTrue(any("not portrait A4" in error for error in check_pdf(document)))


if __name__ == "__main__":
    unittest.main()
