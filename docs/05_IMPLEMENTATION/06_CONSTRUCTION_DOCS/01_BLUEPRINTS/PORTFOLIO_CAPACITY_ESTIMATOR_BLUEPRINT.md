---
module_id: PORTFOLIO_CAPACITY_ESTIMATOR_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 6 组合优化层
compliance_level: 专业标准
responsibility:
  - 组合容量动态估算
  - 市场冲击成本评估
  - 容量限制识别
  - 容量优化建议
layer: Layer 6 (组合优化层)
---

# 组合容量估算模块蓝图

## 1. 概述

### 1.1 定位与目标

**核心定位**: 动态估算策略的资金容量，识别容量限制因素

**业务价值**:
- 避免资金规模超过策略容量
- 优化资金配置效率
- 降低市场冲击成本

**版本信息**: v1.0.0

### 1.2 职责边界

**负责**:
- 估算策略资金容量
- 评估市场冲击成本
- 识别容量限制因素
- 提供容量优化建议

**不负责**:
- 执行交易（由Layer 5负责）
- 资金管理（由资金模块负责）
- 风险控制（由风险模块负责）

## 2. 架构设计

### 2.1 Layer定位

**Layer**: Layer 6 (组合优化层)

**上游依赖**:
- Layer 1: 数据预处理层（市场数据）
- Layer 6: 组合优化模块（组合配置）

**下游服务**:
- Layer 6: 组合优化模块（容量限制）
- Layer 7: AI报告层（容量报告）

### 2.2 模块架构

```
┌─────────────────────────────────────────────────────────┐
│        组合容量估算模块 (Portfolio Capacity Estimator)   │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 流动性分析    │  │ 冲击成本评估  │  │ 容量计算      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 限制识别      │  │ 优化建议      │  │ 监控预警      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.3 核心功能模块

| 模块 | 功能 | 开源方案 |
|------|------|----------|
| 流动性分析 | 分析资产流动性 | pandas + numpy |
| 冲击成本评估 | 评估市场冲击成本 | 自研 + cvxpy |
| 容量计算 | 计算策略容量 | 自研 |
| 限制识别 | 识别容量限制因素 | 自研 |
| 优化建议 | 提供容量优化建议 | 自研 |
| 监控预警 | 监控容量使用情况 | 自研 |

## 3. 技术实现

### 3.1 技术栈选择

| 技术领域 | 选择方案 | 理由 |
|----------|----------|------|
| 数值计算 | numpy, pandas | 高性能数值计算 |
| 优化求解 | cvxpy | 约束优化 |
| 统计分析 | scipy | 统计分析 |
| 可视化 | matplotlib, plotly | 容量图表展示 |

### 3.2 核心算法

```python
import numpy as np
import pandas as pd
from scipy import stats

class PortfolioCapacityEstimator:
    def __init__(self, max_impact_cost=0.005, max_participation_rate=0.1,
                 min_liquidity_ratio=0.05):
        self.max_impact_cost = max_impact_cost
        self.max_participation_rate = max_participation_rate
        self.min_liquidity_ratio = min_liquidity_ratio
    
    def estimate_liquidity(self, volume_data, avg_daily_volume):
        liquidity_metrics = {
            'avg_volume': np.mean(volume_data),
            'volume_std': np.std(volume_data),
            'volume_trend': stats.linregress(range(len(volume_data)), volume_data).slope,
            'liquidity_score': np.mean(volume_data) / avg_daily_volume
        }
        
        return liquidity_metrics
    
    def estimate_market_impact(self, trade_size, avg_daily_volume, volatility):
        participation_rate = trade_size / avg_daily_volume
        
        square_root_law = 0.1 * volatility * np.sqrt(participation_rate)
        
        linear_model = 0.05 * participation_rate * volatility
        
        return {
            'square_root_impact': square_root_law,
            'linear_impact': linear_model,
            'participation_rate': participation_rate,
            'estimated_impact': max(square_root_law, linear_model)
        }
    
    def calculate_capacity(self, portfolio_weights, liquidity_data, 
                          volatility_data, target_impact_cost=None):
        if target_impact_cost is None:
            target_impact_cost = self.max_impact_cost
        
        capacity_constraints = []
        
        for symbol, weight in portfolio_weights.items():
            liquidity = liquidity_data.get(symbol, {})
            volatility = volatility_data.get(symbol, 0.02)
            
            avg_volume = liquidity.get('avg_volume', 0)
            if avg_volume == 0:
                capacity_constraints.append({
                    'symbol': symbol,
                    'constraint_type': 'no_liquidity',
                    'max_capacity': 0,
                    'reason': '无流动性数据'
                })
                continue
            
            max_trade_size_by_impact = (target_impact_cost / (0.1 * volatility)) ** 2 * avg_volume
            
            max_trade_size_by_participation = self.max_participation_rate * avg_volume
            
            max_trade_size = min(max_trade_size_by_impact, max_trade_size_by_participation)
            
            max_position = max_trade_size / weight if weight > 0 else 0
            
            capacity_constraints.append({
                'symbol': symbol,
                'constraint_type': 'liquidity',
                'max_capacity': max_position,
                'max_trade_size': max_trade_size,
                'avg_volume': avg_volume,
                'volatility': volatility,
                'impact_cost': target_impact_cost,
                'participation_rate': self.max_participation_rate
            })
        
        total_capacity = min([c['max_capacity'] for c in capacity_constraints 
                             if c['max_capacity'] > 0])
        
        return {
            'total_capacity': total_capacity,
            'capacity_constraints': capacity_constraints,
            'bottleneck_asset': min(capacity_constraints, 
                                   key=lambda x: x['max_capacity'])['symbol'],
            'capacity_utilization': self._calculate_utilization(capacity_constraints)
        }
    
    def _calculate_utilization(self, constraints):
        capacities = [c['max_capacity'] for c in constraints if c['max_capacity'] > 0]
        if not capacities:
            return 0
        
        return {
            'min_capacity': min(capacities),
            'max_capacity': max(capacities),
            'avg_capacity': np.mean(capacities),
            'capacity_std': np.std(capacities)
        }
    
    def identify_capacity_limitations(self, capacity_result, current_aum):
        limitations = []
        
        if current_aum > capacity_result['total_capacity']:
            limitations.append({
                'type': 'capacity_exceeded',
                'severity': 'high',
                'current_aum': current_aum,
                'max_capacity': capacity_result['total_capacity'],
                'excess': current_aum - capacity_result['total_capacity'],
                'recommendation': '当前规模超过容量限制，建议减少规模或优化组合'
            })
        
        bottleneck = capacity_result['bottleneck_asset']
        bottleneck_constraint = next(
            (c for c in capacity_result['capacity_constraints'] if c['symbol'] == bottleneck),
            None
        )
        
        if bottleneck_constraint:
            limitations.append({
                'type': 'bottleneck_asset',
                'severity': 'medium',
                'symbol': bottleneck,
                'max_capacity': bottleneck_constraint['max_capacity'],
                'reason': f'资产{bottleneck}流动性限制组合容量',
                'recommendation': f'考虑降低{bottleneck}权重或寻找替代资产'
            })
        
        for constraint in capacity_result['capacity_constraints']:
            if constraint.get('participation_rate', 0) > 0.05:
                limitations.append({
                    'type': 'high_participation',
                    'severity': 'low',
                    'symbol': constraint['symbol'],
                    'participation_rate': constraint['participation_rate'],
                    'recommendation': f'资产{constraint["symbol"]}参与率较高，注意市场冲击'
                })
        
        return limitations
    
    def optimize_capacity(self, portfolio_weights, liquidity_data, 
                         volatility_data, current_aum):
        capacity_result = self.calculate_capacity(
            portfolio_weights, liquidity_data, volatility_data
        )
        
        limitations = self.identify_capacity_limitations(capacity_result, current_aum)
        
        optimization_suggestions = []
        
        if capacity_result['total_capacity'] < current_aum:
            bottleneck = capacity_result['bottleneck_asset']
            bottleneck_weight = portfolio_weights[bottleneck]
            
            optimized_weights = portfolio_weights.copy()
            optimized_weights[bottleneck] *= 0.5
            
            other_assets = [s for s in portfolio_weights.keys() if s != bottleneck]
            redistribute_weight = bottleneck_weight * 0.5 / len(other_assets)
            
            for asset in other_assets:
                optimized_weights[asset] += redistribute_weight
            
            new_capacity = self.calculate_capacity(
                optimized_weights, liquidity_data, volatility_data
            )
            
            optimization_suggestions.append({
                'type': 'weight_reduction',
                'description': f'降低{bottleneck}权重50%',
                'new_capacity': new_capacity['total_capacity'],
                'capacity_improvement': new_capacity['total_capacity'] - capacity_result['total_capacity']
            })
        
        return {
            'current_capacity': capacity_result['total_capacity'],
            'current_aum': current_aum,
            'capacity_utilization': current_aum / capacity_result['total_capacity'] if capacity_result['total_capacity'] > 0 else 0,
            'limitations': limitations,
            'optimization_suggestions': optimization_suggestions,
            'recommendation': self._generate_recommendation(capacity_result, current_aum)
        }
    
    def _generate_recommendation(self, capacity_result, current_aum):
        if current_aum > capacity_result['total_capacity']:
            return '当前规模超过容量限制，建议立即优化'
        elif current_aum > capacity_result['total_capacity'] * 0.8:
            return '接近容量上限，建议关注容量优化'
        else:
            return '容量充足，可继续扩大规模'

## 4. 数据模型

### 4.1 数据结构

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class LiquidityMetrics:
    symbol: str
    avg_volume: float
    volume_std: float
    volume_trend: float
    liquidity_score: float

@dataclass
class CapacityConstraint:
    symbol: str
    constraint_type: str
    max_capacity: float
    max_trade_size: float
    avg_volume: float
    volatility: float
    impact_cost: float
    participation_rate: float

@dataclass
class CapacityResult:
    total_capacity: float
    capacity_constraints: List[CapacityConstraint]
    bottleneck_asset: str
    capacity_utilization: Dict
```

### 4.2 存储方案

| 数据类型 | 存储方案 | 保留期限 |
|----------|----------|----------|
| 容量历史 | SQLite | 1年 |
| 限制记录 | SQLite | 永久 |
| 优化建议 | SQLite | 永久 |

## 5. 实施路径

### 5.1 Phase 1: 核心功能 (1周)

- [x] 流动性分析
- [x] 冲击成本评估
- [x] 容量计算
- [x] 基础监控功能

### 5.2 Phase 2: 高级功能 (1周)

- [ ] 限制识别
- [ ] 优化建议
- [ ] 预警系统
- [ ] 可视化界面

### 5.3 Phase 3: 优化完善 (1周)

- [ ] 性能优化
- [ ] API接口完善
- [ ] 文档完善
- [ ] 测试覆盖

## 6. 文档治理

### 6.1 System_Manifest.md索引

```yaml
- module_id: PORTFOLIO_CAPACITY_ESTIMATOR_001
  module_name: 组合容量估算模块
  layer: Layer 6 (组合优化层)
  status: Active
  blueprint: PORTFOLIO_CAPACITY_ESTIMATOR_BLUEPRINT.md
```

### 6.2 模块职责边界

**与组合优化模块的关系**:
- 组合优化模块提供组合配置
- 容量估算模块提供容量限制

**与风险管理模块的关系**:
- 容量估算模块提供容量风险
- 风险管理模块进行风险控制

### 6.3 版本管理策略

- v1.0.0: 初始版本，基础容量估算
- v1.1.0: 增加优化建议功能
- v1.2.0: 增加预警系统

## 7. 风险评估

### 7.1 技术风险

| 风险 | 概率 | 应对措施 |
|------|------|----------|
| 流动性数据缺失 | 中 | 使用历史数据估算 |
| 模型误差 | 中 | 持续优化模型 |
| 计算性能瓶颈 | 低 | 使用缓存优化 |

### 7.2 业务风险

| 风险 | 概率 | 应对措施 |
|------|------|----------|
| 容量误判 | 中 | 多维度验证 |
| 市场冲击超预期 | 中 | 设置安全边际 |
| 规模失控 | 低 | 设置容量上限 |

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 组合优化层负责人 |
