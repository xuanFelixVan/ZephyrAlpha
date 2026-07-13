# [A_test] module_id: SRC-TST-0617 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_contract_bus
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_contract_bus.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip("zephyr.feedback_loop.capacity_assurance.contract_bus", reason="contract_bus not available")
ContractBusLoader = mod.ContractBusLoader
get_contract_bus_loader = mod.get_contract_bus_loader


class TestContractBusLoader:
    def test_instantiation(self):
        loader = ContractBusLoader()
        assert loader.contract_count == 44

    def test_batch_summary(self):
        loader = ContractBusLoader()
        summary = loader.batch_summary
        assert summary["batch1_infra"] == 15
        assert summary["batch2_governance"] == 15
        assert summary["batch3_integration"] == 14
        assert summary["total"] == 44

    def test_list_contracts_sorted(self):
        loader = ContractBusLoader()
        contracts = loader.list_contracts()
        assert len(contracts) == 44
        assert contracts == sorted(contracts)

    def test_get_contract_existing(self):
        loader = ContractBusLoader()
        ct = loader.get_contract("CT-SLO-001")
        assert ct is not None

    def test_get_contract_nonexistent(self):
        loader = ContractBusLoader()
        ct = loader.get_contract("CT-FAKE-999")
        assert ct is None

    def test_validate_payload_valid(self):
        loader = ContractBusLoader()
        result = loader.validate_payload(
            "CT-SLO-001",
            {
                "slo_id": "sli_1",
                "metric": "latency",
                "target": 0.999,
                "window": "5m",
                "severity": "critical",
            },
        )
        assert result.slo_id == "sli_1"

    def test_validate_payload_missing_field(self):
        loader = ContractBusLoader()
        with pytest.raises(Exception):
            loader.validate_payload("CT-SLO-001", {"slo_id": "sli_1"})

    def test_validate_payload_unknown_contract(self):
        loader = ContractBusLoader()
        with pytest.raises(KeyError, match="Contract not found"):
            loader.validate_payload("CT-FAKE-999", {})

    def test_get_contract_bus_loader_singleton(self):
        loader1 = get_contract_bus_loader()
        loader2 = get_contract_bus_loader()
        assert loader1 is loader2
