"""commit_belt_daemon 单测（st-commitspeed-20260916）：单例锁/死信登记/once 模式。

不 spawn 真守护进程（对标 write_audit_daemon 测试先例）；watchdog 主循环
以 max_events 上界最小驱动。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge import commit_belt_daemon as cbd


class TestSingleton:
    def test_acquire_release(self, tmp_path):
        qroot = tmp_path / "commit_queue"
        qroot.mkdir(parents=True)
        assert cbd._acquire_singleton(qroot) is True
        # 二次获取=拒（活体 PID=当前进程）
        assert cbd._acquire_singleton(qroot) is False
        cbd._release_singleton(qroot)
        # 释放后可再取
        assert cbd._acquire_singleton(qroot) is True
        cbd._release_singleton(qroot)

    def test_zombie_lock_reclaimed(self, tmp_path):
        qroot = tmp_path / "commit_queue"
        qroot.mkdir(parents=True)
        (qroot / cbd._DAEMON_LOCK).write_text(
            json.dumps({"pid": 999999999, "ts": 0.0}), encoding="utf-8"
        )
        assert cbd._acquire_singleton(qroot) is True  # 僵尸锁回收
        cbd._release_singleton(qroot)


class TestDeadLetterLedger:
    def test_dead_letter_registered_to_ledger(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "bottleneck_ledger.jsonl")
        qroot = cbd._queue_root(tmp_path)
        (qroot / "dead").mkdir(parents=True)
        (qroot / "dead" / "q-20260916-sessA-0001.json").write_text(
            json.dumps({"qid": "q-20260916-sessA-0001", "session_id": "sessA", "dead_reason": "GATE-X 阻断: ..."}),
            encoding="utf-8",
        )
        seen: set[str] = set()
        n = cbd._ledger_dead_letters(tmp_path, seen)
        assert n == 1
        line = json.loads((tmp_path / "bottleneck_ledger.jsonl").read_text(encoding="utf-8").splitlines()[0])
        assert line["kind"] == "dead_letter" and line["qid"] == "q-20260916-sessA-0001"
        assert "专人专事" in line["protocol"]
        # 幂等：再跑不重复登记
        assert cbd._ledger_dead_letters(tmp_path, seen) == 0


class TestOnceMode:
    def test_once_never_raises(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = cbd.main(["--once", str(tmp_path)])
        assert rc == 0
