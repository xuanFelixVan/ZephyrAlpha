---
module_id: UNIFIED_INTERFACE_CONTRACT_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 首席技术评审官
standard_type: 接口契约规范
applicable_scope: Layer 4 机器学习层及相关模块
compliance_level: 专业标准
---

# 统一接口契约规范 v1.0

> **文档版本**: v1.0
> **创建日期**: 2026-04-03
> **适用范围**: Layer 4 机器学习层及相关模块
> **目的**: 消除接口重复定义，建立统一的接口契�?
---

## 1. 概述

### 1.1 文档目的

本文档定义了机器学习层及相关模块的统一接口契约，解决以下问题：
- 接口定义重复（因子计算、模型训练、特征服务）
- 职责边界不清
- 调用关系混乱

### 1.2 适用模块

| 模块 | 接口类型 | 契约版本 |
|------|----------|----------|
| FactorCalculator | 因子计算 | IFactorCalculator v1.0 |
| AlphaFactorFactory | 因子计算 | IFactorCalculator v1.0 |
| QlibAlpha158 | 因子计算 | IFactorCalculator v1.0 |
| ModelTrainingPipeline | 模型训练 | IModelTrainer v1.0 |
| LSTMModel | 模型训练 | IModelTrainer v1.0 |
| TransformerModel | 模型训练 | IModelTrainer v1.0 |
| FeatureEngineering | 特征服务 | IFeatureService v1.0 |
| FeatureStore | 特征服务 | IFeatureService v1.0 |

---

## 2. 因子计算接口契约

### 2.1 IFactorCalculator v1.0

**职责**: 定义因子计算的标准接�?
**实现模块**: FactorCalculator (Layer 2), QlibAlpha158 (Layer 4)

**调用�?*: AlphaFactorFactory, 策略引擎

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class FactorInput:
    """因子计算输入"""
    instruments: List[str]
    start_date: datetime
    end_date: datetime
    data: Optional[pd.DataFrame] = None
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class FactorOutput:
    """因子计算输出"""
    factor_values: pd.DataFrame
    factor_names: List[str]
    calculation_time: float
    metadata: Dict[str, Any]


class IFactorCalculator(ABC):
    """因子计算接口契约 v1.0
    
    实现模块:
    - FactorCalculator: 基础因子计算 (Layer 2)
    - QlibAlpha158: AI因子计算 (Layer 4)
    
    调用�?
    - AlphaFactorFactory: 因子筛选和合成
    - 策略引擎: 直接使用因子
    """
    
    @abstractmethod
    def calculate_factors(
        self,
        factor_input: FactorInput
    ) -> FactorOutput:
        """计算因子
        
        Args:
            factor_input: 因子计算输入
            
        Returns:
            FactorOutput: 因子计算结果
            
        Raises:
            FactorCalculationError: 因子计算失败
            InvalidInputError: 输入参数无效
        """
        pass
    
    @abstractmethod
    def get_factor_definitions(self) -> Dict[str, Dict[str, Any]]:
        """获取因子定义
        
        Returns:
            Dict[str, Dict]: 因子名称 -> 因子定义
        """
        pass
    
    @abstractmethod
    def validate_input(self, factor_input: FactorInput) -> bool:
        """验证输入参数
        
        Args:
            factor_input: 因子计算输入
            
        Returns:
            bool: 验证是否通过
        """
        pass
```

### 2.2 接口实现映射

| 实现模块 | 接口方法 | 因子类型 | Layer |
|----------|----------|----------|-------|
| FactorCalculator | calculate_factors | 价值、成长、动量、技术指�?| Layer 2 |
| QlibAlpha158 | calculate_factors | Alpha158 AI因子 | Layer 4 |
| BarraStyleFactorCalculator | calculate_factors | 风格因子 | Layer 6 |

### 2.3 调用关系

```
AlphaFactorFactory
    ├── FactorCalculator.calculate_factors() -> 基础因子
    ├── QlibAlpha158.calculate_factors() -> AI因子
    └── 内部筛选和合成逻辑
```

---

## 3. 模型训练接口契约

### 3.1 IModelTrainer v1.0

**职责**: 定义模型训练的标准接�?
**实现模块**: LSTMTrainer, TransformerTrainer

**调用�?*: ModelTrainingPipeline

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class TrainingConfig:
    """训练配置"""
    num_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    early_stop_patience: int = 10
    validation_split: float = 0.2
    device: str = 'cuda'
    checkpoint_dir: str = './checkpoints'


@dataclass
class TrainingResult:
    """训练结果"""
    model_id: str
    training_history: Dict[str, List[float]]
    best_epoch: int
    best_val_loss: float
    training_time: float
    model_path: str
    metrics: Dict[str, float]


class IModelTrainer(ABC):
    """模型训练接口契约 v1.0
    
    实现模块:
    - LSTMTrainer: LSTM模型训练�?    - TransformerTrainer: Transformer模型训练�?    
    调用�?
    - ModelTrainingPipeline: 通用训练流水�?    """
    
    @abstractmethod
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> TrainingResult:
        """训练模型
        
        Args:
            X_train: 训练特征
            y_train: 训练标签
            X_val: 验证特征
            y_val: 验证标签
            
        Returns:
            TrainingResult: 训练结果
        """
        pass
    
    @abstractmethod
    def save_model(self, path: str) -> None:
        """保存模型
        
        Args:
            path: 保存路径
        """
        pass
    
    @abstractmethod
    def load_model(self, path: str) -> None:
        """加载模型
        
        Args:
            path: 模型路径
        """
        pass
    
    @abstractmethod
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置
        
        Returns:
            Dict: 模型配置
        """
        pass
```

### 3.2 接口实现映射

| 实现模块 | 接口方法 | 模型类型 | 职责 |
|----------|----------|----------|------|
| LSTMTrainer | train() | LSTM | 模型特定训练逻辑 |
| TransformerTrainer | train() | Transformer | 模型特定训练逻辑 |

### 3.3 调用关系

```
ModelTrainingPipeline (通用流水�?
    �?    ├── 数据版本管理 (DVC)
    ├── 超参数优�?(Optuna)
    ├── 实验跟踪 (MLflow)
    �?    └── IModelTrainer.train() (模型特定训练)
            ├── LSTMTrainer.train()
            └── TransformerTrainer.train()
```

---

## 4. 特征服务接口契约

### 4.1 IFeatureService v1.0

**职责**: 定义特征服务的标准接�?
**实现模块**: FeatureStore

**调用�?*: 模型训练、在线推�?
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class FeatureVectorRequest:
    """特征向量请求"""
    entity_keys: List[str]
    feature_names: List[str]
    entity_type: str = 'stock'
    request_id: Optional[str] = None


@dataclass
class FeatureVectorResponse:
    """特征向量响应"""
    entity_key: str
    feature_values: Dict[str, Any]
    feature_timestamps: Dict[str, datetime]
    request_id: str


@dataclass
class HistoricalFeaturesRequest:
    """历史特征请求"""
    entity_keys: List[str]
    feature_names: List[str]
    start_time: datetime
    end_time: datetime
    entity_type: str = 'stock'


class IFeatureService(ABC):
    """特征服务接口契约 v1.0
    
    实现模块:
    - FeatureStore: 特征存储服务
    
    调用�?
    - ModelTrainingPipeline: 训练数据获取
    - ModelServingService: 在线推理特征
    """
    
    @abstractmethod
    def get_online_features(
        self,
        request: FeatureVectorRequest
    ) -> List[FeatureVectorResponse]:
        """获取在线特征
        
        Args:
            request: 特征请求
            
        Returns:
            List[FeatureVectorResponse]: 特征向量列表
        """
        pass
    
    @abstractmethod
    def get_historical_features(
        self,
        request: HistoricalFeaturesRequest
    ) -> pd.DataFrame:
        """获取历史特征
        
        Args:
            request: 历史特征请求
            
        Returns:
            pd.DataFrame: 历史特征数据
        """
        pass
    
    @abstractmethod
    def register_feature(
        self,
        feature_name: str,
        feature_definition: Dict[str, Any]
    ) -> str:
        """注册特征
        
        Args:
            feature_name: 特征名称
            feature_definition: 特征定义
            
        Returns:
            str: 特征ID
        """
        pass
```

### 4.2 接口实现映射

| 实现模块 | 接口方法 | 服务类型 | 职责 |
|----------|----------|----------|------|
| FeatureStore | get_online_features() | 在线服务 | 实时特征检�?|
| FeatureStore | get_historical_features() | 离线服务 | 批量特征检�?|

### 4.3 与FeatureEngineering的协�?
```
FeatureEngineering (特征工程)
    �?    ├── 特征生成
    ├── 特征选择
    ├── 特征变换
    └── 输出计算后的特征
            �?            �?FeatureStore (特征存储)
    �?    ├── register_feature() -> 注册特征
    ├── 存储特征数据
    └── get_online_features() -> 服务特征
```

---

## 5. 接口版本管理

### 5.1 版本控制规则

1. **向后兼容**: 新版本必须向后兼容旧版本
2. **废弃通知**: 废弃接口需提前3个月通知
3. **版本标识**: 所有接口需标注版本�?
### 5.2 变更记录

| 版本 | 日期 | 变更内容 | 影响模块 |
|------|------|----------|----------|
| v1.0 | 2026-04-03 | 初始版本 | 因子计算、模型训练、特征服�?|

---

## 6. 接口使用指南

### 6.1 因子计算接口使用

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

### 6.2 模型训练接口使用

```python
from model_training_pipeline import ModelTrainingPipeline
from lstm_model import LSTMTrainer

trainer = LSTMTrainer(model, config)
pipeline = ModelTrainingPipeline(trainer, pipeline_config)

result = pipeline.train(training_config)
```

### 6.3 特征服务接口使用

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

## 7. 附录

### 7.1 相关文档

- [FACTOR_CALCULATOR_TECHNICAL_SPECIFICATION](./FACTOR_CALCULATOR_TECHNICAL_SPECIFICATION.md)
- [ALPHA_FACTOR_FACTORY_TECHNICAL_SPECIFICATION](./ALPHA_FACTOR_FACTORY_TECHNICAL_SPECIFICATION.md)
- [QLIB_ALPHA158_TECHNICAL_SPECIFICATION](./QLIB_ALPHA158_TECHNICAL_SPECIFICATION.md)
- [MODEL_TRAINING_PIPELINE_TECHNICAL_SPECIFICATION](./MODEL_TRAINING_PIPELINE_TECHNICAL_SPECIFICATION.md)
- [LSTM_MODEL_TECHNICAL_SPECIFICATION](./LSTM_MODEL_TECHNICAL_SPECIFICATION.md)
- [TRANSFORMER_MODEL_TECHNICAL_SPECIFICATION](./TRANSFORMER_MODEL_TECHNICAL_SPECIFICATION.md)
- [FEATURE_ENGINEERING_TECHNICAL_SPECIFICATION](./FEATURE_ENGINEERING_TECHNICAL_SPECIFICATION.md)
- [FEATURE_STORE_TECHNICAL_SPECIFICATION](./FEATURE_STORE_TECHNICAL_SPECIFICATION.md)

### 7.2 术语�?
| 术语 | 定义 |
|------|------|
| 接口契约 | 模块间交互的标准化接口定�?|
| 因子计算 | 从原始数据计算因子值的过程 |
| 模型训练 | 使用数据训练机器学习模型的过�?|
| 特征服务 | 提供特征数据的存储和检索服�?|

---

**文档版本**: v1.0
**创建日期**: 2026-04-03
**维护�?*: 首席技术评审官
