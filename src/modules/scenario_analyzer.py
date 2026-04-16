"""
ScenarioAnalyzer - 情景分析器模块

模块ID: SCENARIO_ANALYZER_001
技术层次: Layer 7 - AI报告层 | 业务架构: 三级时间框架融合架构
版本: v1.0.0
创建日期: 2026-04-02

核心功能:
1. 情景定义与管理
2. 市场冲击模拟
3. 资产影响评估
4. 风险指标计算
5. 情景分析报告生成

参考模型: Bridgewater Scenario Analysis, Renaissance Stress Testing
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import logging
from pathlib import Path
import json


class ScenarioType(Enum):
    """情景类型枚举"""
    FINANCIAL_CRISIS = "financial_crisis"
    COVID_CRASH = "covid_crash"
    RATE_HIKE = "rate_hike"
    TRADE_WAR = "trade_war"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    CUSTOM = "custom"


@dataclass
class MarketShock:
    """市场冲击参数"""
    equity_shock: float
    bond_shock: float
    commodity_shock: float
    currency_shock: float
    volatility_spike: float
    liquidity_drop: float

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'equity_shock': self.equity_shock,
            'bond_shock': self.bond_shock,
            'commodity_shock': self.commodity_shock,
            'currency_shock': self.currency_shock,
            'volatility_spike': self.volatility_spike,
            'liquidity_drop': self.liquidity_drop
        }


@dataclass
class AssetImpact:
    """资产影响结果"""
    asset_id: str
    asset_name: str
    asset_type: str
    original_value: float
    shocked_value: float
    impact_pct: float
    impact_amount: float

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'asset_id': self.asset_id,
            'asset_name': self.asset_name,
            'asset_type': self.asset_type,
            'original_value': self.original_value,
            'shocked_value': self.shocked_value,
            'impact_pct': self.impact_pct,
            'impact_amount': self.impact_amount
        }


@dataclass
class ScenarioResult:
    """情景分析结果"""
    scenario_name: str
    scenario_type: ScenarioType
    shock_params: MarketShock
    asset_impacts: List[AssetImpact]
    portfolio_impact: float
    portfolio_impact_pct: float
    risk_metrics: Dict[str, float]
    recommendations: List[str] = field(default_factory=list)
    analysis_time: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'scenario_name': self.scenario_name,
            'scenario_type': self.scenario_type.value,
            'shock_params': self.shock_params.to_dict(),
            'asset_impacts': [impact.to_dict() for impact in self.asset_impacts],
            'portfolio_impact': self.portfolio_impact,
            'portfolio_impact_pct': self.portfolio_impact_pct,
            'risk_metrics': self.risk_metrics,
            'recommendations': self.recommendations,
            'analysis_time': self.analysis_time.isoformat()
        }


class ScenarioLibrary:
    """情景库管理器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scenarios = self._load_default_scenarios()

    def _load_default_scenarios(self) -> Dict[str, Dict]:
        """加载默认情景库"""
        return {
            "financial_crisis": {
                "name": "2008金融危机",
                "description": "2008年全球金融危机情景模拟",
                "shock_params": MarketShock(
                    equity_shock=-0.45,
                    bond_shock=-0.05,
                    commodity_shock=-0.30,
                    currency_shock=0.10,
                    volatility_spike=3.0,
                    liquidity_drop=0.60
                ),
                "historical_reference": "2008-09-15 Lehman Brothers破产",
                "duration_days": 180,
                "recovery_days": 720
            },
            "covid_crash": {
                "name": "COVID-19冲击",
                "description": "2020年COVID-19疫情冲击情景模拟",
                "shock_params": MarketShock(
                    equity_shock=-0.35,
                    bond_shock=0.05,
                    commodity_shock=-0.40,
                    currency_shock=0.05,
                    volatility_spike=4.0,
                    liquidity_drop=0.50
                ),
                "historical_reference": "2020-03-09 全球股市熔断",
                "duration_days": 30,
                "recovery_days": 180
            },
            "rate_hike": {
                "name": "加息周期",
                "description": "美联储加息周期情景模拟",
                "shock_params": MarketShock(
                    equity_shock=-0.15,
                    bond_shock=-0.20,
                    commodity_shock=-0.10,
                    currency_shock=0.15,
                    volatility_spike=1.5,
                    liquidity_drop=0.20
                ),
                "historical_reference": "2022年美联储激进加息",
                "duration_days": 365,
                "recovery_days": 365
            },
            "trade_war": {
                "name": "贸易战",
                "description": "中美贸易摩擦情景模拟",
                "shock_params": MarketShock(
                    equity_shock=-0.20,
                    bond_shock=-0.05,
                    commodity_shock=-0.25,
                    currency_shock=-0.10,
                    volatility_spike=2.0,
                    liquidity_drop=0.30
                ),
                "historical_reference": "2018-03-22 特朗普签署贸易备忘录",
                "duration_days": 180,
                "recovery_days": 365
            },
            "liquidity_crisis": {
                "name": "流动性危机",
                "description": "市场流动性枯竭情景模拟",
                "shock_params": MarketShock(
                    equity_shock=-0.25,
                    bond_shock=-0.15,
                    commodity_shock=-0.30,
                    currency_shock=0.20,
                    volatility_spike=5.0,
                    liquidity_drop=0.80
                ),
                "historical_reference": "2020-03-23 美股流动性危机",
                "duration_days": 14,
                "recovery_days": 90
            }
        }

    def get_scenario(self, scenario_type: ScenarioType) -> Optional[Dict]:
        """获取情景定义"""
        return self.scenarios.get(scenario_type.value)

    def list_scenarios(self) -> List[str]:
        """列出所有可用情景"""
        return list(self.scenarios.keys())

    def add_custom_scenario(self, name: str, scenario_def: Dict) -> bool:
        """添加自定义情景"""
        try:
            self.scenarios[name] = scenario_def
            self.logger.info(f"Added custom scenario: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add custom scenario: {e}")
            return False


class MarketShockEngine:
    """市场冲击模拟引擎"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def apply_market_shock(
        self,
        asset_value: float,
        asset_type: str,
        shock_params: MarketShock,
        beta: float = 1.0,
        sector_factor: float = 1.0
    ) -> float:
        """应用市场冲击

        Args:
            asset_value: 资产原始价值
            asset_type: 资产类型 (equity/bond/commodity/currency)
            shock_params: 市场冲击参数
            beta: 资产Beta系数
            sector_factor: 行业因子调整

        Returns:
            冲击后的资产价值
        """
        shock_map = {
            'equity': shock_params.equity_shock,
            'bond': shock_params.bond_shock,
            'commodity': shock_params.commodity_shock,
            'currency': shock_params.currency_shock
        }

        base_shock = shock_map.get(asset_type, 0)
        adjusted_shock = base_shock * beta * sector_factor

        shocked_value = asset_value * (1 + adjusted_shock)

        return shocked_value

    def apply_shock_to_portfolio(
        self,
        portfolio: pd.DataFrame,
        shock_params: MarketShock
    ) -> pd.DataFrame:
        """应用市场冲击到整个投资组合

        Args:
            portfolio: 投资组合数据
            shock_params: 市场冲击参数

        Returns:
            冲击后的投资组合
        """
        shocked_portfolio = portfolio.copy()

        for idx, row in portfolio.iterrows():
            asset_type = row.get('asset_type', 'equity')
            beta = row.get('beta', 1.0)
            sector_factor = row.get('sector_factor', 1.0)

            shocked_value = self.apply_market_shock(
                asset_value=row['value'],
                asset_type=asset_type,
                shock_params=shock_params,
                beta=beta,
                sector_factor=sector_factor
            )

            shocked_portfolio.at[idx, 'shocked_value'] = shocked_value
            shocked_portfolio.at[idx, 'impact_amount'] = row['value'] - shocked_value
            shocked_portfolio.at[idx, 'impact_pct'] = (row['value'] - shocked_value) / row['value']

        return shocked_portfolio


class RiskMetricsCalculator:
    """风险指标计算器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_scenario_risk_metrics(
        self,
        portfolio: pd.DataFrame,
        shocked_portfolio: pd.DataFrame
    ) -> Dict[str, float]:
        """计算情景下的风险指标

        Args:
            portfolio: 原始投资组合
            shocked_portfolio: 冲击后的投资组合

        Returns:
            风险指标字典
        """
        metrics = {}

        original_value = portfolio['value'].sum()
        shocked_value = shocked_portfolio['shocked_value'].sum()

        metrics['portfolio_loss'] = original_value - shocked_value
        metrics['portfolio_loss_pct'] = (original_value - shocked_value) / original_value

        asset_losses = portfolio['value'] - shocked_portfolio['shocked_value']
        metrics['max_single_asset_loss'] = asset_losses.max()
        metrics['max_single_asset_loss_pct'] = (asset_losses / portfolio['value']).max()

        if 'liquidity_drop' in shocked_portfolio.columns:
            metrics['liquidity_risk'] = shocked_portfolio['liquidity_drop'].mean()
        else:
            metrics['liquidity_risk'] = 0.0

        weights = shocked_portfolio['shocked_value'] / shocked_value
        metrics['concentration_risk'] = (weights ** 2).sum()

        metrics['num_assets_affected'] = (asset_losses > 0).sum()
        metrics['pct_assets_affected'] = (asset_losses > 0).sum() / len(portfolio)

        return metrics

    def calculate_var_equivalent(
        self,
        portfolio_loss: float,
        portfolio_value: float,
        confidence_level: float = 0.99
    ) -> float:
        """计算VaR等价值

        Args:
            portfolio_loss: 组合损失
            portfolio_value: 组合价值
            confidence_level: 置信水平

        Returns:
            VaR等价值
        """
        var_pct = portfolio_loss / portfolio_value
        return var_pct


class ScenarioAnalyzer:
    """情景分析器主类"""

    def __init__(self, config: Optional[Dict] = None):
        """初始化情景分析器

        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        self.scenario_library = ScenarioLibrary()
        self.shock_engine = MarketShockEngine()
        self.risk_calculator = RiskMetricsCalculator()

    def analyze_scenario(
        self,
        portfolio: pd.DataFrame,
        scenario_type: ScenarioType,
        custom_shock: Optional[MarketShock] = None
    ) -> ScenarioResult:
        """分析特定情景下的组合表现

        Args:
            portfolio: 投资组合数据
            scenario_type: 情景类型
            custom_shock: 自定义冲击参数 (仅用于custom类型)

        Returns:
            情景分析结果
        """
        self.logger.info(f"Analyzing scenario: {scenario_type.value}")

        if scenario_type == ScenarioType.CUSTOM:
            if custom_shock is None:
                raise ValueError("Custom scenario requires custom_shock parameter")
            shock_params = custom_shock
            scenario_name = "自定义情景"
        else:
            scenario_def = self.scenario_library.get_scenario(scenario_type)
            if scenario_def is None:
                raise ValueError(f"Unknown scenario type: {scenario_type}")
            shock_params = scenario_def['shock_params']
            scenario_name = scenario_def['name']

        shocked_portfolio = self.shock_engine.apply_shock_to_portfolio(
            portfolio, shock_params
        )

        risk_metrics = self.risk_calculator.calculate_scenario_risk_metrics(
            portfolio, shocked_portfolio
        )

        asset_impacts = []
        for idx, row in shocked_portfolio.iterrows():
            impact = AssetImpact(
                asset_id=row.get('asset_id', f'asset_{idx}'),
                asset_name=row.get('asset_name', f'资产{idx}'),
                asset_type=row.get('asset_type', 'equity'),
                original_value=row['value'],
                shocked_value=row['shocked_value'],
                impact_pct=row['impact_pct'],
                impact_amount=row['impact_amount']
            )
            asset_impacts.append(impact)

        recommendations = self._generate_recommendations(risk_metrics, scenario_type)

        result = ScenarioResult(
            scenario_name=scenario_name,
            scenario_type=scenario_type,
            shock_params=shock_params,
            asset_impacts=asset_impacts,
            portfolio_impact=risk_metrics['portfolio_loss'],
            portfolio_impact_pct=risk_metrics['portfolio_loss_pct'],
            risk_metrics=risk_metrics,
            recommendations=recommendations
        )

        self.logger.info(f"Scenario analysis completed: {scenario_type.value}")
        return result

    def analyze_multiple_scenarios(
        self,
        portfolio: pd.DataFrame,
        scenario_types: Optional[List[ScenarioType]] = None
    ) -> Dict[str, ScenarioResult]:
        """分析多个情景下的组合表现

        Args:
            portfolio: 投资组合数据
            scenario_types: 情景类型列表 (默认分析所有预设情景)

        Returns:
            多个情景的分析结果字典
        """
        if scenario_types is None:
            scenario_types = [
                ScenarioType.FINANCIAL_CRISIS,
                ScenarioType.COVID_CRASH,
                ScenarioType.RATE_HIKE,
                ScenarioType.TRADE_WAR,
                ScenarioType.LIQUIDITY_CRISIS
            ]

        results = {}
        for scenario_type in scenario_types:
            try:
                result = self.analyze_scenario(portfolio, scenario_type)
                results[scenario_type.value] = result
            except Exception as e:
                self.logger.error(f"Failed to analyze scenario {scenario_type.value}: {e}")

        return results

    def generate_scenario_report(
        self,
        results: Dict[str, ScenarioResult],
        output_format: str = "markdown"
    ) -> str:
        """生成情景分析报告

        Args:
            results: 情景分析结果
            output_format: 输出格式 (markdown/html/json)

        Returns:
            报告内容
        """
        if output_format == "json":
            return json.dumps({
                scenario: result.to_dict()
                for scenario, result in results.items()
            }, indent=2, ensure_ascii=False)

        elif output_format == "markdown":
            return self._generate_markdown_report(results)

        elif output_format == "html":
            return self._generate_html_report(results)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _generate_markdown_report(self, results: Dict[str, ScenarioResult]) -> str:
        """生成Markdown格式报告"""
        report = []
        report.append("# 情景分析报告")
        report.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n**分析情景数**: {len(results)}")
        report.append("\n---\n")

        for scenario_key, result in results.items():
            report.append(f"## {result.scenario_name}")
            report.append(f"\n**情景类型**: {result.scenario_type.value}")
            report.append(f"\n**组合损失**: ¥{result.portfolio_impact:,.2f} ({result.portfolio_impact_pct:.2%})")

            report.append("\n### 市场冲击参数")
            shock_dict = result.shock_params.to_dict()
            report.append("\n| 冲击类型 | 冲击幅度 |")
            report.append("\n|---------|---------|")
            for key, value in shock_dict.items():
                if 'shock' in key:
                    report.append(f"\n| {key} | {value:.2%} |")
                else:
                    report.append(f"\n| {key} | {value:.2f} |")

            report.append("\n### 风险指标")
            report.append("\n| 指标 | 数值 |")
            report.append("\n|-----|------|")
            for key, value in result.risk_metrics.items():
                if isinstance(value, float):
                    if 'pct' in key or 'loss_pct' in key:
                        report.append(f"\n| {key} | {value:.2%} |")
                    else:
                        report.append(f"\n| {key} | {value:,.2f} |")
                else:
                    report.append(f"\n| {key} | {value} |")

            if result.recommendations:
                report.append("\n### 风险管理建议")
                for i, rec in enumerate(result.recommendations, 1):
                    report.append(f"\n{i}. {rec}")

            report.append("\n---\n")

        return "\n".join(report)

    def _generate_html_report(self, results: Dict[str, ScenarioResult]) -> str:
        """生成HTML格式报告"""
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='zh-CN'>")
        html.append("<head>")
        html.append("<meta charset='UTF-8'>")
        html.append("<title>情景分析报告</title>")
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; margin: 20px; }")
        html.append("table { border-collapse: collapse; width: 100%; margin: 20px 0; }")
        html.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html.append("th { background-color: #4CAF50; color: white; }")
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")
        html.append("<h1>情景分析报告</h1>")
        html.append(f"<p><strong>生成时间</strong>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")

        for scenario_key, result in results.items():
            html.append(f"<h2>{result.scenario_name}</h2>")
            html.append(f"<p><strong>组合损失</strong>: ¥{result.portfolio_impact:,.2f} ({result.portfolio_impact_pct:.2%})</p>")

            html.append("<h3>风险指标</h3>")
            html.append("<table>")
            html.append("<tr><th>指标</th><th>数值</th></tr>")
            for key, value in result.risk_metrics.items():
                if isinstance(value, float):
                    if 'pct' in key or 'loss_pct' in key:
                        html.append(f"<tr><td>{key}</td><td>{value:.2%}</td></tr>")
                    else:
                        html.append(f"<tr><td>{key}</td><td>{value:,.2f}</td></tr>")
                else:
                    html.append(f"<tr><td>{key}</td><td>{value}</td></tr>")
            html.append("</table>")

        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _generate_recommendations(
        self,
        risk_metrics: Dict[str, float],
        scenario_type: ScenarioType
    ) -> List[str]:
        """生成风险管理建议"""
        recommendations = []

        if risk_metrics['portfolio_loss_pct'] > 0.30:
            recommendations.append("⚠️ 组合损失超过30%，建议立即降低仓位或增加对冲")
        elif risk_metrics['portfolio_loss_pct'] > 0.20:
            recommendations.append("⚠️ 组合损失超过20%，建议评估风险敞口并考虑调整仓位")

        if risk_metrics['concentration_risk'] > 0.15:
            recommendations.append("⚠️ 集中度风险较高，建议分散投资降低单一资产依赖")

        if risk_metrics['liquidity_risk'] > 0.50:
            recommendations.append("⚠️ 流动性风险较高，建议增加现金或高流动性资产配置")

        if scenario_type == ScenarioType.FINANCIAL_CRISIS:
            recommendations.append("建议增加防御性资产配置（国债、黄金）")
            recommendations.append("建议降低杠杆率，提高现金储备")
        elif scenario_type == ScenarioType.RATE_HIKE:
            recommendations.append("建议缩短债券久期，降低利率风险敞口")
            recommendations.append("建议增加浮动利率资产配置")

        if not recommendations:
            recommendations.append("✅ 当前风险水平可控，建议持续监控")

        return recommendations


def create_sample_portfolio() -> pd.DataFrame:
    """创建示例投资组合"""
    data = [
        {'asset_id': '600519.SH', 'asset_name': '贵州茅台', 'asset_type': 'equity', 'value': 800000, 'beta': 1.2, 'sector_factor': 1.0},
        {'asset_id': '000858.SZ', 'asset_name': '五粮液', 'asset_type': 'equity', 'value': 600000, 'beta': 1.1, 'sector_factor': 1.0},
        {'asset_id': '601318.SH', 'asset_name': '中国平安', 'asset_type': 'equity', 'value': 500000, 'beta': 1.3, 'sector_factor': 0.9},
        {'asset_id': 'BOND_001', 'asset_name': '国债ETF', 'asset_type': 'bond', 'value': 400000, 'beta': 0.2, 'sector_factor': 1.0},
        {'asset_id': 'GOLD_001', 'asset_name': '黄金ETF', 'asset_type': 'commodity', 'value': 300000, 'beta': 0.0, 'sector_factor': 1.0},
        {'asset_id': 'USD_001', 'asset_name': '美元货币基金', 'asset_type': 'currency', 'value': 200000, 'beta': 0.0, 'sector_factor': 1.0},
    ]

    return pd.DataFrame(data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    analyzer = ScenarioAnalyzer()

    portfolio = create_sample_portfolio()
    print(f"投资组合总价值: ¥{portfolio['value'].sum():,.2f}")

    print("\n=== 分析2008金融危机情景 ===")
    result = analyzer.analyze_scenario(portfolio, ScenarioType.FINANCIAL_CRISIS)
    print(f"组合损失: ¥{result.portfolio_impact:,.2f} ({result.portfolio_impact_pct:.2%})")
    print(f"风险指标: {result.risk_metrics}")

    print("\n=== 分析所有预设情景 ===")
    results = analyzer.analyze_multiple_scenarios(portfolio)

    report = analyzer.generate_scenario_report(results, output_format="markdown")
    print("\n" + report)
