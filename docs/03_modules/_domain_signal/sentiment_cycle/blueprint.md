---
module_id: MOD-SIG-140
title: "五阶段情绪周期蓝图 — 冰点/反核/主升/疯狂/退潮"
doc_type: blueprint
status: Active
version: "0.1.4"
design_maturity: production
ttl: permanent
layer: L01_market
layer_name: market
functional_domain: signal_ashare
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-11"
last_updated: "2026-09-11"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-140 Sentiment Cycle — 五阶段情绪周期 蓝图

> **module_id**: MOD-SIG-140 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L2-05-1（水温档推导，主判）
> **出身**：晨审 D1 depgraph 编号规范化批（st-tdm-review-20260911 §四 D1；Owner 四批开工令批 4）——原 [BLUEPRINT] 头挂设计备忘录 spec 引用，无正规 MOD id，地图 R21 交叉锚无法回填。本件=该模块的正式 MOD 蓝图注册，设计真源保留引用。

## 1. 模块语义（摘自代码头/INVARIANTS）

SentimentPhase 五阶段枚举（冰点/反核/主升/疯狂/退潮）+ phase_prob 归一分布 + PHASE_DISCIPLINE 五阶段买卖纪律硬约束 + STRATEGY_DEPLOYMENT_MATRIX（3 策略×5 阶段部署矩阵）+ 水温档推导（L1 五档水温→档位主判）。

## 2. 设计真源

design_memos/28_sentiment_cycle_trading.md §3.2-§3.10（原 [BLUEPRINT] 头引用）。注意：模块 MATURITY=new，待 G07 相关性验证（晨审 §7.1 L2-05 挂起链路的既有定性，本注册不改变该状态）。

## 3. 注册说明

- 编号 MOD-SIG-140 于 2026-09-11 由 night-gw-2300 会话在 D1 批内分配注册（depgraph 设计态）。
- 本蓝图只做身份注册与语义索引，不改模块行为；模块成熟度见代码头 [MATURITY]。

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/sentiment/sentiment_cycle.py` | ✅ 已实现 | |

### 4.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §4（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-140`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-140` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-140` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-140 | MOD-SIG-140 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
