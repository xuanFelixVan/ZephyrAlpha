# [A_test] module_id: SRC-TST-1015 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_exceptions
# [INVARIANTS] FLEBaseException always carries forensic_context; ForensicContext defaults are safe
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
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


class TestForensicContextInstantiation:
    def test_default_values(self):
        ctx = ForensicContext()
        assert ctx.stack_trace is None
        assert ctx.causal_chain == []
        assert ctx.decision_id is None

    def test_custom_values(self):
        ctx = ForensicContext(
            stack_trace="traceback...",
            causal_chain=["cause_a", "cause_b"],
            decision_id="DEC-001",
        )
        assert ctx.stack_trace == "traceback..."
        assert ctx.causal_chain == ["cause_a", "cause_b"]
        assert ctx.decision_id == "DEC-001"

    def test_empty_causal_chain(self):
        ctx = ForensicContext(causal_chain=[])
        assert ctx.causal_chain == []


class TestFLEBaseException:
    def test_instantiation_with_message(self):
        exc = FLEBaseException("test error")
        assert str(exc) == "test error"
        assert exc.forensic_context is not None

    def test_instantiation_with_forensic_context(self):
        ctx = ForensicContext(decision_id="DEC-002")
        exc = FLEBaseException("error with context", forensic_context=ctx)
        assert exc.forensic_context.decision_id == "DEC-002"

    def test_default_forensic_context(self):
        exc = FLEBaseException("error")
        assert isinstance(exc.forensic_context, ForensicContext)
        assert exc.forensic_context.stack_trace is None
        assert exc.forensic_context.causal_chain == []

    def test_is_exception(self):
        exc = FLEBaseException("test")
        assert isinstance(exc, Exception)

    def test_none_forensic_context_gets_default(self):
        exc = FLEBaseException("msg", forensic_context=None)
        assert isinstance(exc.forensic_context, ForensicContext)


class TestDiagnosisError:
    def test_instantiation(self):
        exc = DiagnosisError("diagnosis failed")
        assert str(exc) == "diagnosis failed"
        assert isinstance(exc, FLEBaseException)

    def test_with_context(self):
        ctx = ForensicContext(causal_chain=["root_cause"])
        exc = DiagnosisError("bad diagnosis", forensic_context=ctx)
        assert exc.forensic_context.causal_chain == ["root_cause"]

    def test_raise_and_catch(self):
        with pytest.raises(DiagnosisError):
            raise DiagnosisError("fail")


class TestRepairError:
    def test_instantiation(self):
        exc = RepairError("repair failed")
        assert str(exc) == "repair failed"
        assert isinstance(exc, FLEBaseException)

    def test_raise_and_catch(self):
        with pytest.raises(RepairError):
            raise RepairError("fail")


class TestGateBlockedError:
    def test_instantiation(self):
        exc = GateBlockedError("gate blocked")
        assert str(exc) == "gate blocked"
        assert isinstance(exc, FLEBaseException)

    def test_raise_and_catch(self):
        with pytest.raises(GateBlockedError):
            raise GateBlockedError("blocked")


class TestAutonomyViolationError:
    def test_instantiation(self):
        exc = AutonomyViolationError("violation")
        assert str(exc) == "violation"
        assert isinstance(exc, FLEBaseException)

    def test_raise_and_catch(self):
        with pytest.raises(AutonomyViolationError):
            raise AutonomyViolationError("violation")


class TestExceptionHierarchy:
    def test_catch_base_catches_subclass(self):
        with pytest.raises(FLEBaseException):
            raise DiagnosisError("caught by base")

    def test_catch_base_catches_all(self):
        for exc_cls in [DiagnosisError, RepairError, GateBlockedError, AutonomyViolationError]:
            with pytest.raises(FLEBaseException):
                raise exc_cls("test")
