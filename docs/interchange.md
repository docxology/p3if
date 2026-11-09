# P3IF interchange v1

Interchange is a versioned, data-only snapshot of a framework. The contract is portable between producers and consumers. It gives a **Property**, **Process**, and **Perspective** stable identities in their own collections, then names exact endpoints in each declared relationship.

## Read and inspect a snapshot

Install the package from the checkout and run these commands from its root.

```sh
python -m pip install -e .
python -m p3if validate examples/interchange/framework-v1.json
python -m p3if inspect examples/interchange/framework-v1.json
python -m p3if analyze examples/interchange/framework-v1.json
python -m p3if canonicalize examples/interchange/framework-v1.json --output framework.json
python -m p3if schema --output p3if-interchange-v1.schema.json
```

The installed `p3if` command is equivalent to `python -m p3if`. Use `-` for standard input or output. File output creates a new file, so a failed conversion or a repeated command cannot replace an existing artifact. Invalid input or an I/O failure produces a diagnostic on standard error and exits with status 2.

`validate` checks the declared graph and prints the SHA-256 of its canonical representation. `inspect` reports axis counts, domains, unlinked elements, pair and triple relationship counts, and how often strength and confidence were explicitly reported. It counts distinct triples separately from relationship records because several records may declare the same endpoints. The number of possible triples is the product of the three axis counts. These counts describe the declared graph. Whether an unlinked element or an empty coordinate is a meaningful gap depends on the application.

## Analyze and compare snapshots

Use `p3if analyze SNAPSHOT.json` for a report with each axis's total, linked, and unlinked counts. The report shows declared relationships, distinct observed coordinates, the possible coordinate count, and the unobserved count for each of the three pair spaces and the triple space. A triple contributes to the triple space. A pair coordinate requires its own relationship declaration. Score tallies separate omitted values, explicit `null`, zero, and nonzero values.

Use `p3if compare BEFORE.json AFTER.json` for two snapshots with the same framework ID. The report binds both canonical hashes, reports changed framework fields, and groups additions, removals, and modifications by record type. A relationship is rewired when one of its endpoint fields changes value. A metadata-only change appears as a modified field. Omitted and explicitly null values are distinct field states. One comparison input can be `-` for standard input.

The Python methods are `analyze_interchange(snapshot)` and `compare_interchange(before, after)` in `p3if.interchange_analysis`. Both return typed reports that serialize with `model_dump(mode="json")`. [Measurement definitions and worked examples](manuscript/METHODS.md)

## Wire fields

| Field | Meaning |
| --- | --- |
| `format` | Exactly `p3if.interchange` |
| `version` | The integer `1` |
| `framework` | Stable `id` and `name`, with optional description and JSON metadata |
| `properties` | Properties and their declared measurement, value, or category attributes |
| `processes` | Processes and their declared steps, inputs, outputs, and dependencies |
| `perspectives` | Perspectives and their declared viewpoint, concerns, and constraints |
| `relationships` | Stable relationship IDs and at least two axis-specific endpoint IDs |

The three axis arrays and the relationship array are always present and may be empty. Axis item IDs are unique across the three collections. Each axis item declares its name and domain, with a description where the source provides one. Every relationship endpoint resolves to an item of the named axis. Parent, dependency, related-pattern, and evidence declarations may refer outside the snapshot. Consumers should preserve them as supplied. Process steps are JSON data and carry no authority to execute anything.

Canonical UTF-8 output sorts object keys and sorts the four collections by ID. Other arrays, such as process steps and evidence sources, retain their order. Omitted scores remain omitted. A declared zero remains zero. Duplicate object members, non-finite numbers, malformed UTF-8, wrong-axis references, and invalid or unsupported versions are errors. The reader admits at most 4 MiB, 10,000 elements per axis, and 20,000 relationships, with additional structural depth and value limits.

The JSON Schema describes the wire fields. Cross-collection identity and endpoint validation is part of the P3IF validator. [Published schema](../schemas/p3if-interchange-v1.schema.json) · [Example snapshot](../examples/interchange/framework-v1.json)

## Export and materialize native frameworks

```python
from p3if import P3IFFramework, Process, Property, Relationship
from p3if.interchange import FrameworkIdentity, canonical_bytes, load_interchange
from p3if.interchange_native import framework_from_interchange, interchange_from_framework

native = P3IFFramework()
native.add_pattern(Property(
    id="availability", name="Availability", description="Service reachability", domain="service",
))
native.add_pattern(Process(
    id="restore", name="Restore", description="Recover a service", domain="service",
))
native.add_relationship(Relationship(
    id="restore-availability", property_id="availability", process_id="restore", strength=0.0,
))

identity = FrameworkIdentity(id="service-recovery", name="Service recovery")
snapshot = interchange_from_framework(native, identity)
wire = canonical_bytes(snapshot)
restored = framework_from_interchange(load_interchange(wire))
assert canonical_bytes(interchange_from_framework(restored, identity)) == wire
```

The exporter takes a detached snapshot under the framework lock. Its framework identity is supplied explicitly. Materialization creates a new in-memory framework and checks that re-export preserves the canonical snapshot. It refuses data that the native models would normalize or cannot represent. A legacy document with missing descriptions or viewpoints can still be retained and inspected as wire data.

Use `p3if roundtrip framework.json` to run the same check and write the canonical result.

## Migrate older exports

```sh
python -m p3if migrate legacy.json --id service-recovery --name 'Service recovery' --output framework.json
```

Migration supports the grouped output of `p3if.data.exporters.export_to_json`, the flat `patterns` and `relationships` arrays from `P3IFFramework.export_to_json`, the ID-keyed maps from `P3IFCore.export_framework`, and the grouped `patterns` in the domain library. ID-keyed entries must declare their matching IDs. Domain files must have name lists that match their corresponding pattern lists in order. Migration retains provided fields and places the source domain, version, description, and export metadata under `framework.metadata.legacy_export` where present. It refuses unknown shapes and invalid references. If a previous exporter omitted a field, the migrated snapshot records that omission. The producer can explicitly supply the field later when its source is known.

```sh
python -m p3if migrate data/domains/scienceresearch.json \
  --id p3if.science-research --name 'Science research' --output science-research.json
python -m p3if inspect science-research.json
```
