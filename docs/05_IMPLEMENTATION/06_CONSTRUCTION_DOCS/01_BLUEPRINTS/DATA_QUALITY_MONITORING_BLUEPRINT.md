---
module_id: DATA_QUALITY_MONITORING_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: 专业标准
responsibility:
  - 数据质量监控
  - 质量规则验证
  - 质量报告
  - 质量预警
layer: Layer 5.1 (数据处理)
---

# DATA QUALITY MONITORING BLUEPRINT

## 核心定位

负责数据质量监控的设计与实现，基于质量规则，实时监控数据质量，及时发现数据问题。 提供数据管理、查询、更新功能，确保数据质量和一致性。


## 设计目标

### 主要目标

1. **功能完整性**: 确保DATA QUALITY MONITORING功能完整，满足业务需求
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

采用DATA QUALITY MONITORING化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控


## 核心定位

**åä¸èè´£**: æ°æ®è´¨éçæ§ä¸å¼å¸¸æ£æµï¼ä¿éå
¨ç³»ç»æ°æ®è´¨é?

### 职责边界

**â?æ ¸å¿èè´£**:

- 质量规则管理
- è´¨éæ£æµæ§è¡?
- 异常检测与识别
- 质量报告生成

**â?éèè´£èå?*:
- 数据采集
- 数据存储
- æ°æ®æ¸
洗
- 数据修复

## ð¯ æ¨¡åå®ä½ä¸èè´?

### 层级定位

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?          æ¸
é£éåç³»ç» - ä¸çº§æ¶é´æ¡æ¶æ¶æ                â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â? ç¬¬ä¸çº§ï¼å®è§é
ç½®å±ï¼å­£åº¦/å¹´åº¦ï¼?                        â?
â? ç¬¬äºçº§ï¼ä¸­è§ç­ç¥å±ï¼å¨åº¦/æ¥åº¦ï¼?                        â?
â? ç¬¬ä¸çº§ï¼å¾®è§æ§è¡å±ï¼æ¥å
/åé/ç§çº§ï¼?                   â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?          æ°æ®è´¨éçæ§ç³»ç»ï¼æ¬æ¨¡åï¼?                    â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â? è´¨éè§åå¼æ  â? å¼å¸¸æ£æµå¨  â? è´¨éæ¥åçæå? â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### 核心职责

| èè´£ç±»å« | å
·ä½èè´£ | è¾åºäº§ç© |
|---------|---------|---------|
| **è´¨éè§åç®¡ç** | å®ä¹åç®¡çæ°æ®è´¨éè§å?| è´¨éè§ååº?|
| **è´¨éæ£æµ?* | æ§è¡æ°æ®è´¨éæ£æ?| è´¨éæ£æµç»æ?|
| **å¼å¸¸æ£æµ?* | è¯å«æ°æ®å¼å¸¸åå¼å¸¸æ¨¡å¼?| å¼å¸¸æ¥å |
| **è´¨éæ¥å** | çæè´¨éæ¥ååè¶å¿åæ?| è´¨éæ¥å |
| **åè­¦éç¥** | åéè´¨éåè­?| åè­¦æ¶æ¯ |

### éèè´£è¾¹ç?

- â?**æ°æ®éé**: ç±ç»ä¸æ°æ®åºç¡è®¾æ½è´è´£
- â?**æ°æ®å­å¨**: ç±ç»ä¸æ°æ®åºç¡è®¾æ½è´è´£
- â?**æ°æ®æ¸
洗**: 由统一数据基础设施负责
- â?**æ°æ®ä¿®å¤**: ç±æ°æ®æ²»çå¹³å°è´è´?

---

## ð ç¸å
³ææ¡£

### 上游依赖

| 文档名称 | module_id | 依赖类型 | 说明 |
|---------|-----------|---------|------|
| [æ°æ®æºç®¡çèå¾](./DATA_SOURCE_MANAGEMENT_BLUEPRINT.md) | DATA_SOURCE_MANAGEMENT_001 | å¼ºä¾èµ?| æä¾æ°æ®æºè¿æ¥åå
æ°æ?|
| [æ°æ®å®å
¨åè§èå¾](./DATA_SECURITY_COMPLIANCE_BLUEPRINT.md) | DATA_SECURITY_COMPLIANCE_001 | ä¸­ä¾èµ?| æä¾æ°æ®å®å
¨ç­ç¥ |
| [é«æ§è½æ°æ®ç®¡éèå¾](./HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md) | HIGH_PERFORMANCE_DATA_PIPELINE_001 | å¼ºä¾èµ?| æä¾å®æ¶æ°æ®æµ?|

### 下游依赖

| 文档名称 | module_id | 依赖类型 | 说明 |
|---------|-----------|---------|------|
| [èªå¨ä¿®å¤å¼æèå¾](./AUTO_REPAIR_ENGINE_BLUEPRINT.md) | AUTO_REPAIR_ENGINE_001 | å¼ºä¾èµ?| æ¥æ¶è´¨éå¼å¸¸è¿è¡ä¿®å¤ |
| [è´¨éè¯åç³»ç»èå¾](./QUALITY_SCORING_SYSTEM_BLUEPRINT.md) | QUALITY_SCORING_SYSTEM_001 | å¼ºä¾èµ?| æ¥æ¶è´¨éæ£æµç»æè¯å?|
| [è´¨éæ¥åèªå¨åèå¾](./QUALITY_REPORT_AUTOMATION_BLUEPRINT.md) | QUALITY_REPORT_AUTOMATION_001 | ä¸­ä¾èµ?| æ¥æ¶è´¨éæ°æ®çææ¥å |
| [æ°æ®å¯è§æµæ§èå¾](./DATA_OBSERVABILITY_BLUEPRINT.md) | DATA_OBSERVABILITY_001 | ä¸­ä¾èµ?| æä¾è´¨éçæ§ææ  |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **Great Expectations** | 0.18+ | 数据质量验证 | [官方文档](https://docs.greatexpectations.io/) |
| **Apache Griffin** | 0.5+ | 数据质量度量 | [官方文档](https://griffin.apache.org/) |
| **Deequ** | 2.0+ | 数据质量测试 | [官方文档](https://github.com/awslabs/deequ) |
| **Prometheus** | 2.40+ | 监控指标采集 | [官方文档](https://prometheus.io/) |
| **Grafana** | 9.0+ | å¯è§åå±ç¤?| [å®æ¹ææ¡£](https://grafana.com/) |

### å¼ç¨å
³ç³»å?

```mermaid
graph LR
    A[数据源管理] --> B[数据质量监控]
    C[æ°æ®å®å
¨åè§] --> B
    D[高性能数据管道] --> B
    
    B --> E[自动修复引擎]
    B --> F[质量评分系统]
    B --> G[质量报告自动化]
    B --> H[数据可观测性]
    
    style B fill:#ff6b6b
    style A fill:#4ecdc4
    style C fill:#45b7d1
    style D fill:#96ceb4
```

---

## ðï¸?æ¶æè®¾è®¡

### 整体架构

```mermaid
graph TB
    subgraph "æ°æ®æº?
        A1[宏观经济数据]
        A2[æ¥é¢è¡æ
数据]
        A3[æ¥å
è¡æ
数据]
        A4[å®æ¶è¡æ
数据]
    end
    
    subgraph "数据质量监控系统"
        subgraph "质量规则引擎"
            B1[规则定义器]
            B2[规则解析器]
            B3[规则执行器]
            B4[规则库]
        end
        
        subgraph "质量检测器"
            C1[完整性检测]
            C2[准确性检测]
            C3[一致性检测]
            C4[时效性检测]
            C5[唯一性检测]
        end
        
        subgraph "异常检测器"
            D1[统计异常检测]
            D2[机器学习异常检测]
            D3[业务规则异常检测]
            D4[异常模式识别]
        end
        
        subgraph "è´¨éæ¥åçæå?
            E1[质量评分计算]
            E2[趋势分析]
            E3[报告生成]
            E4[可视化展示]
        end
        
        subgraph "告警系统"
            F1[告警规则引擎]
            F2[告警通道管理]
            F3[告警历史记录]
        end
    end
    
    subgraph "输出"
        G1[质量报告]
        G2[异常报告]
        G3[告警通知]
        G4[质量仪表板]
    end
    
    A1 --> C1
    A2 --> C1
    A3 --> C1
    A4 --> C1
    
    B1 --> B4
    B4 --> B2
    B2 --> B3
    B3 --> C1
    
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5
    
    C5 --> D1
    D1 --> D2
    D2 --> D3
    D3 --> D4
    
    D4 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> E4
    
    E4 --> F1
    F1 --> F2
    F2 --> F3
    
    F2 --> G3
    E3 --> G1
    D4 --> G2
    E4 --> G4
```

### æ°æ®æµè®¾è®?

#### å®æ¶æ°æ®è´¨éçæ§æµ?

```
å®æ¶è¡æ
æ°æ® â?è´¨éæ£æµå¨ï¼æ¶ææ?åç¡®æ§ï¼ â?å¼å¸¸æ£æµå¨ â?åè­¦ç³»ç» â?åè­¦éç¥
```

**特点**:
- ç§çº§æ£æµ?
- ä½å»¶è¿è¦æ±?
- 自动告警

#### 批量数据质量检查流

```
åå²æ°æ® â?è´¨éæ£æµå¨ï¼å®æ´æ?ä¸è´æ?å¯ä¸æ§ï¼ â?å¼å¸¸æ£æµå¨ â?è´¨éæ¥åçæå?â?è´¨éæ¥å
```

**特点**:
- 定时执行
- å
¨é¢æ£æ?
- 报告生成

---

## ð§ å
³é®ç»ä»¶è®¾è®¡

### 1. 质量规则引擎 (Quality Rule Engine)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

class QualityRule(ABC):
    """质量规则基类"""
    
    def __init__(self, rule_id: str, rule_name: str, severity: str):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.severity = severity  # critical, high, medium, low
        
    @abstractmethod
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """执行质量规则验证"""
        pass
    
    @abstractmethod
    def get_rule_definition(self) -> Dict[str, Any]:
        """获取规则定义"""
        pass


class CompletenessRule(QualityRule):
    """å®æ´æ§è§å?""
    
    def __init__(self, rule_id: str, columns: List[str], threshold: float = 0.95):
        super().__init__(rule_id, "å®æ´æ§æ£æ?, "critical")
        self.columns = columns
        self.threshold = threshold
        
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """æ£æ¥æ°æ®å®æ´æ?""
        results = {}
        
        for column in self.columns:
            if column not in data.columns:
                results[column] = {
                    'status': 'fail',
                    'message': f'Column {column} not found',
                    'completeness': 0.0
                }
                continue
            
            non_null_count = data[column].notna().sum()
            total_count = len(data)
            completeness = non_null_count / total_count if total_count > 0 else 0.0
            
            status = 'pass' if completeness >= self.threshold else 'fail'
            
            results[column] = {
                'status': status,
                'message': f'Completeness: {completeness:.2%}',
                'completeness': completeness,
                'non_null_count': non_null_count,
                'total_count': total_count
            }
        
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'severity': self.severity,
            'results': results,
            'overall_status': 'pass' if all(r['status'] == 'pass' for r in results.values()) else 'fail'
        }
    
    def get_rule_definition(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'rule_type': 'completeness',
            'columns': self.columns,
            'threshold': self.threshold,
            'severity': self.severity
        }


class AccuracyRule(QualityRule):
    """åç¡®æ§è§å?""
    
    def __init__(self, rule_id: str, column: str, value_range: tuple):
        super().__init__(rule_id, "åç¡®æ§æ£æ?, "high")
        self.column = column
        self.value_range = value_range
        
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """æ£æ¥æ°æ®åç¡®æ?""
        if self.column not in data.columns:
            return {
                'rule_id': self.rule_id,
                'rule_name': self.rule_name,
                'severity': self.severity,
                'overall_status': 'fail',
                'message': f'Column {self.column} not found'
            }
        
        min_val, max_val = self.value_range
        valid_count = ((data[self.column] >= min_val) & (data[self.column] <= max_val)).sum()
        total_count = len(data)
        accuracy = valid_count / total_count if total_count > 0 else 0.0
        
        status = 'pass' if accuracy >= 0.99 else 'fail'
        
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'severity': self.severity,
            'overall_status': status,
            'results': {
                'accuracy': accuracy,
                'valid_count': valid_count,
                'total_count': total_count,
                'value_range': self.value_range
            }
        }
    
    def get_rule_definition(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'rule_type': 'accuracy',
            'column': self.column,
            'value_range': self.value_range,
            'severity': self.severity
        }


class ConsistencyRule(QualityRule):
    """ä¸è´æ§è§å?""
    
    def __init__(self, rule_id: str, columns: List[str], consistency_type: str):
        super().__init__(rule_id, "ä¸è´æ§æ£æ?, "high")
        self.columns = columns
        self.consistency_type = consistency_type  # cross_field, temporal, cross_source
        
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """æ£æ¥æ°æ®ä¸è´æ?""
        if self.consistency_type == 'cross_field':
            return self._check_cross_field_consistency(data)
        elif self.consistency_type == 'temporal':
            return self._check_temporal_consistency(data)
        else:
            return {
                'rule_id': self.rule_id,
                'overall_status': 'fail',
                'message': f'Unknown consistency type: {self.consistency_type}'
            }
    
    def _check_cross_field_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """æ£æ¥è·¨å­æ®µä¸è´æ?""
        # 例如：high >= low, high >= open, high >= close
        if 'high' in data.columns and 'low' in data.columns:
            inconsistent_count = (data['high'] < data['low']).sum()
            total_count = len(data)
            consistency = 1 - (inconsistent_count / total_count) if total_count > 0 else 1.0
            
            return {
                'rule_id': self.rule_id,
                'rule_name': self.rule_name,
                'severity': self.severity,
                'overall_status': 'pass' if consistency >= 0.99 else 'fail',
                'results': {
                    'consistency': consistency,
                    'inconsistent_count': inconsistent_count,
                    'total_count': total_count
                }
            }
        
        return {
            'rule_id': self.rule_id,
            'overall_status': 'fail',
            'message': 'Required columns not found'
        }
    
    def _check_temporal_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """æ£æ¥æ¶é´ä¸è´æ?""
        # 例如：时间戳单调递增
        if 'timestamp' in data.columns:
            is_sorted = data['timestamp'].is_monotonic_increasing
            return {
                'rule_id': self.rule_id,
                'rule_name': self.rule_name,
                'severity': self.severity,
                'overall_status': 'pass' if is_sorted else 'fail',
                'results': {
                    'is_sorted': is_sorted
                }
            }
        
        return {
            'rule_id': self.rule_id,
            'overall_status': 'fail',
            'message': 'Timestamp column not found'
        }
    
    def get_rule_definition(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'rule_type': 'consistency',
            'columns': self.columns,
            'consistency_type': self.consistency_type,
            'severity': self.severity
        }


class TimelinessRule(QualityRule):
    """æ¶ææ§è§å?""
    
    def __init__(self, rule_id: str, timestamp_column: str, max_delay_seconds: int):
        super().__init__(rule_id, "æ¶ææ§æ£æ?, "critical")
        self.timestamp_column = timestamp_column
        self.max_delay_seconds = max_delay_seconds
        
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """æ£æ¥æ°æ®æ¶ææ?""
        if self.timestamp_column not in data.columns:
            return {
                'rule_id': self.rule_id,
                'overall_status': 'fail',
                'message': f'Column {self.timestamp_column} not found'
            }
        
        latest_timestamp = data[self.timestamp_column].max()
        current_time = datetime.now()
        delay_seconds = (current_time - latest_timestamp).total_seconds()
        
        status = 'pass' if delay_seconds <= self.max_delay_seconds else 'fail'
        
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'severity': self.severity,
            'overall_status': status,
            'results': {
                'latest_timestamp': latest_timestamp.isoformat(),
                'current_time': current_time.isoformat(),
                'delay_seconds': delay_seconds,
                'max_delay_seconds': self.max_delay_seconds
            }
        }
    
    def get_rule_definition(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'rule_type': 'timeliness',
            'timestamp_column': self.timestamp_column,
            'max_delay_seconds': self.max_delay_seconds,
            'severity': self.severity
        }


class UniquenessRule(QualityRule):
    """å¯ä¸æ§è§å?""
    
    def __init__(self, rule_id: str, columns: List[str]):
        super().__init__(rule_id, "å¯ä¸æ§æ£æ?, "medium")
        self.columns = columns
        
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """æ£æ¥æ°æ®å¯ä¸æ?""
        missing_columns = [col for col in self.columns if col not in data.columns]
        if missing_columns:
            return {
                'rule_id': self.rule_id,
                'overall_status': 'fail',
                'message': f'Columns not found: {missing_columns}'
            }
        
        total_count = len(data)
        unique_count = data[self.columns].drop_duplicates().shape[0]
        uniqueness = unique_count / total_count if total_count > 0 else 1.0
        
        status = 'pass' if uniqueness >= 0.99 else 'fail'
        
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'severity': self.severity,
            'overall_status': status,
            'results': {
                'uniqueness': uniqueness,
                'unique_count': unique_count,
                'total_count': total_count,
                'duplicate_count': total_count - unique_count
            }
        }
    
    def get_rule_definition(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'rule_type': 'uniqueness',
            'columns': self.columns,
            'severity': self.severity
        }


class QualityRuleEngine:
    """质量规则引擎"""
    
    def __init__(self):
        self.rules: Dict[str, QualityRule] = {}
        
    def register_rule(self, rule: QualityRule) -> None:
        """注册质量规则"""
        self.rules[rule.rule_id] = rule
        
    def unregister_rule(self, rule_id: str) -> None:
        """注销质量规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            
    def execute_rule(self, rule_id: str, data: pd.DataFrame) -> Dict[str, Any]:
        """执行单个规则"""
        if rule_id not in self.rules:
            return {
                'rule_id': rule_id,
                'status': 'error',
                'message': f'Rule {rule_id} not found'
            }
        
        return self.rules[rule_id].validate(data)
    
    def execute_all_rules(self, data: pd.DataFrame) -> Dict[str, Any]:
        """æ§è¡ææè§å?""
        results = []
        
        for rule_id, rule in self.rules.items():
            result = rule.validate(data)
            results.append(result)
        
        overall_status = 'pass' if all(r['overall_status'] == 'pass' for r in results) else 'fail'
        
        return {
            'execution_time': datetime.now().isoformat(),
            'total_rules': len(results),
            'passed_rules': sum(1 for r in results if r['overall_status'] == 'pass'),
            'failed_rules': sum(1 for r in results if r['overall_status'] == 'fail'),
            'overall_status': overall_status,
            'results': results
        }
    
    def get_rule_library(self) -> List[Dict[str, Any]]:
        """è·åè§ååº?""
        return [rule.get_rule_definition() for rule in self.rules.values()]
```

### 2. 异常检测器 (Anomaly Detector)

```python
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self):
        self.statistical_detector = StatisticalAnomalyDetector()
        self.ml_detector = MLAnomalyDetector()
        self.business_detector = BusinessRuleAnomalyDetector()
        
    def detect_anomalies(self, 
                        data: pd.DataFrame,
                        detection_methods: List[str] = ['statistical', 'ml', 'business']) -> Dict[str, Any]:
        """æ£æµæ°æ®å¼å¸?""
        results = {}
        
        if 'statistical' in detection_methods:
            results['statistical'] = self.statistical_detector.detect(data)
        
        if 'ml' in detection_methods:
            results['ml'] = self.ml_detector.detect(data)
        
        if 'business' in detection_methods:
            results['business'] = self.business_detector.detect(data)
        
        # 合并异常结果
        all_anomalies = self._merge_anomalies(results)
        
        return {
            'detection_time': datetime.now().isoformat(),
            'anomaly_count': len(all_anomalies),
            'anomalies': all_anomalies,
            'details': results
        }
    
    def _merge_anomalies(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """合并异常结果"""
        anomalies = []
        
        for method, result in results.items():
            if 'anomalies' in result:
                for anomaly in result['anomalies']:
                    anomaly['detection_method'] = method
                    anomalies.append(anomaly)
        
        return anomalies


class StatisticalAnomalyDetector:
    """统计异常检测器"""
    
    def detect(self, data: pd.DataFrame) -> Dict[str, Any]:
        """ä½¿ç¨ç»è®¡æ¹æ³æ£æµå¼å¸?""
        anomalies = []
        
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            # Z-Score方法
            z_scores = np.abs(stats.zscore(data[column].dropna()))
            outlier_indices = np.where(z_scores > 3)[0]
            
            if len(outlier_indices) > 0:
                anomalies.append({
                    'type': 'statistical_outlier',
                    'column': column,
                    'method': 'z_score',
                    'anomaly_count': len(outlier_indices),
                    'anomaly_indices': outlier_indices.tolist(),
                    'severity': 'medium'
                })
            
            # IQR方法
            Q1 = data[column].quantile(0.25)
            Q3 = data[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (data[column] < lower_bound) | (data[column] > upper_bound)
            outlier_count = outlier_mask.sum()
            
            if outlier_count > 0:
                anomalies.append({
                    'type': 'statistical_outlier',
                    'column': column,
                    'method': 'iqr',
                    'anomaly_count': outlier_count,
                    'bounds': {'lower': lower_bound, 'upper': upper_bound},
                    'severity': 'medium'
                })
        
        return {
            'method': 'statistical',
            'anomaly_count': len(anomalies),
            'anomalies': anomalies
        }


class MLAnomalyDetector:
    """机器学习异常检测器"""
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
    def detect(self, data: pd.DataFrame) -> Dict[str, Any]:
        """ä½¿ç¨æºå¨å­¦ä¹ æ¹æ³æ£æµå¼å¸?""
        anomalies = []
        
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            return {
                'method': 'ml',
                'anomaly_count': 0,
                'anomalies': []
            }
        
        # 准备数据
        X = data[numeric_columns].dropna()
        
        if len(X) == 0:
            return {
                'method': 'ml',
                'anomaly_count': 0,
                'anomalies': []
            }
        
        # æ åå?
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练模型
        self.model.fit(X_scaled)
        
        # 预测
        predictions = self.model.predict(X_scaled)
        anomaly_indices = np.where(predictions == -1)[0]
        
        if len(anomaly_indices) > 0:
            anomalies.append({
                'type': 'ml_anomaly',
                'method': 'isolation_forest',
                'anomaly_count': len(anomaly_indices),
                'anomaly_indices': anomaly_indices.tolist(),
                'severity': 'high'
            })
        
        return {
            'method': 'ml',
            'anomaly_count': len(anomalies),
            'anomalies': anomalies
        }


class BusinessRuleAnomalyDetector:
    """业务规则异常检测器"""
    
    def detect(self, data: pd.DataFrame) -> Dict[str, Any]:
        """ä½¿ç¨ä¸å¡è§åæ£æµå¼å¸?""
        anomalies = []
        
        # æ£æ¥ä»·æ ¼å¼å¸?
        if all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            # 检查涨跌停
            price_change = (data['close'] - data['open']) / data['open']
            limit_up = price_change >= 0.095  # 涨停
            limit_down = price_change <= -0.095  # 跌停
            
            if limit_up.any():
                anomalies.append({
                    'type': 'business_rule_violation',
                    'rule': 'limit_up',
                    'anomaly_count': limit_up.sum(),
                    'severity': 'low',
                    'message': 'Detected limit-up stocks'
                })
            
            if limit_down.any():
                anomalies.append({
                    'type': 'business_rule_violation',
                    'rule': 'limit_down',
                    'anomaly_count': limit_down.sum(),
                    'severity': 'low',
                    'message': 'Detected limit-down stocks'
                })
            
            # 检查价格逻辑
            price_logic_violation = (
                (data['high'] < data['low']) |
                (data['high'] < data['open']) |
                (data['high'] < data['close']) |
                (data['low'] > data['open']) |
                (data['low'] > data['close'])
            )
            
            if price_logic_violation.any():
                anomalies.append({
                    'type': 'business_rule_violation',
                    'rule': 'price_logic',
                    'anomaly_count': price_logic_violation.sum(),
                    'severity': 'critical',
                    'message': 'Price logic violation detected'
                })
        
        # 检查成交量异常
        if 'volume' in data.columns:
            volume_mean = data['volume'].mean()
            volume_std = data['volume'].std()
            volume_anomaly = data['volume'] > volume_mean + 3 * volume_std
            
            if volume_anomaly.any():
                anomalies.append({
                    'type': 'business_rule_violation',
                    'rule': 'volume_anomaly',
                    'anomaly_count': volume_anomaly.sum(),
                    'severity': 'medium',
                    'message': 'Abnormal volume detected'
                })
        
        return {
            'method': 'business',
            'anomaly_count': len(anomalies),
            'anomalies': anomalies
        }
```

### 3. è´¨éæ¥åçæå?(Quality Report Generator)

```python
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class QualityReportGenerator:
    """è´¨éæ¥åçæå?""
    
    def __init__(self):
        self.quality_scorer = QualityScorer()
        self.trend_analyzer = TrendAnalyzer()
        
    def generate_report(self,
                       quality_results: Dict[str, Any],
                       anomaly_results: Dict[str, Any],
                       report_type: str = 'daily') -> Dict[str, Any]:
        """生成质量报告"""
        # 计算质量评分
        quality_score = self.quality_scorer.calculate_score(quality_results)
        
        # 趋势分析
        trend_analysis = self.trend_analyzer.analyze(quality_score)
        
        # 生成报告
        report = {
            'report_id': f"QR_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'report_type': report_type,
            'report_time': datetime.now().isoformat(),
            'summary': {
                'overall_quality_score': quality_score['overall_score'],
                'quality_grade': quality_score['grade'],
                'total_rules': quality_results['total_rules'],
                'passed_rules': quality_results['passed_rules'],
                'failed_rules': quality_results['failed_rules'],
                'anomaly_count': anomaly_results['anomaly_count']
            },
            'quality_score': quality_score,
            'quality_results': quality_results,
            'anomaly_results': anomaly_results,
            'trend_analysis': trend_analysis,
            'recommendations': self._generate_recommendations(quality_results, anomaly_results)
        }
        
        return report
    
    def _generate_recommendations(self,
                                  quality_results: Dict[str, Any],
                                  anomaly_results: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于质量结果生成建议
        if quality_results['failed_rules'] > 0:
            recommendations.append("å»ºè®®æ£æ¥å¤±è´¥çè´¨éè§åï¼ä¿®å¤æ°æ®è´¨éé®é¢?)
        
        # 基于异常结果生成建议
        if anomaly_results['anomaly_count'] > 10:
            recommendations.append("æ£æµå°å¤§éæ°æ®å¼å¸¸ï¼å»ºè®®è¿è¡æ°æ®æ¸
æ´?)
        
        critical_anomalies = [a for a in anomaly_results.get('anomalies', []) 
                             if a.get('severity') == 'critical']
        if critical_anomalies:
            recommendations.append("æ£æµå°ä¸¥éå¼å¸¸ï¼å»ºè®®ç«å³å¤ç?)
        
        return recommendations


class QualityScorer:
    """è´¨éè¯åå?""
    
    def calculate_score(self, quality_results: Dict[str, Any]) -> Dict[str, Any]:
        """计算质量评分"""
        # 基础分数
        total_rules = quality_results['total_rules']
        passed_rules = quality_results['passed_rules']
        
        if total_rules == 0:
            base_score = 100
        else:
            base_score = (passed_rules / total_rules) * 100
        
        # æ ¹æ®è§åä¸¥éæ§è°æ´åæ?
        severity_penalty = 0
        for result in quality_results['results']:
            if result['overall_status'] == 'fail':
                severity = result.get('severity', 'medium')
                if severity == 'critical':
                    severity_penalty += 10
                elif severity == 'high':
                    severity_penalty += 5
                elif severity == 'medium':
                    severity_penalty += 2
                else:
                    severity_penalty += 1
        
        # æç»åæ?
        final_score = max(0, base_score - severity_penalty)
        
        # 评级
        if final_score >= 90:
            grade = 'A'
        elif final_score >= 80:
            grade = 'B'
        elif final_score >= 70:
            grade = 'C'
        elif final_score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'overall_score': final_score,
            'base_score': base_score,
            'severity_penalty': severity_penalty,
            'grade': grade
        }


class TrendAnalyzer:
    """è¶å¿åæå?""
    
    def __init__(self, history_window: int = 30):
        self.history_window = history_window
        self.score_history: List[float] = []
        
    def analyze(self, quality_score: Dict[str, Any]) -> Dict[str, Any]:
        """分析质量趋势"""
        current_score = quality_score['overall_score']
        
        # æ·»å å°åå²è®°å½?
        self.score_history.append(current_score)
        
        # 保持窗口大小
        if len(self.score_history) > self.history_window:
            self.score_history = self.score_history[-self.history_window:]
        
        # 计算趋势
        if len(self.score_history) < 2:
            trend = 'stable'
            trend_score = 0
        else:
            recent_avg = np.mean(self.score_history[-7:]) if len(self.score_history) >= 7 else np.mean(self.score_history)
            previous_avg = np.mean(self.score_history[:-7]) if len(self.score_history) > 7 else self.score_history[0]
            
            trend_score = recent_avg - previous_avg
            
            if trend_score > 5:
                trend = 'improving'
            elif trend_score < -5:
                trend = 'declining'
            else:
                trend = 'stable'
        
        return {
            'trend': trend,
            'trend_score': trend_score,
            'current_score': current_score,
            'average_score': np.mean(self.score_history) if self.score_history else current_score,
            'min_score': min(self.score_history) if self.score_history else current_score,
            'max_score': max(self.score_history) if self.score_history else current_score,
            'history_length': len(self.score_history)
        }
```

### 4. 告警系统 (Alert System)

```python
from typing import Dict, Any, List, Callable
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertSystem:
    """告警系统"""
    
    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alert_channels: Dict[str, AlertChannel] = {}
        self.alert_history: List[Dict[str, Any]] = []
        
    def register_alert_rule(self, alert_rule: 'AlertRule') -> None:
        """注册告警规则"""
        self.alert_rules[alert_rule.rule_id] = alert_rule
        
    def register_alert_channel(self, channel_name: str, channel: 'AlertChannel') -> None:
        """注册告警通道"""
        self.alert_channels[channel_name] = channel
        
    def check_and_alert(self, 
                       quality_results: Dict[str, Any],
                       anomaly_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """æ£æ¥å¹¶åéåè­?""
        alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if rule.should_alert(quality_results, anomaly_results):
                alert = rule.create_alert(quality_results, anomaly_results)
                alerts.append(alert)
                
                # åéåè­?
                for channel_name in rule.channels:
                    if channel_name in self.alert_channels:
                        self.alert_channels[channel_name].send(alert)
                
                # 记录历史
                self.alert_history.append(alert)
        
        return alerts


class AlertRule:
    """告警规则"""
    
    def __init__(self,
                 rule_id: str,
                 rule_name: str,
                 condition: Callable,
                 channels: List[str],
                 severity: str = 'high'):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.condition = condition
        self.channels = channels
        self.severity = severity
        
    def should_alert(self,
                     quality_results: Dict[str, Any],
                     anomaly_results: Dict[str, Any]) -> bool:
        """å¤æ­æ¯å¦éè¦åè­?""
        return self.condition(quality_results, anomaly_results)
    
    def create_alert(self,
                    quality_results: Dict[str, Any],
                    anomaly_results: Dict[str, Any]) -> Dict[str, Any]:
        """创建告警"""
        return {
            'alert_id': f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'severity': self.severity,
            'alert_time': datetime.now().isoformat(),
            'message': self._generate_message(quality_results, anomaly_results),
            'quality_summary': {
                'total_rules': quality_results['total_rules'],
                'failed_rules': quality_results['failed_rules']
            },
            'anomaly_summary': {
                'anomaly_count': anomaly_results['anomaly_count']
            }
        }
    
    def _generate_message(self,
                         quality_results: Dict[str, Any],
                         anomaly_results: Dict[str, Any]) -> str:
        """生成告警消息"""
        message = f"数据质量告警: {self.rule_name}\n"
        message += f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"å¤±è´¥è§åæ? {quality_results['failed_rules']}\n"
        message += f"异常数量: {anomaly_results['anomaly_count']}\n"
        return message


class AlertChannel(ABC):
    """告警通道基类"""
    
    @abstractmethod
    def send(self, alert: Dict[str, Any]) -> bool:
        """åéåè­?""
        pass


class EmailAlertChannel(AlertChannel):
    """邮件告警通道"""
    
    def __init__(self,
                 smtp_server: str,
                 smtp_port: int,
                 sender_email: str,
                 sender_password: str,
                 recipients: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipients = recipients
        
    def send(self, alert: Dict[str, Any]) -> bool:
        """åéé®ä»¶åè­?""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = f"[{alert['severity'].upper()}] {alert['rule_name']}"
            
            body = alert['message']
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False


class SlackAlertChannel(AlertChannel):
    """Slack告警通道"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def send(self, alert: Dict[str, Any]) -> bool:
        """发送Slack告警"""
        try:
            import requests
            
            payload = {
                'text': alert['message'],
                'attachments': [
                    {
                        'color': 'danger' if alert['severity'] == 'critical' else 'warning',
                        'fields': [
                            {
                                'title': 'Severity',
                                'value': alert['severity'],
                                'short': True
                            },
                            {
                                'title': 'Time',
                                'value': alert['alert_time'],
                                'short': True
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
            return False


class WebhookAlertChannel(AlertChannel):
    """Webhook告警通道"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def send(self, alert: Dict[str, Any]) -> bool:
        """发送Webhook告警"""
        try:
            import requests
            
            response = requests.post(self.webhook_url, json=alert)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send webhook alert: {e}")
            return False
```

---

## 📊 数据模型设计

### è´¨éè§åè¡?

```sql
CREATE TABLE quality_rules (
    rule_id VARCHAR(50) PRIMARY KEY COMMENT '规则ID',
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    rule_type VARCHAR(50) NOT NULL COMMENT '规则类型',
    rule_definition TEXT NOT NULL COMMENT 'è§åå®ä¹ï¼JSONï¼?,
    severity VARCHAR(20) NOT NULL COMMENT 'ä¸¥éæ§ï¼critical/high/medium/lowï¼?,
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_rule_type (rule_type),
    INDEX idx_severity (severity)
) COMMENT 'è´¨éè§åè¡?;
```

### 质量检查结果表

```sql
CREATE TABLE quality_check_results (
    check_id VARCHAR(100) PRIMARY KEY COMMENT '检查ID',
    rule_id VARCHAR(50) NOT NULL COMMENT '规则ID',
    data_source VARCHAR(100) NOT NULL COMMENT 'æ°æ®æº?,
    check_time TIMESTAMP NOT NULL COMMENT 'æ£æ¥æ¶é?,
    status VARCHAR(20) NOT NULL COMMENT 'ç¶æï¼pass/failï¼?,
    result_details TEXT COMMENT 'ç»æè¯¦æ
ï¼JSONï¼?,
    error_message TEXT COMMENT '错误信息',
    INDEX idx_rule_id (rule_id),
    INDEX idx_check_time (check_time),
    INDEX idx_status (status)
) COMMENT '质量检查结果表';
```

### å¼å¸¸è®°å½è¡?

```sql
CREATE TABLE anomaly_records (
    anomaly_id VARCHAR(100) PRIMARY KEY COMMENT '异常ID',
    data_source VARCHAR(100) NOT NULL COMMENT 'æ°æ®æº?,
    anomaly_type VARCHAR(50) NOT NULL COMMENT '异常类型',
    detection_method VARCHAR(50) NOT NULL COMMENT 'æ£æµæ¹æ³?,
    detection_time TIMESTAMP NOT NULL COMMENT 'æ£æµæ¶é?,
    severity VARCHAR(20) NOT NULL COMMENT 'ä¸¥éæ?,
    anomaly_details TEXT COMMENT 'å¼å¸¸è¯¦æ
ï¼JSONï¼?,
    status VARCHAR(20) DEFAULT 'open' COMMENT 'ç¶æï¼open/resolved/ignoredï¼?,
    resolved_time TIMESTAMP COMMENT '解决时间',
    resolved_by VARCHAR(50) COMMENT 'è§£å³äº?,
    INDEX idx_data_source (data_source),
    INDEX idx_anomaly_type (anomaly_type),
    INDEX idx_detection_time (detection_time),
    INDEX idx_status (status)
) COMMENT 'å¼å¸¸è®°å½è¡?;
```

### è´¨éæ¥åè¡?

```sql
CREATE TABLE quality_reports (
    report_id VARCHAR(100) PRIMARY KEY COMMENT '报告ID',
    report_type VARCHAR(20) NOT NULL COMMENT 'æ¥åç±»åï¼daily/weekly/monthlyï¼?,
    report_time TIMESTAMP NOT NULL COMMENT '报告时间',
    overall_score DECIMAL(5, 2) COMMENT '总体评分',
    quality_grade VARCHAR(1) COMMENT '质量等级',
    summary TEXT COMMENT 'æè¦ï¼JSONï¼?,
    report_details TEXT COMMENT 'æ¥åè¯¦æ
ï¼JSONï¼?,
    recommendations TEXT COMMENT 'å»ºè®®ï¼JSONï¼?,
    INDEX idx_report_type (report_type),
    INDEX idx_report_time (report_time)
) COMMENT 'è´¨éæ¥åè¡?;
```

---

## 🔌 接口规范

### RESTful API接口

#### 1. æ§è¡è´¨éæ£æ?

```
POST /api/v1/quality/check
Content-Type: application/json

Request:
{
    "data_source": "daily_market_data",
    "rules": ["completeness_check", "accuracy_check"],
    "data_range": {
        "start_date": "2024-12-01",
        "end_date": "2024-12-31"
    }
}

Response:
{
    "status": "success",
    "check_id": "QC_20241206100000",
    "check_time": "2024-12-06T10:00:00Z",
    "results": {
        "total_rules": 2,
        "passed_rules": 2,
        "failed_rules": 0,
        "overall_status": "pass"
    }
}
```

#### 2. æ£æµå¼å¸?

```
POST /api/v1/quality/anomaly/detect
Content-Type: application/json

Request:
{
    "data_source": "realtime_quotes",
    "detection_methods": ["statistical", "ml", "business"],
    "time_window": "5m"
}

Response:
{
    "status": "success",
    "detection_time": "2024-12-06T10:00:00Z",
    "anomaly_count": 3,
    "anomalies": [
        {
            "type": "statistical_outlier",
            "column": "volume",
            "severity": "medium"
        }
    ]
}
```

#### 3. 生成质量报告

```
POST /api/v1/quality/report/generate
Content-Type: application/json

Request:
{
    "report_type": "daily",
    "data_sources": ["daily_market_data", "intraday_data"],
    "report_date": "2024-12-06"
}

Response:
{
    "status": "success",
    "report_id": "QR_20241206100000",
    "report_time": "2024-12-06T10:00:00Z",
    "summary": {
        "overall_quality_score": 95.5,
        "quality_grade": "A",
        "total_rules": 10,
        "passed_rules": 9,
        "failed_rules": 1
    }
}
```

#### 4. 查询质量报告

```
GET /api/v1/quality/report/{report_id}

Response:
{
    "status": "success",
    "report": {
        "report_id": "QR_20241206100000",
        "report_type": "daily",
        "overall_score": 95.5,
        "quality_grade": "A",
        "summary": {...},
        "recommendations": [...]
    }
}
```

---

## 🚀 实施要点

### é¶æ®µ1ï¼è´¨éè§åå¼æå¼åï¼ç¬?å¨ï¼

**任务**:
1. â?å®ç°è´¨éè§ååºç±»ååç±»è§å?
2. â?å®ç°è´¨éè§åå¼æ
3. â?å®ç°è§åæ³¨ååç®¡ç?
4. â?ç¼ååå
æµè¯

**验收标准**:
- ææè§åç±»åå¯ä»¥æ­£å¸¸æ§è¡?
- è§åå¼æå¯ä»¥æ³¨ååç®¡çè§å?
- åå
æµè¯è¦ççâ¥80%

---

### é¶æ®µ2ï¼å¼å¸¸æ£æµå¨å¼åï¼ç¬?-2å¨ï¼

**任务**:
1. â?å®ç°ç»è®¡å¼å¸¸æ£æµå¨
2. â?å®ç°æºå¨å­¦ä¹ å¼å¸¸æ£æµå¨
3. â?å®ç°ä¸å¡è§åå¼å¸¸æ£æµå¨
4. â?ç¼ååå
æµè¯

**验收标准**:
- æææ£æµæ¹æ³å¯ä»¥æ­£å¸¸å·¥ä½?
- å¼å¸¸æ£æµç»æåç¡?
- åå
æµè¯è¦ççâ¥80%

---

### é¶æ®µ3ï¼è´¨éæ¥åçæå¨å¼åï¼ç¬?å¨ï¼

**任务**:
1. â?å®ç°è´¨éè¯åå?
2. â?å®ç°è¶å¿åæå?
3. â?å®ç°æ¥åçæå?
4. â?ç¼ååå
æµè¯

**验收标准**:
- 质量评分计算正确
- 趋势分析准确
- 报告生成完整
- åå
æµè¯è¦ççâ¥80%

---

### é¶æ®µ4ï¼åè­¦ç³»ç»å¼åï¼ç¬?å¨ï¼

**任务**:
1. â?å®ç°åè­¦è§åå¼æ
2. â?å®ç°å¤ç§åè­¦éé
3. â?å®ç°åè­¦åå²è®°å½
4. â?ç¼ååå
æµè¯

**验收标准**:
- 告警规则可以正常触发
- åè­¦å¯ä»¥æ­£å¸¸åé?
- 告警历史记录完整
- åå
æµè¯è¦ççâ¥80%

---

### 阶段5：集成测试与部署（第2周）

**任务**:
1. â?ç¼åéææµè¯ç¨ä¾
2. â?æ§è¡ç«¯å°ç«¯æµè¯?
3. â?é¨ç½²å°çäº§ç¯å¢?
4. â?ç¼åé¨ç½²ææ¡£

**验收标准**:
- éææµè¯å
¨é¨éè¿
- 系统可以正常运行
- 部署文档完整

---

## 🧪 测试策略

### åå
æµè¯

```python
import pytest
import pandas as pd
import numpy as np

def test_completeness_rule():
    """æµè¯å®æ´æ§è§å?""
    rule = CompletenessRule(
        rule_id='test_completeness',
        columns=['open', 'close'],
        threshold=0.95
    )
    
    # 创建测试数据
    data = pd.DataFrame({
        'open': [1.0, 2.0, np.nan, 4.0, 5.0],
        'close': [1.1, 2.1, 3.1, 4.1, 5.1]
    })
    
    # æ§è¡æ£æ?
    result = rule.validate(data)
    
    # 验证结果
    assert result['overall_status'] == 'pass'
    assert result['results']['open']['completeness'] == 0.8
    assert result['results']['close']['completeness'] == 1.0


def test_statistical_anomaly_detector():
    """测试统计异常检测器"""
    detector = StatisticalAnomalyDetector()
    
    # åå»ºæµè¯æ°æ®ï¼å
含异常值）
    data = pd.DataFrame({
        'value': [1, 2, 3, 4, 5, 100]  # 100æ¯å¼å¸¸å?
    })
    
    # æ£æµå¼å¸?
    result = detector.detect(data)
    
    # 验证结果
    assert result['anomaly_count'] > 0
    assert any(a['column'] == 'value' for a in result['anomalies'])


def test_quality_scorer():
    """æµè¯è´¨éè¯åå?""
    scorer = QualityScorer()
    
    # 创建测试结果
    quality_results = {
        'total_rules': 10,
        'passed_rules': 9,
        'failed_rules': 1,
        'results': [
            {'overall_status': 'pass', 'severity': 'medium'},
            {'overall_status': 'fail', 'severity': 'high'}
        ]
    }
    
    # 计算评分
    score = scorer.calculate_score(quality_results)
    
    # 验证结果
    assert score['overall_score'] >= 0
    assert score['overall_score'] <= 100
    assert score['grade'] in ['A', 'B', 'C', 'D', 'F']
```

---

## 📈 性能指标

### 检测性能要求

| æ£æµç±»å?| æ°æ®é?| ååºæ¶é´è¦æ± |
|---------|--------|------------|
| **å®æ¶è´¨éæ£æµ?* | 1ä¸æ¡ | <1ç§?|
| **æ¹éè´¨éæ£æ?* | 100ä¸æ¡ | <30ç§?|
| **å¼å¸¸æ£æµ?* | 10ä¸æ¡ | <5ç§?|
| **æ¥åçæ** | 1ä¸ªææ°æ® | <10ç§?|

### åç¡®æ§è¦æ±?

| ææ  | ç®æ å?|
|------|--------|
| **è§åæ§è¡åç¡®ç?* | 100% |
| **å¼å¸¸æ£æµå¬åç** | â?0% |
| **å¼å¸¸æ£æµç²¾ç¡®ç** | â?5% |
| **è´¨éè¯ååç¡®æ?* | â?5% |

---

## ð ç¸å
³ææ¡£

- [统一数据基础设施蓝图](./UNIFIED_DATA_INFRASTRUCTURE_BLUEPRINT.md)
- [数据治理平台蓝图](./DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md)
- ä¸ä¸å¤æ¶é´æ¡æ¶ç­ç¥æ¶æ?

---

## 📝 变更历史

| çæ¬ | æ¥æ | åæ´å
å®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**èå¾ç¶æ?*: â?è®¾è®¡å®æ
**ä¸ä¸æ­?*: å¼å§å®æ½é¶æ®? - è´¨éè§åå¼æå¼å?

## 变更历史

| çæ¬ | æ¥æ | åæ´å
å®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-02 | 初始版本创建 | 首席技术评审官 |
| v1.0.1 | 2026-04-06 | è¡¥å

YAMLå¤´é¨å­æ®µååæ´åå?| å®¡è®¡ç³»ç» |
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 6: ç»åä¼åå±?
##### 6.001. Data Quality Monitoring
- **模块ID**: DATA_QUALITY_MONITORING_001
- **蓝图文档**: DATA_QUALITY_MONITORING_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾
åå»?
- **èè´£**: å
¨ç³»ç»æ°æ®è´¨éä¿é?
- **ç¶æ?*: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Data Quality Monitoring** | å
¨ç³»ç»æ°æ®è´¨éä¿é?| **æ ¸å¿æ¨¡å** |

### 1.3 版本管理

| çæ¬ | æ¥æ | åæ´å
å®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active
