# Data dictionary - PANPM

> This is the planned internal schema, not a copy of PPMI's original field names. The data-import layer must map actual PPMI release columns to this normalized schema and record the mapping/version. Do not assume every field exists in every export.

## Keys and conventions

- `participant_id`: project-generated pseudonymous key. Any source-ID mapping is stored in a separate restricted crosswalk with restricted access; it is not part of ordinary analysis tables.
- `event_id`: normalized visit identifier linked to the source visit label.
- `scan_id`: unique project scan/series key.
- Dates use ISO-8601. Store source timezone/precision where relevant.
- Missing values remain missing with an explicit missingness reason where useful. Do not replace missing with zero.
- Numeric values preserve source units. Every derived variable records a unit and derivation version.
- Raw PPMI fields are retained in restricted source snapshots, not copied wholesale into public analysis tables.

## Restricted identifier crosswalk

When a source identifier is required to link approved PPMI files, store the mapping from source identifier to `participant_id` in a separate encrypted, access-controlled file or database. Do not place the crosswalk in `participants.parquet`, derived feature tables, model outputs, event logs or Git. Access to this crosswalk must be restricted to the data-ingestion role and must follow the PPMI terms.

## `participants.parquet`

**Grain:** one row per participant.

| Field | Type | Meaning |
|---|---|---|
| participant_id | string | Pseudonymous project key |
| cohort | category | Normalized PD / HC / prodromal / other approved cohort |
| cohort_definition_version | string | Version of official cohort definition used |
| age_at_index | float | Age at the chosen index date |
| recorded_sex | category | Source-recorded sex; source coding retained in lineage |
| site_id | category | Recruiting or acquisition site identifier where available |
| ancestry_group | category | Only where explicitly available and permitted |
| index_event_id | string | Selected baseline event |
| index_date | date | Selected baseline date |
| inclusion_status | category | Included / excluded / pending |
| exclusion_reason | string | Controlled reason code, no free-text identifiers |

## `clinical_visits.parquet`

**Grain:** one row per participant, event and assessment-state record. Different medication states must not be silently collapsed.

| Field | Type | Meaning |
|---|---|---|
| participant_id | string | Participant key |
| event_id | string | Normalized visit/event key |
| visit_date | date | Assessment date |
| months_from_index | float | Months relative to index date |
| diagnosis_at_visit | category | Diagnosis recorded for that visit |
| mds_updrs_1 | float | MDS-UPDRS Part I total, if available |
| mds_updrs_2 | float | MDS-UPDRS Part II total, if available |
| mds_updrs_3 | float | MDS-UPDRS Part III total, if available |
| mds_updrs_4 | float | MDS-UPDRS Part IV total, if available |
| hy_stage | float | Hoehn and Yahr stage, if available |
| moca | float | MoCA score, if available |
| upsit | float | UPSIT score, if available |
| medication_state | category | ON / OFF / untreated / unknown using verified source coding |
| pd_state_code | string | Original state code for traceability where permitted |
| led_dose | float | Levodopa-equivalent daily dose if calculated and supported |
| assessment_source | string | Source table / release / assessment identifier |
| qc_status | category | Valid / review / excluded |

## `imaging_scans.parquet`

**Grain:** one row per MRI series/acquisition, not one row per participant.

| Field | Type | Meaning |
|---|---|---|
| scan_id | string | Unique project series key |
| participant_id | string | Pseudonymous participant key |
| event_id | string | Linked visit, if validated |
| acquisition_datetime | datetime | Acquisition time, if available |
| months_from_index | float | Acquisition time relative to index |
| modality | category | MRI / other imaging class |
| sequence_family | category | Verified normalized family, e.g. T1, DTI, fMRI, neuromelanin |
| series_description | string | De-identified original series description |
| manufacturer | category | Scanner manufacturer |
| scanner_model | string | Scanner model, if available |
| field_strength_t | float | Field strength in Tesla |
| tr_ms | float | Repetition time |
| te_ms | float | Echo time |
| ti_ms | float | Inversion time |
| flip_angle_deg | float | Flip angle |
| voxel_spacing_mm | string | Serialized voxel spacing |
| orientation | string | Verified image orientation |
| derivative_artifact_id | string | Opaque key to a restricted artifact store; filesystem paths are held outside analysis tables |
| series_checksum | string | File/series checksum |
| sequence_confidence | category | Verified / probable / ambiguous / excluded |
| qc_status | category | Pass / review / fail |
| qc_reason_code | string | Controlled exclusion or review reason |
| preprocessing_version | string | Pipeline version |

## `roi_features.parquet`

**Grain:** one row per scan, atlas region, feature and feature version.

| Field | Type | Meaning |
|---|---|---|
| participant_id | string | Participant key |
| scan_id | string | Source scan key |
| atlas_id | string | Atlas and version |
| roi_id | string | Stable atlas region key |
| hemisphere | category | Left / right / bilateral / not applicable |
| feature_name | string | Volume / thickness / intensity / FA / MD / other |
| feature_value | float | Numeric feature |
| feature_unit | string | Unit of measurement |
| qc_score | float | Defined QC score, if available |
| feature_version | string | Extraction code/config version |

## `progression_targets.parquet`

**Grain:** one row per participant, target horizon and medication-state definition.

| Field | Type | Meaning |
|---|---|---|
| participant_id | string | Participant key |
| index_date | date | Baseline/index date |
| horizon_months | integer | 12 or 24 months |
| baseline_updrs3 | float | Valid baseline Part III score |
| followup_updrs3 | float | Valid follow-up Part III score |
| delta_updrs3 | float | Follow-up minus baseline score |
| followup_days | integer | Actual elapsed days |
| target_medication_state | category | OFF / ON / untreated / adjusted analysis |
| baseline_medication_state | category | Medication state at baseline |
| led_dose_baseline | float | Baseline LEDD where available |
| led_dose_followup | float | Follow-up LEDD where available |
| target_valid | boolean | Whether prespecified endpoint rules are met |
| target_exclusion_reason | string | Controlled reason if invalid |
| target_definition_version | string | Endpoint construction version |

The target windows and permitted medication-state comparisons must be prespecified in `docs/research-protocol.md`. Do not choose a follow-up visit based on which score gives the best model result.

## `gene_risk.parquet`

**Grain:** one row per variant-to-gene evidence record, with a separate gene-level aggregation artifact.

| Field | Type | Meaning |
|---|---|---|
| gene_id | string | Stable gene identifier and namespace |
| variant_id | string | Variant identifier |
| locus_id | string | GWAS locus identifier |
| gwas_release | string | GWAS Catalog or study release |
| p_value | float | Association p-value where available |
| credible_set_probability | float | Fine-mapping posterior probability where available |
| qtl_evidence | string | eQTL/sQTL source and evidence reference |
| functional_evidence | string | Functional evidence reference/type |
| gene_prioritization_method | string | Versioned method |
| evidence_weight | float | Standardized evidence weight with documented derivation |

Do not equate a nearest gene with a causal gene. Store gene-level summaries separately and retain evidence provenance.

## `atlas_expression.parquet`

**Grain:** one row per donor, sample/probe, gene and mapped region as supported by the source data.

| Field | Type | Meaning |
|---|---|---|
| donor_id | string | Allen donor key |
| sample_id | string | Tissue sample key |
| probe_id | string | Expression probe identifier |
| gene_id | string | Mapped gene identifier |
| region_id | string | Harmonized brain region |
| expression_value | float | Processed expression value |
| expression_method_version | string | Probe selection / normalization / mapping version |
| qc_status | category | Valid / review / excluded |

## `regional_genetic_prior.parquet`

**Grain:** one row per atlas region and prior version.

| Field | Type | Meaning |
|---|---|---|
| atlas_id | string | Atlas/version |
| region_id | string | Region key |
| prior_score | float | Weighted regional expression/enrichment summary |
| null_model_p | float | Corrected null-model result if defined |
| multiple_test_q | float | Multiple-testing-adjusted value |
| donor_robustness | float | Defined donor sensitivity statistic |
| gene_set_version | string | Prioritized gene set version |
| prior_version | string | End-to-end prior version |

This is a population-level reference prior, not patient-specific gene expression.

## `rl_episodes.parquet`

**Grain:** one row per action within one participant/task episode. Keep any outcome used for reward in a separate restricted training artifact rather than in the policy observation.

| Field | Type | Meaning |
|---|---|---|
| episode_id | string | Unique episode key |
| participant_id | string | Pseudonymous participant key |
| task_type | category | Diagnosis / progression |
| split | category | Train / validation / test; test trajectories are evaluation only |
| timestep | integer | Action number |
| inspected_roi_mask | string | Serialized mask or linked mask artifact |
| available_action_mask | string | Legal actions at this step |
| selected_action | string | ROI action or STOP |
| prediction_version | string | Frozen predictor used in this episode |
| prediction_summary | string | Current prediction representation, without target values |
| uncertainty | float | Defined uncertainty measure |
| remaining_budget | float | Remaining normalized computational budget |
| action_cost | float | Cost of selected ROI inspection |
| reward | float | Training-only reward |
| terminal | boolean | STOP or budget exhaustion |
| policy_version | string | Agent checkpoint/config version |
| environment_version | string | Simulator version |

## `split_manifest.parquet`

**Grain:** one row per participant and frozen split assignment.

| Field | Type | Meaning |
|---|---|---|
| participant_id | string | Pseudonymous key |
| split | category | Train / validation / test / external |
| split_version | string | Immutable split version |
| grouping_basis | string | Participant / site-held-out / cohort-held-out |
| random_seed | integer | Seed used where relevant |
| assignment_date | date | Manifest creation date |

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
