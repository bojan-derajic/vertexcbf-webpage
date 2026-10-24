"""Render the A0 poster to PDF (and a PNG proof) with headless Chromium.

    pip install playwright && python -m playwright install chromium
    python tools/build_poster.py

Writes assets/poster/vertexcbf-corl2026-poster.pdf
and    assets/poster/preview.jpg
"""
import pathlib, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC  = ROOT / "poster/poster.html"
OUT  = ROOT / "assets/poster"
OUT.mkdir(parents=True, exist_ok=True)

W_MM, H_MM = 1189, 841           # A0 landscape
PX_PER_MM  = 96 / 25.4


def _thumbnail(src: pathlib.Path, dst: pathlib.Path, width: int) -> None:
    """The full-page screenshot doubles as the site thumbnail and link preview."""
    im = Image.open(src).convert("RGB")
    im.resize((width, round(width * im.height / im.width)), Image.LANCZOS) \
      .save(dst, quality=86, optimize=True, progressive=True)
    src.unlink()


def main() -> int:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width":  round(W_MM * PX_PER_MM),
                                          "height": round(H_MM * PX_PER_MM)})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(SRC.as_uri(), wait_until="networkidle")
        page.wait_for_function("document.documentElement.dataset.mathReady === '1'")
        page.wait_for_timeout(400)

        pdf = OUT / "vertexcbf-corl2026-poster.pdf"
        page.pdf(path=str(pdf), width=f"{W_MM}mm", height=f"{H_MM}mm",
                 print_background=True, margin={"top": "0", "right": "0",
                                                "bottom": "0", "left": "0"})
        page.screenshot(path=str(OUT / "preview.png"), full_page=True)
        _thumbnail(OUT / "preview.png", OUT / "preview.jpg", 1800)

        # the poster must stay exactly one page, with evenly filled columns
        overflow = page.evaluate(
            "() => ({h: document.body.scrollHeight, w: document.body.scrollWidth,"
            "        ch: document.body.clientHeight, cw: document.body.clientWidth})")
        # one card per column stretches to the bottom, so measure with stretching off
        fill = page.evaluate("""() => {
            document.querySelectorAll('.block.grow').forEach(b => b.style.flex = 'none');
            return [...document.querySelectorAll('.board .col')].map(col => {
                const kids = [...col.children];
                const gap = parseFloat(getComputedStyle(col).rowGap) || 0;
                const used = kids.reduce((a, k) => a + k.getBoundingClientRect().height, 0)
                             + gap * Math.max(0, kids.length - 1);
                return used / col.clientHeight;
            });
        }""")
        # display math cannot wrap, so flag any formula wider than its column
        wide = page.evaluate("""() => {
            const bad = [];
            document.querySelectorAll('.math').forEach(m => {
                const k = m.querySelector('.katex-display > .katex, .katex');
                if (!k) return;
                const over = k.getBoundingClientRect().width - m.clientWidth;
                if (over > 2) bad.push([m.textContent.trim().slice(0, 50),
                                        Math.round(over / 3.7795)]);
            });
            return bad;
        }""")
        browser.close()

    print(f"wrote {pdf.relative_to(ROOT)}  ({pdf.stat().st_size/1024:.0f} KB)")
    print(f"content {overflow['w']}x{overflow['h']} px   page {overflow['cw']}x{overflow['ch']} px")
    print("column fill: " + "  ".join(f"{i+1}:{f:5.1%}" for i, f in enumerate(fill)))
    if overflow["h"] > overflow["ch"] + 1 or overflow["w"] > overflow["cw"] + 1:
        print("WARNING: content overflows the A0 page")
    for i, f in enumerate(fill):
        if f > 1.001:
            print(f"WARNING: column {i+1} overflows ({f:.1%})")
    for txt, mm in wide:
        print(f"WARNING: formula overflows its column by {mm} mm: {txt}")
    for e in errors:
        print("console:", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
