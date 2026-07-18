# [A_test] module_id: SRC-TST-1999 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-616 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_contract_metrics
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""system-telemetry.contract_metrics 框架单测。"""


from zephyr.infrastructure.system_telemetry.contract_metrics import (
    ContractMetricsCollector,
    get_contract_metrics,
)


def test_measure_sla_respects_budget() -> None:
    c = ContractMetricsCollector()
    r = c.measure_sla("CTR-001", "trace", 5000, 10_000)
    assert r.passed is True
    r2 = c.measure_sla("CTR-001", "trace", 50_000, 10_000)
    assert r2.passed is False


def test_record_violation_increments() -> None:
    c = ContractMetricsCollector()
    c.record_violation("CTR-ERR-006")
    c.record_violation("CTR-ERR-006")
    stats = c.get_stats()
    assert stats["total_violations"] == 2


def test_get_contract_metrics_singleton() -> None:
    a = get_contract_metrics()
    b = get_contract_metrics()
    assert a is b
