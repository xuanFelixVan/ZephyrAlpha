# [MODULE] tests.governance.rule_bridge.test_session_worktree_merge_no_side_effect
# [DOMAIN] D_GOV_CODE_QUALITY
# [TTL] permanent
# [DEPENDENCIES] scripts.session_worktree (cmd_merge/_capture_merge_pre_state/_restore_merge_pre_state)
# [CONSUMERS] pytest（tests/governance/rule_bridge/）
# [STARTUP] imported
# [MATURITY] production
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [INVARIANTS] 本文件钉死 st-mergefix-1016：cmd_merge 失败路径零工作树副作用——被拒/部分写/
#   squash 后 commit 失败/异常，工作树与暂存态必须与调用前逐字节一致；成功路径语义零变化
#   （不触发恢复动作）。病灶=2026-10-16 01:43:36 四件工作区回滚→ebe4cbd7d4 陈旧快照二次落地。
# [MODIFY-GUARD] 新建 2026-10-16 st-mergefix-1016（st-diskp0-20261015 P0 修复红证）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=防线缺失；永不 skip（tmp git 仓不可用时 raise，禁静默放行）
# [TESTS] 本文件即测试
"""cmd_merge 失败路径零工作树副作用回归测试（st-mergefix-1016）。

背景（2026-10-16 两次实锤）：主区 merge 失败同窗内工作树文件被静默回滚为旧版本
（reflog "merge X: updating HEAD"=reset 族签名），旧字节随后被队列当快照二次落地
（ebe4cbd7d4 覆盖 6e05b4dc90）→ HEAD 有新码、工作树跑旧码 + import 断链。
本文件断言：merge 被拒/部分应用/commit 失败/异常时，工作树+暂存态恢复到调用前。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def _repo_root() -> Path:
    """从测试文件位置上溯找仓根（禁硬编码 parents[N]——目录搬迁即静默指空）。"""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "scripts" / "session_worktree.py").exists():
            return parent
    raise RuntimeError(f"未从 {here} 上溯到含 scripts/session_worktree.py 的仓根")


_ROOT = _repo_root()
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "src"))

import session_worktree as sw  # noqa: E402

assert str(_ROOT) in str(sw.__file__), f"装载来源非本仓（假绿风险）: {sw.__file__}"


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    return out.stdout


def _worktree_face(repo: Path) -> dict[str, str]:
    """全 tracked 面现场指纹：{rel: 磁盘 blob sha}；另以 ls-files -s 记暂存态。"""
    files = _git(repo, "ls-files").splitlines()
    face: dict[str, str] = {}
    for rel in files:
        p = repo / rel
        face[rel] = (
            subprocess.run(
                ["git", "hash-object", "--", rel],
                cwd=str(repo),
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            ).stdout.strip()
            if p.is_file()
            else "<missing>"
        )
    face["<index>"] = _git(repo, "ls-files", "-s")
    return face


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """临时仓：dev 上 F.py 已推进 v2；主区盘面滞留 v1（staged 脏）＝序列化器落地后滞留形态。"""
    _git(tmp_path, "init", "-b", "dev", ".")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "config", "core.autocrlf", "false")
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "F.py").write_text("v1\n", encoding="utf-8")
    (tmp_path / "src" / "O.py").write_text("o1\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "base")
    # lane 自 base 分叉：改 F.py（与主区滞留盘面重叠）+ 新增 N.py
    _git(tmp_path, "checkout", "-b", "ai/lane/x")
    (tmp_path / "src" / "F.py").write_text("lane\n", encoding="utf-8")
    (tmp_path / "src" / "N.py").write_text("new\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "lane work")
    _git(tmp_path, "checkout", "dev")
    # dev 推进 F.py 到 v2（等价 6e05b4dc90 完整版已入 HEAD）
    (tmp_path / "src" / "F.py").write_text("v2\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "dev advance")
    # 主区盘面滞留：F.py 回写旧版 v1 并 staged（等价队列 CAS 落地后主区未收敛）
    (tmp_path / "src" / "F.py").write_text("v1\n", encoding="utf-8")
    _git(tmp_path, "add", "src/F.py")
    return tmp_path


def _run_cmd_merge(repo: Path, monkeypatch: pytest.MonkeyPatch, *, squash_mode: bool = False) -> int:
    (repo / ".worktrees" / "lane").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sw, "REPO_ROOT", repo)
    monkeypatch.setattr(sw, "WORKTREE_ROOT", repo / ".worktrees")
    monkeypatch.setattr(sw, "_worktree_path", lambda sid: repo / ".worktrees" / "lane")
    monkeypatch.setattr(sw, "_find_branch_for_session", lambda sid: "ai/lane/x")

    class _Args:
        session_id = "lane"
        to = "dev"
        squash = squash_mode
        yes = True
        allow_unchecked_merge = False

    return sw.cmd_merge(_Args())


def test_rejected_merge_leaves_worktree_byte_identical(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """红证主案（01:43:36 形态）：merge 被拒后工作树+暂存态与调用前逐字节一致。"""
    face_before = _worktree_face(repo)
    head_before = _git(repo, "rev-parse", "HEAD").strip()

    rc = _run_cmd_merge(repo, monkeypatch)

    assert rc == 1, f"脏面重叠 merge 应被 git 拒绝（rc={rc}）"
    assert _git(repo, "rev-parse", "HEAD").strip() == head_before, "被拒 merge 移动了 HEAD"
    face_after = _worktree_face(repo)
    assert face_after == face_before, (
        "被拒 merge 改写了工作树/暂存态（零副作用破防）: "
        "diff={k: (face_before.get(k), face_after.get(k)) for k in set(face_before) | set(face_after) if face_before.get(k) != face_after.get(k)}"
    )
    # merge 残留状态零遗留
    assert not (repo / ".git" / "MERGE_HEAD").exists(), "MERGE_HEAD 残留"
    # 主区滞留面原样保留：F.py 盘面=v1 且仍 staged
    assert (repo / "src" / "F.py").read_text(encoding="utf-8") == "v1\n"


def test_partially_applied_merge_failure_restores_bytes(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """注入失败：merge 子进程部分改写工作树后报败——恢复必须逐件还原调用前字节。"""
    face_before = _worktree_face(repo)
    head_before = _git(repo, "rev-parse", "HEAD").strip()
    real_run_git = sw._run_git

    def failing_merge_then_partial_write(args, cwd=None, check=True):  # noqa: ANN001
        if args and args[0] == "merge":
            # 模拟 ort 部分应用后失败（Windows 句柄占用形态）：N.py 已写入、F.py 被改写
            (repo / "src" / "N.py").write_text("new\n", encoding="utf-8")
            (repo / "src" / "F.py").write_text("lane\n", encoding="utf-8")
            return subprocess.CompletedProcess(args, 1, "", "Merge with strategy ort failed.\n")
        return real_run_git(args, cwd=cwd, check=check)

    monkeypatch.setattr(sw, "_run_git", failing_merge_then_partial_write)

    rc = _run_cmd_merge(repo, monkeypatch)

    assert rc == 1
    assert _git(repo, "rev-parse", "HEAD").strip() == head_before
    face_after = _worktree_face(repo)
    assert face_after == face_before, (
        "部分应用失败后未恢复: "
        "diff={k: (face_before.get(k), face_after.get(k)) for k in set(face_before) | set(face_after) if face_before.get(k) != face_after.get(k)}"
    )


def test_squash_commit_failure_restores_pre_state(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """squash merge 成功但手动 commit 失败＝本次合并未完成——现场必须恢复（零残留）。"""
    face_before = _worktree_face(repo)
    head_before = _git(repo, "rev-parse", "HEAD").strip()
    real_run_git = sw._run_git

    def squash_ok_commit_fail(args, cwd=None, check=True):  # noqa: ANN001
        if args and args[0] == "merge":
            # squash 语义：改写工作树+index、不建 commit、rc=0
            (repo / "src" / "F.py").write_text("lane\n", encoding="utf-8")
            (repo / "src" / "N.py").write_text("new\n", encoding="utf-8")
            return subprocess.CompletedProcess(args, 0, "", "")
        if args and args[0] == "commit":
            return subprocess.CompletedProcess(args, 1, "", "gate rejected\n")
        return real_run_git(args, cwd=cwd, check=check)

    monkeypatch.setattr(sw, "_run_git", squash_ok_commit_fail)

    rc = _run_cmd_merge(repo, monkeypatch, squash_mode=True)

    assert rc == 1, "squash 后 commit 失败必须判失败（旧版静默吞 rc）"
    assert _git(repo, "rev-parse", "HEAD").strip() == head_before
    face_after = _worktree_face(repo)
    assert face_after == face_before, (
        "squash commit 失败未恢复现场: "
        "diff={k: (face_before.get(k), face_after.get(k)) for k in set(face_before) | set(face_after) if face_before.get(k) != face_after.get(k)}"
    )


def test_success_path_triggers_no_restore(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """红线守卫：merge 成功路径语义零变化——恢复逻辑不得在成功分支运行。"""
    # 让 lane 落后于 dev（Already up to date 形态，merge rc=0 且零改动）；
    # 主区滞留脏面先清掉（-f 丢弃 tmp 仓脏面，仅为本测试准备干净 merge 前提）
    _git(repo, "reset", "--hard", "HEAD")
    _git(repo, "clean", "-fd")
    _git(repo, "checkout", "-f", "ai/lane/x")
    _git(repo, "reset", "--hard", "dev")
    _git(repo, "checkout", "-f", "dev")

    restore_calls: list[str] = []
    real_restore = sw._restore_merge_pre_state
    monkeypatch.setattr(
        sw,
        "_restore_merge_pre_state",
        lambda pre_state, *, reason: (restore_calls.append(reason), real_restore(pre_state, reason=reason))[1],
    )
    monkeypatch.setattr(sw, "cmd_abort_inner", lambda sid, **kw: 0)

    rc = _run_cmd_merge(repo, monkeypatch)

    assert rc == 0, f"干净 merge 应成功（rc={rc}）"
    assert restore_calls == [], f"成功路径触发了恢复动作: {restore_calls}"
