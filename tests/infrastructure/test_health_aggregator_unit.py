# [A_test] module_id: SRC-TST-2031 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-648 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_health_aggregator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""健康聚合器单元测试。"""


import pytest

from zephyr.infrastructure.system_telemetry.health_aggregator import HealthAggregator, HealthProbeManager


@pytest.fixture
def aggregator():
    return HealthAggregator(HealthProbeManager())


def test_poll_all_returns_12(aggregator):
    results = aggregator.poll_all()
    assert len(results) == 12


def test_all_systems_in_result(aggregator):
    results = aggregator.poll_all()
    systems = {r.system for r in results}
    assert "orchestrator" in systems
    assert "pipeline" in systems


def test_latest_snapshots(aggregator):
    aggregator.poll_all()
    latest = aggregator.latest_snapshots()
    assert len(latest) == 12


def test_annual_report(aggregator):
    report = aggregator.annual_report(2026, {}, {}, {})
    assert report.year == 2026
