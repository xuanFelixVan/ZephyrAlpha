# [A_module] module_id=MOD-SEC_dependency_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_audit.dependency_manager
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [CONSUMERS] MOD-INF-007;MOD-INF-021;MOD-INF-020
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/

from __future__ import annotations

from enum import Enum

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


DEPENDENCIES: list[ManagedDependency] = [
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
