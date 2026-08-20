# [BLUEPRINT] MOD-RPT-008 | docs/03_modules/_domain_reporting/risk_report_engine/blueprint.md
# [MODULE] tests.reporting.test_risk_report_engine
# [DOMAIN] D_REPORTING
# [INVARIANTS] RiskLevel 4档判定; 4类报告frozen不可变; 事件快报仅active_alerts非空生成; 周度趋势前后半段比对; 月度分布按RiskLevel统计
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRiskReportInputError(ZA-RPT-0007)
# [TESTS] self
# [A_module] module_id=MOD-RPT-008 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-008 Risk Report Engine 单元测试.

覆盖（blueprint §9）:
  - 日度报告: 字段映射 / risk_level 判定 / portfolio_id 不一致拒绝 / 空告警 / 多告警
  - 事件快报: 有告警生成 / 无告警返回None / 影响评估 / 处置建议按等级
  - 周度报告: 聚合计算 / 趋势判定(上升/下降/平稳) / 空列表拒绝 / 单点趋势
  - 月度报告: 分布统计 / high/critical天数 / 空列表拒绝 / 月份提取
  - RiskLevel 阈值判定: LOW/MEDIUM/HIGH/CRITICAL 边界
  - frozen不可变
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime

import pytest

from zephyr.reporting.risk_report_engine import (
    DailyRiskSummary,
    EventRiskFlash,
    InvalidRiskReportInputError,
    MonthlyRiskGovernance,
    RiskLevel,
    RiskReportEngine,
    TrendDirection,
    WeeklyRiskDeep,
)
from zephyr.shared.contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.shared.contracts.risk.risk_metrics import RiskMetricsReport

# ── 辅助构造 ──


def make_snapshot(
    portfolio_id: str = "PF-001",
    overall_risk_score: float = 0.25,
    active_alerts: list[str] | None = None,
    snapshot_time: str = "2026-08-02T15:00:00Z",
    gross_leverage: float = 1.2,
    top_position_concentration: float = 0.15,
    sector_concentrations: dict[str, float] | None = None,
) -> RiskDashboardSnapshot:
    """构造测试用 RiskDashboardSnapshot (CTR-P1-008)。"""
    return RiskDashboardSnapshot(
        snapshot_time=snapshot_time,
        portfolio_id=portfolio_id,
        portfolio_var_1d=0.02,
        max_drawdown_current=-0.05,
        gross_leverage=gross_leverage,
        top_position_concentration=top_position_concentration,
        overall_risk_score=overall_risk_score,
        idempotency_key="ik-snap-001",
        sector_concentrations=sector_concentrations or {"科技": 0.3, "金融": 0.2},
        active_alerts=active_alerts or [],
    )


def make_metrics(
    portfolio_id: str = "PF-001",
    as_of_date: datetime | None = None,
    var_1d_95: float = 0.02,
    var_1d_99: float = 0.03,
    cvar_1d_95: float = 0.025,
    cvar_1d_99: float = 0.035,
    current_drawdown: float = -0.05,
    max_drawdown: float = -0.12,
    sharpe_ratio: float = 1.5,
    sortino_ratio: float = 2.0,
    beta: float = 0.95,
    volatility_1d: float = 0.015,
) -> RiskMetricsReport:
    """构造测试用 RiskMetricsReport (CTR-P1-011)。"""
    return RiskMetricsReport(
        as_of_date=as_of_date or datetime(2026, 8, 2, 15, 0, 0, tzinfo=UTC),
        beta=beta,
        calculation_method="historical",
        confidence_level=0.95,
        current_drawdown=current_drawdown,
        cvar_1d_95=cvar_1d_95,
        cvar_1d_99=cvar_1d_99,
        idempotency_key="ik-metrics-001",
        lookback_period=252,
        max_drawdown=max_drawdown,
        portfolio_id=portfolio_id,
        sharpe_ratio=sharpe_ratio,
        sortino_ratio=sortino_ratio,
        var_1d_95=var_1d_95,
        var_1d_99=var_1d_99,
        volatility_1d=volatility_1d,
        volatility_1m=0.08,
    )


def make_daily(
    report_date: str = "2026-08-02",
    portfolio_id: str = "PF-001",
    overall_risk_score: float = 0.25,
    var_1d_95: float = 0.02,
    var_1d_99: float = 0.03,
    current_drawdown: float = -0.05,
    max_drawdown: float = -0.12,
    alert_count: int = 0,
) -> DailyRiskSummary:
    """构造测试用 DailyRiskSummary（用于周度/月度聚合测试）。"""
    level = RiskLevel.LOW
    if overall_risk_score >= 0.8:
        level = RiskLevel.CRITICAL
    elif overall_risk_score >= 0.6:
        level = RiskLevel.HIGH
    elif overall_risk_score >= 0.3:
        level = RiskLevel.MEDIUM
    return DailyRiskSummary(
        report_id=f"DRS-test-{report_date}",
        report_date=report_date,
        portfolio_id=portfolio_id,
        risk_level=level,
        var_1d_95=var_1d_95,
        var_1d_99=var_1d_99,
        cvar_1d_95=0.025,
        cvar_1d_99=0.035,
        current_drawdown=current_drawdown,
        max_drawdown=max_drawdown,
        gross_leverage=1.2,
        top_position_concentration=0.15,
        overall_risk_score=overall_risk_score,
        sharpe_ratio=1.5,
        sortino_ratio=2.0,
        beta=0.95,
        volatility_1d=0.015,
        sector_concentrations={"科技": 0.3},
        active_alerts=["alert"] * alert_count,
        alert_count=alert_count,
        generated_at=datetime.now(UTC),
    )


# ── 日度风险摘要测试 ──


class TestGenerateDaily:
    def test_field_mapping_from_contracts(self) -> None:
        """字段正确映射自两个契约。"""
        engine = RiskReportEngine()
        snap = make_snapshot(overall_risk_score=0.25)
        metrics = make_metrics()
        daily = engine.generate_daily(snap, metrics)

        assert daily.portfolio_id == "PF-001"
        assert daily.report_date == "2026-08-02"
        assert daily.var_1d_95 == 0.02
        assert daily.var_1d_99 == 0.03
        assert daily.cvar_1d_95 == 0.025
        assert daily.cvar_1d_99 == 0.035
        assert daily.current_drawdown == -0.05
        assert daily.max_drawdown == -0.12
        assert daily.gross_leverage == 1.2
        assert daily.top_position_concentration == 0.15
        assert daily.overall_risk_score == 0.25
        assert daily.sharpe_ratio == 1.5
        assert daily.sortino_ratio == 2.0
        assert daily.beta == 0.95
        assert daily.volatility_1d == 0.015
        assert daily.sector_concentrations == {"科技": 0.3, "金融": 0.2}
        assert daily.active_alerts == []
        assert daily.alert_count == 0
        assert daily.schema_version == "1.0"
        assert daily.report_id.startswith("DRS-")

    def test_risk_level_low(self) -> None:
        """score < 0.3 → LOW。"""
        engine = RiskReportEngine()
        daily = engine.generate_daily(make_snapshot(overall_risk_score=0.29), make_metrics())
        assert daily.risk_level == RiskLevel.LOW

    def test_risk_level_medium(self) -> None:
        """0.3 <= score < 0.6 → MEDIUM。"""
        engine = RiskReportEngine()
        daily = engine.generate_daily(make_snapshot(overall_risk_score=0.3), make_metrics())
        assert daily.risk_level == RiskLevel.MEDIUM

    def test_risk_level_high(self) -> None:
        """0.6 <= score < 0.8 → HIGH。"""
        engine = RiskReportEngine()
        daily = engine.generate_daily(make_snapshot(overall_risk_score=0.7), make_metrics())
        assert daily.risk_level == RiskLevel.HIGH

    def test_risk_level_critical(self) -> None:
        """score >= 0.8 → CRITICAL。"""
        engine = RiskReportEngine()
        daily = engine.generate_daily(make_snapshot(overall_risk_score=0.8), make_metrics())
        assert daily.risk_level == RiskLevel.CRITICAL

    def test_risk_level_boundary_zero(self) -> None:
        """score=0 → LOW。"""
        engine = RiskReportEngine()
        daily = engine.generate_daily(make_snapshot(overall_risk_score=0.0), make_metrics())
        assert daily.risk_level == RiskLevel.LOW

    def test_portfolio_id_mismatch_rejected(self) -> None:
        """portfolio_id 不一致拒绝。"""
        engine = RiskReportEngine()
        with pytest.raises(InvalidRiskReportInputError) as exc_info:
            engine.generate_daily(
                make_snapshot(portfolio_id="PF-001"),
                make_metrics(portfolio_id="PF-002"),
            )
        assert exc_info.value.error_code == "ZA-RPT-0007"
        assert "portfolio_id" in exc_info.value.message

    def test_with_alerts(self) -> None:
        """有告警时 alert_count 正确。"""
        engine = RiskReportEngine()
        alerts = ["VaR 超限", "集中度过高"]
        daily = engine.generate_daily(
            make_snapshot(overall_risk_score=0.65, active_alerts=alerts),
            make_metrics(),
        )
        assert daily.alert_count == 2
        assert daily.active_alerts == alerts

    def test_report_date_from_metrics(self) -> None:
        """report_date 取自 metrics.as_of_date。"""
        engine = RiskReportEngine()
        metrics = make_metrics(as_of_date=datetime(2026, 12, 31, 15, 0, 0, tzinfo=UTC))
        daily = engine.generate_daily(make_snapshot(), metrics)
        assert daily.report_date == "2026-12-31"

    def test_sector_concentrations_copied(self) -> None:
        """sector_concentrations 防御性拷贝。"""
        engine = RiskReportEngine()
        sectors = {"科技": 0.3}
        snap = make_snapshot(sector_concentrations=sectors)
        daily = engine.generate_daily(snap, make_metrics())
        sectors["科技"] = 0.99  # 外部修改
        assert daily.sector_concentrations["科技"] == 0.3


# ── 事件风险快报测试 ──


class TestGenerateEventFlash:
    def test_no_alerts_returns_none(self) -> None:
        """无告警返回 None。"""
        engine = RiskReportEngine()
        snap = make_snapshot(active_alerts=[])
        assert engine.generate_event_flash(snap) is None

    def test_with_alerts_generates_flash(self) -> None:
        """有告警生成快报。"""
        engine = RiskReportEngine()
        alerts = ["VaR 1d 95% 超限", "回撤接近止损线"]
        snap = make_snapshot(overall_risk_score=0.7, active_alerts=alerts)
        flash = engine.generate_event_flash(snap)

        assert flash is not None
        assert flash.alert_messages == alerts
        assert flash.alert_count == 2
        assert flash.portfolio_id == "PF-001"
        assert flash.overall_risk_score == 0.7
        assert flash.risk_level == RiskLevel.HIGH
        assert flash.report_id.startswith("ERF-")
        assert flash.event_time is not None

    def test_single_alert(self) -> None:
        """单条告警。"""
        engine = RiskReportEngine()
        snap = make_snapshot(overall_risk_score=0.2, active_alerts=["漂移检测告警"])
        flash = engine.generate_event_flash(snap)
        assert flash is not None
        assert flash.alert_count == 1
        assert "单点" in flash.impact_assessment

    def test_multiple_alerts_breadth(self) -> None:
        """多条告警 → 多点。"""
        engine = RiskReportEngine()
        snap = make_snapshot(
            overall_risk_score=0.85,
            active_alerts=["a", "b", "c"],
        )
        flash = engine.generate_event_flash(snap)
        assert flash is not None
        assert "多点" in flash.impact_assessment
        assert "3" in flash.impact_assessment

    def test_recommendations_by_level_low(self) -> None:
        """LOW 级处置建议。"""
        engine = RiskReportEngine()
        flash = engine.generate_event_flash(make_snapshot(overall_risk_score=0.1, active_alerts=["info"]))
        assert flash is not None
        assert len(flash.recommendations) >= 1
        assert any("监控" in r for r in flash.recommendations)

    def test_recommendations_by_level_critical(self) -> None:
        """CRITICAL 级处置建议含止损/Kill Switch。"""
        engine = RiskReportEngine()
        flash = engine.generate_event_flash(make_snapshot(overall_risk_score=0.9, active_alerts=["critical alert"]))
        assert flash is not None
        assert any("止损" in r or "Kill Switch" in r for r in flash.recommendations)

    def test_impact_assessment_contains_level(self) -> None:
        """影响评估含风险等级。"""
        engine = RiskReportEngine()
        flash = engine.generate_event_flash(make_snapshot(overall_risk_score=0.65, active_alerts=["alert"]))
        assert flash is not None
        assert "HIGH" in flash.impact_assessment


# ── 周度风险深度测试 ──


class TestGenerateWeekly:
    def test_aggregation_basic(self) -> None:
        """5天聚合: avg/max/min 正确。"""
        engine = RiskReportEngine()
        dailies = [
            make_daily(
                report_date=f"2026-08-{d:02d}",
                var_1d_95=0.01 * d,
                overall_risk_score=0.1 * d,
                current_drawdown=-0.01 * d,
                max_drawdown=-0.12,
                alert_count=d - 1,
            )
            for d in range(1, 6)
        ]
        weekly = engine.generate_weekly(dailies)

        assert weekly.daily_count == 5
        assert weekly.week_start == "2026-08-01"
        assert weekly.week_end == "2026-08-05"
        assert weekly.portfolio_id == "PF-001"
        assert weekly.avg_var_1d_95 == pytest.approx(0.03)
        assert weekly.max_var_1d_95 == 0.05
        assert weekly.min_var_1d_95 == 0.01
        assert weekly.avg_risk_score == pytest.approx(0.3)
        assert weekly.max_risk_score == 0.5
        assert weekly.max_drawdown == -0.12
        assert weekly.alert_total == 0 + 1 + 2 + 3 + 4
        assert weekly.report_id.startswith("WRD-")

    def test_trend_rising(self) -> None:
        """后半段风险上升 → RISING。"""
        engine = RiskReportEngine()
        dailies = [make_daily(report_date=f"2026-08-{d:02d}", overall_risk_score=0.1) for d in range(1, 4)] + [
            make_daily(report_date=f"2026-08-{d:02d}", overall_risk_score=0.8) for d in range(4, 7)
        ]
        weekly = engine.generate_weekly(dailies)
        assert weekly.trend_direction == TrendDirection.RISING

    def test_trend_falling(self) -> None:
        """后半段风险下降 → FALLING。"""
        engine = RiskReportEngine()
        dailies = [make_daily(report_date=f"2026-08-{d:02d}", overall_risk_score=0.8) for d in range(1, 4)] + [
            make_daily(report_date=f"2026-08-{d:02d}", overall_risk_score=0.1) for d in range(4, 7)
        ]
        weekly = engine.generate_weekly(dailies)
        assert weekly.trend_direction == TrendDirection.FALLING

    def test_trend_stable(self) -> None:
        """前后半段变化不显著 → STABLE。"""
        engine = RiskReportEngine()
        dailies = [make_daily(report_date=f"2026-08-{d:02d}", overall_risk_score=0.3) for d in range(1, 6)]
        weekly = engine.generate_weekly(dailies)
        assert weekly.trend_direction == TrendDirection.STABLE

    def test_single_day_trend_stable(self) -> None:
        """单天数据 → STABLE。"""
        engine = RiskReportEngine()
        weekly = engine.generate_weekly([make_daily()])
        assert weekly.trend_direction == TrendDirection.STABLE
        assert weekly.daily_count == 1

    def test_empty_list_rejected(self) -> None:
        """空列表拒绝。"""
        engine = RiskReportEngine()
        with pytest.raises(InvalidRiskReportInputError) as exc_info:
            engine.generate_weekly([])
        assert exc_info.value.error_code == "ZA-RPT-0007"

    def test_unsorted_input_sorted_internally(self) -> None:
        """乱序输入内部排序。"""
        engine = RiskReportEngine()
        dailies = [
            make_daily(report_date="2026-08-05"),
            make_daily(report_date="2026-08-01"),
            make_daily(report_date="2026-08-03"),
        ]
        weekly = engine.generate_weekly(dailies)
        assert weekly.week_start == "2026-08-01"
        assert weekly.week_end == "2026-08-05"


# ── 月度风险治理测试 ──


class TestGenerateMonthly:
    def test_aggregation_basic(self) -> None:
        """月度聚合基本字段。"""
        engine = RiskReportEngine()
        dailies = [
            make_daily(
                report_date=f"2026-08-{d:02d}", overall_risk_score=0.2, var_1d_95=0.01, var_1d_99=0.02, alert_count=0
            )
            for d in range(1, 21)
        ]
        monthly = engine.generate_monthly(dailies)

        assert monthly.month == "2026-08"
        assert monthly.trading_days == 20
        assert monthly.portfolio_id == "PF-001"
        assert monthly.avg_var_1d_95 == pytest.approx(0.01)
        assert monthly.max_var_1d_99 == 0.02
        assert monthly.avg_risk_score == pytest.approx(0.2)
        assert monthly.total_alerts == 0
        assert monthly.report_id.startswith("MRG-")

    def test_risk_score_distribution(self) -> None:
        """风险评分分布: 4档统计。"""
        engine = RiskReportEngine()
        dailies = [
            make_daily(report_date="2026-08-01", overall_risk_score=0.1),  # LOW
            make_daily(report_date="2026-08-02", overall_risk_score=0.4),  # MEDIUM
            make_daily(report_date="2026-08-03", overall_risk_score=0.7),  # HIGH
            make_daily(report_date="2026-08-04", overall_risk_score=0.9),  # CRITICAL
        ]
        monthly = engine.generate_monthly(dailies)
        assert monthly.risk_score_distribution["LOW"] == 1
        assert monthly.risk_score_distribution["MEDIUM"] == 1
        assert monthly.risk_score_distribution["HIGH"] == 1
        assert monthly.risk_score_distribution["CRITICAL"] == 1

    def test_high_critical_days(self) -> None:
        """high_risk_days / critical_risk_days 统计。"""
        engine = RiskReportEngine()
        dailies = [
            make_daily(report_date="2026-08-01", overall_risk_score=0.1),  # LOW
            make_daily(report_date="2026-08-02", overall_risk_score=0.65),  # HIGH
            make_daily(report_date="2026-08-03", overall_risk_score=0.85),  # CRITICAL
            make_daily(report_date="2026-08-04", overall_risk_score=0.7),  # HIGH
            make_daily(report_date="2026-08-05", overall_risk_score=0.9),  # CRITICAL
        ]
        monthly = engine.generate_monthly(dailies)
        assert monthly.high_risk_days == 2
        assert monthly.critical_risk_days == 2

    def test_total_alerts(self) -> None:
        """total_alerts 聚合。"""
        engine = RiskReportEngine()
        dailies = [
            make_daily(report_date="2026-08-01", alert_count=2),
            make_daily(report_date="2026-08-02", alert_count=3),
            make_daily(report_date="2026-08-03", alert_count=0),
        ]
        monthly = engine.generate_monthly(dailies)
        assert monthly.total_alerts == 5

    def test_empty_list_rejected(self) -> None:
        """空列表拒绝。"""
        engine = RiskReportEngine()
        with pytest.raises(InvalidRiskReportInputError):
            engine.generate_monthly([])

    def test_month_extracted_from_date(self) -> None:
        """月份从 report_date 提取 (YYYY-MM)。"""
        engine = RiskReportEngine()
        dailies = [make_daily(report_date="2026-12-15")]
        monthly = engine.generate_monthly(dailies)
        assert monthly.month == "2026-12"

    def test_max_drawdown_across_days(self) -> None:
        """max_drawdown 取所有天最大值。"""
        engine = RiskReportEngine()
        dailies = [
            make_daily(report_date="2026-08-01", max_drawdown=-0.05),
            make_daily(report_date="2026-08-02", max_drawdown=-0.15),
            make_daily(report_date="2026-08-03", max_drawdown=-0.08),
        ]
        monthly = engine.generate_monthly(dailies)
        assert monthly.max_drawdown == -0.15


# ── 不可变测试 ──


class TestImmutability:
    def test_daily_summary_frozen(self) -> None:
        """DailyRiskSummary frozen。"""
        engine = RiskReportEngine()
        daily = engine.generate_daily(make_snapshot(), make_metrics())
        with pytest.raises(dataclasses.FrozenInstanceError):
            daily.risk_level = RiskLevel.CRITICAL  # type: ignore[misc]

    def test_event_flash_frozen(self) -> None:
        """EventRiskFlash frozen。"""
        engine = RiskReportEngine()
        flash = engine.generate_event_flash(make_snapshot(overall_risk_score=0.7, active_alerts=["a"]))
        assert flash is not None
        with pytest.raises(dataclasses.FrozenInstanceError):
            flash.alert_count = 999  # type: ignore[misc]

    def test_weekly_frozen(self) -> None:
        """WeeklyRiskDeep frozen。"""
        engine = RiskReportEngine()
        weekly = engine.generate_weekly([make_daily()])
        with pytest.raises(dataclasses.FrozenInstanceError):
            weekly.trend_direction = TrendDirection.RISING  # type: ignore[misc]

    def test_monthly_frozen(self) -> None:
        """MonthlyRiskGovernance frozen。"""
        engine = RiskReportEngine()
        monthly = engine.generate_monthly([make_daily()])
        with pytest.raises(dataclasses.FrozenInstanceError):
            monthly.trading_days = 999  # type: ignore[misc]


# ── RiskLevel 枚举测试 ──


class TestRiskLevelEnum:
    def test_risk_level_values(self) -> None:
        """RiskLevel 4档值。"""
        assert RiskLevel.LOW.value == "LOW"
        assert RiskLevel.MEDIUM.value == "MEDIUM"
        assert RiskLevel.HIGH.value == "HIGH"
        assert RiskLevel.CRITICAL.value == "CRITICAL"

    def test_trend_direction_values(self) -> None:
        """TrendDirection 3档值。"""
        assert TrendDirection.RISING.value == "RISING"
        assert TrendDirection.FALLING.value == "FALLING"
        assert TrendDirection.STABLE.value == "STABLE"
