# T-Slen technical blog rewrite — design spec

Date: 2026-08-16

## Purpose

Replace the current bare-bones Angular 13 app (unstyled `<ul>` list, raw
`innerHTML` injection, no routing, no per-post URLs) with a modern,
read-only static technical blog, hosted via GitHub Pages at
`blog.t-slen.com`. Visually matches the monochrome black/white system
already built for `t-slen.com` and `tslen-crm`'s actual UI. No
in-app authoring — content stays exactly the existing 33 Medium-exported
posts, shown, not editable.

## Content pipeline

A one-time (rerunnable) Python script, `scripts/generate-posts.py`,
regenerates the static site content from the raw exports:

- Input: `content/raw-posts/posts.info.json` (id, date, title, fileName)
  and `content/raw-posts/*.html` (the 33 Medium export files) — moved
  from their current location at `src/assets/posts/` as part of this
  rewrite.
- For each post: extract `<h1 class="p-name">` (title),
  `<section data-field="subtitle" class="p-summary">` (excerpt), and
  `<section data-field="body" class="e-content">...</section>` (article
  body) from the raw export via regex (the Medium export structure is
  consistent across all 33 files — confirmed by inspection).
- Generate a URL-safe slug from the title (lowercase, ASCII,
  non-alphanumerics → `-`, collapse repeats, trim).
- Write `posts/<slug>.html` per post: the extracted body dropped into
  the shared page template (see below), with the extracted `<h1>` title
  and a `<time>` element for the date.
- Write `index.html`: reverse-chronological list of all posts (title as
  a link to `posts/<slug>.html`, `<time>` date, excerpt), newest first.
- Images are **not** migrated — they stay hotlinked to Medium's CDN
  (`cdn-images-1.medium.com`) exactly as in the original export.
- The script is safe to rerun (overwrites `posts/*.html` and
  `index.html` from `content/raw-posts/` + `posts.info.json`), so
  a future Medium export can be dropped into `content/raw-posts/` and
  regenerated later — but there is no in-app UI to do this.

## Page structure

- **`index.html`** — header (logo, "t-slen.com" link, "GitHub" link),
  then a plain vertical list of all 33 posts (title/link, date,
  excerpt), footer.
- **`posts/<slug>.html`** (33 files) — same header/footer, `<article>`
  with the post title, date, and extracted body content (headings,
  paragraphs, code blocks, images, figures, links, blockquotes).

## Visual design

- Same CSS custom-property token system as `t-slen.com`, but **light by
  default** (`:root` holds the light palette) with a
  `prefers-color-scheme: dark` override for dark mode — the inverse of
  how `t-slen.com` is set up (dark by default, light override).
- Same tokens/values: `--color-bg`, `--color-bg-alt`, `--color-text`,
  `--color-text-muted`, `--color-border`, `--color-btn-bg`,
  `--color-btn-bg-hover`, `--color-btn-text`, `--radius`, `--font-sans`.
- Same header pattern: sticky, blurred background, T-SLEN logo (same
  `logo.png` asset, same dark-mode invert filter), nav links styled the
  same as `t-slen.com`'s `.primary-nav a:not(.btn)`. No hamburger/mobile
  toggle — only two nav links (`t-slen.com`, `GitHub`), short enough to
  stay on one line at any width.
- List page (`index.html`): plain vertical list, no card borders,
  generous vertical spacing between entries, title/date/excerpt per
  entry — matches the "simple reverse-chronological list" approach.
- Post page (`posts/<slug>.html`): reading column capped at ~680px
  (narrower than the site's general 1200px container, for readability),
  distinct typographic rules for the article body: `h2`/`h3` sizing,
  `p` line-height, `blockquote` with a left border, `pre`/`code` in a
  monospace stack with a subtle background and `overflow-x: auto` for
  long lines, `figure`/`figcaption` styling, `img { max-width: 100% }`.
  All driven by the same color tokens so it stays theme-aware.

## Technical structure & deployment

Files at repo root (same repo, `TeslenkoOleg/angular-tslen-blog`,
Angular app files removed):

- `index.html`, `styles.css` — shared shell + list page
- `posts/<slug>.html` × 33 — generated post pages
- `scripts/generate-posts.py` — the generator described above
- `content/raw-posts/posts.info.json`, `content/raw-posts/*.html` — the
  33 raw Medium exports (generator input, kept for future reruns)
- `logo.png`, `favicon.svg`, `og-image.png` — same pattern as
  `t-slen.com` (logo copied from the same source; favicon/OG image
  regenerated with this site's title)
- `CNAME` — contains `blog.t-slen.com`

Deployment: GitHub Pages switches from the current `gh-pages` branch +
`angular-cli-ghpages` build step to serving `main` branch root directly
— same simplification as `t-slen.com`, no build step at all. DNS fix
for `blog.t-slen.com` (Cloudflare CNAME → `teslenkooleg.github.io`,
DNS-only) is tracked separately and done whenever the user is ready —
not part of this rewrite's implementation tasks.

## Testing

No automated tests (static content site). Manual QA before merging:
verify all 33 `posts.info.json` entries produced a linked, non-empty
`posts/<slug>.html`; spot-check at least three posts (one with code
blocks, one with many images, one plain-text) for clean extraction (no
leftover Medium-specific wrapper markup, no broken tags); responsive,
keyboard-focus, and color-contrast checks same as done for `t-slen.com`.
