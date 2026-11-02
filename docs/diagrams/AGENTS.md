# AGENTS.md — `docs/diagrams/`

Text diagrams, kept as Markdown: `system-architecture.md`, `system-diagrams.md`, and
`process-flows.md`. Every diagram is drawn in Markdown (Mermaid or ASCII) — there are
no image assets in this folder.

- Diagrams are hand-maintained illustrations of the architecture described in
  `../technical/architecture.md` and implemented in `../../src/p3if/`. Nothing
  generates or validates them, so a diagram can be older than the code it describes.
- When the architecture changes, update the diagram and the technical document
  together; a corrected diagram alone still leaves the prose stale.
- No gate reads this folder: no doc build, no link check in CI, no test.

Docs-tree guide: [`../AGENTS.md`](../AGENTS.md); repository rules:
[root guide](../../AGENTS.md).
