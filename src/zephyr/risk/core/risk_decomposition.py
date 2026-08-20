# [BLUEPRINT] MOD-RK-16 | docs/03_modules/_domain_risk/risk_decomposition/blueprint.md
# [MODULE] zephyr.risk.core.risk_decomposition
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy; MOD-RK-05(VaR输入)
# [CONSUMERS] MOD-RK-08(Risk Budget Allocator,风险贡献复用) ; MOD-RK-20(Daily Auditor,归因报告)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] factor_risk+residual_risk=total_risk(平方和守恒);CCR之和=σ_p;MCR=Σw/σ_p;权重归一化(Σw=1)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDecompositionInputError
# [TESTS] tests/risk/test_risk_decomposition.py
# [A_module] module_id=MOD-RK-16 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Risk Decomposition Engine — 风险分解引擎 (MOD-RK-16)

D-RISK §1.2 L3 Post-Trade 盘后审计核心模块。将组合风险分解为可归因的成分:
    1. 因子风险 (Factor Risk): 系统性风险, 由因子模型解释的部分
       - σ_p² = w'(BΣ_fB' + Σ_ε)w = w'BΣ_fB'w + w'Σ_εw
       - factor_risk² = w'BΣ_fB'w  (因子贡献的方差)
    2. 残差风险 (Residual Risk): 个股特异性风险, 因子无法解释的部分
       - residual_risk² = w'Σ_εw
    3. 边际风险贡献 (Marginal Contribution to Risk, MCR):
       - MCR_i = ∂σ_p/∂w_i = (Σw)_i / σ_p
    4. 成分风险贡献 (Component Contribution to Risk, CCR):
       - CCR_i = w_i · MCR_i,  ΣCCR_i = σ_p (守恒)
    5. 百分比贡献 (Percentage Contribution): CCR_i / σ_p

供 RK-08 风险预算分配 (复用 CCR) + RK-20 日终归因报告。

属 A 类基础设施 (矩阵运算 + 偏导, 数学逻辑明确), 因子模型为 B 类可选输入。
依据: D:\临时工作区\依赖图	-D-RISK-风控域.md §1.2 RK-16, §2 依赖(RK-05→RK-16)
SSoT: depgraph MOD-RK-16
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 协方差矩阵 np.ndarray
#   fields: cov (N,N)资产收益协方差矩阵, 对称半正定, 应≈BΣ_fB'+diag(ε)
#   code: decompose() cov L182
# - id: I2
#   name: 权重向量 np.ndarray
#   fields: weights (N,)持仓权重, 拒绝负权重(long-only), 自动归一化Σw=1
#   code: decompose() weights L183
# - id: I3
#   name: 因子模型三件套 np.ndarray
#   fields: factor_loadings B(N,K)因子载荷 + factor_cov Σ_f(K,K)因子协方差 + residual_var ε(N,)残差方差
#   code: decompose_with_factors() L224-226
# 层: 算法
# - id: A1
#   name_zh: ① 输入校验与权重归一化
#   name_en: _validate
#   intro: 检查协方差方阵维度匹配权重非负再归一化
#   desc: cov必须2D方阵; weights维度=N且全非负且和>0; weights/=Σw
#   inputs: I1 I2
#   outputs: 归一化后的(cov, weights)
#   invariant: 权重归一化Σw=1
# - id: A2
#   name_zh: ② 组合总风险
#   name_en: decompose
#   intro: 矩阵二次型算组合方差和标准差
#   desc: total_var=w'Σw; total_risk=√total_var
#   inputs: A1
#   outputs: total_variance + total_risk σ_p
# - id: A3
#   name_zh: ③ 因子残差方差分解
#   name_en: decompose_with_factors
#   intro: 把总方差拆成因子能解释的和个股特异的两块
#   desc: Bw=B'w; factor_var=Bw'Σ_f Bw; resid_var=Σ ε_i w_i²(对角残差); 校验B/Σ_f/ε维度
#   inputs: A1 I3
#   outputs: factor_variance + residual_variance
#   invariant: factor_risk+residual_risk=total_risk(平方和守恒)
# - id: A4
#   name_zh: ④ 边际与成分风险贡献
#   name_en: _contributions
#   intro: 算每个资产对总风险的边际贡献和成分贡献
#   desc: MCR=(Σw)/σ_p; CCR=w⊙MCR; pct=CCR/σ_p; σ_p<=0时全零
#   inputs: A1 A2
#   outputs: mcr + ccr + pct_contribution 向量
#   invariant: ΣCCR=σ_p; Σpct=1
# 层: 输出
# - id: O1
#   name_zh: 风险分解结果
#   name_en: DecompositionResult
#   intro: 含总风险/因子残差分解/MCR/CCR/百分比贡献的frozen结果对象
#   invariant: factor_risk²+residual_risk²=total_risk²
#   downstream: MOD-RK-08(Risk Budget Allocator 风险贡献复用); MOD-RK-20(Daily Auditor 归因报告)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A3
# A1 --> A2
# A1 --> A3
# A2 --> A4
# A1 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "DecompositionResult",
    "RiskDecomposer",
    "InvalidDecompositionInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidDecompositionInputError(ZephyrBaseError):
    """风险分解输入数据非法 (如协方差矩阵非方阵、权重维度不匹配)。"""

    error_code = "ZA-RK-0016"


# ──────────────────────────────────────────────────────────────────────────────
# 计算结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DecompositionResult:
    """风险分解结果。

    所有风险以方差 (variance) 或标准差 (std) 形式给出, 非金额。

    Attributes:
        total_risk: 组合标准差 σ_p = sqrt(w'Σw)
        total_variance: 组合方差 w'Σw
        factor_risk: 因子贡献的标准差 (None=无因子模型)
        factor_variance: 因子贡献的方差 (None=无因子模型)
        residual_risk: 残差标准差 (None=无因子模型)
        residual_variance: 残差方差 (None=无因子模型)
        mcr: 边际风险贡献向量 (N,), MCR_i = (Σw)_i / σ_p
        ccr: 成分风险贡献向量 (N,), CCR_i = w_i · MCR_i, ΣCCR_i = σ_p
        pct_contribution: 百分比贡献向量 (N,), CCR_i / σ_p, 和为 1
        assets: 资产代码列表 (可选, 用于可读输出)
        weights: 归一化权重向量
        timestamp: 计算时间
    """

    total_risk: float
    total_variance: float
    mcr: np.ndarray
    ccr: np.ndarray
    pct_contribution: np.ndarray
    weights: np.ndarray
    timestamp: datetime
    assets: list[str] | None = None
    factor_risk: float | None = None
    factor_variance: float | None = None
    residual_risk: float | None = None
    residual_variance: float | None = None

    @property
    def has_factor_model(self) -> bool:
        """是否提供了因子模型分解。"""
        return self.factor_variance is not None

    @property
    def factor_contribution_pct(self) -> float | None:
        """因子贡献占总风险比例 (0~1)。"""
        if self.factor_variance is None or self.total_variance <= 0:
            return None
        return self.factor_variance / self.total_variance

    @property
    def residual_contribution_pct(self) -> float | None:
        """残差贡献占总风险比例 (0~1)。"""
        if self.residual_variance is None or self.total_variance <= 0:
            return None
        return self.residual_variance / self.total_variance

    def to_dict(self) -> dict[str, Any]:
        """转为字典 (供事件/日志)。"""
        return {
            "total_risk": self.total_risk,
            "total_variance": self.total_variance,
            "factor_risk": self.factor_risk,
            "factor_variance": self.factor_variance,
            "residual_risk": self.residual_risk,
            "residual_variance": self.residual_variance,
            "factor_contribution_pct": self.factor_contribution_pct,
            "residual_contribution_pct": self.residual_contribution_pct,
            "mcr": self.mcr.tolist(),
            "ccr": self.ccr.tolist(),
            "pct_contribution": self.pct_contribution.tolist(),
            "weights": self.weights.tolist(),
            "assets": self.assets,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 风险分解引擎
# ──────────────────────────────────────────────────────────────────────────────


class RiskDecomposer:
    """风险分解引擎——因子/残差分解 + 边际/成分风险贡献。

    用法 (基础, 无因子模型):
        decomposer = RiskDecomposer()
        cov = np.array([[0.04, 0.01], [0.01, 0.09]])
        weights = np.array([0.6, 0.4])
        result = decomposer.decompose(cov, weights)

    用法 (含因子模型):
        # B: (N, K) 因子载荷, factor_cov: (K, K) 因子协方差, resid_var: (N,) 残差方差
        result = decomposer.decompose_with_factors(cov, weights, B, factor_cov, resid_var)

    数学:
        - σ_p = sqrt(w'Σw)
        - MCR = Σw / σ_p  (边际风险贡献)
        - CCR = w ⊙ MCR   (成分风险贡献, 和 = σ_p)
        - factor_variance = w'BΣ_fB'w
        - residual_variance = w'Σ_εw = Σ ε_i² w_i² (对角残差)
    """

    def __init__(self) -> None:
        pass

    # ── 公开 API ──

    def decompose(
        self,
        cov: np.ndarray,
        weights: np.ndarray,
        assets: list[str] | None = None,
        now: datetime | None = None,
    ) -> DecompositionResult:
        """基础风险分解 (无因子模型, 仅 MCR/CCR)。

        Args:
            cov: 协方差矩阵 (N, N), 对称半正定
            weights: 权重向量 (N,), 自动归一化
            assets: 资产代码列表 (可选)
            now: 时间戳

        Returns:
            DecompositionResult (factor_*/residual_* 均为 None)

        Raises:
            InvalidDecompositionInputError: 维度不匹配 / 协方差非方阵 / 权重全非正
        """
        cov, weights = self._validate(cov, weights)
        now = now or datetime.now(timezone.utc)

        total_var = float(weights @ cov @ weights)
        total_risk = float(np.sqrt(total_var)) if total_var > 0 else 0.0

        mcr, ccr, pct = self._contributions(cov, weights, total_risk)

        return DecompositionResult(
            total_risk=total_risk,
            total_variance=total_var,
            mcr=mcr,
            ccr=ccr,
            pct_contribution=pct,
            weights=weights,
            assets=assets,
            timestamp=now,
        )

    def decompose_with_factors(
        self,
        cov: np.ndarray,
        weights: np.ndarray,
        factor_loadings: np.ndarray,
        factor_cov: np.ndarray,
        residual_var: np.ndarray,
        assets: list[str] | None = None,
        now: datetime | None = None,
    ) -> DecompositionResult:
        """含因子模型的风险分解 (因子 + 残差 + MCR/CCR)。

        Args:
            cov: 协方差矩阵 (N, N), 应满足 cov ≈ BΣ_fB' + diag(ε)
            weights: 权重向量 (N,)
            factor_loadings: B (N, K), K=因子数
            factor_cov: Σ_f (K, K), 因子协方差矩阵
            residual_var: ε (N,), 残差方差向量 (对角)
            assets: 资产代码列表
            now: 时间戳

        Returns:
            DecompositionResult (含 factor_*/residual_* 分解)
        """
        cov, weights = self._validate(cov, weights)
        now = now or datetime.now(timezone.utc)
        B = np.asarray(factor_loadings, dtype=float)
        Sigma_f = np.asarray(factor_cov, dtype=float)
        eps = np.asarray(residual_var, dtype=float)
        N = len(weights)
        K = B.shape[1] if B.ndim == 2 else 0

        # 校验因子模型维度
        if B.ndim != 2 or B.shape[0] != N:
            raise InvalidDecompositionInputError(f"factor_loadings shape {B.shape} must be (N={N}, K)")
        if Sigma_f.shape != (K, K):
            raise InvalidDecompositionInputError(f"factor_cov shape {Sigma_f.shape} must be ({K}, {K})")
        if eps.shape != (N,):
            raise InvalidDecompositionInputError(f"residual_var shape {eps.shape} must be ({N},)")

        total_var = float(weights @ cov @ weights)
        total_risk = float(np.sqrt(total_var)) if total_var > 0 else 0.0

        # 因子贡献方差 = w' B Σ_f B' w
        Bw = B.T @ weights  # (K,)
        factor_var = float(Bw @ Sigma_f @ Bw)
        # 残差贡献方差 = Σ ε_i w_i² (对角)
        resid_var = float(np.sum(eps * weights * weights))

        mcr, ccr, pct = self._contributions(cov, weights, total_risk)

        logger.info(
            "Risk decomposed: total=%.6f factor=%.6f (%.1f%%) residual=%.6f (%.1f%%) K=%d",
            total_risk,
            np.sqrt(max(factor_var, 0.0)),
            100 * factor_var / total_var if total_var > 0 else 0,
            np.sqrt(max(resid_var, 0.0)),
            100 * resid_var / total_var if total_var > 0 else 0,
            K,
        )

        return DecompositionResult(
            total_risk=total_risk,
            total_variance=total_var,
            mcr=mcr,
            ccr=ccr,
            pct_contribution=pct,
            weights=weights,
            assets=assets,
            factor_risk=float(np.sqrt(max(factor_var, 0.0))),
            factor_variance=factor_var,
            residual_risk=float(np.sqrt(max(resid_var, 0.0))),
            residual_variance=resid_var,
            timestamp=now,
        )

    # ── 内部: 计算 ──

    @staticmethod
    def _contributions(
        cov: np.ndarray, weights: np.ndarray, total_risk: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """计算 MCR, CCR, 百分比贡献。

        - MCR_i = (Σw)_i / σ_p
        - CCR_i = w_i · MCR_i
        - pct_i = CCR_i / σ_p
        """
        if total_risk <= 0:
            N = len(weights)
            return (
                np.zeros(N),
                np.zeros(N),
                np.zeros(N),
            )
        sigma_w = cov @ weights  # (N,)
        mcr = sigma_w / total_risk
        ccr = weights * mcr
        pct = ccr / total_risk
        return mcr, ccr, pct

    # ── 内部: 校验 ──

    @staticmethod
    def _validate(cov: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """校验协方差矩阵与权重, 返回归一化后的 (cov, weights)。"""
        cov = np.asarray(cov, dtype=float)
        weights = np.asarray(weights, dtype=float)
        if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
            raise InvalidDecompositionInputError(f"cov must be square 2D, got shape {cov.shape}")
        N = cov.shape[0]
        if weights.ndim != 1 or weights.shape[0] != N:
            raise InvalidDecompositionInputError(f"weights shape {weights.shape} mismatched with cov ({N}, {N})")
        # 拒绝负权重 (long-only 假设; 允许 0)
        if np.any(weights < 0):
            raise InvalidDecompositionInputError(f"negative weights not allowed: {weights}")
        total = float(np.sum(weights))
        if total <= 0:
            raise InvalidDecompositionInputError(f"weights sum must be positive, got {total}")
        weights = weights / total  # 归一化
        return cov, weights
