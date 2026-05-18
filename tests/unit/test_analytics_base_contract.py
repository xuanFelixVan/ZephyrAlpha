# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.test_analytics_base_contract
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""L07 analytics_base — OCP 扩展点抽象方法形状。"""

from __future__ import annotations

from zephyr.l07_post_trade_analytics.analytics_base import AttributionEngineBase, TCAEngineBase


def test_tca_engine_base_is_abstract() -> None:
    assert TCAEngineBase.__abstractmethods__ == frozenset({"analyze"})


def test_attribution_engine_base_is_abstract() -> None:
    assert AttributionEngineBase.__abstractmethods__ == frozenset({"attribute"})
