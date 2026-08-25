---
module_id: MOD-PA-013
title: "MaxDdLimit Allocation Strategist 蓝图 — 按策略回撤预算分配资金+超限降档/暂停"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L2_domain
layer_name: portfolio_alloc
functional_domain: portfolio_alloc
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
design_maturity: design
build_status: testing
responsibility_domain: 
---

# MOD-PA-013 MaxDdLimit Allocation Strategist — 最大回撤限制分配器 蓝图

> **module_id**: MOD-PA-013 | **域**: D_PF_ALLOC | **层**: L2 业务域
> **优先级**: P0 | **来源**: CAND-PFALLOC-006（B10-02101，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-PA-013

## 1. 定位

PA-13（A1 交易决策架构 §30.1.4）。回撤约束资金分配=机构风险预算标准实践。
场内现状：回撤跟踪/控制已有（MOD-RK-011 drawdown_tracker 实时告警 +
MOD-PA-003 组合级 MaxDD>15% 全线减 50% 一刀切），**按各策略 MaxDD 预算做资金
分配+超限动态降档缺失**。本模块补按策略颗粒度的预算制分配器。

与既有模块职责区分：

| 模块 | 颗粒度 | 动作 |
|---|---|---|
| MOD-RK-011 drawdown_tracker | 组合 | 三级告警（监控导向） |
| MOD-PA-003 multi_strategy_capital_allocator | 组合 | MaxDD>15% 全线 ×0.5（一刀切） |
| **MOD-PA-013（本模块）** | **按策略** | **预算制三档：NORMAL/DERATE ×0.5/SUSPEND=0** |

## 2. 输入 / 输出

- 输入：
  - `StrategyDdBudget`（strategy_id + base_weight + max_dd_budget∈(0,1]）逐策略预算声明；
  - `current_drawdowns`（{strategy_id: 当前回撤幅度}）——接线时源自 MOD-RK-011
    drawdown_tracker 资金曲线追踪（本模块自含输入契约，不反向依赖采集）；
  - `MaxDdAllocatorConfig`（derate_threshold=0.8 / derate_factor=0.5）。
- 输出 `MaxDdAllocationResult`：weights（Σ=1.0，全暂停时全零）+ actions（三档）+
  all_suspended 标记。

## 3. 核心规则

1. utilization = current_dd / max_dd_budget：
   - u < 0.8 → NORMAL（原权重）；
   - 0.8 ≤ u < 1.0 → DERATE（权重 ×0.5 降档）；
   - u ≥ 1.0 → SUSPEND（权重=0 暂停）。
2. 不变式：最终权重 Σ=1.0（有激活策略）；降档/暂停因子 ≤1.0 只减不增；
   全员暂停 → 权重全零 + all_suspended=True（零除防护）。
3. Fail-Closed：未知策略/缺失当前回撤/负回撤/非法预算 → InvalidMaxDdInputError
   （当前回撤是风控关键输入，缺失不默认 0）。
4. 错误码 ZA-PA-0013 未登记（申请中，W3 fragment 补登草稿，治理闭环后回补类属性）。

## 4. 依赖

- `zephyr.shared.foundation.errors`（ZephyrBaseError）；
- 设计态依赖：MOD-RK-011 drawdown_tracker（当前回撤数据源，运行时装配批接线）。

## 5. 测试

- `tests/pf_alloc/test_maxdd_limit_allocator.py`（12 测：三档判定/权重不变式/
  全暂停零除/输入 Fail-Closed）。

## 6. 依据

- construction_backlog_dig.tsv B10-02101（A1 交易决策架构 §30.1.4，裁定=做 P0）；
- CAND-PFALLOC-006（candidate_module_registry.yaml）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PA-013`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PA-013` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-PA-013` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PA-013 | MOD-PA-013 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | testing | testing | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
