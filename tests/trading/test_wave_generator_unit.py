# [A_test] module_id: SRC-TST-2089 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-706 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_wave_generator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Unit tests for wave_generator.py (ADR-003)"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.governance.persistence.sqlite_schema import get_db_connection
from zephyr.orchestrator.execution.wave_generator import WaveGenerator


@pytest.fixture
def generator(tmp_db: Path) -> WaveGenerator:
    return WaveGenerator(db_path=tmp_db)


def _insert_task(conn, task_id: str, phase: int = 2, depends_on: list[str] | None = None) -> None:
    deps = json.dumps(depends_on or [])
    now = "2026-04-24T00:00:00+00:00"
    namespace = task_id.split("-")[0]
    seq = int(task_id.split("-")[-1])
    conn.execute("BEGIN")
    conn.execute(
        """INSERT OR REPLACE INTO tasks
           (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, depends_on, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'PENDING', 'P2', ?, 'glm', 'M', ?, ?, ?)""",
        (task_id, namespace, seq, task_id, phase, deps, now, now),
    )
    conn.execute("COMMIT")


class TestWaveGeneratorBasic:
    def test_empty_db_returns_empty(self, generator: WaveGenerator) -> None:
        waves = generator.generate_waves()
        assert waves == []

    def test_single_task_is_wave_0(self, generator: WaveGenerator, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001")
        conn.close()
        waves = generator.generate_waves()
        assert len(waves) == 1
        assert waves[0].wave_id == 0
        assert "ADR-001" in waves[0].task_ids

    def test_two_independent_tasks_same_wave(self, generator: WaveGenerator, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001")
        _insert_task(conn, "ADR-002")
        conn.close()
        waves = generator.generate_waves()
        assert len(waves) == 1
        assert len(waves[0].task_ids) == 2

    def test_dependent_tasks_separate_waves(self, generator: WaveGenerator, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001")
        _insert_task(conn, "ADR-002", depends_on=["ADR-001"])
        conn.close()
        waves = generator.generate_waves()
        assert len(waves) == 2
        assert "ADR-001" in waves[0].task_ids
        assert "ADR-002" in waves[1].task_ids

    def test_diamond_dependency(self, generator: WaveGenerator, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001")
        _insert_task(conn, "ADR-002", depends_on=["ADR-001"])
        _insert_task(conn, "ADR-003", depends_on=["ADR-001"])
        _insert_task(conn, "ADR-004", depends_on=["ADR-002", "ADR-003"])
        conn.close()
        waves = generator.generate_waves()
        assert len(waves) == 3
        assert "ADR-001" in waves[0].task_ids
        assert "ADR-002" in waves[1].task_ids
        assert "ADR-003" in waves[1].task_ids
        assert "ADR-004" in waves[2].task_ids

    def test_filter_by_phase(self, generator: WaveGenerator, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001", phase=2)
        _insert_task(conn, "STD-001", phase=1)
        conn.close()
        waves = generator.generate_waves(phase=2)
        assert len(waves) == 1
        assert "ADR-001" in waves[0].task_ids
        assert "STD-001" not in waves[0].task_ids


class TestGetNextWave:
    def test_returns_first_pending_wave(self, generator: WaveGenerator, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001")
        _insert_task(conn, "ADR-002", depends_on=["ADR-001"])
        conn.close()
        wave = generator.get_next_wave()
        assert wave is not None
        assert "ADR-001" in wave.task_ids

    def test_returns_none_when_all_completed(self, generator: WaveGenerator, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        now = "2026-04-24T00:00:00+00:00"
        conn.execute("BEGIN")
        conn.execute(
            """INSERT INTO tasks
               (task_id, namespace, seq, title, status, priority, phase, execution_model, safety_level, created_at, updated_at)
               VALUES ('ADR-001', 'ADR', 1, 'test', 'COMPLETED', 'P2', 2, 'glm', 'M', ?, ?)""",
            (now, now),
        )
        conn.execute("COMMIT")
        conn.close()
        wave = generator.get_next_wave()
        assert wave is None


class TestWaveStatus:
    def test_wave_status_counts(self, generator: WaveGenerator, tmp_db: Path) -> None:
        conn = get_db_connection(tmp_db)
        _insert_task(conn, "ADR-001")
        _insert_task(conn, "ADR-002")
        conn.close()

        conn = get_db_connection(tmp_db)
        conn.execute("BEGIN")
        conn.execute("UPDATE tasks SET status = 'COMPLETED' WHERE task_id = 'ADR-001'")
        conn.execute("COMMIT")
        conn.close()

        statuses = generator.wave_status()
        assert len(statuses) == 1
        assert statuses[0].completed == 1
        assert statuses[0].pending == 1
