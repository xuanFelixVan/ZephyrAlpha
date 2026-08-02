# [BLUEPRINT] MOD-RPT-006 | docs/03_modules/_domain_reporting/regulatory_report_generator/blueprint.md
# [MODULE] zephyr.reporting.regulatory_report_generator
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.reporting
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 4类报告(程序化交易/异常交易/持仓/绩效); data_hash=SHA-256(canonical_json(content)); 必填字段缺失拒绝; RegulatoryReport frozen不可变; 基础版不含自动化报送(GATE-002/003)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRegulatoryReportError(ZA-RPT-0006)
# [TESTS] tests/reporting/test_regulatory_report_generator.py
# [TTL] permanent
"""D_REPORTING — Regulatory Report Generator (监管报告生成器)

生成证监会/交易所要求的 4 类监管报告（基础版, 手动生成）:
  - ProgrammaticTradingReport: 程序化交易报告 (策略架构/参数/风控规则)
  - AbnormalTradingReport: 异常交易自报 (异常事件/触发条件/处置动作)
  - PositionReport: 持仓报告 (持仓结构/集中度/行业偏离)
  - PerformanceReport: 绩效报告 (收益率/回撤/Sharpe/归因摘要)

基础版不含自动化报送接口（GATE-002/GATE-003 门禁）。
属 A 类基础设施(确定性报告生成), 纯消费层不发布事件。

设计真源: D:/临时工作区/依赖图/10-D-REPORTING-报告域.md §1.2 D-REPORTING-06, §4.8
蓝图: docs/03_modules/_domain_reporting/regulatory_report_generator/blueprint.md
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

_TEMPLATE_VERSION = "1.0"


class InvalidRegulatoryReportError(ZephyrBaseError):
    """监管报告输入非法——缺必填字段/类型错/值为空。"""

    error_code = "ZA-RPT-0006"


class ReportType(str, Enum):
    """监管报告类型——4类证监会/交易所报告。"""

    PROGRAMMATIC_TRADING = "programmatic_trading"
    ABNORMAL_TRADING = "abnormal_trading"
    POSITION = "position"
    PERFORMANCE = "performance"


# ── 数据模型（frozen 不可变）──


@dataclass(frozen=True)
class RegulatoryReport:
    """监管报告——含内容+完整性指纹的不可变记录。

    data_hash = SHA-256(canonical_json(content)), 用于防篡改校验。
    """

    report_id: str
    report_type: ReportType
    reporting_period: str  # YYYY-MM / YYYY-Qn / YYYY
    portfolio_id: str
    generated_at: datetime
    content: dict
    data_hash: str
    schema_version: str = _TEMPLATE_VERSION


# ── 哈希工具 ──


def _canonical_json(content: dict) -> str:
    """规范 JSON 序列化（sort_keys 确保确定性）。"""
    return json.dumps(content, sort_keys=True, ensure_ascii=False, default=str)


def _compute_data_hash(content: dict) -> str:
    """计算内容指纹——SHA-256(canonical_json(content))。"""
    return hashlib.sha256(_canonical_json(content).encode("utf-8")).hexdigest()


def _require(value: Any, field: str) -> Any:
    """提取必填字段, 缺失或空抛异常。"""
    if value is None:
        raise InvalidRegulatoryReportError(
            f"缺少必填字段: {field}",
            details={"missing_field": field},
        )
    if isinstance(value, str) and not value.strip():
        raise InvalidRegulatoryReportError(
            f"字段 {field} 不能为空",
            details={"field": field},
        )
    if isinstance(value, (list, dict)) and len(value) == 0:
        raise InvalidRegulatoryReportError(
            f"字段 {field} 不能为空列表/字典",
            details={"field": field},
        )
    return value


def _build_report(
    report_type: ReportType,
    reporting_period: str,
    portfolio_id: str,
    content: dict,
) -> RegulatoryReport:
    """构建监管报告（内部工具）。"""
    _require(reporting_period, "reporting_period")
    _require(portfolio_id, "portfolio_id")

    report = RegulatoryReport(
        report_id=f"REG-{report_type.value[:3].upper()}-{uuid.uuid4().hex[:10]}",
        report_type=report_type,
        reporting_period=reporting_period,
        portfolio_id=portfolio_id,
        generated_at=datetime.now(UTC),
        content=dict(content),
        data_hash=_compute_data_hash(content),
        schema_version=_TEMPLATE_VERSION,
    )

    _logger.debug(
        "build_report: type=%s period=%s portfolio=%s data_hash=%s",
        report_type.value, reporting_period, portfolio_id, report.data_hash[:8],
    )
    return report


# ── 监管报告生成器主类 ──


class RegulatoryReportGenerator:
    """监管报告生成器——4类报告+数据完整性校验。

    纯基础设施, 无外部状态。线程安全（无共享可变状态）。
    基础版: 手动生成, 不含自动化报送接口（GATE-002/003）。

    Usage:
        gen = RegulatoryReportGenerator()
        report = gen.generate_position("PF-001", "2026-08", holdings=[...])
        assert gen.validate_report(report) is True
    """

    # ── 程序化交易报告 ──

    def generate_programmatic_trading(
        self,
        portfolio_id: str,
        reporting_period: str,
        strategies: list[dict],
        risk_rules: list[dict],
    ) -> RegulatoryReport:
        """生成程序化交易报告——策略架构/参数/风控规则。

        Args:
            portfolio_id: 账户标识。
            reporting_period: 报告期 (如 "2026" 或 "2026-Q3")。
            strategies: 策略列表, 每项含 name/parameters/status。
            risk_rules: 风控规则列表, 每项含 name/threshold/action。

        Returns:
            RegulatoryReport: 程序化交易报告。
        """
        _require(strategies, "strategies")
        _require(risk_rules, "risk_rules")

        content = {
            "report_category": "programmatic_trading",
            "strategies": strategies,
            "risk_rules": risk_rules,
            "strategy_count": len(strategies),
            "risk_rule_count": len(risk_rules),
        }
        return _build_report(
            ReportType.PROGRAMMATIC_TRADING, reporting_period, portfolio_id, content
        )

    # ── 异常交易自报 ──

    def generate_abnormal_trading(
        self,
        portfolio_id: str,
        reporting_period: str,
        events: list[dict],
    ) -> RegulatoryReport:
        """生成异常交易自报——异常事件/触发条件/处置动作。

        Args:
            portfolio_id: 账户标识。
            reporting_period: 报告期。
            events: 异常事件列表, 每项含 event_type/trigger/action/timestamp。

        Returns:
            RegulatoryReport: 异常交易自报。
        """
        _require(events, "events")

        content = {
            "report_category": "abnormal_trading",
            "events": events,
            "event_count": len(events),
            "event_types": list({e.get("event_type", "unknown") for e in events}),
        }
        return _build_report(
            ReportType.ABNORMAL_TRADING, reporting_period, portfolio_id, content
        )

    # ── 持仓报告 ──

    def generate_position(
        self,
        portfolio_id: str,
        reporting_period: str,
        holdings: list[dict],
    ) -> RegulatoryReport:
        """生成持仓报告——持仓结构/集中度/行业偏离。

        Args:
            portfolio_id: 账户标识。
            reporting_period: 报告期 (如 "2026-08" 月度)。
            holdings: 持仓列表, 每项含 symbol/quantity/market_value/sector。

        Returns:
            RegulatoryReport: 持仓报告。
        """
        _require(holdings, "holdings")

        total_value = sum(h.get("market_value", 0) for h in holdings)
        # 集中度: 最大持仓占比
        max_position = max(
            (h.get("market_value", 0) for h in holdings), default=0
        )
        top_concentration = max_position / total_value if total_value > 0 else 0.0
        # 行业分布
        sector_values: dict[str, float] = {}
        for h in holdings:
            sector = h.get("sector", "unknown")
            sector_values[sector] = sector_values.get(sector, 0) + h.get("market_value", 0)
        sector_concentrations = {
            s: v / total_value for s, v in sector_values.items()
        } if total_value > 0 else {}

        content = {
            "report_category": "position",
            "holdings": holdings,
            "holding_count": len(holdings),
            "total_market_value": total_value,
            "top_position_concentration": top_concentration,
            "sector_concentrations": sector_concentrations,
        }
        return _build_report(
            ReportType.POSITION, reporting_period, portfolio_id, content
        )

    # ── 绩效报告 ──

    def generate_performance(
        self,
        portfolio_id: str,
        reporting_period: str,
        metrics: dict,
    ) -> RegulatoryReport:
        """生成绩效报告——收益率/回撤/Sharpe/归因摘要。

        Args:
            portfolio_id: 账户标识。
            reporting_period: 报告期 (如 "2026-Q3" 或 "2026")。
            metrics: 绩效指标, 含 return_pct/max_drawdown/sharpe_ratio/
                     sortino_ratio/attribution_summary。

        Returns:
            RegulatoryReport: 绩效报告。
        """
        _require(metrics, "metrics")
        # 必填绩效字段
        for field in ("return_pct", "max_drawdown", "sharpe_ratio"):
            if field not in metrics:
                raise InvalidRegulatoryReportError(
                    f"绩效报告缺少必填指标: {field}",
                    details={"missing_metric": field},
                )

        content = {
            "report_category": "performance",
            "metrics": metrics,
            "return_pct": metrics["return_pct"],
            "max_drawdown": metrics["max_drawdown"],
            "sharpe_ratio": metrics["sharpe_ratio"],
        }
        return _build_report(
            ReportType.PERFORMANCE, reporting_period, portfolio_id, content
        )

    # ── 完整性校验 ──

    def validate_report(self, report: RegulatoryReport) -> bool:
        """校验报告完整性——重算 data_hash 比对。

        Args:
            report: 待校验报告。

        Returns:
            bool: True=内容未篡改, False=内容被篡改。
        """
        actual_hash = _compute_data_hash(report.content)
        if actual_hash != report.data_hash:
            _logger.warning(
                "validate_report FAIL: report_id=%s data_hash 不匹配（内容被篡改）",
                report.report_id,
            )
            return False
        return True


__all__ = [
    "InvalidRegulatoryReportError",
    "RegulatoryReport",
    "RegulatoryReportGenerator",
    "ReportType",
]
