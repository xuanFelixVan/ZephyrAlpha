# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §4.2 B2 / §5
# [MODULE] zephyr.regime.validation.b2_crps
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan B2 概率预测技能(BM-BT-03-E)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯分析函数: 只消费既有逐日 7 维概率 + 事后主导态产物; 离散 CRPS=Σ_k(CDF_k−1{y≤k})²; climatology=样本经验频率常数预测; climatology CRPS=0(单一类别样本)→无法评估,抛错; frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] B2CRPSError(ZA-REGIME-0033)
# [TESTS] tests/regime/validation/test_b2_crps.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: prob_matrix(T,K) 逐日状态概率分布 + outcomes(T,) 事后实际主导态(0..K-1)
# F1: crps_categorical(单点离散 CRPS: CDF 与结局指示的平方偏差和)
# A1: evaluate_crps(模型均值 CRPS vs climatology CRPS → skill=1−model/clim → model<clim 判定)
# O1: B2CRPSReport(crps_model/crps_climatology/skill/passed)
# [/ALGO_FLOW]
"""
D_REGIME — B2 CRPS 概率预测技能（11 号 memo §4.2 B2）。

纯分析函数：消费既有逐日状态概率分布（7 维：4 HMM 基态 + 3 overlay）与
事后实际主导态，计算离散 CRPS（Cumulative Ranked Probability Score 的
类别形式），并对照 climatology 基准（样本经验频率常数预测）判定：
CRPS_model < CRPS_climatology → 概率分布比「永远预测平均频率」有技能。

依据: 11_regime_backtest_validation_plan §4.2 B2 / §5
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: probs 参数
#   fields: 参数 probs，类型注解 Sequence[float]
#   code: b2_crps.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: outcome 参数
#   fields: 参数 outcome，类型注解 int
#   code: b2_crps.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: prob_matrix 参数
#   fields: 参数 prob_matrix，类型注解 np.ndarray
#   code: b2_crps.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: outcomes 参数
#   fields: 参数 outcomes，类型注解 Sequence[int]
#   code: b2_crps.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① crps_categorical
#   name_en: crps_categorical
#   intro: 单点离散 CRPS：Σ_k (CDF_k − 1{outcome ≤ k})²。
#   desc: 单点离散 CRPS：Σ_k (CDF_k − 1{outcome ≤ k})²。 Args: probs: (K,) 状态概率分布（非负、和≈1）。 outcome: 实际状态索…；源码 L126-L147
#   inputs: probs outcome
#   outputs: float
# - id: A2
#   name_zh: ② evaluate_crps
#   name_en: evaluate_crps
#   intro: B2 主入口：模型 CRPS vs climatology 基准。
#   desc: B2 主入口：模型 CRPS vs climatology 基准。 Args: prob_matrix: (T, K) 逐日状态概率分布。 outcomes: (T,) 事后实际…；源码 L150-L193
#   inputs: prob_matrix outcomes
#   outputs: B2CRPSReport
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan B2 概率预测技能(BM-BT-03-E)
# - id: O2
#   name_zh: B2CRPSReport
#   name_en: B2CRPSReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan B2 概率预测技能(BM-BT-03-E)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Sequence

import numpy as np

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

_PROB_ATOL = 1e-4  # 概率和=1 容差


class B2CRPSError(ZephyrBaseError):
    """ZA-REGIME-0033: B2 CRPS 分析错误（输入非法/概率分布不合法）。"""

    error_code = "ZA-REGIME-0033"


@dataclass(frozen=True)
class B2CRPSReport:
    """B2 CRPS 技能报告——不可变。"""

    n_samples: int
    n_states: int
    crps_model: float  # 模型平均 CRPS（越小越好）
    crps_climatology: float  # climatology 基准平均 CRPS
    skill: float  # 1 − model/climatology（>0 有技能）
    passed: bool  # crps_model < crps_climatology（§4.2 B2）
    summary: str


def crps_categorical(probs: Sequence[float], outcome: int) -> float:
    """单点离散 CRPS：Σ_k (CDF_k − 1{outcome ≤ k})²。

    Args:
        probs: (K,) 状态概率分布（非负、和≈1）。
        outcome: 实际状态索引（0..K-1）。

    Raises:
        B2CRPSError: 分布非法 / outcome 越界。
    """
    p = np.asarray(probs, dtype=float)
    if p.ndim != 1 or p.size < 2:
        raise B2CRPSError(f"probs 须为 (K≥2,) 向量: shape={p.shape}")
    if not np.isfinite(p).all() or (p < 0).any():
        raise B2CRPSError("probs 含非法值（NaN/Inf/负数）")
    if abs(float(p.sum()) - 1.0) > _PROB_ATOL:
        raise B2CRPSError(f"probs 和须≈1: {float(p.sum())}")
    if not 0 <= outcome < p.size:
        raise B2CRPSError(f"outcome 越界: {outcome}（K={p.size}）")
    cdf = np.cumsum(p)
    indicators = (np.arange(p.size) >= outcome).astype(float)
    return float(np.sum((cdf - indicators) ** 2))


def evaluate_crps(
    prob_matrix: np.ndarray,
    outcomes: Sequence[int],
) -> B2CRPSReport:
    """B2 主入口：模型 CRPS vs climatology 基准。

    Args:
        prob_matrix: (T, K) 逐日状态概率分布。
        outcomes: (T,) 事后实际主导态（0..K-1）。

    Raises:
        B2CRPSError: 维度不符 / 空样本 / climatology CRPS=0（单一类别样本，无法评估技能）。
    """
    P = np.asarray(prob_matrix, dtype=float)
    if P.ndim != 2 or P.shape[0] < 1:
        raise B2CRPSError(f"prob_matrix 须为 (T≥1, K) 二维: {P.shape}")
    T, K = P.shape
    y = np.asarray(outcomes, dtype=int)
    if y.shape != (T,):
        raise B2CRPSError(f"outcomes 长度须={T}: {y.shape}")
    if (y < 0).any() or (y >= K).any():
        raise B2CRPSError(f"outcomes 越界 [0,{K})")

    model = float(np.mean([crps_categorical(P[t], int(y[t])) for t in range(T)]))
    freq = np.bincount(y, minlength=K).astype(float) / T
    clim = float(np.mean([crps_categorical(freq, int(y[t])) for t in range(T)]))
    if clim <= 0.0:
        raise B2CRPSError("climatology CRPS=0（样本单一类别），无法评估技能")
    skill = 1.0 - model / clim
    passed = model < clim
    summary = (
        f"B2 CRPS: {T} 样本 × {K} 态, model={model:.4f} climatology={clim:.4f} "
        f"skill={skill:+.3f} → {'有技能（优于 climatology）' if passed else '无技能'}"
    )
    _logger.info("B2 完成: %s", summary)
    return B2CRPSReport(
        n_samples=T,
        n_states=K,
        crps_model=model,
        crps_climatology=clim,
        skill=skill,
        passed=passed,
        summary=summary,
    )


__all__ = [
    "B2CRPSError",
    "B2CRPSReport",
    "crps_categorical",
    "evaluate_crps",
]
