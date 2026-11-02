# AGENTS.md — `assets/`

Portal assets: `css/styles.css` and `js/portal.js`. They belong to the generated web
portal, whose code writes both into an `assets/` directory beside the portal HTML it
produces (`src/p3if/visualization/portals/portal.py`).

- Treat these as generated copies, not sources. The same pair appears inside
  generated output directories (for example under `outputs/` and
  `tests/visualization/test_output/`), because the portal writes its assets once per
  output directory.
- Editing these files here changes nothing a rerun would not overwrite: change the
  generator in `src/p3if/visualization/portals/portal.py` and regenerate.
- No test or CI job checks these files, and nothing compares them with what the
  current generator emits.
- Not an inventory: read the listing for the current file set.

Portal code: [`../src/p3if/visualization/portals/`](../src/p3if/visualization/portals/);
repository rules: [root guide](../AGENTS.md).
