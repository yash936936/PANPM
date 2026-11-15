"""Inventory approved tabular exports and imaging metadata without loading images."""
from __future__ import annotations

import csv
import hashlib
from collections.abc import Iterable
from pathlib import Path


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return a streaming SHA-256 checksum for a file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv_header(path: str | Path) -> list[str]:
    """Read a CSV header without loading participant records."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        try:
            header = next(csv.reader(stream))
        except StopIteration as exc:
            raise ValueError(f"CSV is empty: {path}") from exc
    if not header or any(not name.strip() for name in header):
        raise ValueError(f"CSV has an empty or invalid header: {path}")
    if len(header) != len(set(header)):
        raise ValueError(f"CSV has duplicate column names: {path}")
    return [name.strip() for name in header]


def inspect_csv(path: str | Path, release_id: str) -> dict[str, object]:
    """Return non-sensitive file provenance and schema metadata."""
    file_path = Path(path)
    if not release_id.strip():
        raise ValueError("release_id must be non-empty")
    return {
        "file_name": file_path.name,
        "release_id": release_id,
        "sha256": sha256_file(file_path),
        "size_bytes": file_path.stat().st_size,
        "columns": read_csv_header(file_path),
    }


def count_csv_rows(path: str | Path) -> int:
    """Count data rows in a CSV without retaining their contents."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        try:
            next(reader)
        except StopIteration:
            raise ValueError(f"CSV is empty: {path}")
        return sum(1 for _ in reader)


def summarize_values(values: Iterable[object]) -> dict[str, int]:
    """Count explicit values, representing missing entries separately."""
    counts: dict[str, int] = {}
    for value in values:
        key = "MISSING" if value is None or str(value).strip() == "" else str(value).strip()
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def discover_csv_exports(root: str | Path) -> list[Path]:
    """Discover CSV exports recursively without reading participant-level values.

    Hidden directories are skipped to avoid indexing caches and repository
    metadata. Returned paths are sorted and remain local to the supplied root.
    """
    base = Path(root)
    if not base.is_dir():
        raise NotADirectoryError(f"Export root is not a directory: {base}")
    discovered = [
        path
        for path in base.rglob("*.csv")
        if path.is_file()
        and not any(part.startswith(".") for part in path.relative_to(base).parts)
    ]
    return sorted(discovered, key=lambda path: path.relative_to(base).as_posix())


def inventory_csv_tree(
    root: str | Path, *, release_id: str
) -> list[dict[str, object]]:
    """Inventory discovered CSV files using relative paths and metadata only."""
    base = Path(root)
    if not release_id.strip():
        raise ValueError("release_id must be non-empty")
    inventory: list[dict[str, object]] = []
    for path in discover_csv_exports(base):
        record = inspect_csv(path, release_id)
        record["relative_path"] = path.relative_to(base).as_posix()
        record["row_count"] = count_csv_rows(path)
        inventory.append(record)
    return inventory
