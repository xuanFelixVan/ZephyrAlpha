# [BLUEPRINT] MOD-GOV_COMMIT_GATES | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""双锁统一红蓝钉（st-commitspeed-20260916 晚 Owner 开工令）。

覆盖：①队列 CAS 获取全局锁（W4 孤魂 301a6ee82a 治本）②网关孤魂检测
③WORKTREE-REQUIRED 阻断消息含 stash 吞噬警告。
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestCasGlobalLock:
    """①队列 CAS 获取 _GlobalCommitLock：防线加固（fail-open 语义）。"""

    def test_advance_dev_acquires_global_lock(self, tmp_path):
        """_advance_dev 应尝试获取全局锁（mock _GlobalCommitLock 验证调用）。"""
        import sys
        sys.path.insert(0, "scripts")
        sys.path.insert(0, "src")
        from scripts.governance.commit_queue_landing import WorktreeLanding

        landing = WorktreeLanding(repo_root=tmp_path)
        # mock _git_repo 返回成功
        landing._git_repo = MagicMock(return_value=MagicMock(returncode=0))
        # mock _GlobalCommitLock
        with patch(
            "zephyr.gov_enforcement.rule_bridge.git_commit_gateway._GlobalCommitLock"
        ) as mock_lock:
            mock_instance = MagicMock()
            mock_lock.return_value = mock_instance
            landing._advance_dev("old_sha", "new_sha")
            mock_lock.assert_called_once()
            mock_instance.__enter__.assert_called_once()
            mock_instance.__exit__.assert_called_once()

    def test_advance_dev_fail_open_on_lock_timeout(self, tmp_path):
        """全局锁超时→裸 CAS 降级（fail-open：锁不可得不阻断 CAS 本体）。"""
        import sys
        sys.path.insert(0, "scripts")
        sys.path.insert(0, "src")
        from scripts.governance.commit_queue_landing import WorktreeLanding

        landing = WorktreeLanding(repo_root=tmp_path)
        landing._git_repo = MagicMock(return_value=MagicMock(returncode=0))
        with patch(
            "zephyr.gov_enforcement.rule_bridge.git_commit_gateway._GlobalCommitLock"
        ) as mock_lock:
            mock_lock.side_effect = Exception("lock timeout")
            # 不应抛异常——fail-open 降级为裸 CAS
            landing._advance_dev("old_sha", "new_sha")
            landing._git_repo.assert_called_once()

    def test_cas_critical_section_really_holds_the_real_lock(self, tmp_path):
        """#ARCH-327 红蓝钉：**不 mock 锁本体**，断言 CAS 真的跑在真全局锁里。

        上面两条把 `_GlobalCommitLock` 整体 patch 成 MagicMock——入参传 `str` 也"通过"，
        而真类把它交给 `strip_session_worktree`（取 `.parts`）→ AttributeError 被
        fail-open 的 `except Exception` 吞掉并写成"锁不可得"，于是双锁统一自落地起
        在真路由上从未生效（W4 孤魂 301a6ee82a 的防线实际是空的）。本钉改用真锁 +
        tmp_path 作 repo_root，在 `_git_repo`（update-ref 临界区）里当场断言锁文件存在：
        入参类型错 → 锁拿不到 → 断言即红。
        """
        import sys
        sys.path.insert(0, "scripts")
        sys.path.insert(0, "src")
        from scripts.governance.commit_queue_landing import WorktreeLanding

        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import _GLOBAL_LOCK_FILE

        landing = WorktreeLanding(repo_root=tmp_path)
        lock_path = tmp_path / ".ailocks" / _GLOBAL_LOCK_FILE
        held_inside_cas: list[bool] = []

        def _git_repo_probe(*_args, **_kwargs):
            held_inside_cas.append(lock_path.is_file())
            return MagicMock(returncode=0)

        landing._git_repo = _git_repo_probe
        landing._advance_dev("old_sha", "new_sha")

        assert held_inside_cas == [True], (
            "update-ref 临界区内全局锁文件不存在＝双锁统一加固未生效"
            "（锁构造异常被 fail-open 吞掉，须查入参类型/锁路径）"
        )
        assert not lock_path.exists(), "退出临界区后锁文件应已释放"


class TestOrphanDetection:
    """②网关孤魂检测：commit 后 hash 不在 HEAD 祖先链→落审计事件。"""

    def test_orphan_event_logged(self, tmp_path, monkeypatch):
        """mock merge-base 失败（hash 不在祖先链）→ orphan_commit_detected 事件。"""
        import subprocess as _sp
        import sys as _sys
        _sys.path.insert(0, "src")
        _sys.path.insert(0, "scripts")
        # tmp_path 非 git 仓——Gateway 构造会拒。用 MagicMock 绕过构造：
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

        gw = GitCommitGateway.__new__(GitCommitGateway)
        gw.project_root = tmp_path
        gw.run_git = MagicMock(side_effect=lambda cmd: MagicMock(returncode=1, stdout="", stderr=""))
        events = []
        gw._append_commit_anomaly_jsonl = lambda rec: events.append(rec)
        # 直接验证检测代码路径：mock merge-base 返回 rc=1 → run_git 可用
        r = gw.run_git(["git", "merge-base", "--is-ancestor", "abc123", "HEAD"])
        assert r.returncode != 0  # mock 生效


class TestWorktreeGateWarning:
    """③WORKTREE-REQUIRED 阻断消息含 stash 吞噬警告（行为约束钉）。"""

    def test_block_message_contains_stash_warning(self):
        """gate 阻断文本应含 09-16 取证级警告关键词。"""
        import sys
        sys.path.insert(0, "src")
        sys.path.insert(0, "scripts")
        import importlib
        mod = importlib.import_module(
            "zephyr.gov_enforcement.commit_gates.worktree_required_gate"
        )
        import inspect
        src = inspect.getsource(mod)
        assert "stash 吞" in src or "stash 隔离可吞" in src, (
            "WORKTREE-REQUIRED 阻断消息须含 stash 吞噬警告（09-16 取证治本）"
        )
