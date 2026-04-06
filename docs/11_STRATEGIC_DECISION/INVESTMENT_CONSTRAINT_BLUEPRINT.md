---
module_id: INVESTMENTCONSTRAINTBLUEPRIN_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
layer: Layer 9 (治理层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---

﻿---
module_id: INVESTMENT_CONSTRAINT_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 11.14 - 投资限制管理系统
compliance_level: 专业标准
reference_models: ["BlackRock Aladdin Constraints", "Citadel Risk Limits", "Bridgewater Investment Guidelines"]
open_source_solution: "PyPortfolioOpt + skfolio"
priority: P1
---

# 投资限制管理系统蓝图

## 📋 文档职责说明

### 核心职责

本文档是**模块蓝图，负责特定功能的实现**。

### 职责边界

**负责**：
- ✅ 核心功能实现
- ✅ 接口定义
- ✅ 数据模型设计

**不负责**：
- ❌ 其他模块职责
- ❌ 跨模块协调

### 对接模块

**上游模块**：
- 上游模块

**下游模块**：
- 下游模块

---
> **版本**: v1.0
> **创建日期**: 2026-04-06
> **优先级**: 🟡 P1 - 专业增强
> **开源方案**: PyPortfolioOpt, skfolio
> **目标**: 构建专业级投资限制管理体系，确保投资组合符合各项约束

---

## 📋 执行摘要

### 核心定位

投资限制管理系统是Layer 11战略决策层的**合规守护者**，负责：
- 投资限制规则定义与管理
- 实时约束检查与违规预警
- 投资组合合规性验证
- 限制违规处理与调整建议

### 专业价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |
|---------|-------------|-------------|---------|
| **行业限制管理** | 专业合规团队 | 自动化约束引擎 | ⭐⭐⭐⭐ |
| **个股权重限制** | 风险委员会设定 | 配置化规则管理 | ⭐⭐⭐⭐⭐ |
| **集中度控制** | 实时监控 | 自动预警系统 | ⭐⭐⭐⭐ |
| **合规报告** | 专业报告团队 | 自动生成报告 | ⭐⭐⭐ |

**综合价值评级**: ⭐⭐⭐⭐ (4/5) - **推荐实施**

---

## 一、架构设计

### 1.1 系统整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│            投资限制管理系统架构 (Investment Constraint System)     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.14.1 限制规则管理层                         │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 规则定义引擎 (Rule Definition Engine)               │  │ │
│  │  │ ├── 行业限制规则（行业权重上下限）                   │  │ │
│  │  │ ├── 个股权重限制（单只股票权重限制）                 │  │ │
│  │  │ ├── 集中度限制（前N大持仓集中度）                    │  │ │
│  │  │ ├── 流动性限制（流动性约束）                         │  │ │
│  │  │ └── 自定义限制（用户自定义规则）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 规则配置管理 (Rule Configuration)                   │  │ │
│  │  │ ├── 规则版本管理（规则变更历史）                     │  │ │
│  │  │ ├── 规则优先级（规则执行顺序）                       │  │ │
│  │  │ ├── 规则生效条件（条件触发规则）                     │  │ │
│  │  │ └── 规则豁免机制（特殊豁免处理）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.14.2 约束检查层                            │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 实时约束检查器 (Real-time Constraint Checker)       │  │ │
│  │  │ ├── 权重约束检查（权重是否在限制内）                 │  │ │
│  │  │ ├── 行业约束检查（行业权重是否合规）                 │  │ │
│  │  │ ├── 集中度检查（集中度是否超标）                     │  │ │
│  │  │ ├── 流动性检查（流动性是否满足）                     │  │ │
│  │  │ └── 综合合规检查（所有约束综合检查）                 │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 违规检测引擎 (Violation Detector)                   │  │ │
│  │  │ ├── 违规识别（识别违反限制的情况）                   │  │ │
│  │  │ ├── 违规分级（违规严重程度分级）                     │  │ │
│  │  │ ├── 违规追踪（违规状态持续追踪）                     │  │ │
│  │  │ └── 违规记录（违规历史记录存储）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.14.3 预警与处理层                          │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 预警系统 (Alert System)                             │  │ │
│  │  │ ├── 实时预警（接近限制阈值预警）                     │  │ │
│  │  │ ├── 违规告警（违反限制紧急告警）                     │  │ │
│  │  │ ├── 趋势预警（违规趋势预警）                         │  │ │
│  │  │ └── 多级通知（分级通知机制）                         │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 调整建议引擎 (Adjustment Suggestion Engine)         │  │ │
│  │  │ ├── 自动调整建议（AI生成调整方案）                   │  │ │
│  │  │ ├── 手动调整指导（调整操作指导）                     │  │ │
│  │  │ ├── 调整影响评估（调整方案影响评估）                 │  │ │
│  │  │ └── 调整执行跟踪（调整执行效果跟踪）                 │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.14.4 报告与审计层                          │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 合规报告生成 (Compliance Report Generator)          │  │ │
│  │  │ ├── 日报（每日合规状态报告）                         │  │ │
│  │  │ ├── 周报（每周合规汇总报告）                         │  │ │
│  │  │ ├── 月报（每月合规分析报告）                         │  │ │
│  │  │ └── 专项报告（特定事件专项报告）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 审计追踪系统 (Audit Trail System)                   │  │ │
│  │  │ ├── 操作日志（所有操作记录）                         │  │ │
│  │  │ ├── 变更历史（规则变更历史）                         │  │ │
│  │  │ ├── 违规历史（违规事件历史）                         │  │ │
│  │  │ └── 审计报告（审计分析报告）                         │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责边界

| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |
|------|---------|------|------|---------|
| **限制规则管理层** | 规则定义、配置管理 | 规则配置 | 规则对象 | 约束检查层 |
| **约束检查层** | 实时检查、违规检测 | 组合权重、规则 | 检查结果、违规信息 | 预警处理层 |
| **预警与处理层** | 预警通知、调整建议 | 违规信息 | 预警信号、调整方案 | Layer 6, 11 |
| **报告与审计层** | 报告生成、审计追踪 | 检查结果 | 合规报告、审计日志 | Layer 7, 10 |

---

## 二、核心组件详细设计

### 2.1 限制规则管理层

#### 2.1.1 规则定义引擎

```python
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np

class ConstraintType(Enum):
    """约束类型"""
    SECTOR = "sector"              # 行业约束
    SINGLE_STOCK = "single_stock"  # 个股权重约束
    CONCENTRATION = "concentration"  # 集中度约束
    LIQUIDITY = "liquidity"        # 流动性约束
    FACTOR = "factor"              # 因子暴露约束
    CUSTOM = "custom"              # 自定义约束

class ConstraintSeverity(Enum):
    """约束严重程度"""
    HARD = "hard"      # 硬约束（必须满足）
    SOFT = "soft"      # 软约束（尽量满足）
    PREFERRED = "preferred"  # 偏好约束（优化目标）

@dataclass
class ConstraintRule:
    """约束规则"""
    rule_id: str
    rule_name: str
    constraint_type: ConstraintType
    severity: ConstraintSeverity
    description: str
    parameters: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'constraint_type': self.constraint_type.value,
            'severity': self.severity.value,
            'description': self.description,
            'parameters': self.parameters,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ConstraintRuleEngine:
    """约束规则引擎"""
    
    def __init__(self):
        self.rules: Dict[str, ConstraintRule] = {}
        self.sector_mapping: Dict[str, str] = {}
        
    def add_rule(self, rule: ConstraintRule):
        """添加规则"""
        self.rules[rule.rule_id] = rule
        
    def remove_rule(self, rule_id: str):
        """移除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            
    def update_rule(self, rule_id: str, parameters: Dict[str, Any]):
        """更新规则参数"""
        if rule_id in self.rules:
            self.rules[rule_id].parameters.update(parameters)
            self.rules[rule_id].updated_at = datetime.now()
    
    def set_sector_mapping(self, mapping: Dict[str, str]):
        """设置行业映射"""
        self.sector_mapping = mapping
    
    def get_active_rules(self) -> List[ConstraintRule]:
        """获取所有活跃规则"""
        return [r for r in self.rules.values() if r.is_active]
    
    def get_rules_by_type(self, constraint_type: ConstraintType) -> List[ConstraintRule]:
        """按类型获取规则"""
        return [r for r in self.rules.values() 
                if r.constraint_type == constraint_type and r.is_active]
    
    def create_sector_constraint(self,
                                sector_lower: Dict[str, float],
                                sector_upper: Dict[str, float]) -> ConstraintRule:
        """创建行业约束"""
        return ConstraintRule(
            rule_id=f"sector_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            rule_name="行业权重约束",
            constraint_type=ConstraintType.SECTOR,
            severity=ConstraintSeverity.HARD,
            description="限制各行业权重在指定范围内",
            parameters={
                'sector_lower': sector_lower,
                'sector_upper': sector_upper
            }
        )
    
    def create_single_stock_constraint(self,
                                      max_weight: float,
                                      min_weight: float = 0.0) -> ConstraintRule:
        """创建个股权重约束"""
        return ConstraintRule(
            rule_id=f"single_stock_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            rule_name="个股权重约束",
            constraint_type=ConstraintType.SINGLE_STOCK,
            severity=ConstraintSeverity.HARD,
            description=f"单只股票权重限制在{min_weight:.2%}到{max_weight:.2%}之间",
            parameters={
                'max_weight': max_weight,
                'min_weight': min_weight
            }
        )
    
    def create_concentration_constraint(self,
                                       top_n: int,
                                       max_concentration: float) -> ConstraintRule:
        """创建集中度约束"""
        return ConstraintRule(
            rule_id=f"concentration_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            rule_name="持仓集中度约束",
            constraint_type=ConstraintType.CONCENTRATION,
            severity=ConstraintSeverity.HARD,
            description=f"前{top_n}大持仓集中度不超过{max_concentration:.2%}",
            parameters={
                'top_n': top_n,
                'max_concentration': max_concentration
            }
        )
    
    def create_liquidity_constraint(self,
                                   min_adv_ratio: float = 0.01,
                                   max_adv_ratio: float = 0.05) -> ConstraintRule:
        """创建流动性约束"""
        return ConstraintRule(
            rule_id=f"liquidity_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            rule_name="流动性约束",
            constraint_type=ConstraintType.LIQUIDITY,
            severity=ConstraintSeverity.SOFT,
            description=f"持仓不超过日均成交量的{max_adv_ratio:.2%}",
            parameters={
                'min_adv_ratio': min_adv_ratio,
                'max_adv_ratio': max_adv_ratio
            }
        )
```

#### 2.1.2 规则配置管理

```python
@dataclass
class RuleVersion:
    """规则版本"""
    version_id: str
    rule_id: str
    parameters: Dict[str, Any]
    effective_date: datetime
    expiry_date: Optional[datetime]
    change_reason: str

class RuleConfigurationManager:
    """规则配置管理器"""
    
    def __init__(self):
        self.rule_versions: Dict[str, List[RuleVersion]] = {}
        self.rule_priorities: Dict[str, int] = {}
        
    def create_version(self,
                      rule_id: str,
                      parameters: Dict[str, Any],
                      effective_date: datetime,
                      change_reason: str,
                      expiry_date: Optional[datetime] = None) -> RuleVersion:
        """创建规则版本"""
        version_id = f"{rule_id}_v{len(self.rule_versions.get(rule_id, [])) + 1}"
        
        version = RuleVersion(
            version_id=version_id,
            rule_id=rule_id,
            parameters=parameters,
            effective_date=effective_date,
            expiry_date=expiry_date,
            change_reason=change_reason
        )
        
        if rule_id not in self.rule_versions:
            self.rule_versions[rule_id] = []
        self.rule_versions[rule_id].append(version)
        
        return version
    
    def get_active_version(self, 
                          rule_id: str,
                          as_of_date: datetime = None) -> Optional[RuleVersion]:
        """获取生效版本"""
        if as_of_date is None:
            as_of_date = datetime.now()
        
        versions = self.rule_versions.get(rule_id, [])
        
        for version in reversed(versions):
            if version.effective_date <= as_of_date:
                if version.expiry_date is None or version.expiry_date > as_of_date:
                    return version
        
        return None
    
    def set_priority(self, rule_id: str, priority: int):
        """设置规则优先级"""
        self.rule_priorities[rule_id] = priority
    
    def get_sorted_rules(self, rule_ids: List[str]) -> List[str]:
        """按优先级排序规则"""
        return sorted(rule_ids, 
                     key=lambda x: self.rule_priorities.get(x, 999))
```

---

### 2.2 约束检查层

#### 2.2.1 实时约束检查器

```python
@dataclass
class ConstraintCheckResult:
    """约束检查结果"""
    rule_id: str
    rule_name: str
    is_satisfied: bool
    current_value: float
    limit_value: float
    violation_amount: float
    violation_severity: str  # 'none', 'minor', 'moderate', 'severe'
    message: str

class RealtimeConstraintChecker:
    """实时约束检查器"""
    
    def __init__(self, rule_engine: ConstraintRuleEngine):
        self.rule_engine = rule_engine
        
    def check_all_constraints(self,
                             weights: Dict[str, float],
                             prices: Dict[str, float] = None,
                             volumes: Dict[str, float] = None,
                             adv: Dict[str, float] = None) -> List[ConstraintCheckResult]:
        """检查所有约束"""
        results = []
        
        for rule in self.rule_engine.get_active_rules():
            if rule.constraint_type == ConstraintType.SECTOR:
                result = self._check_sector_constraint(weights, rule)
            elif rule.constraint_type == ConstraintType.SINGLE_STOCK:
                result = self._check_single_stock_constraint(weights, rule)
            elif rule.constraint_type == ConstraintType.CONCENTRATION:
                result = self._check_concentration_constraint(weights, rule)
            elif rule.constraint_type == ConstraintType.LIQUIDITY:
                result = self._check_liquidity_constraint(
                    weights, prices, volumes, adv, rule
                )
            else:
                continue
            
            results.append(result)
        
        return results
    
    def _check_sector_constraint(self,
                                weights: Dict[str, float],
                                rule: ConstraintRule) -> ConstraintCheckResult:
        """检查行业约束"""
        sector_weights = self._calculate_sector_weights(weights)
        
        violations = []
        max_violation = 0
        violated_sector = None
        
        sector_lower = rule.parameters.get('sector_lower', {})
        sector_upper = rule.parameters.get('sector_upper', {})
        
        for sector, weight in sector_weights.items():
            lower = sector_lower.get(sector, 0)
            upper = sector_upper.get(sector, 1.0)
            
            if weight < lower:
                violation = lower - weight
                if violation > max_violation:
                    max_violation = violation
                    violated_sector = sector
                violations.append(f"{sector}权重{weight:.2%}低于下限{lower:.2%}")
            
            if weight > upper:
                violation = weight - upper
                if violation > max_violation:
                    max_violation = violation
                    violated_sector = sector
                violations.append(f"{sector}权重{weight:.2%}超过上限{upper:.2%}")
        
        is_satisfied = len(violations) == 0
        
        return ConstraintCheckResult(
            rule_id=rule.rule_id,
            rule_name=rule.rule_name,
            is_satisfied=is_satisfied,
            current_value=sector_weights.get(violated_sector, 0) if violated_sector else 0,
            limit_value=sector_upper.get(violated_sector, 1.0) if violated_sector else 1.0,
            violation_amount=max_violation,
            violation_severity=self._get_severity(max_violation),
            message="; ".join(violations) if violations else "行业约束满足"
        )
    
    def _check_single_stock_constraint(self,
                                      weights: Dict[str, float],
                                      rule: ConstraintRule) -> ConstraintCheckResult:
        """检查个股权重约束"""
        max_weight = rule.parameters.get('max_weight', 1.0)
        min_weight = rule.parameters.get('min_weight', 0.0)
        
        violations = []
        max_violation = 0
        violated_stock = None
        
        for stock, weight in weights.items():
            if weight < min_weight:
                violation = min_weight - weight
                if violation > max_violation:
                    max_violation = violation
                    violated_stock = stock
                violations.append(f"{stock}权重{weight:.2%}低于下限{min_weight:.2%}")
            
            if weight > max_weight:
                violation = weight - max_weight
                if violation > max_violation:
                    max_violation = violation
                    violated_stock = stock
                violations.append(f"{stock}权重{weight:.2%}超过上限{max_weight:.2%}")
        
        is_satisfied = len(violations) == 0
        
        return ConstraintCheckResult(
            rule_id=rule.rule_id,
            rule_name=rule.rule_name,
            is_satisfied=is_satisfied,
            current_value=weights.get(violated_stock, 0) if violated_stock else 0,
            limit_value=max_weight,
            violation_amount=max_violation,
            violation_severity=self._get_severity(max_violation),
            message="; ".join(violations) if violations else "个股权重约束满足"
        )
    
    def _check_concentration_constraint(self,
                                       weights: Dict[str, float],
                                       rule: ConstraintRule) -> ConstraintCheckResult:
        """检查集中度约束"""
        top_n = rule.parameters.get('top_n', 10)
        max_concentration = rule.parameters.get('max_concentration', 0.5)
        
        sorted_weights = sorted(weights.values(), reverse=True)
        top_n_concentration = sum(sorted_weights[:top_n])
        
        is_satisfied = top_n_concentration <= max_concentration
        violation_amount = max(0, top_n_concentration - max_concentration)
        
        return ConstraintCheckResult(
            rule_id=rule.rule_id,
            rule_name=rule.rule_name,
            is_satisfied=is_satisfied,
            current_value=top_n_concentration,
            limit_value=max_concentration,
            violation_amount=violation_amount,
            violation_severity=self._get_severity(violation_amount),
            message=f"前{top_n}大持仓集中度{top_n_concentration:.2%}" + 
                   (f"超过上限{max_concentration:.2%}" if not is_satisfied else f"在限制内")
        )
    
    def _check_liquidity_constraint(self,
                                   weights: Dict[str, float],
                                   prices: Dict[str, float],
                                   volumes: Dict[str, float],
                                   adv: Dict[str, float],
                                   rule: ConstraintRule) -> ConstraintCheckResult:
        """检查流动性约束"""
        if not adv or not prices:
            return ConstraintCheckResult(
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                is_satisfied=True,
                current_value=0,
                limit_value=0,
                violation_amount=0,
                violation_severity='none',
                message="流动性数据缺失，跳过检查"
            )
        
        max_adv_ratio = rule.parameters.get('max_adv_ratio', 0.05)
        
        violations = []
        max_violation = 0
        violated_stock = None
        
        for stock, weight in weights.items():
            if stock in adv and stock in prices:
                position_value = weight * 1000000  # 假设组合规模100万
                daily_volume = adv[stock] * prices[stock]
                
                if daily_volume > 0:
                    adv_ratio = position_value / daily_volume
                    
                    if adv_ratio > max_adv_ratio:
                        violation = adv_ratio - max_adv_ratio
                        if violation > max_violation:
                            max_violation = violation
                            violated_stock = stock
                        violations.append(f"{stock}持仓占日均成交量{adv_ratio:.2%}超过上限{max_adv_ratio:.2%}")
        
        is_satisfied = len(violations) == 0
        
        return ConstraintCheckResult(
            rule_id=rule.rule_id,
            rule_name=rule.rule_name,
            is_satisfied=is_satisfied,
            current_value=0,
            limit_value=max_adv_ratio,
            violation_amount=max_violation,
            violation_severity=self._get_severity(max_violation),
            message="; ".join(violations) if violations else "流动性约束满足"
        )
    
    def _calculate_sector_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """计算行业权重"""
        sector_weights = {}
        
        for stock, weight in weights.items():
            sector = self.rule_engine.sector_mapping.get(stock, 'other')
            sector_weights[sector] = sector_weights.get(sector, 0) + weight
        
        return sector_weights
    
    def _get_severity(self, violation_amount: float) -> str:
        """获取违规严重程度"""
        if violation_amount <= 0:
            return 'none'
        elif violation_amount < 0.02:
            return 'minor'
        elif violation_amount < 0.05:
            return 'moderate'
        else:
            return 'severe'
```

#### 2.2.2 违规检测引擎

```python
@dataclass
class ViolationRecord:
    """违规记录"""
    violation_id: str
    rule_id: str
    detected_at: datetime
    violation_type: str
    severity: str
    details: Dict[str, Any]
    status: str  # 'active', 'resolved', 'waived'
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None

class ViolationDetector:
    """违规检测引擎"""
    
    def __init__(self):
        self.violations: Dict[str, ViolationRecord] = {}
        self.violation_counter = 0
        
    def detect_violations(self,
                         check_results: List[ConstraintCheckResult]) -> List[ViolationRecord]:
        """检测违规"""
        new_violations = []
        
        for result in check_results:
            if not result.is_satisfied:
                self.violation_counter += 1
                
                violation = ViolationRecord(
                    violation_id=f"VIO_{self.violation_counter:06d}",
                    rule_id=result.rule_id,
                    detected_at=datetime.now(),
                    violation_type=result.rule_name,
                    severity=result.violation_severity,
                    details={
                        'current_value': result.current_value,
                        'limit_value': result.limit_value,
                        'violation_amount': result.violation_amount,
                        'message': result.message
                    },
                    status='active'
                )
                
                self.violations[violation.violation_id] = violation
                new_violations.append(violation)
        
        return new_violations
    
    def resolve_violation(self,
                         violation_id: str,
                         resolution: str):
        """解决违规"""
        if violation_id in self.violations:
            self.violations[violation_id].status = 'resolved'
            self.violations[violation_id].resolved_at = datetime.now()
            self.violations[violation_id].resolution = resolution
    
    def waive_violation(self,
                       violation_id: str,
                       reason: str):
        """豁免违规"""
        if violation_id in self.violations:
            self.violations[violation_id].status = 'waived'
            self.violations[violation_id].resolved_at = datetime.now()
            self.violations[violation_id].resolution = f"豁免原因: {reason}"
    
    def get_active_violations(self) -> List[ViolationRecord]:
        """获取活跃违规"""
        return [v for v in self.violations.values() if v.status == 'active']
    
    def get_violation_statistics(self) -> Dict:
        """获取违规统计"""
        all_violations = list(self.violations.values())
        
        return {
            'total': len(all_violations),
            'active': len([v for v in all_violations if v.status == 'active']),
            'resolved': len([v for v in all_violations if v.status == 'resolved']),
            'waived': len([v for v in all_violations if v.status == 'waived']),
            'by_severity': {
                'minor': len([v for v in all_violations if v.severity == 'minor']),
                'moderate': len([v for v in all_violations if v.severity == 'moderate']),
                'severe': len([v for v in all_violations if v.severity == 'severe'])
            }
        }
```

---

### 2.3 预警与处理层

#### 2.3.1 预警系统

```python
from enum import Enum
from typing import List, Callable

class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """预警信息"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    related_violation: Optional[str] = None
    acknowledged: bool = False

class AlertSystem:
    """预警系统"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable] = []
        self.alert_counter = 0
        
    def add_handler(self, handler: Callable):
        """添加预警处理器"""
        self.alert_handlers.append(handler)
    
    def generate_alerts(self,
                       check_results: List[ConstraintCheckResult],
                       violations: List[ViolationRecord]) -> List[Alert]:
        """生成预警"""
        new_alerts = []
        
        for result in check_results:
            if not result.is_satisfied:
                self.alert_counter += 1
                
                level = self._determine_alert_level(result.violation_severity)
                
                alert = Alert(
                    alert_id=f"ALT_{self.alert_counter:06d}",
                    level=level,
                    title=f"约束违规: {result.rule_name}",
                    message=result.message,
                    timestamp=datetime.now(),
                    related_violation=None
                )
                
                self.alerts.append(alert)
                new_alerts.append(alert)
                
                self._dispatch_alert(alert)
        
        for violation in violations:
            self.alert_counter += 1
            
            level = AlertLevel.ERROR if violation.severity == 'severe' else AlertLevel.WARNING
            
            alert = Alert(
                alert_id=f"ALT_{self.alert_counter:06d}",
                level=level,
                title=f"违规检测: {violation.violation_type}",
                message=f"检测到{violation.severity}级别违规",
                timestamp=datetime.now(),
                related_violation=violation.violation_id
            )
            
            self.alerts.append(alert)
            new_alerts.append(alert)
            
            self._dispatch_alert(alert)
        
        return new_alerts
    
    def _determine_alert_level(self, severity: str) -> AlertLevel:
        """确定预警级别"""
        mapping = {
            'none': AlertLevel.INFO,
            'minor': AlertLevel.WARNING,
            'moderate': AlertLevel.ERROR,
            'severe': AlertLevel.CRITICAL
        }
        return mapping.get(severity, AlertLevel.WARNING)
    
    def _dispatch_alert(self, alert: Alert):
        """分发预警"""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Alert handler error: {e}")
    
    def acknowledge_alert(self, alert_id: str):
        """确认预警"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                break
    
    def get_unacknowledged_alerts(self) -> List[Alert]:
        """获取未确认预警"""
        return [a for a in self.alerts if not a.acknowledged]
```

#### 2.3.2 调整建议引擎

```python
@dataclass
class AdjustmentSuggestion:
    """调整建议"""
    suggestion_id: str
    violation_id: str
    adjustment_type: str  # 'reduce', 'increase', 'rebalance'
    target_stocks: List[str]
    suggested_changes: Dict[str, float]
    expected_impact: Dict[str, float]
    priority: int

class AdjustmentSuggestionEngine:
    """调整建议引擎"""
    
    def __init__(self, 
                 rule_engine: ConstraintRuleEngine,
                 checker: RealtimeConstraintChecker):
        self.rule_engine = rule_engine
        self.checker = checker
        
    def generate_suggestions(self,
                            weights: Dict[str, float],
                            violations: List[ViolationRecord]) -> List[AdjustmentSuggestion]:
        """生成调整建议"""
        suggestions = []
        
        for violation in violations:
            rule = self.rule_engine.rules.get(violation.rule_id)
            
            if rule is None:
                continue
            
            if rule.constraint_type == ConstraintType.SINGLE_STOCK:
                suggestion = self._generate_single_stock_adjustment(
                    weights, violation, rule
                )
                if suggestion:
                    suggestions.append(suggestion)
            
            elif rule.constraint_type == ConstraintType.SECTOR:
                suggestion = self._generate_sector_adjustment(
                    weights, violation, rule
                )
                if suggestion:
                    suggestions.append(suggestion)
            
            elif rule.constraint_type == ConstraintType.CONCENTRATION:
                suggestion = self._generate_concentration_adjustment(
                    weights, violation, rule
                )
                if suggestion:
                    suggestions.append(suggestion)
        
        return sorted(suggestions, key=lambda x: x.priority)
    
    def _generate_single_stock_adjustment(self,
                                         weights: Dict[str, float],
                                         violation: ViolationRecord,
                                         rule: ConstraintRule) -> Optional[AdjustmentSuggestion]:
        """生成个股权重调整建议"""
        max_weight = rule.parameters.get('max_weight', 1.0)
        
        overweight_stocks = [
            stock for stock, weight in weights.items()
            if weight > max_weight
        ]
        
        if not overweight_stocks:
            return None
        
        suggested_changes = {}
        for stock in overweight_stocks:
            excess = weights[stock] - max_weight
            suggested_changes[stock] = -excess
        
        return AdjustmentSuggestion(
            suggestion_id=f"ADJ_{violation.violation_id}",
            violation_id=violation.violation_id,
            adjustment_type='reduce',
            target_stocks=overweight_stocks,
            suggested_changes=suggested_changes,
            expected_impact={
                'weight_reduction': sum(abs(v) for v in suggested_changes.values())
            },
            priority=1 if violation.severity == 'severe' else 2
        )
    
    def _generate_sector_adjustment(self,
                                   weights: Dict[str, float],
                                   violation: ViolationRecord,
                                   rule: ConstraintRule) -> Optional[AdjustmentSuggestion]:
        """生成行业调整建议"""
        sector_weights = self.checker._calculate_sector_weights(weights)
        sector_upper = rule.parameters.get('sector_upper', {})
        
        overweight_sectors = [
            sector for sector, weight in sector_weights.items()
            if sector in sector_upper and weight > sector_upper[sector]
        ]
        
        if not overweight_sectors:
            return None
        
        target_stocks = []
        suggested_changes = {}
        
        for sector in overweight_sectors:
            excess = sector_weights[sector] - sector_upper[sector]
            
            sector_stocks = [
                stock for stock, s in self.rule_engine.sector_mapping.items()
                if s == sector
            ]
            
            for stock in sector_stocks:
                if stock in weights:
                    target_stocks.append(stock)
                    suggested_changes[stock] = -weights[stock] * (excess / sector_weights[sector])
        
        return AdjustmentSuggestion(
            suggestion_id=f"ADJ_{violation.violation_id}",
            violation_id=violation.violation_id,
            adjustment_type='reduce',
            target_stocks=target_stocks,
            suggested_changes=suggested_changes,
            expected_impact={
                'sector_rebalance': overweight_sectors
            },
            priority=1
        )
    
    def _generate_concentration_adjustment(self,
                                          weights: Dict[str, float],
                                          violation: ViolationRecord,
                                          rule: ConstraintRule) -> Optional[AdjustmentSuggestion]:
        """生成集中度调整建议"""
        top_n = rule.parameters.get('top_n', 10)
        max_concentration = rule.parameters.get('max_concentration', 0.5)
        
        sorted_stocks = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        top_stocks = sorted_stocks[:top_n]
        top_concentration = sum(w for _, w in top_stocks)
        
        if top_concentration <= max_concentration:
            return None
        
        excess = top_concentration - max_concentration
        
        suggested_changes = {}
        for stock, weight in top_stocks:
            reduction = weight * (excess / top_concentration)
            suggested_changes[stock] = -reduction
        
        return AdjustmentSuggestion(
            suggestion_id=f"ADJ_{violation.violation_id}",
            violation_id=violation.violation_id,
            adjustment_type='reduce',
            target_stocks=[s for s, _ in top_stocks],
            suggested_changes=suggested_changes,
            expected_impact={
                'concentration_reduction': excess
            },
            priority=2
        )
```

---

## 三、开源集成方案

### 3.1 PyPortfolioOpt集成

```python
from pypfopt import EfficientFrontier
from pypfopt import objective_functions

class PyPortfolioOptIntegration:
    """PyPortfolioOpt约束集成"""
    
    def __init__(self, 
                 expected_returns: pd.Series,
                 cov_matrix: pd.DataFrame):
        self.expected_returns = expected_returns
        self.cov_matrix = cov_matrix
        self.ef = EfficientFrontier(expected_returns, cov_matrix)
    
    def add_sector_constraints(self,
                              sector_mapper: Dict[str, str],
                              sector_lower: Dict[str, float],
                              sector_upper: Dict[str, float]):
        """添加行业约束"""
        self.ef.add_sector_constraints(
            sector_mapper, sector_lower, sector_upper
        )
    
    def add_weight_constraints(self,
                              min_weight: float = 0.0,
                              max_weight: float = 1.0):
        """添加权重约束"""
        self.ef.add_constraint(lambda w: w >= min_weight)
        self.ef.add_constraint(lambda w: w <= max_weight)
    
    def add_tracking_error_constraint(self,
                                     benchmark_weights: Dict[str, float],
                                     max_tracking_error: float):
        """添加跟踪误差约束"""
        self.ef.add_constraint(
            objective_functions.ex_ante_tracking_error,
            cov_matrix=self.cov_matrix,
            benchmark_weights=benchmark_weights,
            max_tracking_error=max_tracking_error
        )
    
    def optimize(self, objective: str = 'max_sharpe') -> Dict[str, float]:
        """执行优化"""
        if objective == 'max_sharpe':
            weights = self.ef.max_sharpe()
        elif objective == 'min_volatility':
            weights = self.ef.min_volatility()
        else:
            weights = self.ef.min_volatility()
        
        return self.ef.clean_weights()
```

### 3.2 skfolio集成

```python
from skfolio import Portfolio
from skfolio.optimization import MeanRisk, RiskBudgeting
from skfolio.prior import EmpiricalPrior

class SkfolioIntegration:
    """skfolio约束集成"""
    
    def __init__(self):
        self.model = None
    
    def create_constrained_model(self,
                                min_weights: float = 0.0,
                                max_weights: float = 1.0,
                                transaction_costs: float = 0.001):
        """创建约束模型"""
        self.model = MeanRisk(
            prior_estimator=EmpiricalPrior(),
            min_weights=min_weights,
            max_weights=max_weights,
            transaction_costs=transaction_costs
        )
        return self.model
    
    def fit(self, returns: pd.DataFrame):
        """训练模型"""
        if self.model:
            self.model.fit(returns)
    
    def predict(self, returns: pd.DataFrame) -> Portfolio:
        """预测"""
        if self.model:
            return self.model.predict(returns)
        return None
```

---

## 四、实施路径

### Phase 1: 核心功能（1周）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 规则定义引擎 | 2天 | ConstraintRuleEngine |
| 约束检查器 | 2天 | RealtimeConstraintChecker |
| 违规检测器 | 1天 | ViolationDetector |

### Phase 2: 预警处理（1周）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 预警系统 | 2天 | AlertSystem |
| 调整建议引擎 | 2天 | AdjustmentSuggestionEngine |
| 开源集成 | 2天 | PyPortfolioOpt/skfolio集成 |

### Phase 3: 报告审计（3天）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 合规报告生成 | 1天 | ReportGenerator |
| 审计追踪系统 | 1天 | AuditTrailSystem |
| 文档完善 | 1天 | 使用文档 |

---

## 五、相关文档

| 文档 | 说明 |
|------|------|
| [BLUEPRINT.md](./BLUEPRINT.md) | Layer 11主蓝图 |
| [MARKET_REGIME_BLUEPRINT.md](./MARKET_REGIME_BLUEPRINT.md) | 市场状态识别系统 |
| [MACRO_FACTOR_BLUEPRINT.md](./MACRO_FACTOR_BLUEPRINT.md) | 宏观因子系统 |

---

**版本**: v1.0 | **更新**: 2026-04-06 | **状态**: ✅ 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Investment Constraint
- **模块ID**: INVESTMENT_CONSTRAINT_001
- **蓝图文档**: [INVESTMENT_CONSTRAINT_BLUEPRINT.md](./11_STRATEGIC_DECISION\INVESTMENT_CONSTRAINT_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: Layer 11.14 - 投资限制管理系统
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Investment Constraint** | Layer 11.14 - 投资限制管理系统 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
