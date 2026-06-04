# CV — Adrián Koller

A single-page, ATS-friendly creative CV built in LaTeX/TikZ. Designed for software
engineering applications in Ireland (mobile, full-stack, low-level systems).

The latest compiled output is committed as [`cv.pdf`](cv.pdf).

## Design notes

- **One page, A4**, midnight-blue accent palette.
- **Sidebar layout** with full-width dark header, kerned-caps name lockup, and a
  tracked-caps tagline.
- **Beaded timeline rails** connect entries in Experience, Selected Projects, and
  Education.
- **Soft pill chips** for the “Also Familiar With” block; filled pills for
  Languages; dot-rated scale for Top Skills.
- **ATS-readable** — `pdftitle`/`pdfauthor`/`pdfsubject`/`pdfkeywords` metadata
  is set in `\hypersetup`, and an invisible (1pt, deepink-on-deepink) plain-text
  name + role string is rendered at the top-left of the page so parsers extract
  `Adrián Koller — Software Developer — …` cleanly.
- `\frenchspacing` + a curated `\hyphenation{...}` exception list eliminate
  awkward double-spaces and ugly word breaks.

## Requirements

- A LaTeX engine that supports `xelatex` / `lualatex` features used here.
  [Tectonic](https://tectonic-typesetting.github.io/) is recommended — it
  resolves and downloads packages automatically on first run.

Optional, only for previewing PNG renders during development:

- Python 3 with [`PyMuPDF`](https://pymupdf.readthedocs.io/) (`pip install pymupdf`)

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

### Quick ATS-extraction sanity check

```bash
python -c "import fitz; print(fitz.open('cv.pdf')[0].get_text())"
```

The first non-empty line should be
`Adrián Koller – Software Developer – Mobile, Full-Stack, Low-Level Systems`.

## Project layout

```
cv.tex          # LaTeX source (palette, macros, content)
cv.pdf          # Latest compiled output (committed for convenience)
README.md       # This file
.gitignore
```

## Editing tips

- **Palette** is defined near the top of `cv.tex` (`ink`, `deepink`, `body`,
  `mute`, `paper`).
- **Macros** for sidebar items, language pills, chips, timeline markers, and
  section headers live just below the palette — modify there to retheme.
- The chip block uses explicit `\\` line breaks to enforce a 3-3-3 layout.
  Reorder `\chip{...}` calls to rebalance row widths if you change the entries.
- If a word hyphenates badly after edits, add it (without explicit hyphens) to
  the `\hyphenation{...}` list at the top of `cv.tex`.

## Continuous build

Every push to `main` and every PR triggers
[`.github/workflows/build.yml`](.github/workflows/build.yml), which installs
Tectonic, compiles `cv.tex`, runs an ATS-extraction sanity check, and uploads
the resulting `cv.pdf` as a workflow artifact (`cv-pdf`). You can download the
latest build from the *Actions* tab.

## License

Personal CV — all content © Adrián Koller. The LaTeX scaffolding (macros,
layout) is provided as-is for personal reference; please don’t reuse the
content verbatim.
