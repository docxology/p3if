# AGENTS.md — `docs/visualization/`

The visualization documentation: `user_guide.md` and `domain_visualizations.md` for
what the views show, `3d_cube_visualization.md` for the interactive cube, and
`technical_documentation.md` for how the rendering layer is put together.

- The rendering code is authoritative: [`../../src/p3if/visualization/`](../../src/p3if/visualization/).
  No test or build checks these documents against it, so treat type lists and options
  here as descriptions to verify, not as an interface reference.
- Committed images under `../../visualizations/` and `../../outputs/` are snapshots of
  particular runs — they illustrate the documents but prove nothing about what the
  current code renders.
- Nothing is generated here; the folder holds Markdown only.

Visualization package guide: [`../../src/p3if/visualization/AGENTS.md`](../../src/p3if/visualization/AGENTS.md).
