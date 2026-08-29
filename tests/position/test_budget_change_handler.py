# [BLUEPRINT] MOD-POS-009 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.position.test_budget_change_handler
# [DOMAIN] D_POSITION
# [MATURITY] production
# [TTL] permanent

"""
BudgetChangeHandler (MOD-POS-022) 单元测试

按 33_budget_change_handler §3 + blueprint §7 Phase 1 测试规划施工。
覆盖：触发判定五规则 / 防抖双层 / 三级指令内容 / 差异化窗口 / 收敛三条件 /
Tier3 强裁边界 / re-target 豁免 / 状态机留痕 / 多策略隔离 / #4 修复验证。
纯内存状态机，无 IO 依赖（33 号 §3.1 指令型设计）。
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from zephyr.position.core.budget_change_handler import (
    BudgetChangeError,
    BudgetChangeHandler,
    BudgetHandlerEvent,
    ForcedTrim,
    FreezeNewPositions,
    RebalanceRequest,
    StateRecoveryError,
    TierLevel,
    TierState,
)

D1 = "2026-08-13"
D2 = "2026-08-14"


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def handler() -> BudgetChangeHandler:
    return BudgetChangeHandler()


@pytest.fixture
def triggered_handler(handler: BudgetChangeHandler) -> BudgetChangeHandler:
    """已触发三级升级（打板，0.30→0.20，窗口 2 天）的 handler。"""
    handler.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板", current_date=D1)
    return handler


# ── 触发判定（blueprint §7：上调不处理 / 下调启动三级 / delta=0 边界）─────────


def test_upgrade_no_action(handler: BudgetChangeHandler) -> None:
    """budget 上调 → NO_ACTION 不防抖（33 号 §3.3 对称性豁免）。"""
    result = handler.handle_budget_change("s1", 0.30, 0.35, current_date=D1)
    assert result.action.startswith("NO_ACTION")
    assert result.instructions == []
    assert result.state.current_tier == TierLevel.IDLE


def test_upgrade_updates_target_budget(handler: BudgetChangeHandler) -> None:
    """非收敛中上调：target_budget 即时更新（自然部署）。"""
    result = handler.handle_budget_change("s1", 0.30, 0.35, current_date=D1)
    assert result.state.target_budget == pytest.approx(0.35)


def test_delta_zero_no_action(handler: BudgetChangeHandler) -> None:
    """delta=0 边界：new == old 按上调处理，不触发。"""
    result = handler.handle_budget_change("s1", 0.30, 0.30, current_date=D1)
    assert result.action.startswith("NO_ACTION")
    assert result.state.current_tier == TierLevel.IDLE


def test_downgrade_over_threshold_triggers(handler: BudgetChangeHandler) -> None:
    """首次下调 ≥5% → 触发三级升级（规则 4）。"""
    result = handler.handle_budget_change("s1", 0.30, 0.28, current_date=D1)  # 6.7%
    assert "TIER1+TIER2" in result.action
    assert result.state.current_tier == TierLevel.TIER_2_REBALANCE


# ── 防抖双层（33 号 §3.3）─────────────────────────────────────────────────────


def test_debounce_small_downgrade_ignored(handler: BudgetChangeHandler) -> None:
    """首次下调 <5% 且累计 <10% → DEBOUNCE 忽略（规则 3）。"""
    result = handler.handle_budget_change("s1", 1.00, 0.97, current_date=D1)  # 3%
    assert result.action.startswith("DEBOUNCE")
    assert result.instructions == []
    assert result.state.current_tier == TierLevel.IDLE


def test_cumulative_trend_forces_trigger(handler: BudgetChangeHandler) -> None:
    """日间累计连降 >10% 强制触发（规则 5，防抖不过度）。"""
    handler.handle_budget_change("s1", 1.00, 0.96, current_date=D1)  # 4%，累计 4%
    handler.handle_budget_change("s1", 0.96, 0.92, current_date=D1)  # 4.17%，累计 8.2%
    result = handler.handle_budget_change("s1", 0.92, 0.89, current_date=D1)  # 3.3%，累计 11.5%
    assert "累计趋势" in result.action
    assert result.state.current_tier == TierLevel.TIER_2_REBALANCE


def test_debounce_cumulative_resets_daily(handler: BudgetChangeHandler) -> None:
    """新交易日重置日内累计（last_budget_change_date 切换）。"""
    handler.handle_budget_change("s1", 1.00, 0.96, current_date=D1)  # 累计 4%
    result = handler.handle_budget_change("s1", 0.96, 0.93, current_date=D2)  # 新日重置后 3.125%
    assert result.action.startswith("DEBOUNCE")
    assert result.state.cumulative_budget_change == pytest.approx(0.03125, abs=1e-6)


# ── Tier 1 / Tier 2 指令内容（33 号 §3.2/§3.6）────────────────────────────────


def test_tier1_tier2_issued_together(triggered_handler: BudgetChangeHandler) -> None:
    """Tier1 与 Tier2 同调用内连发；状态机止于 TIER_2_REBALANCE（Tier1 瞬时）。"""
    result = triggered_handler.handle_budget_change("s2", 0.30, 0.20, current_date=D1)
    assert [i["tier"] for i in result.instructions] == [1, 2]
    assert result.state.tier1_at is not None
    assert result.state.tier2_at is not None
    assert result.state.current_tier == TierLevel.TIER_2_REBALANCE


def test_tier1_freeze_instruction(triggered_handler: BudgetChangeHandler) -> None:
    """FreezeNewPositions：撤买单留卖单不对称设计（33 号 §3.2）。"""
    state = triggered_handler.get_state("s1")
    assert state is not None
    result = triggered_handler.handle_budget_change("s3", 0.30, 0.20, current_date=D1)
    instr = result.instructions[0]["instruction"]
    assert isinstance(instr, FreezeNewPositions)
    assert instr.cancel_pending_buy_orders is True
    assert instr.keep_pending_sell_orders is True
    assert instr.schema_version == "1.0"


def test_tier2_rebalance_instruction_contract(triggered_handler: BudgetChangeHandler) -> None:
    """RebalanceRequest 携带 new_budget + window + 接口契约（策略不能说"我不卖"）。"""
    state = triggered_handler.get_state("s1")
    assert state is not None
    result = triggered_handler.handle_budget_change("s4", 0.30, 0.20, strategy_type="多因子", current_date=D1)
    instr = result.instructions[1]["instruction"]
    assert isinstance(instr, RebalanceRequest)
    assert instr.new_budget == pytest.approx(0.20)
    assert instr.convergence_window == timedelta(days=4)
    assert "rebalance_to_budget" in instr.interface_contract


# ── convergence_window 差异化（33 号 §3.4）────────────────────────────────────


@pytest.mark.parametrize(
    ("strategy_type", "days"),
    [("打板", 2), ("多因子", 4), ("事件驱动", 3), ("未知类型", 3)],
)
def test_convergence_window_differentiated(handler: BudgetChangeHandler, strategy_type: str, days: int) -> None:
    """打板 2 天 / 多因子 4 天 / 事件驱动 3 天 / 未知缺省 3 天。"""
    result = handler.handle_budget_change("s1", 0.30, 0.20, strategy_type=strategy_type, current_date=D1)
    instr = result.instructions[1]["instruction"]
    assert isinstance(instr, RebalanceRequest)
    assert instr.convergence_window == timedelta(days=days)


def test_window_end_recorded(triggered_handler: BudgetChangeHandler) -> None:
    """convergence_window_end = tier2_at + window（打板 2 天）。"""
    state = triggered_handler.get_state("s1")
    assert state is not None
    assert state.convergence_window_end is not None
    delta = state.convergence_window_end - state.tier2_at
    assert delta == timedelta(days=2)


# ── 收敛三条件（33 号 §3.5）───────────────────────────────────────────────────


def test_convergence_success(triggered_handler: BudgetChangeHandler) -> None:
    """仓位差 <5% 且持续 ≥1 日 → CONVERGED（eps_days=1 一次达标）。"""
    result = triggered_handler.check_convergence("s1", current_exposure=0.205)
    assert result.action.startswith("CONVERGED")
    assert result.state.current_tier == TierLevel.CONVERGED
    assert result.state.converged_at is not None


def test_convergence_waiting_persistence() -> None:
    """eps_days=2：首次贴近仅计数，持续性未达标 → WAITING。"""
    handler = BudgetChangeHandler(eps_days=2)
    handler.handle_budget_change("s1", 0.30, 0.20, current_date=D1)
    first = handler.check_convergence("s1", current_exposure=0.205)
    assert first.action.startswith("WAITING")
    assert "1/2" in first.action
    second = handler.check_convergence("s1", current_exposure=0.205)
    assert second.action.startswith("CONVERGED")


def test_convergence_resets_on_deviation() -> None:
    """仓位偏离 → 持续性计数清零重计（防单日假收敛后漂移）。"""
    handler = BudgetChangeHandler(eps_days=2)
    handler.handle_budget_change("s1", 0.30, 0.20, current_date=D1)
    handler.check_convergence("s1", current_exposure=0.205)  # 贴近，计数 1
    handler.check_convergence("s1", current_exposure=0.28)  # 偏离，清零
    result = handler.check_convergence("s1", current_exposure=0.205)  # 再贴近，计数 1
    assert result.action.startswith("WAITING")
    assert result.state.convergence_days_satisfied == 1


def test_convergence_target_zero_boundary() -> None:
    """target=0 边界：仅 exposure≈0 算收敛。"""
    handler = BudgetChangeHandler()
    handler.handle_budget_change("s1", 0.30, 0.0, current_date=D1)  # 下调 100%
    not_converged = handler.check_convergence("s1", current_exposure=0.05)
    assert not_converged.action.startswith("WAITING")
    converged = handler.check_convergence("s1", current_exposure=0.0)
    assert converged.action.startswith("CONVERGED")


# ── Tier 3 强裁（33 号 §3.2/§3.5 边界 fail-safe）──────────────────────────────


def test_tier3_on_timeout(triggered_handler: BudgetChangeHandler) -> None:
    """窗口超时未收敛 → 升级 Tier3 发 ForcedTrim。"""
    overdue = datetime.now() + timedelta(days=3)
    result = triggered_handler.check_convergence("s1", current_exposure=0.28, now=overdue)
    assert "TIER3" in result.action
    assert result.state.current_tier == TierLevel.TIER_3_FORCE_TRIM
    assert result.instructions[0]["tier"] == 3
    assert isinstance(result.instructions[0]["instruction"], ForcedTrim)


def test_tier3_trim_ratio_calculation(triggered_handler: BudgetChangeHandler) -> None:
    """trim_ratio = (exposure − target) / exposure（等比缩放不挑仓位）。"""
    overdue = datetime.now() + timedelta(days=3)
    result = triggered_handler.check_convergence("s1", current_exposure=0.28, now=overdue)
    instr = result.instructions[0]["instruction"]
    assert isinstance(instr, ForcedTrim)
    assert instr.trim_ratio == pytest.approx((0.28 - 0.20) / 0.28)
    assert "超时" in instr.reason


def test_tier3_zero_exposure_converged(triggered_handler: BudgetChangeHandler) -> None:
    """超时但 exposure=0 → 无需裁剪直接 CONVERGED（fail-safe）。"""
    overdue = datetime.now() + timedelta(days=3)
    result = triggered_handler.check_convergence("s1", current_exposure=0.0, now=overdue)
    assert result.action.startswith("CONVERGED")
    assert result.instructions == []


def test_tier3_already_converged_no_trim(triggered_handler: BudgetChangeHandler) -> None:
    """窗口结束时实际已 ≤target → 认定收敛不强裁（fail-safe）。"""
    overdue = datetime.now() + timedelta(days=3)
    # 0.19 ≤ target 0.20，但 |0.19-0.20|/0.20=5% 不满足 <5% 收敛条件 → 走超时路径
    result = triggered_handler.check_convergence("s1", current_exposure=0.19, now=overdue)
    assert result.action.startswith("CONVERGED")
    assert result.instructions == []


def test_waiting_within_window(triggered_handler: BudgetChangeHandler) -> None:
    """窗口内未收敛 → WAITING 继续等待（不升级）。"""
    result = triggered_handler.check_convergence("s1", current_exposure=0.28)
    assert result.action.startswith("WAITING")
    assert result.state.current_tier == TierLevel.TIER_2_REBALANCE


# ── re-target 防抖豁免（33 号 §3.3，含 #4 修复验证）───────────────────────────


def test_retarget_upgrade_in_tier2(triggered_handler: BudgetChangeHandler) -> None:
    """Tier2 收敛中上调 → 更新 target 重置收敛计数（不防抖）。"""
    result = triggered_handler.handle_budget_change("s1", 0.20, 0.25, current_date=D2)
    assert result.action.startswith("RETARGET")
    assert result.state.target_budget == pytest.approx(0.25)
    assert result.state.convergence_days_satisfied == 0
    assert result.state.current_tier == TierLevel.TIER_2_REBALANCE


def test_retarget_upgrade_stops_tier3(triggered_handler: BudgetChangeHandler) -> None:
    """Tier3 强裁中上调 → 停止强裁直接 CONVERGED。"""
    overdue = datetime.now() + timedelta(days=3)
    triggered_handler.check_convergence("s1", current_exposure=0.28, now=overdue)
    result = triggered_handler.handle_budget_change("s1", 0.20, 0.30, current_date=D2)
    assert "停止 Tier 3 强裁" in result.action
    assert result.state.current_tier == TierLevel.CONVERGED


def test_retarget_downgrade_uses_strategy_type() -> None:
    """#4 修复验证：收敛中下调按策略自身类型重置窗口（打板 2 天，非硬编码多因子 4 天）。"""
    handler = BudgetChangeHandler()
    handler.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板", current_date=D1)
    before = datetime.now()
    result = handler.handle_budget_change("s1", 0.20, 0.15, strategy_type="打板", current_date=D2)
    assert result.action.startswith("RETARGET")
    assert result.state.target_budget == pytest.approx(0.15)
    window = result.state.convergence_window_end - before
    assert window < timedelta(days=3)  # 打板 2 天 + 执行耗时 << 多因子 4 天
    assert window >= timedelta(days=2)


# ── 状态机 / 留痕 / 隔离（33 号 §3.1 指令即审计）───────────────────────────────


def test_instructions_issued_trail(triggered_handler: BudgetChangeHandler) -> None:
    """instructions_issued 逐条留痕 tier1→tier2→tier3（每级独立可复盘）。"""
    overdue = datetime.now() + timedelta(days=3)
    triggered_handler.check_convergence("s1", current_exposure=0.28, now=overdue)
    state = triggered_handler.get_state("s1")
    assert state is not None
    tiers = [rec["tier"] for rec in state.instructions_issued]
    assert tiers == [1, 2, 3]
    assert all("at" in rec and "reason" in rec for rec in state.instructions_issued)


def test_multi_strategy_isolation(handler: BudgetChangeHandler) -> None:
    """多策略并发：状态相互隔离，窗口各自独立。"""
    handler.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板", current_date=D1)
    handler.handle_budget_change("s2", 0.40, 0.30, strategy_type="多因子", current_date=D1)
    s1 = handler.get_state("s1")
    s2 = handler.get_state("s2")
    assert s1 is not None and s2 is not None
    assert s1.target_budget == pytest.approx(0.20)
    assert s2.target_budget == pytest.approx(0.30)
    assert s1.convergence_window_end != s2.convergence_window_end


def test_get_state_unknown_returns_none(handler: BudgetChangeHandler) -> None:
    """get_state 未知策略返回 None。"""
    assert handler.get_state("nonexistent") is None


def test_check_convergence_no_active_state(handler: BudgetChangeHandler) -> None:
    """无活跃状态 → NO_ACTION（进程内缓存语义：state 缺失=从未有 budget 变动）。"""
    result = handler.check_convergence("nonexistent", current_exposure=0.20)
    assert result.action.startswith("NO_ACTION")
    assert result.instructions == []


def test_check_convergence_wrong_tier(triggered_handler: BudgetChangeHandler) -> None:
    """非 Tier2 阶段（如 Tier3 强裁中）→ NO_ACTION 不重复检查。"""
    overdue = datetime.now() + timedelta(days=3)
    triggered_handler.check_convergence("s1", current_exposure=0.28, now=overdue)  # → Tier3
    result = triggered_handler.check_convergence("s1", current_exposure=0.28, now=overdue)
    assert result.action.startswith("NO_ACTION")
    assert "非 Tier 2" in result.action


def test_tier_state_dataclass_defaults() -> None:
    """TierState 默认 IDLE，strategy_type 缺省"多因子"（#4 修复新增字段）。"""
    state = TierState(strategy_id="s1")
    assert state.current_tier == TierLevel.IDLE
    assert state.strategy_type == "多因子"
    assert state.is_in_convergence() is False


# ── G15→G14 接线就绪入口适配（33号 §7 新发现3：BudgetChanged 事件链）─────────


class TestOnBudgetAllocation:
    """on_budget_allocation：BudgetAllocation.effective_budgets → handle_budget_change 适配器。"""

    def test_downsize_triggers_escalation(self, handler: BudgetChangeHandler) -> None:
        """新 budget 下调 ≥5% → 触发 Tier1+Tier2 指令。"""
        results = handler.on_budget_allocation(
            effective_budgets={"s1": 0.20},
            previous_budgets={"s1": 0.30},
            strategy_types={"s1": "打板"},
            current_date=D1,
        )
        assert "s1" in results
        tiers = [i["tier"] for i in results["s1"].instructions]
        assert tiers == [1, 2]

    def test_upsize_no_action(self, handler: BudgetChangeHandler) -> None:
        """上调 → NO_ACTION（自然部署，不防抖）。"""
        results = handler.on_budget_allocation(
            effective_budgets={"s1": 0.35},
            previous_budgets={"s1": 0.30},
            current_date=D1,
        )
        assert results["s1"].action.startswith("NO_ACTION")

    def test_new_strategy_first_allocation_skipped(self, handler: BudgetChangeHandler) -> None:
        """previous 缺失的策略=新策略首配 → 跳过（非 budget 变动，冷启动承载渐进暴露）。"""
        results = handler.on_budget_allocation(
            effective_budgets={"s_new": 0.10},
            previous_budgets={"s1": 0.30},
            current_date=D1,
        )
        assert results == {}
        assert handler.get_state("s_new") is None

    def test_missing_in_new_not_auto_zeroed(self, handler: BudgetChangeHandler) -> None:
        """new 中缺失的策略不自动按 budget→0 强裁（防数据缺口误触 Tier3）。"""
        results = handler.on_budget_allocation(
            effective_budgets={},
            previous_budgets={"s1": 0.30},
            current_date=D1,
        )
        assert results == {}
        assert handler.get_state("s1") is None

    def test_multi_strategy_mixed(self, handler: BudgetChangeHandler) -> None:
        """多策略混合：各策略独立 diff 裁决。"""
        results = handler.on_budget_allocation(
            effective_budgets={"s1": 0.20, "s2": 0.40, "s3": 0.28},
            previous_budgets={"s1": 0.30, "s2": 0.35, "s3": 0.28},
            strategy_types={"s1": "打板", "s2": "多因子"},
            current_date=D1,
        )
        assert [i["tier"] for i in results["s1"].instructions] == [1, 2]  # 下调 33% → 触发
        assert results["s2"].action.startswith("NO_ACTION")  # 上调
        assert results["s3"].action.startswith("NO_ACTION")  # 不变


# ── on_firm_violation firm 违例直触 Tier3（30号 §2.4 + 33号 §7-③）─────────────


class TestOnFirmViolation:
    """firm 违例直触 Tier3 入口：不等 Tier2 窗口，立即 ForcedTrim。"""

    def test_direct_tier3_forced_trim(self, handler: BudgetChangeHandler) -> None:
        """无活跃状态 + 显式 target → 直触 Tier3，trim_ratio 正确。"""
        result = handler.on_firm_violation("s1", current_exposure=0.40, target_budget=0.20, violation="单票超限未纠正")
        assert result.state.current_tier == TierLevel.TIER_3_FORCE_TRIM
        assert len(result.instructions) == 1
        instr = result.instructions[0]
        assert instr["tier"] == 3
        assert isinstance(instr["instruction"], ForcedTrim)
        assert instr["instruction"].trim_ratio == pytest.approx(0.5)  # (0.40-0.20)/0.40
        assert "firm 风险违例" in instr["reason"]
        assert "单票超限未纠正" in instr["reason"]

    def test_inherits_target_from_active_state(self, triggered_handler: BudgetChangeHandler) -> None:
        """target_budget=None → 继承活跃状态的 target（Tier2 收敛中违例直触升级）。"""
        result = triggered_handler.on_firm_violation("s1", current_exposure=0.28)
        assert result.state.current_tier == TierLevel.TIER_3_FORCE_TRIM
        instr = result.instructions[0]["instruction"]
        # target=0.20（继承触发时状态）：trim=(0.28-0.20)/0.28
        assert instr.trim_ratio == pytest.approx((0.28 - 0.20) / 0.28)

    def test_no_target_no_state_raises(self, handler: BudgetChangeHandler) -> None:
        """无 target 且无活跃状态 → ValueError（Fail-Closed 不猜目标）。"""
        with pytest.raises(ValueError, match="target_budget"):
            handler.on_firm_violation("s1", current_exposure=0.40)

    def test_exposure_below_target_converged(self, handler: BudgetChangeHandler) -> None:
        """exposure ≤ target → CONVERGED 无需强裁（边界）。"""
        result = handler.on_firm_violation("s1", current_exposure=0.18, target_budget=0.20)
        assert result.state.current_tier == TierLevel.CONVERGED
        assert result.instructions == []

    def test_zero_exposure_converged(self, handler: BudgetChangeHandler) -> None:
        """exposure=0 → CONVERGED（退化）。"""
        result = handler.on_firm_violation("s1", current_exposure=0.0, target_budget=0.20)
        assert result.state.current_tier == TierLevel.CONVERGED

    def test_violation_instruction_logged(self, handler: BudgetChangeHandler) -> None:
        """Tier3 直触指令入 instructions_issued 留痕（§2.4 每级独立事件可复盘）。"""
        handler.on_firm_violation("s1", current_exposure=0.40, target_budget=0.20)
        state = handler.get_state("s1")
        assert state is not None
        tiers = [rec["tier"] for rec in state.instructions_issued]
        assert tiers == [3]  # 直触：无 Tier1/2 记录


# ── A13：E-POS-40/41 事件发射（进程内回调分发）─────────────────────────────


class TestEventEmission:
    """E-POS-40 BudgetChangeHandled / E-POS-41 TierEscalation 事件发射。"""

    def test_handled_event_on_trigger(self, handler: BudgetChangeHandler) -> None:
        """触发三级升级 → BudgetChangeHandled（E-POS-40）携带动作与指令级别。"""
        events: list[BudgetHandlerEvent] = []
        handler.subscribe(events.append)
        handler.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板", current_date=D1)
        handled = [e for e in events if e.event_id == "E-POS-40"]
        assert len(handled) == 1
        assert handled[0].name == "BudgetChangeHandled"
        assert handled[0].strategy_id == "s1"
        assert handled[0].payload["instruction_tiers"] == [1, 2]
        assert handled[0].payload["current_tier"] == "tier_2_rebalance"

    def test_handled_event_on_no_action(self, handler: BudgetChangeHandler) -> None:
        """上调 NO_ACTION 也发 BudgetChangeHandled（变动处理完成，归因用）。"""
        events: list[BudgetHandlerEvent] = []
        handler.subscribe(events.append)
        handler.handle_budget_change("s1", 0.30, 0.35, current_date=D1)
        handled = [e for e in events if e.event_id == "E-POS-40"]
        assert len(handled) == 1
        assert handled[0].payload["action"].startswith("NO_ACTION")
        assert handled[0].payload["instruction_tiers"] == []

    def test_tier_escalation_events_on_trigger(self, handler: BudgetChangeHandler) -> None:
        """触发 → TierEscalation（E-POS-41）两连发：IDLE→T1、T1→T2。"""
        events: list[BudgetHandlerEvent] = []
        handler.subscribe(events.append)
        handler.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板", current_date=D1)
        esc = [e for e in events if e.event_id == "E-POS-41"]
        assert [(e.payload["from_tier"], e.payload["to_tier"]) for e in esc] == [
            ("idle", "tier_1_lock"),
            ("tier_1_lock", "tier_2_rebalance"),
        ]

    def test_tier_escalation_event_on_tier3_timeout(self, triggered_handler: BudgetChangeHandler) -> None:
        """窗口超时升 Tier3 → TierEscalation 记录 T2→T3 流转。"""
        events: list[BudgetHandlerEvent] = []
        triggered_handler.subscribe(events.append)
        now = datetime.now() + timedelta(days=3)
        triggered_handler.check_convergence("s1", current_exposure=0.28, now=now)
        esc = [e for e in events if e.event_id == "E-POS-41"]
        assert len(esc) == 1
        assert esc[0].payload["from_tier"] == "tier_2_rebalance"
        assert esc[0].payload["to_tier"] == "tier_3_force_trim"

    def test_tier_escalation_event_on_firm_violation(self, handler: BudgetChangeHandler) -> None:
        """firm 违例直触 Tier3 → TierEscalation 留痕。"""
        events: list[BudgetHandlerEvent] = []
        handler.subscribe(events.append)
        handler.on_firm_violation("s1", current_exposure=0.40, target_budget=0.20)
        esc = [e for e in events if e.event_id == "E-POS-41"]
        assert len(esc) == 1
        assert esc[0].payload["to_tier"] == "tier_3_force_trim"
        assert "firm 风险违例" in esc[0].payload["reason"]

    def test_subscriber_exception_isolated(self, triggered_handler: BudgetChangeHandler) -> None:
        """订阅者抛异常不阻断状态机（仅 log），后续订阅者仍收到事件。"""

        def bad_callback(_event: BudgetHandlerEvent) -> None:
            raise RuntimeError("boom")

        events: list[BudgetHandlerEvent] = []
        triggered_handler.subscribe(bad_callback)
        triggered_handler.subscribe(events.append)
        now = datetime.now() + timedelta(days=3)
        result = triggered_handler.check_convergence("s1", current_exposure=0.28, now=now)
        assert result.state.current_tier == TierLevel.TIER_3_FORCE_TRIM  # 状态机照常推进
        assert any(e.event_id == "E-POS-41" for e in events)  # 后续订阅者仍收到

    def test_unsubscribe_stops_events(self, handler: BudgetChangeHandler) -> None:
        """退订后不再收到事件。"""
        events: list[BudgetHandlerEvent] = []
        handler.subscribe(events.append)
        handler.unsubscribe(events.append)
        handler.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板", current_date=D1)
        assert events == []


# ── A13：TierState 跨日持久化（JSON 快照 + fail-closed 恢复）─────────────────


class TestTierStatePersistence:
    """persist_path 配置后：状态变更自动快照，重启恢复；损坏 fail-closed。"""

    def test_snapshot_roundtrip_across_restart(self, tmp_path: Path) -> None:
        """触发升级 → 新实例从快照恢复 tier/窗口/指令留痕（跨日收敛窗口不断档）。"""
        path = tmp_path / "tier_state.json"
        h1 = BudgetChangeHandler(persist_path=path)
        h1.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板", current_date=D1)

        h2 = BudgetChangeHandler(persist_path=path)
        state = h2.get_state("s1")
        assert state is not None
        assert state.current_tier == TierLevel.TIER_2_REBALANCE
        assert state.target_budget == pytest.approx(0.20)
        assert state.strategy_type == "打板"
        assert state.convergence_window_end is not None
        assert [rec["tier"] for rec in state.instructions_issued] == [1, 2]

    def test_missing_snapshot_starts_empty(self, tmp_path: Path) -> None:
        """快照不存在 → 空起步（首日运行），不抛错。"""
        path = tmp_path / "nonexistent.json"
        h = BudgetChangeHandler(persist_path=path)
        assert h.get_state("s1") is None

    def test_corrupt_snapshot_fail_closed(self, tmp_path: Path) -> None:
        """快照 JSON 损坏 → StateRecoveryError（ZA-POS-0044），不静默丢弃降级中状态。"""
        path = tmp_path / "tier_state.json"
        path.write_text("{ not json", encoding="utf-8")
        with pytest.raises(StateRecoveryError) as exc_info:
            BudgetChangeHandler(persist_path=path)
        assert exc_info.value.error_code == "ZA-POS-0044"

    def test_schema_version_mismatch_fail_closed(self, tmp_path: Path) -> None:
        """schema_version 不符 → StateRecoveryError fail-closed。"""
        import json

        path = tmp_path / "tier_state.json"
        path.write_text(json.dumps({"schema_version": "9.9", "states": {}}), encoding="utf-8")
        with pytest.raises(StateRecoveryError, match="schema"):
            BudgetChangeHandler(persist_path=path)

    def test_tier_state_dict_roundtrip(self, triggered_handler: BudgetChangeHandler) -> None:
        """TierState.to_dict/from_dict 全字段往返一致。"""
        state = triggered_handler.get_state("s1")
        assert state is not None
        restored = TierState.from_dict(state.to_dict())
        assert restored.strategy_id == state.strategy_id
        assert restored.current_tier == state.current_tier
        assert restored.old_budget == pytest.approx(state.old_budget)
        assert restored.target_budget == pytest.approx(state.target_budget)
        assert restored.tier1_at == state.tier1_at
        assert restored.convergence_window_end == state.convergence_window_end
        assert restored.strategy_type == state.strategy_type
        assert [r["tier"] for r in restored.instructions_issued] == [1, 2]

    def test_convergence_check_persists_days_count(self, tmp_path: Path) -> None:
        """check_convergence 的持续性计数也入快照（跨日累计不丢）。"""
        path = tmp_path / "tier_state.json"
        h1 = BudgetChangeHandler(persist_path=path, eps_days=3)
        h1.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板", current_date=D1)
        h1.check_convergence("s1", current_exposure=0.205)  # 收敛但持续性 1/3

        h2 = BudgetChangeHandler(persist_path=path, eps_days=3)
        state = h2.get_state("s1")
        assert state is not None
        assert state.convergence_days_satisfied == 1

    def test_no_persist_path_no_file(self, handler: BudgetChangeHandler, tmp_path: Path) -> None:
        """默认无 persist_path → 纯进程内缓存，不产生文件（向后兼容）。"""
        handler.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板", current_date=D1)
        assert list(tmp_path.iterdir()) == []


# ── A13：sync_from_allocator 生产调用方接线 ──────────────────────────────


class _FakeAllocation:
    """duck-typed BudgetAllocation（不 import pf_alloc，依赖倒置）。"""

    def __init__(self, effective_budgets: dict[str, float]) -> None:
        self.effective_budgets = effective_budgets


class TestSyncFromAllocator:
    """sync_from_allocator：BudgetAllocation → 自动 diff 上期快照 → 三级升级裁决。"""

    def test_first_sync_all_new_strategies_skipped(self, handler: BudgetChangeHandler) -> None:
        """首次同步无上期快照 → 全部视为新策略首配跳过，且记忆本期快照。"""
        results = handler.sync_from_allocator(_FakeAllocation({"s1": 0.30}), current_date=D1)
        assert results == {}
        assert handler._last_effective_budgets == {"s1": 0.30}

    def test_second_sync_diffs_remembered_previous(self, handler: BudgetChangeHandler) -> None:
        """第二次同步自动以上期快照为 previous：下调 ≥5% → 触发 Tier1+Tier2。"""
        handler.sync_from_allocator(_FakeAllocation({"s1": 0.30}), current_date=D1)
        results = handler.sync_from_allocator(_FakeAllocation({"s1": 0.20}), current_date=D2)
        assert [i["tier"] for i in results["s1"].instructions] == [1, 2]

    def test_explicit_previous_overrides_memory(self, handler: BudgetChangeHandler) -> None:
        """显式 previous_budgets 优先于记忆快照。"""
        results = handler.sync_from_allocator(
            _FakeAllocation({"s1": 0.20}), previous_budgets={"s1": 0.30}, current_date=D1
        )
        assert [i["tier"] for i in results["s1"].instructions] == [1, 2]

    def test_plain_dict_accepted(self, handler: BudgetChangeHandler) -> None:
        """纯 dict 映射同样接受（无 effective_budgets 属性时按 dict 处理）。"""
        handler.sync_from_allocator({"s1": 0.30}, current_date=D1)
        results = handler.sync_from_allocator({"s1": 0.35}, current_date=D2)
        assert results["s1"].action.startswith("NO_ACTION")

    def test_none_allocation_raises(self, handler: BudgetChangeHandler) -> None:
        """allocation=None → BudgetChangeError（ZA-POS-0040）。"""
        with pytest.raises(BudgetChangeError) as exc_info:
            handler.sync_from_allocator(None, current_date=D1)
        assert exc_info.value.error_code == "ZA-POS-0040"

    def test_invalid_effective_budgets_raises(self, handler: BudgetChangeHandler) -> None:
        """effective_budgets 含非数值 → BudgetChangeError（Fail-Closed 不猜输入）。"""
        with pytest.raises(BudgetChangeError):
            handler.sync_from_allocator(_FakeAllocation({"s1": "0.30"}), current_date=D1)  # type: ignore[dict-item]

    def test_non_dict_non_allocation_raises(self, handler: BudgetChangeHandler) -> None:
        """既非 dict 又无 effective_budgets → BudgetChangeError。"""
        with pytest.raises(BudgetChangeError):
            handler.sync_from_allocator(42, current_date=D1)

    def test_previous_snapshot_survives_restart(self, tmp_path: Path) -> None:
        """persist_path 配置时上期快照跨日持久：重启后第二次同步仍能 diff 触发。"""
        path = tmp_path / "tier_state.json"
        h1 = BudgetChangeHandler(persist_path=path)
        h1.sync_from_allocator(_FakeAllocation({"s1": 0.30}), current_date=D1)

        h2 = BudgetChangeHandler(persist_path=path)  # 模拟次日重启
        results = h2.sync_from_allocator(_FakeAllocation({"s1": 0.20}), current_date=D2)
        assert [i["tier"] for i in results["s1"].instructions] == [1, 2]

    def test_sync_emits_handled_events(self, handler: BudgetChangeHandler) -> None:
        """sync 走 handle_budget_change → 每策略发 BudgetChangeHandled。"""
        events: list[BudgetHandlerEvent] = []
        handler.subscribe(events.append)
        handler.sync_from_allocator({"s1": 0.30}, current_date=D1)
        handler.sync_from_allocator({"s1": 0.20}, current_date=D2)
        handled = [e for e in events if e.event_id == "E-POS-40" and e.strategy_id == "s1"]
        assert len(handled) == 1  # 首配跳过无事件，第二次下调裁决发一条
