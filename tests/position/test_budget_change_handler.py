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

import pytest

from zephyr.position.core.budget_change_handler import (
    BudgetChangeHandler,
    ForcedTrim,
    FreezeNewPositions,
    RebalanceRequest,
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
def test_convergence_window_differentiated(
    handler: BudgetChangeHandler, strategy_type: str, days: int
) -> None:
    """打板 2 天 / 多因子 4 天 / 事件驱动 3 天 / 未知缺省 3 天。"""
    result = handler.handle_budget_change(
        "s1", 0.30, 0.20, strategy_type=strategy_type, current_date=D1
    )
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
    handler.check_convergence("s1", current_exposure=0.28)   # 偏离，清零
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
        result = handler.on_firm_violation(
            "s1", current_exposure=0.40, target_budget=0.20, violation="单票超限未纠正"
        )
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
