# AGENTS.md — `outputs/`

Committed snapshots of visualization runs: one directory per run, named
`p3if_output_<UTC timestamp>` by the output organizer in
`src/p3if/utils/output_organizer.py`, each holding the rendered views under
`visualizations/`.

- Generated, not hand-maintained. Rerunning the pipeline (`scripts/run_all.py
  --viz`, or the visualization orchestrator) writes a new timestamped directory
  instead of refreshing an old one; do not edit rendered HTML in place.
- Nothing in CI builds, refreshes, or checks anything under `outputs/`, and no
  test asserts on these files. They record what particular runs produced, not what
  the current code produces.
- Guides exist at this level and for the runs of 2026-08-04 and 2026-08-20 (as of
  2026-11-02). The four 2026-08-31 runs have no folder guides; an absent guide there
  is not evidence of an empty run.
- This guide is not a manifest. The directory listing is the truth about which runs
  exist and what each holds, and the `README.md` files beside the guides are
  generated listings that can lag behind it.

The rendering code is in [`../src/p3if/visualization/`](../src/p3if/visualization/);
repository rules are in the [root guide](../AGENTS.md).
