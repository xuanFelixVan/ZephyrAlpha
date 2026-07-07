# [A_test] module_id: SRC-TST-2045 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-662 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_mcp_servers
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for 5 MCP Servers (T-3-04, B15)
==========================================
验收标准：每个 Server ≥ 3 条单元测试，合计 ≥ 15 条，覆盖：
  - BaseMCPServer: tools/list、tools/call、initialize、ping、unknown method、stdio run
  - Task Manager（FastMCP）→ tests/infrastructure/test_task_manager_mcp.py
  - KnowledgeBaseServer: search、upsert_ke、get_ke
  - GateEngineServer: run_g1_write、run_g4_contract、submit_exemption
  - DocGuardServer: create_package、validate_package、emit_manual_event
  - SentinelServer: map_intent、reload_keywords、evaluate_golden_set
"""

from __future__ import annotations

import io
import json
from typing import Any

from zephyr.integration.mcp._base_server import (
    ERR_METHOD_NOT_FOUND,
    ERR_TOOL_NOT_FOUND,
    BaseMCPServer,
)
from zephyr.integration.mcp.doc_guard_server import create_server as make_doc_server
from zephyr.integration.mcp.gate_engine_server import create_server as make_gate_server
from zephyr.integration.mcp.knowledge_base_server import (
    create_server as make_kb_server,
)
from zephyr.integration.mcp.sentinel_server import create_server as make_sentinel_server

# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def _call(server: BaseMCPServer, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """构造 JSON-RPC 请求并调用 handle_request。"""
    request: dict[str, Any] = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        request["params"] = params
    return server.handle_request(request)


def _tool_call(server: BaseMCPServer, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """调用 tools/call。"""
    return _call(server, "tools/call", {"name": tool_name, "arguments": arguments})


def _ok(response: dict[str, Any]) -> Any:
    """断言无 error 并返回 result。"""
    assert "error" not in response, f"Unexpected error: {response.get('error')}"
    return response["result"]


def _err(response: dict[str, Any]) -> dict[str, Any]:
    """断言有 error 并返回 error 字段。"""
    assert "error" in response, f"Expected error, got: {response}"
    return response["error"]


def _tool_result(server: BaseMCPServer, tool_name: str, arguments: dict[str, Any]) -> Any:
    """调用 tools/call 并解析 JSON 内容层，返回工具实际结果字典。"""
    resp = _tool_call(server, tool_name, arguments)
    result = _ok(resp)
    return json.loads(result["content"][0]["text"])


# ===========================================================================
# BaseMCPServer 测试
# ===========================================================================


class TestBaseMCPServer:
    def _make_server(self) -> BaseMCPServer:
        server = BaseMCPServer("test_server", "1.0.0", "Test server")

        def _echo(message: str) -> dict[str, Any]:
            return {"echo": message}

        server.register_tool(
            name="test_server.echo",
            description="Echo message",
            input_schema={
                "type": "object",
                "required": ["message"],
                "properties": {"message": {"type": "string"}},
            },
            handler=_echo,
        )
        server._rbac_guard = None
        return server

    def test_initialize(self) -> None:
        server = self._make_server()
        result = _ok(_call(server, "initialize"))
        assert result["serverInfo"]["name"] == "test_server"
        assert result["serverInfo"]["version"] == "1.0.0"

    def test_ping(self) -> None:
        server = self._make_server()
        result = _ok(_call(server, "ping"))
        assert result["pong"] is True

    def test_tools_list(self) -> None:
        server = self._make_server()
        result = _ok(_call(server, "tools/list"))
        assert isinstance(result["tools"], list)
        assert len(result["tools"]) == 1
        assert result["tools"][0]["name"] == "test_server.echo"

    def test_tools_call_success(self) -> None:
        server = self._make_server()
        result = _ok(_tool_call(server, "test_server.echo", {"message": "hello"}))
        content = json.loads(result["content"][0]["text"])
        assert content["echo"] == "hello"

    def test_tools_call_unknown_tool(self) -> None:
        server = self._make_server()
        err = _err(_tool_call(server, "nonexistent.tool", {}))
        assert err["code"] == ERR_TOOL_NOT_FOUND

    def test_unknown_method(self) -> None:
        server = self._make_server()
        err = _err(_call(server, "no_such_method"))
        assert err["code"] == ERR_METHOD_NOT_FOUND

    def test_stdio_run_parses_requests(self) -> None:
        server = self._make_server()
        req = json.dumps({"jsonrpc": "2.0", "id": 99, "method": "ping"}) + "\n"
        inp = io.StringIO(req)
        out = io.StringIO()
        server.run(input_stream=inp, output_stream=out)
        out.seek(0)
        response = json.loads(out.read().strip())
        assert response["id"] == 99
        assert response["result"]["pong"] is True

    def test_stdio_run_handles_invalid_json(self) -> None:
        server = self._make_server()
        inp = io.StringIO("not json\n")
        out = io.StringIO()
        server.run(input_stream=inp, output_stream=out)
        out.seek(0)
        response = json.loads(out.read().strip())
        assert "error" in response


# KnowledgeBaseServer 测试
# ===========================================================================


class TestKnowledgeBaseServer:
    def setup_method(self) -> None:
        self.server = make_kb_server(enable_rbac=False)

    def test_tools_list_has_six_tools(self) -> None:
        result = _ok(_call(self.server, "tools/list"))
        names = [t["name"] for t in result["tools"]]
        assert "knowledge_base.search" in names
        assert "knowledge_base.upsert_ke" in names
        assert "knowledge_base.get_ke" in names
        assert len(names) == 6

    def test_upsert_and_get_ke(self) -> None:
        upsert = _tool_result(
            self.server,
            "knowledge_base.upsert_ke",
            {
                "ke_id": "KE-001",
                "title": "Test Entry",
                "category": "best_practice",
                "content": "Use structlog for logging.",
                "source_file": "docs/test.md",
            },
        )
        assert upsert["ke_id"] == "KE-001"
        assert "fingerprint_sha256" in upsert

        get = _tool_result(self.server, "knowledge_base.get_ke", {"ke_id": "KE-001"})
        assert get["title"] == "Test Entry"

    def test_get_ke_not_found_returns_error(self) -> None:
        err = _err(_tool_call(self.server, "knowledge_base.get_ke", {"ke_id": "KE-999"}))
        assert "ZA-KB-0005" in err["message"]

    def test_search_returns_hits(self) -> None:
        _tool_result(
            self.server,
            "knowledge_base.upsert_ke",
            {
                "ke_id": "KE-002",
                "title": "Prompt Registry",
                "category": "best_practice",
                "content": "YAML-driven prompt template registry with token budget.",
                "source_file": "src/infra/prompt_registry.py",
            },
        )
        result = _tool_result(
            self.server,
            "knowledge_base.search",
            {
                "query_text": "YAML",
                "score_threshold": 0.0,
            },
        )
        assert result["total_scanned"] >= 1
        assert "latency_ms" in result

    def test_rebuild_index(self) -> None:
        result = _tool_result(
            self.server,
            "knowledge_base.rebuild_index",
            {
                "collection": "ke_entries",
            },
        )
        assert "chunks_indexed" in result
        assert "duration_seconds" in result

    def test_invalid_collection_returns_error(self) -> None:
        err = _err(
            _tool_call(
                self.server,
                "knowledge_base.search",
                {
                    "query_text": "test",
                    "collection": "invalid_collection",
                },
            )
        )
        assert "ZA-KB-0001" in err["message"]


# ===========================================================================
# GateEngineServer 测试
# ===========================================================================


class TestGateEngineServer:
    def setup_method(self) -> None:
        self.server = make_gate_server(enable_rbac=False)

    def test_tools_list_has_eight_tools(self) -> None:
        result = _ok(_call(self.server, "tools/list"))
        names = [t["name"] for t in result["tools"]]
        assert "gate_engine.run_g1_write" in names
        assert "gate_engine.run_g4_contract" in names
        assert len(names) == 8

    def test_g1_write_clean_path_passes(self) -> None:
        result = _tool_result(
            self.server,
            "gate_engine.run_g1_write",
            {
                "target_path": "src/zephyr/context-engine/prompt_registry.py",
                "content_preview": "# clean file",
            },
        )
        assert result["passed"] is True
        assert result["gate_id"] == "G1"

    def test_g1_write_blacklisted_path_fails(self) -> None:
        err = _err(
            _tool_call(
                self.server,
                "gate_engine.run_g1_write",
                {
                    "target_path": "scripts/archive/old_script.py",
                    "content_preview": "some content",
                },
            )
        )
        assert "ZA-GT-0001" in err["message"]

    def test_g4_contract_valid_task(self) -> None:
        result = _tool_result(
            self.server,
            "gate_engine.run_g4_contract",
            {
                "payload": {
                    "task_id": "T-2-28",
                    "phase": 2,
                    "status": "PENDING",
                    "directive": "266+325",
                },
                "model_name": "Task",
            },
        )
        assert result["passed"] is True
        assert result["errors"] == []

    def test_g4_contract_missing_field(self) -> None:
        result = _tool_result(
            self.server,
            "gate_engine.run_g4_contract",
            {
                "payload": {"task_id": "T-2-28"},
                "model_name": "Task",
            },
        )
        assert result["passed"] is False
        assert len(result["errors"]) > 0

    def test_submit_exemption_valid(self) -> None:
        result = _tool_result(
            self.server,
            "gate_engine.submit_exemption",
            {
                "check_id": "G2.4",
                "reason": "Emergency deployment override approved by owner.",
                "valid_until": "2026-12-31",
                "signer_email": "owner@example.com",
            },
        )
        assert result["accepted"] is True
        assert "EX-G2.4-" in result["exemption_id"]

    def test_submit_exemption_invalid_email(self) -> None:
        err = _err(
            _tool_call(
                self.server,
                "gate_engine.submit_exemption",
                {
                    "check_id": "G1.1",
                    "reason": "Ten characters reason here.",
                    "valid_until": "2026-12-31",
                    "signer_email": "not-an-email",
                },
            )
        )
        assert "ZA-GT-0003" in err["message"]

    def test_g3_phase_valid(self) -> None:
        result = _tool_result(
            self.server,
            "gate_engine.run_g3_phase",
            {
                "phase_id": 2,
                "target_phase": 3,
            },
        )
        assert result["passed"] is True


# ===========================================================================
# DocGuardServer 测试
# ===========================================================================


class TestDocGuardServer:
    def setup_method(self) -> None:
        self.server = make_doc_server(enable_rbac=False)

    def test_tools_list_has_five_tools(self) -> None:
        result = _ok(_call(self.server, "tools/list"))
        names = [t["name"] for t in result["tools"]]
        assert "session_handoff.create_package" in names
        assert "session_handoff.validate_package" in names
        assert len(names) == 5

    def test_create_package_basic(self) -> None:
        result = _tool_result(
            self.server,
            "session_handoff.create_package",
            {
                "from_session": "session-001",
                "to_model": "claude-sonnet",
                "completed_tasks": ["T-2-27"],
                "next_tasks": ["T-2-28", "T-3-04"],
                "open_files": ["src/zephyr/context-engine/prompt_registry.py"],
            },
        )
        assert result["from_session"] == "session-001"
        assert result["context_priority"] == "P1"

    def test_validate_package_pass(self) -> None:
        package = {
            "from_session": "session-001",
            "to_model": "claude",
            "completed_tasks": ["T-2-27"],
            "next_tasks": ["T-2-28"],
            "open_files": ["src/file.py"],
            "decisions_log": ["used structlog"],
            "blocked_items": [],
            "context_priority": "P1",
        }
        result = _tool_result(
            self.server,
            "session_handoff.validate_package",
            {
                "package": package,
            },
        )
        assert result["passed"] is True

    def test_validate_package_fail_missing_from_session(self) -> None:
        package: dict[str, Any] = {
            "from_session": "",
            "to_model": "claude",
            "completed_tasks": [],
            "next_tasks": ["T-2-28"],
            "open_files": [],
            "decisions_log": [],
            "blocked_items": [],
            "context_priority": "P1",
        }
        err = _err(
            _tool_call(
                self.server,
                "session_handoff.validate_package",
                {
                    "package": package,
                },
            )
        )
        assert "ZA-HF-0002" in err["message"]

    def test_get_carryover_empty_raises_error(self) -> None:
        err = _err(_tool_call(self.server, "session_handoff.get_carryover", {}))
        assert "ZA-HF-0003" in err["message"]

    def test_get_carryover_after_create(self) -> None:
        _tool_result(
            self.server,
            "session_handoff.create_package",
            {
                "from_session": "session-001",
                "to_model": "claude-sonnet",
                "completed_tasks": [],
                "next_tasks": [],
                "open_files": [],
            },
        )
        result = _tool_result(self.server, "session_handoff.get_carryover", {})
        assert "session_id" in result

    def test_emit_manual_event(self) -> None:
        result = _tool_result(
            self.server,
            "session_handoff.emit_manual_event",
            {
                "task_id": "T-2-28",
                "priority": "HIGH",
                "reason": "Gate P0 blocked, owner approval needed.",
            },
        )
        assert "event_id" in result
        assert "delivered_at" in result

    def test_emit_event_short_reason_fails(self) -> None:
        err = _err(
            _tool_call(
                self.server,
                "session_handoff.emit_manual_event",
                {
                    "task_id": "T-2-28",
                    "priority": "HIGH",
                    "reason": "short",
                },
            )
        )
        assert "error" in str(err).lower() or err["code"] != 0


# ===========================================================================
# SentinelServer 测试
# ===========================================================================


class TestSentinelServer:
    def setup_method(self) -> None:
        self.server = make_sentinel_server(enable_rbac=False)

    def test_tools_list_has_four_tools(self) -> None:
        result = _ok(_call(self.server, "tools/list"))
        names = [t["name"] for t in result["tools"]]
        assert "intent_router.map_intent" in names
        assert "intent_router.reload_keywords" in names
        assert "intent_router.evaluate_golden_set" in names
        assert len(names) == 4

    def test_map_intent_data_domain(self) -> None:
        result = _tool_result(
            self.server,
            "intent_router.map_intent",
            {
                "query": "帮我获取 A 股 ohlcv 日线行情数据",
            },
        )
        assert result["primary_domain"] == "D0"
        assert result["confidence"] > 0.0
        assert result["source_stage"] == "keyword"

    def test_map_intent_governance_domain(self) -> None:
        result = _tool_result(
            self.server,
            "intent_router.map_intent",
            {
                "query": "查看 KB 决策记录治理规则和审计蓝图",
            },
        )
        assert result["primary_domain"] == "D2"

    def test_map_intent_unknown_raises_error(self) -> None:
        err = _err(
            _tool_call(
                self.server,
                "intent_router.map_intent",
                {
                    "query": "xyzzy florp quux 随机测试",
                },
            )
        )
        assert "ZA-INT-0001" in err["message"]

    def test_reload_keywords_with_dict(self) -> None:
        result = _tool_result(
            self.server,
            "intent_router.reload_keywords",
            {
                "keyword_dict": {
                    "D0": ["custom_kw"],
                },
            },
        )
        assert result["domains_loaded"] == 1
        assert result["keywords_loaded"] == 1

    def test_reload_keywords_restores_default(self) -> None:
        _tool_result(
            self.server,
            "intent_router.reload_keywords",
            {
                "keyword_dict": {"D0": ["only_kw"]},
            },
        )
        _tool_result(self.server, "intent_router.reload_keywords", {})
        result = _tool_result(
            self.server,
            "intent_router.map_intent",
            {
                "query": "获取行情数据 akshare",
            },
        )
        assert result["primary_domain"] == "D0"

    def test_evaluate_golden_set(self) -> None:
        result = _tool_result(self.server, "intent_router.evaluate_golden_set", {})
        assert "top1_accuracy" in result
        assert "total" in result
        assert result["total"] >= 1
        assert 0.0 <= result["top1_accuracy"] <= 1.0

    def test_map_intent_too_long_query(self) -> None:
        err = _err(
            _tool_call(
                self.server,
                "intent_router.map_intent",
                {
                    "query": "x" * 1001,
                },
            )
        )
        assert "ZA-INT-0002" in err["message"]
