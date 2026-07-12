# [A_test] module_id: SRC-TST-0960 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_exceptions
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.exceptions
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_exceptions.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.exceptions import (
    AutonomyViolationError,
    DiagnosisError,
    FLEBaseException,
    ForensicContext,
    GateBlockedError,
    RepairError,
)


class TestForensicContext:
    def test_creates_with_defaults(self):
        ctx = ForensicContext()
        assert ctx.stack_trace is None
        assert ctx.causal_chain == []
        assert ctx.decision_id is None

    def test_creates_with_custom_params(self):
        ctx = ForensicContext(
            stack_trace="traceback...",
            causal_chain=["step1", "step2"],
            decision_id="D-001",
        )
        assert ctx.stack_trace == "traceback..."
        assert len(ctx.causal_chain) == 2
        assert ctx.decision_id == "D-001"


class TestFLEBaseException:
    def test_creates_with_message(self):
        exc = FLEBaseException("test error")
        assert str(exc) == "test error"
        assert exc.forensic_context is not None

    def test_creates_with_forensic_context(self):
        ctx = ForensicContext(decision_id="D-001")
        exc = FLEBaseException("error", forensic_context=ctx)
        assert exc.forensic_context.decision_id == "D-001"

    def test_is_exception(self):
        exc = FLEBaseException("test")
        assert isinstance(exc, Exception)

    def test_boundary_empty_message(self):
        exc = FLEBaseException("")
        assert str(exc) == ""


class TestDiagnosisError:
    def test_inherits_from_base(self):
        exc = DiagnosisError("diagnosis failed")
        assert isinstance(exc, FLEBaseException)

    def test_carries_forensic_context(self):
        ctx = ForensicContext(stack_trace="tb")
        exc = DiagnosisError("fail", forensic_context=ctx)
        assert exc.forensic_context.stack_trace == "tb"


class TestRepairError:
    def test_inherits_from_base(self):
        exc = RepairError("repair failed")
        assert isinstance(exc, FLEBaseException)


class TestGateBlockedError:
    def test_inherits_from_base(self):
        exc = GateBlockedError("gate blocked")
        assert isinstance(exc, FLEBaseException)


class TestAutonomyViolationError:
    def test_inherits_from_base(self):
        exc = AutonomyViolationError("violation")
        assert isinstance(exc, FLEBaseException)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(AutonomyViolationError, match="violation"):
            raise AutonomyViolationError("violation")
