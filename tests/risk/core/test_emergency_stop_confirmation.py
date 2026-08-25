# [BLUEPRINT] MOD-RK-36 | docs/03_modules/_domain_risk/emergency_stop_confirmation/blueprint.md | §test
# [MODULE] tests.risk.core.test_emergency_stop_confirmation
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.emergency_stop_confirmation
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_emergency_stop_confirmation.py
# [A_test] module_id: MOD-RK-36 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-36 单元测试: EmergencyStopConfirmation — 紧急停止双锁二次确认。

覆盖: 动作白名单、操作人身份核验（空名册/未授权 Fail-Closed）、双锁确认放行、
任一拒绝即终态、同人重复确认拒绝（MOD-INF-049 透传）、确认留痕导出与哈希链
离线校验、非法输入拒绝。
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.venra_double_lock_anchor import VenraDoubleLockError
from zephyr.risk.core.emergency_stop_confirmation import (
    ConfirmationVerdict,
    EmergencyActionType,
    EmergencyStopConfirmation,
    EmergencyStopConfirmationError,
)

_OPERATORS = frozenset({"op-alice", "op-bob", "op-carol"})


def _new_gate() -> EmergencyStopConfirmation:
    return EmergencyStopConfirmation(authorized_operators=_OPERATORS)


class TestWhitelistAndIdentity:
    def test_empty_roster_fail_closed(self):
        with pytest.raises(EmergencyStopConfirmationError):
            EmergencyStopConfirmation(authorized_operators=frozenset())

    def test_propose_rejects_unauthorized_operator(self):
        gate = _new_gate()
        with pytest.raises(EmergencyStopConfirmationError):
            gate.propose(
                EmergencyActionType.EMERGENCY_STOP,
                operator="op-mallory",
                reason="测试",
            )

    def test_propose_rejects_empty_reason(self):
        gate = _new_gate()
        with pytest.raises(EmergencyStopConfirmationError):
            gate.propose(EmergencyActionType.EMERGENCY_STOP, operator="op-alice", reason="")

    def test_confirm_rejects_unauthorized_actor(self):
        gate = _new_gate()
        req = gate.propose(EmergencyActionType.EMERGENCY_STOP, operator="op-alice", reason="回撤超限")
        with pytest.raises(EmergencyStopConfirmationError):
            gate.confirm(req.request_id, actor="op-mallory", approve=True)


class TestDoubleLockFlow:
    def test_two_distinct_lockers_confirm_release(self):
        gate = _new_gate()
        req = gate.propose(
            EmergencyActionType.FORCED_LIQUIDATION,
            operator="op-alice",
            reason="黑档清仓",
            payload={"scope": "all"},
        )
        v1 = gate.confirm(req.request_id, actor="op-bob", approve=True)
        assert v1.decision == "pending"
        assert not v1.released
        v2 = gate.confirm(req.request_id, actor="op-carol", approve=True)
        assert v2.decision == "confirmed"
        assert v2.released
        assert gate.is_released(req.request_id)

    def test_single_reject_finalizes_rejected(self):
        gate = _new_gate()
        req = gate.propose(EmergencyActionType.EMERGENCY_STOP, operator="op-alice", reason="演练")
        v1 = gate.confirm(req.request_id, actor="op-bob", approve=True)
        assert v1.decision == "pending"
        v2 = gate.confirm(req.request_id, actor="op-carol", approve=False)
        assert v2.decision == "rejected"
        assert not v2.released
        assert not gate.is_released(req.request_id)

    def test_same_actor_twice_rejected(self):
        gate = _new_gate()
        req = gate.propose(EmergencyActionType.EMERGENCY_STOP, operator="op-alice", reason="演练")
        gate.confirm(req.request_id, actor="op-bob", approve=True)
        with pytest.raises(VenraDoubleLockError):
            gate.confirm(req.request_id, actor="op-bob", approve=True)

    def test_unknown_request_rejected(self):
        gate = _new_gate()
        with pytest.raises(VenraDoubleLockError):
            gate.confirm("REQ-NOPE", actor="op-bob", approve=True)

    def test_terminal_state_blocks_further_ops(self):
        gate = _new_gate()
        req = gate.propose(EmergencyActionType.EMERGENCY_STOP, operator="op-alice", reason="演练")
        gate.confirm(req.request_id, actor="op-bob", approve=True)
        gate.confirm(req.request_id, actor="op-carol", approve=True)
        with pytest.raises(VenraDoubleLockError):
            gate.confirm(req.request_id, actor="op-alice", approve=True)


class TestAuditTrail:
    def test_audit_trail_export_and_verify(self):
        gate = _new_gate()
        r1 = gate.propose(EmergencyActionType.EMERGENCY_STOP, operator="op-alice", reason="回撤超限")
        gate.confirm(r1.request_id, actor="op-bob", approve=True)
        gate.confirm(r1.request_id, actor="op-carol", approve=True)
        r2 = gate.propose(EmergencyActionType.FORCED_LIQUIDATION, operator="op-bob", reason="流动性危机")
        gate.confirm(r2.request_id, actor="op-alice", approve=False)

        trail = gate.audit_trail()
        assert len(trail) == 2
        assert trail[0]["decision"] == "confirmed"
        assert trail[0]["action_type"] == EmergencyActionType.EMERGENCY_STOP.value
        assert trail[0]["reason"] == "回撤超限"
        assert trail[1]["decision"] == "rejected"
        assert gate.verify_audit_trail() is True

    def test_audit_trail_records_reason_and_payload_hash(self):
        gate = _new_gate()
        req = gate.propose(
            EmergencyActionType.EMERGENCY_STOP,
            operator="op-alice",
            reason="演练留痕",
            payload={"note": "drill"},
        )
        gate.confirm(req.request_id, actor="op-bob", approve=True)
        gate.confirm(req.request_id, actor="op-carol", approve=True)
        rec = gate.audit_trail()[0]
        assert rec["reason"] == "演练留痕"
        assert len(rec["payload_hash"]) == 64  # sha256 hex
        assert rec["operator"] == "op-alice"
        assert rec["lockers"] == ("op-bob", "op-carol")
