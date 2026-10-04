# CV — Adrián Koller

A single-page creative CV built in LaTeX/TikZ, with lightweight PDF sanity checks.
Designed for software engineering applications in Ireland (mobile, full-stack,
low-level systems). The two-column layout is retained deliberately; compatibility
with every applicant tracking system is not guaranteed.

The latest compiled output is committed as [`cv.pdf`](cv.pdf).

## Design notes

- **One page, A4**, midnight-blue accent palette.
- **Sidebar layout** with a full-width dark header and tracked-caps name and
  tagline. `soul` controls letter-spacing; the source uses normal words rather
  than spaces between individual letters.
- **Beaded timeline rails** connect entries in Experience, Selected Projects, and
  Education.
- **Soft pill chips** for Tools & Platforms; filled pills for Languages;
  the existing skill dots are retained for visual continuity, not as an ATS score.
- **Visible, readable identity** — the normal-spaced name is printed in Contact,
  and the header specialisms appear in Profile. There is no invisible name or
  keyword layer. The GitHub URL is printed in full; a single-line "LinkedIn
  profile" label keeps the original, complete LinkedIn destination clickable.
  The full LinkedIn URL is not included in plain-text-only extraction.
- **Decorative text** — `accsupp` maps the repeated, letter-spaced header lettering
  and icons to a space via PDF `/ActualText`. A space also works with older readers
  that ignore an empty replacement. The header information remains visible as
  ordinary text elsewhere; extraction does not depend on decoding the header.
- **Document metadata** includes the title, author, subject and `en-IE` language.
  Metadata is descriptive, not a substitute for readable page content.
- `\frenchspacing` and disabled word hyphenation keep text spacing and extracted
  words predictable.

## Requirements

- [Tectonic](https://tectonic-typesetting.github.io/) 0.15.0 (the CI version) is
  recommended. It resolves and downloads LaTeX packages, including `accsupp` and `soul`,
  automatically on first run. XeLaTeX and LuaLaTeX are alternatives.

For PDF checks and optional PNG previews:

- Python 3 with a current [`PyMuPDF`](https://pymupdf.readthedocs.io/)
  (`python -m pip install pymupdf`), including `TEXT_IGNORE_ACTUALTEXT`.

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
python -c "import pymupdf; pymupdf.open('cv.pdf')[0].get_pixmap(dpi=220).save('preview.png')"
```

### Check PDF mechanics

```powershell
python .\scripts\check_cv.py .\cv.pdf
python -m unittest discover -s tests -v
```

On Linux/macOS, use `python scripts/check_cv.py cv.pdf`.

The small PyMuPDF checker enforces the design's mechanical constraints: one
portrait A4 page, a 2.5 MB size budget, extractable text, no text smaller than 6pt,
and no off-page text. It does **not** hardcode names, employers, skills, dates,
section headings or link destinations. Its tests create small synthetic PDFs;
they do not use the real CV as a fixture.

For normal content edits, change `cv.tex` and rebuild `cv.pdf`. There are no
biographical assertions or expected-text lists to update elsewhere.

These are local regression checks, **not an ATS certification or ranking**.
Different systems may still interleave the columns or ignore `/ActualText`.
For example, Poppler's default layout heuristic was observed interleaving the
columns. The sanity checks do not certify reading order or field associations.
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
- **Tracking** is set once for each header style in `\nametracking` and
  `\taglinetracking`. Edit their word arguments normally; do not insert spaces
  between letters.
- The chip block uses explicit `\\` line breaks to enforce a 3-3-3 layout.
  Reorder `\chip{...}` calls to rebalance row widths if you change the entries.
- Keep icons inside `\decorativeicon{...}` and preserve the normal-spaced Contact
  name when changing the decorative header.
- Keep the current role as the primary experience heading. Employer and employment
  dates share a muted line; location and the starting role form a smaller caption.
  The One Identity dates cover total employment, not an invented promotion date.
- Rebuild `cv.pdf`, run the checks, and review a PNG at normal reading size before
  committing. Text extraction alone does not establish visual quality.

## Continuous build & deploy

Every push to `main` and every PR triggers
[`.github/workflows/build.yml`](.github/workflows/build.yml), which:

1. Installs Tectonic and compiles `cv.tex`.
2. Runs the content-independent checker tests and checks PDF mechanics with PyMuPDF.
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
