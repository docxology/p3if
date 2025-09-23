"""
Comprehensive unit tests for the P3IF data models.
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from core.models import (
    BasePattern,
    Property,
    Process,
    Perspective,
    Relationship,
    PatternType,
    RelationshipStrength,
    ConfidenceScore,
    MetadataMixin
)


class TestMetadataMixin:
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


class TestBasePattern:
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
        assert "Test Pattern" in str_repr
        assert "test_domain" in str_repr
        assert pattern.id in str_repr

    def test_base_pattern_repr_method(self):
        """Test the repr representation of BasePattern."""
        pattern = Property(
            name="Test Pattern",
            description="Test description",
            domain="test_domain"
        )

        repr_str = repr(pattern)
        assert "Property" in repr_str
        assert "Test Pattern" in repr_str
        assert pattern.id in repr_str

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

        assert pattern1 == pattern2
        assert pattern1 != pattern3
        assert pattern2 != pattern3

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
        assert isinstance(hash_value, int)

        # Same patterns should have same hash
        pattern2 = Property(
            name="Test Pattern",
            description="Test description",
            domain="test_domain",
            id="test_id"
        )
        assert hash(pattern) == hash(pattern2)


class TestProperty:
    """Test cases for the Property class."""

    def test_property_initialization(self):
        """Test Property initialization."""
        prop = Property(
            name="Test Property",
            description="Test description",
            domain="test_domain",
            property_type="qualitative"
        )

        assert prop.name == "Test Property"
        assert prop.description == "Test description"
        assert prop.domain == "test_domain"
        assert prop.pattern_type == PatternType.PROPERTY
        assert prop.property_type == "qualitative"
        assert prop.units is None
        assert prop.data_type == "string"
        assert prop.constraints == {}

    def test_property_custom_values(self):
        """Test Property initialization with custom values."""
        prop = Property(
            name="Custom Property",
            description="Custom description",
            domain="custom_domain",
            property_type="quantitative",
            units="kg",
            data_type="float",
            constraints={"min": 0, "max": 100},
            tags=["tag1", "tag2"],
            quality_score=0.8,
            confidence=0.9
        )

        assert prop.property_type == "quantitative"
        assert prop.units == "kg"
        assert prop.data_type == "float"
        assert prop.constraints == {"min": 0, "max": 100}
        assert prop.tags == ["tag1", "tag2"]
        assert prop.quality_score == 0.8
        assert prop.confidence == 0.9

    def test_property_validation_property_type(self):
        """Test Property type validation."""
        with pytest.raises(ValidationError):
            Property(
                name="Test Property",
                description="Test description",
                domain="test_domain",
                property_type="invalid_type"
            )

    def test_property_validation_data_type(self):
        """Test Property data_type validation."""
        with pytest.raises(ValidationError):
            Property(
                name="Test Property",
                description="Test description",
                domain="test_domain",
                data_type="invalid_type"
            )


class TestProcess:
    """Test cases for the Process class."""

    def test_process_initialization(self):
        """Test Process initialization."""
        proc = Process(
            name="Test Process",
            description="Test description",
            domain="test_domain"
        )

        assert proc.name == "Test Process"
        assert proc.description == "Test description"
        assert proc.domain == "test_domain"
        assert proc.pattern_type == PatternType.PROCESS
        assert proc.process_type == "generic"
        assert proc.inputs == []
        assert proc.outputs == []
        assert proc.duration is None
        assert proc.frequency is None
        assert proc.resources == []

    def test_process_custom_values(self):
        """Test Process initialization with custom values."""
        proc = Process(
            name="Custom Process",
            description="Custom description",
            domain="custom_domain",
            process_type="batch",
            inputs=["input1", "input2"],
            outputs=["output1", "output2"],
            duration=3600,  # 1 hour
            frequency="daily",
            resources=["resource1", "resource2"],
            tags=["tag1", "tag2"],
            quality_score=0.8,
            confidence=0.9
        )

        assert proc.process_type == "batch"
        assert proc.inputs == ["input1", "input2"]
        assert proc.outputs == ["output1", "output2"]
        assert proc.duration == 3600
        assert proc.frequency == "daily"
        assert proc.resources == ["resource1", "resource2"]
        assert proc.tags == ["tag1", "tag2"]
        assert proc.quality_score == 0.8
        assert proc.confidence == 0.9

    def test_process_validation_process_type(self):
        """Test Process type validation."""
        with pytest.raises(ValidationError):
            Process(
                name="Test Process",
                description="Test description",
                domain="test_domain",
                process_type="invalid_type"
            )


class TestPerspective:
    """Test cases for the Perspective class."""

    def test_perspective_initialization(self):
        """Test Perspective initialization."""
        persp = Perspective(
            name="Test Perspective",
            description="Test description",
            domain="test_domain"
        )

        assert persp.name == "Test Perspective"
        assert persp.description == "Test description"
        assert persp.domain == "test_domain"
        assert persp.pattern_type == PatternType.PERSPECTIVE
        assert persp.perspective_type == "analytical"
        assert persp.scope == "general"
        assert persp.timeframe == "current"
        assert persp.stakeholders == []
        assert persp.assumptions == []
        assert persp.methodology == "qualitative"

    def test_perspective_custom_values(self):
        """Test Perspective initialization with custom values."""
        persp = Perspective(
            name="Custom Perspective",
            description="Custom description",
            domain="custom_domain",
            perspective_type="strategic",
            scope="specific",
            timeframe="long_term",
            stakeholders=["stakeholder1", "stakeholder2"],
            assumptions=["assumption1", "assumption2"],
            methodology="quantitative",
            tags=["tag1", "tag2"],
            quality_score=0.8,
            confidence=0.9
        )

        assert persp.perspective_type == "strategic"
        assert persp.scope == "specific"
        assert persp.timeframe == "long_term"
        assert persp.stakeholders == ["stakeholder1", "stakeholder2"]
        assert persp.assumptions == ["assumption1", "assumption2"]
        assert persp.methodology == "quantitative"
        assert persp.tags == ["tag1", "tag2"]
        assert persp.quality_score == 0.8
        assert persp.confidence == 0.9

    def test_perspective_validation_perspective_type(self):
        """Test Perspective type validation."""
        with pytest.raises(ValidationError):
            Perspective(
                name="Test Perspective",
                description="Test description",
                domain="test_domain",
                perspective_type="invalid_type"
            )

    def test_perspective_validation_scope(self):
        """Test Perspective scope validation."""
        with pytest.raises(ValidationError):
            Perspective(
                name="Test Perspective",
                description="Test description",
                domain="test_domain",
                scope="invalid_scope"
            )

    def test_perspective_validation_timeframe(self):
        """Test Perspective timeframe validation."""
        with pytest.raises(ValidationError):
            Perspective(
                name="Test Perspective",
                description="Test description",
                domain="test_domain",
                timeframe="invalid_timeframe"
            )

    def test_perspective_validation_methodology(self):
        """Test Perspective methodology validation."""
        with pytest.raises(ValidationError):
            Perspective(
                name="Test Perspective",
                description="Test description",
                domain="test_domain",
                methodology="invalid_methodology"
            )


class TestRelationship:
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

        assert rel.property_id == "prop_id"
        assert rel.process_id == "proc_id"
        assert rel.perspective_id == "persp_id"
        assert rel.strength == 0.8
        assert rel.confidence == 0.9
        assert rel.relationship_type == "correlation"
        assert rel.direction == "bidirectional"
        assert rel.temporal_context == "current"
        assert rel.validity_period == "current"
        assert rel.evidence_sources == []
        assert rel.validation_method == "manual"
        assert rel.assumptions == []
        assert rel.status == "active"
        assert rel.quality_score == 0.5

    def test_relationship_custom_values(self):
        """Test Relationship initialization with custom values."""
        rel = Relationship(
            property_id="prop_id",
            process_id="proc_id",
            perspective_id="persp_id",
            strength=0.8,
            confidence=0.9,
            relationship_type="causation",
            direction="unidirectional",
            temporal_context="historical",
            validity_period="2024-01-01T00:00:00Z/2024-12-31T23:59:59Z",
            evidence_sources=["source1", "source2"],
            validation_method="automated",
            assumptions=["assumption1", "assumption2"],
            status="deprecated",
            quality_score=0.8
        )

        assert rel.relationship_type == "causation"
        assert rel.direction == "unidirectional"
        assert rel.temporal_context == "historical"
        assert rel.validity_period == "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z"
        assert rel.evidence_sources == ["source1", "source2"]
        assert rel.validation_method == "automated"
        assert rel.assumptions == ["assumption1", "assumption2"]
        assert rel.status == "deprecated"
        assert rel.quality_score == 0.8

    def test_relationship_validation_strength_range(self):
        """Test Relationship strength validation."""
        with pytest.raises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                strength=1.5
            )

        with pytest.raises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                strength=-0.1
            )

    def test_relationship_validation_confidence_range(self):
        """Test Relationship confidence validation."""
        with pytest.raises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                confidence=1.5
            )

        with pytest.raises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                confidence=-0.1
            )

    def test_relationship_validation_relationship_type(self):
        """Test Relationship type validation."""
        with pytest.raises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                relationship_type="invalid_type"
            )

    def test_relationship_validation_direction(self):
        """Test Relationship direction validation."""
        with pytest.raises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                direction="invalid_direction"
            )

    def test_relationship_validation_status(self):
        """Test Relationship status validation."""
        with pytest.raises(ValidationError):
            Relationship(
                property_id="prop_id",
                process_id="proc_id",
                perspective_id="persp_id",
                status="invalid_status"
            )

    def test_relationship_get_connected_patterns(self):
        """Test getting connected patterns from relationship."""
        rel = Relationship(
            property_id="prop_id",
            process_id="proc_id",
            perspective_id="persp_id"
        )

        connected = rel.get_connected_patterns()
        assert connected == ["prop_id", "proc_id", "persp_id"]

    def test_relationship_get_connected_patterns_partial(self):
        """Test getting connected patterns with partial connections."""
        rel = Relationship(
            property_id="prop_id",
            process_id=None,
            perspective_id="persp_id"
        )

        connected = rel.get_connected_patterns()
        assert connected == ["prop_id", None, "persp_id"]

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
        assert "prop_id" in str_repr
        assert "proc_id" in str_repr
        assert "persp_id" in str_repr
        assert "0.8" in str_repr
        assert "0.9" in str_repr

    def test_relationship_repr_method(self):
        """Test the repr representation of Relationship."""
        rel = Relationship(
            property_id="prop_id",
            process_id="proc_id",
            perspective_id="persp_id"
        )

        repr_str = repr(rel)
        assert "Relationship" in repr_str
        assert "prop_id" in repr_str
        assert "proc_id" in repr_str
        assert "persp_id" in repr_str


class TestPatternType:
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


class TestRelationshipStrength:
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


class TestConfidenceScore:
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


class TestModelIntegration:
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
