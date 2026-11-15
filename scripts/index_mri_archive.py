"""Run local-only DICOM header indexing; outputs must remain outside the Git worktree."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from src.preprocessing.mri_manifest import index_dicom_zip


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path, help="Local LONI DICOM ZIP")
    parser.add_argument("--secret-file", required=True, type=Path, help="Private file containing >=32 random bytes")
    parser.add_argument("--output", required=True, type=Path, help="Private JSON manifest path outside this repository")
    args = parser.parse_args()

    archive = args.archive.expanduser().resolve(strict=True)
    secret_path = args.secret_file.expanduser().resolve(strict=True)
    output = args.output.expanduser().resolve()
    if output == REPOSITORY_ROOT or REPOSITORY_ROOT in output.parents:
        parser.error("--output must be outside the PANPM Git worktree")
    if output in (archive, secret_path) or archive == secret_path:
        parser.error("Archive, secret and output must be separate files")

    secret = secret_path.read_bytes().strip()
    if len(secret) < 32:
        parser.error("--secret-file must contain at least 32 random bytes")

    report = index_dicom_zip(archive, secret=secret)
    report["provenance"] = {
        "archive_sha256": sha256_file(archive),
        "archive_name": archive.name,
        "manifest_schema_version": report["schema_version"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + chr(10), encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "archive_sha256": report["provenance"]["archive_sha256"],
        "series_count": report["series_count"],
        "counts": report["counts"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
