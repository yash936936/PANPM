"""Run private, non-destructive temporal QC on verified BOLD scans."""
from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("MPLBACKEND", "Agg")

from src.data.inventory import sha256_file
from src.preprocessing.bold_qc import aggregate_bold_qc, inspect_bold, render_bold_montage


def _inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _pseudonym(participant_id: str, secret: bytes) -> str:
    return hmac.new(
        secret,
        f"panpm-bold-qc-v1:{participant_id}".encode(),
        hashlib.sha256,
    ).hexdigest()[:20]


def _sidecar_for(scan_path: Path) -> Path:
    name = scan_path.name
    if name.endswith(".nii.gz"):
        return scan_path.with_name(name[:-7] + ".json")
    if name.endswith(".nii"):
        return scan_path.with_name(name[:-4] + ".json")
    raise ValueError("BOLD scan path must end in .nii or .nii.gz")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bids-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--secret-file", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--thresholds-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bids_root = args.bids_root.resolve()
    manifest_path = args.manifest.resolve()
    secret_path = args.secret_file.resolve()
    output_dir = args.output_dir.resolve()
    if not bids_root.is_dir():
        raise NotADirectoryError("BIDS root does not exist")
    for candidate in (manifest_path, secret_path):
        if _inside(candidate, ROOT.resolve()) or _inside(candidate, bids_root):
            raise ValueError("Private manifest and secret must be outside Git and the BIDS source")
    if _inside(output_dir, ROOT.resolve()) or _inside(output_dir, bids_root):
        raise ValueError("QC output must be outside Git and the BIDS source")
    if not manifest_path.is_file() or not secret_path.is_file():
        raise FileNotFoundError("Manifest or secret file does not exist")
    secret = secret_path.read_bytes()
    if len(secret) < 32:
        raise ValueError("HMAC secret must contain at least 32 bytes")

    thresholds = {}
    if args.thresholds_json:
        threshold_path = args.thresholds_json.resolve()
        if _inside(threshold_path, ROOT.resolve()) or _inside(threshold_path, bids_root):
            raise ValueError("Threshold configuration must be stored outside Git and the BIDS source")
        payload = json.loads(threshold_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("Threshold configuration must be a JSON object")
        thresholds = payload

    with manifest_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"participant_id", "scan_path", "sequence_verified"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Manifest requires participant_id, scan_path and sequence_verified")
        rows = list(reader)
    if not rows:
        raise ValueError("BOLD manifest is empty")

    seen = set()
    private_records = []
    montage_dir = output_dir / "montages"
    motion_count = 0
    for row in rows:
        participant_id = (row.get("participant_id") or "").strip()
        if not participant_id or participant_id in seen:
            raise ValueError("Manifest has an empty or duplicate participant ID")
        seen.add(participant_id)
        if (row.get("sequence_verified") or "").strip().lower() != "true":
            raise ValueError("Every BOLD scan must be explicitly sequence-verified before QC")
        scan_path = Path((row.get("scan_path") or "").strip())
        if not scan_path.is_absolute():
            scan_path = bids_root / scan_path
        scan_path = scan_path.resolve()
        if not _inside(scan_path, bids_root) or not scan_path.is_file():
            raise ValueError("Every BOLD scan path must resolve inside the BIDS root")
        sidecar_path = _sidecar_for(scan_path)
        if not _inside(sidecar_path.resolve(), bids_root) or not sidecar_path.is_file():
            raise ValueError("Every BOLD scan must have a matching JSON sidecar inside the BIDS root")

        motion_path = None
        raw_motion_path = (row.get("motion_parameters_path") or "").strip()
        if raw_motion_path:
            motion_path = Path(raw_motion_path)
            if not motion_path.is_absolute():
                motion_path = bids_root / motion_path
            motion_path = motion_path.resolve()
            if not _inside(motion_path, bids_root) or not motion_path.is_file():
                raise ValueError("Motion parameter paths must resolve inside the BIDS root")
            motion_count += 1

        pseudonym = _pseudonym(participant_id, secret)
        metrics = inspect_bold(
            scan_path,
            sidecar_path,
            motion_parameters_path=motion_path,
            thresholds=thresholds,
        )
        render_bold_montage(
            scan_path,
            montage_dir / f"{pseudonym}.png",
            pseudonym=pseudonym,
        )
        private_records.append({
            "participant_key": pseudonym,
            "image_sha256": sha256_file(scan_path),
            **metrics,
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    private_report = {
        "report_schema_version": "1.0",
        "evidence_class": "local_bold_temporal_qc",
        "scan_records": private_records,
        "participant_level_identifiers_emitted": False,
        "raw_images_modified": False,
        "automatic_exclusions": False,
    }
    aggregate_report = {
        "report_schema_version": "1.0",
        "evidence_class": "aggregate_local_bold_temporal_qc",
        **aggregate_bold_qc(private_records),
    }
    (output_dir / "bold_qc_private.json").write_text(
        json.dumps(private_report, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "bold_qc_aggregate.json").write_text(
        json.dumps(aggregate_report, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Scans inspected: {len(private_records)}")
    print(f"Review flags: {sum(len(row['review_flags']) for row in private_records)}")
    print(f"Scans with supplied motion estimates: {motion_count}")
    print("Source images modified: no")
    print(f"Private outputs written under: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
