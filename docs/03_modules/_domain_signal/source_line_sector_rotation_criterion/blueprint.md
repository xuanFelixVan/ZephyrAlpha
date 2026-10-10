---
module_id: MOD-SIG-157
title: "A03 板块/概念指数源线判据转化器蓝图 — 相对强度分位×持续跑赢×领先性判据"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
ttl: permanent
layer: L05_signal
layer_name: signal
functional_domain: ashare_signal
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-10-05"
last_updated: "2026-10-05"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-157 Sector Rotation Criterion — A03 板块/概念指数源线判据转化器 蓝图

> **module_id**: MOD-SIG-157 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L9-A03（源线·板块/概念指数，module_ref 挂载=总裁终裁批，本班不落图）
> **出身**：施工单 st-fg-srcline1-20261005（红源线首批 6 条判据转化器）；能力反查零命中（新增能力面，2026-10-05 留审计）。

## 1. 判据语义（地图节点 decision_question 逐条对码）

节点问句：**板块轮动与强弱持续性能否领先个股？** 本件把板块指数日收盘序列族（DS-117 概念板块 / DS-119 概念行业，CH 表由调用方读取注入）转为三段判据：

1. **相对强度分位**（rs_rank_pct）：板块 N 日收益（N=20 初拟）在全板块横截面的分位 ∈[0,1]，1=最强；
2. **领涨持续性**（streak）：板块连续跑赢市场基准（日收益比对）天数，从末日起逐日计数，跑输即断；
3. **领先性判据**（lead_tier）：RS ≥0.8 且 streak ≥3 → LEAD（板块领先、成分股跟随预期）；RS ≥0.6 → WATCH；其余 NONE。双门设计防"一日游板块"误报（A 股板块一日游特征在案，spec §2.3）。

## 2. 关键口径（proposed，待实盘标定）

- **横截面分位**：rank/(n−1)，单板块时取 0.0（无可比横截面，不编方向）。
- **基准**：市场基准日收盘序列由调用方注入（同交易日轴）。
- **PIT 注记**（A03 节点 algo_note）：指数快照落定不修订，成分随披露更新。
- **正交性**：sector_rotation_state（MOD-SIG-026 系，市场级 5 状态快照）与本件（源线级逐板块判据）口径与消费面不同，不并。

## 3. 查重分工（三重反查留痕 2026-10-05）

CapabilityLookup「板块轮动判据」零命中；clone_guard 写前预查 0 findings；sector/ 族（rotation_state/sector_momentum/rrg 等）均为信号算法件（多源合成打分），本件是源线判据件（板块指数序列 → decision_question 判据），问句不同不并。

## 4. INVARIANTS（代码头部同文）

纯函数核零 IO（板块序列调用方注入升序）；RS 分位 ∈[0,1] 单值输出；基准非法/板块族空 fail-closed（SectorRotationInputError）；单板块缺陷跳过记 notes；同输入必同输出。

## 5. 接口

- `build_sector_rotation_snapshot(board_closes, benchmark_closes, *, window=20) -> SectorRotationSnapshot`：主入口（板块→收盘序列族）。
- `build_from_index_rows(rows, benchmark_closes, ...)`：DS 读入形态入口（board/date/close 行字典序列，缺陷行跳过记 notes）。
- 输出 `SectorRotationSnapshot.to_dict()`：全板块判据+lead_boards 清单，json.dumps 直序列化。
- 测试：`tests/signal_ashare/source_line/test_sector_rotation_criterion.py`（16 测）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-157`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-157` 的 1 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-157` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-157 | MOD-SIG-157 | ✅ |
| domain_id | N/A | ashare_signal | — |
| build_status | planned | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/source_line/sector_rotation_criterion.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/signal_ashare/source_line/test_sector_rotation_criterion.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
