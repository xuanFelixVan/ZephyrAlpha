# [A_test] module_id: MOD-GOV_rollback_budget | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_budget
# [INVARIANTS] consume() writes JSONL entry; release() decrements concurrent_count >= 0
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BudgetConsumeResult.allowed=False when any limit exceeded
# [TESTS] tests/test_rollback_budget.py
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from zephyr.infrastructure.rollback.rollback_budget import (
    BudgetConsumeResult,
    BudgetStatus,
    RollbackBudget,
)


class TestBudgetStatus:
    def test_default_values(self):
        s = BudgetStatus(
            daily_used=0,
            daily_limit=10,
            total_used=0,
            total_limit=100,
            current_concurrent=0,
            max_concurrent=3,
            available=True,
        )
        assert s.daily_used == 0
        assert s.daily_tokens_used == 0
        assert s.max_daily_tokens == 100000
        assert s.total_tokens_used == 0

    def test_custom_values(self):
        s = BudgetStatus(
            daily_used=5,
            daily_limit=10,
            total_used=50,
            total_limit=100,
            current_concurrent=2,
            max_concurrent=3,
            available=False,
            daily_tokens_used=50000,
            max_daily_tokens=100000,
            total_tokens_used=200000,
        )
        assert s.daily_used == 5
        assert s.total_tokens_used == 200000


class TestBudgetConsumeResult:
    def test_allowed_result(self):
        r = BudgetConsumeResult(allowed=True, reason="ok", remaining_daily=9, remaining_total=99)
        assert r.allowed is True
        assert r.remaining_daily == 9

    def test_denied_result(self):
        r = BudgetConsumeResult(allowed=False, reason="limit", remaining_daily=0, remaining_total=0)
        assert r.allowed is False


class TestRollbackBudgetInstantiation:
    def test_default_project_root(self):
        b = RollbackBudget()
        assert b._project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        assert b._project_root == tmp_path

    def test_none_project_root_defaults_to_cwd(self):
        b = RollbackBudget(project_root=None)
        assert b._project_root == Path.cwd()

    def test_initial_concurrent_count(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        assert b.concurrent_count == 0


class TestRollbackBudgetStatus:
    def test_status_empty_log(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        s = b.status()
        assert isinstance(s, BudgetStatus)
        assert s.daily_used == 0
        assert s.total_used == 0
        assert s.available is True
        assert s.daily_tokens_used == 0
        assert s.total_tokens_used == 0

    def test_status_with_entries(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        log_path = tmp_path / b.BUDGET_LOG
        log_path.parent.mkdir(parents=True, exist_ok=True)
        today = datetime.now(UTC).isoformat()
        entries = [
            {"timestamp_utc": today, "reason": "test", "token_cost": 100},
            {"timestamp_utc": today, "reason": "test2", "token_cost": 200},
        ]
        with open(log_path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        s = b.status()
        assert s.total_used == 2
        assert s.daily_used == 2
        assert s.total_tokens_used == 300
        assert s.daily_tokens_used == 300

    def test_status_malformed_entry_skipped(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        log_path = tmp_path / b.BUDGET_LOG
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("not json\n")
            f.write("\n")
        s = b.status()
        assert s.total_used == 0

    def test_status_missing_key_skipped(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        log_path = tmp_path / b.BUDGET_LOG
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"no_timestamp": True}) + "\n")
        s = b.status()
        assert s.total_used == 0


class TestRollbackBudgetConsume:
    def test_consume_allowed(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        r = b.consume(reason="test_rollback", token_cost=50)
        assert r.allowed is True
        assert r.remaining_daily == b.DAILY_LIMIT - 1
        assert r.remaining_total == b.TOTAL_LIMIT - 1

    def test_consume_writes_log(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        b.consume(reason="test_rollback", token_cost=50)
        log_path = tmp_path / b.BUDGET_LOG
        assert log_path.exists()
        with open(log_path, encoding="utf-8") as f:
            entry = json.loads(f.readline())
        assert entry["reason"] == "test_rollback"
        assert entry["token_cost"] == 50

    def test_consume_empty_reason(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        r = b.consume(reason="", token_cost=0)
        assert r.allowed is True

    def test_consume_daily_limit_reached(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        log_path = tmp_path / b.BUDGET_LOG
        log_path.parent.mkdir(parents=True, exist_ok=True)
        today = datetime.now(UTC).isoformat()
        for i in range(b.DAILY_LIMIT):
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"timestamp_utc": today, "reason": f"fill_{i}", "token_cost": 0}) + "\n")
        r = b.consume(reason="overflow")
        assert r.allowed is False
        assert "Daily limit" in r.reason

    def test_consume_total_limit_reached(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        log_path = tmp_path / b.BUDGET_LOG
        log_path.parent.mkdir(parents=True, exist_ok=True)
        old_date = datetime(2000, 1, 1, tzinfo=UTC).isoformat()
        for i in range(b.TOTAL_LIMIT):
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"timestamp_utc": old_date, "reason": f"fill_{i}", "token_cost": 0}) + "\n")
        r = b.consume(reason="overflow")
        assert r.allowed is False
        assert "Total limit" in r.reason

    def test_consume_concurrent_limit_reached(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        for _ in range(b.MAX_CONCURRENT):
            b.consume(reason="fill_concurrent")
        r = b.consume(reason="overflow")
        assert r.allowed is False
        assert "Concurrent limit" in r.reason

    def test_consume_daily_token_limit_reached(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        log_path = tmp_path / b.BUDGET_LOG
        log_path.parent.mkdir(parents=True, exist_ok=True)
        today = datetime.now(UTC).isoformat()
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp_utc": today, "reason": "big", "token_cost": 99999}) + "\n")
        r = b.consume(reason="overflow", token_cost=2)
        assert r.allowed is False
        assert "Daily token limit" in r.reason

    def test_consume_increments_concurrent(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        assert b.concurrent_count == 0
        b.consume(reason="first")
        assert b.concurrent_count == 1
        b.consume(reason="second")
        assert b.concurrent_count == 2


class TestRollbackBudgetRelease:
    def test_release_decrements_concurrent(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        b.consume(reason="test")
        assert b.concurrent_count == 1
        b.release()
        assert b.concurrent_count == 0

    def test_release_does_not_go_negative(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        b.release()
        assert b.concurrent_count == 0

    def test_release_multiple_times(self, tmp_path: Path):
        b = RollbackBudget(project_root=tmp_path)
        b.consume(reason="a")
        b.consume(reason="b")
        b.release()
        assert b.concurrent_count == 1
        b.release()
        assert b.concurrent_count == 0
