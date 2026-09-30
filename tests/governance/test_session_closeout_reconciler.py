# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] tests.governance.test_session_closeout_reconciler
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] tmp_path 全隔离（monkeypatch 注入证据采集函数+tmp git 仓），生产盘零触碰；判死四门/豁免面/动作分级行为对齐 RB3_session_closeout.md §4
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即判死/豁免/动作分级漂移证据（含 sid 与门描述）
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RB-3 会话收尾协调器（session_closeout_reconciler）行为测试.

三态覆盖（设计文档 §5.3）：a) 死会话+claim+staged（==HEAD 清 index / ≠HEAD stash 归档）；
b) 心跳死但 PID 活→零动作；c) 死会话+MERGE_HEAD 归属→只告警。另覆盖在飞队列豁免、
logical/白名单豁免、2 轮 strikes 状态机、归档幂等可逆、shadow 默认与 fail-safe。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.governance._tasks import session_closeout_reconciler as scr  # noqa: E402

SID = "st-dead-20260929"
# 锚定真实时钟（lock_files._alive_sessions 内部用 wall clock 判活——合成未来时间戳会判活反转）
NOW = time.time()


# ============== 夹具 ==============


def _write_raw_registry(root: Path, entries: dict) -> None:
    reg = root / ".runtime" / "session_registry.json"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")


def _dead_entry(sid: str = SID) -> dict:
    """pid=0 且心跳远超 90s 的死条目（_is_session_alive 纯函数判死，无需进程真源）。"""
    return {
        "session_id": sid,
        "pid": 0,
        "start_time": NOW - 7200,
        "held_files": [],
        "last_heartbeat": NOW - 10_000,
        "last_activity": NOW - 10_000,
    }


def _mk_session_dir(root: Path, sid: str = SID) -> Path:
    d = root / ".runtime" / "sessions" / sid
    d.mkdir(parents=True, exist_ok=True)
    (d / "notes.txt").write_text("session artifacts", encoding="utf-8")
    return d


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """全隔离环境：tmp 仓根 + 证据采集函数全量 monkeypatch（生产盘零触碰）。"""
    root = tmp_path
    _write_raw_registry(root, {SID: _dead_entry()})
    _mk_session_dir(root)
    monkeypatch.setattr(scr, "_active_session_ids", lambda _root: set())  # gate1：全员不在活跃集
    monkeypatch.setattr(scr, "_index_locked", lambda _root: False)
    monkeypatch.setattr(scr, "_queue_inflight_sids", lambda _root: set())
    monkeypatch.setattr(scr, "_load_keep_sids", lambda _root: set())
    monkeypatch.setattr(
        scr,
        "_session_claims",
        lambda _root, sid: (
            {f"src/{sid}.py": {"owner_id": sid, "expires_at": NOW - 100, "pid": 0}} if sid == SID else {}
        ),
    )
    monkeypatch.setattr(scr, "_all_claim_owners", lambda _root: {SID})
    # 双登记处释放打桩（lock_files 全局锁根指向生产 .ailocks——execute 态测试绝不触碰）
    monkeypatch.setattr("scripts.lock_files._force_release_locks", lambda sid, paths: sorted(paths))
    monkeypatch.setattr("scripts.lock_files._force_release_session_registry", lambda *a, **k: [])
    return root


def _run(root: Path, *, execute: bool = False, now: float = NOW):
    return scr.run_cycle(root, now=now, execute=execute)


# ============== a) 死会话 + claim + staged：RB1 判型（真实 tmp git 仓） ==============


def _init_git_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"], ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, cwd=root, capture_output=True, check=True)
    (root / "a.txt").write_text("head-version\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=root, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=root, capture_output=True, check=True)


def _claim_paths(sid: str, paths: list[str]) -> dict:
    return {p: {"owner_id": sid, "expires_at": NOW - 100, "pid": 0} for p in paths}


@pytest.fixture
def git_env(env: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, list[str]]:
    """在 env 上叠真实 git 仓 + 死会话 staged 双件：a.txt==HEAD（残影）、b.txt≠HEAD（WIP）。"""
    _init_git_repo(env)
    (env / "a.txt").write_text("dead-session-edit\n", encoding="utf-8")  # staged 版本≠HEAD
    (env / "b.txt").write_text("wip-new-file\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt", "b.txt"], cwd=env, capture_output=True, check=True)
    (env / "a.txt").write_text("head-version\n", encoding="utf-8")  # worktree 回写 HEAD 版 → ==HEAD
    claims = _claim_paths(SID, ["a.txt", "b.txt"])
    monkeypatch.setattr(scr, "_session_claims", lambda _root, sid: claims if sid == SID else {})
    released: list[str] = []
    monkeypatch.setattr(
        "scripts.lock_files._force_release_locks", lambda sid, paths: released.extend(paths) or sorted(paths)
    )
    return env, released


def test_dead_session_rb1_unstage_and_stash_then_reversible(
    git_env: tuple[Path, list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """a) 判死四门全过+实弹：==HEAD 清 index 残影、≠HEAD stash 可 pop、双登记处释放、目录归档、第二轮幂等零动作。"""
    git_root, released = git_env
    first = _run(git_root, now=NOW)
    assert first["suspected"] and not first["confirmed"]  # 首轮只留观
    second = _run(git_root, execute=True, now=NOW + 1200)  # 第二轮 strikes=2 → confirmed（20min∈视界）
    assert SID in second["confirmed"]
    assert second["mode"] == "live"

    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=git_root, capture_output=True, text=True
    ).stdout.split()
    assert staged == [], "==HEAD/≠HEAD 件均应离开 index（==HEAD reset；≠HEAD stash push 同步卸载）"
    stash = subprocess.run(["git", "stash", "list"], cwd=git_root, capture_output=True, text=True).stdout
    assert f"{scr._STASH_MSG_PREFIX} {SID}" in stash
    # 可逆：stash pop 恢复 WIP 内容
    subprocess.run(["git", "stash", "pop", "-q"], cwd=git_root, capture_output=True, check=True)
    assert (git_root / "b.txt").read_text(encoding="utf-8") == "wip-new-file\n"
    assert released == ["a.txt", "b.txt"]
    # 级②：会话目录归档（可逆 mv）
    archive = list((git_root / ".runtime" / "sessions_archive").glob(f"*/{SID}"))
    assert archive and archive[0].is_dir() and not (git_root / ".runtime" / "sessions" / SID).exists()
    # 告警 jsonl 与 state 账落盘（tmp 内）
    alert = git_root / ".runtime" / "logs" / "session_closeout_alert.jsonl"
    assert alert.exists() and SID in alert.read_text(encoding="utf-8")
    state = json.loads((git_root / ".runtime" / "session_closeout" / "state.json").read_text(encoding="utf-8"))
    assert state["archived"][SID]["dest"]
    # 幂等轮：claim 已真实释放、条目已 reap → 零动作零嫌疑
    _write_raw_registry(git_root, {})
    monkeypatch.setattr(scr, "_session_claims", lambda _root, sid: {})
    monkeypatch.setattr(scr, "_all_claim_owners", lambda _root: set())
    third = scr.run_cycle(git_root, now=NOW + 2400, execute=True)
    assert third["confirmed"] == [] and third["actions"] == {}


def test_shadow_default_zero_action(env: Path) -> None:
    """默认 shadow：只判只记，index/工作树/目录零触碰，记录 would 动作。"""
    _init_git_repo(env)
    (env / "c.txt").write_text("wip\n", encoding="utf-8")
    subprocess.run(["git", "add", "c.txt"], cwd=env, capture_output=True, check=True)
    _run(env, now=NOW)
    s2 = _run(env, execute=False, now=NOW + 1200)
    assert s2["mode"] == "shadow" and SID in s2["confirmed"]
    assert s2["actions"][SID].get("would_level1_claims") == 1
    assert (
        "c.txt"
        in subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=env, capture_output=True, text=True).stdout
    )
    assert (env / ".runtime" / "sessions" / SID).is_dir()  # 未归档


# ============== b/c/豁免面 ==============


def test_pid_alive_session_untouched(env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """b) 心跳死但 PID 活→在场一票否决，零动作零嫌疑。"""
    monkeypatch.setattr(scr, "_pid_present_sessions", lambda _raw: {SID})
    s = _run(env, now=NOW)
    assert s["confirmed"] == [] and s["suspected"] == []
    assert any(k.endswith(":gate") and "pid-alive" in v for k, v in s["skipped"].items())
    assert (env / ".runtime" / "sessions" / SID).is_dir()


def test_merge_head_attributed_warn_only(env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """c) MERGE_HEAD 归属死会话→只告警：禁 abort、禁 claim/stash 动作、禁归档。"""
    (env / ".git").mkdir(parents=True, exist_ok=True)
    mh = env / ".git" / "MERGE_HEAD"
    mh.write_text("0" * 40, encoding="utf-8")
    # 活动窗：start=NOW-20000，activity=NOW-10000 → mtime=NOW-15000 落在 [start-grace, act+grace]
    entry = _dead_entry()
    entry["start_time"] = NOW - 20_000
    _write_raw_registry(env, {SID: entry})
    os.utime(mh, (NOW - 15_000, NOW - 15_000))
    monkeypatch.setattr(scr, "_session_claims", lambda _root, sid: {})
    monkeypatch.setattr(scr, "_all_claim_owners", lambda _root: set())
    state = env / ".runtime" / "session_closeout" / "state.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(
        json.dumps({"version": 1, "suspects": {SID: {"strikes": 1, "first_seen": NOW - 1200}}}), encoding="utf-8"
    )
    s = scr.run_cycle(env, now=NOW, execute=True)
    assert s["merge_warned"] and s["merge_warned"][0]["sid"] == SID
    assert all(not v for v in s["actions"].values())  # 归属→只告警，零实际动作
    assert mh.exists()  # 禁 abort
    assert (env / ".runtime" / "sessions" / SID).is_dir()  # 不归档


def test_queue_inflight_exempt(env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """在飞提交队列豁免：本轮缩手，等袋落完。"""
    monkeypatch.setattr(scr, "_queue_inflight_sids", lambda _root: {SID})
    s = _run(env, now=NOW)
    assert f"{SID}:queue_inflight" in s["skipped"] and not s["suspected"]


def test_logical_and_whitelist_exempt(env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """logical=True（W-29）与 keep 白名单永不收尾。"""
    entry = _dead_entry()
    entry["logical"] = True
    _write_raw_registry(env, {SID: entry})
    s = scr.run_cycle(env, now=NOW, execute=True)
    assert f"{SID}:logical" in s["skipped"]
    _write_raw_registry(env, {SID: _dead_entry()})
    monkeypatch.setattr(scr, "_load_keep_sids", lambda _root: {SID})
    s2 = scr.run_cycle(env, now=NOW, execute=True)
    assert f"{SID}:whitelist" in s2["skipped"]


def test_orphan_dir_archive_by_mtime(env: Path) -> None:
    """无注册表条目的孤儿垃圾目录：mtime>7d 归档；新目录保留。"""
    old = env / ".runtime" / "sessions" / "--help"
    old.mkdir(parents=True, exist_ok=True)
    os.utime(old, (NOW - 8 * 86400, NOW - 8 * 86400))
    fresh = env / ".runtime" / "sessions" / "sess-pytest-pool-A"
    fresh.mkdir(parents=True, exist_ok=True)
    os.utime(fresh, (NOW - 60, NOW - 60))
    s = scr.run_cycle(env, now=NOW, execute=True)
    assert "--help" in s["confirmed"] and s["actions"]["--help"].get("archived")
    assert not old.exists()
    assert "sess-pytest-pool-A" not in s["confirmed"] and fresh.is_dir()


def test_index_locked_round_shrink(env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """index.lock 在飞→整轮缩手（A1 加固②同款）。"""
    monkeypatch.setattr(scr, "_index_locked", lambda _root: True)
    s = _run(env, now=NOW)
    assert any(k.startswith("round:index_locked") for k in s["skipped"]) and not s["confirmed"]


def test_registry_unreachable_fail_safe(env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """registry 不可达→本轮零动作+error（fail-safe 偏向不动作）。"""
    monkeypatch.setattr(scr, "_active_session_ids", lambda _root: None)
    s = _run(env, now=NOW)
    assert "registry-unreachable" in s["errors"] and not s["confirmed"]


def test_strike_reset_on_revive(env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """「连续」语义：中间一轮活过来（进活跃集）→ strikes 清零，重新计数。"""
    _run(env, now=NOW)  # strikes=1
    monkeypatch.setattr(scr, "_active_session_ids", lambda _root: {SID})  # 复活
    s = scr.run_cycle(env, now=NOW + 1200, execute=False)
    assert not s["confirmed"]
    monkeypatch.setattr(scr, "_active_session_ids", lambda _root: set())  # 再死
    s2 = scr.run_cycle(env, now=NOW + 2400, execute=False)
    assert s2["suspected"] and not s2["confirmed"]  # 从 1 重新起算
