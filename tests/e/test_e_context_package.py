# [A_test] module_id: MOD-GOV_e_context_package | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §

# [MODULE] tests.test_e_context_package

# [INVARIANTS] test完整性

# [MODIFY-GUARD] none

# [CONSUMERS] none

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] none

# [TESTS] self
# [TTL] task_bound

from datetime import UTC, datetime

from zephyr.governance.context_governance.context_package import (
    ContextPackageBuilder,
    EscalationContext,
)


class TestEscalationContext:
    def test_instantiation_context_id_only_defaults(self):
        ctx = EscalationContext(context_id="ctx-001")

        assert ctx.context_id == "ctx-001"
        assert ctx.task_id == ""
        assert ctx.reason == ""
        assert ctx.evidence_chain == []
        assert ctx.try_trace == []
        assert isinstance(ctx.escalated_at, datetime)
        assert ctx.escalation_level == ""
        assert ctx.suggested_action == ""

    def test_instantiation_all_fields(self):
        now = datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC)
        ctx = EscalationContext(
            context_id="ctx-002",
            task_id="TASK-42",
            reason="test failure escalation",
            evidence_chain=["log_line_1", "log_line_2"],
            try_trace=[{"attempt": 1, "result": "fail"}, {"attempt": 2, "result": "fail"}],
            escalated_at=now,
            escalation_level="P1",
            suggested_action="manual review required",
        )

        assert ctx.context_id == "ctx-002"
        assert ctx.task_id == "TASK-42"
        assert ctx.reason == "test failure escalation"
        assert ctx.evidence_chain == ["log_line_1", "log_line_2"]
        assert ctx.try_trace == [{"attempt": 1, "result": "fail"}, {"attempt": 2, "result": "fail"}]
        assert ctx.escalated_at == now
        assert ctx.escalation_level == "P1"
        assert ctx.suggested_action == "manual review required"


class TestContextPackageBuilder:
    def test_build_returns_escalation_context(self):
        builder = ContextPackageBuilder()
        result = builder.build(task_id="TASK-01", reason="reason", level="P0")

        assert isinstance(result, EscalationContext)

    def test_build_context_id_format(self):
        builder = ContextPackageBuilder()
        result = builder.build(task_id="TASK-99", reason="reason", level="P0")

        assert result.context_id == "CTX-TASK-99"

    def test_build_with_evidence_and_trace(self):
        evidence = ["e1", "e2"]
        trace = [{"step": 1}, {"step": 2}]
        builder = ContextPackageBuilder()
        result = builder.build(
            task_id="TASK-10",
            reason="escalation reason",
            level="P2",
            evidence=evidence,
            trace=trace,
        )

        assert result.task_id == "TASK-10"
        assert result.reason == "escalation reason"
        assert result.escalation_level == "P2"
        assert result.evidence_chain == evidence
        assert result.try_trace == trace

    def test_build_none_evidence_trace_becomes_empty_lists(self):
        builder = ContextPackageBuilder()
        result = builder.build(
            task_id="TASK-20",
            reason="reason",
            level="P1",
            evidence=None,
            trace=None,
        )

        assert result.evidence_chain == []
        assert result.try_trace == []

    def test_build_empty_task_id(self):
        builder = ContextPackageBuilder()
        result = builder.build(task_id="", reason="some reason", level="P0")

        assert result.context_id == "CTX-"
        assert result.task_id == ""

    def test_build_empty_reason(self):
        builder = ContextPackageBuilder()
        result = builder.build(task_id="TASK-30", reason="", level="P0")

        assert result.reason == ""
        assert result.task_id == "TASK-30"
