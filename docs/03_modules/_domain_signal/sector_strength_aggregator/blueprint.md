---
module_id: MOD-SIG-142
title: "板块强度四路合分蓝图 — 等权先验+Top15%候选池"
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

# MOD-SIG-142 Sector Strength Aggregator — 板块强度四路合分 蓝图

> **module_id**: MOD-SIG-142 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L2-01；下游=L2-06 强度传导/L3 候选池（待接线）
> **出身**：晨审定性"聚合公式需权重裁定"；Owner 2026-09-12 授权架构师自行裁定令后落地。

## 1. 权重裁定（架构师分析过程，2026-09-12）

四路子分（结构强度/动量活跃/多周期动量/资金流）尚无独立 IC 证据链，此时任何非对称
权重都是无证据的先验注入。量化社区标准做法（Barra 风格因子初始等权、WorldQuant
Alpha101 未加权合成、QLib Alpha158 等权基线）：**无证据时等权是最大熵先验**。
据此裁定：w = 0.25×4 等权起步，weights 参数显式可注入；IC 数据积累后按
multifactor_synthesis（L3-07-2）的 IC 加权惯例重校。市场级调节（L2-01-5 产出）
为加法 delta ∈[-10,+10]，合成后 clamp [0,100]。

## 2. 候选池

composite 降序 Top-ceil(N×15%)（节点真源"总分进前 15%"），保底 1 个；
平分按板块名稳定序（确定性）。

## 3. 查重分工

四个子分产出件（L2-01-1~5）各自已锚定；本件为纯聚合核（零 IO、等权+clamp+Top 池），
不重复任何子件逻辑。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-142`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-142` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-142` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-142 | MOD-SIG-142 | ✅ |
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
| `src/zephyr/signal_ashare/core/candidate_pool_aggregator.py` | ✅ 已实现 | |

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
