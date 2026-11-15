"""Validate held-out keys, cite exact lexical JSON values, and derive audit math.

Uses only Python's standard library and supplied raw snapshots. It never loads
or runs the P3IF case builder, audit, transition, or evaluation harness.
"""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from math import prod
from pathlib import Path
import re

AXES = ("property", "process", "perspective")
KINDS = ("framework", *AXES, "relationship")
COLLECTIONS = dict(zip(KINDS[1:], ("properties", "processes", "perspectives", "relationships")))
SCORES = ("strength", "confidence")
FLOAT_FIELDS = {
    "properties": ("range_min", "range_max", "quality_score"),
    "processes": ("quality_score",),
    "perspectives": ("bias_factor", "quality_score"),
    "relationships": (*SCORES, "quality_score"),
}
SIDES = ("before", "after")
SPACES = (*combinations(AXES, 2), AXES)
WHITESPACE = re.compile(r"[\x20\t\r\n]*")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "Duplicate object member")
    return result


def reject_constant(constant):
    raise ValueError(f"Non-JSON numeric literal: {constant}")


DECODER = json.JSONDecoder(object_pairs_hook=unique, parse_constant=reject_constant)


def compact(obj):
    return json.dumps(
        obj, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    )


def decode(text, start):
    return DECODER.raw_decode(text, skip_whitespace(text, start))


def skip_whitespace(text, index):
    return WHITESPACE.match(text, index).end()


def consume(text, index, token):
    at = skip_whitespace(text, index)
    require(text[at : at + len(token)] == token, f"Expected JSON separator {token!r} at {at}")
    return at + len(token)


def lexical_values(raw):
    """Locate a complete source object and each direct array entry without text matching."""
    text = raw.decode("utf-8")
    document = DECODER.decode(text)
    located = {}
    index = consume(text, 0, "{")
    for ordinal, field in enumerate(document):
        if ordinal:
            index = consume(text, index, ",")
        key, index = decode(text, index)
        require(key == field, "Document traversal changed object order")
        start = skip_whitespace(text, consume(text, index, ":"))
        if field in COLLECTIONS.values():
            index = consume(text, start, "[")
            for item_index, reference in enumerate(document[field]):
                if item_index:
                    index = consume(text, index, ",")
                item_start = skip_whitespace(text, index)
                value, index = decode(text, item_start)
                require(compact(value) == compact(reference), "Array item traversal mismatch")
                located[f"/{field}/{item_index}"] = (item_start, index)
            index = consume(text, index, "]")
        else:
            value, index = decode(text, start)
            require(compact(value) == compact(document[field]), "Field traversal mismatch")
            if field == "framework":
                located["/framework"] = (start, index)
    require(skip_whitespace(text, consume(text, index, "}")) == len(text), "Extra input")
    return document, located, text


def declarations(document):
    """Index wire rows by kind and stable ID, retaining the original location."""
    rows = {("framework", document["framework"]["id"]): (document["framework"], "/framework")}
    for kind, field in COLLECTIONS.items():
        for index, record in enumerate(document[field]):
            key = kind, record["id"]
            require(key not in rows, f"Duplicate retained identity: {key}")
            rows[key] = (record, f"/{field}/{index}")
    return rows


def coordinate(kind, row):
    return [
        row.get(axis + "_id") if kind == "relationship" else row["id"] if kind == axis else None
        for axis in AXES
    ]


def metric(row, score):
    if score not in row:
        return "omitted"
    if row[score] is None:
        return "explicit_null"
    return "reported_zero" if row[score] == 0 else "reported_nonzero"


def side(kind, row):
    if row is None:
        return None
    return {
        "coordinate": coordinate(kind, row),
        "scores": {score: metric(row, score) for score in SCORES}
        if kind == "relationship"
        else None,
    }


def event_set(before, after):
    events = {}
    for kind, identity in before.keys() | after.keys():
        left = before.get((kind, identity), (None, None))[0]
        right = after.get((kind, identity), (None, None))[0]
        if left is None:
            operation, fields = "added", []
        elif right is None:
            operation, fields = "removed", []
        else:
            fields = [
                key
                for key in sorted(left.keys() | right.keys())
                if key not in left or key not in right or compact(left[key]) != compact(right[key])
            ]
            if not fields:
                continue
            operation = "modified"
        events[kind, identity] = {
            "kind": kind,
            "id": identity,
            "change": operation,
            "fields": fields,
            "rewired": kind == "relationship"
            and operation == "modified"
            and coordinate(kind, left) != coordinate(kind, right),
            "before": side(kind, left),
            "after": side(kind, right),
        }
    return events


def stable_bytes(document):
    ordered = {**document}
    for field in COLLECTIONS.values():
        rows = [
            {
                key: float(value) if key in FLOAT_FIELDS[field] and value is not None else value
                for key, value in row.items()
            }
            for row in document[field]
        ]
        ordered[field] = sorted(rows, key=lambda row: row["id"])
    return (compact(ordered) + "\n").encode("utf-8")


def exact_span(source, text, bounds, record, pointer):
    lo, hi = bounds[pointer]
    quote = text[lo:hi]
    require(
        compact(DECODER.decode(quote)) == compact(record), f"Exact token does not match {pointer}"
    )
    start = len(text[:lo].encode("utf-8"))
    end = start + len(quote.encode("utf-8"))
    require(source[start:end] == quote.encode("utf-8"), f"Byte span does not match {pointer}")
    return {
        "source_sha256": digest(source),
        "pointer": pointer,
        "start_char": lo,
        "end_char": hi,
        "start_byte": start,
        "end_byte": end,
        "quote_sha256": digest(source[start:end]),
    }


def snapshot_analysis(document, semantic_sha256):
    memberships = {axis: {row["id"] for row in document[COLLECTIONS[axis]]} for axis in AXES}
    require(
        sum(map(len, memberships.values())) == len(set.union(*memberships.values())),
        "Axis IDs must be disjoint",
    )
    linked = {axis: set() for axis in AXES}
    relationships = {space: [] for space in SPACES}
    rows = document["relationships"]
    for row in rows:
        endpoints = {axis: row[axis + "_id"] for axis in AXES if row.get(axis + "_id") is not None}
        require(len(endpoints) >= 2, "Relationship declares fewer than two endpoints")
        for axis, endpoint in endpoints.items():
            require(endpoint in memberships[axis], f"Out-of-axis endpoint for {row['id']}")
            linked[axis].add(endpoint)
        relationships[tuple(endpoints)].append(tuple(endpoints.values()))
    axes = [
        {
            "axis": axis,
            "total": len(memberships[axis]),
            "linked": len(linked[axis]),
            "unlinked": len(memberships[axis] - linked[axis]),
        }
        for axis in AXES
    ]
    spaces = []
    for space, points in relationships.items():
        observed, possible = len(set(points)), prod(len(memberships[axis]) for axis in space)
        spaces.append(
            {
                "axes": list(space),
                "relationships": len(points),
                "observed": observed,
                "possible": possible,
                "unobserved": possible - observed,
            }
        )
    coverage = {}
    for score in SCORES:
        counts = Counter(metric(row, score) for row in rows)
        omitted, null, zero, nonzero = (
            counts[key] for key in ("omitted", "explicit_null", "reported_zero", "reported_nonzero")
        )
        coverage[score] = {
            "omitted": omitted,
            "null": null,
            "missing": omitted + null,
            "zero": zero,
            "nonzero": nonzero,
            "reported": zero + nonzero,
        }
    return {
        "framework_id": document["framework"]["id"],
        "semantic_sha256": semantic_sha256,
        "axes": axes,
        "spaces": spaces,
        "relationship_count": len(rows),
        **coverage,
    }


def subtract(before, after):
    return {
        key: value - before[key] if isinstance(value, int) else value
        for key, value in after.items()
    }


def audit_math(raw, analyses, classification, events):
    first, second = (analyses[name] for name in SIDES)
    changes = []
    for kind in KINDS:
        per_kind = [event for event in events.values() if event["kind"] == kind]
        counts = Counter(event["change"] for event in per_kind)
        changes.append(
            {
                "kind": kind,
                **{key: counts[key] for key in ("added", "removed", "modified")},
                "rewired": sum(event["rewired"] for event in per_kind),
            }
        )
    return {
        "method": "p3if.snapshot-audit.v1",
        "framework_id": first["framework_id"],
        "classification": classification,
        **{
            name: {
                "source_sha256": digest(raw[name]),
                "source_bytes": len(raw[name]),
                "analysis": analyses[name],
            }
            for name in SIDES
        },
        "framework_fields": events.get(("framework", first["framework_id"]), {"fields": []})[
            "fields"
        ],
        "changes": changes,
        "axes": [subtract(left, right) for left, right in zip(first["axes"], second["axes"])],
        "coordinates": [
            subtract(left, right) for left, right in zip(first["spaces"], second["spaces"])
        ],
        **{score: subtract(first[score], second[score]) for score in SCORES},
        "relationship_delta": second["relationship_count"] - first["relationship_count"],
    }


def build_reference(case, case_root):
    identity = case["case_id"]
    folder = case_root / identity
    require(
        {path.name for path in folder.iterdir()} == {"before.json", "after.json"},
        f"Unexpected case files: {identity}",
    )
    raw = {name: (folder / f"{name}.json").read_bytes() for name in SIDES}
    parsed = {name: lexical_values(data) for name, data in raw.items()}
    docs = {name: parsed[name][0] for name in SIDES}
    require(
        all(doc["format"] == "p3if.interchange" and doc["version"] == 1 for doc in docs.values()),
        f"Unexpected wire envelope: {identity}",
    )
    records = {name: declarations(document) for name, document in docs.items()}
    events = event_set(*records.values())
    semantic_sha = {name: digest(stable_bytes(document)) for name, document in docs.items()}
    classification = (
        "identical_bytes"
        if raw["before"] == raw["after"]
        else "encoding_only"
        if len(set(semantic_sha.values())) == 1
        else "declared_change"
    )
    require(
        bool(events) == (classification == "declared_change"),
        f"Classification/event disagreement: {identity}",
    )
    analyses = {name: snapshot_analysis(doc, semantic_sha[name]) for name, doc in docs.items()}
    citations = {}
    for key in events:
        citations[key] = {}
        for name in SIDES:
            if key not in records[name]:
                citations[key][name] = None
                continue
            _, bounds, text = parsed[name]
            citations[key][name] = exact_span(raw[name], text, bounds, *records[name][key])
    return (
        raw,
        docs,
        records,
        {
            "classification": classification,
            "events": events,
            "citations": citations,
            "audit": audit_math(raw, analyses, classification, events),
        },
    )


def fixture_baseline(fixtures, domain, context):
    path = fixtures / domain["fixture"]
    raw = path.read_bytes()
    require(digest(raw) == domain["fixture_sha256"], f"Fixture digest mismatch: {path.name}")
    fixture = DECODER.decode(raw.decode("utf-8"))
    legacy_labels = {
        key: fixture[key]
        for key in ("domain", "version", "description", "metadata", "framework_metadata")
        if key in fixture
    }
    framework = {**domain["framework"], "description": context}
    framework["metadata"] = {**(framework.get("metadata") or {}), "legacy_export": legacy_labels}
    return {
        "format": "p3if.interchange",
        "version": 1,
        "framework": framework,
        **{
            field: sorted(fixture["patterns"][field], key=lambda row: row["id"])
            for field in COLLECTIONS.values()
            if field != "relationships"
        },
        "relationships": sorted(fixture["relationships"], key=lambda row: row["id"]),
    }


def apply_declared_edits(document, edits):
    """Replay external intervention declarations directly over the indexed candidates."""
    changed = set()
    for edit in edits:
        kind, identity, operation = (edit[key] for key in ("kind", "id", "change"))
        key = kind, identity
        require(key not in changed, f"Duplicate intervention on {key}")
        changed.add(key)
        index = declarations(document)
        values, omissions = edit.get("set", {}), set(edit.get("omit", []))
        require(
            not (values.keys() & omissions) and "id" not in omissions, f"Ambiguous fields in {key}"
        )
        if operation == "added":
            require(
                kind != "framework" and key not in index and values["id"] == identity,
                f"Invalid added record {key}",
            )
            document[COLLECTIONS[kind]].append(values)
            continue
        actual, pointer = index[key]
        if operation == "removed":
            require(kind != "framework" and not values and not omissions, f"Invalid removal {key}")
            del document[COLLECTIONS[kind]][int(pointer.rsplit("/", 1)[1])]
            continue
        require(operation == "modified" and "id" not in values, f"Invalid modification {key}")
        require(
            omissions <= actual.keys()
            and all(
                field not in actual or compact(value) != compact(actual[field])
                for field, value in values.items()
            ),
            f"No-op predeclared edit {key}",
        )
        actual = {field: value for field, value in actual.items() if field not in omissions}
        actual.update(values)
        if kind == "framework":
            document["framework"] = actual
        else:
            document[COLLECTIONS[kind]][int(pointer.rsplit("/", 1)[1])] = actual
    return changed


def verify_lineage(raw, docs, declared, spec, fixtures):
    reference = fixture_baseline(
        fixtures,
        spec["domains"][declared["domain"]],
        spec["context_template"].format(case_id=declared["case_id"]),
    )
    seed_targets = apply_declared_edits(reference, declared["seed_edits"])
    require(
        compact(reference) == compact(docs["before"]),
        f"Before does not follow public recipe: {declared['case_id']}",
    )
    edit_targets = apply_declared_edits(reference, declared["edits"])
    encoding = declared["after_encoding"]
    for field in encoding["reverse"]:
        reference[field].reverse()
    require(
        compact(reference) == compact(docs["after"]),
        f"After does not follow public recipe: {declared['case_id']}",
    )
    for name in SIDES:
        ascii_only = name == "after" and encoding["ascii"]
        serialized = json.dumps(
            docs[name], ensure_ascii=ascii_only, sort_keys=True, indent=2, allow_nan=False
        )
        require(
            (serialized + "\n").encode("utf-8") == raw[name],
            f"Source encoding differs from recipe: {declared['case_id']} {name}",
        )
    return seed_targets, edit_targets


def keyed(rows, label):
    result = {(row["kind"], row["id"]): {**row} for row in rows}
    require(len(rows) == len(result), f"Duplicate {label} entry")
    return result


def write_json(path, data):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
        )


def check(root, spec_path, expected_manifest, fixtures, pilot_manifest, summary_path, audit_path):
    generated = (root / "case-manifest.json").read_bytes()
    registered = expected_manifest.read_bytes()
    specification = spec_path.read_bytes()
    require(generated == registered, "Generated manifest differs from the registered file")
    manifest = DECODER.decode(registered.decode("utf-8"))
    spec = DECODER.decode(specification.decode("utf-8"))
    require(
        manifest["schema_version"] == "p3if.held-out-case-manifest.v1", "Unexpected manifest schema"
    )
    require(
        spec["schema_version"] == "p3if.held-out-case-spec.v1", "Unexpected specification schema"
    )
    require(manifest["specification_sha256"] == digest(specification), "Unbound specification")
    require(manifest["domains"] == spec["domains"], "Spec and manifest disagree on domains")
    case_ids = [row["case_id"] for row in manifest["cases"]]
    require(
        case_ids == [f"H{number:02d}" for number in range(1, 17)],
        "The expected 16 case IDs were changed",
    )
    require(
        case_ids == [row["case_id"] for row in spec["cases"]],
        "Spec and manifest disagree on case IDs",
    )
    require(
        {path.name for path in root.iterdir()} == {"case-manifest.json", *case_ids},
        "Unexpected case directory members",
    )
    pilot = DECODER.decode(pilot_manifest.read_text(encoding="utf-8"))
    pilot_targets = {event["id"] for row in pilot["cases"] for event in row["expected"]["events"]}
    summary = Counter()
    features_per_domain = {}
    case_rows, audit_rows = [], {}
    for case, declared in zip(manifest["cases"], spec["cases"]):
        identity, domain, intervention = (
            case[key] for key in ("case_id", "domain", "intervention")
        )
        require(
            (domain, intervention) == (declared["domain"], declared["intervention"]),
            f"Spec and manifest disagree on {identity}",
        )
        summary["cases"] += 1
        features = features_per_domain.setdefault(domain, Counter())
        features[f"case_{intervention}"] += 1
        raw, docs, records, reference = build_reference(case, root)
        seed_targets, edit_targets = verify_lineage(raw, docs, declared, spec, fixtures)
        require(
            not (({key[1] for key in seed_targets | edit_targets} & pilot_targets)),
            f"Pilot target reused for {identity}",
        )
        events, citations = reference["events"], reference["citations"]
        require(
            edit_targets == events.keys(),
            f"Independent events disagree with declared targets for {identity}",
        )
        expected = case["expected"]
        require(
            expected["case_id"] == identity
            and expected["classification"] == reference["classification"],
            f"Wrong answer classification for {identity}",
        )
        require(
            keyed(expected["events"], "event") == events,
            f"Independent events disagree with registered key for {identity}",
        )
        expected_spans = {
            key: {name: item[name] for name in SIDES}
            for key, item in keyed(case["citations"], "citation").items()
        }
        require(expected_spans == citations, f"Wrong pointer or lexical quote span for {identity}")
        evidence = Counter()
        for name in SIDES:
            require(
                digest(raw[name]) == case[f"{name}_sha256"],
                f"Source digest mismatch for {identity} {name}",
            )
            summary["sources"] += 1
        for key, event in events.items():
            summary["events"] += 1
            features[f"events_{event['kind']}_{event['change']}"] += 1
            if event["rewired"]:
                features["rewired"] += 1
            if event["kind"] == "relationship" and event["before"] and event["after"]:
                for score in SCORES:
                    previous, current = (event[name]["scores"][score] for name in SIDES)
                    if previous != current:
                        features[f"{score}_{previous}_to_{current}"] += 1
            first, second = (citations[key][name] for name in SIDES)
            if first and second and first["pointer"] != second["pointer"]:
                evidence["pointer_shifts"] += 1
            for source in (first, second):
                if source is None:
                    evidence["absent_sides"] += 1
                else:
                    evidence["exact_spans"] += 1
                    if (
                        source["start_char"] != source["start_byte"]
                        or source["end_char"] != source["end_byte"]
                    ):
                        evidence["unicode_offset_divergences"] += 1
        if reference["classification"] == "encoding_only":
            require(
                not events
                and raw["before"] != raw["after"]
                and any(
                    compact(docs["before"][group]) != compact(docs["after"][group])
                    for group in COLLECTIONS.values()
                ),
                f"Weak encoding control: {identity}",
            )
            require(
                all(ord(char) < 128 for char in raw["after"].decode("utf-8"))
                and any(ord(char) > 127 for char in raw["before"].decode("utf-8")),
                f"Missing alternate Unicode escape representation: {identity}",
            )
        summary.update(evidence)
        case_rows.append(
            {
                "case_id": identity,
                "domain": domain,
                "intervention": intervention,
                "classification": reference["classification"],
                "events": len(events),
                **{
                    key: evidence[key]
                    for key in (
                        "exact_spans",
                        "absent_sides",
                        "pointer_shifts",
                        "unicode_offset_divergences",
                    )
                },
            }
        )
        audit_rows[identity] = reference["audit"]
    require(
        set(features_per_domain) == {"ScienceResearch", "MathEducation"},
        "Unexpected domain identities",
    )
    counts = Counter(row["domain"] for row in case_rows)
    require(set(counts.values()) == {8}, "Expected eight cases per domain")
    families = {
        domain: {
            feature[5:]: count for feature, count in features.items() if feature.startswith("case_")
        }
        for domain, features in features_per_domain.items()
    }
    require(
        len(families["ScienceResearch"]) == 8
        and families["ScienceResearch"] == families["MathEducation"],
        "Case families are not balanced across domains",
    )
    require(
        all(
            summary[key]
            for key in (
                "exact_spans",
                "unicode_offset_divergences",
                "pointer_shifts",
                "absent_sides",
            )
        ),
        "An intended citation challenge is absent",
    )
    summary_doc = {
        "method": "p3if.held-out-independent-source-check.v1",
        "specification_sha256": digest(specification),
        "case_manifest_sha256": digest(registered),
        "pilot_case_manifest_sha256": digest(pilot_manifest.read_bytes()),
        "pilot_target_id_overlap": 0,
        "implementation": "Python standard library and independent raw JSON parsing",
        "summary": dict(summary),
        "families": families,
        "feature_counts_by_domain": {
            key: dict(value) for key, value in features_per_domain.items()
        },
        "cases": case_rows,
    }
    write_json(summary_path, summary_doc)
    write_json(audit_path, {"case_manifest_sha256": digest(registered), "cases": audit_rows})
    print(compact(summary_doc["summary"]))


def main():
    """Write the raw-source verification receipt and independent audit reference."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_root", type=Path, help="Generated case directory")
    parser.add_argument("summary_output", type=Path, help="New verification receipt file")
    parser.add_argument(
        "audit_reference_output", type=Path, help="New independent audit reference file"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    docs = root / "docs/manuscript"
    check(
        args.case_root,
        docs / "held-out-case-spec.json",
        docs / "held-out-case-manifest.json",
        root / "data/domains",
        docs / "reviewer-study-case-manifest.json",
        args.summary_output,
        args.audit_reference_output,
    )


if __name__ == "__main__":
    main()
