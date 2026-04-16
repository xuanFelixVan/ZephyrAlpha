"""
ExecutionCostReporter - 执行成本分析报告器模块

模块ID: EXECUTION_COST_REPORTER_001
技术层次: Layer 7 - AI报告层 | 业务架构: 三级时间框架融合架构
版本: v1.0.0
创建日期: 2026-04-02

核心功能:
1. 交易执行成本分析
2. 滑点分析
3. 市场冲击成本分析
4. 执行效率评估

参考模型: Renaissance Execution Analysis, Two Sigma Transaction Cost Analysis
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
import logging


@dataclass
class TradeExecution:
    """交易执行记录"""
    trade_id: str
    symbol: str
    side: str  # buy/sell
    order_size: float
    executed_size: float
    order_price: float
    executed_price: float
    execution_time: datetime
    market_impact: float

    @property
    def slippage(self) -> float:
        """计算滑点"""
        return abs(self.executed_price - self.order_price) / self.order_price

    @property
    def fill_rate(self) -> float:
        """计算成交率"""
        return self.executed_size / self.order_size if self.order_size > 0 else 0

    def to_dict(self) -> Dict:
        return {
            'trade_id': self.trade_id,
            'symbol': self.symbol,
            'side': self.side,
            'order_size': self.order_size,
            'executed_size': self.executed_size,
            'order_price': self.order_price,
            'executed_price': self.executed_price,
            'slippage': self.slippage,
            'fill_rate': self.fill_rate,
            'market_impact': self.market_impact,
            'execution_time': self.execution_time.isoformat()
        }


@dataclass
class ExecutionCostMetrics:
    """执行成本指标"""
    total_trades: int
    total_volume: float
    total_value: float

    avg_slippage: float
    max_slippage: float
    avg_market_impact: float

    avg_fill_rate: float
    execution_efficiency: float

    total_cost: float
    cost_per_share: float

    def to_dict(self) -> Dict:
        return {
            'total_trades': self.total_trades,
            'total_volume': self.total_volume,
            'total_value': self.total_value,
            'avg_slippage': self.avg_slippage,
            'max_slippage': self.max_slippage,
            'avg_market_impact': self.avg_market_impact,
            'avg_fill_rate': self.avg_fill_rate,
            'execution_efficiency': self.execution_efficiency,
            'total_cost': self.total_cost,
            'cost_per_share': self.cost_per_share
        }


@dataclass
class ExecutionCostReport:
    """执行成本报告"""
    report_id: str
    timestamp: datetime
    reporting_period: str

    execution_metrics: ExecutionCostMetrics
    trade_executions: List[TradeExecution]

    cost_breakdown: Dict[str, float]
    optimization_opportunities: List[str]

    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            'report_id': self.report_id,
            'timestamp': self.timestamp.isoformat(),
            'reporting_period': self.reporting_period,
            'execution_metrics': self.execution_metrics.to_dict(),
            'trade_executions': [t.to_dict() for t in self.trade_executions],
            'cost_breakdown': self.cost_breakdown,
            'optimization_opportunities': self.optimization_opportunities,
            'recommendations': self.recommendations
        }


class SlippageAnalyzer:
    """滑点分析器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_slippage(
        self,
        trades: List[TradeExecution]
    ) -> Dict[str, float]:
        """分析滑点"""
        if not trades:
            return {
                'avg_slippage': 0,
                'max_slippage': 0,
                'min_slippage': 0,
                'std_slippage': 0
            }

        slippages = [t.slippage for t in trades]

        return {
            'avg_slippage': np.mean(slippages),
            'max_slippage': np.max(slippages),
            'min_slippage': np.min(slippages),
            'std_slippage': np.std(slippages)
        }


class MarketImpactAnalyzer:
    """市场冲击分析器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_market_impact(
        self,
        trades: List[TradeExecution]
    ) -> Dict[str, float]:
        """分析市场冲击"""
        if not trades:
            return {
                'avg_impact': 0,
                'max_impact': 0,
                'total_impact_cost': 0
            }

        impacts = [t.market_impact for t in trades]

        return {
            'avg_impact': np.mean(impacts),
            'max_impact': np.max(impacts),
            'total_impact_cost': sum(impacts)
        }


class ExecutionCostReporter:
    """执行成本分析报告器主类"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.slippage_analyzer = SlippageAnalyzer()
        self.market_impact_analyzer = MarketImpactAnalyzer()
        self.report_counter = 0

    def generate_execution_cost_report(
        self,
        trades: List[TradeExecution],
        reporting_period: str = "2026年第一季度"
    ) -> ExecutionCostReport:
        """生成执行成本报告"""
        self.report_counter += 1
        report_id = f"EXEC_COST_RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.report_counter:06d}"

        metrics = self._calculate_execution_metrics(trades)

        cost_breakdown = {
            'slippage_cost': metrics.total_cost * 0.4,
            'market_impact_cost': metrics.total_cost * 0.3,
            'commission_cost': metrics.total_cost * 0.2,
            'spread_cost': metrics.total_cost * 0.1
        }

        optimization_opportunities = self._identify_optimization_opportunities(metrics)

        recommendations = self._generate_recommendations(metrics)

        return ExecutionCostReport(
            report_id=report_id,
            timestamp=datetime.now(),
            reporting_period=reporting_period,
            execution_metrics=metrics,
            trade_executions=trades,
            cost_breakdown=cost_breakdown,
            optimization_opportunities=optimization_opportunities,
            recommendations=recommendations
        )

    def _calculate_execution_metrics(
        self,
        trades: List[TradeExecution]
    ) -> ExecutionCostMetrics:
        """计算执行指标"""
        if not trades:
            return ExecutionCostMetrics(
                total_trades=0,
                total_volume=0,
                total_value=0,
                avg_slippage=0,
                max_slippage=0,
                avg_market_impact=0,
                avg_fill_rate=0,
                execution_efficiency=0,
                total_cost=0,
                cost_per_share=0
            )

        total_volume = sum(t.executed_size for t in trades)
        total_value = sum(t.executed_size * t.executed_price for t in trades)

        slippage_stats = self.slippage_analyzer.analyze_slippage(trades)
        impact_stats = self.market_impact_analyzer.analyze_market_impact(trades)

        avg_fill_rate = np.mean([t.fill_rate for t in trades])

        execution_efficiency = avg_fill_rate * (1 - slippage_stats['avg_slippage'])

        total_cost = total_value * slippage_stats['avg_slippage'] + impact_stats['total_impact_cost']
        cost_per_share = total_cost / total_volume if total_volume > 0 else 0

        return ExecutionCostMetrics(
            total_trades=len(trades),
            total_volume=total_volume,
            total_value=total_value,
            avg_slippage=slippage_stats['avg_slippage'],
            max_slippage=slippage_stats['max_slippage'],
            avg_market_impact=impact_stats['avg_impact'],
            avg_fill_rate=avg_fill_rate,
            execution_efficiency=execution_efficiency,
            total_cost=total_cost,
            cost_per_share=cost_per_share
        )

    def _identify_optimization_opportunities(
        self,
        metrics: ExecutionCostMetrics
    ) -> List[str]:
        """识别优化机会"""
        opportunities = []

        if metrics.avg_slippage > 0.001:
            opportunities.append("💡 平均滑点较高，建议优化下单时机和算法")

        if metrics.avg_fill_rate < 0.95:
            opportunities.append("💡 成交率较低，建议调整限价单策略")

        if metrics.avg_market_impact > 0.005:
            opportunities.append("💡 市场冲击较大，建议分批下单或使用VWAP算法")

        return opportunities

    def _generate_recommendations(
        self,
        metrics: ExecutionCostMetrics
    ) -> List[str]:
        """生成建议"""
        recommendations = []

        if metrics.execution_efficiency < 0.8:
            recommendations.append("⚠️ 执行效率较低，建议全面优化交易执行流程")
        elif metrics.execution_efficiency < 0.9:
            recommendations.append("⚠️ 执行效率中等，建议优化滑点和成交率")
        else:
            recommendations.append("✅ 执行效率良好，建议持续监控")

        if metrics.total_cost > metrics.total_value * 0.01:
            recommendations.append("⚠️ 总执行成本超过1%，建议降低交易频率或优化执行算法")

        return recommendations

    def generate_report_markdown(self, report: ExecutionCostReport) -> str:
        """生成Markdown报告"""
        md = []
        md.append(f"# 执行成本分析报告")
        md.append(f"\n**报告ID**: {report.report_id}")
        md.append(f"\n**报告期间**: {report.reporting_period}")
        md.append(f"\n**生成时间**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        metrics = report.execution_metrics
        md.append(f"\n## 执行指标汇总")
        md.append(f"\n- 总交易次数: {metrics.total_trades}")
        md.append(f"\n- 总交易量: {metrics.total_volume:,.0f}股")
        md.append(f"\n- 总交易额: ¥{metrics.total_value:,.2f}")
        md.append(f"\n- 平均滑点: {metrics.avg_slippage:.4%}")
        md.append(f"\n- 最大滑点: {metrics.max_slippage:.4%}")
        md.append(f"\n- 平均市场冲击: {metrics.avg_market_impact:.4%}")
        md.append(f"\n- 平均成交率: {metrics.avg_fill_rate:.2%}")
        md.append(f"\n- 执行效率: {metrics.execution_efficiency:.2%}")
        md.append(f"\n- 总执行成本: ¥{metrics.total_cost:,.2f}")
        md.append(f"\n- 单股成本: ¥{metrics.cost_per_share:.4f}")

        md.append(f"\n## 成本分解")
        md.append(f"\n| 成本类型 | 金额 |")
        md.append(f"\n|---------|------|")
        for cost_type, amount in report.cost_breakdown.items():
            md.append(f"\n| {cost_type} | ¥{amount:,.2f} |")

        if report.optimization_opportunities:
            md.append(f"\n## 优化机会")
            for opportunity in report.optimization_opportunities:
                md.append(f"\n- {opportunity}")

        if report.recommendations:
            md.append(f"\n## 建议")
            for rec in report.recommendations:
                md.append(f"\n- {rec}")

        return "\n".join(md)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    reporter = ExecutionCostReporter()

    trades = [
        TradeExecution(
            trade_id="TRADE_001",
            symbol="600519.SH",
            side="buy",
            order_size=10000,
            executed_size=9500,
            order_price=1800.00,
            executed_price=1805.00,
            execution_time=datetime.now(),
            market_impact=0.002
        ),
        TradeExecution(
            trade_id="TRADE_002",
            symbol="000858.SZ",
            side="sell",
            order_size=8000,
            executed_size=7800,
            order_price=150.00,
            executed_price=149.50,
            execution_time=datetime.now(),
            market_impact=0.001
        )
    ]

    report = reporter.generate_execution_cost_report(trades)

    markdown_report = reporter.generate_report_markdown(report)
    print(markdown_report)
