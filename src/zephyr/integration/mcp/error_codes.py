# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.error_codes
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INT_error_codes | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MCP 错误码集中注册（MOD-INF-013 §3.4）。

本文件是 MCP 协议错误码的 canonical SSoT。
_base_server.py 中的硬编码错误码已迁移至此处导入。
"""

from __future__ import annotations

from typing import Final
ERR_PARSE_ERROR: Final[int] = -32700
ERR_INVALID_REQUEST: Final[int] = -32600
ERR_METHOD_NOT_FOUND: Final[int] = -32601
ERR_INVALID_PARAMS: Final[int] = -32602
ERR_INTERNAL_ERROR: Final[int] = -32603

ERR_TOOL_NOT_FOUND: Final[int] = -32001
ERR_TOOL_EXECUTION: Final[int] = -32002
ERR_GATE_FAILED: Final[int] = -32003
ERR_RBAC_DENIED: Final[int] = -32004
ERR_SAFETY_APPROVAL_REQUIRED: Final[int] = -32005

__all__ = [
    "ERR_GATE_FAILED",
    "ERR_INTERNAL_ERROR",
    "ERR_INVALID_PARAMS",
    "ERR_INVALID_REQUEST",
    "ERR_METHOD_NOT_FOUND",
    "ERR_PARSE_ERROR",
    "ERR_RBAC_DENIED",
    "ERR_SAFETY_APPROVAL_REQUIRED",
    "ERR_TOOL_EXECUTION",
    "ERR_TOOL_NOT_FOUND",
]

_MESSAGE_MAP: dict[int, str] = {
    ERR_PARSE_ERROR: "Parse error",
    ERR_INVALID_REQUEST: "Invalid Request",
    ERR_METHOD_NOT_FOUND: "Method not found",
    ERR_INTERNAL_ERROR: "Internal error",
    ERR_INVALID_PARAMS: "Invalid params",
    ERR_TOOL_NOT_FOUND: "Tool not found",
    ERR_TOOL_EXECUTION: "Tool execution error",
    ERR_GATE_FAILED: "Gate check failed",
    ERR_RBAC_DENIED: "RBAC permission denied",
    ERR_SAFETY_APPROVAL_REQUIRED: "Safety approval required",
}


def error_message(code: int) -> str:
    return _MESSAGE_MAP.get(code, f"Unknown error code: {code}")


def lookup(code: int) -> str:
    return _MESSAGE_MAP.get(code, f"UNKNOWN_{abs(code)}")
