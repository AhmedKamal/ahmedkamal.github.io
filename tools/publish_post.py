#!/usr/bin/env python3
"""Publish exactly one post: the parking dance, scripted.

    python3 tools/publish_post.py <slug> [--dry-run]

Other unpublished (untracked) posts are parked so the built index/feed
contain only already-published posts plus this one; builds; verifies;
commits; pushes; restores the parked drafts and rebuilds locally.
Pushing triggers the newsletter workflow automatically.
"""
import os, re, subprocess, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def sh(cmd, **kw):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.exit(f"FAILED: {cmd}\n{r.stdout}{r.stderr}")
    return r.stdout

def main():
    slug = re.sub(r"^.*/|\.md$|\.html$", "", sys.argv[1])
    dry = "--dry-run" in sys.argv
    post = None
    for ext in (".md", ".html"):
        if os.path.exists(f"_blogsrc/posts/{slug}{ext}"): post = f"_blogsrc/posts/{slug}{ext}"
    if not post: sys.exit(f"no such post: {slug}")

    src = open(post, encoding="utf-8").read()
    title = re.search(r'^title:\s*"(.+?)"', src, re.M).group(1)

    # ---- preflight: refuse to ship a lying file -------------------------
    from datetime import date as _date
    problems = []
    if 'image: "' not in src:
        problems.append(f"no social card. Run: python3 tools/make-og-card.py {slug}")
    fm_date = (re.search(r'^date:\s*"([0-9-]+)"', src, re.M) or [None, ""])[1]
    if fm_date != str(_date.today()) and "--allow-date" not in sys.argv:
        problems.append(f"front-matter date is {fm_date}, today is {_date.today()} "
                        f"(stale ordering games?). Fix the date or pass --allow-date.")
    if "[ADD:" in src:
        problems.append("draft still contains [ADD: ...] placeholders")
    if "One sentence. Shows on the index" in src:
        problems.append("description is still the scaffold placeholder")
    if problems and not dry:
        sys.exit("PREFLIGHT FAILED:\n- " + "\n- ".join(problems))
    if problems:
        print("preflight would fail:\n- " + "\n- ".join(problems))

    untracked = sh("git ls-files --others --exclude-standard _blogsrc/posts/").split()
    park = [p for p in untracked if not p.endswith(f"{slug}.md") and not p.endswith(f"{slug}.html")]
    if dry:
        print(f"would publish: {title}\nwould park: {park or 'nothing'}"); return

    tmp = tempfile.mkdtemp(prefix="park-")
    try:
        for p in park:
            shutil.move(p, os.path.join(tmp, os.path.basename(p)))
            pslug = re.sub(r"\.(md|html)$", "", os.path.basename(p))
            shutil.rmtree(f"blog/{pslug}", ignore_errors=True)
        sh("npm run build")
        idx = open("blog/index.html", encoding="utf-8").read()
        feed = open("blog/feed.xml", encoding="utf-8").read()
        assert slug in idx and slug in feed, "post missing from built index/feed"
        for p in park:
            pslug = re.sub(r"\.(md|html)$", "", os.path.basename(p))
            assert pslug not in idx and pslug not in feed, f"parked draft {pslug} leaked into build"
        sh("git add -A")
        sh(f'git commit -m "Publish: {title}" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"')
        sh("git push origin master")
        print(f"PUBLISHED: {title}\nhttps://ahmedkamal.me/blog/{slug}/\nNewsletter broadcast will schedule itself ~30 min out.")
    finally:
        for f in os.listdir(tmp):
            shutil.move(os.path.join(tmp, f), f"_blogsrc/posts/{f}")
        os.rmdir(tmp)
        subprocess.run("npm run build", shell=True, capture_output=True)

if __name__ == "__main__":
    main()
