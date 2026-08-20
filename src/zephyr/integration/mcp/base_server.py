# [A_module] module_id=SH-INF-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md
# [TTL] permanent
"""公共模块别名（R5 公共化）— 从 _base_server 重新导出所有公共符号。

测试通过 ``from zephyr.integration.mcp.base_server import BaseMCPServer`` 导入，
本模块提供公共路径，实际实现在 ``_base_server.py``。
"""

from zephyr.integration.mcp._base_server import (  # noqa: F401
    ERR_GATE_FAILED,
    ERR_INTERNAL_ERROR,
    ERR_INVALID_PARAMS,
    ERR_INVALID_REQUEST,
    ERR_METHOD_NOT_FOUND,
    ERR_PARSE_ERROR,
    ERR_RBAC_DENIED,
    ERR_TOOL_EXECUTION,
    ERR_TOOL_NOT_FOUND,
    JSONRPC_VERSION,
    MCP_PROTOCOL_VERSION,
    BaseMCPServer,
    MCPError,
    ToolDefinition,
    __all__,
)
