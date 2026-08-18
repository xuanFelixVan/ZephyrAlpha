# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.test_miniqmt_broker
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""miniqmt_broker 正式测试（原 scripts/tests/ 临时验证脚本转正）

适配新版 xtquant 250807.1.2 API（#ARCH-XTQUANT-API-COMPAT-001）：
  - order_stock 返回 order_id（正整数=成功，-1=失败），非旧版错误码
  - account 参数传 StockAccount 对象，非 str session_id
  - start() 在 connect() 时调一次，submit_order 不再调 start()

2026-08-17：历史循环导入已消除，改为包路径直接导入（原 importlib 按文件
加载 workaround 拆除——绕过包 __init__ 会让模块脱离包上下文，掩盖真实问题）。
"""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from zephyr.backtest.core.matching_logic import (
    MatchingConfig,
    MatchingLogic,
    MatchOrderInput,
    OrderBookSnapshot,
)
from zephyr.ex_core.adapters.miniqmt_broker import (
    XTTRADER_ERROR_CODES,
    MiniQmtBroker,
    MiniQmtBrokerError,
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


def make_broker(account_id="test_account"):
    """构造测试用 broker：绕过 connect()，直接 mock xttrader + StockAccount。

    新版 xtquant 适配后：
      - account_id 构造 StockAccount，submit_order 用 self._account 下单
      - order_stock 返回 order_id（正整数=成功）
    """
    broker = MiniQmtBroker(path="mock", session_id="test", account_id=account_id)
    broker.connected = True
    broker.xttrader = MagicMock()
    broker._account = MagicMock(name="StockAccount")  # 模拟 StockAccount 对象
    broker.xttrader.order_stock.return_value = 1001  # 正整数 order_id = 成功
    return broker


def test_idempotency():
    """测试幂等去重"""
    broker = make_broker()

    order1 = make_order(idempotency_key="idem-001")
    broker_order_id1 = broker.submit_order(order1)

    order2 = make_order(idempotency_key="idem-001")
    broker_order_id2 = broker.submit_order(order2)
    assert broker_order_id1 == broker_order_id2, "幂等去重应返回相同 order_id"
    assert broker_order_id1 == "1001", "broker_order_id 应为券商返回的 order_id"


def test_a_share_constraints():
    """测试A股约束校验"""
    broker = make_broker()

    try:
        broker.submit_order(make_order(qty=50, idempotency_key="qty-001"))
        assert False, "50股应被拒绝"
    except MiniQmtBrokerError as e:
        assert e.error_code == 52

    try:
        broker.submit_order(make_order(qty=150, idempotency_key="qty-002"))
        assert False, "150股应被拒绝"
    except MiniQmtBrokerError as e:
        assert e.error_code == 52

    try:
        order = make_order()
        order.idempotency_key = ""
        broker.submit_order(order)
        assert False, "空 idempotency_key 应被拒绝"
    except MiniQmtBrokerError:
        pass


@pytest.mark.xfail(reason="broker 涨停校验需 prev_close 数据，mock 不完整；T+1 逻辑依赖持仓状态，需补充 mock")
def test_t_plus_1():
    """测试T+1锁定"""
    broker = make_broker()

    buy_order = make_order(side=OrderSide.BUY, idempotency_key="t1-buy-001")
    broker.submit_order(buy_order)

    try:
        sell_order = make_order(side=OrderSide.SELL, idempotency_key="t1-sell-001")
        broker.submit_order(sell_order)
        assert False, "同日卖出应被T+1锁定"
    except MiniQmtBrokerError as e:
        assert e.error_code == -2


def test_order_stock_failure():
    """测试下单失败：order_stock 返回 -1（新版 xtquant 失败码）。

    新版 xtquant 250807.1.2：order_stock 返回 order_id（正整数=成功，-1=失败），
    不再返回 50/54 等业务错误码（那些通过 on_order_error 回调推送）。
    """
    broker = make_broker()
    broker.xttrader.order_stock.return_value = -1

    try:
        broker.submit_order(make_order(idempotency_key="err-001"))
        assert False, "order_stock 返回 -1 应被拒绝"
    except MiniQmtBrokerError as e:
        assert e.error_code == -1


def test_account_passed_to_xttrader():
    """测试 StockAccount 对象传给 order_stock（非 str session_id）。

    新版 xtquant 适配核心（#ARCH-XTQUANT-API-COMPAT-001）：
    order_stock 第一个参数必须是 StockAccount 对象，旧版传 str 已废弃。
    """
    broker = make_broker()

    broker.submit_order(make_order(idempotency_key="acc-001"))

    # 断言 order_stock 第一个位置参数是 _account（StockAccount 对象，非 str）
    broker.xttrader.order_stock.assert_called_once()
    call_args = broker.xttrader.order_stock.call_args
    first_arg = call_args.args[0] if call_args.args else None
    assert first_arg is broker._account, "order_stock 应传 StockAccount 对象（非 str）"


def test_order_side_mapping():
    """测试买卖方向映射（23=买/24=卖，非旧版订单类型 5/11）。

    新版 xtquant order_type 是买卖方向，price_type 区分限价/市价。
    """
    broker = make_broker()

    # 买单 → order_type=23
    broker.submit_order(make_order(side=OrderSide.BUY, idempotency_key="buy-001"))
    buy_call = broker.xttrader.order_stock.call_args
    assert buy_call.args[2] == 23, "买单 order_type 应为 23"

    # 卖单 → order_type=24（需先重置 mock + 清幂等缓存）
    broker.xttrader.order_stock.reset_mock()
    broker.xttrader.order_stock.return_value = 1002
    broker._idempotency_map.clear()
    broker.submit_order(make_order(side=OrderSide.SELL, idempotency_key="sell-001"))
    sell_call = broker.xttrader.order_stock.call_args
    assert sell_call.args[2] == 24, "卖单 order_type 应为 24"


def test_pre_trade_simulate():
    """测试回测=实盘一致性：预成交模拟"""
    logic = MatchingLogic(MatchingConfig())
    broker = MiniQmtBroker(
        path="mock",
        session_id="test",
        account_id="test_account",
        matching_logic=logic,
    )

    ob = OrderBookSnapshot(
        symbol="600000.SH",
        ask_price=(Decimal("10.50"), Decimal("10.51"), Decimal("10.52"), Decimal("10.53"), Decimal("10.54")),
        bid_price=(Decimal("10.49"), Decimal("10.48"), Decimal("10.47"), Decimal("10.46"), Decimal("10.45")),
        ask_vol=(Decimal("1000"), Decimal("2000"), Decimal("3000"), Decimal("4000"), Decimal("5000")),
        bid_vol=(Decimal("1000"), Decimal("2000"), Decimal("3000"), Decimal("4000"), Decimal("5000")),
        last_price=Decimal("10.50"),
    )

    order = make_order(
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        limit_price=None,
        idempotency_key="sim-001",
    )
    fill = broker.pre_trade_simulate(order, ob)
    assert fill.filled
    assert fill.price >= Decimal("10.50")
    assert broker.matching_logic is logic


def test_thread_safety():
    """测试线程安全（Lock）"""
    broker = MiniQmtBroker(path="mock", session_id="test", account_id="test_account")
    assert hasattr(broker, "_lock"), "broker 必须有 _lock"
    import threading

    assert isinstance(broker.lock, type(threading.Lock())), "_lock 必须是 threading.Lock 实例"


def make_order_book(symbol="600000.SH", ask1=Decimal("10.50"), bid1=Decimal("10.49")):
    """构造5档盘口快照（预校验/价格笼子测试用）。"""
    return OrderBookSnapshot(
        symbol=symbol,
        ask_price=tuple(ask1 + Decimal("0.01") * i for i in range(5)),
        bid_price=tuple(bid1 - Decimal("0.01") * i for i in range(5)),
        ask_vol=(Decimal("1000"),) * 5,
        bid_vol=(Decimal("1000"),) * 5,
        last_price=Decimal("10.50"),
    )


def test_board_differentiated_quantity():
    """板块差异化整手校验（board_lot 真源，§决策⑰）。

    科创板（688）：min_unit=200、1股递增——100股申报应拒绝（废单级），
    201股合法应放行；主板 100 股整数倍规则不变。
    """
    broker = make_broker()

    # 科创板 100 股（非法：低于 200 起买量）→ 拒绝
    try:
        broker.submit_order(make_order(qty=100, symbol="688001.SH", idempotency_key="star-100"))
        assert False, "科创板 100 股应被拒绝（低于 200 股起买量）"
    except MiniQmtBrokerError as e:
        assert e.error_code == 52

    # 科创板 201 股（合法：200 起 +1 股递增）→ 放行
    broker.xttrader.order_stock.return_value = 2001
    broker_id = broker.submit_order(make_order(qty=201, symbol="688001.SH", idempotency_key="star-201"))
    assert broker_id == "2001"

    # 创业板 100 股（合法：100 整数倍）→ 放行
    broker.xttrader.order_stock.return_value = 2002
    broker_id = broker.submit_order(make_order(qty=100, symbol="300750.SZ", idempotency_key="gem-100"))
    assert broker_id == "2002"

    # 北交所 150 股（非法：100 递增）→ 拒绝
    try:
        broker.submit_order(make_order(qty=150, symbol="830799.BJ", idempotency_key="bse-150"))
        assert False, "北交所 150 股应被拒绝（须 100 股递增）"
    except MiniQmtBrokerError as e:
        assert e.error_code == 52


def test_price_cage_clamp_in_submit():
    """价格笼子接入下单链：限价单超笼子上限 → 夹到边界提交（不废单）。"""
    broker = make_broker()
    ob = make_order_book()  # ask1=10.50
    # 买入 limit 10.80：超笼子（主板上限=max(10.50*1.02, 10.50+0.10)=10.71）
    # 但低于涨停价 11.00（prev_close=10.00 × 1.10），不触发涨跌停拒单
    order = make_order(qty=100, limit_price=Decimal("10.80"), idempotency_key="cage-001")
    broker.submit_order(order, order_book=ob, prev_close=Decimal("10.00"))
    assert order.limit_price == Decimal("10.71"), f"超笼子买入价应夹到 10.71，实际 {order.limit_price}"
    # 夹边后的价格必须真实发给 xttrader
    call_args = broker.xttrader.order_stock.call_args
    assert call_args.args[5] == 10.71  # price 位置参数（float）


def test_price_cage_in_cage_no_change():
    """价格笼子内限价单：价格不被改动。"""
    broker = make_broker()
    ob = make_order_book()
    order = make_order(qty=100, limit_price=Decimal("10.50"), idempotency_key="cage-002")
    broker.submit_order(order, order_book=ob, prev_close=Decimal("10.00"))
    assert order.limit_price == Decimal("10.50")


def test_query_order_int_order_id_match():
    """query_order 对 int 型 xt order_id 也能命中缓存（类型归一）。"""
    broker = make_broker()
    broker_order_id = broker.submit_order(make_order(idempotency_key="q-001"))
    assert broker_order_id == "1001"

    xt_order = MagicMock()
    xt_order.order_id = 1001  # int 型（新版 xtquant）
    xt_order.order_status = 52  # FILLED
    xt_order.traded_volume = 100
    xt_order.traded_price = 10.5
    broker.xttrader.query_stock_orders.return_value = [xt_order]

    found = broker.query_order("1001")
    assert found is not None, "int order_id 应能命中（str 归一比较）"
    assert found.status.name == "FILLED"
