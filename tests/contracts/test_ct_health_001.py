# [A_test] module_id: SRC-TST-0100 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-258 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_health_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-HEALTH-001 集成测试——三态健康探针：liveness / readiness / healthz。"""

from __future__ import annotations

from zephyr.infrastructure.system_telemetry.health_probes import (
    SPECIAL_RULES,
    SYSTEMS,
    HealthProbeManager,
    ProbeStatus,
)
from zephyr.orchestrator.contracts.contract_registry import ContractRegistry
from zephyr.orchestrator.contracts.contract_router import ContractRouter


def test_ct_health_registered():
    contract = ContractRegistry().get("CT-HEALTH-001")
    assert contract is not None
    assert contract.producer == "System Telemetry"
    assert contract.consumer == "全系统"


def test_ct_health_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-HEALTH-001")
    assert result.allowed is True
    assert "部分功能" in result.message


def test_ct_health_route():
    router = ContractRouter(ContractRegistry())
    result = router.route("CT-HEALTH-001")
    assert result.target_system == "telemetry"


def test_probe_status_enum():
    assert ProbeStatus.HEALTHY == "healthy"
    assert ProbeStatus.DEGRADED == "degraded"
    assert ProbeStatus.UNHEALTHY == "unhealthy"
    assert len(ProbeStatus) == 3


def test_systems_are_12():
    assert len(SYSTEMS) == 12
    assert "orchestrator" in SYSTEMS
    assert "mcp_servers" in SYSTEMS


def test_special_rules_have_expected_keys():
    assert "orchestrator" in SPECIAL_RULES
    assert "context-engine" in SPECIAL_RULES
    assert "llm-security" in SPECIAL_RULES
    assert "database" in SPECIAL_RULES
    assert SPECIAL_RULES["llm-security"]["no_degraded"] is True


def test_health_manager_liveness():
    mgr = HealthProbeManager()
    result = mgr.liveness("orchestrator")
    assert result["status"] == "alive"
    assert result["system"] == "orchestrator"
    assert result["uptime_s"] >= 0


def test_health_manager_readiness_ok():
    mgr = HealthProbeManager()
    result = mgr.readiness("database", deps_ok=True)
    assert result["status"] == "ready"


def test_health_manager_readiness_not_ok():
    mgr = HealthProbeManager()
    result = mgr.readiness("database", deps_ok=False)
    assert result["status"] == "not_ready"
    assert result["dependencies"]["db"] == "down"


def test_health_manager_healthz_orchestrator_healthy():
    mgr = HealthProbeManager()
    result = mgr.healthz("orchestrator", {"pending_queue": 50})
    assert result["status"] == "healthy"


def test_health_manager_healthz_orchestrator_degraded():
    mgr = HealthProbeManager()
    result = mgr.healthz("orchestrator", {"pending_queue": 150})
    assert result["status"] == "degraded"
    assert "pending_queue" in result["degraded_details"]


def test_health_manager_healthz_llm_security_never_degraded():
    mgr = HealthProbeManager()
    result = mgr.healthz("llm-security", {"token_budget": 9999})
    assert result["status"] == "healthy"


def test_health_manager_healthz_unknown_system():
    mgr = HealthProbeManager()
    result = mgr.healthz("nonexistent_system")
    assert result["status"] == "healthy"


def test_health_manager_list_systems():
    mgr = HealthProbeManager()
    systems = mgr.list_systems()
    assert len(systems) == 12
