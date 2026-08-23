# [BLUEPRINT] MOD-SIG-048 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.6
# [MODULE] zephyr.signal_ashare.fine_scoring_engine
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none（密度摘要按鸭子类型消费，与 conditional_density_predictor 解耦）
# [CONSUMERS] zephyr.signal_ashare.event_driven_screener
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 输出 Top-N 按 z_score 降序；kept ≤ top_n；regime_shift 截断 ±0.10；8 态修正暂缓置 0；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] top_n<=0 或空输入 → 空结果；密度摘要缺字段 → AttributeError 由调用方兜底（装配层职责）
# [TESTS] tests/signal_ashare/test_fine_scoring_engine.py
# [A_module] module_id=MOD-SIG-048 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: FineScoreRecord（四维基础分/状态偏移/主力分/拥挤度/密度摘要/8态分）
# A1: 六要素合成——基础评分(价值40/动量30/质量20/情绪10)×(1+状态偏移±10%) + 主力×0.20 − 拥挤×0.10 − 密度×0.15（8态置0）
# A2: 密度要素——density_penalty = 负偏度×10 + 超额峰度×5 + 前瞻VaR%（消费 BM-SEL-13 密度摘要）
# A3: 横截面 Z-score 标准化 → 降序 Top-N（std≈0 时 Z 置 0 按 raw 兜底排名）
# O1: FineScoreResult(top: ScoredEntry(symbol/raw_score/z_score/rank), degraded)
# [/ALGO_FLOW]
"""选股漏斗第三层——精筛评分（BM-SEL-18，~300→~50）。

六要素综合评分（21 号 memo §3.6 ③ 契约）：基础评分（价值 40%/动量 30%/质量 20%/
情绪 10%）×(1+状态偏移 ±10%) + 主力评分 ×0.20 − 拥挤度 ×0.10 − 密度要素 ×0.15
+ 8 态修正（90 号 §7 暂缓，置 0 不参与）。横截面 Z-score 标准化后降序取 Top ~50，
喂 BM-SEL-19 事件驱动筛选 / sleeve 排序。

密度要素按鸭子类型消费：任何带 neg_skewness / excess_kurtosis / forward_var_pct
三属性的摘要对象均可（BM-SEL-13 conditional_density_predictor 的分布派生量是其
一），本模块不 import 密度预测实现，保持漏斗层与模型层解耦。

降级：精筛未就绪 → 等权综合评分（degraded=True）。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

__all__: Final = [
    "FineScoreConfig",
    "FineScoreRecord",
    "FineScoreResult",
    "ScoredEntry",
    "compute_density_penalty",
    "composite_raw_score",
    "score_fine",
]


@dataclass(frozen=True)
class FineScoreConfig:
    """六要素合成权重（memo §3.6 ③ 契约值；主力/拥挤/密度权重为经验初值，G09 校准）。

    Attributes:
        weight_value / weight_momentum / weight_quality / weight_sentiment: 基础评分四维权重
        regime_shift_max: 状态偏移修正截断幅度（±10%，C-021）
        weight_main_force: 主力评分合成权重（C-034/C-035）
        weight_crowding: 拥挤度扣分权重（C-045）
        weight_density: 密度要素扣分权重（memo 定值 15%）
        weight_eight_state: 8 态修正权重（90 号 §7 暂缓 → 0.0）
    """

    weight_value: float = 0.40
    weight_momentum: float = 0.30
    weight_quality: float = 0.20
    weight_sentiment: float = 0.10
    regime_shift_max: float = 0.10
    weight_main_force: float = 0.20
    weight_crowding: float = 0.10
    weight_density: float = 0.15
    weight_eight_state: float = 0.0


@dataclass(frozen=True)
class FineScoreRecord:
    """第三层精筛候选标的记录（各基础维 0-100 分）。"""

    symbol: str
    base_value_score: float = 50.0  # 价值分
    base_momentum_score: float = 50.0  # 动量分
    base_quality_score: float = 50.0  # 质量分
    base_sentiment_score: float = 50.0  # 情绪分
    regime_shift: float = 0.0  # 状态偏移修正（C-021，合成前截断 ±regime_shift_max）
    main_force_score: float = 50.0  # 主力评分（C-034/C-035）
    crowding_score: float = 0.0  # 拥挤度（越高越扣分，C-045）
    density: Any = None  # 密度摘要（鸭子类型：neg_skewness/excess_kurtosis/forward_var_pct）
    eight_state_score: float = 0.0  # 8 态修正（暂缓，默认置 0 不参与）


@dataclass(frozen=True)
class ScoredEntry:
    """单标的精筛评分结果。"""

    symbol: str
    raw_score: float  # 六要素合成原始分
    z_score: float  # 横截面 Z-score 标准化分
    rank: int  # 降序排名（1 起）


@dataclass(frozen=True)
class FineScoreResult:
    """第三层精筛输出。"""

    top: tuple[ScoredEntry, ...]  # Top-N（按 z_score 降序）
    degraded: bool = False  # True=降级路径（等权综合评分）


def compute_density_penalty(density: Any) -> float:
    """密度要素扣分项 = 负偏度幅度×10 + 超额峰度×5 + 前瞻 VaR 幅度%（memo §3.6 ③）。

    density 为 None 时返回 0.0（密度预测未就绪 → 密度要素不参与扣分，
    与 memo"8 态置 0"同构的缺省处理）。
    """
    if density is None:
        return 0.0
    return float(density.neg_skewness) * 10.0 + float(density.excess_kurtosis) * 5.0 + float(density.forward_var_pct)


def composite_raw_score(rec: FineScoreRecord, *, cfg: FineScoreConfig, degraded: bool) -> float:
    """六要素合成原始分。degraded=True → 等权综合（四维基础分+主力五维等权）。"""
    if degraded:
        return (
            rec.base_value_score
            + rec.base_momentum_score
            + rec.base_quality_score
            + rec.base_sentiment_score
            + rec.main_force_score
        ) / 5.0
    base = (
        cfg.weight_value * rec.base_value_score
        + cfg.weight_momentum * rec.base_momentum_score
        + cfg.weight_quality * rec.base_quality_score
        + cfg.weight_sentiment * rec.base_sentiment_score
    )
    shift = max(-cfg.regime_shift_max, min(cfg.regime_shift_max, rec.regime_shift))
    return (
        base * (1.0 + shift)
        + cfg.weight_main_force * rec.main_force_score
        - cfg.weight_crowding * rec.crowding_score
        - cfg.weight_density * compute_density_penalty(rec.density)
        + cfg.weight_eight_state * rec.eight_state_score
    )


def score_fine(
    records: list[FineScoreRecord],
    *,
    top_n: int = 50,
    config: FineScoreConfig | None = None,
    degraded: bool = False,
) -> FineScoreResult:
    """六要素综合评分 → 横截面 Z-score 标准化 → 降序取 Top-N（~300→~50）。

    Z-score：std≈0（全体同分）时 Z 全部置 0（无区分度，按 raw 降序兜底排名）。
    top_n<=0 或空输入 → 空结果。排名同分时按 symbol 字典序保证确定性。
    """
    cfg = config or FineScoreConfig()
    if not records or top_n <= 0:
        return FineScoreResult(top=(), degraded=degraded)
    raws = {r.symbol: composite_raw_score(r, cfg=cfg, degraded=degraded) for r in records}
    values = list(raws.values())
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(var)
    zs = {s: (0.0 if std < 1e-12 else (v - mean) / std) for s, v in raws.items()}
    ordered = sorted(raws, key=lambda s: (-zs[s], -raws[s], s))[:top_n]
    top = tuple(ScoredEntry(symbol=s, raw_score=raws[s], z_score=zs[s], rank=i + 1) for i, s in enumerate(ordered))
    return FineScoreResult(top=top, degraded=degraded)
