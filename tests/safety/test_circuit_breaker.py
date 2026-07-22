# [A_test] module_id: MOD-GOV_circuit_breaker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §16
# [MODULE] zephyr.security.adversarial_validation.circuit_breaker
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_circuit_breaker.py
# [TTL] task_bound

import time
from pathlib import Path

import pytest

cb_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.circuit_breaker",
    reason="circuit_breaker not available",
)
CircuitBreaker = cb_mod.CircuitBreaker
CircuitBreakerOpenError = cb_mod.CircuitBreakerOpenError
CircuitState = cb_mod.CircuitState
DEFAULT_COOL_DOWN_MS = cb_mod.DEFAULT_COOL_DOWN_MS
BYPASS_RATE_OPEN_THRESHOLD = cb_mod.BYPASS_RATE_OPEN_THRESHOLD

cleanup_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.cleanup",
    reason="cleanup not available",
)
Cleanup = cleanup_mod.Cleanup
CleanupVerificationError = cleanup_mod.CleanupVerificationError
CLEANUP_PATTERNS = cleanup_mod.CLEANUP_PATTERNS

models_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.models",
    reason="models not available",
)
RedBlueReport = models_mod.RedBlueReport


def _make_report(total: int, bypassed: int, circuit_breaker_open: bool = False) -> RedBlueReport:
    return RedBlueReport(
        session_id="test-session",
        total=total,
        bypassed=bypassed,
        blocked=max(total - bypassed, 0),
        circuit_breaker_open=circuit_breaker_open,
    )


class TestCircuitBreakerInitialState:
    def test_initial_state_is_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_open is False

    def test_before_run_ok_when_closed(self):
        cb = CircuitBreaker()
        cb.before_run()


class TestCircuitBreakerStateTransitions:
    def test_closed_to_open_on_high_bypass_rate(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=10, bypassed=5))
        assert cb.state == CircuitState.OPEN
        assert cb.is_open is True

    def test_no_trip_when_bypass_rate_below_threshold(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=10, bypassed=2))
        assert cb.state == CircuitState.CLOSED

    def test_before_run_raises_when_open(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=10, bypassed=5))
        with pytest.raises(CircuitBreakerOpenError):
            cb.before_run()

    def test_trip_via_circuit_breaker_open_flag(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=10, bypassed=0, circuit_breaker_open=True))
        assert cb.state == CircuitState.OPEN

    def test_full_state_cycle_closed_open_half_open_closed(self):
        cb = CircuitBreaker(cool_down_ms=10000)
        assert cb.state == CircuitState.CLOSED
        cb.after_run(_make_report(total=10, bypassed=5))
        assert cb.state == CircuitState.OPEN
        cb._opened_at = time.time() * 1000 - 11000
        assert cb.state == CircuitState.HALF_OPEN
        cb.after_run(_make_report(total=10, bypassed=1))
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerBypassThreshold:
    def test_avg_bypass_rate_above_30_percent_trips(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=10, bypassed=0))
        assert cb.state == CircuitState.CLOSED
        cb.after_run(_make_report(total=10, bypassed=10))
        assert cb.state == CircuitState.OPEN

    def test_avg_bypass_rate_uses_history(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=10, bypassed=3))
        assert cb.state == CircuitState.CLOSED
        cb.after_run(_make_report(total=10, bypassed=4))
        avg = (0.3 + 0.4) / 2
        assert avg > BYPASS_RATE_OPEN_THRESHOLD
        assert cb.state == CircuitState.OPEN

    def test_history_capped_at_20(self):
        cb = CircuitBreaker()
        for _ in range(25):
            cb.after_run(_make_report(total=10, bypassed=1))
        assert len(cb._bypass_history) == 20
        assert cb.state == CircuitState.CLOSED

    def test_zero_total_report_no_effect(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=0, bypassed=0))
        assert cb.state == CircuitState.CLOSED
        assert cb._bypass_history == []


class TestCircuitBreakerCoolDown:
    def test_default_cooldown_is_30000_ms(self):
        cb = CircuitBreaker()
        assert cb._cool_down_ms == DEFAULT_COOL_DOWN_MS
        assert cb._cool_down_ms == 30000

    def test_cooldown_clamped_to_min_10000_ms(self):
        cb = CircuitBreaker(cool_down_ms=5000)
        assert cb._cool_down_ms == 10000

    def test_open_to_half_open_after_cooldown(self):
        cb = CircuitBreaker(cool_down_ms=10000)
        cb.after_run(_make_report(total=10, bypassed=5))
        assert cb.state == CircuitState.OPEN
        cb._opened_at = time.time() * 1000 - 11000
        assert cb.state == CircuitState.HALF_OPEN

    def test_still_open_within_cooldown(self):
        cb = CircuitBreaker(cool_down_ms=10000)
        cb.after_run(_make_report(total=10, bypassed=5))
        cb._opened_at = time.time() * 1000 - 5000
        assert cb.state == CircuitState.OPEN
        with pytest.raises(CircuitBreakerOpenError):
            cb.before_run()

    def test_half_open_state_allows_before_run(self):
        cb = CircuitBreaker(cool_down_ms=10000)
        cb.after_run(_make_report(total=10, bypassed=5))
        cb._opened_at = time.time() * 1000 - 11000
        assert cb.state == CircuitState.HALF_OPEN
        cb.before_run()


class TestCircuitBreakerHalfOpenRecovery:
    def test_half_open_low_bypass_resets_to_closed(self):
        cb = CircuitBreaker(cool_down_ms=10000)
        cb.after_run(_make_report(total=10, bypassed=5))
        cb._opened_at = time.time() * 1000 - 11000
        assert cb.state == CircuitState.HALF_OPEN
        cb.after_run(_make_report(total=10, bypassed=1))
        assert cb.state == CircuitState.CLOSED

    def test_half_open_high_bypass_trips_again(self):
        cb = CircuitBreaker(cool_down_ms=10000)
        cb.after_run(_make_report(total=10, bypassed=5))
        cb._opened_at = time.time() * 1000 - 11000
        assert cb.state == CircuitState.HALF_OPEN
        cb.after_run(_make_report(total=10, bypassed=6))
        assert cb.state == CircuitState.OPEN


class TestCircuitBreakerTripMethod:
    def test_trip_sets_state_open(self):
        cb = CircuitBreaker()
        cb._trip()
        assert cb._state == CircuitState.OPEN
        assert cb.state == CircuitState.OPEN

    def test_trip_increments_trip_count(self):
        cb = CircuitBreaker()
        assert cb._trip_count == 0
        cb._trip()
        assert cb._trip_count == 1
        cb._trip()
        assert cb._trip_count == 2

    def test_trip_records_opened_at(self):
        cb = CircuitBreaker()
        before = time.time() * 1000
        cb._trip()
        after = time.time() * 1000
        assert before <= cb._opened_at <= after


class TestCircuitBreakerResetMethod:
    def test_reset_returns_to_closed(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=10, bypassed=5))
        assert cb.state == CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED

    def test_reset_clears_trip_count(self):
        cb = CircuitBreaker()
        cb._trip()
        cb._trip()
        assert cb._trip_count == 2
        cb.reset()
        assert cb._trip_count == 0

    def test_reset_clears_bypass_history(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=10, bypassed=5))
        assert len(cb._bypass_history) == 1
        cb.reset()
        assert cb._bypass_history == []

    def test_reset_clears_opened_at(self):
        cb = CircuitBreaker()
        cb._trip()
        assert cb._opened_at > 0
        cb.reset()
        assert cb._opened_at == 0.0

    def test_reset_allows_before_run(self):
        cb = CircuitBreaker()
        cb.after_run(_make_report(total=10, bypassed=5))
        with pytest.raises(CircuitBreakerOpenError):
            cb.before_run()
        cb.reset()
        cb.before_run()


class TestCleanupEnsureClean:
    def test_ensure_clean_no_residue(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        c = Cleanup()
        assert c.ensure_clean() is True

    def test_ensure_clean_removes_attack_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_attack_test1.txt").write_text("x", encoding="utf-8")
        (tmp_path / "_attack_test2.txt").write_text("y", encoding="utf-8")
        c = Cleanup()
        assert c.ensure_clean() is True
        assert not (tmp_path / "_attack_test1.txt").exists()
        assert not (tmp_path / "_attack_test2.txt").exists()

    def test_ensure_clean_removes_rb_backup(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "config.rb_backup").write_text("x", encoding="utf-8")
        c = Cleanup()
        assert c.ensure_clean() is True
        assert not (tmp_path / "config.rb_backup").exists()

    def test_ensure_clean_removes_temp_py(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_temp_foo.py").write_text("x", encoding="utf-8")
        c = Cleanup()
        assert c.ensure_clean() is True
        assert not (tmp_path / "_temp_foo.py").exists()

    def test_ensure_clean_removes_check_py(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_check_bar.py").write_text("x", encoding="utf-8")
        c = Cleanup()
        assert c.ensure_clean() is True
        assert not (tmp_path / "_check_bar.py").exists()

    def test_ensure_clean_removes_red_blue_temp(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        d = tmp_path / "data" / "red_blue"
        d.mkdir(parents=True)
        (d / "_temp_baz.yaml").write_text("x", encoding="utf-8")
        c = Cleanup()
        assert c.ensure_clean() is True
        assert not (d / "_temp_baz.yaml").exists()

    def test_ensure_clean_removes_checkpoint_yaml(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        d = tmp_path / "data" / "red_blue"
        d.mkdir(parents=True)
        (d / "checkpoint_001.yaml").write_text("x", encoding="utf-8")
        c = Cleanup()
        assert c.ensure_clean() is True
        assert not (d / "checkpoint_001.yaml").exists()

    def test_ensure_clean_removes_attack_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        d = tmp_path / "_attack_dir"
        d.mkdir()
        (d / "inner.txt").write_text("x", encoding="utf-8")
        c = Cleanup()
        assert c.ensure_clean() is True
        assert not d.exists()


class TestCleanupVerificationError:
    def test_ensure_clean_raises_when_residue_remains(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_attack_undeletable.txt").write_text("x", encoding="utf-8")

        def fail_unlink(self, *args, **kwargs):
            raise OSError("permission denied")

        monkeypatch.setattr(Path, "unlink", fail_unlink)
        c = Cleanup()
        with pytest.raises(CleanupVerificationError):
            c.ensure_clean()

    def test_verified_returns_false_on_residue(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_attack_undeletable.txt").write_text("x", encoding="utf-8")

        def fail_unlink(self, *args, **kwargs):
            raise OSError("permission denied")

        monkeypatch.setattr(Path, "unlink", fail_unlink)
        c = Cleanup()
        assert c.verified() is False

    def test_verified_returns_true_when_clean(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        c = Cleanup()
        assert c.verified() is True

    def test_cleanup_verification_error_is_runtime_error(self):
        assert issubclass(CleanupVerificationError, RuntimeError)


class TestCleanupBackupRestore:
    def test_backup_and_restore_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        f = tmp_path / "target.txt"
        f.write_text("original", encoding="utf-8")
        c = Cleanup()
        c.backup_file(f)
        f.write_text("modified", encoding="utf-8")
        assert f.read_text(encoding="utf-8") == "modified"
        assert c.restore_backups() is True
        assert f.read_text(encoding="utf-8") == "original"

    def test_backup_nonexistent_file_no_raise(self, tmp_path):
        c = Cleanup()
        c.backup_file(tmp_path / "nonexistent.txt")

    def test_backup_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        d = tmp_path / "subdir"
        d.mkdir()
        (d / "a.txt").write_text("a", encoding="utf-8")
        (d / "b.txt").write_text("b", encoding="utf-8")
        c = Cleanup()
        c.backup_directory(d)
        assert len(c._backups) >= 2
        (d / "a.txt").write_text("changed", encoding="utf-8")
        c.restore_backups()
        assert (d / "a.txt").read_text(encoding="utf-8") == "a"

    def test_restore_backups_clears_dict(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        f = tmp_path / "target.txt"
        f.write_text("original", encoding="utf-8")
        c = Cleanup()
        c.backup_file(f)
        c.restore_backups()
        assert c._backups == {}


class TestCleanupArtifact:
    def test_cleanup_artifact_file(self, tmp_path):
        f = tmp_path / "_attack_x.txt"
        f.write_text("x", encoding="utf-8")
        c = Cleanup()
        c.cleanup_artifact(f)
        assert not f.exists()

    def test_cleanup_artifact_directory(self, tmp_path):
        d = tmp_path / "_attack_dir"
        d.mkdir()
        (d / "inner.txt").write_text("x", encoding="utf-8")
        c = Cleanup()
        c.cleanup_artifact(d)
        assert not d.exists()

    def test_cleanup_artifact_nonexistent_no_raise(self, tmp_path):
        c = Cleanup()
        c.cleanup_artifact(tmp_path / "nonexistent")
