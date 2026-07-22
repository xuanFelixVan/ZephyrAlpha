# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.shared.contracts.protocols
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.gate_types
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement;zephyr.compliance.behavioral_auditor;zephyr.gov_audit;zephyr.infrastructure.rollback;zephyr.autonomy_core;zephyr.integration;zephyr.governance
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Protocols define structural interfaces only; no concrete implementations
# [MODIFY-GUARD] contracts_blueprint.md §Protocols; __init__.py __all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT-protocols | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Structural Protocol interfaces for cross-module contracts.

These @runtime_checkable Protocols break bidirectional dependencies by
defining shared structural interfaces that modules depend on instead of
depending on each other's concrete implementations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Protocol, runtime_checkable

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    # 5.22.3 修复：消除 shared -> governance 顶层 import 闭环
    # GateResult 仅作为 Protocol 方法的字符串注解使用（from __future__ import annotations
    # 已启用，注解在运行时为字符串，无需 runtime import）
    from zephyr.gov_enforcement.rule_enforcement.gate_types import GateResult

# ── 9 Protocol interfaces ────────────────────────────────────────────


@runtime_checkable
class GateActionProtocol(Protocol):
    """Structural interface for rollback/gate action execution."""

    def execute(self) -> GateResult: ...

    @property
    def name(self) -> str: ...


@runtime_checkable
class DriftBudgetCheckerProtocol(Protocol):
    """Structural interface for drift budget checking."""

    def check_budget_for_gate(self, module: str) -> dict: ...


@runtime_checkable
class RecoveryTriggerProtocol(Protocol):
    """Structural interface for drift recovery triggering."""

    def trigger_recovery(self, payload: dict) -> dict: ...


@runtime_checkable
class AuditWriterProtocol(Protocol):
    """Structural interface for immutable audit writing."""

    def write_audit(self, entry: dict) -> str: ...


@runtime_checkable
class DriftScannerProtocol(Protocol):
    """Structural interface for drift event scanning."""

    def scan_drift_events(self) -> list[dict]: ...


@runtime_checkable
class SelfTestableProtocol(Protocol):
    """Structural interface for self-test / health check components."""

    def run_self_test(self) -> bool: ...


@runtime_checkable
class ModuleStatusProtocol(Protocol):
    """Structural interface for module/pipeline status reporting."""

    def get_status(self) -> dict: ...


@runtime_checkable
class EstimateCostFn(Protocol):
    """Structural interface for LLM cost estimation (5.12.2#2 签名漂移治本).

    Canonical 签名：estimate_cost(model, tokens) -> float（总成本 USD）。
    model_router.estimate_cost 已收敛为返回 float；cost_tracker/cost_router/pricing_sync
    的 estimate_cost 均已返回 float，满足此 Protocol。
    分项明细（input_cost/output_cost/total_cost）请用 model_router.estimate_cost_detailed()。
    """

    def estimate_cost(self, model: str, tokens: int) -> float: ...


@runtime_checkable
class HealthCheckFn(Protocol):
    """Structural interface for health check (5.12.2#4 签名漂移治本).

    Canonical 签名：health_check() -> dict[str, Any]（主流签名，17/29=59%）。
    返回健康状态字典。LifecycleAware.health_check 是独立子协议（返回 ModuleHealth），
    已修复 async/sync 契约违反（改 sync）。fail_mode_manager.record_health_check
    （原 health_check）是记录语义非查询，已改名。29 实现分批迁移中。
    """

    def health_check(self) -> dict[str, Any]: ...


@runtime_checkable
class ContractRegistryProtocol(Protocol):
    """Structural interface for integration contract registry (5.60.2 治本).

    governance 门禁检查（phase_check_registry.check_contract_compliance）依赖此抽象，
    替代运行时直接 import zephyr.orchestrator 具体实现（依赖倒置）。
    orchestrator 侧模块加载时经 set_contract_registry_provider() 自注册。
    """

    def list_all(self) -> list[Any]: ...


# ── Contract registry provider（5.60.2 依赖倒置）────────────────────
# governance(L2) 不再 import orchestrator 具体 ContractRegistry；
# orchestrator 在模块加载时调用 set_contract_registry_provider 自注册，
# 消费方经 get_contract_registry() 获取实例。测试可注册 fake provider 独立测试。

_CONTRACT_REGISTRY_PROVIDER: Callable[[], ContractRegistryProtocol] | None = None


def set_contract_registry_provider(provider: Callable[[], ContractRegistryProtocol]) -> None:
    """注册 ContractRegistry 类/工厂（由 orchestrator 侧模块加载时调用）。"""
    global _CONTRACT_REGISTRY_PROVIDER
    _CONTRACT_REGISTRY_PROVIDER = provider


def get_contract_registry() -> ContractRegistryProtocol | None:
    """返回已注册的 ContractRegistry 实例；未注册时返回 None。"""
    if _CONTRACT_REGISTRY_PROVIDER is None:
        return None
    return _CONTRACT_REGISTRY_PROVIDER()


# ── Shared contract types ────────────────────────────────────────────


class AgentCapability(BaseModel):
    """Agent capability contract — shared across agent-spec / governance / audit."""

    agent_id: str
    capabilities: list[str] = Field(default_factory=list)
    version: str = "1.0.0"
    spec_hash: str = ""


class IntegrityVerifier(BaseModel):
    """Integrity verification contract — shared across audit-trail / governance."""

    spec_hash: str = ""

    def verify_chain(self) -> dict:
        raise NotImplementedError


_STABILITY_FROZEN = True
_FROZEN_PUBLIC_API = frozenset(
    {
        "GateActionProtocol",
        "DriftBudgetCheckerProtocol",
        "RecoveryTriggerProtocol",
        "AuditWriterProtocol",
        "DriftScannerProtocol",
        "SelfTestableProtocol",
        "ModuleStatusProtocol",
        "EstimateCostFn",
        "HealthCheckFn",
        "ContractRegistryProtocol",
        "set_contract_registry_provider",
        "get_contract_registry",
        "AgentCapability",
        "IntegrityVerifier",
    }
)
