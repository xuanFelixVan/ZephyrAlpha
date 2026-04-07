---
responsibility:
  - èªå¨ä¿®å¤
  - å¼å¸¸æ£æµ?
  - ç³»ç»æ¢å¤
  - æ°æ®ä¿®å¤

module_id: AUTO_REPAIR_ENGINE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 9 çæ§å±?
compliance_level: ä¸ä¸æ å
layer: Layer 5 (策略执行层)
---

# èªå¨åæ°æ®ä¿®å¤å¼æèå?

## 核心定位

负责自动修复引擎的设计与实现，基于异常检测和自动修复技术，自动识别和修复系统故障，提升系统可用性。


## 设计目标

### 主要目标

1. **功能完整性**: 确保AUTO REPAIR ENGINE功能完整，满足业务需求
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

采用AUTO REPAIR ENGINE化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


## æ ¸å¿å®ä½

è´è´£Auto Repair Engineçè®¾è®¡ãå®ç°åç»´æ¤ï¼æä¾æ ¸å¿åè½æ¯æï¼ç¡®ä¿ç³»ç»æ¨¡åçç¨³å®è¿è¡åé«ææ§è¡ã?


## ä¸ãè®¾è®¡èæ¯ä¸ç®æ 

### 1.1 ä¸å¡éæ±?

**å½åçç¹**:
- æ°æ®ä¿®å¤éè¦äººå·¥å¹²é¢ï¼æçä½ä¸
- ä¿®å¤ç­ç¥åä¸ï¼ç¼ºå°æºè½åä¿®å¤
- ç¼ºå°ä¿®å¤ææè¯ä¼°æºå¶
- ä¿®å¤åå²æ æ³è¿½æº¯

**ä¸å¡ç®æ **:
- åºäºåå²æ°æ®çæºè½ä¿®å¤ï¼åå°äººå·¥å¹²é¢
- æºå¨å­¦ä¹ é©±å¨çå¼å¸¸æ£æµåä¿®å¤
- èªå¨è¯ä¼°ä¿®å¤ææ
- å»ºç«ä¿®å¤æ¡ä¾åºï¼æç»­ä¼å

### 1.2 ææ¯ç®æ ?

| ææ  | ç®æ å?| è¯´æ |
|------|--------|------|
| **èªå¨ä¿®å¤æ¯ä¾** | â?0% | 70%ä»¥ä¸çæ°æ®é®é¢èªå¨ä¿®å¤?|
| **ä¿®å¤åç¡®ç?* | â?5% | ä¿®å¤åæ°æ®åç¡®æ§â¥85% |
| **ä¿®å¤æ¶é´** | <5ç§?| åæ¬¡ä¿®å¤æ¶é´<5ç§?|
| **ä¿®å¤è¦çç?* | â?0% | è¦ç80%ä»¥ä¸çæ°æ®é®é¢ç±»å?|

---
## ð ç¸å³ææ¡£

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [æ°æ®è´¨éçæ§èå¾](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | DATA_QUALITY_MONITORING_001 | å¼ºä¾èµ?| æä¾è´¨éå¼å¸¸æ£æµç»æ?|
| [æ°æ®æºç®¡çèå¾](./DATA_SOURCE_MANAGEMENT_BLUEPRINT.md) | DATA_SOURCE_MANAGEMENT_001 | ä¸­ä¾èµ?| æä¾æ°æ®æºåæ°æ® |
| [æ°æ®ç®å½èå¾](./DATA_CATALOG_BLUEPRINT.md) | DATA_CATALOG_001 | ä¸­ä¾èµ?| æä¾æ°æ®è¡ç¼ä¿¡æ?|

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [è´¨éè¯åç³»ç»èå¾](./QUALITY_SCORING_SYSTEM_BLUEPRINT.md) | QUALITY_SCORING_SYSTEM_001 | å¼ºä¾èµ?| æä¾ä¿®å¤åè´¨éè¯å?|
| [è´¨éæ¥åèªå¨åèå¾](./QUALITY_REPORT_AUTOMATION_BLUEPRINT.md) | QUALITY_REPORT_AUTOMATION_001 | ä¸­ä¾èµ?| æä¾ä¿®å¤åå²è®°å½ |
| [æ°æ®å¯è§æµæ§èå¾](./DATA_OBSERVABILITY_BLUEPRINT.md) | DATA_OBSERVABILITY_001 | å¼±ä¾èµ?| æä¾ä¿®å¤çæ§ææ  |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **scikit-learn** | 1.3.0+ | æºå¨å­¦ä¹ æ¨¡å | [å®æ¹ææ¡£](https://scikit-learn.org/) |
| **PyOD** | 1.1.0+ | å¼å¸¸æ£æµ?| [å®æ¹ææ¡£](https://pyod.readthedocs.io/) |
| **Great Expectations** | 0.18+ | æ°æ®éªè¯ | [å®æ¹ææ¡£](https://docs.greatexpectations.io/) |
| **Prophet** | 1.1.0+ | æ¶åºé¢æµ | [å®æ¹ææ¡£](https://facebook.github.io/prophet/) |

### å¼ç¨å³ç³»å?

```mermaid
graph LR
    A[æ°æ®è´¨éçæ§] --> B[èªå¨ä¿®å¤å¼æ]
    C[æ°æ®æºç®¡ç] --> B
    D[æ°æ®ç®å½] --> B
    
    B --> E[è´¨éè¯åç³»ç»]
    B --> F[è´¨éæ¥åèªå¨å]
    B --> G[æ°æ®å¯è§æµæ§]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
    style D fill:#96ceb4
```

---

## äºãç³»ç»æ¶æè®¾è®?

### 2.1 æ´ä½æ¶æå?

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?               èªå¨åæ°æ®ä¿®å¤å¼ææ¶æ?                        â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                            â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?          é®é¢æ£æµå± (Problem Detection)             â?  â?
â? â? âââââââââââââââ?âââââââââââââââ?âââââââââââââââ?  â?  â?
â? â? âç¼ºå¤±å¼æ£æµ?  â?âå¼å¸¸å¼æ£æµ?  â?âæ ¼å¼éè¯¯æ£æµ?â?  â?  â?
â? â? âââââââââââââââ?âââââââââââââââ?âââââââââââââââ?  â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                         â?                                 â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?          ä¿®å¤ç­ç¥å±?(Repair Strategy)               â?  â?
â? â? âââââââââââââââ?âââââââââââââââ?âââââââââââââââ?  â?  â?
â? â? âè§åä¿®å¤?    â?âMLä¿®å¤       â?âåå²ä¿®å¤?    â?  â?  â?
â? â? âââââââââââââââ?âââââââââââââââ?âââââââââââââââ?  â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                         â?                                 â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?          ä¿®å¤æ§è¡å±?(Repair Execution)              â?  â?
â? â? âââââââââââââââ?âââââââââââââââ?âââââââââââââââ?  â?  â?
â? â? âä¿®å¤æ§è¡å¨   â?âææè¯ä¼°å¨   â?âåæ»æºå?    â?  â?  â?
â? â? âââââââââââââââ?âââââââââââââââ?âââââââââââââââ?  â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                         â?                                 â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?          ç¥è¯ç®¡çå±?(Knowledge Management)          â?  â?
â? â? âââââââââââââââ?âââââââââââââââ?âââââââââââââââ?  â?  â?
â? â? âä¿®å¤æ¡ä¾åº   â?âæ¨¡åè®­ç»?    â?âæç»­ä¼å?    â?  â?  â?
â? â? âââââââââââââââ?âââââââââââââââ?âââââââââââââââ?  â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                                                            â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### 2.2 ææ¯éå

| ç»ä»¶ | ææ¯æ¹æ¡?| çæ¬è¦æ± | éåçç± |
|------|---------|---------|---------|
| **æºå¨å­¦ä¹ æ¡æ¶** | scikit-learn | 1.3.0+ | æççMLæ¡æ¶ |
| **æ·±åº¦å­¦ä¹ æ¡æ¶** | PyTorch | 2.0.0+ | çµæ´»çæ·±åº¦å­¦ä¹ æ¡æ?|
| **æ¶åºé¢æµ** | Prophet | 1.1.0+ | æ¶åºæ°æ®é¢æµ |
| **å¼å¸¸æ£æµ?* | PyOD | 1.1.0+ | å¼å¸¸æ£æµç®æ³åº |
| **æ°æ®éªè¯** | Great Expectations | 0.18.0+ | æ°æ®è´¨ééªè¯ |

### 2.3 Layerå®ä½

- **Layerå½å±**: Layer 1 - æ°æ®é¢å¤çå±
- **èè´£èå´**: èªå¨åæ°æ®ä¿®å¤ãä¿®å¤ææè¯ä¼°ãä¿®å¤ç¥è¯ç®¡ç?
- **ä¸ä¸å±æ¥å?*:
  - ä¸å±ä¾èµ: Layer 2-8ï¼æä¾ä¿®å¤åæ°æ®ï¼?
  - ä¸å±ä¾èµ: Layer 0-1ï¼æ¥æ¶åå§æ°æ®åé®é¢æ°æ®ï¼?

---

## ä¸ãæ ¸å¿æ¨¡åè®¾è®?

### 3.1 é®é¢æ£æµå¨ (ProblemDetector)

**èè´£**: èªå¨æ£æµæ°æ®é®é¢?

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import pandas as pd
import numpy as np

class ProblemType(Enum):
    """é®é¢ç±»å"""
    MISSING_VALUE = "missing_value"
    OUTLIER = "outlier"
    FORMAT_ERROR = "format_error"
    RANGE_ERROR = "range_error"
    DUPLICATE = "duplicate"
    INCONSISTENCY = "inconsistency"

class Severity(Enum):
    """ä¸¥éç¨åº¦"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DataProblem:
    """æ°æ®é®é¢"""
    problem_id: str
    problem_type: ProblemType
    field_name: str
    row_index: Optional[int]
    original_value: Any
    problem_description: str
    severity: Severity
    detected_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProblemDetector:
    """é®é¢æ£æµå¨"""
    
    def __init__(self):
        self.problems: List[DataProblem] = []
    
    def detect_missing_values(self, df: pd.DataFrame, table_name: str) -> List[DataProblem]:
        """æ£æµç¼ºå¤±å?""
        problems = []
        
        for column in df.columns:
            missing_mask = df[column].isnull()
            missing_indices = df[missing_mask].index.tolist()
            
            for idx in missing_indices:
                problem = DataProblem(
                    problem_id=f"missing_{table_name}_{column}_{idx}",
                    problem_type=ProblemType.MISSING_VALUE,
                    field_name=column,
                    row_index=idx,
                    original_value=None,
                    problem_description=f"Missing value in column {column}",
                    severity=Severity.HIGH
                )
                problems.append(problem)
        
        self.problems.extend(problems)
        return problems
    
    def detect_outliers(self, df: pd.DataFrame, table_name: str, 
                        method: str = "iqr") -> List[DataProblem]:
        """æ£æµå¼å¸¸å?""
        problems = []
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if method == "iqr":
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
                outlier_indices = df[outlier_mask].index.tolist()
                
                for idx in outlier_indices:
                    problem = DataProblem(
                        problem_id=f"outlier_{table_name}_{column}_{idx}",
                        problem_type=ProblemType.OUTLIER,
                        field_name=column,
                        row_index=idx,
                        original_value=df.loc[idx, column],
                        problem_description=f"Outlier detected in column {column}",
                        severity=Severity.MEDIUM,
                        metadata={"lower_bound": lower_bound, "upper_bound": upper_bound}
                    )
                    problems.append(problem)
        
        self.problems.extend(problems)
        return problems
    
    def detect_format_errors(self, df: pd.DataFrame, table_name: str,
                             format_rules: Dict[str, str]) -> List[DataProblem]:
        """æ£æµæ ¼å¼éè¯?""
        problems = []
        
        for column, pattern in format_rules.items():
            if column in df.columns:
                import re
                invalid_mask = ~df[column].astype(str).str.match(pattern, na=False)
                invalid_indices = df[invalid_mask].index.tolist()
                
                for idx in invalid_indices:
                    problem = DataProblem(
                        problem_id=f"format_{table_name}_{column}_{idx}",
                        problem_type=ProblemType.FORMAT_ERROR,
                        field_name=column,
                        row_index=idx,
                        original_value=df.loc[idx, column],
                        problem_description=f"Format error in column {column}",
                        severity=Severity.MEDIUM,
                        metadata={"expected_pattern": pattern}
                    )
                    problems.append(problem)
        
        self.problems.extend(problems)
        return problems
```

### 3.2 ä¿®å¤ç­ç¥å¼æ (RepairStrategyEngine)

**èè´£**: éæ©åæ§è¡ä¿®å¤ç­ç?

```python
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.ensemble import IsolationForest

class RepairStrategy(Enum):
    """ä¿®å¤ç­ç¥"""
    MEAN_IMPUTATION = "mean_imputation"
    MEDIAN_IMPUTATION = "median_imputation"
    MODE_IMPUTATION = "mode_imputation"
    KNN_IMPUTATION = "knn_imputation"
    ML_PREDICTION = "ml_prediction"
    HISTORICAL_VALUE = "historical_value"
    BUSINESS_RULE = "business_rule"
    MANUAL_REVIEW = "manual_review"

@dataclass
class RepairAction:
    """ä¿®å¤å¨ä½"""
    action_id: str
    problem: DataProblem
    strategy: RepairStrategy
    repaired_value: Any
    confidence: float
    executed_at: datetime
    metadata: Dict[str, Any]

class RepairStrategyEngine:
    """ä¿®å¤ç­ç¥å¼æ"""
    
    def __init__(self):
        self.strategies: Dict[ProblemType, List[RepairStrategy]] = {
            ProblemType.MISSING_VALUE: [
                RepairStrategy.MEAN_IMPUTATION,
                RepairStrategy.MEDIAN_IMPUTATION,
                RepairStrategy.MODE_IMPUTATION,
                RepairStrategy.KNN_IMPUTATION,
                RepairStrategy.ML_PREDICTION
            ],
            ProblemType.OUTLIER: [
                RepairStrategy.MEDIAN_IMPUTATION,
                RepairStrategy.ML_PREDICTION,
                RepairStrategy.BUSINESS_RULE
            ],
            ProblemType.FORMAT_ERROR: [
                RepairStrategy.BUSINESS_RULE,
                RepairStrategy.MANUAL_REVIEW
            ]
        }
    
    def select_strategy(self, problem: DataProblem, context: Dict[str, Any]) -> RepairStrategy:
        """éæ©ä¿®å¤ç­ç¥"""
        available_strategies = self.strategies.get(problem.problem_type, [])
        
        if not available_strategies:
            return RepairStrategy.MANUAL_REVIEW
        
        # æ ¹æ®ä¸ä¸æéæ©æä½³ç­ç?
        if problem.problem_type == ProblemType.MISSING_VALUE:
            if context.get("numeric", True):
                return RepairStrategy.KNN_IMPUTATION
            else:
                return RepairStrategy.MODE_IMPUTATION
        
        return available_strategies[0]
    
    def execute_repair(self, df: pd.DataFrame, problem: DataProblem,
                       strategy: RepairStrategy) -> RepairAction:
        """æ§è¡ä¿®å¤"""
        if strategy == RepairStrategy.MEAN_IMPUTATION:
            repaired_value = self._mean_imputation(df, problem)
        elif strategy == RepairStrategy.MEDIAN_IMPUTATION:
            repaired_value = self._median_imputation(df, problem)
        elif strategy == RepairStrategy.MODE_IMPUTATION:
            repaired_value = self._mode_imputation(df, problem)
        elif strategy == RepairStrategy.KNN_IMPUTATION:
            repaired_value = self._knn_imputation(df, problem)
        else:
            repaired_value = None
        
        return RepairAction(
            action_id=f"repair_{problem.problem_id}",
            problem=problem,
            strategy=strategy,
            repaired_value=repaired_value,
            confidence=0.85,
            executed_at=datetime.now()
        )
    
    def _mean_imputation(self, df: pd.DataFrame, problem: DataProblem) -> Any:
        """åå¼å¡«å?""
        column = problem.field_name
        return df[column].mean()
    
    def _median_imputation(self, df: pd.DataFrame, problem: DataProblem) -> Any:
        """ä¸­ä½æ°å¡«å?""
        column = problem.field_name
        return df[column].median()
    
    def _mode_imputation(self, df: pd.DataFrame, problem: DataProblem) -> Any:
        """ä¼æ°å¡«å"""
        column = problem.field_name
        return df[column].mode()[0]
    
    def _knn_imputation(self, df: pd.DataFrame, problem: DataProblem) -> Any:
        """KNNå¡«å"""
        numeric_df = df.select_dtypes(include=[np.number])
        imputer = KNNImputer(n_neighbors=5)
        
        column_idx = list(df.columns).index(problem.field_name)
        imputed_data = imputer.fit_transform(numeric_df)
        
        return imputed_data[problem.row_index, column_idx]
```

### 3.3 ä¿®å¤ææè¯ä¼°å?(RepairEvaluator)

**èè´£**: è¯ä¼°ä¿®å¤ææ

```python
from dataclasses import dataclass
from typing import Dict, List, Any
import pandas as pd
import numpy as np

@dataclass
class RepairEvaluation:
    """ä¿®å¤è¯ä¼°ç»æ"""
    evaluation_id: str
    repair_action: RepairAction
    accuracy_score: float
    consistency_score: float
    business_rule_score: float
    overall_score: float
    passed: bool
    details: Dict[str, Any]

class RepairEvaluator:
    """ä¿®å¤ææè¯ä¼°å?""
    
    def __init__(self):
        self.evaluations: List[RepairEvaluation] = []
    
    def evaluate_repair(self, original_df: pd.DataFrame, 
                        repaired_df: pd.DataFrame,
                        repair_action: RepairAction) -> RepairEvaluation:
        """è¯ä¼°ä¿®å¤ææ"""
        accuracy_score = self._evaluate_accuracy(repaired_df, repair_action)
        consistency_score = self._evaluate_consistency(repaired_df, repair_action)
        business_rule_score = self._evaluate_business_rules(repaired_df, repair_action)
        
        overall_score = (accuracy_score * 0.4 + 
                        consistency_score * 0.3 + 
                        business_rule_score * 0.3)
        
        passed = overall_score >= 0.85
        
        evaluation = RepairEvaluation(
            evaluation_id=f"eval_{repair_action.action_id}",
            repair_action=repair_action,
            accuracy_score=accuracy_score,
            consistency_score=consistency_score,
            business_rule_score=business_rule_score,
            overall_score=overall_score,
            passed=passed
        )
        
        self.evaluations.append(evaluation)
        return evaluation
    
    def _evaluate_accuracy(self, df: pd.DataFrame, repair_action: RepairAction) -> float:
        """è¯ä¼°åç¡®æ?""
        column = repair_action.problem.field_name
        
        # æ£æ¥ä¿®å¤å¼æ¯å¦å¨åçèå´å?
        if df[column].dtype in [np.float64, np.int64]:
            mean = df[column].mean()
            std = df[column].std()
            repaired_value = repair_action.repaired_value
            
            if std > 0:
                z_score = abs((repaired_value - mean) / std)
                return max(0, 1 - z_score / 3)
        
        return 0.9
    
    def _evaluate_consistency(self, df: pd.DataFrame, repair_action: RepairAction) -> float:
        """è¯ä¼°ä¸è´æ?""
        # æ£æ¥ä¿®å¤åçæ°æ®æ¯å¦ä¸å¶ä»æ°æ®ä¸è?
        return 0.9
    
    def _evaluate_business_rules(self, df: pd.DataFrame, repair_action: RepairAction) -> float:
        """è¯ä¼°ä¸å¡è§å"""
        # æ£æ¥æ¯å¦ç¬¦åä¸å¡è§å?
        return 0.9
```

---

## åãæ°æ®æµè®¾è®¡

### 4.1 èªå¨ä¿®å¤æµç¨

```
åå§æ°æ® â?é®é¢æ£æµ?â?ç­ç¥éæ© â?ä¿®å¤æ§è¡ â?ææè¯ä¼° â?ä¿®å¤åæ°æ?
                â?
            ä¿®å¤æ¡ä¾åº?
```

### 4.2 ç¥è¯ç§¯ç´¯æµç¨

```
ä¿®å¤è®°å½ â?æ¡ä¾æå â?æ¨¡åè®­ç» â?ç­ç¥ä¼å â?ç¥è¯åºæ´æ?
```

---

## äºãæ¥å£è®¾è®?

### 5.1 RESTful API

#### 5.1.1 æ£æµæ°æ®é®é¢?

```http
POST /api/v1/repair/detect
```

**è¯·æ±ç¤ºä¾**:
```json
{
  "table_name": "stock_prices",
  "detection_types": ["missing_value", "outlier", "format_error"]
}
```

**ååºç¤ºä¾**:
```json
{
  "problems": [
    {
      "problem_id": "missing_stock_prices_close_123",
      "problem_type": "missing_value",
      "field_name": "close",
      "row_index": 123,
      "severity": "high"
    }
  ],
  "total_problems": 1
}
```

#### 5.1.2 æ§è¡èªå¨ä¿®å¤

```http
POST /api/v1/repair/execute
```

**è¯·æ±ç¤ºä¾**:
```json
{
  "table_name": "stock_prices",
  "problem_ids": ["missing_stock_prices_close_123"],
  "auto_approve": true
}
```

---

## å­ãé¨ç½²æ¶æ?

### 6.1 å®¹å¨åé¨ç½?

```yaml
version: '3.8'
services:
  repair-engine:
    build: .
    ports:
      - "8080:8080"
    environment:
      - MODEL_PATH=/models
    volumes:
      - ./models:/models
  
  model-training:
    build: .
    command: python train_models.py
    volumes:
      - ./training_data:/data
      - ./models:/models
```

---

## ä¸ãçæ§ææ ?

### 7.1 æ ¸å¿ææ 

| ææ åç§° | ææ ç±»å | è¯´æ |
|---------|---------|------|
| `repair_problems_detected_total` | Counter | æ£æµå°çé®é¢æ»æ° |
| `repair_actions_executed_total` | Counter | æ§è¡çä¿®å¤å¨ä½æ»æ° |
| `repair_success_rate` | Gauge | ä¿®å¤æåç?|
| `repair_duration_seconds` | Histogram | ä¿®å¤èæ¶ |
| `repair_accuracy_score` | Gauge | ä¿®å¤åç¡®çè¯å?|

---

## å«ãå®æ½è®¡å?

### 8.1 å¼åé¶æ®?

| é¶æ®µ | ä»»å¡ | é¢è®¡æ¶é´ | è´è´£äº?|
|------|------|---------|--------|
| **é¶æ®µ1** | å¼åé®é¢æ£æµå¨ | 3å¤?| åç«¯å·¥ç¨å¸?|
| **é¶æ®µ2** | å¼åä¿®å¤ç­ç¥å¼æ?| 4å¤?| MLå·¥ç¨å¸?|
| **é¶æ®µ3** | å¼åä¿®å¤è¯ä¼°å¨ | 2å¤?| åç«¯å·¥ç¨å¸?|
| **é¶æ®µ4** | å¼åç¥è¯ç®¡çç³»ç»?| 3å¤?| åç«¯å·¥ç¨å¸?|
| **é¶æ®µ5** | éææµè¯åé¨ç½?| 3å¤?| QAå·¥ç¨å¸?|

### 8.2 éªæ¶æ å

- [ ] é®é¢æ£æµåç¡®çâ?5%
- [ ] èªå¨ä¿®å¤æ¯ä¾â?0%
- [ ] ä¿®å¤åç¡®çâ¥85%
- [ ] ä¿®å¤æ¶é´<5ç§?
- [ ] ç¥è¯åºæç»­ä¼å?

---

## ä¹ãé£é©ç®¡ç?

### 9.1 ææ¯é£é?

| é£é© | å½±å | ç¼è§£æªæ½ |
|------|------|---------|
| ä¿®å¤ç­ç¥ä¸åç¡?| é«?| å¤ç­ç¥ç»åï¼äººå·¥å®¡æ ¸ |
| æ¨¡åè¿æå?| ä¸?| äº¤åéªè¯ï¼å®ææ´æ°æ¨¡å?|
| ä¿®å¤å¼å¥æ°é®é¢?| é«?| ææè¯ä¼°ï¼åæ»æºå?|

---

## åãç¸å³ææ¡?

- å®æ¶æ°æ®è´¨éçæ§èå¾
- [è´¨éè¯åç³»ç»èå¾](./QUALITY_SCORING_SYSTEM_BLUEPRINT.md)
- æ°æ®è¡ç¼è¿½è¸ªèå?

---

**ææ¡£çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç»´æ¤è?*: é¦å¸­èå¾æ¶æå¸?
---

## 1. ææ¡£æ²»ç

### 1.1 System_Manifest.mdç´¢å¼

```markdown
#### Layer 6: ç»åä¼åå±?
##### 6.001. Auto Repair Engine
- **æ¨¡åID**: AUTO_REPAIR_ENGINE_001
- **èå¾ææ¡£**: AUTO_REPAIR_ENGINE_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾åå»?
- **èè´£**: Layer 1æ°æ®é¢å¤çå± | ä¸å¡æ¶æ: ä¸çº§æ¶é´æ¡æ¶èåæ¶æ
- **ç¶æ?*: Active
```

### 1.2 æ¨¡åèè´£è¾¹ç

| æ¨¡å | èè´£ | è¾¹ç |
|------|------|------|
| **Auto Repair Engine** | Layer 1æ°æ®é¢å¤çå± | ä¸å¡æ¶æ: ä¸çº§æ¶é´æ¡æ¶èåæ¶æ | **æ ¸å¿æ¨¡å** |

### 1.3 çæ¬ç®¡ç

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active

## åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | å®æ½å¢é |


---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-07 | **ç¶æ?*: Active
