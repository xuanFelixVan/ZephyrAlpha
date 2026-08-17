# [A_test] module_id: MOD-GOV_async_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §16
# [MODULE] zephyr.security.adversarial_validation.async_monitor
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_async_monitor.py
# [TTL] task_bound

import re
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

async_monitor_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.async_monitor",
    reason="async_monitor not available",
)
AsyncMonitor = async_monitor_mod.AsyncMonitor
MonitorAlert = async_monitor_mod.MonitorAlert
MonitorStallError = async_monitor_mod.MonitorStallError
MonitorState = async_monitor_mod.MonitorState
DEFAULT_POLL_INTERVAL_S = async_monitor_mod.DEFAULT_POLL_INTERVAL_S

circuit_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.circuit_breaker",
    reason="circuit_breaker not available",
)
CircuitState = circuit_mod.CircuitState

cold_start_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.cold_start",
    reason="cold_start not available",
)
ColdStart = cold_start_mod.ColdStart
BootstrapPhase = cold_start_mod.BootstrapPhase
BootstrapVerificationError = cold_start_mod.BootstrapVerificationError
REGISTRATION_TEMPLATES = cold_start_mod.REGISTRATION_TEMPLATES


@pytest.fixture
def safe_monitor(monkeypatch):
    """创建一个 check 方法被 mock 为 no-op 的 AsyncMonitor，避免文件系统副作用。"""
    monitor = AsyncMonitor(poll_interval_s=5)
    monkeypatch.setattr(monitor, "check_circuit_breaker", lambda: None)
    monkeypatch.setattr(monitor, "check_bypass_backlog", lambda: None)
    monkeypatch.setattr(monitor, "check_cleanup_residue", lambda: None)
    return monitor


@pytest.fixture
def temp_registry(tmp_path: Path) -> Path:
    """创建临时场景注册表路径（文件不存在，由 ColdStart 初始化）。"""
    return tmp_path / "_scenario_registry.yaml"


@pytest.fixture
def cold_start(temp_registry: Path) -> ColdStart:
    """创建使用临时注册表的 ColdStart 实例。"""
    return ColdStart(registry_path=temp_registry)


# ============================================================================
# AsyncMonitor 导入与基础结构测试
# ============================================================================


class TestAsyncMonitorImport:
    def test_import_success(self):
        assert AsyncMonitor is not None

    def test_monitor_state_enum_values(self):
        assert MonitorState.IDLE.value == "IDLE"
        assert MonitorState.RUNNING.value == "RUNNING"
        assert MonitorState.STALLED.value == "STALLED"
        assert MonitorState.STOPPED.value == "STOPPED"

    def test_monitor_stall_error_is_runtime_error(self):
        assert issubclass(MonitorStallError, RuntimeError)

    def test_monitor_alert_attributes(self):
        alert = MonitorAlert("test_monitor", "HIGH", "test message")
        assert alert.monitor == "test_monitor"
        assert alert.severity == "HIGH"
        assert alert.message == "test message"
        assert isinstance(alert.timestamp, float)

    def test_default_poll_interval_constant(self):
        assert DEFAULT_POLL_INTERVAL_S == 30


# ============================================================================
# AsyncMonitor 构造与初始化测试
# ============================================================================


class TestAsyncMonitorInit:
    def test_default_poll_interval_is_30(self):
        monitor = AsyncMonitor()
        assert monitor.poll_interval_s == 30

    def test_custom_poll_interval(self):
        monitor = AsyncMonitor(poll_interval_s=10)
        assert monitor.poll_interval_s == 10

    def test_poll_interval_below_minimum_clamped_to_5(self):
        monitor = AsyncMonitor(poll_interval_s=3)
        assert monitor.poll_interval_s == 5

    def test_poll_interval_exactly_5(self):
        monitor = AsyncMonitor(poll_interval_s=5)
        assert monitor.poll_interval_s == 5

    def test_poll_interval_zero_clamped_to_5(self):
        monitor = AsyncMonitor(poll_interval_s=0)
        assert monitor.poll_interval_s == 5

    def test_initial_state_is_idle(self):
        monitor = AsyncMonitor()
        assert monitor.state == MonitorState.IDLE

    def test_initial_alerts_empty(self):
        monitor = AsyncMonitor()
        assert monitor.alerts() == []
        assert monitor.alert_count() == 0

    def test_initial_consecutive_failures_zero(self):
        monitor = AsyncMonitor()
        assert monitor.consecutive_failures == 0

    def test_has_circuit_breaker(self):
        monitor = AsyncMonitor()
        assert monitor.circuit_breaker is not None

    def test_has_bypass_recorder(self):
        monitor = AsyncMonitor()
        assert monitor.bypass_recorder is not None

    def test_has_stop_event(self):
        monitor = AsyncMonitor()
        assert monitor.stop_event is not None
        assert monitor.stop_event.is_set() is False

    def test_thread_initially_none(self):
        monitor = AsyncMonitor()
        assert monitor.thread is None


# ============================================================================
# AsyncMonitor 启动/停止生命周期测试
# ============================================================================


class TestAsyncMonitorLifecycle:
    def test_start_transitions_to_running(self, safe_monitor):
        assert safe_monitor.state == MonitorState.IDLE
        safe_monitor.start()
        assert safe_monitor.state == MonitorState.RUNNING
        safe_monitor.stop()

    def test_stop_transitions_to_stopped(self, safe_monitor):
        safe_monitor.start()
        safe_monitor.stop()
        assert safe_monitor.state == MonitorState.STOPPED

    def test_start_when_already_running_is_noop(self, safe_monitor):
        safe_monitor.start()
        first_thread = safe_monitor.thread
        assert first_thread is not None
        safe_monitor.start()
        assert safe_monitor.thread is first_thread
        safe_monitor.stop()

    def test_stop_without_start(self):
        monitor = AsyncMonitor()
        monitor.stop()
        assert monitor.state == MonitorState.STOPPED

    def test_start_creates_daemon_thread(self, safe_monitor):
        safe_monitor.start()
        assert safe_monitor.thread is not None
        assert safe_monitor.thread.daemon is True
        safe_monitor.stop()

    def test_stop_joins_thread(self, safe_monitor):
        safe_monitor.start()
        thread = safe_monitor.thread
        safe_monitor.stop()
        assert thread is not None

    def test_stop_sets_stop_event(self, safe_monitor):
        safe_monitor.start()
        safe_monitor.stop()
        assert safe_monitor.stop_event.is_set() is True

    def test_can_restart_after_stop(self, safe_monitor):
        safe_monitor.start()
        safe_monitor.stop()
        safe_monitor.start()
        assert safe_monitor.state == MonitorState.RUNNING
        safe_monitor.stop()


# ============================================================================
# AsyncMonitor 告警管理测试
# ============================================================================


class TestAsyncMonitorAlerts:
    def test_alerts_returns_copy(self):
        monitor = AsyncMonitor()
        alerts1 = monitor.alerts()
        alerts1.append(MonitorAlert("fake", "LOW", "fake"))
        alerts2 = monitor.alerts()
        assert len(alerts2) == 0

    def test_alert_count(self):
        monitor = AsyncMonitor()
        monitor.add_alert(MonitorAlert("m1", "LOW", "msg1"))
        monitor.add_alert(MonitorAlert("m2", "HIGH", "msg2"))
        assert monitor.alert_count() == 2

    def test_clear_alerts(self):
        monitor = AsyncMonitor()
        monitor.add_alert(MonitorAlert("m1", "LOW", "msg1"))
        monitor.clear_alerts()
        assert monitor.alert_count() == 0
        assert monitor.alerts() == []


# ============================================================================
# AsyncMonitor 30秒轮询间隔测试
# ============================================================================


class TestAsyncMonitorPollInterval:
    def test_default_interval_is_30_seconds(self):
        monitor = AsyncMonitor()
        assert monitor.poll_interval_s == 30

    def test_default_interval_constant_matches(self):
        assert AsyncMonitor().poll_interval_s == DEFAULT_POLL_INTERVAL_S

    def test_interval_used_in_wait(self, monkeypatch):
        captured_intervals = []
        monitor = AsyncMonitor(poll_interval_s=7)

        def mock_wait(timeout=None):
            captured_intervals.append(timeout)
            monitor.stop_event.set()
            return True

        monkeypatch.setattr(monitor.stop_event, "wait", mock_wait)
        monkeypatch.setattr(monitor, "check_circuit_breaker", lambda: None)
        monkeypatch.setattr(monitor, "check_bypass_backlog", lambda: None)
        monkeypatch.setattr(monitor, "check_cleanup_residue", lambda: None)

        monitor.monitor_loop()
        assert 7 in captured_intervals


# ============================================================================
# AsyncMonitor monitor_loop 轮询方法测试
# ============================================================================


class TestAsyncMonitorMonitorLoop:
    def test_loop_calls_all_checks_once(self, monkeypatch):
        monitor = AsyncMonitor(poll_interval_s=5)
        calls = {"cb": 0, "bb": 0, "cr": 0}

        monkeypatch.setattr(monitor, "check_circuit_breaker", lambda: calls.__setitem__("cb", calls["cb"] + 1))
        monkeypatch.setattr(monitor, "check_bypass_backlog", lambda: calls.__setitem__("bb", calls["bb"] + 1))
        monkeypatch.setattr(monitor, "check_cleanup_residue", lambda: calls.__setitem__("cr", calls["cr"] + 1))

        def mock_wait(timeout=None):
            monitor.stop_event.set()
            return True

        monkeypatch.setattr(monitor.stop_event, "wait", mock_wait)
        monitor.monitor_loop()

        assert calls["cb"] == 1
        assert calls["bb"] == 1
        assert calls["cr"] == 1

    def test_loop_resets_failures_on_success(self, monkeypatch):
        monitor = AsyncMonitor(poll_interval_s=5)
        monitor.consecutive_failures = 3

        monkeypatch.setattr(monitor, "check_circuit_breaker", lambda: None)
        monkeypatch.setattr(monitor, "check_bypass_backlog", lambda: None)
        monkeypatch.setattr(monitor, "check_cleanup_residue", lambda: None)

        def mock_wait(timeout=None):
            monitor.stop_event.set()
            return True

        monkeypatch.setattr(monitor.stop_event, "wait", mock_wait)
        monitor.monitor_loop()

        assert monitor.consecutive_failures == 0

    def test_loop_exits_when_stop_event_set(self):
        monitor = AsyncMonitor(poll_interval_s=5)
        monitor.stop_event.set()
        monitor.monitor_loop()
        assert monitor.state == MonitorState.IDLE


# ============================================================================
# AsyncMonitor 连续5次失败进入 STALLED 状态测试
# ============================================================================


class TestAsyncMonitorStallDetection:
    def test_stalled_after_five_consecutive_failures(self, monkeypatch):
        monitor = AsyncMonitor(poll_interval_s=5)

        def raising_check():
            raise RuntimeError("simulated monitor failure")

        monkeypatch.setattr(monitor, "check_circuit_breaker", raising_check)
        monkeypatch.setattr(monitor, "check_bypass_backlog", raising_check)
        monkeypatch.setattr(monitor, "check_cleanup_residue", raising_check)

        wait_call_count = {"n": 0}

        def mock_wait(timeout=None):
            wait_call_count["n"] += 1
            if wait_call_count["n"] >= 5:
                monitor.stop_event.set()
            return False

        monkeypatch.setattr(monitor.stop_event, "wait", mock_wait)
        monitor.monitor_loop()

        assert monitor.state == MonitorState.STALLED
        assert monitor.consecutive_failures >= 5

    def test_stall_produces_critical_alert(self, monkeypatch):
        monitor = AsyncMonitor(poll_interval_s=5)

        def raising_check():
            raise RuntimeError("simulated monitor failure")

        monkeypatch.setattr(monitor, "check_circuit_breaker", raising_check)
        monkeypatch.setattr(monitor, "check_bypass_backlog", raising_check)
        monkeypatch.setattr(monitor, "check_cleanup_residue", raising_check)

        wait_call_count = {"n": 0}

        def mock_wait(timeout=None):
            wait_call_count["n"] += 1
            if wait_call_count["n"] >= 5:
                monitor.stop_event.set()
            return False

        monkeypatch.setattr(monitor.stop_event, "wait", mock_wait)
        monitor.monitor_loop()

        stall_alerts = [a for a in monitor.alerts() if a.monitor == "stall_detector"]
        assert len(stall_alerts) >= 1
        assert stall_alerts[0].severity == "CRITICAL"
        assert "stalled" in stall_alerts[0].message.lower()

    def test_four_failures_does_not_stall(self, monkeypatch):
        monitor = AsyncMonitor(poll_interval_s=5)

        def raising_check():
            raise RuntimeError("simulated monitor failure")

        monkeypatch.setattr(monitor, "check_circuit_breaker", raising_check)
        monkeypatch.setattr(monitor, "check_bypass_backlog", raising_check)
        monkeypatch.setattr(monitor, "check_cleanup_residue", raising_check)

        wait_call_count = {"n": 0}

        def mock_wait(timeout=None):
            wait_call_count["n"] += 1
            if wait_call_count["n"] >= 4:
                monitor.stop_event.set()
            return False

        monkeypatch.setattr(monitor.stop_event, "wait", mock_wait)
        monitor.monitor_loop()

        assert monitor.state != MonitorState.STALLED
        assert monitor.consecutive_failures == 4

    def test_failures_reset_on_success(self, monkeypatch):
        monitor = AsyncMonitor(poll_interval_s=5)
        call_count = {"n": 0}

        def mixed_check():
            call_count["n"] += 1
            if call_count["n"] <= 2:
                raise RuntimeError("fail")
            # 后续成功

        monkeypatch.setattr(monitor, "check_circuit_breaker", mixed_check)
        monkeypatch.setattr(monitor, "check_bypass_backlog", lambda: None)
        monkeypatch.setattr(monitor, "check_cleanup_residue", lambda: None)

        wait_call_count = {"n": 0}

        def mock_wait(timeout=None):
            wait_call_count["n"] += 1
            if wait_call_count["n"] >= 4:
                monitor.stop_event.set()
            return False

        monkeypatch.setattr(monitor.stop_event, "wait", mock_wait)
        monitor.monitor_loop()

        assert monitor.state != MonitorState.STALLED
        assert monitor.consecutive_failures == 0


# ============================================================================
# AsyncMonitor 监控项: circuit_breaker 测试
# ============================================================================


class TestAsyncMonitorCheckCircuitBreaker:
    def test_open_circuit_adds_high_alert(self):
        monitor = AsyncMonitor()
        monitor.circuit_breaker.force_state(CircuitState.OPEN, opened_at=time.time() * 1000)
        monitor.check_circuit_breaker()
        assert monitor.alert_count() == 1
        alert = monitor.alerts()[0]
        assert alert.monitor == "circuit_breaker"
        assert alert.severity == "HIGH"
        assert "OPEN" in alert.message

    def test_closed_circuit_no_alert(self):
        monitor = AsyncMonitor()
        monitor.circuit_breaker.force_state(CircuitState.CLOSED)
        monitor.check_circuit_breaker()
        assert monitor.alert_count() == 0

    def test_half_open_no_alert(self):
        monitor = AsyncMonitor()
        monitor.circuit_breaker.force_state(CircuitState.HALF_OPEN)
        monitor.check_circuit_breaker()
        assert monitor.alert_count() == 0


# ============================================================================
# AsyncMonitor 监控项: bypass_backlog 测试
# ============================================================================


class TestAsyncMonitorCheckBypassBacklog:
    def test_escalated_entries_add_medium_alert(self):
        monitor = AsyncMonitor()
        mock_recorder = MagicMock()
        mock_recorder.escalated_entries.return_value = [MagicMock(), MagicMock()]
        monitor.bypass_recorder = mock_recorder
        monitor.check_bypass_backlog()
        assert monitor.alert_count() == 1
        alert = monitor.alerts()[0]
        assert alert.monitor == "bypass_backlog"
        assert alert.severity == "MEDIUM"
        assert "2" in alert.message

    def test_no_escalated_entries_no_alert(self):
        monitor = AsyncMonitor()
        mock_recorder = MagicMock()
        mock_recorder.escalated_entries.return_value = []
        monitor.bypass_recorder = mock_recorder
        monitor.check_bypass_backlog()
        assert monitor.alert_count() == 0

    def test_single_escalated_entry_adds_alert(self):
        monitor = AsyncMonitor()
        mock_recorder = MagicMock()
        mock_recorder.escalated_entries.return_value = [MagicMock()]
        monitor.bypass_recorder = mock_recorder
        monitor.check_bypass_backlog()
        assert monitor.alert_count() == 1
        assert "1" in monitor.alerts()[0].message


# ============================================================================
# AsyncMonitor 监控项: cleanup_residue 测试
# ============================================================================


class TestAsyncMonitorCheckCleanupResidue:
    def test_residue_detected_adds_low_alert(self, monkeypatch):
        import zephyr.security.adversarial_validation.async_monitor as am_module

        monitor = AsyncMonitor()
        mock_cleanup = MagicMock()
        mock_cleanup.verified.return_value = False
        monkeypatch.setattr(am_module, "Cleanup", lambda: mock_cleanup)
        monitor.check_cleanup_residue()
        assert monitor.alert_count() == 1
        alert = monitor.alerts()[0]
        assert alert.monitor == "cleanup_residue"
        assert alert.severity == "LOW"
        assert "residue" in alert.message.lower()

    def test_clean_no_alert(self, monkeypatch):
        import zephyr.security.adversarial_validation.async_monitor as am_module

        monitor = AsyncMonitor()
        mock_cleanup = MagicMock()
        mock_cleanup.verified.return_value = True
        monkeypatch.setattr(am_module, "Cleanup", lambda: mock_cleanup)
        monitor.check_cleanup_residue()
        assert monitor.alert_count() == 0


# ============================================================================
# ColdStart 导入与基础结构测试
# ============================================================================


class TestColdStartImport:
    def test_import_success(self):
        assert ColdStart is not None

    def test_bootstrap_phase_enum_values(self):
        assert BootstrapPhase.SCAN.value == "SCAN"
        assert BootstrapPhase.MAP.value == "MAP"
        assert BootstrapPhase.REGISTER.value == "REGISTER"
        assert BootstrapPhase.VERIFY.value == "VERIFY"
        assert BootstrapPhase.COMPLETE.value == "COMPLETE"

    def test_bootstrap_verification_error_is_runtime_error(self):
        assert issubclass(BootstrapVerificationError, RuntimeError)

    def test_registration_templates_has_all_types(self):
        assert "python_module" in REGISTRATION_TEMPLATES
        assert "mcp_server" in REGISTRATION_TEMPLATES
        assert "script" in REGISTRATION_TEMPLATES

    def test_registration_templates_have_required_fields(self):
        for template_name, template in REGISTRATION_TEMPLATES.items():
            assert "name" in template, f"{template_name} missing name"
            assert "description" in template, f"{template_name} missing description"
            assert "tier" in template, f"{template_name} missing tier"
            assert "severity" in template, f"{template_name} missing severity"
            assert "target_module" in template, f"{template_name} missing target_module"
            assert "injection_vector" in template, f"{template_name} missing injection_vector"
            assert "defense" in template, f"{template_name} missing defense"
            assert "blast_radius" in template, f"{template_name} missing blast_radius"


# ============================================================================
# ColdStart 构造与初始化测试
# ============================================================================


class TestColdStartInit:
    def test_default_registry_path(self):
        cs = ColdStart()
        assert cs.registry_path is not None
        assert cs.registry_path.name == "_scenario_registry.yaml"

    def test_custom_registry_path(self, temp_registry):
        cs = ColdStart(registry_path=temp_registry)
        assert cs.registry_path == temp_registry

    def test_initial_phase_is_scan(self, cold_start):
        assert cold_start.phase == BootstrapPhase.SCAN


# ============================================================================
# ColdStart classify 分类测试
# ============================================================================


class TestColdStartClassify:
    def test_classify_python_module(self, cold_start):
        assert cold_start.classify("zephyr.trading.signal") == "python_module"

    def test_classify_mcp_server_by_name(self, cold_start):
        assert cold_start.classify("zephyr.infrastructure.mcp_server.foo") == "mcp_server"

    def test_classify_mcp_server_by_prefix(self, cold_start):
        assert cold_start.classify("mcp.myserver") == "mcp_server"

    def test_classify_script(self, cold_start):
        assert cold_start.classify("scripts/run_test.py") == "script"

    def test_classify_non_py_in_scripts_is_python_module(self, cold_start):
        assert cold_start.classify("scripts/readme.txt") == "python_module"

    def test_classify_plain_module(self, cold_start):
        assert cold_start.classify("zephyr.utils.helper") == "python_module"


# ============================================================================
# ColdStart onboard_module 新模块自动注册测试
# ============================================================================


class TestColdStartOnboardModule:
    def test_onboard_python_module_returns_scenario_id(self, cold_start):
        scenario_id = cold_start.onboard_module("zephyr.trading.new_module")
        assert scenario_id is not None
        assert scenario_id.startswith("RB-CS-")
        assert len(scenario_id) == len("RB-CS-") + 8

    def test_onboard_completes_to_complete_phase(self, cold_start):
        cold_start.onboard_module("zephyr.trading.new_module")
        assert cold_start.phase == BootstrapPhase.COMPLETE

    def test_onboard_creates_registry_file(self, cold_start, temp_registry):
        assert not temp_registry.exists()
        cold_start.onboard_module("zephyr.trading.new_module")
        assert temp_registry.exists()

    def test_onboard_writes_scenario_to_registry(self, cold_start, temp_registry):
        import yaml

        scenario_id = cold_start.onboard_module("zephyr.trading.new_module")
        with open(temp_registry, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        scenarios = raw.get("scenarios", [])
        assert len(scenarios) == 1
        assert scenarios[0]["scenario_id"] == scenario_id
        assert scenarios[0]["target_module"] == "zephyr.trading.new_module"
        assert scenarios[0]["source"] == "cold_start"
        assert scenarios[0]["status"] == "active"
        assert scenarios[0]["tier"] == "L1"

    def test_onboard_already_registered_returns_none(self, cold_start):
        first_id = cold_start.onboard_module("zephyr.trading.duplicate")
        assert first_id is not None
        second_id = cold_start.onboard_module("zephyr.trading.duplicate")
        assert second_id is None

    def test_onboard_already_registered_sets_complete_phase(self, cold_start):
        cold_start.onboard_module("zephyr.trading.duplicate")
        cold_start.onboard_module("zephyr.trading.duplicate")
        assert cold_start.phase == BootstrapPhase.COMPLETE

    def test_onboard_mcp_server_uses_mcp_template(self, cold_start, temp_registry):
        import yaml

        scenario_id = cold_start.onboard_module("zephyr.infrastructure.mcp_server.web_search")
        with open(temp_registry, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        scenario = raw["scenarios"][0]
        assert scenario["scenario_id"] == scenario_id
        assert "mcp_server" in scenario["name"].lower() or "MCP" in scenario["name"]
        assert scenario["injection_vector"] == "mcp.zephyr.infrastructure.mcp_server.web_search.tool_abuse"

    def test_onboard_script_uses_script_template(self, cold_start, temp_registry):
        import yaml

        scenario_id = cold_start.onboard_module("scripts/deploy.py")
        with open(temp_registry, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        scenario = raw["scenarios"][0]
        assert scenario["scenario_id"] == scenario_id
        assert scenario["severity"] == "LOW"
        assert scenario["target_module"] == "scripts/deploy.py"

    def test_onboard_verification_failure_raises_error(self, monkeypatch, cold_start):
        monkeypatch.setattr(cold_start, "verify_registration", lambda sid: False)
        with pytest.raises(BootstrapVerificationError):
            cold_start.onboard_module("zephyr.trading.failing_module")

    def test_onboard_verification_failure_leaves_verify_phase(self, monkeypatch, cold_start):
        monkeypatch.setattr(cold_start, "verify_registration", lambda sid: False)
        with pytest.raises(BootstrapVerificationError):
            cold_start.onboard_module("zephyr.trading.failing_module")
        assert cold_start.phase == BootstrapPhase.VERIFY

    def test_onboard_scenario_id_format(self, cold_start):
        scenario_id = cold_start.onboard_module("zephyr.test.module")
        pattern = r"^RB-CS-[0-9a-f]{8}$"
        assert re.match(pattern, scenario_id) is not None

    def test_onboard_two_different_modules(self, cold_start, temp_registry):
        import yaml

        id1 = cold_start.onboard_module("zephyr.module.alpha")
        id2 = cold_start.onboard_module("zephyr.module.beta")
        assert id1 != id2
        with open(temp_registry, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        assert len(raw["scenarios"]) == 2


# ============================================================================
# ColdStart onboard_batch 批量注册测试
# ============================================================================


class TestColdStartOnboardBatch:
    def test_batch_returns_list_of_ids(self, cold_start):
        paths = ["zephyr.module.one", "zephyr.module.two", "zephyr.module.three"]
        ids = cold_start.onboard_batch(paths)
        assert len(ids) == 3
        for sid in ids:
            assert sid.startswith("RB-CS-")

    def test_batch_skips_already_registered(self, cold_start):
        cold_start.onboard_module("zephyr.module.existing")
        paths = ["zephyr.module.existing", "zephyr.module.new"]
        ids = cold_start.onboard_batch(paths)
        assert len(ids) == 1

    def test_batch_empty_list_returns_empty(self, cold_start):
        ids = cold_start.onboard_batch([])
        assert ids == []

    def test_batch_mixed_types(self, cold_start):
        paths = [
            "zephyr.trading.module",
            "zephyr.infrastructure.mcp_server.svc",
            "scripts/helper.py",
        ]
        ids = cold_start.onboard_batch(paths)
        assert len(ids) == 3


# ============================================================================
# ColdStart 注册表初始化与验证测试
# ============================================================================


class TestColdStartRegistry:
    def test_init_registry_creates_file(self, cold_start, temp_registry):
        assert not temp_registry.exists()
        cold_start.init_registry()
        assert temp_registry.exists()
        import yaml

        with open(temp_registry, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        assert "scenarios" in raw
        assert raw["scenarios"] == []
        assert raw["total_count"] == 0

    def test_is_registered_returns_false_for_missing_file(self, cold_start, temp_registry):
        assert not temp_registry.exists()
        assert cold_start.is_registered("target_module", "anything") is False

    def test_is_registered_returns_true_after_onboard(self, cold_start):
        cold_start.onboard_module("zephyr.trading.registered")
        assert cold_start.is_registered("target_module", "zephyr.trading.registered") is True

    def test_is_registered_returns_false_for_unregistered(self, cold_start):
        cold_start.onboard_module("zephyr.trading.registered")
        assert cold_start.is_registered("target_module", "zephyr.trading.unregistered") is False

    def test_verify_registration_returns_true_after_onboard(self, cold_start):
        scenario_id = cold_start.onboard_module("zephyr.trading.verifiable")
        assert cold_start.verify_registration(scenario_id) is True

    def test_verify_registration_returns_false_for_unknown_id(self, cold_start):
        cold_start.onboard_module("zephyr.trading.verifiable")
        assert cold_start.verify_registration("RB-CS-nonexist") is False

    def test_verify_registration_returns_false_for_missing_file(self, cold_start, temp_registry):
        assert not temp_registry.exists()
        assert cold_start.verify_registration("RB-CS-anything") is False
