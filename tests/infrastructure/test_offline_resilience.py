# [A_test] module_id: MOD-GOV_offline_resilience | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-413 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_offline_resilience
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.offline_resilience import (
    DECAY_RATE_PER_24H,
    DECAY_START_HOURS,
    E2E_BUDGET_BREAKDOWN_MS,
    E2E_TARGET_MS,
    MAX_DECAY_HOURS,
    TIFLevel,
)


class TestTIFLevel:
    def test_enum_values(self):
        assert TIFLevel.L1 == "L1_<5m"
        assert TIFLevel.L2 == "L2_5-30m"
        assert TIFLevel.L3 == "L3_30m-4h"
        assert TIFLevel.L4 == "L4_4-24h"
        assert TIFLevel.L5 == "L5_24h+"

    def test_enum_members_count(self):
        assert len(TIFLevel) == 5


class TestConstants:
    def test_decay_start_hours(self):
        assert DECAY_START_HOURS == 8
        assert isinstance(DECAY_START_HOURS, int)

    def test_decay_rate(self):
        assert DECAY_RATE_PER_24H == 0.25
        assert isinstance(DECAY_RATE_PER_24H, float)

    def test_max_decay_hours(self):
        assert MAX_DECAY_HOURS == 72
        assert isinstance(MAX_DECAY_HOURS, int)

    def test_e2e_target_ms(self):
        assert E2E_TARGET_MS == 460
        assert isinstance(E2E_TARGET_MS, int)

    def test_e2e_budget_breakdown_keys(self):
        assert "MARKETDATA" in E2E_BUDGET_BREAKDOWN_MS
        assert "SIGNAL" in E2E_BUDGET_BREAKDOWN_MS
        assert "RISK" in E2E_BUDGET_BREAKDOWN_MS

    def test_e2e_budget_breakdown_values_positive(self):
        for key, val in E2E_BUDGET_BREAKDOWN_MS.items():
            assert val > 0, f"{key} budget must be positive"
