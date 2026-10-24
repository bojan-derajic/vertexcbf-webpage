"""Turn the paper's vector figures and the raw logos into web assets.

    python tools/make_assets.py [--src ../vertexcbf]

The sources are the git-ignored `paper/`, `dev/` and `logos/` working directories of a
local checkout of the code repository (github.com/bojan-derajic/vertexcbf), by default a
clone next to this one.  The generated PNG/SVG files under assets/ are tracked, so the
site builds without them.
"""
import argparse
import pathlib
import pymupdf
import segno
from PIL import Image, ImageChops

ROOT  = pathlib.Path(__file__).resolve().parents[1]
IMG   = ROOT / "assets/img"
LOGO  = ROOT / "assets/logo"

# QR codes printed on the poster
QR_CODES = {
    "qr-paper":   "https://arxiv.org/abs/2609.12831",
    "qr-project": "https://bojan-derajic.github.io/vertexcbf-page/",
}

# figure -> (output name, longest edge in px)
FIGURES = [
    ("compare_inverted_pendulum.pdf",      "compare-ip.png",      1900),
    ("trajectories_inverted_pendulum.pdf", "trajectories-ip.png", 1700),
    ("hardw_exp_vertex_cbf.pdf",           "hardware-plots.png",  1700),
    ("hardw_exp_screen.drawio.pdf",        "hardware-screen.png", 1600),
]


def trim_white(im: Image.Image, pad: int = 6) -> Image.Image:
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if not bbox:
        return im
    return im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                    min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))


def convert(src: pathlib.Path, dst: pathlib.Path, long_edge: int) -> None:
    page = pymupdf.open(src)[0]
    dpi  = max(150, round(long_edge / (max(page.rect.width, page.rect.height) / 72)))
    pix  = page.get_pixmap(dpi=dpi, alpha=False)
    im   = trim_white(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    if im.width > long_edge:
        im = im.resize((long_edge, round(long_edge * im.height / im.width)), Image.LANCZOS)
    im.save(dst, optimize=True)
    print(f"{dst.name:24s} {im.width}x{im.height}  {dst.stat().st_size/1024:6.0f} KB")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", type=pathlib.Path, default=ROOT.parent / "vertexcbf",
                    help="checkout of the code repository holding paper/, dev/, logos/")
    src = ap.parse_args().src.resolve()
    paper, dev, logos = src / "paper/figures", src / "dev/figures", src / "logos"
    for d in (paper, dev, logos):
        if not d.is_dir():
            raise SystemExit(f"missing source directory: {d}  (set --src)")

    IMG.mkdir(parents=True, exist_ok=True)
    LOGO.mkdir(parents=True, exist_ok=True)

    for name, out, edge in FIGURES:
        convert(paper / name, IMG / out, edge)

    # 2-D slices of the learned CBF for all fifteen systems, in one panel
    grid = Image.open(dev / "VRC_DATA_grid_preview.png").convert("RGB")
    grid = grid.resize((1920, round(1920 * grid.height / grid.width)), Image.LANCZOS)
    grid.save(IMG / "systems-grid.png", optimize=True)
    print(f"{'systems-grid.png':24s} {grid.width}x{grid.height} "
          f" {(IMG / 'systems-grid.png').stat().st_size/1024:6.0f} KB")

    # logos: the TU Berlin file is a WEBP despite its .svg name
    tub = Image.open(logos / "LogoDerTechnischenUniversitätBerlin2020.svg").convert("RGBA")
    tub.resize((1200, round(1200 * tub.height / tub.width)), Image.LANCZOS) \
       .save(LOGO / "tu-berlin.png", optimize=True)
    corl = Image.open(logos / "corl_logo.png").convert("RGBA")
    corl = corl.crop(corl.split()[-1].getbbox() or corl.getbbox())
    corl.save(LOGO / "corl.png", optimize=True)
    (LOGO / "imrc.svg").write_bytes((logos / "Logo_RGB.svg").read_bytes())
    print("logos: tu-berlin.png, corl.png, imrc.svg")

    for name, url in QR_CODES.items():
        segno.make(url, error="m").save(IMG / f"{name}.svg", kind="svg",
                                        scale=10, border=0, dark="#16181D")
        print(f"{name + '.svg':24s} {url}")


if __name__ == "__main__":
    main()
