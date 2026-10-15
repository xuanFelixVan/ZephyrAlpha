# [MODULE] tests.gov.session.test_session_keepalive_ghost_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.heartbeat_daemon; zephyr.security.access_control.session_concurrency; scripts.commit_queue
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/gov/session/test_session_keepalive_ghost_gate.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp_path 隔离（不触生产 .runtime/队列/注册表，不发真实 daemon 进程，不写 data/ 业务目录）；
#   保活正门三态钉桩=登记且未过期判活／未登记照旧 idle 自退／过期或被 revoke 照旧自退；
#   存活闸三腿（excused 赦免／judged_dead 判死／downgraded 降级）各自独立计数+裁决面落 JSONL 审计；
#   pristine 红证用 git show <ref>:<path> 现取字节（内容寻址，不落 .orig 副本）；
#   基线两笔在册袋以 dev 可达 commit sha 钉住 [1d5c0d36c4, f87bfa8bf7]（R9 袋/三证袋，钉内容非件名）
# [MODIFY-GUARD] 与 heartbeat_daemon（保活正门=run_daemon 5b''' 支）/commit_queue._session_ghost_verdict
#   同批改；出口字面量 excused/judged_dead/downgraded/alive_fast/not_in_registry/in_registry/
#   no_registry_file/undecidable 机读禁改名
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [CONSUMERS] pytest 自动发现；长班 keeper 侧集成检查（保活正门调用面=本件 test_keeper_*）
# [TESTS] tests/gov/session/test_session_keepalive_ghost_gate.py
# [A_module] module_id=MOD-GOV_HEARTBEAT_DAEMON_TEST-TEST_SESSION_KEEPALIVE_GHOST_GATE | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""心跳保活正门 + 幽灵存活闸同源化 红证（2026-10-11 维护二班，病=守护 idle 自退）。

病（在册条目"心跳 idle 自退使队列判袋为幽灵"，历史 421 袋死于 env:ghost_session）：
长班（pid=0 逻辑会话）的 detached 心跳守护在 idle>1800s 自退并写末行
``status="exited"``。此后 ①注册表心跳断供→会话被单一活性口径判死→提交被
[SESSION-REQUIRED] 拦；②队列存活闸读同一末行**短路判死**→在途袋直落 dead/。

六面红证：
  1. 正向：登记保活（名目/请求方/TTL 齐）时 idle 超阈不自退，且"谁/何时/何名义"落账；
  2. 反向钉桩（防把"补保活"做成"永不判死/永不退出"）：未登记／TTL 过期／被 revoke／
     名目不合规／账本损坏 → 照旧自退；exited 残留且无活性正证 → 照旧判死；
  3. 末行 status=exited 不再单独短路判死（裁定#507 判定面同源化——实测 dev **未落**，
     本班按在册裁定复位，pristine 用例即其红证）；
  4. 三证旁证"只读 refs、禁读 worktree index mtime"约束未被破坏（观测不污染观测对象）；
  5. 存活闸三腿独立计数 + 每裁决出口落一条审计（含真实判定链出口 _recover_orphans）；
  6. pristine 红证：dev 原版字节确实带缺陷（idle 支无保活入口；exited 无条件短路判死），
     并把 dev 原版函数体 exec 起来做行为对照（不靠文档转述）。
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import scripts.commit_queue as cq  # noqa: E402
from zephyr.gov_enforcement.rule_bridge import heartbeat_daemon as hb_mod  # noqa: E402
from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import (  # noqa: E402
    _KEEPALIVE_MAX_TTL_SECONDS,
    keepalive_file_path,
    read_active_keepalive,
    register_heartbeat_keepalive,
    revoke_heartbeat_keepalive,
    run_daemon,
)
from zephyr.security.access_control import session_concurrency as sc  # noqa: E402
from zephyr.security.access_control.session_concurrency import SessionRegistry  # noqa: E402

_LANE_ROOT = Path(__file__).resolve().parents[3]
_HB_REL = "src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py"
_CQ_REL = "scripts/commit_queue.py"
# 在册基线两笔（R9=1d5c0d36c4 治理判据班袋、三证=f87bfa8bf7 维护一班 T3 袋）——钉
# **dev 可达 commit sha** 而非件名：件名随后续袋漂移，sha 是内容真源。可达≠已落判据面
# （R9 的 commit_queue 面实测未落，见 test_pristine_commit_queue_* 的行为对照）。
_DEV_BASELINES = ("1d5c0d36c4", "f87bfa8bf7")
# pristine 参照系 MUST 钉死开工基线：dev 是活动分支，本班自己的袋子一落地，
# "dev 上该缺陷应存在"这类断言就会翻红（实测踩过：3 条 pristine 探针因本班袋 c869c0a3b5 落地而失效）。
_PRISTINE_REF = "cfbebbf8dd49f8b8ae935d186f4fbe7f8cfc6c66"


# ---------------------------------------------------------------------------
# 夹具
# ---------------------------------------------------------------------------


def _recs(root: Path, sid: str) -> list[dict]:
    path = hb_mod.heartbeat_file_path(root, sid)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _registry_cls(*, idle_seconds: float, logical: bool = False, hb_age_seconds: float | None = None):
    """造 SessionRegistry 替身：last_activity（可选 last_heartbeat）停在给定 age。

    只给 get_session 一个口（存活闸只准经公开正门读活性，见 test_single_source...）。
    """

    class _Reg:
        def __init__(self, root):
            self.root = root

        def get_session(self, sid):
            hb = time.time() - (idle_seconds if hb_age_seconds is None else hb_age_seconds)
            return {
                "session_id": sid,
                "last_activity": time.time() - idle_seconds,
                "start_time": time.time() - idle_seconds - 1000,
                "last_heartbeat": hb,
                "pid": 0,
                "logical": logical,
                "held_files": [],
                "task_files": [],
            }

        def heartbeat(self, sid):  # 守护每轮刷新（缺了它 run_daemon 会计到 fatal 出口）
            return True

        def list_active(self, **_kw):  # 禁走（带写副作用的判死轨=第四套口径）
            raise AssertionError("存活闸禁走 list_active")

    return _Reg


def _runtime_with_heartbeat(base: Path, sid: str, statuses: list[str]) -> Path:
    """造 runtime 根：``<base>/sessions/<sid>/heartbeat.jsonl`` 按序落 status。"""
    hb_dir = base / "sessions" / sid
    hb_dir.mkdir(parents=True, exist_ok=True)
    with (hb_dir / "heartbeat.jsonl").open("w", encoding="utf-8") as fh:
        for st in statuses:
            fh.write(json.dumps({"ts": "2026-10-11T00:00:00+00:00", "pid": 7, "status": st}) + "\n")
    return base


# ---------------------------------------------------------------------------
# 1) 正向：登记保活 → idle 超阈不自退 + 审计在场
# ---------------------------------------------------------------------------


def test_registered_keeper_prevents_idle_self_exit(tmp_path: Path) -> None:
    """保活正门在岗：idle 4000s>1800s 仍不自退，逐轮落 keepalive=registered_keeper 留痕。"""
    sid = "sess-keeper-on"
    reg = register_heartbeat_keepalive(
        tmp_path,
        sid,
        reason="长班心跳保活（统筹裁定⑤治本）",
        requested_by="st-maint2-20261011",
    )
    with (
        patch.object(sc, "SessionRegistry", _registry_cls(idle_seconds=4000.0)),
        patch.object(hb_mod, "_INITIAL_DELAY", 0.01),
        patch.object(hb_mod, "_MAX_IDLE_SECONDS", 1800),
    ):
        rc = run_daemon(sid, tmp_path, interval=0.01, max_iterations=3)

    assert rc == 0
    recs = _recs(tmp_path, sid)
    statuses = [r["status"] for r in recs]
    assert "exited" not in statuses, f"登记保活后不得因 idle 自退：{statuses}"
    assert statuses.count("alive") >= 3, f"豁免后应继续心跳：{statuses}"
    keep = [r for r in recs if r.get("keepalive") == "registered_keeper"]
    assert keep, "应有 registered_keeper 留痕"
    assert keep[0]["keeper"] == "st-maint2-20261011", "留痕必须写出请求方"
    assert keep[0]["keeper_reason"] == reg["reason"], "留痕必须写出续命名目"
    assert keep[0]["keeper_ttl_remaining_seconds"] > 0
    assert reg["ttl_seconds"] <= _KEEPALIVE_MAX_TTL_SECONDS


def test_keeper_audit_who_when_and_nominally(tmp_path: Path) -> None:
    """续命账本自身可审计：谁、何时、以何名义、多久到期逐字段落盘（append-only）。"""
    sid = "sess-keeper-audit"
    before = time.time()
    rec = register_heartbeat_keepalive(
        tmp_path,
        sid,
        reason="队列在途袋待落地，守护不得 idle 自退",
        requested_by="st-keeper-demo",
        ttl_seconds=600,
    )
    after = time.time()
    path = keepalive_file_path(tmp_path, sid)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    row = rows[0]
    assert row["event"] == "grant"
    assert row["session_id"] == sid
    assert row["requested_by"] == "st-keeper-demo"
    assert row["reason"] == "队列在途袋待落地，守护不得 idle 自退"
    assert before - 0.01 <= row["granted_at"] <= after + 0.01  # 微秒截断容差
    assert row["expires_at"] == pytest.approx(row["granted_at"] + 600, abs=1)
    assert row["ts"].endswith("+00:00"), "审计时间戳必须带显式时区（RULE-SCHEMA-TZ）"
    assert read_active_keepalive(tmp_path, sid) is not None


# ---------------------------------------------------------------------------
# 2) 反向钉桩（防"补保活"被做成"永不退出/永不判死"）
# ---------------------------------------------------------------------------


def test_no_keeper_registration_still_exits_on_idle(tmp_path: Path) -> None:
    """缺省态零变更：不登记保活 → idle 超阈照旧写 exited(idle timeout) 自退。"""
    sid = "sess-keeper-absent"
    assert read_active_keepalive(tmp_path, sid) is None
    with (
        patch.object(sc, "SessionRegistry", _registry_cls(idle_seconds=4000.0)),
        patch.object(hb_mod, "_INITIAL_DELAY", 0.01),
        patch.object(hb_mod, "_MAX_IDLE_SECONDS", 1800),
    ):
        rc = run_daemon(sid, tmp_path, interval=0.01)

    assert rc == 0
    recs = _recs(tmp_path, sid)
    exited = [r for r in recs if r["status"] == "exited"]
    assert exited and exited[0]["reason"] == "idle timeout", "无授权必须照旧自退"
    assert not [r for r in recs if r.get("keepalive") == "registered_keeper"]


def test_expired_keeper_still_exits_on_idle(tmp_path: Path) -> None:
    """TTL 过期即失效：授权到期照旧自退（"永不退出"不得成为新默认）。"""
    sid = "sess-keeper-expired"
    register_heartbeat_keepalive(
        tmp_path, sid, reason="已到期的一次性续命", requested_by="st-maint2-20261011", ttl_seconds=60
    )
    future = time.time() + 3600
    assert read_active_keepalive(tmp_path, sid, now=future) is None
    with (
        patch.object(sc, "SessionRegistry", _registry_cls(idle_seconds=4000.0)),
        patch.object(hb_mod, "_INITIAL_DELAY", 0.01),
        patch.object(hb_mod, "_MAX_IDLE_SECONDS", 1800),
        patch.object(hb_mod, "_epoch_seconds", lambda: future),
    ):
        rc = run_daemon(sid, tmp_path, interval=0.01)

    assert rc == 0
    exited = [r for r in _recs(tmp_path, sid) if r["status"] == "exited"]
    assert exited and exited[0]["reason"] == "idle timeout", "过期授权必须回落自退语义"


def test_revoked_keeper_still_exits_on_idle(tmp_path: Path) -> None:
    """revoke 后授权即刻失效（末条事件为准）：照旧自退。"""
    sid = "sess-keeper-revoked"
    register_heartbeat_keepalive(tmp_path, sid, reason="先续后撤一条授权吧", requested_by="st-maint2-20261011")
    assert read_active_keepalive(tmp_path, sid) is not None
    revoke_heartbeat_keepalive(tmp_path, sid, reason="收工撤销", requested_by="st-maint2-20261011")
    assert read_active_keepalive(tmp_path, sid) is None
    with (
        patch.object(sc, "SessionRegistry", _registry_cls(idle_seconds=4000.0)),
        patch.object(hb_mod, "_INITIAL_DELAY", 0.01),
        patch.object(hb_mod, "_MAX_IDLE_SECONDS", 1800),
    ):
        rc = run_daemon(sid, tmp_path, interval=0.01)

    assert rc == 0
    exited = [r for r in _recs(tmp_path, sid) if r["status"] == "exited"]
    assert exited and exited[0]["reason"] == "idle timeout"


@pytest.mark.parametrize(
    ("reason", "requested_by"),
    [
        ("", "st-maint2-20261011"),
        ("短名目", "st-maint2-20261011"),
        ("合理名目但没人签字", ""),
        ("合理名目但没人签字", "   "),
        ("合理名目但没人签字", None),
    ],
)
def test_keeper_door_rejects_unnamed_grants(tmp_path: Path, reason: str, requested_by: str | None) -> None:
    """正门拒收无名目/匿名授权：大声拒绝而非静默放行（静默拒绝=下一条漏洞）。"""
    with pytest.raises(ValueError):
        register_heartbeat_keepalive(tmp_path, "sess-keeper-bad", reason=reason, requested_by=requested_by)
    assert not keepalive_file_path(tmp_path, "sess-keeper-bad").exists()


def test_keeper_ttl_and_max_clamped(tmp_path: Path) -> None:
    """TTL 上限硬钳制：超上限按上限落账；非正 TTL 拒绝（防"永久授权"从后门进来）。"""
    rec = register_heartbeat_keepalive(
        tmp_path, "sess-keeper-clamp", reason="越界 TTL 必须被钳制", requested_by="lane", ttl_seconds=10**6
    )
    assert rec["ttl_seconds"] == _KEEPALIVE_MAX_TTL_SECONDS
    with pytest.raises(ValueError):
        register_heartbeat_keepalive(
            tmp_path, "sess-keeper-zero", reason="零 TTL 不是授权", requested_by="lane", ttl_seconds=0
        )


def test_corrupt_keeper_ledger_is_not_liveness(tmp_path: Path) -> None:
    """账本损坏/半行/缺名目=无授权（保守侧：宁自退不扩权保活）。"""
    sid = "sess-keeper-corrupt"
    path = keepalive_file_path(tmp_path, sid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"event": "grant", "session_id": "%s" 半行\n' % sid, encoding="utf-8")
    assert read_active_keepalive(tmp_path, sid) is None
    path.write_text(
        json.dumps({"event": "grant", "session_id": sid, "expires_at": time.time() + 600}) + "\n",
        encoding="utf-8",
    )
    assert read_active_keepalive(tmp_path, sid) is None, "缺名目的 grant 不算授权"
    path.write_text(
        json.dumps(
            {"event": "grant", "session_id": "别的会话", "reason": "别人的授权", "expires_at": time.time() + 600}
        )
        + "\n",
        encoding="utf-8",
    )
    assert read_active_keepalive(tmp_path, sid) is None, "别人的授权不得给本会话续命"


# ---------------------------------------------------------------------------
# 3) 末行 status=exited 不再单独短路判死（裁定#507 同源化，真注册表）
# ---------------------------------------------------------------------------


def _real_registry_at(root: Path) -> SessionRegistry:
    return SessionRegistry(root)


def _seed_entry(reg: SessionRegistry, sid: str, *, hb_age: float) -> None:
    """写真实注册表条目：last_heartbeat 停在 hb_age 秒前（pid=0 逻辑会话判活锚）。"""
    reg.register(sid, pid=0, held_files=[f"x/{sid}.py"], task_files=[f"x/{sid}.py"])
    shard = reg._shards_dir / reg._shard_filename(sid)
    entry = json.loads(shard.read_text(encoding="utf-8"))
    entry["last_heartbeat"] = time.time() - hb_age
    entry["last_activity"] = time.time() - hb_age
    entry["logical"] = True
    shard.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")


def test_exited_residue_with_live_registry_is_excused(tmp_path: Path) -> None:
    """事故形态复刻：守护 idle 自退留 exited 残留，注册表仍判活 → 存活闸赦免不烧袋。"""
    sid = "sess-ghost-excused"
    reg = _real_registry_at(tmp_path)
    _seed_entry(reg, sid, hb_age=5.0)
    rt = _runtime_with_heartbeat(tmp_path / "rt", sid, ["alive", "exited"])
    cq.reset_ghost_gate_counts()
    v = cq._session_ghost_verdict(sid, runtime_root=rt)
    assert v["exit"] == "excused" and v["dead"] is False, "exited 残留不得单独短路判死"
    assert cq.ghost_gate_counts()["excused"] == 1
    audit = (rt / "audit" / "ghost_liveness.jsonl").read_text(encoding="utf-8")
    assert sid in audit and '"exit": "excused"' in audit


def test_exited_residue_with_stale_registry_still_judged_dead(tmp_path: Path) -> None:
    """反向钉桩：在册但活性判死（心跳停 4000s，无旁证）→ 照旧判死（没正证就是死）。"""
    sid = "sess-ghost-dead"
    reg = _real_registry_at(tmp_path)
    _seed_entry(reg, sid, hb_age=4000.0)
    rt = _runtime_with_heartbeat(tmp_path / "rt", sid, ["exited"])
    cq.reset_ghost_gate_counts()
    v = cq._session_ghost_verdict(sid, runtime_root=rt)
    assert v["exit"] == "judged_dead" and v["dead"] is True
    assert cq.ghost_gate_counts()["judged_dead"] == 1
    assert cq.ghost_gate_counts()["excused"] == 0


def test_exited_residue_without_registry_activity_is_dead(tmp_path: Path) -> None:
    """除名面（注册表查无此 sid）：exited 残留照旧判死——unregister 即终审。"""
    sid = "sess-ghost-unregistered"
    rt = _runtime_with_heartbeat(tmp_path / "rt", sid, ["exited"])
    _real_registry_at(tmp_path)  # 构造真册（目录在场），但本 sid 不写条目
    cq.reset_ghost_gate_counts()
    v = cq._session_ghost_verdict(sid, runtime_root=rt)
    assert v["exit"] == "judged_dead" and v["dead"] is True


def test_exited_residue_with_registry_facility_unavailable_downgrades(tmp_path: Path) -> None:
    """降级腿：注册表设施不可用（SessionRegistry 都造不出）→ 退回原"残留→死"。

    赦免必须有正证——设施故障绝不等于会话活着（fail-open 只保留"无任何信号"一面）。
    """
    sid = "sess-ghost-downgraded"
    rt = _runtime_with_heartbeat(tmp_path / "rt", sid, ["exited"])
    cq.reset_ghost_gate_counts()

    class _Boom:
        def __init__(self, root):
            raise RuntimeError("registry facility unavailable")

    with patch.object(sc, "SessionRegistry", _Boom):
        v = cq._session_ghost_verdict(sid, runtime_root=rt)
    assert v["exit"] == "downgraded" and v["dead"] is True
    counts = cq.ghost_gate_counts()
    assert counts["downgraded"] == 1 and counts["excused"] == 0 and counts["judged_dead"] == 0
    assert '"exit": "downgraded"' in (rt / "audit" / "ghost_liveness.jsonl").read_text(encoding="utf-8")


def test_alive_tail_fast_path_never_asks_registry(tmp_path: Path) -> None:
    """活心跳快路（末行非 exited）逐字不变，且零注册表 IO。"""
    sid = "sess-ghost-alive"
    rt = _runtime_with_heartbeat(tmp_path / "rt", sid, ["exited", "alive"])

    def _boom(*_a, **_k):
        raise AssertionError("活心跳快路不得咨询注册表（原语义：其余值→活）")

    cq.reset_ghost_gate_counts()
    with patch.object(sc, "SessionRegistry", _boom):
        v = cq._session_ghost_verdict(sid, runtime_root=rt)
    assert v["exit"] == "alive_fast" and v["dead"] is False
    assert cq.ghost_gate_counts()["alive_fast"] == 1


def test_ghost_gate_no_heartbeat_keeps_legacy_registry_branch(tmp_path: Path) -> None:
    """无心跳文件面逐字未动：旧单表在册性判死/放行原语义（裁定#459 第二支）。"""
    sid = "sess-ghost-nohb"
    rt = tmp_path / "rt"
    (rt / "sessions").mkdir(parents=True)
    (rt / "session_registry.json").write_text(json.dumps({"someone-else": {}}), encoding="utf-8")
    assert cq._session_ghost_verdict(sid, runtime_root=rt)["exit"] == "not_in_registry"
    assert cq._session_ghost_dead(sid, runtime_root=rt) is True
    (rt / "session_registry.json").write_text(json.dumps({sid: {}}), encoding="utf-8")
    assert cq._session_ghost_verdict(sid, runtime_root=rt)["exit"] == "in_registry"
    assert cq._session_ghost_dead(sid, runtime_root=rt) is False
    (rt / "session_registry.json").unlink()
    assert cq._session_ghost_verdict(sid, runtime_root=rt)["exit"] == "no_registry_file"
    assert cq._session_ghost_dead(sid, runtime_root=rt) is False


def test_ghost_gate_undecidable_failopen_faces(tmp_path: Path) -> None:
    """判定不了的面全部 fail-open 放行（空 sid/全损坏/非对象行，原语义逐字保留）。"""
    empty_rt = tmp_path / "rt"
    (empty_rt / "sessions").mkdir(parents=True)
    assert cq._session_ghost_verdict("", runtime_root=empty_rt)["exit"] == "undecidable"

    rt = _runtime_with_heartbeat(tmp_path / "rt2", "sess-ghost-corrupt", ["garbage-not-json", ""])
    assert cq._session_ghost_dead("sess-ghost-corrupt", runtime_root=rt) is False

    rt3 = tmp_path / "rt3"
    d = rt3 / "sessions" / "sess-ghost-list"
    d.mkdir(parents=True)
    (d / "heartbeat.jsonl").write_text(json.dumps([1, 2, 3]) + "\n", encoding="utf-8")
    assert cq._session_ghost_verdict("sess-ghost-list", runtime_root=rt3)["exit"] == "undecidable"


def test_ghost_gate_consumes_registry_single_source(tmp_path: Path) -> None:
    """赦免腿只经公开正门 get_session（单一口径），绝不碰 list_active（副作用轨=第四套）。"""
    sid = "sess-single-source"
    rt = _runtime_with_heartbeat(tmp_path / "rt", sid, ["exited"])
    seen = {"get_session": 0, "list_active": 0}

    class _Reg:
        def __init__(self, root):
            self.root = root

        def get_session(self, _sid):
            seen["get_session"] += 1
            return {"session_id": _sid}

        def list_active(self, **_kw):
            seen["list_active"] += 1
            raise AssertionError("存活闸禁走 list_active（判死带写副作用，且属第四套口径）")

    with patch.object(sc, "SessionRegistry", _Reg):
        v = cq._session_ghost_verdict(sid, runtime_root=rt)
    assert v["dead"] is False and v["exit"] == "excused"
    assert seen["get_session"] == 1 and seen["list_active"] == 0


# ---------------------------------------------------------------------------
# 5) 每出口独立计数（含真实判定链出口 _recover_orphans）
# ---------------------------------------------------------------------------


def test_each_ghost_gate_exit_counts_independently(tmp_path: Path) -> None:
    """三条腿各自可断言计数，禁合并成单一 bool；孤儿回收出口也过同一计数器。"""
    cq.reset_ghost_gate_counts()
    assert cq.ghost_gate_counts() == dict.fromkeys(cq._GHOST_GATE_EXITS, 0)

    # 腿①赦免 + 腿②判死（同 rt，真注册表）
    reg = _real_registry_at(tmp_path)
    alive_sid, dead_sid = "sess-count-excused", "sess-count-dead"
    _seed_entry(reg, alive_sid, hb_age=5.0)
    _seed_entry(reg, dead_sid, hb_age=4000.0)
    rt = _runtime_with_heartbeat(tmp_path / "rt", alive_sid, ["exited"])
    _runtime_with_heartbeat(rt, dead_sid, ["exited"])
    assert cq._session_ghost_dead(alive_sid, runtime_root=rt) is False
    assert cq._session_ghost_dead(dead_sid, runtime_root=rt) is True

    # 判定链真实出口：processing 孤儿回收（赦免袋必须照常回收）
    orphan_sid = "sess-count-orphan"
    _seed_entry(reg, orphan_sid, hb_age=5.0)
    _runtime_with_heartbeat(rt, orphan_sid, ["alive", "exited"])
    queue_root = rt / "queue"
    (queue_root / "pending").mkdir(parents=True)
    (queue_root / "processing").mkdir(parents=True)
    (queue_root / "processing" / "q-orphan.json").write_text(
        json.dumps({"qid": "q-orphan", "session_id": orphan_sid}), encoding="utf-8"
    )
    recovered = cq._recover_orphans(queue_root)

    counts = cq.ghost_gate_counts()
    assert counts["excused"] == 2, f"赦免腿独立计数（含孤儿回收出口）：{counts}"
    assert counts["judged_dead"] == 1, f"判死腿独立计数：{counts}"
    assert counts["downgraded"] == 0, "未触发的降级腿不得计数（禁把降级混进赦免）"
    assert recovered == ["q-orphan"], "赦免袋照常回收重投，不得被顺手烧掉"
    assert (queue_root / "pending" / "q-orphan.json").exists()
    assert not (queue_root / "dead").exists(), "赦免路径绝不得产死信"
    rows = [
        json.loads(line)
        for line in (rt / "audit" / "ghost_liveness.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert [r["exit"] for r in rows] == ["excused", "judged_dead", "excused"], "每裁决出口各落一条"


# ---------------------------------------------------------------------------
# 4) 三证旁证：只读 refs，禁读 worktree index mtime（观测不污染观测对象）
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


@pytest.mark.parametrize("sha", _DEV_BASELINES)
def test_baselines_reachable_on_dev(sha: str) -> None:
    """在册基线两笔可达且在 dev 祖先面（本班据此判定"R9/三证落没落"，不靠转述）。"""
    full = subprocess.run(
        ["git", "-C", str(_LANE_ROOT), "rev-parse", sha],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert full.startswith(sha)
    assert (
        subprocess.run(
            ["git", "-C", str(_LANE_ROOT), "merge-base", "--is-ancestor", full, "dev"],
            capture_output=True,
        ).returncode
        == 0
    ), f"基线件 {sha} 不在 dev 可达面"


def test_branch_side_proof_reads_refs_not_index(tmp_path: Path) -> None:
    """证③真读 refs（for-each-ref），且读数不回写 linked worktree 的 index。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    (repo / "a.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    branch = "ai/sess-wt-1/task-x"
    (repo / "b.txt").write_text("work\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "work")
    # 分支只建 ref 不在主仓 checkout（否则 worktree add 报 already checked out）
    _git(repo, "branch", branch)
    wt = tmp_path / "wt-1"
    _git(repo, "worktree", "add", "-q", str(wt), branch)

    index_meta = repo / ".git" / "worktrees" / wt.name / "index"
    assert index_meta.exists(), "linked worktree 应有自己的 index（本用例的观测对象）"
    before = index_meta.stat().st_mtime_ns

    sc.reset_alive_side_evidence_cache()
    fresh, age, br = sc._branch_side_proof(repo, "sess-wt-1", time.time())
    assert fresh is True and br == branch, f"分支提交应在 900s 窗内：{fresh}/{br}"
    assert age is not None and age < 900
    assert index_meta.stat().st_mtime_ns == before, "读旁证不得回写 worktree index（观测即造证）"

    src = Path(sc.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_branch_side_proof"), None)
    assert fn is not None, "_branch_side_proof 定义不可见"
    # 只看代码面（docstring 里"禁拿 index mtime"等字样是规范叙述，不是实现）
    code = "\n".join(ast.get_source_segment(src, stmt) or "" for stmt in fn.body[1:])
    assert "for-each-ref" in code, "证③必须经 for-each-ref 读 refs"
    for forbidden in ("status", "rev-parse", "index", "diff-index", "ls-files"):
        assert forbidden not in code, f"证③实现面出现禁用项：{forbidden}"

    # 分支超窗=无正证（index 再新也不作活证）
    future = time.time() + 10_000
    fresh2, _, _ = sc._branch_side_proof(repo, "sess-wt-1", future)
    assert fresh2 is False, "分支提交超窗即无正证——不得被任何 mtime 类读数蒙混成活"


def test_alive_side_evidence_three_legs_and_fallback_handle(tmp_path: Path, monkeypatch) -> None:
    """三证在岗（心跳新鲜且末行非 exited／窗内袋／窗内分支提交）+ 回退手柄=逐字无旁证。"""
    monkeypatch.delenv("ZEPHYR_COMMIT_QUEUE_DIR", raising=False)
    sid = "sess-evidence-legs"
    root = tmp_path
    # 证①：心跳新鲜且末行 alive
    hb_dir = root / ".runtime" / "sessions" / sid
    hb_dir.mkdir(parents=True)
    (hb_dir / "heartbeat.jsonl").write_text(
        json.dumps({"ts": "t", "pid": 1, "status": "alive"}) + "\n", encoding="utf-8"
    )
    # 证②：pending 有 900s 窗内的本 sid 袋
    bag_dir = root / ".runtime" / "commit_queue" / "pending"
    bag_dir.mkdir(parents=True)
    (bag_dir / "q-1.json").write_text(json.dumps({"qid": "q-1", "session_id": sid}), encoding="utf-8")

    sc.reset_alive_side_evidence_cache()
    one = sc.collect_alive_side_evidence(sid, time.time(), root=root, use_cache=False)
    assert one["heartbeat_fresh"] is True and one["bag_inflight"] is True
    assert sc._ALIVE_WITNESS_HEARTBEAT in one["witnesses"] and sc._ALIVE_WITNESS_BAG in one["witnesses"]

    # 证①的反面：末行 exited → 心跳面不得算正证（在册铁律"exited 只证守护死"）
    (hb_dir / "heartbeat.jsonl").write_text(
        json.dumps({"ts": "t", "pid": 1, "status": "exited"}) + "\n", encoding="utf-8"
    )
    sc.reset_alive_side_evidence_cache()
    two = sc.collect_alive_side_evidence(sid, time.time(), root=root, use_cache=False)
    assert two["heartbeat_fresh"] is False, "exited 残留不得当会话活证"
    assert two["bag_inflight"] is True and two["any_alive_side"] is True

    # 回退手柄：ZEPHYR_ALIVE_SIDE_EVIDENCE=0 → 整轴停用=逐字旧判死（无旁证）
    monkeypatch.setenv("ZEPHYR_ALIVE_SIDE_EVIDENCE", "0")
    sc.reset_alive_side_evidence_cache()
    off = sc.collect_alive_side_evidence(sid, time.time(), root=root, use_cache=False)
    assert off["any_alive_side"] is False and off["witnesses"] == []
    monkeypatch.delenv("ZEPHYR_ALIVE_SIDE_EVIDENCE", raising=False)
    sc.reset_alive_side_evidence_cache()
    on = sc.collect_alive_side_evidence(sid, time.time(), root=root, use_cache=False)
    assert set(on) == set(off), "两态出参形状全等（只关判据不关形状）"
    assert on["any_alive_side"] is True


# ---------------------------------------------------------------------------
# 6) pristine 红证：dev 原版字节确实带病（内容寻址现取，不落 .orig 副本）
# ---------------------------------------------------------------------------


def _show(ref: str, rel: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(_LANE_ROOT), "show", f"{ref}:{rel}"],
        check=True,
        capture_output=True,
    )
    return proc.stdout.replace(b"\r\n", b"\n")


def _func(text: str, name: str) -> str:
    m = re.search(rf"\ndef {name}\(.*?(?=\ndef |\Z)", text, re.S)
    assert m, f"函数 {name} 不可见"
    return m.group(0)


def test_pristine_heartbeat_daemon_has_no_keepalive_door() -> None:
    """pristine（dev tip 字节）：idle 支只有 logical/C355 两条既有豁免，无保活正门。"""
    text = _show(_PRISTINE_REF, _HB_REL).decode("utf-8")
    for absent in ("register_heartbeat_keepalive", "read_active_keepalive", "registered_keeper"):
        assert absent not in text, f"dev 不该已有 {absent}（若有=本班在重复施工）"
    idle = _func(text, "_session_idle_seconds")
    assert "last_activity" in idle, "idle 真源=last_activity 独立锚（守护自刷心跳不算活证）"
    run = _func(text, "run_daemon")
    assert '"exited"' in run and "idle timeout" in run, "idle 超限支无条件写 exited 自退"

    now = (_LANE_ROOT / _HB_REL).read_text(encoding="utf-8")
    assert "register_heartbeat_keepalive" in now and "registered_keeper" in now
    for must_keep in ("logical_session", "commit_queue_wait", "idle timeout"):
        assert must_keep in now, f"既有豁免/自退字面量不得被顺手删：{must_keep}"


def test_pristine_commit_queue_ghost_gate_shortcircuits_on_exited(tmp_path: Path) -> None:
    """pristine（dev tip 字节）：闸第一支以末行 status=='exited' 无条件短路判死。

    在册裁定#507 明写该支要降为"前代守护死亡证明"、终审归注册表活性单一口径；
    dev 字节实测=裁定未落地（本用例即其红证，本班按在册裁定复位）。
    """
    text = _show(_PRISTINE_REF, _CQ_REL).decode("utf-8")
    ghost = _func(text, "_session_ghost_dead")
    assert 'return isinstance(last, dict) and last.get("status") == "exited"' in ghost
    for absent in ("get_session", "_is_session_alive", "excused", "collect_alive_side_evidence"):
        assert absent not in ghost, f"dev 的 ghost 支不该已有 {absent}（同源化未落地才是本病）"

    # 行为对照：把 dev 原版函数体 exec 起来跑事故形态（现取字节，不落 .orig 副本）
    ns: dict = {"json": json, "Path": Path}
    exec(compile(ghost.strip(), "<dev-ghost-pristine>", "exec"), ns)  # noqa: S102 — 基线字节对照用
    dev_dead = ns["_session_ghost_dead"]
    rt = _runtime_with_heartbeat(tmp_path / "rt", "sid-a", ["exited"])
    assert dev_dead("sid-a", runtime_root=rt) is True, "dev 原版必须短路判死（缺陷在场实证）"
    assert cq._session_ghost_dead("sid-a", runtime_root=rt) is True, "无册正证时本班也判死"

    # dev 原版"活性册也照杀"——本班缺陷清偿的行为差分实证：
    # 同一现场（exited 残留 + 注册表判活）dev 判死、本班赦免（pristine 支的假阴性面）。
    reg = _real_registry_at(tmp_path)
    _seed_entry(reg, "sid-a", hb_age=5.0)
    assert dev_dead("sid-a", runtime_root=rt) is True, "dev 原版不看注册表（缺陷面）"
    assert cq._session_ghost_verdict("sid-a", runtime_root=rt)["exit"] == "excused"

    cur = _func((_LANE_ROOT / _CQ_REL).read_text(encoding="utf-8"), "_session_ghost_dead")
    assert ghost.encode("utf-8") != cur.encode("utf-8"), "改后字节必须与 dev 原版不同（否则没改到点上）"


def test_pristine_dev_line_anchor_of_the_short_circuit() -> None:
    """现场行号可复核（报告锚点）：dev 的 exited 短路支确在 _session_ghost_dead 体内。"""
    raw = _show(_PRISTINE_REF, _CQ_REL).decode("utf-8").splitlines()
    hits = [(i + 1, ln.strip()) for i, ln in enumerate(raw) if 'last.get("status") == "exited"' in ln]
    assert len(hits) == 1, f"dev 上 exited 短路应恰一处，实测 {hits}"
    lineno, _line = hits[0]
    def_lines = [i + 1 for i, ln in enumerate(raw) if ln.startswith("def _session_ghost_dead")]
    assert def_lines and def_lines[0] < lineno < def_lines[0] + 40, f"短路支行号越界：{lineno}"


# ---------------------------------------------------------------------------
# 4) 托管正门（2026-10-15 车道，裁定#459 实现层正门豁免已报总包）：
#    enqueue 即托管（meta.custody=true）→ 属主名义存活直到末袋终态
# ---------------------------------------------------------------------------


class TestCustodyExemptionFace:
    """托管豁免面：meta.custody 袋不因属主死而判死；无标袋原判据逐字不变。"""

    def _dead_owner_runtime(self, tmp_path: Path, sid: str) -> Path:
        """最死形态现场：exited 残留 + 真册在场但 sid 除名（unregister 即终审）。"""
        rt = _runtime_with_heartbeat(tmp_path / "rt", sid, ["alive", "exited"])
        _real_registry_at(tmp_path)  # 真册构造在场，本 sid 不写条目
        return rt

    def test_custody_bag_exempt_even_fully_dead_owner(self, tmp_path: Path) -> None:
        """托管袋在最死形态下豁免：custody_excused 出口+裁决面审计（禁静默翻转）。"""
        sid = "sess-custody-live"
        rt = self._dead_owner_runtime(tmp_path, sid)
        cq.reset_ghost_gate_counts()
        item = {"qid": "q-x-0001", "session_id": sid, "meta": {"custody": True}}
        assert cq._session_ghost_dead_for_item(item, runtime_root=rt) is False
        assert cq.ghost_gate_counts()["custody_excused"] == 1
        assert cq.ghost_gate_counts()["judged_dead"] == 0
        audit = (rt / "audit" / "ghost_liveness.jsonl").read_text(encoding="utf-8")
        assert "custody_excused" in audit and sid in audit

    def test_no_custody_marker_keeps_original_death(self, tmp_path: Path) -> None:
        """反向钉桩（豁免不扩面）：同现场无托管标 → 原判死逐字（历史袋/终态件）。"""
        sid = "sess-custody-legacy"
        rt = self._dead_owner_runtime(tmp_path, sid)
        cq.reset_ghost_gate_counts()
        item = {"qid": "q-x-0002", "session_id": sid, "meta": {}}
        assert cq._session_ghost_dead_for_item(item, runtime_root=rt) is True
        assert cq.ghost_gate_counts()["judged_dead"] == 1
        assert cq.ghost_gate_counts()["custody_excused"] == 0

    def test_enqueue_grants_custody_marker(self, tmp_path: Path, monkeypatch) -> None:
        """托管权在唯一入袋口授予：enqueue_item 落袋即带 meta.custody=true
        （requeue 复投经 enqueue_item 自动继承；预检/登记门 mock=本用例只钉托管标）。"""
        monkeypatch.setattr(cq, "_run_declared_preflight", lambda *a, **k: None)
        monkeypatch.setattr(cq, "_run_registration_gate", lambda *a, **k: (0, [], {}))
        item = cq.enqueue_item(
            "sess-custody-enq",
            "托管标随袋（mock 预检）",
            [("docs/custody_probe.txt", b"x")],
            queue_root=tmp_path / "q",
        )
        assert item["meta"]["custody"] is True, "入袋即托管（托管正门授予面）"

    def test_all_gate_call_sites_route_through_custody_wrapper(self) -> None:
        """四调用点（drain 拾取/_drain_env_requeue/_recover_orphans/pool 拾取）必须经
        托管豁免面，禁绕过托管面直连 _session_ghost_dead（漏闸=整批判死复发）。"""
        all_src = (
            (_LANE_ROOT / _CQ_REL).read_text(encoding="utf-8")
            + "\n"
            + (_LANE_ROOT / "scripts/governance/commit_queue_landing.py").read_text(encoding="utf-8")
        )
        direct = re.findall(r"(?<!def )_session_ghost_dead\(", all_src)
        # 合法直连仅一处：_session_ghost_dead_for_item 体内的委托（真源唯一出口）
        assert len(direct) == 1, f"ghost 闸出现绕过托管面的直连调用 {len(direct)} 处"


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v", "--tb=short"])
