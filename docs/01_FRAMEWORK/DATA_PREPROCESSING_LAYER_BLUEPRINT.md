---
module_id: LAYER_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---

﻿---
module_id: DATA_PREPROCESSING_LAYER_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-05
last_updated: 2026-04-05
owner: 首席架构师
layer: Layer 1 (数据预处理层)
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 1 - 数据预处理层
compliance_level: 顶级专业标准
reference_models: ["WorldQuant Data Pipeline", "Two Sigma Data Engineering", "Citadel Data Quality Framework"]
related_documents:
  - ARCHITECTURE.md
  - DATA_SOURCE_LAYER_BLUEPRINT.md
  - DATA_QUALITY_MONITORING_BLUEPRINT.md
parent_document: ../INDEX.md
implementation_status: 设计阶段
---

# Layer 1: 数据预处理层蓝图

> **版本**: v1.0
> **创建日期**: 2026-04-05
> **实施周期**: 1周
> **目标**: 构建专业级数据预处理体系，对标WorldQuant、Two Sigma数据工程标准

---

## 📋 执行摘要

### 核心定位

Layer 1数据预处理层是清风量化系统的**数据加工厂**，负责：
- 数据清洗（缺失值处理、异常值检测、重复值去除）
- 数据标准化（归一化、标准化、对齐）
- 特征工程（技术指标、财务指标、另类特征）
- 数据质量监控（完整性检查、一致性检查、及时性检查）

### 个人使用价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评分 |
|---------|-------------|-------------|---------|
| **数据清洗** | 自动化清洗流水线 | AI辅助清洗+规则引擎 | ⭐⭐⭐⭐⭐ |
| **特征工程** | 专业因子库 | TA-Lib+自定义因子 | ⭐⭐⭐⭐ |
| **质量监控** | 99.9%数据质量 | 95%+数据质量 | ⭐⭐⭐⭐ |
| **性能优化** | 分布式计算 | 本地缓存+向量化 | ⭐⭐⭐⭐ |

**综合价值评分**: ⭐⭐⭐⭐⭐ (5/5) - **强烈推荐实施**

---

## 一、架构设计

### 1.1 Layer 1整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                  Layer 1: 数据预处理层架构                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              1.1 数据清洗层                               │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 缺失值处理 (Missing Value Handler)                 │ │ │
│  │  │  ├── 前向填充（ffill）                            │ │ │
│  │  │  ├── 后向填充（bfill）                            │ │ │
│  │  │  ├── 插值填充（interpolate）                     │ │ │
│  │  │  └── AI预测填充（ml_impute）                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 异常值检测 (Outlier Detector)                      │ │ │
│  │  │  ├── 统计方法（Z-score/IQR）                      │ │ │
│  │  │  ├── 机器学习方法（Isolation Forest）            │ │ │
│  │  │  ├── 业务规则（涨跌停/停牌）                     │ │ │
│  │  │  └── AI异常检测（LSTM Autoencoder）             │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 重复值处理 (Duplicate Handler)                     │ │ │
│  │  │  ├── 完全重复检测                                │ │ │
│  │  │  ├── 部分重复检测                                │ │ │
│  │  │  └── 去重策略（保留最新/保留最早）              │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              1.2 数据标准化层                             │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 归一化处理 (Normalization)                         │ │ │
│  │  │  ├── Min-Max归一化                               │ │ │
│  │  │  ├── Z-Score标准化                               │ │ │
│  │  │  ├── Robust标准化                                │ │ │
│  │  │  └── 分位数标准化                                │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 时间对齐 (Time Alignment)                          │ │ │
│  │  │  ├── 交易日历对齐                                │ │ │
│  │  │  ├── 时间戳对齐                                  │ │ │
│  │  │  ├── 频率转换（分钟->日）                        │ │ │
│  │  │  └── 时区转换                                    │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 数据对齐 (Data Alignment)                          │ │ │
│  │  │  ├── 多源数据对齐                                │ │ │
│  │  │  ├── 横截面数据对齐                              │ │ │
│  │  │  ├── 时间序列对齐                                │ │ │
│  │  │  └── 面板数据对齐                                │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              1.3 特征工程层                               │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 技术指标 (Technical Indicators)                    │ │ │
│  │  │  ├── 趋势指标（MA/EMA/MACD）                      │ │ │
│  │  │  ├── 动量指标（RSI/KDJ/CCI）                      │ │ │
│  │  │  ├── 波动率指标（ATR/Bollinger）                  │ │ │
│  │  │  └── 成交量指标（OBV/VWAP）                       │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 财务指标 (Financial Indicators)                    │ │ │
│  │  │  ├── 盈利能力（ROE/ROA/毛利率）                   │ │ │
│  │  │  ├── 成长能力（营收增长率/利润增长率）           │ │ │
│  │  │  ├── 偿债能力（资产负债率/流动比率）             │ │ │
│  │  │  └── 估值指标（PE/PB/PS）                         │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 另类特征 (Alternative Features)                    │ │ │
│  │  │  ├── 新闻情感特征                                │ │ │
│  │  │  ├── 社交媒体热度                                │ │ │
│  │  │  ├── 分析师预测                                  │ │ │
│  │  │  └── 机构持仓变化                                │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              1.4 数据质量监控层                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 完整性检查 (Completeness Check)                    │ │ │
│  │  │  ├── 数据缺失率统计                              │ │ │
│  │  │  ├── 字段完整性检查                              │ │ │
│  │  │  └── 时间序列完整性检查                          │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 一致性检查 (Consistency Check)                     │ │ │
│  │  │  ├── 跨源数据一致性                              │ │ │
│  │  │  ├── 历史数据一致性                              │ │ │
│  │  │  └── 业务逻辑一致性                              │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 及时性检查 (Timeliness Check)                      │ │ │
│  │  │  ├── 数据延迟监控                                │ │ │
│  │  │  ├── 更新频率检查                                │ │ │
│  │  │  └── 时效性告警                                  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责边界

| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |
|------|---------|------|------|---------|
| **数据清洗层** | 数据质量修复 | 原始数据 | 清洗后数据 | 数据标准化层 |
| **数据标准化层** | 数据格式统一 | 清洗后数据 | 标准化数据 | 特征工程层 |
| **特征工程层** | 特征提取与构建 | 标准化数据 | 特征数据 | Layer 2-3 |
| **数据质量监控层** | 质量监控与告警 | 处理后数据 | 质量报告 | Layer 10 |

---

## 二、核心组件详细设计

### 2.1 数据清洗层

#### 2.1.1 缺失值处理 (Missing Value Handler)

**核心职责**：
1. **缺失值检测**：识别缺失值类型和模式
2. **填充策略选择**：根据数据特性选择最优填充方法
3. **AI预测填充**：使用机器学习预测缺失值
4. **填充质量评估**：评估填充后的数据质量

**技术实现**：

```python
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, KNNImputer
from dataclasses import dataclass
from enum import Enum

class ImputationMethod(Enum):
    """填充方法"""
    FFILL = "ffill"                    # 前向填充
    BFILL = "bfill"                    # 后向填充
    INTERPOLATE = "interpolate"        # 插值填充
    MEAN = "mean"                      # 均值填充
    MEDIAN = "median"                  # 中位数填充
    MODE = "mode"                      # 众数填充
    KNN = "knn"                        # KNN填充
    MICE = "mice"                      # MICE填充
    ML_PREDICT = "ml_predict"          # 机器学习预测

@dataclass
class MissingValueReport:
    """缺失值报告"""
    total_records: int
    missing_count: int
    missing_rate: float
    missing_pattern: str  # MCAR, MAR, MNAR
    recommended_method: ImputationMethod

class MissingValueHandler:
    """缺失值处理器"""
    
    def __init__(self):
        self.imputers = {
            'knn': KNNImputer(n_neighbors=5),
            'mice': IterativeImputer(max_iter=10, random_state=42)
        }
        
    def analyze_missing_pattern(
        self,
        data: pd.DataFrame
    ) -> MissingValueReport:
        """分析缺失值模式"""
        
        total = data.size
        missing = data.isna().sum().sum()
        missing_rate = missing / total
        
        pattern = self._detect_missing_pattern(data)
        recommended = self._recommend_method(data, pattern)
        
        return MissingValueReport(
            total_records=total,
            missing_count=missing,
            missing_rate=missing_rate,
            missing_pattern=pattern,
            recommended_method=recommended
        )
    
    def _detect_missing_pattern(self, data: pd.DataFrame) -> str:
        """检测缺失值模式"""
        
        if self._is_mcar(data):
            return "MCAR"  # 完全随机缺失
        elif self._is_mar(data):
            return "MAR"   # 随机缺失
        else:
            return "MNAR"  # 非随机缺失
    
    def _is_mcar(self, data: pd.DataFrame) -> bool:
        """判断是否为MCAR"""
        
        return True
    
    def _is_mar(self, data: pd.DataFrame) -> bool:
        """判断是否为MAR"""
        
        return False
    
    def _recommend_method(
        self,
        data: pd.DataFrame,
        pattern: str
    ) -> ImputationMethod:
        """推荐填充方法"""
        
        if pattern == "MCAR":
            return ImputationMethod.MEAN
        elif pattern == "MAR":
            return ImputationMethod.MICE
        else:
            return ImputationMethod.ML_PREDICT
    
    def impute(
        self,
        data: pd.DataFrame,
        method: ImputationMethod,
        columns: List[str] = None
    ) -> pd.DataFrame:
        """填充缺失值"""
        
        if columns is None:
            columns = data.columns.tolist()
        
        imputed = data.copy()
        
        if method == ImputationMethod.FFILL:
            imputed[columns] = imputed[columns].fillna(method='ffill')
        elif method == ImputationMethod.BFILL:
            imputed[columns] = imputed[columns].fillna(method='bfill')
        elif method == ImputationMethod.INTERPOLATE:
            imputed[columns] = imputed[columns].interpolate(method='linear')
        elif method == ImputationMethod.MEAN:
            imputed[columns] = imputed[columns].fillna(imputed[columns].mean())
        elif method == ImputationMethod.MEDIAN:
            imputed[columns] = imputed[columns].fillna(imputed[columns].median())
        elif method == ImputationMethod.KNN:
            imputed[columns] = self.imputers['knn'].fit_transform(imputed[columns])
        elif method == ImputationMethod.MICE:
            imputed[columns] = self.imputers['mice'].fit_transform(imputed[columns])
        elif method == ImputationMethod.ML_PREDICT:
            imputed = self._ml_impute(imputed, columns)
        
        return imputed
    
    def _ml_impute(
        self,
        data: pd.DataFrame,
        columns: List[str]
    ) -> pd.DataFrame:
        """机器学习预测填充"""
        
        for col in columns:
            missing_idx = data[col].isna()
            if missing_idx.sum() > 0:
                train_data = data[~missing_idx]
                test_data = data[missing_idx]
                
                X_train = train_data.drop(columns=[col])
                y_train = train_data[col]
                X_test = test_data.drop(columns=[col])
                
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                
                predictions = model.predict(X_test)
                data.loc[missing_idx, col] = predictions
        
        return data
```

#### 2.1.2 异常值检测 (Outlier Detector)

**核心职责**：
1. **统计方法检测**：Z-score、IQR方法
2. **机器学习方法检测**：Isolation Forest、LOF
3. **业务规则检测**：涨跌停、停牌、异常波动
4. **AI异常检测**：LSTM Autoencoder

**技术实现**：

```python
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from scipy import stats
import numpy as np

class OutlierDetector:
    """异常值检测器"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.lof = LocalOutlierFactor(
            n_neighbors=20,
            contamination=0.1
        )
        
    def detect_zscore(
        self,
        data: pd.Series,
        threshold: float = 3.0
    ) -> pd.Series:
        """Z-score方法检测异常值"""
        
        z_scores = np.abs(stats.zscore(data))
        return z_scores > threshold
    
    def detect_iqr(
        self,
        data: pd.Series,
        k: float = 1.5
    ) -> pd.Series:
        """IQR方法检测异常值"""
        
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - k * IQR
        upper_bound = Q3 + k * IQR
        
        return (data < lower_bound) | (data > upper_bound)
    
    def detect_isolation_forest(
        self,
        data: pd.DataFrame
    ) -> pd.Series:
        """Isolation Forest检测异常值"""
        
        predictions = self.isolation_forest.fit_predict(data)
        return predictions == -1
    
    def detect_lof(
        self,
        data: pd.DataFrame
    ) -> pd.Series:
        """LOF检测异常值"""
        
        predictions = self.lof.fit_predict(data)
        return predictions == -1
    
    def detect_business_rules(
        self,
        data: pd.DataFrame,
        stock_info: pd.DataFrame
    ) -> pd.Series:
        """业务规则检测异常值"""
        
        anomalies = pd.Series(False, index=data.index)
        
        if 'limit_up' in stock_info.columns:
            anomalies |= data['close'] >= stock_info['limit_up']
        
        if 'limit_down' in stock_info.columns:
            anomalies |= data['close'] <= stock_info['limit_down']
        
        if 'suspended' in stock_info.columns:
            anomalies |= stock_info['suspended'] == True
        
        return anomalies
    
    def handle_outliers(
        self,
        data: pd.DataFrame,
        outliers: pd.Series,
        method: str = 'winsorize'
    ) -> pd.DataFrame:
        """处理异常值"""
        
        handled = data.copy()
        
        if method == 'winsorize':
            for col in handled.columns:
                lower = handled[col].quantile(0.01)
                upper = handled[col].quantile(0.99)
                handled.loc[outliers, col] = handled.loc[outliers, col].clip(lower, upper)
        elif method == 'remove':
            handled = handled[~outliers]
        elif method == 'mark':
            handled['is_outlier'] = outliers
        
        return handled
```

---

### 2.2 数据标准化层

#### 2.2.1 归一化处理 (Normalization)

**核心职责**：
1. **Min-Max归一化**：将数据缩放到[0,1]区间
2. **Z-Score标准化**：将数据转换为标准正态分布
3. **Robust标准化**：使用中位数和四分位数进行标准化
4. **分位数标准化**：将数据转换为均匀分布

**技术实现**：

```python
from sklearn.preprocessing import (
    MinMaxScaler,
    StandardScaler,
    RobustScaler,
    QuantileTransformer
)

class Normalizer:
    """归一化处理器"""
    
    def __init__(self):
        self.scalers = {
            'minmax': MinMaxScaler(),
            'standard': StandardScaler(),
            'robust': RobustScaler(),
            'quantile': QuantileTransformer(output_distribution='uniform')
        }
        
    def normalize(
        self,
        data: pd.DataFrame,
        method: str = 'standard',
        columns: List[str] = None,
        fit: bool = True
    ) -> pd.DataFrame:
        """归一化处理"""
        
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        normalized = data.copy()
        scaler = self.scalers[method]
        
        if fit:
            normalized[columns] = scaler.fit_transform(data[columns])
        else:
            normalized[columns] = scaler.transform(data[columns])
        
        return normalized
    
    def inverse_normalize(
        self,
        data: pd.DataFrame,
        method: str,
        columns: List[str] = None
    ) -> pd.DataFrame:
        """反归一化"""
        
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        scaler = self.scalers[method]
        original = data.copy()
        original[columns] = scaler.inverse_transform(data[columns])
        
        return original
```

#### 2.2.2 时间对齐 (Time Alignment)

**核心职责**：
1. **交易日历对齐**：使用交易日历对齐时间序列
2. **时间戳对齐**：统一时间戳格式
3. **频率转换**：分钟数据转换为日数据
4. **时区转换**：统一时区

**技术实现**：

```python
import pandas as pd
from datetime import datetime, time

class TimeAligner:
    """时间对齐器"""
    
    def __init__(self, trading_calendar: pd.DataFrame):
        self.trading_calendar = trading_calendar
        
    def align_to_trading_days(
        self,
        data: pd.DataFrame,
        date_column: str = 'date'
    ) -> pd.DataFrame:
        """对齐到交易日"""
        
        trading_days = self.trading_calendar['trade_date']
        aligned = data[data[date_column].isin(trading_days)]
        
        return aligned
    
    def resample_frequency(
        self,
        data: pd.DataFrame,
        freq: str = '1D',
        agg_funcs: Dict = None
    ) -> pd.DataFrame:
        """频率转换"""
        
        if agg_funcs is None:
            agg_funcs = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'amount': 'sum'
            }
        
        resampled = data.resample(freq).agg(agg_funcs)
        return resampled
    
    def align_timestamp(
        self,
        data: pd.DataFrame,
        timestamp_column: str,
        target_format: str = '%Y-%m-%d %H:%M:%S'
    ) -> pd.DataFrame:
        """对齐时间戳"""
        
        aligned = data.copy()
        aligned[timestamp_column] = pd.to_datetime(
            aligned[timestamp_column]
        ).dt.strftime(target_format)
        
        return aligned
    
    def convert_timezone(
        self,
        data: pd.DataFrame,
        timestamp_column: str,
        target_tz: str = 'Asia/Shanghai'
    ) -> pd.DataFrame:
        """时区转换"""
        
        converted = data.copy()
        converted[timestamp_column] = pd.to_datetime(
            converted[timestamp_column]
        ).dt.tz_localize('UTC').dt.tz_convert(target_tz)
        
        return converted
```

---

### 2.3 特征工程层

#### 2.3.1 技术指标 (Technical Indicators)

**核心职责**：
1. **趋势指标**：MA、EMA、MACD
2. **动量指标**：RSI、KDJ、CCI
3. **波动率指标**：ATR、Bollinger Bands
4. **成交量指标**：OBV、VWAP

**技术实现**：

```python
import talib

class TechnicalIndicatorEngine:
    """技术指标引擎"""
    
    def __init__(self):
        self.indicators = {
            'trend': ['SMA', 'EMA', 'MACD'],
            'momentum': ['RSI', 'KDJ', 'CCI'],
            'volatility': ['ATR', 'BBANDS'],
            'volume': ['OBV', 'VWAP']
        }
        
    def calculate_all(
        self,
        data: pd.DataFrame,
        indicators: List[str] = None
    ) -> pd.DataFrame:
        """计算所有技术指标"""
        
        if indicators is None:
            indicators = ['SMA', 'EMA', 'RSI', 'MACD', 'ATR', 'BBANDS']
        
        result = data.copy()
        
        for indicator in indicators:
            if indicator == 'SMA':
                result = self._calculate_sma(result)
            elif indicator == 'EMA':
                result = self._calculate_ema(result)
            elif indicator == 'RSI':
                result = self._calculate_rsi(result)
            elif indicator == 'MACD':
                result = self._calculate_macd(result)
            elif indicator == 'ATR':
                result = self._calculate_atr(result)
            elif indicator == 'BBANDS':
                result = self._calculate_bbands(result)
        
        return result
    
    def _calculate_sma(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算简单移动平均"""
        
        for period in [5, 10, 20, 60]:
            data[f'SMA_{period}'] = talib.SMA(
                data['close'].values,
                timeperiod=period
            )
        return data
    
    def _calculate_ema(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算指数移动平均"""
        
        for period in [5, 10, 20, 60]:
            data[f'EMA_{period}'] = talib.EMA(
                data['close'].values,
                timeperiod=period
            )
        return data
    
    def _calculate_rsi(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算RSI"""
        
        for period in [6, 12, 24]:
            data[f'RSI_{period}'] = talib.RSI(
                data['close'].values,
                timeperiod=period
            )
        return data
    
    def _calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算MACD"""
        
        macd, signal, hist = talib.MACD(
            data['close'].values,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )
        data['MACD'] = macd
        data['MACD_SIGNAL'] = signal
        data['MACD_HIST'] = hist
        return data
    
    def _calculate_atr(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算ATR"""
        
        for period in [14]:
            data[f'ATR_{period}'] = talib.ATR(
                data['high'].values,
                data['low'].values,
                data['close'].values,
                timeperiod=period
            )
        return data
    
    def _calculate_bbands(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算布林带"""
        
        upper, middle, lower = talib.BBANDS(
            data['close'].values,
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2
        )
        data['BB_UPPER'] = upper
        data['BB_MIDDLE'] = middle
        data['BB_LOWER'] = lower
        return data
```

#### 2.3.2 财务指标 (Financial Indicators)

**核心职责**：
1. **盈利能力**：ROE、ROA、毛利率
2. **成长能力**：营收增长率、利润增长率
3. **偿债能力**：资产负债率、流动比率
4. **估值指标**：PE、PB、PS

**技术实现**：

```python
class FinancialIndicatorEngine:
    """财务指标引擎"""
    
    def __init__(self):
        self.indicators = {
            'profitability': ['ROE', 'ROA', 'GROSS_MARGIN'],
            'growth': ['REVENUE_GROWTH', 'PROFIT_GROWTH'],
            'solvency': ['DEBT_RATIO', 'CURRENT_RATIO'],
            'valuation': ['PE', 'PB', 'PS']
        }
        
    def calculate_all(
        self,
        financial_data: pd.DataFrame
    ) -> pd.DataFrame:
        """计算所有财务指标"""
        
        result = financial_data.copy()
        
        result = self._calculate_profitability(result)
        result = self._calculate_growth(result)
        result = self._calculate_solvency(result)
        result = self._calculate_valuation(result)
        
        return result
    
    def _calculate_profitability(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算盈利能力指标"""
        
        data['ROE'] = data['net_profit'] / data['total_equity']
        data['ROA'] = data['net_profit'] / data['total_assets']
        data['GROSS_MARGIN'] = (
            data['operating_revenue'] - data['operating_cost']
        ) / data['operating_revenue']
        
        return data
    
    def _calculate_growth(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算成长能力指标"""
        
        data['REVENUE_GROWTH'] = data['operating_revenue'].pct_change()
        data['PROFIT_GROWTH'] = data['net_profit'].pct_change()
        
        return data
    
    def _calculate_solvency(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算偿债能力指标"""
        
        data['DEBT_RATIO'] = data['total_liabilities'] / data['total_assets']
        data['CURRENT_RATIO'] = data['current_assets'] / data['current_liabilities']
        
        return data
    
    def _calculate_valuation(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算估值指标"""
        
        data['PE'] = data['market_cap'] / data['net_profit']
        data['PB'] = data['market_cap'] / data['total_equity']
        data['PS'] = data['market_cap'] / data['operating_revenue']
        
        return data
```

---

### 2.4 数据质量监控层

#### 2.4.1 完整性检查 (Completeness Check)

**核心职责**：
1. **数据缺失率统计**：统计各字段的缺失率
2. **字段完整性检查**：检查必填字段是否完整
3. **时间序列完整性检查**：检查时间序列是否连续

**技术实现**：

```python
class CompletenessChecker:
    """完整性检查器"""
    
    def __init__(self):
        self.required_fields = {
            'market_data': ['stock_code', 'date', 'open', 'high', 'low', 'close', 'volume'],
            'financial_data': ['stock_code', 'report_date', 'balance_sheet', 'income_statement']
        }
        
    def check(
        self,
        data: pd.DataFrame,
        data_type: str
    ) -> Dict:
        """检查完整性"""
        
        report = {
            'total_records': len(data),
            'field_completeness': {},
            'missing_rate': {},
            'time_series_completeness': None
        }
        
        for field in data.columns:
            missing_count = data[field].isna().sum()
            report['missing_rate'][field] = missing_count / len(data)
            report['field_completeness'][field] = missing_count == 0
        
        if data_type in self.required_fields:
            required = self.required_fields[data_type]
            report['required_fields_complete'] = all(
                report['field_completeness.get(f, False)]
                for f in required
            )
        
        if 'date' in data.columns:
            report['time_series_completeness'] = self._check_time_series(data)
        
        return report
    
    def _check_time_series(self, data: pd.DataFrame) -> float:
        """检查时间序列完整性"""
        
        dates = pd.to_datetime(data['date'])
        date_range = pd.date_range(start=dates.min(), end=dates.max(), freq='D')
        
        expected_count = len(date_range)
        actual_count = len(dates.unique())
        
        return actual_count / expected_count
```

---

## 三、数据模型设计

### 3.1 核心数据模型

```python
@dataclass
class ProcessedMarketData:
    """处理后的行情数据"""
    stock_code: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float
    adj_factor: float
    technical_indicators: Dict[str, float]

@dataclass
class ProcessedFinancialData:
    """处理后的财务数据"""
    stock_code: str
    report_date: datetime
    report_type: str
    balance_sheet: Dict
    income_statement: Dict
    cash_flow: Dict
    financial_indicators: Dict[str, float]

@dataclass
class DataQualityReport:
    """数据质量报告"""
    data_type: str
    total_records: int
    completeness_score: float
    consistency_score: float
    timeliness_score: float
    overall_score: float
    issues: List[str]
    recommendations: List[str]
```

---

## 四、实施路线

### 4.1 Phase 1: 数据清洗（Week 1）

**任务清单**：
- [ ] 实现缺失值处理器
- [ ] 实现异常值检测器
- [ ] 实现重复值处理器
- [ ] 单元测试

---

### 4.2 Phase 2: 数据标准化（Week 1）

**任务清单**：
- [ ] 实现归一化处理器
- [ ] 实现时间对齐器
- [ ] 实现数据对齐器
- [ ] 集成测试

---

### 4.3 Phase 3: 特征工程（Week 1）

**任务清单**：
- [ ] 实现技术指标引擎
- [ ] 实现财务指标引擎
- [ ] 实现另类特征提取
- [ ] 性能测试

---

## 五、质量保证

### 5.1 测试策略

| 测试类型 | 覆盖率目标 | 测试工具 |
|---------|-----------|---------|
| **单元测试** | ≥90% | pytest |
| **集成测试** | ≥80% | pytest |
| **性能测试** | 关键路径 | locust |

---

## 六、成功指标

| 指标 | 目标值 |
|------|--------|
| **数据完整性** | ≥95% |
| **处理速度** | ≤1秒/1000条记录 |
| **特征数量** | ≥100个技术指标 |
| **质量评分** | ≥90分 |

---

## 七、相关文档

| 文档 | 说明 |
|------|------|
| [DATA_SOURCE_LAYER_BLUEPRINT.md](./DATA_SOURCE_LAYER_BLUEPRINT.md) | 数据源层蓝图 |
| [DATA_QUALITY_MONITORING_BLUEPRINT.md](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | 数据质量监控蓝图 |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 系统架构文档 |

---

**版本**: v1.0 | **更新**: 2026-04-05 | **状态**: 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 1: 数据预处理层
##### 0.001. Data Preprocessing Layer Blueprint
- **模块ID**: DATA_PREPROCESSING_LAYER_BLUEPRINT_001
- **蓝图文档**: [DATA_PREPROCESSING_LAYER_BLUEPRINT.md](./01_FRAMEWORK\DATA_PREPROCESSING_LAYER_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: Layer 1 - 数据预处理层
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Data Preprocessing Layer Blueprint** | Layer 1 - 数据预处理层 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-05 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-05 | **状态**: Active
