# [A_test] module_id: SRC-TST-1759 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §test
# [MODULE] zephyr.trading.trading_contracts
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_trading_contracts.py
# [TTL] task_bound

from datetime import datetime
from decimal import Decimal

import pytest

order_mod = pytest.importorskip(
    "zephyr.trading.trading_contracts.execution.order", reason="trading-contracts.order not available"
)
Order = order_mod.Order
OrderSide = order_mod.OrderSide
OrderType = order_mod.OrderType
OrderStatus = order_mod.OrderStatus

fill_mod = pytest.importorskip(
    "zephyr.trading.trading_contracts.execution.fill", reason="trading-contracts.fill not available"
)
Fill = fill_mod.Fill

instrument_mod = pytest.importorskip(
    "zephyr.governance.financial_governance.instrument", reason="trading-contracts.instrument not available"
)
Instrument = instrument_mod.Instrument
Stock = instrument_mod.Stock
ETF = instrument_mod.ETF
make_stock_identifier = instrument_mod.make_stock_identifier

money_mod = pytest.importorskip(
    "zephyr.trading.trading_contracts.portfolio.contracts.money", reason="trading-contracts.money not available"
)
Money = money_mod.Money
MoneyPrecisionError = money_mod.MoneyPrecisionError
MoneyCurrencyMismatchError = money_mod.MoneyCurrencyMismatchError
get_currency_precision = money_mod.get_currency_precision

risk_mod = pytest.importorskip("zephyr.risk.risk_limits", reason="trading-contracts.risk_limits not available")
RiskLimits = risk_mod.RiskLimits


class TestOrderSide:
    def test_enum_values(self):
        assert OrderSide.BUY.value == "BUY"
        assert OrderSide.SELL.value == "SELL"

    def test_all_members(self):
        assert set(OrderSide.__members__.keys()) == {"BUY", "SELL"}


class TestOrderType:
    def test_enum_values(self):
        assert OrderType.LIMIT.value == "LIMIT"
        assert OrderType.MARKET.value == "MARKET"
        assert OrderType.STOP.value == "STOP"
        assert OrderType.STOP_LIMIT.value == "STOP_LIMIT"
        assert OrderType.TRAILING_STOP.value == "TRAILING_STOP"

    def test_all_members(self):
        assert len(OrderType) == 5


class TestOrderStatus:
    def test_enum_values(self):
        assert OrderStatus.PENDING.value == "PENDING"
        assert OrderStatus.FILLED.value == "FILLED"
        assert OrderStatus.CANCELLED.value == "CANCELLED"

    def test_all_members(self):
        expected = {"PENDING", "SUBMITTED", "PARTIAL", "FILLED", "CANCELLED", "REJECTED", "EXPIRED"}
        assert set(OrderStatus.__members__.keys()) == expected


class TestOrder:
    def test_creation_with_required_fields(self):
        order = Order(
            idempotency_key="idem-001",
            order_id="ord-001",
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            side=OrderSide.BUY,
            strategy_id="strat-001",
            symbol="600000.SS",
        )
        assert order.order_id == "ord-001"
        assert order.order_type == OrderType.LIMIT
        assert order.quantity == Decimal("100")
        assert order.side == OrderSide.BUY
        assert order.status == OrderStatus.PENDING
        assert order.filled_quantity == Decimal("0")
        assert order.schema_version == "1.0"

    def test_with_optional_fields(self):
        now = datetime.now()
        order = Order(
            idempotency_key="idem-002",
            order_id="ord-002",
            order_type=OrderType.MARKET,
            quantity=Decimal("200"),
            side=OrderSide.SELL,
            strategy_id="strat-002",
            symbol="000001.SZ",
            limit_price=Decimal("10.50"),
            status=OrderStatus.SUBMITTED,
            created_at=now,
        )
        assert order.limit_price == Decimal("10.50")
        assert order.status == OrderStatus.SUBMITTED
        assert order.created_at == now

    def test_default_none_fields(self):
        order = Order(
            idempotency_key="idem-003",
            order_id="ord-003",
            order_type=OrderType.STOP,
            quantity=Decimal("50"),
            side=OrderSide.BUY,
            strategy_id="strat-003",
            symbol="AAPL",
        )
        assert order.avg_fill_price is None
        assert order.broker_order_id is None
        assert order.limit_price is None
        assert order.trace_context is None


class TestFill:
    def test_creation(self):
        now = datetime.now()
        fill = Fill(
            fill_id="fill-001",
            fill_price=Decimal("10.50"),
            fill_timestamp=now,
            filled_quantity=Decimal("100"),
            idempotency_key="idem-001",
            order_id="ord-001",
            strategy_id="strat-001",
            symbol="600000.SS",
        )
        assert fill.fill_id == "fill-001"
        assert fill.fill_price == Decimal("10.50")
        assert fill.filled_quantity == Decimal("100")
        assert fill.commission == Decimal("0")

    def test_frozen(self):
        now = datetime.now()
        fill = Fill(
            fill_id="fill-002",
            fill_price=Decimal("10.50"),
            fill_timestamp=now,
            filled_quantity=Decimal("100"),
            idempotency_key="idem-002",
            order_id="ord-002",
            strategy_id="strat-002",
            symbol="600000.SS",
        )
        with pytest.raises(AttributeError):
            fill.fill_id = "changed"

    def test_with_optional_fields(self):
        now = datetime.now()
        fill = Fill(
            fill_id="fill-003",
            fill_price=Decimal("10.50"),
            fill_timestamp=now,
            filled_quantity=Decimal("100"),
            idempotency_key="idem-003",
            order_id="ord-003",
            strategy_id="strat-003",
            symbol="AAPL",
            commission=Decimal("5.00"),
            slippage=Decimal("0.02"),
            broker_fill_id="bf-001",
        )
        assert fill.commission == Decimal("5.00")
        assert fill.slippage == Decimal("0.02")
        assert fill.broker_fill_id == "bf-001"


class TestInstrument:
    def test_creation(self):
        inst = Instrument(identifier="600000.SS", asset_class="equity")
        assert inst.identifier == "600000.SS"
        assert inst.asset_class == "equity"
        assert inst.exchange == "OTHER"
        assert inst.country == "CN"
        assert inst.currency == "CNY"

    def test_repr(self):
        inst = Instrument(identifier="600000.SS", asset_class="equity")
        assert "600000.SS" in repr(inst)

    def test_frozen(self):
        inst = Instrument(identifier="600000.SS", asset_class="equity")
        with pytest.raises(AttributeError):
            inst.identifier = "changed"


class TestStock:
    def test_creation(self):
        stock = Stock(identifier="600000.SS", asset_class="equity")
        assert stock.lot_size == 100
        assert stock.price_tick == Decimal("0.01")
        assert stock.is_adr is False
        assert stock.is_st is False

    def test_inherits_instrument(self):
        stock = Stock(identifier="600000.SS", asset_class="equity", exchange="SSE")
        assert isinstance(stock, Instrument)
        assert stock.exchange == "SSE"


class TestETF:
    def test_creation(self):
        etf = ETF(identifier="510050.SS", asset_class="etf")
        assert etf.lot_size == 100
        assert etf.price_tick == Decimal("0.001")
        assert etf.tracking_method == "full_replication"
        assert etf.leverage_factor == Decimal("1.0")

    def test_with_underlying_index(self):
        etf = ETF(identifier="510050.SS", asset_class="etf", underlying_index="SSE50")
        assert etf.underlying_index == "SSE50"


class TestMakeStockIdentifier:
    def test_format(self):
        result = make_stock_identifier("SSE", "600000")
        assert result == "SSE:600000"


class TestMoney:
    def test_creation_from_string(self):
        m = Money("1234.56", "CNY")
        assert m.amount == Decimal("1234.56")
        assert m.currency == "CNY"

    def test_creation_from_decimal(self):
        m = Money(Decimal("100.00"), "USD")
        assert m.amount == Decimal("100.00")

    def test_creation_from_int(self):
        m = Money(100, "CNY")
        assert m.amount == Decimal("100")

    def test_float_raises_precision_error(self):
        with pytest.raises(MoneyPrecisionError):
            Money(1234.56, "CNY")

    def test_addition(self):
        a = Money("100.50", "CNY")
        b = Money("50.25", "CNY")
        result = a + b
        assert result.amount == Decimal("150.75")
        assert result.currency == "CNY"

    def test_subtraction(self):
        a = Money("100.50", "CNY")
        b = Money("50.25", "CNY")
        result = a - b
        assert result.amount == Decimal("50.25")

    def test_multiplication_by_int(self):
        m = Money("100.50", "CNY")
        result = m * 2
        assert result.amount == Decimal("201.00")

    def test_multiplication_by_decimal(self):
        m = Money("100.00", "CNY")
        result = m * Decimal("1.5")
        assert result.amount == Decimal("150.00")

    def test_rmul(self):
        m = Money("100.00", "CNY")
        result = 2 * m
        assert result.amount == Decimal("200.00")

    def test_multiplication_float_raises(self):
        m = Money("100.00", "CNY")
        with pytest.raises(MoneyPrecisionError):
            m * 1.5

    def test_division(self):
        m = Money("100.00", "CNY")
        result = m / 2
        assert result.amount == Decimal("50.00")

    def test_division_by_zero(self):
        m = Money("100.00", "CNY")
        with pytest.raises(ZeroDivisionError):
            m / 0

    def test_division_float_raises(self):
        m = Money("100.00", "CNY")
        with pytest.raises(MoneyPrecisionError):
            m / 2.0

    def test_negation(self):
        m = Money("100.00", "CNY")
        result = -m
        assert result.amount == Decimal("-100.00")

    def test_abs(self):
        m = Money("-100.00", "CNY")
        result = abs(m)
        assert result.amount == Decimal("100.00")

    def test_comparison(self):
        a = Money("100.00", "CNY")
        b = Money("50.00", "CNY")
        assert a > b
        assert a >= b
        assert b < a
        assert b <= a

    def test_currency_mismatch_addition(self):
        a = Money("100.00", "CNY")
        b = Money("50.00", "USD")
        with pytest.raises(MoneyCurrencyMismatchError):
            a + b

    def test_currency_mismatch_comparison(self):
        a = Money("100.00", "CNY")
        b = Money("50.00", "USD")
        with pytest.raises(MoneyCurrencyMismatchError):
            a > b

    def test_is_zero(self):
        assert Money("0", "CNY").is_zero() is True
        assert Money("100", "CNY").is_zero() is False

    def test_is_positive(self):
        assert Money("100", "CNY").is_positive() is True
        assert Money("-100", "CNY").is_positive() is False

    def test_is_negative(self):
        assert Money("-100", "CNY").is_negative() is True
        assert Money("100", "CNY").is_negative() is False

    def test_bool(self):
        assert bool(Money("100", "CNY")) is True
        assert bool(Money("0", "CNY")) is False

    def test_str_format(self):
        m = Money("1234.56", "CNY")
        s = str(m)
        assert "CNY" in s

    def test_repr(self):
        m = Money("100.00", "CNY")
        r = repr(m)
        assert "Money" in r
        assert "CNY" in r

    def test_jpy_precision_zero(self):
        m = Money("1000", "JPY")
        assert m.amount == Decimal("1000")

    def test_btc_precision_eight(self):
        m = Money("1.12345678", "BTC")
        assert m.amount == Decimal("1.12345678")


class TestGetCurrencyPrecision:
    def test_known_currencies(self):
        assert get_currency_precision("CNY") == 2
        assert get_currency_precision("JPY") == 0
        assert get_currency_precision("BTC") == 8

    def test_unknown_currency_returns_default(self):
        with pytest.warns(UserWarning):
            prec = get_currency_precision("UNKNOWN")
        assert prec == 2


class TestRiskLimits:
    def test_creation_with_required_fields(self):
        now = datetime.now()
        rl = RiskLimits(as_of_date=now, idempotency_key="idem-001")
        assert rl.as_of_date == now
        assert rl.idempotency_key == "idem-001"
        assert rl.max_gross_leverage == 1.0
        assert rl.max_single_position == 0.1
        assert rl.max_sector_concentration == 0.3
        assert rl.min_single_position == 0.0

    def test_with_optional_fields(self):
        now = datetime.now()
        rl = RiskLimits(
            as_of_date=now,
            idempotency_key="idem-002",
            max_drawdown_limit=0.15,
            max_portfolio_var_1d=0.02,
            max_gross_leverage=2.0,
            max_single_position=0.05,
            symbol_overrides={"AAPL": 0.03},
        )
        assert rl.max_drawdown_limit == 0.15
        assert rl.max_portfolio_var_1d == 0.02
        assert rl.symbol_overrides == {"AAPL": 0.03}

    def test_frozen(self):
        now = datetime.now()
        rl = RiskLimits(as_of_date=now, idempotency_key="idem-003")
        with pytest.raises(AttributeError):
            rl.max_gross_leverage = 5.0

    def test_default_symbol_overrides(self):
        now = datetime.now()
        rl = RiskLimits(as_of_date=now, idempotency_key="idem-004")
        assert rl.symbol_overrides == {}
