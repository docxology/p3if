# AGENTS.md — `website/static/css/`

`styles.css`, the portal's hand-maintained stylesheet, served directly by Flask —
no preprocessor, bundler, or minification step.

- Editing it changes the running site; nothing regenerates or overwrites it.
- It is unrelated to the generated `styles.css` files under the repository's `assets/`
  and inside run output directories, which the portal generator writes for standalone
  portals. Do not copy one over the other.
- No test or linter reads it.

Application guide: [`../AGENTS.md`](../AGENTS.md).
