# [A_test] module_id: MOD-GOV_auto_fix_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-456 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.auto_fix_engine.test_auto_fix_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: auto-fix-engine core — AutoFixEngine init + fix_safety validation + basic fix workflow"""

import tempfile

import pytest

from zephyr.infrastructure.auto_fix_engine.engine import NO_AUTO_FIX_TYPES, AutoFixEngine
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
    FixHealthReport,
    FixLevel,
    FixReport,
    FixStatus,
    SafetyDecision,
    ValidationResult,
)


@pytest.fixture
def engine(tmp_path):
    config_path = str(tmp_path / "auto_fix_config.yaml")
    budget_db = (tmp_path / "budget.db").as_posix()
    with open(config_path, "w", encoding="utf-8") as f:
        # budget.db_path -> tmp: keep test consumption off the shared DB_PATH SSoT
        f.write(
            "safety:\n  safety_gate_enabled: true\nbudget:\n  daily_limit: 50\n  monthly_limit: 500\n  db_path: "
            + budget_db
            + "\n"
        )
    return AutoFixEngine(config_path=config_path)


@pytest.fixture
def safety_gate():
    return SafetyGate()


@pytest.fixture
def cascade_breaker():
    return CascadeBreaker()


@pytest.fixture
def secret_guard():
    return SecretLeakGuard()


class TestAutoFixEngineInit:
    def test_engine_creates_with_config(self, engine):
        assert engine.safety_gate is not None
        assert engine.cascade_breaker is not None
        assert engine.fix_budget is not None
        assert engine.storm_guard is not None
        assert engine.idempotency is not None
        assert engine.conflict_resolver is not None
        assert engine.blast_radius is not None
        assert engine.dead_letter_queue is not None
        assert engine.approval_queue is not None
        assert engine.canary_fixer is not None
        assert engine.secret_guard is not None
        assert engine.validator is not None
        assert engine.write_safety is not None
        assert engine.shadow is not None
        assert engine.compliance is not None
        assert engine.escalation is not None
        assert engine.pattern_miner is not None
        assert engine.report_generator is not None
        assert engine.batch_fixer is not None

    def test_engine_creates_without_config(self):
        engine = AutoFixEngine(config_path="/nonexistent/config.yaml")
        assert engine.safety_gate is not None

    def test_no_auto_fix_types(self):
        assert "behavioral_audit_red" in NO_AUTO_FIX_TYPES
        assert "security_critical" in NO_AUTO_FIX_TYPES
        assert "data_loss_risk" in NO_AUTO_FIX_TYPES

    def test_fixers_dict_initialized(self, engine):
        assert isinstance(engine.fixers, dict)


class TestAutoFixEngineNoAutoFixTypes:
    def test_behavioral_audit_red_cancelled(self, engine):
        action = engine.fix("behavioral_audit_red", "some_target")
        assert action.status == FixStatus.CANCELLED
        assert "no-auto-fix" in action.metadata.get("reason", "").lower() or "no-auto-fix list" in action.metadata.get(
            "reason", ""
        )

    def test_security_critical_cancelled(self, engine):
        action = engine.fix("security_critical", "some_target")
        assert action.status == FixStatus.CANCELLED

    def test_data_loss_risk_cancelled(self, engine):
        action = engine.fix("data_loss_risk", "some_target")
        assert action.status == FixStatus.CANCELLED


class TestAutoFixEngineFixWorkflow:
    def test_fix_no_fixer_found(self, engine):
        action = engine.fix("nonexistent_action_type", "some_target")
        assert action.status == FixStatus.FAILED
        assert "No fixer found" in action.metadata.get("error", "")

    def test_dry_run(self, engine):
        action = engine.dry_run("nonexistent_action_type", "some_target")
        assert action.status == FixStatus.FAILED

    def test_fix_all_empty_list(self, engine):
        report = engine.fix_all([])
        assert isinstance(report, FixReport)
        assert report.total_attempted == 0

    def test_fix_all_with_no_auto_fix_types(self, engine):
        actions = [
            FixAction(action_type="behavioral_audit_red", target="t1"),
            FixAction(action_type="security_critical", target="t2"),
        ]
        report = engine.fix_all(actions)
        assert report.total_attempted == 2
        assert len(report.cascade_alerts) > 0

    def test_health_check(self, engine):
        report = engine.health_check()
        assert isinstance(report, FixHealthReport)
        assert isinstance(report.healthy, bool)
        assert isinstance(report.budget_ok, bool)
        assert isinstance(report.dead_letter_count, int)
        assert isinstance(report.approval_queue_size, int)

    def test_get_dead_letters(self, engine):
        dead = engine.get_dead_letters()
        assert isinstance(dead, list)

    def test_get_approval_queue(self, engine):
        queue = engine.get_approval_queue()
        assert isinstance(queue, list)


class TestSafetyGate:
    def test_allows_l1_action(self, safety_gate):
        action = FixAction(action_type="zombie_cleanup", target="src/mod.py", level=FixLevel.L1_RULE)
        decision = safety_gate.check(action)
        assert decision.approved is True

    def test_blocks_l3_action(self, safety_gate):
        action = FixAction(action_type="self_heal", target="src/mod.py", level=FixLevel.L3_AGENT)
        decision = safety_gate.check(action)
        assert decision.approved is False
        assert "human approval" in decision.reason.lower() or "L3" in decision.reason

    def test_blocks_protected_path(self):
        gate = SafetyGate(config={"protected_paths": [".env"]})
        action = FixAction(action_type="zombie_cleanup", target=".env")
        decision = gate.check(action)
        assert decision.approved is False
        assert "protected path" in decision.reason.lower()

    def test_blocks_protected_pattern(self):
        gate = SafetyGate(config={"protected_patterns": ["*.secret"]})
        action = FixAction(action_type="zombie_cleanup", target="keys.secret")
        decision = gate.check(action)
        assert decision.approved is False
        assert "protected pattern" in decision.reason.lower()

    def test_blocks_l2_low_confidence(self, safety_gate):
        action = FixAction(
            action_type="llm_fix",
            target="src/mod.py",
            level=FixLevel.L2_LLM,
            confidence=FixConfidence.LOW,
        )
        decision = safety_gate.check(action)
        assert decision.approved is False
        assert "LOW confidence" in decision.reason

    def test_allows_l2_high_confidence(self, safety_gate):
        action = FixAction(
            action_type="llm_fix",
            target="src/mod.py",
            level=FixLevel.L2_LLM,
            confidence=FixConfidence.HIGH,
        )
        decision = safety_gate.check(action)
        assert decision.approved is True

    def test_disabled_gate_allows_all(self):
        gate = SafetyGate(config={"safety_gate_enabled": False})
        action = FixAction(action_type="self_heal", target="src/mod.py", level=FixLevel.L3_AGENT)
        decision = gate.check(action)
        assert decision.approved is True
        assert "disabled" in decision.reason.lower()


class TestCascadeBreaker:
    def test_initial_check_passes(self, cascade_breaker):
        ok, reason = cascade_breaker.check()
        assert ok is True
        assert reason == ""

    def test_record_and_check_module(self, cascade_breaker):
        for _ in range(10):
            cascade_breaker.record("MOD-TEST")
        ok, reason = cascade_breaker.check("MOD-TEST")
        assert ok is False
        assert "cascade breaker" in reason.lower() or "MOD-TEST" in reason

    def test_check_empty_module_passes(self, cascade_breaker):
        ok, reason = cascade_breaker.check("")
        assert ok is True

    def test_different_modules_independent(self, cascade_breaker):
        for _ in range(10):
            cascade_breaker.record("MOD-A")
        ok, reason = cascade_breaker.check("MOD-B")
        assert ok is True

    def test_global_threshold(self):
        cb = CascadeBreaker(config={"global_threshold": 5, "global_window_sec": 300})
        for _ in range(5):
            cb.record("MOD-X")
        ok, reason = cb.check("MOD-Y")
        assert ok is False
        assert "global cascade" in reason.lower()


class TestSecretLeakGuard:
    def test_clean_text(self, secret_guard):
        clean, findings = secret_guard.scan("Hello world, no secrets here")
        assert clean is True
        assert findings == []

    def test_detects_api_key(self, secret_guard):
        clean, findings = secret_guard.scan("api_key = 'ABCDEFGHabcdefgh1234567890ABCD'")
        assert clean is False
        assert len(findings) > 0

    def test_detects_sk_token(self, secret_guard):
        clean, findings = secret_guard.scan("token = sk-" + "A" * 32)
        assert clean is False
        assert len(findings) > 0

    def test_detects_private_key(self, secret_guard):
        clean, findings = secret_guard.scan("-----BEGIN RSA PRIVATE KEY-----")
        assert clean is False
        assert len(findings) > 0

    def test_scan_and_redact(self, secret_guard):
        text = "api_key = 'my_secret_key_1234567890abcd'"
        redacted, findings = secret_guard.scan_and_redact(text)
        assert len(findings) > 0
        assert "[REDACTED]" in redacted


class TestWriteSafety:
    def test_atomic_write_success(self, tmp_path):
        filepath = str(tmp_path / "test_write.txt")
        result = WriteSafety.atomic_write(filepath, "hello world")
        assert result is True
        with open(filepath, encoding="utf-8") as f:
            assert f.read() == "hello world"

    def test_atomic_write_verify(self, tmp_path):
        filepath = str(tmp_path / "test_verify.txt")
        WriteSafety.atomic_write(filepath, "verify me")
        assert WriteSafety.verify_write(filepath, "verify me") is True
        assert WriteSafety.verify_write(filepath, "wrong content") is False

    def test_verify_nonexistent_file(self):
        assert WriteSafety.verify_write("/nonexistent/file.txt", "content") is False


class TestFixValidator:
    def test_validate_nonexistent_target(self):
        validator = FixValidator()
        result = validator.validate_fix("/nonexistent/file.py")
        assert isinstance(result, ValidationResult)
        assert result.valid is False

    def test_validate_valid_python(self, tmp_path):
        py_file = tmp_path / "valid.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        validator = FixValidator()
        result = validator.validate_fix(str(py_file))
        assert result.valid is True

    def test_validate_invalid_python_syntax(self, tmp_path):
        py_file = tmp_path / "invalid.py"
        py_file.write_text("def broken(\n", encoding="utf-8")
        validator = FixValidator()
        result = validator.validate_fix(str(py_file))
        assert result.valid is False

    def test_validate_non_py_file_passes(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("key: value\n", encoding="utf-8")
        validator = FixValidator()
        result = validator.validate_fix(str(yaml_file))
        assert result.valid is True


class TestLockGuard:
    def test_not_locked_by_default(self):
        guard = LockGuard()
        locked, owner = guard.check("some/file.py")
        assert locked is False
        assert owner == ""

    def test_is_locked_returns_tuple(self):
        guard = LockGuard()
        result = guard.is_locked("any/path.py")
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestSandboxExecutor:
    def test_execute_success(self):
        executor = SandboxExecutor(base_dir=tempfile.gettempdir())
        action = FixAction(action_type="test", target="dummy")
        ok, msg = executor.execute(action, lambda target, dry_run=False: "ok")
        assert ok is True

    def test_execute_failure(self):
        executor = SandboxExecutor(base_dir=tempfile.gettempdir())
        action = FixAction(action_type="test", target="dummy")

        def failing_fix(target, dry_run=False):
            raise RuntimeError("fix failed")

        ok, msg = executor.execute(action, failing_fix)
        assert ok is False


class TestFixActionModel:
    def test_creation_defaults(self):
        action = FixAction(action_type="zombie_cleanup", target="src/mod.py")
        assert action.action_type == "zombie_cleanup"
        assert action.target == "src/mod.py"
        assert action.level == FixLevel.L1_RULE
        assert action.status == FixStatus.PENDING
        assert action.confidence == FixConfidence.HIGH
        assert action.fingerprint != ""

    def test_fingerprint_deterministic(self):
        a1 = FixAction(action_type="zombie_cleanup", target="src/mod.py", before="old")
        a2 = FixAction(action_type="zombie_cleanup", target="src/mod.py", before="old")
        assert a1.fingerprint == a2.fingerprint

    def test_fingerprint_differs_for_different_input(self):
        a1 = FixAction(action_type="zombie_cleanup", target="src/a.py", before="old")
        a2 = FixAction(action_type="zombie_cleanup", target="src/b.py", before="old")
        assert a1.fingerprint != a2.fingerprint

    def test_fix_level_values(self):
        assert FixLevel.L1_RULE.value == "l1_rule"
        assert FixLevel.L2_LLM.value == "l2_llm"
        assert FixLevel.L3_AGENT.value == "l3_agent"

    def test_fix_status_values(self):
        assert FixStatus.PENDING.value == "pending"
        assert FixStatus.COMPLETED.value == "completed"
        assert FixStatus.FAILED.value == "failed"
        assert FixStatus.CANCELLED.value == "cancelled"

    def test_fix_confidence_values(self):
        assert FixConfidence.HIGH.value == "high"
        assert FixConfidence.MEDIUM.value == "medium"
        assert FixConfidence.LOW.value == "low"


class TestSafetyDecisionModel:
    def test_approved(self):
        sd = SafetyDecision(approved=True, confidence=FixConfidence.HIGH, reason="ok")
        assert sd.approved is True
        assert sd.confidence == FixConfidence.HIGH

    def test_denied(self):
        sd = SafetyDecision(approved=False, confidence=FixConfidence.LOW, reason="blocked")
        assert sd.approved is False
        assert sd.confidence == FixConfidence.LOW
