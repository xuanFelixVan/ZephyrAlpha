# [A_test] module_id: SRC-TST-1855 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-483 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.db.test_circuit_breaker_repo
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
=============================================
覆盖矩阵：
  CircuitBreakerRepo.insert:
    - 正常插入 × 1
    - 返回 lastrowid × 1
  CircuitBreakerRepo.get_state:
    - 查询已有记录 × 1
    - 无匹配返回 None × 1
  CircuitBreakerRepo.update:
    - 更新状态 × 1
  CircuitBreakerRepo.reset:
    - 重置为 CLOSED × 1
  CircuitBreakerRepo.list_open:
    - 列出 OPEN 状态 × 1
  CircuitBreakerRecord:
    - frozen dataclass × 1
=============================================
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.integration.shared.schema.severity_types import CircuitBreakerState
from zephyr.shared.utils.db_utils import ensure_schema
from zephyr.ops.circuit_breaker_repo import CircuitBreakerRecord, CircuitBreakerRepo


@pytest.fixture()
def repo(tmp_path: Path) -> CircuitBreakerRepo:
    db = tmp_path / "test_cb.db"
    ensure_schema(db)
    r = CircuitBreakerRepo(db_path=db)
    yield r
    r.close()


class TestCircuitBreakerRepoInsert:
    def test_insert_returns_id(self, repo: CircuitBreakerRepo) -> None:
        row_id = repo.insert(
            caller="module_a",
            target="module_b",
            state=CircuitBreakerState.CLOSED,
        )
        assert isinstance(row_id, int)
        assert row_id > 0

    def test_insert_with_reason(self, repo: CircuitBreakerRepo) -> None:
        row_id = repo.insert(
            caller="module_c",
            target="module_d",
            state=CircuitBreakerState.OPEN,
            reason="too many errors",
        )
        assert row_id > 0


class TestCircuitBreakerRepoGetState:
    def test_get_existing(self, repo: CircuitBreakerRepo) -> None:
        repo.insert(
            caller="mod_x",
            target="mod_y",
            state=CircuitBreakerState.CLOSED,
        )
        record = repo.get_state("mod_x", "mod_y")
        assert record is not None
        assert record.caller_module == "mod_x"
        assert record.target_module == "mod_y"
        assert record.state == CircuitBreakerState.CLOSED

    def test_get_nonexistent(self, repo: CircuitBreakerRepo) -> None:
        record = repo.get_state("no_such", "no_such")
        assert record is None


class TestCircuitBreakerRepoUpdate:
    def test_update_state(self, repo: CircuitBreakerRepo) -> None:
        repo.insert(
            caller="mod_u",
            target="mod_v",
            state=CircuitBreakerState.CLOSED,
        )
        repo.update(
            caller="mod_u",
            target="mod_v",
            state=CircuitBreakerState.OPEN,
            failure_count=5,
            last_failure_at="2026-01-01T00:00:00",
            opened_at="2026-01-01T00:00:00",
            reason="threshold exceeded",
        )
        record = repo.get_state("mod_u", "mod_v")
        assert record is not None
        assert record.state == CircuitBreakerState.OPEN
        assert record.failure_count == 5


class TestCircuitBreakerRepoReset:
    def test_reset_to_closed(self, repo: CircuitBreakerRepo) -> None:
        repo.insert(
            caller="mod_r",
            target="mod_s",
            state=CircuitBreakerState.OPEN,
            reason="error",
        )
        repo.reset("mod_r", "mod_s")
        record = repo.get_state("mod_r", "mod_s")
        assert record is not None
        assert record.state == CircuitBreakerState.CLOSED
        assert record.failure_count == 0
        assert record.reason is None


class TestCircuitBreakerRepoListOpen:
    def test_list_open(self, repo: CircuitBreakerRepo) -> None:
        repo.insert(
            caller="open_1",
            target="target_1",
            state=CircuitBreakerState.OPEN,
            reason="error",
        )
        repo.insert(
            caller="closed_1",
            target="target_2",
            state=CircuitBreakerState.CLOSED,
        )
        open_records = repo.list_open()
        assert len(open_records) >= 1
        assert all(r.state == CircuitBreakerState.OPEN for r in open_records)


class TestCircuitBreakerRecord:
    def test_frozen(self) -> None:
        r = CircuitBreakerRecord(
            id=1,
            caller_module="a",
            target_module="b",
            state=CircuitBreakerState.CLOSED,
            failure_count=0,
            last_failure_at=None,
            opened_at=None,
            reason=None,
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        with pytest.raises(AttributeError):
            r.state = CircuitBreakerState.OPEN  # type: ignore[misc]
