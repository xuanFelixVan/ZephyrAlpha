# [BLUEPRINT] MOD-L02-014 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-12
# [MODULE] zephyr.factor.analysis.simple_factor_attribution
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas
# [CONSUMERS] decay_monitor(低贡献因子联动衰减复检)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——暴露与因子收益同期对齐; 残差=总PnL-因子归因和(不强制为零)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->空结果; 总PnL为0->contribution_ratio/explained_ratio置0
# [TESTS] tests/factor/test_simple_factor_attribution.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: factor_exposures(dict[factor_id, pd.Series] t日组合暴露) + benchmark_exposures(dict/float t日基准暴露) + factor_returns(dict[factor_id, pd.Series] t日因子截面收益) + total_pnl
# F1: attribute(Brinson式因子PnL分解: PnL_i=Σ_t (w_i,t - w_benchmark,t) × r_i,t)
# F2: 汇总(contribution_ratio=pnl_i/total_pnl; avg_active_exposure; residual=total-Σ; explained_ratio=Σ/total; 按pnl排序标记低贡献)
# O1: AttributionReport(rows按pnl降序 + residual + explained_ratio + low_contribution_factors)
# [/ALGO_FLOW]
"""25号memo §3.7#4 MVP 因子归因（SimpleFactorAttribution，MOD-L02-014）。

Brinson 式因子 PnL 分解，不依赖 Barra 基础设施（Phase 4.5 远期候选前的过渡方案）。
benchmark='csi300'（沪深300）。验证 §3.3 衰减监控的因子贡献与 §3.1 合成方法的
因子有效性；低贡献因子联动 §3.3 衰减复检。

归因公式：PnL_i = Σ_t (w_{i,t} - w_{benchmark,t}) × r_{i,t}
  w = t 日因子 i 的组合暴露，r = t 日因子 i 的截面收益。
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

__all__ = [
    "FactorAttributionRow",
    "AttributionReport",
    "attribute",
    "LOW_CONTRIBUTION_THRESHOLD",
]

LOW_CONTRIBUTION_THRESHOLD = 0.05  # |contribution_ratio|<5% → 低贡献标记


@dataclass(frozen=True)
class FactorAttributionRow:
    """单因子归因行。"""

    factor_id: str
    pnl: float
    contribution_ratio: float
    avg_active_exposure: float
    low_contribution: bool


@dataclass(frozen=True)
class AttributionReport:
    """归因报告（按 pnl 降序）。"""

    rows: tuple[FactorAttributionRow, ...]
    total_pnl: float
    attributed_pnl: float
    residual: float
    explained_ratio: float
    low_contribution_factors: tuple[str, ...] = field(default_factory=tuple)


def attribute(
    factor_exposures: dict[str, pd.Series],
    factor_returns: dict[str, pd.Series],
    total_pnl: float,
    benchmark_exposures: dict[str, pd.Series | float] | None = None,
) -> AttributionReport:
    """Brinson 式因子 PnL 分解。

    Args:
        factor_exposures: factor_id → t 日组合暴露 w_{i,t}（pd.Series）
        factor_returns: factor_id → t 日因子截面收益 r_{i,t}（pd.Series，index 对齐）
        total_pnl: 组合总 PnL（残差 = total - 因子归因和）
        benchmark_exposures: factor_id → 基准暴露（标量或 Series）；None→0（纯主动暴露）

    Returns:
        AttributionReport。空输入返回全零报告。
    """
    benchmark_exposures = benchmark_exposures or {}
    rows: list[FactorAttributionRow] = []
    attributed = 0.0
    for fid, w in factor_exposures.items():
        r = factor_returns.get(fid)
        if r is None or w.empty:
            continue
        bench = benchmark_exposures.get(fid, 0.0)
        active = w - bench
        common = active.index.intersection(r.dropna().index)
        if len(common) == 0:
            continue
        pnl_i = float((active.loc[common] * r.loc[common]).sum())
        avg_active = float(active.loc[common].mean())
        attributed += pnl_i
        ratio = pnl_i / total_pnl if abs(total_pnl) > 1e-12 else 0.0
        rows.append(
            FactorAttributionRow(
                factor_id=fid,
                pnl=pnl_i,
                contribution_ratio=ratio,
                avg_active_exposure=avg_active,
                low_contribution=abs(ratio) < LOW_CONTRIBUTION_THRESHOLD,
            )
        )
    rows.sort(key=lambda x: x.pnl, reverse=True)
    residual = float(total_pnl) - attributed
    explained = attributed / total_pnl if abs(total_pnl) > 1e-12 else 0.0
    return AttributionReport(
        rows=tuple(rows),
        total_pnl=float(total_pnl),
        attributed_pnl=attributed,
        residual=residual,
        explained_ratio=explained,
        low_contribution_factors=tuple(r.factor_id for r in rows if r.low_contribution),
    )
