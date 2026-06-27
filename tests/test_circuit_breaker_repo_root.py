# [A_test] module_id: SRC-TST-0520 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-012 | docs/03_modules/_cross_layer/database/blueprint.md | §test
# [MODULE] tests.test_circuit_breaker_repo
# [INVARIANTS] circuit_breaker_state表CRUD完整性
# [MODIFY-GUARD] src/zephyr/db/circuit_breaker_repo.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/test_circuit_breaker_repo_root.py
# [TTL] task_bound

from __future__ import annotations

import sqlite3
from unittest.mock import patch

import pytest

cbt_mod = pytest.importorskip("zephyr.data.persistence.circuit_breaker_types")
CircuitBreakerState = cbt_mod.CircuitBreakerState

repo_mod = pytest.importorskip("zephyr.data.persistence.circuit_breaker_repo")
CircuitBreakerRecord = repo_mod.CircuitBreakerRecord
CircuitBreakerRepo = repo_mod.CircuitBreakerRepo

_DDL = """
CREATE TABLE IF NOT EXISTS circuit_breaker_state (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_module    TEXT    NOT NULL,
    target_module    TEXT    NOT NULL,
    state            TEXT    NOT NULL CHECK (state IN ('CLOSED', 'OPEN', 'HALF_OPEN')),
    failure_count    INTEGER NOT NULL DEFAULT 0,
    last_failure_at  TEXT,
    opened_at        TEXT,
    reason           TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(caller_module, target_module)
)
"""


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test_cb.db"
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(_DDL)
    conn.close()
    return path


@pytest.fixture
def repo(db_path):
    mock_conn = sqlite3.connect(str(db_path))
    mock_conn.row_factory = sqlite3.Row
    mock_conn.execute("PRAGMA journal_mode = WAL")
    mock_conn.execute("PRAGMA foreign_keys = ON")

    with patch("zephyr.data.persistence.circuit_breaker_repo.get_db_connection", return_value=mock_conn):
        with patch("zephyr.data.persistence.circuit_breaker_repo.DB_PATH", db_path):
            r = CircuitBreakerRepo(db_path=db_path)
            r._conn = mock_conn
            yield r
    mock_conn.close()


class TestCircuitBreakerRecord:
    def test_create_record(self):
        record = CircuitBreakerRecord(
            id=1,
            caller_module="mod_a",
            target_module="mod_b",
            state=CircuitBreakerState.CLOSED,
            failure_count=0,
            last_failure_at=None,
            opened_at=None,
            reason=None,
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert record.id == 1
        assert record.caller_module == "mod_a"
        assert record.state == CircuitBreakerState.CLOSED

    def test_record_is_frozen(self):
        record = CircuitBreakerRecord(
            id=1,
            caller_module="a",
            target_module="b",
            state=CircuitBreakerState.OPEN,
            failure_count=3,
            last_failure_at=None,
            opened_at=None,
            reason=None,
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        with pytest.raises(AttributeError):
            record.id = 99


class TestCircuitBreakerRepoInsert:
    def test_insert_returns_id(self, repo):
        row_id = repo.insert(
            caller="mod_a",
            target="mod_b",
            state=CircuitBreakerState.CLOSED,
        )
        assert isinstance(row_id, int)
        assert row_id > 0

    def test_insert_and_get(self, repo):
        repo.insert(
            caller="mod_a",
            target="mod_b",
            state=CircuitBreakerState.OPEN,
            failure_count=5,
            reason="too many failures",
        )
        record = repo.get_state("mod_a", "mod_b")
        assert record is not None
        assert record.caller_module == "mod_a"
        assert record.target_module == "mod_b"
        assert record.state == CircuitBreakerState.OPEN
        assert record.failure_count == 5
        assert record.reason == "too many failures"

    def test_get_nonexistent_returns_none(self, repo):
        result = repo.get_state("no_such", "no_target")
        assert result is None


class TestCircuitBreakerRepoUpdate:
    def test_update_state(self, repo):
        repo.insert(
            caller="mod_a",
            target="mod_b",
            state=CircuitBreakerState.CLOSED,
        )
        repo.update(
            caller="mod_a",
            target="mod_b",
            state=CircuitBreakerState.OPEN,
            failure_count=3,
            last_failure_at="2026-01-01T12:00:00",
            opened_at="2026-01-01T12:00:00",
            reason="threshold exceeded",
        )
        record = repo.get_state("mod_a", "mod_b")
        assert record is not None
        assert record.state == CircuitBreakerState.OPEN
        assert record.failure_count == 3


class TestCircuitBreakerRepoReset:
    def test_reset_to_closed(self, repo):
        repo.insert(
            caller="mod_a",
            target="mod_b",
            state=CircuitBreakerState.OPEN,
            failure_count=10,
        )
        repo.reset("mod_a", "mod_b")
        record = repo.get_state("mod_a", "mod_b")
        assert record is not None
        assert record.state == CircuitBreakerState.CLOSED
        assert record.failure_count == 0


class TestCircuitBreakerRepoListOpen:
    def test_list_open_returns_only_open(self, repo):
        repo.insert(caller="mod_a", target="mod_b", state=CircuitBreakerState.OPEN)
        repo.insert(caller="mod_c", target="mod_d", state=CircuitBreakerState.CLOSED)
        repo.insert(caller="mod_e", target="mod_f", state=CircuitBreakerState.OPEN)
        open_records = repo.list_open()
        assert len(open_records) == 2
        for r in open_records:
            assert r.state == CircuitBreakerState.OPEN

    def test_list_open_empty_when_none(self, repo):
        repo.insert(caller="mod_a", target="mod_b", state=CircuitBreakerState.CLOSED)
        assert repo.list_open() == []
