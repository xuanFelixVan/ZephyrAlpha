---
module_id: MULTISTRATEGYCOORDINATIONBL_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
layer: Layer 3 (策略层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
responsibility:
  - 蓝图设计、架构规划

---
---

﻿---
module_id: MULTI_STRATEGY_COORDINATION_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 11.18 - 多策略协调系统
compliance_level: 专业标准
reference_models: ["Citadel Multi-Strategy Framework", "Two Sigma Strategy Coordination", "Millennium Platform"]
open_source_solution: "自研核心 + skfolio辅助"
priority: P0
---

# 多策略协调系统蓝图
> **核心职责**: Multi Strategy Coordination蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Multi Strategy Coordination蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


## 📋 文档职责说明

### 核心职责

本文档是**多策略协调系统蓝图，负责策略信号冲突解决和资金协调**。

### 职责边界

**负责**：
- ✅ 策略信号冲突解决（信号优先级判断）
- ✅ 策略资金协调（跨策略资金分配）
- ✅ 策略风险协调（跨策略风险控制）
- ✅ 协调报告生成（协调决策报告）

**不负责**：
- ❌ 资产配置决策（由战略资产配置模块负责）
- ❌ 风险预算分配（由风险预算分配模块负责）
- ❌ 具体交易执行（由Layer 6组合优化层负责）

### 对接模块

**上游模块**：
- Layer 5 策略层
- Layer 10 质量保证层

**下游模块**：
- Layer 6 组合优化层
- Layer 7 风险管理层

---
> **版本**: v1.0
> **创建日期**: 2026-04-06
> **优先级**: 🔴 P0 - 必须实施
> **开源方案**: 自研核心逻辑
> **目标**: 构建多策略信号协调系统，避免信号冲突，优化资金使用

---

## 📋 执行摘要

### 核心定位

多策略协调系统是Layer 11战略决策层的**信号协调中枢**，负责：
- 多策略信号冲突检测与解决
- 信号强度加权与优先级排序
- 跨策略资金竞争协调
- 组合层面风险评估与控制

### 专业价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |
|---------|-------------|-------------|---------|
| **信号冲突解决** | 专业协调团队 | 自动化冲突检测引擎 | ⭐⭐⭐⭐⭐ |
| **资金竞争协调** | 资本配置委员会 | 动态资金分配算法 | ⭐⭐⭐⭐⭐ |
| **风险预算协调** | 风险管理委员会 | 自动化风险预算系统 | ⭐⭐⭐⭐ |
| **执行优先级** | 交易台协调 | 智能优先级排序 | ⭐⭐⭐⭐ |

**综合价值评级**: ⭐⭐⭐⭐⭐ (5/5) - **必须实施**

---

## 一、架构设计

### 1.1 系统整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│          多策略协调系统架构 (Multi-Strategy Coordination)         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.18.1 信号收集与标准化层                     │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 信号收集器 (Signal Collector)                       │  │ │
│  │  │ ├── 策略信号接入（多策略信号接口）                   │  │ │
│  │  │ ├── 信号格式标准化（统一信号格式）                   │  │ │
│  │  │ ├── 信号时间戳对齐（时间对齐处理）                   │  │ │
│  │  │ └── 信号完整性检查（信号有效性验证）                 │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 信号标准化器 (Signal Normalizer)                    │  │ │
│  │  │ ├── 方向标准化（买入/卖出/持有）                     │  │ │
│  │  │ ├── 强度标准化（0-1信号强度）                        │  │ │
│  │  │ ├── 置信度标准化（信号置信度）                       │  │ │
│  │  │ └── 时间尺度标准化（信号有效期）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.18.2 冲突检测与解决层                       │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 冲突检测器 (Conflict Detector)                      │  │ │
│  │  │ ├── 方向冲突检测（同标的不同方向信号）               │  │ │
│  │  │ ├── 资金冲突检测（资金需求超过可用）                 │  │ │
│  │  │ ├── 风险冲突检测（风险预算超限）                     │  │ │
│  │  │ └── 约束冲突检测（违反投资约束）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 冲突解决器 (Conflict Resolver)                      │  │ │
│  │  │ ├── 信号强度加权（按策略历史表现加权）               │  │ │
│  │  │ ├── 置信度优先（高置信度信号优先）                   │  │ │
│  │  │ ├── 时间优先原则（先到先得或最新优先）               │  │ │
│  │  │ ├── 风险调整决策（风险调整后决策）                   │  │ │
│  │  │ └── 人工介入机制（复杂冲突人工决策）                 │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.18.3 资金协调层                            │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 资金需求评估器 (Capital Demand Estimator)           │  │ │
│  │  │ ├── 单策略资金需求（各策略资金需求计算）             │  │ │
│  │  │ ├── 总资金需求汇总（汇总所有策略需求）               │  │ │
│  │  │ ├── 资金可用性检查（可用资金评估）                   │  │ │
│  │  │ └── 资金缺口分析（需求与可用差额）                   │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 资金分配器 (Capital Allocator)                      │  │ │
│  │  │ ├── 按优先级分配（策略优先级排序）                   │  │ │
│  │  │ ├── 按风险预算分配（风险预算比例分配）               │  │ │
│  │  │ ├── 按预期收益分配（预期收益比例分配）               │  │ │
│  │  │ ├── 动态调整机制（市场变化动态调整）                 │  │ │
│  │  │ └── 资金预留机制（预留现金缓冲）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.18.4 执行协调层                            │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 执行优先级排序 (Execution Priority Ranking)         │  │ │
│  │  │ ├── 紧急程度排序（信号紧急程度）                     │  │ │
│  │  │ ├── 信号强度排序（信号强弱排序）                     │  │ │
│  │  │ ├── 策略重要性排序（策略优先级）                     │  │ │
│  │  │ └── 风险调整排序（风险调整后排序）                   │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 执行批处理 (Execution Batching)                     │  │ │
│  │  │ ├── 同向信号合并（同方向信号合并执行）               │  │ │
│  │  │ ├── 批量执行优化（减少交易次数）                     │  │ │
│  │  │ ├── 执行时间窗口（执行时间优化）                     │  │ │
│  │  │ └── 执行状态跟踪（执行进度监控）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.18.5 组合风险监控层                        │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 组合风险评估 (Portfolio Risk Assessment)            │  │ │
│  │  │ ├── 总体风险计算（组合整体风险）                     │  │ │
│  │  │ ├── 策略风险贡献（各策略风险贡献）                   │  │ │
│  │  │ ├── 相关性风险（策略间相关性风险）                   │  │ │
│  │  │ └── 集中度风险（持仓集中度风险）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 风险预警系统 (Risk Alert System)                    │  │ │
│  │  │ ├── 风险预算超限预警（风险预算监控）                 │  │ │
│  │  │ ├── 策略风险异常预警（策略风险异常）                 │  │ │
│  │  │ ├── 相关性突变预警（策略相关性变化）                 │  │ │
│  │  │ └── 组合风险报告（风险状态报告）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责边界

| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |
|------|---------|------|------|---------|
| **信号收集标准化层** | 信号收集、格式标准化 | 多策略原始信号 | 标准化信号 | 冲突检测层 |
| **冲突检测解决层** | 冲突检测、冲突解决 | 标准化信号 | 解决后信号 | 资金协调层 |
| **资金协调层** | 资金评估、资金分配 | 解决后信号 | 资金分配方案 | 执行协调层 |
| **执行协调层** | 优先级排序、批处理 | 资金分配方案 | 执行指令 | Layer 5 |
| **组合风险监控层** | 风险评估、风险预警 | 组合状态 | 风险报告 | Layer 11.2 |

---

## 二、核心组件详细设计

### 2.1 信号收集与标准化层

```python
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np

class SignalDirection(Enum):
    """信号方向"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"

class SignalType(Enum):
    """信号类型"""
    ENTRY = "entry"       # 入场信号
    EXIT = "exit"         # 出场信号
    ADJUST = "adjust"     # 调仓信号
    HEDGE = "hedge"       # 对冲信号

@dataclass
class StandardizedSignal:
    """标准化信号"""
    signal_id: str
    strategy_id: str
    stock_code: str
    direction: SignalDirection
    signal_type: SignalType
    strength: float          # 0.0 - 1.0
    confidence: float        # 0.0 - 1.0
    target_weight: float     # 目标权重
    target_price: Optional[float] = None
    valid_until: Optional[datetime] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

@dataclass
class RawSignal:
    """原始信号"""
    strategy_id: str
    stock_code: str
    direction: str
    strength: float
    metadata: Dict = field(default_factory=dict)

class SignalCollector:
    """信号收集器"""
    
    def __init__(self):
        self.raw_signals: List[RawSignal] = []
        self.strategies: Dict[str, Dict] = {}
        
    def register_strategy(self, 
                         strategy_id: str,
                         strategy_info: Dict):
        """注册策略"""
        self.strategies[strategy_id] = strategy_info
    
    def receive_signal(self, signal: RawSignal):
        """接收信号"""
        self.raw_signals.append(signal)
    
    def receive_signals(self, signals: List[RawSignal]):
        """批量接收信号"""
        self.raw_signals.extend(signals)
    
    def get_signals_by_strategy(self, 
                               strategy_id: str) -> List[RawSignal]:
        """按策略获取信号"""
        return [s for s in self.raw_signals if s.strategy_id == strategy_id]
    
    def get_signals_by_stock(self, 
                            stock_code: str) -> List[RawSignal]:
        """按股票获取信号"""
        return [s for s in self.raw_signals if s.stock_code == stock_code]
    
    def clear_signals(self):
        """清空信号"""
        self.raw_signals = []

class SignalNormalizer:
    """信号标准化器"""
    
    def __init__(self):
        self.signal_counter = 0
    
    def normalize_direction(self, direction: str) -> SignalDirection:
        """标准化方向"""
        direction_map = {
            'buy': SignalDirection.BUY,
            'long': SignalDirection.BUY,
            'sell': SignalDirection.SELL,
            'short': SignalDirection.SELL,
            'hold': SignalDirection.HOLD,
            'neutral': SignalDirection.HOLD,
            'close': SignalDirection.CLOSE,
            'exit': SignalDirection.CLOSE
        }
        return direction_map.get(direction.lower(), SignalDirection.HOLD)
    
    def normalize_strength(self, strength: float) -> float:
        """标准化强度"""
        return max(0.0, min(1.0, abs(strength)))
    
    def normalize_confidence(self, confidence: float) -> float:
        """标准化置信度"""
        return max(0.0, min(1.0, confidence))
    
    def normalize_signal(self, 
                        raw_signal: RawSignal,
                        strategy_info: Dict) -> StandardizedSignal:
        """标准化信号"""
        self.signal_counter += 1
        
        direction = self.normalize_direction(raw_signal.direction)
        strength = self.normalize_strength(raw_signal.strength)
        
        base_confidence = strategy_info.get('base_confidence', 0.5)
        confidence = self.normalize_confidence(
            raw_signal.metadata.get('confidence', base_confidence)
        )
        
        target_weight = raw_signal.metadata.get('target_weight', 0.0)
        
        return StandardizedSignal(
            signal_id=f"SIG_{self.signal_counter:08d}",
            strategy_id=raw_signal.strategy_id,
            stock_code=raw_signal.stock_code,
            direction=direction,
            signal_type=SignalType(
                raw_signal.metadata.get('signal_type', 'entry')
            ),
            strength=strength,
            confidence=confidence,
            target_weight=target_weight,
            target_price=raw_signal.metadata.get('target_price'),
            valid_until=raw_signal.metadata.get('valid_until'),
            metadata=raw_signal.metadata
        )
    
    def normalize_all(self, 
                     raw_signals: List[RawSignal],
                     strategies: Dict[str, Dict]) -> List[StandardizedSignal]:
        """批量标准化"""
        normalized = []
        for raw in raw_signals:
            strategy_info = strategies.get(raw.strategy_id, {})
            normalized.append(self.normalize_signal(raw, strategy_info))
        return normalized
```

### 2.2 冲突检测与解决层

```python
@dataclass
class Conflict:
    """冲突记录"""
    conflict_id: str
    conflict_type: str      # 'direction', 'capital', 'risk', 'constraint'
    involved_signals: List[str]  # signal_ids
    description: str
    severity: str           # 'low', 'medium', 'high', 'critical'
    detected_at: datetime = field(default_factory=datetime.now)

@dataclass
class ConflictResolution:
    """冲突解决方案"""
    resolution_id: str
    conflict_id: str
    resolution_method: str
    winning_signal_id: str
    losing_signal_ids: List[str]
    resolution_reason: str
    resolved_at: datetime = field(default_factory=datetime.now)

class ConflictDetector:
    """冲突检测器"""
    
    def __init__(self):
        self.conflicts: List[Conflict] = []
        self.conflict_counter = 0
    
    def detect_direction_conflicts(self,
                                  signals: List[StandardizedSignal]) -> List[Conflict]:
        """检测方向冲突"""
        conflicts = []
        
        by_stock = {}
        for sig in signals:
            if sig.stock_code not in by_stock:
                by_stock[sig.stock_code] = []
            by_stock[sig.stock_code].append(sig)
        
        for stock_code, stock_signals in by_stock.items():
            if len(stock_signals) < 2:
                continue
            
            directions = set(s.direction for s in stock_signals)
            
            if SignalDirection.BUY in directions and SignalDirection.SELL in directions:
                self.conflict_counter += 1
                conflict = Conflict(
                    conflict_id=f"CONF_{self.conflict_counter:06d}",
                    conflict_type='direction',
                    involved_signals=[s.signal_id for s in stock_signals],
                    description=f"股票{stock_code}存在买入和卖出信号冲突",
                    severity='high'
                )
                conflicts.append(conflict)
                self.conflicts.append(conflict)
        
        return conflicts
    
    def detect_capital_conflicts(self,
                                signals: List[StandardizedSignal],
                                available_capital: float) -> List[Conflict]:
        """检测资金冲突"""
        conflicts = []
        
        total_demand = sum(
            abs(s.target_weight) * available_capital 
            for s in signals if s.direction in [SignalDirection.BUY, SignalDirection.SELL]
        )
        
        if total_demand > available_capital:
            self.conflict_counter += 1
            conflict = Conflict(
                conflict_id=f"CONF_{self.conflict_counter:06d}",
                conflict_type='capital',
                involved_signals=[s.signal_id for s in signals],
                description=f"资金需求{total_demand:.2f}超过可用资金{available_capital:.2f}",
                severity='medium'
            )
            conflicts.append(conflict)
            self.conflicts.append(conflict)
        
        return conflicts
    
    def detect_all_conflicts(self,
                            signals: List[StandardizedSignal],
                            available_capital: float,
                            risk_budget: float) -> List[Conflict]:
        """检测所有冲突"""
        all_conflicts = []
        all_conflicts.extend(self.detect_direction_conflicts(signals))
        all_conflicts.extend(self.detect_capital_conflicts(signals, available_capital))
        return all_conflicts

class ConflictResolver:
    """冲突解决器"""
    
    def __init__(self):
        self.resolutions: List[ConflictResolution] = []
        self.resolution_counter = 0
        self.strategy_weights: Dict[str, float] = {}
    
    def set_strategy_weights(self, weights: Dict[str, float]):
        """设置策略权重"""
        self.strategy_weights = weights
    
    def resolve_by_strength(self,
                           signals: List[StandardizedSignal]) -> StandardizedSignal:
        """按信号强度解决"""
        return max(signals, key=lambda s: s.strength)
    
    def resolve_by_confidence(self,
                             signals: List[StandardizedSignal]) -> StandardizedSignal:
        """按置信度解决"""
        return max(signals, key=lambda s: s.confidence)
    
    def resolve_by_strategy_weight(self,
                                   signals: List[StandardizedSignal]) -> StandardizedSignal:
        """按策略权重解决"""
        def get_weighted_score(sig: StandardizedSignal) -> float:
            strategy_weight = self.strategy_weights.get(sig.strategy_id, 1.0)
            return sig.strength * sig.confidence * strategy_weight
        
        return max(signals, key=get_weighted_score)
    
    def resolve_conflict(self,
                        conflict: Conflict,
                        signals: List[StandardizedSignal],
                        method: str = 'weighted') -> ConflictResolution:
        """解决冲突"""
        self.resolution_counter += 1
        
        involved_signals = [s for s in signals if s.signal_id in conflict.involved_signals]
        
        if method == 'strength':
            winner = self.resolve_by_strength(involved_signals)
        elif method == 'confidence':
            winner = self.resolve_by_confidence(involved_signals)
        else:
            winner = self.resolve_by_strategy_weight(involved_signals)
        
        losers = [s.signal_id for s in involved_signals if s.signal_id != winner.signal_id]
        
        resolution = ConflictResolution(
            resolution_id=f"RES_{self.resolution_counter:06d}",
            conflict_id=conflict.conflict_id,
            resolution_method=method,
            winning_signal_id=winner.signal_id,
            losing_signal_ids=losers,
            resolution_reason=f"使用{method}方法选择信号{winner.signal_id}"
        )
        
        self.resolutions.append(resolution)
        return resolution
    
    def resolve_all_conflicts(self,
                             conflicts: List[Conflict],
                             signals: List[StandardizedSignal],
                             method: str = 'weighted') -> List[ConflictResolution]:
        """解决所有冲突"""
        return [
            self.resolve_conflict(c, signals, method) 
            for c in conflicts
        ]
```

### 2.3 资金协调层

```python
@dataclass
class CapitalDemand:
    """资金需求"""
    strategy_id: str
    signal_id: str
    stock_code: str
    required_capital: float
    priority: int
    expected_return: float
    risk_contribution: float

@dataclass
class CapitalAllocation:
    """资金分配"""
    allocation_id: str
    strategy_id: str
    signal_id: str
    stock_code: str
    allocated_capital: float
    allocated_weight: float
    allocation_reason: str
    allocated_at: datetime = field(default_factory=datetime.now)

class CapitalDemandEstimator:
    """资金需求评估器"""
    
    def __init__(self):
        self.demands: List[CapitalDemand] = []
    
    def estimate_signal_demand(self,
                              signal: StandardizedSignal,
                              total_capital: float,
                              strategy_priority: int = 1,
                              expected_return: float = 0.0,
                              risk_contribution: float = 0.0) -> CapitalDemand:
        """评估单信号资金需求"""
        required = abs(signal.target_weight) * total_capital
        
        return CapitalDemand(
            strategy_id=signal.strategy_id,
            signal_id=signal.signal_id,
            stock_code=signal.stock_code,
            required_capital=required,
            priority=strategy_priority,
            expected_return=expected_return,
            risk_contribution=risk_contribution
        )
    
    def estimate_all_demands(self,
                            signals: List[StandardizedSignal],
                            total_capital: float,
                            strategy_priorities: Dict[str, int],
                            expected_returns: Dict[str, float]) -> List[CapitalDemand]:
        """评估所有资金需求"""
        self.demands = []
        
        for sig in signals:
            priority = strategy_priorities.get(sig.strategy_id, 1)
            exp_ret = expected_returns.get(sig.signal_id, 0.0)
            
            demand = self.estimate_signal_demand(
                sig, total_capital, priority, exp_ret
            )
            self.demands.append(demand)
        
        return self.demands
    
    def get_total_demand(self) -> float:
        """获取总资金需求"""
        return sum(d.required_capital for d in self.demands)
    
    def get_capital_gap(self, available: float) -> float:
        """获取资金缺口"""
        return max(0, self.get_total_demand() - available)

class CapitalAllocator:
    """资金分配器"""
    
    def __init__(self, reserve_ratio: float = 0.1):
        self.reserve_ratio = reserve_ratio
        self.allocations: List[CapitalAllocation] = []
        self.allocation_counter = 0
    
    def allocate_by_priority(self,
                            demands: List[CapitalDemand],
                            available_capital: float) -> List[CapitalAllocation]:
        """按优先级分配"""
        self.allocations = []
        
        investable = available_capital * (1 - self.reserve_ratio)
        remaining = investable
        
        sorted_demands = sorted(demands, key=lambda d: d.priority)
        
        for demand in sorted_demands:
            if remaining <= 0:
                break
            
            allocated = min(demand.required_capital, remaining)
            remaining -= allocated
            
            self.allocation_counter += 1
            allocation = CapitalAllocation(
                allocation_id=f"ALLOC_{self.allocation_counter:06d}",
                strategy_id=demand.strategy_id,
                signal_id=demand.signal_id,
                stock_code=demand.stock_code,
                allocated_capital=allocated,
                allocated_weight=allocated / available_capital,
                allocation_reason="按优先级分配"
            )
            self.allocations.append(allocation)
        
        return self.allocations
    
    def allocate_proportionally(self,
                               demands: List[CapitalDemand],
                               available_capital: float) -> List[CapitalAllocation]:
        """按比例分配"""
        self.allocations = []
        
        investable = available_capital * (1 - self.reserve_ratio)
        total_demand = sum(d.required_capital for d in demands)
        
        if total_demand == 0:
            return self.allocations
        
        scale_factor = min(1.0, investable / total_demand)
        
        for demand in demands:
            allocated = demand.required_capital * scale_factor
            
            self.allocation_counter += 1
            allocation = CapitalAllocation(
                allocation_id=f"ALLOC_{self.allocation_counter:06d}",
                strategy_id=demand.strategy_id,
                signal_id=demand.signal_id,
                stock_code=demand.stock_code,
                allocated_capital=allocated,
                allocated_weight=allocated / available_capital,
                allocation_reason="按比例分配"
            )
            self.allocations.append(allocation)
        
        return self.allocations
    
    def allocate_by_risk_budget(self,
                               demands: List[CapitalDemand],
                               available_capital: float,
                               risk_budgets: Dict[str, float]) -> List[CapitalAllocation]:
        """按风险预算分配"""
        self.allocations = []
        
        investable = available_capital * (1 - self.reserve_ratio)
        
        total_risk_budget = sum(risk_budgets.values())
        
        for demand in demands:
            strategy_budget = risk_budgets.get(demand.strategy_id, 0)
            budget_ratio = strategy_budget / total_risk_budget if total_risk_budget > 0 else 0
            
            allocated = investable * budget_ratio
            
            self.allocation_counter += 1
            allocation = CapitalAllocation(
                allocation_id=f"ALLOC_{self.allocation_counter:06d}",
                strategy_id=demand.strategy_id,
                signal_id=demand.signal_id,
                stock_code=demand.stock_code,
                allocated_capital=min(allocated, demand.required_capital),
                allocated_weight=allocated / available_capital,
                allocation_reason="按风险预算分配"
            )
            self.allocations.append(allocation)
        
        return self.allocations
```

### 2.4 执行协调层

```python
@dataclass
class ExecutionOrder:
    """执行指令"""
    order_id: str
    signal_id: str
    strategy_id: str
    stock_code: str
    direction: SignalDirection
    target_weight: float
    priority_score: float
    execution_batch: int
    status: str = 'pending'
    created_at: datetime = field(default_factory=datetime.now)

class ExecutionCoordinator:
    """执行协调器"""
    
    def __init__(self):
        self.orders: List[ExecutionOrder] = []
        self.order_counter = 0
    
    def calculate_priority_score(self,
                                signal: StandardizedSignal,
                                allocation: CapitalAllocation,
                                strategy_priority: int = 1) -> float:
        """计算优先级分数"""
        urgency = signal.metadata.get('urgency', 0.5)
        
        score = (
            signal.strength * 0.3 +
            signal.confidence * 0.2 +
            allocation.allocated_weight * 0.2 +
            (1 / strategy_priority) * 0.15 +
            urgency * 0.15
        )
        
        return score
    
    def rank_by_priority(self,
                        signals: List[StandardizedSignal],
                        allocations: List[CapitalAllocation],
                        strategy_priorities: Dict[str, int]) -> List[ExecutionOrder]:
        """按优先级排序"""
        self.orders = []
        
        allocation_map = {a.signal_id: a for a in allocations}
        
        orders_with_scores = []
        for sig in signals:
            if sig.signal_id not in allocation_map:
                continue
            
            alloc = allocation_map[sig.signal_id]
            priority = strategy_priorities.get(sig.strategy_id, 1)
            score = self.calculate_priority_score(sig, alloc, priority)
            
            self.order_counter += 1
            order = ExecutionOrder(
                order_id=f"ORD_{self.order_counter:06d}",
                signal_id=sig.signal_id,
                strategy_id=sig.strategy_id,
                stock_code=sig.stock_code,
                direction=sig.direction,
                target_weight=alloc.allocated_weight,
                priority_score=score
            )
            orders_with_scores.append(order)
        
        self.orders = sorted(orders_with_scores, 
                            key=lambda o: o.priority_score, 
                            reverse=True)
        
        return self.orders
    
    def batch_orders(self,
                    orders: List[ExecutionOrder],
                    batch_size: int = 5) -> List[ExecutionOrder]:
        """批处理指令"""
        for i, order in enumerate(orders):
            order.execution_batch = i // batch_size
        
        return orders
    
    def merge_same_direction_orders(self,
                                   orders: List[ExecutionOrder]) -> List[ExecutionOrder]:
        """合并同向指令"""
        merged = {}
        
        for order in orders:
            key = (order.stock_code, order.direction)
            
            if key not in merged:
                merged[key] = order
            else:
                existing = merged[key]
                existing.target_weight += order.target_weight
                existing.priority_score = max(
                    existing.priority_score, 
                    order.priority_score
                )
        
        return list(merged.values())
```

### 2.5 组合风险监控层

```python
@dataclass
class PortfolioRiskMetrics:
    """组合风险指标"""
    total_risk: float
    strategy_risk_contributions: Dict[str, float]
    correlation_risk: float
    concentration_risk: float
    var_95: float
    max_drawdown_risk: float
    calculated_at: datetime = field(default_factory=datetime.now)

class PortfolioRiskMonitor:
    """组合风险监控器"""
    
    def __init__(self):
        self.risk_history: List[PortfolioRiskMetrics] = []
    
    def calculate_strategy_risk_contribution(self,
                                            positions: Dict[str, Dict],
                                            strategy_ids: List[str]) -> Dict[str, float]:
        """计算策略风险贡献"""
        contributions = {}
        
        for strategy_id in strategy_ids:
            strategy_positions = {
                k: v for k, v in positions.items()
                if v.get('strategy_id') == strategy_id
            }
            
            if not strategy_positions:
                contributions[strategy_id] = 0.0
                continue
            
            strategy_weight = sum(
                abs(p.get('weight', 0)) for p in strategy_positions.values()
            )
            contributions[strategy_id] = strategy_weight
        
        total = sum(contributions.values())
        if total > 0:
            contributions = {k: v/total for k, v in contributions.items()}
        
        return contributions
    
    def calculate_concentration_risk(self,
                                    positions: Dict[str, Dict]) -> float:
        """计算集中度风险"""
        weights = [abs(p.get('weight', 0)) for p in positions.values()]
        
        if not weights:
            return 0.0
        
        herfindahl = sum(w**2 for w in weights)
        
        n = len(weights)
        max_herfindahl = 1.0
        min_herfindahl = 1.0 / n
        
        if max_herfindahl == min_herfindahl:
            return 0.0
        
        normalized = (herfindahl - min_herfindahl) / (max_herfindahl - min_herfindahl)
        
        return normalized
    
    def calculate_correlation_risk(self,
                                  strategy_returns: Dict[str, pd.Series]) -> float:
        """计算相关性风险"""
        if len(strategy_returns) < 2:
            return 0.0
        
        returns_df = pd.DataFrame(strategy_returns)
        corr_matrix = returns_df.corr()
        
        n = len(corr_matrix)
        if n < 2:
            return 0.0
        
        upper_triangle = corr_matrix.values[np.triu_indices(n, k=1)]
        
        if len(upper_triangle) == 0:
            return 0.0
        
        avg_abs_corr = np.mean(np.abs(upper_triangle))
        
        return avg_abs_corr
    
    def assess_portfolio_risk(self,
                             positions: Dict[str, Dict],
                             strategy_returns: Dict[str, pd.Series],
                             strategy_ids: List[str]) -> PortfolioRiskMetrics:
        """评估组合风险"""
        strategy_contrib = self.calculate_strategy_risk_contribution(
            positions, strategy_ids
        )
        
        concentration = self.calculate_concentration_risk(positions)
        
        correlation = self.calculate_correlation_risk(strategy_returns)
        
        total_risk = (
            sum(strategy_contrib.values()) * 0.4 +
            concentration * 0.3 +
            correlation * 0.3
        )
        
        metrics = PortfolioRiskMetrics(
            total_risk=total_risk,
            strategy_risk_contributions=strategy_contrib,
            correlation_risk=correlation,
            concentration_risk=concentration,
            var_95=0.0,
            max_drawdown_risk=0.0
        )
        
        self.risk_history.append(metrics)
        
        return metrics
```

---

## 三、核心协调流程

### 3.1 信号协调主流程

```python
class MultiStrategyCoordinator:
    """多策略协调器"""
    
    def __init__(self,
                 signal_collector: SignalCollector,
                 signal_normalizer: SignalNormalizer,
                 conflict_detector: ConflictDetector,
                 conflict_resolver: ConflictResolver,
                 capital_estimator: CapitalDemandEstimator,
                 capital_allocator: CapitalAllocator,
                 execution_coordinator: ExecutionCoordinator,
                 risk_monitor: PortfolioRiskMonitor):
        
        self.collector = signal_collector
        self.normalizer = signal_normalizer
        self.conflict_detector = conflict_detector
        self.conflict_resolver = conflict_resolver
        self.capital_estimator = capital_estimator
        self.capital_allocator = capital_allocator
        self.execution_coordinator = execution_coordinator
        self.risk_monitor = risk_monitor
    
    def coordinate(self,
                  raw_signals: List[RawSignal],
                  available_capital: float,
                  strategy_priorities: Dict[str, int],
                  risk_budgets: Dict[str, float]) -> List[ExecutionOrder]:
        """协调主流程"""
        
        normalized = self.normalizer.normalize_all(
            raw_signals, 
            self.collector.strategies
        )
        
        conflicts = self.conflict_detector.detect_all_conflicts(
            normalized, 
            available_capital,
            sum(risk_budgets.values())
        )
        
        resolutions = self.conflict_resolver.resolve_all_conflicts(
            conflicts, normalized, method='weighted'
        )
        
        resolved_signals = self._apply_resolutions(normalized, resolutions)
        
        demands = self.capital_estimator.estimate_all_demands(
            resolved_signals,
            available_capital,
            strategy_priorities,
            {}
        )
        
        allocations = self.capital_allocator.allocate_by_priority(
            demands, available_capital
        )
        
        orders = self.execution_coordinator.rank_by_priority(
            resolved_signals, allocations, strategy_priorities
        )
        
        orders = self.execution_coordinator.batch_orders(orders)
        
        return orders
    
    def _apply_resolutions(self,
                          signals: List[StandardizedSignal],
                          resolutions: List[ConflictResolution]) -> List[StandardizedSignal]:
        """应用冲突解决方案"""
        losing_ids = set()
        for res in resolutions:
            losing_ids.update(res.losing_signal_ids)
        
        return [s for s in signals if s.signal_id not in losing_ids]
```

---

## 四、实施路径

### Phase 1: 核心协调功能（1周）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 信号收集与标准化 | 2天 | SignalCollector, SignalNormalizer |
| 冲突检测与解决 | 2天 | ConflictDetector, ConflictResolver |
| 资金协调 | 1天 | CapitalDemandEstimator, CapitalAllocator |

### Phase 2: 执行与监控（1周）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 执行协调 | 2天 | ExecutionCoordinator |
| 组合风险监控 | 2天 | PortfolioRiskMonitor |
| 集成测试 | 1天 | 端到端测试 |

---

## 五、相关文档

| 文档 | 说明 |
|------|------|
| [BLUEPRINT.md](./BLUEPRINT.md) | Layer 11主蓝图 |
| [CAPITAL_ALLOCATION_BLUEPRINT.md](./CAPITAL_ALLOCATION_BLUEPRINT.md) | 资本配置系统 |
| [INVESTMENT_CONSTRAINT_BLUEPRINT.md](./INVESTMENT_CONSTRAINT_BLUEPRINT.md) | 投资限制管理系统 |

---

**版本**: v1.0 | **更新**: 2026-04-06 | **状态**: ✅ 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Multi Strategy Coordination
- **模块ID**: MULTI_STRATEGY_COORDINATION_001
- **蓝图文档**: [MULTI_STRATEGY_COORDINATION_BLUEPRINT.md](./11_STRATEGIC_DECISION\MULTI_STRATEGY_COORDINATION_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: Layer 11.18 - 多策略协调系统
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Multi Strategy Coordination** | Layer 11.18 - 多策略协调系统 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
