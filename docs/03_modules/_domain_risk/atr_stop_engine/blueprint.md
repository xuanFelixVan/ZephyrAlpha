---
module_id: MOD-RK-35
title: "ATR 动态止损与 Bayesian 参数优化蓝图 — k×ATR 参数化止损/分批止盈/时间止损"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
design_maturity: production
build_status: stable
responsibility_domain: 
---

# MOD-RK-35 ATR Stop Engine — ATR 动态止损与 Bayesian 参数优化 蓝图

> **module_id**: MOD-RK-35 | **域**: D_RISK | **层**: L02 盘中实时监控 + L03 离场决策
> **优先级**: P0 | **来源**: CAND-RSK-038（B10-01478，模块43，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-RK-35

## 1. 定位

Wilder(1978) ATR 止损经典落码：止损间距以波动率自适应单位 k×ATR14 参数化
（替代固定百分比），体制自适应 k（趋势 3~4 / 均值回归 1.5~2，ADX>25 用标准 k），
追踪止损只上移不下移，分批止盈 1/3@1R + 1/3@2R + 1/3 追踪，时间止损 N 日未达
1R 平仓。与既有件分工：MOD-SELL-014 为"风格画像→百分比止损参数"映射框架；
本模块为 ATR 波动率单位止损引擎（参数化 k + Bayesian 优化），两者口径互补不重复。

## 2. 输入 / 输出

- 输入：entry_price、atr14（D_FACTOR volatility ATR，调用方注入）、regime
  （trend/mean_reversion/auto+adx）、持仓内最高价/当前价/持有天数；配置（k 档、
  盈亏比 m、时间止损 N）。
- 输出：AtrStopPlan（initial_stop / trailing_stop / profit_targets 三段
  （1/3@1R、1/3@2R、1/3 追踪）/ time_stop_price 与 time_stop_due 标记 / R 单位）。
- 参数优化：bayesian_optimize_k(objective, k_bounds)——轻量高斯过程（RBF 核，
  纯 numpy）+ EI 采集，网格初探 + 序贯优化；grid_search_k 同款接口对照。

## 3. 核心规则

1. 初始止损 = entry − k×ATR（多头；空头取 +）；k 体制自适应：trend→3.5（3~4 中值）、
   mean_reversion→1.75（1.5~2 中值）、auto 由 ADX>25 判 trend 否则 mean_reversion。
2. 追踪止损 = max(历史 trailing, 持仓内最高价 − k×ATR)，只上移不下移（多头）。
3. 1R = k×ATR；分批止盈：TP1=entry+1R（减 1/3）、TP2=entry+2R（再减 1/3）、
   余 1/3 走追踪止损；盈亏比 m≥1.5 校验。
4. 时间止损：持有 > N 日且浮盈 < 1R → 平仓标记（time_stop_due=True）。
5. Bayesian 优化：k∈[1.0,4.0]，目标函数由调用方注入（回测评分），
   GP 代理 + EI 序贯建议；评估点与最优解留痕。
6. Fail-Closed：entry/ATR 非正、regime 非法、k 越界、价格序列非有限 → 拒绝。

## 4. 依赖前置

- D_FACTOR volatility ATR（factor/technical_indicators/volatility.py，调用方注入 ATR14）
- MOD-SELL-014 strategy_specific_stop_framework（风格止损框架，口径互补）

## 5. 验收标准

- 单测全绿（初始/追踪只上移/分批止盈价位与时间止损/体制 k 映射/Bayesian 优化
  收敛于合成目标最优点附近且留痕/非法输入拒绝）；tests/risk 域集成零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-35`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-35` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-35` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-35 | MOD-RK-35 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/risk/atr_stop_engine.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_atr_stop_engine.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
