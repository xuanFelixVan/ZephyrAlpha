# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.test_health_aggregator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""健康聚合器单元测试。"""

from __future__ import annotations

import pytest
from zephyr.l01_infrastructure.system_telemetry.health_aggregator import HealthAggregator, HealthProbeManager


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
