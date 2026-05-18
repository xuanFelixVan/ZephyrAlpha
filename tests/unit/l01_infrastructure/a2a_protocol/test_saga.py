# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_saga
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Saga"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_saga import (
    A2ASaga,
    SagaStatus,
    SagaResult,
)


def test_saga_execute_success():
    s = A2ASaga("saga-1")
    s.add_step("step-1", "agent-a", "write_file", {"path": "f.py"})
    s.add_step("step-2", "agent-b", "run_tests", {"path": "f.py"})
    result = s.execute({"write_file": lambda p: {"ok": True}, "run_tests": lambda p: {"ok": True}})
    assert isinstance(result, SagaResult)
    assert result.status == SagaStatus.COMPLETED
    assert result.executed_count == 2


def test_saga_execute_failure_compensates():
    s = A2ASaga("saga-2")
    s.add_step("step-1", "agent-a", "write_file", {"path": "f.py"}, compensate_action="delete_file")
    s.add_step("step-2", "agent-b", "fail_action", {"path": "f.py"})

    def fail_fn(params):
        raise RuntimeError("intentional failure")

    result = s.execute({
        "write_file": lambda p: {"ok": True},
        "fail_action": fail_fn,
        "delete_file": lambda p: {"compensated": True},
    })
    assert result.status == SagaStatus.COMPENSATED
    assert result.executed_count == 1
    assert result.compensated_count == 1


def test_saga_empty():
    s = A2ASaga("saga-3")
    result = s.execute({})
    assert result.status == SagaStatus.COMPLETED
    assert result.executed_count == 0


def test_saga_status_property():
    s = A2ASaga("saga-4")
    assert s.status == SagaStatus.PENDING
