# [A_test] module_id: SRC-TST-1768 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_trust_anchor
# [INVARIANTS] TripleTrustAnchorGate.verify returns TrustAnchorResult; _calculate_trust is pure
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] subprocess.TimeoutExpired handled gracefully
# [TESTS] tests/test_trust_anchor_root.py
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from zephyr.infrastructure.asset_inventory.trust_anchor import (
    BypassManager,
    BypassState,
    TripleTrustAnchorGate,
    TrustAnchorResult,
    TrustLevel,
)


class TestTrustLevelEnum:
    def test_values(self):
        assert TrustLevel.FULL == "FULL"
        assert TrustLevel.PARTIAL == "PARTIAL"
        assert TrustLevel.BROKEN == "BROKEN"


class TestTrustAnchorResult:
    def test_defaults(self):
        r = TrustAnchorResult()
        assert r.git_ok is False
        assert r.test_ok is False
        assert r.audit_ok is False
        assert r.trust_level == TrustLevel.BROKEN
        assert r.recommendation == ""

    def test_all_green(self):
        r = TrustAnchorResult(git_ok=True, test_ok=True, audit_ok=True, trust_level=TrustLevel.FULL)
        assert r.trust_level == TrustLevel.FULL


class TestTripleTrustAnchorGateInstantiation:
    def test_default(self, tmp_path):
        gate = TripleTrustAnchorGate(project_root=tmp_path)
        assert gate._root == tmp_path
        assert gate._cache is None

    def test_cache_initially_none(self, tmp_path):
        gate = TripleTrustAnchorGate(project_root=tmp_path)
        assert gate._cache is None


class TestCalculateTrust:
    def test_all_true(self):
        assert TripleTrustAnchorGate._calculate_trust({"git_ok": True, "test_ok": True, "audit_ok": True}) == TrustLevel.FULL

    def test_two_true(self):
        assert TripleTrustAnchorGate._calculate_trust({"git_ok": True, "test_ok": True, "audit_ok": False}) == TrustLevel.PARTIAL
        assert TripleTrustAnchorGate._calculate_trust({"git_ok": True, "test_ok": False, "audit_ok": True}) == TrustLevel.PARTIAL
        assert TripleTrustAnchorGate._calculate_trust({"git_ok": False, "test_ok": True, "audit_ok": True}) == TrustLevel.PARTIAL

    def test_one_true(self):
        assert TripleTrustAnchorGate._calculate_trust({"git_ok": True, "test_ok": False, "audit_ok": False}) == TrustLevel.BROKEN

    def test_none_true(self):
        assert TripleTrustAnchorGate._calculate_trust({"git_ok": False, "test_ok": False, "audit_ok": False}) == TrustLevel.BROKEN


class TestRecommend:
    def test_full(self):
        r = TripleTrustAnchorGate._recommend(TrustLevel.FULL)
        assert "完全可信" in r

    def test_partial(self):
        r = TripleTrustAnchorGate._recommend(TrustLevel.PARTIAL)
        assert "部分可信" in r

    def test_broken(self):
        r = TripleTrustAnchorGate._recommend(TrustLevel.BROKEN)
        assert "不可信" in r


class TestVerify:
    def test_verify_returns_result(self, tmp_path):
        gate = TripleTrustAnchorGate(project_root=tmp_path)
        result = gate.verify(force=True)
        assert isinstance(result, TrustAnchorResult)
        assert isinstance(result.trust_level, TrustLevel)

    def test_verify_caches_result(self, tmp_path):
        gate = TripleTrustAnchorGate(project_root=tmp_path)
        r1 = gate.verify(force=True)
        r2 = gate.verify(force=False)
        assert r1.trust_level == r2.trust_level

    def test_verify_force_bypasses_cache(self, tmp_path):
        gate = TripleTrustAnchorGate(project_root=tmp_path)
        r1 = gate.verify(force=True)
        r2 = gate.verify(force=True)
        assert isinstance(r2, TrustAnchorResult)


class TestCheckAuditContinuity:
    def test_no_log_file(self, tmp_path):
        gate = TripleTrustAnchorGate(project_root=tmp_path)
        assert gate._check_audit_continuity() is True

    def test_empty_log(self, tmp_path):
        log_dir = tmp_path / "data" / "reports"
        log_dir.mkdir(parents=True)
        (log_dir / "security_access_log.jsonl").write_text("", encoding="utf-8")
        gate = TripleTrustAnchorGate(project_root=tmp_path)
        assert gate._check_audit_continuity() is True

    def test_recent_entries_pass(self, tmp_path):
        log_dir = tmp_path / "data" / "reports"
        log_dir.mkdir(parents=True)
        now = datetime.now(UTC)
        lines = [
            json.dumps({"ts": (now - timedelta(hours=1)).isoformat()}),
            json.dumps({"ts": now.isoformat()}),
        ]
        (log_dir / "security_access_log.jsonl").write_text("\n".join(lines), encoding="utf-8")
        gate = TripleTrustAnchorGate(project_root=tmp_path)
        assert gate._check_audit_continuity() is True

    def test_large_gap_fails(self, tmp_path):
        log_dir = tmp_path / "data" / "reports"
        log_dir.mkdir(parents=True)
        now = datetime.now(UTC)
        lines = [
            json.dumps({"ts": (now - timedelta(hours=48)).isoformat()}),
            json.dumps({"ts": now.isoformat()}),
        ]
        (log_dir / "security_access_log.jsonl").write_text("\n".join(lines), encoding="utf-8")
        gate = TripleTrustAnchorGate(project_root=tmp_path)
        assert gate._check_audit_continuity() is False


class TestBypassState:
    def test_defaults(self):
        s = BypassState()
        assert s.enabled is False
        assert s.reason == ""
        assert s.is_expired is False

    def test_expired(self):
        s = BypassState(is_expired=True)
        assert s.is_expired is True


class TestBypassManager:
    def test_no_override_file(self, tmp_path):
        mgr = BypassManager(project_root=tmp_path)
        state = mgr.get_bypass_state()
        assert state.enabled is False

    def test_is_bypass_active_no_file(self, tmp_path):
        mgr = BypassManager(project_root=tmp_path)
        assert mgr.is_bypass_active() is False

    def test_write_and_read_override(self, tmp_path):
        mgr = BypassManager(project_root=tmp_path)
        path = mgr.write_override("test reason", "tester", hours=24)
        assert path.exists()
        state = mgr.get_bypass_state()
        assert state.enabled is True
        assert state.reason == "test reason"

    def test_remove_override(self, tmp_path):
        mgr = BypassManager(project_root=tmp_path)
        mgr.write_override("test", "tester")
        assert mgr.remove_override() is True
        assert mgr.is_bypass_active() is False

    def test_remove_nonexistent_override(self, tmp_path):
        mgr = BypassManager(project_root=tmp_path)
        assert mgr.remove_override() is False

    def test_expired_override_not_active(self, tmp_path):
        mgr = BypassManager(project_root=tmp_path)
        override_dir = tmp_path / "config" / "capacity"
        override_dir.mkdir(parents=True)
        past = (datetime.now(UTC) - timedelta(hours=48)).isoformat()
        override_data = {
            "enabled": True,
            "reason": "old",
            "activated_at": past,
            "expires_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
        }
        import yaml

        (override_dir / "inventory_override.yaml").write_text(yaml.dump(override_data), encoding="utf-8")
        assert mgr.is_bypass_active() is False
