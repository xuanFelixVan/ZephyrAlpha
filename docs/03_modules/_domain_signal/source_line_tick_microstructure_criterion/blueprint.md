---
module_id: MOD-SIG-156
title: "A02 Tick分笔源线判据转化器蓝图 — 买卖不平衡×冲击成本×次日方向判据"
doc_type: blueprint
status: Active
version: "0.1.0"
design_maturity: design
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
responsibility_domain: ashare_signal
---

# MOD-SIG-156 Tick Microstructure Criterion — A02 Tick分笔源线判据转化器 蓝图

> **module_id**: MOD-SIG-156 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L9-A02（源线·Tick分笔，module_ref 挂载=总裁终裁批，本班不落图）
> **出身**：施工单 st-fg-srcline1-20261005（红源线首批 6 条判据转化器）；能力反查零命中（新增能力面，2026-10-05 留审计）。

## 1. 判据语义（地图节点 decision_question 逐条对码）

节点问句：**日内微观结构能否预测次日方向与冲击成本？** 本件把标准化 tick 成交流（DS-001 口径）转为三段判据：

1. **主动性买卖不平衡**（imbalance）：买向成交量占比 − 卖向占比，∈[-1,1]，五档（STRONG_BUY/BUY/NEUTRAL/SELL/STRONG_SELL），阈值 ±0.10/±0.25 初拟待标定；
2. **冲击成本代理**（impact_coef）：Kyle-λ 简化代理 = Σ|Δprice|/Σvolume（相邻笔价格差绝对值累加 ÷ 后笔量累加，值越大流动性越薄）；
3. **方向判据**（direction_lean）：不平衡档 + 尾段动量（末 max(5, 10%笔数) 笔净收益方向）同向 → long/short，背离或尾段不可判 → flat 不编方向。

## 2. 关键口径（proposed，待实盘标定）

- **方向别名归一**：B/b/buy/BUY/1=买向；S/s/sell/SELL/0/-1=卖向；其余 fail-closed。
- **冲击成本代理**取差分绝对值口径（非回归斜率）——样本内无窗宽选择问题，代理量纲=每手推动的价格幅度。
- **PIT 注记**（A02 节点 algo_note）：TDX 分笔仅近交易日，历史依赖包断档不可补——本件不补数，缺口由调用方感知。
- **DS 真源注记**：DS-001（market_data.tick，CTR-001 NormalizedMarketData，candidate）；DS-057（tick_data_manager）deprecated，读入形态按 DS-001 契约。

## 3. 查重分工（三重反查留痕 2026-10-05）

CapabilityLookup「tick 微观结构」零命中；clone_guard 写前预查 0 findings；既有 auction_microstructure_analyzer（集合竞价微观）与本件（连续成交 tick 流）输入面与问句正交，不并。

## 4. INVARIANTS（代码头部同文）

纯函数核零 IO（tick 序列调用方注入升序）；不平衡 ∈[-1,1] 单值输出；输入非法 fail-closed（TickMicroInputError）；记录级缺陷跳过记 notes；同输入必同输出；tick 断档不补数。

## 5. 接口

- `build_tick_micro_criterion(symbol, prices, volumes, sides) -> TickMicroCriterion`：主入口（三元序列）。
- `build_from_ticks(symbol, ticks)`：DS 读入形态入口（tick 字典序列，缺陷笔跳过记 notes）。
- 输出 `TickMicroCriterion.to_dict()`：全基本类型，json.dumps 直序列化。
- 测试：`tests/signal_ashare/source_line/test_tick_microstructure_criterion.py`（21 测）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-156`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-156` 的 1 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-156` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-156 | MOD-SIG-156 | ✅ |
| domain_id | N/A | ashare_signal | — |
| build_status | planned | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
