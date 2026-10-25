# Data provenance and local inputs

## Available snapshot

`data/local/df3.csv` is a local-only copy of the original derived Yahoo Finance analysis dataset. The original notebook requests `^SPGSCI`, `^FCHI`, `^VIX` and `EURUSD=X` from 1 January 1990 up to (exclusive) 30 March 2025. The aligned saved sample actually starts in December 2003. The code divides GSCI USD levels by EURUSD to express GSCI in EUR, computes shifted daily returns scaled by 252, and adds overlapping regime indicators and interactions.

That provenance is recovered from code; no independent provider download was performed during cleanup. Exact provider revision, download date, index return variant and adjustment settings cannot be established from this derived CSV. A later download need not reproduce historical quotes. No credentials or live external feeds are needed for the offline demo.

Required CSV columns:

| Column | Meaning in recovered snapshot |
|---|---|
| Date | Sorted unique observation date |
| r_GSCI | Following-observation commodity simple return × 252 |
| r_GSCI_lag | Next row's r_GSCI, despite its name |
| r_CAC40 | Following-observation CAC40 simple return × 252 |
| VIX | VIX close at labeled date |

Additional saved columns include r_CAC40_lag, D1–D5 and gamma1–gamma5. The shared code rebuilds the regime interactions. See `docs/reconciliation.md` before interpreting any returns.

To reproduce locally, obtain an authorized copy of the exact original CSV, place it at `data/local/df3.csv`, and run the snapshot notebook. To run without it, use the synthetic notebook. The synthetic observations are generated deterministically with seed 42 and cannot substantiate any thesis conclusion.

## Material excluded from the upload folder

The original folder also contains two exports with mnemonic/company identifiers (`tsmcvk6kwhxttflp.csv`, `sradk2tvrcmqlkqr.csv`), an ECB rate export, and an unrelated fractional Brownian simulation CSV. Their provenance or relevance differs; they are preserved in the private source archive and not bundled as thesis input. No redistribution rights are assumed for provider exports or the Yahoo-derived snapshot. Publication of a data snapshot is a separate decision from using the author's report/code.

Future exact reproduction should record raw price/FX files, the download timestamp, index variant, provider configuration and checksums, plus a clear transformation log. Those missing inputs are not invented here.
