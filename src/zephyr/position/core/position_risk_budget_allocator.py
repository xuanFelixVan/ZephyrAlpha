# [BLUEPRINT] MOD-POS-013 | docs/03_modules/MOD-POS-013/
# [MODULE] zephyr.position.core.position_risk_budget_allocator
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.covariance_estimator ; zephyr.shared.foundation.errors
# [CONSUMERS] D-PORTFOLIO(组合权重层) ; MOD-POS-012(相关性regime可作为预算调节输入)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 风险预算分配:相对风险贡献∝预算(等预算=ERC等风险贡献); 权重和=1; 相对风险贡献和=1; max_weight上限投影(N·max_weight≥1可行性校验); 迭代有界(max_iter封顶,无while True); 消费MOD-POS-011协方差估计(与选股信号零耦合,三维解耦); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-POS-013/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRiskBudgetInputError(ZA-POS-0021)
# [TESTS] tests/position/test_position_risk_budget_allocator.py
# [A_module] module_id=MOD-POS-013 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Position Risk Budget Allocator — 风险预算分配器 (MOD-POS-013)

按风险预算分配组合权重：使各标的的**相对风险贡献**（relative risk
contribution, RRC）与预算成正比。预算缺省为等权 → 即经典 ERC（等风险
贡献 / Risk Parity）组合：

    RC_i  = w_i·(Σw)_i / σ_p          （绝对风险贡献）
    RRC_i = RC_i / σ_p = w_i·(Σw)_i / σ_p²
    目标  : RRC_i = budget_i（归一化预算）

算法：Spinu 式循环迭代（w_i ← budget_i·σ_p²/(Σw)_i 方向收缩，逐轮归一化），
每轮嵌入 max_weight 上限投影（clip+重归一，有界轮次），收敛判据为
max|RRC_i − budget_i| < tol。迭代 max_iter 封顶（无无界循环）。

三维解耦（宪章 §3 约束四）：本模块只回答 how much（权重），消费
MOD-POS-011 的协方差估计，不关心标的是怎么选出来的（what）。

纪律：纯函数、无 IO；CovarianceEstimate 由调用方注入（禁自造数据管道）。
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Final

from zephyr.position.core.covariance_estimator import CovarianceEstimate
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidRiskBudgetInputError",
    "RiskBudgetAllocation",
    "allocate_risk_budget",
]

_DEFAULT_TOL: Final = 1e-8
_DEFAULT_MAX_ITER: Final = 500


class InvalidRiskBudgetInputError(ZephyrBaseError):
    """风险预算分配输入非法（预算不齐/负值/全零/上限不可行）。"""

    error_code = "ZA-POS-0021"


@dataclass(frozen=True)
class RiskBudgetAllocation:
    """风险预算分配结果（frozen 不可变）。

    Attributes:
        weights: {symbol: 权重}，和为 1
        relative_risk_contributions: {symbol: 相对风险贡献}，和为 1
        portfolio_volatility: 组合波动率 σ_p = sqrt(w'Σw)
        converged: 是否在 max_iter 内收敛（max|RRC−budget| < tol）
        iterations: 实际迭代轮数
        budget: 归一化后预算（等预算缺省时为 1/N）
    """

    weights: dict[str, float]
    relative_risk_contributions: dict[str, float]
    portfolio_volatility: float
    converged: bool
    iterations: int
    budget: dict[str, float] = field(default_factory=dict)


def _normalize_budget(
    covariance: CovarianceEstimate,
    budget: Mapping[str, float] | None,
) -> dict[str, float]:
    """校验并归一化预算（缺省=等预算 1/N）。"""
    symbols = covariance.symbols
    n = len(symbols)
    if budget is None:
        return {s: 1.0 / n for s in symbols}
    if set(budget) != set(symbols):
        raise InvalidRiskBudgetInputError(
            f"预算标的集与协方差标的不齐：budget={sorted(budget)} vs symbols={list(symbols)}"
        )
    for s, b in budget.items():
        if not math.isfinite(b) or b < 0.0:
            raise InvalidRiskBudgetInputError(f"标的 {s} 预算非法（须为有限非负值），got {b}")
    total = sum(budget.values())
    if total <= 0.0:
        raise InvalidRiskBudgetInputError("预算全零（须至少一个正预算）")
    return {s: budget[s] / total for s in symbols}


def _project_weights(
    weights: list[float],
    max_weight: float,
) -> list[float]:
    """上限投影：clip 到 [0, max_weight] 后重归一（有界不动点迭代）。"""
    n = len(weights)
    w = [min(max(x, 0.0), max_weight) for x in weights]
    for _ in range(n + 1):
        total = sum(w)
        if total <= 0.0:
            return [1.0 / n] * n
        w = [x / total for x in w]
        overflow = [x > max_weight for x in w]
        if not any(overflow):
            return w
        # 超限者钉在上限，剩余按相对比例分配余量
        capped = sum(max_weight for x in w if x > max_weight)
        free_idx = [i for i, x in enumerate(w) if x <= max_weight]
        free_sum = sum(w[i] for i in free_idx)
        remainder = 1.0 - capped
        w = [
            max_weight if x > max_weight else (x / free_sum * remainder if free_sum > 0 else 0.0)
            for x in w
        ]
    return w


def allocate_risk_budget(
    covariance: CovarianceEstimate,
    budget: Mapping[str, float] | None = None,
    *,
    max_weight: float = 1.0,
    tol: float = _DEFAULT_TOL,
    max_iter: int = _DEFAULT_MAX_ITER,
) -> RiskBudgetAllocation:
    """按风险预算分配权重（纯函数）。

    Args:
        covariance: MOD-POS-011 的协方差估计（标的集=候选池）
        budget: {symbol: 预算}，缺省=等预算（ERC）；允许未归一化
        max_weight: 单标的上限（须 ∈(0,1] 且 ≥1/N，否则不可行）
        tol: 收敛容差（max|RRC−budget|）
        max_iter: 迭代上限（有界）

    Returns:
        RiskBudgetAllocation

    Raises:
        InvalidRiskBudgetInputError: 预算/上限非法或不可行
    """
    symbols = covariance.symbols
    n = len(symbols)
    norm_budget = _normalize_budget(covariance, budget)

    if not math.isfinite(max_weight) or max_weight <= 0.0 or max_weight > 1.0:
        raise InvalidRiskBudgetInputError(f"max_weight 非法（须 ∈(0,1]），got {max_weight}")
    if max_weight * n < 1.0 - 1e-12:
        raise InvalidRiskBudgetInputError(
            f"max_weight 不可行：N·max_weight={n * max_weight} < 1（N={n}）"
        )
    if tol <= 0.0 or not math.isfinite(tol):
        raise InvalidRiskBudgetInputError(f"tol 非法（须为正有限值），got {tol}")
    if max_iter < 1:
        raise InvalidRiskBudgetInputError(f"max_iter 非法（须 ≥1），got {max_iter}")

    cov = [[covariance.matrix[i][j] for j in range(n)] for i in range(n)]
    b = [norm_budget[s] for s in symbols]

    # 初始权重：等权
    w = [1.0 / n] * n
    converged = False
    iterations = 0

    for it in range(1, max_iter + 1):
        iterations = it
        # Σw（矩阵-向量乘）
        cw = [sum(cov[i][j] * w[j] for j in range(n)) for i in range(n)]
        var_p = sum(w[i] * cw[i] for i in range(n))
        if var_p <= 0.0:
            raise InvalidRiskBudgetInputError("组合方差非正（协方差矩阵病态）")
        # RRC 与收敛检查
        rrc = [w[i] * cw[i] / var_p for i in range(n)]
        if max(abs(rrc[i] - b[i]) for i in range(n)) < tol:
            converged = True
            break
        # 阻尼 Spinu 迭代：candidate_i = b_i/(Σw)_i 归一化方向，
        # w ← (1−λ)w + λ·candidate（λ=0.5 阻尼抑制两步振荡，不动点即 RRC=budget）
        candidate = [b[i] / cw[i] if cw[i] > 0.0 else w[i] for i in range(n)]
        total = sum(candidate)
        candidate = [x / total for x in candidate]
        mixed = [0.5 * w[i] + 0.5 * candidate[i] for i in range(n)]
        total = sum(mixed)
        mixed = [x / total for x in mixed]
        w = _project_weights(mixed, max_weight)

    # 终态风险指标
    cw = [sum(cov[i][j] * w[j] for j in range(n)) for i in range(n)]
    var_p = sum(w[i] * cw[i] for i in range(n))
    if var_p <= 0.0:
        raise InvalidRiskBudgetInputError("组合方差非正（协方差矩阵病态）")
    final_rrc = [w[i] * cw[i] / var_p for i in range(n)]

    return RiskBudgetAllocation(
        weights={s: w[i] for i, s in enumerate(symbols)},
        relative_risk_contributions={s: final_rrc[i] for i, s in enumerate(symbols)},
        portfolio_volatility=math.sqrt(var_p),
        converged=converged,
        iterations=iterations,
        budget=norm_budget,
    )
