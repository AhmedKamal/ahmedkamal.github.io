# ahmedkamal.me

Personal site for Ahmed Kamal. Static, served by GitHub Pages from `master` at the
apex domain (`CNAME` → ahmedkamal.me), behind Cloudflare.

## Structure

- `index.html` — hand-written single-page bio. No build step. Edit directly.
- `ar/` — hand-written RTL Arabic blog (IBM Plex Sans Arabic + Reem Kufi).
- `thoughts/` — hand-written personal page.
- `_blogsrc/` — Eleventy source for the English blog. **Write here.**
- `blog/` — Eleventy output, committed. **Never edit by hand**, `npm run build` wins.
- `tools/migrate_ghost.py` — one-shot Ghost → Eleventy migration, re-runnable.

Deploy model is deliberate: output is committed so GitHub Pages keeps deploying
straight from the branch. Do not switch Pages to a GitHub Actions source without
asking — the live site is used at events and must not gain a new failure mode.

## Blog build

```bash
npm run dev      # preview http://localhost:8080/blog/
npm run build    # regenerate blog/ (always run before committing)
```

Eleventy notes that matter:

- `htmlTemplateEngine: false` — migrated posts are literal HTML and old code
  samples contain `{{ }}`. Do not turn templating on for `.html` posts.
- Permalinks come from `_blogsrc/posts/posts.11tydata.js` via `eleventyComputed`,
  because front-matter permalinks are not interpolated with templating off.
- `pathPrefix: "/blog/"`, so always pipe URLs through the `url` filter.
- The table of contents is a build-time transform that fills `<!-- TOC -->`, adds
  missing heading ids, and needs 3+ headings to appear.

## Design constraints

Benchmarks are huyenchip.com and karpathy.ai. Light cream `#faf7f2`, single
terracotta accent `#a04f3c`, Fraunces for titles, system sans (SF Pro) for body.
No dark mode (the rest of the site is light-only). No third-party JS on load:
Disqus and YouTube both load on click only. Employer-independent copy — Hudhud
gets one sentence, never branding. Never mention KACST.

## Content rules

- Curated stream = 5 posts. 29 archived posts are `noindex`, banner-marked, out of
  the index and feed. Triage lists live at the top of `tools/migrate_ghost.py`.
- Root-level `<slug>/index.html` directories are generated apex redirect stubs
  (`tools/gen-legacy-redirects.py`). Re-run it after changing the post set.
- Ahmed's LinkedIn export is at `../Profile.pdf`. It needs a real PDF extractor
  (`pypdf` in a venv); `pdftoppm` is absent and Spotlight returns null. It is the
  authoritative source for bio copy, titles, and dates.
- **This repo is public. Drafts do not live here.** Drafting happens in Ahmed's
  Obsidian vault, under `Notebook/Blogging/Writing Pipeline/`. Only finished
  posts move into `_blogsrc/posts/`. The 26 old Ghost drafts were migrated out
  in Aug 2026 because a `_blogsrc/drafts/` file never builds but is still
  readable by anyone on GitHub. `eleventy.config.js` still ignores
  `_blogsrc/drafts/**`, so a local, untracked drafts folder is safe.
- Do not invent facts, metrics, or artifact links. Use `[ADD: ...]` placeholders.

## Config

`_blogsrc/_data/site.json` — `ga4_id` is live (`G-7SGXTR10EE`);
`disqus_shortname` is still empty, and empty means the block is omitted entirely.
The hand-written pages (`index.html`, `ar/**`, `thoughts/`) carry the same GA4
snippet inline, including its localhost guard: keep those in sync by hand when the
include changes.

See `PUBLISHING.md` for the full operating manual.
