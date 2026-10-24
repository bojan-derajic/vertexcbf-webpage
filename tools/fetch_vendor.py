"""Download the third-party assets the site and the poster are built on.

    python tools/fetch_vendor.py

Inter  -> assets/fonts   (SIL Open Font License 1.1, latin + latin-ext subsets)
KaTeX  -> assets/katex   (MIT, pinned version, woff2 fonts only)

Both are vendored so that the published page makes no third-party requests.
"""
import pathlib, re, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
KATEX_VERSION = "0.16.22"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}


def get(url: str, binary: bool = False):
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
    return data if binary else data.decode()


def fetch_inter() -> None:
    out = ROOT / "assets/fonts"
    out.mkdir(parents=True, exist_ok=True)
    css = get("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap")
    keep, rules, total = {"latin", "latin-ext"}, [], 0
    parts = re.split(r"/\*\s*([a-z0-9\-]+)\s*\*/", css)      # [pre, label, block, ...]
    for label, block in zip(parts[1::2], parts[2::2]):
        if label not in keep:
            continue
        weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
        url    = re.search(r"url\((https://[^)]+)\)", block).group(1)
        rng    = re.search(r"unicode-range:\s*([^;]+);", block).group(1).strip()
        name   = f"inter-{weight}-{label}.woff2"
        blob   = get(url, binary=True)
        (out / name).write_bytes(blob)
        total += len(blob)
        rules.append(f"@font-face {{\n  font-family: 'Inter';\n  font-style: normal;\n"
                     f"  font-weight: {weight};\n  font-display: swap;\n"
                     f"  src: url('{name}') format('woff2');\n  unicode-range: {rng};\n}}")
    (out / "inter.css").write_text(
        "/* Inter (SIL Open Font License 1.1) — latin + latin-ext subsets, self-hosted. */\n"
        + "\n".join(rules) + "\n")
    print(f"Inter: {len(rules)} faces, {total/1024:.0f} KB -> {out.relative_to(ROOT)}")


def fetch_katex() -> None:
    out = ROOT / "assets/katex"
    (out / "fonts").mkdir(parents=True, exist_ok=True)
    base = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/"
    css = get(base + "katex.min.css")          # kept verbatim: browsers pick the woff2 src
    (out / "katex.min.css").write_text(css)
    (out / "katex.min.js").write_text(get(base + "katex.min.js"))
    (out / "auto-render.min.js").write_text(get(base + "contrib/auto-render.min.js"))
    names, total = sorted(set(re.findall(r"fonts/(KaTeX_[A-Za-z0-9\-]+\.woff2)", css))), 0
    for n in names:                            # only woff2; woff/ttf are never requested
        blob = get(base + "fonts/" + n, binary=True)
        (out / "fonts" / n).write_bytes(blob)
        total += len(blob)
    print(f"KaTeX {KATEX_VERSION}: {len(names)} fonts, {total/1024:.0f} KB -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    fetch_inter()
    fetch_katex()
