---
module_id: MARKETREGIMEBLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
layer: Layer 4 (机器学习层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
responsibility:
  - 提供market regime blueprint的架构设计和实施蓝图
---
---

﻿---
module_id: MARKET_REGIME_DETECTION_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 11.13 - 市场状态识别系统
compliance_level: 顶级专业标准
reference_models: ["Renaissance Technologies Regime Detection", "Two Sigma Market State Model", "Citadel Risk Regime System"]
open_source_solution: "hmmlearn + MarketRegimeTrader"
priority: P0
---

# 市场状态识别系统蓝图
> **核心职责**: Market Regime蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Market Regime蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


## 📋 文档职责说明

### 核心职责

本文档是**市场状态识别系统蓝图，负责市场状态判断和预测**。

### 职责边界

**负责**：
- ✅ 市场状态识别（趋势/震荡/极端）
- ✅ 市场状态预测（状态转换预测）
- ✅ 状态转换预警（范式变化预警）
- ✅ 市场环境报告（状态报告生成）

**不负责**：
- ❌ 资产配置决策（由战略资产配置模块负责）
- ❌ 风险预算分配（由风险预算分配模块负责）
- ❌ 策略选择决策（由投资策略选择模块负责）

### 对接模块

**上游模块**：
- Layer 2 数据层
- Layer 10 质量保证层

**下游模块**：
- Layer 6 组合优化层
- Layer 7 风险管理层

---
> **版本**: v1.0
> **创建日期**: 2026-04-06
> **优先级**: 🔴 P0 - 核心功能增强
> **开源方案**: hmmlearn, MarketRegimeTrader
> **目标**: 构建专业级市场状态识别系统，提升战略决策准确性

---

## 📋 执行摘要

### 核心定位

市场状态识别系统是Layer 11战略决策层的**状态感知核心**，负责：
- 识别市场隐藏状态（牛市/熊市/震荡市）
- 检测市场范式转换
- 为战略决策提供状态依据
- 支持动态风险管理

### 专业价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |
|---------|-------------|-------------|---------|
| **市场状态识别** | HMM+多因子模型 | hmmlearn开源集成 | ⭐⭐⭐⭐⭐ |
| **范式转换预警** | 专业团队监控 | AI自动检测 | ⭐⭐⭐⭐⭐ |
| **风险状态判断** | 风险委员会 | AI+人工确认 | ⭐⭐⭐⭐ |
| **策略适配** | 多策略切换 | 状态驱动策略 | ⭐⭐⭐⭐⭐ |

**综合价值评级**: ⭐⭐⭐⭐⭐ (5/5) - **强烈推荐实施**

---

## 一、架构设计

### 1.1 系统整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│              市场状态识别系统架构 (Market Regime Detection)        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.13.1 数据预处理层                          │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 特征工程引擎 (Feature Engineering)                  │  │ │
│  │  │ ├── 收益率特征（日/周/月收益率）                    │  │ │
│  │  │ ├── 波动率特征（已实现波动率、GARCH波动率）         │  │ │
│  │  │ ├── 技术指标（RSI、MACD、布林带）                   │  │ │
│  │  │ ├── 成交量特征（成交量变化、换手率）                │  │ │
│  │  │ └── 宏观因子（利率、汇率、信用利差）                │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 数据标准化 (Data Normalization)                     │  │ │
│  │  │ ├── PCA降维（保留95%方差）                          │  │ │
│  │  │ ├── 白化处理（消除特征相关性）                      │  │ │
│  │  │ └── 滚动标准化（适应非平稳性）                      │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.13.2 HMM状态识别层                         │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ HMM模型引擎 (Hidden Markov Model Engine)            │  │ │
│  │  │ ├── 高斯HMM（Gaussian HMM）                         │  │ │
│  │  │ ├── 高斯混合HMM（GMM-HMM）                          │  │ │
│  │  │ ├── 多状态模型（2-5个隐藏状态）                     │  │ │
│  │  │ └── 滚动训练（Walk-Forward训练）                    │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 状态解码器 (State Decoder)                          │  │ │
│  │  │ ├── Viterbi算法（最优状态序列）                     │  │ │
│  │  │ ├── 前向-后向算法（状态概率）                       │  │ │
│  │  │ └── 状态标签映射（Bull/Bear/Range）                 │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.13.3 状态解释层                            │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 状态标签系统 (State Labeling)                       │  │ │
│  │  │ ├── 牛市状态（Bull: 高收益、低波动）                │  │ │
│  │  │ ├── 熊市状态（Bear: 低收益、高波动）                │  │ │
│  │  │ ├── 震荡状态（Range: 中等收益、中等波动）           │  │ │
│  │  │ └── 危机状态（Crisis: 极端负收益、超高波动）        │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 状态统计系统 (State Statistics)                     │  │ │
│  │  │ ├── 状态持续期（Expected Duration）                 │  │ │
│  │  │ ├── 转移概率（Transition Probability）              │  │ │
│  │  │ ├── 状态特征（State Characteristics）               │  │ │
│  │  │ └── 历史匹配（Historical Pattern Matching）         │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.13.4 预警与决策层                          │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 范式转换检测 (Regime Change Detection)              │  │ │
│  │  │ ├── 状态概率监控（实时状态概率）                    │  │ │
│  │  │ ├── 转换信号检测（状态切换信号）                    │  │ │
│  │  │ ├── 置信度评估（转换置信度）                        │  │ │
│  │  │ └── 历史转换分析（历史转换模式）                    │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 决策支持系统 (Decision Support)                     │  │ │
│  │  │ ├── 状态报告生成（市场状态报告）                    │  │ │
│  │  │ ├── 策略适配建议（状态驱动策略建议）                │  │ │
│  │  │ ├── 风险调整建议（状态驱动风险调整）                │  │ │
│  │  │ └── 预警通知（状态转换预警）                        │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责边界

| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |
|------|---------|------|------|---------|
| **数据预处理层** | 特征工程、数据标准化 | 原始市场数据 | 标准化特征矩阵 | HMM状态识别层 |
| **HMM状态识别层** | HMM训练、状态解码 | 特征矩阵 | 状态序列、状态概率 | 状态解释层 |
| **状态解释层** | 状态标签、状态统计 | 状态序列 | 状态标签、统计信息 | 预警决策层 |
| **预警决策层** | 转换检测、决策支持 | 状态信息 | 预警信号、决策建议 | Layer 11.1-11.4 |

---

## 二、核心组件详细设计

### 2.1 数据预处理层

#### 2.1.1 特征工程引擎

```python
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

@dataclass
class FeatureConfig:
    """特征配置"""
    return_windows: List[int] = None  # 收益率窗口
    volatility_windows: List[int] = None  # 波动率窗口
    technical_indicators: List[str] = None  # 技术指标
    macro_factors: List[str] = None  # 宏观因子
    
    def __post_init__(self):
        self.return_windows = self.return_windows or [1, 5, 20, 60]
        self.volatility_windows = self.volatility_windows or [20, 60, 120]
        self.technical_indicators = self.technical_indicators or ['rsi', 'macd', 'bollinger']
        self.macro_factors = self.macro_factors or []

class FeatureEngineeringEngine:
    """特征工程引擎"""
    
    def __init__(self, config: FeatureConfig):
        self.config = config
        
    def extract_features(self, 
                        price_data: pd.DataFrame,
                        volume_data: pd.DataFrame = None,
                        macro_data: pd.DataFrame = None) -> pd.DataFrame:
        """提取特征"""
        features = pd.DataFrame(index=price_data.index)
        
        features = self._extract_return_features(price_data, features)
        
        features = self._extract_volatility_features(price_data, features)
        
        features = self._extract_technical_indicators(price_data, features)
        
        if volume_data is not None:
            features = self._extract_volume_features(volume_data, features)
        
        if macro_data is not None and self.config.macro_factors:
            features = self._extract_macro_features(macro_data, features)
        
        return features
    
    def _extract_return_features(self, 
                                price_data: pd.DataFrame,
                                features: pd.DataFrame) -> pd.DataFrame:
        """提取收益率特征"""
        returns = price_data['close'].pct_change()
        
        for window in self.config.return_windows:
            features[f'return_{window}d'] = returns.rolling(window).sum()
            features[f'return_std_{window}d'] = returns.rolling(window).std()
        
        return features
    
    def _extract_volatility_features(self,
                                    price_data: pd.DataFrame,
                                    features: pd.DataFrame) -> pd.DataFrame:
        """提取波动率特征"""
        returns = price_data['close'].pct_change()
        
        for window in self.config.volatility_windows:
            features[f'volatility_{window}d'] = returns.rolling(window).std() * np.sqrt(252)
        
        features['parkinson_vol'] = self._calculate_parkinson_volatility(price_data)
        
        return features
    
    def _calculate_parkinson_volatility(self, price_data: pd.DataFrame) -> pd.Series:
        """计算Parkinson波动率"""
        high = price_data['high']
        low = price_data['low']
        
        return np.sqrt(
            (np.log(high / low) ** 2).rolling(20).mean() / (4 * np.log(2))
        ) * np.sqrt(252)
    
    def _extract_technical_indicators(self,
                                     price_data: pd.DataFrame,
                                     features: pd.DataFrame) -> pd.DataFrame:
        """提取技术指标"""
        if 'rsi' in self.config.technical_indicators:
            features['rsi_14'] = self._calculate_rsi(price_data['close'], 14)
        
        if 'macd' in self.config.technical_indicators:
            macd, signal, hist = self._calculate_macd(price_data['close'])
            features['macd'] = macd
            features['macd_signal'] = signal
            features['macd_hist'] = hist
        
        if 'bollinger' in self.config.technical_indicators:
            upper, middle, lower = self._calculate_bollinger(price_data['close'])
            features['bb_upper'] = upper
            features['bb_middle'] = middle
            features['bb_lower'] = lower
            features['bb_position'] = (price_data['close'] - lower) / (upper - lower)
        
        return features
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, 
                       prices: pd.Series,
                       fast: int = 12,
                       slow: int = 26,
                       signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return macd, signal_line, histogram
    
    def _calculate_bollinger(self,
                            prices: pd.Series,
                            period: int = 20,
                            std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算布林带"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    def _extract_volume_features(self,
                                volume_data: pd.DataFrame,
                                features: pd.DataFrame) -> pd.DataFrame:
        """提取成交量特征"""
        features['volume_ratio'] = volume_data['volume'] / volume_data['volume'].rolling(20).mean()
        features['turnover_rate'] = volume_data['turnover'] if 'turnover' in volume_data.columns else np.nan
        
        return features
    
    def _extract_macro_features(self,
                               macro_data: pd.DataFrame,
                               features: pd.DataFrame) -> pd.DataFrame:
        """提取宏观因子"""
        for factor in self.config.macro_factors:
            if factor in macro_data.columns:
                features[f'macro_{factor}'] = macro_data[factor]
        
        return features
```

#### 2.1.2 数据标准化器

```python
class DataNormalizer:
    """数据标准化器"""
    
    def __init__(self, 
                 pca_variance: float = 0.95,
                 use_whitening: bool = True,
                 rolling_window: int = 252):
        self.pca_variance = pca_variance
        self.use_whitening = use_whitening
        self.rolling_window = rolling_window
        self.pca = None
        self.scaler = None
        
    def fit_transform(self, features: pd.DataFrame) -> np.ndarray:
        """训练并转换"""
        features_clean = features.dropna()
        
        self.scaler = StandardScaler()
        scaled_features = self.scaler.fit_transform(features_clean)
        
        self.pca = PCA(n_components=self.pca_variance, whiten=self.use_whitening)
        transformed_features = self.pca.fit_transform(scaled_features)
        
        return transformed_features
    
    def transform(self, features: pd.DataFrame) -> np.ndarray:
        """转换新数据"""
        features_clean = features.dropna()
        
        scaled_features = self.scaler.transform(features_clean)
        transformed_features = self.pca.transform(scaled_features)
        
        return transformed_features
    
    def get_n_components(self) -> int:
        """获取PCA组件数"""
        return self.pca.n_components_ if self.pca else 0
```

---

### 2.2 HMM状态识别层

#### 2.2.1 HMM模型引擎

```python
from hmmlearn import hmm
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class HMMConfig:
    """HMM配置"""
    n_states: int = 3  # 状态数量
    covariance_type: str = 'full'  # 协方差类型
    n_iter: int = 100  # 迭代次数
    random_state: int = 42
    tol: float = 1e-4  # 收敛阈值
    
class HMMRegimeDetector:
    """HMM市场状态检测器"""
    
    def __init__(self, config: HMMConfig):
        self.config = config
        self.model = None
        self.state_labels = None
        self.training_score = None
        
    def train(self, 
             features: np.ndarray,
             n_init: int = 10) -> float:
        """训练HMM模型"""
        best_model = None
        best_score = float('-inf')
        
        for _ in range(n_init):
            model = hmm.GaussianHMM(
                n_components=self.config.n_states,
                covariance_type=self.config.covariance_type,
                n_iter=self.config.n_iter,
                random_state=np.random.randint(0, 10000),
                tol=self.config.tol
            )
            
            try:
                model.fit(features)
                score = model.score(features)
                
                if score > best_score:
                    best_score = score
                    best_model = model
            except Exception as e:
                continue
        
        self.model = best_model
        self.training_score = best_score
        
        self._assign_state_labels(features)
        
        return best_score
    
    def _assign_state_labels(self, features: np.ndarray):
        """分配状态标签"""
        if self.model is None:
            return
        
        state_stats = []
        
        for state in range(self.config.n_states):
            state_mask = self.model.predict(features) == state
            
            if state_mask.sum() > 0:
                state_features = features[state_mask]
                
                mean_return = state_features[:, 0].mean() if state_features.shape[1] > 0 else 0
                mean_vol = state_features[:, 1].std() if state_features.shape[1] > 1 else 0
                
                state_stats.append({
                    'state': state,
                    'mean_return': mean_return,
                    'mean_volatility': mean_vol,
                    'count': state_mask.sum()
                })
        
        sorted_states = sorted(state_stats, 
                              key=lambda x: (x['mean_return'], -x['mean_volatility']),
                              reverse=True)
        
        self.state_labels = {}
        for i, stats in enumerate(sorted_states):
            if i == 0:
                self.state_labels[stats['state']] = 'bull'
            elif i == len(sorted_states) - 1:
                self.state_labels[stats['state']] = 'bear'
            else:
                self.state_labels[stats['state']] = 'range'
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """预测状态序列"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        return self.model.predict(features)
    
    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """预测状态概率"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        return self.model.predict_proba(features)
    
    def decode(self, features: np.ndarray) -> Tuple[np.ndarray, float]:
        """Viterbi解码"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        return self.model.decode(features, algorithm='viterbi')
    
    def get_state_statistics(self) -> Dict:
        """获取状态统计"""
        if self.model is None:
            return {}
        
        stats = {
            'transition_matrix': self.model.transmat_,
            'means': self.model.means_,
            'covars': self.model.covars_,
            'state_labels': self.state_labels,
            'training_score': self.training_score
        }
        
        return stats
    
    def get_expected_durations(self) -> Dict[str, float]:
        """计算期望持续期"""
        if self.model is None:
            return {}
        
        durations = {}
        for i in range(self.config.n_states):
            self_stay_prob = self.model.transmat_[i, i]
            if self_stay_prob < 1:
                expected_duration = 1 / (1 - self_stay_prob)
                label = self.state_labels.get(i, f'state_{i}')
                durations[label] = expected_duration
        
        return durations
```

#### 2.2.2 状态解码器

```python
class StateDecoder:
    """状态解码器"""
    
    def __init__(self, hmm_detector: HMMRegimeDetector):
        self.hmm_detector = hmm_detector
        
    def decode_sequence(self, 
                       features: np.ndarray,
                       dates: pd.DatetimeIndex) -> pd.DataFrame:
        """解码状态序列"""
        states = self.hmm_detector.predict(features)
        probs = self.hmm_detector.predict_proba(features)
        
        results = pd.DataFrame(index=dates)
        results['state'] = states
        results['state_label'] = [self.hmm_detector.state_labels.get(s, f'state_{s}') 
                                  for s in states]
        
        for i in range(probs.shape[1]):
            label = self.hmm_detector.state_labels.get(i, f'state_{i}')
            results[f'prob_{label}'] = probs[:, i]
        
        return results
    
    def get_current_state(self, 
                         features: np.ndarray,
                         lookback: int = 1) -> Dict:
        """获取当前状态"""
        recent_features = features[-lookback:]
        
        states = self.hmm_detector.predict(recent_features)
        probs = self.hmm_detector.predict_proba(recent_features)
        
        current_state = states[-1]
        current_prob = probs[-1]
        
        state_label = self.hmm_detector.state_labels.get(current_state, f'state_{current_state}')
        state_prob = current_prob[current_state]
        
        return {
            'state': current_state,
            'state_label': state_label,
            'probability': state_prob,
            'all_probabilities': {
                self.hmm_detector.state_labels.get(i, f'state_{i}'): prob
                for i, prob in enumerate(current_prob)
            }
        }
```

---

### 2.3 状态解释层

#### 2.3.1 状态标签系统

```python
@dataclass
class StateCharacteristics:
    """状态特征"""
    state_label: str
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    duration_days: float
    frequency: float

class StateInterpreter:
    """状态解释器"""
    
    def __init__(self, hmm_detector: HMMRegimeDetector):
        self.hmm_detector = hmm_detector
        self.state_characteristics = {}
        
    def analyze_states(self,
                      features: np.ndarray,
                      returns: pd.Series) -> Dict[str, StateCharacteristics]:
        """分析各状态特征"""
        states = self.hmm_detector.predict(features)
        
        for state in range(self.hmm_detector.config.n_states):
            state_mask = states == state
            state_returns = returns.values[state_mask]
            
            if len(state_returns) > 0:
                label = self.hmm_detector.state_labels.get(state, f'state_{state}')
                
                expected_return = np.mean(state_returns) * 252
                expected_volatility = np.std(state_returns) * np.sqrt(252)
                sharpe_ratio = expected_return / expected_volatility if expected_volatility > 0 else 0
                
                cumulative = np.cumsum(state_returns)
                running_max = np.maximum.accumulate(cumulative)
                drawdown = cumulative - running_max
                max_drawdown = np.min(drawdown)
                
                durations = self._calculate_durations(states, state)
                avg_duration = np.mean(durations) if durations else 0
                
                frequency = state_mask.sum() / len(states)
                
                self.state_characteristics[label] = StateCharacteristics(
                    state_label=label,
                    expected_return=expected_return,
                    expected_volatility=expected_volatility,
                    sharpe_ratio=sharpe_ratio,
                    max_drawdown=max_drawdown,
                    duration_days=avg_duration,
                    frequency=frequency
                )
        
        return self.state_characteristics
    
    def _calculate_durations(self, states: np.ndarray, target_state: int) -> List[int]:
        """计算状态持续期"""
        durations = []
        current_duration = 0
        
        for state in states:
            if state == target_state:
                current_duration += 1
            else:
                if current_duration > 0:
                    durations.append(current_duration)
                    current_duration = 0
        
        if current_duration > 0:
            durations.append(current_duration)
        
        return durations
    
    def get_state_report(self) -> str:
        """生成状态报告"""
        if not self.state_characteristics:
            return "No state analysis available. Run analyze_states() first."
        
        report = "市场状态特征分析报告\n"
        report += "=" * 50 + "\n\n"
        
        for label, chars in self.state_characteristics.items():
            report += f"状态: {label.upper()}\n"
            report += f"  期望年化收益: {chars.expected_return:.2%}\n"
            report += f"  期望年化波动: {chars.expected_volatility:.2%}\n"
            report += f"  夏普比率: {chars.sharpe_ratio:.2f}\n"
            report += f"  最大回撤: {chars.max_drawdown:.2%}\n"
            report += f"  平均持续期: {chars.duration_days:.1f}天\n"
            report += f"  出现频率: {chars.frequency:.2%}\n"
            report += "\n"
        
        return report
```

---

### 2.4 预警与决策层

#### 2.4.1 范式转换检测器

```python
@dataclass
class RegimeChangeSignal:
    """范式转换信号"""
    timestamp: datetime
    from_state: str
    to_state: str
    confidence: float
    probability_change: float
    alert_level: str  # 'low', 'medium', 'high'

class RegimeChangeDetector:
    """范式转换检测器"""
    
    def __init__(self, 
                 hmm_detector: HMMRegimeDetector,
                 prob_threshold: float = 0.3,
                 confidence_threshold: float = 0.7):
        self.hmm_detector = hmm_detector
        self.prob_threshold = prob_threshold
        self.confidence_threshold = confidence_threshold
        self.history = []
        
    def detect_change(self,
                     features: np.ndarray,
                     dates: pd.DatetimeIndex) -> Optional[RegimeChangeSignal]:
        """检测范式转换"""
        if len(features) < 2:
            return None
        
        probs = self.hmm_detector.predict_proba(features)
        
        current_probs = probs[-1]
        prev_probs = probs[-2]
        
        current_state = np.argmax(current_probs)
        prev_state = np.argmax(prev_probs)
        
        if current_state != prev_state:
            prob_change = abs(current_probs[current_state] - prev_probs[prev_state])
            
            confidence = current_probs[current_state]
            
            if confidence >= self.confidence_threshold:
                alert_level = 'high'
            elif confidence >= 0.5:
                alert_level = 'medium'
            else:
                alert_level = 'low'
            
            signal = RegimeChangeSignal(
                timestamp=dates[-1],
                from_state=self.hmm_detector.state_labels.get(prev_state, f'state_{prev_state}'),
                to_state=self.hmm_detector.state_labels.get(current_state, f'state_{current_state}'),
                confidence=confidence,
                probability_change=prob_change,
                alert_level=alert_level
            )
            
            self.history.append(signal)
            
            return signal
        
        return None
    
    def get_recent_changes(self, n: int = 10) -> List[RegimeChangeSignal]:
        """获取最近的转换信号"""
        return self.history[-n:]
```

#### 2.4.2 决策支持系统

```python
class DecisionSupportSystem:
    """决策支持系统"""
    
    def __init__(self, 
                 state_interpreter: StateInterpreter,
                 change_detector: RegimeChangeDetector):
        self.state_interpreter = state_interpreter
        self.change_detector = change_detector
        
    def generate_recommendations(self,
                                current_state: Dict,
                                change_signal: Optional[RegimeChangeSignal] = None) -> Dict:
        """生成决策建议"""
        recommendations = {
            'current_state': current_state,
            'strategy_adjustment': None,
            'risk_adjustment': None,
            'position_adjustment': None,
            'alerts': []
        }
        
        state_label = current_state['state_label']
        state_chars = self.state_interpreter.state_characteristics.get(state_label)
        
        if state_chars:
            if state_label == 'bull':
                recommendations['strategy_adjustment'] = {
                    'action': 'increase_risk',
                    'suggestion': '牛市状态，可适当增加风险敞口',
                    'target_volatility': min(state_chars.expected_volatility * 1.2, 0.25)
                }
                recommendations['position_adjustment'] = {
                    'action': 'increase_equity',
                    'suggestion': '可增加股票仓位至目标上限'
                }
            
            elif state_label == 'bear':
                recommendations['strategy_adjustment'] = {
                    'action': 'reduce_risk',
                    'suggestion': '熊市状态，建议降低风险敞口',
                    'target_volatility': state_chars.expected_volatility * 0.7
                }
                recommendations['position_adjustment'] = {
                    'action': 'reduce_equity',
                    'suggestion': '建议降低股票仓位，增加债券或现金'
                }
                recommendations['alerts'].append({
                    'level': 'warning',
                    'message': f'熊市状态，期望波动率{state_chars.expected_volatility:.2%}'
                })
            
            else:  # range
                recommendations['strategy_adjustment'] = {
                    'action': 'maintain',
                    'suggestion': '震荡市状态，维持当前风险水平',
                    'target_volatility': state_chars.expected_volatility
                }
        
        if change_signal and change_signal.alert_level == 'high':
            recommendations['alerts'].append({
                'level': 'critical',
                'message': f'检测到市场状态转换: {change_signal.from_state} -> {change_signal.to_state}'
            })
        
        return recommendations
    
    def generate_report(self,
                       features: np.ndarray,
                       dates: pd.DatetimeIndex) -> str:
        """生成完整报告"""
        current_state = self.change_detector.hmm_detector.predict(features[-1:])
        
        state_label = self.change_detector.hmm_detector.state_labels.get(
            current_state[0], f'state_{current_state[0]}'
        )
        
        report = "市场状态识别报告\n"
        report += "=" * 50 + "\n\n"
        report += f"报告日期: {dates[-1]}\n\n"
        
        report += f"当前市场状态: {state_label.upper()}\n\n"
        
        if self.state_interpreter.state_characteristics:
            chars = self.state_interpreter.state_characteristics.get(state_label)
            if chars:
                report += "状态特征:\n"
                report += f"  期望年化收益: {chars.expected_return:.2%}\n"
                report += f"  期望年化波动: {chars.expected_volatility:.2%}\n"
                report += f"  夏普比率: {chars.sharpe_ratio:.2f}\n\n"
        
        recent_changes = self.change_detector.get_recent_changes(5)
        if recent_changes:
            report += "近期状态转换:\n"
            for change in recent_changes:
                report += f"  {change.timestamp}: {change.from_state} -> {change.to_state} "
                report += f"(置信度: {change.confidence:.2%})\n"
        
        return report
```

---

## 三、数据模型

### 3.1 核心数据结构

```python
@dataclass
class MarketRegimeState:
    """市场状态数据结构"""
    timestamp: datetime
    state: int
    state_label: str
    probability: float
    all_probabilities: Dict[str, float]
    expected_duration: float
    transition_probabilities: Dict[str, float]

@dataclass
class RegimeAnalysisResult:
    """状态分析结果"""
    current_state: MarketRegimeState
    state_characteristics: Dict[str, StateCharacteristics]
    recent_changes: List[RegimeChangeSignal]
    recommendations: Dict
    report: str
```

### 3.2 数据存储设计

```python
class MarketRegimeStorage:
    """市场状态存储"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def save_state(self, state: MarketRegimeState):
        """保存状态"""
        pass
    
    def save_change_signal(self, signal: RegimeChangeSignal):
        """保存转换信号"""
        pass
    
    def get_state_history(self, 
                         start_date: datetime,
                         end_date: datetime) -> List[MarketRegimeState]:
        """获取历史状态"""
        pass
```

---

## 四、开源集成方案

### 4.1 hmmlearn集成

```python
from hmmlearn import hmm

class HMMIntegrator:
    """HMM集成器"""
    
    def __init__(self):
        self.available_models = {
            'gaussian': hmm.GaussianHMM,
            'gmm': hmm.GMMHMM,
            'multinomial': hmm.MultinomialHMM
        }
    
    def create_model(self, 
                    model_type: str = 'gaussian',
                    n_states: int = 3,
                    **kwargs) -> hmm._base._BaseHMM:
        """创建HMM模型"""
        model_class = self.available_models.get(model_type)
        if model_class is None:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return model_class(n_components=n_states, **kwargs)
```

### 4.2 MarketRegimeTrader参考架构

```python
class MarketRegimeTraderIntegration:
    """MarketRegimeTrader项目集成"""
    
    def __init__(self):
        self.project_url = "https://github.com/0x596173736972/MarketRegimeTrader"
        
    def get_reference_features(self) -> List[str]:
        """获取参考特征列表"""
        return [
            'returns',
            'volatility',
            'rsi',
            'macd',
            'bollinger_position',
            'volume_ratio',
            'momentum',
            'mean_reversion'
        ]
    
    def get_reference_strategies(self) -> Dict[str, str]:
        """获取参考策略"""
        return {
            'regime_momentum': '牛市做多，熊市做空',
            'mean_reversion': '状态内均值回归',
            'adaptive_volatility': '基于状态波动率调整仓位',
            'contrarian': '极端状态反向操作'
        }
```

---

## 五、实施路径

### Phase 1: 核心功能（1周）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 特征工程引擎开发 | 2天 | FeatureEngineeringEngine |
| HMM模型集成 | 2天 | HMMRegimeDetector |
| 状态解码器开发 | 1天 | StateDecoder |
| 单元测试 | 1天 | 测试用例 |

### Phase 2: 分析功能（1周）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 状态解释系统 | 2天 | StateInterpreter |
| 范式转换检测 | 2天 | RegimeChangeDetector |
| 决策支持系统 | 2天 | DecisionSupportSystem |
| 集成测试 | 1天 | 测试报告 |

### Phase 3: 生产部署（1周）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 数据存储实现 | 2天 | MarketRegimeStorage |
| API接口开发 | 2天 | REST API |
| 监控告警 | 2天 | 监控系统 |
| 文档完善 | 1天 | 使用文档 |

---

## 六、质量保证

### 6.1 模型验证指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 状态识别准确率 | ≥ 70% | 历史回测验证 |
| 转换信号准确率 | ≥ 60% | 转换后验证 |
| 状态持续期预测误差 | ≤ 30% | 期望持续期vs实际 |
| 模型稳定性 | ≥ 0.8 | 多次训练一致性 |

### 6.2 测试策略

```python
class MarketRegimeTester:
    """市场状态识别测试"""
    
    def test_hmm_training(self):
        """测试HMM训练"""
        pass
    
    def test_state_prediction(self):
        """测试状态预测"""
        pass
    
    def test_change_detection(self):
        """测试转换检测"""
        pass
    
    def test_backtest_performance(self):
        """测试回测表现"""
        pass
```

---

## 七、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 模型过拟合 | 高 | 滚动训练、交叉验证 |
| 状态识别错误 | 中 | 多模型集成、置信度过滤 |
| 转换信号延迟 | 中 | 多特征组合、实时监控 |
| 计算资源消耗 | 低 | 特征降维、增量训练 |

---

## 八、相关文档

| 文档 | 说明 |
|------|------|
| [BLUEPRINT.md](#) | Layer 11主蓝图 |
| [TCA_BLUEPRINT.md](#) | 交易成本分析系统 |
| [REBALANCING_BLUEPRINT.md](#) | 再平衡决策系统 |

---

**版本**: v1.0 | **更新**: 2026-04-06 | **状态**: ✅ 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Market Regime Detection
- **模块ID**: MARKET_REGIME_DETECTION_001
- **蓝图文档**: [MARKET_REGIME_BLUEPRINT.md](#)
- **技术规格书**: 待创建
- **职责**: Layer 11.13 - 市场状态识别系统
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Market Regime Detection** | Layer 11.13 - 市场状态识别系统 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
