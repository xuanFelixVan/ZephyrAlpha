# [BLUEPRINT] MOD-INT-MATRIX | docs/03_modules/_domain_integration/integration_matrix_registry/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INT-MATRIX | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.integration.test_integration_matrix_registry
# [TESTS] src/zephyr/integration/integration_matrix_registry.py
"""MOD-INT-MATRIX 单元测试：integration_matrix_registry 集成交互矩阵注册表。

蓝图验收（B14-04736/CAND-BACL-005，A10 v6.0）：
四要素注册（系统×交互×协议×隔离策略，同条目幂等/冲突拒绝）+ 故障降级
链表（声明/查询/解析）+ 隔离规则 schema 校验（Fail-Closed）。
时钟全注入，纯内存不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.integration.integration_matrix_registry",
    reason="integration_matrix_registry not importable",
)

from zephyr.integration.integration_matrix_registry import (  # noqa: E402
    IntegrationMatrixError,
    IntegrationMatrixRegistry,
    IsolationPolicy,
    ProtocolKind,
)

_T0 = datetime.datetime(2026, 8, 27, 9, 30, 0)


def _registry() -> IntegrationMatrixRegistry:
    return IntegrationMatrixRegistry(clock=lambda: _T0)


def _seed_basic(reg: IntegrationMatrixRegistry) -> None:
    reg.register("tushare", "daily_bars", ProtocolKind.REST, IsolationPolicy.NETWORK)
    reg.register("akshare", "daily_bars", ProtocolKind.REST, IsolationPolicy.PROCESS)
    reg.register("ctp", "order_submit", ProtocolKind.GRPC, IsolationPolicy.SANDBOX)


# ──────────────────────────────────────────────────────────────────────────────
# 四要素注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_ok(self) -> None:
        reg = _registry()
        entry = reg.register("tushare", "daily_bars", ProtocolKind.REST, IsolationPolicy.NETWORK)
        assert entry.system == "tushare"
        assert entry.protocol is ProtocolKind.REST
        assert entry.isolation is IsolationPolicy.NETWORK
        assert entry.registered_at == _T0

    def test_empty_system_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register("", "daily_bars", ProtocolKind.REST, IsolationPolicy.NONE)

    def test_empty_interaction_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register("tushare", "", ProtocolKind.REST, IsolationPolicy.NONE)

    def test_invalid_protocol_type_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register("tushare", "bars", "rest", IsolationPolicy.NONE)

    def test_invalid_isolation_type_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register("tushare", "bars", ProtocolKind.REST, "network")

    def test_duplicate_same_entry_idempotent(self) -> None:
        reg = _registry()
        e1 = reg.register("tushare", "bars", ProtocolKind.REST, IsolationPolicy.NONE)
        e2 = reg.register("tushare", "bars", ProtocolKind.REST, IsolationPolicy.NONE)
        assert e1 is e2  # 幂等返回原条目
        assert len(reg.matrix()) == 1

    def test_conflicting_entry_rejected(self) -> None:
        reg = _registry()
        reg.register("tushare", "bars", ProtocolKind.REST, IsolationPolicy.NONE)
        with pytest.raises(IntegrationMatrixError):
            reg.register("tushare", "bars", ProtocolKind.GRPC, IsolationPolicy.NONE)
        with pytest.raises(IntegrationMatrixError):
            reg.register("tushare", "bars", ProtocolKind.REST, IsolationPolicy.SANDBOX)

    def test_same_interaction_different_system_ok(self) -> None:
        reg = _registry()
        reg.register("tushare", "daily_bars", ProtocolKind.REST, IsolationPolicy.NONE)
        reg.register("akshare", "daily_bars", ProtocolKind.SQL, IsolationPolicy.NONE)
        assert len(reg.matrix()) == 2


# ──────────────────────────────────────────────────────────────────────────────
# 隔离规则配置化（schema 校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestIsolationRule:
    def test_rule_ok(self) -> None:
        reg = _registry()
        entry = reg.register_rule(
            {
                "system": "tushare",
                "interaction": "daily_bars",
                "protocol": "rest",
                "isolation": "network",
            }
        )
        assert entry.protocol is ProtocolKind.REST
        assert entry.isolation is IsolationPolicy.NETWORK

    def test_rule_not_mapping_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register_rule(["not", "a", "mapping"])

    def test_rule_missing_key_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register_rule(
                {
                    "system": "tushare",
                    "interaction": "daily_bars",
                    "protocol": "rest",
                }
            )  # 缺 isolation

    def test_rule_empty_value_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register_rule(
                {
                    "system": "",
                    "interaction": "daily_bars",
                    "protocol": "rest",
                    "isolation": "network",
                }
            )

    def test_rule_bad_protocol_vocab_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register_rule(
                {
                    "system": "tushare",
                    "interaction": "daily_bars",
                    "protocol": "carrier-pigeon",
                    "isolation": "network",
                }
            )

    def test_rule_bad_isolation_vocab_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register_rule(
                {
                    "system": "tushare",
                    "interaction": "daily_bars",
                    "protocol": "rest",
                    "isolation": "vibe",
                }
            )

    def test_rule_non_string_value_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.register_rule(
                {
                    "system": "tushare",
                    "interaction": "daily_bars",
                    "protocol": 42,
                    "isolation": "network",
                }
            )


# ──────────────────────────────────────────────────────────────────────────────
# 故障降级链
# ──────────────────────────────────────────────────────────────────────────────


class TestFallbackChain:
    def test_set_and_query_chain(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        reg.set_fallback_chain("tushare", ("akshare", "ctp"))
        assert reg.fallback_chain_of("tushare") == ("akshare", "ctp")

    def test_undeclared_chain_empty(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        assert reg.fallback_chain_of("akshare") == ()

    def test_chain_unknown_system_raises(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        with pytest.raises(IntegrationMatrixError):
            reg.set_fallback_chain("ghost", ("akshare",))
        with pytest.raises(IntegrationMatrixError):
            reg.set_fallback_chain("tushare", ("ghost",))

    def test_chain_empty_raises(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        with pytest.raises(IntegrationMatrixError):
            reg.set_fallback_chain("tushare", ())

    def test_chain_with_self_raises(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        with pytest.raises(IntegrationMatrixError):
            reg.set_fallback_chain("tushare", ("akshare", "tushare"))

    def test_chain_with_duplicate_raises(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        with pytest.raises(IntegrationMatrixError):
            reg.set_fallback_chain("tushare", ("akshare", "akshare"))

    def test_resolve_fallback_first_alive(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        reg.set_fallback_chain("tushare", ("akshare", "ctp"))
        assert reg.resolve_fallback("tushare", set()) == "akshare"
        assert reg.resolve_fallback("tushare", {"akshare"}) == "ctp"
        assert reg.resolve_fallback("tushare", {"akshare", "ctp"}) is None

    def test_resolve_no_chain_returns_none(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        assert reg.resolve_fallback("ctp", set()) is None


# ──────────────────────────────────────────────────────────────────────────────
# 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_get_unknown_raises(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        with pytest.raises(IntegrationMatrixError):
            reg.get("tushare", "ghost")

    def test_interactions_of_sorted(self) -> None:
        reg = _registry()
        reg.register("tushare", "realtime_quote", ProtocolKind.WEBSOCKET, IsolationPolicy.NONE)
        reg.register("tushare", "daily_bars", ProtocolKind.REST, IsolationPolicy.NONE)
        names = [e.interaction for e in reg.interactions_of("tushare")]
        assert names == ["daily_bars", "realtime_quote"]

    def test_interactions_of_unknown_system_raises(self) -> None:
        reg = _registry()
        with pytest.raises(IntegrationMatrixError):
            reg.interactions_of("ghost")

    def test_matrix_deterministic_order(self) -> None:
        reg = _registry()
        _seed_basic(reg)
        keys = [(e.system, e.interaction) for e in reg.matrix()]
        assert keys == sorted(keys)
        assert len(keys) == 3
