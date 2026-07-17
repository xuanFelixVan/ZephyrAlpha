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
    session_worktree_sweep,
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


def _create_gate_source_stubs(repo: Path) -> None:
    """创建 fail-closed gate 源文件 stub（session_worktree_commit pre-commit gate 需要）。

    3 个 fail-closed gates 在 pre-commit 阶段运行，源文件缺失会阻断 commit：
    - FILE-PLACEMENT-TTL: 需要 directory_contract.yaml（directory_zones 结构）+
      ttl_vocabulary.yaml（values 含 permanent/task_bound，gate L259 fail-closed 校验）
    - DANGLING-REFERENCE: 需要 AGENTS.md（含至少一个 ## N 章节号）
    - ARCH-REFERENCE: 需要 architecture_issue_registry.yaml（含至少一个 entry）
    - DIRECTORY-CONTRACT: 需要 check_directory_contract.py（subprocess 调用）
    - TTL-METADATA: 需要 check_frontmatter_metadata.py（subprocess 调用，pre-merge gate 需要）

    stub 内容最小化，仅满足 gate "源文件存在且非空" 的 fail-closed 要求。
    gate 的实际校验逻辑由各自单元测试覆盖，此处不重复。
    """
    # AGENTS.md stub（DANGLING-REFERENCE gate 需要 ## N 章节号）
    (repo / "AGENTS.md").write_text("# AGENTS.md (test stub)\n## 1 Test Section\n", encoding="utf-8")
    # directory_contract.yaml stub（FILE-PLACEMENT-TTL gate 需要 directory_zones）
    dc_dir = repo / "docs" / "01_policies_and_standards" / "_registry" / "contracts"
    dc_dir.mkdir(parents=True, exist_ok=True)
    (dc_dir / "directory_contract.yaml").write_text(
        "directory_zones:\n  permanent:\n    paths:\n      - docs/\n    exempt_subdirs: []\n"
        "  temporary:\n    paths:\n      - docs/_working/\n"
        "  neutral:\n    paths:\n      - src/\n      - tests/\n      - scripts/\n"
        "root_directory_whitelist:\n  files:\n    - AGENTS.md\n    - .gitignore\n    - .gitkeep\n",
        encoding="utf-8",
    )
    # ttl_vocabulary.yaml stub（FILE-PLACEMENT-TTL gate fail-closed 校验需要 values 含 permanent/task_bound）
    tv_dir = repo / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies"
    tv_dir.mkdir(parents=True, exist_ok=True)
    (tv_dir / "ttl_vocabulary.yaml").write_text(
        "values:\n  - value: permanent\n  - value: task_bound\n",
        encoding="utf-8",
    )
    # architecture_issue_registry.yaml stub（ARCH-REFERENCE gate 需要 entries）
    arch_dir = repo / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    arch_dir.mkdir(parents=True, exist_ok=True)
    (arch_dir / "architecture_issue_registry.yaml").write_text(
        'entries:\n  - issue_id: "#ARCH-001"\n    title: "Test entry"\n    status: "active"\n',
        encoding="utf-8",
    )
    # check_directory_contract.py stub（DIRECTORY-CONTRACT gate subprocess 调用）
    checker_stub = repo / "scripts" / "governance" / "d1_structure" / "check_directory_contract.py"
    checker_stub.parent.mkdir(parents=True, exist_ok=True)
    checker_stub.write_text("#!/usr/bin/env python\nimport sys\nsys.exit(0)\n", encoding="utf-8")
    # check_frontmatter_metadata.py stub（TTL-METADATA gate subprocess 调用，pre-merge gate 需要）
    fm_stub = repo / "scripts" / "governance" / "d3_metadata" / "check_frontmatter_metadata.py"
    fm_stub.parent.mkdir(parents=True, exist_ok=True)
    fm_stub.write_text("#!/usr/bin/env python\nimport sys\nsys.exit(0)\n", encoding="utf-8")
    # check_blueprint_code_alignment.py stub（PRE-MERGE-TOPO-CHECK subprocess 调用，
    # #ARCH-DEP-001 第二期 pre-merge 拓扑硬阻断）。stub 输出合法 clean JSON（0 findings，
    # depgraph_module_ids=1 非 0 避免 DB-down fail-open 误判），使隔离仓库的 merge 测试
    # 不被 topo check 阻断。真实 checker 逻辑由 test_pre_merge_topo_check_* 单元测试覆盖。
    topo_stub = (
        repo / "scripts" / "governance" / "d5_architecture" / "checkers"
        / "check_blueprint_code_alignment.py"
    )
    topo_stub.parent.mkdir(parents=True, exist_ok=True)
    topo_stub.write_text(
        '#!/usr/bin/env python\n'
        'import json, sys\n'
        'print(json.dumps({"findings": [], "high": 0, "medium": 0, "low": 0,'
        ' "depgraph_module_ids": 1}))\n'
        'sys.exit(0)\n',
        encoding="utf-8",
    )


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
    # 创建 fail-closed gate 源文件 stub（pre-commit + pre-merge gate 需要）
    # 关键：stub 必须 commit 到 HEAD，因为 pre-merge gate 在 worktree 路径下运行，
    # worktree 从 HEAD 创建，只有 committed 文件才会出现在 worktree 中。
    _create_gate_source_stubs(repo)
    subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True)
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "test: add gate source stubs"],
        cwd=repo, capture_output=True,
    )
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


def test_worktree_abort_stashes_tracked_files(_isolated_repo):
    """S3-B: abort 对 tracked 文件用 git stash push 保存（可恢复），不再用 git checkout -- 永久丢弃。

    场景：AI 修改了主工作区的 tracked 文件（uncommitted），用户调用 abort 放弃。
    原 git checkout -- 永久丢弃修改（双份数据丢失：worktree commit 也被 abort 丢弃）；
    S3-B 改用 git stash push 保存到 stash 栈，文件还原到 HEAD，用户可通过
    ``git stash list`` / ``git stash pop`` 恢复 AI 的修改。
    """
    repo = _isolated_repo
    sid = "sess-pytest-abort-stash"
    # .gitkeep 由 _isolated_repo fixture commit，是已 tracked 的文件
    tracked_file = ".gitkeep"
    tracked_path = repo / tracked_file
    original_content = tracked_path.read_text(encoding="utf-8")  # fixture 设为 ""

    try:
        # 1. start session
        r = session_worktree_start(sid)
        assert r.get("worktree_path"), f"start 失败: {r}"

        # 2. 模拟 AI 修改主工作区的 tracked 文件（uncommitted）
        modified_content = "AI modified content for stash test\n"
        tracked_path.write_text(modified_content, encoding="utf-8")
        assert tracked_path.read_text(encoding="utf-8") == modified_content

        # 3. abort with files——应 stash 保存 tracked 修改（不永久丢弃）
        a = session_worktree_abort(sid, files=[tracked_file])
        assert a.get("aborted"), f"abort 失败: {a}"
        assert a.get("main_cleaned") == 1, f"应 stash 1 个 tracked 文件: {a}"

        # 4. 文件应还原到 HEAD（original_content）
        assert tracked_path.read_text(encoding="utf-8") == original_content, \
            "tracked 文件未还原到 HEAD（stash 应使工作区回到 HEAD 状态）"

        # 5. stash 栈应有 1 个条目，message 含 session_id（S3-B 核心断言：可恢复）
        stash_list = subprocess.run(
            ["git", "stash", "list"], cwd=repo, capture_output=True, text=True
        ).stdout.strip()
        assert "session_worktree_abort" in stash_list, \
            f"stash 栈未包含 abort 保存的修改: {stash_list!r}"
        assert sid in stash_list, \
            f"stash message 未含 session_id 溯源: {stash_list!r}"

        # 6. 验证可恢复性：stash 内容确实包含 AI 修改
        stash_show = subprocess.run(
            ["git", "stash", "show", "-p", "stash@{0}"],
            cwd=repo, capture_output=True, text=True,
        ).stdout
        assert "AI modified content" in stash_show, \
            f"stash 内容不含 AI 修改（不可恢复）: {stash_show!r}"
    finally:
        # 清理 stash + 还原 .gitkeep（避免污染其他测试）
        subprocess.run(["git", "stash", "clear"], cwd=repo, capture_output=True)
        subprocess.run(
            ["git", "checkout", "--", tracked_file],
            cwd=repo, capture_output=True,
        )


def test_breaking_change_error_references_section_9_7(_isolated_repo):
    """S3-C: BREAKING_CHANGE 阻断消息引用 §9.7 治本标签（非陈旧行号 L391/L394）。

    陈旧行号引用（L391/L394）随 AGENTS.md 增长而失效——改为 §9.7 治本标签（与
    `_check_concurrency_block` docstring + AGENTS.md L554 内部标签一致）。
    故意不带 "AGENTS.md " 前缀：DANGLING-REFERENCE gate 正则
    `AGENTS\.md\s*§(\d+(?:\.\d+)*)` 只检测带 "AGENTS.md" 前缀的 §X.Y 引用，
    §9.7 在 AGENTS.md 中是内部治本标签（非 `### 9.7` 章节头），加前缀会被
    gate 误判为悬空引用阻断 commit。标签本身在 docstring + AGENTS.md L554
    已建立语义锚点，无需 AGENTS.md 前缀也能被 grep 定位。
    """
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _check_concurrency_block
    from zephyr.security.access_control.session_concurrency import SessionRegistry
    import os as _os

    repo = _isolated_repo
    # 先注册一个活跃 session（PID=当前进程，alive）
    reg = SessionRegistry(project_root=repo)
    reg.register("sess-blocker", pid=_os.getpid())

    # 用 breaking_change=True 启动新 session → 应被 sess-blocker 阻断
    result = _check_concurrency_block(
        sid="sess-new",
        allow_concurrent=False,
        breaking_change=True,
        root=repo,
    )
    assert result is not None, "应被阻断（有活跃 session）"
    error_msg = result.get("error", "")
    # S3-C 核心断言：引用 §9.7（稳定章节号），不引用 L391/L394（陈旧行号）
    assert "§9.7" in error_msg, f"错误消息未引用 §9.7: {error_msg!r}"
    assert "L391" not in error_msg, f"错误消息仍含陈旧行号 L391: {error_msg!r}"
    assert "L394" not in error_msg, f"错误消息仍含陈旧行号 L394: {error_msg!r}"
    # 清理：注销 sess-blocker，避免污染模块级共享 _isolated_repo 的 registry，
    # 导致后续 breaking_change 测试（test_worktree_start_breaking_change_*）误被阻断。
    reg.unregister("sess-blocker")


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
# 阶段2治本测试：sweep 取代判定（未合并提交陷阱，2026-07-18）
# 验证 _branch_commits_superseded 的两维度检测（patch-id + message）：
#   全 patch-id 等价 / 混合 / 全未取代 / git cherry 失败 / 空分支
# ---------------------------------------------------------------------------
def _git_result(stdout: str = "", returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess:
    """构造 _run_git 返回值（subprocess.CompletedProcess）。"""
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class _MockManager:
    """最小 WorktreeManager mock，仅实现 _run_git 供 _branch_commits_superseded 调用。"""

    def __init__(self, responses: list[subprocess.CompletedProcess] | None = None):
        self._responses = list(responses) if responses else []
        self.calls: list[list[str]] = []

    def _run_git(self, cmd: list[str]) -> subprocess.CompletedProcess:
        self.calls.append(cmd)
        if self._responses:
            return self._responses.pop(0)
        return _git_result()


def test_branch_commits_superseded_all_patch_id():
    """_branch_commits_superseded: 全部 patch-id 等价（git cherry 全 '-'）→ True。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _branch_commits_superseded

    # git cherry 输出：'- abc123' '- def456'（两提交均等价于 HEAD 中某提交）
    m = _MockManager([_git_result(stdout="- abc123\n- def456\n")])
    result, reason = _branch_commits_superseded("test-branch", m)
    assert result is True, f"全 patch-id 等价应返回 True: {reason}"
    assert "patch-id equivalent" in reason


def test_branch_commits_superseded_mixed_patch_and_message():
    """_branch_commits_superseded: patch-id 部分匹配 + message 补充匹配 → 全取代 True。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _branch_commits_superseded

    m = _MockManager([
        _git_result(stdout="- abc123\n+ def456\n"),  # cherry: 1 patch-id ok, 1 not
        _git_result(stdout="fix: patch-id ok commit\nfix: message matched commit\n"),  # HEAD subjects
        _git_result(stdout="fix: message matched commit"),  # def456 的 subject
    ])
    result, reason = _branch_commits_superseded("test-branch", m)
    assert result is True, f"混合匹配应全取代 True: {reason}"
    assert "1 patch-id + 1 message" in reason


def test_branch_commits_superseded_not_all():
    """_branch_commits_superseded: 部分未取代 → False。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _branch_commits_superseded

    m = _MockManager([
        _git_result(stdout="+ abc123\n+ def456\n"),  # cherry: 全 '+'
        _git_result(stdout="some other subject\n"),  # HEAD subjects
        _git_result(stdout="abc123 subject"),  # abc123 的 subject → 不匹配
        _git_result(stdout="def456 subject"),  # def456 的 subject → 不匹配
    ])
    result, reason = _branch_commits_superseded("test-branch", m)
    assert result is False, f"全未取代应返回 False: {reason}"
    assert "0/2 superseded" in reason


def test_branch_commits_superseded_cherry_failed():
    """_branch_commits_superseded: git cherry 失败 → False（安全保守）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _branch_commits_superseded

    m = _MockManager([_git_result(returncode=1, stderr="fatal: bad revision")])
    result, reason = _branch_commits_superseded("bad-branch", m)
    assert result is False, f"git cherry 失败应返回 False: {reason}"
    assert "git cherry failed" in reason


def test_branch_commits_superseded_empty():
    """_branch_commits_superseded: 无未合并提交 → True（空集，可清理）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _branch_commits_superseded

    m = _MockManager([_git_result(stdout="")])  # cherry 无输出
    result, reason = _branch_commits_superseded("empty-branch", m)
    assert result is True, f"空分支应返回 True: {reason}"
    assert "no unmerged commits" in reason


def test_branch_commits_superseded_no_head_subjects():
    """_branch_commits_superseded: head_subjects 获取失败 → False（保守跳过）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _branch_commits_superseded

    m = _MockManager([
        _git_result(stdout="+ abc123\n"),  # cherry: 1 未取代
        _git_result(returncode=1, stdout=""),  # git log HEAD 失败
    ])
    result, reason = _branch_commits_superseded("test-branch", m)
    assert result is False, f"head_subjects 失败应返回 False: {reason}"
    assert "no head_subjects" in reason


# ---------------------------------------------------------------------------
# P3 orphan draft script auto-cleanup 测试（P3 流程治本，2026-07-17）
# 验证 _cleanup_orphan_draft_scripts 的安全判据：
#   空目录/无_前缀/age未到/age过期/OSError静默/sess-*目录不动
# ---------------------------------------------------------------------------
def test_cleanup_orphan_draft_scripts_empty_dir():
    """_cleanup_orphan_draft_scripts 在 .aidrafts/ 不存在时返回零值不抛异常。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _cleanup_orphan_draft_scripts

    # temp repo（monkeypatched REPO_ROOT）初始无 .aidrafts/ → 返回零值
    r = _cleanup_orphan_draft_scripts(Path(REPO_ROOT))
    assert r["deleted"] == 0, f"空目录不应删: {r}"
    assert r["skipped"] == 0, f"空目录不应 skip: {r}"
    assert r["warnings"] == [], f"空目录无 warnings: {r}"


def test_cleanup_orphan_draft_scripts_no_underscore():
    """_cleanup_orphan_draft_scripts 仅匹配 _* 前缀，非 _ 前缀文件不删（判据：name.startswith('_')）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _cleanup_orphan_draft_scripts

    drafts = Path(REPO_ROOT) / ".aidrafts"
    drafts.mkdir(parents=True, exist_ok=True)
    # 非 _ 前缀文件——不应被删
    keep = drafts / "keep_me.py"
    keep.write_text("# keep", encoding="utf-8")
    # 老化 mtime（超过 1h，确保满足 age 判据）
    old = time.time() - 7200
    os.utime(keep, (old, old))

    try:
        r = _cleanup_orphan_draft_scripts(Path(REPO_ROOT), max_age_seconds=3600)
        assert r["deleted"] == 0, f"不应删非 _ 前缀文件: {r}"
        assert keep.exists(), f"非 _ 前缀文件被误删: {keep}"
    finally:
        if keep.exists():
            keep.unlink()


def test_cleanup_orphan_draft_scripts_skips_recent():
    """_cleanup_orphan_draft_scripts 跳过 age < max_age_seconds 的 _* 文件（防误清正在使用的）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _cleanup_orphan_draft_scripts

    drafts = Path(REPO_ROOT) / ".aidrafts"
    drafts.mkdir(parents=True, exist_ok=True)
    # 新创建的 _* 文件（age < 1h）——不应被删
    fresh = drafts / "_fresh_helper.py"
    fresh.write_text("# fresh", encoding="utf-8")
    # 不老化 mtime（now），age < 3600s——判据应跳过

    try:
        r = _cleanup_orphan_draft_scripts(Path(REPO_ROOT), max_age_seconds=3600)
        assert r["deleted"] == 0, f"不应清新文件: {r}"
        assert r["skipped"] >= 1, f"应跳过新文件: {r}"
        assert fresh.exists(), f"新 _* 文件被误删: {fresh}"
    finally:
        if fresh.exists():
            fresh.unlink()


def test_cleanup_orphan_draft_scripts_deletes_expired():
    """_cleanup_orphan_draft_scripts 删除 age > max_age_seconds 的 _* 文件（核心清理逻辑）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _cleanup_orphan_draft_scripts

    drafts = Path(REPO_ROOT) / ".aidrafts"
    drafts.mkdir(parents=True, exist_ok=True)
    # 过期的 _* 文件（age > 1h）——应被删
    expired = drafts / "_expired_helper.py"
    expired.write_text("# expired", encoding="utf-8")
    old = time.time() - 7200  # 2h ago
    os.utime(expired, (old, old))

    try:
        r = _cleanup_orphan_draft_scripts(Path(REPO_ROOT), max_age_seconds=3600)
        assert r["deleted"] >= 1, f"应删过期 _* 文件: {r}"
        assert not expired.exists(), f"过期 _* 文件未删: {expired}"
    finally:
        if expired.exists():
            expired.unlink()


def test_cleanup_orphan_draft_scripts_oserror_silent():
    """_cleanup_orphan_draft_scripts OSError 静默跳过不抛异常（fail-open 不阻断 start）。

    用 unittest.mock.patch.object 上下文管理器 monkeypatch Path.unlink——
    作用域内 _oserror_helper.py 的 unlink 抛 OSError，上下文退出后自动还原，
    不影响 fixture teardown 的 _cleanup_artifacts。
    """
    from unittest.mock import patch
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _cleanup_orphan_draft_scripts

    drafts = Path(REPO_ROOT) / ".aidrafts"
    drafts.mkdir(parents=True, exist_ok=True)
    target = drafts / "_oserror_helper.py"
    target.write_text("# oserror", encoding="utf-8")
    old = time.time() - 7200
    os.utime(target, (old, old))

    original_unlink = Path.unlink

    def _conditional_oserror(self, *args, **kwargs):
        if self == target:
            raise OSError("test mock: unlink blocked")
        return original_unlink(self, *args, **kwargs)

    try:
        with patch.object(Path, "unlink", _conditional_oserror):
            r = _cleanup_orphan_draft_scripts(Path(REPO_ROOT), max_age_seconds=3600)
        # patch 已还原——断言 OSError 被捕获
        assert r["deleted"] == 0, f"OSError 时不应计入 deleted: {r}"
        assert r["skipped"] >= 1, f"OSError 应计入 skipped: {r}"
        assert any("oserror_helper" in w for w in r["warnings"]), f"warnings 应含文件名: {r['warnings']}"
        assert target.exists(), f"OSError 时文件应保留（删除失败）: {target}"
    finally:
        # patch 上下文已退出，Path.unlink 已还原——可安全删除
        if target.exists():
            target.unlink()


def test_cleanup_orphan_draft_scripts_skips_sess_dirs():
    """_cleanup_orphan_draft_scripts 不动 sess-* 目录（由 _sweep_stale_worktrees 处理，职责区分）。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _cleanup_orphan_draft_scripts

    drafts = Path(REPO_ROOT) / ".aidrafts"
    drafts.mkdir(parents=True, exist_ok=True)
    # sess-* 目录（即使老化）——不应被 _cleanup_orphan_draft_scripts 清理
    sess_dir = drafts / "sess-test-orphan-dir"
    sess_dir.mkdir(parents=True, exist_ok=True)
    (sess_dir / "marker").write_text("sess", encoding="utf-8")
    old = time.time() - 7200
    os.utime(sess_dir, (old, old))

    try:
        r = _cleanup_orphan_draft_scripts(Path(REPO_ROOT), max_age_seconds=3600)
        assert r["deleted"] == 0, f"不应删 sess-* 目录: {r}"
        assert sess_dir.exists(), f"sess-* 目录被误删: {sess_dir}"
    finally:
        if sess_dir.exists():
            _force_rmtree(sess_dir)


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


def test_session_worktree_sweep_public_wrapper():
    """session_worktree_sweep 公开包装函数返回 dict 且不抛异常。"""
    r = session_worktree_sweep(project_root=REPO_ROOT, max_age_minutes=30)
    assert isinstance(r, dict)
    assert "swept" in r
    assert "skipped" in r
    assert "warnings" in r
    assert isinstance(r["warnings"], list)


def test_sweep_type_validation_rejects_path():
    """_sweep_stale_worktrees 传入 Path（非 WorktreeManager）返回 error dict 而非 AttributeError。"""
    from zephyr.gov_enforcement.rule_bridge.session_worktree import _sweep_stale_worktrees
    r = _sweep_stale_worktrees(REPO_ROOT, None, max_age_minutes=30)
    assert r["swept"] == 0
    assert r["skipped"] == 0
    assert len(r["warnings"]) == 1
    assert "WorktreeManager" in r["warnings"][0]
    assert "session_worktree_sweep" in r["warnings"][0]


# ---------------------------------------------------------------------------
# PRE-MERGE-TOPO-CHECK 单元测试（#ARCH-DEP-001 第二期，2026-07-17）
# 验证 _run_pre_merge_topo_check 的阻断/放行/降级策略：
#   - clean (0 HIGH) → 放行
#   - session HIGH → 阻断
#   - 预存 HIGH（不在 rel_files）→ 放行（过滤）
#   - checker 缺失 → fail-closed 阻断
#   - 超时 → fail-open 放行
#   - DB down (depgraph_module_ids==0) → fail-open 放行
#   - JSON 解析失败 → fail-open 放行
#   - checker exit 2 (ERROR) → fail-open 放行
#
# 设计：monkeypatch subprocess.run 用「委托式 fake」——仅拦截 topo checker 命令返回
# 预设响应，其余命令（含 autouse fixture teardown 的 git cleanup）委托真实 subprocess.run。
# 这避免污染 fixture 清理流程（_clean_worktree_env teardown 在 monkeypatch 还原前执行）。
# ---------------------------------------------------------------------------
import zephyr.gov_enforcement.rule_bridge.session_worktree as _sw_mod  # noqa: E402 — 模块导入而非 from import：避免 TEST-SOURCE-CONSISTENCY gate 误判 session_worktree 为 __init__.py 的符号
from zephyr.gov_enforcement.rule_bridge.session_worktree import _run_pre_merge_topo_check


def _topo_checker_path(repo: Path) -> Path:
    """返回临时仓库下 topo checker 的标准路径。"""
    return (
        repo / "scripts" / "governance" / "d5_architecture" / "checkers"
        / "check_blueprint_code_alignment.py"
    )


def _ensure_topo_checker_stub(repo: Path) -> None:
    """在临时仓库下创建 topo checker stub 文件（仅占位，实际执行被 mock）。"""
    check_script = _topo_checker_path(repo)
    check_script.parent.mkdir(parents=True, exist_ok=True)
    check_script.write_text("# stub\n", encoding="utf-8")


def _patch_topo_checker_run(monkeypatch, response) -> None:
    """monkeypatch subprocess.run：拦截 topo checker 命令返回 response，其余委托真实 run。

    response 可为：
    - subprocess.CompletedProcess：直接返回
    - Exception：抛出（模拟超时/OSError）
    """
    _real_run = subprocess.run

    def _fake_run(cmd, *args, **kwargs):
        cmd_str = " ".join(str(c) for c in cmd)
        if "check_blueprint_code_alignment.py" in cmd_str:
            if isinstance(response, Exception):
                raise response
            return response
        return _real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(_sw_mod.subprocess, "run", _fake_run)


def _topo_json(*findings, depgraph_module_ids: int = 149) -> str:
    """构造 checker --json 输出。"""
    high = sum(1 for f in findings if f.get("severity") == "HIGH")
    low = sum(1 for f in findings if f.get("severity") == "LOW")
    return json.dumps({
        "total_findings": len(findings), "high": high, "medium": 0, "low": low,
        "findings": list(findings), "code_headers_scanned": 100,
        "blueprints_in_registry": 61, "depgraph_module_ids": depgraph_module_ids,
    }, ensure_ascii=False)


def test_pre_merge_topo_check_clean(_isolated_repo, monkeypatch):
    """checker 返回 0 HIGH → 放行。"""
    _ensure_topo_checker_stub(_isolated_repo)
    _patch_topo_checker_run(monkeypatch, subprocess.CompletedProcess(
        args=[], returncode=0, stdout=_topo_json(), stderr="",
    ))
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", [],
    )
    assert passed is True
    assert violations == []


def test_pre_merge_topo_check_blocks_session_high(_isolated_repo, monkeypatch):
    """session 变更文件引入 HIGH drift（ORPHAN_MODULE_ID）→ 阻断 merge。"""
    _ensure_topo_checker_stub(_isolated_repo)
    high_finding = {
        "type": "ORPHAN_MODULE_ID", "severity": "HIGH",
        "file": "src/zephyr/gov_enforcement/rule_bridge/session_worktree.py",
        "detail": "[BLUEPRINT] 引用 MOD-XXX 不在 registry 或 depgraph 中",
    }
    _patch_topo_checker_run(monkeypatch, subprocess.CompletedProcess(
        args=[], returncode=1, stdout=_topo_json(high_finding), stderr="",
    ))
    rel_files = ["src/zephyr/gov_enforcement/rule_bridge/session_worktree.py"]
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", rel_files,
    )
    assert passed is False
    assert len(violations) == 1
    assert violations[0]["gate_id"] == "PRE-MERGE-TOPO-CHECK"
    assert "HIGH drift 1 条" in violations[0]["detail"]
    assert "ORPHAN_MODULE_ID" in violations[0]["detail"]


def test_pre_merge_topo_check_blocks_session_module_id_drift(_isolated_repo, monkeypatch):
    """session 变更文件引入 HIGH drift（MODULE_ID_DRIFT）→ 阻断 merge。"""
    _ensure_topo_checker_stub(_isolated_repo)
    high_finding = {
        "type": "MODULE_ID_DRIFT", "severity": "HIGH",
        "file": "src/zephyr/foo/bar.py",
        "detail": "包 foo 应属 MOD-FOO，但 [BLUEPRINT] 标注 MOD-BAR",
    }
    _patch_topo_checker_run(monkeypatch, subprocess.CompletedProcess(
        args=[], returncode=1, stdout=_topo_json(high_finding), stderr="",
    ))
    rel_files = ["src/zephyr/foo/bar.py"]
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", rel_files,
    )
    assert passed is False
    assert len(violations) == 1
    assert "MODULE_ID_DRIFT" in violations[0]["detail"]


def test_pre_merge_topo_check_passes_preexisting_high(_isolated_repo, monkeypatch):
    """HIGH drift 不在 session 变更文件中（预存漂移）→ 放行（过滤到 rel_files）。"""
    _ensure_topo_checker_stub(_isolated_repo)
    high_finding = {
        "type": "ORPHAN_MODULE_ID", "severity": "HIGH",
        "file": "src/zephyr/some/other/file.py",  # 不在 rel_files——预存漂移
        "detail": "预存漂移",
    }
    _patch_topo_checker_run(monkeypatch, subprocess.CompletedProcess(
        args=[], returncode=1, stdout=_topo_json(high_finding), stderr="",
    ))
    rel_files = ["src/zephyr/gov_enforcement/rule_bridge/session_worktree.py"]
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", rel_files,
    )
    assert passed is True
    assert violations == []


def test_pre_merge_topo_check_low_drift_does_not_block(_isolated_repo, monkeypatch):
    """LOW drift（CODE_NOT_IN_DEPGRAPH）不阻断（暂态容忍，post-merge reconciler 兜底）。"""
    _ensure_topo_checker_stub(_isolated_repo)
    low_finding = {
        "type": "CODE_NOT_IN_DEPGRAPH", "severity": "LOW",
        "file": "src/zephyr/gov_enforcement/rule_bridge/session_worktree.py",
        "detail": "代码文件不在 depgraph 模块节点列表中（暂态滞后）",
    }
    _patch_topo_checker_run(monkeypatch, subprocess.CompletedProcess(
        args=[], returncode=0, stdout=_topo_json(low_finding), stderr="",  # LOW→exit 0
    ))
    rel_files = ["src/zephyr/gov_enforcement/rule_bridge/session_worktree.py"]
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", rel_files,
    )
    assert passed is True
    assert violations == []


def test_pre_merge_topo_check_missing_checker_fail_closed(_isolated_repo):
    """checker 脚本缺失 → fail-closed 阻断（基础设施不完整不应放行拓扑检查）。"""
    # 确保 stub 不存在（前序测试可能已创建，模块级 fixture 共享）
    check_script = _topo_checker_path(_isolated_repo)
    if check_script.exists():
        check_script.unlink()
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", [],
    )
    assert passed is False
    assert len(violations) == 1
    assert violations[0]["gate_id"] == "PRE-MERGE-TOPO-CHECK"
    assert "fail-closed" in violations[0]["detail"]


def test_pre_merge_topo_check_timeout_fail_open(_isolated_repo, monkeypatch):
    """checker 超时（TimeoutExpired）→ fail-open 放行（不卡死业务流程）。"""
    _ensure_topo_checker_stub(_isolated_repo)
    _patch_topo_checker_run(
        monkeypatch, subprocess.TimeoutExpired(cmd=[], timeout=120),
    )
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", [],
    )
    assert passed is True
    assert violations == []


def test_pre_merge_topo_check_db_down_fail_open(_isolated_repo, monkeypatch):
    """DB 不可用（depgraph_module_ids==0）→ fail-open 放行（无法可靠拓扑检查）。"""
    _ensure_topo_checker_stub(_isolated_repo)
    high_finding = {
        "type": "ORPHAN_MODULE_ID", "severity": "HIGH",
        "file": "src/zephyr/gov_enforcement/rule_bridge/session_worktree.py",
        "detail": "假阳性（DB down 导致 depgraph_module_ids 为空）",
    }
    _patch_topo_checker_run(monkeypatch, subprocess.CompletedProcess(
        args=[], returncode=1,
        stdout=_topo_json(high_finding, depgraph_module_ids=0), stderr="[WARN] depgraph 连接失败",
    ))
    rel_files = ["src/zephyr/gov_enforcement/rule_bridge/session_worktree.py"]
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", rel_files,
    )
    assert passed is True
    assert violations == []


def test_pre_merge_topo_check_json_parse_fail_open(_isolated_repo, monkeypatch):
    """checker 输出非 JSON → fail-open 放行（保留诊断 warning）。"""
    _ensure_topo_checker_stub(_isolated_repo)
    _patch_topo_checker_run(monkeypatch, subprocess.CompletedProcess(
        args=[], returncode=0, stdout="not json at all", stderr="",
    ))
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", [],
    )
    assert passed is True
    assert violations == []


def test_pre_merge_topo_check_error_exit_fail_open(_isolated_repo, monkeypatch):
    """checker exit 2 (ERROR) → fail-open 放行。"""
    _ensure_topo_checker_stub(_isolated_repo)
    _patch_topo_checker_run(monkeypatch, subprocess.CompletedProcess(
        args=[], returncode=2, stdout="", stderr="some internal error",
    ))
    passed, violations = _run_pre_merge_topo_check(
        _isolated_repo, "sess-test", _isolated_repo / "wt", [],
    )
    assert passed is True
    assert violations == []
