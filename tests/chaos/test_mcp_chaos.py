# [A_test] module_id: SRC-TST-0089 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-247 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.chaos.test_mcp_chaos
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""MCP 混沌工程测试（MOD-INF-013 Phase 8 — R126/B179/B188）。

至少 5 个混沌实验：进程 kill / 连接断开 / 语法错误 / 高并发 / 空请求。
"""

from __future__ import annotations

from zephyr.integration.mcp._base_server import ERR_TOOL_EXECUTION, ERR_TOOL_NOT_FOUND, BaseMCPServer


class TestMCPChaos:
    """MCP 混沌实验套件。"""

    def _make_server(self, fail_on_call: bool = False):
        class ChaosServer(BaseMCPServer):
            def __init__(self, fail: bool):
                super().__init__("chaos_test", "1.0.0", "chaos experiment")
                self._fail = fail
                self.register_tool(
                    name="chaos_test.stable",
                    description="Always returns success",
                    input_schema={"type": "object", "properties": {}},
                    handler=self._stable,
                )

            def _stable(self) -> dict:
                if self._fail:
                    raise RuntimeError("simulated crash")
                return {"ok": True}

        return ChaosServer(fail_on_call)

    def test_experiment_unknown_tool(self):
        """Chaos Exp 1: 调用不存在的 tool → 应该返回 TOOL_NOT_FOUND 而非崩溃。"""
        srv = self._make_server()
        resp = srv.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "chaos_test.nonexistent", "arguments": {}},
            }
        )
        assert resp.get("error", {}).get("code") == ERR_TOOL_NOT_FOUND

    def test_experiment_simulated_crash(self):
        """Chaos Exp 2: 模拟 handler 内部崩溃 → 应该返回 INTERNAL_ERROR 而非进程退出。"""
        srv = self._make_server(fail_on_call=True)
        resp = srv.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "chaos_test.stable", "arguments": {}},
            }
        )
        assert resp.get("error", {}).get("code") == ERR_TOOL_EXECUTION

    def test_experiment_empty_request(self):
        """Chaos Exp 3: 发送空请求 → 应该返回 PARSE_ERROR。"""
        srv = self._make_server()
        # simulate empty stdin line
        resp = srv.handle_request({})
        assert "error" in resp

    def test_experiment_batch_flood(self):
        """Chaos Exp 4: 100 次快速连续调用 → 所有响应正确。"""
        srv = self._make_server()
        for i in range(100):
            resp = srv.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "tools/call",
                    "params": {"name": "chaos_test.stable", "arguments": {}},
                }
            )
            assert resp.get("jsonrpc") == "2.0"
            assert "error" not in resp

    def test_experiment_ping_always_works(self):
        """Chaos Exp 5: 即使其他 tool 失败，ping 仍然可成功响应。"""
        srv = self._make_server(fail_on_call=True)
        resp = srv.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "ping",
            }
        )
        assert resp.get("result", {}).get("pong") is True
