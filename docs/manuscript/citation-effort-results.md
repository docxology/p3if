# Exact citation accuracy and model review effort

Four fresh Codex sessions reviewed 16 new ScienceResearch and MathEducation revision pairs in two balanced periods. Each revision appeared once per workflow at the same position in different sessions. The inputs, answer key, measures, and packet SHA-256 were publicly committed before any review. [Public preregistration](https://github.com/docxology/p3if/commit/6f6bb684c40e1526afef923f3c2039272ae3d210) · [Protocol](citation-effort-preregistration.md) · [Session metadata](citation-effort/session-metadata.json)

| Workflow or domain | Exact sides | Complete cases | Measured effort cases | Median evidence operations | Median elapsed time |
| --- | ---: | ---: | ---: | ---: | ---: |
| P3IF audit and transition with source navigation | 72/72 | 16/16 | 16/16 | 8 | 9.9 s |
| Type-sensitive stable-ID diff | 72/72 | 16/16 | 16/16 | 10 | 12.8 s |
| ScienceResearch, P3IF | 36/36 | 8/8 | 8/8 | 7 | 8.9 s |
| ScienceResearch, stable-ID diff | 36/36 | 8/8 | 8/8 | 10.5 | 13.6 s |
| MathEducation, P3IF | 36/36 | 8/8 | 8/8 | 8 | 10.9 s |
| MathEducation, stable-ID diff | 36/36 | 8/8 | 8/8 | 10 | 12.7 s |

The matched accuracy counts were 72 sides correct in both workflows, 0 correct only with P3IF, 0 correct only with stable-ID diff, and 0 correct in neither. P3IF verified 62/62 present sides and 10/10 absent sides. Stable-ID diff verified 62/62 present sides and 10/10 absent sides. [Full side-level score and error fields](citation-effort/score.json)

Across 16 matched cases with usable effort logs, the median within-case difference was -2 evidence operations and -1.6 s of measured elapsed time, taking P3IF minus stable-ID diff. The median of paired differences has a different interpretation from the difference between the two workflow medians. The log counts each instrumented open, find, search, or citation extraction from the first evidence operation through submission. [Independent replay](citation-effort/score-check.json)

Both workflows had the same source bytes, case questions, lookups and reader. The P3IF report also exposed navigation pointers to changed declarations. The packet check verified all 172 delivery files. The source check covered 19 moved pointers, seven CRLF transports, and 49 present sides after multibyte text. Report structures and sizes remained distinguishable. The four fresh sessions did not receive assignment labels, other session packets, or the reference key. The exact deployed model identifier was unavailable. [Packet inventory](citation-effort/packet-manifest.json) · [Packet check](citation-effort/packet-check.json) · [Source check](citation-effort/source-check.json)

All 32 case traces were usable. Each workflow made 62 citation extractions. The P3IF workflow made 30 finds and the stable-ID diff workflow made 68. P3IF used fewer operations in ten matched cases and tied in six, including both no-change controls. One session reopened a report after a display-filter error, and both opens count. Another recovered from a shell wrapper failure between a submitted case and the next case. [Recorded departures](citation-effort/session-metadata.json)

The logged operation count measures interactions with the supplied reader. Elapsed time includes tool and model delays. The comparison is descriptive for these constructed cases, four sessions, and the two supplied workflows. It does not identify a human effort effect or isolate the contribution of source navigation from report structure.

## Live citation verification

Live FOLIO verified all 16 prespecified citation sides across C01, C03, C09, and C12. Twelve present sides replayed from 11 native anchors, and four sides explicitly confirmed absence. Both no-change controls also verified contextual anchors and zero change events. The compact citation inventory agreed with native replay and live HTTP. The in-app browser confirmed a moved pointer, both offset units, full quotation hashes, and the absent side of a removal.

## Reproduce

Use the [registered regeneration commands](citation-effort-preregistration.md#regenerate-the-packets), then compare the packet inventory, score, and independent replay to the archived files. The original answer bytes and action logs are fixed inputs. A new set of model sessions may produce different answers and times.

```sh
results=docs/manuscript/citation-effort
cmp "$trial/packets/packet-manifest.json" "$results/packet-manifest.json"
python scripts/citation_effort_score.py "$trial/cases/case-manifest.json" "$trial/packets/packet-manifest.json" "$results/submissions" > "$trial/score.json"
cmp "$trial/score.json" "$results/score.json"
```

For the independent check, pass the registration and scoring timestamps recorded in the [session metadata](citation-effort/session-metadata.json) to `scripts/citation_effort_crosscheck.py` with the same manifests, submissions directory, and generated score. Compare its output to `score-check.json`.

[Session S1 action log](citation-effort/submissions/S1/actions.jsonl) · [Session S2 action log](citation-effort/submissions/S2/actions.jsonl) · [Session S3 action log](citation-effort/submissions/S3/actions.jsonl) · [Session S4 action log](citation-effort/submissions/S4/actions.jsonl)
