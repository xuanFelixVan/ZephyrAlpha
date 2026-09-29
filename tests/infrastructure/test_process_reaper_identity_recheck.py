# [MODULE] tests.infrastructure.test_process_reaper_identity_recheck
# [TTL] task_bound
# [STARTUP] on_demand_test（仅 pytest 触发，零 scheduled_task）
# [CONSUMERS] pytest；案卷 docs/_working/total_command_closeout/wave4/dr_chain_report.md §4.1
# [DOMAIN] D_INFRA_RUNTIME
# [INVARIANTS] 断言对象=杀前身份复验闸门：三要素任一不符必须赦免（不杀）且落 shadow 记账；
#   正常命中必须仍可杀（防"改到永不杀"的反向回归）；本文件零真杀（_kill_pid_tree 全程 stub）
"""P-28（Z-23）杀前身份复验回归网。

红证来源：案卷 X-08——旧实现 `_reap_incubated_expired()` 杀前只验"PID 在进程表存在"，
登记时 name/cmdline/create_time 从不参与比对，PID 复用（本仓实测 27-29 号撞同花顺/svchost）
即误杀无辜系统进程。三例：PID 复用 / 同 PID 换皮 / 正常命中。
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from zephyr.trading import process_reaper as pr

_T0 = 1_700_000_000.0  # 固定登记锚（2023-11，恒在实 now 之下＝判据必过寿命闸；禁 datetime.now()）


def _rec(pid: int, name: str, cmd: str, *, spawned: float = _T0 - 4000.0) -> dict:
    return {
        "record_id": f"rec-{pid}",
        "child_pid": pid,
        "name": name,
        "cmd": cmd,
        "spawned_at": spawned,
        "expected_lifetime_s": 60.0,
        "owner": "unit",
    }


def _live(pid: int, name: str, cmd: str, create_time: float, *, ppid: int = 4) -> dict:
    return {pid: {"name": name, "ppid": ppid, "create_time": create_time, "cmdline": cmd}}


@pytest.fixture()
def h(monkeypatch, tmp_path: Path):
    """把收割腿的三个副作用（真杀/台账回写/kill 日志）全部换成记录型 stub。"""

    class Harness:
        kill_calls: list[int]
        marks: list[str]
        report: pr.ReapReport

    h = Harness()
    h.kill_calls = []
    h.marks = []
    h.report = pr.ReapReport(timestamp="unit", dry_run=False)
    monkeypatch.setattr(pr, "_KILL_LOG", tmp_path / "reaper_kill.log")
    monkeypatch.setattr(pr, "_kill_pid_tree", lambda pid: (h.kill_calls.append(pid), True)[1])
    monkeypatch.setattr(pr, "_mark_incubation_reaped", lambda ids: (h.marks.append(",".join(ids)), len(ids))[1])
    return h


def _run(monkeypatch, h, rec: dict, live: dict, *, recheck: dict | None = None) -> None:
    monkeypatch.setattr(pr, "_load_incubation_ledger", lambda: [json.loads(json.dumps(rec))])
    pr._reap_incubated_expired(
        dict(live),
        False,
        h.report,
        whitelist_res=[],
        keep_subs=[],
        recheck=dict(live) if recheck is None else dict(recheck),
    )


def test_pid_reuse_is_spared_and_recorded(monkeypatch, h):
    """改前红证场景：PID 号还在进程表，但活体是"更晚出生的 svchost" ⇒ 旧实现必误杀。"""
    rec = _rec(4321, "python.exe", "python -m zephyr.data.scheduler --batch")
    live = _live(4321, "svchost.exe", r"C:\Windows\System32\svchost.exe -k netsvcs", _T0 - 900.0)
    # 前置：该 PID 在进程表存在且已过寿命（旧实现据此一刀切杀）
    assert 4321 in live
    _run(monkeypatch, h, rec, live)
    assert h.kill_calls == [], "PID 复用场景仍走杀路径＝P-28 未治本"
    assert h.marks == [], "赦免项不得回写 reaped（收敛归孵化方）"
    mism = h.report.identity_mismatches
    assert len(mism) == 1 and mism[0]["pid"] == 4321
    assert mism[0]["reason"].startswith("identity_mismatch:born_after_registration")
    assert h.report.killed == []


def test_same_pid_skin_swap_is_spared(monkeypatch, h):
    """同 PID 换皮：出生时刻对得上但镜像/命令行与登记不同源 ⇒ 镜像维度赦免。"""
    rec = _rec(5555, "python.exe", "python -m zephyr.governance.capability_lookup")
    live = _live(5555, "bash.exe", "bash -lc 'git stash pop'", _T0 - 3999.5)
    _run(monkeypatch, h, rec, live)
    assert h.kill_calls == []
    reasons = [m["reason"] for m in h.report.identity_mismatches]
    assert any("image_diverged" in r for r in reasons), reasons
    assert any("bash" in r for r in reasons), reasons


def test_normal_hit_still_reaped(monkeypatch, h):
    """正常命中：三要素全等 ⇒ 仍可收割（防"改到永不杀"的反向回归）。"""
    cmd = "python -m zephyr.data.tick_subscriber --lane unit"
    rec = _rec(7777, "python.exe", cmd)
    live = _live(7777, "python.exe", cmd, _T0 - 3999.0)
    _run(monkeypatch, h, rec, live)
    assert h.kill_calls == [7777]
    assert h.marks == ["rec-7777"]
    assert h.report.identity_mismatches == []
    assert h.report.killed[0]["pid"] == 7777 and h.report.killed[0]["killed"] is True


def test_absent_at_recheck_is_spared(monkeypatch, h):
    """复查时已自行退出（本轮读数里有、动杀前重取的现场表里没有）⇒ 赦免，方向同幽灵腿。"""
    rec = _rec(9090, "python.exe", "python -m zephyr.probe")
    stale = _live(9090, "python.exe", "python -m zephyr.probe", _T0 - 4000.0)
    fresh = _live(111, "python.exe", "python -c 1", _T0)  # 现场表：9090 已消失
    _run(monkeypatch, h, rec, stale, recheck=fresh)
    assert h.kill_calls == []
    assert h.report.identity_mismatches[0]["reason"] == "identity_mismatch:gone_at_recheck:pid_absent"


def test_missing_registration_fields_abstain(monkeypatch, h):
    """观测缺字段只能赦免方向弃权：登记无 name/cmd 时不因缺失而判，也不因缺失而杀。"""
    assert (
        pr.identity_mismatch_reason(rec_name="", rec_cmd="", rec_born_at=0.0, live=_live(1, "svchost.exe", "x", 0.0)[1])
        is None
    )
    # 但活体 create_time 存在 + 登记时刻存在 ⇒ 复用仍可判
    r = pr.identity_mismatch_reason(rec_name="", rec_cmd="", rec_born_at=_T0, live={"create_time": _T0 + 60.0})
    assert r is not None and r.startswith("born_after_registration")


def test_cmd_diverged_only_when_prefix_disagrees() -> None:
    """cmdline 维度：登记侧 300 字符截断 ⇒ 前缀互含视为同一身份（宁宽勿窄）。"""
    same = "python -m zephyr.probe --a 1 --b 2"
    assert (
        pr.identity_mismatch_reason(
            rec_name="python.exe", rec_cmd=same, rec_born_at=_T0, live=_live(2, "python.exe", same + " --tail", _T0)[2]
        )
        is None
    )
    assert (
        pr.identity_mismatch_reason(
            rec_name="python.exe",
            rec_cmd=same,
            rec_born_at=_T0,
            live=_live(3, "python.exe", "python -m zephyr.other", _T0)[3],
        )
        == "cmd_diverged:rec=python -m zephyr.probe --a 1 --b 2 live=python -m zephyr.other"
    )


def test_registration_anchor_is_now_used() -> None:
    """内收留痕：create_time 第三要素必须进判据（旧实现里 spawned_at 只算寿命、不参与身份）。"""
    src = Path(pr.__file__).read_text(encoding="utf-8")
    assert "born_after_registration" in src and "identity_mismatch" in src
    # 登记时刻与活体出生时刻同源于 psutil 进程表字段（快照三要素齐备）
    assert '"create_time"' in src
