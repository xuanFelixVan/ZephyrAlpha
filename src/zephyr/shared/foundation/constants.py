"""
constants.py —— 共享枚举 & 常量集中 re-export（Single Source of Truth）

痛点修复：此前 AI 施工时需要到多个文件找枚举定义——
  - instrument.py → AssetClass / Exchange / Country / CurrencyCode / ...
  - order.py → OrderSide / OrderType / OrderStatus
  - observer.py → EventType
  - runtime_plane_tag.py → RuntimePlane
  - schemas.py → TaskStatus / SafetyLevel / KeCategory / ...

本文件作为「共享枚举总目录」——AI 只需 import 此文件即可获取所有共享枚举。

设计原则：
  - 纯 re-export：所有枚举的 SSoT 仍在原文件，本文件只做集中暴露
  - 按域分组注释，方便 AI 快速定位所需枚举
  - 本文件禁止定义新枚举——新枚举 MUST 先在对应领域文件中定义

AI 施工约定：
  - 新增枚举时：在原文件定义 → 在本文件追加 re-export → 更新 __all__
  - 查找枚举时：优先查本文件，找不到再去原文件

SSoT: MOD-INF-016 §2.4 shared-constants
Version: 0.1.0
"""

from zephyr.shared.contracts.market.instrument import (
    ETF,
    FX,
    AssetClass,
    Country,
    CryptoContractType,
    CurrencyCode,
    Exchange,
    Future,
    Jurisdiction,
    OptionType,
    Stock,
    TradingCalendarName,
)
from zephyr.shared.contracts.execution.order import (
    OrderSide,
    OrderStatus,
    OrderType,
)
from zephyr.shared.contracts.core.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
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

__all__ = [
    "AssetClass",
    "Country",
    "CurrencyCode",
    "Exchange",
    "Jurisdiction",
    "TradingCalendarName",
    "ETF",
    "FX",
    "Future",
    "OptionType",
    "CryptoContractType",
    "Stock",
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "RuntimePlane",
    "HOT_PATH_LATENCY_BUDGET_MS",
    "WARM_PATH_LATENCY_BUDGET_MS",
    "COLD_PATH_LATENCY_BUDGET_MS",
    "HOT_PATH_ACTIVATED",
    "COLD_PATH_PARTIAL_ACTIVATED",
    "EventType",
    "TaskStatus",
    "TaskNamespace",
    "SafetyLevel",
    "Classification",
    "EvolutionPolicy",
    "ExecutionModel",
    "AuditSeverity",
    "Priority",
    "KeCategory",
]
