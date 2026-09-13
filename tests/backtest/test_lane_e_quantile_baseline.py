# [BLUEPRINT] MOD-BT-085 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_lane_e_quantile_baseline
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; scripts.backtest.lane_e_quantile_baseline
# [CONSUMERS] lane_e_quantile_baseline 质量守卫
# [STARTUP] manual
# [INVARIANTS] 合成数据测试（不连 CH）；评估双标准=覆盖率接近名义+锐度非负
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-085 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""车道 E 分位数基线质量守卫——评估函数+run 档案步骤 filename 修正回归。"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys_path = str(Path(__file__).resolve().parents[2] / "scripts" / "backtest")
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from lane_e_quantile_baseline import QUANTILES, evaluate  # noqa: E402


def _synthetic_pred_realized(n: int = 500, seed: int = 42):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2022-01-03", periods=n)
    realized = pd.Series(rng.normal(0.0003, 0.012, n), index=dates)
    q05 = realized - 0.02 + rng.normal(0, 0.002, n)
    q50 = realized + rng.normal(0, 0.001, n)
    q95 = realized + 0.02 + rng.normal(0, 0.002, n)
    pred = pd.DataFrame({"q05": q05, "q50": q50, "q95": q95}, index=dates)
    return pred, realized


class TestEvaluateDualStandard:
    def test_structure(self):
        pred, realized = _synthetic_pred_realized()
        ev = evaluate(pred, realized)
        assert ev["n"] > 0
        assert 0 <= ev["coverage_low_nominal_5pct"] <= 1
        assert 0 <= ev["coverage_inside_nominal_90pct"] <= 1
        assert ev["interval_mean_width"] > 0
        assert "pinball_median" in ev

    def test_calibration_reasonable(self):
        pred, realized = _synthetic_pred_realized()
        ev = evaluate(pred, realized)
        # 名义 90% 区间，合成数据下覆盖率应在 80-100%（宽松容忍，窄分布数据可能 100%）
        assert 0.80 <= ev["coverage_inside_nominal_90pct"] <= 1.0

    def test_empty_intersection_rejected(self):
        pred = pd.DataFrame({"q05": [1], "q50": [1], "q95": [1]}, index=[0])
        realized = pd.Series([0.01], index=[999])
        with pytest.raises(Exception):
            evaluate(pred, realized)
