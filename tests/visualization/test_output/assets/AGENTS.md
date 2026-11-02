# AGENTS.md — `tests/visualization/test_output/assets/`

The `css/` and `js/` files the visualization tests wrote for their portal pages — the
same asset pair the portal generator emits beside every portal it builds.

- Generated per test run. Rerun the suite to refresh; editing here changes nothing the
  generator would not overwrite.
- No test reads them back: their presence shows the generator wrote assets, not that
  those assets are current or correct.

Portal code: [`../../../../src/p3if/visualization/portals/`](../../../../src/p3if/visualization/portals/).
