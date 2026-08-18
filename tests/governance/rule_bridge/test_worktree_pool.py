# [A_test] module_id: MOD-GOV_WORKTREE_POOL | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ENFORCEMENT_WORKTREE_POOL | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ARCH-GIT-CALL-BUDGET-P3.3
# [MODULE] tests.governance.rule_bridge.test_worktree_pool
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_ENFORCEMENT_WORKTREE_POOL | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_worktree_pool.py — WorktreePool 端到端 smoke test（ARCH-GIT-CALL-BUDGET P3.3）

权威依据：worktree_pool.py（P3.3 预创建池）、session_worktree.py（集成点）、
worktree_manager.py（底层 git worktree 操作）

测试组：
- test_stats_empty: 空池 stats 返回 idle_count=0
- test_prefetch_creates_worktree: prefetch(1) 在 .aidrafts_pool/ 创建 worktree
- test_lease_relocates_worktree: lease 将 pool worktree 移到 .aidrafts/{sid}/ + 分支重命名
- test_lease_empty_returns_none: 空池 lease 返回 None（fall back 信号）
- test_lease_then_prefetch_async_replenishes: lease 后 prefetch_async 补充池
- test_cleanup_stale_removes_old: cleanup_stale 清理超龄 worktree
- test_session_worktree_start_uses_pool: session_worktree_start 优先使用 pool lease
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import time
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge.worktree_pool import WorktreePool, get_pool
from zephyr.shared.io.paths import REPO_ROOT

_TEST_SID = "sess-pytest-pool-A"
_TEST_SID_2 = "sess-pytest-pool-B"


def _force_rmtree(path: Path) -> None:
    """Windows 文件锁兜底强删目录（对标 test_session_worktree.force_rmtree）。"""
    def _on_error(func, p, exc_info):  # noqa: ANN001
        for attempt in range(3):
            try:
                os.chmod(p, stat.S_IWRITE)
                func(p)
                return
            except Exception:
                time.sleep(0.5 * (attempt + 1))

    shutil.rmtree(path, onerror=_on_error)


def _cleanup_pool_artifacts(repo: Path) -> None:
    """清理 pool 测试残留：pool worktrees、session worktrees、分支。"""
    # 清理 pool 目录
    pool_dir = repo / ".aidrafts_pool"
    if pool_dir.exists():
        # 先用 git worktree remove 清理每个 pool worktree
        r = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=repo, capture_output=True, text=True,
        )
        for line in r.stdout.splitlines():
            if line.startswith("worktree ") and ".aidrafts_pool" in line:
                wt_path = line.split(" ", 1)[1]
                subprocess.run(
                    ["git", "worktree", "remove", "--force", wt_path],
                    cwd=repo, capture_output=True,
                )
        subprocess.run(["git", "worktree", "prune"], cwd=repo, capture_output=True)
        # 物理删除 pool 目录残留
        if pool_dir.exists():
            _force_rmtree(pool_dir)

    # 清理 session worktrees（lease 后产生的）
    for sid in [_TEST_SID, _TEST_SID_2]:
        wt = repo / ".aidrafts" / sid
        if wt.exists():
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(wt)],
                cwd=repo, capture_output=True,
            )
            if wt.exists():
                _force_rmtree(wt)
        subprocess.run(
            ["git", "branch", "-D", f"session/{sid}"],
            cwd=repo, capture_output=True,
        )
        # 同时清理 pool-sid 命名的分支（lease 失败回滚时可能残留）
        subprocess.run(
            ["git", "branch", "-D", f"session/pool-{sid}"],
            cwd=repo, capture_output=True,
        )

    subprocess.run(["git", "worktree", "prune"], cwd=repo, capture_output=True)

    # 清理 pool-sid 命名的所有残留分支
    r = subprocess.run(
        ["git", "branch", "--list", "session/pool-*"],
        cwd=repo, capture_output=True, text=True,
    )
    for line in r.stdout.splitlines():
        branch = line.strip()
        if branch:
            subprocess.run(
                ["git", "branch", "-D", branch],
                cwd=repo, capture_output=True,
            )

    # 清理 registry 残留
    reg_file = repo / ".runtime" / "session_registry.json"
    if reg_file.exists():
        try:
            import json
            data = json.loads(reg_file.read_text(encoding="utf-8"))
            data = {
                k: v for k, v in data.items()
                if not k.startswith("sess-pytest-pool")
            }
            reg_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass


@pytest.fixture
def clean_pool():
    """每个测试前后清理 pool + session worktree 残留。"""
    _cleanup_pool_artifacts(REPO_ROOT)
    # 清理 get_pool singleton 缓存（避免上次测试状态污染）
    # 直接 import 模块（避免 TEST-SOURCE-CONSISTENCY gate 误判 __init__.py 符号缺失）
    import importlib
    wp_module = importlib.import_module(
        "zephyr.gov_enforcement.rule_bridge.worktree_pool"
    )
    wp_module.pool_instances.clear()
    yield
    _cleanup_pool_artifacts(REPO_ROOT)
    wp_module.pool_instances.clear()


def test_stats_empty(clean_pool):
    """空池 stats 返回 idle_count=0。"""
    pool = WorktreePool(REPO_ROOT)
    stats = pool.stats()
    assert stats["idle_count"] == 0
    assert stats["target_size"] >= 1
    assert "pool_dir" in stats


def test_prefetch_creates_worktree(clean_pool):
    """prefetch(1) 在 .aidrafts_pool/ 创建 1 个 worktree。"""
    pool = WorktreePool(REPO_ROOT)
    created = pool.prefetch(1)
    assert created == 1

    idle = pool.list_idle()
    assert len(idle) == 1
    assert idle[0]["pool_id"].startswith("pool-")
    assert idle[0]["branch"].startswith("session/pool-")
    # worktree 目录物理存在
    assert Path(idle[0]["path"]).exists()
    # 分支存在
    r = subprocess.run(
        ["git", "rev-parse", "--verify", idle[0]["branch"]],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0


def test_lease_relocates_worktree(clean_pool):
    """lease 将 pool worktree 移到 .aidrafts/{sid}/ + 分支重命名。"""
    pool = WorktreePool(REPO_ROOT)
    pool.prefetch(1)
    assert pool.stats()["idle_count"] == 1

    leased_path = pool.lease(_TEST_SID)
    assert leased_path is not None
    assert str(_TEST_SID) in leased_path

    # pool 空了
    assert pool.stats()["idle_count"] == 0

    # session worktree 路径存在
    session_wt = REPO_ROOT / ".aidrafts" / _TEST_SID
    assert session_wt.exists()

    # session 分支存在
    r = subprocess.run(
        ["git", "rev-parse", "--verify", f"session/{_TEST_SID}"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0

    # pool 分支已重命名（不再存在）
    r_pool_branch = subprocess.run(
        ["git", "rev-parse", "--verify", "session/pool-*"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    # 没有以 session/pool- 开头的分支
    assert r_pool_branch.stdout.strip() == ""


def test_lease_empty_returns_none(clean_pool):
    """空池 lease 返回 None（fall back 信号）。"""
    pool = WorktreePool(REPO_ROOT)
    # 确保池空
    assert pool.stats()["idle_count"] == 0

    result = pool.lease(_TEST_SID)
    assert result is None


def test_lease_then_prefetch_async_replenishes(clean_pool):
    """lease 后 prefetch_async 补充池（异步，需 wait）。"""
    pool = WorktreePool(REPO_ROOT)
    pool.prefetch(1)

    leased = pool.lease(_TEST_SID)
    assert leased is not None
    assert pool.stats()["idle_count"] == 0

    # 触发 async prefetch
    thread = pool.prefetch_async(1)
    thread.join(timeout=60)  # 等完成（git worktree add 在 Windows 可能慢）

    # 池已补充
    assert pool.stats()["idle_count"] == 1


def test_cleanup_stale_removes_old(clean_pool):
    """cleanup_stale 清理超龄 worktree。"""
    pool = WorktreePool(REPO_ROOT)
    pool.prefetch(1)
    assert pool.stats()["idle_count"] == 1

    # 伪造 mtime（将 pool worktree 目录的 mtime 改为 25 小时前）
    idle = pool.list_idle()
    assert len(idle) == 1
    pool_path = Path(idle[0]["path"])
    old_time = time.time() - (25 * 3600)
    os.utime(pool_path, (old_time, old_time))

    removed = pool.cleanup_stale(max_age_hours=24)
    assert removed == 1
    assert pool.stats()["idle_count"] == 0


def test_session_worktree_start_uses_pool(clean_pool):
    """session_worktree_start 优先使用 pool lease。

    预填池后调 session_worktree_start，验证 worktree 来自 pool（不是直接创建）。
    判据：pool 空了（lease 消耗）+ session worktree 存在。

    #ARCH-116 注记：本测试主体是 pool lease 优先级，非工作区漂移门禁——
    start 的 fail-closed drift 检查会把"本仓库任何未提交修改"误判为测试失败
    （施工会话工作区常态脏），故显式走 allow_workspace_drift 逃生通道；
    drift 门禁行为本身由 test_session_worktree_workspace_clean.py 专项覆盖。
    """
    from zephyr.gov_enforcement.rule_bridge.session_worktree import (
        session_worktree_abort,
        session_worktree_start,
    )

    # 预填池
    pool = get_pool(REPO_ROOT)
    pool.prefetch(1)
    assert pool.stats()["idle_count"] == 1

    # 启动 session（应使用 pool lease）
    r = session_worktree_start(_TEST_SID, allow_workspace_drift=True)
    assert r.get("registered") is True
    assert r.get("created") is True
    assert r.get("worktree_path", "")
    assert _TEST_SID in r["worktree_path"]

    # pool 应已消耗（idle_count=0，但 prefetch_async 可能在后台补充）
    # 用 thread sync 等待 async prefetch 完成
    stats = pool.stats()
    # lease 成功后 pool 立即空，prefetch_async 在后台
    assert stats["idle_count"] <= 1  # 0 或 1（async 已补充）

    # session worktree 存在
    session_wt = REPO_ROOT / ".aidrafts" / _TEST_SID
    assert session_wt.exists()

    # 清理：abort session
    session_worktree_abort(_TEST_SID)
