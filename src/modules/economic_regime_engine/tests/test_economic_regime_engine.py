"""
经济范式判断引擎单元测试

测试经济范式判断引擎的核心功能。

模块ID: ECONOMIC_REGIME_ENGINE_001
版本: v1.0.0
"""

import unittest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from economic_regime_engine import (
    EconomicRegime,
    RegimeAnalysis,
    MacroIndicators,
    EconomicRegimeEngine,
    FeatureEngineer,
    ExpansionRegimeModel,
    StagflationRegimeModel,
    RecessionRegimeModel,
    RecoveryRegimeModel,
    AssetAllocationAdvisor,
    RiskWarner
)


class TestEconomicRegimeEnum(unittest.TestCase):
    """测试经济范式枚举"""

    def test_regime_values(self):
        """测试范式枚举值"""
        self.assertEqual(EconomicRegime.EXPANSION.value, "expansion")
        self.assertEqual(EconomicRegime.STAGFLATION.value, "stagflation")
        self.assertEqual(EconomicRegime.RECESSION.value, "recession")
        self.assertEqual(EconomicRegime.RECOVERY.value, "recovery")

    def test_regime_count(self):
        """测试范式数量"""
        self.assertEqual(len(EconomicRegime), 4)


class TestMacroIndicators(unittest.TestCase):
    """测试宏观经济指标"""

    def test_macro_indicators_creation(self):
        """测试宏观经济指标创建"""
        macro_data = MacroIndicators(
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

        self.assertEqual(macro_data.gdp_growth, 6.5)
        self.assertEqual(macro_data.cpi, 2.3)
        self.assertEqual(macro_data.pmi, 51.2)

    def test_macro_indicators_to_dict(self):
        """测试宏观经济指标转换为字典"""
        macro_data = MacroIndicators(
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

        result = macro_data.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result['gdp_growth'], 6.5)
        self.assertEqual(result['cpi'], 2.3)


class TestFeatureEngineer(unittest.TestCase):
    """测试特征工程器"""

    def setUp(self):
        """设置测试环境"""
        self.config = {
            'indicators': {
                'gdp_growth': {'threshold_high': 7.0, 'threshold_low': 5.0, 'weight': 0.5},
                'cpi': {'threshold_high': 3.0, 'threshold_low': 1.0, 'weight': 0.7},
                'pmi': {'threshold_high': 52.0, 'threshold_low': 48.0, 'weight': 0.3},
                'ppi': {'threshold_high': 2.0, 'threshold_low': -2.0, 'weight': 0.3},
                'industrial_output': {'threshold_high': 8.0, 'threshold_low': 5.0, 'weight': 0.2},
                'm2_growth': {'threshold_high': 12.0, 'threshold_low': 8.0, 'weight': 0.5},
                'credit_growth': {'threshold_high': 15.0, 'threshold_low': 10.0, 'weight': 0.5}
            }
        }
        self.feature_engineer = FeatureEngineer(self.config)

    def test_extract_features(self):
        """测试特征提取"""
        macro_data = MacroIndicators(
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

        features = self.feature_engineer.extract_features(macro_data)

        self.assertIn('growth_score', features)
        self.assertIn('inflation_score', features)
        self.assertIn('monetary_score', features)
        self.assertIn('momentum_score', features)

        self.assertGreaterEqual(features['growth_score'], 0.0)
        self.assertLessEqual(features['growth_score'], 1.0)

    def test_normalize(self):
        """测试归一化函数"""
        result = self.feature_engineer._normalize(6.0, 5.0, 7.0)
        self.assertEqual(result, 0.5)

        result = self.feature_engineer._normalize(8.0, 5.0, 7.0)
        self.assertEqual(result, 1.0)

        result = self.feature_engineer._normalize(4.0, 5.0, 7.0)
        self.assertEqual(result, 0.0)


class TestRegimeModels(unittest.TestCase):
    """测试范式识别模型"""

    def test_expansion_model(self):
        """测试扩张期模型"""
        import pandas as pd

        model = ExpansionRegimeModel()

        features_high_growth_low_inflation = pd.Series({
            'growth_score': 0.7,
            'inflation_score': 0.3
        })
        prob = model.predict_probability(features_high_growth_low_inflation)
        self.assertEqual(prob, 0.8)

        features_medium = pd.Series({
            'growth_score': 0.55,
            'inflation_score': 0.45
        })
        prob = model.predict_probability(features_medium)
        self.assertEqual(prob, 0.6)

    def test_stagflation_model(self):
        """测试滞胀期模型"""
        import pandas as pd

        model = StagflationRegimeModel()

        features_low_growth_high_inflation = pd.Series({
            'growth_score': 0.3,
            'inflation_score': 0.7
        })
        prob = model.predict_probability(features_low_growth_high_inflation)
        self.assertEqual(prob, 0.8)

    def test_recession_model(self):
        """测试衰退期模型"""
        import pandas as pd

        model = RecessionRegimeModel()

        features_low_growth_low_inflation = pd.Series({
            'growth_score': 0.3,
            'inflation_score': 0.3
        })
        prob = model.predict_probability(features_low_growth_low_inflation)
        self.assertEqual(prob, 0.8)

    def test_recovery_model(self):
        """测试复苏期模型"""
        import pandas as pd

        model = RecoveryRegimeModel()

        features_high_growth_high_inflation = pd.Series({
            'growth_score': 0.7,
            'inflation_score': 0.7
        })
        prob = model.predict_probability(features_high_growth_high_inflation)
        self.assertEqual(prob, 0.8)


class TestAssetAllocationAdvisor(unittest.TestCase):
    """测试资产配置建议器"""

    def setUp(self):
        """设置测试环境"""
        self.advisor = AssetAllocationAdvisor()

    def test_get_allocation_advice(self):
        """测试获取资产配置建议"""
        allocation = self.advisor.get_allocation_advice(EconomicRegime.EXPANSION)

        self.assertEqual(allocation['equity'], 0.60)
        self.assertEqual(allocation['bonds'], 0.20)
        self.assertEqual(allocation['commodities'], 0.15)
        self.assertEqual(allocation['cash'], 0.05)

    def test_adjust_for_probability(self):
        """测试基于概率调整资产配置"""
        probabilities = {
            EconomicRegime.EXPANSION: 0.6,
            EconomicRegime.STAGFLATION: 0.2,
            EconomicRegime.RECESSION: 0.1,
            EconomicRegime.RECOVERY: 0.1
        }

        allocation = self.advisor.adjust_for_probability(probabilities)

        self.assertIn('equity', allocation)
        self.assertIn('bonds', allocation)
        self.assertIn('commodities', allocation)
        self.assertIn('cash', allocation)


class TestRiskWarner(unittest.TestCase):
    """测试风险预警器"""

    def setUp(self):
        """设置测试环境"""
        self.warner = RiskWarner()

    def test_generate_warnings_stagflation(self):
        """测试滞胀期风险预警"""
        probabilities = {
            EconomicRegime.EXPANSION: 0.1,
            EconomicRegime.STAGFLATION: 0.7,
            EconomicRegime.RECESSION: 0.1,
            EconomicRegime.RECOVERY: 0.1
        }

        warnings = self.warner.generate_warnings(
            EconomicRegime.STAGFLATION,
            probabilities
        )

        self.assertGreater(len(warnings), 0)

    def test_generate_warnings_recession(self):
        """测试衰退期风险预警"""
        probabilities = {
            EconomicRegime.EXPANSION: 0.1,
            EconomicRegime.STAGFLATION: 0.1,
            EconomicRegime.RECESSION: 0.7,
            EconomicRegime.RECOVERY: 0.1
        }

        warnings = self.warner.generate_warnings(
            EconomicRegime.RECESSION,
            probabilities
        )

        self.assertGreater(len(warnings), 0)


class TestEconomicRegimeEngine(unittest.TestCase):
    """测试经济范式判断引擎"""

    def setUp(self):
        """设置测试环境"""
        self.engine = EconomicRegimeEngine()

    def test_analyze_current_regime(self):
        """测试分析当前经济范式"""
        analysis = self.engine.analyze_current_regime()

        self.assertIsInstance(analysis, RegimeAnalysis)
        self.assertIn(analysis.dominant_regime, EconomicRegime)
        self.assertGreater(analysis.confidence, 0.0)
        self.assertLessEqual(analysis.confidence, 1.0)

    def test_get_regime_probability(self):
        """测试获取范式概率分布"""
        probabilities = self.engine.get_regime_probability()

        self.assertEqual(len(probabilities), 4)

        total_prob = sum(probabilities.values())
        self.assertAlmostEqual(total_prob, 1.0, places=2)

    def test_get_asset_allocation(self):
        """测试获取资产配置建议"""
        allocation = self.engine.get_asset_allocation()

        self.assertIn('equity', allocation)
        self.assertIn('bonds', allocation)
        self.assertIn('commodities', allocation)
        self.assertIn('cash', allocation)

        total_weight = sum(allocation.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)

    def test_get_risk_warnings(self):
        """测试获取风险预警"""
        warnings = self.engine.get_risk_warnings()

        self.assertIsInstance(warnings, list)

    def test_custom_macro_data(self):
        """测试自定义宏观数据"""
        custom_macro_data = MacroIndicators(
            gdp_growth=5.5,
            cpi=4.2,
            ppi=3.5,
            pmi=48.5,
            interest_rate=3.5,
            m2_growth=8.5,
            credit_growth=10.2,
            industrial_output=5.0,
            timestamp=datetime.now()
        )

        analysis = self.engine.analyze_current_regime(custom_macro_data)

        self.assertIsInstance(analysis, RegimeAnalysis)

    def test_normalize_probabilities(self):
        """测试概率归一化"""
        probabilities = {
            EconomicRegime.EXPANSION: 0.8,
            EconomicRegime.STAGFLATION: 0.8,
            EconomicRegime.RECESSION: 0.8,
            EconomicRegime.RECOVERY: 0.8
        }

        normalized = self.engine._normalize_probabilities(probabilities)

        total = sum(normalized.values())
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_calculate_confidence(self):
        """测试置信度计算"""
        probabilities = {
            EconomicRegime.EXPANSION: 0.6,
            EconomicRegime.STAGFLATION: 0.2,
            EconomicRegime.RECESSION: 0.1,
            EconomicRegime.RECOVERY: 0.1
        }

        confidence = self.engine._calculate_confidence(probabilities)

        self.assertEqual(confidence, 0.4)


class TestRegimeAnalysis(unittest.TestCase):
    """测试范式分析结果"""

    def test_regime_analysis_to_dict(self):
        """测试范式分析结果转换为字典"""
        analysis = RegimeAnalysis(
            dominant_regime=EconomicRegime.EXPANSION,
            probabilities={
                EconomicRegime.EXPANSION: 0.6,
                EconomicRegime.STAGFLATION: 0.2,
                EconomicRegime.RECESSION: 0.1,
                EconomicRegime.RECOVERY: 0.1
            },
            confidence=0.4,
            recommended_assets={
                'equity': 0.55,
                'bonds': 0.22,
                'commodities': 0.18,
                'cash': 0.05
            },
            risk_level='低风险',
            risk_warnings=[],
            timestamp=datetime.now(),
            metadata={}
        )

        result = analysis.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result['dominant_regime'], 'expansion')
        self.assertIn('expansion', result['probabilities'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
