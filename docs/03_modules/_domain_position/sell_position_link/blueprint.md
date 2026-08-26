---
module_id: MOD-POS-016
title: "卖出-仓位双向链接蓝图 — 阈值动态调整+买入后即时验证"
doc_type: blueprint
status: Active
version: "0.1.2"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-016 Sell-Position Bidirectional Link — 卖出-仓位双向链接 蓝图

> **module_id**: MOD-POS-016 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-016 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.4 POS-16

## 1. 定位

卖出-仓位双向链接——在卖出决策域与仓位管理域之间建立双向反馈通道:
正向根据仓位盈亏状态动态调整卖出阈值(盈利放宽/亏损收紧),
反向执行买入后即时验证(5min/15min/30min 三级窗口), 产出 PositionStateFeedback 反馈 D-SELL-DECISION。

属 A 类基础设施(盈亏判定+阈值缩放+时间窗口验证, 逻辑明确), 缩放因子与阈值为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | SellDecision + 仓位盈亏状态 | 来自 D-SELL-DECISION / 仓位状态 |
| 输入 | 买入后行情(价格/量/均线/ATR) | 实时行情 |
| 输出 | PositionStateFeedback | → D-SELL-DECISION |

## 3. 核心规则 (设计真源 §1.4 POS-16)

### 3.1 卖出阈值动态调整

| 盈亏状态 | 调整方向 | 因子 | 说明 |
|----------|----------|------|------|
| PROFIT (pnl_ratio > 0) | 放宽 | ×profit_loosen_factor (默认1.2) | 盈利持仓容忍度提高 |
| LOSS (pnl_ratio < 0) | 收紧 | ×loss_tighten_factor (默认0.8) | 亏损持仓加快退出 |
| BREAKEVEN (pnl_ratio ≈ 0) | 不变 | ×1.0 | 中性 |

### 3.2 买入后即时验证 (三级时间窗口)

| 窗口 | 条件 | 动作 |
|------|------|------|
| 5min | 跌破买入价 > 1% 且放量(volume_ratio > spike) | OBSERVE (进入观察) |
| 15min | 跌破分时均线 且 反弹无力 | REDUCE_50 (减仓50%) |
| 30min | 反向运动 > 2×ATR | FULL_STOP (全部止损) |

### 3.3 放量判定

- volume_ratio = 当前成交量 / 均量 > volume_spike_ratio (默认 1.5)

## 4. 关键不变量 (INVARIANTS)

- profit_loosen_factor ≥ 1.0 (放宽方向)
- loss_tighten_factor ≤ 1.0 (收紧方向)
- 调整后阈值 ≥ 0 (不可为负)
- FULL_STOP 优先级 > REDUCE_50 > OBSERVE > NORMAL
- 多窗口同时触发时取最高告警级别

## 5. 错误契约

- `InvalidSellPositionLinkInputError` (ZA-POS-0016): 价格非正、ATR非正、分钟数非正、因子越界

## 6. 测试

- `tests/position/test_sell_position_link.py`
- 覆盖: 三级盈亏阈值调整、5min/15min/30min验证、放量判定、告警级别优先级、输入校验、反馈事件订阅

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: D-SELL-DECISION (卖出决策域)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-016`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-016` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-016` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-016 | MOD-POS-016 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/position/core/sell_position_link.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


