# [A_test] module_id: MOD-GOV_broker_resilience | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-355 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_broker_resilience
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] BrokerLevel has 3 tiers; BROKER_FAILOVER keys match BrokerLevel enum
# [MODIFY-GUARD] Changes must sync with broker_resilience.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_broker_resilience.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.resilience_governance.broker_resilience import (
    BROKER_FAILOVER,
    EMERGENCY_LIQUIDATION_STEPS,
    BrokerFailure,
    BrokerLevel,
)


class TestBrokerLevel:
    def test_enum_values(self):
        assert BrokerLevel.P0_PRIMARY.value == "P0"
        assert BrokerLevel.P1_FALLBACK.value == "P1"
        assert BrokerLevel.P2_EMERGENCY.value == "P2"

    def test_enum_count(self):
        assert len(BrokerLevel) == 3

    def test_ordering(self):
        levels = [BrokerLevel.P0_PRIMARY, BrokerLevel.P1_FALLBACK, BrokerLevel.P2_EMERGENCY]
        values = [l.value for l in levels]
        assert values == sorted(values)


class TestBrokerFailure:
    def test_enum_values(self):
        assert BrokerFailure.API_LOST.value == "API_LOST"
        assert BrokerFailure.REJECT_ERROR.value == "REJECT_ERROR"
        assert BrokerFailure.GAP_FILL.value == "GAP_FILL"
        assert BrokerFailure.EXCHANGE_HALT.value == "EXCHANGE_HALT"

    def test_enum_count(self):
        assert len(BrokerFailure) == 4


class TestBrokerFailover:
    def test_keys_match_broker_level(self):
        assert set(BROKER_FAILOVER.keys()) == set(BrokerLevel)

    def test_all_values_are_strings(self):
        for key, value in BROKER_FAILOVER.items():
            assert isinstance(value, str), f"Value for {key} is not a string"

    def test_p0_is_primary(self):
        assert "Primary" in BROKER_FAILOVER[BrokerLevel.P0_PRIMARY]

    def test_p2_is_emergency(self):
        assert "应急" in BROKER_FAILOVER[BrokerLevel.P2_EMERGENCY]


class TestEmergencyLiquidationSteps:
    def test_is_list(self):
        assert isinstance(EMERGENCY_LIQUIDATION_STEPS, list)

    def test_non_empty(self):
        assert len(EMERGENCY_LIQUIDATION_STEPS) > 0

    def test_all_entries_are_strings(self):
        for step in EMERGENCY_LIQUIDATION_STEPS:
            assert isinstance(step, str)

    def test_has_detection_step(self):
        all_steps = " ".join(EMERGENCY_LIQUIDATION_STEPS)
        assert "检测" in all_steps or "P0" in all_steps
