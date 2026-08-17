# [BLUEPRINT] MOD-RK-23 | docs/03_modules/_domain_risk/strategy_deviation_monitor/blueprint.md | §
# [MODULE] zephyr.risk.core.strategy_deviation_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.io.paths; docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml (SSoT，阈值 fail-closed 加载)
# [CONSUMERS] MOD-RPT-009(ReviewOrchestrator,周复盘偏离段); 调用方(日终偏离评估)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 阈值唯一真源=alert_threshold_registry(THD-DEVIATION-001/002/003,fail-closed);偏离口径=累计收益相对偏差+日收益相关双口径;事件去抖=仅 action 级别变化时发射;本模块永不直接改策略状态
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDeviationInputError;DeviationConfigError
# [TESTS] tests/risk/core/test_strategy_deviation_monitor.py
# [A_module] module_id=MOD-RK-23 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

D_RISK — Strategy Deviation Monitor (MOD-RK-23)

策略偏离监控器——实盘 vs 回测净值偏离度持续度量（55 号 G26 §3.4 决策落地）。

组装缺口（非从零实现）：decision_gate.monitor_backtest_live_deviation 只覆盖
Sharpe 单口径且为无编排的被动函数；PLV 规约覆盖上线后短期验证；position_drift_monitor
覆盖仓位内部漂移。「实盘 vs 回测净值偏离」主线无持续度量——本模块闭合该缺口：
每日收盘后计算两口径偏差（累计收益相对偏差 / 日收益 Pearson 相关），
阈值复用 decision_gate 同体系（>30% 告警 / >50% 退役评估），
阈值真源 = alert_threshold_registry.yaml（THD-DEVIATION-001/002/003，fail-closed）。

核心公式 (blueprint §3):
  cum_return = ∏(1+r_daily) - 1（尾部对齐后的日收益序列）
  cum_relative_deviation = |cum_live - cum_backtest| / |cum_backtest|
    （|cum_backtest| < eps 时：cum_live 亦≈0 → 0.0；否则 → inf 必然触发 RETIRE）
  daily_return_correlation = Pearson(live_daily, backtest_daily)（零方差 → None）
  action: deviation > retire(0.50) → RETIRE; > warn(0.30) → WARN; else OK
  correlation_below_floor（默认下限 0.5，pending_adjudication）只标注不升级 action
    ——周报「偏离与告警事件」段消费（55 号 §3.6）

事件去抖不变量（同 drawdown_tracker 模式）:
  每个 strategy 仅当 action 级别发生变化时发射 DeviationAlertedEvent（升降级均发射）。

基准供给（50 号桥，55 号 §3.7）:
  load_backtest_returns_from_experiment(run_id) 经 experiment_tracking.query.get_run
  读 nav_curve_experiment.csv artifact → 日收益序列；失败降级 None 不抛（监控不阻断主链路）。

SSoT: depgraph MOD-RK-23 | blueprint.md §3 核心规则 | 55 号 §3.4
"""

from __future__ import annotations

import csv
import logging
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Final, Sequence

import yaml

from zephyr.shared.alerts.threshold_loader import load_alert_thresholds
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class InvalidDeviationInputError(ZephyrBaseError):
    """偏离度量输入非法（非数值/NaN/空序列）。"""

    error_code = "ZA-RK-0022"


class DeviationConfigError(ZephyrBaseError):
    """阈值注册表缺失/畸形（fail-closed：禁止码内第二真源兜底）。"""

    error_code = "ZA-RK-0023"


class DeviationAction(str, Enum):
    """偏离动作分级（语义对齐 decision_gate.monitor_backtest_live_deviation）。"""

    OK = "ok"
    WARN = "warn"
    RETIRE = "retire"


#: 阈值注册表相对路径（真源唯一：55 号 §3.3 决策）
ALERT_THRESHOLD_REGISTRY_PATH: Final[Path] = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "alert_threshold_registry.yaml"
)

_EPS = 1e-12


@dataclass(frozen=True)
class DeviationVerdict:
    """单次偏离度量结论（不可变快照，供日报/周报聚合）。"""

    strategy_id: str
    evaluated_at: datetime
    sample_size: int
    sufficient_data: bool
    cum_return_live: float | None
    cum_return_backtest: float | None
    cum_relative_deviation: float | None
    daily_return_correlation: float | None
    correlation_below_floor: bool
    action: DeviationAction
    thresholds: dict[str, float]
    note: str = ""


@dataclass(frozen=True)
class DeviationAlertedEvent:
    """偏离级别变化事件（仅级别变化时发射——事件去抖不变量）。"""

    strategy_id: str
    previous_action: DeviationAction
    new_action: DeviationAction
    verdict: DeviationVerdict
    emitted_at: datetime


def _load_deviation_thresholds(registry_path: Path | None = None) -> dict[str, float]:
    """从告警阈值注册表加载偏离三阈值（fail-closed：缺文件/缺条目/非数值直接报错）。"""
    try:
        out = load_alert_thresholds(
            {"THD-DEVIATION-001": "warn", "THD-DEVIATION-002": "retire", "THD-DEVIATION-003": "correlation_floor"},
            registry_path=registry_path,
        )
    except Exception as exc:
        details = {"error": str(exc), "path": str(registry_path or ALERT_THRESHOLD_REGISTRY_PATH)}
        if hasattr(exc, "details") and isinstance(exc.details, dict):
            details.update(exc.details)
        raise DeviationConfigError(
            "阈值注册表加载失败",
            details=details,
        ) from exc
    if not (0 < out["warn"] and out["warn"] < out["retire"]):
        raise DeviationConfigError(
            f"偏离阈值须满足 0 < warn < retire: {out['warn']}, {out['retire']}"
        )
    return out


def _as_float_list(values: Sequence[float], *, name: str) -> list[float]:
    """输入校验：数值序列 → list[float]；NaN/非数值 fail-closed。"""
    if values is None:
        raise InvalidDeviationInputError(f"{name} 不能为 None")
    out: list[float] = []
    for i, v in enumerate(values):
        try:
            f = float(v)
        except (TypeError, ValueError) as exc:
            raise InvalidDeviationInputError(f"{name}[{i}] 非数值: {v!r}") from exc
        if math.isnan(f) or math.isinf(f):
            raise InvalidDeviationInputError(f"{name}[{i}] 非法数值: {f}")
        out.append(f)
    return out


def _cum_return(daily_returns: list[float]) -> float:
    nav = 1.0
    for r in daily_returns:
        nav *= 1.0 + r
    return nav - 1.0


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    """Pearson 相关；任一序列零方差 → None（无定义）。"""
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    if var_x < _EPS or var_y < _EPS:
        return None
    return cov / math.sqrt(var_x * var_y)


class StrategyDeviationMonitor:
    """策略偏离监控器（实盘 vs 回测，日频事后度量，55 号 §3.4）。

    用法：每日收盘后由调用方对每个上线策略调 evaluate()；
    级别变化经 on_deviation_alerted 订阅消费（告警路由由调用方/orchestrator 接线）。
    """

    def __init__(
        self,
        registry_path: Path | None = None,
        min_samples: int = 5,
    ) -> None:
        if min_samples < 2:
            raise InvalidDeviationInputError(f"min_samples 须 >= 2: {min_samples}")
        self._thresholds = _load_deviation_thresholds(registry_path)
        self._min_samples = min_samples
        self._last_action: dict[str, DeviationAction] = {}
        self._latest_verdicts: dict[str, DeviationVerdict] = {}
        self._listeners: list[Callable[[DeviationAlertedEvent], None]] = []

    @property
    def thresholds(self) -> dict[str, float]:
        return dict(self._thresholds)

    def on_deviation_alerted(
        self, listener: Callable[[DeviationAlertedEvent], None]
    ) -> None:
        """订阅偏离级别变化事件。"""
        self._listeners.append(listener)

    def get_latest_verdicts(self) -> dict[str, DeviationVerdict]:
        """各策略最新 verdict 快照（周复盘「偏离与告警事件」段数据源）。"""
        return dict(self._latest_verdicts)

    def evaluate(
        self,
        strategy_id: str,
        live_returns: Sequence[float],
        backtest_returns: Sequence[float],
        now: datetime | None = None,
    ) -> DeviationVerdict:
        """度量单策略实盘 vs 回测偏离（尾部对齐，双口径）。

        Args:
            strategy_id: 策略 ID（STR-XXX-NNN）
            live_returns: 实盘日收益序列（小数，非百分比）
            backtest_returns: 同期回测日收益序列（experiment_tracking 基准供给）
            now: 评估时刻（默认 datetime.now(timezone.utc)）

        Returns:
            DeviationVerdict；样本不足（< min_samples）时 sufficient_data=False 且 action=OK
        """
        evaluated_at = now or datetime.now(timezone.utc)
        live = _as_float_list(live_returns, name="live_returns")
        backtest = _as_float_list(backtest_returns, name="backtest_returns")
        n = min(len(live), len(backtest))
        if n == 0:
            raise InvalidDeviationInputError("live/backtest 收益序列不可为空")
        live = live[-n:]
        backtest = backtest[-n:]

        if n < self._min_samples:
            verdict = DeviationVerdict(
                strategy_id=strategy_id,
                evaluated_at=evaluated_at,
                sample_size=n,
                sufficient_data=False,
                cum_return_live=None,
                cum_return_backtest=None,
                cum_relative_deviation=None,
                daily_return_correlation=None,
                correlation_below_floor=False,
                action=DeviationAction.OK,
                thresholds=dict(self._thresholds),
                note=f"样本不足（{n} < {self._min_samples}），仅登记不判定",
            )
            self._latest_verdicts[strategy_id] = verdict
            return verdict

        cum_live = _cum_return(live)
        cum_bt = _cum_return(backtest)
        if abs(cum_bt) < _EPS:
            deviation = 0.0 if abs(cum_live) < _EPS else math.inf
        else:
            deviation = abs(cum_live - cum_bt) / abs(cum_bt)
        correlation = _pearson(live, backtest)
        corr_below_floor = (
            correlation is not None and correlation < self._thresholds["correlation_floor"]
        )

        if deviation > self._thresholds["retire"]:
            action = DeviationAction.RETIRE
        elif deviation > self._thresholds["warn"]:
            action = DeviationAction.WARN
        else:
            action = DeviationAction.OK

        verdict = DeviationVerdict(
            strategy_id=strategy_id,
            evaluated_at=evaluated_at,
            sample_size=n,
            sufficient_data=True,
            cum_return_live=cum_live,
            cum_return_backtest=cum_bt,
            cum_relative_deviation=deviation,
            daily_return_correlation=correlation,
            correlation_below_floor=corr_below_floor,
            action=action,
            thresholds=dict(self._thresholds),
        )
        self._latest_verdicts[strategy_id] = verdict
        self._emit_if_level_changed(verdict, evaluated_at)
        logger.info(
            "偏离度量完成 %s: deviation=%.4f corr=%s action=%s",
            strategy_id,
            deviation,
            f"{correlation:.4f}" if correlation is not None else "NA",
            action.value,
        )
        return verdict

    def _emit_if_level_changed(
        self, verdict: DeviationVerdict, emitted_at: datetime
    ) -> None:
        previous = self._last_action.get(verdict.strategy_id)
        if previous is verdict.action:
            return
        self._last_action[verdict.strategy_id] = verdict.action
        if previous is None and verdict.action is DeviationAction.OK:
            return  # 首次评估即 OK 不发射（无事件）
        event = DeviationAlertedEvent(
            strategy_id=verdict.strategy_id,
            previous_action=previous or DeviationAction.OK,
            new_action=verdict.action,
            verdict=verdict,
            emitted_at=emitted_at,
        )
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:  # noqa: BLE001 — 监听器异常不阻断监控主链路
                logger.exception("偏离事件监听器异常（已隔离）: %s", verdict.strategy_id)

    @staticmethod
    def load_backtest_returns_from_experiment(
        run_id: str,
        artifact_suffix: str = "nav_curve_experiment.csv",
    ) -> list[float] | None:
        """从 experiment_tracking 历史 run 读回测净值 → 日收益序列（50 号基准供给桥）。

        失败一律降级返回 None（监控链路永不阻断业务）；lazy import 避免
        risk 域对 experiment_tracking 的硬依赖。
        """
        try:
            from zephyr.experiment_tracking.query import get_run
        except ImportError:
            logger.warning("experiment_tracking 不可用，基准供给降级 None")
            return None
        try:
            detail = get_run(run_id)
            if detail is None:
                logger.warning("run 不存在: %s", run_id)
                return None
            csv_path = next(
                (p for name, p in detail.artifact_paths.items() if name.endswith(artifact_suffix)),
                None,
            )
            if csv_path is None:
                logger.warning("run %s 无 %s artifact", run_id, artifact_suffix)
                return None
            navs: list[float] = []
            with open(csv_path, newline="", encoding="utf-8") as f:
                for row in csv.reader(f):
                    if not row or row[-1] == "nav":
                        continue  # 表头/坏行跳过
                    try:
                        navs.append(float(row[-1]))
                    except ValueError:
                        continue
            returns = [
                navs[i] / navs[i - 1] - 1.0
                for i in range(1, len(navs))
                if abs(navs[i - 1]) > _EPS
            ]
            return returns or None
        except Exception:  # noqa: BLE001 — 基准供给失败不阻断监控
            logger.exception("读取回测基准失败（降级 None）: %s", run_id)
            return None


__all__: Final = [
    "ALERT_THRESHOLD_REGISTRY_PATH",
    "DeviationAction",
    "DeviationAlertedEvent",
    "DeviationConfigError",
    "DeviationVerdict",
    "InvalidDeviationInputError",
    "StrategyDeviationMonitor",
]
