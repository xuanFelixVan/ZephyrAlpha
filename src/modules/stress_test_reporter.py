"""
StressTestReporter - 压力测试报告生成器模块

模块ID: STRESS_TEST_REPORTER_001
技术层次: Layer 7 - AI报告层 | 业务架构: 三级时间框架融合架构
版本: v1.0.0
创建日期: 2026-04-02

核心功能:
1. 压力测试执行与管理
2. 极端市场条件模拟
3. 压力测试报告生成
4. 监管合规报告输出

参考模型: Bridgewater Stress Testing, Renaissance Risk Analysis
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import logging
from pathlib import Path
import json
from scipy import stats


class StressTestType(Enum):
    """压力测试类型枚举"""
    HISTORICAL = "historical"
    HYPOTHETICAL = "hypothetical"
    REVERSE = "reverse"
    REGULATORY = "regulatory"


@dataclass
class StressTestConfig:
    """压力测试配置"""
    test_name: str
    test_type: StressTestType
    shock_magnitude: float
    shock_duration_days: int
    recovery_period_days: int
    confidence_level: float = 0.99
    description: str = ""


@dataclass
class StressTestResult:
    """压力测试结果"""
    test_name: str
    test_type: StressTestType
    config: StressTestConfig

    portfolio_value_original: float
    portfolio_value_stressed: float
    portfolio_loss: float
    portfolio_loss_pct: float

    var_estimate: float
    cvar_estimate: float
    expected_shortfall: float

    liquidity_impact: float
    concentration_impact: float

    risk_decomposition: Dict[str, float]
    scenario_details: Dict[str, Any]

    passed: bool
    failure_reasons: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    test_time: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'test_name': self.test_name,
            'test_type': self.test_type.value,
            'portfolio_loss': self.portfolio_loss,
            'portfolio_loss_pct': self.portfolio_loss_pct,
            'var_estimate': self.var_estimate,
            'cvar_estimate': self.cvar_estimate,
            'passed': self.passed,
            'recommendations': self.recommendations,
            'test_time': self.test_time.isoformat()
        }


class HistoricalStressTestEngine:
    """历史压力测试引擎"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.historical_scenarios = self._load_historical_scenarios()

    def _load_historical_scenarios(self) -> Dict[str, Dict]:
        """加载历史压力测试情景"""
        return {
            "2008_financial_crisis": {
                "name": "2008年全球金融危机",
                "start_date": "2008-09-01",
                "end_date": "2009-03-01",
                "equity_shock": -0.45,
                "bond_shock": -0.05,
                "volatility_spike": 3.5,
                "liquidity_drop": 0.70
            },
            "2020_covid_crash": {
                "name": "2020年COVID-19冲击",
                "start_date": "2020-02-20",
                "end_date": "2020-03-23",
                "equity_shock": -0.35,
                "bond_shock": 0.05,
                "volatility_spike": 4.0,
                "liquidity_drop": 0.60
            },
            "2015_china_crash": {
                "name": "2015年中国股灾",
                "start_date": "2015-06-12",
                "end_date": "2015-08-26",
                "equity_shock": -0.45,
                "bond_shock": -0.10,
                "volatility_spike": 2.5,
                "liquidity_drop": 0.50
            },
            "2018_trade_war": {
                "name": "2018年中美贸易战",
                "start_date": "2018-01-26",
                "end_date": "2018-12-31",
                "equity_shock": -0.25,
                "bond_shock": -0.05,
                "volatility_spike": 1.8,
                "liquidity_drop": 0.30
            }
        }

    def run_historical_test(
        self,
        portfolio: pd.DataFrame,
        scenario_name: str
    ) -> StressTestResult:
        """运行历史压力测试"""
        if scenario_name not in self.historical_scenarios:
            raise ValueError(f"Unknown historical scenario: {scenario_name}")

        scenario = self.historical_scenarios[scenario_name]

        shocked_portfolio = self._apply_historical_shock(portfolio, scenario)

        result = self._calculate_stress_test_result(
            portfolio=portfolio,
            shocked_portfolio=shocked_portfolio,
            test_name=scenario['name'],
            test_type=StressTestType.HISTORICAL,
            scenario_details=scenario
        )

        return result

    def _apply_historical_shock(
        self,
        portfolio: pd.DataFrame,
        scenario: Dict
    ) -> pd.DataFrame:
        """应用历史冲击"""
        shocked_portfolio = portfolio.copy()

        for idx, row in portfolio.iterrows():
            asset_type = row.get('asset_type', 'equity')

            if asset_type == 'equity':
                shock = scenario['equity_shock']
            elif asset_type == 'bond':
                shock = scenario['bond_shock']
            else:
                shock = scenario['equity_shock'] * 0.5

            beta = row.get('beta', 1.0)
            adjusted_shock = shock * beta

            shocked_portfolio.at[idx, 'shocked_value'] = row['value'] * (1 + adjusted_shock)

        return shocked_portfolio

    def _calculate_stress_test_result(
        self,
        portfolio: pd.DataFrame,
        shocked_portfolio: pd.DataFrame,
        test_name: str,
        test_type: StressTestType,
        scenario_details: Dict
    ) -> StressTestResult:
        """计算压力测试结果"""
        original_value = portfolio['value'].sum()
        stressed_value = shocked_portfolio['shocked_value'].sum()
        loss = original_value - stressed_value
        loss_pct = loss / original_value

        returns = (portfolio['value'] - shocked_portfolio['shocked_value']) / portfolio['value']
        var_estimate = np.percentile(returns, 1) * original_value
        cvar_estimate = returns[returns <= np.percentile(returns, 1)].mean() * original_value

        liquidity_impact = scenario_details.get('liquidity_drop', 0) * 0.1 * original_value

        weights = portfolio['value'] / original_value
        concentration_impact = (weights ** 2).sum() * loss

        risk_decomposition = {
            'market_risk': loss * 0.7,
            'liquidity_risk': liquidity_impact,
            'concentration_risk': concentration_impact * 0.1,
            'credit_risk': loss * 0.1,
            'operational_risk': loss * 0.05
        }

        passed = loss_pct < 0.30
        failure_reasons = []
        if not passed:
            failure_reasons.append(f"组合损失{loss_pct:.2%}超过30%阈值")

        recommendations = self._generate_recommendations(loss_pct, risk_decomposition)

        config = StressTestConfig(
            test_name=test_name,
            test_type=test_type,
            shock_magnitude=scenario_details.get('equity_shock', 0),
            shock_duration_days=180,
            recovery_period_days=365,
            description=scenario_details.get('name', '')
        )

        return StressTestResult(
            test_name=test_name,
            test_type=test_type,
            config=config,
            portfolio_value_original=original_value,
            portfolio_value_stressed=stressed_value,
            portfolio_loss=loss,
            portfolio_loss_pct=loss_pct,
            var_estimate=var_estimate,
            cvar_estimate=cvar_estimate,
            expected_shortfall=cvar_estimate,
            liquidity_impact=liquidity_impact,
            concentration_impact=concentration_impact,
            risk_decomposition=risk_decomposition,
            scenario_details=scenario_details,
            passed=passed,
            failure_reasons=failure_reasons,
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        loss_pct: float,
        risk_decomposition: Dict[str, float]
    ) -> List[str]:
        """生成风险管理建议"""
        recommendations = []

        if loss_pct > 0.30:
            recommendations.append("🚨 组合损失严重，建议立即降低仓位至50%以下")
            recommendations.append("🚨 建议增加现金储备，提高流动性缓冲")
        elif loss_pct > 0.20:
            recommendations.append("⚠️ 组合损失较大，建议适度降低风险敞口")
            recommendations.append("⚠️ 建议增加对冲工具，降低市场风险")
        elif loss_pct > 0.10:
            recommendations.append("⚠️ 组合损失中等，建议优化资产配置")
        else:
            recommendations.append("✅ 组合损失可控，建议持续监控")

        if risk_decomposition['liquidity_risk'] > 100000:
            recommendations.append("⚠️ 流动性风险较高，建议增加高流动性资产")

        if risk_decomposition['concentration_risk'] > 50000:
            recommendations.append("⚠️ 集中度风险较高，建议分散投资")

        return recommendations


class HypotheticalStressTestEngine:
    """假设性压力测试引擎"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def run_hypothetical_test(
        self,
        portfolio: pd.DataFrame,
        shock_params: Dict[str, float]
    ) -> StressTestResult:
        """运行假设性压力测试"""
        shocked_portfolio = portfolio.copy()

        for idx, row in portfolio.iterrows():
            asset_type = row.get('asset_type', 'equity')
            shock = shock_params.get(f'{asset_type}_shock', shock_params.get('equity_shock', -0.30))

            beta = row.get('beta', 1.0)
            adjusted_shock = shock * beta

            shocked_portfolio.at[idx, 'shocked_value'] = row['value'] * (1 + adjusted_shock)

        original_value = portfolio['value'].sum()
        stressed_value = shocked_portfolio['shocked_value'].sum()
        loss = original_value - stressed_value
        loss_pct = loss / original_value

        config = StressTestConfig(
            test_name="假设性压力测试",
            test_type=StressTestType.HYPOTHETICAL,
            shock_magnitude=shock_params.get('equity_shock', -0.30),
            shock_duration_days=shock_params.get('duration_days', 90),
            recovery_period_days=shock_params.get('recovery_days', 180)
        )

        return StressTestResult(
            test_name="假设性压力测试",
            test_type=StressTestType.HYPOTHETICAL,
            config=config,
            portfolio_value_original=original_value,
            portfolio_value_stressed=stressed_value,
            portfolio_loss=loss,
            portfolio_loss_pct=loss_pct,
            var_estimate=loss * 0.8,
            cvar_estimate=loss * 1.2,
            expected_shortfall=loss * 1.2,
            liquidity_impact=loss * 0.1,
            concentration_impact=loss * 0.05,
            risk_decomposition={'market_risk': loss * 0.85},
            scenario_details=shock_params,
            passed=loss_pct < 0.30,
            recommendations=["建议根据压力测试结果调整风险限额"]
        )


class ReverseStressTestEngine:
    """逆向压力测试引擎"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def run_reverse_test(
        self,
        portfolio: pd.DataFrame,
        target_loss_pct: float = 0.30
    ) -> Dict[str, Any]:
        """运行逆向压力测试

        找出导致指定损失的市场冲击
        """
        original_value = portfolio['value'].sum()
        target_loss = original_value * target_loss_pct

        required_shock = self._calculate_required_shock(portfolio, target_loss)

        return {
            'target_loss_pct': target_loss_pct,
            'target_loss_amount': target_loss,
            'required_equity_shock': required_shock,
            'scenario_description': f"需要股票市场下跌{abs(required_shock):.2%}才能导致{target_loss_pct:.2%}的组合损失",
            'likelihood': self._assess_likelihood(required_shock)
        }

    def _calculate_required_shock(
        self,
        portfolio: pd.DataFrame,
        target_loss: float
    ) -> float:
        """计算所需的冲击幅度"""
        equity_value = portfolio[portfolio['asset_type'] == 'equity']['value'].sum()

        if equity_value == 0:
            return 0.0

        required_shock = -target_loss / equity_value

        return required_shock

    def _assess_likelihood(self, shock: float) -> str:
        """评估冲击发生的可能性"""
        if abs(shock) > 0.50:
            return "极低（历史罕见）"
        elif abs(shock) > 0.30:
            return "低（每10年可能发生1-2次）"
        elif abs(shock) > 0.20:
            return "中等（每5年可能发生1次）"
        else:
            return "较高（每2-3年可能发生1次）"


class StressTestReporter:
    """压力测试报告生成器主类"""

    def __init__(self, config: Optional[Dict] = None):
        """初始化压力测试报告生成器

        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        self.historical_engine = HistoricalStressTestEngine()
        self.hypothetical_engine = HypotheticalStressTestEngine()
        self.reverse_engine = ReverseStressTestEngine()

    def run_stress_test(
        self,
        portfolio: pd.DataFrame,
        test_type: StressTestType,
        **kwargs
    ) -> StressTestResult:
        """运行压力测试

        Args:
            portfolio: 投资组合数据
            test_type: 压力测试类型
            **kwargs: 其他参数

        Returns:
            压力测试结果
        """
        self.logger.info(f"Running stress test: {test_type.value}")

        if test_type == StressTestType.HISTORICAL:
            scenario_name = kwargs.get('scenario_name', '2008_financial_crisis')
            return self.historical_engine.run_historical_test(portfolio, scenario_name)

        elif test_type == StressTestType.HYPOTHETICAL:
            shock_params = kwargs.get('shock_params', {'equity_shock': -0.30})
            return self.hypothetical_engine.run_hypothetical_test(portfolio, shock_params)

        elif test_type == StressTestType.REVERSE:
            target_loss_pct = kwargs.get('target_loss_pct', 0.30)
            reverse_result = self.reverse_engine.run_reverse_test(portfolio, target_loss_pct)

            return StressTestResult(
                test_name="逆向压力测试",
                test_type=StressTestType.REVERSE,
                config=StressTestConfig(
                    test_name="逆向压力测试",
                    test_type=StressTestType.REVERSE,
                    shock_magnitude=reverse_result['required_equity_shock'],
                    shock_duration_days=90,
                    recovery_period_days=180
                ),
                portfolio_value_original=portfolio['value'].sum(),
                portfolio_value_stressed=portfolio['value'].sum() * (1 - target_loss_pct),
                portfolio_loss=portfolio['value'].sum() * target_loss_pct,
                portfolio_loss_pct=target_loss_pct,
                var_estimate=0,
                cvar_estimate=0,
                expected_shortfall=0,
                liquidity_impact=0,
                concentration_impact=0,
                risk_decomposition={},
                scenario_details=reverse_result,
                passed=False,
                recommendations=[reverse_result['scenario_description']]
            )

        else:
            raise ValueError(f"Unsupported test type: {test_type}")

    def run_comprehensive_stress_test(
        self,
        portfolio: pd.DataFrame
    ) -> Dict[str, StressTestResult]:
        """运行综合性压力测试

        包括所有历史情景 + 假设性测试 + 逆向测试
        """
        results = {}

        for scenario_name in self.historical_engine.historical_scenarios.keys():
            try:
                result = self.run_stress_test(
                    portfolio,
                    StressTestType.HISTORICAL,
                    scenario_name=scenario_name
                )
                results[f'historical_{scenario_name}'] = result
            except Exception as e:
                self.logger.error(f"Failed to run historical test {scenario_name}: {e}")

        hypothetical_result = self.run_stress_test(
            portfolio,
            StressTestType.HYPOTHETICAL,
            shock_params={'equity_shock': -0.30, 'bond_shock': -0.10}
        )
        results['hypothetical_moderate'] = hypothetical_result

        severe_result = self.run_stress_test(
            portfolio,
            StressTestType.HYPOTHETICAL,
            shock_params={'equity_shock': -0.50, 'bond_shock': -0.20}
        )
        results['hypothetical_severe'] = severe_result

        reverse_result = self.run_stress_test(
            portfolio,
            StressTestType.REVERSE,
            target_loss_pct=0.30
        )
        results['reverse_30pct'] = reverse_result

        return results

    def generate_stress_test_report(
        self,
        results: Dict[str, StressTestResult],
        output_format: str = "markdown"
    ) -> str:
        """生成压力测试报告

        Args:
            results: 压力测试结果
            output_format: 输出格式 (markdown/html/json)

        Returns:
            报告内容
        """
        if output_format == "json":
            return json.dumps({
                test_name: result.to_dict()
                for test_name, result in results.items()
            }, indent=2, ensure_ascii=False)

        elif output_format == "markdown":
            return self._generate_markdown_report(results)

        elif output_format == "html":
            return self._generate_html_report(results)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _generate_markdown_report(self, results: Dict[str, StressTestResult]) -> str:
        """生成Markdown格式报告"""
        report = []
        report.append("# 压力测试报告")
        report.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n**测试情景数**: {len(results)}")
        report.append("\n---\n")

        passed_count = sum(1 for r in results.values() if r.passed)
        failed_count = len(results) - passed_count

        report.append("## 测试结果汇总")
        report.append(f"\n- ✅ 通过测试: {passed_count}")
        report.append(f"\n- ❌ 未通过测试: {failed_count}")
        report.append("\n")

        for test_name, result in results.items():
            status = "✅ 通过" if result.passed else "❌ 未通过"
            report.append(f"## {result.test_name} ({status})")
            report.append(f"\n**测试类型**: {result.test_type.value}")
            report.append(f"\n**组合损失**: ¥{result.portfolio_loss:,.2f} ({result.portfolio_loss_pct:.2%})")

            if result.var_estimate > 0:
                report.append(f"\n**VaR估计**: ¥{result.var_estimate:,.2f}")
                report.append(f"\n**CVaR估计**: ¥{result.cvar_estimate:,.2f}")

            if result.risk_decomposition:
                report.append("\n### 风险分解")
                report.append("\n| 风险类型 | 风险敞口 |")
                report.append("\n|---------|---------|")
                for risk_type, risk_value in result.risk_decomposition.items():
                    report.append(f"\n| {risk_type} | ¥{risk_value:,.2f} |")

            if result.recommendations:
                report.append("\n### 风险管理建议")
                for i, rec in enumerate(result.recommendations, 1):
                    report.append(f"\n{i}. {rec}")

            report.append("\n---\n")

        return "\n".join(report)

    def _generate_html_report(self, results: Dict[str, StressTestResult]) -> str:
        """生成HTML格式报告"""
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='zh-CN'>")
        html.append("<head>")
        html.append("<meta charset='UTF-8'>")
        html.append("<title>压力测试报告</title>")
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; margin: 20px; }")
        html.append("table { border-collapse: collapse; width: 100%; margin: 20px 0; }")
        html.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html.append("th { background-color: #4CAF50; color: white; }")
        html.append(".pass { color: green; font-weight: bold; }")
        html.append(".fail { color: red; font-weight: bold; }")
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")
        html.append("<h1>压力测试报告</h1>")
        html.append(f"<p><strong>生成时间</strong>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")

        for test_name, result in results.items():
            status_class = "pass" if result.passed else "fail"
            status_text = "通过" if result.passed else "未通过"

            html.append(f"<h2 class='{status_class}'>{result.test_name} ({status_text})</h2>")
            html.append(f"<p><strong>组合损失</strong>: ¥{result.portfolio_loss:,.2f} ({result.portfolio_loss_pct:.2%})</p>")

        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    reporter = StressTestReporter()

    portfolio_data = [
        {'asset_id': '600519.SH', 'asset_name': '贵州茅台', 'asset_type': 'equity', 'value': 800000, 'beta': 1.2},
        {'asset_id': '000858.SZ', 'asset_name': '五粮液', 'asset_type': 'equity', 'value': 600000, 'beta': 1.1},
        {'asset_id': '601318.SH', 'asset_name': '中国平安', 'asset_type': 'equity', 'value': 500000, 'beta': 1.3},
        {'asset_id': 'BOND_001', 'asset_name': '国债ETF', 'asset_type': 'bond', 'value': 400000, 'beta': 0.2},
    ]
    portfolio = pd.DataFrame(portfolio_data)

    print(f"投资组合总价值: ¥{portfolio['value'].sum():,.2f}")

    print("\n=== 运行综合性压力测试 ===")
    results = reporter.run_comprehensive_stress_test(portfolio)

    report = reporter.generate_stress_test_report(results, output_format="markdown")
    print("\n" + report)
