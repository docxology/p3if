# AGENTS.md — `tests/integration/`

Cross-boundary tests: the core integration path, the HTTP API, and the website routes.
The point of this folder is to fail when two packages disagree even though each passes
alone.

- `test_website_routes.py` imports the Flask application from `../../website/`, so a
  route or template change that breaks request handling should fail here.
- Run with `pytest tests/integration -v`. Nothing here starts a real server or drives
  a browser: passing tests are not end-to-end confirmation of the running site.

Web application: [`../../website/AGENTS.md`](../../website/AGENTS.md); repository
rules: [root guide](../../AGENTS.md).
