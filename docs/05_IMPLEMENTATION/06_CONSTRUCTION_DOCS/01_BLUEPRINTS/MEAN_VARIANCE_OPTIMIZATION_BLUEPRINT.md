---
responsibility:
  - åå¼æ¹å·®ä¼å?
  - ææåæ²¿è®¡ç®
  - æä¼ç»åæ±è§?
  - é£é©æ¶çæè¡¡

module_id: MEAN_VARIANCE_OPTIMIZATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 6 ç»åä¼åå±?
compliance_level: ä¸ä¸æ å
layer: Layer 5.2 (组合优化)
---

# Mean Variance Optimization

## 核心定位

负责均值方差优化的设计与实现，优化资产权重。



> **æ ¸å¿èè´£**: åå¼æ¹å·®ä¼å?
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼åå¼æ¹å·®ä¼åãææåæ²¿è®¡ç®ãæä¼ç»åæ±è§?
> - â?æ¬ææ¡£ä¸è´è´£ï¼å å­ä¸­æ§çº¦æï¼ç±FACTOR_NEUTRAL_OPTIMIZATIONè´è´£ï¼?

## æ ¸å¿å®ä½

è´è´£Mean Variance Optimizationçè®¾è®¡ãå®ç°åç»´æ¤ï¼æä¾æ ¸å¿åè½æ¯æï¼ç¡®ä¿ç³»ç»æ¨¡åçç¨³å®è¿è¡åé«ææ§è¡ã?


## 1. æ¨¡åæ¦è¿°

### 1.1 æ ¸å¿èè´£

**åä¸èè´£**: å®ç°Markowitzåå¼æ¹å·®ä¼åçè®ºï¼æä¾ææåæ²¿è®¡ç®åæä¼ç»åæ±è§£è½å?

**èè´£è¾¹ç**:
- â?è´è´£: åå¼æ¹å·®ä¼åãææåæ²¿è®¡ç®ãæä¼ç»åæ±è§?
- â?ä¸è´è´? å å­ä¸­æ§çº¦æï¼ç±FACTOR_NEUTRAL_OPTIMIZATIONè´è´£ï¼?
- â?ä¸è´è´? é²æ£ä¼åï¼ç±ROBUST_OPTIMIZATIONè´è´£ï¼?
- â?ä¸è´è´? äº¤æææ¬å»ºæ¨¡ï¼ç±TRANSACTION_COST_MODELè´è´£ï¼?

### 1.2 å¼æºä¾èµ?

| åºå | çæ¬ | ç¨é?| GitHub Stars |
|
layer: Layer 5.2 (组合优化)
## 2. åè½è®¾è®¡

### 2.1 æ ¸å¿åè½

#### 2.1.1 ææåæ²¿è®¡ç®

```python
class EfficientFrontierCalculator:
    """
    ææåæ²¿è®¡ç®å?
    
    å¼æºä¾èµ? PyPortfolioOpt.EfficientFrontier
    """
    
    def calculate_efficient_frontier(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        n_points: int = 100
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        è®¡ç®ææåæ²¿
        
        åæ°:
            expected_returns: é¢ææ¶çåé (n_assets,)
            covariance_matrix: åæ¹å·®ç©é?(n_assets, n_assets)
            n_points: ææåæ²¿ç¹æ°
            
        è¿å:
            returns: æ¶ççæ°ç»?
            volatilities: æ³¢å¨çæ°ç»?
            weights: æéç©éµ (n_points, n_assets)
        """
        pass
```

#### 2.1.2 æä¼ç»åæ±è§?

```python
class OptimalPortfolioSolver:
    """
    æä¼ç»åæ±è§£å¨
    
    å¼æºä¾èµ? PyPortfolioOpt
    """
    
    def max_sharpe_portfolio(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        risk_free_rate: float = 0.02,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        æå¤§å¤æ®æ¯çç»å?
        
        è¿å:
            weights: æä¼æé?
            expected_return: é¢ææ¶ç
            volatility: æ³¢å¨ç?
            sharpe_ratio: å¤æ®æ¯ç
        """
        pass
    
    def min_volatility_portfolio(
        self,
        covariance_matrix: np.ndarray,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        æå°æ¹å·®ç»å?
        """
        pass
    
    def max_return_portfolio(
        self,
        expected_returns: np.ndarray,
        target_volatility: float,
        covariance_matrix: np.ndarray,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        ç»å®é£é©æ°´å¹³ä¸çæå¤§æ¶çç»å?
        """
        pass
```

#### 2.1.3 ç¦»æ£åéè½¬æ¢

```python
class DiscreteAllocationConverter:
    """
    ç¦»æ£åéè½¬æ¢å?
    
    å¼æºä¾èµ? PyPortfolioOpt.discrete_allocation
    """
    
    def convert_to_discrete(
        self,
        weights: Dict[str, float],
        latest_prices: Dict[str, float],
        total_portfolio_value: float,
        method: str = 'greedy'
    ) -> Tuple[Dict[str, int], float]:
        """
        å°è¿ç»­æéè½¬æ¢ä¸ºå®éå¯è´­ä¹°æ°é?
        
        åæ°:
            weights: èµäº§æéå­å¸
            latest_prices: ææ°ä»·æ ¼å­å?
            total_portfolio_value: æ»æèµéé¢?
            method: åéæ¹æ³ ('greedy' æ?'round')
            
        è¿å:
            allocation: èµäº§æ°éå­å¸
            leftover: å©ä½èµé
        """
        pass
```

### 2.2 åæ°ä¼°è®¡

#### 2.2.1 é¢ææ¶çä¼°è®¡

```python
class ExpectedReturnsEstimator:
    """
    é¢ææ¶çä¼°è®¡å?
    
    å¼æºä¾èµ? PyPortfolioOpt.expected_returns
    """
    
    def mean_historical_return(
        self,
        prices: pd.DataFrame,
        frequency: int = 252
    ) -> pd.Series:
        """
        åå²åå¼æ¶ç?
        """
        pass
    
    def ema_historical_return(
        self,
        prices: pd.DataFrame,
        span: int = 500,
        frequency: int = 252
    ) -> pd.Series:
        """
        ææ°å æç§»å¨å¹³åæ¶ç
        """
        pass
    
    def capm_return(
        self,
        prices: pd.DataFrame,
        market_prices: pd.DataFrame,
        risk_free_rate: float = 0.02,
        frequency: int = 252
    ) -> pd.Series:
        """
        CAPMé¢ææ¶ç
        """
        pass
```

#### 2.2.2 åæ¹å·®ä¼°è®?

```python
class CovarianceEstimator:
    """
    åæ¹å·®ä¼°è®¡å¨
    
    å¼æºä¾èµ? PyPortfolioOpt.risk_models
    """
    
    def sample_cov(
        self,
        returns: pd.DataFrame,
        frequency: int = 252
    ) -> pd.DataFrame:
        """
        æ ·æ¬åæ¹å·?
        """
        pass
    
    def semicovariance(
        self,
        returns: pd.DataFrame,
        benchmark: float = 0.0,
        frequency: int = 252
    ) -> pd.DataFrame:
        """
        ååæ¹å·®ï¼ä¸è¡é£é©ï¼
        """
        pass
    
    def exp_cov(
        self,
        returns: pd.DataFrame,
        span: int = 180,
        frequency: int = 252
    ) -> pd.DataFrame:
        """
        ææ°å æåæ¹å·?
        """
        pass
    
    def ledoit_wolf_shrinkage(
        self,
        returns: pd.DataFrame,
        frequency: int = 252
    ) -> pd.DataFrame:
        """
        Ledoit-Wolfæ¶ç¼©ä¼°è®¡
        """
        pass
```

### 2.3 çº¦æå¤ç

```python
class ConstraintHandler:
    """
    çº¦æå¤çå?
    
    å¼æºä¾èµ? PyPortfolioOptçº¦æç³»ç»
    """
    
    def add_weight_constraint(
        self,
        min_weight: float = 0.0,
        max_weight: float = 1.0
    ) -> None:
        """
        æéçº¦æï¼é¿ä»?ç­ä»éå¶ï¼?
        """
        pass
    
    def add_sector_constraint(
        self,
        sector_mapping: Dict[str, str],
        sector_weights: Dict[str, Tuple[float, float]]
    ) -> None:
        """
        è¡ä¸æéçº¦æ
        """
        pass
    
    def add_leverage_constraint(
        self,
        max_leverage: float = 1.0
    ) -> None:
        """
        æ æçº¦æ
        """
        pass
```

---
## 3. ææ¯è§æ ?

### 3.1 æ¥å£è®¾è®¡

```python
class MeanVarianceOptimizer:
    """
    åå¼æ¹å·®ä¼åå¨
    
    ä¸»è¦æ¥å£ç±»ï¼å°è£PyPortfolioOptåè½
    """
    
    def __init__(
        self,
        returns_data: pd.DataFrame,
        risk_free_rate: float = 0.02,
        frequency: int = 252
    ):
        """
        åå§åä¼åå¨
        
        åæ°:
            returns_data: æ¶ççæ°æ?(date Ã ticker)
            risk_free_rate: æ é£é©å©ç?
            frequency: å¹´åé¢ç
        """
        self.returns = returns_data
        self.risk_free_rate = risk_free_rate
        self.frequency = frequency
        
        # åå§åä¼°è®¡å¨
        self.mu_estimator = ExpectedReturnsEstimator()
        self.cov_estimator = CovarianceEstimator()
        self.solver = OptimalPortfolioSolver()
        self.converter = DiscreteAllocationConverter()
    
    def optimize(
        self,
        objective: str = 'max_sharpe',
        method_mu: str = 'mean',
        method_cov: str = 'sample',
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        æ§è¡ä¼å
        
        åæ°:
            objective: ä¼åç®æ  ('max_sharpe', 'min_volatility', 'max_return')
            method_mu: æ¶çä¼°è®¡æ¹æ³
            method_cov: åæ¹å·®ä¼°è®¡æ¹æ³?
            constraints: çº¦ææ¡ä»¶
            
        è¿å:
            ä¼åç»æå­å¸
        """
        pass
    
    def get_efficient_frontier(
        self,
        n_points: int = 100
    ) -> pd.DataFrame:
        """
        è·åææåæ²¿æ°æ®
        """
        pass
    
    def get_discrete_allocation(
        self,
        weights: Dict[str, float],
        latest_prices: Dict[str, float],
        total_value: float
    ) -> Tuple[Dict[str, int], float]:
        """
        è·åç¦»æ£åéæ¹æ¡
        """
        pass
```

### 3.2 æ°æ®ç»æ

```python
@dataclass
class OptimizationResult:
    """ä¼åç»ææ°æ®ç»æ"""
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    method_mu: str
    method_cov: str
    constraints: Dict
    timestamp: datetime

@dataclass
class EfficientFrontierPoint:
    """ææåæ²¿ç¹æ°æ®ç»æ?""
    return_: float
    volatility: float
    sharpe_ratio: float
    weights: np.ndarray
```

### 3.3 éç½®åæ°

```yaml
mean_variance_optimization:
  # æ¶çä¼°è®¡éç½®
  expected_returns:
    method: 'mean'  # mean, ema, capm
    ema_span: 500
    capm_benchmark: 'SPY'
    
  # åæ¹å·®ä¼°è®¡éç½?
  covariance:
    method: 'ledoit_wolf'  # sample, exp, ledoit_wolf, semicov
    exp_span: 180
    shrinkage_target: 'single_factor'
    
  # ä¼åéç½®
  optimization:
    objective: 'max_sharpe'
    risk_free_rate: 0.02
    frequency: 252
    
  # çº¦æéç½®
  constraints:
    min_weight: 0.0  # ä¸åè®¸åç©?
    max_weight: 0.10  # åèµäº§æå¤?0%
    max_leverage: 1.0  # ä¸ä½¿ç¨æ æ?
    
  # ç¦»æ£åééç½®
  discrete_allocation:
    method: 'greedy'
    min_remaining: 100  # æå°å©ä½èµé?
```


## ð æ¦è¿°

æ¬ææ¡£å®ä¹äºMEAN VARIANCE OPTIMIZATIONçæ ¸å¿åè½åææ¯å®ç°ã?

from pypfopt import EfficientFrontier, expected_returns, risk_models
from pypfopt.discrete_allocation import DiscreteAllocation

class PyPortfolioOptAdapter(MeanVarianceOptimizer):
    """
    PyPortfolioOptééå?
    
    ç´æ¥ä½¿ç¨PyPortfolioOptçæ ¸å¿åè?
    """
    
    def optimize(self, objective: str, **kwargs) -> Dict:
        # è®¡ç®é¢ææ¶ç
        mu = expected_returns.mean_historical_return(self.returns)
        
        # è®¡ç®åæ¹å·®ç©é?
        S = risk_models.risk_models.sample_cov(self.returns)
        
        # åå»ºææåæ²¿å¯¹è±¡
        ef = EfficientFrontier(mu, S)
        
        # æ·»å çº¦æ
        if self.constraints:
            self._add_constraints(ef)
        
        # æ§è¡ä¼å
        if objective == 'max_sharpe':
            weights = ef.max_sharpe()
        elif objective == 'min_volatility':
            weights = ef.min_volatility()
        
        # è·åç»åç»è®¡
        ret, vol, sharpe = ef.portfolio_performance()
        
        return {
            'weights': weights,
            'expected_return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe
        }
```

### 4.2 å¼åéç¨ç¢

| é¶æ®µ | ä»»å¡ | å·¥ä½é?| ä¾èµ |
|------|------|--------|------|
| ç¬?å¤?| PyPortfolioOptéææµè¯ | 8h | - |
| ç¬?å¤?| é¢ææ¶çä¼°è®¡å¨å®ç?| 8h | ç¬?å¤?|
| ç¬?å¤?| åæ¹å·®ä¼°è®¡å¨å®ç° | 8h | ç¬?å¤?|
| ç¬?å¤?| çº¦æå¤çå¨å®ç?| 8h | ç¬?-3å¤?|
| ç¬?å¤?| ç¦»æ£åéè½¬æ¢å®ç° | 8h | ç¬?å¤?|
| ç¬?å¤?| æ¥å£å°è£åæµè¯?| 8h | ç¬?å¤?|
| ç¬?å¤?| ææ¡£åéææµè¯?| 8h | ç¬?å¤?|

---

## 5. æµè¯è§æ ¼

### 5.1 ååæµè¯

```python
class TestMeanVarianceOptimizer:
    
    def test_max_sharpe_portfolio(self):
        """æµè¯æå¤§å¤æ®æ¯çç»å?""
        pass
    
    def test_min_volatility_portfolio(self):
        """æµè¯æå°æ¹å·®ç»å?""
        pass
    
    def test_efficient_frontier(self):
        """æµè¯ææåæ²¿è®¡ç®"""
        pass
    
    def test_discrete_allocation(self):
        """æµè¯ç¦»æ£åé"""
        pass
    
    def test_constraints(self):
        """æµè¯çº¦æå¤ç"""
        pass
```

### 5.2 éææµè¯

```python
class TestIntegration:
    
    def test_with_black_litterman(self):
        """æµè¯ä¸Black-Littermanæ¨¡åéæ"""
        pass
    
    def test_with_risk_parity(self):
        """æµè¯ä¸é£é©å¹³ä»·ç­ç¥éæ?""
        pass
    
    def test_with_rebalancing(self):
        """æµè¯ä¸åå¹³è¡¡ç³»ç»éæ"""
        pass
```

---

## 6. æ§è½ææ 

### 6.1 è®¡ç®æ§è½

| ææ  | ç®æ å?| æµéæ¹æ³ |
|------|--------|----------|
| ä¼åæ¶é´ï¼?00èµäº§ï¼?| <100ms | æ¶é´æµè¯ |
| ææåæ²¿è®¡ç®ï¼?00ç¹ï¼ | <1s | æ¶é´æµè¯ |
| åå­å ç¨ | <100MB | åå­çæ§ |

### 6.2 æ°å¼ç¨³å®æ?

| ææ  | ç®æ å?| æµéæ¹æ³ |
|------|--------|----------|
| æéå?| 1.0Â±1e-6 | æ°å¼éªè¯?|
| çº¦ææ»¡è¶³ç?| 100% | çº¦ææ£æ?|
| æ¶æç?| >99% | ä¼åæ¥å¿ |

---

## 7. åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-07 | **ç¶æ?*: Active

## 8. ææ¡£æ²»ç

### 8.1 ææ¡£ç´¢å¼

**æ¬ææ¡£å¨ç³»ç»ä¸­çä½ç½®**:
- **æå±å±çº?*: Layer 6 (ç»åä¼åå±?
- **æ¨¡åç´¢å¼**: 001
- **æ¨¡ååç§°**: MEAN_VARIANCE_OPTIMIZATION
- **ææ¡£è·¯å¾**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/

### 8.2 çæ¬ç®¡ç

**çæ¬åå²**:
- v1.0.0 (2026-04-07): åå§çæ¬

### 8.3 ç»´æ¤è´£ä»»

**ææ¡£ç»´æ¤**:
- **è´£ä»»æ¨¡å**: MEAN_VARIANCE_OPTIMIZATION
- **ç»´æ¤å¨æ**: æ¯å­£åº¦å®¡æ?
- **åæ´æµç¨**: æäº¤åæ´ç³è¯· â?ææ¯è¯å®?â?æ´æ°ææ¡£

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-07 | **ç¶æ?*: Active
