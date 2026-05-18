# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_economic_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""Test Economic Guard — SSoT validation via escalation_models."""
from zephyr.escalation_engine.escalation_models import EconomicGuard


def test_within_budget():
    g = EconomicGuard("test-guard")
    ok = g.can_proceed(1.0)
    assert ok


def test_exceeds_daily_budget():
    g = EconomicGuard("test-guard2", daily_budget=5.0)
    g.consume(4.0)
    ok = g.can_proceed(2.0)
    assert not ok
