# Auditing a ScienceResearch editorial proposal

Can a reviewer distinguish a change to an editorial model from a different rendering of the same snapshot? This worked case compares a public ScienceResearch fixture with one controlled proposal and two controls. It measures what the snapshots declare and shows which effects a census alone would miss.

## Editorial question and intervention

For the Journal Editor perspective, which existing process best represents the work of making research data discoverable and accessible through a data availability statement? PLOS ONE recommends repository deposition where possible and asks for repository names and persistent identifiers in statements for deposited data. Springer Nature asks authors to explain how supporting data can be accessed, including repository identifiers where available and explanations when open sharing is restricted. [PLOS ONE data availability policy](https://journals.plos.org/plosone/s/data-availability) · [Springer Nature guidance for authors and editors](https://www.springernature.com/gp/authors/research-data-policy/data-availability-statements)

The proposal interprets that guidance as support for mapping Research Data Sharing, from the Journal Editor viewpoint, to Data Repository Management. All four named axis entries are from the shipped fixture. The policy pages supply the rationale for the modeling decision, and the relationship carries their URLs as evidence references. The proposal status records the decision for review. [Shipped ScienceResearch fixture](../../data/domains/scienceresearch.json)

| Declaration | Baseline | Proposal |
| --- | --- | --- |
| Relationship ID | `2df34732-0613-4919-adfe-0c871ad9ccd4` | Same ID |
| Property | Research Data Sharing | Research Data Sharing |
| Process | Sustainability Analysis | Data Repository Management |
| Perspective | Journal Editor | Journal Editor |
| Strength | `0.81` | Omitted |
| Confidence | `0.83` | Omitted |
| Status | Omitted | `proposed` |
| Evidence sources | Omitted | Two public publisher guidance pages |

The earlier scores were attached to the earlier coordinate. The proposal leaves the scores unassigned because the cited guidance supplies no measurement procedure or quantitative result for the proposed relationship.

## Reproduce the audit

From a checkout or extracted source distribution, use a Python environment with P3IF installed. The [reproduction driver](../../scripts/scienceresearch_editorial_audit.py) runs `p3if migrate` on the shipped fixture, writes a pretty-printed copy of the baseline, and writes the proposal in the same pretty-printed form. The driver requires a new output directory. The outputs and comparisons can be generated offline after installation.

```sh
python -m pip install -e .
p3if_work=$(mktemp -d "${TMPDIR:-/tmp}/p3if-editorial.XXXXXX")
python scripts/scienceresearch_editorial_audit.py "$p3if_work/snapshots"
baseline="$p3if_work/snapshots/baseline.json"
proposal="$p3if_work/snapshots/proposal.json"
encoding="$p3if_work/snapshots/encoding-only.json"
python -m p3if audit "$baseline" "$proposal" --output "$p3if_work/proposal-audit.json"
python -m p3if audit "$baseline" "$encoding" --output "$p3if_work/encoding-audit.json"
python -m p3if audit "$baseline" "$baseline" --output "$p3if_work/identity-audit.json"
python -m p3if transition "$baseline" "$proposal" --output "$p3if_work/transition.json"
```

The audits use `p3if.snapshot-audit.v1`. Compare `before.source_sha256` and `after.source_sha256` for exact bytes and the two `analysis.semantic_sha256` values for canonical declared content.

| Comparison | Expected classification | Exact hashes | Canonical hashes | Expected relationship result |
| --- | --- | --- | --- | --- |
| Baseline → proposal | `declared_change` | Different | Different | One modification and one rewire on the same record |
| Baseline → pretty-printed baseline | `encoding_only` | Different | Equal | Zero changes and zero deltas |
| Baseline → baseline | `identical_bytes` | Equal | Equal | Zero changes and zero deltas |

The proposal transition contains one event with changed fields `confidence`, `evidence_sources`, `process_id`, `status`, and `strength`. Its middle coordinate moves from `096bd1eb-52ba-4bde-8396-56814f8da38b` to `97e2f3ad-597c-4bc1-bf01-e29105879c50`. The other endpoints stay fixed. Sustainability Analysis loses its only declared link and Data Repository Management already has a link, so the number of linked processes falls from 40 to 39 and the number of unlinked processes rises from 10 to 11. The three pair spaces and the triple space have zero count deltas. There are still 71 declared relationships on 71 distinct triples out of 112,500 possible triples. Each score tally loses one reported nonzero value and gains one omission. [Measurement definitions](METHODS.md)

## Proposed evaluation

The worked case is a software check with a known intervention. To test whether the audit helps people review unfamiliar changes, preregister a comparison with a stable-ID JSON diff. Supply both workflows with the same snapshots, ID-to-name lookups, and policy excerpts. Give the audit group the audit and transition outputs. Give the comparison group the field-level diff keyed by the same IDs. Recruit reviewers who routinely inspect editorial or requirements changes, and use a counterbalanced crossover design with disjoint cases in each round. Record participant familiarity before assignment and use it in the analysis plan.

Before the study, have two independent annotators record the expected change class, changed ID, old and new endpoints, and score-presence states for each case. Resolve disagreements through a third annotator before revealing the study outputs. Include exact copies, re-encodings, metadata-only edits, endpoint changes, additions and removals, and changes that preserve aggregate counts. Keep a held-out test set from a second domain and freeze case hashes and scoring rules before data collection.

The primary outcome is the proportion of cases whose complete change description matches the frozen annotations. The hypothesis is that the audit workflow increases that proportion by at least 10 percentage points. Set the sample size from a pilot that is separate from the evaluation. Report paired differences with 95% intervals that account for repeated reviewers and cases. A lower bound at or above 10 percentage points supports the hypothesis. An upper bound below 10 percentage points contradicts it. An interval spanning the threshold leaves the result inconclusive. Report the encoding-only false-positive rate and review time as secondary outcomes.

## Limits of the worked case

The fixture and proposal show how a change in declared coordinates can coexist with identical coordinate counts. Claims about editorial uptake, policy compliance, model completeness, and reviewer utility require separate evidence. The proposal reflects an interpretation of two policies as accessed on 2026-11-09. Decisions about repository deposition or restricted access depend on the journal and the circumstances of the paper. Coverage deltas depend on the supplied graph, and stable-ID alignment depends on the producer retaining IDs across snapshots. The proposed reviewer study has yet to be run.
