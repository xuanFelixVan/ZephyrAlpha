# [A_test] module_id: MOD-GOV_session_audit_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-680 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_session_audit
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for session_audit.py
"""

import tempfile

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


class TestPromptRecord:
    def test_create(self):
        record = PromptRecord(
            timestamp="2026-05-07T00:00:00Z",
            role="user",
            content_preview="hello",
            token_count=10,
        )
        assert record.role == "user"
        assert record.token_count == 10


class TestDecisionRecord:
    def test_create(self):
        record = DecisionRecord(
            timestamp="2026-05-07T00:00:00Z",
            decision_id="D1",
            summary="Use SQLite",
            rationale="Lightweight",
            alternatives=["DuckDB"],
        )
        assert record.decision_id == "D1"
        assert len(record.alternatives) == 1


class TestToolCallRecord:
    def test_create(self):
        record = ToolCallRecord(
            timestamp="2026-05-07T00:00:00Z",
            tool_name="search",
            parameters_preview="{}",
            result_summary="found",
            duration_ms=123.4,
        )
        assert record.tool_name == "search"
        assert record.duration_ms == 123.4
        assert record.success is True


class TestCostRecord:
    def test_create(self):
        record = CostRecord(
            timestamp="2026-05-07T00:00:00Z",
            provider="openai",
            model="gpt-4o",
            input_tokens=500,
            output_tokens=200,
            cost_usd=0.0075,
        )
        assert record.cost_usd == 0.0075


class TestErrorRecord:
    def test_create(self):
        record = ErrorRecord(
            timestamp="2026-05-07T00:00:00Z",
            error_type="TimeoutError",
            message="LLM timeout",
            recovery_action="retry",
            recovered=True,
        )
        assert record.recovered is True


class TestOutcomeRecord:
    def test_create(self):
        record = OutcomeRecord(
            timestamp="2026-05-07T00:00:00Z",
            files_created=["a.py"],
            tests_run=10,
            tests_passed=9,
        )
        assert record.files_created == ["a.py"]
        assert record.tests_passed == 9


class TestSessionRecord:
    def test_create(self):
        record = SessionRecord(session_id="session-20260507-001")
        assert record.session_id == "session-20260507-001"
        assert record.started_at is not None
        assert record.ended_at is None

    def test_add_prompt(self):
        record = SessionRecord("s1")
        p = record.add_prompt("user", "hello world")
        assert p.role == "user"
        assert len(record.prompts) == 1

    def test_add_prompt_truncates_long_content(self):
        record = SessionRecord("s1")
        p = record.add_prompt("system", "a" * 500)
        assert len(p.content_preview) <= 203

    def test_add_decision(self):
        record = SessionRecord("s1")
        d = record.add_decision("D1", "Use SQLite", "Lightweight", ["DuckDB"])
        assert d.decision_id == "D1"
        assert len(record.decisions) == 1

    def test_add_tool_call(self):
        record = SessionRecord("s1")
        t = record.add_tool_call("search", "{}", "ok", 100.0)
        assert t.tool_name == "search"
        assert len(record.tool_calls) == 1

    def test_add_cost(self):
        record = SessionRecord("s1")
        c = record.add_cost("openai", "gpt-4o", 100, 50, 0.005)
        assert c.cost_usd == 0.005
        assert len(record.costs) == 1

    def test_add_error(self):
        record = SessionRecord("s1")
        e = record.add_error("ValueError", "bad input", "fixed", True)
        assert e.recovered is True
        assert len(record.errors) == 1

    def test_set_outcomes(self):
        record = SessionRecord("s1")
        record.set_outcomes(
            files_created=["a.py"],
            files_modified=["b.py"],
            tests_run=5,
            tests_passed=5,
            knowledge_extracted=3,
            deviations_found=1,
        )
        assert record.outcomes is not None
        assert record.outcomes.files_created == ["a.py"]

    def test_finish(self):
        record = SessionRecord("s1")
        assert record.ended_at is None
        record.finish()
        assert record.ended_at is not None

    def test_total_cost_usd(self):
        record = SessionRecord("s1")
        record.add_cost("a", "m1", cost_usd=0.01)
        record.add_cost("b", "m2", cost_usd=0.02)
        assert record.total_cost_usd == 0.03

    def test_total_tokens(self):
        record = SessionRecord("s1")
        record.add_cost("a", "m1", input_tokens=100, output_tokens=50)
        record.add_cost("b", "m2", input_tokens=200, output_tokens=100)
        assert record.total_tokens == 450

    def test_error_and_recovered_count(self):
        record = SessionRecord("s1")
        record.add_error("E1", "msg1", recovered=True)
        record.add_error("E2", "msg2", recovered=False)
        assert record.error_count == 2
        assert record.recovered_count == 1

    def test_to_dict(self):
        record = SessionRecord("s1")
        record.add_prompt("user", "hello")
        record.add_decision("D1", "Use X", "reason")
        record.finish()
        d = record.to_dict()
        assert d["session_id"] == "s1"
        assert d["prompts_count"] == 1
        assert d["decisions_count"] == 1
        assert d["total_cost_usd"] == 0.0


class TestSessionAuditTrail:
    def test_start_and_append(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trail = SessionAuditTrail(audit_dir=tmpdir)
            record = trail.start_session("s1")
            record.add_decision("D1", "Test", "Testing")
            record.finish()
            path = trail.append_record(record)
            assert path.exists()

    def test_query_returns_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trail = SessionAuditTrail(audit_dir=tmpdir)
            record = trail.start_session("s1")
            record.finish()
            trail.append_record(record)
            results = trail.query("s1")
            assert len(results) == 1
            assert results[0]["session_id"] == "s1"

    def test_query_missing_session(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trail = SessionAuditTrail(audit_dir=tmpdir)
            results = trail.query("nonexistent")
            assert results == []

    def test_export_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trail = SessionAuditTrail(audit_dir=tmpdir)
            record = trail.start_session("s1")
            record.finish()
            trail.append_record(record)
            exported = trail.export_jsonl("s1")
            assert "s1" in exported

    def test_export_jsonl_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trail = SessionAuditTrail(audit_dir=tmpdir)
            assert trail.export_jsonl("nonexistent") == ""

    def test_list_sessions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trail = SessionAuditTrail(audit_dir=tmpdir)
            for sid in ["s1", "s2"]:
                record = trail.start_session(sid)
                record.finish()
                trail.append_record(record)
            sessions = trail.list_sessions()
            assert len(sessions) == 2
            assert "s1" in sessions
            assert "s2" in sessions

    def test_get_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trail = SessionAuditTrail(audit_dir=tmpdir)
            record = trail.start_session("s1")
            record.add_cost("openai", "gpt-4o", 100, 50, 0.005)
            record.add_decision("D1", "Test", "Testing")
            record.finish()
            trail.append_record(record)
            summary = trail.get_summary("s1")
            assert summary["record_count"] == 1
            assert summary["total_cost_usd"] == 0.005
            assert summary["total_decisions"] == 1

    def test_get_summary_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trail = SessionAuditTrail(audit_dir=tmpdir)
            summary = trail.get_summary("nonexistent")
            assert summary["session_id"] == "nonexistent"
            assert summary["record_count"] == 0
