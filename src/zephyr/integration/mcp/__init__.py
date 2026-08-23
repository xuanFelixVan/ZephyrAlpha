# [A_module] module_id=MOD-INF-013 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md
# [TTL] permanent
"""

ZephyrAlpha MCP (Model Context Protocol) 子包。

八个 MCP 服务端通过 stdio 协议对外暴露内部系统能力：

- task_manager_server.py — TaskManagerMCP: 蓝图->任务卡拆解、任务 CRUD（FastMCP）
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 蓝图检索文本 参数
#   fields: task_description 任务描述字符串
#   code: search_blueprints(task_description) L95
# - id: I2
#   name: 返回条数 参数
#   fields: num_results 默认3
#   code: num_results=3 L95
# 层: 算法
# - id: A1
#   name_zh: ① 双栈MCP服务符号聚合
#   name_en: __init__ 聚合导出
#   intro: 把自研JSON-RPC栈与FastMCP栈的全部server类和错误码集中到包入口
#   desc: 聚合 BaseMCPServer 自研栈 + FastMCP 栈共 8+ server 类与 9 个 ERR_* 错误码（L24-88）；双栈并存是有意的渐进迁移（L18-21）
#   inputs: I1
#   outputs: MCP Server 类集 + 错误码集
# - id: A2
#   name_zh: ② 蓝图检索捷径
#   name_en: search_blueprints
#   intro: 不走MCP stdio RPC，进程内直接检索相关蓝图
#   desc: 实例化 BlueprintSearchServer 调 _find_relevant_blueprint，返回 results 列表（L95-107）
#   inputs: I1 I2
#   outputs: list[dict]（blueprint_id/blueprint_level/relevance_score/priority）
# 层: 输出
# - id: O1
#   name_zh: MCP服务面与蓝图检索结果
#   name_en: MCP servers + search_blueprints results
#   intro: 对外暴露8个MCP server入口与蓝图检索捷径
#   downstream: 无下游/内部使用（AI agent / Pipeline orchestrator 运行时调用，docstring L98）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> O1
# A2 --> O1
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
    "MCPError",
    "SentinelServer",
    "TaskManagerMCP",
    "TelemetryMCP",
    "ToolDefinition",
    "VectorMemoryServer",
    "_base_server",
    "audit_logger",
    "blueprint_search_server",
    "client_discovery",
    "doc_guard_server",
    "error_codes",
    "gate_engine_server",
    "gateway_server",
    "governance_server",
    "handoff_auto_loader",
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
