# [BLUEPRINT] MOD-ALT-010 | docs/03_modules/_domain_alt_data/policy_expectation_analyzer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ALT-010 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_policy_expectation_analyzer
# [TESTS] src/zephyr/alt_data/policy_expectation_analyzer.py
"""MOD-ALT-010 单元测试：policy_expectation_analyzer A股政策预期分析器。

蓝图验收（B5-07096/CAND-TESTA-026，B5 D-ALT-DATA-16，承接 TESTA-013）：
公开表态采集（注入源/去重幂等）+ 窗口指导关键词命中扫描（词表序/确定性）
+ 政策事件日历（排序/起滤）+ LLM 预期倾向打分（[-1,1] 闭合校验 Fail-Closed）
+ 国家队持仓异动识别（ETF 份额阈值/as_of 单调）+ 预期差信号（is_inferred
恒 True + 人工审核队列）。源/LLM/审核回调/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.alt_data.policy_expectation_analyzer",
    reason="policy_expectation_analyzer not importable",
)

from zephyr.alt_data.policy_expectation_analyzer import (  # noqa: E402
    EtfSharesSnapshot,
    PolicyEvent,
    PolicyExpectationAnalyzer,
    PolicyExpectationError,
    PolicyStatement,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 26, 10, 0, 0)
_D0 = datetime.date(2026, 8, 26)

_KEYWORDS = ("窗口指导", "降准", "审慎")


def _statement(
    statement_id: str = "st1",
    authority: str = "央行",
    content: str = "坚持稳健货币政策，适时降准保持流动性合理充裕",
    published_at: datetime.datetime = _T0,
) -> PolicyStatement:
    return PolicyStatement(
        statement_id=statement_id,
        authority=authority,
        content=content,
        published_at=published_at,
    )


def _analyzer(**kw) -> PolicyExpectationAnalyzer:
    kw.setdefault("clock", lambda: _T0)
    kw.setdefault("keyword_library", _KEYWORDS)
    return PolicyExpectationAnalyzer(**kw)


def _snapshot(etf_code: str = "510300", shares: float = 100.0, as_of: datetime.date = _D0) -> EtfSharesSnapshot:
    return EtfSharesSnapshot(etf_code=etf_code, shares=shares, as_of=as_of)


# ──────────────────────────────────────────────────────────────────────────────
# 构造期配置 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_invalid_config_raises(self) -> None:
        for bad_threshold in (0.0, -0.1, float("nan"), float("inf"), True, "0.1"):
            with pytest.raises(PolicyExpectationError):
                _analyzer(etf_change_threshold=bad_threshold)
        for bad_kw in ("", 123, None):
            with pytest.raises(PolicyExpectationError):
                _analyzer(keyword_library=("降准", bad_kw))
        with pytest.raises(PolicyExpectationError):
            _analyzer(llm_scorer="not-callable")
        with pytest.raises(PolicyExpectationError):
            _analyzer(statement_source=1)
        with pytest.raises(PolicyExpectationError):
            _analyzer(review_sink=2)

    def test_keyword_library_dedup_preserve_order(self) -> None:
        az = _analyzer(keyword_library=("降准", "窗口指导", "降准"))
        assert az._keywords == ("降准", "窗口指导")  # 去重保序（词表序=命中序）


# ──────────────────────────────────────────────────────────────────────────────
# 表态采集
# ──────────────────────────────────────────────────────────────────────────────


class TestCollectStatements:
    def test_collect_ok_dedup_sorted(self) -> None:
        az = _analyzer(statement_source=lambda: [
            _statement("st2", published_at=_T1),
            _statement("st1"),
            _statement("st1"),  # 批内重复
        ])
        assert az.collect_statements() == 2
        assert az.collect_statements() == 0  # 跨批幂等
        assert [s.statement_id for s in az.statements()] == ["st1", "st2"]  # 时序升序

    def test_collect_without_source_fail_closed(self) -> None:
        with pytest.raises(PolicyExpectationError):
            _analyzer().collect_statements()

    def test_source_errors_raise(self) -> None:
        def _boom():
            raise RuntimeError("src down")

        with pytest.raises(PolicyExpectationError):
            _analyzer(statement_source=_boom).collect_statements()  # 抓取异常包装
        with pytest.raises(PolicyExpectationError):
            _analyzer(statement_source=lambda: {"not": "list"}).collect_statements()  # 类型非法
        with pytest.raises(PolicyExpectationError):
            _analyzer(statement_source=lambda: [{"not": "statement"}]).collect_statements()

    def test_invalid_statement_raises(self) -> None:
        bad_cases = [
            _statement(statement_id=""),
            _statement(authority=""),
            _statement(content=""),
            _statement(published_at="2026-08-26"),
        ]
        for bad in bad_cases:
            az = _analyzer(statement_source=lambda b=bad: [b])
            with pytest.raises(PolicyExpectationError):
                az.collect_statements()


# ──────────────────────────────────────────────────────────────────────────────
# 窗口指导关键词扫描
# ──────────────────────────────────────────────────────────────────────────────


class TestScan:
    def _filled(self) -> PolicyExpectationAnalyzer:
        az = _analyzer(statement_source=lambda: [
            _statement("st_b", content="适度宽松，研究降准工具"),
            _statement("st_a", content="对地产窗口指导并要求审慎放贷，降准空间仍存"),
            _statement("st_c", content="常态化监管座谈会"),
        ])
        az.collect_statements()
        return az

    def test_hits_library_order_deterministic(self) -> None:
        hits = self._filled().scan_window_guidance()
        assert list(hits) == ["st_a", "st_b"]  # 仅命中者 + id 升序
        assert hits["st_a"] == ("窗口指导", "降准", "审慎")  # 命中序=词表序
        assert hits["st_b"] == ("降准",)

    def test_scan_subset_and_unknown_raises(self) -> None:
        az = self._filled()
        assert list(az.scan_window_guidance(["st_b", "st_c"])) == ["st_b"]
        with pytest.raises(PolicyExpectationError):
            az.scan_window_guidance(["ghost"])

    def test_empty_library_no_hits(self) -> None:
        az = _analyzer(keyword_library=(), statement_source=lambda: [_statement()])
        az.collect_statements()
        assert az.scan_window_guidance() == {}


# ──────────────────────────────────────────────────────────────────────────────
# 政策事件日历
# ──────────────────────────────────────────────────────────────────────────────


class TestCalendar:
    def test_add_sorted_and_from_date_filter(self) -> None:
        az = _analyzer()
        az.add_event(PolicyEvent("ev2", _D0 + datetime.timedelta(days=7), "降准落地日"))
        az.add_event(PolicyEvent("ev1", _D0, "国常会"))
        az.add_event(PolicyEvent("ev3", _D0 + datetime.timedelta(days=3), "三中全会"))
        assert [e.event_id for e in az.calendar()] == ["ev1", "ev3", "ev2"]
        assert [e.event_id for e in az.calendar(from_date=_D0 + datetime.timedelta(days=3))] == ["ev3", "ev2"]

    def test_invalid_event_raises(self) -> None:
        az = _analyzer()
        az.add_event(PolicyEvent("ev1", _D0, "国常会"))
        with pytest.raises(PolicyExpectationError):
            az.add_event(PolicyEvent("ev1", _D0, "重复"))  # id 重复
        with pytest.raises(PolicyExpectationError):
            az.add_event(PolicyEvent("", _D0, "空id"))
        with pytest.raises(PolicyExpectationError):
            az.add_event(PolicyEvent("ev9", _D0, ""))  # 空标题
        with pytest.raises(PolicyExpectationError):
            az.add_event(PolicyEvent("ev9", "2026-08-26", "坏日期"))
        with pytest.raises(PolicyExpectationError):
            az.add_event("not-an-event")
        with pytest.raises(PolicyExpectationError):
            az.calendar(from_date="2026-08-26")


# ──────────────────────────────────────────────────────────────────────────────
# LLM 预期倾向打分（[-1,1] 闭合校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestScore:
    def test_score_ok_and_enqueued(self) -> None:
        review_log: list = []
        az = _analyzer(llm_scorer=lambda text: 0.66, review_sink=review_log.append)
        signal = az.score_expectation("降准", text="适时降准，窗口指导信贷投向")
        assert signal.expectation_score == 0.66
        assert signal.is_inferred is True  # 推断性质标注，仅作信号输入
        assert signal.keyword_hits == ("窗口指导", "降准")  # 语料关键词命中
        assert signal.generated_at == _T0
        assert az.signals() == (signal,)
        assert az.pending_review() == (signal,)  # 必入人工审核队列
        assert review_log == [signal]

    def test_score_without_llm_fail_closed(self) -> None:
        with pytest.raises(PolicyExpectationError):
            _analyzer().score_expectation("降准", text="任何语料")

    def test_score_out_of_range_fail_closed(self) -> None:
        for bad in (1.01, -1.5, float("nan"), float("inf"), True, "0.5", None):
            az = _analyzer(llm_scorer=lambda _t, b=bad: b)
            with pytest.raises(PolicyExpectationError):
                az.score_expectation("降准", text="语料")  # 闭合校验拒绝

    def test_score_boundary_accepted(self) -> None:
        for edge in (-1.0, 1.0, 0):
            az = _analyzer(llm_scorer=lambda _t, e=edge: e)
            signal = az.score_expectation("降准", text="语料")
            assert signal.expectation_score == float(edge)  # 恰等边界合法

    def test_llm_exception_wrapped(self) -> None:
        def _boom(_t):
            raise RuntimeError("llm down")

        with pytest.raises(PolicyExpectationError):
            _analyzer(llm_scorer=_boom).score_expectation("降准", text="语料")

    def test_topic_corpus_aggregation_and_empty_raises(self) -> None:
        seen: list = []
        az = _analyzer(
            statement_source=lambda: [
                _statement("st2", content="财政发力与地产无关表态", published_at=_T1),
                _statement("st1", content="适时降准释放流动性", published_at=_T0),
                _statement("st3", content="再次强调降准节奏", published_at=_T0 + datetime.timedelta(hours=2)),
            ],
            llm_scorer=lambda text: seen.append(text) or 0.1,
        )
        az.collect_statements()
        signal = az.score_expectation("降准")  # text=None → 按 topic 聚合语料
        assert seen == ["适时降准释放流动性\n再次强调降准节奏"]  # 时序确定性拼接
        assert signal.topic == "降准"
        with pytest.raises(PolicyExpectationError):
            az.score_expectation("不存在的话题")  # 空语料禁止打分
        with pytest.raises(PolicyExpectationError):
            az.score_expectation("")  # topic 空
        with pytest.raises(PolicyExpectationError):
            az.score_expectation("降准", text="")  # text 空


# ──────────────────────────────────────────────────────────────────────────────
# 国家队持仓变动识别
# ──────────────────────────────────────────────────────────────────────────────


class TestHolding:
    def test_first_and_below_threshold_no_change(self) -> None:
        az = _analyzer(etf_change_threshold=0.10)
        assert az.register_etf_snapshot(_snapshot(shares=100.0)) is None  # 首期无基期
        nxt = _snapshot(shares=105.0, as_of=_D0 + datetime.timedelta(days=90))
        assert az.register_etf_snapshot(nxt) is None  # 5% < 阈值 10%
        assert az.holding_changes() == ()

    def test_threshold_hit_flagged_both_directions(self) -> None:
        az = _analyzer(etf_change_threshold=0.10)
        az.register_etf_snapshot(_snapshot(shares=100.0))
        up = az.register_etf_snapshot(
            _snapshot(shares=112.0, as_of=_D0 + datetime.timedelta(days=90)),
        )
        assert up is not None
        assert up.previous_shares == 100.0 and up.current_shares == 112.0
        assert up.change_ratio == pytest.approx(0.12)
        assert up.flagged_at == _T0
        down = az.register_etf_snapshot(
            _snapshot(shares=100.0, as_of=_D0 + datetime.timedelta(days=180)),
        )
        assert down is not None and down.change_ratio == pytest.approx(-0.1071, abs=1e-4)
        assert [c.change_ratio for c in az.holding_changes()] == [
            pytest.approx(0.12), pytest.approx(-0.1071, abs=1e-4),
        ]

    def test_threshold_boundary_exact_hit(self) -> None:
        az = _analyzer(etf_change_threshold=0.10)
        az.register_etf_snapshot(_snapshot(shares=100.0))
        hit = az.register_etf_snapshot(
            _snapshot(shares=110.0, as_of=_D0 + datetime.timedelta(days=90)),
        )
        assert hit is not None  # 恰等阈值命中（≥）

    def test_ordering_conflict_and_idempotent(self) -> None:
        az = _analyzer()
        az.register_etf_snapshot(_snapshot(shares=100.0, as_of=_D0))
        assert az.register_etf_snapshot(_snapshot(shares=100, as_of=_D0)) is None  # 同日同额幂等
        with pytest.raises(PolicyExpectationError):
            az.register_etf_snapshot(_snapshot(shares=120.0, as_of=_D0))  # 同日异额冲突
        with pytest.raises(PolicyExpectationError):
            az.register_etf_snapshot(
                _snapshot(shares=110.0, as_of=_D0 - datetime.timedelta(days=1)),
            )  # 乱序拒绝

    def test_invalid_snapshot_raises(self) -> None:
        az = _analyzer()
        for bad in (
            _snapshot(etf_code=""),
            _snapshot(shares=0.0),
            _snapshot(shares=-5.0),
            _snapshot(shares=float("nan")),
            _snapshot(shares=True),
            EtfSharesSnapshot("510300", 100.0, "2026-08-26"),
        ):
            with pytest.raises(PolicyExpectationError):
                az.register_etf_snapshot(bad)
        with pytest.raises(PolicyExpectationError):
            az.register_etf_snapshot("not-a-snapshot")


# ──────────────────────────────────────────────────────────────────────────────
# 人工审核队列
# ──────────────────────────────────────────────────────────────────────────────


class TestReviewQueue:
    def test_mark_reviewed_flow(self) -> None:
        now = [_T0]
        az = PolicyExpectationAnalyzer(
            clock=lambda: now[0],
            llm_scorer=lambda _t: 0.5,
            keyword_library=_KEYWORDS,
        )
        s1 = az.score_expectation("降准", text="语料一")
        now[0] = _T1
        s2 = az.score_expectation("降息", text="语料二")
        assert az.pending_review() == (s1, s2)  # 入队序
        az.mark_reviewed("降准", _T0)
        assert az.pending_review() == (s2,)
        assert az.signals() == (s1, s2)  # 销号不删信号档案

    def test_mark_reviewed_no_match_raises(self) -> None:
        az = _analyzer(llm_scorer=lambda _t: 0.5)
        az.score_expectation("降准", text="语料")
        with pytest.raises(PolicyExpectationError):
            az.mark_reviewed("降准", _T1)  # 时间戳不匹配
        with pytest.raises(PolicyExpectationError):
            az.mark_reviewed("降息", _T0)  # topic 不匹配

    def test_review_sink_exception_not_blocking(self) -> None:
        def _boom(_s):
            raise RuntimeError("sink down")

        az = _analyzer(llm_scorer=lambda _t: 0.5, review_sink=_boom)
        signal = az.score_expectation("降准", text="语料")
        assert az.pending_review() == (signal,)  # 回调异常不阻断入队
