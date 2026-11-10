# P3IF snapshot review study preregistration

Protocol version 1 · 2026-11-09 · Registration in the public P3IF repository.

This protocol defines a technical pilot and a later confirmatory study with people who review editorial or requirements changes. The technical pilot exercises case construction, allocation, response capture, scoring, and exact source replay. Its units are assigned review sessions and synthetic response controls. Its results can identify broken steps or ambiguous instructions. Estimates of reviewer accuracy, utility, and time for people come from the later human study. [Prior study proposal](scienceresearch-audit.md#proposed-evaluation)

## Question and conditions

Does access to the P3IF audit and transition reports increase the chance that a reviewer correctly describes every material change in a snapshot pair? Compare two workflows using the same exact source snapshots, stable IDs, ID-to-name lookup, question, and response schema. Supply the same contextual notes or evidence excerpts on both sides whenever a case includes them.

| Condition | Additional material |
| --- | --- |
| P3IF | Snapshot audit and directional transition reports |
| Stable-ID diff | Field-level JSON diff keyed by stable ID |

Both workflows retain additions and removals, distinguish omitted fields from present fields, and expose exact-byte identity. Reviewers can inspect the source pair in either condition. The treatment is the complete report workflow, including its organization and derived information. Reviewers will recognize their assigned interface. They receive neutral instructions without the directional hypothesis, answer key, or other arm's packet. Scorers see only opaque case identifiers and submitted answers until scoring is locked. [Audit and transition definitions](METHODS.md)

## Cases, allocation, and annotation

- Build six pilot cases each from the public ScienceResearch and MathEducation fixtures. Each domain contributes one exact copy, re-encoding, relationship metadata edit, endpoint rewire, addition, and removal. Include a rewire with a score withdrawal and a change that preserves coordinate counts. These are controlled declarations in supplied fixtures. [ScienceResearch fixture](../../data/domains/scienceresearch.json) · [MathEducation fixture](../../data/domains/matheducation.json)
- Before review, record exact source hashes, case IDs, expected responses, condition packet hashes, allocation, response schema, and scoring rule. Case builders derive expectations from declared interventions and source inspection. The audit and diff are treatment materials and cannot serve as the sole answer key. Compare the frozen expected values against direct inspection of the source bytes. Retain the inspection record with the preregistration artifacts. [Intervention specification](reviewer-study-case-spec.json) · [Frozen case manifest](reviewer-study-case-manifest.json)
- Divide cases into disjoint panels with three cases per domain in each panel. Keep assignment and packet identities with the response record, apart from the scorer's inputs.
- Prepare a fresh case bank for human evaluation. Use distinct variants and reserve one fresh domain panel for cross-domain analysis. Two annotators independently inspect exact source pairs and record answers under the response schema. A third adjudicates discrepancies before anyone sees condition packets. Report counts and types of initial disagreements and the resolution procedure. Seal the adjudicated key before assignment.

## Outcomes and scoring

The primary outcome is complete case accuracy, a binary exact match to the frozen answer. Each response gives a case ID, one class (`identical_bytes`, `encoding_only`, or `declared_change`), and a list of changed records. For each changed record, require the stable ID, change operation (`added`, `removed`, or `modified`), changed fields, and applicable before and after states. Each state gives endpoints in property, process, perspective order and a presence class for strength and confidence (`omitted`, `explicit_null`, `reported_zero`, or `reported_nonzero`). For additions and removals, use an empty changed-fields list and null for the absent state. Apply the same normalization to both arms. Allow irrelevant ordering differences in the record and field lists and compare identifiers exactly. An extra, missing, or incorrect required item makes the case incorrect. For identity and encoding-only cases, a complete answer has the correct class and no changes.

Secondary outcomes are the proportion of encoding-only cases falsely labeled as declared changes and, for human sessions, time from opening the assigned packet to final submission. A deadline without a submission counts as incorrect and as incomplete for the timing report. Keep valid partial records so another analyst can reproduce the denominator and reasons for missingness. Publish complete-case accuracy, coverage, and errors by class and domain as descriptive pilot results when the response data support those summaries.

## Technical pilot

Run the locked cases through the allocation and scoring pipeline after the protocol and case hashes are frozen. Use opaque identifiers and neutral filenames within review packets. Panel A runs in order R01, R04, R07, R10, R11, R06. Panel B runs in order R08, R03, R02, R12, R09, R05.

| Pilot session | Period 1 | Period 2 |
| --- | --- | --- |
| T1 | Panel A with P3IF | Panel B with stable-ID diff |
| T2 | Panel A with stable-ID diff | Panel B with P3IF |

Each session sees each case once. Every case is reviewed in both conditions across sessions, and the tool order is balanced. Panel order is fixed for the technical pilot. Label any model reviewer explicitly and identify its session and available model metadata. Start each assigned session without the answer key or previous responses. Synthetic positive and negative submissions can check the scorer. Keep these controls separate from any reviewer responses. Technical acceptance requires reproducible packet identities, one assignment per case per session, both conditions represented for every case, and a scorer that accepts exact answers and rejects at least one incorrect class and one incorrect event field. Report missing, malformed, or leaked packets and any changes made after the freeze as deviations.

Check citation replay in FOLIO independently of the scorer. For a changed record, compare its stable ID and original JSON pointer with the retained source bytes. For each cited side, verify the content hash, parser identity, and exact referenced text. Record replay failures and their disposition. Citation replay shows that the evidence can be recovered. It does not score the scientific merits of a fixture, intervention, or rationale.

## Confirmatory human study

Recruit consenting adults who routinely review editorial or technical requirements changes after obtaining the applicable research oversight and approval. Record review experience and self-rated familiarity with both domains and diff tools before assignment. Run a separate feasibility cohort to estimate completion time, variance components, and the recruitment target. Exclude its observations and cases from the confirmatory study. Plan the target with simulation under a 20-point true gain and a zero-gain alternative. Seek at least 80% probability that the primary interval resolves the 10-point threshold in each scenario. Use the pilot to estimate nuisance parameters and plan attrition. Fix the target, allocation strata, and analysis inputs in a dated amendment before confirmatory enrollment. Recruit to that target without interim accuracy looks or efficacy stopping.

For confirmatory sessions, randomize within predeclared experience strata to four allocations balancing tool order and the case panel seen under each tool. Include the two panel-first allocations in the pilot table and their counterparts with the panel order reversed and the tool order held fixed. Use both domains in each period, block the order by domain, and provide a break between periods. Give everyone the same practice materials on separate cases. The interface enforces a fixed eight-minute maximum per case. Preserve condition assignments in the analysis, including timeouts and skipped cases. Report post-assignment losses and prespecify the handling of consent withdrawals under the approved policy before enrollment.

The primary estimand is the marginal probability of complete case accuracy under the P3IF workflow minus that under the stable-ID diff, with equal weight for both domains and equal case weight within each domain. Estimate the difference from assigned responses, first calculating each case's difference across conditions, then averaging within domain and across domains. Use a 95% percentile interval from 10,000 crossed bootstrap replicates with reviewers resampled within their allocation strata and cases resampled within domain and panel. Use multiplicative reviewer and case weights. Publish the random seed and the frequency of replicates in which a condition has no observations. Do not make a threshold decision if 5% or more of replicates are undefined. Report sensitivity estimates stratified by familiarity and analyses by period and domain as secondary. For missingness, additionally report best-case and worst-case arm contrasts.

The hypothesis threshold is an improvement of at least 10 percentage points. A 95% interval with a lower bound at or above 10 points supports that threshold. An upper bound below 10 points contradicts it. All other intervals leave the threshold unresolved. Technical pilot outcomes do not enter this test or substitute for human feasibility estimates.

## Registration and deviations

Identify the immutable public protocol revision and the case and scoring manifest in the pilot report. Date each deviation and report when it was discovered relative to packet generation, review, and scoring. Keep the original record available. Store public fixtures, code, manifests, and shareable pilot results together. Human consent and private workspace material remain outside this publication.

## Reproduce the registered materials

Run these commands from a checkout or extracted source distribution after installing P3IF. Use new output paths.

```sh
python -m pip install .
study_dir=$(mktemp -d)
python scripts/reviewer_study_cases.py "$study_dir/cases"
cmp "$study_dir/cases/case-manifest.json" docs/manuscript/reviewer-study-case-manifest.json
python scripts/reviewer_study.py packets "$study_dir/cases" "$study_dir/packets"
cmp "$study_dir/packets/packet-manifest.json" docs/manuscript/reviewer-study-packet-manifest.json
```

Send each session only its own packet directory. Each directory contains common instructions and a schedule. Keep submitted answers in separate `T1.json` and `T2.json` files, each containing a JSON array. To score the submissions, use the command below with the directory that contains both answer files. A row with a known case ID and a malformed answer stays in the denominator. A session file with duplicate or unassignable case IDs needs resolution before scoring.

```sh
python scripts/reviewer_study.py score "$study_dir/cases/case-manifest.json" "$study_dir/responses"
```

The crossed interval plan uses separate resampling weights for reviewers and cases. Report randomized sequence, participant flow, period results, and potential carryover for the human study. [Owen and Eckles on crossed resampling](https://arxiv.org/abs/1106.2125) · [Dwan and colleagues on crossover reporting](https://www.bmj.com/content/366/bmj.l4378)
