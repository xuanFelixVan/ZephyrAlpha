# [A_test] module_id: SRC-TST-1664 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_slo_manager
# [INVARIANTS] SLO_MATRIX keys must match CT-* contract IDs; check() returns (bool, str)
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound


from zephyr.feedback_loop.slo_manager import SLO_MATRIX, SLOManager


class TestSLOManagerInstantiation:
    def test_init(self):
        mgr = SLOManager()
        assert mgr is not None


class TestSLOManagerGetSLOs:
    def test_get_existing_contract(self):
        mgr = SLOManager()
        slo = mgr.get_slos("CT-ORC-SCRIPT-001")
        assert slo is not None
        assert "slos" in slo
        assert "metric" in slo

    def test_get_nonexistent_contract(self):
        mgr = SLOManager()
        slo = mgr.get_slos("CT-NONEXISTENT-999")
        assert slo is None

    def test_slo_has_p95_or_p99(self):
        mgr = SLOManager()
        for cid in mgr.list_contracts():
            slo = mgr.get_slos(cid)
            percentiles = {p for p, _ in slo["slos"]}
            assert percentiles & {"p95", "p99"}, f"{cid} has no p95/p99"


class TestSLOManagerListContracts:
    def test_list_contracts_count(self):
        mgr = SLOManager()
        contracts = mgr.list_contracts()
        assert len(contracts) == len(SLO_MATRIX)

    def test_list_contracts_returns_list(self):
        mgr = SLOManager()
        contracts = mgr.list_contracts()
        assert isinstance(contracts, list)
        assert all(isinstance(c, str) for c in contracts)


class TestSLOManagerCheck:
    def test_check_within_slo(self):
        mgr = SLOManager()
        ok, msg = mgr.check("CT-ORC-SCRIPT-001", 100.0)
        assert ok is True
        assert msg == "OK"

    def test_check_exceeds_slo(self):
        mgr = SLOManager()
        ok, msg = mgr.check("CT-ORC-SCRIPT-001", 5000.0)
        assert ok is False
        assert "p95" in msg

    def test_check_unknown_contract(self):
        mgr = SLOManager()
        ok, msg = mgr.check("CT-NONEXISTENT-999", 100.0)
        assert ok is True
        assert msg == "NO_SLO_DEFINED"

    def test_check_p99_contract_within(self):
        mgr = SLOManager()
        ok, msg = mgr.check("CT-ORC-VMS-001", 0.5)
        assert ok is True

    def test_check_p99_contract_exceeds(self):
        mgr = SLOManager()
        ok, msg = mgr.check("CT-ORC-VMS-001", 5.0)
        assert ok is False

    def test_check_zero_latency(self):
        mgr = SLOManager()
        ok, msg = mgr.check("CT-ORC-SCRIPT-001", 0.0)
        assert ok is True
