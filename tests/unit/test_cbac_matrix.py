# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.test_cbac_matrix
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""CBAC 矩阵单元测试——18条capability + checksum防篡改。"""

from __future__ import annotations

import pytest
from zephyr.gates.cbac_matrix import CbacMatrix
from zephyr.gates.capability_checker import CapabilityChecker


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


def test_audit_log_records( checker):
    checker.capability_check("orchestrator", "script_system", "dispatch_task")
    checker.capability_check("script_system", "orchestrator", "invoke_gate")
    assert len(checker.audit_log()) >= 1
