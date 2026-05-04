"""
ZephyrAlpha — shared/

跨层共享基础设施：契约（contracts）、工具（utils）、不可变核心（immutable_core）。

本包的内容**不绑定任何业务层**，所有 L00-L11 层均可 import。

SSoT 模块（所有路径/时间/解析/token 常量和函数的唯一真源）：
  - paths.py           → REPO_ROOT, DB_PATH, 路径常量
  - time_utils.py      → utc_now(), now_iso(), default_now()
  - frontmatter_utils.py → parse_frontmatter(), extract_body()
  - token_utils.py     → estimate_tokens()

跨层数据契约（CTR-001 ~ CTR-006，承重墙，禁止在模块内自造等价类型）：
  - contracts.market_data    → NormalizedMarketData（L00→L02）
  - contracts.factor_signal  → FactorSignal（L02→L03/L04/L05）
  - contracts.risk_limits    → RiskLimits（L04→L05）
  - contracts.order          → Order, OrderSide, OrderType, OrderStatus（L05→L06）
  - contracts.fill           → Fill（L06→L07）
  - contracts.position       → PositionSnapshot（L06/L07→L04/L11）
  - contracts.instrument     → Instrument + 6子类
  - contracts.money          → Money + 货币精度表
  - contracts.timestamp      → Timestamp + utcnow/ensure_utc
  - contracts.runtime_plane_tag → RuntimePlaneTag + HOT/WARM/COLD

参见：
  - ADR-0009（shared 层定位）
  - cross-layer-contracts.yaml（CTR SSoT）
"""

from zephyr.shared.contracts.enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)
from zephyr.shared.contracts.factor_signal import FactorSignal
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.instrument import (
    ETF,
    FX,
    Bond,
    Crypto,
    Future,
    Instrument,
    Option,
    Stock,
)
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.contracts.money import Money, get_currency_precision
from zephyr.shared.contracts.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.contracts.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.shared.contracts.timestamp import Timestamp, ensure_utc, utcnow

__all__ = [
    "NormalizedMarketData",
    "FactorSignal",
    "RiskLimits",
    "Order",
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "Fill",
    "PositionSnapshot",
    "Instrument",
    "Stock",
    "ETF",
    "Future",
    "Option",
    "Bond",
    "FX",
    "Crypto",
    "Money",
    "get_currency_precision",
    "Timestamp",
    "utcnow",
    "ensure_utc",
    "RuntimePlane",
    "HOT_PATH_LATENCY_BUDGET_MS",
    "WARM_PATH_LATENCY_BUDGET_MS",
    "COLD_PATH_LATENCY_BUDGET_MS",
    "HOT_PATH_ACTIVATED",
    "COLD_PATH_PARTIAL_ACTIVATED",
    "enforce_output",
    "enforce_input",
    "enforce",
    "ContractViolationError",
    "EnforcementMode",
]
