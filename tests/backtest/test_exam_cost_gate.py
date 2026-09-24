# [A_test] module_id: zephyr.backtest.regime_validation.exam_cost_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-IBT-COSTGATE | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_exam_cost_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; zephyr.backtest.regime_validation.exam_cost_gate
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/backtest/test_exam_cost_gate.py
# [MATURITY] testing
# [INVARIANTS] 纯函数测试零 IO；判定只收数字证据；fail-closed 语义（缺证据=不通过）；4440 照妖镜复形=高换手必拦
# [MODIFY-GUARD] 批C 考尺成本门（st-ibt-remedy-cf-20260923）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_exam_cost_gate.py — E4 考尺成本门（批C）正反例。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.regime_validation.exam_cost_gate import (
    CostGateConfig,
    evaluate_exam_cost_gate,
    run_cost_tier_scan,
)

CFG = CostGateConfig()


def _monotone_tier_sharpes() -> dict[float, float]:
    return {0.0: 0.80, 5.0: 0.62, 10.0: 0.45, 20.0: 0.18, 40.0: -0.05}


class TestConfigValidation:
    def test_rejects_non_ascending_tiers(self):
        with pytest.raises(ValueError):
            CostGateConfig(tiers_bp=(0.0, 10.0, 5.0, 20.0, 40.0))

    def test_rejects_missing_zero_cost_tier(self):
        with pytest.raises(ValueError):
            CostGateConfig(tiers_bp=(5.0, 10.0, 20.0, 40.0))

    def test_rejects_nonpositive_cap(self):
        with pytest.raises(ValueError):
            CostGateConfig(turnover_cap_annual_x=0.0)


class TestEvaluateCostGate:
    def test_pass_case(self):
        v = evaluate_exam_cost_gate(_monotone_tier_sharpes(), 0.016, 400, CFG)
        # 0.016×244=3.904x ≤ 8x；40bp 档 -0.05 < 0 → 存活地板不过
        assert v.passed is False and v.monotonic is True and v.full_cost_survived is False

    def test_pass_surviving_monotone_low_turnover(self):
        tiers = {0.0: 0.80, 5.0: 0.70, 10.0: 0.60, 20.0: 0.45, 40.0: 0.30}
        v = evaluate_exam_cost_gate(tiers, 0.02, 400, CFG)  # 4.88x
        assert v.passed is True and v.turnover_within_cap is True
        assert v.reasons and "成本门通过" in v.reasons[-1]

    def test_monotonicity_violation_fails(self):
        tiers = {0.0: 0.40, 5.0: 0.50, 10.0: 0.60, 20.0: 0.70, 40.0: 0.90}  # 成本升收益升=前视嫌疑
        v = evaluate_exam_cost_gate(tiers, 0.01, 400, CFG)
        assert v.passed is False and v.monotonic is False
        assert any("单调性破缺" in r for r in v.reasons)

    def test_e7_turnover_gate_blocks_high_turnover(self):
        """照妖镜复形：4440 型超短高频（年化 30x+）必被换手门拦截。"""
        v = evaluate_exam_cost_gate(_monotone_tier_sharpes(), 0.13, 400, CFG)  # 0.13×244≈31.7x
        assert v.passed is False and v.turnover_within_cap is False
        assert any("E7 换手门" in r for r in v.reasons)
        assert v.annual_turnover_x > 30

    def test_insufficient_days_fail_closed(self):
        v = evaluate_exam_cost_gate(_monotone_tier_sharpes(), 0.01, 30, CFG)
        assert v.passed is False
        assert any("证据不足" in r for r in v.reasons)


class TestTierScan:
    def test_scan_uses_injected_net_fn(self):
        idx = pd.date_range("2024-01-01", periods=120, freq="B")
        weights = pd.DataFrame({"A": [0.5] * 120}, index=idx)
        px = pd.DataFrame({"A": np.linspace(10, 12, 120)}, index=idx)

        calls: list[float] = []

        def fake_net(w, px_, gate_limits=True, slippage_bp=None):
            # 形参序/默认值刻意与引擎 daily_net_returns 同构：原桩 (w, px_, slip_bp)
            # 三个位置参恰好掩盖了调用方位置传参的缺陷（哑门由此漏网）。
            assert gate_limits is True, "gate_limits 被滑点档污染=传参错位复发"
            slip_bp = slippage_bp
            calls.append(float(slip_bp))
            base = pd.Series(0.001, index=w.index)
            return base - float(slip_bp) * 1e-4  # 滑点越高净收益越低（单调）

        out = run_cost_tier_scan(weights, px, fake_net, CFG)
        assert calls == list(CFG.tiers_bp) and 0.0 in out
        vals = [out[b] for b in sorted(out)]
        assert vals == sorted(vals, reverse=True), "注入单调函数应产出单调递减 sharpe"
