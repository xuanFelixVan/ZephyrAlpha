# [BLUEPRINT] MOD-INF-070 | docs/03_modules/_domain_infrastructure_runtime/signal_engine_process/blueprint.md | §test
# [MODULE] tests.infrastructure.test_signal_engine_process_spec
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.signal_engine_process_spec
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_signal_engine_process_spec.py
# [A_test] module_id: MOD-INF-070 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-INF-070 单元测试: P2 信号引擎进程规格 SSOT（A9 §1.1.1/§1.1.3）。

覆盖: P2 规格真源值（四职责/核4-7/16GB/priority=20/hb 5s/30s/core_degrade）、
畸形规格 Fail-Closed、心跳键与 TTL（复用 MOD-INF-063 dynamic_ttl）、产出通道
声明（signal:* 60s + market:state）、supervisor P2 注册行双向对账、配置就绪件
仅声明不执行。
"""

from __future__ import annotations

import pytest

from zephyr.infrastructure.signal_engine_process_spec import (
    SIGNAL_ENGINE_SPEC,
    SignalEngineProcessSpec,
    SignalEngineSpecError,
    check_supervisor_alignment,
    heartbeat_key,
    heartbeat_ttl_seconds,
    render_process_spec_declaration,
)


class TestSpecTruthValues:
    def test_identity(self):
        spec = SIGNAL_ENGINE_SPEC
        assert spec.process_id == "P2"
        assert spec.process_name == "signal_engine"
        assert spec.priority == 20

    def test_duties(self):
        assert SIGNAL_ENGINE_SPEC.duties == ("因子计算", "信号生成", "策略路由", "市场状态判定")

    def test_resources(self):
        assert SIGNAL_ENGINE_SPEC.cpu_cores == (4, 5, 6, 7)
        assert SIGNAL_ENGINE_SPEC.memory_budget_gb == 16

    def test_heartbeat(self):
        assert SIGNAL_ENGINE_SPEC.heartbeat_interval_s == 5
        assert SIGNAL_ENGINE_SPEC.heartbeat_timeout_s == 30

    def test_restart_policy_core_degrade(self):
        spec = SIGNAL_ENGINE_SPEC
        assert spec.restart_class == "core_degrade"
        assert spec.trading_hours_degrade == "alert_and_p3_cached_signal"
        assert spec.max_restart_attempts == 3

    def test_output_channels(self):
        spec = SIGNAL_ENGINE_SPEC
        assert spec.signal_key_pattern == "signal:{strategy_id}:{date}"
        assert spec.signal_ttl_seconds == 60
        assert spec.market_state_key == "market:state:current"


class TestFailClosed:
    def test_empty_duties(self):
        with pytest.raises(SignalEngineSpecError):
            SignalEngineProcessSpec(duties=())

    def test_heartbeat_interval_ge_timeout(self):
        with pytest.raises(SignalEngineSpecError):
            SignalEngineProcessSpec(heartbeat_interval_s=30, heartbeat_timeout_s=30)

    def test_duplicate_cores(self):
        with pytest.raises(SignalEngineSpecError):
            SignalEngineProcessSpec(cpu_cores=(4, 4, 6, 7))

    def test_negative_core(self):
        with pytest.raises(SignalEngineSpecError):
            SignalEngineProcessSpec(cpu_cores=(4, 5, -1, 7))

    def test_non_positive_memory(self):
        with pytest.raises(SignalEngineSpecError):
            SignalEngineProcessSpec(memory_budget_gb=0)

    def test_unknown_restart_class(self):
        with pytest.raises(SignalEngineSpecError):
            SignalEngineProcessSpec(restart_class="critical_no_restart")

    def test_non_positive_signal_ttl(self):
        with pytest.raises(SignalEngineSpecError):
            SignalEngineProcessSpec(signal_ttl_seconds=0)


class TestHeartbeat:
    def test_heartbeat_key(self):
        assert heartbeat_key() == "hb:signal_engine"

    def test_heartbeat_ttl_reuses_dynamic_ttl(self):
        # MOD-INF-063 规则：TTL = 超时阈值 + 30s 缓冲（不重造）
        assert heartbeat_ttl_seconds() == 30 + 30


class TestSupervisorAlignment:
    def test_aligned_with_five_process_registry(self):
        spec = check_supervisor_alignment()
        assert spec is SIGNAL_ENGINE_SPEC

    def test_registry_row_fields(self):
        from zephyr.infrastructure.process_supervisor import get_process_spec

        row = get_process_spec("P2")
        spec = SIGNAL_ENGINE_SPEC
        assert row.process_name == spec.process_name
        assert row.priority == spec.priority
        assert row.cpu_cores == spec.cpu_cores
        assert row.memory_budget_gb == spec.memory_budget_gb
        assert row.heartbeat_interval_s == spec.heartbeat_interval_s
        assert row.heartbeat_timeout_s == spec.heartbeat_timeout_s
        assert row.duties == "/".join(spec.duties)


class TestNamespaceAlignment:
    def test_signal_namespace_truth(self):
        from zephyr.infrastructure.redis_state_layer_ssot import get_namespace

        ns = get_namespace("signal")
        assert ns.producer == "P2"
        assert ns.ttl_seconds == SIGNAL_ENGINE_SPEC.signal_ttl_seconds
        assert ns.key_pattern == SIGNAL_ENGINE_SPEC.signal_key_pattern

    def test_market_state_namespace_truth(self):
        from zephyr.infrastructure.redis_state_layer_ssot import get_namespace

        ns = get_namespace("market_state")
        assert ns.producer == "P2"
        assert ns.key_pattern == SIGNAL_ENGINE_SPEC.market_state_key


class TestDeclaration:
    def test_render_declaration_shape(self):
        decl = render_process_spec_declaration()
        assert decl["process_id"] == "P2"
        assert decl["process_name"] == "signal_engine"
        assert decl["cpu_cores"] == [4, 5, 6, 7]
        assert decl["memory_budget_gb"] == 16
        assert decl["heartbeat"]["key"] == "hb:signal_engine"
        assert decl["heartbeat"]["interval_s"] == 5
        assert decl["heartbeat"]["timeout_s"] == 30
        assert decl["restart"]["restart_class"] == "core_degrade"
        assert decl["output_channels"]["signal_pubsub"] == "signal:*"
        assert decl["output_channels"]["market_state"] == "market:state:current"

    def test_declaration_is_declaration_only(self):
        decl = render_process_spec_declaration()
        assert decl["execution_boundary"] == "declaration_only_owner_window"
