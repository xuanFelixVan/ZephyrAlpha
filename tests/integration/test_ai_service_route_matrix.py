# [BLUEPRINT] MOD-INT-AIROUTE | docs/03_modules/_domain_integration/ai_service_route_matrix/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INT-AIROUTE | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.integration.test_ai_service_route_matrix
# [TESTS] src/zephyr/integration/ai_service_route_matrix.py
"""MOD-INT-AIROUTE 单元测试：ai_service_route_matrix AI 服务分级路由表。

蓝图验收（B14-04762/CAND-BACL-006，A10）：
四类 AI 服务（本地LLM/API/ASR/MCP）× L1/L2/L3 分级注册 + 成本延迟画像
（单价/P50/P99 取值域校验）+ 故障降级链（首选不可用按链降级 + degrade_sink
标记留痕 + 全链不可用 Fail-Closed）。
健康探针/留痕回调全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.integration.ai_service_route_matrix",
    reason="ai_service_route_matrix not importable",
)

from zephyr.integration.ai_service_route_matrix import (  # noqa: E402
    AiRouteError,
    AiServiceRouteMatrix,
    CostProfile,
    DegradeEvent,
    ServiceClass,
    ServiceLevel,
)

_T0 = datetime.datetime(2026, 8, 27, 9, 30, 0)

_LOCAL = CostProfile(unit_price_per_1k=0.0, latency_p50_ms=80.0, latency_p99_ms=200.0)
_API = CostProfile(unit_price_per_1k=0.02, latency_p50_ms=300.0, latency_p99_ms=900.0)
_API_PREMIUM = CostProfile(unit_price_per_1k=0.08, latency_p50_ms=500.0, latency_p99_ms=1500.0)


def _matrix(
    down: set | None = None,
    events: list | None = None,
) -> AiServiceRouteMatrix:
    down = down or set()
    return AiServiceRouteMatrix(
        clock=lambda: _T0,
        health_probe=lambda sid: sid not in down,
        degrade_sink=(lambda e: events.append(e)) if events is not None else None,
    )


def _seed_chat(m: AiServiceRouteMatrix) -> None:
    m.register_service("ollama-qwen3", ServiceClass.LOCAL_LLM, ServiceLevel.L1, _LOCAL)
    m.register_service("deepseek-api", ServiceClass.API, ServiceLevel.L2, _API)
    m.register_service("claude-api", ServiceClass.API, ServiceLevel.L3, _API_PREMIUM)
    m.set_route("chat", ("ollama-qwen3", "deepseek-api", "claude-api"))


# ──────────────────────────────────────────────────────────────────────────────
# 服务注册（画像校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterService:
    def test_register_ok(self) -> None:
        m = _matrix()
        svc = m.register_service("ollama-qwen3", ServiceClass.LOCAL_LLM, ServiceLevel.L1, _LOCAL)
        assert svc.service_class is ServiceClass.LOCAL_LLM
        assert svc.level is ServiceLevel.L1
        assert svc.profile is _LOCAL

    def test_all_four_classes(self) -> None:
        m = _matrix()
        m.register_service("a", ServiceClass.LOCAL_LLM, ServiceLevel.L1, _LOCAL)
        m.register_service("b", ServiceClass.API, ServiceLevel.L2, _API)
        m.register_service("c", ServiceClass.ASR, ServiceLevel.L1, _LOCAL)
        m.register_service("d", ServiceClass.MCP, ServiceLevel.L2, _API)
        assert len(m.services()) == 4

    def test_empty_service_id_raises(self) -> None:
        m = _matrix()
        with pytest.raises(AiRouteError):
            m.register_service("", ServiceClass.API, ServiceLevel.L2, _API)

    def test_duplicate_service_id_raises(self) -> None:
        m = _matrix()
        m.register_service("x", ServiceClass.API, ServiceLevel.L2, _API)
        with pytest.raises(AiRouteError):
            m.register_service("x", ServiceClass.ASR, ServiceLevel.L1, _LOCAL)

    def test_invalid_class_raises(self) -> None:
        m = _matrix()
        with pytest.raises(AiRouteError):
            m.register_service("x", "api", ServiceLevel.L2, _API)

    def test_invalid_level_raises(self) -> None:
        m = _matrix()
        with pytest.raises(AiRouteError):
            m.register_service("x", ServiceClass.API, "L9", _API)

    def test_negative_price_raises(self) -> None:
        m = _matrix()
        bad = CostProfile(unit_price_per_1k=-0.01, latency_p50_ms=1.0, latency_p99_ms=2.0)
        with pytest.raises(AiRouteError):
            m.register_service("x", ServiceClass.API, ServiceLevel.L2, bad)

    def test_negative_latency_raises(self) -> None:
        m = _matrix()
        bad = CostProfile(unit_price_per_1k=0.0, latency_p50_ms=-1.0, latency_p99_ms=2.0)
        with pytest.raises(AiRouteError):
            m.register_service("x", ServiceClass.API, ServiceLevel.L2, bad)

    def test_p99_below_p50_raises(self) -> None:
        m = _matrix()
        bad = CostProfile(unit_price_per_1k=0.0, latency_p50_ms=500.0, latency_p99_ms=100.0)
        with pytest.raises(AiRouteError):
            m.register_service("x", ServiceClass.API, ServiceLevel.L2, bad)


# ──────────────────────────────────────────────────────────────────────────────
# 路由链声明
# ──────────────────────────────────────────────────────────────────────────────


class TestSetRoute:
    def test_set_route_ok(self) -> None:
        m = _matrix()
        _seed_chat(m)
        assert m.route_chain_of("chat") == ("ollama-qwen3", "deepseek-api", "claude-api")

    def test_empty_route_name_raises(self) -> None:
        m = _matrix()
        _seed_chat(m)
        with pytest.raises(AiRouteError):
            m.set_route("", ("ollama-qwen3",))

    def test_empty_chain_raises(self) -> None:
        m = _matrix()
        _seed_chat(m)
        with pytest.raises(AiRouteError):
            m.set_route("asr", ())

    def test_chain_with_unknown_service_raises(self) -> None:
        m = _matrix()
        _seed_chat(m)
        with pytest.raises(AiRouteError):
            m.set_route("asr", ("ollama-qwen3", "ghost"))

    def test_chain_with_duplicate_raises(self) -> None:
        m = _matrix()
        _seed_chat(m)
        with pytest.raises(AiRouteError):
            m.set_route("asr", ("deepseek-api", "deepseek-api"))

    def test_unknown_route_query_raises(self) -> None:
        m = _matrix()
        with pytest.raises(AiRouteError):
            m.route_chain_of("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 选路（降级链）
# ──────────────────────────────────────────────────────────────────────────────


class TestSelect:
    def test_select_preferred_when_healthy(self) -> None:
        events: list[DegradeEvent] = []
        m = _matrix(events=events)
        _seed_chat(m)
        decision = m.select("chat")
        assert decision.service_id == "ollama-qwen3"
        assert decision.position == 0
        assert decision.degraded is False
        assert decision.decided_at == _T0
        assert events == []

    def test_select_degrades_along_chain_with_mark(self) -> None:
        events: list[DegradeEvent] = []
        m = _matrix(down={"ollama-qwen3"}, events=events)
        _seed_chat(m)
        decision = m.select("chat")
        assert decision.service_id == "deepseek-api"
        assert decision.position == 1
        assert decision.degraded is True
        assert len(events) == 1
        assert events[0].preferred_id == "ollama-qwen3"
        assert events[0].selected_id == "deepseek-api"
        assert events[0].failed_ids == ("ollama-qwen3",)
        assert events[0].raised_at == _T0

    def test_select_skips_multiple_failures(self) -> None:
        events: list[DegradeEvent] = []
        m = _matrix(down={"ollama-qwen3", "deepseek-api"}, events=events)
        _seed_chat(m)
        decision = m.select("chat")
        assert decision.service_id == "claude-api"
        assert decision.degraded is True
        assert events[0].failed_ids == ("ollama-qwen3", "deepseek-api")

    def test_select_all_down_fail_closed(self) -> None:
        m = _matrix(down={"ollama-qwen3", "deepseek-api", "claude-api"})
        _seed_chat(m)
        with pytest.raises(AiRouteError):
            m.select("chat")

    def test_select_unknown_route_raises(self) -> None:
        m = _matrix()
        with pytest.raises(AiRouteError):
            m.select("ghost")

    def test_probe_exception_treated_as_down(self) -> None:
        def _bad_probe(sid: str) -> bool:
            if sid == "ollama-qwen3":
                raise RuntimeError("probe boom")
            return True

        m = AiServiceRouteMatrix(clock=lambda: _T0, health_probe=_bad_probe)
        _seed_chat(m)
        decision = m.select("chat")
        assert decision.service_id == "deepseek-api"
        assert decision.degraded is True

    def test_degrade_sink_exception_not_blocking(self) -> None:
        def _bad_sink(_: DegradeEvent) -> None:
            raise RuntimeError("boom")

        m = AiServiceRouteMatrix(
            clock=lambda: _T0,
            health_probe=lambda sid: sid != "ollama-qwen3",
            degrade_sink=_bad_sink,
        )
        _seed_chat(m)
        assert m.select("chat").service_id == "deepseek-api"  # 留痕异常不阻断

    def test_default_probe_all_healthy(self) -> None:
        m = AiServiceRouteMatrix(clock=lambda: _T0)
        _seed_chat(m)
        assert m.select("chat").service_id == "ollama-qwen3"


# ──────────────────────────────────────────────────────────────────────────────
# 画像查询
# ──────────────────────────────────────────────────────────────────────────────


class TestProfileQuery:
    def test_services_filter_by_class(self) -> None:
        m = _matrix()
        _seed_chat(m)
        apis = m.services(ServiceClass.API)
        assert [s.service_id for s in apis] == ["claude-api", "deepseek-api"]
        assert len(m.services()) == 3

    def test_services_invalid_class_raises(self) -> None:
        m = _matrix()
        with pytest.raises(AiRouteError):
            m.services("api")

    def test_cheapest(self) -> None:
        m = _matrix()
        _seed_chat(m)
        assert m.cheapest(ServiceClass.API).service_id == "deepseek-api"

    def test_fastest(self) -> None:
        m = _matrix()
        _seed_chat(m)
        assert m.fastest(ServiceClass.API).service_id == "deepseek-api"

    def test_cheapest_empty_class_raises(self) -> None:
        m = _matrix()
        _seed_chat(m)
        with pytest.raises(AiRouteError):
            m.cheapest(ServiceClass.ASR)
        with pytest.raises(AiRouteError):
            m.fastest(ServiceClass.MCP)

    def test_cheapest_tiebreak_by_service_id(self) -> None:
        m = _matrix()
        m.register_service("b-svc", ServiceClass.API, ServiceLevel.L2, _API)
        m.register_service("a-svc", ServiceClass.API, ServiceLevel.L2, _API)
        assert m.cheapest(ServiceClass.API).service_id == "a-svc"  # 同价按 id 确定性
