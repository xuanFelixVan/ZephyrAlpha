---
module_id: MOD-SIG-159
title: "A06 资金流源线判据转化器蓝图 — 流向持续×信念度×跟随判据"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: design
ttl: permanent
layer: L05_signal
layer_name: signal
functional_domain: ashare_signal
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-10-08"
last_updated: "2026-10-08"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-159 Capital Flow Direction Criterion — A06 资金流源线判据转化器 蓝图

> **module_id**: MOD-SIG-159 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L9-A06（源线·资金流，module_ref 挂载=总裁终裁批，本班不落图）
> **出身**：全流通总包交接令 R6（st-fullflow2-20261008）；红源线首批 6 判据中 st-fg-srcline1-20261005 预登记 token 未建的最后两件之一（本件+A09），按 MOD-SIG-157 同构先例补建；能力反查零命中（新增能力面，2026-10-08 留审计）。

## 1. 判据语义（地图节点 decision_question 逐条对码）

节点问句：**主力/大单净流向能否预测短期方向？** 本件把个股日度主力净流入序列族（DS-016 TUSHARE moneyflow 日度聚合，CH 表由调用方读取注入）+ 同轴收盘序列转为三段判据：

1. **流向持续性**（streak，带符号）：从末日起逐日计数连续同向天数，零流断号（净流入连续 3 天=+3）；
2. **方向信念度**（conviction）：近 window（默认 10 日）净流累计 / 绝对流累计 ∈[-1,1]，绝对值=同向一致度（对冲流互相抵消趋 0）；
3. **跟随判据**（flow_tier）：conviction ≥+0.6 且 |streak| ≥3 → FOLLOW_IN（主力持续净流入、短期上行跟随预期）；conviction ≤-0.6 且 |streak| ≥3 → FOLLOW_OUT；|conviction| ≥0.3 → WATCH；其余 NONE。双门设计防"单日脉冲流"误报。

价流背离注记（note 级不改档）：近 window 价格涨而 conviction <-0.3 → 顶背离；价格跌而 conviction >+0.3 → 底背离。

## 2. 关键口径（proposed，待实盘标定）

- **符号语义分工**：方向由 conviction 符号承载、持续性由 |streak| 承载，单处判号防漂移（判档取 abs(streak)，红测覆盖带符号双路）。
- **零流动窗**：绝对流累计=0 → conviction 记 0 判 NONE 记 notes（不编方向，不 fail）。
- **PIT 注记**（A06 节点 algo_note）：日度聚合盘后落定不修订。
- **正交性**：moneyflow 数据管道（采集/落库/聚合）与本件（序列 → 判据）问句不同不并；sector_rotation（MOD-SIG-157 板块横截面）与个股流向判据不并。

## 3. 查重分工（三重反查留痕 2026-10-08）

CapabilityLookup「check_tick_duplication/data_supply_chain_map/tick 判重/判重正门」+「capital_flow_direction」系列留审计（`.runtime/lookup_audit/`）；clone_guard 同构先例对照：本件与 MOD-SIG-157 共享"序列→判据快照"骨架但字段/判据/入口全异（流向 vs 收益、横截面分位 vs 时序信念度）；signal_ashare 全域无第二份资金流判据件。

## 4. INVARIANTS（代码头部同文）

纯函数核零 IO（流水/收盘序列调用方注入升序）；conviction ∈[-1,1] 单值输出；输入非法 fail-closed（CapitalFlowInputError）；单标的缺陷跳过记 notes 不整体 fail（全败 raise 带跳过原因，先例同款）；同输入必同输出。

## 5. 接口

- `build_capital_flow_snapshot(flows_by_symbol, closes_by_symbol, *, window=10) -> CapitalFlowSnapshot`：主入口（标的→序列族）。
- `build_from_moneyflow_rows(rows, closes_by_symbol, ...)`：DS 读入形态入口（symbol/trade_date/net_main_amount 行字典序列，缺陷行跳过计数）。
- `flow_streak(flows)`：带符号连续同向天数（可独立复用）。
- 输出 `CapitalFlowSnapshot.to_dict()`：全标的判据+follow_in/follow_out 清单，json.dumps 直序列化。
- 测试：`tests/signal_ashare/source_line/test_capital_flow_direction_criterion.py`（红蓝 25 测：边界/确定性/契约手算对拍/fault 注入）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-159`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-159` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-159` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-159 | MOD-SIG-159 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | N/A | — |
| file_count | 2 文件 | N/A | — |

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
| — | — | 本模块尚无已实现代码 |

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
