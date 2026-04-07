﻿---
module_id: AI_FACTOR_MINER_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: docs/module_designs/layer_9/L9_FACTOR_MINER.md
last_updated: 2026-04-02
created_date: 2026-04-02
layer: Layer 9 (AIﮒﮔﺍ? | ﻛﺕﮒ۰ﮔﭘﮔ: ﻛﺕﻝﭦ۶ﮔﭘﻠﺑﮔ۰ﮔﭘﻟﮒﮔﭘﮔ
index: AI_FACTOR_MINER_001
estimated_hours: 80
review_status: Pending
reviewer: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
review_date: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﭘﮔ?standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶?applicable_scope: ﮒ۷ﻝﺏﭨ?compliance_level: ﻛﺕﻛﺕﮔ ﮒ
responsibility:
  - 实施指南、部署文档
parent_document: ../INDEX.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﮒ؟ﮔ
---
---


# AIﮒ ﮒ­ﮔﮔﮔ۷۰ﮒﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ v1.0
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.3 - AIﮒ ﮒ­ﮔﮔﮔ۷۰ﮒﻟﺁ۵ﻝﭨﮔﮔﺁﻟ؟ﺝ?> **ﻝﺑ۱ﮒﺙ**: `AI_FACTOR_MINER_001`
> **ﮒﺙﮒﮔﭘ?*: 80h
---

## 1. ﮔ۵ﻟﺟﺍ

### 1.1 ﻟ؟ﺝﻟ؟۰ﻟﮔﺁﻛﺕﻛﺕﮒ۰ﻝ؟?
**ﻛﺕﮒ۰ﻠ?*:
- ﻛﺕﻛﺕﮔﭦﮔ(ﮔ۰۴ﮔﺍﺑﻙﮔﻟﭦﮒ۳?ﮒﮒﺓﮒ۳ﮒﺙﭦﮒ۳۶ﻝﮒﮒﮒ ﮒ­ﻝ ﮒﻟﺛﮒ

**ﮔﮔﺁﻝ?*:
- ﻛﺙ ﻝﭨﮒ ﮒ­ﮔﮔﻛﺝﻟﭖﻛﭦﭦﮒﺓ۴ﻝﭨﻠ۹,ﮔﻝﻛﺛﻛﺕ
- ﻝﺙﭦﮒﺍﻟ۹ﮒ۷ﮒﮒ ﮒ­ﮒﻝﺍﮒﻠ۹ﻟﺁﮔﭦﮒﭘ
- AIﮔﮔﺁﮒﭦﻝ۷ﮔﺓﺎﮒﭦ۵ﻛﺕ?ﻛﭨﮒﻝﮒ۷LLMﻟﺝﮒ۸ﮒﺎﻠ۱

**ﻠ۱ﮔﻛﭨ?*:
- ﻟ۹ﮒ۷ﮔﮔﮒﮒﮒ ﮒ­,ﮔﮒAlphaﮔﭘﻝ
- ﻠﻛﺛﮒ ﮒ­ﻝ ﮒﮔﮔ؛80%ﻛﭨ۴ﻛﺕ
- ﻝﺙ۸ﻝ­ﮒ ﮒ­ﻝ ﮒﮒ۷ﮔﻛﭨﮔﺍﮔﮒﺍﮔﺍﮒ۳۸
- ﮔﮒﮒ ﮒ­ﮒﭦﮒﺓ؟ﮒﺙﮒﻝ،ﻛﭦﻛﺙﮒﺟ

### 1.2 ﮔﮔﺁﮒ؟ﻛﺛﻛﺕﮔﭘﮔﮒﺎﮒﺛ?
**Layerﮒ؟ﻛﺛ**: Layer 9 - AIﮒ۱ﮒﺙﭦ?(ﻝ؛۵ﮒARCHITECTURE.mdﮒ؟ﻛﺗ)

**ﮔ۷۰ﮒﻝﺎﭨﮒ،**: ﮔ ﺕﮒﺟﮔ۷۰ﮒ

**ﮔﭘﮔﻟ۶ﻟﺎ**: 
- ﮒﻛﺕ: ﻛﺕﭦLayer 2ﮒ ﮒ­ﮒﺎﮔﻛﺝﮒﮒﮒ ?- ﮒﻛﺕ: ﻛﺝﻟﭖLayer 0ﮔﺍﮔ؟ﮔﭦﮒﺎﮒLayer 1ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝﮒﺎ
- ﮔ۷۹ﮒ: ﻛﺕLayer 4ﮔﭦﮒ۷ﮒ­۵ﻛﺗ ﮒﺎﮒﮒﮒﺓ۴?
### 1.3 ﻝﮔ؛ﻛﺟ۰ﮔﺁﻛﺕﮒﮔﺑﻟ؟ﺍ?
| ﻝﮔ؛ | ﮔ۴ﮔ | ﻛﺛ?| ﮒﮔﺑﻟﺁﺑﮔ | ﻝ?|
|------|------|------|----------|------|
| v1.0 | 2026-04-02 | ﻠ۵ﮒﺕ­ﮔﭘﮔ?| ﮒﮒ۶ﻝﮔ؛,ﮒﮒ،ﻛﺕﮒ۳۶AIﮔﮔﮒﺙﮔ | Draft |

---

## 2. ﻟﺁ۵ﻝﭨﮔﭘﮔﻟ؟ﺝﻟ؟۰

### 2.1 ﻝﺏﭨﻝﭨﮔﭘﮔ?
```

### 2.2 Layerﮒ؟ﻛﺛﻟﺁ۵ﻝﭨﻟﺁﺑﮔ

**Layerﮒﺛﮒﺎ**: Layer 9 - AIﮒ۱ﮒﺙﭦ?
**ﻟﻟﺑ۲ﻟﮒﺑ**: 
- ﻛﺛﺟﻝ۷AIﮔﮔﺁﻟ۹ﮒ۷ﮔﮔﮒﮒAlphaﮒ ﮒ­
- ﮒ ﮒ­ﻟﺑ۷ﻠﻟﺁﻛﺙﺍﻛﺕﻠ۹?- ﮒ ﮒ­ﮔﺏ۷ﮒﻛﺕﻝﮒﺛﮒ۷ﮔﻝ؟۰?
**ﻛﺕﻛﺕﮒﺎﮔ۴?*:
- **ﻛﺕﮒﺎﻛﺝﻟﭖ**: Layer 2ﮒ ﮒ­?(ﮔﻛﺝﮔﮔﻝﮒ ?
- **ﻛﺕﮒﺎﻛﺝﻟﭖ**: 
  - Layer 0ﮔﺍﮔ؟ﮔﭦﮒﺎ (ﮒﮒ۶ﮔﺍﮔ؟)
  - Layer 1ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝﮒﺎ (ﮔﺕﮔﺑﮒﮔﺍ?
  - Layer 4ﮔﭦﮒ۷ﮒ­۵ﻛﺗ ?(ﮔ۷۰ﮒﻟ؟­ﻝﭨﮔﺁﮔ)

### 2.3 ﮔ۷۰ﮒﻟﻟﺑ۲ﻛﺕﻟﺝﺗﻝﮒ؟?
**ﮔ ﺕﮒﺟﻟﻟﺑ۲**: AIﻠ۸ﺎﮒ۷ﻝﮒﮒﮒ ﮒ­ﻟ۹ﮒ۷ﮔ?
**ﻟﻟﺑ۲ﻟﺝﺗﻝ**:
- ?ﮔ؛ﮔ۷۰ﮒﻟﺑ?
  - ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮒ ﮒ­ﮔﮔ(LSTMﻙTransformerﻙGNN)
  - ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﮒ ﮒ­ﻛﺙﮒ(DQNﻙPPOﻙA2C)
  - ﻠﻛﺙ ﻝ؟ﮔﺏﮒ ﮒ­ﮒﻝﺍ(ﻟ۰۷ﻟﺝﺝﮒﺙﮔﮔﻙﻟ۶ﮒﮒ?
  - ﮒ ﮒ­ﻟﺑ۷ﻠﻟﺁﻛﺙﺍ(IC/IRﻙﻝﺕﮒﺏﮔ۶ﻙﻝ۷ﺏﮒ؟?
  - ﮒ ﮒ­ﮔﺏ۷ﮒﻛﺕﮒ­?  
- ?ﮔ؛ﮔ۷۰ﮒﻛﺕﻟﺑﻟﺑ۲:
  - ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮔ۶ﻟ۰ (ﻝﺎLayer 2ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮒﺙﮔﻟﺑﻟﺑ۲)
  - ﮒ ﮒ­ﮒﮔﭖﻠ۹ﻟﺁ (ﻝﺎﮒ ﮒ­ﮒﮔﭖﮔ۷۰ﮒﻟﺑ?
  - ﮒ ﮒ­ﮒﮔﻛﺙﮒ (ﻝﺎﮒ ﮒ­ﮒﮔﮔ۷۰ﮒﻟﺑ?
  - ﻝ­ﻝ۴ﻛﺟ۰ﮒﺓﻝﮔ (ﻝﺎﻝ­ﻝ۴ﮒﺙﮔﻟﺑ?

**ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵**: ﮔﻛﺝﻝﭨﻛﺕﻝPython APIﮔ۴ﮒ۲

### 2.4 ﻛﺝﻟﭖﮒﺏﻝﺏﭨ

| ﻛﺝﻟﭖﮔ۷۰ﮒ | ﻛﺝﻟﭖﻝﺎﭨﮒ | ﮔ۴ﮒ۲ﮔﺗﮒﺙ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﮒ۳ﮔﺏ۷ |
|----------|----------|----------|----------|------|
| **PyTorch** | ﮒﺙﭦﻛﺝ?| Python?| >=2.0.0 | ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮔ۰ﮔﭘ |
| **Stable-Baselines3** | ﮒﺙﭦﻛﺝ?| Python?| >=2.0.0 | ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﮔ۰ﮔﭘ |
| **DEAP** | ﮒﺙﭦﻛﺝ?| Python?| >=1.4.0 | ﻠﻛﺙ ﻝ؟ﮔﺏﮔ۰ﮔﭘ |
| **pandas** | ﮒﺙﭦﻛﺝ?| Python?| >=2.0.0 | ﮔﺍﮔ؟ﮒ۳ﻝ |
| **numpy** | ﮒﺙﭦﻛﺝ?| Python?| >=1.24.0 | ﮔﺍﮒﺙﻟ؟۰?|
| **scikit-learn** | ﮒﺙﭦﻛﺝ?| Python?| >=1.3.0 | ﮔﭦﮒ۷ﮒ­۵ﻛﺗ ﮒﺓ۴ﮒﺓ |
| **Feast** | ﮒﺙﺎﻛﺝ?| Python?| >=0.30.0 | ﻝﺗﮒﺝﮒ­ﮒ۷ |
| **MLflow** | ﮒﺙﺎﻛﺝ?| Python?| >=2.0.0 | ﮔ۷۰ﮒﻝ؟۰ﻝ |

---

## 3. ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 3.1 APIﮔ۴ﮒ۲ﻟ۶ﻟ

#### 3.1.1 ﻛﺕﭨﮔ۴ﮒ۲ﻝﺎﭨ

```python
from typing import List, Dict, Optional
import pandas as pd
import numpy as np

class AIFactorMiner:
    """AIﮒ ﮒ­ﮔﮔﻛﺕﭨﮔ۴?    
    ﻝﭨﻛﺕﻝ؟۰ﻝﻛﺕﮒ۳۶AIﮔﮔﮒﺙﮔ,ﮔﻛﺝﮒ ﮒ­ﮔﮔﻙﻟﺁﻛﺙﺍﻙﮔﺏ۷ﮒﻝﮒ؟ﮔﺑﮔﭖﻝ۷
    """
    
    def __init__(self, config: Dict):
        """
        ﮒﮒ۶ﮒAIﮒ ﮒ­ﮔﮔ?        
        Args:
            config: ﻠﻝﺛ؟ﮒ­ﮒﺕ,ﮒﮒ،ﻛﺕﮒ۳۶ﮒﺙﮔﻝﮒ?        """
        self.config = config
        self.dl_miner = DeepLearningFactorMiner(config.get('deep_learning', {}))
        self.rl_miner = ReinforcementLearningMiner(config.get('reinforcement_learning', {}))
        self.ga_miner = GeneticAlgorithmMiner(config.get('genetic_algorithm', {}))
        self.evaluator = FactorEvaluator()
        self.registry = FactorRegistry()
        
    def mine_factors(self, 
                    data: pd.DataFrame,
                    target: pd.Series,
                    methods: List[str] = ['deep_learning', 'reinforcement_learning', 'genetic_algorithm'],
                    min_ic: float = 0.03,
                    max_factors: int = 20) -> List[Dict]:
        """
        ﮔﮔﮒ ﮒ­ﻛﺕﭨﮔﺗ?        
        Args:
            data: ﮒﮒ۶ﻝﺗﮒﺝﮔﺍﮔ؟ (index=date, columns=features)
            target: ﻝ؟ﮔ ﮔﭘﻝﻝﮒﭦ?            methods: ﻛﺛﺟﻝ۷ﻝﮔﮔﮔﺗﮔﺏﮒ?            min_ic: ﮔﮒﺍICﻠ?            max_factors: ﮔﮒ۳۶ﻟﺟﮒﮒ ﮒ­ﮔﺍ?            
        Returns:
            ﮒ ﮒ­ﮒﻟ۰۷,ﮔﺁﻛﺕ۹ﮒ ﮒ­ﮒﮒ،:
            - factor_id: ﮒ ﮒ­ID
            - factor_name: ﮒ ﮒ­ﮒﻝ۶ﺍ
            - expression: ﮒ ﮒ­ﻟ۰۷ﻟﺝﺝ?            - ic_mean: ICﮒ?            - ic_ir: ICﻛﺟ۰ﮔﺁﮔﺁﻝ
            - method: ﮔﮔﮔﺗﮔﺏ
            - complexity: ﮒ۳ﮔﮒﭦ۵ﻟﺁ?            - created_at: ﮒﮒﭨﭦﮔﭘﻠﺑ
            
        Raises:
            ValueError: ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻛﺕﮔ­۲?            RuntimeError: ﮔﮔﻟﺟﻝ۷ﮒ۳ﺎﻟﺑ۴
        """
        pass
    
    def evaluate_factor(self,
                       factor_expression: str,
                       data: pd.DataFrame,
                       target: pd.Series) -> Dict:
        """
        ﻟﺁﻛﺙﺍﮒﻛﺕ۹ﮒ ﮒ­
        
        Args:
            factor_expression: ﮒ ﮒ­ﻟ۰۷ﻟﺝﺝ?            data: ﮒﮒ۶ﮔﺍﮔ؟
            target: ﻝ؟ﮔ ﮔﭘﻝ?            
        Returns:
            ﻟﺁﻛﺙﺍﻝﭨﮔﮒ­ﮒﺕ,ﮒﮒ،ICﻙIRﻙﻝﺕﮒﺏﮔ۶ﻝ­ﮔﮔ 
        """
        pass
    
    def register_factor(self, factor: Dict) -> str:
        """
        ﮔﺏ۷ﮒﮒ ﮒ­ﮒﺍﮒ ﮒ­ﮒﭦ
        
        Args:
            factor: ﮒ ﮒ­ﮒ­ﮒﺕ
            
        Returns:
            factor_id: ﮔﺏ۷ﮒﮒﻝﮒ ﮒ­ID
            
        Raises:
            ValueError: ﮒ ﮒ­ﻠ۹ﻟﺁﮒ۳ﺎﻟﺑ۴
        """
        pass
```

#### 3.1.2 ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮒ ﮒ­ﮔﮔ?
```python
class DeepLearningFactorMiner:
    """ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮒ ﮒ­ﮔﮔ?    
    ﻛﺛﺟﻝ۷LSTMﻙTransformerﻙGNNﻝ­ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮔ۷۰ﮒﮔﮔﮒ ?    """
    
    def __init__(self, config: Dict):
        """
        ﮒﮒ۶ﮒﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮔﮔﮒ۷
        
        Args:
            config: ﻠﻝﺛ؟ﮒ­ﮒﺕ
                - model_type: 'lstm' | 'transformer' | 'gnn'
                - hidden_size: ﻠﻟﮒﺎﮒ۳۶?                - num_layers: ﮒﺎﮔﺍ
                - dropout: Dropout?                - learning_rate: ﮒ­۵ﻛﺗ ?                - batch_size: ﮔﺗﮔ؛۰ﮒ۳۶ﮒﺍ
                - epochs: ﻟ؟­ﻝﭨﻟﺛ؟ﮔﺍ
        """
        self.config = config
        self.model = None
        
    def mine_lstm_factors(self,
                         data: pd.DataFrame,
                         target: pd.Series,
                         lookback_window: int = 20) -> List[Dict]:
        """
        ﻛﺛﺟﻝ۷LSTMﮔﮔﮔﭘﮒﭦﮒ ﮒ­
        
        Args:
            data: ﮔﭘﮒﭦﻝﺗﮒﺝﮔﺍﮔ؟
            target: ﻝ؟ﮔ ﮔﭘﻝ?            lookback_window: ﮒﻝﻝ۹ﮒ۲
            
        Returns:
            LSTMﮔﮔﻝﮒ ﮒ­ﮒ?        """
        pass
    
    def mine_transformer_factors(self,
                                 data: pd.DataFrame,
                                 target: pd.Series,
                                 num_heads: int = 8) -> List[Dict]:
        """
        ﻛﺛﺟﻝ۷Transformerﮔﮔﮔﺏ۷ﮔﮒﮒ ?        
        Args:
            data: ﻝﺗﮒﺝﮔﺍﮔ؟
            target: ﻝ؟ﮔ ﮔﭘﻝ?            num_heads: ﮔﺏ۷ﮔﮒﮒ۳ﺑ?            
        Returns:
            Transformerﮔﮔﻝﮒ ﮒ­ﮒ?        """
        pass
    
    def mine_gnn_factors(self,
                        data: pd.DataFrame,
                        correlation_matrix: np.ndarray,
                        target: pd.Series) -> List[Dict]:
        """
        ﻛﺛﺟﻝ۷GNNﮔﮔﮒﺏﻝﺏﭨﮒ ﮒ­
        
        Args:
            data: ﻝﺗﮒﺝﮔﺍﮔ؟
            correlation_matrix: ﻟﭖﻛﭦ۶ﻝﺕﮒﺏﮔ۶ﻝ۸?            target: ﻝ؟ﮔ ﮔﭘﻝ?            
        Returns:
            GNNﮔﮔﻝﮒ ﮒ­ﮒ?        """
        pass
```

#### 3.1.3 ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﮒ ﮒ­ﻛﺙﮒ?
```python
class ReinforcementLearningMiner:
    """ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﮒ ﮒ­ﻛﺙﮒ?    
    ﻛﺛﺟﻝ۷DQNﻙPPOﻙA2Cﻝ­ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﻝ؟ﮔﺏﻛﺙﮒﮒ ﮒ­ﻝﭨ?    """
    
    def __init__(self, config: Dict):
        """
        ﮒﮒ۶ﮒﮒﺙﭦﮒﮒ­۵ﻛﺗ ﻛﺙﮒﮒ۷
        
        Args:
            config: ﻠﻝﺛ؟ﮒ­ﮒﺕ
                - algorithm: 'dqn' | 'ppo' | 'a2c'
                - learning_rate: ﮒ­۵ﻛﺗ ?                - gamma: ﮔﮔ۲ﮒ ﮒ­
                - buffer_size: ﻝﭨﻠ۹ﮒﮔﺝﻝﺙﮒﺎﮒﭦﮒ۳۶?                - batch_size: ﮔﺗﮔ؛۰ﮒ۳۶ﮒﺍ
        """
        self.config = config
        self.model = None
        
    def optimize_factor_weights(self,
                               factors: List[Dict],
                               data: pd.DataFrame,
                               target: pd.Series,
                               optimization_target: str = 'sharpe') -> Dict:
        """
        ﻛﺙﮒﮒ ﮒ­ﮔﻠ
        
        Args:
            factors: ﮒ ﮒ­ﮒﻟ۰۷
            data: ﮒﮒ۶ﮔﺍﮔ؟
            target: ﻝ؟ﮔ ﮔﭘﻝ?            optimization_target: ﻛﺙﮒﻝ؟ﮔ  ('sharpe' | 'return' | 'min_risk')
            
        Returns:
            ﻛﺙﮒﮒﻝﮒ ﮒ­ﮔﻠﮒ­ﮒﺕ
        """
        pass
    
    def dynamic_factor_selection(self,
                                factors: List[Dict],
                                market_state: str) -> List[str]:
        """
        ﮒ۷ﮔﮒ ﮒ­ﻠﮔ۸
        
        Args:
            factors: ﮒ ﮒ­ﮒﻟ۰۷
            market_state: ﮒﺕﮒﭦﻝ?('bull' | 'bear' | 'sideways')
            
        Returns:
            ﻠﻛﺕ­ﻝﮒ ﮒ­IDﮒﻟ۰۷
        """
        pass
```

#### 3.1.4 ﻠﻛﺙ ﻝ؟ﮔﺏﮒ ﮒ­ﮒﻝﺍ?
```python
class GeneticAlgorithmMiner:
    """ﻠﻛﺙ ﻝ؟ﮔﺏﮒ ﮒ­ﮒﻝﺍ?    
    ﻛﺛﺟﻝ۷ﻠﻛﺙ ﻝﺙﻝ۷ﻟ۹ﮒ۷ﮒﻝﺍﮒ ﮒ­ﻟ۰۷ﻟﺝﺝ?    """
    
    def __init__(self, config: Dict):
        """
        ﮒﮒ۶ﮒﻠﻛﺙ ﻝ؟ﮔﺏﮔﮔﮒ۷
        
        Args:
            config: ﻠﻝﺛ؟ﮒ­ﮒﺕ
                - population_size: ﻝ۶ﻝﺝ۳ﮒ۳۶ﮒﺍ
                - generations: ﻟﺟ­ﻛﭨ۲ﻛﭨ۲ﮔﺍ
                - crossover_prob: ﻛﭦ۳ﮒﮔ۵ﻝ
                - mutation_prob: ﮒﮒﺙﮔ۵ﻝ
                - function_set: ﮒﺛﮔﺍ?        """
        self.config = config
        self.custom_functions = self._define_custom_functions()
        
    def mine_expression_factors(self,
                               data: pd.DataFrame,
                               target: pd.Series,
                               max_complexity: int = 50) -> List[Dict]:
        """
        ﮔﮔﻟ۰۷ﻟﺝﺝﮒﺙﮒ ?        
        Args:
            data: ﮒﮒ۶ﻝﺗﮒﺝﮔﺍﮔ؟
            target: ﻝ؟ﮔ ﮔﭘﻝ?            max_complexity: ﮔﮒ۳۶ﮒ۳ﮔﮒﭦ۵
            
        Returns:
            ﻟ۰۷ﻟﺝﺝﮒﺙﮒ ﮒ­ﮒ?        """
        pass
    
    def _define_custom_functions(self) -> Dict:
        """
        ﮒ؟ﻛﺗﻠﮒﻛﺕﻝ۷ﮒﺛﮔﺍ?        
        Returns:
            ﮒﺛﮔﺍﮒ­ﮒﺕ
        """
        return {
            'returns': lambda x: np.diff(x) / x[:-1],
            'volatility': lambda x: np.std(x),
            'zscore': lambda x: (x - np.mean(x)) / np.std(x),
            'rank': lambda x: pd.Series(x).rank().values,
            'delay': lambda x, n=1: np.roll(x, n),
            'ts_mean': lambda x, window=5: pd.Series(x).rolling(window).mean().values,
            'ts_std': lambda x, window=5: pd.Series(x).rolling(window).std().values,
            'ts_corr': lambda x, y, window=20: pd.Series(x).rolling(window).corr(pd.Series(y)).values
        }
```

### 3.2 ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻛﺕﮒﻟ؟؟ﮒ؟?
#### 3.2.1 ﻟﺝﮒ۴ﮔﺍﮔ؟ﮔ ﺙﮒﺙ

```json
{
  "data": {
    "index": ["2024-01-01", "2024-01-02", "..."],
    "columns": ["close", "volume", "pe_ratio", "momentum_20", "..."],
    "values": [[10.5, 1000000, 25.3, 0.05], [...], ...]
  },
  "target": {
    "index": ["2024-01-01", "2024-01-02", "..."],
    "values": [0.02, -0.01, 0.03, ...]
  },
  "config": {
    "methods": ["deep_learning", "genetic_algorithm"],
    "min_ic": 0.03,
    "max_factors": 20,
    "deep_learning": {
      "model_type": "lstm",
      "hidden_size": 128,
      "num_layers": 2,
      "epochs": 100
    },
    "genetic_algorithm": {
      "population_size": 1000,
      "generations": 50,
      "max_complexity": 50
    }
  }
}
```

#### 3.2.2 ﻟﺝﮒﭦﮔﺍﮔ؟ﮔ ﺙﮒﺙ

```json
{
  "status": "success",
  "mined_factors": [
    {
      "factor_id": "AI_DL_001",
      "factor_name": "LSTM_Momentum_20",
      "method": "deep_learning",
      "expression": "lstm_attention(close, volume, window=20)",
      "ic_mean": 0.045,
      "ic_ir": 1.25,
      "ic_std": 0.036,
      "complexity": 35,
      "correlation_with_existing": 0.25,
      "training_loss": 0.012,
      "validation_ic": 0.042,
      "created_at": "2026-04-02T10:30:00Z"
    },
    {
      "factor_id": "AI_GA_001",
      "factor_name": "Genetic_Combo_1",
      "method": "genetic_algorithm",
      "expression": "rank(ts_mean(close, 10) / ts_std(volume, 20))",
      "ic_mean": 0.038,
      "ic_ir": 1.15,
      "ic_std": 0.033,
      "complexity": 28,
      "correlation_with_existing": 0.32,
      "fitness_score": 0.85,
      "created_at": "2026-04-02T10:35:00Z"
    }
  ],
  "summary": {
    "total_mined": 50,
    "passed_filter": 20,
    "registered": 18,
    "failed_validation": 2,
    "mining_duration_seconds": 3600,
    "methods_used": ["deep_learning", "genetic_algorithm"]
  }
}
```

### 3.3 ﮔ۶ﻟﺛﮔﮔ ﻛﺕSLAﻟ۵ﮔﺎ

| ﮔﮔ  | ﻝ؟ﮔ ?| ﮔﭖﻠﮔﺗﮔﺏ | ﮒ۳ﮔﺏ۷ |
|------|--------|----------|------|
| **ﮔﮔﻠﮒﭦ۵** | ?ﮒﺍﮔﭘ/100ﮒ ﮒ­ | ﻝ،ﺁﮒﺍﻝ،ﺁﮔﭘ?| ﮒﮒ،ﻟ؟­ﻝﭨﮒﻟﺁ?|
| **ﮒ ﮒ­ﻟﺑ۷ﻠ** | ICﮒﮒﺙﻗ۴0.03 | ﻝﭨﻟ؟۰ﮔ۲?| ﻠﻟﺟtﮔ۲?p<0.05) |
| **ﮒ ﮒ­ﻝ۷ﺏﮒ؟?* | ICIR?.0 | ICﮔ ﮒ?| ﻝ۷ﺏﮒ؟ﮔ۶ﻟ۵?|
| **ﮒ ﮒ­ﮒﺓ؟ﮒﺙ?* | ﻝﺕﮒﺏﮔ۶ﻗ۳0.5 | ﻛﺕﻝﺍﮔﮒ ﮒ­ﻝﺕﮒ?| ﻠﺟﮒﻠﮒ۳ |
| **GPUﮒ۸ﻝ۷?* | ?0% | nvidia-smiﻝﮔ۶ | ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﻟ؟­ﻝﭨ |
| **ﮒﮒ­ﮒ ﻝ۷** | ?6GB | ﮒﮒ­ﻝﮔ۶ | ﮒﮔ؛۰ﮔﮔﻛﭨﭨﮒ۰ |
| **ﮒﺗﭘﮒﻟﺛﮒ** | ?ﻛﺕ۹ﻛﭨﭨ?| ﮒﮔﭘﻟﺟﻟ۰ | ﻛﺕﮒﮔﮔﮔﺗﮔﺏ |

### 3.4 ﮒ؟ﮒ۷ﻛﺕﻟ؟۳ﻟﺁﮔﭦ?
**ﻟ؟۳ﻟﺁﮔﺗﮒﺙ**: 
- APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁ (ﻛﺕﻝﺍﮔﻝﺏﭨﻝﭨﻝﭨﻛﺕ)
- ﮒﭦﻛﭦﻟ۶ﻟﺎﻝﻟ؟ﺟﻠ؟ﮔ۶?(RBAC)

**ﮔﮔﮔﭦﮒﭘ**:
- ﻝ ﻝ۸ﭘ? ﮒﺁﮒﺁﮒ۷ﮔﮔﻛﭨﭨﮒ۰ﻙﮔ۴ﻝﻝﭨ?- ﻝ؟۰ﻝ? ﮒﺁﮔﺏ۷ﮒﮒ ﮒ­ﻙﮒ ﻠ۳ﮒ ?- ﻝﺏﭨﻝﭨﻝ؟۰ﻝ? ﮒﺁﻠﻝﺛ؟ﮒﮔﺍﻙﻝﮔ۶ﻝﺏﭨ?
**ﮔﺍﮔ؟ﮒ ﮒﺁ**:
- ﻛﺙ ﻟﺝﮒ ﮒﺁ: HTTPS/TLS 1.3
- ﮒ­ﮒ۷ﮒ ﮒﺁ: AES-256 (ﮒ ﮒ­ﻟ۰۷ﻟﺝﺝﮒﺙﮒﮔ۷۰ﮒ)

**ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ**:

---

## 4. ﮔﺍﮔ؟ﮔ۷۰ﮒﻛﺕﮒ­?
### 4.1 ﮔﺍﮔ؟ﮒﭦﻟ۰۷ﻝﭨﮔﻟ؟ﺝﻟ؟۰

#### 4.1.1 ﮒ ﮒ­ﮔﺏ۷ﮒ?(factor_registry)

```sql
CREATE TABLE IF NOT EXISTS factor_registry (
    factor_id VARCHAR(50) PRIMARY KEY,
    factor_name VARCHAR(100) NOT NULL,
    method VARCHAR(20) NOT NULL,  -- 'deep_learning' | 'reinforcement_learning' | 'genetic_algorithm'
    expression TEXT NOT NULL,
    ic_mean DECIMAL(10, 6),
    ic_ir DECIMAL(10, 6),
    ic_std DECIMAL(10, 6),
    complexity INTEGER,
    correlation_with_existing DECIMAL(10, 6),
    status VARCHAR(20) DEFAULT 'experimental',  -- 'experimental' | 'testing' | 'active' | 'deprecated'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    metadata JSON,
    INDEX idx_method (method),
    INDEX idx_status (status),
    INDEX idx_ic_mean (ic_mean)
);
```

#### 4.1.2 ﮔﮔﻛﭨﭨﮒ۰?(mining_tasks)

```sql
CREATE TABLE IF NOT EXISTS mining_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    task_name VARCHAR(100),
    methods JSON,  -- ['deep_learning', 'genetic_algorithm']
    config JSON,
    status VARCHAR(20),  -- 'pending' | 'running' | 'completed' | 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    total_mined INTEGER,
    passed_filter INTEGER,
    registered INTEGER,
    error_message TEXT,
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 4.1.3 ﮒ ﮒ­ﻟﺁﻛﺙﺍﻟ؟ﺍﮒﺛ?(factor_evaluations)

```sql
CREATE TABLE IF NOT EXISTS factor_evaluations (
    evaluation_id VARCHAR(50) PRIMARY KEY,
    factor_id VARCHAR(50),
    task_id VARCHAR(50),
    evaluation_date DATE,
    ic_mean DECIMAL(10, 6),
    ic_ir DECIMAL(10, 6),
    ic_std DECIMAL(10, 6),
    sharpe_ratio DECIMAL(10, 6),
    max_drawdown DECIMAL(10, 6),
    correlation_matrix JSON,
    validation_metrics JSON,
    FOREIGN KEY (factor_id) REFERENCES factor_registry(factor_id),
    FOREIGN KEY (task_id) REFERENCES mining_tasks(task_id),
    INDEX idx_factor_id (factor_id),
    INDEX idx_evaluation_date (evaluation_date)
);
```

### 4.2 ﮔﺍﮔ؟ﮔﭖﻛﺕETLﮔﭖﻝ۷

```
```

**ﮔﺍﮔ؟?*:
- Layer 0: ﮒﮒ۶ﮒﺕﮒﭦﮔﺍﮔ؟(OHLCVﻙﻟﺑ۱ﮒ۰ﮔﺍ?
- Layer 1: ﮔﺕﮔﺑﮒﻝﻝﺗﮒﺝﮔﺍﮔ؟

**ETLﮔ­۴ﻠ۹۳**:
1. **ﮔﺍﮔ؟ﮔﮒ**: ﻛﭨﮔﺍﮔ؟ﮔﭦﻟﺓﮒﮒﮒ۶ﮔﺍﮔ؟
2. **ﻝﺗﮒﺝﮒﺓ۴ﻝ۷**: 
   - ﻝﺙﭦﮒ۳ﺎﮒﺙﮒ۳?ﮒﮒﮒ۰،ﮒ)
   - ﮒﺙﮒﺕﺕﮒﺙﮔ۲?3ﺵﮒﮒ)
   - ﮔ ﮒ?Z-Score)
   - ﻝﺗﮒﺝﮔ?ﮔﮔﺁﮔﮔ ﻙﻟﺑ۱ﮒ۰ﮔﺁ?
3. **AIﮔﮔ**: 
   - ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﻟ؟­ﻝﭨ(LSTM/Transformer/GNN)
   - ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﻛﺙﮒ(DQN/PPO/A2C)
   - ﻠﻛﺙ ﻝ؟ﮔﺏﻟﺟﮒ(DEAP)
4. **ﮒ ﮒ­ﻟﺁﻛﺙﺍ**:
   - IC/IRﻟ؟۰ﻝ؟
   - ﻝﺕﮒﺏﮔ۶ﮒ?   - ﻝ۷ﺏﮒ؟ﮔ۶ﮔ۲?   - ﻟﺟﮔﮒﮔ۲?5. **ﮒ ﮒ­ﻝ­?*:
   - ICﻠﮒﺙﻟﺟ??.03)
   - ﮒ۳ﮔﮒﭦ۵ﮔ۶??0)
   - ﻝﺕﮒﺏﮔ۶ﮒﭨ??.5)
6. **ﮒ ﮒ­ﮔﺏ۷ﮒ**:
   - ﮒﮒ۴ﮒ ﮒ­ﮔﺏ۷ﮒ?   - ﮒ­ﮒ۷ﮒﺍFeastﻝﺗﮒﺝ?   - ﮒﭨﭦﻝ،ﻟ۰ﻝﺙﮒﺏ?
**ﮔﺍﮔ؟ﻟﺑ۷ﻠﮔ۲ﮔ۴ﻟ۶?*:
- ﮔﺍﮔ؟ﮒ؟ﮔﺑ? ﻝﺙﭦﮒ۳ﺎ?5%
- ﮔﺍﮔ؟ﮒﻝ۰؟? ﮒﺙﮒﺕﺕﮒﺙﮔﺁ?1%
- ﮔﺍﮔ؟ﻛﺕﻟ? ﮔﭘﻠﺑﮔﺏﮒﺁﺗ?- ﮔﺍﮔ؟ﮔﭘﮔ? T+1ﮔﺑﮔﺍ

### 4.3 ﻝﺙﮒ­ﻝ­ﻝ۴ﻛﺕﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﮔﺗ?
**ﻝﺙﮒ­ﻝﺎﭨﮒ**: 
- ﮒﮒ­ﻝﺙﮒ­: Redis (ﻟ؟­ﻝﭨﻛﺕ­ﻠﺑﻝﭨﮔ)
- ﮒﮒﺕﮒﺙﻝﺙ? Redis Cluster (ﮒ ﮒ­ﮔﺍﮔ؟)

**ﻝﺙﮒ­ﻝ­ﻝ۴**:
- **ﮒﻝ۸ﺟ?*: ﮒ ﮒ­ﮔﺏ۷ﮒﮔﭘﮒﮔ­۴ﮔﺑﮔﺍﻝﺙ?
**ﻛﺕﻟﺑﮔ۶ﻛﺟ?*:
- **ﮔﻝﭨﻛﺕﻟ?*: ﮒ ﮒ­ﮔﺍﮔ؟ﮔﺑﮔﺍ?ﮒﻠﮒﮒﮔ­۴ﮒﺍﮔﮔﻟ?- **ﮒﺙﭦﻛﺕﻟ?*: ﮒ ﮒ­ﮔﺏ۷ﮒﮔﻛﺛﻛﺛﺟﻝ۷ﮒﮒﺕﮒﺙﻠ

**ﮒ۳ﺎﮔﻝ­ﻝ۴**:
- **ﻛﺕﭨﮒ۷ﮒ۳ﺎﮔ**: ﮒ ﮒ­ﻝﭘﮔﮒﮔﺑﮔﭘﻛﺕﭨﮒ۷ﮔﺕﻠ۳ﻝﺙﮒ­
- **ﻟ۱،ﮒ۷ﮒ۳ﺎﮔ**: TTLﮒﺍﮔﻟ۹ﮒ۷ﮔﺕﻠ۳

### 4.4 ﮒ۳ﻛﭨﺛﻛﺕﮔ۱ﮒ۳ﮔﺗ?
**ﮒ۳ﻛﭨﺛﻝ­ﻝ۴**:
- **ﮒ۷ﻠﮒ۳ﻛﭨﺛ**: ﮔﺁﮒ۷ﮔ۴ﮒ??- **ﮒ۱ﻠﮒ۳ﻛﭨﺛ**: ﮔﺁﮔ۴ﮒﮔ۷2?- **ﮒ؟ﮔﭘﮒ۳ﻛﭨﺛ**: ﮒ ﮒ­ﮔﺏ۷ﮒﮔﻛﺛﮒ؟ﮔﭘﮒﮔ­۴ﮒﺍﮒ۳?
**ﮔ۱ﮒ۳ﻝﺗﻝ؟?RPO)**: ?ﮒﺍﮔﭘ

**ﮔ۱ﮒ۳ﮔﭘﻠﺑﻝ؟ﮔ (RTO)**: ?ﮒﺍﮔﭘ

**ﻝﺝﻠﺝﮔ۱ﮒ۳**:
- ﻛﺕﭨﮒ۳ﮔﺍﮔ؟ﻛﺕ­ﮒﺟ: ﮒﺙﮒﺍﮒﮔﺑﭨ
- ﮔﺍﮔ؟ﮒﮔ­۴: ﮒ؟ﮔﭘﮒﺙﮔ­۴ﮒ۳ﮒﭘ
- ﮔﻠﮒﮔ۱: ﻟ۹ﮒ۷ﮔ۲?ﮔﮒ۷ﮒﮔ۱

---

## 5. ﻝ؟ﮔﺏﮒ؟ﻝﺍﻟﺁﺑﮔ

### 5.1 ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮒ ﮒ­ﮔﮔﻝ؟ﮔﺏ

#### 5.1.1 LSTMﮒ ﮒ­ﮔﮔ

**ﻝ؟ﮔﺏﮒﻝ**:
ﻛﺛﺟﻝ۷LSTMﻝﺛﻝﭨﮒ­۵ﻛﺗ ﮔﭘﮒﭦﮔﺍﮔ؟ﻝﻠﺟﮔﻛﺝﻟﭖﮒﺏ?ﮔﮒﮔﺛﮒ۷ﻝAlphaﮒ ﮒ­

**ﮔﺍﮒ­۵ﮒ؛ﮒﺙ**:
```
ﻠﮒﺟ? f_t = ﺵ(W_f ﺡﺓ [h_{t-1}, x_t] + b_f)
ﻟﺝﮒ۴? i_t = ﺵ(W_i ﺡﺓ [h_{t-1}, x_t] + b_i)
ﮒﻠ? Cﮊ_t = tanh(W_C ﺡﺓ [h_{t-1}, x_t] + b_C)
ﻝﭨﻟﻝ? C_t = f_t * C_{t-1} + i_t * Cﮊ_t
ﻟﺝﮒﭦ? o_t = ﺵ(W_o ﺡﺓ [h_{t-1}, x_t] + b_o)
ﻠﻟﻝ? h_t = o_t * tanh(C_t)
ﮒ ﮒ­? factor_t = W_factor ﺡﺓ h_t + b_factor
```

**ﮔﭘﻠﺑﮒ۳ﮔ?*: O(n ﺡﺓ dﺡﺎ) (n=ﮒﭦﮒﻠﺟﮒﭦ۵, d=ﻠﻟﮒﺎﮒ۳۶?

**ﻝ۸ﭦﻠﺑﮒ۳ﮔ?*: O(dﺡﺎ) (ﮔ۷۰ﮒﮒﮔﺍ)

**ﮒﮔﺍﻠﻝﺛ؟**:
```yaml
lstm_config:
  hidden_size: 128
  num_layers: 2
  dropout: 0.2
  learning_rate: 0.001
  batch_size: 64
  epochs: 100
  early_stopping_patience: 10
  lookback_window: 20
```

#### 5.1.2 Transformerﮒ ﮒ­ﮔﮔ

**ﻝ؟ﮔﺏﮒﻝ**:
ﻛﺛﺟﻝ۷Transformerﻝﻟ۹ﮔﺏ۷ﮔﮒﮔﭦﮒﭘﮔﮔﻝﺗﮒﺝﻠﺑﻝﮒ۳ﮔﮒﺏ?
**ﮔﺍﮒ­۵ﮒ؛ﮒﺙ**:
```
ﮔﺏ۷ﮔ? Attention(Q, K, V) = softmax(QK^T / ﻗd_k) V
ﮒ۳ﮒ۳ﺑﮔﺏ۷ﮔ? MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O
ﮒﭘﻛﺕ­ head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
ﮒ ﮒ­? factor = Linear(MultiHead(X, X, X))
```

**ﮔﭘﻠﺑﮒ۳ﮔ?*: O(nﺡﺎ ﺡﺓ d) (n=ﮒﭦﮒﻠﺟﮒﭦ۵, d=ﻝﺗﮒﺝﻝﭨﺑﮒﭦ۵)

**ﻝ۸ﭦﻠﺑﮒ۳ﮔ?*: O(nﺡﺎ + dﺡﺎ)

**ﮒﮔﺍﻠﻝﺛ؟**:
```yaml
transformer_config:
  d_model: 128
  nhead: 8
  num_encoder_layers: 3
  dim_feedforward: 512
  dropout: 0.1
  learning_rate: 0.0001
  batch_size: 32
  epochs: 150
```

### 5.2 ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﮒ ﮒ­ﻛﺙﮒﻝ؟ﮔﺏ

#### 5.2.1 DQNﮒ ﮒ­ﮔﻠﻛﺙﮒ

**ﻝ؟ﮔﺏﮒﻝ**:
ﻛﺛﺟﻝ۷ﮔﺓﺎﮒﭦ۵Qﻝﺛﻝﭨﮒ­۵ﻛﺗ ﮔﻛﺙﻝﮒ ﮒ­ﮔﻠﮒﻠﻝ­ﻝ۴

**ﮔﺍﮒ­۵ﮒ؛ﮒﺙ**:
```
Qﮒﺙﮒﺛ? Q(s, a; ﺳﺕ) ?r + ﺳﺏ ﺡﺓ max_{a'} Q(s', a'; ﺳﺕ')
ﮔﮒ۳ﺎﮒﺛﮔﺍ: L(ﺳﺕ) = E[(r + ﺳﺏ ﺡﺓ max_{a'} Q(s', a'; ﺳﺕ') - Q(s, a; ﺳﺕ))ﺡﺎ]
ﮒ۷ﻛﺛ: ﮒ ﮒ­ﮔﻠﻟﺍﮔﺑ
ﻝ? ﮒﺛﮒﮒ ﮒ­ﻝﭨﮒﻟ۰۷ﻝﺍ
ﮒ۴ﮒﺎ: ﮒ۳ﮔ؟ﮔﺁﻝﮔﮒ
```

**ﮔﭘﻠﺑﮒ۳ﮔ?*: O(n ﺡﺓ m) (n=ﻟ؟­ﻝﭨﮔ­۴ﮔﺍ, m=ﻝﭨﻠ۹ﮒﮔﺝﻝﺙﮒﺎﮒﭦﮒ۳۶?

**ﻝ۸ﭦﻠﺑﮒ۳ﮔ?*: O(m) (ﻝﭨﻠ۹ﮒﮔﺝﻝﺙﮒﺎ?

**ﮒﮔﺍﻠﻝﺛ؟**:
```yaml
dqn_config:
  learning_rate: 0.0001
  gamma: 0.99
  buffer_size: 100000
  batch_size: 64
  target_update_freq: 1000
  exploration_fraction: 0.1
  exploration_final_eps: 0.01
```

#### 5.2.2 PPOﮒ ﮒ­ﻠﮔ۸ﻛﺙﮒ

**ﻝ؟ﮔﺏﮒﻝ**:

**ﮔﺍﮒ­۵ﮒ؛ﮒﺙ**:
```
ﻝ­ﻝ۴ﮔ۱ﺁﮒﭦ۵: L^{CLIP}(ﺳﺕ) = E[min(r_t(ﺳﺕ) ﺡﺓ A_t, clip(r_t(ﺳﺕ), 1-ﺳﭖ, 1+ﺳﭖ) ﺡﺓ A_t)]
ﮒﭘﻛﺕ­ r_t(ﺳﺕ) = ﺵ_ﺳﺕ(a_t | s_t) / ﺵ_ﺳﺕ_old(a_t | s_t)
ﻛﺙﮒﺟﮒﺛﮔﺍ: A_t = Q(s_t, a_t) - V(s_t)
```

**ﮔﭘﻠﺑﮒ۳ﮔ?*: O(n ﺡﺓ k) (n=ﻟ؟­ﻝﭨﮔ­۴ﮔﺍ, k=epoch?

**ﻝ۸ﭦﻠﺑﮒ۳ﮔ?*: O(b) (b=batch size)

**ﮒﮔﺍﻠﻝﺛ؟**:
```yaml
ppo_config:
  learning_rate: 0.0003
  n_steps: 2048
  batch_size: 64
  n_epochs: 10
  gamma: 0.99
  gae_lambda: 0.95
  clip_range: 0.2
  ent_coef: 0.01
```

### 5.3 ﻠﻛﺙ ﻝ؟ﮔﺏﮒ ﮒ­ﮒﻝﺍﻝ؟ﮔﺏ

#### 5.3.1 ﻠﻛﺙ ﻝﺙﻝ۷ﮒ ﮒ­ﮔﮔ

**ﻝ؟ﮔﺏﮒﻝ**:
ﻛﺛﺟﻝ۷ﻠﻛﺙ ﻝﺙﻝ۷ﻟ۹ﮒ۷ﻟﺟﮒﮒ ﮒ­ﻟ۰۷ﻟﺝﺝﮒﺙﮔ 

**ﮔﺍﮒ­۵ﮒ؛ﮒﺙ**:
```
ﻠﮒﭦﮒﭦ۵ﮒﺛ? fitness = IC_mean - ﺳﭨ ﺡﺓ complexity
ﻠﮔ۸: tournament_selection(size=7)
ﻛﭦ۳ﮒ: subtree_crossover(p=0.7)
ﮒﮒﺙ: subtree_mutation(p=0.1) + hoist_mutation(p=0.05) + point_mutation(p=0.1)
```

**ﮔﭘﻠﺑﮒ۳ﮔ?*: O(g ﺡﺓ p ﺡﺓ n) (g=ﻛﭨ۲ﮔﺍ, p=ﻝ۶ﻝﺝ۳ﮒ۳۶ﮒﺍ, n=ﮔﺍﮔ؟ﻝﺗﮔﺍ)

**ﻝ۸ﭦﻠﺑﮒ۳ﮔ?*: O(p ﺡﺓ m) (m=ﮒﺗﺏﮒﮔ ﻟﻝﺗﮔﺍ)

**ﮒﮔﺍﻠﻝﺛ؟**:
```yaml
genetic_config:
  population_size: 1000
  generations: 50
  tournament_size: 7
  p_crossover: 0.7
  p_subtree_mutation: 0.1
  p_hoist_mutation: 0.05
  p_point_mutation: 0.1
  parsimony_coefficient: 0.01
  max_samples: 0.9
  stopping_criteria: 0.01
```

**ﮒﺛﮔﺍﻠﮒ؟?*:
```python
function_set = {
    'arithmetic': ['add', 'sub', 'mul', 'div', 'sqrt', 'log', 'abs', 'neg', 'inv'],
    'trigonometric': ['sin', 'cos', 'tan'],
    'custom': ['returns', 'volatility', 'zscore', 'rank', 'delay', 
               'ts_mean', 'ts_std', 'ts_corr', 'ts_max', 'ts_min']
}
```

### 5.4 ﮒ ﮒ­ﻟﺁﻛﺙﺍﻝ؟ﮔﺏ

#### 5.4.1 ICﻟ؟۰ﻝ؟

**ﮔﺍﮒ­۵ﮒ؛ﮒﺙ**:
```
IC_t = corr(factor_value_t, return_{t+1})
IC_mean = mean(IC_t)
IC_std = std(IC_t)
ICIR = IC_mean / IC_std
```

**ﮔﺝﻟﮔ۶ﮔ۲?*:
```
tﻝﭨﻟ؟۰? t = IC_mean / (IC_std / ﻗn)
p? p = 2 ﺡﺓ (1 - CDF(|t|))
ﮔﺝﻟﮔ۶ﮔ ? p < 0.05
```

#### 5.4.2 ﮒ ﮒ­ﻝﺕﮒﺏﮔ۶ﮒ?
**ﮔﺍﮒ­۵ﮒ؛ﮒﺙ**:
```
ﻝﺕﮒﺏﮔ۶ﻝ۸? R = corr(F) (Fﻛﺕﭦﮒ ﮒ­ﻝ۸?
ﮒﭨﻠﮔ ﮒ: |R_{ij}| < 0.5 (i ?j)
```

#### 5.4.3 ﻟﺟﮔﮒﮔ۲?
**ﮔﺗﮔﺏ**: Walk-Forwardﻠ۹ﻟﺁ
```
ﻟ؟­ﻝﭨ? [0, T_train]
ﻠ۹ﻟﺁ? [T_train, T_train + T_val]
ﮔﭖﻟﺁ? [T_train + T_val, T]
ﮒ۳ﮒ؟: IC_test > IC_val * 0.8 (ﮔ۹ﻟﺟﮔﮒ)
```

---

## 6. ﮒ؟ﮔﺛﮔﮔﺁﮔ 

### 6.1 ﻟﺁ­ﻟ۷ﻛﺕﮔ۰?
| ﻝﺎﭨﮒ، | ﮔﮔﺁﻠﮒ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﻝ?|
|------|---------|---------|------|
| **ﻝﺙﻝ۷ﻟﺁ­ﻟ۷** | Python | >=3.9 | ﻛﺕﭨﻟ۵ﮒﺙﮒﻟﺁ­ﻟ۷ |
| **ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮔ۰ﮔﭘ** | PyTorch | >=2.0.0 | LSTM/Transformer/GNN |
| **ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﮔ۰ﮔﭘ** | Stable-Baselines3 | >=2.0.0 | DQN/PPO/A2C |
| **ﻠﻛﺙ ﻝ؟ﮔﺏﮔ۰ﮔﭘ** | DEAP | >=1.4.0 | ﻠﻛﺙ ﻝﺙﻝ۷ |
| **ﮔﺍﮔ؟ﮒ۳ﻝ** | pandas | >=2.0.0 | ﮔﺍﮔ؟ﮒ۳ﻝ |
| **ﮔﺍﮒﺙﻟ؟۰?* | numpy | >=1.24.0 | ﮔﺍﮒﺙﻟ؟۰?|
| **ﮔﭦﮒ۷ﮒ­۵ﻛﺗ ** | scikit-learn | >=1.3.0 | ﻟﺁﻛﺙﺍﮔﮔ  |
| **ﻝﺗﮒﺝﮒ­ﮒ۷** | Feast | >=0.30.0 | ﮒ ﮒ­ﻝﺗﮒﺝ?|
| **ﮔ۷۰ﮒﻝ؟۰ﻝ** | MLflow | >=2.0.0 | ﮔ۷۰ﮒﻝﮔ؛ﻝ؟۰ﻝ |

### 6.2 ﻝ؛؛ﻛﺕﮔﺗﻛﺝ?
```txt
# requirements.txt
torch>=2.0.0
stable-baselines3>=2.0.0
deap>=1.4.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
feast>=0.30.0
mlflow>=2.0.0
redis>=4.0.0
sqlalchemy>=2.0.0
pyyaml>=6.0
tqdm>=4.65.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### 6.3 ﻝﺁﮒ۱ﻟ۵ﮔﺎ

**ﻝ۰؛ﻛﭨﭘﻟ۵ﮔﺎ**:
- CPU: ?6ﮔ ﺕﮒﺟ
- ﮒﮒ­: ?4GB
- GPU: NVIDIA GPU (?2GBﮔﺝﮒ­,ﮔ۷ﻟRTX 4090ﮔA100)
- ﮒ­ﮒ۷: ?00GB SSD

**ﻟﺛﺁﻛﭨﭘﻝﺁﮒ۱**:
- ﮔﻛﺛﻝﺏﭨﻝﭨ: Ubuntu 22.04 LTS / Windows 11
- CUDA: >=11.8
- cuDNN: >=8.6
- Python: >=3.9

**ﮒﺙﮒﻝﺁ?*:
- IDE: VSCode / PyCharm
- ﻝﮔ؛ﮔ۶ﮒﭘ: Git
- ﮒ؟ﺗﮒ۷? Docker
- ﻝﺙﮔ: Kubernetes (ﮒ?

### 6.4 ﻠ۷ﻝﺛﺎﮔﭘﮔ

```

---

## 7. ﮔﭖﻟﺁﻝ­ﻝ۴

### 7.1 ﮒﮒﮔﭖﻟﺁ

**ﮔﭖﻟﺁﻟﮒﺑ**:
- ﮒ ﮒ­ﮔﺏ۷ﮒﮒﮒ­?
**ﮔﭖﻟﺁﮔ۰ﮔﭘ**: pytest

**ﮔﭖﻟﺁﻟ۵ﻝﻝﻟ۵?*: ?0%

**ﻝ۳ﭦﻛﺝﮔﭖﻟﺁﻝ۷ﻛﺝ**:
```python
def test_lstm_factor_mining():
    """ﮔﭖﻟﺁLSTMﮒ ﮒ­ﮔﮔ"""
    miner = DeepLearningFactorMiner(config)
    data = pd.DataFrame(...)
    target = pd.Series(...)
    
    factors = miner.mine_lstm_factors(data, target)
    
    assert len(factors) > 0
    assert all(f['ic_mean'] >= 0.03 for f in factors)
    assert all(f['method'] == 'deep_learning' for f in factors)
```

### 7.2 ﻠﮔﮔﭖﻟﺁ

**ﮔﭖﻟﺁﻟﮒﺑ**:
- ﻝ،ﺁﮒﺍﻝ،ﺁﮒ ﮒ­ﮔﮔﮔﭖ?- ﮒ۳ﮒﺙﮔﮒﮒﮒﺓ۴?- ﮒ ﮒ­ﮔﺏ۷ﮒﮒﺍﻝﺗﮒﺝﮒﭦ
- APIﮔ۴ﮒ۲ﻟﺍﻝ۷

**ﮔﭖﻟﺁﻝﺁﮒ۱**: Docker Compose

**ﮔﭖﻟﺁﮒﭦﮔﺁ**:
1. ﮒ؟ﮔﺑﮔﮔﮔﭖﻝ۷ﮔﭖﻟﺁ
2. ﮒﺗﭘﮒﮔﮔﻛﭨﭨﮒ۰ﮔﭖﻟﺁ
3. ﮒﺙﮒﺕﺕﮒ۳ﻝﮔﭖﻟﺁ
4. ﮔ۶ﻟﺛﮒﮒﮔﭖﻟﺁ

### 7.3 ﮔ۶ﻟﺛﮔﭖﻟﺁ

**ﮔﭖﻟﺁﮔﮔ **:
- ﮔﮔﻠﮒﭦ۵: ?ﮒﺍﮔﭘ/100ﮒ ﮒ­
- GPUﮒ۸ﻝ۷? ?0%
- ﮒﮒ­ﮒ ﻝ۷: ?6GB
- ﮒﺗﭘﮒﻟﺛﮒ: ?ﻛﺕ۹ﻛﭨﭨ?
**ﮔﭖﻟﺁﮒﺓ۴ﮒﺓ**: Locust + Prometheus

**ﮔﭖﻟﺁﮒﭦﮔﺁ**:
```yaml
performance_test:
  concurrent_users: 10
  spawn_rate: 2
  run_time: 1h
  tasks:
    - mine_factors_deep_learning: 40%
    - mine_factors_genetic: 40%
    - evaluate_factor: 20%
```

### 7.4 ﮒ؟ﮒ۷ﮔﭖﻟﺁ

**ﮔﭖﻟﺁﻟﮒﺑ**:
- APIﻟ؟۳ﻟﺁﮒﮔ?- SQLﮔﺏ۷ﮒ۴ﻠﺎﮔ۳
- XSSﻠﺎﮔ۳
- ﮔﺍﮔ؟ﮒ ﮒﺁﻠ۹ﻟﺁ
- ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟﮒ؟ﮔﺑ?
**ﮔﭖﻟﺁﮒﺓ۴ﮒﺓ**: OWASP ZAP

---

## 8. ﻠ۲ﻠ۸ﻛﺕﻝﭦ۵?
### 8.1 ﮔﮔﺁﻠ۲?
| ﻠ۲ﻠ۸?| ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶ | ﮒﺛﺎﮒﻟﮒﺑ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |
|--------|---------|---------|---------|
| **GPUﻟﭖﮔﭦﻛﺕﻟﭘﺏ** | P1 | ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﻟ؟­ﻝﭨ | ﻛﭦGPUﮒﺙﺗﮔ۶ﮔ۸ﮒﺎﻙﻛﭨﭨﮒ۰ﻠ?|
| **ﻟﺟﮔﮒﻠ۲?* | P1 | ﮒ ﮒ­ﻟﺑ۷ﻠ | Walk-Forwardﻠ۹ﻟﺁﻙﮔ­۲ﮒﮒ |
| **ﻟ؟۰ﻝ؟ﮒ۳ﮔﮒﭦ۵ﻠ،** | P2 | ﮔﮔﻠﮒﭦ۵ | ﮒﺗﭘﻟ۰ﻟ؟۰ﻝ؟ﻙﻝ؟ﮔﺏﻛﺙ?|
| **ﮔﺍﮔ؟ﻟﺑ۷ﻠﻠ؟ﻠ۱** | P2 | ﮒ ﮒ­ﮒﻝ۰؟?| ﮔﺍﮔ؟ﻟﺑ۷ﻠﮔ۲ﮔ۴ﻙﮒﺙﮒﺕﺕﮔ۲?|
| **ﮔ۷۰ﮒﮒﺁﻟ۶۲ﻠﮔ۶ﮒﺓ؟** | P3 | ﮒ ﮒ­ﻛﺟ۰ﻛﭨﭨ?| SHAPﮒﺙﮒﮔﻙﮒﺁﻟ۶ﮒ |

### 8.2 ﮒ؟ﮔﺛﻠ۲ﻠ۸

| ﻠ۲ﻠ۸?| ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶ | ﮒﺛﺎﮒﻟﮒﺑ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |
|--------|---------|---------|---------|
| **ﮔﮔﺁﮔ ﮒ­۵ﻛﺗ ﮔﺎﻝﭦﺟ** | P1 | ﮒﺙﮒﻟﺟ?| ﮒﺗﻟ؟­ﻙﮔﮔ۰۲ﻙﻛﭨ۲ﻝ ﮒ۳?|
| **GPUﮔﮔ؛?* | P2 | ﻠ۰ﺗﻝ؟ﻠ۱ﻝ؟ | ﻛﭦGPUﮔﻠﻛﺛﺟﻝ۷ﻙﮔﺓﺓﮒﻛﭦ |
| **ﻠﮔﮒ۳ﮔ?* | P2 | ﻝﺏﭨﻝﭨﻝ۷ﺏﮒ؟?| ﮔﺕﻟﺟﮒﺙﻠﮔﻙﮒﮒﮔﭖ?|
| **ﻛﭦﭦﮔﻝ­ﻝﺙﭦ** | P3 | ﻠ۰ﺗﻝ؟ﻟﺟﮒﭦ۵ | ﮒ۳ﻠ۷ﮒﻛﺛﻙAIﻟﺝﮒ۸ﮒﺙ?|

### 8.3 ﻝﭦ۵ﮔﮔ۰ﻛﭨﭘ

**ﮔﮔﺁﻝﭦ۵?*:
- ﮒﺟﻠ۰ﭨﮒﺙﮒ؟ﺗﻝﺍﮔLayer 0-11ﮔﭘﮔ
- ﮒﺟﻠ۰ﭨﻛﺛﺟﻝ۷Python 3.9+
- ﮒﺟﻠ۰ﭨﮔﺁﮔGPUﮒ?- ﮒﺟﻠ۰ﭨﻝ؛۵ﮒﮔﺍﮔ؟ﮒ؟ﮒ۷ﻟ۶ﻟ

**ﻛﺕﮒ۰ﻝﭦ۵ﮔ**:
- ﮒ ﮒ­ﮔﮔﮒ۷ﮔ?ﮒﺍﮔﭘ
- ﮒ ﮒ­ICﮒﮒﺙﻗ۴0.03
- ﮒ ﮒ­ﻛﺕﻝﺍﮔﮒ ﮒ­ﻝﺕﮒﺏﮔ۶ﻗ۳0.5
- ﮒﮔ؛۰ﮔﮔﮔﮔ؛?00?
**ﮒﻟ۶ﻝﭦ۵ﮔ**:
- ﮔﺍﮔ؟ﻛﺛﺟﻝ۷ﻝ؛۵ﮒﻝﻝ؟۰ﻟ۵ﮔﺎ
- ﮒ ﮒ­ﻟ۰۷ﻟﺝﺝﮒﺙﮒﺁﻟ۶۲ﻠ
- ﮔ۷۰ﮒﻟ؟­ﻝﭨﻟﺟﻝ۷ﮒﺁﮒ؟۰?- ﮒ ﮒ­ﮔﺏ۷ﮒﻠﻛﭦﭦﮒﺓ۴ﮒ؟۰ﮔ ﺕ

---

## 9. ﻠ۹ﮔﭘﮔ ﮒ

### 9.1 ﮒﻟﺛﻠ۹ﮔﭘﮔ ﮒ

| ﮒﻟﺛ?| ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|--------|---------|---------|
| **ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮔﮔ** | ﮔﮒﮔﮔ?0ﻛﺕ۹IC?.03ﻝﮒ ?| ﮒﮒﮔﭖﻟﺁ+ﻠﮔﮔﭖﻟﺁ |
| **ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﻛﺙﮒ** | ﮒ ﮒ­ﻝﭨﮒﮒ۳ﮔ؟ﮔﺁﻝﮔﮒ?0% | ﮒﮔﭖﻠ۹ﻟﺁ |
| **ﻠﻛﺙ ﻝ؟ﮔﺏﮒﻝﺍ** | ﮔﮒﮒﻝﺍ?ﻛﺕ۹ﮒﮒﮒ ﮒ­ﻟ۰۷ﻟﺝﺝﮒﺙ | ﻛﭦﭦﮒﺓ۴ﮒ؟۰ﮔ۴ |
| **ﮒ ﮒ­ﻟﺁﻛﺙﺍ** | ICﻟ؟۰ﻝ؟ﮒﻝ۰؟?00% | ﮒﮒﮔﭖﻟﺁ |
| **ﮒ ﮒ­ﮔﺏ۷ﮒ** | ﮔﺏ۷ﮒﮔﮒﻝﻗ۴95% | ﻠﮔﮔﭖﻟﺁ |
| **APIﮔ۴ﮒ۲** | ﮔﮔﮔ۴ﮒ۲ﮒﮒﭦﮔﭘﻠﺑﻗ۳100ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |

### 9.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘﮔ ﮒ

| ﮔ۶ﻟﺛﮔﮔ  | ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|---------|---------|---------|
| **ﮔﮔﻠﮒﭦ۵** | ?ﮒﺍﮔﭘ/100ﮒ ﮒ­ | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **GPUﮒ۸ﻝ۷?* | ?0% | ﻝﮔ۶ﻝﺏﭨﻝﭨ |
| **ﮒﮒ­ﮒ ﻝ۷** | ?6GB | ﻝﮔ۶ﻝﺏﭨﻝﭨ |
| **ﮒﺗﭘﮒﻟﺛﮒ** | ?ﻛﺕ۹ﻛﭨﭨﮒ۰ﮒﮔﭘﻟﺟ?| ﮒﮒﮔﭖﻟﺁ |
| **ﮒﺁﻝ۷?* | ?9.5% | ﻝﮔ۶ﻝﺏﭨﻝﭨ |

### 9.3 ﻟﺑ۷ﻠﻠ۹ﮔﭘﮔ ﮒ

| ﻟﺑ۷ﻠﮔﮔ  | ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|---------|---------|---------|
| **ﻛﭨ۲ﻝ ﻟ۵ﻝ?* | ?0% | pytest-cov |
| **ﻛﭨ۲ﻝ ﻟﺑ۷ﻠ** | ﮔ ﻛﺕ۴ﻠﻛﭨ۲ﻝ ﮒﺙ?| SonarQube |
| **ﮔﮔ۰۲ﮒ؟ﮔﺑ?* | 100%ﮔ۴ﮒ۲ﮔﮔ?| ﻛﭦﭦﮒﺓ۴ﮒ؟۰ﮔ۴ |
| **ﮒ؟ﮒ۷?* | ﮔ ﻠ،ﮒﺎﮔﺙ?| OWASP ZAP |
| **ﮒﺁﻝﭨﺑﮔ?* | ﮔ۷۰ﮒﮒﻟ؟ﺝﻟ؟۰ﻙﻛﺛﻟ۵ﮒ | ﮔﭘﮔﮒ؟۰ﮔ۴ |

### 9.4 ﮔﮔ۰۲ﻠ۹ﮔﭘﮔ ﮒ

| ﮔﮔ۰۲ﻝﺎﭨﮒ | ﻠ۹ﮔﭘﮔ ﮒ | ﻛﭦ۳ﻛﭨ?|
|---------|---------|--------|
| **ﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵** | ﮒ؟ﮔﺑﻟﺁ۵ﻝﭨﻙﻝ؛۵ﮒﮔ۷۰?| ﮔ؛ﮔ?|
| **APIﮔﮔ۰۲** | ﮔﮔﮔ۴ﮒ۲ﮔﮔﮔ۰۲ | Swagger UI |
| **ﻠ۷ﻝﺛﺎﮔﮔ۰۲** | ﻟﺁ۵ﻝﭨﻠ۷ﻝﺛﺎﮔ­۴ﻠ۹۳ | Markdownﮔﮔ۰۲ |
| **ﻝ۷ﮔﺓﮔﮒ** | ﮔﻛﺛﮔ­۴ﻠ۹۳ﮔﺕﮔﺍ | PDFﮔﮔ۰۲ |
| **ﮔﭖﻟﺁﮔ۴ﮒ** | ﻟ۵ﻝﮔﮔﮔﭖﻟﺁﮒﭦ?| PDFﮔ۴ﮒ |

---

## 10. ﮒ؟ﮔﺛﻟﺓﺁﻝﭦﺟ?
### 10.1 Phase 1: ﮒﭦﻝ۰ﮔ۰ﮔﭘﮔ­ﮒﭨﭦ (Week 1-2)

**ﻝ؟ﮔ **: ﮔ­ﮒﭨﭦAIﮒ ﮒ­ﮔﮔﮔ۷۰ﮒﻝﮒﭦﻝ۰ﮔ۰ﮔﭘ

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒﮒﭨﭦﻠ۰ﺗﻝ؟ﻝﭨﮔﮒﻠﻝﺛ؟ﮔ?- [ ] ﮒ؟ﻝﺍAIFactorMinerﻛﺕﭨﮔ۴ﮒ۲ﻝﺎﭨ
- [ ] ﮒ؟ﻝﺍFactorEvaluatorﻟﺁﻛﺙﺍ?- [ ] ﮒ؟ﻝﺍFactorRegistryﮔﺏ۷ﮒ?- [ ] ﮔ­ﮒﭨﭦﮔﺍﮔ؟ﮒﭦﻟ۰۷ﻝﭨﮔ
- [ ] ﻠﻝﺛ؟Feastﻝﺗﮒﺝﮒ­ﮒ۷
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁﮔ۰ﮔﭘ

**ﻛﭦ۳ﻛﭨ?*:
- ﻠ۰ﺗﻝ؟ﻛﭨ۲ﻝ ﮔ۰ﮔﭘ
- ﮔﺍﮔ؟ﮒﭦﻟ۰۷ﻝﭨﮔ
- ﮒﮒﮔﭖﻟﺁﮔ۰ﮔﭘ
- ﮔﮔﺁﮔﮔ۰۲ﮒ?
**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﮔﮔﮒﭦﻝ۰ﻝﺎﭨﮒﺁﮒ؟ﻛﺝ?- ﮔﺍﮔ؟ﮒﭦﻟ۰۷ﮒﮒﭨﭦﮔﮒ
- ﮒﮒﮔﭖﻟﺁﮔ۰ﮔﭘﻟﺟﻟ۰ﮔ­۲ﮒﺕﺕ

### 10.2 Phase 2: ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮒﺙﮔﮒ؟ﻝﺍ (Week 3-4)

**ﻝ؟ﮔ **: ﮒ؟ﻝﺍLSTMﮒTransformerﮒ ﮒ­ﮔﮔ

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍDeepLearningFactorMiner?- [ ] ﮒ؟ﻝﺍLSTMﮒ ﮒ­ﮔﮔﮔ۷۰ﮒ
- [ ] ﮒ؟ﻝﺍTransformerﮒ ﮒ­ﮔﮔﮔ۷۰ﮒ
- [ ] ﮒ؟ﻝﺍGNNﮒ ﮒ­ﮔﮔﮔ۷۰ﮒ(ﮒ?
- [ ] ﻟ؟­ﻝﭨﮔﺍﮔ؟ﮒﮒ۳ﮒﻠ۱ﮒ۳ﻝ
- [ ] ﮔ۷۰ﮒﻟ؟­ﻝﭨﮒﻟﺍ?- [ ] ﻝﺙﮒﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮔ۷۰ﮒﮒﮒﮔﭖﻟﺁ
- [ ] ﮔ۶ﻟﺛﻛﺙﮒﮒGPUﮒ?
**ﻛﭦ۳ﻛﭨ?*:
- ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮔﮔﮒﺙﮔﻛﭨ۲ﻝ 
- ﻟ؟­ﻝﭨﮒ۴ﺛﻝﮔ۷۰ﮒﮔﻛﭨﭘ
- ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮔ۷۰ﮒﮔﭖﻟﺁﮔ۴ﮒ
- ﮔ۶ﻟﺛﻛﺙﮒﮔ۴ﮒ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- LSTMﮔﮔﮒﭦﻗ۴5ﻛﺕ۹IC?.03ﻝﮒ ?- Transformerﮔﮔﮒﭦﻗ۴5ﻛﺕ۹IC?.03ﻝﮒ ?- GPUﮒ۸ﻝ۷ﻝﻗ۴80%
- ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝﻗ۴80%

### 10.3 Phase 3: ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﮒﺙﮔﮒ؟ﻝﺍ (Week 5-6)

**ﻝ؟ﮔ **: ﮒ؟ﻝﺍDQNﮒPPOﮒ ﮒ­ﻛﺙﮒ

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍReinforcementLearningMiner?- [ ] ﮒ؟ﻝﺍDQNﮒ ﮒ­ﮔﻠﻛﺙﮒﮔ۷۰ﮒ
- [ ] ﮒ؟ﻝﺍPPOﮒ ﮒ­ﻠﮔ۸ﻛﺙﮒﮔ۷۰ﮒ
- [ ] ﮒ؟ﻝﺍﮒﺙﭦﮒﮒ­۵ﻛﺗ ﻝﺁﮒ۱(Env)
- [ ] ﮔ۷۰ﮒﻟ؟­ﻝﭨﮒﻟﺍ?- [ ] ﻝﺙﮒﮒﺙﭦﮒﮒ­۵ﻛﺗ ﮔ۷۰ﮒﮒﮒﮔﭖﻟﺁ
- [ ] ﮔ۶ﻟﺛﻛﺙﮒ

**ﻛﭦ۳ﻛﭨ?*:
- ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﻛﺙﮒﮒﺙﮔﻛﭨ۲ﻝ 
- ﻟ؟­ﻝﭨﮒ۴ﺛﻝﮔ۷۰ﮒﮔﻛﭨﭘ
- ﮒﺙﭦﮒﮒ­۵ﻛﺗ ﮔ۷۰ﮒﮔﭖﻟﺁﮔ۴ﮒ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- DQNﻛﺙﮒﮒﮒ۳ﮔ؟ﮔﺁﻝﮔﮒﻗ۴10%
- PPOﮒ۷ﮔﮒ ﮒ­ﻠﮔ۸ﮒﻝ۰؟ﻝﻗ۴70%
- ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝﻗ۴80%

### 10.4 Phase 4: ﻠﻛﺙ ﻝ؟ﮔﺏﮒﺙﮔﮒ؟ﻝﺍ (Week 7-8)

**ﻝ؟ﮔ **: ﮒ؟ﻝﺍﻠﻛﺙ ﻝﺙﻝ۷ﮒ ﮒ­ﮒﻝﺍ

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍGeneticAlgorithmMiner?- [ ] ﮒ؟ﻛﺗﻠﮒﻛﺕﻝ۷ﮒﺛﮔﺍ?- [ ] ﮒ؟ﻝﺍﻠﻛﺙ ﻝﺙﻝ۷ﻟﺟﮒﮔﭖﻝ۷
- [ ] ﮒ؟ﻝﺍﮒ ﮒ­ﻟ۰۷ﻟﺝﺝﮒﺙﻟ۶۲ﮔﮒ۷
- [ ] ﮒ؟ﻝﺍﮒ۳ﮔﮒﭦ۵ﮔ۶ﮒﭘﮔﭦ?- [ ] ﻝﺙﮒﻠﻛﺙ ﻝ؟ﮔﺏﮔ۷۰ﮒﮒﮒﮔﭖﻟﺁ
- [ ] ﮔ۶ﻟﺛﻛﺙﮒ

**ﻛﭦ۳ﻛﭨ?*:
- ﻠﻛﺙ ﻝ؟ﮔﺏﮒﻝﺍﮒﺙﮔﻛﭨ۲ﻝ 
- ﮒﻝﺍﻝﮒ ﮒ­ﻟ۰۷ﻟﺝﺝﮒﺙ?- ﻠﻛﺙ ﻝ؟ﮔﺏﮔ۷۰ﮒﮔﭖﻟﺁﮔ۴ﮒ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻠﻛﺙ ﻝ؟ﮔﺏﮒﻝﺍ?0ﻛﺕ۹ﮔﮔﮒ ﮒ­ﻟ۰۷ﻟﺝﺝﮒﺙ
- ﮒ ﮒ­ﻟ۰۷ﻟﺝﺝﮒﺙﮒﺁﻟ۶۲ﻠ?00%
- ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝﻗ۴80%

### 10.5 Phase 5: ﻠﮔﮔﭖﻟﺁﻛﺕﻛﺙ?(Week 9-10)

**ﻝ؟ﮔ **: ﮒ؟ﮔﻝ،ﺁﮒﺍﻝ،ﺁﻠﮔﮔﭖﻟﺁﮒﮔ۶ﻟﺛﻛﺙﮒ

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﻝ،ﺁﮒﺍﻝ،ﺁﻠﮔﮔﭖ?- [ ] ﮔ۶ﻟﺛﮒﮒﮔﭖﻟﺁ
- [ ] ﮒ؟ﮒ۷ﮔﭖﻟﺁ
- [ ] ﮔ۶ﻟﺛﻛﺙﮒﮒﻟﺍ?- [ ] Bugﻛﺟ؟ﮒ۳
- [ ] ﮔﮔ۰۲ﮒ؟ﮒ

**ﻛﭦ۳ﻛﭨ?*:
- ﻠﮔﮔﭖﻟﺁﮔ۴ﮒ
- ﮔ۶ﻟﺛﮔﭖﻟﺁﮔ۴ﮒ
- ﮒ؟ﮒ۷ﮔﭖﻟﺁﮔ۴ﮒ
- ﮒ؟ﮔﺑﮔﮔﺁﮔ?
**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻝ،ﺁﮒﺍﻝ،ﺁﮔﭖﻟﺁﻠﻟﺟ?00%
- ﮔ۶ﻟﺛﮔﮔ ﻟﺝﺝﮔ 
- ﮔ ﻠ،ﮒﺎﮒ؟ﮒ۷ﮔﺙ?- ﮔﮔ۰۲ﮒ؟ﮔﺑ

### 10.6 Phase 6: ﻛﺕﻝﭦﺟﻠ۷ﻝﺛﺎ (Week 11-12)

**ﻝ؟ﮔ **: ﻝﻛﭦ۶ﻝﺁﮒ۱ﻠ۷ﻝﺛﺎﮒﻝ?
**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﻝﻛﭦ۶ﻝﺁﮒ۱ﻠ۷ﻝﺛﺎ
- [ ] ﻝﮔ۶ﻝﺏﭨﻝﭨﻠﻝﺛ؟
- [ ] ﮒﻟ­۵ﻟ۶ﮒﻠﻝﺛ؟
- [ ] ﻝ۷ﮔﺓﮒﺗﻟ؟­
- [ ] ﻛﺕﻝﭦﺟﻠ۹ﮔﭘ
- [ ] ﻟﺟﻝﭨﺑﮔﮔ۰۲ﻝﺙﮒ

**ﻛﭦ۳ﻛﭨ?*:
- ﻝﻛﭦ۶ﻝﺁﮒ۱ﻠ۷ﻝﺛﺎﮔﮔ۰۲
- ﻝﮔ۶ﮒﻟ­۵ﻠﻝﺛ؟
- ﻝ۷ﮔﺓﮒﺗﻟ؟­ﮔﮔ
- ﻟﺟﻝﭨﺑﮔﮒ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻝﻛﭦ۶ﻝﺁﮒ۱ﻟﺟﻟ۰ﻝ۷ﺏﮒ؟
- ﻝﮔ۶ﮒﻟ­۵ﮔ­۲ﮒﺕﺕ
- ﻝ۷ﮔﺓﮒﺗﻟ؟­ﮒ؟ﮔ
- ﻟﺟﻝﭨﺑﮔﮔ۰۲ﮒ؟ﮔﺑ

---

## 11. ﻠﮒﺛ

### 11.1 ﮒﻟﻟﭖ?
1. **PyTorchﮒ؟ﮔﺗﮔﮔ۰۲**: https://pytorch.org/docs/
2. **Stable-Baselines3ﮔﮔ۰۲**: https://stable-baselines3.readthedocs.io/
3. **DEAPﮔﮔ۰۲**: https://deap.readthedocs.io/
4. **Feastﮔﮔ۰۲**: https://docs.feast.dev/
5. **QLibﮔ۰ﮔﭘ**: https://qlib.readthedocs.io/
6. **gplearnﮔﮔ۰۲**: https://gplearn.readthedocs.io/

### 11.2 ﻛﺕﻛﺕﮔﭦﮔﮔﻛﺛﺏﮒ؟?
**ﮔ۰۴ﮔﺍﺑﮒﭦﻠ**:
- ﮒ؟ﻟ۶ﻝﭨﮔﭖﮒ ﮒ­ﻝ ﻝ۸ﭘﮔﺗﮔﺏ?- ﻠ۲ﻠ۸ﮒﺗﺏﻛﭨﺓﮔ۷۰ﮒ
- ﮒ۷ﮒ۳۸ﮒﻝ­?
**ﮔﻟﭦﮒ۳ﮒﺑﻝ۶ﮔ**:
- ﻝﭨﻟ؟۰ﮒ۴ﮒ۸ﮔ۷۰ﮒ
- ﮔﺓﺎﮒﭦ۵ﮒ­۵ﻛﺗ ﮒ ﮒ­ﮔﮔ
- ﻠ،ﻠ۱ﻛﭦ۳ﮔﮔ۶ﻟ۰

**Two Sigma**:
- ﮔﭦﮒ۷ﮒ­۵ﻛﺗ ﮒ ﮒ­ﻝ ﻝ۸ﭘ
- ﮒ۳۶ﮔﺍﮔ؟ﮒ۳ﻝﮔﭘ?- AIﻠ۸ﺎﮒ۷ﮔﻟﭖ

### 11.3 ﮔﺁﻟﺁ­?
| ﮔﺁﻟﺁ­ | ﮒ؟ﻛﺗ |
|------|------|
| **Alphaﮒ ﮒ­** | ﻟﺛﮒ۳ﻛﭦ۶ﻝﻟﭘﻠ۱ﮔﭘﻝﻝﮒ ?|
| **IC (Information Coefficient)** | ﮒ ﮒ­ﮒﺙﻛﺕﮔ۹ﮔ۴ﮔﭘﻝﻝﻝﻝﺕﮒﺏﻝﺏﭨﮔﺍ |
| **ICIR (IC Information Ratio)** | ICﮒﮒﺙﻛﺕICﮔ ﮒﮒﺓ؟ﻝﮔﺁ?|
| **LSTM** | ﻠﺟﻝ­ﮔﻟ؟ﺍﮒﺟﻝﺛ?|
| **Transformer** | ﮒﭦﻛﭦﻟ۹ﮔﺏ۷ﮔﮒﮔﭦﮒﭘﻝﻝ۴ﻝﭨﻝﺛ?|
| **GNN** | ﮒﺝﻝ۴ﻝﭨﻝﺛ?|
| **DQN** | ﮔﺓﺎﮒﭦ۵Qﻝﺛﻝﭨ |
| **PPO** | ﻟﺟﻝ،ﺁﻝ­ﻝ۴ﻛﺙﮒ |
| **ﻠﻛﺙ ﻝﺙﻝ۷** | ﻛﺛﺟﻝ۷ﻠﻛﺙ ﻝ؟ﮔﺏﻟ۹ﮒ۷ﻟﺟﮒﻝ۷ﮒﭦ |
| **ﻟﺟﮔ?* | ﮔ۷۰ﮒﮒ۷ﻟ؟­ﻝﭨﻠﻟ۰۷ﻝﺍﮒ۴ﺛﻛﺛﮒ۷ﮔﭖﻟﺁﻠﻟ۰۷ﻝﺍ?|

---

**ﮔﮔ۰۲ﻝﮔ؛**: v1.0  
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02  
**ﮔﮒﮔﺑ?*: 2026-04-02  
**ﮔﮔ۰۲ﻝ?*: ?ﮒ؟ﮔ  
**ﻛﺕﻛﺕ?*: ﮒﺙﮒ۶ﮒ؟ﮔﺛPhase 1
