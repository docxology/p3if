# AGENTS.md — `website/templates/docs/`

`index.html`, the documentation-browsing page. It renders Markdown that
`../routes/docs.py` reads from the repository's `docs/` tree at request time, so the
page has no content of its own to update.

- Adding a documentation page does not require a template change; removing or renaming
  one can break navigation built here.
- Nothing renders this template in CI — a change is verified only by starting the
  application and opening the page.

Routes: [`../../routes/docs.py`](../../routes/docs.py).
