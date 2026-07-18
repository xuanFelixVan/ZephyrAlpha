# [A_test] module_id: SRC-TST-1956 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-573 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_session_audit
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/session_audit.py
==============================================
覆盖矩阵：
  SessionRecord：
    - 初始化 & 属性 × 2（session_id, started_at）
    - total_cost_usd / total_tokens / error_count × 3
    - add_prompt × 1
    - add_decision × 1
    - add_tool_call × 2（成功/失败）
    - add_cost × 1
    - add_error × 2（恢复/未恢复）
    - recovered_count × 1
    - set_outcomes / finish × 2
    - to_dict 完整输出 × 1
  SessionAuditTrail：
    - start_session × 1
    - append_record / query 环形 × 1
    - query 空 session × 1
    - list_sessions × 1
    - get_summary × 2
    - export_jsonl × 1
  Record types（Prompt/Decision/ToolCall/Cost/Error/Outcome）：
    - 构造 × 各 1

Safety: HIGH（审计记录是不可变安全证据）
"""

from zephyr.shared.session.session_audit import (
    CostRecord,
    DecisionRecord,
    ErrorRecord,
    OutcomeRecord,
    PromptRecord,
    SessionAuditTrail,
    SessionRecord,
    ToolCallRecord,
)


class TestRecordTypes:
    def test_prompt_record(self):
        r = PromptRecord(
            timestamp="2026-05-08T00:00:00Z",
            role="user",
            content_preview="Hello...",
            token_count=50,
        )
        assert r.role == "user"
        assert r.token_count == 50

    def test_decision_record(self):
        r = DecisionRecord(
            timestamp="2026-05-08T00:00:00Z",
            decision_id="D1",
            summary="Use SQLite",
            rationale="Lightweight",
            alternatives=["PostgreSQL"],
        )
        assert r.decision_id == "D1"
        assert r.alternatives == ["PostgreSQL"]

    def test_tool_call_record(self):
        r = ToolCallRecord(
            timestamp="2026-05-08T00:00:00Z",
            tool_name="read_file",
            parameters_preview='{"path": "x.py"}',
            result_summary="file content...",
            duration_ms=12.5,
            success=True,
        )
        assert r.tool_name == "read_file"
        assert r.duration_ms == 12.5
        assert r.success is True

    def test_cost_record(self):
        r = CostRecord(
            timestamp="2026-05-08T00:00:00Z",
            provider="openai",
            model="gpt-4o",
            input_tokens=500,
            output_tokens=200,
            cost_usd=0.0075,
        )
        assert r.provider == "openai"
        assert r.cost_usd == 0.0075

    def test_error_record(self):
        r = ErrorRecord(
            timestamp="2026-05-08T00:00:00Z",
            error_type="ImportError",
            message="No module named 'foo'",
            recovery_action="pip install foo",
            recovered=True,
        )
        assert r.error_type == "ImportError"
        assert r.recovered is True

    def test_outcome_record(self):
        r = OutcomeRecord(
            timestamp="2026-05-08T00:00:00Z",
            files_created=["a.py"],
            files_modified=["b.py"],
            tests_run=10,
            tests_passed=9,
            knowledge_extracted=3,
            deviations_found=1,
        )
        assert r.files_created == ["a.py"]
        assert r.tests_run == 10


class TestSessionRecord:
    def test_initialization(self):
        record = SessionRecord(session_id="session-001")
        assert record.session_id == "session-001"
        assert record.started_at != ""
        assert record.ended_at is None
        assert record.prompts == []
        assert record.outcomes is None

    def test_metadata(self):
        record = SessionRecord(session_id="session-001", metadata={"task": "build"})
        assert record.metadata["task"] == "build"

    def test_add_prompt(self):
        record = SessionRecord(session_id="session-001")
        pr = record.add_prompt("user", "Hello, write a function", token_count=5)
        assert pr.role == "user"
        assert len(record.prompts) == 1

    def test_add_prompt_truncates_long_content(self):
        record = SessionRecord(session_id="session-001")
        long_content = "x" * 300
        pr = record.add_prompt("system", long_content)
        assert pr.content_preview.endswith("...")
        assert len(pr.content_preview) <= 203

    def test_add_decision(self):
        record = SessionRecord(session_id="session-001")
        dr = record.add_decision("D1", "Use async", "Better throughput", ["sync"])
        assert dr.decision_id == "D1"
        assert len(dr.alternatives) == 1

    def test_add_tool_call_success(self):
        record = SessionRecord(session_id="session-001")
        tr = record.add_tool_call("write", '{"path":"x.py"}', "OK", duration_ms=5.0)
        assert tr.success is True

    def test_add_tool_call_failure(self):
        record = SessionRecord(session_id="session-001")
        tr = record.add_tool_call("write", '{"path":"x.py"}', "err", success=False)
        assert tr.success is False

    def test_add_cost(self):
        record = SessionRecord(session_id="session-001")
        cr = record.add_cost("openai", "gpt-4o", 100, 50, 0.0075)
        assert cr.provider == "openai"

    def test_add_error(self):
        record = SessionRecord(session_id="session-001")
        er = record.add_error("KeyError", "missing key", "retry", True)
        assert er.error_type == "KeyError"
        assert er.recovered is True

    def test_total_cost_usd(self):
        record = SessionRecord(session_id="session-001")
        record.add_cost("openai", "gpt-4o", cost_usd=0.01)
        record.add_cost("openai", "gpt-4o", cost_usd=0.02)
        assert record.total_cost_usd == 0.03

    def test_total_tokens(self):
        record = SessionRecord(session_id="session-001")
        record.add_cost("openai", "gpt-4o", input_tokens=100, output_tokens=50)
        record.add_cost("openai", "gpt-4o", input_tokens=200, output_tokens=100)
        assert record.total_tokens == 450

    def test_recovered_count(self):
        record = SessionRecord(session_id="session-001")
        record.add_error("E1", "msg", recovered=True)
        record.add_error("E2", "msg", recovered=False)
        record.add_error("E3", "msg", recovered=True)
        assert record.error_count == 3
        assert record.recovered_count == 2

    def test_set_outcomes(self):
        record = SessionRecord(session_id="session-001")
        outcome = record.set_outcomes(
            files_created=["x.py"],
            tests_run=5,
            tests_passed=5,
        )
        assert outcome.files_created == ["x.py"]
        assert record.outcomes is outcome

    def test_finish(self):
        record = SessionRecord(session_id="session-001")
        record.finish()
        assert record.ended_at is not None

    def test_to_dict(self):
        record = SessionRecord(session_id="session-001")
        record.add_prompt("user", "Hi")
        record.add_decision("D1", "Use SQLite", "rationale")
        record.add_tool_call("read", "{}", "ok")
        record.add_cost("openai", "gpt-4o", cost_usd=0.01)
        record.add_error("E1", "msg")
        record.set_outcomes(tests_run=3, tests_passed=3)
        d = record.to_dict()
        assert d["session_id"] == "session-001"
        assert d["prompts_count"] == 1
        assert d["decisions_count"] == 1
        assert d["tool_calls_count"] == 1
        assert d["total_cost_usd"] == 0.01
        assert "outcomes" in d


class TestSessionAuditTrail:
    def test_start_session(self):
        trail = SessionAuditTrail(audit_dir="logs/test_audit/")
        record = trail.start_session("test-session")
        assert isinstance(record, SessionRecord)
        assert record.session_id == "test-session"

    def test_append_and_query(self, tmp_path):
        trail = SessionAuditTrail(audit_dir=str(tmp_path / "audit"))
        record = trail.start_session("s1")
        record.add_decision("D1", "test", "reason")
        trail.append_record(record)

        records = trail.query("s1")
        assert len(records) == 1
        assert records[0]["session_id"] == "s1"

    def test_query_nonexistent(self):
        trail = SessionAuditTrail(audit_dir="logs/test_audit/")
        assert trail.query("nonexistent-session") == []

    def test_list_sessions(self, tmp_path):
        trail = SessionAuditTrail(audit_dir=str(tmp_path / "audit2"))
        trail.append_record(trail.start_session("a"))
        trail.append_record(trail.start_session("b"))
        sessions = trail.list_sessions()
        assert "a" in sessions
        assert "b" in sessions

    def test_get_summary(self, tmp_path):
        trail = SessionAuditTrail(audit_dir=str(tmp_path / "audit3"))
        record = trail.start_session("s1")
        record.add_cost("openai", "gpt-4o", cost_usd=0.05)
        record.add_decision("D1", "test", "reason")
        trail.append_record(record)

        summary = trail.get_summary("s1")
        assert summary["record_count"] == 1
        assert summary["total_cost_usd"] == 0.05
        assert summary["total_decisions"] == 1

    def test_get_summary_nonexistent(self):
        trail = SessionAuditTrail(audit_dir="logs/test_audit/")
        summary = trail.get_summary("no-such")
        assert summary["record_count"] == 0

    def test_export_jsonl(self, tmp_path):
        trail = SessionAuditTrail(audit_dir=str(tmp_path / "audit4"))
        record = trail.start_session("s1")
        record.add_decision("D1", "test", "reason")
        trail.append_record(record)

        exported = trail.export_jsonl("s1")
        assert "session_id" in exported

    def test_export_jsonl_nonexistent(self):
        trail = SessionAuditTrail(audit_dir="logs/test_audit/")
        assert trail.export_jsonl("no-such") == ""
