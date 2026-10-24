# VertexCBF — project page and poster

Source of the [VertexCBF project page](https://bojan-derajic.github.io/vertexcbf-page/) and of the
CoRL 2026 poster. The code lives in [bojan-derajic/vertexcbf](https://github.com/bojan-derajic/vertexcbf).

> B. Derajić, S. Bernhard, W. Hönig. *VertexCBF: Improving Neural Control Barrier Functions via
> Vertex-Restricted Control Search.* CoRL 2026. [arXiv:2609.12831](https://arxiv.org/abs/2609.12831)

```
.
├── index.html                              project page
├── poster/poster.html                      poster source (A0 landscape, 1189 × 841 mm)
├── assets/
│   ├── css/{site,poster}.css
│   ├── img/                                figures, schematics, QR codes
│   ├── logo/                               TU Berlin, IMRC, CoRL
│   ├── fonts/, katex/                      vendored Inter and KaTeX
│   └── poster/
│       ├── vertexcbf-corl2026-poster.pdf   the printable poster
│       └── preview.jpg                     thumbnail / link preview
└── tools/                                  build scripts
```

Everything is static HTML and CSS; the page and the poster share one accent colour, the same type
scale and the same vendored web fonts, so the page makes no third-party requests.

## Publishing

GitHub Pages serves the repository root: **Settings → Pages → Deploy from a branch → `main`,
`/ (root)`**. The empty `.nojekyll` file makes Pages serve the files as they are.

## Rebuilding

```bash
pip install -r tools/requirements.txt
python -m playwright install chromium

python tools/fetch_vendor.py                    # (re)download Inter + KaTeX into assets/
python tools/make_assets.py --src ../vertexcbf  # paper figures, logos, QR codes -> assets/
python tools/make_diagrams.py                   # the schematic SVGs
python tools/build_poster.py                    # poster.html -> A0 PDF + preview.jpg
```

`make_assets.py` reads the git-ignored `paper/`, `dev/` and `logos/` working directories of a local
checkout of the code repository (`--src`, by default a clone next to this one). The files it
generates under `assets/` are committed, so the site builds without them.

`build_poster.py` prints how full each poster column is and warns if a column or a display formula
overflows — the poster must stay exactly one page.

## Editing the poster

Edit `poster/poster.html` and `assets/css/poster.css`, then re-run `tools/build_poster.py`. Layout
is authored in millimetres and points, so what the browser shows is what the PDF contains. Open
`poster/poster.html` directly in a browser to iterate without rebuilding.

## Third-party assets

- [Inter](https://rsms.me/inter/) — SIL Open Font License 1.1 (latin + latin-ext subsets)
- [KaTeX](https://katex.org) 0.16.22 — MIT License
