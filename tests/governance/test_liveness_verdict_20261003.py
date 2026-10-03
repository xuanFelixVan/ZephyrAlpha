# [A_test] module_id: MOD-GOV_liveness_verdict | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_liveness_verdict_20261003
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] pytest；zephyr.security.access_control.session_concurrency（liveness_verdict 裁决表）
# [CONSUMERS] pytest（tests/governance/）
# [INVARIANTS] 裁定#480 C-2 活性合流裁决表测试——tmp_path 全隔离（monkeypatch.chdir 假 root，零真库/零真 registry）；裁决时刻 now=固定常量（零墙钟依赖）；覆盖 8 信号逐级触发/优先级压倒（P1 压 alive、P2 压 dead、P4 压 P5）/边界（恰好 90s/1800s/1860s/3600s）/pid=0 与 pid>0 双轨/纯读零副作用；阈值断言锚定模块常量（90=_HEARTBEAT_TIMEOUT_SECONDS 等），禁写死漂移
# [MODIFY-GUARD] 判据/优先级变更须与 src/zephyr/security/access_control/session_concurrency.py 的 liveness_verdict 同批
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；不写生产路径（宪法 §9.6）
# [TESTS] self
# [A_module] module_id=MOD-GOV_liveness_verdict | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# -*- coding: utf-8 -*-
"""test_liveness_verdict_20261003.py — 裁定#480 C-2 活性合流：单一活性裁决表测试。

覆盖面（对应任务书四要求）：
1. 8 信号逐级触发（P1 接管待决/P2 回魂/P3 ghost/P4 三种判死/P5 两种降级/P6 存活）；
2. 优先级压倒（P1 压过 alive、P2 压过 dead、P4 压过 P5——低级只作 reasons 旁证）；
3. 边界（恰好 90s/1800s/1860s/3600s 均不越界——与既有判据同向 ``>`` 口径）；
4. pid=0（心跳轨）与 pid>0（PID+TTL 双轨）分轨判死；纯读零写副作用。
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

import zephyr.security.access_control.session_concurrency as sc

# 固定裁决时刻（所有时间锚/审计 ts/文件 mtime 全部锚定它，零墙钟）
NOW = 1_900_000_000.0
SID = "sess-lv-probe"
DEAD_PID = 4_000_000  # 不存在的进程（is_pid_alive 实测 False）


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """假仓根：chdir 进 tmp（anchor_main_root 对非 worktree 路径原样返回，测试隔离保持）。"""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _entry(**over: object) -> dict:
    """构造一条健康的 pid=0 注册表条目（缺省全锚=NOW）。"""
    base: dict = {
        "session_id": SID,
        "pid": 0,
        "start_time": NOW,
        "held_files": [],
        "last_heartbeat": NOW,
        "last_activity": NOW,
        "is_breaking_change": False,
        "task_files": [],
        "depends_on_sessions": [],
        "logical": False,
        "last_register_ts": NOW,
        "reincarnation_count": 0,
    }
    base.update(over)
    return base


def _write_shard(root: Path, entry: dict, sid: str = SID) -> None:
    d = root / ".runtime" / "session_registry"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{sid}.json").write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")


def _write_heartbeat_file(root: Path, sid: str = SID, age: float = 30.0) -> None:
    p = root / ".runtime" / "sessions" / sid / "heartbeat.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}\n", encoding="utf-8")
    os.utime(p, (NOW - age, NOW - age))


def _append_audit(root: Path, name: str, sid: str = SID, age: float = 100.0) -> None:
    d = root / ".runtime" / "session_registry_audit"
    d.mkdir(parents=True, exist_ok=True)
    ts = datetime.fromtimestamp(NOW - age, tz=timezone.utc).isoformat()
    rec = {"ts": ts, "pid": os.getpid(), "event": name, "session_id": sid}
    with (d / name).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _append_takeover(root: Path, sid: str = SID, status: str = "open") -> None:
    d = root / ".runtime"
    d.mkdir(parents=True, exist_ok=True)
    row = {"sid": sid, "status": status, "ts_epoch": NOW - 60.0, "ts": "iso"}
    with (d / "takeover_ledger.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# P6 存活（含 pid=0 / pid>0 双轨与 90s/TTL 边界）
# ---------------------------------------------------------------------------


def test_session_alive_pid0_fresh_heartbeat(repo: Path) -> None:
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 30))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"
    assert v.authoritative_signal == "REGISTRY-FRESH"
    assert v.checked_at == NOW


def test_session_alive_pid0_boundary_heartbeat_exactly_90s(repo: Path) -> None:
    """恰好 90s：与 _is_session_alive 同向（> 判死），等于阈值=未越界。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - sc._HEARTBEAT_TIMEOUT_SECONDS))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"


def test_session_alive_pid_positive_skips_90s_window(repo: Path) -> None:
    """双轨：pid>0 不走 90s 心跳窗——心跳 300s 陈旧但 TTL 内+进程在岗=存活。"""
    _write_shard(repo, _entry(pid=os.getpid(), last_heartbeat=NOW - 300))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"
    assert v.authoritative_signal == "REGISTRY-FRESH"


def test_session_dead_pid_positive_ttl_boundary(repo: Path) -> None:
    """pid>0 TTL 兜底边界：恰 3600s=存活，3601s=TTL-EXPIRED。"""
    _write_shard(repo, _entry(pid=os.getpid(), last_heartbeat=NOW - sc._SESSION_TTL_SECONDS))
    assert sc.liveness_verdict(SID, now=NOW).state == "alive"
    _write_shard(repo, _entry(pid=os.getpid(), last_heartbeat=NOW - sc._SESSION_TTL_SECONDS - 1))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "dead"
    assert v.authoritative_signal == "TTL-EXPIRED"


# ---------------------------------------------------------------------------
# P4 判死（② 90s 心跳窗 / ① PID 轨；③ 墓碑宽限折入 reason）
# ---------------------------------------------------------------------------


def test_session_dead_pid0_stale_just_over_90s_tombstone_grace(repo: Path) -> None:
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - sc._HEARTBEAT_TIMEOUT_SECONDS - 1))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "dead"
    assert v.authoritative_signal == "HEARTBEAT-STALE"
    assert v.reasons[0].startswith("心跳停止")
    assert "墓碑宽限" in v.reasons[0]  # 91s < 900s → 宽限内文案


def test_session_dead_pid0_beyond_reap_grace(repo: Path) -> None:
    """超 15m 收割宽限（③ 折入）：reason 切换为"已超宽限"文案。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - sc._REAP_GRACE_SECONDS - 100))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "dead"
    assert "已超 15 分钟收割宽限" in v.reasons[0]


def test_session_dead_pid_positive_dead_pid_beats_fresh_heartbeat(repo: Path) -> None:
    """pid>0：进程死=零窗口判死，心跳再新鲜也没用（①PID 轨压 ②心跳信号）。"""
    _write_shard(repo, _entry(pid=DEAD_PID, last_heartbeat=NOW - 5))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "dead"
    assert v.authoritative_signal == "PID-DEAD"


# ---------------------------------------------------------------------------
# P3 ghost（⑥ 拾取闸口径：注册表无片+无心跳>90s）
# ---------------------------------------------------------------------------


def test_session_ghost_no_shard_no_heartbeat_file(repo: Path) -> None:
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "ghost"
    assert v.authoritative_signal == "GHOST-NO-SHARD"
    assert v.reasons[0].startswith("幽灵会话")


def test_session_ghost_no_shard_stale_heartbeat_file(repo: Path) -> None:
    _write_heartbeat_file(repo, age=sc._HEARTBEAT_TIMEOUT_SECONDS + 110)
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "ghost"


def test_session_alive_no_shard_but_fresh_heartbeat_file(repo: Path) -> None:
    """ghost 需双条件：无片+心跳不新鲜；心跳文件新鲜=守护在岗的存活旁证。"""
    _write_heartbeat_file(repo, age=30)
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"
    assert "旁证" in v.reasons[0]


# ---------------------------------------------------------------------------
# P2 回魂违规（⑤ 回魂闸：静态判据 + 审计事件；压过 P4 dead）
# ---------------------------------------------------------------------------


def test_session_reincarnation_static_beats_dead(repo: Path) -> None:
    """优先级压倒：投胎次数超限（心跳同时 stale）→ ghost 压过 dead。"""
    _write_shard(
        repo,
        _entry(
            pid=0,
            held_files=[],
            task_files=[],
            last_heartbeat=NOW - 500,
            reincarnation_count=sc.SessionRegistry._REINCARNATION_LIMIT + 1,
        ),
    )
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "ghost"
    assert v.authoritative_signal == "REINCARNATION-VIOLATION"
    assert v.reasons[0].startswith("回魂违规")  # 获胜级 reason 在首位
    assert any(r.startswith("心跳停止") for r in v.reasons[1:])  # P4 作旁证


def test_session_reincarnation_by_age_over_6h(repo: Path) -> None:
    """年龄辅判据：count 未超限但条目超 6h 寿命上限 → 仍判回魂。"""
    _write_shard(
        repo,
        _entry(
            pid=0,
            held_files=[],
            task_files=[],
            start_time=NOW - sc.SessionRegistry._MAX_SESSION_LIFETIME_SECONDS - 600,
            last_heartbeat=NOW - 500,
            reincarnation_count=2,
        ),
    )
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "ghost"
    assert v.authoritative_signal == "REINCARNATION-VIOLATION"


def test_session_reincarnation_below_limit_stays_dead(repo: Path) -> None:
    """误杀防护：count/age 均未达 → 不判回魂，按心跳 stale 判 dead。"""
    _write_shard(repo, _entry(pid=0, held_files=[], task_files=[], last_heartbeat=NOW - 500, reincarnation_count=2))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "dead"
    assert v.authoritative_signal == "HEARTBEAT-STALE"


def test_session_reincarnation_held_files_exempts(repo: Path) -> None:
    """误杀防护：有 claim（在干活）→ 回魂判据不成立（与 _is_reanimation 同硬前提）。"""
    _write_shard(
        repo,
        _entry(
            pid=0,
            held_files=["D:/x/src/a.py"],
            task_files=[],
            last_heartbeat=NOW - 500,
            reincarnation_count=sc.SessionRegistry._REINCARNATION_LIMIT + 3,
        ),
    )
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "dead"  # 不回魂，走 P4


def test_session_reincarnation_fresh_heartbeat_file_exempts(repo: Path) -> None:
    """误杀防护：心跳守护在岗（文件 mtime<120s 窗）→ 外部佐证阻断回魂判据。"""
    _write_shard(
        repo,
        _entry(
            pid=0,
            held_files=[],
            task_files=[],
            last_heartbeat=NOW - 30,
            reincarnation_count=sc.SessionRegistry._REINCARNATION_LIMIT + 3,
        ),
    )
    _write_heartbeat_file(repo, age=30)
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"


def test_session_reanimation_recent_audit_event(repo: Path) -> None:
    """⑤ 审计面：1860s 窗内 register_reanimation 事件 → ghost（条目心跳还新鲜也压）。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 30))
    _append_audit(repo, "register_reanimation.jsonl", age=100)
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "ghost"
    assert v.authoritative_signal == "REINCARNATION-VIOLATION"


def test_session_reanimation_audit_boundary_exactly_1860(repo: Path) -> None:
    """回魂审计窗边界：恰好 1860s=窗已过，不再压（与 V5 护栏 < 窗同口径）。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 30))
    _append_audit(repo, "register_reanimation.jsonl", age=sc._REREGISTER_MIN_INTERVAL_SECONDS)
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"


# ---------------------------------------------------------------------------
# P1 接管待决（⑦ 台账 open 条目：压过一切活性信号）
# ---------------------------------------------------------------------------


def test_session_takeover_pending_beats_alive(repo: Path) -> None:
    """优先级压倒：条目心跳全新鲜 + 台账 open → dead（P1 压过 P6 alive）。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 10))
    _write_heartbeat_file(repo, age=10)
    _append_takeover(repo, status="open")
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "dead"
    assert v.authoritative_signal == "TAKEOVER-PENDING"
    assert v.reasons[0].startswith("接管待决")


def test_session_takeover_resolved_not_authoritative(repo: Path) -> None:
    """台账已 resolve=不立案，活性信号回归主导。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 10))
    _append_takeover(repo, status="resolved")
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"


# ---------------------------------------------------------------------------
# P5 降级（④ V5 降级窗 / ④b 守护自退 1800s）
# ---------------------------------------------------------------------------


def test_session_degraded_rate_guard_recent(repo: Path) -> None:
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 30))
    _append_audit(repo, "register_rate_guard.jsonl", age=100)
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "degraded"
    assert v.authoritative_signal == "RATE-GUARD-DOWNGRADED"
    assert v.reasons[0].startswith("降级重建中")


def test_session_degraded_rate_guard_boundary_exactly_1860(repo: Path) -> None:
    """④ 窗边界：降级审计恰好 1860s 前=窗已过，不再降级。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 30))
    _append_audit(repo, "register_rate_guard.jsonl", age=sc._REREGISTER_MIN_INTERVAL_SECONDS)
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"


def test_session_degraded_idle_boundary_exactly_1800(repo: Path) -> None:
    """④b 边界：idle 恰 1800s=未越界（alive）；1801s=守护超期降级。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 30, last_activity=NOW - sc._ACTIVITY_IDLE_TIMEOUT_SECONDS))
    assert sc.liveness_verdict(SID, now=NOW).state == "alive"
    _write_shard(
        repo, _entry(pid=0, last_heartbeat=NOW - 30, last_activity=NOW - sc._ACTIVITY_IDLE_TIMEOUT_SECONDS - 1)
    )
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "degraded"
    assert v.authoritative_signal == "DAEMON-IDLE-OVERDUE"


def test_session_logical_exempt_from_idle_degraded(repo: Path) -> None:
    """W-29：logical=True（chief 形态）豁免 ④b 守护自退判据。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 30, last_activity=NOW - 9999, logical=True))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"


def test_session_pid_positive_idle_not_degraded(repo: Path) -> None:
    """④b 是 pid=0 守护模型判据：pid>0 在岗进程 idle 不降级（活性真源=进程本身）。"""
    _write_shard(repo, _entry(pid=os.getpid(), last_heartbeat=NOW - 30, last_activity=NOW - 9999))
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "alive"


# ---------------------------------------------------------------------------
# 优先级：P4 dead 压过 P5 degraded（低级仅作旁证）
# ---------------------------------------------------------------------------


def test_session_dead_beats_degraded(repo: Path) -> None:
    """心跳 stale>90s + 近窗降级审计并存 → 结论 dead；降级 reason 降为旁证。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 200))
    _append_audit(repo, "register_rate_guard.jsonl", age=100)
    v = sc.liveness_verdict(SID, now=NOW)
    assert v.state == "dead"
    assert v.authoritative_signal == "HEARTBEAT-STALE"
    assert any(r.startswith("降级重建中") for r in v.reasons[1:])


# ---------------------------------------------------------------------------
# 契约面：dataclass 形状 + 纯读零副作用
# ---------------------------------------------------------------------------


def test_session_verdict_dataclass_shape(repo: Path) -> None:
    v = sc.liveness_verdict(SID, now=NOW)
    assert isinstance(v, sc.LivenessVerdict)
    assert v.state in {"alive", "degraded", "dead", "ghost"}
    assert isinstance(v.reasons, list) and v.reasons
    assert isinstance(v.authoritative_signal, str) and v.authoritative_signal
    assert v.session_id == SID


def test_session_verdict_is_readonly_no_file_writes(repo: Path) -> None:
    """纯函数铁证：裁决前后假仓文件面零变化（不写/不 mkdir）。"""
    _write_shard(repo, _entry(pid=0, last_heartbeat=NOW - 30))
    _write_heartbeat_file(repo, age=10)
    _append_audit(repo, "register_rate_guard.jsonl", age=100)
    _append_takeover(repo, status="open")
    before = sorted(str(p.relative_to(repo)) for p in repo.rglob("*"))
    sc.liveness_verdict(SID, now=NOW)
    sc.liveness_verdict(SID, now=NOW + 1)  # 复跑防懒写
    after = sorted(str(p.relative_to(repo)) for p in repo.rglob("*"))
    assert before == after
