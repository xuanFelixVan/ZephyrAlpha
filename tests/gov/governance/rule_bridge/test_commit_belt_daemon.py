# [TTL] permanent
"""commit_belt_daemon 单测（st-commitspeed-20260916）：单例锁/死信登记/once 模式。

不 spawn 真守护进程（对标 write_audit_daemon 测试先例）；watchdog 主循环
以 max_events 上界最小驱动。
"""

from __future__ import annotations

import json
import threading
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


class TestBookkeepingKindsNotBacklog:
    """W5（st-regfix-laneB-20260922）：三类记账 kind 只留痕不积压。

    registry_drift/landing_staleness/phantom_staging 是流水（只增不减），若计入
    积压计数则记账越勤告警越假——积压 n 收窄为只数 dead_letter。
    """

    def _append(self, ledger, record):
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": "2026-09-22T21:00:00+08:00", **record}, ensure_ascii=False) + "\n")

    def test_bookkeeping_rows_do_not_count_as_backlog(self, tmp_path, monkeypatch):
        ledger = tmp_path / "bottleneck_ledger.jsonl"
        monkeypatch.setattr(cbd, "_LEDGER", ledger)
        # 25 条记账流水（>20 阈）+ 0 条死信 → 不得触发积压告警
        for i in range(10):
            self._append(ledger, {"kind": "registry_drift", "path": f"a{i}.yaml", "added": 1, "removed": 0})
            self._append(ledger, {"kind": "landing_staleness", "qid": f"q-{i}", "age_s": 3600, "threshold_s": 1800})
            self._append(ledger, {"kind": "phantom_staging", "scanned": 5, "phantom": 1})
        cbd._check_ledger_backlog()
        assert "bottleneck_backlog_threshold" not in ledger.read_text(encoding="utf-8")

    def test_dead_letters_still_count_after_narrowing(self, tmp_path, monkeypatch):
        ledger = tmp_path / "bottleneck_ledger.jsonl"
        monkeypatch.setattr(cbd, "_LEDGER", ledger)
        self._append(ledger, {"kind": "registry_drift", "path": "a.yaml", "added": 1, "removed": 0})
        for i in range(20):
            self._append(ledger, {"kind": "dead_letter", "qid": f"q-{i}"})
        cbd._check_ledger_backlog()
        alerts = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if '"alert"' in x]
        assert any(a.get("alert") == "bottleneck_backlog_threshold" for a in alerts)


class TestLedgerRecordKinds:
    """W5 记账 API 三 kind：字段契约 + fail-open。"""

    def test_record_registry_drift(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "led.jsonl")
        cbd.record_registry_drift(
            "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml",
            added=3,
            removed=1,
            session_id="st-regfix-laneA-20260922",
            qid="q-20260922-laneA-0001",
        )
        rec = json.loads((tmp_path / "led.jsonl").read_text(encoding="utf-8").splitlines()[0])
        assert rec["kind"] == "registry_drift" and rec["added"] == 3 and rec["removed"] == 1
        assert rec["session_id"] == "st-regfix-laneA-20260922" and "ts" in rec

    def test_record_landing_staleness(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "led.jsonl")
        cbd.record_landing_staleness("q-20260922-x-0007", age_s=5400.4, session_id="s1", base_head="abc123def456")
        rec = json.loads((tmp_path / "led.jsonl").read_text(encoding="utf-8").splitlines()[0])
        assert rec["kind"] == "landing_staleness" and rec["qid"] == "q-20260922-x-0007"
        assert rec["age_s"] == 5400 and rec["threshold_s"] == round(cbd._STALE_BASE_S)

    def test_record_phantom_staging(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "led.jsonl")
        cbd.record_phantom_staging(scanned=12, phantom=2, session_id="s2")
        rec = json.loads((tmp_path / "led.jsonl").read_text(encoding="utf-8").splitlines()[0])
        assert rec["kind"] == "phantom_staging" and rec["scanned"] == 12 and rec["phantom"] == 2


class TestHeartbeatAndOfflineGap:
    """W5：心跳文件 + THD-ALERT-007 离线缺口告警（结构照抄 005/006 消费先例）。"""

    def test_touch_heartbeat_writes_wall_ts(self, tmp_path):
        qroot = tmp_path / "commit_queue"
        cbd._touch_heartbeat(qroot)
        data = json.loads((qroot / cbd._HEARTBEAT_FILE).read_text(encoding="utf-8"))
        assert data["pid"] > 0 and abs(data["wall_ts"] - __import__("time").time()) < 60

    def test_stale_heartbeat_writes_offline_alert(self, tmp_path, monkeypatch):
        import time as _time

        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "led.jsonl")
        monkeypatch.setattr(cbd, "_load_offline_threshold", lambda: 86400.0)
        qroot = tmp_path / "commit_queue"
        qroot.mkdir(parents=True)
        (qroot / cbd._HEARTBEAT_FILE).write_text(
            json.dumps({"pid": 1, "wall_ts": _time.time() - 25 * 3600}), encoding="utf-8"
        )
        offline_s = cbd._check_daemon_offline_gap(qroot)
        assert offline_s is not None and offline_s > 86400
        rec = json.loads((tmp_path / "led.jsonl").read_text(encoding="utf-8").splitlines()[0])
        assert rec["kind"] == "alert" and rec["alert"] == "belt_daemon_offline_gap"
        assert rec["offline_hours"] > 24

    def test_fresh_or_missing_heartbeat_no_alert(self, tmp_path, monkeypatch):
        import time as _time

        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "led.jsonl")
        monkeypatch.setattr(cbd, "_load_offline_threshold", lambda: 86400.0)
        qroot = tmp_path / "commit_queue"
        qroot.mkdir(parents=True)
        # 无历史心跳：无证据不告警
        assert cbd._check_daemon_offline_gap(qroot) is None
        assert not (tmp_path / "led.jsonl").exists()
        # 新鲜心跳：离线 0
        (qroot / cbd._HEARTBEAT_FILE).write_text(json.dumps({"pid": 1, "wall_ts": _time.time() - 60}), encoding="utf-8")
        assert cbd._check_daemon_offline_gap(qroot) is None

    def test_threshold_unavailable_skips(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "led.jsonl")
        monkeypatch.setattr(cbd, "_load_offline_threshold", lambda: None)
        qroot = tmp_path / "commit_queue"
        qroot.mkdir(parents=True)
        (qroot / cbd._HEARTBEAT_FILE).write_text(json.dumps({"pid": 1, "wall_ts": 0.0}), encoding="utf-8")
        assert cbd._check_daemon_offline_gap(qroot) is None
        assert not (tmp_path / "led.jsonl").exists()

    def test_load_offline_threshold_reads_registry(self, tmp_path, monkeypatch):
        """fail-closed 统读接线：从 REG-ATH-001 读 THD-ALERT-007。"""
        reg = tmp_path / "alert_threshold_registry.yaml"
        reg.write_text(
            "thresholds:\n  - threshold_id: THD-ALERT-007\n    value: 86400\n",
            encoding="utf-8",
        )
        import zephyr.shared.alerts.threshold_loader as tl

        monkeypatch.setattr(tl, "ALERT_THRESHOLD_REGISTRY_PATH", reg)
        assert cbd._load_offline_threshold() == 86400.0


class TestStalePendingScan:
    """W5：pending 陈旧快照扫描（>30min 记账，进程内每 qid 一次）。"""

    @staticmethod
    def _seed(qroot, qid, created_iso, session="sA"):
        (qroot / "pending").mkdir(parents=True, exist_ok=True)
        (qroot / "pending" / f"{qid}.json").write_text(
            json.dumps({"qid": qid, "session_id": session, "created_at": created_iso, "base_head": "abc123def4567890"}),
            encoding="utf-8",
        )

    def test_stale_pending_flagged_once(self, tmp_path, monkeypatch):
        from datetime import datetime, timedelta, timezone

        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "led.jsonl")
        qroot = cbd._queue_root(tmp_path)
        old = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        fresh = datetime.now(timezone.utc).isoformat()
        self._seed(qroot, "q-20260922-a-0001", old)
        self._seed(qroot, "q-20260922-a-0002", fresh)
        alerted: set[str] = set()
        n = cbd._scan_stale_pending(tmp_path, alerted)
        assert n == 1
        rec = json.loads((tmp_path / "led.jsonl").read_text(encoding="utf-8").splitlines()[0])
        assert rec["kind"] == "landing_staleness" and rec["qid"] == "q-20260922-a-0001"
        assert rec["age_s"] > cbd._STALE_BASE_S
        # 幂等：同进程二扫不重复记账
        assert cbd._scan_stale_pending(tmp_path, alerted) == 0

    def test_missing_created_at_falls_back_to_mtime(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "led.jsonl")
        qroot = cbd._queue_root(tmp_path)
        p = qroot / "pending" / "q-20260922-b-0001.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"qid": "q-20260922-b-0001"}), encoding="utf-8")
        import os as _os

        old = __import__("time").time() - 7200
        _os.utime(p, (old, old))
        alerted: set[str] = set()
        assert cbd._scan_stale_pending(tmp_path, alerted) == 1


# ---------------------------------------------------------------------------
# belt daemon drain 链存活闸+瞬态截收（裁定#459 延伸，st-circ-a1-20260930）：
# 生产主通道 bootstrap_drain_with_landing→drain_queue_pool→_pool_process_item 的
# 认领即判活（死会话袋直落 dead/，绝不烧工线程 worktree+门禁段）与泛化异常的
# 瞬态截收（WinError233 管道类 OSError 旧径直落假死信，现按 env 语义退 pending）。
# 直接驱动 _pool_process_item（闸点在 landing 使用之前，哑 landing 即证零工段消耗）。
# ---------------------------------------------------------------------------
class TestPoolDrainSurvivalGate:
    @staticmethod
    def _write_heartbeat(runtime_root: Path, session: str, status: str) -> None:
        hb_dir = runtime_root / "sessions" / session
        hb_dir.mkdir(parents=True, exist_ok=True)
        with open(hb_dir / "heartbeat.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": "2026-09-30T00:00:00+00:00", "pid": 1, "status": status}) + "\n")

    @staticmethod
    def _to_processing(queue_root: Path, item: dict) -> Path:
        (queue_root / "processing").mkdir(parents=True, exist_ok=True)
        src = queue_root / "pending" / f"{item['qid']}.json"
        dst = queue_root / "processing" / f"{item['qid']}.json"
        src.replace(dst)
        return dst

    @staticmethod
    def _strip_custody(processing_path: Path) -> None:
        """剥托管标=历史袋形态（托管正门前入队）：原 ghost 判据逐字可测，不扩面。"""
        bag = json.loads(processing_path.read_text(encoding="utf-8"))
        bag["meta"].pop("custody", None)
        processing_path.write_text(json.dumps(bag, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _pool_stats() -> tuple[dict, dict, threading.Lock]:
        return (
            {
                "done": 0,
                "dead": 0,
                "processed_qids": [],
                "stale_cleared": 0,
                "cascade_marked": 0,
                "successors_rebuilt": 0,
                "landed_index": [],
            },
            {"processed": 0, "env_aborted": False, "budget_left": None},
            threading.Lock(),
        )

    def test_pool_item_of_dead_session_deadletters_as_ghost_never_touches_landing(self, tmp_path) -> None:
        """belt drain 拾取闸：死会话袋认领即判活直落 dead/，landing（工段）零消耗。

        袋取历史形态（_strip_custody 剥托管标）——托管正门后 enqueue 即托管豁免。
        """
        import os

        import scripts.commit_queue as cq
        import scripts.governance.commit_queue_landing as cql

        queue_root = tmp_path / "commit_queue"
        item = cq.enqueue_item(
            "ghost-sess",
            "belt ghost bag",
            [("a.txt", b"v")],
            queue_root=queue_root,
            options=cq.EnqueueOptions(worktree_root=str(tmp_path / "wt")),
        )
        processing_path = self._to_processing(queue_root, item)
        self._strip_custody(processing_path)
        self._write_heartbeat(queue_root.parent, "ghost-sess", "exited")

        class _Sentinel:
            repo_root = tmp_path  # phase 账本 anchor 兜底（fail-open 写 tmp）

            def __call__(self, item: dict, root: Path):
                raise AssertionError("幽灵闸必须在此之前出局——死会话袋不得烧工段")

        stats, shared, lock = self._pool_stats()
        cql._pool_process_item(_Sentinel(), queue_root, processing_path, stats, lock, shared)
        assert stats["dead"] == 1
        assert shared["processed"] == 1
        payload = json.loads((queue_root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert payload["meta"]["ghost"] is True
        assert payload["dead_reason"].startswith("ghost_session:")
        assert cq.classify_dead_reason(payload["dead_reason"]) == "env", "可 requeue（处方向 env）"
        assert payload.get("prescription"), "pool 死信出口处方在场"

    def test_pool_transient_escape_requeues_not_dead(self, tmp_path) -> None:
        """pool 泛化异常截收：WinError233 管道类 OSError 按 env 语义退 pending，绝不死信。"""
        import os

        import scripts.commit_queue as cq
        import scripts.governance.commit_queue_landing as cql

        queue_root = tmp_path / "commit_queue"
        item = cq.enqueue_item(
            "live-sess",
            "pipe broken bag",
            [("a.txt", b"v")],
            queue_root=queue_root,
            options=cq.EnqueueOptions(worktree_root=str(tmp_path / "wt")),
        )
        processing_path = self._to_processing(queue_root, item)

        class _BrokenLanding:
            repo_root = tmp_path

            @staticmethod
            def _item_paths(item: dict) -> list[str]:
                return []

            def __call__(self, item: dict, root: Path):
                raise OSError(233, "管道的另一端上无任何进程。")

        stats, shared, lock = self._pool_stats()
        cql._pool_process_item(_BrokenLanding(), queue_root, processing_path, stats, lock, shared)
        assert stats["dead"] == 0, "管道瞬断绝不死信"
        assert shared["env_aborted"] is True, "共享终止旗置位（本波收工，同 drain 语义）"
        assert (queue_root / "pending" / f"{item['qid']}.json").is_file(), "项退回 pending 等下次自举"
        payload = json.loads((queue_root / "pending" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert int((payload.get("meta") or {}).get("env_retry") or 0) == 1, "env_retry 计数闸进账（≤3 防活锁）"

    def test_pool_item_of_alive_session_still_processed(self, tmp_path) -> None:
        """对照：活会话袋不被闸误伤（heartbeat alive → 闸 fail-open 放行进 landing）。"""
        import os

        import scripts.commit_queue as cq
        import scripts.governance.commit_queue_landing as cql

        queue_root = tmp_path / "commit_queue"
        item = cq.enqueue_item(
            "live-sess",
            "alive bag",
            [("a.txt", b"v")],
            queue_root=queue_root,
            options=cq.EnqueueOptions(worktree_root=str(tmp_path / "wt")),
        )
        self._to_processing(queue_root, item)
        self._write_heartbeat(queue_root.parent, "live-sess", "alive")

        class _LiveLanding:
            repo_root = tmp_path
            touched = False

            @staticmethod
            def _item_paths(item: dict) -> list[str]:
                return []

            def __call__(self, item: dict, root: Path):
                self.touched = True
                from scripts.commit_queue import LandingResult

                return LandingResult(ok=True, landed_id="stub0" * 6)

        stats, shared, lock = self._pool_stats()
        live = _LiveLanding()
        cql._pool_process_item(live, queue_root, queue_root / "processing" / f"{item['qid']}.json", stats, lock, shared)
        assert live.touched is True, "活会话袋必须照常进 landing"
        assert stats["dead"] == 0


class TestT14LedgerSizeGate:
    """T14（2026-10-11）：堵点本裸 append 写侧必须过 audit_jsonl_writer 的体积闸。

    实测病根：.runtime/audit/bottleneck_ledger.jsonl = 118,806,146 B（阈值 52,428,800
    的 2.27 倍），盘上零轮转段＝写侧从来没问过那把 50MB 尺。
    """

    def test_ledger_record_rotates_oversized_segment(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """红证（修前必红：_ledger_record 内无闸）：超限先移位轮转再追加。"""
        import functools

        import zephyr.shared.io.audit_jsonl_writer as w

        ledger = tmp_path / "bottleneck_ledger.jsonl"
        monkeypatch.setattr(cbd, "_LEDGER", ledger)
        monkeypatch.setattr(w, "rotate_if_oversized", functools.partial(w.rotate_if_oversized, max_bytes=1024))
        ledger.write_text("x" * 2048 + "\n", encoding="utf-8")

        cbd._ledger_record({"kind": "probe", "qid": "q-t14"})

        assert (tmp_path / "bottleneck_ledger.jsonl.1").exists(), "超限堵点本未移位轮转"
        rows = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(rows) == 1 and rows[0]["kind"] == "probe" and rows[0]["qid"] == "q-t14", "轮转后新行应落当前段"
        assert rows[0]["ts"], "_ledger_record 的 ts 前缀语义不许坏"
        assert "x" * 64 in (tmp_path / "bottleneck_ledger.jsonl.1").read_text(encoding="utf-8"), "历史段不得被删"

    def test_ledger_record_under_threshold_not_rotated(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """反向腿：未超限照旧纯追加（防"每次打开都搬文件"）。"""
        import functools

        import zephyr.shared.io.audit_jsonl_writer as w

        ledger = tmp_path / "bottleneck_ledger.jsonl"
        monkeypatch.setattr(cbd, "_LEDGER", ledger)
        monkeypatch.setattr(w, "rotate_if_oversized", functools.partial(w.rotate_if_oversized, max_bytes=1024))
        ledger.write_text('{"kind":"old"}\n', encoding="utf-8")

        cbd._ledger_record({"kind": "new"})

        assert not (tmp_path / "bottleneck_ledger.jsonl.1").exists()
        assert [r["kind"] for r in (json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines())] == [
            "old",
            "new",
        ]

    def test_every_bare_ledger_append_is_gated(self) -> None:
        """结构锁：本模块每一处 `_LEDGER.open("a"` 前必须紧邻一次 rotate_if_oversized。

        防的是"以后又添一处裸 append"——行为用例只覆盖被走到的分支，本例逐处扫。
        """
        import re
        from pathlib import Path as _P

        src = (_P(cbd.__file__)).read_text(encoding="utf-8").splitlines()
        opens = [i for i, ln in enumerate(src) if '_LEDGER.open("a"' in ln]
        assert opens, "本例前提（存在堵点本 append）已失效——写侧被整体重写，请同步复核"
        for i in opens:
            window = "\n".join(src[max(0, i - 5) : i + 1])
            assert re.search(r"rotate_if_oversized\(", window), f"第 {i + 1} 行 append 前无体积闸：{window[-160:]}"


# ── #ARCH-084 追加刀：投影自愈写口署名（2026-10-12 维护三班夜班，Owner 通宵令"写者必须署名"）──
# 病根读数：safe_write 审计的 session 字段取 env ZEPHYR_SESSION_ID（file_utils.py:575），
# daemon 从不设 ⇒ 热册每轮自愈重写记成空串（实测 03:23-03:31 每 ~50s 一次、pid 互异）。


def test_projection_render_write_is_attributed_and_env_restored(monkeypatch) -> None:
    """红证臂：写口内看得见署名；出口 env 必须复原（别的门也消费这个 env）。"""
    import os

    seen: dict[str, object] = {}

    def _fake_run(root, mode=None, registry_id=None, physical_path=None, actor_session=None):
        seen["env"] = os.environ.get("ZEPHYR_SESSION_ID")
        seen["kw"] = (mode, registry_id, physical_path, actor_session)
        return "REPORT"

    monkeypatch.delenv("ZEPHYR_SESSION_ID", raising=False)
    out = cbd._render_projection_with_attribution(_fake_run, Path("."), "REG-X", "p.yaml")
    assert out == "REPORT"
    assert seen["env"] == cbd._PROJECTION_WRITE_ACTOR, "写口未署名＝审计面永远空串（本刀白装）"
    assert seen["kw"] == ("render", "REG-X", "p.yaml", "belt_daemon"), "换壳不得改渲染语义与既有 actor_session"
    assert "ZEPHYR_SESSION_ID" not in os.environ, "用完没复原＝给后续无关写者挂名"


def test_projection_render_attribution_preserves_outer_sid(monkeypatch) -> None:
    """不误伤臂：外层已设 sid（车道内跑 daemon 探针）⇒ 复原成原值而不是删掉。"""
    import os

    monkeypatch.setenv("ZEPHYR_SESSION_ID", "outer-sid")
    cbd._render_projection_with_attribution(lambda *a, **k: None, Path("."), "R", "p")
    assert os.environ.get("ZEPHYR_SESSION_ID") == "outer-sid"


def test_projection_render_attribution_restores_on_exception(monkeypatch) -> None:
    """异常臂：render 抛错也必须复原 env——否则一次 PG 抖动就把 daemon 变成"署名写者"混入后续流程。"""
    import os

    monkeypatch.delenv("ZEPHYR_SESSION_ID", raising=False)

    def _boom(*a, **k):
        raise RuntimeError("PG 断了")

    with pytest.raises(RuntimeError):
        cbd._render_projection_with_attribution(_boom, Path("."), "R", "p")
    assert "ZEPHYR_SESSION_ID" not in os.environ


# ---------------------------------------------------------------------------
# 段二常态化两条腿（Owner 2026-10-13 死信放量班追加令；99_delivery §四-4 交接面）
#   腿①＝当日四态分诊的自动触发（事件驱动，禁 cron）——只判不删；
#   腿②＝主区暂存区无主 staged 巡检——TierA 存证后复位 index，TierB 歧义面只记不修。
# 判据本身（内容级四态门）已由 tests/gov/governance/test_commit_queue.py 的
# TestDeadArchiveContentGate 钉扎，本批只测"接线面"：触发/幂等/只判不删/谓词分档/停腿。
# ---------------------------------------------------------------------------


@pytest.fixture()
def triage_repo(tmp_path, monkeypatch):
    """临时仓 + dead/ 两封袋 + 假门（判据注入，本批不测判据）。"""
    monkeypatch.setattr(cbd, "_DEAD_TRIAGE_LEDGER", tmp_path / "triage_ledger.jsonl")
    monkeypatch.setattr(cbd, "_dev_head_sha", lambda root: "sha-v1")
    qroot = cbd._queue_root(tmp_path)
    (qroot / "dead").mkdir(parents=True)
    for qid, verdict in (("q-20261013-sA-0001", "A_LANDED"), ("q-20261013-sB-0002", "C_UNIQUE_WOULD_REGRESS")):
        (qroot / "dead" / f"{qid}.json").write_text(
            json.dumps({"qid": qid, "session_id": qid.split("-")[2], "dead_at": "2026-10-13T10:00:00+08:00"}),
            encoding="utf-8",
        )
        # 每封一条判定：A 放行、C 不放行

    def _fake_gate(item):
        v = "A_LANDED" if item["qid"].endswith("0001") else "C_UNIQUE_WOULD_REGRESS"
        return (v == "A_LANDED"), {"verdict": v, "n_items": 1, "n_unique": 0 if v == "A_LANDED" else 1}

    monkeypatch.setattr(cbd, "_triage_state", {"dev_sha": "sha-v1", "gate": _fake_gate})
    return tmp_path


class TestDeadTriageProbe:
    def test_writes_one_verdict_row_per_unjudged_bag(self, triage_repo) -> None:
        out = cbd.dead_triage_probe(triage_repo, now="2026-10-13T21:00:00+08:00", force=True)
        assert out["scanned"] == 2 and out["triaged"] == 2
        rows = [json.loads(l) for l in (triage_repo / "triage_ledger.jsonl").read_text(encoding="utf-8").splitlines()]
        assert {r["verdict"] for r in rows} == {"A_LANDED", "C_UNIQUE_WOULD_REGRESS"}
        assert rows[0]["kind"] == "dead_letter_triage" and rows[0]["triage_day"] == "2026-10-13"
        assert [r["allow_archive_by_gate"] for r in rows] == [True, False]

    def test_idempotent_same_day_and_other_day_rejudges(self, triage_repo) -> None:
        cbd.dead_triage_probe(triage_repo, now="2026-10-13T21:00:00+08:00", force=True)
        again = cbd.dead_triage_probe(triage_repo, now="2026-10-13T21:05:00+08:00", force=True)
        assert again["scanned"] == 0 and again["triaged"] == 0, "当日已判过的袋不得重复落行（禁积压翻倍）"
        nxt = cbd.dead_triage_probe(triage_repo, now="2026-10-14T00:30:00+08:00", force=True)
        assert nxt["triaged"] == 2, "跨日须重新分诊（当日不隔夜＝按日账）"

    def test_probe_never_moves_bags_or_creates_archive(self, triage_repo) -> None:
        """只判不删：跑完 dead/ 两封仍在原位，且不得出现任何归档目录。"""
        cbd.dead_triage_probe(triage_repo, now="2026-10-13T21:00:00+08:00", force=True)
        qroot = cbd._queue_root(triage_repo)
        assert len(list((qroot / "dead").glob("q-*.json"))) == 2
        assert not list(triage_repo.rglob("dead_archive_*")), "分诊腿自动清袋＝把'存疑回态④'变成'自动硬清'"

    def test_cooldown_requires_event_not_timer(self, triage_repo) -> None:
        cbd.dead_triage_probe(triage_repo, now="2026-10-13T21:00:00+08:00")  # 非 force：本轮建账
        skip = cbd.dead_triage_probe(triage_repo, now="2026-10-13T21:00:30+08:00")
        assert skip["skipped_cooldown"] is True and skip["triaged"] == 0

    def test_gate_error_records_row_and_does_not_raise(self, triage_repo, monkeypatch) -> None:
        def _boom(item):
            raise RuntimeError("rev-list 炸了")

        monkeypatch.setattr(cbd, "_triage_state", {"dev_sha": "sha-v1", "gate": _boom})
        out = cbd.dead_triage_probe(triage_repo, now="2026-10-13T21:00:00+08:00", force=True)
        assert out["verdicts"] == {"GATE_ERROR": 2}
        rows = [json.loads(l) for l in (triage_repo / "triage_ledger.jsonl").read_text(encoding="utf-8").splitlines()]
        assert "rev-list 炸了" in rows[0]["gate_error"]

    def test_index_rebuilt_when_dev_head_moves(self, triage_repo, monkeypatch) -> None:
        seen: list = []

        def _gate(item):
            seen.append(item["qid"])
            return True, {"verdict": "A_LANDED"}

        import scripts.commit_queue as cq

        monkeypatch.setattr(cq, "make_dead_letter_content_gate", lambda *a, **k: _gate)
        monkeypatch.setattr(cbd, "_triage_state", {"dev_sha": "sha-v1", "gate": _gate})
        cbd.dead_triage_probe(triage_repo, now="2026-10-13T21:00:00+08:00", force=True)
        assert len(seen) == 2
        monkeypatch.setattr(cbd, "_dev_head_sha", lambda root: "sha-v2")  # dev 前进＝旧索引作废
        (cbd._queue_root(triage_repo) / "dead" / "q-20261013-sC-0003.json").write_text(
            json.dumps({"qid": "q-20261013-sC-0003", "session_id": "sC", "dead_at": "2026-10-13T22:00:00+08:00"}),
            encoding="utf-8",
        )
        out = cbd.dead_triage_probe(triage_repo, now="2026-10-13T21:30:00+08:00", force=True)
        assert out["triaged"] == 1 and cbd._triage_state["dev_sha"] == "sha-v2"


# ── 腿②：主区暂存区无主 staged 巡检 ──────────────────────────────────────


def _git(repo: Path, *a: str) -> str:
    import subprocess

    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, encoding="utf-8", check=True)
    return r.stdout.strip()


@pytest.fixture()
def staging_repo(tmp_path, monkeypatch):
    """临时仓：a.md=纯索引幽灵(TierA)、b.md=盘也改(TierB)、c.md=有主跳过。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "dev")
    _git(repo, "config", "user.email", "t@l")
    _git(repo, "config", "user.name", "t")
    for n in ("a.md", "b.md", "c.md"):
        (repo / n).write_text(f"{n} head\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "init")

    # TierA：index 留旧快照，工作区随后回到 HEAD（磁盘即真源）
    (repo / "a.md").write_text("stale index snapshot\n", encoding="utf-8")
    _git(repo, "add", "a.md")
    (repo / "a.md").write_text("a.md head\n", encoding="utf-8")
    # TierB：index 与工作区都改（歧义面）
    (repo / "b.md").write_text("both sides changed\n", encoding="utf-8")
    _git(repo, "add", "b.md")
    (repo / "b.md").write_text("worktree further edited\n", encoding="utf-8")
    # 有主：c.md 同 TierA 形态，但被"活跃会话 claim"
    (repo / "c.md").write_text("stale snapshot claimed\n", encoding="utf-8")
    _git(repo, "add", "c.md")
    (repo / "c.md").write_text("c.md head\n", encoding="utf-8")

    class _Sess:
        held_files = ["c.md"]

    class _Reg:
        def __init__(self, *a, **k):
            pass

        def list_active_readonly(self):
            return [_Sess()]

    import zephyr.security.access_control.session_concurrency as sc

    monkeypatch.setattr(sc, "SessionRegistry", _Reg)
    monkeypatch.setattr(cbd, "_LEDGER", tmp_path / "bottleneck_ledger.jsonl")
    monkeypatch.setattr(cbd, "_PHANTOM_STAGING_EVIDENCE", Path(".runtime/quarantine/phantom_staging"))
    return repo


class TestPhantomStagingProbe:
    def test_tier_a_reset_to_head_with_evidence(self, staging_repo) -> None:
        out = cbd.phantom_staging_probe(staging_repo, force=True)
        assert out["tier_a"] == 1 and out["reset"] == 1
        assert "a.md" not in _git(staging_repo, "diff", "--cached", "--name-only").splitlines(), (
            "index 仍压旧快照＝没复位"
        )
        assert (staging_repo / "a.md").read_text(encoding="utf-8") == "a.md head\n", "工作区字节一个都不许动"
        man = list((staging_repo / ".runtime/quarantine/phantom_staging").rglob("MANIFEST.jsonl"))
        assert man, "复位必须留证"
        row = json.loads(man[0].read_text(encoding="utf-8").splitlines()[0])
        assert row["path"] == "a.md" and row["action"] == "reset_index_to_head"
        assert (man[0].parent / row["evidence"]).exists(), "存证字节必须可回放"

    def test_tier_b_ambiguous_left_untouched(self, staging_repo) -> None:
        out = cbd.phantom_staging_probe(staging_repo, force=True)
        assert out["tier_b"] == 1
        staged = _git(staging_repo, "diff", "--cached", "--name-only").splitlines()
        assert "b.md" in staged, "歧义面被自动复位＝可能洗掉他班在途编辑"
        assert (staging_repo / "b.md").read_text(encoding="utf-8") == "worktree further edited\n"

    def test_owned_paths_skipped_via_readonly_ruler(self, staging_repo) -> None:
        out = cbd.phantom_staging_probe(staging_repo, force=True)
        assert out["owned"] == 1
        assert "c.md" in _git(staging_repo, "diff", "--cached", "--name-only").splitlines()

    def test_kill_switch_disables_mutation_only(self, staging_repo) -> None:
        (staging_repo / ".runtime/registry_ledger").mkdir(parents=True)
        (staging_repo / ".runtime/registry_ledger/phantom_staging.disabled").write_text("1\n", encoding="utf-8")
        out = cbd.phantom_staging_probe(staging_repo, force=True)
        assert out.get("disabled") is True and out["reset"] == 0
        assert "a.md" in _git(staging_repo, "diff", "--cached", "--name-only").splitlines()

    def test_execute_false_is_pure_noop(self, staging_repo) -> None:
        out = cbd.phantom_staging_probe(staging_repo, execute=False, force=True)
        assert out == {"scanned": 0, "tier_a": 0, "tier_b": 0, "owned": 0, "reset": 0, "evidence_dir": ""}

    def test_ledger_row_written_for_each_round(self, staging_repo) -> None:
        cbd.phantom_staging_probe(staging_repo, force=True)
        led = Path(cbd._LEDGER)
        rows = [json.loads(l) for l in led.read_text(encoding="utf-8").splitlines()]
        ps = [r for r in rows if r["kind"] == "phantom_staging"]
        assert len(ps) == 1 and ps[0]["scanned"] == 3 and ps[0]["phantom"] == 1
        assert "TierB" in ps[0]["detail"] and ps[0]["session_id"] == "belt_daemon:phantom_staging_probe"

    def test_missing_evidence_write_blocks_reset(self, staging_repo, monkeypatch) -> None:
        """fail-closed：取不到存证字节就不复位（防"无证的不可逆动作"）。

        写侧现走 process_pool 统一入口（BARE-SUBPROCESS 铁律），所以探针打在同一个口上。
        """
        import zephyr.shared.infra.process_pool as pp

        real = pp.run_subprocess_hidden

        def _only_cat_file_fails(cmd, *a, **k):
            if "cat-file" in cmd:
                raise RuntimeError("存不了证")
            return real(cmd, *a, **k)

        monkeypatch.setattr(pp, "run_subprocess_hidden", _only_cat_file_fails)
        out = cbd.phantom_staging_probe(staging_repo, force=True)
        assert out["reset"] == 0, "没留证就复位＝制造查无此事的不可逆动作"
        assert "a.md" in _git(staging_repo, "diff", "--cached", "--name-only").splitlines()
