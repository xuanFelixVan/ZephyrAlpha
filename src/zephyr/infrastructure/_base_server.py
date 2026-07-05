# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/mcp-servers/blueprint.md
# [MODULE] zephyr.infrastructure._base_server
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF__base_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: JSON-RPC 2.0 over stdio MCP base server (
"""
BaseMCPServer: stdio 传输 + JSON-RPC 2.0 协议基类
==================================================
Task ID  : T-3-04 (B15) 共享基础设施
Protocol :  传输、JSON-RPC 2.0）
Spec     : MCP/0.3

职责
----
- 封装 JSON-RPC 2.0 解析/响应逻辑
- 提供 tools/list 和 tools/call 标准方法
- initialize / ping 握手支持
- 子类通过 register_tool() 注册工具处理函数
- Content-Length 帧格式支持（MCP 2024-11-05 规范）

MCP 原语覆盖表
--------------
| 原语 | 实现状态 | 备注 |
|------|:---:|------|
| ``initialize`` | ✅ | 返回 capabilities + serverInfo |
| ``ping`` | ✅ | 返回 {"pong": true} |
| ``tools/list`` | ✅ | 返回所有注册工具定义 |
| ``tools/call`` | ✅ | 执行工具 handler，返回 MCP content |
| ``resources/list`` | ✅ | resource_provider.py 已实现 |
| ``resources/read`` | ✅ | resource_provider.py read() 已实现 |
| ``prompts/list`` | ✅ | prompt_provider.py 已实现 |
| ``prompts/get`` | ✅ | prompt_provider.py get() 已实现 |
| ``notifications/message`` | ❌ | 未实现（Server→Client 通知） |

错误码体系
----------
错误码集中定义于 ``zephyr.infrastructure.error_codes``（MOD-INF-013 §3.4）。
标准 JSON-RPC 码：-32700 ~ -32603。
MCP 扩展码：-32001(ERR_TOOL_NOT_FOUND) / -32002(ERR_TOOL_EXECUTION) /
           -32003(ERR_GATE_FAILED) / -32004(ERR_RBAC_DENIED)。

双栈 MCP 说明
-------------
- BaseMCPServer（本类）：自研 JSON-RPC 2.0，供 knowledge_base / gate_engine /
  doc_guard(session_handoff) / sentinel(intent_router) / blueprint_search 使用。
- FastMCP（task_manager_server.py）：官方 mcp SDK，task_manager MCP 使用。
- 两条路径均 speak MCP over stdio——属有意的渐进迁移，而非实现漏做。
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TextIO

import structlog
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

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
    "MCPError",
    "ToolDefinition",
]

JSONRPC_VERSION = "2.0"
MCP_PROTOCOL_VERSION = "2024-11-05"

import asyncio

from zephyr.infrastructure.error_codes import (
    ERR_GATE_FAILED,
    ERR_INTERNAL_ERROR,
    ERR_INVALID_PARAMS,
    ERR_INVALID_REQUEST,
    ERR_METHOD_NOT_FOUND,
    ERR_PARSE_ERROR,
    ERR_RBAC_DENIED,
    ERR_TOOL_EXECUTION,
    ERR_TOOL_NOT_FOUND,
)


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
    safety_level: str = "L"


# ---------------------------------------------------------------------------
# 基类
# ---------------------------------------------------------------------------


class BaseMCPServer:
    """JSON-RPC 2.0 over stdio MCP Server 基类。

     传输，JSON-RPC 2.0 协议。

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
        *,
        enable_rbac: bool = True,
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
        self._rbac_guard = None
        self._agent_session_id: str = ""
        if enable_rbac:
            self._try_auto_enable_rbac()

    def _try_auto_enable_rbac(self) -> None:
        # 5.17.8 修复：翻转默认为 True（default-deny），未声明权限的 server 拒绝所有写
        if not getattr(self, "_AUTO_ENABLE_RBAC", True):
            return
        try:
            from zephyr.governance.agent_spec.rbac_bridge import EscalationRBACBridge

            self._rbac_guard = EscalationRBACBridge()
            self._agent_session_id = self.server_id
        except Exception as e:
            logger.warning("suppressed error in _base_server", exc_info=True)

    def enable_rbac(self, session_id: str = "") -> None:
        self._agent_session_id = session_id
        try:
            from zephyr.governance.agent_spec.rbac_bridge import EscalationRBACBridge

            self._rbac_guard = EscalationRBACBridge()
            self._log.info("rbac_enabled", session_id=session_id or "auto-detect")
        except ImportError:
            self._log.warning("rbac_unavailable", reason="rbac_bridge import failed")

    def disable_rbac(self) -> None:
        self._rbac_guard = None
        self._log.info("rbac_disabled")

    # ------------------------------------------------------------------
    # 工具注册
    # ------------------------------------------------------------------

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable[..., Any],
        *,
        safety_level: str = "L",
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
        safety_level:
            L = Low（直接执行）
            M = Medium（返回确认提示）
            H = High（返回 Owner approval required）
            与 MOD-INF-018 RBAC 对齐。
        """
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
            safety_level=safety_level,
        )

    @property
    def tool_names(self) -> list[str]:
        """已注册工具名称列表。"""
        return list(self._tools.keys())

    @classmethod
    def register_tool_decorator(
        cls,
        name: str,
        description: str,
        input_schema: dict[str, Any],
    ):
        """类级别工具注册装饰器（解决 R7 copy-paste 问题）。

        用法::

            class MyServer(BaseMCPServer):
                SERVER_ID = "my_server"

                @BaseMCPServer.register_tool_decorator(
                    name="my_server.hello",
                    description="Say hello",
                    input_schema={"type": "object", "properties": {}},
                )
                def hello(self):
                    return {"message": "hello"}

        在 ``__init_subclass__`` 或 ``__init__`` 中调用 ``_install_decorated_tools()``
        自动注册所有被装饰的方法。
        """

        def decorator(handler: Callable[..., Any]) -> Callable[..., Any]:
            handler._mcp_tool_meta = {
                "name": name,
                "description": description,
                "input_schema": input_schema,
            }
            return handler

        return decorator

    def _install_decorated_tools(self) -> None:
        """扫描自身方法，自动注册被 ``@register_tool_decorator`` 装饰的工具。"""
        for attr_name in dir(self):
            attr = getattr(self, attr_name, None)
            if callable(attr) and hasattr(attr, "_mcp_tool_meta"):
                meta = attr._mcp_tool_meta
                self.register_tool(
                    name=meta["name"],
                    description=meta["description"],
                    input_schema=meta["input_schema"],
                    handler=attr,
                )

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

        level = getattr(tool, "safety_level", "L")
        if level == "H":
            return self._err(
                req_id,
                ERR_RBAC_DENIED,
                f"Tool {tool_name!r} requires Owner approval (safety_level=H). "
                f"Submit exemption in MOD-INF-018 before retry.",
            )
        if level == "M":
            return self._ok(
                req_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "confirmation_required": True,
                                    "tool": tool_name,
                                    "message": f"Confirm execution of {tool_name!r} (safety_level=M)",
                                },
                                ensure_ascii=False,
                            ),
                        }
                    ],
                    "isError": False,
                },
            )

        if self._rbac_guard is not None:
            sid = self._agent_session_id or self.server_id
            rbac_result = self._rbac_guard.pre_execute_check(sid, f"mcp:{tool_name}", "")
            if not rbac_result.passed:
                return self._err(
                    req_id,
                    ERR_RBAC_DENIED,
                    f"RBAC blocked {tool_name!r}: {rbac_result.reason} "
                    f"(layer={rbac_result.layer}, rule={rbac_result.rule_id})",
                )

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
            return self._err(req_id, ERR_TOOL_EXECUTION, "internal error")

    # ------------------------------------------------------------------
    # 主循环（stdio）
    # ------------------------------------------------------------------

    @staticmethod
    def _read_message(inp: TextIO) -> tuple[str | None, bool]:
        """从输入流读取一条 JSON-RPC 消息。

        支持两种格式：
        1. Content-Length 帧（MCP 2024-11-05 规范）：
           先读 ``Content-Length: N\\r\\n\\r\\n`` 头，再读 N 字节 body。
        2. Legacy 逐行模式（向后兼容）：
           如果首行不是 Content-Length 头，回退到 ``readline()``。

        Returns
        -------
        (body_str, used_cl):
            body_str 为消息体字符串，EOF 时返回 None。
            used_cl 为 True 表示使用了 Content-Length 帧格式。
        """
        first_line = inp.readline()
        if not first_line:
            return None, False

        stripped = first_line.strip()
        if stripped.startswith("Content-Length:"):
            try:
                content_length = int(stripped.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                return first_line.strip(), False

            # 5.147.3 修复: Content-Length 无上限, 恶意客户端可发送超大值触发 OOM Kill。
            # 设定 MAX_MESSAGE_BYTES=10MB 上限, 超限返回错误
            MAX_MESSAGE_BYTES = 10 * 1024 * 1024  # 10MB
            if content_length > MAX_MESSAGE_BYTES:
                return f"ERROR: Content-Length {content_length} exceeds limit {MAX_MESSAGE_BYTES}", False

            inp.readline()

            body = inp.read(content_length)
            return body.strip(), True

        return stripped, False

    def run(
        self,
        *,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ) -> None:
        """启动 stdio 主循环，读取 JSON-RPC 请求并写出响应。

        支持 Content-Length 帧格式（MCP 2024-11-05）和 legacy 逐行格式。

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

        while True:
            line, _used_cl = self._read_message(inp)
            if line is None:
                break
            if not line:
                continue

            try:
                request: object = json.loads(line)
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

    async def run_async(
        self,
        *,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ) -> None:
        """启动 asyncio stdio 主循环（非阻塞 I/O），解决 R1 stdio 单线程阻塞风险。

        使用 ``loop.run_in_executor`` 将阻塞的 ``readline()`` 委托到线程池，
        使事件循环在等待 stdin 时可调度其他协程。

        用法::

            import asyncio
            run_sync(server.run_async())

        Parameters
        ----------
        input_stream:
            默认 sys.stdin（测试时可传入 StringIO）。
        output_stream:
            默认 sys.stdout（测试时可传入 StringIO）。
        """
        loop = asyncio.get_running_loop()
        inp: TextIO = input_stream or sys.stdin
        out: TextIO = output_stream or sys.stdout

        self._log.info("server_started", server_id=self.server_id, version=self.version, mode="async")

        while True:
            line = await loop.run_in_executor(None, inp.readline)
            if not line:
                break

            decoded = line.strip()
            if not decoded:
                continue

            try:
                request: object = json.loads(decoded)
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

        self._log.info("server_stopped", server_id=self.server_id, mode="async")
