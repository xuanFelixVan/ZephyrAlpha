---
module_id: MOD-SIG-158
title: "A05 财务源线判据转化器蓝图 — 改善五档×定价滞后（PEAD）判据"
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

# MOD-SIG-158 Fundamental Pricing Lag Criterion — A05 财务源线判据转化器 蓝图

> **module_id**: MOD-SIG-158 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L9-A05（源线·财务，module_ref 挂载=总裁终裁批，本班不落图）
> **出身**：施工单 st-fg-srcline1-20261005（红源线首批 6 条判据转化器）；能力反查零命中（新增能力面，2026-10-05 留审计）。

## 1. 判据语义（地图节点 decision_question 逐条对码）

节点问句：**基本面改善能否被定价滞后捕捉？** 本件把财报记录（DS-232 statement 粒度）+ 公告日附近价格序列转为两段判据：

1. **改善五档**（improvement_tier）：单季净利同比五档（IMPROVING_FAST ≥+30% / IMPROVING ≥+10% / FLAT / DETERIORATING / DETERIORATING_FAST ≤−30%，阈值初拟待标定）——改善判据不依赖价格窗，公告即可出；
2. **定价滞后判据**（pead_signal）：公告日跳空（[0]→[1] 收益）方向在 drift 窗（5 交易日初拟）延续 → UNDERPRICED（反应不足可捕捉）；无延续/无跳空 → PRICED；公告后价格不足窗 → UNAVAILABLE（改善档照出）。

## 2. 关键口径（proposed，待实盘标定）

- **PIT 铁律**（A05 节点 algo_note + DS-232 哨兵过滤）：announce_date ≤ 1970-01-02 哨兵命中 → 记录不可信，主入口 fail-closed 拒绝、批量入口静默跳过；改善判据只用公告时点可见数据，价格窗从公告日起算（不含公告日前数据，无前视）。
- **DS 真源注记**：DS-232（financial_derived，粒度=(symbol,report_period,announce_date)，单季同比+派生比率宽表）；DS-208（financial_indicator，miniqmt 夜间增量为源）。yoy_profit 口径由调用方从 DS-232 单季同比字段注入，本件不感知 CH 细节。
- **跳空代理**：公告前收→公告日收（含隔夜跳空+当日反应），非纯开盘跳空——口径粗但免分时数据依赖。

## 3. 查重分工（三重反查留痕 2026-10-05）

CapabilityLookup「财务 PIT 判据」零命中；clone_guard 写前预查 0 findings；既有 FQ/GR 事实侧因子族（DS-232 消费端 M2）产出因子列，本件产出 decision_question 判据（含 PEAD 时序判定，横截面因子族无此口径），正交不并。

## 4. INVARIANTS（代码头部同文）

纯函数核零 IO；PIT 哨兵必拒；改善档三/五值单输出；输入非法 fail-closed（FundamentalLagInputError）；批量面记录级缺陷静默跳过；同输入必同输出。

## 5. 接口

- `build_pricing_lag_criterion(record, post_announce_closes, *, drift_days=5) -> PricingLagCriterion`：主入口。
- `build_from_report_rows(rows, closes_by_symbol, ...)`：批量入口（缺陷记录跳过）。
- 输出 `PricingLagCriterion.to_dict()`：全基本类型，json.dumps 直序列化。
- 测试：`tests/signal_ashare/source_line/test_fundamental_pricing_lag_criterion.py`（18 测）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-158`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-158` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-158` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-158 | MOD-SIG-158 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
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
| `src/zephyr/signal_ashare/source_line/fundamental_pricing_lag_criterion.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/signal_ashare/source_line/test_fundamental_pricing_lag_criterion.py` | ✅ 已实现 | |

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
