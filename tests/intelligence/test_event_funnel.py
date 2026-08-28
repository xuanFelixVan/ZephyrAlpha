# [MODULE] tests.intelligence.test_event_funnel
# [DOMAIN] D_INTELLIGENCE
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_event_funnel.py -q
"""test_event_funnel.py — 事件驱动选股漏斗单元测试（26 号 §2.5 / BM-SEL-19）。

覆盖：
  1. 候选池生成（精筛 ∪ 事件触发合并去重、精筛序优先、映射装配）
  2. 正常过滤（无事件中性保留 / 利多保留评分 / 利空剔除 / 排序降序）
  3. 三重门控（极端反应 / 条件PDF>15% / 传导链>0.7）与边界恰好值
  4. 噪声带（|score|<0.2 保留 score=0 / 边界 ±0.2）
  5. 降级链（skipped 直通 / degraded 仅剔除利空 / None 未就绪不判定）
  6. 容量截断与异常（capacity_target≤0 抛 / 契约违反单标的剔除不整批抛）
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.event_funnel import (
    CONDUCTION_RISK_MAX,
    EventFunnelCandidate,
    EventFunnelConfig,
    EventFunnelError,
    build_candidate_pool,
    run_event_funnel,
)
from zephyr.intelligence.event_score import EventRecord, EventScoreError


def _event(
    symbol: str,
    class_: str = "surprise",
    direction: float = 1.0,
    sentiment: float = 1.0,
    day0_reaction: float = 0.0,
) -> EventRecord:
    return EventRecord(
        symbol=symbol,
        class_=class_,
        surprise_direction=direction,
        sentiment_score=sentiment,
        day0_reaction=day0_reaction,
    )


def _cand(
    symbol: str,
    event: EventRecord | None = None,
    prob_shift: float | None = None,
    conduction: float | None = None,
) -> EventFunnelCandidate:
    return EventFunnelCandidate(
        symbol=symbol,
        event=event,
        conditional_prob_shift=prob_shift,
        conduction_risk=conduction,
    )


# ============ 1. 候选池生成 ============


class TestBuildCandidatePool:
    def test_prescreened_without_event_kept_neutral(self):
        pool = build_candidate_pool(["600519", "000001"], {})
        assert [c.symbol for c in pool] == ["600519", "000001"]
        assert all(c.event is None for c in pool)

    def test_event_triggered_outside_prescreened_enters_pool(self):
        # 26 号 §2.5：事件触发标的即候选（非固定池）
        pool = build_candidate_pool(["600519"], {"300750": _event("300750")})
        assert [c.symbol for c in pool] == ["600519", "300750"]
        assert pool[1].event is not None

    def test_overlap_dedup_prescreened_order_first(self):
        pool = build_candidate_pool(
            ["600519", "000001"],
            {"000001": _event("000001"), "300750": _event("300750")},
        )
        assert [c.symbol for c in pool] == ["600519", "000001", "300750"]
        assert pool[1].event is not None  # 精筛内标的事件已装配

    def test_prescreened_duplicates_dedup(self):
        pool = build_candidate_pool(["600519", "600519"], {})
        assert [c.symbol for c in pool] == ["600519"]

    def test_maps_assembled(self):
        from zephyr.intelligence.event_score import EarningsFactorData

        earnings = {"600519": EarningsFactorData(consensus_eps=1.0, surprise_std=0.2, ear=0.01)}
        pool = build_candidate_pool(
            ["600519"],
            {"600519": _event("600519", class_="earnings")},
            earnings_map=earnings,
            prob_shift_map={"600519": -0.05},
            conduction_risk_map={"600519": 0.3},
        )
        c = pool[0]
        assert c.earnings is earnings["600519"]
        assert c.conditional_prob_shift == -0.05
        assert c.conduction_risk == 0.3

    def test_empty_pool(self):
        assert build_candidate_pool([], {}) == []


# ============ 2. 正常过滤与排序 ============


class TestNormalFilter:
    def test_no_event_candidate_kept_score_zero(self):
        result = run_event_funnel([_cand("600519")])
        assert result.kept == ("600519",)
        assert result.scores == {"600519": 0.0}
        assert result.excluded == {}

    def test_positive_event_kept_with_score(self):
        # surprise 1.5 × 1 × 1 × 1 × 1 = 1.5
        result = run_event_funnel([_cand("600519", _event("600519"))])
        assert result.kept == ("600519",)
        assert result.scores["600519"] == pytest.approx(1.5)

    def test_negative_event_excluded(self):
        # ma 1.2 × (-1) × 1 × 1 × 1 = -1.2 → 利空剔除（不能做空）
        result = run_event_funnel([_cand("600519", _event("600519", class_="ma", direction=-1.0))])
        assert result.kept == ()
        assert result.excluded == {"600519": "event:negative_score"}

    def test_ranking_by_score_desc(self):
        candidates = [
            _cand("A", None),  # 0.0
            _cand("B", _event("B", class_="policy", sentiment=0.5)),  # 0.8×0.5=0.4
            _cand("C", _event("C")),  # 1.5
        ]
        result = run_event_funnel(candidates)
        assert result.kept == ("C", "B", "A")
        assert result.scores["C"] == pytest.approx(1.5)
        assert result.scores["B"] == pytest.approx(0.4)
        assert result.scores["A"] == 0.0

    def test_tie_break_keeps_input_order(self):
        candidates = [_cand("A", _event("A")), _cand("B", _event("B"))]
        result = run_event_funnel(candidates)
        assert result.kept == ("A", "B")  # 同分 1.5 保持输入序


# ============ 3. 三重门控与边界 ============


class TestTripleGates:
    def test_extreme_reaction_excluded(self):
        # 利多评分但 |day0_reaction|=5% >3% → PEAD Inversion 不进入买入候选
        result = run_event_funnel([_cand("600519", _event("600519", day0_reaction=0.05))])
        assert result.excluded == {"600519": "event:extreme_reaction"}

    def test_extreme_reaction_negative_side_excluded(self):
        result = run_event_funnel([_cand("600519", _event("600519", day0_reaction=-0.04))])
        assert result.excluded == {"600519": "event:extreme_reaction"}

    def test_extreme_reaction_boundary_exactly_3pct_kept(self):
        result = run_event_funnel([_cand("600519", _event("600519", day0_reaction=0.03))])
        assert result.kept == ("600519",)

    def test_prob_shift_down_15pct_excluded(self):
        result = run_event_funnel([_cand("600519", _event("600519"), prob_shift=-0.20)])
        assert result.excluded == {"600519": "event:prob_shift_down"}

    def test_prob_shift_boundary_exactly_minus15pct_kept(self):
        result = run_event_funnel([_cand("600519", _event("600519"), prob_shift=-0.15)])
        assert result.kept == ("600519",)

    def test_prob_shift_none_not_judged(self):
        result = run_event_funnel([_cand("600519", _event("600519"), prob_shift=None)])
        assert result.kept == ("600519",)

    def test_conduction_risk_excluded(self):
        result = run_event_funnel([_cand("600519", _event("600519"), conduction=0.8)])
        assert result.excluded == {"600519": "event:conduction_risk"}

    def test_conduction_risk_boundary_exactly_max_kept(self):
        result = run_event_funnel([_cand("600519", _event("600519"), conduction=CONDUCTION_RISK_MAX)])
        assert result.kept == ("600519",)

    def test_conduction_risk_none_not_judged(self):
        result = run_event_funnel([_cand("600519", _event("600519"), conduction=None)])
        assert result.kept == ("600519",)

    def test_no_event_candidate_skips_event_gates(self):
        # 无事件标的即便挂了极端 PDF/传导值也先过评分中性路径；
        # PDF/传导门控与事件有无无关（字段维度剔除）
        result = run_event_funnel([_cand("600519", None, prob_shift=-0.20, conduction=0.9)])
        assert result.excluded.get("600519") == "event:prob_shift_down"


# ============ 4. 噪声带 ============


class TestNoiseBand:
    def test_noise_kept_score_zero(self):
        # policy 0.8 × 1 × 0.2 × 1 × 1 = 0.16 <0.2 → 保留但不加权
        result = run_event_funnel([_cand("600519", _event("600519", class_="policy", sentiment=0.2))])
        assert result.kept == ("600519",)
        assert result.scores["600519"] == 0.0

    def test_boundary_exactly_plus_noise_threshold_kept_with_score(self):
        # 恰好 0.2 非噪声：policy 0.8 × 1 × 0.25 = 0.2
        result = run_event_funnel([_cand("600519", _event("600519", class_="policy", sentiment=0.25))])
        assert result.kept == ("600519",)
        assert result.scores["600519"] == pytest.approx(0.2)

    def test_boundary_exactly_minus_noise_threshold_excluded(self):
        # 恰好 -0.2 利空剔除：policy 0.8 × (-1) × 0.25 = -0.2
        result = run_event_funnel(
            [_cand("600519", _event("600519", class_="policy", direction=-1.0, sentiment=0.25))]
        )
        assert result.excluded == {"600519": "event:negative_score"}


# ============ 5. 降级链 ============


class TestDegradation:
    def test_skipped_when_event_source_not_ready(self):
        candidates = [
            _cand("A", _event("A")),
            _cand("B", _event("B", class_="ma", direction=-1.0)),
        ]
        result = run_event_funnel(candidates, event_source_ready=False)
        assert result.skipped is True
        assert result.kept == ("A", "B")  # 直通不筛（含利空也不剔）
        assert result.scores == {"A": 0.0, "B": 0.0}

    def test_degraded_only_negative_excluded(self):
        candidates = [
            _cand("A", _event("A", class_="ma", direction=-1.0)),  # 利空 → 剔
            _cand("B", _event("B", day0_reaction=0.05)),  # 极端反应 → 降级不判定放行
            _cand("C", _event("C"), -0.30, 0.95),  # PDF+传导 → 降级不判定放行
        ]
        result = run_event_funnel(candidates, degraded=True)
        assert result.degraded is True
        assert result.excluded == {"A": "event:negative_score"}
        assert set(result.kept) == {"B", "C"}

    def test_empty_input_empty_result(self):
        result = run_event_funnel([])
        assert result.kept == ()
        assert result.excluded == {}
        assert result.skipped is False


# ============ 6. 容量截断与异常 ============


class TestCapacityAndErrors:
    def test_capacity_truncation(self):
        candidates = [
            _cand(f"S{i:03d}", _event(f"S{i:03d}", sentiment=min(1.0, 0.3 + i * 0.01)))
            for i in range(40)
        ]
        result = run_event_funnel(candidates)
        assert result.truncated is True
        assert len(result.kept) == 30
        # 截断后首位是评分最高者
        scores = [result.scores[s] for s in result.kept]
        assert scores == sorted(scores, reverse=True)

    def test_capacity_custom_target(self):
        candidates = [_cand(f"S{i}", _event(f"S{i}")) for i in range(5)]
        result = run_event_funnel(candidates, config=EventFunnelConfig(capacity_target=3))
        assert len(result.kept) == 3
        assert result.truncated is True

    def test_no_truncation_within_capacity(self):
        result = run_event_funnel([_cand("A", _event("A"))])
        assert result.truncated is False

    def test_zero_capacity_target_raises(self):
        with pytest.raises(EventFunnelError) as exc_info:
            run_event_funnel([_cand("A")], config=EventFunnelConfig(capacity_target=0))
        assert exc_info.value.error_code == "ZA-IT-0023"
        assert exc_info.value.details["capacity_target"] == 0

    def test_negative_capacity_target_raises(self):
        with pytest.raises(EventFunnelError):
            run_event_funnel([], config=EventFunnelConfig(capacity_target=-1))

    def test_score_contract_violation_excluded_not_raised(self, monkeypatch):
        def _raising(event, data=None):  # noqa: ANN001, ANN202
            raise EventScoreError("contract")

        monkeypatch.setattr("zephyr.intelligence.event_funnel.compute_event_score", _raising)
        result = run_event_funnel([_cand("A", _event("A")), _cand("B")])
        assert result.excluded == {"A": "event:score_contract"}
        assert result.kept == ("B",)  # 整批不抛，其余标的正常保留
