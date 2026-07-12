# [A_test] module_id: SRC-TST-0179 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-336 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_verify_b54_b56_b59_deep
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Deeper integration test: P0 inflation guard + block_sessions_count + timeout exemption"""

import warnings
from datetime import UTC, datetime
from pathlib import Path

import pytest

from zephyr.governance.persistence.task_repo import (
    P0InflationFrozenError,
    TaskRepository,
)
from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus
from zephyr.integration.shared.schema.severity_types import Priority as P
from zephyr.shared.foundation.models import TaskCard

now = datetime.now(UTC)


def mt(suffix, priority=P.P2, tags=None):
    seq = 99900 + suffix
    return TaskCard(
        task_id=f"CP-{seq:05d}",
        namespace=TaskNamespace.CP,
        seq=seq,
        title=f"Test-{suffix}",
        status=TaskStatus.PENDING,
        priority=priority,
        phase=9,
        execution_model="deepseek",
        safety_level="M",
        source_blueprint="test",
        source_section="test",
        description=f"Test task {suffix}",
        tags=tags or [],
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def repo(tmp_path: Path) -> TaskRepository:
    db = tmp_path / "test_deep.db"
    r = TaskRepository(db_path=db, auto_init=True, enable_gate=False)
    yield r
    r.close()


class TestP0InflationGuard:
    def test_p0_frozen_when_at_cap(self, repo: TaskRepository) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            for i in range(5):
                repo.create(mt(100 + i, P.P0))
        t = mt(200, P.P0)
        with pytest.raises(P0InflationFrozenError):
            repo.create(t)

    def test_p0_warning_when_near_cap(self, repo: TaskRepository) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            for i in range(3):
                repo.create(mt(110 + i, P.P0))
        t = mt(210, P.P0)
        with pytest.warns(UserWarning):
            tcard = repo.create(t)
        assert tcard is not None
        repo.hard_delete(t.task_id)

    def test_p0_allowed_when_below_threshold(self, repo: TaskRepository) -> None:
        t = mt(220, P.P0)
        tcard = repo.create(t)
        assert tcard is not None
        repo.hard_delete(t.task_id)


class TestBlockSessionsCount:
    def test_increments_on_blocked(self, repo: TaskRepository) -> None:
        t = mt(1)
        repo.create(t)
        repo.transition(t.task_id, TaskStatus.IN_PROGRESS)
        repo.transition(t.task_id, TaskStatus.BLOCKED, waiting_for="test")
        after_b1 = repo.get(t.task_id)
        assert after_b1.block_sessions_count == 1

        repo.transition(t.task_id, TaskStatus.READY)
        repo.transition(t.task_id, TaskStatus.IN_PROGRESS)
        repo.transition(t.task_id, TaskStatus.BLOCKED, waiting_for="test2")
        after_b2 = repo.get(t.task_id)
        assert after_b2.block_sessions_count == 2
        repo.transition(t.task_id, TaskStatus.READY)
        repo.hard_delete(t.task_id)


class TestEscalation:
    def test_p0_escalation_at_two_blocked(self, repo: TaskRepository) -> None:
        t = mt(3, P.P0)
        repo.create(t)
        esc0 = repo.check_escalation(t.task_id)
        assert esc0 is None

        repo.transition(t.task_id, TaskStatus.IN_PROGRESS)
        repo.transition(t.task_id, TaskStatus.BLOCKED, waiting_for="t3b1")
        repo.transition(t.task_id, TaskStatus.READY)
        repo.transition(t.task_id, TaskStatus.IN_PROGRESS)
        repo.transition(t.task_id, TaskStatus.BLOCKED, waiting_for="t3b2")
        esc2 = repo.check_escalation(t.task_id)
        assert esc2 is not None
        assert "P0" in str(esc2["triggers"])
        repo.transition(t.task_id, TaskStatus.READY)
        repo.hard_delete(t.task_id)


class TestTimeoutExemption:
    def test_exempt_tag_skips_timeout(self, repo: TaskRepository) -> None:
        t = mt(4, tags=["exempt:timeout", "test"])
        repo.create(t)
        assert repo._is_timeout_exempt(t.task_id) is True
        assert repo.check_task_timeout(t.task_id) is None

    def test_list_by_tag_finds_exempt(self, repo: TaskRepository) -> None:
        t = mt(14, tags=["exempt:timeout", "test"])
        repo.create(t)
        tagged = repo.list_by_tag("exempt:timeout")
        assert t.task_id in [x.task_id for x in tagged]
        repo.hard_delete(t.task_id)


class TestProposePriorityUpgrade:
    def test_upgrade_to_p0_frozen_at_cap(self, repo: TaskRepository) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            for i in range(5):
                repo.create(mt(120 + i, P.P0))
        t = mt(230)
        repo.create(t)
        with pytest.raises(P0InflationFrozenError):
            repo.propose_priority_upgrade(t.task_id, "P0")
        repo.hard_delete(t.task_id)

    def test_upgrade_to_p0_sets_approval(self, repo: TaskRepository) -> None:
        t = mt(240)
        repo.create(t)
        repo.propose_priority_upgrade(t.task_id, "P0")
        upgraded = repo.get(t.task_id)
        assert upgraded.approval_required == 1
        assert upgraded.priority_proposed == "P0"
        repo.reject_priority_upgrade(t.task_id)
        repo.hard_delete(t.task_id)
