# Source navigation ablation

Four fresh Codex sessions reviewed 16 constructed ScienceResearch and MathEducation revision pairs. Each case appeared once per arm at the same ordinal position and period in different sessions. The protocol, answer key, and packet commitment were anonymously readable on public GitHub before the first reader event. [Public preregistration](https://github.com/docxology/p3if/commit/809419a9af314eeb2ffca62256d5c329feea0970) · [Protocol](navigation-ablation-preregistration.md) · [Session metadata](../manuscript/navigation-ablation/session-metadata.json)

| Workflow or domain | Exact sides | Complete cases | Measured cases | Median evidence operations | Median elapsed time |
| --- | ---: | ---: | ---: | ---: | ---: |
| With source navigation | 76/76 | 16/16 | 16/16 | 7 | 9.223 s |
| Empty navigation array | 76/76 | 16/16 | 16/16 | 10 | 14.057 s |
| ScienceResearch, with source navigation | 38/38 | 8/8 | 8/8 | 7 | 9.058 s |
| ScienceResearch, empty navigation array | 38/38 | 8/8 | 8/8 | 10 | 14.866 s |
| MathEducation, with source navigation | 38/38 | 8/8 | 8/8 | 7 | 9.341 s |
| MathEducation, empty navigation array | 38/38 | 8/8 | 8/8 | 10 | 13.204 s |

All 76 matched sides were correct in both arms, comprising 65 present citations and 11 explicit absences. [Side-level scores](../manuscript/navigation-ablation/score.json)

Among 16 matched cases, the median within-case difference was -3.5 evidence operations and -2.323 s, taking navigation minus the empty-array control. Elapsed time includes the model and tool delays between the first evidence operation and the accepted submission. [Independent score replay](../manuscript/navigation-ablation/score-check.json)

Both arms received the same source bytes, question lists, lookups, reader, audit and transition fields. Only the source navigation array differed on the 14 changed cases. The audit checked 172 delivered files and all 16 paired report bodies. Sessions could see whether the array was populated. Each fresh session received only its own materials and generic instructions. The exact deployed model identifier was unavailable. [Packet inventory](../manuscript/navigation-ablation/packet-manifest.json) · [Packet audit](../manuscript/navigation-ablation/packet-check.json)

| Workflow | Opens | Finds | Searches | Citation extractions | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| With source navigation | 32 | 20 | 0 | 65 | 117 |
| Empty navigation array | 32 | 70 | 0 | 65 | 167 |

Navigation saved evidence operations in all 14 changed cases. The two no-change controls had empty navigation in both packets and identical operation counts. Their navigation-minus-control elapsed times still differed by +13.937 s for A01 (identical bytes) and +9.023 s for A09 (encoding only).

Independent source replay checked 32 transports, 20 moved pointers, 7 CRLF transports, and 50 present sides after multibyte text. The operation and timing differences describe the four observed sessions on these fixed revisions. [Source check](../manuscript/navigation-ablation/source-check.json) · [Session departures](../manuscript/navigation-ablation/session-metadata.json)

## Live FOLIO verification

Live FOLIO verified all 20 prespecified citation sides across A01, A04, A09, and A13. Sixteen present sides matched 14 retained native anchors, and four absent sides explicitly confirmed absence. Both no-change controls verified contextual declarations and zero events. The exact source-citation CLI, native workspace replay, and live loopback API agreed on source hashes, pointers, both offset units, and full quotation hashes. The dashboard’s 3D + Time view showed an exact moved citation and the verified absence of a removed property. The initial 352 workspace objects were preserved.

## Reproduce

Regenerate the case and packet inputs using the [registered commands](navigation-ablation-preregistration.md#regenerate-the-packets). The original model answers and logs are fixed inputs. Fresh model sessions can produce different answers and times.

~~~sh
results=docs/manuscript/navigation-ablation
key="$trial/cases/case-manifest.json"
packets="$trial/packets/packet-manifest.json"
cmp "$packets" "$results/packet-manifest.json"
python scripts/navigation_ablation_check_packets.py "$trial/packets" "$key" "$trial/packet-check.json"
cmp "$trial/packet-check.json" "$results/packet-check.json"
python scripts/navigation_ablation_score.py "$key" "$packets" "$results/submissions" > "$trial/score.json"
cmp "$trial/score.json" "$results/score.json"
python scripts/citation_effort_crosscheck.py "$key" "$packets" "$results/submissions" "$trial/score.json" --navigation-ablation --registered-utc 2026-11-15T21:18:26.147098Z --scoring-started-utc 2026-11-15T21:24:26.041999Z > "$trial/score-check.json"
cmp "$trial/score-check.json" "$results/score-check.json"
~~~

[Session S1 action log](../manuscript/navigation-ablation/submissions/S1/actions.jsonl) · [Session S2 action log](../manuscript/navigation-ablation/submissions/S2/actions.jsonl) · [Session S3 action log](../manuscript/navigation-ablation/submissions/S3/actions.jsonl) · [Session S4 action log](../manuscript/navigation-ablation/submissions/S4/actions.jsonl)
