# MRI metadata intake

PANPM's first MRI intake stage indexes DICOM headers from a local archive. It does not extract pixels, convert images, classify a sequence family, or choose a scan for modelling.

## What the first stage records

`src/preprocessing/mri_manifest.py` reads an archive member's DICOM header and aggregates records by `SeriesInstanceUID`. Patient, study and series identifiers are HMACed in memory. The output is a series-level JSON manifest with:
- modality and acquisition metadata explicitly present in the DICOM headers;
- scanner manufacturer, model and field strength;
- series/protocol/sequence descriptions and image type;
- image dimensions, pixel spacing, slice thickness and instance counts;
- missing-header counts, duplicate SOP instance UID counts and intra-series conflicts;
- explicit checks for MR modality, 3-D acquisition and ORIGINAL image type.

The manifest intentionally leaves `sequence_family` unset and `selection_status` at `needs_sequence_review`. A series description containing 'T1' is not enough to classify an acquisition. The LONI Weighting field is not read or trusted as a substitute for DICOM headers and the official MRI acquisition metadata.

## Run locally

Install `pydicom` in the institution-approved imaging environment. Generate a private random HMAC secret of at least 32 bytes and keep it outside the repository. Run:

```bash
python -m pip install pydicom
python scripts/index_mri_archive.py \
  --archive /secure/ppmi/Imaging/MRI_collection.zip \
  --secret-file /secure/keys/panpm-mri-hmac.key \
  --output /secure/reports/mri-series-manifest.json
```

The CLI rejects an output path inside the PANPM Git worktree. It writes a private participant-level derived manifest, so the output must still be handled under the PPMI agreement and institutional controls. HMAC pseudonyms are linkage protection, not anonymization. Do not upload the archive, manifest, DICOM headers or participant-level summaries to public AI services.

## Limits and next gates

- This is a metadata index, not a DICOM validation, image-quality, sequence-identification or preprocessing pipeline.
- `is_3d` only reflects the explicit `MRAcquisitionType` header value; it does not establish that the volume is complete or suitable for FastSurfer.
- `is_original` is a conservative interpretation of `ImageType`; ambiguous or missing values require review.
- The implementation does not use LONI collection CSVs, IDA XML metadata, PPMI `MRI_ACQUISITION` sequence flags or the clinical visit table yet.
- It does not choose T1 candidates. A later reviewed rule must reconcile DICOM headers, PPMI acquisition metadata, image manifest records, date linkage, scanner changes and visual QC.
- No DICOM archive has been run through this code in this session. The tests use synthetic metadata only.

Do not begin dcm2niix conversion or FastSurfer until a release-specific sequence mapping and a representative local QC pilot are approved.
