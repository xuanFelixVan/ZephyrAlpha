# [BLUEPRINT] MOD-RK-08 | docs/03_modules/_domain_risk/risk_budget_allocator/blueprint.md
# [MODULE] zephyr.risk.core.risk_budget_allocator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy; scipy; MOD-RK-16(Risk Decomposition,风险贡献复用)
# [CONSUMERS] MOD-RK-03(Portfolio Risk Monitor,实时监控) ; MOD-PC-02(Portfolio Optimizer,预算约束)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 权重归一化(Σw=1);long-only(w≥0);ERC→CCR_i≈σ_p/N;rebalance触发由风险贡献漂移唯一决定
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidBudgetInputError;BudgetOptimizationError
# [TESTS] tests/risk/test_risk_budget_allocator.py
# [A_module] module_id=MOD-RK-08 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Risk Budget Allocator — 风险预算分配器 (MOD-RK-08)

D-RISK §1.2 L2 Real-Time 盘中监控核心模块。基于风险贡献 (复用 RK-16) 实现风险预算分配:
    1. 等风险贡献 (ERC / Risk Parity): 每个资产贡献等量风险 CCR_i ≈ σ_p/N
    2. 自定义风险预算: 按 target_budgets 分配风险贡献占比
    3. 约束处理: long-only (w≥0), 满仓 (Σw=1), 可选 min/max 权重上下限
    4. 再平衡触发: 当前 vs 目标风险贡献漂移超阈值 → 触发再平衡

数学 (复用 RK-16):
    - σ_p = sqrt(w'Σw)
    - CCR_i = w_i · (Σw)_i / σ_p  (成分风险贡献, ΣCCR_i = σ_p)
    - pct_i = CCR_i / σ_p  (百分比贡献, Σpct_i = 1)
    - ERC 目标: pct_i = 1/N ∀i

求解器: scipy.optimize.minimize (SLSQP), 目标 = Σ(pct_i - target_i)²。
属 A 类基础设施 (凸优化 + 风险贡献, 数学逻辑明确), target_budgets 为 B 类策略输入。
依据: D:\\临时工作区\\依赖图\\11-D-RISK-风控域.md §1.2 RK-08, §2 依赖(RK-16→RK-08)
SSoT: depgraph MOD-RK-08
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from scipy.optimize import minimize

from zephyr.risk.core.risk_decomposition import RiskDecomposer
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "BudgetConfig",
    "BudgetAllocationResult",
    "RiskBudgetAllocator",
    "InvalidBudgetInputError",
    "BudgetOptimizationError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidBudgetInputError(ZephyrBaseError):
    """风险预算输入数据非法 (如预算非正、维度不匹配)。"""

    error_code = "ZA-RK-0008"


class BudgetOptimizationError(ZephyrBaseError):
    """风险预算优化求解失败 (不收敛 / 数值异常)。"""

    error_code = "ZA-RK-0009"


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BudgetConfig:
    """风险预算优化配置。

    Attributes:
        max_iter: SLSQP 最大迭代次数, 默认 500
        ftol: 目标函数收敛容差, 默认 1e-10
        rebalance_drift_threshold: 再平衡触发的风险贡献漂移阈值, 默认 0.05 (5%)
        min_weight: 单资产权重下限, 默认 0.0 (long-only)
        max_weight: 单资产权重上限, 默认 1.0 (无上限)
    """

    max_iter: int = 500
    ftol: float = 1e-10
    rebalance_drift_threshold: float = 0.05
    min_weight: float = 0.0
    max_weight: float = 1.0

    def __post_init__(self) -> None:
        if self.max_iter < 10:
            raise InvalidBudgetInputError(f"max_iter must be >=10, got {self.max_iter}")
        if self.ftol <= 0:
            raise InvalidBudgetInputError(f"ftol must be >0, got {self.ftol}")
        if not 0 < self.rebalance_drift_threshold <= 1:
            raise InvalidBudgetInputError(
                f"rebalance_drift_threshold must be in (0,1], got {self.rebalance_drift_threshold}"
            )
        if self.min_weight < 0:
            raise InvalidBudgetInputError(f"min_weight must be >=0 (long-only), got {self.min_weight}")
        if self.max_weight < self.min_weight:
            raise InvalidBudgetInputError(f"max_weight ({self.max_weight}) < min_weight ({self.min_weight})")


# ──────────────────────────────────────────────────────────────────────────────
# 计算结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BudgetAllocationResult:
    """风险预算分配结果。

    Attributes:
        weights: 求解得到的权重向量 (N,), Σw=1, w∈[min,max]
        total_risk: 组合标准差 σ_p
        risk_contributions: CCR 向量 (N,), ΣCCR = σ_p
        pct_contributions: 百分比贡献 (N,), Σpct = 1
        target_pct: 目标百分比贡献 (N,)
        contribution_error: 实际 vs 目标贡献的最大绝对偏差
        converged: 优化是否收敛
        method: 分配方法 ('erc' 或 'budget')
        timestamp: 计算时间
    """

    weights: np.ndarray
    total_risk: float
    risk_contributions: np.ndarray
    pct_contributions: np.ndarray
    target_pct: np.ndarray
    contribution_error: float
    converged: bool
    method: str
    timestamp: datetime

    @property
    def is_erc(self) -> bool:
        """是否为等风险贡献分配。"""
        return self.method == "erc"

    def to_dict(self) -> dict[str, Any]:
        return {
            "weights": self.weights.tolist(),
            "total_risk": self.total_risk,
            "risk_contributions": self.risk_contributions.tolist(),
            "pct_contributions": self.pct_contributions.tolist(),
            "target_pct": self.target_pct.tolist(),
            "contribution_error": self.contribution_error,
            "converged": self.converged,
            "method": self.method,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 风险预算分配器
# ──────────────────────────────────────────────────────────────────────────────


class RiskBudgetAllocator:
    """风险预算分配器——ERC + 自定义预算 + 约束处理 + 再平衡触发。

    用法 (等风险贡献):
        allocator = RiskBudgetAllocator()
        cov = np.array([[0.04, 0.01], [0.01, 0.09]])
        result = allocator.equal_risk_contribution(cov)
        # result.weights → 风险平价权重

    用法 (自定义预算):
        # 让资产0承担30%风险, 资产1承担70%
        result = allocator.allocate_by_budget(cov, target_budgets=[0.3, 0.7])

    用法 (再平衡触发):
        trigger = allocator.needs_rebalance(cov, current_weights, target_weights)
    """

    def __init__(
        self,
        config: BudgetConfig | None = None,
        decomposer: RiskDecomposer | None = None,
    ) -> None:
        self._config = config or BudgetConfig()
        # 复用 RK-16 的风险分解 (L1 依赖先行: RK-08 → RK-16)
        self._decomposer = decomposer or RiskDecomposer()

    @property
    def config(self) -> BudgetConfig:
        return self._config

    # ── 公开 API ──

    def equal_risk_contribution(
        self,
        cov: np.ndarray,
        assets: list[str] | None = None,
        now: datetime | None = None,
    ) -> BudgetAllocationResult:
        """等风险贡献 (ERC / Risk Parity) 分配。

        每个资产贡献等量风险: pct_i = 1/N。

        Args:
            cov: 协方差矩阵 (N, N)
            assets: 资产代码 (可选)
            now: 时间戳

        Returns:
            BudgetAllocationResult (method='erc')
        """
        cov = self._validate_cov(cov)
        N = cov.shape[0]
        target = np.ones(N) / N  # 等预算
        return self._solve(cov, target, method="erc", assets=assets, now=now)

    def allocate_by_budget(
        self,
        cov: np.ndarray,
        target_budgets: np.ndarray,
        assets: list[str] | None = None,
        now: datetime | None = None,
    ) -> BudgetAllocationResult:
        """按自定义风险预算分配。

        target_budgets 指定各资产应承担的风险贡献占比 (自动归一化)。

        Args:
            cov: 协方差矩阵 (N, N)
            target_budgets: 风险预算向量 (N,), 须全正, 自动归一化为占比
            assets: 资产代码
            now: 时间戳

        Returns:
            BudgetAllocationResult (method='budget')
        """
        cov = self._validate_cov(cov)
        target = np.asarray(target_budgets, dtype=float)
        if target.ndim != 1 or target.shape[0] != cov.shape[0]:
            raise InvalidBudgetInputError(
                f"target_budgets shape {target.shape} mismatched with cov ({cov.shape[0]},{cov.shape[0]})"
            )
        if np.any(target <= 0):
            raise InvalidBudgetInputError(f"target_budgets must be all positive, got {target}")  # noqa: MSG-EXPOSURE — target=预算权重数组数值非敏感信息
        target = target / np.sum(target)  # 归一化为占比
        return self._solve(cov, target, method="budget", assets=assets, now=now)

    def risk_contributions(self, cov: np.ndarray, weights: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
        """计算给定权重的风险贡献 (复用 RK-16)。

        Returns:
            (total_risk, ccr, pct) — 标准差, 成分贡献, 百分比贡献
        """
        result = self._decomposer.decompose(cov, weights)
        return result.total_risk, result.ccr, result.pct_contribution

    def needs_rebalance(
        self,
        cov: np.ndarray,
        current_weights: np.ndarray,
        target_weights: np.ndarray,
    ) -> bool:
        """判断是否需要再平衡 (风险贡献漂移超阈值)。

        比较 current_weights 与 target_weights 的风险贡献百分比漂移,
        任一资产漂移超过 rebalance_drift_threshold → 触发再平衡。

        Args:
            cov: 协方差矩阵
            current_weights: 当前权重
            target_weights: 目标权重

        Returns:
            True=需要再平衡
        """
        _, _, cur_pct = self.risk_contributions(cov, current_weights)
        _, _, tgt_pct = self.risk_contributions(cov, target_weights)
        drift = np.abs(cur_pct - tgt_pct)
        max_drift = float(np.max(drift)) if len(drift) > 0 else 0.0
        triggered = max_drift > self._config.rebalance_drift_threshold
        if triggered:
            logger.info(
                "Rebalance triggered: max_drift=%.4f > threshold=%.4f",
                max_drift,
                self._config.rebalance_drift_threshold,
            )
        return triggered

    # ── 内部: 求解 ──

    def _solve(
        self,
        cov: np.ndarray,
        target_pct: np.ndarray,
        method: str,
        assets: list[str] | None,
        now: datetime | None,
    ) -> BudgetAllocationResult:
        """SLSQP 求解风险预算优化问题。"""
        now = now or datetime.now(timezone.utc)
        N = cov.shape[0]
        cfg = self._config

        # 初始点: 按 target_pct 的反比波动率加权 (更好的起点)
        diag_vol = np.sqrt(np.diag(cov))
        inv_vol = 1.0 / np.where(diag_vol > 0, diag_vol, 1.0)
        x0 = inv_vol * target_pct
        x0 = x0 / np.sum(x0)

        # 约束: Σw = 1
        constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
        # 边界: [min_weight, max_weight]
        bounds = [(cfg.min_weight, cfg.max_weight)] * N

        def objective(w: np.ndarray) -> float:
            """目标: Σ(pct_i - target_i)²。"""
            w = np.clip(w, 0, None)  # 数值保护
            total = np.sum(w)
            if total <= 0:
                return 1e10
            w = w / total
            var = w @ cov @ w
            if var <= 0:
                return 1e10
            sigma = np.sqrt(var)
            ccr = w * (cov @ w) / sigma
            pct = ccr / sigma
            return float(np.sum((pct - target_pct) ** 2))

        res = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": cfg.max_iter, "ftol": cfg.ftol},
        )

        if not res.success:
            logger.warning(
                "Budget optimization did not fully converge: %s (error=%.2e)",
                res.message,
                res.fun,
            )

        weights = np.clip(res.x, 0, None)
        total = np.sum(weights)
        if total <= 0:
            raise BudgetOptimizationError(f"optimization yielded zero weights: {res.x}")
        weights = weights / total

        # 计算最终风险贡献
        sigma_p = float(np.sqrt(weights @ cov @ weights))
        if sigma_p > 0:
            ccr = weights * (cov @ weights) / sigma_p
            pct = ccr / sigma_p
        else:
            ccr = np.zeros(N)
            pct = np.zeros(N)

        contribution_error = float(np.max(np.abs(pct - target_pct)))

        return BudgetAllocationResult(
            weights=weights,
            total_risk=sigma_p,
            risk_contributions=ccr,
            pct_contributions=pct,
            target_pct=target_pct,
            contribution_error=contribution_error,
            converged=res.success,
            method=method,
            timestamp=now,
        )

    # ── 内部: 校验 ──

    @staticmethod
    def _validate_cov(cov: np.ndarray) -> np.ndarray:
        cov = np.asarray(cov, dtype=float)
        if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
            raise InvalidBudgetInputError(f"cov must be square 2D, got shape {cov.shape}")
        if cov.shape[0] < 2:
            raise InvalidBudgetInputError(f"need >=2 assets for budget allocation, got {cov.shape[0]}")
        # 检查对角线非负 (方差非负)
        if np.any(np.diag(cov) < 0):
            raise InvalidBudgetInputError(f"covariance diagonal must be non-negative, got {np.diag(cov)}")
        return cov
