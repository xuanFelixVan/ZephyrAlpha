---
responsibility:
  - VaR/ESè®¡ç®
  - é£é©çæ§
  - é£é©é¢è­¦
  - é£é©åº¦é

module_id: VAR_ES_MONITORING_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 7 é£é©ç®¡çå±?
compliance_level: ä¸ä¸æ å
layer: Layer 5.3 (风险管理)
---

# VaR/ESå®æ¶çæ§èå¾

> **æ ¸å¿èè´£**: å®æ¶çæ§ç»åçVaRåESé£é©ææ 
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼VaR/ESè®¡ç®ãå®æ¶çæ§ãåæµéªè¯?
> - â?æ¬ææ¡£ä¸è´è´£ï¼å å­è®¡ç®ï¼ç±å å­æ¨¡åè´è´£ï¼


## æ ¸å¿å®ä½

å»ºç«VAR ES MONITORINGçè®¾è®¡ä¸å®ç°ï¼åºäºELK Stackææ¯ï¼åè­¦æ ¸å¿åè½ï¼é¢é²ç³»ç»æéã?

## 1. æ¦è¿°

### 1.1 æ¨¡åå®ä½

**Layerå®ä½**: Layer 6 - ç»åä¼åå±ï¼é£é©ç®¡çæ¨¡åï¼?

**æ ¸å¿ä»·å?*:
- å®æ¶çæ§æèµç»åçVaRï¼é£é©ä»·å¼ï¼åESï¼é¢æ?shortfallï¼ææ ?
- æ¯æåå²æ¨¡ææ³ãåæ°æ³ãèç¹å¡æ´æ¨¡æç­å¤ç§è®¡ç®æ¹æ³
- æä¾å®æ´çåæµéªè¯åè?
- ä¸ä¸æºæé£é©ç®¡ççæ ¸å¿ææ ?

**ä¸å¡ä»·å?*:
- éåæèµç»åçä¸è¡é£é?
- è®¾ç½®é£é©é¢è­¦éå?
- æ»¡è¶³åè§çç®¡è¦æ±
- æ¯æé£é©é¢ç®ç®¡ç

### 1.2 çæ¬ä¿¡æ¯

| é¡¹ç® | åå®¹ |
|------|------|
| **æ¨¡åID** | VAR_ES_MONITORING_001 |
| **çæ¬** | v1.0.0 |
| **ç¶æ?* | Active |
| **åå»ºæ¥æ** | 2026-04-06 |
| **å¼æºä¾èµ?* | pyRisk, arch, pyfolio |
| **é¢è®¡å·¥æ¶** | 5-7å¤?|

---
## ð ç¸å³ææ¡£

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [ç»åä¼åå¼æéæèå¾](./PORTFOLIO_OPTIMIZER_INTEGRATION_BLUEPRINT.md) | PORTFOLIO_OPTIMIZER_INTEGRATION_001 | å¼ºä¾èµ?| æä¾ç»åæéæ°æ® |
| [ç»åææ¯åæèå¾](./PORTFOLIO_SCENARIO_ANALYSIS_BLUEPRINT.md) | PORTFOLIO_SCENARIO_ANALYSIS_001 | å¼ºä¾èµ?| æä¾ææ¯åæç»æ |
| [æ°æ®è´¨éçæ§èå¾](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | DATA_QUALITY_MONITORING_001 | å¼ºä¾èµ?| æä¾æ°æ®è´¨éææ  |

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md](./RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md) | RISK_CONTRIBUTION_ANALYSIS_001 | å¼ºä¾èµ?| é£é©è´¡ç®åæ |
| [PORTFOLIO_PERFORMANCE_EVALUATION_BLUEPRINT.md](./PORTFOLIO_PERFORMANCE_EVALUATION_BLUEPRINT.md) | PORTFOLIO_PERFORMANCE_EVALUATION_001 | å¼ºä¾èµ?| ç»åç»©æè¯ä¼° |
| [STRESS_TESTING_SYSTEM_BLUEPRINT.md](./STRESS_TESTING_SYSTEM_BLUEPRINT.md) | STRESS_TESTING_SYSTEM_001 | ä¸­ä¾èµ?| ååæµè¯ç³»ç» |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **pyRisk** | 1.0+ | é£é©ææ è®¡ç® | [GitHub](https://github.com/quantopian/pyfolio) |
| **arch** | 5.0+ | æ³¢å¨çæ¨¡å?| [å®æ¹ææ¡£](https://arch.readthedocs.io/) |
| **pyfolio** | 0.9+ | ç»ååæ | [GitHub](https://github.com/quantopian/pyfolio) |
| **NumPy** | 1.24+ | æ°å¼è®¡ç®?| [å®æ¹ææ¡£](https://numpy.org/) |

### å¼ç¨å³ç³»å?

```mermaid
graph LR
    A[ç»åä¼åå¼æ] --> B[VaR/ESçæ§]
    C[ç»åææ¯åæ] --> B
    D[æ°æ®è´¨éçæ§] --> B
    
    B --> E[é£é©è´¡ç®åæ]
    B --> F[ç»åç»©æè¯ä¼°]
    B --> G[ååæµè¯ç³»ç»]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
```

---

## 2. æ¶æè®¾è®¡

### 2.1 æ ¸å¿ç»ä»¶

```mermaid
graph TB
    subgraph "æ°æ®è¾å¥"
        A[ç»åæä»] --> D[VaR/ESè®¡ç®å¨]
        B[æ¶ççåºå] --> D
        C[å¸åºæ°æ®] --> D
    end
    
    subgraph "è®¡ç®æ¹æ³"
        D --> E[åå²æ¨¡ææ³]
        D --> F[åæ°æ³]
        D --> G[èç¹å¡æ´æ³]
        D --> H[æå¼çè®ºæ³]
    end
    
    subgraph "çæ§å±?
        I[é£é©éå¼æ£æ¥]
        J[é¢è­¦ä¿¡å·çæ]
        K[åæµéªè¯]
    end
    
    subgraph "è¾åº"
        L[å®æ¶çæ§é¢æ¿]
        M[é£é©æ¥å]
        N[åå²è®°å½]
    end
    
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J
    J --> L
    J --> M
    K --> N
```

---

## 3. ææ¯å®ç?

### 3.1 æ ¸å¿API

```python
from dataclasses import dataclass
from typing import Optional, List, Dict
import numpy as np
import pandas as pd

class VaRESCalculator:
    """VaR/ESè®¡ç®å?""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
        
    def historical_var(
        self,
        returns: np.ndarray,
        confidence: float = 0.95
    ) -> float:
        """åå²æ¨¡ææ³VaR"""
        return -np.percentile(returns, (1 - confidence) * 100)
    
    def parametric_var(
        self,
        returns: np.ndarray,
        confidence: float = 0.95
    ) -> float:
        """åæ°æ³VaR (æ­£æåå¸?"""
        mu = np.mean(returns)
        sigma = np.std(returns)
        z = stats.norm.ppf(1 - confidence)
        return -(mu + z * sigma)
    
    def historical_es(
        self,
        returns: np.ndarray,
        confidence: float = 0.95
    ) -> float:
        """åå²æ¨¡ææ³ES"""
        var = -self.historical_var(returns, confidence)
        tail_returns = returns[returns <= -var]
        return -np.mean(tail_returns) if len(tail_returns) > 0 else var
    
    def parametric_es(
        self,
        returns: np.ndarray,
        confidence: float = 0.95
    ) -> float:
        """åæ°æ³ES"""
        mu = np.mean(returns)
        sigma = np.std(returns)
        z = stats.norm.ppf(1 - confidence)
        es = -(mu - sigma * stats.norm.pdf(z) / (1 - confidence))
        return es
```

### 3.2 æ§è½è¦æ±

| ææ  | ç®æ å?|
|------|--------|
| è®¡ç®æ¶é´ | <100ms |
| åå­å ç¨ | <50MB |
| å®æ¶æ´æ°é¢ç | 1åé |
| æ¯æèµäº§æ?| 1000+ |

---

## 4. VaR/ESè®¡ç®æ¹æ³è¯¦è§£

### 4.1 åå²æ¨¡ææ³?(Historical Simulation)

**åç**: ä½¿ç¨åå²æ¶ççåå¸ç´æ¥ä¼°è®¡VaRåES

**ä¼ç¹**:
- æ éåè®¾æ¶ççåå¸?
- ææè¥å°¾ç¹å¾
- å®ç°ç®åç´è§?

**ç¼ºç¹**:
- ä¾èµåå²æ°æ®è´¨é
- æ æ³é¢æµæç«¯äºä»¶
- æ ·æ¬éè¦æ±é«

```python
class HistoricalVaR:
    """åå²æ¨¡ææ³VaRè®¡ç®å?""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
    
    def calculate_var(
        self,
        returns: np.ndarray,
        portfolio_value: float
    ) -> Tuple[float, float]:
        """
        è®¡ç®åå²æ¨¡æVaR
        
        åæ°:
            returns: åå²æ¶ççåºå?
            portfolio_value: ç»åä»·å?
            
        è¿å:
            (VaRéé¢, VaRç¾åæ¯?
        """
        var_percentile = np.percentile(
            returns, 
            (1 - self.confidence_level) * 100
        )
        var_value = -var_percentile * portfolio_value
        
        return var_value, -var_percentile
    
    def calculate_es(
        self,
        returns: np.ndarray,
        portfolio_value: float
    ) -> Tuple[float, float]:
        """
        è®¡ç®åå²æ¨¡æES (Expected Shortfall)
        
        åæ°:
            returns: åå²æ¶ççåºå?
            portfolio_value: ç»åä»·å?
            
        è¿å:
            (ESéé¢, ESç¾åæ¯?
        """
        var_percentile = np.percentile(
            returns,
            (1 - self.confidence_level) * 100
        )
        
        tail_returns = returns[returns <= var_percentile]
        
        if len(tail_returns) == 0:
            es_percentile = var_percentile
        else:
            es_percentile = np.mean(tail_returns)
        
        es_value = -es_percentile * portfolio_value
        
        return es_value, -es_percentile
```

### 4.2 åæ°æ³?(Parametric Method)

**åç**: åè®¾æ¶ççæä»ç¹å®åå¸ï¼éå¸¸ä¸ºæ­£æåå¸ï¼ï¼ä½¿ç¨åæ°ä¼°è®?

**ä¼ç¹**:
- è®¡ç®æçé«?
- æ°å­¦æ¨å¯¼æ¸æ°
- æäºæ©å±å°å¤èµäº§

**ç¼ºç¹**:
- åå¸åè®¾å¯è½ä¸æç«?
- æ æ³ææè¥å°¾ç¹å¾
- å¯¹æç«¯äºä»¶ä¼°è®¡ä¸è¶?

```python
class ParametricVaR:
    """åæ°æ³VaRè®¡ç®å?""
    
    def __init__(
        self,
        confidence_level: float = 0.95,
        distribution: str = "normal"
    ):
        self.confidence_level = confidence_level
        self.distribution = distribution
    
    def calculate_var(
        self,
        returns: np.ndarray,
        portfolio_value: float
    ) -> Tuple[float, float]:
        """
        è®¡ç®åæ°æ³VaR
        
        åæ°:
            returns: æ¶ççåºå?
            portfolio_value: ç»åä»·å?
            
        è¿å:
            (VaRéé¢, VaRç¾åæ¯?
        """
        mu = np.mean(returns)
        sigma = np.std(returns, ddof=1)
        
        if self.distribution == "normal":
            z_score = stats.norm.ppf(self.confidence_level)
        elif self.distribution == "t":
            df = self._estimate_degrees_of_freedom(returns)
            z_score = stats.t.ppf(self.confidence_level, df)
        
        var_percentile = mu - z_score * sigma
        var_value = -var_percentile * portfolio_value
        
        return var_value, -var_percentile
    
    def calculate_es(
        self,
        returns: np.ndarray,
        portfolio_value: float
    ) -> Tuple[float, float]:
        """
        è®¡ç®åæ°æ³ES
        
        åæ°:
            returns: æ¶ççåºå?
            portfolio_value: ç»åä»·å?
            
        è¿å:
            (ESéé¢, ESç¾åæ¯?
        """
        mu = np.mean(returns)
        sigma = np.std(returns, ddof=1)
        
        if self.distribution == "normal":
            z_score = stats.norm.ppf(self.confidence_level)
            es_percentile = mu - sigma * stats.norm.pdf(z_score) / (1 - self.confidence_level)
        elif self.distribution == "t":
            df = self._estimate_degrees_of_freedom(returns)
            z_score = stats.t.ppf(self.confidence_level, df)
            es_percentile = mu - sigma * (df + z_score**2) / (df - 1) * \
                           stats.t.pdf(z_score, df) / (1 - self.confidence_level)
        
        es_value = -es_percentile * portfolio_value
        
        return es_value, -es_percentile
    
    def _estimate_degrees_of_freedom(
        self,
        returns: np.ndarray
    ) -> int:
        """ä¼°è®¡tåå¸èªç±åº?""
        kurtosis = stats.kurtosis(returns)
        if kurtosis <= 0:
            return 30
        df = int(6 / kurtosis + 4)
        return max(3, min(df, 30))
```

### 4.3 èç¹å¡æ´æ¨¡ææ³?(Monte Carlo Simulation)

**åç**: éè¿éæºæ¨¡æçæå¤§éææ¯ï¼ä¼°è®¡VaRåES

**ä¼ç¹**:
- çµæ´»æ§é«
- å¯å¤çå¤æåå¸?
- å¯çº³å¥éçº¿æ§å³ç³?

**ç¼ºç¹**:
- è®¡ç®éå¤§
- ä¾èµæ¨¡ååè®¾
- éè¦å¤§éæ¨¡ææ¬¡æ?

```python
class MonteCarloVaR:
    """èç¹å¡æ´æ¨¡æVaRè®¡ç®å?""
    
    def __init__(
        self,
        confidence_level: float = 0.95,
        n_simulations: int = 10000,
        distribution: str = "student_t"
    ):
        self.confidence_level = confidence_level
        self.n_simulations = n_simulations
        self.distribution = distribution
    
    def calculate_var(
        self,
        returns: pd.DataFrame,
        weights: np.ndarray,
        portfolio_value: float
    ) -> Tuple[float, float]:
        """
        è®¡ç®èç¹å¡æ´VaR
        
        åæ°:
            returns: èµäº§æ¶ççDataFrame
            weights: ç»åæé
            portfolio_value: ç»åä»·å?
            
        è¿å:
            (VaRéé¢, VaRç¾åæ¯?
        """
        mean_returns = returns.mean().values
        cov_matrix = returns.cov().values
        
        simulated_returns = self._simulate_returns(mean_returns, cov_matrix)
        
        portfolio_returns = simulated_returns @ weights
        
        var_percentile = np.percentile(
            portfolio_returns,
            (1 - self.confidence_level) * 100
        )
        var_value = -var_percentile * portfolio_value
        
        return var_value, -var_percentile
    
    def calculate_es(
        self,
        returns: pd.DataFrame,
        weights: np.ndarray,
        portfolio_value: float
    ) -> Tuple[float, float]:
        """
        è®¡ç®èç¹å¡æ´ES
        
        åæ°:
            returns: èµäº§æ¶ççDataFrame
            weights: ç»åæé
            portfolio_value: ç»åä»·å?
            
        è¿å:
            (ESéé¢, ESç¾åæ¯?
        """
        mean_returns = returns.mean().values
        cov_matrix = returns.cov().values
        
        simulated_returns = self._simulate_returns(mean_returns, cov_matrix)
        
        portfolio_returns = simulated_returns @ weights
        
        var_percentile = np.percentile(
            portfolio_returns,
            (1 - self.confidence_level) * 100
        )
        
        tail_returns = portfolio_returns[portfolio_returns <= var_percentile]
        es_percentile = np.mean(tail_returns) if len(tail_returns) > 0 else var_percentile
        
        es_value = -es_percentile * portfolio_value
        
        return es_value, -es_percentile
    
    def _simulate_returns(
        self,
        mean: np.ndarray,
        cov: np.ndarray
    ) -> np.ndarray:
        """æ¨¡ææ¶çç?""
        n_assets = len(mean)
        
        L = np.linalg.cholesky(cov)
        
        if self.distribution == "normal":
            z = np.random.standard_normal((self.n_simulations, n_assets))
        elif self.distribution == "student_t":
            df = 5
            z = np.random.standard_t(df, (self.n_simulations, n_assets))
        
        simulated = z @ L.T + mean
        
        return simulated
```

### 4.4 æ¹æ³æ¯è¾ä¸éæ©

| æ¹æ³ | è®¡ç®éåº¦ | åç¡®æ?| éç¨åºæ¯ | æ¨èç½®ä¿¡åº?|
|------|----------|--------|----------|------------|
| **åå²æ¨¡ææ³?* | å¿?| ä¸?| æ°æ®åè¶³ãåå¸æªç?| 95%-99% |
| **åæ°æ³?* | æå¿?| ä½?| æ­£æåå¸åè®¾æç«?| 95%-99% |
| **èç¹å¡æ´** | æ?| é«?| å¤æåå¸ãéçº¿æ?| 95%-99.9% |

---

## 5. çæ§ææ ä½ç³»

### 5.1 æ ¸å¿çæ§ææ 

| ææ ç±»å« | ææ åç§° | è®¡ç®æ¹æ³ | çæ§é¢ç | é¢è­¦éå?| è¯´æ |
|----------|----------|----------|----------|----------|------|
| **VaRææ ** | 1æ¥VaR(95%) | åå²æ¨¡ææ³?| å®æ¶ | -5% | 95%ç½®ä¿¡åº¦ä¸1æ¥æå¤§æå¤?|
| **VaRææ ** | 1æ¥VaR(99%) | åå²æ¨¡ææ³?| å®æ¶ | -8% | 99%ç½®ä¿¡åº¦ä¸1æ¥æå¤§æå¤?|
| **VaRææ ** | 10æ¥VaR(99%) | â?0Ã1æ¥VaR | æ¯æ¥ | -25% | 99%ç½®ä¿¡åº¦ä¸10æ¥æå¤§æå¤?|
| **ESææ ** | 1æ¥ES(95%) | å°¾é¨å¹³åæå¤± | å®æ¶ | -7% | è¶è¿VaRçå¹³åæå¤?|
| **ESææ ** | 1æ¥ES(99%) | å°¾é¨å¹³åæå¤± | å®æ¶ | -12% | è¶è¿VaRçå¹³åæå¤?|
| **åæµææ ** | Kupiecæ£éª?| LRç»è®¡é?| æ¯å¨ | p<0.05 | VaRæ¨¡åæææ§æ£éª?|
| **åæµææ ** | Christoffersenæ£éª?| ç¬ç«æ§æ£éª?| æ¯å¨ | p<0.05 | çªç ´åºåç¬ç«æ§æ£éª?|
| **åæµææ ** | çªç ´æ¬¡æ° | å®éæå¤±>VaRæ¬¡æ° | æ¯æ¥ | >5% | VaRçªç ´é¢ç |

### 5.2 çæ§ææ è®¡ç®å?

```python
class VaRESMonitor:
    """VaR/ESçæ§å?""
    
    def __init__(
        self,
        confidence_levels: List[float] = [0.95, 0.99],
        holding_periods: List[int] = [1, 10]
    ):
        self.confidence_levels = confidence_levels
        self.holding_periods = holding_periods
        self.historical_var = HistoricalVaR()
        self.parametric_var = ParametricVaR()
        self.monte_carlo_var = MonteCarloVaR()
    
    def calculate_all_metrics(
        self,
        returns: np.ndarray,
        portfolio_value: float
    ) -> Dict[str, float]:
        """è®¡ç®ææçæ§ææ ?""
        metrics = {}
        
        for conf in self.confidence_levels:
            self.historical_var.confidence_level = conf
            
            var_value, var_pct = self.historical_var.calculate_var(
                returns, portfolio_value
            )
            metrics[f"var_{int(conf*100)}_value"] = var_value
            metrics[f"var_{int(conf*100)}_pct"] = var_pct
            
            es_value, es_pct = self.historical_var.calculate_es(
                returns, portfolio_value
            )
            metrics[f"es_{int(conf*100)}_value"] = es_value
            metrics[f"es_{int(conf*100)}_pct"] = es_pct
        
        for period in self.holding_periods:
            for conf in self.confidence_levels:
                var_1d = metrics[f"var_{int(conf*100)}_pct"]
                var_nd = var_1d * np.sqrt(period)
                metrics[f"var_{period}d_{int(conf*100)}_pct"] = var_nd
        
        return metrics
    
    def check_thresholds(
        self,
        metrics: Dict[str, float],
        thresholds: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """æ£æ¥éå¼å¹¶çæé¢è­¦"""
        alerts = []
        
        for metric_name, value in metrics.items():
            if metric_name in thresholds:
                threshold = thresholds[metric_name]
                
                if value < threshold:
                    alerts.append({
                        "metric": metric_name,
                        "value": value,
                        "threshold": threshold,
                        "severity": "HIGH" if value < threshold * 1.5 else "MEDIUM",
                        "message": f"{metric_name} è¶è¿éå? {value:.2%} > {threshold:.2%}"
                    })
        
        return alerts
```

### 5.3 åæµéªè¯ç³»ç»

```python
class VaRBacktester:
    """VaRåæµéªè¯å?""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
    
    def kupiec_test(
        self,
        actual_returns: np.ndarray,
        var_estimates: np.ndarray
    ) -> Dict[str, float]:
        """
        Kupiecæ æ¡ä»¶è¦çæ£éª?
        
        åæ°:
            actual_returns: å®éæ¶çç?
            var_estimates: VaRä¼°è®¡å?
            
        è¿å:
            æ£éªç»æå­å?
        """
        n = len(actual_returns)
        x = np.sum(actual_returns < -var_estimates)
        p = 1 - self.confidence_level
        
        if x == 0 or x == n:
            lr_stat = 0
            p_value = 1.0
        else:
            lr_stat = -2 * (
                x * np.log(p / (x / n)) +
                (n - x) * np.log((1 - p) / (1 - x / n))
            )
            p_value = 1 - stats.chi2.cdf(lr_stat, 1)
        
        return {
            "test_name": "Kupiec Test",
            "n_observations": n,
            "n_breaches": x,
            "expected_breaches": n * p,
            "breach_rate": x / n,
            "expected_rate": p,
            "lr_statistic": lr_stat,
            "p_value": p_value,
            "passed": p_value > 0.05
        }
    
    def christoffersen_test(
        self,
        actual_returns: np.ndarray,
        var_estimates: np.ndarray
    ) -> Dict[str, float]:
        """
        Christoffersenç¬ç«æ§æ£éª?
        
        åæ°:
            actual_returns: å®éæ¶çç?
            var_estimates: VaRä¼°è®¡å?
            
        è¿å:
            æ£éªç»æå­å?
        """
        breaches = (actual_returns < -var_estimates).astype(int)
        
        n00 = np.sum((breaches[:-1] == 0) & (breaches[1:] == 0))
        n01 = np.sum((breaches[:-1] == 0) & (breaches[1:] == 1))
        n10 = np.sum((breaches[:-1] == 1) & (breaches[1:] == 0))
        n11 = np.sum((breaches[:-1] == 1) & (breaches[1:] == 1))
        
        if n01 + n00 == 0 or n10 + n11 == 0:
            lr_stat = 0
            p_value = 1.0
        else:
            p01 = n01 / (n00 + n01)
            p10 = n10 / (n10 + n11)
            p = (n01 + n11) / (n00 + n01 + n10 + n11)
            
            lr_stat = -2 * (
                (n00 + n01) * np.log(1 - p) + (n10 + n11) * np.log(p) -
                n00 * np.log(1 - p01) - n01 * np.log(p01) -
                n10 * np.log(1 - p10) - n11 * np.log(p10)
            )
            p_value = 1 - stats.chi2.cdf(lr_stat, 1)
        
        return {
            "test_name": "Christoffersen Test",
            "n_00": n00,
            "n_01": n01,
            "n_10": n10,
            "n_11": n11,
            "lr_statistic": lr_stat,
            "p_value": p_value,
            "passed": p_value > 0.05
        }
    
    def generate_backtest_report(
        self,
        actual_returns: np.ndarray,
        var_estimates: np.ndarray
    ) -> Dict[str, Any]:
        """çæåæµæ¥å"""
        kupiec_result = self.kupiec_test(actual_returns, var_estimates)
        christoffersen_result = self.christoffersen_test(actual_returns, var_estimates)
        
        return {
            "summary": {
                "total_observations": len(actual_returns),
                "total_breaches": kupiec_result["n_breaches"],
                "breach_rate": kupiec_result["breach_rate"],
                "expected_rate": kupiec_result["expected_rate"]
            },
            "kupiec_test": kupiec_result,
            "christoffersen_test": christoffersen_result,
            "overall_passed": kupiec_result["passed"] and christoffersen_result["passed"]
        }
```

### 5.4 å®æ¶çæ§é¢æ¿ææ 

```python
class VaRESMonitorDashboard:
    """VaR/ESå®æ¶çæ§é¢æ¿"""
    
    def __init__(self):
        self.monitor = VaRESMonitor()
        self.backtester = VaRBacktester()
    
    def get_dashboard_metrics(
        self,
        portfolio_id: str,
        returns: np.ndarray,
        portfolio_value: float
    ) -> Dict[str, Any]:
        """è·åçæ§é¢æ¿ææ """
        metrics = self.monitor.calculate_all_metrics(returns, portfolio_value)
        
        thresholds = {
            "var_95_pct": -0.05,
            "var_99_pct": -0.08,
            "es_95_pct": -0.07,
            "es_99_pct": -0.12
        }
        
        alerts = self.monitor.check_thresholds(metrics, thresholds)
        
        return {
            "portfolio_id": portfolio_id,
            "timestamp": datetime.now(),
            "metrics": metrics,
            "alerts": alerts,
            "risk_level": self._calculate_risk_level(metrics, thresholds)
        }
    
    def _calculate_risk_level(
        self,
        metrics: Dict[str, float],
        thresholds: Dict[str, float]
    ) -> str:
        """è®¡ç®é£é©ç­çº§"""
        breach_count = 0
        
        for metric_name, value in metrics.items():
            if metric_name in thresholds and value < thresholds[metric_name]:
                breach_count += 1
        
        if breach_count >= 3:
            return "HIGH"
        elif breach_count >= 1:
            return "MEDIUM"
        else:
            return "LOW"
```

---

## 6. æ§è½è¦æ±

```python
class VaRESAPI:
    """VaR/ES APIæ¥å£"""
    
    @endpoint("/api/v1/var_es/calculate")
    async def calculate(
        self,
        portfolio_id: str,
        method: str = "historical"
    ) -> VaRESResult:
        """è®¡ç®VaRåES"""
        
    @endpoint("/api/v1/var_es/backtest")
    async def backtest(
        self,
        portfolio_id: str,
        start_date: str,
        end_date: str
    ) -> BacktestResult:
        """VaRåæµéªè¯"""
        
    @endpoint("/api/v1/var_es/alerts")
    async def get_alerts(
        self,
        portfolio_id: str
    ) -> List[Alert]:
        """è·åé£é©é¢è­¦"""
```

---

## 5. å®æ½è·¯å¾

| é¶æ®µ | ä»»å¡ | å·¥æ¶ |
|------|------|------|
| Phase 1 | æ ¸å¿è®¡ç®æ¨¡åå®ç° | 16h |
| Phase 2 | å¤æ¹æ³æ¯æãåæµéªè¯?| 16h |
| Phase 3 | APIå¼åãå®æ¶çæ§é¢æ?| 16h |

---

## 6. ææ¡£æ²»ç

**ç´¢å¼ä½ç½®**: Layer 6 - ç»åä¼åå±?- é£é©ç®¡çæ¨¡å

**çæ¬ç®¡ç**:
- v1.0.0: åå§çæ¬ (2026-04-06)

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active | **åè§ç?*: 100% â?

## åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|
| v1.0.1 | 2026-04-06 | è¡¥åYAMLå¤´é¨å­æ®µååæ´åå?| å®¡è®¡ç³»ç» |

---

**èå¾çæ¬**: v1.0.1 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active
