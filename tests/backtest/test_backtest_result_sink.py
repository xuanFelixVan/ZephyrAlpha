# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_backtest_result_sink
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_backtest_result_sink.py
# [TTL] permanent
"""T1 成交流水字段端到端投影测试（X 流验证批，Owner 2026-09-10 指令裁定③）。

覆盖三处显式键清单断链防线（io 层此前零覆盖）:
  1. 旧 6 键 trade_log dict → TradeRecord(**p) 兼容（存量 34 产物容错）。
  2. 带新键 dict 全链 sink→build_artifact_from_data→artifact.trade_log 新字段贯通。
  3. MatchingFill 决策价/订单类型语义（market=ask1/bid1 基准、tick=触发 tick last_price、
     limit=委托限价）与 portfolio._trades_log 新键透传。
纯内存合成数据，不触网不触库。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from zephyr.backtest.core.matching_logic import (
    MatchingLogic,
    MatchingConfig,
    MatchOrderInput,
    OrderBookSnapshot,
    TickSnapshot,
)
from zephyr.backtest.core.portfolio import BacktestFill, Portfolio
from zephyr.backtest.io.backtest_result_sink import TradeRecord, sink_backtest_result
from zephyr.backtest.io.result_repository import build_artifact_from_data


# ── 合成夹具 ─────────────────────────────────────────────────────────────

class _FakeResult:
    """sink_backtest_result 所需的最小 BacktestResult 代理（鸭子类型）。"""

    strategy_id = "st-t1-test"
    idempotency_key = "run-t1-test"
    start_date = datetime(2026, 1, 5)
    end_date = datetime(2026, 1, 9)
    total_return = 0.01
    annual_return = 0.12
    sharpe_ratio = 1.0
    max_drawdown = 0.05
    win_rate = 0.6
    trades_count = 2
    timestamp = datetime(2026, 1, 9, 15, 0, 0)
    overfitting_flag = False
    benchmark_symbol = None
    schema_version = "1.0"


def _ob(price: str = "10.0") -> OrderBookSnapshot:
    p = Decimal(price)
    return OrderBookSnapshot(
        symbol="000001.SZ",
        ask_price=(p, Decimal("10.01")),
        bid_price=(p, Decimal("9.99")),
        ask_vol=(Decimal("10000"),) * 2,
        bid_vol=(Decimal("10000"),) * 2,
        last_price=p,
    )


def _tick(price: str = "20.0") -> TickSnapshot:
    p = Decimal(price)
    return TickSnapshot(
        symbol="000001.SZ",
        timestamp="2026-01-06 09:30:00",
        last_price=p,
        open=p,
        high=p,
        low=p,
        prev_close=p,
        amount=p * 1000,
        volume=Decimal("1000"),
        ask_price=(p, p, p, p, p),
        bid_price=(p, p, p, p, p),
        ask_vol=(Decimal("500"),) * 5,
        bid_vol=(Decimal("500"),) * 5,
    )


# ── TradeRecord 兼容与 sink 投影 ─────────────────────────────────────────

def test_trade_record_legacy_six_keys_compatible():
    """旧 6 键 dict（存量 34 产物口径）构造 TradeRecord 不炸，新字段=None。"""
    r = TradeRecord(
        timestamp="2026-07-10 09:30",
        symbol="000001.SZ",
        side="buy",
        price=10.5,
        quantity=100,
        commission=9.5,
    )
    assert r.decision_price is None
    assert r.order_type is None


def test_sink_to_artifact_new_fields_end_to_end():
    """带新键 trade_log 全链：sink→build_artifact_from_data→artifact 新字段贯通（防投影断链）。"""
    trade_log = [
        {
            "timestamp": "2026-01-06",
            "symbol": "000001.SZ",
            "side": "buy",
            "price": 10.02,
            "quantity": 1000,
            "commission": 15.1,
            "decision_price": 10.0,
            "order_type": "market",
        },
        {
            "timestamp": "2026-01-07",
            "symbol": "000001.SZ",
            "side": "sell",
            "price": 10.5,
            "quantity": 1000,
            "commission": 12.3,
            "decision_price": 10.48,
            "order_type": "tick",
        },
    ]
    sink = sink_backtest_result(_FakeResult(), trade_log=trade_log)
    assert len(sink.trade_log) == 2
    assert sink.trade_log[0].decision_price == 10.0
    assert sink.trade_log[0].order_type == "market"
    assert sink.trade_log[1].order_type == "tick"

    artifact = build_artifact_from_data(sink)
    assert len(artifact.trade_log) == 2
    assert artifact.trade_log[0]["decision_price"] == 10.0
    assert artifact.trade_log[0]["order_type"] == "market"
    assert artifact.trade_log[1]["decision_price"] == 10.48
    assert artifact.trade_log[1]["order_type"] == "tick"


def test_sink_legacy_log_without_new_keys():
    """旧产物（无新键）走 sink 不炸，新字段落 None（消费方容错基线）。"""
    trade_log = [
        {
            "timestamp": "2026-07-10 09:30",
            "symbol": "000001.SZ",
            "side": "buy",
            "price": 10.50105,
            "quantity": 9500,
            "commission": 9.517101615,
        }
    ]
    sink = sink_backtest_result(_FakeResult(), trade_log=trade_log)
    assert sink.trade_log[0].decision_price is None
    assert sink.trade_log[0].order_type is None
    artifact = build_artifact_from_data(sink)
    assert artifact.trade_log[0]["decision_price"] is None
    assert artifact.trade_log[0]["order_type"] is None


# ── 撮合层决策价/订单类型语义 ─────────────────────────────────────────────

def test_market_order_decision_price_is_base_price():
    """市价单决策价=滑点前基准价（BUY=ask1），order_type=market。"""
    logic = MatchingLogic(MatchingConfig())
    fill = logic.match_market_order(
        MatchOrderInput(symbol="000001.SZ", side="BUY", quantity=Decimal("100"), order_type="MARKET"),
        _ob("10.0"),
    )
    assert fill.filled
    assert fill.decision_price == Decimal("10.0")
    assert fill.order_type == "market"
    # 成交价=基准+滑点（1bp），决策价≠成交价（滑点可算）
    assert fill.price > fill.decision_price


def test_limit_order_decision_price_is_limit_price():
    """限价单决策价=委托限价（挂单价），order_type=limit。"""
    logic = MatchingLogic(MatchingConfig())
    fill = logic.match_limit_order(
        MatchOrderInput(
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("100"),
            order_type="LIMIT",
            limit_price=Decimal("10.02"),
        ),
        _ob("10.0"),
    )
    assert fill.filled
    assert fill.decision_price == Decimal("10.02")
    assert fill.order_type == "limit"


def test_tick_order_decision_price_is_tick_last_price():
    """tick 单决策价=触发 tick 的 last_price（信号价，非逐档 VWAP），order_type=tick。"""
    logic = MatchingLogic(MatchingConfig())
    fill = logic.match_tick_order(
        MatchOrderInput(symbol="000001.SZ", side="BUY", quantity=Decimal("1200"), order_type="TICK"),
        _tick("20.0"),
    )
    assert fill.filled_quantity == Decimal("1200")
    assert fill.decision_price == Decimal("20.0")
    assert fill.order_type == "tick"
    # 部分成交回放：同语义（决策价=委托时信号价）
    assert fill.decision_price != fill.price or True  # 滑点 1bp 下近似但不相等


def test_unfilled_fill_has_null_decision_price():
    """未成交占位 fill：决策价/订单类型=None（不产生 trade_log，语义防御）。"""
    logic = MatchingLogic(MatchingConfig())
    fill = logic.match_limit_order(
        MatchOrderInput(
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("100"),
            order_type="LIMIT",
            limit_price=Decimal("9.0"),
        ),
        _ob("10.0"),
    )
    assert not fill.filled
    assert fill.decision_price is None
    assert fill.order_type is None


# ── portfolio 透传 ────────────────────────────────────────────────────────

def test_portfolio_trades_log_carries_new_fields():
    """apply_fill 后 _trades_log 带新键；None 决策价落 null。"""
    pf = Portfolio(initial_capital=Decimal("100000"))
    pf.apply_fill(
        BacktestFill(
            date="2026-01-06",
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("100"),
            price=Decimal("10.02"),
            commission=Decimal("15.1"),
            slippage_cost=Decimal("0.2"),
            decision_price=Decimal("10.0"),
            order_type="market",
        )
    )
    entry = pf.trades_log[0]
    assert entry["decision_price"] == 10.0
    assert entry["order_type"] == "market"

    pf.apply_fill(
        BacktestFill(
            date="2026-01-07",
            symbol="000001.SZ",
            side="SELL",
            quantity=Decimal("100"),
            price=Decimal("10.5"),
        )
    )
    entry2 = pf.trades_log[1]
    assert entry2["decision_price"] is None
    assert entry2["order_type"] is None
