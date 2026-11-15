## D-017 - Include BOLD acquisition metadata in QC outputs (2026-11-15)
**Decision:** Before running the BOLD QC CLI on the local cohort, extend each private per-scan QC record to preserve the sidecar's `PhaseEncodingDirection`, `EffectiveEchoSpacing`, `TotalReadoutTime`, `ReconMatrixPE`, `EchoTime`, `TaskName`, `MRAcquisitionType`, `ScanningSequence`, and slice-timing summary. Include an affine-derived normalized phase-encoding vector in RAS coordinates when the direction is valid. Add aggregate phase-encoding-direction counts without participant identifiers. Summarize SliceTiming as count/minimum/median/maximum rather than copying the full array. Validate BIDS direction syntax and numeric metadata; when EffectiveEchoSpacing, TotalReadoutTime and ReconMatrixPE are all present, check `TotalReadoutTime` against `EffectiveEchoSpacing * (ReconMatrixPE - 1)` using an absolute tolerance of 1e-5 seconds (10 microseconds). A missing optional field leaves the consistency result unavailable; both readout values present without ReconMatrixPE is an error because the check cannot be performed.

**Reason:** D-016 establishes a genuine phase-encoding difference in one scan. The current `inspect_bold` report includes TR and geometry but does not serialize the phase-encoding and readout metadata, so the current QC JSON would lose a key acquisition distinction.

**Consequences:** Update `src/preprocessing/bold_qc.py`, aggregate output and synthetic tests in PR #20 before local execution. Do not rewrite source sidecars or force a cohort-wide phase-encoding direction. Local QC remains blocked on this small implementation gap and explicit sequence verification.

---
## D-016 - Preserve per-scan BOLD phase-encoding metadata (2026-11-15)
**Decision:** Keep each BOLD scan's BIDS `PhaseEncodingDirection` and NIfTI affine together as scan-level acquisition metadata. Do not force one phase-encoding label across the cohort, infer equivalence from voxel orientation labels alone, or automatically exclude a scan because its direction differs. The observed direction difference must remain visible in QC reports and downstream preprocessing configuration.

**Evidence:** The researcher audited all 55 local BOLD NIfTI/JSON pairs. All 55 have matching sidecars and consistent core acquisition values: TR 2 s, TE 0.029 s, 64 x 64 x 32 x 200 image shape, EffectiveEchoSpacing 0.000590001 s, TotalReadoutTime 0.0371701 s and ReconMatrixPE 64. All are LAS. PhaseEncodingDirection is j- for 54 scans and i for one scan. The exceptional scan's affine-derived physical direction is predominantly negative RAS X, whereas j- scans are predominantly negative RAS Y. Siemens TrioTim, 3 T and flip angle 90 degrees are consistent in the inspected metadata. The differing direction is therefore a genuine physical-direction difference in the supplied NIfTI affine/sidecar pair, not merely a relabeling of the same physical axis.

**Consequences:** Preserve per-scan values and flag cohort heterogeneity for review; do not change source JSON/NIfTI files. No scan is excluded on this evidence alone. This audit does not establish the availability of reverse-phase-encoding companions or field maps, so susceptibility-distortion correction must not be assumed. Sequence verification, local BOLD QC execution and visual review remain separate gates.

---
## D-015 - Keep BOLD temporal QC distinct from motion estimation (2026-11-15)
**Decision:** The first-pass BOLD QC path may report acquisition geometry, header/sidecar TR agreement, finite-value summaries, temporal-SNR summaries, whole-volume RMS temporal differences and global-mean signal variation. It must not claim to estimate or correct head motion. Power FD may be calculated only from a separately generated motion TSV whose translation and rotation units and column names are explicit.

**Reason:** The raw BOLD time series and NIfTI headers do not provide realignment parameters. Motion estimates require a defined registration/realignment method and validated outputs. Whole-volume temporal differences are not equivalent to standardized, brain-masked DVARS.

**Consequences:** Raw BOLD QC and motion estimation remain separate workflow stages. No FD threshold is applied without supplied motion parameters; no cohort-derived thresholds or automatic exclusions are introduced. Visual review and preprocessing remain mandatory before cohort freeze.

---

## D-014 - Hold cohort/split PR after repeated Ruff import-order failure - 2026-11-15
**Decision:** Keep the Phase 1 cohort/split implementation in draft PR #16. Do not merge or use it until the Ruff import-order failure is resolved from a local checkout where the autofix diff can be inspected and tested.

**Reason:** Three consecutive CI attempts for PR #16 failed at `ruff check .` on `src/data/cohort.py` with `I001 Import block is un-sorted or un-formatted`. Two import-style changes did not resolve it. The third run also reported `UP012` for an explicit UTF-8 encoding argument. CI skipped compilation and pytest after lint failed.

**Consequences:** PR #16 remains draft and unmerged. Its cohort/split helpers are not part of `main`, have no passing test evidence, and must not be used to create the final cohort or split manifest. This hold does not block separate preprocessing work. Do not train models.

---

# Decisions - PANPM

> Append-only decision log. New decisions go at the top. Do not edit or delete older entries. Supersede a decision with a new ID and reference the old one.

## D-013 - Keep progression window and state caller-configured - 2026-11-15
**Decision:** progression assessment selection must require an explicit target date, tolerance and normalized medication-state label. Select the nearest eligible record; raise an ambiguity error when equally close records exist. Do not hard-code the 12/24-month window tolerance or primary ON/OFF/untreated state before the approved export is audited.

**Reason:** the protocol leaves the follow-up window and medication-state rule to be prespecified, while the PPMI source documents identify multiple assessment forms and states. Actual state-specific coverage and medication exposure are not yet known.

**Consequences:** the generic helper enforces deterministic, state-consistent selection but does not make the clinical protocol decision. A protocol amendment and coverage report are required before target extraction.

# Decisions - PANPM

> Append-only decision log. New decisions go at the top. Do not edit or delete older entries. Supersede a decision with a new ID and reference the old one.

## D-012 - Preserve MDS-UPDRS Part III medication and DBS state - 2026-11-15
**Decision:** retain the assessment form/state, ON/OFF order, medication-use flags, dose timing and DBS status alongside each MDS-UPDRS Part III score. Do not pool ON-state and OFF-state examinations as interchangeable observations. Define the primary progression endpoint only after actual state-specific completeness and medication exposure can be audited.

**Reason:** the annotated PPMI dictionary places `NP3TOT` in `NUPDRS3TRT` alongside `PDSTATE`, `ONOFFORDER`, `PDMEDYN`, `PDTRTMNT`, medication dose timing and DBS fields. The Code List identifies distinct OFF-state, ON-state and no-treatment form names.

**Consequences:** progression dataset construction must preserve treatment context and use a predeclared state-selection rule. The 12- and 24-month horizons remain conditional on valid repeated observations and medication-aware alignment.

## D-011 - Preserve PPMI cohort codes and documentation differences - 2026-11-15
**Decision:** retain raw PPMI cohort values and descriptions in the source layer. Define any binary PD-versus-healthy-control cohort with a separate, versioned inclusion rule. Do not merge genetic registry codes 7/8 into the legacy cohort groups or infer that the guide's five-cohort summary fully supersedes the annotated dictionary.

**Reason:** the supplied 2026 Data User Guide describes five enrollment cohorts, while the May 2025 annotated Code List includes cohort codes 1, 2, 3, 4, 7 and 8. The participant dictionary and code list are source-specific and may reflect additional groups.

**Consequences:** source values remain unchanged; all cohort mappings and exclusions must be logged. Prodromal, SWEDD and genetic registry groups stay distinct from the primary PD-versus-healthy-control task unless a separate experiment defines otherwise.

## D-008 - Research-only claims and data handling - 2026-11-15
**Decision:** PANPM is a research prototype, not a diagnostic or treatment system. Raw PPMI data, direct identifiers, participant-level genetic data, credentials and private paths must not be committed or copied into ordinary logs.
**Why:** The project uses sensitive participant-level research data and has no clinical validation or authorization for clinical use.
**Affects:** all phases; `AGENTS.md`, data ingestion, reports and release materials.

## D-007 - Subject-level split and label isolation - 2026-11-15
**Decision:** all visits and scans from one participant stay in one partition. Diagnosis labels and future progression outcomes may be used in training loss/reward calculation only, and must never be exposed as agent observations or used to select the final test policy.
**Why:** Prevent participant leakage and future-outcome leakage in both supervised and RL experiments.
**Affects:** Phase 0, Phase 1, Phase 2, Phase 4 and all evaluation modules.

## D-006 - Genetic evidence and Atlas reference are separate - 2026-11-15
**Decision:** GWAS/fine-mapping gene prioritization and Allen Atlas expression form a population-level regional prior. Participant genotype or PRS, if authorized and available, is a separate patient-level data branch.
**Why:** Healthy post-mortem regional expression is not a participant's genotype and is not PD-specific expression.
**Affects:** Phase 3, `src/genetics/`, model fusion and interpretation reports.

## D-005 - RL scope is active ROI inspection - 2026-11-15
**Decision:** the core RL task is sequential computational inspection of high-resolution MRI regions from an already acquired volume. The first policy selects an available, uninspected ROI or STOP. It does not choose treatment and does not claim physical scan-time reduction.
**Why:** Retrospective PPMI imaging supports a more defensible ROI-selection simulator than assuming each participant has all candidate MRI sequences and that action selection can initiate an actual scan.
**Affects:** Phase 4, RL environment, reward design and research claims.

## D-004 - Dual prediction objectives - 2026-11-15
**Decision:** maintain separate primary tasks: baseline PD-versus-healthy-control classification and longitudinal change in MDS-UPDRS Part III at 12 and 24 months where valid observations exist. Prodromal conversion is secondary and not part of the primary binary classifier.
**Why:** The user selected both diagnosis and progression objectives; the outcome definitions and cohorts differ.
**Affects:** PRD, TRD, data dictionary, model heads and research protocol.

## D-003 - MRI modality is not assumed - 2026-11-15
**Decision:** inspect PPMI participant-level imaging metadata before choosing the definitive modality set. T1-weighted MRI is the first baseline candidate only if sequence verification, coverage and QC support it. Advanced modalities remain conditional.
**Why:** The available MRI modality and participant-level coverage were not known when the design was selected.
**Affects:** Phase 0, Phase 1 and all model input definitions.

## D-002 - PPMI as primary cohort - 2026-11-15
**Decision:** PPMI is the primary data source for the initial research build. Use current official cohort definitions and document the downloaded release and data-use terms.
**Why:** The user explicitly selected PPMI and requires longitudinal clinical/imaging data.
**Affects:** all data and modelling phases.

## D-001 - PANPM system scope - 2026-11-15
**Decision:** use the project name Parkinson's Active Neuroimaging and Progression Model (PANPM). Build a multi-component research pipeline combining MRI, longitudinal clinical outcomes, genetic spatial priors and RL-based ROI inspection.
**Why:** This captures the selected research objectives and retains the user's original GWAS/Allen Atlas idea while making MRI and RL central.
**Affects:** all documents, phases and repository structure.

---

**Next:** Return to [`context.md`](../context.md) before starting a new task.


## D-009 - Continue source-independent data validation while PPMI access is unavailable (2026-11-15)
**Decision:** Implement PANPM internal schema contracts using synthetic in-memory records, without fabricating PPMI source headers, values, cohort sizes or MRI modalities.

**Reason:** The user reports no PPMI access and no files. Software-level schema validation can be developed against the documented PANPM data dictionary, but feasibility and scientific modelling require approved source data.

**Consequences:** Phase 0 remains incomplete. Do not select an MRI modality, define PPMI source mappings, train diagnostic/progression models or train PPO until approved metadata and a leakage-safe participant manifest exist.


## D-010 - Treat public PPMI tooling as implementation reference, not source truth (2026-11-15)
**Decision:** Review and adapt public PPMI-oriented code patterns only after checking provenance, licence, table grain, validation and fit to PANPM. Do not treat public repositories as a source of PPMI participant data or assume their source mappings and MRI sequence heuristics are correct for the current release.

**Reason:** PIE and PIE-clean document useful cleaning and imaging workflows, but explicitly do not distribute PPMI participant data. PIE also documents potential LONI MRI weighting-label issues that require verification against actual acquisition metadata.

**Consequences:** PANPM adds a public-source review document and generic CSV discovery. PPMI source mapping and MRI sequence selection remain blocked on official documentation and approved metadata.

