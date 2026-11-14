# Work not covered by CI

A green CI run verifies only the automated checks listed in `.github/workflows/ci.yml`. It does not establish any of the following:

- PPMI account approval, data-use compliance or completeness of downloaded data.
- Correctness of source-to-normalized cohort mapping or all participant/visit joins.
- MRI sequence identity, DICOM de-identification, visual image QC, registration or segmentation quality.
- Correctness of scanner/site harmonization or biological interpretation.
- Scientific validity of GWAS fine-mapping, gene prioritization, Allen Atlas probe mapping or spatial null models.
- Clinical endpoint validity, medication-state comparability or completeness of 12/24-month follow-up.
- Model performance on a locked participant-level test set or independent cohort.
- CUDA/GPU execution, memory use, preprocessing throughput or performance on real MRI volumes.
- PPO learning quality, policy stability, simulator realism or fairness across subgroups.
- Whether ROI inspection cost is a meaningful proxy for real clinical workflow cost.
- Clinical utility, diagnostic safety, medical-device status or regulatory compliance.
- Human expert review of brain maps, segmentation outputs, QC reports or research conclusions.

These checks require controlled research data, imaging tools/hardware, independent review or external validation. Record the evidence and limitations in the experiment report and `docs/status.md`.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
