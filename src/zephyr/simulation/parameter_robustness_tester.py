# [BLUEPRINT] MOD-SIM-021 | docs/03_modules/_domain_simulation/parameter_robustness_tester/blueprint.md
# [MODULE] zephyr.simulation.parameter_robustness_tester
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.simulation.strategy_simulator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 所有dataclass frozen不可变; stability_ratio∈[0,1]; 无稳定区间时stable_region=None; 纯math无第三方依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SimulationError(ZA-SIM-0021)
# [TESTS] tests/simulation/test_parameter_robustness_tester.py
# [A_module] module_id=MOD-SIM-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_SIMULATION — Parameter Robustness Tester (参数鲁棒性测试器)

寻找参数**稳定区间**而非最优值, 输出敏感性曲线 + 扰动测试 + 稳定区间标注 +
过拟合风险评估。核心思想: 鲁棒参数在较宽范围内表现稳定, 过拟合参数仅在最优点
附近表现好(窄峰=高风险)。

属 A 类基础设施(确定性计算), 纯基础层不涉及策略。

设计真源: depgraph MOD-SIM-021
蓝图: docs/03_modules/_domain_simulation/parameter_robustness_tester/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 目标函数 objective_func
#   fields: 接受参数值返回目标值(如Sharpe，越大越好)的回调
#   code: test_parameter(objective_func) L216
# - id: I2
#   name: 参数测试配置
#   fields: 参数名param_name + 待测参数值序列param_values(≥2个) + 基准值baseline/baseline_value
#   code: test_parameter(param_name, param_values, baseline) L217
# - id: I3
#   name: 鲁棒性配置 RobustnessConfig
#   fields: 稳定阈值比0.9 + 低风险≥0.5/高风险<0.2 + 默认扰动±5%/±10% + 扰动稳定阈值0.1
#   code: RobustnessConfig L57
# 层: 算法
# - id: A1
#   name_zh: ① 敏感性曲线扫描
#   name_en: test_parameter
#   intro: 逐参数值跑目标函数，得到敏感性曲线和最优点
#   desc: 各param_value调objective_func → ParameterPoint序列 → 最优点(argmax) + 总范围(max-min) + 目标值std(ddof=1)
#   inputs: I1 I2
#   outputs: 敏感性曲线points + 最优点 + total_range
# - id: A2
#   name_zh: ② 稳定区间检测
#   name_en: _find_stable_region
#   intro: 找目标值≥基准90%的最长连续参数区间（宽峰=鲁棒）
#   desc: 按参数值排序 → 标记objective≥baseline×0.9 → 最长连续True run为稳定区间 → stability_ratio=width/total_range钳到[0,1]；无稳定点→None
#   inputs: A1 I3
#   outputs: StableRegion + stability_ratio
#   invariant: stability_ratio∈[0,1]；无稳定区间时stable_region=None
# - id: A3
#   name_zh: ③ 过拟合风险分级
#   name_en: _classify_risk
#   intro: 稳定性比率越高风险越低，窄峰=过拟合高风险
#   desc: ratio≥0.5→LOW；ratio<0.2→HIGH；其余→MEDIUM
#   inputs: A2 I3
#   outputs: OverfitRisk等级
# - id: A4
#   name_zh: ④ 扰动测试
#   name_en: perturb_parameter
#   intro: 对基准参数施加±5%/±10%扰动，量目标值最大退化幅度
#   desc: 基准值×(1+ratio)逐扰动跑目标函数 → max_degradation=max|base-obj|/|base| → <0.1判稳定；baseline=0拒绝
#   inputs: I1 I2 I3
#   outputs: PerturbationResult
# - id: A5
#   name_zh: ⑤ 多参数汇总评估
#   name_en: assess
#   intro: 多参数稳定性取平均、总体风险取最差，定整体是否鲁棒
#   desc: overall_stability=mean(stability_ratio) → overall_risk=按LOW<MEDIUM<HIGH取最高 → is_robust=(总体风险≠HIGH)
#   inputs: A1
#   outputs: RobustnessReport
# - id: A6
#   name_zh: ⑥ 审计摘要生成
#   name_en: audit_summary
#   intro: 输出PASS/FAIL结论+各参数稳定区间明细的审计文本
#   desc: 结论行 + 总体稳定性/风险 + 逐参数ratio/risk/optimal/稳定区间
#   inputs: A5
#   outputs: 审计摘要字符串
# 层: 输出
# - id: O1
#   name_zh: 参数敏感性结果 ParameterSensitivity
#   name_en: ParameterSensitivity
#   intro: 单参数敏感性曲线+最优点+稳定区间+稳定性比率+过拟合风险
#   invariant: frozen不可变；stability_ratio∈[0,1]
#   downstream: zephyr.simulation.strategy_simulator（[CONSUMERS]）
# - id: O2
#   name_zh: 扰动测试结果 PerturbationResult
#   name_en: PerturbationResult
#   intro: 基准值+各扰动目标值+最大退化比例+是否稳定
#   downstream: zephyr.simulation.strategy_simulator（[CONSUMERS]）
# - id: O3
#   name_zh: 鲁棒性汇总报告与审计摘要
#   name_en: RobustnessReport / audit summary
#   intro: 多参数总体稳定性+总体过拟合风险+是否鲁棒，附人类可读审计摘要
#   downstream: zephyr.simulation.strategy_simulator（[CONSUMERS]）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# I3 --> A2
# A2 --> A3
# I3 --> A3
# I1 --> A4
# I2 --> A4
# I3 --> A4
# A1 --> A5
# A5 --> A6
# A1 --> O1
# A3 --> O1
# A4 --> O2
# A5 --> O3
# A6 --> O3
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class SimulationError(ZephyrBaseError):
    """仿真测试异常——输入非法。"""

    error_code = "ZA-SIM-0021"


class OverfitRisk(str, Enum):
    """过拟合风险等级。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class RobustnessConfig:
    """鲁棒性测试配置——不可变。

    Attributes:
        stable_threshold_ratio: 稳定判定阈值(目标值>=baseline*ratio视为稳定)。
        low_risk_min_ratio: stability_ratio>=此值 → LOW 风险。
        high_risk_max_ratio: stability_ratio<此值 → HIGH 风险。
        default_perturbations: 默认扰动比例(相对基准值)。
        perturbation_stable_threshold: 扰动稳定阈值(max_degradation<此值→稳定)。
    """

    stable_threshold_ratio: float = 0.9
    low_risk_min_ratio: float = 0.5
    high_risk_max_ratio: float = 0.2
    default_perturbations: tuple[float, ...] = (-0.1, -0.05, 0.05, 0.1)
    perturbation_stable_threshold: float = 0.1


@dataclass(frozen=True)
class ParameterPoint:
    """单参数测试点——不可变。

    Attributes:
        param_value: 参数值。
        objective: 目标值(如 Sharpe)。
    """

    param_value: float
    objective: float


@dataclass(frozen=True)
class StableRegion:
    """参数稳定区间——不可变。

    Attributes:
        low: 区间下界。
        high: 区间上界。
        width: 区间宽度(high - low)。
        point_count: 区间内测试点数。
    """

    low: float
    high: float
    width: float
    point_count: int


@dataclass(frozen=True)
class ParameterSensitivity:
    """单参数敏感性分析结果——不可变。

    Attributes:
        param_name: 参数名。
        points: 敏感性曲线(参数值→目标值)。
        optimal_value: 最优参数值。
        optimal_objective: 最优目标值。
        stable_region: 稳定区间(无则 None)。
        total_range: 参数总范围(max-min)。
        stability_ratio: 稳定性比率(stable_width/total_range)。
        objective_std: 目标值标准差(敏感性度量)。
        overfit_risk: 过拟合风险等级。
    """

    param_name: str
    points: list[ParameterPoint] = field(default_factory=list)
    optimal_value: float = 0.0
    optimal_objective: float = 0.0
    stable_region: StableRegion | None = None
    total_range: float = 0.0
    stability_ratio: float = 0.0
    objective_std: float = 0.0
    overfit_risk: OverfitRisk = OverfitRisk.HIGH


@dataclass(frozen=True)
class PerturbationResult:
    """扰动测试结果——不可变。

    Attributes:
        param_name: 参数名。
        baseline_value: 基准参数值。
        baseline_objective: 基准目标值。
        perturbations: 扰动比例列表。
        objectives: 各扰动下的目标值。
        max_degradation: 最大退化比例。
        is_stable: 是否稳定(max_degradation<阈值)。
    """

    param_name: str
    baseline_value: float
    baseline_objective: float
    perturbations: tuple[float, ...] = ()
    objectives: tuple[float, ...] = ()
    max_degradation: float = 0.0
    is_stable: bool = False


@dataclass(frozen=True)
class RobustnessReport:
    """多参数鲁棒性汇总报告——不可变。

    Attributes:
        sensitivities: 各参数敏感性结果。
        overall_stability: 总体稳定性(平均 stability_ratio)。
        overall_overfit_risk: 总体过拟合风险(取最高)。
        is_robust: 是否鲁棒(总体风险非 HIGH)。
    """

    sensitivities: list[ParameterSensitivity] = field(default_factory=list)
    overall_stability: float = 0.0
    overall_overfit_risk: OverfitRisk = OverfitRisk.HIGH
    is_robust: bool = False


_RISK_RANK: dict[OverfitRisk, int] = {
    OverfitRisk.LOW: 1,
    OverfitRisk.MEDIUM: 2,
    OverfitRisk.HIGH: 3,
}


def _std(values: list[float]) -> float:
    """样本标准差(ddof=1)。"""
    n = len(values)
    if n < 2:
        return 0.0
    m = sum(values) / n
    return math.sqrt(sum((v - m) ** 2 for v in values) / (n - 1))


class ParameterRobustnessTester:
    """参数鲁棒性测试器——寻找稳定区间而非最优值。

    Usage:
        tester = ParameterRobustnessTester()

        # 测试单参数(如均线周期对Sharpe的影响)
        sens = tester.test_parameter(
            objective_func=lambda p: backtest_sharpe(period=int(p)),
            param_name="ma_period",
            param_values=[5, 10, 15, 20, 25, 30],
        )
        print(sens.overfit_risk, sens.stability_ratio)

        # 多参数汇总
        report = tester.assess([sens1, sens2])
        print(tester.audit_summary(report))
    """

    def __init__(self, config: RobustnessConfig | None = None) -> None:
        self._config = config if config is not None else RobustnessConfig()

    @property
    def config(self) -> RobustnessConfig:
        """配置(只读)。"""
        return self._config

    def test_parameter(
        self,
        objective_func: Callable[[float], float],
        param_name: str,
        param_values: list[float],
        baseline: float | None = None,
    ) -> ParameterSensitivity:
        """测试单个参数的鲁棒性。

        Args:
            objective_func: 目标函数, 接受参数值返回目标值(越大越好)。
            param_name: 参数名。
            param_values: 待测试参数值序列(需排序以正确检测连续区间)。
            baseline: 基准目标值, None=用最大目标值。

        Returns:
            ParameterSensitivity

        Raises:
            SimulationError: 参数序列为空 / 单值无法计算区间。
        """
        if not param_values:
            raise SimulationError(
                "param_values 不能为空",
                details={"param_name": param_name},
            )
        if len(param_values) < 2:
            raise SimulationError(
                f"param_values 至少需要 2 个值(当前 {len(param_values)})",
                details={"param_name": param_name, "count": len(param_values)},
            )

        # 1. 计算各参数点的目标值
        points = [ParameterPoint(param_value=v, objective=float(objective_func(v))) for v in param_values]
        objectives = [p.objective for p in points]

        # 2. 基准与最优
        opt_idx = max(range(len(objectives)), key=lambda i: objectives[i])
        optimal_value = points[opt_idx].param_value
        optimal_objective = objectives[opt_idx]
        base = baseline if baseline is not None else optimal_objective

        # 3. 总范围
        pmin = min(param_values)
        pmax = max(param_values)
        total_range = pmax - pmin

        # 4. 稳定区间
        stable_region = self._find_stable_region(points, base, total_range)

        # 5. 稳定性比率
        if stable_region is not None and total_range > 0:
            stability_ratio = stable_region.width / total_range
        else:
            stability_ratio = 0.0
        # 钳制到 [0, 1]
        stability_ratio = max(0.0, min(1.0, stability_ratio))

        # 6. 过拟合风险
        risk = self._classify_risk(stability_ratio)

        result = ParameterSensitivity(
            param_name=param_name,
            points=points,
            optimal_value=optimal_value,
            optimal_objective=optimal_objective,
            stable_region=stable_region,
            total_range=total_range,
            stability_ratio=stability_ratio,
            objective_std=_std(objectives),
            overfit_risk=risk,
        )
        _logger.debug(
            "参数鲁棒性[%s]: ratio=%.3f risk=%s stable=%s",
            param_name,
            stability_ratio,
            risk.value,
            f"[{stable_region.low},{stable_region.high}]" if stable_region else "None",
        )
        return result

    def _find_stable_region(
        self,
        points: list[ParameterPoint],
        baseline: float,
        total_range: float,
    ) -> StableRegion | None:
        """找最大连续稳定区间(目标值>=baseline*threshold_ratio)。

        稳定点按 param_value 排序后找最长连续 run。
        """
        threshold = baseline * self._config.stable_threshold_ratio
        # 按 param_value 排序
        sorted_pts = sorted(points, key=lambda p: p.param_value)
        stable_flags = [p.objective >= threshold for p in sorted_pts]
        if not any(stable_flags):
            return None

        # 找最长连续 True run
        best_start = 0
        best_len = 0
        cur_start = 0
        cur_len = 0
        for i, flag in enumerate(stable_flags):
            if flag:
                if cur_len == 0:
                    cur_start = i
                cur_len += 1
                if cur_len > best_len:
                    best_len = cur_len
                    best_start = cur_start
            else:
                cur_len = 0

        region_pts = sorted_pts[best_start : best_start + best_len]
        low = region_pts[0].param_value
        high = region_pts[-1].param_value
        width = high - low
        return StableRegion(low=low, high=high, width=width, point_count=best_len)

    def _classify_risk(self, stability_ratio: float) -> OverfitRisk:
        """按稳定性比率分级过拟合风险。"""
        cfg = self._config
        if stability_ratio >= cfg.low_risk_min_ratio:
            return OverfitRisk.LOW
        if stability_ratio < cfg.high_risk_max_ratio:
            return OverfitRisk.HIGH
        return OverfitRisk.MEDIUM

    # ------------------------------------------------------------------
    # 扰动测试
    # ------------------------------------------------------------------
    def perturb_parameter(
        self,
        objective_func: Callable[[float], float],
        param_name: str,
        baseline_value: float,
        perturbations: list[float] | None = None,
    ) -> PerturbationResult:
        """对基准参数施加扰动, 测量目标值退化。

        Args:
            objective_func: 目标函数。
            param_name: 参数名。
            baseline_value: 基准参数值。
            perturbations: 扰动比例列表(相对基准值), None=用 config 默认。

        Returns:
            PerturbationResult

        Raises:
            SimulationError: baseline_value 为 0 无法施加比例扰动。
        """
        if baseline_value == 0:
            raise SimulationError(
                "baseline_value=0 无法施加比例扰动",
                details={"param_name": param_name},
            )
        perts = tuple(perturbations) if perturbations is not None else self._config.default_perturbations
        baseline_obj = float(objective_func(baseline_value))
        objectives: list[float] = []
        max_deg = 0.0
        for ratio in perts:
            perturbed = baseline_value * (1.0 + ratio)
            obj = float(objective_func(perturbed))
            objectives.append(obj)
            if baseline_obj != 0:
                deg = abs(baseline_obj - obj) / abs(baseline_obj)
                max_deg = max(max_deg, deg)
        is_stable = max_deg < self._config.perturbation_stable_threshold
        result = PerturbationResult(
            param_name=param_name,
            baseline_value=baseline_value,
            baseline_objective=baseline_obj,
            perturbations=perts,
            objectives=tuple(objectives),
            max_degradation=max_deg,
            is_stable=is_stable,
        )
        _logger.debug(
            "扰动测试[%s]: max_deg=%.4f stable=%s",
            param_name,
            max_deg,
            is_stable,
        )
        return result

    # ------------------------------------------------------------------
    # 汇总评估
    # ------------------------------------------------------------------
    def assess(self, sensitivities: list[ParameterSensitivity]) -> RobustnessReport:
        """汇总多参数鲁棒性。

        Args:
            sensitivities: 各参数敏感性结果。

        Returns:
            RobustnessReport

        Raises:
            SimulationError: 列表为空。
        """
        if not sensitivities:
            raise SimulationError("sensitivities 不能为空")

        ratios = [s.stability_ratio for s in sensitivities]
        overall_stability = sum(ratios) / len(ratios)
        # 总体风险取最高(最差参数决定整体风险)
        overall_risk = max(
            (s.overfit_risk for s in sensitivities),
            key=lambda r: _RISK_RANK[r],
        )
        is_robust = overall_risk != OverfitRisk.HIGH
        report = RobustnessReport(
            sensitivities=sensitivities,
            overall_stability=overall_stability,
            overall_overfit_risk=overall_risk,
            is_robust=is_robust,
        )
        _logger.debug(
            "鲁棒性汇总: stability=%.3f risk=%s robust=%s",
            overall_stability,
            overall_risk.value,
            is_robust,
        )
        return report

    # ------------------------------------------------------------------
    # 审计摘要
    # ------------------------------------------------------------------
    def audit_summary(self, report: RobustnessReport) -> str:
        """生成审计摘要文本。"""
        lines: list[str] = []
        lines.append("=== 参数鲁棒性测试审计 ===")
        verdict = "PASS(参数鲁棒)" if report.is_robust else "FAIL(参数过拟合风险)"
        lines.append(f"结论: {verdict}")
        lines.append(
            f"总体稳定性: {report.overall_stability:.3f} | 总体过拟合风险: {report.overall_overfit_risk.value}"
        )
        lines.append(f"参数数: {len(report.sensitivities)}")
        if report.sensitivities:
            lines.append("")
            lines.append("各参数明细:")
            for s in report.sensitivities:
                sr = s.stable_region
                region_str = f"[{sr.low:.4g}, {sr.high:.4g}] (width={sr.width:.4g}, {sr.point_count}点)" if sr else "无"
                lines.append(
                    f"  - {s.param_name}: ratio={s.stability_ratio:.3f} "
                    f"risk={s.overfit_risk.value} optimal={s.optimal_value:.4g} "
                    f"stable={region_str}"
                )
        return "\n".join(lines)


__all__ = [
    "OverfitRisk",
    "ParameterPoint",
    "ParameterRobustnessTester",
    "ParameterSensitivity",
    "PerturbationResult",
    "RobustnessConfig",
    "RobustnessReport",
    "SimulationError",
    "StableRegion",
]
