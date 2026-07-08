# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.foundation.constants
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.core.runtime_plane_tag; zephyr.shared.infra.observer; zephyr.shared.schema.schemas; zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_constants | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
constants.py —— 共享枚举 & 常量集中 re-export（Single Source of Truth）

痛点修复：此前 AI 施工时需要到多个文件找枚举定义——
  - instrument.py -> AssetClass / Exchange / Country / CurrencyCode / ...
  - order.py -> OrderSide / OrderType / OrderStatus
  - observer.py -> EventType
  - runtime_plane_tag.py -> RuntimePlane
  - schemas.py -> TaskStatus / SafetyLevel / KeCategory / ...

本文件作为「共享枚举总目录」——AI 只需 import 此文件即可获取所有共享枚举。

设计原则：
  - 纯 re-export：所有枚举的 SSoT 仍在原文件，本文件只做集中暴露
  - 按域分组注释，方便 AI 快速定位所需枚举
  - 本文件禁止定义新枚举——新枚举 MUST 先在对应领域文件中定义

AI 施工约定：
  - 新增枚举时：在原文件定义 -> 在本文件追加 re-export -> 更新 __all__
  - 查找枚举时：优先查本文件，找不到再去原文件

SSoT: MOD-INF-016 §2.4 shared-constants
Version: 0.1.0
"""

import importlib
import re
from typing import Final

from zephyr.shared.contracts.core.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS as _COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED as _COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED as _HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS as _HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS as _WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.shared.infra.observer import EventType
from zephyr.shared.schema.schemas import (
    AuditSeverity,
    Classification,
    EvolutionPolicy,
    ExecutionModel,
    KeCategory,
    Priority,
    SafetyLevel,
    TaskNamespace,
    TaskStatus,
)

# 5.114.6: re-export 常量显式声明 Final 语义，确保跨模块传递 Final 约束
COLD_PATH_LATENCY_BUDGET_MS: Final[float] = _COLD_PATH_LATENCY_BUDGET_MS
COLD_PATH_PARTIAL_ACTIVATED: Final[bool] = _COLD_PATH_PARTIAL_ACTIVATED
HOT_PATH_ACTIVATED: Final[bool] = _HOT_PATH_ACTIVATED
HOT_PATH_LATENCY_BUDGET_MS: Final[float] = _HOT_PATH_LATENCY_BUDGET_MS
WARM_PATH_LATENCY_BUDGET_MS: Final[float] = _WARM_PATH_LATENCY_BUDGET_MS

# 5.160.20 修复：SEMVER正则统一为共享常量
SEMVER_PATTERN: Final[re.Pattern] = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# Lazy imports for trading-domain symbols (upward dependency from L0 shared -> L3 trading)
_TRADING_SYMBOLS = {
    "ETF": "zephyr.trading.trading_contracts.market.instrument",
    "FX": "zephyr.trading.trading_contracts.market.instrument",
    "AssetClass": "zephyr.trading.trading_contracts.market.instrument",
    "Country": "zephyr.trading.trading_contracts.market.instrument",
    "CryptoContractType": "zephyr.trading.trading_contracts.market.instrument",
    "CurrencyCode": "zephyr.trading.trading_contracts.market.instrument",
    "Exchange": "zephyr.trading.trading_contracts.market.instrument",
    "Future": "zephyr.trading.trading_contracts.market.instrument",
    "Jurisdiction": "zephyr.trading.trading_contracts.market.instrument",
    "OptionType": "zephyr.trading.trading_contracts.market.instrument",
    "Stock": "zephyr.trading.trading_contracts.market.instrument",
    "TradingCalendarName": "zephyr.trading.trading_contracts.market.instrument",
    "OrderSide": "zephyr.trading.trading_contracts.execution.order",
    "OrderStatus": "zephyr.trading.trading_contracts.execution.order",
    "OrderType": "zephyr.trading.trading_contracts.execution.order",
}

# Lazy imports for governance-domain symbols (upward dependency from L0 shared -> L2 governance)
_GOVERNANCE_SYMBOLS = {
    "EscalationLevel": "zephyr.governance.escalation.escalation_models",
}

_LAZY_SYMBOLS = {**_TRADING_SYMBOLS, **_GOVERNANCE_SYMBOLS}


def __getattr__(name):
    if name in _LAZY_SYMBOLS:
        mod = importlib.import_module(_LAZY_SYMBOLS[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "COLD_PATH_LATENCY_BUDGET_MS",
    "COLD_PATH_PARTIAL_ACTIVATED",
    "ETF",
    "FX",
    "HOT_PATH_ACTIVATED",
    "HOT_PATH_LATENCY_BUDGET_MS",
    "WARM_PATH_LATENCY_BUDGET_MS",
    "AssetClass",
    "AuditSeverity",
    "Classification",
    "Country",
    "CryptoContractType",
    "CurrencyCode",
    "EscalationLevel",
    "EventType",
    "EvolutionPolicy",
    "Exchange",
    "ExecutionModel",
    "Future",
    "Jurisdiction",
    "KeCategory",
    "OptionType",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "Priority",
    "RuntimePlane",
    "SEMVER_PATTERN",
    "SafetyLevel",
    "Stock",
    "TaskNamespace",
    "TaskStatus",
    "TradingCalendarName",
]
