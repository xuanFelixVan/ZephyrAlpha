# [BLUEPRINT] MOD-KNW-006 | docs/03_modules/_domain_knowledge/strategy_knowledge_base/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-006 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_strategy_knowledge_base
# [TESTS] src/zephyr/knowledge/strategy_knowledge_base.py
"""MOD-KNW-006 单元测试：strategy_knowledge_base 策略知识库。

蓝图验收（B10-02182/CAND-KNW-005，A1 D-KNOWLEDGE-03）：
策略卡三要素（定义+表现+教训）+ 表现从 experiment_tracking 回填（注入适配器，
未注入 Fail-Closed）+ 按状态/风格/表现区间查询确定性排序 + 教训 FTS5 检索
（注入 sqlite :memory: 真连接）。时钟/kb_writer/适配器全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.knowledge.strategy_knowledge_base",
    reason="strategy_knowledge_base not importable",
)

from zephyr.knowledge.strategy_knowledge_base import (  # noqa: E402
    StrategyCard,
    StrategyKbError,
    StrategyKnowledgeBase,
    StrategyStatus,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _card(strategy_id: str = "t0_breakout", style: str = "趋势") -> StrategyCard:
    return StrategyCard(
        strategy_id=strategy_id,
        name="T0突破",
        style=style,
        definition={"entry": "突破20日高点", "exit": "跌破10日均线"},
    )


def _kb(
    entries: list | None = None,
    adapter=None,
    conn: sqlite3.Connection | None = None,
) -> StrategyKnowledgeBase:
    return StrategyKnowledgeBase(
        clock=lambda: _T0,
        kb_writer=(lambda e: entries.append(e)) if entries is not None else None,
        backfill_adapter=adapter,
        sqlite_conn=conn,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 策略卡注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterCard:
    def test_register_ok_initial_draft(self) -> None:
        kb = _kb()
        kb.register_card(_card())
        assert kb.get_card("t0_breakout").style == "趋势"
        assert kb.get_status("t0_breakout") is StrategyStatus.DRAFT

    def test_register_writes_kb_callback(self) -> None:
        entries: list[dict] = []
        kb = _kb(entries)
        kb.register_card(_card())
        assert len(entries) == 1
        assert entries[0]["kind"] == "strategy_card"
        assert entries[0]["strategy_id"] == "t0_breakout"

    def test_register_empty_fields_raises(self) -> None:
        kb = _kb()
        with pytest.raises(StrategyKbError):
            kb.register_card(StrategyCard(strategy_id="", name="n", style="s", definition={"k": 1}))
        with pytest.raises(StrategyKbError):
            kb.register_card(StrategyCard(strategy_id="x", name="", style="s", definition={"k": 1}))
        with pytest.raises(StrategyKbError):
            kb.register_card(StrategyCard(strategy_id="x", name="n", style="", definition={"k": 1}))
        with pytest.raises(StrategyKbError):
            kb.register_card(StrategyCard(strategy_id="x", name="n", style="s", definition={}))

    def test_register_duplicate_raises(self) -> None:
        kb = _kb()
        kb.register_card(_card())
        with pytest.raises(StrategyKbError):
            kb.register_card(_card())

    def test_unknown_strategy_raises(self) -> None:
        kb = _kb()
        with pytest.raises(StrategyKbError):
            kb.get_card("ghost")
        with pytest.raises(StrategyKbError):
            kb.get_status("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 表现回填（注入适配器）
# ──────────────────────────────────────────────────────────────────────────────


class TestPerformanceBackfill:
    def test_refresh_ok(self) -> None:
        entries: list[dict] = []
        kb = _kb(entries, adapter=lambda sid: {"sharpe": 1.5, "max_drawdown": -0.08})
        kb.register_card(_card())
        record = kb.refresh_performance("t0_breakout")
        assert record.metrics == {"sharpe": 1.5, "max_drawdown": -0.08}
        assert record.source == "experiment_tracking"
        assert record.updated_at == _T0
        assert entries[-1]["kind"] == "strategy_performance"
        assert kb.get_performance("t0_breakout") is record

    def test_refresh_adapter_missing_fail_closed(self) -> None:
        kb = _kb()  # 未注入适配器
        kb.register_card(_card())
        with pytest.raises(StrategyKbError):
            kb.refresh_performance("t0_breakout")

    def test_refresh_adapter_none_return_raises(self) -> None:
        kb = _kb(adapter=lambda sid: None)
        kb.register_card(_card())
        with pytest.raises(StrategyKbError):
            kb.refresh_performance("t0_breakout")

    def test_refresh_adapter_exception_raises(self) -> None:
        def _boom(sid: str):
            raise RuntimeError("tracking 失联")

        kb = _kb(adapter=_boom)
        kb.register_card(_card())
        with pytest.raises(StrategyKbError):
            kb.refresh_performance("t0_breakout")

    def test_refresh_non_numeric_metric_raises(self) -> None:
        kb = _kb(adapter=lambda sid: {"sharpe": "高"})
        kb.register_card(_card())
        with pytest.raises(StrategyKbError):
            kb.refresh_performance("t0_breakout")

    def test_refresh_unknown_strategy_raises(self) -> None:
        kb = _kb(adapter=lambda sid: {"sharpe": 1.0})
        with pytest.raises(StrategyKbError):
            kb.refresh_performance("ghost")

    def test_get_performance_before_refresh_raises(self) -> None:
        kb = _kb()
        kb.register_card(_card())
        with pytest.raises(StrategyKbError):
            kb.get_performance("t0_breakout")


# ──────────────────────────────────────────────────────────────────────────────
# 教训（FTS5 检索）
# ──────────────────────────────────────────────────────────────────────────────


class TestLessons:
    def test_add_lesson_deterministic_id(self) -> None:
        kb = _kb()
        kb.register_card(_card())
        l1 = kb.add_lesson("t0_breakout", "放量突破假信号多，需量能确认")
        l2 = kb.add_lesson("t0_breakout", "尾盘流动性差，避免重仓")
        assert l1.lesson_id == "t0_breakout#L001"
        assert l2.lesson_id == "t0_breakout#L002"
        assert [l.lesson_id for l in kb.lessons_of("t0_breakout")] == [
            "t0_breakout#L001",
            "t0_breakout#L002",
        ]

    def test_add_lesson_empty_text_raises(self) -> None:
        kb = _kb()
        kb.register_card(_card())
        with pytest.raises(StrategyKbError):
            kb.add_lesson("t0_breakout", "")

    def test_add_lesson_unknown_strategy_raises(self) -> None:
        kb = _kb()
        with pytest.raises(StrategyKbError):
            kb.add_lesson("ghost", "教训")

    def test_search_lessons_fts_hit(self) -> None:
        conn = sqlite3.connect(":memory:")
        kb = _kb(conn=conn)
        kb.register_card(_card())
        # FTS5 unicode61 分词：连续中文为单 token，关键词以空格分隔成独立词元
        kb.add_lesson("t0_breakout", "放量 突破假信号多，需 量能 确认")
        kb.add_lesson("t0_breakout", "尾盘流动性差，避免重仓")
        hits = kb.search_lessons("放量")
        assert [l.lesson_id for l in hits] == ["t0_breakout#L001"]
        hits2 = kb.search_lessons("量能")
        assert [l.lesson_id for l in hits2] == ["t0_breakout#L001"]

    def test_search_lessons_no_hit(self) -> None:
        conn = sqlite3.connect(":memory:")
        kb = _kb(conn=conn)
        kb.register_card(_card())
        kb.add_lesson("t0_breakout", "尾盘流动性差")
        assert kb.search_lessons("套利") == ()

    def test_search_lessons_conn_missing_fail_closed(self) -> None:
        kb = _kb()  # 未注入连接
        kb.register_card(_card())
        kb.add_lesson("t0_breakout", "教训文本")
        with pytest.raises(StrategyKbError):
            kb.search_lessons("教训")

    def test_search_lessons_empty_query_raises(self) -> None:
        conn = sqlite3.connect(":memory:")
        kb = _kb(conn=conn)
        with pytest.raises(StrategyKbError):
            kb.search_lessons("")


# ──────────────────────────────────────────────────────────────────────────────
# 状态机
# ──────────────────────────────────────────────────────────────────────────────


class TestStatusMachine:
    def test_full_lifecycle_with_history(self) -> None:
        entries: list[dict] = []
        kb = _kb(entries)
        kb.register_card(_card())
        kb.transition_status("t0_breakout", StrategyStatus.ACTIVE)
        kb.transition_status("t0_breakout", StrategyStatus.RETIRED)
        assert kb.get_status("t0_breakout") is StrategyStatus.RETIRED
        history = kb.status_history("t0_breakout")
        assert [t.to_status for t in history] == [StrategyStatus.ACTIVE, StrategyStatus.RETIRED]
        assert history[0].changed_at == _T0
        assert entries[-1]["kind"] == "strategy_status"

    def test_illegal_transition_raises(self) -> None:
        kb = _kb()
        kb.register_card(_card())
        kb.transition_status("t0_breakout", StrategyStatus.RETIRED)
        with pytest.raises(StrategyKbError):
            kb.transition_status("t0_breakout", StrategyStatus.ACTIVE)  # 终态不可逆

    def test_transition_unknown_or_bad_vocab_raises(self) -> None:
        kb = _kb()
        kb.register_card(_card())
        with pytest.raises(StrategyKbError):
            kb.transition_status("ghost", StrategyStatus.ACTIVE)
        with pytest.raises(StrategyKbError):
            kb.transition_status("t0_breakout", "paused")  # 词表外


# ──────────────────────────────────────────────────────────────────────────────
# 查询（确定性排序）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def _kb_with_cards(self) -> StrategyKnowledgeBase:
        perf = {
            "s_alpha": {"sharpe": 2.0},
            "s_beta": {"sharpe": 1.0},
            "s_gamma": {"sharpe": 1.5},
        }
        kb = _kb(adapter=lambda sid: perf[sid])
        kb.register_card(_card("s_alpha", style="趋势"))
        kb.register_card(_card("s_beta", style="套利"))
        kb.register_card(_card("s_gamma", style="趋势"))
        return kb

    def test_by_status_sorted(self) -> None:
        kb = self._kb_with_cards()
        kb.transition_status("s_beta", StrategyStatus.ACTIVE)
        kb.transition_status("s_alpha", StrategyStatus.ACTIVE)
        assert [c.strategy_id for c in kb.by_status(StrategyStatus.ACTIVE)] == ["s_alpha", "s_beta"]
        assert [c.strategy_id for c in kb.by_status(StrategyStatus.DRAFT)] == ["s_gamma"]

    def test_by_style_sorted(self) -> None:
        kb = self._kb_with_cards()
        assert [c.strategy_id for c in kb.by_style("趋势")] == ["s_alpha", "s_gamma"]
        assert kb.by_style("价值") == ()
        with pytest.raises(StrategyKbError):
            kb.by_style("")

    def test_by_performance_range(self) -> None:
        kb = self._kb_with_cards()
        for sid in ("s_alpha", "s_beta", "s_gamma"):
            kb.refresh_performance(sid)
        hits = kb.by_performance_range("sharpe", min_value=1.0, max_value=1.5)
        assert [c.strategy_id for c in hits] == ["s_gamma", "s_beta"]  # (-值, id) 排序
        assert [c.strategy_id for c in kb.by_performance_range("sharpe", min_value=2.0)] == ["s_alpha"]
        assert kb.by_performance_range("sharpe", min_value=9.9) == ()

    def test_by_performance_range_skips_missing_metric(self) -> None:
        kb = _kb(adapter=lambda sid: {"sharpe": 1.0} if sid == "s_a" else {"win_rate": 0.6})
        kb.register_card(_card("s_a"))
        kb.register_card(_card("s_b"))
        kb.refresh_performance("s_a")
        kb.refresh_performance("s_b")
        assert [c.strategy_id for c in kb.by_performance_range("sharpe", min_value=0.0)] == ["s_a"]

    def test_by_performance_range_invalid_raises(self) -> None:
        kb = _kb()
        with pytest.raises(StrategyKbError):
            kb.by_performance_range("")  # 空指标
        with pytest.raises(StrategyKbError):
            kb.by_performance_range("sharpe")  # 无界区间
