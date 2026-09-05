# [A_test] module_id: MOD-GOV_task_repo_batch_api | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md | §task-system
# [MODULE] tests.governance.persistence.test_task_repo_batch_api
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] get_distinct_batch_ids/get_task_batch_ids 只读; 空串/NULL batch_id 不入返回值; 软删行排除
# [MODIFY-GUARD] src/zephyr/governance/persistence/task_repo.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on invalid status literal
# [TESTS] —
# [A_module] module_id=MOD-TASK_SYSTEM | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""单元测试：TaskRepository batch_id 公开 API（AI-AUDIT13-002 主项① + B1 治本 2026-09-05）

覆盖矩阵
--------
get_distinct_batch_ids : IN_PROGRESS 批次去重 / 无批次排除 / 空串排除 / 软删排除 / 字符串入参 / 非法状态码
get_task_batch_ids     : task_id->batch_id 映射 / 无批次排除 / 多批次映射 / NULL 排除 / 软删排除 / 字符串入参
写入公共 API（B1 治本）: create/upsert batch_id 参数 / assign_batch / get_task_batch_id /
                         new_batch_id 命名约定 / create→READY→claim_next 端到端

语义对齐旁路 SQL（src/zephyr/trading/conductor.py:173 / src/zephyr/trading/autopilot.py:109,160），
供 AI-06 下一轮接线收敛。注：batch_id 是 tasks 表内部列（TaskCard 不承载）；
B1 治本后写入走公共 API（create/upsert/assign_batch），存量裸 SQL helper 保留作底层语义对照。
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace, TaskStatus
from zephyr.governance.persistence.task_repo import TaskRepository, new_batch_id
from zephyr.shared.foundation.models import TaskCard
from zephyr.shared.schema.base_config import Classification, EvolutionPolicy
from zephyr.shared.schema.severity_types import SafetyLevel

_UTC = UTC


def _make_task(
    task_id: str = "SRC-1",
    status: TaskStatus = TaskStatus.PENDING,
    phase: int = 1,
    namespace: TaskNamespace = TaskNamespace.SRC,
    seq: int | None = None,
) -> TaskCard:
    now = datetime.now(_UTC)
    if seq is None:
        try:
            seq = int(task_id.split("-")[1])
        except (IndexError, ValueError):
            seq = 1
    return TaskCard(
        task_id=task_id,
        namespace=namespace,
        seq=seq,
        phase=phase,
        title=f"Task {task_id}",
        status=status,
        execution_model="claude",
        safety_level=SafetyLevel.M,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=1.0,
        source_blueprint="test",
        source_section="test",
        description=f"根因：测试 TaskRepository batch_id 公开 API。治根：验证 get_distinct_batch_ids/get_task_batch_ids 语义。施工步骤：(1) 建卡 (2) 写入 batch_id。验收标准：API 返回与旁路 SQL 语义一致。",
        files_in_scope=["src/zephyr/governance/persistence/task_repo.py"],
        deliverables=["test deliverable"],
        applicable_rules=[{"module_id": "GOV-TASK-001", "section": "v3.0.0", "reason": "test"}],
        allowed_touch=["src/zephyr/governance/persistence/task_repo.py"],
        rollback_instructions="git checkout -- task_repo.py",
        post_sync_standard=["echo ok"],
        acceptance=["exit=0"],
        dependency_type="none",
        session_id=None,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture()
def repo(tmp_path: Path) -> TaskRepository:
    db = tmp_path / "test_data/databases/governance.db"
    r = TaskRepository(db_path=db, auto_init=True, enable_gate=False)
    yield r
    r.close()


def _make_in_progress_with_batch(repo: TaskRepository, task_id: str, batch_id: str | None) -> None:
    """建卡推进到 IN_PROGRESS 并写入 batch_id（batch_id 为内部列，测试直接 SQL 准备数据）。"""
    repo.create(_make_task(task_id))
    repo.transition(task_id, TaskStatus.IN_PROGRESS)
    with repo._write_tx() as conn:
        conn.execute("UPDATE tasks SET batch_id = ? WHERE task_id = ?", (batch_id, task_id))


class TestGetDistinctBatchIds:
    def test_in_progress_batch_dedup(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        _make_in_progress_with_batch(repo, "SRC-2", "batch-B")
        # 同批次第二个任务不产生重复 batch_id
        _make_in_progress_with_batch(repo, "SRC-3", "batch-A")
        result = repo.get_distinct_batch_ids(TaskStatus.IN_PROGRESS)
        assert sorted(result) == ["batch-A", "batch-B"]

    def test_unbatched_status_returns_empty(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-1"))
        repo.transition("SRC-1", TaskStatus.IN_PROGRESS)
        # batch_id 为 NULL（无批次任务）-> 不入返回值
        assert repo.get_distinct_batch_ids(TaskStatus.IN_PROGRESS) == []

    def test_empty_string_batch_id_excluded(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "")
        assert repo.get_distinct_batch_ids(TaskStatus.IN_PROGRESS) == []

    def test_soft_deleted_excluded(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        repo.delete("SRC-1")
        assert repo.get_distinct_batch_ids(TaskStatus.IN_PROGRESS) == []

    def test_string_status_accepted(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        assert repo.get_distinct_batch_ids("IN_PROGRESS") == ["batch-A"]

    def test_invalid_status_raises(self, repo: TaskRepository) -> None:
        with pytest.raises(ValueError):
            repo.get_distinct_batch_ids("NOT_A_STATUS")


class TestGetTaskBatchIds:
    def test_claimed_task_mapping(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {"SRC-1": "batch-A"}

    def test_unbatched_task_not_in_mapping(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-1"))
        repo.transition("SRC-1", TaskStatus.IN_PROGRESS)
        # 无批次任务不在映射中，调用方以哨兵值兜底（对齐 autopilot COALESCE 语义）
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {}

    def test_multiple_batches_mapping(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        _make_in_progress_with_batch(repo, "SRC-2", "batch-B")
        _make_in_progress_with_batch(repo, "SRC-3", "batch-A")
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {
            "SRC-1": "batch-A",
            "SRC-3": "batch-A",
            "SRC-2": "batch-B",
        }

    def test_null_batch_id_excluded(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        with repo._write_tx() as conn:
            conn.execute("UPDATE tasks SET batch_id = NULL WHERE task_id = 'SRC-1'")
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {}

    def test_soft_deleted_excluded(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        repo.delete("SRC-1")
        assert repo.get_task_batch_ids(TaskStatus.IN_PROGRESS) == {}

    def test_string_status_accepted(self, repo: TaskRepository) -> None:
        _make_in_progress_with_batch(repo, "SRC-1", "batch-A")
        assert repo.get_task_batch_ids("IN_PROGRESS") == {"SRC-1": "batch-A"}


# ══════════════════════════════════════════════════════════════════
# B1 治本（2026-09-05）：批次写入公共 API——create/upsert batch_id 参数、
# assign_batch、get_task_batch_id、new_batch_id、claim_next 端到端。
# 治本前：生产零写入方（裸 SQL 仅存于测试），claim_next 恒 None（静默失效）。
# ══════════════════════════════════════════════════════════════════


class TestBatchWritePublicApi:
    def test_create_with_batch_id_end_to_end_claim(self, repo: TaskRepository) -> None:
        """B1 核心回归：create_and_ready(batch_id) → claim_next(batch_id) 端到端闭环。"""
        repo.create_and_ready(
            _make_task("SRC-1"), allow_direct_create=True, batch_id="decomp-20260905-abc123"
        )
        assert repo.get_task_batch_id("SRC-1") == "decomp-20260905-abc123"
        assert repo.get("SRC-1").status == TaskStatus.READY
        claimed = repo.claim_next("decomp-20260905-abc123", worker_id="w1")
        assert claimed is not None and claimed.task_id == "SRC-1"

    def test_create_and_ready_rejects_dep_tasks(self, repo: TaskRepository) -> None:
        task = _make_task("SRC-1")
        task.depends_on = ["SRC-0"]
        with pytest.raises(ValueError, match="depends_on"):
            repo.create_and_ready(task, allow_direct_create=True)

    def test_create_without_batch_id_claim_returns_none(self, repo: TaskRepository) -> None:
        """无批次任务不可认领（历史语义锁定，__no_batch__ 哨兵非真实批次）。"""
        repo.create_and_ready(_make_task("SRC-1"), allow_direct_create=True)
        assert repo.get("SRC-1").status == TaskStatus.READY
        assert repo.claim_next("__no_batch__", worker_id="w1") is None

    def test_upsert_new_row_writes_batch_id(self, repo: TaskRepository) -> None:
        repo.upsert(_make_task("SRC-1"), batch_id="mcp-20260905-fff000")
        assert repo.get_task_batch_id("SRC-1") == "mcp-20260905-fff000"

    def test_upsert_conflict_preserves_existing_batch(self, repo: TaskRepository) -> None:
        """冲突更新不覆盖既有批次（upsert SET 子句不含 batch_id）。"""
        repo.upsert(_make_task("SRC-1"), batch_id="mcp-20260905-fff000")
        repo.upsert(_make_task("SRC-1"), batch_id="other-batch")
        assert repo.get_task_batch_id("SRC-1") == "mcp-20260905-fff000"

    def test_assign_batch_reassign_and_count(self, repo: TaskRepository) -> None:
        repo.create(_make_task("SRC-1"), allow_direct_create=True)
        repo.create(_make_task("SRC-2"), allow_direct_create=True)
        # 不存在的 task_id 不计入；存在的成功归属
        assert repo.assign_batch(["SRC-1", "SRC-2", "SRC-404"], "finding-20260905-aaa111") == 2
        assert repo.get_task_batch_id("SRC-1") == "finding-20260905-aaa111"
        assert repo.get_task_batch_id("SRC-2") == "finding-20260905-aaa111"

    def test_assign_batch_empty_batch_id_rejected(self, repo: TaskRepository) -> None:
        with pytest.raises(ValueError):
            repo.assign_batch(["SRC-1"], "")

    def test_assign_batch_empty_task_ids_noop(self, repo: TaskRepository) -> None:
        assert repo.assign_batch([], "batch-A") == 0

    def test_assign_batch_makes_legacy_task_claimable(self, repo: TaskRepository) -> None:
        """存量无批次任务补录批次后即可认领（B1 存量修复通道）。"""
        repo.create_and_ready(_make_task("SRC-1"), allow_direct_create=True)
        assert repo.claim_next("backfill-20260905-bbb222", worker_id="w1") is None
        repo.assign_batch(["SRC-1"], "backfill-20260905-bbb222")
        claimed = repo.claim_next("backfill-20260905-bbb222", worker_id="w1")
        assert claimed is not None and claimed.task_id == "SRC-1"

    def test_get_task_batch_id_missing_and_empty(self, repo: TaskRepository) -> None:
        assert repo.get_task_batch_id("SRC-404") is None
        repo.create(_make_task("SRC-1"), allow_direct_create=True)
        assert repo.get_task_batch_id("SRC-1") is None
        with repo._write_tx() as conn:
            conn.execute("UPDATE tasks SET batch_id = '' WHERE task_id = 'SRC-1'")
        assert repo.get_task_batch_id("SRC-1") is None  # 空串视为无批次


class TestNewBatchId:
    def test_format_convention(self) -> None:
        bid = new_batch_id("decomp")
        assert re.fullmatch(r"decomp-\d{8}-[0-9a-f]{6}", bid), bid

    def test_origin_sanitized_and_uniqueness(self) -> None:
        a = new_batch_id("Find!ng X")
        b = new_batch_id("finding-x")
        assert a.startswith("find-ng-x-") or a.startswith("finding-x-")
        # rand6 保证连续生成不碰撞
        assert new_batch_id("mcp") != new_batch_id("mcp")

    def test_empty_origin_fallback(self) -> None:
        assert re.fullmatch(r"task-\d{8}-[0-9a-f]{6}", new_batch_id("  "))
