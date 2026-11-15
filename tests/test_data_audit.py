"""Synthetic tests for aggregate CSV key-grain and relationship audits."""
import pytest

from src.data.audit import audit_csv_keys, audit_csv_relationship


def test_audit_csv_keys_reports_duplicates_and_missing_without_values(tmp_path):
    path = tmp_path / "table.csv"
    path.write_text(
        "PATNO,EVENT_ID,IMAGE_ID\n001,BL,I1\n001,BL,I2\n002,,I3\n",
        encoding="utf-8",
    )

    result = audit_csv_keys(
        path,
        candidate_keys=[("PATNO",), ("PATNO", "EVENT_ID"), ("IMAGE_ID",)],
    )

    assert result["row_count"] == 3
    participant_key, visit_key, image_key = result["candidate_keys"]
    assert participant_key["distinct_keys"] == 2
    assert participant_key["duplicate_key_groups"] == 1
    assert participant_key["duplicate_rows"] == 1
    assert visit_key["rows_with_missing_key"] == 1
    assert visit_key["duplicate_key_groups"] == 1
    assert image_key["duplicate_key_groups"] == 0
    assert "001" not in str(result)


def test_audit_csv_keys_requires_known_candidate_fields(tmp_path):
    path = tmp_path / "table.csv"
    path.write_text("PATNO,EVENT_ID\n001,BL\n", encoding="utf-8")

    with pytest.raises(ValueError, match="absent"):
        audit_csv_keys(path, candidate_keys=[("PATNO", "IMAGE_ID")])


def test_audit_csv_keys_requires_candidate_key(tmp_path):
    path = tmp_path / "table.csv"
    path.write_text("PATNO\n001\n", encoding="utf-8")

    with pytest.raises(ValueError, match="at least one"):
        audit_csv_keys(path, candidate_keys=[])


def test_audit_csv_relationship_reports_unmatched_and_parent_duplicates(tmp_path):
    parent = tmp_path / "parent.csv"
    child = tmp_path / "child.csv"
    parent.write_text(
        "PATNO,EVENT_ID\n001,BL\n001,BL\n002,V01\n", encoding="utf-8"
    )
    child.write_text(
        "SUBJECT,VISIT\n001,BL\n002,V01\n003,V01\n,BL\n",
        encoding="utf-8",
    )

    result = audit_csv_relationship(
        parent,
        child,
        parent_key=("PATNO", "EVENT_ID"),
        child_key=("SUBJECT", "VISIT"),
    )

    assert result["child_rows"] == 4
    assert result["child_rows_matched"] == 2
    assert result["child_rows_unmatched"] == 1
    assert result["child_rows_with_missing_key"] == 1
    assert result["parent_duplicate_key_groups"] == 1
    assert result["relationship_is_many_to_one_candidate"] is False
    assert "001" not in str(result)


def test_audit_csv_relationship_rejects_different_key_arity(tmp_path):
    parent = tmp_path / "parent.csv"
    child = tmp_path / "child.csv"
    parent.write_text("PATNO\n001\n", encoding="utf-8")
    child.write_text("PATNO,EVENT_ID\n001,BL\n", encoding="utf-8")

    with pytest.raises(ValueError, match="same number"):
        audit_csv_relationship(
            parent,
            child,
            parent_key=("PATNO",),
            child_key=("PATNO", "EVENT_ID"),
        )
