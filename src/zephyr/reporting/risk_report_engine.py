# [BLUEPRINT] MOD-RPT-008 | docs/03_modules/_domain_reporting/risk_report_engine/blueprint.md
# [MODULE] zephyr.reporting.risk_report_engine
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.contracts.risk.risk_dashboard_snapshot; zephyr.shared.contracts.risk.risk_metrics; zephyr.shared.foundation.errors; zephyr.shared.alerts.threshold_loader
# [CONSUMERS] zephyr.reporting
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] RiskLevel 4档判定(overall_risk_score 阈值); 4类报告frozen不可变; 事件快报仅active_alerts非空时生成; 周度趋势前后半段比对; 月度分布按RiskLevel统计天数; 分级/趋势阈值真源=alert_threshold_registry(THD-REPORT-001~004,fail-closed)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRiskReportInputError(ZA-RPT-0007)
# [TESTS] tests/reporting/test_risk_report_engine.py
# [A_module] module_id=MOD-RPT-008 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_REPORTING — Risk Report Engine (风险报告引擎)

消费 D-RISK 诊断结果(RiskDashboardSnapshot + RiskMetricsReport), 生成 4 类风险报告:
  - DailyRiskSummary: 日度风险摘要 (VaR/CVaR/回撤/杠杆/集中度/告警)
  - EventRiskFlash: 事件风险快报 (告警触发→影响评估+处置建议)
  - WeeklyRiskDeep: 周度风险深度 (日度聚合+趋势判定)
  - MonthlyRiskGovernance: 月度风险治理 (分布统计+high/critical天数)

属 A 类基础设施(确定性报告生成), 纯消费层不发布事件(D-RPT-D01)。
不做风险诊断, 只负责"消费诊断结果→生成报告"。

设计真源: D:/临时工作区/依赖图/10-D-REPORTING-报告域.md §1.2 D-REPORTING-08, §5.1
蓝图: docs/03_modules/_domain_reporting/risk_report_engine/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 风险仪表盘快照 RiskDashboardSnapshot（CTR-P1-008）
#   fields: overall_risk_score / gross_leverage / top_position_concentration / sector_concentrations / active_alerts
#   code: snapshot（generate_daily/generate_event_flash 参数）
# - id: I2
#   name: 风险指标报告 RiskMetricsReport（CTR-P1-011）
#   fields: var_1d_95/99 / cvar_1d_95/99 / current_drawdown / max_drawdown / sharpe_ratio / sortino_ratio / beta / volatility_1d / as_of_date
#   code: metrics（generate_daily 参数）
# - id: I3
#   name: 日度风险摘要列表
#   fields: daily_summaries（≥1 条 DailyRiskSummary，按 report_date 排序聚合）
#   code: generate_weekly/generate_monthly 参数 daily_summaries
# 层: 算法
# - id: A1
#   name_zh: ① 风险等级 4 档判定
#   name_en: _classify_risk_level
#   intro: 把 overall_risk_score 按 0.3/0.6/0.8 三档阈值映射成 LOW/MEDIUM/HIGH/CRITICAL
#   desc: score<0.3→LOW；<0.6→MEDIUM；<0.8→HIGH；≥0.8→CRITICAL
#   inputs: I1
#   outputs: RiskLevel
#   invariant: RiskLevel 4档判定(overall_risk_score 阈值)
# - id: A2
#   name_zh: ② 日度风险摘要生成
#   name_en: RiskReportEngine.generate_daily
#   intro: 校验两输入 portfolio_id 一致后，把风险快照与指标合并成单日风险全貌报告
#   desc: portfolio_id 不一致抛 ZA-RPT-0007；risk_level=A1(snapshot.overall_risk_score)；report_date=as_of_date→YYYY-MM-DD；汇总 VaR/CVaR/回撤/杠杆/集中度/告警
#   inputs: I1 I2 A1
#   outputs: DailyRiskSummary
# - id: A3
#   name_zh: ③ 事件风险快报生成
#   name_en: RiskReportEngine.generate_event_flash/_assess_impact/_recommendations_for_level
#   intro: 有活跃告警时生成即时快报：按等级给影响评估和标准化处置建议
#   desc: active_alerts 为空返回 None；impact=等级严重度(低/中/高/极高)+告警广度(单点/多点)；recommendations 按等级查静态建议表（LOW 监控→CRITICAL 减仓/Kill Switch）
#   inputs: I1 A1
#   outputs: EventRiskFlash（可空）
#   invariant: 事件快报仅active_alerts非空时生成
# - id: A4
#   name_zh: ④ 周度风险深度聚合
#   name_en: RiskReportEngine.generate_weekly/_determine_trend
#   intro: 聚合一周日度报告算 VaR/回撤/评分均值极值，并用前后半段均值差判定趋势
#   desc: 按日期排序；avg/max/min(var_1d_95)；max_drawdown 取 min（负值最负=最差）；趋势=后半段均值-前半段均值，>0.05→RISING，<-0.05→FALLING，否则 STABLE；空列表抛 ZA-RPT-0007
#   inputs: I3
#   outputs: WeeklyRiskDeep
#   invariant: 周度趋势前后半段比对
# - id: A5
#   name_zh: ⑤ 月度风险治理聚合
#   name_en: RiskReportEngine.generate_monthly
#   intro: 聚合一个月日度报告，按风险等级统计天数分布和 high/critical 天数
#   desc: month=首条 report_date[:7]；distribution[level]=天数计数；high_risk_days/critical_risk_days 分别统计；avg_var/max_var_99/avg_dd/avg_score；空列表抛 ZA-RPT-0007
#   inputs: I3
#   outputs: MonthlyRiskGovernance
#   invariant: 月度分布按RiskLevel统计天数
# 层: 输出
# - id: O1
#   name_zh: 日度风险摘要
#   name_en: DailyRiskSummary
#   intro: 单日风险全貌不可变报告（VaR/CVaR/回撤/杠杆/集中度/告警/等级）
#   invariant: 4类报告frozen不可变
#   downstream: zephyr.reporting；并作为周度/月度聚合的输入
# - id: O2
#   name_zh: 事件风险快报
#   name_en: EventRiskFlash
#   intro: 告警触发的即时风险通报（影响评估+处置建议），无告警不生成
#   downstream: zephyr.reporting
# - id: O3
#   name_zh: 周度/月度风险报告
#   name_en: WeeklyRiskDeep/MonthlyRiskGovernance
#   intro: 周度趋势判定与月度风险等级分布治理报告
#   downstream: zephyr.reporting
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I2 --> A2
# I3 --> A4
# I3 --> A5
# A1 --> A2
# A1 --> A3
# A2 --> O1
# A3 --> O2
# A4 --> O3
# A5 --> O3
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from statistics import mean
from typing import Final

from zephyr.shared.alerts.threshold_loader import load_alert_thresholds
from zephyr.shared.contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.shared.contracts.risk.risk_metrics import RiskMetricsReport
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class InvalidRiskReportInputError(ZephyrBaseError):
    """风险报告输入非法——空列表/缺少必要字段/类型不匹配。"""

    error_code = "ZA-RPT-0007"


# ── 枚举 ──


class RiskLevel(str, Enum):
    """风险等级——基于 overall_risk_score 4 档判定。"""

    LOW = "LOW"  # score < 0.3
    MEDIUM = "MEDIUM"  # 0.3 <= score < 0.6
    HIGH = "HIGH"  # 0.6 <= score < 0.8
    CRITICAL = "CRITICAL"  # score >= 0.8


class TrendDirection(str, Enum):
    """趋势方向——周度报告前后半段比对。"""

    RISING = "RISING"  # 后半段风险上升
    FALLING = "FALLING"  # 后半段风险下降
    STABLE = "STABLE"  # 变化不显著


# ── 风险等级判定 ──

#: 报告阈值 ↔ 注册表条目映射（55 号 §3.3 统读：THD-REPORT-001~004）
_REPORT_THRESHOLD_SPEC: Final[dict[str, str]] = {
    "THD-REPORT-001": "risk_score_low",
    "THD-REPORT-002": "risk_score_medium",
    "THD-REPORT-003": "risk_score_high",
    "THD-REPORT-004": "trend_stable",
}


def _load_report_thresholds(registry_path: Path | None = None) -> dict[str, float]:
    """从告警阈值注册表加载报告分级/趋势阈值（fail-closed；registry_path 为测试逃生门）。"""
    return load_alert_thresholds(_REPORT_THRESHOLD_SPEC, registry_path=registry_path)


#: import 期 fail-closed 加载（注册表缺失/畸形 → import 即 raise，禁止码内第二真源兜底）
_REPORT_DEFAULTS: Final[dict[str, float]] = _load_report_thresholds()

_RISK_THRESHOLDS = (
    (_REPORT_DEFAULTS["risk_score_low"], RiskLevel.LOW),
    (_REPORT_DEFAULTS["risk_score_medium"], RiskLevel.MEDIUM),
    (_REPORT_DEFAULTS["risk_score_high"], RiskLevel.HIGH),
    (float("inf"), RiskLevel.CRITICAL),
)

# 趋势判定阈值: 前后半段均值差绝对值 < 此值视为 STABLE（真源=THD-REPORT-004）
_TREND_THRESHOLD = _REPORT_DEFAULTS["trend_stable"]


def _classify_risk_level(
    score: float,
    thresholds: tuple[tuple[float, "RiskLevel"], ...] | None = None,
) -> RiskLevel:
    """根据 overall_risk_score 判定风险等级（thresholds 可注入覆盖，默认注册表加载值）。"""
    for threshold, level in thresholds or _RISK_THRESHOLDS:
        if score < threshold:
            return level
    return RiskLevel.CRITICAL  # 理论不可达, 防御


def _recommendations_for_level(level: RiskLevel) -> list[str]:
    """按风险等级给出标准化处置建议。"""
    return {
        RiskLevel.LOW: [
            "维持当前风控参数, 继续监控",
            "按日度频率审查风险摘要",
        ],
        RiskLevel.MEDIUM: [
            "审查持仓集中度与杠杆水平",
            "确认漂移检测状态, 必要时调整因子暴露",
            "提高风险摘要审查频率至盘中",
        ],
        RiskLevel.HIGH: [
            "立即审查高风险持仓, 考虑减仓",
            "降低整体杠杆至安全区间",
            "激活漂移检测紧急复核流程",
            "通知 Risk Manager 介入审查",
        ],
        RiskLevel.CRITICAL: [
            "立即执行减仓/止损操作",
            "触发 Kill Switch 评估流程",
            "暂停新开仓直至风险降至 HIGH 以下",
            "紧急通知 Trader + Risk Manager + 治理层",
        ],
    }[level]


# ── 报告数据模型（frozen 不可变）──


@dataclass(frozen=True)
class DailyRiskSummary:
    """日度风险摘要——单日风险全貌快照。"""

    report_id: str
    report_date: str  # YYYY-MM-DD
    portfolio_id: str
    risk_level: RiskLevel
    var_1d_95: float
    var_1d_99: float
    cvar_1d_95: float
    cvar_1d_99: float
    current_drawdown: float
    max_drawdown: float
    gross_leverage: float
    top_position_concentration: float
    overall_risk_score: float
    sharpe_ratio: float
    sortino_ratio: float
    beta: float
    volatility_1d: float
    sector_concentrations: dict[str, float]
    active_alerts: list[str]
    alert_count: int
    generated_at: datetime
    schema_version: str = "1.0"


@dataclass(frozen=True)
class EventRiskFlash:
    """事件风险快报——告警触发的即时风险通报。"""

    report_id: str
    event_time: datetime
    portfolio_id: str
    risk_level: RiskLevel
    alert_messages: list[str]
    alert_count: int
    overall_risk_score: float
    impact_assessment: str
    recommendations: list[str]
    schema_version: str = "1.0"


@dataclass(frozen=True)
class WeeklyRiskDeep:
    """周度风险深度——一周风险聚合与趋势。"""

    report_id: str
    week_start: str
    week_end: str
    portfolio_id: str
    daily_count: int
    avg_var_1d_95: float
    max_var_1d_95: float
    min_var_1d_95: float
    avg_drawdown: float
    max_drawdown: float
    avg_risk_score: float
    max_risk_score: float
    trend_direction: TrendDirection
    alert_total: int
    generated_at: datetime
    schema_version: str = "1.0"


@dataclass(frozen=True)
class MonthlyRiskGovernance:
    """月度风险治理——月度风险统计与分布。"""

    report_id: str
    month: str  # YYYY-MM
    portfolio_id: str
    trading_days: int
    avg_var_1d_95: float
    max_var_1d_99: float
    avg_drawdown: float
    max_drawdown: float
    avg_risk_score: float
    risk_score_distribution: dict[str, int]
    total_alerts: int
    high_risk_days: int
    critical_risk_days: int
    generated_at: datetime
    schema_version: str = "1.0"


# ── 风险报告引擎主类 ──


class RiskReportEngine:
    """风险报告引擎——消费 D-RISK 诊断结果, 生成 4 类风险报告。

    纯基础设施, 无外部状态。线程安全（无共享可变状态）。

    Usage:
        engine = RiskReportEngine()
        daily = engine.generate_daily(snapshot, metrics)
        flash = engine.generate_event_flash(snapshot)
        weekly = engine.generate_weekly([daily1, daily2, ...])
        monthly = engine.generate_monthly([daily1, daily2, ...])
    """

    def __init__(
        self,
        *,
        risk_thresholds: tuple[tuple[float, RiskLevel], ...] | None = None,
        trend_threshold: float | None = None,
    ) -> None:
        """初始化风险报告引擎。

        Args:
            risk_thresholds: 风险分级阈值（None=注册表加载值 _RISK_THRESHOLDS；显式传参可覆盖——逃生门）
            trend_threshold: 趋势平稳判定阈值（None=注册表加载值 _TREND_THRESHOLD；显式传参可覆盖）
        """
        self._risk_thresholds = risk_thresholds or _RISK_THRESHOLDS
        self._trend_threshold = trend_threshold if trend_threshold is not None else _TREND_THRESHOLD

    # ── 日度风险摘要 ──

    def generate_daily(
        self,
        snapshot: RiskDashboardSnapshot,
        metrics: RiskMetricsReport,
    ) -> DailyRiskSummary:
        """生成日度风险摘要。

        Args:
            snapshot: 风险仪表盘快照 (CTR-P1-008)。
            metrics: 风险指标报告 (CTR-P1-011)。

        Returns:
            DailyRiskSummary: 日度风险摘要报告。

        Raises:
            InvalidRiskReportInputError: portfolio_id 不一致。
        """
        if snapshot.portfolio_id != metrics.portfolio_id:
            raise InvalidRiskReportInputError(
                f"portfolio_id 不一致: snapshot={snapshot.portfolio_id} metrics={metrics.portfolio_id}",
                details={
                    "snapshot_portfolio": snapshot.portfolio_id,
                    "metrics_portfolio": metrics.portfolio_id,
                },
            )

        risk_level = _classify_risk_level(snapshot.overall_risk_score, self._risk_thresholds)
        report_date = metrics.as_of_date.strftime("%Y-%m-%d")

        report = DailyRiskSummary(
            report_id=f"DRS-{uuid.uuid4().hex[:12]}",
            report_date=report_date,
            portfolio_id=snapshot.portfolio_id,
            risk_level=risk_level,
            var_1d_95=metrics.var_1d_95,
            var_1d_99=metrics.var_1d_99,
            cvar_1d_95=metrics.cvar_1d_95,
            cvar_1d_99=metrics.cvar_1d_99,
            current_drawdown=metrics.current_drawdown,
            max_drawdown=metrics.max_drawdown,
            gross_leverage=snapshot.gross_leverage,
            top_position_concentration=snapshot.top_position_concentration,
            overall_risk_score=snapshot.overall_risk_score,
            sharpe_ratio=metrics.sharpe_ratio,
            sortino_ratio=metrics.sortino_ratio,
            beta=metrics.beta,
            volatility_1d=metrics.volatility_1d,
            sector_concentrations=dict(snapshot.sector_concentrations),
            active_alerts=list(snapshot.active_alerts),
            alert_count=len(snapshot.active_alerts),
            generated_at=datetime.now(UTC),
        )

        _logger.debug(
            "generate_daily: date=%s portfolio=%s level=%s alerts=%d",
            report_date,
            report.portfolio_id,
            risk_level.value,
            report.alert_count,
        )
        return report

    # ── 事件风险快报 ──

    def generate_event_flash(
        self,
        snapshot: RiskDashboardSnapshot,
    ) -> EventRiskFlash | None:
        """生成事件风险快报——仅当 active_alerts 非空时。

        Args:
            snapshot: 风险仪表盘快照 (CTR-P1-008)。

        Returns:
            EventRiskFlash: 事件快报; 无告警时返回 None。
        """
        alerts = list(snapshot.active_alerts)
        if not alerts:
            return None

        risk_level = _classify_risk_level(snapshot.overall_risk_score, self._risk_thresholds)
        impact = self._assess_impact(risk_level, len(alerts))
        recommendations = _recommendations_for_level(risk_level)
        event_time = datetime.now(UTC)

        report = EventRiskFlash(
            report_id=f"ERF-{uuid.uuid4().hex[:12]}",
            event_time=event_time,
            portfolio_id=snapshot.portfolio_id,
            risk_level=risk_level,
            alert_messages=alerts,
            alert_count=len(alerts),
            overall_risk_score=snapshot.overall_risk_score,
            impact_assessment=impact,
            recommendations=recommendations,
        )

        _logger.warning(
            "generate_event_flash: portfolio=%s level=%s alerts=%d impact=%s",
            report.portfolio_id,
            risk_level.value,
            report.alert_count,
            impact,
        )
        return report

    @staticmethod
    def _assess_impact(level: RiskLevel, alert_count: int) -> str:
        """影响评估——基于风险等级+告警数量。"""
        severity = {
            RiskLevel.LOW: "低",
            RiskLevel.MEDIUM: "中",
            RiskLevel.HIGH: "高",
            RiskLevel.CRITICAL: "极高",
        }[level]
        breadth = "单点" if alert_count == 1 else f"多点({alert_count}条)"
        return (
            f"风险等级={level.value}({severity}), 告警{breadth}, overall_risk_score 反映当前组合风险处于{severity}水平"
        )

    # ── 周度风险深度 ──

    def generate_weekly(
        self,
        daily_summaries: list[DailyRiskSummary],
    ) -> WeeklyRiskDeep:
        """生成周度风险深度——聚合一周日度报告。

        Args:
            daily_summaries: 一周的日度摘要列表（≥1 条）。

        Returns:
            WeeklyRiskDeep: 周度风险深度报告。

        Raises:
            InvalidRiskReportInputError: 列表为空。
        """
        if not daily_summaries:
            raise InvalidRiskReportInputError(
                "daily_summaries 不能为空",
                details={"count": 0},
            )

        # 按日期排序
        sorted_daily = sorted(daily_summaries, key=lambda d: d.report_date)
        portfolio_id = sorted_daily[0].portfolio_id

        var_values = [d.var_1d_95 for d in sorted_daily]
        dd_values = [d.current_drawdown for d in sorted_daily]
        score_values = [d.overall_risk_score for d in sorted_daily]
        alert_total = sum(d.alert_count for d in sorted_daily)

        trend = self._determine_trend(score_values)

        report = WeeklyRiskDeep(
            report_id=f"WRD-{uuid.uuid4().hex[:12]}",
            week_start=sorted_daily[0].report_date,
            week_end=sorted_daily[-1].report_date,
            portfolio_id=portfolio_id,
            daily_count=len(sorted_daily),
            avg_var_1d_95=mean(var_values),
            max_var_1d_95=max(var_values),
            min_var_1d_95=min(var_values),
            avg_drawdown=mean(dd_values),
            # 回撤为负值, 最负值=最大回撤(最差), 故取 min()
            max_drawdown=min(d.max_drawdown for d in sorted_daily),
            avg_risk_score=mean(score_values),
            max_risk_score=max(score_values),
            trend_direction=trend,
            alert_total=alert_total,
            generated_at=datetime.now(UTC),
        )

        _logger.debug(
            "generate_weekly: %s~%s days=%d trend=%s avg_score=%.4f",
            report.week_start,
            report.week_end,
            report.daily_count,
            trend.value,
            report.avg_risk_score,
        )
        return report

    def _determine_trend(self, score_values: list[float]) -> TrendDirection:
        """趋势判定——前后半段均值比对。

        - 前/后半段均值差 > 阈值 → RISING/FALLING
        - 差值不显著 → STABLE
        - 单点数据 → STABLE
        """
        n = len(score_values)
        if n < 2:
            return TrendDirection.STABLE

        mid = n // 2
        first_half = score_values[:mid] if mid > 0 else score_values[:1]
        second_half = score_values[mid:] if mid < n else score_values[-1:]

        avg_first = mean(first_half)
        avg_second = mean(second_half)
        diff = avg_second - avg_first

        if diff > self._trend_threshold:
            return TrendDirection.RISING
        if diff < -self._trend_threshold:
            return TrendDirection.FALLING
        return TrendDirection.STABLE

    # ── 月度风险治理 ──

    def generate_monthly(
        self,
        daily_summaries: list[DailyRiskSummary],
    ) -> MonthlyRiskGovernance:
        """生成月度风险治理——聚合一个月日度报告。

        Args:
            daily_summaries: 一个月的日度摘要列表（≥1 条）。

        Returns:
            MonthlyRiskGovernance: 月度风险治理报告。

        Raises:
            InvalidRiskReportInputError: 列表为空。
        """
        if not daily_summaries:
            raise InvalidRiskReportInputError(
                "daily_summaries 不能为空",
                details={"count": 0},
            )

        sorted_daily = sorted(daily_summaries, key=lambda d: d.report_date)
        portfolio_id = sorted_daily[0].portfolio_id
        # month 从第一条报告日期提取 (YYYY-MM)
        month = sorted_daily[0].report_date[:7]

        var_95_values = [d.var_1d_95 for d in sorted_daily]
        var_99_values = [d.var_1d_99 for d in sorted_daily]
        dd_values = [d.current_drawdown for d in sorted_daily]
        score_values = [d.overall_risk_score for d in sorted_daily]

        # 风险评分分布
        distribution: dict[str, int] = {level.value: 0 for level in RiskLevel}
        high_days = 0
        critical_days = 0
        for d in sorted_daily:
            distribution[d.risk_level.value] += 1
            if d.risk_level == RiskLevel.HIGH:
                high_days += 1
            elif d.risk_level == RiskLevel.CRITICAL:
                critical_days += 1

        total_alerts = sum(d.alert_count for d in sorted_daily)

        report = MonthlyRiskGovernance(
            report_id=f"MRG-{uuid.uuid4().hex[:12]}",
            month=month,
            portfolio_id=portfolio_id,
            trading_days=len(sorted_daily),
            avg_var_1d_95=mean(var_95_values),
            max_var_1d_99=max(var_99_values),
            avg_drawdown=mean(dd_values),
            # 回撤为负值, 最负值=最大回撤(最差), 故取 min()
            max_drawdown=min(d.max_drawdown for d in sorted_daily),
            avg_risk_score=mean(score_values),
            risk_score_distribution=distribution,
            total_alerts=total_alerts,
            high_risk_days=high_days,
            critical_risk_days=critical_days,
            generated_at=datetime.now(UTC),
        )

        _logger.debug(
            "generate_monthly: month=%s days=%d high=%d critical=%d alerts=%d",
            report.month,
            report.trading_days,
            high_days,
            critical_days,
            total_alerts,
        )
        return report


__all__ = [
    "DailyRiskSummary",
    "EventRiskFlash",
    "InvalidRiskReportInputError",
    "MonthlyRiskGovernance",
    "RiskLevel",
    "RiskReportEngine",
    "TrendDirection",
    "WeeklyRiskDeep",
]
