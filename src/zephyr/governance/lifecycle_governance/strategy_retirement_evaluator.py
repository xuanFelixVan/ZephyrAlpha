# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.strategy_retirement_evaluator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.reporting.report_publisher; docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml (SSoT，阈值 fail-closed 加载)
# [CONSUMERS] MOD-RPT-009(ReviewOrchestrator,月复盘退役判据扫描); 调用方(周/月退役评审)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 评审制铁律=判据触发只生成评估报告+人工裁定，本模块永不自动改策略状态;阈值唯一真源=alert_threshold_registry(THD-RETIRE-001/002/003 + THD-DEVIATION-002,fail-closed);偏离度量唯一真源=MOD-RK-23(本模块只消费 deviation 值不重算)
# [MODIFY-GUARD] 55_monitoring_review.md §3.5
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRetirementInputError;RetirementConfigError
# [TESTS] tests/governance/lifecycle/test_strategy_retirement_evaluator.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

D_GOVERNANCE — Strategy Retirement Evaluator（MOD-GOVERNANCE 伞，PLV 先例无独立 blueprint）

策略退役评估器——双判据 + 评审制（55 号 G26 §3.5 决策落地）。

代码现状缺口：仅因子级生命周期状态机有 retired 终态，model_drift_monitor 有一条
静态登记「Sharpe 30 日<0→策略退役评估」（DRIFT_MONITORS，无执行体）。
本模块闭合「判据触发 → 退役评估报告 → 人工裁定」链路的执行体。

判据体系（阈值真源 = alert_threshold_registry.yaml，fail-closed）:
  ①连续跑输判据 A：滚动 20 日实盘累计收益 − 基准累计收益 < −5%（THD-RETIRE-001）
  ①连续跑输判据 B：滚动 60 日 Sharpe < 0（THD-RETIRE-002）
  ①回撤漂移判据：当前回撤 > 1.5 × 历史最大回撤（THD-RETIRE-003）
  ①回测-实盘偏离判据：backtest_live_deviation > 0.50（THD-DEVIATION-002，
    偏离值由 MOD-RK-23 StrategyDeviationMonitor 供给——本模块不重算，真源唯一）
  ②逻辑失效判据：alpha_falsified（调用方供给：因子 IC 衰减退役联动
    factor_registry decay_state / 打板生态结构性变化人工判定）

评审制铁律（55 号 §3.5 决策 3 + LuxAlgo 2026-08 研究锚点）:
  退役不自动执行——判据触发 → 生成退役评估报告（ReportPublisher TRADING_REVIEW 源）
  → 人工裁定。个人项目策略 ≤5 个，误退役代价远高于评审成本；
  阈值是评审触发器，不是自动关停规则。

样本不足的判据跳过（detail 标注 insufficient_data），不产生误报。
入参封装为 RetirementEvalInput（NO-LONG-PARAM-LIST 合规：参数对象模式）。

SSoT: depgraph node=9664222 | 55 号 §3.5/§7⑤ | alert_threshold_registry THD-RETIRE-*
"""

from __future__ import annotations

import logging
import math
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Final, Sequence

import yaml

from zephyr.reporting.report_publisher import ReportPublisher, ReportSource
from zephyr.shared.alerts.threshold_loader import load_alert_thresholds
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class InvalidRetirementInputError(ZephyrBaseError):
    """退役评估输入非法。"""

    error_code = "ZA-GV-0046"


class RetirementConfigError(ZephyrBaseError):
    """阈值注册表缺失/畸形（fail-closed）。"""

    error_code = "ZA-GV-0047"


class RetirementCriterion(str, Enum):
    """退役判据五类（①跑输族 4 条 + ②逻辑失效 1 条）。"""

    ROLLING_UNDERPERFORMANCE = "rolling_underperformance"
    ROLLING_SHARPE_NEGATIVE = "rolling_sharpe_negative"
    DRAWDOWN_DRIFT = "drawdown_drift"
    BACKTEST_LIVE_DEVIATION = "backtest_live_deviation"
    ALPHA_FALSIFIED = "alpha_falsified"


@dataclass(frozen=True)
class RetirementEvalInput:
    """退役评估入参（参数对象，NO-LONG-PARAM-LIST 合规）。

    Attributes:
        strategy_id: 策略 ID
        live_returns: 实盘日收益序列（小数）
        benchmark_returns: 基准日收益序列（benchmark_registry 供给）
        backtest_live_deviation: MOD-RK-23 偏离值（None=跳过偏离判据）
        historical_max_drawdown: 历史最大回撤基线（strategy_registry baseline_max_drawdown；None/<=0=跳过）
        alpha_falsified: 逻辑失效判据（因子 decay_state 联动/人工判定）
        falsified_factors: 被证伪因子 ID 列表（证据）
        now: 评估时刻（默认 datetime.now(timezone.utc)）
        publish: 是否经 ReportPublisher 归档（测试可关）
    """

    strategy_id: str
    live_returns: Sequence[float]
    benchmark_returns: Sequence[float]
    backtest_live_deviation: float | None = None
    historical_max_drawdown: float | None = None
    alpha_falsified: bool = False
    falsified_factors: Sequence[str] = ()
    now: datetime | None = None
    publish: bool = True


@dataclass(frozen=True)
class TriggeredCriterion:
    """单条被触发判据的证据快照。"""

    criterion: RetirementCriterion
    metric_value: float | None
    threshold: float | None
    detail: str


@dataclass(frozen=True)
class RetirementEvaluationReport:
    """退役评估报告（评审制产物——status 恒 pending_human_review，永不自动退役）。"""

    report_id: str
    strategy_id: str
    evaluated_at: datetime
    triggered: tuple[TriggeredCriterion, ...]
    metrics: dict[str, float]
    falsified_factors: tuple[str, ...] = ()
    recommendation: str = "retire_review"
    status: str = "pending_human_review"


def _load_retirement_thresholds(registry_path: Path | None = None) -> dict[str, float]:
    """从告警阈值注册表加载退役判据阈值（fail-closed）。"""
    try:
        return load_alert_thresholds(
            {
                "THD-RETIRE-001": "underperformance_gap",
                "THD-RETIRE-002": "sharpe_floor",
                "THD-RETIRE-003": "drawdown_drift_multiplier",
                "THD-DEVIATION-002": "deviation_retire",
            },
            registry_path=registry_path,
        )
    except Exception as exc:
        raise RetirementConfigError(
            "阈值注册表加载失败",
            details={"error": str(exc), "path": str(registry_path or ALERT_THRESHOLD_REGISTRY_PATH)},
        ) from exc


def _as_float_list(values: Sequence[float], *, name: str) -> list[float]:
    """输入校验：数值序列 → list[float]；NaN/非数值 fail-closed（边界自查，不跨域引私有符号）。"""
    if values is None:
        raise InvalidRetirementInputError(f"{name} 不能为 None")
    out: list[float] = []
    for i, v in enumerate(values):
        try:
            f = float(v)
        except (TypeError, ValueError) as exc:
            raise InvalidRetirementInputError(f"{name}[{i}] 非数值: {v!r}") from exc
        if math.isnan(f) or math.isinf(f):
            raise InvalidRetirementInputError(f"{name}[{i}] 非法数值: {f}")
        out.append(f)
    return out


def _rolling_sharpe(daily_returns: list[float], periods_per_year: int = 252) -> float:
    """滚动年化 Sharpe（无风险利率 0）；零波动：均值<0 → -inf，否则 0。"""
    n = len(daily_returns)
    mean = sum(daily_returns) / n
    var = sum((r - mean) ** 2 for r in daily_returns) / n
    std = math.sqrt(var)
    if std < 1e-12:
        return float("-inf") if mean < 0 else 0.0
    return mean / std * math.sqrt(periods_per_year)


def _current_drawdown(daily_returns: list[float]) -> float:
    """由日收益序列重建净值曲线，取终点相对历史峰值的回撤。"""
    nav = 1.0
    peak = 1.0
    for r in daily_returns:
        nav *= 1.0 + r
        peak = max(peak, nav)
    if peak < 1e-12:
        return 0.0
    return max(0.0, 1.0 - nav / peak)


class StrategyRetirementEvaluator:
    """策略退役评估器（双判据 + 评审制，55 号 §3.5）。

    用法：周/月复盘时由调用方（或 ReviewOrchestrator 月复盘链路）对每个上线策略
    调 evaluate(RetirementEvalInput(...))；任一判据触发 → 评估报告经 ReportPublisher
    TRADING_REVIEW 源归档，人工裁定后才允许动策略状态（本模块无策略状态写接口——
    评审制铁律）。
    """

    def __init__(
        self,
        publisher: ReportPublisher | None = None,
        registry_path: Path | None = None,
        underperformance_window: int = 20,
        sharpe_window: int = 60,
    ) -> None:
        if underperformance_window < 2 or sharpe_window < 2:
            raise InvalidRetirementInputError(
                f"滚动窗口须 >= 2: {underperformance_window}, {sharpe_window}"
            )
        self._publisher = publisher
        self._thresholds = _load_retirement_thresholds(registry_path)
        self._underperformance_window = underperformance_window
        self._sharpe_window = sharpe_window

    @property
    def thresholds(self) -> dict[str, float]:
        return dict(self._thresholds)

    # ── 判据检查（每判据一个 helper，NO-HIGH-COMPLEXITY 合规）──

    def _check_underperformance(
        self,
        live: list[float],
        bench: list[float],
        triggered: list[TriggeredCriterion],
        metrics: dict[str, float],
    ) -> None:
        """①A 滚动跑输判据（窗口内累计收益差，THD-RETIRE-001）。"""
        w = self._underperformance_window
        if len(live) < w or len(bench) < w:
            return
        cum_live = math.prod(1.0 + r for r in live[-w:]) - 1.0
        cum_bench = math.prod(1.0 + r for r in bench[-w:]) - 1.0
        gap = cum_live - cum_bench
        metrics["rolling_underperformance_gap"] = gap
        if gap < -self._thresholds["underperformance_gap"]:
            triggered.append(
                TriggeredCriterion(
                    criterion=RetirementCriterion.ROLLING_UNDERPERFORMANCE,
                    metric_value=gap,
                    threshold=-self._thresholds["underperformance_gap"],
                    detail=f"滚动 {w} 日实盘 {cum_live:.2%} vs 基准 {cum_bench:.2%}，跑输 {-gap:.2%}",
                )
            )

    def _check_sharpe(
        self,
        live: list[float],
        triggered: list[TriggeredCriterion],
        metrics: dict[str, float],
    ) -> None:
        """①B 滚动 Sharpe 判据（THD-RETIRE-002）。"""
        sw = self._sharpe_window
        if len(live) < sw:
            return
        sharpe = _rolling_sharpe(live[-sw:])
        metrics["rolling_sharpe"] = sharpe
        if sharpe < self._thresholds["sharpe_floor"]:
            triggered.append(
                TriggeredCriterion(
                    criterion=RetirementCriterion.ROLLING_SHARPE_NEGATIVE,
                    metric_value=sharpe,
                    threshold=self._thresholds["sharpe_floor"],
                    detail=f"滚动 {sw} 日 Sharpe={sharpe:.3f} < {self._thresholds['sharpe_floor']}",
                )
            )

    def _check_drawdown_drift(
        self,
        live: list[float],
        historical_max_drawdown: float | None,
        triggered: list[TriggeredCriterion],
        metrics: dict[str, float],
    ) -> None:
        """①C 回撤漂移判据（当前回撤 > 倍数×历史最大回撤，THD-RETIRE-003）。"""
        if historical_max_drawdown is None or historical_max_drawdown <= 0:
            return
        current_dd = _current_drawdown(live)
        metrics["current_drawdown"] = current_dd
        metrics["historical_max_drawdown"] = historical_max_drawdown
        limit = self._thresholds["drawdown_drift_multiplier"] * historical_max_drawdown
        if current_dd > limit:
            triggered.append(
                TriggeredCriterion(
                    criterion=RetirementCriterion.DRAWDOWN_DRIFT,
                    metric_value=current_dd,
                    threshold=limit,
                    detail=(
                        f"当前回撤 {current_dd:.2%} > "
                        f"{self._thresholds['drawdown_drift_multiplier']}×历史最大回撤 "
                        f"{historical_max_drawdown:.2%}"
                    ),
                )
            )

    def _check_deviation(
        self,
        backtest_live_deviation: float | None,
        triggered: list[TriggeredCriterion],
        metrics: dict[str, float],
    ) -> None:
        """①D 回测-实盘偏离判据（偏离值由 MOD-RK-23 供给不重算，THD-DEVIATION-002）。"""
        if backtest_live_deviation is None:
            return
        metrics["backtest_live_deviation"] = backtest_live_deviation
        if backtest_live_deviation > self._thresholds["deviation_retire"]:
            triggered.append(
                TriggeredCriterion(
                    criterion=RetirementCriterion.BACKTEST_LIVE_DEVIATION,
                    metric_value=backtest_live_deviation,
                    threshold=self._thresholds["deviation_retire"],
                    detail=(
                        f"回测-实盘偏离 {backtest_live_deviation:.2%} > "
                        f"{self._thresholds['deviation_retire']:.0%}"
                    ),
                )
            )

    @staticmethod
    def _check_alpha_falsified(
        inp: RetirementEvalInput,
        triggered: list[TriggeredCriterion],
    ) -> None:
        """②逻辑失效判据（外部供给：因子衰减退役联动/人工判定）。"""
        if inp.alpha_falsified:
            triggered.append(
                TriggeredCriterion(
                    criterion=RetirementCriterion.ALPHA_FALSIFIED,
                    metric_value=None,
                    threshold=None,
                    detail="alpha 信号被证伪: " + (", ".join(inp.falsified_factors) or "人工判定"),
                )
            )

    # ── 主入口 ──

    def evaluate(self, inp: RetirementEvalInput) -> RetirementEvaluationReport | None:
        """评估单策略退役判据；任一触发 → 报告（归档）→ 返回；全未触发 → None。"""
        evaluated_at = inp.now or datetime.now(timezone.utc)
        live = _as_float_list(inp.live_returns, name="live_returns")
        bench = _as_float_list(inp.benchmark_returns, name="benchmark_returns")
        if not live or not bench:
            raise InvalidRetirementInputError("live/benchmark 收益序列不可为空")
        if inp.backtest_live_deviation is not None and inp.backtest_live_deviation < 0.0:
            raise InvalidRetirementInputError(
                f"backtest_live_deviation 须 >= 0: {inp.backtest_live_deviation}"
            )

        triggered: list[TriggeredCriterion] = []
        metrics: dict[str, float] = {}
        self._check_underperformance(live, bench, triggered, metrics)
        self._check_sharpe(live, triggered, metrics)
        self._check_drawdown_drift(live, inp.historical_max_drawdown, triggered, metrics)
        self._check_deviation(inp.backtest_live_deviation, triggered, metrics)
        self._check_alpha_falsified(inp, triggered)

        if not triggered:
            logger.info("退役评估 %s: 无判据触发", inp.strategy_id)
            return None

        report = RetirementEvaluationReport(
            report_id=f"RETIRE-{inp.strategy_id}-{evaluated_at:%Y%m%d}-{uuid.uuid4().hex[:8]}",
            strategy_id=inp.strategy_id,
            evaluated_at=evaluated_at,
            triggered=tuple(triggered),
            metrics=metrics,
            falsified_factors=tuple(inp.falsified_factors),
        )
        logger.warning(
            "退役评估触发 %s: %d 条判据 → 评审报告 %s（人工裁定，不自动退役）",
            inp.strategy_id,
            len(triggered),
            report.report_id,
        )
        if inp.publish and self._publisher is not None:
            self._publisher.publish(
                report_id=report.report_id,
                source=ReportSource.TRADING_REVIEW,
                report_type="strategy_retirement_evaluation",
                content={
                    "strategy_id": report.strategy_id,
                    "evaluated_at": report.evaluated_at.isoformat(),
                    "triggered": [
                        {
                            "criterion": t.criterion.value,
                            "metric_value": t.metric_value,
                            "threshold": t.threshold,
                            "detail": t.detail,
                        }
                        for t in report.triggered
                    ],
                    "metrics": report.metrics,
                    "falsified_factors": list(report.falsified_factors),
                    "recommendation": report.recommendation,
                    "status": report.status,
                },
            )
        return report


__all__: Final = [
    "InvalidRetirementInputError",
    "RetirementConfigError",
    "RetirementCriterion",
    "RetirementEvalInput",
    "RetirementEvaluationReport",
    "StrategyRetirementEvaluator",
    "TriggeredCriterion",
]
