---
module_id: ARCHIVE_L9_ANOMALY_DETECTOR_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席文档架构�?
standard_type: 专业量化机构文档
applicable_scope: 全系�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
responsibility:
  - 数据质量 (Layer 1)
---

# L9_ANOMALY_DETECTOR: AI异常检测模块设�?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **模块ID**: L9_ANOMALY_DETECTOR  
> **模块名称**: AI异常检�? 
> **所属层�?*: Layer 9 - AI增强�? 
> **优先�?*: P1  
> **预计工时**: 28小时  
> **设计状�?*: 🟡 设计�? 
> **设计日期**: 2026-04-01  
> **关联蓝图**: [AI_ENHANCEMENT_INTEGRATION_BLUEPRINT.md](../../02_FACTOR_LIBRARY/AI_ENHANCEMENT_INTEGRATION_BLUEPRINT.md)

---

## 📋 模块概述

### 1.1 功能定位
**L9_ANOMALY_DETECTOR** 是AI增强层的第六个模块，负责使用pyod异常检测框架构建强大的异常检测系统。该模块专门用于识别量化交易中的异常模式、极端事件、数据质量问题以及潜在的欺诈行为，为风险管理和策略优化提供关键支持�?

### 1.2 设计原则
- **多算法集�?*: 集成多种异常检测算法，提高检测准确性和鲁棒�?
- **自适应阈�?*: 根据数据分布动态调整异常检测阈�?
- **可解释�?*: 提供异常原因分析和可视化解释
- **实时�?*: 支持实时异常检测和预警
- **可扩展�?*: 易于添加新的异常检测算法和特征
- **集成友好**: 与Layer 0数据预处理层和Layer 8人机交互层无缝集�?

### 1.3 输入输出
| 项目 | 描述 |
|------|------|
| **输入** | 时间序列数据、特征数据、历史异常标签（可选）、检测配�?|
| **输出** | 异常分数、异常标签、异常原因分析、预警信号、检测报�?|
| **控制参数** | 检测算法、阈值策略、时间窗口、特征选择、预警规�?|

---

## 🏗�?架构设计

### 2.1 模块结构
```
L9_ANOMALY_DETECTOR/
├── pyod_integration.py             # pyod集成核心�?
├── anomaly_detection_pipeline.py   # 异常检测流水线
├── anomaly_detector_ensemble.py    # 异常检测集成器
├── anomaly_scorer.py               # 异常评分�?
├── threshold_optimizer.py          # 阈值优化器
├── anomaly_explainer.py            # 异常解释�?
├── config/
�?  └── pyod_config.yaml           # 配置文件
├── tests/
�?  ├── test_pyod_integration.py
�?  └── test_anomaly_pipeline.py
└── monitoring/
    └── anomaly_detection_monitor.py
```

### 2.2 核心类设�?
```python
# pyod_integration.py
class PyodAnomalyDetector:
    """pyod异常检测集�?""
    
    def __init__(self, config: AnomalyDetectionConfig):
        self.config = config
        self.detectors = {}
        self.ensemble_detector = None
        self.threshold_optimizer = ThresholdOptimizer()
        self.anomaly_explainer = AnomalyExplainer()
        self._initialize_pyod()
    
    def detect_anomalies(
        self,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None,
        detection_mode: str = 'unsupervised',
        ensemble_method: str = 'average'
    ) -> AnomalyDetectionResult:
        """检测异常主方法"""
        # 1. 数据预处�?
        X_processed = self._preprocess_data(X)
        
        # 2. 训练检测器
        if detection_mode == 'unsupervised':
            self._train_unsupervised_detectors(X_processed)
        elif detection_mode == 'semi_supervised':
            self._train_semi_supervised_detectors(X_processed, y)
        elif detection_mode == 'supervised':
            self._train_supervised_detectors(X_processed, y)
        else:
            raise ValueError(f"未知检测模�? {detection_mode}")
        
        # 3. 检测异�?
        anomaly_scores = self._detect_with_ensemble(X_processed, ensemble_method)
        
        # 4. 优化阈�?
        optimal_threshold = self.threshold_optimizer.optimize_threshold(
            anomaly_scores, X_processed, self.config.threshold_optimization
        )
        
        # 5. 生成异常标签
        anomaly_labels = (anomaly_scores >= optimal_threshold).astype(int)
        
        # 6. 解释异常
        anomaly_explanations = self.anomaly_explainer.explain_anomalies(
            X_processed, anomaly_scores, anomaly_labels, optimal_threshold
        )
        
        # 7. 生成检测报�?
        detection_report = self._generate_detection_report(
            X_processed, anomaly_scores, anomaly_labels, anomaly_explanations
        )
        
        return AnomalyDetectionResult(
            anomaly_scores=anomaly_scores,
            anomaly_labels=anomaly_labels,
            threshold=optimal_threshold,
            explanations=anomaly_explanations,
            report=detection_report,
            detectors=self.detectors,
            ensemble_method=ensemble_method
        )
    
    def _initialize_pyod(self):
        """初始化pyod检测器"""
        detector_configs = self.config.detectors
        
        for detector_name, detector_config in detector_configs.items():
            if not detector_config.get('enabled', True):
                continue
                
            detector_type = detector_config.get('type')
            params = detector_config.get('params', {})
            
            # 创建检测器实例
            detector = self._create_detector(detector_type, params)
            
            self.detectors[detector_name] = {
                'detector': detector,
                'type': detector_type,
                'config': detector_config,
                'trained': False
            }
    
    def _create_detector(self, detector_type: str, params: Dict[str, Any]) -> Any:
        """创建检测器实例"""
        if detector_type == 'iforest':
            from pyod.models.iforest import IForest
            return IForest(**params)
        elif detector_type == 'lof':
            from pyod.models.lof import LOF
            return LOF(**params)
        elif detector_type == 'ocsvm':
            from pyod.models.ocsvm import OCSVM
            return OCSVM(**params)
        elif detector_type == 'hbos':
            from pyod.models.hbos import HBOS
            return HBOS(**params)
        elif detector_type == 'knn':
            from pyod.models.knn import KNN
            return KNN(**params)
        elif detector_type == 'autoencoder':
            from pyod.models.auto_encoder import AutoEncoder
            return AutoEncoder(**params)
        elif detector_type == 'vae':
            from pyod.models.vae import VAE
            return VAE(**params)
        elif detector_type == 'copod':
            from pyod.models.copod import COPOD
            return COPOD(**params)
        elif detector_type == 'sos':
            from pyod.models.sos import SOS
            return SOS(**params)
        elif detector_type == 'abod':
            from pyod.models.abod import ABOD
            return ABOD(**params)
        elif detector_type == 'mcd':
            from pyod.models.mcd import MCD
            return MCD(**params)
        elif detector_type == 'pca':
            from pyod.models.pca import PCA
            return PCA(**params)
        elif detector_type == 'loda':
            from pyod.models.loda import LODA
            return LODA(**params)
        elif detector_type == 'cof':
            from pyod.models.cof import COF
            return COF(**params)
        elif detector_type == 'rod':
            from pyod.models.rod import ROD
            return ROD(**params)
        elif detector_type == 'sampling':
            from pyod.models.sampling import Sampling
            return Sampling(**params)
        elif detector_type == 'gmm':
            from pyod.models.gmm import GMM
            return GMM(**params)
        elif detector_type == 'so_gaal':
            from pyod.models.so_gaal import SO_GAAL
            return SO_GAAL(**params)
        elif detector_type == 'mo_gaal':
            from pyod.models.mo_gaal import MO_GAAL
            return MO_GAAL(**params)
        elif detector_type == 'xgbod':
            from pyod.models.xgbod import XGBOD
            return XGBOD(**params)
        elif detector_type == 'cblof':
            from pyod.models.cblof import CBLOF
            return CBLOF(**params)
        elif detector_type == 'lodof':
            from pyod.models.lodof import LODOF
            return LODOF(**params)
        elif detector_type == 'inne':
            from pyod.models.inne import INNE
            return INNE(**params)
        elif detector_type == 'ecod':
            from pyod.models.ecod import ECOD
            return ECOD(**params)
        elif detector_type == 'deepsvdd':
            from pyod.models.deep_svdd import DeepSVDD
            return DeepSVDD(**params)
        elif detector_type == 'anogan':
            from pyod.models.anogan import AnoGAN
            return AnoGAN(**params)
        else:
            raise ValueError(f"未知检测器类型: {detector_type}")
    
    def _train_unsupervised_detectors(self, X: pd.DataFrame):
        """训练无监督检测器"""
        for detector_name, detector_info in self.detectors.items():
            detector = detector_info['detector']
            
            # 检查是否支持无监督训练
            if hasattr(detector, 'fit'):
                try:
                    detector.fit(X)
                    detector_info['trained'] = True
                    print(f"训练完成: {detector_name}")
                except Exception as e:
                    print(f"训练失败 {detector_name}: {str(e)}")
                    detector_info['trained'] = False
    
    def _train_semi_supervised_detectors(self, X: pd.DataFrame, y: pd.Series):
        """训练半监督检测器"""
        # 分离正常样本和异常样�?
        normal_indices = y == 0
        abnormal_indices = y == 1
        
        X_normal = X[normal_indices]
        X_abnormal = X[abnormal_indices] if any(abnormal_indices) else None
        
        for detector_name, detector_info in self.detectors.items():
            detector = detector_info['detector']
            
            # 检查是否支持半监督训练
            if hasattr(detector, 'fit'):
                try:
                    # 根据检测器类型选择训练方式
                    if detector_info['type'] in ['ocsvm', 'autoencoder', 'vae', 'deepsvdd']:
                        # 这些检测器可以使用正常样本训练
                        if len(X_normal) > 0:
                            detector.fit(X_normal)
                            detector_info['trained'] = True
                        else:
                            print(f"无正常样本可用于训练 {detector_name}")
                            detector_info['trained'] = False
                    else:
                        # 其他检测器使用所有样本（无监督）
                        detector.fit(X)
                        detector_info['trained'] = True
                    
                    print(f"训练完成: {detector_name}")
                except Exception as e:
                    print(f"训练失败 {detector_name}: {str(e)}")
                    detector_info['trained'] = False
    
    def _train_supervised_detectors(self, X: pd.DataFrame, y: pd.Series):
        """训练监督检测器"""
        for detector_name, detector_info in self.detectors.items():
            detector = detector_info['detector']
            
            # 检查是否支持监督训�?
            if hasattr(detector, 'fit') and hasattr(detector, 'predict_proba'):
                try:
                    detector.fit(X, y)
                    detector_info['trained'] = True
                    print(f"训练完成: {detector_name}")
                except Exception as e:
                    print(f"训练失败 {detector_name}: {str(e)}")
                    detector_info['trained'] = False
            else:
                print(f"检测器 {detector_name} 不支持监督训�?)
                detector_info['trained'] = False
    
    def _detect_with_ensemble(
        self,
        X: pd.DataFrame,
        ensemble_method: str = 'average'
    ) -> np.ndarray:
        """使用集成方法检测异�?""
        # 收集训练好的检测器的预�?
        detector_scores = {}
        
        for detector_name, detector_info in self.detectors.items():
            if not detector_info['trained']:
                continue
                
            detector = detector_info['detector']
            
            try:
                # 获取异常分数
                if hasattr(detector, 'decision_function'):
                    scores = detector.decision_function(X)
                elif hasattr(detector, 'predict_proba'):
                    scores = detector.predict_proba(X)[:, 1]  # 异常类的概率
                elif hasattr(detector, 'predict'):
                    scores = detector.predict(X)
                else:
                    print(f"检测器 {detector_name} 无评分方�?)
                    continue
                
                # 标准化分数到[0, 1]范围
                if scores.ndim == 1:
                    # 一维数�?
                    if np.std(scores) > 0:
                        scores_normalized = (scores - np.min(scores)) / (np.max(scores) - np.min(scores))
                    else:
                        scores_normalized = np.zeros_like(scores)
                else:
                    # 多维数组（如某些检测器返回多列�?
                    scores_normalized = scores
                
                detector_scores[detector_name] = scores_normalized
                
            except Exception as e:
                print(f"检测器 {detector_name} 预测失败: {str(e)}")
                continue
        
        # 如果没有检测器成功，返回零数组
        if not detector_scores:
            return np.zeros(len(X))
        
        # 应用集成方法
        if ensemble_method == 'average':
            # 平均分数
            all_scores = np.array(list(detector_scores.values()))
            ensemble_scores = np.mean(all_scores, axis=0)
        
        elif ensemble_method == 'weighted_average':
            # 加权平均（根据检测器性能�?
            weights = self._calculate_detector_weights(detector_scores)
            weighted_scores = []
            
            for detector_name, scores in detector_scores.items():
                weight = weights.get(detector_name, 1.0)
                weighted_scores.append(scores * weight)
            
            ensemble_scores = np.mean(weighted_scores, axis=0)
        
        elif ensemble_method == 'maximum':
            # 最大分数（最敏感�?
            all_scores = np.array(list(detector_scores.values()))
            ensemble_scores = np.max(all_scores, axis=0)
        
        elif ensemble_method == 'minimum':
            # 最小分数（最保守�?
            all_scores = np.array(list(detector_scores.values()))
            ensemble_scores = np.min(all_scores, axis=0)
        
        elif ensemble_method == 'median':
            # 中位�?
            all_scores = np.array(list(detector_scores.values()))
            ensemble_scores = np.median(all_scores, axis=0)
        
        elif ensemble_method == 'vote':
            # 投票（基于阈值）
            threshold = self.config.default_threshold
            votes = []
            
            for detector_name, scores in detector_scores.items():
                votes.append((scores >= threshold).astype(int))
            
            vote_matrix = np.array(votes)
            ensemble_scores = np.mean(vote_matrix, axis=0)  # 异常投票比例
        
        else:
            raise ValueError(f"未知集成方法: {ensemble_method}")
        
        return ensemble_scores
    
    def _calculate_detector_weights(self, detector_scores: Dict[str, np.ndarray]) -> Dict[str, float]:
        """计算检测器权重"""
        weights = {}
        
        for detector_name, scores in detector_scores.items():
            # 基于分数分布计算权重
            # 1. 分数方差（越大越好，表示检测器有区分度�?
            score_variance = np.var(scores)
            
            # 2. 分数峰度（越小越好，表示分布不极端）
            from scipy.stats import kurtosis
            score_kurtosis = kurtosis(scores) if len(scores) > 3 else 0
            
            # 3. 分数偏度（绝对值越小越好）
            from scipy.stats import skew
            score_skewness = abs(skew(scores)) if len(scores) > 3 else 0
            
            # 综合权重
            weight = score_variance * (1 / (1 + abs(score_kurtosis))) * (1 / (1 + score_skewness))
            
            weights[detector_name] = max(weight, 0.1)  # 最小权�?.1
        
        # 归一化权�?
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights
    
    def _preprocess_data(self, X: pd.DataFrame) -> pd.DataFrame:
        """预处理数�?""
        # 1. 处理缺失�?
        if self.config.preprocessing.get('handle_missing', True):
            X = self._handle_missing_values(X)
        
        # 2. 标准�?归一�?
        if self.config.preprocessing.get('scale_features', True):
            X = self._scale_features(X)
        
        # 3. 特征选择
        if self.config.preprocessing.get('feature_selection', False):
            X = self._select_features(X)
        
        # 4. 降维（可选）
        if self.config.preprocessing.get('dimensionality_reduction', False):
            X = self._reduce_dimensions(X)
        
        return X
    
    def _handle_missing_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """处理缺失�?""
        # 简单策略：用中位数填充数值特征，用众数填充分类特�?
        X_filled = X.copy()
        
        for column in X.columns:
            if X[column].dtype in [np.float64, np.float32, np.int64, np.int32]:
                # 数值特�?
                median_value = X[column].median()
                X_filled[column] = X[column].fillna(median_value)
            else:
                # 分类特征
                mode_value = X[column].mode()[0] if not X[column].mode().empty else 'missing'
                X_filled[column] = X[column].fillna(mode_value)
        
        return X_filled
    
    def _scale_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """标准化特�?""
        from sklearn.preprocessing import StandardScaler
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
```

### 2.3 数据流水�?
```python
# anomaly_detection_pipeline.py
class AnomalyDetectionPipeline:
    """异常检测流水线"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.detector = PyodAnomalyDetector(self.config)
        self.data_preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.alert_generator = AlertGenerator()
        
    def run(
        self,
        data_source: str,
        start_date: str,
        end_date: str,
        detection_mode: str = 'unsupervised',
        real_time: bool = False
    ) -> PipelineResult:
        """运行完整异常检测流水线"""
        results = {}
        
        # 1. 数据加载
        raw_data = self._load_data(data_source, start_date, end_date)
        results['data_stats'] = self._get_data_stats(raw_data)
        
        # 2. 特征工程
        features = self.feature_engineer.create_anomaly_features(raw_data)
        results['feature_info'] = self._get_feature_info(features)
        
        # 3. 异常检�?
        detection_result = self.detector.detect_anomalies(
            X=features,
            y=None,  # 无监督模�?
            detection_mode=detection_mode,
            ensemble_method=self.config.ensemble_method
        )
        results['detection_result'] = detection_result
        
        # 4. 异常分析
        anomaly_analysis = self._analyze_anomalies(
            raw_data, features, detection_result
        )
        results['anomaly_analysis'] = anomaly_analysis
        
        # 5. 预警生成
        if self.config.alerts_enabled:
            alerts = self.alert_generator.generate_alerts(
                detection_result, raw_data, self.config.alert_rules
            )
            results['alerts'] = alerts
        
        # 6. 生成报告
        results['final_report'] = self._generate_final_report(results)
        
        # 7. 实时监控设置
        if real_time:
            self._setup_real_time_monitoring(detection_result, features)
        
        return PipelineResult(**results)
    
    def _analyze_anomalies(
        self,
        raw_data: pd.DataFrame,
        features: pd.DataFrame,
        detection_result: AnomalyDetectionResult
    ) -> Dict[str, Any]:
        """分析异常"""
        analysis = {}
        
        # 异常统计
        anomaly_labels = detection_result.anomaly_labels
        anomaly_count = np.sum(anomaly_labels)
        total_samples = len(anomaly_labels)
        
        analysis['anomaly_statistics'] = {
            'total_samples': total_samples,
            'anomaly_count': int(anomaly_count),
            'anomaly_ratio': float(anomaly_count / total_samples) if total_samples > 0 else 0.0,
            'threshold': float(detection_result.threshold)
        }
        
        # 异常时间分布
        if 'timestamp' in raw_data.columns:
            anomaly_timestamps = raw_data.loc[anomaly_labels == 1, 'timestamp']
            analysis['temporal_distribution'] = self._analyze_temporal_distribution(
                anomaly_timestamps
            )
        
        # 异常特征分析
        anomaly_features = features[anomaly_labels == 1]
        normal_features = features[anomaly_labels == 0]
        
        if len(anomaly_features) > 0 and len(normal_features) > 0:
            analysis['feature_analysis'] = self._analyze_feature_differences(
                anomaly_features, normal_features
            )
        
        # 异常聚类分析
        if len(anomaly_features) > 1:
            analysis['cluster_analysis'] = self._cluster_anomalies(anomaly_features)
        
        # 异常关联分析
        analysis['correlation_analysis'] = self._analyze_anomaly_correlations(
            raw_data, anomaly_labels
        )
        
        return analysis
    
    def _analyze_temporal_distribution(self, timestamps: pd.Series) -> Dict[str, Any]:
        """分析异常时间分布"""
        analysis = {}
        
        if len(timestamps) == 0:
            return analysis
        
        # 转换为datetime（如果还不是�?
        if not pd.api.types.is_datetime64_any_dtype(timestamps):
            try:
                timestamps = pd.to_datetime(timestamps)
            except:
                return analysis
        
        # 时间频率分析
        analysis['hourly_distribution'] = timestamps.dt.hour.value_counts().sort_index().to_dict()
        analysis['daily_distribution'] = timestamps.dt.dayofweek.value_counts().sort_index().to_dict()
        analysis['monthly_distribution'] = timestamps.dt.month.value_counts().sort_index().to_dict()
        
        # 时间间隔分析
        if len(timestamps) > 1:
            time_diffs = np.diff(timestamps.sort_values().values)
            time_diffs_seconds = [td.total_seconds() for td in time_diffs]
            
            analysis['time_interval_stats'] = {
                'min_interval': float(np.min(time_diffs_seconds)),
                'max_interval': float(np.max(time_diffs_seconds)),
                'mean_interval': float(np.mean(time_diffs_seconds)),
                'median_interval': float(np.median(time_diffs_seconds)),
                'std_interval': float(np.std(time_diffs_seconds))
            }
        
        return analysis
    
    def _analyze_feature_differences(
        self,
        anomaly_features: pd.DataFrame,
        normal_features: pd.DataFrame
    ) -> Dict[str, Any]:
        """分析异常与正常样本的特征差异"""
        analysis = {}
        
        for column in anomaly_features.columns:
            anomaly_values = anomaly_features[column].dropna()
            normal_values = normal_features[column].dropna()
            
            if len(anomaly_values) > 0 and len(normal_values) > 0:
                # 基本统计
                analysis[column] = {
                    'anomaly_mean': float(np.mean(anomaly_values)),
                    'anomaly_std': float(np.std(anomaly_values)),
                    'normal_mean': float(np.mean(normal_values)),
                    'normal_std': float(np.std(normal_values)),
                    'mean_difference': float(np.mean(anomaly_values) - np.mean(normal_values)),
                    'effect_size': self._calculate_effect_size(anomaly_values, normal_values)
                }
                
                # 统计检验（如果样本量足够）
                if len(anomaly_values) > 2 and len(normal_values) > 2:
                    from scipy.stats import ttest_ind, mannwhitneyu
                    
                    # t检�?
                    t_stat, p_value_t = ttest_ind(anomaly_values, normal_values, equal_var=False)
                    analysis[column]['t_test'] = {
                        't_statistic': float(t_stat),
                        'p_value': float(p_value_t)
                    }
                    
                    # Mann-Whitney U检�?
                    u_stat, p_value_u = mannwhitneyu(anomaly_values, normal_values)
                    analysis[column]['u_test'] = {
                        'u_statistic': float(u_stat),
                        'p_value': float(p_value_u)
                    }
        
        return analysis
    
    def _calculate_effect_size(self, group1: np.ndarray, group2: np.ndarray) -> float:
        """计算效应大小（Cohen's d�?""
        mean1, mean2 = np.mean(group1), np.mean(group2)
        std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
        n1, n2 = len(group1), len(group2)
        
        # 合并标准�?
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0.0
        
        return abs(mean1 - mean2) / pooled_std
    
    def _cluster_anomalies(self, anomaly_features: pd.DataFrame) -> Dict[str, Any]:
        """聚类分析异常"""
        analysis = {}
        
        if len(anomaly_features) < 2:
            return analysis
        
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        
        # 尝试不同聚类�?
        max_clusters = min(10, len(anomaly_features))
        silhouette_scores = []
        
        for n_clusters in range(2, max_clusters + 1):
            try:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(anomaly_features)
                
                if len(np.unique(cluster_labels)) > 1:
                    score = silhouette_score(anomaly_features, cluster_labels)
                    silhouette_scores.append((n_clusters, score, kmeans))
            except:
                continue
        
        # 选择最佳聚类数
        if silhouette_scores:
            best_n_clusters, best_score, best_kmeans = max(silhouette_scores, key=lambda x: x[1])
            
            analysis['optimal_clusters'] = int(best_n_clusters)
            analysis['silhouette_score'] = float(best_score)
            analysis['cluster_sizes'] = {
                f'cluster_{i}': int(np.sum(best_kmeans.labels_ == i))
                for i in range(best_n_clusters)
            }
            
            # 聚类中心
            analysis['cluster_centers'] = best_kmeans.cluster_centers_.tolist()
        
        return analysis
```

---

## ⚙️ 配置设计

### 3.1 配置文件
```yaml
# config/pyod_config.yaml
anomaly_detection:
  enabled: true
  mode: "production"  # development | production | high_sensitivity
  
  # 检测器配置
  detectors:
    iforest:
      enabled: true
      type: "iforest"
      params:
        n_estimators: 100
        max_samples: 'auto'
        contamination: 0.1
        random_state: 42
        behaviour: 'new'
    
    lof:
      enabled: true
      type: "lof"
      params:
        n_neighbors: 20
        contamination: 0.1
        novelty: false
    
    ocsvm:
      enabled: true
      type: "ocsvm"
      params:
        kernel: 'rbf'
        nu: 0.1
        gamma: 'auto'
    
    hbos:
      enabled: true
      type: "hbos"
      params:
        n_bins: 10
        alpha: 0.1
        tol: 0.5
    
    knn:
      enabled: true
      type: "knn"
      params:
        n_neighbors: 5
        method: 'largest'
        contamination: 0.1
    
    autoencoder:
      enabled: false  # 深度学习，需要更多资�?
      type: "autoencoder"
      params:
        hidden_neurons: [64, 32, 32, 64]
        hidden_activation: 'relu'
        output_activation: 'sigmoid'
        loss: 'mse'
        optimizer: 'adam'
        epochs: 100
        batch_size: 32
        dropout_rate: 0.2
        l2_regularizer: 0.1
        validation_size: 0.1
        preprocessing: true
        contamination: 0.1
        verbose: 0
        random_state: 42
    
    copod:
      enabled: true
      type: "copod"
      params:
        contamination: 0.1
    
    ecod:
      enabled: true
      type: "ecod"
      params:
        contamination: 0.1
    
    # 更多检测器...
  
  # 集成配置
  ensemble:
    method: "weighted_average"  # average | weighted_average | maximum | minimum | median | vote
    min_detectors: 3  # 最少需要的检测器数量
    weight_calculation: "performance_based"  # performance_based | uniform | variance_based
  
  # 阈值配�?
  threshold:
    default: 0.9  # 默认阈�?
    optimization:
      enabled: true
      method: "percentile"  # percentile | gaussian | mixture | elbow
      percentile: 95  # 用于percentile方法
      sigma: 3  # 用于gaussian方法�?sigma�?
      contamination: 0.1  # 预期异常比例
    
    adaptive:
      enabled: true
      window_size: 1000  # 滑动窗口大小
      update_frequency: 100  # 更新频率（样本数�?
      min_samples: 100  # 最小样本数
  
  # 预处理配�?
  preprocessing:
    handle_missing: true
    scale_features: true
    feature_selection: false
    dimensionality_reduction: false
    
    scaling_method: "standard"  # standard | minmax | robust
    missing_strategy: "median"  # median | mean | mode | constant | drop
    
    feature_selection_method: "variance"  # variance | correlation | mutual_info
    variance_threshold: 0.01  # 方差阈�?
    
    dimensionality_reduction_method: "pca"  # pca | tsne | umap
    n_components: 0.95  # 保留的方差比例或组件�?
  
  # 特征工程配置
  feature_engineering:
    time_features: true
    statistical_features: true
    technical_indicators: true
    rolling_features: true
    
    time_windows: [5, 10, 20, 60]  # 时间窗口（分�?条）
    statistical_measures: ["mean", "std", "skew", "kurtosis", "min", "max", "median"]
    
    technical_indicators:
      - "sma"
      - "ema"
      - "rsi"
      - "macd"
      - "bollinger_bands"
      - "atr"
    
    rolling_features:
      enabled: true
      windows: [10, 30, 60, 120]
      functions: ["mean", "std", "min", "max", "median", "sum"]
  
  # 检测模式配�?
  detection_mode:
    default: "unsupervised"  # unsupervised | semi_supervised | supervised
    retrain_frequency: "daily"  # hourly | daily | weekly | monthly
    incremental_learning: true
    model_persistence: true
  
  # 预警配置
  alerts:
    enabled: true
    levels:
      - level: "info"
        threshold: 0.7
        channels: ["log"]
      
      - level: "warning"
        threshold: 0.85
        channels: ["log", "email"]
      
      - level: "critical"
        threshold: 0.95
        channels: ["log", "email", "sms", "webhook"]
    
    notification_channels:
      email:
        enabled: true
        recipients: ["alerts@zephyralpha.com"]
        smtp_server: "smtp.gmail.com"
        smtp_port: 587
        
      sms:
        enabled: false
        provider: "twilio"
        
      webhook:
        enabled: true
        url: "https://hooks.slack.com/services/..."
    
    cooldown_period: 300  # 相同预警冷却时间（秒�?
    grouping_window: 60  # 预警分组时间窗口（秒�?
  
  # 性能配置
  performance:
    batch_size: 1000
    n_jobs: -1
    memory_limit: "2GB"
    use_gpu: false
    gpu_device: 0
    
    real_time:
      enabled: true
      processing_latency: 100  # 毫秒
      max_queue_size: 10000
      batch_processing: true
      batch_interval: 1000  # 毫秒
  
  # 监控配置
  monitoring:
    metrics_logging: true
    real_time_dashboard: true
    anomaly_tracking: true
    
    metrics:
      - "anomaly_count"
      - "anomaly_ratio"
      - "detection_latency"
      - "false_positive_rate"
      - "true_positive_rate"
      - "precision"
      - "recall"
      - "f1_score"
      - "auc_roc"
    
    alert_thresholds:
      high_false_positive_rate: 0.1
      low_precision: 0.7
      high_detection_latency: 1000  # 毫秒
      memory_usage: "1.5GB"
    
    visualization:
      enabled: true
      anomaly_heatmap: true
      feature_importance: true
      temporal_distribution: true
      cluster_visualization: true
```

### 3.2 环境依赖
```txt
# requirements.txt (部分)
pyod>=1.0.0
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
scipy>=1.7.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.10.0
joblib>=1.1.0
tqdm>=4.64.0
statsmodels>=0.13.0  # 时间序列特征
ta>=0.10.0  # 技术指�?
umap-learn>=0.5.0  # 降维
```

---

## 🔧 接口设计

### 4.1 外部接口
```python
class AnomalyDetectionAPI:
    """异常检测API接口"""
    
    @staticmethod
    def detect_anomalies_in_data(
        data: pd.DataFrame,
        config: Optional[Dict[str, Any]] = None,
        detection_mode: str = "unsupervised"
    ) -> AnomalyDetectionResult:
        """在数据中检测异�?""
        pass
    
    @staticmethod
    def detect_anomalies_in_stream(
        data_stream: Iterator[pd.DataFrame],
        config: Optional[Dict[str, Any]] = None,
        window_size: int = 1000
    ) -> Iterator[AnomalyDetectionResult]:
        """在数据流中实时检测异�?""
        pass
    
    @staticmethod
    def evaluate_detection_performance(
        ground_truth: pd.Series,
        detection_result: AnomalyDetectionResult,
        metrics: List[str] = ["precision", "recall", "f1", "auc_roc"]
    ) -> PerformanceEvaluation:
        """评估异常检测性能"""
        pass
    
    @staticmethod
    def explain_anomaly(
        data_point: pd.Series,
        detection_result: AnomalyDetectionResult,
        explanation_method: str = "feature_contribution"
    ) -> AnomalyExplanation:
        """解释单个异常"""
        pass
    
    @staticmethod
    def train_custom_detector(
        training_data: pd.DataFrame,
        labels: Optional[pd.Series] = None,
        detector_type: str = "autoencoder",
        params: Optional[Dict[str, Any]] = None
    ) -> CustomDetector:
        """训练自定义异常检测器"""
        pass
```

### 4.2 内部接口
```python
# 与Layer 0数据预处理层的接�?
class DataPreprocessingLayerIntegration:
    """数据预处理层集成接口"""
    
    def get_processed_data(
        self,
        data_source: str,
        start_date: str,
        end_date: str,
        feature_config: FeatureConfig
    ) -> pd.DataFrame:
        """获取预处理后的数�?""
        # 调用L0数据预处理层的API
        pass
    
    def stream_real_time_data(
        self,
        data_source: str,
        feature_config: FeatureConfig
    ) -> Iterator[pd.DataFrame]:
        """获取实时数据�?""
        pass
    
    def report_data_quality_issues(
        self,
        anomalies: pd.DataFrame,
        issue_type: str,
        severity: str
    ) -> bool:
        """报告数据质量问题"""
        pass

# 与Layer 8人机交互层的接口
class HumanInteractionLayerIntegration:
    """人机交互层集成接�?""
    
    def send_anomaly_alert(
        self,
        alert_level: str,
        alert_message: str,
        anomaly_details: Dict[str, Any],
        notification_channels: List[str]
    ) -> bool:
        """发送异常预�?""
        pass
    
    def log_anomaly_event(
        self,
        anomaly_event: AnomalyEvent,
        context: Dict[str, Any]
    ) -> bool:
        """记录异常事件"""
        pass
    
    def get_anomaly_feedback(
        self,
        anomaly_id: str,
        feedback_type: str = "confirmation"
    ) -> Optional[AnomalyFeedback]:
        """获取异常反馈"""
        pass
```

### 4.3 数据接口
```python
# 异常检测数据格�?
class AnomalyDetectionData:
    """异常检测数据格�?""
    
    def __init__(self):
        self.raw_data: pd.DataFrame  # 原始数据
        self.features: pd.DataFrame  # 特征数据
        self.timestamps: pd.Series  # 时间�?
        self.labels: Optional[pd.Series] = None  # 真实标签（如果有�?
        self.metadata: Dict[str, Any]  # 元数�?
        
    @classmethod
    def from_raw_data(
        cls,
        raw_data: pd.DataFrame,
        feature_config: FeatureConfig,
        label_column: Optional[str] = None
    ) -> "AnomalyDetectionData":
        """从原始数据创�?""
        instance = cls()
        instance.raw_data = raw_data
        instance.features = cls._extract_features(raw_data, feature_config)
        
        if 'timestamp' in raw_data.columns:
            instance.timestamps = raw_data['timestamp']
        
        if label_column and label_column in raw_data.columns:
            instance.labels = raw_data[label_column]
        
        instance.metadata = {
            'sample_count': len(raw_data),
            'feature_count': len(instance.features.columns),
            'feature_names': list(instance.features.columns),
            'data_source': feature_config.get('data_source', 'unknown'),
            'timestamp_range': (
                instance.timestamps.min() if len(instance.timestamps) > 0 else None,
                instance.timestamps.max() if len(instance.timestamps) > 0 else None
            )
        }
        
        return instance
    
    @staticmethod
    def _extract_features(
        raw_data: pd.DataFrame,
        feature_config: FeatureConfig
    ) -> pd.DataFrame:
        """提取特征"""
        features = pd.DataFrame(index=raw_data.index)
        
        # 基础特征
        if feature_config.get('include_raw_features', True):
            numeric_cols = raw_data.select_dtypes(include=[np.number]).columns
            features[numeric_cols] = raw_data[numeric_cols]
        
        # 时间特征
        if feature_config.get('include_time_features', False) and 'timestamp' in raw_data.columns:
            timestamps = pd.to_datetime(raw_data['timestamp'])
            features['hour'] = timestamps.dt.hour
            features['day_of_week'] = timestamps.dt.dayofweek
            features['day_of_month'] = timestamps.dt.day
            features['month'] = timestamps.dt.month
            features['is_weekend'] = timestamps.dt.dayofweek >= 5
        
        # 统计特征
        if feature_config.get('include_statistical_features', False):
            window_sizes = feature_config.get('statistical_windows', [5, 10, 20])
            for window in window_sizes:
                for col in numeric_cols:
                    features[f'{col}_rolling_mean_{window}'] = raw_data[col].rolling(window).mean()
                    features[f'{col}_rolling_std_{window}'] = raw_data[col].rolling(window).std()
                    features[f'{col}_rolling_min_{window}'] = raw_data[col].rolling(window).min()
                    features[f'{col}_rolling_max_{window}'] = raw_data[col].rolling(window).max()
        
        return features
```

---

## 🧪 测试设计

### 5.1 单元测试
```python
# tests/test_pyod_integration.py
import pytest
import pandas as pd
import numpy as np
import pyod
from unittest.mock import Mock, patch, MagicMock
from L9_ANOMALY_DETECTOR.pyod_integration import PyodAnomalyDetector
from L9_ANOMALY_DETECTOR.anomaly_detection_pipeline import AnomalyDetectionPipeline

class TestPyodAnomalyDetector:
    """pyod异常检测测�?""
    
    def setup_method(self):
        self.config = {
            'detectors': {
                'iforest': {
                    'enabled': True,
                    'type': 'iforest',
                    'params': {
                        'n_estimators': 50,
                        'contamination': 0.1,
                        'random_state': 42
                    }
                },
                'lof': {
                    'enabled': True,
                    'type': 'lof',
                    'params': {
                        'n_neighbors': 20,
                        'contamination': 0.1
                    }
                }
            },
            'ensemble': {
                'method': 'average',
                'min_detectors': 1
            },
            'threshold': {
                'default': 0.9,
                'optimization': {
                    'enabled': True,
                    'method': 'percentile',
                    'percentile': 95
                }
            },
            'preprocessing': {
                'handle_missing': True,
                'scale_features': True
            }
        }
        self.detector = PyodAnomalyDetector(self.config)
        
        # 创建测试数据
        n_samples = 1000
        n_features = 10
        
        # 正常数据（多元正态分布）
        np.random.seed(42)
        self.X_normal = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        
        # 异常数据（与正常数据分布不同�?
        self.X_abnormal = pd.DataFrame(
            np.random.randn(50, n_features) * 3 + 5,  # 不同的均值和方差
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        
        # 合并数据
        self.X = pd.concat([self.X_normal, self.X_abnormal], ignore_index=True)
        
        # 标签（用于监�?半监督测试）
        self.y = pd.Series([0] * n_samples + [1] * 50)
    
    def test_initialization(self):
        assert self.detector.config == self.config
        assert 'iforest' in self.detector.detectors
        assert 'lof' in self.detector.detectors
        assert self.detector.threshold_optimizer is not None
        assert self.detector.anomaly_explainer is not None
        
        # 验证检测器类型
        from pyod.models.iforest import IForest
        from pyod.models.lof import LOF
        assert isinstance(self.detector.detectors['iforest']['detector'], IForest)
        assert isinstance(self.detector.detectors['lof']['detector'], LOF)
    
    def test_create_detector_iforest(self):
        detector = self.detector._create_detector('iforest', {'n_estimators': 50})
        from pyod.models.iforest import IForest
        assert isinstance(detector, IForest)
        assert detector.n_estimators == 50
    
    def test_create_detector_lof(self):
        detector = self.detector._create_detector('lof', {'n_neighbors': 20})
        from pyod.models.lof import LOF
        assert isinstance(detector, LOF)
        assert detector.n_neighbors == 20
    
    def test_create_detector_ocsvm(self):
        detector = self.detector._create_detector('ocsvm', {'nu': 0.1})
        from pyod.models.ocsvm import OCSVM
        assert isinstance(detector, OCSVM)
        assert detector.nu == 0.1
    
    def test_train_unsupervised_detectors(self):
        self.detector._train_unsupervised_detectors(self.X)
        
        # 验证检测器已训�?
        assert self.detector.detectors['iforest']['trained'] == True
        assert self.detector.detectors['lof']['trained'] == True
        
        # 验证可以预测
        iforest = self.detector.detectors['iforest']['detector']
        lof = self.detector.detectors['lof']['detector']
        
        scores_iforest = iforest.decision_function(self.X)
        scores_lof = lof.decision_function(self.X)
        
        assert len(scores_iforest) == len(self.X)
        assert len(scores_lof) == len(self.X)
    
    def test_detect_with_ensemble_average(self):
        # 训练检测器
        self.detector._train_unsupervised_detectors(self.X)
        
        # 使用平均集成
        ensemble_scores = self.detector._detect_with_ensemble(self.X, 'average')
        
        assert len(ensemble_scores) == len(self.X)
        assert ensemble_scores.ndim == 1
        assert np.all(ensemble_scores >= 0)  # 分数应该非负
        assert np.all(ensemble_scores <= 1)  # 分数应该在[0,1]范围�?
    
    def test_detect_with_ensemble_weighted_average(self):
        # 训练检测器
        self.detector._train_unsupervised_detectors(self.X)
        
        # 使用加权平均集成
        ensemble_scores = self.detector._detect_with_ensemble(self.X, 'weighted_average')
        
        assert len(ensemble_scores) == len(self.X)
        assert ensemble_scores.ndim == 1
        assert np.all(ensemble_scores >= 0)
        assert np.all(ensemble_scores <= 1)
    
    def test_detect_anomalies_unsupervised(self):
        result = self.detector.detect_anomalies(
            X=self.X,
            detection_mode='unsupervised',
            ensemble_method='average'
        )
        
        # 验证结果
        assert hasattr(result, 'anomaly_scores')
        assert hasattr(result, 'anomaly_labels')
        assert hasattr(result, 'threshold')
        assert hasattr(result, 'explanations')
        assert hasattr(result, 'report')
        
        # 验证形状
        assert len(result.anomaly_scores) == len(self.X)
        assert len(result.anomaly_labels) == len(self.X)
        
        # 验证标签�?�?
        assert set(result.anomaly_labels) <= {0, 1}
        
        # 验证异常比例大致符合预期
        anomaly_ratio = np.mean(result.anomaly_labels)
        expected_contamination = 0.1  # 配置中的默认�?
        assert abs(anomaly_ratio - expected_contamination) < 0.1  # 允许一些误�?
    
    def test_handle_missing_values(self):
        # 创建有缺失值的数据
        X_with_nan = self.X.copy()
        X_with_nan.iloc[0:10, 0] = np.nan  # �?0行的第一列为NaN
        
        X_processed = self.detector._handle_missing_values(X_with_nan)
        
        # 验证缺失值已处理
        assert not X_processed.isnull().any().any()
        
        # 验证非缺失值未改变
        non_nan_mask = ~X_with_nan.iloc[10:, 0].isnull()
        assert np.allclose(
            X_processed.iloc[10:, 0][non_nan_mask].values,
            X_with_nan.iloc[10:, 0][non_nan_mask].values
        )
    
    def test_scale_features(self):
        X_scaled = self.detector._scale_features(self.X)
        
        # 验证每列的均值为0，标准差�?（近似）
        for col in X_scaled.columns:
            col_mean = np.mean(X_scaled[col])
            col_std = np.std(X_scaled[col])
            
            assert abs(col_mean) < 1e-10  # 均值接�?
            assert abs(col_std - 1) < 1e-10  # 标准差接�?
```

### 5.2 集成测试
```python
# tests/test_anomaly_pipeline.py
class TestAnomalyDetectionPipeline:
    """异常检测流水线测试"""
    
    def test_full_pipeline(self):
        pipeline = AnomalyDetectionPipeline('config/pyod_config.yaml')
        
        # 运行流水�?
        result = pipeline.run(
            data_source='synthetic',
            start_date='2026-01-01',
            end_date='2026-01-31',
            detection_mode='unsupervised',
            real_time=False
        )
        
        # 验证结果结构
        assert 'data_stats' in result
        assert 'feature_info' in result
        assert 'detection_result' in result
        assert 'anomaly_analysis' in result
        assert 'final_report' in result
        
        # 验证检测结�?
        detection_result = result.detection_result
        assert detection_result.anomaly_scores is not None
        assert detection_result.anomaly_labels is not None
        assert detection_result.threshold > 0
        
        # 验证异常分析
        anomaly_analysis = result.anomaly_analysis
        assert 'anomaly_statistics' in anomaly_analysis
        stats = anomaly_analysis['anomaly_statistics']
        assert 'total_samples' in stats
        assert 'anomaly_count' in stats
        assert 'anomaly_ratio' in stats
        
        # 验证异常比例合理
        assert 0 <= stats['anomaly_ratio'] <= 1
        
        # 验证最终报�?
        final_report = result.final_report
        assert 'summary' in final_report
        assert 'detection_metrics' in final_report
        assert 'recommendations' in final_report
    
    def test_real_time_pipeline(self):
        """测试实时异常检�?""
        pipeline = AnomalyDetectionPipeline('config/pyod_config.yaml')
        
        # 创建模拟数据�?
        def mock_data_stream():
            for i in range(5):
                batch_data = pd.DataFrame({
                    'timestamp': pd.date_range(start=f'2026-01-0{i+1}', periods=100, freq='T'),
                    'price': np.random.randn(100).cumsum() + 100,
                    'volume': np.random.exponential(1000, 100)
                })
                yield batch_data
        
        # 运行实时检�?
        stream_results = []
        for data_batch in mock_data_stream():
            result = pipeline.run(
                data_source='stream',
                start_date='2026-01-01',
                end_date='2026-01-02',
                detection_mode='unsupervised',
                real_time=True
            )
            stream_results.append(result)
        
        # 验证结果
        assert len(stream_results) == 5
        for result in stream_results:
            assert result.detection_result.anomaly_scores is not None
            assert len(result.detection_result.anomaly_scores) == 100
    
    def test_anomaly_analysis_methods(self):
        pipeline = AnomalyDetectionPipeline('config/pyod_config.yaml')
        
        # 创建测试数据
        np.random.seed(42)
        n_samples = 1000
        features = pd.DataFrame({
            'feature1': np.random.randn(n_samples),
            'feature2': np.random.randn(n_samples) * 2,
            'feature3': np.random.randn(n_samples) + 1
        })
        
        # 创建异常标签�?0%异常�?
        anomaly_labels = np.zeros(n_samples)
        anomaly_indices = np.random.choice(n_samples, size=100, replace=False)
        anomaly_labels[anomaly_indices] = 1
        
        # 测试特征差异分析
        anomaly_features = features[anomaly_labels == 1]
        normal_features = features[anomaly_labels == 0]
        
        feature_analysis = pipeline._analyze_feature_differences(
            anomaly_features, normal_features
        )
        
        assert 'feature1' in feature_analysis
        assert 'feature2' in feature_analysis
        assert 'feature3' in feature_analysis
        
        for feature_name, analysis in feature_analysis.items():
            assert 'anomaly_mean' in analysis
            assert 'normal_mean' in analysis
            assert 'mean_difference' in analysis
            assert 'effect_size' in analysis
        
        # 测试异常聚类分析
        if len(anomaly_features) > 1:
            cluster_analysis = pipeline._cluster_anomalies(anomaly_features)
            
            if 'optimal_clusters' in cluster_analysis:
                assert cluster_analysis['optimal_clusters'] >= 2
                assert 'silhouette_score' in cluster_analysis
                assert 'cluster_sizes' in cluster_analysis
        
        # 测试时间分布分析
        timestamps = pd.Series(pd.date_range('2026-01-01', periods=n_samples, freq='T'))
        anomaly_timestamps = timestamps[anomaly_labels == 1]
        
        temporal_analysis = pipeline._analyze_temporal_distribution(anomaly_timestamps)
        
        if anomaly_timestamps.size > 0:
            assert 'hourly_distribution' in temporal_analysis
            assert 'daily_distribution' in temporal_analysis
            assert 'monthly_distribution' in temporal_analysis
```

### 5.3 性能测试
```python
# tests/performance/test_pyod_performance.py
class TestPyodPerformance:
    """pyod性能测试"""
    
    def test_detection_scalability(self):
        """测试检测可扩展�?""
        import time
        
        config = {
            'detectors': {
                'iforest': {'enabled': True, 'type': 'iforest', 'params': {'n_estimators': 50}},
                'lof': {'enabled': True, 'type': 'lof', 'params': {'n_neighbors': 20}},
                'ocsvm': {'enabled': True, 'type': 'ocsvm', 'params': {'nu': 0.1}},
                'hbos': {'enabled': True, 'type': 'hbos', 'params': {'n_bins': 10}},
                'knn': {'enabled': True, 'type': 'knn', 'params': {'n_neighbors': 5}}
            },
            'ensemble': {'method': 'average', 'min_detectors': 3},
            'threshold': {'optimization': {'enabled': True, 'method': 'percentile'}},
            'preprocessing': {'scale_features': True}
        }
        
        detector = PyodAnomalyDetector(config)
        
        # 测试不同数据规模
        test_sizes = [1000, 5000, 10000, 20000]
        feature_counts = [10, 20, 50]
        
        results = []
        
        for n_samples in test_sizes:
            for n_features in feature_counts:
                # 创建测试数据
                X = pd.DataFrame(
                    np.random.randn(n_samples, n_features),
                    columns=[f'feature_{i}' for i in range(n_features)]
                )
                
                # 添加一些异�?
                n_anomalies = int(n_samples * 0.05)
                anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
                X.iloc[anomaly_indices] += np.random.randn(n_anomalies, n_features) * 5
                
                # 测量检测时�?
                start_time = time.time()
                result = detector.detect_anomalies(
                    X=X,
                    detection_mode='unsupervised',
                    ensemble_method='average'
                )
                end_time = time.time()
                
                detection_time = end_time - start_time
                samples_per_second = n_samples / detection_time
                
                results.append({
                    'n_samples': n_samples,
                    'n_features': n_features,
                    'detection_time': detection_time,
                    'samples_per_second': samples_per_second,
                    'anomaly_count': int(np.sum(result.anomaly_labels))
                })
                
                print(f"样本�? {n_samples}, 特征�? {n_features}, "
                      f"时间: {detection_time:.2f}s, 样本/�? {samples_per_second:.0f}")
        
        # 分析结果
        df_results = pd.DataFrame(results)
        print("\n性能摘要:")
        print(df_results.groupby('n_samples')[['detection_time', 'samples_per_second']].mean())
        
        # 验证性能要求
        # 对于10000样本，检测时间应小于10�?
        large_sample_result = df_results[df_results['n_samples'] == 10000]
        if len(large_sample_result) > 0:
            avg_time = large_sample_result['detection_time'].mean()
            assert avg_time < 10, f"10000样本检测时间过�? {avg_time:.2f}s"
        
        # 对于10特征，每秒应处理至少1000样本
        low_feature_result = df_results[df_results['n_features'] == 10]
        if len(low_feature_result) > 0:
            avg_speed = low_feature_result['samples_per_second'].mean()
            assert avg_speed > 1000, f"10特征处理速度过低: {avg_speed:.0f}样本/�?
    
    def test_memory_usage_large_data(self):
        """测试大数据内存使�?""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        config = {
            'detectors': {
                'iforest': {'enabled': True, 'type': 'iforest', 'params': {'n_estimators': 50}},
                'lof': {'enabled': True, 'type': 'lof', 'params': {'n_neighbors': 20}}
            },
            'ensemble': {'method': 'average', 'min_detectors': 2},
            'threshold': {'optimization': {'enabled': True}},
            'preprocessing': {'scale_features': True}
        }
        
        detector = PyodAnomalyDetector(config)
        
        # 创建大规模数�?
        n_samples = 50000
        n_features = 30
        X = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行检�?
        result = detector.detect_anomalies(
            X=X,
            detection_mode='unsupervised',
            ensemble_method='average'
        )
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        print(f"样本�? {n_samples}, 特征�? {n_features}")
        print(f"内存增加: {memory_increase:.2f}MB")
        print(f"检测到异常: {np.sum(result.anomaly_labels)}")
        
        # 验证内存使用
        assert memory_increase < 2048  # 内存增加不超�?GB
        assert memory_increase / n_samples < 0.05  # 每样本内存增加小�?.05MB
    
    def test_real_time_performance(self):
        """测试实时性能"""
        import time
        
        config = {
            'detectors': {
                'iforest': {'enabled': True, 'type': 'iforest', 'params': {'n_estimators': 50}}
            },
            'ensemble': {'method': 'average', 'min_detectors': 1},
            'threshold': {'optimization': {'enabled': False}, 'default': 0.9},
            'preprocessing': {'scale_features': True},
            'performance': {
                'real_time': {
                    'enabled': True,
                    'processing_latency': 100,
                    'batch_processing': False
                }
            }
        }
        
        detector = PyodAnomalyDetector(config)
        
        # 训练检测器
        n_train_samples = 10000
        n_features = 20
        X_train = pd.DataFrame(
            np.random.randn(n_train_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        
        detector.detect_anomalies(X_train, detection_mode='unsupervised')
        
        # 测试实时检测延�?
        latencies = []
        
        for i in range(100):
            # 单个样本检�?
            X_single = pd.DataFrame(
                np.random.randn(1, n_features),
                columns=[f'feature_{i}' for i in range(n_features)]
            )
            
            start_time = time.perf_counter()
            result = detector.detect_anomalies(
                X_single,
                detection_mode='unsupervised'
            )
            end_time = time.perf_counter()
            
            latency = (end_time - start_time) * 1000  # 转换为毫�?
            latencies.append(latency)
        
        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
        max_latency = np.max(latencies)
        
        print(f"平均延迟: {avg_latency:.2f}ms")
        print(f"P95延迟: {p95_latency:.2f}ms")
        print(f"最大延�? {max_latency:.2f}ms")
        
        # 验证实时性能要求
        assert avg_latency < 50  # 平均延迟小于50ms
        assert p95_latency < 100  # 95%的延迟小�?00ms
        assert max_latency < 200  # 最大延迟小�?00ms
```

---

## 📊 监控设计

### 6.1 监控指标
```python
# monitoring/anomaly_detection_monitor.py
class AnomalyDetectionMonitor:
    """异常检测监�?""
    
    METRICS = [
        'data_volume',
        'feature_count',
        'anomaly_count',
        'anomaly_ratio',
        'detection_latency',
        'processing_throughput',
        'false_positive_rate',
        'true_positive_rate',
        'precision',
        'recall',
        'f1_score',
        'auc_roc',
        'detector_performance',
        'threshold_value',
        'memory_usage',
        'cpu_utilization',
        'alert_count',
        'feedback_accuracy'
    ]
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        self.metrics_history = []
        self.alerts = []
        self.performance_baseline = {}
        self.drift_detector = DataDriftDetector()
        
    def record_detection_metrics(self, detection_result: AnomalyDetectionResult, metadata: Dict[str, Any]):
        """记录检测指�?""
        metrics = {
            'timestamp': datetime.now(),
            'system_id': self.system_id,
            'data_volume': metadata.get('sample_count', 0),
            'feature_count': metadata.get('feature_count', 0),
            'anomaly_count': int(np.sum(detection_result.anomaly_labels)),
            'anomaly_ratio': float(np.mean(detection_result.anomaly_labels)),
            'threshold_value': float(detection_result.threshold)
        }
        
        # 添加性能指标（如果有真实标签�?
        if 'ground_truth' in metadata:
            self._add_performance_metrics(metrics, detection_result, metadata['ground_truth'])
        
        # 添加系统指标
        self._add_system_metrics(metrics)
        
        self.metrics_history.append(metrics)
        
        # 更新性能基线
        self._update_performance_baseline(metrics)
        
        # 检查异�?
        self._check_detection_anomalies(metrics, detection_result)
        
        # 检查数据漂�?
        if 'features' in metadata:
            self._check_data_drift(metadata['features'], metrics['timestamp'])
    
    def _add_performance_metrics(self, metrics: Dict[str, Any], detection_result: AnomalyDetectionResult, ground_truth: pd.Series):
        """添加性能指标"""
        from sklearn.metrics import (
            precision_score, recall_score, f1_score,
            roc_auc_score, confusion_matrix
        )
        
        y_true = ground_truth.values
        y_pred = detection_result.anomaly_labels
        
        # 确保形状一�?
        if len(y_true) == len(y_pred):
            try:
                metrics['precision'] = float(precision_score(y_true, y_pred, zero_division=0))
                metrics['recall'] = float(recall_score(y_true, y_pred, zero_division=0))
                metrics['f1_score'] = float(f1_score(y_true, y_pred, zero_division=0))
                
                # AUC-ROC（需要概率分数）
                if hasattr(detection_result, 'anomaly_scores'):
                    y_scores = detection_result.anomaly_scores
                    if len(np.unique(y_true)) > 1:  # 需要正负样�?
                        metrics['auc_roc'] = float(roc_auc_score(y_true, y_scores))
                
                # 混淆矩阵
                tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
                metrics['true_positive'] = int(tp)
                metrics['false_positive'] = int(fp)
                metrics['true_negative'] = int(tn)
                metrics['false_negative'] = int(fn)
                metrics['false_positive_rate'] = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
                metrics['true_positive_rate'] = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
                
            except Exception as e:
                print(f"计算性能指标失败: {str(e)}")
    
    def _add_system_metrics(self, metrics: Dict[str, Any]):
        """添加系统指标"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        metrics['memory_usage'] = process.memory_info().rss / 1024 / 1024  # MB
        metrics['cpu_utilization'] = process.cpu_percent(interval=0.1)
        metrics['thread_count'] = process.num_threads()
        
        # 系统级别指标
        system_memory = psutil.virtual_memory()
        metrics['system_memory_percent'] = system_memory.percent
        metrics['system_cpu_percent'] = psutil.cpu_percent(interval=0.1)
    
    def _update_performance_baseline(self, metrics: Dict[str, Any]):
        """更新性能基线"""
        for metric_name in ['anomaly_ratio', 'precision', 'recall', 'f1_score']:
            if metric_name in metrics:
                if metric_name not in self.performance_baseline:
                    self.performance_baseline[metric_name] = {
                        'values': [],
                        'mean': None,
                        'std': None
                    }
                
                baseline = self.performance_baseline[metric_name]
                baseline['values'].append(metrics[metric_name])
                
                # 保持最�?00个�?
                if len(baseline['values']) > 100:
                    baseline['values'] = baseline['values'][-100:]
                
                # 重新计算统计�?
                if len(baseline['values']) >= 10:
                    baseline['mean'] = np.mean(baseline['values'])
                    baseline['std'] = np.std(baseline['values'])
    
    def _check_detection_anomalies(self, metrics: Dict[str, Any], detection_result: AnomalyDetectionResult):
        """检查检测异�?""
        alerts = []
        
        # 异常比例异常
        if 'anomaly_ratio' in metrics and 'anomaly_ratio' in self.performance_baseline:
            baseline = self.performance_baseline['anomaly_ratio']
            if baseline['mean'] is not None and baseline['std'] is not None:
                current_value = metrics['anomaly_ratio']
                z_score = abs(current_value - baseline['mean']) / baseline['std'] if baseline['std'] > 0 else 0
                
                if z_score > 3:  # 3sigma异常
                    alerts.append({
                        'type': 'anomaly_ratio_outlier',
                        'severity': 'warning',
                        'message': f'异常比例异常: {current_value:.3f} (基准: {baseline["mean"]:.3f}±{baseline["std"]:.3f})',
                        'z_score': z_score,
                        'threshold': 3
                    })
        
        # 性能下降
        for metric_name in ['precision', 'recall', 'f1_score']:
            if metric_name in metrics and metric_name in self.performance_baseline:
                baseline = self.performance_baseline[metric_name]
                if baseline['mean'] is not None and baseline['std'] is not None:
                    current_value = metrics[metric_name]
                    # 检查是否显著下降（超过2个标准差�?
                    if current_value < baseline['mean'] - 2 * baseline['std']:
                        alerts.append({
                            'type': f'{metric_name}_degradation',
                            'severity': 'critical',
                            'message': f'{metric_name}下降: {current_value:.3f} (基准: {baseline["mean"]:.3f}±{baseline["std"]:.3f})',
                            'decrease': baseline['mean'] - current_value,
                            'threshold': 2
                        })
        
        # 假阳性率过高
        if 'false_positive_rate' in metrics:
            fpr = metrics['false_positive_rate']
            if fpr > 0.1:  # 假阳性率超过10%
                alerts.append({
                    'type': 'high_false_positive_rate',
                    'severity': 'warning',
                    'message': f'假阳性率过高: {fpr:.3f}',
                    'value': fpr,
                    'threshold': 0.1
                })
        
        # 检测延迟过�?
        if 'detection_latency' in metrics:
            latency = metrics.get('detection_latency', 0)
            if latency > 1000:  # 延迟超过1�?
                alerts.append({
                    'type': 'high_detection_latency',
                    'severity': 'warning',
                    'message': f'检测延迟过�? {latency:.0f}ms',
                    'value': latency,
                    'threshold': 1000
                })
        
        # 内存使用过高
        if 'memory_usage' in metrics:
            memory = metrics['memory_usage']
            if memory > 2048:  # 内存超过2GB
                alerts.append({
                    'type': 'high_memory_usage',
                    'severity': 'critical',
                    'message': f'内存使用过高: {memory:.0f}MB',
                    'value': memory,
                    'threshold': 2048
                })
        
        # 存储告警
        for alert in alerts:
            alert['timestamp'] = metrics['timestamp']
            alert['system_id'] = self.system_id
            self.alerts.append(alert)
            
            # 发送告警（调用外部通知系统�?
            self._send_alert(alert)
    
    def _check_data_drift(self, features: pd.DataFrame, timestamp: datetime):
        """检查数据漂�?""
        if len(features) == 0:
            return
        
        # 检查特征分布漂�?
        drift_result = self.drift_detector.detect_drift(features)
        
        if drift_result['has_drift']:
            self.alerts.append({
                'type': 'data_drift_detected',
                'severity': 'warning',
                'message': f'数据漂移检�? {drift_result["drift_score"]:.3f}',
                'drift_score': drift_result['drift_score'],
                'affected_features': drift_result['affected_features'],
                'timestamp': timestamp,
                'system_id': self.system_id
            })
    
    def _send_alert(self, alert: Dict[str, Any]):
        """发送告�?""
        # 这里集成到外部通知系统
        # 例如：发送到Slack、Email、短信等
        print(f"告警: [{alert['severity']}] {alert['message']}")
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """获取性能报告"""
        recent_metrics = [
            m for m in self.metrics_history
            if m['timestamp'] > datetime.now() - timedelta(hours=hours)
        ]
        
        if not recent_metrics:
            return {}
        
        df = pd.DataFrame(recent_metrics)
        
        report = {
            'time_range': {
                'start': df['timestamp'].min(),
                'end': df['timestamp'].max()
            },
            'summary': {
                'total_detections': len(df),
                'total_samples': int(df['data_volume'].sum()),
                'total_anomalies': int(df['anomaly_count'].sum()),
                'avg_anomaly_ratio': float(df['anomaly_ratio'].mean())
            },
            'performance_metrics': {},
            'alerts_summary': {
                'total_alerts': len(self.alerts),
                'alerts_by_severity': {},
                'alerts_by_type': {}
            },
            'system_metrics': {
                'avg_memory_usage': float(df['memory_usage'].mean()),
                'max_memory_usage': float(df['memory_usage'].max()),
                'avg_cpu_utilization': float(df['cpu_utilization'].mean()),
                'max_cpu_utilization': float(df['cpu_utilization'].max())
            }
        }
        
        # 性能指标（如果可用）
        performance_metrics = ['precision', 'recall', 'f1_score', 'auc_roc', 'false_positive_rate']
        for metric in performance_metrics:
            if metric in df.columns:
                report['performance_metrics'][metric] = {
                    'mean': float(df[metric].mean()),
                    'std': float(df[metric].std()),
                    'min': float(df[metric].min()),
                    'max': float(df[metric].max()),
                    'median': float(df[metric].median())
                }
        
        # 告警统计
        recent_alerts = [
            a for a in self.alerts
            if a['timestamp'] > datetime.now() - timedelta(hours=hours)
        ]
        
        if recent_alerts:
            alert_df = pd.DataFrame(recent_alerts)
            report['alerts_summary']['alerts_by_severity'] = alert_df['severity'].value_counts().to_dict()
            report['alerts_summary']['alerts_by_type'] = alert_df['type'].value_counts().to_dict()
        
        return report
```

### 6.2 告警规则
```python
# monitoring/alert_rules.py
class AnomalyDetectionAlertRules:
    """异常检测告警规�?""
    
    RULES = {
        # 性能相关告警
        'performance_degradation': {
            'enabled': True,
            'severity': 'critical',
            'condition': lambda metrics: (
                metrics.get('precision', 1.0) < 0.7 or
                metrics.get('recall', 1.0) < 0.7 or
                metrics.get('f1_score', 1.0) < 0.7
            ),
            'message': '检测性能下降，请检查数据质量或重新训练模型'
        },
        
        'high_false_positive_rate': {
            'enabled': True,
            'severity': 'warning',
            'condition': lambda metrics: metrics.get('false_positive_rate', 0) > 0.1,
            'message': '假阳性率过高，可能导致过多误�?
        },
        
        'low_anomaly_detection': {
            'enabled': True,
            'severity': 'info',
            'condition': lambda metrics: metrics.get('anomaly_ratio', 0) < 0.01,
            'message': '异常检测率过低，可能漏报异�?
        },
        
        'high_anomaly_detection': {
            'enabled': True,
            'severity': 'warning',
            'condition': lambda metrics: metrics.get('anomaly_ratio', 0) > 0.3,
            'message': '异常检测率过高，可能误报正常数�?
        },
        
        # 系统相关告警
        'high_detection_latency': {
            'enabled': True,
            'severity': 'warning',
            'condition': lambda metrics: metrics.get('detection_latency', 0) > 1000,
            'message': '检测延迟过高，影响实时�?
        },
        
        'high_memory_usage': {
            'enabled': True,
            'severity': 'critical',
            'condition': lambda metrics: metrics.get('memory_usage', 0) > 2048,
            'message': '内存使用过高，可能影响系统稳定�?
        },
        
        'high_cpu_utilization': {
            'enabled': True,
            'severity': 'warning',
            'condition': lambda metrics: metrics.get('cpu_utilization', 0) > 80,
            'message': 'CPU使用率过高，可能影响系统性能'
        },
        
        # 数据相关告警
        'data_drift_detected': {
            'enabled': True,
            'severity': 'warning',
            'condition': lambda metrics: metrics.get('data_drift_score', 0) > 0.2,
            'message': '检测到数据漂移，可能需要更新模�?
        },
        
        'low_data_volume': {
            'enabled': True,
            'severity': 'info',
            'condition': lambda metrics: metrics.get('data_volume', 0) < 100,
            'message': '数据量不足，可能影响检测准确�?
        },
        
        'high_missing_rate': {
            'enabled': True,
            'severity': 'warning',
            'condition': lambda metrics: metrics.get('missing_rate', 0) > 0.1,
            'message': '数据缺失率过高，可能影响检测准确�?
        },
        
        # 业务相关告警
        'consecutive_anomalies': {
            'enabled': True,
            'severity': 'critical',
            'condition': lambda metrics: metrics.get('consecutive_anomalies', 0) > 5,
            'message': '连续检测到多个异常，可能存在系统性风�?
        },
        
        'anomaly_cluster_detected': {
            'enabled': True,
            'severity': 'warning',
            'condition': lambda metrics: metrics.get('anomaly_cluster_score', 0) > 0.8,
            'message': '检测到异常聚集，可能存在模式异�?
        },
        
        'unusual_temporal_pattern': {
            'enabled': True,
            'severity': 'info',
            'condition': lambda metrics: metrics.get('temporal_anomaly_score', 0) > 0.7,
            'message': '检测到异常时间模式'
        }
    }
    
    def evaluate_alerts(self, metrics: Dict[str, Any], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """评估告警规则"""
        alerts = []
        context = context or {}
        
        for rule_name, rule_config in self.RULES.items():
            if not rule_config['enabled']:
                continue
            
            try:
                # 检查条�?
                if rule_config:
                    alert = {
                        'rule': rule_name,
                        'severity': rule_config['severity'],
                        'message': rule_config['message'],
                        'timestamp': datetime.now(),
                        'metrics': {k: v for k, v in metrics.items() if not callable(v)},
                        'context': context
                    }
                    
                    # 添加上下文信�?
                    if 'anomaly_details' in context:
                        alert['anomaly_details'] = context['anomaly_details']
                    
                    alerts.append(alert)
                    
            except Exception as e:
                print(f"评估告警规则 {rule_name} 失败: {str(e)}")
                continue
        
        # 按严重性排�?
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return alerts
    
    def suppress_similar_alerts(self, alerts: List[Dict[str, Any]], cooldown_period: int = 300) -> List[Dict[str, Any]]:
        """抑制相似告警（冷却期�?""
        if not alerts:
            return []
        
        suppressed_alerts = []
        last_alert_time = {}
        
        for alert in alerts:
            rule_name = alert['rule']
            current_time = alert['timestamp']
            
            # 检查冷却期
            if rule_name in last_alert_time:
                time_since_last = (current_time - last_alert_time[rule_name]).total_seconds()
                if time_since_last < cooldown_period:
                    continue  # 跳过，仍在冷却期�?
            
            # 更新最后告警时�?
            last_alert_time[rule_name] = current_time
            suppressed_alerts.append(alert)
        
        return suppressed_alerts
```

---
## 🚀 部署设计

### 7.1 部署脚本
```python
# deployment/deploy_anomaly_detector.py
#!/usr/bin/env python3
"""
异常检测模块部署脚�?
"""

import os
import sys
import yaml
import argparse
import subprocess
import logging
from pathlib import Path

class AnomalyDetectorDeployer:
    """异常检测部署器"""
    
    def __init__(self, config_path: str, environment: str = 'production'):
        self.config_path = config_path
        self.environment = environment
        self.project_root = Path(__file__).parent.parent.parent
        
        # 设置日志
        self._setup_logging()
        
        # 加载配置
        self.config = self._load_config()
    
    def _setup_logging(self):
        """设置日志"""
        log_dir = self.project_root / 'logs' / 'deployment'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'anomaly_detector_deploy_{self.environment}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # 根据环境选择配置
        env_config = config.get('environments', {}).get(self.environment, {})
        config.update(env_config)
        
        return config
    
    def run(self):
        """运行部署流程"""
        self.logger.info(f"开始部署异常检测模块到 {self.environment} 环境")
        
        try:
            # 1. 验证环境
            self._validate_environment()
            
            # 2. 检查依�?
            self._check_dependencies()
            
            # 3. 安装依赖
            self._install_dependencies()
            
            # 4. 配置环境
            self._configure_environment()
            
            # 5. 部署代码
            self._deploy_code()
            
            # 6. 初始化数据库
            self._initialize_database()
            
            # 7. 启动服务
            self._start_services()
            
            # 8. 运行健康检�?
            self._run_health_checks()
            
            # 9. 验证部署
            self._verify_deployment()
            
            self.logger.info("部署成功完成")
            return True
            
        except Exception as e:
            self.logger.error(f"部署失败: {str(e)}", exc_info=True)
            self._rollback_deployment()
            return False
    
    def _validate_environment(self):
        """验证环境"""
        self.logger.info("验证部署环境")
        
        # 检查Python版本
        python_version = sys.version_info
        required_version = (3, 8, 0)
        
        if python_version < required_version:
            raise RuntimeError(f"Python版本需�?{required_version} 或更高，当前版本: {python_version}")
        
        # 检查可用内�?
        if self.environment == 'production':
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.available < 4 * 1024 * 1024 * 1024:  # 4GB
                self.logger.warning(f"可用内存不足: {memory.available / 1024 / 1024 / 1024:.1f}GB")
        
        # 检查磁盘空�?
        disk_usage = psutil.disk_usage('/')
        if disk_usage.free < 10 * 1024 * 1024 * 1024:  # 10GB
            self.logger.warning(f"磁盘空间不足: {disk_usage.free / 1024 / 1024 / 1024:.1f}GB")
        
        self.logger.info("环境验证通过")
    
    def _check_dependencies(self):
        """检查依�?""
        self.logger.info("检查系统依�?)
        
        required_commands = [
            'git', 'python3', 'pip', 'docker', 'redis-cli'
        ]
        
        missing_commands = []
        for cmd in required_commands:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                self.logger.debug(f"�?{cmd} 可用")
            except (subprocess.SubprocessError, FileNotFoundError):
                missing_commands.append(cmd)
                self.logger.warning(f"�?{cmd} 不可�?)
        
        if missing_commands:
            self.logger.warning(f"缺少命令: {', '.join(missing_commands)}")
            # 非阻塞，继续部署
    
    def _install_dependencies(self):
        """安装依赖"""
        self.logger.info("安装Python依赖")
        
        requirements_files = [
            self.project_root / 'requirements.txt',
            self.project_root / 'requirements_extra.txt',
            self.project_root / 'docs' / 'module_designs' / 'layer_9' / 'requirements_anomaly.txt'
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                self.logger.info(f"安装依赖: {req_file}")
                
                cmd = [
                    sys.executable, '-m', 'pip', 'install',
                    '-r', str(req_file),
                    '--upgrade'
                ]
                
                if self.environment == 'production':
                    cmd.append('--no-cache-dir')
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    self.logger.debug(f"安装输出: {result.stdout[:500]}")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"安装失败: {e.stderr}")
                    raise
    
    def _configure_environment(self):
        """配置环境"""
        self.logger.info("配置环境变量")
        
        # 创建环境配置文件
        env_file = self.project_root / '.env' / f'{self.environment}.env'
        env_file.parent.mkdir(parents=True, exist_ok=True)
        
        env_vars = self.config.get('environment_variables', {})
        
        with open(env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        # 设置环境变量
        for key, value in env_vars.items():
            os.environ[key] = str(value)
        
        self.logger.info(f"环境变量已写�? {env_file}")
    
    def _deploy_code(self):
        """部署代码"""
        self.logger.info("部署代码")
        
        # 目标目录
        deploy_dir = Path(self.config.get('deploy_directory', '/opt/zephyralpha/anomaly_detector'))
        
        # 确保目录存在
        deploy_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制代码
        source_dirs = [
            self.project_root / 'docs' / 'module_designs' / 'layer_9',
            self.project_root / 'src' / 'anomaly_detection'
        ]
        
        for source_dir in source_dirs:
            if source_dir.exists():
                dest_dir = deploy_dir / source_dir.relative_to(self.project_root)
                dest_dir.parent.mkdir(parents=True, exist_ok=True)
                
                self.logger.info(f"复制: {source_dir} -> {dest_dir}")
                
                # 使用rsync或cp（简化版�?
                import shutil
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(source_dir, dest_dir)
        
        # 复制配置文件
        config_files = [
            self.config_path,
            self.project_root / 'config' / 'pyod_config.yaml'
        ]
        
        for config_file in config_files:
            if config_file.exists():
                dest_file = deploy_dir / 'config' / config_file.name
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(config_file, dest_file)
        
        self.logger.info(f"代码已部署到: {deploy_dir}")
    
    def _initialize_database(self):
        """初始化数据库"""
        self.logger.info("初始化数据库")
        
        db_config = self.config.get('database', {})
        
        if not db_config.get('enabled', True):
            self.logger.info("数据库未启用，跳过初始化")
            return
        
        # 初始化异常检测数据库
        from L9_ANOMALY_DETECTOR.database import AnomalyDetectionDatabase
        
        db = AnomalyDetectionDatabase(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 5432),
            database=db_config.get('database', 'anomaly_detection'),
            user=db_config.get('user', 'postgres'),
            password=db_config.get('password', '')
        )
        
        db.initialize_tables()
        db.create_indexes()
        
        self.logger.info("数据库初始化完成")
    
    def _start_services(self):
        """启动服务"""
        self.logger.info("启动异常检测服�?)
        
        services = self.config.get('services', {})
        
        # 启动主检测服�?
        if services.get('detection_service', {}).get('enabled', True):
            self._start_detection_service()
        
        # 启动监控服务
        if services.get('monitoring_service', {}).get('enabled', True):
            self._start_monitoring_service()
        
        # 启动API服务
        if services.get('api_service', {}).get('enabled', True):
            self._start_api_service()
        
        self.logger.info("所有服务已启动")
    
    def _start_detection_service(self):
        """启动检测服�?""
        self.logger.info("启动异常检测服�?)
        
        service_config = self.config['services']['detection_service']
        
        cmd = [
            sys.executable,
            '-m', 'L9_ANOMALY_DETECTOR.anomaly_detection_service',
            '--config', service_config.get('config_path', '/opt/zephyralpha/anomaly_detector/config/pyod_config.yaml'),
            '--mode', service_config.get('mode', 'production'),
            '--log-level', service_config.get('log_level', 'INFO')
        ]
        
        # 后台运行
        if service_config.get('daemon', True):
            import daemon
            from daemon.pidfile import TimeoutPIDLockFile
            
            pid_file = Path(service_config.get('pid_file', '/var/run/anomaly_detector.pid'))
            pid_file.parent.mkdir(parents=True, exist_ok=True)
            
            context = daemon.DaemonContext(
                working_directory='/opt/zephyralpha/anomaly_detector',
                umask=0o002,
                pidfile=TimeoutPIDLockFile(str(pid_file)),
                stdout=open('/var/log/anomaly_detector.log', 'w'),
                stderr=open('/var/log/anomaly_detector.error.log', 'w')
            )
            
            with context:
                subprocess.run(cmd)
        else:
            # 前台运行
            subprocess.run(cmd)
    
    def _run_health_checks(self):
        """运行健康检�?""
        self.logger.info("运行健康检�?)
        
        import time
        import requests
        
        health_endpoints = self.config.get('health_check', {}).get('endpoints', [])
        
        for endpoint in health_endpoints:
            url = endpoint['url']
            timeout = endpoint.get('timeout', 30)
            retries = endpoint.get('retries', 3)
            
            for attempt in range(retries):
                try:
                    self.logger.info(f"检查健康端�? {url} (尝试 {attempt+1}/{retries})")
                    
                    response = requests.get(url, timeout=timeout)
                    
                    if response.status_code == 200:
                        self.logger.info(f"�?{url} 健康")
                        break
                    else:
                        self.logger.warning(f"�?{url} 不健�? {response.status_code}")
                        
                except Exception as e:
                    self.logger.warning(f"�?{url} 检查失�? {str(e)}")
                
                if attempt < retries - 1:
                    time.sleep(5)  # 重试前等�?
            else:
                self.logger.error(f"健康检查失�? {url}")
    
    def _verify_deployment(self):
        """验证部署"""
        self.logger.info("验证部署")
        
        # 运行测试
        test_config = self.config.get('verification', {}).get('tests', {})
        
        if test_config.get('run_unit_tests', True):
            self._run_unit_tests()
        
        if test_config.get('run_integration_tests', False):
            self._run_integration_tests()
        
        if test_config.get('run_performance_tests', False):
            self._run_performance_tests()
        
        # 验证功能
        self._verify_functionality()
        
        self.logger.info("部署验证通过")
    
    def _rollback_deployment(self):
        """回滚部署"""
        self.logger.info("开始回滚部�?)
        
        # 停止服务
        self._stop_services()
        
        # 恢复备份
        backup_dir = Path(self.config.get('backup_directory', '/var/backup/anomaly_detector'))
        
        if backup_dir.exists():
            deploy_dir = Path(self.config.get('deploy_directory', '/opt/zephyralpha/anomaly_detector'))
            
            if deploy_dir.exists():
                import shutil
                shutil.rmtree(deploy_dir)
            
            shutil.copytree(backup_dir, deploy_dir)
            
            self.logger.info(f"已从备份恢复: {backup_dir}")
        
        self.logger.info("回滚完成")

def main():
    """主函�?""
    parser = argparse.ArgumentParser(description='部署异常检测模�?)
    parser.add_argument('--config', required=True, help='配置文件路径')
    parser.add_argument('--environment', default='production', choices=['development', 'staging', 'production'],
                       help='部署环境')
    parser.add_argument('--dry-run', action='store_true', help='干运行（不实际部署）')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("干运行模式，不实际部�?)
        print(f"配置: {args.config}")
        print(f"环境: {args.environment}")
        return
    
    deployer = AnomalyDetectorDeployer(args.config, args.environment)
    success = deployer.run()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

### 7.2 调度配置
```yaml
# deployment/scheduler_config.yaml
scheduling:
  # 实时检测任�?
  real_time_detection:
    enabled: true
    schedule: "*/1 * * * *"  # 每分钟执�?
    command: "python -m L9_ANOMALY_DETECTOR.real_time_detector"
    args:
      - "--config"
      - "/opt/zephyralpha/anomaly_detector/config/pyod_config.yaml"
      - "--mode"
      - "real_time"
      - "--window-size"
      - "1000"
    resources:
      memory: "1GB"
      cpu: "1"
      timeout: "5m"
    retry_policy:
      max_retries: 3
      backoff_delay: "30s"
    
  # 批量检测任�?
  batch_detection:
    enabled: true
    schedule: "0 2 * * *"  # 每天凌晨2�?
    command: "python -m L9_ANOMALY_DETECTOR.batch_detector"
    args:
      - "--config"
      - "/opt/zephyralpha/anomaly_detector/config/pyod_config.yaml"
      - "--date"
      - "yesterday"
      - "--data-source"
      - "ifind"
    resources:
      memory: "2GB"
      cpu: "2"
      timeout: "2h"
    
  # 模型重训练任�?
  model_retraining:
    enabled: true
    schedule: "0 3 * * 0"  # 每周日凌�?�?
    command: "python -m L9_ANOMALY_DETECTOR.model_retrainer"
    args:
      - "--config"
      - "/opt/zephyralpha/anomaly_detector/config/pyod_config.yaml"
      - "--training-data"
      - "last_30_days"
      - "--retrain-mode"
      - "full"
    resources:
      memory: "4GB"
      cpu: "4"
      timeout: "4h"
    
  # 性能监控任务
  performance_monitoring:
    enabled: true
    schedule: "*/5 * * * *"  # �?分钟
    command: "python -m L9_ANOMALY_DETECTOR.performance_monitor"
    args:
      - "--config"
      - "/opt/zephyralpha/anomaly_detector/config/pyod_config.yaml"
      - "--metrics"
      - "all"
      - "--output"
      - "/var/log/anomaly_detector/metrics.json"
    resources:
      memory: "512MB"
      cpu: "0.5"
      timeout: "10m"
    
  # 数据清理任务
  data_cleanup:
    enabled: true
    schedule: "0 4 * * *"  # 每天凌晨4�?
    command: "python -m L9_ANOMALY_DETECTOR.data_cleaner"
    args:
      - "--config"
      - "/opt/zephyralpha/anomaly_detector/config/pyod_config.yaml"
      - "--retention-days"
      - "30"
      - "--cleanup-mode"
      - "anomaly_data"
    resources:
      memory: "1GB"
      cpu: "1"
      timeout: "1h"
    
  # 报告生成任务
  report_generation:
    enabled: true
    schedule: "0 6 * * *"  # 每天凌晨6�?
    command: "python -m L9_ANOMALY_DETECTOR.report_generator"
    args:
      - "--config"
      - "/opt/zephyralpha/anomaly_detector/config/pyod_config.yaml"
      - "--period"
      - "daily"
      - "--output-format"
      - "html,pdf"
      - "--recipients"
      - "alerts@zephyralpha.com"
    resources:
      memory: "2GB"
      cpu: "2"
      timeout: "1h"

execution:
  # 执行器配�?
  executor: "kubernetes"  # kubernetes | docker | systemd | cron
  
  kubernetes:
    namespace: "zephyralpha-anomaly"
    service_account: "anomaly-detector-sa"
    image_pull_secrets: ["registry-secret"]
    
  docker:
    network: "zephyralpha-network"
    volumes:
      - "/opt/zephyralpha/anomaly_detector:/app"
      - "/var/log/anomaly_detector:/var/log"
      - "/var/lib/anomaly_detector:/var/lib"
    
  systemd:
    user: "anomaly_detector"
    group: "anomaly_detector"
    working_directory: "/opt/zephyralpha/anomaly_detector"
    
  cron:
    user: "anomaly_detector"
    mailto: "alerts@zephyralpha.com"

monitoring:
  # 调度监控
  job_monitoring:
    enabled: true
    metrics:
      - "job_success_rate"
      - "job_duration"
      - "job_failure_rate"
      - "resource_utilization"
    
    alerts:
      - metric: "job_success_rate"
        condition: "< 0.9"
        severity: "critical"
        message: "任务成功率过�?
        
      - metric: "job_duration"
        condition: "> 2h"
        severity: "warning"
        message: "任务执行时间过长"
        
      - metric: "job_failure_rate"
        condition: "> 0.1"
        severity: "critical"
        message: "任务失败率过�?
    
    dashboard:
      enabled: true
      url: "http://localhost:3000/d/anomaly_detector_scheduler"
      refresh_interval: "30s"

backup:
  # 备份配置
  enabled: true
  schedule: "0 1 * * *"  # 每天凌晨1�?
  retention_days: 7
  
  backup_items:
    - name: "configuration"
      paths:
        - "/opt/zephyralpha/anomaly_detector/config"
      compression: "gzip"
      
    - name: "models"
      paths:
        - "/opt/zephyralpha/anomaly_detector/models"
      compression: "gzip"
      
    - name: "database"
      type: "postgres"
      database: "anomaly_detection"
      compression: "gzip"
      
    - name: "logs"
      paths:
        - "/var/log/anomaly_detector"
      retention_days: 30
      compression: "gzip"
  
  storage:
    type: "s3"  # s3 | local | nfs
    s3:
      bucket: "zephyralpha-backups"
      prefix: "anomaly_detector/"
      region: "us-east-1"
    
    local:
      path: "/var/backup/anomaly_detector"
      
    nfs:
      server: "nfs.example.com"
      path: "/backup/anomaly_detector"
```

### 7.3 环境配置
```yaml
# deployment/environments.yaml
environments:
  development:
    description: "开发环�?
    
    # 数据库配�?
    database:
      host: "localhost"
      port: 5432
      database: "anomaly_detection_dev"
      user: "postgres"
      password: "dev_password"
      pool_size: 5
      
    # Redis配置
    redis:
      host: "localhost"
      port: 6379
      db: 0
      password: ""
      
    # 服务配置
    services:
      detection_service:
        enabled: true
        mode: "development"
        log_level: "DEBUG"
        daemon: false
        
      monitoring_service:
        enabled: true
        interval: "10s"
        metrics_port: 9090
        
      api_service:
        enabled: true
        host: "0.0.0.0"
        port: 8000
        debug: true
        
    # 性能配置
    performance:
      batch_size: 100
      n_jobs: 2
      memory_limit: "512MB"
      use_gpu: false
      
    # 监控配置
    monitoring:
      metrics_logging: true
      real_time_dashboard: true
      alerting: false
      
    # 部署配置
    deployment:
      deploy_directory: "/tmp/zephyralpha/anomaly_detector_dev"
      backup_directory: "/tmp/backup/anomaly_detector_dev"
      
  staging:
    description: "预发布环�?
    
    # 数据库配�?
    database:
      host: "staging-db.example.com"
      port: 5432
      database: "anomaly_detection_staging"
      user: "anomaly_user"
      password: "${DB_PASSWORD}"
      pool_size: 10
      
    # Redis配置
    redis:
      host: "staging-redis.example.com"
      port: 6379
      db: 1
      password: "${REDIS_PASSWORD}"
      
    # 服务配置
    services:
      detection_service:
        enabled: true
        mode: "staging"
        log_level: "INFO"
        daemon: true
        pid_file: "/var/run/anomaly_detector_staging.pid"
        
      monitoring_service:
        enabled: true
        interval: "30s"
        metrics_port: 9091
        
      api_service:
        enabled: true
        host: "0.0.0.0"
        port: 8001
        debug: false
        
    # 性能配置
    performance:
      batch_size: 1000
      n_jobs: 4
      memory_limit: "2GB"
      use_gpu: false
      
    # 监控配置
    monitoring:
      metrics_logging: true
      real_time_dashboard: true
      alerting: true
      alert_channels: ["email", "slack"]
      
    # 部署配置
    deployment:
      deploy_directory: "/opt/zephyralpha/anomaly_detector_staging"
      backup_directory: "/var/backup/anomaly_detector_staging"
      
  production:
    description: "生产环境"
    
    # 数据库配置（高可用）
    database:
      host: "prod-db-cluster.example.com"
      port: 5432
      database: "anomaly_detection_prod"
      user: "anomaly_prod_user"
      password: "${PROD_DB_PASSWORD}"
      pool_size: 20
      ssl_mode: "require"
      read_replicas:
        - host: "prod-db-replica1.example.com"
          port: 5432
        - host: "prod-db-replica2.example.com"
          port: 5432
          
    # Redis配置（集群）
    redis:
      cluster_mode: true
      nodes:
        - host: "prod-redis-node1.example.com"
          port: 6379
        - host: "prod-redis-node2.example.com"
          port: 6379
        - host: "prod-redis-node3.example.com"
          port: 6379
      password: "${PROD_REDIS_PASSWORD}"
      
    # 服务配置
    services:
      detection_service:
        enabled: true
        mode: "production"
        log_level: "WARNING"
        daemon: true
        pid_file: "/var/run/anomaly_detector.pid"
        replicas: 3
        
      monitoring_service:
        enabled: true
        interval: "60s"
        metrics_port: 9092
        replicas: 2
        
      api_service:
        enabled: true
        host: "0.0.0.0"
        port: 8002
        debug: false
        replicas: 3
        load_balancer: true
        
    # 性能配置
    performance:
      batch_size: 5000
      n_jobs: 8
      memory_limit: "8GB"
      use_gpu: true
      gpu_device: 0
      
    # 监控配置
    monitoring:
      metrics_logging: true
      real_time_dashboard: true
      alerting: true
      alert_channels: ["email", "slack", "sms", "pagerduty"]
      alert_cooldown: "5m"
      
    # 安全配置
    security:
      ssl_enabled: true
      authentication: true
      rate_limiting: true
      audit_logging: true
      
    # 高可用配�?
    high_availability:
      enabled: true
      zones: ["us-east-1a", "us-east-1b", "us-east-1c"]
      auto_scaling:
        enabled: true
        min_replicas: 2
        max_replicas: 10
        cpu_threshold: 70
        memory_threshold: 80
        
    # 部署配置
    deployment:
      deploy_directory: "/opt/zephyralpha/anomaly_detector"
      backup_directory: "/var/backup/anomaly_detector"
      rolling_update: true
      max_unavailable: 1
      max_surge: 1
```

---
## 📈 总结

### 8.1 设计亮点

1. **全面集成pyod框架**�?
   - 支持30+异常检测算�?
   - 灵活的无监督、半监督、监督模�?
   - 多种集成方法（平均、加权、投票等�?

2. **完整的异常分析流水线**�?
   - 从数据加载到预警生成的全流程
   - 多维异常分析（时间、特征、聚类等�?
   - 可解释异常检�?

3. **专业级监控系�?*�?
   - 实时性能监控和指标收�?
   - 智能告警规则和抑制机�?
   - 数据漂移检�?

4. **企业级部署方�?*�?
   - 多环境支持（开发、预发、生产）
   - 自动化部署脚�?
   - 调度系统和资源管�?
   - 高可用和备份策略

### 8.2 预期效益

1. **风险控制提升**�?
   - 实时检测交易异常和市场异常
   - 提前预警潜在风险事件
   - 减少异常交易损失

2. **数据质量保障**�?
   - 自动检测数据质量问�?
   - 及时发现数据漂移
   - 提高数据可靠�?

3. **运维效率提升**�?
   - 自动化异常检测流�?
   - 减少人工监控工作�?
   - 快速定位问题根�?

4. **决策支持增强**�?
   - 提供异常分析报告
   - 支持异常原因调查
   - 辅助风险决策

### 8.3 后续优化方向

1. **算法优化**�?
   - 引入深度学习异常检测模�?
   - 优化集成策略和权重计�?
   - 支持在线学习和增量更�?

2. **性能提升**�?
   - GPU加速支�?
   - 分布式检测框�?
   - 流式处理优化

3. **功能扩展**�?
   - 多模态异常检测（文本、图像）
   - 因果异常分析
   - 预测性异常预�?

4. **集成增强**�?
   - 与现有监控系统深度集�?
   - 支持更多数据源和格式
   - 提供REST API和SDK

### 8.4 风险评估与缓�?

| 风险类型 | 风险描述 | 影响程度 | 缓解措施 |
|---------|---------|---------|---------|
| 技术风�?| pyod框架更新不兼�?| �?| 版本锁定、兼容性测试、备用算�?|
| 性能风险 | 实时检测延迟过�?| �?| 性能监控、算法优化、硬件升�?|
| 数据风险 | 数据质量影响检测准确�?| �?| 数据验证、质量监控、异常过�?|
| 安全风险 | 敏感数据泄露 | �?| 数据脱敏、访问控制、审计日�?|
| 运维风险 | 系统故障影响业务 | �?| 高可用架构、自动恢复、备份策�?|

### 8.5 成功指标

1. **检测性能指标**�?
   - 准确�?> 85%
   - 召回�?> 80%
   - 假阳性率 < 10%
   - 检测延�?< 1�?

2. **系统性能指标**�?
   - 可用�?> 99.9%
   - 并发处理能力 > 1000请求/�?
   - 资源利用�?< 80%

3. **业务价值指�?*�?
   - 异常发现时间减少 > 50%
   - 人工监控工作量减�?> 70%
   - 风险事件损失减少 > 30%

4. **运维效率指标**�?
   - 部署成功�?> 95%
   - 平均恢复时间 < 5分钟
   - 自动化程�?> 80%

---

> **设计完成状�?*: �?已完�? 
> **下一�?*: 按照MODULE_DESIGN_PLAN.md计划，进入技术验证阶�