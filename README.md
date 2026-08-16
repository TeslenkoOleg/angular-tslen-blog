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
