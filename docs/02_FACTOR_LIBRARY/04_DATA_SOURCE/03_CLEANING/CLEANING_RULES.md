---
module_id: DATA_CLEANING_RULES_001
version: 1.0.0
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构师
standard_type: 数据清洗规则
applicable_scope: 数据清洗规则配置
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 已完成
responsibility: 数据清洗规则库与异常数据处理
---
---

# 数据清洗规则配置

> **核心职责**: 数据清洗规则定义和质量控制标准，涉及数据清洗规则配置
> **职责边界**: 
> - ✅ 本文档负责：数据清洗规则定义和质量控制标准
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 数据清洗规则定义
- 定义标准化的数据清洗规则
- 提供YAML格式的规则配置
- 说明异常检测和处理策略

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 清洗蓝图 | [BLUEPRINT.md](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md) | 架构层 | 数据清洗引擎设计 |
| 清洗索引 | [INDEX.md](./INDEX.md) | 上级索引 | 数据清洗模块索引 |

**职责边界**:
- ✅ 本文档负责: 清洗规则配置和定义
- ❌ 本文档不负责: 清洗引擎实现（由 BLUEPRINT.md 负责）

> 清风量化系统 - 数据清洗规则配置指南
> **核心定位**: 提供标准化的数据清洗规则配置，确保数据质量一致性

---

## 1. 规则配置概述

### 1.1 规则配置原则

| 原则 | 说明 |
|------|------|
| **保守清洗** | 保留原始数据，只标记异常 |
| **可配置** | 所有规则通过YAML配置 |
| **可追溯** | 记录所有清洗操作历史 |
| **可回滚** | 支持清洗结果回滚 |

### 1.2 规则配置文件

```yaml
# config/cleaning_rules.yaml

# 全局配置
global:
  version: "1.0"
  created_date: "2026-04-04"
  owner: "数据质量团队"
  
  # 默认策略
  default_strategy: "conservative"  # conservative | aggressive
  
  # 异常处理
  on_error: "mark"  # mark | remove | fix
  
  # 日志级别
  log_level: "INFO"  # DEBUG | INFO | WARNING | ERROR
```

---

## 2. 数据类型规则

### 2.1 行情数据清洗规则

```yaml
# 行情数据清洗规则
market_data:
  # 日线数据
  daily:
    # 价格合理性检查
    - name: "price_range_check"
      type: "range"
      field: "close"
      min: 0.01
      max: 10000
      severity: "critical"
      action: "mark"
      
    # 涨跌幅检查
    - name: "pct_change_check"
      type: "pct_change"
      field: "pct_chg"
      max_abs: 20  # A股涨跌停限制
      severity: "warning"
      action: "mark"
      
    # 成交量检查
    - name: "volume_check"
      type: "positive"
      field: "volume"
      allow_zero: true
      severity: "warning"
      action: "mark"
      
    # 数据完整性检查
    - name: "completeness_check"
      type: "completeness"
      required_fields: ["open", "high", "low", "close", "volume"]
      severity: "critical"
      action: "mark"
      
  # 分钟线数据
  minute:
    # 时间连续性检查
    - name: "time_continuity_check"
      type: "time_continuity"
      frequency: "1min"
      tolerance: 5  # 允许5分钟缺失
      severity: "warning"
      action: "mark"
      
    # 价格跳跃检查
    - name: "price_jump_check"
      type: "price_jump"
      threshold: 0.05  # 5%跳跃阈值
      severity: "warning"
      action: "mark"
```

### 2.2 财务数据清洗规则

```yaml
# 财务数据清洗规则
financial_data:
  # 资产负债表
  balance_sheet:
    # 资产负债平衡检查
    - name: "balance_check"
      type: "equation"
      formula: "total_assets == total_liabilities + equity"
      tolerance: 0.01  # 1%容差
      severity: "critical"
      action: "mark"
      
    # 负值检查
    - name: "negative_check"
      type: "negative"
      fields: ["total_assets", "total_liabilities"]
      allow_negative: false
      severity: "critical"
      action: "mark"
      
  # 利润表
  income_statement:
    # 利润计算检查
    - name: "profit_check"
      type: "equation"
      formula: "net_profit == operating_profit + non_operating_profit"
      tolerance: 0.05
      severity: "warning"
      action: "mark"
      
  # 现金流量表
  cash_flow:
    # 现金流平衡检查
    - name: "cash_flow_check"
      type: "equation"
      formula: "cash_change == operating_cf + investing_cf + financing_cf"
      tolerance: 0.05
      severity: "warning"
      action: "mark"
```

### 2.3 因子数据清洗规则

```yaml
# 因子数据清洗规则
factor_data:
  # 因子值检查
  - name: "factor_range_check"
    type: "range"
    min: -100
    max: 100
    severity: "warning"
    action: "mark"
    
  # 因子缺失检查
  - name: "factor_missing_check"
    type: "missing"
    max_missing_ratio: 0.3  # 最大缺失率30%
    severity: "warning"
    action: "mark"
    
  # 因子异常值检查
  - name: "factor_outlier_check"
    type: "outlier"
    method: "zscore"  # zscore | iqr | mad
    threshold: 3.0
    severity: "info"
    action: "mark"
```

---

## 3. 清洗规则类型

### 3.1 范围检查（Range Check）

```python
from dataclasses import dataclass
from typing import Optional, Union
import pandas as pd

@dataclass
class RangeCheckRule:
    """范围检查规则"""
    name: str
    field: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    severity: str = "warning"
    action: str = "mark"
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """应用范围检查规则"""
        result = df.copy()
        
        # 检查下限
        if self.min_value is not None:
            mask_min = result[self.field] < self.min_value
            result.loc[mask_min, f'{self.field}_below_min'] = True
            
        # 检查上限
        if self.max_value is not None:
            mask_max = result[self.field] > self.max_value
            result.loc[mask_max, f'{self.field}_above_max'] = True
            
        # 标记异常
        mask = (
            (self.min_value is not None and result[self.field] < self.min_value) |
            (self.max_value is not None and result[self.field] > self.max_value)
        )
        result.loc[mask, f'{self.field}_range_anomaly'] = True
        
        return result
```

### 3.2 缺失值检查（Missing Check）

```python
@dataclass
class MissingCheckRule:
    """缺失值检查规则"""
    name: str
    fields: list
    max_missing_ratio: float = 0.3
    severity: str = "warning"
    action: str = "mark"
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """应用缺失值检查规则"""
        result = df.copy()
        
        # 计算缺失率
        for field in self.fields:
            missing_ratio = result[field].isna().sum() / len(result)
            result[f'{field}_missing_ratio'] = missing_ratio
            
            # 标记超过阈值的字段
            if missing_ratio > self.max_missing_ratio:
                result[f'{field}_high_missing'] = True
                
        return result
```

### 3.3 异常值检查（Outlier Check）

```python
import numpy as np

@dataclass
class OutlierCheckRule:
    """异常值检查规则"""
    name: str
    field: str
    method: str = "zscore"  # zscore | iqr | mad
    threshold: float = 3.0
    severity: str = "info"
    action: str = "mark"
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """应用异常值检查规则"""
        result = df.copy()
        
        if self.method == "zscore":
            # Z-Score方法
            mean = result[self.field].mean()
            std = result[self.field].std()
            z_scores = (result[self.field] - mean) / std
            mask = np.abs(z_scores) > self.threshold
            
        elif self.method == "iqr":
            # IQR方法
            Q1 = result[self.field].quantile(0.25)
            Q3 = result[self.field].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - self.threshold * IQR
            upper_bound = Q3 + self.threshold * IQR
            mask = (result[self.field] < lower_bound) | (result[self.field] > upper_bound)
            
        elif self.method == "mad":
            # MAD方法
            median = result[self.field].median()
            mad = np.median(np.abs(result[self.field] - median))
            modified_z_scores = 0.6745 * (result[self.field] - median) / mad
            mask = np.abs(modified_z_scores) > self.threshold
            
        result.loc[mask, f'{self.field}_outlier'] = True
        
        return result
```

---

## 4. 规则优先级

### 4.1 严重级别定义

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| **Critical** | 致命错误，数据不可用 | 标记并隔离 |
| **Warning** | 警告，数据可能有问题 | 标记并记录 |
| **Info** | 信息，数据有轻微异常 | 仅记录 |

### 4.2 规则执行顺序

```yaml
# 规则执行顺序
execution_order:
  1. "completeness_check"      # 完整性检查
  2. "range_check"             # 范围检查
  3. "negative_check"          # 负值检查
  4. "outlier_check"           # 异常值检查
  5. "equation_check"          # 等式检查
  6. "time_continuity_check"   # 时间连续性检查
```

---

## 5. 规则管理

### 5.1 规则版本控制

```yaml
# 规则版本历史
version_history:
  - version: "1.0"
    date: "2026-04-04"
    changes:
      - "初始版本，建立基础清洗规则"
      - "添加行情数据清洗规则"
      - "添加财务数据清洗规则"
      
  - version: "1.1"
    date: "2026-04-05"
    changes:
      - "添加因子数据清洗规则"
      - "优化异常值检测算法"
```

### 5.2 规则测试

```python
def test_cleaning_rule(rule, test_data):
    """测试清洗规则"""
    # 应用规则
    result = rule.apply(test_data)
    
    # 统计异常数量
    anomaly_count = result[f'{rule.field}_anomaly'].sum()
    anomaly_ratio = anomaly_count / len(result)
    
    print(f"规则: {rule.name}")
    print(f"异常数量: {anomaly_count}")
    print(f"异常比例: {anomaly_ratio:.2%}")
    
    return result
```

---

## 6. 使用示例

### 6.1 加载规则配置

```python
import yaml
from pathlib import Path

def load_cleaning_rules(config_path: str):
    """加载清洗规则配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

# 加载规则
rules = load_cleaning_rules('config/cleaning_rules.yaml')
```

### 6.2 应用清洗规则

```python
from zephyr.data.cleaning import CleaningEngine

# 创建清洗引擎
engine = CleaningEngine(rules_path='config/cleaning_rules.yaml')

# 应用清洗规则
cleaned_data = engine.clean(
    data=df,
    data_type='market_data',
    subtype='daily'
)

# 查看清洗结果
print(f"原始数据: {len(df)} 行")
print(f"异常数据: {cleaned_data['anomaly'].sum()} 行")
print(f"正常数据: {(~cleaned_data['anomaly']).sum()} 行")
```

---

## 7. 最佳实践

### 7.1 规则设计原则

1. **保守原则**: 宁可漏报，不可误报
2. **可解释性**: 每个规则都有明确的业务含义
3. **可配置性**: 所有参数都可通过配置文件调整
4. **可追溯性**: 记录所有清洗操作的详细信息

### 7.2 规则维护建议

1. **定期审查**: 每月审查规则有效性
2. **持续优化**: 根据实际数据情况调整规则
3. **版本管理**: 使用Git管理规则配置文件
4. **文档更新**: 及时更新规则文档

---

## 8. 相关文档

- [数据清洗引擎蓝图](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md) - 清洗引擎架构设计
- [数据质量管理系统](01_FRAMEWORK/DATA_QUALITY_MANAGEMENT_BLUEPRINT.md) - 数据质量管理
- [数据采集系统](02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_ACQUISITION.md) - 数据采集方案

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-04 | **维护者**: 首席文档架构师

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
