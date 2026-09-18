#!/usr/bin/env python3
"""Generate a post's social (og:image) card.

    python3 tools/make-og-card.py <slug> [--subtitle "text"] [--replace]

Reads title (and optional card_subtitle) from _blogsrc/posts/<slug>.md,
renders og/<slug>.png at 2400x1260 in the site palette (cream, terracotta,
Fraunces), and writes the image: line into the post's front matter.

Why this exists: without a per-post card, shared links fall back to the
site-wide og-image, which is a personal photo and wrong for an essay.
Rendered at 2x because platforms re-encode cards to JPEG and downscale;
1200px serif strokes come out pixelated.

Cache rule: scrapers cache the card by URL. If a card was already shared
publicly, do NOT overwrite it in place -- rerun with --replace, which
writes a -2/-3 suffixed file and repoints the front matter.

Font: Fraunces (SIL OFL), vendored in tools/fonts/.
"""
import re, sys, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "tools/fonts/Fraunces-variable.ttf")
W, H = 2400, 1260
CREAM, INK = (250, 247, 242), (26, 24, 22)
TERRA, GRAY = (160, 79, 60), (110, 105, 99)
MARGIN, MAXW = 180, 2040

def fr(size, name):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(name)
    return f

def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    replace = "--replace" in sys.argv
    subtitle = None
    if "--subtitle" in sys.argv:
        subtitle = sys.argv[sys.argv.index("--subtitle") + 1]
    if not args:
        sys.exit(__doc__)
    slug = re.sub(r"^.*/|\.md$", "", args[0])
    post = os.path.join(ROOT, f"_blogsrc/posts/{slug}.md")
    src = open(post, encoding="utf-8").read()
    title = re.search(r'^title:\s*"(.+?)"', src, re.M).group(1)
    if subtitle is None:
        m = re.search(r'^card_subtitle:\s*"(.+?)"', src, re.M)
        subtitle = m.group(1) if m else None

    out_name = f"{slug}.png"
    if os.path.exists(os.path.join(ROOT, "og", out_name)) and not replace:
        sys.exit(f"og/{out_name} exists. If it was never shared, delete it and rerun.\n"
                 f"If it WAS shared, rerun with --replace (writes a suffixed file; scrapers cache by URL).")
    if replace:
        n = 2
        while os.path.exists(os.path.join(ROOT, "og", f"{slug}-{n}.png")): n += 1
        out_name = f"{slug}-{n}.png"

    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle((MARGIN, 216, MARGIN + 120, 232), fill=TERRA)
    # fit title: shrink until <=3 lines
    size = 170
    while True:
        big = fr(size, "SemiBold")
        lines = wrap(d, title, big, MAXW)
        if len(lines) <= 3 or size <= 110: break
        size -= 10
    y = 330
    for ln in lines:
        d.text((MARGIN, y), ln, font=big, fill=INK)
        y += int(size * 1.24)
    if subtitle:
        d.text((MARGIN, y + 80), subtitle, font=fr(58, "Regular"), fill=GRAY)
    d.text((MARGIN, H - 160), "ahmedkamal.me", font=fr(50, "SemiBold"), fill=TERRA)

    os.makedirs(os.path.join(ROOT, "og"), exist_ok=True)
    out_path = os.path.join(ROOT, "og", out_name)
    img.save(out_path)

    url = f"https://ahmedkamal.me/og/{out_name}"
    line = f'image: "{url}"'
    if re.search(r'^image:.*$', src, re.M):
        src = re.sub(r'^image:.*$', line, src, count=1, flags=re.M)
    else:
        src = src.replace("archived: false", f"archived: false\n{line}", 1)
    open(post, "w", encoding="utf-8").write(src)
    print(f"wrote og/{out_name} and set front matter:\n  {line}")

if __name__ == "__main__":
    main()
