"""Check this CV's extracted content and geometry, not an ATS ranking."""

import argparse
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

import fitz


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "CONTACT": (
        "Adri\u00e1n Koller", "Dublin, Ireland", "akoller@tcd.ie",
        "+36 30 907 3040",
    ),
    "ELIGIBILITY": ("EU citizen", "no sponsorship required"),
    "TECHNICAL SKILLS": (
        "Flutter / Dart", "NestJS / Node.js", "Rust", "C# / .NET",
        "Python", "TypeScript / JavaScript",
    ),
    "TOOLS & PLATFORMS": (
        "MCP servers", "Unity", "AWS", "GitLab CI", "Docker", "Java",
        "CircleCI", "OpenGL", "Git",
    ),
    "LANGUAGES": ("Hungarian", "Native", "English", "Proficient", "C1", "German", "B2"),
    "INTERESTS": ("Low-level & graphics code", "Game development", "Volleyball"),
    "AVAILABILITY": ("full-time roles from September 2027", "Trinity College Dublin"),
    "PROFILE": (
        "MSc Computer Science", "Trinity College Dublin", "September 2027",
        "mobile, full-stack, and low-level systems", "C#/.NET",
        "automated testing", "Flutter/NestJS", "Rust",
    ),
    "WORK EXPERIENCE": (
        "May 2025 - Present One Identity Hungary",
        "Budapest, Hungary", "Software Developer Previously: Software Tester",
        "Active Directory", "Microsoft Entra ID", "automated test suites",
        "quality assurance (QA)", "single sign-on (SSO/RSTS)",
        "GitHub Copilot", "Model Context Protocol (MCP)",
    ),
    "SELECTED PROJECTS": (
        "Aug 2023 - Present Lumina Thesis", "entity-component system (ECS)",
        "multithreaded logic/render split", "OpenGL / GLSL 450",
        "Jul 2025 - Present KeepYourHabits", "Amazon Web Services (AWS)",
        "continuous integration and delivery (CI/CD)",
        "Apr 2024 - Nov 2024 Touch", "NFC scanning", "PKPass creation",
        "Apple ID authentication", "Feb 2025 - May 2025 Wild Trails",
        "procedural terrain", "GitLab CI",
    ),
    "EDUCATION": (
        "Sep 2026 - Sep 2027 (expected) MSc Computer Science",
        "Trinity College Dublin, Ireland",
        "Jul 2023 - Jun 2026 BSc Computer Science",
        "E\u00f6tv\u00f6s Lor\u00e1nd University (ELTE)",
        "Sep 2025 - Jan 2026 Erasmus+ Exchange",
        "Universitat Polit\u00e8cnica de Val\u00e8ncia (ETSINF)",
        "Network Information Security Technologies, Computer Architecture",
    ),
}
CONTACT_URLS = (
    "linkedin.com/in/adri\u00e1n-koller-aba007319",
    "github.com/kolleradrian2005",
)
LINK_TARGETS = {
    "mailto:akoller@tcd.ie",
    "https://www.linkedin.com/in/adri\u00e1n-koller-aba007319/",
    "https://github.com/kolleradrian2005",
    "https://github.com/kolleradrian2005/Lumina",
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.replace("\u2013", "-").replace("\u2014", "-").split())


def check_text(text: str) -> list[str]:
    lines = [normalize(line) for line in text.splitlines()]
    errors = []
    positions = []
    for heading in EXPECTED:
        matches = [i for i, line in enumerate(lines) if line == heading]
        if len(matches) != 1:
            errors.append(f"Expected one clean {heading} heading, found {len(matches)}")
        else:
            positions.append(matches[0])
    if errors:
        return errors
    if positions != sorted(positions):
        return ["Section reading order has changed"]

    sections = {}
    for (heading, fields), start, end in zip(
        EXPECTED.items(), positions, positions[1:] + [len(lines)]
    ):
        content = " ".join(lines[start + 1:end])
        sections[heading] = content
        for field in fields:
            pattern = rf"(?<!\w){re.escape(normalize(field))}(?!\w)"
            if not re.search(pattern, content):
                errors.append(f"{heading}: missing or broken field: {field}")

    compact_contact = "".join(sections["CONTACT"].split())
    for url in CONTACT_URLS:
        if url not in compact_contact:
            errors.append(f"CONTACT: missing visible URL: {url}")
    if normalize(text).count("Adri\u00e1n Koller") != 1:
        errors.append("Expected exactly one unspaced, extractable full name")
    if "\ufffd" in text or any(unicodedata.category(c) == "Co" for c in text):
        errors.append("Unmapped or private-use glyphs leaked into extracted text")
    return errors


def check_layout(document: fitz.Document) -> list[str]:
    errors = []
    if len(document) != 1:
        errors.append(f"Expected one page, found {len(document)}")
    links = set()
    for page in document:
        if abs(page.rect.width - 595.28) > 1 or abs(page.rect.height - 841.89) > 1:
            errors.append(f"Page {page.number + 1} is not portrait A4")
        # Inspect the underlying glyphs too, so ActualText cannot hide a tiny text layer.
        flags = fitz.TEXTFLAGS_DICT | fitz.TEXT_IGNORE_ACTUALTEXT
        blocks = page.get_text("dict", flags=flags, clip=fitz.INFINITE_RECT())["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if not span["text"].strip():
                        continue
                    if span["size"] < 6:
                        errors.append(f"Text below 6pt: {span['text']!r}")
                    if not page.rect.contains(fitz.Rect(span["bbox"])):
                        errors.append(f"Text outside the page: {span['text']!r}")
        links.update(link["uri"] for link in page.get_links() if "uri" in link)
    for target in sorted(LINK_TARGETS - links):
        errors.append(f"Missing clickable link: {target}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="?", type=Path, default=ROOT / "cv.pdf")
    args = parser.parse_args()
    if not args.pdf.is_file():
        parser.error(f"PDF does not exist: {args.pdf}")

    errors = []
    if args.pdf.stat().st_size > 2_500_000:
        errors.append("PDF exceeds the 2.5 MB size budget")
    with fitz.open(args.pdf) as document:
        errors.extend(check_layout(document))
        text = "\n".join(page.get_text() for page in document)
        errors.extend(f"PyMuPDF: {error}" for error in check_text(text))
    try:
        result = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(args.pdf.resolve()), "-"],
            check=True, capture_output=True, encoding="utf-8",
        )
    except FileNotFoundError:
        errors.append("pdftotext is missing; install Poppler or Xpdf and add it to PATH")
    except subprocess.CalledProcessError as error:
        errors.append(f"pdftotext failed ({error.returncode}): {error.stderr.strip()}")
    else:
        if result.stderr.strip():
            errors.append(f"pdftotext diagnostic: {result.stderr.strip()}")
        errors.extend(f"pdftotext: {error}" for error in check_text(result.stdout))
    if errors:
        print("CV checks failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("CV checks passed: one A4 page, expected fields in both extractors, links and text bounds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
