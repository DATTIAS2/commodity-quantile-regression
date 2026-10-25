import numpy as np
import pandas as pd
import pytest
from commodity_qr.analysis import prepare_snapshot, pseudo_r2, synthetic_sample, fit_models, add_regimes


def test_corrected_lag_uses_only_past_snapshot_rows():
    # Distinct values expose either an off-by-one error or accidental future data.
    index = pd.bdate_range("2020-01-01", periods=6)
    raw = pd.DataFrame({"r_GSCI": [11., 22., 33., 44., 55., 66.], "r_GSCI_lag": [22., 33., 44., 55., 66., 77.], "r_CAC40": [1., 2., 3., 4., 5., 6.], "VIX": [20.]*6}, index=index)
    frame = prepare_snapshot(raw)
    assert frame.loc[index[2], "r_GSCI"] == 22
    assert frame.loc[index[2], "r_GSCI_lag"] == 11
    assert frame.loc[index[2], "r_CAC40"] == 2
    modified = raw.copy()
    modified.loc[index[3]:, ["r_GSCI", "r_CAC40"]] = 99999
    pd.testing.assert_frame_equal(frame.loc[:index[3]], prepare_snapshot(modified).loc[:index[3]])


def test_check_loss_reference_and_perfect_fit():
    y = np.arange(10.)
    assert pseudo_r2(y, y, .25) == pytest.approx(1.)
    assert pseudo_r2(y, np.full_like(y, np.quantile(y, .25)), .25) == pytest.approx(0.)
    assert np.isnan(pseudo_r2(np.ones(5), np.ones(5), .5))


def test_overlapping_regimes_and_report_boundaries():
    index = pd.to_datetime(["2008-01-01", "2014-01-01", "2020-01-30", "2022-01-03"])
    frame = add_regimes(pd.DataFrame({"r_CAC40": 2.}, index=index))
    assert frame.D2.iloc[0] == 1
    assert frame.D3.iloc[1] == 1
    assert frame.D4.iloc[2] == 1
    assert frame.D4.iloc[3] == frame.D5.iloc[3] == 1
    assert frame.gamma5.iloc[3] == 2


def test_synthetic_pipeline_produces_finite_fits():
    frame = synthetic_sample(n=500)
    coefficients, diagnostics, ols, meta = fit_models(frame, "report_reduced", quantiles=(.1, .5, .9))
    assert np.isfinite(coefficients[["coefficient", "p_value", "ci_low", "ci_high"]]).all().all()
    assert (diagnostics.pseudo_r2 >= -1e-6).all()
    assert not diagnostics.iteration_limit.any()
    assert meta["rank"] == meta["columns"]
