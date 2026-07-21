# [A_test] module_id: MOD-GOV_e_position_reconciler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_position_reconciler
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.position.position_reconciler import PositionReconciler


class TestPositionReconciler:
    def test_reconcile_identical(self):
        pr = PositionReconciler()
        result = pr.reconcile({"BTC": 10}, {"BTC": 10})
        assert result["match"] is True
        assert result["count"] == 0

    def test_reconcile_different(self):
        pr = PositionReconciler()
        result = pr.reconcile({"BTC": 10}, {"BTC": 12})
        assert result["match"] is False
        assert result["count"] == 1
        assert result["diffs"]["BTC"]["internal"] == 10
        assert result["diffs"]["BTC"]["external"] == 12
        assert result["diffs"]["BTC"]["diff"] == -2

    def test_reconcile_missing_key(self):
        pr = PositionReconciler()
        result = pr.reconcile({"BTC": 10}, {"ETH": 5})
        assert result["match"] is False
        assert result["count"] == 2

    def test_reconcile_empty(self):
        pr = PositionReconciler()
        result = pr.reconcile({}, {})
        assert result["match"] is True
        assert result["count"] == 0


class TestShouldEscalate:
    def test_default_threshold(self):
        pr = PositionReconciler()
        assert pr.should_escalate(3) is True
        assert pr.should_escalate(2) is False

    def test_custom_threshold(self):
        pr = PositionReconciler()
        assert pr.should_escalate(5, threshold=5) is True
        assert pr.should_escalate(4, threshold=5) is False

    def test_zero_diffs(self):
        pr = PositionReconciler()
        assert pr.should_escalate(0) is False
