# [A_test] module_id: MOD-GOV_engine_sandbox | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_engine_sandbox
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] 沙箱隔离边界不可突破;网络隔离必须强制
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_engine_sandbox.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""EngineSandbox — filesystem/network/boundary isolation and integrity tests."""

from __future__ import annotations

import time
from pathlib import Path

from zephyr.governance.resilience_governance.engine_sandbox import (
    AccessDecision,
    EngineSandbox,
    IntegritySnapshot,
    IsolationProfile,
    SandboxAccessEvent,
    SandboxState,
    _ResourceGuard,
)


class TestSandboxState:
    def test_enum_values(self) -> None:
        assert SandboxState.INIT == "init"
        assert SandboxState.RUNNING == "running"
        assert SandboxState.DEGRADED == "degraded"
        assert SandboxState.LOCKED == "locked"

    def test_is_str_enum(self) -> None:
        assert isinstance(SandboxState.RUNNING, str)


class TestAccessDecision:
    def test_enum_values(self) -> None:
        assert AccessDecision.ALLOW == "allow"
        assert AccessDecision.DENY == "deny"
        assert AccessDecision.AUDIT_ONLY == "audit_only"

    def test_is_str_enum(self) -> None:
        assert isinstance(AccessDecision.DENY, str)


class TestIsolationProfile:
    def test_default_profile(self) -> None:
        p = IsolationProfile()
        assert "docs/" in p.read_paths
        assert "docs/_working/audit/" in p.write_paths
        assert ".env" in p.deny_paths
        assert "localhost" in p.network_allowed
        assert "api.openai.com" in p.network_denied
        assert p.max_memory_mb == 256
        assert p.max_cpu_seconds == 5.0

    def test_custom_profile(self) -> None:
        p = IsolationProfile(
            read_paths=["custom/"],
            write_paths=["out/"],
            deny_paths=["secret/"],
            network_allowed=["10.0.0.1"],
            network_denied=["evil.com"],
            max_memory_mb=512,
            max_cpu_seconds=10.0,
        )
        assert p.read_paths == ["custom/"]
        assert p.write_paths == ["out/"]
        assert p.deny_paths == ["secret/"]
        assert p.network_allowed == ["10.0.0.1"]
        assert p.network_denied == ["evil.com"]
        assert p.max_memory_mb == 512
        assert p.max_cpu_seconds == 10.0


class TestSandboxAccessEvent:
    def test_default_event(self) -> None:
        e = SandboxAccessEvent()
        assert e.actor == ""
        assert e.path == ""
        assert e.decision == AccessDecision.DENY
        assert e.reason == ""
        assert e.hash_checksum == ""
        assert e.timestamp > 0

    def test_custom_event(self) -> None:
        e = SandboxAccessEvent(
            actor="agent-1",
            path="docs/readme.md",
            decision=AccessDecision.ALLOW,
            reason="Read path allowed",
        )
        assert e.actor == "agent-1"
        assert e.path == "docs/readme.md"
        assert e.decision == AccessDecision.ALLOW


class TestIntegritySnapshot:
    def test_fields(self) -> None:
        s = IntegritySnapshot(path="/tmp/f.txt", checksum="abc123")
        assert s.path == "/tmp/f.txt"
        assert s.checksum == "abc123"
        assert s.timestamp > 0


class TestEngineSandboxInit:
    def test_default_init(self) -> None:
        sb = EngineSandbox()
        assert sb.state == SandboxState.RUNNING
        assert sb.uptime_seconds >= 0

    def test_custom_root(self, tmp_path: Path) -> None:
        sb = EngineSandbox(project_root=tmp_path)
        assert sb.state == SandboxState.RUNNING

    def test_custom_profile(self) -> None:
        p = IsolationProfile(max_memory_mb=1024)
        sb = EngineSandbox(profile=p)
        assert sb.state == SandboxState.RUNNING

    def test_none_root_uses_cwd(self) -> None:
        sb = EngineSandbox(project_root=None)
        assert sb.state == SandboxState.RUNNING


class TestCheckFileRead:
    def test_allowed_read(self) -> None:
        sb = EngineSandbox()
        event = sb.check_file_read("docs/readme.md")
        assert event.decision == AccessDecision.ALLOW

    def test_denied_path(self) -> None:
        sb = EngineSandbox()
        event = sb.check_file_read(".env")
        assert event.decision == AccessDecision.DENY
        assert "deny list" in event.reason

    def test_unknown_path_denied(self) -> None:
        sb = EngineSandbox()
        event = sb.check_file_read("random_dir/file.txt")
        assert event.decision == AccessDecision.DENY
        assert "not in read allowlist" in event.reason

    def test_deny_takes_precedence_over_allow(self) -> None:
        sb = EngineSandbox()
        event = sb.check_file_read("src/zephyr/escalation-engine/engine_sandbox.py")
        assert event.decision == AccessDecision.DENY

    def test_actor_recorded(self) -> None:
        sb = EngineSandbox()
        event = sb.check_file_read("docs/x.md", actor="bot-7")
        assert event.actor == "bot-7"

    def test_path_object_input(self) -> None:
        sb = EngineSandbox()
        event = sb.check_file_read(Path("docs/x.md"))
        assert event.decision == AccessDecision.ALLOW


class TestCheckFileWrite:
    def test_allowed_write(self) -> None:
        sb = EngineSandbox()
        event = sb.check_file_write("docs/_working/audit/log.txt")
        assert event.decision == AccessDecision.ALLOW

    def test_denied_write(self) -> None:
        sb = EngineSandbox()
        event = sb.check_file_write(".env")
        assert event.decision == AccessDecision.DENY

    def test_unknown_write_denied(self) -> None:
        sb = EngineSandbox()
        event = sb.check_file_write("tmp/output.txt")
        assert event.decision == AccessDecision.DENY
        assert "not in write allowlist" in event.reason

    def test_deny_overrides_write_allow(self) -> None:
        p = IsolationProfile(
            write_paths=["src/"],
            deny_paths=["src/"],
        )
        sb = EngineSandbox(profile=p)
        event = sb.check_file_write("src/main.py")
        assert event.decision == AccessDecision.DENY


class TestCheckNetworkAccess:
    def test_allowed_internal(self) -> None:
        sb = EngineSandbox()
        event = sb.check_network_access("localhost")
        assert event.decision == AccessDecision.ALLOW

    def test_denied_external(self) -> None:
        sb = EngineSandbox()
        event = sb.check_network_access("api.openai.com")
        assert event.decision == AccessDecision.DENY

    def test_unknown_host_audit_only(self) -> None:
        sb = EngineSandbox()
        event = sb.check_network_access("internal-service.local")
        assert event.decision == AccessDecision.AUDIT_ONLY

    def test_case_insensitive(self) -> None:
        sb = EngineSandbox()
        event = sb.check_network_access("API.OPENAI.COM")
        assert event.decision == AccessDecision.DENY

    def test_partial_host_match(self) -> None:
        sb = EngineSandbox()
        event = sb.check_network_access("sub.api.openai.com")
        assert event.decision == AccessDecision.DENY

    def test_empty_host(self) -> None:
        sb = EngineSandbox()
        event = sb.check_network_access("")
        assert event.decision == AccessDecision.AUDIT_ONLY


class TestDetectBoundaryViolation:
    def test_violation_recorded(self) -> None:
        sb = EngineSandbox()
        event = sb.detect_boundary_violation("external_agent", 8080)
        assert event.decision == AccessDecision.DENY
        assert "8080" in event.path

    def test_violation_count_increments(self) -> None:
        sb = EngineSandbox()
        sb.detect_boundary_violation("attacker", 22)
        sb.detect_boundary_violation("attacker", 22)
        summary = sb.get_violation_summary()
        assert summary["violations_by_actor"]["attacker"] == 2

    def test_multiple_actors_tracked(self) -> None:
        sb = EngineSandbox()
        sb.detect_boundary_violation("a1", 80)
        sb.detect_boundary_violation("a2", 443)
        summary = sb.get_violation_summary()
        assert "a1" in summary["violations_by_actor"]
        assert "a2" in summary["violations_by_actor"]


class TestIntegrityManagement:
    def test_register_and_verify(self, tmp_path: Path) -> None:
        f = tmp_path / "data.txt"
        f.write_text("hello world", encoding="utf-8")
        sb = EngineSandbox()
        snap = sb.register_integrity_snapshot(str(f))
        assert snap.checksum != "MISSING"
        ok, msg = sb.verify_integrity(str(f))
        assert ok is True
        assert "verified" in msg

    def test_tampered_file_detected(self, tmp_path: Path) -> None:
        f = tmp_path / "data.txt"
        f.write_text("original", encoding="utf-8")
        sb = EngineSandbox()
        sb.register_integrity_snapshot(str(f))
        f.write_text("tampered", encoding="utf-8")
        ok, msg = sb.verify_integrity(str(f))
        assert ok is False
        assert "mismatch" in msg

    def test_missing_file_baseline(self, tmp_path: Path) -> None:
        f = tmp_path / "nonexistent.txt"
        sb = EngineSandbox()
        snap = sb.register_integrity_snapshot(str(f))
        assert snap.checksum == "MISSING"

    def test_verify_no_baseline(self, tmp_path: Path) -> None:
        f = tmp_path / "data.txt"
        f.write_text("content", encoding="utf-8")
        sb = EngineSandbox()
        ok, msg = sb.verify_integrity(str(f))
        assert ok is False
        assert "No baseline" in msg

    def test_verify_file_deleted_after_baseline(self, tmp_path: Path) -> None:
        f = tmp_path / "temp.txt"
        f.write_text("temp", encoding="utf-8")
        sb = EngineSandbox()
        sb.register_integrity_snapshot(str(f))
        f.unlink()
        ok, msg = sb.verify_integrity(str(f))
        assert ok is False
        assert "missing" in msg


class TestLockSandbox:
    def test_lock_changes_state(self) -> None:
        sb = EngineSandbox()
        assert sb.state == SandboxState.RUNNING
        sb.lock_sandbox("security breach")
        assert sb.state == SandboxState.LOCKED

    def test_lock_records_event(self) -> None:
        sb = EngineSandbox()
        sb.lock_sandbox("test reason")
        summary = sb.get_violation_summary()
        assert summary["total_access_events"] >= 1


class TestGrantTemporaryAccess:
    def test_grant_read(self) -> None:
        sb = EngineSandbox()
        result = sb.grant_temporary_access("custom_dir/", duration_s=0, mode="read")
        assert result is True
        event = sb.check_file_read("custom_dir/file.txt")
        assert event.decision == AccessDecision.ALLOW

    def test_grant_write(self) -> None:
        sb = EngineSandbox()
        result = sb.grant_temporary_access("output/", duration_s=0, mode="write")
        assert result is True
        event = sb.check_file_write("output/result.txt")
        assert event.decision == AccessDecision.ALLOW

    def test_grant_blocked_when_locked(self) -> None:
        sb = EngineSandbox()
        sb.lock_sandbox("emergency")
        result = sb.grant_temporary_access("any/", duration_s=0, mode="read")
        assert result is False

    def test_grant_no_duplicate(self) -> None:
        sb = EngineSandbox()
        sb.grant_temporary_access("docs/", duration_s=0, mode="read")
        count_before = len(sb.profile.read_paths)
        sb.grant_temporary_access("docs/", duration_s=0, mode="read")
        assert len(sb.profile.read_paths) == count_before

    def test_temporary_access_expires(self) -> None:
        sb = EngineSandbox()
        sb.grant_temporary_access("ephemeral/", duration_s=0.1, mode="read")
        event = sb.check_file_read("ephemeral/file.txt")
        assert event.decision == AccessDecision.ALLOW
        time.sleep(0.25)
        event2 = sb.check_file_read("ephemeral/file.txt")
        assert event2.decision == AccessDecision.DENY


class TestGetViolationSummary:
    def test_empty_summary(self) -> None:
        sb = EngineSandbox()
        s = sb.get_violation_summary()
        assert s["state"] == "running"
        assert s["total_access_events"] == 0
        assert s["violations_by_actor"] == {}
        assert s["integrity_snapshots"] == 0

    def test_summary_after_events(self) -> None:
        sb = EngineSandbox()
        sb.check_file_read("docs/x.md")
        sb.detect_boundary_violation("intruder", 9999)
        s = sb.get_violation_summary()
        assert s["total_access_events"] == 2
        assert "intruder" in s["violations_by_actor"]


class TestResourceGuard:
    def test_init_defaults(self) -> None:
        rg = _ResourceGuard()
        assert rg.max_memory_mb == 256
        assert rg.max_cpu_seconds == 5.0
        assert rg.violations == 0

    def test_start_and_check_within_limit(self) -> None:
        rg = _ResourceGuard(max_cpu_seconds=10.0)
        rg.start_operation()
        assert rg.check_limits() is True
        assert rg.violations == 0

    def test_check_without_start(self) -> None:
        rg = _ResourceGuard(max_cpu_seconds=10.0)
        assert rg.check_limits() is True

    def test_cpu_exceeded(self) -> None:
        rg = _ResourceGuard(max_cpu_seconds=0.0)
        rg.start_operation()
        time.sleep(0.05)
        assert rg.check_limits() is False
        assert rg.violations == 1

    def test_reset(self) -> None:
        rg = _ResourceGuard(max_cpu_seconds=0.0)
        rg.start_operation()
        time.sleep(0.05)
        rg.check_limits()
        rg.reset()
        rg.start_operation()
        assert rg.check_limits() is True

    def test_summary(self) -> None:
        rg = _ResourceGuard(max_memory_mb=512, max_cpu_seconds=10.0)
        s = rg.summary()
        assert s["max_memory_mb"] == 512
        assert s["max_cpu_seconds"] == 10.0
        assert s["violations"] == 0


class TestAccessLogRecording:
    def test_events_recorded_in_order(self) -> None:
        sb = EngineSandbox()
        sb.check_file_read("docs/a.md", actor="a1")
        sb.check_file_write("docs/_working/audit/b.txt", actor="a2")
        sb.check_network_access("localhost", actor="a3")
        assert len(sb.access_log) == 3
        assert sb.access_log[0].actor == "a1"
        assert sb.access_log[1].actor == "a2"
        assert sb.access_log[2].actor == "a3"

    def test_summary_method_alias(self) -> None:
        sb = EngineSandbox()
        assert sb.summary() == sb.get_violation_summary()


class TestMatchPathStatic:
    def test_exact_match(self) -> None:
        assert EngineSandbox.match_path(Path("docs/readme.md"), ["docs/"]) is True

    def test_no_match(self) -> None:
        assert EngineSandbox.match_path(Path("tmp/file.txt"), ["docs/"]) is False

    def test_empty_patterns(self) -> None:
        assert EngineSandbox.match_path(Path("any/path"), []) is False


class TestUptime:
    def test_uptime_increases(self) -> None:
        sb = EngineSandbox()
        t1 = sb.uptime_seconds
        time.sleep(0.05)
        t2 = sb.uptime_seconds
        assert t2 >= t1
