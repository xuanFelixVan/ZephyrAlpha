---
module_id: MOD-PLAN-024
title: "买入逻辑存活判定蓝图 — 按买入理由逐仓回查三态"
doc_type: blueprint
status: Active
version: "0.1.2"
design_maturity: production
ttl: permanent
layer: L07_plan
layer_name: plan
functional_domain: plan
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-10"
last_updated: "2026-09-10"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-PLAN-024 Thesis Survival — 买入逻辑存活判定 蓝图

> **module_id**: MOD-PLAN-024 | **域**: D_PLAN | **消费节点**: TDM-P-P1-03（失效=转离场评估）

## 1. 四类买入理由判据（节点真源逐条）
打板仓查情绪梯队还在不在；多因子仓查因子暴露漂移；事件仓查利好兑现度；
做T底仓查趋势破没破。输出 成立（ALIVE）/弱化（WEAKENED）/失效（DEAD）三态。

## 2. 阈值（经验拍定=proposed）
- 多因子漂移：>0.30 弱化，>0.60 失效（原因子失效）
- 事件兑现：≤0.50 成立，>0.50 弱化，>0.80 失效（利好兑现完）
- 证据缺失（None）→ WEAKENED：不确定降预期，不武断判死（判死=触发离场，须明确证伪）

## 3. 查重分工
plan_deviation_monitor=计划收益偏差 z 监控；execution_deviation_attributor=执行偏差
事后归因；本件=买入理由逻辑存活回查。三者正交。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PLAN-024`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PLAN-024` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-PLAN-024` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PLAN-024 | MOD-PLAN-024 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 4. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/plan_engine/thesis_survival.py` | ✅ 已实现 | |

### 4.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/plan_engine/test_thesis_survival.py` | ✅ 已实现 | |

### 4.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §4（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


