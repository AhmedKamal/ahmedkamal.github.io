#!/usr/bin/env python3
"""Migrate the Ghost blog (blog.ahmedkamal.me) into the Eleventy source tree.

Reads the Ghost SQLite backup, applies the editorial triage (promote / archive /
retire), cleans Ghost-specific markup, localises and optimises images, and writes
post sources into _blogsrc/posts and _blogsrc/drafts.

Run once (or re-run: it is idempotent, it overwrites its own output):

    python3 tools/migrate_ghost.py \
        --db  ../ghost-backup-2026-08-04_02-00-01/data/ghost.db \
        --img ../ghost-backup-2026-08-04_02-00-01/images
"""

import argparse
import html
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys

# --- Editorial triage -------------------------------------------------------

# Promoted: migrated into the curated blog stream.
PROMOTED = [
    "how-to-be-a-machine-learning-engineer",
    "managing-emr-cluster-logs",
    # Both Spark posts are archived, not promoted. They are the two Publications
    # on Ahmed's LinkedIn, but the tooling they recommend (Spark 1.6, Ooyala's
    # Spark Job Server, early Livy, Zeppelin-era notebooks) has been superseded
    # by EMR Serverless, the Kubernetes operator and Spark Connect. Obsolete
    # advice costs more credibility with senior engineers than it earns.
    "the-future-of-remote-work",
    "my-reflections-on-careem-deal-with-uber",
    "how-to-effectively-manage-teams-as-your-organization-scales",
]

# "Start here" picks on the blog index. Empty on purpose: with only 5 curated
# posts, highlighting 3 of them is repetition, not curation. The index template
# hides the section when nothing is featured; add a slug here (or featured: true
# in a post's front matter) once there is an anchor piece worth pointing at.
FEATURED = set()

# Kept in the stream, but sunk to the bottom of the index regardless of date:
# posts worth having but not worth setting the tone of the page.
DEMOTE = {"managing-emr-cluster-logs"}

# Published posts that are not worth keeping online at all: Ghost meta-posts and
# sub-150-word troubleshooting stubs.
RETIRE = {
    "migration-to-ghost",
    "how-to-setup-mobinil-usb-modem-connection",
    "error-aapt-exe-exited-with-code-1",
    "why-visualization-is-important-in-data-science",
}

# Ghost's own demo content, shipped with every new install. Never ours.
GHOST_DEMO = {
    "welcome-2", "the-editor-2", "using-tags", "managing-users",
    "advanced-markdown", "themes-2", "coming-soon",
}

# Pages handled outside the blog build.
PAGES_ELSEWHERE = {"muslim-thoughts", "public-speaking", "about"}

# Titles worth a light touch on the way in. Everything else keeps its title.
RETITLE = {
    "how-to-be-a-machine-learning-engineer": "How to become a machine learning engineer",
    "managing-emr-cluster-logs":
        "Your absolute guide to managing Hadoop logging configurations",
    "productionizing-apache-spark-data-pipelines":
        "Productionizing Apache Spark data pipelines",
    "how-to-effectively-manage-teams-as-your-organization-scales":
        "How to manage teams as your organization scales",
    "my-reflections-on-careem-deal-with-uber":
        "My reflections on the Careem–Uber deal",
    "the-future-of-remote-work":
        "The virtual workspace: how AI is shaping the future of remote work",
}

# Decorative stock photography. The brief rules it out, and every one of these is
# a remote hotlink that can rot. Content images (diagrams, screenshots) are kept.
DROP_REMOTE_STOCK = re.compile(r"https?://images\.unsplash\.com/")

MAX_IMG_WIDTH = 1400  # 700px column at 2x
WEBP_QUALITY = "82"


# --- Ghost markup cleanup ---------------------------------------------------

def strip_scripts(h):
    """Remove third-party widget loaders: embedly, Quora, twitter, etc."""
    return re.sub(r"<script\b.*?</script>", "", h, flags=re.S | re.I)


def strip_ghost_comments(h):
    return re.sub(r"<!--\s*kg-card-(begin|end):[^>]*-->", "", h)


def fix_spacing(h):
    """Ghost inherited French-style spacing before punctuation. Clean it up.

    Non-breaking spaces are normalised first, otherwise they survive the strip.
    Punctuation is only closed up when a space or tag follows, so emoticons like
    " ;)" and ellipses like " ..etc" are left alone.
    """
    h = h.replace("\xa0", " ").replace("&nbsp;", " ")
    h = re.sub(r" +([?!:;,])(\s|<|$)", r"\1\2", h)
    # A full stop only when it closes a word, so " ..etc" survives.
    h = re.sub(r"(\w) +\.(\s|<|$)", r"\1.\2", h)
    return h


def drop_title_echo(h, title):
    """Remove a leading heading that just restates the post title."""
    m = re.match(r"\s*<h[1-3][^>]*>(.*?)</h[1-3]>\s*", h, re.S)
    if not m:
        return h
    def tokens(s):
        return set(re.findall(r"[a-z0-9]+", s.lower())) - {
            "a", "an", "the", "for", "on", "of", "in", "to", "and"}
    a, b = tokens(text_of(m.group(1))), tokens(title)
    if not a or not b:
        return h
    overlap = len(a & b) / min(len(a), len(b))
    return h[m.end():] if overlap >= 0.6 else h


def rewrite_ghost_urls(h, slug_map):
    """__GHOST_URL__ pointed at blog.ahmedkamal.me. Repoint at /blog/."""
    h = re.sub(r"__GHOST_URL__/content/images/", "/blog/media/", h)
    # Internal post links: keep them only if the target survived the triage.
    def _link(m):
        target = m.group(1)
        if target in slug_map:
            return '"/blog/%s/"' % target
        return '"/blog/archive/"'
    h = re.sub(r'"__GHOST_URL__/([a-z0-9\-]+)/"', _link, h)
    # Subscribe anchors: Ghost membership is gone. Unwrap the link, keep the text.
    h = re.sub(r'<a[^>]*href="__GHOST_URL__/#subscribe"[^>]*>(.*?)</a>',
               r"\1", h, flags=re.S)
    h = re.sub(r'<a[^>]*href="__GHOST_URL__[^"]*"[^>]*>(.*?)</a>', r"\1", h,
               flags=re.S)
    h = h.replace("__GHOST_URL__", "https://ahmedkamal.me/blog")
    return h


SELF_PROMO = re.compile(
    r"(did you like what you read|don'?t forget to subscribe|please share this post"
    r"|subscribe to my personal blog|find me on twitter|shameless plug"
    r"|make sure to subscribe|check my other posts on medium"
    r"|feel free to share this|i tweet about"
    # LinkedIn-style engagement bait. Wrong register for this site.
    r"|have you faced similar|what strategies or lessons)",
    re.I)


def strip_self_promo(h):
    """Drop Ghost-era 'subscribe / follow me on Medium' tails and engagement bait.

    These blocks name a dead newsletter and an old handle (@_akamal8_). Matching
    runs on the text of each block, not the raw HTML, because Ghost buried the
    wording under nested <em>/<strong> tags.
    """
    def filter_blocks(tag, body):
        pat = re.compile(r"<%s\b[^>]*>((?:(?!</%s>).)*)</%s>" % (tag, tag, tag),
                         re.S)
        return pat.sub(
            lambda m: "" if SELF_PROMO.search(text_of(m.group(1))) else m.group(0),
            body)

    for tag in ("p", "h1", "h2", "h3", "li"):
        h = filter_blocks(tag, h)
    # Headings and list wrappers left empty by the filter.
    h = re.sub(r"<h[1-6][^>]*>\s*</h[1-6]>", "", h)
    h = re.sub(r"<(ul|ol)>\s*</\1>", "", h)
    # Orphaned trailing rules.
    h = re.sub(r"(?:<hr\s*/?>\s*)+\Z", "", h)
    return h


def embedly_cards(h):
    """Embedly blockquote cards (their JS is stripped) -> static link cards."""
    def build(m):
        inner = m.group(1)
        link = re.search(r'<h[1-6][^>]*><a href="([^"]+)">(.*?)</a></h[1-6]>',
                         inner, re.S)
        desc = re.search(r"<p>(.*?)</p>", inner, re.S)
        if not link:
            return m.group(0)
        out = ['<a class="link-card" href="%s" rel="noopener">' % link.group(1),
               '<span class="lc-title">%s</span>' % link.group(2).strip()]
        if desc:
            out.append('<span class="lc-desc">%s</span>' % desc.group(1).strip())
        out.append("</a>")
        return "".join(out)

    return re.sub(r'<blockquote class="embedly-card">(.*?)</blockquote>', build, h,
                  flags=re.S)


def drop_empty_anchors(h):
    return re.sub(r"<a\b[^>]*>\s*</a>", "", h)


def bookmark_cards(h):
    """Ghost bookmark cards -> static link cards.

    Drops the remote favicon and thumbnail (both hotlinks, one an animated GIF).
    """
    pat = re.compile(
        r'<figure class="kg-card kg-bookmark-card[^"]*">\s*'
        r'<a class="kg-bookmark-container" href="([^"]+)">(.*?)</a>\s*</figure>',
        re.S)

    def build(m):
        href, inner = m.group(1), m.group(2)
        def grab(cls):
            mm = re.search(r'<div class="kg-bookmark-%s">(.*?)</div>' % cls,
                           inner, re.S)
            return mm.group(1).strip() if mm else ""
        def grab_span(cls):
            mm = re.search(r'<span class="kg-bookmark-%s">(.*?)</span>' % cls,
                           inner, re.S)
            return mm.group(1).strip() if mm else ""
        title = grab("title")
        desc = grab("description")
        author = grab_span("author")
        out = ['<a class="link-card" href="%s" rel="noopener">' % href]
        if title:
            out.append('<span class="lc-title">%s</span>' % title)
        if desc:
            out.append('<span class="lc-desc">%s</span>' % desc)
        if author:
            out.append('<span class="lc-meta">%s</span>' % author)
        out.append("</a>")
        return "".join(out)

    return pat.sub(build, h)


def youtube_embeds(h):
    """YouTube iframes -> click-to-play facade. No third-party JS until clicked."""
    def build(m):
        vid = m.group(1)
        return (
            '<div class="video-embed" data-video="%s">'
            '<button type="button" class="video-play" '
            'aria-label="Play video">'
            '<svg viewBox="0 0 24 24" aria-hidden="true">'
            '<path d="M8 5v14l11-7z"/></svg>'
            '<span>Play video</span></button></div>' % vid)

    h = re.sub(
        r'<figure class="kg-card kg-embed-card">\s*'
        r'<iframe[^>]*src="https://www\.youtube(?:-nocookie)?\.com/embed/'
        r'([A-Za-z0-9_\-]+)[^"]*"[^>]*>\s*</iframe>\s*</figure>',
        build, h, flags=re.S)
    return h


def tweet_embeds(h):
    """Twitter blockquote embeds -> static quote cards linking to the tweet.

    Handles both figure-wrapped and bare blockquotes, and reads the author from
    the embed rather than assuming it is ours (some are quoted third parties).
    """
    def build(m):
        inner = m.group("inner")
        body = re.search(r"<p[^>]*>(.*?)</p>", inner, re.S)
        text = body.group(1).strip() if body else ""
        link = re.search(r'href="(https://twitter\.com/[^"]*/status/[^"]*)"',
                         inner)
        url = link.group(1).split("?")[0] if link else ""
        date = re.search(r'status/[^"]*"[^>]*>([^<]+)</a>', inner)
        when = date.group(1).strip() if date else "View tweet"
        who = re.search(r"&mdash;\s*([^(<]+)\(@([A-Za-z0-9_]+)\)", inner)
        handle = "@" + who.group(2) if who else ""
        rtl = ' dir="rtl" lang="ar"' if 'dir="rtl"' in inner else ""
        out = ['<blockquote class="tweet-card"%s>' % rtl, "<p>%s</p>" % text]
        if url:
            label = " · ".join(x for x in (handle, when) if x)
            out.append('<a class="tweet-src" href="%s" rel="noopener">%s</a>'
                       % (url, label))
        out.append("</blockquote>")
        return "".join(out)

    # Figure-wrapped first, then any bare blockquote left over.
    h = re.sub(r'<figure class="kg-card kg-embed-card">\s*'
               r'<blockquote class="twitter-tweet">(?P<inner>.*?)</blockquote>'
               r"\s*</figure>", build, h, flags=re.S)
    h = re.sub(r'<blockquote class="twitter-tweet">(?P<inner>.*?)</blockquote>',
               build, h, flags=re.S)
    return h


def figure_from_paragraph(h):
    """<p><img><br>caption</p> (Ghost markdown cards) -> <figure>."""
    pat = re.compile(
        r"<p>\s*(<img[^>]*>)\s*(?:<br\s*/?>)?\s*(.*?)\s*</p>", re.S)

    def build(m):
        img, caption = m.group(1), m.group(2).strip()
        caption = re.sub(r"^<small>(.*)</small>$", r"\1", caption, flags=re.S)
        if not caption:
            return "<figure>%s</figure>" % img
        return "<figure>%s<figcaption>%s</figcaption></figure>" % (img, caption)

    return pat.sub(build, h)


def normalise_kg_figures(h):
    h = re.sub(r'<figure class="kg-card kg-image-card[^"]*">', "<figure>", h)
    h = re.sub(r'<img([^>]*?)\sclass="kg-image"', r"<img\1", h)
    return h


def drop_stock_photos(h):
    """Remove decorative stock photography, keeping its caption's siblings intact.

    Covers both remote Unsplash hotlinks and the copies Ghost cached locally
    (recognisable by Unsplash's photo-<id> filenames).
    """
    stock = r"(?:images\.unsplash\.com|/photo-\d{10,}-[0-9a-f]{6,})"
    # Whole figures whose image is stock.
    h = re.sub(r"<figure>(?:(?!</figure>).)*?" + stock +
               r"(?:(?!</figure>).)*?</figure>", "", h, flags=re.S)
    # Bare <img> plus any trailing credit line.
    h = re.sub(r"<img[^>]*" + stock + r"[^>]*>\s*(?:<br\s*/?>)?\s*"
               r"(?:<small>.*?</small>)?", "", h, flags=re.S)
    # Empty paragraphs left over.
    h = re.sub(r"<p>\s*</p>", "", h)
    return h


def promote_headings(h):
    """Normalise heading levels so the table of contents reflects the real outline.

    Ghost-era posts mix <h2> and <h3> as siblings. When there is at most one <h2>
    and several <h3>s, the <h3>s are peers, not children.
    """
    h2s = len(re.findall(r"<h2\b", h))
    h3s = len(re.findall(r"<h3\b", h))
    if h2s <= 1 and h3s >= 2:
        h = re.sub(r"<(/?)h3", r"<\1h2", h)
        h = re.sub(r"<(/?)h4", r"<\1h3", h)
    return h


def br_lists(h):
    """<p>a<br>b<br>c</p> of short lines -> a real list.

    Ghost-era posts used line breaks where lists belonged. Same words, correct
    semantics, much cleaner rendering.
    """
    def build(m):
        inner = m.group(1)
        parts = [p.strip() for p in re.split(r"<br\s*/?>\s*", inner)]
        parts = [p for p in parts if p]
        if len(parts) < 3:
            return m.group(0)
        if any(len(text_of(p)) > 60 or "<" in p.replace("<a", "").replace("</a", "")
               for p in parts):
            return m.group(0)
        return "<ul>%s</ul>" % "".join("<li>%s</li>" % p for p in parts)

    return re.sub(r"<p>((?:(?!</p>).)*?<br\s*/?>(?:(?!</p>).)*)</p>", build, h,
                  flags=re.S)


def tidy(h):
    h = re.sub(r"<p>\s*(?:<br\s*/?>)?\s*</p>", "", h)
    h = re.sub(r"\n{3,}", "\n\n", h)
    return h.strip()


# --- Images ----------------------------------------------------------------

def optimise_image(src, dest_webp):
    """Resize to a sane max width and encode WebP. Falls back to a plain copy."""
    os.makedirs(os.path.dirname(dest_webp), exist_ok=True)
    tmp = dest_webp + ".tmp" + os.path.splitext(src)[1]
    try:
        shutil.copy2(src, tmp)
        subprocess.run(["sips", "-Z", str(MAX_IMG_WIDTH), tmp],
                       check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        subprocess.run(["cwebp", "-quiet", "-q", WEBP_QUALITY, tmp,
                        "-o", dest_webp], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        fallback = os.path.splitext(dest_webp)[0] + os.path.splitext(src)[1]
        shutil.copy2(src, fallback)
        return False
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def localise_images(h, img_root, media_out, report):
    """Copy every referenced Ghost image into /blog/media, optimised."""
    def repl(m):
        attr, path = m.group(1), m.group(2)
        src = os.path.join(img_root, path)
        if not os.path.exists(src):
            report["missing"].append(path)
            return m.group(0)
        stem, _ = os.path.splitext(path)
        dest = os.path.join(media_out, stem + ".webp")
        if not os.path.exists(dest):
            ok = optimise_image(src, dest)
            report["images"].append((path, "webp" if ok else "copied"))
        return '%s="/blog/media/%s.webp"' % (attr, stem)

    return re.sub(r'(src|href)="/blog/media/([^"]+)"', repl, h)


def add_img_attrs(h):
    h = re.sub(r"<img(?![^>]*\bloading=)", '<img loading="lazy" decoding="async"',
               h)
    h = re.sub(r"<img([^>]*?)\salt(?=[\s>])", r'<img\1 alt=""', h)
    # Ghost derived alt text from filenames ("data-scientist-def--1-"). That is
    # noise in a screen reader; the figcaption carries the real description.
    h = re.sub(r'alt="([^"]*)"',
               lambda m: 'alt=""' if re.fullmatch(r"[\w\-.]{3,}", m.group(1))
               and " " not in m.group(1) else m.group(0), h)
    return h


# --- Front matter ----------------------------------------------------------

def text_of(h):
    t = re.sub(r"<[^>]+>", " ", h)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def excerpt_of(h, limit=185):
    for m in re.finditer(r"<p>(.*?)</p>", h, re.S):
        t = text_of(m.group(1))
        if len(t) > 60:
            if len(t) <= limit:
                return t
            cut = t[:limit].rsplit(" ", 1)[0]
            return cut + "…"
    return text_of(h)[:limit]


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)


def clean_title(slug, title):
    if slug in RETITLE:
        return RETITLE[slug]
    t = re.sub(r"\s+([?!])", r"\1", title.replace(" ", " ")).strip()
    return t


def write_post(out_dir, slug, meta, body):
    os.makedirs(out_dir, exist_ok=True)
    fm = ["---"]
    for k, v in meta.items():
        if isinstance(v, bool):
            fm.append("%s: %s" % (k, "true" if v else "false"))
        elif isinstance(v, list):
            fm.append("%s: [%s]" % (k, ", ".join(yaml_str(x) for x in v)))
        else:
            fm.append("%s: %s" % (k, yaml_str(str(v))))
    fm.append("---")
    path = os.path.join(out_dir, slug + ".html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(fm) + "\n" + body + "\n")
    return path


# --- Main ------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--img", required=True)
    ap.add_argument("--src", default="_blogsrc")
    ap.add_argument("--media", default="blog/media")
    args = ap.parse_args()

    db = sqlite3.connect(args.db)
    db.row_factory = sqlite3.Row
    rows = db.execute(
        "SELECT slug, title, html, status, type, published_at, feature_image "
        "FROM posts ORDER BY published_at").fetchall()

    posts_dir = os.path.join(args.src, "posts")
    drafts_dir = os.path.join(args.src, "drafts")
    pages_dir = os.path.join(args.src, "pages-out")
    for d in (posts_dir, drafts_dir, pages_dir):
        os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            if f.endswith(".html"):
                os.remove(os.path.join(d, f))

    tags_by_slug = {}
    for r in db.execute(
            "SELECT p.slug, t.name FROM posts p "
            "JOIN posts_tags pt ON pt.post_id = p.id "
            "JOIN tags t ON t.id = pt.tag_id"):
        if r[1].startswith("#Import"):
            continue
        tags_by_slug.setdefault(r[0], []).append(r[1])

    published = [r for r in rows if r["status"] == "published"
                 and r["type"] == "post" and r["slug"] not in RETIRE]
    kept_slugs = {r["slug"] for r in published}

    report = {"images": [], "missing": [], "promoted": [], "archived": [],
              "drafts": [], "retired": [], "pages": []}

    def clean_body(raw):
        h = raw or ""
        h = strip_scripts(h)
        h = strip_ghost_comments(h)
        h = rewrite_ghost_urls(h, kept_slugs)
        h = bookmark_cards(h)
        h = embedly_cards(h)
        h = youtube_embeds(h)
        h = tweet_embeds(h)
        h = drop_empty_anchors(h)
        h = normalise_kg_figures(h)
        h = drop_stock_photos(h)
        h = figure_from_paragraph(h)
        h = br_lists(h)
        h = strip_self_promo(h)
        h = fix_spacing(h)
        h = promote_headings(h)
        h = localise_images(h, args.img, args.media, report)
        h = add_img_attrs(h)
        return tidy(h)

    for r in rows:
        slug, status, ptype = r["slug"], r["status"], r["type"]

        if slug in GHOST_DEMO or slug in RETIRE or slug in PAGES_ELSEWHERE:
            if slug in RETIRE or slug in GHOST_DEMO:
                report["retired"].append(slug)
            continue

        title = clean_title(slug, r["title"] or slug)
        body = drop_title_echo(clean_body(r["html"]), title)
        date = (r["published_at"] or "")[:10]

        if status == "published" and ptype == "post":
            archived = slug not in PROMOTED
            meta = {
                "title": title,
                "date": date or "2012-01-01",
                "slug": slug,
                "description": excerpt_of(body),
                "archived": archived,
                "layout": "post.njk",
            }
            if slug in FEATURED:
                meta["featured"] = True
            if slug in DEMOTE:
                meta["demote"] = True
            if tags_by_slug.get(slug):
                meta["tags_original"] = tags_by_slug[slug]
            write_post(posts_dir, slug, meta, body)
            report["archived" if archived else "promoted"].append(slug)
        else:
            meta = {
                "title": title,
                "slug": slug,
                "note": "Ghost draft, never published. Not built.",
            }
            write_post(drafts_dir, slug, meta, body)
            report["drafts"].append(slug)

    # The faith page lives at /thoughts/, outside the blog build.
    page = db.execute("SELECT title, html FROM posts WHERE slug='muslim-thoughts'"
                      ).fetchone()
    if page:
        with open(os.path.join(pages_dir, "muslim-thoughts.html"), "w",
                  encoding="utf-8") as fh:
            fh.write(clean_body(page["html"]))
        report["pages"].append("muslim-thoughts -> /thoughts/")

    print("promoted : %d" % len(report["promoted"]))
    for s in report["promoted"]:
        print("           %s" % s)
    print("archived : %d" % len(report["archived"]))
    print("drafts   : %d" % len(report["drafts"]))
    print("retired  : %d  (%s)" % (len(report["retired"]),
                                   ", ".join(sorted(report["retired"]))))
    print("images   : %d optimised" % len(report["images"]))
    if report["missing"]:
        print("MISSING IMAGES:")
        for m in sorted(set(report["missing"])):
            print("   %s" % m)
    print("pages    : %s" % ", ".join(report["pages"]))


if __name__ == "__main__":
    sys.exit(main())
