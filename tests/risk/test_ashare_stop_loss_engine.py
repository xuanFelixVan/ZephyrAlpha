# [BLUEPRINT] MOD-RK-09 | docs/03_modules/_domain_risk/ashare_stop_loss_engine/blueprint.md | §
# [TTL] permanent
"""AshareStopLossRuleEngine 单元测试 (MOD-RK-09)。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from zephyr.risk.core.ashare_stop_loss_engine import (
    AshareStopLossConfig,
    AshareStopLossRuleEngine,
    InvalidStopLossInputError,
    LossLimitAlert,
    LossLimitLevel,
    StopLossSeverity,
    StopLossSignal,
    StopLossTriggerType,
)

T0 = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)


def t(offset_seconds: float = 0.0) -> datetime:
    return T0 + timedelta(seconds=offset_seconds)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_default_thresholds():
    cfg = AshareStopLossConfig()
    assert cfg.fixed_pct_threshold == pytest.approx(0.07)
    assert cfg.daily_loss_limit == pytest.approx(0.02)
    assert cfg.weekly_loss_limit == pytest.approx(0.05)
    assert cfg.monthly_loss_limit == pytest.approx(0.10)
    assert cfg.daily_halt_days == 1
    assert cfg.weekly_halt_days == 2
    assert cfg.monthly_halt_days == 3


def test_config_invalid_fixed_pct_threshold():
    with pytest.raises(InvalidStopLossInputError):
        AshareStopLossConfig(fixed_pct_threshold=0)


def test_config_invalid_loss_limit_not_increasing():
    with pytest.raises(InvalidStopLossInputError, match="must be increasing"):
        AshareStopLossConfig(
            daily_loss_limit=0.05,
            weekly_loss_limit=0.05,
            monthly_loss_limit=0.10,
        )


def test_config_halt_days_not_decreasing():
    with pytest.raises(InvalidStopLossInputError, match="non-decreasing"):
        AshareStopLossConfig(
            daily_halt_days=3,
            weekly_halt_days=2,
            monthly_halt_days=1,
        )


# ── 1. 固定比例-7% ────────────────────────────────────────────────────────────


def test_fixed_pct_triggered_at_threshold():
    engine = AshareStopLossRuleEngine()
    # 买入 100, 当前 93 → 亏损 7%
    signals = engine.check_position("600519", 100.0, 93.0, now=t())
    fixed = [s for s in signals if s.trigger_type is StopLossTriggerType.FIXED_PCT]
    assert len(fixed) == 1
    assert fixed[0].severity is StopLossSeverity.CRITICAL
    assert fixed[0].trigger_value == pytest.approx(0.07)
    assert fixed[0].threshold == pytest.approx(0.07)
    assert fixed[0].is_critical is True


def test_fixed_pct_not_triggered_below_threshold():
    engine = AshareStopLossRuleEngine()
    # 亏损 6.9% < 7%
    signals = engine.check_position("600519", 100.0, 93.1, now=t())
    fixed = [s for s in signals if s.trigger_type is StopLossTriggerType.FIXED_PCT]
    assert len(fixed) == 0


def test_fixed_pct_triggered_with_large_loss():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("000001", 10.0, 8.5, now=t())
    fixed = [s for s in signals if s.trigger_type is StopLossTriggerType.FIXED_PCT]
    assert len(fixed) == 1
    assert fixed[0].trigger_value == pytest.approx(0.15, abs=1e-6)


# ── 2. 关键支撑破位 ───────────────────────────────────────────────────────────


def test_support_break_triggered():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 16.5, support_level=16.8, now=t())
    sb = [s for s in signals if s.trigger_type is StopLossTriggerType.SUPPORT_BREAK]
    assert len(sb) == 1
    assert sb[0].severity is StopLossSeverity.CRITICAL
    assert sb[0].trigger_value == pytest.approx(16.5)
    assert sb[0].threshold == pytest.approx(16.8)


def test_support_break_not_triggered_above():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 17.0, support_level=16.8, now=t())
    sb = [s for s in signals if s.trigger_type is StopLossTriggerType.SUPPORT_BREAK]
    assert len(sb) == 0


def test_support_break_skipped_when_none():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 93.0, now=t())
    sb = [s for s in signals if s.trigger_type is StopLossTriggerType.SUPPORT_BREAK]
    assert len(sb) == 0


def test_support_break_invalid_level():
    engine = AshareStopLossRuleEngine()
    with pytest.raises(InvalidStopLossInputError):
        engine.check_position("X", 100.0, 90.0, support_level=0, now=t())


# ── 3. 逻辑失效 ───────────────────────────────────────────────────────────────


def test_logic_invalidation_triggered():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 99.0, logic_valid=False, now=t())
    li = [s for s in signals if s.trigger_type is StopLossTriggerType.LOGIC_INVALIDATION]
    assert len(li) == 1
    assert li[0].severity is StopLossSeverity.WARNING


def test_logic_invalidation_skipped_when_true():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 99.0, logic_valid=True, now=t())
    li = [s for s in signals if s.trigger_type is StopLossTriggerType.LOGIC_INVALIDATION]
    assert len(li) == 0


def test_logic_invalidation_skipped_when_none():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 99.0, now=t())
    li = [s for s in signals if s.trigger_type is StopLossTriggerType.LOGIC_INVALIDATION]
    assert len(li) == 0


# ── 4. 竞价不及预期 ───────────────────────────────────────────────────────────


def test_auction_disappoint_triggered():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position(
        "600519",
        100.0,
        95.0,
        auction_expected_price=100.0,
        auction_actual_price=97.5,
        now=t(),
    )
    ad = [s for s in signals if s.trigger_type is StopLossTriggerType.AUCTION_DISAPPOINT]
    assert len(ad) == 1
    assert ad[0].severity is StopLossSeverity.WARNING
    assert ad[0].trigger_value == pytest.approx(0.025)


def test_auction_disappoint_not_triggered():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position(
        "600519",
        100.0,
        99.0,
        auction_expected_price=100.0,
        auction_actual_price=99.5,
        now=t(),
    )
    ad = [s for s in signals if s.trigger_type is StopLossTriggerType.AUCTION_DISAPPOINT]
    assert len(ad) == 0


# ── 5. 分时破位 ───────────────────────────────────────────────────────────────


def test_intraday_break_vwap_triggered():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 16.5, vwap=16.8, now=t())
    ib = [s for s in signals if s.trigger_type is StopLossTriggerType.INTRADAY_BREAK]
    assert len(ib) == 1
    assert ib[0].severity is StopLossSeverity.WARNING


def test_intraday_break_prev_low_triggered():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 16.5, prev_low=16.8, now=t())
    ib = [s for s in signals if s.trigger_type is StopLossTriggerType.INTRADAY_BREAK]
    assert len(ib) == 1


def test_intraday_break_not_triggered():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 16.8, vwap=16.8, now=t())
    ib = [s for s in signals if s.trigger_type is StopLossTriggerType.INTRADAY_BREAK]
    assert len(ib) == 0


# ── 6. 板块退潮 ───────────────────────────────────────────────────────────────


def test_sector_ebb_triggered():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 99.0, sector_momentum=-0.03, now=t())
    se = [s for s in signals if s.trigger_type is StopLossTriggerType.SECTOR_EBB]
    assert len(se) == 1
    assert se[0].severity is StopLossSeverity.WARNING
    assert se[0].trigger_value == pytest.approx(-0.03)


def test_sector_ebb_not_triggered():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("600519", 100.0, 99.0, sector_momentum=-0.01, now=t())
    se = [s for s in signals if s.trigger_type is StopLossTriggerType.SECTOR_EBB]
    assert len(se) == 0


# ── 多模式同时触发 + 排序 ─────────────────────────────────────────────────────


def test_multiple_triggers_sorted_by_severity():
    """固定比例(CRITICAL) + 支撑破位(CRITICAL) + 逻辑失效(WARNING) + 板块退潮(WARNING)。"""
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position(
        "600519",
        100.0,
        90.0,  # 亏损 10% → 固定比例
        support_level=92.0,  # 跌破支撑
        logic_valid=False,  # 逻辑失效
        sector_momentum=-0.03,  # 板块退潮
        now=t(),
    )
    assert len(signals) == 4
    # CRITICAL 应排在 WARNING 前
    severities = [s.severity for s in signals]
    assert severities[0] is StopLossSeverity.CRITICAL
    assert severities[-1] is StopLossSeverity.WARNING


def test_no_triggers_returns_empty():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position(
        "600519",
        100.0,
        99.0,
        support_level=95.0,
        logic_valid=True,
        sector_momentum=0.01,
        now=t(),
    )
    assert signals == []


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_invalid_symbol_empty():
    engine = AshareStopLossRuleEngine()
    with pytest.raises(InvalidStopLossInputError):
        engine.check_position("", 100.0, 99.0, now=t())


def test_invalid_entry_price_zero():
    engine = AshareStopLossRuleEngine()
    with pytest.raises(InvalidStopLossInputError):
        engine.check_position("X", 0, 99.0, now=t())


def test_invalid_current_price_negative():
    engine = AshareStopLossRuleEngine()
    with pytest.raises(InvalidStopLossInputError):
        engine.check_position("X", 100.0, -5.0, now=t())


# ── 亏损限额检测 ──────────────────────────────────────────────────────────────


def test_loss_limit_no_trigger():
    engine = AshareStopLossRuleEngine()
    alert = engine.check_loss_limit(-0.01, -0.03, -0.05, now=t())
    assert alert.triggered_level is LossLimitLevel.NONE
    assert alert.forced_halt_days == 0
    assert alert.is_triggered is False
    assert alert.severity is StopLossSeverity.NONE


def test_loss_limit_daily_trigger():
    engine = AshareStopLossRuleEngine()
    alert = engine.check_loss_limit(-0.025, -0.01, -0.01, now=t())
    assert alert.triggered_level is LossLimitLevel.DAILY
    assert alert.forced_halt_days == 1
    assert alert.is_triggered is True
    assert alert.severity is StopLossSeverity.CRITICAL


def test_loss_limit_weekly_trigger():
    engine = AshareStopLossRuleEngine()
    alert = engine.check_loss_limit(-0.01, -0.06, -0.01, now=t())
    assert alert.triggered_level is LossLimitLevel.WEEKLY
    assert alert.forced_halt_days == 2
    assert alert.severity is StopLossSeverity.CRITICAL


def test_loss_limit_monthly_trigger():
    engine = AshareStopLossRuleEngine()
    alert = engine.check_loss_limit(-0.01, -0.01, -0.12, now=t())
    assert alert.triggered_level is LossLimitLevel.MONTHLY
    assert alert.forced_halt_days == 3
    assert alert.severity is StopLossSeverity.EMERGENCY


def test_loss_limit_takes_highest_level():
    """日/周/月都触发 → 取最高 (MONTHLY)。"""
    engine = AshareStopLossRuleEngine()
    alert = engine.check_loss_limit(-0.03, -0.06, -0.12, now=t())
    assert alert.triggered_level is LossLimitLevel.MONTHLY
    assert alert.forced_halt_days == 3


def test_loss_limit_profit_not_triggered():
    """盈利不算亏损。"""
    engine = AshareStopLossRuleEngine()
    alert = engine.check_loss_limit(0.05, 0.10, 0.15, now=t())
    assert alert.triggered_level is LossLimitLevel.NONE


def test_loss_limit_mixed_pnl():
    """日亏 + 周盈 + 月亏 → 取日亏触发。"""
    engine = AshareStopLossRuleEngine()
    alert = engine.check_loss_limit(-0.025, 0.05, -0.01, now=t())
    assert alert.triggered_level is LossLimitLevel.DAILY


def test_loss_limit_to_dict():
    engine = AshareStopLossRuleEngine()
    alert = engine.check_loss_limit(-0.025, -0.01, -0.01, now=t())
    d = alert.to_dict()
    assert d["triggered_level"] == "daily"
    assert d["forced_halt_days"] == 1
    assert d["severity"] == "critical"
    assert d["is_triggered"] is True


# ── 自定义配置 ────────────────────────────────────────────────────────────────


def test_custom_config_fixed_pct():
    cfg = AshareStopLossConfig(fixed_pct_threshold=0.05)  # -5%
    engine = AshareStopLossRuleEngine(cfg)
    # 亏损 6% > 5%
    signals = engine.check_position("X", 100.0, 94.0, now=t())
    fixed = [s for s in signals if s.trigger_type is StopLossTriggerType.FIXED_PCT]
    assert len(fixed) == 1
    assert fixed[0].threshold == pytest.approx(0.05)


def test_custom_config_loss_limits():
    cfg = AshareStopLossConfig(
        daily_loss_limit=0.01,
        weekly_loss_limit=0.03,
        monthly_loss_limit=0.06,
        daily_halt_days=2,
        weekly_halt_days=4,
        monthly_halt_days=6,
    )
    engine = AshareStopLossRuleEngine(cfg)
    alert = engine.check_loss_limit(-0.015, -0.01, -0.01, now=t())
    assert alert.triggered_level is LossLimitLevel.DAILY
    assert alert.forced_halt_days == 2


# ── 信号属性 ──────────────────────────────────────────────────────────────────


def test_signal_is_critical_property():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("X", 100.0, 90.0, now=t())
    fixed = [s for s in signals if s.trigger_type is StopLossTriggerType.FIXED_PCT][0]
    assert fixed.is_critical is True
    assert fixed.is_emergency is False


def test_signal_to_dict():
    engine = AshareStopLossRuleEngine()
    signals = engine.check_position("X", 100.0, 90.0, now=t())
    d = signals[0].to_dict()
    assert d["symbol"] == "X"
    assert d["trigger_type"] == "fixed_pct"
    assert d["severity"] == "critical"
    assert d["is_critical"] is True
