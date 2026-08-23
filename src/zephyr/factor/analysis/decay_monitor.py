# [BLUEPRINT] MOD-L02-009 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-08
# [MODULE] zephyr.factor.analysis.decay_monitor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.ic_decay; zephyr.factor.analysis.bhy_fdr; pandas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——衰减监控基于已实现IC衰减曲线
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据不足->DecayStatus(half_life=0, is_decaying=True)；相对轨道数据不足->RelativeTrackResult(quantile=NaN, passed=False)；min_quantile 越界->ValueError
# [TESTS] tests/factor/test_factor_decay_monitor.py
# [A_module] module_id=MOD-L02-009 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-ANA-08 衰减监控——监控因子 IC 衰减速度，半衰期低于阈值告警。

计算因子的 IC 半衰期，若低于配置的 min_half_life（默认10），标记为衰减中。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 因子ID与预计算IC衰减序列
#   fields: factor_id + ic_decay_series（可选，index=lag values=IC均值）
#   code: monitor_decay 函数参数
# - id: I2
#   name: 评估参数组
#   fields: symbols 标的池 + start/end 回测区间（无预计算序列时用于现算）
#   code: symbols/start/end 函数参数
# - id: I3
#   name: 最小半衰期阈值配置 float
#   fields: decay_monitor.min_half_life，默认 10（lag数）
#   code: _config.yaml L12-13
# 层: 算法
# - id: A1
#   name_zh: ① 因子衰减状态判定
#   name_en: monitor_decay
#   intro: 算IC半衰期并与阈值比较，低于阈值标记衰减过快
#   desc: 无序列则调 ic_decay.compute_ic_decay 现算 → compute_half_life 得半衰期 → half_life<min_hl 判 is_decaying 并生成趋势描述（L70-81）
#   inputs: I1 I2 I3
#   outputs: DecayStatus(factor_id, half_life, is_decaying, trend)
#   invariant: INV-004 PIT铁律——基于已实现IC衰减曲线；数据不足→half_life=0且is_decaying=True
# 层: 输出
# - id: O1
#   name_zh: 因子衰减状态 DecayStatus
#   name_en: DecayStatus
#   intro: 冻结dataclass：因子ID/半衰期/是否衰减中/趋势描述
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from zephyr.factor.analysis import load_analysis_config
from zephyr.factor.analysis.bhy_fdr import DEFAULT_Q, BHYFDRResult, bhy_fdr
from zephyr.factor.analysis.ic_decay import compute_half_life, compute_ic_decay


@dataclass(frozen=True)
class DecayStatus:
    """因子衰减状态。

    Attributes:
        factor_id: 因子ID
        half_life: IC 半衰期（lag 数）
        is_decaying: 是否衰减过快（半衰期 < 阈值）
        trend: 衰减趋势描述
        relative_quantile: 滚动分位相对轨道分位（90 号 §2 裁定②；None=未评估）
        relative_pass: 是否守前 50% 相对轨道（None=未评估）
    """

    factor_id: str
    half_life: float
    is_decaying: bool
    trend: str
    relative_quantile: float | None = None
    relative_pass: bool | None = None


def _get_min_half_life(default: int = 10) -> float:
    """从配置读取最小半衰期阈值。"""
    cfg = load_analysis_config()
    return float(cfg.get("decay_monitor", {}).get("min_half_life", default))


def monitor_decay(
    factor_id: str,
    ic_decay_series=None,
    symbols: list[str] | None = None,
    start: str = "",
    end: str = "",
    relative: RelativeTrackInput | None = None,
) -> DecayStatus:
    """监控因子 IC 衰减状态。

    Args:
        factor_id: 因子ID
        ic_decay_series: 预计算的 IC 衰减 Series（可选，省略则用 symbols/start/end 计算）
        symbols: 评估标的池（ic_decay_series 为 None 时使用）
        start: 回测起始日期
        end: 回测结束日期
        relative: 滚动分位相对轨道输入（90 号 §2 裁定②；None=不评估，向后兼容）

    Returns:
        DecayStatus
    """
    min_hl = _get_min_half_life()
    if ic_decay_series is None:
        if not symbols or not start or not end:
            return DecayStatus(factor_id, 0.0, True, "数据不足")
        ic_decay_series = compute_ic_decay(factor_id, symbols, start, end)
    half_life = compute_half_life(ic_decay_series)
    is_decaying = half_life < min_hl
    if is_decaying:
        trend = f"衰减过快（半衰期 {half_life:.1f} < {min_hl:.0f}）"
    else:
        trend = f"衰减正常（半衰期 {half_life:.1f} >= {min_hl:.0f}）"
    relative_quantile: float | None = None
    relative_pass: bool | None = None
    if relative is not None:
        track = rolling_relative_quantile(factor_id, relative)
        relative_quantile, relative_pass = track.quantile, track.passed
        trend += f"；{track.detail}"
    return DecayStatus(factor_id, half_life, is_decaying, trend, relative_quantile, relative_pass)


# ──────────────────────────────────────────────────────────────────────────────
# 90 号 Phase2 扩展（#2 因子IC 双轨采纳：滚动分位相对轨道 + BHY FDR 嵌入）
# 裁定真源 90_methodology_open_questions.md §2（v2.0.0）：
#   ② 叠加相对轨道：同类因子滚动 RankIC 分布前 50% 分位（抗 regime 漂移）；
#   ③ 硬性统计门禁：ICIR≥0.5 + BHY 控制 FDR q=10%（入池链：
#     IC/RankIC 回测 → BHY FDR 校正 → ICIR≥0.5 → 滚动分位前 50% → candidate）。
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RelativeTrackInput:
    """滚动分位相对轨道输入（同类因子 RankIC 截面分布）。

    Attributes:
        factor_ic: 本因子滚动 RankIC 序列（index=评估日）
        peers_ic: 同类因子滚动 RankIC 分布（index=评估日，columns=同类 factor_id）
        min_quantile: 相对轨道门槛分位（裁定②：前 50%，即 ≥0.5）
    """

    factor_ic: pd.Series
    peers_ic: pd.DataFrame
    min_quantile: float = 0.5


@dataclass(frozen=True)
class RelativeTrackResult:
    """滚动分位相对轨道评估结果。"""

    factor_id: str
    quantile: float  # 窗口内逐日截面分位的中位数 ∈[0,1]；数据不足=NaN
    passed: bool  # quantile >= min_quantile
    window: int  # 实际参与评估的截面日数
    detail: str


def rolling_relative_quantile(
    factor_id: str,
    track: RelativeTrackInput,
    window: int | None = None,
) -> RelativeTrackResult:
    """滚动分位相对轨道评估（90 号 §2 裁定②嵌入点）。

    逐日计算本因子 RankIC 在同类因子截面分布中的分位（ peers ≤ 本因子
    的比例），取窗口尾部 ``window`` 日（None=全窗口）分位中位数；
    中位数 ≥ min_quantile（前 50%）判 passed。

    Args:
        factor_id: 因子ID
        track: 相对轨道输入（本因子序列 + 同类分布 + 门槛）
        window: 尾部窗口日数（None=全部对齐日期）

    Returns:
        RelativeTrackResult（数据不足时 quantile=NaN、passed=False）

    Raises:
        ValueError: min_quantile 不在 (0,1)
    """
    if not 0 < track.min_quantile < 1:
        raise ValueError(f"min_quantile 须在 (0,1)，实际 {track.min_quantile}")
    aligned = track.factor_ic.rename("__self__").to_frame().join(track.peers_ic, how="inner").dropna()
    if window is not None:
        aligned = aligned.tail(window)
    peer_cols = [c for c in aligned.columns if c != "__self__"]
    if aligned.empty or not peer_cols:
        return RelativeTrackResult(factor_id, float("nan"), False, 0, "相对轨道数据不足")
    daily_pct = aligned[peer_cols].le(aligned["__self__"], axis=0).mean(axis=1)
    quantile = float(daily_pct.median())
    passed = quantile >= track.min_quantile
    detail = (
        f"相对分位 {quantile:.2f}（{'守' if passed else '破'}前 "
        f"{track.min_quantile:.0%} 轨道，{len(aligned)} 日截面）"
    )
    return RelativeTrackResult(factor_id, quantile, passed, len(aligned), detail)


def screen_significance_bhy(
    p_values: list[float],
    q: float = DEFAULT_Q,
) -> BHYFDRResult:
    """入池批量显著性门禁（90 号 §2 裁定③ BHY FDR 嵌入 decay_monitor 入口）。

    单批筛选 >100 因子时以 BHY 控制 FDR q=10%（Harvey-Liu-Zhu 标准），
    算法本体见 bhy_fdr.py（纯 numpy 等价实现）。
    """
    return bhy_fdr(p_values, q=q)
