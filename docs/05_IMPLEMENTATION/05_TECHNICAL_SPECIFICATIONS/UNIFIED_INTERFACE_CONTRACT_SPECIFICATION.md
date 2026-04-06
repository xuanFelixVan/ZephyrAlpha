---
module_id: UNIFIED_INTERFACE_CONTRACT_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 因子计算
  - 数据源
  - 特征工程
standard_type: ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ﻟ۶ﻟ
applicable_scope: Layer 4 ﮔﭦﮒ۷ﮒ­۵ﻛﺗ ﮒﺎﮒﻝﺕﮒﺏﮔ۷۰ﮒ
compliance_level: ﻛﺕﻛﺕﮔ ﮒ---


# ﻝﭨﻛﺕﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ﻟ۶ﻟ v1.0

> **ﮔﮔ۰۲ﻝﮔ؛**: v1.0
> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-03
> **ﻠﻝ۷ﻟﮒﺑ**: Layer 4 ﮔﭦﮒ۷ﮒ­۵ﻛﺗ ﮒﺎﮒﻝﺕﮒﺏﮔ۷۰ﮒ
> **ﻝ؟ﻝ**: ﮔﭘﻠ۳ﮔ۴ﮒ۲ﻠﮒ۳ﮒ؟ﻛﺗﺅﺙﮒﭨﭦﻝ،ﻝﭨﻛﺕﻝﮔ۴ﮒ۲ﮒ۴ﺅﺟ?
---

## 1. ﮔ۵ﻟﺟﺍ

### 1.1 ﮔﮔ۰۲ﻝ؟ﻝ

ﮔ؛ﮔﮔ۰۲ﮒ؟ﻛﺗﻛﭦﮔﭦﮒ۷ﮒ­۵ﻛﺗ ﮒﺎﮒﻝﺕﮒﺏﮔ۷۰ﮒﻝﻝﭨﻛﺕﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ﺅﺙﻟ۶۲ﮒﺏﻛﭨ۴ﻛﺕﻠ؟ﻠ۱ﺅﺙ
- ﮔ۴ﮒ۲ﮒ؟ﻛﺗﻠﮒ۳ﺅﺙﮒ ﮒ­ﻟ؟۰ﻝ؟ﻙﮔ۷۰ﮒﻟ؟­ﻝﭨﻙﻝﺗﮒﺝﮔﮒ۰ﺅﺙ
- ﻟﻟﺑ۲ﻟﺝﺗﻝﻛﺕﮔﺕ
- ﻟﺍﻝ۷ﮒﺏﻝﺏﭨﮔﺓﺓﻛﺗﺎ

### 1.2 ﻠﻝ۷ﮔ۷۰ﮒ

| ﮔ۷۰ﮒ | ﮔ۴ﮒ۲ﻝﺎﭨﮒ | ﮒ۴ﻝﭦ۵ﻝﮔ؛ |
|------|----------|----------|
| FactorCalculator | ﮒ ﮒ­ﻟ؟۰ﻝ؟ | IFactorCalculator v1.0 |
| AlphaFactorFactory | ﮒ ﮒ­ﻟ؟۰ﻝ؟ | IFactorCalculator v1.0 |
| QlibAlpha158 | ﮒ ﮒ­ﻟ؟۰ﻝ؟ | IFactorCalculator v1.0 |
| ModelTrainingPipeline | ﮔ۷۰ﮒﻟ؟­ﻝﭨ | IModelTrainer v1.0 |
| LSTMModel | ﮔ۷۰ﮒﻟ؟­ﻝﭨ | IModelTrainer v1.0 |
| TransformerModel | ﮔ۷۰ﮒﻟ؟­ﻝﭨ | IModelTrainer v1.0 |
| FeatureEngineering | ﻝﺗﮒﺝﮔﮒ۰ | IFeatureService v1.0 |
| FeatureStore | ﻝﺗﮒﺝﮔﮒ۰ | IFeatureService v1.0 |

---

## 2. ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵

### 2.1 IFactorCalculator v1.0

**ﻟﻟﺑ۲**: ﮒ؟ﻛﺗﮒ ﮒ­ﻟ؟۰ﻝ؟ﻝﮔ ﮒﮔ۴ﺅﺟ?
**ﮒ؟ﻝﺍﮔ۷۰ﮒ**: FactorCalculator (Layer 2), QlibAlpha158 (Layer 4)

**ﻟﺍﻝ۷ﺅﺟ?*: AlphaFactorFactory, ﻝ­ﻝ۴ﮒﺙﮔ

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class FactorInput:
    """ﮒ ﮒ­ﻟ؟۰ﻝ؟ﻟﺝﮒ۴"""
    instruments: List[str]
    start_date: datetime
    end_date: datetime
    data: Optional[pd.DataFrame] = None
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class FactorOutput:
    """ﮒ ﮒ­ﻟ؟۰ﻝ؟ﻟﺝﮒﭦ"""
    factor_values: pd.DataFrame
    factor_names: List[str]
    calculation_time: float
    metadata: Dict[str, Any]


class IFactorCalculator(ABC):
    """ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ v1.0
    
    ﮒ؟ﻝﺍﮔ۷۰ﮒ:
    - FactorCalculator: ﮒﭦﻝ۰ﮒ ﮒ­ﻟ؟۰ﻝ؟ (Layer 2)
    - QlibAlpha158: AIﮒ ﮒ­ﻟ؟۰ﻝ؟ (Layer 4)
    
    ﻟﺍﻝ۷ﺅﺟ?
    - AlphaFactorFactory: ﮒ ﮒ­ﻝ­ﻠﮒﮒﮔ
    - ﻝ­ﻝ۴ﮒﺙﮔ: ﻝﺑﮔ۴ﻛﺛﺟﻝ۷ﮒ ﮒ­
    """
    
    @abstractmethod
    def calculate_factors(
        self,
        factor_input: FactorInput
    ) -> FactorOutput:
        """ﻟ؟۰ﻝ؟ﮒ ﮒ­
        
        Args:
            factor_input: ﮒ ﮒ­ﻟ؟۰ﻝ؟ﻟﺝﮒ۴
            
        Returns:
            FactorOutput: ﮒ ﮒ­ﻟ؟۰ﻝ؟ﻝﭨﮔ
            
        Raises:
            FactorCalculationError: ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮒ۳ﺎﻟﺑ۴
            InvalidInputError: ﻟﺝﮒ۴ﮒﮔﺍﮔ ﮔ
        """
        pass
    
    @abstractmethod
    def get_factor_definitions(self) -> Dict[str, Dict[str, Any]]:
        """ﻟﺓﮒﮒ ﮒ­ﮒ؟ﻛﺗ
        
        Returns:
            Dict[str, Dict]: ﮒ ﮒ­ﮒﻝ۶ﺍ -> ﮒ ﮒ­ﮒ؟ﻛﺗ
        """
        pass
    
    @abstractmethod
    def validate_input(self, factor_input: FactorInput) -> bool:
        """ﻠ۹ﻟﺁﻟﺝﮒ۴ﮒﮔﺍ
        
        Args:
            factor_input: ﮒ ﮒ­ﻟ؟۰ﻝ؟ﻟﺝﮒ۴
            
        Returns:
            bool: ﻠ۹ﻟﺁﮔﺁﮒ۵ﻠﻟﺟ
        """
        pass
```

### 2.2 ﮔ۴ﮒ۲ﮒ؟ﻝﺍﮔ ﮒﺍ

| ﮒ؟ﻝﺍﮔ۷۰ﮒ | ﮔ۴ﮒ۲ﮔﺗﮔﺏ | ﮒ ﮒ­ﻝﺎﭨﮒ | Layer |
|----------|----------|----------|-------|
| FactorCalculator | calculate_factors | ﻛﭨﺓﮒﺙﻙﮔﻠﺟﻙﮒ۷ﻠﻙﮔﮔﺁﮔﺅﺟ?| Layer 2 |
| QlibAlpha158 | calculate_factors | Alpha158 AIﮒ ﮒ­ | Layer 4 |
| BarraStyleFactorCalculator | calculate_factors | ﻠ۲ﮔ ﺙﮒ ﮒ­ | Layer 6 |

### 2.3 ﻟﺍﻝ۷ﮒﺏﻝﺏﭨ

```
AlphaFactorFactory
    ﻗﻗﻗ FactorCalculator.calculate_factors() -> ﮒﭦﻝ۰ﮒ ﮒ­
    ﻗﻗﻗ QlibAlpha158.calculate_factors() -> AIﮒ ﮒ­
    ﻗﻗﻗ ﮒﻠ۷ﻝ­ﻠﮒﮒﮔﻠﭨﻟﺝ
```

---

## 3. ﮔ۷۰ﮒﻟ؟­ﻝﭨﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵

### 3.1 IModelTrainer v1.0

**ﻟﻟﺑ۲**: ﮒ؟ﻛﺗﮔ۷۰ﮒﻟ؟­ﻝﭨﻝﮔ ﮒﮔ۴ﺅﺟ?
**ﮒ؟ﻝﺍﮔ۷۰ﮒ**: LSTMTrainer, TransformerTrainer

**ﻟﺍﻝ۷ﺅﺟ?*: ModelTrainingPipeline

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class TrainingConfig:
    """ﻟ؟­ﻝﭨﻠﻝﺛ؟"""
    num_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    early_stop_patience: int = 10
    validation_split: float = 0.2
    device: str = 'cuda'
    checkpoint_dir: str = './checkpoints'


@dataclass
class TrainingResult:
    """ﻟ؟­ﻝﭨﻝﭨﮔ"""
    model_id: str
    training_history: Dict[str, List[float]]
    best_epoch: int
    best_val_loss: float
    training_time: float
    model_path: str
    metrics: Dict[str, float]


class IModelTrainer(ABC):
    """ﮔ۷۰ﮒﻟ؟­ﻝﭨﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ v1.0
    
    ﮒ؟ﻝﺍﮔ۷۰ﮒ:
    - LSTMTrainer: LSTMﮔ۷۰ﮒﻟ؟­ﻝﭨﺅﺟ?    - TransformerTrainer: Transformerﮔ۷۰ﮒﻟ؟­ﻝﭨﺅﺟ?    
    ﻟﺍﻝ۷ﺅﺟ?
    - ModelTrainingPipeline: ﻠﻝ۷ﻟ؟­ﻝﭨﮔﭖﮔﺍﺑﺅﺟ?    """
    
    @abstractmethod
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> TrainingResult:
        """ﻟ؟­ﻝﭨﮔ۷۰ﮒ
        
        Args:
            X_train: ﻟ؟­ﻝﭨﻝﺗﮒﺝ
            y_train: ﻟ؟­ﻝﭨﮔ ﻝ­ﺝ
            X_val: ﻠ۹ﻟﺁﻝﺗﮒﺝ
            y_val: ﻠ۹ﻟﺁﮔ ﻝ­ﺝ
            
        Returns:
            TrainingResult: ﻟ؟­ﻝﭨﻝﭨﮔ
        """
        pass
    
    @abstractmethod
    def save_model(self, path: str) -> None:
        """ﻛﺟﮒ­ﮔ۷۰ﮒ
        
        Args:
            path: ﻛﺟﮒ­ﻟﺓﺁﮒﺝ
        """
        pass
    
    @abstractmethod
    def load_model(self, path: str) -> None:
        """ﮒ ﻟﺛﺛﮔ۷۰ﮒ
        
        Args:
            path: ﮔ۷۰ﮒﻟﺓﺁﮒﺝ
        """
        pass
    
    @abstractmethod
    def get_model_config(self) -> Dict[str, Any]:
        """ﻟﺓﮒﮔ۷۰ﮒﻠﻝﺛ؟
        
        Returns:
            Dict: ﮔ۷۰ﮒﻠﻝﺛ؟
        """
        pass
```

### 3.2 ﮔ۴ﮒ۲ﮒ؟ﻝﺍﮔ ﮒﺍ

| ﮒ؟ﻝﺍﮔ۷۰ﮒ | ﮔ۴ﮒ۲ﮔﺗﮔﺏ | ﮔ۷۰ﮒﻝﺎﭨﮒ | ﻟﻟﺑ۲ |
|----------|----------|----------|------|
| LSTMTrainer | train() | LSTM | ﮔ۷۰ﮒﻝﺗﮒ؟ﻟ؟­ﻝﭨﻠﭨﻟﺝ |
| TransformerTrainer | train() | Transformer | ﮔ۷۰ﮒﻝﺗﮒ؟ﻟ؟­ﻝﭨﻠﭨﻟﺝ |

### 3.3 ﻟﺍﻝ۷ﮒﺏﻝﺏﭨ

```
ModelTrainingPipeline (ﻠﻝ۷ﮔﭖﮔﺍﺑﺅﺟ?
    ﺅﺟ?    ﻗﻗﻗ ﮔﺍﮔ؟ﻝﮔ؛ﻝ؟۰ﻝ (DVC)
    ﻗﻗﻗ ﻟﭘﮒﮔﺍﻛﺙﺅﺟ?(Optuna)
    ﻗﻗﻗ ﮒ؟ﻠ۹ﻟﺓﻟﺕ۹ (MLflow)
    ﺅﺟ?    ﻗﻗﻗ IModelTrainer.train() (ﮔ۷۰ﮒﻝﺗﮒ؟ﻟ؟­ﻝﭨ)
            ﻗﻗﻗ LSTMTrainer.train()
            ﻗﻗﻗ TransformerTrainer.train()
```

---

## 4. ﻝﺗﮒﺝﮔﮒ۰ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵

### 4.1 IFeatureService v1.0

**ﻟﻟﺑ۲**: ﮒ؟ﻛﺗﻝﺗﮒﺝﮔﮒ۰ﻝﮔ ﮒﮔ۴ﺅﺟ?
**ﮒ؟ﻝﺍﮔ۷۰ﮒ**: FeatureStore

**ﻟﺍﻝ۷ﺅﺟ?*: ﮔ۷۰ﮒﻟ؟­ﻝﭨﻙﮒ۷ﻝﭦﺟﮔ۷ﺅﺟ?
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class FeatureVectorRequest:
    """ﻝﺗﮒﺝﮒﻠﻟﺁﺓﮔﺎ"""
    entity_keys: List[str]
    feature_names: List[str]
    entity_type: str = 'stock'
    request_id: Optional[str] = None


@dataclass
class FeatureVectorResponse:
    """ﻝﺗﮒﺝﮒﻠﮒﮒﭦ"""
    entity_key: str
    feature_values: Dict[str, Any]
    feature_timestamps: Dict[str, datetime]
    request_id: str


@dataclass
class HistoricalFeaturesRequest:
    """ﮒﮒﺎﻝﺗﮒﺝﻟﺁﺓﮔﺎ"""
    entity_keys: List[str]
    feature_names: List[str]
    start_time: datetime
    end_time: datetime
    entity_type: str = 'stock'


class IFeatureService(ABC):
    """ﻝﺗﮒﺝﮔﮒ۰ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ v1.0
    
    ﮒ؟ﻝﺍﮔ۷۰ﮒ:
    - FeatureStore: ﻝﺗﮒﺝﮒ­ﮒ۷ﮔﮒ۰
    
    ﻟﺍﻝ۷ﺅﺟ?
    - ModelTrainingPipeline: ﻟ؟­ﻝﭨﮔﺍﮔ؟ﻟﺓﮒ
    - ModelServingService: ﮒ۷ﻝﭦﺟﮔ۷ﻝﻝﺗﮒﺝ
    """
    
    @abstractmethod
    def get_online_features(
        self,
        request: FeatureVectorRequest
    ) -> List[FeatureVectorResponse]:
        """ﻟﺓﮒﮒ۷ﻝﭦﺟﻝﺗﮒﺝ
        
        Args:
            request: ﻝﺗﮒﺝﻟﺁﺓﮔﺎ
            
        Returns:
            List[FeatureVectorResponse]: ﻝﺗﮒﺝﮒﻠﮒﻟ۰۷
        """
        pass
    
    @abstractmethod
    def get_historical_features(
        self,
        request: HistoricalFeaturesRequest
    ) -> pd.DataFrame:
        """ﻟﺓﮒﮒﮒﺎﻝﺗﮒﺝ
        
        Args:
            request: ﮒﮒﺎﻝﺗﮒﺝﻟﺁﺓﮔﺎ
            
        Returns:
            pd.DataFrame: ﮒﮒﺎﻝﺗﮒﺝﮔﺍﮔ؟
        """
        pass
    
    @abstractmethod
    def register_feature(
        self,
        feature_name: str,
        feature_definition: Dict[str, Any]
    ) -> str:
        """ﮔﺏ۷ﮒﻝﺗﮒﺝ
        
        Args:
            feature_name: ﻝﺗﮒﺝﮒﻝ۶ﺍ
            feature_definition: ﻝﺗﮒﺝﮒ؟ﻛﺗ
            
        Returns:
            str: ﻝﺗﮒﺝID
        """
        pass
```

### 4.2 ﮔ۴ﮒ۲ﮒ؟ﻝﺍﮔ ﮒﺍ

| ﮒ؟ﻝﺍﮔ۷۰ﮒ | ﮔ۴ﮒ۲ﮔﺗﮔﺏ | ﮔﮒ۰ﻝﺎﭨﮒ | ﻟﻟﺑ۲ |
|----------|----------|----------|------|
| FeatureStore | get_online_features() | ﮒ۷ﻝﭦﺟﮔﮒ۰ | ﮒ؟ﮔﭘﻝﺗﮒﺝﮔ۲ﺅﺟ?|
| FeatureStore | get_historical_features() | ﻝ۵ﭨﻝﭦﺟﮔﮒ۰ | ﮔﺗﻠﻝﺗﮒﺝﮔ۲ﺅﺟ?|

### 4.3 ﻛﺕFeatureEngineeringﻝﮒﺅﺟ?
```
FeatureEngineering (ﻝﺗﮒﺝﮒﺓ۴ﻝ۷)
    ﺅﺟ?    ﻗﻗﻗ ﻝﺗﮒﺝﻝﮔ
    ﻗﻗﻗ ﻝﺗﮒﺝﻠﮔ۸
    ﻗﻗﻗ ﻝﺗﮒﺝﮒﮔ۱
    ﻗﻗﻗ ﻟﺝﮒﭦﻟ؟۰ﻝ؟ﮒﻝﻝﺗﮒﺝ
            ﺅﺟ?            ﺅﺟ?FeatureStore (ﻝﺗﮒﺝﮒ­ﮒ۷)
    ﺅﺟ?    ﻗﻗﻗ register_feature() -> ﮔﺏ۷ﮒﻝﺗﮒﺝ
    ﻗﻗﻗ ﮒ­ﮒ۷ﻝﺗﮒﺝﮔﺍﮔ؟
    ﻗﻗﻗ get_online_features() -> ﮔﮒ۰ﻝﺗﮒﺝ
```

---

## 5. ﮔ۴ﮒ۲ﻝﮔ؛ﻝ؟۰ﻝ

### 5.1 ﻝﮔ؛ﮔ۶ﮒﭘﻟ۶ﮒ

1. **ﮒﮒﮒﺙﮒ؟ﺗ**: ﮔﺍﻝﮔ؛ﮒﺟﻠ۰ﭨﮒﮒﮒﺙﮒ؟ﺗﮔ۶ﻝﮔ؛
2. **ﮒﭦﮒﺙﻠﻝ۴**: ﮒﭦﮒﺙﮔ۴ﮒ۲ﻠﮔﮒ3ﻛﺕ۹ﮔﻠﻝ۴
3. **ﻝﮔ؛ﮔ ﻟﺁ**: ﮔﮔﮔ۴ﮒ۲ﻠﮔ ﮔﺏ۷ﻝﮔ؛ﺅﺟ?
### 5.2 ﮒﮔﺑﻟ؟ﺍﮒﺛ

| ﻝﮔ؛ | ﮔ۴ﮔ | ﮒﮔﺑﮒﮒ؟ﺗ | ﮒﺛﺎﮒﮔ۷۰ﮒ |
|------|------|----------|----------|
| v1.0 | 2026-04-03 | ﮒﮒ۶ﻝﮔ؛ | ﮒ ﮒ­ﻟ؟۰ﻝ؟ﻙﮔ۷۰ﮒﻟ؟­ﻝﭨﻙﻝﺗﮒﺝﮔﺅﺟ?|

---

## 6. ﮔ۴ﮒ۲ﻛﺛﺟﻝ۷ﮔﮒ

### 6.1 ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮔ۴ﮒ۲ﻛﺛﺟﻝ۷

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

### 6.2 ﮔ۷۰ﮒﻟ؟­ﻝﭨﮔ۴ﮒ۲ﻛﺛﺟﻝ۷

```python
from model_training_pipeline import ModelTrainingPipeline
from lstm_model import LSTMTrainer

trainer = LSTMTrainer(model, config)
pipeline = ModelTrainingPipeline(trainer, pipeline_config)

result = pipeline.train(training_config)
```

### 6.3 ﻝﺗﮒﺝﮔﮒ۰ﮔ۴ﮒ۲ﻛﺛﺟﻝ۷

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

## 7. ﻠﮒﺛ

### 7.1 ﻝﺕﮒﺏﮔﮔ۰۲

- [FACTOR_CALCULATOR_TECHNICAL_SPECIFICATION](./FACTOR_CALCULATOR_TECHNICAL_SPECIFICATION.md)
- [ALPHA_FACTOR_FACTORY_TECHNICAL_SPECIFICATION](./ALPHA_FACTOR_FACTORY_TECHNICAL_SPECIFICATION.md)
- [QLIB_ALPHA158_TECHNICAL_SPECIFICATION](./QLIB_ALPHA158_TECHNICAL_SPECIFICATION.md)
- [MODEL_TRAINING_PIPELINE_TECHNICAL_SPECIFICATION](./MODEL_TRAINING_PIPELINE_TECHNICAL_SPECIFICATION.md)
- [LSTM_MODEL_TECHNICAL_SPECIFICATION](./LSTM_MODEL_TECHNICAL_SPECIFICATION.md)
- [TRANSFORMER_MODEL_TECHNICAL_SPECIFICATION](./TRANSFORMER_MODEL_TECHNICAL_SPECIFICATION.md)
- [FEATURE_ENGINEERING_TECHNICAL_SPECIFICATION](./FEATURE_ENGINEERING_TECHNICAL_SPECIFICATION.md)
- [FEATURE_STORE_TECHNICAL_SPECIFICATION](./FEATURE_STORE_TECHNICAL_SPECIFICATION.md)

### 7.2 ﮔﺁﻟﺁ­ﺅﺟ?
| ﮔﺁﻟﺁ­ | ﮒ؟ﻛﺗ |
|------|------|
| ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵ | ﮔ۷۰ﮒﻠﺑﻛﭦ۳ﻛﭦﻝﮔ ﮒﮒﮔ۴ﮒ۲ﮒ؟ﺅﺟ?|
| ﮒ ﮒ­ﻟ؟۰ﻝ؟ | ﻛﭨﮒﮒ۶ﮔﺍﮔ؟ﻟ؟۰ﻝ؟ﮒ ﮒ­ﮒﺙﻝﻟﺟﻝ۷ |
| ﮔ۷۰ﮒﻟ؟­ﻝﭨ | ﻛﺛﺟﻝ۷ﮔﺍﮔ؟ﻟ؟­ﻝﭨﮔﭦﮒ۷ﮒ­۵ﻛﺗ ﮔ۷۰ﮒﻝﻟﺟﺅﺟ?|
| ﻝﺗﮒﺝﮔﮒ۰ | ﮔﻛﺝﻝﺗﮒﺝﮔﺍﮔ؟ﻝﮒ­ﮒ۷ﮒﮔ۲ﻝﺑ۱ﮔﺅﺟ?|

---

**ﮔﮔ۰۲ﻝﮔ؛**: v1.0
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-03
**ﻝﭨﺑﮔ۳ﺅﺟ?*: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
