# [BLUEPRINT] MOD-SIG-123 | docs/03_modules/_domain_signal/event_conditional_density/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-123 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_event_conditional_density
# [TESTS] src/zephyr/signal_ashare/event_conditional_density.py
"""MOD-SIG-123 单元测试：event_conditional_density 事件驱动条件分布预测。

蓝图验收（B10-01412/CAND-TESTB-043，A1 B3）：
事件类型分桶收益分布直方图+分位数 + 盘后批处理≤100只护栏 +
事件源注入NLP分类回调（未注入Fail-Closed）+ 分布计数守恒校验。
NLP分类/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
import math

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.event_conditional_density",
    reason="event_conditional_density not importable",
)

from zephyr.signal_ashare.event_conditional_density import (  # noqa: E402
    EventCondDensityConfig,
    EventCondDensityError,
    EventConditionalDensity,
    EventDensity,
    EventType,
    HistogramBin,
)

_T0 = datetime.datetime(2026, 8, 26, 15, 30, 0)  # 盘后时刻

_CLASSIFY_MAP = {
    "公司发布业绩预增公告": EventType.EARNINGS,
    "发改委出台产业扶持政策": "policy",  # 回调返回 str，须收口为枚举
}


def _engine(
    classifier=None,
    config: EventCondDensityConfig | None = None,
) -> EventConditionalDensity:
    return EventConditionalDensity(
        clock=lambda: _T0,
        event_classifier=classifier if classifier is not None else _CLASSIFY_MAP.get,
        config=config,
    )


def _seed(
    engine: EventConditionalDensity,
    event_type: EventType = EventType.EARNINGS,
    values: tuple[float, ...] = (-0.05, -0.02, 0.0, 0.01, 0.03, 0.08),
) -> None:
    engine.add_samples(event_type, values)


# ──────────────────────────────────────────────────────────────────────────────
# 事件源注入（NLP 分类回调）
# ──────────────────────────────────────────────────────────────────────────────


class TestClassifyEvent:
    def test_classify_ok_and_str_coerced(self) -> None:
        engine = _engine()
        assert engine.classify_event("公司发布业绩预增公告") is EventType.EARNINGS
        assert engine.classify_event("发改委出台产业扶持政策") is EventType.POLICY

    def test_classify_unknown_type_raises(self) -> None:
        engine = _engine(classifier=lambda text: "alien_event")
        with pytest.raises(EventCondDensityError):
            engine.classify_event("某未知类型事件")

    def test_classifier_not_injected_fail_closed(self) -> None:
        engine = EventConditionalDensity(clock=lambda: _T0, event_classifier=None)
        with pytest.raises(EventCondDensityError):
            engine.classify_event("公司发布业绩预增公告")

    def test_classify_empty_text_raises(self) -> None:
        engine = _engine()
        with pytest.raises(EventCondDensityError):
            engine.classify_event("")
        with pytest.raises(EventCondDensityError):
            engine.classify_event("   ")

    def test_classifier_exception_wrapped(self) -> None:
        def _boom(text: str) -> EventType:
            raise RuntimeError("nlp model down")

        engine = _engine(classifier=_boom)
        with pytest.raises(EventCondDensityError):
            engine.classify_event("公司发布业绩预增公告")


# ──────────────────────────────────────────────────────────────────────────────
# 样本登记（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestSampleIngest:
    def test_add_sample_and_bucket_size(self) -> None:
        engine = _engine()
        engine.add_sample("earnings", 0.01)  # str 类型收口
        _seed(engine, EventType.POLICY, (0.01, 0.02))
        assert engine.bucket_size(EventType.EARNINGS) == 1
        assert engine.bucket_size(EventType.POLICY) == 2

    def test_add_sample_unknown_type_raises(self) -> None:
        engine = _engine()
        with pytest.raises(EventCondDensityError):
            engine.add_sample("alien_event", 0.01)

    def test_add_sample_invalid_return_raises(self) -> None:
        engine = _engine()
        for bad in (math.nan, math.inf, -math.inf, "0.1", True):
            with pytest.raises(EventCondDensityError):
                engine.add_sample(EventType.EARNINGS, bad)

    def test_add_samples_empty_raises(self) -> None:
        engine = _engine()
        with pytest.raises(EventCondDensityError):
            engine.add_samples(EventType.EARNINGS, [])


# ──────────────────────────────────────────────────────────────────────────────
# 条件分布（直方图 + 分位数 + 降级 + 守恒校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestDensity:
    def test_histogram_counts_and_last_bin_right_closed(self) -> None:
        engine = _engine(config=EventCondDensityConfig(bin_count=4, min_samples=1))
        _seed(engine, values=(0.0, 1.0, 2.0, 3.0))
        d = engine.density(EventType.EARNINGS)
        assert [b.count for b in d.histogram] == [1, 1, 1, 1]
        assert d.histogram[-1].upper == pytest.approx(3.0)  # 最大值末桶右闭
        assert sum(b.count for b in d.histogram) == d.n_samples == 4

    def test_quantiles_linear_interpolation(self) -> None:
        engine = _engine(config=EventCondDensityConfig(bin_count=2, min_samples=1, quantiles=(0.5,)))
        engine.add_samples(EventType.EARNINGS, [float(i) for i in range(1, 101)])
        d = engine.density(EventType.EARNINGS)
        assert d.quantiles[0.5] == pytest.approx(50.5)

    def test_degraded_fallback_pooled(self) -> None:
        engine = _engine()  # min_samples=5
        _seed(engine, EventType.EARNINGS, (0.01, 0.02))  # 2 < 5
        _seed(engine, EventType.POLICY, (0.0, 0.01, 0.02, 0.03, 0.04))
        d = engine.density(EventType.EARNINGS)
        assert d.degraded is True
        assert d.n_samples == 7  # 回退全事件池

    def test_not_degraded_when_bucket_enough(self) -> None:
        engine = _engine()
        _seed(engine, EventType.POLICY, (0.0, 0.01, 0.02, 0.03, 0.04))
        d = engine.density(EventType.POLICY)
        assert d.degraded is False
        assert d.n_samples == 5

    def test_empty_pool_raises(self) -> None:
        engine = _engine()
        with pytest.raises(EventCondDensityError):
            engine.density(EventType.EARNINGS)

    def test_constant_series_single_bin_conserved(self) -> None:
        engine = _engine(config=EventCondDensityConfig(bin_count=4, min_samples=1))
        _seed(engine, values=(0.02, 0.02, 0.02, 0.02, 0.02, 0.02))
        d = engine.density(EventType.EARNINGS)
        assert d.histogram[0].count == 6
        assert all(b.count == 0 for b in d.histogram[1:])
        assert sum(b.count for b in d.histogram) == 6
        assert d.quantiles[0.5] == pytest.approx(0.02)

    def test_validate_conservation_tampered_raises(self) -> None:
        tampered = EventDensity(
            event_type=EventType.EARNINGS,
            n_samples=3,
            histogram=(HistogramBin(lower=0.0, upper=1.0, count=1),),
        )
        with pytest.raises(EventCondDensityError):
            EventConditionalDensity.validate_conservation(tampered)

    def test_determinism_same_input_same_output(self) -> None:
        e1, e2 = _engine(), _engine()
        for e in (e1, e2):
            _seed(e)
            _seed(e, EventType.POLICY, (0.0, 0.01, 0.02, 0.03, 0.04))
        assert e1.density(EventType.EARNINGS) == e2.density(EventType.EARNINGS)
        assert e1.density(EventType.POLICY) == e2.density(EventType.POLICY)


# ──────────────────────────────────────────────────────────────────────────────
# 配置校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_invalid_config_raises(self) -> None:
        with pytest.raises(EventCondDensityError):
            EventCondDensityConfig(bin_count=0)
        with pytest.raises(EventCondDensityError):
            EventCondDensityConfig(min_samples=0)
        with pytest.raises(EventCondDensityError):
            EventCondDensityConfig(max_batch_symbols=0)
        with pytest.raises(EventCondDensityError):
            EventCondDensityConfig(quantiles=())
        with pytest.raises(EventCondDensityError):
            EventCondDensityConfig(quantiles=(0.5, 0.5))  # 非严格递增
        with pytest.raises(EventCondDensityError):
            EventCondDensityConfig(quantiles=(0.0, 0.5))  # 越界开区间


# ──────────────────────────────────────────────────────────────────────────────
# 盘后批处理（≤100 只护栏）
# ──────────────────────────────────────────────────────────────────────────────


class TestAfterCloseBatch:
    def test_batch_ok(self) -> None:
        engine = _engine()
        report = engine.run_after_close_batch(
            {
                "600000": (EventType.EARNINGS, (-0.05, -0.02, 0.0, 0.01, 0.03, 0.08)),
                "000001": ("policy", (0.0, 0.01, 0.02, 0.03, 0.04, 0.05)),
            }
        )
        assert report.n_symbols == 2
        assert report.generated_at == _T0  # 注入时钟
        assert set(report.densities) == {"600000", "000001"}
        d = report.densities["600000"]
        assert d.event_type is EventType.EARNINGS
        assert d.degraded is False
        assert sum(b.count for b in d.histogram) == d.n_samples == 6

    def test_batch_guardrail_over_100_raises(self) -> None:
        engine = _engine()
        samples = {f"{i:06d}": (EventType.POLICY, (0.01,)) for i in range(101)}
        with pytest.raises(EventCondDensityError):
            engine.run_after_close_batch(samples)

    def test_batch_exactly_100_ok(self) -> None:
        engine = _engine()
        samples = {f"{i:06d}": (EventType.POLICY, (0.01, 0.02, 0.03, 0.04, 0.05)) for i in range(100)}
        report = engine.run_after_close_batch(samples)
        assert report.n_symbols == 100

    def test_batch_invalid_input_raises(self) -> None:
        engine = _engine()
        with pytest.raises(EventCondDensityError):
            engine.run_after_close_batch({})  # 空批次
        with pytest.raises(EventCondDensityError):
            engine.run_after_close_batch({"  ": (EventType.POLICY, (0.01,))})  # 空 symbol
        with pytest.raises(EventCondDensityError):
            engine.run_after_close_batch({"600000": (EventType.POLICY, [])})  # 空样本

    def test_batch_unknown_event_type_raises(self) -> None:
        engine = _engine()
        with pytest.raises(EventCondDensityError):
            engine.run_after_close_batch({"600000": ("alien_event", (0.01,))})

    def test_batch_degraded_mark_for_thin_symbol(self) -> None:
        engine = _engine()  # min_samples=5
        report = engine.run_after_close_batch(
            {
                "600000": (EventType.EARNINGS, (0.01, 0.02)),  # 2 < 5 → 回退批内池
                "000001": (EventType.POLICY, (0.0, 0.01, 0.02, 0.03, 0.04, 0.05)),
            }
        )
        thin = report.densities["600000"]
        assert thin.degraded is True
        assert thin.n_samples == 8  # 批内全池 2+6
        assert report.densities["000001"].degraded is False
