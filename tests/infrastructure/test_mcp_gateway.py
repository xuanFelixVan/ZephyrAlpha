# [A_test] module_id: SRC-TST-2044 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-661 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_mcp_gateway
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""MCP Gateway 单元测试（MOD-INF-013 §12 Phase 5）。"""


import json
import time

import pytest

from zephyr.integration.mcp._base_server import (
    ERR_TOOL_NOT_FOUND,
)
from zephyr.integration.mcp.gateway_server import MCPGateway, create_gateway
from zephyr.integration.mcp.rate_limiter import PerToolRateLimiter, RateLimiter


@pytest.fixture
def gw() -> MCPGateway:
    return create_gateway()


class TestMCPGateway:
    """Gateway 基础功能测试。"""

    def test_initialize(self, gw: MCPGateway) -> None:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
            }
        )
        result = resp.get("result", {})
        assert result.get("protocolVersion") == "2024-11-05"
        assert result.get("serverInfo", {}).get("name") == "mcp_gateway"
        assert "capabilities" in result

    def test_ping(self, gw: MCPGateway) -> None:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "ping",
            }
        )
        result = resp.get("result", {})
        assert result.get("pong") is True
        assert result.get("gateway") is True

    def test_tools_list_aggregates(self, gw: MCPGateway) -> None:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "_session_id": "test01",
            }
        )
        result = resp.get("result", {})
        assert result["count"] > 0
        assert result["source"] == "mcp_gateway_aggregated"
        assert result.get("degraded_servers") == []

    def test_tools_call_invalid_tool_returns_error(self, gw: MCPGateway) -> None:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "nonexistent.tool"},
                "_session_id": "test01",
            }
        )
        error = resp.get("error", {})
        assert error.get("code") == ERR_TOOL_NOT_FOUND

    def test_route_task_manager_tool(self, gw: MCPGateway) -> None:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "task_manager.get_task", "arguments": {"task_id": "T-2-16"}},
                "_session_id": "test01",
            }
        )
        assert resp.get("jsonrpc") == "2.0"

    def test_route_knowledge_base_tool(self, gw: MCPGateway) -> None:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "knowledge_base.health_check", "arguments": {}},
                "_session_id": "test01",
            }
        )
        result = resp.get("result", {})
        assert result.get("content")

    def test_gateway_own_tools_exist(self, gw: MCPGateway) -> None:
        names = gw._tools
        assert "mcp_gateway.health_status" in names
        assert "mcp_gateway.list_servers" in names
        assert "mcp_gateway.audit_stats" in names

    def test_health_status_returns_all_cbs(self, gw: MCPGateway) -> None:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "mcp_gateway.health_status", "arguments": {}},
                "_session_id": "test01",
            }
        )
        result = resp.get("result", {})
        text = result.get("content", [{}])[0].get("text", "{}")
        data = json.loads(text)
        assert data.get("status") == "operational"
        assert len(data.get("circuit_breakers", {})) > 0

    def test_list_servers_returns_all_registered(self, gw: MCPGateway) -> None:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "mcp_gateway.list_servers", "arguments": {}},
                "_session_id": "test01",
            }
        )
        result = resp.get("result", {})
        text = result.get("content", [{}])[0].get("text", "{}")
        data = json.loads(text)
        servers = data.get("servers", [])
        sids = {s["server_id"] for s in servers}
        assert "task_manager" in sids
        assert "session_handoff" in sids
        assert "intent_router" in sids

    def test_audit_stats_returns_metrics(self, gw: MCPGateway) -> None:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "mcp_gateway.audit_stats", "arguments": {"client_session_id": "test01"}},
                "_session_id": "test01",
            }
        )
        result = resp.get("result", {})
        text = result.get("content", [{}])[0].get("text", "{}")
        data = json.loads(text)
        assert "total_calls" in data


class TestCircuitBreaker:
    """断路器三态测试。"""

    def test_initial_closed(self, gw: MCPGateway) -> None:
        for sid, cb in gw._circuit_breakers.items():
            assert cb.state == "CLOSED"

    def test_failure_opens_breaker(self, gw: MCPGateway) -> None:
        cb = gw._circuit_breakers["knowledge_base"]
        for _ in range(4):
            cb.failure()
        assert cb.state == "OPEN"

    def test_allow_returns_false_when_open(self, gw: MCPGateway) -> None:
        cb = gw._circuit_breakers["knowledge_base"]
        for _ in range(5):
            cb.failure()
        assert cb.allow() is False

    def test_recovery_after_timeout(self, gw: MCPGateway) -> None:
        cb = gw._circuit_breakers["knowledge_base"]
        cb._recovery = 0.01  # 10ms for test
        for _ in range(5):
            cb.failure()
        time.sleep(0.02)
        assert cb.allow() is True
        assert cb.state == "HALF_OPEN"

    def test_success_closes_half_open(self, gw: MCPGateway) -> None:
        cb = gw._circuit_breakers["knowledge_base"]
        cb._recovery = 0.01
        for _ in range(5):
            cb.failure()
        time.sleep(0.02)
        cb.allow()
        cb.success()
        assert cb.state == "CLOSED"


class TestRateLimiterIntegration:
    """限流器集成测试。"""

    def test_acquire_under_limit(self) -> None:
        rl = RateLimiter(100.0, burst_size=100.0)
        for _ in range(50):
            assert rl.try_acquire()

    def test_reject_over_limit(self) -> None:
        rl = RateLimiter(0.1, burst_size=1.0)
        assert rl.try_acquire()
        assert not rl.try_acquire()

    def test_per_tool_buckets_independent(self) -> None:
        pt = PerToolRateLimiter(100.0, 100.0)
        assert pt.try_acquire("tool_a")
        assert pt.try_acquire("tool_b")
        stats = pt.stats()
        assert "tool_a" in stats
        assert "tool_b" in stats


class TestAuditIntegration:
    """审计日志集成测试。"""

    def test_audit_logs_call(self, gw: MCPGateway) -> None:
        gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "mcp_gateway.health_status", "arguments": {}},
                "_session_id": "test_audit",
            }
        )
        stats = gw._audit.stats("test_audit")
        assert stats["total_calls"] >= 1
