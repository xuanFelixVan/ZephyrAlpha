# [BLUEPRINT] MOD-INF-066 | docs/03_modules/_domain_infrastructure_runtime/process_supervisor/blueprint.md | §test
# [MODULE] tests.infrastructure.test_process_supervisor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.process_supervisor
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_process_supervisor.py
# [A_test] module_id: MOD-INF-066 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-INF-066 单元测试: NSSM+5 进程架构与自研 Supervisor。

覆盖: 五进程注册表真源值（P1~P5 优先级/核/内存/心跳）、启动升序与关闭降序编排、
P3 先于 P1 / P1 先于 Redis 硬约束、分级心跳键与 TTL（复用 MOD-INF-063）、
崩溃重启判定全分支（HC-01 P3 恒告警/交易时段降级/非核心 3 次上限）、
注册表一致性自检、NSSM 服务定义与安装脚本草稿（仅就绪件不执行）。
"""

from __future__ import annotations

import pytest

from zephyr.infrastructure.process_supervisor import (
    FIVE_PROCESS_REGISTRY,
    ProcessSupervisorError,
    check_supervisor_consistency,
    compute_shutdown_order,
    compute_start_order,
    decide_crash_action,
    get_process_spec,
    heartbeat_key,
    heartbeat_ttl_seconds,
    render_nssm_install_script,
    render_nssm_service_definitions,
    shutdown_sequence_with_redis,
)


class TestFiveProcessRegistry:
    def test_five_processes_with_true_priorities(self):
        priorities = {spec.process_id: spec.priority for spec in FIVE_PROCESS_REGISTRY}
        assert priorities == {"P1": 10, "P2": 20, "P3": 15, "P4": 30, "P5": 40}

    def test_process_names(self):
        names = {spec.process_id: spec.process_name for spec in FIVE_PROCESS_REGISTRY}
        assert names == {
            "P1": "market_data",
            "P2": "signal_engine",
            "P3": "trading_core",
            "P4": "ai_autonomy",
            "P5": "ml_pipeline",
        }

    def test_cpu_and_memory_budgets(self):
        specs = {spec.process_id: spec for spec in FIVE_PROCESS_REGISTRY}
        assert specs["P1"].cpu_cores == (0, 1, 2, 3) and specs["P1"].memory_budget_gb == 8
        assert specs["P2"].cpu_cores == (4, 5, 6, 7) and specs["P2"].memory_budget_gb == 16
        assert specs["P3"].cpu_cores == (8, 9, 10, 11) and specs["P3"].memory_budget_gb == 8
        assert specs["P4"].cpu_cores == (12, 13, 14, 15) and specs["P4"].memory_budget_gb == 12
        assert specs["P5"].cpu_cores == (16, 17, 18, 19) and specs["P5"].memory_budget_gb == 20

    def test_get_process_spec_unknown_fail_closed(self):
        with pytest.raises(ProcessSupervisorError):
            get_process_spec("P9")


class TestOrchestrationOrder:
    def test_start_order_priority_ascending(self):
        assert compute_start_order() == ["P1", "P3", "P2", "P4", "P5"]

    def test_shutdown_order_priority_descending(self):
        assert compute_shutdown_order() == ["P5", "P4", "P2", "P3", "P1"]

    def test_p3_before_p1_on_shutdown(self):
        order = compute_shutdown_order()
        assert order.index("P3") < order.index("P1")

    def test_redis_after_p1_on_shutdown(self):
        seq = shutdown_sequence_with_redis()
        assert seq[-1] == "redis"
        assert seq.index("P1") < seq.index("redis")


class TestHeartbeat:
    def test_heartbeat_keys(self):
        assert heartbeat_key("P1") == "hb:market_data"
        assert heartbeat_key("P3") == "hb:trading_core"
        assert heartbeat_key("P5") == "hb:ml_pipeline"

    def test_heartbeat_intervals_timeouts(self):
        specs = {spec.process_id: spec for spec in FIVE_PROCESS_REGISTRY}
        assert (specs["P1"].heartbeat_interval_s, specs["P1"].heartbeat_timeout_s) == (3, 15)
        assert (specs["P3"].heartbeat_interval_s, specs["P3"].heartbeat_timeout_s) == (2, 10)
        assert (specs["P2"].heartbeat_interval_s, specs["P2"].heartbeat_timeout_s) == (5, 30)
        assert (specs["P4"].heartbeat_interval_s, specs["P4"].heartbeat_timeout_s) == (10, 60)
        assert (specs["P5"].heartbeat_interval_s, specs["P5"].heartbeat_timeout_s) == (30, 120)

    def test_heartbeat_ttl_uses_mod_inf_063_rule(self):
        assert heartbeat_ttl_seconds("P3") == 40  # 10+30
        assert heartbeat_ttl_seconds("P1") == 45  # 15+30


class TestCrashAction:
    def test_p3_never_auto_restart_any_time(self):
        for trading_hours in (True, False):
            verdict = decide_crash_action("P3", is_trading_hours=trading_hours)
            assert verdict.action == "alert_only"
            assert "HC-01" in verdict.reason

    def test_p1_trading_hours_alert_and_degrade(self):
        verdict = decide_crash_action("P1", is_trading_hours=True)
        assert verdict.action == "alert_and_degrade"

    def test_p1_off_hours_auto_restart(self):
        verdict = decide_crash_action("P1", is_trading_hours=False)
        assert verdict.action == "auto_restart"

    def test_p2_trading_hours_alert_and_degrade(self):
        verdict = decide_crash_action("P2", is_trading_hours=True)
        assert verdict.action == "alert_and_degrade"

    def test_p4_p5_auto_restart_even_trading_hours(self):
        for pid in ("P4", "P5"):
            verdict = decide_crash_action(pid, is_trading_hours=True)
            assert verdict.action == "auto_restart", pid

    def test_restart_loop_breaker_after_3_failures(self):
        verdict = decide_crash_action("P4", is_trading_hours=False, consecutive_failures=3)
        assert verdict.action == "alert_only"
        assert "3" in verdict.reason

    def test_unknown_process_fail_closed(self):
        with pytest.raises(ProcessSupervisorError):
            decide_crash_action("PX", is_trading_hours=True)


class TestConsistency:
    def test_registry_consistency(self):
        report = check_supervisor_consistency()
        assert report["ok"] is True
        assert report["issues"] == []


class TestNssmConfigReadyArtifacts:
    def test_service_definitions_five_entries(self):
        defs = render_nssm_service_definitions()
        assert len(defs) == 5
        names = [d["service_name"] for d in defs]
        assert names == [
            "ZephyrAlpha-P1",
            "ZephyrAlpha-P3",
            "ZephyrAlpha-P2",
            "ZephyrAlpha-P4",
            "ZephyrAlpha-P5",
        ]
        for d in defs:
            assert d["start_mode"] == "auto"
            assert "-m" in d["app_parameters"]
            assert d["log_hosting"]["app_stdout"].endswith(".log")

    def test_service_definitions_mark_owner_window(self):
        defs = render_nssm_service_definitions()
        for d in defs:
            assert d["applied_by_ai"] is False
            assert "Owner" in d["apply_boundary"]

    def test_install_script_is_draft_only(self):
        script = render_nssm_install_script()
        assert "nssm install ZephyrAlpha-P1" in script
        assert "nssm install ZephyrAlpha-P5" in script
        assert "DRAFT" in script
        assert "Owner" in script
