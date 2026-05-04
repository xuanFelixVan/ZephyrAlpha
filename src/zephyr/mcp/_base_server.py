# AI-generated: JSON-RPC 2.0 over stdio MCP base server (ADR-0033)
"""
BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类
==================================================
Task ID  : T-3-04 (B15) 共享基础设施
Protocol : ADR-0033（stdio 传输、JSON-RPC 2.0）
Spec     : MCP/0.3

职责
----
- 封装 JSON-RPC 2.0 解析/响应逻辑
- 提供 tools/list 和 tools/call 标准方法
- initialize / ping 握手支持
- 子类通过 register_tool() 注册工具处理函数
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TextIO

import structlog

__all__ = [
    "BaseMCPServer",
    "ToolDefinition",
    "MCPError",
    "ERR_PARSE_ERROR",
    "ERR_INVALID_REQUEST",
    "ERR_METHOD_NOT_FOUND",
    "ERR_INVALID_PARAMS",
    "ERR_INTERNAL_ERROR",
    "ERR_TOOL_NOT_FOUND",
    "ERR_TOOL_EXECUTION",
]

JSONRPC_VERSION = "2.0"
MCP_PROTOCOL_VERSION = "2024-11-05"

# ---------------------------------------------------------------------------
# 标准 JSON-RPC 错误码
# ---------------------------------------------------------------------------

ERR_PARSE_ERROR = -32700
ERR_INVALID_REQUEST = -32600
ERR_METHOD_NOT_FOUND = -32601
ERR_INVALID_PARAMS = -32602
ERR_INTERNAL_ERROR = -32603

# MCP 扩展错误码
ERR_TOOL_NOT_FOUND = -32001
ERR_TOOL_EXECUTION = -32002

class MCPError(Exception):
    """MCP 协议层错误，携带 JSON-RPC error code。"""

    def __init__(self, code: int, message: str, data: Any | None = None) -> None:
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

# ---------------------------------------------------------------------------
# 工具定义
# ---------------------------------------------------------------------------

@dataclass
class ToolDefinition:
    """MCP Tool 的完整定义。"""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Any]

# ---------------------------------------------------------------------------
# 基类
# ---------------------------------------------------------------------------

class BaseMCPServer:
    """JSON-RPC 2.0 over stdio MCP Server 基类。

    ADR-0033：stdio 传输，JSON-RPC 2.0 协议。

    子类使用示例
    -----------
    ::

        class MyServer(BaseMCPServer):
            def __init__(self):
                super().__init__("my_server", "1.0.0", "描述")
                self.register_tool(
                    name="my_server.do_something",
                    description="做某件事",
                    input_schema={"type": "object", "properties": {"arg": {"type": "string"}}},
                    handler=self._do_something,
                )

            def _do_something(self, arg: str) -> dict[str, Any]:
                return {"result": arg}
    """

    def __init__(
        self,
        server_id: str,
        version: str,
        description: str,
    ) -> None:
        self.server_id = server_id
        self.version = version
        self.description = description
        self._tools: dict[str, ToolDefinition] = {}
        self._log = structlog.get_logger().bind(
            layer="mcp",
            module=server_id,
            operation="server",
        )

    # ------------------------------------------------------------------
    # 工具注册
    # ------------------------------------------------------------------

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        """注册一个 MCP Tool。

        Parameters
        ----------
        name:
            工具全名，约定格式 ``{server_id}.{action}``。
        description:
            工具用途说明（MCP tools/list 中展示）。
        input_schema:
            JSON Schema（type: object），描述工具参数。
        handler:
            Python 可调用对象，接收参数后返回可序列化结果。
        """
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
        )

    @property
    def tool_names(self) -> list[str]:
        """已注册工具名称列表。"""
        return list(self._tools.keys())

    # ------------------------------------------------------------------
    # JSON-RPC 响应构造
    # ------------------------------------------------------------------

    def _ok(self, req_id: Any, result: Any) -> dict[str, Any]:
        return {"jsonrpc": JSONRPC_VERSION, "id": req_id, "result": result}

    def _err(
        self,
        req_id: Any,
        code: int,
        message: str,
        data: Any | None = None,
    ) -> dict[str, Any]:
        error: dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return {"jsonrpc": JSONRPC_VERSION, "id": req_id, "error": error}

    # ------------------------------------------------------------------
    # 请求路由
    # ------------------------------------------------------------------

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """处理单个 JSON-RPC 请求，返回响应字典。"""
        req_id = request.get("id")
        method: str = request.get("method", "")
        params: dict[str, Any] = request.get("params") or {}

        self._log.debug("request_received", method=method, req_id=req_id)

        if method == "initialize":
            return self._handle_initialize(req_id)
        if method == "ping":
            return self._ok(req_id, {"pong": True})
        if method == "tools/list":
            return self._handle_tools_list(req_id)
        if method == "tools/call":
            return self._handle_tools_call(req_id, params)
        return self._err(req_id, ERR_METHOD_NOT_FOUND, f"Unknown method: {method!r}")

    def _handle_initialize(self, req_id: Any) -> dict[str, Any]:
        return self._ok(
            req_id,
            {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": self.server_id,
                    "version": self.version,
                    "description": self.description,
                },
            },
        )

    def _handle_tools_list(self, req_id: Any) -> dict[str, Any]:
        tools = [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": t.input_schema,
            }
            for t in self._tools.values()
        ]
        return self._ok(req_id, {"tools": tools})

    def _handle_tools_call(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        tool_name: str = params.get("name", "")
        arguments: dict[str, Any] = params.get("arguments") or {}

        tool = self._tools.get(tool_name)
        if tool is None:
            return self._err(req_id, ERR_TOOL_NOT_FOUND, f"Tool not found: {tool_name!r}")

        try:
            result = tool.handler(**arguments)
            content = [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
            return self._ok(req_id, {"content": content, "isError": False})
        except TypeError as exc:
            return self._err(req_id, ERR_INVALID_PARAMS, f"Invalid params: {exc}")
        except MCPError as exc:
            return self._err(req_id, exc.code, exc.message, exc.data)
        except Exception as exc:
            self._log.error("tool_execution_error", tool=tool_name, error=str(exc))
            return self._err(req_id, ERR_TOOL_EXECUTION, str(exc))

    # ------------------------------------------------------------------
    # 主循环（stdio）
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ) -> None:
        """启动 stdio 主循环，逐行读取 JSON-RPC 请求并写出响应。

        Parameters
        ----------
        input_stream:
            默认 sys.stdin（测试时可传入 StringIO）。
        output_stream:
            默认 sys.stdout（测试时可传入 StringIO）。
        """
        inp: TextIO = input_stream or sys.stdin
        out: TextIO = output_stream or sys.stdout

        self._log.info("server_started", server_id=self.server_id, version=self.version)

        for raw_line in inp:
            line = raw_line.strip()
            if not line:
                continue

            try:
                request: Any = json.loads(line)
            except json.JSONDecodeError as exc:
                resp = self._err(None, ERR_PARSE_ERROR, f"Parse error: {exc}")
                out.write(json.dumps(resp, ensure_ascii=False) + "\n")
                out.flush()
                continue

            if not isinstance(request, dict):
                resp = self._err(None, ERR_INVALID_REQUEST, "Request must be a JSON object")
                out.write(json.dumps(resp, ensure_ascii=False) + "\n")
                out.flush()
                continue

            response = self.handle_request(request)
            out.write(json.dumps(response, ensure_ascii=False) + "\n")
            out.flush()

        self._log.info("server_stopped", server_id=self.server_id)
