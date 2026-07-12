# [A_test] module_id: SRC-TST-1433 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_reconciliation_loop
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_reconciliation_loop.py
# [TTL] task_bound


from zephyr.orchestrator.execution.reconciliation_loop import (
    RECONCILE_INVARIANTS,
    Invariant,
    ReconcileResult,
    ReconciliationLoop,
)


class TestInvariantModel:
    def test_create_default(self):
        inv = Invariant(name="test")
        assert inv.name == "test"
        assert inv.current == ""
        assert inv.expected == ""
        assert inv.ok is True

    def test_create_with_values(self):
        inv = Invariant(name="check", current="fail", expected="ok", ok=False)
        assert inv.ok is False
        assert inv.current == "fail"


class TestReconcileResultModel:
    def test_create_default(self):
        result = ReconcileResult()
        assert result.all_ok is True
        assert result.invariants == []
        assert result.timestamp is not None

    def test_create_with_invariants(self):
        invs = [Invariant(name="a", ok=True), Invariant(name="b", ok=False)]
        result = ReconcileResult(invariants=invs, all_ok=False)
        assert len(result.invariants) == 2
        assert result.all_ok is False


class TestReconcileInvariantsConstant:
    def test_has_five_invariants(self):
        assert len(RECONCILE_INVARIANTS) == 5

    def test_contains_contract_checksums(self):
        assert "contract_checksums_consistent" in RECONCILE_INVARIANTS

    def test_contains_circuit_breaker(self):
        assert "circuit_breaker_states_valid" in RECONCILE_INVARIANTS

    def test_contains_cbac_matrix(self):
        assert "cbac_matrix_checksum_valid" in RECONCILE_INVARIANTS

    def test_contains_taskcard_pipeline(self):
        assert "taskcard_status_pipeline_valid" in RECONCILE_INVARIANTS

    def test_contains_dlq_count(self):
        assert "dlq_message_count" in RECONCILE_INVARIANTS


class TestReconciliationLoopInstantiation:
    def test_create_instance(self):
        loop = ReconciliationLoop()
        assert loop is not None

    def test_has_reconcile_method(self):
        loop = ReconciliationLoop()
        assert callable(loop.reconcile)

    def test_has_get_invariants_method(self):
        loop = ReconciliationLoop()
        assert callable(loop.get_invariants)


class TestReconcile:
    def test_reconcile_with_no_states(self):
        loop = ReconciliationLoop()
        result = loop.reconcile()
        assert result.all_ok is True
        assert len(result.invariants) == 5

    def test_reconcile_with_all_ok(self):
        loop = ReconciliationLoop()
        states = {name: True for name in RECONCILE_INVARIANTS}
        result = loop.reconcile(states=states)
        assert result.all_ok is True

    def test_reconcile_with_one_failure(self):
        loop = ReconciliationLoop()
        states = {"contract_checksums_consistent": False}
        result = loop.reconcile(states=states)
        assert result.all_ok is False

    def test_reconcile_with_all_failures(self):
        loop = ReconciliationLoop()
        states = {name: False for name in RECONCILE_INVARIANTS}
        result = loop.reconcile(states=states)
        assert result.all_ok is False
        assert all(not inv.ok for inv in result.invariants)

    def test_reconcile_stores_result(self):
        loop = ReconciliationLoop()
        loop.reconcile()
        loop.reconcile()
        assert len(loop._results) == 2

    def test_reconcile_invariant_has_correct_name(self):
        loop = ReconciliationLoop()
        result = loop.reconcile()
        names = [inv.name for inv in result.invariants]
        assert names == list(RECONCILE_INVARIANTS)

    def test_reconcile_partial_states(self):
        loop = ReconciliationLoop()
        states = {"contract_checksums_consistent": False}
        result = loop.reconcile(states=states)
        failed = [inv for inv in result.invariants if not inv.ok]
        assert len(failed) == 1
        assert failed[0].name == "contract_checksums_consistent"


class TestGetInvariants:
    def test_returns_list(self):
        loop = ReconciliationLoop()
        result = loop.get_invariants()
        assert isinstance(result, list)

    def test_returns_all_invariant_names(self):
        loop = ReconciliationLoop()
        result = loop.get_invariants()
        assert result == list(RECONCILE_INVARIANTS)

    def test_returns_copy(self):
        loop = ReconciliationLoop()
        result = loop.get_invariants()
        result.append("extra")
        assert "extra" not in loop.get_invariants()
