# [BLUEPRINT] MOD-INF-073 | docs/03_modules/_domain_integration/external_system_connector/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-073 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [MODULE] tests.integration.test_external_system_connector
# [TESTS] src/zephyr/integration/external_system_connector.py
"""MOD-INF-073 单元测试：external_system_connector 统一外部系统连接器契约。

蓝图验收（B1-00326/CAND-BACL-003，跨域元文档 §功能域模块·D-INTEGRATION）：
能力声明（行情/交易/另类）+ 统一登记（connector_id 唯一）+ 健康检查
（probe 注入）+ 配额管理（rate/daily 双维令牌桶，注入时钟）+
source_circuit_breaker 挂接（factory 注入）+ callable 过滤确定性排序。
全部内存构造，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.integration.external_system_connector",
    reason="external_system_connector not importable",
)

from zephyr.integration.external_system_connector import (  # noqa: E402
    ConnectorAlreadyRegisteredError,
    ConnectorCapability,
    ConnectorKind,
    ConnectorNotFoundError,
    ExternalConnectorError,
    ExternalSystemConnector,
    HealthStatus,
    QuotaExceeded,
    QuotaPolicy,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


class _FakeClock:
    def __init__(self) -> None:
        self.now = _T0

    def __call__(self) -> datetime.datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += datetime.timedelta(seconds=seconds)


class _FakeBreaker:
    """source_circuit_breaker 最小替身（状态机外观）。"""

    def __init__(self) -> None:
        self.is_open = False
        self.results: list[bool] = []

    def record(self, ok: bool) -> None:
        self.results.append(ok)
        if not ok:
            self.is_open = True


def _cap(kind: ConnectorKind, *ops: str, vendor: str = "vt") -> ConnectorCapability:
    return ConnectorCapability(kind=kind, operations=frozenset(ops), vendor=vendor)


# ──────────────────────────────────────────────────────────────────────────────
# 统一登记
# ──────────────────────────────────────────────────────────────────────────────


class TestRegistry:
    def test_register_and_profile(self) -> None:
        reg = ExternalSystemConnector()
        profile = reg.register(
            "miniqmt-01",
            _cap(ConnectorKind.TRADING, "place_order", "cancel_order", vendor="miniQMT"),
        )
        assert profile.connector_id == "miniqmt-01"
        assert profile.capability.kind is ConnectorKind.TRADING
        assert profile.health is HealthStatus.UNKNOWN
        assert "place_order" in profile.capability.operations

    def test_duplicate_register_raises(self) -> None:
        reg = ExternalSystemConnector()
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        with pytest.raises(ConnectorAlreadyRegisteredError):
            reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))

    def test_unregister_and_unknown(self) -> None:
        reg = ExternalSystemConnector()
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        reg.unregister("sina-01")
        with pytest.raises(ConnectorNotFoundError):
            reg.unregister("sina-01")
        with pytest.raises(ConnectorNotFoundError):
            reg.acquire("sina-01")

    def test_empty_connector_id_raises(self) -> None:
        reg = ExternalSystemConnector()
        with pytest.raises(ExternalConnectorError):
            reg.register("", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))

    def test_empty_operations_raises(self) -> None:
        reg = ExternalSystemConnector()
        with pytest.raises(ExternalConnectorError):
            reg.register("x-01", ConnectorCapability(
                kind=ConnectorKind.ALT_DATA, operations=frozenset(), vendor="v"
            ))


# ──────────────────────────────────────────────────────────────────────────────
# 健康检查（probe 注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestHealthCheck:
    def test_default_unknown(self) -> None:
        reg = ExternalSystemConnector()
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        assert reg.health_check("sina-01") is HealthStatus.UNKNOWN

    def test_probe_healthy(self) -> None:
        reg = ExternalSystemConnector(health_probe=lambda cid: HealthStatus.HEALTHY)
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        assert reg.health_check("sina-01") is HealthStatus.HEALTHY

    def test_probe_degraded(self) -> None:
        reg = ExternalSystemConnector(health_probe=lambda cid: HealthStatus.DEGRADED)
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        assert reg.health_check("sina-01") is HealthStatus.DEGRADED

    def test_probe_exception_maps_unhealthy_not_raise(self) -> None:
        def _bad(cid: str) -> HealthStatus:
            raise RuntimeError("probe down")

        reg = ExternalSystemConnector(health_probe=_bad)
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        assert reg.health_check("sina-01") is HealthStatus.UNHEALTHY


# ──────────────────────────────────────────────────────────────────────────────
# 配额管理（注入时钟）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuota:
    def test_rate_per_sec_exceeded(self) -> None:
        clock = _FakeClock()
        reg = ExternalSystemConnector(clock=clock)
        reg.register(
            "sina-01",
            _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"),
            quota=QuotaPolicy(rate_per_sec=2),
        )
        reg.acquire("sina-01")
        reg.acquire("sina-01")
        with pytest.raises(QuotaExceeded):
            reg.acquire("sina-01")
        clock.advance(1.0)  # 下一秒窗口重置
        reg.acquire("sina-01")

    def test_daily_cap_exceeded_across_seconds(self) -> None:
        clock = _FakeClock()
        reg = ExternalSystemConnector(clock=clock)
        reg.register(
            "sina-01",
            _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"),
            quota=QuotaPolicy(rate_per_sec=100, daily_cap=3),
        )
        for i in range(3):
            reg.acquire("sina-01")
            clock.advance(1.0)
        with pytest.raises(QuotaExceeded):
            reg.acquire("sina-01")

    def test_no_quota_unlimited(self) -> None:
        reg = ExternalSystemConnector()
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        for _ in range(1000):
            reg.acquire("sina-01")

    def test_invalid_quota_params_raise(self) -> None:
        reg = ExternalSystemConnector()
        with pytest.raises(ExternalConnectorError):
            QuotaPolicy(rate_per_sec=0)
        with pytest.raises(ExternalConnectorError):
            QuotaPolicy(daily_cap=0)
        with pytest.raises(ExternalConnectorError):
            reg.acquire("sina-01", n=0)


# ──────────────────────────────────────────────────────────────────────────────
# 熔断挂接与 callable 过滤
# ──────────────────────────────────────────────────────────────────────────────


class TestBreakerAndCallable:
    def test_breaker_factory_and_report_passthrough(self) -> None:
        breakers: dict[str, _FakeBreaker] = {}

        def _factory(cid: str) -> _FakeBreaker:
            breakers[cid] = _FakeBreaker()
            return breakers[cid]

        reg = ExternalSystemConnector(breaker_factory=_factory)
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        assert "sina-01" in breakers  # 登记即挂接
        reg.report_result("sina-01", True)
        reg.report_result("sina-01", False)
        assert breakers["sina-01"].results == [True, False]

    def test_open_breaker_not_callable(self) -> None:
        breaker = _FakeBreaker()
        reg = ExternalSystemConnector(breaker_factory=lambda cid: breaker)
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        assert reg.is_callable("sina-01") is True
        reg.report_result("sina-01", False)  # 触发熔断
        assert reg.is_callable("sina-01") is False

    def test_callable_connectors_filter_and_order(self) -> None:
        clock = _FakeClock()
        reg = ExternalSystemConnector(
            clock=clock,
            health_probe=lambda cid: (
                HealthStatus.UNHEALTHY if cid == "bad-01" else HealthStatus.HEALTHY
            ),
        )
        reg.register("b-02", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        reg.register("a-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        reg.register("bad-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        reg.register(
            "t-01", _cap(ConnectorKind.TRADING, "place_order"),
            quota=QuotaPolicy(rate_per_sec=1),
        )
        reg.acquire("t-01")
        with pytest.raises(QuotaExceeded):
            reg.acquire("t-01")  # t-01 配额触顶 → 不可调

        for cid in ("a-01", "b-02", "bad-01", "t-01"):
            reg.health_check(cid)  # 物化 probe 结论（bad-01 → UNHEALTHY）

        md = reg.callable_connectors(ConnectorKind.MARKET_DATA)
        assert [p.connector_id for p in md] == ["a-01", "b-02"]  # 排序+剔除 UNHEALTHY
        assert reg.callable_connectors(ConnectorKind.TRADING) == []  # 配额触顶剔除

    def test_report_result_without_breaker_noop(self) -> None:
        reg = ExternalSystemConnector()
        reg.register("sina-01", _cap(ConnectorKind.MARKET_DATA, "fetch_daily_kline"))
        reg.report_result("sina-01", False)  # 无熔断器不抛
        assert reg.is_callable("sina-01") is True
