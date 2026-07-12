# [A_test] module_id: SRC-TST-1983 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-601 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_capability_checker
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""能力检查器单元测试——capability_check + checksum校验 + 离线更新 T。"""


import pytest

from zephyr.gov_enforcement.rule_enforcement.capability_checker import CapabilityChecker
from zephyr.gov_enforcement.rule_enforcement.cbac_matrix import CbacMatrix


@pytest.fixture
def matrix():
    return CbacMatrix()


@pytest.fixture
def checker(matrix):
    return CapabilityChecker(matrix)


def test_grant_orchestrator_to_db(checker):
    assert checker.capability_check("orchestrator", "database", "write_taskcard")


def test_deny_pipeline_direct_to_db(checker):
    assert not checker.capability_check("pipeline", "database", "write_taskcard")


def test_checksum_consistent(checker, matrix):
    assert checker.get_checksum() == matrix.checksum


def test_audit_log_after_deny(checker):
    checker.capability_check("orchestrator", "llm-security", "check_safety")
    assert len(checker.audit_log()) >= 1
