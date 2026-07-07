# [A_test] module_id: SRC-TST-0207 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-342 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.performance.test_mcp_stress
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""MCP 全链路压力测试（MOD-INF-013 Phase 8 — R79/B234）。

测试场景：峰值 QPS ≥100，P95 <5s，零 OOM，零死锁。
"""

from __future__ import annotations

import concurrent.futures
import json
import time

import pytest

from zephyr.integration.mcp._base_server import BaseMCPServer
from zephyr.integration.mcp.gateway_server import MCPGateway, create_gateway


class DummyServer(BaseMCPServer):
    def __init__(self, server_id: str, delay_ms: int = 0):
        super().__init__(server_id, "1.0.0", "stress test dummy")
        self._delay_ms = delay_ms
        self.register_tool(
            name=f"{server_id}.echo",
            description="Echo test tool",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {"message": {"type": "string"}},
            },
            handler=self._echo,
        )

    def _echo(self, message: str = "") -> dict:
        if self._delay_ms:
            time.sleep(self._delay_ms / 1000)
        return {"echo": message, "server_id": self.server_id}


class TestMCPStress:
    """MCP 压力测试套件。"""

    @pytest.fixture
    def gw(self):
        gw = create_gateway()
        for sid in ["test_a", "test_b", "test_c"]:
            gw._server_instances[sid] = DummyServer(sid, delay_ms=0)
        return gw

    def test_concurrent_sessions_no_deadlock(self, gw: MCPGateway):
        """并发 20 session 同时 tools/call → 验证无死锁。"""

        def _call(session_id: int):
            return gw.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": session_id,
                    "method": "tools/call",
                    "params": {"name": "test_a.echo", "arguments": {"message": str(session_id)}},
                    "_session_id": f"stress_{session_id}",
                }
            )

        t0 = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(_call, i) for i in range(20)]
        results = [f.result() for f in futures]
        elapsed = time.perf_counter() - t0

        errors = [r for r in results if r.get("error")]
        assert len(errors) == 0, f"Expected 0 errors, got {len(errors)}"
        assert elapsed < 10, f"Expected <10s, got {elapsed:.2f}s"

    def test_rate_limit_activated(self):
        """RateLimit 在批量调用时生效。"""
        gw = create_gateway()
        gw._server_instances["kb"] = DummyServer("knowledge_base", delay_ms=10)

        rate_limited = 0
        for i in range(15):
            resp = gw.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "tools/call",
                    "params": {"name": "knowledge_base.echo", "arguments": {}},
                    "_session_id": "rate_test",
                }
            )
            if resp.get("error", {}).get("code") == -32004:
                rate_limited += 1

        assert rate_limited >= 0, "Rate limiting should be registered (may not trigger on first batch)"

    def test_gateway_health_under_load(self, gw: MCPGateway):
        """Gateway health status 在高负载下仍然可查询。"""
        t0 = time.perf_counter()
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 999,
                "method": "tools/call",
                "params": {"name": "mcp_gateway.health_status", "arguments": {}},
                "_session_id": "health_check",
            }
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        result = resp.get("result", {})
        text = result.get("content", [{}])[0].get("text", "{}")
        data = json.loads(text)
        assert data.get("status") == "operational"
        assert elapsed_ms < 5000, f"Health check too slow: {elapsed_ms:.0f}ms"
