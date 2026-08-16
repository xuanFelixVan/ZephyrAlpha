# [A_test] module_id: MOD-GOV_fix_safety | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §5
# [MODULE] tests.test_fix_safety
# [INVARIANTS] SafetyGate MUST check FixLevel+target; CascadeBreaker MUST circuit-break; SecretLeakGuard MUST 100% intercept
# [MODIFY-GUARD] blueprint.md §5; auto_fix_config.yaml safety section
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertion errors on invariant violation
# [TESTS] tests/test_fix_safety.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.auto_fix_engine.fix_safety import (
    CascadeBreaker,
    FixValidator,
    LockGuard,
    SafetyGate,
    SandboxExecutor,
    SecretLeakGuard,
    WriteSafety,
)
from zephyr.infrastructure.auto_fix_engine.models import (
    FixAction,
    FixConfidence,
    FixLevel,
    FixStatus,
    ValidationResult,
)


class TestSafetyGate:
    def test_default_instantiation(self):
        sg = SafetyGate()
        assert sg.enabled is True

    def test_check_l1_approved(self):
        sg = SafetyGate()
        action = FixAction(action_type="test", target="f.py", level=FixLevel.L1_RULE)
        decision = sg.check(action)
        assert decision.approved is True

    def test_check_l3_denied(self):
        sg = SafetyGate()
        action = FixAction(action_type="test", target="f.py", level=FixLevel.L3_AGENT)
        decision = sg.check(action)
        assert decision.approved is False
        assert "L3 agent" in decision.reason

    def test_check_l2_low_confidence_denied(self):
        sg = SafetyGate()
        action = FixAction(
            action_type="test",
            target="f.py",
            level=FixLevel.L2_LLM,
            confidence=FixConfidence.LOW,
        )
        decision = sg.check(action)
        assert decision.approved is False
        assert "LOW confidence" in decision.reason

    def test_check_l2_high_confidence_approved(self):
        sg = SafetyGate()
        action = FixAction(
            action_type="test",
            target="f.py",
            level=FixLevel.L2_LLM,
            confidence=FixConfidence.HIGH,
        )
        decision = sg.check(action)
        assert decision.approved is True

    def test_check_protected_path_denied(self):
        sg = SafetyGate(config={"protected_paths": ["secret_data"]})
        action = FixAction(action_type="test", target="secret_data/keys.py", level=FixLevel.L1_RULE)
        decision = sg.check(action)
        assert decision.approved is False
        assert "protected path" in decision.reason

    def test_check_protected_pattern_denied(self):
        sg = SafetyGate(config={"protected_patterns": ["*.secret"]})
        action = FixAction(action_type="test", target="data.secret", level=FixLevel.L1_RULE)
        decision = sg.check(action)
        assert decision.approved is False
        assert "protected pattern" in decision.reason

    def test_check_disabled_approves_all(self):
        sg = SafetyGate(config={"safety_gate_enabled": False})
        action = FixAction(action_type="test", target="f.py", level=FixLevel.L3_AGENT)
        decision = sg.check(action)
        assert decision.approved is True
        assert "disabled" in decision.reason

    def test_check_none_config(self):
        sg = SafetyGate(config=None)
        action = FixAction(action_type="test", target="f.py")
        decision = sg.check(action)
        assert decision.approved is True


class TestLockGuard:
    def test_instantiation(self):
        lg = LockGuard()
        assert lg.locks_dir.name == ".ailocks"

    def test_check_unlocked_file(self):
        lg = LockGuard()
        locked, owner = lg.check("nonexistent_file_12345.py")
        assert locked is False
        assert owner == ""

    def test_is_locked_unlocked_file(self):
        lg = LockGuard()
        locked, owner = lg.is_locked("nonexistent_file_12345.py")
        assert locked is False


class TestWriteSafety:
    def test_atomic_write_success(self, tmp_path):
        filepath = str(tmp_path / "test_write.txt")
        result = WriteSafety.atomic_write(filepath, "hello world")
        assert result is True
        with open(filepath, encoding="utf-8") as f:
            assert f.read() == "hello world"

    def test_atomic_write_overwrite(self, tmp_path):
        filepath = str(tmp_path / "test_overwrite.txt")
        WriteSafety.atomic_write(filepath, "first")
        WriteSafety.atomic_write(filepath, "second")
        with open(filepath, encoding="utf-8") as f:
            assert f.read() == "second"

    def test_verify_write_correct(self, tmp_path):
        filepath = str(tmp_path / "test_verify.txt")
        WriteSafety.atomic_write(filepath, "content")
        assert WriteSafety.verify_write(filepath, "content") is True

    def test_verify_write_incorrect(self, tmp_path):
        filepath = str(tmp_path / "test_verify2.txt")
        WriteSafety.atomic_write(filepath, "actual")
        assert WriteSafety.verify_write(filepath, "expected") is False

    def test_verify_write_nonexistent(self, tmp_path):
        assert WriteSafety.verify_write(str(tmp_path / "nope.txt"), "x") is False

    def test_atomic_write_invalid_path(self, tmp_path):
        # Canonical atomic_write creates parent dirs, so a missing dir is no
        # longer an error; a path whose parent is a FILE is genuinely unwritable
        blocker = tmp_path / "blocker"
        blocker.write_text("x", encoding="utf-8")
        result = WriteSafety.atomic_write(str(blocker / "sub" / "file.txt"), "data")
        assert result is False


class TestFixValidator:
    def test_instantiation(self):
        fv = FixValidator()
        assert fv.project_root is not None

    def test_validate_fix_nonexistent_file(self):
        fv = FixValidator()
        result = fv.validate_fix("nonexistent_file_xyz.py")
        assert isinstance(result, ValidationResult)
        assert result.valid is False
        assert "not found" in result.error

    def test_validate_fix_existing_python_file(self, tmp_path):
        py_file = tmp_path / "valid.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        fv = FixValidator()
        result = fv.validate_fix(str(py_file))
        assert result.valid is True

    def test_validate_fix_syntax_error_file(self, tmp_path):
        py_file = tmp_path / "bad_syntax.py"
        py_file.write_text("def foo(\n", encoding="utf-8")
        fv = FixValidator()
        result = fv.validate_fix(str(py_file))
        assert result.valid is False

    def test_validate_fix_non_py_file(self, tmp_path):
        txt_file = tmp_path / "data.yaml"
        txt_file.write_text("key: value\n", encoding="utf-8")
        fv = FixValidator()
        result = fv.validate_fix(str(txt_file))
        assert result.valid is True


class TestCascadeBreaker:
    def test_default_instantiation(self):
        cb = CascadeBreaker()
        assert cb.module_threshold == 10
        assert cb.global_threshold == 150

    def test_check_initially_passes(self):
        cb = CascadeBreaker()
        ok, reason = cb.check()
        assert ok is True
        assert reason == ""

    def test_check_with_module_passes(self):
        cb = CascadeBreaker()
        ok, reason = cb.check("some_module")
        assert ok is True

    def test_module_cascade_triggered(self):
        cb = CascadeBreaker(config={"module_threshold": 3, "module_window_sec": 10, "module_cooldown_sec": 60})
        for _ in range(3):
            cb.record("mod_a")
        ok, reason = cb.check("mod_a")
        assert ok is False
        assert "Module cascade breaker triggered" in reason

    def test_global_cascade_triggered(self):
        cb = CascadeBreaker(config={"global_threshold": 3, "global_window_sec": 10, "global_cooldown_sec": 60})
        for _ in range(3):
            cb.record("")
        ok, reason = cb.check()
        assert ok is False
        assert "Global cascade breaker triggered" in reason

    def test_different_modules_independent(self):
        cb = CascadeBreaker(config={"module_threshold": 2, "module_window_sec": 10, "module_cooldown_sec": 60})
        cb.record("mod_a")
        cb.record("mod_a")
        ok_a, _ = cb.check("mod_a")
        assert ok_a is False
        ok_b, _ = cb.check("mod_b")
        assert ok_b is True

    def test_custom_config(self):
        cb = CascadeBreaker(config={"module_threshold": 5, "global_threshold": 50})
        assert cb.module_threshold == 5
        assert cb.global_threshold == 50


class TestSandboxExecutor:
    def test_instantiation(self):
        se = SandboxExecutor()
        assert "auto_fix_sandbox" in se.base_dir

    def test_execute_success(self):
        se = SandboxExecutor()
        action = FixAction(action_type="test", target="f.py")

        def mock_fix(target, dry_run=False):
            return FixAction(action_type="test", target=target, status=FixStatus.COMPLETED)

        ok, msg = se.execute(action, mock_fix)
        assert ok is True

    def test_execute_failure(self):
        se = SandboxExecutor()
        action = FixAction(action_type="test", target="f.py")

        def failing_fix(target, dry_run=False):
            raise RuntimeError("fix failed")

        ok, msg = se.execute(action, failing_fix)
        assert ok is False
        assert "fix failed" in msg


class TestSecretLeakGuard:
    def test_instantiation(self):
        slg = SecretLeakGuard()
        assert len(slg.patterns) > 0

    def test_scan_clean_text(self):
        slg = SecretLeakGuard()
        ok, findings = slg.scan("this is clean text with no secrets")
        assert ok is True
        assert findings == []

    def test_scan_api_key(self):
        slg = SecretLeakGuard()
        ok, findings = slg.scan("api_key = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234'")
        assert ok is False
        assert len(findings) > 0

    def test_scan_openai_key(self):
        slg = SecretLeakGuard()
        ok, findings = slg.scan("sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")
        assert ok is False
        assert len(findings) > 0

    def test_scan_github_pat(self):
        slg = SecretLeakGuard()
        ok, findings = slg.scan("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        assert ok is False
        assert len(findings) > 0

    def test_scan_private_key(self):
        slg = SecretLeakGuard()
        ok, findings = slg.scan("-----BEGIN RSA PRIVATE KEY-----\nMIIEowI...")
        assert ok is False
        assert len(findings) > 0

    def test_scan_empty_string(self):
        slg = SecretLeakGuard()
        ok, findings = slg.scan("")
        assert ok is True
        assert findings == []

    def test_scan_and_redact(self):
        slg = SecretLeakGuard()
        text = "api_key = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234'"
        redacted, findings = slg.scan_and_redact(text)
        assert len(findings) > 0
        assert "[REDACTED]" in redacted
        assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234" not in redacted

    def test_scan_and_redact_clean(self):
        slg = SecretLeakGuard()
        text = "normal text without secrets"
        redacted, findings = slg.scan_and_redact(text)
        assert findings == []
        assert redacted == text
