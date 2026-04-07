---
module_id: DATA_STANDARDIZATION_ENGINE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: ä¸ä¸æ å
responsibility:
  - æ°æ®æ ååå¼æ?
  - æ°æ®æ ¼å¼ç»ä¸
  - æ°æ®æ åå?
  - æ°æ®ç±»åè½¬æ¢
layer: "Layer 1 (æ°æ®å±?"
---

# æ°æ®æ ååå¼æèå?

## 核心定位

负责数据标准化引擎的设计与实现，基于标准化规则，统一数据格式和编码，提升数据一致性。


## æ ¸å¿å®ä½

**åä¸èè´£**: æ°æ®æ ååä¸æ ¼å¼ç»ä¸

### èè´£è¾¹ç

| è´è´£ | ä¸è´è´?|
|------|--------|
| â?å­æ®µå½åæ åå?| â?æ°æ®å­å¨ |
| â?æ°æ®æ ¼å¼ç»ä¸ | â?æ°æ®æ¸æ´ |
| â?æ°æ®ç±»åè½¬æ¢ | â?æ°æ®è´¨éçæ§ |
| â?æ°æ®éªè¯ | â?æ°æ®è®¢é |
| â?æ åè§åç®¡ç | â?æ°æ®è¡ç¼?|

---

## 1. ææ¯éå

### 1.1 ä¸ºä»ä¹éæ©dbt + Great Expectations

| ç¹æ?| dbt + GE | Pandera | Pydantic |
|------|----------|---------|----------|
| æ°æ®è½¬æ¢ | â­â­â­â­â­?| â­â­â­?| â­â­â­?|
| æ°æ®éªè¯ | â­â­â­â­â­?| â­â­â­â­â­?| â­â­â­â­ |
| SQLæ¯æ | â?| â?| â?|
| ææ¡£çæ | â?| â?| â?|
| å­¦ä¹ æ²çº¿ | â­â­â­?| â­â­â­â­ | â­â­â­â­â­?|
| **æ¨èææ°** | **â­â­â­â­â­?* | â­â­â­â­ | â­â­â­â­ |

---

## 2. æ¶æè®¾è®¡

### 2.1 æ´ä½æ¶æ

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   æ°æ®æ ååå¼ææ¶æ?                           â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                                â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â? â?æ åè§åå±?  â?   â?æ°æ®è½¬æ¢å±?  â?   â?æ°æ®éªè¯å±?  â?    â?
â? â?             â?   â?             â?   â?             â?    â?
â? â?â?å½åè§å   â?   â?â?æ ¼å¼è½¬æ¢   â?   â?â?ç±»åéªè¯   â?    â?
â? â?â?æ ¼å¼è§å   â?   â?â?ç±»åè½¬æ¢   â?   â?â?èå´éªè¯   â?    â?
â? â?â?éªè¯è§å   â?   â?â?åä½è½¬æ¢   â?   â?â?å¯ä¸æ§éªè¯?â?    â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â?        â?                  â?                   â?             â?
â?        âââââââââââââââââââââ´âââââââââââââââââââââ?             â?
â?                           â?                                   â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?                   æ ååæµç¨?                           â?  â?
â? â? 1. å½åæ åå?â?2. æ ¼å¼ç»ä¸ â?3. ç±»åè½¬æ¢ â?4. éªè¯    â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                                                                â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

---

## 3. æ ¸å¿åè½å®ç°

### 3.1 å½åæ åå?

```python
import re
from typing import Dict, List

class NamingStandardizer:
    """å½åæ ååå¨"""
    
    FIELD_MAPPING = {
        # åå§åç§° -> æ ååç§°
        "è¡ç¥¨ä»£ç ": "symbol",
        "äº¤ææ¥æ": "trade_date",
        "å¼çä»·": "open",
        "æé«ä»·": "high",
        "æä½ä»·": "low",
        "æ¶çä»?: "close",
        "æäº¤é?: "volume",
        "æäº¤é¢?: "amount",
    }
    
    @classmethod
    def standardize_field_name(cls, name: str) -> str:
        """æ ååå­æ®µå"""
        if name in cls.FIELD_MAPPING:
            return cls.FIELD_MAPPING[name]
        
        name = name.lower()
        name = re.sub(r'[^\w]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        return name
    
    @classmethod
    def standardize_dataframe(cls, df) -> 'DataFrame':
        """æ ååDataFrameåå"""
        rename_map = {
            col: cls.standardize_field_name(col)
            for col in df.columns
        }
        return df.rename(columns=rename_map)
```

### 3.2 æ°æ®æ ¼å¼ç»ä¸

```python
from datetime import datetime
from decimal import Decimal
from typing import Union

class FormatStandardizer:
    """æ ¼å¼æ ååå¨"""
    
    @staticmethod
    def standardize_date(value: Union[str, datetime], format: str = "%Y-%m-%d") -> str:
        """æ ååæ¥ææ ¼å¼?""
        if isinstance(value, datetime):
            return value.strftime(format)
        
        if isinstance(value, str):
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Yå¹?mæ?dæ?]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(format)
                except ValueError:
                    continue
        
        return value
    
    @staticmethod
    def standardize_symbol(symbol: str) -> str:
        """æ ååè¡ç¥¨ä»£ç ?""
        symbol = symbol.upper().strip()
        
        if symbol.isdigit():
            if symbol.startswith('6'):
                return f"{symbol}.SH"
            else:
                return f"{symbol}.SZ"
        
        return symbol
    
    @staticmethod
    def standardize_price(value: Union[str, float, Decimal]) -> Decimal:
        """æ ååä»·æ ?""
        if isinstance(value, str):
            value = value.replace(',', '')
        
        return Decimal(str(value)).quantize(Decimal('0.0001'))
```

### 3.3 æ°æ®éªè¯

```python
from dataclasses import dataclass
from typing import List, Optional
import pandas as pd

@dataclass
class ValidationRule:
    """éªè¯è§å"""
    field: str
    rule_type: str
    params: dict
    error_message: str

class DataValidator:
    """æ°æ®éªè¯å?""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule):
        """æ·»å éªè¯è§å"""
        self.rules.append(rule)
    
    def validate(self, df: pd.DataFrame) -> dict:
        """éªè¯æ°æ®"""
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        for rule in self.rules:
            if rule.field not in df.columns:
                results["warnings"].append(f"å­æ®µ {rule.field} ä¸å­å?)
                continue
            
            errors = self._apply_rule(df, rule)
            if errors:
                results["valid"] = False
                results["errors"].extend(errors)
        
        return results
    
    def _apply_rule(self, df: pd.DataFrame, rule: ValidationRule) -> List[str]:
        """åºç¨éªè¯è§å"""
        errors = []
        
        if rule.rule_type == "not_null":
            null_count = df[rule.field].isnull().sum()
            if null_count > 0:
                errors.append(f"{rule.field}: {null_count} æ¡ç©ºå?)
        
        elif rule.rule_type == "range":
            min_val = rule.params.get("min")
            max_val = rule.params.get("max")
            
            if min_val is not None:
                invalid = df[df[rule.field] < min_val]
                if len(invalid) > 0:
                    errors.append(f"{rule.field}: {len(invalid)} æ¡å°äºæå°å?{min_val}")
            
            if max_val is not None:
                invalid = df[df[rule.field] > max_val]
                if len(invalid) > 0:
                    errors.append(f"{rule.field}: {len(invalid)} æ¡å¤§äºæå¤§å?{max_val}")
        
        elif rule.rule_type == "unique":
            duplicates = df[df.duplicated(subset=[rule.field])]
            if len(duplicates) > 0:
                errors.append(f"{rule.field}: {len(duplicates)} æ¡éå¤å?)
        
        return errors
```

### 3.4 æ ååç®¡é?

```python
class StandardizationPipeline:
    """æ ååç®¡é?""
    
    def __init__(self):
        self.naming_standardizer = NamingStandardizer()
        self.format_standardizer = FormatStandardizer()
        self.validator = DataValidator()
    
    def process(self, df: pd.DataFrame, config: dict) -> pd.DataFrame:
        """æ§è¡æ ååæµç¨?""
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
            raise ValueError(f"æ°æ®éªè¯å¤±è´¥: {validation_result['errors']}")
        
        return df
```

---

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**ææ¡£ç»æ**
