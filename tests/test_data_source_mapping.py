"""Tests for explicit source-column mapping."""
import pytest

from src.data.source_mapping import MappingSpec


def test_mapping_validates_and_normalizes_explicit_columns():
    spec = MappingSpec({"PATNO": "source_participant_id", "EVENT_ID": "source_visit"}, frozenset({"source_participant_id"}))
    assert spec.normalize_record({"PATNO": "001", "EVENT_ID": "BL"}) == {
        "source_participant_id": "001", "source_visit": "BL"
    }


def test_mapping_rejects_missing_source_column():
    spec = MappingSpec({"PATNO": "participant_id"}, frozenset({"participant_id"}))
    with pytest.raises(ValueError, match="Mapped source columns"):
        spec.validate(["SUBJECT"])


def test_mapping_rejects_duplicate_target():
    spec = MappingSpec({"A": "x", "B": "x"}, frozenset({"x"}))
    with pytest.raises(ValueError, match="same target"):
        spec.validate(["A", "B"])


def test_mapping_rejects_unmapped_required_target():
    spec = MappingSpec({"A": "x"}, frozenset({"x", "y"}))
    with pytest.raises(ValueError, match="Required normalized targets"):
        spec.validate(["A"])
