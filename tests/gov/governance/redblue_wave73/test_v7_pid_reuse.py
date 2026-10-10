# [TTL] permanent
# [MODULE] tests.governance.redblue_wave73.test_v7_pid_reuse
# [DOMAIN] D_TRADING
"""wave7.3 V7 PID 复用：收割闭环身份复核防在（与缺陷②修复配套）。

攻击：孵化台账登记的 child_pid 已退出，系统将该 pid 复发给无关进程；
reaper _reap_incubated_expired 若只查 pid 在册即收割 = 误杀无辜。
防御在（wave7.3 修复；留痕通道按 465f2779=backfix 批复① 2026-10-10 对齐）：登记侧
child_create_time 快照 vs 活体三要素复核，任一不符 → 赦免 + 记 identity_mismatches
（旧通道 reason=incubation_expired_pid_reuse_skip 已退役）+ 非 dry_run 时销账 exited_at。
全程 dry_run——证判定不真杀（复用 pid 现实中可能是无辜活体）。
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.trading import process_reaper as pr  # noqa: E402


def test_pid_reused_by_innocent_process_is_not_reaped(tmp_path, monkeypatch):
    ledger = tmp_path / "process_incubator" / "ledger.jsonl"
    monkeypatch.setattr(pr, "_INCUBATOR_LEDGER_REL", ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "record_id": "v7-rec",
        "child_pid": 4294901700,
        "cmd": "python worker.py",
        "spawned_at": time.time() - 3600,
        "expected_lifetime_s": 60.0,
        "owner": "v7",
        "exited_at": None,
        "reaped": False,
        "child_create_time": 1000.0,  # 登记时快照（原进程出生时间）
    }
    ledger.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    live = {
        4294901700: {  # 同号 pid，但 create_time 是复用者的（现在）
            "pid": 4294901700,
            "ppid": 1,
            "cmdline": "innocent_service.exe --port 80",
            "name": "innocent",
            "create_time": time.time(),
        }
    }
    report = pr.ReapReport(dry_run=True)
    pr._reap_incubated_expired(live, dry_run=True, report=report)
    assert report.killed == [], "PID 复用者被进入收割判定——V7 误杀成立（防御缺位）"
    # 留痕通道按 465f2779（backfix 批复①，2026-10-10）对齐：三要素身份不符=赦免并记
    # identity_mismatches；销账（exited_at）只在非 dry_run 分支发生，dry_run 零副作用故此处不钉。
    assert len(report.identity_mismatches) == 1, "身份不符未进 identity_mismatches=留痕通道丢失"
    assert report.identity_mismatches[0]["pid"] == 4294901700
    assert "born_after_registration" in report.identity_mismatches[0]["reason"], "pid 复用的机读标记丢失"
    assert report.reported == [], "旧通道已退役——双通道重复记账即红"
