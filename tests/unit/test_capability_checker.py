"""能力检查器单元测试——capability_check + checksum校验 + 离线更新 T。"""

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


def test_grant_orchestrator_to_db(checker):
    assert checker.capability_check("orchestrator", "database", "write_taskcard")


def test_deny_pipeline_direct_to_db(checker):
    assert not checker.capability_check("pipeline", "database", "write_taskcard")


def test_checksum_consistent(checker, matrix):
    assert checker.get_checksum() == matrix.checksum


def test_audit_log_after_deny(checker):
    checker.capability_check("orchestrator", "llm_security", "check_safety")
    assert len(checker.audit_log()) >= 1
