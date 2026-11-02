# AGENTS.md — `website/templates/visualizations/`

Visualization pages: `index.html` (what is available), `show.html` (one view), and
`generate.html` (the form that starts a generation through `../routes/viz_generate.py`),
with the per-type pages in `type/`.

- The generator form is the only write path in the portal: it starts a run whose output
  lands in a session directory under `../../outputs/`. Treat it as an operator action,
  not a browsing feature.
- No test renders these pages, and no browser test exists; a template change is
  verified by running the application.

Per-type templates: [`type/AGENTS.md`](type/AGENTS.md); routes:
[`../../routes/viz_generate.py`](../../routes/viz_generate.py).
