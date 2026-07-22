# [A_test] module_id: MOD-GOV_analytics_base_contract | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-588 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_analytics_base_contract
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""L07 analytics_base — OCP 扩展点抽象方法形状。"""


from zephyr.reporting.analytics_base import AttributionEngineBase, TCAEngineBase


def test_tca_engine_base_is_abstract() -> None:
    assert TCAEngineBase.__abstractmethods__ == frozenset({"analyze"})


def test_attribution_engine_base_is_abstract() -> None:
    assert AttributionEngineBase.__abstractmethods__ == frozenset({"attribute"})
