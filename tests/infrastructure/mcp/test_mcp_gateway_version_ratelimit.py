# [A_test] module_id: MOD-GOV_mcp_gateway_version_ratelimit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] tests.test_mcp_gateway_version_ratelimit
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""5.35 API 版本管理 + 5.36 限流与配额治本回归测试（MOD-INF-013）。

覆盖：5.35.1 路由表 mcp.json 单向生成 / 5.35.3 version 字段 / 5.35.4 APIVersionContract 接入 /
5.35.7 output_schema / 5.35.8 api_version 响应字段 / 5.36.1 限流器 canonical 归一 /
5.36.2 复合限流键 / 5.36.3 reservation 锁外 sleep / 5.36.6 配额配置加载 /
5.36.7 retry_after_seconds / 5.36.8 Permission 阶段。
"""

import asyncio

import pytest

from zephyr.integration.mcp.error_codes import (
    ERR_API_SUNSET,
    ERR_RATE_LIMITED,
    ERR_RBAC_DENIED,
)
from zephyr.integration.mcp.gateway_server import MCPGateway, create_gateway
from zephyr.integration.mcp.rate_limiter import PerToolRateLimiter
from zephyr.shared.infra.limiter import SyncTokenBucketLimiter, TokenBucketLimiter


@pytest.fixture
def gw() -> MCPGateway:
    return create_gateway()


def _call(
    gw: MCPGateway,
    tool: str,
    args: dict | None = None,
    session: str = "t-session",
    role: str | None = None,
    req_id: int = 1,
) -> dict:
    req: dict = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {"name": tool, "arguments": args or {}},
        "_session_id": session,
    }
    if role:
        req["_role"] = role
    return gw.handle_request(req)


class TestRoutesFromMcpJson:
    """5.35.1：路由表从 mcp.json server_id 单向生成，下划线命名唯一。"""

    def test_route_keys_use_underscore_server_id(self, gw: MCPGateway) -> None:
        assert "vector_memory" in gw.routes
        assert "vector-memory" not in gw.routes
        assert gw.routes["vector_memory"]["prefix"] == "vector_memory."

    def test_stdio_servers_not_inprocess_routed(self, gw: MCPGateway) -> None:
        assert "red_blue_validator" not in gw.routes

    def test_route_tool_name_resolves_vector_memory(self, gw: MCPGateway) -> None:
        assert gw.route_tool_name("vector_memory.search") == "vector_memory"

    def test_routes_carry_version(self, gw: MCPGateway) -> None:
        # 5.35.3：mcp.json servers 带 version 字段并透入路由表
        assert gw.routes["governance"]["version"] == "1.1.0"
        assert gw.routes["sandbox"]["version"] == "0.1.0"


class TestApiVersion:
    """5.35.8：响应统一携带 api_version，版本来自 mcp.json 顶层 version。"""

    def test_initialize_has_api_version(self, gw: MCPGateway) -> None:
        resp = gw.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        assert resp.get("api_version") == "1.0.0"
        assert resp["result"]["serverInfo"]["version"] == "1.0.0"

    def test_ping_has_api_version(self, gw: MCPGateway) -> None:
        resp = gw.handle_request({"jsonrpc": "2.0", "id": 1, "method": "ping"})
        assert resp.get("api_version") == "1.0.0"

    def test_tools_call_has_api_version(self, gw: MCPGateway) -> None:
        resp = _call(gw, "mcp_gateway.list_servers")
        assert resp.get("api_version") == "1.0.0"


class TestOutputSchema:
    """5.35.7：gateway 注册工具声明 output_schema 并在 tools/list 透出。"""

    def test_gateway_tools_have_output_schema(self, gw: MCPGateway) -> None:
        for name in (
            "mcp_gateway.health_status",
            "mcp_gateway.list_servers",
            "mcp_gateway.audit_stats",
        ):
            assert gw.tools[name].output_schema is not None

    def test_tools_list_includes_output_schema(self, gw: MCPGateway) -> None:
        resp = gw.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        tools = {t["name"]: t for t in resp["result"]["tools"]}
        assert "outputSchema" in tools["mcp_gateway.health_status"]


class TestCompositeRateLimitKey:
    """5.36.2：(client_id, tool_name) 复合键分桶，跨客户端隔离。"""

    def test_buckets_isolated_per_client(self) -> None:
        pt = PerToolRateLimiter(1.0, 1.0, config={})
        assert pt.try_acquire("tool_x", client_id="c1")
        assert not pt.try_acquire("tool_x", client_id="c1")
        assert pt.try_acquire("tool_x", client_id="c2")

    def test_stats_key_format(self) -> None:
        pt = PerToolRateLimiter(10.0, 30.0, config={})
        pt.try_acquire("tool_x", client_id="c1")
        assert "c1|tool_x" in pt.stats()

    def test_backward_compatible_tool_only_key(self) -> None:
        pt = PerToolRateLimiter(1.0, 1.0, config={})
        assert pt.try_acquire("tool_a")
        assert not pt.try_acquire("tool_a")
        assert pt.try_acquire("tool_b")


class TestRateLimitConfigLoading:
    """5.36.6：默认配额与 per-server 覆盖从 mcp.json 加载生效。"""

    def test_defaults_from_mcp_json(self) -> None:
        pt = PerToolRateLimiter()
        assert pt.default_qps == 10.0
        assert pt.default_burst == 30.0

    def test_per_server_override(self) -> None:
        pt = PerToolRateLimiter()
        assert pt.get_or_create("blueprint_search.find")._rate == 30.0
        assert pt.get_or_create("sandbox.execute")._rate == 2.0
        assert pt.get_or_create("task_manager.list")._rate == 10.0

    def test_explicit_values_skip_file(self) -> None:
        pt = PerToolRateLimiter(100.0, 100.0)
        assert pt.default_qps == 100.0
        assert pt.get_or_create("blueprint_search.find")._rate == 100.0


class TestRetryAfter:
    """5.36.7：限流拒绝响应携带 retry_after_seconds。"""

    def test_rejection_response_has_retry_after(self, gw: MCPGateway) -> None:
        gw.rate_limiter = PerToolRateLimiter(0.01, 1.0, config={"rate_limit": {"retry_after_header": True}})
        assert _call(gw, "mcp_gateway.list_servers").get("result")
        resp = _call(gw, "mcp_gateway.list_servers", req_id=2)
        err = resp.get("error", {})
        assert err.get("code") == ERR_RATE_LIMITED
        assert err.get("data", {}).get("retry_after_seconds", 0) > 0

    def test_retry_after_disabled_returns_zero(self) -> None:
        pt = PerToolRateLimiter(1.0, 1.0, config={"rate_limit": {"retry_after_header": False}})
        pt.try_acquire("tool_x")
        assert pt.retry_after("tool_x") == 0.0


class TestPermissionStage:
    """5.36.8：Permission 阶段按 mcp.json ACL 校验，排在 RateLimit 前。"""

    def test_reader_denied_sandbox_execute(self, gw: MCPGateway) -> None:
        resp = _call(gw, "sandbox.execute", args={"code": "pass"}, role="reader")
        assert resp.get("error", {}).get("code") == ERR_RBAC_DENIED

    def test_admin_passes_permission(self, gw: MCPGateway) -> None:
        resp = _call(gw, "sandbox.execute", args={"code": "pass"}, role="admin")
        # admin 通过 Permission（后续被 safety_level=H 拦截或执行），不是 RBAC_DENIED
        assert resp.get("error", {}).get("code") != ERR_RBAC_DENIED

    def test_operator_inherits_reader(self, gw: MCPGateway) -> None:
        resp = _call(gw, "governance.list_skills", role="operator")
        assert resp.get("result") is not None

    def test_gateway_own_tools_no_acl_allowed(self, gw: MCPGateway) -> None:
        resp = _call(gw, "mcp_gateway.list_servers")
        assert resp.get("result") is not None

    def test_default_role_is_operator(self, gw: MCPGateway) -> None:
        # 未声明 _role 时按 role_assignment.ai_agent_default=operator 解析
        resp = _call(gw, "governance.list_skills")
        assert resp.get("result") is not None


class TestVersionContract:
    """5.35.4：APIVersionContract 接入管道——sunset 已过工具被拦截。"""

    def test_sunset_tool_blocked(self, gw: MCPGateway) -> None:
        gw.register_tool(
            name="mcp_gateway.old_tool",
            description="d",
            input_schema={"type": "object", "properties": {}},
            handler=lambda: {},
            deprecated=True,
            sunset_date="2020-01-01",
            replacement="mcp_gateway.health_status",
        )
        resp = _call(gw, "mcp_gateway.old_tool")
        assert resp.get("error", {}).get("code") == ERR_API_SUNSET

    def test_deprecated_not_sunset_allowed(self, gw: MCPGateway) -> None:
        gw.register_tool(
            name="mcp_gateway.dep_tool",
            description="d",
            input_schema={"type": "object", "properties": {}},
            handler=lambda: {"ok": True},
            deprecated=True,
            sunset_date="2099-01-01",
        )
        resp = _call(gw, "mcp_gateway.dep_tool")
        assert resp.get("result") is not None


class TestCanonicalLimiters:
    """5.36.1 canonical 归一 + 5.36.3 reservation 锁外 sleep。"""

    def test_sync_token_bucket_basic(self) -> None:
        rl = SyncTokenBucketLimiter(1.0, burst_size=1.0)
        assert rl.try_acquire()
        assert not rl.try_acquire()
        assert rl.retry_after_seconds() > 0
        assert rl.stats().total_rejected == 1

    def test_mcp_rate_limiter_delegates_canonical(self) -> None:
        from zephyr.integration.mcp.rate_limiter import RateLimiter

        assert issubclass(RateLimiter, SyncTokenBucketLimiter)

    def test_async_reservation_lock_free_sleep(self) -> None:
        async def run() -> object:
            limiter = TokenBucketLimiter(20.0, burst_size=1.0)
            await limiter.acquire()  # 立即获取
            await asyncio.gather(*(limiter.acquire() for _ in range(3)))  # 预支排队
            return limiter.stats()

        stats = asyncio.run(run())
        assert stats.total_acquired == 4
        assert stats.total_waited == 3

    def test_a2a_delegation_per_key(self) -> None:
        from zephyr.infrastructure.a2a_protocol.governance.rate_limiter import (
            RateLimiter as A2ARateLimiter,
        )

        rl = A2ARateLimiter(max_requests=2, window_seconds=60)
        assert rl.allow("agent-1")
        assert rl.allow("agent-1")
        assert not rl.allow("agent-1")
        assert rl.allow("agent-2")  # per-key 隔离
        rl.reset("agent-1")
        assert rl.allow("agent-1")
