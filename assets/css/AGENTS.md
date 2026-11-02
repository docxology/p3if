# AGENTS.md — `assets/css/`

`styles.css`: the portal stylesheet written by `_create_css_file` in
`src/p3if/visualization/portals/portal.py`, beside the portal HTML that references
it.

- A generated copy, not the source of truth. Rerunning the portal writes its own
  `assets/css/styles.css` into that run's output directory; change the generator
  instead of this file.
- Nothing tests, lints, or compares this file with the current generator's output.

Portal code: [`../../src/p3if/visualization/portals/`](../../src/p3if/visualization/portals/).
