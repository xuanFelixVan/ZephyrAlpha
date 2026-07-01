# [A_test] module_id: SRC-TST-2040 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-session_worktree | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] tests.governance.rule_enforcement.test_session_worktree
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_session_worktree.py — worktree 物理隔离端到端测试（FP-ISO.4C，2026-07-01 治本）

权威依据：session_worktree.py（FP-ISO.4C）、worktree_manager.py（底层引擎）、
validate_commit_gateway.py（GATE-COMMIT-GW worktree 放行）

测试组：
- test_two_sessions_separate_worktrees: 两 session 各建独立 worktree，路径不同
- test_worktree_commit_isolation: worktree 内 commit 不影响主工作区
- test_worktree_mutual_isolation: A/B worktree 互不干扰
- test_worktree_merge_back: merge 回主分支后主工作区出现改动
- test_worktree_abort_discards: abort 丢弃修改并清理 worktree
- test_end_to_end_lifecycle: 完整生命周期（建→commit→merge→abort→清理）
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import time
from pathlib import Path

import pytest

from zephyr.governance.rule_bridge.session_worktree import (
    session_worktree_abort,
    session_worktree_commit,
    session_worktree_merge,
    session_worktree_start,
    session_worktree_status,
)
from zephyr.shared.io.paths import REPO_ROOT

_TEST_SIDS = ["sess-pytest-A", "sess-pytest-B"]
_TEST_FILE_A = "tests/governance/rule_enforcement/_wt_marker_a.json"
_TEST_FILE_B = "tests/governance/rule_enforcement/_wt_marker_b.json"


def _force_rmtree(path: Path) -> None:
    """Windows 文件锁兜底强删目录。

    ``shutil.rmtree`` 默认遇到 [WinError 32]（另一个程序正在使用此文件）直接失败。
    Windows 上 git/subprocess 刚退出时句柄延迟释放（0.3-2s）。本 helper 用
    ``onerror`` 回调：清除只读位 → sleep 500ms 等句柄释放 → 重试，最多 3 轮。
    最终静默忽略（物理残留无害，git 元数据才是真源，下轮 fixture 会再试）。
    """
    def _on_error(func, p, exc_info):  # noqa: ANN001
        for attempt in range(3):
            try:
                os.chmod(p, stat.S_IWRITE)
                func(p)
                return
            except Exception:
                time.sleep(0.5 * (attempt + 1))  # 0.5s, 1.0s, 1.5s
        # 3 轮后放弃，残留由下轮 fixture 或 create_session_worktree 的 _force_rmtree 处理

    shutil.rmtree(path, onerror=_on_error)


def _cleanup_artifacts(repo: Path, orig_head: str | None = None) -> None:
    """清理测试残留：worktree、分支、registry 记录、marker 文件、test commit。

    Args:
        repo: 仓库根目录。
        orig_head: 测试前的 HEAD SHA。提供时用 ``git reset --soft`` 回退测试 commit
            （保留工作区未提交改动，避免 ``--hard`` 误伤 worktree_manager.py 等修复）。
    """
    for sid in _TEST_SIDS:
        wt = repo / ".aidrafts" / sid
        if wt.exists():
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(wt)],
                cwd=repo, capture_output=True,
            )
            # Windows 文件锁兜底：git worktree remove --force 可能因 [WinError 32]
            # （.gitignore/index 等句柄延迟释放或防病毒扫描占用）失败。
            # 用 _force_rmtree（onerror 清除只读位 + sleep 重试）强删物理目录，
            # 再用 git worktree prune 清理 git 元数据残留。
            if wt.exists():
                _force_rmtree(wt)
        subprocess.run(
            ["git", "branch", "-D", f"session/{sid}"],
            cwd=repo, capture_output=True,
        )
    subprocess.run(["git", "worktree", "prune"], cwd=repo, capture_output=True)

    # 清理 registry 残留
    reg_file = repo / ".runtime" / "session_registry.json"
    if reg_file.exists():
        try:
            data = json.loads(reg_file.read_text(encoding="utf-8"))
            data = {k: v for k, v in data.items() if not k.startswith("sess-pytest")}
            reg_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    # 回退测试产生的 commit（--soft 保留工作区，再 unstage + 删 marker 文件）
    if orig_head:
        subprocess.run(["git", "reset", "--soft", orig_head], cwd=repo, capture_output=True)
        subprocess.run(
            ["git", "reset", "HEAD", "--"] + [_TEST_FILE_A, _TEST_FILE_B],
            cwd=repo, capture_output=True,
        )

    # 清理 marker 文件（主工作区，merge 后可能残留）
    for f in [_TEST_FILE_A, _TEST_FILE_B]:
        p = repo / f
        if p.exists():
            p.unlink()


@pytest.fixture(autouse=True)
def _clean_worktree_env():
    """每个测试前后自动清理 worktree 残留，保证隔离。

    保存测试前 HEAD，测试后用 ``--soft`` 回退（不用 ``--hard``，避免误伤
    worktree_manager.py / validate_commit_gateway.py 等未提交修复）。
    """
    orig_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True
    ).stdout.strip()
    _cleanup_artifacts(REPO_ROOT)
    yield
    _cleanup_artifacts(REPO_ROOT, orig_head=orig_head)


def test_two_sessions_separate_worktrees():
    """两 session 各建 worktree，路径不同且目录存在。"""
    rA = session_worktree_start("sess-pytest-A")
    rB = session_worktree_start("sess-pytest-B")

    assert rA.get("created") or rA.get("registered"), f"A start 失败: {rA}"
    assert rB.get("created") or rB.get("registered"), f"B start 失败: {rB}"
    assert rA["worktree_path"] != rB["worktree_path"], "两 worktree 路径相同"
    assert Path(rA["worktree_path"]).exists(), f"A worktree 目录不存在: {rA['worktree_path']}"
    assert Path(rB["worktree_path"]).exists(), f"B worktree 目录不存在: {rB['worktree_path']}"


def test_worktree_commit_isolation():
    """worktree 内 commit 不影响主工作区（Mode A+B 防护验证）。"""
    rA = session_worktree_start("sess-pytest-A")
    wtA = Path(rA["worktree_path"])

    # 在 worktree 内写文件 + commit
    marker = wtA / _TEST_FILE_A
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text('{"session": "A", "marker": true}\n', encoding="utf-8")

    cA = session_worktree_commit(
        "sess-pytest-A",
        files=[_TEST_FILE_A],
        message="test: session A commit in worktree",
    )
    assert cA["status"] == "OK", f"A commit 失败: {cA}"
    assert cA["commit_hash"], "A commit_hash 为空"

    # 主工作区不应有该文件（物理隔离）
    main_marker = REPO_ROOT / _TEST_FILE_A
    assert not main_marker.exists(), "主工作区出现了 A 的文件！隔离失败"


def test_worktree_mutual_isolation():
    """A/B worktree 互不干扰（各自 commit 不影响对方）。"""
    rA = session_worktree_start("sess-pytest-A")
    assert rA.get("worktree_path"), f"A start 失败: {rA}"
    rB = session_worktree_start("sess-pytest-B")
    assert rB.get("worktree_path"), f"B start 失败: {rB}"
    wtA = Path(rA["worktree_path"])
    wtB = Path(rB["worktree_path"])

    # A 写文件 a + commit
    fa = wtA / _TEST_FILE_A
    fa.parent.mkdir(parents=True, exist_ok=True)
    fa.write_text('{"session": "A"}\n', encoding="utf-8")
    cA = session_worktree_commit("sess-pytest-A", files=[_TEST_FILE_A], message="test: A")
    assert cA["status"] == "OK", f"A commit 失败: {cA}"

    # B 写文件 b + commit
    fb = wtB / _TEST_FILE_B
    fb.parent.mkdir(parents=True, exist_ok=True)
    fb.write_text('{"session": "B"}\n', encoding="utf-8")
    cB = session_worktree_commit("sess-pytest-B", files=[_TEST_FILE_B], message="test: B")
    assert cB["status"] == "OK", f"B commit 失败: {cB}"

    # B worktree 不应有 A 的文件，反之亦然
    assert not (wtB / _TEST_FILE_A).exists(), "B worktree 出现了 A 的文件！隔离失败"
    assert not (wtA / _TEST_FILE_B).exists(), "A worktree 出现了 B 的文件！隔离失败"


def test_worktree_merge_back():
    """merge 回主分支后主工作区出现 A 的改动。"""
    rA = session_worktree_start("sess-pytest-A")
    wtA = Path(rA["worktree_path"])

    # 在 worktree 内写文件 + commit
    marker = wtA / _TEST_FILE_A
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text('{"session": "A"}\n', encoding="utf-8")
    session_worktree_commit("sess-pytest-A", files=[_TEST_FILE_A], message="test: A")

    # merge 回主分支
    mA = session_worktree_merge("sess-pytest-A")
    assert mA.get("merged"), f"A merge 失败: {mA}"

    # 主工作区应出现 A 的文件
    main_marker = REPO_ROOT / _TEST_FILE_A
    assert main_marker.exists(), "merge 后主工作区没有 A 的文件"
    # cleanup 由 fixture 处理（--soft 回退 + 删文件）


def test_worktree_abort_discards():
    """abort 丢弃修改并清理 worktree（Mode D 防护验证）。"""
    rB = session_worktree_start("sess-pytest-B")
    wtB = Path(rB["worktree_path"])

    # 在 worktree 内写文件（不 commit）
    marker = wtB / _TEST_FILE_B
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text('{"session": "B", "uncommitted": true}\n', encoding="utf-8")

    # abort
    aB = session_worktree_abort("sess-pytest-B")
    assert aB.get("aborted"), f"B abort 失败: {aB}"

    # worktree 应已从 git 清理（git 语义；物理目录可能因 Windows 文件锁残留，
    # 无害——下次 start 会用 _force_rmtree 清理后重建）。
    sB = session_worktree_status("sess-pytest-B")
    assert not sB["exists"], f"abort 后 git 仍认 worktree: {sB}"

    # 主工作区不应有 B 的文件
    assert not (REPO_ROOT / _TEST_FILE_B).exists(), "主工作区不应有 B 的文件"


def test_end_to_end_lifecycle():
    """完整生命周期：建 worktree → commit → 互不干扰 → merge → abort → 验证最终状态。"""
    sidA, sidB = "sess-pytest-A", "sess-pytest-B"

    # 1. 两 session 各建 worktree
    rA = session_worktree_start(sidA)
    rB = session_worktree_start(sidB)
    wtA = Path(rA["worktree_path"])
    wtB = Path(rB["worktree_path"])
    assert rA["worktree_path"] != rB["worktree_path"]

    # 2. session A 在 worktree 内 commit
    fa = wtA / _TEST_FILE_A
    fa.parent.mkdir(parents=True, exist_ok=True)
    fa.write_text('{"session": "A"}\n', encoding="utf-8")
    cA = session_worktree_commit(sidA, files=[_TEST_FILE_A], message="test: A e2e")
    assert cA["status"] == "OK", f"A commit 失败: {cA}"

    # 3. 主工作区不受 A 的 commit 影响
    assert not (REPO_ROOT / _TEST_FILE_A).exists(), "主工作区出现 A 的文件！隔离失败"

    # 4. session B 在 worktree 内 commit
    fb = wtB / _TEST_FILE_B
    fb.parent.mkdir(parents=True, exist_ok=True)
    fb.write_text('{"session": "B"}\n', encoding="utf-8")
    cB = session_worktree_commit(sidB, files=[_TEST_FILE_B], message="test: B e2e")
    assert cB["status"] == "OK", f"B commit 失败: {cB}"

    # 5. A/B worktree 互不干扰
    assert not (wtB / _TEST_FILE_A).exists(), "B worktree 出现 A 的文件"
    assert not (wtA / _TEST_FILE_B).exists(), "A worktree 出现 B 的文件"

    # 6. merge session A 回主分支
    mA = session_worktree_merge(sidA)
    assert mA.get("merged"), f"A merge 失败: {mA}"
    assert (REPO_ROOT / _TEST_FILE_A).exists(), "merge 后主工作区没有 A 的文件"

    # 7. abort session B
    aB = session_worktree_abort(sidB)
    assert aB.get("aborted"), f"B abort 失败: {aB}"
    # git 语义验证（物理目录可能因 Windows 文件锁残留，无害）
    sB = session_worktree_status(sidB)
    assert not sB["exists"], f"abort 后 git 仍认 B worktree: {sB}"

    # 8. 主工作区只有 A 的改动（B 被丢弃）
    assert (REPO_ROOT / _TEST_FILE_A).exists(), "主工作区应有 A 的文件"
    assert not (REPO_ROOT / _TEST_FILE_B).exists(), "主工作区不应有 B 的文件"
    # cleanup 由 fixture 处理（--soft 回退 + 删文件）
