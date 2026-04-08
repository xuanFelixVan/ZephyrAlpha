---
module_id: CONSTRAINT_CONFLICT_RESOLVER_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 6 组合优化层
compliance_level: 专业标准
responsibility:
  - 约束冲突检测
  - 冲突自动解决
  - 约束优先级管理
  - 解决方案建议
layer: Layer 6 (组合优化层)
---

# 约束冲突自动解决器蓝图

## 1. 概述

### 1.1 定位与目标

**核心定位**: 自动检测和解决优化约束冲突，确保优化问题可解

**业务价值**:
- 避免优化失败
- 提高优化成功率
- 降低人工干预成本

**版本信息**: v1.0.0

### 1.2 职责边界

**负责**:
- 检测约束冲突
- 自动解决冲突
- 管理约束优先级
- 提供解决方案建议

**不负责**:
- 定义约束（由业务模块负责）
- 执行优化（由优化模块负责）
- 执行交易（由执行模块负责）

## 2. 架构设计

### 2.1 Layer定位

**Layer**: Layer 6 (组合优化层)

**上游依赖**:
- Layer 6: 组合约束管理模块（约束定义）

**下游服务**:
- Layer 6: 组合优化模块（解决后的约束）
- Layer 7: AI报告层（冲突报告）

### 2.2 模块架构

```
┌─────────────────────────────────────────────────────────┐
│      约束冲突自动解决器 (Constraint Conflict Resolver)   │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 冲突检测      │  │ 冲突分类      │  │ 解决策略      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 优先级管理    │  │ 方案生成      │  │ 验证测试      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.3 核心功能模块

| 模块 | 功能 | 开源方案 |
|------|------|----------|
| 冲突检测 | 检测约束冲突 | cvxpy + 自研 |
| 冲突分类 | 分类冲突类型 | 自研 |
| 解决策略 | 应用解决策略 | cvxpy |
| 优先级管理 | 管理约束优先级 | 自研 |
| 方案生成 | 生成解决方案 | 自研 |
| 验证测试 | 验证解决方案 | cvxpy |

## 3. 技术实现

### 3.1 技术栈选择

| 技术领域 | 选择方案 | 理由 |
|----------|----------|------|
| 优化求解 | cvxpy | 约束优化 |
| 数值计算 | numpy, pandas | 高性能数值计算 |
| 图论 | networkx | 约束依赖分析 |
| 可视化 | matplotlib, plotly | 冲突图展示 |

### 3.2 核心算法

```python
import numpy as np
import cvxpy as cp
from typing import List, Dict, Tuple

class ConstraintConflictResolver:
    def __init__(self):
        self.conflict_types = {
            'infeasible': '约束不可行',
            'redundant': '冗余约束',
            'contradictory': '矛盾约束',
            'over_constrained': '过度约束'
        }
    
    def detect_conflicts(self, constraints, n_assets):
        conflicts = []
        
        for i, c1 in enumerate(constraints):
            for j, c2 in enumerate(constraints[i+1:], i+1):
                conflict = self._check_pairwise_conflict(c1, c2, n_assets)
                if conflict:
                    conflicts.append({
                        'type': conflict['type'],
                        'constraint1': c1,
                        'constraint2': c2,
                        'description': conflict['description'],
                        'severity': conflict['severity']
                    })
        
        feasibility = self._check_feasibility(constraints, n_assets)
        if not feasibility['feasible']:
            conflicts.append({
                'type': 'infeasible',
                'description': feasibility['message'],
                'severity': 'critical'
            })
        
        return conflicts
    
    def _check_pairwise_conflict(self, c1, c2, n_assets):
        if c1['type'] == 'weight_sum' and c2['type'] == 'weight_sum':
            if abs(c1['value'] - c2['value']) > 1e-6:
                return {
                    'type': 'contradictory',
                    'description': f'权重和约束矛盾: {c1["value"]} vs {c2["value"]}',
                    'severity': 'critical'
                }
        
        if c1['type'] == 'max_weight' and c2['type'] == 'min_weight':
            if c1['asset'] == c2['asset'] and c1['value'] < c2['value']:
                return {
                    'type': 'contradictory',
                    'description': f'资产{c1["asset"]}权重约束矛盾',
                    'severity': 'critical'
                }
        
        if c1['type'] == 'sector_max' and c2['type'] == 'sector_min':
            if c1['sector'] == c2['sector'] and c1['value'] < c2['value']:
                return {
                    'type': 'contradictory',
                    'description': f'行业{c1["sector"]}约束矛盾',
                    'severity': 'critical'
                }
        
        return None
    
    def _check_feasibility(self, constraints, n_assets):
        try:
            w = cp.Variable(n_assets)
            
            constraint_list = []
            
            constraint_list.append(cp.sum(w) == 1)
            constraint_list.append(w >= 0)
            
            for c in constraints:
                if c['type'] == 'max_weight':
                    constraint_list.append(w[c['asset']] <= c['value'])
                elif c['type'] == 'min_weight':
                    constraint_list.append(w[c['asset']] >= c['value'])
                elif c['type'] == 'sector_max':
                    sector_weights = sum(w[i] for i in c['assets'])
                    constraint_list.append(sector_weights <= c['value'])
            
            objective = cp.Minimize(0)
            problem = cp.Problem(objective, constraint_list)
            problem.solve()
            
            if problem.status == 'infeasible':
                return {
                    'feasible': False,
                    'message': '约束集合不可行，存在冲突'
                }
            else:
                return {
                    'feasible': True,
                    'message': '约束集合可行'
                }
        except Exception as e:
            return {
                'feasible': False,
                'message': f'可行性检查失败: {str(e)}'
            }
    
    def resolve_conflicts(self, constraints, conflicts, n_assets, 
                         priority_rules=None):
        if priority_rules is None:
            priority_rules = self._default_priority_rules()
        
        resolved_constraints = constraints.copy()
        resolutions = []
        
        for conflict in conflicts:
            if conflict['type'] == 'infeasible':
                resolution = self._resolve_infeasibility(
                    resolved_constraints, n_assets, priority_rules
                )
                resolutions.append(resolution)
                resolved_constraints = resolution['modified_constraints']
            
            elif conflict['type'] == 'contradictory':
                resolution = self._resolve_contradiction(
                    conflict, priority_rules
                )
                resolutions.append(resolution)
                resolved_constraints = self._apply_resolution(
                    resolved_constraints, resolution
                )
        
        return {
            'original_constraints': constraints,
            'resolved_constraints': resolved_constraints,
            'resolutions': resolutions,
            'success': self._verify_resolution(resolved_constraints, n_assets)
        }
    
    def _default_priority_rules(self):
        return {
            'weight_sum': 10,
            'max_weight': 8,
            'min_weight': 7,
            'sector_max': 6,
            'sector_min': 5,
            'turnover_max': 4,
            'tracking_error_max': 3
        }
    
    def _resolve_infeasibility(self, constraints, n_assets, priority_rules):
        relaxed_constraints = []
        
        for c in constraints:
            if c['type'] in ['max_weight', 'sector_max']:
                relaxed_c = c.copy()
                relaxed_c['value'] *= 1.1
                relaxed_constraints.append(relaxed_c)
            elif c['type'] in ['min_weight', 'sector_min']:
                relaxed_c = c.copy()
                relaxed_c['value'] *= 0.9
                relaxed_constraints.append(relaxed_c)
            else:
                relaxed_constraints.append(c)
        
        feasibility = self._check_feasibility(relaxed_constraints, n_assets)
        
        if feasibility['feasible']:
            return {
                'type': 'relaxation',
                'description': '放宽约束边界10%',
                'modified_constraints': relaxed_constraints,
                'success': True
            }
        else:
            low_priority_constraints = sorted(
                constraints,
                key=lambda x: priority_rules.get(x['type'], 0)
            )
            
            for i in range(len(low_priority_constraints)):
                test_constraints = low_priority_constraints[i+1:]
                feasibility = self._check_feasibility(test_constraints, n_assets)
                
                if feasibility['feasible']:
                    return {
                        'type': 'removal',
                        'description': f'移除{len(low_priority_constraints) - i - 1}个低优先级约束',
                        'removed_constraints': low_priority_constraints[:i+1],
                        'modified_constraints': test_constraints,
                        'success': True
                    }
            
            return {
                'type': 'failure',
                'description': '无法自动解决冲突，需要人工干预',
                'success': False
            }
    
    def _resolve_contradiction(self, conflict, priority_rules):
        c1 = conflict['constraint1']
        c2 = conflict['constraint2']
        
        p1 = priority_rules.get(c1['type'], 0)
        p2 = priority_rules.get(c2['type'], 0)
        
        if p1 >= p2:
            keep = c1
            remove = c2
        else:
            keep = c2
            remove = c1
        
        return {
            'type': 'priority_selection',
            'description': f'保留高优先级约束{keep["type"]}，移除{remove["type"]}',
            'keep_constraint': keep,
            'remove_constraint': remove,
            'success': True
        }
    
    def _apply_resolution(self, constraints, resolution):
        if resolution['type'] == 'priority_selection':
            return [c for c in constraints 
                   if c != resolution['remove_constraint']]
        else:
            return constraints
    
    def _verify_resolution(self, constraints, n_assets):
        feasibility = self._check_feasibility(constraints, n_assets)
        return feasibility['feasible']
    
    def generate_resolution_suggestions(self, constraints, n_assets):
        conflicts = self.detect_conflicts(constraints, n_assets)
        
        if not conflicts:
            return {
                'has_conflicts': False,
                'message': '约束集合无冲突'
            }
        
        resolution = self.resolve_conflicts(constraints, conflicts, n_assets)
        
        suggestions = []
        
        for conflict in conflicts:
            if conflict['type'] == 'contradictory':
                suggestions.append({
                    'conflict': conflict,
                    'suggestion': f'建议调整约束边界，使{conflict["constraint1"]["type"]}和{conflict["constraint2"]["type"]}兼容',
                    'priority': 'high'
                })
        
        if resolution['success']:
            suggestions.append({
                'conflict': {'type': 'auto_resolved'},
                'suggestion': '系统已自动解决冲突，建议检查解决结果',
                'priority': 'medium'
            })
        
        return {
            'has_conflicts': True,
            'conflicts': conflicts,
            'resolution': resolution,
            'suggestions': suggestions
        }

## 4. 数据模型

### 4.1 数据结构

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class Constraint:
    type: str
    value: float
    asset: Optional[int]
    sector: Optional[str]
    assets: Optional[List[int]]

@dataclass
class Conflict:
    type: str
    constraint1: Constraint
    constraint2: Optional[Constraint]
    description: str
    severity: str

@dataclass
class Resolution:
    type: str
    description: str
    modified_constraints: List[Constraint]
    success: bool
```

### 4.2 存储方案

| 数据类型 | 存储方案 | 保留期限 |
|----------|----------|----------|
| 冲突历史 | SQLite | 1年 |
| 解决方案 | SQLite | 永久 |
| 优先级规则 | YAML | 永久 |

## 5. 实施路径

### 5.1 Phase 1: 核心功能 (1周)

- [x] 冲突检测
- [x] 冲突分类
- [x] 基础解决策略
- [x] 验证功能

### 5.2 Phase 2: 高级功能 (1周)

- [ ] 优先级管理
- [ ] 多策略解决
- [ ] 方案生成
- [ ] 可视化界面

### 5.3 Phase 3: 优化完善 (1周)

- [ ] 性能优化
- [ ] API接口完善
- [ ] 文档完善
- [ ] 测试覆盖

## 6. 文档治理

### 6.1 System_Manifest.md索引

```yaml
- module_id: CONSTRAINT_CONFLICT_RESOLVER_001
  module_name: 约束冲突自动解决器
  layer: Layer 6 (组合优化层)
  status: Active
  blueprint: CONSTRAINT_CONFLICT_RESOLVER_BLUEPRINT.md
```

### 6.2 模块职责边界

**与约束管理模块的关系**:
- 约束管理模块提供约束定义
- 冲突解决器解决约束冲突

**与组合优化模块的关系**:
- 冲突解决器提供解决后的约束
- 组合优化模块使用约束进行优化

### 6.3 版本管理策略

- v1.0.0: 初始版本，基础冲突解决
- v1.1.0: 增加优先级管理
- v1.2.0: 增加多策略解决

## 7. 风险评估

### 7.1 技术风险

| 风险 | 概率 | 应对措施 |
|------|------|----------|
| 解决策略失效 | 中 | 多策略备选 |
| 性能瓶颈 | 低 | 使用缓存优化 |
| 误判冲突 | 中 | 优化检测算法 |

### 7.2 业务风险

| 风险 | 概率 | 应对措施 |
|------|------|----------|
| 过度放宽约束 | 中 | 设置放宽上限 |
| 解决结果不合理 | 低 | 人工复核机制 |
| 解决延迟 | 低 | 异步解决 |

## 接口与契约（蓝图终稿）

- 全库 API 与事件约定真源：[`API_Contract.md`](../../../03_TRADING_TACTICS/API_Contract.md)。约束冲突、解决策略、解释与落地事件等对外约定需以该真源或其子契约为准。
- 邻层协同边界：与 **Layer 6（组合约束管理）**、**Layer 6（组合优化）** 的交互以契约为准（避免“约束口径/求解口径”漂移）。

## 验收标准（可检查）

- 能对一组约束输入检测到冲突并输出冲突类型、证据与严重度，结果可复现。
- 能给出至少一种可执行的解决策略（放宽/替代/优先级），并可复核“修改了哪些约束、修改幅度”。
- 能记录一次冲突解决的审计事件（输入摘要、输出摘要、时间戳、版本号），并可追溯。
- 在冲突无法自动解决时，能输出明确的人工介入建议与阻断策略并留痕。

## 已知限制

- 具体事件载荷、约束 DSL 与解决策略库的字段字典将在施工阶段固化到 `API_Contract.md` 子契约；本蓝图先锁定边界、接口闭合点与验收闭环。

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 组合优化层负责人 |
