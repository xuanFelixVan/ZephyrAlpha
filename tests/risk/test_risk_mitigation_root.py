# [A_test] module_id: SRC-TST-1465 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_risk_mitigation
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_risk_mitigation.py
# [TTL] task_bound

import sqlite3
import threading
import time

import pytest

mod = pytest.importorskip("zephyr.feedback_loop.capacity_assurance.risk_mitigation", reason="risk_mitigation not available")
enable_wal_mode = mod.enable_wal_mode
perform_wal_checkpoint = mod.perform_wal_checkpoint
DeadlockDetector = mod.DeadlockDetector
AlertLinkIsolator = mod.AlertLinkIsolator
SchemaVersionGuard = mod.SchemaVersionGuard
TokenCalibration = mod.TokenCalibration
KillSwitchSafeguard = mod.KillSwitchSafeguard
SandboxHardener = mod.SandboxHardener
ProvenanceIntegrityChecker = mod.ProvenanceIntegrityChecker
incremental_hash_verify = mod.incremental_hash_verify
input_pattern_whitelist = mod.input_pattern_whitelist
kill_switch_channel_arbiter = mod.kill_switch_channel_arbiter
error_budget_reconciler = mod.error_budget_reconciler
slo_config_sanitizer = mod.slo_config_sanitizer
MigrationCrashRecovery = mod.MigrationCrashRecovery
unicode_path_normalizer = mod.unicode_path_normalizer
ChromaDBThreadGuard = mod.ChromaDBThreadGuard


class TestEnableWalMode:
    def test_enables_wal(self, tmp_path):
        db_path = str(tmp_path / "test_wal.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.commit()
        conn.close()
        result = enable_wal_mode(db_path)
        assert result is True

    def test_nonexistent_db(self, tmp_path):
        result = enable_wal_mode(str(tmp_path / "deep" / "nested" / "db.sqlite"))
        assert isinstance(result, bool)


class TestPerformWalCheckpoint:
    def test_checkpoint_on_wal_db(self, tmp_path):
        db_path = str(tmp_path / "test_ckpt.db")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.commit()
        conn.close()
        result = perform_wal_checkpoint(db_path)
        assert result is True


# 治本（2026-06-29 阶段A+）：删除 TestBackupCheckpoint 类（测已删除的 backup_checkpoint 函数）。


class TestDeadlockDetector:
    def test_instantiation(self):
        dd = DeadlockDetector()
        assert dd.timeout == 30.0
        assert dd.max_retries == 3

    def test_acquire_with_timeout(self):
        dd = DeadlockDetector(timeout=1.0)
        lock = threading.Lock()
        assert dd.acquire_with_timeout(lock) is True

    def test_acquire_with_timeout_fails(self):
        dd = DeadlockDetector(timeout=0.1)
        lock = threading.Lock()
        lock.acquire()
        assert dd.acquire_with_timeout(lock, timeout=0.01) is False

    def test_retry_with_backoff_success(self):
        dd = DeadlockDetector(max_retries=3, base_delay=0.01)
        result = dd.retry_with_backoff(lambda: 42)
        assert result == 42

    def test_retry_with_backoff_eventual_success(self):
        dd = DeadlockDetector(max_retries=3, base_delay=0.01)
        counter = {"n": 0}

        def flaky():
            counter["n"] += 1
            if counter["n"] < 3:
                raise RuntimeError("fail")
            return "ok"

        result = dd.retry_with_backoff(flaky)
        assert result == "ok"

    def test_retry_with_backoff_exhausted(self):
        dd = DeadlockDetector(max_retries=2, base_delay=0.01)
        with pytest.raises(RuntimeError, match="always fail"):
            dd.retry_with_backoff(lambda: (_ for _ in ()).throw(RuntimeError("always fail")))

    def test_ordered_lock_acquisition(self):
        dd = DeadlockDetector(timeout=1.0)
        locks = [threading.Lock() for _ in range(3)]
        assert dd.ordered_lock_acquisition(locks) is True
        for lock in locks:
            lock.release()

    def test_ordered_lock_acquisition_fails(self):
        dd = DeadlockDetector(timeout=0.1)
        locks = [threading.Lock() for _ in range(3)]
        locks[1].acquire()
        result = dd.ordered_lock_acquisition(locks)
        assert result is False


class TestAlertLinkIsolator:
    def test_instantiation(self):
        ali = AlertLinkIsolator()
        assert ali.queue.maxsize == 100

    def test_fire_and_forget(self):
        ali = AlertLinkIsolator()
        results = []
        result = ali.fire_and_forget(lambda: results.append(1))
        assert result is True
        time.sleep(0.2)
        ali.shutdown(wait=True)

    def test_fire_and_forget_queue_full(self):
        ali = AlertLinkIsolator(queue_size=2, max_workers=1)
        ali.queue.put((lambda: time.sleep(10), (), {}))
        ali.queue.put((lambda: time.sleep(10), (), {}))
        result = ali.fire_and_forget(lambda: None)
        assert result is False
        ali.shutdown(wait=False)


class TestSchemaVersionGuard:
    def test_instantiation(self):
        svg = SchemaVersionGuard()
        assert svg.expected_version == "2.6.0"

    def test_validate_config_version_match(self):
        svg = SchemaVersionGuard(expected_version="2.6.0")
        assert svg.validate_config_version("2.6.0") is True

    def test_validate_config_version_mismatch(self):
        svg = SchemaVersionGuard(expected_version="2.6.0")
        assert svg.validate_config_version("2.5.0") is False

    def test_check_schema_field(self):
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str = ""

        svg = SchemaVersionGuard()
        result = svg.check_schema_field(TestModel, "name")
        assert isinstance(result, bool)
        assert svg.check_schema_field(TestModel, "nonexistent") is False


class TestTokenCalibration:
    def test_instantiation(self):
        tc = TokenCalibration()
        assert tc.get_correction_factor() == 1.0
        assert tc.get_accuracy_ratio() == 1.0

    def test_record_and_correction_factor(self):
        tc = TokenCalibration(window_size=10)
        tc.record(100, 80)
        assert tc.get_correction_factor() == 0.8

    def test_record_multiple(self):
        tc = TokenCalibration(window_size=10)
        tc.record(100, 80)
        tc.record(100, 120)
        assert tc.get_correction_factor() == 1.0

    def test_window_eviction(self):
        tc = TokenCalibration(window_size=2)
        tc.record(100, 50)
        tc.record(100, 60)
        tc.record(100, 90)
        assert len(tc.window) == 2

    def test_zero_estimated(self):
        tc = TokenCalibration()
        tc.record(0, 100)
        assert tc.get_correction_factor() == 1.0


class TestKillSwitchSafeguard:
    def test_instantiation(self):
        kss = KillSwitchSafeguard()
        assert kss.should_trigger() is False

    def test_single_condition_not_enough(self):
        kss = KillSwitchSafeguard(sustain_duration=0.0)
        kss.register_condition(True)
        assert kss.should_trigger() is False

    def test_two_conditions_trigger(self):
        kss = KillSwitchSafeguard(sustain_duration=0.0)
        kss.register_condition(True)
        kss.register_condition(True)
        time.sleep(0.01)
        assert kss.should_trigger() is True

    def test_manual_override(self):
        kss = KillSwitchSafeguard(sustain_duration=0.0)
        kss.register_condition(True)
        kss.register_condition(True)
        kss.manual_override()
        assert kss.should_trigger() is False

    def test_condition_unregister(self):
        kss = KillSwitchSafeguard(sustain_duration=0.0)
        kss.register_condition(True)
        kss.register_condition(True)
        kss.register_condition(False)
        assert kss.should_trigger() is False


class TestSandboxHardener:
    def test_enforce_no_violations(self):
        limits = {"max_memory_mb": 256, "max_execution_seconds": 30, "max_file_descriptors": 32}
        violations = SandboxHardener.enforce(limits)
        assert violations == []

    def test_enforce_with_violations(self):
        limits = {"max_memory_mb": 1024, "max_execution_seconds": 30, "max_file_descriptors": 32}
        violations = SandboxHardener.enforce(limits)
        assert len(violations) == 1
        assert "max_memory_mb" in violations[0]

    def test_enforce_missing_keys(self):
        limits = {}
        violations = SandboxHardener.enforce(limits)
        assert violations == []


class TestProvenanceIntegrityChecker:
    def test_verify_chain_empty_db(self, tmp_path):
        db_path = str(tmp_path / "test_prov.db")
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE ai_provenance (id INTEGER, prev_hash TEXT, curr_hash TEXT, module TEXT, field TEXT, old_value TEXT, new_value TEXT, author_agent TEXT)"
        )
        conn.commit()
        conn.close()
        checker = ProvenanceIntegrityChecker(db_path)
        ok, errors = checker.verify_chain()
        assert ok is True
        assert errors == []

    def test_verify_chain_nonexistent_db(self):
        checker = ProvenanceIntegrityChecker("/nonexistent/db.sqlite")
        ok, errors = checker.verify_chain()
        assert ok is False


class TestIncrementalHashVerify:
    def test_empty_db(self, tmp_path):
        db_path = str(tmp_path / "test_inc.db")
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE ai_provenance (id INTEGER, prev_hash TEXT, curr_hash TEXT, module TEXT, field TEXT, old_value TEXT, new_value TEXT, author_agent TEXT)"
        )
        conn.commit()
        conn.close()
        assert incremental_hash_verify(db_path) is True


class TestInputPatternWhitelist:
    def test_no_patterns(self):
        assert input_pattern_whitelist("anything") is True

    def test_matching_pattern(self):
        assert input_pattern_whitelist("hello world", ["hello"]) is True

    def test_no_matching_pattern(self):
        assert input_pattern_whitelist("hello world", ["xyz"]) is False

    def test_empty_input(self):
        assert input_pattern_whitelist("", ["test"]) is False


class TestKillSwitchChannelArbiter:
    def test_file_signal_exists(self, tmp_path):
        signal_file = str(tmp_path / "kill_switch.signal")
        with open(signal_file, "w", encoding="utf-8") as f:
            f.write("1")
        assert kill_switch_channel_arbiter(signal_file, "KILL_SWITCH") is True

    def test_env_var_set(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TEST_KS_VAR", "1")
        assert kill_switch_channel_arbiter(str(tmp_path / "nonexistent.signal"), "TEST_KS_VAR") is True

    def test_neither_set(self, tmp_path, monkeypatch):
        monkeypatch.delenv("TEST_KS_NONE", raising=False)
        assert kill_switch_channel_arbiter(str(tmp_path / "nonexistent.signal"), "TEST_KS_NONE") is False


class TestErrorBudgetReconciler:
    def test_matching_values(self):
        assert error_budget_reconciler(100.0, 100.0) is True

    def test_within_tolerance(self):
        assert error_budget_reconciler(100.0, 100.005, tolerance=0.01) is True

    def test_outside_tolerance(self):
        assert error_budget_reconciler(100.0, 110.0, tolerance=0.01) is False

    def test_zero_aggregated(self):
        assert error_budget_reconciler(0.0, 0.0) is True


class TestSloConfigSanitizer:
    def test_sanitizes_sensitive_keys(self):
        config = {"threshold": 0.95, "name": "test"}
        result = slo_config_sanitizer(config)
        assert result["threshold"] == "***"
        assert result["name"] == "test"

    def test_nested_sanitization(self):
        config = {"outer": {"budget": 100, "label": "ok"}}
        result = slo_config_sanitizer(config)
        assert result["outer"]["budget"] == "***"
        assert result["outer"]["label"] == "ok"

    def test_empty_dict(self):
        assert slo_config_sanitizer({}) == {}

    def test_non_numeric_sensitive(self):
        config = {"threshold": "high"}
        result = slo_config_sanitizer(config)
        assert result["threshold"] == "high"


class TestMigrationCrashRecovery:
    def test_instantiation(self, tmp_path):
        checkpoint = str(tmp_path / "checkpoint.txt")
        mcr = MigrationCrashRecovery(checkpoint)
        assert mcr.get_completed_batches() == []

    def test_mark_and_retrieve(self, tmp_path):
        checkpoint = str(tmp_path / "checkpoint.txt")
        mcr = MigrationCrashRecovery(checkpoint)
        mcr.mark_batch_complete("batch_1")
        mcr.mark_batch_complete("batch_2")
        batches = mcr.get_completed_batches()
        assert "batch_1" in batches
        assert "batch_2" in batches


class TestUnicodePathNormalizer:
    def test_normalizes_backslashes(self):
        result = unicode_path_normalizer("C:\\Users\\test")
        assert "\\" not in result

    def test_normalizes_case(self):
        result = unicode_path_normalizer("Hello/World")
        assert result == "hello/world"

    def test_empty_string(self):
        result = unicode_path_normalizer("")
        assert isinstance(result, str)


class TestChromaDBThreadGuard:
    def test_instantiation(self):
        guard = ChromaDBThreadGuard(max_workers=2)
        assert guard.max_workers == 2

    def test_submit_task(self):
        guard = ChromaDBThreadGuard(max_workers=2)
        future = guard.submit(lambda: 42)
        assert future.result() == 42
        guard.shutdown(wait=True)

    def test_recycle_after_threshold(self):
        guard = ChromaDBThreadGuard(max_workers=2)
        guard._recycle_threshold = 3
        for i in range(4):
            guard.submit(lambda: None)
        assert guard._task_count == 1
        guard.shutdown(wait=True)
