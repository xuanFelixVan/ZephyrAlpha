---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.0.0"
date: 2026-08-03
---

# 作战地图·对账阶段

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/_zoomable_html/battle_map_06_reconciliation.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

> battle_map §reconciliation 阶段，5 环节。
> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编。

## 文档基本信息 / Document Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 阶段 | 对账（reconciliation） | Stage | 对账 |
| 环节数 | 5 | Steps | 5 |
| 流转边 | 7 | Edges | 7 |
| 状态分布 | 🟦 运营态（已建）=5 | State Distribution | 🟦 运营态（已建）=5 |

> **图例说明 / Legend**：
> - 🟦 **蓝色实线 = 运营态环节**（production，锚点模块已建）
> - 🟧 **橙色虚线 = 设计态环节**（design，锚点模块待施工）
> - 🟥 **红色 = 弃用态**（deprecated）
> - ⬜ **灰色 = 缺失态**（missing，环节无锚点，BM-INV-001 违例）
> - 🟨 **黄色虚线 = 候选态**（candidate，承载模块在候选池）
> - **实线箭头 ``-->`` = 运营态流转**（两端均 production）
> - **虚线箭头 ``-.->`` = 非运营态流转**（含设计/候选/混合）

## 阶段图 / Stage Diagram

> 展示 对账 阶段全部 5 个环节及流转边，颜色区分五态。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
%% 对账阶段图
flowchart TD
    BM_REC_01["【BM-REC-01 交易运营清算】<br/>把成交回报拿去结算对账、算费率、处理除权除息和公<br/>司行为、监控保证金，变成运营数据。<br/>对账阶段 / reconciliation<br/>（生产态 / production）<br/>【Trade Ops &amp; Settlement】"]
    BM_REC_02["【BM-REC-02 报告复盘】<br/>把运营数据做成复盘报告，看今天打得怎么样。<br/>对账阶段 / reconciliation<br/>（生产态 / production）<br/>【Reporting &amp; Review】"]
    BM_REC_03["【BM-REC-03 闭环优化反馈】<br/>复盘完把教训反馈回每一层——因子衰减就换、信号不准<br/>就退、模型漂移就重训，形成正向闭环。<br/>对账阶段 / reconciliation<br/>（生产态 / production）<br/>🟡候选承载<br/>【Closed-Loop Optimization Feedback】"]
    BM_REC_04["【BM-REC-04 保证金管理】<br/>监控融资融券保证金比例——低于预警线告警、需要追加<br/>时提醒用户；融资融券API不可用时自动休眠，不影响<br/>其他运营功能。<br/>对账阶段 / reconciliation<br/>（生产态 / production）<br/>【Margin Manager】"]
    BM_REC_05["【BM-REC-05 多账户分仓管理】<br/>一个策略同时管多个账户，按各账户AUM分仓，每个账<br/>户独立风控、独立PnL、独立报告。多账户≠多租户SaaS<br/>，所有账户属于同一信任域。<br/>对账阶段 / reconciliation<br/>（生产态 / production）<br/>【Multi-Account Manager】"]
    BM_REC_02 ~~~ BM_REC_04 ~~~ BM_REC_05
    BM_REC_01 -->|运营数据 / data_flow| BM_REC_02
    BM_REC_02 -->|复盘报告 / data_flow| BM_REC_03
    BM_REC_01 -->|保证金监控消费清算数据 / data_flow| BM_REC_04
    BM_REC_01 -->|多账户独立核算消费清算数据 / data_flow| BM_REC_05
classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
classDef deprecated fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
classDef missing fill:#eeeeee,stroke:#9e9e9e,stroke-width:2px,color:#000
classDef candidate fill:#fffde7,stroke:#f9a825,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    class BM_REC_01,BM_REC_02,BM_REC_03,BM_REC_04,BM_REC_05 production
```

## 环节详情

### BM-REC-01 交易运营清算 / Trade Ops & Settlement

> **大白话**：把成交回报拿去结算对账、算费率、处理除权除息和公司行为、监控保证金，变成运营数据。

**机制说明**：

L5/运营层。C-017 交易运营五子能力：①保证金管理(D-TRADING-04 融资融券保证金比例监控/预警/追加)②结算对账(D-TRADING-02 每日15:30后自动对账，系统记录vs券商结算单，差异告警，A股T+1)③除权除息(D-TRADING-03 除权日自动调整持仓成本+目标价)④费率(D-TRADING-03 佣金/印花税/过户费计算→向C-010供PnL数据)⑤公司行为(D-TRADING-03 分红/配股/拆股监控→通知用户)。
是闭环反馈路径的起点，承接 C-002 交易执行产出。事件：E-TR-01 SettlementCompleted / E-TR-02 ReconciliationCompleted / E-TR-03 CorporateActionAdjusted / E-TR-04 MarginWarning / E-TR-05 MarginUnavailable。
降级：融资融券API不可用时保证金管理自动休眠，休眠期间向C-004发送E-TR-05"保证金数据不可用"事件。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 成交回报就绪 + 每日15:30自动触发(A股T+1) 阈值: settles_at=15:30 |
| ② 消费数据/因子 | BM-EXE-02 成交回报<br>券商结算单 |
| ③ 参数 | settle_cycle=T+1（范围 T+0/T+1，代码当前: T+1，状态: production）<br>settles_at=15:30（范围 盘后时段，代码当前: None，状态: proposed）<br>fee_types=佣金/印花税/过户费（范围 —，代码当前: None，状态: proposed）<br>corporate_action_types=分红/配股/拆股（范围 —，代码当前: None，状态: proposed） |
| ④ 数据流 | 输入: 成交回报 + 券商结算单 → 处理: C-017 ①保证金/②结算对账/③除权除息/④费率/⑤公司行为 → 输出: 运营数据 + E-TR-01/02/03/04/05事件 → 下游: BM-REC-02 报告复盘, C-010 PnL(费率数据) |
| ⑤ 代码映射 | D-TRADING-02/03/04 / C-017 §1.8 闭环 |
| ⑥ 降级/中止 | C-017不可用 或 融资融券API不可用 → C-017不可用→手动清算兜底；融资融券API不可用→保证金管理休眠+E-TR-05 |

**指标文案（翻译真源 indicators_zh）**：

①触发：成交回报就绪 + 结算对账每日15:30自动触发(A股T+1)；②消费：BM-EXE-02 成交回报 + 券商结算单；③参数：settle_cycle=T+1、settles_at=15:30、fee_types=佣金/印花税/过户费、corporate_action_types=分红/配股/拆股；④数据流：成交回报→C-017①保证金/②结算对账/③除权除息/④费率/⑤公司行为→运营数据→BM-REC-02，费率→C-010 PnL；⑤代码：D-TRADING-02/03/04(未开发)、C-017 §1.8 闭环；⑥降级：C-017不可用→手动清算兜底，融资融券API不可用→保证金管理休眠+E-TR-05。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-TRADING-003 | primary | planned | generated |
| depgraph | MOD-RPT-027 | supplement | planned | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L5 ｜ **阶段**：reconciliation

### BM-REC-02 报告复盘 / Reporting & Review

> **大白话**：把运营数据做成复盘报告，看今天打得怎么样。

**机制说明**：

L5 层。C-010 报告复盘：把运营数据加工成复盘报告，作为闭环优化的输入素材。MOD-RPT-027 是自我复盘的输入素材。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 运营数据就绪 阈值: 复盘报告 |
| ② 消费数据/因子 | 运营数据（来自 BM-REC-01） |
| ③ 参数 | report_freq=日/周（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 运营数据 → 处理: C-010 报告复盘 → 输出: 复盘报告 → 下游: BM-REC-03 闭环优化 |
| ⑤ 代码映射 | C-010 / 草图§1.8 闭环反馈 |
| ⑥ 降级/中止 | C-010 不可用 → 降级基础 PnL 报表 |

**指标文案（翻译真源 indicators_zh）**：

①触发：运营数据就绪；②消费：BM-REC-01 运营数据；③参数：report_freq=日/周；④数据流：运营数据→C-010 报告复盘→复盘报告→BM-REC-03；⑤代码：C-010 §1.8 闭环；⑥降级：C-010 不可用→基础 PnL 报表。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-RPT-026 | primary | planned | generated |
| depgraph | MOD-RPT-015 | supplement | planned | planned |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L5 ｜ **阶段**：reconciliation

### BM-REC-03 闭环优化反馈 / Closed-Loop Optimization Feedback

> **大白话**：复盘完把教训反馈回每一层——因子衰减就换、信号不准就退、模型漂移就重训，形成正向闭环。

**机制说明**：

L5 层。C-007 闭环优化：反馈到 L1~L4+L3.5 每层（IC衰减→因子替代、准确率监控→信号退役、漂移检测→模型重训练、A/B 淘汰、阈值校准）。每轮迭代改动必须经过 C-003 回测门禁。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 复盘报告就绪 阈值: 反馈到 L1~L4+L3.5 每层 |
| ② 消费数据/因子 | 复盘报告（来自 BM-REC-02） |
| ③ 参数 | feedback_layers=L1~L4+L3.5（范围 -，代码当前: IC衰减1~20期(max_lag=20)+半衰期(compute_half_life)——单层因子质量反馈; L1~L4+L3.5多层架构未完整实现，状态: implemented） |
| ④ 数据流 | 输入: 复盘报告 → 处理: C-007 闭环优化（IC衰减/准确率/漂移检测→重训练） → 输出: 因子/信号/策略/风控迭代信号 → 下游: BM-SEL-02 因子计算（反向闭环） |
| ⑤ 代码映射 | C-007 / 草图§1.8 闭环反馈 |
| ⑥ 降级/中止 | C-007 不可用 → 降级人工复盘 |

**指标文案（翻译真源 indicators_zh）**：

①触发：复盘报告就绪；②消费：BM-REC-02 复盘报告；③参数：feedback_layers=L1~L4+L3.5；④数据流：复盘报告→C-007 闭环优化→迭代信号→BM-SEL-02（反向闭环）；⑤代码：C-007 §1.8 闭环；⑥降级：C-007 不可用→人工复盘。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-L02-004 | primary | production | stable |
| candidate | CAND-WFO-001 | supplement | deferred | — |
| candidate | CAND-SIM-002 | supplement | deferred | — |
| candidate | CAND-BT-001 | supplement | deferred | — |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L5 ｜ **阶段**：reconciliation

### BM-REC-04 保证金管理 / Margin Manager

> **大白话**：监控融资融券保证金比例——低于预警线告警、需要追加时提醒用户；融资融券API不可用时自动休眠，不影响其他运营功能。

**机制说明**：

L5/运营层。C-017●核心子能力①保证金管理(D-TRADING-04)。融资融券保证金比例监控/预警/追加提醒。
降级可休眠：融资融券API不可用时自动休眠，休眠期间向C-004发送E-TR-05"保证金数据不可用"事件，不阻塞结算对账/除权费率等其他运营功能。
事件：E-TR-04 MarginWarning（保证金比例低于预警线）/ E-TR-05 MarginUnavailable（保证金API不可用，休眠）。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 融资融券持仓+保证金比例实时监控 阈值: margin_warning_line/margin_maintain_line |
| ② 消费数据/因子 | BM-REC-01 清算数据<br>券商融资融券API |
| ③ 参数 | margin_warning_line=预警线（范围 —，代码当前: None，状态: proposed）<br>margin_maintain_line=维持担保比例线（范围 —，代码当前: None，状态: proposed） |
| ④ 数据流 | 输入: 清算数据+融资融券API → 处理: D-TRADING-04 保证金监控 → 输出: E-TR-04预警/E-TR-05不可用 → 下游: C-004风控+用户通知 |
| ⑤ 代码映射 | D-TRADING-04 / C-017① 保证金管理 |
| ⑥ 降级/中止 | 融资融券API不可用 → 保证金管理休眠+E-TR-05，其他运营功能不受影响 |

**指标文案（翻译真源 indicators_zh）**：

①触发：融资融券持仓+保证金比例实时监控；②消费：BM-REC-01 清算数据 + 券商融资融券API；③参数：margin_warning_line=预警线、margin_maintain_line=维持担保比例线；④数据流：清算数据→D-TRADING-04 保证金监控→E-TR-04预警/E-TR-05不可用→C-004风控+用户通知；⑤代码：D-TRADING-04(未开发)、C-017①；⑥降级：融资融券API不可用→保证金管理休眠+E-TR-05，其他运营功能不受影响。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-TRADING-003 | supplement | planned | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L5 ｜ **阶段**：reconciliation

### BM-REC-05 多账户分仓管理 / Multi-Account Manager

> **大白话**：一个策略同时管多个账户，按各账户AUM分仓，每个账户独立风控、独立PnL、独立报告。多账户≠多租户SaaS，所有账户属于同一信任域。

**机制说明**：

L5/运营层。C-018●核心多账户多策略(D-TRADING-05)。按AUM分仓/独立风控/独立PnL/独立报告。
多账户≠多租户SaaS：所有账户属于同一信任域，无需租户隔离。
事件：E-TR-06 MultiAccountAllocated（多账户分仓完成）。
与BM-BUY-06联动：外部指令按AUM分仓到多账户；与BM-REC-01联动：多账户独立结算对账。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 交易指令需多账户分仓时 + 对账时多账户独立核算 阈值: 多账户场景 |
| ② 消费数据/因子 | BM-BUY-03 决策编排产出<br>各账户AUM<br>BM-REC-01 清算数据 |
| ③ 参数 | alloc_method=按AUM（范围 按AUM/等额，代码当前: None，状态: proposed）<br>independent_risk=独立风控（范围 —，代码当前: None，状态: proposed）<br>independent_pnl=独立PnL（范围 —，代码当前: None，状态: proposed）<br>independent_report=独立报告（范围 —，代码当前: None，状态: proposed） |
| ④ 数据流 | 输入: 决策编排产出+各账户AUM → 处理: D-TRADING-05 按AUM分仓 → 输出: E-TR-06分配结果 → 下游: D-REPORTING独立报告 |
| ⑤ 代码映射 | D-TRADING-05 / C-018 多账户多策略 |
| ⑥ 降级/中止 | 多账户模式不可用 → 单账户模式→不分仓直接执行 |

**指标文案（翻译真源 indicators_zh）**：

①触发：交易指令需多账户分仓时 + 对账时多账户独立核算；②消费：BM-BUY-03 决策编排产出 + 各账户AUM + BM-REC-01 清算数据；③参数：alloc_method=按AUM、独立风控/独立PnL/独立报告；④数据流：决策→D-TRADING-05 按AUM分仓→E-TR-06分配结果→D-REPORTING独立报告；⑤代码：D-TRADING-05(未开发)、C-018；⑥降级：单账户模式→不分仓直接执行。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-TRADING-003 | supplement | planned | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L5 ｜ **阶段**：reconciliation


[← 返回总指挥图](battle_map_panorama.md)