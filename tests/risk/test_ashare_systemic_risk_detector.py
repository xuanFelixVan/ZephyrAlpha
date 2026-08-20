# [BLUEPRINT] MOD-RK-10 | docs/03_modules/_domain_risk/ashare_systemic_risk_detector/blueprint.md | §
# [TTL] permanent
"""AshareSystemicRiskDetector 单元测试 (MOD-RK-10)。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from zephyr.risk.core.ashare_systemic_risk_detector import (
    AshareSystemicRiskConfig,
    AshareSystemicRiskDetector,
    InvalidSystemicRiskInputError,
    SystemicRiskAlert,
    SystemicRiskAlertLevel,
    SystemicRiskSignal,
    SystemicRiskSignalType,
)

T0 = datetime(2026, 8, 4, 14, 30, tzinfo=timezone.utc)


def t(offset_seconds: float = 0.0) -> datetime:
    return T0 + timedelta(seconds=offset_seconds)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_defaults():
    cfg = AshareSystemicRiskConfig()
    assert cfg.margin_balance_drop_threshold == pytest.approx(-0.03)
    assert cfg.limit_down_count_threshold == 50
    assert cfg.index_drop_threshold == pytest.approx(-0.02)
    assert cfg.volume_surge_ratio_threshold == pytest.approx(2.0)
    assert cfg.sentiment_breaker_threshold == pytest.approx(0.85)
    assert cfg.level_2_position_cap == pytest.approx(0.70)
    assert cfg.level_3_position_cap == pytest.approx(0.0)


def test_config_invalid_margin_threshold_positive():
    with pytest.raises(InvalidSystemicRiskInputError):
        AshareSystemicRiskConfig(margin_balance_drop_threshold=0.01)


def test_config_invalid_volume_surge_below_one():
    with pytest.raises(InvalidSystemicRiskInputError):
        AshareSystemicRiskConfig(volume_surge_ratio_threshold=0.5)


def test_config_invalid_level_caps():
    with pytest.raises(InvalidSystemicRiskInputError):
        AshareSystemicRiskConfig(
            level_2_position_cap=0.3,
            level_3_position_cap=0.5,  # > level_2
        )


def test_config_invalid_sentiment_range():
    with pytest.raises(InvalidSystemicRiskInputError):
        AshareSystemicRiskConfig(sentiment_breaker_threshold=1.5)


# ── 无信号 ────────────────────────────────────────────────────────────────────


def test_no_signals_returns_none():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(now=t())
    assert alert.alert_level is SystemicRiskAlertLevel.NONE
    assert alert.signal_count == 0
    assert alert.is_triggered is False
    assert alert.is_emergency is False
    assert alert.kill_switch_required is False
    assert alert.position_cap == pytest.approx(1.0)


# ── 1. 融资盘平仓潮 ───────────────────────────────────────────────────────────


def test_margin_call_cascade_triggered():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        margin_balance_change=-0.05,  # < -3%
        limit_down_count=80,  # > 50
        now=t(),
    )
    assert alert.signal_count == 1
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_1
    assert any(s.signal_type is SystemicRiskSignalType.MARGIN_CALL_CASCADE for s in alert.triggered_signals)


def test_margin_call_cascade_not_triggered_partial():
    """只有融资余额降, 跌停股数不足 → 不触发。"""
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        margin_balance_change=-0.05,
        limit_down_count=10,  # < 50
        now=t(),
    )
    assert alert.signal_count == 0


def test_margin_call_cascade_invalid_limit_down():
    detector = AshareSystemicRiskDetector()
    with pytest.raises(InvalidSystemicRiskInputError):
        detector.check(margin_balance_change=-0.05, limit_down_count=-1, now=t())


# ── 2. 量化踩踏 ──────────────────────────────────────────────────────────────


def test_quant_stampede_triggered():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        index_change_pct=-0.03,  # < -2%
        volume_surge_ratio=2.5,  # > 2.0
        now=t(),
    )
    assert alert.signal_count == 1
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_1
    assert any(s.signal_type is SystemicRiskSignalType.QUANT_STAMPEDE for s in alert.triggered_signals)


def test_quant_stampede_not_triggered_partial():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        index_change_pct=-0.03,
        volume_surge_ratio=1.5,  # < 2.0
        now=t(),
    )
    assert alert.signal_count == 0


def test_quant_stampede_invalid_volume():
    detector = AshareSystemicRiskDetector()
    with pytest.raises(InvalidSystemicRiskInputError):
        detector.check(index_change_pct=-0.03, volume_surge_ratio=-1.0, now=t())


# ── 3. 流动性危机 ────────────────────────────────────────────────────────────


def test_liquidity_crisis_triggered():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        sell_pressure=0.75,  # > 0.65
        bid_ask_spread=0.008,  # > 0.005
        now=t(),
    )
    assert alert.signal_count == 1
    assert any(s.signal_type is SystemicRiskSignalType.LIQUIDITY_CRISIS for s in alert.triggered_signals)


def test_liquidity_crisis_not_triggered_partial():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        sell_pressure=0.75,
        bid_ask_spread=0.002,  # < 0.005
        now=t(),
    )
    assert alert.signal_count == 0


def test_liquidity_crisis_invalid_sell_pressure():
    detector = AshareSystemicRiskDetector()
    with pytest.raises(InvalidSystemicRiskInputError):
        detector.check(sell_pressure=1.5, bid_ask_spread=0.01, now=t())


# ── 4. 政策转向 ──────────────────────────────────────────────────────────────


def test_policy_shift_triggered():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(policy_shift_flag=True, now=t())
    assert alert.signal_count == 1
    assert any(s.signal_type is SystemicRiskSignalType.POLICY_SHIFT for s in alert.triggered_signals)


def test_policy_shift_skipped_when_false():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(policy_shift_flag=False, now=t())
    assert alert.signal_count == 0


# ── 5. 外围冲击 ──────────────────────────────────────────────────────────────


def test_external_shock_triggered():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(external_market_change=-0.04, now=t())
    assert alert.signal_count == 1
    assert any(s.signal_type is SystemicRiskSignalType.EXTERNAL_SHOCK for s in alert.triggered_signals)


def test_external_shock_not_triggered():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(external_market_change=-0.01, now=t())
    assert alert.signal_count == 0


# ── 三级警报 ──────────────────────────────────────────────────────────────────


def test_level_1_one_signal():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(policy_shift_flag=True, now=t())
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_1
    assert "停止新开仓" in alert.action
    assert alert.kill_switch_required is False


def test_level_2_two_signals():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        policy_shift_flag=True,
        external_market_change=-0.04,
        now=t(),
    )
    assert alert.signal_count == 2
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_2
    assert alert.position_cap == pytest.approx(0.70)
    assert alert.kill_switch_required is False


def test_level_3_three_signals():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        margin_balance_change=-0.05,
        limit_down_count=80,
        index_change_pct=-0.03,
        volume_surge_ratio=2.5,
        policy_shift_flag=True,
        now=t(),
    )
    assert alert.signal_count == 3
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_3
    assert alert.position_cap == pytest.approx(0.0)
    assert alert.kill_switch_required is True
    assert alert.is_emergency is True


def test_level_3_five_signals():
    """5 信号全触发 → LEVEL_3。"""
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        margin_balance_change=-0.05,
        limit_down_count=80,
        index_change_pct=-0.03,
        volume_surge_ratio=2.5,
        sell_pressure=0.75,
        bid_ask_spread=0.008,
        policy_shift_flag=True,
        external_market_change=-0.04,
        now=t(),
    )
    assert alert.signal_count == 5
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_3


# ── 情绪断路器 ────────────────────────────────────────────────────────────────


def test_sentiment_breaker_forces_level_3():
    """1 信号 + 情绪断路器 → 强制升级 LEVEL_3。"""
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        policy_shift_flag=True,
        sentiment_index=0.90,  # > 0.85
        now=t(),
    )
    assert alert.signal_count == 1
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_3
    assert alert.sentiment_breaker_triggered is True
    assert alert.kill_switch_required is True


def test_sentiment_breaker_below_threshold_no_upgrade():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        policy_shift_flag=True,
        sentiment_index=0.50,  # < 0.85
        now=t(),
    )
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_1
    assert alert.sentiment_breaker_triggered is False


def test_sentiment_breaker_already_level_3():
    """已 LEVEL_3 + 情绪断路器 → 保持 LEVEL_3 (不重复升级)。"""
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        policy_shift_flag=True,
        external_market_change=-0.04,
        margin_balance_change=-0.05,
        limit_down_count=80,
        index_change_pct=-0.03,
        volume_surge_ratio=2.5,
        sentiment_index=0.90,
        now=t(),
    )
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_3
    # signal_count=4 (margin+quant+policy+external), sentiment 不增加 signal_count
    assert alert.signal_count == 4


# ── 逃生执行器 ────────────────────────────────────────────────────────────────


def test_escape_directive_level_3():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        policy_shift_flag=True,
        external_market_change=-0.04,
        margin_balance_change=-0.05,
        limit_down_count=80,
        index_change_pct=-0.03,
        volume_surge_ratio=2.5,
        now=t(),
    )
    directive = detector.build_escape_directive(alert)
    assert directive["directive"] == "escape"
    assert directive["action"] == "liquidate_all"
    assert directive["position_cap"] == 0.0
    assert directive["cancel_pending_orders"] is True
    assert directive["halt_new_orders"] is True
    assert directive["kill_switch_required"] is True


def test_escape_directive_rejects_non_level_3():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(policy_shift_flag=True, now=t())  # LEVEL_1
    with pytest.raises(InvalidSystemicRiskInputError):
        detector.build_escape_directive(alert)


# ── to_dict ──────────────────────────────────────────────────────────────────


def test_alert_to_dict():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(
        policy_shift_flag=True,
        external_market_change=-0.04,
        now=t(),
    )
    d = alert.to_dict()
    assert d["alert_level"] == "level_2"
    assert d["signal_count"] == 2
    assert d["is_triggered"] is True
    assert d["is_emergency"] is False
    assert len(d["triggered_signals"]) == 2


def test_signal_to_dict():
    detector = AshareSystemicRiskDetector()
    alert = detector.check(policy_shift_flag=True, now=t())
    sig = alert.triggered_signals[0]
    d = sig.to_dict()
    assert d["signal_type"] == "policy_shift"
    assert "reason" in d


# ── 自定义配置 ────────────────────────────────────────────────────────────────


def test_custom_config_thresholds():
    cfg = AshareSystemicRiskConfig(
        margin_balance_drop_threshold=-0.02,
        limit_down_count_threshold=30,
    )
    detector = AshareSystemicRiskDetector(cfg)
    # 用默认配置不触发, 用自定义配置触发
    alert = detector.check(
        margin_balance_change=-0.025,  # < -0.02 (自定义)
        limit_down_count=35,  # > 30 (自定义)
        now=t(),
    )
    assert alert.signal_count == 1
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_1


def test_custom_position_caps():
    cfg = AshareSystemicRiskConfig(
        level_2_position_cap=0.50,
        level_3_position_cap=0.0,
    )
    detector = AshareSystemicRiskDetector(cfg)
    alert = detector.check(
        policy_shift_flag=True,
        external_market_change=-0.04,
        now=t(),
    )
    assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_2
    assert alert.position_cap == pytest.approx(0.50)


# ── 部分输入跳过 ──────────────────────────────────────────────────────────────


def test_partial_inputs_skip_signals():
    """只提供 margin_balance_change, 不提供 limit_down_count → 融资盘信号跳过。"""
    detector = AshareSystemicRiskDetector()
    alert = detector.check(margin_balance_change=-0.05, now=t())
    assert alert.signal_count == 0
    assert alert.alert_level is SystemicRiskAlertLevel.NONE


def test_index_change_alone_no_quant_stampede():
    """只提供 index_change_pct, 不提供 volume_surge_ratio → 量化踩踏跳过。"""
    detector = AshareSystemicRiskDetector()
    alert = detector.check(index_change_pct=-0.05, now=t())
    assert alert.signal_count == 0
