---
module_id: MOD-SIG-136
title: "板块强度加权传导蓝图 — 10 分制传导系数"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: design
ttl: permanent
layer: L02_sector
layer_name: sector
functional_domain: signal_ashare
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-10"
last_updated: "2026-09-10"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-136 Sector Conduction — 强度加权传导 蓝图

> **module_id**: MOD-SIG-136 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L2-06-3

## 1. 定位
板块强度（10 分制）→ 个股 score 数值传导系数。节点真源锚点：10 分=+15%、
6 分=+5%、<6 分=-10%；强板块的弱票也加分，弱板块的强票打折。

## 2. 系数模型
- 锚点：10 → ×1.15；6 → ×1.05；<6 → ×0.90（平段）
- 6→10 线性插值（每分 +2.5%）；乘数恒 ∈ [0.90, 1.15]
- 应用：adjusted = stock_score × multiplier（保序不重排名）

## 3. 查重分工
sector_attribute_rules=攻防属性标注（标签）；sector_gate.admission_gate=准入闸
（放行/拦截）；本件=数值传导系数。三者正交：先过 gate，属性给语境，本件给加成。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-136`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-136` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-136` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-136 | MOD-SIG-136 | ✅ |
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
| `src/zephyr/signal_ashare/sector_conduction.py` | ✅ 已实现 | |

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
