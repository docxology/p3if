# Two-domain technical reviewer pilot

Two isolated Codex model sessions ran the registered crossover on ScienceResearch and MathEducation. Each reviewed 12 cases using its assigned packet and submitted structured answers before the coordinator ran the frozen scorer. The sessions received separate folders and neutral instructions. The answer key was public after registration, so isolation depended on the packet delivery procedure and reviewer instructions. [Public registration commit](https://github.com/docxology/p3if/commit/f2f1e0c18e6fdc54563e4df81eef59bc651570de) · [Protocol](reviewer-study-preregistration.md) · [Session metadata](reviewer-study-pilot/session-metadata.json)

## Descriptive results

| Domain | Workflow | Assigned | Complete and correct | Incorrect | Missing or malformed | Encoding false positives |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ScienceResearch | P3IF audit + transition | 6 | 6 | 0 | 0 | 0 |
| ScienceResearch | Stable-ID diff | 6 | 6 | 0 | 0 | 0 |
| MathEducation | P3IF audit + transition | 6 | 6 | 0 | 0 | 0 |
| MathEducation | Stable-ID diff | 6 | 6 | 0 | 0 | 0 |

All submitted cases matched the frozen key. These fixtures produced a ceiling in the two technical sessions.

The case set exercises exact copies, re-encodings, metadata edits, endpoint rewires, additions, and removals. An independent raw-source check verified all 12 reference answers and 24 source hashes. The paired packet check verified the same source and lookup bytes in both workflows for every case. Separate synthetic controls accepted 12 exact answers and rejected the two prescribed errors, one in class and one in a changed field. [Raw source check](reviewer-study-pilot/raw-case-key-check.json) · [Packet check](reviewer-study-pilot/packet-mask-check.json) · [Scorer controls](reviewer-study-pilot/pilot-controls.json)

One session flagged a naming ambiguity. The transition report’s `before_sha256` and `after_sha256` identify canonical interchange, while the audit reports exact source hashes separately. The reviewer used the source hashes to classify byte identity. Both sessions reported no departures from the assigned procedure.

The technical sessions check whether reviewers can use the packets and whether their answers can be scored. The two model sessions provide no human observations. Human completion time, recruitment, and the 10-point confirmatory threshold remain unevaluated.

## Reproduce the score

Build the inputs and packets using the [registered commands](reviewer-study-preregistration.md#reproduce-the-registered-materials), then score the archived submissions from the repository root. The archived submissions are fixed model outputs. Regenerating model answers may give different responses.

```sh
python scripts/reviewer_study.py score "$study_dir/cases/case-manifest.json" docs/manuscript/reviewer-study-pilot > "$study_dir/reproduced-score.json"
cmp "$study_dir/reproduced-score.json" docs/manuscript/reviewer-study-pilot/score.json
```

[Session T1 responses](reviewer-study-pilot/T1.json) · [Session T2 responses](reviewer-study-pilot/T2.json) · [Row-level score receipt](reviewer-study-pilot/score.json)
