# [MODULE] tests.scripts.test_session_worktree_create_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] scripts.session_worktree (create 前置闸), pytest.MonkeyPatch
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 全部 git/盘操作在 tmp 仓；阈值两侧/停用降级/死车道家系复用拒绝/无关前缀放行；
#              不跑 cmd_create 成功路径（防测试拉起 heartbeat daemon 常驻）
# [STABILITY] volatile
# [SAFETY] L
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_session_worktree_create_gate.py — D1 车道创建前置闸单测（st-diskp0-20261015）。

测试组:
- test_disk_floor_threshold_both_sides: 剩余 <min_free_gib 拒绝 / ≥ 通过（阈值两侧）
- test_disk_floor_disabled_flag_degrades: enabled:false → 降级放行（回滚通道实测）
- test_create_refuses_below_floor: cmd_create 在地板下返回 1 且零 worktree 落盘
- test_reuse_dead_sibling_refuses_fission: 同岗位死车道存在时 _find_reusable_dead_lanes 命中
- test_unrelated_prefix_not_family: 无关前缀不入家系（不误伤）
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "session_worktree.py"


def _load_module(repo: Path, monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("session_worktree_create_gate_under_test", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "REPO_ROOT", repo)
    monkeypatch.setattr(mod, "WORKTREE_ROOT", repo / ".worktrees")
    return mod


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


@pytest.fixture()
def tmp_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    assert _git(repo, "init").returncode == 0
    _git(repo, "config", "user.email", "test@zephyr.local")
    _git(repo, "config", "user.name", "Zephyr Test")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "init")
    _git(repo, "branch", "-m", "dev")
    mod = _load_module(repo, monkeypatch)
    return mod, repo


def _write_flags(repo: Path, *, enabled: bool = True, min_free_gib: float = 15.0) -> None:
    cfg = repo / "config" / "flags.yaml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(
        f"flags:\n  disk_floor:\n    enabled: {str(enabled).lower()}\n    min_free_gib: {min_free_gib}\n",
        encoding="utf-8",
    )


class _FakeUsage:
    def __init__(self, free_bytes: int) -> None:
        self.free = free_bytes
        self.total = free_bytes * 2
        self.used = free_bytes


def test_disk_floor_threshold_both_sides(tmp_repo, monkeypatch):
    """阈值两侧：<15GiB 拒绝（含清障指引），≥15GiB 通过。"""
    mod, repo = tmp_repo
    _write_flags(repo, min_free_gib=15.0)
    below = 14 * 1024**3
    above = 16 * 1024**3
    monkeypatch.setattr(shutil, "disk_usage", lambda p: _FakeUsage(below))
    ok, msg = mod._check_disk_floor(repo)
    assert not ok, "低于地板必须拒绝"
    assert "拒绝创建新车道" in msg and "cleanup_runtime_tmp_residue" in msg, f"拒绝消息缺清障指引: {msg!r}"
    monkeypatch.setattr(shutil, "disk_usage", lambda p: _FakeUsage(above))
    ok2, msg2 = mod._check_disk_floor(repo)
    assert ok2, "高于地板必须放行"
    assert "PASS" in msg2


def test_disk_floor_disabled_flag_degrades(tmp_repo, monkeypatch):
    """enabled:false → 降级放行（即使剩余为 0）——回滚通道实测。"""
    mod, repo = tmp_repo
    _write_flags(repo, enabled=False, min_free_gib=15.0)
    monkeypatch.setattr(shutil, "disk_usage", lambda p: _FakeUsage(0))
    ok, msg = mod._check_disk_floor(repo)
    assert ok and "降级" in msg


def test_create_refuses_below_floor(tmp_repo, monkeypatch):
    """cmd_create 在地板下返回 1 且不落任何 worktree。"""
    mod, repo = tmp_repo
    _write_flags(repo, min_free_gib=10**9)  # 巨大地板=必拒
    import argparse

    rc = mod.cmd_create(argparse.Namespace(session_id="st-x", task_id="t"))
    assert rc == 1
    assert not (repo / ".worktrees" / "st-x").exists()


def test_reuse_dead_sibling_refuses_fission(tmp_repo):
    """同岗位死车道存在 → _find_reusable_dead_lanes 命中（判活与 archive 同源降级判死）。"""
    mod, repo = tmp_repo
    base = "st-job"
    wt = repo / ".worktrees" / base
    r = _git(repo, "worktree", "add", str(wt), "-b", f"session/{base}")
    assert r.returncode == 0, r.stderr
    # 死判：tmp 仓无 SessionRegistry 记录/无新鲜锁 → 降级判死（与 _check_archive_target_dead 同源）
    dead = mod._find_reusable_dead_lanes(f"{base}-02")
    assert len(dead) == 1 and dead[0]["sid"] == base, f"同岗位死车道应命中: {dead}"
    # 家系反向：新建本名 base 时也应看到 -02 死兄弟（先造一棵）
    wt2 = repo / ".worktrees" / f"{base}-02"
    r2 = _git(repo, "worktree", "add", str(wt2), "-b", f"session/{base}-02")
    assert r2.returncode == 0, r2.stderr
    dead2 = mod._find_reusable_dead_lanes(f"{base}-03")
    assert {d["sid"] for d in dead2} == {base, f"{base}-02"}, f"家系两棵死车道都应命中: {dead2}"


def test_unrelated_prefix_not_family(tmp_repo):
    """无关前缀不入家系：st-other 不因 st-job 死车道被拒。"""
    mod, repo = tmp_repo
    wt = repo / ".worktrees" / "st-job"
    assert _git(repo, "worktree", "add", str(wt), "-b", "session/st-job").returncode == 0
    assert mod._find_reusable_dead_lanes("st-other") == []
    # 日期尾不误切：-20261015 是 8 位数字，不匹配 2-3 位序号
    assert mod._lane_base("st-prevw-20261015") == "st-prevw-20261015"
    assert mod._lane_base("st-job-02") == "st-job"
