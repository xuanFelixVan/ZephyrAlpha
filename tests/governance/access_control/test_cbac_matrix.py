# [A_test] module_id: SRC-TST-1986 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-603 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_cbac_matrix
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""CBAC 矩阵单元测试——18条capability + checksum防篡改。"""


import pytest

from zephyr.gov_enforcement.rule_enforcement.capability_checker import CapabilityChecker
from zephyr.gov_enforcement.rule_enforcement.cbac_matrix import CbacMatrix


@pytest.fixture
def matrix():
    return CbacMatrix()


@pytest.fixture
def checker(matrix):
    return CapabilityChecker(matrix)


def test_18_capabilities(matrix):
    assert len(matrix.list_capabilities()) == 18


def test_checksum_not_empty(matrix):
    assert len(matrix.checksum) > 0


def test_grant_valid_capability(checker):
    assert checker.capability_check("orchestrator", "script_system", "dispatch_task")


def test_deny_invalid_capability(checker):
    assert not checker.capability_check("script_system", "orchestrator", "invoke_gate")


def test_deny_unknown_action(checker):
    assert not checker.capability_check("orchestrator", "script_system", "shutdown")


def test_audit_log_records(checker):
    checker.capability_check("orchestrator", "script_system", "dispatch_task")
    checker.capability_check("script_system", "orchestrator", "invoke_gate")
    assert len(checker.audit_log()) >= 1
