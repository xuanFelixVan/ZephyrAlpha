---
module_id: MOD-RK-30
title: "C-004 自适应风控三层联动装配层蓝图 — 盘前预判+盘中监控+熔断分级（薄装配）MVP"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
blueprint_id: MOD-RK-30
domain_id: D_RISK
path: src/zephyr/risk/core/adaptive_risk_coordinator.py
design_maturity: production
build_status: stable
granularity: file
ai_autonomy: ai_modifiable
safety: H
stability: evolving
responsibility_domain: 
---

# MOD-RK-30 C-004 自适应风控三层联动装配层（Adaptive Risk Coordinator）蓝图

> **module_id**: MOD-RK-30 | **域**: D_RISK | **层**: C-004 三层体系编排面
> **优先级**: P0 | **来源**: CAND-RSK-031（B1-00174，AUD-DRAFT-001-DIGEST P0 波 W1c）

## 1. 定位

C-004 三层联动的**薄装配编排面**（W1c 同族整合裁定：底座复用+薄装配，禁止复制）：

- **预判层消费**：MOD-RK-28 ForwardVarForecast → 盘前计划（sit_out/限额缩放下发）
- **监控层消费**：MOD-RK-29 RiskWatchSnapshot → 盘中熔断分级输入
- **熔断层分级**：CircuitBreakerLevel 四级（NONE/REDUCE_POSITION/HALT_NEW/KILL_SWITCH），
  KILL_SWITCH 仅产 `kill_switch_advised`（BS-007 纪律：建议非直接触发，执行委托
  stop_loss/RiskLayerOrchestrator 存量链路，本模块不 import 不复制）
- **B-001~B-006 硬边界注册表**：代码 SSoT（frozen 映射），值锚定
  config/risk_params.yaml（INV-002/G10/G11/G12），单测锚定防漂移
- **参数随 C-021 状态自适应**：regime 风险乘数表（未知状态保守 0.7，Fail-Closed）

与存量编排器分工：MOD-L06-001 RiskLayerOrchestrator（ex_core 执行侧三层喂入）不动；
本模块是 D_RISK 域内三层数据契约的装配裁决面，产出供其消费。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | ForwardVarForecast + RiskWatchSnapshot + regime_state + black_swan_escalated | ①②层契约 |
| 输出 | PremarketRiskPlan / AdaptiveRiskDecision（level/position_cap_scale/allow_new_positions/kill_switch_advised/reasons） | frozen dataclass |

## 3. 核心规则

1. 盘前：`limit_scale_final = forecast.limit_scale × regime_multiplier`（收紧方向取小）；
   sit_out 透传并记 reason。
2. 盘中分级（取最严）：monitor red → HALT_NEW；orange → REDUCE_POSITION；
   forecast.limit_breached → REDUCE_POSITION（cap=limit_scale_final）；
   forecast.sit_out → HALT_NEW；black_swan_escalated → KILL_SWITCH。
3. 硬边界 B-001~B-006 为不可调下界：任何 limit_scale 不得放大越界（clamp）。
4. 纯函数无 IO；Fail-Closed 配置校验（InvalidCoordinatorConfigError）+ 未知
   regime 保守乘数。

## 4. 依赖

| 依赖 | 模块 | 类型 |
|------|------|------|
| 预判层契约 | MOD-RK-28 adaptive_risk_forecast | import_depends |
| 监控层契约 | MOD-RK-29 adaptive_risk_monitor | import_depends |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-30`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-30` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-30` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-30 | MOD-RK-30 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/risk/core/adaptive_risk_coordinator.py` | ✅ 已实现 | |

### 5.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_adaptive_risk_coordinator.py` | ✅ 已实现 | |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
