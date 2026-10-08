# [BLUEPRINT] MOD-SIG-160 | docs/03_modules/_domain_signal/source_line_news_sentiment_criterion/blueprint.md
# [MODULE] zephyr.signal_ashare.source_line.news_sentiment_criterion
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] TDM-E-L9-A09（源线·财经快讯情绪，decision_question="快讯流密度与情感能否量化情绪并预测次日？"；module_ref 挂载=总裁终裁批，本件先按源线判据口径落码）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数核零 IO（快讯时戳/情感分序列与 as_of 由调用方注入）; PIT=快讯时戳不可回填——ts>as_of 一律 fail-closed（NewsSentimentInputError），聚合窗口右闭 (as_of-window, as_of]; sentiment_index ∈ [-1,1] 单值输出; 密度突增须双条件（比值或绝对地板）防稀疏假突增; 空窗=合法静默态记 notes 判 NONE 不编方向; 同输入必同输出（零墙钟零随机）; 与 news_sentiment_analyzer（MOD 系智能体文本打分层）正交——本件输出源线级窗口判据非文本打分器
# [MODIFY-GUARD] 地图节点 TDM-E-L9-A09（本班禁改 trading_decision_map.yaml，module_ref 挂载待总裁终裁）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未来时戳/情感分越界/快讯族空 → NewsSentimentInputError；当前窗零快讯 → NONE 记 notes
# [TESTS] tests/signal_ashare/source_line/test_news_sentiment_criterion.py
# [TTL] permanent
"""NewsSentimentCriterion — A09 财经快讯情绪源线判据转化器（MOD-SIG-160）。

# [ALGO_FLOW] external: docs/03_modules/_domain_signal/algo_flow/source_line/news_sentiment_criterion.yaml
TDM-E-L9-A09「源线·财经快讯情绪」的 decision_question：
    快讯流密度与情感能否量化情绪并预测次日？

本件把快讯流（DS-104 财联社 / DS-107 东财快讯 / RSS，时戳+情感分 ∈[-1,1]，
情感分可由调用方接 news_sentiment_analyzer 文本打分层产出）转化为三段判据：

    1. 窗口情绪指数（sentiment_index）：右闭窗 (as_of-w, as_of] 内按新近度
       半衰加权均值 ∈ [-1,1]（快讯衰减快，新讯权重高）；
    2. 密度突增（density_burst）：当前窗计数 / 前等长窗计数 ≥2.0，或当前窗
       绝对计数 ≥5（前窗零基准时的地板，防稀疏单条假突增）；
    3. 情绪档（sentiment_tier）：index ≥+0.5 → POSITIVE_SPIKE；≤-0.5 →
       NEGATIVE_SPIKE；|index| ≥0.2 → WATCH；其余 NONE。
       "预测次日"为消费方（日频策略面）的落地语义，本件只量化当窗情绪态。

PIT 纪律（A09 节点 algo_note：快讯时戳不可回填，聚合窗口须右闭）：
ts > as_of 一律 fail-closed（未来泄露禁入）；窗边界 (as_of-w, as_of]——
恰等于 as_of 的快讯入窗，恰等于 as_of-w 的旧讯出窗。

与既有件的正交性：news_sentiment_analyzer（intelligence 域文本打分层，
单条新闻 → 情感分）与本件（窗口流 → 判据档）问句不同不并；
market_sentiment_analyzer（MOD-SIG-025 价格行为情绪）口径不同不并。
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Final

#: 情绪窗口（分钟，A09 realtime 时滞口径对齐待标定）
DEFAULT_WINDOW_MINUTES: Final = 60

#: 新近度半衰（分钟）：快讯热度衰减快，初拟 120min 待标定
DEFAULT_HALF_LIFE_MINUTES: Final = 120.0

#: 情绪档阈值（初拟待标定）
SPIKE_ABS_MIN: Final = 0.5
WATCH_ABS_MIN: Final = 0.2

#: 密度突增双条件：比值门 / 绝对地板门（前窗零基准时启用地板）
DENSITY_BURST_RATIO: Final = 2.0
DENSITY_BURST_FLOOR: Final = 5


class NewsSentimentInputError(ValueError):
    """输入非法（未来时戳/情感分越界/快讯族空）——fail-closed。"""


class SentimentTier:
    """快讯情绪四档（值即输出标签）。"""

    POSITIVE_SPIKE = "POSITIVE_SPIKE"  # 高位正情绪：次日情绪面偏多预期
    NEGATIVE_SPIKE = "NEGATIVE_SPIKE"  # 高位负情绪：次日情绪面偏空预期
    WATCH = "WATCH"  # 中度情绪，未达尖峰阈
    NONE = "NONE"


@dataclass(frozen=True)
class NewsSentimentSnapshot:
    """单市场/标的快讯情绪判据快照（JSON 可序列化经 to_dict）。"""

    as_of: object  # 透传（datetime/epoch 均可，调用方口径）
    window_minutes: int
    sentiment_index: float | None  # None=当前窗零快讯（合法静默态）
    window_count: int
    prev_window_count: int
    density_burst: bool
    sentiment_tier: str  # SentimentTier 四档
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """全基本类型字典（json.dumps 直序列化）。"""
        return {
            "as_of": str(self.as_of),
            "window_minutes": self.window_minutes,
            "sentiment_index": self.sentiment_index,
            "window_count": self.window_count,
            "prev_window_count": self.prev_window_count,
            "density_burst": self.density_burst,
            "sentiment_tier": self.sentiment_tier,
            "notes": list(self.notes),
        }


def _age_minutes(as_of: object, ts: object) -> float:
    """时戳年龄（分钟）：datetime 减法或数值 epoch 均支持（同调用内口径一致）。"""
    delta = as_of - ts
    if isinstance(delta, timedelta):
        return delta.total_seconds() / 60.0
    return float(delta) / 60.0


def classify_sentiment_tier(sentiment_index: float, density_burst: bool) -> str:
    """窗口情绪指数 → 情绪四档（阈值初拟待标定）。

    尖峰档不要求 density_burst（单条重磅快讯可拉满指数）；burst 信息由
    snapshot 字段透传给消费方加权。
    """
    if sentiment_index >= SPIKE_ABS_MIN:
        return SentimentTier.POSITIVE_SPIKE
    if sentiment_index <= -SPIKE_ABS_MIN:
        return SentimentTier.NEGATIVE_SPIKE
    if abs(sentiment_index) >= WATCH_ABS_MIN:
        return SentimentTier.WATCH
    return SentimentTier.NONE


def build_news_sentiment_snapshot(
    items: Sequence[tuple[object, float]],
    as_of: object,
    *,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
    half_life_minutes: float = DEFAULT_HALF_LIFE_MINUTES,
) -> NewsSentimentSnapshot:
    """主入口：快讯（时戳, 情感分）序列 + as_of → A09 判据快照。

    Args:
        items: （时戳, 情感分 ∈[-1,1]）序列（乱序可，内部按需过滤；DS-104/
            DS-107 CH 表由调用方读取注入，时戳不可回填）。
        as_of: 判据锚点时戳（右闭窗上沿；datetime 或数值 epoch）。
        window_minutes: 情绪窗口长（分钟，默认 60）。
        half_life_minutes: 新近度半衰（分钟，默认 120）。

    Returns:
        NewsSentimentSnapshot（frozen）。

    Raises:
        NewsSentimentInputError: 快讯族空/情感分越界/ts>as_of（未来泄露
            fail-closed——A09 PIT 纪律：快讯时戳不可回填）。
    """
    if not items:
        raise NewsSentimentInputError("快讯族为空")
    if half_life_minutes <= 0.0:
        raise NewsSentimentInputError(f"半衰非法: {half_life_minutes} 必须 >0")

    notes: list[str] = []
    win: list[tuple[float, float]] = []  # (age_minutes, score)
    prev_cnt = 0
    for i, (ts, raw_score) in enumerate(items):
        score = float(raw_score)
        if not math.isfinite(score) or not -1.0 <= score <= 1.0:
            raise NewsSentimentInputError(f"情感分越界: idx={i} value={raw_score!r}")
        age = _age_minutes(as_of, ts)
        if age < 0.0:
            raise NewsSentimentInputError(
                f"未来时戳泄露: idx={i} ts={ts!r} 晚于 as_of={as_of!r}（A09 PIT：快讯时戳不可回填，fail-closed）"
            )
        if age < window_minutes:
            win.append((age, score))
        elif age <= 2 * window_minutes:
            prev_cnt += 1

    if not win:
        return NewsSentimentSnapshot(
            as_of=as_of,
            window_minutes=window_minutes,
            sentiment_index=None,
            window_count=0,
            prev_window_count=prev_cnt,
            density_burst=False,
            sentiment_tier=SentimentTier.NONE,
            notes=["当前窗零快讯（合法静默态），不编方向"],
        )

    weight_sum = 0.0
    weighted = 0.0
    for age, score in win:
        w = 0.5 ** (age / half_life_minutes)
        weight_sum += w
        weighted += w * score
    index = weighted / weight_sum
    index = max(-1.0, min(1.0, index))

    cnt = len(win)
    if prev_cnt > 0:
        burst = cnt / prev_cnt >= DENSITY_BURST_RATIO
    else:
        burst = cnt >= DENSITY_BURST_FLOOR
        if cnt > 0 and prev_cnt == 0:
            notes.append(f"前窗零快讯，突增启用绝对地板门（≥{DENSITY_BURST_FLOOR} 条）")
    tier = classify_sentiment_tier(index, burst)
    return NewsSentimentSnapshot(
        as_of=as_of,
        window_minutes=window_minutes,
        sentiment_index=index,
        window_count=cnt,
        prev_window_count=prev_cnt,
        density_burst=burst,
        sentiment_tier=tier,
        notes=notes,
    )


def build_from_news_rows(
    rows: Sequence[Mapping],
    as_of: object,
    *,
    ts_key: str = "timestamp",
    score_key: str = "sentiment",
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
    half_life_minutes: float = DEFAULT_HALF_LIFE_MINUTES,
) -> NewsSentimentSnapshot:
    """DS 读入形态入口：新闻行字典序列（timestamp/sentiment）→ 判据快照。

    标准化：缺 ts/score 或值非法的行 fail-closed（行级缺陷在此件属上游
    打分契约破裂，与 sector_rotation 缺行情行跳过口径不同——新闻缺情感分
    意味着打分层漏单，静默跳过会系统性偏置指数，故逐行硬失败）。
    """
    items: list[tuple[object, float]] = []
    for i, raw in enumerate(rows):
        try:
            ts = raw[ts_key]
            score = float(raw[score_key])
        except (KeyError, TypeError, ValueError) as e:
            raise NewsSentimentInputError(f"新闻行缺陷: idx={i} 缺 {ts_key}/{score_key} 或值非法（{e}）") from e
        items.append((ts, score))
    return build_news_sentiment_snapshot(
        items,
        as_of,
        window_minutes=window_minutes,
        half_life_minutes=half_life_minutes,
    )


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 永久模块最小自检入口（判据冒烟），主体经 zephyr 导入消费（消费方=TDM-E-L9-A09 挂载待总裁终裁）
    import argparse

    _ap = argparse.ArgumentParser(description="A09 判据转化器自检（无副作用冒烟）")
    _ap.add_argument("--selfcheck", action="store_true", help="跑一次合成快讯情绪判据冒烟")
    _args = _ap.parse_args()
    if _args.selfcheck:
        from datetime import datetime

        from zephyr.signal_ashare.source_line.news_sentiment_criterion import (
            build_news_sentiment_snapshot,
        )

        _as_of = datetime(2026, 10, 8, 10, 0)
        _items = [
            (datetime(2026, 10, 8, 9, 30), 0.9),
            (datetime(2026, 10, 8, 9, 50), 0.8),
            (datetime(2026, 10, 8, 8, 30), 0.6),
        ]
        _s = build_news_sentiment_snapshot(_items, _as_of)
        print(f"news_sentiment_criterion selfcheck: index={_s.sentiment_index:.3f} tier={_s.sentiment_tier}")
