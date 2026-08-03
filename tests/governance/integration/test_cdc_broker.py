# [A_test] module_id: MOD-GOV_cdc_broker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-604 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_cdc_broker
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-604 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations

"""CDC 经纪人单元测试。"""


import pytest

from zephyr.gov_enforcement.rule_enforcement.cdc_broker import CdcBroker


@pytest.fixture
def broker():
    return CdcBroker()


def test_register_expectation(broker):
    exp = broker.register_expectation("script_system", "orchestrator", "CT-ORC-SCRIPT-001", "v1.0.0")
    assert exp.consumer == "script_system"


def test_get_expectations_for_producer(broker):
    broker.register_expectation("script_system", "orchestrator", "CT-ORC-SCRIPT-001", "v1.0.0")
    broker.register_expectation("gate_engine", "orchestrator", "CT-ORC-GATE-001", "v1.0.0")
    exps = broker.get_expectations("orchestrator")
    assert len(exps) == 2


def test_verify_pact(broker):
    pact = broker.verify_pact("PACT-001", "script_system", "orchestrator", "CT-ORC-SCRIPT-001", "v1.0.0")
    assert pact.verified is True
    assert len(broker.get_pacts()) == 1
