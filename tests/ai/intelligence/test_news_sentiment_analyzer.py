"""MOD-INT-AISA NewsSentimentAnalyzer 单元测试——MVP 规则法 + 聚合器 + 事件检出。"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from zephyr.intelligence.news_sentiment_analyzer import (
    LLMSentimentScorer,
    NewsSentimentAnalyzer,
    NewsSentimentAnalyzerError,
    RuleBasedSentimentScorer,
    SentimentAggregator,
    SentimentEvent,
    SentimentScore,
    SentimentWindow,
)

# ============================================================================
# 1. 数据契约测试
# ============================================================================


class TestDataContracts:
    """冻结 dataclass 不可变测试。"""

    def test_sentiment_score_frozen(self) -> None:
        s = SentimentScore(news_id="n1", title="t", polarity=0.5, method="rule")
        with pytest.raises(AttributeError):
            s.polarity = 0.9  # type: ignore[misc]

    def test_sentiment_window_frozen(self) -> None:
        w = SentimentWindow(
            window_start=datetime(2026, 8, 18, 9, 0),
            window_end=datetime(2026, 8, 18, 10, 0),
            news_count=5,
            avg_polarity=0.1,
            positive_ratio=0.6,
            negative_ratio=0.2,
            sentiment_index=0.1,
        )
        with pytest.raises(AttributeError):
            w.sentiment_index = 0.9  # type: ignore[misc]

    def test_sentiment_event_defaults(self) -> None:
        e = SentimentEvent(
            event_time=datetime(2026, 8, 18, 10, 0),
            event_type="positive_spike",
            sentiment_index=0.5,
            trigger_news_count=3,
        )
        assert e.symbols == ()
        assert e.description == ""


# ============================================================================
# 2. 规则法打分器测试
# ============================================================================


class TestRuleBasedSentimentScorer:
    """关键词匹配打分逻辑。"""

    def test_positive_title(self) -> None:
        scorer = RuleBasedSentimentScorer()
        polarity, keywords = scorer.score("央行降准释放流动性", "")
        assert polarity > 0
        assert "降准" in keywords

    def test_negative_title(self) -> None:
        scorer = RuleBasedSentimentScorer()
        polarity, keywords = scorer.score("公司被立案调查 业绩暴雷", "")
        assert polarity < 0
        assert "立案调查" in keywords or "业绩暴雷" in keywords

    def test_neutral_title(self) -> None:
        scorer = RuleBasedSentimentScorer()
        polarity, keywords = scorer.score("今日大盘复盘", "")
        assert polarity == 0.0
        assert keywords == ()

    def test_title_weight_higher_than_content(self) -> None:
        scorer = RuleBasedSentimentScorer()
        # 同样关键词，在标题中权重更高
        p_title, _ = scorer.score("涨停", "")
        p_content, _ = scorer.score("", "涨停")
        assert p_title > p_content

    def test_custom_keywords(self) -> None:
        scorer = RuleBasedSentimentScorer(
            positive_keywords=frozenset({"特大利好"}),
            negative_keywords=frozenset({"特大利空"}),
        )
        p, k = scorer.score("特大利好来袭", "")
        assert p > 0
        assert "特大利好" in k

    def test_mixed_polarity(self) -> None:
        scorer = RuleBasedSentimentScorer()
        # 正负抵消
        p, _ = scorer.score("涨停后跌停", "")
        # 涨停+0.20，跌停-0.20 → 0.0
        assert p == 0.0

    def test_cap_at_090(self) -> None:
        scorer = RuleBasedSentimentScorer()
        # 大量正向词也不超 0.90
        p, _ = scorer.score("利好 涨停 增持 回购 分红 降准 降息 突破 超预期", "")
        assert p <= 0.90

    def test_duplicate_keyword_dedup(self) -> None:
        scorer = RuleBasedSentimentScorer()
        p1, _ = scorer.score("涨停", "")
        p2, _ = scorer.score("涨停涨停涨停", "")
        # 同一关键词去重，分数相同
        assert p1 == p2

    # ---------- GLM 复审回归（2026-08-18）：ST 边界 / 反转短语 ----------

    def test_st_risk_flag_matches(self) -> None:
        """大写 ST 风险警示（词边界）命中负向。"""
        scorer = RuleBasedSentimentScorer()
        polarity, keywords = scorer.score("公司股票被实施ST", "")
        assert polarity < 0
        assert "ST" in keywords

    def test_star_st_matches(self) -> None:
        """*ST 警示命中负向。"""
        scorer = RuleBasedSentimentScorer()
        polarity, keywords = scorer.score("*ST公司面临终止上市", "")
        assert polarity < 0
        assert "*ST" in keywords

    def test_lowercase_st_english_no_false_positive(self) -> None:
        """小写英文普通词含 st 子串（steady/boost/first/best）不误伤（P0-2 回归）。"""
        scorer = RuleBasedSentimentScorer()
        polarity, keywords = scorer.score("steady growth boosts investor confidence", "")
        assert polarity == 0.0
        assert keywords == ()

    def test_terminate_reversal_negative(self) -> None:
        """ "终止重大资产重组"是负向公告——反转短语先扣除，不被"重组"判正向（P0-3 回归）。"""
        scorer = RuleBasedSentimentScorer()
        polarity, keywords = scorer.score("公司终止重大资产重组", "")
        assert polarity < 0
        assert "终止重组" in keywords
        assert "重组" not in keywords  # 扣除后不再命中正向短词

    def test_merger_failure_negative(self) -> None:
        """ "并购失败"净负向（反转短语）。"""
        scorer = RuleBasedSentimentScorer()
        polarity, keywords = scorer.score("并购失败 公司寻求新方向", "")
        assert polarity < 0
        assert "并购失败" in keywords

    def test_normal_reversal_words_still_positive(self) -> None:
        """常规"重组成功推进"语境不受反转扣除影响，仍判正向。"""
        scorer = RuleBasedSentimentScorer()
        polarity, keywords = scorer.score("重大资产重组获批", "")
        assert polarity > 0
        assert "重组" in keywords


# ============================================================================
# 3. 聚合器测试
# ============================================================================


class TestSentimentAggregator:
    """时间窗口聚合逻辑。"""

    def test_empty_df(self) -> None:
        agg = SentimentAggregator(window_minutes=60)
        assert agg.aggregate_from_df(pd.DataFrame()) == []

    def test_missing_columns(self) -> None:
        agg = SentimentAggregator(window_minutes=60)
        df = pd.DataFrame({"polarity": [0.5]})
        with pytest.raises(NewsSentimentAnalyzerError, match="缺少列"):
            agg.aggregate_from_df(df)

    def test_single_window(self) -> None:
        agg = SentimentAggregator(window_minutes=60)
        df = pd.DataFrame(
            {
                "publish_time": pd.to_datetime(["2026-08-18 09:15", "2026-08-18 09:45"]),
                "polarity": [0.4, 0.6],
            }
        )
        windows = agg.aggregate_from_df(df)
        assert len(windows) == 1
        w = windows[0]
        assert w.news_count == 2
        assert w.avg_polarity == pytest.approx(0.5, abs=0.01)
        assert w.positive_ratio == pytest.approx(1.0, abs=0.01)
        assert w.negative_ratio == pytest.approx(0.0, abs=0.01)

    def test_multi_window(self) -> None:
        agg = SentimentAggregator(window_minutes=60)
        df = pd.DataFrame(
            {
                "publish_time": pd.to_datetime(
                    [
                        "2026-08-18 09:15",
                        "2026-08-18 09:45",
                        "2026-08-18 10:05",
                        "2026-08-18 10:55",
                    ]
                ),
                "polarity": [0.5, 0.3, -0.2, -0.4],
            }
        )
        windows = agg.aggregate_from_df(df)
        assert len(windows) == 2
        # 第一窗口（9:00~10:00）正向
        assert windows[0].avg_polarity > 0
        # 第二窗口（10:00~11:00）负向
        assert windows[1].avg_polarity < 0

    def test_window_alignment(self) -> None:
        """窗口按整点对齐，非按首条新闻时间对齐。"""
        agg = SentimentAggregator(window_minutes=60)
        df = pd.DataFrame(
            {
                "publish_time": pd.to_datetime(["2026-08-18 09:23"]),
                "polarity": [0.5],
            }
        )
        windows = agg.aggregate_from_df(df)
        assert len(windows) == 1
        assert windows[0].window_start == datetime(2026, 8, 18, 9, 0)
        assert windows[0].window_end == datetime(2026, 8, 18, 10, 0)

    def test_invalid_window_minutes(self) -> None:
        with pytest.raises(NewsSentimentAnalyzerError, match="> 0"):
            SentimentAggregator(window_minutes=0)


# ============================================================================
# 4. 主分析器测试
# ============================================================================


class TestNewsSentimentAnalyzer:
    """集成测试：打分 + 聚合 + 事件检出。"""

    def _sample_news_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "news_id": ["n1", "n2", "n3", "n4"],
                "title": [
                    "央行降准释放流动性",
                    "公司业绩暴雷被立案调查",
                    "今日大盘复盘",
                    "外资流入A股 机构看好",
                ],
                "content": ["", "", "", ""],
                "publish_time": pd.to_datetime(
                    [
                        "2026-08-18 09:15",
                        "2026-08-18 09:45",
                        "2026-08-18 10:05",
                        "2026-08-18 10:55",
                    ]
                ),
            }
        )

    def test_analyze_news_df_empty(self) -> None:
        analyzer = NewsSentimentAnalyzer()
        result = analyzer.analyze_news_df(pd.DataFrame())
        assert result.empty

    def test_analyze_news_df_rule(self) -> None:
        analyzer = NewsSentimentAnalyzer()
        result = analyzer.analyze_news_df(self._sample_news_df())
        assert len(result) == 4
        assert set(result["method"].unique()) == {"rule"}
        # 验证极性方向正确
        n1 = result[result["news_id"] == "n1"].iloc[0]
        assert n1["polarity"] > 0
        n2 = result[result["news_id"] == "n2"].iloc[0]
        assert n2["polarity"] < 0

    def test_analyze_news_df_llm_injected(self) -> None:
        """LLM 扩展口：注入 mock scorer 后走 LLM 通道（取 polarity 而非 score）。"""

        class MockLLMResult:
            """字段集对齐 nlp_inference.SentimentResult 真实契约。"""

            def __init__(self, polarity: float) -> None:
                self.sentiment = "positive"
                self.score = 0.5  # 强度（干扰项：若实现误用 score 会得 0.5）
                self.polarity = polarity

        def mock_scorer(title: str, content: str) -> MockLLMResult:
            return MockLLMResult(0.88)

        analyzer = NewsSentimentAnalyzer(llm_scorer=mock_scorer)
        result = analyzer.analyze_news_df(self._sample_news_df())
        assert set(result["method"].unique()) == {"llm"}
        assert all(abs(v - 0.88) < 0.01 for v in result["polarity"])

    def test_analyze_news_df_llm_neutral_not_faked_positive(self) -> None:
        """P0-1 回归：LLM neutral 结果（score=0.5 强度 / polarity=0.0 极性）
        必须产 0.0 极性——误用 score 会把中性新闻伪装成 +0.5 正向触发假事件。"""
        from types import SimpleNamespace

        def neutral_scorer(title: str, content: str) -> object:
            # 与 nlp_inference.SentimentResult 同字段集构造
            return SimpleNamespace(
                sentiment="neutral",
                score=0.5,
                polarity=0.0,
                news_id="",
                raw="",
                cached=False,
                error="",
            )

        analyzer = NewsSentimentAnalyzer(llm_scorer=neutral_scorer)
        result = analyzer.analyze_news_df(self._sample_news_df())
        assert set(result["method"].unique()) == {"llm"}
        assert all(result["polarity"] == 0.0)

    def test_analyze_news_df_llm_fallback(self) -> None:
        """LLM 抛异常时降级到 fallback，不阻断整体。"""

        def bad_scorer(title: str, content: str) -> None:
            raise RuntimeError("LLM timeout")

        analyzer = NewsSentimentAnalyzer(llm_scorer=bad_scorer)
        result = analyzer.analyze_news_df(self._sample_news_df())
        assert set(result["method"].unique()) == {"llm_fallback"}
        assert all(result["polarity"] == 0.0)

    def test_analyze_date_range_with_mock(self) -> None:
        """mock collect_news 验证全链路。"""
        analyzer = NewsSentimentAnalyzer(window_minutes=60)

        with patch("zephyr.intelligence.news_sentiment_analyzer.collect_news") as mock_collect:
            mock_collect.return_value = self._sample_news_df()
            scored, windows, events = analyzer.analyze_date_range("2026-08-18", "2026-08-18")

        assert len(scored) == 4
        assert len(windows) == 2
        # 第一窗口（9:00~10:00）含降准+暴雷，极性混合
        # 第二窗口（10:00~11:00）含复盘+外资流入，正向为主
        assert windows[1].sentiment_index > 0

    def test_analyze_date_range_scd_dedup(self) -> None:
        """P1-3 回归：news_data 为 SCD 多版本表（同 news_id 修正稿），
        merge 去重防窗口 news_count 膨胀。"""
        analyzer = NewsSentimentAnalyzer(window_minutes=60)

        # n1 两条版本（修正稿），同窗口——若 merge 不去重窗口 news_count=3
        news_df = pd.DataFrame(
            {
                "news_id": ["n1", "n1", "n2"],
                "title": ["央行降准", "央行降准（修正）", "大盘复盘"],
                "content": ["", "", ""],
                "publish_time": pd.to_datetime(["2026-08-18 09:15", "2026-08-18 09:40", "2026-08-18 09:50"]),
            }
        )

        with patch("zephyr.intelligence.news_sentiment_analyzer.collect_news") as mock_collect:
            mock_collect.return_value = news_df
            scored, windows, _ = analyzer.analyze_date_range("2026-08-18", "2026-08-18")

        # 打分仍逐条（3 行 scored），但聚合去重后窗口只算 2 条新闻
        assert len(scored) == 3
        assert len(windows) == 1
        assert windows[0].news_count == 2

    def test_event_detection_positive_spike(self) -> None:
        analyzer = NewsSentimentAnalyzer(positive_threshold=0.25)
        windows = [
            SentimentWindow(
                window_start=datetime(2026, 8, 18, 9, 0),
                window_end=datetime(2026, 8, 18, 10, 0),
                news_count=5,
                avg_polarity=0.4,
                positive_ratio=0.8,
                negative_ratio=0.0,
                sentiment_index=0.4,
            )
        ]
        events = analyzer._detect_events(windows)
        assert len(events) == 1
        assert events[0].event_type == "positive_spike"
        assert events[0].sentiment_index == pytest.approx(0.4, abs=0.01)

    def test_event_detection_negative_spike(self) -> None:
        analyzer = NewsSentimentAnalyzer(negative_threshold=-0.25)
        windows = [
            SentimentWindow(
                window_start=datetime(2026, 8, 18, 9, 0),
                window_end=datetime(2026, 8, 18, 10, 0),
                news_count=3,
                avg_polarity=-0.5,
                positive_ratio=0.0,
                negative_ratio=1.0,
                sentiment_index=-0.5,
            )
        ]
        events = analyzer._detect_events(windows)
        assert len(events) == 1
        assert events[0].event_type == "negative_spike"

    def test_event_detection_no_duplicate(self) -> None:
        """连续同向窗口不重复触发事件（防抖）。"""
        analyzer = NewsSentimentAnalyzer(positive_threshold=0.25)
        windows = [
            SentimentWindow(
                window_start=datetime(2026, 8, 18, 9, 0),
                window_end=datetime(2026, 8, 18, 10, 0),
                news_count=5,
                avg_polarity=0.4,
                positive_ratio=0.8,
                negative_ratio=0.0,
                sentiment_index=0.4,
            ),
            SentimentWindow(
                window_start=datetime(2026, 8, 18, 10, 0),
                window_end=datetime(2026, 8, 18, 11, 0),
                news_count=3,
                avg_polarity=0.5,
                positive_ratio=1.0,
                negative_ratio=0.0,
                sentiment_index=0.5,
            ),
        ]
        events = analyzer._detect_events(windows)
        assert len(events) == 1  # 第二个窗口不重复触发

    def test_event_detection_no_trigger(self) -> None:
        analyzer = NewsSentimentAnalyzer(positive_threshold=0.5, negative_threshold=-0.5)
        windows = [
            SentimentWindow(
                window_start=datetime(2026, 8, 18, 9, 0),
                window_end=datetime(2026, 8, 18, 10, 0),
                news_count=5,
                avg_polarity=0.2,
                positive_ratio=0.6,
                negative_ratio=0.2,
                sentiment_index=0.2,
            )
        ]
        events = analyzer._detect_events(windows)
        assert len(events) == 0


# ============================================================================
# 5. 错误契约测试
# ============================================================================


class TestErrorContract:
    """错误码与异常类型。"""

    def test_error_code(self) -> None:
        assert NewsSentimentAnalyzerError.error_code == "ZA-IT-0003"

    def test_aggregator_invalid_window_raises(self) -> None:
        with pytest.raises(NewsSentimentAnalyzerError):
            SentimentAggregator(window_minutes=-1)


# ============================================================================
# 6. 类型签名测试
# ============================================================================


class TestTypeSignatures:
    """LLMSentimentScorer 类型别名可用性。"""

    def test_llm_scorer_type_alias(self) -> None:
        """确保 LLMSentimentScorer 是可调用的类型注解。"""

        def my_scorer(title: str, content: str):
            class R:
                score = 0.5

            return R()

        scorer: LLMSentimentScorer = my_scorer
        result = scorer("test", "")
        assert result.score == 0.5
