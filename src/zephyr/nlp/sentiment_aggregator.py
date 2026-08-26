# [BLUEPRINT] MOD-NLP-AGGREGATOR-001 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 7
# [MODULE] zephyr.nlp.sentiment_aggregator
# [DOMAIN] D_DATA
# [DEPENDENCIES] pandas; zephyr.nlp.nlp_inference（SentimentResult 鸭型消费）
# [CONSUMERS] scripts/ml/run_sentiment_batch.py; 26_event_driven_strategy_detail §2.5 event_score sentiment_score 维度; regime S2 bad_news_flat（Phase 7 替换关键词 MVP 的 negative_count 源）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 跨源一致性投票——≥2 源同向才输出强信号，单源孤证降级弱信号（×0.5），多源冲突→0；tanh 软投票有界 [-1,1]；空输入→空结果不抛异常；polarity 越界输入裁剪 [-1,1]
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 7; 26_event_driven_strategy_detail.md §2.7
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无自定义异常——空/退化输入返回空结果或中性票，不抛异常
# [TESTS] tests/nlp/test_sentiment_aggregator.py
# [A_module] module_id=MOD-NLP-AGGREGATOR-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-NLP-PIPELINE-001 Phase 7
# [ALGO_FLOW]
# I1: SourceSentiment 序列（source/polarity∈[-1,1]/publish_date/symbol）
# F1: vote_cross_source（按源求均 polarity→源方向；≥2 源同向=strong tanh 软投票；单源=weak ×0.5；冲突/全中性=0）
# F2: aggregate_daily / aggregate_daily_by_symbol（按日[/标的]分组→计数+均值+跨源票）
# A1: to_negative_count_series（DailySentiment→negative_count 日序列，供 S2 bad_news_flat）
# O1: CrossSourceVote（direction/score/strength）+ DailySentiment 列表
# [/ALGO_FLOW]
"""MOD-NLP-AGGREGATOR-001 SentimentAggregator — 跨源情绪一致性投票聚合（NLP Phase 7）。

设计依据：
- 13 号 §3.1.11 步骤 9：情感聚合层 ``sentiment_aggregator.py``，按日/板块聚合。
- 26 号 §2.7（v1.9.0 跨源情绪集成，RavenPack × FT 2026-03）：两独立新闻源秩相关
  仅 10-14%（真正交），cross-validated ensemble + tanh 软投票 IR 0.48→0.81。
  **裁定**：东财/财联社/RSS 三源异质，采用**跨源一致性投票**而非简单均值——
  ≥2 源同向才输出强 sentiment_score，单源孤证降级弱信号。
- 26 号 §2.7 QLoRA 警示：sentiment_score 定位为事件方向触发，非截面排序。

聚合口径：
- 每源先求均 polarity（源内等权），再按源方向投票（源间等权，防单源量级霸票）。
- 强信号：``tanh(mean_polarity)``（软投票有界，防过自信极端值）。
- 弱信号：``tanh(mean_polarity × 0.5)``（单源孤证降级）。
- 冲突（正负互搏无多数）/全中性：0.0。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 7
      docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.7
SSoT: #ARCH-NLP-PIPELINE-001
Version: 0.1.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Final, Sequence

import pandas as pd

# ── 跨源投票参数（26 号 §2.7 裁定）──
MIN_AGREE_SOURCES: Final[int] = 2  # ≥2 源同向才输出强信号
WEAK_SIGNAL_GAIN: Final[float] = 0.5  # 单源孤证降级增益
_DIRECTION_EPS: Final[float] = 1e-9  # 方向判定零区

# ── 投票强度标签 ──
STRENGTH_STRONG: Final[str] = "strong"  # ≥2 源同向
STRENGTH_WEAK: Final[str] = "weak"  # 单源孤证
STRENGTH_CONFLICT: Final[str] = "conflict"  # 多源冲突（正负互搏无多数）
STRENGTH_NONE: Final[str] = "none"  # 无输入 / 全中性


@dataclass(frozen=True, slots=True)
class SourceSentiment:
    """单条新闻的源级情感（聚合输入）。

    Attributes
    ----------
    source : 新闻源标识（eastmoney / cls / rss / ...；空串归 "unknown"）。
    polarity : 有向极性 [-1, 1]（nlp_inference SentimentResult.polarity）。
    publish_date : 聚合日键 'YYYY-MM-DD'。
    symbol : 关联标的/板块标签（可选，板块聚合用）。
    category : 语料四类标（announcement/research_report/macro_data/news，
        zephyr.data.news_taxonomy；空串归 "unknown" 桶，CAND-DAT-024）。
    """

    source: str
    polarity: float
    publish_date: str
    symbol: str = ""
    category: str = ""


@dataclass(frozen=True, slots=True)
class CrossSourceVote:
    """跨源一致性投票结果。

    strength : strong / weak / conflict / none（见模块常量）。
    score    : 软投票分 [-1, 1]；conflict/none → 0.0。
    direction: +1 / -1 / 0。
    """

    direction: int
    score: float
    strength: str
    n_sources: int
    n_agree: int
    source_polarities: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DailySentiment:
    """日级聚合情绪（13 号 Phase 7 按日聚合产物）。

    negative_count : 当日负面新闻计数——regime S2 ``s2_bad_news_flat_score``
        的 ``negative_count`` 入参（Phase 7 替换关键词字典 MVP 计数源）。
    vote_score     : 跨源一致性投票分 [-1, 1]（26 号 §2.5 event_score 的
        sentiment_score 维度候选）。
    """

    day: str
    n_news: int
    n_positive: int
    n_negative: int
    n_neutral: int
    negative_count: int
    mean_polarity: float
    vote_direction: int
    vote_score: float
    vote_strength: str
    symbol: str = ""
    # 四类分桶统计（CAND-DAT-024）：{category: {n_news, n_negative, mean_polarity}}
    # 媒体情绪（news 桶）与研报情绪（research_report 桶）分开读，防研报多头腔污染
    per_category: dict[str, dict[str, Any]] = field(default_factory=dict)


def _clip_polarity(x: float) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(v):
        return 0.0
    return max(-1.0, min(1.0, v))


def _sign(x: float) -> int:
    if x > _DIRECTION_EPS:
        return 1
    if x < -_DIRECTION_EPS:
        return -1
    return 0


def vote_cross_source(
    items: Sequence[SourceSentiment],
    *,
    min_agree_sources: int = MIN_AGREE_SOURCES,
    weak_gain: float = WEAK_SIGNAL_GAIN,
) -> CrossSourceVote:
    """跨源一致性投票（26 号 §2.7 RavenPack 裁定施工化）。

    源内等权求均 polarity → 源方向 → 票决：
    - ``≥min_agree_sources`` 源同向且占多数 → 强信号 ``tanh(均值)``
    - 仅 1 源有方向（单源孤证）→ 弱信号 ``tanh(均值 × weak_gain)``
    - 多源冲突（正负互搏、无多数）/ 全中性 / 空输入 → 0.0

    Returns
    -------
    CrossSourceVote（空输入返回 strength="none" 零票，不抛异常）。
    """
    if not items:
        return CrossSourceVote(0, 0.0, STRENGTH_NONE, 0, 0, {})

    by_source: dict[str, list[float]] = {}
    for it in items:
        src = (it.source or "").strip() or "unknown"
        by_source.setdefault(src, []).append(_clip_polarity(it.polarity))

    source_mean = {s: sum(v) / len(v) for s, v in by_source.items()}
    n_sources = len(source_mean)
    mean_all = sum(source_mean.values()) / n_sources

    n_pos = sum(1 for m in source_mean.values() if m > _DIRECTION_EPS)
    n_neg = sum(1 for m in source_mean.values() if m < -_DIRECTION_EPS)

    # ≥2 源同向且占多数 → 强信号
    if n_pos >= min_agree_sources and n_pos > n_neg:
        return CrossSourceVote(1, math.tanh(mean_all), STRENGTH_STRONG, n_sources, n_pos, source_mean)
    if n_neg >= min_agree_sources and n_neg > n_pos:
        return CrossSourceVote(-1, math.tanh(mean_all), STRENGTH_STRONG, n_sources, n_neg, source_mean)

    directional = n_pos + n_neg
    if directional == 1:
        # 单源孤证 → 弱信号降级
        return CrossSourceVote(
            _sign(mean_all),
            math.tanh(mean_all * weak_gain),
            STRENGTH_WEAK,
            n_sources,
            1,
            source_mean,
        )
    if directional >= 2:
        # 多源冲突（正负互搏无多数）→ 无信号
        return CrossSourceVote(0, 0.0, STRENGTH_CONFLICT, n_sources, 0, source_mean)

    # 全部中性
    return CrossSourceVote(0, 0.0, STRENGTH_NONE, n_sources, 0, source_mean)


def _per_category_stats(group: list[SourceSentiment]) -> dict[str, dict[str, Any]]:
    """四类分桶统计（CAND-DAT-024）：空 category 归 "unknown" 桶。"""
    buckets: dict[str, list[float]] = {}
    for it in group:
        buckets.setdefault((it.category or "").strip() or "unknown", []).append(
            _clip_polarity(it.polarity)
        )
    return {
        cat: {
            "n_news": len(pols),
            "n_negative": sum(1 for p in pols if p < -_DIRECTION_EPS),
            "mean_polarity": sum(pols) / len(pols),
        }
        for cat, pols in sorted(buckets.items())
    }


def _aggregate_group(day: str, symbol: str, group: list[SourceSentiment]) -> DailySentiment:
    polarities = [_clip_polarity(it.polarity) for it in group]
    n_pos = sum(1 for p in polarities if p > _DIRECTION_EPS)
    n_neg = sum(1 for p in polarities if p < -_DIRECTION_EPS)
    n_neu = len(polarities) - n_pos - n_neg
    vote = vote_cross_source(group)
    return DailySentiment(
        day=day,
        n_news=len(group),
        n_positive=n_pos,
        n_negative=n_neg,
        n_neutral=n_neu,
        negative_count=n_neg,
        mean_polarity=sum(polarities) / len(polarities),
        vote_direction=vote.direction,
        vote_score=vote.score,
        vote_strength=vote.strength,
        symbol=symbol,
        per_category=_per_category_stats(group),
    )


def aggregate_daily(items: Sequence[SourceSentiment]) -> list[DailySentiment]:
    """按日聚合（13 号 Phase 7 主口径：全市场日级情绪）。

    Returns
    -------
    list[DailySentiment] —— 按 day 升序；空输入返回空列表。
    """
    by_day: dict[str, list[SourceSentiment]] = {}
    for it in items:
        by_day.setdefault(it.publish_date, []).append(it)
    return [_aggregate_group(day, "", grp) for day, grp in sorted(by_day.items())]


def aggregate_daily_by_symbol(items: Sequence[SourceSentiment]) -> list[DailySentiment]:
    """按 (日, 标的/板块) 聚合（13 号 Phase 7 板块口径）。

    ``symbol`` 为空的记录归入 "" 组。返回按 (day, symbol) 升序；空输入返回空列表。
    """
    by_key: dict[tuple[str, str], list[SourceSentiment]] = {}
    for it in items:
        by_key.setdefault((it.publish_date, it.symbol), []).append(it)
    return [_aggregate_group(day, sym, grp) for (day, sym), grp in sorted(by_key.items())]


def to_negative_count_series(daily: Sequence[DailySentiment]) -> pd.Series:
    """DailySentiment → negative_count 日序列（DatetimeIndex）。

    桥接 regime S2 ``s2_bad_news_flat_score(negative_count, ...)``
    （overlay_features.py，Phase 7 用本聚合产物替换关键词字典 MVP 计数源）。
    空输入返回空 Series。
    """
    if not daily:
        return pd.Series(dtype=float)
    idx = pd.to_datetime([d.day for d in daily])
    vals = [float(d.negative_count) for d in daily]
    return pd.Series(vals, index=idx, name="negative_count")


def source_sentiment_from_result(
    result: Any,
    *,
    source: str,
    publish_date: str,
    symbol: str = "",
) -> SourceSentiment:
    """从 nlp_inference SentimentResult（或含 polarity 的 dict/对象）构造聚合输入。

    鸭型消费：``result.polarity`` 或 ``result["polarity"]``；缺失 → 0.0。
    """
    if isinstance(result, dict):
        polarity = result.get("polarity", 0.0)
    else:
        polarity = getattr(result, "polarity", 0.0)
    return SourceSentiment(
        source=source,
        polarity=_clip_polarity(polarity),
        publish_date=publish_date,
        symbol=symbol,
    )


__all__: Final = [
    "MIN_AGREE_SOURCES",
    "WEAK_SIGNAL_GAIN",
    "STRENGTH_STRONG",
    "STRENGTH_WEAK",
    "STRENGTH_CONFLICT",
    "STRENGTH_NONE",
    "SourceSentiment",
    "CrossSourceVote",
    "DailySentiment",
    "vote_cross_source",
    "aggregate_daily",
    "aggregate_daily_by_symbol",
    "to_negative_count_series",
    "source_sentiment_from_result",
]
