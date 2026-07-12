# [A_test] module_id: SRC-TST-1875 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
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
    def test_default_values(self):
        ctx = ForensicContext()
        assert ctx.stack_trace is None
        assert ctx.causal_chain == []
        assert ctx.decision_id is None

    def test_custom_values(self):
        ctx = ForensicContext(
            stack_trace="traceback...",
            causal_chain=["step_a", "step_b"],
            decision_id="DEC-001",
        )
        assert ctx.stack_trace == "traceback..."
        assert ctx.causal_chain == ["step_a", "step_b"]
        assert ctx.decision_id == "DEC-001"


class TestFLEBaseException:
    def test_message(self):
        exc = FLEBaseException("test error")
        assert str(exc) == "test error"

    def test_default_forensic_context(self):
        exc = FLEBaseException("err")
        assert isinstance(exc.forensic_context, ForensicContext)
        assert exc.forensic_context.stack_trace is None

    def test_custom_forensic_context(self):
        ctx = ForensicContext(decision_id="D-1")
        exc = FLEBaseException("err", forensic_context=ctx)
        assert exc.forensic_context.decision_id == "D-1"

    def test_is_exception(self):
        with pytest.raises(FLEBaseException):
            raise FLEBaseException("boom")


class TestDiagnosisError:
    def test_inherits_base(self):
        exc = DiagnosisError("diag failed")
        assert isinstance(exc, FLEBaseException)
        assert str(exc) == "diag failed"

    def test_with_forensic_context(self):
        ctx = ForensicContext(causal_chain=["root"])
        exc = DiagnosisError("bad", forensic_context=ctx)
        assert exc.forensic_context.causal_chain == ["root"]


class TestRepairError:
    def test_inherits_base(self):
        exc = RepairError("repair failed")
        assert isinstance(exc, FLEBaseException)

    def test_raise_and_catch(self):
        with pytest.raises(RepairError):
            raise RepairError("broken")


class TestGateBlockedError:
    def test_inherits_base(self):
        exc = GateBlockedError("gate blocked")
        assert isinstance(exc, FLEBaseException)


class TestAutonomyViolationError:
    def test_inherits_base(self):
        exc = AutonomyViolationError("violation")
        assert isinstance(exc, FLEBaseException)

    def test_distinct_types(self):
        assert DiagnosisError is not RepairError
        assert GateBlockedError is not AutonomyViolationError
