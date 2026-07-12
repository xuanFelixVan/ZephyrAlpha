# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.dispatch_table
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_dispatch_table | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AI Agent 冷启动分派表（Dispatch Table）

依据：MOD-MASTER-002 蓝图 §零 AI Agent 分派与阅读指南
为 13 个系统提供 CT-* 契约 × 关联 Schema × Token 预算的完整分派映射。

功能：
1. 根据系统名称查询所需 CT-* 契约
2. 返回关联的 Schema 模型
3. 输出 Token 预算估计
4. 新 AI session 冷启动时定位蓝图节段
"""

from __future__ import annotations

from typing import Final
from dataclasses import dataclass


@dataclass(frozen=True)
class SystemDispatch:
    system_name: str
    ct_contracts: tuple[str, ...]
    schemas: tuple[str, ...]
    token_budget: int
    blueprint_section: str = ""


DISPATCH_TABLE: Final[dict[str, SystemDispatch]] = {
    "orchestrator": SystemDispatch(
        system_name="Orchestrator（任务系统）",
        ct_contracts=(
            "CT-ORC-SCRIPT",
            "CT-ORC-CE",
            "CT-ORC-VMS",
            "CT-ORC-GATE",
            "CT-ORC-DB",
        ),
        schemas=("TaskCard", "Finding"),
        token_budget=1800,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Orchestrator 行",
    ),
    "script-system": SystemDispatch(
        system_name="Script System（脚本系统）",
        ct_contracts=(
            "CT-ORC-SCRIPT",
            "CT-SCRIPT-KB",
            "CT-SCRIPT-GATE",
            "CT-FEATUREFLAG",
        ),
        schemas=("Finding", "KE"),
        token_budget=1400,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Script System 行",
    ),
    "knowledge-base": SystemDispatch(
        system_name="Knowledge Base（知识库）",
        ct_contracts=(
            "CT-SCRIPT-KB",
            "CT-KB-VMS",
            "CT-DATA-LIFECYCLE",
        ),
        schemas=("KE",),
        token_budget=1000,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Knowledge Base 行",
    ),
    "context-engine": SystemDispatch(
        system_name="Context Engine（CE）",
        ct_contracts=(
            "CT-ORC-CE",
            "CT-CE-VMS",
            "CT-CE-LSG",
            "CT-BULKHEAD",
        ),
        schemas=("TaskCard",),
        token_budget=1400,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Context Engine 行",
    ),
    "gate-engine": SystemDispatch(
        system_name="Gate Engine（门控引擎）",
        ct_contracts=(
            "CT-ORC-GATE",
            "CT-SCRIPT-GATE",
            "CT-FEATUREFLAG",
        ),
        schemas=("TaskCard",),
        token_budget=900,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Gate Engine 行",
    ),
    "feedback-loop": SystemDispatch(
        system_name="Feedback Loop（FLE）",
        ct_contracts=(
            "CT-FLE-ORC",
            "CT-FLE-DB",
            "CT-TELE-FLE",
            "CT-WATCHDOG",
        ),
        schemas=(),
        token_budget=1200,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Feedback Loop 行",
    ),
    "pipeline": SystemDispatch(
        system_name="Pipeline",
        ct_contracts=("CT-PIPE-ORC",),
        schemas=("TaskCard",),
        token_budget=400,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Pipeline 行",
    ),
    "vector-memory": SystemDispatch(
        system_name="Vector Memory（VMS）",
        ct_contracts=(
            "CT-ORC-VMS",
            "CT-CE-VMS",
            "CT-KB-VMS",
            "CT-BULKHEAD",
        ),
        schemas=(),
        token_budget=900,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Vector Memory 行",
    ),
    "database": SystemDispatch(
        system_name="Database（db）",
        ct_contracts=(
            "CT-FLE-DB",
            "CT-ORC-DB",
            "CT-DLQ",
            "CT-BACKUP",
        ),
        schemas=(),
        token_budget=700,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Database 行",
    ),
    "llm-security": SystemDispatch(
        system_name="LLM Security（LSG）",
        ct_contracts=(
            "CT-CE-LSG",
            "CT-SECRETS",
        ),
        schemas=(),
        token_budget=500,
        blueprint_section="§零 AI Agent 分派与阅读指南 — LLM Security 行",
    ),
    "mcp-servers": SystemDispatch(
        system_name="MCP Servers（MCP）",
        ct_contracts=(
            "CT-MCP-TOOL",
            "CT-MCP-TRANSPORT",
            "CT-SECRETS",
        ),
        schemas=(),
        token_budget=1100,
        blueprint_section="§零 AI Agent 分派与阅读指南 — MCP Servers 行",
    ),
    "system-telemetry": SystemDispatch(
        system_name="System Telemetry",
        ct_contracts=(
            "CT-TELE-FLE",
            "CT-WATCHDOG",
        ),
        schemas=(),
        token_budget=400,
        blueprint_section="§零 AI Agent 分派与阅读指南 — System Telemetry 行",
    ),
    "cross-system-governance": SystemDispatch(
        system_name="跨系统管控（横向）",
        ct_contracts=(
            "CT-HEALTH",
            "CT-CBAC",
            "CT-CDC",
            "CT-CONFIG",
            "CT-FEATUREFLAG",
            "CT-CHAOS",
            "CT-RECONCILE",
            "CT-STARTUP",
            "CT-TEARDOWN",
            "CT-MODEL-REGISTRY",
            "CT-DEPS",
            "CT-KNOWLEDGE-FRESHNESS",
            "CT-HOUSEKEEPING",
            "CT-SESSION-handoff",
            "CT-STABILITY",
            "CT-CANARY",
            "CT-INCIDENT",
            "CT-RACE-CONDITIONS",
            "CT-COST-BUDGET",
            "CT-DISK-GUARD",
            "CT-NETWORK-PARTITION",
            "CT-BENCH",
            "CT-DEPLOY",
            "CT-SCHEMA-MIGRATE",
            "CT-DEGRADE-CASCADE",
            "CT-AUTONOMY",
            "CT-AGENT-QUALITY",
            "CT-PROMPT-VERSION",
            "CT-SESSION-CONFLICT",
            "CT-LEAN",
            "CT-BLUEPRINT-HEALTH",
            "CT-TRANSFER",
            "CT-KE-QUALITY",
        ),
        schemas=(),
        token_budget=1600,
        blueprint_section="§零 AI Agent 分派与阅读指南 — 跨系统管控行",
    ),
}


def lookup_ct(ct_id: str) -> list[str]:
    """根据 CT-* 编号查找使用该契约的所有系统名称。"""
    systems: list[str] = []
    for key, dispatch in DISPATCH_TABLE.items():
        if ct_id in dispatch.ct_contracts:
            systems.append(key)
    return systems


def get_dispatch(system_key: str) -> SystemDispatch | None:
    return DISPATCH_TABLE.get(system_key)


def get_ct_contracts(system_key: str) -> tuple[str, ...]:
    dispatch = DISPATCH_TABLE.get(system_key)
    if dispatch is None:
        return ()
    return dispatch.ct_contracts


def get_schemas(system_key: str) -> tuple[str, ...]:
    dispatch = DISPATCH_TABLE.get(system_key)
    if dispatch is None:
        return ()
    return dispatch.schemas


def get_token_budget(system_key: str) -> int:
    dispatch = DISPATCH_TABLE.get(system_key)
    if dispatch is None:
        return 0
    return dispatch.token_budget


def cold_start_reading(system_key: str) -> dict[str, object]:
    dispatch = DISPATCH_TABLE.get(system_key)
    if dispatch is None:
        return {"error": f"未知系统: {system_key}", "available": list(DISPATCH_TABLE.keys())}
    return {
        "system": dispatch.system_name,
        "ct_contracts": list(dispatch.ct_contracts),
        "schemas": list(dispatch.schemas),
        "estimated_tokens": dispatch.token_budget,
        "blueprint_section": dispatch.blueprint_section,
    }


def list_all_systems() -> list[str]:
    return list(DISPATCH_TABLE.keys())


def get_reading_depth(token_budget: int) -> str:
    if token_budget <= 500:
        return "紧急 — 冷启动"
    elif token_budget <= 1500:
        return "标准 — 功能开发"
    else:
        return "完整 — 架构审查"
