# [A_test] test_id=P21-CLAIMBATCH-001 | module=src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py | gate=pytest
# [BLUEPRINT] MOD-GOV-COMMIT-GATEWAY | src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py | claim_files/release_files 批量路径 P2-1 吞吐治本
# [TTL] permanent
"""GitCommitGateway claim_files/release_files 批量路径回归（P2-1 出仓战役 2026-09-16）。

背景：逐件 claim_file 每次整表重写 session registry JSON、每件再起一个 git 子进程
求基线——千件级 claim 落到分钟级且 O(N²)。治本后真实 SessionRegistry 走
claim_files_batch / release_files_batch + 一次 git diff --name-only 基线预判。

验证场景：
1. 真实 SessionRegistry → 走批量（逐件 claim_file 一次都不被调用）且返回原样路径
2. MagicMock 替身 registry → 退回逐件（鸭子探测被 mock 自动补名骗过的事故回归锚）
3. 他人已持有件在批量路径下同样被排除（不越权改写）
4. release_files 批量摘除全部持有
5. 基线捕获只对 git 判定"有 diff"的件发生（无 diff 件存空基线，等价省子进程）
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
from unittest.mock import MagicMock

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
from zephyr.security.access_control.session_concurrency import SessionRegistry


class _FakeResult:
    def __init__(self, returncode: int, stdout: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout


def _make_gw(tmp_path: Path, registry: Any, *, diff_files: list[str] | None = None) -> GitCommitGateway:
    """最小化 gateway（__new__ 绕过重量级 __init__），run_git 只应答 claim 用到的两类查询。"""
    gw = GitCommitGateway.__new__(GitCommitGateway)
    gw.project_root = tmp_path
    gw.claim_snapshots = {}
    gw.claim_heads = {}
    gw.claim_snapshots_dir = tmp_path / ".runtime" / "claim_snapshots"
    gw.registry = registry
    gw.captured: list[str] = []

    def _capture(abs_f: str) -> str:
        gw.captured.append(abs_f)
        return "DIFF-BASELINE"

    gw.capture_baseline_diff = _capture

    def _run_git(argv: list[str]) -> _FakeResult:
        joined = " ".join(argv)
        if "rev-parse HEAD" in joined:
            return _FakeResult(0, "deadbeef\n")
        if "diff HEAD --name-only" in joined:
            return _FakeResult(0, "\n".join(diff_files or []) + ("\n" if diff_files else ""))
        return _FakeResult(0, "")

    gw.run_git = _run_git
    gw.save_session_snapshot = lambda sid: None
    gw.delete_session_snapshot = lambda sid: None
    return gw


@pytest.fixture
def real_registry(tmp_path: Path) -> SessionRegistry:
    return SessionRegistry(project_root=tmp_path)


def test_claim_uses_batch_path_with_real_registry(tmp_path, real_registry) -> None:
    files = ["a.py", "b.py", "c.py"]
    for f in files:
        (tmp_path / f).write_text("x", encoding="utf-8")

    def _boom(*a, **k):
        raise AssertionError("真实 registry 下不应再逐件 claim_file")

    real_registry.claim_file = _boom  # type: ignore[method-assign]
    gw = _make_gw(tmp_path, real_registry)
    assert gw.claim_files("s1", files) == files
    assert len(real_registry.get_session("s1").held_files) == 3
    # HEAD 锚点整批一次
    assert gw.claim_heads["s1"] == "deadbeef"


def test_claim_falls_back_for_stub_registry(tmp_path) -> None:
    """MagicMock 替身不得被鸭子探测误判（批量方法名自动补出→claim 结果被判空）。"""
    stub = MagicMock()
    stub.claim_file.return_value = True
    gw = _make_gw(tmp_path, stub)
    assert gw.claim_files("s1", ["x.py", "y.py"]) == ["x.py", "y.py"]
    assert stub.claim_file.call_count == 2


def test_claim_batch_excludes_foreign_held(tmp_path, real_registry) -> None:
    (tmp_path / "taken.py").write_text("x", encoding="utf-8")
    (tmp_path / "free.py").write_text("x", encoding="utf-8")
    real_registry.claim_file("s-other", str(tmp_path / "taken.py"))
    gw = _make_gw(tmp_path, real_registry)
    claimed = gw.claim_files("s1", [str(tmp_path / "taken.py"), str(tmp_path / "free.py")])
    assert claimed == [str(tmp_path / "free.py")]
    holder = real_registry.find_session_by_file(str((tmp_path / "taken.py").resolve()))
    assert holder is not None and holder.session_id == "s-other"


def test_release_batch_clears_all_holds(tmp_path, real_registry) -> None:
    gw = _make_gw(tmp_path, real_registry)
    gw.claim_files("s1", ["a.py", "b.py"])
    assert len(real_registry.get_session("s1").held_files) == 2
    gw.release_files("s1", ["a.py", "b.py"])
    assert real_registry.get_session("s1").held_files == []
    assert "s1" not in gw.claim_heads


def test_baseline_captured_only_for_dirty_files(tmp_path, real_registry) -> None:
    """git 判定无 diff 的件直接存空基线；有 diff 的件仍逐件捕获真实基线。"""
    clean = tmp_path / "clean.py"
    dirty = tmp_path / "dirty.py"
    clean.touch()
    dirty.touch()
    gw = _make_gw(tmp_path, real_registry, diff_files=[str(dirty)])
    gw.claim_files("s1", [str(clean), str(dirty)])
    snaps = gw.claim_snapshots["s1"]
    assert len(gw.captured) == 1 and gw.captured[0].endswith("dirty.py")
    by_suffix = {Path(k).name: v for k, v in snaps.items()}
    assert by_suffix["clean.py"] == ""
    assert by_suffix["dirty.py"] == "DIFF-BASELINE"


def test_baseline_falls_back_when_git_predjudgement_unavailable(tmp_path, real_registry) -> None:
    """预判 git 不可达（rc!=0）→ 退回逐件捕获，基线语义不丢。"""
    gw = _make_gw(tmp_path, real_registry)

    def _fail(argv: list[str]) -> _FakeResult:
        return _FakeResult(128) if "diff HEAD --name-only" in " ".join(argv) else _FakeResult(0, "deadbeef\n")

    gw.run_git = _fail
    gw.claim_files("s1", ["a.py", "b.py"])
    assert len(gw.captured) == 2


def test_run_git_raising_is_swallowed_by_predjudgement(tmp_path, real_registry) -> None:
    """run_git 抛异常时预判返回 None，claim 主流程不受影响（fail-safe）。"""
    gw = _make_gw(tmp_path, real_registry)

    def _raise(argv: list[str]) -> subprocess.CompletedProcess:
        if "diff HEAD --name-only" in " ".join(argv):
            raise RuntimeError("git 崩了")
        return _FakeResult(0, "deadbeef\n")

    gw.run_git = _raise
    assert gw.claim_files("s1", [str(tmp_path / "a.py")]) == [str(tmp_path / "a.py")]
    assert len(gw.captured) == 1 and gw.captured[0].endswith("a.py")
