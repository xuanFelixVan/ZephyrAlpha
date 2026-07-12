# [A_test] module_id: SRC-TST-1342 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_orchestrator_wave_generator
# [INVARIANTS] WaveGenerator uses real SQLite via db_utils; tests create in-memory DB with tasks schema
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_orchestrator_wave_generator.py
# [TTL] task_bound

from __future__ import annotations

import json
import sqlite3

import pytest

from zephyr.orchestrator.execution.wave_generator import Wave, WaveGenerator, WaveStatus


def _create_test_db(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'PENDING',
            phase INTEGER NOT NULL DEFAULT 0,
            title TEXT NOT NULL DEFAULT '',
            execution_model TEXT NOT NULL DEFAULT 'deepseek',
            safety_level TEXT NOT NULL DEFAULT 'L',
            directive TEXT NOT NULL DEFAULT '',
            depends_on TEXT NOT NULL DEFAULT '[]',
            files_in_scope TEXT NOT NULL DEFAULT '[]',
            session_id TEXT,
            waiting_for TEXT,
            ready_at TEXT,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()
    return db_path


def _insert_task(db_path, task_id, depends_on=None, status="PENDING", phase=0):
    deps = json.dumps(depends_on or [])
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT OR REPLACE INTO tasks (task_id, status, phase, title, execution_model, safety_level, directive, depends_on, files_in_scope, created_at, updated_at) VALUES (?, ?, ?, ?, 'deepseek', 'L', '', ?, '[]', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')",
        (task_id, status, phase, f"Task {task_id}", deps),
    )
    conn.commit()
    conn.close()


@pytest.fixture
def test_db(tmp_path):
    return _create_test_db(tmp_path)


@pytest.fixture
def generator(test_db):
    return WaveGenerator(db_path=test_db)


class TestWave:
    def test_creation(self):
        w = Wave(wave_id=0, task_ids=["T-1", "T-2"])
        assert w.wave_id == 0
        assert w.task_ids == ["T-1", "T-2"]

    def test_default_task_ids(self):
        w = Wave(wave_id=0)
        assert w.task_ids == []


class TestWaveStatus:
    def test_creation(self):
        ws = WaveStatus(wave_id=0, total=5, completed=3, in_progress=1, pending=1)
        assert ws.total == 5
        assert ws.completed == 3


class TestWaveGeneratorGenerateWaves:
    def test_no_tasks(self, generator):
        waves = generator.generate_waves()
        assert waves == []

    def test_single_task_no_deps(self, generator, test_db):
        _insert_task(test_db, "T-1")
        waves = generator.generate_waves()
        assert len(waves) == 1
        assert waves[0].wave_id == 0
        assert "T-1" in waves[0].task_ids

    def test_multiple_tasks_no_deps(self, generator, test_db):
        _insert_task(test_db, "T-1")
        _insert_task(test_db, "T-2")
        waves = generator.generate_waves()
        assert len(waves) == 1
        assert len(waves[0].task_ids) == 2

    def test_linear_dependency_chain(self, generator, test_db):
        _insert_task(test_db, "T-1")
        _insert_task(test_db, "T-2", depends_on=["T-1"])
        _insert_task(test_db, "T-3", depends_on=["T-2"])
        waves = generator.generate_waves()
        assert len(waves) == 3
        assert "T-1" in waves[0].task_ids
        assert "T-2" in waves[1].task_ids
        assert "T-3" in waves[2].task_ids

    def test_diamond_dependency(self, generator, test_db):
        _insert_task(test_db, "T-1")
        _insert_task(test_db, "T-2", depends_on=["T-1"])
        _insert_task(test_db, "T-3", depends_on=["T-1"])
        _insert_task(test_db, "T-4", depends_on=["T-2", "T-3"])
        waves = generator.generate_waves()
        assert len(waves) == 3
        assert "T-1" in waves[0].task_ids
        assert set(waves[1].task_ids) == {"T-2", "T-3"}
        assert "T-4" in waves[2].task_ids

    def test_filter_by_phase(self, generator, test_db):
        _insert_task(test_db, "T-1", phase=0)
        _insert_task(test_db, "T-2", phase=1)
        waves = generator.generate_waves(phase=0)
        assert len(waves) == 1
        assert "T-1" in waves[0].task_ids

    def test_phase_filter_excludes_other_phases(self, generator, test_db):
        _insert_task(test_db, "T-1", phase=0)
        _insert_task(test_db, "T-2", phase=1)
        waves = generator.generate_waves(phase=1)
        task_ids = [tid for w in waves for tid in w.task_ids]
        assert "T-1" not in task_ids
        assert "T-2" in task_ids


class TestWaveGeneratorGetNextWave:
    def test_returns_first_actionable_wave(self, generator, test_db):
        _insert_task(test_db, "T-1", status="PENDING")
        _insert_task(test_db, "T-2", depends_on=["T-1"], status="PENDING")
        wave = generator.get_next_wave()
        assert wave is not None
        assert "T-1" in wave.task_ids

    def test_no_actionable_tasks(self, generator, test_db):
        _insert_task(test_db, "T-1", status="COMPLETED")
        wave = generator.get_next_wave()
        assert wave is None

    def test_all_completed_returns_none(self, generator, test_db):
        _insert_task(test_db, "T-1", status="COMPLETED")
        _insert_task(test_db, "T-2", status="VERIFIED")
        wave = generator.get_next_wave()
        assert wave is None

    def test_cancelled_skipped(self, generator, test_db):
        _insert_task(test_db, "T-1", status="CANCELLED")
        wave = generator.get_next_wave()
        assert wave is None


class TestWaveGeneratorWaveStatus:
    def test_wave_status_counts(self, generator, test_db):
        _insert_task(test_db, "T-1", status="COMPLETED")
        _insert_task(test_db, "T-2", status="IN_PROGRESS")
        _insert_task(test_db, "T-3", status="PENDING")
        statuses = generator.wave_status()
        assert len(statuses) == 1
        ws = statuses[0]
        assert ws.total == 3
        assert ws.completed == 1
        assert ws.in_progress == 1
        assert ws.pending == 1

    def test_wave_status_blocked(self, generator, test_db):
        _insert_task(test_db, "T-1", status="BLOCKED")
        statuses = generator.wave_status()
        assert len(statuses) == 1
        assert statuses[0].blocked == 1

    def test_wave_status_empty_db(self, generator):
        statuses = generator.wave_status()
        assert statuses == []

    def test_wave_status_multiple_waves(self, generator, test_db):
        _insert_task(test_db, "T-1", status="COMPLETED")
        _insert_task(test_db, "T-2", depends_on=["T-1"], status="PENDING")
        statuses = generator.wave_status()
        assert len(statuses) == 2
