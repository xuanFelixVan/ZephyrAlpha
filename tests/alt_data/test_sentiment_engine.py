# [BLUEPRINT] MOD-ALT-004 | docs/03_modules/_domain_alt_data/sentiment_engine/blueprint.md | §test
# [MODULE] tests.alt_data.test_sentiment_engine
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.alt_data.sentiment_engine
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_sentiment_engine.py
# [A_test] module_id: MOD-ALT-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-ALT-004 单元测试: SentimentEngine — 统一情绪引擎。

覆盖: 复合分（三路加权/缺路归一/权重全零等权兜底/clip）、历史分位（PIT 严格
< 当日/window_days 窗外剔除/≤占比）、状态机（ICE<0.10/OVERHEAT>0.90/恰等
不命中/样本不足 INSUFFICIENT_HISTORY）、单条 Fail-Closed、配置 Fail-Closed、
history_provider 异常不阻断、确定性排序、frozen。
"""

from __future__ import annotations

import datetime
from dataclasses import FrozenInstanceError

import pytest

from zephyr.alt_data.sentiment_engine import (
    HistoryPoint,
    InvalidSentimentConfigError,
    InvalidSentimentInputError,
    SentimentDaily,
    SentimentEngine,
    SentimentEngineConfig,
    SentimentInput,
    SentimentState,
)

D0 = datetime.date(2026, 8, 25)


def _d(days_before: int) -> datetime.date:
    return D0 - datetime.timedelta(days=days_before)


def _row(**kw) -> SentimentInput:
    kw.setdefault("trade_date", D0)
    kw.setdefault("symbol", "600000")
    kw.setdefault("price_volume_score", 0.5)
    return SentimentInput(**kw)


def _history(values: list[float], step_days: int = 1) -> list[HistoryPoint]:
    return [HistoryPoint(trade_date=_d((i + 1) * step_days), composite=v) for i, v in enumerate(values)]


@pytest.fixture
def engine() -> SentimentEngine:
    return SentimentEngine()


class TestComposite:
    def test_three_way_weighted(self, engine):
        r = engine.evaluate_one(_row(price_volume_score=1.0, social_score=0.0, news_score=-1.0))
        # 0.4*1 + 0.3*0 + 0.3*(-1) = 0.1
        assert r.composite == pytest.approx(0.1)
        assert r.components_present == 3

    def test_missing_leg_renormalized(self, engine):
        r = engine.evaluate_one(_row(price_volume_score=0.6, social_score=None, news_score=None))
        assert r.composite == pytest.approx(0.6)
        assert r.components_present == 1

    def test_two_legs_renormalized(self, engine):
        r = engine.evaluate_one(_row(price_volume_score=1.0, social_score=-1.0, news_score=None))
        # 权重 0.4/0.3 归一：(0.4*1 + 0.3*(-1))/0.7
        assert r.composite == pytest.approx(0.1 / 0.7)
        assert r.components_present == 2

    def test_zero_weights_fallback_equal(self):
        eng = SentimentEngine(SentimentEngineConfig(weight_price_volume=0.0, weight_social=0.0, weight_news=0.5))
        r = eng.evaluate_one(_row(price_volume_score=1.0, social_score=None, news_score=None))
        # 在场路仅价量（其权重 0 → w_sum=0）→ 等权兜底=自身
        assert r.composite == pytest.approx(1.0)


class TestPercentileAndState:
    def test_ice_below_10pct(self):
        hist = _history([0.5] * 99 + [-0.9])
        eng = SentimentEngine(history_provider=lambda s, d: hist)
        r = eng.evaluate_one(_row(price_volume_score=-0.85))
        # -0.85 ≥ 仅 -0.9 一个历史值 → 1/100=0.01 < 0.10
        assert r.percentile == pytest.approx(0.01)
        assert r.state is SentimentState.ICE

    def test_overheat_above_90pct(self):
        hist = _history([0.0] * 99 + [1.0])
        eng = SentimentEngine(history_provider=lambda s, d: hist)
        r = eng.evaluate_one(_row(price_volume_score=0.9))
        # 0.9 ≥ 99 个 0.0 → 99/100=0.99 > 0.90
        assert r.percentile == pytest.approx(0.99)
        assert r.state is SentimentState.OVERHEAT

    def test_normal_mid_percentile(self):
        hist = _history([float(x) / 100 for x in range(-50, 50)])
        eng = SentimentEngine(history_provider=lambda s, d: hist)
        r = eng.evaluate_one(_row(price_volume_score=0.0))
        assert r.state is SentimentState.NORMAL

    def test_exact_threshold_not_triggered(self):
        # 恰等 0.10 不命中 ICE（严格小于）；恰等 0.90 不命中 OVERHEAT（严格大于）
        eng = SentimentEngine(history_provider=lambda s, d: _history([0.0] * 10 + [1.0] * 90))
        r = eng.evaluate_one(_row(price_volume_score=0.0))
        assert r.percentile == pytest.approx(0.10)
        assert r.state is SentimentState.NORMAL
        eng2 = SentimentEngine(history_provider=lambda s, d: _history([0.0] * 90 + [1.0] * 10))
        r2 = eng2.evaluate_one(_row(price_volume_score=0.0))
        assert r2.percentile == pytest.approx(0.90)
        assert r2.state is SentimentState.NORMAL

    def test_insufficient_history(self, engine):
        r = engine.evaluate_one(_row())  # 无 provider → 空历史
        assert r.state is SentimentState.INSUFFICIENT_HISTORY
        assert r.percentile is None

    def test_min_history_boundary(self):
        hist = _history([0.0] * 20)
        eng = SentimentEngine(history_provider=lambda s, d: hist)
        assert eng.evaluate_one(_row()).state is not SentimentState.INSUFFICIENT_HISTORY
        eng19 = SentimentEngine(history_provider=lambda s, d: hist[:19])
        assert eng19.evaluate_one(_row()).state is SentimentState.INSUFFICIENT_HISTORY


class TestPitWindow:
    def test_future_and_same_day_excluded(self):
        hist = [
            HistoryPoint(trade_date=D0, composite=-1.0),  # 当日 → 剔除
            HistoryPoint(trade_date=_d(-1), composite=-1.0),  # 未来 → 剔除
        ] + _history([0.0] * 20)
        eng = SentimentEngine(history_provider=lambda s, d: hist)
        r = eng.evaluate_one(_row(price_volume_score=1.0))
        assert r.percentile == pytest.approx(1.0)  # 若 -1.0 混入则 <1.0

    def test_outside_window_excluded(self):
        hist = [HistoryPoint(trade_date=_d(300), composite=-1.0)] + _history([0.0] * 20)
        eng = SentimentEngine(history_provider=lambda s, d: hist)  # window_days=252
        r = eng.evaluate_one(_row(price_volume_score=1.0))
        assert r.percentile == pytest.approx(1.0)


class TestFailClosed:
    def test_score_out_of_range(self):
        with pytest.raises(InvalidSentimentInputError):
            _row(price_volume_score=1.5)
        with pytest.raises(InvalidSentimentInputError):
            _row(price_volume_score=float("nan"))

    def test_all_legs_none(self):
        with pytest.raises(InvalidSentimentInputError):
            SentimentInput(trade_date=D0, symbol="600000")

    def test_bad_symbol(self):
        with pytest.raises(InvalidSentimentInputError):
            _row(symbol="  ")

    def test_bad_date(self):
        with pytest.raises(InvalidSentimentInputError):
            SentimentInput(trade_date="2026-08-25", symbol="600000", price_volume_score=0.5)  # type: ignore[arg-type]
        with pytest.raises(InvalidSentimentInputError):
            SentimentInput(trade_date=datetime.datetime(2026, 8, 25, 9, 30), symbol="600000", price_volume_score=0.5)

    def test_evaluate_one_wrong_type(self, engine):
        with pytest.raises(InvalidSentimentInputError):
            engine.evaluate_one({"symbol": "X"})  # type: ignore[arg-type]

    def test_bad_config(self):
        with pytest.raises(InvalidSentimentConfigError):
            SentimentEngineConfig(weight_social=-0.1)
        with pytest.raises(InvalidSentimentConfigError):
            SentimentEngineConfig(weight_price_volume=0, weight_social=0, weight_news=0)
        with pytest.raises(InvalidSentimentConfigError):
            SentimentEngineConfig(window_days=0)
        with pytest.raises(InvalidSentimentConfigError):
            SentimentEngineConfig(min_history=-1)
        with pytest.raises(InvalidSentimentConfigError):
            SentimentEngineConfig(ice_pct=0.9, overheat_pct=0.1)
        with pytest.raises(InvalidSentimentConfigError):
            SentimentEngineConfig(ice_pct=1.5)

    def test_bad_constructor_args(self):
        with pytest.raises(InvalidSentimentConfigError):
            SentimentEngine(config="x")  # type: ignore[arg-type]
        with pytest.raises(InvalidSentimentConfigError):
            SentimentEngine(history_provider="x")  # type: ignore[arg-type]

    def test_history_provider_exception_rejected_not_block(self):
        def _boom(s, d):
            raise RuntimeError("history down")

        eng = SentimentEngine(history_provider=_boom)
        rep = eng.evaluate([_row(), _row(symbol="000001")])
        assert rep.accepted == 0
        assert rep.rejected == 2
        assert len(rep.errors) == 2


class TestBatch:
    def test_mixed_rows_rejected_ledger(self, engine):
        rep = engine.evaluate(
            [
                _row(symbol="600000"),
                {"trade_date": D0, "symbol": "000001", "price_volume_score": 9.9},  # 越界→拒
                _row(symbol="000002"),
            ]
        )
        assert rep.rows_in == 3
        assert rep.accepted == 2
        assert rep.rejected == 1
        assert rep.errors[0][0] == 1

    def test_deterministic_sort(self, engine):
        rep = engine.evaluate([_row(symbol="B", trade_date=_d(1)), _row(symbol="A", trade_date=_d(1))])
        assert [r.symbol for r in rep.records] == ["A", "B"]

    def test_counts(self):
        hist = _history([0.0] * 100)
        eng = SentimentEngine(history_provider=lambda s, d: hist)
        rep = eng.evaluate(
            [
                _row(symbol="A", price_volume_score=-1.0),  # ICE
                _row(symbol="B", price_volume_score=1.0),  # OVERHEAT(1.0≤全部0.0? 0/100=0→ICE)
            ]
        )
        # A: composite=-1 → 0/100=0.0 <0.10 ICE；B: composite=1 → 100/100=1.0 >0.90 OVERHEAT
        assert rep.ice_count == 1
        assert rep.overheat_count == 1


class TestFrozen:
    def test_frozen_dataclasses(self):
        row = _row()
        with pytest.raises(FrozenInstanceError):
            row.symbol = "X"  # type: ignore[misc]
        rec = SentimentDaily(
            trade_date=D0,
            symbol="600000",
            composite=0.0,
            percentile=None,
            state=SentimentState.NORMAL,
            components_present=1,
        )
        with pytest.raises(FrozenInstanceError):
            rec.composite = 1.0  # type: ignore[misc]
