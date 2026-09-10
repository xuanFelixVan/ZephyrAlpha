---
module_id: MOD-REGIME-016
title: "大盘指数传感器蓝图 — 均线排列+位置打分"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
ttl: permanent
layer: L02_regime
layer_name: regime
functional_domain: regime
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-10"
last_updated: "2026-09-10"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-REGIME-016 Index Sensor — 大盘指数传感器 蓝图

> **module_id**: MOD-REGIME-016 | **域**: D_REGIME | **层**: L02 市场状态
> **优先级**: P0 | **成熟度**: L1 骨架 | **建设标记**: ✅可建
> **裁定真源**: 地图节点 TDM-E-L1-S1（指数趋势/位置如何·数据面）
> **消费节点**: TDM-E-L1-S1 → L1-AGG（L1 聚合输入）

## 1. 定位

指数趋势分打分器（数据面视角）：均线排列+位置 → 单一趋势分 ∈ [-2, +2]。
节点 algo_note 明文口径：MA20 在 MA60 上=多头加分；指数距 60 日高点<3%=高位减分；
破 MA20 减一档、破 MA60 减两档。

## 2. 打分模型（叠加后 clamp）

| 规则 | 分值 |
|---|---|
| MA20 > MA60（多头排列） | +1 |
| 收盘 < MA20（破位） | -1 |
| 收盘 < MA60（破年线级） | -2（叠加） |
| 距 60 日滚动高点 <3%（高位） | -1 |
| clamp | [-2, +2] |

## 3. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 指数日线收盘序列（DS-150，≥61 根，升序时间只用 ≤t 数据无前视） |
| 输出 | IndexTrendScore：score + ma20/ma60/high60/dist + 各规则命中 + reasons（可审计） |

纯函数核零 IO；样本不足/NaN/负价 fail-closed 抛错；SMA 标准口径。

## 4. 查重分工

index_regime_panel（MOD-REGIME-008）=HMM 七态概率面板（概率分布视角）；
本件=规则打分单一分值视角（节点明文口径），互不替代。D109 攻防板块特征
（券商/银行 5 日超额）归 sector 层特征件。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-REGIME-016`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-REGIME-016` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-REGIME-016` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-REGIME-016 | MOD-REGIME-016 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

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
| `src/zephyr/regime/features/index_sensor.py` | ✅ 已实现 | |

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
