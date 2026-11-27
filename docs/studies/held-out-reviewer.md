# Masked model review of 16 held-out revisions

Four fresh Codex model sessions submitted 32 responses after the [public preregistration](https://github.com/docxology/p3if/commit/59e0d13d6f9d81705d0476ba2c1977aba6d75a17). Each of the 16 case pairs was reviewed once with each workflow, at the same period and position across different sessions. All submitted rows followed their session schedule. The available runtime identifier was the GPT-6 family in Codex. Its exact deployed model identifier was unavailable. [Protocol](held-out-reviewer-preregistration.md) · [Session metadata](../manuscript/held-out-reviewer/session-metadata.json)

| Domain | P3IF audit and transition | Stable-ID diff | Both correct | P3IF only | Diff only | Neither |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ScienceResearch | 8/8 | 8/8 | 8 | 0 | 0 | 0 |
| MathEducation | 8/8 | 8/8 | 8 | 0 | 0 | 0 |
| Combined | 16/16 | 16/16 | 16 | 0 | 0 | 0 |

All 32 answers were complete and correct. Neither workflow produced a false declared-change classification on the two encoding controls. There were no incorrect, malformed, or missing responses. The complete-case metric reached its ceiling in both workflows. The observed difference was zero correct cases. This descriptive comparison cannot distinguish the workflows on these cases or establish equivalence, relative efficiency, or human reviewer performance. [Per-case and paired score receipt](../manuscript/held-out-reviewer/score.json)

The packet check matched all 136 delivered file hashes and byte-identical original snapshots and lookups for each paired assignment. Treatment labels and the answer key were withheld from the model sessions. The report formats and sizes remained distinguishable, and the reference was already publicly available. Each model was instructed to use only its assigned packet and reported no deviations. [Packet inventory](../manuscript/held-out-reviewer/packet-manifest.json) · [Packet check](../manuscript/held-out-reviewer/packet-check.json)

## Exact citation replay

On the live FOLIO workspace, the qualified CLI and live HTTP responses agreed on 16 events across H02, H08, H10, and H16. Native parser replay verified 20 exact original quotations and 12 absent sides. The checks matched the original source SHA-256 values, JSON pointers, Unicode and UTF-8 offsets, and full quotation hashes. Paginated evidence replay agreed with the event-by-event responses. The checks used the frozen [case manifest](../manuscript/held-out-case-manifest.json).

## Reproduce

Use the [registered case and packet commands](held-out-reviewer-preregistration.md#reproduce), then verify that the generated inventory and score match the archived bytes. The archived submissions are the original JSON arrays. New model runs may return different answers.

```sh
methods=docs/manuscript
responses="$methods/held-out-reviewer"
cmp "$study_dir/packets/packet-manifest.json" "$responses/packet-manifest.json"
python scripts/held_out_reviewer_score.py "$study_dir/cases/case-manifest.json" "$study_dir/packets/packet-manifest.json" "$responses" > "$study_dir/score.json"
cmp "$study_dir/score.json" "$responses/score.json"
python scripts/held_out_reviewer_crosscheck.py "$study_dir/cases/case-manifest.json" "$study_dir/packets/packet-manifest.json" "$responses" "$study_dir/score.json" > "$study_dir/score-check.json"
cmp "$study_dir/score-check.json" "$responses/score-check.json"
```

[Session S1](../manuscript/held-out-reviewer/S1.json) · [Session S2](../manuscript/held-out-reviewer/S2.json) · [Session S3](../manuscript/held-out-reviewer/S3.json) · [Session S4](../manuscript/held-out-reviewer/S4.json) · [Independent score check](../manuscript/held-out-reviewer/score-check.json)
