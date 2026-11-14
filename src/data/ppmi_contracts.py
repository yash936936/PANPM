"""Source-level contracts transcribed from the supplied PPMI reference files.

The contracts are deliberately conservative: they validate only documented
linkage fields. They do not infer that a table is present in a particular
download, nor do they impose a row grain where the source documentation is
ambiguous or does not declare one.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PPMISourceTable:
    """Minimal source-table metadata grounded in the PPMI dictionary."""

    name: str
    linkage_fields: tuple[str, ...]
    documented_fields: tuple[str, ...]
    declared_unique_fields: tuple[str, ...] = ()


PPMI_SOURCE_TABLES: dict[str, PPMISourceTable] = {
    "PATIENT_STATUS": PPMISourceTable(
        name="PATIENT_STATUS",
        linkage_fields=("PATNO",),
        documented_fields=(
            "PATNO", "COHORT", "COHORT_DEFINITION", "ENROLL_STATUS",
            "ENROLL_DATE", "ENROLL_AGE", "STATUS_DATE", "REC_ID",
        ),
        declared_unique_fields=("REC_ID",),
    ),
    "MRI": PPMISourceTable(
        name="MRI",
        linkage_fields=("PATNO", "EVENT_ID"),
        documented_fields=(
            "PATNO", "EVENT_ID", "INFODT", "MRICMPLT", "MRIRSLT",
            "MRIRSSDF", "MRIWDTI", "MRIWRSS", "PDMEDDT", "PDMEDTM",
            "REC_ID",
        ),
        declared_unique_fields=("REC_ID",),
    ),
    "MRI_ACQUISITION": PPMISourceTable(
        name="MRI_ACQUISITION",
        linkage_fields=("PATNO", "EVENT_ID"),
        documented_fields=(
            "PATNO", "EVENT_ID", "MRI_SCAN_DATE", "PROTOCOL",
            "MRI_SCAN_ANALYZED", "MRI_NOT_ANALYZED_REASON",
            "MRI_SCAN_QUALITY_RATING", "MRI_SEQ_T1_WEIGHTED",
            "MRI_SEQ_T2_WEIGHTED", "MRI_SEQ_DTI", "MRI_SEQ_RS",
            "MRI_SEQ_NM_MT", "SCANNER_CHANGE_AFTER_BASELINE",
            "SCANNER_CHANGE_AFTER_PREVIOUS",
        ),
        # The dictionary marks PATNO and EVENT_ID as unique individually.
        # Their joint semantics conflict with repeated imaging timepoints in
        # the guide, so PANPM records the declaration but does not enforce it.
        declared_unique_fields=("PATNO", "EVENT_ID"),
    ),
    "MRIQC": PPMISourceTable(
        name="MRIQC",
        linkage_fields=(),
        documented_fields=(
            "PATNO", "EVENT_ID", "filename", "cjv", "cnr", "efc",
            "fber", "fwhm_avg", "fwhm_x", "fwhm_y", "fwhm_z",
            "icvs_csf", "icvs_gm", "icvs_wm", "inu_med", "inu_range",
            "rpve_csf", "rpve_gm", "rpve_wm", "snr_csf", "snr_gm",
            "snr_total", "snr_wm", "snrd_csf", "snrd_gm",
            "snrd_total", "snrd_wm",
        ),
    ),
    "GMVOLUME": PPMISourceTable(
        name="GMVOLUME",
        linkage_fields=(),
        documented_fields=("PATNO", "EVENT_ID", "IMAGEID", "MRIDATE", "GM_VOLUME"),
    ),
    "DTIROI": PPMISourceTable(
        name="DTIROI",
        linkage_fields=(),
        documented_fields=(
            "PATNO", "IMAGE_ID", "INFODT", "Measure", "Tissue",
            "REF1", "REF2", "ROI1", "ROI2", "ROI3", "ROI4",
            "ROI5", "ROI6", "RUNDATE",
        ),
    ),
}


def validate_ppmi_source_header(
    table_name: str, columns: tuple[str, ...] | list[str]
) -> list[str]:
    """Return missing documented linkage fields for a known source table."""
    try:
        contract = PPMI_SOURCE_TABLES[table_name]
    except KeyError as exc:
        raise ValueError(f"Unknown documented PPMI source table: {table_name}") from exc
    available = set(columns)
    return [field for field in contract.linkage_fields if field not in available]
