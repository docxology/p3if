# AGENTS.md — `website/templates/`

Jinja2 templates: `base.html` (the layout pages extend), `index.html`, `about.html`,
and page groups in `docs/`, `domains/`, and `visualizations/`.

- Template names are the contract with `../routes/`: a `render_template(...)` call that
  names a missing file fails at request time. No test renders every page, and CI never
  starts the server, so a missing template can survive the gate.
- Keep structure in `base.html` and extend it; the subfolders are organised per
  resource (list, detail, generator) rather than per route module.
- Hand-maintained HTML — nothing here is generated.

Sub-guides: [`docs/AGENTS.md`](docs/AGENTS.md), [`domains/AGENTS.md`](domains/AGENTS.md),
[`visualizations/AGENTS.md`](visualizations/AGENTS.md); application guide:
[`../AGENTS.md`](../AGENTS.md).
