"""Tests for source export inventory utilities."""
import hashlib

import pytest

from src.data.inventory import count_csv_rows, inspect_csv, read_csv_header, sha256_file, summarize_values


def test_inspect_csv_records_checksum_and_header(tmp_path):
    path = tmp_path / "clinical.csv"
    path.write_text("PATNO,EVENT_ID\n001,BL\n", encoding="utf-8")
    info = inspect_csv(path, "release-test")
    assert info["columns"] == ["PATNO", "EVENT_ID"]
    assert info["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert info["release_id"] == "release-test"
    assert count_csv_rows(path) == 1


def test_empty_and_duplicate_headers_are_rejected(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        read_csv_header(empty)
    duplicate = tmp_path / "duplicate.csv"
    duplicate.write_text("A,A\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        read_csv_header(duplicate)


def test_checksum_is_stable(tmp_path):
    path = tmp_path / "x.txt"
    path.write_text("PANPM", encoding="utf-8")
    assert sha256_file(path) == hashlib.sha256(b"PANPM").hexdigest()


def test_missingness_is_counted_separately():
    assert summarize_values(["T1", "", None, "T2", "T1"]) == {
        "MISSING": 2, "T1": 2, "T2": 1
    }
