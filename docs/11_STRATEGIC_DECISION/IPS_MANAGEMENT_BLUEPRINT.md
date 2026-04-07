---
module_id: IPS_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
layer: Layer 7 (风控层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
responsibility:
  - 蓝图设计、架构规划

---
---

﻿---
module_id: IPS_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 11.19 - 投资政策声明管理系统
compliance_level: CFA专业标准
reference_models: ["CFA Institute IPS Standards", "Institutional Investment Policy Statement"]
open_source_solution: "自研简化版"
priority: P1
---

# 投资政策声明(IPS)管理系统蓝图
> **核心职责**: 投资政策声明(IPS)管理系统蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：投资政策声明(IPS)管理系统蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容

> **核心职责**: Ips Management蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Ips Management蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


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
> **优先级**: 🟡 P1 - 强烈建议
> **开源方案**: 自研简化版
> **目标**: 构建投资政策声明管理系统，明确投资纪律，避免情绪化决策

---

## 📋 执行摘要

### 核心定位

投资政策声明(IPS)管理系统是Layer 11战略决策层的**投资纪律框架**，负责：
- 投资目标与风险承受力定义
- 投资约束与限制条件管理
- 资产配置政策制定与监控
- 定期审查与合规检查

### 专业价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |
|---------|-------------|-------------|---------|
| **投资目标明确** | 投委会制定 | 个人定义+AI辅助 | ⭐⭐⭐⭐⭐ |
| **风险纪律约束** | 风险委员会监督 | 自动化监控预警 | ⭐⭐⭐⭐⭐ |
| **决策一致性** | IPS指导决策 | 系统自动检查 | ⭐⭐⭐⭐ |
| **定期审查** | 季度/年度审查 | 自动提醒+报告 | ⭐⭐⭐⭐ |

**综合价值评级**: ⭐⭐⭐⭐⭐ (5/5) - **强烈建议实施**

---

## 一、架构设计

### 1.1 系统整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│        投资政策声明管理系统架构 (IPS Management System)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.19.1 投资目标管理层                        │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 收益目标定义 (Return Objective Definition)          │  │ │
│  │  │ ├── 绝对收益目标（年化收益率目标）                   │  │ │
│  │  │ ├── 相对收益目标（相对基准超额收益）                 │  │ │
│  │  │ ├── 风险调整目标（夏普比率等）                       │  │ │
│  │  │ └── 收益目标优先级（目标优先排序）                   │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 风险承受力定义 (Risk Tolerance Definition)          │  │ │
│  │  │ ├── 最大回撤容忍度（可接受最大回撤）                 │  │ │
│  │  │ ├── 波动率容忍度（可接受波动率）                     │  │ │
│  │  │ ├── 风险预算分配（总风险预算设定）                   │  │ │
│  │  │ └── 风险偏好评估（风险偏好问卷评估）                 │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.19.2 投资约束管理层                        │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 流动性约束 (Liquidity Constraints)                  │  │ │
│  │  │ ├── 现金需求预测（短期现金需求）                     │  │ │
│  │  │ ├── 流动性缓冲（现金/货币基金比例）                  │  │ │
│  │  │ ├── 赎回限制（非流动性资产上限）                     │  │ │
│  │  │ └── 应急资金预留（紧急备用金）                       │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 时间期限约束 (Time Horizon Constraints)             │  │ │
│  │  │ ├── 投资期限设定（短期/中期/长期）                   │  │ │
│  │  │ ├── 目标日期规划（特定目标日期）                     │  │ │
│  │  │ ├── 阶段性目标（分阶段投资目标）                     │  │ │
│  │  │ └── 期限匹配策略（资产期限匹配）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 其他约束条件 (Other Constraints)                    │  │ │
│  │  │ ├── 税务约束（税务效率考虑）                         │  │ │
│  │  │ ├── 法律约束（合规要求）                             │  │ │
│  │  │ ├── 个人偏好（行业/公司偏好）                        │  │ │
│  │  │ └── 特殊限制（ESG、道德投资等）                      │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.19.3 资产配置政策层                        │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 战略资产配置政策 (Strategic Allocation Policy)      │  │ │
│  │  │ ├── 目标配置比例（各资产类目标权重）                 │  │ │
│  │  │ ├── 配置区间（允许偏离范围）                         │  │ │
│  │  │ ├── 再平衡政策（触发条件与频率）                     │  │ │
│  │  │ └── 配置调整规则（市场环境调整规则）                 │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 战术资产配置政策 (Tactical Allocation Policy)       │  │ │
│  │  │ ├── 战术偏离限制（允许战术偏离范围）                 │  │ │
│  │  │ ├── 战术调整触发（战术调整条件）                     │  │ │
│  │  │ ├── 战术期限限制（战术仓位期限）                     │  │ │
│  │  │ └── 战术风险预算（战术仓位风险预算）                 │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.19.4 风险管理政策层                        │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 风险限额政策 (Risk Limit Policy)                    │  │ │
│  │  │ ├── 单一持仓限额（单股票最大权重）                   │  │ │
│  │  │ ├── 行业集中度限额（行业最大权重）                   │  │ │
│  │  │ ├── 组合风险限额（组合总风险上限）                   │  │ │
│  │  │ └── 杠杆限额（最大杠杆倍数）                         │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 止损政策 (Stop Loss Policy)                         │  │ │
│  │  │ ├── 单股票止损（个股止损线）                         │  │ │
│  │  │ ├── 组合止损（组合回撤止损）                         │  │ │
│  │  │ ├── 策略止损（策略层面止损）                         │  │ │
│  │  │ └── 止损后处理（止损后操作规则）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.19.5 审查与合规层                          │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 定期审查机制 (Periodic Review Mechanism)            │  │ │
│  │  │ ├── 季度审查（季度绩效与配置审查）                   │  │ │
│  │  │ ├── 年度审查（年度IPS全面审查）                      │  │ │
│  │  │ ├── 事件触发审查（重大事件触发审查）                 │  │ │
│  │  │ └── 审查报告生成（审查结果报告）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 合规检查引擎 (Compliance Check Engine)              │  │ │
│  │  │ ├── 投资前合规检查（交易前合规验证）                 │  │ │
│  │  │ ├── 持仓合规检查（持仓合规监控）                     │  │ │
│  │  │ ├── 风险合规检查（风险限额合规）                     │  │ │
│  │  │ └── 违规预警（违规情况预警）                         │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责边界

| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |
|------|---------|------|------|---------|
| **投资目标管理层** | 定义收益与风险目标 | 用户输入 | 目标参数 | 所有模块 |
| **投资约束管理层** | 管理各类约束条件 | 用户输入 | 约束规则 | 合规检查 |
| **资产配置政策层** | 制定配置政策 | 目标参数 | 配置规则 | Layer 11.1 |
| **风险管理政策层** | 制定风险政策 | 风险承受力 | 风险规则 | Layer 11.2 |
| **审查与合规层** | 审查与合规检查 | 组合状态 | 合规报告 | Layer 10 |

---

## 二、核心组件详细设计

### 2.1 投资目标管理层

```python
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np

class ReturnObjectiveType(Enum):
    """收益目标类型"""
    ABSOLUTE = "absolute"       # 绝对收益目标
    RELATIVE = "relative"       # 相对收益目标
    RISK_ADJUSTED = "risk_adjusted"  # 风险调整收益

class RiskToleranceLevel(Enum):
    """风险承受力等级"""
    CONSERVATIVE = "conservative"     # 保守型
    MODERATE = "moderate"             # 稳健型
    BALANCED = "balanced"             # 平衡型
    GROWTH = "growth"                 # 成长型
    AGGRESSIVE = "aggressive"         # 进取型

@dataclass
class ReturnObjective:
    """收益目标"""
    objective_type: ReturnObjectiveType
    target_return: float              # 目标收益率
    benchmark: Optional[str] = None   # 基准（相对收益）
    time_horizon: int = 365           # 时间期限（天）
    priority: int = 1                 # 优先级
    description: str = ""

@dataclass
class RiskTolerance:
    """风险承受力"""
    level: RiskToleranceLevel
    max_drawdown: float               # 最大回撤容忍度
    max_volatility: float             # 最大波动率容忍度
    risk_budget: float                # 风险预算
    var_tolerance: float = 0.05       # VaR容忍度
    description: str = ""

class InvestmentObjectiveManager:
    """投资目标管理器"""
    
    def __init__(self):
        self.return_objectives: List[ReturnObjective] = []
        self.risk_tolerance: Optional[RiskTolerance] = None
    
    def set_return_objective(self, objective: ReturnObjective):
        """设置收益目标"""
        self.return_objectives.append(objective)
    
    def set_risk_tolerance(self, tolerance: RiskTolerance):
        """设置风险承受力"""
        self.risk_tolerance = tolerance
    
    def get_primary_objective(self) -> Optional[ReturnObjective]:
        """获取主要收益目标"""
        if not self.return_objectives:
            return None
        return min(self.return_objectives, key=lambda x: x.priority)
    
    def assess_risk_profile(self, 
                           answers: Dict[str, int]) -> RiskToleranceLevel:
        """评估风险偏好"""
        total_score = sum(answers.values())
        avg_score = total_score / len(answers) if answers else 0
        
        if avg_score < 1.5:
            return RiskToleranceLevel.CONSERVATIVE
        elif avg_score < 2.5:
            return RiskToleranceLevel.MODERATE
        elif avg_score < 3.5:
            return RiskToleranceLevel.BALANCED
        elif avg_score < 4.5:
            return RiskToleranceLevel.GROWTH
        else:
            return RiskToleranceLevel.AGGRESSIVE
    
    def get_default_risk_params(self, 
                               level: RiskToleranceLevel) -> Dict:
        """获取默认风险参数"""
        defaults = {
            RiskToleranceLevel.CONSERVATIVE: {
                'max_drawdown': 0.10,
                'max_volatility': 0.12,
                'risk_budget': 0.05,
                'var_tolerance': 0.03
            },
            RiskToleranceLevel.MODERATE: {
                'max_drawdown': 0.15,
                'max_volatility': 0.18,
                'risk_budget': 0.08,
                'var_tolerance': 0.05
            },
            RiskToleranceLevel.BALANCED: {
                'max_drawdown': 0.20,
                'max_volatility': 0.22,
                'risk_budget': 0.10,
                'var_tolerance': 0.07
            },
            RiskToleranceLevel.GROWTH: {
                'max_drawdown': 0.25,
                'max_volatility': 0.28,
                'risk_budget': 0.12,
                'var_tolerance': 0.10
            },
            RiskToleranceLevel.AGGRESSIVE: {
                'max_drawdown': 0.35,
                'max_volatility': 0.35,
                'risk_budget': 0.15,
                'var_tolerance': 0.15
            }
        }
        return defaults.get(level, defaults[RiskToleranceLevel.BALANCED])
```

### 2.2 投资约束管理层

```python
@dataclass
class LiquidityConstraint:
    """流动性约束"""
    min_cash_ratio: float             # 最低现金比例
    emergency_reserve: float          # 应急资金预留
    max_illiquid_ratio: float         # 非流动性资产上限
    short_term_needs: float           # 短期现金需求

@dataclass
class TimeHorizonConstraint:
    """时间期限约束"""
    investment_horizon: int           # 投资期限（年）
    target_date: Optional[date] = None  # 目标日期
    phase_goals: List[Dict] = field(default_factory=list)  # 阶段性目标

@dataclass
class OtherConstraint:
    """其他约束"""
    tax_considerations: bool          # 税务考虑
    excluded_sectors: List[str] = field(default_factory=list)  # 排除行业
    excluded_stocks: List[str] = field(default_factory=list)   # 排除股票
    esg_requirements: bool = False    # ESG要求
    custom_rules: Dict = field(default_factory=dict)  # 自定义规则

class InvestmentConstraintManager:
    """投资约束管理器"""
    
    def __init__(self):
        self.liquidity_constraint: Optional[LiquidityConstraint] = None
        self.time_horizon_constraint: Optional[TimeHorizonConstraint] = None
        self.other_constraint: Optional[OtherConstraint] = None
    
    def set_liquidity_constraint(self, constraint: LiquidityConstraint):
        """设置流动性约束"""
        self.liquidity_constraint = constraint
    
    def set_time_horizon_constraint(self, constraint: TimeHorizonConstraint):
        """设置时间期限约束"""
        self.time_horizon_constraint = constraint
    
    def set_other_constraint(self, constraint: OtherConstraint):
        """设置其他约束"""
        self.other_constraint = constraint
    
    def check_liquidity(self, 
                       portfolio_value: float,
                       cash_position: float,
                       illiquid_position: float) -> Tuple[bool, str]:
        """检查流动性约束"""
        if not self.liquidity_constraint:
            return True, "无流动性约束"
        
        cash_ratio = cash_position / portfolio_value
        illiquid_ratio = illiquid_position / portfolio_value
        
        if cash_ratio < self.liquidity_constraint.min_cash_ratio:
            return False, f"现金比例{cash_ratio:.2%}低于最低要求{self.liquidity_constraint.min_cash_ratio:.2%}"
        
        if illiquid_ratio > self.liquidity_constraint.max_illiquid_ratio:
            return False, f"非流动性资产比例{illiquid_ratio:.2%}超过上限{self.liquidity_constraint.max_illiquid_ratio:.2%}"
        
        return True, "流动性约束满足"
    
    def check_exclusion(self, 
                       stock_code: str,
                       sector: str) -> Tuple[bool, str]:
        """检查排除约束"""
        if not self.other_constraint:
            return True, "无排除约束"
        
        if stock_code in self.other_constraint.excluded_stocks:
            return False, f"股票{stock_code}在排除列表中"
        
        if sector in self.other_constraint.excluded_sectors:
            return False, f"行业{sector}在排除列表中"
        
        return True, "排除约束满足"
```

### 2.3 资产配置政策层

```python
@dataclass
class AssetClassPolicy:
    """资产类别政策"""
    asset_class: str                  # 资产类别
    target_weight: float              # 目标权重
    min_weight: float                 # 最小权重
    max_weight: float                 # 最大权重
    rebalance_threshold: float        # 再平衡阈值

@dataclass
class RebalancePolicy:
    """再平衡政策"""
    trigger_type: str                 # 'threshold', 'time', 'both'
    threshold: float                  # 偏离阈值
    frequency: int                    # 频率（天）
    method: str                       # 'full', 'partial'
    cost_consideration: bool = True   # 是否考虑成本

class AssetAllocationPolicyManager:
    """资产配置政策管理器"""
    
    def __init__(self):
        self.asset_policies: Dict[str, AssetClassPolicy] = {}
        self.rebalance_policy: Optional[RebalancePolicy] = None
        self.tactical_deviation_limit: float = 0.10
    
    def set_asset_policy(self, policy: AssetClassPolicy):
        """设置资产类别政策"""
        self.asset_policies[policy.asset_class] = policy
    
    def set_rebalance_policy(self, policy: RebalancePolicy):
        """设置再平衡政策"""
        self.rebalance_policy = policy
    
    def get_target_allocation(self) -> Dict[str, float]:
        """获取目标配置"""
        return {
            ac: policy.target_weight 
            for ac, policy in self.asset_policies.items()
        }
    
    def check_allocation_compliance(self,
                                   current_weights: Dict[str, float]) -> List[Dict]:
        """检查配置合规性"""
        violations = []
        
        for asset_class, policy in self.asset_policies.items():
            current = current_weights.get(asset_class, 0)
            
            if current < policy.min_weight:
                violations.append({
                    'type': 'below_min',
                    'asset_class': asset_class,
                    'current': current,
                    'limit': policy.min_weight
                })
            elif current > policy.max_weight:
                violations.append({
                    'type': 'above_max',
                    'asset_class': asset_class,
                    'current': current,
                    'limit': policy.max_weight
                })
        
        return violations
    
    def need_rebalance(self,
                      current_weights: Dict[str, float]) -> bool:
        """判断是否需要再平衡"""
        if not self.rebalance_policy:
            return False
        
        for asset_class, policy in self.asset_policies.items():
            current = current_weights.get(asset_class, 0)
            deviation = abs(current - policy.target_weight)
            
            if deviation > policy.rebalance_threshold:
                return True
        
        return False
```

### 2.4 风险管理政策层

```python
@dataclass
class RiskLimit:
    """风险限额"""
    limit_type: str                   # 'single_stock', 'sector', 'portfolio', 'leverage'
    limit_value: float                # 限额值
    hard_limit: bool = True           # 是否硬性限制
    description: str = ""

@dataclass
class StopLossPolicy:
    """止损政策"""
    single_stock_stop: float          # 个股止损线
    portfolio_stop: float             # 组合止损线
    strategy_stop: float              # 策略止损线
    cooldown_period: int = 30         # 冷却期（天）
    post_stop_action: str = "reduce"  # 'reduce', 'exit', 'hold'

class RiskPolicyManager:
    """风险管理政策管理器"""
    
    def __init__(self):
        self.risk_limits: Dict[str, RiskLimit] = {}
        self.stop_loss_policy: Optional[StopLossPolicy] = None
    
    def set_risk_limit(self, limit: RiskLimit):
        """设置风险限额"""
        self.risk_limits[limit.limit_type] = limit
    
    def set_stop_loss_policy(self, policy: StopLossPolicy):
        """设置止损政策"""
        self.stop_loss_policy = policy
    
    def check_position_limit(self,
                            stock_code: str,
                            weight: float) -> Tuple[bool, str]:
        """检查持仓限额"""
        limit = self.risk_limits.get('single_stock')
        
        if not limit:
            return True, "无持仓限额"
        
        if weight > limit.limit_value:
            if limit.hard_limit:
                return False, f"权重{weight:.2%}超过硬性限额{limit.limit_value:.2%}"
            else:
                return True, f"警告：权重{weight:.2%}超过软限额{limit.limit_value:.2%}"
        
        return True, "持仓限额满足"
    
    def check_sector_limit(self,
                          sector: str,
                          sector_weight: float) -> Tuple[bool, str]:
        """检查行业限额"""
        limit = self.risk_limits.get('sector')
        
        if not limit:
            return True, "无行业限额"
        
        if sector_weight > limit.limit_value:
            if limit.hard_limit:
                return False, f"行业{sector}权重{sector_weight:.2%}超过限额{limit.limit_value:.2%}"
        
        return True, "行业限额满足"
    
    def check_stop_loss(self,
                       stock_code: str,
                       entry_price: float,
                       current_price: float) -> Tuple[bool, str]:
        """检查止损"""
        if not self.stop_loss_policy:
            return False, "无止损政策"
        
        loss_pct = (current_price - entry_price) / entry_price
        
        if loss_pct < -self.stop_loss_policy.single_stock_stop:
            return True, f"触发止损：亏损{abs(loss_pct):.2%}超过止损线{self.stop_loss_policy.single_stock_stop:.2%}"
        
        return False, "未触发止损"
```

### 2.5 审查与合规层

```python
@dataclass
class ReviewSchedule:
    """审查计划"""
    review_type: str                  # 'quarterly', 'annual', 'event'
    next_review_date: date
    last_review_date: Optional[date] = None
    reviewer: str = "self"
    checklist: List[str] = field(default_factory=list)

@dataclass
class ComplianceResult:
    """合规检查结果"""
    check_type: str
    is_compliant: bool
    violations: List[Dict]
    warnings: List[str]
    checked_at: datetime = field(default_factory=datetime.now)

class ReviewComplianceManager:
    """审查与合规管理器"""
    
    def __init__(self):
        self.review_schedules: List[ReviewSchedule] = []
        self.compliance_history: List[ComplianceResult] = []
    
    def create_review_schedule(self, schedule: ReviewSchedule):
        """创建审查计划"""
        self.review_schedules.append(schedule)
    
    def check_due_reviews(self) -> List[ReviewSchedule]:
        """检查到期审查"""
        today = date.today()
        return [
            s for s in self.review_schedules
            if s.next_review_date <= today
        ]
    
    def comprehensive_compliance_check(self,
                                      portfolio: Dict,
                                      objective_manager: InvestmentObjectiveManager,
                                      constraint_manager: InvestmentConstraintManager,
                                      allocation_manager: AssetAllocationPolicyManager,
                                      risk_manager: RiskPolicyManager) -> ComplianceResult:
        """综合合规检查"""
        violations = []
        warnings = []
        
        if objective_manager.risk_tolerance:
            max_dd = objective_manager.risk_tolerance.max_drawdown
            if portfolio.get('current_drawdown', 0) > max_dd:
                violations.append({
                    'type': 'max_drawdown_exceeded',
                    'current': portfolio.get('current_drawdown'),
                    'limit': max_dd
                })
        
        if constraint_manager.liquidity_constraint:
            cash_ratio = portfolio.get('cash_ratio', 0)
            min_cash = constraint_manager.liquidity_constraint.min_cash_ratio
            if cash_ratio < min_cash:
                violations.append({
                    'type': 'liquidity_shortage',
                    'current': cash_ratio,
                    'required': min_cash
                })
        
        if allocation_manager.asset_policies:
            weights = portfolio.get('weights', {})
            allocation_violations = allocation_manager.check_allocation_compliance(weights)
            violations.extend(allocation_violations)
        
        if risk_manager.stop_loss_policy:
            positions = portfolio.get('positions', {})
            for stock, pos in positions.items():
                triggered, msg = risk_manager.check_stop_loss(
                    stock, pos.get('entry_price'), pos.get('current_price')
                )
                if triggered:
                    warnings.append(f"{stock}: {msg}")
        
        result = ComplianceResult(
            check_type='comprehensive',
            is_compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings
        )
        
        self.compliance_history.append(result)
        return result
    
    def generate_review_report(self,
                              portfolio: Dict,
                              compliance_result: ComplianceResult) -> str:
        """生成审查报告"""
        report = "投资政策声明审查报告\n"
        report += "=" * 50 + "\n\n"
        report += f"审查日期: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        report += "合规状态:\n"
        if compliance_result.is_compliant:
            report += "  ✅ 完全合规\n"
        else:
            report += f"  ❌ 存在{len(compliance_result.violations)}项违规\n"
        
        if compliance_result.violations:
            report += "\n违规项目:\n"
            for v in compliance_result.violations:
                report += f"  - {v['type']}: {v}\n"
        
        if compliance_result.warnings:
            report += "\n警告信息:\n"
            for w in compliance_result.warnings:
                report += f"  - {w}\n"
        
        return report
```

---

## 三、投资政策声明(IPS)模板

### 3.1 IPS文档结构

```python
@dataclass
class InvestmentPolicyStatement:
    """投资政策声明"""
    ips_id: str
    investor_name: str
    created_date: date
    last_updated: date
    
    # 投资目标
    return_objectives: List[ReturnObjective]
    risk_tolerance: RiskTolerance
    
    # 投资约束
    liquidity_constraint: LiquidityConstraint
    time_horizon_constraint: TimeHorizonConstraint
    other_constraints: OtherConstraint
    
    # 资产配置政策
    asset_allocation_policy: Dict[str, AssetClassPolicy]
    rebalance_policy: RebalancePolicy
    
    # 风险管理政策
    risk_limits: Dict[str, RiskLimit]
    stop_loss_policy: StopLossPolicy
    
    # 审查安排
    review_frequency: str
    next_review_date: date
    
    # 签署
    approved_by: str
    approved_date: date

class IPSGenerator:
    """IPS生成器"""
    
    def __init__(self):
        self.ips_counter = 0
    
    def generate_ips(self,
                    investor_name: str,
                    objective_manager: InvestmentObjectiveManager,
                    constraint_manager: InvestmentConstraintManager,
                    allocation_manager: AssetAllocationPolicyManager,
                    risk_manager: RiskPolicyManager) -> InvestmentPolicyStatement:
        """生成IPS文档"""
        self.ips_counter += 1
        
        return InvestmentPolicyStatement(
            ips_id=f"IPS_{self.ips_counter:06d}",
            investor_name=investor_name,
            created_date=date.today(),
            last_updated=date.today(),
            return_objectives=objective_manager.return_objectives,
            risk_tolerance=objective_manager.risk_tolerance,
            liquidity_constraint=constraint_manager.liquidity_constraint,
            time_horizon_constraint=constraint_manager.time_horizon_constraint,
            other_constraints=constraint_manager.other_constraint,
            asset_allocation_policy=allocation_manager.asset_policies,
            rebalance_policy=allocation_manager.rebalance_policy,
            risk_limits=risk_manager.risk_limits,
            stop_loss_policy=risk_manager.stop_loss_policy,
            review_frequency='quarterly',
            next_review_date=date.today(),
            approved_by=investor_name,
            approved_date=date.today()
        )
    
    def export_ips_document(self, ips: InvestmentPolicyStatement) -> str:
        """导出IPS文档"""
        doc = f"""
投资政策声明 (Investment Policy Statement)
{'=' * 60}

文档编号: {ips.ips_id}
投资者: {ips.investor_name}
创建日期: {ips.created_date}
最后更新: {ips.last_updated}

一、投资目标
{'─' * 40}

1. 收益目标:
"""
        for obj in ips.return_objectives:
            doc += f"   - {obj.objective_type.value}: {obj.target_return:.2%}\n"
        
        doc += f"""
2. 风险承受力:
   - 等级: {ips.risk_tolerance.level.value}
   - 最大回撤容忍: {ips.risk_tolerance.max_drawdown:.2%}
   - 最大波动率容忍: {ips.risk_tolerance.max_volatility:.2%}

二、投资约束
{'─' * 40}

1. 流动性约束:
   - 最低现金比例: {ips.liquidity_constraint.min_cash_ratio:.2%}
   - 应急资金预留: ¥{ips.liquidity_constraint.emergency_reserve:,.2f}

2. 时间期限约束:
   - 投资期限: {ips.time_horizon_constraint.investment_horizon}年

三、资产配置政策
{'─' * 40}

"""
        for asset_class, policy in ips.asset_allocation_policy.items():
            doc += f"   {asset_class}: {policy.target_weight:.2%} ({policy.min_weight:.2%}-{policy.max_weight:.2%})\n"
        
        doc += f"""
四、风险管理政策
{'─' * 40}

1. 风险限额:
"""
        for limit_type, limit in ips.risk_limits.items():
            doc += f"   - {limit_type}: {limit.limit_value:.2%}\n"
        
        doc += f"""
2. 止损政策:
   - 个股止损: {ips.stop_loss_policy.single_stock_stop:.2%}
   - 组合止损: {ips.stop_loss_policy.portfolio_stop:.2%}

五、审查安排
{'─' * 40}

   - 审查频率: {ips.review_frequency}
   - 下次审查: {ips.next_review_date}

六、签署确认
{'─' * 40}

   批准人: {ips.approved_by}
   批准日期: {ips.approved_date}

{'=' * 60}
本投资政策声明是投资决策的重要指导文件，应定期审查更新。
"""
        return doc
```

---

## 四、实施路径

### Phase 1: 核心定义（3天）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 投资目标管理 | 1天 | InvestmentObjectiveManager |
| 投资约束管理 | 1天 | InvestmentConstraintManager |
| IPS生成器 | 1天 | IPSGenerator |

### Phase 2: 政策管理（2天）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 资产配置政策 | 1天 | AssetAllocationPolicyManager |
| 风险管理政策 | 1天 | RiskPolicyManager |

### Phase 3: 合规审查（2天）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 合规检查引擎 | 1天 | ReviewComplianceManager |
| 审查报告生成 | 1天 | 报告生成功能 |

---

## 五、相关文档

| 文档 | 说明 |
|------|------|
| [BLUEPRINT.md](./BLUEPRINT.md) | Layer 11主蓝图 |
| [INVESTMENT_CONSTRAINT_BLUEPRINT.md](./INVESTMENT_CONSTRAINT_BLUEPRINT.md) | 投资限制管理系统 |
| [RISK_BUDGET_BLUEPRINT.md](./CAPITAL_ALLOCATION_BLUEPRINT.md) | 风险预算分配系统 |

---

**版本**: v1.0 | **更新**: 2026-04-06 | **状态**: ✅ 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Ips Management
- **模块ID**: IPS_MANAGEMENT_001
- **蓝图文档**: [IPS_MANAGEMENT_BLUEPRINT.md](11_STRATEGIC_DECISION\IPS_MANAGEMENT_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: Layer 11.19 - 投资政策声明管理系统
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Ips Management** | Layer 11.19 - 投资政策声明管理系统 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
