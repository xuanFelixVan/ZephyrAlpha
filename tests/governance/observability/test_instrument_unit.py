# [A_test] module_id: MOD-GOV_instrument_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-652 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_instrument
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/contracts/instrument.py
====================================================
覆盖矩阵：
  Instrument 基类：
    - 构造 × 3（最小参数、全参数、默认值）
    - frozen 不可变 × 1
    - hashable × 1
    - __repr__ × 1
  Stock 子类：
    - 构造 × 2（A股、美股）
    - 特有字段 × 1
  ETF 子类：
    - 构造 × 1
    - leverage_factor × 1
  Future 子类：
    - 构造 × 1（股指期货）
    - contract_multiplier × 1
  Option 子类：
    - 构造 × 2（看涨、看跌）
    - exercise_style × 1
  Bond 子类：
    - 构造 × 1
    - coupon_frequency × 1
  FX 子类：
    - 构造 × 1
    - price_tick × 1
  Crypto 子类：
    - 构造 × 2（现货、永续）
    - funding_interval × 1
  make_stock_identifier：
    - 正常 × 1
  枚举完整性：
    - AssetClass / Exchange / CurrencyCode / Jurisdiction × 4

Safety: HIGH（金融工具定义契约）
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from zephyr.governance.financial_governance.instrument import (
    ETF,
    FX,
    AssetClass,
    Bond,
    Crypto,
    CurrencyCode,
    Exchange,
    Future,
    Instrument,
    Jurisdiction,
    Option,
    Stock,
    make_stock_identifier,
)


class TestInstrumentBase:
    def test_minimal_construction(self):
        inst = Instrument(
            identifier="SSE:600000",
            asset_class="equity",
        )
        assert inst.identifier == "SSE:600000"
        assert inst.asset_class == "equity"
        assert inst.exchange == "OTHER"
        assert inst.country == "CN"
        assert inst.currency == "CNY"

    def test_full_construction(self):
        inst = Instrument(
            identifier="NYSE:AAPL",
            asset_class="equity",
            sub_class="common_stock",
            exchange="NYSE",
            country="US",
            currency="USD",
            symbol="AAPL",
            isin="US0378331005",
            figi="BBG000B9XRY4",
            trading_calendar="NYSE",
            jurisdiction="US_SEC",
            display_name="Apple Inc.",
        )
        assert inst.symbol == "AAPL"
        assert inst.isin == "US0378331005"
        assert inst.jurisdiction == "US_SEC"

    def test_default_values(self):
        inst = Instrument(identifier="TEST:1", asset_class="index")
        assert inst.sub_class is None
        assert inst.isin is None
        assert inst.figi is None
        assert inst.display_name == ""

    def test_frozen_immutable(self):
        inst = Instrument(identifier="TEST:1", asset_class="equity")
        with pytest.raises(AttributeError):
            inst.identifier = "CHANGED"

    def test_hashable(self):
        a = Instrument(identifier="SSE:600000", asset_class="equity")
        b = Instrument(identifier="SSE:600000", asset_class="equity")
        assert hash(a) == hash(b)
        s = {a, b}
        assert len(s) == 1

    def test_repr(self):
        inst = Instrument(identifier="SSE:600000", asset_class="equity")
        assert "SSE:600000" in repr(inst)
        assert "Instrument" in repr(inst)


class TestStock:
    @pytest.mark.financial
    def test_a_share(self):
        stock = Stock(
            identifier="SSE:600000",
            asset_class="equity",
            sub_class="common_stock",
            exchange="SSE",
            country="CN",
            currency="CNY",
            symbol="600000",
            display_name="浦发银行",
            lot_size=100,
            price_tick=Decimal("0.01"),
        )
        assert stock.lot_size == 100
        assert stock.price_tick == Decimal("0.01")
        assert stock.is_adr is False
        assert stock.is_st is False

    @pytest.mark.financial
    def test_us_stock(self):
        stock = Stock(
            identifier="NYSE:AAPL",
            asset_class="equity",
            exchange="NYSE",
            country="US",
            currency="USD",
            symbol="AAPL",
            lot_size=1,
            price_tick=Decimal("0.01"),
            is_adr=False,
        )
        assert stock.lot_size == 1
        assert stock.currency == "USD"


class TestETF:
    @pytest.mark.financial
    def test_index_etf(self):
        etf = ETF(
            identifier="SSE:510050",
            asset_class="etf",
            sub_class="index_etf",
            exchange="SSE",
            symbol="510050",
            display_name="50ETF",
            underlying_index="000016.SH",
            tracking_method="full_replication",
        )
        assert etf.underlying_index == "000016.SH"
        assert etf.leverage_factor == Decimal("1.0")

    @pytest.mark.financial
    def test_leveraged_etf(self):
        etf = ETF(
            identifier="SSE:2xETF",
            asset_class="etf",
            leverage_factor=Decimal("2.0"),
        )
        assert etf.leverage_factor == Decimal("2.0")


class TestFuture:
    @pytest.mark.financial
    def test_index_future(self):
        future = Future(
            identifier="CFFEX:IF2506",
            asset_class="future",
            sub_class="index_future",
            exchange="CFFEX",
            currency="CNY",
            symbol="IF2506",
            contract_month="202506",
            contract_multiplier=300,
            price_tick=Decimal("0.2"),
            margin_rate=Decimal("0.12"),
            delivery_method="cash",
        )
        assert future.contract_multiplier == 300
        assert future.delivery_method == "cash"


class TestOption:
    @pytest.mark.financial
    def test_call_option(self):
        opt = Option(
            identifier="SSE:510050C2506M03000",
            asset_class="option",
            sub_class="etf_option",
            exchange="SSE",
            currency="CNY",
            symbol="510050C2506M03000",
            underlying_identifier="SSE:510050",
            option_type="call",
            strike_price=Decimal("3.000"),
            expiry_date=date(2026, 6, 24),
            contract_multiplier=10000,
        )
        assert opt.option_type == "call"
        assert opt.strike_price == Decimal("3.000")
        assert opt.exercise_style == "european"

    @pytest.mark.financial
    def test_put_option(self):
        opt = Option(
            identifier="SSE:510050P2506M03000",
            asset_class="option",
            option_type="put",
            strike_price=Decimal("3.000"),
        )
        assert opt.option_type == "put"


class TestBond:
    @pytest.mark.financial
    def test_government_bond(self):
        bond = Bond(
            identifier="SSE:019733",
            asset_class="bond",
            sub_class="government",
            exchange="SSE",
            currency="CNY",
            symbol="019733",
            issuer="Ministry of Finance",
            maturity_date=date(2035, 6, 15),
            coupon_rate=Decimal("0.0285"),
            coupon_frequency="semi_annual",
            face_value=Decimal("100"),
            bond_type="government",
        )
        assert bond.coupon_rate == Decimal("0.0285")
        assert bond.coupon_frequency == "semi_annual"


class TestFX:
    @pytest.mark.financial
    def test_usdcny(self):
        fx = FX(
            identifier="FX_OTC:USDCNY",
            asset_class="fx",
            exchange="FX_OTC",
            currency="CNY",
            base_currency="USD",
            quote_currency="CNY",
            price_tick=Decimal("0.00001"),
        )
        assert fx.base_currency == "USD"
        assert fx.quote_currency == "CNY"
        assert fx.lot_size == 100_000


class TestCrypto:
    @pytest.mark.financial
    def test_spot(self):
        crypto = Crypto(
            identifier="BINANCE:BTCUSDT",
            asset_class="crypto",
            exchange="BINANCE",
            country="GLOBAL",
            currency="USDT",
            symbol="BTCUSDT",
            contract_type="spot",
        )
        assert crypto.contract_type == "spot"
        assert crypto.settlement_currency is None

    @pytest.mark.financial
    def test_perpetual(self):
        crypto = Crypto(
            identifier="BINANCE:BTCUSDT-PERP",
            asset_class="crypto",
            sub_class="perpetual",
            exchange="BINANCE",
            currency="USDT",
            symbol="BTCUSDT",
            contract_type="perpetual",
            settlement_currency="USDT",
            funding_interval_hours=8,
        )
        assert crypto.contract_type == "perpetual"
        assert crypto.funding_interval_hours == 8


class TestMakeStockIdentifier:
    def test_sse_stock(self):
        assert make_stock_identifier("SSE", "600000") == "SSE:600000"

    def test_nyse_stock(self):
        assert make_stock_identifier("NYSE", "AAPL") == "NYSE:AAPL"


class TestEnumCompleteness:
    def test_asset_class_values(self):
        expected = {"equity", "etf", "future", "option", "bond", "fx", "crypto", "index", "swap", "structured_product"}
        actual = set(AssetClass.__args__)
        assert expected == actual

    def test_exchange_includes_major(self):
        major = {"SSE", "SZSE", "HKEX", "NYSE", "NASDAQ", "TSE", "BINANCE"}
        actual = set(Exchange.__args__)
        assert major.issubset(actual)

    def test_currency_code_includes_fiat_and_crypto(self):
        codes = set(CurrencyCode.__args__)
        assert "CNY" in codes
        assert "USD" in codes
        assert "BTC" in codes
        assert "USDT" in codes

    def test_jurisdiction_includes_major(self):
        jurisdictions = set(Jurisdiction.__args__)
        assert "CN_CSRC" in jurisdictions
        assert "US_SEC" in jurisdictions
        assert "CRYPTO_NONE" in jurisdictions
