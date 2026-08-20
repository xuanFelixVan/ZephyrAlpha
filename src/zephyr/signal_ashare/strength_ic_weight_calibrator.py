# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.4
# [MODULE] zephyr.signal_ashare.strength_ic_weight_calibrator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G08 打板细节讨论接入 quant_short_term_strength_engine)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 输出权重 Σ=1 且各维 ≥0；IC 全无效时回退经验权重
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 序列长度不一致→ValueError；n<3 → 回退经验权重（不抛错）
# [TESTS] tests/signal_ashare/test_strength_ic_weight_calibrator.py
# [TTL] permanent
#
# [ALGO_FLOW]
# 层: 输入
# - id: I1  6 维子分数历史序列 {dim: [score_t]} + 前瞻收益序列 [ret_t]（滚动 60 日窗口）
# 层: 算法
# - id: A1  compute_rank_ic：Spearman 秩相关（平均秩处理并列）
# - id: A2  calibrate_dimension_weights_ic：weight_i = max(IC_i,0)/Σmax(IC_j,0)；Σ≈0 或全负 → 回退经验权重
# - id: A3  should_recalibrate_cusum：CUSUM 偏移 >2σ 触发即时重校准
# 层: 输出
# - id: O1  {dim: weight} 归一化权重（Σ=1），供 6 维评分加权合成
# [/ALGO_FLOW]
"""量化短线强度 6 维权重 IC 加权校准（21 号 memo §3.4 路径 A，函数级）。

memo 裁定：6 维各视为子因子，计算滚动 60 日 RankIC，按 weight_i = IC_i / Σ|IC_j|
归一化——IC 高者自动加权，IC 衰减者自动降权。月度重校准 + CUSUM>2σ 即时重校准。
路径 B（SHAP 归因）远期不做。

工程修正（对 memo 公式的两点收敛，防负权重/除零）：
1. 负 IC 维 clip 到 0（负权重做多系统无意义；该维等效出局，与因子工厂 IC 末位淘汰一致）；
2. Σmax(IC,0)≈0（全部维度 IC 无效）→ 回退经验权重（20/15/20/15/20/10 归一化），
   保证 MVP 行为与现行引擎一致、可解释可归因。
"""

from __future__ import annotations

# 6 维维度名（与 quant_short_term_strength_engine 6 维一一对应）
STRENGTH_DIMENSIONS: tuple[str, ...] = (
    "price_momentum",  # 价格动量（满分 20）
    "industry_strength",  # 行业强度（满分 15）
    "relative_strength",  # 相对强度（满分 20）
    "capital",  # 资金（满分 15）
    "technical",  # 技术（满分 20）
    "risk",  # 风险（满分 10，反向：分低风险低）
)

# 经验权重（memo §3.4 MVP 首版：20/15/20/15/20/10 归一化，Σ=1）
EMPIRICAL_WEIGHTS: dict[str, float] = {
    "price_momentum": 0.20,
    "industry_strength": 0.15,
    "relative_strength": 0.20,
    "capital": 0.15,
    "technical": 0.20,
    "risk": 0.10,
}

DEFAULT_ROLLING_WINDOW = 60  # 滚动 60 日 RankIC（memo §3.4）
MIN_IC_SAMPLES = 3  # 少于此样本量 IC 无统计意义 → 回退经验权重
IC_EPS = 1e-9  # Σmax(IC,0) 除零保护
CUSUM_SIGMA_MULT = 2.0  # CUSUM >2σ 触发即时重校准（memo §3.4）


def _average_ranks(values: list[float]) -> list[float]:
    """平均秩（并列取秩均值），1 起。"""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def compute_rank_ic(dim_values: list[float], forward_returns: list[float]) -> float:
    """Spearman 秩相关 RankIC。

    n<MIN_IC_SAMPLES 或任一序列零方差（无区分度）→ 0.0（该维视为无信息）。
    """
    if len(dim_values) != len(forward_returns):
        raise ValueError("维度分数序列与收益序列长度必须一致")
    n = len(dim_values)
    if n < MIN_IC_SAMPLES:
        return 0.0
    rx = _average_ranks(dim_values)
    ry = _average_ranks(forward_returns)
    mx = sum(rx) / n
    my = sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx < IC_EPS or vy < IC_EPS:
        return 0.0
    return cov / (vx**0.5 * vy**0.5)


def calibrate_dimension_weights_ic(
    ic_by_dim: dict[str, float],
) -> dict[str, float]:
    """IC 加权归一化：weight_i = max(IC_i,0) / Σmax(IC_j,0)。

    Σmax(IC,0)≈0（全部维度 IC 无效）→ 回退 EMPIRICAL_WEIGHTS（副本）。
    未出现在 ic_by_dim 的维度视为 IC=0（不占权重）。
    """
    positive = {d: max(0.0, ic_by_dim.get(d, 0.0)) for d in STRENGTH_DIMENSIONS}
    total = sum(positive.values())
    if total < IC_EPS:
        return dict(EMPIRICAL_WEIGHTS)
    return {d: v / total for d, v in positive.items()}


def compute_rolling_ic_weights(
    dim_series: dict[str, list[float]],
    forward_returns: list[float],
    *,
    window: int = DEFAULT_ROLLING_WINDOW,
) -> dict[str, float]:
    """滚动窗口 RankIC → 6 维归一化权重（路径 A 主入口）。

    各维取末 window 个样本与收益对齐；窗口不足 → 该维 IC=0。
    全部维度无效 → 回退经验权重。
    """
    if window < MIN_IC_SAMPLES:
        raise ValueError(f"window 必须 ≥{MIN_IC_SAMPLES}")
    n_ret = len(forward_returns)
    ic_by_dim: dict[str, float] = {}
    for dim in STRENGTH_DIMENSIONS:
        series = dim_series.get(dim, [])
        m = min(window, len(series), n_ret)
        if m < MIN_IC_SAMPLES:
            ic_by_dim[dim] = 0.0
            continue
        ic_by_dim[dim] = compute_rank_ic(series[-m:], forward_returns[-m:])
    return calibrate_dimension_weights_ic(ic_by_dim)


def should_recalibrate_cusum(
    ic_series: list[float],
    *,
    sigma_mult: float = CUSUM_SIGMA_MULT,
) -> bool:
    """IC 均值漂移 CUSUM 检测：|累计偏移| > sigma_mult × σ → 触发即时重校准。

    n<2 或 σ≈0（IC 恒定无漂移证据）→ False。
    """
    n = len(ic_series)
    if n < 2:
        return False
    mean = sum(ic_series) / n
    var = sum((v - mean) ** 2 for v in ic_series) / (n - 1)
    if var < IC_EPS:
        return False
    sigma = var**0.5
    # 前后半段均值偏移的累积和检验（单变点 CUSUM 简化式）
    cusum = 0.0
    max_cusum = 0.0
    for v in ic_series:
        cusum += v - mean
        max_cusum = max(max_cusum, abs(cusum))
    return max_cusum > sigma_mult * sigma * (n**0.5)
