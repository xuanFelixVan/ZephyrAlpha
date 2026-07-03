# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] scripts.tests.test_miniqmt_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.miniqmt_broker
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] TTL=task_bound（施工完成后退役）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] task_bound
"""miniqmt_broker.py 验证脚本（TTL=task_bound，施工完成后退役）"""
import importlib.util
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import MagicMock, patch

# 绕开 zephyr.ex_core.adapters.__init__.py 的循环导入，直接按文件加载模块
_spec = importlib.util.spec_from_file_location(
    "zephyr.ex_core.adapters.miniqmt_broker",
    Path(__file__).resolve().parents[2]
    / "src" / "zephyr" / "ex_core" / "adapters" / "miniqmt_broker.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MiniQmtBroker = _mod.MiniQmtBroker
MiniQmtBrokerError = _mod.MiniQmtBrokerError
XTTRADER_ERROR_CODES = _mod.XTTRADER_ERROR_CODES

from zephyr.backtest.core.matching_logic import (
    MatchingConfig,
    MatchingLogic,
    MatchOrderInput,
    OrderBookSnapshot,
)
from zephyr.trading.trading_contracts.execution.order import (
    Order,
    OrderSide,
    OrderType,
)


def make_order(
    side=OrderSide.BUY,
    qty=100,
    symbol="600000.SH",
    order_type=OrderType.LIMIT,
    limit_price=Decimal("10.50"),
    idempotency_key="test-001",
) -> Order:
    return Order(
        idempotency_key=idempotency_key,
        order_id=idempotency_key,
        order_type=order_type,
        quantity=Decimal(str(qty)),
        side=side,
        strategy_id="test_strategy",
        symbol=symbol,
        limit_price=limit_price,
    )


def test_idempotency():
    """测试幂等去重"""
    print("=== Test 1: 幂等去重 ===")
    broker = MiniQmtBroker(path="mock", session_id="test")

    # Mock connect 和 submit
    broker._connected = True
    broker._xttrader = MagicMock()
    broker._xttrader.start.return_value = 0
    broker._xttrader.order_stock.return_value = 0

    order1 = make_order(idempotency_key="idem-001")
    broker_order_id1 = broker.submit_order(order1)
    print(f"  第一次下单: broker_order_id={broker_order_id1}")

    # 同 idempotency_key 再次下单 → 应返回相同 broker_order_id
    order2 = make_order(idempotency_key="idem-001")
    broker_order_id2 = broker.submit_order(order2)
    print(f"  重复下单: broker_order_id={broker_order_id2}")
    assert broker_order_id1 == broker_order_id2, "幂等去重应返回相同 order_id"
    print("  PASS: 幂等去重")


def test_a_share_constraints():
    """测试A股约束校验"""
    print()
    print("=== Test 2: A股约束校验 ===")
    broker = MiniQmtBroker(path="mock", session_id="test")
    broker._connected = True
    broker._xttrader = MagicMock()

    # 数量不合法: < 100股
    try:
        broker.submit_order(make_order(qty=50, idempotency_key="qty-001"))
        print("  FAIL: 50股应被拒绝")
    except MiniQmtBrokerError as e:
        assert e.error_code == 52
        print(f"  PASS: 50股被拒绝 (code=52)")

    # 数量不合法: 非100整数倍
    try:
        broker.submit_order(make_order(qty=150, idempotency_key="qty-002"))
        print("  FAIL: 150股应被拒绝")
    except MiniQmtBrokerError as e:
        assert e.error_code == 52
        print(f"  PASS: 150股被拒绝 (code=52)")

    # 缺少 idempotency_key
    try:
        order = make_order()
        order.idempotency_key = ""
        broker.submit_order(order)
        print("  FAIL: 空 idempotency_key 应被拒绝")
    except MiniQmtBrokerError as e:
        print(f"  PASS: 空 idempotency_key 被拒绝")


def test_t_plus_1():
    """测试T+1锁定"""
    print()
    print("=== Test 3: T+1锁定 ===")
    broker = MiniQmtBroker(path="mock", session_id="test")
    broker._connected = True
    broker._xttrader = MagicMock()
    broker._xttrader.start.return_value = 0
    broker._xttrader.order_stock.return_value = 0

    # 买入
    buy_order = make_order(side=OrderSide.BUY, idempotency_key="t1-buy-001")
    broker.submit_order(buy_order)
    print(f"  买入成功: {buy_order.symbol}")

    # 同日卖出 → T+1锁定
    try:
        sell_order = make_order(side=OrderSide.SELL, idempotency_key="t1-sell-001")
        broker.submit_order(sell_order)
        print("  FAIL: 同日卖出应被T+1锁定")
    except MiniQmtBrokerError as e:
        assert e.error_code == -2
        print(f"  PASS: 同日卖出被T+1锁定 (code=-2)")


def test_error_code_mapping():
    """测试错误码映射"""
    print()
    print("=== Test 4: 错误码映射 ===")
    broker = MiniQmtBroker(path="mock", session_id="test")
    broker._connected = True
    broker._xttrader = MagicMock()
    broker._xttrader.start.return_value = 0

    # 模拟涨停 (code=50)
    broker._xttrader.order_stock.return_value = 50
    try:
        broker.submit_order(make_order(idempotency_key="err-001"))
        print("  FAIL: 涨停应被拒绝")
    except MiniQmtBrokerError as e:
        assert e.error_code == 50
        print(f"  PASS: 涨停被拒绝 (code=50, msg={XTTRADER_ERROR_CODES[50]})")

    # 模拟资金不足 (code=54)
    broker._xttrader.order_stock.return_value = 54
    try:
        broker.submit_order(make_order(idempotency_key="err-002"))
        print("  FAIL: 资金不足应被拒绝")
    except MiniQmtBrokerError as e:
        assert e.error_code == 54
        print(f"  PASS: 资金不足被拒绝 (code=54, msg={XTTRADER_ERROR_CODES[54]})")


def test_pre_trade_simulate():
    """测试回测=实盘一致性：预成交模拟"""
    print()
    print("=== Test 5: 预成交模拟（回测=实盘一致性）===")
    logic = MatchingLogic(MatchingConfig())
    broker = MiniQmtBroker(
        path="mock", session_id="test", matching_logic=logic,
    )

    # 构造5档盘口
    ob = OrderBookSnapshot(
        symbol="600000.SH",
        ask_price=(Decimal("10.50"), Decimal("10.51"), Decimal("10.52"), Decimal("10.53"), Decimal("10.54")),
        bid_price=(Decimal("10.49"), Decimal("10.48"), Decimal("10.47"), Decimal("10.46"), Decimal("10.45")),
        ask_vol=(Decimal("1000"), Decimal("2000"), Decimal("3000"), Decimal("4000"), Decimal("5000")),
        bid_vol=(Decimal("1000"), Decimal("2000"), Decimal("3000"), Decimal("4000"), Decimal("5000")),
        last_price=Decimal("10.50"),
    )

    # 市价买单
    order = make_order(
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        limit_price=None,
        idempotency_key="sim-001",
    )
    fill = broker.pre_trade_simulate(order, ob)
    print(f"  市价买单预成交: filled={fill.filled} price={fill.price} commission={fill.commission}")
    assert fill.filled
    assert fill.price >= Decimal("10.50")  # 含滑点

    # 验证 broker.matching_logic 就是传入的 logic（回测=实盘一致性）
    assert broker.matching_logic is logic
    print("  PASS: 预成交模拟 + MatchingLogic 共享")


def test_thread_safety():
    """测试线程安全（Lock）"""
    print()
    print("=== Test 6: 线程安全 ===")
    broker = MiniQmtBroker(path="mock", session_id="test")
    assert hasattr(broker, "_lock"), "broker 必须有 _lock"
    import threading
    assert isinstance(broker._lock, type(threading.Lock())), "_lock 必须是 threading.Lock 实例"
    print("  PASS: 线程安全 Lock 存在")


def main():
    test_idempotency()
    test_a_share_constraints()
    test_t_plus_1()
    test_error_code_mapping()
    test_pre_trade_simulate()
    test_thread_safety()
    print()
    print("ALL OK")


if __name__ == "__main__":
    main()
