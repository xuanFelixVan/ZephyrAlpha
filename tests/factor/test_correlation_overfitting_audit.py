# [A_test] module_id: MOD-GOV_test_correlation_overfitting_audit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_correlation_overfitting_audit
# [TESTS] src/zephyr/factor/analysis/correlation_overfitting_audit.py
# [TTL] task_bound
"""23 号 memo §3.3 过拟合检测引擎测试（PDR/PSI/DFR + audit 三态）。

裁定真源：23_strategy_correlation_validation.md §3.1⑤ 第 6 部分 / §3.2——
  PDR<0.5 / PSI_param<3.0 / DFR≥30 / DSR≥0.95 / PBO<0.05 / 斜率>0 /
  胜率>70% 或 PF>3.0 软警告；任一 fail 即不上线（保守）。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.factor.analysis.correlation_overfitting_audit import (
    OverfitVerdict,
    audit,
    check_extreme_backtest_metrics,
    compute_degrees_of_freedom_ratio,
    compute_oos_degradation_slope,
    compute_parameter_stability_index,
    compute_pdr,
)


class TestThreeCoreMetrics:
    def test_pdr_boundaries(self):
        assert compute_pdr(2.0, 1.5) == pytest.approx(0.25)
        assert compute_pdr(2.0, 1.0) == pytest.approx(0.5)  # 边界=fail（<0.5 才通过）
        assert compute_pdr(2.0, -0.5) == pytest.approx(1.25)  # 负 OOS → PDR>1
        assert compute_pdr(0.0, 1.0) == 1.0  # 无 IS edge 约定全额退化
        assert compute_pdr(-1.0, 0.5) == 1.0

    def test_parameter_stability_index(self):
        assert compute_parameter_stability_index(3.0, 1.5) == pytest.approx(2.0)
        assert compute_parameter_stability_index(3.0, 0.0) == float("inf")  # 均值无 edge
        assert compute_parameter_stability_index(3.0, -0.5) == float("inf")

    def test_degrees_of_freedom_ratio(self):
        assert compute_degrees_of_freedom_ratio(300, 10) == pytest.approx(30.0)
        assert compute_degrees_of_freedom_ratio(90, 3) == pytest.approx(30.0)
        with pytest.raises(ValueError):
            compute_degrees_of_freedom_ratio(100, 0)
        with pytest.raises(ValueError):
            compute_degrees_of_freedom_ratio(0, 5)


class TestSlopeAndWarnings:
    def test_oos_degradation_slope(self):
        is_sr = [1.0, 2.0, 3.0, 4.0]
        oos_sr = [0.5, 1.0, 1.5, 2.0]  # 斜率 0.5>0
        assert compute_oos_degradation_slope(is_sr, oos_sr) == pytest.approx(0.5)
        assert compute_oos_degradation_slope([2.0, 2.0], [1.0, 1.0]) == 0.0  # IS 无变异
        with pytest.raises(ValueError):
            compute_oos_degradation_slope([1.0], [1.0])
        with pytest.raises(ValueError):
            compute_oos_degradation_slope([1.0, 2.0], [1.0])

    def test_extreme_metrics_warnings(self):
        assert check_extreme_backtest_metrics(0.75, None)  # 胜率>70%
        assert check_extreme_backtest_metrics(None, 3.5)  # PF>3.0
        assert not check_extreme_backtest_metrics(0.60, 2.0)
        assert not check_extreme_backtest_metrics(None, None)


class TestAudit:
    def test_all_pass_likely_real(self):
        res = audit(2.0, 1.6, 500, 10, best_sharpe=2.0, avg_sharpe=1.2, dsr=0.97, pbo=0.01)
        assert res.verdict is OverfitVerdict.LIKELY_REAL
        assert all(res.checks.values())
        assert res.metrics["pdr"] == pytest.approx(0.2)
        assert res.metrics["dfr"] == pytest.approx(50.0)

    def test_any_hard_fail_likely_overfit(self):
        # PDR = (2.0-0.5)/2.0 = 0.75 ≥ 0.5 → fail
        res = audit(2.0, 0.5, 500, 10, best_sharpe=2.0, avg_sharpe=1.2, dsr=0.99)
        assert res.verdict is OverfitVerdict.LIKELY_OVERFIT
        assert not res.checks["pdr"]
        # DSR fail 同样一票否决
        res2 = audit(2.0, 1.6, 500, 10, best_sharpe=2.0, avg_sharpe=1.2, dsr=0.80)
        assert res2.verdict is OverfitVerdict.LIKELY_OVERFIT
        # DFR<30 fail
        res3 = audit(2.0, 1.6, 100, 10, best_sharpe=2.0, avg_sharpe=1.2)
        assert res3.verdict is OverfitVerdict.LIKELY_OVERFIT

    def test_warning_downgrades_to_inconclusive(self):
        res = audit(2.0, 1.6, 500, 10, best_sharpe=2.0, avg_sharpe=1.2, win_rate=0.75)
        assert res.verdict is OverfitVerdict.INCONCLUSIVE
        assert res.warnings

    def test_slope_check_integrated(self):
        rng = np.random.default_rng(1)
        is_sr = list(rng.uniform(1.0, 3.0, 8))
        oos_sr = [0.6 * v for v in is_sr]  # 正斜率
        res = audit(
            2.0,
            1.6,
            500,
            10,
            best_sharpe=2.0,
            avg_sharpe=1.2,
            trial_is_sharpes=is_sr,
            trial_oos_sharpes=oos_sr,
        )
        assert res.checks["oos_degradation_slope"]
        assert res.verdict is OverfitVerdict.LIKELY_REAL
