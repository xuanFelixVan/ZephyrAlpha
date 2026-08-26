# [BLUEPRINT] MOD-ALT-014 | docs/03_modules/_domain_alt_data/geopolitical_risk_analyzer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ALT-014 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_geopolitical_risk_analyzer
# [TESTS] src/zephyr/alt_data/geopolitical_risk_analyzer.py
"""MOD-ALT-014 单元测试：geopolitical_risk_analyzer 地缘政治风险分析器。

蓝图验收（B5-07092/CAND-TESTA-025，B5 D-ALT-DATA-12）：
事件采集注入 + 风险评分（国家/商品传导矩阵）+ 制裁名单比对命中标记 +
风险事件入事件总线回调（仅达阈值或制裁命中者）仅作信号输入。
事件源/总线/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.alt_data.geopolitical_risk_analyzer",
    reason="geopolitical_risk_analyzer not importable",
)

from zephyr.alt_data.geopolitical_risk_analyzer import (  # noqa: E402
    GeoEvent,
    GeopoliticalRiskAnalyzer,
    GeopoliticalRiskError,
    RiskEvent,
    RiskLevel,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_MATRIX = {
    "IR": {"crude_oil": 0.9, "gold": 0.4},
    "RU": {"natural_gas": 0.8, "wheat": 0.6},
}


def _event(
    event_id: str = "ev-1",
    country: str = "IR",
    severity: float = 0.5,
    commodities: tuple = ("crude_oil",),
    entities: tuple = (),
) -> GeoEvent:
    return GeoEvent(
        event_id=event_id,
        country=country,
        headline="某地局势升级",
        severity=severity,
        commodities=commodities,
        entities=entities,
        occurred_at=_T0,
    )


def _analyzer(
    events: tuple = (),
    bus: list | None = None,
    sanctions: tuple = (),
    **kwargs,
) -> GeopoliticalRiskAnalyzer:
    return GeopoliticalRiskAnalyzer(
        event_source=lambda: list(events),
        transmission_matrix=_MATRIX,
        sanction_list=sanctions,
        clock=lambda: _T0,
        event_bus=(lambda r: bus.append(r)) if bus is not None else None,
        **kwargs,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_missing_event_source_raises(self) -> None:
        with pytest.raises(GeopoliticalRiskError):
            GeopoliticalRiskAnalyzer(event_source=None, transmission_matrix={})

    def test_non_callable_event_source_raises(self) -> None:
        with pytest.raises(GeopoliticalRiskError):
            GeopoliticalRiskAnalyzer(event_source="not-callable", transmission_matrix={})

    def test_matrix_coefficient_out_of_range_raises(self) -> None:
        with pytest.raises(GeopoliticalRiskError):
            GeopoliticalRiskAnalyzer(
                event_source=lambda: [],
                transmission_matrix={"IR": {"crude_oil": 1.5}},
            )

    def test_matrix_blank_keys_raise(self) -> None:
        with pytest.raises(GeopoliticalRiskError):
            GeopoliticalRiskAnalyzer(
                event_source=lambda: [], transmission_matrix={" ": {"oil": 0.5}}
            )
        with pytest.raises(GeopoliticalRiskError):
            GeopoliticalRiskAnalyzer(
                event_source=lambda: [], transmission_matrix={"IR": {"": 0.5}}
            )

    def test_thresholds_unordered_raises(self) -> None:
        with pytest.raises(GeopoliticalRiskError):
            _analyzer(publish_threshold=0.9, high_threshold=0.3)


# ──────────────────────────────────────────────────────────────────────────────
# 事件校验
# ──────────────────────────────────────────────────────────────────────────────


class TestEventValidation:
    def test_non_geoevent_raises(self) -> None:
        az = _analyzer()
        with pytest.raises(GeopoliticalRiskError):
            az.assess("not-an-event")  # type: ignore[arg-type]

    def test_blank_event_id_raises(self) -> None:
        az = _analyzer()
        with pytest.raises(GeopoliticalRiskError):
            az.assess(_event(event_id=" "))

    def test_blank_country_raises(self) -> None:
        az = _analyzer()
        with pytest.raises(GeopoliticalRiskError):
            az.assess(_event(country=""))

    def test_severity_out_of_range_raises(self) -> None:
        az = _analyzer()
        with pytest.raises(GeopoliticalRiskError):
            az.assess(_event(severity=1.2))
        with pytest.raises(GeopoliticalRiskError):
            az.assess(_event(severity=-0.1))


# ──────────────────────────────────────────────────────────────────────────────
# 风险评分（传导矩阵）
# ──────────────────────────────────────────────────────────────────────────────


class TestScoring:
    def test_score_uses_max_transmission_coefficient(self) -> None:
        az = _analyzer()
        ev = _event(severity=0.5, commodities=("crude_oil", "gold"))  # max(0.9,0.4)
        risk = az.assess(ev)
        assert risk.risk_score == pytest.approx(0.45)

    def test_score_defaults_to_severity_without_mapping(self) -> None:
        az = _analyzer()
        risk = az.assess(_event(country="XX", severity=0.6))  # 无传导映射
        assert risk.risk_score == pytest.approx(0.6)

    def test_score_unknown_commodity_ignored(self) -> None:
        az = _analyzer()
        ev = _event(severity=0.5, commodities=("lithium",))  # 国家有映射但商品无
        risk = az.assess(ev)
        assert risk.risk_score == pytest.approx(0.5)

    def test_score_clamped_to_unit(self) -> None:
        az = _analyzer()
        risk = az.assess(_event(severity=1.0, commodities=("crude_oil",)))
        assert 0.0 <= risk.risk_score <= 1.0

    def test_risk_level_bands(self) -> None:
        az = _analyzer()
        high = az.assess(_event(event_id="h", severity=1.0, commodities=("crude_oil",)))   # 0.9
        mid = az.assess(_event(event_id="m", severity=0.5, commodities=("crude_oil",)))   # 0.45
        low = az.assess(_event(event_id="l", severity=0.2, commodities=("gold",)))        # 0.08
        assert high.risk_level is RiskLevel.HIGH
        assert mid.risk_level is RiskLevel.MEDIUM
        assert low.risk_level is RiskLevel.LOW

    def test_assess_idempotent_by_event_id(self) -> None:
        az = _analyzer()
        r1 = az.assess(_event())
        r2 = az.assess(_event())  # 同 event_id
        assert r1 is r2


# ──────────────────────────────────────────────────────────────────────────────
# 制裁名单比对
# ──────────────────────────────────────────────────────────────────────────────


class TestSanction:
    def test_sanction_hit_marked(self) -> None:
        az = _analyzer(sanctions=("ENTITY_A", "ENTITY_B"))
        risk = az.assess(_event(entities=("ENTITY_A", "ENTITY_C")))
        assert risk.sanction_hit is True
        assert risk.hit_entities == ("ENTITY_A",)

    def test_no_hit_when_entities_clean(self) -> None:
        az = _analyzer(sanctions=("ENTITY_A",))
        risk = az.assess(_event(entities=("ENTITY_Z",)))
        assert risk.sanction_hit is False
        assert risk.hit_entities == ()

    def test_low_score_sanction_hit_still_published(self) -> None:
        bus: list[RiskEvent] = []
        az = _analyzer(
            events=(_event(severity=0.05, entities=("BAD_ONE",)),),
            bus=bus,
            sanctions=("BAD_ONE",),
        )
        published = az.run()
        assert len(published) == 1  # 制裁命中者低分也入总线
        assert bus == published


# ──────────────────────────────────────────────────────────────────────────────
# 采集 + 总线发布
# ──────────────────────────────────────────────────────────────────────────────


class TestRun:
    def test_run_publishes_above_threshold(self) -> None:
        bus: list[RiskEvent] = []
        az = _analyzer(
            events=(
                _event(event_id="hi", severity=0.9),
                _event(event_id="lo", severity=0.05),
            ),
            bus=bus,
        )
        published = az.run()
        assert [r.event_id for r in published] == ["hi"]
        assert [r.event_id for r in bus] == ["hi"]

    def test_run_without_bus_still_returns(self) -> None:
        az = _analyzer(events=(_event(severity=0.9),))
        published = az.run()
        assert len(published) == 1

    def test_run_dedupes_repeated_event_id(self) -> None:
        bus: list[RiskEvent] = []
        az = _analyzer(events=(_event(), _event()), bus=bus)  # 同 id 重复
        published = az.run()
        assert len(published) == 2  # 批次内两条均评估，但产物同一对象
        assert published[0] is published[1]
        assert len(az.history()) == 1  # 留痕去重

    def test_event_source_exception_fail_closed(self) -> None:
        def boom():
            raise RuntimeError("rss down")

        az = GeopoliticalRiskAnalyzer(
            event_source=boom, transmission_matrix=_MATRIX, clock=lambda: _T0
        )
        with pytest.raises(GeopoliticalRiskError):
            az.run()

    def test_bus_exception_not_blocking(self) -> None:
        def bad_bus(_r: RiskEvent) -> None:
            raise RuntimeError("bus down")

        az = GeopoliticalRiskAnalyzer(
            event_source=lambda: [_event(severity=0.9)],
            transmission_matrix=_MATRIX,
            clock=lambda: _T0,
            event_bus=bad_bus,
        )
        published = az.run()  # 总线异常不阻断
        assert len(published) == 1

    def test_history_sorted(self) -> None:
        t1 = _T0 - datetime.timedelta(hours=1)
        az = _analyzer()
        az.assess(GeoEvent(
            event_id="b", country="IR", headline="h", severity=0.5,
            commodities=(), entities=(), occurred_at=_T0,
        ))
        az.assess(GeoEvent(
            event_id="a", country="RU", headline="h", severity=0.5,
            commodities=(), entities=(), occurred_at=t1,
        ))
        assert [r.event_id for r in az.history()] == ["a", "b"]

    def test_determinism_same_input_same_output(self) -> None:
        def run() -> tuple:
            az = _analyzer(events=(_event(severity=0.6),))
            published = az.run()
            r = published[0]
            return (r.event_id, r.risk_score, r.risk_level, r.sanction_hit)

        assert run() == run()
