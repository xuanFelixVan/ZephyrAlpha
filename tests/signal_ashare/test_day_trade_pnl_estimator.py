# [BLUEPRINT] MOD-SIG-132 | docs/03_modules/_domain_signal/day_trade_pnl_estimator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-132 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_day_trade_pnl_estimator
# [TESTS] src/zephyr/signal_ashare/day_trade_pnl_estimator.py
"""MOD-SIG-132 单元测试：day_trade_pnl_estimator 做T盈亏预估器。

蓝图验收（B11-02600/CAND-TESTB-055，A7 技能day-trade-pnl-estimate）：
做T净盈亏预估=价差-双边佣金-印花税-冲击成本（四要素费率注入）+
置信度（历史相似价差实现率滚动统计）+
成交回写校准（预估vs实现偏差滚动校正冲击系数）。
时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.day_trade_pnl_estimator",
    reason="day_trade_pnl_estimator not importable",
)

from zephyr.signal_ashare.day_trade_pnl_estimator import (  # noqa: E402
    DayTradeFeeModel,
    DayTradeFillRecord,
    DayTradePnlConfig,
    DayTradePnlError,
    DayTradePnlEstimate,
    DayTradePnlEstimator,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

_FEES = DayTradeFeeModel(
    commission_rate=0.00025,
    stamp_tax_rate=0.0005,
    impact_rate=0.001,
)


def _est(**cfg_kwargs) -> DayTradePnlEstimator:
    return DayTradePnlEstimator(
        fee_model=_FEES,
        config=DayTradePnlConfig(**cfg_kwargs),
        clock=lambda: _T0,
    )


# ----------------------------------------------------------------------
# 费率模型 / 配置 Fail-Closed
# ----------------------------------------------------------------------
def test_fee_model_negative_rate_rejected() -> None:
    with pytest.raises(DayTradePnlError):
        DayTradeFeeModel(commission_rate=-0.1, stamp_tax_rate=0.0, impact_rate=0.0)
    with pytest.raises(DayTradePnlError):
        DayTradeFeeModel(commission_rate=0.0, stamp_tax_rate=0.0, impact_rate=0.0, min_commission=-1.0)


def test_estimator_requires_fee_model() -> None:
    with pytest.raises(DayTradePnlError):
        DayTradePnlEstimator(fee_model=None, clock=lambda: _T0)


def test_config_invalid_rejected() -> None:
    with pytest.raises(DayTradePnlError):
        DayTradePnlConfig(calibration_window=0)
    with pytest.raises(DayTradePnlError):
        DayTradePnlConfig(mult_min=2.0, mult_max=1.0)


# ----------------------------------------------------------------------
# 预估四要素成本
# ----------------------------------------------------------------------
def test_estimate_net_pnl_breakdown() -> None:
    e = _est().estimate(10.0, 10.2, 1000)
    assert isinstance(e, DayTradePnlEstimate)
    assert e.gross_spread == pytest.approx(200.0)
    assert e.commission == pytest.approx(2.5 + 2.55)
    assert e.stamp_tax == pytest.approx(5.1)
    assert e.impact_cost == pytest.approx(20.2)
    assert e.net_pnl == pytest.approx(200.0 - 5.05 - 5.1 - 20.2)
    assert e.spread_ratio == pytest.approx(0.02)
    assert e.impact_multiplier == pytest.approx(1.0)
    assert e.estimated_at == _T0


def test_stamp_tax_only_on_sell_side() -> None:
    e = _est().estimate(10.0, 10.0, 1000)
    assert e.gross_spread == pytest.approx(0.0)
    assert e.stamp_tax == pytest.approx(10000 * 0.0005)


def test_min_commission_applied_per_side() -> None:
    fees = DayTradeFeeModel(commission_rate=0.00025, stamp_tax_rate=0.0005, impact_rate=0.0, min_commission=5.0)
    est = DayTradePnlEstimator(fee_model=fees, clock=lambda: _T0)
    e = est.estimate(10.0, 10.2, 100)  # 单边佣金0.25 < 最低5
    assert e.commission == pytest.approx(10.0)


def test_estimate_confidence_zero_without_fills() -> None:
    e = _est().estimate(10.0, 10.2, 1000)
    assert e.confidence == pytest.approx(0.0)
    assert e.confidence_samples == 0


@pytest.mark.parametrize(
    "buy,sell,shares",
    [
        (0.0, 10.2, 1000),
        (-1.0, 10.2, 1000),
        (10.0, float("nan"), 1000),
        (10.0, 10.2, 0),
        (10.0, 10.2, -100),
        (10.0, 10.2, 2.5),
    ],
)
def test_estimate_invalid_input_rejected(buy, sell, shares) -> None:
    with pytest.raises(DayTradePnlError):
        _est().estimate(buy, sell, shares)


# ----------------------------------------------------------------------
# 成交回写 / 置信度
# ----------------------------------------------------------------------
def test_record_fill_returns_record() -> None:
    est = _est()
    rec = est.record_fill(10.0, 10.2, 1000, realized_net=160.0)
    assert isinstance(rec, DayTradeFillRecord)
    assert rec.estimated_net == pytest.approx(169.65)
    assert rec.realized_net == pytest.approx(160.0)
    assert rec.filled_at == _T0
    assert est.fill_count == 1
    assert est.fills() == (rec,)


def test_confidence_realized_similar_spread() -> None:
    est = _est()
    est.record_fill(10.0, 10.2, 1000, realized_net=160.0)  # >=0.8*预估 → 实现
    e = est.estimate(10.0, 10.2, 1000)
    assert e.confidence_samples == 1
    assert e.confidence == pytest.approx(1.0)


def test_confidence_not_realized_when_below_threshold() -> None:
    est = _est()
    est.record_fill(10.0, 10.2, 1000, realized_net=100.0)  # <0.8*169.65
    e = est.estimate(10.0, 10.2, 1000)
    assert e.confidence_samples == 1
    assert e.confidence == pytest.approx(0.0)


def test_confidence_ignores_dissimilar_spread() -> None:
    est = _est()
    est.record_fill(10.0, 10.2, 1000, realized_net=160.0)  # 价差2%
    e = est.estimate(10.0, 10.5, 1000)  # 价差5% 超出容差
    assert e.confidence_samples == 0
    assert e.confidence == pytest.approx(0.0)


def test_record_fill_invalid_realized_rejected() -> None:
    est = _est()
    with pytest.raises(DayTradePnlError):
        est.record_fill(10.0, 10.2, 1000, realized_net=float("nan"))


# ----------------------------------------------------------------------
# 冲击系数校准
# ----------------------------------------------------------------------
def test_calibration_multiplier_increases_on_shortfall() -> None:
    est = _est()
    est.record_fill(10.0, 10.2, 1000, realized_net=160.0)
    # 偏差率≈9.65/20200 → 倍率≈1+0.4777
    assert est.impact_multiplier == pytest.approx(1.0 + (9.65 / 20200.0) / 0.001)
    e = est.estimate(10.0, 10.2, 1000)
    assert e.impact_cost == pytest.approx(20.2 * est.impact_multiplier)
    assert e.impact_multiplier == pytest.approx(est.impact_multiplier)


def test_calibration_multiplier_decreases_on_overestimate() -> None:
    est = _est()
    est.record_fill(10.0, 10.2, 1000, realized_net=175.0)  # 实现优于预估
    assert est.impact_multiplier == pytest.approx(1.0 + (-5.35 / 20200.0) / 0.001)
    assert est.impact_multiplier < 1.0


def test_calibration_multiplier_clamped_max() -> None:
    est = _est()
    est.record_fill(10.0, 10.2, 1000, realized_net=100.0)  # 大偏差
    assert est.impact_multiplier == pytest.approx(3.0)


def test_calibration_multiplier_clamped_min() -> None:
    est = _est()
    est.record_fill(10.0, 10.2, 1000, realized_net=250.0)  # 远超预估
    assert est.impact_multiplier == pytest.approx(0.5)


def test_calibration_window_trims_oldest() -> None:
    est = _est(calibration_window=2)
    est.record_fill(10.0, 10.2, 1000, realized_net=100.0)
    est.record_fill(10.0, 10.2, 1000, realized_net=160.0)
    est.record_fill(10.0, 10.2, 1000, realized_net=160.0)
    assert est.fill_count == 2
    # 窗口内两笔均为 realized=160，但倍率钳制仍按窗口均值
    assert est.impact_multiplier <= 3.0
    assert est.impact_multiplier >= 0.5


def test_zero_impact_rate_keeps_multiplier_one() -> None:
    fees = DayTradeFeeModel(commission_rate=0.00025, stamp_tax_rate=0.0005, impact_rate=0.0)
    est = DayTradePnlEstimator(fee_model=fees, clock=lambda: _T0)
    est.record_fill(10.0, 10.2, 1000, realized_net=0.0)
    assert est.impact_multiplier == pytest.approx(1.0)


# ----------------------------------------------------------------------
# 确定性
# ----------------------------------------------------------------------
def test_determinism_same_ops_same_result() -> None:
    def run() -> tuple:
        est = _est()
        e1 = est.estimate(10.0, 10.2, 1000)
        est.record_fill(10.0, 10.2, 1000, realized_net=160.0)
        e2 = est.estimate(10.0, 10.2, 1000)
        return (e1.net_pnl, e2.net_pnl, e2.confidence, e2.impact_multiplier)

    assert run() == run()
