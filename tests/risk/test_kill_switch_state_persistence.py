# [BLUEPRINT] MOD-L04-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""Kill Switch 状态持久化 + 清算韧性测试（Qwen P0-3 / 裁定书 §六 ①⑤）。

红队实证（验收①）：
1. 熔断后杀进程重启，熔断状态仍在（Fail-Closed）；
2. 清算函数并发双触发只发一轮单（LIQUIDATING 全局状态锁）；
3. 同一 event_id 重放不重复发单（幂等键贯穿）；
4. 逐标的清算以券商实时持仓为准（非调用方快照）；
5. 两触发入口合并单一仲裁点（stop_loss ↔ DefaultRiskValidator 同一持久化记录）；
6. 幽灵持仓第三枚举 unknown_to_strategy（裁定书 §二）。
"""

from __future__ import annotations

import threading

from zephyr.risk.implementations.default_risk_validator import (
    GHOST_UNKNOWN_TO_STRATEGY,
    DefaultRiskValidator,
)
from zephyr.risk.stop_loss import (
    detect_ghost_positions,
    execute_kill_switch_liquidation,
    reset_kill_switch,
    trigger_kill_switch,
)
from zephyr.shared.state_store import JsonStateStore

# ── 测试替身 ──


class _FakeBroker:
    """无实时查询能力的 broker（兜底快照路径）。"""

    def __init__(self):
        self.placed_orders: list[dict] = []
        self.cancelled_orders: list[str] = []

    def cancel_order(self, order_id: str) -> None:
        self.cancelled_orders.append(order_id)

    def place_order(self, symbol: str, direction: str, qty: float, order_type: str) -> None:
        self.placed_orders.append({"symbol": symbol, "direction": direction, "qty": qty, "order_type": order_type})


class _LiveBroker(_FakeBroker):
    """带 get_holdings 实时持仓的 broker。"""

    def __init__(self, live: dict[str, float]):
        super().__init__()
        self._live = live

    def get_holdings(self) -> dict[str, float]:
        return dict(self._live)


class _BlockingBroker(_FakeBroker):
    """place_order 阻塞的 broker——制造并发清算窗口。"""

    def __init__(self, started: threading.Event, release: threading.Event):
        super().__init__()
        self._started = started
        self._release = release

    def place_order(self, symbol: str, direction: str, qty: float, order_type: str) -> None:
        self._started.set()
        self._release.wait(timeout=5)
        super().place_order(symbol, direction, qty, order_type)


# ── 红队 1：熔断状态持久化（Fail-Closed）──


class TestKillSwitchStatePersistence:
    def test_trigger_persists_and_survives_restart(self, tmp_path):
        """熔断后杀进程重启（新实例），熔断状态仍在。"""
        store = JsonStateStore(tmp_path)
        v1 = DefaultRiskValidator(state_store=store)
        v1.trigger_kill_switch(reason="drawdown > 25%", event_id="evt-dd-1")

        # 模拟进程重启：新实例从同一 store 加载
        v2 = DefaultRiskValidator(state_store=store)
        assert v2.kill_switch_active is True

    def test_corrupt_state_fail_closed(self, tmp_path):
        """状态记录损坏 → 读不到按已熔断处理。"""
        (tmp_path / "kill_switch.json").write_bytes(b"{corrupted!!")
        v = DefaultRiskValidator(state_store=JsonStateStore(tmp_path))
        assert v.kill_switch_active is True

    def test_fresh_boot_not_active(self, tmp_path):
        """fresh boot（无记录）→ 未熔断（不误伤首次部署）。"""
        v = DefaultRiskValidator(state_store=JsonStateStore(tmp_path))
        assert v.kill_switch_active is False

    def test_reset_persists_and_restart_inactive(self, tmp_path):
        store = JsonStateStore(tmp_path)
        v1 = DefaultRiskValidator(state_store=store)
        v1.trigger_kill_switch(reason="test")
        v1.reset_kill_switch({"confirmed_by": "ops", "holdings_verified_zero": True})

        v2 = DefaultRiskValidator(state_store=store)
        assert v2.kill_switch_active is False

    def test_memory_mode_unchanged(self):
        """无 store（既有行为）：纯内存，不持久化。"""
        v = DefaultRiskValidator()
        assert v.kill_switch_active is False
        v.trigger_kill_switch()
        assert v.kill_switch_active is True
        v.reset_kill_switch()
        assert v.kill_switch_active is False


# ── 红队 5：两触发入口合并单一仲裁点 ──


class TestSingleArbitrationPoint:
    def test_stop_loss_trigger_visible_to_validator(self, tmp_path):
        """stop_loss.trigger_kill_switch 触发 → validator 启动加载即熔断。"""
        store = JsonStateStore(tmp_path)
        event = trigger_kill_switch("drawdown EMERGENCY", state_store=store)
        assert event["status"] == "triggered"

        v = DefaultRiskValidator(state_store=store)
        assert v.kill_switch_active is True

    def test_validator_trigger_visible_to_stop_loss_reset(self, tmp_path):
        """validator 触发 → stop_loss.reset 解除 → 新 validator 实例未熔断。"""
        store = JsonStateStore(tmp_path)
        v1 = DefaultRiskValidator(state_store=store)
        v1.trigger_kill_switch(reason="test", event_id="evt-x")

        ok = reset_kill_switch({"confirmed_by": "ops"}, state_store=store)
        assert ok is True

        v2 = DefaultRiskValidator(state_store=store)
        assert v2.kill_switch_active is False


# ── 红队 2/3：清算锁 + 幂等 ──


class TestLiquidationResilience:
    def test_concurrent_double_trigger_only_one_round(self, tmp_path):
        """并发双触发：只发一轮单（另一路 rejected_already_liquidating，未发单）。"""
        store = JsonStateStore(tmp_path)
        started = threading.Event()
        release = threading.Event()
        broker = _BlockingBroker(started, release)
        positions = {"600000.SH": 1000}

        results: dict[str, dict] = {}

        def run_first():
            results["first"] = execute_kill_switch_liquidation(broker, positions, event_id="evt-1", state_store=store)

        def run_second():
            results["second"] = execute_kill_switch_liquidation(broker, positions, event_id="evt-2", state_store=store)

        t1 = threading.Thread(target=run_first)
        t1.start()
        assert started.wait(timeout=5), "第一路清算未进入发单阶段"

        t2 = threading.Thread(target=run_second)
        t2.start()
        t2.join(timeout=10)
        release.set()
        t1.join(timeout=10)

        assert results["second"]["status"] == "rejected_already_liquidating"
        assert results["second"]["all_success"] is False
        # 只发一轮单
        assert len(broker.placed_orders) == 1
        assert results["first"]["liquidation_orders"] == ["600000.SH"]

    def test_same_event_id_replay_no_duplicate_orders(self, tmp_path):
        """同一 event_id 重放 → idempotent_replay，不重复发单。"""
        store = JsonStateStore(tmp_path)
        broker = _FakeBroker()
        positions = {"600000.SH": 1000}

        r1 = execute_kill_switch_liquidation(broker, positions, event_id="evt-dup", state_store=store)
        assert r1["status"] == "executed"
        assert len(broker.placed_orders) == 1

        r2 = execute_kill_switch_liquidation(broker, positions, event_id="evt-dup", state_store=store)
        assert r2["status"] == "idempotent_replay"
        assert len(broker.placed_orders) == 1  # 未重复发单

    def test_corrupt_lock_fail_closed(self, tmp_path):
        """清算锁记录损坏 → Fail-Closed 拒绝进入（未发单）。"""
        store = JsonStateStore(tmp_path)
        (tmp_path / "kill_switch_liquidation.json").write_bytes(b"{broken!!")
        broker = _FakeBroker()

        result = execute_kill_switch_liquidation(broker, {"600000.SH": 1000}, state_store=store)
        assert result["status"] == "rejected_state_corrupt"
        assert result["all_success"] is False
        assert broker.placed_orders == []

    def test_liquidation_uses_live_broker_holdings(self, tmp_path):
        """逐标的以券商实时持仓为准：快照 1000/500，实时 300/0 → 只卖 300。"""
        store = JsonStateStore(tmp_path)
        broker = _LiveBroker({"600000.SH": 300, "000001.SZ": 0})

        result = execute_kill_switch_liquidation(
            broker,
            {"600000.SH": 1000, "000001.SZ": 500},  # 调用方旧快照
            event_id="evt-live",
            state_store=store,
        )
        assert result["all_success"] is True
        assert broker.placed_orders == [
            {"symbol": "600000.SH", "direction": "SELL", "qty": 300, "order_type": "MARKET"}
        ]

    def test_legacy_mode_no_store_unchanged(self):
        """无 store（既有行为）：调用方快照直发，报告带 status=executed。"""
        broker = _FakeBroker()
        result = execute_kill_switch_liquidation(broker, {"600000.SH": 1000}, {"ord-1": {}}, scope="all")
        assert result["status"] == "executed"
        assert len(result["cancelled_orders"]) == 1
        assert len(result["liquidation_orders"]) == 1


# ── 红队 6：幽灵持仓第三枚举 ──


class TestGhostThirdEnum:
    def test_stop_loss_unknown_to_strategy(self):
        ghosts = detect_ghost_positions(
            broker_holdings={"600000.SH": {"qty": 1000}, "000001.SZ": {"qty": 500}},
            strategy_state={"600000.SH": "OPEN"},  # 000001.SZ 无任何记录
        )
        assert ghosts == [("000001.SZ", {"qty": 500}, GHOST_UNKNOWN_TO_STRATEGY)]

    def test_validator_unknown_to_strategy(self):
        v = DefaultRiskValidator()
        ghosts = v.detect_ghost_positions(
            broker_holdings={"600000.SH": {"qty": 1000}},
            strategy_state={},  # 策略侧无记录（crash 后状态丢失场景）
        )
        assert ghosts == [("600000.SH", {"qty": 1000}, GHOST_UNKNOWN_TO_STRATEGY)]

    def test_existing_two_enums_unchanged(self):
        v = DefaultRiskValidator(kill_switch_active=True)
        ghosts = v.detect_ghost_positions(
            broker_holdings={
                "600000.SH": {"qty": 100},  # CLOSED → 情况1
                "000001.SZ": {"qty": 200},  # OPEN → 情况2（kill switch active）
                "000002.SZ": {"qty": 0},  # 零持仓不报
            },
            strategy_state={"600000.SH": "CLOSED", "000001.SZ": "OPEN"},
        )
        assert ("600000.SH", {"qty": 100}, "strategy_closed_but_broker_holds") in ghosts
        assert ("000001.SZ", {"qty": 200}, "kill_switch_active_but_position_remains") in ghosts
        assert len(ghosts) == 2
