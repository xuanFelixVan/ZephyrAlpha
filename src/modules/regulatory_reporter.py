"""
RegulatoryReporter - 监管合规报告器模块

模块ID: REGULATORY_REPORTER_001
技术层次: Layer 7 - AI报告层 | 业务架构: 三级时间框架融合架构
版本: v1.0.0
创建日期: 2026-04-02

核心功能:
1. 证监会合规报告生成
2. 风险敞口报告
3. 投资限制合规检查
4. 信息披露报告

参考模型: 中国证监会私募基金监管要求
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import logging


class ComplianceStatus(Enum):
    """合规状态"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"


@dataclass
class ComplianceCheck:
    """合规检查项"""
    check_name: str
    requirement: str
    actual_value: float
    limit_value: float
    status: ComplianceStatus
    description: str

    def to_dict(self) -> Dict:
        return {
            'check_name': self.check_name,
            'requirement': self.requirement,
            'actual_value': self.actual_value,
            'limit_value': self.limit_value,
            'status': self.status.value,
            'description': self.description
        }


@dataclass
class RegulatoryReport:
    """监管合规报告"""
    report_id: str
    report_type: str
    timestamp: datetime

    fund_name: str
    fund_size: float
    reporting_period: str

    compliance_checks: List[ComplianceCheck]
    overall_status: ComplianceStatus

    risk_exposure: Dict[str, float]
    investment_limits: Dict[str, float]

    violations: List[str]
    corrective_actions: List[str]

    def to_dict(self) -> Dict:
        return {
            'report_id': self.report_id,
            'report_type': self.report_type,
            'timestamp': self.timestamp.isoformat(),
            'fund_name': self.fund_name,
            'fund_size': self.fund_size,
            'reporting_period': self.reporting_period,
            'compliance_checks': [c.to_dict() for c in self.compliance_checks],
            'overall_status': self.overall_status.value,
            'risk_exposure': self.risk_exposure,
            'investment_limits': self.investment_limits,
            'violations': self.violations,
            'corrective_actions': self.corrective_actions
        }


class ComplianceChecker:
    """合规检查器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.limits = {
            'single_stock_max': 0.10,
            'single_industry_max': 0.30,
            'total_equity_max': 0.95,
            'cash_min': 0.05,
            'leverage_max': 1.4
        }

    def check_single_stock_limit(
        self,
        portfolio: pd.DataFrame
    ) -> ComplianceCheck:
        """检查单股权重限制"""
        total_value = portfolio['value'].sum()
        max_weight = (portfolio['value'] / total_value).max()

        status = ComplianceStatus.COMPLIANT if max_weight <= self.limits['single_stock_max'] else ComplianceStatus.VIOLATION

        return ComplianceCheck(
            check_name="单股权重限制",
            requirement="单股权重≤10%",
            actual_value=max_weight,
            limit_value=self.limits['single_stock_max'],
            status=status,
            description=f"最大单股权重为{max_weight:.2%}"
        )

    def check_industry_limit(
        self,
        portfolio: pd.DataFrame
    ) -> ComplianceCheck:
        """检查行业权重限制"""
        if 'industry' not in portfolio.columns:
            return ComplianceCheck(
                check_name="行业权重限制",
                requirement="单一行业权重≤30%",
                actual_value=0,
                limit_value=self.limits['single_industry_max'],
                status=ComplianceStatus.COMPLIANT,
                description="未提供行业分类数据"
            )

        total_value = portfolio['value'].sum()
        industry_weights = portfolio.groupby('industry')['value'].sum() / total_value
        max_industry_weight = industry_weights.max()

        status = ComplianceStatus.COMPLIANT if max_industry_weight <= self.limits['single_industry_max'] else ComplianceStatus.VIOLATION

        return ComplianceCheck(
            check_name="行业权重限制",
            requirement="单一行业权重≤30%",
            actual_value=max_industry_weight,
            limit_value=self.limits['single_industry_max'],
            status=status,
            description=f"最大行业权重为{max_industry_weight:.2%}"
        )

    def check_cash_requirement(
        self,
        portfolio: pd.DataFrame
    ) -> ComplianceCheck:
        """检查现金最低要求"""
        total_value = portfolio['value'].sum()
        cash_value = portfolio[portfolio['asset_type'] == 'currency']['value'].sum() if 'asset_type' in portfolio.columns else 0
        cash_ratio = cash_value / total_value

        status = ComplianceStatus.COMPLIANT if cash_ratio >= self.limits['cash_min'] else ComplianceStatus.WARNING

        return ComplianceCheck(
            check_name="现金最低要求",
            requirement="现金比例≥5%",
            actual_value=cash_ratio,
            limit_value=self.limits['cash_min'],
            status=status,
            description=f"当前现金比例为{cash_ratio:.2%}"
        )


class RegulatoryReporter:
    """监管合规报告器主类"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.compliance_checker = ComplianceChecker()
        self.report_counter = 0

    def generate_regulatory_report(
        self,
        portfolio: pd.DataFrame,
        fund_name: str = "清风量化基金",
        reporting_period: str = "2026年第一季度"
    ) -> RegulatoryReport:
        """生成监管合规报告"""
        self.report_counter += 1
        report_id = f"REG_RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.report_counter:06d}"

        compliance_checks = [
            self.compliance_checker.check_single_stock_limit(portfolio),
            self.compliance_checker.check_industry_limit(portfolio),
            self.compliance_checker.check_cash_requirement(portfolio)
        ]

        overall_status = ComplianceStatus.COMPLIANT
        if any(c.status == ComplianceStatus.VIOLATION for c in compliance_checks):
            overall_status = ComplianceStatus.VIOLATION
        elif any(c.status == ComplianceStatus.WARNING for c in compliance_checks):
            overall_status = ComplianceStatus.WARNING

        violations = [c.description for c in compliance_checks if c.status == ComplianceStatus.VIOLATION]

        corrective_actions = []
        if violations:
            corrective_actions.append("立即调整投资组合以满足监管要求")

        risk_exposure = {
            'market_risk': portfolio['value'].sum() * 0.15,
            'liquidity_risk': portfolio['value'].sum() * 0.05,
            'concentration_risk': portfolio['value'].sum() * 0.03
        }

        investment_limits = self.compliance_checker.limits

        return RegulatoryReport(
            report_id=report_id,
            report_type="季度监管合规报告",
            timestamp=datetime.now(),
            fund_name=fund_name,
            fund_size=portfolio['value'].sum(),
            reporting_period=reporting_period,
            compliance_checks=compliance_checks,
            overall_status=overall_status,
            risk_exposure=risk_exposure,
            investment_limits=investment_limits,
            violations=violations,
            corrective_actions=corrective_actions
        )

    def generate_report_markdown(self, report: RegulatoryReport) -> str:
        """生成Markdown报告"""
        md = []
        md.append(f"# 监管合规报告")
        md.append(f"\n**报告ID**: {report.report_id}")
        md.append(f"\n**基金名称**: {report.fund_name}")
        md.append(f"\n**报告期间**: {report.reporting_period}")
        md.append(f"\n**基金规模**: ¥{report.fund_size:,.2f}")
        md.append(f"\n**整体合规状态**: {report.overall_status.value.upper()}")

        md.append(f"\n## 合规检查项")
        md.append(f"\n| 检查项 | 要求 | 实际值 | 状态 |")
        md.append(f"\n|-------|------|--------|------|")
        for check in report.compliance_checks:
            md.append(f"\n| {check.check_name} | {check.requirement} | {check.actual_value:.2%} | {check.status.value} |")

        if report.violations:
            md.append(f"\n## 违规事项")
            for violation in report.violations:
                md.append(f"\n- 🚨 {violation}")

        if report.corrective_actions:
            md.append(f"\n## 整改措施")
            for action in report.corrective_actions:
                md.append(f"\n- {action}")

        return "\n".join(md)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    reporter = RegulatoryReporter()

    portfolio_data = [
        {'asset_id': '600519.SH', 'asset_name': '贵州茅台', 'asset_type': 'equity', 'industry': '食品饮料', 'value': 800000},
        {'asset_id': '000858.SZ', 'asset_name': '五粮液', 'asset_type': 'equity', 'industry': '食品饮料', 'value': 600000},
        {'asset_id': '601318.SH', 'asset_name': '中国平安', 'asset_type': 'equity', 'industry': '金融', 'value': 500000},
        {'asset_id': 'BOND_001', 'asset_name': '国债ETF', 'asset_type': 'bond', 'industry': '债券', 'value': 400000},
        {'asset_id': 'CASH_001', 'asset_name': '现金', 'asset_type': 'currency', 'industry': '现金', 'value': 200000},
    ]
    portfolio = pd.DataFrame(portfolio_data)

    report = reporter.generate_regulatory_report(portfolio)

    markdown_report = reporter.generate_report_markdown(report)
    print(markdown_report)
