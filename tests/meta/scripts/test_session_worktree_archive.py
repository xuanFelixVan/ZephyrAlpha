# [MODULE] tests.scripts.test_session_worktree_archive
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] scripts.session_worktree (lane-archive), zephyr SessionRegistry
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 全部 git 操作在 tmp 仓；活跃会话硬拒无逃生；真 ahead 分支禁 -D（保留+台账）；dry-run 默认零副作用；存证授权必须覆盖 ③remove 且归档后必收栈、无存证表即零授权
# [MODIFY-GUARD]
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_session_worktree_archive.py — lane-archive 子命令单测（RB-4 车道生命周期治本）。

真源: docs/_working/root_cure_campaign/RB4_lane_lifecycle.md §2
测试组（tmp 仓三态 + 行为契约）:
- test_archive_shell_lane_zero_loss_execute: 纯壳（ahead=0 干净）→ remove+prune+branch -d 全过
- test_archive_real_ahead_keeps_branch_and_ledger: 真 ahead → worktree 删、分支保留（禁 -D）、白名单台账落盘
- test_archive_active_session_hard_reject: 活跃会话（registry 命中）→ 硬拒，车道与分支原样
- test_archive_dry_run_default_noop: 默认 dry-run → 只打印计划，worktree/脏文件原样、零 patch
- test_archive_dirty_lane_rescue_and_evidence: 脏车道 → patch 存证 + ？？入 rescue+mapping + 清理
- test_archive_resolves_by_branch_name: 分支名反查 porcelain 注册表
- test_archive_detached_lane: detached 车道（无分支）→ 清 worktree，跳过分支处置
- test_archive_tomb_authorization_spans_remove_phase: 脏车道存证授权跨段覆盖 ③remove，归档后收栈
- test_archive_without_evidence_carries_no_authorization: 无存证表 → remove 段零授权（fail-closed 反面）
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# scripts/ 非包目录，按路径加载被测模块（对标 tests/scripts/test_session_worktree_env.py 惯例）
_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "session_worktree.py"


def _load_module(repo: Path, monkeypatch: pytest.MonkeyPatch):
    """加载 session_worktree 并把 REPO_ROOT/WORKTREE_ROOT 重定向到给定临时仓。"""
    spec = importlib.util.spec_from_file_location("session_worktree_archive_under_test", _SCRIPT)
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
    """独立临时 git 仓（基线分支名对齐生产约定 dev）+ 模块 REPO_ROOT 重定向。"""
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


def _make_lane(repo: Path, sid: str, *, commit: bool = False, dirty_file: bool = False) -> Path:
    """在 tmp 仓创建测试车道（.worktrees/<sid> + session/<sid> 分支）。"""
    wt = repo / ".worktrees" / sid
    r = _git(repo, "worktree", "add", str(wt), "-b", f"session/{sid}")
    assert r.returncode == 0, f"worktree add 失败: {r.stderr}"
    if commit:
        (wt / "ahead.txt").write_text("ahead content\n", encoding="utf-8")
        r = subprocess.run(["git", "add", "-A"], cwd=wt, capture_output=True, text=True)
        assert r.returncode == 0
        r = subprocess.run(["git", "commit", "-m", f"lane {sid} unique work"], cwd=wt, capture_output=True, text=True)
        assert r.returncode == 0, f"worktree commit 失败: {r.stderr}"
    if dirty_file:
        (wt / "untracked.txt").write_text("dirty rescue me\n", encoding="utf-8")
    return wt


def _ns(mod, targets: list[str], *, execute: bool = False, **kw) -> argparse.Namespace:
    """构造 cmd_archive 的 argparse.Namespace（未传字段走 getattr 默认）。"""
    return argparse.Namespace(
        targets=targets,
        execute=execute,
        batch_file=kw.get("batch_file"),
        all=kw.get("all", False),
        skip_rescue=kw.get("skip_rescue", False),
        base=kw.get("base", "dev"),
        command="archive",
        func=mod.cmd_archive,
    )


def _branch_exists(repo: Path, branch: str) -> bool:
    return bool(_git(repo, "branch", "--list", branch).stdout.strip())


def test_archive_shell_lane_zero_loss_execute(tmp_repo):
    """纯壳（ahead=0 且干净）：execute → worktree remove+prune+branch -d 全过。"""
    mod, repo = tmp_repo
    sid = "st-shell"
    wt = _make_lane(repo, sid)
    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc == 0, "纯壳归档应成功"
    assert sid not in _git(repo, "worktree", "list").stdout, "worktree 仍注册"
    assert not _branch_exists(repo, f"session/{sid}"), "壳分支应被 -d 删除"
    assert not wt.exists(), "worktree 目录应消失"


def test_archive_real_ahead_keeps_branch_and_ledger(tmp_repo):
    """真 ahead：worktree 删、分支保留（禁 -D）、白名单台账落盘。"""
    mod, repo = tmp_repo
    sid = "st-ahead"
    _make_lane(repo, sid, commit=True)
    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc == 0, "真 ahead 车道归档主流程应成功"
    assert sid not in _git(repo, "worktree", "list").stdout, "worktree 仍注册"
    assert _branch_exists(repo, f"session/{sid}"), "真 ahead 分支必须保留（archive 路径禁 -D）"
    ledger = repo / ".runtime" / "quarantine" / "ahead_branches.log"
    assert ledger.exists(), "白名单台账未落盘"
    text = ledger.read_text(encoding="utf-8")
    assert sid in text and f"session/{sid}" in text, f"台账未含 sid/分支: {text!r}"
    assert "ahead=" in text, f"台账未含 ahead 数: {text!r}"


def test_archive_active_session_hard_reject(tmp_repo):
    """活跃会话（registry list_active 命中）：execute 硬拒，车道与分支原样，无逃生。"""
    mod, repo = tmp_repo
    sid = "st-active"
    wt = _make_lane(repo, sid, commit=True, dirty_file=True)
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    SessionRegistry(repo).register(sid, pid=os.getpid())  # 当前进程 pid 存活 → 判活
    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc != 0, "活跃会话必须硬拒（非零退出）"
    assert sid in _git(repo, "worktree", "list").stdout, "活跃 worktree 被动了！"
    assert wt.exists(), "活跃 worktree 目录被动了！"
    assert _branch_exists(repo, f"session/{sid}"), "活跃分支被动了！"
    assert (wt / "untracked.txt").exists(), "活跃车道脏文件被动了！"


def test_archive_dry_run_default_noop(tmp_repo):
    """默认 dry-run：只打印处置计划，worktree/脏文件原样、零 patch 零台账。"""
    mod, repo = tmp_repo
    sid = "st-dry"
    wt = _make_lane(repo, sid, dirty_file=True)
    rc = mod.cmd_archive(_ns(mod, [sid]))  # 不传 --execute
    assert rc == 0
    assert sid in _git(repo, "worktree", "list").stdout, "dry-run 动了 worktree 注册"
    assert (wt / "untracked.txt").exists(), "dry-run 动了脏文件"
    assert _branch_exists(repo, f"session/{sid}"), "dry-run 动了分支"
    q_dir = repo / ".runtime" / "quarantine"
    assert not q_dir.exists() or not list(q_dir.glob("*.patch")), "dry-run 生成了 patch"


def test_archive_dirty_lane_rescue_and_evidence(tmp_repo):
    """脏车道：patch 存证（含 tracked 修改）+ ？？入 rescue+mapping + 车道/壳分支清理。"""
    mod, repo = tmp_repo
    sid = "st-dirty"
    wt = _make_lane(repo, sid, dirty_file=True)
    (wt / "base.txt").write_text("modified tracked content\n", encoding="utf-8")
    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc == 0, "脏车道归档应成功"
    patches = list((repo / ".runtime" / "quarantine").glob(f"{sid}-retire-*.patch"))
    assert patches, "patch 存证未生成"
    assert "modified tracked content" in patches[0].read_text(encoding="utf-8"), "patch 未含 tracked 修改"
    rescue_dir = repo / ".runtime" / "tmp" / "rescue" / sid
    assert (rescue_dir / "untracked.txt").exists(), "？？文件未入 rescue"
    assert (rescue_dir / "untracked.txt").read_text(encoding="utf-8") == "dirty rescue me\n", "rescue 内容漂移"
    mapping = json.loads((rescue_dir / "mapping.json").read_text(encoding="utf-8"))
    assert "untracked.txt" in mapping["rescued"], f"mapping.json 缺条目: {mapping}"
    assert sid not in _git(repo, "worktree", "list").stdout
    assert not _branch_exists(repo, f"session/{sid}"), "ahead=0 壳分支应被 -d 删除"


def test_archive_resolves_by_branch_name(tmp_repo):
    """分支名反查 porcelain 注册表（输入=分支名而非 sid/path）。"""
    mod, repo = tmp_repo
    sid = "st-bybranch"
    _make_lane(repo, sid, commit=True)
    rc = mod.cmd_archive(_ns(mod, [f"session/{sid}"], execute=True))
    assert rc == 0
    assert sid not in _git(repo, "worktree", "list").stdout
    assert _branch_exists(repo, f"session/{sid}"), "真 ahead 分支应保留（禁 -D）"


def test_archive_detached_lane(tmp_repo):
    """detached 车道（无分支）：ahead 记 0，清 worktree、跳过分支处置。"""
    mod, repo = tmp_repo
    name = "dt-lane"
    wt = repo / ".aidrafts" / name
    r = _git(repo, "worktree", "add", "--detach", str(wt))
    assert r.returncode == 0, f"detached worktree add 失败: {r.stderr}"
    rc = mod.cmd_archive(_ns(mod, [name], execute=True))
    assert rc == 0, "detached 车道归档应成功"
    assert name not in _git(repo, "worktree", "list").stdout
    assert not wt.exists()


# 收班即清（Owner 2026-10-13 派工令 v2 段二第三条）：会话壳 .runtime/sessions/<sid>
# 随归档一起拆，不留给下一班。实测分母（主区当日）：497 壳＝108 空＋382 只剩心跳/pid
# 机制件＋7 有实质面——前三类可拆，最后一类必须保留并点名（在册红线：被清除面≠净收官）。
# ---------------------------------------------------------------------------


def _shell(repo: Path, sid: str, *rel_files: str) -> Path:
    d = repo / ".runtime" / "sessions" / sid
    d.mkdir(parents=True, exist_ok=True)
    for name in rel_files:
        (d / name).write_text("x\n", encoding="utf-8")
    return d


def test_prune_shell_empty_removed(tmp_repo):
    mod, repo = tmp_repo
    d = _shell(repo, "st-empty-shell")
    assert mod._prune_session_shell(repo, "st-empty-shell") is True
    assert not d.exists(), "空壳必须随收班拆掉"


def test_prune_shell_only_mechanical_files_removed(tmp_repo):
    """只剩心跳/PID（机制件）＝拆。这两件本就是本会话自己的活性 plumbing，注销后即无读者。"""
    mod, repo = tmp_repo
    d = _shell(repo, "st-hb-shell", "heartbeat.jsonl", "heartbeat_daemon.pid")
    assert mod._prune_session_shell(repo, "st-hb-shell") is True
    assert not d.exists()


def test_prune_shell_keeps_substantive_face(tmp_repo):
    """有实质面（staging 成果/keepalive 审计）＝保留不删，且一个字节都不许动。"""
    mod, repo = tmp_repo
    d = _shell(repo, "st-real-shell", "heartbeat.jsonl")
    (d / "staging").mkdir()
    (d / "staging" / "deliverable.md").write_text("成果未 promote\n", encoding="utf-8")
    assert mod._prune_session_shell(repo, "st-real-shell") is False
    assert d.exists() and (d / "staging" / "deliverable.md").exists(), "实质面被误删＝把第六态藏起来"
    assert (d / "heartbeat.jsonl").exists(), "保留态不得顺手删机制件（要么整壳走要么整壳留）"


def test_prune_shell_refuses_traversal_and_foreign_paths(tmp_repo):
    """谓词①②：sid 带分隔符/越出 sessions 层＝一律拒绝，且不得碰别的目录。"""
    mod, repo = tmp_repo
    victim = _shell(repo, "st-victim", "heartbeat.jsonl")
    assert mod._prune_session_shell(repo, "../st-victim") is False
    assert mod._prune_session_shell(repo, "a/b") is False
    assert mod._prune_session_shell(repo, "") is False
    assert victim.exists(), "拒绝对外越界时不得伤到在册壳"
    nested = repo / ".runtime" / "sessions" / "st-outer" / "st-inner"
    nested.mkdir(parents=True, exist_ok=True)
    (nested / "heartbeat.jsonl").write_text("x\n", encoding="utf-8")
    assert mod._prune_session_shell(repo, "st-outer/st-inner") is False
    assert nested.exists()


def test_prune_shell_missing_is_noop(tmp_repo):
    mod, repo = tmp_repo
    assert mod._prune_session_shell(repo, "st-never-existed") is False


def test_archive_execute_prunes_session_shell(tmp_repo):
    """端到端：归档通道跑完，会话壳（纯机制件）不该继续留在盘上。"""
    mod, repo = tmp_repo
    sid = "st-e2e-shell"
    _make_lane(repo, sid)
    d = _shell(repo, sid, "heartbeat.jsonl")
    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc == 0
    assert not d.exists(), "archive 之后壳仍在＝收班留给下一班（本次立法要堵的口）"


def _ops_guard_under_test(mod):
    """取被测代码**实际使用**的那份 ops_guard 模块（contextvar 只在同一模块实例上可读）。

    返回 None＝存证接线没有判别面，调用方按真红处理（禁 skip：环境性跳过会伪装成通过）。
    """
    factory = mod._tomb_ctx_factory()
    assert factory is not None, "ops_guard 导入失败＝存证授权面整块失效，不是环境噪声"
    return inspect.getmodule(factory)


def _spy_remove_phase(mod, monkeypatch) -> dict:
    """在 ③remove 的那一刻与紧随其后的 ⑤分支处置段各取一次样：授权读数 + 被删的是哪棵树。

    取样点必须落在 `_archive_one` 的**同一帧内**：CPython 引用计数会在该帧返回时把未收栈的
    context manager 关掉（生成器 GC 跑 finally），所以在测试末尾读到的永远是 None——"函数返回后
    再读"这种写法对"忘收栈"零判别力（M2 变异实测 9 全绿，就是这么被瞒过去的）。
    """
    real_remove = mod._archive_remove_and_verify
    real_branch = mod._archive_branch_finish
    og = _ops_guard_under_test(mod)
    seen: dict = {}

    def _spy_remove(wt_path: Path):
        seen["auth_during_remove"] = og.get_tomb_verification()
        seen["target"] = str(wt_path).replace("\\", "/")
        return real_remove(wt_path)

    def _spy_branch(*args, **kwargs):
        seen["auth_after_remove"] = og.get_tomb_verification()
        return real_branch(*args, **kwargs)

    monkeypatch.setattr(mod, "_archive_remove_and_verify", _spy_remove)
    monkeypatch.setattr(mod, "_archive_branch_finish", _spy_branch)
    return seen


def test_archive_tomb_authorization_spans_remove_phase(tmp_repo, monkeypatch):
    """脏车道：①b 存证表的授权必须一路覆盖 ③remove，归档完收栈。

    OPS-GUARD 真正拦死的是"删整棵 .worktrees/<sid>"命中保护区判据（不是搬文件），
    所以 ctx 在 rescue 末尾就 __exit__ ＝ 四棵卡死车道一条命令仍退不了场（维护七班 P1-6
    调用侧接线；死信班终报实证"缺的只是那一行"）。
    """
    mod, repo = tmp_repo
    sid = "st-span"
    wt = _make_lane(repo, sid, dirty_file=True)
    (wt / "base.txt").write_text("modified tracked content\n", encoding="utf-8")

    og = _ops_guard_under_test(mod)
    assert og.get_tomb_verification() is None, "基线：进测试前不得有残留授权"
    seen = _spy_remove_phase(mod, monkeypatch)

    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc == 0, "脏车道归档应成功"
    auth = seen.get("auth_during_remove")
    assert auth is not None, "③remove 时无存证授权＝接线断在 rescue 末尾（死锁原样复现）"
    manifest_path, rows = auth
    assert Path(manifest_path).exists(), f"授权指向的存证表不存在: {manifest_path}"
    assert rows, "存证表零合格行＝授权无面，ops_guard 侧不会放行"
    assert seen["target"].endswith(f".worktrees/{sid}"), f"取样点不在被删的车道树上: {seen}"
    assert not wt.exists(), "车道树应已删除"
    assert "auth_after_remove" in seen, "⑤分支处置段没被跑到＝收栈面是空的"
    assert seen["auth_after_remove"] is None, "删除段之后仍带授权＝收栈点没落在 remove 之后（悬挂豁免）"
    assert og.get_tomb_verification() is None, "整条归档返回后不得有残留授权（防泄漏到下一次删除）"


def test_archive_without_evidence_carries_no_authorization(tmp_repo, monkeypatch):
    """反面对照：干净壳车道没有存证表 → ③remove 段必须零授权（接线不得变成无条件放行）。"""
    mod, repo = tmp_repo
    sid = "st-noauth"
    wt = _make_lane(repo, sid)

    og = _ops_guard_under_test(mod)
    seen = _spy_remove_phase(mod, monkeypatch)

    rc = mod.cmd_archive(_ns(mod, [sid], execute=True))
    assert rc == 0, "壳车道归档应成功"
    assert "target" in seen, "remove 段没被跑到＝对照面是空的"
    assert seen["auth_during_remove"] is None, "无存证表却有授权＝放宽了判据（应为 fail-closed）"
    assert seen.get("auth_after_remove") is None
    assert not wt.exists()
    assert og.get_tomb_verification() is None
