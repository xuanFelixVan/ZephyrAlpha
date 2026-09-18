# [BLUEPRINT] MOD-EX-049 | tests/ex_core | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""订单幂等键确定性 + 去重状态落库持久化测试（R-L3 裁定，尽调 C1/A 类资金安全件）。

覆盖三条硬验收：
  1. 幂等键由业务语义确定性生成（同输入两次运行同键，不再 uuid4 随机）；
  2. 去重状态落库（SQLite，经 DatabaseService 同源连接工厂），进程重启后可读回；
  3. "下单 → 进程崩溃 → 重启 → 同信号重放" 不会二次发单。

安全边界：本套件零实盘路径，全部使用 MagicMock 假 xttrader，不触网、不写生产 data/ 目录
（持久化后端一律 tmp_path fixture）。
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker, MiniQmtBrokerError
from zephyr.ex_core.order_manager import OrderManager
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order
from zephyr.shared.infra.idempotency import (
    IdempotencyStatus,
    SQLiteIdempotencyStore,
    build_order_idempotency_key,
)

# ──────────────────────────────────────────────────────────────────────────────
# 工厂
# ──────────────────────────────────────────────────────────────────────────────

_KEY_INPUTS = {
    "strategy_id": "STR-TEST-001",
    "symbol": "600000",
    "trade_date": "2026-09-18",
    "signal_batch_id": "batch-2026-09-18-01",
    "side": "buy",
}


def _make_order(idempotency_key: str = "ord-deterministic-1") -> Order:
    return Order(
        idempotency_key=idempotency_key,
        order_id="local-order-1",
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        side=OrderSide.BUY,
        strategy_id=_KEY_INPUTS["strategy_id"],
        symbol=_KEY_INPUTS["symbol"],
        limit_price=Decimal("10.00"),
    )


def _make_broker(store_db) -> MiniQmtBroker:
    """构造仅用于幂等验证的 broker：假 xttrader + 假 account + 已连接。"""
    broker = MiniQmtBroker(path="", session_id="idem-test", account_id="8886156677")
    broker._connected = True
    broker._xttrader = MagicMock()
    broker._xttrader.order_stock.return_value = 424242
    broker._account = MagicMock()
    broker.idempotency_store = SQLiteIdempotencyStore(db_path=store_db, default_ttl_seconds=0)
    return broker


@pytest.fixture
def _bypass_constraints():
    """隔离 A 股约束/价格笼子校验，令测试只聚焦幂等语义。"""
    with (
        patch.object(MiniQmtBroker, "_validate_a_share_constraints"),
        patch.object(MiniQmtBroker, "_apply_price_cage_locked"),
    ):
        yield


# ──────────────────────────────────────────────────────────────────────────────
# 验收①：键确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterministicKey:
    def test_same_inputs_same_key_across_calls(self):
        k1 = build_order_idempotency_key(**_KEY_INPUTS)
        k2 = build_order_idempotency_key(**_KEY_INPUTS)
        assert k1 == k2
        assert len(k1) == 64  # sha256 全摘要，不截断

    def test_each_business_field_participates(self):
        base = build_order_idempotency_key(**_KEY_INPUTS)
        for field in _KEY_INPUTS:
            mutated = dict(_KEY_INPUTS)
            mutated[field] = str(mutated[field]) + "-x"
            assert build_order_idempotency_key(**mutated) != base, f"{field} 未参与键构成"

    def test_key_is_not_random_uuid(self):
        k = build_order_idempotency_key(**_KEY_INPUTS)
        assert "-" not in k  # uuid4 形如 8-4-4-4-12

    def test_order_manager_emits_deterministic_key(self):
        """同一信号批次内两次 create_order（同标的/方向）产出同键 ⇒ 重放可去重。"""
        mgr = OrderManager()
        mgr.begin_signal_batch(_KEY_INPUTS["signal_batch_id"], trade_date=_KEY_INPUTS["trade_date"])
        o1 = mgr.create_order(
            symbol=_KEY_INPUTS["symbol"],
            strategy_id=_KEY_INPUTS["strategy_id"],
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10.00"),
        )
        o2 = mgr.create_order(
            symbol=_KEY_INPUTS["symbol"],
            strategy_id=_KEY_INPUTS["strategy_id"],
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10.00"),
        )
        assert o1.idempotency_key == o2.idempotency_key
        assert o1.order_id != o2.order_id  # 本地订单号仍唯一（键与订单号解耦）

    def test_different_batch_yields_different_key(self):
        mgr = OrderManager()
        mgr.begin_signal_batch("batch-A", trade_date=_KEY_INPUTS["trade_date"])
        oa = mgr.create_order(
            symbol="600000",
            strategy_id="STR-TEST-001",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
        )
        mgr.begin_signal_batch("batch-B", trade_date=_KEY_INPUTS["trade_date"])
        ob = mgr.create_order(
            symbol="600000",
            strategy_id="STR-TEST-001",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
        )
        assert oa.idempotency_key != ob.idempotency_key


# ──────────────────────────────────────────────────────────────────────────────
# 验收②：去重状态落库，重启后可读回
# ──────────────────────────────────────────────────────────────────────────────


class TestDurableStorePersistence:
    def test_record_readable_by_new_instance(self, tmp_path):
        db = tmp_path / "idem.db"
        store = SQLiteIdempotencyStore(db_path=db, default_ttl_seconds=0)
        store.start("k-restart")
        store.complete("k-restart", "900001")
        store.close()

        revived = SQLiteIdempotencyStore(db_path=db, default_ttl_seconds=0)
        rec = revived.get("k-restart")
        assert rec is not None
        assert rec.status is IdempotencyStatus.COMPLETED
        assert rec.result == "900001"

    def test_zero_ttl_never_expires_across_restart(self, tmp_path):
        """ttl<=0 = 永不过期（资金安全件：去重记录不得因 TTL 蒸发而放行二次发单）。"""
        db = tmp_path / "idem_noexp.db"
        store = SQLiteIdempotencyStore(db_path=db, default_ttl_seconds=0)
        store.start("k-forever")
        store.complete("k-forever", "900002")
        store.close()

        revived = SQLiteIdempotencyStore(db_path=db, default_ttl_seconds=0)
        assert revived.get("k-forever") is not None
        assert revived.size >= 1

    def test_durable_timestamps_are_wall_clock(self, tmp_path):
        """持久化时间戳必须用墙钟（monotonic 跨进程不可比，会让重启后 TTL 判定失真）。"""
        import time as _time

        db = tmp_path / "idem_wall.db"
        store = SQLiteIdempotencyStore(db_path=db, default_ttl_seconds=0)
        store.start("k-wall")
        store.complete("k-wall", "900003")
        rec = store.get("k-wall")
        # 墙钟 epoch 秒 ≫ monotonic（本机 uptime 秒数）；用 1e9 作为 2001 年后的下界
        assert rec.completed_at > 1_000_000_000
        assert abs(rec.completed_at - _time.time()) < 300


# ──────────────────────────────────────────────────────────────────────────────
# 验收③：下单 → 崩溃 → 重启 → 重放 不二次发单
# ──────────────────────────────────────────────────────────────────────────────


class TestCrashReplayNoDoubleSubmit:
    def test_first_submit_reaches_broker(self, tmp_path, _bypass_constraints):
        """反证锚点：空账本时订单必须真的发出去（证明去重不是"什么都不发"）。"""
        broker = _make_broker(tmp_path / "ledger.db")
        oid = broker.submit_order(_make_order())
        assert oid == "424242"
        assert broker._xttrader.order_stock.call_count == 1

    def test_replay_in_same_process_not_resent(self, tmp_path, _bypass_constraints):
        broker = _make_broker(tmp_path / "ledger.db")
        order = _make_order()
        first = broker.submit_order(order)
        second = broker.submit_order(_make_order())
        assert first == second == "424242"
        assert broker._xttrader.order_stock.call_count == 1

    def test_replay_after_crash_restart_not_resent(self, tmp_path, _bypass_constraints):
        """核心资金安全断言：进程崩溃（实例丢弃）后重启，同信号重放不得二次发单。"""
        db = tmp_path / "ledger_crash.db"

        broker_before_crash = _make_broker(db)
        sent_before = broker_before_crash.submit_order(_make_order())
        assert broker_before_crash._xttrader.order_stock.call_count == 1

        # ── 模拟进程崩溃：丢弃实例（内存态 _idempotency_map 随之消失）──
        del broker_before_crash

        broker_after_restart = _make_broker(db)
        assert broker_after_restart._idempotency_map == {}  # 内存态确已清零
        sent_after = broker_after_restart.submit_order(_make_order())

        assert sent_after == sent_before
        assert broker_after_restart._xttrader.order_stock.call_count == 0  # 未二次发单

    def test_distinct_signal_still_sent_after_restart(self, tmp_path, _bypass_constraints):
        """反向护栏：重启后不同业务语义的订单必须照常发出（去重不得过度拦截）。"""
        db = tmp_path / "ledger_distinct.db"
        b1 = _make_broker(db)
        b1.submit_order(_make_order(idempotency_key="ord-A"))
        del b1

        b2 = _make_broker(db)
        b2._xttrader.order_stock.return_value = 515151
        oid = b2.submit_order(_make_order(idempotency_key="ord-B"))
        assert oid == "515151"
        assert b2._xttrader.order_stock.call_count == 1

    def test_hard_crash_mid_send_fail_closed_on_replay(self, tmp_path, _bypass_constraints):
        """发单途中被硬杀（BaseException，走不到 settle）⇒ 账本留 PROCESSING ⇒ 重放 Fail-Closed。

        资金安全语义：成交与否未知时，宁可漏发一笔等人工对账，绝不冒二次成交风险。
        """
        db = tmp_path / "ledger_hard.db"
        b1 = _make_broker(db)
        b1._xttrader.order_stock.side_effect = KeyboardInterrupt("host killed mid-send")
        with pytest.raises(KeyboardInterrupt):
            b1.submit_order(_make_order(idempotency_key="ord-hard"))
        del b1

        b2 = _make_broker(db)
        with pytest.raises(MiniQmtBrokerError, match="Fail-Closed"):
            b2.submit_order(_make_order(idempotency_key="ord-hard"))
        assert b2._xttrader.order_stock.call_count == 0

    def test_broker_default_store_is_durable_not_memory_only(self, tmp_path):
        """默认账本必须可持久化（不得退回纯内存 dict）——用注入点验证类型契约。"""
        broker = MiniQmtBroker(path="", session_id="idem-default", account_id="8886156677")
        broker.idempotency_db_path = tmp_path / "default_ledger.db"
        store = broker.idempotency_store
        assert isinstance(store, SQLiteIdempotencyStore)
        assert (tmp_path / "default_ledger.db").exists()
