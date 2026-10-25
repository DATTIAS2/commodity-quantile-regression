# Report and notebook reconciliation

## Source selection

The canonical report is the 46-page Desktop `Thesis_Master_David_ATTIAS.pdf`, modified 2 June 2025. Its signed declaration is dated 8 May 2025. A different 46-page copy exists inside `THESIS ESCP`; several earlier 25–41-page drafts are in Downloads. The retained report is unmodified.

Primary implementation: `QREG CAC.ipynb` (40 cells) and `QREG CAC copy.ipynb` (18 cells), last modified 16 May 2025. The CSV snapshot contains 5,285 aligned rows from 1 December 2003 through 26 March 2025. Originals, data exports, supporting examples and both defense decks are preserved outside the upload folder in the sibling `thesis-source-archive`, with hashes and original paths in its source inventory.

## Correspondence

| Report material | Original implementation | Consolidated treatment |
|---|---|---|
| Data exploration, tables 1 and figures 2–4 | CAC full notebook; CAC copy correlation/distribution plots | Local snapshot retained; units and sample trimming explained below |
| QAR equation 4.2.1; table 5 | CAC full notebook, gamma1–gamma5 | `full` specification; historical and corrected timing |
| Reduced model, table 6 | Report keeps gamma1, gamma2, gamma4 | `report_reduced`; this specification is absent from the retained reduced notebook |
| Alternative reduced analysis | CAC copy keeps gamma3, gamma5 | `notebook_reduced`; not mislabeled as report table 6 |
| Figures 8–9, coefficient paths and pseudo R² | Both CAC notebooks, repeated fitting and plotting | Shared fitting/export function; one fit per quantile, confidence intervals and convergence diagnostics |
| Figure 6, CAPM illustration | `example2.ipynb` | Archived; not promoted as a validated empirical result |
| French sector chart | `piechart.ipynb` | Archived; depends on undefined sizes/colors/labels |
| DAX and Euro Stoxx | `QREG DAX.ipynb`, `QUANTILE REG-1.ipynb` | Exploratory predecessors, outside the final CAC40 scope |

## Timing correction

Original code computes `r_GSCI[t] = 252 * (P[t+1] / P[t] - 1)` and then `r_GSCI_lag = r_GSCI.shift(-1)`. Therefore the regressor actually contains the subsequent return. The recovered CSV verifies the equality to the next row exactly, with maximum absolute difference zero.

Historical mode intentionally retains that column for an audit. Corrected mode shifts the commodity and CAC40 return series down one row so they are returns ending on date t, then constructs `r_GSCI_lag = r_GSCI.shift(1)`. VIX stays on t. The first two rows are lost. This changes the research specification and potentially its conclusions. It is explicitly a same-day explanatory model, not a forecast.

The correction is relative to the aligned observations in the snapshot. Underlying asset prices, FX levels and independently recorded trading sessions are absent, so upstream construction and exact calendar-day returns cannot be independently audited from the snapshot alone.

## Units and sample

The code uses daily simple returns multiplied by **252**, not daily percentage returns (which would use 100) and not log returns. Preserve that scale for historical comparability. The report's percentage-point labels are inconsistent with this calculation; rolling standard deviations are also described as variances in parts of the report. VIX is an index level, not a realized return or volatility of CAC40.

The full notebook saves `df3.csv` before computing 20-observation rolling volatility and dropping its first 19 rows. Its fitted historical sample is therefore **5,266 rows, 30 December 2003–26 March 2025**. Historical mode preserves that trimming; corrected mode uses all available correctly aligned observations. The reduced notebook loads the pre-trim CSV, creating an additional sample difference. The consolidated variants intentionally share a sample within each timing mode so interaction-set comparisons are interpretable; they are not exact replays of every original cell execution.

## Regimes

| Term | Report date window (inclusive) |
|---|---|
| gamma1 | 1 January 2004–31 December 2013 |
| gamma2 | 1 January 2008–31 December 2009 |
| gamma3 | 1 January 2014–30 June 2017 |
| gamma4 | 30 January 2020–1 June 2022 |
| gamma5 | 17 December 2021 onward |

Original code excludes the first day for gamma2–gamma4 using strict greater-than comparisons. Historical mode preserves those comparisons; corrected mode follows the report's inclusive dates. Regimes overlap deliberately. Rank and condition number are reported rather than assuming that dropping particular regressors solves identification. Pre-2004 support is extremely short in the recovered snapshot.

## Other corrections and unresolved research issues

- Removed dependencies on out-of-order cells and repeated imports/fits; central exports use explicit output directories.
- `OLS.tex` in the originals contains descriptive statistics instead of OLS results. New OLS exports use the fitted model.
- Default solver limit increased from 1,000 to 10,000 iterations; all warnings and counts are recorded. Historical audits may differ from stopped original iterates and across library versions; see validation.
- Original cross-quantile Wald tests sum separate covariance matrices despite estimates sharing observations. They are omitted. Valid joint inference requires a suitable joint estimator or resampling design.
- Current confidence intervals and p-values use statsmodels' default robust QuantReg convention. They do not establish robustness to general time-series dependence. No causal or tradable-strategy claim is made.
- Pseudo R² uses the check-loss intercept-only benchmark, not ordinary R². Its tail shape alone does not establish portfolio diversification benefits or crisis protection.
- `example.ipynb` initially fits a normal target while plotting Pareto observations and uses plotting imports from interactive state. Its teaching content is replaced by an explicitly synthetic reproducible workflow; it is not treated as an original contribution.
- `example2.ipynb` expects `ESTR.csv`, although the local file has a different name, mixes annualized-decimal returns and rate quotations, interpolates data, and appears to reverse X/Y in its OLS setup. It is archived for future revision.
- The report's text around interaction labels and reduced-model coefficient directions is not fully consistent with its tables. Keep the submitted report unchanged and use computed labeled tables when interpreting new analyses.
