# [BLUEPRINT] MOD-POS-009 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""PositionLimitEnforcer 单元测试 (MOD-POS-010)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.position.core.position_limit_enforcer import (
    InvalidPositionPlanError,
    LimitCheckResult,
    LimitVerdict,
    PositionAction,
    PositionEntry,
    PositionLimitConfig,
    PositionLimitEnforcer,
    PositionPlan,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


def plan(positions: list[PositionEntry], baselines: dict[str, float] | None = None) -> PositionPlan:
    return PositionPlan(positions=positions, sector_baselines=baselines or {})


# ── 通过 ──────────────────────────────────────────────────────────────────────


def test_pass_when_all_within_limits():
    enforcer = PositionLimitEnforcer()
    p = plan([PositionEntry("A", 0.03, "银行", PositionAction.OPEN)])
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.PASS
    assert result.violations == []
    assert result.blocked is False


def test_hold_action_not_checked_for_single_cap():
    # HOLD 动作不触发单票上限 (不是新开/加仓)
    enforcer = PositionLimitEnforcer()
    p = plan([PositionEntry("A", 0.06, "银行", PositionAction.HOLD)])
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.PASS


# ── P0 Kill Switch 短路 ───────────────────────────────────────────────────────


def test_kill_switch_short_circuits_to_p0():
    enforcer = PositionLimitEnforcer()
    # 即使有其他违规, Kill Switch 激活也只返回 P0
    p = plan([PositionEntry("A", 0.20, "银行", PositionAction.OPEN)])  # 多项违规
    result = enforcer.check(p, kill_switch_active=True, now=T0)
    assert result.overall_verdict is LimitVerdict.P0_KILL_SWITCH
    assert result.kill_switch_active is True
    assert len(result.violations) == 1  # 只记 kill_switch, 短路其他
    assert result.force_reduce is True


# ── P1 总仓位 ─────────────────────────────────────────────────────────────────


def test_total_position_exceeded_p1():
    enforcer = PositionLimitEnforcer()
    p = plan(
        [
            PositionEntry("A", 0.60, "银行", PositionAction.HOLD),
            PositionEntry("B", 0.70, "科技", PositionAction.HOLD),
        ]
    )
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.P1_FORCE_REDUCE
    assert result.force_reduce is True


# ── P2 单票 ───────────────────────────────────────────────────────────────────


def test_single_instrument_exceeded_p2():
    enforcer = PositionLimitEnforcer()
    p = plan([PositionEntry("A", 0.06, "银行", PositionAction.OPEN)])  # 6% > 5%
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.P2_BLOCK_NEW
    assert result.blocked is True


def test_add_action_checked_for_single_cap():
    enforcer = PositionLimitEnforcer()
    p = plan([PositionEntry("A", 0.06, "银行", PositionAction.ADD)])
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.P2_BLOCK_NEW


# ── P2 行业 ───────────────────────────────────────────────────────────────────


def test_sector_absolute_exceeded_p2():
    enforcer = PositionLimitEnforcer()
    p = plan(
        [
            PositionEntry("A", 0.15, "银行", PositionAction.HOLD),
            PositionEntry("B", 0.16, "银行", PositionAction.HOLD),
        ]
    )  # 银行 0.31 > 0.30
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.P2_BLOCK_NEW
    assert any(v.rule == "sector_absolute_exceeded" for v in result.violations)


def test_sector_baseline_deviation_p2():
    enforcer = PositionLimitEnforcer()
    p = plan([PositionEntry("A", 0.20, "银行", PositionAction.HOLD)], baselines={"银行": 0.05})  # 偏离 0.15 > 0.10
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.P2_BLOCK_NEW
    assert any(v.rule == "sector_baseline_deviation" for v in result.violations)


# ── P3 亏损加仓 Hard Block ────────────────────────────────────────────────────


def test_loss_add_block_p3():
    enforcer = PositionLimitEnforcer()
    p = plan([PositionEntry("A", 0.03, "银行", PositionAction.ADD, existing_pnl_pct=-0.10)])
    # -10% < -8% 阈值 → Hard Block
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.P3_BLOCK_TRADE
    assert result.blocked is True


def test_loss_add_block_not_triggered_below_threshold():
    enforcer = PositionLimitEnforcer()
    p = plan([PositionEntry("A", 0.03, "银行", PositionAction.ADD, existing_pnl_pct=-0.05)])
    # -5% 不 < -8% → 不触发
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.PASS


def test_loss_add_block_only_for_add_action():
    # OPEN 动作即使有亏损也不触发 loss_add_block (那是加仓约束)
    enforcer = PositionLimitEnforcer()
    p = plan([PositionEntry("A", 0.03, "银行", PositionAction.OPEN, existing_pnl_pct=-0.20)])
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.PASS


# ── P4 压力测试 ───────────────────────────────────────────────────────────────


def test_stress_loss_warn_p4():
    enforcer = PositionLimitEnforcer()
    p = plan([PositionEntry("A", 0.03, "银行", PositionAction.HOLD)])
    result = enforcer.check(p, stress_loss=0.20, now=T0)  # 20% > 15%
    assert result.overall_verdict is LimitVerdict.P4_WARN
    assert result.blocked is False  # P4 是建议, 不强制否决


# ── 整体裁决聚合 ──────────────────────────────────────────────────────────────


def test_overall_verdict_is_worst():
    enforcer = PositionLimitEnforcer()
    p = plan(
        [
            PositionEntry("A", 0.06, "银行", PositionAction.OPEN),  # P2 单票
            PositionEntry("B", 0.70, "科技", PositionAction.HOLD),  # P1 总仓位 (0.76>1? no)
        ]
    )
    # total = 0.76 < 1.0, 单票 A 0.06>0.05 → P2
    result = enforcer.check(p, stress_loss=0.20, now=T0)  # P4
    assert result.overall_verdict is LimitVerdict.P2_BLOCK_NEW  # P2 > P4


def test_multiple_violations_aggregate():
    enforcer = PositionLimitEnforcer()
    p = plan(
        [
            PositionEntry("A", 0.06, "银行", PositionAction.OPEN, existing_pnl_pct=-0.10),
        ]
    )
    # P2 (单票) + P3 (loss add? action=OPEN 不是ADD, no P3)
    # 实际只有 P2
    result = enforcer.check(p, now=T0)
    assert result.overall_verdict is LimitVerdict.P2_BLOCK_NEW
    # 改成 ADD 触发 P3
    p2 = plan([PositionEntry("A", 0.06, "银行", PositionAction.ADD, existing_pnl_pct=-0.10)])
    result2 = enforcer.check(p2, now=T0)
    assert result2.overall_verdict is LimitVerdict.P2_BLOCK_NEW  # P2 > P3


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_weight_out_of_range_raises():
    enforcer = PositionLimitEnforcer()
    with pytest.raises(InvalidPositionPlanError):
        enforcer.check(plan([PositionEntry("A", 1.5, "银行", PositionAction.OPEN)]))


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_threshold_range():
    with pytest.raises(InvalidPositionPlanError):
        PositionLimitConfig(single_instrument_cap=1.5)


# ── 可配置 ────────────────────────────────────────────────────────────────────


def test_custom_config_relaxed_cap():
    cfg = PositionLimitConfig(single_instrument_cap=0.10)
    enforcer = PositionLimitEnforcer(config=cfg)
    # 0.06 < 自定义 0.10 → PASS (默认 0.05 下会 P2)
    result = enforcer.check(plan([PositionEntry("A", 0.06, "银行", PositionAction.OPEN)]), now=T0)
    assert result.overall_verdict is LimitVerdict.PASS
