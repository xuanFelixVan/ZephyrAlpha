# [A_test] module_id: SRC-TST-1004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_slo_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.slo_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_slo_manager.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.slo_manager import SLOManager


class TestSLOManagerInstantiation:
    def test_creates_instance(self):
        mgr = SLOManager()
        assert mgr is not None


class TestGetSlos:
    def test_returns_slo_for_known_contract(self):
        mgr = SLOManager()
        result = mgr.get_slos("CT-FLE-ORC-001")
        assert result is not None
        assert "slos" in result
        assert "metric" in result

    def test_returns_none_for_unknown_contract(self):
        mgr = SLOManager()
        result = mgr.get_slos("NONEXISTENT")
        assert result is None


class TestListContracts:
    def test_lists_all_contracts(self):
        mgr = SLOManager()
        contracts = mgr.list_contracts()
        assert len(contracts) > 0
        assert "CT-FLE-ORC-001" in contracts

    def test_contracts_are_strings(self):
        mgr = SLOManager()
        for c in mgr.list_contracts():
            assert isinstance(c, str)


class TestCheck:
    def test_passing_slo(self):
        mgr = SLOManager()
        passed, msg = mgr.check("CT-FLE-ORC-001", p95=10.0)
        assert passed is True
        assert msg == "OK"

    def test_failing_slo(self):
        mgr = SLOManager()
        passed, msg = mgr.check("CT-FLE-ORC-001", p95=100.0)
        assert passed is False

    def test_unknown_contract_passes(self):
        mgr = SLOManager()
        passed, msg = mgr.check("NONEXISTENT", p95=100.0)
        assert passed is True
        assert msg == "NO_SLO_DEFINED"

    def test_boundary_zero_p95(self):
        mgr = SLOManager()
        passed, msg = mgr.check("CT-FLE-ORC-001", p95=0.0)
        assert passed is True
