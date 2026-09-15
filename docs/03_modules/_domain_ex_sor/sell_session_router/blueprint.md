---
module_id: MOD-XS-016
title: "卖出单时段路由蓝图 — 时段通道分裂路由"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
ttl: permanent
layer: L06_execution
layer_name: execution
functional_domain: ex_sor
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-10"
last_updated: "2026-09-10"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-XS-016 Sell Session Router — 执行时段路由 蓝图

> **module_id**: MOD-XS-016 | **域**: D_EX_SOR | **层**: L06 执行
> **优先级**: P0 | **成熟度**: L1 骨架 | **建设标记**: ✅可建
> **裁定真源**: 地图节点 TDM-X-S2-03（时段通道分裂路由，D60-D66 X 流终裁）
> **消费节点**: TDM-X-S2-03（现在是什么时段、该走哪条卖出通道）

## 1. 定位

卖出单的 A 股微观结构时段路由器：输入当前时刻+交易所+紧急度，输出卖出通道
（竞价逃命/盘中限价/跳水窗谨慎/做T收口/尾盘竞价/急单市价）+可撤单性+谨慎旗标。
只路由不下单（下单归 optimal_order_router/broker 层）。

## 2. 时段→通道规则（节点语义逐条吸收）

| 时段 | 窗口 | 通道 | 可撤 | 备注 |
|---|---|---|---|---|
| 盘外 | <9:15 / ≥15:00 | NO_ROUTE | — | fail-closed 不给通道 |
| 开盘集合竞价 | 9:15-9:25 | 逃命单=挂跌停价（按开盘价成交，排队最优先）；普通=限价参与竞价 | 9:15-9:20 可撤 / 9:20-9:25 不可撤（A 股通用规则） | 节点原文"竞价逃命单=9:15 后挂跌停价" |
| 开盘缺口 | 9:25-9:30 | 限价（已受理未撮合） | 可撤 | |
| 早盘/午盘 | 9:30-11:30 / 13:00-14:30 | 盘中限价 | 可撤 | |
| 午休 | 11:30-13:00 | 限价（未撮合） | 可撤 | |
| 跳水谨慎窗 | 14:30-14:45 | 谨慎限价（caution=True） | 可撤 | 节点原文"跳水窗谨慎挂单" |
| 决策窗 | 14:45-14:57 | 做T收口（t0_closing_pending 时）/ 盘中限价 | 可撤 | 节点原文"14:50 决策窗处理做T收口"；深市要卖赶在 14:57 前挂 |
| 收盘集合竞价 | 14:57-15:00 | 尾盘竞价 | **深市不可撤**（节点原文）；沪市可撤可改（节点口径，config 可改） | |

## 3. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | hhmm（"HH:MM"）、exchange（SH/SZ）、urgency（NORMAL/ESCAPE）、t0_closing_pending |
| 输出 | RouteDecision：window + channel + cancelable + caution + order_style_hint + note |

纯函数核心，零 IO 零时钟依赖（时刻由调用方注入，可回测可重放）。

## 4. 不变量

1. 盘外时刻恒 NO_ROUTE（fail-closed，不给默认通道）。
2. 非法 hhmm/交易所 → SellSessionRouterError（fail-closed）。
3. ESCAPE 紧急度：竞价时段走竞价逃命（跌停价），其余交易时段走急单市价。
4. 深市收盘竞价 cancelable=False（节点真源）；沪市默认 True，config 可调。
5. 同输入必同输出（frozen 返回值）。

## 5. 消费方

TDM-X-S2-03 节点；卖出决策执行链（S2-02 限价单策略 → S2-03 时段路由 → SOR 下单）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/ex_sor/core/sell_session_router.py` | ✅ 已实现 | |

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

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-XS-016`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-XS-016` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-XS-016` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-XS-016 | MOD-XS-016 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
