# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.dispatch_table
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ct_id 参数
#   fields: 参数 ct_id，类型注解 str
#   code: dispatch_table.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: system_key 参数
#   fields: 参数 system_key，类型注解 str
#   code: dispatch_table.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: token_budget 参数
#   fields: 参数 token_budget，类型注解 int
#   code: dispatch_table.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① lookup_ct
#   name_en: lookup_ct
#   intro: 根据 CT-* 编号查找使用该契约的所有系统名称。
#   desc: 根据 CT-* 编号查找使用该契约的所有系统名称。；源码 L309-L315
#   inputs: ct_id
#   outputs: list[str]
# - id: A2
#   name_zh: ② get_dispatch
#   name_en: get_dispatch
#   intro: get_dispatch(system_key) 源码 L318-L319
#   desc: 源码 L318-L319
#   inputs: system_key
#   outputs: SystemDispatch | None
# - id: A3
#   name_zh: ③ get_ct_contracts
#   name_en: get_ct_contracts
#   intro: get_ct_contracts(system_key) 源码 L322-L326
#   desc: 源码 L322-L326
#   inputs: system_key
#   outputs: tuple[str, ...]
# - id: A4
#   name_zh: ④ get_schemas
#   name_en: get_schemas
#   intro: get_schemas(system_key) 源码 L329-L333
#   desc: 源码 L329-L333
#   inputs: system_key
#   outputs: tuple[str, ...]
# - id: A5
#   name_zh: ⑤ get_token_budget
#   name_en: get_token_budget
#   intro: get_token_budget(system_key) 源码 L336-L340
#   desc: 源码 L336-L340
#   inputs: system_key
#   outputs: int
# - id: A6
#   name_zh: ⑥ cold_start_reading
#   name_en: cold_start_reading
#   intro: cold_start_reading(system_key) 源码 L343-L353
#   desc: 源码 L343-L353
#   inputs: system_key
#   outputs: dict[str, object]
# - id: A7
#   name_zh: ⑦ list_all_systems
#   name_en: list_all_systems
#   intro: list_all_systems() 源码 L356-L357
#   desc: 源码 L356-L357
#   inputs: 无参数
#   outputs: list[str]
# - id: A8
#   name_zh: ⑧ get_reading_depth
#   name_en: get_reading_depth
#   intro: get_reading_depth(token_budget) 源码 L360-L366
#   desc: 源码 L360-L366
#   inputs: token_budget
#   outputs: str
#   （注：A8 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: SystemDispatch | None
#   name_en: SystemDispatch | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


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
            "CT-SCRIPT-GATE",
            "CT-FEATUREFLAG",
        ),
        schemas=("Finding", "KE"),
        token_budget=1400,
        blueprint_section="§零 AI Agent 分派与阅读指南 — Script System 行",
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
