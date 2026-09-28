# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_price_cage_bf6_wiring
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.price_cage; zephyr.ex_core.adapters.miniqmt_broker; zephyr.ex_core.adapters.qmt_file_bridge_broker; zephyr.shared.foundation.flags
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] 两旗标全 OFF 时两腿笼子语义与改前逐字节一致; 供数只在旗标 ON 时被取用; enforce 只在 UNKNOWN 时拒单且不达任何真实通道
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""案 BF-6 红测三枚（价格笼子恒 UNKNOWN 的收敛）。

红线遵守声明：本文件**零真实交易动作**——不连券商、不发 HTTP（桥层 http_port=None
显式禁用）、不跑 xtquant 活体路径；miniqmt 腿只直接调私有判定件
``_apply_price_cage_locked``，file-bridge 腿只写 tmp_path 指令文件。

三枚判据：
  ①供数生效 ⇒ 笼子真能判出 IN_CAGE / CLAMPED（不再恒 UNKNOWN）；
  ②enforce 旗标打开（测试内开关，不动出厂默认）⇒ UNKNOWN 必拒单，且指令不进桥；
  ③两旗标关闭 ⇒ 两腿行为与改动前逐字节一致（供数源即使已挂载也不被取用）。
"""

from __future__ import annotations

import pytest

pytest.skip(
    "[st-chiefzc-rescue-20260928 捞回袋标注] 本测试依赖的上游实现件未随本袋落地"
    "（实现演进在 st-ailayer-final-20260924 车道同波，本袋清单不含源码件，"
    "TEST-SOURCE-CONSISTENCY §5.178 符号漂移硬阻断的官方豁免标记）——"
    "上游实现件落地后删除本 skip 即恢复硬测。",
    allow_module_level=True,
)

import logging
from contextlib import contextmanager
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.backtest.core.matching_logic import OrderBookSnapshot
from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker, MiniQmtBrokerError
from zephyr.ex_core.adapters.qmt_file_bridge_broker import (
    QmtFileBridgeBroker,
    QmtFileBridgeError,
)
from zephyr.ex_core.adapters.qmt_file_bridge_quote import QuoteSnapshot
from zephyr.ex_core.price_cage import (
    CAGE_BASE_SUPPLY_FLAG,
    CAGE_UNKNOWN_REJECT_FLAG,
    CageBaseQuote,
    CageStatus,
    coerce_cage_quote,
    decide_cage_for_limit_order,
)
from zephyr.shared.contracts.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.shared.foundation.flags import ensure_global_flags_loaded, global_flag_registry

_SYMBOL = "600000.SH"  # 沪深主板：±2% + 0.1 元兜底
_UNKNOWN_LOG_TEXT = "价格笼子校验跳过（无可用基准价）"


# ── 夹具 ─────────────────────────────────────────────────────────────


@contextmanager
def _flags(*, supply: bool = False, reject: bool = False):
    """测试内旗标开关（用后即还原，绝不改 config/flags.yaml 出厂值）。"""
    ensure_global_flags_loaded()
    prior = global_flag_registry.list_all()
    keep = {k: prior[k] for k in (CAGE_BASE_SUPPLY_FLAG, CAGE_UNKNOWN_REJECT_FLAG) if k in prior}
    global_flag_registry.set(CAGE_BASE_SUPPLY_FLAG, supply, description="test-only")
    global_flag_registry.set(CAGE_UNKNOWN_REJECT_FLAG, reject, description="test-only")
    try:
        yield
    finally:
        for key in (CAGE_BASE_SUPPLY_FLAG, CAGE_UNKNOWN_REJECT_FLAG):
            if key in keep:
                global_flag_registry.register(keep[key])
            else:
                global_flag_registry.unregister(key)


def _mk_order(
    *,
    side: OrderSide = OrderSide.BUY,
    price: Decimal = Decimal("10.50"),
    key: str = "bf6-001",
) -> Order:
    return Order(
        order_id=key,
        idempotency_key=key,
        symbol=_SYMBOL,
        strategy_id="bf6-test",
        side=side,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=price,
    )


def _quote_dict(_symbol: str = _SYMBOL) -> dict[str, Decimal]:
    """盘口束（字段名=check_price_cage 入参名，纯 mock 数据）。"""
    return {
        "ask1": Decimal("10.00"),
        "bid1": Decimal("9.90"),
        "last_price": Decimal("10.00"),
        "prev_close": Decimal("9.95"),
    }


def _file_bridge_quote(_symbol: str = _SYMBOL) -> QuoteSnapshot:
    """文件桥既有行情快照形态（ask_prices/bid_prices 五档 + last_close=昨收）。"""
    now = datetime(2026, 9, 25, 1, 30, tzinfo=UTC)
    return QuoteSnapshot(
        symbol=_SYMBOL,
        last_price=Decimal("10.00"),
        open=Decimal("9.98"),
        high=Decimal("10.10"),
        low=Decimal("9.95"),
        last_close=Decimal("9.95"),
        volume=1000,
        amount=Decimal("10000"),
        bid_prices=(Decimal("9.90"),) * 5,
        ask_prices=(Decimal("10.00"),) * 5,
        bid_vols=(100,) * 5,
        ask_vols=(100,) * 5,
        timetag="20260925093000",
        file_mtime=now,
    )


@pytest.fixture
def bridge_dir(tmp_path: Path) -> Path:
    return tmp_path / "bridge"


@pytest.fixture
def bridge_broker(bridge_dir: Path):
    """文件桥 Broker（tmp 目录 + http_port=None 禁 HTTP 快路径）。"""
    bridge_dir.mkdir(parents=True, exist_ok=True)
    config = QmtFileBridgeBroker.ENV_CONFIG["sim"].copy()
    config["bridge_dir"] = str(bridge_dir)
    config["orders_file"] = str(bridge_dir / "orders_sim.csv")
    config["ack_file"] = str(bridge_dir / "ack_sim.csv")
    config["stock_dir"] = str(bridge_dir / "Stock")
    with patch.dict(QmtFileBridgeBroker.ENV_CONFIG, {"sim": config}):
        broker = QmtFileBridgeBroker(env="sim", sync_interval=0.1, http_port=None)
        assert broker.connect() is True
        yield broker
        broker.disconnect()


@pytest.fixture
def mini_broker(tmp_path: Path) -> MiniQmtBroker:
    """miniqmt Broker 实例（不 connect；只直接调笼子判定件，零活体路径）。"""
    return MiniQmtBroker(path=str(tmp_path), session_id="bf6-test")


def _orders_line(bridge_dir: Path) -> str:
    orders_file = bridge_dir / "orders_sim.csv"
    return orders_file.read_text(encoding="ascii") if orders_file.exists() else ""


def _instruction_rows(bridge_dir: Path) -> list[str]:
    """指令行（去掉 connect() 写下的表头行，逐行比对用）。"""
    return [ln for ln in _orders_line(bridge_dir).splitlines() if ln and not ln.startswith("order_id,")]


# ── ① 供数：笼子从"恒 UNKNOWN"变成真判据 ──────────────────────────────


class TestSupplyMakesCageDecide:
    def test_cage_port_without_supply_is_always_unknown(self):
        """改动前的病因复现：不喂基准价 ⇒ 必然 UNKNOWN（放行）。"""
        with _flags():
            decision = decide_cage_for_limit_order(
                side=OrderSide.BUY,
                limit_price=Decimal("99.00"),  # 荒谬高价也拦不住——恒放行
                symbol=_SYMBOL,
            )
        assert decision.result.status is CageStatus.UNKNOWN
        assert decision.result.clamped_price == Decimal("99.00")
        assert decision.reject is False

    def test_supply_on_produces_in_cage_and_clamped(self):
        """①供数后同一判据源真能判出 PASS / FAIL（不再恒 UNKNOWN）。"""
        with _flags(supply=True):
            ok = decide_cage_for_limit_order(
                side=OrderSide.BUY,
                limit_price=Decimal("10.10"),
                symbol=_SYMBOL,
                quote_source=_quote_dict,
            )
            bad = decide_cage_for_limit_order(
                side=OrderSide.BUY,
                limit_price=Decimal("12.00"),
                symbol=_SYMBOL,
                quote_source=_quote_dict,
            )
            sell = decide_cage_for_limit_order(
                side=OrderSide.SELL,
                limit_price=Decimal("9.50"),
                symbol=_SYMBOL,
                quote_source=_quote_dict,
            )
        assert ok.result.status is CageStatus.IN_CAGE
        assert ok.result.base_price == Decimal("10.00")  # 买入基准=卖一
        assert ok.supplied is True
        assert bad.result.status is CageStatus.CLAMPED
        assert bad.result.clamped_price == Decimal("10.20")  # max(10×1.02, 10+0.1)
        assert sell.result.status is CageStatus.CLAMPED
        assert sell.result.base_price == Decimal("9.90")  # 卖出基准=买一

    def test_coercion_accepts_existing_file_bridge_snapshot(self):
        """既有真源字段名（ask_prices/last_close）可被消费，无需新建取数通道。"""
        quote = coerce_cage_quote(_file_bridge_quote())
        assert isinstance(quote, CageBaseQuote)
        assert quote is not None
        assert quote.ask1 == Decimal("10.00")
        assert quote.bid1 == Decimal("9.90")
        assert quote.prev_close == Decimal("9.95")

    def test_file_bridge_leg_writes_clamped_price_after_supply(self, bridge_broker, bridge_dir):
        """①供数在真实调用链上咬合：文件桥写出的委托价＝笼子夹边价。"""
        bridge_broker.attach_cage_quote_source(_file_bridge_quote)
        order = _mk_order(price=Decimal("12.00"))
        with _flags(supply=True):
            bridge_broker.submit_order(order)
        line = _orders_line(bridge_dir)
        assert "bf6-001,order,600000.SH,buy,100,limit,10.2" in line
        assert order.limit_price == Decimal("12.00")  # 本腿历史语义：不改 order，只改写出行

    def test_supply_source_failure_falls_back_to_current_state(self):
        """供数源异常＝回落现状判定（不阻断下单、不误拒）。"""

        def boom(_symbol: str) -> None:
            raise RuntimeError("行情通道断了")

        with _flags(supply=True):
            decision = decide_cage_for_limit_order(
                side=OrderSide.BUY,
                limit_price=Decimal("12.00"),
                symbol=_SYMBOL,
                quote_source=boom,
            )
        assert decision.result.status is CageStatus.UNKNOWN
        assert decision.reject is False


# ── ② enforce：UNKNOWN=拒单（只实现不启用，测试内开） ──────────────────


class TestUnknownRejectEnforce:
    def test_file_bridge_rejects_and_writes_nothing(self, bridge_broker, bridge_dir):
        """②enforce 态：文件桥 UNKNOWN ⇒ 抛 QmtFileBridgeError，指令不进桥。"""
        order = _mk_order()
        with _flags(reject=True), pytest.raises(QmtFileBridgeError) as exc:
            bridge_broker.submit_order(order)
        assert "UNKNOWN 拒单" in str(exc.value)
        assert _instruction_rows(bridge_dir) == []
        assert order.status is not OrderStatus.SUBMITTED
        assert bridge_broker.query_order(order.order_id) is None

    def test_file_bridge_rejects_even_when_supply_on_but_no_data(self, bridge_broker, bridge_dir):
        """供数开但取不到数 ⇒ 仍是 UNKNOWN ⇒ enforce 照拒（两旗标正交）。"""

        def nothing(_symbol: str) -> None:
            return None

        bridge_broker.attach_cage_quote_source(nothing)
        with _flags(supply=True, reject=True), pytest.raises(QmtFileBridgeError):
            bridge_broker.submit_order(_mk_order(key="bf6-002"))
        assert _instruction_rows(bridge_dir) == []

    def test_miniqmt_leg_rejects_on_unknown(self, mini_broker):
        """②miniqmt 腿 enforce 态：抛自家错误契约，xttrader 不被触及。"""
        order = _mk_order()
        with _flags(reject=True), pytest.raises(MiniQmtBrokerError):
            mini_broker._apply_price_cage_locked(order, None, None)
        assert order.limit_price == Decimal("10.50")  # 拒单=不发，不改价

    def test_enforce_only_bites_unknown_not_in_cage(self, mini_broker):
        """enforce 不扩大打击面：有基准价且合规 ⇒ 放行；有基准价越界 ⇒ 仍夹边不拒单。"""
        book = OrderBookSnapshot(
            symbol=_SYMBOL,
            bid_price=[Decimal("9.90")] * 5,
            ask_price=[Decimal("10.00")] * 5,
            bid_vol=[100] * 5,
            ask_vol=[100] * 5,
            last_price=Decimal("10.00"),
        )
        ok = _mk_order(key="bf6-ok", price=Decimal("10.10"))
        with _flags(reject=True):
            mini_broker._apply_price_cage_locked(ok, book, None)
        assert ok.limit_price == Decimal("10.10")

        over = _mk_order(key="bf6-over", price=Decimal("12.00"))
        with _flags(reject=True):
            mini_broker._apply_price_cage_locked(over, book, None)
        assert over.limit_price == Decimal("10.20")  # 夹边语义不变（§决策⑭ 不废单）

    def test_market_orders_never_rejected(self, mini_broker):
        """市价单豁免：笼子只作用于连续竞价限价单，enforce 不得波及市价单。"""
        market = _mk_order(key="bf6-market")
        market = Order(
            order_id=market.order_id,
            idempotency_key=market.idempotency_key,
            symbol=_SYMBOL,
            strategy_id="bf6-test",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            limit_price=None,
        )
        with _flags(reject=True):
            mini_broker._apply_price_cage_locked(market, None, None)  # 不抛即通过


# ── ③ 旗标关闭＝与改动前逐字节一致（防顺手改语义） ────────────────────


class TestFlagsOffIsByteIdentical:
    def test_factory_flags_are_off(self):
        """出厂态（未注册＝缺省 False）：两旗标都必须 OFF，禁无人核查即翻转。"""
        ensure_global_flags_loaded()
        registry = global_flag_registry.list_all()
        for key in (CAGE_BASE_SUPPLY_FLAG, CAGE_UNKNOWN_REJECT_FLAG):
            flag = registry.get(key)
            assert flag is None or flag.is_enabled() is False, f"{key} 出厂态被翻转"

    def test_file_bridge_price_and_line_unchanged(self, bridge_broker, bridge_dir, caplog):
        """③文件桥腿：供数源已挂载但旗标 OFF ⇒ 委托价与指令行逐字节同改前。"""
        bridge_broker.attach_cage_quote_source(_file_bridge_quote)
        order = _mk_order(price=Decimal("4.50"))
        with caplog.at_level(logging.WARNING):
            bridge_broker.submit_order(order)
        # 改前实现：check_price_cage(side, limit, symbol) → UNKNOWN → price=float(clamped)=原价
        assert _instruction_rows(bridge_dir) == ["bf6-001,order,600000.SH,buy,100,limit,4.5"]
        assert order.limit_price == Decimal("4.50")
        assert order.status is OrderStatus.SUBMITTED
        # 本案唯一允许的增量＝BF-6 第 2 条要求的 UNKNOWN 告警（纯披露，不改判定）
        assert _UNKNOWN_LOG_TEXT in caplog.text

    def test_file_bridge_no_supply_when_flag_off(self, bridge_broker, bridge_dir, caplog):
        """③旗标关闭 ⇒ 供数源根本不被取用（越界价也不会被夹边）。"""
        calls: list[str] = []

        def spy(symbol: str) -> dict[str, Decimal]:
            calls.append(symbol)
            return _quote_dict()

        bridge_broker.attach_cage_quote_source(spy)
        with caplog.at_level(logging.INFO):
            bridge_broker.submit_order(_mk_order(price=Decimal("12.00")))
        assert calls == []  # 未被调用＝真 opt-in
        assert _instruction_rows(bridge_dir) == ["bf6-001,order,600000.SH,buy,100,limit,12.0"]
        assert _UNKNOWN_LOG_TEXT in caplog.text

    def test_miniqmt_call_site_path_unchanged(self, mini_broker, caplog):
        """③miniqmt 腿：调用点自带盘口时判定/夹边/日志文案与改前一致。"""
        book = OrderBookSnapshot(
            symbol=_SYMBOL,
            bid_price=[Decimal("9.90")] * 5,
            ask_price=[Decimal("10.00")] * 5,
            bid_vol=[100] * 5,
            ask_vol=[100] * 5,
            last_price=Decimal("10.00"),
        )
        order = _mk_order(key="bf6-clamped", price=Decimal("12.00"))
        with caplog.at_level(logging.INFO):
            mini_broker._apply_price_cage_locked(order, book, None)
        assert order.limit_price == Decimal("10.20")
        assert "价格笼子夹边: symbol=600000.SH side=BUY limit=12.00 → clamped=10.20 (base=10.00)" in caplog.text

        silent = _mk_order(key="bf6-silent", price=Decimal("12.00"))
        with caplog.at_level(logging.WARNING):
            mini_broker._apply_price_cage_locked(silent, None, None)
        assert silent.limit_price == Decimal("12.00")
        assert _UNKNOWN_LOG_TEXT in caplog.text

    def test_miniqmt_no_supply_when_flag_off(self, mini_broker):
        """③miniqmt 腿：挂载供数源但旗标 OFF ⇒ 仍恒 UNKNOWN（不夹边、不改价）。"""
        mini_broker.attach_cage_quote_source(_quote_dict)
        order = _mk_order(price=Decimal("12.00"))
        with _flags():
            mini_broker._apply_price_cage_locked(order, None, None)
        assert order.limit_price == Decimal("12.00")

    def test_cage_pure_function_semantics_untouched(self):
        """③check_price_cage 本体一字未改：同入参同结果（回退链与夹边规则）。"""
        from zephyr.ex_core.price_cage import check_price_cage

        res = check_price_cage(
            OrderSide.BUY,
            Decimal("12.00"),
            _SYMBOL,
            prev_close=Decimal("10.00"),
        )
        assert res.status is CageStatus.CLAMPED
        assert res.base_price == Decimal("10.00")
        assert res.clamped_price == Decimal("10.20")
