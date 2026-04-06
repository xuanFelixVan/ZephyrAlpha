---
module_id: DESIGN_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 因子计算
  - 交易执行
  - 数据源
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲
applicable_scope: ﮔ۷۰ﮔﻛﭦ۳ﮔﻝﺏﭨﻝﭨ
compliance_level: ﮔﭘﮔﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# Aﻟ۰ﻟ۶ﮒﮒﺙﮔﻟ؟ﺝﻟ؟۰ﮔﮔ۰?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - Aﻟ۰ﻟ۶ﮒﮒﺙﮔﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟?
> **ﻝﺑ۱ﮒﺙ**: `DESIGN_A_STOCK_RULES_001`
> **ﻟ؟ﺝﻟ؟۰ﮔﭘﻠﺑ**: 3-5ﮒ۳?
> **ﮔ ﺕﮒﺟﮒ؟ﻛﺛ**: ﻝﭨﻛﺕﻝ؟۰ﻝAﻟ۰ﮒﺕﮒﭦﻛﭦ۳ﮔﻟ۶ﮒﺅﺙﻝ۰؟ﻛﺟﮔ۷۰ﮔﻛﭦ۳ﮔﻝ؛۵ﮒﻝﮒ؟ﮒﺕﮒﭦﻟ۶ﮒ

## 1. ﻟ؟ﺝﻟ؟۰ﮒﮒ

| ﮒﮒ | ﻟﺁﺑﮔ | ﮒ؟ﻝﺍﮔﺗﮒﺙ |
|------|------|----------|
| **ﻟ۶ﮒﮒﺏﻠﻝﺛ?* | ﮔﮔﻟ۶ﮒﻛﭨ۴YAMLﻠﻝﺛ؟ﮒ؟ﻛﺗﺅﺙﻛﺕﮒﮔ­ﭨﻛﭨ۲ﻝ  | ﻟ۶ﮒﻠﻝﺛ؟ﮔﻛﭨﭘ + ﮒ۷ﮔﮒ ﻟﺛ?|
| **ﮔ۷۰ﮒﮒﻟ؟ﺝﻟ؟?* | ﻛﺕﮒﻟ۶ﮒﻝﺎﭨﮒﻝ؛ﻝ،ﮔ۷۰ﮒﺅﺙﻛﺝﺟﻛﭦﻝﭨﺑﮔ۳ﮔ۸ﮒﺎ?| ﻟ۶ﮒﮒﻝﺎﭨﻛﺛﻝﺏﭨ + ﮔﻛﭨﭘﮔﭦﮒﭘ |
| **ﻠ،ﮔ۶ﻟﺛﮔ۲ﮔ?* | ﻟ۶ﮒﮔ۲ﮔ۴ﻠﻠ،ﮔ۶ﻟﺛﺅﺙﻛﺕﮒﺛﺎﮒﻛﭦ۳ﮔﮔ۶ﻟ۰ | ﻟ۶ﮒﻝﺙﮒ­ + ﮒﺗﭘﻟ۰ﮔ۲ﮔ?|
| **ﮒ؟ﮔﺑﻟ۵ﻝ** | ﻟ۵ﻝAﻟ۰ﮔﮔﮔ ﺕﮒﺟﻛﭦ۳ﮔﻟ۶ﮒ?| T+1ﻙﮔﭘ۷ﻟﺓﮒﻙSTﻙﻟﺑﺗﻝ۷ﻙﻠ۲ﻠ?|
| **ﻝﺎﺝﻝ۰؟ﮔ۷۰ﮔ** | ﻟ۶ﮒﮔ۶ﻟ۰ﻝﭨﮔﻛﺕﻝﮒ؟ﮒﺕﮒﭦﻛﺕﻟ?| ﮒﭦﻛﭦﻝﮒ؟ﻛﭦ۳ﮔﻟ۶ﮒﻠ۹ﻟﺁ |

## 2. ﻟ۶ﮒﮒﻝﺎﭨﻛﺛﻝﺏﭨ

### 2.1 ﻛﭦ۳ﮔﻟ۶ﮒﻝﺎﭨﺅﺙTrade Rulesﺅﺙ?
- **T+1ﻟ۶ﮒ**ﺅﺙﮒﺛﮔ۴ﻛﺗﺍﮒ۴ﮔ؛۰ﮔ۴ﮒﺁﮒﮒﭦ
- **ﮔﭘ۷ﻟﺓﮒﻟ۶ﮒ?*ﺅﺙﻛﺕﭨﮔ?0%ﻙﮒﻛﺕﮔﺟ/ﻝ۶ﮒﮔ?0%ﻙSTﻟ?%
- **STﻟ۰ﻝ۴۷ﻟ۶ﮒ**ﺅﺙﻝﺗﮔ؟ﻛﭦ۳ﮔﻠﮒ?
- **ﮔﺍﻟ۰ﻟ۶ﮒ**ﺅﺙﻠ۵ﮔ۴ﮔﭘ۷ﻟﺓﮒﺗﻠﮒﭘﻙﻛﺕﺑﮔﭘﮒﻝ?
- **ﮒ۳۶ﮒ؟ﻛﭦ۳ﮔﻟ۶ﮒ**ﺅﺙﮒ۳۶ﮒ؟ﻛﭦ۳ﮔﻠﮒ?

### 2.2 ﻟﺑﺗﻝ۷ﻟ۶ﮒﻝﺎﭨﺅﺙFee Rulesﺅﺙ?
- **ﻛﺛ۲ﻠﻟ۶ﮒ**ﺅﺙﻛﺕﻛﺕﺅﺙﮔﻛﺛ?ﮒﺅﺙﮒﮒﮔﭘﮒ
- **ﮒﺍﻟﺎﻝ۷ﻟ۶ﮒ?*ﺅﺙﮒﻛﺕﺅﺙﮒﮒﭦﮔﭘﮒﮒﮔﭘﮒ
- **ﻟﺟﮔﺓﻟﺑﺗﻟ۶ﮒ?*ﺅﺙﻛﺕ0.1ﺅﺙﮔﺎ۹ﮔﺓﺎﮒﺓ؟ﮒﺙﺅﺙﮒﮒﮔﭘﮒ
- **ﻟ۶ﻟﺑﺗﻟ۶ﮒ**ﺅﺙﻛﺕ0.2ﺅﺙﮒﮒﮔﭘﮒ?
- **ﮔﭨﻝﺗﮔ۷۰ﮒ**ﺅﺙﮒﭦﻛﭦﮔﭖﮒ۷ﮔ۶ﻝﮒ۷ﮔﮔﭨﻝﺗﻟ؟۰ﻝ؟?

### 2.3 ﻠ۲ﻠ۸ﻟ۶ﮒﻝﺎﭨﺅﺙRisk Rulesﺅﺙ?
- **ﮒﻟ۰ﻛﭨﻛﺛﻠﮒﭘ**ﺅﺙﮒﻝ۴۷ﮔﮒ۳۶ﻛﭨﻛﺛﮔﺁﻛﺝ?
- **ﮔﭨﻛﭨﻛﺛﻠﮒ?*ﺅﺙﮔﭨﮔﻛﭨﮒﺕﮒﺙﻠﮒ?
- **ﮔ۴ﮔ۱ﮔﻝﻠﮒﭘ**ﺅﺙﮒﺛﮔ۴ﮔﮒ۳۶ﮔ۱ﮔﻝ
- **ﻠﭨﮒﮒﻠﮒ?*ﺅﺙﻝ۵ﮔ­۱ﻛﭦ۳ﮔﻝﻟ۰ﻝ۴۷ﮒﻟ۰۷
- **ﮔﭖﮒ۷ﮔ۶ﻠﮒ?*ﺅﺙﮔﮒﺍﮔﻛﭦ۳ﻠﻟ۵ﮔﺎ

### 2.4 ﮒﺕﮒﭦﻟ۶ﮒﻝﺎﭨﺅﺙMarket Rulesﺅﺙ?
- **ﻛﭦ۳ﮔﮔﭘﻠﺑﻟ۶ﮒ**ﺅﺙﮒﺙﻝﻙﮔﭘﻝﻙﮒﻠﺑﻛﺙﮒﺕ?
- **ﻠﮒﻝ،ﻛﭨﺓﻟ۶ﮒ**ﺅﺙﮒﺙﻝ?ﮔﭘﻝﻠﮒﻝ،ﻛﭨﺓﮔﭦﮒﭘ
- **ﻟﺟﻝﭨ­ﻝ،ﻛﭨﺓﻟ۶ﮒ**ﺅﺙﻛﭨﺓﮔ ﺙﻛﺙﮒﻙﮔﭘﻠﺑﻛﺙﮒ?
- **ﻛﺕﺑﮔﭘﮒﻝﻟ۶ﮒ**ﺅﺙﮔﭘ۷ﻟﺓﮒﻟ۶۵ﮒﻝﻛﺕﺑﮔﭘﮒﻝ?

## 3. ﮔﭘﮔﻟ؟ﺝﻟ؟۰

### 3.1 ﻝﺎﭨﮒﺝﻟ؟ﺝﻟ؟۰

```mermaid
classDiagram
    class AStockRuleEngine {
        -rule_registry: Dict[str, BaseRule]
        -rule_configs: List[RuleConfig]
        +check_order(order: UnifiedOrder) RuleResult
        +check_position(position: Position) RuleResult
        +calculate_fees(order: UnifiedOrder) FeeResult
    }
    
    class BaseRule {
        <<abstract>>
        +rule_id: str
        +rule_name: str
        +category: str
        +enabled: bool
        +check(context: Dict) RuleResult
        +get_description() str
    }
    
    class T1Rule {
        -lock_days: int = 1
        -exceptions: List[str]
        +check_sell_permission(position, buy_date, current_date) RuleResult
        +get_unlock_date(buy_date) datetime
    }
    
    class LimitUpDownRule {
        -limit_rates: Dict[str, float]
        +check_limit_price(symbol, price, preclose) RuleResult
        +get_limit_price(symbol, preclose) float
        +is_limit_up(symbol, price, preclose) bool
    }
    
    class TradingFeeRule {
        -commission_rate: float
        -stamp_tax_rate: float
        -transfer_fee_rate: float
        +calculate_commission(amount, side) float
        +calculate_stamp_tax(amount, side) float
        +calculate_total_fees(order) FeeResult
    }
    
    class RiskRule {
        -max_position_ratio: float
        -max_daily_turnover: float
        +check_position_limit(positions, total_capital) RuleResult
        +check_turnover_limit(daily_turnover) RuleResult
    }
    
    AStockRuleEngine --> BaseRule : ﮒﮒ،
    BaseRule <|-- T1Rule : ﻝﭨ۶ﮔﺟ
    BaseRule <|-- LimitUpDownRule : ﻝﭨ۶ﮔﺟ
    BaseRule <|-- TradingFeeRule : ﻝﭨ۶ﮔﺟ
    BaseRule <|-- RiskRule : ﻝﭨ۶ﮔﺟ
    
    class RuleResult {
        +passed: bool
        +rule_id: str
        +message: str
        +details: Dict
        +actions: List[str]
    }
    
    class FeeResult {
        +commission: float
        +stamp_tax: float
        +transfer_fee: float
        +total_fee: float
        +breakdown: Dict[str, float]
    }
```

### 3.2 ﮔ ﺕﮒﺟﮔ۴ﮒ۲ﮒ؟ﻛﺗ

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class RuleCategory(str, Enum):
    """ﻟ۶ﮒﮒﻝﺎﭨ"""
    TRADE = "trade"      # ﻛﭦ۳ﮔﻟ۶ﮒ
    FEE = "fee"          # ﻟﺑﺗﻝ۷ﻟ۶ﮒ
    RISK = "risk"        # ﻠ۲ﻠ۸ﻟ۶ﮒ
    MARKET = "market"    # ﮒﺕﮒﭦﻟ۶ﮒ


class RuleSeverity(str, Enum):
    """ﻟ۶ﮒﻛﺕ۴ﻠﻝ۷ﮒﭦ۵"""
    INFO = "info"        # ﻛﺟ۰ﮔﺁ
    WARNING = "warning"  # ﻟ­۵ﮒ
    ERROR = "error"      # ﻠﻟﺁﺁ
    CRITICAL = "critical" # ﻛﺕ۴ﻠ


@dataclass
class RuleResult:
    """ﻟ۶ﮒﮔ۲ﮔ۴ﻝﭨﮔ?""
    passed: bool                    # ﮔﺁﮒ۵ﻠﻟﺟ
    rule_id: str                    # ﻟ۶ﮒID
    rule_name: str                  # ﻟ۶ﮒﮒﻝ۶ﺍ
    category: RuleCategory          # ﻟ۶ﮒﮒﻝﺎﭨ
    severity: RuleSeverity          # ﻛﺕ۴ﻠﻝ۷ﮒﭦ۵
    message: str                    # ﮔ۲ﮔ۴ﻝﭨﮔﮔﭘﮔ?
    details: Dict[str, Any] = None  # ﻟﺁ۵ﻝﭨﻝﭨﮔ
    actions: List[str] = None       # ﮒﭨﭦﻟ؟؟ﮒ۷ﻛﺛ


@dataclass
class FeeResult:
    """ﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟ﻝﭨﮔ"""
    commission: float = 0.0          # ﻛﺛ۲ﻠ
    stamp_tax: float = 0.0           # ﮒﺍﻟﺎﻝ۷?
    transfer_fee: float = 0.0        # ﻟﺟﮔﺓﻟﺑ?
    misc_fee: float = 0.0            # ﮒﭘﻛﭨﻟﺑﺗﻝ۷
    total_fee: float = 0.0           # ﮔﭨﻟﺑﺗﻝ?
    breakdown: Dict[str, float] = None  # ﻟﺑﺗﻝ۷ﮔﻝﭨ


class BaseRule(ABC):
    """ﻟ۶ﮒﮒﭦﻝﺎﭨ"""
    
    def __init__(self, rule_id: str, rule_name: str, category: RuleCategory, 
                 enabled: bool = True, config: Dict[str, Any] = None):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.category = category
        self.enabled = enabled
        self.config = config or {}
    
    @abstractmethod
    def check(self, context: Dict[str, Any]) -> RuleResult:
        """ﮔ۲ﮔ۴ﻟ۶ﮒ?
        
        ﮒﮔﺍ:
            context: ﮔ۲ﮔ۴ﻛﺕﻛﺕﮔﺅﺙﮒﮒ،ﻟ؟۱ﮒﻙﮔﻛﭨﻙﮒﺕﮒﭦﮔﺍﮔ؟ﻝ­
            
        ﻟﺟﮒ:
            RuleResult: ﻟ۶ﮒﮔ۲ﮔ۴ﻝﭨﮔ?
        """
        pass
    
    def get_description(self) -> str:
        """ﻟﺓﮒﻟ۶ﮒﮔﻟﺟﺍ"""
        return f"{self.rule_name} ({self.rule_id})"
    
    def enable(self):
        """ﮒﺁﻝ۷ﻟ۶ﮒ"""
        self.enabled = True
    
    def disable(self):
        """ﻝ۵ﻝ۷ﻟ۶ﮒ"""
        self.enabled = False


class AStockRuleEngine:
    """Aﻟ۰ﻟ۶ﮒﮒﺙﮔ?""
    
    def __init__(self, config_path: str = None):
        self.rule_registry: Dict[str, BaseRule] = {}
        self.rule_configs: List[Dict] = []
        
        if config_path:
            self.load_config(config_path)
            self._initialize_rules()
    
    def register_rule(self, rule: BaseRule):
        """ﮔﺏ۷ﮒﻟ۶ﮒ"""
        self.rule_registry[rule.rule_id] = rule
    
    def check_order(self, order: Dict[str, Any], context: Dict[str, Any] = None) -> List[RuleResult]:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﮒﻟ۶ﮔ?
        
        ﮒﮔﺍ:
            order: ﻟ؟۱ﮒﮔﺍﮔ؟
            context: ﻠ۱ﮒ۳ﻛﺕﻛﺕﮔﺅﺙﮔﻛﭨﻙﻟﺑ۵ﮔﺓﻙﮒﺕﮒﭦﮔﺍﮔ؟ﻝ­ﺅﺙ?
            
        ﻟﺟﮒ:
            List[RuleResult]: ﮔﮔﻟ۶ﮒﮔ۲ﮔ۴ﻝﭨﮔ?
        """
        results = []
        check_context = {"order": order}
        if context:
            check_context.update(context)
        
        for rule in self.rule_registry.values():
            if not rule.enabled:
                continue
            
            # ﮒ۹ﮔ۲ﮔ۴ﻛﺕﻟ؟۱ﮒﻝﺕﮒﺏﻝﻟ۶ﮒ?
            if rule.category in [RuleCategory.TRADE, RuleCategory.FEE, RuleCategory.RISK]:
                result = rule.check(check_context)
                results.append(result)
        
        return results
    
    def calculate_fees(self, order: Dict[str, Any], market_data: Dict[str, Any] = None) -> FeeResult:
        """ﻟ؟۰ﻝ؟ﻛﭦ۳ﮔﻟﺑﺗﻝ۷
        
        ﮒﮔﺍ:
            order: ﻟ؟۱ﮒﮔﺍﮔ؟
            market_data: ﮒﺕﮒﭦﮔﺍﮔ؟ﺅﺙﻝ۷ﻛﭦﮔﭨﻝﺗﻟ؟۰ﻝ؟ﻝ­ﺅﺙ?
            
        ﻟﺟﮒ:
            FeeResult: ﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟ﻝﭨﮔ
        """
        # ﻟﺓﮒﻟﺑﺗﻝ۷ﻟ۶ﮒ
        fee_rules = [r for r in self.rule_registry.values() 
                    if r.category == RuleCategory.FEE and r.enabled]
        
        # ﻠﭨﻟ؟۳ﻟﺑﺗﻝ۷ﻝﭨﮔ
        fee_result = FeeResult()
        
        # ﮒﭦﻝ۷ﮔﮔﻟﺑﺗﻝ۷ﻟ۶ﮒ?
        for rule in fee_rules:
            if hasattr(rule, 'calculate_fees'):
                rule_fee_result = rule.calculate_fees(order, market_data)
                # ﮒﮒﺗﭘﻟﺑﺗﻝ۷ﻝﭨﮔ
                fee_result.commission += rule_fee_result.commission
                fee_result.stamp_tax += rule_fee_result.stamp_tax
                fee_result.transfer_fee += rule_fee_result.transfer_fee
                fee_result.misc_fee += rule_fee_result.misc_fee
        
        fee_result.total_fee = (
            fee_result.commission + 
            fee_result.stamp_tax + 
            fee_result.transfer_fee + 
            fee_result.misc_fee
        )
        
        return fee_result
    
    def load_config(self, config_path: str):
        """ﮒ ﻟﺛﺛﻟ۶ﮒﻠﻝﺛ؟"""
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            self.rule_configs = yaml.safe_load(f)
    
    def _initialize_rules(self):
        """ﮔ ﺗﮔ؟ﻠﻝﺛ؟ﮒﮒ۶ﮒﻟ۶ﮒ?""
        # ﻟﺟﻠﻛﺙﮔ ﺗﮔ؟ﻠﻝﺛ؟ﮒﮒﭨﭦﮒﺓﻛﺛﻝﻟ۶ﮒﮒ؟ﻛﺝ
        # ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕ­ﻛﺙﻛﺛﺟﻝ۷ﮒﺓ۴ﮒﮔ۷۰ﮒﺙ
        pass
```

## 4. ﻝﺍﮔﻛﭨ۲ﻝ ﮔﺑﮒﮔﺗﮔ۰

### 4.1 ﮒﺓﺎﮔﻛﭨ۲ﻝ ﮔ۷۰ﮒ

#### 4.1.1 T+1ﻛﭦ۳ﮔﻝﺏﭨﻝﭨﺅﺙﮔ۴ﻟ?technical_documentation.mdﺅﺙ?
```python
class T1TradingSystem:
    """T+1ﻛﭦ۳ﮔﮒﭘﮒﭦ۵ﻠﮒ"""
    T1_RULES = {
        'ﮒﺛﮔ۴ﻛﺗﺍﮒ۴ﻠﮒ؟': True,
        'ﮔ؛۰ﮔ۴ﻟ۶۲ﻠ۳ﻠﮒﭘ': True,
        'ﻠﻝ۷ﻟﮒﺑ': 'Aﻟ۰ﮒﺕﮒﭦﮔﮔﮒﻝ۶?,
        'ﻛﺝﮒ۳ﮔﮒﭖ': ['ETFﮒﭦﻠ', 'ﮒﺁﻟﺛ؛ﮒ?, 'ﮔﮔ']
    }
    
    def check_sell_permission(self, position, buy_date, current_date):
        """ﮔ۲ﮔ۴ﮒﮒﭦﮔﻠ?""
        if buy_date == current_date:
            return {
                'can_sell': False,
                'reason': 'T+1ﮒﭘﮒﭦ۵ﺅﺙﮒﺛﮔ۴ﻛﺗﺍﮒ۴ﻛﺕﻟﺛﮒﮒ?,
                'available_date': self.next_trading_day(buy_date)
            }
        return {'can_sell': True}
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﻠﮔﻛﺕ?`T1Rule` ﻝﺎﭨﺅﺙﻝﭨ۶ﮔﺟ `BaseRule`
- ﻛﺟﻝﮔ ﺕﮒﺟﻝ؟ﮔﺏﺅﺙﻠﻠﻝﭨﻛﺕﮔ۴ﮒ۲
- ﮔﺓﭨﮒ ﻠﻝﺛ؟ﮔﺁﮔﺅﺙﮔﺁﮔﻛﺝﮒ۳ﮒﻝ۶ﻠﻝﺛ?

#### 4.1.2 ﮔﭘ۷ﻟﺓﮒﮔﺟﻝﺏﭨﻝﭨﺅﺙﮔ۴ﻟ?technical_documentation.mdﺅﺙ?
```python
class LimitUpDownSystem:
    """ﮔﭘ۷ﻟﺓﮒﮔﺟﮒﭘﮒﭦ۵ﻠﮒ"""
    LIMIT_RULES = {
        'ﻛﺕﭨﮔﺟﺅﺙﮔﺎ۹ﮒﺕ?0/ﮔﺓﺎﮒﺕ000ﺅﺙ?: {
            'ﮔﭘ۷ﻟﺓﮒﮒﺗﮒﭦ?: 0.10,
            'STﻟ۰ﻝ۴۷ﮒﺗﮒﭦ۵': 0.05,
            'ﻠ۵ﮔ۴ﻛﺕﮒﺕﮒﺗﮒﭦ۵': 0.44
        },
        'ﮒﻛﺕﮔﺟﺅﺙ300ﺅﺙ?: {
            'ﮔﭘ۷ﻟﺓﮒﮒﺗﮒﭦ?: 0.20,
            'STﻟ۰ﻝ۴۷ﮒﺗﮒﭦ۵': 0.20,
            'ﻠ۵ﮔ۴ﻛﺕﮒﺕﮒﺗﮒﭦ۵': 0.44
        },
        'ﻝ۶ﮒﮔﺟﺅﺙ688ﺅﺙ?: {
            'ﮔﭘ۷ﻟﺓﮒﮒﺗﮒﭦ?: 0.20,
            'STﻟ۰ﻝ۴۷ﮒﺗﮒﭦ۵': 0.20,
            'ﻠ۵ﮔ۴ﻛﺕﮒﺕﮒﺗﮒﭦ۵':ﮔ ﮔﭘ۷ﻟﺓﮒ
        }
    }
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﻠﮔﻛﺕ?`LimitUpDownRule` ﻝﺎ?
- ﮔ۸ﮒﺎﻟ۶ﮒﻠﻝﺛ؟ﺅﺙﮔﺁﮔﮔﺑﮒ۳ﮔﺟﻝﺎﭨﮒ
- ﮔﺓﭨﮒ ﻛﭨﺓﮔ ﺙﮔ۲ﮔ۴ﻙﮔﭘ۷ﻟﺓﮒﮒ۳ﮔ­ﮔﺗﮔﺏ

#### 4.1.3 ﻛﭦ۳ﮔﻟﺑﺗﻝ۷ﮒﺕﺕﻠﺅﺙﮔ۴ﻟ?technical_documentation.mdﺅﺙ?
```python
TRADING_FEES = {
    'ﻛﺛ۲ﻠ': {'rate': 0.0003, 'min': 5, 'ﮒﮒ': True},
    'ﮒﺍﻟﺎﻝ۷?: {'rate': 0.001, 'min': 0, 'ﮒﮒ': 'sell'},
    'ﻟﺟﮔﺓﻟﺑ?: {'rate': 0.00001, 'min': 1, 'ﮒﮒ': True, 'market': 'SH'},
    'ﻟ۶ﻟﺑﺗ': {'rate': 0.00002, 'min': 0, 'ﮒﮒ': True}
}
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﻠﮔﻛﺕ?`TradingFeeRule` ﻝﺎ?
- ﮒ؟ﻝﺍﻝﺎﺝﻝ۰؟ﻝﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟ﻝ؟ﮔﺏ?
- ﮔﺁﮔﮔﺎ۹ﮔﺓﺎﮒﺕﮒﭦﮒﺓ؟ﮒﺙ
- ﮔﺓﭨﮒ ﮔﻛﺛﻟﺑﺗﻝ۷ﻙﻠﭘﮔ۱ﺁﻟﺑﺗﻝﮔﺁﮔ?

#### 4.1.4 ﻠ۲ﮔ۶ﻟ۶ﮒﮒﺙﮔﺅﺙﮔ۴ﻟ?RISK_RULE_ENGINE.mdﺅﺙ?
```python
class RiskRule:
    """ﻠ۲ﮔ۶ﻟ۶ﮒ"""
    def __init__(self, rule_id, name, category, severity, condition, action, enabled=True):
        self.rule_id = rule_id
        self.name = name
        self.category = category
        self.severity = severity
        self.condition = condition
        self.action = action
        self.enabled = enabled
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﻠﻝ۷ﻝﺍﮔ `RiskRule` ﻝﺎﭨﻟ؟ﺝﻟ؟?
- ﻠﻠﮒﺍﻝﭨﻛﺕﻟ۶ﮒﮔ۴ﮒ۲
- ﮔ۸ﮒﺎﻛﺕﭦAﻟ۰ﻝﺗﮒ؟ﻠ۲ﻠ۸ﻟ۶ﮒ?

#### 4.1.5 ﮔﭘ۷ﮒﮔﺟﮒﮔﺅﺙﮔ۴ﻟ۹ limit-up-analysis.mdﺅﺙ?
```python
class LimitUpAnalyzer:
    """ﮔﭘ۷ﮒﮔﺟﮒﮔ?""
    def is_limit_up(self, stock_data, limit_rate=0.10):
        """ﮒ۳ﮔ­ﮔﺁﮒ۵ﮔﭘ۷ﮒ"""
        change_pct = stock_data['change_pct']
        return abs(change_pct - limit_rate * 100) < 0.1
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﮔﺑﮒﮒ?`LimitUpDownRule` ﻛﺕ­ﻛﺛﻛﺕﭦﻟﺝﮒ۸ﮔﺗﮔﺏ?
- ﻝ۷ﻛﭦﮒﺕﮒﭦﮔﺍﮔ؟ﮒﮔﮒﻟ۶ﮒﻠ۹ﻟﺁ?

### 4.2 ﻛﭨ۲ﻝ ﻟﺟﻝ۶ﭨﻟ؟۰ﮒ

1. **ﻝ؛؛ﻛﺕﻠﭘﮔ؟ﭖﺅﺙ?-2ﮒ۳۸ﺅﺙ**ﺅﺙﮒﮒﭨﭦﮒﭦﻝ۰ﮔ۰ﮔﭘ
   - ﮒ؟ﻝﺍ `BaseRule`ﻙ`RuleResult`ﻙ`FeeResult` ﻝ­ﮒﭦﻝ۰ﻝﺎ?
   - ﮒ؟ﻝﺍ `AStockRuleEngine` ﮔ ﺕﮒﺟﮒﺙﮔ

2. **ﻝ؛؛ﻛﭦﻠﭘﮔ؟ﭖﺅﺙ?-3ﮒ۳۸ﺅﺙ**ﺅﺙﻟﺟﻝ۶ﭨﻝﺍﮔﻟ۶ﮒ?
   - ﻟﺟﻝ۶ﭨ T+1 ﻟ۶ﮒﻛﺕ?`T1Rule`
   - ﻟﺟﻝ۶ﭨﮔﭘ۷ﻟﺓﮒﻟ۶ﮒﻛﺕﭦ `LimitUpDownRule`
   - ﻟﺟﻝ۶ﭨﻟﺑﺗﻝ۷ﻟ۶ﮒﻛﺕ?`TradingFeeRule`

3. **ﻝ؛؛ﻛﺕﻠﭘﮔ؟ﭖﺅﺙ?-2ﮒ۳۸ﺅﺙ**ﺅﺙﮔ۸ﮒﺎﮒﻟ?
   - ﮔﺓﭨﮒ STﻟ۰ﻝ۴۷ﻟ۶ﮒ
   - ﮔﺓﭨﮒ ﮔﺍﻟ۰ﻟ۶ﮒ
   - ﮔﺓﭨﮒ ﻠ۲ﻠ۸ﻟ۶ﮒﻠﮔ

## 5. ﻟ۶ﮒﻠﻝﺛ؟ﮔ۷۰ﮔﺟ

### 5.1 YAMLﻠﻝﺛ؟ﻝﭨﮔ

```yaml
# config/rules/a_stock_rules.yaml
version: "1.0"
engine: "AStockRuleEngine"
last_updated: "2026-04-02"

rules:
  # ============ ﻛﭦ۳ﮔﻟ۶ﮒ ============
  - rule_id: "TRADE_001"
    rule_name: "T+1ﻛﭦ۳ﮔﻟ۶ﮒ"
    category: "trade"
    enabled: true
    severity: "error"
    class: "T1Rule"
    config:
      lock_days: 1
      exceptions: ["ETF", "ﮒﺁﻟﺛ؛ﮒ?, "ﮔﮔ"]
      check_method: "check_sell_permission"
  
  - rule_id: "TRADE_002"
    rule_name: "ﮔﭘ۷ﻟﺓﮒﻟ۶ﮒ?
    category: "trade"
    enabled: true
    severity: "error"
    class: "LimitUpDownRule"
    config:
      limit_rates:
        "ﻛﺕﭨﮔﺟ":
          normal: 0.10
          st: 0.05
          first_day: 0.44
        "ﮒﻛﺕﮔ?:
          normal: 0.20
          st: 0.20
          first_day: 0.44
        "ﻝ۶ﮒﮔ?:
          normal: 0.20
          st: 0.20
          first_day: null  # ﮔ ﮔﭘ۷ﻟﺓﮒ
      precision: 0.01  # ﻛﭨﺓﮔ ﺙﻝﺎﺝﮒﭦ۵
  
  - rule_id: "TRADE_003"
    rule_name: "STﻟ۰ﻝ۴۷ﻟ۶ﮒ"
    category: "trade"
    enabled: true
    severity: "warning"
    class: "STRule"
    config:
      st_prefixes: ["*ST", "ST"]
      warning_days: 30
      delisting_threshold: 3  # ﻟﺟﻝﭨ­3ﮒﺗﺑﻛﭦﮔ?
  
  # ============ ﻟﺑﺗﻝ۷ﻟ۶ﮒ ============
  - rule_id: "FEE_001"
    rule_name: "ﻛﺛ۲ﻠﻟ۶ﮒ"
    category: "fee"
    enabled: true
    severity: "info"
    class: "CommissionRule"
    config:
      rate: 0.0003  # ﻛﺕﻛﺕ
      min_amount: 5.0
      both_sides: true
      calculate_method: "percentage_with_min"
  
  - rule_id: "FEE_002"
    rule_name: "ﮒﺍﻟﺎﻝ۷ﻟ۶ﮒ?
    category: "fee"
    enabled: true
    severity: "info"
    class: "StampTaxRule"
    config:
      rate: 0.001  # ﮒﻛﺕ
      apply_on: "sell"  # ﮒﮒﭦﮔﭘﮔﭘﮒ?
      exempt_categories: ["ETF", "ﮒﺛﮒ?]
  
  - rule_id: "FEE_003"
    rule_name: "ﻟﺟﮔﺓﻟﺑﺗﻟ۶ﮒ?
    category: "fee"
    enabled: true
    severity: "info"
    class: "TransferFeeRule"
    config:
      sh_rate: 0.00001  # ﮔﺎ۹ﮒﺕﻛﺕ?.1
      sz_rate: 0.00002  # ﮔﺓﺎﮒﺕﻛﺕ?.2
      min_amount: 1.0
      both_sides: true
  
  - rule_id: "FEE_004"
    rule_name: "ﮔﭨﻝﺗﮔ۷۰ﮒ"
    category: "fee"
    enabled: true
    severity: "info"
    class: "SlippageRule"
    config:
      base_rate: 0.0002  # ﮒﭦﻝ۰ﮔﭨﻝﺗﻝ?.02%
      liquidity_factor: true
      volatility_factor: true
      market_cap_weight: true
  
  # ============ ﻠ۲ﻠ۸ﻟ۶ﮒ ============
  - rule_id: "RISK_001"
    rule_name: "ﮒﻟ۰ﻛﭨﻛﺛﻠﮒﭘ"
    category: "risk"
    enabled: true
    severity: "error"
    class: "PositionLimitRule"
    config:
      max_position_ratio: 0.10  # ﮒﻟ۰ﮔﮒ۳?0%
      max_position_value: 1000000  # ﮒﻟ۰ﮔﮒ۳?00ﻛﺕ?
      apply_to: ["Aﻟ?, "ﮔﺕﺁﻟ۰"]
  
  - rule_id: "RISK_002"
    rule_name: "ﮔﭨﻛﭨﻛﺛﻠﮒ?
    category: "risk"
    enabled: true
    severity: "error"
    class: "TotalPositionRule"
    config:
      max_total_ratio: 0.80  # ﮔﭨﻛﭨﻛﺛﮔﮒ۳?0%
      cash_reserve_ratio: 0.05  # ﻝﺍﻠﮒ۷ﮒ۳5%
  
  - rule_id: "RISK_003"
    rule_name: "ﮔ۴ﮔ۱ﮔﻝﻠﮒﭘ"
    category: "risk"
    enabled: true
    severity: "warning"
    class: "TurnoverLimitRule"
    config:
      max_daily_turnover: 0.30  # ﮔ۴ﮔ۱ﮔﻝﻛﺕﻟﭘﻟﺟ?0%
      calculation_period: "daily"
  
  # ============ ﮒﺕﮒﭦﻟ۶ﮒ ============
  - rule_id: "MARKET_001"
    rule_name: "ﻛﭦ۳ﮔﮔﭘﻠﺑﻟ۶ﮒ"
    category: "market"
    enabled: true
    severity: "error"
    class: "TradingHoursRule"
    config:
      market_hours:
        "Aﻟ?:
          morning_open: "09:30"
          morning_close: "11:30"
          afternoon_open: "13:00"
          afternoon_close: "15:00"
        "ﮔﺕﺁﻟ۰":
          morning_open: "09:30"
          morning_close: "12:00"
          afternoon_open: "13:00"
          afternoon_close: "16:00"
      holidays: "config/holidays.yaml"
  
  - rule_id: "MARKET_002"
    rule_name: "ﻠﮒﻝ،ﻛﭨﺓﻟ۶ﮒ"
    category: "market"
    enabled: true
    severity: "info"
    class: "AuctionRule"
    config:
      auction_periods:
        "ﮒﺙﻝﻝ،ﻛﭨ?: "09:15-09:25"
        "ﮔﭘﻝﻝ،ﻛﭨﺓ": "14:57-15:00"
      price_discovery: "volume_weighted"
      match_method: "price_time_priority"
```

### 5.2 ﻠﻝﺛ؟ﻟﺁﺑﮔ

1. **ﻟ۶ﮒIDﮒﺛﮒﻟ۶ﻟ**ﺅﺙ`{ﻝﺎﭨﮒ،}_{ﮒﭦﮒﺓ}`ﺅﺙﮒ۵ `TRADE_001`
2. **ﻝﺎﭨﮒ،ﮔﻛﺕﺝ**ﺅﺙ`trade`ﻙ`fee`ﻙ`risk`ﻙ`market`
3. **ﻛﺕ۴ﻠﻝ۷ﮒﭦ۵**ﺅﺙ`info`ﻙ`warning`ﻙ`error`ﻙ`critical`
4. **ﻝﺎﭨﮒﮒﺙﻝ۷**ﺅﺙﻟ۶ﮒﮒ؟ﻝﺍﻝﺎﭨﻝﮒ۷ﻟﺓﺁﮒﺝﮒ?
5. **ﻠﻝﺛ؟ﮒﮔﺍ**ﺅﺙﮔﺁﻛﺕ۹ﻟ۶ﮒﻝﺗﮔﻝﻠﻝﺛ؟ﮒﮔﺍ

## 6. ﻠﮔﮒﺍﮒ۳ﮒﺙﮔﮔﭘﮔ

### 6.1 ﻛﺕﮒﺙﮔﻠﻠﮒ۷ﻝﻠﮔ

```python
class VnPySimulationAdapter(BaseEngineAdapter):
    """vn.pyﮔ۷۰ﮔﻛﭦ۳ﮔﻠﻠﮒ?""
    
    def __init__(self, config: VnPyConfig):
        super().__init__(config)
        # ﮒﮒ۶ﮒAﻟ۰ﻟ۶ﮒﮒﺙﮔ?
        self.rule_engine = AStockRuleEngine("config/rules/a_stock_rules.yaml")
    
    def submit_order(self, order: UnifiedOrder) -> Result:
        """ﮔﻛﭦ۳ﻟ؟۱ﮒ"""
        # 1. ﻟ۶ﮒﮔ۲ﮔ?
        rule_results = self.rule_engine.check_order(order.to_dict())
        
        # 2. ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮔﻠﻟﺁﺁﻝﭦ۶ﮒ،ﻝﻟ۶ﮒﻟﺟﻟ۶?
        critical_errors = [r for r in rule_results 
                          if r.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL] 
                          and not r.passed]
        
        if critical_errors:
            error_msg = "; ".join([f"{r.rule_name}: {r.message}" for r in critical_errors])
            return Result.error(f"ﻟ؟۱ﮒﻟﺟﮒﻟ۶ﮒ: {error_msg}")
        
        # 3. ﻟ؟۰ﻝ؟ﻟﺑﺗﻝ۷
        fee_result = self.rule_engine.calculate_fees(order.to_dict())
        order.metadata['fees'] = fee_result
        
        # 4. ﮔ۶ﻟ۰ﻟ؟۱ﮒ
        return self._execute_order(order)
```

### 6.2 ﻝﭨﻛﺕﻟ۶ﮒﮔ۲ﮔ۴ﻝﺗ

1. **ﻛﺕﮒﮒﮔ۲ﮔ?*ﺅﺙﻟ؟۱ﮒﮒﻟ۶ﮔ۶ﻙﻠ۲ﻠ۸ﻠﮒ?
2. **ﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟**ﺅﺙﻝﺎﺝﻝ۰؟ﻟ؟۰ﻝ؟ﻛﭦ۳ﮔﮔﮔ?
3. **ﮔﻛﭦ۳ﮒﻠ۹ﻟﺁ?*ﺅﺙﮔ۲ﮔ۴ﮔﻛﭦ۳ﻛﭨﺓﮔ ﺙﮔﺁﮒ۵ﻝ؛۵ﮒﻟ۶ﮒ?
4. **ﮔﻛﭨﻝﮔ۶**ﺅﺙﮔﻝﭨ­ﻝﮔ۶ﮔﻛﭨﮔﺁﮒ۵ﻝ؛۵ﮒﻟ۶ﮒ?

## 7. ﮔﭖﻟﺁﮔﺗﮔ۰

### 7.1 ﮒﮒﮔﭖﻟﺁ

```python
import pytest
from a_stock_rules import AStockRuleEngine, T1Rule, LimitUpDownRule

class TestAStockRuleEngine:
    """Aﻟ۰ﻟ۶ﮒﮒﺙﮔﮔﭖﻟﺁ?""
    
    def setup_method(self):
        self.engine = AStockRuleEngine()
        self.engine.register_rule(T1Rule("TRADE_001", "T+1ﻟ۶ﮒ", RuleCategory.TRADE))
        self.engine.register_rule(LimitUpDownRule("TRADE_002", "ﮔﭘ۷ﻟﺓﮒﻟ۶ﮒ?, RuleCategory.TRADE))
    
    def test_t1_rule_check(self):
        """ﮔﭖﻟﺁT+1ﻟ۶ﮒﮔ۲ﮔ?""
        order = {
            "symbol": "000001.SZ",
            "side": "SELL",
            "quantity": 1000,
            "position_date": "2026-04-01",
            "current_date": "2026-04-01"
        }
        
        results = self.engine.check_order(order)
        t1_result = [r for r in results if r.rule_id == "TRADE_001"][0]
        
        assert not t1_result.passed
        assert "T+1ﮒﭘﮒﭦ۵" in t1_result.message
    
    def test_limit_up_rule_check(self):
        """ﮔﭖﻟﺁﮔﭘ۷ﻟﺓﮒﻟ۶ﮒﮔ۲ﮔ?""
        order = {
            "symbol": "000001.SZ",
            "side": "BUY",
            "quantity": 1000,
            "price": 11.00,
            "preclose": 10.00
        }
        
        results = self.engine.check_order(order)
        limit_result = [r for r in results if r.rule_id == "TRADE_002"][0]
        
        assert not limit_result.passed
        assert "ﮔﭘ۷ﮒ" in limit_result.message
    
    def test_fee_calculation(self):
        """ﮔﭖﻟﺁﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟"""
        order = {
            "symbol": "000001.SZ",
            "side": "BUY",
            "quantity": 10000,
            "price": 10.00
        }
        
        fee_result = self.engine.calculate_fees(order)
        
        assert fee_result.commission == max(100000 * 0.0003, 5.0)  # 30ﮒﮔﮔﻛﺛ?ﮒ?
        assert fee_result.stamp_tax == 0  # ﻛﺗﺍﮒ۴ﻛﺕﮔﭘﮒﺍﻟﺎﻝ۷?
        assert fee_result.total_fee > 0
```

### 7.2 ﻠﮔﮔﭖﻟﺁ

1. **ﻛﺕvn.pyﻠﮔﮔﭖﻟﺁ**ﺅﺙﻠ۹ﻟﺁﻟ۶ﮒﮒﺙﮔﮒ۷vn.pyﻠﻠﮒ۷ﻛﺕ­ﻝﮔ­۲ﻝ۰؟ﮔ?
2. **ﮒ۳ﻟ۶ﮒﻝﭨﮒﮔﭖﻟﺁ?*ﺅﺙﮔﭖﻟﺁﮒ۳ﻛﺕ۹ﻟ۶ﮒﮒﮔﭘﻝﮔﻝﮒﭦﮔﺁ
3. **ﮔ۶ﻟﺛﮔﭖﻟﺁ**ﺅﺙﮔﭖﻟﺁﻟ۶ﮒﮔ۲ﮔ۴ﻝﮔ۶ﻟﺛﮒﺛﺎﮒ
4. **ﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁ**ﺅﺙﮔﭖﻟﺁﮒﻝ۶ﻟﺝﺗﻝﮔﮒ?

### 7.3 ﮔﭖﻟﺁﮔﺍﮔ؟

- **ﮔ­۲ﮒﺕﺕﻛﭦ۳ﮔﮒﭦﮔﺁ**ﺅﺙﮔ؟ﻠﻛﺗﺍﮒﻟ؟۱ﮒ?
- **ﻟ۶ﮒﻟﺟﻟ۶ﮒﭦﮔﺁ**ﺅﺙT+1ﻟﺟﻟ۶ﻙﮔﭘ۷ﻟﺓﮒﻟﺟﻟ۶ﻙﻛﭨﻛﺛﻟﭘﻠ?
- **ﻟﺝﺗﻝﮒﭦﮔﺁ**ﺅﺙﮔﻛﺛﻛﺛ۲ﻠﻙﮔﮒ۳۶ﻛﭨﻛﺛﻙﮔﭘ۷ﮒﻛﭨﺓﮔﻛﭦ۳
- **ﮒﺙﮒﺕﺕﮒﭦﮔﺁ**ﺅﺙﮔ ﮔﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﻙﮒﺙﮒﺕﺕﻛﭨﺓﮔ ﺙﻙﻠﭘﮔﺍﻠ

## 8. ﮒ؟ﮔﺛﻟ؟۰ﮒ

### 8.1 ﻠﭘﮔ؟ﭖﮒﮒ

| ﻠﭘﮔ؟ﭖ | ﮔﭘﻠﺑ | ﻝ؟ﮔ  | ﻛﭦ۳ﻛﭨﻝ?|
|------|------|------|--------|
| **ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ** | 3-5ﮒ۳?| ﮒ؟ﮔﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ | ﮔ؛ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﻙﮔ۴ﮒ۲ﮒ؟ﻛﺗﻙﻠﻝﺛ؟ﮔ۷۰ﮔ?|
| **ﮒﺙﮒﻠﭘﮔ؟?* | 10-15ﮒ۳?| ﮒ؟ﻝﺍﮔ ﺕﮒﺟﮒﻟﺛ | ﻟ۶ﮒﮒﺙﮔﻛﭨ۲ﻝ ﻙﻟ۶ﮒﮒ؟ﻝﺍﻝﺎﭨﻙﮒﮒﮔﭖﻟﺁ?|
| **ﮔﭖﻟﺁﻠﭘﮔ؟ﭖ** | 5-7ﮒ۳?| ﮒ؟ﮔﮒ۷ﻠ۱ﮔﭖﻟﺁ | ﮔﭖﻟﺁﻝ۷ﻛﺝﻙﮔ۶ﻟﺛﮔ۴ﮒﻙﻠﮔﮔﭖﻟﺁﻝﭨﮔ?|
| **ﻠﮔﻠﭘﮔ؟ﭖ** | 3-5ﮒ۳?| ﻠﮔﮒﺍﮒ۳ﮒﺙﮔﮔﭘﮔ | ﻠﻠﮒ۷ﻠﮔﻛﭨ۲ﻝ ﻙﻠﻝﺛ؟ﻝ۳ﭦﻛﺝ?|
| **ﻛﺙﮒﻠﭘﮔ؟ﭖ** | 3-5ﮒ۳?| ﮔ۶ﻟﺛﻛﺙﮒﮒﮒﻟﺛﮒ؟ﮒ?| ﻛﺙﮒﻛﭨ۲ﻝ ﻙﮔﮔ۰۲ﮒ؟ﮒﻙﻝ۳ﭦﻛﺝﻝ­ﻝ?|

### 8.2 ﻟﭖﮔﭦﻠﮔﺎ?

1. **ﮒﺙﮒﻟﭖﮔﭦ?*ﺅﺙ?
   - ﮔ ﺕﮒﺟﮒﺙﮒﮒﺓ۴ﻝ۷ﮒﺕﺅﺙ?ﻛﭦﭦﺅﺙ10-15ﮒ۳۸ﺅﺙ
   - ﮔﭖﻟﺁﮒﺓ۴ﻝ۷ﮒﺕﺅﺙ0.5ﻛﭦﭦﺅﺙ5-7ﮒ۳۸ﺅﺙ
   - ﮔﭘﮔﮒﺕﮔﺁﮔﺅﺙ0.2ﻛﭦﭦﺅﺙﻟﺁﮒ؟۰ﮒﮔﮒﺁﺙﺅﺙ

2. **ﮔﮔﺁﻟﭖﮔﭦ?*ﺅﺙ?
   - ﮔﭖﻟﺁﻝﺁﮒ۱ﺅﺙAﻟ۰ﮒﮒﺎﮔﺍﮔ؟ﻙﮔ۷۰ﮔﻛﭦ۳ﮔﻝﺁﮒ۱?
   - ﮒﺙﮒﮒﺓ۴ﮒﺓﺅﺙPython 3.8+ﻙpytestﻙﮔ۶ﻟﺛﮒﮔﮒﺓ۴ﮒﺓ
   - ﮔﮔ۰۲ﮒﺓ۴ﮒﺓﺅﺙMarkdownﻙMermaidﮒﺝﻟ۰۷

### 8.3 ﻠ۲ﻠ۸ﻟﺁﻛﺙﺍﻛﺕﻝﺙﻟ۶?

| ﻠ۲ﻠ۸ | ﮒﺁﻟﺛﮔ?| ﮒﺛﺎﮒ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |
|------|--------|------|----------|
| **ﻟ۶ﮒﮒ۳ﮔﮔ?* | ﻠ،?| ﻛﺕ?| ﮒﻠﭘﮔ؟ﭖﮒ؟ﻝﺍﺅﺙﮒﮔ ﺕﮒﺟﻟ۶ﮒﮒﮔ۸ﮒﺎﻟ۶ﮒ |
| **ﮔ۶ﻟﺛﻠ؟ﻠ۱** | ﻛﺕ?| ﻛﺕ?| ﮒ؟ﻝﺍﻟ۶ﮒﻝﺙﮒ­ﺅﺙﻛﺙﮒﮔ۲ﮔ۴ﻝ؟ﮔﺏ?|
| **ﻠﻝﺛ؟ﮒ۳ﮔﮔ?* | ﻛﺕ?| ﻛﺛ?| ﮔﻛﺝﻟﺁ۵ﻝﭨﻠﻝﺛ؟ﻝ۳ﭦﻛﺝﮒﻠ۹ﻟﺁﮒﺓ۴ﮒ?|
| **ﻠﮔﻠ؟ﻠ۱** | ﻛﺛ?| ﻠ،?| ﻟ؟ﺝﻟ؟۰ﮔﺕﮔﺍﮔ۴ﮒ۲ﺅﺙﮔﻛﺝﻠﮔﻝ۳ﭦﻛﺝ?|
| **ﻝﭨﺑﮔ۳ﮔﮔ؛** | ﻛﺛ?| ﻛﺕ?| ﮔ۷۰ﮒﮒﻟ؟ﺝﻟ؟۰ﺅﺙﻟﺁﮒ۴ﺛﮔﮔ۰۲ |

## 9. ﮒﻝﭨ­ﮔ۸ﮒﺎ

### 9.1 ﻝ­ﮔﮔ۸ﮒﺎﺅﺙ?ﻛﺕ۹ﮔﮒﺅﺙ

1. **ﮔﺑﮒ۳Aﻟ۰ﻟ۶ﮒ?*ﺅﺙﮒ۳۶ﮒ؟ﻛﭦ۳ﮔﻟ۶ﮒﻙﻟﻟﭖﻟﮒﺕﻟ۶ﮒ?
2. **ﮔﺕﺁﻟ۰ﻟ۶ﮒ**ﺅﺙﮔﺕﺁﻟ۰ﮒﺕﮒﭦﻛﭦ۳ﮔﻟ۶ﮒ?
3. **ﻝﺝﻟ۰ﻟ۶ﮒ**ﺅﺙﻝﺝﻟ۰ﮒﺕﮒﭦﻛﭦ۳ﮔﻟ۶ﮒ?
4. **ﻟ۶ﮒﮒﺁﻟ۶ﮒ?*ﺅﺙﻟ۶ﮒﻠﻝﺛ؟ﮒﻝ؟۰ﻝﻝﻠ۱

### 9.2 ﻛﺕ­ﮔﮔ۸ﮒﺎﺅﺙ?ﻛﺕ۹ﮔﮒﺅﺙ

1. **ﻟ۶ﮒﮒ­۵ﻛﺗ **ﺅﺙﮒﭦﻛﭦﮒﮒﺎﮔﺍﮔ؟ﻟ۹ﮒ۷ﻛﺙﮒﻟ۶ﮒﮒﮔ?
2. **ﮔﭦﻟﺛﻟ۶ﮒﮔ۷ﻟ**ﺅﺙﮔ ﺗﮔ؟ﮒﺕﮒﭦﻝﭘﮔﮔ۷ﻟﻠﻝ۷ﻟ۶ﮒ
3. **ﻟ۶ﮒﮒﮔﭖ**ﺅﺙﻟ۶ﮒﮒﺁﺗﻝ­ﻝ۴ﻝﭨ۸ﮔﻝﮒﺛﺎﮒﮒﮔ?
4. **ﮒﮒﺕﮒﺙﻟ۶ﮒﮒﺙﮔ?*ﺅﺙﮔﺁﮔﮒﮒﺕﮒﺙﻟ۶ﮒﮔ۲ﮔ?

### 9.3 ﻠﺟﮔﮔ۸ﮒﺎﺅﺙ?ﮒﺗﺑﮒﺅﺙ?

1. **AIﻟ۶ﮒﻝﮔ**ﺅﺙﻛﺛﺟﻝ۷AIﻝﮔﻛﭦ۳ﮔﻟ۶ﮒ
2. **ﮒ؟ﮔﭘﻟ۶ﮒﻟﺍﮔﺑ**ﺅﺙﮔ ﺗﮔ؟ﮒﺕﮒﭦﮔﺏ۱ﮒ۷ﮒ؟ﮔﭘﻟﺍﮔﺑﻟ۶ﮒ?
3. **ﻟﺓ۷ﮒﺕﮒﭦﻟ۶ﮒ?*ﺅﺙﮔﺁﮔﮒ۳ﮒﺕﮒﭦﻝﭨﻛﺕﻟ۶ﮒﻝ؟۰ﻝ
4. **ﻟ۶ﮒﮒﺕﮒﭦ**ﺅﺙﻝ۷ﮔﺓﮒﺎﻛﭦ،ﮒﻛﭦ۳ﮔﻟ۶ﮒﮔ۷۰ﮔﺟ

## 10. ﮔﮔ۰۲ﻝﭨﺑﮔ۳

### 10.1 ﮔﮔ۰۲ﮔﺕﮒ

1. **ﮔ؛ﻟ؟ﺝﻟ؟۰ﮔﮔ۰?*ﺅﺙﮔﭘﮔﻟ؟ﺝﻟ؟۰ﮒﮔ۴ﮒ۲ﮒ؟ﻛﺗ
2. **APIﮔﮔ۰۲**ﺅﺙﻟ۶ﮒﮒﺙﮔAPIﮒﻟ?
3. **ﻠﻝﺛ؟ﮔﮒ**ﺅﺙﻟ۶ﮒﻠﻝﺛ؟ﻟﺁ۵ﻝﭨﮔﮒ?
4. **ﻠﮔﮔﮒ**ﺅﺙﻛﺕﮒﭘﻛﭨﮔ۷۰ﮒﻠﮔﮔﮒ
5. **ﻝ۷ﮔﺓﮔﮒ**ﺅﺙﮔﻝﭨﻝ۷ﮔﺓﻛﺛﺟﻝ۷ﮔﮒ?
6. **ﮒﺙﮒﮔﮒ?*ﺅﺙﻟ۶ﮒﮒﺙﮒﮔ۸ﮒﺎﮔﮒ?

### 10.2 ﮔﺑﮔﺍﮔﭦﮒﭘ

1. **ﻝﮔ؛ﮔ۶ﮒﭘ**ﺅﺙﻛﺛﺟﻝ۷ﻟﺁ­ﻛﺗﮒﻝﮔ؛ﮔ۶ﮒﭘ
2. **ﮒﮔﺑﮔ۴ﮒﺟ**ﺅﺙﻟ؟ﺍﮒﺛﮔﮔﻟ؟ﺝﻟ؟۰ﮒﮔ?
3. **ﻟﺁﮒ؟۰ﮔﭖﻝ۷**ﺅﺙﻠﮒ۳۶ﮒﮔﺑﻠﻝﭨﮔﭘﮔﻟﺁﮒ؟?
4. **ﮔﮔ۰۲ﮒﮔ­۴**ﺅﺙﻛﭨ۲ﻝ ﮒﮔﺑﮔﭘﮒﮔ­۴ﮔﺑﮔﺍﮔﮔ۰۲

---

**ﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰ﻟ۵ﻝﺗ**ﺅﺙ?
1. ﻟ۶ﮒﮒﻝﺎﭨﻛﺛﻝﺏﭨﮔﺁﮒ۵ﮒ؟ﮔﺑﻟ۵ﻝAﻟ۰ﻠﮔﺎ?
2. ﮔ۴ﮒ۲ﻟ؟ﺝﻟ؟۰ﮔﺁﮒ۵ﮔﺕﮔﺍﮔﻝ۷
3. ﻠﻝﺛ؟ﮔ۷۰ﮔﺟﮔﺁﮒ۵ﻝﭖﮔﺑﭨﻛﺕﻛﺕﮔﮒﭦﻠ?
4. ﮔ۶ﻟﺛﻟ؟ﺝﻟ؟۰ﮔﺁﮒ۵ﻟﺛﮔﭨ۰ﻟﭘﺏﮒ؟ﮔﭘﻛﭦ۳ﮔﻠﮔﺎ?
5. ﻠﮔﮔﺗﮔ۰ﮔﺁﮒ۵ﻛﺕﻝﺍﮔﮔﭘﮔﮒﺙﮒ؟?

**ﻛﺕﻛﺕﮔ­۴ﻟ۰ﮒ?*ﺅﺙ?
1. ﻝﭨﻝﭨﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰ﻛﺙﻟ؟؟
2. ﮔ ﺗﮔ؟ﻟﺁﮒ؟۰ﮔﻟ۶ﻛﺟ؟ﮔﺗﻟ؟ﺝﻟ؟۰
3. ﮒﺙﮒ۶ﮒﺙﮒﻠﭘﮔ؟ﭖﻛﭨﭨﮒ۰ﮒﻟ۶?
4. ﮒﮒﭨﭦﮒﺙﮒﻝﺁﮒ۱ﮒﮔﮔﺁﮔ ﮒﮒ۳