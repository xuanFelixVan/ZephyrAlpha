---
module_id: STRATEGIC_WEIGHTING_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 6 ç»åä¼åå±?
compliance_level: ä¸ä¸æ å
responsibility:
  - æç¥æéåé
  - æç¥èµäº§éç½®
  - é¿ææéä¼å
  - æç¥éç½®å³ç­
layer: Layer 5 (策略执行层)
---


## 核心定位

负责战略权重的设计与实现，基于战略配置目标，提供资产权重分配方案，支持战略配置实施。

# æç¥æéåéèå¾

> **æ ¸å¿èè´£**: æç¥æéåéï¼æç¥èµäº§éç½?
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼æç¥æéåéãæç¥èµäº§éç½®ãé¿ææéä¼åãæç¥éç½®å³ç­?
> - â?æ¬ææ¡£ä¸è´è´£ï¼ææ¯æéè°æ´ãç­ææéä¼åãé£é©æ§å?

ï»? ð æ§è¡æè¦

> **çæ¬**: v1.0
> **åå»ºæ¥æ**: 2026-04-06
> **æ ¸å¿å®ä½**: å®è§éç½®å±æç¥èµäº§æéåé?
> **ç´¢å¼**: `STRATEGIC_WEIGHTING_001`
> **å¼åå¨æ?*: 2.5å?

## æ ¸å¿å®ä½

è´è´£Strategic Weightingçè®¾è®¡ãå®ç°åç»´æ¤ï¼æä¾æ ¸å¿åè½æ¯æï¼ç¡®ä¿ç³»ç»æ¨¡åçç¨³å®è¿è¡åé«ææ§è¡ã?

## ð¯ æ¨¡åå®ä½ä¸èè´?

### æ ¸å¿èè´£

| èè´£ç±»å« | å·ä½èè´£ | è¾åºäº§ç© |
|---------|---------|---------|
| **æéè®¡ç®** | è®¡ç®æç¥èµäº§æé | ç®æ æéæ¹æ¡ |
| **é£é©å¹³ä»·** | å®ç°é£é©å¹³ä»·éç½® | é£é©å¹³ä»·æé |
| **ä¼åæ±è§£** | å¤ç®æ ä¼åæ±è§?| æä¼æé?|
| **çº¦æå¤ç** | å¤çéç½®çº¦æ | çº¦ææ»¡è¶³æé |

---

## ðï¸?æ¶æè®¾è®¡

### èµäº§éç½®æ¡æ¶

```mermaid
graph TB
    A[ç»æµèå¼å¤æ­] --> B[èµäº§æéåéç³»ç»]
    C[å¸åºç¶æè¯å«] --> B
    D[é£é©é¢ç®] --> B
    
    B --> E{éç½®æ¨¡åéæ©}
    
    E -->|ç»æµæ©å¼ | F[é£é©å¹³ä»·æ¨¡å]
    E -->|ç»æµè¡°é| G[é²å¾¡æ§éç½®]
    E -->|ç»æµæ»è| H[éèå¯¹å²éç½®]
    E -->|ç»æµå¤è| I[è¿æ»æ§éç½®]
    
    F --> J[ç®æ æé]
    G --> J
    H --> J
    I --> J
    
    J --> K[çº¦æä¼å]
    K --> L[æç»éç½®æ¹æ¡]
```

---

## ð§ å³é®ç»ä»¶è®¾è®¡

### 1. é£é©å¹³ä»·æ¨¡å

```python
from typing import Dict, Any
import pandas as pd
import numpy as np
import cvxpy as cp

class RiskParityModel:
    """é£é©å¹³ä»·æ¨¡å"""
    
    def __init__(self):
        self.target_risk_contribution = None
        
    def optimize(self,
                covariance_matrix: pd.DataFrame,
                target_risk: Dict[str, float] = None) -> Dict[str, float]:
        """ä¼åé£é©å¹³ä»·æé"""
        n_assets = len(covariance_matrix)
        
        # å¦ææ²¡ææå®ç®æ é£é©è´¡ç®ï¼åå¹³ååé
        if target_risk is None:
            target_risk_contribution = np.ones(n_assets) / n_assets
        else:
            target_risk_contribution = np.array(list(target_risk.values()))
        
        # å®ä¹ä¼ååé
        weights = cp.Variable(n_assets)
        
        # è®¡ç®ç»åé£é©
        portfolio_risk = cp.quad_form(weights, covariance_matrix.values)
        
        # è®¡ç®é£é©è´¡ç®
        marginal_risk = covariance_matrix.values @ weights
        risk_contribution = cp.multiply(weights, marginal_risk) / portfolio_risk
        
        # ç®æ å½æ°ï¼æå°åé£é©è´¡ç®ä¸ç®æ é£é©è´¡ç®çå·®å¼
        objective = cp.Minimize(
            cp.sum_squares(risk_contribution - target_risk_contribution)
        )
        
        # çº¦ææ¡ä»¶
        constraints = [
            cp.sum(weights) == 1,  # æéåä¸º1
            weights >= 0,  # ä¸åè®¸åç©?
            weights <= 0.40  # åèµäº§æå¤§æé?0%
        ]
        
        # æ±è§£
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        # è¿åæé
        optimal_weights = dict(zip(
            covariance_matrix.columns,
            weights.value
        ))
        
        return optimal_weights


class AllWeatherModel:
    """å¨å¤©åéç½®æ¨¡å?""
    
    def __init__(self):
        # åç§ç»æµç¯å¢
        self.economic_environments = {
            'GROWTH': 'ç»æµå¢é¿',
            'INFLATION': 'éèä¸å',
            'DEFLATION': 'éç¼©è¡°é',
            'RECESSION': 'ç»æµè¡°é'
        }
        
        # åç¯å¢ä¸çèµäº§æé?
        self.environment_weights = {
            'GROWTH': {
                'è¡ç¥¨': 0.30,
                'åºå¸': 0.15,
                'åå': 0.40,
                'ç°é': 0.15
            },
            'INFLATION': {
                'è¡ç¥¨': 0.20,
                'åºå¸': 0.10,
                'åå': 0.50,
                'ç°é': 0.20
            },
            'DEFLATION': {
                'è¡ç¥¨': 0.10,
                'åºå¸': 0.50,
                'åå': 0.10,
                'ç°é': 0.30
            },
            'RECESSION': {
                'è¡ç¥¨': 0.10,
                'åºå¸': 0.40,
                'åå': 0.10,
                'ç°é': 0.40
            }
        }
        
    def allocate(self,
                economic_regime: str,
                regime_probability: float) -> Dict[str, float]:
        """æ ¹æ®ç»æµèå¼åéæé"""
        # è·ååºåæé
        base_weights = self.environment_weights.get(economic_regime, 
                                                   self.environment_weights['GROWTH'])
        
        # æ ¹æ®æ¦çè°æ´æé
        adjusted_weights = {}
        for asset, weight in base_weights.items():
            adjusted_weights[asset] = weight * regime_probability
        
        # å½ä¸å?
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {
                asset: weight / total_weight
                for asset, weight in adjusted_weights.items()
            }
        
        return adjusted_weights
```

### 2. å¤ç®æ ä¼åå¨

```python
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import cvxpy as cp

class MultiObjectiveOptimizer:
    """å¤ç®æ ä¼åå¨"""
    
    def __init__(self):
        self.objectives = {
            'return': self._maximize_return,
            'risk': self._minimize_risk,
            'sharpe': self._maximize_sharpe,
            'diversification': self._maximize_diversification
        }
        
    def optimize(self,
                expected_returns: pd.Series,
                covariance_matrix: pd.DataFrame,
                objective_weights: Dict[str, float],
                constraints: Dict[str, Any]) -> Dict[str, float]:
        """å¤ç®æ ä¼å?""
        n_assets = len(expected_returns)
        
        # å®ä¹ä¼ååé
        weights = cp.Variable(n_assets)
        
        # è®¡ç®åç®æ ?
        portfolio_return = expected_returns.values @ weights
        portfolio_risk = cp.sqrt(cp.quad_form(weights, covariance_matrix.values))
        
        # æå»ºç»¼åç®æ å½æ°
        objective_value = 0
        
        if 'return' in objective_weights:
            objective_value += objective_weights['return'] * portfolio_return
        
        if 'risk' in objective_weights:
            objective_value -= objective_weights['risk'] * portfolio_risk
        
        if 'sharpe' in objective_weights:
            risk_free_rate = 0.02
            objective_value += objective_weights['sharpe'] * (portfolio_return - risk_free_rate) / portfolio_risk
        
        # ç®æ å½æ°
        objective = cp.Maximize(objective_value)
        
        # çº¦ææ¡ä»¶
        constraint_list = [
            cp.sum(weights) == 1,
            weights >= constraints.get('min_weight', 0),
            weights <= constraints.get('max_weight', 1)
        ]
        
        # è¡ä¸çº¦æ
        if 'sector_constraints' in constraints:
            for sector, (min_weight, max_weight) in constraints['sector_constraints'].items():
                sector_mask = self._get_sector_mask(sector)
                constraint_list.append(cp.sum(weights[sector_mask]) >= min_weight)
                constraint_list.append(cp.sum(weights[sector_mask]) <= max_weight)
        
        # æ±è§£
        problem = cp.Problem(objective, constraint_list)
        problem.solve()
        
        # è¿åæé
        optimal_weights = dict(zip(
            expected_returns.index,
            weights.value
        ))
        
        return optimal_weights
    
    def _maximize_return(self, weights, expected_returns):
        """æå¤§åæ¶ç"""
        return expected_returns @ weights
    
    def _minimize_risk(self, weights, covariance_matrix):
        """æå°åé£é©"""
        return cp.quad_form(weights, covariance_matrix)
    
    def _maximize_sharpe(self, weights, expected_returns, covariance_matrix, risk_free_rate=0.02):
        """æå¤§åå¤æ®æ¯ç"""
        portfolio_return = expected_returns @ weights
        portfolio_risk = cp.sqrt(cp.quad_form(weights, covariance_matrix))
        return (portfolio_return - risk_free_rate) / portfolio_risk
    
    def _maximize_diversification(self, weights, covariance_matrix):
        """æå¤§ååæ£åº?""
        n = len(weights)
        return -cp.sum_squares(weights - 1/n)
    
    def _get_sector_mask(self, sector: str) -> np.ndarray:
        """è·åè¡ä¸æ©ç """
        # ç®åå®ç°ï¼å®éåºæ ¹æ®è¡ä¸åç±»æ å°?
        return np.ones(100, dtype=bool)
```

### 3. çº¦æå¤çå?

```python
class ConstraintHandler:
    """çº¦æå¤çå?""
    
    def __init__(self):
        self.constraints = {}
        
    def add_constraint(self, constraint_type: str, constraint_params: Dict[str, Any]) -> None:
        """æ·»å çº¦æ"""
        self.constraints[constraint_type] = constraint_params
        
    def apply_constraints(self,
                         weights: Dict[str, float],
                         portfolio_value: float) -> Dict[str, float]:
        """åºç¨çº¦æ"""
        adjusted_weights = weights.copy()
        
        # åºç¨æéçº¦æ
        if 'weight_bounds' in self.constraints:
            min_weight = self.constraints['weight_bounds'].get('min', 0)
            max_weight = self.constraints['weight_bounds'].get('max', 1)
            
            for asset in adjusted_weights:
                adjusted_weights[asset] = np.clip(
                    adjusted_weights[asset],
                    min_weight,
                    max_weight
                )
        
        # åºç¨æµå¨æ§çº¦æ?
        if 'liquidity' in self.constraints:
            min_liquidity = self.constraints['liquidity'].get('min', 0)
            
            for asset, weight in adjusted_weights.items():
                asset_value = weight * portfolio_value
                # æ£æ¥æµå¨æ§æ¯å¦è¶³å¤?
                # å¦æä¸è¶³ï¼éä½æé?
                # adjusted_weights[asset] = ...
                pass
        
        # å½ä¸å?
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {
                asset: weight / total_weight
                for asset, weight in adjusted_weights.items()
            }
        
        return adjusted_weights
```

---

## ð å®æ½è¦ç¹

### é¶æ®µ1ï¼é£é©å¹³ä»·æ¨¡åå¼åï¼ç¬?å¨ï¼

**ä»»å¡**:
1. â?å®ç°é£é©å¹³ä»·ä¼å
2. â?å®ç°å¨å¤©åéç½?
3. â?å®ç°åæ¹å·®ç©éµä¼°è®?
4. â?ç¼åååæµè¯

---

### é¶æ®µ2ï¼å¤ç®æ ä¼åå¨å¼åï¼ç¬?-2å¨ï¼

**ä»»å¡**:
1. â?å®ç°æ¶çæå¤§å
2. â?å®ç°é£é©æå°å
3. â?å®ç°å¤æ®æ¯çæå¤§å
4. â?å®ç°åæ£åº¦æå¤§å
5. â?ç¼åååæµè¯

---

### é¶æ®µ3ï¼çº¦æå¤çå¨å¼åï¼ç¬?-3å¨ï¼

**ä»»å¡**:
1. â?å®ç°æéçº¦æ
2. â?å®ç°æµå¨æ§çº¦æ?
3. â?å®ç°è¡ä¸çº¦æ
4. â?éææµè¯

---

## ð æ§è½ææ 

### éç½®è´¨éææ 

| ææ  | ç®æ å?|
|------|--------|
| **é£é©è´¡ç®åè¡¡åº?* | < 10% |
| **å¤æ®æ¯çæå** | > 0.2 |
| **åæ£åº?* | > 0.7 |
| **çº¦ææ»¡è¶³ç?* | 100% |

---

## ð ç¸å³ææ¡£

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [ç­ç¥éæ©ç³»ç»èå¾](./STRATEGY_SELECTION_BLUEPRINT.md) | STRATEGY_SELECTION_001 | å¼ºä¾èµ?| æä¾ç­ç¥éæ©ç»æ |
| [æ°æ®è´¨éçæ§èå¾](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | DATA_QUALITY_MONITORING_001 | å¼ºä¾èµ?| æä¾æ°æ®è´¨éææ  |
| [é£é©å¹³ä»·ç­ç¥èå¾](./RISK_PARITY_STRATEGY_BLUEPRINT.md) | RISK_PARITY_STRATEGY_001 | ä¸­ä¾èµ?| æä¾é£é©å¹³ä»·æ¨¡å |

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [å­£åº¦è°ä»èå¾](./QUARTERLY_REBALANCE_BLUEPRINT.md) | QUARTERLY_REBALANCE_001 | å¼ºä¾èµ?| å­£åº¦è°ä»å³ç­ |
| [ç»ååå¹³è¡¡èå¾](./PORTFOLIO_REBALANCING_BLUEPRINT.md) | PORTFOLIO_REBALANCING_001 | ä¸­ä¾èµ?| ç»ååå¹³è¡?|
| [ç»åä¼åå¼æéæèå¾](./PORTFOLIO_OPTIMIZER_INTEGRATION_BLUEPRINT.md) | PORTFOLIO_OPTIMIZER_INTEGRATION_001 | ä¸­ä¾èµ?| ç»åä¼å |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **CVXPY** | 1.4+ | å¸ä¼å?| [å®æ¹ææ¡£](https://www.cvxpy.org/) |
| **Pandas** | 2.0+ | æ°æ®å¤ç | [å®æ¹ææ¡£](https://pandas.pydata.org/) |
| **NumPy** | 1.24+ | æ°å¼è®¡ç®?| [å®æ¹ææ¡£](https://numpy.org/) |
| **SciPy** | 1.10+ | ç§å­¦è®¡ç® | [å®æ¹ææ¡£](https://scipy.org/) |

### å¼ç¨å³ç³»å?

```mermaid
graph LR
    A[ç­ç¥éæ©ç³»ç»] --> B[æç¥æéåé]
    C[æ°æ®è´¨éçæ§] --> B
    D[é£é©å¹³ä»·ç­ç¥] --> B
    
    B --> E[å­£åº¦è°ä»]
    B --> F[ç»ååå¹³è¡¡]
    B --> G[ç»åä¼åå¼æ]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
```

### ç¸å³èå¾ææ¡£

- [å­£åº¦è°ä»å³ç­ç³»ç»èå¾](./QUARTERLY_REBALANCE_BLUEPRINT.md)
- [ç»æµèå¼å¤æ­å¼æèå¾](./ECONOMIC_REGIME_ENGINE_BLUEPRINT.md)
- ä¸ä¸å¤æ¶é´æ¡æ¶ç­ç¥æ¶æ?

---

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**èå¾ç¶æ?*: â?è®¾è®¡å®æ
**ä¸ä¸æ­?*: å¼å§å®æ½é¶æ®? - é£é©å¹³ä»·æ¨¡åå¼å?
---

## 1. ææ¡£æ²»ç

### 1.1 System_Manifest.mdç´¢å¼

```markdown
#### Layer 5: å®è§éç½®å±?
##### 6.001. Strategic Weighting
- **æ¨¡åID**: STRATEGIC_WEIGHTING_001
- **èå¾ææ¡£**: STRATEGIC_WEIGHTING_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾åå»?
- **èè´£**: å®è§éç½®å±æç¥èµäº§éç½?
- **ç¶æ?*: Active
```

### 1.2 æ¨¡åèè´£è¾¹ç

| æ¨¡å | èè´£ | è¾¹ç |
|------|------|------|
| **Strategic Weighting** | å®è§éç½®å±æç¥èµäº§éç½?| **æ ¸å¿æ¨¡å** |

### 1.3 çæ¬ç®¡ç

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active
