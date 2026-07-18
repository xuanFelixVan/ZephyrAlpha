# [A_test] module_id: SRC-TST-2105 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-649 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_health_probes
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""HealthCheck 探针单元测试。"""


import pytest

from zephyr.infrastructure.system_telemetry.health_probes import HealthProbeManager


@pytest.fixture
def probes():
    return HealthProbeManager()


def test_liveness_all_systems(probes):
    for system in probes.list_systems():
        result = probes.liveness(system)
        assert result["status"] == "alive"
        assert "uptime_s" in result


def test_readiness_ok(probes):
    result = probes.readiness("orchestrator", deps_ok=True)
    assert result["status"] == "ready"


def test_readiness_down(probes):
    result = probes.readiness("orchestrator", deps_ok=False)
    assert result["status"] == "not_ready"


def test_healthz_healthy_default(probes):
    result = probes.healthz("orchestrator")
    assert result["status"] == "healthy"


def test_healthz_orchestrator_degraded(probes):
    result = probes.healthz("orchestrator", {"pending_queue": 150})
    assert result["status"] == "degraded"


def test_healthz_lsg_no_degraded(probes):
    result = probes.healthz("llm-security", {"token_budget": 8000})
    assert result["status"] == "healthy"


def test_healthz_db_degraded_wal_lag(probes):
    result = probes.healthz("database", {"wal_checkpoint_lag": 10.0})
    assert result["status"] == "degraded"


def test_list_12_systems(probes):
    assert len(probes.list_systems()) == 12
