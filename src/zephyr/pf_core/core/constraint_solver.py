# [BLUEPRINT] MOD-PF-006 | docs/03_modules/_domain_portfolio_core/constraint_solver/blueprint.md
# [MODULE] zephyr.pf_core.core.constraint_solver
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.shared.contracts.risk_limits(CTR-003); numpy; zephyr.shared.foundation.errors; MOD-PA-004(StrategyCorrelationGate,策略级门禁由上层调用)
# [CONSUMERS] MOD-PF-002(Portfolio Optimizer,约束输入)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Σw≤max_gross_leverage;单标的w_i≤max_single_position;输出与输入同维度;不收敛返回最后迭代+converged=False
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ConstraintViolationError;CorrelationGateFailure
# [TESTS] tests/pf_core/test_constraint_solver.py
# [A_module] module_id=MOD-PF-006 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Constraint Solver — 约束求解器 (MOD-PF-006)

D-PF-CORE §1.2 L2 组合构建核心模块。将风险限额 (CTR-003) 和拥挤检测转化为
可执行权重约束, 供 PC-02 组合优化器消费:

    1. 7 约束链 (迭代投影法): 行业绝对≤30% / 行业相对±10% / 市值暴露 /
       MDD≤5% / 相关性≤0.7 / 风格≤±0.3σ / 仓位上限
    2. 拥挤检测: 资产间相关性 ρ>0.8 → 权重减半; ρ>0.9 → 仅保留其一
    3. 求解: 逐约束裁剪 → 归一化 → 收敛判定

数学 (迭代投影法):
    - w_{i+1} = normalize(project_Ci(w_i))
    - 收敛: ||w_new - w_old||_∞ < tol
    - 最大迭代: max_iter (默认 100)

属 A 类纯基础设施 (数学约束投影, 无策略决策), 阈值来源 RiskLimits (CTR-003)。
策略级相关性门禁 (MOD-PA-004) 由上层 Portfolio Optimizer 在调用本求解器前执行。
依据: D:\临时工作区\依赖图
-D-PF-CORE-组合构建域.md §1.2 PC-04
SSoT: depgraph MOD-PF-006
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 候选权重 weights
#   fields: dict{symbol: weight} 或 np.ndarray（long-only，非负，非空）
#   code: constraint_solver.py L247 solve(weights)
# - id: I2
#   name: 风险限额 RiskLimits（CTR-003）
#   fields: max_single_position/min_single_position/max_gross_leverage/max_sector_concentration/symbol_overrides
#   code: constraint_solver.py L250 risk_limits
# - id: I3
#   name: 行业映射与基准
#   fields: sector_mapping {symbol: sector} + benchmark_sector_weights {sector: weight}
#   code: constraint_solver.py L252-253
# - id: I4
#   name: 相关性与暴露数据
#   fields: correlation_matrix (N,N) + style_exposures + market_cap_exposures {symbol: σ}
#   code: constraint_solver.py L254-256
# - id: I5
#   name: 求解器配置 ConstraintSolverConfig
#   fields: max_iter=100 / tol=1e-6 / 拥挤阈值0.8/0.9 / max_correlation=0.7 / 暴露σ=0.3 / 行业偏移±0.10
#   code: constraint_solver.py L88 ConstraintSolverConfig
# 层: 算法
# - id: A1
#   name_zh: ① 7 约束链迭代投影主循环
#   name_en: ConstraintSolver.solve
#   intro: 迭代投影法：逐约束裁剪 → 归一化 → 收敛判定，最多 max_iter 次
#   desc: L306-383：w_{i+1}=normalize(project_Ci(w_i))；||Δw||∞<tol 收敛；全零权重直接返回；不收敛返回最后迭代+converged=False
#   inputs: I1 I5 A2 A3 A4 A5 A6 A7
#   outputs: 收敛权重 w + violations + scaling + iterations
#   invariant: Σw≤max_gross_leverage；w_i≤max_single_position；输出与输入同维度
# - id: A2
#   name_zh: ② 单标的仓位投影 C7
#   name_en: _project_single_position
#   intro: 每个标的权重裁剪到 [min_pos, 个票override或max_pos] 区间
#   desc: L387-412：w_i>limit → 记违规并 clip；0<w_i<min_pos → 抬到 min_pos（w=0 刻意排除不抬回，#208-③）
#   inputs: I1 I2
#   outputs: 裁剪后 w + C7 违规记录
# - id: A3
#   name_zh: ③ 行业集中度投影 C1/C2
#   name_en: _project_sector_absolute / _project_sector_relative
#   intro: 行业聚合权重超上限等比缩放；相对基准偏移超 ±10% 裁到边界
#   desc: L414-480：sector_w>max_sector → 组内 ×(max_sector/sector_w)；|sw_pct-bw|>max_dev → 组内 ×(target_w/sw)
#   inputs: I1 I2 I3
#   outputs: 裁剪后 w + C1/C2 违规记录
# - id: A4
#   name_zh: ④ 暴露约束投影 C3/C6
#   name_en: _project_market_cap / _project_style
#   intro: 组合加权市值/风格暴露超 0.3σ 时，同向标的按比例压缩
#   desc: L482-588：weighted_exp=Σw_i·exp_i/Σw；|E|>max_exp → 同向标的 ×(max_exp/|E|)
#   inputs: I1 I4 I5
#   outputs: 裁剪后 w + C3/C6 违规记录
# - id: A5
#   name_zh: ⑤ 相关性裁剪 C5
#   name_en: _project_correlation
#   intro: 标的相关性 |ρ|>0.7 时降权权重较大者
#   desc: L516-554：高相关对中 w 大者 ×max(1-(ρ-0.7), 0.5)；矩阵形状不符抛 CorrelationGateFailure
#   inputs: I1 I4 I5
#   outputs: 裁剪后 w + C5 违规记录
# - id: A6
#   name_zh: ⑥ 拥挤检测
#   name_en: _apply_crowding
#   intro: ρ>0.9 仅保留权重较大者（另一清零）；ρ>0.8 双方权重减半
#   desc: L590-636：硬拥挤 w 小者=0；软拥挤双方 ×crowding_scale(0.5)
#   inputs: I1 I4 I5
#   outputs: 裁剪后 w + CROWD 违规记录
# - id: A7
#   name_zh: ⑦ 杠杆投影与归一化
#   name_en: _project_leverage / _normalize
#   intro: 总权重超杠杆上限时整体缩放到 max_gross_leverage
#   desc: L638-708：Σw>max_lev → w×(max_lev/Σw)；归一化到 [0, max_leverage]
#   inputs: I1 I2
#   outputs: 缩放后 w + LEV 违规记录
# 层: 输出
# - id: O1
#   name_zh: 约束求解结果 ConstraintSolveResult
#   name_en: ConstraintSolveResult
#   intro: 求解后权重 + 违规清单 + 全局缩放因子 + 收敛标志 + 迭代次数
#   invariant: Σw≤max_gross_leverage；不收敛时 converged=False 仍返回最后迭代
#   downstream: MOD-PF-002 Portfolio Optimizer（约束输入，[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I5 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# I3 --> A3
# I1 --> A4
# I4 --> A4
# I5 --> A4
# I1 --> A5
# I4 --> A5
# I5 --> A5
# I1 --> A6
# I4 --> A6
# I5 --> A6
# I1 --> A7
# I2 --> A7
# A2 --> A1
# A3 --> A1
# A4 --> A1
# A5 --> A1
# A6 --> A1
# A7 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np

from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ConstraintSolverConfig",
    "ConstraintViolation",
    "ConstraintSolveResult",
    "ConstraintSolver",
    "ConstraintViolationError",
    "CorrelationGateFailure",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class ConstraintViolationError(ZephyrBaseError):
    """约束不可满足 (如 max_single_position × N < max_gross_leverage)。"""

    error_code = "ZA-PF-0061"


class CorrelationGateFailure(ZephyrBaseError):
    """拥挤检测异常 (降级为跳过拥挤检测)。"""

    error_code = "ZA-PF-0062"


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ConstraintSolverConfig:
    """约束求解器配置。

    Attributes:
        max_iter: 最大迭代次数, 默认 100
        tol: 收敛容差 (L∞ 范数), 默认 1e-6
        crowding_threshold: 拥挤检测相关性阈值, 默认 0.8 (ρ>0.8 权重减半)
        crowding_hard_threshold: 硬拥挤阈值, 默认 0.9 (ρ>0.9 仅保留其一)
        crowding_scale: 拥挤减半因子, 默认 0.5
        max_correlation: 标的间最大允许相关性, 默认 0.7
        max_style_exposure_sigma: 风格因子暴露上限 (σ), 默认 0.3
        max_market_cap_exposure_sigma: 市值暴露上限 (σ), 默认 0.3
        max_drawdown_limit: MDD 约束阈值, 默认 0.05 (5%)
        sector_relative_deviation: 行业相对偏移上限, 默认 0.10 (±10%)
    """

    max_iter: int = 100
    tol: float = 1e-6
    crowding_threshold: float = 0.8
    crowding_hard_threshold: float = 0.9
    crowding_scale: float = 0.5
    max_correlation: float = 0.7
    max_style_exposure_sigma: float = 0.3
    max_market_cap_exposure_sigma: float = 0.3
    max_drawdown_limit: float = 0.05
    sector_relative_deviation: float = 0.10

    def __post_init__(self) -> None:
        if self.max_iter < 1:
            raise ConstraintViolationError(f"max_iter must be >=1, got {self.max_iter}")
        if self.tol <= 0:
            raise ConstraintViolationError(f"tol must be >0, got {self.tol}")
        if not 0 <= self.crowding_threshold <= 1:
            raise ConstraintViolationError(f"crowding_threshold must be in [0,1], got {self.crowding_threshold}")
        if not 0 <= self.crowding_hard_threshold <= 1:
            raise ConstraintViolationError(
                f"crowding_hard_threshold must be in [0,1], got {self.crowding_hard_threshold}"
            )
        if self.crowding_hard_threshold < self.crowding_threshold:
            raise ConstraintViolationError("crowding_hard_threshold must be >= crowding_threshold")
        if not 0 < self.crowding_scale <= 1:
            raise ConstraintViolationError(f"crowding_scale must be in (0,1], got {self.crowding_scale}")


# ──────────────────────────────────────────────────────────────────────────────
# 约束违规记录
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ConstraintViolation:
    """单条约束违规记录。

    Attributes:
        constraint_id: 约束编号 (C1-C7)
        constraint_name: 约束名称
        symbol: 涉及标的 (或 'portfolio' 表示组合级)
        original_value: 原始值
        threshold: 阈值
        scaling_applied: 应用的缩放因子
    """

    constraint_id: str
    constraint_name: str
    symbol: str
    original_value: float
    threshold: float
    scaling_applied: float


# ──────────────────────────────────────────────────────────────────────────────
# 求解结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ConstraintSolveResult:
    """约束求解结果。

    Attributes:
        weights: 求解后权重 (N,), Σw ≤ max_gross_leverage
        violations: 约束违规列表 (裁剪记录)
        scaling_applied: 全局缩放因子 (原始 Σw / 输出 Σw)
        converged: 是否收敛
        iterations: 实际迭代次数
        timestamp: 计算时间
    """

    weights: np.ndarray
    violations: list[ConstraintViolation] = field(default_factory=list)
    scaling_applied: float = 1.0
    converged: bool = True
    iterations: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "weights": self.weights.tolist(),
            "violations": [
                {
                    "constraint_id": v.constraint_id,
                    "constraint_name": v.constraint_name,
                    "symbol": v.symbol,
                    "original_value": v.original_value,
                    "threshold": v.threshold,
                    "scaling_applied": v.scaling_applied,
                }
                for v in self.violations
            ],
            "scaling_applied": self.scaling_applied,
            "converged": self.converged,
            "iterations": self.iterations,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 约束求解器
# ──────────────────────────────────────────────────────────────────────────────


class ConstraintSolver:
    """约束求解器——7 约束链迭代投影 + 拥挤检测。

    用法 (基本约束):
        solver = ConstraintSolver()
        risk_limits = RiskLimits(as_of_date=..., idempotency_key="k1")
        result = solver.solve(weights, risk_limits)

    用法 (含行业约束):
        result = solver.solve(
            weights, risk_limits,
            sector_mapping={"600519.SH": "白酒", "000858.SZ": "白酒"},
        )

    用法 (含相关性约束):
        result = solver.solve(
            weights, risk_limits,
            correlation_matrix=cov_matrix,
            assets=["600519.SH", "000858.SZ"],
        )
    """

    def __init__(self, config: ConstraintSolverConfig | None = None) -> None:
        self._config = config or ConstraintSolverConfig()

    @property
    def config(self) -> ConstraintSolverConfig:
        return self._config

    # ── 公开 API ──

    def solve(
        self,
        weights: dict[str, float] | np.ndarray,
        risk_limits: RiskLimits,
        assets: list[str] | None = None,
        sector_mapping: dict[str, str] | None = None,
        benchmark_sector_weights: dict[str, float] | None = None,
        correlation_matrix: np.ndarray | None = None,
        style_exposures: dict[str, float] | None = None,
        market_cap_exposures: dict[str, float] | None = None,
        now: datetime | None = None,
    ) -> ConstraintSolveResult:
        """执行 7 约束链迭代投影求解。

        Args:
            weights: 候选权重 {symbol: weight} 或权重向量
            risk_limits: 风险限额 (CTR-003)
            assets: 标的列表 (weights 为 np.ndarray 时必填)
            sector_mapping: {symbol: sector} 行业映射 (C1/C2)
            benchmark_sector_weights: 基准行业权重 {sector: weight} (C2)
            correlation_matrix: 标的间相关性矩阵 (C5 + 拥挤检测)
            style_exposures: {symbol: style_exposure_sigma} (C6)
            market_cap_exposures: {symbol: market_cap_exposure_sigma} (C3)
            now: 时间戳

        Returns:
            ConstraintSolveResult
        """
        now = now or datetime.now(timezone.utc)
        assets, w = self._parse_weights(weights, assets)
        cfg = self._config
        violations: list[ConstraintViolation] = []

        # 可行性检查: max_single_position × N ≥ max_gross_leverage
        # 不报错——只是意味着组合无法满仓投资 (Σw < max_gross_leverage), 属正常欠配
        min_capacity = risk_limits.max_single_position * len(assets)
        if min_capacity < risk_limits.max_gross_leverage:
            logger.info(
                "portfolio under-invested: max_single_position(%.4f) × N(%d) = %.4f "
                "< max_gross_leverage(%.4f) — Σw will be < max_gross_leverage",
                risk_limits.max_single_position,
                len(assets),
                min_capacity,
                risk_limits.max_gross_leverage,
            )

        original_sum = float(np.sum(w))

        # 全零权重 → 直接返回 (无需投影)
        if original_sum <= 0:
            return ConstraintSolveResult(
                weights=w,
                violations=[],
                scaling_applied=1.0,
                converged=True,
                iterations=0,
                timestamp=now,
            )

        # 迭代投影
        converged = False
        crowding_scaled: set[tuple[int, int]] = set()  # AI-NIGHT-001 #205：软拥挤一次性响应记忆
        corr_scaled: set[tuple[int, int]] = set()  # AI-NIGHT-001 #205 同族：C5 相关性一次性响应记忆
        for iteration in range(cfg.max_iter):
            w_prev = w.copy()

            # C7: 单标的仓位上限 (CTR-003 max_single_position)
            w, v = self._project_single_position(w, assets, risk_limits)
            violations.extend(v)

            # C1: 行业绝对集中度 (CTR-003 max_sector_concentration)
            if sector_mapping:
                w, v = self._project_sector_absolute(w, assets, sector_mapping, risk_limits)
                violations.extend(v)

            # C2: 行业相对偏移 (±sector_relative_deviation)
            if sector_mapping and benchmark_sector_weights:
                w, v = self._project_sector_relative(w, assets, sector_mapping, benchmark_sector_weights)
                violations.extend(v)

            # C3: 市值暴露 (±max_market_cap_exposure_sigma)
            if market_cap_exposures:
                w, v = self._project_market_cap(w, assets, market_cap_exposures)
                violations.extend(v)

            # C5: 标的相关性 (≤max_correlation；一次性响应 #205 同族)
            if correlation_matrix is not None:
                w, v = self._project_correlation(w, assets, correlation_matrix, corr_scaled)
                violations.extend(v)

            # C6: 风格因子暴露 (±max_style_exposure_sigma)
            if style_exposures:
                w, v = self._project_style(w, assets, style_exposures)
                violations.extend(v)

            # 拥挤检测 (ρ>crowding_threshold → 减半；一次性响应 #205)
            if correlation_matrix is not None:
                w, v = self._apply_crowding(w, assets, correlation_matrix, crowding_scaled)
                violations.extend(v)

            # 杠杆约束: Σw ≤ max_gross_leverage
            w, v = self._project_leverage(w, risk_limits)
            violations.extend(v)

            # 归一化到 [0, max_gross_leverage]
            w = self._normalize(w, risk_limits.max_gross_leverage)

            # 收敛判定
            delta = float(np.max(np.abs(w - w_prev))) if len(w) > 0 else 0.0
            if delta < cfg.tol:
                converged = True
                logger.debug(
                    "Constraint solver converged at iteration %d (delta=%.2e)",
                    iteration + 1,
                    delta,
                )
                break

        iterations = iteration + 1 if not converged else iteration + 1
        if not converged:
            logger.warning("Constraint solver did not converge after %d iterations", cfg.max_iter)

        final_sum = float(np.sum(w))
        scaling = original_sum / final_sum if final_sum > 0 else 1.0

        # AI-NIGHT-001：权重坍缩兜底检测——Σw 较原始值消失 99%+ 必为迭代缩放失控
        # （原实现对坍缩仍报 converged=True，静默清零组合=最恶劣失效形态）
        if original_sum > 0 and final_sum < original_sum * 0.01:
            logger.error(
                "约束求解权重坍缩: Σw %.6f → %.2e（迭代失控），强制标记不收敛",
                original_sum,
                final_sum,
            )
            converged = False
            violations.append(
                ConstraintViolation(
                    constraint_id="COLLAPSE",
                    constraint_name="weight_collapse_guard",
                    symbol="portfolio",
                    original_value=original_sum,
                    threshold=original_sum * 0.01,
                    scaling_applied=scaling,
                )
            )

        return ConstraintSolveResult(
            weights=w,
            violations=list(violations),
            scaling_applied=scaling,
            converged=converged,
            iterations=iterations,
            timestamp=now,
        )

    # ── 约束投影方法 ──

    def _project_single_position(
        self, w: np.ndarray, assets: list[str], risk_limits: RiskLimits
    ) -> tuple[np.ndarray, list[ConstraintViolation]]:
        """C7: 单标的仓位上限裁剪。"""
        violations: list[ConstraintViolation] = []
        max_pos = risk_limits.max_single_position
        min_pos = risk_limits.min_single_position
        symbol_overrides = risk_limits.symbol_overrides or {}

        for i, sym in enumerate(assets):
            limit = symbol_overrides.get(sym, max_pos)
            if w[i] > limit:
                violations.append(
                    ConstraintViolation(
                        constraint_id="C7",
                        constraint_name="single_position",
                        symbol=sym,
                        original_value=float(w[i]),
                        threshold=limit,
                        scaling_applied=limit / float(w[i]) if w[i] > 0 else 1.0,
                    )
                )
                w[i] = limit
            # AI-NIGHT-001 #208-③：区分"零权重刻意排除"与"小权重抬升"——
            # w=0 是上游刻意排除（或硬拥挤清零）的语义，每轮强制抬回 min_pos
            # 会破坏排除意图；仅 0<w<min_pos 的微量仓位抬升到 min_pos。
            if 0.0 < w[i] < min_pos:
                w[i] = min_pos
        return w, violations

    def _project_sector_absolute(
        self,
        w: np.ndarray,
        assets: list[str],
        sector_mapping: dict[str, str],
        risk_limits: RiskLimits,
    ) -> tuple[np.ndarray, list[ConstraintViolation]]:
        """C1: 行业绝对集中度裁剪 (≤max_sector_concentration)。"""
        violations: list[ConstraintViolation] = []
        max_sector = risk_limits.max_sector_concentration
        sector_weights = self._aggregate_sectors(w, assets, sector_mapping)

        for sector, sw in sector_weights.items():
            if sw > max_sector:
                scale = max_sector / sw if sw > 0 else 1.0
                for i, sym in enumerate(assets):
                    if sector_mapping.get(sym) == sector:
                        w[i] *= scale
                violations.append(
                    ConstraintViolation(
                        constraint_id="C1",
                        constraint_name="sector_absolute",
                        symbol=sector,
                        original_value=sw,
                        threshold=max_sector,
                        scaling_applied=scale,
                    )
                )
        return w, violations

    def _project_sector_relative(
        self,
        w: np.ndarray,
        assets: list[str],
        sector_mapping: dict[str, str],
        benchmark: dict[str, float],
    ) -> tuple[np.ndarray, list[ConstraintViolation]]:
        """C2: 行业相对偏移裁剪 (±sector_relative_deviation)。"""
        violations: list[ConstraintViolation] = []
        max_dev = self._config.sector_relative_deviation
        sector_weights = self._aggregate_sectors(w, assets, sector_mapping)
        total = float(np.sum(w))
        if total <= 0:
            return w, violations

        for sector, sw in sector_weights.items():
            sw_pct = sw / total
            bw = benchmark.get(sector, 0.0)
            deviation = sw_pct - bw
            if abs(deviation) > max_dev:
                target_pct = bw + max_dev if deviation > 0 else bw - max_dev
                target_w = target_pct * total
                scale = target_w / sw if sw > 0 else 1.0
                for i, sym in enumerate(assets):
                    if sector_mapping.get(sym) == sector:
                        w[i] *= scale
                violations.append(
                    ConstraintViolation(
                        constraint_id="C2",
                        constraint_name="sector_relative",
                        symbol=sector,
                        original_value=sw_pct,
                        threshold=bw,
                        scaling_applied=scale,
                    )
                )
        return w, violations

    def _project_market_cap(
        self,
        w: np.ndarray,
        assets: list[str],
        exposures: dict[str, float],
    ) -> tuple[np.ndarray, list[ConstraintViolation]]:
        """C3: 市值暴露裁剪 (±max_market_cap_exposure_sigma)。"""
        violations: list[ConstraintViolation] = []
        max_exp = self._config.max_market_cap_exposure_sigma
        total = float(np.sum(w))
        if total <= 0:
            return w, violations

        weighted_exp = sum(w[i] * exposures.get(sym, 0.0) for i, sym in enumerate(assets)) / total
        if abs(weighted_exp) > max_exp:
            # AI-NIGHT-001 #207：统一缩放仅当存在"不随缩锚"（反向或零暴露标的）时才能
            # 改变加权平均暴露（锚侧不动、同号侧缩放→均值移动）；全同号暴露场景分子
            # 分母同乘 scale、均值不变→迭代每轮重复缩放必致权重几何坍缩（实证 Σw→1e-6
            # 且 converged=True）。不可达场景标 infeasible 不缩放（fail-visible）。
            has_anchor = any(exposures.get(sym, 0.0) * weighted_exp <= 0 for sym in assets)
            if not has_anchor:
                violations.append(
                    ConstraintViolation(
                        constraint_id="C3",
                        constraint_name="market_cap_exposure_infeasible",
                        symbol="portfolio",
                        original_value=weighted_exp,
                        threshold=max_exp,
                        scaling_applied=1.0,
                    )
                )
                return w, violations
            scale = max_exp / abs(weighted_exp) if weighted_exp != 0 else 1.0
            for i, sym in enumerate(assets):
                exp = exposures.get(sym, 0.0)
                if exp * weighted_exp > 0:
                    w[i] *= scale
            violations.append(
                ConstraintViolation(
                    constraint_id="C3",
                    constraint_name="market_cap_exposure",
                    symbol="portfolio",
                    original_value=weighted_exp,
                    threshold=max_exp,
                    scaling_applied=scale,
                )
            )
        return w, violations

    def _project_correlation(
        self,
        w: np.ndarray,
        assets: list[str],
        corr: np.ndarray,
        already_scaled: set[tuple[int, int]] | None = None,
    ) -> tuple[np.ndarray, list[ConstraintViolation]]:
        """C5: 标的相关性裁剪 (≤max_correlation)。

        AI-NIGHT-001 #205 同族：触发条件仅依赖静态 ρ（相关矩阵不变）→ 原实现
        每轮迭代重复缩放较大者，几何坍缩（与软拥挤同根因）。改为一次性响应
        （already_scaled 记忆，同一对相关轮次不重复缩放）。
        """
        violations: list[ConstraintViolation] = []
        max_corr = self._config.max_correlation
        n = len(assets)
        if corr.shape[0] != n or corr.shape[1] != n:
            raise CorrelationGateFailure(f"correlation_matrix shape {corr.shape} != ({n},{n})")

        for i in range(n):
            for j in range(i + 1, n):
                rho = abs(float(corr[i, j]))
                if rho > max_corr:
                    if already_scaled is not None and (i, j) in already_scaled:
                        continue  # 一次性响应（#205 同族）
                    # 高相关对: 降权较大者
                    if w[i] >= w[j]:
                        scale = (1.0 - (rho - max_corr)) if rho < 1.0 else 0.5
                        w[i] *= max(scale, 0.5)
                        sym = assets[i]
                    else:
                        scale = (1.0 - (rho - max_corr)) if rho < 1.0 else 0.5
                        w[j] *= max(scale, 0.5)
                        sym = assets[j]
                    if already_scaled is not None:
                        already_scaled.add((i, j))
                    violations.append(
                        ConstraintViolation(
                            constraint_id="C5",
                            constraint_name="asset_correlation",
                            symbol=f"{assets[i]}:{assets[j]}",
                            original_value=rho,
                            threshold=max_corr,
                            scaling_applied=max(scale, 0.5),
                        )
                    )
        return w, violations

    def _project_style(
        self,
        w: np.ndarray,
        assets: list[str],
        exposures: dict[str, float],
    ) -> tuple[np.ndarray, list[ConstraintViolation]]:
        """C6: 风格因子暴露裁剪 (±max_style_exposure_sigma)。"""
        violations: list[ConstraintViolation] = []
        max_exp = self._config.max_style_exposure_sigma
        total = float(np.sum(w))
        if total <= 0:
            return w, violations

        weighted_exp = sum(w[i] * exposures.get(sym, 0.0) for i, sym in enumerate(assets)) / total
        if abs(weighted_exp) > max_exp:
            # AI-NIGHT-001 #207：同 C3——全同号风格暴露下统一缩放数学无效，
            # 迭代重复缩放必坍缩；标 infeasible 不缩放（fail-visible）。
            has_anchor = any(exposures.get(sym, 0.0) * weighted_exp <= 0 for sym in assets)
            if not has_anchor:
                violations.append(
                    ConstraintViolation(
                        constraint_id="C6",
                        constraint_name="style_exposure_infeasible",
                        symbol="portfolio",
                        original_value=weighted_exp,
                        threshold=max_exp,
                        scaling_applied=1.0,
                    )
                )
                return w, violations
            scale = max_exp / abs(weighted_exp) if weighted_exp != 0 else 1.0
            for i, sym in enumerate(assets):
                exp = exposures.get(sym, 0.0)
                if exp * weighted_exp > 0:
                    w[i] *= scale
            violations.append(
                ConstraintViolation(
                    constraint_id="C6",
                    constraint_name="style_exposure",
                    symbol="portfolio",
                    original_value=weighted_exp,
                    threshold=max_exp,
                    scaling_applied=scale,
                )
            )
        return w, violations

    def _apply_crowding(
        self,
        w: np.ndarray,
        assets: list[str],
        corr: np.ndarray,
        already_scaled: set[tuple[int, int]] | None = None,
    ) -> tuple[np.ndarray, list[ConstraintViolation]]:
        """拥挤检测: ρ>threshold → 权重减半; ρ>hard_threshold → 仅保留其一。

        AI-NIGHT-001 #205：软拥挤缩放为一次性响应（already_scaled 记忆）——
        原实现每轮迭代重复减半，触发条件仅依赖静态 ρ → 权重 0.5^n 几何坍缩
        （实证 {0.5,0.5} ρ=0.85 → 16 轮 Σw≈8e-7 且 converged=True 静默）。
        """
        violations: list[ConstraintViolation] = []
        cfg = self._config
        n = len(assets)

        for i in range(n):
            for j in range(i + 1, n):
                rho = abs(float(corr[i, j]))
                if rho > cfg.crowding_hard_threshold:
                    # 硬拥挤: 仅保留权重较大者
                    if w[i] >= w[j]:
                        w[j] = 0.0
                        sym = assets[j]
                    else:
                        w[i] = 0.0
                        sym = assets[i]
                    violations.append(
                        ConstraintViolation(
                            constraint_id="CROWD",
                            constraint_name="crowding_hard",
                            symbol=f"{assets[i]}:{assets[j]}",
                            original_value=rho,
                            threshold=cfg.crowding_hard_threshold,
                            scaling_applied=0.0,
                        )
                    )
                elif rho > cfg.crowding_threshold:
                    # 软拥挤: 权重减半（一次性——同一对不重复缩放）
                    if already_scaled is not None and (i, j) in already_scaled:
                        continue
                    w[i] *= cfg.crowding_scale
                    w[j] *= cfg.crowding_scale
                    if already_scaled is not None:
                        already_scaled.add((i, j))
                    violations.append(
                        ConstraintViolation(
                            constraint_id="CROWD",
                            constraint_name="crowding_soft",
                            symbol=f"{assets[i]}:{assets[j]}",
                            original_value=rho,
                            threshold=cfg.crowding_threshold,
                            scaling_applied=cfg.crowding_scale,
                        )
                    )
        return w, violations

    def _project_leverage(self, w: np.ndarray, risk_limits: RiskLimits) -> tuple[np.ndarray, list[ConstraintViolation]]:
        """杠杆约束: Σw ≤ max_gross_leverage。"""
        violations: list[ConstraintViolation] = []
        total = float(np.sum(w))
        max_lev = risk_limits.max_gross_leverage
        if total > max_lev:
            scale = max_lev / total if total > 0 else 1.0
            w = w * scale
            violations.append(
                ConstraintViolation(
                    constraint_id="LEV",
                    constraint_name="gross_leverage",
                    symbol="portfolio",
                    original_value=total,
                    threshold=max_lev,
                    scaling_applied=scale,
                )
            )
        return w, violations

    # ── 内部工具 ──

    @staticmethod
    def _parse_weights(
        weights: dict[str, float] | np.ndarray,
        assets: list[str] | None,
    ) -> tuple[list[str], np.ndarray]:
        """解析权重输入为 (assets, np.ndarray)。"""
        if isinstance(weights, dict):
            assets = list(weights.keys())
            w = np.array([weights[a] for a in assets], dtype=float)
        else:
            w = np.asarray(weights, dtype=float)
            if assets is None:
                assets = [f"asset_{i}" for i in range(len(w))]
            if len(assets) != len(w):
                raise ConstraintViolationError(f"assets count ({len(assets)}) != weights length ({len(w)})")
        if len(w) == 0:
            raise ConstraintViolationError("weights cannot be empty")
        # AI-NIGHT-001 #208-②：NaN/Inf 权重原静默通过（np.any(w<0) 对 NaN 为 False），
        # NaN 进入迭代投影污染全组合。H 级安全模块 fail-closed——非有限输入与
        # 空/负权重同口径直接 raise。
        if not np.all(np.isfinite(w)):
            raise ConstraintViolationError(f"weights must be finite (no NaN/Inf), got {w}")
        if np.any(w < 0):
            raise ConstraintViolationError(f"weights must be non-negative (long-only), got {w}")
        return assets, w

    @staticmethod
    def _aggregate_sectors(
        w: np.ndarray,
        assets: list[str],
        sector_mapping: dict[str, str],
    ) -> dict[str, float]:
        """聚合各行业权重。"""
        sector_w: dict[str, float] = {}
        for i, sym in enumerate(assets):
            sector = sector_mapping.get(sym, "unknown")
            sector_w[sector] = sector_w.get(sector, 0.0) + float(w[i])
        return sector_w

    @staticmethod
    def _normalize(w: np.ndarray, max_leverage: float) -> np.ndarray:
        """归一化到 [0, max_leverage]。"""
        total = float(np.sum(w))
        if total <= 0:
            return w
        if total > max_leverage:
            return w * (max_leverage / total)
        return w
