---
module_id: MOD-PF-003
title: "再平衡调度器蓝图 — 四触发源 + 成本收益判定"
doc_type: blueprint
status: Active
version: "0.1.3"
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
build_status: production
---

# MOD-PF-003 Rebalance Scheduler — 再平衡调度器 蓝图

> **module_id**: MOD-PF-003 | **域**: D_PF_CORE | **层**: L02 组合构建核心
> **优先级**: P0 | **成熟度**: design | **SSoT**: depgraph node 7445493
> **设计真源**: D:\临时工作区\依赖图\12-D-PF-CORE-组合构建域.md §1.2 PC-03

## 1. 定位

再平衡调度器——决定是否触发 PC-02 组合优化器重跑:
- 四触发源: 漂移阈值 ±2%/±3% + 周五日历 + 事件驱动 + 风控 E-RK-01/03
- 成本收益判定: benefit > 2× cost 才执行 (⑦⑧⑨ 项成本 ×1.5)
- 边界: PC-03=组合级调度(决定是否重跑优化器), POS-004=持仓级执行(复用其成本判定逻辑)

属 A 类基础设施(调度逻辑 + 成本收益数学, 无策略决策)。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | drift_pct(CTR-007) + 日历 + 事件 + 风控状态 | CTR-007 |
| 输出 | RebalanceEvaluation{triggered, trigger_source, cost_benefit_passed, new_target_portfolio, decision} | 内部 |
| 依赖 | PositionDriftMonitor(MOD-POS-003) | import_depends |
| 依赖 | RebalanceEngine(MOD-POS-004) | import_depends |
| 依赖 | PortfolioOptimizer(PC-02) | import |

## 3. 核心规则

### 3.1 四触发源

| 触发源 | 条件 | 优先级 |
|--------|------|--------|
| 漂移阈值 | drift_pct > 2% (警告) / > 3% (强制) | 1 (最高) |
| 日历 | 每周五收盘前 | 2 |
| 事件 | 策略上下线 / 标的退市 / 分红除权 | 3 |
| 风控 | E-RK-01 风控熔断 / E-RK-03 回撤超限 | 4 |

- 多触发源同时满足: 取最高优先级作为 trigger_source
- 风控触发: 跳过成本收益判定, 直接执行

### 3.2 成本收益判定

```
benefit = expected_tracking_error_reduction
cost = ⑦印花税 + ⑧佣金 + ⑨冲击成本 (×1.5 系数)

if benefit > 2 × cost:
    execute_rebalance = True
else:
    execute_rebalance = False (记录 skipped_reason)
```

- ⑦⑧⑨ 成本系数 ×1.5: 保守估计(含滑点+市场冲击)
- 风控触发: 跳过此判定

### 3.3 与 POS-004 的边界

| 维度 | PC-03 (本模块) | POS-004 (RebalanceEngine) |
|------|----------------|--------------------------|
| 层级 | 组合级 | 持仓级 |
| 决策 | 是否重跑优化器 | 如何执行买卖 |
| 复用 | 复用 POS-004 的成本估算 | — |

## 4. 关键不变量 (INVARIANTS)

- 风控触发 MUST 执行(跳过成本收益)
- 非风控触发 MUST 通过成本收益判定
- decision 字段记录最终决策: execute / skip / defer
- new_target_portfolio 仅在 triggered=True 且 cost_benefit_passed=True 时非空
- 同一交易日最多触发一次再平衡(幂等)

## 5. 错误契约

- `RebalanceCostEstimationError`: 成本估算失败(降级为保守高估)
- `DriftMonitorUnavailable`: drift 数据缺失(降级为日历触发)

## 6. 测试

- `tests/pf_core/test_rebalance_scheduler.py`
- 覆盖: 四触发源独立+组合、成本收益判定(通过+不通过)、风控跳过成本判定、幂等性(同日不重复)、POS-004 成本复用、退化场景

## 7. 依赖

- `zephyr.position.core.position_drift_monitor` (MOD-POS-003, drift 事件消费)
- `zephyr.position.core.rebalance_engine` (MOD-POS-004, 成本判定复用)
- `zephyr.pf_core.core.portfolio_optimizer` (PC-02, 重优化触发)
- 消费者: 组合管理层 (调度决策消费)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PF-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PF-003` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-PF-003` |
| 数据流图 (dataflow) | 1 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PF-003 | MOD-PF-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/pf_core/test_rebalance_scheduler.py` | ✅ 已实现 | |

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


