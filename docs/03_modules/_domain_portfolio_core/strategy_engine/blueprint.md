---
module_id: MOD-PF-001
title: "策略引擎蓝图 — 生命周期状态机 + 四维决策 + OCP-002 扩展"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L02_portfolio_core
layer_name: portfolio_core
functional_domain: portfolio_core
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-PF-001 Strategy Engine — 策略引擎 蓝图

> **module_id**: MOD-PF-001 | **域**: D_PF_CORE | **层**: L02 组合构建核心
> **优先级**: P0 | **成熟度**: design | **SSoT**: depgraph node 7439827
> **设计真源**: D:\临时工作区\依赖图\12-D-PF-CORE-组合构建域.md §1.2 PC-01

## 1. 定位

策略引擎——管理策略生命周期 + 产出目标权重,供 PC-02 组合优化器消费:
- 生命周期状态机: registered → testing → active → deprecated (不可逆)
- 版本控制: 每策略多版本共存, active 版本唯一
- 冷启动保护: 新策略前 30 天权重上限 30% (cold_start_cap=0.3)
- 四维决策: 选股 / 买入 / 卖出 / 仓位
- OCP-002 扩展: 复用 StrategyBase/StrategyRegistry (开放扩展,封闭修改)

属 A 类基础设施(生命周期管理 + 权重聚合, 无策略逻辑本身), 策略实现为 B 类扩展。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | StrategyBase 子类实例 + 市场信号 | OCP-002 |
| 输出 | StrategyDecision{target_weights, selection_universe, buy/sell_signals, cold_start_active, lifecycle_event} | 内部 → PC-02 |
| 产出事件 | StrategyLifecycleEvent | CTR-P1-006 |
| 依赖 | StrategyBase/StrategyRegistry (OCP-002) | import_depends |

## 3. 核心规则

### 3.1 生命周期状态机

```
registered → testing → active → deprecated
    ↑                      ↓
    └─── (不可逆, 只进不退) ─┘
```

- registered: 已注册未测试, 不参与实盘
- testing: 回测中, 影子模式(产出但不执行)
- active: 实盘生效, 产出 target_weights
- deprecated: 生命周期终态, 不再产出

### 3.2 冷启动保护

- 新策略激活后前 30 个交易日: cold_start_active=True
- 冷启动期间: 权重 × cold_start_cap (默认 0.3)
- 冷启动期满: 自动解除, lifecycle_event 记录状态转换

### 3.3 四维决策

| 维度 | 方法 | 产出 |
|------|------|------|
| 选股 | select_universe() | selection_universe: list[str] |
| 买入 | generate_buy_signals() | buy_signals: dict[str, float] |
| 卖出 | generate_sell_signals() | sell_signals: dict[str, float] |
| 仓位 | generate_target_weights() | target_weights: dict[str, float] |

### 3.4 多策略权重聚合

- 等权: 各 active 策略 target_weights 等权平均
- IC 加权: 按近期 IC 加权(需策略暴露 IC 指标)
- 冷启动策略单独缩放后参与聚合

## 4. 关键不变量 (INVARIANTS)

- 同时只有一个 active 版本 per strategy_id
- 冷启动期间权重 ≤ cold_start_cap × 原始权重
- deprecated 策略不产出任何 decision
- lifecycle_event 在状态转换时 MUST 产出 (CTR-P1-006)
- target_weights 的 keys ⊆ selection_universe

## 5. 错误契约

- `StrategyNotFoundError`: 策略未注册或处于 deprecated 状态
- `StrategyVersionConflict`: 多版本同时 active
- `ColdStartBreachError`: 冷启动权重超限

## 6. 测试

- `tests/pf_core/test_strategy_engine.py`
- 覆盖: 生命周期状态转换(合法+非法)、冷启动缩放、四维决策产出、多策略聚合、OCP-002 扩展注册、幂等性

## 7. 依赖

- `zephyr.governance.strategies.strategy_base` (OCP-002, StrategyBase/StrategyRegistry)
- `zephyr.shared.contracts.strategy_lifecycle_event` (CTR-P1-006, 生命周期事件)
- 消费者: PC-02 Portfolio Optimizer (target_weights), PC-10 Performance Attribution (策略降级检测)
