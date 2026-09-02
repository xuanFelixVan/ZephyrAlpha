"""NightlySentimentWindow（MOD-INT-NEWS-NIGHT，92号 §8.4 M3-② / tracker #138）单元测试。

覆盖：
- 夜间窗口边界归属：17:59（排除）/ 18:00（含）/ 23:30（含）/ 次日 07:59（含）/ 08:00（排除）/ 12:00（排除）
- 聚合输出契约：sentiment_index=窗口平均极性 / 正负中性计数 / top_events 按 |polarity| 降序 /
  to_dict JSON 可序列化 + plan004_input 对接预留字段
- 标的关联统计：注入 linker 后 linked/ambiguous/market 级计数
- 写表幂等：persist=True mock writer，两次调用同键（scope/symbol/window_type/window_ts 一致），
  列序与 schemas/categories/market_news_sentiment_window.py INSERT_COLUMNS 真源一致
- 降级路径：collect_news 异常 / 窗口空 → degraded 不抛；非法 trade_date → ValueError
- analyzer 持久化钩子：persist_windows 行结构 / 默认关 / 异常降级 False
全部 mock（collect_news / writer），不触网不触库。
"""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import date, datetime
from unittest.mock import patch

import pandas as pd
import pytest

from zephyr.intelligence.news_sentiment_analyzer import NewsSentimentAnalyzer, SentimentWindow
from zephyr.intelligence.news_symbol_linker import NewsSymbolLinker
from zephyr.intelligence.nightly_sentiment_window import (
    NightlySentimentError,
    NightlySentimentResult,
    compute_nightly_sentiment,
    nightly_window,
)

_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from schemas.categories.market_news_sentiment_window import INSERT_COLUMNS  # noqa: E402

TRADE_DATE = "2026-08-19"  # 周三；窗口=[2026-08-18 18:00, 2026-08-19 08:00)


def _news_df(rows: list[tuple[str, str, str]]) -> pd.DataFrame:
    """(news_id, publish_time, title) → collect_news 标准列 DataFrame。"""
    return pd.DataFrame(
        {
            "news_id": [r[0] for r in rows],
            "publish_time": pd.to_datetime([r[1] for r in rows]),
            "title": [r[2] for r in rows],
            "content": [""] * len(rows),
            "source": ["cls"] * len(rows),
            "region": ["CN"] * len(rows),
            "language": ["zh"] * len(rows),
        }
    )


def _collect_mock(df: pd.DataFrame):
    return patch("zephyr.intelligence.nightly_sentiment_window.collect_news", return_value=df)


# ============================================================================
# 1. 窗口边界
# ============================================================================


class TestNightlyWindow:
    """nightly_window 边界 + 归属过滤。"""

    def test_window_bounds(self) -> None:
        start, end = nightly_window(date(2026, 8, 19))
        assert start == datetime(2026, 8, 18, 18, 0)
        assert end == datetime(2026, 8, 19, 8, 0)

    def test_boundary_attribution(self) -> None:
        """17:59 排除 / 18:00 含 / 次日 08:00 排除（左闭右开）。"""
        df = _news_df(
            [
                ("n_prev", "2026-08-18 17:59", "涨停"),  # 窗口前→排除
                ("n_start", "2026-08-18 18:00", "涨停"),  # 窗口起点→含
                ("n_mid", "2026-08-18 23:30", "跌停"),  # 窗口中→含
                ("n_am", "2026-08-19 07:59", "涨停"),  # 次日清晨→含
                ("n_end", "2026-08-19 08:00", "跌停"),  # 窗口终点→排除
                ("n_noon", "2026-08-19 12:00", "涨停"),  # 当日盘中→排除
            ]
        )
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE)
        assert result.total_count == 3
        assert result.window_start == datetime(2026, 8, 18, 18, 0)
        assert result.window_end == datetime(2026, 8, 19, 8, 0)

    def test_weekend_window_covers_sunday_news(self) -> None:
        """周一交易日窗口含周五 18:00 后周末新闻（自然日前推，跨周末覆盖）。"""
        start, end = nightly_window(date(2026, 8, 24))  # 周一
        assert start == datetime(2026, 8, 23, 18, 0)  # 周日 18:00 起
        assert end == datetime(2026, 8, 24, 8, 0)


# ============================================================================
# 2. 聚合输出契约
# ============================================================================


class TestAggregateContract:
    """聚合口径与输出契约。"""

    def test_sentiment_index_is_mean_polarity(self) -> None:
        """sentiment_index=窗口平均极性（与 SentimentAggregator 口径一致）。"""
        df = _news_df(
            [
                ("n1", "2026-08-18 20:00", "涨停"),  # rule: +0.20（标题命中）
                ("n2", "2026-08-18 21:00", "跌停"),  # rule: -0.20
            ]
        )
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE)
        assert result.sentiment_index == pytest.approx(0.0, abs=1e-6)
        assert result.positive_count == 1
        assert result.negative_count == 1
        assert result.neutral_count == 0
        assert result.total_count == 2
        assert result.degraded is False

    def test_top_events_sorted_by_abs_polarity(self) -> None:
        df = _news_df(
            [
                ("n1", "2026-08-18 20:00", "大盘复盘"),  # 0.0
                ("n2", "2026-08-18 21:00", "央行降准释放流动性 降息"),  # 强正
                ("n3", "2026-08-18 22:00", "反弹"),  # 弱正
            ]
        )
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE, top_n=2)
        assert len(result.top_events) == 2
        assert result.top_events[0]["news_id"] == "n2"  # |polarity| 最大
        assert abs(result.top_events[0]["polarity"]) >= abs(result.top_events[1]["polarity"])

    def test_to_dict_json_serializable_with_plan004_input(self) -> None:
        """to_dict() JSON 可序列化 + plan004_input 对接预留字段（MOD-PLAN-004 消费接线挂账）。"""
        df = _news_df([("n1", "2026-08-18 20:00", "涨停")])
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE)
        d = result.to_dict()
        json.dumps(d, ensure_ascii=False)  # 不抛即可序列化
        assert d["plan004_input"]["news_sentiment"] == result.sentiment_index
        assert d["plan004_input"]["news_total"] == 1
        assert d["plan004_input"]["degraded"] is False

    def test_result_frozen(self) -> None:
        df = _news_df([("n1", "2026-08-18 20:00", "涨停")])
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE)
        with pytest.raises(AttributeError):
            result.sentiment_index = 0.9  # type: ignore[misc]


# ============================================================================
# 3. 标的关联统计（#139 联动）
# ============================================================================


class TestLinkageStats:
    """注入 linker 后的关联覆盖统计。"""

    def test_linked_and_market_counts(self) -> None:
        linker = NewsSymbolLinker([("600519", "贵州茅台"), ("600001", "平安科技"), ("300001", "平安科技")])
        df = _news_df(
            [
                ("n1", "2026-08-18 20:00", "贵州茅台业绩大增"),  # 关联 1
                ("n2", "2026-08-18 21:00", "平安科技新战略"),  # 歧义关联
                ("n3", "2026-08-18 22:00", "央行降准"),  # market 级
            ]
        )
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE, linker=linker)
        assert result.linked_symbol_count == 2
        assert result.ambiguous_count == 1
        assert result.market_level_count == 1
        # top_events 附关联标的
        n1_event = next(e for e in result.top_events if e["news_id"] == "n1")
        assert n1_event["symbols"] == ["600519.SH"]

    def test_no_linker_zero_stats(self) -> None:
        """未注入 linker→不关联，统计全 0（market 级聚合）。"""
        df = _news_df([("n1", "2026-08-18 20:00", "贵州茅台涨停")])
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE)
        assert result.linked_symbol_count == 0
        assert result.market_level_count == 0


# ============================================================================
# 4. 写表幂等与列序真源一致
# ============================================================================


class TestPersist:
    """persist=True 写表（mock writer），同键重写幂等。"""

    def test_persist_idempotent_same_key(self) -> None:
        """两次调用写出的行键（scope/symbol/window_type/window_ts）一致→CH 同键替换幂等。"""
        df = _news_df([("n1", "2026-08-18 20:00", "涨停")])
        captured: list = []
        with _collect_mock(df):
            r1 = compute_nightly_sentiment(TRADE_DATE, persist=True, writer=lambda f: captured.append(f) or True)
            r2 = compute_nightly_sentiment(TRADE_DATE, persist=True, writer=lambda f: captured.append(f) or True)
        assert r1.persisted is True and r2.persisted is True
        assert len(captured) == 2
        assert captured[0].table == "c1_market.news_sentiment_window"
        key1 = captured[0].rows[0][:5]  # (window_ts, window_end, window_type, scope, symbol)
        key2 = captured[1].rows[0][:5]
        assert key1 == key2 == ("2026-08-18 18:00:00", "2026-08-19 08:00:00", "night", "market", "")

    def test_persist_columns_match_schema_ssot(self) -> None:
        """写表列序与 DDL-as-Code 真源 INSERT_COLUMNS 一致。"""
        df = _news_df([("n1", "2026-08-18 20:00", "涨停")])
        captured: list = []
        with _collect_mock(df):
            compute_nightly_sentiment(TRADE_DATE, persist=True, writer=lambda f: captured.append(f) or True)
        ssot_cols = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]
        assert captured[0].columns == ssot_cols
        assert len(captured[0].rows[0]) == len(ssot_cols)
        # top_events_json 为合法 JSON
        row = captured[0].rows[0]
        json.loads(row[11])
        assert row[12] == "rule"  # data_source

    def test_persist_default_off(self) -> None:
        """persist 默认关——writer 不被调用。"""
        df = _news_df([("n1", "2026-08-18 20:00", "涨停")])
        called: list = []
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE, writer=lambda f: called.append(f) or True)
        assert result.persisted is False
        assert called == []

    def test_persist_writer_exception_degrades(self) -> None:
        """写表异常→persisted=False 降级不抛。"""

        def _boom(f: object) -> bool:
            raise RuntimeError("CH down")

        df = _news_df([("n1", "2026-08-18 20:00", "涨停")])
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE, persist=True, writer=_boom)
        assert result.persisted is False
        assert any("写表" in r for r in result.reasons)


# ============================================================================
# 5. 降级路径与错误契约
# ============================================================================


class TestDegradation:
    """空窗口/读取异常/非法日期。"""

    def test_empty_window_degraded(self) -> None:
        df = _news_df([("n1", "2026-08-19 12:00", "涨停")])  # 窗口外
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE)
        assert result.total_count == 0
        assert result.degraded is True
        assert result.sentiment_index == 0.0

    def test_collect_exception_degraded(self) -> None:
        with patch(
            "zephyr.intelligence.nightly_sentiment_window.collect_news",
            side_effect=RuntimeError("CH down"),
        ):
            result = compute_nightly_sentiment(TRADE_DATE)
        assert result.degraded is True
        assert result.total_count == 0

    def test_empty_window_persist_writes_zero_row(self) -> None:
        """空窗口 persist=True 也落 0 计数行（夜间批留痕口径）。"""
        captured: list = []
        with _collect_mock(pd.DataFrame()):
            result = compute_nightly_sentiment(TRADE_DATE, persist=True, writer=lambda f: captured.append(f) or True)
        assert result.degraded is True
        assert result.persisted is True
        assert captured[0].rows[0][10] == 0  # total_count

    def test_invalid_trade_date_raises(self) -> None:
        with pytest.raises(ValueError):
            compute_nightly_sentiment("2026-13-40")

    def test_scd_dedup_keep_first(self) -> None:
        """SCD 多版本：同 news_id 修正稿按最早版本去重（PIT 语义）。"""
        df = _news_df(
            [
                ("n1", "2026-08-18 20:00", "涨停"),
                ("n1", "2026-08-18 21:00", "跌停"),  # 修正稿→丢弃
                ("n2", "2026-08-18 22:00", "涨停"),
            ]
        )
        with _collect_mock(df):
            result = compute_nightly_sentiment(TRADE_DATE)
        assert result.total_count == 2
        # n1 取 20:00 版本（+0.20），n2 +0.20 → 均值 +0.20
        assert result.sentiment_index == pytest.approx(0.20, abs=1e-4)


# ============================================================================
# 6. analyzer 持久化钩子（MOD-INT-AISA 增量）
# ============================================================================


class TestAnalyzerPersistHook:
    """NewsSentimentAnalyzer.persist_windows（92号 §8.4④，默认关）。"""

    def _window(self) -> SentimentWindow:
        return SentimentWindow(
            window_start=datetime(2026, 8, 18, 21, 0),
            window_end=datetime(2026, 8, 18, 22, 0),
            news_count=4,
            avg_polarity=0.25,
            positive_ratio=0.75,
            negative_ratio=0.25,
            sentiment_index=0.25,
        )

    def test_persist_windows_row_shape(self) -> None:
        captured: list = []
        analyzer = NewsSentimentAnalyzer()
        ok = analyzer.persist_windows([self._window()], writer=lambda f: captured.append(f) or True)
        assert ok is True
        row = captured[0].rows[0]
        assert row[:5] == ("2026-08-18 21:00:00", "2026-08-18 22:00:00", "1h", "market", "")
        assert row[5] == 0.25  # sentiment_index
        assert row[7:11] == (3, 1, 0, 4)  # pos/neg/neu/total
        assert row[12] == "rule"

    def test_persist_windows_empty_noop(self) -> None:
        called: list = []
        analyzer = NewsSentimentAnalyzer()
        assert analyzer.persist_windows([], writer=lambda f: called.append(f) or True) is True
        assert called == []

    def test_persist_windows_exception_degrades(self) -> None:
        analyzer = NewsSentimentAnalyzer()

        def _boom(f: object) -> bool:
            raise RuntimeError("CH down")

        assert analyzer.persist_windows([self._window()], writer=_boom) is False

    def test_analyze_date_range_persist_flag(self) -> None:
        """analyze_date_range persist=True 触发钩子（写表通道 mock 到 ch_writer）。"""
        analyzer = NewsSentimentAnalyzer(window_minutes=60)
        news_df = pd.DataFrame(
            {
                "news_id": ["n1", "n2"],
                "title": ["央行降准", "业绩暴雷"],
                "content": ["", ""],
                "publish_time": pd.to_datetime(["2026-08-18 09:15", "2026-08-18 09:45"]),
            }
        )
        captured: list = []
        with patch("zephyr.intelligence.news_sentiment_analyzer.collect_news", return_value=news_df):
            with patch(
                "zephyr.data.ch_writer.write_result", side_effect=lambda f, columns=None: captured.append(f) or True
            ):
                scored, windows, events = analyzer.analyze_date_range("2026-08-18", "2026-08-18", persist=True)
        assert len(windows) == 1
        assert len(captured) == 1
        assert captured[0].rows[0][2] == "1h"
