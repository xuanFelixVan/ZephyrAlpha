# [BLUEPRINT] MOD-INF-084 | docs/03_modules/_domain_infrastructure_operations/latency_attributor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-084 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.test_latency_attributor
# [TESTS] src/zephyr/infrastructure/system_telemetry/latency_attributor.py
"""MOD-INF-084 单元测试：latency_attributor 延迟归因器。

蓝图验收（B14-04702/CAND-INFRATEL-004，A9运维架构 §8.3.11）：
注入 span 序列分段统计（stage/duration_ms）+ 各阶段占比降序与最大贡献阶段 +
慢链路样本环形缓冲（容量注入）+ 周报聚合（按阶段 P50/P95/max）+ 非法输入
Fail-Closed。纯内存确定性，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.latency_attributor",
    reason="latency_attributor not importable",
)

from zephyr.infrastructure.system_telemetry.latency_attributor import (  # noqa: E402
    LatencyAttributor,
    LatencyAttributorError,
    StageSpan,
)


def _spans(*pairs: tuple[str, float]) -> list[StageSpan]:
    return [StageSpan(stage=s, duration_ms=d) for s, d in pairs]


# ──────────────────────────────────────────────────────────────────────────────
# 归因（attribute）
# ──────────────────────────────────────────────────────────────────────────────


class TestAttribute:
    def test_attribute_ok_shares(self) -> None:
        attr = LatencyAttributor()
        report = attr.attribute("tr-1", _spans(("tick", 10.0), ("signal", 30.0)))
        assert report.trace_id == "tr-1"
        assert report.total_ms == 40.0
        assert sum(s.share for s in report.shares) == pytest.approx(1.0)
        assert report.shares[0].stage == "signal"
        assert report.shares[0].share == pytest.approx(0.75)

    def test_shares_sorted_desc(self) -> None:
        report = LatencyAttributor().attribute(
            "tr-1", _spans(("a", 10.0), ("b", 50.0), ("c", 40.0))
        )
        assert [s.stage for s in report.shares] == ["b", "c", "a"]

    def test_top_stage_is_max_contributor(self) -> None:
        report = LatencyAttributor().attribute(
            "tr-1", _spans(("tick", 5.0), ("order", 80.0), ("signal", 15.0))
        )
        assert report.top_stage == "order"

    def test_tie_break_by_stage_name(self) -> None:
        report = LatencyAttributor().attribute(
            "tr-1", _spans(("b", 10.0), ("a", 10.0))
        )
        assert [s.stage for s in report.shares] == ["a", "b"]  # 确定性决胜

    def test_empty_trace_id_raises(self) -> None:
        with pytest.raises(LatencyAttributorError):
            LatencyAttributor().attribute("", _spans(("a", 1.0)))

    def test_empty_spans_raises(self) -> None:
        with pytest.raises(LatencyAttributorError):
            LatencyAttributor().attribute("tr-1", [])

    def test_empty_stage_raises(self) -> None:
        with pytest.raises(LatencyAttributorError):
            LatencyAttributor().attribute("tr-1", _spans(("", 1.0)))

    def test_negative_duration_raises(self) -> None:
        with pytest.raises(LatencyAttributorError):
            LatencyAttributor().attribute("tr-1", _spans(("a", -1.0)))

    def test_zero_total_raises(self) -> None:
        with pytest.raises(LatencyAttributorError):
            LatencyAttributor().attribute("tr-1", _spans(("a", 0.0), ("b", 0.0)))


# ──────────────────────────────────────────────────────────────────────────────
# 慢链路样本（环形缓冲）
# ──────────────────────────────────────────────────────────────────────────────


class TestSlowSamples:
    def test_slow_sample_recorded(self) -> None:
        attr = LatencyAttributor(slow_threshold_ms=100.0)
        attr.attribute("tr-slow", _spans(("a", 80.0), ("b", 70.0)))  # total=150
        samples = attr.slow_samples()
        assert len(samples) == 1
        assert samples[0].trace_id == "tr-slow"
        assert samples[0].total_ms == 150.0
        assert samples[0].top_stage == "a"

    def test_fast_not_recorded(self) -> None:
        attr = LatencyAttributor(slow_threshold_ms=1000.0)
        attr.attribute("tr-fast", _spans(("a", 10.0)))
        assert attr.slow_samples() == ()

    def test_ring_buffer_eviction(self) -> None:
        attr = LatencyAttributor(slow_threshold_ms=100.0, capacity=2)
        attr.attribute("tr-1", _spans(("a", 150.0)))
        attr.attribute("tr-2", _spans(("a", 200.0)))
        attr.attribute("tr-3", _spans(("a", 300.0)))  # 覆盖最旧
        assert [s.trace_id for s in attr.slow_samples()] == ["tr-2", "tr-3"]

    def test_slow_samples_insertion_order(self) -> None:
        attr = LatencyAttributor(slow_threshold_ms=100.0, capacity=5)
        for i in range(3):
            attr.attribute(f"tr-{i}", _spans(("a", 150.0)))
        assert [s.trace_id for s in attr.slow_samples()] == ["tr-0", "tr-1", "tr-2"]


# ──────────────────────────────────────────────────────────────────────────────
# 周报聚合（weekly_report）
# ──────────────────────────────────────────────────────────────────────────────


class TestWeeklyReport:
    def test_weekly_empty(self) -> None:
        assert LatencyAttributor().weekly_report() == {}

    def test_weekly_single_stage_percentiles(self) -> None:
        attr = LatencyAttributor()
        for i, d in enumerate([10.0, 20.0, 30.0, 40.0]):
            attr.attribute(f"tr-{i}", _spans(("signal", d), ("tick", 1.0)))
        rep = attr.weekly_report()
        assert rep["signal"]["count"] == 4.0
        assert rep["signal"]["p50"] == 20.0   # 最近秩 ceil(0.5*4)=2
        assert rep["signal"]["p95"] == 40.0   # 最近秩 ceil(0.95*4)=4
        assert rep["signal"]["max"] == 40.0

    def test_weekly_multi_stage_sorted(self) -> None:
        attr = LatencyAttributor()
        attr.attribute("tr-1", _spans(("zeta", 5.0), ("alpha", 5.0)))
        attr.attribute("tr-2", _spans(("zeta", 7.0), ("alpha", 3.0)))
        rep = attr.weekly_report()
        assert list(rep.keys()) == ["alpha", "zeta"]
        assert rep["zeta"]["max"] == 7.0
        assert rep["alpha"]["count"] == 2.0

    def test_capacity_invalid_raises(self) -> None:
        with pytest.raises(LatencyAttributorError):
            LatencyAttributor(capacity=0)
        with pytest.raises(LatencyAttributorError):
            LatencyAttributor(capacity=-1)

    def test_threshold_invalid_raises(self) -> None:
        with pytest.raises(LatencyAttributorError):
            LatencyAttributor(slow_threshold_ms=-0.1)
