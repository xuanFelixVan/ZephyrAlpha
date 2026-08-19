# [A_test] module_id: MOD-RK-DSP | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] 35_drawdown_protocol_impl | §3.15/§3.18/§6.12
# [MODULE] tests.risk.test_drawdown_session_persistence
# [INVARIANTS] 盘前四阶段顺序; 盘后审计门控+原子提交; peak单调非减; nav_history幂等滚动窗; restore_peak取max保不变量
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/test_drawdown_session_persistence.py
# [TTL] task_bound
"""盘前初始化 + 盘后持久化配对编排测试（35 号 §3.15/§3.18/§6.12）。"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from zephyr.position.core.capital_curve_manager import CapitalCurveManager
from zephyr.risk.core.drawdown_session_persistence import (
    STATUS_AUDIT_FAILED_SKIP,
    STATUS_DRAWDOWN_COMPLETE,
    InvalidSessionPersistInputError,
    append_nav_history,
    load_attribution_result,
    load_entry_var,
    load_nav_history,
    load_peak_nav,
    load_persistable_status,
    load_strategy_state,
    mark_persistable,
    postmarket_persist,
    premarket_initialization,
    save_attribution_result,
    save_entry_var,
    save_peak_nav,
    save_strategy_state,
)
from zephyr.risk.core.drawdown_state_machine import DrawdownStateMachine
from zephyr.shared.state_store import JsonStateStore

D0 = date(2026, 8, 3)


def _day(n: int) -> date:
    return D0 + timedelta(days=n)


# ── 低层存取原语对 ──


class TestPrimitives:
    def test_peak_nav_roundtrip_and_none(self, tmp_path):
        store = JsonStateStore(tmp_path)
        assert load_peak_nav(store) is None
        save_peak_nav(store, 1_050_000.0)
        assert load_peak_nav(store) == 1_050_000.0

    def test_peak_nav_rejects_non_positive(self, tmp_path):
        with pytest.raises(InvalidSessionPersistInputError):
            save_peak_nav(JsonStateStore(tmp_path), 0.0)

    def test_nav_history_append_trim_and_idempotent(self, tmp_path):
        store = JsonStateStore(tmp_path)
        for i in range(5):
            append_nav_history(store, _day(i), 100.0 + i, window=3)
        assert load_nav_history(store) == (102.0, 103.0, 104.0)  # trim 到窗口 3
        # 同日重复 = 更新当日（幂等）
        append_nav_history(store, _day(4), 999.0, window=3)
        assert load_nav_history(store) == (102.0, 103.0, 999.0)

    def test_entry_var_roundtrip_and_validation(self, tmp_path):
        store = JsonStateStore(tmp_path)
        assert load_entry_var(store) is None
        save_entry_var(store, _day(0), 0.025)
        assert load_entry_var(store) == 0.025
        with pytest.raises(InvalidSessionPersistInputError):
            save_entry_var(store, _day(1), -0.01)

    def test_attribution_roundtrip(self, tmp_path):
        store = JsonStateStore(tmp_path)
        assert load_attribution_result(store) is None
        save_attribution_result(store, _day(0), {"root_cause": "SYSTEMIC", "systemic_pct": 1.0})
        assert load_attribution_result(store)["root_cause"] == "SYSTEMIC"

    def test_strategy_state_roundtrip(self, tmp_path):
        store = JsonStateStore(tmp_path)
        assert load_strategy_state(store) is None
        save_strategy_state(store, _day(0), {"600519": "OPEN"})
        assert load_strategy_state(store) == {"600519": "OPEN"}

    def test_mark_persistable_and_status(self, tmp_path):
        store = JsonStateStore(tmp_path)
        assert load_persistable_status(store) is None
        mark_persistable(store, _day(0), STATUS_DRAWDOWN_COMPLETE)
        assert load_persistable_status(store) == STATUS_DRAWDOWN_COMPLETE
        with pytest.raises(InvalidSessionPersistInputError):
            mark_persistable(store, _day(0), "BOGUS")


# ── 盘后持久化（§3.18）──


class TestPostmarketPersist:
    def test_happy_path_full_phases(self, tmp_path):
        store = JsonStateStore(tmp_path)
        sm = DrawdownStateMachine(store)
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.06)  # → WARN
        result = postmarket_persist(
            store,
            trade_date=_day(0),
            closing_nav=940_000.0,
            state_machine=sm,
            var_95=0.023,
            attribution_result={"root_cause": "SYSTEMIC_HIGH_CORRELATION"},
            strategy_holdings={"600519": "OPEN"},
        )
        assert result.status == "PERSISTED"
        assert result.new_peak == 940_000.0 and result.old_peak is None
        assert result.is_new_high is True
        assert load_persistable_status(store) == STATUS_DRAWDOWN_COMPLETE
        assert load_peak_nav(store) == 940_000.0
        assert load_nav_history(store) == (940_000.0,)
        assert load_entry_var(store) == 0.023
        assert load_attribution_result(store)["root_cause"] == "SYSTEMIC_HIGH_CORRELATION"
        assert load_strategy_state(store) == {"600519": "OPEN"}

    def test_peak_monotonic_max(self, tmp_path):
        store = JsonStateStore(tmp_path)
        postmarket_persist(store, trade_date=_day(0), closing_nav=1_000_000.0)
        result = postmarket_persist(store, trade_date=_day(1), closing_nav=940_000.0)
        assert result.new_peak == 1_000_000.0  # peak 不回退（§3.8 单调非减）
        assert result.is_new_high is False

    def test_audit_gate_skips_persistence(self, tmp_path):
        store = JsonStateStore(tmp_path)
        sm = DrawdownStateMachine(store)
        result = postmarket_persist(
            store,
            trade_date=_day(0),
            closing_nav=940_000.0,
            state_machine=sm,
            var_95=0.02,
            audit_passed=False,
            audit_failure_reason="ghost_not_cleared",
        )
        assert result.status == "SKIPPED_AUDIT_FAILED"
        assert load_persistable_status(store) == STATUS_AUDIT_FAILED_SKIP
        # 门控失败：后续阶段全部不执行（宁丢状态不存错状态）
        assert load_nav_history(store) == ()
        assert load_entry_var(store) is None
        assert load_peak_nav(store) is None

    def test_invalid_closing_nav_raises(self, tmp_path):
        with pytest.raises(InvalidSessionPersistInputError):
            postmarket_persist(
                JsonStateStore(tmp_path), trade_date=_day(0), closing_nav=0.0
            )


# ── 盘前初始化（§3.15 四阶段）──


class TestPremarketInitialization:
    def test_cold_start_defaults(self, tmp_path):
        store = JsonStateStore(tmp_path)
        result = premarket_initialization(store)
        assert result.status == "READY"
        assert result.restored_state == "cold_start_default_NORMAL"
        assert result.state_machine is not None
        assert result.state_machine.current.value == "NORMAL"
        assert result.insufficient_history is True  # 0 < 30
        assert result.conservative_position_cap == 0.5
        assert result.entry_var is None

    def test_restore_after_postmarket(self, tmp_path):
        """配对闭环：T-1 盘后持久化 → T 盘前恢复（状态机/peak/entry_var/归因）。"""
        store = JsonStateStore(tmp_path)
        sm = DrawdownStateMachine(store)
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.06)  # → WARN
        postmarket_persist(
            store, trade_date=_day(0), closing_nav=940_000.0,
            state_machine=sm, var_95=0.023,
            attribution_result={"root_cause": "MIXED_PARTIAL_SYSTEMIC"},
        )
        result = premarket_initialization(store)
        assert result.status == "READY"
        assert result.restored_state == "restored_WARN"
        assert result.state_machine.current.value == "WARN"
        assert result.peak_nav == 940_000.0
        assert result.entry_var == 0.023
        assert result.prev_attribution["root_cause"] == "MIXED_PARTIAL_SYSTEMIC"

    def test_ghost_cold_start_guard(self, tmp_path):
        """冷启动守卫：无策略记录但 broker 有持仓 → 全部视为 Ghost，拒绝启动。"""
        store = JsonStateStore(tmp_path)
        result = premarket_initialization(
            store, broker_holdings={"600519": {"qty": 100}}, strategy_state=None
        )
        assert result.status == "REFUSED"
        assert "Ghost" in result.refuse_reason
        assert result.ghosts[0][0] == "600519"

    def test_ghost_detected_with_strategy_state(self, tmp_path):
        store = JsonStateStore(tmp_path)
        result = premarket_initialization(
            store,
            broker_holdings={"600519": {"qty": 100}},
            strategy_state={"600519": "CLOSED"},
        )
        assert result.status == "REFUSED"
        assert result.ghosts[0][2] == "strategy_closed_but_broker_holds"

    def test_empty_holdings_pass(self, tmp_path):
        store = JsonStateStore(tmp_path)
        result = premarket_initialization(
            store, broker_holdings={}, strategy_state=None
        )
        assert result.status == "READY"

    def test_health_check_failure_refuses(self, tmp_path):
        store = JsonStateStore(tmp_path)
        result = premarket_initialization(store, health_check=lambda: False)
        assert result.status == "REFUSED"
        assert "不健康" in result.refuse_reason

    def test_kill_switch_still_closed_flag(self, tmp_path):
        """持久化态 KILL → 盘前保持禁开仓标记（待人工复位）。"""
        store = JsonStateStore(tmp_path)
        sm = DrawdownStateMachine(store)
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.30)  # → KILL
        postmarket_persist(store, trade_date=_day(0), closing_nav=700_000.0, state_machine=sm)
        result = premarket_initialization(store)
        assert result.restored_state == "restored_KILL"
        assert result.kill_switch_still_closed is True

    def test_sufficient_history_no_conservative_cap(self, tmp_path):
        store = JsonStateStore(tmp_path)
        for i in range(30):
            append_nav_history(store, _day(i), 100.0 + i)
        result = premarket_initialization(store)
        assert result.insufficient_history is False
        assert result.conservative_position_cap is None
        assert len(result.nav_history) == 30


# ── capital_curve_manager.restore_peak（§3.15 基线校准配套）──


class TestRestorePeak:
    def test_restore_higher_peak(self):
        mgr = CapitalCurveManager(initial_capital=1_000_000.0)
        mgr.restore_peak(1_200_000.0)
        assert mgr.peak == 1_200_000.0
        snap = mgr.record(1_100_000.0)  # 回撤按恢复后 peak 计算
        assert snap.peak == 1_200_000.0
        assert abs(snap.drawdown - (1_100_000.0 - 1_200_000.0) / 1_200_000.0) < 1e-12

    def test_restore_lower_peak_keeps_max(self):
        """不变量优先：恢复值低于内存 peak 取 max（防持久化回退造假新高）。"""
        mgr = CapitalCurveManager(initial_capital=1_000_000.0)
        mgr.record(1_500_000.0)
        mgr.restore_peak(1_200_000.0)
        assert mgr.peak == 1_500_000.0

    def test_restore_rejects_non_positive(self):
        mgr = CapitalCurveManager(initial_capital=1_000_000.0)
        with pytest.raises(Exception, match="positive"):
            mgr.restore_peak(0.0)
        with pytest.raises(Exception, match="positive"):
            mgr.restore_peak(-5.0)
