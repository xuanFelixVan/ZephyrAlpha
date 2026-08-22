# [A_test] module_id: MOD-GOV_stop_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_stop_gate
# [INVARIANTS] StopGate是无状态检查;check返回StopGateResult
# [MODIFY-GUARD] src/zephyr/runtime/stop_gate.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check返回StopGateResult;can_stop返回bool;acknowledge_shutdown无返回
# [TESTS] tests/test_stop_gate.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.trading.stop_gate import StopGate, StopGateResult


class TestStopGateInit:
    def test_default_state(self):
        gate = StopGate()
        assert gate.session_start == ""
        assert gate.shutdown_acknowledged is False

    def test_initialize_sets_session_start(self):
        gate = StopGate()
        gate.initialize()
        assert gate.session_start != ""
        assert gate.shutdown_acknowledged is False


class TestCheck:
    def test_all_pass(self):
        gate = StopGate()
        result = gate.check(
            audit_has_new_entries=True,
            night_shift_all_resolved=True,
            dream_cycle_archived=True,
            git_clean=True,
        )
        assert result.can_stop is True
        assert result.reasons == []

    def test_audit_missing(self):
        gate = StopGate()
        result = gate.check(audit_has_new_entries=False)
        assert result.can_stop is False
        assert any("AiAuditLogger" in r for r in result.reasons)

    def test_night_shift_unresolved(self):
        gate = StopGate()
        result = gate.check(night_shift_all_resolved=False)
        assert result.can_stop is False
        assert any("NightShiftQueue" in r for r in result.reasons)

    def test_dream_cycle_unarchived(self):
        gate = StopGate()
        result = gate.check(dream_cycle_archived=False)
        assert result.can_stop is False
        assert any("DreamCycle" in r for r in result.reasons)

    def test_git_dirty(self):
        gate = StopGate()
        result = gate.check(git_clean=False)
        assert result.can_stop is False
        assert any("Git" in r for r in result.reasons)

    def test_multiple_failures(self):
        gate = StopGate()
        result = gate.check(
            audit_has_new_entries=False,
            night_shift_all_resolved=False,
            dream_cycle_archived=False,
            git_clean=False,
        )
        assert result.can_stop is False
        assert len(result.reasons) == 4

    def test_default_all_true(self):
        gate = StopGate()
        result = gate.check()
        assert result.can_stop is True


class TestCanStop:
    def test_can_stop_shorthand(self):
        gate = StopGate()
        assert gate.can_stop() is True

    def test_can_stop_with_failure(self):
        gate = StopGate()
        assert gate.can_stop(audit_has_new_entries=False) is False


class TestAcknowledgeShutdown:
    def test_acknowledge(self):
        gate = StopGate()
        gate.acknowledge_shutdown()
        assert gate.shutdown_acknowledged is True

    def test_initialize_resets_acknowledgement(self):
        gate = StopGate()
        gate.acknowledge_shutdown()
        assert gate.shutdown_acknowledged is True
        gate.initialize()
        assert gate.shutdown_acknowledged is False


class TestStopGateResult:
    def test_default_values(self):
        result = StopGateResult()
        assert result.can_stop is True
        assert result.reasons == []

    def test_custom_values(self):
        result = StopGateResult(can_stop=False, reasons=["reason1", "reason2"])
        assert result.can_stop is False
        assert len(result.reasons) == 2


class TestSessionBudget:
    """Session 预算参数（蓝图 §16.3 步骤 1）：超限阻断继续工作、放行退出。"""

    def test_default_no_budget_zero_behavior_change(self):
        gate = StopGate()
        assert gate.budget_exceeded() is False
        assert gate.can_continue() is True
        assert gate.check().can_stop is True
        assert gate.budget_status()["exceeded"] is False

    def test_action_budget_not_exceeded(self):
        gate = StopGate(session_max_actions=3)
        gate.record_action()
        gate.record_action()
        assert gate.budget_exceeded() is False
        assert gate.can_continue() is True

    def test_action_budget_exceeded_blocks_continue(self):
        gate = StopGate(session_max_actions=2)
        gate.record_action(2)
        assert gate.budget_exceeded() is True
        assert gate.can_continue() is False

    def test_action_budget_exceeded_forces_stop_despite_quality_failures(self):
        gate = StopGate(session_max_actions=1)
        gate.record_action()
        result = gate.check(audit_has_new_entries=False, git_clean=False)
        assert result.can_stop is True
        assert any("budget" in r.lower() for r in result.reasons)
        # 质量原因仍留痕
        assert any("AiAuditLogger" in r for r in result.reasons)

    def test_minutes_budget_exceeded(self):
        gate = StopGate(session_max_minutes=0.0)  # 0 分钟预算：initialize 后立即超限
        gate.initialize()
        assert gate.budget_exceeded() is True
        assert gate.can_continue() is False

    def test_minutes_budget_not_exceeded_without_initialize(self):
        gate = StopGate(session_max_minutes=10.0)
        assert gate.budget_exceeded() is False

    def test_minutes_budget_invalid_start_tolerated(self):
        gate = StopGate(session_max_minutes=10.0)
        gate.session_start = "not-a-timestamp"
        assert gate.budget_exceeded() is False

    def test_initialize_resets_action_count(self):
        gate = StopGate(session_max_actions=2)
        gate.record_action(2)
        assert gate.budget_exceeded() is True
        gate.initialize()
        assert gate.budget_exceeded() is False
        assert gate.budget_status()["action_count"] == 0
