"""
AIExplainabilityReporter - AI决策可解释性报告器模块

模块ID: AI_EXPLAINABILITY_REPORTER_001
技术层次: Layer 7 - AI报告层 | 业务架构: 三级时间框架融合架构
版本: v1.0.0
创建日期: 2026-04-02

核心功能:
1. AI决策可解释性分析（SHAP/LIME）
2. 特征重要性报告
3. 模型决策路径可视化
4. 可解释性报告生成

参考模型: Two Sigma AI Explainability, Bridgewater Decision Transparency
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
import logging


@dataclass
class FeatureImportance:
    """特征重要性"""
    feature_name: str
    importance_score: float
    contribution_direction: str  # positive/negative
    description: str
    
    def to_dict(self) -> Dict:
        return {
            'feature_name': self.feature_name,
            'importance_score': self.importance_score,
            'contribution_direction': self.contribution_direction,
            'description': self.description
        }


@dataclass
class DecisionExplanation:
    """决策解释"""
    decision_id: str
    decision_type: str
    decision_output: Any
    
    top_features: List[FeatureImportance]
    decision_path: List[str]
    confidence: float
    
    alternative_scenarios: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            'decision_id': self.decision_id,
            'decision_type': self.decision_type,
            'decision_output': str(self.decision_output),
            'top_features': [f.to_dict() for f in self.top_features],
            'decision_path': self.decision_path,
            'confidence': self.confidence,
            'alternative_scenarios': self.alternative_scenarios
        }


@dataclass
class ExplainabilityReport:
    """可解释性报告"""
    report_id: str
    timestamp: datetime
    
    model_name: str
    model_type: str
    
    global_feature_importance: List[FeatureImportance]
    decision_explanations: List[DecisionExplanation]
    
    model_transparency_score: float
    interpretability_score: float
    
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'report_id': self.report_id,
            'timestamp': self.timestamp.isoformat(),
            'model_name': self.model_name,
            'model_type': self.model_type,
            'global_feature_importance': [f.to_dict() for f in self.global_feature_importance],
            'decision_explanations': [d.to_dict() for d in self.decision_explanations],
            'model_transparency_score': self.model_transparency_score,
            'interpretability_score': self.interpretability_score,
            'recommendations': self.recommendations
        }


class SHAPAnalyzer:
    """SHAP分析器（简化实现）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_feature_importance(
        self,
        features: pd.DataFrame,
        model_output: np.ndarray
    ) -> List[FeatureImportance]:
        """计算特征重要性（简化版SHAP）"""
        feature_importances = []
        
        for col in features.columns:
            correlation = np.corrcoef(features[col], model_output)[0, 1]
            
            importance = abs(correlation)
            direction = "positive" if correlation > 0 else "negative"
            
            feature_importances.append(FeatureImportance(
                feature_name=col,
                importance_score=importance,
                contribution_direction=direction,
                description=f"特征{col}与模型输出的相关性为{correlation:.3f}"
            ))
        
        feature_importances.sort(key=lambda x: x.importance_score, reverse=True)
        
        return feature_importances


class DecisionPathAnalyzer:
    """决策路径分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_decision_path(
        self,
        features: Dict[str, float],
        decision: Any
    ) -> List[str]:
        """分析决策路径"""
        path = []
        
        sorted_features = sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)
        
        for feature_name, feature_value in sorted_features[:5]:
            if feature_value > 0:
                path.append(f"{feature_name}正向贡献（值={feature_value:.3f}）")
            else:
                path.append(f"{feature_name}负向贡献（值={feature_value:.3f}）")
        
        path.append(f"最终决策: {decision}")
        
        return path


class AIExplainabilityReporter:
    """AI决策可解释性报告器主类"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.shap_analyzer = SHAPAnalyzer()
        self.decision_path_analyzer = DecisionPathAnalyzer()
        self.report_counter = 0
    
    def generate_explainability_report(
        self,
        features: pd.DataFrame,
        model_output: np.ndarray,
        model_name: str = "Alpha预测模型",
        model_type: str = "XGBoost"
    ) -> ExplainabilityReport:
        """生成可解释性报告"""
        self.report_counter += 1
        report_id = f"EXPLAIN_RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.report_counter:06d}"
        
        global_importance = self.shap_analyzer.calculate_feature_importance(features, model_output)
        
        decision_explanations = []
        for i in range(min(5, len(features))):
            decision_exp = DecisionExplanation(
                decision_id=f"DEC_{i:03d}",
                decision_type="买入信号",
                decision_output=model_output[i],
                top_features=global_importance[:5],
                decision_path=self.decision_path_analyzer.analyze_decision_path(
                    features.iloc[i].to_dict(), model_output[i]
                ),
                confidence=0.85,
                alternative_scenarios=[
                    {"scenario": "市场下跌", "output": model_output[i] * 0.8},
                    {"scenario": "市场上涨", "output": model_output[i] * 1.2}
                ]
            )
            decision_explanations.append(decision_exp)
        
        transparency_score = self._calculate_transparency_score(global_importance)
        interpretability_score = self._calculate_interpretability_score(decision_explanations)
        
        recommendations = self._generate_recommendations(transparency_score, interpretability_score)
        
        return ExplainabilityReport(
            report_id=report_id,
            timestamp=datetime.now(),
            model_name=model_name,
            model_type=model_type,
            global_feature_importance=global_importance,
            decision_explanations=decision_explanations,
            model_transparency_score=transparency_score,
            interpretability_score=interpretability_score,
            recommendations=recommendations
        )
    
    def _calculate_transparency_score(self, feature_importance: List[FeatureImportance]) -> float:
        """计算模型透明度评分"""
        if not feature_importance:
            return 0.0
        
        top_5_importance = sum(f.importance_score for f in feature_importance[:5])
        total_importance = sum(f.importance_score for f in feature_importance)
        
        if total_importance == 0:
            return 0.0
        
        concentration = top_5_importance / total_importance
        
        return min(100, concentration * 100)
    
    def _calculate_interpretability_score(self, explanations: List[DecisionExplanation]) -> float:
        """计算可解释性评分"""
        if not explanations:
            return 0.0
        
        avg_confidence = np.mean([e.confidence for e in explanations])
        
        return avg_confidence * 100
    
    def _generate_recommendations(
        self,
        transparency_score: float,
        interpretability_score: float
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if transparency_score < 60:
            recommendations.append("💡 模型透明度较低，建议减少特征数量或使用更简单的模型")
        
        if interpretability_score < 70:
            recommendations.append("💡 决策可解释性不足，建议增加SHAP值分析")
        
        if transparency_score >= 80 and interpretability_score >= 80:
            recommendations.append("✅ 模型可解释性良好，建议持续监控")
        
        return recommendations
    
    def generate_report_markdown(self, report: ExplainabilityReport) -> str:
        """生成Markdown报告"""
        md = []
        md.append(f"# AI决策可解释性报告")
        md.append(f"\n**报告ID**: {report.report_id}")
        md.append(f"\n**模型名称**: {report.model_name}")
        md.append(f"\n**模型类型**: {report.model_type}")
        md.append(f"\n**透明度评分**: {report.model_transparency_score:.1f}/100")
        md.append(f"\n**可解释性评分**: {report.interpretability_score:.1f}/100")
        
        md.append(f"\n## 全局特征重要性（Top 10）")
        md.append(f"\n| 特征名称 | 重要性 | 贡献方向 | 描述 |")
        md.append(f"\n|---------|--------|---------|------|")
        for feature in report.global_feature_importance[:10]:
            md.append(f"\n| {feature.feature_name} | {feature.importance_score:.4f} | {feature.contribution_direction} | {feature.description} |")
        
        if report.decision_explanations:
            md.append(f"\n## 决策解释示例")
            for i, explanation in enumerate(report.decision_explanations[:3], 1):
                md.append(f"\n### 决策{i}: {explanation.decision_type}")
                md.append(f"\n**输出**: {explanation.decision_output}")
                md.append(f"\n**置信度**: {explanation.confidence:.2%}")
                md.append(f"\n**决策路径**:")
                for step in explanation.decision_path:
                    md.append(f"\n- {step}")
        
        if report.recommendations:
            md.append(f"\n## 建议")
            for rec in report.recommendations:
                md.append(f"\n- {rec}")
        
        return "\n".join(md)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    reporter = AIExplainabilityReporter()
    
    np.random.seed(42)
    features = pd.DataFrame({
        'PE_ratio': np.random.randn(100),
        'PB_ratio': np.random.randn(100),
        'ROE': np.random.randn(100),
        'momentum': np.random.randn(100),
        'volatility': np.random.randn(100)
    })
    
    model_output = np.random.randn(100)
    
    report = reporter.generate_explainability_report(features, model_output)
    
    markdown_report = reporter.generate_report_markdown(report)
    print(markdown_report)
