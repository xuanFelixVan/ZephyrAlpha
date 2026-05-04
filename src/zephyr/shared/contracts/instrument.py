"""
ZephyrAlpha — shared/contracts/instrument.py

全球证券标识契约（Global Instrument Identifier Contract）。

🔒 **锁定文件（Immutable Core）**：任何修改必须先建 ADR 并经人工批准。

═══════════════════════════════════════════════════════════════════════
【设计目标】
═══════════════════════════════════════════════════════════════════════
本契约一次性覆盖 ZephyrAlpha 未来终局的全球市场 + 全资产类 × 全辖区扩展需求：

- 12 主要市场：CN(A股)、HK、US、JP、KR、SG、TW、IN、UK、DE、FR、CH …
- 7 资产类：equity、etf、future、option、bond、fx、crypto
- 10+ 监管辖区：CN_CSRC、HK_SFC、US_SEC、UK_FCA、EU_ESMA、JP_FSA、KR_FSC、CRYPTO_NONE …

**核心设计原则**：
  1. `Instrument` 基类覆盖所有资产类共有字段（12 字段）
  2. 子类（Stock / Future / Option / Bond / FX / Crypto）承载品种特有字段
  3. 全部 `frozen=True`，不可变，可哈希，可作字典键
  4. `identifier` 字段是全局唯一主键，建议使用 FIGI（Bloomberg 全球标准）
     或退化为 `f"{exchange}:{symbol}"`

**与架构的关系**：
  - 本契约**不属于任何业务层**，放在 shared/contracts/
  - L00（数据源）、L02（因子）、L05（组合）、L06（执行）、L10（合规）均依赖本契约
  - 14 层架构如何调整都不影响本契约（契约是业务物理常识，不是组织架构）

参见：
  - OQ-070（全球市场扩展契约规划，会话 11 落盘）
  - ADR-0009（应用架构 shared 层定位）
  - Bloomberg FIGI 标准：https://www.openfigi.com/
  - ISO 10962 CFI Code 分类标准
  - ISO 4217 Currency Code
  - ISO 3166-1 Country Code
═══════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import ClassVar, Literal, Optional


# ═══════════════════════════════════════════════════════════════════
# 核心枚举（Literal 类型，轻量且可静态检查）
# ═══════════════════════════════════════════════════════════════════

AssetClass = Literal[
    "equity",              # 股票
    "etf",                 # 交易所交易基金
    "future",              # 期货
    "option",              # 期权
    "bond",                # 债券
    "fx",                  # 外汇
    "crypto",              # 加密货币
    "index",               # 指数（只有行情，不可交易，如 CSI 300 指数）
    "swap",                # 互换（P2 预留）
    "structured_product",  # 结构化产品（P3 预留）
]
"""
资产类枚举。遵循 ISO 10962 CFI Code 大类划分。

未来新增资产类时：
  1. 在 Literal 中加新值
  2. 新增对应子类（如 Swap / StructuredProduct）
  3. 所有依赖本契约的代码无需改动（因为依赖的是 Instrument 基类）
"""


Exchange = Literal[
    # 中国
    "SSE",       # 上海证券交易所
    "SZSE",      # 深圳证券交易所
    "BSE",       # 北京证券交易所
    "SHFE",      # 上海期货交易所
    "DCE",       # 大连商品交易所
    "CZCE",      # 郑州商品交易所
    "CFFEX",     # 中国金融期货交易所
    "INE",       # 上海国际能源交易中心
    # 香港
    "HKEX",      # 香港交易所
    # 美国
    "NYSE",      # 纽约证券交易所
    "NASDAQ",    # 纳斯达克
    "CBOE",      # 芝加哥期权交易所
    "CME",       # 芝加哥商业交易所
    "ICE",       # 洲际交易所
    # 日本
    "TSE",       # 东京证券交易所
    "OSE",       # 大阪交易所（期货期权）
    # 韩国
    "KRX",       # 韩国交易所
    # 新加坡
    "SGX",       # 新加坡交易所
    # 台湾
    "TWSE",      # 台湾证券交易所
    # 印度
    "NSE",       # 印度国家证券交易所
    "BSE_IN",    # 孟买证券交易所
    # 英国
    "LSE",       # 伦敦证券交易所
    # 欧陆
    "XETRA",     # 德国电子交易所
    "EURONEXT",  # 泛欧交易所
    "SIX",       # 瑞士交易所
    # 加拿大
    "TSX",       # 多伦多交易所
    # 澳大利亚
    "ASX",       # 澳交所
    # 加密货币（去中心化或中心化平台）
    "BINANCE",
    "OKX",
    "COINBASE",
    "KRAKEN",
    "BYBIT",
    # 外汇
    "FX_OTC",    # 场外外汇（银行间/经纪商网络）
    # 未知/其他
    "OTHER",
]
"""
交易所枚举。使用业界广泛接受的缩写（MIC 标准或本地俗称）。

Kimi OSS 抓取阶段允许 "OTHER"，白天 Sonnet 合并时校准。
"""


Country = Literal[
    "CN", "HK", "TW", "JP", "KR", "SG", "IN", "TH", "ID", "VN", "MY",  # 亚太
    "US", "CA",                                                         # 北美
    "UK", "DE", "FR", "CH", "NL", "ES", "IT", "SE", "NO",              # 欧洲
    "AU", "NZ",                                                         # 大洋洲
    "BR", "MX",                                                         # 拉美
    "GLOBAL",                                                           # 加密货币等无国界
]
"""ISO 3166-1 alpha-2 国家代码（精简版，覆盖主要交易市场）。"""


CurrencyCode = Literal[
    "CNY",  # 人民币
    "HKD",  # 港币
    "USD",  # 美元
    "JPY",  # 日元（无小数位）
    "KRW",  # 韩元（无小数位）
    "SGD",  # 新加坡元
    "TWD",  # 新台币
    "INR",  # 印度卢比
    "GBP",  # 英镑
    "EUR",  # 欧元
    "CHF",  # 瑞郎
    "CAD",  # 加元
    "AUD",  # 澳元
    "NZD",  # 纽元
    # 加密
    "BTC", "ETH", "USDT", "USDC",
]
"""ISO 4217 货币代码 + 主流加密货币。完整清单在 money.py 的 Currency 类中维护精度。"""


Jurisdiction = Literal[
    "CN_CSRC",     # 中国证监会
    "HK_SFC",      # 香港证监会
    "US_SEC",      # 美国证监会
    "US_CFTC",     # 美国商品期货交易委员会（期货/期权/加密衍生品）
    "UK_FCA",      # 英国金融行为监管局
    "EU_ESMA",     # 欧盟证券与市场管理局（MiFID II）
    "JP_FSA",      # 日本金融厅
    "KR_FSC",      # 韩国金融委员会
    "SG_MAS",      # 新加坡金管局
    "AU_ASIC",     # 澳大利亚证券投资委员会
    "CRYPTO_NONE", # 无监管（部分加密货币场景）
    "MULTI",       # 多辖区（如跨境 ADR）
]
"""
监管辖区枚举。决定 L10 Governance 走哪套合规规则。

用法：`l10_governance/policies/{jurisdiction.lower()}/` 目录对应各辖区规则包。
"""


TradingCalendarName = Literal[
    # 股票日历
    "SSE_A",           # 上交所 A股（T+1，11:30-13:00 午休）
    "SZSE_A",          # 深交所 A股（同上）
    "HKEX",            # 港交所（T+2，12:00-13:00 午休）
    "NYSE",            # 纽交所（T+2，无午休，有盘前盘后）
    "NASDAQ",          # 纳斯达克（同纽交所）
    "TSE",             # 东交所（日股，T+2，11:30-12:30 午休）
    "KRX",             # 韩交所
    "SGX",             # 新交所
    "LSE",             # 伦交所
    "XETRA",           # 德交所
    "EURONEXT",        # 泛欧
    # 期货日历
    "CFFEX_INDEX",     # 中金所股指期货（T+0，有夜盘部分品种）
    "SHFE_COMMODITY",  # 上期所商品期货（T+0，有夜盘）
    "CME_ELECTRONIC",  # CME 电子盘（近 24×5）
    # 加密
    "CRYPTO_24x7",     # 加密 7×24 连续
    # 外汇
    "FX_24x5",         # 外汇周一-周五 24 小时
]
"""
交易日历名称。实际日历实现延后到 trading_calendar.py（见 OQ-071 P0 待锁清单）。

本阶段仅作为字符串标签用于 Instrument，便于未来 TradingCalendar 实现时按名查表。
"""


# ═══════════════════════════════════════════════════════════════════
# Instrument 基类
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Instrument:
    """
    全球证券标识基类。

    所有交易/分析/风控/合规对象的核心主键。不可变（frozen=True），可哈希。

    **12 字段覆盖全球所有资产类共有信息**：
        identifier / asset_class / sub_class / exchange / country / currency
        symbol / isin / figi / trading_calendar / jurisdiction / display_name

    具体品种的特有字段（如期货的合约月、期权的行权价、债券的久期）由子类承载。

    【用法示例 1：A股股票】
        stock = Stock(
            identifier="SSE:600000",
            asset_class="equity",
            sub_class="common_stock",
            exchange="SSE",
            country="CN",
            currency="CNY",
            symbol="600000",
            isin="CNE000000007",
            figi=None,
            trading_calendar="SSE_A",
            jurisdiction="CN_CSRC",
            display_name="浦发银行",
            lot_size=100,
            price_tick=Decimal("0.01"),
        )

    【用法示例 2：上证50 ETF期权】
        option = Option(
            identifier="SSE:510050C2506M03000",
            asset_class="option",
            sub_class="etf_option",
            exchange="SSE",
            country="CN",
            currency="CNY",
            symbol="510050C2506M03000",
            isin=None,
            figi=None,
            trading_calendar="SSE_A",
            jurisdiction="CN_CSRC",
            display_name="50ETF购6月3000",
            underlying_identifier="SSE:510050",
            option_type="call",
            strike_price=Decimal("3.000"),
            expiry_date=date(2026, 6, 24),
            contract_multiplier=10000,
        )

    【用法示例 3：比特币永续合约】
        crypto = Crypto(
            identifier="BINANCE:BTCUSDT-PERP",
            asset_class="crypto",
            sub_class="perpetual",
            exchange="BINANCE",
            country="GLOBAL",
            currency="USDT",
            symbol="BTCUSDT",
            isin=None,
            figi=None,
            trading_calendar="CRYPTO_24x7",
            jurisdiction="CRYPTO_NONE",
            display_name="Bitcoin 永续 USDT 本位",
            contract_type="perpetual",
            settlement_currency="USDT",
            contract_multiplier=1,
        )
    """

    # --- 全局唯一标识（第一优先级主键）---
    identifier: str
    """
    全局唯一标识。推荐格式：
      - Bloomberg FIGI（12 位，如 "BBG000BLNNH6"），若可获得
      - 退化为 `"{exchange}:{symbol}"`（如 "SSE:600000"）

    本字段必须在**全公司范围内唯一**，可作 dict 键、数据库主键、消息队列路由键。
    """

    # --- 资产分类 ---
    asset_class: AssetClass
    """资产大类。"""

    sub_class: Optional[str] = None
    """
    子类（自由文本，约定俗成）。示例：
      - equity: "common_stock" / "preferred_stock" / "h_share" / "adr"
      - etf: "index_etf" / "commodity_etf" / "bond_etf" / "leveraged_etf"
      - future: "index_future" / "commodity_future" / "treasury_future" / "fx_future"
      - option: "index_option" / "etf_option" / "stock_option"
      - bond: "government" / "corporate" / "convertible" / "abs"
      - crypto: "spot" / "perpetual" / "futures" / "options"
    """

    # --- 地域 + 交易所 ---
    exchange: Exchange = "OTHER"
    """交易所枚举。"""

    country: Country = "CN"
    """ISO 3166-1 国家代码。"""

    currency: CurrencyCode = "CNY"
    """
    计价货币（ISO 4217）。

    ⚠️ 注意：这是**证券的报价货币**，不是账户本位币。跨币种估值时由 FXRateProvider 换算。
    """

    # --- 本地标识 ---
    symbol: str = ""
    """交易所本地代码（如 A股 "600000"、美股 "AAPL"、日股 "7203"）。"""

    isin: Optional[str] = None
    """
    ISO 6166 国际证券标识码（12 位）。适用于大部分股票和债券。

    加密货币/外汇/本地期货通常无 ISIN。
    """

    figi: Optional[str] = None
    """
    Bloomberg FIGI 全球标准（12 位）。比 ISIN 覆盖更广（含期货期权加密）。

    可从 OpenFIGI API 免费查询：https://www.openfigi.com/api
    """

    # --- 时段模型 ---
    trading_calendar: TradingCalendarName = "SSE_A"
    """
    交易日历名称（字符串标签）。

    ⚠️ 本阶段仅作为标签存储，具体日历实现（is_trading_day / trading_hours 等）
    延后到 `shared/contracts/trading_calendar.py`（见 OQ-071 P0 待锁清单）。
    """

    # --- 监管辖区 ---
    jurisdiction: Jurisdiction = "CN_CSRC"
    """监管辖区。决定 L10 走哪套合规规则包。"""

    # --- 展示 ---
    display_name: str = ""
    """人类可读名称（中文/英文/本地语言）。仅用于 UI 和日志，不参与逻辑判断。"""

    # --- 版本（用于证券主数据变更追踪）---
    version: ClassVar[str] = "1.0.0"
    """Instrument 契约 schema 版本。变更时走 ADR。"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.identifier}>"


# ═══════════════════════════════════════════════════════════════════
# 子类：按资产类承载特有字段
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Stock(Instrument):
    """股票（普通股 / 优先股 / H股 / ADR 等）。"""

    lot_size: int = 100
    """最小交易单位（A股 100 股/手，港股因股而异，美股常为 1 股）。"""

    price_tick: Decimal = Decimal("0.01")
    """最小报价变动单位。"""

    is_adr: bool = False
    """是否为 ADR（美国存托凭证）。"""

    is_st: bool = False
    """是否特别处理股票（ST / *ST / 退市整理期），影响风控和涨跌停。"""


@dataclass(frozen=True)
class ETF(Instrument):
    """交易所交易基金。"""

    lot_size: int = 100
    price_tick: Decimal = Decimal("0.001")
    """ETF 报价精度常高于股票（A股 ETF 0.001 元）。"""

    underlying_index: Optional[str] = None
    """跟踪的标的指数（如 "000300.SH" 沪深300）。"""

    tracking_method: Literal["full_replication", "sampling", "synthetic"] = "full_replication"
    """复制方法：完全复制 / 抽样复制 / 合成复制。"""

    leverage_factor: Decimal = Decimal("1.0")
    """杠杆倍数（普通 ETF=1，2×做多=2，3×做空=-3）。"""


@dataclass(frozen=True)
class Future(Instrument):
    """期货合约。"""

    underlying_identifier: Optional[str] = None
    """标的资产的 Instrument.identifier（如 "CSI:000300" 或 "CME:WTI"）。"""

    contract_month: str = ""
    """合约月份，YYYYMM 格式，如 "202506"。"""

    contract_multiplier: int = 1
    """合约乘数（如沪深300股指期货 300，原油期货 1000 桶）。"""

    price_tick: Decimal = Decimal("0.2")
    """最小变动价位。"""

    tick_value: Optional[Decimal] = None
    """每跳对应的货币价值（= price_tick × contract_multiplier）。"""

    margin_rate: Decimal = Decimal("0.1")
    """保证金率（10% 默认）。"""

    delivery_method: Literal["physical", "cash"] = "cash"
    """交割方式：实物交割 / 现金交割。"""

    last_trading_date: Optional[date] = None
    """最后交易日。"""

    delivery_date: Optional[date] = None
    """交割日。"""


OptionType = Literal["call", "put"]
"""期权类型：看涨 / 看跌。"""


@dataclass(frozen=True)
class Option(Instrument):
    """期权合约（标准欧式/美式，股票/ETF/指数/期货期权）。"""

    underlying_identifier: str = ""
    """标的资产的 Instrument.identifier。"""

    option_type: OptionType = "call"
    """看涨 / 看跌。"""

    strike_price: Decimal = Decimal("0")
    """行权价。"""

    expiry_date: Optional[date] = None
    """到期日（YYYY-MM-DD）。"""

    contract_multiplier: int = 10000
    """合约乘数（A股 50ETF 期权 10000 份，标普 500 期权 100 股）。"""

    exercise_style: Literal["european", "american", "bermudan"] = "european"
    """行权风格：欧式 / 美式 / 百慕大式。"""

    settlement_style: Literal["physical", "cash"] = "physical"
    """结算方式。"""


@dataclass(frozen=True)
class Bond(Instrument):
    """债券。"""

    issuer: str = ""
    """发行人。"""

    maturity_date: Optional[date] = None
    """到期日。"""

    coupon_rate: Decimal = Decimal("0")
    """票面利率（年化，0.03 表示 3%）。"""

    coupon_frequency: Literal["annual", "semi_annual", "quarterly", "zero"] = "semi_annual"
    """付息频率。零息债券用 'zero'。"""

    face_value: Decimal = Decimal("100")
    """面值（按面值 100 报价为业界惯例）。"""

    credit_rating: Optional[str] = None
    """信用评级（"AAA" / "AA+" / "BBB-" 等，按评级机构原文）。"""

    bond_type: Literal[
        "government",      # 政府债
        "municipal",       # 市政债
        "corporate",       # 公司债
        "convertible",     # 可转债
        "abs",             # 资产支持证券
        "mbs",             # 抵押贷款支持证券
        "perpetual",       # 永续债
    ] = "corporate"


@dataclass(frozen=True)
class FX(Instrument):
    """外汇货币对。"""

    base_currency: CurrencyCode = "USD"
    """基础货币（分子）。"""

    quote_currency: CurrencyCode = "CNY"
    """报价货币（分母）。"""

    price_tick: Decimal = Decimal("0.00001")
    """报价最小变动（通常 1 pip = 0.0001，部分货币对 0.00001）。"""

    lot_size: int = 100_000
    """标准手（100,000 基础货币单位）。"""


CryptoContractType = Literal[
    "spot",         # 现货
    "perpetual",    # 永续合约
    "futures",      # 交割合约
    "option",       # 加密期权
]
"""加密货币合约类型。"""


@dataclass(frozen=True)
class Crypto(Instrument):
    """加密货币（现货/永续/交割/期权）。"""

    contract_type: CryptoContractType = "spot"
    """合约类型。"""

    settlement_currency: Optional[CurrencyCode] = None
    """
    结算币种。用于衍生品区分 USDT 本位 / 币本位。
      - USDT 本位永续：settlement_currency = "USDT"
      - 币本位永续（如 BTCUSD 以 BTC 结算）：settlement_currency = "BTC"
      - 现货：None
    """

    contract_multiplier: Decimal = Decimal("1")
    """合约乘数（现货=1，BTC 季度合约 CME=5 BTC，Bybit 反向合约通常=1 USD）。"""

    expiry_date: Optional[date] = None
    """交割合约到期日。永续合约和现货为 None。"""

    funding_interval_hours: Optional[int] = None
    """永续合约资金费率结算间隔（小时）。典型 Binance=8h，Bybit=8h，OKX=8h。"""


# ═══════════════════════════════════════════════════════════════════
# 便捷辅助（仅供调试/测试，生产代码请显式构造子类）
# ═══════════════════════════════════════════════════════════════════

def make_stock_identifier(exchange: Exchange, symbol: str) -> str:
    """
    生成标准 identifier：`{exchange}:{symbol}`。

    例：make_stock_identifier("SSE", "600000") → "SSE:600000"
    """
    return f"{exchange}:{symbol}"
