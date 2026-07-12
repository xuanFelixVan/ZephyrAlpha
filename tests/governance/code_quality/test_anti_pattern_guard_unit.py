# [A_test] module_id: SRC-TST-1973 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-590 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_anti_pattern_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""Anti-Patterns 防护单元测试——逐条验证 AP1~AP8。"""


import pytest

from zephyr.gov_enforcement.rule_enforcement.anti_pattern_guard import AntiPatternGuard


@pytest.fixture
def guard():
    return AntiPatternGuard()


class TestAP1BypassContract:
    def test_ap1_reject_no_ct(self, guard):
        result = guard.check_ap1_bypass_contract("unknown_system", False, "agent-001")
        assert result is False
        assert len(guard.violations()) == 1
        assert guard.violations()[0].ap_id == "AP1"

    def test_ap1_allow_with_ct(self, guard):
        result = guard.check_ap1_bypass_contract("script_system", True, "agent-001")
        assert result is True


class TestAP2SilentException:
    def test_ap2_reject_no_audit_log(self, guard):
        result = guard.check_ap2_silent_exception(False, "agent-002")
        assert result is False
        assert guard.violations()[-1].ap_id == "AP2"

    def test_ap2_allow_with_audit_log(self, guard):
        result = guard.check_ap2_silent_exception(True, "agent-002")
        assert result is True


class TestAP3CircuitBreaker:
    def test_ap3_reject_circuit_open(self, guard):
        result = guard.check_ap3_ignore_circuit_breaker(True, "agent-003")
        assert result is False
        assert guard.violations()[-1].ap_id == "AP3"

    def test_ap3_allow_circuit_closed(self, guard):
        result = guard.check_ap3_ignore_circuit_breaker(False, "agent-003")
        assert result is True


class TestAP4CodeOverDocument:
    def test_ap4_reject_code_differs(self, guard):
        result = guard.check_ap4_code_over_document(62, 74, "TaskCard.field_count", "agent-004")
        assert result is False
        assert guard.violations()[-1].ap_id == "AP4"

    def test_ap4_allow_consistent(self, guard):
        result = guard.check_ap4_code_over_document(62, 62, "TaskCard.field_count", "agent-004")
        assert result is True


class TestAP5ModifyUpstream:
    def test_ap5_reject_no_finding(self, guard):
        result = guard.check_ap5_modify_upstream(True, False, "agent-005")
        assert result is False
        assert guard.violations()[-1].ap_id == "AP5"

    def test_ap5_allow_with_finding(self, guard):
        result = guard.check_ap5_modify_upstream(True, True, "agent-005")
        assert result is True

    def test_ap5_allow_not_upstream(self, guard):
        result = guard.check_ap5_modify_upstream(False, False, "agent-005")
        assert result is True


class TestAP6SharedState:
    def test_ap6_reject_non_ct_path(self, guard):
        result = guard.check_ap6_shared_mutable_state("/tmp/shared", False, "agent-006")
        assert result is False
        assert guard.violations()[-1].ap_id == "AP6"

    def test_ap6_allow_ct_path(self, guard):
        result = guard.check_ap6_shared_mutable_state("CT-ORC-SCRIPT-001", True, "agent-006")
        assert result is True


class TestAP7GateDecision:
    def test_ap7_reject_gate_fail(self, guard):
        result = guard.check_ap7_ignore_gate_decision("FAIL", "agent-007")
        assert result is False
        assert guard.violations()[-1].ap_id == "AP7"

    def test_ap7_allow_gate_pass(self, guard):
        result = guard.check_ap7_ignore_gate_decision("PASS", "agent-007")
        assert result is True


class TestAP8SessionOrphan:
    def test_ap8_reject_orphans(self, guard):
        result = guard.check_ap8_session_orphan_tasks(3, "session-001", "agent-008")
        assert result is False
        assert guard.violations()[-1].ap_id == "AP8"

    def test_ap8_allow_no_orphans(self, guard):
        result = guard.check_ap8_session_orphan_tasks(0, "session-001", "agent-008")
        assert result is True
