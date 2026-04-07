---
module_id: UNIFIED_INTERFACE_CONTRACT_SPECIFICATION
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - UNIFIED_INTERFACE_CONTRACT技术规范
---

﻿---
module_id: UNIFIED_INTERFACE_CONTRACT_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: ﻠ۵ﮒﺕﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 系统实施与部署管理与优化维护
standard_type: ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ﻟ۶ﻟ
applicable_scope: Layer 4 ﮔﭦﮒ۷ﮒ۵ﻛﺗﮒﺎﮒﻝﺕﮒﺏﮔ۷۰ﮒ
compliance_level: ﻛﺕﻛﺕﮔﮒ
---
---


# ﻝﭨﻛﺕﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ﻟ۶ﻟ v1.0
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **ﮔﮔ۰۲ﻝﮔ؛**: v1.0
> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-03
> **ﻠﻝ۷ﻟﮒﺑ**: Layer 4 ﮔﭦﮒ۷ﮒ۵ﻛﺗﮒﺎﮒﻝﺕﮒﺏﮔ۷۰ﮒ
> **ﻝ؟ﻝ**: ﮔﭘﻠ۳ﮔ۴ﮒ۲ﻠﮒ۳ﮒ؟ﻛﺗﺅﺙﮒﭨﭦﻝ،ﻝﭨﻛﺕﻝﮔ۴ﮒ۲ﮒ۴ﺅﺟ?
---

## 1. ﮔ۵ﻟﺟﺍ

### 1.1 ﮔﮔ۰۲ﻝ؟ﻝ

ﮔ؛ﮔﮔ۰۲ﮒ؟ﻛﺗﻛﭦﮔﭦﮒ۷ﮒ۵ﻛﺗﮒﺎﮒﻝﺕﮒﺏﮔ۷۰ﮒﻝﻝﭨﻛﺕﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ﺅﺙﻟ۶۲ﮒﺏﻛﭨ۴ﻛﺕﻠ؟ﻠ۱ﺅﺙ
- ﮔ۴ﮒ۲ﮒ؟ﻛﺗﻠﮒ۳ﺅﺙﮒﮒﻟ؟۰ﻝ؟ﻙﮔ۷۰ﮒﻟ؟ﻝﭨﻙﻝﺗﮒﺝﮔﮒ۰ﺅﺙ
- ﻟﻟﺑ۲ﻟﺝﺗﻝﻛﺕﮔﺕ
- ﻟﺍﻝ۷ﮒﺏﻝﺏﭨﮔﺓﺓﻛﺗﺎ

### 1.2 ﻠﻝ۷ﮔ۷۰ﮒ

| ﮔ۷۰ﮒ | ﮔ۴ﮒ۲ﻝﺎﭨﮒ | ﮒ۴ﻝﭦ۵ﻝﮔ؛ |
|------|----------|----------|
| FactorCalculator | ﮒﮒﻟ؟۰ﻝ؟ | IFactorCalculator v1.0 |
| AlphaFactorFactory | ﮒﮒﻟ؟۰ﻝ؟ | IFactorCalculator v1.0 |
| QlibAlpha158 | ﮒﮒﻟ؟۰ﻝ؟ | IFactorCalculator v1.0 |
| ModelTrainingPipeline | ﮔ۷۰ﮒﻟ؟ﻝﭨ | IModelTrainer v1.0 |
| LSTMModel | ﮔ۷۰ﮒﻟ؟ﻝﭨ | IModelTrainer v1.0 |
| TransformerModel | ﮔ۷۰ﮒﻟ؟ﻝﭨ | IModelTrainer v1.0 |
| FeatureEngineering | ﻝﺗﮒﺝﮔﮒ۰ | IFeatureService v1.0 |
| FeatureStore | ﻝﺗﮒﺝﮔﮒ۰ | IFeatureService v1.0 |

---

## 2. ﮒﮒﻟ؟۰ﻝ؟ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵

### 2.1 IFactorCalculator v1.0

**ﻟﻟﺑ۲**: ﮒ؟ﻛﺗﮒﮒﻟ؟۰ﻝ؟ﻝﮔﮒﮔ۴ﺅﺟ?
**ﮒ؟ﻝﺍﮔ۷۰ﮒ**: FactorCalculator (Layer 2), QlibAlpha158 (Layer 4)

**ﻟﺍﻝ۷ﺅﺟ?*: AlphaFactorFactory, ﻝﻝ۴ﮒﺙﮔ

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class FactorInput:
"""ﮒﮒﻟ؟۰ﻝ؟ﻟﺝﮒ۴"""
    instruments: List[str]
    start_date: datetime
    end_date: datetime
    data: Optional[pd.DataFrame] = None
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class FactorOutput:
"""ﮒﮒﻟ؟۰ﻝ؟ﻟﺝﮒﭦ"""
    factor_values: pd.DataFrame
    factor_names: List[str]
    calculation_time: float
    metadata: Dict[str, Any]


class IFactorCalculator(ABC):
"""ﮒﮒﻟ؟۰ﻝ؟ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ v1.0
    
    ﮒ؟ﻝﺍﮔ۷۰ﮒ:
- FactorCalculator: ﮒﭦﻝ۰ﮒﮒﻟ؟۰ﻝ؟ (Layer 2)
- QlibAlpha158: AIﮒﮒﻟ؟۰ﻝ؟ (Layer 4)
    
    ﻟﺍﻝ۷ﺅﺟ?
- AlphaFactorFactory: ﮒﮒﻝﻠﮒﮒﮔ
- ﻝﻝ۴ﮒﺙﮔ: ﻝﺑﮔ۴ﻛﺛﺟﻝ۷ﮒﮒ
    """
    
    @abstractmethod
    def calculate_factors(
        self,
        factor_input: FactorInput
    ) -> FactorOutput:
"""ﻟ؟۰ﻝ؟ﮒﮒ
        
        Args:
factor_input: ﮒﮒﻟ؟۰ﻝ؟ﻟﺝﮒ۴
            
        Returns:
FactorOutput: ﮒﮒﻟ؟۰ﻝ؟ﻝﭨﮔ
            
        Raises:
FactorCalculationError: ﮒﮒﻟ؟۰ﻝ؟ﮒ۳ﺎﻟﺑ۴
InvalidInputError: ﻟﺝﮒ۴ﮒﮔﺍﮔﮔ
        """
        pass
    
    @abstractmethod
    def get_factor_definitions(self) -> Dict[str, Dict[str, Any]]:
"""ﻟﺓﮒﮒﮒﮒ؟ﻛﺗ
        
        Returns:
Dict[str, Dict]: ﮒﮒﮒﻝ۶ﺍ -> ﮒﮒﮒ؟ﻛﺗ
        """
        pass
    
    @abstractmethod
    def validate_input(self, factor_input: FactorInput) -> bool:
        """ﻠ۹ﻟﺁﻟﺝﮒ۴ﮒﮔﺍ
        
        Args:
factor_input: ﮒﮒﻟ؟۰ﻝ؟ﻟﺝﮒ۴
            
        Returns:
            bool: ﻠ۹ﻟﺁﮔﺁﮒ۵ﻠﻟﺟ
        """
        pass
```

### 2.2 ﮔ۴ﮒ۲ﮒ؟ﻝﺍﮔﮒﺍ

| ﮒ؟ﻝﺍﮔ۷۰ﮒ | ﮔ۴ﮒ۲ﮔﺗﮔﺏ | ﮒﮒﻝﺎﭨﮒ | Layer |
|----------|----------|----------|-------|
| FactorCalculator | calculate_factors | ﻛﭨﺓﮒﺙﻙﮔﻠﺟﻙﮒ۷ﻠﻙﮔﮔﺁﮔﺅﺟ?| Layer 2 |
| QlibAlpha158 | calculate_factors | Alpha158 AIﮒﮒ | Layer 4 |
| BarraStyleFactorCalculator | calculate_factors | ﻠ۲ﮔﺙﮒﮒ | Layer 6 |

### 2.3 ﻟﺍﻝ۷ﮒﺏﻝﺏﭨ

```
AlphaFactorFactory
ﻗﻗﻗ FactorCalculator.calculate_factors() -> ﮒﭦﻝ۰ﮒﮒ
ﻗﻗﻗ QlibAlpha158.calculate_factors() -> AIﮒﮒ
ﻗﻗﻗ ﮒﻠ۷ﻝﻠﮒﮒﮔﻠﭨﻟﺝ
```

---

## 3. ﮔ۷۰ﮒﻟ؟ﻝﭨﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵

### 3.1 IModelTrainer v1.0

**ﻟﻟﺑ۲**: ﮒ؟ﻛﺗﮔ۷۰ﮒﻟ؟ﻝﭨﻝﮔﮒﮔ۴ﺅﺟ?
**ﮒ؟ﻝﺍﮔ۷۰ﮒ**: LSTMTrainer, TransformerTrainer

**ﻟﺍﻝ۷ﺅﺟ?*: ModelTrainingPipeline

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class TrainingConfig:
"""ﻟ؟ﻝﭨﻠﻝﺛ؟"""
    num_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    early_stop_patience: int = 10
    validation_split: float = 0.2
    device: str = 'cuda'
    checkpoint_dir: str = './checkpoints'


@dataclass
class TrainingResult:
"""ﻟ؟ﻝﭨﻝﭨﮔ"""
    model_id: str
    training_history: Dict[str, List[float]]
    best_epoch: int
    best_val_loss: float
    training_time: float
    model_path: str
    metrics: Dict[str, float]


class IModelTrainer(ABC):
"""ﮔ۷۰ﮒﻟ؟ﻝﭨﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ v1.0
    
    ﮒ؟ﻝﺍﮔ۷۰ﮒ:
- LSTMTrainer: LSTMﮔ۷۰ﮒﻟ؟ﻝﭨﺅﺟ?    - TransformerTrainer: Transformerﮔ۷۰ﮒﻟ؟ﻝﭨﺅﺟ?
    ﻟﺍﻝ۷ﺅﺟ?
- ModelTrainingPipeline: ﻠﻝ۷ﻟ؟ﻝﭨﮔﭖﮔﺍﺑﺅﺟ?    """
    
    @abstractmethod
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> TrainingResult:
"""ﻟ؟ﻝﭨﮔ۷۰ﮒ
        
        Args:
X_train: ﻟ؟ﻝﭨﻝﺗﮒﺝ
y_train: ﻟ؟ﻝﭨﮔﻝﺝ
            X_val: ﻠ۹ﻟﺁﻝﺗﮒﺝ
y_val: ﻠ۹ﻟﺁﮔﻝﺝ
            
        Returns:
TrainingResult: ﻟ؟ﻝﭨﻝﭨﮔ
        """
        pass
    
    @abstractmethod
    def save_model(self, path: str) -> None:
"""ﻛﺟﮒﮔ۷۰ﮒ
        
        Args:
path: ﻛﺟﮒﻟﺓﺁﮒﺝ
        """
        pass
    
    @abstractmethod
    def load_model(self, path: str) -> None:
"""ﮒﻟﺛﺛﮔ۷۰ﮒ
        
        Args:
            path: ﮔ۷۰ﮒﻟﺓﺁﮒﺝ
        """
        pass
    
    @abstractmethod
    def get_model_config(self) -> Dict[str, Any]:
        """ﻟﺓﮒﮔ۷۰ﮒﻠﻝﺛ؟
        
        Returns:
            Dict: ﮔ۷۰ﮒﻠﻝﺛ؟
        """
        pass
```

### 3.2 ﮔ۴ﮒ۲ﮒ؟ﻝﺍﮔﮒﺍ

| ﮒ؟ﻝﺍﮔ۷۰ﮒ | ﮔ۴ﮒ۲ﮔﺗﮔﺏ | ﮔ۷۰ﮒﻝﺎﭨﮒ | ﻟﻟﺑ۲ |
|----------|----------|----------|------|
| LSTMTrainer | train() | LSTM | ﮔ۷۰ﮒﻝﺗﮒ؟ﻟ؟ﻝﭨﻠﭨﻟﺝ |
| TransformerTrainer | train() | Transformer | ﮔ۷۰ﮒﻝﺗﮒ؟ﻟ؟ﻝﭨﻠﭨﻟﺝ |

### 3.3 ﻟﺍﻝ۷ﮒﺏﻝﺏﭨ

```
ModelTrainingPipeline (ﻠﻝ۷ﮔﭖﮔﺍﺑﺅﺟ?
    ﺅﺟ?    ﻗﻗﻗ ﮔﺍﮔ؟ﻝﮔ؛ﻝ؟۰ﻝ (DVC)
    ﻗﻗﻗ ﻟﭘﮒﮔﺍﻛﺙﺅﺟ?(Optuna)
    ﻗﻗﻗ ﮒ؟ﻠ۹ﻟﺓﻟﺕ۹ (MLflow)
ﺅﺟ?    ﻗﻗﻗ IModelTrainer.train() (ﮔ۷۰ﮒﻝﺗﮒ؟ﻟ؟ﻝﭨ)
            ﻗﻗﻗ LSTMTrainer.train()
            ﻗﻗﻗ TransformerTrainer.train()
```

---

## 4. ﻝﺗﮒﺝﮔﮒ۰ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵

### 4.1 IFeatureService v1.0

**ﻟﻟﺑ۲**: ﮒ؟ﻛﺗﻝﺗﮒﺝﮔﮒ۰ﻝﮔﮒﮔ۴ﺅﺟ?
**ﮒ؟ﻝﺍﮔ۷۰ﮒ**: FeatureStore

**ﻟﺍﻝ۷ﺅﺟ?*: ﮔ۷۰ﮒﻟ؟ﻝﭨﻙﮒ۷ﻝﭦﺟﮔ۷ﺅﺟ?
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class FeatureVectorRequest:
    """ﻝﺗﮒﺝﮒﻠﻟﺁﺓﮔﺎ"""
    entity_keys: List[str]
    feature_names: List[str]
    entity_type: str = 'stock'
    request_id: Optional[str] = None


@dataclass
class FeatureVectorResponse:
    """ﻝﺗﮒﺝﮒﻠﮒﮒﭦ"""
    entity_key: str
    feature_values: Dict[str, Any]
    feature_timestamps: Dict[str, datetime]
    request_id: str


@dataclass
class HistoricalFeaturesRequest:
    """ﮒﮒﺎﻝﺗﮒﺝﻟﺁﺓﮔﺎ"""
    entity_keys: List[str]
    feature_names: List[str]
    start_time: datetime
    end_time: datetime
    entity_type: str = 'stock'


class IFeatureService(ABC):
    """ﻝﺗﮒﺝﮔﮒ۰ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ v1.0
    
    ﮒ؟ﻝﺍﮔ۷۰ﮒ:
- FeatureStore: ﻝﺗﮒﺝﮒﮒ۷ﮔﮒ۰
    
    ﻟﺍﻝ۷ﺅﺟ?
- ModelTrainingPipeline: ﻟ؟ﻝﭨﮔﺍﮔ؟ﻟﺓﮒ
    - ModelServingService: ﮒ۷ﻝﭦﺟﮔ۷ﻝﻝﺗﮒﺝ
    """
    
    @abstractmethod
    def get_online_features(
        self,
        request: FeatureVectorRequest
    ) -> List[FeatureVectorResponse]:
        """ﻟﺓﮒﮒ۷ﻝﭦﺟﻝﺗﮒﺝ
        
        Args:
            request: ﻝﺗﮒﺝﻟﺁﺓﮔﺎ
            
        Returns:
            List[FeatureVectorResponse]: ﻝﺗﮒﺝﮒﻠﮒﻟ۰۷
        """
        pass
    
    @abstractmethod
    def get_historical_features(
        self,
        request: HistoricalFeaturesRequest
    ) -> pd.DataFrame:
        """ﻟﺓﮒﮒﮒﺎﻝﺗﮒﺝ
        
        Args:
            request: ﮒﮒﺎﻝﺗﮒﺝﻟﺁﺓﮔﺎ
            
        Returns:
            pd.DataFrame: ﮒﮒﺎﻝﺗﮒﺝﮔﺍﮔ؟
        """
        pass
    
    @abstractmethod
    def register_feature(
        self,
        feature_name: str,
        feature_definition: Dict[str, Any]
    ) -> str:
        """ﮔﺏ۷ﮒﻝﺗﮒﺝ
        
        Args:
            feature_name: ﻝﺗﮒﺝﮒﻝ۶ﺍ
            feature_definition: ﻝﺗﮒﺝﮒ؟ﻛﺗ
            
        Returns:
            str: ﻝﺗﮒﺝID
        """
        pass
```

### 4.2 ﮔ۴ﮒ۲ﮒ؟ﻝﺍﮔﮒﺍ

| ﮒ؟ﻝﺍﮔ۷۰ﮒ | ﮔ۴ﮒ۲ﮔﺗﮔﺏ | ﮔﮒ۰ﻝﺎﭨﮒ | ﻟﻟﺑ۲ |
|----------|----------|----------|------|
| FeatureStore | get_online_features() | ﮒ۷ﻝﭦﺟﮔﮒ۰ | ﮒ؟ﮔﭘﻝﺗﮒﺝﮔ۲ﺅﺟ?|
| FeatureStore | get_historical_features() | ﻝ۵ﭨﻝﭦﺟﮔﮒ۰ | ﮔﺗﻠﻝﺗﮒﺝﮔ۲ﺅﺟ?|

### 4.3 ﻛﺕFeatureEngineeringﻝﮒﺅﺟ?
```
FeatureEngineering (ﻝﺗﮒﺝﮒﺓ۴ﻝ۷)
    ﺅﺟ?    ﻗﻗﻗ ﻝﺗﮒﺝﻝﮔ
    ﻗﻗﻗ ﻝﺗﮒﺝﻠﮔ۸
    ﻗﻗﻗ ﻝﺗﮒﺝﮒﮔ۱
    ﻗﻗﻗ ﻟﺝﮒﭦﻟ؟۰ﻝ؟ﮒﻝﻝﺗﮒﺝ
ﺅﺟ?            ﺅﺟ?FeatureStore (ﻝﺗﮒﺝﮒﮒ۷)
    ﺅﺟ?    ﻗﻗﻗ register_feature() -> ﮔﺏ۷ﮒﻝﺗﮒﺝ
ﻗﻗﻗ ﮒﮒ۷ﻝﺗﮒﺝﮔﺍﮔ؟
    ﻗﻗﻗ get_online_features() -> ﮔﮒ۰ﻝﺗﮒﺝ
```

---

## 5. ﮔ۴ﮒ۲ﻝﮔ؛ﻝ؟۰ﻝ

### 5.1 ﻝﮔ؛ﮔ۶ﮒﭘﻟ۶ﮒ

1. **ﮒﮒﮒﺙﮒ؟ﺗ**: ﮔﺍﻝﮔ؛ﮒﺟﻠ۰ﭨﮒﮒﮒﺙﮒ؟ﺗﮔ۶ﻝﮔ؛
2. **ﮒﭦﮒﺙﻠﻝ۴**: ﮒﭦﮒﺙﮔ۴ﮒ۲ﻠﮔﮒ3ﻛﺕ۹ﮔﻠﻝ۴
3. **ﻝﮔ؛ﮔﻟﺁ**: ﮔﮔﮔ۴ﮒ۲ﻠﮔﮔﺏ۷ﻝﮔ؛ﺅﺟ?
### 5.2 ﮒﮔﺑﻟ؟ﺍﮒﺛ

| ﻝﮔ؛ | ﮔ۴ﮔ | ﮒﮔﺑﮒﮒ؟ﺗ | ﮒﺛﺎﮒﮔ۷۰ﮒ |
|------|------|----------|----------|
| v1.0 | 2026-04-03 | ﮒﮒ۶ﻝﮔ؛ | ﮒﮒﻟ؟۰ﻝ؟ﻙﮔ۷۰ﮒﻟ؟ﻝﭨﻙﻝﺗﮒﺝﮔﺅﺟ?|

---

## 6. ﮔ۴ﮒ۲ﻛﺛﺟﻝ۷ﮔﮒ

### 6.1 ﮒﮒﻟ؟۰ﻝ؟ﮔ۴ﮒ۲ﻛﺛﺟﻝ۷

```python
from factor_calculator import FactorCalculator
from qlib_alpha158 import QlibAlpha158Manager

factor_calculator = FactorCalculator(config)
alpha158_manager = QlibAlpha158Manager(config)

factor_input = FactorInput(
    instruments=['000001.SZ', '000002.SZ'],
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 3, 31)
)

basic_factors = factor_calculator.calculate_factors(factor_input)
ai_factors = alpha158_manager.calculate_factors(factor_input)
```

### 6.2 ﮔ۷۰ﮒﻟ؟ﻝﭨﮔ۴ﮒ۲ﻛﺛﺟﻝ۷

```python
from model_training_pipeline import ModelTrainingPipeline
from lstm_model import LSTMTrainer

trainer = LSTMTrainer(model, config)
pipeline = ModelTrainingPipeline(trainer, pipeline_config)

result = pipeline.train(training_config)
```

### 6.3 ﻝﺗﮒﺝﮔﮒ۰ﮔ۴ﮒ۲ﻛﺛﺟﻝ۷

```python
from feature_store import FeatureStoreAPI

feature_store = FeatureStoreAPI(config)

request = FeatureVectorRequest(
    entity_keys=['000001.SZ'],
    feature_names=['PE', 'PB', 'momentum_1m']
)

features = feature_store.get_online_features(request)
```

---

## 7. ﻠﮒﺛ

### 7.1 ﻝﺕﮒﺏﮔﮔ۰۲

- [FACTOR_CALCULATOR_TECHNICAL_SPECIFICATION](./FACTOR_CALCULATOR_TECHNICAL_SPECIFICATION.md)
- [ALPHA_FACTOR_FACTORY_TECHNICAL_SPECIFICATION](./ALPHA_FACTOR_FACTORY_TECHNICAL_SPECIFICATION.md)
- [QLIB_ALPHA158_TECHNICAL_SPECIFICATION](./QLIB_ALPHA158_TECHNICAL_SPECIFICATION.md)
- [MODEL_TRAINING_PIPELINE_TECHNICAL_SPECIFICATION](./MODEL_TRAINING_PIPELINE_TECHNICAL_SPECIFICATION.md)
- [LSTM_MODEL_TECHNICAL_SPECIFICATION](./LSTM_MODEL_TECHNICAL_SPECIFICATION.md)
- [TRANSFORMER_MODEL_TECHNICAL_SPECIFICATION](./TRANSFORMER_MODEL_TECHNICAL_SPECIFICATION.md)
- [FEATURE_ENGINEERING_TECHNICAL_SPECIFICATION](./FEATURE_ENGINEERING_TECHNICAL_SPECIFICATION.md)
- FEATURE_STORE_TECHNICAL_SPECIFICATION

### 7.2 ﮔﺁﻟﺁﺅﺟ?
| ﮔﺁﻟﺁ | ﮒ؟ﻛﺗ |
|------|------|
| ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ | ﮔ۷۰ﮒﻠﺑﻛﭦ۳ﻛﭦﻝﮔﮒﮒﮔ۴ﮒ۲ﮒ؟ﺅﺟ?|
| ﮒﮒﻟ؟۰ﻝ؟ | ﻛﭨﮒﮒ۶ﮔﺍﮔ؟ﻟ؟۰ﻝ؟ﮒﮒﮒﺙﻝﻟﺟﻝ۷ |
| ﮔ۷۰ﮒﻟ؟ﻝﭨ | ﻛﺛﺟﻝ۷ﮔﺍﮔ؟ﻟ؟ﻝﭨﮔﭦﮒ۷ﮒ۵ﻛﺗﮔ۷۰ﮒﻝﻟﺟﺅﺟ?|
| ﻝﺗﮒﺝﮔﮒ۰ | ﮔﻛﺝﻝﺗﮒﺝﮔﺍﮔ؟ﻝﮒﮒ۷ﮒﮔ۲ﻝﺑ۱ﮔﺅﺟ?|

---

**ﮔﮔ۰۲ﻝﮔ؛**: v1.0
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-03
**ﻝﭨﺑﮔ۳ﺅﺟ?*: ﻠ۵ﮒﺕﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
