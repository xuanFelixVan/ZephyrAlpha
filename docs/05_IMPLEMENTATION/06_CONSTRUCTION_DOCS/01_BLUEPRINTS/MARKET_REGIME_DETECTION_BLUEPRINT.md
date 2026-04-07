---
module_id: MARKET_REGIME_DETECTION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 6 ç»åä¼åå±?
compliance_level: ä¸ä¸æ å
responsibility:
  - å¸åºç¶ææ£æµ?
  - å¸åºç¯å¢è¯å«
  - ç¶æè½¬æ¢åæ?
  - å¸åºç¹å¾æå
layer: Layer 5 (策略执行层)
---

# MARKET REGIME DETECTION BLUEPRINT

> **æ ¸å¿èè´£**: Market Regime Detectionèå¾è®¾è®¡
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼Market Regime Detectionèå¾è®¾è®¡ç¸å³åå®¹
> - â?æ¬ææ¡£ä¸è´è´£ï¼å¶ä»æ¨¡ååå®?

ï»? ð æ§è¡æè¦

> **çæ¬**: v1.0
> **åå»ºæ¥æ**: 2026-04-06
> **æ ¸å¿å®ä½**: ä¸ºä¸­è§ç­ç¥å±æä¾å¸åºç¶æè¯å«è½å?
> **ç´¢å¼**: `MARKET_REGIME_DETECTION_001`
> **å¼åå¨æ?*: 2.5å?

## æ ¸å¿å®ä½

layer: Layer 5 (策略执行层)
---
---ï¼ç¡®ä¿ç³»ç»åè½çç¨³å®è¿è¡åé«ææ§è¡ã?

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


## ð¯ æ¨¡åå®ä½ä¸èè´?

### å±çº§å®ä½

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?          æ¸é£éåç³»ç» - ä¸çº§æ¶é´æ¡æ¶æ¶æ                â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â? ç¬¬ä¸çº§ï¼å®è§éç½®å±ï¼å­£åº¦/å¹´åº¦ï¼?                        â?
â? ç¬¬äºçº§ï¼ä¸­è§ç­ç¥å±ï¼å¨åº¦/æ¥åº¦ï¼?                        â?
â?   ââ å¸åºç¶æè¯å«ç³»ç»ï¼æ¬æ¨¡åï¼                        â?
â?   ââ é¿å°æ³å å­å·¥å?                                   â?
â?   ââ å¤å å­åæå¼æ?                                   â?
â?   ââ æ¥çº¿ç»åä¼åå?                                   â?
â? ç¬¬ä¸çº§ï¼å¾®è§æ§è¡å±ï¼æ¥å/åé/ç§çº§ï¼?                   â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### æ ¸å¿èè´£

| èè´£ç±»å« | å·ä½èè´£ | è¾åºäº§ç© |
|---------|---------|---------|
| **ç¶æè¯å?* | è¯å«å½åå¸åºç¶æ?| å¸åºç¶ææ ç­?|
| **ç¹å¾æå** | æåå¸åºç¹å¾ææ  | ç¹å¾åé |
| **æ¨¡åè®­ç»** | è®­ç»ç¶æè¯å«æ¨¡å?| è®­ç»å¥½çæ¨¡å |
| **ç¶æé¢æµ?* | é¢æµæªæ¥å¸åºç¶æ?| ç¶æé¢æµç»æ?|
| **è½¬æ¢é¢è­¦** | é¢è­¦ç¶æè½¬æ?| é¢è­¦ä¿¡å· |

### éèè´£è¾¹ç?

- â?**å å­è®¡ç®**: ç±é¿å°æ³å å­å·¥åè´è´£
- â?**ç»åä¼å**: ç±æ¥çº¿ç»åä¼åå¨è´è´£
- â?**äº¤ææ§è¡**: ç±å¾®è§æ§è¡å±è´è´£
- â?**ç»æµèå¼å¤æ­**: ç±å®è§éç½®å±è´è´£


## ð§ å³é®ç»ä»¶è®¾è®¡

### 1. ç¹å¾æåå?(Feature Extractor)

```python
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats

class MarketFeatureExtractor:
    """å¸åºç¹å¾æåå?""
    
    def __init__(self):
        self.trend_extractor = TrendFeatureExtractor()
        self.volatility_extractor = VolatilityFeatureExtractor()
        self.liquidity_extractor = LiquidityFeatureExtractor()
        self.sentiment_extractor = SentimentFeatureExtractor()
        
    def extract_features(self, 
                        market_data: pd.DataFrame,
                        window: int = 20) -> pd.DataFrame:
        """æåå¸åºç¹å¾"""
        features = pd.DataFrame(index=market_data.index)
        
        # æåè¶å¿ç¹å¾
        trend_features = self.trend_extractor.extract(market_data, window)
        features = pd.concat([features, trend_features], axis=1)
        
        # æåæ³¢å¨çç¹å¾?
        volatility_features = self.volatility_extractor.extract(market_data, window)
        features = pd.concat([features, volatility_features], axis=1)
        
        # æåæµå¨æ§ç¹å¾?
        liquidity_features = self.liquidity_extractor.extract(market_data, window)
        features = pd.concat([features, liquidity_features], axis=1)
        
        # æåæç»ªç¹å¾
        sentiment_features = self.sentiment_extractor.extract(market_data, window)
        features = pd.concat([features, sentiment_features], axis=1)
        
        return features


class TrendFeatureExtractor:
    """è¶å¿ç¹å¾æåå?""
    
    def extract(self, data: pd.DataFrame, window: int) -> pd.DataFrame:
        """æåè¶å¿ç¹å¾"""
        features = pd.DataFrame(index=data.index)
        
        # 1. ç§»å¨å¹³åçº¿æç?
        features['ma_slope'] = self._calculate_ma_slope(data['close'], window)
        
        # 2. ä»·æ ¼å¨é
        features['momentum'] = data['close'].pct_change(window)
        
        # 3. è¶å¿å¼ºåº¦ï¼ADXï¼?
        features['adx'] = self._calculate_adx(data, window)
        
        # 4. ä»·æ ¼ä½ç½®ï¼ç¸å¯¹äºNæ¥é«ä½ç¹ï¼?
        features['price_position'] = (data['close'] - data['low'].rolling(window).min()) / \
                                     (data['high'].rolling(window).max() - data['low'].rolling(window).min())
        
        # 5. MACD
        features['macd'], features['macd_signal'], features['macd_hist'] = \
            self._calculate_macd(data['close'])
        
        return features
    
    def _calculate_ma_slope(self, prices: pd.Series, window: int) -> pd.Series:
        """è®¡ç®ç§»å¨å¹³åçº¿æç?""
        ma = prices.rolling(window).mean()
        slope = ma.diff() / ma.shift(1)
        return slope
    
    def _calculate_adx(self, data: pd.DataFrame, window: int) -> pd.Series:
        """è®¡ç®ADXææ """
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
        """è®¡ç®çå®æ³¢å¹"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr
    
    def _calculate_macd(self, prices: pd.Series) -> tuple:
        """è®¡ç®MACDææ """
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        return macd, signal, hist


class VolatilityFeatureExtractor:
    """æ³¢å¨çç¹å¾æåå¨"""
    
    def extract(self, data: pd.DataFrame, window: int) -> pd.DataFrame:
        """æåæ³¢å¨çç¹å¾?""
        features = pd.DataFrame(index=data.index)
        
        # 1. åå²æ³¢å¨ç?
        features['historical_vol'] = data['close'].pct_change().rolling(window).std() * np.sqrt(252)
        
        # 2. Parkinsonæ³¢å¨ç?
        features['parkinson_vol'] = self._calculate_parkinson_volatility(data, window)
        
        # 3. Garman-Klassæ³¢å¨ç?
        features['garman_klass_vol'] = self._calculate_garman_klass_volatility(data, window)
        
        # 4. æ³¢å¨çååº?
        features['vol_skew'] = data['close'].pct_change().rolling(window).skew()
        
        # 5. æ³¢å¨çå³°åº?
        features['vol_kurtosis'] = data['close'].pct_change().rolling(window).kurt()
        
        # 6. VIX-likeææ 
        features['vix_like'] = features['historical_vol'] * 100
        
        return features
    
    def _calculate_parkinson_volatility(self, data: pd.DataFrame, window: int) -> pd.Series:
        """è®¡ç®Parkinsonæ³¢å¨ç?""
        high = data['high']
        low = data['low']
        
        hl_ratio = np.log(high / low)
        parkinson_vol = np.sqrt(
            (hl_ratio ** 2).rolling(window).mean() / (4 * np.log(2))
        ) * np.sqrt(252)
        
        return parkinson_vol
    
    def _calculate_garman_klass_volatility(self, data: pd.DataFrame, window: int) -> pd.Series:
        """è®¡ç®Garman-Klassæ³¢å¨ç?""
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
    """æµå¨æ§ç¹å¾æåå¨"""
    
    def extract(self, data: pd.DataFrame, window: int) -> pd.DataFrame:
        """æåæµå¨æ§ç¹å¾?""
        features = pd.DataFrame(index=data.index)
        
        # 1. æäº¤éååç
        features['volume_change'] = data['volume'].pct_change(window)
        
        # 2. æäº¤é¢ååç
        features['amount_change'] = data['amount'].pct_change(window) if 'amount' in data.columns else 0
        
        # 3. æ¢æç?
        features['turnover_rate'] = data['turnover_rate'] if 'turnover_rate' in data.columns else \
            data['volume'] / data['volume'].rolling(window).mean()
        
        # 4. Amihudéæµå¨æ§ææ ?
        features['amihud_illiquidity'] = self._calculate_amihud_illiquidity(data, window)
        
        # 5. æäº¤éå æä»·æ ¼åç¦?
        features['vwap_deviation'] = self._calculate_vwap_deviation(data, window)
        
        return features
    
    def _calculate_amihud_illiquidity(self, data: pd.DataFrame, window: int) -> pd.Series:
        """è®¡ç®Amihudéæµå¨æ§ææ ?""
        returns = abs(data['close'].pct_change())
        volume = data['volume']
        
        illiquidity = (returns / volume).rolling(window).mean()
        return illiquidity
    
    def _calculate_vwap_deviation(self, data: pd.DataFrame, window: int) -> pd.Series:
        """è®¡ç®VWAPåç¦»åº?""
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        vwap = (typical_price * data['volume']).rolling(window).sum() / \
               data['volume'].rolling(window).sum()
        
        deviation = (data['close'] - vwap) / vwap
        return deviation


class SentimentFeatureExtractor:
    """æç»ªç¹å¾æåå?""
    
    def extract(self, data: pd.DataFrame, window: int) -> pd.DataFrame:
        """æåæç»ªç¹å¾"""
        features = pd.DataFrame(index=data.index)
        
        # 1. æ¶¨è·åæ¯ä¾?
        features['limit_ratio'] = self._calculate_limit_ratio(data, window)
        
        # 2. ä¸æ¶¨ä¸è·æ¯ä¾
        features['advance_decline_ratio'] = self._calculate_advance_decline_ratio(data, window)
        
        # 3. æ°é«æ°ä½æ¯ä¾
        features['new_high_low_ratio'] = self._calculate_new_high_low_ratio(data, window)
        
        # 4. å¸åºå®½åº¦
        features['market_breadth'] = self._calculate_market_breadth(data, window)
        
        return features
    
    def _calculate_limit_ratio(self, data: pd.DataFrame, window: int) -> pd.Series:
        """è®¡ç®æ¶¨è·åæ¯ä¾?""
        # ç®åå®ç°ï¼ä½¿ç¨ä»·æ ¼ååçä»£æ?
        price_change = data['close'].pct_change()
        limit_up = (price_change >= 0.095).rolling(window).mean()
        limit_down = (price_change <= -0.095).rolling(window).mean()
        
        return limit_up / (limit_down + 1e-10)
    
    def _calculate_advance_decline_ratio(self, data: pd.DataFrame, window: int) -> pd.Series:
        """è®¡ç®ä¸æ¶¨ä¸è·æ¯ä¾"""
        price_change = data['close'].pct_change()
        advance = (price_change > 0).rolling(window).mean()
        decline = (price_change < 0).rolling(window).mean()
        
        return advance / (decline + 1e-10)
    
    def _calculate_new_high_low_ratio(self, data: pd.DataFrame, window: int) -> pd.Series:
        """è®¡ç®æ°é«æ°ä½æ¯ä¾"""
        new_high = (data['close'] == data['high'].rolling(window).max()).rolling(window).mean()
        new_low = (data['close'] == data['low'].rolling(window).min()).rolling(window).mean()
        
        return new_high / (new_low + 1e-10)
    
    def _calculate_market_breadth(self, data: pd.DataFrame, window: int) -> pd.Series:
        """è®¡ç®å¸åºå®½åº¦"""
        # ä½¿ç¨ä»·æ ¼ç¸å¯¹äºç§»å¨å¹³åçº¿çä½ç½?
        ma = data['close'].rolling(window).mean()
        breadth = (data['close'] > ma).rolling(window).mean()
        
        return breadth
```

### 2. éé©¬å°å¯å¤«æ¨¡å?(Hidden Markov Model)

```python
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from hmmlearn import hmm

class MarketRegimeHMM:
    """åºäºéé©¬å°å¯å¤«æ¨¡åçå¸åºç¶æè¯å?""
    
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
        """è®­ç»HMMæ¨¡å"""
        # åå¤è®­ç»æ°æ®
        X = features.values
        
        # æ åå?
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # è®­ç»HMMæ¨¡å
        self.model = hmm.GaussianHMM(
            n_components=self.n_states,
            covariance_type='full',
            n_iter=100,
            random_state=42
        )
        
        self.model.fit(X_scaled)
        self.scaler = scaler
        
    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        """é¢æµå¸åºç¶æ?""
        X = features.values
        X_scaled = self.scaler.transform(X)
        
        # é¢æµéç¶æåºå?
        hidden_states = self.model.predict(X_scaled)
        
        # è®¡ç®ç¶ææ¦ç?
        state_probs = self.model.predict_proba(X_scaled)
        
        # è½¬æ¢ä¸ºDataFrame
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
        """è·åç¶æè½¬ç§»ç©é?""
        transmat = self.model.transmat_
        
        transmat_df = pd.DataFrame(
            transmat,
            index=[self.state_names[i] for i in range(self.n_states)],
            columns=[self.state_names[i] for i in range(self.n_states)]
        )
        
        return transmat_df
    
    def get_state_duration(self, state_series: pd.Series) -> Dict[str, float]:
        """è®¡ç®åç¶æå¹³åæç»­æ¶é?""
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

### 3. æºå¨å­¦ä¹ åç±»å?(ML Classifier)

```python
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

class MarketRegimeClassifier:
    """åºäºæºå¨å­¦ä¹ çå¸åºç¶æåç±»å¨"""
    
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
        """åå»ºè®­ç»æ ç­¾"""
        labels = pd.Series(index=returns.index, dtype=str)
        
        # å®ä¹æ ç­¾è§å
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
        """è®­ç»åç±»å?""
        # åå²è®­ç»éåæµè¯é?
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42
        )
        
        # è®­ç»æ¨¡å
        self.model.fit(X_train, y_train)
        
        # è¯ä¼°æ¨¡å
        y_pred = self.model.predict(X_test)
        
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred)
        
        return {
            'classification_report': report,
            'confusion_matrix': cm,
            'feature_importance': dict(zip(features.columns, self.model.feature_importances_))
        }
    
    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        """é¢æµå¸åºç¶æ?""
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

### 4. éæå­¦ä¹ å?(Ensemble Learner)

```python
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

class MarketRegimeEnsemble:
    """å¸åºç¶æè¯å«éæå­¦ä¹ å¨"""
    
    def __init__(self):
        self.hmm_model = MarketRegimeHMM()
        self.ml_classifier = MarketRegimeClassifier()
        self.rule_engine = MarketRegimeRuleEngine()
        
        # æééç½®
        self.weights = {
            'hmm': 0.4,
            'ml': 0.4,
            'rule': 0.2
        }
        
    def train(self, 
             features: pd.DataFrame,
             returns: pd.Series,
             volatility: pd.Series) -> None:
        """è®­ç»æææ¨¡å?""
        # è®­ç»HMM
        self.hmm_model.train(features)
        
        # åå»ºæ ç­¾å¹¶è®­ç»MLåç±»å?
        labels = self.ml_classifier.create_labels(returns, volatility)
        self.ml_classifier.train(features, labels)
        
    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        """éæé¢æµ"""
        # HMMé¢æµ
        hmm_states, hmm_probs = self.hmm_model.predict(features)
        
        # MLé¢æµ
        ml_states, ml_probs = self.ml_classifier.predict(features)
        
        # è§åå¼æé¢æµ
        rule_states, rule_probs = self.rule_engine.predict(features)
        
        # å ææç¥¨
        final_states = self._weighted_voting(
            hmm_states, ml_states, rule_states,
            hmm_probs, ml_probs, rule_probs
        )
        
        # è®¡ç®æç»æ¦ç?
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
        """å ææç¥¨"""
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
                
                # å ä¸æ¦çæé
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
        """å ææ¦ç"""
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
        
        # å½ä¸å?
        final_probs = final_probs.div(final_probs.sum(axis=1), axis=0)
        
        return final_probs


class MarketRegimeRuleEngine:
    """åºäºè§åçå¸åºç¶æè¯å«å¼æ?""
    
    def __init__(self):
        self.state_names = ['BULL', 'BEAR', 'SIDEWAYS', 'HIGH_VOL', 'CRISIS']
        
    def predict(self, features: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        """åºäºè§åé¢æµå¸åºç¶æ?""
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
        """åºç¨è§å"""
        probs = pd.Series(0.0, index=self.state_names)
        
        # è§å1: è¶å¿å¤æ­
        if features.get('ma_slope', 0) > 0.01 and features.get('adx', 0) > 25:
            probs['BULL'] += 0.3
        elif features.get('ma_slope', 0) < -0.01 and features.get('adx', 0) > 25:
            probs['BEAR'] += 0.3
        else:
            probs['SIDEWAYS'] += 0.3
        
        # è§å2: æ³¢å¨çå¤æ?
        if features.get('historical_vol', 0) > 0.35:
            probs['HIGH_VOL'] += 0.3
        elif features.get('historical_vol', 0) > 0.45 and features.get('momentum', 0) < -0.05:
            probs['CRISIS'] += 0.4
        
        # è§å3: å¨éå¤æ­
        if features.get('momentum', 0) > 0.05:
            probs['BULL'] += 0.2
        elif features.get('momentum', 0) < -0.05:
            probs['BEAR'] += 0.2
        
        # è§å4: æµå¨æ§å¤æ?
        if features.get('amihud_illiquidity', 0) > 1e-8:
            probs['CRISIS'] += 0.2
        
        # å½ä¸åæ¦ç?
        if probs.sum() > 0:
            probs = probs / probs.sum()
        else:
            probs['SIDEWAYS'] = 1.0
        
        # éæ©æå¤§æ¦ççç¶æ?
        state = probs.idxmax()
        
        return state, probs
```

---

## ð æ°æ®æ¨¡åè®¾è®¡

### å¸åºç¶æè¯å«ç»æè¡¨

```sql
CREATE TABLE market_regime_detection (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    trade_date DATE NOT NULL COMMENT 'äº¤ææ¥æ',
    market_state VARCHAR(20) NOT NULL COMMENT 'å¸åºç¶æ?,
    state_probability DECIMAL(5, 4) COMMENT 'ç¶ææ¦ç?,
    bull_prob DECIMAL(5, 4) COMMENT 'çå¸æ¦ç',
    bear_prob DECIMAL(5, 4) COMMENT 'çå¸æ¦ç',
    sideways_prob DECIMAL(5, 4) COMMENT 'éè¡å¸æ¦ç?,
    high_vol_prob DECIMAL(5, 4) COMMENT 'é«æ³¢å¨å¸æ¦ç',
    crisis_prob DECIMAL(5, 4) COMMENT 'å±æºå¸æ¦ç?,
    detection_method VARCHAR(50) COMMENT 'æ£æµæ¹æ³?,
    confidence_score DECIMAL(5, 4) COMMENT 'ç½®ä¿¡åº¦åæ?,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'åå»ºæ¶é´',
    UNIQUE KEY uk_trade_date (trade_date),
    INDEX idx_market_state (market_state),
    INDEX idx_trade_date (trade_date)
) COMMENT 'å¸åºç¶æè¯å«ç»æè¡¨';
```

### å¸åºç¹å¾è¡?

```sql
CREATE TABLE market_features (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    trade_date DATE NOT NULL COMMENT 'äº¤ææ¥æ',
    feature_name VARCHAR(50) NOT NULL COMMENT 'ç¹å¾åç§°',
    feature_value DECIMAL(20, 10) COMMENT 'ç¹å¾å?,
    feature_category VARCHAR(50) COMMENT 'ç¹å¾ç±»å«',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'åå»ºæ¶é´',
    UNIQUE KEY uk_date_feature (trade_date, feature_name),
    INDEX idx_trade_date (trade_date),
    INDEX idx_feature_category (feature_category)
) COMMENT 'å¸åºç¹å¾è¡?;
```

### ç¶æè½¬æ¢è®°å½è¡¨

```sql
CREATE TABLE regime_transition_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transition_date DATE NOT NULL COMMENT 'è½¬æ¢æ¥æ',
    from_state VARCHAR(20) NOT NULL COMMENT 'åç¶æ?,
    to_state VARCHAR(20) NOT NULL COMMENT 'æ°ç¶æ?,
    transition_probability DECIMAL(5, 4) COMMENT 'è½¬æ¢æ¦ç',
    duration_days INT COMMENT 'ç¶ææç»­å¤©æ?,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'åå»ºæ¶é´',
    INDEX idx_transition_date (transition_date),
    INDEX idx_from_state (from_state),
    INDEX idx_to_state (to_state)
) COMMENT 'ç¶æè½¬æ¢è®°å½è¡¨';
```

---

## ð æ¥å£è§è

### RESTful APIæ¥å£

#### 1. è·åå½åå¸åºç¶æ?

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

#### 2. è·ååå²å¸åºç¶æ?

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

#### 3. è·åç¶æè½¬æ¢é¢è­?

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

---

## ð å®æ½è¦ç¹

### é¶æ®µ1ï¼ç¹å¾æåå¨å¼åï¼ç¬?å¨ï¼

**ä»»å¡**:
1. â?å®ç°è¶å¿ç¹å¾æåå?
2. â?å®ç°æ³¢å¨çç¹å¾æåå¨
3. â?å®ç°æµå¨æ§ç¹å¾æåå¨
4. â?å®ç°æç»ªç¹å¾æåå?
5. â?ç¼åååæµè¯

**éªæ¶æ å**:
- ææç¹å¾å¯ä»¥æ­£ç¡®æå?
- ç¹å¾å¼èå´åç?
- ååæµè¯è¦ççâ¥80%

---

### é¶æ®µ2ï¼æ¨¡åå¼åï¼ç¬?-2å¨ï¼

**ä»»å¡**:
1. â?å®ç°HMMæ¨¡å
2. â?å®ç°MLåç±»å?
3. â?å®ç°è§åå¼æ
4. â?å®ç°éæå­¦ä¹ å?
5. â?ç¼åååæµè¯

**éªæ¶æ å**:
- æææ¨¡åå¯ä»¥æ­£å¸¸è®­ç»åé¢æµ
- æ¨¡åæ§è½è¾¾æ 
- ååæµè¯è¦ççâ¥80%

---

### é¶æ®µ3ï¼éææµè¯ä¸ä¼åï¼ç¬¬2-3å¨ï¼

**ä»»å¡**:
1. â?ç¼åéææµè¯ç¨ä¾
2. â?æ§è¡æ¨¡åæ§è½è¯ä¼°
3. â?ä¼åæ¨¡ååæ°
4. â?é¨ç½²å°çäº§ç¯å¢?
5. â?ç¼åé¨ç½²ææ¡£

**éªæ¶æ å**:
- éææµè¯å¨é¨éè¿
- æ¨¡ååç¡®çâ¥80%
- é¨ç½²ææ¡£å®æ´

---

## ð§ª æµè¯ç­ç¥

### ååæµè¯

```python
import pytest
import pandas as pd
import numpy as np

def test_trend_feature_extractor():
    """æµè¯è¶å¿ç¹å¾æåå?""
    extractor = TrendFeatureExtractor()
    
    # åå»ºæµè¯æ°æ®
    data = pd.DataFrame({
        'open': [100, 101, 102, 103, 104],
        'high': [105, 106, 107, 108, 109],
        'low': [95, 96, 97, 98, 99],
        'close': [102, 103, 104, 105, 106]
    })
    
    # æåç¹å¾
    features = extractor.extract(data, window=3)
    
    # éªè¯ç»æ
    assert 'ma_slope' in features.columns
    assert 'momentum' in features.columns
    assert 'adx' in features.columns


def test_hmm_model():
    """æµè¯HMMæ¨¡å"""
    model = MarketRegimeHMM(n_states=5)
    
    # åå»ºæµè¯æ°æ®
    features = pd.DataFrame(
        np.random.randn(100, 10),
        columns=[f'feature_{i}' for i in range(10)]
    )
    
    # è®­ç»æ¨¡å
    model.train(features)
    
    # é¢æµ
    states, probs = model.predict(features)
    
    # éªè¯ç»æ
    assert len(states) == len(features)
    assert probs.shape == (len(features), 5)
```

---

## ð æ§è½ææ 

### æ¨¡åæ§è½è¦æ±

| ææ  | ç®æ å?|
|------|--------|
| **ç¶æè¯å«åç¡®ç** | â?0% |
| **ç¶æè½¬æ¢å¬åç** | â?0% |
| **é¢æµå»¶è¿** | <1ç§?|
| **æ¨¡åæ´æ°é¢ç** | æ¯æ¥ |

### ç¹å¾æåæ§è½

| ç¹å¾ç±»å | è®¡ç®æ¶é´ |
|---------|---------|
| **è¶å¿ç¹å¾** | <100ms |
| **æ³¢å¨çç¹å¾?* | <150ms |
| **æµå¨æ§ç¹å¾?* | <100ms |
| **æç»ªç¹å¾** | <200ms |

---

## ð ç¸å³ææ¡£

- [é¿å°æ³å å­å·¥åèå¾](./ALPHA_FACTOR_FACTORY_BLUEPRINT.md)
- å¤å å­åæå¼æèå?
- ä¸ä¸å¤æ¶é´æ¡æ¶ç­ç¥æ¶æ?

---

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**èå¾ç¶æ?*: â?è®¾è®¡å®æ
**ä¸ä¸æ­?*: å¼å§å®æ½é¶æ®? - ç¹å¾æåå¨å¼å?
---

## 1. ææ¡£æ²»ç

### 1.1 System_Manifest.mdç´¢å¼

```markdown
#### Layer 3: ä¸­è§ç­ç¥å±?
##### 6.001. Meso Market Regime
- **æ¨¡åID**: MARKET_REGIME_DETECTION_001
- **èå¾ææ¡£**: MARKET_REGIME_DETECTION_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾åå»?
- **èè´£**: ä¸­è§ç­ç¥å±å¸åºç¶æè¯å?
- **ç¶æ?*: Active
```

### 1.2 æ¨¡åèè´£è¾¹ç

| æ¨¡å | èè´£ | è¾¹ç |
|------|------|------|
| **Meso Market Regime** | ä¸­è§ç­ç¥å±å¸åºç¶æè¯å?| **æ ¸å¿æ¨¡å** |

### 1.3 çæ¬ç®¡ç

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active
