# Modern Static Blog Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Angular 13 app in `angular-tslen-blog` with a modern, read-only static technical blog (list page + 33 individually-URLed post pages), visually matching the monochrome design system already built for `t-slen.com`, deployable to GitHub Pages with no build step.

**Architecture:** A one-time Python generator script reads the 33 raw Medium-export HTML files plus their metadata, extracts each post's title/excerpt/body via a verified balanced-tag extraction algorithm, and writes plain static `posts/<slug>.html` files plus `index.html`. No framework, no runtime JS required for content.

**Tech Stack:** HTML5, CSS3 (custom properties, matching `t-slen.com`'s token system but light-by-default), Python 3 (stdlib only) for the one-time generator, GitHub Pages.

**Spec:** `/Users/olegteslenko/Desktop/angular-tslen-blog/docs/superpowers/specs/2026-08-16-modern-static-blog-design.md`

## Global Constraints

- No build step, no framework, no JS required for content to render (spec: "Content pipeline", "Technical structure").
- `:root` holds the **light** palette by default; `@media (prefers-color-scheme: dark)` holds the dark override — the inverse of `t-slen.com` (spec: "Visual design").
- Images stay hotlinked to Medium's CDN (`cdn-images-1.medium.com`) — no image migration (spec: "Content pipeline").
- No in-app authoring UI; the generator script is a one-time/rerunnable content-build step, not part of the served site (spec: "Content pipeline").
- Post reading column capped at ~680px; site-wide container stays 1200px like `t-slen.com` (spec: "Visual design").
- Repo stays `TeslenkoOleg/angular-tslen-blog`; deploy target is `blog.t-slen.com` via `CNAME` (spec: "Technical structure & deployment").
- DNS fix for `blog.t-slen.com` is explicitly **out of scope** for this plan (spec: "Technical structure & deployment").

---

## File Structure

- `styles.css` — single stylesheet: design tokens (light default / dark override), shared header/footer, post-list styles, post-page/article typography.
- `scripts/generate-posts.py` — the one-time/rerunnable generator: extraction functions + page templates + `main()`. Reads `content/raw-posts/`, writes `posts/*.html` and `index.html`.
- `content/raw-posts/posts.info.json`, `content/raw-posts/*.html` (33 files) — raw Medium exports, relocated from `src/assets/`. Generator input only; not linked from the site.
- `posts/<slug>.html` (33 generated files) — one per post, `<slug>` = `<date>-<title-slug>` (date prefix guarantees uniqueness even for the 4 posts that share the literal title "Best Design Principles in Angular").
- `index.html` (generated) — post list.
- `logo.png`, `favicon.svg`, `og-image.png`, `CNAME` — static assets, same pattern as `t-slen.com`.
- Removed: `src/`, `angular.json`, `package.json`, `package-lock.json`, `karma.conf.js`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.spec.json`, `.browserslistrc`, `.editorconfig`, `generatePostsInfo.js` (superseded by `scripts/generate-posts.py`).

## Task 1: Repo cleanup — remove Angular app, relocate raw content

**Files:**
- Delete: `src/`, `angular.json`, `package.json`, `package-lock.json`, `karma.conf.js`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.spec.json`, `.browserslistrc`, `.editorconfig`, `generatePostsInfo.js`
- Create: `content/raw-posts/posts.info.json` (moved from `src/assets/posts.info.json`)
- Create: `content/raw-posts/*.html` × 33 (moved from `src/assets/posts/*.html`)
- Modify: `.gitignore`
- Modify: `README.md`

**Interfaces:**
- Produces: `content/raw-posts/posts.info.json` (array of `{id, date, title, fileName}`) and `content/raw-posts/<fileName>` for each entry — consumed by Task 3's generator script.

- [ ] **Step 1: Move the raw content into its new home**

```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
mkdir -p content/raw-posts
git mv src/assets/posts.info.json content/raw-posts/posts.info.json
git mv src/assets/posts/*.html content/raw-posts/
```

- [ ] **Step 2: Remove the Angular app and its tooling files**

```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
git rm -r src angular.json package.json package-lock.json karma.conf.js tsconfig.json tsconfig.app.json tsconfig.spec.json .browserslistrc .editorconfig generatePostsInfo.js
```

- [ ] **Step 3: Verify nothing Angular-related remains**

Run:
```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
find . -maxdepth 1 -not -path '.' -not -path './.git' -not -path './docs' -not -path './content' | sort
ls content/raw-posts | wc -l
```
Expected: the listing shows only `CNAME` and `README.md` (plus whatever this task creates next); `content/raw-posts` lists 34 files (33 `.html` + `posts.info.json`).

- [ ] **Step 4: Replace `.gitignore` contents**

```
.DS_Store
```

- [ ] **Step 5: Rewrite `README.md`**

```markdown
# T-Slen Blog

A static technical blog mirroring [my Medium posts](https://medium.com/@teslenkooleg2017), hosted at [blog.t-slen.com](https://blog.t-slen.com).

Plain HTML/CSS, no framework, no build step. Content lives as generated
static files in `posts/` and `index.html`.

## Regenerating post pages

Post pages are generated from the raw Medium exports in
`content/raw-posts/` by a one-time script. Re-run it after adding new
raw exports to `content/raw-posts/` (and an entry to
`content/raw-posts/posts.info.json`):

```bash
python3 scripts/generate-posts.py
```

There is no in-app way to add posts — this is a read-only site.
```

- [ ] **Step 6: Commit**

```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
git add content .gitignore README.md
git commit -m "chore: remove Angular app, relocate raw post content"
```

## Task 2: Stylesheet

**Files:**
- Create: `styles.css`

**Interfaces:**
- Produces: CSS custom properties (`--color-bg`, `--color-bg-alt`, `--color-text`, `--color-text-muted`, `--color-border`, `--color-btn-bg`, `--color-btn-bg-hover`, `--color-btn-text`, `--radius`, `--container-width`, `--font-sans`, `--font-mono`), and classes `.container`, `.site-header`, `.header-inner`, `.logo`, `.logo-img`, `.primary-nav`, `.site-footer`, `.footer-inner`, `.footer-links`, `.post-list`, `.post-list-item`, `.post-page`, `.post-content`, `.post-back`, `.post-body` — consumed by Task 3's page templates.

- [ ] **Step 1: Write `styles.css`**

```css
:root {
  --color-bg: #ffffff;
  --color-bg-alt: #f5f5f5;
  --color-text: #212121;
  --color-text-muted: #6b6b6b;
  --color-border: #e2e2e2;
  --color-btn-bg: #212121;
  --color-btn-bg-hover: #050505;
  --color-btn-text: #ffffff;
  --radius: 10px;
  --container-width: 1200px;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0a0a0a;
    --color-bg-alt: #151515;
    --color-text: #f2f2f2;
    --color-text-muted: #9c9c9c;
    --color-border: #2a2a2a;
    --color-btn-bg: #f2f2f2;
    --color-btn-bg-hover: #d6d6d6;
    --color-btn-text: #111111;
  }
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font-sans);
  background: var(--color-bg);
  color: var(--color-text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}
img, svg { max-width: 100%; display: block; }
a { color: inherit; text-decoration: none; }
h1, h2, h3, p { margin: 0; }
.container { max-width: var(--container-width); margin: 0 auto; padding: 0 1.5rem; }

.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
}
@media (prefers-color-scheme: dark) {
  .site-header { background: rgba(10, 10, 10, 0.85); }
}
.header-inner { display: flex; align-items: center; justify-content: space-between; height: 64px; }
.logo { display: flex; align-items: center; }
.logo-img { height: 32px; width: auto; }
@media (prefers-color-scheme: dark) {
  .logo-img { filter: invert(1) brightness(2); }
}
.primary-nav { display: flex; align-items: center; gap: 1.75rem; }
.primary-nav a { color: var(--color-text-muted); font-weight: 500; font-size: 0.95rem; }
.primary-nav a:hover { color: var(--color-text); }

.site-footer { border-top: 1px solid var(--color-border); padding: 2rem 0; }
.footer-inner { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; color: var(--color-text-muted); font-size: 0.9rem; }
.footer-links { display: flex; gap: 1.25rem; }
.footer-links a:hover { color: var(--color-text); }

.post-list { padding: 3rem 0 5rem; }
.post-list h1 { font-size: 2rem; margin-bottom: 2.5rem; }
.post-list-item { padding: 1.5rem 0; border-bottom: 1px solid var(--color-border); }
.post-list-item:last-child { border-bottom: none; }
.post-list-item h2 { font-size: 1.25rem; margin: 0 0 0.35rem; font-weight: 600; }
.post-list-item h2 a:hover { color: var(--color-text-muted); }
.post-list-item time { color: var(--color-text-muted); font-size: 0.85rem; }
.post-list-item p { color: var(--color-text-muted); margin-top: 0.5rem; }

.post-page { padding: 3rem 0 5rem; }
.post-content { max-width: 680px; margin: 0 auto; }
.post-back { display: inline-block; margin-bottom: 2rem; color: var(--color-text-muted); font-size: 0.9rem; }
.post-back:hover { color: var(--color-text); }
.post-content > header { margin-bottom: 2.5rem; }
.post-content > header h1 { font-size: 2.25rem; line-height: 1.2; margin-bottom: 0.75rem; }
.post-content > header time { color: var(--color-text-muted); font-size: 0.9rem; }

.post-body h2 { font-size: 1.5rem; margin: 2.5rem 0 1rem; }
.post-body h3 { font-size: 1.25rem; margin: 2rem 0 0.85rem; }
.post-body h4 { font-size: 1.05rem; margin: 1.75rem 0 0.75rem; }
.post-body p { margin: 0 0 1.25rem; }
.post-body ul, .post-body ol { margin: 0 0 1.25rem; padding-left: 1.5rem; }
.post-body a { color: var(--color-text); text-decoration: underline; text-underline-offset: 2px; }
.post-body blockquote { margin: 1.5rem 0; padding-left: 1.25rem; border-left: 3px solid var(--color-border); color: var(--color-text-muted); }
.post-body pre { background: var(--color-bg-alt); border: 1px solid var(--color-border); border-radius: var(--radius); padding: 1rem; overflow-x: auto; margin: 0 0 1.25rem; }
.post-body code { font-family: var(--font-mono); font-size: 0.9em; }
.post-body p code { background: var(--color-bg-alt); padding: 0.15em 0.4em; border-radius: 4px; }
.post-body figure { margin: 1.75rem 0; }
.post-body figcaption { color: var(--color-text-muted); font-size: 0.85rem; margin-top: 0.5rem; text-align: center; }
.post-body img { border-radius: var(--radius); }
```

- [ ] **Step 2: Verify the file is syntactically sane**

Run:
```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
python3 -c "
content = open('styles.css').read()
assert content.count('{') == content.count('}'), 'brace mismatch'
print('braces balanced:', content.count('{'))
"
```
Expected: prints a matching brace count with no assertion error.

- [ ] **Step 3: Commit**

```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
git add styles.css
git commit -m "feat: add stylesheet with light-default token system"
```

## Task 3: Post generator script

**Files:**
- Create: `scripts/generate-posts.py`

**Interfaces:**
- Consumes: `content/raw-posts/posts.info.json` and `content/raw-posts/<fileName>` from Task 1; CSS classes from Task 2 (`.site-header`, `.primary-nav`, `.post-list`, `.post-list-item`, `.post-page`, `.post-content`, `.post-back`, `.post-body`, `.site-footer`, `.footer-links`).
- Produces: `posts/<slug>.html` (one per entry in `posts.info.json`) and `index.html` at repo root.

- [ ] **Step 1: Write `scripts/generate-posts.py`**

```python
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


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    posts = json.loads((RAW_DIR / "posts.info.json").read_text(encoding="utf-8"))
    posts.sort(key=lambda p: p["date"], reverse=True)

    index_items = []
    for post in posts:
        raw_html = (RAW_DIR / post["fileName"]).read_text(encoding="utf-8")
        title, subtitle, body = extract_post(raw_html)
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
```

- [ ] **Step 2: Run the generator**

Run:
```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
python3 scripts/generate-posts.py
```
Expected: `Generated 33 post pages and index.html`

- [ ] **Step 3: Verify all 33 posts generated with no leftover Medium wrapper markup**

Run:
```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
ls posts | wc -l
grep -L 'class="post-body"' posts/*.html
grep -l '<footer><p>By' posts/*.html
grep -c '<article class="post-list-item">' index.html
```
Expected: `33`; both `grep -L`/`grep -l` commands print nothing (every post has the new wrapper, none still contain the original Medium `<footer><p>By ...` byline); the last command prints `33`.

- [ ] **Step 4: Spot-check three specific posts for clean extraction**

Run:
```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
grep -c '<pre' posts/2023-04-24-the-unknown-angular-pipes-you-need-to-start-using.html
grep -c '<img' posts/2024-04-09-how-to-build-responsive-layouts-using-angular-react-or-vue.html
grep -c 'best-design-principles-in-angular' <(ls posts)
```
Expected: first command prints a number `>= 1` (code blocks preserved); second prints a number `>= 1` (images preserved); third prints `4` (all four same-titled posts got unique date-prefixed slugs, confirming the duplicate-title collision is resolved).

If any filename in this step doesn't match what the generator produced, run `ls posts | grep <keyword>` to find the actual generated slug and adjust the check — the exact slug depends on `slugify()`'s output for that title.

- [ ] **Step 5: Commit**

```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
git add scripts/generate-posts.py posts index.html
git commit -m "feat: add post generator and generate all post pages"
```

## Task 4: Static assets — logo, favicon, OG image, CNAME

**Files:**
- Create: `logo.png` (copied from `t-slen.com`)
- Create: `favicon.svg`
- Create: `og-image.png`
- Create: `CNAME`

**Interfaces:**
- Consumes: `<link rel="icon" href="favicon.svg">` / `<img src="logo.png">` references already emitted by Task 3's templates (root-level pages reference `favicon.svg`/`logo.png` directly; post pages reference `../favicon.svg`/`../logo.png`).

- [ ] **Step 1: Copy the logo from the sibling landing page repo**

```bash
cp /Users/olegteslenko/Desktop/t-slen.com/logo.png /Users/olegteslenko/Desktop/angular-tslen-blog/logo.png
```

- [ ] **Step 2: Write `favicon.svg`**

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="8" fill="#212121"/>
  <text x="16" y="22" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#ffffff" text-anchor="middle">T</text>
</svg>
```

- [ ] **Step 3: Generate `og-image.png`**

Run:
```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
python3 -c "import PIL" 2>/dev/null || pip3 install --quiet Pillow
python3 - <<'EOF'
from PIL import Image, ImageDraw, ImageFont

img = Image.new("RGB", (1200, 630), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
draw.ellipse([-150, -150, 350, 350], fill=(245, 245, 245))

try:
    font_big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
    font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
except OSError:
    font_big = ImageFont.load_default()
    font_small = ImageFont.load_default()

draw.text((80, 250), "T-Slen Blog", font=font_big, fill=(33, 33, 33))
draw.text((80, 340), "Technical writing on Angular, Node.js, and the web", font=font_small, fill=(107, 107, 107))
img.save("og-image.png")
EOF
```

- [ ] **Step 4: Write `CNAME`**

```
blog.t-slen.com
```

- [ ] **Step 5: Verify all four files exist**

Run:
```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
ls -la logo.png favicon.svg og-image.png CNAME
file og-image.png
```
Expected: all four listed with non-zero size; `file og-image.png` reports `PNG image data, 1200 x 630`.

- [ ] **Step 6: Wire the OG image and description into `index.html`'s `<head>`**

The `<head>` currently has a `<title>` and one `<meta name="description">` from Task 3's `INDEX_PAGE` template but no Open Graph tags. Add them directly to the generator template so they survive re-runs.

In `scripts/generate-posts.py`, update `INDEX_PAGE`'s `<head>` block from:
```python
  <meta name="description" content="A technical blog by Oleh Teslenko covering Angular, Node.js, and web development.">
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
```
to:
```python
  <meta name="description" content="A technical blog by Oleh Teslenko covering Angular, Node.js, and web development.">
  <meta property="og:title" content="T-Slen Blog">
  <meta property="og:description" content="A technical blog by Oleh Teslenko covering Angular, Node.js, and web development.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://blog.t-slen.com">
  <meta property="og:image" content="https://blog.t-slen.com/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
```

Then re-run the generator so `index.html` picks up the change:
```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
python3 scripts/generate-posts.py
grep -c 'og:image' index.html
```
Expected: `1`.

- [ ] **Step 7: Commit**

```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
git add logo.png favicon.svg og-image.png CNAME scripts/generate-posts.py index.html
git commit -m "feat: add static assets and OG meta tags"
```

## Task 5: Full-page QA pass

**Files:** none expected (fix-only if a check below fails).

**Interfaces:**
- Consumes: the complete site from Tasks 1–4.

- [ ] **Step 1: Serve the site locally and confirm key pages return 200**

Run:
```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
python3 -m http.server 8010 &>/tmp/tslen-blog-http.log &
sleep 1
for f in / styles.css logo.png favicon.svg og-image.png posts/2023-04-24-the-unknown-angular-pipes-you-need-to-start-using.html; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8010/$f")
  echo "$f -> $code"
done
```
Expected: every line ends `-> 200`. (If the specific post filename doesn't exist, run `ls posts | head -1` and substitute an actual generated filename.)

- [ ] **Step 2: Manual visual + accessibility check in the browser**

With the server still running, open `http://localhost:8010/` in a browser:
- Confirm the list shows all 33 posts, newest first, each with a title link, date, and excerpt.
- Click into at least three posts (one with code blocks, one with several images, one plain-text) and confirm: the logo/nav header renders, code blocks are readable in a monospace block with a scrollable container for long lines, images load from Medium's CDN, the "&larr; All posts" link returns to the list.
- Resize from mobile (~375px) to desktop (~1440px) width; confirm no horizontal scrollbar and the reading column stays comfortably narrow on a post page.
- Toggle macOS system appearance between light and dark; confirm the palette switches automatically (light by default) and the logo inverts to white in dark mode.
- Tab through the list page with the keyboard; confirm every link receives a visible focus outline.

Stop the server: `kill %1`.

- [ ] **Step 3: Check the browser console is clean on both the list page and a post page**

With dev tools open while browsing both page types, confirm zero console errors.

- [ ] **Step 4: Commit any fixes found during QA (skip if none needed)**

```bash
cd /Users/olegteslenko/Desktop/angular-tslen-blog
git add -A
git commit -m "fix: address QA findings from full-page pass"
```

## Task 6: GitHub Pages configuration (manual — after merge)

**Files:** none (repo/infra operations only).

**Interfaces:**
- Consumes: the finished branch from Tasks 1–5, merged to `main`.

- [ ] **Step 1 (manual — user action): Switch the Pages source**

Go to `github.com/TeslenkoOleg/angular-tslen-blog/settings/pages`:
- Under "Build and deployment" → "Source", switch from the current `gh-pages` branch to **Deploy from a branch**, branch `main`, folder `/ (root)`. Save.
- The "Custom domain" field should already show `blog.t-slen.com` (from the `CNAME` file) — leave it as-is.

- [ ] **Step 2: Verify the GitHub Pages build succeeded**

Run:
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://teslenkooleg.github.io/angular-tslen-blog/
```
Expected: `200` (confirms the Pages build works on the `github.io` URL independent of `blog.t-slen.com`'s separately-tracked DNS fix).

- [ ] **Step 3 (optional, manual — user action): Retire the old `gh-pages` branch**

Once `main` is confirmed live, the `gh-pages` branch and the `angular-cli-ghpages`-based deploy flow are no longer used. Delete it whenever convenient — not required for this rewrite to be complete.
