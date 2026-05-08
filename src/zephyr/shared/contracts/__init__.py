# CODEGEN-GUARD: CTR-declarations-manual
# Phase D — codegen auto-override disabled.
# All exports below are manually maintained.
# DO NOT run generate_contracts.py without removing this guard.
"""
ZephyrAlpha — shared/contracts/

全公司共享的数据契约（Data Contracts）。

**核心原则**：
  - 🔒 **本目录所有文件为 Immutable Core 级别**，任何修改必须先建 KB 决策记录并经人工批准
  - ✅ 所有 L00-L11 业务层均可 import，但不可修改
  - ❌ 禁止在本目录放业务逻辑，只放数据结构定义（dataclass / Protocol / Enum / Literal / TypedDict）

**P0 六大跨层数据契约**（CTR-001~006，locked-5yr，frozen dataclass）：
  - market_data.py         — CTR-001 NormalizedMarketData（L00→L02）
  - factor_signal.py       — CTR-002 FactorSignal（L02→L03/L04/L05）
  - risk_limits.py         — CTR-003 RiskLimits（L04→L05）
  - order.py               — CTR-004 Order（L05→L06）
  - fill.py                — CTR-005 Fill（L06→L07）
  - position.py            — CTR-006 PositionSnapshot（L06/L07→L04/L11）

**运行时契约强制执行**（CTR-ERR-006，2026-05-04 新建）：
  - enforcer.py            — ContractEnforcer（@enforce_output / @enforce_input）
  - registry.py            — ContractRegistry（单例，契约注册与查询）
  - base_event.py          — BaseEvent（幂等 Key 基类，INV-007）

**已锁基础契约**（Immutable Core，首批 3 铁板 + runtime_plane_tag 预留）：
  - instrument.py          — 全球证券标识（14 字段，覆盖 12 市场 × 7 资产类）
  - money.py               — 金额 + 货币 + 精度（强制 Decimal，禁止 float）
  - timestamp.py           — 统一时间戳（UTC 存储，纳秒精度，tz-aware 强制）
  - runtime_plane_tag.py   — Runtime Plane 契约预留

**待锁契约**（见 OQ-071 备忘，延后）：
  - trading_calendar.py    — 交易日历抽象（P0）
  - currency.py            — Currency + FXRate（P0）
  - market_session.py      — 市场时段（P0）
  - id_generator.py        — 业务 ID 统一（P0）
  - order_lifecycle.py     — 订单状态机（P1）
  - retention_policy.py    — 审计保留策略（P1）
  - ai_operator_contract.py — AI Operator 接口（P1）

参见：
  - cross-layer-contracts.yaml（31 条契约 SSoT）
  - ADR-0009（shared 层定位）
  - ADR-0004（OCP 扩展点）
  - OQ-070（全球市场扩展）
  - OQ-071（剩余契约待锁）
  - 2026-05-04-架构盲点补全分析.md
"""

from zephyr.shared.contracts.backpressure import (
    BackpressurePause,
    BackpressureResume,
    BackpressureThrottle,
)
from zephyr.shared.contracts.core.enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)
from zephyr.shared.contracts.errors import (
    ContractViolationError as ContractErrViolationError,
    DataQualityError,
    ExecutionRejectionError,
    FactorComputationError,
    RiskLimitViolationError,
    SignalDegradationWarning,
)
from zephyr.shared.contracts.market.factor_signal import FactorSignal
from zephyr.shared.contracts.execution.fill import Fill
from zephyr.shared.contracts.market.instrument import (
    ETF,
    FX,
    AssetClass,
    Bond,
    Country,
    Crypto,
    CryptoContractType,
    CurrencyCode,
    Exchange,
    Future,
    Instrument,
    Jurisdiction,
    Option,
    OptionType,
    Stock,
    TradingCalendarName,
)
from zephyr.shared.contracts.market.market_data import NormalizedMarketData
from zephyr.shared.contracts.portfolio.money import (
    Money,
    MoneyCurrencyMismatchError,
    MoneyPrecisionError,
)
from zephyr.shared.contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.portfolio.position import PositionSnapshot
from zephyr.shared.contracts.core.registry import (
    ContractMeta,
    ContractRegistry,
    VersionMismatchError,
    VersionTransition,
    get_registry,
    reset_registry,
)
from zephyr.shared.contracts.risk.risk_limits import RiskLimits
from zephyr.shared.contracts.core.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.shared.contracts.core.timestamp import (
    NaiveDatetimeError,
    Timestamp,
    ensure_utc,
    utcnow,
)
from zephyr.shared.contracts.core.trace_context import TraceContext
from zephyr.shared.contracts.market.synthesized_signal import SynthesizedSignal
from zephyr.shared.contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.shared.contracts.portfolio.performance_attribution_report import PerformanceAttributionReport
from zephyr.shared.contracts.core.system_configuration import SystemConfiguration
from zephyr.shared.contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.shared.contracts.risk.risk_metrics import RiskMetricsReport
from zephyr.shared.contracts.experiment.experiment_result import ExperimentResult
from zephyr.shared.contracts.risk.compliance_rule import ComplianceRule
from zephyr.shared.contracts.portfolio.strategy_lifecycle_event import StrategyLifecycleEvent
from zephyr.shared.contracts.execution.execution_report import ExecutionReport
from zephyr.shared.contracts.execution.model_serving_request import ModelServingRequest
from zephyr.shared.contracts.experiment.model_serving_response import ModelServingResponse
from zephyr.shared.contracts.core.telemetry_emitter import TelemetryEmitter
from zephyr.shared.contracts.core.factories import (
    make_factor_signal,
    make_order,
    make_risk_dashboard_snapshot,
    make_risk_limits,
    make_risk_metrics_report,
    make_synthesized_signal,
)

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
    "ContractViolationError",
    "EnforcementMode",
    "enforce_output",
    "enforce_input",
    "enforce",
    "AssetClass",
    "Exchange",
    "Country",
    "CurrencyCode",
    "Jurisdiction",
    "TradingCalendarName",
    "Instrument",
    "Stock",
    "ETF",
    "Future",
    "Option",
    "OptionType",
    "Bond",
    "FX",
    "Crypto",
    "CryptoContractType",
    "Money",
    "MoneyPrecisionError",
    "MoneyCurrencyMismatchError",
    "Timestamp",
    "utcnow",
    "ensure_utc",
    "NaiveDatetimeError",
    "RuntimePlane",
    "HOT_PATH_LATENCY_BUDGET_MS",
    "WARM_PATH_LATENCY_BUDGET_MS",
    "COLD_PATH_LATENCY_BUDGET_MS",
    "HOT_PATH_ACTIVATED",
    "COLD_PATH_PARTIAL_ACTIVATED",
    "TraceContext",
    "DataQualityError",
    "FactorComputationError",
    "SignalDegradationWarning",
    "RiskLimitViolationError",
    "ExecutionRejectionError",
    "ContractErrViolationError",
    "BackpressurePause",
    "BackpressureThrottle",
    "BackpressureResume",
    "ContractRegistry",
    "ContractMeta",
    "VersionTransition",
    "VersionMismatchError",
    "get_registry",
    "reset_registry",
    "SynthesizedSignal",
    "CapitalAllocationResult",
    "PerformanceAttributionReport",
    "SystemConfiguration",
    "RiskDashboardSnapshot",
    "RiskMetricsReport",
    "ExperimentResult",
    "ComplianceRule",
    "StrategyLifecycleEvent",
    "ExecutionReport",
    "ModelServingRequest",
    "ModelServingResponse",
    "TelemetryEmitter",
    "make_risk_limits",
    "make_risk_dashboard_snapshot",
    "make_risk_metrics_report",
    "make_factor_signal",
    "make_synthesized_signal",
    "make_order",
]
