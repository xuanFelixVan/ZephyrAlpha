# [A_module] module_id=MOD-INT_mcp | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md
# [TTL] permanent
"""ZephyrAlpha MCP (Model Context Protocol) 子包。

八个 MCP 服务端通过 stdio 协议对外暴露内部系统能力：

- task_manager_server.py — TaskManagerMCP: 蓝图→任务卡拆解、任务 CRUD（FastMCP）
- knowledge_base_server.py — KnowledgeBaseServer: KE 查询/创建、健康检查（functional，内存存储）
- gate_engine_server.py — GateEngineServer: Gate 判定/熔断状态（functional，6 门禁+熔断+豁免）
- doc_guard_server.py — DocGuardServer: session_handoff 文档安全校验（functional，5 项反腐败校验，文件名≠server_id）
- sentinel_server.py — SentinelServer: intent_router 意图路由哨兵/监控（functional，3 阶段路由，文件名≠server_id）
- blueprint_search_server.py — BlueprintSearchServer: 蓝图检索
- sandbox_server.py — SandboxServer: 安全代码执行沙箱（subprocess 隔离）
- telemetry_server.py — TelemetryMCP: 系统遥测可观测性（MOD-INF-015 · health/metrics/alerts/profile/schema）

设计基线：MOD-TASK_SYSTEM §3.5 MCP 接口 + ADR-0040 Pydantic V2。

**双栈 MCP（病根说明）**：历史 ADR-0033 采用自研 JSON-RPC（``BaseMCPServer``）以便无 SDK
依赖地跑 tools；任务管理 MCP 后因多工具注册冲突与 SDK 成熟度，改用官方 ``FastMCP``。
两条路径均 speak MCP over stdio——属**有意的渐进迁移**，而非实现漏做；新 server 如无强
约束可优先 FastMCP，旧 server 保持稳定即可。
"""

from zephyr.integration.mcp._base_server import (
    ERR_GATE_FAILED,
    ERR_INTERNAL_ERROR,
    ERR_INVALID_PARAMS,
    ERR_INVALID_REQUEST,
    ERR_METHOD_NOT_FOUND,
    ERR_PARSE_ERROR,
    ERR_RBAC_DENIED,
    ERR_TOOL_EXECUTION,
    ERR_TOOL_NOT_FOUND,
    BaseMCPServer,
    MCPError,
    ToolDefinition,
)
from zephyr.integration.mcp.blueprint_search_server import BlueprintSearchServer
from zephyr.integration.mcp.doc_guard_server import DocGuardServer
from zephyr.integration.mcp.gate_engine_server import GateEngineServer
from zephyr.integration.mcp.governance_server import GovernanceServer
from zephyr.integration.mcp.knowledge_base_server import KnowledgeBaseServer
from zephyr.integration.mcp.sentinel_server import SentinelServer
from zephyr.integration.mcp.task_manager_server import TaskManagerMCP
from zephyr.integration.mcp.telemetry_server import TelemetryMCP
from zephyr.integration.mcp.vector_memory_server import VectorMemoryServer

from . import handoff_auto_loader, prompt_provider, resource_provider, sandbox_server

__all__ = [
    "ERR_GATE_FAILED",
    "ERR_INTERNAL_ERROR",
    "ERR_INVALID_PARAMS",
    "ERR_INVALID_REQUEST",
    "ERR_METHOD_NOT_FOUND",
    "ERR_PARSE_ERROR",
    "ERR_RBAC_DENIED",
    "ERR_TOOL_EXECUTION",
    "ERR_TOOL_NOT_FOUND",
    "BaseMCPServer",
    "BlueprintSearchServer",
    "DocGuardServer",
    "GateEngineServer",
    "GovernanceServer",
    "KnowledgeBaseServer",
    "MCPError",
    "SentinelServer",
    "TaskManagerMCP",
    "TelemetryMCP",
    "ToolDefinition",
    "VectorMemoryServer",
    "_base_server",
    "audit_logger",
    "blueprint_search_server",
    "doc_guard_server",
    "error_codes",
    "gate_engine_server",
    "gateway_server",
    "governance_server",
    "handoff_auto_loader",
    "knowledge_base_server",
    "prompt_provider",
    "rate_limiter",
    "resource_provider",
    "sandbox_server",
    "search_blueprints",
    "sentinel_server",
    "task_manager_server",
    "telemetry_server",
    "vector_memory_server",
]

# ------------------------------------------------------------------
# Runtime convenience — search_blueprints()
# ------------------------------------------------------------------


def search_blueprints(task_description: str, num_results: int = 3) -> list[dict[str, object]]:
    """BlueprintSearchServer 捷径——无需 MCP stdio RPC 可直接调用。

    供 AI agent / Pipeline orchestrator 在 runtime 中定位相关蓝图。
    返回列表中的每个 dict 包含 blueprint_id, blueprint_level, relevance_score, priority 等字段。

    >>> results = search_blueprints("修复 gate_engine YAML parse bug")
    >>> print(results[0]["blueprint_id"])
    'MOD-GATE_ENGINE'
    """
    server = BlueprintSearchServer()
    result = server._find_relevant_blueprint(task_description, num_results=num_results)
    return result.get("results", [])
