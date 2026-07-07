# [A_test] module_id: SRC-TST-0171 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-328 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_mcp_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
# AI-generated: MCP E2E lifecycle + protocol compliance tests (T-3-05, B16)
"""
MCP 端到端测试 — T-3-05 (B16)
==============================
任务 ID : T-3-05 (B16)
依赖    : B15 ✅（5 MCP Server 已包装）
验收标准：
  - 5 个 Server 完整生命周期测试（initialize → tools/list → tools/call）
  - JSON-RPC 2.0 协议合规性验证（id 匹配、错误码、content-type）
  - stdio 传输层模拟测试
  - 跨 Server 调用链测试（task_manager → gate_engine → knowledge_base）
  - ≥ 20 条单元测试

测试矩阵
--------
ProtocolCompliance  : id 匹配 / jsonrpc 版本 / 错误码常量 / null-id 错误 / 批量 id 唯一性
LifecycleTaskManager   : initialize→tools_list→create→get→update_status
LifecycleKnowledgeBase : initialize→tools_list→upsert_ke→search→rebuild
LifecycleGateEngine    : initialize→tools_list→g1_write→g2_commit→g4_contract
LifecycleDocGuard      : initialize→tools_list→create_package→validate
LifecycleSentinel      : initialize→tools_list→map_intent→evaluate_golden_set
StdioTransport         : multi-request / malformed JSON / empty-line skip
CrossServerChain       : task_manager→gate_engine→knowledge_base 完整调用链
"""

from __future__ import annotations

import io
import json
from typing import Any, cast

import pytest

pytestmark = pytest.mark.e2e

from zephyr.integration.mcp._base_server import (
    ERR_INVALID_REQUEST,
    ERR_METHOD_NOT_FOUND,
    ERR_PARSE_ERROR,
    ERR_TOOL_NOT_FOUND,
    JSONRPC_VERSION,
    BaseMCPServer,
)
from zephyr.integration.mcp.doc_guard_server import DocGuardServer
from zephyr.integration.mcp.gate_engine_server import GateEngineServer
from zephyr.integration.mcp.knowledge_base_server import KnowledgeBaseServer
from zephyr.integration.mcp.sentinel_server import SentinelServer

# ---------------------------------------------------------------------------
# 辅助：JSON-RPC 请求构造 + 结果解析
# ---------------------------------------------------------------------------


def _req(
    method: str,
    params: dict[str, Any] | None = None,
    req_id: Any = 1,
) -> dict[str, Any]:
    """构造合规 JSON-RPC 2.0 请求 dict。"""
    r: dict[str, Any] = {"jsonrpc": JSONRPC_VERSION, "id": req_id, "method": method}
    if params is not None:
        r["params"] = params
    return r


def _call(
    server: BaseMCPServer,
    method: str,
    params: dict[str, Any] | None = None,
    req_id: Any = 1,
) -> dict[str, Any]:
    """向 Server 发送请求并返回原始响应。"""
    return cast(dict[str, Any], server.handle_request(_req(method, params, req_id)))


def _tool(
    server: BaseMCPServer,
    name: str,
    arguments: dict[str, Any],
    req_id: Any = 1,
) -> dict[str, Any]:
    """封装 tools/call 调用。"""
    return _call(server, "tools/call", {"name": name, "arguments": arguments}, req_id)


def _result(resp: dict[str, Any]) -> Any:
    """断言无 error，返回 result。"""
    assert "error" not in resp, f"Unexpected error: {resp.get('error')}"
    return resp["result"]


def _error(resp: dict[str, Any]) -> dict[str, Any]:
    """断言有 error，返回 error 字段。"""
    assert "error" in resp, f"Expected error, got result: {resp.get('result')}"
    return cast(dict[str, Any], resp["error"])


def _tool_result_text(resp: dict[str, Any]) -> Any:
    """提取 tools/call 成功响应中 content[0].text 并 JSON 解析。"""
    r = _result(resp)
    assert r["isError"] is False
    text: str = r["content"][0]["text"]
    return json.loads(text)


def _stdio_roundtrip(
    server: BaseMCPServer,
    requests: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """通过 stdio 管道发送多条请求，收集响应列表。"""
    lines = "\n".join(json.dumps(req, ensure_ascii=False) for req in requests) + "\n"
    inp = io.StringIO(lines)
    out = io.StringIO()
    server.run(input_stream=inp, output_stream=out)
    raw = out.getvalue().strip()
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


# ===========================================================================
# 1. JSON-RPC 2.0 协议合规性验证
# ===========================================================================


class TestProtocolCompliance:
    """JSON-RPC 2.0 协议合规性——与 Server 无关的通用约束。"""

    def setup_method(self) -> None:
        self.server = KnowledgeBaseServer()

    def test_response_jsonrpc_version_always_2_0(self) -> None:
        """所有成功响应必须含 jsonrpc='2.0'。"""
        resp = _call(self.server, "initialize")
        assert resp["jsonrpc"] == JSONRPC_VERSION

    def test_response_id_matches_request_integer(self) -> None:
        """响应 id 必须与请求 id 完全一致（整数）。"""
        resp = _call(self.server, "initialize", req_id=42)
        assert resp["id"] == 42

    def test_response_id_matches_request_string(self) -> None:
        """响应 id 必须与请求 id 完全一致（字符串）。"""
        resp = _call(self.server, "ping", req_id="abc-123")
        assert resp["id"] == "abc-123"

    def test_null_id_on_parse_error(self) -> None:
        """JSON 解析失败时响应 id 必须为 null，错误码 -32700。"""
        inp = io.StringIO("{not valid json\n")
        out = io.StringIO()
        self.server.run(input_stream=inp, output_stream=out)
        resp = json.loads(out.getvalue().strip())
        assert resp["id"] is None
        assert resp["error"]["code"] == ERR_PARSE_ERROR

    def test_method_not_found_error_code(self) -> None:
        """未知方法返回 error.code == -32601。"""
        resp = _call(self.server, "no_such_method")
        err = _error(resp)
        assert err["code"] == ERR_METHOD_NOT_FOUND

    def test_tool_not_found_error_code(self) -> None:
        """tools/call 调用不存在工具返回 error.code == -32001。"""
        resp = _tool(self.server, "no_such_tool", {})
        err = _error(resp)
        assert err["code"] == ERR_TOOL_NOT_FOUND

    def test_non_object_request_returns_invalid_request(self) -> None:
        """非 dict 请求（如数组）返回 -32600。"""
        inp = io.StringIO('["not", "an", "object"]\n')
        out = io.StringIO()
        self.server.run(input_stream=inp, output_stream=out)
        resp = json.loads(out.getvalue().strip())
        assert resp["error"]["code"] == ERR_INVALID_REQUEST

    def test_tools_call_content_is_json_serializable(self) -> None:
        """tools/call 返回的 content[0].text 必须是合法 JSON 字符串。"""
        _tool_result_text(
            _tool(
                self.server,
                "knowledge_base.upsert_ke",
                {
                    "ke_id": "KE-099",
                    "title": "protocol json test",
                    "category": "best_practice",
                    "content": "json roundtrip content for mcp e2e",
                    "source_file": "tests/infrastructure/test_mcp_e2e.py",
                },
            )
        )
        resp = _tool(self.server, "knowledge_base.get_ke", {"ke_id": "KE-099"})
        r = _result(resp)
        text = r["content"][0]["text"]
        parsed = json.loads(text)
        assert isinstance(parsed, dict)

    def test_batch_requests_return_unique_ids(self) -> None:
        """多请求 id 各不相同，响应 id 一一对应。"""
        responses = _stdio_roundtrip(
            self.server,
            [
                _req("initialize", req_id=10),
                _req("ping", req_id=20),
                _req("tools/list", req_id=30),
            ],
        )
        ids = [r["id"] for r in responses]
        assert ids == [10, 20, 30]


# Task Manager 已迁移至 FastMCP——JSON-RPC 生命周期测例见 tests/infrastructure/test_task_manager_mcp.py


# 3. KnowledgeBaseServer 完整生命周期
# ===========================================================================


class TestLifecycleKnowledgeBase:
    """knowledge_base Server: initialize → tools/list → upsert → search → rebuild。"""

    def setup_method(self) -> None:
        self.server = KnowledgeBaseServer()

    def test_initialize_returns_correct_server_id(self) -> None:
        resp = _call(self.server, "initialize")
        assert _result(resp)["serverInfo"]["name"] == KnowledgeBaseServer.SERVER_ID

    def test_full_lifecycle_upsert_search_rebuild(self) -> None:
        """upsert_ke → search → rebuild_index 完整流程。"""
        # 1. 写入知识条目
        upsert = _tool_result_text(
            _tool(
                self.server,
                "knowledge_base.upsert_ke",
                {
                    "ke_id": "KE-099",
                    "title": "E2E test KE",
                    "category": "best_practice",
                    "content": "duckdb olap integration test knowledge entry",
                    "source_file": "tests/infrastructure/test_mcp_e2e.py",
                },
            )
        )
        assert upsert["ke_id"] == "KE-099"

        # 2. 搜索
        search = _tool_result_text(
            _tool(
                self.server,
                "knowledge_base.search",
                {
                    "query_text": "duckdb olap",
                    "collection": "ke_entries",
                    "score_threshold": 0.5,
                },
            )
        )
        assert len(search["hits"]) >= 1
        assert search["hits"][0]["ke_id"] == "KE-099"

        # 3. 重建索引（幂等）
        rebuild = _tool_result_text(
            _tool(
                self.server,
                "knowledge_base.rebuild_index",
                {"collection": "ke_entries", "force": True},
            )
        )
        assert rebuild["chunks_indexed"] >= 1

    def test_get_ke_after_upsert(self) -> None:
        """upsert_ke 后 get_ke 应返回相同 ke_id。"""
        _tool_result_text(
            _tool(
                self.server,
                "knowledge_base.upsert_ke",
                {
                    "ke_id": "KE-100",
                    "title": "GetKE test",
                    "category": "strategy",
                    "content": "content for get test",
                    "source_file": "tests/test_mcp_e2e.py",
                },
            )
        )
        got = _tool_result_text(_tool(self.server, "knowledge_base.get_ke", {"ke_id": "KE-100"}))
        assert got["ke_id"] == "KE-100"
        assert got["title"] == "GetKE test"


# ===========================================================================
# 4. GateEngineServer 完整生命周期
# ===========================================================================


class TestLifecycleGateEngine:
    """gate_engine Server: initialize → tools/list → G1/G2/G4 → exemption。"""

    def setup_method(self) -> None:
        self.server = GateEngineServer()

    def test_initialize_returns_gate_engine_id(self) -> None:
        resp = _call(self.server, "initialize")
        assert _result(resp)["serverInfo"]["name"] == GateEngineServer.SERVER_ID

    def test_g1_write_clean_path_passes(self) -> None:
        """G1 检查干净路径时返回 passed=True，gate_run_id 存在。"""
        r = _tool_result_text(
            _tool(
                self.server,
                "gate_engine.run_g1_write",
                {
                    "target_path": "src/zephyr/feedback-loop/fitness_functions.py",
                    "content_preview": "# clean python file content",
                },
            )
        )
        assert r["passed"] is True
        assert "gate_run_id" in r

    def test_g2_commit_blocks_versioned_filename(self) -> None:
        """G2 对含 -v2. 文件名的 commit 返回错误（P0 违规）。"""
        resp = _tool(
            self.server,
            "gate_engine.run_g2_commit",
            {"files": ["docs/design-v2.md"], "commit_message": "feat(test): test"},
        )
        err = _error(resp)
        assert err["code"] == -32412

    def test_g4_contract_valid_task_payload(self) -> None:
        """G4 契约校验：完整 Task payload 通过验证。"""
        r = _tool_result_text(
            _tool(
                self.server,
                "gate_engine.run_g4_contract",
                {
                    "payload": {
                        "task_id": "T-0-001",
                        "phase": 0,
                        "status": "PENDING",
                        "directive": "e2e test task",
                    },
                    "model_name": "Task",
                },
            )
        )
        assert r["passed"] is True
        assert r["errors"] == []

    def test_submit_exemption_returns_exemption_id(self) -> None:
        """submit_exemption 返回 EX- 开头的豁免 ID。"""
        r = _tool_result_text(
            _tool(
                self.server,
                "gate_engine.submit_exemption",
                {
                    "check_id": "G1.1",
                    "reason": "this is a valid reason for exemption",
                    "valid_until": "2026-12-31",
                    "signer_email": "owner@zephyr.io",
                },
            )
        )
        assert r["accepted"] is True
        assert r["exemption_id"].startswith("EX-G1.1-")


# ===========================================================================
# 5. DocGuardServer 完整生命周期
# ===========================================================================


class TestLifecycleDocGuard:
    """session_handoff Server: initialize → tools/list → create_package → validate。"""

    def setup_method(self) -> None:
        self.server = DocGuardServer()

    def test_initialize_returns_session_handoff_id(self) -> None:
        resp = _call(self.server, "initialize")
        assert _result(resp)["serverInfo"]["name"] == DocGuardServer.SERVER_ID

    def test_full_lifecycle_create_and_validate_package(self) -> None:
        """create_package → get_carryover → validate_package 完整流程。"""
        # 1. 创建交接包
        pkg = _tool_result_text(
            _tool(
                self.server,
                "session_handoff.create_package",
                {
                    "from_session": "sess-e2e-001",
                    "to_model": "claude-sonnet-4-6",
                    "completed_tasks": ["T-0-001", "T-0-002"],
                    "next_tasks": ["T-1-001"],
                    "open_files": ["src/zephyr/feedback-loop/fitness_functions.py"],
                    "decisions_log": ["chose DuckDB for OLAP"],
                },
            )
        )
        assert pkg["from_session"] == "sess-e2e-001"
        assert pkg["anti_corruption_report"]["passed"] is True

        # 2. 获取 carryover
        co = _tool_result_text(_tool(self.server, "session_handoff.get_carryover", {}))
        assert co["session_id"] == "sess-e2e-001"

        # 3. 独立校验同一包
        validated = _tool_result_text(
            _tool(
                self.server,
                "session_handoff.validate_package",
                {"package": pkg},
            )
        )
        assert validated["passed"] is True

    def test_emit_manual_event_lifecycle(self) -> None:
        """emit_manual_event 返回 event_id + delivered_at。"""
        r = _tool_result_text(
            _tool(
                self.server,
                "session_handoff.emit_manual_event",
                {
                    "task_id": "T-1-BLOCKED-001",
                    "priority": "HIGH",
                    "reason": "Gate P0 violation detected in e2e test",
                },
            )
        )
        assert "event_id" in r
        assert "delivered_at" in r


# ===========================================================================
# 6. SentinelServer 完整生命周期
# ===========================================================================


class TestLifecycleSentinel:
    """intent_router Server: initialize → tools/list → map_intent → golden_set。"""

    def setup_method(self) -> None:
        self.server = SentinelServer()

    def test_initialize_returns_intent_router_id(self) -> None:
        resp = _call(self.server, "initialize")
        assert _result(resp)["serverInfo"]["name"] == SentinelServer.SERVER_ID

    def test_map_intent_data_domain(self) -> None:
        """D0 数据域查询：primary_domain == 'D0'。"""
        r = _tool_result_text(
            _tool(
                self.server,
                "intent_router.map_intent",
                {"query": "帮我获取 AKShare OHLCV 行情数据"},
            )
        )
        assert r["primary_domain"] == "D0"
        assert r["confidence"] > 0.0

    def test_map_intent_governance_domain(self) -> None:
        """D2 治理域：audit + governance 关键词触发 D2。"""
        r = _tool_result_text(
            _tool(
                self.server,
                "intent_router.map_intent",
                {"query": "查看 ADR 治理规则和审计报告"},
            )
        )
        assert r["primary_domain"] == "D2"

    def test_evaluate_golden_set_returns_accuracy(self) -> None:
        """evaluate_golden_set 返回 top1_accuracy 字段（≥ 0.0）。"""
        r = _tool_result_text(
            _tool(
                self.server,
                "intent_router.evaluate_golden_set",
                {"max_stage": 1},
            )
        )
        assert "top1_accuracy" in r
        assert 0.0 <= r["top1_accuracy"] <= 1.0

    def test_reload_keywords_then_map(self) -> None:
        """reload_keywords 后 map_intent 使用新词典。"""
        # 加载自定义词典
        reload_r = _tool_result_text(
            _tool(
                self.server,
                "intent_router.reload_keywords",
                {"keyword_dict": {"D0": ["custom_ticker", "tick_data"]}},
            )
        )
        assert reload_r["domains_loaded"] >= 1

        # 使用新词典路由
        map_r = _tool_result_text(
            _tool(
                self.server,
                "intent_router.map_intent",
                {"query": "fetch custom_ticker data"},
            )
        )
        assert map_r["primary_domain"] == "D0"


# ===========================================================================
# 7. stdio 传输层模拟测试
# ===========================================================================


class TestStdioTransport:
    """stdio 传输层：多请求批量、无效 JSON 恢复、空行跳过。"""

    def setup_method(self) -> None:
        self.server = KnowledgeBaseServer()

    def test_multi_request_batch_via_stdio(self) -> None:
        """3 条请求通过 stdio 逐行处理，响应数量和 id 正确。"""
        requests = [
            _req("initialize", req_id=1),
            _req("ping", req_id=2),
            _req("tools/list", req_id=3),
        ]
        responses = _stdio_roundtrip(self.server, requests)
        assert len(responses) == 3
        assert [r["id"] for r in responses] == [1, 2, 3]

    def test_malformed_json_followed_by_valid_request(self) -> None:
        """无效 JSON 行不中断后续合法请求处理。"""
        inp = io.StringIO("not json at all\n" + json.dumps(_req("ping", req_id=99)) + "\n")
        out = io.StringIO()
        self.server.run(input_stream=inp, output_stream=out)
        lines = [ln for ln in out.getvalue().splitlines() if ln.strip()]
        assert len(lines) == 2  # parse_error + pong
        parse_err = json.loads(lines[0])
        assert parse_err["error"]["code"] == ERR_PARSE_ERROR
        pong = json.loads(lines[1])
        assert pong["id"] == 99

    def test_empty_lines_are_skipped(self) -> None:
        """纯空行不产生响应。"""
        inp = io.StringIO("\n\n\n" + json.dumps(_req("ping", req_id=7)) + "\n" + "\n")
        out = io.StringIO()
        self.server.run(input_stream=inp, output_stream=out)
        lines = [ln for ln in out.getvalue().splitlines() if ln.strip()]
        assert len(lines) == 1
        assert json.loads(lines[0])["id"] == 7


# ===========================================================================
# 8. 跨 Server 调用链测试（task_manager → gate_engine → knowledge_base）
# ===========================================================================


class TestCrossServerChain:
    """
    跨服务调用链（JSON-RPC BaseMCPServer）：
      ① 合成 Task 形状 payload（与 Task Manager 工具解耦）
      ② gate_engine G4 契约校验
      ③ knowledge_base 存储审计知识条目
    """

    def setup_method(self) -> None:
        self.ge = GateEngineServer()
        self.kb = KnowledgeBaseServer()

    def test_chain_task_payload_gate_validate_kb_store(self) -> None:
        """G4 契约校验代表性 Task payload → knowledge_base upsert。"""
        gate_payload = {
            "task_id": "SRC-001",
            "phase": 0,
            "status": "PENDING",
            "directive": "cross-server chain test synthetic payload",
        }
        gate_r = _tool_result_text(
            _tool(
                self.ge,
                "gate_engine.run_g4_contract",
                {"payload": gate_payload, "model_name": "Task"},
            )
        )
        assert gate_r["passed"] is True

        ke_content = f"Gate G4 passed for task {gate_payload['task_id']}: {gate_r}"
        ke_r = _tool_result_text(
            _tool(
                self.kb,
                "knowledge_base.upsert_ke",
                {
                    "ke_id": "KE-200",
                    "title": f"Gate pass record: {gate_payload['task_id']}",
                    "category": "best_practice",
                    "content": ke_content,
                    "source_file": "cross-server-chain",
                },
            )
        )
        assert ke_r["ke_id"] == "KE-200"

    def test_chain_gate_block_triggers_manual_event(self) -> None:
        """G1 阻断 → doc_guard emit_manual_event 完整链。"""
        doc_guard = DocGuardServer()

        # Step 1: gate_engine G1 对黑名单路径阻断
        gate_resp = _tool(
            self.ge,
            "gate_engine.run_g1_write",
            {
                "target_path": "scripts/archive/old_module.py",
                "content_preview": "old code",
            },
        )
        err = _error(gate_resp)
        assert err["code"] == -32412  # ZA-GT-0001

        # Step 2: doc_guard 触发人工介入事件
        event_r = _tool_result_text(
            _tool(
                doc_guard,
                "session_handoff.emit_manual_event",
                {
                    "task_id": "T-0-CHAIN-002",
                    "priority": "CRITICAL",
                    "reason": f"Gate G1 blocked: {err['message'][:50]}",
                },
            )
        )
        assert "event_id" in event_r

    def test_chain_g3_phase_passes_standalone(self) -> None:
        """G3 阶段门禁可独立通过（不依赖 task_manager JSON-RPC）。"""
        g3_r = _tool_result_text(
            _tool(
                self.ge,
                "gate_engine.run_g3_phase",
                {"phase_id": 0, "target_phase": 1},
            )
        )
        assert g3_r["passed"] is True
