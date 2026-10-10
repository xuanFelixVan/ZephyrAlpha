# [MODULE] tests.infrastructure.test_process_reaper_pid_recycle_backfix
# [TTL] task_bound
# [STARTUP] on_demand_test（仅 pytest 触发，零 scheduled_task）
# [CONSUMERS] pytest；案卷 docs/_working/backfix_campaign/00_ledger.md 案 #5-#9 + 总统统筹批复 2026-10-10
# [DOMAIN] D_INFRA_RUNTIME
# [INVARIANTS] pid 回收复刻场景必拦：孵化台账陈旧条目（原主已死+create_time 过期+永不销账）
#   遇 pid 被回收给 backup.ps1 活体时——必不杀（三要素复核+backup 活体白名单双闸）、
#   必销账（exited_at 回写，条目退出 active 面）；正常超寿 worker 仍可杀（反向回归）。
#   本文件零真杀（_kill_pid_tree 全程 stub）；台账回写指向 tmp 副本（测试隔离禁写生产路径）。
"""backfix 批复①+②红蓝网（2026-10-10，案 #5-#9 连环实证）。

案 #8 铁证：孵化台账条目 24507cf3fab1（child_pid=3684，原主=10-06 pytest 造
reconcile-worker，reaped=false/exited_at=null 永不销账）遇 Windows pid 回收把
3684 发给备份 powershell——任何无 create_time 复核的账本消费者都会"合法"处决备份。
批复处方：①销账（exited_at 必写）+create_time 身份复核推广；②账本消费者跳过
cmdline 含 backup.ps1 的活体 pid。本文件锁住两个"必"。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.trading import process_reaper as pr

_BASE = 1_700_000_000.0  # 恒 past 锚（禁 datetime.now()，与 P-28 网同款）
_SPAWNED = _BASE  # 登记时刻；案 #8 条目形态=登记后四天 pid 被回收（超期 4 天）


@pytest.fixture()
def h(monkeypatch, tmp_path: Path):
    class Harness:
        kill_calls: list[int]
        marks: list[str]
        exited_marks: list[str]
        report: pr.ReapReport

    h = Harness()
    h.kill_calls = []
    h.marks = []
    h.exited_marks = []
    h.report = pr.ReapReport(timestamp="unit", dry_run=False)
    monkeypatch.setattr(pr, "_KILL_LOG", tmp_path / "reaper_kill.log")
    monkeypatch.setattr(pr, "_kill_pid_tree", lambda pid: (h.kill_calls.append(pid), True)[1])
    monkeypatch.setattr(pr, "_mark_incubation_reaped", lambda ids: (h.marks.append(",".join(ids)), len(ids))[1])
    monkeypatch.setattr(pr, "_mark_incubation_exited", lambda ids: (h.exited_marks.append(",".join(ids)), len(ids))[1])
    return h


def _run(monkeypatch, h, rec: dict, live: dict) -> None:
    monkeypatch.setattr(pr, "_load_incubation_ledger", lambda: [json.loads(json.dumps(rec))])
    pr._reap_incubated_expired(dict(live), False, h.report, whitelist_res=[], keep_subs=[])


def test_pid_recycle_onto_backup_must_block(monkeypatch, h):
    """批复红证（案 #8 复刻）：陈旧 reconcile-worker 条目 + pid 被回收给 backup.ps1
    活体（出生晚于登记四天）⇒ 必不杀 + 身份复核留痕 + 销账（exited_at，非 reaped）。"""
    rec = {
        "record_id": "24507cf3fab1",
        "child_pid": 3684,
        "name": "python.exe",
        "cmd": "python -m zephyr.governance.audit.reconcile_worker --payload x.json",
        "spawned_at": _SPAWNED,
        "expected_lifetime_s": 1800.0,
        "owner": "reconcile_runner",
        "child_create_time": _SPAWNED,
    }
    live = {
        3684: {
            "name": "powershell.exe",
            "ppid": 34588,
            "create_time": _BASE + 4 * 24 * 3600.0,  # 四天后出生=回收者（恒 past，早于实 now）
            "cmdline": r"D:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -File D:\ZephyrAlpha\scripts\backup\backup.ps1",
        }
    }
    _run(monkeypatch, h, rec, live)
    assert h.kill_calls == [], "pid 回收复刻场景走杀路径=批复红证未拦"
    reasons = [m["reason"] for m in h.report.identity_mismatches]
    assert any("born_after_registration" in r for r in reasons), reasons
    assert h.exited_marks == ["24507cf3fab1"], "销账缺失=条目永滞、下轮继续瞄准备份"
    assert h.marks == [], "赦免项不得标 reaped（P-28 契约：收敛语义分离）"
    assert h.report.killed == []


def test_live_backup_cmdline_skipped_even_with_clean_identity(monkeypatch, h):
    """处方②第三道闸：三要素全符（身份复核弃权）但活体 cmdline 含 backup.ps1 的
    超寿 pid 仍必跳过——防未来账本登记面把备份注册进台账后按寿命处决（belt 2）。"""
    backup_cmd = r"powershell.exe -File D:\ZephyrAlpha\scripts\backup.ps1"
    rec = {
        "record_id": "oldfmt-0001",
        "child_pid": 46216,
        "name": "powershell.exe",
        "cmd": backup_cmd,
        "spawned_at": _SPAWNED,
        "expected_lifetime_s": 1800.0,
        "owner": "unit",
        # 无 child_create_time 键=旧格式，born_after 以 spawned 为锚弃权
    }
    live = {
        46216: {
            "name": "powershell.exe",
            "ppid": 1,
            "create_time": _SPAWNED,  # 同刻出生（不构成回收），但活体是备份且已超寿
            "cmdline": backup_cmd,
        }
    }
    _run(monkeypatch, h, rec, live)
    assert h.kill_calls == [], "backup.ps1 活体白名单失效"
    assert any(r.get("reason") == "incubation_expired_backup_whitelisted" for r in h.report.reported), h.report.reported
    assert h.report.killed == []


def test_dead_child_entry_gets_exited_at(monkeypatch, h):
    """批复销账①a：登记的 pid 已不在进程表（孩子确已消亡）⇒ 销账（exited_at），
    条目退出 active 面——永不销账=pid 回收暴露的根源（案 #8）。"""
    rec = {
        "record_id": "dead-0001",
        "child_pid": 59999,
        "name": "python.exe",
        "cmd": "python -m zephyr.governance.audit.reconcile_worker --payload z.json",
        "spawned_at": _SPAWNED,
        "expected_lifetime_s": 1800.0,
        "owner": "reconcile_runner",
    }
    live = {111: {"name": "python.exe", "ppid": 1, "create_time": _BASE, "cmdline": "python -c 1"}}
    _run(monkeypatch, h, rec, live)
    assert h.kill_calls == []
    assert h.exited_marks == ["dead-0001"], "pid 已消亡的条目必须销账"


def test_normal_expired_worker_still_killed(monkeypatch, h):
    """反向回归：身份三要素全符的真超寿 worker 必仍可杀（防改到永不杀）。"""
    cmd = "python -m zephyr.governance.audit.reconcile_worker --payload real.json"
    rec = {
        "record_id": "real-0001",
        "child_pid": 7777,
        "name": "python.exe",
        "cmd": cmd,
        "spawned_at": _BASE - 3600.0,
        "expected_lifetime_s": 1800.0,
        "owner": "reconcile_runner",
        "child_create_time": _BASE - 3599.0,  # 登记快照≈活体出生（容差 1s 内）
    }
    live = {
        7777: {
            "name": "python.exe",
            "ppid": 1,
            "create_time": _BASE - 3599.5,
            "cmdline": cmd,
        }
    }
    _run(monkeypatch, h, rec, live)
    assert h.kill_calls == [7777], "真超寿 worker 被赦免=反向回归（改到永不杀）"
    assert h.marks == ["real-0001"]
    assert h.exited_marks == [], "正常收割不得重复销账"
