---
module_id: DATA_STANDARDIZATION_ENGINE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 1 数据�?
compliance_level: 专业标准
responsibility:
  - 数据标准化引�?
  - 数据格式统一
  - 数据标准�?
  - 数据类型转换
layer: "Layer 1 (数据�?"
---

# 数据标准化引擎蓝�?

> **核心职责**: 数据标准化、数据格式统一、数据验�?
> **职责边界**: 
> - �?本模块负责：字段命名标准化、数据格式统一、数据类型转换、数据验�?
> - �?本模块不负责：数据存储、数据清洗、数据质量监�?

## 核心定位

**单一职责**: 数据标准化与格式统一

### 职责边界

| 负责 | 不负�?|
|------|--------|
| �?字段命名标准�?| �?数据存储 |
| �?数据格式统一 | �?数据清洗 |
| �?数据类型转换 | �?数据质量监控 |
| �?数据验证 | �?数据订阅 |
| �?标准规则管理 | �?数据血�?|

---

## 1. 技术选型

### 1.1 为什么选择dbt + Great Expectations

| 特�?| dbt + GE | Pandera | Pydantic |
|------|----------|---------|----------|
| 数据转换 | ⭐⭐⭐⭐�?| ⭐⭐�?| ⭐⭐�?|
| 数据验证 | ⭐⭐⭐⭐�?| ⭐⭐⭐⭐�?| ⭐⭐⭐⭐ |
| SQL支持 | �?| �?| �?|
| 文档生成 | �?| �?| �?|
| 学习曲线 | ⭐⭐�?| ⭐⭐⭐⭐ | ⭐⭐⭐⭐�?|
| **推荐指数** | **⭐⭐⭐⭐�?* | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────�?
�?                   数据标准化引擎架�?                           �?
├─────────────────────────────────────────────────────────────────�?
�?                                                                �?
�? ┌──────────────�?   ┌──────────────�?   ┌──────────────�?    �?
�? �?标准规则�?  �?   �?数据转换�?  �?   �?数据验证�?  �?    �?
�? �?             �?   �?             �?   �?             �?    �?
�? �?�?命名规则   �?   �?�?格式转换   �?   �?�?类型验证   �?    �?
�? �?�?格式规则   �?   �?�?类型转换   �?   �?�?范围验证   �?    �?
�? �?�?验证规则   �?   �?�?单位转换   �?   �?�?唯一性验�?�?    �?
�? └──────────────�?   └──────────────�?   └──────────────�?    �?
�?        �?                  �?                   �?             �?
�?        └───────────────────┴────────────────────�?             �?
�?                           �?                                   �?
�? ┌─────────────────────────────────────────────────────────�?  �?
�? �?                   标准化流�?                           �?  �?
�? �? 1. 命名标准�?�?2. 格式统一 �?3. 类型转换 �?4. 验证    �?  �?
�? └─────────────────────────────────────────────────────────�?  �?
�?                                                                �?
└─────────────────────────────────────────────────────────────────�?
```

---

## 3. 核心功能实现

### 3.1 命名标准�?

```python
import re
from typing import Dict, List

class NamingStandardizer:
    """命名标准化器"""
    
    FIELD_MAPPING = {
        # 原始名称 -> 标准名称
        "股票代码": "symbol",
        "交易日期": "trade_date",
        "开盘价": "open",
        "最高价": "high",
        "最低价": "low",
        "收盘�?: "close",
        "成交�?: "volume",
        "成交�?: "amount",
    }
    
    @classmethod
    def standardize_field_name(cls, name: str) -> str:
        """标准化字段名"""
        if name in cls.FIELD_MAPPING:
            return cls.FIELD_MAPPING[name]
        
        name = name.lower()
        name = re.sub(r'[^\w]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        return name
    
    @classmethod
    def standardize_dataframe(cls, df) -> 'DataFrame':
        """标准化DataFrame列名"""
        rename_map = {
            col: cls.standardize_field_name(col)
            for col in df.columns
        }
        return df.rename(columns=rename_map)
```

### 3.2 数据格式统一

```python
from datetime import datetime
from decimal import Decimal
from typing import Union

class FormatStandardizer:
    """格式标准化器"""
    
    @staticmethod
    def standardize_date(value: Union[str, datetime], format: str = "%Y-%m-%d") -> str:
        """标准化日期格�?""
        if isinstance(value, datetime):
            return value.strftime(format)
        
        if isinstance(value, str):
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y�?m�?d�?]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(format)
                except ValueError:
                    continue
        
        return value
    
    @staticmethod
    def standardize_symbol(symbol: str) -> str:
        """标准化股票代�?""
        symbol = symbol.upper().strip()
        
        if symbol.isdigit():
            if symbol.startswith('6'):
                return f"{symbol}.SH"
            else:
                return f"{symbol}.SZ"
        
        return symbol
    
    @staticmethod
    def standardize_price(value: Union[str, float, Decimal]) -> Decimal:
        """标准化价�?""
        if isinstance(value, str):
            value = value.replace(',', '')
        
        return Decimal(str(value)).quantize(Decimal('0.0001'))
```

### 3.3 数据验证

```python
from dataclasses import dataclass
from typing import List, Optional
import pandas as pd

@dataclass
class ValidationRule:
    """验证规则"""
    field: str
    rule_type: str
    params: dict
    error_message: str

class DataValidator:
    """数据验证�?""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule):
        """添加验证规则"""
        self.rules.append(rule)
    
    def validate(self, df: pd.DataFrame) -> dict:
        """验证数据"""
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        for rule in self.rules:
            if rule.field not in df.columns:
                results["warnings"].append(f"字段 {rule.field} 不存�?)
                continue
            
            errors = self._apply_rule(df, rule)
            if errors:
                results["valid"] = False
                results["errors"].extend(errors)
        
        return results
    
    def _apply_rule(self, df: pd.DataFrame, rule: ValidationRule) -> List[str]:
        """应用验证规则"""
        errors = []
        
        if rule.rule_type == "not_null":
            null_count = df[rule.field].isnull().sum()
            if null_count > 0:
                errors.append(f"{rule.field}: {null_count} 条空�?)
        
        elif rule.rule_type == "range":
            min_val = rule.params.get("min")
            max_val = rule.params.get("max")
            
            if min_val is not None:
                invalid = df[df[rule.field] < min_val]
                if len(invalid) > 0:
                    errors.append(f"{rule.field}: {len(invalid)} 条小于最小�?{min_val}")
            
            if max_val is not None:
                invalid = df[df[rule.field] > max_val]
                if len(invalid) > 0:
                    errors.append(f"{rule.field}: {len(invalid)} 条大于最大�?{max_val}")
        
        elif rule.rule_type == "unique":
            duplicates = df[df.duplicated(subset=[rule.field])]
            if len(duplicates) > 0:
                errors.append(f"{rule.field}: {len(duplicates)} 条重复�?)
        
        return errors
```

### 3.4 标准化管�?

```python
class StandardizationPipeline:
    """标准化管�?""
    
    def __init__(self):
        self.naming_standardizer = NamingStandardizer()
        self.format_standardizer = FormatStandardizer()
        self.validator = DataValidator()
    
    def process(self, df: pd.DataFrame, config: dict) -> pd.DataFrame:
        """执行标准化流�?""
        df = self.naming_standardizer.standardize_dataframe(df)
        
        for field, format_type in config.get("format_rules", {}).items():
            if field in df.columns:
                if format_type == "date":
                    df[field] = df[field].apply(self.format_standardizer.standardize_date)
                elif format_type == "symbol":
                    df[field] = df[field].apply(self.format_standardizer.standardize_symbol)
                elif format_type == "price":
                    df[field] = df[field].apply(self.format_standardizer.standardize_price)
        
        validation_result = self.validator.validate(df)
        if not validation_result["valid"]:
            raise ValueError(f"数据验证失败: {validation_result['errors']}")
        
        return df
```

---

## 📋 变更历史

| 版本 | 日期 | 变更内容 | 作�?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席架构�?|

---

**文档结束**
