# [A_test] module_id: MOD-TEST-TAKEOVER-PID-FALSEPOS | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.session.test_takeover_pid_false_positive
# [DOMAIN] D_AUTONOMY_CORE
# [INVARIANTS] 红证件（st-maint1-t3lane-20261010，T3 判据治疗班）——PID 亡＝必要非充分：
#              pid>0 条目判死/开 TAKEOVER 案前必须过"三证旁证"（①心跳文件新鲜且末行非
#              exited ②队列在途/新袋 ③分支真实写入痕迹）。本件三条正例（判活/不开账/
#              verdict 非 PID-DEAD）在**未修码上必红**；反例（真死会话仍判死开账）
#              在修码前后都必须绿——防把闸拆成恒活。全部 tmp_path，禁写生产 .runtime。
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound
"""test_takeover_pid_false_positive.py — 接管闸"只看 PID 不看心跳"误判死红蓝证。

今日三案实证（st-govjudge/st-backfix/st-datalane-20261010）：注册 PID 位被**瞬时
git_commit/CLI 进程**占住（claim_file 懒注册以 os.getpid() 重建条目），进程一退
`_is_session_alive`/`_salvage_takeover_ledger`/`liveness_verdict` 三处判死轨
零宽限判死 → 接管台账 open → TAKEOVER-PENDING 咬住活会话自己的提交。

本件按任务书立法钉三处落点的行为契约：
1. `_is_session_alive()`：PID 亡先过三证，任一为真→判活（并把用了哪一证结构化返回）；
2. `_salvage_takeover_ledger()`：`_pid_dead` 单独不得立案，须"PID 亡 **且** 三证全空"；
3. `liveness_verdict()`：P1（TAKEOVER-PENDING）/P4（PID-DEAD）判死前须消费心跳文件。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from zephyr.security.access_control.session_concurrency import (
    _HEARTBEAT_TIMEOUT_SECONDS,
    _REAP_GRACE_SECONDS,
    SessionInfo,
    SessionRegistry,
    _is_session_alive,
    liveness_verdict,
)
from zephyr.shared.infra.process_pool import is_pid_alive

SID = "sess-fp-takeover"
LEDGER_REL = ".runtime/takeover_ledger.jsonl"


# ---------------------------------------------------------------------------
# fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def lane_root(tmp_path, monkeypatch):
    """隔离仓根：anchor_main_root 打桩为恒等（禁 subprocess git 解析）+ cwd 落入 tmp。"""
    import zephyr.security.access_control.session_concurrency as sc

    monkeypatch.setattr(sc, "anchor_main_root", lambda p: Path(p))
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ZEPHYR_COMMIT_QUEUE_DIR", raising=False)
    return tmp_path


def confirmed_dead_pid() -> int:
    """起一个立即退出的子进程，拿**确认已死**的 PID（瞬时 CLI 占 PID 位的真实形态）。"""
    proc = subprocess.Popen(  # noqa: bare-subprocess — tests/ 面，取证用真子进程
        [sys.executable, "-c", "raise SystemExit(0)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    proc.wait(timeout=60)
    pid = int(proc.pid)
    assert not is_pid_alive(pid), f"pid {pid} 未确认退出，红证前提不成立"
    return pid


def register_dead_pid_session(root: Path, sid: str, pid: int, *, heartbeat_age: float = 5.0) -> SessionRegistry:
    """写入"注册 PID=已退瞬态进程 + 心跳字段新鲜"的分片条目（三案现场复刻）。"""
    reg = SessionRegistry(project_root=root)
    reg.register(sid, pid=pid)
    now = time.time()
    data = reg.load()
    data[sid]["last_heartbeat"] = now - heartbeat_age
    data[sid]["last_activity"] = now - heartbeat_age
    reg.save(data)
    return reg


def write_heartbeat_file(root: Path, sid: str, *, status: str = "alive", age: float = 5.0) -> Path:
    """落 `.runtime/sessions/<sid>/heartbeat.jsonl`（mtime 相对 now 偏移，禁 sleep）。"""
    hb = root / ".runtime" / "sessions" / sid / "heartbeat.jsonl"
    hb.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.fromtimestamp(time.time() - age, tz=timezone.utc).isoformat()
    hb.write_text(json.dumps({"ts": ts, "pid": 4242, "status": status}) + "\n", encoding="utf-8")
    touch = time.time() - age
    os.utime(hb, (touch, touch))
    return hb


def write_inflight_bag(
    root: Path, sid: str, *, qid: str = "bag-0001", age: float = 5.0, state: str = "pending"
) -> Path:
    """落一个该 sid 的在途袋（旁证②）。"""
    bag_dir = root / ".runtime" / "commit_queue" / state
    bag_dir.mkdir(parents=True, exist_ok=True)
    bag = bag_dir / f"{qid}.json"
    bag.write_text(
        json.dumps({"qid": qid, "session_id": sid, "files": ["src/zephyr/foo.py"], "state": state}) + "\n",
        encoding="utf-8",
    )
    touch = time.time() - age
    os.utime(bag, (touch, touch))
    return bag


def make_branch_with_commit(root: Path, sid: str, *, commit_age: float = 5.0) -> None:
    """真 git 仓 + `ai/<sid>/task-x` 分支上一次提交（旁证③=分支提交时刻，非 index mtime）。"""
    env = {**os.environ, "GIT_AUTHOR_DATE": "", "GIT_COMMITTER_DATE": ""}
    stamp = int(time.time() - commit_age)
    iso = datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")
    env["GIT_AUTHOR_DATE"] = iso
    env["GIT_COMMITTER_DATE"] = iso

    def _git(*args: str) -> None:
        subprocess.run(  # noqa: bare-subprocess — tests/ 面，红证需要真 refs
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

    _git("init", "-q", "-b", "main")
    _git("config", "user.email", "t3lane@example.invalid")
    _git("config", "user.name", "t3-lane")
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git("add", "seed.txt")
    _git("commit", "-q", "-m", "seed")
    _git("checkout", "-q", "-b", f"ai/{sid}/task-takeover-cure")
    (root / "work.txt").write_text("real write trace\n", encoding="utf-8")
    _git("add", "work.txt")
    _git("commit", "-q", "-m", "ai/<sid> 真实写入痕迹")


def open_ledger_sids(root: Path) -> set[str]:
    """台账里 status=open 的 sid 集合（不存在=空集）。"""
    path = root / LEDGER_REL
    if not path.exists():
        return set()
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if row.get("status") == "open":
            out.add(str(row.get("sid")))
    return out


# ---------------------------------------------------------------------------
# 1. 正例：瞬时 PID 退 + 心跳文件新鲜 → 判活 / 不开账 / verdict 非 PID-DEAD
# ---------------------------------------------------------------------------


def test_fresh_heartbeat_file_overrides_dead_pid(lane_root):
    """落点①：pid>0 且 PID 亡，但心跳文件新鲜（末行非 exited）→ 三证①判活。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="alive")
    now = time.time()

    info = SessionInfo.from_dict(reg.load()[SID])
    assert _is_session_alive(info, now, root=lane_root) is True

    sink: dict = {}
    assert _is_session_alive(info, now, root=lane_root, evidence_sink=sink) is True
    assert "HEARTBEAT-FILE-FRESH" in sink["witnesses"], sink  # 禁静默翻转：用了哪一证可查


def test_list_active_keeps_transient_pid_session_with_fresh_heartbeat(lane_root):
    """落点①/④：list_active 不得把"PID 亡+心跳文件新鲜"的会话排除，且不得立案。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="alive")

    assert SID in reg.load()
    active_ids = {i.session_id for i in reg.list_active()}
    assert SID in active_ids
    assert SID not in open_ledger_sids(lane_root)  # 台账不开 open 条目


def test_liveness_verdict_not_pid_dead_when_heartbeat_file_fresh(lane_root):
    """落点③：P4 判死前须消费心跳文件 → 不得再以 PID-DEAD 定论。"""
    pid = confirmed_dead_pid()
    register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="alive")

    verdict = liveness_verdict(SID, now=time.time())
    assert verdict.state != "dead", verdict
    assert verdict.authoritative_signal not in {"PID-DEAD", "TAKEOVER-PENDING"}, verdict


def test_takeover_open_entry_is_overridden_by_fresh_heartbeat(lane_root):
    """落点③ P1：既有 open 条目 + 心跳文件新鲜 → 不再判 dead（历史误立案可自愈）。"""
    (lane_root / LEDGER_REL).parent.mkdir(parents=True, exist_ok=True)
    (lane_root / LEDGER_REL).write_text(
        json.dumps({"sid": SID, "status": "open", "death_evidence": {"reason": "误立案"}, "resources": {}}) + "\n",
        encoding="utf-8",
    )
    pid = confirmed_dead_pid()
    register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="alive")

    verdict = liveness_verdict(SID, now=time.time())
    assert verdict.authoritative_signal != "TAKEOVER-PENDING", verdict
    assert verdict.state != "dead", verdict


def test_ledger_hook_does_not_open_case_for_transient_pid(lane_root):
    """落点②：_salvage_takeover_ledger 里 _pid_dead 单独不得立案。"""
    from zephyr.security.access_control.session_concurrency import _salvage_takeover_ledger

    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="alive")
    now = time.time()
    data = reg.load()

    _salvage_takeover_ledger(lane_root, data, [SID], now)
    assert SID not in open_ledger_sids(lane_root)


# ---------------------------------------------------------------------------
# 2. 旁证②③：末行 exited（只证守护死、不证会话死）但队列/分支旁证在场 → 判活
# ---------------------------------------------------------------------------


def test_exited_last_line_but_inflight_bag_proves_alive(lane_root):
    """铁律：末行 exited 不得当活证；但旁证②（在途/新袋）在场仍判活。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    hb = write_heartbeat_file(lane_root, SID, status="exited")
    write_inflight_bag(lane_root, SID)
    now = time.time()

    sink: dict = {}
    assert _is_session_alive(SessionInfo.from_dict(reg.load()[SID]), now, root=lane_root, evidence_sink=sink) is True
    assert sink["witnesses"] == ["QUEUE-BAG-INFLIGHT"], sink
    assert sink["signals"]["heartbeat_fresh"] is False  # exited 不作数
    assert hb.exists()


def test_exited_last_line_but_branch_write_trace_proves_alive(lane_root):
    """旁证③：分支 ref 提交时刻新鲜（禁拿 index mtime 当活证）→ 判活 + 不开账。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="exited")
    make_branch_with_commit(lane_root, SID)
    now = time.time()

    sink: dict = {}
    assert _is_session_alive(SessionInfo.from_dict(reg.load()[SID]), now, root=lane_root, evidence_sink=sink) is True
    assert "BRANCH-WRITE-TRACE" in sink["witnesses"], sink

    assert SID in {i.session_id for i in reg.list_active()}
    assert SID not in open_ledger_sids(lane_root)


def test_stale_bag_and_stale_branch_are_not_evidence(lane_root):
    """旁证不得把闸拆成恒活：袋超窗（>_REAP_GRACE_SECONDS）+ 分支提交超窗 + exited → 判死。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="exited")
    write_inflight_bag(lane_root, SID, age=_REAP_GRACE_SECONDS + 600)
    make_branch_with_commit(lane_root, SID, commit_age=_REAP_GRACE_SECONDS + 3600)

    now = time.time()
    assert _is_session_alive(SessionInfo.from_dict(reg.load()[SID]), now, root=lane_root) is False
    assert SID not in {i.session_id for i in reg.list_active()}


# ---------------------------------------------------------------------------
# 3. 反例不误放：真死会话（三证全空）仍须判死开账
# ---------------------------------------------------------------------------


def test_true_death_still_judged_dead_and_opened(lane_root):
    """PID 亡 + 心跳末行 exited + 无在途袋 + 无写入痕迹 → 判死 + 开 open 条目 + 证据可原文核。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="exited")
    now = time.time()

    assert _is_session_alive(SessionInfo.from_dict(reg.load()[SID]), now, root=lane_root) is False
    assert SID not in {i.session_id for i in reg.list_active()}
    assert SID in open_ledger_sids(lane_root)

    row = next(
        json.loads(ln)
        for ln in (lane_root / LEDGER_REL).read_text(encoding="utf-8").splitlines()
        if ln.strip() and json.loads(ln).get("sid") == SID and json.loads(ln).get("status") == "open"
    )
    ev = row["death_evidence"]
    assert ev["pid_alive"] is False
    assert ev["alive_side_evidence"]["any_alive_side"] is False
    assert ev["alive_side_evidence"]["witnesses"] == []


def test_true_death_verdict_is_pid_dead_with_machine_readable_signal(lane_root):
    """反例 verdict 侧：reason/signal 字面量机读兼容必须保留（PID-DEAD 不改名）。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="exited")

    verdict = liveness_verdict(SID, now=time.time())
    assert verdict.state == "dead"
    assert verdict.authoritative_signal == "PID-DEAD", verdict
    assert reg.get_session(SID) is None


def test_no_heartbeat_file_at_all_still_dead(lane_root):
    """三证全缺（连心跳文件都没有）→ 判死，行为与修码前一致。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    now = time.time()

    assert _is_session_alive(SessionInfo.from_dict(reg.load()[SID]), now, root=lane_root) is False
    assert SID not in {i.session_id for i in reg.list_active()}
    assert SID in open_ledger_sids(lane_root)


# ---------------------------------------------------------------------------
# 4. 读侧零写副作用（落点④）
# ---------------------------------------------------------------------------


def test_list_active_readonly_channel_has_no_side_effects(lane_root):
    """mutating=False：只看不判死立账、不删分片（巡检/探针通道）。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid, heartbeat_age=_REAP_GRACE_SECONDS + 60)
    shard = lane_root / ".runtime" / "session_registry" / f"{SID}.json"
    assert shard.exists()

    active_ids = {i.session_id for i in reg.list_active(mutating=False)}
    assert SID not in active_ids
    assert SID not in open_ledger_sids(lane_root)  # 不写台账
    assert shard.exists()  # 不删分片（连超宽限的死片也只读不收割）


def test_readonly_probe_does_not_flip_anything(lane_root):
    """只读入口 list_active_readonly() 与 list_active(mutating=False) 同语义。"""
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid, heartbeat_age=_REAP_GRACE_SECONDS + 60)

    assert {i.session_id for i in reg.list_active_readonly()} == set()
    assert SID not in open_ledger_sids(lane_root)
    assert (lane_root / ".runtime" / "session_registry" / f"{SID}.json").exists()


# ---------------------------------------------------------------------------
# 5. 新 API 的存在性（判据可观测面）
# ---------------------------------------------------------------------------


def test_collect_alive_side_evidence_reports_three_readings(lane_root):
    """三证读数结构化：witnesses 机读名 + signals 原始读数（原文可见，禁静默翻转）。"""
    from zephyr.security.access_control.session_concurrency import collect_alive_side_evidence

    write_heartbeat_file(lane_root, SID, status="alive")
    write_inflight_bag(lane_root, SID)

    out = collect_alive_side_evidence(SID, time.time(), root=lane_root, use_cache=False)
    assert out["heartbeat_fresh"] is True
    assert out["bag_inflight"] is True
    assert out["write_trace"] is False
    assert out["any_alive_side"] is True
    assert set(out["witnesses"]) == {"HEARTBEAT-FILE-FRESH", "QUEUE-BAG-INFLIGHT"}
    assert out["signals"]["heartbeat_last_status"] == "alive"
    assert out["signals"]["heartbeat_window_seconds"] == _HEARTBEAT_TIMEOUT_SECONDS


def test_collect_alive_side_evidence_fail_soft_on_missing_root(lane_root):
    """证据读不到=无正证（不得当活证，也不得抛）——保守侧=不新增判活通道。"""
    from zephyr.security.access_control.session_concurrency import collect_alive_side_evidence

    out = collect_alive_side_evidence("sess-not-exist", time.time(), root=lane_root / "nope", use_cache=False)
    assert out["any_alive_side"] is False
    assert out["witnesses"] == []


def test_kill_switch_env_restores_pre_fix_death_judgement(lane_root, monkeypatch):
    """回退手柄 ZEPHYR_ALIVE_SIDE_EVIDENCE=0 → 逐字回到修码前（判死+立案），一键可撤。"""
    monkeypatch.setenv("ZEPHYR_ALIVE_SIDE_EVIDENCE", "0")
    pid = confirmed_dead_pid()
    reg = register_dead_pid_session(lane_root, SID, pid)
    write_heartbeat_file(lane_root, SID, status="alive")
    now = time.time()

    assert _is_session_alive(SessionInfo.from_dict(reg.load()[SID]), now, root=lane_root) is False
    assert SID not in {i.session_id for i in reg.list_active()}
    assert SID in open_ledger_sids(lane_root)  # 停用旁证即恢复旧立案行为
