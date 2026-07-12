# [A_test] module_id: SRC-TST-2108 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-session_worktree | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] tests.governance.rule_bridge.test_session_worktree
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
- test_worktree_commit_file_deletion: 文件删除同步——主工作区删除 tracked 文件，worktree commit 同步删除
- test_worktree_mutual_isolation: A/B worktree 互不干扰
- test_worktree_merge_back: merge 回主分支后主工作区出现改动
- test_worktree_abort_discards: abort 丢弃修改并清理 worktree
- test_worktree_abort_cleans_main_workdir: abort with files 清理主工作区残留（君子协定模式）
- test_worktree_commit_held_overlap_blocks: HELD-OVERLAP 硬阻断——A commit 后 B commit 同文件被阻断
- test_worktree_commit_allow_overlap: allow_overlap=True 逃生通道放行
- test_worktree_merge_releases_claims: merge 后 unregister 自动释放 claim，其他 session 可 commit
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

from zephyr.gov_enforcement.rule_bridge.session_worktree import (
    session_worktree_abort,
    session_worktree_commit,
    session_worktree_merge,
    session_worktree_start,
    session_worktree_status,
)
from zephyr.shared.io.paths import REPO_ROOT

_TEST_SIDS = ["sess-pytest-A", "sess-pytest-B"]
_TEST_FILE_A = "tests/governance/rule_bridge/_wt_marker_a.json"
_TEST_FILE_B = "tests/governance/rule_bridge/_wt_marker_b.json"


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


@pytest.fixture(scope="module")
def _isolated_repo(tmp_path_factory):
    """创建独立临时 git 仓库，测试完全隔离不污染主工作区。

    临时仓库初始化一个空 commit（作为 worktree 创建分支的 base），
    所有测试在此仓库上创建/删除 worktree、commit、merge，与主仓库零交集。
    根因：原 fixture 在主仓库跑测试，git merge/reset 污染主工作区导致代码丢失。
    """
    repo = tmp_path_factory.mktemp("wt_test_repo")
    subprocess.run(["git", "init"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@zephyr.local"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Zephyr Test"], cwd=repo, capture_output=True)
    # 初始 commit（worktree 基于当前 HEAD 创建分支，无 commit 则 HEAD 不存在）
    (repo / ".gitkeep").write_text("", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, capture_output=True)
    return repo


@pytest.fixture(autouse=True)
def _clean_worktree_env(_isolated_repo, monkeypatch):
    """每个测试用临时仓库，monkeypatch REPO_ROOT 指向它，隔离主工作区。

    patch session_worktree 模块 + 测试模块的 REPO_ROOT → 临时仓库；
    测试前清理残留，测试后清理残留 + soft reset 回退测试 commit。
    monkeypatch function 级自动还原（不影响其他测试模块）。
    """
    # 用模块对象 patch（字符串路径在 pytest 下不可靠）
    import sys
    import zephyr.gov_enforcement.rule_bridge.session_worktree as sw_mod
    import zephyr.gov_enforcement.rule_bridge.worktree_manager as wm_mod
    test_mod = sys.modules[__name__]
    monkeypatch.setattr(sw_mod, "REPO_ROOT", _isolated_repo)
    monkeypatch.setattr(wm_mod, "REPO_ROOT", _isolated_repo)
    monkeypatch.setattr(test_mod, "REPO_ROOT", _isolated_repo)
    orig_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=_isolated_repo, capture_output=True, text=True
    ).stdout.strip()
    _cleanup_artifacts(_isolated_repo)
    yield
    _cleanup_artifacts(_isolated_repo, orig_head=orig_head)


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


def test_worktree_commit_file_deletion():
    """文件删除同步——主工作区删除 tracked 文件，worktree commit 同步删除并 stage。

    验证 session_worktree_commit 的删除同步逻辑（FP-ISO.4C 君子协定模式）：
    - AI 在主工作区删除 tracked 文件 → session_worktree_commit 应将删除同步到 worktree
    - worktree commit 应包含删除操作（unlink + git add -A stage 删除）
    - 排除直接写入 worktree 的未跟踪新文件（不应被误删，由 test_worktree_commit_isolation 覆盖）
    """
    # 1. 在主工作区创建 tracked 文件（commit 到 HEAD，worktree 会继承）
    marker = REPO_ROOT / _TEST_FILE_A
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text('{"session": "del-test"}\n', encoding="utf-8")
    subprocess.run(["git", "add", "--", _TEST_FILE_A], cwd=REPO_ROOT, capture_output=True)
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "test: add marker for deletion test"],
        cwd=REPO_ROOT, capture_output=True,
    )

    # 2. 启动 worktree（继承 HEAD，含 _TEST_FILE_A）
    rA = session_worktree_start("sess-pytest-A")
    wtA = Path(rA["worktree_path"])
    assert (wtA / _TEST_FILE_A).exists(), "worktree 未继承 tracked 文件"

    # 3. 在主工作区删除文件（模拟 AI 删除文件后调用 session_worktree_commit）
    marker.unlink()
    assert not marker.exists(), "主工作区文件未删除"

    # 4. worktree commit（应同步删除到 worktree 并 stage 删除）
    cA = session_worktree_commit(
        "sess-pytest-A",
        files=[_TEST_FILE_A],
        message="test: delete file via worktree",
    )
    assert cA["status"] == "OK", f"删除 commit 失败: {cA}"

    # 5. 验证 worktree 内文件已被删除（删除同步生效）
    assert not (wtA / _TEST_FILE_A).exists(), "worktree 内文件未被删除——删除同步失败"


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
    mA = session_worktree_merge("sess-pytest-A", reconcile_verify=False)
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


def test_worktree_abort_cleans_main_workdir():
    """abort with files 参数清理主工作区残留（君子协定模式：AI 写项目根，abort 需同步清理）。"""
    sid = "sess-pytest-abort-files"
    r = session_worktree_start(sid)
    assert r.get("worktree_path"), f"start 失败: {r}"

    # 模拟 AI 用 Write 创建新文件到项目根（untracked）
    new_file = "tests/governance/rule_bridge/_wt_abort_main.json"
    new_path = REPO_ROOT / new_file
    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text('{"abort_test": true}\n', encoding="utf-8")
    assert new_path.exists(), "文件未创建"

    # abort with files——应清理主工作区 untracked 文件
    a = session_worktree_abort(sid, files=[new_file])
    assert a.get("aborted"), f"abort 失败: {a}"
    assert a.get("main_cleaned") == 1, f"应清理 1 个文件: {a}"

    # 验证 untracked 文件已被删除
    assert not new_path.exists(), "主工作区 untracked 文件未被清理"


def test_worktree_commit_held_overlap_blocks():
    """HELD-OVERLAP 硬阻断：A commit 文件后（auto-claim），B commit 同文件被阻断。"""
    # Session A commit _TEST_FILE_A（auto-claim）
    rA = session_worktree_start("sess-pytest-A")
    wtA = Path(rA["worktree_path"])
    marker_a = wtA / _TEST_FILE_A
    marker_a.parent.mkdir(parents=True, exist_ok=True)
    marker_a.write_text('{"session": "A"}\n', encoding="utf-8")
    cA = session_worktree_commit("sess-pytest-A", files=[_TEST_FILE_A], message="test: A claims file")
    assert cA["status"] == "OK", f"A commit 失败: {cA}"

    # Session B try commit _TEST_FILE_A（应被硬阻断）
    rB = session_worktree_start("sess-pytest-B")
    wtB = Path(rB["worktree_path"])
    marker_b = wtB / _TEST_FILE_A  # B 也写同文件
    marker_b.parent.mkdir(parents=True, exist_ok=True)
    marker_b.write_text('{"session": "B"}\n', encoding="utf-8")
    cB = session_worktree_commit("sess-pytest-B", files=[_TEST_FILE_A], message="test: B overlap")
    assert cB["status"] == "FAILED", f"B 应被阻断: {cB}"
    assert cB.get("held_overlap") is True, f"B 应返回 held_overlap=True: {cB}"


def test_worktree_commit_allow_overlap():
    """allow_overlap=True 逃生通道：B commit A 持有的文件时放行。"""
    # Session A commit _TEST_FILE_A（auto-claim）
    rA = session_worktree_start("sess-pytest-A")
    wtA = Path(rA["worktree_path"])
    marker_a = wtA / _TEST_FILE_A
    marker_a.parent.mkdir(parents=True, exist_ok=True)
    marker_a.write_text('{"session": "A"}\n', encoding="utf-8")
    cA = session_worktree_commit("sess-pytest-A", files=[_TEST_FILE_A], message="test: A claims file")
    assert cA["status"] == "OK", f"A commit 失败: {cA}"

    # Session B commit _TEST_FILE_A with allow_overlap=True（逃生通道放行）
    rB = session_worktree_start("sess-pytest-B")
    wtB = Path(rB["worktree_path"])
    marker_b = wtB / _TEST_FILE_A
    marker_b.parent.mkdir(parents=True, exist_ok=True)
    marker_b.write_text('{"session": "B"}\n', encoding="utf-8")
    cB = session_worktree_commit(
        "sess-pytest-B", files=[_TEST_FILE_A], message="test: B overlap escape",
        allow_overlap=True,
    )
    assert cB["status"] == "OK", f"B allow_overlap 应放行: {cB}"


def test_worktree_merge_releases_claims():
    """merge 后 unregister 自动释放 claim，其他 session 可 commit 同文件。"""
    from zephyr.security.access_control.session_concurrency import SessionRegistry
    registry = SessionRegistry(REPO_ROOT)

    # Session A commit _TEST_FILE_A（auto-claim）
    rA = session_worktree_start("sess-pytest-A")
    wtA = Path(rA["worktree_path"])
    marker_a = wtA / _TEST_FILE_A
    marker_a.parent.mkdir(parents=True, exist_ok=True)
    marker_a.write_text('{"session": "A"}\n', encoding="utf-8")
    cA = session_worktree_commit("sess-pytest-A", files=[_TEST_FILE_A], message="test: A claims")
    assert cA["status"] == "OK", f"A commit 失败: {cA}"

    # 验证 A 持有 _TEST_FILE_A
    test_file_a_abs = str((REPO_ROOT / _TEST_FILE_A).resolve())
    other_held = registry.other_held_files("sess-pytest-B")
    assert test_file_a_abs in other_held, f"A 应持有 {_TEST_FILE_A}: {other_held}"

    # Session B try commit _TEST_FILE_A → blocked
    rB = session_worktree_start("sess-pytest-B")
    wtB = Path(rB["worktree_path"])
    marker_b = wtB / _TEST_FILE_A
    marker_b.parent.mkdir(parents=True, exist_ok=True)
    marker_b.write_text('{"session": "B"}\n', encoding="utf-8")
    cB = session_worktree_commit("sess-pytest-B", files=[_TEST_FILE_A], message="test: B blocked")
    assert cB.get("held_overlap") is True, f"B 应被阻断: {cB}"

    # A merge → unregister → 释放 claim
    mA = session_worktree_merge("sess-pytest-A", reconcile_verify=False)
    assert mA.get("merged"), f"A merge 失败: {mA}"

    # 验证 A 不再持有 _TEST_FILE_A
    other_held = registry.other_held_files("sess-pytest-B")
    assert test_file_a_abs not in other_held, f"A merge 后应释放 {_TEST_FILE_A}: {other_held}"

    # B 现在可以 commit _TEST_FILE_A
    cB2 = session_worktree_commit("sess-pytest-B", files=[_TEST_FILE_A], message="test: B after A merge")
    assert cB2["status"] == "OK", f"B 应在 A merge 后成功: {cB2}"


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
    mA = session_worktree_merge(sidA, reconcile_verify=False)
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


# ---------------------------------------------------------------------------
# 启动清扫 _sweep_stale_worktrees 单元测试（治本 4.2 方案 1）
# 验证三重安全保护：age + active registry + 分支 tip（核心两重：age + active）
# ---------------------------------------------------------------------------

def test_sweep_cleans_stale_orphan():
    """sweep 清理老化的孤儿物理目录（git worktree 未注册，判据通过）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _sweep_stale_worktrees
    from zephyr.gov_enforcement.rule_bridge.worktree_manager import WorktreeManager
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    orphan = Path(REPO_ROOT) / ".aidrafts" / "sess-stale-orphan"
    orphan.mkdir(parents=True, exist_ok=True)
    (orphan / "marker").write_text("stale", encoding="utf-8")
    # 老化 mtime（2小时前，超过默认 30min 阈值）
    old = time.time() - 7200
    os.utime(orphan, (old, old))

    try:
        manager = WorktreeManager(REPO_ROOT)
        registry = SessionRegistry(REPO_ROOT)
        r = _sweep_stale_worktrees(manager, registry, max_age_minutes=30)
        assert r["swept"] >= 1, f"应清理孤儿目录: {r}"
        assert not orphan.exists(), f"孤儿目录未被清: {orphan}"
    finally:
        if orphan.exists():
            _force_rmtree(orphan)


def test_sweep_preserves_active_session():
    """sweep 不清理活跃 session 的 worktree（判据2：在 active registry）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _sweep_stale_worktrees
    from zephyr.gov_enforcement.rule_bridge.worktree_manager import WorktreeManager
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    # 创建活跃 session worktree（start 会注册到 active registry）
    rA = session_worktree_start("sess-pytest-A")
    wtA = Path(rA["worktree_path"])
    assert wtA.exists(), f"A worktree 未创建: {rA}"
    # 老化 A 的 mtime（模拟看起来老，但仍在 active registry——判据2 应保护）
    old = time.time() - 7200
    os.utime(wtA, (old, old))

    manager = WorktreeManager(REPO_ROOT)
    registry = SessionRegistry(REPO_ROOT)
    r = _sweep_stale_worktrees(manager, registry, max_age_minutes=30)
    assert r["swept"] == 0, f"不应清活跃 session worktree: {r}"
    assert wtA.exists(), f"活跃 worktree 被误清: {wtA}"


def test_sweep_skips_recent_dirs():
    """sweep 跳过太新的目录（判据1：age < threshold，防误清并发 AI 正在创建的）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _sweep_stale_worktrees
    from zephyr.gov_enforcement.rule_bridge.worktree_manager import WorktreeManager
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    fresh = Path(REPO_ROOT) / ".aidrafts" / "sess-fresh-orphan"
    fresh.mkdir(parents=True, exist_ok=True)
    (fresh / "marker").write_text("fresh", encoding="utf-8")
    # 不老化 mtime（now），age < 30min——判据1 应跳过

    try:
        manager = WorktreeManager(REPO_ROOT)
        registry = SessionRegistry(REPO_ROOT)
        r = _sweep_stale_worktrees(manager, registry, max_age_minutes=30)
        assert r["swept"] == 0, f"不应清新目录: {r}"
        assert fresh.exists(), f"新目录被误清: {fresh}"
    finally:
        if fresh.exists():
            _force_rmtree(fresh)


# ---------------------------------------------------------------------------
# 治本变更并发阻断测试（§9.7 治本，2026-07-04）
# 验证双向阻断：breaking_change session 阻止其他 session，普通 session 避让 breaking_change session
# ---------------------------------------------------------------------------
def test_worktree_start_breaking_change_blocks_new_session():
    """breaking_change 双向阻断：A (breaking_change=True) 启动后，B (普通) 启动被阻断。"""
    # Session A 启动 with breaking_change=True
    rA = session_worktree_start("sess-pytest-A", breaking_change=True)
    assert rA["registered"], f"A 注册失败: {rA}"
    assert rA["created"], f"A worktree 创建失败: {rA}"

    # Session B 启动 (breaking_change=False, 默认) → 应被阻断（避让治本变更）
    rB = session_worktree_start("sess-pytest-B")
    assert not rB["registered"], f"B 不应注册成功: {rB}"
    assert "BREAKING_CHANGE_AVOIDANCE_BLOCKED" in rB.get("error", ""), f"B 应被阻断: {rB}"
    assert rB.get("blocked_by") == ["sess-pytest-A"], f"blocked_by 应为 A: {rB}"

    # cleanup: A abort
    session_worktree_abort("sess-pytest-A")


def test_worktree_start_breaking_change_blocks_concurrent_breaking():
    """breaking_change 双向阻断：A (breaking_change=True) 启动后，B (breaking_change=True) 也被阻断。"""
    # Session A 启动 with breaking_change=True
    rA = session_worktree_start("sess-pytest-A", breaking_change=True)
    assert rA["registered"], f"A 注册失败: {rA}"

    # Session B 启动 with breaking_change=True → 应被阻断（治本变更期间禁止任何并发）
    rB = session_worktree_start("sess-pytest-B", breaking_change=True)
    assert not rB["registered"], f"B 不应注册成功: {rB}"
    assert "BREAKING_CHANGE_CONCURRENCY_BLOCKED" in rB.get("error", ""), f"B 应被阻断: {rB}"
    assert "sess-pytest-A" in rB.get("blocked_by", []), f"blocked_by 应含 A: {rB}"

    # cleanup: A abort
    session_worktree_abort("sess-pytest-A")


def test_worktree_start_breaking_change_allow_concurrent_escape():
    """allow_concurrent=True 逃生通道：A (breaking_change=True) 启动后，B (allow_concurrent=True) 放行。"""
    # Session A 启动 with breaking_change=True
    rA = session_worktree_start("sess-pytest-A", breaking_change=True)
    assert rA["registered"], f"A 注册失败: {rA}"

    # Session B 启动 with allow_concurrent=True（逃生通道）→ 应放行
    rB = session_worktree_start("sess-pytest-B", allow_concurrent=True)
    assert rB["registered"], f"B 应注册成功（逃生通道）: {rB}"
    assert rB["created"], f"B worktree 应创建: {rB}"

    # cleanup: A + B abort
    session_worktree_abort("sess-pytest-A")
    session_worktree_abort("sess-pytest-B")
