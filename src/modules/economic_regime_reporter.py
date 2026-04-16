"""
EconomicRegimeReporter - 经济范式分析报告器模块

模块ID: ECONOMIC_REGIME_REPORTER_001
技术层次: Layer 7 - AI报告层 | 业务架构: 三级时间框架融合架构
版本: v1.0.0
创建日期: 2026-04-03

核心功能:
1. 全球经济周期判断（扩张/顶峰/衰退/复苏）
2. 范式转换预警
3. 宏观因子暴露分析
4. 战略资产配置建议

对标机构: 桥水基金 (Bridgewater Associates)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EconomicRegime(Enum):
    EXPANSION = "expansion"
    PEAK = "peak"
    RECESSION = "recession"
    RECOVERY = "recovery"
    UNKNOWN = "unknown"


class RegimeTransitionRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MacroFactorExposure:
    growth_exposure: float
    inflation_exposure: float
    rate_exposure: float
    credit_exposure: float
    currency_exposure: float
    commodity_exposure: float


@dataclass
class RegimeReport:
    current_regime: EconomicRegime
    regime_probability: float
    factor_exposure: MacroFactorExposure
    regime_transition_risk: RegimeTransitionRisk
    strategic_allocation_suggestion: Dict[str, float]
    warning_signals: List[str]
    timestamp: datetime


class RegimeClassifier:

    def __init__(self):
        self.regime_indicators = {
            EconomicRegime.EXPANSION: {
                'gdp_growth': (0.02, 0.05),
                'unemployment': (0.03, 0.05),
                'inflation': (0.01, 0.03),
                'yield_curve_slope': (0.01, 0.03)
            },
            EconomicRegime.PEAK: {
                'gdp_growth': (0.01, 0.03),
                'unemployment': (0.03, 0.05),
                'inflation': (0.03, 0.06),
                'yield_curve_slope': (-0.01, 0.01)
            },
            EconomicRegime.RECESSION: {
                'gdp_growth': (-0.05, 0.01),
                'unemployment': (0.06, 0.12),
                'inflation': (-0.02, 0.02),
                'yield_curve_slope': (-0.03, -0.01)
            },
            EconomicRegime.RECOVERY: {
                'gdp_growth': (0.01, 0.04),
                'unemployment': (0.05, 0.08),
                'inflation': (0.00, 0.02),
                'yield_curve_slope': (0.00, 0.02)
            }
        }

    def classify(self, macro_data: pd.DataFrame) -> EconomicRegime:
        if macro_data.empty:
            return EconomicRegime.UNKNOWN

        latest_data = macro_data.iloc[-1]

        scores = {}
        for regime, indicators in self.regime_indicators.items():
            score = 0
            count = 0
            for indicator, (low, high) in indicators.items():
                if indicator in latest_data:
                    value = latest_data[indicator]
                    if low <= value <= high:
                        score += 1
                    count += 1

            if count > 0:
                scores[regime] = score / count

        if not scores:
            return EconomicRegime.UNKNOWN

        best_regime = max(scores, key=scores.get)
        return best_regime

    def calculate_probability(self, macro_data: pd.DataFrame, regime: EconomicRegime) -> float:
        if macro_data.empty or regime == EconomicRegime.UNKNOWN:
            return 0.0

        latest_data = macro_data.iloc[-1]
        indicators = self.regime_indicators.get(regime, {})

        if not indicators:
            return 0.0

        probabilities = []
        for indicator, (low, high) in indicators.items():
            if indicator in latest_data:
                value = latest_data[indicator]
                mid = (low + high) / 2
                width = high - low

                distance = abs(value - mid)
                prob = max(0, 1 - (distance / width))
                probabilities.append(prob)

        return np.mean(probabilities) if probabilities else 0.0


class MacroFactorModel:

    def __init__(self):
        self.factor_loadings = {
            'growth': ['gdp_growth', 'industrial_production', 'retail_sales'],
            'inflation': ['cpi', 'ppi', 'core_inflation'],
            'rate': ['fed_funds_rate', 'treasury_10y', 'treasury_2y'],
            'credit': ['credit_spread', 'high_yield_spread', 'investment_grade_spread'],
            'currency': ['dollar_index', 'eur_usd', 'usd_jpy'],
            'commodity': ['oil_price', 'gold_price', 'copper_price']
        }

    def calculate_exposure(self, macro_data: pd.DataFrame, portfolio_data: Optional[pd.DataFrame] = None) -> MacroFactorExposure:
        if macro_data.empty:
            return MacroFactorExposure(
                growth_exposure=0.0,
                inflation_exposure=0.0,
                rate_exposure=0.0,
                credit_exposure=0.0,
                currency_exposure=0.0,
                commodity_exposure=0.0
            )

        latest_data = macro_data.iloc[-1]

        def calculate_factor_exposure(factor_name: str) -> float:
            indicators = self.factor_loadings.get(factor_name, [])
            values = []
            for indicator in indicators:
                if indicator in latest_data:
                    values.append(latest_data[indicator])

            return float(np.mean(values)) if values else 0.0

        return MacroFactorExposure(
            growth_exposure=calculate_factor_exposure('growth'),
            inflation_exposure=calculate_factor_exposure('inflation'),
            rate_exposure=calculate_factor_exposure('rate'),
            credit_exposure=calculate_factor_exposure('credit'),
            currency_exposure=calculate_factor_exposure('currency'),
            commodity_exposure=calculate_factor_exposure('commodity')
        )


class StrategicAllocator:

    def __init__(self):
        self.regime_allocation = {
            EconomicRegime.EXPANSION: {
                'equity': 0.60,
                'bond': 0.25,
                'commodity': 0.10,
                'cash': 0.05
            },
            EconomicRegime.PEAK: {
                'equity': 0.40,
                'bond': 0.35,
                'commodity': 0.15,
                'cash': 0.10
            },
            EconomicRegime.RECESSION: {
                'equity': 0.20,
                'bond': 0.50,
                'commodity': 0.05,
                'cash': 0.25
            },
            EconomicRegime.RECOVERY: {
                'equity': 0.50,
                'bond': 0.30,
                'commodity': 0.15,
                'cash': 0.05
            },
            EconomicRegime.UNKNOWN: {
                'equity': 0.40,
                'bond': 0.40,
                'commodity': 0.10,
                'cash': 0.10
            }
        }

    def suggest_allocation(self, regime: EconomicRegime, factor_exposure: MacroFactorExposure) -> Dict[str, float]:
        base_allocation = self.regime_allocation.get(regime, self.regime_allocation[EconomicRegime.UNKNOWN])

        adjusted_allocation = base_allocation.copy()

        if factor_exposure.growth_exposure > 0.03:
            adjusted_allocation['equity'] = min(0.70, adjusted_allocation['equity'] * 1.1)
            adjusted_allocation['bond'] = max(0.15, adjusted_allocation['bond'] * 0.9)

        if factor_exposure.inflation_exposure > 0.04:
            adjusted_allocation['commodity'] = min(0.20, adjusted_allocation['commodity'] * 1.2)
            adjusted_allocation['bond'] = max(0.15, adjusted_allocation['bond'] * 0.85)

        if factor_exposure.rate_exposure > 0.05:
            adjusted_allocation['cash'] = min(0.30, adjusted_allocation['cash'] * 1.5)

        total = sum(adjusted_allocation.values())
        adjusted_allocation = {k: v / total for k, v in adjusted_allocation.items()}

        return adjusted_allocation


class TransitionRiskAssessor:

    def __init__(self):
        self.transition_signals = {
            'yield_curve_inversion': -0.01,
            'credit_spread_widening': 0.02,
            'volatility_spike': 0.03,
            'leading_indicator_decline': -0.02
        }

    def assess_transition_risk(self, macro_data: pd.DataFrame, current_regime: EconomicRegime) -> Tuple[RegimeTransitionRisk, List[str]]:
        if macro_data.empty or len(macro_data) < 30:
            return RegimeTransitionRisk.LOW, []

        warning_signals = []
        risk_score = 0

        latest_data = macro_data.iloc[-1]
        prev_data = macro_data.iloc[-30]

        if 'yield_curve_slope' in latest_data and 'yield_curve_slope' in prev_data:
            slope_change = latest_data['yield_curve_slope'] - prev_data['yield_curve_slope']
            if slope_change < self.transition_signals['yield_curve_inversion']:
                warning_signals.append(f"收益率曲线倒挂预警: 斜率变化 {slope_change:.4f}")
                risk_score += 2

        if 'credit_spread' in latest_data and 'credit_spread' in prev_data:
            spread_change = latest_data['credit_spread'] - prev_data['credit_spread']
            if spread_change > self.transition_signals['credit_spread_widening']:
                warning_signals.append(f"信用利差扩大预警: 利差变化 {spread_change:.4f}")
                risk_score += 1.5

        if 'vix' in latest_data and 'vix' in prev_data:
            vix_change = latest_data['vix'] - prev_data['vix']
            if vix_change > self.transition_signals['volatility_spike']:
                warning_signals.append(f"波动率飙升预警: VIX变化 {vix_change:.4f}")
                risk_score += 1

        if current_regime == EconomicRegime.EXPANSION:
            risk_score *= 1.2
        elif current_regime == EconomicRegime.PEAK:
            risk_score *= 1.5
        elif current_regime == EconomicRegime.RECESSION:
            risk_score *= 0.8

        if risk_score >= 4:
            return RegimeTransitionRisk.CRITICAL, warning_signals
        elif risk_score >= 3:
            return RegimeTransitionRisk.HIGH, warning_signals
        elif risk_score >= 1.5:
            return RegimeTransitionRisk.MEDIUM, warning_signals
        else:
            return RegimeTransitionRisk.LOW, warning_signals


class EconomicRegimeReporter:

    def __init__(self):
        self.regime_classifier = RegimeClassifier()
        self.macro_factor_model = MacroFactorModel()
        self.strategic_allocator = StrategicAllocator()
        self.transition_risk_assessor = TransitionRiskAssessor()

        logger.info("EconomicRegimeReporter initialized successfully")

    def analyze_regime(self, macro_data: pd.DataFrame, portfolio_data: Optional[pd.DataFrame] = None) -> RegimeReport:
        logger.info("Starting economic regime analysis...")

        current_regime = self.regime_classifier.classify(macro_data)
        logger.info(f"Current regime classified as: {current_regime.value}")

        regime_probability = self.regime_classifier.calculate_probability(macro_data, current_regime)
        logger.info(f"Regime probability: {regime_probability:.2%}")

        factor_exposure = self.macro_factor_model.calculate_exposure(macro_data, portfolio_data)
        logger.info(f"Factor exposure calculated: growth={factor_exposure.growth_exposure:.4f}")

        strategic_allocation = self.strategic_allocator.suggest_allocation(current_regime, factor_exposure)
        logger.info(f"Strategic allocation suggested: {strategic_allocation}")

        transition_risk, warning_signals = self.transition_risk_assessor.assess_transition_risk(macro_data, current_regime)
        logger.info(f"Transition risk: {transition_risk.value}, warnings: {len(warning_signals)}")

        report = RegimeReport(
            current_regime=current_regime,
            regime_probability=regime_probability,
            factor_exposure=factor_exposure,
            regime_transition_risk=transition_risk,
            strategic_allocation_suggestion=strategic_allocation,
            warning_signals=warning_signals,
            timestamp=datetime.now()
        )

        logger.info("Economic regime analysis completed successfully")
        return report

    def generate_report(self, macro_data: pd.DataFrame, portfolio_data: Optional[pd.DataFrame] = None, output_format: str = "dict") -> Dict:
        regime_report = self.analyze_regime(macro_data, portfolio_data)

        report_dict = {
            'report_id': f"REGIME_RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': regime_report.timestamp.isoformat(),
            'regime_analysis': {
                'current_regime': regime_report.current_regime.value,
                'regime_probability': regime_report.regime_probability,
                'transition_risk': regime_report.regime_transition_risk.value
            },
            'factor_exposure': {
                'growth': regime_report.factor_exposure.growth_exposure,
                'inflation': regime_report.factor_exposure.inflation_exposure,
                'rate': regime_report.factor_exposure.rate_exposure,
                'credit': regime_report.factor_exposure.credit_exposure,
                'currency': regime_report.factor_exposure.currency_exposure,
                'commodity': regime_report.factor_exposure.commodity_exposure
            },
            'strategic_allocation': regime_report.strategic_allocation_suggestion,
            'warning_signals': regime_report.warning_signals,
            'recommendations': self._generate_recommendations(regime_report)
        }

        if output_format == "markdown":
            return self._to_markdown(report_dict)
        else:
            return report_dict

    def _generate_recommendations(self, regime_report: RegimeReport) -> List[str]:
        recommendations = []

        regime = regime_report.current_regime
        if regime == EconomicRegime.EXPANSION:
            recommendations.append("建议维持风险资产配置，关注通胀压力")
            recommendations.append("考虑增加周期性行业暴露")
        elif regime == EconomicRegime.PEAK:
            recommendations.append("建议逐步降低风险资产配置")
            recommendations.append("增加防御性资产和对冲头寸")
        elif regime == EconomicRegime.RECESSION:
            recommendations.append("建议保持高流动性，等待复苏信号")
            recommendations.append("关注优质债券和防御性股票")
        elif regime == EconomicRegime.RECOVERY:
            recommendations.append("建议逐步增加风险资产配置")
            recommendations.append("关注周期性行业和成长股")

        if regime_report.regime_transition_risk in [RegimeTransitionRisk.HIGH, RegimeTransitionRisk.CRITICAL]:
            recommendations.append("⚠️ 范式转换风险较高，建议密切监控市场信号")

        if regime_report.warning_signals:
            recommendations.append(f"检测到 {len(regime_report.warning_signals)} 个预警信号，请关注")

        return recommendations

    def _to_markdown(self, report_dict: Dict) -> str:
        md = f"""# 经济范式分析报告

**报告ID**: {report_dict['report_id']}
**生成时间**: {report_dict['timestamp']}

## 一、经济范式判断

- **当前范式**: {report_dict['regime_analysis']['current_regime']}
- **范式概率**: {report_dict['regime_analysis']['regime_probability']:.2%}
- **转换风险**: {report_dict['regime_analysis']['transition_risk']}

## 二、宏观因子暴露

| 因子 | 暴露度 |
|------|--------|
| 增长因子 | {report_dict['factor_exposure']['growth']:.4f} |
| 通胀因子 | {report_dict['factor_exposure']['inflation']:.4f} |
| 利率因子 | {report_dict['factor_exposure']['rate']:.4f} |
| 信用因子 | {report_dict['factor_exposure']['credit']:.4f} |
| 汇率因子 | {report_dict['factor_exposure']['currency']:.4f} |
| 商品因子 | {report_dict['factor_exposure']['commodity']:.4f} |

## 三、战略资产配置建议

| 资产类别 | 建议配置 |
|---------|---------|
"""
        for asset, allocation in report_dict['strategic_allocation'].items():
            md += f"| {asset} | {allocation:.2%} |\n"

        md += "\n## 四、预警信号\n\n"
        if report_dict['warning_signals']:
            for signal in report_dict['warning_signals']:
                md += f"- {signal}\n"
        else:
            md += "无预警信号\n"

        md += "\n## 五、投资建议\n\n"
        for rec in report_dict['recommendations']:
            md += f"- {rec}\n"

        return md


if __name__ == "__main__":
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')

    macro_data = pd.DataFrame({
        'date': dates,
        'gdp_growth': np.random.uniform(0.02, 0.04, 100),
        'unemployment': np.random.uniform(0.03, 0.05, 100),
        'inflation': np.random.uniform(0.02, 0.04, 100),
        'yield_curve_slope': np.random.uniform(0.01, 0.02, 100),
        'cpi': np.random.uniform(0.02, 0.03, 100),
        'fed_funds_rate': np.random.uniform(0.04, 0.06, 100),
        'credit_spread': np.random.uniform(0.01, 0.02, 100),
        'vix': np.random.uniform(15, 25, 100)
    })
    macro_data.set_index('date', inplace=True)

    reporter = EconomicRegimeReporter()
    report = reporter.generate_report(macro_data, output_format="dict")

    print("\n" + "="*80)
    print("经济范式分析报告")
    print("="*80)
    print(f"\n当前经济范式: {report['regime_analysis']['current_regime']}")
    print(f"范式概率: {report['regime_analysis']['regime_probability']:.2%}")
    print(f"转换风险: {report['regime_analysis']['transition_risk']}")
    print("\n战略资产配置建议:")
    for asset, allocation in report['strategic_allocation'].items():
        print(f"  {asset}: {allocation:.2%}")
    print("\n投资建议:")
    for rec in report['recommendations']:
        print(f"  - {rec}")

    print("\n" + "="*80)
    print("Markdown格式报告:")
    print("="*80)
    print(reporter.generate_report(macro_data, output_format="markdown"))
