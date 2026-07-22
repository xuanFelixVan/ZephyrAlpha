# [A_test] module_id: MOD-GOV_position_reconciler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_position_reconciler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_position_reconciler.py -q
# [TTL] task_bound
from zephyr.position.position_reconciler import PositionReconciler


class TestPositionReconcilerInstantiation:
    def test_creates_instance(self):
        reconciler = PositionReconciler()
        assert isinstance(reconciler, PositionReconciler)

    def test_has_reconcile_method(self):
        reconciler = PositionReconciler()
        assert callable(getattr(reconciler, "reconcile", None))

    def test_has_should_escalate_method(self):
        reconciler = PositionReconciler()
        assert callable(getattr(reconciler, "should_escalate", None))


class TestReconcile:
    def test_matching_positions(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100, "GOOG": 50}
        external = {"AAPL": 100, "GOOG": 50}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True
        assert result["diffs"] == {}
        assert result["count"] == 0

    def test_mismatched_positions(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100, "GOOG": 50}
        external = {"AAPL": 90, "GOOG": 50}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is False
        assert result["count"] == 1
        assert "AAPL" in result["diffs"]
        assert result["diffs"]["AAPL"]["internal"] == 100
        assert result["diffs"]["AAPL"]["external"] == 90
        assert result["diffs"]["AAPL"]["diff"] == 10

    def test_key_only_in_internal(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100, "MSFT": 30}
        external = {"AAPL": 100}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is False
        assert "MSFT" in result["diffs"]
        assert result["diffs"]["MSFT"]["internal"] == 30
        assert result["diffs"]["MSFT"]["external"] == 0
        assert result["diffs"]["MSFT"]["diff"] == 30

    def test_key_only_in_external(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100}
        external = {"AAPL": 100, "TSLA": 75}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is False
        assert "TSLA" in result["diffs"]
        assert result["diffs"]["TSLA"]["internal"] == 0
        assert result["diffs"]["TSLA"]["external"] == 75
        assert result["diffs"]["TSLA"]["diff"] == -75

    def test_both_empty(self):
        reconciler = PositionReconciler()
        result = reconciler.reconcile({}, {})
        assert result["match"] is True
        assert result["diffs"] == {}
        assert result["count"] == 0

    def test_multiple_mismatches(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100, "GOOG": 50, "MSFT": 30}
        external = {"AAPL": 90, "GOOG": 60, "MSFT": 30}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is False
        assert result["count"] == 2

    def test_diff_value_is_internal_minus_external(self):
        reconciler = PositionReconciler()
        internal = {"X": 200}
        external = {"X": 250}
        result = reconciler.reconcile(internal, external)
        assert result["diffs"]["X"]["diff"] == -50

    def test_result_structure(self):
        reconciler = PositionReconciler()
        result = reconciler.reconcile({}, {})
        assert "match" in result
        assert "diffs" in result
        assert "count" in result


class TestShouldEscalate:
    def test_below_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(1, threshold=3) is False

    def test_at_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(3, threshold=3) is True

    def test_above_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(5, threshold=3) is True

    def test_zero_diffs(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(0, threshold=3) is False

    def test_default_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(2) is False
        assert reconciler.should_escalate(3) is True

    def test_custom_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(4, threshold=5) is False
        assert reconciler.should_escalate(5, threshold=5) is True


class TestBoundaryConditions:
    def test_reconcile_with_zero_values(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 0}
        external = {"AAPL": 0}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True

    def test_reconcile_large_values(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 999999999}
        external = {"AAPL": 999999999}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True

    def test_reconcile_negative_values(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": -10}
        external = {"AAPL": -10}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True

    def test_should_escalate_threshold_one(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(0, threshold=1) is False
        assert reconciler.should_escalate(1, threshold=1) is True

    def test_reconcile_many_keys(self):
        reconciler = PositionReconciler()
        internal = {f"K{i}": i for i in range(100)}
        external = {f"K{i}": i for i in range(100)}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True
        assert result["count"] == 0

    def test_reconcile_single_key_diff(self):
        reconciler = PositionReconciler()
        internal = {"A": 1}
        external = {"A": 2}
        result = reconciler.reconcile(internal, external)
        assert result["count"] == 1
        assert result["diffs"]["A"]["diff"] == -1
