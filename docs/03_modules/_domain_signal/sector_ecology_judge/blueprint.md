---
module_id: MOD-SIG-143
title: "板块级市场状态三态判定蓝图 — 主线清晰/高潮/混沌"
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

# MOD-SIG-143 Sector Ecology Judge — 板块级市场状态三态判定 蓝图

> **module_id**: MOD-SIG-143 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L2-04；下游=L3-06 环境开关六段归并/L2 板块排序（待接线）
> **出身**：晨审定性"三态判据需阈值裁定"；Owner 2026-09-12 授权架构师自行裁定令后落地。

## 1. 三态判定（节点 TDM-E-L2-04 algo_note 逐条对码）

优先级（风险方向优先）：**CLIMAX > MAINLINE_CLEAR > CHAOS**。

| 态 | 判据 | 阈值出处 |
|---|---|---|
| CLIMAX 高潮 | 高潮分 ≥ 90 | sector_rotation_state 既有文档阈值（高潮≥90） |
| MAINLINE_CLEAR 主线清晰 | 梯队连击 ≥ 2 且 Top2 成交集中度 ≥ 30% | MOD-SIG-064"lead_streak<2=无主线混沌"反向 + 节点真源"吸走 30%+成交额" |
| CHAOS 混沌 | 其余 | —— |

## 2. 阈值裁定（架构师分析过程，2026-09-12）

零自创数字：三个阈值全部取自已锚定模块的既有文档口径（见上表"出处"列）。
节点真源"1-2 个板块吸走 30%+成交额"中的 30% 直接落为集中度下限；
连击 2 与高潮 90 分别是 mainline/rotation 件的既有关注线。判定为封闭三态，
输入越界 fail-closed。

## 3. 查重分工

子件承载：L2-04-1 sector_rotation_state（五分类/高潮分）、L2-04-2 sector_siphon（虹吸）、
mainline_probability MOD-SIG-064（主线概率/无主线混沌判据）。本件只做三态收敛判定
（三个子件结论的合成器），不重复任何子件算法。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-143`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-143` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-143` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-143 | MOD-SIG-143 | ✅ |
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


## 4. 研究依据（2026-09-12 全网调研，架构师复核）

- **集中度指标=机构标准做法**：RBC《The Great Narrowing》、Barclays Private Bank（2025-10）、MDPI 同行评审论文（成交量集中度作为广度指标）——头部集中度/市场广度是 2024-2025 机构研究的核心风险指标；"指数涨而广度恶化=晚周期风险信号"与本节点"高潮=次日分歧"的判定同构。
- **本件 30% 集中度阈值**与机构实践的 Top-N 集中度比率口径一致；高潮分 90 沿用内部 rotation 件文档阈值。
- 升级建议（登记，生产接线时评估）：三态边界（89-91/29-31）输出"灰色带"标记（ambiguity flag），避免贴线误判；或引入 HMM 软分类作对照。
