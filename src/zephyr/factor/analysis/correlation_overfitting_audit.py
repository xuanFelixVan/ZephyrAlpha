# [BLUEPRINT] 23_strategy_correlation_validation.md §3.1⑤第6部分/§3.3 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/
# [MODULE] zephyr.factor.analysis.correlation_overfitting_audit
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] numpy(仅slope); DSR由调用方经 zephyr.simulation.deflated_sharpe_calculator 预算后传入(解耦跨域依赖)
# [CONSUMERS] G07 策略相关性验证报告（过拟合检测矩阵）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数无IO; 任一硬指标fail即LIKELY_OVERFIT(保守); 外部deflated-alpha vendor不引入
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] n_params<1/样本对长度不一致->ValueError; avg_sharpe<=0->PSI=inf判fail
# [TESTS] tests/factor/test_correlation_overfitting_audit.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: IS/OOS Sharpe + N_obs/N_params + 可选 dsr/pbo/win_rate/profit_factor/trial级IS-OOS序列
# F1: PDR=(IS−OOS)/IS(<0.5通过); PSI_param=Best/Avg(<3.0通过, 与§5.4 PSI同名异义); DFR=N_obs/N_params(>=30通过)
# F2: OOS退化斜率(IS→OOS Sharpe回归斜率>0通过) + 胜率>70%/PF>3.0警戒线(软警告)
# A1: compute_pdr / compute_parameter_stability_index / compute_degrees_of_freedom_ratio(三指标自实现核心)
# A2: compute_oos_degradation_slope(最小二乘斜率) / check_extreme_backtest_metrics(警戒线)
# A3: audit(函数级入口: 汇总硬指标+可选dsr/pbo→LIKELY_REAL/INCONCLUSIVE/LIKELY_OVERFIT)
# O1: OverfitAuditResult(各指标值+per-check状态+三态verdict)
# [/ALGO_FLOW]
"""
D_FACTOR — G07 过拟合检测引擎（23 号 memo §3.3，PDR/PSI/DFR 自实现核心）

三指标补 DSR/PBO 盲区（digitalninjasystems 2026-05 / backtrex 2026-05）：
  - PDR=(IS_SR−OOS_SR)/IS_SR，≥0.5 严重过拟合
  - PSI=Best_SR/Avg_SR，≥3.0 过拟合（**Parameter Stability Index**，与 §5.4
    Population Stability Index 同名异义）
  - DFR=N_obs/N_params，<30 参数过多（机构共识 ≥30 trades/parameter）

外部 deflated-alpha v0.3.0 vendor 不引入（夜班裁定）；audit() 为函数级集成入口：
DSR 由调用方经 DeflatedSharpeCalculator（MOD-SIM-024 已 production）预算后传入，
PBO/CSCV 同理留口； verdict 保守策略"任一 fail 即不上线"（memo §5.3）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: is_sharpe 参数
#   fields: 参数 is_sharpe，类型注解 float
#   code: correlation_overfitting_audit.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: oos_sharpe 参数
#   fields: 参数 oos_sharpe，类型注解 float
#   code: correlation_overfitting_audit.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: best_sharpe 参数
#   fields: 参数 best_sharpe，类型注解 float
#   code: correlation_overfitting_audit.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: avg_sharpe 参数
#   fields: 参数 avg_sharpe，类型注解 float
#   code: correlation_overfitting_audit.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① compute_pdr
#   name_en: compute_pdr
#   intro: PDR 性能退化比 = (IS_SR − OOS_SR)/IS_SR。
#   desc: PDR 性能退化比 = (IS_SR − OOS_SR)/IS_SR。 IS_SR≤0（无 IS edge）约定返回 1.0（全额退化，判 fail）。负 OOS 使 PDR>1。；源码 L189-L196
#   inputs: is_sharpe oos_sharpe
#   outputs: float
# - id: A2
#   name_zh: ② compute_parameter_stability_index
#   name_en: compute_parameter_stability_index
#   intro: PSI 参数稳定指数 = Best_SR/Avg_SR（与 §5.4 PSI 同名异义）。
#   desc: PSI 参数稳定指数 = Best_SR/Avg_SR（与 §5.4 PSI 同名异义）。 avg_sharpe≤0（试探均值无 edge）→ inf（判 fail）。；源码 L199-L206
#   inputs: best_sharpe avg_sharpe
#   outputs: float
# - id: A3
#   name_zh: ③ compute_degrees_of_freedom_ratio
#   name_en: compute_degrees_of_freedom_ratio
#   intro: DFR 自由度比 = N_obs/N_params（≥30 通过）。
#   desc: DFR 自由度比 = N_obs/N_params（≥30 通过）。 Raises: ValueError: n_params<1 或 n_obs<1；源码 L209-L219
#   inputs: n_obs n_params
#   outputs: float
# - id: A4
#   name_zh: ④ compute_oos_degradation_slope
#   name_en: compute_oos_degradation_slope
#   intro: OOS 退化斜率：OOS_SR 对 IS_SR 的最小二乘回归斜率（>0 通过）。
#   desc: OOS 退化斜率：OOS_SR 对 IS_SR 的最小二乘回归斜率（>0 通过）。 注意机械陷阱（deflated-alpha README Limitations）：IS/OO…；源码 L222-L240
#   inputs: is_sharpes oos_sharpes
#   outputs: float
# - id: A5
#   name_zh: ⑤ check_extreme_backtest_metrics
#   name_en: check_extreme_backtest_metrics
#   intro: 胜率/PF 警戒线（软警告）：胜率>70% 或 PF>3.0 需极端怀疑。
#   desc: 胜率/PF 警戒线（软警告）：胜率>70% 或 PF>3.0 需极端怀疑。；源码 L243-L250
#   inputs: win_rate profit_factor
#   outputs: list[str]
# - id: A6
#   name_zh: ⑥ audit
#   name_en: audit
#   intro: 过拟合审计函数级入口：PDR/PSI/DFR 三核心 + 可选 DSR/PBO/退化斜率。
#   desc: 过拟合审计函数级入口：PDR/PSI/DFR 三核心 + 可选 DSR/PBO/退化斜率。 verdict 规则（memo §5.3 保守策略"任一 fail 即不上线"）： -…；源码 L253-L313
#   inputs: is_sharpe oos_sharpe n_obs n_params best_sharpe avg_sharpe dsr pbo
#   outputs: OverfitAuditResult
#   （注：A6 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: G07 策略相关性验证报告（过拟合检测矩阵）
# - id: O2
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: G07 策略相关性验证报告（过拟合检测矩阵）
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

from dataclasses import dataclass, field
from enum import Enum

import numpy as np

__all__ = [
    "DFR_MIN",
    "DSR_MIN",
    "PBO_MAX",
    "PDR_MAX",
    "PSI_PARAM_MAX",
    "OverfitAuditResult",
    "OverfitVerdict",
    "audit",
    "check_extreme_backtest_metrics",
    "compute_degrees_of_freedom_ratio",
    "compute_oos_degradation_slope",
    "compute_parameter_stability_index",
    "compute_pdr",
]

#: PDR 阈值：≥0.5 严重过拟合（digitalninjasystems 2026-05）
PDR_MAX = 0.5
#: 参数稳定指数阈值：≥3.0 过拟合
PSI_PARAM_MAX = 3.0
#: 自由度比阈值：<30 参数过多（backtrex 2026-05 机构共识）
DFR_MIN = 30.0
#: DSR 显著性阈值（Bailey-López de Prado 2014，MOD-SIM-024 同口径）
DSR_MIN = 0.95
#: PBO 通过阈值（<0.05 通过；null=0.5 非 0，pbo-search.marketmaker.cc 2026-07）
PBO_MAX = 0.05
#: 胜率/PF 警戒线（>70% 胜率或 PF>3.0 需极端怀疑，软警告非硬 fail）
WIN_RATE_WARN = 0.70
PROFIT_FACTOR_WARN = 3.0


class OverfitVerdict(str, Enum):
    """过拟合三态判定（deflated-alpha 三态口径）。"""

    LIKELY_REAL = "LIKELY_REAL"
    INCONCLUSIVE = "INCONCLUSIVE"
    LIKELY_OVERFIT = "LIKELY_OVERFIT"


@dataclass(frozen=True)
class OverfitAuditResult:
    """过拟合审计结果（不可变）。

    Attributes:
        verdict: 三态判定（任一硬指标 fail→LIKELY_OVERFIT；软警告→INCONCLUSIVE）
        metrics: 指标名 → 数值（pdr/psi_param/dfr/slope/dsr/pbo...）
        checks: 硬指标名 → 是否通过
        warnings: 软警告列表（胜率/PF 警戒线等）
    """

    verdict: OverfitVerdict
    metrics: dict[str, float]
    checks: dict[str, bool]
    warnings: list[str] = field(default_factory=list)


def compute_pdr(is_sharpe: float, oos_sharpe: float) -> float:
    """PDR 性能退化比 = (IS_SR − OOS_SR)/IS_SR。

    IS_SR≤0（无 IS edge）约定返回 1.0（全额退化，判 fail）。负 OOS 使 PDR>1。
    """
    if is_sharpe <= 0.0:
        return 1.0
    return (is_sharpe - oos_sharpe) / is_sharpe


def compute_parameter_stability_index(best_sharpe: float, avg_sharpe: float) -> float:
    """PSI 参数稳定指数 = Best_SR/Avg_SR（与 §5.4 PSI 同名异义）。

    avg_sharpe≤0（试探均值无 edge）→ inf（判 fail）。
    """
    if avg_sharpe <= 0.0:
        return float("inf")
    return best_sharpe / avg_sharpe


def compute_degrees_of_freedom_ratio(n_obs: int, n_params: int) -> float:
    """DFR 自由度比 = N_obs/N_params（≥30 通过）。

    Raises:
        ValueError: n_params<1 或 n_obs<1
    """
    if n_params < 1:
        raise ValueError(f"n_params 必须 >=1, got {n_params}")
    if n_obs < 1:
        raise ValueError(f"n_obs 必须 >=1, got {n_obs}")
    return n_obs / n_params


def compute_oos_degradation_slope(is_sharpes: list[float] | np.ndarray, oos_sharpes: list[float] | np.ndarray) -> float:
    """OOS 退化斜率：OOS_SR 对 IS_SR 的最小二乘回归斜率（>0 通过）。

    注意机械陷阱（deflated-alpha README Limitations）：IS/OOS halves 互补时常胜
    策略即使有真 edge 也显示反相关 halves——斜率应基于多组独立 IS/OOS 划分。

    Raises:
        ValueError: 长度不一致或 <2 个点
    """
    x = np.asarray(is_sharpes, dtype=float)
    y = np.asarray(oos_sharpes, dtype=float)
    if x.shape != y.shape:
        raise ValueError("is_sharpes 与 oos_sharpes 长度不一致")
    if len(x) < 2:
        raise ValueError(f"回归至少需要 2 个点, got {len(x)}")
    var_x = float(((x - x.mean()) ** 2).sum())
    if var_x == 0.0:
        return 0.0  # IS 无变异 → 斜率无定义，保守记 0（不通过 >0 判据）
    return float(((x - x.mean()) * (y - y.mean())).sum() / var_x)


def check_extreme_backtest_metrics(win_rate: float | None = None, profit_factor: float | None = None) -> list[str]:
    """胜率/PF 警戒线（软警告）：胜率>70% 或 PF>3.0 需极端怀疑。"""
    warnings: list[str] = []
    if win_rate is not None and win_rate > WIN_RATE_WARN:
        warnings.append(f"win_rate={win_rate:.2%} > 70% 警戒线")
    if profit_factor is not None and profit_factor > PROFIT_FACTOR_WARN:
        warnings.append(f"profit_factor={profit_factor:.2f} > 3.0 警戒线")
    return warnings


def audit(
    is_sharpe: float,
    oos_sharpe: float,
    n_obs: int,
    n_params: int,
    best_sharpe: float,
    avg_sharpe: float,
    *,
    dsr: float | None = None,
    pbo: float | None = None,
    trial_is_sharpes: list[float] | None = None,
    trial_oos_sharpes: list[float] | None = None,
    win_rate: float | None = None,
    profit_factor: float | None = None,
) -> OverfitAuditResult:
    """过拟合审计函数级入口：PDR/PSI/DFR 三核心 + 可选 DSR/PBO/退化斜率。

    verdict 规则（memo §5.3 保守策略"任一 fail 即不上线"）：
      - 任一硬指标 fail → LIKELY_OVERFIT
      - 硬指标全过但有软警告（胜率/PF 警戒线）→ INCONCLUSIVE
      - 硬指标全过且无软警告 → LIKELY_REAL

    Args:
        is_sharpe/oos_sharpe: 最优参数的 IS/OOS Sharpe
        n_obs/n_params: 样本量 / 参数个数（DFR）
        best_sharpe/avg_sharpe: N 次试探的最优/平均 Sharpe（参数稳定指数）
        dsr: 预计算 DSR（调用方经 DeflatedSharpeCalculator，≥0.95 通过）
        pbo: 预计算 PBO/CSCV（<0.05 通过，null=0.5）
        trial_is_sharpes/trial_oos_sharpes: 多组划分的 IS/OOS 序列（退化斜率）
        win_rate/profit_factor: 警戒线软警告

    Returns:
        OverfitAuditResult
    """
    metrics: dict[str, float] = {}
    checks: dict[str, bool] = {}

    metrics["pdr"] = compute_pdr(is_sharpe, oos_sharpe)
    checks["pdr"] = metrics["pdr"] < PDR_MAX
    metrics["psi_param"] = compute_parameter_stability_index(best_sharpe, avg_sharpe)
    checks["psi_param"] = metrics["psi_param"] < PSI_PARAM_MAX
    metrics["dfr"] = compute_degrees_of_freedom_ratio(n_obs, n_params)
    checks["dfr"] = metrics["dfr"] >= DFR_MIN
    if dsr is not None:
        metrics["dsr"] = dsr
        checks["dsr"] = dsr >= DSR_MIN
    if pbo is not None:
        metrics["pbo"] = pbo
        checks["pbo"] = pbo < PBO_MAX
    if trial_is_sharpes is not None and trial_oos_sharpes is not None:
        metrics["oos_degradation_slope"] = compute_oos_degradation_slope(trial_is_sharpes, trial_oos_sharpes)
        checks["oos_degradation_slope"] = metrics["oos_degradation_slope"] > 0.0

    warnings = check_extreme_backtest_metrics(win_rate, profit_factor)
    if not all(checks.values()):
        verdict = OverfitVerdict.LIKELY_OVERFIT
    elif warnings:
        verdict = OverfitVerdict.INCONCLUSIVE
    else:
        verdict = OverfitVerdict.LIKELY_REAL
    return OverfitAuditResult(verdict, metrics, checks, warnings)
