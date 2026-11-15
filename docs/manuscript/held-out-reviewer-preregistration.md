# Masked model comparison on held-out P3IF revisions

Registered on 2026-11-14 for a technical model review comparison on the 16 ordered pairs in the [held-out case manifest](held-out-case-manifest.json). These pairs were excluded from the [first technical reviewer pilot](reviewer-study-pilot.md) and have a previously published [deterministic reference check](held-out-conformance.md). The fixture domains, interventions, exact source bytes, and answer key are fixed. There are no human participants.

## Assignment and packet contents

Four fresh Codex model sessions each review eight cases in two four-case periods, using one workflow per period. Two sessions see each workflow first. Each case appears once per workflow, at the same period and position in two different sessions. No session sees the same case twice. Every period contains two ScienceResearch and two MathEducation cases. Complementary panels swap the domains for each intervention family while preserving its position.

Both workflows receive byte-identical original snapshots, stable-ID lookups, instructions, and neutral filenames. One workflow receives a P3IF audit and transition report with the producer method label removed and canonical hashes explicitly named. The comparison receives a field-level JSON diff over matched stable IDs for the framework, each axis, and relationships. That diff preserves field presence, JSON value types, and array order, and includes the full record for additions and removals. Both reports identify the exact transport hashes. The report structures remain different and may reveal the workflow.

Each session receives only its scheduled packet directory, without previous chat history, the other packets, condition and allocation labels, or the reference answer key. Instructions allow inspecting the supplied snapshots and lookup for context and disallow rebuilding a second whole-case comparison, consulting the repository or internet, or reading outside the packet. The study withholds these materials at delivery. The published fixture identities and answer key remain independently accessible, and the sessions are not an operating-system sandbox.

Publish this protocol, the packet and scorer code, and [the SHA-256 commitment](held-out-reviewer-commitment.json) on a public ref before starting model sessions. Independently verify schedule balance, file hashes, equal common inputs and masking in the delivered folders. Once delivery starts, retain the first submitted responses, timestamps and deviations. Do not replace an incorrect response. Publish the committed packet inventory and raw responses after submission.

## Outcome and analysis

The primary descriptive endpoint is complete-case correctness for each of the 32 assigned slots. Classify exact byte identity, encoding-only change, or declared change, then report the entire set of changed stable identities, kinds, operations, modified fields, rewire flags, before/after coordinates and score states. Score all event fields and both sides. Event and field list order are flexible. Axis order and the before/after direction are fixed.

An omitted response file or assigned case row counts as missing. Unparseable or non-array session files count as malformed for each of their eight assignments. A repeated assigned ID or an invalid answer structure marks that case malformed. Unassignable rows are documented and do not enter the denominator. Well-formed wrong answers count as incorrect. The frozen assignment, rather than response order, attaches each case to a workflow.

Report exact correct counts by workflow and domain, plus the number of case pairs correct in both workflows, only P3IF, only stable-ID diff, or neither. Report encoding false positives on parseable rows, component errors and any departures. The unit of matching is the case. Answers share four model sessions, and there is one answer per case and workflow. This descriptive comparison provides no inferential effect estimate or evidence about human reviewers. Tool use and completion time are excluded from scoring.

## Source verification in FOLIO

On the local live workspace, recheck H02 and H10 and replay the endpoint lifecycle changes H08 and H16. These four prespecified pairs cover 16 declared events, 20 present quotation spans, and 12 absent sides. For every present side match its original transport SHA-256, pointer, half-open Unicode and UTF-8 ranges, and full quotation SHA-256. Verify native anchor replay and CLI/dashboard agreement. Maintain the private workspace inventory and publish only aggregate evidence and instructions.

## Reproduce

Build into a new temporary directory from the repository root, with P3IF installed.

```sh
study_dir=$(mktemp -d)
python scripts/held_out_cases.py "$study_dir/cases"
cmp "$study_dir/cases/case-manifest.json" docs/manuscript/held-out-case-manifest.json
python scripts/held_out_reviewer_packets.py "$study_dir/cases" "$study_dir/packets"
```

Verify the packet manifest digest with the commitment before scoring. The generator and scorer run locally. The archived model responses are fixed inputs to scoring, and new model sessions can produce different answers.
