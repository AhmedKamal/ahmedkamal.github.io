#!/usr/bin/env python3
"""Generate apex-path redirects for the era when the blog lived at ahmedkamal.me/<slug>/.

Before the move to blog.ahmedkamal.me, posts were served straight off the apex
domain, and links from that era are still in the wild — Ahmed's own LinkedIn
profile links ahmedkamal.me/using-spark-for-data-exploration/ under the Seeloz
role. Those paths now belong to the new site, so each one gets a stub that sends
the reader (and the crawler, via rel=canonical) to /blog/<slug>/.

A Cloudflare redirect rule would be marginally better because it returns a real
301, but it depends on the plan's regex support. These stubs work today with no
configuration. If the rule is set up later, delete the directories this created.

    python3 tools/gen-legacy-redirects.py
"""

import glob
import os
import re

# Paths that belong to the current site and must never be overwritten.
RESERVED = {"blog", "ar", "thoughts", "speaking", "assets", "tools", "fontawesome",
            "static-page", "node_modules"}

# Ghost pages that moved somewhere other than /blog/<slug>/.
SPECIAL = {"public-speaking": "/speaking/"}

STUB = """<!DOCTYPE html>
<html lang="en">
<head>
\t<meta charset="UTF-8">
\t<title>Moved · Ahmed Kamal</title>
\t<meta name="robots" content="noindex, follow">
\t<link rel="canonical" href="https://ahmedkamal.me{target}">
\t<meta http-equiv="refresh" content="0; url={target}">
\t<script>location.replace('{target}');</script>
</head>
<body>
\t<p>This page moved to <a href="{target}">ahmedkamal.me{target}</a>.</p>
</body>
</html>
"""


def main():
    slugs = sorted(
        os.path.basename(p).rsplit(".", 1)[0]
        for p in glob.glob("_blogsrc/posts/*.html") + glob.glob("_blogsrc/posts/*.md"))

    targets = {s: "/blog/%s/" % s for s in slugs}
    targets.update(SPECIAL)

    written, skipped = 0, []
    for slug, target in sorted(targets.items()):
        if slug in RESERVED or not re.fullmatch(r"[a-z0-9][a-z0-9\-]*", slug):
            skipped.append(slug)
            continue
        path = os.path.join(slug, "index.html")
        # Never clobber a real page.
        if os.path.exists(path) and "location.replace" not in open(path, encoding="utf-8").read():
            skipped.append(slug + " (real page)")
            continue
        os.makedirs(slug, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(STUB.format(target=target))
        written += 1

    print("wrote %d apex redirect stubs" % written)
    if skipped:
        print("skipped: %s" % ", ".join(skipped))


if __name__ == "__main__":
    main()
