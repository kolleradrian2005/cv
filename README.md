# CV — Adrián Koller

A single-page creative CV built in LaTeX/TikZ, with text-extraction safeguards.
Designed for software engineering applications in Ireland (mobile, full-stack,
low-level systems). The two-column layout is retained deliberately; compatibility
with every applicant tracking system is not guaranteed.

The latest compiled output is committed as [`cv.pdf`](cv.pdf).

## Design notes

- **One page, A4**, midnight-blue accent palette.
- **Sidebar layout** with full-width dark header, kerned-caps name lockup, and a
  tracked-caps tagline.
- **Beaded timeline rails** connect entries in Experience, Selected Projects, and
  Education.
- **Soft pill chips** for Tools & Platforms; filled pills for Languages;
  the existing skill dots are retained for visual continuity, not as an ATS score.
- **Visible, readable identity** — the normal-spaced name is printed in Contact,
  and the header specialisms appear in Profile. There is no invisible name or
  keyword layer. Contact URLs are both visible and clickable.
- **Decorative text** — `accsupp` maps the repeated, letter-spaced header lettering
  and icons to a space via PDF `/ActualText`. A space also works with older readers
  that ignore an empty replacement. All meaningful information remains visible as
  ordinary text elsewhere; extraction does not depend on decoding the header.
- **Document metadata** includes the title, author, subject and `en-IE` language.
  Metadata is descriptive, not a substitute for readable page content.
- `\frenchspacing` and disabled word hyphenation keep text spacing and extracted
  words predictable.

## Requirements

- [Tectonic](https://tectonic-typesetting.github.io/) 0.15.0 (the CI version) is
  recommended. It resolves and downloads LaTeX packages, including `accsupp`,
  automatically on first run. XeLaTeX and LuaLaTeX are alternatives.

For extraction checks and optional PNG previews:

- Python 3 with a current [`PyMuPDF`](https://pymupdf.readthedocs.io/)
  (`python -m pip install pymupdf`), including `TEXT_IGNORE_ACTUALTEXT`.
- `pdftotext` from Poppler or Xpdf, available on `PATH`. CI installs Poppler's
  `poppler-utils`; MiKTeX's Xpdf tool can also be used locally.

## Usage

### Build the PDF (Tectonic)

```bash
tectonic -X compile cv.tex
```

This produces `cv.pdf` in the project root.

### Build the PDF (XeLaTeX / LuaLaTeX)

```bash
xelatex cv.tex
# or
lualatex cv.tex
```

You may need to run twice so cross-references settle.

### Render a PNG preview (optional)

```bash
python -c "import fitz; fitz.open('cv.pdf')[0].get_pixmap(dpi=220).save('preview.png')"
```

### Check PDF text and layout

```powershell
python .\scripts\check_cv.py .\cv.pdf
python -m unittest discover -s tests -v
```

On Linux/macOS, use `python scripts/check_cv.py cv.pdf`.

The checker uses **both PyMuPDF and pdftotext**. It requires clean section headings,
their expected reading order, and the correct contact details, skills, employer,
role progression, project dates, education and availability in the relevant
sections. It also checks visible contact URLs, clickable links, one portrait A4
page, the 2.5 MB size budget, and underlying text size and page bounds. A 1pt hidden
name no longer satisfies the checks. Tests exercise missing, misplaced, noisy,
letter-spaced and off-page content, as well as pagination regressions.

These are local regression checks, **not an ATS certification or ranking**.
Different systems may still interleave the columns or ignore `/ActualText`.
Review the employer's auto-filled profile before submitting an application.
The PDF is not claimed to be a fully tagged or PDF/UA-conformant document.

## Project layout

```
cv.tex          # LaTeX source (palette, macros, content)
cv.pdf          # Latest compiled output (committed for convenience)
scripts/check_cv.py
tests/test_check_cv.py
README.md       # This file
.gitignore
```

## Editing tips

- **Palette** is defined near the top of `cv.tex` (`ink`, `deepink`, `body`,
  `mute`, `sidebg`).
- **Macros** for sidebar items, language pills, chips, timeline markers, and
  section headers live just below the palette — modify there to retheme.
- The chip block uses explicit `\\` line breaks to enforce a 3-3-3 layout.
  Reorder `\chip{...}` calls to rebalance row widths if you change the entries.
- Keep icons inside `\decorativeicon{...}` and preserve the normal-spaced Contact
  name when changing the decorative header.
- Keep employer, current role and previous role on separate lines. The displayed
  One Identity dates cover total employment; do not invent a promotion date.
- When intentionally changing facts, dates or section names, update `EXPECTED`,
  `CONTACT_URLS` and `LINK_TARGETS` in `scripts/check_cv.py` as applicable.
- Rebuild `cv.pdf`, run the checks, and review a PNG at normal reading size before
  committing. Text extraction alone does not establish visual quality.

## Continuous build & deploy

Every push to `main` and every PR triggers
[`.github/workflows/build.yml`](.github/workflows/build.yml), which:

1. Installs Tectonic and compiles `cv.tex`.
2. Runs the extraction-checker tests and checks the PDF with PyMuPDF and Poppler.
3. Uploads the resulting `cv.pdf` as a workflow artifact (`cv-pdf`).
4. On pushes to `main`, deploys the PDF to **GitHub Pages**, available at
   `https://<your-user>.github.io/<repo>/cv.pdf` (with a redirect from the
   site root).

To enable Pages: repository **Settings → Pages → Build and deployment → Source:
GitHub Actions**. After the first successful run on `main` the URL will appear
in the *Actions* run summary.

## License

Personal CV — all content © Adrián Koller. The LaTeX scaffolding (macros,
layout) is provided as-is for personal reference; please don’t reuse the
content verbatim.
