---
module_id: MOD-SIG-144
title: "板块强度生产接线蓝图 — 报告→排名归一→聚合+生态"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
ttl: permanent
layer: L01_market
layer_name: market
functional_domain: signal_ashare
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-12"
last_updated: "2026-09-12"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-144 Sector Strength Wiring — 板块强度生产接线 蓝图

> **module_id**: MOD-SIG-144 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L2-01/TDM-E-L2-04 生产层
> **出身**：L2-01/L2-04 生产接线批（Owner"现在就接线"令）。

## 1. 接线语义

sector_report_builder（MOD-L00-009 production）日频报告 → 本件四维跨截面排名归一
（结构强度/动量活跃/多周期动量/资金流，rank-based 抗离群方案）→
aggregate_sector_strength（MOD-SIG-142）逐板块合成 + Top-15% 候选池 →
judge_sector_ecology（MOD-SIG-143）三态生态 → WiringResult。

## 2. 输入输出与降级

- 输入：报告 dict（top_sectors 条目 + lead_streak 透传 + breadth_label）
- 缺维度板块剔除+notes 留痕；lead_streak 缺失→ecology=None 不判定
- 高潮分代理=涨停比分档映射（极强95/强70/中40/弱15，sector_breadth 既有分档）

## 3. 查重分工

report_builder=观测层报告（数据采集编排）；本件=报告之上的 L2-01/L2-04 生产接线
（排名归一+聚合核调用+三态判定调用），算法本体全在 MOD-SIG-142/143 两核。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-144`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-144` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-144` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-144 | MOD-SIG-144 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

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
| — | — | 本模块尚无已实现代码 |

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
