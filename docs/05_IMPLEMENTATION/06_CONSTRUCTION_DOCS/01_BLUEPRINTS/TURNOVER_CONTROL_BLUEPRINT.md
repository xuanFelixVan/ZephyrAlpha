---
responsibility:
  - å¨è½¬çæ§å?
  - äº¤æææ¬ä¼å
  - æ¢æçç®¡ç?
  - ææ¬çº¦æ

module_id: TURNOVER_CONTROL_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 6 ç»åä¼åå±?
compliance_level: ä¸ä¸æ å
layer: Layer 5.4 (交易执行)
---

# ç»åå¨è½¬çæ§å¶èå?

> **æ ¸å¿èè´£**: æ§å¶ç»åå¨è½¬çï¼éä½äº¤æææ¬
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼å¨è½¬çæ§å¶ãäº¤æææ¬ä¼å?
> - â?æ¬ææ¡£ä¸è´è´£ï¼å å­è®¡ç®ï¼ç±å å­æ¨¡åè´è´£ï¼

## æ ¸å¿å®ä½

è´è´£TURNOVER CONTROLçè®¾è®¡ä¸å®ç°ï¼ä¿éæ ¸å¿åè½ï¼ä¼åç¨æ·ä½éªãæ¯æä¸å¡éæ±ï¼ç¡®ä¿ç³»ç»ç¨³å®è¿è¡ã?

## 2. åè½è®¾è®¡

### 2.1 æ ¸å¿åè½

```python
class TurnoverController:
    """
    å¨è½¬çæ§å¶å¨
    """
    
    def set_turnover_constraint(
        self,
        current_weights: np.ndarray,
        max_turnover: float = 0.3
    ) -> None:
        """
        è®¾ç½®å¨è½¬ççº¦æ?
        
        åæ°:
            current_weights: å½åæé
            max_turnover: æå¤§å¨è½¬çï¼å¦0.3è¡¨ç¤º30%ï¼?
        """
        pass
    
    def calculate_turnover(
        self,
        current_weights: np.ndarray,
        target_weights: np.ndarray
    ) -> float:
        """
        è®¡ç®å¨è½¬ç?
        
        Turnover = 0.5 * sum(|w_target - w_current|)
        """
        pass
    
    def optimize_with_turnover_constraint(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        current_weights: np.ndarray,
        max_turnover: float
    ) -> Dict:
        """
        å¸¦å¨è½¬ççº¦æçä¼å?
        """
        pass
```

---

## 3. éç½®åæ°

```yaml
turnover_control:
  # å¨è½¬ççº¦æ?
  max_turnover: 0.3  # å¹´å30%
  
  # äº¤æé¢ç
  min_holding_period: 5  # æå°æä»å¤©æ?
  
  # ææ¬èè
  transaction_cost_rate: 0.001  # äº¤æææ¬ç?
```

---

## ð ç¸å³ææ¡£

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [ç»åä¼åå¼æéæèå¾](./PORTFOLIO_OPTIMIZER_INTEGRATION_BLUEPRINT.md) | PORTFOLIO_OPTIMIZER_INTEGRATION_001 | å¼ºä¾èµ?| æä¾ä¼åå¨åºç¡æ¥å£ |
| [æ°æ®è´¨éçæ§èå¾](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | DATA_QUALITY_MONITORING_001 | å¼ºä¾èµ?| æä¾æ°æ®è´¨éææ  |
| [äº¤æææ¬åæå¼æèå¾](./TRANSACTION_COST_ANALYSIS_ENGINE_BLUEPRINT.md) | TRANSACTION_COST_ANALYSIS_ENGINE_001 | ä¸­ä¾èµ?| æä¾ææ¬åæ |

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [ç»ååå¹³è¡¡èå¾](./PORTFOLIO_REBALANCING_BLUEPRINT.md) | PORTFOLIO_REBALANCING_001 | å¼ºä¾èµ?| ç»ååå¹³è¡?|
| [å­£åº¦è°ä»èå¾](./QUARTERLY_REBALANCE_BLUEPRINT.md) | QUARTERLY_REBALANCE_001 | ä¸­ä¾èµ?| å­£åº¦è°ä»å³ç­ |
| [ç¨ææ¶å²èå¾](./TAX_LOSS_HARVESTING_BLUEPRINT.md) | TAX_LOSS_HARVESTING_001 | ä¸­ä¾èµ?| ç¨ææ¶å²ç­ç¥ |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **Riskfolio-Lib** | 7.0+ | å¨è½¬ççº¦æ?| [å®æ¹ææ¡£](https://riskfolio-lib.readthedocs.io/) |
| **PyPortfolioOpt** | 1.5+ | çº¦æç³»ç» | [å®æ¹ææ¡£](https://pyportfolioopt.readthedocs.io/) |
| **NumPy** | 1.24+ | æ°å¼è®¡ç®?| [å®æ¹ææ¡£](https://numpy.org/) |
| **Pandas** | 2.0+ | æ°æ®å¤ç | [å®æ¹ææ¡£](https://pandas.pydata.org/) |

### å¼ç¨å³ç³»å?

```mermaid
graph LR
    A[ç»åä¼åå¼æ] --> B[å¨è½¬çæ§å¶]
    C[æ°æ®è´¨éçæ§] --> B
    D[äº¤æææ¬åæå¼æ] --> B
    
    B --> E[ç»ååå¹³è¡¡]
    B --> F[å­£åº¦è°ä»]
    B --> G[ç¨ææ¶å²]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
```

---

## 4. åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-07 | **ç¶æ?*: Active

## 5. ææ¡£æ²»ç

### 5.1 ææ¡£ç´¢å¼

**æ¬ææ¡£å¨ç³»ç»ä¸­çä½ç½®**:
- **æå±å±çº?*: Layer 6 (ç»åä¼åå±?
- **æ¨¡åç´¢å¼**: 001
- **æ¨¡ååç§°**: TURNOVER_CONTROL
- **ææ¡£è·¯å¾**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/

### 5.2 çæ¬ç®¡ç

**çæ¬åå²**:
- v1.0.0 (2026-04-07): åå§çæ¬

### 5.3 ç»´æ¤è´£ä»»

**ææ¡£ç»´æ¤**:
- **è´£ä»»æ¨¡å**: TURNOVER_CONTROL
- **ç»´æ¤å¨æ**: æ¯å­£åº¦å®¡æ?
- **åæ´æµç¨**: æäº¤åæ´ç³è¯· â?ææ¯è¯å®?â?æ´æ°ææ¡£

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-07 | **ç¶æ?*: Active
