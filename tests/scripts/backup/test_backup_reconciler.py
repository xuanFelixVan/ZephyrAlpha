# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/backup_inventory.md | §
# [TTL] permanent
# tests/scripts/backup/test_backup_reconciler.py
"""backup_reconciler 单元测试。

覆盖：
- INV-08/09/10：post-commit 触发、双条件（重要文件+8h）、状态持久化。
- INV-11：假绿交叉核验闸——ok 落账前须过 system.backup_log 当窗 BACKUP_CREATED。
- INV-12：lock-skip 不推进计时/不降级真实状态；裁决锚定主仓 state（State saved 通道）。
- INV-13（P-7 点火/托管分离）：post-commit 只点火不托管——主动锁自查、脱离启动、
  三条 stdout 语义改由落盘日志解析、裁决延后由 settle_previous_ignition 交叉核验。

P-7 之前 reconcile() 是同步 subprocess.run(timeout=14400) 托管整条流水线（旧实现在
收割器按活 PPID 链级联处决下会连坐杀掉它托管的备份）。本套断言针对新点火模型；
同一组断言打在旧实现上必红（旧 reconcile 无主动锁自查/无 Start-Process 脱离/
无 settle_previous_ignition，且必然 subprocess.run 同步托管）。测试全用 tmp_path +
monkeypatch，禁写 data/ 生产目录、禁真连 CH/PG、禁真点火备份。
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest


@pytest.fixture
def reconciler_module(tmp_path, monkeypatch):
    """导入 backup_reconciler 模块（scripts/backup 入 sys.path）。"""
    backup_dir = Path(__file__).parent.parent.parent.parent / "scripts" / "backup"
    monkeypatch.syspath_prepend(str(backup_dir))
    import backup_reconciler

    return backup_reconciler


def _field(result, name):
    """ReconcileResult 在测试环境可能是 dict（fallback）也可能是真类。"""
    if result is None:
        return None
    return result[name] if isinstance(result, dict) else getattr(result, name)


def _make_ps1(tmp_path):
    ps1 = tmp_path / "scripts" / "backup" / "backup.ps1"
    ps1.parent.mkdir(parents=True, exist_ok=True)
    ps1.write_text("# fake backup.ps1", encoding="utf-8")
    return ps1


def _launch_args(fake_run_call):
    """从被记录的 subprocess.run 调用里取出可断言的命令字符串与 kwargs。"""
    args, kwargs = fake_run_call
    joined = " ".join(str(x) for x in (args[0] if args else []))
    return joined, kwargs


# ── 触发/状态/路径：与 P-7 无关，保持对既有语义的守护 ────────────────────────
class TestTriggerImportantFiles:
    def test_important_prefix_src_triggers(self, reconciler_module, tmp_path):
        committed = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value={}):
                assert reconciler_module.trigger(committed) is True

    def test_non_important_file_does_not_trigger(self, reconciler_module, tmp_path):
        committed = [str(tmp_path / "logs" / "app.log")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            assert reconciler_module.trigger(committed) is False

    def test_aidrafts_does_not_trigger(self, reconciler_module, tmp_path):
        committed = [str(tmp_path / ".aidrafts" / "sess-123" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            assert reconciler_module.trigger(committed) is False


class TestTriggerIntervalProtection:
    def test_recent_backup_blocks_trigger(self, reconciler_module, tmp_path):
        recent = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        committed = [str(tmp_path / "src" / "foo.py")]
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "load_state", return_value={"last_backup_time": recent}),
            patch.object(reconciler_module, "get_state_file", return_value=tmp_path / "backup_state.json"),
        ):
            assert reconciler_module.trigger(committed) is False

    def test_old_backup_allows_trigger(self, reconciler_module, tmp_path):
        old = (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
        committed = [str(tmp_path / "src" / "foo.py")]
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "load_state", return_value={"last_backup_time": old}),
        ):
            assert reconciler_module.trigger(committed) is True

    def test_trigger_cadence_skip_writes_separate_state(self, reconciler_module, tmp_path):
        recent = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        state_file = tmp_path / "backup_state.json"
        committed = [str(tmp_path / "src" / "foo.py")]
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "load_state", return_value={"last_backup_time": recent}),
            patch.object(reconciler_module, "get_state_file", return_value=state_file),
        ):
            assert reconciler_module.trigger(committed) is False
        written = json.loads(state_file.read_text(encoding="utf-8"))
        assert "last_cadence_skip_time" in written
        assert "min_interval" in written["last_cadence_skip_reason"]


class TestStateAndEndpoint:
    def test_update_state_writes_file(self, reconciler_module, tmp_path):
        state_file = tmp_path / "backup_state.json"
        with patch.object(reconciler_module, "get_state_file", return_value=state_file):
            reconciler_module.update_state(last_backup_time="2026-07-09T10:00:00+00:00")
            assert json.loads(state_file.read_text(encoding="utf-8"))["last_backup_time"] == "2026-07-09T10:00:00+00:00"

    def test_get_state_file_reads_from_yaml(self, reconciler_module, tmp_path):
        with (
            patch.object(
                reconciler_module, "load_config", return_value={"trigger": {"state_file": "custom/path/state.json"}}
            ),
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
        ):
            assert reconciler_module.get_state_file() == tmp_path / "custom" / "path" / "state.json"

    def test_endpoint_missing_fail_closed(self, reconciler_module, tmp_path):
        reconciler_module.CH_ENV_FILE = tmp_path / "nonexistent" / ".env.clickhouse"
        r = reconciler_module.query_backup_log_created(datetime.now(timezone.utc))
        assert r["ok"] is False
        assert "fail-closed" in (r.get("error") or "")


# ── INV-13 / 需求(a)(b)：主动锁自查 ──────────────────────────────────────────
class TestLockHolderParsing:
    def test_parse_pid_from_ps1_lock_format(self, reconciler_module, tmp_path):
        lock = tmp_path / "backup.lock"
        lock.write_text("PID:4242 START:2026-09-26T00:00:00.0000000+08:00", encoding="utf-8")
        assert reconciler_module.read_backup_lock_holder_pid(lock) == 4242

    def test_missing_lock_returns_none(self, reconciler_module, tmp_path):
        assert reconciler_module.read_backup_lock_holder_pid(tmp_path / "nope.lock") is None

    def test_corrupt_lock_returns_none(self, reconciler_module, tmp_path):
        lock = tmp_path / "backup.lock"
        lock.write_text("garbage without a pid token", encoding="utf-8")
        assert reconciler_module.read_backup_lock_holder_pid(lock) is None

    def test_json_lock_not_confused_with_ps1_format(self, reconciler_module, tmp_path):
        # backup_runtime_state._read_lock_holder_pid 读的是 JSON；ps1 锁是 PID: 文本。
        # JSON 内容里没有 "PID:" token，主动自查须判为不可辨识 → None（走点火支路）。
        lock = tmp_path / "backup.lock"
        lock.write_text(json.dumps({"pid": 4242, "label": "x"}), encoding="utf-8")
        assert reconciler_module.read_backup_lock_holder_pid(lock) is None


class TestLockPrecheckSkipsWithoutSubprocess:
    """(a) 持锁者存活 → 不启动任何子进程且记 lock_skipped（INV-12 前移）。"""

    def test_live_holder_no_subprocess_and_lock_skipped(self, reconciler_module, tmp_path):
        _make_ps1(tmp_path)
        state_file = tmp_path / "backup_state.json"
        state_file.write_text(
            json.dumps({"last_backup_time": "2026-09-20T00:00:00+00:00", "last_backup_status": "ok"}),
            encoding="utf-8",
        )
        lock = tmp_path / ".runtime" / "backup.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("PID:4242 START:2026-09-26T00:00:00+08:00", encoding="utf-8")
        calls = []

        def _fake_run(*a, **k):
            calls.append((a, k))
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=state_file),
            patch.object(reconciler_module, "_is_pid_alive", lambda pid: True),
            patch.object(reconciler_module.subprocess, "run", _fake_run),
        ):
            result = reconciler_module.reconcile([str(tmp_path / "src" / "x.py")], "sess-a")
        assert calls == [], "持锁者存活时严禁启动子进程"
        assert _field(result, "action") == "warn"
        written = json.loads(state_file.read_text(encoding="utf-8"))
        assert written["last_run_outcome"] == "lock_skipped"
        assert "last_lock_skip_time" in written
        # 不推进 cadence（last_backup_time 不动）
        assert written["last_backup_time"] == "2026-09-20T00:00:00+00:00"
        # 不降级真实状态
        assert written["last_backup_status"] == "ok"

    def test_dead_holder_goes_to_ignite(self, reconciler_module, tmp_path):
        _make_ps1(tmp_path)
        state_file = tmp_path / "backup_state.json"
        lock = tmp_path / ".runtime" / "backup.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("PID:4242 START:2026-09-26T00:00:00+08:00", encoding="utf-8")
        launched = []

        def _fake_run(*a, **k):
            launched.append((a, k))
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=state_file),
            patch.object(reconciler_module, "_is_pid_alive", lambda pid: False),
            patch.object(reconciler_module.subprocess, "run", _fake_run),
        ):
            reconciler_module.reconcile([str(tmp_path / "src" / "x.py")], "sess-b")
        assert len(launched) == 1, "持锁者已死应走点火支路"

    def test_corrupt_lock_goes_to_ignite(self, reconciler_module, tmp_path):
        _make_ps1(tmp_path)
        state_file = tmp_path / "backup_state.json"
        lock = tmp_path / ".runtime" / "backup.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("corrupted contents", encoding="utf-8")
        launched = []
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=state_file),
            patch.object(
                reconciler_module.subprocess,
                "run",
                lambda *a, **k: launched.append(a) or SimpleNamespace(returncode=0, stdout="", stderr=""),
            ),
        ):
            reconciler_module.reconcile([str(tmp_path / "src" / "x.py")], "sess-c")
        assert len(launched) == 1


# ── INV-13 / 需求(c)：脱离启动，绝不同步托管 ────────────────────────────────
class TestDetachedIgnition:
    def test_launch_args_carry_detach_flags(self, reconciler_module, tmp_path):
        ps1 = _make_ps1(tmp_path)
        log = tmp_path / "logs" / "ignite.log"
        captured = []
        with patch.object(
            reconciler_module.subprocess,
            "run",
            lambda *a, **k: captured.append((a, k)) or SimpleNamespace(returncode=0, stdout="", stderr=""),
        ):
            reconciler_module.launch_detached_backup(ps1, log)
        joined, kwargs = _launch_args(captured[0])
        assert "Start-Process" in joined
        assert "-WindowStyle Hidden" in joined
        assert "-RedirectStandardOutput" in joined
        # 只等瞬时装载器（秒级），绝非同步托管流水线（旧值 14400）
        assert kwargs["timeout"] == reconciler_module.IGNITE_SPAWN_TIMEOUT_S
        assert kwargs["timeout"] != 14400

    def test_reconcile_ignites_without_hosting_and_returns_pending(self, reconciler_module, tmp_path):
        _make_ps1(tmp_path)
        state_file = tmp_path / "backup_state.json"
        captured = []
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=state_file),
            patch.object(reconciler_module, "_is_pid_alive", lambda pid: False),
            patch.object(
                reconciler_module.subprocess,
                "run",
                lambda *a, **k: captured.append((a, k)) or SimpleNamespace(returncode=0, stdout="", stderr=""),
            ),
        ):
            result = reconciler_module.reconcile([str(tmp_path / "src" / "x.py")], "sess-d")
        assert len(captured) == 1
        joined, kwargs = _launch_args(captured[0])
        # 点火经 Start-Process 脱离，而非把 backup.ps1 作为 -Command 之外的直接 -File 托管目标
        assert "Start-Process" in joined
        assert kwargs["timeout"] != 14400
        # 点火轮不冒领备份健康：绝返回 auto_committed（避免假绿，INV-11）
        assert _field(result, "action") == "warn"
        written = json.loads(state_file.read_text(encoding="utf-8"))
        assert written["last_run_outcome"] == "ignited_pending_verification"
        assert "last_backup_launch_time" in written
        assert written.get("last_ignite_log", "").endswith(".log")


# ── 需求(d)：三条 stdout 语义改由落盘日志解析 ────────────────────────────────
class TestDetachedLogParsing:
    def test_read_ignition_log_strips_bom(self, reconciler_module, tmp_path):
        log = tmp_path / "ignite.log"
        log.write_bytes("State saved: D:\\ZephyrAlpha\\data\\databases\\backup_state.json".encode("utf-8-sig"))
        text = reconciler_module.read_ignition_log(log)
        assert text[:1] != "﻿"  # utf-8-sig 已去 BOM
        assert "State saved:" in text

    def test_read_missing_log_returns_empty(self, reconciler_module, tmp_path):
        assert reconciler_module.read_ignition_log(tmp_path / "absent.log") == ""

    def test_three_semantics_parsed_from_log(self, reconciler_module, tmp_path):
        report = tmp_path / "logs" / "backup_report_20260926_060000.json"
        report.parent.mkdir(parents=True)
        report.write_text(
            json.dumps({"databases": {"clickhouse": {"status": "ok", "verified": True}}}), encoding="utf-8"
        )
        main_state = tmp_path / "main_state.json"
        log = tmp_path / "ignite.log"
        log.write_text(
            f"[OK] Report saved: {report}\nState saved: {main_state}\n",
            encoding="utf-8-sig",
        )
        text = reconciler_module.read_ignition_log(log)
        # lock-skip 甄别（INV-12）
        assert reconciler_module._LOCK_SKIP_MARKER not in text
        # state 真源锚定通道（P0-1）
        m = reconciler_module._RE_STATE_SAVED.search(text)
        assert m and Path(m.group(1)) == main_state
        # 报告路径通道（read_report_ch_status 从 log 文本取 Report saved: 绝对路径）
        run_start = datetime.fromtimestamp(report.stat().st_mtime, tz=timezone.utc) - timedelta(minutes=5)
        rr = reconciler_module.read_report_ch_status(run_start, text)
        assert rr["found"] is True and rr["ch_status"] == "ok"

    def test_lock_skip_marker_detected_in_log(self, reconciler_module, tmp_path):
        log = tmp_path / "ignite.log"
        log.write_text("[WARN] Another backup is running (holder PID 7 alive). Exiting.", encoding="utf-8-sig")
        assert reconciler_module._LOCK_SKIP_MARKER in reconciler_module.read_ignition_log(log)


# ── INV-11：延后验核（settle_previous_ignition）——假绿闸语义原样保留 ──────────
class TestDeferredVerification:
    def _setup_pending(self, reconciler_module, tmp_path, *, log_body, state):
        """写脱离日志 + 本地 pending state；返回本地 state 文件路径。

        调用方若要 State saved: 锚定主仓 state，须先自行定义 main_state 路径再
        拼进 log_body（主仓 state 文件本身由被测逻辑创建）。
        """
        log = tmp_path / "ignite.log"
        log.write_text(log_body, encoding="utf-8-sig")
        seed = {
            "last_run_outcome": "ignited_pending_verification",
            "last_ignite_log": str(log),
            "last_backup_launch_time": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        }
        seed.update(state)
        sf = tmp_path / "backup_state.json"
        sf.write_text(json.dumps(seed), encoding="utf-8")
        return sf

    def _settle(self, reconciler_module, tmp_path, sf, *, report, probe):
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=sf),
            patch.object(reconciler_module, "read_report_ch_status", return_value=report),
            patch.object(
                reconciler_module,
                "query_backup_log_created",
                side_effect=probe if isinstance(probe, list) else None,
                return_value=None if isinstance(probe, list) else probe,
            ),
        ):
            result = reconciler_module.settle_previous_ignition("sess-verify")
        return result

    def test_verified_ok_passes(self, reconciler_module, tmp_path):
        main_state = tmp_path / "main_state.json"
        sf = self._setup_pending(
            reconciler_module,
            tmp_path,
            log_body=f"State saved: {main_state}\n",
            state={"last_backup_status": "ok"},
        )
        result = self._settle(
            reconciler_module,
            tmp_path,
            sf,
            report={"found": True, "ch_status": "ok", "ch_verified": True, "reason": None, "report": "r.json"},
            probe={"ok": True, "count": 2, "max_event_time": "2026-09-26 01:00:00", "error": None},
        )
        st = json.loads(main_state.read_text(encoding="utf-8"))
        assert _field(result, "action") == "auto_committed"
        assert st["last_backup_status"] == "ok"
        assert st["last_backup_log_verified"] is True
        assert st["last_run_outcome"] == "backed_up"
        assert st["last_ch_backup_status"] == "ok"
        # 结算后清本地 pending 指针，防重复结算
        assert json.loads(sf.read_text(encoding="utf-8")).get("last_ignite_log") is None

    def test_fake_green_blocked_when_log_has_no_row(self, reconciler_module, tmp_path):
        main_state = tmp_path / "main_state.json"
        sf = self._setup_pending(reconciler_module, tmp_path, log_body=f"State saved: {main_state}\n", state={})
        result = self._settle(
            reconciler_module,
            tmp_path,
            sf,
            report={"found": True, "ch_status": "ok", "ch_verified": True, "reason": None, "report": "r.json"},
            probe={"ok": True, "count": 0, "max_event_time": "", "error": None},
        )
        st = json.loads(main_state.read_text(encoding="utf-8"))
        assert _field(result, "action") == "warn"
        assert "FAKE-GREEN" in _field(result, "detail")
        assert st["last_backup_status"] == "ch_log_missing"
        assert st["last_ch_backup_status"] == "ch_log_missing"
        assert st["last_ch_backup_verified"] is False
        assert st["last_run_outcome"] == "fake_green_blocked"

    def test_probe_error_fail_closed(self, reconciler_module, tmp_path):
        main_state = tmp_path / "main_state.json"
        sf = self._setup_pending(reconciler_module, tmp_path, log_body=f"State saved: {main_state}\n", state={})
        self._settle(
            reconciler_module,
            tmp_path,
            sf,
            report={"found": True, "ch_status": "ok", "ch_verified": True, "reason": None, "report": "r.json"},
            probe={"ok": False, "count": 0, "max_event_time": "", "error": "http down"},
        )
        st = json.loads(main_state.read_text(encoding="utf-8"))
        assert st["last_backup_status"] == "ch_log_missing"
        assert st["last_ch_backup_status"] == "ch_log_missing"

    def test_probe_retry_recovers_after_flush_delay(self, reconciler_module, tmp_path):
        main_state = tmp_path / "main_state.json"
        sf = self._setup_pending(reconciler_module, tmp_path, log_body=f"State saved: {main_state}\n", state={})
        self._settle(
            reconciler_module,
            tmp_path,
            sf,
            report={"found": True, "ch_status": "ok", "ch_verified": True, "reason": None, "report": "r.json"},
            probe=[
                {"ok": True, "count": 0, "max_event_time": "", "error": None},
                {"ok": True, "count": 1, "max_event_time": "2026-09-26 06:05:00", "error": None},
            ],
        )
        st = json.loads(main_state.read_text(encoding="utf-8"))
        assert st["last_backup_status"] == "ok"
        assert st["last_backup_log_verified"] is True

    def test_size_sanity_verified_false_demotes(self, reconciler_module, tmp_path):
        main_state = tmp_path / "main_state.json"
        sf = self._setup_pending(reconciler_module, tmp_path, log_body=f"State saved: {main_state}\n", state={})
        result = self._settle(
            reconciler_module,
            tmp_path,
            sf,
            report={"found": True, "ch_status": "ok", "ch_verified": False, "reason": None, "report": "r.json"},
            probe={"ok": True, "count": 3, "max_event_time": "x", "error": None},
        )
        st = json.loads(main_state.read_text(encoding="utf-8"))
        assert st["last_backup_status"] == "ch_log_missing"
        assert "size_sanity_failed" in _field(result, "detail")

    def test_ch_service_down_is_degraded_not_silent(self, reconciler_module, tmp_path):
        main_state = tmp_path / "main_state.json"
        sf = self._setup_pending(reconciler_module, tmp_path, log_body=f"State saved: {main_state}\n", state={})
        result = self._settle(
            reconciler_module,
            tmp_path,
            sf,
            report={
                "found": True,
                "ch_status": "skipped",
                "ch_verified": None,
                "reason": "service down",
                "report": "r.json",
            },
            probe={"ok": True, "count": 0, "max_event_time": "", "error": None},
        )
        st = json.loads(main_state.read_text(encoding="utf-8"))
        assert _field(result, "action") == "auto_committed"
        assert st["last_run_outcome"] == "ok_ch_degraded"
        assert "service down" in st["last_ch_skip_reason"]

    def test_ch_cadence_skip_is_legal_ok(self, reconciler_module, tmp_path):
        main_state = tmp_path / "main_state.json"
        sf = self._setup_pending(reconciler_module, tmp_path, log_body=f"State saved: {main_state}\n", state={})
        self._settle(
            reconciler_module,
            tmp_path,
            sf,
            report={
                "found": True,
                "ch_status": "skipped",
                "ch_verified": None,
                "reason": "24h cadence (last 5.0h ago)",
                "report": "r.json",
            },
            probe={"ok": True, "count": 0, "max_event_time": "", "error": None},
        )
        st = json.loads(main_state.read_text(encoding="utf-8"))
        assert st["last_backup_status"] == "ok"
        assert st["last_run_outcome"] == "ok_ch_skipped"

    def test_ch_failed_report_maps_to_ch_failed(self, reconciler_module, tmp_path):
        main_state = tmp_path / "main_state.json"
        sf = self._setup_pending(reconciler_module, tmp_path, log_body=f"State saved: {main_state}\n", state={})
        result = self._settle(
            reconciler_module,
            tmp_path,
            sf,
            report={"found": True, "ch_status": "failed", "ch_verified": None, "reason": None, "report": "r.json"},
            probe={"ok": True, "count": 5, "max_event_time": "x", "error": None},
        )
        st = json.loads(main_state.read_text(encoding="utf-8"))
        assert _field(result, "action") == "warn"
        assert st["last_backup_status"] == "ch_failed"
        assert st["last_run_outcome"] == "ch_failed"
        assert st["last_backup_log_verified"] is False

    def test_state_saved_anchors_main_state(self, reconciler_module, tmp_path):
        """P0-1：State saved: 主仓路径 → 权威裁决写主仓 state（此处经脱离日志通道，非 stdout）。"""
        main_root = tmp_path / "main_repo"
        (main_root / "data" / "databases").mkdir(parents=True)
        main_state = main_root / "data" / "databases" / "backup_state.json"
        log = tmp_path / "ignite.log"
        log.write_text(f"State saved: {main_state}\n", encoding="utf-8-sig")
        sf = tmp_path / "worktree_state.json"
        sf.write_text(
            json.dumps(
                {
                    "last_run_outcome": "ignited_pending_verification",
                    "last_ignite_log": str(log),
                    "last_backup_launch_time": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                }
            ),
            encoding="utf-8",
        )
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=sf),
            patch.object(
                reconciler_module,
                "read_report_ch_status",
                return_value={
                    "found": True,
                    "ch_status": "ok",
                    "ch_verified": True,
                    "reason": None,
                    "report": "r.json",
                },
            ),
            patch.object(
                reconciler_module,
                "query_backup_log_created",
                return_value={"ok": True, "count": 1, "max_event_time": "x", "error": None},
            ),
        ):
            result = reconciler_module.settle_previous_ignition("sess-anchor")
        assert _field(result, "action") == "auto_committed"
        assert main_state.exists(), "裁决必须写进有消费者的主仓 state"
        st = json.loads(main_state.read_text(encoding="utf-8"))
        assert st["last_backup_status"] == "ok" and st["last_run_outcome"] == "backed_up"
        # worktree 本地 pending 指针被显式清除（跨根不重复结算）
        assert json.loads(sf.read_text(encoding="utf-8")).get("last_ignite_log") is None

    def test_lock_skip_in_log_leaves_cadence_untouched(self, reconciler_module, tmp_path):
        """INV-12：脱离日志显示 ps1 自撞锁短退出 → 只记 lock_skipped，不推进/不降级。"""
        sf = self._setup_pending(
            reconciler_module,
            tmp_path,
            log_body="[WARN] Another backup is running (holder PID 9 alive). Exiting.",
            state={"last_backup_time": "2026-09-24T00:00:00+00:00", "last_backup_status": "ok"},
        )
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=sf),
        ):
            result = reconciler_module.settle_previous_ignition("sess-skip")
        w = json.loads(sf.read_text(encoding="utf-8"))
        assert _field(result, "action") == "warn"
        assert w["last_backup_status"] == "ok"
        assert w["last_backup_time"] == "2026-09-24T00:00:00+00:00"
        assert w["last_run_outcome"] == "lock_skipped"
        assert w.get("last_ignite_log") is None

    def test_incomplete_log_keeps_pending_fail_closed(self, reconciler_module, tmp_path):
        """未到 STAGE 4（在跑/夭折）→ 不记任何 ok，保留 pending 等下轮（fail-closed）。"""
        sf = self._setup_pending(
            reconciler_module,
            tmp_path,
            log_body="[BACKUP] Stage 1: code vault started",
            state={"last_backup_status": "ok"},
        )
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=sf),
        ):
            result = reconciler_module.settle_previous_ignition("sess-running")
        assert result is None
        w = json.loads(sf.read_text(encoding="utf-8"))
        assert w.get("last_ignite_log") == str(tmp_path / "ignite.log")  # pending 保留

    def test_no_pending_is_noop(self, reconciler_module, tmp_path):
        sf = tmp_path / "backup_state.json"
        sf.write_text(json.dumps({"last_backup_status": "ok"}), encoding="utf-8")
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=sf),
        ):
            assert reconciler_module.settle_previous_ignition("sess") is None
