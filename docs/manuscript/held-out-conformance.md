# Held-out P3IF interchange conformance

The [public registration](https://github.com/docxology/p3if/commit/c5a5e4f3f3ce77ddf0b39bf8b8fa3e74670093cc) fixed 16 ordered pairs, their expected events, and the decision rules before evaluation. The two shipped domain fixtures are shared with the earlier [technical reviewer pilot](reviewer-study-pilot.md). The interventions are new, and the independent source check found zero changed-target ID overlap with that pilot. [Protocol](held-out-preregistration.md) · [Case manifest](held-out-case-manifest.json) · [Independent source check](held-out-source-check.json)

| Domain | Passed | Encoding-only controls | Declared-change pairs | Events | Exact spans | Absent sides |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ScienceResearch | 8/8 | 1 | 7 | 24 | 39 | 9 |
| MathEducation | 8/8 | 1 | 7 | 24 | 39 | 9 |

All 16 passed on the first registered run. The audit reported zero declaration changes on both re-encoding controls. The 14 remaining pairs matched all 48 reference events in both directions, including score presence, coordinates, and the changes in framework and axis records. Independent lexical verification checked 78 full source tokens and 18 absent sides. Four retained records moved to different JSON pointers. The independent audit also matched every CLI output field on all 16 pairs, including signed axis, occupied-coordinate, and score deltas. [Per-case conformance receipt](held-out-conformance.json) · [Independent audit comparison](held-out-audit-comparison.json)

H02 and H10 each combine a rewire, addition, and removal while preserving both the relationship count and each occupied-coordinate count. H06 and H14 add another declaration at an existing pair coordinate. H07 and H15 replace a stable relationship ID while preserving the coordinate. H08 and H16 replace an occupied triple with a pair while preserving the relationship count. These checks distinguish record identity and declared coverage from aggregate relationship totals. [Interventions](held-out-case-spec.json)

Live FOLIO replay verified the six selected relationship events in H02 and H10. The dashboard, CLI, and native parser replay agreed on eight exact quotations and four absent sides. Both browser timelines advanced to their After state and displayed the moved pointers, separate UTF-8 byte and Unicode codepoint ranges, and full quotation hashes.

The registered comparison first ran on Python 3.12. The Python 3.9 CI job rejected an assignment expression inside a subscript. The follow-up uses explicit index updates, and the frozen inputs and output receipt remain byte-identical.

## Reproduce

Use the [registered commands](held-out-preregistration.md#reproduce), then compare the generated report with the [checked receipt](held-out-conformance.json).

```sh
cmp "$trial/conformance.json" docs/manuscript/held-out-conformance.json
python scripts/held_out_compare_audit.py "$trial/cases" "$trial/reference-audit.json" "$trial/source-check.json" "$trial/conformance.json" c5a5e4f3f3ce77ddf0b39bf8b8fa3e74670093cc "$trial/audit-comparison.json"
cmp "$trial/audit-comparison.json" docs/manuscript/held-out-audit-comparison.json
```

The receipts describe deterministic software behavior on constructed edits. The fixtures do not provide observed editorial revisions, human responses, comparative workflow accuracy, or estimates of effect size.
