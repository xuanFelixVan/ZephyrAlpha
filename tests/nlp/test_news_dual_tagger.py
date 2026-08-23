# [BLUEPRINT] MOD-NLP-DUALTAG-001 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-21 行）
# [MODULE] tests.nlp.test_news_dual_tagger
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.nlp.news_dual_tagger
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=新闻双标签逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-NLP-DUALTAG-001_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-NLP-DUALTAG-001 新闻双标签生成器 单元测试（GAP-F-21，合成数据不触库）。

覆盖：日历规则命中（含 advance_notice=False 排除）、可预测性四态、预期差四态
（含 anchor=0/actual None → 无锚未定不出伪差）、双标签合成计数、
load_consensus_anchors PIT 最新条选取/空清单/日期非法 fail-closed（假 client）、
JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date

import pytest

from zephyr.nlp.news_dual_tagger import (
    GAP_BEAT,
    GAP_MEET,
    GAP_MISS,
    GAP_NO_ANCHOR,
    PRED_BOTH,
    PRED_CALENDAR,
    PRED_CAPITAL,
    PRED_SURPRISE,
    ConsensusAnchor,
    DualTagConfig,
    EventKeywordRule,
    NewsTagInput,
    classify_expectation_gap,
    classify_predictability,
    load_consensus_anchors,
    match_calendar_rules,
    tag_news_dual,
)

TD = date(2026, 8, 21)


def _anchor(symbol: str = "000001.SZ") -> ConsensusAnchor:
    return ConsensusAnchor(
        symbol=symbol, forecast_year="2026", forecast_eps=1.0, forecast_pe=20.0,
        rating="买入", analyst_count=5, report_date="2026-08-15",
    )


# ------------------------------------------------------------------
# match_calendar_rules
# ------------------------------------------------------------------


def test_calendar_rule_hit():
    hits = match_calendar_rules("公司发布业绩预告，预计净利润大幅增长")
    assert any(r.name_zh == "业绩预告" for r in hits)


def test_calendar_rule_no_hit():
    assert match_calendar_rules("今日市场震荡整理") == []


def test_calendar_rule_advance_notice_false_excluded():
    rules = (EventKeywordRule("EVT-X-001", "突发事件", ("地震",), advance_notice=False),)
    assert match_calendar_rules("突发地震", rules) == []


# ------------------------------------------------------------------
# classify_predictability 四态
# ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("cal", "cap", "expected"),
    [
        (True, True, PRED_BOTH),
        (True, False, PRED_CALENDAR),
        (False, True, PRED_CAPITAL),
        (False, False, PRED_SURPRISE),
    ],
)
def test_predictability_four_states(cal, cap, expected):
    assert classify_predictability(cal, cap) == expected


# ------------------------------------------------------------------
# classify_expectation_gap 四态
# ------------------------------------------------------------------


def test_gap_beat():
    label, gap = classify_expectation_gap(1.2, 1.0, 5.0)
    assert label == GAP_BEAT and gap == pytest.approx(20.0)


def test_gap_miss():
    label, gap = classify_expectation_gap(0.8, 1.0, 5.0)
    assert label == GAP_MISS and gap == pytest.approx(-20.0)


def test_gap_meet_within_tolerance():
    label, gap = classify_expectation_gap(1.03, 1.0, 5.0)
    assert label == GAP_MEET and gap == pytest.approx(3.0)


def test_gap_no_anchor_zero():
    assert classify_expectation_gap(1.0, 0.0, 5.0) == (GAP_NO_ANCHOR, None)


def test_gap_no_anchor_none_actual():
    assert classify_expectation_gap(None, 1.0, 5.0) == (GAP_NO_ANCHOR, None)


# ------------------------------------------------------------------
# tag_news_dual 合成
# ------------------------------------------------------------------


def test_tag_dual_both_labels():
    news = [
        NewsTagInput(
            news_id="n1", title="华芯科技业绩预告预增", publish_time="2026-08-21 10:00:00",
            symbols=("000001.SZ",), actual_value=1.3, actual_symbol="000001.SZ",
        ),
        NewsTagInput(news_id="n2", title="午间突发传闻", publish_time="2026-08-21 12:00:00"),
    ]
    result = tag_news_dual(
        news,
        capital_traces={"000001.SZ": 5000.0},
        anchors={"000001.SZ": _anchor()},
        trade_date=TD,
    )
    assert result.date == "2026-08-21"
    first = result.items[0]
    assert first.predictability_label == PRED_BOTH  # 业绩预告日历 + 资金痕迹
    assert first.expectation_label == GAP_BEAT  # 1.3 vs 1.0 = +30%
    assert first.anchor_missing is False
    second = result.items[1]
    assert second.predictability_label == PRED_SURPRISE
    assert second.expectation_label == GAP_NO_ANCHOR
    assert second.anchor_missing is True
    assert result.counts[PRED_BOTH] == 1 and result.counts[GAP_NO_ANCHOR] == 1


def test_tag_capital_threshold_boundary():
    news = [NewsTagInput(news_id="n1", title="普通新闻", publish_time="t", symbols=("000001.SZ",))]
    result = tag_news_dual(news, capital_traces={"000001.SZ": 999.0})
    assert result.items[0].predictability_label == PRED_SURPRISE  # 未达阈值
    result2 = tag_news_dual(news, capital_traces={"000001.SZ": 1000.0})
    assert result2.items[0].predictability_label == PRED_CAPITAL  # 达阈值


def test_tag_anchor_field_pe():
    news = [
        NewsTagInput(
            news_id="n1", title="x", publish_time="t", symbols=("000001.SZ",), actual_value=25.0,
        ),
    ]
    cfg = DualTagConfig(anchor_field="forecast_pe", gap_tolerance_pct=5.0)
    result = tag_news_dual(news, anchors={"000001.SZ": _anchor()}, config=cfg)
    assert result.items[0].expectation_label == GAP_BEAT  # 25 vs 20 = +25%


def test_tag_bad_anchor_field_fail_closed():
    news = [NewsTagInput(news_id="n1", title="x", publish_time="t", symbols=("000001.SZ",), actual_value=1.0)]
    with pytest.raises(ValueError):
        tag_news_dual(news, anchors={"000001.SZ": _anchor()}, config=DualTagConfig(anchor_field="bad"))


def test_tag_bad_trade_date_fail_closed():
    with pytest.raises(ValueError):
        tag_news_dual([], trade_date="2026/08/21")


# ------------------------------------------------------------------
# load_consensus_anchors（假 client，不触库）
# ------------------------------------------------------------------


class _FakeClient:
    def __init__(self, rows):
        self._rows = rows
        self.last_params = None

    def execute(self, sql, params):
        self.last_params = params
        return self._rows


def test_load_anchors_pit_latest():
    rows = [
        ("000001.SZ", "2026", 1.0, 20.0, "买入", 5, date(2026, 8, 20)),  # 新
        ("000001.SZ", "2026", 0.9, 22.0, "增持", 3, date(2026, 8, 10)),  # 旧（ORDER BY DESC 首见取新）
    ]
    anchors = load_consensus_anchors(["000001.SZ"], TD, ch_client=_FakeClient(rows))
    assert anchors["000001.SZ"].forecast_eps == 1.0
    assert anchors["000001.SZ"].analyst_count == 5


def test_load_anchors_empty_symbols():
    assert load_consensus_anchors([], TD, ch_client=_FakeClient([])) == {}


def test_load_anchors_bad_date_fail_closed():
    with pytest.raises(ValueError):
        load_consensus_anchors(["000001.SZ"], "2026年8月21日", ch_client=_FakeClient([]))


def test_result_json_serializable():
    result = tag_news_dual(
        [NewsTagInput(news_id="n1", title="业绩预告预增", publish_time="t", symbols=("000001.SZ",), actual_value=1.3)],
        capital_traces={"000001.SZ": 5000.0}, anchors={"000001.SZ": _anchor()}, trade_date=TD,
    )
    json.dumps(asdict(result), ensure_ascii=False)
