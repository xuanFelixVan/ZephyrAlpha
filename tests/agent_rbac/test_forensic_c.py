"""跨切面 B 取证审计 C 层——audit_log/replay/legal_chain/rollback_sandbox/monotonic_clock 测试."""
from __future__ import annotations

import pytest
import time
from zephyr.agent_rbac.audit_log_guard import AuditLogGuard
from zephyr.agent_rbac.replay_attack_guard import ReplayAttackGuard
from zephyr.agent_rbac.legal_audit_chain import LegalAuditChain
from zephyr.agent_rbac.rollback_sandbox import RollbackSandbox
from zephyr.agent_rbac.monotonic_clock import MonotonicClock


class TestForensicC:
    def test_audit_log_sanitize_newline(self):
        guard = AuditLogGuard()
        sanitized = guard.sanitize("hello\ninjected")
        assert "\n" not in sanitized

    def test_audit_log_validate_dict(self):
        guard = AuditLogGuard()
        result = guard.validate_dict({"user": "clean", "evil": "value\ninjection"})
        assert result["clean"] is False

    def test_replay_attack_nonce_unique(self):
        guard = ReplayAttackGuard()
        r1 = guard.check("nonce_001", time.time())
        assert r1["allowed"] is True

        r2 = guard.check("nonce_001", time.time())
        assert r2["allowed"] is False

    def test_legal_audit_chain_integrity(self):
        chain = LegalAuditChain()
        chain.append("bootstrap", "bytebuddy")
        chain.append("create_agent", "bytebuddy")
        chain.append("assign_role", "admin")

        result = chain.verify()
        assert result["intact"] is True
        assert result["length"] == 3

    def test_rollback_sandbox_reversible(self):
        sandbox = RollbackSandbox()
        sandbox.isolate("op_001", '{"state": "before"}')
        sandbox.execute("op_001", '{"state": "after"}')

        result = sandbox.rollback("op_001")
        assert result["success"] is True

    def test_rollback_sandbox_irreversible(self):
        sandbox = RollbackSandbox()
        op = sandbox.isolate("op_002", "before")
        op.reversible = False
        sandbox.execute("op_002", "after")

        result = sandbox.rollback("op_002")
        assert result["success"] is False

    def test_monotonic_clock_no_drift(self):
        clock = MonotonicClock()
        result = clock.verify(time.time())
        assert result["valid"] is True
