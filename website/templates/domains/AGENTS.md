# AGENTS.md — `website/templates/domains/`

Domain pages: `index.html` (the domain list), `show.html` (one domain), and
`patterns.html` (its patterns). `../routes/domains.py` supplies the data, read from
`../../data/domains/` at request time.

- The templates assume the shape of the domain JSON described in
  `../../data/README.md`; a field renamed there shows up as an empty page or a broken
  loop here, not as a test failure.
- No test renders these pages; verify in a browser after changing them.

Routes: [`../../routes/domains.py`](../../routes/domains.py); format contract:
[`../../../data/README.md`](../../../data/README.md).
