# Validation record

Validation performed during the local cleanup on 25 October 2026, using Python 3.12 in an isolated environment. Package versions are recorded in `requirements-validated.txt`; this is not the unrecovered original 2025 environment.

## Executed checks

- `python -m pytest -q`: **4 passed**. Tests cover genuine lag alignment and future-data perturbation, check-loss benchmark identities, overlapping regime boundaries, and finite fitting on deterministic synthetic data.
- Both notebooks executed from fresh Jupyter kernels with no cell errors. Executed copies are in ignored `results/executed-notebooks`; upload copies remain free of market outputs and interactive-state metadata.
- Both notebooks pass nbformat schema validation and Python-cell syntax parsing. The shared module parses successfully.
- Seven complete model runs were executed: synthetic full and both timing modes across all three interaction specifications, for 49 quantile fits plus seven OLS benchmarks. No fit reached the 10,000-iteration limit.
- The copied report matches the selected source PDF byte-for-byte. Its cover was rendered and visually inspected; it remains unchanged.
- The synthetic summary figure was visually inspected for legibility and layout.

## Fitting diagnostics

| Run | Observations | Design rank/columns | Pseudo R² range | Iteration-limit fits |
|---|---:|---:|---:|---:|
| corrected_full | 5283 | 9/9 | 0.045032–0.127261 | 0 |
| corrected_notebook_reduced | 5283 | 6/6 | 0.044752–0.118526 | 0 |
| corrected_report_reduced | 5283 | 7/7 | 0.044286–0.119768 | 0 |
| demo_notebook | 1199 | 9/9 | 0.064942–0.085387 | 0 |
| historical_full | 5266 | 9/9 | 0.046042–0.126639 | 0 |
| historical_notebook_reduced | 5266 | 6/6 | 0.045060–0.119772 | 0 |
| historical_report_reduced | 5266 | 7/7 | 0.043735–0.120672 | 0 |

Historical full-sample fit at the 5th quantile is **0.126639** and at the median is **0.046042**, consistent with the broad shape and approximate levels described in the report. This comparison does not validate the historical timing specification.

## Comparison to the recovered coefficient export

Compared **63 quantile coefficients** from `reports/historical-tables/qreg_coefs.tex` against the historical full model. The largest absolute difference is **0.02273472**, for the 95th-quantile intercept (export 2.709235; current fit approximately 2.686500). The complete comparison is saved locally at `results/historical_full/reference_comparison.csv`.

An additional run with the old 1,000-iteration limit emitted an IterationLimitWarning at the 95th quantile. Its intercept was approximately 2.701394, so merely reverting the limit does not recreate the historical export exactly. The original software versions and interactive state were not recovered. Exact numerical reproduction is therefore **not claimed**. Historical tables are labeled references; converged current estimates are separate output.

The corrected model changes timing, boundary inclusion and available sample; coefficient differences cannot be attributed solely to the lag correction without a controlled same-sample comparison. No new finding is presented as a result of the original thesis.

Report SHA-256: `8c5881daaeb6a423d67dabbf02522a3193647e6cb03f3437c7a46ee8bb3f4d9c`.

## Limits

No fresh market-data download, raw FX/price verification, out-of-sample portfolio backtest, serial-dependence-robust inference, independent financial review, or hosted GitHub Actions run was performed. CI configuration is supplied and the equivalent local tests/demo have run. The original PDF was not edited. Supporting defense decks were recovered but not reviewed slide by slide.
