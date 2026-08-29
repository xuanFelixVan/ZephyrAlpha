# [A_test] module_id: MOD-RK-DWD | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RK-011 | §3.5.1/§6.11
# [MODULE] tests.risk.test_drawdown_watchdog
# [INVARIANTS] 一致→CONSISTENT 不锁仓; ghosts→GHOST_DETECTED+强平清单去重+锁新开仓; 轮询失败→POLL_FAILED 锁新开仓但不盲强平; kill_switch CLOSED+有持仓→全量强平; strategy_state None=冷启动守卫全部 Ghost
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/test_drawdown_watchdog.py
# [TTL] task_bound
"""L3 看门狗一致性裁决测试（35 号 §6.11，§3.5.1 四层架构 L3 落地）。"""

from __future__ import annotations

import pytest

from zephyr.risk.core.drawdown_watchdog import (
    WATCHDOG_STATUS_CONSISTENT,
    WATCHDOG_STATUS_GHOST_DETECTED,
    WATCHDOG_STATUS_POLL_FAILED,
    InvalidWatchdogInputError,
    poll_once,
)


class TestPollOnceConsistent:
    def test_consistent(self):
        v = poll_once({"A": {"qty": 100}}, {"A": "OPEN"})
        assert v.status == WATCHDOG_STATUS_CONSISTENT
        assert v.ghosts == () and v.force_liquidate_symbols == ()
        assert v.halt_new_orders is False

    def test_empty_holdings_consistent(self):
        v = poll_once({}, {"A": "CLOSED"})
        assert v.status == WATCHDOG_STATUS_CONSISTENT
        assert v.halt_new_orders is False

    def test_zero_qty_ignored(self):
        """qty=0 非持仓，不触发 Ghost。"""
        v = poll_once({"A": {"qty": 0}}, {})
        assert v.status == WATCHDOG_STATUS_CONSISTENT


class TestPollOnceGhostDetected:
    def test_strategy_closed_but_broker_holds(self):
        """情况 1：策略 CLOSED 但 broker 仍持有 → 强平该标的。"""
        v = poll_once({"A": {"qty": 100}}, {"A": "CLOSED"})
        assert v.status == WATCHDOG_STATUS_GHOST_DETECTED
        assert v.force_liquidate_symbols == ("A",)
        assert v.halt_new_orders is True
        assert v.ghosts[0][2] == "strategy_closed_but_broker_holds"

    def test_unknown_to_strategy(self):
        """情况 3：策略无记录但 broker 有持仓 → 来源不明 Ghost。"""
        v = poll_once({"A": {"qty": 100}}, {"B": "OPEN"})
        assert v.status == WATCHDOG_STATUS_GHOST_DETECTED
        assert v.force_liquidate_symbols == ("A",)
        assert v.ghosts[0][2] == "unknown_to_strategy"

    def test_kill_switch_closed_force_liquidate_all(self):
        """情况 2：Kill Switch CLOSED 且残余持仓 → 全量强平。"""
        v = poll_once(
            {"A": {"qty": 100}, "B": {"qty": 200}},
            {"A": "OPEN", "B": "OPEN"},
            kill_switch_state="CLOSED",
        )
        assert v.status == WATCHDOG_STATUS_GHOST_DETECTED
        assert set(v.force_liquidate_symbols) == {"A", "B"}
        assert v.halt_new_orders is True
        assert all(g[2] == "kill_switch_closed_but_position_remains" for g in v.ghosts)

    def test_kill_switch_closed_dedup_with_strategy_closed(self):
        """同标的多类型 Ghost 去重（force_liquidate 不重复）。"""
        v = poll_once({"A": {"qty": 100}}, {"A": "CLOSED"}, kill_switch_state="CLOSED")
        assert v.status == WATCHDOG_STATUS_GHOST_DETECTED
        assert v.force_liquidate_symbols == ("A",)

    def test_cold_start_guard(self):
        """strategy_state=None 冷启动守卫：broker 有持仓全部视为 Ghost。"""
        v = poll_once({"A": {"qty": 100}, "B": {"qty": 0}}, None)
        assert v.status == WATCHDOG_STATUS_GHOST_DETECTED
        assert v.force_liquidate_symbols == ("A",)
        assert v.ghosts[0][2] == "unknown_to_strategy"

    def test_cold_start_guard_empty_broker(self):
        """冷启动 + broker 空仓 → 正常通过。"""
        v = poll_once({}, None)
        assert v.status == WATCHDOG_STATUS_CONSISTENT


class TestPollOnceFailClosed:
    def test_poll_failed_halt_without_blind_liquidation(self):
        """轮询失败 fail-closed：锁新开仓但绝不基于缺失数据盲强平。"""
        v = poll_once(None, {"A": "OPEN"})
        assert v.status == WATCHDOG_STATUS_POLL_FAILED
        assert v.halt_new_orders is True
        assert v.force_liquidate_symbols == ()
        assert v.ghosts == ()

    def test_invalid_kill_switch_state(self):
        with pytest.raises(InvalidWatchdogInputError):
            poll_once({}, {}, kill_switch_state="BROKEN")

    def test_invalid_holding_payload(self):
        with pytest.raises(InvalidWatchdogInputError):
            poll_once({"A": "not_a_mapping"}, {"A": "OPEN"})
