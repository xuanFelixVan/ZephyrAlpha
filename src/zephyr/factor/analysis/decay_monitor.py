# [BLUEPRINT] MOD-L02-009 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-08
# [MODULE] zephyr.factor.analysis.decay_monitor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.ic_decay
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——衰减监控基于已实现IC衰减曲线
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据不足->DecayStatus(half_life=0, is_decaying=True)
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

from zephyr.factor.analysis import load_analysis_config
from zephyr.factor.analysis.ic_decay import compute_half_life, compute_ic_decay


@dataclass(frozen=True)
class DecayStatus:
    """因子衰减状态。

    Attributes:
        factor_id: 因子ID
        half_life: IC 半衰期（lag 数）
        is_decaying: 是否衰减过快（半衰期 < 阈值）
        trend: 衰减趋势描述
    """

    factor_id: str
    half_life: float
    is_decaying: bool
    trend: str


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
) -> DecayStatus:
    """监控因子 IC 衰减状态。

    Args:
        factor_id: 因子ID
        ic_decay_series: 预计算的 IC 衰减 Series（可选，省略则用 symbols/start/end 计算）
        symbols: 评估标的池（ic_decay_series 为 None 时使用）
        start: 回测起始日期
        end: 回测结束日期

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
    return DecayStatus(factor_id, half_life, is_decaying, trend)
