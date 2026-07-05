# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.market.instrument
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] data; factor; pf_core; ex_core; l10-compliance; shared.foundation.constants
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_instrument | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import ClassVar, Literal

AssetClass = Literal[
    "equity",
    "etf",
    "future",
    "option",
    "bond",
    "fx",
    "crypto",
    "index",
    "swap",
    "structured_product",
]

Exchange = Literal[
    "SSE",
    "SZSE",
    "BSE",
    "SHFE",
    "DCE",
    "CZCE",
    "CFFEX",
    "INE",
    "HKEX",
    "NYSE",
    "NASDAQ",
    "CBOE",
    "CME",
    "ICE",
    "TSE",
    "OSE",
    "KRX",
    "SGX",
    "TWSE",
    "NSE",
    "BSE_IN",
    "LSE",
    "XETRA",
    "EURONEXT",
    "SIX",
    "TSX",
    "ASX",
    "BINANCE",
    "OKX",
    "COINBASE",
    "KRAKEN",
    "BYBIT",
    "FX_OTC",
    "OTHER",
]

Country = Literal[
    "CN",
    "HK",
    "TW",
    "JP",
    "KR",
    "SG",
    "IN",
    "TH",
    "ID",
    "VN",
    "MY",
    "US",
    "CA",
    "UK",
    "DE",
    "FR",
    "CH",
    "NL",
    "ES",
    "IT",
    "SE",
    "NO",
    "AU",
    "NZ",
    "BR",
    "MX",
    "GLOBAL",
]

CurrencyCode = Literal[
    "CNY",
    "HKD",
    "USD",
    "JPY",
    "KRW",
    "SGD",
    "TWD",
    "INR",
    "GBP",
    "EUR",
    "CHF",
    "CAD",
    "AUD",
    "NZD",
    "BTC",
    "ETH",
    "USDT",
    "USDC",
]

Jurisdiction = Literal[
    "CN_CSRC",
    "HK_SFC",
    "US_SEC",
    "US_CFTC",
    "UK_FCA",
    "EU_ESMA",
    "JP_FSA",
    "KR_FSC",
    "SG_MAS",
    "AU_ASIC",
    "CRYPTO_NONE",
    "MULTI",
]

TradingCalendarName = Literal[
    "SSE_A",
    "SZSE_A",
    "HKEX",
    "NYSE",
    "NASDAQ",
    "TSE",
    "KRX",
    "SGX",
    "LSE",
    "XETRA",
    "EURONEXT",
    "CFFEX_INDEX",
    "SHFE_COMMODITY",
    "CME_ELECTRONIC",
    "CRYPTO_24x7",
    "FX_24x5",
]


@dataclass(frozen=True)
class Instrument:
    identifier: str
    asset_class: AssetClass
    sub_class: str | None = None
    exchange: Exchange = "OTHER"
    country: Country = "CN"
    currency: CurrencyCode = "CNY"
    symbol: str = ""
    isin: str | None = None
    figi: str | None = None
    trading_calendar: TradingCalendarName = "SSE_A"
    jurisdiction: Jurisdiction = "CN_CSRC"
    display_name: str = ""
    version: ClassVar[str] = "1.0.0"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.identifier}>"


@dataclass(frozen=True)
class Stock(Instrument):
    lot_size: int = 100
    price_tick: Decimal = Decimal("0.01")
    is_adr: bool = False
    is_st: bool = False


@dataclass(frozen=True)
class ETF(Instrument):
    lot_size: int = 100
    price_tick: Decimal = Decimal("0.001")
    underlying_index: str | None = None
    tracking_method: Literal["full_replication", "sampling", "synthetic"] = "full_replication"
    leverage_factor: Decimal = Decimal("1.0")


@dataclass(frozen=True)
class Future(Instrument):
    underlying_identifier: str | None = None
    contract_month: str = ""
    contract_multiplier: int = 1
    price_tick: Decimal = Decimal("0.2")
    tick_value: Decimal | None = None
    margin_rate: Decimal = Decimal("0.1")
    delivery_method: Literal["physical", "cash"] = "cash"
    last_trading_date: date | None = None
    delivery_date: date | None = None


OptionType = Literal["call", "put"]


@dataclass(frozen=True)
class Option(Instrument):
    underlying_identifier: str = ""
    option_type: OptionType = "call"
    strike_price: Decimal = Decimal("0")
    expiry_date: date | None = None
    contract_multiplier: int = 10000
    exercise_style: Literal["european", "american", "bermudan"] = "european"
    settlement_style: Literal["physical", "cash"] = "physical"


@dataclass(frozen=True)
class Bond(Instrument):
    issuer: str = ""
    maturity_date: date | None = None
    coupon_rate: Decimal = Decimal("0")
    coupon_frequency: Literal["annual", "semi_annual", "quarterly", "zero"] = "semi_annual"
    face_value: Decimal = Decimal("100")
    credit_rating: str | None = None
    bond_type: Literal["government", "municipal", "corporate", "convertible", "abs", "mbs", "perpetual"] = "corporate"


@dataclass(frozen=True)
class FX(Instrument):
    base_currency: CurrencyCode = "USD"
    quote_currency: CurrencyCode = "CNY"
    price_tick: Decimal = Decimal("0.00001")
    lot_size: int = 100_000


CryptoContractType = Literal[
    "spot",
    "perpetual",
    "futures",
    "option",
]


@dataclass(frozen=True)
class Crypto(Instrument):
    contract_type: CryptoContractType = "spot"
    settlement_currency: CurrencyCode | None = None
    contract_multiplier: Decimal = Decimal("1")
    expiry_date: date | None = None
    funding_interval_hours: int | None = None


def make_stock_identifier(exchange: Exchange, symbol: str) -> str:
    return f"{exchange}:{symbol}"
