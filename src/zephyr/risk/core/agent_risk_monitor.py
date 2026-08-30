# [BLUEPRINT] MOD-RK-22 | docs/03_modules/MOD-RK-22/
# [MODULE] zephyr.risk.core.agent_risk_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.risk_data_pipeline; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RK-24(Risk Veto Engine,监控等级输入) ; MOD-L04-001(DefaultRiskManagerOrchestrator)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] risk等级由触发指标唯一决定(CRITICAL>WARNING>NORMAL); 比率类指标有样本地板(min_decisions_for_rates以下不评估); CRITICAL→suspend_new_orders/WARNING→throttle/NORMAL→none; 非法活动输入(负数/拒>提/置信度越界/窗口倒置)→InvalidAgentActivityError(Fail-Closed); 与MOD-RK-14分工: RK-14管行为越界评分(涌现/轨迹/指纹), 本模块管交易活动风险(下单/拒单/撤单/置信度/数据质量)
# [MODIFY-GUARD] docs/03_modules/MOD-RK-22/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAgentActivityError
# [TESTS] tests/risk/core/test_agent_risk_monitor.py
# [A_module] module_id=MOD-RK-22 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Agent Risk Monitor — agent 交易行为风险监控器 (MOD-RK-22)

监控 AI 交易 agent 的活动窗口风险，消费 MOD-RK-25 统一风控快照 (RiskSnapshot)：
  - order_burst      : 窗口下单数超阈值（约束三：miniQMT 10笔/秒硬上限的前置哨兵）
  - reject_rate      : 拒单率超阈（券商端已在拦，agent 决策与风控脱节信号）
  - cancel_rate      : 撤单率超阈（程序化交易异常行为监控，L-002 映射）
  - low_confidence   : 平均置信度低于下限（约束六：AI置信度低→降级"仅建议"）
  - snapshot_degraded: 数据底座降级（§6：数据质量优先，脏数据比晚数据更危险）
  - limit_proximity  : 持仓权重逼近单仓硬限（warning_ratio 提前告警）

判定核心为纯函数 evaluate_agent_risk（同输入必同输出，可单测）；
AgentRiskMonitor 为薄封装（配置持有 + 最近一次报告留痕）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: activity 参数
#   fields: 参数 activity，类型注解 AgentActivityWindow
#   code: agent_risk_monitor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: snapshot 参数
#   fields: 参数 snapshot，类型注解 RiskSnapshot
#   code: agent_risk_monitor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: thresholds 参数
#   fields: 参数 thresholds，类型注解 AgentRiskThresholds
#   code: agent_risk_monitor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: evaluated_at 参数
#   fields: 参数 evaluated_at（无注解）
#   code: agent_risk_monitor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① evaluate_agent_risk
#   name_en: evaluate_agent_risk
#   intro: 评估 agent 交易活动风险（纯函数）。
#   desc: 评估 agent 交易活动风险（纯函数）。 等级由触发指标唯一决定：任一 CRITICAL → CRITICAL；否则任一 WARNING → WARNING。 比率类指标仅在…；源码 L200-L314
#   inputs: activity snapshot thresholds evaluated_at
#   outputs: AgentRiskReport
# - id: A2
#   name_zh: ② AgentRiskMonitor
#   name_en: AgentRiskMonitor
#   intro: agent 风险监控器（薄封装：阈值持有 + 最近报告留痕）。
#   desc: agent 风险监控器（薄封装：阈值持有 + 最近报告留痕）。；公共方法（定义序）: assess, last_report；源码 L317-L345
#   inputs: thresholds
#   outputs: 返回值
#   （注：A2 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: AgentRiskReport
#   name_en: AgentRiskReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-RK-24(Risk Veto Engine,监控等级输入) ; MOD-L04-001(DefaultRiskManagerOrchestrator)
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
from datetime import UTC, datetime
from enum import Enum
from typing import Final

from zephyr.risk.core.risk_data_pipeline import RiskSnapshot
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AgentActivityWindow",
    "AgentRiskIndicator",
    "AgentRiskLevel",
    "AgentRiskMonitor",
    "AgentRiskReport",
    "AgentRiskThresholds",
    "InvalidAgentActivityError",
    "evaluate_agent_risk",
]


class InvalidAgentActivityError(ZephyrBaseError):
    """agent 活动窗口输入非法（Fail-Closed：宁可报错也不评估脏输入）。"""

    error_code = "ZA-RK-0070"


class AgentRiskLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class AgentActivityWindow:
    """agent 交易活动窗口（由调用方从执行/审计链路聚合注入）。"""

    window_start: datetime
    window_end: datetime
    orders_submitted: int
    orders_rejected: int
    orders_cancelled: int
    decisions_made: int
    avg_confidence: float | None = None


@dataclass(frozen=True)
class AgentRiskThresholds:
    """监控阈值配置（C 类可调参数）。"""

    max_orders_per_window: int = 100
    max_reject_rate: float = 0.2
    max_cancel_rate: float = 0.5
    min_confidence: float = 0.5
    min_decisions_for_rates: int = 10
    limit_warning_ratio: float = 0.8


@dataclass(frozen=True)
class AgentRiskIndicator:
    """单条触发指标（结构化留痕）。"""

    indicator_id: str
    severity: str  # "WARNING" | "CRITICAL"
    message: str
    actual: float
    limit: float


@dataclass(frozen=True)
class AgentRiskReport:
    """agent 风险监控报告（frozen；risk_veto_engine / 编排层消费）。"""

    level: AgentRiskLevel
    recommended_action: str  # "none" | "throttle" | "suspend_new_orders"
    indicators: tuple[AgentRiskIndicator, ...]
    snapshot_id: str
    evaluated_at: datetime


def _validate_activity(activity: AgentActivityWindow) -> None:
    counts = {
        "orders_submitted": activity.orders_submitted,
        "orders_rejected": activity.orders_rejected,
        "orders_cancelled": activity.orders_cancelled,
        "decisions_made": activity.decisions_made,
    }
    for field_name, value in counts.items():
        if value < 0:
            raise InvalidAgentActivityError(
                f"活动窗口计数非法: {field_name}={value}（不允许负数）",
                details={"field": field_name, "value": value},
            )
    if activity.orders_rejected > activity.orders_submitted:
        raise InvalidAgentActivityError(
            "拒单数超过下单数（账本不一致）: "
            f"rejected={activity.orders_rejected} > submitted={activity.orders_submitted}",
            details={
                "orders_rejected": activity.orders_rejected,
                "orders_submitted": activity.orders_submitted,
            },
        )
    if activity.avg_confidence is not None and not 0.0 <= activity.avg_confidence <= 1.0:
        raise InvalidAgentActivityError(
            f"平均置信度越界: {activity.avg_confidence}（合法域 [0,1]）",
            details={"avg_confidence": activity.avg_confidence},
        )
    if activity.window_end < activity.window_start:
        raise InvalidAgentActivityError(
            f"活动窗口时间倒置: start={activity.window_start.isoformat()} > end={activity.window_end.isoformat()}",
            details={},
        )


def evaluate_agent_risk(
    activity: AgentActivityWindow,
    snapshot: RiskSnapshot,
    thresholds: AgentRiskThresholds,
    *,
    evaluated_at: datetime | None = None,
) -> AgentRiskReport:
    """评估 agent 交易活动风险（纯函数）。

    等级由触发指标唯一决定：任一 CRITICAL → CRITICAL；否则任一 WARNING → WARNING。
    比率类指标仅在 orders_submitted >= min_decisions_for_rates 时评估（小样本地板）。
    """
    _validate_activity(activity)
    indicators: list[AgentRiskIndicator] = []

    # ① 下单爆发
    if activity.orders_submitted > thresholds.max_orders_per_window:
        indicators.append(
            AgentRiskIndicator(
                indicator_id="order_burst",
                severity="CRITICAL",
                message=(f"窗口下单数超限: {activity.orders_submitted} > {thresholds.max_orders_per_window}"),
                actual=float(activity.orders_submitted),
                limit=float(thresholds.max_orders_per_window),
            )
        )

    # ②③ 拒单率/撤单率（小样本地板守卫）
    if activity.orders_submitted >= thresholds.min_decisions_for_rates:
        reject_rate = activity.orders_rejected / activity.orders_submitted
        if reject_rate > thresholds.max_reject_rate:
            severity = "CRITICAL" if reject_rate > thresholds.max_reject_rate * 2 else "WARNING"
            indicators.append(
                AgentRiskIndicator(
                    indicator_id="reject_rate",
                    severity=severity,
                    message=f"拒单率超阈: {reject_rate:.2%} > {thresholds.max_reject_rate:.2%}",
                    actual=reject_rate,
                    limit=thresholds.max_reject_rate,
                )
            )
        cancel_rate = activity.orders_cancelled / activity.orders_submitted
        if cancel_rate > thresholds.max_cancel_rate:
            indicators.append(
                AgentRiskIndicator(
                    indicator_id="cancel_rate",
                    severity="WARNING",
                    message=f"撤单率超阈: {cancel_rate:.2%} > {thresholds.max_cancel_rate:.2%}",
                    actual=cancel_rate,
                    limit=thresholds.max_cancel_rate,
                )
            )

    # ④ 置信度下限（None=无置信度真源，跳过不臆造）
    if activity.avg_confidence is not None and activity.avg_confidence < thresholds.min_confidence:
        indicators.append(
            AgentRiskIndicator(
                indicator_id="low_confidence",
                severity="WARNING",
                message=(
                    f"平均置信度低于下限: {activity.avg_confidence:.2f} < "
                    f"{thresholds.min_confidence:.2f}（约束六→降级仅建议）"
                ),
                actual=activity.avg_confidence,
                limit=thresholds.min_confidence,
            )
        )

    # ⑤ 数据底座降级
    if snapshot.degraded:
        indicators.append(
            AgentRiskIndicator(
                indicator_id="snapshot_degraded",
                severity="WARNING",
                message="风控快照降级: " + ";".join(snapshot.data_warnings),
                actual=1.0,
                limit=0.0,
            )
        )

    # ⑥ 限额逼近（limits 缺失时不臆测）
    if snapshot.limits is not None:
        max_single = snapshot.limits.max_single_position
        warn_line = max_single * thresholds.limit_warning_ratio
        for view in snapshot.positions:
            if view.weight is not None and view.weight >= warn_line:
                indicators.append(
                    AgentRiskIndicator(
                        indicator_id="limit_proximity",
                        severity="WARNING",
                        message=(f"持仓逼近单仓硬限: {view.symbol} weight={view.weight:.4f} warn_line={warn_line:.4f}"),
                        actual=view.weight,
                        limit=max_single,
                    )
                )

    has_critical = any(i.severity == "CRITICAL" for i in indicators)
    has_warning = any(i.severity == "WARNING" for i in indicators)
    if has_critical:
        level = AgentRiskLevel.CRITICAL
        action = "suspend_new_orders"
    elif has_warning:
        level = AgentRiskLevel.WARNING
        action = "throttle"
    else:
        level = AgentRiskLevel.NORMAL
        action = "none"

    return AgentRiskReport(
        level=level,
        recommended_action=action,
        indicators=tuple(indicators),
        snapshot_id=snapshot.snapshot_id,
        evaluated_at=evaluated_at or datetime.now(tz=UTC),
    )


class AgentRiskMonitor:
    """agent 风险监控器（薄封装：阈值持有 + 最近报告留痕）。"""

    def __init__(self, thresholds: AgentRiskThresholds | None = None) -> None:
        self._thresholds = thresholds or AgentRiskThresholds()
        self._last_report: AgentRiskReport | None = None

    def assess(
        self,
        activity: AgentActivityWindow,
        snapshot: RiskSnapshot,
        *,
        evaluated_at: datetime | None = None,
    ) -> AgentRiskReport:
        report = evaluate_agent_risk(activity, snapshot, self._thresholds, evaluated_at=evaluated_at)
        if report.level is not AgentRiskLevel.NORMAL:
            _logger.warning(
                "AGENT_RISK_%s action=%s indicators=%s snapshot=%s",
                report.level.value,
                report.recommended_action,
                [i.indicator_id for i in report.indicators],
                report.snapshot_id,
            )
        self._last_report = report
        return report

    @property
    def last_report(self) -> AgentRiskReport | None:
        return self._last_report
