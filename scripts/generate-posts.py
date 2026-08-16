#!/usr/bin/env python3
"""Generate posts/*.html and index.html from content/raw-posts/."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "content" / "raw-posts"
OUTPUT_DIR = ROOT / "posts"

HEADER = """\
  <header class="site-header">
    <div class="container header-inner">
      <a class="logo" href="__HOME__index.html">
        <img src="__HOME__logo.png" alt="T-Slen Blog" class="logo-img">
      </a>
      <nav class="primary-nav">
        <a href="https://t-slen.com">t-slen.com</a>
        <a href="https://github.com/TeslenkoOleg/angular-tslen-blog" target="_blank" rel="noopener">GitHub</a>
      </nav>
    </div>
  </header>
"""

FOOTER = """\
  <footer class="site-footer">
    <div class="container footer-inner">
      <span>&copy; 2026 Oleh Teslenko.</span>
      <div class="footer-links">
        <a href="https://t-slen.com">t-slen.com</a>
        <a href="https://github.com/TeslenkoOleg/angular-tslen-blog" target="_blank" rel="noopener">GitHub</a>
      </div>
    </div>
  </footer>
"""

POST_PAGE = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>__TITLE__ — T-Slen Blog</title>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
__HEADER__
  <main class="post-page">
    <div class="container post-content">
      <a class="post-back" href="../index.html">&larr; All posts</a>
      <header>
        <h1>__TITLE__</h1>
        <time datetime="__DATE__">__DATE__</time>
      </header>
      <article class="post-body">
__BODY__
      </article>
    </div>
  </main>
__FOOTER__
</body>
</html>
"""

INDEX_PAGE = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>T-Slen Blog</title>
  <meta name="description" content="A technical blog by Oleh Teslenko covering Angular, Node.js, and web development.">
  <meta property="og:title" content="T-Slen Blog">
  <meta property="og:description" content="A technical blog by Oleh Teslenko covering Angular, Node.js, and web development.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://blog.t-slen.com">
  <meta property="og:image" content="https://blog.t-slen.com/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
__HEADER__
  <main class="container post-list">
    <h1>Posts</h1>
__ITEMS__
  </main>
__FOOTER__
</body>
</html>
"""

INDEX_ITEM = """\
    <article class="post-list-item">
      <h2><a href="posts/__SLUG__.html">__TITLE__</a></h2>
      <time datetime="__DATE__">__DATE__</time>
      <p>__EXCERPT__</p>
    </article>
"""


def slugify(title: str) -> str:
    text = html.unescape(title).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def extract_section(source: str, start_marker: str) -> str:
    start = source.find(start_marker)
    if start == -1:
        raise ValueError(f"marker not found: {start_marker}")
    open_tag_end = source.find(">", start) + 1
    depth = 1
    for m in re.finditer(r"<section\b|</section>", source[open_tag_end:]):
        if m.group(0) == "</section>":
            depth -= 1
            if depth == 0:
                return source[open_tag_end : open_tag_end + m.start()]
        else:
            depth += 1
    raise ValueError("unbalanced <section> tags")


def extract_post(raw_html: str) -> tuple[str, str, str]:
    title_match = re.search(r'<h1 class="p-name">(.*?)</h1>', raw_html, re.S)
    if not title_match:
        raise ValueError("title not found")
    title = title_match.group(1).strip()

    subtitle_match = re.search(
        r'<section data-field="subtitle" class="p-summary">(.*?)</section>',
        raw_html,
        re.S,
    )
    subtitle = subtitle_match.group(1).strip() if subtitle_match else ""

    body = extract_section(
        raw_html, '<section data-field="body" class="e-content">'
    ).strip()

    return title, subtitle, body


def strip_script_embeds(body: str) -> str:
    """Replace GitHub Gist script embeds with plain links."""
    def gist_link_replacement(match: re.Match[str]) -> str:
        gist_url = match.group(1)
        return f'<p class="gist-embed-link"><a href="{gist_url}" target="_blank" rel="noopener">View code on GitHub Gist &#8599;</a></p>'

    return re.sub(
        r'<script src="(https://gist\.github\.com/[^"]+)\.js"></script>',
        gist_link_replacement,
        body
    )


LEADING_DIVIDER_RE = re.compile(
    r'^(<section[^>]*>)<div class="section-divider"><hr class="section-divider"></div>'
)
LEADING_TITLE_RE = re.compile(
    r'(<div class="section-inner[^"]*">)\s*'
    r'<h[1-6][^>]*\bclass="[^"]*\bgraf--title\b[^"]*"[^>]*>.*?</h[1-6]>',
    re.S,
)
MIXTAPE_LINK_RE = re.compile(
    r'<a\b[^>]*class="[^"]*\bmixtapeImage\b[^"]*"[^>]*>\s*</a>'
)


def clean_body(body: str) -> str:
    """Remove Medium-specific cruft that doesn't translate to this site.

    - The leading `<div class="section-divider">...</div>` at the very start
      of the body (Medium hides it via CSS for the first section; we don't
      replicate that CSS, so drop the markup instead).
    - The leading in-body title heading (`graf--title`), which duplicates
      the page's own `<h1>`.
    - Empty "mixtape" related-post link cards (`mixtapeImage`), which render
      as invisible, focusable, nameless anchors without Medium's CSS.
    """
    body = LEADING_DIVIDER_RE.sub(r"\1", body, count=1)
    body = LEADING_TITLE_RE.sub(r"\1", body, count=1)
    body = MIXTAPE_LINK_RE.sub("", body)
    return body


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    posts = json.loads((RAW_DIR / "posts.info.json").read_text(encoding="utf-8"))
    posts.sort(key=lambda p: p["date"], reverse=True)

    index_items = []
    for post in posts:
        raw_html = (RAW_DIR / post["fileName"]).read_text(encoding="utf-8")
        title, subtitle, body = extract_post(raw_html)
        body = strip_script_embeds(body)
        body = clean_body(body)
        slug = f"{post['date']}-{slugify(title)}"

        page = (
            POST_PAGE.replace("__HEADER__", HEADER.replace("__HOME__", "../"))
            .replace("__FOOTER__", FOOTER)
            .replace("__TITLE__", title)
            .replace("__DATE__", post["date"])
            .replace("__BODY__", body)
        )
        (OUTPUT_DIR / f"{slug}.html").write_text(page, encoding="utf-8")

        index_items.append(
            INDEX_ITEM.replace("__SLUG__", slug)
            .replace("__TITLE__", title)
            .replace("__DATE__", post["date"])
            .replace("__EXCERPT__", subtitle)
        )

    index_page = (
        INDEX_PAGE.replace("__HEADER__", HEADER.replace("__HOME__", ""))
        .replace("__FOOTER__", FOOTER)
        .replace("__ITEMS__", "".join(index_items))
    )
    (ROOT / "index.html").write_text(index_page, encoding="utf-8")

    print(f"Generated {len(posts)} post pages and index.html")


if __name__ == "__main__":
    main()
