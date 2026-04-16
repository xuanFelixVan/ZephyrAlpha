"""
SignalQualityReporter - 信号质量监控报告器模块

模块ID: SIGNAL_QUALITY_REPORTER_001
技术层次: Layer 7 - AI报告层 | 业务架构: 三级时间框架融合架构
版本: v1.0.0
创建日期: 2026-04-03

核心功能:
1. 信号衰减监控
2. 信号拥挤度分析
3. 信号稳定性评估
4. 信号质量评分

对标机构: 文艺复兴科技 (Renaissance Technologies)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    CRITICAL = "critical"


class DecayRate(Enum):
    NONE = "none"
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"
    CRITICAL = "critical"


class CrowdingLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class SignalDecayAnalysis:
    decay_rate: DecayRate
    half_life: float
    decay_trend: str
    historical_decay: List[float]


@dataclass
class SignalCrowdingAnalysis:
    crowding_level: CrowdingLevel
    crowding_score: float
    capacity_estimate: float
    crowding_trend: str


@dataclass
class SignalStabilityAnalysis:
    stability_score: float
    volatility: float
    autocorrelation: float
    stationarity_pvalue: float


@dataclass
class SignalQualityReport:
    signal_id: str
    quality_score: float
    quality_level: SignalQuality
    decay_analysis: SignalDecayAnalysis
    crowding_analysis: SignalCrowdingAnalysis
    stability_analysis: SignalStabilityAnalysis
    recommendations: List[str]
    warning_signals: List[str]
    timestamp: datetime


class SignalDecayAnalyzer:

    def __init__(self, lookback_period: int = 252):
        self.lookback_period = lookback_period

        self.decay_thresholds = {
            DecayRate.NONE: 0.95,
            DecayRate.SLOW: 0.85,
            DecayRate.MODERATE: 0.70,
            DecayRate.FAST: 0.50,
            DecayRate.CRITICAL: 0.0
        }

    def calculate_decay(self, signals: pd.DataFrame, returns: Optional[pd.DataFrame] = None) -> SignalDecayAnalysis:
        if signals.empty:
            return SignalDecayAnalysis(
                decay_rate=DecayRate.NONE,
                half_life=999.0,
                decay_trend="unknown",
                historical_decay=[]
            )

        signal_values = signals.iloc[:, 0] if len(signals.columns) == 1 else signals.mean(axis=1)

        decay_scores = []
        window_size = min(20, len(signal_values) // 5)

        for i in range(window_size, len(signal_values)):
            window_data = signal_values.iloc[i-window_size:i]

            if returns is not None and len(returns) > i:
                window_returns = returns.iloc[i-window_size:i]
                if len(window_data) == len(window_returns):
                    correlation = window_data.corr(window_returns.iloc[:, 0] if len(window_returns.columns) > 0 else window_returns)
                    decay_scores.append(abs(correlation) if not np.isnan(correlation) else 0.5)
            else:
                autocorr = window_data.autocorr(lag=1) if len(window_data) > 1 else 0.5
                decay_scores.append(abs(autocorr) if not np.isnan(autocorr) else 0.5)

        if not decay_scores:
            decay_scores = [0.5]

        current_decay = decay_scores[-1] if decay_scores else 0.5
        decay_rate = self._classify_decay_rate(current_decay)

        half_life = self._estimate_half_life(signal_values)

        decay_trend = self._analyze_decay_trend(decay_scores)

        return SignalDecayAnalysis(
            decay_rate=decay_rate,
            half_life=half_life,
            decay_trend=decay_trend,
            historical_decay=decay_scores[-20:] if len(decay_scores) >= 20 else decay_scores
        )

    def _classify_decay_rate(self, decay_score: float) -> DecayRate:
        if decay_score >= self.decay_thresholds[DecayRate.NONE]:
            return DecayRate.NONE
        elif decay_score >= self.decay_thresholds[DecayRate.SLOW]:
            return DecayRate.SLOW
        elif decay_score >= self.decay_thresholds[DecayRate.MODERATE]:
            return DecayRate.MODERATE
        elif decay_score >= self.decay_thresholds[DecayRate.FAST]:
            return DecayRate.FAST
        else:
            return DecayRate.CRITICAL

    def _estimate_half_life(self, signal_series: pd.Series) -> float:
        if len(signal_series) < 10:
            return 999.0

        try:
            lagged = signal_series.shift(1).dropna()
            current = signal_series[1:]

            if len(lagged) != len(current):
                min_len = min(len(lagged), len(current))
                lagged = lagged[:min_len]
                current = current[:min_len]

            slope, _, _, _, _ = stats.linregress(lagged, current)

            if slope <= 0 or slope >= 1:
                return 999.0

            half_life = -np.log(2) / np.log(slope)
            return min(max(half_life, 1.0), 999.0)
        except Exception:
            return 999.0

    def _analyze_decay_trend(self, decay_scores: List[float]) -> str:
        if len(decay_scores) < 5:
            return "insufficient_data"

        recent_scores = decay_scores[-5:]
        earlier_scores = decay_scores[-10:-5] if len(decay_scores) >= 10 else decay_scores[:-5]

        recent_mean = np.mean(recent_scores)
        earlier_mean = np.mean(earlier_scores)

        change = (recent_mean - earlier_mean) / earlier_mean if earlier_mean != 0 else 0

        if change > 0.1:
            return "improving"
        elif change < -0.1:
            return "deteriorating"
        else:
            return "stable"


class SignalCrowdingDetector:

    def __init__(self):
        self.crowding_thresholds = {
            CrowdingLevel.LOW: 0.3,
            CrowdingLevel.MODERATE: 0.5,
            CrowdingLevel.HIGH: 0.7,
            CrowdingLevel.EXTREME: 1.0
        }

    def detect_crowding(self, signals: pd.DataFrame, market_data: Optional[pd.DataFrame] = None) -> SignalCrowdingAnalysis:
        if signals.empty:
            return SignalCrowdingAnalysis(
                crowding_level=CrowdingLevel.LOW,
                crowding_score=0.0,
                capacity_estimate=999.0,
                crowding_trend="unknown"
            )

        signal_values = signals.iloc[:, 0] if len(signals.columns) == 1 else signals.mean(axis=1)

        crowding_score = self._calculate_crowding_score(signal_values, market_data)

        crowding_level = self._classify_crowding_level(crowding_score)

        capacity_estimate = self._estimate_capacity(signal_values, crowding_score)

        crowding_trend = self._analyze_crowding_trend(signal_values)

        return SignalCrowdingAnalysis(
            crowding_level=crowding_level,
            crowding_score=crowding_score,
            capacity_estimate=capacity_estimate,
            crowding_trend=crowding_trend
        )

    def _calculate_crowding_score(self, signal_series: pd.Series, market_data: Optional[pd.DataFrame]) -> float:
        if len(signal_series) < 20:
            return 0.0

        recent_std = signal_series[-20:].std()
        historical_std = signal_series.std()

        if historical_std == 0:
            return 0.0

        std_ratio = recent_std / historical_std

        herding_score = 1.0 - min(std_ratio, 1.0)

        if market_data is not None and 'volume' in market_data.columns:
            volume_corr = signal_series[-20:].corr(market_data['volume'][-20:])
            if not np.isnan(volume_corr):
                herding_score = (herding_score + abs(volume_corr)) / 2

        return min(max(herding_score, 0.0), 1.0)

    def _classify_crowding_level(self, crowding_score: float) -> CrowdingLevel:
        if crowding_score < self.crowding_thresholds[CrowdingLevel.LOW]:
            return CrowdingLevel.LOW
        elif crowding_score < self.crowding_thresholds[CrowdingLevel.MODERATE]:
            return CrowdingLevel.MODERATE
        elif crowding_score < self.crowding_thresholds[CrowdingLevel.HIGH]:
            return CrowdingLevel.HIGH
        else:
            return CrowdingLevel.EXTREME

    def _estimate_capacity(self, signal_series: pd.Series, crowding_score: float) -> float:
        base_capacity = 100.0

        signal_strength = abs(signal_series[-20:].mean()) if len(signal_series) >= 20 else 0.5

        capacity = base_capacity * (1 - crowding_score) * signal_strength * 10

        return max(capacity, 1.0)

    def _analyze_crowding_trend(self, signal_series: pd.Series) -> str:
        if len(signal_series) < 30:
            return "insufficient_data"

        recent = signal_series[-10:]
        earlier = signal_series[-30:-20]

        recent_concentration = (recent ** 2).sum()
        earlier_concentration = (earlier ** 2).sum()

        if earlier_concentration == 0:
            return "unknown"

        change = (recent_concentration - earlier_concentration) / earlier_concentration

        if change > 0.2:
            return "increasing"
        elif change < -0.2:
            return "decreasing"
        else:
            return "stable"


class SignalStabilityAnalyzer:

    def __init__(self):
        self.stability_thresholds = {
            'excellent': 0.9,
            'good': 0.75,
            'moderate': 0.6,
            'poor': 0.4
        }

    def analyze_stability(self, signals: pd.DataFrame) -> SignalStabilityAnalysis:
        if signals.empty:
            return SignalStabilityAnalysis(
                stability_score=0.0,
                volatility=0.0,
                autocorrelation=0.0,
                stationarity_pvalue=1.0
            )

        signal_values = signals.iloc[:, 0] if len(signals.columns) == 1 else signals.mean(axis=1)

        volatility = self._calculate_volatility(signal_values)

        autocorrelation = self._calculate_autocorrelation(signal_values)

        stationarity_pvalue = self._test_stationarity(signal_values)

        stability_score = self._calculate_stability_score(volatility, autocorrelation, stationarity_pvalue)

        return SignalStabilityAnalysis(
            stability_score=stability_score,
            volatility=volatility,
            autocorrelation=autocorrelation,
            stationarity_pvalue=stationarity_pvalue
        )

    def _calculate_volatility(self, signal_series: pd.Series) -> float:
        if len(signal_series) < 2:
            return 0.0

        return float(signal_series.std() / abs(signal_series.mean()) if signal_series.mean() != 0 else signal_series.std())

    def _calculate_autocorrelation(self, signal_series: pd.Series) -> float:
        if len(signal_series) < 10:
            return 0.0

        try:
            autocorr = signal_series.autocorr(lag=1)
            return abs(autocorr) if not np.isnan(autocorr) else 0.0
        except Exception:
            return 0.0

    def _test_stationarity(self, signal_series: pd.Series) -> float:
        if len(signal_series) < 20:
            return 1.0

        try:
            from statsmodels.tsa.stattools import adfuller
            result = adfuller(signal_series.dropna())
            return result[1]
        except Exception:
            return 1.0

    def _calculate_stability_score(self, volatility: float, autocorrelation: float, stationarity_pvalue: float) -> float:
        volatility_score = max(0, 1 - volatility)

        autocorr_score = autocorrelation

        stationarity_score = 1 - stationarity_pvalue

        stability_score = (volatility_score * 0.4 + autocorr_score * 0.3 + stationarity_score * 0.3)

        return min(max(stability_score, 0.0), 1.0)


class SignalQualityReporter:

    def __init__(self):
        self.decay_analyzer = SignalDecayAnalyzer()
        self.crowding_detector = SignalCrowdingDetector()
        self.stability_analyzer = SignalStabilityAnalyzer()

        self.quality_thresholds = {
            SignalQuality.EXCELLENT: 0.9,
            SignalQuality.GOOD: 0.75,
            SignalQuality.MODERATE: 0.6,
            SignalQuality.POOR: 0.4
        }

        logger.info("SignalQualityReporter initialized successfully")

    def analyze_signal_quality(self, signals: pd.DataFrame, returns: Optional[pd.DataFrame] = None, market_data: Optional[pd.DataFrame] = None, signal_id: str = "SIGNAL_001") -> SignalQualityReport:
        logger.info(f"Starting signal quality analysis for {signal_id}...")

        decay_analysis = self.decay_analyzer.calculate_decay(signals, returns)
        logger.info(f"Decay rate: {decay_analysis.decay_rate.value}, half-life: {decay_analysis.half_life:.2f}")

        crowding_analysis = self.crowding_detector.detect_crowding(signals, market_data)
        logger.info(f"Crowding level: {crowding_analysis.crowding_level.value}, score: {crowding_analysis.crowding_score:.2%}")

        stability_analysis = self.stability_analyzer.analyze_stability(signals)
        logger.info(f"Stability score: {stability_analysis.stability_score:.2%}")

        quality_score = self._calculate_quality_score(decay_analysis, crowding_analysis, stability_analysis)
        quality_level = self._classify_quality_level(quality_score)

        recommendations = self._generate_recommendations(decay_analysis, crowding_analysis, stability_analysis, quality_level)
        warning_signals = self._generate_warning_signals(decay_analysis, crowding_analysis, stability_analysis)

        report = SignalQualityReport(
            signal_id=signal_id,
            quality_score=quality_score,
            quality_level=quality_level,
            decay_analysis=decay_analysis,
            crowding_analysis=crowding_analysis,
            stability_analysis=stability_analysis,
            recommendations=recommendations,
            warning_signals=warning_signals,
            timestamp=datetime.now()
        )

        logger.info(f"Signal quality analysis completed: {quality_level.value} ({quality_score:.2%})")
        return report

    def _calculate_quality_score(self, decay_analysis: SignalDecayAnalysis, crowding_analysis: SignalCrowdingAnalysis, stability_analysis: SignalStabilityAnalysis) -> float:
        decay_scores = {
            DecayRate.NONE: 1.0,
            DecayRate.SLOW: 0.85,
            DecayRate.MODERATE: 0.65,
            DecayRate.FAST: 0.40,
            DecayRate.CRITICAL: 0.15
        }

        crowding_scores = {
            CrowdingLevel.LOW: 1.0,
            CrowdingLevel.MODERATE: 0.75,
            CrowdingLevel.HIGH: 0.50,
            CrowdingLevel.EXTREME: 0.25
        }

        decay_score = decay_scores.get(decay_analysis.decay_rate, 0.5)
        crowding_score = crowding_scores.get(crowding_analysis.crowding_level, 0.5)
        stability_score = stability_analysis.stability_score

        quality_score = decay_score * 0.4 + crowding_score * 0.3 + stability_score * 0.3

        return quality_score

    def _classify_quality_level(self, quality_score: float) -> SignalQuality:
        if quality_score >= self.quality_thresholds[SignalQuality.EXCELLENT]:
            return SignalQuality.EXCELLENT
        elif quality_score >= self.quality_thresholds[SignalQuality.GOOD]:
            return SignalQuality.GOOD
        elif quality_score >= self.quality_thresholds[SignalQuality.MODERATE]:
            return SignalQuality.MODERATE
        elif quality_score >= self.quality_thresholds[SignalQuality.POOR]:
            return SignalQuality.POOR
        else:
            return SignalQuality.CRITICAL

    def _generate_recommendations(self, decay_analysis: SignalDecayAnalysis, crowding_analysis: SignalCrowdingAnalysis, stability_analysis: SignalStabilityAnalysis, quality_level: SignalQuality) -> List[str]:
        recommendations = []

        if decay_analysis.decay_rate in [DecayRate.FAST, DecayRate.CRITICAL]:
            recommendations.append("⚠️ 信号衰减严重，建议重新训练模型或调整信号参数")
            recommendations.append("考虑增加信号频率或缩短持仓周期")
        elif decay_analysis.decay_rate == DecayRate.MODERATE:
            recommendations.append("信号存在一定衰减，建议监控衰减趋势")

        if crowding_analysis.crowding_level in [CrowdingLevel.HIGH, CrowdingLevel.EXTREME]:
            recommendations.append("⚠️ 信号拥挤度高，建议降低仓位或寻找新信号")
            recommendations.append(f"当前容量估计: {crowding_analysis.capacity_estimate:.2f}M")
        elif crowding_analysis.crowding_level == CrowdingLevel.MODERATE:
            recommendations.append("信号拥挤度适中，建议持续监控")

        if stability_analysis.stability_score < 0.6:
            recommendations.append("⚠️ 信号稳定性不足，建议检查数据质量和模型假设")
        elif stability_analysis.stability_score < 0.75:
            recommendations.append("信号稳定性一般，建议优化特征工程")

        if quality_level == SignalQuality.EXCELLENT:
            recommendations.append("✅ 信号质量优秀，可以增加配置权重")
        elif quality_level == SignalQuality.GOOD:
            recommendations.append("✅ 信号质量良好，维持当前配置")
        elif quality_level == SignalQuality.MODERATE:
            recommendations.append("信号质量中等，建议优化后继续使用")
        elif quality_level in [SignalQuality.POOR, SignalQuality.CRITICAL]:
            recommendations.append("❌ 信号质量较差，建议暂停使用或重新设计")

        return recommendations

    def _generate_warning_signals(self, decay_analysis: SignalDecayAnalysis, crowding_analysis: SignalCrowdingAnalysis, stability_analysis: SignalStabilityAnalysis) -> List[str]:
        warnings = []

        if decay_analysis.decay_trend == "deteriorating":
            warnings.append(f"信号衰减趋势恶化，半衰期: {decay_analysis.half_life:.2f}天")

        if crowding_analysis.crowding_trend == "increasing":
            warnings.append(f"信号拥挤度上升趋势，当前: {crowding_analysis.crowding_score:.2%}")

        if stability_analysis.stationarity_pvalue > 0.05:
            warnings.append(f"信号非平稳 (p={stability_analysis.stationarity_pvalue:.4f})，可能存在趋势")

        if stability_analysis.volatility > 2.0:
            warnings.append(f"信号波动率过高: {stability_analysis.volatility:.2f}")

        return warnings

    def generate_report(self, signals: pd.DataFrame, returns: Optional[pd.DataFrame] = None, market_data: Optional[pd.DataFrame] = None, signal_id: str = "SIGNAL_001", output_format: str = "dict") -> Dict:
        quality_report = self.analyze_signal_quality(signals, returns, market_data, signal_id)

        report_dict = {
            'report_id': f"SIGNAL_QUALITY_RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'signal_id': quality_report.signal_id,
            'timestamp': quality_report.timestamp.isoformat(),
            'quality_assessment': {
                'quality_score': quality_report.quality_score,
                'quality_level': quality_report.quality_level.value
            },
            'decay_analysis': {
                'decay_rate': quality_report.decay_analysis.decay_rate.value,
                'half_life': quality_report.decay_analysis.half_life,
                'decay_trend': quality_report.decay_analysis.decay_trend
            },
            'crowding_analysis': {
                'crowding_level': quality_report.crowding_analysis.crowding_level.value,
                'crowding_score': quality_report.crowding_analysis.crowding_score,
                'capacity_estimate': quality_report.crowding_analysis.capacity_estimate,
                'crowding_trend': quality_report.crowding_analysis.crowding_trend
            },
            'stability_analysis': {
                'stability_score': quality_report.stability_analysis.stability_score,
                'volatility': quality_report.stability_analysis.volatility,
                'autocorrelation': quality_report.stability_analysis.autocorrelation,
                'stationarity_pvalue': quality_report.stability_analysis.stationarity_pvalue
            },
            'recommendations': quality_report.recommendations,
            'warning_signals': quality_report.warning_signals
        }

        if output_format == "markdown":
            return self._to_markdown(report_dict)
        else:
            return report_dict

    def _to_markdown(self, report_dict: Dict) -> str:
        md = f"""# 信号质量监控报告

**报告ID**: {report_dict['report_id']}
**信号ID**: {report_dict['signal_id']}
**生成时间**: {report_dict['timestamp']}

## 一、信号质量评估

- **质量评分**: {report_dict['quality_assessment']['quality_score']:.2%}
- **质量等级**: {report_dict['quality_assessment']['quality_level']}

## 二、信号衰减分析

| 指标 | 数值 |
|------|------|
| 衰减速率 | {report_dict['decay_analysis']['decay_rate']} |
| 半衰期 | {report_dict['decay_analysis']['half_life']:.2f}天 |
| 衰减趋势 | {report_dict['decay_analysis']['decay_trend']} |

## 三、信号拥挤度分析

| 指标 | 数值 |
|------|------|
| 拥挤度等级 | {report_dict['crowding_analysis']['crowding_level']} |
| 拥挤度评分 | {report_dict['crowding_analysis']['crowding_score']:.2%} |
| 容量估计 | {report_dict['crowding_analysis']['capacity_estimate']:.2f}M |
| 拥挤趋势 | {report_dict['crowding_analysis']['crowding_trend']} |

## 四、信号稳定性分析

| 指标 | 数值 |
|------|------|
| 稳定性评分 | {report_dict['stability_analysis']['stability_score']:.2%} |
| 波动率 | {report_dict['stability_analysis']['volatility']:.4f} |
| 自相关系数 | {report_dict['stability_analysis']['autocorrelation']:.4f} |
| 平稳性p值 | {report_dict['stability_analysis']['stationarity_pvalue']:.4f} |

## 五、预警信号

"""
        if report_dict['warning_signals']:
            for signal in report_dict['warning_signals']:
                md += f"- {signal}\n"
        else:
            md += "无预警信号\n"

        md += "\n## 六、优化建议\n\n"
        for rec in report_dict['recommendations']:
            md += f"- {rec}\n"

        return md


if __name__ == "__main__":
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=252, freq='D')

    signals = pd.DataFrame({
        'date': dates,
        'signal': np.random.randn(252).cumsum() * 0.01 + np.sin(np.arange(252) * 0.05) * 0.5
    })
    signals.set_index('date', inplace=True)

    returns = pd.DataFrame({
        'date': dates,
        'returns': np.random.randn(252) * 0.02
    })
    returns.set_index('date', inplace=True)

    market_data = pd.DataFrame({
        'date': dates,
        'volume': np.random.uniform(1000000, 5000000, 252)
    })
    market_data.set_index('date', inplace=True)

    reporter = SignalQualityReporter()
    report = reporter.generate_report(signals, returns, market_data, signal_id="MOMENTUM_001", output_format="dict")

    print("\n" + "="*80)
    print("信号质量监控报告")
    print("="*80)
    print(f"\n信号ID: {report['signal_id']}")
    print(f"质量评分: {report['quality_assessment']['quality_score']:.2%}")
    print(f"质量等级: {report['quality_assessment']['quality_level']}")
    print(f"\n衰减分析:")
    print(f"  衰减速率: {report['decay_analysis']['decay_rate']}")
    print(f"  半衰期: {report['decay_analysis']['half_life']:.2f}天")
    print(f"\n拥挤度分析:")
    print(f"  拥挤度等级: {report['crowding_analysis']['crowding_level']}")
    print(f"  拥挤度评分: {report['crowding_analysis']['crowding_score']:.2%}")
    print(f"\n稳定性分析:")
    print(f"  稳定性评分: {report['stability_analysis']['stability_score']:.2%}")
    print(f"\n优化建议:")
    for rec in report['recommendations']:
        print(f"  - {rec}")

    print("\n" + "="*80)
    print("Markdown格式报告:")
    print("="*80)
    print(reporter.generate_report(signals, returns, market_data, signal_id="MOMENTUM_001", output_format="markdown"))
