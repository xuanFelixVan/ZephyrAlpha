# [BLUEPRINT] MOD-SIM-012 | docs/03_modules/_domain_simulation/result_analyzer/blueprint.md
# [MODULE] zephyr.simulation.result_analyzer
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.simulation.strategy_simulator ; zephyr.shared.foundation.errors
# [CONSUMERS] D_FRONTEND可视化 ; 人工审查 ; C-007 AI自治进化闭环
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯numpy统计; 全frozen不可变; 空列表→空聚合; 单场景std/CI退化; 不修改输入
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SimulationAnalysisError(ZA-SIM-0012)
# [TESTS] tests/simulation/test_result_analyzer.py
# [A_module] module_id=MOD-SIM-012 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_SIMULATION — Simulation Result Analyzer (仿真结果分析器)

对多个 SimulationResult(跨场景, 来自 SIM-02)执行聚合统计分析+分布检验+可视化数据准备,
输出 SimulationAnalysisReport。是仿真流水线分析终点(策略仿真→结果分析)。

跨场景回答"策略在 N 个 what-if 场景下整体表现如何": 均值/标准差/分位数/置信区间
+ 收益分布正态性检验(Jarque-Bera) + 可视化数据。

属 A 类基础设施(纯 numpy 统计), 自包含不跨域依赖 D_BACKTEST metrics。
设计真源: D-SIMULATION-12 "仿真结果分析+统计检验+可视化 | 与D-FRONTEND联动"
蓝图: docs/03_modules/_domain_simulation/result_analyzer/blueprint.md
SSoT: depgraph MOD-SIM-012

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 跨场景仿真结果列表 list[SimulationResult]
#   fields: 各场景equity_curve(时间戳+权益) + total_return + trades_count（来自SIM-02策略仿真器）
#   code: analyze(results) L219
# - id: I2
#   name: 分析配置 AnalysisConfig
#   fields: 置信水平0.95 + 无风险利率 + 年化因子252 + 直方图10桶 + JB临界值5.99
#   code: AnalysisConfig L75
# 层: 特征
# - id: F1
#   name_zh: 收益率偏度
#   name_en: skew
#   intro: 全场景bar收益率分布的不对称程度
#   formula: skew=mean(((r-μ)/σ)³)；σ=0时取0
#   code: result_analyzer.py L410
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 收益率超额峰度
#   name_en: kurt
#   intro: 全场景bar收益率分布的厚尾程度（正态=0）
#   formula: kurt=mean(((r-μ)/σ)⁴)-3；σ=0时取0
#   code: result_analyzer.py L411
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 单场景指标计算
#   name_en: _compute_scenario_metrics
#   intro: 从权益曲线算出单场景7项业绩指标
#   desc: returns=Δeq/eq[:-1](剔除非有限值) → 年化=(1+total_ret)^(252/bars)-1 → vol=std×√252 → sharpe=(年化-rf)/vol → max_dd=min((eq-峰值)/峰值) → win_rate=mean(returns>0)
#   inputs: I1 I2
#   outputs: ScenarioMetrics(7指标)
# - id: A2
#   name_zh: ② 跨场景聚合统计
#   name_en: _aggregate
#   intro: 对7项指标跨场景算均值/标准差/分位数/置信区间
#   desc: 每指标取各场景值 → mean/std(ddof=1)/min/max/p5~p95 → CI=mean±z·std/√n（N<2时CI=None）；空列表→空聚合
#   inputs: A1 I2
#   outputs: AggregateAnalysis
#   invariant: 空列表→空聚合；单场景CI退化None
# - id: A3
#   name_zh: ③ 收益分布正态性检验
#   name_en: _analyze_distribution
#   intro: 汇总全场景收益率做直方图+Jarque-Bera正态检验
#   desc: 收集所有场景bar收益率 → np.histogram(10桶) → JB=n/6×(S²+K²/4) → is_normal=(JB<5.99)；样本<3返回空分布默认正态
#   inputs: I1 I2 F1 F2
#   outputs: DistributionAnalysis
# - id: A4
#   name_zh: ④ 可视化数据准备
#   name_en: _build_visualization
#   intro: 打包各场景权益曲线集合+指标均值摘要供前端画图
#   desc: equity_curve_ensemble=各场景[(ts,equity)]列表 + metric_summary=各指标均值dict
#   inputs: I1 A2
#   outputs: VisualizationData
# - id: A5
#   name_zh: ⑤ 分析摘要生成
#   name_en: _build_summary
#   intro: 把聚合与分布结论拼成人类可读摘要
#   desc: 场景数 + 平均总收益(std) + 95%置信区间 + 平均Sharpe + 正态性结论(JB/偏度)
#   inputs: A2 A3 I2
#   outputs: 摘要字符串
# 层: 输出
# - id: O1
#   name_zh: 仿真结果分析报告 SimulationAnalysisReport
#   name_en: SimulationAnalysisReport
#   intro: 含跨场景聚合+分布检验+可视化数据+摘要的不可变报告（仿真流水线分析终点）
#   invariant: 全frozen不可变；不修改输入
#   downstream: D_FRONTEND可视化 ; 人工审查 ; C-007 AI自治进化闭环（[CONSUMERS]）
# - id: O2
#   name_zh: 单场景指标 ScenarioMetrics
#   name_en: ScenarioMetrics
#   intro: analyze_single公开API返回的单场景7项业绩指标
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# I1 --> A1
# I2 --> A1
# A1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# F1 --> A3
# F2 --> A3
# I1 --> A4
# A2 --> A4
# A2 --> A5
# A3 --> A5
# I2 --> A5
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A5 --> O1
# A1 --> O2
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Final

import numpy as np

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.simulation.strategy_simulator import SimulationResult

__all__: Final = [
    "AnalysisConfig",
    "ScenarioMetrics",
    "MetricAggregate",
    "AggregateAnalysis",
    "DistributionAnalysis",
    "VisualizationData",
    "SimulationAnalysisReport",
    "SimulationResultAnalyzer",
    "SimulationAnalysisError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class SimulationAnalysisError(ZephyrBaseError):
    """仿真结果分析输入非法(非 list / 元素非 SimulationResult)。"""

    error_code = "ZA-SIM-0012"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AnalysisConfig:
    """仿真结果分析配置——不可变。"""

    confidence_level: float = 0.95  # 置信水平
    risk_free_rate: float = 0.0  # 无风险利率(年化)
    annualization_factor: int = 252  # 年化因子(交易日)
    histogram_bins: int = 10  # 直方图分桶数
    jb_critical_value: float = 5.99  # Jarque-Bera 5% 临界值(chi2, df=2)

    def __post_init__(self) -> None:
        if not 0 < self.confidence_level < 1:
            raise SimulationAnalysisError(f"confidence_level must be in (0,1), got {self.confidence_level}")
        if self.annualization_factor <= 0:
            raise SimulationAnalysisError(f"annualization_factor must be > 0, got {self.annualization_factor}")
        if self.histogram_bins <= 0:
            raise SimulationAnalysisError(f"histogram_bins must be > 0, got {self.histogram_bins}")


# 置信水平 → z 值
_Z_LEVELS: Final = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}


def _z_for_level(level: float) -> float:
    return _Z_LEVELS.get(level, 1.96)


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型 (frozen 不可变)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ScenarioMetrics:
    """单场景指标——不可变。"""

    total_return: float
    annualized_return: float
    volatility: float
    sharpe: float
    max_drawdown: float
    win_rate: float
    trades_count: int


@dataclass(frozen=True)
class MetricAggregate:
    """单指标的跨场景聚合——不可变。"""

    name: str
    mean: float
    std: float
    min: float
    max: float
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float
    ci_lower: float | None  # 均值置信区间下界 (None=N<2)
    ci_upper: float | None  # 均值置信区间上界 (None=N<2)


@dataclass(frozen=True)
class AggregateAnalysis:
    """跨场景聚合分析——不可变。"""

    scenario_count: int
    metrics: dict[str, MetricAggregate]


@dataclass(frozen=True)
class DistributionAnalysis:
    """收益率分布分析——不可变。"""

    histogram_bins: list[float]  # 分桶边界
    histogram_counts: list[int]  # 各桶计数
    skewness: float
    kurtosis: float  # 超额峰度(正态=0)
    jarque_bera_stat: float
    is_normal: bool  # JB < 临界值 → 正态
    total_returns: int  # 收益率样本数


@dataclass(frozen=True)
class VisualizationData:
    """可视化数据——不可变。"""

    equity_curve_ensemble: list[list[tuple[Any, float]]]  # 各场景 [(ts, equity), ...]
    metric_summary: dict[str, float]  # 各指标均值(供箱线图/摘要)


@dataclass(frozen=True)
class SimulationAnalysisReport:
    """仿真结果分析报告——不可变。"""

    aggregate: AggregateAnalysis
    distribution: DistributionAnalysis
    visualization: VisualizationData
    summary: str


# ──────────────────────────────────────────────────────────────────────────────
# 仿真结果分析器
# ──────────────────────────────────────────────────────────────────────────────

# 待聚合的指标名
_METRIC_NAMES: Final = [
    "total_return",
    "annualized_return",
    "volatility",
    "sharpe",
    "max_drawdown",
    "win_rate",
    "trades_count",
]


class SimulationResultAnalyzer:
    """仿真结果分析器——跨场景聚合统计+分布检验+可视化数据。

    用法:
        analyzer = SimulationResultAnalyzer()
        # results = [sim.run(scenario_i, strategy) for i in range(N)]
        report = analyzer.analyze(results)
        print(report.summary)
        # report.aggregate.metrics["total_return"].mean  # 平均总收益
        # report.distribution.is_normal                  # 收益是否正态

    纯 numpy 统计计算, 不修改输入。

    Args:
        config: 分析配置(置信水平/无风险利率/年化因子/直方图桶数)
    """

    def __init__(self, config: AnalysisConfig | None = None) -> None:
        self._config = config or AnalysisConfig()

    @property
    def config(self) -> AnalysisConfig:
        return self._config

    # ── 公开 API ──

    def analyze(self, results: list[SimulationResult]) -> SimulationAnalysisReport:
        """对多个 SimulationResult 执行聚合分析。

        Args:
            results: 跨场景仿真结果列表

        Returns:
            SimulationAnalysisReport (聚合+分布+可视化+摘要)

        Raises:
            SimulationAnalysisError: results 非 list / 元素非 SimulationResult
        """
        if not isinstance(results, list):
            raise SimulationAnalysisError(f"results must be a list, got {type(results).__name__}")
        for i, r in enumerate(results):
            if not isinstance(r, SimulationResult):
                raise SimulationAnalysisError(f"results[{i}] must be SimulationResult, got {type(r).__name__}")

        # 单场景指标
        scenario_metrics = [self._compute_scenario_metrics(r) for r in results]

        # 跨场景聚合
        aggregate = self._aggregate(scenario_metrics)

        # 分布分析(收集所有场景的收益率)
        all_returns = self._collect_returns(results)
        distribution = self._analyze_distribution(all_returns)

        # 可视化数据
        visualization = self._build_visualization(results, aggregate)

        # 摘要
        summary = self._build_summary(aggregate, distribution)

        return SimulationAnalysisReport(
            aggregate=aggregate,
            distribution=distribution,
            visualization=visualization,
            summary=summary,
        )

    def analyze_single(self, result: SimulationResult) -> ScenarioMetrics:
        """计算单个 SimulationResult 的指标。"""
        if not isinstance(result, SimulationResult):
            raise SimulationAnalysisError(f"result must be SimulationResult, got {type(result).__name__}")
        return self._compute_scenario_metrics(result)

    # ── 内部: 单场景指标 ──

    def _compute_scenario_metrics(self, result: SimulationResult) -> ScenarioMetrics:
        cfg = self._config
        equities = [p.equity for p in result.equity_curve]

        if len(equities) < 2:
            # 不足以算收益统计
            return ScenarioMetrics(
                total_return=result.total_return,
                annualized_return=result.total_return,
                volatility=0.0,
                sharpe=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                trades_count=result.trades_count,
            )

        eq = np.array(equities, dtype=float)
        # 收益率序列
        returns = np.diff(eq) / eq[:-1]
        # 防止除零(eq 含 0)
        returns = returns[np.isfinite(returns)]

        n = len(returns)
        # 年化收益
        total_ret = result.total_return
        bars = len(equities)
        if total_ret > -1 and bars > 0:
            annualized = (1 + total_ret) ** (cfg.annualization_factor / bars) - 1
        else:
            annualized = total_ret

        # 波动率(年化)
        vol = float(np.std(returns, ddof=1)) * math.sqrt(cfg.annualization_factor) if n > 1 else 0.0

        # Sharpe
        sharpe = (annualized - cfg.risk_free_rate) / vol if vol > 0 else 0.0

        # 最大回撤
        peak = np.maximum.accumulate(eq)
        drawdown = (eq - peak) / peak
        max_dd = float(drawdown.min()) if len(drawdown) > 0 else 0.0

        # 胜率(正收益 bar 占比)
        win_rate = float(np.mean(returns > 0)) if n > 0 else 0.0

        return ScenarioMetrics(
            total_return=total_ret,
            annualized_return=annualized,
            volatility=vol,
            sharpe=sharpe,
            max_drawdown=max_dd,
            win_rate=win_rate,
            trades_count=result.trades_count,
        )

    # ── 内部: 跨场景聚合 ──

    def _aggregate(self, scenario_metrics: list[ScenarioMetrics]) -> AggregateAnalysis:
        n = len(scenario_metrics)
        if n == 0:
            return AggregateAnalysis(scenario_count=0, metrics={})

        metrics: dict[str, MetricAggregate] = {}
        z = _z_for_level(self._config.confidence_level)

        for name in _METRIC_NAMES:
            values = np.array([getattr(sm, name) for sm in scenario_metrics], dtype=float)
            mean = float(np.mean(values))
            std = float(np.std(values, ddof=1)) if n > 1 else 0.0
            # 置信区间 (N>=2 时)
            if n >= 2 and std > 0:
                se = std / math.sqrt(n)
                ci_lower = mean - z * se
                ci_upper = mean + z * se
            elif n >= 2:
                ci_lower = mean
                ci_upper = mean
            else:
                ci_lower = None
                ci_upper = None

            metrics[name] = MetricAggregate(
                name=name,
                mean=mean,
                std=std,
                min=float(np.min(values)),
                max=float(np.max(values)),
                p5=float(np.percentile(values, 5)),
                p25=float(np.percentile(values, 25)),
                p50=float(np.percentile(values, 50)),
                p75=float(np.percentile(values, 75)),
                p95=float(np.percentile(values, 95)),
                ci_lower=ci_lower,
                ci_upper=ci_upper,
            )

        return AggregateAnalysis(scenario_count=n, metrics=metrics)

    # ── 内部: 分布分析 ──

    def _collect_returns(self, results: list[SimulationResult]) -> np.ndarray:
        """收集所有场景的 bar 收益率。"""
        all_returns: list[float] = []
        for r in results:
            equities = [p.equity for p in r.equity_curve]
            if len(equities) < 2:
                continue
            eq = np.array(equities, dtype=float)
            rets = np.diff(eq) / eq[:-1]
            all_returns.extend(rets[np.isfinite(rets)].tolist())
        return np.array(all_returns, dtype=float)

    def _analyze_distribution(self, returns: np.ndarray) -> DistributionAnalysis:
        cfg = self._config
        n = len(returns)

        if n < 3:
            # 样本不足, 返回空分布
            return DistributionAnalysis(
                histogram_bins=[],
                histogram_counts=[],
                skewness=0.0,
                kurtosis=0.0,
                jarque_bera_stat=0.0,
                is_normal=True,  # 样本不足默认不拒绝
                total_returns=n,
            )

        # 直方图
        counts, edges = np.histogram(returns, bins=cfg.histogram_bins)
        # 偏度/峰度
        mean = float(np.mean(returns))
        std = float(np.std(returns, ddof=1))
        if std > 0:
            skew = float(np.mean(((returns - mean) / std) ** 3))
            kurt = float(np.mean(((returns - mean) / std) ** 4)) - 3.0  # 超额峰度
        else:
            skew = 0.0
            kurt = 0.0

        # Jarque-Bera: JB = N/6 * (S² + K²/4)
        jb = (n / 6.0) * (skew**2 + (kurt**2) / 4.0)
        is_normal = jb < cfg.jb_critical_value

        return DistributionAnalysis(
            histogram_bins=edges.tolist(),
            histogram_counts=counts.tolist(),
            skewness=skew,
            kurtosis=kurt,
            jarque_bera_stat=float(jb),
            is_normal=is_normal,
            total_returns=n,
        )

    # ── 内部: 可视化数据 ──

    def _build_visualization(self, results: list[SimulationResult], aggregate: AggregateAnalysis) -> VisualizationData:
        ensemble = [[(p.timestamp, p.equity) for p in r.equity_curve] for r in results]
        metric_summary = {name: agg.mean for name, agg in aggregate.metrics.items()}
        return VisualizationData(
            equity_curve_ensemble=ensemble,
            metric_summary=metric_summary,
        )

    # ── 内部: 摘要 ──

    def _build_summary(self, aggregate: AggregateAnalysis, distribution: DistributionAnalysis) -> str:
        cfg = self._config
        n = aggregate.scenario_count
        if n == 0:
            return "无仿真结果可分析。"

        tr = aggregate.metrics.get("total_return")
        sharpe = aggregate.metrics.get("sharpe")
        parts = [
            f"共分析 {n} 个仿真场景。",
            f"平均总收益: {tr.mean:.2%} (std={tr.std:.2%})" if tr else "平均总收益: N/A",
        ]
        if tr and tr.ci_lower is not None:
            parts.append(f"{int(cfg.confidence_level * 100)}% 置信区间: [{tr.ci_lower:.2%}, {tr.ci_upper:.2%}]")
        if sharpe:
            parts.append(f"平均 Sharpe: {sharpe.mean:.3f}")
        parts.append(
            f"收益率分布: {'正态' if distribution.is_normal else '非正态'}"
            f"(JB={distribution.jarque_bera_stat:.2f}, 偏度={distribution.skewness:.3f})"
        )
        return " | ".join(parts)
