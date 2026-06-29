# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.foundation.constants
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.core.runtime_plane_tag; zephyr.shared.infra_06.observer; zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_constants | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

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

import importlib as _il

from zephyr.integration.shared.schema.schemas import (
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
from zephyr.shared.contracts.core.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.shared.infra_06.observer import EventType

_mod = _il.import_module("zephyr.governance.escalation_models")
EscalationLevel = _mod.EscalationLevel

__all__ = [
    "COLD_PATH_LATENCY_BUDGET_MS",
    "COLD_PATH_PARTIAL_ACTIVATED",
    "HOT_PATH_ACTIVATED",
    "HOT_PATH_LATENCY_BUDGET_MS",
    "WARM_PATH_LATENCY_BUDGET_MS",
    "AuditSeverity",
    "Classification",
    "EscalationLevel",
    "EventType",
    "EvolutionPolicy",
    "ExecutionModel",
    "KeCategory",
    "Priority",
    "RuntimePlane",
    "SafetyLevel",
    "TaskNamespace",
    "TaskStatus",
]
