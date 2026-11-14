# PPMI source catalog (reference-document extraction)

**Reference files inspected**

- PPMI Data User Guide, cover version updated August 6, 2026.
- Data Dictionary (Annotated), dated May 23, 2025.
- Code List (Annotated), dated May 23, 2025.

The guide's introductory page still contains an older August 28, 2024 revision note. PANPM therefore records the cover date and retains this internal version discrepancy rather than assuming every page was revised simultaneously.

## Participant and cohort fields

The guide identifies `PATNO` as the participant identifier used to link PPMI Clinical, Remote and Online records. It notes a special historical case in which one participant was enrolled under two different PATNOs; whether to combine those records depends on the analysis. This crosswalk must be handled explicitly and must not be silently merged.

The annotated dictionary's `PATIENT_STATUS` table includes `PATNO`, `COHORT`, `COHORT_DEFINITION`, `ENROLL_STATUS`, `ENROLL_DATE`, `ENROLL_AGE`, `STATUS_DATE` and `REC_ID`. The annotated Code List defines cohort codes including 1 Parkinson's Disease, 2 Healthy Control, 3 SWEDD, 4 Prodromal, 7 Genetic Registry - PD and 8 Genetic Registry - Unaffected. Do not collapse these categories into a binary diagnosis label without a separately versioned cohort-selection rule. The 2026 guide describes five enrollment cohorts, while the 2025 dictionary/code list also contain genetic registry codes; this difference requires explicit study-population decisions and should be preserved in the audit log.

The guide describes enrollment statuses Pending, Screened, Declined, Screen_failed, Excluded, Enrolled, Withdrew and Complete. For longitudinal analysis, status is a time-dependent study-status field, not a diagnosis label.

## MRI source tables

### `MRI`

Documented fields relevant to PANPM include `PATNO`, `EVENT_ID`, `INFODT`, `MRICMPLT`, `MRIRSLT`, `MRIRSSDF`, `MRIWDTI`, `MRIWRSS`, `PDMEDDT`, `PDMEDTM` and `REC_ID`.

The Code List defines:

- `MRICMPLT`: 0 Not Completed, 1 Completed.
- `MRIRSLT`: 1 Normal, 2 Abnormal, not clinically significant, 3 Abnormal, clinically significant.
- `MRIRSSDF`, `MRIWDTI`, `MRIWRSS`: 0 No, 1 Yes.

These are assessment-level fields and are not substitutes for image-file metadata.

### `MRI_ACQUISITION`

The annotated dictionary defines acquisition-level fields:

- Linkage/time: `PATNO`, `EVENT_ID`, `MRI_SCAN_DATE`.
- Protocol/scanner: `PROTOCOL`, `SCANNER_CHANGE_AFTER_BASELINE`, `SCANNER_CHANGE_AFTER_PREVIOUS`.
- QC/analysis: `MRI_SCAN_ANALYZED`, `MRI_NOT_ANALYZED_REASON`, `MRI_SCAN_QUALITY_RATING`.
- Sequence flags: `MRI_SEQ_T1_WEIGHTED`, `MRI_SEQ_T2_WEIGHTED` (described as T2-weighted FLAIR), `MRI_SEQ_DTI`, `MRI_SEQ_RS` (resting-state fMRI), and `MRI_SEQ_NM_MT` (neuromelanin MT).

The Code List supplies MRI acquisition visit codes including BL, SC, V02, V04, V05, V06, V08, V10 and later visits through V20. It also supplies scan-quality ratings 1 Good Quality, 2 Adequate Quality, 3 Lower Quality, and protocol codes 1, 2 and T011. Sequence yes/no codes are not present in the extracted Code List rows, so PANPM must inspect actual export values before decoding them.

The dictionary marks both `PATNO` and `EVENT_ID` as unique for this table. Because the guide describes repeated MRI timepoints, PANPM records this declaration but does not assume the fields are globally unique until the downloaded table and its actual grain are audited.

### Derived MRI tables

- `MRIQC`: T1-weighted MRIQC metrics, including `cnr`, `efc`, `fber`, `fwhm_avg`, `snr_total`, `snrd_total`, `icvs_gm`, `icvs_wm`, `icvs_csf`, and regional/background summary metrics. The dictionary does not mark a required or unique key; inspect the actual export grain and filename conventions.
- `GMVOLUME`: `PATNO`, `EVENT_ID`, `IMAGEID`, `MRIDATE`, `GM_VOLUME` (extracted grey-matter volume in mm³). The dictionary does not declare a unique key.
- `DTIROI`: `PATNO`, `IMAGE_ID` (LONI image UID), `INFODT`, `Measure`, `Tissue`, `REF1`, `REF2`, `ROI1`–`ROI6`, `RUNDATE`. The dictionary does not declare a unique key.

## Cohort and prediction implications

1. Keep diagnosis, prodromal status, SWEDD and genetic registry categories separate in the source layer.
2. Create a binary PD-versus-healthy-control label only from an explicit, frozen cohort rule. Exclude prodromal, SWEDD and genetic registry participants from that primary binary task unless a separately registered experiment says otherwise.
3. Keep progression labels separate from diagnosis. The 12- and 24-month MDS-UPDRS Part III targets remain conditional on valid repeated assessments and a predeclared visit-window rule.
4. Preserve `PATNO` only in the restricted linkage layer. Convert it to a keyed pseudonym before creating ordinary analysis tables; HMAC pseudonyms are not anonymization.
5. Do not treat MRI assessment flags as proof that an image file exists. Join acquisition records to LONI image metadata and downloaded image manifests, then audit participant/visit/sequence coverage.
6. Do not choose T1 or advanced sequences based on cohort-wide assumptions. Use `MRI_ACQUISITION`, image metadata and DICOM headers for the actual release.

## Scope and limitations

This catalog is based on the three reference documents named above, not on approved participant-level PPMI exports or downloaded MRI files. No participant counts, scan counts, missingness rates, MRI sequence coverage or endpoint availability have been measured. The code in `src/data/ppmi_contracts.py` validates only the documented participant/visit linkage fields for selected source tables; it does not claim to validate every PPMI table or the complete imaging archive.
