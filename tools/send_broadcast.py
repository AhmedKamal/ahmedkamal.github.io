#!/usr/bin/env python3
"""Create and schedule a Kit broadcast for a newly published post.

    KIT_API_SECRET=... python3 tools/send_broadcast.py <slug> [--dry-run]

Reads the post, builds a teaser email (title, first paragraphs, read-more
link), and schedules a broadcast 30 minutes out. Skips archived posts,
posts marked `newsletter: false`, and anything already broadcast (subject
match) so re-runs are safe. Called by .github/workflows/newsletter.yml.
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.convertkit.com/v3"
SITE = "https://ahmedkamal.me"

def api(path, payload=None):
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(API + path, data=data,
        headers={"Content-Type": "application/json"}, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def first_paragraphs(body, n=3):
    out = []
    for block in re.split(r"\n\s*\n", body.strip()):
        b = block.strip()
        if not b or b.startswith(("#", "!", "<", "-", ">", "|", "```")):
            if b.startswith("#") and out: break   # stop at first section heading
            continue
        b = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b)          # strip links
        b = re.sub(r"\*\*([^*]+)\*\*", r"\1", b)                 # strip bold
        out.append(b.replace("\n", " "))
        if len(out) >= n: break
    return out

def main():
    slug = re.sub(r"^.*/|\.md$|\.html$", "", sys.argv[1])
    dry = "--dry-run" in sys.argv
    secret = os.environ.get("KIT_API_SECRET", "")
    if not dry and not secret:
        sys.exit("KIT_API_SECRET not set")

    for ext in (".md", ".html"):
        p = f"_blogsrc/posts/{slug}{ext}"
        if os.path.exists(p): break
    src = open(p, encoding="utf-8").read()
    fm, body = re.match(r"^---\n(.*?)\n---\n(.*)$", src, re.S).groups()
    get = lambda k: (re.search(rf'^{k}:\s*"?(.*?)"?\s*$', fm, re.M) or [None, ""])[1]

    if get("archived") == "true":  sys.exit(f"skip: {slug} is archived")
    if get("newsletter") == "false": sys.exit(f"skip: {slug} opted out")

    title = get("title"); url = f"{SITE}/blog/{slug}/"
    paras = first_paragraphs(body)
    content = "".join(f"<p>{p}</p>" for p in paras) + \
        f'<p><a href="{url}">Read the whole essay &rarr;</a></p>' + \
        '<p style="color:#8a7f6d;font-size:14px">You subscribed at ahmedkamal.me. ' \
        'If there is no essay, there is no email.</p>'

    if dry:
        print(f"DRY RUN\nsubject: {title}\nurl: {url}\n---\n{content}")
        return

    existing = api(f"/broadcasts?api_secret={secret}&page=1").get("broadcasts", [])
    if any(b.get("subject") == title for b in existing):
        sys.exit(f"skip: broadcast '{title}' already exists")

    send_at = (datetime.now(timezone.utc) + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = api("/broadcasts", {"api_secret": secret, "subject": title,
        "content": content, "description": f"Essay: {slug}",
        "public": False, "send_at": send_at})
    print(f"scheduled broadcast {r['broadcast']['id']} for {send_at}: {title}")

if __name__ == "__main__":
    main()
