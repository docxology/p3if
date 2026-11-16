# Preregistration for exact citation accuracy and model review effort

This comparison uses 16 new ordered pairs from the public ScienceResearch and MathEducation fixtures. It follows the [earlier masked study](held-out-reviewer.md), where both workflows reached the complete-case scoring ceiling. The new task is to identify and locate complete original JSON records, including a contextual record in each no-change control. The [case specification](citation-case-spec.json) and [case manifest](citation-case-manifest.json) fix the question identities, both source digests, exact answers, and expected absent sides before delivery.

Four fresh Codex sessions each review eight cases in two periods of four, with one workflow per period and two sessions starting with each workflow. Every case occurs once per workflow, at the same period and position in two different sessions. Each period contains two cases per domain. Neither session history nor allocation labels nor the answer key is delivered. Sessions receive only their assigned packet and the same instrumented reader. Original sources, name lookups, and citation questions match across workflows. The publicly regenerable packets are masked at delivery. The report contents and the presence of source navigation may reveal which workflow produced them.

The P3IF workflow supplies an audit and transition with source pointers for changed records. The comparator supplies a type-sensitive stable-ID field diff with field values and complete added or removed records. The same reader lets each reviewer view reports, search raw declarations, and extract an exact citation using a supplied pointer. The pointer search is available even for unchanged contextual records. Neither report supplies exact quotation hashes or offsets. This comparison measures the two workflows as delivered, including the P3IF source navigation.

Sessions use the reader for evidence access and submission, with operations run serially within each session. They may inspect counts and manually assemble responses. They may not independently rebuild a whole-case diff or audit, script selection of the answers, access other packets or the project, or consult the answer key. One exclusive submission is retained per case. The reader records evidence operations and submission boundaries without storing excerpts. Failures are counted once the reader has parsed a case action. Command syntax errors that occur before action logging do not appear in the ledger. Use the same pinned CPython 3.12.16 runtime for all four sessions. Score the full scheduled batch after all sessions finish.

## Outcomes

- The primary accuracy endpoint is the proportion of scheduled citation sides exactly correct. A present citation matches only when its source SHA-256, JSON Pointer, half-open Unicode codepoint bounds, half-open UTF-8 byte bounds, and complete quote SHA-256 all match. An absent side requires explicit JSON null. Missing, malformed, and incorrect sides remain in the denominator. Extra questions or duplicate question identities make the case response malformed. Also report complete-case accuracy, present and absent side accuracy, mismatched fields, and matched correct side counts.
- The primary effort endpoint is the number of instrumented evidence operations per completed case. Count each case resource open, find, literal search, and citation extraction, including logged failed and repeated operations. Exclude the explicit case start and submission operations from the operation count. The secondary effort endpoint is elapsed monotonic time from the first evidence operation for a case to its first validly logged submission. This boundary depends on submission integrity rather than citation correctness. Exclude the shared instructions and schedule, reporting their use separately when logged. Report effort separately by workflow and domain, the median number of operations, and the paired median difference (P3IF minus stable-ID diff). Missing or invalid logs do not enter the effort summaries. Report their count and paired denominator. Show elapsed milliseconds as descriptive observations and retain raw timestamps and actions for reruns. Model latency, tool overhead, and scheduling can affect elapsed time. Neither measure directly estimates human effort.
- Report outcomes on every assigned case, with complementary workflow order visible. These 16 constructed cases and four model sessions support descriptive comparisons. Citation correctness, tool operations, and elapsed time answer different questions.

## Verification and release

Publish the protocol, generator, scorer, and [SHA-256 commitments](citation-effort-commitment.json) before starting any session. Verify all delivered files independently and compare common inputs across arms. After submission, publish raw JSON answers, reader logs, registration and session metadata, and the score receipt. Confirm that regenerating packets and replaying the archived answers and logs reproduces the receipt byte-for-byte.

In the live FOLIO workspace, verify all questions for C01, C03, C09, and C12 against the frozen source hashes, pointers, both offset units, quotation hashes, and absent sides. The controls exercise contextual native citations when a transition has no events. Preserve every existing workspace object, and publish only aggregate verification results.

## Regenerate the packets

From the repository root with P3IF installed, run the following commands in a fresh directory.

```sh
trial=$(mktemp -d)
python scripts/citation_cases.py "$trial/cases"
cmp "$trial/cases/case-manifest.json" docs/manuscript/citation-case-manifest.json
python scripts/citation_effort_packets.py "$trial/cases" "$trial/packets"
```

Compare the SHA-256 of the generated `packet-manifest.json` with the commitment. The same packet generator works on the supported Python versions. The live study uses a single reader interpreter so its monotonic times are comparable within each session.
