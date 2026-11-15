# Phase 0 feasibility pipeline

This module builds aggregate-only coverage summaries from approved PPMI exports.
It does not download data, infer source columns, classify MRI from filenames,
or authorize model training.

## Mapping configuration

Copy `configs/ppmi_mapping.example.json` to a private local configuration
file, replace the release identifier, and validate each mapping against the
actual CSV headers. The example uses documented source fields but is not a
validated mapping for any PPMI release. Keep participant identifiers and
restricted staging outputs outside Git.

`load_mapping_config` validates the JSON structure.
`normalize_configured_rows` applies only the explicit source-to-target mapping.
It does not pseudonymize identifiers or decide which fields may enter an
analysis table; restricted fields must be removed or pseudonymized in the
ingestion boundary.

## Reports

- `cohort_coverage`: distinct participant counts by raw cohort and enrollment
  status. It preserves source codes rather than silently normalizing them.
- `mri_manifest_matching`: compares explicitly configured acquisition and
  image-manifest keys and reports sequence-flag coverage, missing keys and
  duplicate join-key groups. The caller must supply the correct LONI/image
  manifest join keys and source-specific flag interpretation after inspecting
  the actual release.
- `progression_endpoint_coverage`: estimates same-state baseline and
  12/24-month score availability using an explicit source-state map, allowed
  `PAG_NAME` form list, target states and date tolerance. Follow-up records
  must occur after the selected baseline assessment. Ties and duplicate
  baseline participants are excluded as ambiguous. It is a coverage estimate,
  not a final clinical endpoint definition. The optional LEDD count means
  “any LEDDLOG record exists”; it is not time-aligned medication exposure.
- `build_phase0_report`: combines the three aggregate reports with release
  and download-date provenance.

All join keys are represented as ephemeral HMAC digests. Use a random secret
of at least 32 bytes, supplied from a secure local secret store. Do not write
the secret, crosswalk, raw exports, source IDs or participant-level outputs
to Git.

## Limits

The pipeline has not been run on approved participant-level PPMI exports.
The example mapping is not validated against real headers. MRI sequence flags
are counted only for explicit truth-like values; if the release uses other
codes, add a reviewed mapping rather than guessing. Image matching is only as
valid as the configured keys. Progression counts do not establish that the
endpoint is clinically appropriate. A successful report does not mean the
dataset is complete or ready for training.

## Run the report

After reviewing and completing every release-specific placeholder in the private
mapping configuration, run the CLI with all inputs stored outside the repository:

```bash
python scripts/build_phase0_report.py \
  --config /secure/ppmi-mapping.json \
  --status /secure/exports/PATIENT_STATUS.csv \
  --acquisitions /secure/exports/MRI_ACQUISITION.csv \
  --image-manifest /secure/loni/image_manifest.csv \
  --baseline /secure/derived/baseline_index.csv \
  --assessments /secure/exports/NUPDRS3TRT.csv \
  --ledd /secure/exports/LEDDLOG.csv \
  --secret-file /secure/keys/panpm-hmac.key \
  --download-date YYYY-MM-DD \
  --output /secure/reports/phase0.json
```

The CLI checks mapped export headers, requires a 32-byte HMAC secret, and
records SHA-256 checksums for each input and the mapping config. It fails
closed when state codes, allowed assessment forms, baseline date fields or
image-manifest join keys remain unset. Use the actual download date and keep
the generated report outside Git if its aggregate counts are subject to the
data-use agreement.
