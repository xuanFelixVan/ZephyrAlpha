# [MODULE] tests.ex_core.adapters.test_qmt_file_bridge_idempotency
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_broker; zephyr.shared.infra.idempotency
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] 幂等权威态落库（跨重启去重）；PROCESSING=Fail-Closed 拒重发；FAILED=允许重试；两腿共享同一账本文件名
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=TEST-MOD-L06-001-QMTFB-TEST_QMT_FILE_BRIDGE_IDEMPOTENCY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""QMT File Bridge Broker 幂等账本落库测试（Q7/#ARCH-TRADING-IDEMPOTENCY-001）。

病历：FF-11（R-L3）给 miniqmt 腿落了 SQLite 幂等账本，file-bridge 腿的
``_idempotency_map`` 仍是纯内存——进程重启即失忆，同信号重放=重复合同（量化红线）。
本套件钉死 file-bridge 腿的四条硬验收：

  1. 跨重启去重：新实例（内存 map 为空）凭 SQLite 账本拦截同键重发；
  2. PROCESSING 记录 = Fail-Closed 拒发（上次进程可能死于发单途中，成交未知）；
  3. 写失败 → FAILED（允许重试）+ 内存认领回滚；
  4. 两腿账本文件名单真源（与 miniqmt 常量钉死一致）。

安全边界：零实盘路径；账本与桥目录全部走 tmp_path，禁触生产 data/。
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

import zephyr.ex_core.adapters.miniqmt_broker as miniqmt_mod
import zephyr.ex_core.adapters.qmt_file_bridge_broker as bridge_mod
from zephyr.ex_core.adapters.qmt_file_bridge_broker import (
    QmtFileBridgeBroker,
    QmtFileBridgeError,
)
from zephyr.shared.contracts.order import Order, OrderSide, OrderType
from zephyr.shared.infra.idempotency import (
    IdempotencyStatus,
    SQLiteIdempotencyStore,
)

_KEY = "idem-key-q7-001"


def _make_order(order_id: str = "local-1", key: str = _KEY) -> Order:
    return Order(
        order_id=order_id,
        idempotency_key=key,
        symbol="510300.SH",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("4.50"),
        strategy_id="strat-q7",
    )


def _make_broker(tmp_path: Path, store_db: Path) -> QmtFileBridgeBroker:
    """构造 file-bridge broker：临时桥目录 + 注入 tmp 账本（禁触生产 data/）。"""
    config = QmtFileBridgeBroker.ENV_CONFIG["sim"].copy()
    config["bridge_dir"] = str(tmp_path)
    config["orders_file"] = str(tmp_path / "orders_sim.csv")
    config["ack_file"] = str(tmp_path / "ack_sim.csv")
    config["stock_dir"] = str(tmp_path / "Stock")
    with patch.dict(QmtFileBridgeBroker.ENV_CONFIG, {"sim": config}):
        broker = QmtFileBridgeBroker(env="sim", sync_interval=0.1, http_port=None)
    broker.idempotency_store = SQLiteIdempotencyStore(db_path=store_db, default_ttl_seconds=0)
    broker.connect()
    return broker


def _instruction_lines(tmp_path: Path) -> list[str]:
    f = tmp_path / "orders_sim.csv"
    if not f.exists():
        return []
    return [
        ln
        for ln in f.read_text(encoding="ascii").splitlines()
        if ln.strip() and not ln.startswith("order_id,")  # 排除 connect() 写入的表头
    ]


@pytest.fixture
def store_db(tmp_path):
    return tmp_path / "idem_ledger.db"


@pytest.fixture
def bridge_dir(tmp_path):
    return tmp_path / "bridge"


class TestFileBridgeIdempotencyLedger:
    """Q7 硬验收：file-bridge 幂等权威态落库。"""

    def test_crash_restart_no_duplicate_submit(self, tmp_path, store_db):
        """新实例（内存 map 空）凭账本拦截同键重发——不写第二条指令行。"""
        broker_a = _make_broker(tmp_path, store_db)
        returned = broker_a.submit_order(_make_order("local-1"))
        assert returned == "local-1"
        assert len(_instruction_lines(tmp_path)) == 1
        broker_a.disconnect()

        # 模拟崩溃重启：全新实例、内存 map 必为空、只读同一账本
        broker_b = _make_broker(tmp_path, store_db)
        assert broker_b._idempotency_map == {}
        replay_id = broker_b.submit_order(_make_order("local-2"))
        assert replay_id == "local-1"
        assert len(_instruction_lines(tmp_path)) == 1  # 关键断言：无第二条合同
        broker_b.disconnect()

    def test_processing_record_fail_closed(self, tmp_path, store_db):
        """账本存在 PROCESSING（上进程可能死于发单途中）→ Fail-Closed 拒发。"""
        seed = SQLiteIdempotencyStore(db_path=store_db, default_ttl_seconds=0)
        seed.start(_KEY)
        broker = _make_broker(tmp_path, store_db)
        with pytest.raises(QmtFileBridgeError, match="Fail-Closed"):
            broker.submit_order(_make_order())
        assert _instruction_lines(tmp_path) == []  # 指令不进桥
        broker.disconnect()

    def test_completed_record_hit_returns_existing(self, tmp_path, store_db):
        """账本 COMPLETED → 直接返回既有引用，零新指令。"""
        seed = SQLiteIdempotencyStore(db_path=store_db, default_ttl_seconds=0)
        seed.start(_KEY)
        seed.complete(_KEY, "oid-9")
        broker = _make_broker(tmp_path, store_db)
        assert broker.submit_order(_make_order("local-x")) == "oid-9"
        assert _instruction_lines(tmp_path) == []
        broker.disconnect()

    def test_failed_record_allows_resubmit(self, tmp_path, store_db):
        """账本 FAILED（上次明确未发单）→ 允许重发，成功后落 COMPLETED。"""
        seed = SQLiteIdempotencyStore(db_path=store_db, default_ttl_seconds=0)
        seed.start(_KEY)
        seed.fail(_KEY)
        broker = _make_broker(tmp_path, store_db)
        assert broker.submit_order(_make_order("retry-1")) == "retry-1"
        assert len(_instruction_lines(tmp_path)) == 1
        rec = broker.idempotency_store.get(_KEY)
        assert rec.status is IdempotencyStatus.COMPLETED
        assert rec.result == "retry-1"
        broker.disconnect()

    def test_settle_persists_after_success(self, tmp_path, store_db):
        """成功发单后账本留 COMPLETED(result=本地单号)——重启后可读回。"""
        broker = _make_broker(tmp_path, store_db)
        returned = broker.submit_order(_make_order("local-1"))
        rec = broker.idempotency_store.get(_KEY)
        assert rec is not None
        assert rec.status is IdempotencyStatus.COMPLETED
        assert rec.result == returned
        broker.disconnect()

    def test_write_failure_marks_failed_and_rolls_back(self, tmp_path, store_db):
        """指令写失败 → 账本 FAILED（可重试）+ 内存认领回滚，不假声称。"""
        broker = _make_broker(tmp_path, store_db)

        def _boom(_inst):
            raise OSError("disk full")

        with patch.object(broker, "_append_instruction", side_effect=_boom):
            with pytest.raises(OSError):
                broker.submit_order(_make_order("local-1"))
        rec = broker.idempotency_store.get(_KEY)
        assert rec.status is IdempotencyStatus.FAILED
        assert _KEY not in broker._idempotency_map
        assert _instruction_lines(tmp_path) == []
        broker.disconnect()

        # 修复后同键重试成功
        broker2 = _make_broker(tmp_path, store_db)
        assert broker2.submit_order(_make_order("local-1")) == "local-1"
        assert len(_instruction_lines(tmp_path)) == 1
        broker2.disconnect()

    def test_empty_idempotency_key_rejected(self, tmp_path, store_db):
        """空幂等键=INV-007 对齐拒收（空键进账本=全局污染）。"""
        broker = _make_broker(tmp_path, store_db)
        with pytest.raises(QmtFileBridgeError, match="idempotency_key"):
            broker.submit_order(_make_order(key=""))
        assert _instruction_lines(tmp_path) == []
        broker.disconnect()

    def test_db_name_pinned_with_miniqmt(self):
        """两腿账本同库单真源：文件名常量与 miniqmt 钉死一致（漂移=两本账=去重失效）。"""
        assert bridge_mod._ORDER_IDEMPOTENCY_DB_NAME == miniqmt_mod._ORDER_IDEMPOTENCY_DB_NAME
