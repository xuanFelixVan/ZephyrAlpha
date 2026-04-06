---
module_id: INTERFACE_CONTRACT_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: é¦å¸­æ¶æå¸?standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: ä¸çº§æ¶é´æ¡æ¶æ¶æ
compliance_level: ä¸ä¸æ å
parent_document: PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
---

# ä¸çº§æ¶é´æ¡æ¶æ¥å£å¥çº¦èå¾

> **çæ¬**: v1.0
> **åå»ºæ¥æ**: 2026-04-02
> **ç®ç**: æç¡®ä¸çº§æ¶é´æ¡æ¶æ¶æçæ¨¡åé´æ¥å£å¥çº¦
> **æ ¸å¿ä»·å?*: ç¡®ä¿æ¨¡åé´éä¿¡çè§èæ§ãå¯é æ§åå¯ç»´æ¤æ?
---

## ð ä¸ãæ¥å£å¥çº¦æ»è§

### 1.1 æ¥å£å¥çº¦è®¾è®¡åå

| è®¾è®¡åå | å·ä½è¦æ± | éªè¯æ¹æ³ |
|---------|---------|---------|
| **æ¥å£åè¡** | åå®ä¹æ¥å?åå®ç°åè?| æ¥å£å®ä¹è¯å®¡ |
| **çæ¬ç®¡ç** | æææ¥å£é½æçæ¬å· | çæ¬å¼å®¹æ§æ£æ?|
| **ååå¼å®¹** | æ°çæ¬ä¸ç ´åæ§çæ?| å¼å®¹æ§æµè¯?|
| **éè¯¯å¤ç** | æææ¥å£é½æéè¯¯å¤ç?| éè¯¯åºæ¯æµè¯ |
| **ææ¡£å®æ´** | æææ¥å£é½æå®æ´ææ¡?| ææ¡£å®æ´æ§æ£æ?|

### 1.2 æ¥å£åç±»

| æ¥å£ç±»å | æ¥å£æ°é | ä¸»è¦ç¨é?| åè®®ç±»å |
|---------|---------|---------|---------|
| **å±åæ¥å£** | 15+ | åä¸å±çº§æ¨¡åé´éä¿¡ | å½æ°è°ç¨/æ¶æ¯éå |
| **è·¨å±æ¥å£** | 8+ | è·¨å±çº§æ°æ®ä¼ é?| API/æ¶æ¯éå |
| **å¤é¨æ¥å£** | 5+ | ä¸å¤é¨ç³»ç»äº¤äº?| REST API/æ°æ®åº?|

---

## ð¯ äºãå®è§éç½®å±æ¥å£å¥çº¦

### 2.1 ç»æµèå¼å¤æ­å¼ææ¥å£

#### 2.1.1 æ¥å£å®ä¹

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

@dataclass
class MacroDataInput:
    """å®è§æ°æ®è¾å¥"""
    gdp_growth: float                    # GDPå¢é¿ç?    cpi: float                           # CPI
    ppi: float                           # PPI
    pmi: float                           # PMI
    m2_growth: float                     # M2å¢é?    interest_rate: float                 # å©ç
    credit_spread: float                 # ä¿¡ç¨å©å·®
    timestamp: datetime                  # æ¶é´æ?
@dataclass
class RegimeOutput:
    """ç»æµèå¼è¾åº"""
    dominant_regime: str                 # ä¸»å¯¼èå¼ (expansion/stagflation/recession/recovery)
    probabilities: Dict[str, float]      # åèå¼æ¦ç?    confidence: float                    # ç½®ä¿¡åº?    transition_probability: Dict[str, float]  # èå¼è½¬æ¢æ¦ç
    recommended_assets: List[str]        # æ¨èèµäº§
    timestamp: datetime                  # æ¶é´æ?
class IEconomicRegimeEngine(ABC):
    """ç»æµèå¼å¤æ­å¼ææ¥å£"""
    
    @abstractmethod
    def analyze_regime(self, macro_data: MacroDataInput) -> RegimeOutput:
        """åæç»æµèå¼
        
        Args:
            macro_data: å®è§æ°æ®è¾å¥
            
        Returns:
            RegimeOutput: ç»æµèå¼è¾åº
            
        Raises:
            DataValidationError: æ°æ®éªè¯å¤±è´¥
            ModelInferenceError: æ¨¡åæ¨çå¤±è´¥
        """
        pass
    
    @abstractmethod
    def predict_transition(self, current_regime: str, 
                          horizon_days: int = 90) -> Dict[str, float]:
        """é¢æµèå¼è½¬æ¢
        
        Args:
            current_regime: å½åèå¼
            horizon_days: é¢æµæ¶é´èå´(å¤?
            
        Returns:
            Dict[str, float]: åèå¼è½¬æ¢æ¦ç?            
        Raises:
            InvalidRegimeError: æ æèå¼
            PredictionError: é¢æµå¤±è´¥
        """
        pass
    
    @abstractmethod
    def get_regime_history(self, start_date: datetime, 
                          end_date: datetime) -> pd.DataFrame:
        """è·åèå¼åå²
        
        Args:
            start_date: å¼å§æ¥æ?            end_date: ç»ææ¥æ
            
        Returns:
            pd.DataFrame: èå¼åå²æ°æ®
            
        Raises:
            DateRangeError: æ¥æèå´éè¯¯
        """
        pass
```

#### 2.1.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **è¾å¥éªè¯** | ææè¾å¥åæ°å¿é¡»ç»è¿éªè¯?| ååæµè¯ |
| **è¾åºä¿è¯** | è¾åºå¿é¡»åå«ææå¿éå­æ®µ | éææµè¯ |
| **éè¯¯å¤ç** | ææå¼å¸¸é½å¿é¡»è¢«æè·åå¤ç | å¼å¸¸æµè¯ |
| **æ§è½ä¿è¯** | æ¨çæ¶é´ â?1ç§?| æ§è½æµè¯ |
| **åç¡®çä¿è¯?* | èå¼è¯å«åç¡®ç?â?75% | åæµéªè¯ |

### 2.2 å¨å¤©åéç½®ä¼åå¨æ¥å£

#### 2.2.1 æ¥å£å®ä¹

```python
@dataclass
class AllocationInput:
    """èµäº§éç½®è¾å¥"""
    regime_output: RegimeOutput          # ç»æµèå¼è¾åº
    current_weights: Dict[str, float]    # å½åæé
    risk_budget: Dict[str, float]        # é£é©é¢ç®
    constraints: Dict[str, any]          # çº¦ææ¡ä»¶

@dataclass
class AllocationOutput:
    """èµäº§éç½®è¾åº"""
    target_weights: Dict[str, float]     # ç®æ æé
    expected_return: float               # é¢ææ¶ç
    expected_risk: float                 # é¢æé£é©
    risk_contributions: Dict[str, float] # é£é©è´¡ç®
    rebalance_trigger: bool              # è°ä»è§¦å
    timestamp: datetime                  # æ¶é´æ?
class IAllWeatherOptimizer(ABC):
    """å¨å¤©åéç½®ä¼åå¨æ¥å£"""
    
    @abstractmethod
    def optimize_allocation(self, allocation_input: AllocationInput) -> AllocationOutput:
        """ä¼åèµäº§éç½®
        
        Args:
            allocation_input: èµäº§éç½®è¾å¥
            
        Returns:
            AllocationOutput: èµäº§éç½®è¾åº
            
        Raises:
            OptimizationError: ä¼åå¤±è´¥
            ConstraintViolationError: çº¦æè¿å
        """
        pass
    
    @abstractmethod
    def check_rebalance_trigger(self, current_weights: Dict[str, float],
                               target_weights: Dict[str, float],
                               threshold: float = 0.05) -> bool:
        """æ£æ¥è°ä»è§¦å?        
        Args:
            current_weights: å½åæé
            target_weights: ç®æ æé
            threshold: è§¦åéå?            
        Returns:
            bool: æ¯å¦è§¦åè°ä»
        """
        pass
```

#### 2.2.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **æéå½ä¸å?* | æææéä¹å?= 1.0 | æ°å­¦éªè¯ |
| **é£é©é¢ç®çº¦æ** | é£é©è´¡ç®ç¬¦åé¢ç® | é£é©æ£æ?|
| **çº¦ææ»¡è¶³** | ææçº¦ææ¡ä»¶é½æ»¡è¶³ | çº¦æéªè¯ |
| **ä¼åæ¶æ** | ä¼åç®æ³å¿é¡»æ¶æ | ä¼åæµè¯ |
| **æ§è½ä¿è¯** | ä¼åæ¶é´ â?10ç§?| æ§è½æµè¯ |

---

## ð§  ä¸ãä¸­è§ç­ç¥å±æ¥å£å¥çº¦

### 3.1 å¸åºç¶æè¯å«ç³»ç»æ¥å?
#### 3.1.1 æ¥å£å®ä¹

```python
@dataclass
class MarketDataInput:
    """å¸åºæ°æ®è¾å¥"""
    price_data: pd.DataFrame             # ä»·æ ¼æ°æ®
    volume_data: pd.DataFrame            # æäº¤éæ°æ?    technical_indicators: Dict[str, pd.Series]  # ææ¯ææ ?    timestamp: datetime                  # æ¶é´æ?
@dataclass
class MarketStateOutput:
    """å¸åºç¶æè¾å?""
    market_regime: str                   # å¸åºç¶æ?(bull/bear/sideways/volatile)
    trend_strength: float                # è¶å¿å¼ºåº¦
    volatility_level: float              # æ³¢å¨çæ°´å¹?    liquidity_score: float               # æµå¨æ§è¯å?    recommended_strategies: List[str]    # æ¨èç­ç¥
    timestamp: datetime                  # æ¶é´æ?
class IMarketRegimeSystem(ABC):
    """å¸åºç¶æè¯å«ç³»ç»æ¥å?""
    
    @abstractmethod
    def identify_regime(self, market_data: MarketDataInput) -> MarketStateOutput:
        """è¯å«å¸åºç¶æ?        
        Args:
            market_data: å¸åºæ°æ®è¾å¥
            
        Returns:
            MarketStateOutput: å¸åºç¶æè¾å?            
        Raises:
            DataInsufficientError: æ°æ®ä¸è¶³
            ModelInferenceError: æ¨¡åæ¨çå¤±è´¥
        """
        pass
    
    @abstractmethod
    def get_regime_probability(self, regime: str) -> float:
        """è·åç¶ææ¦ç?        
        Args:
            regime: å¸åºç¶æ?            
        Returns:
            float: ç¶ææ¦ç?        """
        pass
```

#### 3.1.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **ç¶æè¯å«åç¡®ç** | â?70% | åæµéªè¯ |
| **å®æ¶æ§ä¿è¯?* | è¯å«æ¶é´ â?1ç§?| æ§è½æµè¯ |
| **ç¶æä¸è´æ?* | è¿ç»­ç¶æè¯å«ä¸è´æ?â?80% | ä¸è´æ§æµè¯?|
| **æ¨èç­ç¥æææ?* | æ¨èç­ç¥å¤æ®æ¯ç â?1.5 | ç­ç¥éªè¯ |

### 3.2 Alphaå å­å·¥åæ¥å£

#### 3.2.1 æ¥å£å®ä¹

```python
@dataclass
class FactorInput:
    """å å­è¾å¥"""
    stock_data: pd.DataFrame             # è¡ç¥¨æ°æ®
    financial_data: pd.DataFrame         # è´¢å¡æ°æ®
    market_data: pd.DataFrame            # å¸åºæ°æ®
    timestamp: datetime                  # æ¶é´æ?
@dataclass
class FactorOutput:
    """å å­è¾åº"""
    factor_values: pd.DataFrame          # å å­å?    factor_ic: Dict[str, float]          # å å­IC
    factor_correlation: pd.DataFrame     # å å­ç¸å³æ?    selected_factors: List[str]          # ç­éåçå å­?    timestamp: datetime                  # æ¶é´æ?
class IAlphaFactorFactory(ABC):
    """Alphaå å­å·¥åæ¥å£"""
    
    @abstractmethod
    def calculate_factors(self, factor_input: FactorInput) -> FactorOutput:
        """è®¡ç®å å­
        
        Args:
            factor_input: å å­è¾å¥
            
        Returns:
            FactorOutput: å å­è¾åº
            
        Raises:
            DataValidationError: æ°æ®éªè¯å¤±è´¥
            FactorCalculationError: å å­è®¡ç®å¤±è´¥
        """
        pass
    
    @abstractmethod
    def filter_factors(self, factor_output: FactorOutput,
                      ic_threshold: float = 0.03) -> List[str]:
        """ç­éå å­?        
        Args:
            factor_output: å å­è¾åº
            ic_threshold: ICéå?            
        Returns:
            List[str]: ç­éåçå å­åè¡?        """
        pass
    
    @abstractmethod
    def synthesize_factors(self, factor_values: pd.DataFrame,
                          weights: Optional[Dict[str, float]] = None) -> pd.Series:
        """åæå å­
        
        Args:
            factor_values: å å­å?            weights: å å­æé(å¯é?
            
        Returns:
            pd.Series: åæå å­
        """
        pass
```

#### 3.2.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **å å­è¦çåº?* | â?95%è¡ç¥¨æå å­å?| è¦çåº¦æ£æ?|
| **å å­æææ?* | ICåå?â?0.03 | ICæ£éª?|
| **å å­æ­£äº¤æ?* | å å­ç¸å³æ?â?0.5 | ç¸å³æ§æ£æ?|
| **è®¡ç®æ§è½** | å å­è®¡ç®æ¶é´ â?30ç§?| æ§è½æµè¯ |

### 3.3 æ¥çº¿ç»åä¼åå¨æ¥å?
#### 3.3.1 æ¥å£å®ä¹

```python
@dataclass
class PortfolioInput:
    """ç»åè¾å¥"""
    alpha_signals: pd.Series             # Alphaä¿¡å·
    risk_model: Dict[str, any]           # é£é©æ¨¡å
    constraints: Dict[str, any]          # çº¦ææ¡ä»¶
    current_portfolio: Dict[str, float]  # å½åç»å

@dataclass
class PortfolioOutput:
    """ç»åè¾åº"""
    target_weights: Dict[str, float]     # ç®æ æé
    expected_return: float               # é¢ææ¶ç
    expected_risk: float                 # é¢æé£é©
    turnover: float                      # æ¢æç?    timestamp: datetime                  # æ¶é´æ?
class IDailyPortfolioOptimizer(ABC):
    """æ¥çº¿ç»åä¼åå¨æ¥å?""
    
    @abstractmethod
    def optimize_portfolio(self, portfolio_input: PortfolioInput) -> PortfolioOutput:
        """ä¼åç»å
        
        Args:
            portfolio_input: ç»åè¾å¥
            
        Returns:
            PortfolioOutput: ç»åè¾åº
            
        Raises:
            OptimizationError: ä¼åå¤±è´¥
            InfeasibleError: ä¸å¯è¡?        """
        pass
    
    @abstractmethod
    def apply_constraints(self, weights: Dict[str, float],
                        constraints: Dict[str, any]) -> Dict[str, float]:
        """åºç¨çº¦æ
        
        Args:
            weights: æé
            constraints: çº¦ææ¡ä»¶
            
        Returns:
            Dict[str, float]: çº¦æåçæé
        """
        pass
```

#### 3.3.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **æéå½ä¸å?* | æææéä¹å?= 1.0 | æ°å­¦éªè¯ |
| **çº¦ææ»¡è¶³** | ææçº¦ææ¡ä»¶é½æ»¡è¶³ | çº¦æéªè¯ |
| **æ¢æçæ§å?* | æ¢æç?â?è®¾å®ä¸é | æ¢æçæ£æ?|
| **ä¼åæ§è½** | ä¼åæ¶é´ â?5ç§?| æ§è½æµè¯ |

---

## â?åãå¾®è§æ§è¡å±æ¥å£å¥çº¦

### 4.1 åéæ§è¡ä¼åå¨æ¥å?
#### 4.1.1 æ¥å£å®ä¹

```python
@dataclass
class ExecutionInput:
    """æ§è¡è¾å¥"""
    target_portfolio: Dict[str, float]    # ç®æ ç»å
    current_portfolio: Dict[str, float]   # å½åç»å
    market_data: pd.DataFrame             # å¸åºæ°æ®
    execution_constraints: Dict[str, any] # æ§è¡çº¦æ

@dataclass
class ExecutionPlan:
    """æ§è¡è®¡å"""
    orders: List[Dict[str, any]]          # è®¢ååè¡¨
    execution_schedule: Dict[str, any]    # æ§è¡æ¶é´è¡?    algorithm_selection: Dict[str, str]   # ç®æ³éæ©
    expected_cost: float                  # é¢æææ¬
    timestamp: datetime                   # æ¶é´æ?
class IMinuteExecutionOptimizer(ABC):
    """åéæ§è¡ä¼åå¨æ¥å?""
    
    @abstractmethod
    def generate_execution_plan(self, execution_input: ExecutionInput) -> ExecutionPlan:
        """çææ§è¡è®¡å
        
        Args:
            execution_input: æ§è¡è¾å¥
            
        Returns:
            ExecutionPlan: æ§è¡è®¡å
            
        Raises:
            ExecutionError: æ§è¡å¤±è´¥
        """
        pass
    
    @abstractmethod
    def select_algorithm(self, order: Dict[str, any],
                        market_condition: Dict[str, any]) -> str:
        """éæ©æ§è¡ç®æ³
        
        Args:
            order: è®¢å
            market_condition: å¸åºæ¡ä»¶
            
        Returns:
            str: ç®æ³åç§° (VWAP/TWAP/IS/POV)
        """
        pass
```

#### 4.1.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **æ§è¡å®æç?* | â?99% | æ§è¡éªè¯ |
| **ææ¬æ§å¶** | æ§è¡ææ¬ â?é¢æææ¬Ã1.2 | ææ¬åæ |
| **æ§è¡æ¶é´** | â?è®¾å®æ¶é´çªå£ | æ¶é´æ£æ?|
| **ç®æ³éç¨æ?* | ç®æ³éæ©åç¡®ç?â?80% | ç®æ³éªè¯ |

### 4.2 æºè½æ§è¡ç®æ³åºæ¥å?
#### 4.2.1 æ¥å£å®ä¹

```python
@dataclass
class AlgorithmInput:
    """ç®æ³è¾å¥"""
    order: Dict[str, any]                 # è®¢å
    market_data: pd.DataFrame             # å¸åºæ°æ®
    algorithm_params: Dict[str, any]      # ç®æ³åæ°

@dataclass
class AlgorithmOutput:
    """ç®æ³è¾åº"""
    child_orders: List[Dict[str, any]]    # å­è®¢å?    execution_progress: float             # æ§è¡è¿åº¦
    market_impact: float                  # å¸åºå²å»
    timestamp: datetime                   # æ¶é´æ?
class ISmartExecutionAlgorithm(ABC):
    """æºè½æ§è¡ç®æ³æ¥å£"""
    
    @abstractmethod
    def execute(self, algorithm_input: AlgorithmInput) -> AlgorithmOutput:
        """æ§è¡ç®æ³
        
        Args:
            algorithm_input: ç®æ³è¾å¥
            
        Returns:
            AlgorithmOutput: ç®æ³è¾åº
            
        Raises:
            AlgorithmError: ç®æ³æ§è¡å¤±è´¥
        """
        pass
    
    @abstractmethod
    def estimate_market_impact(self, order: Dict[str, any]) -> float:
        """ä¼°ç®å¸åºå²å»
        
        Args:
            order: è®¢å
            
        Returns:
            float: å¸åºå²å»ææ¬
        """
        pass
```

#### 4.2.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **ç®æ³æ§è½** | æ§è¡ææ¬ä¼äºåºå â?5% | ææ¬æ¯è¾ |
| **å¸åºå²å»æ§å¶** | å¸åºå²å» â?é¢ä¼°å¼Ã?.5 | å²å»åæ |
| **æ§è¡ç¨³å®æ?* | æ§è¡æåç?â?99% | ç¨³å®æ§æµè¯?|
| **å®æ¶ååº** | ç®æ³ååºæ¶é´ â?100ms | æ§è½æµè¯ |

### 4.3 å®æ¶é£é©å¯¹å²å¼ææ¥å£

#### 4.3.1 æ¥å£å®ä¹

```python
@dataclass
class RiskHedgeInput:
    """é£é©å¯¹å²è¾å¥"""
    portfolio_risk: Dict[str, float]      # ç»åé£é©
    market_risk: Dict[str, float]         # å¸åºé£é©
    hedge_instruments: List[str]          # å¯¹å²å·¥å·
    hedge_ratio: float                    # å¯¹å²æ¯ä¾

@dataclass
class RiskHedgeOutput:
    """é£é©å¯¹å²è¾åº"""
    hedge_orders: List[Dict[str, any]]    # å¯¹å²è®¢å
    hedge_effectiveness: float            # å¯¹å²æææ?    remaining_risk: Dict[str, float]      # å©ä½é£é©
    timestamp: datetime                   # æ¶é´æ?
class IRealtimeRiskHedger(ABC):
    """å®æ¶é£é©å¯¹å²å¼ææ¥å£"""
    
    @abstractmethod
    def hedge_risk(self, hedge_input: RiskHedgeInput) -> RiskHedgeOutput:
        """å¯¹å²é£é©
        
        Args:
            hedge_input: å¯¹å²è¾å¥
            
        Returns:
            RiskHedgeOutput: å¯¹å²è¾åº
            
        Raises:
            HedgeError: å¯¹å²å¤±è´¥
        """
        pass
    
    @abstractmethod
    def calculate_hedge_ratio(self, portfolio_risk: Dict[str, float],
                             hedge_instrument: str) -> float:
        """è®¡ç®å¯¹å²æ¯ä¾
        
        Args:
            portfolio_risk: ç»åé£é©
            hedge_instrument: å¯¹å²å·¥å·
            
        Returns:
            float: å¯¹å²æ¯ä¾
        """
        pass
```

#### 4.3.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **å¯¹å²æææ?* | â?80% | æææ§éªè¯?|
| **å¯¹å²åæ¶æ?* | å¯¹å²ååºæ¶é´ â?1ç§?| æ§è½æµè¯ |
| **ææ¬æ§å¶** | å¯¹å²ææ¬ â?é¢ç® | ææ¬æ£æ?|
| **é£é©è¦ç** | å¯¹å²è¦ç â?90%é£é© | é£é©æ£æ?|

---

## ð äºãè·¨å±æ¥å£å¥çº?
### 5.1 å®è§âä¸­è§æ¥å£å¥çº?
#### 5.1.1 æ¥å£å®ä¹

```python
@dataclass
class MacroToTacticalInput:
    """å®è§âä¸­è§è¾å?""
    regime_context: RegimeOutput          # ç»æµèå¼
    strategic_constraints: AllocationOutput  # æç¥çº¦æ
    risk_limits: Dict[str, float]         # é£é©éé¢

@dataclass
class MacroToTacticalOutput:
    """å®è§âä¸­è§è¾å?""
    strategy_selection_context: Dict[str, any]  # ç­ç¥éæ©ä¸ä¸æ?    portfolio_constraints: Dict[str, any]       # ç»åçº¦æ
    risk_budget_allocation: Dict[str, float]    # é£é©é¢ç®åé

class IMacroToTacticalBridge(ABC):
    """å®è§âä¸­è§æ¡¥æ¥æ¥å?""
    
    @abstractmethod
    def transfer_context(self, macro_input: MacroToTacticalInput) -> MacroToTacticalOutput:
        """ä¼ éä¸ä¸æ
        
        Args:
            macro_input: å®è§å±è¾å?            
        Returns:
            MacroToTacticalOutput: ä¸­è§å±è¾å?        """
        pass
```

#### 5.1.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **ä¸ä¸æå®æ´æ?* | ææå¿éä¸ä¸æé½ä¼ é?| å®æ´æ§æ£æ?|
| **çº¦æä¸è´æ?* | çº¦ææ¡ä»¶ä¸å®è§å±ä¸è?| ä¸è´æ§éªè¯?|
| **ä¼ éåæ¶æ?* | ä¼ éå»¶è¿?â?1åé | æ§è½æµè¯ |

### 5.2 ä¸­è§âå¾®è§æ¥å£å¥çº?
#### 5.2.1 æ¥å£å®ä¹

```python
@dataclass
class TacticalToExecutionInput:
    """ä¸­è§âå¾®è§è¾å?""
    execution_targets: PortfolioOutput    # æ§è¡ç®æ 
    execution_priority: pd.Series         # æ§è¡ä¼åçº?    hedge_requirements: Dict[str, any]    # å¯¹å²éæ±?
@dataclass
class TacticalToExecutionOutput:
    """ä¸­è§âå¾®è§è¾å?""
    execution_plan: ExecutionPlan         # æ§è¡è®¡å
    hedge_plan: RiskHedgeOutput           # å¯¹å²è®¡å
    execution_monitoring: Dict[str, any]  # æ§è¡çæ§

class ITacticalToExecutionBridge(ABC):
    """ä¸­è§âå¾®è§æ¡¥æ¥æ¥å?""
    
    @abstractmethod
    def transfer_targets(self, tactical_input: TacticalToExecutionInput) -> TacticalToExecutionOutput:
        """ä¼ éç®æ ?        
        Args:
            tactical_input: ä¸­è§å±è¾å?            
        Returns:
            TacticalToExecutionOutput: å¾®è§å±è¾å?        """
        pass
```

#### 5.2.2 æ¥å£å¥çº¦

| å¥çº¦é¡?| å¥çº¦åå®¹ | éªè¯æ¹æ³ |
|--------|---------|---------|
| **ç®æ ä¸è´æ?* | æ§è¡ç®æ ä¸ç»åæéä¸è?| ä¸è´æ§éªè¯?|
| **ä¼åçº§æç¡?* | æ§è¡ä¼åçº§æç¡?| ä¼åçº§æ£æ?|
| **ä¼ éå®æ¶æ?* | ä¼ éå»¶è¿?â?10ç§?| æ§è½æµè¯ |

---

## ð å­ãæ¥å£çæ¬ç®¡ç?
### 6.1 çæ¬å½åè§è

```
çæ¬æ ¼å¼: v{MAJOR}.{MINOR}.{PATCH}

MAJOR: éå¤§åæ´(ä¸å¼å®¹æ§çæ¬)
MINOR: åè½æ°å¢(å¼å®¹æ§çæ?
PATCH: é®é¢ä¿®å¤(å¼å®¹æ§çæ?

ç¤ºä¾:
v1.0.0 â?åå§çæ¬
v1.1.0 â?æ°å¢åè½
v1.1.1 â?é®é¢ä¿®å¤
v2.0.0 â?éå¤§åæ´
```

### 6.2 çæ¬å¼å®¹æ§ç­ç?
| åæ´ç±»å | çæ¬åçº§ | å¼å®¹æ?| è¿ç§»ç­ç¥ |
|---------|---------|--------|---------|
| **æ°å¢æ¥å£** | MINOR | ååå¼å®¹ | æ éè¿ç§» |
| **æ°å¢åæ°(å¯é?** | MINOR | ååå¼å®¹ | æ éè¿ç§» |
| **æ°å¢åæ°(å¿é)** | MAJOR | ä¸å¼å®?| å¿é¡»è¿ç§» |
| **å é¤æ¥å£** | MAJOR | ä¸å¼å®?| å¿é¡»è¿ç§» |
| **ä¿®æ¹æ¥å£ç­¾å** | MAJOR | ä¸å¼å®?| å¿é¡»è¿ç§» |
| **é®é¢ä¿®å¤** | PATCH | ååå¼å®¹ | æ éè¿ç§» |

---

## ð¯ ä¸ãæ»ç»

### 7.1 æ ¸å¿ä»·å?
éè¿æç¡®ä¸çº§æ¶é´æ¡æ¶çæ¥å£å¥çº?æä»¬å®ç°äº?

1. **æ¥å£è§èå?*: æææ¨¡åé´éä¿¡é½ææç¡®çæ¥å£å®ä¹?2. **å¥çº¦æç¡®å?*: æ¯ä¸ªæ¥å£é½ææç¡®çå¥çº¦åéªè¯æ¹æ³
3. **çæ¬ç®¡ç**: æææ¥å£é½æçæ¬ç®¡çæºå?4. **è´¨éä¿è¯**: æ¥å£è´¨éææç¡®çéªè¯æ å

### 7.2 å®æ½å»ºè®®

1. **Phase 1**: å®æ½å®è§éç½®å±æ¥å£å¥çº?2. **Phase 2**: å®æ½ä¸­è§ç­ç¥å±æ¥å£å¥çº?3. **Phase 3**: å®æ½å¾®è§æ§è¡å±æ¥å£å¥çº?4. **Phase 4**: å®æ½è·¨å±æ¥å£å¥çº¦
5. **Phase 5**: å»ºç«æ¥å£çæ¬ç®¡çæºå¶

---

**çæ¬**: v1.0 | **åå»ºæ¥æ**: 2026-04-02 | **ç¶æ?*: â?æ­£å¼åå¸
