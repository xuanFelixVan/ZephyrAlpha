# [A_test] test_id=G1-R10-20260918 | module=scripts/lock_files.py | gate=pytest
# [BLUEPRINT] MOD-INF-005 | scripts/lock_files.py | §R-10 死会话遗物回收
# [TESTS] self
# [TTL] task_bound
"""R-10 死会话遗物回收验收钉（lane G1，2026-09-18；真源 S18 根因表 R-10 行）。

覆盖验收矩阵：
1. 活会话不误收——证据①缺一（registry 活 + claim 过期）不动；证据②缺一
   （registry 死 + claim 新鲜）不动（防误收活会话=S18 R-10 反例红线）。
2. 死会话双证齐全 → 三件套回收：MERGE_HEAD abort + stash 归档 + claim 释放
   （.ailocks + SessionRegistry 两登记处）。
3. 无 MERGE_HEAD 时幂等（二次运行无副作用无报错）。
4. stash 归档可 pop 恢复（禁丢弃）。
5. MERGE_HEAD 归属不明（有先于 merge 的存活会话）→ 不 abort。
6. dry-run 只判证不动手。
7. cmd_cleanup 自动回收集成（含零 claim 纯 SessionRegistry 遗物形态）。

隔离纪律：全部用 tmp_path + git init 临时仓，禁碰真仓 git 状态。
模块路径默认指向 scripts/lock_files.py 本体；落地前验证用
ZEPHYR_G1_SURGERY_LOCK_FILES 环境变量指向 .runtime/tmp/surgery/ 镜像。
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
# 镜像 bootstrap 的 _PROJECT_ROOT 指向 surgery 目录（找不到真仓 d3_metadata）——
# 预置真仓 scripts/governance/d3_metadata 到 sys.path，使镜像模块级 import 可解析
_D3_METADATA = _REPO / "scripts" / "governance" / "d3_metadata"
if str(_D3_METADATA) not in sys.path:
    sys.path.insert(0, str(_D3_METADATA))

_LOCK_FILES_PATH = Path(
    os.environ.get("ZEPHYR_G1_SURGERY_LOCK_FILES", str(_REPO / "scripts" / "lock_files.py"))
)


def _load_lock_files():
    """按 env 覆盖加载 lock_files（落地前=镜像，落地后=本体）。"""
    spec = importlib.util.spec_from_file_location("lock_files_g1", _LOCK_FILES_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["lock_files_g1"] = mod  # dataclass 处理等按 __module__ 反查 sys.modules
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def lf(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """加载被测 lock_files 并把锁库隔离到 tmp；git tracked 判定打桩（防碰真仓）。"""
    mod = _load_lock_files()
    monkeypatch.setattr(mod, "LOCK_ROOT", tmp_path / ".ailocks")
    monkeypatch.setattr(mod, "REGISTRY_PATH", tmp_path / ".ailocks" / "registry.json")
    monkeypatch.setattr(mod, "_is_git_tracked", lambda _p: True)
    return mod


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True, timeout=60,
    )
    if check and r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {r.stderr}")
    return r


@pytest.fixture()
def tmp_git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "g1@test.local")
    _git(repo, "config", "user.name", "g1-test")
    # .runtime/.ailocks 是运行时状态，与真仓 hygiene 一致——禁入 git index
    # （否则 session_registry.json 进出 index 会让 merge --abort 撞 "not uptodate"）
    (repo / ".gitignore").write_text(".runtime/\n.ailocks/\n", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "x.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "src" / "y.py").write_text("y = 1\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "init")
    return repo


def _register_session(repo: Path, sid: str, *, pid: int) -> None:
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    SessionRegistry(repo).register(sid, pid=pid)


def _backdate_session(
    repo: Path,
    sid: str,
    *,
    heartbeat_age: float,
    activity_age: float,
    start_age: float = 7200.0,
) -> None:
    """把会话条目改造成指定死亡/活性形态（raw load/save，无 list_active 副作用）。"""
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    reg = SessionRegistry(repo)
    data = reg.load()
    now = time.time()
    data[sid]["last_heartbeat"] = now - heartbeat_age
    data[sid]["last_activity"] = now - activity_age
    data[sid]["start_time"] = now - start_age
    reg.save(data)


def _make_dead_session(repo: Path, sid: str) -> None:
    """pid=0 逻辑会话 + 心跳 1h 前（>90s 超时判死）；最后活动 60s 前。"""
    _register_session(repo, sid, pid=0)
    _backdate_session(repo, sid, heartbeat_age=3600.0, activity_age=60.0)


def _make_dead_session_with_held(repo: Path, sid: str, held: list[str]) -> None:
    """死会话 + SessionRegistry 侧 held_files（先 claim 再回拨——
    对已死条目 claim 会触发懒注册复活心跳，顺序不可反）。"""
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    _register_session(repo, sid, pid=0)
    SessionRegistry(repo).claim_files_batch(sid, held)
    _backdate_session(repo, sid, heartbeat_age=3600.0, activity_age=60.0)


def _claim(lf, rel: str, owner: str, *, ttl_minutes: float = 30.0) -> None:
    rc = lf.cmd_acquire(rel, owner, lf.AcquireOptions(skip_naming_check=True, ttl_minutes=ttl_minutes))
    assert rc == 0, f"claim {rel} failed"


def _expire_claim(lf, rel: str) -> None:
    """把 claim 的 expires_at 回拨为已过期（owner.json + registry.json 两处）。"""
    owner_file = lf._owner_file(lf._lock_dir(rel))
    owner = json.loads(owner_file.read_text(encoding="utf-8"))
    owner["expires_at"] = time.time() - 100
    owner_file.write_text(json.dumps(owner, ensure_ascii=False), encoding="utf-8")
    registry = json.loads(lf.REGISTRY_PATH.read_text(encoding="utf-8"))
    registry["locks"][rel]["expires_at"] = time.time() - 100
    lf.REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")


def _make_merge_head(repo: Path) -> None:
    """制造冲突 merge → 主区 MERGE_HEAD 晾置。"""
    _git(repo, "checkout", "-b", "feature")
    (repo / "src" / "x.py").write_text("x = 2  # feature\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feature change")
    _git(repo, "checkout", "main")
    (repo / "src" / "x.py").write_text("x = 3  # main\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "main change")
    r = _git(repo, "merge", "--no-ff", "feature", check=False)
    assert r.returncode != 0
    assert (repo / ".git" / "MERGE_HEAD").is_file()


def _registry_locks(lf) -> dict:
    return json.loads(lf.REGISTRY_PATH.read_text(encoding="utf-8")).get("locks", {})


def _run(func, *args, **kwargs) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = func(*args, **kwargs)
    return rc, buf.getvalue()


# ── 1a. 证据①缺一：registry 显示存活 + claim 已过期 → 不回收 ──
def test_alive_session_not_salvaged(lf, tmp_git_repo: Path) -> None:
    sid = "sess-alive"
    _register_session(tmp_git_repo, sid, pid=os.getpid())  # 活：PID 活 + 心跳新鲜
    _claim(lf, "src/x.py", sid)
    _expire_claim(lf, "src/x.py")

    res = lf.salvage_dead_session(sid, repo_root=tmp_git_repo)

    assert res.dead_confirmed is False
    assert res.evidence1 == "registry:alive"
    assert "双证不齐全" in res.notes[0]
    assert "src/x.py" in _registry_locks(lf)  # claim 原样保留
    assert lf._lock_dir("src/x.py").is_dir()


# ── 1b. 证据②缺一：会话已死 + claim 新鲜未过期 → 不回收 ──
def test_dead_session_with_fresh_claims_not_salvaged(lf, tmp_git_repo: Path) -> None:
    sid = "sess-dead-fresh"
    _make_dead_session(tmp_git_repo, sid)
    _claim(lf, "src/x.py", sid, ttl_minutes=30.0)  # 新鲜 claim

    res = lf.salvage_dead_session(sid, repo_root=tmp_git_repo)

    assert res.dead_confirmed is False
    assert res.evidence1 == "registry:dead"
    assert "0/1 expired" in res.evidence2
    assert "src/x.py" in _registry_locks(lf)


# ── 2. 双证齐全 → 三件套齐全回收（merge abort + stash + 两登记处释放）──
def test_dead_session_full_salvage_three_piece(lf, tmp_git_repo: Path) -> None:
    sid = "sess-dead-full"
    _make_merge_head(tmp_git_repo)
    # 死会话遗物：x.py 卷入 merge 冲突；y.py 有未卷入 merge 的 WIP 改动
    (tmp_git_repo / "src" / "y.py").write_text("y = 2  # wip\n", encoding="utf-8")
    _claim(lf, "src/x.py", sid)
    _claim(lf, "src/y.py", sid)
    _expire_claim(lf, "src/x.py")
    _expire_claim(lf, "src/y.py")
    # 死会话（含 SessionRegistry 侧第二登记处持有；先 claim 再回拨防懒注册复活）
    _make_dead_session_with_held(tmp_git_repo, sid, ["src/x.py"])

    res = lf.salvage_dead_session(sid, repo_root=tmp_git_repo)

    assert res.dead_confirmed is True
    # ① MERGE_HEAD abort
    assert res.merge_abort == "aborted"
    assert res.merge_head_sha  # 留痕
    assert not (tmp_git_repo / ".git" / "MERGE_HEAD").exists()
    # ② stash 归档（y.py 的 WIP 未卷入 merge，abort 后幸存并被归档）
    assert res.stash_ref
    assert any("y.py" in p for p in res.stashed_paths)
    out = _git(tmp_git_repo, "status", "--porcelain").stdout
    assert "y.py" not in out  # 工作区已清静
    # ③ claim 双登记处释放
    assert sorted(res.released_locks) == ["src/x.py", "src/y.py"]
    assert _registry_locks(lf) == {}
    assert not lf._lock_dir("src/x.py").is_dir()
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    assert sid not in SessionRegistry(tmp_git_repo).load()  # 条目注销
    # 审计留痕
    audit = lf.LOCK_ROOT / "salvage_audit.jsonl"
    assert audit.is_file()
    last = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert last["action"] == "salvage" and last["session_id"] == sid


# ── 3. 无 MERGE_HEAD 幂等 + 二次运行无副作用 ──
def test_salvage_idempotent_without_merge_head(lf, tmp_git_repo: Path) -> None:
    sid = "sess-dead-plain"
    _make_dead_session(tmp_git_repo, sid)
    (tmp_git_repo / "src" / "x.py").write_text("x = 9  # wip\n", encoding="utf-8")
    _claim(lf, "src/x.py", sid)
    _expire_claim(lf, "src/x.py")

    res = lf.salvage_dead_session(sid, repo_root=tmp_git_repo)
    assert res.dead_confirmed is True
    assert res.merge_abort == "skipped"  # 无 merge，幂等跳过
    assert res.stash_ref  # WIP 已归档

    res2 = lf.salvage_dead_session(sid, repo_root=tmp_git_repo)
    # 会话已注销 + claim 已空 → 无任何死亡证据 → 整体不动（幂等无报错）
    assert res2.dead_confirmed is False
    assert _registry_locks(lf) == {}


# ── 4. stash 归档可 pop 恢复（禁丢弃）──
def test_stash_archive_poppable(lf, tmp_git_repo: Path) -> None:
    sid = "sess-dead-stash"
    _make_dead_session(tmp_git_repo, sid)
    (tmp_git_repo / "src" / "x.py").write_text("x = 42  # salvaged-wip\n", encoding="utf-8")
    _claim(lf, "src/x.py", sid)
    _expire_claim(lf, "src/x.py")

    res = lf.salvage_dead_session(sid, repo_root=tmp_git_repo)
    assert res.stash_ref

    lst = _git(tmp_git_repo, "stash", "list").stdout
    assert f"dead-session salvage {sid}" in lst
    _git(tmp_git_repo, "stash", "pop")
    assert (tmp_git_repo / "src" / "x.py").read_text(encoding="utf-8") == "x = 42  # salvaged-wip\n"


# ── 5. MERGE_HEAD 归属不明（有先于 merge 的存活会话）→ 不 abort，claim 仍释放 ──
def test_merge_head_not_attributed_when_alive_session_predates(lf, tmp_git_repo: Path) -> None:
    sid = "sess-dead-merge"
    _make_dead_session(tmp_git_repo, sid)
    _make_merge_head(tmp_git_repo)
    _claim(lf, "src/x.py", sid)
    _expire_claim(lf, "src/x.py")
    # 另一个存活会话，注册时间早于 merge → merge 可能归它 → 拒 abort
    other = "sess-alive-owner"
    _register_session(tmp_git_repo, other, pid=os.getpid())
    _backdate_session(tmp_git_repo, other, heartbeat_age=0.0, activity_age=0.0, start_age=7200.0)

    res = lf.salvage_dead_session(sid, repo_root=tmp_git_repo)

    assert res.dead_confirmed is True
    assert res.merge_abort == "not_attributed"
    assert (tmp_git_repo / ".git" / "MERGE_HEAD").is_file()  # 原样保留
    assert any("归属不明" in n for n in res.notes)
    assert _registry_locks(lf) == {}  # claim 释放独立成立
    _git(tmp_git_repo, "merge", "--abort")  # 测试收尾（tmp 仓）


# ── 6. dry-run 只判证不动手 ──
def test_dry_run_touches_nothing(lf, tmp_git_repo: Path) -> None:
    sid = "sess-dead-dry"
    _make_dead_session(tmp_git_repo, sid)
    _make_merge_head(tmp_git_repo)
    _claim(lf, "src/x.py", sid)
    _expire_claim(lf, "src/x.py")

    res = lf.salvage_dead_session(sid, repo_root=tmp_git_repo, dry_run=True)

    assert res.dead_confirmed is True
    assert res.merge_abort == "dry-run"
    assert (tmp_git_repo / ".git" / "MERGE_HEAD").is_file()  # 未动
    assert "src/x.py" in _registry_locks(lf)  # 未释放
    _git(tmp_git_repo, "merge", "--abort")


# ── 7. cmd_cleanup 自动回收：零 claim 纯 SessionRegistry 遗物形态 ──
def test_cleanup_auto_salvage_registry_only_relic(lf, tmp_git_repo: Path) -> None:
    sid = "sess-dead-registry-only"
    _make_dead_session_with_held(tmp_git_repo, sid, ["src/x.py"])

    rc, out = _run(lf.cmd_cleanup, repo_root=tmp_git_repo)

    assert rc == 0
    assert "SALVAGED" in out
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    assert sid not in SessionRegistry(tmp_git_repo).load()


# ── 8. CLI 面：cmd_salvage 退出码与 dry-run ──
def test_cmd_salvage_cli_exit_codes(lf, tmp_git_repo: Path) -> None:
    sid = "sess-dead-cli"
    _make_dead_session(tmp_git_repo, sid)
    _claim(lf, "src/x.py", sid)
    _expire_claim(lf, "src/x.py")

    rc, out = _run(lf.cmd_salvage, sid, dry_run=True, repo_root=tmp_git_repo)
    assert rc == 0
    payload = json.loads(out)
    assert payload["dead_confirmed"] is True
    assert "src/x.py" in _registry_locks(lf)  # dry-run 未释放

    rc, _ = _run(lf.cmd_salvage, sid, repo_root=tmp_git_repo)
    assert rc == 0
    assert _registry_locks(lf) == {}

    # 活会话：exit 1 且不动
    alive = "sess-alive-cli"
    _register_session(tmp_git_repo, alive, pid=os.getpid())
    _claim(lf, "src/y.py", alive)
    rc, _ = _run(lf.cmd_salvage, alive, repo_root=tmp_git_repo)
    assert rc == 1
    assert "src/y.py" in _registry_locks(lf)


def test_cleanup_no_salvage_flag_skips(lf, tmp_git_repo: Path) -> None:
    sid = "sess-dead-nosalvage"
    _make_dead_session_with_held(tmp_git_repo, sid, ["src/x.py"])

    rc, out = _run(lf.cmd_cleanup, repo_root=tmp_git_repo, auto_salvage=False)

    assert rc == 0
    assert "SALVAGED" not in out
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    assert sid in SessionRegistry(tmp_git_repo).load()

