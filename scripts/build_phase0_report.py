"""Build a reproducible aggregate Phase 0 feasibility JSON report.

Example:
python scripts/build_phase0_report.py --config /secure/ppmi-mapping.json \
  --status /secure/exports/PATIENT_STATUS.csv \
  --acquisitions /secure/exports/MRI_ACQUISITION.csv \
  --image-manifest /secure/loni/image_manifest.csv \
  --baseline /secure/derived/baseline_index.csv \
  --assessments /secure/exports/NUPDRS3TRT.csv \
  --ledd /secure/exports/LEDDLOG.csv \
  --secret-file /secure/keys/panpm-hmac.key \
  --download-date 2026-11-15 --output /secure/reports/phase0.json

All input files, secrets and outputs must remain outside Git.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.data.feasibility import (
    build_phase0_report,
    cohort_coverage,
    load_mapping_config,
    mri_manifest_matching,
    progression_endpoint_coverage,
    validate_configured_header,
)
from src.data.inventory import read_csv_header, sha256_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--acquisitions", required=True, type=Path)
    parser.add_argument("--image-manifest", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--assessments", required=True, type=Path)
    parser.add_argument("--ledd", type=Path)
    parser.add_argument("--secret-file", required=True, type=Path)
    parser.add_argument("--download-date", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_mapping_config(args.config)
    report_fields = config.get("report_fields", {})
    cohort_fields = report_fields.get("cohort", {})
    imaging_fields = report_fields.get("imaging", {})
    progression_fields = report_fields.get("progression", {})
    progression_rules = config.get("progression_rules", {})

    for table_name, path in (
        ("PATIENT_STATUS", args.status),
        ("MRI_ACQUISITION", args.acquisitions),
        ("NUPDRS3TRT", args.assessments),
    ):
        validate_configured_header(table_name, read_csv_header(path), config)
    if args.ledd:
        validate_configured_header("LEDDLOG", read_csv_header(args.ledd), config)

    secret = args.secret_file.read_bytes()
    if len(secret) < 32:
        raise ValueError("HMAC secret file must contain at least 32 bytes")

    cohort = cohort_coverage(
        args.status,
        participant_field=cohort_fields["participant_field"],
        cohort_field=cohort_fields["cohort_field"],
        enrollment_field=cohort_fields.get("enrollment_field"),
        secret=secret,
    )
    imaging = mri_manifest_matching(
        args.acquisitions,
        args.image_manifest,
        acquisition_key=imaging_fields["acquisition_key"],
        manifest_key=imaging_fields["manifest_key"],
        sequence_flags=imaging_fields["sequence_flags"],
        secret=secret,
    )
    progression = progression_endpoint_coverage(
        args.baseline,
        args.assessments,
        participant_field=progression_fields["participant_field"],
        index_date_field=progression_fields["index_date_field"],
        assessment_date_field=progression_fields["assessment_date_field"],
        score_field=progression_fields["score_field"],
        state_field=progression_fields["state_field"],
        assessment_form_field=progression_fields["assessment_form_field"],
        allowed_assessment_forms=progression_fields["allowed_assessment_forms"],
        state_map=progression_rules["source_state_map"],
        target_states=progression_rules["target_states"],
        horizons_months=progression_rules["horizons_months"],
        tolerance_days=progression_rules["date_tolerance_days"],
        secret=secret,
        ledd_csv=args.ledd,
        ledd_participant_field=progression_fields.get("ledd_participant_field"),
    )

    source_paths = {
        "PATIENT_STATUS": args.status,
        "MRI_ACQUISITION": args.acquisitions,
        "IMAGE_MANIFEST": args.image_manifest,
        "BASELINE_INDEX": args.baseline,
        "NUPDRS3TRT": args.assessments,
    }
    if args.ledd:
        source_paths["LEDDLOG"] = args.ledd
    report = build_phase0_report(
        release_id=config["release_id"],
        download_date=args.download_date,
        source_checksums={name: sha256_file(path) for name, path in source_paths.items()},
        mapping_config_sha256=sha256_file(args.config),
        cohort=cohort,
        imaging=imaging,
        progression=progression,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote aggregate Phase 0 report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
