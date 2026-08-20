# [A_test] module_id: MOD-RK-DAT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] 35_drawdown_protocol_impl | §3.12/§3.16/§6.7/§6.13
# [MODULE] tests.risk.test_drawdown_attribution
# [INVARIANTS] 五问任一违例→行为性; VaR恶化前馈优先; dd<5%门控; 相关阈值分流; BIASED最高优先; regime只加后缀
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/test_drawdown_attribution.py
# [TTL] task_bound
"""回撤类型诊断 + 归因自动化测试（35 号 §3.12/§3.16/§6.7/§6.13）。"""

from __future__ import annotations

import pytest

from zephyr.risk.core.daily_auditor import AttributionBias, AttributionStatus
from zephyr.risk.core.drawdown_attribution import (
    DrawdownType,
    InvalidAttributionInputError,
    ResponseRouting,
    diagnose_drawdown_type,
    drawdown_attribution_flow,
)

# 相关性构造（8 点序列，Pearson 解析值）
S_BASE = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
S_SAME = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]  # corr = 1.0 → 系统性
S_MID = [1.0, 2.0, 3.0, 8.0, 7.0, 6.0, 5.0, 4.0]  # corr ≈ 0.518 → MIXED
S_ANTI = [8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]  # corr = -1.0 → 策略特定


def _bias(status: AttributionStatus) -> AttributionBias:
    return AttributionBias(predicted_factor_pct=0.6, actual_factor_pct=0.3, bias=0.3, status=status)


# ── §3.12 五问诊断 ──


class TestDiagnoseDrawdownType:
    def test_all_unknown_undetermined(self):
        d = diagnose_drawdown_type()
        assert d.drawdown_type is DrawdownType.UNDETERMINED
        assert d.violations == ()

    def test_all_clean_statistical(self):
        d = diagnose_drawdown_type(
            signals_follow_rules=True,
            avg_loss_r=1.0,
            position_sizing_consistent=True,
            trade_frequency_in_plan=True,
            market_structure_changed=False,
        )
        assert d.drawdown_type is DrawdownType.STATISTICAL

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"signals_follow_rules": False},
            {"avg_loss_r": 1.5},
            {"position_sizing_consistent": False},
            {"trade_frequency_in_plan": False},
        ],
    )
    def test_any_violation_behavioural(self, kwargs):
        d = diagnose_drawdown_type(**kwargs)
        assert d.drawdown_type is DrawdownType.BEHAVIOURAL
        assert len(d.violations) == 1

    def test_avg_loss_boundary_1_2r_not_violation(self):
        """边界：均损恰 1.2R 不算止损放宽（严格大于才违例）。"""
        d = diagnose_drawdown_type(avg_loss_r=1.2)
        assert d.drawdown_type is DrawdownType.STATISTICAL

    def test_market_structure_changed_not_violation(self):
        """市场结构质变=regime 提示，不构成行为性违例。"""
        d = diagnose_drawdown_type(signals_follow_rules=True, market_structure_changed=True)
        assert d.drawdown_type is DrawdownType.STATISTICAL
        assert d.market_structure_changed is True

    def test_negative_avg_loss_r_raises(self):
        with pytest.raises(InvalidAttributionInputError):
            diagnose_drawdown_type(avg_loss_r=-0.5)


# ── §3.16 归因流程：前馈 VaR 恶化 ──


class TestRiskDeterioration:
    def test_var_ratio_above_1_5_triggers_feedforward(self):
        r = drawdown_attribution_flow(drawdown_pct=-0.02, entry_var=0.02, current_var=0.032)
        assert r is not None
        assert r.response_routing == ResponseRouting.RISK_BASED_REDUCTION.value
        assert r.systemic_pct == 1.0
        assert r.risk_deterioration_ratio == pytest.approx(1.6)
        assert r.recommended_reduction == 0.5  # min(1.6-1, 0.5)
        assert r.root_cause.startswith("RISK_DETERIORATION_VAR_RATIO_")

    def test_var_ratio_below_threshold_falls_through(self):
        """ratio ≤ 1.5 不触发前馈，继续常规门控（dd<5% → None）。"""
        r = drawdown_attribution_flow(drawdown_pct=-0.02, entry_var=0.02, current_var=0.029)
        assert r is None

    def test_missing_or_zero_entry_var_skips_feedforward(self):
        assert drawdown_attribution_flow(drawdown_pct=-0.02, entry_var=None, current_var=0.05) is None
        assert drawdown_attribution_flow(drawdown_pct=-0.02, entry_var=0.0, current_var=0.05) is None


# ── §3.16 归因流程：门控 + 相关性 + 因子 + regime ──


class TestAttributionFlow:
    def test_below_warning_threshold_returns_none(self):
        assert drawdown_attribution_flow(drawdown_pct=-0.049) is None

    def test_single_strategy_specific(self):
        r = drawdown_attribution_flow(drawdown_pct=-0.08, strategy_pnls={"alpha": -5000.0})
        assert r is not None
        assert r.root_cause == "STRATEGY_SPECIFIC_SINGLE_STRATEGY_REGIME_MISALIGNED"
        assert r.per_strategy_contribution == {"alpha": 1.0}
        assert r.response_routing == ResponseRouting.PER_STRATEGY_CONTRACTION.value

    def test_insufficient_history_specific(self):
        r = drawdown_attribution_flow(
            drawdown_pct=-0.08,
            strategy_pnls={"a": -1.0, "b": -2.0},
            strategy_pnls_history=None,
        )
        assert r is not None
        assert r.root_cause.startswith("STRATEGY_SPECIFIC_INSUFFICIENT_HISTORY")

    def test_high_correlation_systemic(self):
        r = drawdown_attribution_flow(
            drawdown_pct=-0.08,
            strategy_pnls={"a": -1.0, "b": -2.0},
            strategy_pnls_history={"a": S_BASE, "b": S_SAME},
            regime="PANIC_CRASH",
        )
        assert r is not None
        assert r.root_cause == "SYSTEMIC_HIGH_CORRELATION_REGIME_ALIGNED"
        assert r.systemic_pct == 1.0
        assert r.response_routing == ResponseRouting.GLOBAL_CONTRACTION.value

    def test_low_correlation_strategy_specific(self):
        r = drawdown_attribution_flow(
            drawdown_pct=-0.08,
            strategy_pnls={"a": -1.0, "b": -2.0},
            strategy_pnls_history={"a": S_BASE, "b": S_ANTI},
        )
        assert r is not None
        assert r.root_cause.startswith("STRATEGY_SPECIFIC_LOW_CORRELATION")
        assert r.systemic_pct == 0.0

    def test_mixed_correlation_split_by_pnl_share(self):
        """MIXED：systemic_pct=avg_corr，贡献按 |pnl| 占比拆分。"""
        r = drawdown_attribution_flow(
            drawdown_pct=-0.08,
            strategy_pnls={"a": -1.0, "b": -3.0},
            strategy_pnls_history={"a": S_BASE, "b": S_MID},
        )
        assert r is not None
        assert r.root_cause.startswith("MIXED_PARTIAL_SYSTEMIC")
        assert r.systemic_pct == pytest.approx(0.5238, abs=1e-3)
        assert r.per_strategy_contribution == pytest.approx({"a": 0.25, "b": 0.75})

    def test_constant_series_correlation_guard(self):
        """除零守卫：常数序列无方差 → 跳过该对 → 保守低相关。"""
        r = drawdown_attribution_flow(
            drawdown_pct=-0.08,
            strategy_pnls={"a": -1.0, "b": -2.0},
            strategy_pnls_history={"a": [1.0] * 10, "b": S_BASE},
        )
        assert r is not None
        assert r.systemic_pct == 0.0  # 无有效相关对 → 0.0 → 策略特定

    def test_attribution_bias_biased_is_top_priority(self):
        """BIASED=行为性最高优先级：覆盖系统性根因 + 停实盘分流。"""
        r = drawdown_attribution_flow(
            drawdown_pct=-0.08,
            strategy_pnls={"a": -1.0, "b": -2.0},
            strategy_pnls_history={"a": S_BASE, "b": S_SAME},
            attribution_bias=_bias(AttributionStatus.BIASED),
            regime="CRISIS",
        )
        assert r is not None
        assert r.root_cause == "BEHAVIOURAL_ATTRIBUTION_BIAS_REGIME_ALIGNED"
        assert r.response_routing == ResponseRouting.STOP_LIVE_AND_FIX_EXECUTION.value
        assert r.attribution_bias is not None

    def test_attribution_bias_aligned_keeps_root_cause(self):
        r = drawdown_attribution_flow(
            drawdown_pct=-0.08,
            strategy_pnls={"a": -1.0, "b": -2.0},
            strategy_pnls_history={"a": S_BASE, "b": S_SAME},
            attribution_bias=_bias(AttributionStatus.ALIGNED),
        )
        assert r is not None
        assert r.root_cause.startswith("SYSTEMIC_HIGH_CORRELATION")

    def test_regime_suffix_misaligned_when_none(self):
        r = drawdown_attribution_flow(drawdown_pct=-0.08, strategy_pnls={"a": -1.0})
        assert r is not None
        assert r.root_cause.endswith("_REGIME_MISALIGNED")

    def test_to_dict_serializable(self):
        r = drawdown_attribution_flow(
            drawdown_pct=-0.08,
            strategy_pnls={"a": -1.0},
            attribution_bias=_bias(AttributionStatus.ALIGNED),
        )
        assert r is not None
        d = r.to_dict()
        assert d["response_routing"] == ResponseRouting.PER_STRATEGY_CONTRACTION.value
        assert d["attribution_bias"]["status"] == "ALIGNED"

    def test_invalid_thresholds_raise(self):
        with pytest.raises(InvalidAttributionInputError):
            drawdown_attribution_flow(drawdown_pct=-0.08, warning_threshold=1.5)
        with pytest.raises(InvalidAttributionInputError):
            drawdown_attribution_flow(drawdown_pct=-0.08, var_deterioration_threshold=1.0)
        with pytest.raises(InvalidAttributionInputError):
            drawdown_attribution_flow(drawdown_pct=-0.08, systemic_corr=0.3, specific_corr=0.5)
