# [A_test] module_id: MOD-GOV_slo_manager_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-685 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_slo_manager
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-685 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""SLO 管理器单元测试。"""

# 治本：zephyr.ops 已迁移到 zephyr.feedback_loop（ARCH-032）。
from zephyr.feedback_loop.slo_manager import SLOManager


def test_12_contracts_defined():
    mgr = SLOManager()
    assert len(mgr.list_contracts()) == 12


def test_get_slos():
    mgr = SLOManager()
    slo = mgr.get_slos("CT-ORC-SCRIPT-001")
    assert slo is not None
    assert slo["slos"][0] == ("p95", 3600.0)


def test_check_fails_over_threshold():
    mgr = SLOManager()
    ok, reason = mgr.check("CT-ORC-CE-001", 5.0)
    assert not ok


def test_check_passes_under_threshold():
    mgr = SLOManager()
    ok, reason = mgr.check("CT-ORC-CE-001", 1.0)
    assert ok
