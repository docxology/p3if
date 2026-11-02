# AGENTS.md — `website/static/`

Static assets Flask serves from `static_folder="static"`: `css/`, `js/`, and `img/`.
No build step produces them — editing a file here changes the running site directly.

- These are hand-maintained site assets. They are not the generated `assets/` copies
  at the repository root or inside run folders, which the portal generator writes once
  per output directory.
- Nothing tests, lints, or minifies these files: a wrong path or a syntax error shows
  up only in a browser.
- The three images under `img/` are zero-byte placeholders (verified 2026-11-02), so
  they render as broken images; they are not screenshots.

Sub-guides: [`css/AGENTS.md`](css/AGENTS.md), [`js/AGENTS.md`](js/AGENTS.md),
[`img/AGENTS.md`](img/AGENTS.md); application guide: [`../AGENTS.md`](../AGENTS.md).
