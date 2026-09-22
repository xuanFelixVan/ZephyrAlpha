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
        (qroot / cbd._DAEMON_LOCK).write_text(json.dumps({"pid": 999999999, "ts": 0.0}), encoding="utf-8")
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
                ts = (
                    (datetime.now(cst) - timedelta(hours=old_first_hours)).isoformat()
                    if (i == 0 and old_first_hours)
                    else datetime.now(cst).isoformat()
                )
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


# ── 裁定#281①：纪元自检三态（未变不重启/变了安全点 execv/lease 被持不重启）──


def _epoch_mod():
    return cbd


def _fake_execv(monkeypatch, calls):
    import os as _os

    def _fake(exec_path, argv):
        calls.append((exec_path, argv))

    monkeypatch.setattr(_os, "execv", _fake)


def test_epoch_unchanged_no_reexec(tmp_path, monkeypatch):
    """纪元未变 → 不重启（drain 正常继续）。"""
    mod = _epoch_mod()
    calls: list = []
    _fake_execv(monkeypatch, calls)
    monkeypatch.setattr(mod, "_gov_enforcement_epoch", lambda root: "sha-same")
    # 判据子树单独 stub：tmp_path 落在真仓内，不 stub 会取到真 sha 造出假"纪元变更"
    monkeypatch.setattr(mod, "_subtree_epoch", lambda root, sub: None)
    # D4（st-commitchain-20260922）第三子树：commit_queue 文件 blob 同理必须 stub
    monkeypatch.setattr(mod, "_commit_queue_epoch", lambda root: None)
    monkeypatch.setattr(mod, "_serializer_lease_held", lambda qroot: False)
    state: dict = {"epoch": "sha-same"}
    assert mod._check_and_reexec(tmp_path, tmp_path, state) is False
    assert calls == []


def test_epoch_changed_reexecs_at_safe_point(tmp_path, monkeypatch):
    """纪元变更 + lease 已释放（安全点）→ 单例锁先释放、execv 原地替换进程。"""
    mod = _epoch_mod()
    calls: list = []
    _fake_execv(monkeypatch, calls)
    monkeypatch.setattr(mod, "_gov_enforcement_epoch", lambda root: "sha-new")
    monkeypatch.setattr(mod, "_subtree_epoch", lambda root, sub: None)
    monkeypatch.setattr(mod, "_commit_queue_epoch", lambda root: None)
    monkeypatch.setattr(mod, "_serializer_lease_held", lambda qroot: False)
    # 预置活体单例锁（真实位置=<root>/.runtime/commit_queue/）→ execv 前必须被释放
    # （execv 不跑 finally，不释放=新进程被锁挡死 exit 2）
    qroot = tmp_path / ".runtime" / "commit_queue"
    qroot.mkdir(parents=True, exist_ok=True)
    lock = qroot / mod._DAEMON_LOCK
    lock.write_text(json.dumps({"pid": 1, "ts": 0.0}), encoding="utf-8")
    state: dict = {"epoch": "sha-old"}
    assert mod._check_and_reexec(tmp_path, tmp_path, state) is True
    assert len(calls) == 1
    assert not lock.exists(), "execv 前必须释放单例锁"


def test_epoch_changed_but_lease_held_defers(tmp_path, monkeypatch):
    """lease 被持（非安全点）→ 不重启，等下一个安全点。"""
    mod = _epoch_mod()
    calls: list = []
    _fake_execv(monkeypatch, calls)
    monkeypatch.setattr(mod, "_gov_enforcement_epoch", lambda root: "sha-new")
    monkeypatch.setattr(mod, "_subtree_epoch", lambda root, sub: None)
    monkeypatch.setattr(mod, "_serializer_lease_held", lambda qroot: True)
    state: dict = {"epoch": "sha-old"}
    assert mod._check_and_reexec(tmp_path, tmp_path, state) is False
    assert calls == []


def test_criteria_subtree_only_change_also_reexecs(tmp_path, monkeypatch):
    """判据真源子树单独变更也要 re-exec——旧口径只测 src/zephyr/gov_enforcement，
    extractor（scripts/governance/_shared）治本对常驻守护永不可见：红蓝实弹 R1/R3
    经生产队列落地的正是这个盲区（守护 07:17 常驻，死块判据符号 21:58 才进 extractor）。
    """
    mod = _epoch_mod()
    calls: list = []
    _fake_execv(monkeypatch, calls)
    monkeypatch.setattr(mod, "_gov_enforcement_epoch", lambda root: "sha-gate")
    monkeypatch.setattr(
        mod,
        "_subtree_epoch",
        lambda root, sub: "sha-gate" if sub == mod._PRIMARY_SUBTREE else "sha-crit-new",
    )
    monkeypatch.setattr(mod, "_serializer_lease_held", lambda qroot: False)
    state: dict = {"epoch": "sha-gate|sha-crit-old"}
    assert mod._check_and_reexec(tmp_path, tmp_path, state) is True
    assert len(calls) == 1


class TestBacklogAlertCooldown:
    """R-06（S18 kimi-audit G2）：堵点本告警冷却状态机。

    改前：越阈期间每 tick 重写同一事实（取证：1095 行同事实告警，落盘间隔
    P50 2.0s）。改后：同档位 30min 内不重复落盘；档位翻转（↑↓跨档）立即落盘；
    冷却期后同档位重报。阈值判据与告警内容语义零变化（仅新增 backlog_level 字段）。
    """

    @staticmethod
    def _write_ledger(path, items, old_first_hours=None, keep_alerts=False):
        """重写账本条目；keep_alerts=True 时保留既有 alert 行（生产账本 append-only，
        告警行永不消失——"清账/账龄翻转"=非告警条目变化，告警历史保留）。"""
        import json as _json
        from datetime import datetime, timedelta, timezone

        alerts = []
        if keep_alerts and path.exists():
            alerts = [
                x
                for x in path.read_text(encoding="utf-8").splitlines()
                if x.strip() and _json.loads(x).get("kind") == "alert"
            ]
        cst = timezone(timedelta(hours=8))
        with path.open("w", encoding="utf-8") as fh:
            for i in range(items):
                ts = (
                    (datetime.now(cst) - timedelta(hours=old_first_hours)).isoformat()
                    if (i == 0 and old_first_hours)
                    else datetime.now(cst).isoformat()
                )
                fh.write(_json.dumps({"ts": ts, "kind": "dead_letter", "qid": f"q-{i}"}) + "\n")
            for a in alerts:
                fh.write(a + "\n")

    @staticmethod
    def _alerts(path):
        import json as _json

        if not path.exists():
            return []
        return [
            _json.loads(x)
            for x in path.read_text(encoding="utf-8").splitlines()
            if x.strip() and _json.loads(x).get("kind") == "alert"
        ]

    def test_same_level_suppressed_within_cooldown(self, tmp_path, monkeypatch):
        """同档位连发被冷却：20 条积压连查 3 次 → 只落盘 1 行告警。"""
        ledger = tmp_path / "bottleneck_ledger.jsonl"
        monkeypatch.setattr(cbd, "_LEDGER", ledger)
        self._write_ledger(ledger, 20)  # 新鲜足量 → 档位 "count"
        for _ in range(3):
            cbd._check_ledger_backlog()
        alerts = self._alerts(ledger)
        assert len(alerts) == 1, alerts
        assert alerts[0]["backlog_level"] == "count"
        # 冷却状态已持久化（与账本同目录）
        state = json.loads(cbd._backlog_alert_state_path().read_text(encoding="utf-8"))
        assert state["level"] == "count" and state["last_alert_ts"] > 0

    def test_level_flip_writes_immediately(self, tmp_path, monkeypatch):
        """跨档立即出声：count → count+age（首条变老越龄）→ 冷却窗内也立刻落盘。"""
        ledger = tmp_path / "bottleneck_ledger.jsonl"
        monkeypatch.setattr(cbd, "_LEDGER", ledger)
        self._write_ledger(ledger, 20)  # 档位 "count"
        cbd._check_ledger_backlog()
        assert len(self._alerts(ledger)) == 1
        # 同量但首条 25h → 档位翻转 "count+age"（alert 历史保留，模拟 append-only 账本）
        self._write_ledger(ledger, 20, old_first_hours=25, keep_alerts=True)
        cbd._check_ledger_backlog()
        alerts = self._alerts(ledger)
        assert len(alerts) == 2, alerts
        assert alerts[1]["backlog_level"] == "count+age"

    def test_realert_after_cooldown_expires(self, tmp_path, monkeypatch):
        """冷却期后同档位重报：回拨 last_alert_ts 超窗 → 同档位再落 1 行。"""
        ledger = tmp_path / "bottleneck_ledger.jsonl"
        monkeypatch.setattr(cbd, "_LEDGER", ledger)
        self._write_ledger(ledger, 20)
        cbd._check_ledger_backlog()
        assert len(self._alerts(ledger)) == 1
        # 时光机：把上次告警时间回拨到冷却窗之外
        state_path = cbd._backlog_alert_state_path()
        st = json.loads(state_path.read_text(encoding="utf-8"))
        st["last_alert_ts"] -= cbd._LEDGER_ALERT_COOLDOWN_S + 1
        state_path.write_text(json.dumps(st), encoding="utf-8")
        cbd._check_ledger_backlog()
        alerts = self._alerts(ledger)
        assert len(alerts) == 2, alerts
        assert alerts[1]["backlog_level"] == "count"

    def test_clear_below_threshold_resets_level(self, tmp_path, monkeypatch):
        """回落清零档位：积压消解不写行，但下次再越阈按翻转立即出声。"""
        ledger = tmp_path / "bottleneck_ledger.jsonl"
        monkeypatch.setattr(cbd, "_LEDGER", ledger)
        self._write_ledger(ledger, 20)
        cbd._check_ledger_backlog()
        assert len(self._alerts(ledger)) == 1
        # 维护班清账 → 未越阈：不写行、档位归零（alert 历史保留）
        self._write_ledger(ledger, 3, keep_alerts=True)
        cbd._check_ledger_backlog()
        assert len(self._alerts(ledger)) == 1
        state = json.loads(cbd._backlog_alert_state_path().read_text(encoding="utf-8"))
        assert state["level"] == ""
        # 再次越阈：档位 ""→"count" 翻转 → 冷却窗内也立即落盘
        self._write_ledger(ledger, 21, keep_alerts=True)
        cbd._check_ledger_backlog()
        assert len(self._alerts(ledger)) == 2
