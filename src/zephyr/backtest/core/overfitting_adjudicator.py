# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.overfitting_adjudicator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.overfitting_detector; zephyr.simulation.deflated_sharpe_calculator
# [CONSUMERS] 上线评审流程(挂钩点预留, 未接真门禁)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三检验器纯统计; OOS/IS阈值0.70与扰动容忍0.30复用overfitting_detector SSoT; DSR显著线0.95复用MOD-SIM-024 SSoT; DSR数学(V[SR]峰度口径/E[max]/退化判定)全委托MOD-SIM-024禁另写公式; 退化态fail-closed(degenerate=True⇒dsr=0.0且永不判显著); backtest引擎走注入callable契约; 报告frozen不可变; 无有效折fail-closed
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
  - 检验器② Deflated Sharpe Ratio: 数学全量委托官方件 MOD-SIM-024
    (zephyr.simulation.deflated_sharpe_calculator)——V[SR] 峰度口径(超额→Pearson +3)、
    E[max(Z_N)] 闭式 (1−γ)Φ⁻¹(1−1/N)+γΦ⁻¹(1−1/(N·e)) 与退化态 fail-closed 判定
    皆同一真源, 本件只做"输入矩→裁定卡"封装;
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
  - DSR 数学不另立真源: Φ/Φ⁻¹、V[SR]、E[max(Z_N)]、退化判定一律取自 MOD-SIM-024
    (原自建 Acklam 有理逼近块已随 SDC-3/SDC-4 口径统一删除, 免同族三处互斥)

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7
# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/overfitting_adjudicator.yaml
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
from zephyr.simulation.deflated_sharpe_calculator import (
    DSR_SIGNIFICANCE_THRESHOLD,
    EULER_MASCHERONI,
    deflated_sharpe_from_moments,
)
from zephyr.simulation.deflated_sharpe_calculator import (
    expected_max_sharpe_z as _canonical_expected_max_z,
)

_logger = logging.getLogger(__name__)

_EPS = 1e-12

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
# 检验器② DSR (Deflated Sharpe Ratio)
# ---------------------------------------------------------------------------
# 数学真源不在本件：Φ/Φ⁻¹、V[SR]、E[max(Z_N)]、退化判定一律取自
# MOD-SIM-024(zephyr.simulation.deflated_sharpe_calculator)，本件只做
# "输入矩 → 裁定卡"的封装。同族三处实现口径必须一致(SDC-3/SDC-4 施工 2026-09-17)，
# 故此处只准委托、不准另写公式；原自建的 _normal_cdf/Φ⁻¹ Acklam 逼近块已删。


def expected_max_sharpe_z(num_trials: int) -> float:
    """多重试验期望最大值 E[max(Z_N)]——委托官方件 MOD-SIM-024（SSoT，禁重写数学）。

    N=1: 0(无多重试验膨胀)
    N>1: (1−γ)Φ⁻¹(1−1/N)+γΦ⁻¹(1−1/(N·e)), γ=Euler–Mascheroni 常数

    Args:
        num_trials: 试验次数 N(回测尝试的策略/参数组合数)

    Returns:
        E[max(Z_N)], 随 N 单调不减。

    Raises:
        OverfittingAdjudicationError: num_trials < 1(本件输入契约，官方件口径为 N≤1→0)。
    """
    if num_trials < 1:
        raise OverfittingAdjudicationError(f"num_trials 必须 >= 1: {num_trials}")
    return _canonical_expected_max_z(num_trials)


@dataclass(frozen=True)
class DSRVerdict:
    """DSR 裁定结果——不可变。

    Attributes:
        sharpe: 观测 Sharpe(输入原值, 年化口径由调用方自定)
        num_trials: 试验次数 N
        num_obs: 样本量 T
        skewness: 收益率偏度(正态=0)
        kurtosis: 收益率**超额**峰度(正态=0; V[SR] 内转 Pearson=excess+3, 转换真源 MOD-SIM-024)
        var_sr: Sharpe 估计量方差 V[SR]=(1−γ3·SR+(κ_p−1)/4·SR²)/(T−1), κ_p 为 Pearson 峰度
        expected_max_sharpe: 多重试验期望虚高 E[max SR]=√V[SR]·E[max(Z_N)](Sharpe 量纲;
            官方件 DSRResult.expected_max 是同一 E[max(Z_N)] 的无量纲 z 形式, 两者差一个 σ_SR)
        dsr: Deflated Sharpe Ratio ∈ [0,1]; degenerate=True 时恒为 DSR_UNDECIDABLE(=0.0)
        threshold: 显著性阈值(默认 0.95 SSoT)
        is_significant: dsr >= threshold 且非退化(退化态永不判显著)
        degenerate: True=V[SR] 估计失效(矩输入互斥等) ⇒ "不可判定"而非"测得不显著"(SDC-4)
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
    degenerate: bool = False


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
        DSRVerdict; is_significant = dsr >= threshold 且非退化。
        退化态（V[SR] 非正/NaN=矩输入互斥、估计失效）下 degenerate=True、
        dsr=DSR_UNDECIDABLE(=0.0)、is_significant=False，并由官方件出声 WARNING
        ——绝不用占位值把"没有信息"伪装成"极显著"(SDC-4)。

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

    # 数学全部委托 MOD-SIM-024（V[SR] 峰度口径 + E[max(Z_N)] + 退化判定同一真源）
    var_sr, dsr, emax_z, degenerate = deflated_sharpe_from_moments(
        sr,
        int(num_trials),
        int(num_obs),
        skewness=skew,
        excess_kurtosis=float(kurtosis),
    )
    expected_max = 0.0 if degenerate else math.sqrt(var_sr) * emax_z

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
        is_significant=bool(not degenerate and dsr >= threshold),
        degenerate=degenerate,
    )
    _logger.debug(
        "DSR裁定: SR=%.4f N=%d T=%d V[SR]=%.6f E[max]=%.4f DSR=%.4f significant=%s degenerate=%s",
        sr,
        num_trials,
        num_obs,
        var_sr,
        expected_max,
        dsr,
        verdict.is_significant,
        degenerate,
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
                if dsr_verdict.degenerate:
                    # 退化态≠"测得不显著"：如实上报为不可判定，仍按 fail-closed 计入否决理由
                    reasons.append(
                        f"DSR 不可判定(V[SR]={dsr_verdict.var_sr:.6g} 退化:"
                        f"矩输入互斥/样本不足=估计失效, N={dsr_verdict.num_trials} T={dsr_verdict.num_obs})"
                        "→ Fail-Closed 不放行(非'已证明不显著')"
                    )
                else:
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
