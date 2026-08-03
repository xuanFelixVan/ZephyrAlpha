# [A_test] module_id: MOD-GOV_fsm_verifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_fsm_verifier
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] Git-native回滚;SQLite Dump Checkpoint;自动回滚
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/rollback-system/blueprint.md
# [CONSUMERS] CI
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [A_module] module_id=MOD-INF-021 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.financial_governance.fsm_verifier import (
    FSM_INITIAL,
    FSM_INVARIANTS,
    FSM_TERMINAL,
    FSM_TRANSITIONS,
    FSMInstance,
    FSMSpec,
    FSMState,
    FSMTransition,
    generate_test_cases,
    reconcile_state,
)


class TestFSMState:
    def test_all_states_exist(self):
        assert FSMState.PENDING.value == "PENDING"
        assert FSMState.ACK.value == "ACK"
        assert FSMState.PARTIAL_FILL.value == "PARTIAL_FILL"
        assert FSMState.FILLED.value == "FILLED"
        assert FSMState.REJECTED.value == "REJECTED"
        assert FSMState.CANCELLED.value == "CANCELLED"

    def test_initial_is_pending(self):
        assert FSM_INITIAL == FSMState.PENDING

    def test_terminal_states(self):
        assert FSMState.FILLED in FSM_TERMINAL
        assert FSMState.REJECTED in FSM_TERMINAL
        assert FSMState.CANCELLED in FSM_TERMINAL
        assert len(FSM_TERMINAL) == 3


class TestFSMTransition:
    def test_transition_creation(self):
        t = FSMTransition(from_state=FSMState.PENDING, event="ack_received", to_state=FSMState.ACK)
        assert t.from_state == FSMState.PENDING
        assert t.event == "ack_received"
        assert t.to_state == FSMState.ACK

    def test_transitions_list_not_empty(self):
        assert len(FSM_TRANSITIONS) > 0


class TestFSMInstance:
    def test_instantiation_default_state(self):
        inst = FSMInstance(entity_id="order-1")
        assert inst.current_state == FSMState.PENDING
        assert inst.entity_id == "order-1"

    def test_apply_valid_transition(self):
        inst = FSMInstance(entity_id="order-2")
        result = inst.apply("ack_received")
        assert result is True
        assert inst.current_state == FSMState.ACK

    def test_apply_invalid_transition(self):
        inst = FSMInstance(entity_id="order-3")
        result = inst.apply("fill")
        assert result is False
        assert inst.current_state == FSMState.PENDING

    def test_no_transition_from_terminal(self):
        inst = FSMInstance(entity_id="order-4", current_state=FSMState.FILLED)
        result = inst.apply("ack_received")
        assert result is False
        assert inst.current_state == FSMState.FILLED

    def test_full_happy_path(self):
        inst = FSMInstance(entity_id="order-5")
        assert inst.apply("ack_received") is True
        assert inst.apply("fill") is True
        assert inst.current_state == FSMState.FILLED

    def test_partial_fill_path(self):
        inst = FSMInstance(entity_id="order-6")
        assert inst.apply("ack_received") is True
        assert inst.apply("partial_fill") is True
        assert inst.current_state == FSMState.PARTIAL_FILL
        assert inst.apply("fill") is True
        assert inst.current_state == FSMState.FILLED

    def test_cancel_from_ack(self):
        inst = FSMInstance(entity_id="order-7")
        inst.apply("ack_received")
        assert inst.apply("cancel") is True
        assert inst.current_state == FSMState.CANCELLED

    def test_reject_from_pending(self):
        inst = FSMInstance(entity_id="order-8")
        assert inst.apply("reject") is True
        assert inst.current_state == FSMState.REJECTED

    def test_no_transition_from_cancelled(self):
        inst = FSMInstance(entity_id="order-9", current_state=FSMState.CANCELLED)
        assert inst.apply("ack_received") is False
        assert inst.apply("fill") is False

    def test_no_transition_from_rejected(self):
        inst = FSMInstance(entity_id="order-10", current_state=FSMState.REJECTED)
        assert inst.apply("ack_received") is False

    def test_empty_event(self):
        inst = FSMInstance(entity_id="order-11")
        assert inst.apply("") is False


class TestFSMSpec:
    def test_default_spec(self):
        spec = FSMSpec()
        assert spec.initial == FSMState.PENDING
        assert len(spec.states) == len(FSMState)
        assert len(spec.transitions) == len(FSM_TRANSITIONS)
        assert len(spec.invariants) == len(FSM_INVARIANTS)

    def test_custom_spec(self):
        spec = FSMSpec(
            states=[FSMState.PENDING, FSMState.FILLED],
            initial=FSMState.PENDING,
            terminal=[FSMState.FILLED],
            transitions=[],
            invariants=["test invariant"],
        )
        assert len(spec.states) == 2
        assert len(spec.invariants) == 1


class TestGenerateTestCases:
    def test_generates_valid_and_invalid(self):
        spec = FSMSpec()
        cases = generate_test_cases(spec)
        assert "valid" in cases
        assert "invalid" in cases
        assert len(cases["valid"]) == len(FSM_TRANSITIONS)
        assert len(cases["invalid"]) == len(FSM_TERMINAL)

    def test_valid_test_names_format(self):
        spec = FSMSpec()
        cases = generate_test_cases(spec)
        for name in cases["valid"]:
            assert name.startswith("test_CAN_")

    def test_invalid_test_names_format(self):
        spec = FSMSpec()
        cases = generate_test_cases(spec)
        for name in cases["invalid"]:
            assert name.startswith("test_CANNOT_")

    def test_empty_spec(self):
        spec = FSMSpec(transitions=[], terminal=[])
        cases = generate_test_cases(spec)
        assert cases["valid"] == []
        assert cases["invalid"] == []


class TestReconcileState:
    def test_consistent_states(self):
        state, msg = reconcile_state(FSMState.ACK, FSMState.ACK)
        assert state == FSMState.ACK
        assert "consistent" in msg

    def test_inconsistent_states_uses_broker(self):
        state, msg = reconcile_state(FSMState.PENDING, FSMState.ACK)
        assert state == FSMState.ACK
        assert "broker" in msg.lower() or "source of truth" in msg.lower()

    def test_terminal_vs_terminal(self):
        state, msg = reconcile_state(FSMState.FILLED, FSMState.REJECTED)
        assert state == FSMState.REJECTED

    def test_same_terminal_state(self):
        state, msg = reconcile_state(FSMState.CANCELLED, FSMState.CANCELLED)
        assert state == FSMState.CANCELLED
        assert "consistent" in msg
