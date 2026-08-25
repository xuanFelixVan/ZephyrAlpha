# [BLUEPRINT] MOD-INF-064 | docs/03_modules/_domain_infrastructure_runtime/trading_core_process/blueprint.md | §test
# [MODULE] tests.trading.test_trading_core_process_spec
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.trading_core_process_spec
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_trading_core_process_spec.py
# [A_test] module_id: MOD-INF-064 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-INF-064 单元测试: P3 交易核心进程规格 SSOT。

覆盖: 规格常量真源值（核 8-11 独占/8GB 禁 swap/NN 显存 2GB/心跳 2s/10s/HC-01）、
畸形规格 Fail-Closed、心跳键与 TTL（复用 MOD-INF-063 hb dynamic_ttl）、
配置就绪件声明 dict（仅声明不执行，含 Owner 窗口标注）、HC-01 不可放宽。
"""

from __future__ import annotations

import pytest

from zephyr.trading.trading_core_process_spec import (
    TRADING_CORE_SPEC,
    TradingCoreProcessSpec,
    TradingCoreSpecError,
    heartbeat_key,
    heartbeat_ttl_seconds,
    render_process_spec_declaration,
)


class TestSpecConstants:
    def test_identity_and_priority(self):
        spec = TRADING_CORE_SPEC
        assert spec.process_id == "P3"
        assert spec.process_name == "trading_core"
        assert spec.priority == 15

    def test_cpu_memory_gpu_budgets(self):
        spec = TRADING_CORE_SPEC
        assert spec.cpu_cores == (8, 9, 10, 11)
        assert spec.cpu_exclusive is True
        assert spec.memory_budget_gb == 8
        assert spec.swap_forbidden is True
        assert spec.risk_nn_vram_gb == 2

    def test_heartbeat_and_hc01(self):
        spec = TRADING_CORE_SPEC
        assert spec.heartbeat_interval_s == 2
        assert spec.heartbeat_timeout_s == 10
        assert spec.hc01_no_auto_restart is True
        assert spec.restart_policy == "alert_only_always"

    def test_duties(self):
        assert TRADING_CORE_SPEC.duties == ("风控检查", "订单构建", "miniQMT下单", "持仓同步")


class TestSpecValidation:
    def test_empty_duties_fail_closed(self):
        with pytest.raises(TradingCoreSpecError):
            TradingCoreProcessSpec(duties=())

    def test_heartbeat_interval_must_be_below_timeout(self):
        with pytest.raises(TradingCoreSpecError):
            TradingCoreProcessSpec(heartbeat_interval_s=10, heartbeat_timeout_s=10)

    def test_duplicate_cores_fail_closed(self):
        with pytest.raises(TradingCoreSpecError):
            TradingCoreProcessSpec(cpu_cores=(8, 8, 9, 10))

    def test_non_positive_memory_fail_closed(self):
        with pytest.raises(TradingCoreSpecError):
            TradingCoreProcessSpec(memory_budget_gb=0)

    def test_hc01_relaxation_rejected(self):
        with pytest.raises(TradingCoreSpecError):
            TradingCoreProcessSpec(hc01_no_auto_restart=True, restart_policy="auto_restart")


class TestHeartbeatContract:
    def test_heartbeat_key(self):
        assert heartbeat_key() == "hb:trading_core"

    def test_heartbeat_ttl_uses_mod_inf_063_rule(self):
        # TTL = 超时阈值 10s + 30s 缓冲（MOD-INF-063 hb 命名空间 dynamic_ttl）
        assert heartbeat_ttl_seconds() == 40


class TestConfigReadyDeclaration:
    def test_declaration_dict_shape(self):
        decl = render_process_spec_declaration()
        assert decl["process_id"] == "P3"
        assert decl["cpu"]["cores"] == [8, 9, 10, 11]
        assert decl["cpu"]["exclusive"] is True
        assert decl["memory"]["budget_gb"] == 8
        assert decl["memory"]["swap_forbidden"] is True
        assert decl["gpu"]["risk_nn_vram_gb"] == 2
        assert decl["heartbeat"]["key"] == "hb:trading_core"
        assert decl["heartbeat"]["ttl_seconds"] == 40

    def test_declaration_marks_owner_window(self):
        decl = render_process_spec_declaration()
        assert "Owner" in decl["apply_boundary"]
        assert decl["applied_by_ai"] is False
