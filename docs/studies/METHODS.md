# Measuring and comparing declared P3IF graphs

## Unit of analysis

A P3IF snapshot contains three typed sets of entities. A Property describes a system characteristic, a Process describes an activity, and a Perspective identifies a viewpoint. A relationship declares exact endpoints on two or three of these axes. The snapshot carries its canonical SHA-256 so that a reported measurement can be bound to the same validated input. The hash covers declared values and presence, after serialization through the wire contract. [Interchange contract](../interchange.md)

## Sparse coverage

For each axis, count its declared identities and the distinct identities mentioned in at least one relationship. The difference is the number of unlinked entities on that axis. Count each relationship once in the space defined by its exact endpoint axes. The four spaces consist of the three axis pairs and the triple. A relationship on all three axes contributes to the triple count. Pair coverage measures independently declared pairs.

A coordinate is the ordered tuple of endpoint IDs. Multiple relationships can occupy the same coordinate. The report therefore carries both the relationship count and the distinct observed coordinate count. Multiply the participating axis sizes to compute the number of possible coordinates. Subtract the observed count for the number of unobserved coordinates. These calculations use the retained relationships and cardinalities without enumerating the Cartesian product. An empty axis gives a zero-size space. The relationship and coordinate counts describe the supplied snapshot. A claim that an unobserved coordinate is an important gap needs a scoped inquiry or external criterion.

For strength and confidence separately, tally omitted values, explicit JSON `null`, reported zero, and reported nonzero. The missing total is omitted plus null. The reported total is zero plus nonzero. These are counts of declared values. An absent score supplies no numeric evidence.

## Version comparison

Validate both snapshots and require the same framework ID. Within each type, align records by their explicit IDs. An ID present on one side is added or removed. Compare the declared fields of retained IDs, including field presence. For relationships, compare endpoint identities as well as other fields. A change to an endpoint value marks a rewire. Changing a label leaves the ID in place, while changing an ID creates an addition and a removal. Matching uses declared IDs and types.

The methods apply to a single declared graph or to revisions within one declared framework identity. The combination of a name, ID, and hash identifies what the producer supplied. The resulting report concerns the supplied structure and declared metadata. Assessing authority, framework adequacy, or relationship quality requires separate evidence.

## Coordinate transitions

Use the sorted union of declared IDs on each axis as the discrete coordinate system for both snapshots. A changed relationship occupies the coordinates of its exact endpoints at each stage. A change to a single axis member occupies just that axis. A metadata change to the framework itself has no declared location. Keep a separate null slot for an absent endpoint and a distinct state for a record absent from a whole snapshot. These rules preserve the difference between a pair, a triple, and an added or removed relationship.

Coordinates describe categorical identifiers. Spatial distances depend on how a renderer positions the sorted IDs and have no domain meaning. A line joining the two coordinates of a rewired relationship connects the declared endpoints of that comparison. Two retained snapshots establish the displayed stage order. Additional data is required to date a change or reconstruct intervening activity.

## Reproduce the ScienceResearch census

From the repository root, install P3IF and put outputs in a new temporary directory.

```sh
python -m pip install -e .
p3if_work=$(mktemp -d "${TMPDIR:-/tmp}/p3if-methods.XXXXXX")
python -m p3if migrate data/domains/scienceresearch.json \
  --id p3if.science-research --name 'Science research' \
  --output "$p3if_work/science.json"
python -m p3if analyze "$p3if_work/science.json" --output "$p3if_work/science-analysis.json"
cat "$p3if_work/science-analysis.json"
```

The shipped source declares 50 properties, 50 processes, and 45 perspectives. Its 71 relationships occupy 71 distinct triple coordinates. The triple space contains 112,500 possible coordinates. Both metrics have 71 reported values. The report shows 8 unlinked properties, 10 unlinked processes, and 12 unlinked perspectives. These are descriptive counts for this exact dataset. [Shipped ScienceResearch domain](../../data/domains/scienceresearch.json)

To reproduce the census across the domain library, write one report per shipped domain. The directory index supplies navigation, and the template supplies a copyable example. The corpus loop selects the domain datasets.

```sh
mkdir "$p3if_work/corpus"
for source in data/domains/*.json; do
  name=${source##*/}
  case "$name" in index.json|template_domain.json) continue ;; esac
  key=${name%.json}
  python -m p3if migrate "$source" --id "p3if.$key" --name "$key" \
    --output "$p3if_work/corpus/$key.snapshot.json" || exit 1
  python -m p3if analyze "$p3if_work/corpus/$key.snapshot.json" \
    --output "$p3if_work/corpus/$key.analysis.json" || exit 1
done
```

Each denominator belongs to its own framework. A combined coordinate count needs a separately defined merged set of identities and relationships.

## Reproduce a controlled revision

Use the same temporary directory. Create a second snapshot from the synthetic archive fixture. Keep the framework ID and relationship ID, introduce a new process, point the triadic relationship to it, and remove the reported strength of zero. The edit is intentionally small so its expected effects can be checked directly.

```sh
python - "$p3if_work/archive-after.json" <<'PY'
import json
import sys
from pathlib import Path

fixture = Path("examples/interchange/framework-v1.json")
document = json.loads(fixture.read_text(encoding="utf-8"))
document["processes"].append({
    "id": "process.recheck-intake",
    "name": "Recheck intake",
    "description": "Repeat intake verification after an initial discrepancy.",
    "domain": "synthetic-archive",
})
link = next(row for row in document["relationships"]
            if row["id"] == "relationship.fidelity-at-intake")
link["process_id"] = "process.recheck-intake"
del link["strength"]
with Path(sys.argv[1]).open("x", encoding="utf-8") as output:
    json.dump(document, output, ensure_ascii=False, indent=2)
    output.write("\n")
PY
python -m p3if compare examples/interchange/framework-v1.json \
  "$p3if_work/archive-after.json" --output "$p3if_work/archive-comparison.json"
python -m p3if transition examples/interchange/framework-v1.json \
  "$p3if_work/archive-after.json" --output "$p3if_work/archive-transition.json"
python -m p3if analyze "$p3if_work/archive-after.json"
cat "$p3if_work/archive-comparison.json"
cat "$p3if_work/archive-transition.json"
```

Expect one added process and one modified relationship with changed `process_id` and `strength` fields. The transition places the new process only on the later Process axis. The rewired relationship moves from `process.verify-intake` to `process.recheck-intake` while keeping the same Property and Perspective. The number of observed triple coordinates remains one while the possible triple count grows from two to four. The strength tally moves from one reported zero and one omission to two omissions. The expected changes follow from the explicit edit and can be checked independently of archive practice. [Synthetic archive fixture](../../examples/interchange/framework-v1.json)
