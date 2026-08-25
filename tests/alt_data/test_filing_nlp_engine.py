# [BLUEPRINT] MOD-ALT-003 | docs/03_modules/_domain_alt_data/filing_nlp_engine/blueprint.md | §test
# [A_test] module_id: MOD-ALT-003 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FilingNlpEngine 单元测试 (MOD-ALT-003, MVP)。

覆盖: 规则分类（各事件类型命中/优先序/无命中→其他）/ 影响评分（正向/负向/
混合 clip/无命中=0）/ LLM 路径（合法采纳/结构非法/分越界/置信度越界→回落规则
留痕）/ 单条 Fail-Closed / 配置 Fail-Closed / sink 委托与异常不阻断 /
确定性排序 / frozen。
"""

from __future__ import annotations

import dataclasses
import datetime

import pytest

from zephyr.alt_data.filing_nlp_engine import (
    EVENT_TYPES,
    ClassifyReport,
    FilingEvent,
    FilingInput,
    FilingNlpEngine,
    InvalidFilingError,
    InvalidFilingNlpConfigError,
)

_TS = datetime.datetime(2026, 8, 25, 12, 0, 0)


def _filing(
    filing_id: str = "F-1",
    symbol: str = "600519",
    title: str = "2026年半年度业绩预告",
    text: str = "净利润大幅增长，超预期",
    publish_time: datetime.datetime = _TS,
) -> FilingInput:
    return FilingInput(
        filing_id=filing_id,
        symbol=symbol,
        title=title,
        text=text,
        publish_time=publish_time,
    )


# ---------------------------------------------------------------------------
# 规则分类
# ---------------------------------------------------------------------------


class TestRuleClassify:
    @pytest.mark.parametrize(
        "title,expected",
        [
            ("2026年半年度业绩预告", "业绩预告"),
            ("2026年一季度业绩快报", "业绩快报"),
            ("关于股东减持股份的公告", "减持"),
            ("控股股东增持计划公告", "增持"),
            ("非公开发行股票（定增）预案", "定增"),
            ("关于重大诉讼的公告", "诉讼"),
            ("关于收到交易所问询函的公告", "问询函"),
            ("关于收到证监会行政处罚决定书的公告", "处罚"),
            ("2025年度分红派息实施公告", "分红"),
            ("关于回购公司股份方案的公告", "回购"),
            ("关于召开临时股东大会的通知", "其他"),
        ],
    )
    def test_event_type_hit(self, title, expected):
        eng = FilingNlpEngine()
        ev = eng.classify_one(_filing(title=title, text="正文"))
        assert ev.event_type == expected and ev.extractor == "rule"

    def test_priority_first_match(self):
        # "业绩预告" 与 "增长" 同现时按规则优先序定类
        eng = FilingNlpEngine()
        ev = eng.classify_one(_filing(title="业绩预告：净利润增长", text=""))
        assert ev.event_type == "业绩预告"

    def test_no_hit_other(self):
        eng = FilingNlpEngine()
        ev = eng.classify_one(_filing(title="普通公告", text="无关键词"))
        assert ev.event_type == "其他" and ev.impact_score == 0.0

    def test_event_types_closed_set(self):
        assert "其他" in EVENT_TYPES and len(EVENT_TYPES) == 11


# ---------------------------------------------------------------------------
# 影响评分
# ---------------------------------------------------------------------------


class TestImpactScore:
    def test_positive(self):
        eng = FilingNlpEngine()
        ev = eng.classify_one(_filing(text="净利润大幅增长"))
        assert ev.impact_score > 0 and ev.confidence == pytest.approx(0.6)

    def test_negative(self):
        eng = FilingNlpEngine()
        ev = eng.classify_one(_filing(title="关于股东减持股份的公告", text="拟减持股份，存在风险"))
        assert ev.impact_score < 0

    def test_clipped_to_range(self):
        eng = FilingNlpEngine()
        ev = eng.classify_one(_filing(text="增长 增长 增长 增长 增长 超预期 利好 利好 利好"))
        assert -1.0 <= ev.impact_score <= 1.0
        assert ev.impact_score == pytest.approx(1.0)

    def test_no_keyword_zero(self):
        eng = FilingNlpEngine()
        ev = eng.classify_one(_filing(title="普通公告", text="无"))
        assert ev.impact_score == 0.0


# ---------------------------------------------------------------------------
# LLM 路径
# ---------------------------------------------------------------------------


class TestLlmPath:
    def test_llm_valid_adopted(self):
        llm = lambda f: {"event_type": "减持", "impact_score": -0.8, "confidence": 0.9}
        eng = FilingNlpEngine(llm_extractor=llm)
        ev = eng.classify_one(_filing())
        assert (ev.event_type, ev.impact_score, ev.confidence, ev.extractor) == ("减持", -0.8, 0.9, "llm")

    def test_llm_unknown_type_fallback(self):
        llm = lambda f: {"event_type": "外星人事件", "impact_score": 0.5, "confidence": 0.9}
        eng = FilingNlpEngine(llm_extractor=llm)
        rep = eng.classify([_filing()])
        assert rep.llm_invalid == 1 and rep.events[0].extractor == "rule"

    def test_llm_score_out_of_range_fallback(self):
        llm = lambda f: {"event_type": "减持", "impact_score": -2.5, "confidence": 0.9}
        eng = FilingNlpEngine(llm_extractor=llm)
        rep = eng.classify([_filing()])
        assert rep.llm_invalid == 1 and rep.events[0].extractor == "rule"

    def test_llm_confidence_out_of_range_fallback(self):
        llm = lambda f: {"event_type": "减持", "impact_score": -0.5, "confidence": 1.5}
        eng = FilingNlpEngine(llm_extractor=llm)
        assert eng.classify([_filing()]).llm_invalid == 1

    def test_llm_exception_fallback_not_blocking(self):
        def boom(f):
            raise RuntimeError("llm down")

        eng = FilingNlpEngine(llm_extractor=boom)
        rep = eng.classify([_filing()])
        assert rep.llm_invalid == 1 and rep.events[0].extractor == "rule"
        assert rep.events[0].event_type == "业绩预告"

    def test_llm_non_dict_fallback(self):
        eng = FilingNlpEngine(llm_extractor=lambda f: "bad")
        assert eng.classify([_filing()]).llm_invalid == 1

    def test_llm_hits_counted(self):
        llm = lambda f: {"event_type": "增持", "impact_score": 0.7, "confidence": 0.8}
        eng = FilingNlpEngine(llm_extractor=llm)
        rep = eng.classify([_filing("F-1"), _filing("F-2")])
        assert rep.llm_hits == 2 and rep.rule_hits == 0


# ---------------------------------------------------------------------------
# 校验 / 配置
# ---------------------------------------------------------------------------


class TestValidation:
    @pytest.mark.parametrize("kw", [{"filing_id": ""}, {"symbol": " "}, {"title": ""}])
    def test_blank_fields_rejected(self, kw):
        raw = {
            "filing_id": "F-1",
            "symbol": "600519",
            "title": "业绩预告",
            "text": "增长",
            "publish_time": _TS,
        }
        raw.update(kw)
        eng = FilingNlpEngine()
        rep = eng.classify([raw])
        assert rep.rejected == 1 and rep.events == ()

    def test_bad_publish_time_rejected(self):
        eng = FilingNlpEngine()
        rep = eng.classify(
            [{"filing_id": "F-1", "symbol": "600519", "title": "业绩预告", "text": "", "publish_time": "bad"}]
        )
        assert rep.rejected == 1

    def test_dict_input_accepted(self):
        eng = FilingNlpEngine()
        rep = eng.classify(
            [{"filing_id": "F-9", "symbol": "600519", "title": "业绩预告", "text": "增长", "publish_time": _TS}]
        )
        assert rep.accepted == 1

    def test_filing_input_blank_raises(self):
        with pytest.raises(InvalidFilingError):
            _filing(filing_id="")

    def test_llm_not_callable_config(self):
        with pytest.raises(InvalidFilingNlpConfigError):
            FilingNlpEngine(llm_extractor=1)

    def test_sink_not_callable_config(self):
        with pytest.raises(InvalidFilingNlpConfigError):
            FilingNlpEngine(sink="x")

    def test_keyword_rules_unknown_type_config(self):
        with pytest.raises(InvalidFilingNlpConfigError):
            FilingNlpEngine(keyword_rules={"不存在类型": ("x",)})

    def test_keyword_rules_override(self):
        eng = FilingNlpEngine(keyword_rules={"诉讼": ("仲裁",)})
        ev = eng.classify_one(_filing(title="关于仲裁的公告", text=""))
        assert ev.event_type == "诉讼"
        # 覆盖后内置规则不再生效
        ev2 = eng.classify_one(_filing(title="2026年半年度业绩预告", text=""))
        assert ev2.event_type == "其他"


# ---------------------------------------------------------------------------
# 批量 / sink / 确定性 / frozen
# ---------------------------------------------------------------------------


class TestBatchSinkDeterminism:
    def test_sorted_by_time_then_id(self):
        f1 = _filing("F-2", publish_time=datetime.datetime(2026, 8, 25, 9, 0, 0))
        f2 = _filing("F-1", publish_time=datetime.datetime(2026, 8, 25, 10, 0, 0))
        f3 = _filing("F-0", publish_time=datetime.datetime(2026, 8, 25, 9, 0, 0))
        eng = FilingNlpEngine()
        rep = eng.classify([f1, f2, f3])
        assert [e.event_id for e in rep.events] == ["F-0", "F-2", "F-1"]

    def test_sink_called(self):
        seen = []
        eng = FilingNlpEngine(sink=lambda events: seen.extend(events))
        rep = eng.classify([_filing()])
        assert rep.sink_attempted and rep.sink_ok and len(seen) == 1

    def test_sink_exception_not_blocking(self):
        def boom(events):
            raise RuntimeError("db down")

        eng = FilingNlpEngine(sink=boom)
        rep = eng.classify([_filing()])
        assert rep.sink_attempted and not rep.sink_ok and rep.events

    def test_same_input_same_output(self):
        e1, e2 = FilingNlpEngine(), FilingNlpEngine()
        assert e1.classify([_filing()]) == e2.classify([_filing()])

    def test_event_fields(self):
        eng = FilingNlpEngine()
        ev = eng.classify_one(_filing())
        assert ev.event_id == "F-1" and ev.symbol == "600519"
        assert ev.source_id == "cninfo" and ev.summary

    def test_frozen(self):
        eng = FilingNlpEngine()
        ev = eng.classify_one(_filing())
        with pytest.raises(dataclasses.FrozenInstanceError):
            ev.event_type = "减持"
        with pytest.raises(dataclasses.FrozenInstanceError):
            _filing().symbol = "000001"
