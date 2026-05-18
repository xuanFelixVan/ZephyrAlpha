# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.test_slo_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""SLO 管理器单元测试。"""

import pytest
from zephyr.feedback_loop.slo_manager import SLOManager


def test_14_contracts_defined():
    mgr = SLOManager()
    assert len(mgr.list_contracts()) == 14


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
