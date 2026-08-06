#!/bin/bash
# Create a new post and open it.
#
#   ./tools/new-post.sh "The machine that keeps Saudi mapped"
#
# Then write, run `npm run dev` to preview, `npm run build`, and commit.

set -euo pipefail

if [ $# -lt 1 ]; then
	echo "usage: $0 \"Post title\"" >&2
	exit 1
fi

TITLE="$1"
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' \
	| sed -e 's/[^a-z0-9 -]//g' -e 's/  */-/g' -e 's/^-//' -e 's/-$//')
DATE=$(date +%Y-%m-%d)
FILE="_blogsrc/posts/${SLUG}.md"

if [ -e "$FILE" ]; then
	echo "already exists: $FILE" >&2
	exit 1
fi

cat > "$FILE" <<EOF
---
title: "${TITLE}"
date: "${DATE}"
slug: "${SLUG}"
description: "One sentence. Shows on the index and in link previews."
archived: false
---

Write here in Markdown.

## A section heading

Three or more headings turn on the table of contents automatically.
EOF

echo "created $FILE"
echo
echo "next:"
echo "  npm run dev      # preview at http://localhost:8080/blog/"
echo "  npm run build    # regenerate blog/"
echo "  git add -A && git commit -m \"Post: ${TITLE}\" && git push"
