---
module_id: SMART_ORDER_ROUTER_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: '2026-04-06'
owner: 首席架构师
layer: Layer 5 (策略执行层)
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 5 - 策略执行层
compliance_level: 专业标准
reference_models:
- Citadel Smart Order Router
- Two Sigma Order Routing
- Jump Trading SOR
related_documents:
- ARCHITECTURE.md
- STRATEGY_EXECUTION_LAYER_BLUEPRINT.md
- QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md
parent_document: ../INDEX.md
implementation_status: 设计阶段
opensource_project: 自研简化版
open_source_dependency: pandas, numpy
estimated_effort: 3周
priority: P2
---

# 智能订单路由器蓝图

> **版本**: v1.0
> **创建日期**: 2026-04-06
> **开源项目**: 自研简化版（个人单券商场景）
> **目标**: 构建简化版智能订单路由器，优化订单拆分和执行

---

## 📋 一、执行摘要

### 核心定位

智能订单路由器（SOR）是策略执行层的**订单路由核心**，负责：
- 订单拆分优化（大单拆分、时间拆分）
- 执行路径选择（最优执行路径）
- 流动性聚合（多流动性源聚合）
- 执行监控（实时执行监控）

### 个人使用价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评分 |
|---------|-------------|-------------|---------|
| **订单拆分** | 专业拆分算法 | 简化拆分逻辑 | ⭐⭐⭐⭐ |
| **执行路径** | 多市场路由 | 单券商优化 | ⭐⭐ |
| **流动性聚合** | 多源聚合 | 单源优化 | ⭐⭐ |
| **执行监控** | 实时监控 | 批量监控 | ⭐⭐⭐ |

**综合价值评分**: ⭐⭐ (2/5) - **个人单券商场景价值有限**

**重要说明**: 个人交易者通常只有1个券商账户（QMT），专业级SOR的多市场路由功能价值有限。建议实施简化版，重点优化订单拆分逻辑。

---

## 二、架构设计

### 2.1 Layer定位

**Layer归属**: Layer 5 - 策略执行层

**模块类别**: 订单路由模块

**架构角色**: 
- 作为策略执行层的订单路由核心
- 为QMT执行器提供订单拆分优化
- 为交易审计器提供路由记录

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                  智能订单路由器架构（简化版）                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              订单接收层                                   │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 订单信息                                            │ │ │
│  │  │  ├── 订单ID                                        │ │ │
│  │  │  ├── 股票代码                                      │ │ │
│  │  │  ├── 方向                                          │ │ │
│  │  │  ├── 数量                                          │ │ │
│  │  │  └── 价格                                          │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 订单分析                                            │ │ │
│  │  │  ├── 订单大小分析                                  │ │ │
│  │  │  ├── 流动性分析                                    │ │ │
│  │  │  ├── 市场冲击分析                                  │ │ │
│  │  │  └── 执行时间分析                                  │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              订单拆分层                                   │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 拆分策略                                            │ │ │
│  │  │  ├── 固定拆分                                      │ │ │
│  │  │  ├── 百分比拆分                                    │ │ │
│  │  │  ├── VWAP拆分                                      │ │ │
│  │  │  └── TWAP拆分                                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 拆分优化                                            │ │ │
│  │  │  ├── 流动性优化                                    │ │ │
│  │  │  ├── 冲击优化                                      │ │ │
│  │  │  ├── 时间优化                                      │ │ │
│  │  │  └── 成本优化                                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 子订单生成                                          │ │ │
│  │  │  ├── 子订单列表                                    │ │ │
│  │  │  ├── 执行时间表                                    │ │ │
│  │  │  ├── 价格限制                                      │ │ │
│  │  │  └── 执行条件                                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              执行监控层                                   │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 执行状态监控                                        │ │ │
│  │  │  ├── 已执行数量                                    │ │ │
│  │  │  ├── 未执行数量                                    │ │ │
│  │  │  ├── 执行价格                                      │ │ │
│  │  │  └── 执行时间                                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 执行调整                                            │ │ │
│  │  │  ├── 动态调整                                      │ │ │
│  │  │  ├── 价格调整                                      │ │ │
│  │  │  ├── 时间调整                                      │ │ │
│  │  │  └── 取消处理                                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 执行报告                                            │ │ │
│  │  │  ├── 执行摘要                                      │ │ │
│  │  │  ├── 成本分析                                      │ │ │
│  │  │  ├── 执行质量                                      │ │ │
│  │  │  └── 优化建议                                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 模块职责与边界

**核心职责**: 为订单提供拆分优化和执行监控能力

**职责边界**:
- ✅ 本模块负责:
  - 订单拆分优化
  - 执行路径选择（简化版）
  - 执行监控
  - 执行报告
  
- ❌ 本模块不负责:
  - 订单生成（由SignalGenerator负责）
  - 订单执行（由QMTExecutor负责）
  - 风险控制（由RiskHedgeEngine负责）
  - 成本分析（由TCAEngine负责）

---

## 三、技术实现方案

### 3.1 自研简化版实现

**设计理念**:
- 个人交易者通常只有1个券商账户（QMT）
- 专业级SOR的多市场路由功能价值有限
- 重点优化订单拆分逻辑，而非多市场路由

**核心功能**:
- 订单拆分优化
- 执行时间安排
- 执行监控
- 执行报告

**集成方案**:
```python
class SmartOrderRouter:
    def __init__(self):
        self.split_strategies = {
            'fixed': self.fixed_split,
            'percentage': self.percentage_split,
            'vwap': self.vwap_split,
            'twap': self.twap_split
        }
        
    def route_order(self, order, strategy='vwap'):
        split_func = self.split_strategies.get(strategy, self.vwap_split)
        sub_orders = split_func(order)
        return sub_orders
        
    def vwap_split(self, order, num_splits=10):
        volume_profile = self.predict_volume_profile(order.symbol)
        split_volumes = self.calculate_vwap_splits(order.volume, volume_profile, num_splits)
        
        sub_orders = []
        for i, volume in enumerate(split_volumes):
            sub_order = {
                'order_id': f"{order.order_id}_{i}",
                'symbol': order.symbol,
                'direction': order.direction,
                'volume': volume,
                'price': order.price,
                'execution_time': self.calculate_execution_time(i, num_splits)
            }
            sub_orders.append(sub_order)
            
        return sub_orders
```

### 3.2 核心算法设计

#### 3.2.1 订单拆分算法

**固定拆分**:
```python
def fixed_split(self, order, num_splits=10):
    split_volume = order.volume // num_splits
    remainder = order.volume % num_splits
    
    sub_orders = []
    for i in range(num_splits):
        volume = split_volume + (1 if i < remainder else 0)
        sub_order = self.create_sub_order(order, volume, i)
        sub_orders.append(sub_order)
        
    return sub_orders
```

**VWAP拆分**:
```python
def vwap_split(self, order, num_splits=10):
    volume_profile = self.predict_volume_profile(order.symbol)
    total_volume = sum(volume_profile.values())
    
    split_volumes = []
    for time_slot, volume in volume_profile.items():
        split_volume = int(order.volume * (volume / total_volume))
        split_volumes.append((time_slot, split_volume))
        
    return split_volumes
```

**TWAP拆分**:
```python
def twap_split(self, order, duration_minutes=30, interval_minutes=5):
    num_splits = duration_minutes // interval_minutes
    split_volume = order.volume // num_splits
    remainder = order.volume % num_splits
    
    sub_orders = []
    for i in range(num_splits):
        volume = split_volume + (1 if i < remainder else 0)
        execution_time = datetime.now() + timedelta(minutes=i * interval_minutes)
        sub_order = self.create_sub_order(order, volume, i, execution_time)
        sub_orders.append(sub_order)
        
    return sub_orders
```

#### 3.2.2 执行监控算法

**执行状态监控**:
```python
def monitor_execution(self, order_id):
    execution_status = {
        'total_volume': self.get_total_volume(order_id),
        'executed_volume': self.get_executed_volume(order_id),
        'remaining_volume': self.get_remaining_volume(order_id),
        'avg_execution_price': self.calculate_avg_execution_price(order_id),
        'execution_progress': self.calculate_execution_progress(order_id)
    }
    return execution_status
```

**动态调整**:
```python
def adjust_execution(self, order_id, market_conditions):
    if market_conditions['volatility'] > self.volatility_threshold:
        self.reduce_execution_speed(order_id)
    elif market_conditions['liquidity'] < self.liquidity_threshold:
        self.pause_execution(order_id)
    else:
        self.continue_execution(order_id)
```

### 3.3 数据模型设计

#### 3.3.1 订单数据模型

```python
class Order:
    order_id: str
    symbol: str
    direction: str  # buy/sell
    volume: float
    price: float
    order_type: str  # market/limit
    timestamp: datetime
```

#### 3.3.2 子订单数据模型

```python
class SubOrder:
    sub_order_id: str
    parent_order_id: str
    symbol: str
    direction: str
    volume: float
    price: float
    execution_time: datetime
    status: str  # pending/executed/cancelled
```

---

## 四、个人开发适用性分析

### 4.1 个人场景分析

| 场景维度 | 专业机构 | 个人交易者 | 说明 |
|---------|---------|-----------|------|
| **券商账户** | 多个 | 1个（QMT） | 无需多市场路由 |
| **交易频率** | 高频 | 中低频 | 拆分需求较低 |
| **订单大小** | 大单 | 中小单 | 拆分需求较低 |
| **流动性需求** | 多源聚合 | 单源优化 | 聚合价值有限 |

### 4.2 简化版优势

| 优势维度 | 说明 | 评分 |
|---------|------|------|
| **实施简单** | 仅需订单拆分逻辑 | ⭐⭐⭐⭐⭐ |
| **维护简单** | 功能简单，易于维护 | ⭐⭐⭐⭐⭐ |
| **成本可控** | 无需额外投入 | ⭐⭐⭐⭐⭐ |
| **价值有限** | 个人场景价值有限 | ⭐⭐ |

### 4.3 实施成本评估

| 成本维度 | 评估结果 | 说明 |
|---------|---------|------|
| **开发工时** | 3周 | 自研简化版 |
| **学习成本** | 低 | 功能简单 |
| **维护成本** | 低 | 功能简单 |
| **硬件成本** | 无 | 无需额外硬件投入 |

---

## 五、实施路径规划

### 5.1 Phase 1: 基础功能（Week 1-2）

**目标**: 实现基础订单拆分功能

**任务清单**:
1. ✅ 创建SOR基础类
2. ✅ 实现固定拆分策略
3. ✅ 实现VWAP拆分策略
4. ✅ 实现TWAP拆分策略
5. ✅ 单元测试和集成测试

**交付成果**:
- SOR基础框架
- 订单拆分功能
- 单元测试覆盖

### 5.2 Phase 2: 执行监控（Week 3）

**目标**: 实现执行监控功能

**任务清单**:
1. ✅ 实现执行状态监控
2. ✅ 实现动态调整功能
3. ✅ 实现执行报告功能
4. ✅ 集成测试
5. ✅ 文档完善

**交付成果**:
- 执行监控功能
- 动态调整功能
- 执行报告功能
- API接口文档
- 用户手册

---

## 六、质量保证标准

### 6.1 功能完整性检查

| 功能项 | 完整性要求 | 验证方法 |
|--------|-----------|---------|
| **订单拆分** | 支持多种拆分策略 | 功能测试 |
| **执行监控** | 支持实时监控 | 单元测试 |
| **动态调整** | 支持条件调整 | 集成测试 |
| **执行报告** | 支持完整报告 | 性能测试 |

### 6.2 性能要求

| 性能指标 | 要求 | 说明 |
|---------|------|------|
| **拆分速度** | <100ms | 订单拆分时间 |
| **监控频率** | 1次/秒 | 执行监控频率 |
| **调整延迟** | <1s | 动态调整延迟 |

### 6.3 准确性要求

| 准确性指标 | 要求 | 说明 |
|---------|------|------|
| **拆分精度** | 100% | 拆分数量准确 |
| **执行监控准确性** | 99% | 监控数据准确 |
| **调整有效性** | 90% | 调整决策有效 |

---

## 七、风险评估与缓解

### 7.1 技术风险

| 风险项 | 风险等级 | 缓解措施 |
|--------|---------|---------|
| **功能简单** | 低 | 功能简单，风险低 |
| **性能瓶颈** | 低 | 功能简单，性能要求低 |
| **数据质量** | 低 | 数据来源单一 |

### 7.2 实施风险

| 风险项 | 风险等级 | 缓解措施 |
|--------|---------|---------|
| **学习曲线** | 低 | 功能简单，易于学习 |
| **集成复杂度** | 低 | 功能简单，集成容易 |
| **维护成本** | 低 | 功能简单，维护容易 |

---

## 八、专业机构对标

### 8.1 Citadel对标

| 功能模块 | Citadel实现 | 本蓝图实现 | 对标程度 |
|---------|------------|-----------|---------|
| **多市场路由** | 多市场智能路由 | 单券商优化 | ⭐⭐ (40%) |
| **流动性聚合** | 多源流动性聚合 | 单源优化 | ⭐⭐ (40%) |
| **订单拆分** | 专业拆分算法 | 简化拆分逻辑 | ⭐⭐⭐⭐ (80%) |
| **执行监控** | 实时监控 | 批量+实时监控 | ⭐⭐⭐⭐ (80%) |

### 8.2 Two Sigma对标

| 功能模块 | Two Sigma实现 | 本蓝图实现 | 对标程度 |
|---------|--------------|-----------|---------|
| **AI路由** | AI驱动路由 | 规则路由 | ⭐⭐ (40%) |
| **实时优化** | 实时路径优化 | 批量优化 | ⭐⭐⭐ (60%) |

---

## 九、相关文档

| 文档名称 | 说明 |
|---------|------|
| [ARCHITECTURE.md](../../../01_FRAMEWORK/ARCHITECTURE.md) | 系统架构文档 |
| [STRATEGY_EXECUTION_LAYER_BLUEPRINT.md](../../../01_FRAMEWORK/STRATEGY_EXECUTION_LAYER_BLUEPRINT.md) | 策略执行层蓝图 |
| [QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md](../../05_TECHNICAL_SPECIFICATIONS/QMT_EXECUTOR_TECHNICAL_SPECIFICATION.md) | QMT执行器技术规格 |

---

**蓝图版本**: v1.0
**蓝图日期**: 2026-04-06
**蓝图编写**: 首席架构师
**蓝图状态**: 已完成

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 5: 策略执行层
##### 6.001. Smart Order Router
- **模块ID**: SMART_ORDER_ROUTER_001
- **蓝图文档**: [SMART_ORDER_ROUTER_BLUEPRINT.md](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SMART_ORDER_ROUTER_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: Layer 5 - 策略执行层
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Smart Order Router** | Layer 5 - 策略执行层 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
