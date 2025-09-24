"""
Comprehensive unit tests for the P3IF data models.
"""
import unittest
from datetime import datetime, timezone
from pydantic import ValidationError

from p3if_methods.models import (
    Property, Process, Perspective, Relationship,
    PatternType, RelationshipStrength, ConfidenceScore
)


class TestMetadataMixin(unittest.TestCase):
    """Test cases for the MetadataMixin class."""

    def test_metadata_mixin_initialization(self):
        """Test MetadataMixin initialization with default values."""
        mixin = MetadataMixin()
        mixin.id = "test_id"
        mixin.created_at = datetime.now(timezone.utc)
        mixin.updated_at = datetime.now(timezone.utc)

        assert mixin.id == "test_id"
        assert mixin.created_at is not None
        assert mixin.updated_at is not None
        assert mixin.version == "1.0.0"
        assert mixin.parent_id is None
        assert mixin.validation_status == "pending"
        assert mixin.quality_score == 0.5
        assert mixin.confidence == 0.5
        assert mixin.references == []
        assert mixin.related_patterns == []
        assert mixin.tags == []

    def test_metadata_mixin_custom_values(self):
        """Test MetadataMixin initialization with custom values."""
        now = datetime.now(timezone.utc)
        mixin = MetadataMixin(
            id="custom_id",
            created_at=now,
            updated_at=now,
            version="2.0.0",
            parent_id="parent_id",
            validation_status="validated",
            quality_score=0.8,
            confidence=0.9,
            references=["ref1", "ref2"],
            related_patterns=["pattern1", "pattern2"],
            tags=["tag1", "tag2"]
        )

        assert mixin.id == "custom_id"
        assert mixin.created_at == now
        assert mixin.updated_at == now
        assert mixin.version == "2.0.0"
        assert mixin.parent_id == "parent_id"
        assert mixin.validation_status == "validated"
        assert mixin.quality_score == 0.8
        assert mixin.confidence == 0.9
        assert mixin.references == ["ref1", "ref2"]
        assert mixin.related_patterns == ["pattern1", "pattern2"]
        assert mixin.tags == ["tag1", "tag2"]


class TestBasePattern(unittest.TestCase):
    """Test cases for the BasePattern class."""

    def test_base_pattern_initialization(self):
        """Test BasePattern initialization with default values."""
        pattern = Property(
            name="Test Pattern",
            description="Test description",
            domain="test_domain"
        )

        assert pattern.name == "Test Pattern"
        assert pattern.description == "Test description"
        assert pattern.domain == "test_domain"
        assert len(pattern.id) > 0  # ID should be a valid UUID string
        assert pattern.type == PatternType.PROPERTY
        assert isinstance(pattern.created_at, datetime)
        assert isinstance(pattern.updated_at, datetime)
        assert pattern.version == "1.0.0"
        assert pattern.quality_score == 1.0
        assert pattern.confidence == 0.5
        assert pattern.tags == []

    def test_base_pattern_custom_values(self):
        """Test BasePattern initialization with custom values."""
        now = datetime.now(timezone.utc)
        pattern = Property(
            name="Custom Pattern",
            description="Custom description",
            domain="custom_domain",
            id="custom_id",
            created_at=now,
            updated_at=now,
            version="2.0.0",
            parent_id="parent_id",
            validation_status="validated",
            quality_score=0.8,
            confidence=0.9,
            references=["ref1"],
            related_patterns=["pattern1"],
            tags=["tag1", "tag2"]
        )

        assert pattern.name == "Custom Pattern"
        assert pattern.description == "Custom description"
        assert pattern.domain == "custom_domain"
        assert pattern.id == "custom_id"
        assert pattern.type == PatternType.PROPERTY
        assert pattern.created_at == now
        assert pattern.updated_at == now
        assert pattern.version == "2.0.0"
        assert pattern.parent_id == "parent_id"
        assert pattern.validation_status == "validated"
        assert pattern.quality_score == 0.8
        assert pattern.confidence == 0.9
        assert pattern.references == ["ref1"]
        assert pattern.related_patterns == ["pattern1"]
        assert pattern.tags == ["tag1", "tag2"]

    def test_base_pattern_validation_name_required(self):
        """Test that name is required for BasePattern."""
        with pytest.raises(ValidationError):
            Property(description="Test description", domain="test_domain")

    def test_base_pattern_validation_description_required(self):
        """Test that description is required for BasePattern."""
        with pytest.raises(ValidationError):
            Property(name="Test Pattern", domain="test_domain")

    def test_base_pattern_validation_domain_required(self):
        """Test that domain is required for BasePattern."""
        with pytest.raises(ValidationError):
            Property(name="Test Pattern", description="Test description")

    def test_base_pattern_validation_quality_score_range(self):
        """Test that quality_score must be between 0 and 1."""
        with pytest.raises(ValidationError):
            Property(
                name="Test Pattern",
                description="Test description",
                domain="test_domain",
                quality_score=1.5
            )

        with pytest.raises(ValidationError):
            Property(
                name="Test Pattern",
                description="Test description",
                domain="test_domain",
                quality_score=-0.1
            )

    def test_base_pattern_validation_confidence_range(self):
        """Test that confidence must be between 0 and 1."""
        with pytest.raises(ValidationError):
            Property(
                name="Test Pattern",
                description="Test description",
                domain="test_domain",
                confidence=1.5
            )

        with pytest.raises(ValidationError):
            Property(
                name="Test Pattern",
                description="Test description",
                domain="test_domain",
                confidence=-0.1
            )

    def test_base_pattern_str_method(self):
        """Test the string representation of BasePattern."""
        pattern = Property(
            name="Test Pattern",
            description="Test description",
            domain="test_domain"
        )

        str_repr = str(pattern)
        self.assertIn("Test Pattern", str_repr)
        self.assertIn("test_domain", str_repr)
        self.assertIn(pattern.id, str_repr)

    def test_base_pattern_repr_method(self):
        """Test the repr representation of BasePattern."""
        pattern = Property(
            name="Test Pattern",
            description="Test description",
            domain="test_domain"
        )

        repr_str = repr(pattern)
        self.assertIn("Property", repr_str)
        self.assertIn("Test Pattern", repr_str)
        self.assertIn(pattern.id, repr_str)

    def test_base_pattern_equality(self):
        """Test BasePattern equality comparison."""
        pattern1 = Property(
            name="Test Pattern",
            description="Test description",
            domain="test_domain",
            id="test_id"
        )

        pattern2 = Property(
            name="Test Pattern",
            description="Test description",
            domain="test_domain",
            id="test_id"
        )

        pattern3 = Property(
            name="Different Pattern",
            description="Different description",
            domain="different_domain",
            id="different_id"
        )

        self.assertEqual(pattern1, pattern2)
        self.assertNotEqual(pattern1, pattern3)
        self.assertNotEqual(pattern2, pattern3)

    def test_base_pattern_hash(self):
        """Test BasePattern hashing."""
        pattern = Property(
            name="Test Pattern",
            description="Test description",
            domain="test_domain",
            id="test_id"
        )

        # Should be hashable
        hash_value = hash(pattern)
        self.assertIsInstance(hash_value, int)

        # Same patterns should have same hash
        pattern2 = Property(
            name="Test Pattern",
            description="Test description",
            domain="test_domain",
            id="test_id"
        )
        self.assertEqual(hash(pattern), hash(pattern2))


class TestProperty(unittest.TestCase):
    """Test cases for the Property class."""

    def test_property_initialization(self):
        """Test Property initialization."""
        prop = Property(
            name="Test Property",
            description="Test description",
            domain="test_domain",
            property_type="qualitative"
        )

        self.assertEqual(prop.name, "Test Property")
        self.assertEqual(prop.description, "Test description")
        self.assertEqual(prop.domain, "test_domain")
        self.assertEqual(prop.type, PatternType.PROPERTY)
        self.assertIsNone(prop.data_type)
        self.assertIsNone(prop.unit)
        self.assertEqual(prop.allowed_values, [])
        self.assertEqual(prop.quality_score, 1.0)  # Default value from BasePattern

    def test_property_custom_values(self):
        """Test Property initialization with custom values."""
        prop = Property(
            name="Custom Property",
            description="Custom description",
            domain="custom_domain",
            data_type="float",
            unit="kg",
            allowed_values=["value1", "value2"],
            tags=["tag1", "tag2"],
            quality_score=0.8
        )

        self.assertEqual(prop.data_type, "float")
        self.assertEqual(prop.unit, "kg")
        self.assertEqual(prop.allowed_values, ["value1", "value2"])
        self.assertEqual(prop.tags, ["tag1", "tag2"])
        self.assertEqual(prop.quality_score, 0.8)

    def test_property_validation_priority(self):
        """Test Property priority validation."""
        with self.assertRaises(ValidationError):
            Property(
                name="Test Property",
                description="Test description",
                domain="test_domain",
                priority="invalid_priority"
            )


class TestProcess(unittest.TestCase):
    """Test cases for the Process class."""

    def test_process_initialization(self):
        """Test Process initialization."""
        proc = Process(
            name="Test Process",
            description="Test description",
            domain="test_domain"
        )

        self.assertEqual(proc.name, "Test Process")
        self.assertEqual(proc.description, "Test description")
        self.assertEqual(proc.domain, "test_domain")
        self.assertEqual(proc.type, PatternType.PROCESS)
        self.assertEqual(proc.complexity, "medium")
        self.assertEqual(proc.automation_level, "manual")
        self.assertEqual(proc.inputs, [])
        self.assertEqual(proc.outputs, [])
        self.assertIsNone(proc.duration)
        self.assertEqual(proc.prerequisites, [])
        self.assertEqual(proc.dependencies, [])

    def test_process_custom_values(self):
        """Test Process initialization with custom values."""
        proc = Process(
            name="Custom Process",
            description="Custom description",
            domain="custom_domain",
            complexity="high",
            automation_level="high",
            inputs=["input1", "input2"],
            outputs=["output1", "output2"],
            duration="1 hour",
            prerequisites=["prereq1", "prereq2"],
            dependencies=["dep1", "dep2"],
            tags=["tag1", "tag2"],
            quality_score=0.8
        )

        self.assertEqual(proc.complexity, "high")
        self.assertEqual(proc.automation_level, "high")
        self.assertEqual(proc.inputs, ["input1", "input2"])
        self.assertEqual(proc.outputs, ["output1", "output2"])
        self.assertEqual(proc.duration, "1 hour")
        self.assertEqual(proc.prerequisites, ["prereq1", "prereq2"])
        self.assertEqual(proc.dependencies, ["dep1", "dep2"])
        self.assertEqual(proc.tags, ["tag1", "tag2"])
        self.assertEqual(proc.quality_score, 0.8)

    def test_process_validation_complexity(self):
        """Test Process complexity validation."""
        with self.assertRaises(ValidationError):
            Process(
                name="Test Process",
                description="Test description",
                domain="test_domain",
                complexity="invalid_complexity"
            )


class TestPerspective(unittest.TestCase):
    """Test cases for the Perspective class."""

    def test_perspective_initialization(self):
        """Test Perspective initialization."""
        persp = Perspective(
            name="Test Perspective",
            description="Test description",
            domain="test_domain",
            viewpoint="test_viewpoint"
        )

        self.assertEqual(persp.name, "Test Perspective")
        self.assertEqual(persp.description, "Test description")
        self.assertEqual(persp.domain, "test_domain")
        self.assertEqual(persp.type, PatternType.PERSPECTIVE)
        self.assertEqual(persp.viewpoint, "test_viewpoint")
        self.assertEqual(persp.scope, "general")
        self.assertEqual(persp.bias_factor, 0.0)
        self.assertEqual(persp.concerns, [])
        self.assertEqual(persp.constraints, [])
        self.assertIsNone(persp.stakeholder_type)
        self.assertEqual(persp.expertise_level, "intermediate")

    def test_perspective_custom_values(self):
        """Test Perspective initialization with custom values."""
        persp = Perspective(
            name="Custom Perspective",
            description="Custom description",
            domain="custom_domain",
            viewpoint="strategic_viewpoint",
            scope="specific",
            bias_factor=0.3,
            concerns=["concern1", "concern2"],
            constraints=["constraint1", "constraint2"],
            stakeholder_type="external",
            expertise_level="expert",
            tags=["tag1", "tag2"],
            quality_score=0.8
        )

        self.assertEqual(persp.viewpoint, "strategic_viewpoint")
        self.assertEqual(persp.scope, "specific")
        self.assertEqual(persp.bias_factor, 0.3)
        self.assertEqual(persp.concerns, ["concern1", "concern2"])
        self.assertEqual(persp.constraints, ["constraint1", "constraint2"])
        self.assertEqual(persp.stakeholder_type, "external")
        self.assertEqual(persp.expertise_level, "expert")
        self.assertEqual(persp.tags, ["tag1", "tag2"])
        self.assertEqual(persp.quality_score, 0.8)

    def test_perspective_validation_scope(self):
        """Test Perspective scope validation."""
        with self.assertRaises(ValidationError):
            Perspective(
                name="Test Perspective",
                description="Test description",
                domain="test_domain",
                viewpoint="test_viewpoint",
                scope="invalid_scope"
            )

    def test_perspective_validation_expertise_level(self):
        """Test Perspective expertise level validation."""
        with self.assertRaises(ValidationError):
            Perspective(
                name="Test Perspective",
                description="Test description",
                domain="test_domain",
                viewpoint="test_viewpoint",
                expertise_level="invalid_level"
            )



class TestRelationship(unittest.TestCase):
    """Test cases for the Relationship class."""

    def test_relationship_initialization(self):
        """Test Relationship initialization."""
        rel = Relationship(
            property_id="prop_id",
            process_id="proc_id",
            perspective_id="persp_id",
            strength=0.8,
            confidence=0.9
        )

        self.assertEqual(rel.property_id, "prop_id")
        self.assertEqual(rel.process_id, "proc_id")
        self.assertEqual(rel.perspective_id, "persp_id")
        self.assertEqual(rel.strength, 0.8)
        self.assertEqual(rel.confidence, 0.9)
        self.assertEqual(rel.relationship_type, "general")
        self.assertEqual(rel.bidirectional, True)
        self.assertIsNone(rel.direction)
        self.assertIsNone(rel.temporal_context)
        self.assertIsNone(rel.validity_period)
        self.assertEqual(rel.evidence_sources, [])
        self.assertIsNone(rel.validation_method)
        self.assertEqual(rel.assumptions, [])
        self.assertEqual(rel.status, "active")
        self.assertEqual(rel.quality_score, 1.0)

    def test_relationship_custom_values(self):
        """Test Relationship initialization with custom values."""
        rel = Relationship(
            property_id="prop_id",
            process_id="proc_id",
            perspective_id="persp_id",
            strength=0.8,
            confidence=0.9,
            relationship_type="causal",
            direction="unidirectional",
            temporal_context="historical",
            evidence_sources=["source1", "source2"],
            validation_method="automated",
            assumptions=["assumption1", "assumption2"],
            status="deprecated",
            quality_score=0.8
        )

        self.assertEqual(rel.relationship_type, "causal")
        self.assertEqual(rel.direction, "unidirectional")
        self.assertEqual(rel.temporal_context, "historical")
        self.assertIsNone(rel.validity_period)
        self.assertEqual(rel.evidence_sources, ["source1", "source2"])
        self.assertEqual(rel.validation_method, "automated")
        self.assertEqual(rel.assumptions, ["assumption1", "assumption2"])
        self.assertEqual(rel.status, "deprecated")
        self.assertEqual(rel.quality_score, 0.8)

    def test_relationship_validation_insufficient_connections(self):
        """Test Relationship requires at least 2 connections."""
        with self.assertRaises(ValidationError):
            Relationship(
                property_id="prop_id"
                # Missing required second connection
            )

    def test_relationship_validation_relationship_type(self):
        """Test Relationship type validation."""
        with self.assertRaises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                relationship_type="invalid_type"
            )

    def test_relationship_validation_complete(self):
        """Test Relationship with all valid attributes."""
        rel = Relationship(
            property_id="prop_id",
            process_id="proc_id",
            perspective_id="persp_id",
            strength=0.8,
            confidence=0.9,
            relationship_type="causal",
            direction="bidirectional",
            temporal_context="current",
            evidence_sources=["evidence1"],
            validation_method="expert_review",
            assumptions=["assumption1"],
            status="experimental",
            quality_score=0.9
        )

        self.assertEqual(rel.status, "experimental")
        self.assertEqual(rel.relationship_type, "causal")
        self.assertEqual(rel.direction, "bidirectional")
        self.assertEqual(rel.evidence_sources, ["evidence1"])

    def test_relationship_get_connected_patterns(self):
        """Test getting connected patterns from relationship."""
        rel = Relationship(
            property_id="prop_id",
            process_id="proc_id",
            perspective_id="persp_id"
        )

        connected = rel.get_connected_patterns()
        self.assertEqual(connected, ["prop_id", "proc_id", "persp_id"])

    def test_relationship_get_connected_patterns_partial(self):
        """Test getting connected patterns with partial connections."""
        rel = Relationship(
            property_id="prop_id",
            process_id=None,
            perspective_id="persp_id"
        )

        connected = rel.get_connected_patterns()
        self.assertEqual(connected, ["prop_id", "persp_id"])  # None values are filtered out

    def test_relationship_str_method(self):
        """Test the string representation of Relationship."""
        rel = Relationship(
            property_id="prop_id",
            process_id="proc_id",
            perspective_id="persp_id",
            strength=0.8,
            confidence=0.9
        )

        str_repr = str(rel)
        self.assertIn("prop_id", str_repr)
        self.assertIn("proc_id", str_repr)
        self.assertIn("persp_id", str_repr)
        self.assertIn("0.8", str_repr)
        self.assertIn("0.9", str_repr)

    def test_relationship_repr_method(self):
        """Test the repr representation of Relationship."""
        rel = Relationship(
            property_id="prop_id",
            process_id="proc_id",
            perspective_id="persp_id"
        )

        repr_str = repr(rel)
        self.assertIn("Relationship", repr_str)
        self.assertIn("prop_id", repr_str)
        self.assertIn("proc_id", repr_str)
        self.assertIn("persp_id", repr_str)


class TestPatternType(unittest.TestCase):
    """Test cases for the PatternType enum."""

    def test_pattern_type_values(self):
        """Test PatternType enum values."""
        assert PatternType.BASE == "base"
        assert PatternType.PROPERTY == "property"
        assert PatternType.PROCESS == "process"
        assert PatternType.PERSPECTIVE == "perspective"

    def test_pattern_type_uniqueness(self):
        """Test that PatternType values are unique."""
        values = [PatternType.BASE, PatternType.PROPERTY, PatternType.PROCESS, PatternType.PERSPECTIVE]
        assert len(values) == len(set(values))


class TestRelationshipStrength(unittest.TestCase):
    """Test cases for the RelationshipStrength custom type."""

    def test_relationship_strength_valid_values(self):
        """Test valid RelationshipStrength values."""
        # Valid float values should work
        strength1 = RelationshipStrength(0.0)
        strength2 = RelationshipStrength(0.5)
        strength3 = RelationshipStrength(1.0)

        assert float(strength1) == 0.0
        assert float(strength2) == 0.5
        assert float(strength3) == 1.0

    def test_relationship_strength_invalid_values(self):
        """Test invalid RelationshipStrength values."""
        with pytest.raises(ValueError, match="Relationship strength must be between 0 and 1"):
            RelationshipStrength(-0.1)

        with pytest.raises(ValueError, match="Relationship strength must be between 0 and 1"):
            RelationshipStrength(1.1)

    def test_relationship_strength_string_conversion(self):
        """Test string conversion of RelationshipStrength."""
        strength = RelationshipStrength(0.75)
        assert str(strength) == "0.75"
        assert float(strength) == 0.75


class TestConfidenceScore(unittest.TestCase):
    """Test cases for the ConfidenceScore custom type."""

    def test_confidence_score_valid_values(self):
        """Test valid ConfidenceScore values."""
        # Valid float values should work
        confidence1 = ConfidenceScore(0.0)
        confidence2 = ConfidenceScore(0.5)
        confidence3 = ConfidenceScore(1.0)

        assert float(confidence1) == 0.0
        assert float(confidence2) == 0.5
        assert float(confidence3) == 1.0

    def test_confidence_score_invalid_values(self):
        """Test invalid ConfidenceScore values."""
        with pytest.raises(ValueError, match="Confidence score must be between 0 and 1"):
            ConfidenceScore(-0.1)

        with pytest.raises(ValueError, match="Confidence score must be between 0 and 1"):
            ConfidenceScore(1.1)

    def test_confidence_score_string_conversion(self):
        """Test string conversion of ConfidenceScore."""
        confidence = ConfidenceScore(0.85)
        assert str(confidence) == "0.85"
        assert float(confidence) == 0.85


class TestModelIntegration(unittest.TestCase):
    """Integration tests for the data models."""

    def test_pattern_relationship_integration(self):
        """Test integration between patterns and relationships."""
        # Create patterns
        prop = Property(
            name="Test Property",
            description="Test property",
            domain="test_domain",
            property_type="qualitative"
        )

        proc = Process(
            name="Test Process",
            description="Test process",
            domain="test_domain",
            process_type="generic"
        )

        persp = Perspective(
            name="Test Perspective",
            description="Test perspective",
            domain="test_domain",
            perspective_type="analytical"
        )

        # Create relationship
        rel = Relationship(
            property_id=prop.id,
            process_id=proc.id,
            perspective_id=persp.id,
            strength=0.8,
            confidence=0.9,
            relationship_type="correlation"
        )

        # Test that relationship correctly references patterns
        connected_patterns = rel.get_connected_patterns()
        assert prop.id in connected_patterns
        assert proc.id in connected_patterns
        assert persp.id in connected_patterns

        # Test that patterns have correct types
        assert prop.pattern_type == PatternType.PROPERTY
        assert proc.pattern_type == PatternType.PROCESS
        assert persp.pattern_type == PatternType.PERSPECTIVE

    def test_model_validation_integration(self):
        """Test that all models work together with validation."""
        # Create a complete set of patterns and relationships
        properties = []
        processes = []
        perspectives = []
        relationships = []

        # Create 3 of each pattern type
        for i in range(3):
            prop = Property(
                name=f"Property {i}",
                description=f"Test property {i}",
                domain=f"domain_{i}",
                quality_score=0.7 + (i * 0.1)
            )
            properties.append(prop)

            proc = Process(
                name=f"Process {i}",
                description=f"Test process {i}",
                domain=f"domain_{i}",
                quality_score=0.7 + (i * 0.1)
            )
            processes.append(proc)

            persp = Perspective(
                name=f"Perspective {i}",
                description=f"Test perspective {i}",
                domain=f"domain_{i}",
                quality_score=0.7 + (i * 0.1)
            )
            perspectives.append(persp)

        # Create relationships connecting all patterns
        for i in range(3):
            rel = Relationship(
                property_id=properties[i].id,
                process_id=processes[i].id,
                perspective_id=perspectives[i].id,
                strength=0.6 + (i * 0.1),
                confidence=0.8 + (i * 0.05)
            )
            relationships.append(rel)

        # Validate all models were created successfully
        assert len(properties) == 3
        assert len(processes) == 3
        assert len(perspectives) == 3
        assert len(relationships) == 3

        # Test that all quality scores and confidences are within valid ranges
        for prop in properties:
            assert 0 <= prop.quality_score <= 1
            assert 0 <= prop.confidence <= 1

        for proc in processes:
            assert 0 <= proc.quality_score <= 1
            assert 0 <= proc.confidence <= 1

        for persp in perspectives:
            assert 0 <= persp.quality_score <= 1
            assert 0 <= persp.confidence <= 1

        for rel in relationships:
            assert 0 <= rel.strength <= 1
            assert 0 <= rel.confidence <= 1

    def test_model_serialization(self):
        """Test model serialization and deserialization."""
        # Create a pattern with complex data
        prop = Property(
            name="Complex Property",
            description="A property with complex metadata",
            domain="test_domain",
            property_type="quantitative",
            units="meters",
            data_type="float",
            constraints={"min": 0, "max": 100},
            tags=["test", "complex", "quantitative"],
            quality_score=0.85,
            confidence=0.92,
            version="1.2.3",
            references=["ref1", "ref2"],
            related_patterns=["pattern1", "pattern2"]
        )

        # Test serialization
        prop_dict = prop.dict(by_alias=True)
        assert isinstance(prop_dict, dict)
        assert prop_dict["name"] == "Complex Property"
        assert prop_dict["domain"] == "test_domain"
        assert prop_dict["property_type"] == "quantitative"
        assert prop_dict["tags"] == ["test", "complex", "quantitative"]
        assert prop_dict["quality_score"] == 0.85
        assert prop_dict["confidence"] == 0.92

        # Test deserialization
        prop_copy = Property(**prop_dict)
        assert prop_copy.name == prop.name
        assert prop_copy.domain == prop.domain
        assert prop_copy.property_type == prop.property_type
        assert prop_copy.tags == prop.tags
        assert prop_copy.quality_score == prop.quality_score
        assert prop_copy.confidence == prop.confidence

        # Test that they're equal
        assert prop == prop_copy

    def test_model_error_handling(self):
        """Test error handling in models."""
        # Test validation errors with invalid data
        with pytest.raises(ValidationError):
            Property(
                name="",
                description="Test property",
                domain="test_domain"
            )

        with pytest.raises(ValidationError):
            Property(
                name="Test Property",
                description="",
                domain="test_domain"
            )

        with pytest.raises(ValidationError):
            Property(
                name="Test Property",
                description="Test description",
                domain=""
            )

        with pytest.raises(ValidationError):
            Process(
                name="Test Process",
                description="Test description",
                domain="test_domain",
                process_type="invalid_type"
            )

        with pytest.raises(ValidationError):
            Perspective(
                name="Test Perspective",
                description="Test description",
                domain="test_domain",
                perspective_type="invalid_type"
            )

        with pytest.raises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                strength=1.5,
                confidence=0.9
            )

        with pytest.raises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                strength=0.8,
                confidence=1.5
            )
