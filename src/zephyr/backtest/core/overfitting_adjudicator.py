# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.overfitting_adjudicator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.overfitting_detector; zephyr.simulation.deflated_sharpe_calculator
# [CONSUMERS] 上线评审流程(挂钩点预留, 未接真门禁)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三检验器纯统计; OOS/IS阈值0.70与扰动容忍0.30复用overfitting_detector SSoT; DSR显著线0.95复用MOD-SIM-024 SSoT; backtest引擎走注入callable契约; 报告frozen不可变; 无有效折fail-closed
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OverfittingAdjudicationError(ZA-BT-0036)
# [TESTS] tests/backtest/test_overfitting_adjudicator.py
# [TTL] permanent
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
"""
P-5 过拟合裁定协议组件(三检验器 + 上线门禁挂钩点预留)

职责:
  - 检验器① walk-forward 汇总: 各折 OOS/IS 衰减比分布(mean/std/min) + 最差折定位,
    阈值复用 overfitting_detector.DEFAULT_OOS_SHARPE_THRESHOLD_RATIO=0.70(P0-9 SSoT);
    IS<=0 折不适用比率(对齐 compare_in_out_sample 口径), 无有效折 fail-closed 判不稳定
  - 检验器② Deflated Sharpe Ratio: Bailey & López de Prado (2014) 闭式,
    E[max(Z_N)]≈(1−γ)Φ⁻¹(1−1/N)+γΦ⁻¹(1−1/(N·e)) (γ=Euler–Mascheroni 常数);
    输入=观测Sharpe/试验次数/收益矩(偏度+超额峰度)/样本量, 输出=DSR≥阈值判定,
    显著性阈值复用 MOD-SIM-024 DSR_SIGNIFICANCE_THRESHOLD=0.95(SSoT)
  - 检验器③ 参数扰动±20%收益稳定性: one-at-a-time ±pct 网格,
    回测引擎走注入 callable 契约(不硬绑引擎, 合成伪引擎可测);
    绩效衰减率=(基准−扰动)/|基准|, 稳健区间占比=衰减率≤容忍度的扰动点占比,
    容忍度复用 overfitting_detector.PARAM_MAX_CHANGE_THRESHOLD=0.30(SSoT)
  - 上线门禁挂钩点: OverfitGateHook Protocol 预留, gate_hook=None 默认不接真门禁

约束:
  - 不重造轮子: 切分/三维度检测/扰动引擎既有件(walk_forward/overfitting_detector/
    parameter_robustness_tester)之上做裁定口径汇总, 仅阈值常量单向导入复用
  - Φ⁻¹ 用 Acklam 有理逼近 + 一步 Newton 精化(纯 math, 无 scipy 硬依赖)

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: num_trials 参数
#   fields: 参数 num_trials，类型注解 int
#   code: overfitting_adjudicator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: sharpe 参数
#   fields: 参数 sharpe，类型注解 float
#   code: overfitting_adjudicator.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: num_obs 参数
#   fields: 参数 num_obs，类型注解 int
#   code: overfitting_adjudicator.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: skewness 参数
#   fields: 参数 skewness，类型注解 float
#   code: overfitting_adjudicator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① expected_max_sharpe_z
#   name_en: expected_max_sharpe_z
#   intro: 多重试验期望最大值 E[max(Z_N)](Bailey & López de Prado 2014 闭式)。
#   desc: 多重试验期望最大值 E[max(Z_N)](Bailey & López de Prado 2014 闭式)。 N=1: 0(无多重试验膨胀) N>1: E[max(Z_N)]≈…；源码 L263-L285
#   inputs: num_trials
#   outputs: float
# - id: A2
#   name_zh: ② adjudicate_dsr
#   name_en: adjudicate_dsr
#   intro: DSR 裁定: 多次试验后真实 Sharpe 折减(Bailey & López de Prado 2014)。
#   desc: DSR 裁定: 多次试验后真实 Sharpe 折减(Bailey & López de Prado 2014)。 DSR = Φ((SR − E[max SR]) / √V[SR…；源码 L317-L391
#   inputs: sharpe num_trials num_obs skewness kurtosis threshold
#   outputs: DSRVerdict
# - id: A3
#   name_zh: ③ summarize_walk_forward
#   name_en: summarize_walk_forward
#   intro: 检验器①: 各折 OOS/IS 衰减比分布 + 最差折汇总。
#   desc: 检验器①: 各折 OOS/IS 衰减比分布 + 最差折汇总。 Args: folds: 各折 (is_sharpe, oos_sharpe) 对, 至少 1 折; IS<=0 折…；源码 L428-L494
#   inputs: folds threshold
#   outputs: WalkForwardDecaySummary
# - id: A4
#   name_zh: ④ perturbation_stability
#   name_en: perturbation_stability
#   intro: 检验器③: 策略参数 ±pct one-at-a-time 扰动, 统计绩效衰减率与稳健区间占比。
#   desc: 检验器③: 策略参数 ±pct one-at-a-time 扰动, 统计绩效衰减率与稳健区间占比。 回测引擎走契约接口: backtest_fn(params) -> 绩效标量(…；源码 L550-L642
#   inputs: base_params backtest_fn pct tolerance min_robust_share
#   outputs: PerturbationStabilityReport
# - id: A5
#   name_zh: ⑤ OverfitGateHook
#   name_en: OverfitGateHook
#   intro: 上线门禁挂钩点 Protocol——预留接口, 默认不接真门禁。
#   desc: 上线门禁挂钩点 Protocol——预留接口, 默认不接真门禁。 真门禁实现方(上线流水线)按本 Protocol 注入: 裁定完成后收到 OverfitAdjudication…；公共方法（定义序）: on_adju…
#   inputs: 无参数
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ OverfittingAdjudicator
#   name_en: OverfittingAdjudicator
#   intro: P-5 过拟合裁定器: 三检验器编排 + 门禁挂钩点回调。
#   desc: P-5 过拟合裁定器: 三检验器编排 + 门禁挂钩点回调。 未提供的检验器视为未检测(不参与否决), 与 overfitting_detector.detect 口径一致。 ga…；公共方法（定义序）: adjudic…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A6 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 上线评审流程(挂钩点预留, 未接真门禁)
# - id: O2
#   name_zh: DSRVerdict
#   name_en: DSRVerdict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 上线评审流程(挂钩点预留, 未接真门禁)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol, Sequence, runtime_checkable

from zephyr.backtest.core.overfitting_detector import (
    DEFAULT_OOS_SHARPE_THRESHOLD_RATIO,
    PARAM_MAX_CHANGE_THRESHOLD,
)
from zephyr.simulation.deflated_sharpe_calculator import DSR_SIGNIFICANCE_THRESHOLD

_logger = logging.getLogger(__name__)

_EPS = 1e-12

#: Euler–Mascheroni 常数 γ(Bailey & López de Prado 2014 E[max] 闭式)
EULER_MASCHERONI = 0.5772156649015329

#: 参数扰动默认幅度(P-5 协议口径: ±20%)
DEFAULT_PERTURBATION_PCT = 0.20


class OverfittingAdjudicationError(Exception):
    """P-5 过拟合裁定错误(输入非法/契约违反)。"""

    error_code = "ZA-BT-0036"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


# ---------------------------------------------------------------------------
# 正态分布 Φ / Φ⁻¹(纯 math 实现)
# ---------------------------------------------------------------------------


def _normal_cdf(x: float) -> float:
    """标准正态 CDF Φ(x), math.erf 实现。"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# Acklam 有理逼近系数(Φ⁻¹, 最大绝对误差 ~1.15e-9, 再经 Newton 精化至机器精度)
_ACKLAM_A = (
    -3.969683028665376e01,
    2.209460984245205e02,
    -2.759285104469687e02,
    1.383577518672690e02,
    -3.066479806614716e01,
    2.506628277459239e00,
)
_ACKLAM_B = (
    -5.447609879822406e01,
    1.615858368580409e02,
    -1.556989798598866e02,
    6.680131188771972e01,
    -1.328068155288572e01,
)
_ACKLAM_C = (
    -7.784894002430293e-03,
    -3.223964580411365e-01,
    -2.400758277161838e00,
    -2.549732539343734e00,
    4.374664141464968e00,
    2.938163982698783e00,
)
_ACKLAM_D = (
    7.784695709041462e-03,
    3.224671290700398e-01,
    2.445134137142996e00,
    3.754408661907416e00,
)
_ACKLAM_P_LOW = 0.02425
_ACKLAM_P_HIGH = 1.0 - _ACKLAM_P_LOW


def _inverse_normal_cdf(p: float) -> float:
    """标准正态逆 CDF Φ⁻¹(p), Acklam 逼近 + 一步 Newton 精化。

    Args:
        p: 概率, 必须落在 (0, 1) 开区间。

    Returns:
        x 使 Φ(x)=p, 精度约 1e-15。

    Raises:
        OverfittingAdjudicationError: p 不在 (0, 1)。
    """
    if not (0.0 < p < 1.0):
        raise OverfittingAdjudicationError(f"Φ⁻¹ 定义域为 (0,1): p={p}")

    if p < _ACKLAM_P_LOW:
        q = math.sqrt(-2.0 * math.log(p))
        x = (
            ((((_ACKLAM_C[0] * q + _ACKLAM_C[1]) * q + _ACKLAM_C[2]) * q + _ACKLAM_C[3]) * q + _ACKLAM_C[4]) * q
            + _ACKLAM_C[5]
        ) / ((((_ACKLAM_D[0] * q + _ACKLAM_D[1]) * q + _ACKLAM_D[2]) * q + _ACKLAM_D[3]) * q + 1.0)
    elif p <= _ACKLAM_P_HIGH:
        q = p - 0.5
        r = q * q
        x = (
            (
                ((((_ACKLAM_A[0] * r + _ACKLAM_A[1]) * r + _ACKLAM_A[2]) * r + _ACKLAM_A[3]) * r + _ACKLAM_A[4]) * r
                + _ACKLAM_A[5]
            )
            * q
            / (
                ((((_ACKLAM_B[0] * r + _ACKLAM_B[1]) * r + _ACKLAM_B[2]) * r + _ACKLAM_B[3]) * r + _ACKLAM_B[4]) * r
                + 1.0
            )
        )
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        x = -(
            ((((_ACKLAM_C[0] * q + _ACKLAM_C[1]) * q + _ACKLAM_C[2]) * q + _ACKLAM_C[3]) * q + _ACKLAM_C[4]) * q
            + _ACKLAM_C[5]
        ) / ((((_ACKLAM_D[0] * q + _ACKLAM_D[1]) * q + _ACKLAM_D[2]) * q + _ACKLAM_D[3]) * q + 1.0)

    # 一步 Newton 精化: x -= (Φ(x)-p)/φ(x)
    err = _normal_cdf(x) - p
    pdf = math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)
    if pdf > 0.0:
        x -= err / pdf
    return x


# ---------------------------------------------------------------------------
# 检验器② DSR (Deflated Sharpe Ratio)
# ---------------------------------------------------------------------------


def expected_max_sharpe_z(num_trials: int) -> float:
    """多重试验期望最大值 E[max(Z_N)](Bailey & López de Prado 2014 闭式)。

    N=1: 0(无多重试验膨胀)
    N>1: E[max(Z_N)]≈(1−γ)Φ⁻¹(1−1/N)+γΦ⁻¹(1−1/(N·e)), γ=Euler–Mascheroni 常数

    Args:
        num_trials: 试验次数 N(回测尝试的策略/参数组合数)

    Returns:
        E[max(Z_N)], 随 N 单调不减。

    Raises:
        OverfittingAdjudicationError: num_trials < 1。
    """
    if num_trials < 1:
        raise OverfittingAdjudicationError(f"num_trials 必须 >= 1: {num_trials}")
    if num_trials == 1:
        return 0.0
    n = float(num_trials)
    return (1.0 - EULER_MASCHERONI) * _inverse_normal_cdf(1.0 - 1.0 / n) + EULER_MASCHERONI * _inverse_normal_cdf(
        1.0 - 1.0 / (n * math.e)
    )


@dataclass(frozen=True)
class DSRVerdict:
    """DSR 裁定结果——不可变。

    Attributes:
        sharpe: 观测 Sharpe(输入原值, 年化口径由调用方自定)
        num_trials: 试验次数 N
        num_obs: 样本量 T
        skewness: 收益率偏度(正态=0)
        kurtosis: 收益率超额峰度(正态=0, 内部转 Pearson=excess+3 参与 V[SR])
        var_sr: Sharpe 估计量方差 V[SR]=(1−γ3·SR+(γ4−1)/4·SR²)/(T−1)
        expected_max_sharpe: 多重试验期望虚高 E[max SR]=√V[SR]·E[max(Z_N)]
        dsr: Deflated Sharpe Ratio ∈ [0,1]
        threshold: 显著性阈值(默认 0.95 SSoT)
        is_significant: dsr >= threshold
    """

    sharpe: float
    num_trials: int
    num_obs: int
    skewness: float
    kurtosis: float
    var_sr: float
    expected_max_sharpe: float
    dsr: float
    threshold: float
    is_significant: bool


def adjudicate_dsr(
    sharpe: float,
    num_trials: int,
    num_obs: int,
    skewness: float = 0.0,
    kurtosis: float = 0.0,
    threshold: float = DSR_SIGNIFICANCE_THRESHOLD,
) -> DSRVerdict:
    """DSR 裁定: 多次试验后真实 Sharpe 折减(Bailey & López de Prado 2014)。

    DSR = Φ((SR − E[max SR]) / √V[SR]), 语义=P(真实 Sharpe > 0 | 修正试验膨胀)。

    Args:
        sharpe: 观测 Sharpe(多次试验取最好的那个)
        num_trials: 试验次数 N
        num_obs: 样本量 T(收益率观测数, >=2)
        skewness: 收益率偏度(正态=0)
        kurtosis: 收益率超额峰度(正态=0)
        threshold: 显著性阈值(默认 DSR_SIGNIFICANCE_THRESHOLD=0.95)

    Returns:
        DSRVerdict; is_significant = dsr >= threshold。

    Raises:
        OverfittingAdjudicationError: 输入非有限 / num_trials<1 / num_obs<2 / 阈值越界。
    """
    vals = (float(sharpe), float(skewness), float(kurtosis))
    if not all(math.isfinite(v) for v in vals):
        raise OverfittingAdjudicationError("sharpe/skewness/kurtosis 含 NaN/Inf")
    if num_trials < 1:
        raise OverfittingAdjudicationError(f"num_trials 必须 >= 1: {num_trials}")
    if num_obs < 2:
        raise OverfittingAdjudicationError(f"num_obs 必须 >= 2(需 T−1>0): {num_obs}")
    if not (0.0 < threshold < 1.0):
        raise OverfittingAdjudicationError(f"threshold 必须在 (0,1): {threshold}")

    sr = float(sharpe)
    skew = float(skewness)
    kurt_pearson = float(kurtosis) + 3.0  # 超额峰度 -> Pearson 峰度(正态=3)

    var_term = 1.0 - skew * sr + (kurt_pearson - 1.0) / 4.0 * sr * sr
    var_sr = var_term / (num_obs - 1)

    if var_sr <= 0.0:
        # 方差退化(极端矩输入): DSR 退化为阶跃判定
        dsr = 1.0 if sr > 0.0 else 0.0
        expected_max = 0.0
    else:
        sigma_sr = math.sqrt(var_sr)
        expected_max = sigma_sr * expected_max_sharpe_z(num_trials)
        dsr = _normal_cdf((sr - expected_max) / sigma_sr)

    verdict = DSRVerdict(
        sharpe=sr,
        num_trials=int(num_trials),
        num_obs=int(num_obs),
        skewness=skew,
        kurtosis=float(kurtosis),
        var_sr=var_sr,
        expected_max_sharpe=expected_max,
        dsr=dsr,
        threshold=float(threshold),
        is_significant=bool(dsr >= threshold),
    )
    _logger.debug(
        "DSR裁定: SR=%.4f N=%d T=%d V[SR]=%.6f E[max]=%.4f DSR=%.4f significant=%s",
        sr,
        num_trials,
        num_obs,
        var_sr,
        expected_max,
        dsr,
        verdict.is_significant,
    )
    return verdict


# ---------------------------------------------------------------------------
# 检验器① walk-forward 汇总
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WalkForwardDecaySummary:
    """walk-forward OOS/IS 衰减比汇总——不可变。

    Attributes:
        n_folds: 输入折总数
        n_valid_folds: 有效折数(IS>0, 对齐 compare_in_out_sample 口径)
        ratios: 各有效折 OOS/IS 衰减比(按输入顺序)
        mean_ratio: 衰减比均值(无有效折=0.0)
        std_ratio: 衰减比样本标准差(ddof=1, 单折/无有效折=0.0)
        min_ratio: 最小衰减比(无有效折=0.0)
        worst_fold_index: 最差折在原始输入中的索引(无有效折=-1)
        threshold: 否决阈值(默认 0.70 SSoT, P0-9)
        n_below_threshold: 衰减比 < threshold 的折数
        is_stable: n_valid_folds>0 且 min_ratio >= threshold(无有效折 fail-closed=False)
    """

    n_folds: int
    n_valid_folds: int
    ratios: tuple[float, ...]
    mean_ratio: float
    std_ratio: float
    min_ratio: float
    worst_fold_index: int
    threshold: float
    n_below_threshold: int
    is_stable: bool


def summarize_walk_forward(
    folds: Sequence[tuple[float, float]],
    threshold: float = DEFAULT_OOS_SHARPE_THRESHOLD_RATIO,
) -> WalkForwardDecaySummary:
    """检验器①: 各折 OOS/IS 衰减比分布 + 最差折汇总。

    Args:
        folds: 各折 (is_sharpe, oos_sharpe) 对, 至少 1 折;
            IS<=0 折不适用 OOS/IS 比率, 剔除出分布但计入 n_folds
        threshold: 否决阈值(默认 DEFAULT_OOS_SHARPE_THRESHOLD_RATIO=0.70, P0-9)

    Returns:
        WalkForwardDecaySummary。

    Raises:
        OverfittingAdjudicationError: 空折序列 / 含非有限值 / 阈值越出 [0,1]。
    """
    if not folds:
        raise OverfittingAdjudicationError("folds 不能为空")
    if not (0.0 <= threshold <= 1.0):
        raise OverfittingAdjudicationError(f"threshold 必须在 [0,1]: {threshold}")

    pairs: list[tuple[float, float]] = []
    for i, pair in enumerate(folds):
        is_s, oos_s = float(pair[0]), float(pair[1])
        if not (math.isfinite(is_s) and math.isfinite(oos_s)):
            raise OverfittingAdjudicationError(f"第{i}折含 NaN/Inf: {pair}")
        pairs.append((is_s, oos_s))

    valid: list[tuple[int, float]] = [(i, oos / is_s) for i, (is_s, oos) in enumerate(pairs) if is_s > _EPS]
    ratios = tuple(r for _, r in valid)
    n_valid = len(valid)

    if n_valid == 0:
        return WalkForwardDecaySummary(
            n_folds=len(pairs),
            n_valid_folds=0,
            ratios=(),
            mean_ratio=0.0,
            std_ratio=0.0,
            min_ratio=0.0,
            worst_fold_index=-1,
            threshold=float(threshold),
            n_below_threshold=0,
            is_stable=False,  # fail-closed: 无有效折无法证明稳定
        )

    mean_ratio = sum(ratios) / n_valid
    if n_valid >= 2:
        std_ratio = math.sqrt(sum((r - mean_ratio) ** 2 for r in ratios) / (n_valid - 1))
    else:
        std_ratio = 0.0
    worst_idx, min_ratio = min(valid, key=lambda t: t[1])
    n_below = sum(1 for r in ratios if r < threshold)

    return WalkForwardDecaySummary(
        n_folds=len(pairs),
        n_valid_folds=n_valid,
        ratios=ratios,
        mean_ratio=mean_ratio,
        std_ratio=std_ratio,
        min_ratio=min_ratio,
        worst_fold_index=worst_idx,
        threshold=float(threshold),
        n_below_threshold=n_below,
        is_stable=bool(min_ratio >= threshold),
    )


# ---------------------------------------------------------------------------
# 检验器③ 参数扰动 ±20% 收益稳定性
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PerturbationPoint:
    """单扰动点——不可变。

    Attributes:
        param_name: 被扰动参数名
        direction: 扰动方向(+pct / −pct)
        perturbed_value: 扰动后参数值
        performance: 扰动后绩效(backtest_fn 返回)
        decay_rate: 绩效衰减率=(基准−扰动)/|基准|(正=衰减, 负=改善)
    """

    param_name: str
    direction: float
    perturbed_value: float
    performance: float
    decay_rate: float


@dataclass(frozen=True)
class PerturbationStabilityReport:
    """参数扰动稳定性报告——不可变。

    Attributes:
        base_performance: 基准参数绩效
        pct: 扰动幅度(默认 ±20%)
        n_points: 扰动点数(参数数 × 2 方向)
        max_decay: 最大衰减率
        mean_decay: 平均衰减率
        robust_share: 稳健区间占比(衰减率 <= tolerance 的扰动点占比)
        tolerance: 单点衰减容忍度(默认 PARAM_MAX_CHANGE_THRESHOLD=0.30 SSoT)
        min_robust_share: 稳健区间占比下限(默认 1.0=全部扰动点须稳健)
        is_stable: robust_share >= min_robust_share
        points: 全部扰动点明细
    """

    base_performance: float
    pct: float
    n_points: int
    max_decay: float
    mean_decay: float
    robust_share: float
    tolerance: float
    min_robust_share: float
    is_stable: bool
    points: tuple[PerturbationPoint, ...]


def perturbation_stability(
    base_params: Mapping[str, float],
    backtest_fn: Callable[[Mapping[str, float]], float],
    pct: float = DEFAULT_PERTURBATION_PCT,
    tolerance: float = PARAM_MAX_CHANGE_THRESHOLD,
    min_robust_share: float = 1.0,
) -> PerturbationStabilityReport:
    """检验器③: 策略参数 ±pct one-at-a-time 扰动, 统计绩效衰减率与稳健区间占比。

    回测引擎走契约接口: backtest_fn(params) -> 绩效标量(如 Sharpe), 注入式不硬绑引擎。

    Args:
        base_params: 基准参数(非空, 值须非零有限——零值无法施加比例扰动)
        backtest_fn: 回测契约 callable, 入参为参数字典, 返回绩效标量
        pct: 扰动幅度(默认 0.20=±20%)
        tolerance: 单点衰减容忍度(默认 0.30 SSoT)
        min_robust_share: 稳健区间占比下限(默认 1.0)

    Returns:
        PerturbationStabilityReport。

    Raises:
        OverfittingAdjudicationError: 参数空/零值/非有限 / pct 越出 (0,1] /
            tolerance<0 / min_robust_share 越出 (0,1] / 基准绩效≈0(衰减率无定义)。
    """
    if not base_params:
        raise OverfittingAdjudicationError("base_params 不能为空")
    if not (0.0 < pct <= 1.0):
        raise OverfittingAdjudicationError(f"pct 必须在 (0,1]: {pct}")
    if tolerance < 0.0:
        raise OverfittingAdjudicationError(f"tolerance 必须 >= 0: {tolerance}")
    if not (0.0 < min_robust_share <= 1.0):
        raise OverfittingAdjudicationError(f"min_robust_share 必须在 (0,1]: {min_robust_share}")
    for name, value in base_params.items():
        v = float(value)
        if not math.isfinite(v):
            raise OverfittingAdjudicationError(f"参数 {name} 非有限: {value}")
        if v == 0.0:
            raise OverfittingAdjudicationError(f"参数 {name}=0 无法施加比例扰动")

    base_params_f = {k: float(v) for k, v in base_params.items()}
    base_perf = float(backtest_fn(dict(base_params_f)))
    if not math.isfinite(base_perf):
        raise OverfittingAdjudicationError(f"基准绩效非有限: {base_perf}")
    if abs(base_perf) < _EPS:
        raise OverfittingAdjudicationError(f"基准绩效≈0, 衰减率无定义: {base_perf}")

    points: list[PerturbationPoint] = []
    for name, base_value in base_params_f.items():
        for direction in (pct, -pct):
            perturbed = dict(base_params_f)
            perturbed[name] = base_value * (1.0 + direction)
            perf = float(backtest_fn(perturbed))
            if not math.isfinite(perf):
                raise OverfittingAdjudicationError(f"扰动点 {name}{direction:+.0%} 绩效非有限: {perf}")
            decay = (base_perf - perf) / abs(base_perf)
            points.append(
                PerturbationPoint(
                    param_name=name,
                    direction=direction,
                    perturbed_value=perturbed[name],
                    performance=perf,
                    decay_rate=decay,
                )
            )

    decays = [p.decay_rate for p in points]
    max_decay = max(decays)
    mean_decay = sum(decays) / len(decays)
    robust_share = sum(1 for d in decays if d <= tolerance) / len(decays)
    is_stable = robust_share >= min_robust_share

    report = PerturbationStabilityReport(
        base_performance=base_perf,
        pct=float(pct),
        n_points=len(points),
        max_decay=max_decay,
        mean_decay=mean_decay,
        robust_share=robust_share,
        tolerance=float(tolerance),
        min_robust_share=float(min_robust_share),
        is_stable=bool(is_stable),
        points=tuple(points),
    )
    _logger.debug(
        "扰动裁定: %d点 pct=%.0%% max_decay=%.4f robust_share=%.2f stable=%s",
        report.n_points,
        pct,
        max_decay,
        robust_share,
        is_stable,
    )
    return report


# ---------------------------------------------------------------------------
# 上线门禁挂钩点(Protocol 预留) + 综合裁定
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OverfitAdjudicationReport:
    """P-5 综合裁定报告——不可变。

    Attributes:
        walk_forward: 检验器①汇总(未提供折数据=None)
        dsr: 检验器②判定(未提供 DSR 输入=None)
        perturbation: 检验器③报告(未提供扰动输入=None)
        is_overfitting: 任一已执行检验器失败=True
        reasons: 失败原因列表(全通过=空)
    """

    walk_forward: WalkForwardDecaySummary | None
    dsr: DSRVerdict | None
    perturbation: PerturbationStabilityReport | None
    is_overfitting: bool
    reasons: tuple[str, ...]


@runtime_checkable
class OverfitGateHook(Protocol):
    """上线门禁挂钩点 Protocol——预留接口, 默认不接真门禁。

    真门禁实现方(上线流水线)按本 Protocol 注入: 裁定完成后收到
    OverfitAdjudicationReport, 自行决定阻断/放行/人工审批。
    """

    def on_adjudication(self, report: OverfitAdjudicationReport) -> None:
        """裁定完成回调。"""
        ...


class OverfittingAdjudicator:
    """P-5 过拟合裁定器: 三检验器编排 + 门禁挂钩点回调。

    未提供的检验器视为未检测(不参与否决), 与 overfitting_detector.detect 口径一致。
    gate_hook=None(默认)时仅产出裁定报告, 不触达任何真门禁。
    """

    def adjudicate(
        self,
        *,
        walk_forward_folds: Sequence[tuple[float, float]] | None = None,
        dsr_kwargs: Mapping[str, object] | None = None,
        perturbation_kwargs: Mapping[str, object] | None = None,
        gate_hook: OverfitGateHook | None = None,
    ) -> OverfitAdjudicationReport:
        """执行已提供的检验器并汇总裁定。

        Args:
            walk_forward_folds: 检验器①输入, 各折 (is_sharpe, oos_sharpe) 对
            dsr_kwargs: 检验器②输入, adjudicate_dsr 的关键字参数
            perturbation_kwargs: 检验器③输入, perturbation_stability 的关键字参数
            gate_hook: 上线门禁挂钩点(Protocol), None=不接真门禁

        Returns:
            OverfitAdjudicationReport; is_overfitting=任一已执行检验器失败。
        """
        reasons: list[str] = []
        wf_summary: WalkForwardDecaySummary | None = None
        dsr_verdict: DSRVerdict | None = None
        pert_report: PerturbationStabilityReport | None = None

        if walk_forward_folds is not None:
            wf_summary = summarize_walk_forward(walk_forward_folds)
            if not wf_summary.is_stable:
                reasons.append(
                    f"walk-forward 衰减: {wf_summary.n_valid_folds}有效折中最差折"
                    f"(第{wf_summary.worst_fold_index}折)OOS/IS={wf_summary.min_ratio:.2%}"
                    f"低于阈值{wf_summary.threshold:.0%}"
                )

        if dsr_kwargs is not None:
            dsr_verdict = adjudicate_dsr(**dict(dsr_kwargs))  # type: ignore[arg-type]
            if not dsr_verdict.is_significant:
                reasons.append(
                    f"DSR={dsr_verdict.dsr:.4f}低于显著性阈值{dsr_verdict.threshold:.2f}"
                    f"(N={dsr_verdict.num_trials}次试验折减后无超出运气的证据)"
                )

        if perturbation_kwargs is not None:
            pert_report = perturbation_stability(**dict(perturbation_kwargs))  # type: ignore[arg-type]
            if not pert_report.is_stable:
                reasons.append(
                    f"参数扰动±{pert_report.pct:.0%}: 稳健区间占比{pert_report.robust_share:.2%}"
                    f"低于要求{pert_report.min_robust_share:.0%}(最大衰减{pert_report.max_decay:.2%})"
                )

        report = OverfitAdjudicationReport(
            walk_forward=wf_summary,
            dsr=dsr_verdict,
            perturbation=pert_report,
            is_overfitting=bool(reasons),
            reasons=tuple(reasons),
        )
        _logger.info("P-5 裁定完成: is_overfitting=%s reasons=%d", report.is_overfitting, len(reasons))

        if gate_hook is not None:
            gate_hook.on_adjudication(report)
        return report


__all__ = [
    "DEFAULT_PERTURBATION_PCT",
    "DSRVerdict",
    "EULER_MASCHERONI",
    "OverfitAdjudicationReport",
    "OverfitGateHook",
    "OverfittingAdjudicationError",
    "OverfittingAdjudicator",
    "PerturbationPoint",
    "PerturbationStabilityReport",
    "WalkForwardDecaySummary",
    "adjudicate_dsr",
    "expected_max_sharpe_z",
    "perturbation_stability",
    "summarize_walk_forward",
]
