# AGENTS.md — `website/`

The Flask web portal: `app.py` builds the application with `static_folder="static"`,
`run.py` and `run_stable.py` start it, and `routes/`, `static/`, and `templates/`
carry the rest.

- Run it with `python website/run.py`; there is no build step, bundler, or asset
  pipeline — templates are Jinja2 and the CSS/JS are served as committed.
- The portal is a view over repository content: it reads documentation from `../docs/`
  and domain JSON from `../data/domains/` at request time. Those files change the site
  without anything in this folder changing.
- Tests: `tests/integration/test_website_routes.py` imports this application and
  exercises routes in-process. No browser test exists and CI never starts the server,
  so a green suite is not a rendering or interaction check.

Sub-guides: [`routes/AGENTS.md`](routes/AGENTS.md), [`static/AGENTS.md`](static/AGENTS.md),
[`templates/AGENTS.md`](templates/AGENTS.md); repository rules:
[root guide](../AGENTS.md).
