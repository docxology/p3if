# Background

An interchange snapshot gives each declared entity a type and an identity.
A relationship specifies which endpoints it refers to. Distinct
relationships can share a coordinate. A relationship occupying a triple
contributes to the triple space. An independently declared pair occupies
its own pair space.

The snapshots use JSON for typed fields and presence information. A field
can be omitted, carry a null, or report a value such as zero. JSON defines
the wire types [@rfc8259]. P3IF imposes its own validation and stable
serialization rules for comparing framework snapshots.
