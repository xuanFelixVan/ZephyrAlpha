# [BLUEPRINT] MOD-INF-063 | docs/03_modules/_domain_infrastructure_runtime/redis_state_layer_ssot/blueprint.md | §test
# [MODULE] tests.infrastructure.test_redis_state_layer_ssot
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.redis_state_layer_ssot
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_redis_state_layer_ssot.py
# [A_test] module_id: MOD-INF-063 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-INF-063 单元测试: Redis 共享状态层 SSOT — 13 命名空间/TTL 矩阵/混合持久化收口。

覆盖: 13 命名空间完整性与三层归属、TTL 矩阵真源值（tick=5s/signal=60s/factor=300s）、
RDB 每小时+AOF everysec 混合持久化参数、maxmemory 8GB 硬限+volatile-ttl、
AOF 重放优先恢复 runbook、redis.conf 配置就绪件草稿（仅文本不执行）、
Key 校验与未知命名空间 Fail-Closed、注册表一致性自检。
"""

from __future__ import annotations

import pytest

from zephyr.infrastructure.redis_state_layer_ssot import (
    NAMESPACE_TTL_MATRIX,
    REDIS_NAMESPACE_REGISTRY,
    REDIS_PERSISTENCE_PROFILE,
    RedisStateLayerSotError,
    check_registry_consistency,
    get_namespace,
    recovery_runbook,
    render_redis_conf_draft,
    ttl_for,
    validate_key,
)

_EXPECTED_NAMESPACES = frozenset(
    {
        "tick",
        "signal",
        "factor",
        "position",
        "order",
        "strategy",
        "market_state",
        "hb",
        "cmd",
        "alert",
        "config",
        "degrade",
        "gpu",
    }
)


class TestNamespaceRegistry:
    def test_registry_has_exactly_13_namespaces(self):
        assert len(REDIS_NAMESPACE_REGISTRY) == 13
        assert {spec.name for spec in REDIS_NAMESPACE_REGISTRY} == _EXPECTED_NAMESPACES

    def test_three_layer_assignment(self):
        layers = {spec.name: spec.layer for spec in REDIS_NAMESPACE_REGISTRY}
        for name in ("tick", "signal", "factor", "market_state"):
            assert layers[name] == "realtime_data", name
        for name in ("position", "order", "strategy", "hb"):
            assert layers[name] == "state_coordination", name
        for name in ("cmd", "alert", "config", "degrade", "gpu"):
            assert layers[name] == "ops_control", name

    def test_each_namespace_declares_producer_and_structure(self):
        for spec in REDIS_NAMESPACE_REGISTRY:
            assert spec.producer, spec.name
            assert spec.structure, spec.name
            assert spec.key_pattern.startswith(spec.name.split("_")[0]), spec.name

    def test_get_namespace_unknown_fail_closed(self):
        with pytest.raises(RedisStateLayerSotError):
            get_namespace("nonexistent_ns")


class TestTtlMatrix:
    def test_ttl_matrix_core_values(self):
        assert NAMESPACE_TTL_MATRIX["tick"] == 5
        assert NAMESPACE_TTL_MATRIX["signal"] == 60
        assert NAMESPACE_TTL_MATRIX["factor"] == 300
        assert NAMESPACE_TTL_MATRIX["cmd"] == 60
        assert NAMESPACE_TTL_MATRIX["alert"] == 3600

    def test_persistent_namespaces_have_no_ttl(self):
        for name in ("position", "order", "strategy", "market_state", "config", "degrade", "gpu"):
            assert NAMESPACE_TTL_MATRIX[name] is None, name

    def test_ttl_for_returns_matrix_value(self):
        assert ttl_for("tick") == 5
        assert ttl_for("position") is None

    def test_ttl_for_unknown_fail_closed(self):
        with pytest.raises(RedisStateLayerSotError):
            ttl_for("bogus")

    def test_hb_ttl_computed_from_process_timeout(self):
        spec = get_namespace("hb")
        # hb TTL = 各进程超时阈值 + 30s 缓冲（A9 §1.2 表注）
        assert spec.ttl_seconds is None  # 静态矩阵按进程动态计算
        assert callable(spec.dynamic_ttl)
        assert spec.dynamic_ttl(10) == 40


class TestPersistenceProfile:
    def test_rdb_hourly_baseline(self):
        profile = REDIS_PERSISTENCE_PROFILE
        assert ("3600", "1") in profile.rdb_save_rules

    def test_aof_everysec_enabled(self):
        profile = REDIS_PERSISTENCE_PROFILE
        assert profile.aof_enabled is True
        assert profile.aof_fsync == "everysec"

    def test_memory_hard_limit_and_eviction(self):
        profile = REDIS_PERSISTENCE_PROFILE
        assert profile.maxmemory_gb == 8
        assert profile.maxmemory_policy == "volatile-ttl"

    def test_recovery_aof_first_under_15s(self):
        profile = REDIS_PERSISTENCE_PROFILE
        assert profile.recovery_strategy == "aof_first_hybrid"
        assert profile.recovery_target_seconds <= 15


class TestConfigReadyDraft:
    def test_render_redis_conf_draft_contains_directives(self):
        draft = render_redis_conf_draft()
        assert "save 3600 1" in draft
        assert "appendonly yes" in draft
        assert "appendfsync everysec" in draft
        assert "maxmemory 8gb" in draft
        assert "maxmemory-policy volatile-ttl" in draft
        assert "aof-use-rdb-preamble yes" in draft

    def test_draft_is_text_only_no_side_effect(self):
        draft = render_redis_conf_draft()
        assert isinstance(draft, str)
        assert "Owner" in draft  # 草稿头标注：实际应用属 Owner 窗口

    def test_recovery_runbook_aof_first(self):
        steps = recovery_runbook()
        assert len(steps) >= 3
        joined = "\n".join(steps)
        assert "AOF" in joined
        assert "15" in joined


class TestKeyValidation:
    def test_validate_key_accepts_known_patterns(self):
        assert validate_key("tick:000001.SZ") == "tick"
        assert validate_key("signal:strat-1:2026-08-25") == "signal"
        assert validate_key("hb:trading_core") == "hb"
        assert validate_key("degrade:level") == "degrade"

    def test_validate_key_unknown_namespace_fail_closed(self):
        with pytest.raises(RedisStateLayerSotError):
            validate_key("unknownns:foo")

    def test_validate_key_rejects_empty(self):
        with pytest.raises(RedisStateLayerSotError):
            validate_key("")


class TestConsistency:
    def test_registry_consistency_self_check(self):
        report = check_registry_consistency()
        assert report["ok"] is True
        assert report["namespace_count"] == 13
        assert report["issues"] == []
