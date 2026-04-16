"""
经济范式判断引擎主模块

实现了宏观经济周期识别和范式判断的核心功能。

模块ID: ECONOMIC_REGIME_ENGINE_001
版本: v1.0.0
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
import logging
import yaml
from pathlib import Path


class EconomicRegime(Enum):
    """经济范式枚举"""
    EXPANSION = "expansion"      # 扩张期：高增长 + 低通胀
    STAGFLATION = "stagflation"  # 滞胀期：低增长 + 高通胀
    RECESSION = "recession"      # 衰退期：低增长 + 低通胀
    RECOVERY = "recovery"        # 复苏期：高增长 + 高通胀（过渡期）


@dataclass
class RegimeAnalysis:
    """范式分析结果"""
    dominant_regime: EconomicRegime              # 主导范式
    probabilities: Dict[EconomicRegime, float]   # 范式概率分布
    confidence: float                             # 置信度
    recommended_assets: Dict[str, float]         # 推荐资产配置
    risk_level: str                              # 风险等级
    risk_warnings: List[str]                     # 风险预警
    timestamp: datetime                          # 时间戳
    metadata: Dict[str, Any]                     # 元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = asdict(self)
        result['dominant_regime'] = self.dominant_regime.value
        result['probabilities'] = {
            k.value: v for k, v in self.probabilities.items()
        }
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class MacroIndicators:
    """宏观经济指标"""
    gdp_growth: float        # GDP增长率
    cpi: float               # CPI通胀率
    ppi: float               # PPI通胀率
    pmi: float               # PMI景气度
    interest_rate: float     # 利率
    m2_growth: float         # M2增速
    credit_growth: float     # 信贷增速
    industrial_output: float # 工业增加值
    timestamp: datetime      # 时间戳

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class FeatureEngineer:
    """特征工程器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化特征工程器

        Args:
            config: 配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.config = config

    def extract_features(self, macro_data: MacroIndicators) -> pd.Series:
        """
        提取特征

        Args:
            macro_data: 宏观经济指标

        Returns:
            pd.Series: 特征向量
        """
        features = pd.Series()

        features['growth_score'] = self._calculate_growth_score(macro_data)
        features['inflation_score'] = self._calculate_inflation_score(macro_data)
        features['monetary_score'] = self._calculate_monetary_score(macro_data)
        features['momentum_score'] = self._calculate_momentum_score(macro_data)

        self.logger.info(f"特征提取完成: growth={features['growth_score']:.2f}, "
                         f"inflation={features['inflation_score']:.2f}")

        return features

    def _calculate_growth_score(self, macro_data: MacroIndicators) -> float:
        """计算增长评分"""
        indicators_config = self.config.get('indicators', {})

        gdp_config = indicators_config.get('gdp_growth', {})
        gdp_score = self._normalize(
            macro_data.gdp_growth,
            gdp_config.get('threshold_low', 5.0),
            gdp_config.get('threshold_high', 7.0)
        )

        pmi_config = indicators_config.get('pmi', {})
        pmi_score = self._normalize(
            macro_data.pmi,
            pmi_config.get('threshold_low', 48.0),
            pmi_config.get('threshold_high', 52.0)
        )

        industrial_config = indicators_config.get('industrial_output', {})
        industrial_score = self._normalize(
            macro_data.industrial_output,
            industrial_config.get('threshold_low', 5.0),
            industrial_config.get('threshold_high', 8.0)
        )

        gdp_weight = gdp_config.get('weight', 0.5)
        pmi_weight = pmi_config.get('weight', 0.3)
        industrial_weight = industrial_config.get('weight', 0.2)

        return (gdp_score * gdp_weight + pmi_score * pmi_weight +
                industrial_score * industrial_weight)

    def _calculate_inflation_score(self, macro_data: MacroIndicators) -> float:
        """计算通胀评分"""
        indicators_config = self.config.get('indicators', {})

        cpi_config = indicators_config.get('cpi', {})
        cpi_score = self._normalize(
            macro_data.cpi,
            cpi_config.get('threshold_low', 1.0),
            cpi_config.get('threshold_high', 3.0)
        )

        ppi_config = indicators_config.get('ppi', {})
        ppi_score = self._normalize(
            macro_data.ppi,
            ppi_config.get('threshold_low', -2.0),
            ppi_config.get('threshold_high', 2.0)
        )

        cpi_weight = cpi_config.get('weight', 0.7)
        ppi_weight = ppi_config.get('weight', 0.3)

        return cpi_score * cpi_weight + ppi_score * ppi_weight

    def _calculate_monetary_score(self, macro_data: MacroIndicators) -> float:
        """计算货币评分"""
        indicators_config = self.config.get('indicators', {})

        m2_config = indicators_config.get('m2_growth', {})
        m2_score = self._normalize(
            macro_data.m2_growth,
            m2_config.get('threshold_low', 8.0),
            m2_config.get('threshold_high', 12.0)
        )

        credit_config = indicators_config.get('credit_growth', {})
        credit_score = self._normalize(
            macro_data.credit_growth,
            credit_config.get('threshold_low', 10.0),
            credit_config.get('threshold_high', 15.0)
        )

        m2_weight = m2_config.get('weight', 0.5)
        credit_weight = credit_config.get('weight', 0.5)

        return m2_score * m2_weight + credit_score * credit_weight

    def _calculate_momentum_score(self, macro_data: MacroIndicators) -> float:
        """计算动量评分（简化版本）"""
        return 0.5

    def _normalize(self, value: float, low: float, high: float) -> float:
        """
        归一化到[0, 1]区间

        Args:
            value: 原始值
            low: 下限
            high: 上限

        Returns:
            float: 归一化后的值
        """
        if value >= high:
            return 1.0
        elif value <= low:
            return 0.0
        else:
            return (value - low) / (high - low)


class ExpansionRegimeModel:
    """扩张期模型"""

    def predict_probability(self, features: pd.Series) -> float:
        """
        预测扩张期概率

        Args:
            features: 特征向量

        Returns:
            float: 扩张期概率
        """
        growth_score = features['growth_score']
        inflation_score = features['inflation_score']

        if growth_score > 0.6 and inflation_score < 0.4:
            return 0.8
        elif growth_score > 0.5 and inflation_score < 0.5:
            return 0.6
        else:
            return 0.2


class StagflationRegimeModel:
    """滞胀期模型"""

    def predict_probability(self, features: pd.Series) -> float:
        """
        预测滞胀期概率

        Args:
            features: 特征向量

        Returns:
            float: 滞胀期概率
        """
        growth_score = features['growth_score']
        inflation_score = features['inflation_score']

        if growth_score < 0.4 and inflation_score > 0.6:
            return 0.8
        elif growth_score < 0.5 and inflation_score > 0.5:
            return 0.6
        else:
            return 0.2


class RecessionRegimeModel:
    """衰退期模型"""

    def predict_probability(self, features: pd.Series) -> float:
        """
        预测衰退期概率

        Args:
            features: 特征向量

        Returns:
            float: 衰退期概率
        """
        growth_score = features['growth_score']
        inflation_score = features['inflation_score']

        if growth_score < 0.4 and inflation_score < 0.4:
            return 0.8
        elif growth_score < 0.5 and inflation_score < 0.5:
            return 0.6
        else:
            return 0.2


class RecoveryRegimeModel:
    """复苏期模型"""

    def predict_probability(self, features: pd.Series) -> float:
        """
        预测复苏期概率

        Args:
            features: 特征向量

        Returns:
            float: 复苏期概率
        """
        growth_score = features['growth_score']
        inflation_score = features['inflation_score']

        if growth_score > 0.6 and inflation_score > 0.6:
            return 0.8
        elif growth_score > 0.5 and inflation_score > 0.5:
            return 0.6
        else:
            return 0.2


class AssetAllocationAdvisor:
    """资产配置建议器"""

    def __init__(self):
        """初始化资产配置建议器"""
        self.logger = logging.getLogger(__name__)

        self.regime_asset_mapping = {
            EconomicRegime.EXPANSION: {
                'equity': 0.60,      # 股票
                'bonds': 0.20,       # 债券
                'commodities': 0.15, # 商品
                'cash': 0.05         # 现金
            },
            EconomicRegime.STAGFLATION: {
                'equity': 0.20,
                'bonds': 0.15,
                'commodities': 0.50,  # 商品抗通胀
                'cash': 0.15
            },
            EconomicRegime.RECESSION: {
                'equity': 0.20,
                'bonds': 0.60,        # 债券避险
                'commodities': 0.05,
                'cash': 0.15
            },
            EconomicRegime.RECOVERY: {
                'equity': 0.50,
                'bonds': 0.25,
                'commodities': 0.20,
                'cash': 0.05
            }
        }

    def get_allocation_advice(self, regime: EconomicRegime) -> Dict[str, float]:
        """
        获取资产配置建议

        Args:
            regime: 经济范式

        Returns:
            Dict[str, float]: 资产配置建议
        """
        return self.regime_asset_mapping.get(
            regime,
            self.regime_asset_mapping[EconomicRegime.EXPANSION]
        )

    def adjust_for_probability(
        self,
        regime_probabilities: Dict[EconomicRegime, float]
    ) -> Dict[str, float]:
        """
        基于概率分布调整资产配置

        Args:
            regime_probabilities: 范式概率分布

        Returns:
            Dict[str, float]: 调整后的资产配置
        """
        weighted_allocation = {
            'equity': 0.0,
            'bonds': 0.0,
            'commodities': 0.0,
            'cash': 0.0
        }

        for regime, probability in regime_probabilities.items():
            regime_allocation = self.regime_asset_mapping[regime]
            for asset, weight in regime_allocation.items():
                weighted_allocation[asset] += weight * probability

        self.logger.info(f"资产配置建议: {weighted_allocation}")

        return weighted_allocation


class RiskWarner:
    """风险预警器"""

    def __init__(self):
        """初始化风险预警器"""
        self.logger = logging.getLogger(__name__)

        self.regime_risk_mapping = {
            EconomicRegime.EXPANSION: {
                'level': '低风险',
                'warnings': []
            },
            EconomicRegime.STAGFLATION: {
                'level': '高风险',
                'warnings': [
                    '经济滞胀风险上升，建议增加商品配置',
                    '通胀压力较大，注意债券风险',
                    '增长动力不足，警惕企业盈利下滑'
                ]
            },
            EconomicRegime.RECESSION: {
                'level': '中高风险',
                'warnings': [
                    '经济衰退风险，建议增加债券配置',
                    '企业盈利可能下滑，注意股票风险',
                    '货币政策可能宽松，关注利率变化'
                ]
            },
            EconomicRegime.RECOVERY: {
                'level': '中低风险',
                'warnings': [
                    '经济复苏初期，注意通胀压力',
                    '政策可能收紧，关注利率风险'
                ]
            }
        }

    def generate_warnings(
        self,
        dominant_regime: EconomicRegime,
        regime_probabilities: Dict[EconomicRegime, float]
    ) -> List[str]:
        """
        生成风险预警

        Args:
            dominant_regime: 主导范式
            regime_probabilities: 范式概率分布

        Returns:
            List[str]: 风险预警列表
        """
        warnings = []

        regime_info = self.regime_risk_mapping.get(
            dominant_regime,
            {'warnings': []}
        )
        warnings.extend(regime_info.get('warnings', []))

        if regime_probabilities.get(EconomicRegime.STAGFLATION, 0) > 0.3:
            warnings.append('滞胀概率较高，建议密切关注通胀数据')

        if regime_probabilities.get(EconomicRegime.RECESSION, 0) > 0.3:
            warnings.append('衰退概率较高，建议增加防御性资产')

        self.logger.info(f"生成风险预警: {len(warnings)}条")

        return warnings


class EconomicRegimeEngine:
    """经济范式判断引擎"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化经济范式判断引擎

        Args:
            config_path: 配置文件路径
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化经济范式判断引擎")

        self.config = self._load_config(config_path)

        self.macro_indicators = {
            'growth': ['gdp_growth', 'industrial_output', 'pmi'],
            'inflation': ['cpi', 'ppi'],
            'monetary': ['m2_growth', 'interest_rate', 'credit_growth']
        }

        self.regime_models = {
            EconomicRegime.EXPANSION: ExpansionRegimeModel(),
            EconomicRegime.STAGFLATION: StagflationRegimeModel(),
            EconomicRegime.RECESSION: RecessionRegimeModel(),
            EconomicRegime.RECOVERY: RecoveryRegimeModel()
        }

        self.feature_engineer = FeatureEngineer(self.config)
        self.asset_allocator = AssetAllocationAdvisor()
        self.risk_warner = RiskWarner()

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            Dict[str, Any]: 配置参数
        """
        if config_path is None:
            config_path = Path(__file__).parent / 'config' / 'economic_regime_config.yaml'

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.logger.info(f"配置文件加载成功: {config_path}")
                return config
        except Exception as e:
            self.logger.warning(f"配置文件加载失败，使用默认配置: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'update_frequency': 'daily',
            'indicators': {
                'gdp_growth': {
                    'threshold_high': 7.0,
                    'threshold_low': 5.0,
                    'weight': 0.5
                },
                'cpi': {
                    'threshold_high': 3.0,
                    'threshold_low': 1.0,
                    'weight': 0.7
                },
                'pmi': {
                    'threshold_high': 52.0,
                    'threshold_low': 48.0,
                    'weight': 0.3
                }
            }
        }

    def analyze_current_regime(self, macro_data: Optional[MacroIndicators] = None) -> RegimeAnalysis:
        """
        分析当前经济范式

        Args:
            macro_data: 宏观经济指标（可选，如果不提供则自动采集）

        Returns:
            RegimeAnalysis: 范式分析结果
        """
        self.logger.info("开始分析当前经济范式")

        if macro_data is None:
            macro_data = self._collect_macro_data()

        features = self.feature_engineer.extract_features(macro_data)

        regime_probabilities = {}
        for regime, model in self.regime_models.items():
            probability = model.predict_probability(features)
            regime_probabilities[regime] = probability

        regime_probabilities = self._normalize_probabilities(regime_probabilities)

        dominant_regime = max(regime_probabilities, key=regime_probabilities.get)

        confidence = self._calculate_confidence(regime_probabilities)

        asset_allocation = self.asset_allocator.adjust_for_probability(regime_probabilities)

        risk_warnings = self.risk_warner.generate_warnings(
            dominant_regime,
            regime_probabilities
        )

        analysis = RegimeAnalysis(
            dominant_regime=dominant_regime,
            probabilities=regime_probabilities,
            confidence=confidence,
            recommended_assets=asset_allocation,
            risk_level=self._assess_risk_level(dominant_regime),
            risk_warnings=risk_warnings,
            timestamp=datetime.now(),
            metadata={'features': features.to_dict()}
        )

        self.logger.info(f"经济范式分析完成: {dominant_regime.value}, "
                        f"置信度={confidence:.2f}")

        return analysis

    def get_regime_probability(self) -> Dict[EconomicRegime, float]:
        """
        获取范式概率分布

        Returns:
            Dict[EconomicRegime, float]: 范式概率分布
        """
        analysis = self.analyze_current_regime()
        return analysis.probabilities

    def get_asset_allocation(self) -> Dict[str, float]:
        """
        获取资产配置建议

        Returns:
            Dict[str, float]: 资产配置建议
        """
        analysis = self.analyze_current_regime()
        return analysis.recommended_assets

    def get_risk_warnings(self) -> List[str]:
        """
        获取风险预警

        Returns:
            List[str]: 风险预警列表
        """
        analysis = self.analyze_current_regime()
        return analysis.risk_warnings

    def _collect_macro_data(self) -> MacroIndicators:
        """
        收集宏观经济数据（模拟数据）

        Returns:
            MacroIndicators: 宏观经济指标
        """
        self.logger.info("收集宏观经济数据（使用模拟数据）")

        return MacroIndicators(
            gdp_growth=6.5,
            cpi=2.3,
            ppi=1.5,
            pmi=51.2,
            interest_rate=3.5,
            m2_growth=10.5,
            credit_growth=12.8,
            industrial_output=6.8,
            timestamp=datetime.now()
        )

    def _normalize_probabilities(
        self,
        probabilities: Dict[EconomicRegime, float]
    ) -> Dict[EconomicRegime, float]:
        """
        归一化概率分布

        Args:
            probabilities: 原始概率

        Returns:
            Dict[EconomicRegime, float]: 归一化后的概率
        """
        total = sum(probabilities.values())
        if total == 0:
            return {regime: 0.25 for regime in EconomicRegime}

        return {regime: prob / total for regime, prob in probabilities.items()}

    def _calculate_confidence(
        self,
        probabilities: Dict[EconomicRegime, float]
    ) -> float:
        """
        计算置信度

        Args:
            probabilities: 概率分布

        Returns:
            float: 置信度
        """
        sorted_probs = sorted(probabilities.values(), reverse=True)
        if len(sorted_probs) < 2:
            return 0.0
        return sorted_probs[0] - sorted_probs[1]

    def _assess_risk_level(self, regime: EconomicRegime) -> str:
        """
        评估风险等级

        Args:
            regime: 经济范式

        Returns:
            str: 风险等级
        """
        risk_mapping = {
            EconomicRegime.EXPANSION: "低风险",
            EconomicRegime.RECOVERY: "中低风险",
            EconomicRegime.STAGFLATION: "高风险",
            EconomicRegime.RECESSION: "中高风险"
        }
        return risk_mapping.get(regime, "中风险")
