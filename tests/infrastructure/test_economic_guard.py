# [A_test] module_id: MOD-GOV_economic_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-310 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_economic_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Test Economic Guard — SSoT validation via escalation_models."""

from zephyr.governance.escalation.escalation_models import EconomicGuard


def test_within_budget():
    g = EconomicGuard("test-guard")
    ok = g.can_proceed(1.0)
    assert ok


def test_exceeds_daily_budget():
    g = EconomicGuard("test-guard2", daily_budget=5.0)
    g.consume(4.0)
    ok = g.can_proceed(2.0)
    assert not ok
