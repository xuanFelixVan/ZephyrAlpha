# [A_test] module_id: MOD-GOV_a2a_saga | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_a2a_saga
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_a2a_saga.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_saga import (
    A2ASaga,
    SagaResult,
    SagaStatus,
)


class TestA2ASaga:
    def test_create(self):
        saga = A2ASaga("saga-1")
        assert saga.status == SagaStatus.PENDING

    def test_add_step(self):
        saga = A2ASaga("saga-2")
        step = saga.add_step("step-1", "agent-a", "do_work", {"key": "val"})
        assert step.step_id == "step-1"
        assert step.agent_id == "agent-a"
        assert step.action_name == "do_work"
        assert step.executed is False

    def test_execute_all_success(self):
        saga = A2ASaga("saga-3")
        saga.add_step("s1", "agent-a", "action_a", {"x": 1})
        saga.add_step("s2", "agent-b", "action_b", {"y": 2})

        funcs = {
            "action_a": lambda p: {"result": "a_done"},
            "action_b": lambda p: {"result": "b_done"},
        }
        result = saga.execute(funcs)
        assert result.status == SagaStatus.COMPLETED
        assert result.executed_count == 2
        assert saga.status == SagaStatus.COMPLETED

    def test_execute_failure_triggers_compensation(self):
        saga = A2ASaga("saga-4")
        saga.add_step("s1", "agent-a", "good_action", {})
        saga.add_step("s2", "agent-b", "bad_action", {})

        compensated = []

        def bad_func(p):
            raise RuntimeError("boom")

        funcs = {
            "good_action": lambda p: {"ok": True},
            "bad_action": bad_func,
            "compensate_good_action": lambda p: compensated.append("s1"),
        }
        result = saga.execute(funcs)
        assert result.status == SagaStatus.COMPENSATED
        assert result.executed_count == 1
        assert result.compensated_count == 1
        assert "s1" in compensated

    def test_execute_with_default_action(self):
        saga = A2ASaga("saga-5")
        saga.add_step("s1", "agent-a", "unknown_action", {})
        result = saga.execute({})
        assert result.status == SagaStatus.COMPLETED

    def test_saga_result_properties(self):
        result = SagaResult(saga_id="test", status=SagaStatus.COMPLETED)
        assert result.executed_count == 0
        assert result.compensated_count == 0

    def test_add_step_with_compensate(self):
        saga = A2ASaga("saga-6")
        saga.add_step("s1", "a", "act", {}, compensate_action="undo_act", compensate_params={"undo": True})
        assert saga.compensations["s1"]["action"] == "undo_act"
        assert saga.compensations["s1"]["params"] == {"undo": True}
