# Review Log — Agent-Ergonomics Deep Pass (2026-08-31)

Fleet lane: p3if. Doctrine: /Users/4d/HermesWorkspace/agent-erg-fleet-20260831/SHARED_FRAME.md.

## Phase 0 — Preflight

- Branch `main` confirmed (matches brief). Remote `origin` = github.com/docxology/p3if.git. `git fetch origin` run.
- State: `main...origin/main [ahead 1]` before this pass. Dirty files at dispatch: 277 — all generated
  visualization artifacts under `outputs/` and `tests/visualization/test_output/`. Treated as pre-existing;
  none staged by this pass.
- Inventory: entry docs README.md / AGENTS.md / CLAUDE.md / PAI.md; TODO.md exists (preserved conventions);
  CHANGELOG.md; docs/ tree with own AGENTS.md; scripts/ with README and AGENTS; manuscript status at
  `docs/manuscript/MANUSCRIPT_STATUS.md`; no CI/Makefile; gates = pytest via `uv run --extra dev`.

## Phase 1 — Cold-start audit

Scored as a cold agent reading only entry docs:

- (a) Determine current project status — PASS (with friction). TODO.md + CHANGELOG "Unreleased" section
  answer "what state" and are fresh (v2.5.0 completed). But the README never pointed to TODO.md, so status
  discovery required reading past the entry doc.
- (b) Find what to do next — FAIL before changes. README had no backlog pointer; TODO.md was found only
  via the fleet brief. Fixed: README now has a "Project Status and Next Actions" section.
- (c) Find how to run primary verification — PASS. CLAUDE.md and README both give `pytest tests/ -v` and
  `pip install -e ".[dev,web]"`. Verified live: the dev extra (`pytest>=7.0`) is real in pyproject.toml
  lines 38-41; `.venv` existed but lacked pytest until `uv sync --extra dev --extra web` was run this
  session. Full-suite execution deferred (see Phase 4 note).

Sweep findings (all link-checked with a script across root *.md + docs/*.md + docs/*/*.md):

1. MINOR — Broken link `docs/P3IF_IMPROVEMENTS_SUMMARY.md` in CONTRIBUTING.md:44 (file does not exist).
   Fixed: now points to TODO.md (the real roadmap).
2. MINOR — Wrong repo URL `https://github.com/p3if/p3if/issues` in CONTRIBUTING.md:44 (actual remote is
   docxology/p3if, verified via `git remote -v`). Fixed.
3. MINOR — README lacked backlog/status pointer (doctrine orientation ladder step 3). Fixed with new
   section; verification commands embedded.
4. MEDIUM — Transient QA report `docs/DOCUMENTATION_IMPROVEMENTS_SUMMARY.md` (dated September 23, 2025,
   one-off audit snapshot) was presented in docs/README.md "Project Reports and Validation" as if current.
   Fixed: docs/README.md now labels it as a historical one-time audit record (2025-09-23), not current
   status; canonical current-status surfaces are TODO.md and CHANGELOG.md (links, not copies).
5. MEDIUM — Status/backlog fact-class had no canonical-home signpost: README now declares TODO.md as the
   single backlog authority and CHANGELOG.md as the single release-history authority.
6. MINOR — README "Python Usage" example writes `output/cube.html` while the tree's real output dir is
   `outputs/`; example still works (relative to CWD) — left as-is, noted here rather than churned.
7. DEFERRED — Full pytest suite not run this session: `uv sync --extra dev --extra web` on the slow
   external drive exceeded the session timeout window. Command a human would run:
   `uv run --extra dev pytest tests/ -q`. The dev-extra install was verified as the correct prerequisite
   (pyproject `dev` extra contains pytest>=7.0); `.venv/bin/python` exists. Verification path documented
   in README instead of an unverified pass/fail claim.
8. MINOR — No fast pre-push gate declared anywhere; noted in report rather than invented.

## Phase 2 — TODO.md scoping

All findings requiring doc change were fixed immediately (items 1-5); the only deferred item (full
test-suite run) is a session constraint, not a repo defect, so it stays in this log and the report rather
than TODO.md. TODO.md conventions preserved; verified its [x] items correspond to CHANGELOG Unreleased
entries (A1/Q13/Q14/Q10/A2/M1/M2/M3) — no stale backlog entries found.

## Phase 3 — Implementation record

- README.md: added "Project Status and Next Actions" (orientation ladder), backlog/changelog links with
  verification commands, current-state line marked "as of 2026-08-31".
- CONTRIBUTING.md: fixed dead roadmap link -> TODO.md; fixed wrong GitHub org URL.
- docs/README.md: relabeled DOCUMENTATION_IMPROVEMENTS_SUMMARY.md as historical record (dated),
  pointing current status to TODO.md/CHANGELOG.md.

## Phase 4 — Verify and close

- Link re-check: re-ran the link script; 0 broken links among touched docs.
- TODO.md: unchanged (all items already [x]; conventions preserved).
- Gate: no declared fast gate; `pytest tests/` deferred per item 7 (documented, not fabricated).
- Commits: see git log; path-scoped adds only (README.md, CONTRIBUTING.md, docs/README.md, this log).
- Push: to origin/main per brief.
