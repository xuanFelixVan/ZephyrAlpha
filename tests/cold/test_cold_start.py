# [A_test] module_id: SRC-TST-0542 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_cold_start
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_cold_start.py -q
# [TTL] task_bound

from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import UTC, datetime
from unittest.mock import patch

from zephyr.gov_audit.cold_start import (
    DEFAULT_DB_PATH,
    DRIFT_EVENTS_SCHEMA,
    REQUIRED_DIRS,
    REQUIRED_ENV_VARS,
    ColdStartResult,
    detect_missing_env,
    init_database,
    init_directories,
)


class TestColdStartResult:
    def test_instantiation_defaults(self):
        r = ColdStartResult()
        assert r.dirs_created == []
        assert r.db_initialized is False
        assert r.missing_env == []
        assert r.first_scan_triggered is False
        assert r.warnings == []
        assert isinstance(r.timestamp, datetime)

    def test_instantiation_custom(self):
        now = datetime.now(UTC)
        r = ColdStartResult(
            dirs_created=["data/drift"],
            db_initialized=True,
            missing_env=["ZEPHYR_PROJECT_ROOT"],
            first_scan_triggered=True,
            warnings=["test warning"],
            timestamp=now,
        )
        assert r.dirs_created == ["data/drift"]
        assert r.db_initialized is True
        assert r.missing_env == ["ZEPHYR_PROJECT_ROOT"]
        assert r.first_scan_triggered is True
        assert r.warnings == ["test warning"]
        assert r.timestamp == now


class TestRequiredConstants:
    def test_required_dirs_non_empty(self):
        assert len(REQUIRED_DIRS) > 0

    def test_required_dirs_contain_key_paths(self):
        assert "data/drift" in REQUIRED_DIRS
        assert "temp" in REQUIRED_DIRS
        assert "logs" in REQUIRED_DIRS

    def test_required_env_vars_non_empty(self):
        assert len(REQUIRED_ENV_VARS) > 0

    def test_required_env_vars_contain_project_root(self):
        assert "ZEPHYR_PROJECT_ROOT" in REQUIRED_ENV_VARS

    def test_default_db_path_is_under_data(self):
        assert DEFAULT_DB_PATH.startswith("data/")


class TestInitDirectories:
    def test_creates_missing_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            created = init_directories(tmpdir)
            assert len(created) > 0
            for d in created:
                assert os.path.isdir(os.path.join(tmpdir, d))

    def test_existing_dirs_not_recreated(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for d in REQUIRED_DIRS:
                os.makedirs(os.path.join(tmpdir, d), exist_ok=True)
            created = init_directories(tmpdir)
            assert created == []

    def test_partial_existing_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, REQUIRED_DIRS[0]), exist_ok=True)
            created = init_directories(tmpdir)
            assert REQUIRED_DIRS[0] not in created
            assert len(created) == len(REQUIRED_DIRS) - 1


class TestInitDatabase:
    def test_creates_db_returns_boolean(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            result = init_database(tmpdir)
            assert isinstance(result, bool)

    def test_creates_db_directory(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            init_database(tmpdir)
            drift_dir = os.path.join(tmpdir, "data", "drift")
            assert os.path.isdir(drift_dir)

    def test_manual_schema_creates_table(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            statements = [
                s.strip()
                for s in DRIFT_EVENTS_SCHEMA.strip().split(";")
                if s.strip() and s.strip().startswith("CREATE")
            ]
            for stmt in statements:
                cursor.execute(stmt)
            conn.commit()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='drift_events'")
            assert cursor.fetchone() is not None
            conn.close()

    def test_manual_schema_creates_indexes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            statements = [
                s.strip()
                for s in DRIFT_EVENTS_SCHEMA.strip().split(";")
                if s.strip() and s.strip().startswith("CREATE")
            ]
            for stmt in statements:
                cursor.execute(stmt)
            conn.commit()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            conn.close()
            assert any("drift-detector" in idx or "drift_state" in idx or "drift_severity" in idx for idx in indexes)


class TestDetectMissingEnv:
    def test_missing_var_detected(self):
        with patch.dict(os.environ, {}, clear=True):
            missing = detect_missing_env()
            assert "ZEPHYR_PROJECT_ROOT" in missing

    def test_present_var_not_reported(self):
        with patch.dict(os.environ, {"ZEPHYR_PROJECT_ROOT": "/tmp/test"}, clear=True):
            missing = detect_missing_env()
            assert "ZEPHYR_PROJECT_ROOT" not in missing

    def test_returns_list(self):
        result = detect_missing_env()
        assert isinstance(result, list)


class TestDriftEventsSchema:
    def test_schema_contains_table(self):
        assert "drift_events" in DRIFT_EVENTS_SCHEMA

    def test_schema_contains_key_columns(self):
        assert "event_id" in DRIFT_EVENTS_SCHEMA
        assert "detector_id" in DRIFT_EVENTS_SCHEMA
        assert "severity" in DRIFT_EVENTS_SCHEMA
        assert "state" in DRIFT_EVENTS_SCHEMA
        assert "timestamp" in DRIFT_EVENTS_SCHEMA
