# [BLUEPRINT] MOD-PF-002 | docs/03_modules/_domain_portfolio_core/portfolio_optimizer/blueprint.md
# [MODULE] zephyr.pf_core.core.portfolio_optimizer
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.risk.core.risk_budget_allocator(MOD-RK-08); zephyr.pf_core.core.constraint_solver(MOD-PF-006); zephyr.shared.contracts.risk_limits(CTR-003); zephyr.shared.contracts.target_portfolio(CTR-007); numpy; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-PF-003(Rebalance Scheduler,触发重优化) ; D_EX_CORE(消费 TargetPortfolio) ; D_POSITION ; D_REPORTING
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] target_weights Σ≤max_gross_leverage;单标的≤max_single_position;Kelly只减不增;TargetPortfolio不可变;幂等键防重复
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OptimizationError;InvalidOptimizationInputError
# [TESTS] tests/pf_core/test_portfolio_optimizer.py
# [A_module] module_id=MOD-PF-002 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


Portfolio Optimizer — 组合优化器 (MOD-PF-002)

D-PF-CORE §1.2 L2 组合构建核心模块。将策略目标权重 (PC-01) + 风险限额 (CTR-003) +
协方差矩阵转化为合规的目标组合 (CTR-007), 供 D-EX-CORE/D-POSITION/D-REPORTING 消费。

核心流程:
    1. 优化方法 (风险预算为主选, 复用 MOD-RK-08):
       - risk_budget: 候选权重作风险预算目标 → RiskBudgetAllocator.allocate_by_budget
       - mean_variance: 均值方差 (期望收益+协方差, 备选)
       - equal_weight: 等权 (fallback)
    2. Kelly 截断 (只减不增): kelly_weight_i = μ_i/σ_i² × fraction, 取 min(kelly, 优化)
    3. 约束求解 (复用 PC-04): ConstraintSolver 强制 CTR-003 (仓位/行业/杠杆/相关性)
    4. 产出 TargetPortfolio (CTR-007): 不可变快照 + drift_pct + idempotency_key

属 A 类纯基础设施 (凸优化+约束投影+契约装配), 策略意图由 PC-01 candidate_weights 注入。
依据: D:\临时工作区\依赖图-D-PF-CORE-组合核心域.md §1.2 PC-02, §3.3 CTR-007
SSoT: depgraph MOD-PF-002
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 策略候选权重 candidate_weights
#   fields: {symbol: weight}（PC-01 注入的策略意图，long-only 非负，非空）
#   code: portfolio_optimizer.py L229 optimize 参数
# - id: I2
#   name: 风险限额 RiskLimits（CTR-003）
#   fields: max_single_position / max_gross_leverage 等限额
#   code: portfolio_optimizer.py L230 optimize 参数
# - id: I3
#   name: 协方差矩阵 covariance + 资产列表 assets
#   fields: cov (N,N) 对角非负，顺序同 assets
#   code: portfolio_optimizer.py L231-232 optimize 参数
# - id: I4
#   name: 期望收益向量 expected_returns（可选）
#   fields: μ (N,)，均值方差与 Kelly 截断用
#   code: portfolio_optimizer.py L234 optimize 参数
# - id: I5
#   name: 当前持仓权重 current_weights（可选）
#   fields: {symbol: weight}，drift_pct 漂移计算用
#   code: portfolio_optimizer.py L233 optimize 参数
# 层: 算法
# - id: A1
#   name_zh: ① 输入校验
#   name_en: _validate_inputs
#   intro: 把输入合法性一次查完：非空、维度匹配、对角非负、long-only
#   desc: L443-479 candidate 非空；cov.shape==(N,N) 且 diag≥0；candidate≥0；expected_returns.shape==(N,)；不合法抛 InvalidOptimizationInputError
#   inputs: I1 I3 I4
#   outputs: (assets, candidate_arr)
# - id: A2
#   name_zh: ② 基础权重计算（三方法）
#   name_en: _compute_base_weights
#   intro: 主选风险预算复用 RK-08，备选均值方差，兜底等权 1/N
#   desc: L345-405 risk_budget: 候选作预算目标→allocate_by_budget(cov,budgets)，全非正/失败→等权；mean_variance: w=(1/λ)Σ⁻¹μ clip≥0 归一，缺 μ/失败→等权
#   inputs: A1 I3 I4
#   outputs: base_weights（归一化 long-only）
# - id: A3
#   name_zh: ③ Kelly 截断（只减不增）
#   name_en: _apply_kelly_cap
#   intro: 用半 Kelly 上限压住单标的权重，只往下压不往上抬
#   desc: L409-439 kelly_i=μ_i/σ_i²×fraction(0.5)（σ²>1e-12 且 μ>0 才算）；capped=min(kelly,w)，kelly=0 不限制；最后归一化
#   inputs: A2 I4 I3
#   outputs: capped_weights + kelly_applied
#   invariant: Kelly 只减不增
# - id: A4
#   name_zh: ④ 约束求解（复用 PC-04）
#   name_en: ConstraintSolver.solve
#   intro: 把 Kelly 后权重交给约束求解器强制满足 CTR-003 限额
#   desc: L292-297 solve(weights, risk_limits, assets)→ConstraintSolveResult（裁剪后权重+违规清单+收敛标志）
#   inputs: A3 I2
#   outputs: post_weights（合规权重）
# - id: A5
#   name_zh: ⑤ 漂移计算
#   name_en: _compute_drift / needs_rebalance
#   intro: 目标与当前持仓的加权漂移超 2% 就标记需要再平衡
#   desc: L481-495 drift=Σ|target_i-current_i|/2；needs_rebalance: drift>drift_threshold(0.02)
#   inputs: A4 I5
#   outputs: drift_pct + 再平衡布尔
# - id: A6
#   name_zh: ⑥ 目标组合装配（optimize 主流程）
#   name_en: optimize
#   intro: 串联校验→优化→Kelly→约束→漂移，产出不可变 TargetPortfolio 快照
#   desc: L227-332 丢弃 ≤1e-9 权重；组装 TargetPortfolio(CTR-007) 含 drift_pct/risk_limits/rebalance_reason/uuid4 幂等键
#   inputs: A4 A5 I5
#   outputs: OptimizationResult
#   invariant: TargetPortfolio 不可变；幂等键防重复
# 层: 输出
# - id: O1
#   name_zh: 优化结果 OptimizationResult（含 TargetPortfolio CTR-007）
#   name_en: OptimizationResult / TargetPortfolio
#   intro: 目标组合不可变快照 + 方法/Kelly 标记 + 约束前后权重 + 收敛标志
#   invariant: Σtarget≤max_gross_leverage；单标的≤max_single_position
#   downstream: MOD-PF-003 Rebalance Scheduler 触发重优化；D_EX_CORE 消费 TargetPortfolio；D_POSITION；D_REPORTING（[CONSUMERS] 头）
# - id: O2
#   name_zh: 再平衡判定 needs_rebalance
#   name_en: needs_rebalance bool
#   intro: drift_pct 超阈值返回 True，供调度器决定是否触发重优化
#   downstream: MOD-PF-003 Rebalance Scheduler（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# I3 --> A2
# I4 --> A2
# A2 --> A3
# I4 --> A3
# I3 --> A3
# A3 --> A4
# I2 --> A4
# A4 --> A5
# I5 --> A5
# A4 --> A6
# A5 --> A6
# I5 --> A6
# A6 --> O1
# A5 --> O2
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

import numpy as np

from zephyr.pf_core.core.constraint_solver import ConstraintSolver, ConstraintSolveResult
from zephyr.risk.core.risk_budget_allocator import (
    BudgetAllocationResult,
    RiskBudgetAllocator,
)
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.contracts.target_portfolio import TargetPortfolio
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "OptimizationMethod",
    "OptimizerConfig",
    "OptimizationResult",
    "PortfolioOptimizer",
    "OptimizationError",
    "InvalidOptimizationInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class OptimizationMethod(str, Enum):
    """组合优化方法 (风险预算为主选)。"""

    RISK_BUDGET = "risk_budget"      # 风险预算 (主选, 复用 RK-08)
    MEAN_VARIANCE = "mean_variance"  # 均值方差 (备选)
    EQUAL_WEIGHT = "equal_weight"    # 等权 (fallback)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidOptimizationInputError(ZephyrBaseError):
    """优化输入数据非法 (如权重负值/维度不匹配/协方差非正定)。"""

    error_code = "ZA-PF-0021"


class OptimizationError(ZephyrBaseError):
    """优化求解失败 (不收敛/数值异常)。"""

    error_code = "ZA-PF-0022"


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class OptimizerConfig:
    """组合优化器配置。

    Attributes:
        default_method: 默认优化方法, 默认 RISK_BUDGET
        kelly_fraction: Kelly 系数 (半 Kelly=0.5), 默认 0.5
        kelly_cap_enabled: 是否启用 Kelly 截断, 默认 True
        risk_aversion: 均值方差风险厌恶系数 λ, 默认 2.0
        drift_threshold: 漂移阈值 (drift_pct 超此值标记需再平衡), 默认 0.02
    """

    default_method: OptimizationMethod = OptimizationMethod.RISK_BUDGET
    kelly_fraction: float = 0.5
    kelly_cap_enabled: bool = True
    risk_aversion: float = 2.0
    drift_threshold: float = 0.02

    def __post_init__(self) -> None:
        if not 0 < self.kelly_fraction <= 1:
            raise InvalidOptimizationInputError(
                f"kelly_fraction must be in (0,1], got {self.kelly_fraction}"
            )
        if self.risk_aversion <= 0:
            raise InvalidOptimizationInputError(
                f"risk_aversion must be >0, got {self.risk_aversion}"
            )
        if self.drift_threshold <= 0:
            raise InvalidOptimizationInputError(
                f"drift_threshold must be >0, got {self.drift_threshold}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 优化结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class OptimizationResult:
    """组合优化结果。

    Attributes:
        target_portfolio: 目标组合 (CTR-007, 不可变)
        method_used: 实际使用的优化方法
        kelly_applied: 是否应用了 Kelly 截断
        pre_constraint_weights: 约束求解前权重 (Kelly 截断后)
        post_constraint_weights: 约束求解后权重 (= target_portfolio.target_weights)
        constraint_result: PC-04 约束求解结果
        converged: 优化是否收敛
        timestamp: 优化时间
    """

    target_portfolio: TargetPortfolio
    method_used: OptimizationMethod
    kelly_applied: bool
    pre_constraint_weights: dict[str, float]
    post_constraint_weights: dict[str, float]
    constraint_result: ConstraintSolveResult
    converged: bool
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "method_used": self.method_used.value,
            "kelly_applied": self.kelly_applied,
            "converged": self.converged,
            "pre_constraint_sum": sum(self.pre_constraint_weights.values()),
            "post_constraint_sum": sum(self.post_constraint_weights.values()),
            "violation_count": len(self.constraint_result.violations),
            "drift_pct": self.target_portfolio.drift_pct,
            "idempotency_key": self.target_portfolio.idempotency_key,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 组合优化器
# ──────────────────────────────────────────────────────────────────────────────


class PortfolioOptimizer:
    """组合优化器——风险预算为主 + Kelly 截断 + 约束求解 → TargetPortfolio。

    用法:
        optimizer = PortfolioOptimizer()
        result = optimizer.optimize(
            candidate_weights={"A": 0.6, "B": 0.4},
            risk_limits=risk_limits,
            covariance=cov_matrix,
            assets=["A", "B"],
            current_weights={"A": 0.5, "B": 0.5},
            strategy_id="s1",
            portfolio_id="p1",
        )
        # result.target_portfolio (CTR-007) → D-EX-CORE 消费

    Args:
        config: 优化器配置
        budget_allocator: 风险预算分配器 (可注入, 默认 RK-08)
        constraint_solver: 约束求解器 (可注入, 默认 PC-04)
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        config: OptimizerConfig | None = None,
        budget_allocator: RiskBudgetAllocator | None = None,
        constraint_solver: ConstraintSolver | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config or OptimizerConfig()
        self._budget_allocator = budget_allocator or RiskBudgetAllocator()
        self._constraint_solver = constraint_solver or ConstraintSolver()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @property
    def config(self) -> OptimizerConfig:
        return self._config

    # ── 公开 API ──

    def optimize(
        self,
        candidate_weights: dict[str, float],
        risk_limits: RiskLimits,
        covariance: np.ndarray,
        assets: list[str],
        current_weights: dict[str, float] | None = None,
        expected_returns: np.ndarray | None = None,
        method: OptimizationMethod | None = None,
        strategy_id: str = "",
        portfolio_id: str = "",
        rebalance_reason: str = "drift_threshold",
        now: datetime | None = None,
    ) -> OptimizationResult:
        """执行组合优化, 产出 TargetPortfolio (CTR-007)。

        Args:
            candidate_weights: 策略目标权重 {symbol: weight} (PC-01 产出)
            risk_limits: 风险限额 (CTR-003)
            covariance: 协方差矩阵 (N, N), 顺序同 assets
            assets: 资产列表
            current_weights: 当前持仓权重 (计算 drift_pct 用)
            expected_returns: 期望收益向量 (N,) (均值方差 + Kelly 用)
            method: 优化方法 (None=用 config.default_method)
            strategy_id: 来源策略 ID
            portfolio_id: 组合 ID
            rebalance_reason: 再平衡原因
            now: 时间戳

        Returns:
            OptimizationResult

        Raises:
            InvalidOptimizationInputError: 输入非法
        """
        now = now or self._clock()
        method = method or self._config.default_method
        current_weights = current_weights or {}

        # 输入校验
        assets, candidate_arr = self._validate_inputs(
            candidate_weights, covariance, assets, expected_returns
        )

        # 1. 优化方法计算基础权重
        base_weights = self._compute_base_weights(
            method, candidate_arr, covariance, expected_returns, assets
        )

        # 2. Kelly 截断 (只减不增)
        kelly_applied = False
        if (
            self._config.kelly_cap_enabled
            and expected_returns is not None
        ):
            base_weights, kelly_applied = self._apply_kelly_cap(
                base_weights, expected_returns, covariance
            )

        # 转回 dict 用于约束求解
        pre_constraint = {
            assets[i]: float(base_weights[i]) for i in range(len(assets))
        }

        # 3. 约束求解 (PC-04 强制 CTR-003)
        constraint_result = self._constraint_solver.solve(
            weights=pre_constraint,
            risk_limits=risk_limits,
            assets=assets,
        )
        post_weights = constraint_result.weights

        # 4. 构建 target_weights dict (只保留非零)
        target_weights = {
            assets[i]: float(post_weights[i])
            for i in range(len(assets))
            if post_weights[i] > 1e-9
        }

        # 5. 计算 drift_pct (加权漂移)
        drift_pct = self._compute_drift(target_weights, current_weights, assets)

        # 6. 构建 TargetPortfolio (CTR-007)
        target_portfolio = TargetPortfolio(
            portfolio_id=portfolio_id,
            strategy_id=strategy_id,
            target_weights=target_weights,
            current_weights=dict(current_weights),
            drift_pct=drift_pct,
            risk_limits=risk_limits,
            rebalance_reason=rebalance_reason,
            created_at=now,
            idempotency_key=str(uuid.uuid4()),
            schema_version="1.0",
        )

        return OptimizationResult(
            target_portfolio=target_portfolio,
            method_used=method,
            kelly_applied=kelly_applied,
            pre_constraint_weights=pre_constraint,
            post_constraint_weights=target_weights,
            constraint_result=constraint_result,
            converged=bool(constraint_result.converged),
            timestamp=now,
        )

    def needs_rebalance(
        self,
        target_weights: dict[str, float],
        current_weights: dict[str, float],
    ) -> bool:
        """判断是否需要再平衡 (drift_pct > drift_threshold)。"""
        drift = self._compute_drift(target_weights, current_weights, list(target_weights.keys()))
        return drift > self._config.drift_threshold

    # ── 内部: 优化方法 ──

    def _compute_base_weights(
        self,
        method: OptimizationMethod,
        candidate: np.ndarray,
        cov: np.ndarray,
        expected_returns: np.ndarray | None,
        assets: list[str],
    ) -> np.ndarray:
        """根据优化方法计算基础权重 (归一化, long-only)。"""
        if method == OptimizationMethod.RISK_BUDGET:
            return self._risk_budget_weights(candidate, cov, assets)
        if method == OptimizationMethod.MEAN_VARIANCE:
            return self._mean_variance_weights(cov, expected_returns)
        if method == OptimizationMethod.EQUAL_WEIGHT:
            return self._equal_weights(len(assets))
        raise InvalidOptimizationInputError(f"unknown method: {method}")

    def _risk_budget_weights(
        self, candidate: np.ndarray, cov: np.ndarray, assets: list[str]
    ) -> np.ndarray:
        """风险预算: 候选权重作风险预算目标 (复用 RK-08)。"""
        # 候选权重作预算目标 (须全正, 自动归一化)
        budgets = np.where(candidate > 0, candidate, 1e-6)
        if np.all(budgets <= 0):
            # 候选全零/负 → 退化为等权
            logger.warning("risk_budget: candidate all non-positive, fallback to equal_weight")
            return self._equal_weights(len(assets))
        try:
            result = self._budget_allocator.allocate_by_budget(cov, budgets)
            return result.weights
        except Exception as exc:  # noqa: BLE001 — 5.135治标: RK-08 求解失败 → 等权 fallback（故障隔离不阻断优化主流程）
            logger.warning("risk_budget optimization failed (%s), fallback to equal_weight", exc)
            return self._equal_weights(len(assets))

    def _mean_variance_weights(
        self, cov: np.ndarray, expected_returns: np.ndarray | None
    ) -> np.ndarray:
        """均值方差: w ∝ Σ^-1 μ (max Sharpe 近似), 归一化 long-only。"""
        if expected_returns is None:
            logger.warning("mean_variance needs expected_returns, fallback to equal_weight")
            return self._equal_weights(cov.shape[0])
        lam = self._config.risk_aversion
        try:
            # w = (1/λ) Σ^-1 μ, 然后 long-only 截断 + 归一化
            inv_cov = np.linalg.pinv(cov)
            w = inv_cov @ expected_returns / lam
            w = np.clip(w, 0, None)  # long-only
            total = np.sum(w)
            if total <= 0:
                return self._equal_weights(cov.shape[0])
            return w / total
        except Exception as exc:  # noqa: BLE001
            logger.warning("mean_variance optimization failed (%s), fallback to equal_weight", exc)
            return self._equal_weights(cov.shape[0])

    @staticmethod
    def _equal_weights(n: int) -> np.ndarray:
        """等权 (1/N)。"""
        if n <= 0:
            raise InvalidOptimizationInputError("assets count must be >0")
        return np.ones(n) / n

    # ── 内部: Kelly 截断 ──

    def _apply_kelly_cap(
        self,
        weights: np.ndarray,
        expected_returns: np.ndarray,
        cov: np.ndarray,
    ) -> tuple[np.ndarray, bool]:
        """Kelly 截断 (只减不增): kelly_i = μ_i/σ_i² × fraction, 取 min(kelly, w)。

        Returns:
            (capped_weights, kelly_applied)
        """
        diag_var = np.diag(cov)
        # Kelly 权重: f*_i = μ_i / σ_i² × fraction
        kelly = np.zeros_like(weights, dtype=float)
        for i in range(len(weights)):
            if diag_var[i] > 1e-12 and expected_returns[i] > 0:
                kelly[i] = (expected_returns[i] / diag_var[i]) * self._config.kelly_fraction

        # Kelly 只减不增: min(kelly, w), 但 kelly=0 不限制 (无正期望)
        capped = np.where(
            (kelly > 0) & (kelly < weights),
            kelly,
            weights,
        )
        applied = bool(np.any(capped < weights - 1e-12))

        # 归一化
        total = np.sum(capped)
        if total > 0:
            capped = capped / total
        return capped, applied

    # ── 内部: 校验 / 工具 ──

    def _validate_inputs(
        self,
        candidate_weights: dict[str, float],
        covariance: np.ndarray,
        assets: list[str],
        expected_returns: np.ndarray | None,
    ) -> tuple[list[str], np.ndarray]:
        """校验输入, 返回 (assets, candidate_array)。"""
        if not candidate_weights:
            raise InvalidOptimizationInputError("candidate_weights cannot be empty")
        if not assets:
            assets = list(candidate_weights.keys())
        cov = np.asarray(covariance, dtype=float)
        n = len(assets)
        if cov.shape != (n, n):
            raise InvalidOptimizationInputError(
                f"covariance shape {cov.shape} != ({n},{n})"
            )
        # 协方差对角线非负
        if np.any(np.diag(cov) < 0):
            raise InvalidOptimizationInputError("covariance diagonal must be non-negative")
        # 候选权重对齐 assets
        candidate_arr = np.array(
            [float(candidate_weights.get(a, 0.0)) for a in assets], dtype=float
        )
        if np.any(candidate_arr < 0):
            raise InvalidOptimizationInputError(
                "candidate_weights must be non-negative (long-only)"
            )
        # 期望收益维度
        if expected_returns is not None:
            er = np.asarray(expected_returns, dtype=float)
            if er.shape != (n,):
                raise InvalidOptimizationInputError(
                    f"expected_returns shape {er.shape} != ({n},)"
                )
        return assets, candidate_arr

    @staticmethod
    def _compute_drift(
        target: dict[str, float],
        current: dict[str, float],
        assets: list[str],
    ) -> float:
        """计算加权漂移百分比: Σ|target_i - current_i| / 2 (归一化漂移)。"""
        if not target and not current:
            return 0.0
        drift = 0.0
        for a in assets:
            t = target.get(a, 0.0)
            c = current.get(a, 0.0)
            drift += abs(t - c)
        return drift / 2.0
