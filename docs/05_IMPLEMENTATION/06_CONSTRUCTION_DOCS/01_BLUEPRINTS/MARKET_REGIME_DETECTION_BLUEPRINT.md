---
module_id: MARKET_REGIME_DETECTION_BLUEPRINT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 市场范式检测
  - 范式识别
  - 状态转换
  - 趋势判断


﻿
module_id: MARKET_REGIME_DETECTION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
responsibility:
  - 系统架构蓝图设计与实施指导与实施方案
layer: Layer 5 (策略执行层)
---


# MARKET REGIME DETECTION BLUEPRINT

> **核心职责**: Market Regime Detection蓝图设计
> **职责边界**: 
®?


> **版本**: v1.0
> **创建日期**: 2026-04-06
> **索引**: `MARKET_REGIME_DETECTION_001`

## 核心定位

市场状态检测模块，识别和分类市场状态（牛市、熊市、震荡市等），为投资决策提供市场环境判断，支持多种状态检测算法和模型。
## 设计目标

### 主要目标

1. **功能完整性**: 确保MARKET REGIME DETECTION功能完整，满足业务需求
2. **性能优化**: 提升系统性能，降低资源消耗
3. **可维护性**: 提高代码质量，便于后续维护
4. **可扩展性**: 支持功能扩展，适应业务变化

### 质量目标

- 代码覆盖率: ≥80%
- 性能指标: 满足设计要求
- 文档完整性: 100%


## 核心功能

### 功能清单

1. **数据管理**: 提供数据存储、查询、更新功能
2. **业务逻辑**: 实现核心业务逻辑处理
3. **接口服务**: 提供标准化的API接口
4. **监控告警**: 实时监控系统状态

### 功能特性

- 高可用性设计
- 自动故障恢复
- 灵活配置管理


## 实现方案

### 技术架构

采用MARKET REGIME DETECTION化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控



### 层级定位

```
```

### 核心职责

|---------|---------|---------|
| **特征提取** | 提取市场特征指标 | 特征向量 |






```python
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats

class MarketFeatureExtractor:
    
    def __init__(self):
        self.trend_extractor = TrendFeatureExtractor()
        self.volatility_extractor = VolatilityFeatureExtractor()
        self.liquidity_extractor = LiquidityFeatureExtractor()
        self.sentiment_extractor = SentimentFeatureExtractor()
        
    def extract_features(self, 
                        market_data: pd.DataFrame,
                        window: int = 20) -> pd.DataFrame:
        """提取市场特征"""
        features = pd.DataFrame(index=market_data.index)
        
        # 提取趋势特征
        trend_features = self.trend_extractor.extract(market_data, window)
        features = pd.concat([features, trend_features], axis=1)
        
        volatility_features = self.volatility_extractor.extract(market_data, window)
        features = pd.concat([features, volatility_features], axis=1)
        
        liquidity_features = self.liquidity_extractor.extract(market_data, window)
        features = pd.concat([features, liquidity_features], axis=1)
        
绪特征
        sentiment_features = self.sentiment_extractor.extract(market_data, window)
        features = pd.concat([features, sentiment_features], axis=1)
        
        return features


class TrendFeatureExtractor:
    
    def extract(self, data: pd.DataFrame, window: int) -> pd.DataFrame:
        """提取趋势特征"""
        features = pd.DataFrame(index=data.index)
        
        features['ma_slope'] = self._calculate_ma_slope(data['close'], window)
        
        # 2. 价格动量
        features['momentum'] = data['close'].pct_change(window)
        
        features['adx'] = self._calculate_adx(data, window)
        
        features['price_position'] = (data['close'] - data['low'].rolling(window).min()) / \
                                     (data['high'].rolling(window).max() - data['low'].rolling(window).min())
        
        # 5. MACD
        features['macd'], features['macd_signal'], features['macd_hist'] = \
            self._calculate_macd(data['close'])
        
        return features
    
    def _calculate_ma_slope(self, prices: pd.Series, window: int) -> pd.Series:
        ma = prices.rolling(window).mean()
        slope = ma.diff() / ma.shift(1)
        return slope
    
    def _calculate_adx(self, data: pd.DataFrame, window: int) -> pd.Series:
        """计算ADX指标"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr = self._calculate_true_range(data)
        atr = tr.rolling(window).mean()
        
        plus_di = 100 * (plus_dm.rolling(window).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window).mean()
        
        return adx
    
    def _calculate_true_range(self, data: pd.DataFrame) -> pd.Series:
"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr
    
    def _calculate_macd(self, prices: pd.Series) -> tuple:
        """计算MACD指标"""
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        return macd, signal, hist


class VolatilityFeatureExtractor:
    """波动率特征提取器"""
    
    def extract(self, data: pd.DataFrame, window: int) -> pd.DataFrame:
        features = pd.DataFrame(index=data.index)
        
        features['historical_vol'] = data['close'].pct_change().rolling(window).std() * np.sqrt(252)
        
        features['parkinson_vol'] = self._calculate_parkinson_volatility(data, window)
        
        features['garman_klass_vol'] = self._calculate_garman_klass_volatility(data, window)
        
        features['vol_skew'] = data['close'].pct_change().rolling(window).skew()
        
        features['vol_kurtosis'] = data['close'].pct_change().rolling(window).kurt()
        
        # 6. VIX-like指标
        features['vix_like'] = features['historical_vol'] * 100
        
        return features
    
    def _calculate_parkinson_volatility(self, data: pd.DataFrame, window: int) -> pd.Series:
        high = data['high']
        low = data['low']
        
        hl_ratio = np.log(high / low)
        parkinson_vol = np.sqrt(
            (hl_ratio ** 2).rolling(window).mean() / (4 * np.log(2))
        ) * np.sqrt(252)
        
        return parkinson_vol
    
    def _calculate_garman_klass_volatility(self, data: pd.DataFrame, window: int) -> pd.Series:
        high = data['high']
        low = data['low']
        close = data['close']
        open_price = data['open']
        
        hl_log = np.log(high / low)
        co_log = np.log(close / open_price)
        
        gk_vol = np.sqrt(
            (0.5 * hl_log ** 2 - (2 * np.log(2) - 1) * co_log ** 2).rolling(window).mean()
        ) * np.sqrt(252)
        
        return gk_vol


class LiquidityFeatureExtractor:
    """流动性特征提取器"""
    
    def extract(self, data: pd.DataFrame, window: int) -> pd.DataFrame:
        features = pd.DataFrame(index=data.index)
        
        # 1. 成交量变化率
        features['volume_change'] = data['volume'].pct_change(window)
        
        # 2. 成交额变化率
        features['amount_change'] = data['amount'].pct_change(window) if 'amount' in data.columns else 0
        
        features['turnover_rate'] = data['turnover_rate'] if 'turnover_rate' in data.columns else \
            data['volume'] / data['volume'].rolling(window).mean()
        
        features['amihud_illiquidity'] = self._calculate_amihud_illiquidity(data, window)
        
        features['vwap_deviation'] = self._calculate_vwap_deviation(data, window)
        
        return features
    
    def _calculate_amihud_illiquidity(self, data: pd.DataFrame, window: int) -> pd.Series:
        returns = abs(data['close'].pct_change())
        volume = data['volume']
        
        illiquidity = (returns / volume).rolling(window).mean()
        return illiquidity
    
    def _calculate_vwap_deviation(self, data: pd.DataFrame, window: int) -> pd.Series:
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        vwap = (typical_price * data['volume']).rolling(window).sum() / \
               data['volume'].rolling(window).sum()
        
        deviation = (data['close'] - vwap) / vwap
        return deviation


class SentimentFeatureExtractor:
    """
    
    def extract(self, data: pd.DataFrame, window: int) -> pd.DataFrame:
绪特征"""
        features = pd.DataFrame(index=data.index)
        
        features['limit_ratio'] = self._calculate_limit_ratio(data, window)
        
        # 2. 上涨下跌比例
        features['advance_decline_ratio'] = self._calculate_advance_decline_ratio(data, window)
        
        # 3. 新高新低比例
        features['new_high_low_ratio'] = self._calculate_new_high_low_ratio(data, window)
        
        # 4. 市场宽度
        features['market_breadth'] = self._calculate_market_breadth(data, window)
        
        return features
    
    def _calculate_limit_ratio(self, data: pd.DataFrame, window: int) -> pd.Series:
        price_change = data['close'].pct_change()
        limit_up = (price_change >= 0.095).rolling(window).mean()
        limit_down = (price_change <= -0.095).rolling(window).mean()
        
        return limit_up / (limit_down + 1e-10)
    
    def _calculate_advance_decline_ratio(self, data: pd.DataFrame, window: int) -> pd.Series:
        """计算上涨下跌比例"""
        price_change = data['close'].pct_change()
        advance = (price_change > 0).rolling(window).mean()
        decline = (price_change < 0).rolling(window).mean()
        
        return advance / (decline + 1e-10)
    
    def _calculate_new_high_low_ratio(self, data: pd.DataFrame, window: int) -> pd.Series:
        """计算新高新低比例"""
        new_high = (data['close'] == data['high'].rolling(window).max()).rolling(window).mean()
        new_low = (data['close'] == data['low'].rolling(window).min()).rolling(window).mean()
        
        return new_high / (new_low + 1e-10)
    
    def _calculate_market_breadth(self, data: pd.DataFrame, window: int) -> pd.Series:
        """计算市场宽度"""
        ma = data['close'].rolling(window).mean()
        breadth = (data['close'] > ma).rolling(window).mean()
        
        return breadth
```


```python
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from hmmlearn import hmm

class MarketRegimeHMM:
    
    def __init__(self, n_states: int = 5):
        self.n_states = n_states
        self.model = None
        self.state_names = {
            0: 'BULL',
            1: 'BEAR',
            2: 'SIDEWAYS',
            3: 'HIGH_VOL',
            4: 'CRISIS'
        }
        
    def train(self, features: pd.DataFrame) -> None:
        """训练HMM模型"""
        # 准备训练数据
        X = features.values
        
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 训练HMM模型
        self.model = hmm.GaussianHMM(
            n_components=self.n_states,
            covariance_type='full',
            n_iter=100,
            random_state=42
        )
        
        self.model.fit(X_scaled)
        self.scaler = scaler
        
    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        X = features.values
        X_scaled = self.scaler.transform(X)
        
        hidden_states = self.model.predict(X_scaled)
        
        state_probs = self.model.predict_proba(X_scaled)
        
        # 转换为DataFrame
        state_series = pd.Series(
            [self.state_names[s] for s in hidden_states],
            index=features.index
        )
        
        state_probs_df = pd.DataFrame(
            state_probs,
            index=features.index,
            columns=[self.state_names[i] for i in range(self.n_states)]
        )
        
        return state_series, state_probs_df
    
    def get_transition_matrix(self) -> pd.DataFrame:
        transmat = self.model.transmat_
        
        transmat_df = pd.DataFrame(
            transmat,
            index=[self.state_names[i] for i in range(self.n_states)],
            columns=[self.state_names[i] for i in range(self.n_states)]
        )
        
        return transmat_df
    
    def get_state_duration(self, state_series: pd.Series) -> Dict[str, float]:
        durations = {}
        
        for state_name in self.state_names.values():
            state_mask = state_series == state_name
            state_changes = state_mask.astype(int).diff().fillna(0)
            
            starts = state_changes[state_changes == 1].index
            ends = state_changes[state_changes == -1].index
            
            if len(starts) > 0 and len(ends) > 0:
                if starts[0] > ends[0]:
                    ends = ends[1:]
                if len(starts) > len(ends):
                    starts = starts[:len(ends)]
                
                duration_list = [(end - start).days for start, end in zip(starts, ends)]
                durations[state_name] = np.mean(duration_list) if duration_list else 0
            else:
                durations[state_name] = 0
        
        return durations
```


```python
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

class MarketRegimeClassifier:
    """基于机器学习的市场状态分类器"""
    
    def __init__(self, model_type: str = 'random_forest'):
        self.model_type = model_type
        self.model = None
        self.state_names = ['BULL', 'BEAR', 'SIDEWAYS', 'HIGH_VOL', 'CRISIS']
        
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
    
    def create_labels(self, 
                     returns: pd.Series,
                     volatility: pd.Series) -> pd.Series:
        """创建训练标签"""
        labels = pd.Series(index=returns.index, dtype=str)
        
        # 定义标签规则
        for i in range(len(returns)):
            ret = returns.iloc[i]
            vol = volatility.iloc[i]
            
            if ret > 0.02 and vol < 0.20:
                labels.iloc[i] = 'BULL'
            elif ret < -0.02 and vol > 0.25:
                labels.iloc[i] = 'BEAR'
            elif abs(ret) < 0.01 and vol < 0.15:
                labels.iloc[i] = 'SIDEWAYS'
            elif vol > 0.35:
                labels.iloc[i] = 'HIGH_VOL'
            elif ret < -0.05 and vol > 0.40:
                labels.iloc[i] = 'CRISIS'
            else:
                labels.iloc[i] = 'SIDEWAYS'
        
        return labels
    
    def train(self, 
             features: pd.DataFrame,
             labels: pd.Series) -> Dict[str, Any]:
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42
        )
        
        # 训练模型
        self.model.fit(X_train, y_train)
        
        # 评估模型
        y_pred = self.model.predict(X_test)
        
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred)
        
        return {
            'classification_report': report,
            'confusion_matrix': cm,
            'feature_importance': dict(zip(features.columns, self.model.feature_importances_))
        }
    
    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        predictions = self.model.predict(features)
        probabilities = self.model.predict_proba(features)
        
        state_series = pd.Series(predictions, index=features.index)
        
        state_probs_df = pd.DataFrame(
            probabilities,
            index=features.index,
            columns=self.model.classes_
        )
        
        return state_series, state_probs_df
```


```python
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

class MarketRegimeEnsemble:
    """市场状态识别集成学习器"""
    
    def __init__(self):
        self.hmm_model = MarketRegimeHMM()
        self.ml_classifier = MarketRegimeClassifier()
        self.rule_engine = MarketRegimeRuleEngine()
        
        self.weights = {
            'hmm': 0.4,
            'ml': 0.4,
            'rule': 0.2
        }
        
    def train(self, 
             features: pd.DataFrame,
             returns: pd.Series,
             volatility: pd.Series) -> None:
        # 训练HMM
        self.hmm_model.train(features)
        
        labels = self.ml_classifier.create_labels(returns, volatility)
        self.ml_classifier.train(features, labels)
        
    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        """集成预测"""
        # HMM预测
        hmm_states, hmm_probs = self.hmm_model.predict(features)
        
        # ML预测
        ml_states, ml_probs = self.ml_classifier.predict(features)
        
        # 规则引擎预测
        rule_states, rule_probs = self.rule_engine.predict(features)
        
        # 加权投票
        final_states = self._weighted_voting(
            hmm_states, ml_states, rule_states,
            hmm_probs, ml_probs, rule_probs
        )
        
        final_probs = self._weighted_probability(
            hmm_probs, ml_probs, rule_probs
        )
        
        return final_states, final_probs
    
    def _weighted_voting(self,
                        hmm_states: pd.Series,
                        ml_states: pd.Series,
                        rule_states: pd.Series,
                        hmm_probs: pd.DataFrame,
                        ml_probs: pd.DataFrame,
                        rule_probs: pd.DataFrame) -> pd.Series:
        """加权投票"""
        final_states = pd.Series(index=hmm_states.index, dtype=str)
        
        for idx in hmm_states.index:
            scores = {}
            
            for state in self.hmm_model.state_names.values():
                score = 0
                if hmm_states.loc[idx] == state:
                    score += self.weights['hmm']
                if ml_states.loc[idx] == state:
                    score += self.weights['ml']
                if rule_states.loc[idx] == state:
                    score += self.weights['rule']
                
                # 加上概率权重
                if state in hmm_probs.columns:
                    score += self.weights['hmm'] * hmm_probs.loc[idx, state]
                if state in ml_probs.columns:
                    score += self.weights['ml'] * ml_probs.loc[idx, state]
                if state in rule_probs.columns:
                    score += self.weights['rule'] * rule_probs.loc[idx, state]
                
                scores[state] = score
            
            final_states.loc[idx] = max(scores, key=scores.get)
        
        return final_states
    
    def _weighted_probability(self,
                             hmm_probs: pd.DataFrame,
                             ml_probs: pd.DataFrame,
                             rule_probs: pd.DataFrame) -> pd.DataFrame:
        """加权概率"""
        all_states = list(set(
            hmm_probs.columns.tolist() +
            ml_probs.columns.tolist() +
            rule_probs.columns.tolist()
        ))
        
        final_probs = pd.DataFrame(
            index=hmm_probs.index,
            columns=all_states,
            dtype=float
        )
        
        for state in all_states:
            prob = 0
            if state in hmm_probs.columns:
                prob += self.weights['hmm'] * hmm_probs[state]
            if state in ml_probs.columns:
                prob += self.weights['ml'] * ml_probs[state]
            if state in rule_probs.columns:
                prob += self.weights['rule'] * rule_probs[state]
            
            final_probs[state] = prob
        
        final_probs = final_probs.div(final_probs.sum(axis=1), axis=0)
        
        return final_probs


class MarketRegimeRuleEngine:
    
    def __init__(self):
        self.state_names = ['BULL', 'BEAR', 'SIDEWAYS', 'HIGH_VOL', 'CRISIS']
        
    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        states = pd.Series(index=features.index, dtype=str)
        probs = pd.DataFrame(
            0.0,
            index=features.index,
            columns=self.state_names
        )
        
        for idx in features.index:
            state, prob = self._apply_rules(features.loc[idx])
            states.loc[idx] = state
            probs.loc[idx] = prob
        
        return states, probs
    
    def _apply_rules(self, features: pd.Series) -> Tuple[str, pd.Series]:
        """应用规则"""
        probs = pd.Series(0.0, index=self.state_names)
        
        # 规则1: 趋势判断
        if features.get('ma_slope', 0) > 0.01 and features.get('adx', 0) > 25:
            probs['BULL'] += 0.3
        elif features.get('ma_slope', 0) < -0.01 and features.get('adx', 0) > 25:
            probs['BEAR'] += 0.3
        else:
            probs['SIDEWAYS'] += 0.3
        
        if features.get('historical_vol', 0) > 0.35:
            probs['HIGH_VOL'] += 0.3
        elif features.get('historical_vol', 0) > 0.45 and features.get('momentum', 0) < -0.05:
            probs['CRISIS'] += 0.4
        
        # 规则3: 动量判断
        if features.get('momentum', 0) > 0.05:
            probs['BULL'] += 0.2
        elif features.get('momentum', 0) < -0.05:
            probs['BEAR'] += 0.2
        
        if features.get('amihud_illiquidity', 0) > 1e-8:
            probs['CRISIS'] += 0.2
        
        if probs.sum() > 0:
            probs = probs / probs.sum()
        else:
            probs['SIDEWAYS'] = 1.0
        
        state = probs.idxmax()
        
        return state, probs
```



## 📊 数据模型设计

### 市场状态识别结果表

```sql
CREATE TABLE market_regime_detection (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    trade_date DATE NOT NULL COMMENT '交易日期',
    bull_prob DECIMAL(5, 4) COMMENT '牛市概率',
    bear_prob DECIMAL(5, 4) COMMENT '熊市概率',
    high_vol_prob DECIMAL(5, 4) COMMENT '高波动市概率',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_trade_date (trade_date),
    INDEX idx_market_state (market_state),
    INDEX idx_trade_date (trade_date)
) COMMENT '市场状态识别结果表';
```


```sql
CREATE TABLE market_features (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    trade_date DATE NOT NULL COMMENT '交易日期',
    feature_name VARCHAR(50) NOT NULL COMMENT '特征名称',
    feature_category VARCHAR(50) COMMENT '特征类别',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_date_feature (trade_date, feature_name),
    INDEX idx_trade_date (trade_date),
    INDEX idx_feature_category (feature_category)
```

### 状态转换记录表

```sql
CREATE TABLE regime_transition_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transition_date DATE NOT NULL COMMENT '转换日期',
    transition_probability DECIMAL(5, 4) COMMENT '转换概率',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_transition_date (transition_date),
    INDEX idx_from_state (from_state),
    INDEX idx_to_state (to_state)
) COMMENT '状态转换记录表';
```



## 🔌 接口规范

### RESTful API接口


```
GET /api/v1/market/regime/current

Response:
{
    "status": "success",
    "data": {
        "trade_date": "2024-12-06",
        "market_state": "BULL",
        "state_probability": 0.75,
        "probabilities": {
            "BULL": 0.75,
            "BEAR": 0.10,
            "SIDEWAYS": 0.10,
            "HIGH_VOL": 0.04,
            "CRISIS": 0.01
        },
        "confidence_score": 0.85
    }
}
```


```
GET /api/v1/market/regime/history?start_date=2024-01-01&end_date=2024-12-31

Response:
{
    "status": "success",
    "data": [
        {
            "trade_date": "2024-12-06",
            "market_state": "BULL",
            "state_probability": 0.75
        },
        ...
    ]
}
```


```
GET /api/v1/market/regime/alert

Response:
{
    "status": "success",
    "alerts": [
        {
            "alert_type": "regime_transition",
            "current_state": "BULL",
            "predicted_state": "SIDEWAYS",
            "transition_probability": 0.35,
            "alert_time": "2024-12-06T10:00:00Z"
        }
    ]
}
```



## 🚀 实施要点


**任务**:

**验收标准**:




**任务**:

**验收标准**:
- 所有模型可以正常训练和预测
- 模型性能达标



### 阶段3：集成测试与优化（第2-3周）

**任务**:

**验收标准**:
- 模型准确率≥80%
- 部署文档完整



## 🧪 测试策略


```python
import pytest
import pandas as pd
import numpy as np

def test_trend_feature_extractor():
    extractor = TrendFeatureExtractor()
    
    # 创建测试数据
    data = pd.DataFrame({
        'open': [100, 101, 102, 103, 104],
        'high': [105, 106, 107, 108, 109],
        'low': [95, 96, 97, 98, 99],
        'close': [102, 103, 104, 105, 106]
    })
    
    # 提取特征
    features = extractor.extract(data, window=3)
    
    # 验证结果
    assert 'ma_slope' in features.columns
    assert 'momentum' in features.columns
    assert 'adx' in features.columns


def test_hmm_model():
    """测试HMM模型"""
    model = MarketRegimeHMM(n_states=5)
    
    # 创建测试数据
    features = pd.DataFrame(
        np.random.randn(100, 10),
        columns=[f'feature_{i}' for i in range(10)]
    )
    
    # 训练模型
    model.train(features)
    
    # 预测
    states, probs = model.predict(features)
    
    # 验证结果
    assert len(states) == len(features)
    assert probs.shape == (len(features), 5)
```



## 📈 性能指标

### 模型性能要求

|------|--------|
| **模型更新频率** | 每日 |

### 特征提取性能

| 特征类型 | 计算时间 |
|---------|---------|
| **趋势特征** | <100ms |
| **
绪特征** | <200ms |




- [阿尔法因子工厂蓝图](./ALPHA_FACTOR_FACTORY_BLUEPRINT.md)



## 📝 变更历史

|------|------|---------|------|





## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
##### 6.001. Meso Market Regime
- **模块ID**: MARKET_REGIME_DETECTION_001
- **蓝图文档**: MARKET_REGIME_DETECTION_BLUEPRINT.md
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|

### 1.3 版本管理

|------|------|----------|--------|



## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 实施团队 |



