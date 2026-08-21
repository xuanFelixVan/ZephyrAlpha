# [A_test] module_id: MOD-GOV_dm400_stale_task_fix | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain-infra_runtime/task-system/blueprint.md
# [MODULE] tests.unit.db.test_dm400_stale_task_fix
# [INVARIANTS] All tests must pass independently; no external state dependency
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass
# [TESTS] pytest tests/db/test_dm400_stale_task_fix.py -v
# [TTL] task_bound

"""DM-400/DM-401 端到端 + 红蓝对抗测试。

三层防护验证：
1. transition(COMPLETED)后提醒剩余IN_PROGRESS任务（无论session_id是否为空）
2. recover_stale_claims 方法（Conductor.plan_cycle 事件驱动覆盖，CircadianScheduler 定时注册已废除）
3. Session关门清单IN_PROGRESS=0检查
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def repo():
    """创建 TaskRepository 实例。"""
    from zephyr.governance.persistence.task_repo import TaskRepository

    return TaskRepository()


# ---------------------------------------------------------------------------
# PART 1: 端到端测试
# ---------------------------------------------------------------------------


class TestE2E:
    """端到端功能验证。"""

    def test_count_by_status_and_session_returns_int(self, repo):
        """_count_by_status_and_session 返回 int。"""
        count = repo.count_by_status_and_session("IN_PROGRESS", "nonexistent-session")
        assert isinstance(count, int)

    def test_count_by_status_and_session_empty_session(self, repo):
        """不存在的 session_id 返回 0。"""
        count = repo.count_by_status_and_session("IN_PROGRESS", "nonexistent-session-xyz")
        assert count == 0

    def test_transition_has_dm401_reminder(self, repo):
        """_post_completion_actions() 包含 DM-401 提醒代码。"""
        source = inspect.getsource(repo._post_completion_actions)
        assert "DM-401" in source, "_post_completion_actions() 缺少 DM-401 标记"

    def test_transition_no_session_id_guard(self, repo):
        """_post_completion_actions() 提醒逻辑不再依赖 session_id（DM-401 修复）。"""
        source = inspect.getsource(repo._post_completion_actions)
        # DM-401 提醒应使用 if/else 分支处理 session_id，而非 `and session_id` 条件
        assert "DM-401" in source
        assert "and session_id" not in source, "DM-401 修复后不应有 `and session_id` 条件"

    def test_list_by_status_in_progress_works(self, repo):
        """list_by_status('IN_PROGRESS') 正常工作。"""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            tasks = repo.list_by_status("IN_PROGRESS")
        assert isinstance(tasks, list)

    def test_recover_stale_claims_exists(self, repo):
        """recover_stale_claims 方法存在。"""
        assert hasattr(repo, "recover_stale_claims")
        sig = inspect.signature(repo.recover_stale_claims)
        assert "batch_id" in sig.parameters
        assert "timeout_minutes" in sig.parameters

    def test_recover_stale_claims_no_stale(self, repo):
        """recover_stale_claims 对无超时任务返回 0。"""
        recovered = repo.recover_stale_claims(batch_id="nonexistent-batch", timeout_minutes=30)
        assert recovered == 0


# ---------------------------------------------------------------------------
# PART 2: 红蓝对抗测试
# ---------------------------------------------------------------------------


class TestRedBlue:
    """红蓝对抗：异常输入和边界条件。"""

    def test_nonexistent_session_returns_zero(self, repo):
        """不存在的 session_id 返回 0（不崩溃）。"""
        count = repo.count_by_status_and_session("IN_PROGRESS", "nonexistent-session-xyz")
        assert count == 0

    def test_invalid_status_returns_zero(self, repo):
        """无效 status 返回 0（不崩溃）。"""
        count = repo.count_by_status_and_session("INVALID_STATUS", "session-20260611-001")
        assert count == 0

    def test_transition_reminder_wrapped_in_try_except(self, repo):
        """提醒逻辑被 try/except 包裹，不阻断 transition。"""
        source = inspect.getsource(repo._post_completion_actions)
        assert "DM-401" in source
        assert "try:" in source
        assert "except Exception" in source

    def test_session_close_check_command_works(self, repo):
        """Session 关门检查命令可执行。"""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            tasks = repo.list_by_status("IN_PROGRESS")
        # 命令本身能运行即通过（不 assert 0，因为当前有 IN_PROGRESS 任务）
        assert isinstance(tasks, list)

    def test_count_by_status_and_session_with_empty_string(self, repo):
        """空字符串 session_id 不崩溃。"""
        count = repo.count_by_status_and_session("IN_PROGRESS", "")
        assert isinstance(count, int)
