# [BLUEPRINT] MOD-SIG-142 | docs/03_modules/_domain_signal/sector_strength_aggregator/blueprint.md
# [MODULE] zephyr.signal_ashare.core.sector_strength_aggregator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（纯函数聚合核，零 IO；四路子分与市场级调节由调用方注入——子分产出=sector_analyzer/sector_ranking_engine/sector_momentum/sector_breadth（L2-01-1~4 已锚定件），市场级调节=market_forecast_fusion（L2-01-5 已锚定件））
# [CONSUMERS] TDM-E-L2-01（板块强度综合）；TDM-E-L2-06 板块个股传导（强度调节分上游，待接线）；TDM-E-L3 板块候选池（Top-15% 消费，待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 四路等权合成（0.25×4，最大熵默认=量化社区无 IC 证据时的标准起步，weights 可注入重加权）；市场级调节为加法 delta ∈[-10,+10] 注入后 clamp [0,100]; 输入越界/缺失维度/NaN → SectorStrengthInputError（fail-closed）; 候选池截取 ratio ∈ (0,1]，Top-N=ceil(N×ratio) 并保证 ≥1 个; 同输入必同输出（frozen+纯函数）; 权重与阈值为 proposed 待 IC 数据重加权（晨审 L2-01 定性"聚合公式需权重裁定"的落地=等权先验+显式可配置）
# [MODIFY-GUARD] 地图节点 TDM-E-L2-01
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 子分缺失/负值/非有限/权重不归一 → SectorStrengthInputError（fail-closed）
# [TESTS] tests/signal_ashare/sector/test_sector_strength_aggregator.py
# [TTL] permanent
"""SectorStrengthAggregator — 板块强度四路合分（MOD-SIG-142，TDM-E-L2-01）。

节点语义（TDM-E-L2-01 algo_note 逐条对码）：
    四路合分：结构强度（子1）+动量活跃（子2）+多周期动量（子3）+资金流（子4），
    再加市场级调节（子5）。总分进前 15% 的板块进候选池。

子分全部由调用方注入（L2-01-1~5 已锚定件各自产出），本件只做：
    composite = clamp(Σ w_i × 子分_i + market_adjustment, 0, 100)
    候选池 = composite 降序 Top-ceil(N×15%)（保底 1 个）

晨审定性（st-tdm-review-20260911 §7.1 前批）：聚合公式需权重裁定——本件的裁定
（night-gw-2300 架构师自裁，Owner 授权"自行裁定"令）：等权 0.25×4 为最大熵先验
（量化社区无 IC 证据时的标准起步），显式 weights 参数可注入，IC 数据积累后按
标准 IC 加权重校（对齐 L3-07-2 multifactor_synthesis 的 IC 加权惯例）。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Final, Sequence

#: 默认四路等权（proposed，IC 数据积累后重加权）
DEFAULT_WEIGHTS: Final[tuple[float, float, float, float]] = (0.25, 0.25, 0.25, 0.25)
#: 候选池截取比例（节点真源：总分进前 15%）
CANDIDATE_POOL_RATIO: Final = 0.15
#: 市场级调节幅度上限（|delta| ≤ 10 分）
MARKET_ADJUSTMENT_MAX: Final = 10.0


class SectorStrengthInputError(ValueError):
    """输入非法（子分缺失/负值/非有限、权重不归一）——fail-closed。"""


@dataclass(frozen=True)
class SectorStrength:
    """单板块四路合分输出（frozen，JSON 可序列化经 to_dict）。"""

    sector: str
    structure_score: float  # 结构强度（L2-01-1 sector_analyzer）
    momentum_activity: float  # 动量活跃（L2-01-2 sector_ranking_engine）
    multi_period_momentum: float  # 多周期动量（L2-01-3 sector_momentum）
    capital_flow: float  # 资金流（L2-01-4 sector_breadth）
    market_adjustment: float  # 市场级调节（L2-01-5 market_forecast_fusion 注入）
    composite: float  # 合分（clamp [0,100] 后）
    in_candidate_pool: bool = False  # 是否进前 15% 候选池（跨板块排名后回填）

    def to_dict(self) -> dict:
        return {
            "sector": self.sector,
            "structure_score": self.structure_score,
            "momentum_activity": self.momentum_activity,
            "multi_period_momentum": self.multi_period_momentum,
            "capital_flow": self.capital_flow,
            "market_adjustment": self.market_adjustment,
            "composite": self.composite,
            "in_candidate_pool": self.in_candidate_pool,
        }


def _validate_score(v: float, what: str) -> float:
    fv = float(v)
    if not math.isfinite(fv):
        raise SectorStrengthInputError(f"{what} 非有限: {v!r}")
    if fv < 0.0:
        raise SectorStrengthInputError(f"{what} 为负: {v!r}")
    return fv


def aggregate_sector_strength(
    sector: str,
    structure_score: float,
    momentum_activity: float,
    multi_period_momentum: float,
    capital_flow: float,
    market_adjustment: float = 0.0,
    weights: tuple[float, float, float, float] = DEFAULT_WEIGHTS,
) -> SectorStrength:
    """四路合分主入口（单板块）。

    Args:
        sector: 板块名。
        structure_score / momentum_activity / multi_period_momentum / capital_flow:
            四路子分（0-100，调用方从 L2-01-1~4 已锚定件取得）。
        market_adjustment: 市场级调节 delta（-10..+10，来自 L1-AGG/market_forecast_fusion）。
        weights: 四路权重（须归一，默认等权 0.25×4）。

    Returns:
        SectorStrength（frozen，composite 已 clamp [0,100]）。

    Raises:
        SectorStrengthInputError: 板块名空/子分负值或非有限/权重不归一/调节越界。
    """
    if not sector or not str(sector).strip():
        raise SectorStrengthInputError("板块名为空")
    scores = [
        _validate_score(structure_score, "结构强度"),
        _validate_score(momentum_activity, "动量活跃"),
        _validate_score(multi_period_momentum, "多周期动量"),
        _validate_score(capital_flow, "资金流"),
    ]
    if any(not math.isfinite(w) or w < 0 for w in weights):
        raise SectorStrengthInputError(f"权重非法: {weights!r}")
    w_total = sum(weights)
    if abs(w_total - 1.0) > 1e-6:
        raise SectorStrengthInputError(f"权重不归一: sum={w_total!r}")
    adj = float(market_adjustment)
    if not math.isfinite(adj):
        raise SectorStrengthInputError(f"市场调节非有限: {market_adjustment!r}")
    adj = max(-MARKET_ADJUSTMENT_MAX, min(MARKET_ADJUSTMENT_MAX, adj))
    raw = sum(w * s for w, s in zip(weights, scores)) + adj
    composite = max(0.0, min(100.0, raw))
    return SectorStrength(
        sector=sector,
        structure_score=scores[0],
        momentum_activity=scores[1],
        multi_period_momentum=scores[2],
        capital_flow=scores[3],
        market_adjustment=adj,
        composite=composite,
    )


def select_candidate_pool(
    strengths: Sequence[SectorStrength],
    ratio: float = CANDIDATE_POOL_RATIO,
) -> list[SectorStrength]:
    """跨板块排名取 Top-ratio 候选池（保底 1 个；composite 降序，平分按板块名稳定序）。

    Returns:
        全量 SectorStrength 列表（composite 降序），前 n_pool 个 in_candidate_pool=True。
    """
    if not 0.0 < ratio <= 1.0:
        raise SectorStrengthInputError(f"候选池比例非法: {ratio!r}")
    if not strengths:
        return []
    ranked = sorted(
        strengths,
        key=lambda s: (-s.composite, s.sector),
    )
    n_pool = max(1, math.ceil(len(ranked) * ratio))
    out: list[SectorStrength] = []
    for i, s in enumerate(ranked):
        out.append(
            SectorStrength(
                sector=s.sector,
                structure_score=s.structure_score,
                momentum_activity=s.momentum_activity,
                multi_period_momentum=s.multi_period_momentum,
                capital_flow=s.capital_flow,
                market_adjustment=s.market_adjustment,
                composite=s.composite,
                in_candidate_pool=i < n_pool,
            )
        )
    return out


def build_sector_strengths(
    rows: Sequence[dict],
    weights: tuple[float, float, float, float] = DEFAULT_WEIGHTS,
) -> list[SectorStrength]:
    """批量聚合（rows: 含 sector/structure_score/momentum_activity/multi_period_momentum/capital_flow/market_adjustment 键的字典序列）。"""
    out = []
    for r in rows:
        out.append(
            aggregate_sector_strength(
                sector=str(r["sector"]),
                structure_score=float(r["structure_score"]),
                momentum_activity=float(r["momentum_activity"]),
                multi_period_momentum=float(r["multi_period_momentum"]),
                capital_flow=float(r["capital_flow"]),
                market_adjustment=float(r.get("market_adjustment", 0.0)),
                weights=weights,
            )
        )
    return select_candidate_pool(out)
