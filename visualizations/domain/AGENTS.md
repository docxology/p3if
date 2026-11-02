# AGENTS.md — `visualizations/domain/`

Domain-level static plots from one visualization run, committed as a snapshot: a
domain network, a pattern distribution, and the three similarity matrices. Rendered
by `src/p3if/visualization/static/`.

- Generated output. Regenerate rather than edit: rerunning the generator writes into
  a timestamped session directory under `outputs/`, so a refresh reaches this folder
  only when an output directory is passed explicitly.
- No CI job or test reads these PNGs. A committed plot records one render; it is not
  evidence that the current code produces the same image.
- Listing first: this guide does not name files, and the folder is not a manifest.

Static rendering code: [`../../src/p3if/visualization/static/`](../../src/p3if/visualization/static/).
