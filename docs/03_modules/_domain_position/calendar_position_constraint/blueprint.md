---
module_id: MOD-POS-017
title: "日历仓位约束蓝图 — A股风险日历→仓位上限调整"
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
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-017 Calendar Position Constraint — 日历仓位约束 蓝图

> **module_id**: MOD-POS-017 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P1 | **成熟度**: L1 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-017 | **设计真源**: 07-D-POSITION §1.5 POS-17 + §7.4

## 1. 定位

A股风险日历仓位约束——根据当前日期和A股风险日历事件, 生成临时仓位上限调整和否决指令。
覆盖期权交割日/年报截止/股东空窗期/财报发布等7类日历事件。

属A类基础设施(日历计算+约束判定, 逻辑明确), 纯Python日期计算。

## 2. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 当前日期 + 持仓元数据(标的/ST/市值/预告/财报日) |
| 输出 | CalendarPositionAlert (约束列表+综合cap调整+否决标志) |

## 3. 日历事件规则 (设计真源 §7.4)

| 事件 | 时间规则 | 仓位约束 | action |
|------|---------|---------|--------|
| 股指期权交割日 | 每月第四个周三 | 否决新开仓(仅允许减仓) | BLOCK_NEW |
| 期权交割日±窗口 | 前2天+后1天 | 仓位上限下调10% | REDUCE_CAP(0.9) |
| 年报预告截止前5日 | 1月26-31日 | 未出预告个股否决新买入 | BLOCK_NEW(特定标的) |
| 年报+一季报截止 | 4月20-30日 | ST股强制清零 | FORCE_CLEAR(0.0) |
| 半年报预告截止前5日 | 7月10-15日 | 未出预告个股否决新买入 | BLOCK_NEW(特定标的) |
| 股东信息空窗期 | 11月-次年4月30日 | 微盘股(<50亿)上限收紧50% | TIGHTEN_CAP(0.5) |
| 财报发布前3天 | earnings_release_date-3 | 该标的上限下调+禁止新建 | BLOCK_NEW+REDUCE_CAP(0.9) |

## 4. 不变量

- overall_cap_adjustment = min(各约束cap) (取最严格)
- block_new_positions = any(BLOCK_NEW 且 affected_symbols is None)
- 无约束日期 → cap=1.0, block=False
- 日期计算用自然日(不做交易日历调整, 由上层处理)

## 5. 测试

`tests/position/test_calendar_position_constraint.py`

## 6. 依赖

- zephyr.shared.foundation.errors
- 消费者: MOD-POS-010(限仓执行器), MOD-POS-001(仓位决策引擎)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-017`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-017` 的 4 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-017` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-017 | MOD-POS-017 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 4 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/position/core/calendar_position_constraint.py` | ✅ 已实现 | |

### 7.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/position/test_calendar_position_constraint.py` | ✅ 已实现 | |
| `tests/position/test_drawdown_controller.py` | ✅ 已实现 | |
| `tests/position/test_position_sizing_engine.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


