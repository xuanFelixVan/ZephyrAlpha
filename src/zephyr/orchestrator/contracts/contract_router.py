# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.contracts.contract_router
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_contract_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
契约路由（Contract Router）

依据：MOD-MASTER-002 蓝图 §二 集成契约登记表
根据 CT-* 编号路由到对应的系统调用，集成 contract_registry 的 ai_read_only_hint 检查。

路由映射：
  CT-ORC-SCRIPT-001 -> Script System
  CT-ORC-CE-001 -> Context Engine
  CT-ORC-VMS-001 -> Vector Memory
  CT-ORC-GATE-001 -> Gate Engine
  CT-SCRIPT-KB-001 -> Knowledge Base
  CT-SCRIPT-GATE-001 -> Gate Engine
  CT-CE-VMS-001 -> Vector Memory
  CT-CE-LSG-001 -> LLM Security
  CT-KB-VMS-001 -> Vector Memory
  CT-FLE-ORC-001 -> Orchestrator
  CT-FLE-DB-001 -> Database
  CT-TELE-FLE-001 -> Feedback Loop
  CT-PIPE-ORC-001 -> Pipeline
"""

from __future__ import annotations

from typing import Final
from typing import Any

from pydantic import BaseModel, Field

from zephyr.orchestrator.contracts.contract_registry import (
    AIReadOnlyHint,
    ContractRegistry,
)

ROUTE_MAP: Final[dict[str, str]] = {
    "CT-ORC-SCRIPT-001": "script_system",
    "CT-ORC-CE-001": "context-engine",
    "CT-ORC-VMS-001": "vector-memory",
    "CT-ORC-GATE-001": "gate_engine",
    "CT-SCRIPT-KB-001": "knowledge_base",
    "CT-SCRIPT-GATE-001": "gate_engine",
    "CT-CE-VMS-001": "vector-memory",
    "CT-CE-LSG-001": "llm-security",
    "CT-KB-VMS-001": "vector-memory",
    "CT-FLE-ORC-001": "orchestrator",
    "CT-FLE-DB-001": "database",
    "CT-TELE-FLE-001": "feedback-loop",
    "CT-PIPE-ORC-001": "pipeline",
    "CT-RBK-GATE-001": "rollback",
    "CT-HEALTH-001": "telemetry",
    "CT-DLQ-001": "database",
    "CT-RECONCILE-001": "gate_engine",
    "CT-STARTUP-001": "orchestrator",
    "CT-TEARDOWN-001": "orchestrator",
    "CT-SLO-001": "telemetry",
    "CT-BULKHEAD-001": "gate_engine",
    "CT-WATCHDOG-001": "gate_engine",
    "CT-BACKUP-001": "database",
    "CT-CONFIG-001": "orchestrator",
    "CT-FEATUREFLAG-001": "orchestrator",
    "CT-SECRETS-001": "llm-security",
    "CT-KISS-001": "gate_engine",
    "CT-DATA-LIFECYCLE-001": "database",
    "CT-CHAOS-001": "orchestrator",
    "CT-MODEL-REGISTRY-001": "orchestrator",
    "CT-DEPS-001": "gate_engine",
    "CT-KNOWLEDGE-FRESHNESS-001": "knowledge_base",
    "CT-HOUSEKEEPING-001": "database",
    "CT-STABILITY-001": "gate_engine",
    "CT-CANARY-001": "orchestrator",
    "CT-INCIDENT-001": "orchestrator",
    "CT-RACE-CONDITIONS-001": "gate_engine",
    "CT-COST-BUDGET-001": "orchestrator",
    "CT-DISK-GUARD-001": "orchestrator",
    "CT-NETWORK-PARTITION-001": "orchestrator",
    "CT-BENCH-001": "orchestrator",
    "CT-DEPLOY-001": "orchestrator",
    "CT-SCHEMA-MIGRATE-001": "database",
    "CT-DEGRADE-CASCADE-001": "gate_engine",
    "CT-AUTONOMY-001": "orchestrator",
    "CT-AGENT-QUALITY-001": "orchestrator",
    "CT-PROMPT-VERSION-001": "orchestrator",
    "CT-SESSION-CONFLICT-001": "orchestrator",
    "CT-LEAN-001": "orchestrator",
    "CT-BLUEPRINT-HEALTH-001": "gate_engine",
    "CT-TRANSFER-001": "orchestrator",
    "CT-KE-QUALITY-001": "knowledge_base",
}

SYSTEM_NAME_MAP: Final[dict[str, str]] = {
    "script_system": "Script System",
    "context-engine": "Context Engine",
    "vector-memory": "Vector Memory Service",
    "gate_engine": "Gate Engine",
    "knowledge_base": "Knowledge Base",
    "llm-security": "LLM Security Gateway",
    "orchestrator": "Agent Orchestrator",
    "database": "Database",
    "feedback-loop": "Feedback Loop Engine",
    "pipeline": "Task Pipeline",
    "rollback": "Rollback System",
    "telemetry": "System Telemetry",
}


class RouteResult(BaseModel):
    allowed: bool
    contract_id: str
    target_system: str = ""
    target_system_name: str = ""
    hint: AIReadOnlyHint = AIReadOnlyHint.DO_NOT_CALL
    message: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class ContractRouter:
    def __init__(self, registry: ContractRegistry | None = None):
        self._registry = registry or ContractRegistry()

    def route(self, contract_id: str, payload: dict[str, Any] | None = None) -> RouteResult:
        check = self._registry.check_ai_read_only(contract_id)
        target_system = ROUTE_MAP.get(contract_id, "")

        if not check.allowed:
            return RouteResult(
                allowed=False,
                contract_id=contract_id,
                target_system=target_system,
                target_system_name=SYSTEM_NAME_MAP.get(target_system, ""),
                hint=check.hint,
                message=check.message,
            )

        return RouteResult(
            allowed=True,
            contract_id=contract_id,
            target_system=target_system,
            target_system_name=SYSTEM_NAME_MAP.get(target_system, ""),
            hint=check.hint,
            message=check.message,
            payload=payload or {},
        )

    def can_route(self, contract_id: str) -> bool:
        return contract_id in ROUTE_MAP and self._registry.check_ai_read_only(contract_id).allowed

    def get_target_system(self, contract_id: str) -> str:
        return ROUTE_MAP.get(contract_id, "")

    def list_routable(self) -> list[str]:
        return [cid for cid in ROUTE_MAP if self.can_route(cid)]
