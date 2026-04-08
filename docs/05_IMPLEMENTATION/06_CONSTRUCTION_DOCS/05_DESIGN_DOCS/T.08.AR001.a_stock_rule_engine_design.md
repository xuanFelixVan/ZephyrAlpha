---
module_id: DESIGN_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: '2026-04-07'
owner: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
- 系统实施与部署管理与优化维护
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲
applicable_scope: ﮔ۷۰ﮔﻛﭦ۳ﮔﻝﺏﭨﻝﭨ
compliance_level: ﮔﭘﮔﮔﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?
# Aﻟ۰ﻟ۶ﮒﮒﺙﮔﻟ؟ﺝﻟ؟۰ﮔﮔ۰?

## 核心定位

提供A股规则引擎的详细设计，包含规则定义、规则执行、规则管理等，支持A股交易规则实现。


> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - Aﻟ۰ﻟ۶ﮒﮒﺙﮔﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟?
> **ﻝﺑ۱ﮒﺙ**: `DESIGN_A_STOCK_RULES_001`
> **ﻟ؟ﺝﻟ؟۰ﮔﭘﻠﺑ**: 3-5ﮒ۳?
> **ﮔﺕﮒﺟﮒ؟ﻛﺛ**: ﻝﭨﻛﺕﻝ؟۰ﻝAﻟ۰ﮒﺕﮒﭦﻛﭦ۳ﮔﻟ۶ﮒﺅﺙﻝ۰؟ﻛﺟﮔ۷۰ﮔﻛﭦ۳ﮔﻝ؛۵ﮒﻝﮒ؟ﮒﺕﮒﭦﻟ۶ﮒ


## 设计目标

### 主要目标

1. **功能完整性**: 确保文档内容完整，满足使用需求
2. **易用性**: 提高文档可读性，便于快速理解
3. **可维护性**: 文档结构清晰，便于后续维护
4. **一致性**: 确保文档格式和风格统一

### 质量目标

- 文档完整性: 100%
- 格式规范性: 100%
- 内容准确性: 100%


## 1. ﻟ؟ﺝﻟ؟۰ﮒﮒ

| ﮒﮒ | ﻟﺁﺑﮔ | ﮒ؟ﻝﺍﮔﺗﮒﺙ |
|
------|------|----------|
| **ﻟ۶ﮒﮒﺏﻠﻝﺛ?* | ﮔﮔﻟ۶ﮒﻛﭨ۴YAMLﻠﻝﺛ؟ﮒ؟ﻛﺗﺅﺙﻛﺕﮒﮔﭨﻛﭨ۲ﻝ | ﻟ۶ﮒﻠﻝﺛ؟ﮔﻛﭨﭘ + ﮒ۷ﮔﮒﻟﺛ?|
| **ﮔ۷۰ﮒﮒﻟ؟ﺝﻟ؟?* | ﻛﺕﮒﻟ۶ﮒﻝﺎﭨﮒﻝ؛ﻝ،ﮔ۷۰ﮒﺅﺙﻛﺝﺟﻛﭦﻝﭨﺑﮔ۳ﮔ۸ﮒﺎ?| ﻟ۶ﮒﮒﻝﺎﭨﻛﺛﻝﺏﭨ + ﮔﻛﭨﭘﮔﭦﮒﭘ |
| **ﻠ،ﮔ۶ﻟﺛﮔ۲ﮔ?* | ﻟ۶ﮒﮔ۲ﮔ۴ﻠﻠ،ﮔ۶ﻟﺛﺅﺙﻛﺕﮒﺛﺎﮒﻛﭦ۳ﮔﮔ۶ﻟ۰ | ﻟ۶ﮒﻝﺙﮒ + ﮒﺗﭘﻟ۰ﮔ۲ﮔ?|
| **ﮒ؟ﮔﺑﻟ۵ﻝ** | ﻟ۵ﻝAﻟ۰ﮔﮔﮔﺕﮒﺟﻛﭦ۳ﮔﻟ۶ﮒ?| T+1ﻙﮔﭘ۷ﻟﺓﮒﻙSTﻙﻟﺑﺗﻝ۷ﻙﻠ۲ﻠ?|
| **ﻝﺎﺝﻝ۰؟ﮔ۷۰ﮔ** | ﻟ۶ﮒﮔ۶ﻟ۰ﻝﭨﮔﻛﺕﻝﮒ؟ﮒﺕﮒﭦﻛﺕﻟ?| ﮒﭦﻛﭦﻝﮒ؟ﻛﭦ۳ﮔﻟ۶ﮒﻠ۹ﻟﺁ |

## 2. ﻟ۶ﮒﮒﻝﺎﭨﻛﺛﻝﺏﭨ

### 2.1 ﻛﭦ۳ﮔﻟ۶ﮒﻝﺎﭨﺅﺙTrade Rulesﺅﺙ?
- **T+1ﻟ۶ﮒ**ﺅﺙﮒﺛﮔ۴ﻛﺗﺍﮒ۴ﮔ؛۰ﮔ۴ﮒﺁﮒﮒﭦ
- **ﮔﭘ۷ﻟﺓﮒﻟ۶ﮒ?*ﺅﺙﻛﺕﭨﮔ?0%ﻙﮒﻛﺕﮔﺟ/ﻝ۶ﮒﮔ?0%ﻙSTﻟ?%
- **STﻟ۰ﻝ۴۷ﻟ۶ﮒ**ﺅﺙﻝﺗﮔ؟ﻛﭦ۳ﮔﻠﮒ?
- **ﮔﺍﻟ۰ﻟ۶ﮒ**ﺅﺙﻠ۵ﮔ۴ﮔﭘ۷ﻟﺓﮒﺗﻠﮒﭘﻙﻛﺕﺑﮔﭘﮒﻝ?
- **ﮒ۳۶ﮒ؟ﻛﭦ۳ﮔﻟ۶ﮒ**ﺅﺙﮒ۳۶ﮒ؟ﻛﭦ۳ﮔﻠﮒ?

### 2.2 ﻟﺑﺗﻝ۷ﻟ۶ﮒﻝﺎﭨﺅﺙFee Rulesﺅﺙ?
- **ﻛﺛ۲ﻠﻟ۶ﮒ**ﺅﺙﻛﺕﻛﺕﺅﺙﮔﻛﺛ?ﮒﺅﺙﮒﮒﮔﭘﮒ
- **ﮒﺍﻟﺎﻝ۷ﻟ۶ﮒ?*ﺅﺙﮒﻛﺕﺅﺙﮒﮒﭦﮔﭘﮒﮒﮔﭘﮒ
- **ﻟﺟﮔﺓﻟﺑﺗﻟ۶ﮒ?*ﺅﺙﻛﺕ0.1ﺅﺙﮔﺎ۹ﮔﺓﺎﮒﺓ؟ﮒﺙﺅﺙﮒﮒﮔﭘﮒ
- **ﻟ۶ﻟﺑﺗﻟ۶ﮒ**ﺅﺙﻛﺕ0.2ﺅﺙﮒﮒﮔﭘﮒ?
- **ﮔﭨﻝﺗﮔ۷۰ﮒ**ﺅﺙﮒﭦﻛﭦﮔﭖﮒ۷ﮔ۶ﻝﮒ۷ﮔﮔﭨﻝﺗﻟ؟۰ﻝ؟?

### 2.3 ﻠ۲ﻠ۸ﻟ۶ﮒﻝﺎﭨﺅﺙRisk Rulesﺅﺙ?
- **ﮒﻟ۰ﻛﭨﻛﺛﻠﮒﭘ**ﺅﺙﮒﻝ۴۷ﮔﮒ۳۶ﻛﭨﻛﺛﮔﺁﻛﺝ?
- **ﮔﭨﻛﭨﻛﺛﻠﮒ?*ﺅﺙﮔﭨﮔﻛﭨﮒﺕﮒﺙﻠﮒ?
- **ﮔ۴ﮔ۱ﮔﻝﻠﮒﭘ**ﺅﺙﮒﺛﮔ۴ﮔﮒ۳۶ﮔ۱ﮔﻝ
- **ﻠﭨﮒﮒﻠﮒ?*ﺅﺙﻝ۵ﮔ۱ﻛﭦ۳ﮔﻝﻟ۰ﻝ۴۷ﮒﻟ۰۷
- **ﮔﭖﮒ۷ﮔ۶ﻠﮒ?*ﺅﺙﮔﮒﺍﮔﻛﭦ۳ﻠﻟ۵ﮔﺎ

### 2.4 ﮒﺕﮒﭦﻟ۶ﮒﻝﺎﭨﺅﺙMarket Rulesﺅﺙ?
- **ﻛﭦ۳ﮔﮔﭘﻠﺑﻟ۶ﮒ**ﺅﺙﮒﺙﻝﻙﮔﭘﻝﻙﮒﻠﺑﻛﺙﮒﺕ?
- **ﻠﮒﻝ،ﻛﭨﺓﻟ۶ﮒ**ﺅﺙﮒﺙﻝ?ﮔﭘﻝﻠﮒﻝ،ﻛﭨﺓﮔﭦﮒﭘ
- **ﻟﺟﻝﭨﻝ،ﻛﭨﺓﻟ۶ﮒ**ﺅﺙﻛﭨﺓﮔﺙﻛﺙﮒﻙﮔﭘﻠﺑﻛﺙﮒ?
- **ﻛﺕﺑﮔﭘﮒﻝﻟ۶ﮒ**ﺅﺙﮔﭘ۷ﻟﺓﮒﻟ۶۵ﮒﻝﻛﺕﺑﮔﭘﮒﻝ?

## 3. ﮔﭘﮔﻟ؟ﺝﻟ؟۰

### 3.1 ﻝﺎﭨﮒﺝﻟ؟ﺝﻟ؟۰

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
    
    AStockRuleEngine --> BaseRule : ﮒﮒ،
    BaseRule <|-- T1Rule : ﻝﭨ۶ﮔﺟ
    BaseRule <|-- LimitUpDownRule : ﻝﭨ۶ﮔﺟ
    BaseRule <|-- TradingFeeRule : ﻝﭨ۶ﮔﺟ
    BaseRule <|-- RiskRule : ﻝﭨ۶ﮔﺟ
    
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

### 3.2 ﮔﺕﮒﺟﮔ۴ﮒ۲ﮒ؟ﻛﺗ

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class RuleCategory(str, Enum):
    """ﻟ۶ﮒﮒﻝﺎﭨ"""
    TRADE = "trade"      # ﻛﭦ۳ﮔﻟ۶ﮒ
    FEE = "fee"          # ﻟﺑﺗﻝ۷ﻟ۶ﮒ
    RISK = "risk"        # ﻠ۲ﻠ۸ﻟ۶ﮒ
    MARKET = "market"    # ﮒﺕﮒﭦﻟ۶ﮒ


class RuleSeverity(str, Enum):
    """ﻟ۶ﮒﻛﺕ۴ﻠﻝ۷ﮒﭦ۵"""
    INFO = "info"        # ﻛﺟ۰ﮔﺁ
WARNING = "warning"  # ﻟ۵ﮒ
    ERROR = "error"      # ﻠﻟﺁﺁ
    CRITICAL = "critical" # ﻛﺕ۴ﻠ


@dataclass
class RuleResult:
    """ﻟ۶ﮒﮔ۲ﮔ۴ﻝﭨﮔ?""
    passed: bool                    # ﮔﺁﮒ۵ﻠﻟﺟ
    rule_id: str                    # ﻟ۶ﮒID
    rule_name: str                  # ﻟ۶ﮒﮒﻝ۶ﺍ
    category: RuleCategory          # ﻟ۶ﮒﮒﻝﺎﭨ
    severity: RuleSeverity          # ﻛﺕ۴ﻠﻝ۷ﮒﭦ۵
    message: str                    # ﮔ۲ﮔ۴ﻝﭨﮔﮔﭘﮔ?
    details: Dict[str, Any] = None  # ﻟﺁ۵ﻝﭨﻝﭨﮔ
    actions: List[str] = None       # ﮒﭨﭦﻟ؟؟ﮒ۷ﻛﺛ


@dataclass
class FeeResult:
    """ﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟ﻝﭨﮔ"""
    commission: float = 0.0          # ﻛﺛ۲ﻠ
    stamp_tax: float = 0.0           # ﮒﺍﻟﺎﻝ۷?
    transfer_fee: float = 0.0        # ﻟﺟﮔﺓﻟﺑ?
    misc_fee: float = 0.0            # ﮒﭘﻛﭨﻟﺑﺗﻝ۷
    total_fee: float = 0.0           # ﮔﭨﻟﺑﺗﻝ?
    breakdown: Dict[str, float] = None  # ﻟﺑﺗﻝ۷ﮔﻝﭨ


class BaseRule(ABC):
    """ﻟ۶ﮒﮒﭦﻝﺎﭨ"""
    
    def __init__(self, rule_id: str, rule_name: str, category: RuleCategory, 
                 enabled: bool = True, config: Dict[str, Any] = None):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.category = category
        self.enabled = enabled
        self.config = config or {}
    
    @abstractmethod
    def check(self, context: Dict[str, Any]) -> RuleResult:
        """ﮔ۲ﮔ۴ﻟ۶ﮒ?
        
        ﮒﮔﺍ:
context: ﮔ۲ﮔ۴ﻛﺕﻛﺕﮔﺅﺙﮒﮒ،ﻟ؟۱ﮒﻙﮔﻛﭨﻙﮒﺕﮒﭦﮔﺍﮔ؟ﻝ
            
        ﻟﺟﮒ:
            RuleResult: ﻟ۶ﮒﮔ۲ﮔ۴ﻝﭨﮔ?
        """
        pass
    
    def get_description(self) -> str:
        """ﻟﺓﮒﻟ۶ﮒﮔﻟﺟﺍ"""
        return f"{self.rule_name} ({self.rule_id})"
    
    def enable(self):
        """ﮒﺁﻝ۷ﻟ۶ﮒ"""
        self.enabled = True
    
    def disable(self):
        """ﻝ۵ﻝ۷ﻟ۶ﮒ"""
        self.enabled = False


class AStockRuleEngine:
    """Aﻟ۰ﻟ۶ﮒﮒﺙﮔ?""
    
    def __init__(self, config_path: str = None):
        self.rule_registry: Dict[str, BaseRule] = {}
        self.rule_configs: List[Dict] = []
        
        if config_path:
            self.load_config(config_path)
            self._initialize_rules()
    
    def register_rule(self, rule: BaseRule):
        """ﮔﺏ۷ﮒﻟ۶ﮒ"""
        self.rule_registry[rule.rule_id] = rule
    
    def check_order(self, order: Dict[str, Any], context: Dict[str, Any] = None) -> List[RuleResult]:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﮒﻟ۶ﮔ?
        
        ﮒﮔﺍ:
            order: ﻟ؟۱ﮒﮔﺍﮔ؟
context: ﻠ۱ﮒ۳ﻛﺕﻛﺕﮔﺅﺙﮔﻛﭨﻙﻟﺑ۵ﮔﺓﻙﮒﺕﮒﭦﮔﺍﮔ؟ﻝﺅﺙ?
            
        ﻟﺟﮒ:
            List[RuleResult]: ﮔﮔﻟ۶ﮒﮔ۲ﮔ۴ﻝﭨﮔ?
        """
        results = []
        check_context = {"order": order}
        if context:
            check_context.update(context)
        
        for rule in self.rule_registry.values():
            if not rule.enabled:
                continue
            
            # ﮒ۹ﮔ۲ﮔ۴ﻛﺕﻟ؟۱ﮒﻝﺕﮒﺏﻝﻟ۶ﮒ?
            if rule.category in [RuleCategory.TRADE, RuleCategory.FEE, RuleCategory.RISK]:
                result = rule.check(check_context)
                results.append(result)
        
        return results
    
    def calculate_fees(self, order: Dict[str, Any], market_data: Dict[str, Any] = None) -> FeeResult:
        """ﻟ؟۰ﻝ؟ﻛﭦ۳ﮔﻟﺑﺗﻝ۷
        
        ﮒﮔﺍ:
            order: ﻟ؟۱ﮒﮔﺍﮔ؟
market_data: ﮒﺕﮒﭦﮔﺍﮔ؟ﺅﺙﻝ۷ﻛﭦﮔﭨﻝﺗﻟ؟۰ﻝ؟ﻝﺅﺙ?
            
        ﻟﺟﮒ:
            FeeResult: ﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟ﻝﭨﮔ
        """
        # ﻟﺓﮒﻟﺑﺗﻝ۷ﻟ۶ﮒ
        fee_rules = [r for r in self.rule_registry.values() 
                    if r.category == RuleCategory.FEE and r.enabled]
        
        # ﻠﭨﻟ؟۳ﻟﺑﺗﻝ۷ﻝﭨﮔ
        fee_result = FeeResult()
        
        # ﮒﭦﻝ۷ﮔﮔﻟﺑﺗﻝ۷ﻟ۶ﮒ?
        for rule in fee_rules:
            if hasattr(rule, 'calculate_fees'):
                rule_fee_result = rule.calculate_fees(order, market_data)
                # ﮒﮒﺗﭘﻟﺑﺗﻝ۷ﻝﭨﮔ
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
"""ﮒﻟﺛﺛﻟ۶ﮒﻠﻝﺛ؟"""
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            self.rule_configs = yaml.safe_load(f)
    
    def _initialize_rules(self):
"""ﮔﺗﮔ؟ﻠﻝﺛ؟ﮒﮒ۶ﮒﻟ۶ﮒ?""
# ﻟﺟﻠﻛﺙﮔﺗﮔ؟ﻠﻝﺛ؟ﮒﮒﭨﭦﮒﺓﻛﺛﻝﻟ۶ﮒﮒ؟ﻛﺝ
# ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕﻛﺙﻛﺛﺟﻝ۷ﮒﺓ۴ﮒﮔ۷۰ﮒﺙ
        pass
```

## 4. ﻝﺍﮔﻛﭨ۲ﻝﮔﺑﮒﮔﺗﮔ۰

### 4.1 ﮒﺓﺎﮔﻛﭨ۲ﻝﮔ۷۰ﮒ

#### 4.1.1 T+1ﻛﭦ۳ﮔﻝﺏﭨﻝﭨﺅﺙﮔ۴ﻟ?technical_documentation.mdﺅﺙ?
```python
class T1TradingSystem:
    """T+1ﻛﭦ۳ﮔﮒﭘﮒﭦ۵ﻠﮒ"""
    T1_RULES = {
        'ﮒﺛﮔ۴ﻛﺗﺍﮒ۴ﻠﮒ؟': True,
        'ﮔ؛۰ﮔ۴ﻟ۶۲ﻠ۳ﻠﮒﭘ': True,
        'ﻠﻝ۷ﻟﮒﺑ': 'Aﻟ۰ﮒﺕﮒﭦﮔﮔﮒﻝ۶?,
        'ﻛﺝﮒ۳ﮔﮒﭖ': ['ETFﮒﭦﻠ', 'ﮒﺁﻟﺛ؛ﮒ?, 'ﮔﮔ']
    }
    
    def check_sell_permission(self, position, buy_date, current_date):
        """ﮔ۲ﮔ۴ﮒﮒﭦﮔﻠ?""
        if buy_date == current_date:
            return {
                'can_sell': False,
                'reason': 'T+1ﮒﭘﮒﭦ۵ﺅﺙﮒﺛﮔ۴ﻛﺗﺍﮒ۴ﻛﺕﻟﺛﮒﮒ?,
                'available_date': self.next_trading_day(buy_date)
            }
        return {'can_sell': True}
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﻠﮔﻛﺕ?`T1Rule` ﻝﺎﭨﺅﺙﻝﭨ۶ﮔﺟ `BaseRule`
- ﻛﺟﻝﮔﺕﮒﺟﻝ؟ﮔﺏﺅﺙﻠﻠﻝﭨﻛﺕﮔ۴ﮒ۲
- ﮔﺓﭨﮒﻠﻝﺛ؟ﮔﺁﮔﺅﺙﮔﺁﮔﻛﺝﮒ۳ﮒﻝ۶ﻠﻝﺛ?

#### 4.1.2 ﮔﭘ۷ﻟﺓﮒﮔﺟﻝﺏﭨﻝﭨﺅﺙﮔ۴ﻟ?technical_documentation.mdﺅﺙ?
```python
class LimitUpDownSystem:
    """ﮔﭘ۷ﻟﺓﮒﮔﺟﮒﭘﮒﭦ۵ﻠﮒ"""
    LIMIT_RULES = {
        'ﻛﺕﭨﮔﺟﺅﺙﮔﺎ۹ﮒﺕ?0/ﮔﺓﺎﮒﺕ000ﺅﺙ?: {
            'ﮔﭘ۷ﻟﺓﮒﮒﺗﮒﭦ?: 0.10,
            'STﻟ۰ﻝ۴۷ﮒﺗﮒﭦ۵': 0.05,
            'ﻠ۵ﮔ۴ﻛﺕﮒﺕﮒﺗﮒﭦ۵': 0.44
        },
        'ﮒﻛﺕﮔﺟﺅﺙ300ﺅﺙ?: {
            'ﮔﭘ۷ﻟﺓﮒﮒﺗﮒﭦ?: 0.20,
            'STﻟ۰ﻝ۴۷ﮒﺗﮒﭦ۵': 0.20,
            'ﻠ۵ﮔ۴ﻛﺕﮒﺕﮒﺗﮒﭦ۵': 0.44
        },
        'ﻝ۶ﮒﮔﺟﺅﺙ688ﺅﺙ?: {
            'ﮔﭘ۷ﻟﺓﮒﮒﺗﮒﭦ?: 0.20,
            'STﻟ۰ﻝ۴۷ﮒﺗﮒﭦ۵': 0.20,
'ﻠ۵ﮔ۴ﻛﺕﮒﺕﮒﺗﮒﭦ۵':ﮔﮔﭘ۷ﻟﺓﮒ
        }
    }
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﻠﮔﻛﺕ?`LimitUpDownRule` ﻝﺎ?
- ﮔ۸ﮒﺎﻟ۶ﮒﻠﻝﺛ؟ﺅﺙﮔﺁﮔﮔﺑﮒ۳ﮔﺟﻝﺎﭨﮒ
- ﮔﺓﭨﮒﻛﭨﺓﮔﺙﮔ۲ﮔ۴ﻙﮔﭘ۷ﻟﺓﮒﮒ۳ﮔﮔﺗﮔﺏ

#### 4.1.3 ﻛﭦ۳ﮔﻟﺑﺗﻝ۷ﮒﺕﺕﻠﺅﺙﮔ۴ﻟ?technical_documentation.mdﺅﺙ?
```python
TRADING_FEES = {
    'ﻛﺛ۲ﻠ': {'rate': 0.0003, 'min': 5, 'ﮒﮒ': True},
    'ﮒﺍﻟﺎﻝ۷?: {'rate': 0.001, 'min': 0, 'ﮒﮒ': 'sell'},
    'ﻟﺟﮔﺓﻟﺑ?: {'rate': 0.00001, 'min': 1, 'ﮒﮒ': True, 'market': 'SH'},
    'ﻟ۶ﻟﺑﺗ': {'rate': 0.00002, 'min': 0, 'ﮒﮒ': True}
}
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﻠﮔﻛﺕ?`TradingFeeRule` ﻝﺎ?
- ﮒ؟ﻝﺍﻝﺎﺝﻝ۰؟ﻝﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟ﻝ؟ﮔﺏ?
- ﮔﺁﮔﮔﺎ۹ﮔﺓﺎﮒﺕﮒﭦﮒﺓ؟ﮒﺙ
- ﮔﺓﭨﮒﮔﻛﺛﻟﺑﺗﻝ۷ﻙﻠﭘﮔ۱ﺁﻟﺑﺗﻝﮔﺁﮔ?

#### 4.1.4 ﻠ۲ﮔ۶ﻟ۶ﮒﮒﺙﮔﺅﺙﮔ۴ﻟ?RISK_RULE_ENGINE.mdﺅﺙ?
```python
class RiskRule:
    """ﻠ۲ﮔ۶ﻟ۶ﮒ"""
    def __init__(self, rule_id, name, category, severity, condition, action, enabled=True):
        self.rule_id = rule_id
        self.name = name
        self.category = category
        self.severity = severity
        self.condition = condition
        self.action = action
        self.enabled = enabled
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﻠﻝ۷ﻝﺍﮔ `RiskRule` ﻝﺎﭨﻟ؟ﺝﻟ؟?
- ﻠﻠﮒﺍﻝﭨﻛﺕﻟ۶ﮒﮔ۴ﮒ۲
- ﮔ۸ﮒﺎﻛﺕﭦAﻟ۰ﻝﺗﮒ؟ﻠ۲ﻠ۸ﻟ۶ﮒ?

#### 4.1.5 ﮔﭘ۷ﮒﮔﺟﮒﮔﺅﺙﮔ۴ﻟ۹ limit-up-analysis.mdﺅﺙ?
```python
class LimitUpAnalyzer:
    """ﮔﭘ۷ﮒﮔﺟﮒﮔ?""
    def is_limit_up(self, stock_data, limit_rate=0.10):
"""ﮒ۳ﮔﮔﺁﮒ۵ﮔﭘ۷ﮒ"""
        change_pct = stock_data['change_pct']
        return abs(change_pct - limit_rate * 100) < 0.1
```

**ﮔﺑﮒﮔﺗﮔ۰**ﺅﺙ?
- ﮔﺑﮒﮒ?`LimitUpDownRule` ﻛﺕﻛﺛﻛﺕﭦﻟﺝﮒ۸ﮔﺗﮔﺏ?
- ﻝ۷ﻛﭦﮒﺕﮒﭦﮔﺍﮔ؟ﮒﮔﮒﻟ۶ﮒﻠ۹ﻟﺁ?

### 4.2 ﻛﭨ۲ﻝﻟﺟﻝ۶ﭨﻟ؟۰ﮒ

1. **ﻝ؛؛ﻛﺕﻠﭘﮔ؟ﭖﺅﺙ?-2ﮒ۳۸ﺅﺙ**ﺅﺙﮒﮒﭨﭦﮒﭦﻝ۰ﮔ۰ﮔﭘ
- ﮒ؟ﻝﺍ `BaseRule`ﻙ`RuleResult`ﻙ`FeeResult` ﻝﮒﭦﻝ۰ﻝﺎ?
- ﮒ؟ﻝﺍ `AStockRuleEngine` ﮔﺕﮒﺟﮒﺙﮔ

2. **ﻝ؛؛ﻛﭦﻠﭘﮔ؟ﭖﺅﺙ?-3ﮒ۳۸ﺅﺙ**ﺅﺙﻟﺟﻝ۶ﭨﻝﺍﮔﻟ۶ﮒ?
   - ﻟﺟﻝ۶ﭨ T+1 ﻟ۶ﮒﻛﺕ?`T1Rule`
   - ﻟﺟﻝ۶ﭨﮔﭘ۷ﻟﺓﮒﻟ۶ﮒﻛﺕﭦ `LimitUpDownRule`
   - ﻟﺟﻝ۶ﭨﻟﺑﺗﻝ۷ﻟ۶ﮒﻛﺕ?`TradingFeeRule`

3. **ﻝ؛؛ﻛﺕﻠﭘﮔ؟ﭖﺅﺙ?-2ﮒ۳۸ﺅﺙ**ﺅﺙﮔ۸ﮒﺎﮒﻟ?
- ﮔﺓﭨﮒSTﻟ۰ﻝ۴۷ﻟ۶ﮒ
- ﮔﺓﭨﮒﮔﺍﻟ۰ﻟ۶ﮒ
- ﮔﺓﭨﮒﻠ۲ﻠ۸ﻟ۶ﮒﻠﮔ

## 5. ﻟ۶ﮒﻠﻝﺛ؟ﮔ۷۰ﮔﺟ

### 5.1 YAMLﻠﻝﺛ؟ﻝﭨﮔ

```yaml
# config/rules/a_stock_rules.yaml
version: "1.0"
engine: "AStockRuleEngine"
last_updated: "2026-04-02"

rules:
  # ============ ﻛﭦ۳ﮔﻟ۶ﮒ ============
  - rule_id: "TRADE_001"
    rule_name: "T+1ﻛﭦ۳ﮔﻟ۶ﮒ"
    category: "trade"
    enabled: true
    severity: "error"
    class: "T1Rule"
    config:
      lock_days: 1
      exceptions: ["ETF", "ﮒﺁﻟﺛ؛ﮒ?, "ﮔﮔ"]
      check_method: "check_sell_permission"
  
  - rule_id: "TRADE_002"
    rule_name: "ﮔﭘ۷ﻟﺓﮒﻟ۶ﮒ?
    category: "trade"
    enabled: true
    severity: "error"
    class: "LimitUpDownRule"
    config:
      limit_rates:
        "ﻛﺕﭨﮔﺟ":
          normal: 0.10
          st: 0.05
          first_day: 0.44
        "ﮒﻛﺕﮔ?:
          normal: 0.20
          st: 0.20
          first_day: 0.44
        "ﻝ۶ﮒﮔ?:
          normal: 0.20
          st: 0.20
first_day: null  # ﮔﮔﭘ۷ﻟﺓﮒ
precision: 0.01  # ﻛﭨﺓﮔﺙﻝﺎﺝﮒﭦ۵
  
  - rule_id: "TRADE_003"
    rule_name: "STﻟ۰ﻝ۴۷ﻟ۶ﮒ"
    category: "trade"
    enabled: true
    severity: "warning"
    class: "STRule"
    config:
      st_prefixes: ["*ST", "ST"]
      warning_days: 30
delisting_threshold: 3  # ﻟﺟﻝﭨ3ﮒﺗﺑﻛﭦﮔ?
  
  # ============ ﻟﺑﺗﻝ۷ﻟ۶ﮒ ============
  - rule_id: "FEE_001"
    rule_name: "ﻛﺛ۲ﻠﻟ۶ﮒ"
    category: "fee"
    enabled: true
    severity: "info"
    class: "CommissionRule"
    config:
      rate: 0.0003  # ﻛﺕﻛﺕ
      min_amount: 5.0
      both_sides: true
      calculate_method: "percentage_with_min"
  
  - rule_id: "FEE_002"
    rule_name: "ﮒﺍﻟﺎﻝ۷ﻟ۶ﮒ?
    category: "fee"
    enabled: true
    severity: "info"
    class: "StampTaxRule"
    config:
      rate: 0.001  # ﮒﻛﺕ
      apply_on: "sell"  # ﮒﮒﭦﮔﭘﮔﭘﮒ?
      exempt_categories: ["ETF", "ﮒﺛﮒ?]
  
  - rule_id: "FEE_003"
    rule_name: "ﻟﺟﮔﺓﻟﺑﺗﻟ۶ﮒ?
    category: "fee"
    enabled: true
    severity: "info"
    class: "TransferFeeRule"
    config:
      sh_rate: 0.00001  # ﮔﺎ۹ﮒﺕﻛﺕ?.1
      sz_rate: 0.00002  # ﮔﺓﺎﮒﺕﻛﺕ?.2
      min_amount: 1.0
      both_sides: true
  
  - rule_id: "FEE_004"
    rule_name: "ﮔﭨﻝﺗﮔ۷۰ﮒ"
    category: "fee"
    enabled: true
    severity: "info"
    class: "SlippageRule"
    config:
      base_rate: 0.0002  # ﮒﭦﻝ۰ﮔﭨﻝﺗﻝ?.02%
      liquidity_factor: true
      volatility_factor: true
      market_cap_weight: true
  
  # ============ ﻠ۲ﻠ۸ﻟ۶ﮒ ============
  - rule_id: "RISK_001"
    rule_name: "ﮒﻟ۰ﻛﭨﻛﺛﻠﮒﭘ"
    category: "risk"
    enabled: true
    severity: "error"
    class: "PositionLimitRule"
    config:
      max_position_ratio: 0.10  # ﮒﻟ۰ﮔﮒ۳?0%
      max_position_value: 1000000  # ﮒﻟ۰ﮔﮒ۳?00ﻛﺕ?
      apply_to: ["Aﻟ?, "ﮔﺕﺁﻟ۰"]
  
  - rule_id: "RISK_002"
    rule_name: "ﮔﭨﻛﭨﻛﺛﻠﮒ?
    category: "risk"
    enabled: true
    severity: "error"
    class: "TotalPositionRule"
    config:
      max_total_ratio: 0.80  # ﮔﭨﻛﭨﻛﺛﮔﮒ۳?0%
      cash_reserve_ratio: 0.05  # ﻝﺍﻠﮒ۷ﮒ۳5%
  
  - rule_id: "RISK_003"
    rule_name: "ﮔ۴ﮔ۱ﮔﻝﻠﮒﭘ"
    category: "risk"
    enabled: true
    severity: "warning"
    class: "TurnoverLimitRule"
    config:
      max_daily_turnover: 0.30  # ﮔ۴ﮔ۱ﮔﻝﻛﺕﻟﭘﻟﺟ?0%
      calculation_period: "daily"
  
  # ============ ﮒﺕﮒﭦﻟ۶ﮒ ============
  - rule_id: "MARKET_001"
    rule_name: "ﻛﭦ۳ﮔﮔﭘﻠﺑﻟ۶ﮒ"
    category: "market"
    enabled: true
    severity: "error"
    class: "TradingHoursRule"
    config:
      market_hours:
        "Aﻟ?:
          morning_open: "09:30"
          morning_close: "11:30"
          afternoon_open: "13:00"
          afternoon_close: "15:00"
        "ﮔﺕﺁﻟ۰":
          morning_open: "09:30"
          morning_close: "12:00"
          afternoon_open: "13:00"
          afternoon_close: "16:00"
      holidays: "config/holidays.yaml"
  
  - rule_id: "MARKET_002"
    rule_name: "ﻠﮒﻝ،ﻛﭨﺓﻟ۶ﮒ"
    category: "market"
    enabled: true
    severity: "info"
    class: "AuctionRule"
    config:
      auction_periods:
        "ﮒﺙﻝﻝ،ﻛﭨ?: "09:15-09:25"
        "ﮔﭘﻝﻝ،ﻛﭨﺓ": "14:57-15:00"
      price_discovery: "volume_weighted"
      match_method: "price_time_priority"
```

### 5.2 ﻠﻝﺛ؟ﻟﺁﺑﮔ

1. **ﻟ۶ﮒIDﮒﺛﮒﻟ۶ﻟ**ﺅﺙ`{ﻝﺎﭨﮒ،}_{ﮒﭦﮒﺓ}`ﺅﺙﮒ۵ `TRADE_001`
2. **ﻝﺎﭨﮒ،ﮔﻛﺕﺝ**ﺅﺙ`trade`ﻙ`fee`ﻙ`risk`ﻙ`market`
3. **ﻛﺕ۴ﻠﻝ۷ﮒﭦ۵**ﺅﺙ`info`ﻙ`warning`ﻙ`error`ﻙ`critical`
4. **ﻝﺎﭨﮒﮒﺙﻝ۷**ﺅﺙﻟ۶ﮒﮒ؟ﻝﺍﻝﺎﭨﻝﮒ۷ﻟﺓﺁﮒﺝﮒ?
5. **ﻠﻝﺛ؟ﮒﮔﺍ**ﺅﺙﮔﺁﻛﺕ۹ﻟ۶ﮒﻝﺗﮔﻝﻠﻝﺛ؟ﮒﮔﺍ

## 6. ﻠﮔﮒﺍﮒ۳ﮒﺙﮔﮔﭘﮔ

### 6.1 ﻛﺕﮒﺙﮔﻠﻠﮒ۷ﻝﻠﮔ

```python
class VnPySimulationAdapter(BaseEngineAdapter):
    """vn.pyﮔ۷۰ﮔﻛﭦ۳ﮔﻠﻠﮒ?""
    
    def __init__(self, config: VnPyConfig):
        super().__init__(config)
        # ﮒﮒ۶ﮒAﻟ۰ﻟ۶ﮒﮒﺙﮔ?
        self.rule_engine = AStockRuleEngine("config/rules/a_stock_rules.yaml")
    
    def submit_order(self, order: UnifiedOrder) -> Result:
        """ﮔﻛﭦ۳ﻟ؟۱ﮒ"""
        # 1. ﻟ۶ﮒﮔ۲ﮔ?
        rule_results = self.rule_engine.check_order(order.to_dict())
        
        # 2. ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮔﻠﻟﺁﺁﻝﭦ۶ﮒ،ﻝﻟ۶ﮒﻟﺟﻟ۶?
        critical_errors = [r for r in rule_results 
                          if r.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL] 
                          and not r.passed]
        
        if critical_errors:
            error_msg = "; ".join([f"{r.rule_name}: {r.message}" for r in critical_errors])
            return Result.error(f"ﻟ؟۱ﮒﻟﺟﮒﻟ۶ﮒ: {error_msg}")
        
        # 3. ﻟ؟۰ﻝ؟ﻟﺑﺗﻝ۷
        fee_result = self.rule_engine.calculate_fees(order.to_dict())
        order.metadata['fees'] = fee_result
        
        # 4. ﮔ۶ﻟ۰ﻟ؟۱ﮒ
        return self._execute_order(order)
```

### 6.2 ﻝﭨﻛﺕﻟ۶ﮒﮔ۲ﮔ۴ﻝﺗ

1. **ﻛﺕﮒﮒﮔ۲ﮔ?*ﺅﺙﻟ؟۱ﮒﮒﻟ۶ﮔ۶ﻙﻠ۲ﻠ۸ﻠﮒ?
2. **ﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟**ﺅﺙﻝﺎﺝﻝ۰؟ﻟ؟۰ﻝ؟ﻛﭦ۳ﮔﮔﮔ?
3. **ﮔﻛﭦ۳ﮒﻠ۹ﻟﺁ?*ﺅﺙﮔ۲ﮔ۴ﮔﻛﭦ۳ﻛﭨﺓﮔﺙﮔﺁﮒ۵ﻝ؛۵ﮒﻟ۶ﮒ?
4. **ﮔﻛﭨﻝﮔ۶**ﺅﺙﮔﻝﭨﻝﮔ۶ﮔﻛﭨﮔﺁﮒ۵ﻝ؛۵ﮒﻟ۶ﮒ?

## 7. ﮔﭖﻟﺁﮔﺗﮔ۰

### 7.1 ﮒﮒﮔﭖﻟﺁ

```python
import pytest
from a_stock_rules import AStockRuleEngine, T1Rule, LimitUpDownRule

class TestAStockRuleEngine:
    """Aﻟ۰ﻟ۶ﮒﮒﺙﮔﮔﭖﻟﺁ?""
    
    def setup_method(self):
        self.engine = AStockRuleEngine()
        self.engine.register_rule(T1Rule("TRADE_001", "T+1ﻟ۶ﮒ", RuleCategory.TRADE))
        self.engine.register_rule(LimitUpDownRule("TRADE_002", "ﮔﭘ۷ﻟﺓﮒﻟ۶ﮒ?, RuleCategory.TRADE))
    
    def test_t1_rule_check(self):
        """ﮔﭖﻟﺁT+1ﻟ۶ﮒﮔ۲ﮔ?""
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
        assert "T+1ﮒﭘﮒﭦ۵" in t1_result.message
    
    def test_limit_up_rule_check(self):
        """ﮔﭖﻟﺁﮔﭘ۷ﻟﺓﮒﻟ۶ﮒﮔ۲ﮔ?""
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
        assert "ﮔﭘ۷ﮒ" in limit_result.message
    
    def test_fee_calculation(self):
        """ﮔﭖﻟﺁﻟﺑﺗﻝ۷ﻟ؟۰ﻝ؟"""
        order = {
            "symbol": "000001.SZ",
            "side": "BUY",
            "quantity": 10000,
            "price": 10.00
        }
        
        fee_result = self.engine.calculate_fees(order)
        
        assert fee_result.commission == max(100000 * 0.0003, 5.0)  # 30ﮒﮔﮔﻛﺛ?ﮒ?
        assert fee_result.stamp_tax == 0  # ﻛﺗﺍﮒ۴ﻛﺕﮔﭘﮒﺍﻟﺎﻝ۷?
        assert fee_result.total_fee > 0
```

### 7.2 ﻠﮔﮔﭖﻟﺁ

1. **ﻛﺕvn.pyﻠﮔﮔﭖﻟﺁ**ﺅﺙﻠ۹ﻟﺁﻟ۶ﮒﮒﺙﮔﮒ۷vn.pyﻠﻠﮒ۷ﻛﺕﻝﮔ۲ﻝ۰؟ﮔ?
2. **ﮒ۳ﻟ۶ﮒﻝﭨﮒﮔﭖﻟﺁ?*ﺅﺙﮔﭖﻟﺁﮒ۳ﻛﺕ۹ﻟ۶ﮒﮒﮔﭘﻝﮔﻝﮒﭦﮔﺁ
3. **ﮔ۶ﻟﺛﮔﭖﻟﺁ**ﺅﺙﮔﭖﻟﺁﻟ۶ﮒﮔ۲ﮔ۴ﻝﮔ۶ﻟﺛﮒﺛﺎﮒ
4. **ﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁ**ﺅﺙﮔﭖﻟﺁﮒﻝ۶ﻟﺝﺗﻝﮔﮒ?

### 7.3 ﮔﭖﻟﺁﮔﺍﮔ؟

- **ﮔ۲ﮒﺕﺕﻛﭦ۳ﮔﮒﭦﮔﺁ**ﺅﺙﮔ؟ﻠﻛﺗﺍﮒﻟ؟۱ﮒ?
- **ﻟ۶ﮒﻟﺟﻟ۶ﮒﭦﮔﺁ**ﺅﺙT+1ﻟﺟﻟ۶ﻙﮔﭘ۷ﻟﺓﮒﻟﺟﻟ۶ﻙﻛﭨﻛﺛﻟﭘﻠ?
- **ﻟﺝﺗﻝﮒﭦﮔﺁ**ﺅﺙﮔﻛﺛﻛﺛ۲ﻠﻙﮔﮒ۳۶ﻛﭨﻛﺛﻙﮔﭘ۷ﮒﻛﭨﺓﮔﻛﭦ۳
- **ﮒﺙﮒﺕﺕﮒﭦﮔﺁ**ﺅﺙﮔﮔﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﻙﮒﺙﮒﺕﺕﻛﭨﺓﮔﺙﻙﻠﭘﮔﺍﻠ

## 8. ﮒ؟ﮔﺛﻟ؟۰ﮒ

### 8.1 ﻠﭘﮔ؟ﭖﮒﮒ

| ﻠﭘﮔ؟ﭖ | ﮔﭘﻠﺑ | ﻝ؟ﮔ | ﻛﭦ۳ﻛﭨﻝ?|
|------|------|------|--------|
| **ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ** | 3-5ﮒ۳?| ﮒ؟ﮔﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ | ﮔ؛ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ﻙﮔ۴ﮒ۲ﮒ؟ﻛﺗﻙﻠﻝﺛ؟ﮔ۷۰ﮔ?|
| **ﮒﺙﮒﻠﭘﮔ؟?* | 10-15ﮒ۳?| ﮒ؟ﻝﺍﮔﺕﮒﺟﮒﻟﺛ | ﻟ۶ﮒﮒﺙﮔﻛﭨ۲ﻝﻙﻟ۶ﮒﮒ؟ﻝﺍﻝﺎﭨﻙﮒﮒﮔﭖﻟﺁ?|
| **ﮔﭖﻟﺁﻠﭘﮔ؟ﭖ** | 5-7ﮒ۳?| ﮒ؟ﮔﮒ۷ﻠ۱ﮔﭖﻟﺁ | ﮔﭖﻟﺁﻝ۷ﻛﺝﻙﮔ۶ﻟﺛﮔ۴ﮒﻙﻠﮔﮔﭖﻟﺁﻝﭨﮔ?|
| **ﻠﮔﻠﭘﮔ؟ﭖ** | 3-5ﮒ۳?| ﻠﮔﮒﺍﮒ۳ﮒﺙﮔﮔﭘﮔ | ﻠﻠﮒ۷ﻠﮔﻛﭨ۲ﻝﻙﻠﻝﺛ؟ﻝ۳ﭦﻛﺝ?|
| **ﻛﺙﮒﻠﭘﮔ؟ﭖ** | 3-5ﮒ۳?| ﮔ۶ﻟﺛﻛﺙﮒﮒﮒﻟﺛﮒ؟ﮒ?| ﻛﺙﮒﻛﭨ۲ﻝﻙﮔﮔ۰۲ﮒ؟ﮒﻙﻝ۳ﭦﻛﺝﻝﻝ?|

### 8.2 ﻟﭖﮔﭦﻠﮔﺎ?

1. **ﮒﺙﮒﻟﭖﮔﭦ?*ﺅﺙ?
- ﮔﺕﮒﺟﮒﺙﮒﮒﺓ۴ﻝ۷ﮒﺕﺅﺙ?ﻛﭦﭦﺅﺙ10-15ﮒ۳۸ﺅﺙ
   - ﮔﭖﻟﺁﮒﺓ۴ﻝ۷ﮒﺕﺅﺙ0.5ﻛﭦﭦﺅﺙ5-7ﮒ۳۸ﺅﺙ
   - ﮔﭘﮔﮒﺕﮔﺁﮔﺅﺙ0.2ﻛﭦﭦﺅﺙﻟﺁﮒ؟۰ﮒﮔﮒﺁﺙﺅﺙ

2. **ﮔﮔﺁﻟﭖﮔﭦ?*ﺅﺙ?
   - ﮔﭖﻟﺁﻝﺁﮒ۱ﺅﺙAﻟ۰ﮒﮒﺎﮔﺍﮔ؟ﻙﮔ۷۰ﮔﻛﭦ۳ﮔﻝﺁﮒ۱?
   - ﮒﺙﮒﮒﺓ۴ﮒﺓﺅﺙPython 3.8+ﻙpytestﻙﮔ۶ﻟﺛﮒﮔﮒﺓ۴ﮒﺓ
   - ﮔﮔ۰۲ﮒﺓ۴ﮒﺓﺅﺙMarkdownﻙMermaidﮒﺝﻟ۰۷

### 8.3 ﻠ۲ﻠ۸ﻟﺁﻛﺙﺍﻛﺕﻝﺙﻟ۶?

| ﻠ۲ﻠ۸ | ﮒﺁﻟﺛﮔ?| ﮒﺛﺎﮒ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |
|------|--------|------|----------|
| **ﻟ۶ﮒﮒ۳ﮔﮔ?* | ﻠ،?| ﻛﺕ?| ﮒﻠﭘﮔ؟ﭖﮒ؟ﻝﺍﺅﺙﮒﮔﺕﮒﺟﻟ۶ﮒﮒﮔ۸ﮒﺎﻟ۶ﮒ |
| **ﮔ۶ﻟﺛﻠ؟ﻠ۱** | ﻛﺕ?| ﻛﺕ?| ﮒ؟ﻝﺍﻟ۶ﮒﻝﺙﮒﺅﺙﻛﺙﮒﮔ۲ﮔ۴ﻝ؟ﮔﺏ?|
| **ﻠﻝﺛ؟ﮒ۳ﮔﮔ?* | ﻛﺕ?| ﻛﺛ?| ﮔﻛﺝﻟﺁ۵ﻝﭨﻠﻝﺛ؟ﻝ۳ﭦﻛﺝﮒﻠ۹ﻟﺁﮒﺓ۴ﮒ?|
| **ﻠﮔﻠ؟ﻠ۱** | ﻛﺛ?| ﻠ،?| ﻟ؟ﺝﻟ؟۰ﮔﺕﮔﺍﮔ۴ﮒ۲ﺅﺙﮔﻛﺝﻠﮔﻝ۳ﭦﻛﺝ?|
| **ﻝﭨﺑﮔ۳ﮔﮔ؛** | ﻛﺛ?| ﻛﺕ?| ﮔ۷۰ﮒﮒﻟ؟ﺝﻟ؟۰ﺅﺙﻟﺁﮒ۴ﺛﮔﮔ۰۲ |

## 9. ﮒﻝﭨﮔ۸ﮒﺎ

### 9.1 ﻝﮔﮔ۸ﮒﺎﺅﺙ?ﻛﺕ۹ﮔﮒﺅﺙ

1. **ﮔﺑﮒ۳Aﻟ۰ﻟ۶ﮒ?*ﺅﺙﮒ۳۶ﮒ؟ﻛﭦ۳ﮔﻟ۶ﮒﻙﻟﻟﭖﻟﮒﺕﻟ۶ﮒ?
2. **ﮔﺕﺁﻟ۰ﻟ۶ﮒ**ﺅﺙﮔﺕﺁﻟ۰ﮒﺕﮒﭦﻛﭦ۳ﮔﻟ۶ﮒ?
3. **ﻝﺝﻟ۰ﻟ۶ﮒ**ﺅﺙﻝﺝﻟ۰ﮒﺕﮒﭦﻛﭦ۳ﮔﻟ۶ﮒ?
4. **ﻟ۶ﮒﮒﺁﻟ۶ﮒ?*ﺅﺙﻟ۶ﮒﻠﻝﺛ؟ﮒﻝ؟۰ﻝﻝﻠ۱

### 9.2 ﻛﺕﮔﮔ۸ﮒﺎﺅﺙ?ﻛﺕ۹ﮔﮒﺅﺙ

1. **ﻟ۶ﮒﮒ۵ﻛﺗ**ﺅﺙﮒﭦﻛﭦﮒﮒﺎﮔﺍﮔ؟ﻟ۹ﮒ۷ﻛﺙﮒﻟ۶ﮒﮒﮔ?
2. **ﮔﭦﻟﺛﻟ۶ﮒﮔ۷ﻟ**ﺅﺙﮔﺗﮔ؟ﮒﺕﮒﭦﻝﭘﮔﮔ۷ﻟﻠﻝ۷ﻟ۶ﮒ
3. **ﻟ۶ﮒﮒﮔﭖ**ﺅﺙﻟ۶ﮒﮒﺁﺗﻝﻝ۴ﻝﭨ۸ﮔﻝﮒﺛﺎﮒﮒﮔ?
4. **ﮒﮒﺕﮒﺙﻟ۶ﮒﮒﺙﮔ?*ﺅﺙﮔﺁﮔﮒﮒﺕﮒﺙﻟ۶ﮒﮔ۲ﮔ?

### 9.3 ﻠﺟﮔﮔ۸ﮒﺎﺅﺙ?ﮒﺗﺑﮒﺅﺙ?

1. **AIﻟ۶ﮒﻝﮔ**ﺅﺙﻛﺛﺟﻝ۷AIﻝﮔﻛﭦ۳ﮔﻟ۶ﮒ
2. **ﮒ؟ﮔﭘﻟ۶ﮒﻟﺍﮔﺑ**ﺅﺙﮔﺗﮔ؟ﮒﺕﮒﭦﮔﺏ۱ﮒ۷ﮒ؟ﮔﭘﻟﺍﮔﺑﻟ۶ﮒ?
3. **ﻟﺓ۷ﮒﺕﮒﭦﻟ۶ﮒ?*ﺅﺙﮔﺁﮔﮒ۳ﮒﺕﮒﭦﻝﭨﻛﺕﻟ۶ﮒﻝ؟۰ﻝ
4. **ﻟ۶ﮒﮒﺕﮒﭦ**ﺅﺙﻝ۷ﮔﺓﮒﺎﻛﭦ،ﮒﻛﭦ۳ﮔﻟ۶ﮒﮔ۷۰ﮔﺟ

## 10. ﮔﮔ۰۲ﻝﭨﺑﮔ۳

### 10.1 ﮔﮔ۰۲ﮔﺕﮒ

1. **ﮔ؛ﻟ؟ﺝﻟ؟۰ﮔﮔ۰?*ﺅﺙﮔﭘﮔﻟ؟ﺝﻟ؟۰ﮒﮔ۴ﮒ۲ﮒ؟ﻛﺗ
2. **APIﮔﮔ۰۲**ﺅﺙﻟ۶ﮒﮒﺙﮔAPIﮒﻟ?
3. **ﻠﻝﺛ؟ﮔﮒ**ﺅﺙﻟ۶ﮒﻠﻝﺛ؟ﻟﺁ۵ﻝﭨﮔﮒ?
4. **ﻠﮔﮔﮒ**ﺅﺙﻛﺕﮒﭘﻛﭨﮔ۷۰ﮒﻠﮔﮔﮒ
5. **ﻝ۷ﮔﺓﮔﮒ**ﺅﺙﮔﻝﭨﻝ۷ﮔﺓﻛﺛﺟﻝ۷ﮔﮒ?
6. **ﮒﺙﮒﮔﮒ?*ﺅﺙﻟ۶ﮒﮒﺙﮒﮔ۸ﮒﺎﮔﮒ?

### 10.2 ﮔﺑﮔﺍﮔﭦﮒﭘ

1. **ﻝﮔ؛ﮔ۶ﮒﭘ**ﺅﺙﻛﺛﺟﻝ۷ﻟﺁﻛﺗﮒﻝﮔ؛ﮔ۶ﮒﭘ
2. **ﮒﮔﺑﮔ۴ﮒﺟ**ﺅﺙﻟ؟ﺍﮒﺛﮔﮔﻟ؟ﺝﻟ؟۰ﮒﮔ?
3. **ﻟﺁﮒ؟۰ﮔﭖﻝ۷**ﺅﺙﻠﮒ۳۶ﮒﮔﺑﻠﻝﭨﮔﭘﮔﻟﺁﮒ؟?
4. **ﮔﮔ۰۲ﮒﮔ۴**ﺅﺙﻛﭨ۲ﻝﮒﮔﺑﮔﭘﮒﮔ۴ﮔﺑﮔﺍﮔﮔ۰۲

---

**ﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰ﻟ۵ﻝﺗ**ﺅﺙ?
1. ﻟ۶ﮒﮒﻝﺎﭨﻛﺛﻝﺏﭨﮔﺁﮒ۵ﮒ؟ﮔﺑﻟ۵ﻝAﻟ۰ﻠﮔﺎ?
2. ﮔ۴ﮒ۲ﻟ؟ﺝﻟ؟۰ﮔﺁﮒ۵ﮔﺕﮔﺍﮔﻝ۷
3. ﻠﻝﺛ؟ﮔ۷۰ﮔﺟﮔﺁﮒ۵ﻝﭖﮔﺑﭨﻛﺕﻛﺕﮔﮒﭦﻠ?
4. ﮔ۶ﻟﺛﻟ؟ﺝﻟ؟۰ﮔﺁﮒ۵ﻟﺛﮔﭨ۰ﻟﭘﺏﮒ؟ﮔﭘﻛﭦ۳ﮔﻠﮔﺎ?
5. ﻠﮔﮔﺗﮔ۰ﮔﺁﮒ۵ﻛﺕﻝﺍﮔﮔﭘﮔﮒﺙﮒ؟?

**ﻛﺕﻛﺕﮔ۴ﻟ۰ﮒ?*ﺅﺙ?
1. ﻝﭨﻝﭨﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰ﻛﺙﻟ؟؟
2. ﮔﺗﮔ؟ﻟﺁﮒ؟۰ﮔﻟ۶ﻛﺟ؟ﮔﺗﻟ؟ﺝﻟ؟۰
3. ﮒﺙﮒ۶ﮒﺙﮒﻠﭘﮔ؟ﭖﻛﭨﭨﮒ۰ﮒﻟ۶?
4. ﮒﮒﭨﭦﮒﺙﮒﻝﺁﮒ۱ﮒﮔﮔﺁﮔﮒﮒ۳
