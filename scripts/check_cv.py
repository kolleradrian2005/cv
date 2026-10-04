"""Check PDF mechanics without pinning the CV's wording or personal details."""

import argparse
from pathlib import Path
import sys

import pymupdf


def check_pdf(document: pymupdf.Document) -> list[str]:
    errors = []
    if len(document) != 1:
        errors.append(f"Expected one page, found {len(document)}")
    for page in document:
        if abs(page.rect.width - 595.28) > 1 or abs(page.rect.height - 841.89) > 1:
            errors.append(f"Page {page.number + 1} is not portrait A4")
        if not page.get_text().strip():
            errors.append(f"Page {page.number + 1} has no extractable text")

        # Include underlying and off-page glyphs, even if ActualText hides them.
        flags = pymupdf.TEXTFLAGS_DICT | pymupdf.TEXT_IGNORE_ACTUALTEXT
        blocks = page.get_text("dict", flags=flags, clip=pymupdf.INFINITE_RECT())["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if not span["text"].strip():
                        continue
                    if span["size"] < 6:
                        errors.append(f"Text below 6pt: {span['text']!r}")
                    if not page.rect.contains(pymupdf.Rect(span["bbox"])):
                        errors.append(f"Text outside the page: {span['text']!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdf", nargs="?", type=Path,
        default=Path(__file__).resolve().parents[1] / "cv.pdf",
    )
    args = parser.parse_args()
    if not args.pdf.is_file():
        parser.error(f"PDF does not exist: {args.pdf}")

    errors = []
    if args.pdf.stat().st_size > 2_500_000:
        errors.append("PDF exceeds the 2.5 MB size budget")
    with pymupdf.open(args.pdf) as document:
        errors.extend(check_pdf(document))
    if errors:
        print("PDF checks failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("PDF checks passed: one A4 page, extractable text, text size and page bounds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
