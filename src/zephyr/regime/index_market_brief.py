# [BLUEPRINT] MOD-REGIME-008 | 待统筹登记（supplement：GAP-F-10 四指数分市场分析组合卡；主号=四指数 regime 面板 IDX-01）
# [MODULE] zephyr.regime.index_market_brief
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.signal_ashare.next_day_8state_forecast(build_state_series/forecast_next_day 参数化复用，MOD-SIG-037); zephyr.regime.index_regime_panel(IndexRegimePanel 鸭型消费，MOD-REGIME-008)
# [CONSUMERS] （候选：盘中实时页四指数卡——分指数 regime/情绪/预判）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 四指数清单=L14 裁定（000001 上证/399001 深成/399006 创业板指/000680 科创综指）；三腿独立降级（regime=MOD-REGIME-008 注入按裸码匹配缺卡留痕/预判=MOD-SIG-037 参数化每指数 8 态分布/情绪=市场共享注入四卡同值与"1 引擎×4 代理"语义一致）；90号§7铁律——只出概率分布不出点位/方向预测；全腿缺位面板级 degraded；输入校验 fail-closed；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-10 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] trade_date 非法→ValueError（fail-closed）；单指数单腿异常→该腿降级 notes 不炸面板
# [TESTS] tests/regime/test_index_market_brief.py
# [A_module] module_id=MOD-REGIME-008_brief | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-REGIME-008 supplement — 四指数分市场分析组合卡（GAP-F-10，盘中实时四指数卡后端）。

「1 引擎 × 4 代理」组合层（裁定一语义延伸，复用 regime 域产出）：
- **指数宇宙**（L14 Owner 裁定）：上证指数 000001 / 深证成指 399001 /
  创业板指 399006 / 科创综指 000680（科创50→科创综指已纠正）。
- **regime 腿**：MOD-REGIME-008 IndexRegimePanel 注入（按裸码匹配卡片）——
  概率分布+强弱位次；缺卡该指数 regime 字段 None+notes（不炸面板）。
- **预判腿**：MOD-SIG-037 参数化复用——同一 8 态马尔可夫引擎按各指数自身
  日 K 序列出次日 8 态概率分布（90号§7铁律：只出分布不出点位）；历史不足
  （<min_history+1 根）该腿降级 notes。
- **情绪腿**：市场情绪为共享环境维度（与 MOD-REGIME-008 F3/F4 同语义——
  同一市场环境不同指数载体），注入单值四卡同值透传；指数特异强弱由
  regime 面板 strength_ranking 承载。
三腿独立降级；全腿缺位 → 面板级 degraded。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 IndexRegimePanel（regime 腿，可 None）
# - id: I2 各指数日 K dict[code → bars]（预判腿，可 None）
# - id: I3 市场情绪 label/score（共享注入，可 None）
# 层: 算法
# - id: A1 裸码匹配 regime 卡
# - id: A2 每指数 8 态预判（MOD-SIG-037 引擎）
# 层: 输出
# - id: O1 IndexMarketBrief（4 张 IndexBriefCard + 强弱序 + 情绪）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1,A2,I3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Final, Mapping, Sequence

from zephyr.signal_ashare.next_day_8state_forecast import (
    build_state_series,
    forecast_next_day,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "FOUR_INDEX_CODES",
    "IndexBriefCard",
    "IndexBriefConfig",
    "IndexMarketBrief",
    "build_index_market_brief",
]

#: L14 裁定四指数（裸码；科创50→科创综指 000680 已纠正）
FOUR_INDEX_CODES: Final[tuple[str, str, str, str]] = ("000001", "399001", "399006", "000680")

_INDEX_NAMES: Final[dict[str, str]] = {
    "000001": "上证指数",
    "399001": "深证成指",
    "399006": "创业板指",
    "000680": "科创综指",
}


@dataclass(frozen=True, slots=True)
class IndexBriefConfig:
    """组合卡配置。"""

    index_codes: tuple[str, ...] = FOUR_INDEX_CODES
    min_forecast_history: int = 30  # 预判腿最少状态序列（对齐 MOD-SIG-037 min_history）


@dataclass(frozen=True, slots=True)
class IndexBriefCard:
    """单指数分市场分析卡（regime/情绪/预判三腿，观测层消费）。"""

    code: str
    name: str
    regime_dominant: str | None = None
    regime_confidence: float | None = None
    regime_probs: dict[str, float] | None = None
    strength_rank: int | None = None
    forecast_top_state: str | None = None
    forecast_top_probability: float | None = None
    forecast_confidence: float | None = None
    forecast_probs: dict[str, float] | None = None
    sentiment_label: str | None = None
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class IndexMarketBrief:
    """四指数分市场分析输出（盘中实时页消费，不接交易）。"""

    trade_date: str
    cards: list[IndexBriefCard] = field(default_factory=list)
    strength_ranking: tuple[str, ...] = ()
    market_sentiment_label: str | None = None
    market_sentiment_score: float | None = None
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 组合主核（纯函数；panel/bars 注入）
# ------------------------------------------------------------------


def _bare(code: str) -> str:
    c = str(code).strip()
    if "." in c:
        c = c.split(".")[0]
    return c


def _regime_leg(panel: Any | None, code: str) -> tuple[str | None, float | None, dict[str, float] | None, int | None, str | None]:
    """regime 卡裸码匹配 → (dominant, confidence, probs, rank, note)。"""
    if panel is None:
        return None, None, None, None, "regime 面板未注入，regime 腿降级"
    for card in getattr(panel, "cards", ()):
        if _bare(getattr(card, "code", "")) == code:
            if getattr(card, "degraded", False):
                return None, None, None, None, "regime 面板该卡降级"
            return (
                getattr(card, "dominant_regime", None),
                getattr(card, "confidence", None),
                dict(getattr(card, "probabilities", {}) or {}) or None,
                getattr(card, "rank", None),
                None,
            )
    return None, None, None, None, "regime 面板无该指数卡，regime 腿降级"


def _forecast_leg(bars: Sequence[Any] | None, cfg: IndexBriefConfig) -> tuple[str | None, float | None, float | None, dict[str, float] | None, str | None]:
    """8 态预判（MOD-SIG-037 参数化）→ (top_state, top_prob, confidence, probs, note)。"""
    if not bars:
        return None, None, None, None, "日 K 序列未供给，预判腿降级"
    try:
        states = build_state_series(bars)
        if len(states) < cfg.min_forecast_history:
            return None, None, None, None, f"历史不足（状态序列 {len(states)}<{cfg.min_forecast_history}），预判腿降级"
        fc = forecast_next_day(states)
        probs = {k.value: v for k, v in fc.probabilities.items()}  # 透传保 Σ=1 不变量（舍入会破坏）
        return fc.top_state.value, round(fc.top_probability, 6), round(fc.confidence, 6), probs, None
    except (ValueError, AttributeError, TypeError) as exc:
        return None, None, None, None, f"预判腿计算异常降级: {exc!r}"


def build_index_market_brief(
    trade_date: str | date | datetime,
    panel: Any | None,
    index_bars: Mapping[str, Sequence[Any]] | None,
    sentiment_label: str | None = None,
    sentiment_score: float | None = None,
    config: IndexBriefConfig | None = None,
) -> IndexMarketBrief:
    """四指数分市场分析组合主核（纯函数，不触库）。

    Args:
        trade_date: 面板日（YYYY-MM-DD，fail-closed）。
        panel: MOD-REGIME-008 IndexRegimePanel 鸭型（None=regime 腿全降级）。
        index_bars: {裸码或 canonical: 日 K 序列}（MOD-SIG-037 DailyBar 鸭型；
            None=预判腿全降级）。
        sentiment_label/sentiment_score: 市场情绪共享注入（None=情绪腿缺位）。
        config: 配置（None 用默认）。

    Returns:
        IndexMarketBrief；四卡全降级 → 面板级 degraded。

    Raises:
        ValueError: trade_date 非法（fail-closed）。
    """
    if isinstance(trade_date, datetime):
        v_date = trade_date.date().isoformat()
    elif isinstance(trade_date, date):
        v_date = trade_date.isoformat()
    else:
        if not isinstance(trade_date, str):
            raise ValueError(f"trade_date 非法（须 YYYY-MM-DD 字符串）: {trade_date!r}")
        try:
            date.fromisoformat(trade_date)
        except ValueError as exc:
            raise ValueError(f"trade_date 非真实日期: {trade_date!r}") from exc
        v_date = trade_date
    cfg = config or IndexBriefConfig()
    bars_map = {_bare(k): v for k, v in (index_bars or {}).items()}

    cards: list[IndexBriefCard] = []
    for code in cfg.index_codes:
        dominant, conf, probs, rank, note_r = _regime_leg(panel, code)
        top_state, top_prob, fc_conf, fc_probs, note_f = _forecast_leg(bars_map.get(code), cfg)
        notes = [n for n in (note_r, note_f) if n]
        degraded = dominant is None and top_state is None
        cards.append(
            IndexBriefCard(
                code=code,
                name=_INDEX_NAMES.get(code, code),
                regime_dominant=dominant,
                regime_confidence=conf,
                regime_probs=probs,
                strength_rank=rank,
                forecast_top_state=top_state,
                forecast_top_probability=top_prob,
                forecast_confidence=fc_conf,
                forecast_probs=fc_probs,
                sentiment_label=sentiment_label,
                degraded=degraded,
                notes=notes,
            )
        )
    ranking: tuple[str, ...] = ()
    if panel is not None:
        ranking = tuple(_bare(c) for c in getattr(panel, "strength_ranking", ()) or ())
    all_degraded = all(c.degraded for c in cards)
    panel_notes: list[str] = []
    if all_degraded:
        panel_notes.append("四指数 regime/预判双腿全缺位，面板级降级")
    return IndexMarketBrief(
        trade_date=v_date,
        cards=cards,
        strength_ranking=ranking,
        market_sentiment_label=sentiment_label,
        market_sentiment_score=sentiment_score,
        degraded=all_degraded,
        notes=panel_notes,
    )
