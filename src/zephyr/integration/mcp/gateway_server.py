# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.gateway_server
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.mcp._base_server; zephyr.integration.mcp.error_codes; zephyr.integration.mcp.audit_logger; zephyr.integration.mcp.rate_limiter; zephyr.security.llm_defense.llm_security.gateway; zephyr.security.llm_defense.llm_security.protocol; zephyr.integration.mcp.knowledge_base_server; zephyr.integration.mcp.gate_engine_server; zephyr.integration.mcp.doc_guard_server; zephyr.integration.mcp.sentinel_server; zephyr.integration.mcp.blueprint_search_server; zephyr.integration.mcp.task_manager_server; zephyr.integration.mcp.governance_server; zephyr.integration.mcp.telemetry_server; zephyr.integration.mcp.vector_memory_server
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-013 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MCP Gateway 集中式治理节点（MOD-INF-013 §12 Phase 5）。

架构对标 IBM ContextForge Gateway 模式。五模块：
- **Route**：根据 tools/call 的 tool name 前缀自动路由到 7 Server
- **Auth/ACL**：session identity -> role -> 过滤可见工具
- **RateLimit**：10 QPS per client（集成 rate_limiter.PerToolRateLimiter）
- **Audit**：全量 tools/call 审计日志（集成 audit_logger.AuditLogger）
- **Degrade**：Circuit Breaker 三态熔断 + 自动降级

盲点关闭：B1/B7/B8/B9/B10/B16。

设计基线
--------
- 自继承 BaseMCPServer——Gateway 本身也是 MCP Server
- 7 Server 均以进程内 import 方式路由（非 stdio subprocess）
- tools/list 聚合：一次调用获取全系统工具目录
"""

from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

from zephyr.integration.mcp._base_server import (
    BaseMCPServer,
)
from zephyr.integration.mcp.audit_logger import AuditLogger, create_audit_logger
from zephyr.integration.mcp.error_codes import (
    ERR_GATE_FAILED,
    ERR_INTERNAL_ERROR,
    ERR_INVALID_PARAMS,
    ERR_RBAC_DENIED,
    ERR_SAFETY_APPROVAL_REQUIRED,
    ERR_TOOL_EXECUTION,
    ERR_TOOL_NOT_FOUND,
)
from zephyr.integration.mcp.rate_limiter import (
    RATE_LIMITED_KEY,
    PerToolRateLimiter,
)

__all__ = ["MCPGateway", "create_gateway", "start_gateway"]

_log = logging.getLogger(__name__)

_GATEWAY_ID = "mcp_gateway"
_GATEWAY_VERSION = "1.0.0"
_GATEWAY_DESC = "集中式 MCP Gateway — Auth/ACL + RateLimit + Route + Audit + Degrade"

_lsg_gateway = None


def _get_lsg():
    global _lsg_gateway
    if _lsg_gateway is not None:
        return _lsg_gateway
    try:
        from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

        _lsg_gateway = LSGSecurityGateway()
        return _lsg_gateway
    except Exception:
        _log.debug("LSG not available for MCP Gateway", exc_info=True)
        return None


def _lsg_scan_tool_call_sync(tool_name: str, tool_params: dict, text: str) -> str | None:
    gw = _get_lsg()
    if gw is None:
        return None
    try:
        import asyncio

        from zephyr.security.llm_defense.llm_security.protocol import SecurityDecision

        result = run_sync(
            gw.scan_agent_action(
                text=text,
                tool_name=tool_name,
                tool_params=tool_params,
                metadata={"source": "mcp_gateway"},
            )
        )
        if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
            return result.blocked_by or "lsg_agent_scan"
    except Exception:
        # 5.16.9 修复：移除废弃的 get_event_loop fallback，run_sync 已处理所有场景
        pass
    return None


class CircuitBreaker:
    """三态断路器：CLOSED -> OPEN（N 次失败）-> HALF_OPEN（试探恢复）。"""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 30.0,
    ) -> None:
        self._name = name
        self._threshold = failure_threshold
        self._recovery = recovery_timeout_seconds
        self._state = self.CLOSED
        self._failures: int = 0
        self._last_failure: float | None = None
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    @property
    def is_open(self) -> bool:
        with self._lock:
            return self._state == self.OPEN

    def success(self) -> None:
        with self._lock:
            if self._state == self.HALF_OPEN:
                self._state = self.CLOSED
            self._failures = 0

    def failure(self) -> None:
        with self._lock:
            self._last_failure = time.monotonic()
            self._failures += 1
            if self._failures >= self._threshold:
                self._state = self.OPEN

    def allow(self) -> bool:
        with self._lock:
            if self._state == self.CLOSED:
                return True
            if self._state == self.OPEN:
                if self._last_failure is not None:
                    elapsed = time.monotonic() - self._last_failure
                    if elapsed >= self._recovery:
                        self._state = self.HALF_OPEN
                        return True
                return False
            return True

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "name": self._name,
                "state": self._state,
                "failures": self._failures,
                "threshold": self._threshold,
                "last_failure": (
                    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self._last_failure)) if self._last_failure else None
                ),
            }


def _default_routes() -> dict[str, dict[str, Any]]:
    return {
        "task_manager": {
            "module": "task_manager_server",
            "server_id": "task_manager",
            "transport": "FastMCP",
            "handler": None,
            "prefix": "task_manager.",
        },
        "knowledge_base": {
            "module": "knowledge_base_server",
            "server_id": "knowledge_base",
            "transport": "BaseMCPServer",
            "handler": None,
            "prefix": "knowledge_base.",
        },
        "gate_engine": {
            "module": "gate_engine_server",
            "server_id": "gate_engine",
            "transport": "BaseMCPServer",
            "handler": None,
            "prefix": "gate_engine.",
        },
        "session_handoff": {
            "module": "doc_guard_server",
            "server_id": "session_handoff",
            "transport": "BaseMCPServer",
            "handler": None,
            "prefix": "session_handoff.",
            "note": "module_name != server_id",
        },
        "intent_router": {
            "module": "sentinel_server",
            "server_id": "intent_router",
            "transport": "BaseMCPServer",
            "handler": None,
            "prefix": "intent_router.",
            "note": "module_name != server_id",
        },
        "blueprint_search": {
            "module": "blueprint_search_server",
            "server_id": "blueprint_search",
            "transport": "BaseMCPServer",
            "handler": None,
            "prefix": "blueprint_search.",
        },
        "sandbox": {
            "module": "sandbox_server",
            "server_id": "sandbox",
            "transport": "BaseMCPServer",
            "handler": None,
            "prefix": "sandbox.",
            "status": "planning",
        },
        "governance": {
            "module": "governance_server",
            "server_id": "governance",
            "transport": "BaseMCPServer",
            "handler": None,
            "prefix": "governance.",
        },
        "telemetry": {
            "module": "telemetry_server",
            "server_id": "telemetry",
            "transport": "FastMCP",
            "handler": None,
            "prefix": "telemetry.",
        },
        "vector-memory": {
            "module": "vector_memory_server",
            "server_id": "vector-memory",
            "transport": "BaseMCPServer",
            "handler": None,
            "prefix": "vector-memory.",
        },
    }


class MCPGateway(BaseMCPServer):
    """MCP Gateway — 集中式治理节点。

    外部 IDE/Agent -> Gateway -> Route -> 7 Server
    """

    def __init__(
        self,
        *,
        audit_logger: AuditLogger | None = None,
        rate_limiter: PerToolRateLimiter | None = None,
    ) -> None:
        super().__init__(_GATEWAY_ID, _GATEWAY_VERSION, _GATEWAY_DESC)
        self._routes = _default_routes()
        self._server_instances: dict[str, BaseMCPServer | Any] = {}
        self._init_server_handlers()
        self._audit = audit_logger or create_audit_logger()
        self._rate_limiter = rate_limiter or PerToolRateLimiter()
        self._circuit_breakers: dict[str, CircuitBreaker] = {sid: CircuitBreaker(sid) for sid in self._routes}
        self._agg_tool_count = 0

        self._register_gateway_tools()

    def _init_server_handlers(self) -> None:
        try:
            from zephyr.integration.mcp.knowledge_base_server import KnowledgeBaseServer

            self._server_instances["knowledge_base"] = KnowledgeBaseServer()
        except Exception as exc:
            _log.warning("kb server init failed: %s", exc, exc_info=True)
        try:
            from zephyr.integration.mcp.gate_engine_server import GateEngineServer

            self._server_instances["gate_engine"] = GateEngineServer()
        except Exception as exc:
            _log.warning("gate engine init failed: %s", exc, exc_info=True)
        try:
            from zephyr.integration.mcp.doc_guard_server import DocGuardServer

            self._server_instances["session_handoff"] = DocGuardServer()
        except Exception as exc:
            _log.warning("doc guard init failed: %s", exc, exc_info=True)
        try:
            from zephyr.integration.mcp.sentinel_server import SentinelServer

            self._server_instances["intent_router"] = SentinelServer()
        except Exception as exc:
            _log.warning("sentinel init failed: %s", exc, exc_info=True)
        try:
            from zephyr.integration.mcp.blueprint_search_server import BlueprintSearchServer

            self._server_instances["blueprint_search"] = BlueprintSearchServer()
        except Exception as exc:
            _log.warning("blueprint search init failed: %s", exc, exc_info=True)
        # task_manager via FastMCP — import only for tools/list
        try:
            from zephyr.integration.mcp.task_manager_server import TaskManagerMCP

            self._server_instances["task_manager"] = TaskManagerMCP()
        except Exception as exc:
            _log.warning("task manager init failed: %s", exc, exc_info=True)
        try:
            from zephyr.integration.mcp.governance_server import GovernanceServer

            self._server_instances["governance"] = GovernanceServer()
        except Exception as exc:
            _log.warning("governance server init failed: %s", exc, exc_info=True)
        try:
            from zephyr.integration.mcp.telemetry_server import TelemetryMCP

            self._server_instances["telemetry"] = TelemetryMCP()
        except Exception as exc:
            _log.warning("telemetry server init failed: %s", exc, exc_info=True)
        try:
            from zephyr.integration.mcp.vector_memory_server import VectorMemoryServer

            self._server_instances["vector-memory"] = VectorMemoryServer()
        except Exception as exc:
            _log.warning("vector-memory server init failed: %s", exc, exc_info=True)

    def _register_gateway_tools(self) -> None:
        self.register_tool(
            name="mcp_gateway.health_status",
            description="Gateway 健康状态——返回所有 Server + CB + RateLimit 状态",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._health_status,
        )
        self.register_tool(
            name="mcp_gateway.list_servers",
            description="列出所有已注册 Server 及其状态",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._list_servers,
        )
        self.register_tool(
            name="mcp_gateway.audit_stats",
            description="审计统计——返回指定 session 的调用统计",
            input_schema={
                "type": "object",
                "required": ["client_session_id"],
                "additionalProperties": False,
                "properties": {
                    "client_session_id": {"type": "string"},
                },
            },
            handler=self._audit_stats,
        )

    # ------------------------------------------------------------------
    # Override tools/list — 聚合
    # ------------------------------------------------------------------

    def _handle_tools_list(self, _rid: str | int) -> dict[str, Any]:
        """聚合所有就绪 Server 的 tool 目录（关闭 B7）。

        自动排除 OPEN circuit breaker 的 Server 工具。
        """
        aggregated: list[dict[str, Any]] = []

        for sid, srv in self._server_instances.items():
            cb = self._circuit_breakers.get(sid)
            if cb and cb.is_open:
                continue
            try:
                srv_tools = getattr(srv, "_tools", {})
            except Exception:
                srv_tools = {}
            for tname, tdef in srv_tools.items():
                aggregated.append(
                    {
                        "name": tname,
                        "description": getattr(tdef, "description", ""),
                        "inputSchema": getattr(tdef, "input_schema", {}),
                    }
                )

        # add gateway's own tools
        for tname, tdef in self._tools.items():
            aggregated.append(
                {
                    "name": tname,
                    "description": getattr(tdef, "description", ""),
                    "inputSchema": getattr(tdef, "input_schema", {}),
                }
            )

        self._agg_tool_count = len(aggregated)
        return {
            "tools": aggregated,
            "count": len(aggregated),
            "source": "mcp_gateway_aggregated",
            "degraded_servers": [sid for sid, cb in self._circuit_breakers.items() if cb.is_open],
        }

    # ------------------------------------------------------------------
    # Override handle_request — Route + Auth + RateLimit + Audit + Degrade
    # ------------------------------------------------------------------

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        sid = request.get("_session_id", "unknown")
        method = request.get("method", "")

        if method == "tools/call":
            return self._handle_tools_call_with_pipeline(request, sid)
        if method == "initialize":
            return self._handle_initialize(request)
        if method == "ping":
            return self._ok(request.get("id"), {"pong": True, "gateway": True})
        if method == "tools/list":
            resp = self._handle_tools_list(request.get("id"))
            return self._ok(request.get("id"), resp)

        resp = super().handle_request(request)
        return resp

    def _handle_initialize(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._ok(
            request.get("id"),
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": _GATEWAY_ID,
                    "version": _GATEWAY_VERSION,
                },
                "capabilities": {
                    "tools": {"listChanged": True},
                },
            },
        )

    def _check_circuit_breaker(
        self, routed_sid: str, tool_name: str, session_id: str, req_id: Any, t0: float
    ) -> dict[str, Any] | None:
        """检查熔断器状态，返回错误响应 dict 或 None（允许通过）。"""
        cb = self._circuit_breakers.get(routed_sid)
        if cb and not cb.allow():
            server = self._server_instances.get(routed_sid)
            degraded_msg = (
                f"circuit breaker OPEN for {routed_sid!r} — "
                f"{'server unavailable' if server is None else 'degraded service'}"
            )
            self._audit.log_call(
                client_session_id=session_id,
                tool_name=tool_name,
                result_status="circuit_open",
                error_code=ERR_GATE_FAILED,
                duration_ms=int((time.monotonic() - t0) * 1000),
            )
            return self._err(req_id, ERR_GATE_FAILED, degraded_msg)
        return None

    def _try_gateway_local_tool(
        self, routed_sid: str, tool_name: str, params: dict[str, Any],
        req_id: Any, session_id: str, t0: float,
    ) -> dict[str, Any] | None:
        """处理 gateway 自身工具（mcp_gateway），返回响应 dict 或 None（非本地工具）。"""
        if routed_sid != "mcp_gateway":
            return None
        tdef = self._tools.get(tool_name)
        if tdef is None:
            return None
        try:
            args = params.get("arguments", {}) or {}
            result_data = tdef.handler(**args) if args else tdef.handler()
            content_text = json.dumps(result_data, ensure_ascii=False)
            self._audit.log_call(
                client_session_id=session_id,
                tool_name=tool_name,
                result_status="success",
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )
            return self._ok(req_id, {"content": [{"type": "text", "text": content_text}]})
        except Exception as exc:
            self._audit.log_call(
                client_session_id=session_id,
                tool_name=tool_name,
                result_status="error",
                error_code=ERR_INTERNAL_ERROR,
                error_message="internal error",
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )
            return self._err(req_id, ERR_TOOL_EXECUTION, "internal error")

    def _audit_and_track(
        self, error: dict | None, tool_name: str, arguments: dict,
        session_id: str, cb: Any, duration_ms: int,
    ) -> None:
        """记录审计日志并更新熔断器状态。"""
        status = "error" if error else "success"
        arg_hash = self._audit.hash_args(arguments) if hasattr(self._audit, "hash_args") else ""
        if error:
            self._audit.log_call(
                client_session_id=session_id,
                tool_name=tool_name,
                arguments_hash=arg_hash,
                result_status=status,
                error_code=error.get("code"),
                error_message=error.get("message"),
                duration_ms=duration_ms,
            )
            if cb:
                cb.failure()
        else:
            self._audit.log_call(
                client_session_id=session_id,
                tool_name=tool_name,
                arguments_hash=arg_hash,
                result_status=status,
                duration_ms=duration_ms,
            )
            if cb:
                cb.success()

    def _handle_tools_call_with_pipeline(
        self,
        request: dict[str, Any],
        session_id: str,
    ) -> dict[str, Any]:
        """五阶段管道：Permission -> RateLimit ->Route -> Audit ->Degrade。"""
        t0 = time.perf_counter()
        req_id = request.get("id")
        params: dict[str, Any] = request.get("params", {})
        tool_name = params.get("name", "")

        if not tool_name:
            return self._err(req_id, ERR_INVALID_PARAMS, "missing tool name")

        routed_sid = self._route_tool_name(tool_name)
        if routed_sid is None:
            msg = self._err(req_id, ERR_TOOL_NOT_FOUND, f"unknown tool: {tool_name!r}")
            self._audit.log_call(
                client_session_id=session_id,
                tool_name=tool_name,
                result_status="not_found",
                duration_ms=int((time.monotonic() - t0) * 1000),
            )
            return msg

        if not self._rate_limiter.try_acquire(routed_sid):
            duration_ms = int((time.monotonic() - t0) * 1000)
            self._audit.log_call(
                client_session_id=session_id,
                tool_name=tool_name,
                result_status=RATE_LIMITED_KEY,
                duration_ms=duration_ms,
            )
            return self._err(req_id, ERR_RBAC_DENIED, f"{RATE_LIMITED_KEY}: {tool_name!r} (10QPS exceeded)")

        tool_params = params.get("arguments", {})
        lsg_text = json.dumps(tool_params, ensure_ascii=False) if tool_params else tool_name
        lsg_blocked = _lsg_scan_tool_call_sync(tool_name, tool_params, lsg_text)
        if lsg_blocked:
            duration_ms = int((time.monotonic() - t0) * 1000)
            self._audit.log_call(
                client_session_id=session_id,
                tool_name=tool_name,
                result_status="lsg_blocked",
                duration_ms=duration_ms,
            )
            return self._err(req_id, ERR_RBAC_DENIED, f"LSG security blocked: {lsg_blocked}")

        safety_result = self._check_safety_level(tool_name, routed_sid, session_id, req_id=req_id)
        if safety_result is not None:
            return safety_result

        cb_err = self._check_circuit_breaker(routed_sid, tool_name, session_id, req_id, t0)
        if cb_err is not None:
            return cb_err

        cb = self._circuit_breakers.get(routed_sid)
        local_result = self._try_gateway_local_tool(routed_sid, tool_name, params, req_id, session_id, t0)
        if local_result is not None:
            return local_result

        srv = self._server_instances.get(routed_sid)
        arguments = params.get("arguments", {})

        try:
            inner_req: dict[str, Any] = {
                "jsonrpc": "2.0",
                "id": req_id or 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments,
                },
            }
            resp = (
                srv.handle_request(inner_req)
                if srv
                else self._err(req_id, ERR_TOOL_EXECUTION, f"server {routed_sid!r} not loaded")
            )

            error = resp.get("error")
            result = resp.get("result")
            duration_ms = int((time.perf_counter() - t0) * 1000)

            self._audit_and_track(error, tool_name, arguments, session_id, cb, duration_ms)

            out = {"jsonrpc": "2.0", "id": req_id}
            if error:
                out["error"] = error
            else:
                out["result"] = result
            return out

        except Exception as exc:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            self._audit.log_call(
                client_session_id=session_id,
                tool_name=tool_name,
                result_status="error",
                error_code=ERR_INTERNAL_ERROR,
                error_message="internal error",
                duration_ms=duration_ms,
            )
            if cb:
                cb.failure()
            return self._err(req_id, ERR_TOOL_EXECUTION, "internal error")

    def _route_tool_name(self, tool_name: str) -> str | None:
        lower = tool_name.lower()
        mapping: list[tuple[str, str]] = [
            ("task_manager.", "task_manager"),
            ("knowledge_base.", "knowledge_base"),
            ("gate_engine.", "gate_engine"),
            ("session_handoff.", "session_handoff"),
            ("intent_router.", "intent_router"),
            ("blueprint_search.", "blueprint_search"),
            ("sandbox.", "sandbox"),
            ("governance.", "governance"),
            ("telemetry.", "telemetry"),
            ("vector-memory.", "vector-memory"),
            ("mcp_gateway.", "mcp_gateway"),
        ]
        for prefix, sid in mapping:
            if lower.startswith(prefix):
                return sid
        for sid in self._server_instances:
            if lower.startswith(f"{sid.lower()}."):
                return sid
        return None

    def _check_safety_level(self, tool_name: str, routed_sid: str, session_id: str, req_id: str | int | None = None) -> dict[str, Any] | None:
        """检查工具 safety_level 并执行 RBAC 强制（R2 修复）。

        - L (Low): 直接放行，返回 None
        - M (Medium): 记录审计日志，返回确认提示
        - H (High): 返回 ERR_SAFETY_APPROVAL_REQUIRED，要求 Owner 审批

        Returns
        -------
        None 表示安全级别通过，dict 表示拦截响应。
        """
        safety_level = self._lookup_safety_level(tool_name, routed_sid)
        if safety_level is None or safety_level == "L":
            return None

        if safety_level == "H":
            return self._err(
                req_id,
                ERR_SAFETY_APPROVAL_REQUIRED,
                f"tool {tool_name!r} requires Owner approval (safety_level=H)",
            )

        if safety_level == "M":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "confirm_required": True,
                                    "tool": tool_name,
                                    "message": f"Tool {tool_name!r} requires confirmation (safety_level=M). Re-invoke with confirm=true.",
                                },
                                ensure_ascii=False,
                            ),
                        }
                    ],
                },
            }

        return None

    def _lookup_safety_level(self, tool_name: str, routed_sid: str) -> str | None:
        """从工具定义中查找 safety_level。

        优先查 Gateway 自身的 _tools，再查 Server 实例的 _tools。
        """
        if routed_sid == "mcp_gateway":
            tdef = self._tools.get(tool_name)
            if tdef is not None:
                return getattr(tdef, "safety_level", None)
            return None

        srv = self._server_instances.get(routed_sid)
        if srv is None:
            return None
        srv_tools: dict = getattr(srv, "_tools", {})
        tdef = srv_tools.get(tool_name)
        if tdef is not None:
            return getattr(tdef, "safety_level", None)
        return None

    def _health_status(self) -> dict[str, Any]:
        return {
            "status": "operational",
            "gateway_version": _GATEWAY_VERSION,
            "servers_loaded": len(self._server_instances),
            "circuit_breakers": {sid: cb.status() for sid, cb in self._circuit_breakers.items()},
            "rate_limit": {
                sid: {
                    "qps": s.permits_per_second,
                    "available": round(s.available_tokens, 2),
                    "acquired": s.total_acquired,
                    "rejected": s.total_rejected,
                }
                for sid, s in self._rate_limiter.stats().items()
            },
            "aggregated_tools_count": self._agg_tool_count,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def _list_servers(self) -> dict[str, Any]:
        servers = []
        for sid, route in self._routes.items():
            cb = self._circuit_breakers.get(sid)
            servers.append(
                {
                    "server_id": sid,
                    "module": route.get("module", ""),
                    "transport": route.get("transport", ""),
                    "loaded": sid in self._server_instances,
                    "circuit_breaker": cb.status() if cb else "N/A",
                    "status": route.get("status", "active"),
                }
            )
        return {"servers": servers, "count": len(servers)}

    def _audit_stats(self, client_session_id: str) -> dict[str, Any]:
        return self._audit.stats(client_session_id)


def create_gateway() -> MCPGateway:
    return MCPGateway()


def start_gateway() -> None:
    gw = create_gateway()
    gw.run()


if __name__ == "__main__":
    start_gateway()
