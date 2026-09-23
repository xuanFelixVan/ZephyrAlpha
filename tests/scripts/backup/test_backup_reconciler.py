# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/backup_inventory.md | §
# [TTL] permanent
# tests/scripts/backup/test_backup_reconciler.py
"""backup_reconciler单元测试——验证触发条件与间隔保护逻辑。

测试覆盖蓝图INV-08/INV-09/INV-10：
- INV-08: post-commit reconciler触发，非时间触发
- INV-09: 双条件触发（重要文件变更 + 8h间隔）
- INV-10: 状态持久化到backup_state.json
"""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_state_file(tmp_path):
    """临时状态文件fixture"""
    state_file = tmp_path / "backup_state.json"
    return state_file


@pytest.fixture
def reconciler_module(tmp_path, monkeypatch):
    """导入backup_reconciler模块，patch项目根路径"""
    import sys

    # 将scripts/backup加入sys.path
    backup_dir = Path(__file__).parent.parent.parent.parent / "scripts" / "backup"
    monkeypatch.syspath_prepend(str(backup_dir))
    import backup_reconciler

    return backup_reconciler


class TestTriggerImportantFiles:
    """测试trigger的重要文件检测逻辑"""

    def test_important_prefix_src_triggers(self, reconciler_module, tmp_path):
        """src/下文件变更应触发"""
        committed = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value={}):
                assert reconciler_module.trigger(committed) is True

    def test_important_prefix_config_triggers(self, reconciler_module, tmp_path):
        """config/下文件变更应触发"""
        committed = [str(tmp_path / "config" / "sla_targets.yaml")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value={}):
                assert reconciler_module.trigger(committed) is True

    def test_important_file_AGENTS_md_triggers(self, reconciler_module, tmp_path):
        """AGENTS.md变更应触发"""
        committed = [str(tmp_path / "AGENTS.md")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value={}):
                assert reconciler_module.trigger(committed) is True

    def test_non_important_file_does_not_trigger(self, reconciler_module, tmp_path):
        """logs/下文件变更不应触发"""
        committed = [str(tmp_path / "logs" / "app.log")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            assert reconciler_module.trigger(committed) is False

    def test_aidrafts_does_not_trigger(self, reconciler_module, tmp_path):
        """.aidrafts/下文件变更不应触发（临时草稿）"""
        committed = [str(tmp_path / ".aidrafts" / "sess-123" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            assert reconciler_module.trigger(committed) is False


class TestTriggerIntervalProtection:
    """测试trigger的8小时间隔保护逻辑"""

    def test_recent_backup_blocks_trigger(self, reconciler_module, tmp_path):
        """距上次备份<8h应阻断触发"""
        recent_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        state = {"last_backup_time": recent_time}
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value=state):
                # cadence-skip 会写 last_cadence_skip_*，隔离到 tmp 防止写生产状态
                with patch.object(
                    reconciler_module,
                    "get_state_file",
                    return_value=tmp_path / "backup_state.json",
                ):
                    assert reconciler_module.trigger(committed) is False

    def test_old_backup_allows_trigger(self, reconciler_module, tmp_path):
        """距上次备份≥8h应允许触发"""
        old_time = (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
        state = {"last_backup_time": old_time}
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value=state):
                assert reconciler_module.trigger(committed) is True

    def test_no_state_allows_trigger(self, reconciler_module, tmp_path):
        """无状态文件（首次备份）应允许触发"""
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value={}):
                assert reconciler_module.trigger(committed) is True


class TestTriggerYamlWiring:
    """测试 trigger() 从 YAML 读取触发参数（F-06 Track A 治本）

    验证 trigger 调用 load_config() 读取 trigger.important_prefixes /
    trigger.important_files / trigger.min_interval_seconds，而非硬编码常量。
    """

    def test_trigger_reads_custom_prefixes_from_yaml(self, reconciler_module, tmp_path):
        """trigger 应从 YAML 读取自定义 important_prefixes"""
        # YAML 配置自定义前缀（不含 src/，含 custom/）
        fake_config = {"trigger": {"important_prefixes": ["custom/"], "important_files": []}}
        committed_custom = [str(tmp_path / "custom" / "foo.py")]
        committed_src = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "load_config", return_value=fake_config):
            with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
                with patch.object(reconciler_module, "load_state", return_value={}):
                    # custom/ 在 YAML 中 -> 触发
                    assert reconciler_module.trigger(committed_custom) is True
                    # src/ 不在 YAML 中 -> 不触发
                    assert reconciler_module.trigger(committed_src) is False

    def test_trigger_reads_custom_min_interval_from_yaml(self, reconciler_module, tmp_path):
        """trigger 应从 YAML 读取自定义 min_interval_seconds"""
        # YAML 配置 1 秒间隔（远小于默认 8 小时）
        fake_config = {"trigger": {"min_interval_seconds": 1}}
        recent_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        state = {"last_backup_time": recent_time}
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "load_config", return_value=fake_config):
            with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
                with patch.object(reconciler_module, "load_state", return_value=state):
                    # 2 小前备份，但 YAML 设 1 秒间隔 -> 允许触发
                    assert reconciler_module.trigger(committed) is True

    def test_trigger_falls_back_to_defaults_when_yaml_empty(self, reconciler_module, tmp_path):
        """YAML 为空时 fallback 到硬编码常量"""
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "load_config", return_value={}):
            with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
                with patch.object(reconciler_module, "load_state", return_value={}):
                    # 硬编码 IMPORTANT_PREFIXES 含 src/ -> 触发
                    assert reconciler_module.trigger(committed) is True


class TestStatePersistence:
    """测试状态文件持久化（INV-10）

    F-06 Track A（2026-07-17）：load_state/update_state 通过 get_state_file() 读取
    backup_config.yaml §trigger.state_file，fallback 到 STATE_FILE。测试 patch
    get_state_file 以隔离 YAML 依赖。
    """

    def test_load_state_returns_empty_when_no_file(self, reconciler_module, tmp_path):
        """状态文件不存在时返回空dict"""
        with patch.object(reconciler_module, "get_state_file", return_value=tmp_path / "nonexistent.json"):
            assert reconciler_module.load_state() == {}

    def test_load_state_returns_dict_when_file_exists(self, reconciler_module, tmp_path):
        """状态文件存在时返回解析后的dict"""
        state_file = tmp_path / "backup_state.json"
        state_file.write_text(json.dumps({"last_backup_time": "2026-07-09T10:00:00+00:00"}), encoding="utf-8")
        with patch.object(reconciler_module, "get_state_file", return_value=state_file):
            state = reconciler_module.load_state()
            assert state["last_backup_time"] == "2026-07-09T10:00:00+00:00"

    def test_update_state_writes_file(self, reconciler_module, tmp_path):
        """update_state应写入状态文件"""
        state_file = tmp_path / "backup_state.json"
        with patch.object(reconciler_module, "get_state_file", return_value=state_file):
            reconciler_module.update_state(last_backup_time="2026-07-09T10:00:00+00:00")
            state = json.loads(state_file.read_text(encoding="utf-8"))
            assert state["last_backup_time"] == "2026-07-09T10:00:00+00:00"


class TestGetStateFileYamlWiring:
    """测试 get_state_file() 从 YAML 读取 state_file（F-06 Track A 治本）"""

    def test_get_state_file_reads_from_yaml(self, reconciler_module, tmp_path):
        """get_state_file 应从 YAML trigger.state_file 读取路径"""
        fake_config = {"trigger": {"state_file": "custom/path/state.json"}}
        with patch.object(reconciler_module, "load_config", return_value=fake_config):
            with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
                result = reconciler_module.get_state_file()
                assert result == tmp_path / "custom" / "path" / "state.json"

    def test_get_state_file_falls_back_to_constant(self, reconciler_module, tmp_path):
        """YAML 缺失 state_file 时 fallback 到 STATE_FILE"""
        with patch.object(reconciler_module, "load_config", return_value={}):
            with patch.object(reconciler_module, "STATE_FILE", tmp_path / "fallback.json"):
                result = reconciler_module.get_state_file()
                assert result == tmp_path / "fallback.json"

    def test_get_state_file_falls_back_when_config_none(self, reconciler_module, tmp_path):
        """load_config 返回 None 时 fallback 到 STATE_FILE"""
        with patch.object(reconciler_module, "load_config", return_value=None):
            with patch.object(reconciler_module, "STATE_FILE", tmp_path / "fallback.json"):
                result = reconciler_module.get_state_file()
                assert result == tmp_path / "fallback.json"


def _field(result, name):
    """ReconcileResult 在测试环境可能是 dict（fallback）也可能是真类。"""
    return result[name] if isinstance(result, dict) else getattr(result, name)


class TestBackupLogGate:
    """INV-11 假绿交叉核验闸（2026-09-24 处方）

    2026-09-22 实证：backup.ps1 CH 段轮询 system.backups（内存态）自报 ok
    （state 记 verified=true），而持久真源 system.backup_log 当日零行。
    处方：exit=0 的 ok 落账前必须过 backup_log 当窗 BACKUP_CREATED 交叉核验；
    核验不过降级 ch_log_missing 并连带摘除 last_ch_backup_status 的 ok
    （下游 db_dumps 轮转闸消费该字段，宁停转勿假绿）；cadence-skip 单独记账。
    """

    def _run(self, reconciler_module, tmp_path, *, returncode=0, report, probe, stdout="backup done"):
        from types import SimpleNamespace

        ps1 = tmp_path / "scripts" / "backup" / "backup.ps1"
        ps1.parent.mkdir(parents=True, exist_ok=True)
        ps1.write_text("# fake backup.ps1", encoding="utf-8")
        probe_mock = (
            patch.object(reconciler_module, "query_backup_log_created", side_effect=probe)
            if isinstance(probe, list)
            else patch.object(reconciler_module, "query_backup_log_created", return_value=probe)
        )
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=tmp_path / "backup_state.json"),
            patch.object(
                reconciler_module.subprocess,
                "run",
                return_value=SimpleNamespace(returncode=returncode, stdout=stdout, stderr=""),
            ),
            patch.object(reconciler_module, "read_report_ch_status", return_value=report),
            probe_mock,
        ):
            result = reconciler_module.reconcile([str(tmp_path / "src" / "x.py")], "sess-test")
        state = json.loads((tmp_path / "backup_state.json").read_text(encoding="utf-8"))
        return result, state

    def test_verified_ok_passes(self, reconciler_module, tmp_path):
        """backup_log 当窗有 BACKUP_CREATED 行 -> ok 照常落账，闸显式复权 CH 状态（P2-13）"""
        result, state = self._run(
            reconciler_module,
            tmp_path,
            report={"found": True, "ch_status": "ok", "ch_verified": True, "reason": None, "report": "r.json"},
            probe={"ok": True, "count": 2, "max_event_time": "2026-09-24 01:00:00", "error": None},
        )
        assert _field(result, "action") == "auto_committed"
        assert state["last_backup_status"] == "ok"
        assert state["last_backup_log_verified"] is True
        assert state["last_backup_log_count"] == 2
        assert state["last_run_outcome"] == "backed_up"
        assert state["last_ch_backup_status"] == "ok"
        assert state["last_ch_backup_verified"] is True

    def test_fake_green_blocked_when_log_has_no_row(self, reconciler_module, tmp_path):
        """红测：伪造无 log 的 ok 必须被拦——不记 ok、降级 ch_log_missing、摘 CH ok"""
        result, state = self._run(
            reconciler_module,
            tmp_path,
            report={"found": True, "ch_status": "ok", "ch_verified": True, "reason": None, "report": "r.json"},
            probe={"ok": True, "count": 0, "max_event_time": "", "error": None},
        )
        assert _field(result, "action") == "warn"
        assert "FAKE-GREEN" in _field(result, "detail")
        assert state["last_backup_status"] == "ch_log_missing"
        # 连带摘除 CH ok 字段：下游 db_dumps 轮转闸只认 last_ch_backup_status=="ok"
        assert state["last_ch_backup_status"] == "ch_log_missing"
        assert state["last_ch_backup_verified"] is False
        assert state["last_run_outcome"] == "fake_green_blocked"

    def test_probe_error_fail_closed(self, reconciler_module, tmp_path):
        """交叉核验探针故障（复查一次仍失败）= fail-closed，同样不得记 ok"""
        result, state = self._run(
            reconciler_module,
            tmp_path,
            report={"found": True, "ch_status": "ok", "ch_verified": True, "reason": None, "report": "r.json"},
            probe={"ok": False, "count": 0, "max_event_time": "", "error": "http down"},
        )
        assert _field(result, "action") == "warn"
        assert state["last_backup_status"] == "ch_log_missing"
        assert state["last_ch_backup_status"] == "ch_log_missing"

    def test_report_missing_without_log_fail_closed(self, reconciler_module, tmp_path):
        """本轮报告缺失走 fail-closed 探针兜底；探针无行则不记 ok"""
        result, state = self._run(
            reconciler_module,
            tmp_path,
            report={"found": False, "ch_status": None, "ch_verified": None, "reason": None, "report": None},
            probe={"ok": True, "count": 0, "max_event_time": "", "error": None},
        )
        assert _field(result, "action") == "warn"
        assert state["last_backup_status"] == "ch_log_missing"

    def test_ch_service_down_is_degraded_not_silent(self, reconciler_module, tmp_path):
        """P1-7：CH 宕机跳过不得隐身——outcome 记 ok_ch_degraded 而非 ok_ch_skipped"""
        result, state = self._run(
            reconciler_module,
            tmp_path,
            report={
                "found": True,
                "ch_status": "skipped",
                "ch_verified": None,
                "reason": "service down",
                "report": "r.json",
            },
            probe={"ok": True, "count": 0, "max_event_time": "", "error": None},
        )
        assert _field(result, "action") == "auto_committed"
        assert state["last_backup_status"] == "ok"
        assert state["last_run_outcome"] == "ok_ch_degraded"
        assert "service down" in state["last_ch_skip_reason"]

    def test_probe_retry_recovers_after_flush_delay(self, reconciler_module, tmp_path):
        """P2-10/P1-4：首查零行（flush 延迟）-> 复查出行 -> 放行为 backed_up"""
        result, state = self._run(
            reconciler_module,
            tmp_path,
            report={"found": True, "ch_status": "ok", "ch_verified": True, "reason": None, "report": "r.json"},
            probe=[
                {"ok": True, "count": 0, "max_event_time": "", "error": None},
                {"ok": True, "count": 1, "max_event_time": "2026-09-24 06:05:00", "error": None},
            ],
        )
        assert _field(result, "action") == "auto_committed"
        assert state["last_backup_status"] == "ok"
        assert state["last_backup_log_verified"] is True

    def test_size_sanity_verified_false_demotes(self, reconciler_module, tmp_path):
        """P2-15b：ps1 尺寸自检 verified=false——即使 backup_log 有行也降级"""
        result, state = self._run(
            reconciler_module,
            tmp_path,
            report={"found": True, "ch_status": "ok", "ch_verified": False, "reason": None, "report": "r.json"},
            probe={"ok": True, "count": 3, "max_event_time": "x", "error": None},
        )
        assert _field(result, "action") == "warn"
        assert state["last_backup_status"] == "ch_log_missing"
        assert "size_sanity_failed" in _field(result, "detail")

    def test_ch_cadence_skip_is_legal_ok_and_recorded_separately(self, reconciler_module, tmp_path):
        """CH 24h cadence 跳过 -> 合法 ok，但 outcome 与 backed_up 分开记"""
        result, state = self._run(
            reconciler_module,
            tmp_path,
            report={"found": True, "ch_status": "skipped", "reason": "24h cadence (last 5.0h ago)", "report": "r.json"},
            probe={"ok": True, "count": 0, "max_event_time": "", "error": None},
        )
        assert _field(result, "action") == "auto_committed"
        assert state["last_backup_status"] == "ok"
        assert state["last_run_outcome"] == "ok_ch_skipped"
        assert "cadence" in state["last_ch_skip_reason"]

    def test_ch_failed_exit2_keeps_warn_semantics(self, reconciler_module, tmp_path):
        """exit=2（CH 失败）保持 warn + ch_failed，且 P2-12 卫生字段落地"""
        result, state = self._run(
            reconciler_module,
            tmp_path,
            returncode=2,
            report={"found": True, "ch_status": "failed", "ch_verified": None, "reason": None, "report": "r.json"},
            probe={"ok": True, "count": 5, "max_event_time": "x", "error": None},
        )
        assert _field(result, "action") == "warn"
        assert state["last_backup_status"] == "ch_failed"
        assert state["last_run_outcome"] == "ch_failed"
        assert state["last_backup_log_verified"] is False

    def test_trigger_cadence_skip_writes_separate_state(self, reconciler_module, tmp_path):
        """8h 节奏闸拦下触发时，last_cadence_skip_* 单独落账（隔离在 tmp）"""
        recent_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        state_file = tmp_path / "backup_state.json"
        committed = [str(tmp_path / "src" / "foo.py")]
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "load_state", return_value={"last_backup_time": recent_time}),
            patch.object(reconciler_module, "get_state_file", return_value=state_file),
        ):
            assert reconciler_module.trigger(committed) is False
        written = json.loads(state_file.read_text(encoding="utf-8"))
        assert "last_cadence_skip_time" in written
        assert "min_interval" in written["last_cadence_skip_reason"]

    def test_report_discovered_via_stdout_path(self, reconciler_module, tmp_path):
        """报告在主仓 logs（backup.ps1 硬编码）而 PROJECT_ROOT=worktree 时，
        靠 stdout 的 Report saved: 路径通道仍能读到本轮报告（2026-09-24 实战案例）。"""
        from types import SimpleNamespace

        real_logs = tmp_path / "main_repo_logs"
        real_logs.mkdir()
        report_path = real_logs / "backup_report_20260924_060000.json"
        report_path.write_text(
            json.dumps({"databases": {"clickhouse": {"status": "ok", "mode": "incremental"}}}),
            encoding="utf-8",
        )
        ps1 = tmp_path / "scripts" / "backup" / "backup.ps1"
        ps1.parent.mkdir(parents=True, exist_ok=True)
        ps1.write_text("# fake backup.ps1", encoding="utf-8")
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=tmp_path / "backup_state.json"),
            patch.object(
                reconciler_module.subprocess,
                "run",
                return_value=SimpleNamespace(returncode=0, stdout=f"Report saved: {report_path}", stderr=""),
            ),
            patch.object(
                reconciler_module,
                "query_backup_log_created",
                return_value={"ok": True, "count": 1, "max_event_time": "2026-09-24 06:10:00", "error": None},
            ),
        ):
            result = reconciler_module.reconcile([str(tmp_path / "src" / "x.py")], "sess-x")
        state = json.loads((tmp_path / "backup_state.json").read_text(encoding="utf-8"))
        assert _field(result, "action") == "auto_committed"
        assert state["last_backup_status"] == "ok"
        assert state["last_run_outcome"] == "backed_up"

    def test_lock_skip_leaves_state_untouched(self, reconciler_module, tmp_path):
        """P1-3：lock-skip 短退出=本轮没备份——不得推进计时、不得降级在飞备份的
        真实状态，只记 last_run_outcome=lock_skipped（2026-09-23 23:38 案例反转）。"""
        from types import SimpleNamespace

        ps1 = tmp_path / "scripts" / "backup" / "backup.ps1"
        ps1.parent.mkdir(parents=True, exist_ok=True)
        ps1.write_text("# fake backup.ps1", encoding="utf-8")
        seed = {
            "last_backup_time": "2026-09-24T00:00:00+00:00",
            "last_backup_status": "ok",
            "last_ch_backup_status": "ok",
            "last_ch_backup_verified": True,
        }
        state_file = tmp_path / "backup_state.json"
        state_file.write_text(json.dumps(seed), encoding="utf-8")
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=state_file),
            patch.object(
                reconciler_module.subprocess,
                "run",
                return_value=SimpleNamespace(returncode=0, stdout="Another backup is running", stderr=""),
            ),
        ):
            result = reconciler_module.reconcile([str(tmp_path / "src" / "x.py")], "sess-y")
        written = json.loads(state_file.read_text(encoding="utf-8"))
        assert _field(result, "action") == "warn"
        assert written["last_backup_status"] == "ok"  # 不被降级
        assert written["last_ch_backup_status"] == "ok"  # 不被摘除
        assert written["last_backup_time"] == seed["last_backup_time"]  # 计时不推进
        assert written["last_run_outcome"] == "lock_skipped"  # 只留观测行

    def test_state_saved_stdout_anchors_state_write(self, reconciler_module, tmp_path):
        """P0-1：stdout 携带 State saved: 主仓路径时，gate 裁决写入主仓 state
        而非 PROJECT_ROOT 下无消费者的副本（worktree 分家治理）。"""
        from types import SimpleNamespace

        main_root = tmp_path / "main_repo"
        (main_root / "data" / "databases").mkdir(parents=True)
        main_state = main_root / "data" / "databases" / "backup_state.json"
        ps1 = tmp_path / "scripts" / "backup" / "backup.ps1"
        ps1.parent.mkdir(parents=True, exist_ok=True)
        ps1.write_text("# fake backup.ps1", encoding="utf-8")
        with (
            patch.object(reconciler_module, "PROJECT_ROOT", tmp_path),
            patch.object(reconciler_module, "get_state_file", return_value=tmp_path / "backup_state.json"),
            patch.object(
                reconciler_module.subprocess,
                "run",
                return_value=SimpleNamespace(returncode=0, stdout=f"State saved: {main_state}", stderr=""),
            ),
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
            result = reconciler_module.reconcile([str(tmp_path / "src" / "x.py")], "sess-z")
        assert _field(result, "action") == "auto_committed"
        assert main_state.exists(), "gate must write the anchored main state file"
        written = json.loads(main_state.read_text(encoding="utf-8"))
        assert written["last_backup_status"] == "ok"
        assert written["last_run_outcome"] == "backed_up"

    def test_endpoint_missing_fail_closed(self, reconciler_module, tmp_path):
        """P1-9：CH env 缺失不再静默兜底 localhost——探针 fail-closed"""
        reconciler_module.CH_ENV_FILE = tmp_path / "nonexistent" / ".env.clickhouse"
        r = reconciler_module.query_backup_log_created(datetime.now(timezone.utc))
        assert r["ok"] is False
        assert "fail-closed" in (r.get("error") or "")
