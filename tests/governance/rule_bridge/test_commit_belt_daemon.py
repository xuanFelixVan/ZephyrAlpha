# [BLUEPRINT] MOD-GOV_COMMIT_GATES | (auto-injected by S4 reconciler) | §
# [TTL] permanent
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


class TestBacklogAlert:
    """P2 堵点本阈值告警（Owner 2026-09-16 晚授权自裁）：≥20 条或最老>24h → alert 行。"""

    def _write_ledger(self, path, items, old_first_hours=None):
        import json as _json
        from datetime import datetime, timedelta, timezone

        cst = timezone(timedelta(hours=8))
        with path.open("w", encoding="utf-8") as fh:
            for i in range(items):
                ts = (datetime.now(cst) - timedelta(hours=old_first_hours)).isoformat() if (i == 0 and old_first_hours) else datetime.now(cst).isoformat()
                fh.write(_json.dumps({"ts": ts, "kind": "dead_letter", "qid": f"q-{i}"}) + "\n")

    def test_threshold_alert_written(self, tmp_path, monkeypatch):
        import json as _json
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "bottleneck_ledger.jsonl")
        self._write_ledger(tmp_path / "bottleneck_ledger.jsonl", 20, old_first_hours=25)
        cbd._check_ledger_backlog()
        lines = (tmp_path / "bottleneck_ledger.jsonl").read_text(encoding="utf-8").splitlines()
        alerts = [_json.loads(x) for x in lines if _json.loads(x).get("kind") == "alert"]
        assert alerts and alerts[0]["alert"] == "bottleneck_backlog_threshold"
        assert alerts[0]["pending_items"] == 20

    def test_below_threshold_no_alert(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "bottleneck_ledger.jsonl")
        self._write_ledger(tmp_path / "bottleneck_ledger.jsonl", 5)  # 新鲜少量
        cbd._check_ledger_backlog()
        assert "alert" not in (tmp_path / "bottleneck_ledger.jsonl").read_text(encoding="utf-8")

    def test_old_entry_triggers_age_alert(self, tmp_path, monkeypatch):
        import json as _json
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "bottleneck_ledger.jsonl")
        self._write_ledger(tmp_path / "bottleneck_ledger.jsonl", 3, old_first_hours=25)  # 少量但首条 25h 老
        cbd._check_ledger_backlog()
        content = (tmp_path / "bottleneck_ledger.jsonl").read_text(encoding="utf-8")
        assert "bottleneck_backlog_threshold" in content


class TestEnvAbortEscalation:
    """P3 债1：连续环境失败 ≥3 → CRITICAL 行；成功复位。"""

    def test_escalation_and_reset(self, tmp_path, monkeypatch):
        import json as _json
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "bottleneck_ledger.jsonl")
        st = {}
        cbd._escalate_env_aborts(st)
        cbd._escalate_env_aborts(st)
        assert not (tmp_path / "bottleneck_ledger.jsonl").exists()  # 未达阈不写
        cbd._escalate_env_aborts(st)  # 第 3 次 → 写
        content = (tmp_path / "bottleneck_ledger.jsonl").read_text(encoding="utf-8")
        assert "serializer_env_abort_loop" in content
        st["env_aborts"] = 0  # 复位语义
        cbd._escalate_env_aborts(st)
        assert st["env_aborts"] == 1
