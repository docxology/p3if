# Held-out interchange conformance preregistration

Registered for the 2026-11-14 technical follow-up to the [two-domain reviewer pilot](reviewer-study-pilot.md). The unit of analysis is one ordered snapshot pair. The experiment exercises deterministic P3IF and FOLIO software with synthetic edits to shipped frameworks. It involves no participants, reviewer assignments, or model-generated answers.

## Cases and freeze

The [case specification](../manuscript/held-out-case-spec.json) declares the fixture sources and edits for 16 pairs, eight in ScienceResearch and eight in MathEducation. The [answer manifest](../manuscript/held-out-case-manifest.json) binds the case generator to exact UTF-8 input digests, declarative answers, and citation spans. The intervention families exercise top-level ordering and JSON escaping with unchanged declarations, simultaneous rewire/add/remove, score presence transitions, type-sensitive nested metadata, multi-kind edits, pair/triple changes, stable-ID replacement, and referentially closed axis changes.

Held-out here means the challenges were constructed for this follow-up and excluded from the initial pilot. The two public domain fixtures are shared with the pilot. The case design and reference answers are public after registration.

Before running the held-out evaluation, regenerate the candidate inputs from the specification, verify source bytes and answers with an independent raw-JSON check, and publish this protocol with the exact specification, manifest, and executable comparison on a public Git ref. Record that ref's full commit identity and the verified manifest digest. After the freeze, keep these case identities, bytes, answer fields, and rules fixed. If execution exposes a defect, retain the first result, explain the repair, and rerun against the same manifest. Report a changed case or scoring rule in an explicit amendment.

## Outcomes and checks

- A P3IF case passes only if the audit's classification and both exact source SHA-256 values match the reference, the canonical hashes agree with transition output, and the complete stable-ID event set agrees on kind, operation, changed fields, rewiring, coordinates, and score states. Recover score states from the indexed source sides. Check audit event counts, framework fields and identity, and axis unions. Compare reverse transitions to the same key with sides and add/remove operations reversed. Report each case and domain, including all failures. The conformance target is 16 of 16 cases.
- A citation span is half-open in both Unicode codepoints and UTF-8 bytes against the original document. The event's JSON Pointer must locate its exact original JSON value. Verify the full quoted-byte SHA-256, and require null for a side where the event record is absent. Validate citation keys and sides for all events. Report the exact denominator.
- The live FOLIO check is fixed to the added, removed, and modified relationship events in ScienceResearch H02 and MathEducation H10. Import the four registered files into the actual workspace and replay both sides of those six events. Verify eight present spans and four absent sides against the frozen source hashes, pointers, offsets, and full quotation digests. Require exact CLI and live HTTP parity and verify retained native anchors by parser replay. In the browser, compare the chosen pair for each domain, advance the snapshot slider, and inspect the modified event's before/after quotation cards. Check at least one moved source pointer per domain and at least one distinct byte vs. codepoint offset per domain.
- Repeat the case build and P3IF evaluation and compare the manifest and receipt byte-for-byte. Perturb a source byte in a disposable copy to verify rejection against the frozen digest. A result requires all registered pairs and reports any rejected inputs or unverified live surfaces.

## Reproduce

From the repository root with P3IF and its dependencies installed, build into an empty temporary namespace.

```sh
trial=$(mktemp -d)
python scripts/held_out_cases.py "$trial/cases"
cmp "$trial/cases/case-manifest.json" docs/manuscript/held-out-case-manifest.json
python scripts/held_out_source_check.py "$trial/cases" "$trial/source-check.json" "$trial/reference-audit.json"
cmp "$trial/source-check.json" docs/manuscript/held-out-source-check.json
python scripts/held_out_verify.py "$trial/cases" > "$trial/conformance.json"
```

The technical results apply to these constructed changes. They do not estimate reviewer accuracy or workflow advantage, describe naturally occurring revisions, or establish generalization to other domains.
