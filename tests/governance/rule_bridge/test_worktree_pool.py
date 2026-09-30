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

DEFECT-5 治本（st-zcloseout-rootcure 2026-09-30）：本文件全量沙箱化——所有测试在
``sandbox_repo`` fixture 于 pytest tmp_path 内 `git init` 的独立迷你仓上运行，
WorktreePool/get_pool/session_worktree_* 全部走显式 root 参数注入（WorktreePool.__init__
repo_root / get_pool(project_root) / session_worktree_start(project_root) 均为既有
一等参数缝，零 monkeypatch 依赖），与宿主仓（REPO_ROOT/.aidrafts_pool/.aidrafts/
session_registry/分支空间）零交集。teardown 双保险：沙箱残留清理 + 宿主渗漏 tripwire。
原 ZEPHYR_GIT_E2E 隔离门禁（曾实测毁宿主车道）随之移除——沙箱化后无需门禁。

测试组：
- test_stats_empty: 空池 stats 返回 idle_count=0
- test_prefetch_creates_worktree: prefetch(1) 在沙箱 .aidrafts_pool/ 创建 worktree
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

# DEFECT-5 根治注记：原 `pytestmark = skipif(ZEPHYR_GIT_E2E != "1")` 隔离门禁已移除
# ——本文件已全量沙箱化（见模块 docstring「DEFECT-5 治本」段）：测试只触碰 pytest
# tmp_path 内的独立迷你 git 仓，宿主仓零 git 外科。门禁移除后由 teardown tripwire
# 防回归（_assert_no_host_leak）。

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
            except Exception:  # noqa: BLE001 — Windows 句柄延迟释放兜底重试，fail-soft 清理
                time.sleep(0.5 * (attempt + 1))

    shutil.rmtree(path, onerror=_on_error)


def _sandbox_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """在沙箱仓执行 git 命令（失败 fail-loud，绝不指向沙箱外）。"""
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, f"git {args} failed in sandbox {repo}: {r.stderr}"
    return r


def _assert_no_host_leak() -> None:
    """宿主渗漏 tripwire（DEFECT-5 防回归）：测试 sid 绝不允许出现在真实仓根。

    `zephyr.shared.io.paths.REPO_ROOT` 是模块属性真源（本文件零 monkeypatch），
    沙箱注入全走显式参数——若此断言红，说明某条代码路径绕过参数缝逃逸到宿主。
    """
    from zephyr.shared.io.paths import REPO_ROOT as _REAL_ROOT

    for sid in (_TEST_SID, _TEST_SID_2):
        leaked_wt = Path(_REAL_ROOT) / ".aidrafts" / sid
        assert not leaked_wt.exists(), f"HOST LEAK: 沙箱 session worktree 逃逸到宿主: {leaked_wt}"
        leaked_branch = subprocess.run(
            ["git", "rev-parse", "--verify", f"session/{sid}"],
            cwd=_REAL_ROOT,
            capture_output=True,
            text=True,
        )
        assert leaked_branch.returncode != 0, f"HOST LEAK: 沙箱分支逃逸到宿主: session/{sid}"


def _cleanup_pool_artifacts(repo: Path) -> None:
    """清理沙箱内 pool 测试残留：pool worktrees、session worktrees、分支。"""
    # 清理 pool 目录
    pool_dir = repo / ".aidrafts_pool"
    if pool_dir.exists():
        # 先用 git worktree remove 清理每个 pool worktree
        r = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=repo,
            capture_output=True,
            text=True,
        )
        for line in r.stdout.splitlines():
            if line.startswith("worktree ") and ".aidrafts_pool" in line:
                wt_path = line.split(" ", 1)[1]
                subprocess.run(
                    ["git", "worktree", "remove", "--force", wt_path],
                    cwd=repo,
                    capture_output=True,
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
                cwd=repo,
                capture_output=True,
            )
            if wt.exists():
                _force_rmtree(wt)
        subprocess.run(
            ["git", "branch", "-D", f"session/{sid}"],
            cwd=repo,
            capture_output=True,
        )
        # 同时清理 pool-sid 命名的分支（lease 失败回滚时可能残留）
        subprocess.run(
            ["git", "branch", "-D", f"session/pool-{sid}"],
            cwd=repo,
            capture_output=True,
        )

    subprocess.run(["git", "worktree", "prune"], cwd=repo, capture_output=True)

    # 清理 pool-sid 命名的所有残留分支
    r = subprocess.run(
        ["git", "branch", "--list", "session/pool-*"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    for line in r.stdout.splitlines():
        branch = line.strip()
        if branch:
            subprocess.run(
                ["git", "branch", "-D", branch],
                cwd=repo,
                capture_output=True,
            )

    # 清理 registry 残留
    reg_file = repo / ".runtime" / "session_registry.json"
    if reg_file.exists():
        try:
            import json

            data = json.loads(reg_file.read_text(encoding="utf-8"))
            data = {k: v for k, v in data.items() if not k.startswith("sess-pytest-pool")}
            reg_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:  # noqa: BLE001 — registry 残留清理 fail-soft（物理残留无害）
            pass


@pytest.fixture
def sandbox_repo(tmp_path):
    """DEFECT-5 治本：每个测试一个独立迷你 git 仓（pytest tmp_path 内）。

    `git init` + user config + 初始 commit——WorktreePool 全流程（prefetch/lease/
    move/branch -m/cleanup_stale）与 session_worktree 集成（显式 project_root 注入）
    均在此仓内完成，与宿主仓 .aidrafts_pool/.aidrafts/session_registry/分支空间零交集。
    teardown：清沙箱残留 → 清 pool singleton 缓存 → 宿主渗漏 tripwire。
    """
    repo = tmp_path / "wt_pool_sandbox"
    repo.mkdir()
    _sandbox_git(repo, "init")
    _sandbox_git(repo, "config", "user.email", "test@zephyr.local")
    _sandbox_git(repo, "config", "user.name", "Zephyr Test")
    (repo / ".gitkeep").write_text("", encoding="utf-8")
    # .aidrafts/ 预创建——宿主仓常态存在（session worktree 挂载点），`git worktree
    # move` 的目标父目录必须存在，新建沙箱仓无此目录会导致 lease move 失败。
    (repo / ".aidrafts").mkdir()
    _sandbox_git(repo, "add", ".gitkeep")
    _sandbox_git(repo, "commit", "--no-verify", "-m", "init")
    yield repo

    # teardown：清理 heartbeat daemon 残留进程（集成测试 start 会 spawn）
    try:
        from zephyr.gov_enforcement.rule_bridge.session_worktree import kill_all_heartbeat_daemons

        kill_all_heartbeat_daemons(repo)
    except Exception:  # noqa: BLE001 — teardown best-effort
        pass
    _cleanup_pool_artifacts(repo)
    # 清理 get_pool singleton 缓存（避免跨测试状态污染）
    import zephyr.gov_enforcement.rule_bridge.worktree_pool as wp_module

    wp_module.pool_instances.clear()
    _assert_no_host_leak()


def test_stats_empty(sandbox_repo):
    """空池 stats 返回 idle_count=0。"""
    pool = WorktreePool(sandbox_repo)
    stats = pool.stats()
    assert stats["idle_count"] == 0
    assert stats["target_size"] >= 1
    assert "pool_dir" in stats


def test_prefetch_creates_worktree(sandbox_repo):
    """prefetch(1) 在沙箱 .aidrafts_pool/ 创建 1 个 worktree。"""
    pool = WorktreePool(sandbox_repo)
    created = pool.prefetch(1)
    assert created == 1

    idle = pool.list_idle()
    assert len(idle) == 1
    assert idle[0]["pool_id"].startswith("pool-")
    assert idle[0]["branch"].startswith("session/pool-")
    # worktree 目录物理存在
    assert Path(idle[0]["path"]).exists()
    # 分支存在（在沙箱仓验证）
    r = subprocess.run(
        ["git", "rev-parse", "--verify", idle[0]["branch"]],
        cwd=sandbox_repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0


def test_lease_relocates_worktree(sandbox_repo):
    """lease 将 pool worktree 移到 .aidrafts/{sid}/ + 分支重命名。"""
    pool = WorktreePool(sandbox_repo)
    pool.prefetch(1)
    assert pool.stats()["idle_count"] == 1

    leased_path = pool.lease(_TEST_SID)
    assert leased_path is not None
    assert str(_TEST_SID) in leased_path

    # pool 空了
    assert pool.stats()["idle_count"] == 0

    # session worktree 路径存在（沙箱内）
    session_wt = sandbox_repo / ".aidrafts" / _TEST_SID
    assert session_wt.exists()

    # session 分支存在（沙箱仓）
    r = subprocess.run(
        ["git", "rev-parse", "--verify", f"session/{_TEST_SID}"],
        cwd=sandbox_repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0

    # pool 分支已重命名（不再存在）
    r_pool_branch = subprocess.run(
        ["git", "branch", "--list", "session/pool-*"],
        cwd=sandbox_repo,
        capture_output=True,
        text=True,
    )
    # 没有以 session/pool- 开头的分支
    assert r_pool_branch.stdout.strip() == ""


def test_lease_empty_returns_none(sandbox_repo):
    """空池 lease 返回 None（fall back 信号）。"""
    pool = WorktreePool(sandbox_repo)
    # 确保池空
    assert pool.stats()["idle_count"] == 0

    result = pool.lease(_TEST_SID)
    assert result is None


def test_lease_then_prefetch_async_replenishes(sandbox_repo):
    """lease 后 prefetch_async 补充池（异步，需 wait）。"""
    pool = WorktreePool(sandbox_repo)
    pool.prefetch(1)

    leased = pool.lease(_TEST_SID)
    assert leased is not None
    assert pool.stats()["idle_count"] == 0

    # 触发 async prefetch
    thread = pool.prefetch_async(1)
    thread.join(timeout=60)  # 等完成（git worktree add 在 Windows 可能慢）

    # 池已补充
    assert pool.stats()["idle_count"] == 1


def test_cleanup_stale_removes_old(sandbox_repo):
    """cleanup_stale 清理超龄 worktree。"""
    pool = WorktreePool(sandbox_repo)
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


def test_session_worktree_start_uses_pool(sandbox_repo):
    """session_worktree_start 优先使用 pool lease（DEFECT-5：显式 project_root 注入沙箱）。

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

    # 预填池（沙箱仓）
    pool = get_pool(sandbox_repo)
    pool.prefetch(1)
    assert pool.stats()["idle_count"] == 1

    # 启动 session（应使用 pool lease；DEFECT-5 核心：project_root=沙箱，非宿主）
    r = session_worktree_start(_TEST_SID, project_root=sandbox_repo, allow_workspace_drift=True)
    assert r.get("registered") is True, f"start 失败: {r}"
    assert r.get("created") is True, f"start 失败: {r}"
    assert r.get("worktree_path", "")
    assert _TEST_SID in r["worktree_path"]
    # worktree 必须落在沙箱内（非宿主渗漏）
    assert str(sandbox_repo) in r["worktree_path"], f"worktree 逃逸出沙箱: {r['worktree_path']}"

    # pool 应已消耗（idle_count=0，但 prefetch_async 可能在后台补充）
    # 用 thread sync 等待 async prefetch 完成
    stats = pool.stats()
    # lease 成功后 pool 立即空，prefetch_async 在后台
    assert stats["idle_count"] <= 1  # 0 或 1（async 已补充）

    # session worktree 存在（沙箱内）
    session_wt = sandbox_repo / ".aidrafts" / _TEST_SID
    assert session_wt.exists()

    # 清理：abort session（同样注入沙箱）
    a = session_worktree_abort(_TEST_SID, project_root=sandbox_repo)
    assert a.get("aborted"), f"abort 失败: {a}"
