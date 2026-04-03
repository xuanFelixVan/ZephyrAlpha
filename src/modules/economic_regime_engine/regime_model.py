"""
经济范式判断引擎 - 随机森林模型模块

实现基于随机森林的经济周期识别模型。

模块ID: ECONOMIC_REGIME_ENGINE_002
版本: v2.0.0
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import json
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report,
    confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns


class EconomicRegime(Enum):
    """经济范式枚举"""
    EXPANSION = 0      # 扩张期：高增长 + 低通胀
    STAGFLATION = 1    # 滞胀期：低增长 + 高通胀
    RECESSION = 2      # 衰退期：低增长 + 低通胀
    RECOVERY = 3       # 复苏期：高增长 + 高通胀（过渡期）


@dataclass
class ModelPerformance:
    """模型性能指标"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    cv_scores: List[float]
    feature_importance: Dict[str, float]
    confusion_matrix: List[List[int]]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


class FeatureEngineer:
    """特征工程器"""
    
    FEATURE_NAMES = [
        'gdp_growth',
        'cpi',
        'ppi',
        'pmi',
        'interest_rate',
        'm2_growth',
        'credit_growth',
        'industrial_output',
        'growth_momentum',
        'inflation_momentum',
        'monetary_momentum'
    ]
    
    def __init__(self):
        """初始化特征工程器"""
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        提取特征
        
        Args:
            df: 原始宏观经济数据
            
        Returns:
            DataFrame: 特征数据
        """
        self.logger.info("开始特征提取")
        
        features = df.copy()
        
        features['growth_momentum'] = features['gdp_growth'].pct_change()
        features['inflation_momentum'] = features['cpi'].pct_change()
        features['monetary_momentum'] = features['m2_growth'].pct_change()
        
        features = features.fillna(method='ffill').fillna(method='bfill')
        
        features = features.replace([np.inf, -np.inf], np.nan)
        features = features.fillna(0)
        
        self.logger.info(f"特征提取完成: {features.shape}")
        
        return features
    
    def normalize_features(self, features: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        标准化特征
        
        Args:
            features: 特征数据
            fit: 是否拟合scaler
            
        Returns:
            DataFrame: 标准化后的特征
        """
        if fit:
            normalized = self.scaler.fit_transform(features)
        else:
            normalized = self.scaler.transform(features)
        
        return pd.DataFrame(normalized, index=features.index, columns=features.columns)
    
    def get_feature_importance(self, model: RandomForestClassifier) -> Dict[str, float]:
        """
        获取特征重要性
        
        Args:
            model: 随机森林模型
            
        Returns:
            Dict[str, float]: 特征重要性字典
        """
        importance = model.feature_importances_
        feature_importance = dict(zip(self.FEATURE_NAMES, importance))
        
        sorted_importance = dict(sorted(
            feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        return sorted_importance


class LabelGenerator:
    """标签生成器"""
    
    def __init__(self):
        """初始化标签生成器"""
        self.logger = logging.getLogger(__name__)
        
    def generate_labels(self, df: pd.DataFrame) -> pd.Series:
        """
        生成经济范式标签
        
        Args:
            df: 宏观经济数据
            
        Returns:
            Series: 经济范式标签
        """
        self.logger.info("开始生成经济范式标签")
        
        labels = []
        
        for idx, row in df.iterrows():
            gdp_growth = row.get('gdp_growth', 6.5)
            cpi = row.get('cpi', 2.5)
            
            if gdp_growth > 6.5 and cpi < 3.0:
                label = EconomicRegime.EXPANSION.value
            elif gdp_growth < 5.5 and cpi > 3.5:
                label = EconomicRegime.STAGFLATION.value
            elif gdp_growth < 5.5 and cpi < 2.0:
                label = EconomicRegime.RECESSION.value
            elif gdp_growth > 6.0 and cpi > 3.0:
                label = EconomicRegime.RECOVERY.value
            else:
                if gdp_growth > 6.0:
                    label = EconomicRegime.EXPANSION.value
                elif cpi > 3.0:
                    label = EconomicRegime.STAGFLATION.value
                else:
                    label = EconomicRegime.RECESSION.value
            
            labels.append(label)
        
        labels_series = pd.Series(labels, index=df.index)
        
        label_counts = labels_series.value_counts()
        self.logger.info(f"标签分布:\n{label_counts}")
        
        return labels_series


class EconomicRegimeModel:
    """经济范式识别模型"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化经济范式识别模型
        
        Args:
            model_path: 模型文件路径
        """
        self.logger = logging.getLogger(__name__)
        self.feature_engineer = FeatureEngineer()
        self.label_generator = LabelGenerator()
        
        self.model = None
        self.scaler = None
        
        if model_path:
            self.load_model(model_path)
        
    def train(self, 
              df: pd.DataFrame,
              test_size: float = 0.2,
              random_state: int = 42,
              optimize: bool = False) -> ModelPerformance:
        """
        训练随机森林模型
        
        Args:
            df: 宏观经济数据
            test_size: 测试集比例
            random_state: 随机种子
            optimize: 是否进行参数优化
            
        Returns:
            ModelPerformance: 模型性能指标
        """
        self.logger.info("开始训练随机森林模型")
        
        features = self.feature_engineer.extract_features(df)
        labels = self.label_generator.generate_labels(df)
        
        features_normalized = self.feature_engineer.normalize_features(features, fit=True)
        
        X_train, X_test, y_train, y_test = train_test_split(
            features_normalized, 
            labels, 
            test_size=test_size, 
            random_state=random_state,
            stratify=labels
        )
        
        if optimize:
            self.model = self._optimize_hyperparameters(X_train, y_train)
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features='sqrt',
                random_state=random_state,
                n_jobs=-1,
                class_weight='balanced'
            )
            
            self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        cv_scores = cross_val_score(self.model, features_normalized, labels, cv=5)
        
        feature_importance = self.feature_engineer.get_feature_importance(self.model)
        
        cm = confusion_matrix(y_test, y_pred)
        
        performance = ModelPerformance(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            cv_scores=cv_scores.tolist(),
            feature_importance=feature_importance,
            confusion_matrix=cm.tolist()
        )
        
        self.logger.info(f"模型训练完成:")
        self.logger.info(f"  准确率: {accuracy:.4f}")
        self.logger.info(f"  精确率: {precision:.4f}")
        self.logger.info(f"  召回率: {recall:.4f}")
        self.logger.info(f"  F1分数: {f1:.4f}")
        self.logger.info(f"  交叉验证: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        return performance
    
    def _optimize_hyperparameters(self, X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
        """
        优化超参数
        
        Args:
            X_train: 训练特征
            y_train: 训练标签
            
        Returns:
            RandomForestClassifier: 优化后的模型
        """
        self.logger.info("开始超参数优化")
        
        param_grid = {
            'n_estimators': [50, 100, 150],
            'max_depth': [5, 10, 15],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2']
        }
        
        rf = RandomForestClassifier(random_state=42, n_jobs=-1, class_weight='balanced')
        
        grid_search = GridSearchCV(
            estimator=rf,
            param_grid=param_grid,
            cv=3,
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        self.logger.info(f"最佳参数: {grid_search.best_params_}")
        self.logger.info(f"最佳得分: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        预测经济范式
        
        Args:
            df: 宏观经济数据
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: 预测标签和概率
        """
        if self.model is None:
            raise ValueError("模型未训练，请先调用train()方法")
        
        features = self.feature_engineer.extract_features(df)
        features_normalized = self.feature_engineer.normalize_features(features, fit=False)
        
        predictions = self.model.predict(features_normalized)
        probabilities = self.model.predict_proba(features_normalized)
        
        return predictions, probabilities
    
    def predict_current_regime(self, current_data: Dict[str, float]) -> Tuple[EconomicRegime, float]:
        """
        预测当前经济范式
        
        Args:
            current_data: 当前宏观经济数据
            
        Returns:
            Tuple[EconomicRegime, float]: 经济范式和置信度
        """
        df = pd.DataFrame([current_data])
        
        predictions, probabilities = self.predict(df)
        
        regime = EconomicRegime(predictions[0])
        confidence = probabilities[0].max()
        
        return regime, confidence
    
    def save_model(self, model_path: str):
        """
        保存模型
        
        Args:
            model_path: 模型文件路径
        """
        model_dir = Path(model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.feature_engineer.scaler
        }
        
        joblib.dump(model_data, model_path)
        
        self.logger.info(f"模型已保存: {model_path}")
        
    def load_model(self, model_path: str):
        """
        加载模型
        
        Args:
            model_path: 模型文件路径
        """
        model_data = joblib.load(model_path)
        
        self.model = model_data['model']
        self.feature_engineer.scaler = model_data['scaler']
        
        self.logger.info(f"模型已加载: {model_path}")
    
    def plot_feature_importance(self, save_path: Optional[str] = None):
        """
        绘制特征重要性图
        
        Args:
            save_path: 图片保存路径
        """
        if self.model is None:
            raise ValueError("模型未训练")
        
        feature_importance = self.feature_engineer.get_feature_importance(self.model)
        
        plt.figure(figsize=(10, 6))
        plt.barh(list(feature_importance.keys()), list(feature_importance.values()))
        plt.xlabel('Feature Importance')
        plt.ylabel('Feature Name')
        plt.title('Feature Importance for Economic Regime Classification')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"特征重要性图已保存: {save_path}")
        
        plt.show()
    
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray, save_path: Optional[str] = None):
        """
        绘制混淆矩阵
        
        Args:
            y_true: 真实标签
            y_pred: 预测标签
            save_path: 图片保存路径
        """
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=[regime.name for regime in EconomicRegime],
                   yticklabels=[regime.name for regime in EconomicRegime])
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.title('Confusion Matrix for Economic Regime Classification')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"混淆矩阵图已保存: {save_path}")
        
        plt.show()


def main():
    """主函数 - 模型训练示例"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    from data_collector import MacroDataManager
    
    manager = MacroDataManager(use_mock_data=True)
    
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    df = manager.collect_all_indicators(start_date, end_date, save_to_db=False)
    
    model = EconomicRegimeModel()
    
    performance = model.train(df, optimize=False)
    
    print("\n模型性能:")
    print(f"  准确率: {performance.accuracy:.4f}")
    print(f"  精确率: {performance.precision:.4f}")
    print(f"  召回率: {performance.recall:.4f}")
    print(f"  F1分数: {performance.f1_score:.4f}")
    print(f"  交叉验证: {np.mean(performance.cv_scores):.4f} (+/- {np.std(performance.cv_scores):.4f})")
    
    print("\n特征重要性:")
    for feature, importance in performance.feature_importance.items():
        print(f"  {feature}: {importance:.4f}")
    
    model.save_model('models/economic_regime_model.pkl')
    
    print("\n预测当前经济范式:")
    current_data = {
        'gdp_growth': 6.5,
        'cpi': 2.3,
        'ppi': 1.5,
        'pmi': 51.2,
        'interest_rate': 3.5,
        'm2_growth': 10.5,
        'credit_growth': 12.8,
        'industrial_output': 6.8
    }
    
    regime, confidence = model.predict_current_regime(current_data)
    print(f"  经济范式: {regime.name}")
    print(f"  置信度: {confidence:.4f}")


if __name__ == '__main__':
    main()
