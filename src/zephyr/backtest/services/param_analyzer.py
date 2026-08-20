# [BLUEPRINT] MOD-BT-021 | docs/03_modules/_domain_backtest/param_analyzer/blueprint.md
# [MODULE] zephyr.backtest.services.param_analyzer
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.services.cache_manager ; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-BT-019(report_generator) ; 人工审查
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ParamRun/Sensitivity/Overfitting/Config/Report frozen不可变; 空列表raise; 单条记录返回空敏感度; 不修改输入
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ParamAnalysisError(ZA-BT-0021)
# [TESTS] tests/backtest/test_param_analyzer.py
# [A_module] module_id=MOD-BT-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_BACKTEST — Parameter Analyzer (参数优化结果分析器)

对多组参数回测结果执行显著性分析和过拟合检测。
识别最优参数组合, 评估各参数敏感度, 检测 IS/OOS 性能差距, 评估统计稳定性。

属 A 类基础设施(纯统计分析+阈值判定), 纯基础层不涉及策略。

设计真源: depgraph MOD-BT-021
蓝图: docs/03_modules/_domain_backtest/param_analyzer/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 参数运行列表 list[ParamRun]
#   fields: params dict + objective目标值 + in_sample + out_of_sample可选
#   code: runs
# - id: I2
#   name: 分析配置 ParamAnalysisConfig frozen
#   fields: sensitivity_threshold=0.5 + overfit_threshold=0.5 + stability_cv_threshold=0.1 + top_n=5
#   code: ParamAnalysisConfig L124-148
# 层: 算法
# - id: A1
#   name_zh: ① 最优参数选择
#   name_en: analyze(选优段)
#   intro: 按目标值取最大的那组参数当最优
#   desc: 空runs直接raise → best_run=max(runs, key=objective)（L203-218）
#   inputs: I1
#   outputs: best_run
#   invariant: 空列表raise ParamAnalysisError
# - id: A2
#   name_zh: ② 参数敏感度分析
#   name_en: _compute_sensitivities
#   intro: 按参数值分组看目标均值极差占总体波动几成
#   desc: 汇总参数名 → 按参数值分组求组均值 → sensitivity=(max组均值-min组均值)/总体std → >0.5判显著（L248-289）
#   inputs: I1 I2
#   outputs: ParamSensitivity列表
#   invariant: 单条记录返回空敏感度
# - id: A3
#   name_zh: ③ 过拟合检测
#   name_en: _check_overfitting
#   intro: 样本内好看样本外拉胯就是过拟合
#   desc: 取有IS/OOS的最优run → overfit_score=(IS-OOS)/|IS| → >0.5判过拟合 无OOS数据返回None（L294-320）
#   inputs: I1 I2
#   outputs: OverfittingCheck或None
# - id: A4
#   name_zh: ④ 稳定性评估
#   name_en: _assess_stability
#   intro: 前5名结果的变异系数越小参数越稳
#   desc: objective降序取top_n → CV=std/|mean| → <0.1判稳定 均值≈0直接判稳定（L325-348）
#   inputs: I1 I2
#   outputs: StabilityAssessment或None
# - id: A5
#   name_zh: ⑤ 报告组装与缓存
#   name_en: analyze+_cache_report
#   intro: 拼frozen分析报告，可选顺手写进BT-020缓存
#   desc: 组装ParamAnalysisReport → cache非空则compute_key+put缓存摘要 失败仅warning（L223-243, L353-373）
#   inputs: A1 A2 A3 A4
#   outputs: ParamAnalysisReport
# 层: 输出
# - id: O1
#   name_zh: 参数分析报告 ParamAnalysisReport
#   name_en: ParamAnalysisReport
#   intro: 最优参数+敏感度+过拟合+稳定性四件套，供报告生成和人工审查
#   invariant: Report frozen不可变; 不修改输入
#   downstream: report_generator MOD-BT-019 ; 人工审查
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# I1 --> A4
# I2 --> A4
# A1 --> A5
# A2 --> A5
# A3 --> A5
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

from zephyr.backtest.services.cache_manager import BacktestCacheManager, CacheKey
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ParamAnalysisError",
    "ParamRun",
    "ParamSensitivity",
    "OverfittingCheck",
    "StabilityAssessment",
    "ParamAnalysisConfig",
    "ParamAnalysisReport",
    "ParameterAnalyzer",
]

_logger = logging.getLogger(__name__)


class ParamAnalysisError(ZephyrBaseError):
    """参数分析异常——输入非法。"""

    error_code = "ZA-BT-0021"


@dataclass(frozen=True)
class ParamRun:
    """单次参数优化运行——不可变。

    Attributes:
        params: 参数字典。
        objective: 目标函数值 (越大越好)。
        in_sample: 样本内指标 (可选)。
        out_of_sample: 样本外指标 (可选)。
    """

    params: dict
    objective: float
    in_sample: float | None = None
    out_of_sample: float | None = None


@dataclass(frozen=True)
class ParamSensitivity:
    """单个参数的敏感度分析——不可变。

    Attributes:
        param_name: 参数名。
        sensitivity: 敏感度 (组间均值极差 / 总体标准差)。
        is_significant: 是否显著 (> threshold)。
        group_means: 各参数值对应的目标均值。
    """

    param_name: str
    sensitivity: float
    is_significant: bool
    group_means: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class OverfittingCheck:
    """过拟合检测结果——不可变。

    Attributes:
        overfit_score: 过拟合分数 (IS-OOS)/|IS|, 越高越严重。
        is_overfit: 是否过拟合 (> threshold)。
        in_sample: 样本内指标。
        out_of_sample: 样本外指标。
    """

    overfit_score: float
    is_overfit: bool
    in_sample: float
    out_of_sample: float


@dataclass(frozen=True)
class StabilityAssessment:
    """稳定性评估——不可变。

    Attributes:
        coefficient_of_variation: top_n 结果的变异系数。
        is_stable: 是否稳定 (CV < threshold)。
        top_n: 评估的最优结果数。
    """

    coefficient_of_variation: float
    is_stable: bool
    top_n: int


@dataclass(frozen=True)
class ParamAnalysisConfig:
    """参数分析配置——不可变。

    Attributes:
        sensitivity_threshold: 敏感度显著性阈值。
        overfit_threshold: 过拟合分数阈值。
        stability_cv_threshold: 稳定性 CV 阈值。
        top_n: 稳定性评估的最优结果数。
    """

    sensitivity_threshold: float = 0.5
    overfit_threshold: float = 0.5
    stability_cv_threshold: float = 0.1
    top_n: int = 5

    def __post_init__(self) -> None:
        if self.sensitivity_threshold <= 0:
            raise ParamAnalysisError(f"sensitivity_threshold must be > 0, got {self.sensitivity_threshold}")
        if self.top_n <= 0:
            raise ParamAnalysisError(f"top_n must be > 0, got {self.top_n}")


@dataclass(frozen=True)
class ParamAnalysisReport:
    """参数分析报告——不可变。

    Attributes:
        best_run: 最优参数运行。
        total_runs: 总运行数。
        sensitivities: 各参数敏感度列表。
        overfitting: 过拟合检测 (无 OOS 数据时为 None)。
        stability: 稳定性评估。
    """

    best_run: ParamRun | None
    total_runs: int
    sensitivities: list[ParamSensitivity] = field(default_factory=list)
    overfitting: OverfittingCheck | None = None
    stability: StabilityAssessment | None = None


class ParameterAnalyzer:
    """参数优化结果分析器——显著性+过拟合+稳定性。

    Usage:
        analyzer = ParameterAnalyzer()
        runs = [
            ParamRun(params={"fast": 5, "slow": 20}, objective=1.5,
                     in_sample=2.0, out_of_sample=1.0),
            ParamRun(params={"fast": 10, "slow": 20}, objective=1.2,
                     in_sample=1.8, out_of_sample=1.1),
        ]
        report = analyzer.analyze(runs)
        print(f"Best: {report.best_run.params} objective={report.best_run.objective}")
        if report.overfitting and report.overfitting.is_overfit:
            print("过拟合风险!")
    """

    def __init__(
        self,
        config: ParamAnalysisConfig | None = None,
        cache: BacktestCacheManager | None = None,
    ) -> None:
        self._config = config if config is not None else ParamAnalysisConfig()
        self._cache = cache

    @property
    def config(self) -> ParamAnalysisConfig:
        """配置 (只读)。"""
        return self._config

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------
    def analyze(self, runs: list[ParamRun]) -> ParamAnalysisReport:
        """分析参数优化结果。

        Args:
            runs: 参数运行列表。

        Returns:
            ParamAnalysisReport

        Raises:
            ParamAnalysisError: runs 为空。
        """
        if not runs:
            raise ParamAnalysisError("runs 不能为空")

        best_run = max(runs, key=lambda r: r.objective)
        sensitivities = self._compute_sensitivities(runs)
        overfitting = self._check_overfitting(runs)
        stability = self._assess_stability(runs)

        report = ParamAnalysisReport(
            best_run=best_run,
            total_runs=len(runs),
            sensitivities=sensitivities,
            overfitting=overfitting,
            stability=stability,
        )

        # 可选缓存
        if self._cache is not None:
            self._cache_report(report)

        _logger.debug(
            "参数分析: %d runs, best=%.4f, %d sensitivities, overfit=%s, stable=%s",
            len(runs),
            best_run.objective,
            len(sensitivities),
            overfitting.is_overfit if overfitting else "N/A",
            stability.is_stable if stability else "N/A",
        )
        return report

    # ------------------------------------------------------------------
    # 敏感度分析
    # ------------------------------------------------------------------
    def _compute_sensitivities(self, runs: list[ParamRun]) -> list[ParamSensitivity]:
        """计算各参数敏感度。"""
        if len(runs) < 2:
            return []

        # 收集所有参数名
        param_names: set[str] = set()
        for r in runs:
            param_names.update(r.params.keys())

        objectives = [r.objective for r in runs]
        overall_std = _std(objectives)
        if overall_std == 0:
            return []

        results: list[ParamSensitivity] = []
        for name in sorted(param_names):
            # 按参数值分组
            groups: dict[str, list[float]] = {}
            for r in runs:
                val = r.params.get(name)
                if val is not None:
                    key = str(val)
                    groups.setdefault(key, []).append(r.objective)

            if len(groups) < 2:
                # 参数只有一个值 → 无敏感度
                continue

            group_means = {k: _mean(v) for k, v in groups.items()}
            mean_vals = list(group_means.values())
            sensitivity = (max(mean_vals) - min(mean_vals)) / overall_std
            is_sig = sensitivity > self._config.sensitivity_threshold

            results.append(
                ParamSensitivity(
                    param_name=name,
                    sensitivity=sensitivity,
                    is_significant=is_sig,
                    group_means=group_means,
                )
            )

        return results

    # ------------------------------------------------------------------
    # 过拟合检测
    # ------------------------------------------------------------------
    def _check_overfitting(self, runs: list[ParamRun]) -> OverfittingCheck | None:
        """检测过拟合 (需要 IS/OOS 数据)。"""
        with_oos = [r for r in runs if r.out_of_sample is not None and r.in_sample is not None]
        if not with_oos:
            return None

        # 用最优运行的 IS/OOS
        best = max(with_oos, key=lambda r: r.objective)
        is_val = best.in_sample or 0.0
        oos_val = best.out_of_sample or 0.0

        if abs(is_val) < 1e-12:
            return OverfittingCheck(
                overfit_score=0.0,
                is_overfit=False,
                in_sample=is_val,
                out_of_sample=oos_val,
            )

        score = (is_val - oos_val) / abs(is_val)
        is_overfit = score > self._config.overfit_threshold
        return OverfittingCheck(
            overfit_score=score,
            is_overfit=is_overfit,
            in_sample=is_val,
            out_of_sample=oos_val,
        )

    # ------------------------------------------------------------------
    # 稳定性评估
    # ------------------------------------------------------------------
    def _assess_stability(self, runs: list[ParamRun]) -> StabilityAssessment | None:
        """评估 top_n 最优结果的稳定性。"""
        if len(runs) < 2:
            return None

        sorted_runs = sorted(runs, key=lambda r: r.objective, reverse=True)
        n = min(self._config.top_n, len(sorted_runs))
        top_objectives = [r.objective for r in sorted_runs[:n]]

        mean_val = _mean(top_objectives)
        if abs(mean_val) < 1e-12:
            return StabilityAssessment(
                coefficient_of_variation=0.0,
                is_stable=True,
                top_n=n,
            )

        cv = _std(top_objectives) / abs(mean_val)
        is_stable = cv < self._config.stability_cv_threshold
        return StabilityAssessment(
            coefficient_of_variation=cv,
            is_stable=is_stable,
            top_n=n,
        )

    # ------------------------------------------------------------------
    # 缓存
    # ------------------------------------------------------------------
    def _cache_report(self, report: ParamAnalysisReport) -> None:
        """将分析结果缓存到 BT-020 CacheManager。"""
        if self._cache is None or report.best_run is None:
            return
        try:
            key = self._cache.compute_key(
                strategy_id="param_analysis",
                params=report.best_run.params,
                start_date="1970-01-01",
                end_date="1970-01-01",
            )
            self._cache.put(
                key,
                {
                    "best_objective": report.best_run.objective,
                    "total_runs": report.total_runs,
                    "overfit_score": (report.overfitting.overfit_score if report.overfitting else None),
                },
            )
        except Exception:
            _logger.warning("缓存分析结果失败", exc_info=True)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _std(values: list[float], ddof: int = 1) -> float:
    n = len(values)
    if n <= ddof:
        return 0.0
    m = _mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (n - ddof))
