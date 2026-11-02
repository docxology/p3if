# AGENTS.md — `docs/api/`

The API reference: [`README.md`](README.md) describes the HTTP surface the web portal
exposes — endpoints, headers, and a hand-written "Current Implementation Status".

- The routes are the truth. `website/routes/api/` implements them, and no test,
  schema check, or build compares those routes with this document, so drift is
  possible and this guide cannot tell you which side is stale.
- The document's status section is dated and manual; read it as a claim about when it
  was written, not as current state.
- There is nothing to run here and nothing generated: a change to the API belongs in
  the code first, with the document updated beside it.

Route code: [`../../website/routes/api/`](../../website/routes/api/); the docs-tree
guide is [`../AGENTS.md`](../AGENTS.md).
