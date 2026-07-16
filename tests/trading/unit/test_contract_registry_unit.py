# [A_test] module_id: SRC-TST-2000 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-617 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_contract_registry
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""Contract registry unit tests -- CT-* contracts registered and ai_read_only_hint checked."""


import pytest

from zephyr.orchestrator.contracts.contract_registry import (
    CONTRACTS,
    AIReadOnlyHint,
    ContractRegistry,
)


@pytest.fixture
def registry():
    return ContractRegistry()


class TestContractCount:
    def test_contracts_registered(self):
        assert len(CONTRACTS) >= 60

    def test_all_have_route_target(self, registry):
        for c in registry.list_all():
            assert c.route_target != ""


class TestGet:
    def test_get_valid_contract(self, registry):
        contract = registry.get("CT-ORC-SCRIPT-001")
        assert contract is not None
        assert contract.producer == "Orchestrator"
        assert contract.consumer == "Script System"

    def test_get_invalid_contract(self, registry):
        contract = registry.get("CT-NONEXISTENT")
        assert contract is None


class TestListAll:
    def test_list_all_returns_contracts(self, registry):
        contracts = registry.list_all()
        assert len(contracts) >= 60

    def test_list_ids_returns_contracts(self, registry):
        ids = registry.list_ids()
        assert len(ids) >= 60
        assert "CT-ORC-SCRIPT-001" in ids


class TestCheckAIReadOnly:
    def test_do_not_call_rejected(self, registry):
        result = registry.check_ai_read_only("CT-ORC-CE-001")
        assert result.allowed is False
        assert result.hint == AIReadOnlyHint.DO_NOT_CALL
        assert "not" in result.message.lower() or "not yet" in result.message.lower()

    def test_impl_required_rejected(self, registry):
        result = registry.check_ai_read_only("CT-SCRIPT-KB-001")
        assert result.allowed is False
        assert result.hint == AIReadOnlyHint.IMPL_REQUIRED

    def test_caution_stub_allowed_with_warning(self, registry):
        result = registry.check_ai_read_only("CT-ORC-SCRIPT-001")
        assert result.allowed is True
        assert result.hint == AIReadOnlyHint.CAUTION_STUB

    def test_safe_allowed(self, registry):
        result = registry.check_ai_read_only("CT-PIPE-ORC-001")
        assert result.allowed is True
        assert result.hint == AIReadOnlyHint.SAFE

    def test_nonexistent_contract_rejected(self, registry):
        result = registry.check_ai_read_only("CT-NONEXISTENT")
        assert result.allowed is False


class TestFilterBy:
    def test_get_by_producer_orchestrator(self, registry):
        contracts = registry.get_by_producer("Orchestrator")
        assert len(contracts) >= 20

    def test_get_by_consumer_gate_engine(self, registry):
        contracts = registry.get_by_consumer("Gate Engine")
        assert len(contracts) >= 5
