"""CDC 经纪人单元测试。"""

from __future__ import annotations

import pytest
from zephyr.gates.cdc_broker import CdcBroker


@pytest.fixture
def broker():
    return CdcBroker()


def test_register_expectation(broker):
    exp = broker.register_expectation("script_system", "orchestrator", "CT-ORC-SCRIPT-001", "v1.0.0")
    assert exp.consumer == "script_system"


def test_get_expectations_for_producer(broker):
    broker.register_expectation("script_system", "orchestrator", "CT-ORC-SCRIPT-001", "v1.0.0")
    broker.register_expectation("knowledge_base", "orchestrator", "CT-ORC-CE-001", "v1.0.0")
    exps = broker.get_expectations("orchestrator")
    assert len(exps) == 2


def test_verify_pact(broker):
    pact = broker.verify_pact("PACT-001", "script_system", "orchestrator", "CT-ORC-SCRIPT-001", "v1.0.0")
    assert pact.verified is True
    assert len(broker.get_pacts()) == 1
