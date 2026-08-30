# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.architecture_governance.dependency_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: tier 参数
#   fields: 参数 tier，类型注解 DependencyTier
#   code: dependency_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_by_tier
#   name_en: get_by_tier
#   intro: get_by_tier(tier) 源码 L104-L105
#   desc: 源码 L104-L105
#   inputs: tier
#   outputs: list[ManagedDependency]
# - id: A2
#   name_zh: ② get_core_deps
#   name_en: get_core_deps
#   intro: get_core_deps() 源码 L108-L109
#   desc: 源码 L108-L109
#   inputs: 无参数
#   outputs: list[ManagedDependency]
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[ManagedDependency]
#   name_en: list[ManagedDependency]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final

from pydantic import BaseModel


class DependencyTier(str, Enum):
    TIER1_CORE = "Tier1_CORE"
    TIER2_ENHANCED = "Tier2_ENHANCED"
    TIER3_OPTIONAL = "Tier3_OPTIONAL"


class ManagedDependency(BaseModel):
    name: str
    tier: DependencyTier
    redundancy: str = ""
    fallback: str | None = None


DEPENDENCIES: Final[list[ManagedDependency]] = [
    ManagedDependency(
        name="Market Data API", tier=DependencyTier.TIER1_CORE, redundancy="双源冗余", fallback="Vendor B"
    ),
    ManagedDependency(
        name="Broker API", tier=DependencyTier.TIER1_CORE, redundancy="多经纪商", fallback="Broker B / C"
    ),
    ManagedDependency(name="Database", tier=DependencyTier.TIER1_CORE, redundancy="主备切换", fallback="Replica"),
    ManagedDependency(
        name="LLM API (DeepSeek)",
        tier=DependencyTier.TIER2_ENHANCED,
        redundancy="多模型路由",
        fallback="GLM-4.7 / Kimi-K2",
    ),
    ManagedDependency(
        name="LLM API (GLM-4.7)",
        tier=DependencyTier.TIER2_ENHANCED,
        redundancy="多模型路由",
        fallback="DeepSeek / Kimi-K2",
    ),
    ManagedDependency(
        name="Backup Data Source", tier=DependencyTier.TIER3_OPTIONAL, redundancy="best-effort", fallback=None
    ),
]


def get_by_tier(tier: DependencyTier) -> list[ManagedDependency]:
    return [d for d in DEPENDENCIES if d.tier == tier]


def get_core_deps() -> list[ManagedDependency]:
    return get_by_tier(DependencyTier.TIER1_CORE)
