---
module_id: MOD-L08-001
submodule_path: src/zephyr/frontend
title: "Human Machine Interface Core 蓝图 — 人机交互层"
doc_type: blueprint
status: Active
version: "3.1.0"
layer: L3_application
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/frontend/"
last_updated: "2026-07-05"
last_verified: "2026-07-05"
generation: 2
functional_domain: interface
summary: "业务层已开放，可施工。人机交互层。DashboardBase+NotificationManagerBase+ApprovalGatewayBase为OCP扩展点。v3.0.0(#ARCH-047)技术栈切换: Streamlit→Panel+HoloViz+Plotly+plotly_resampler+Lightweight Charts; ChartFactory图表统一工厂(callback仅编排); 5个交易/回测组件(backtest_results/tick_replay/order_book/position_monitor/trade_panel)已迁移至Panel+HoloViz。v3.1.0(#ARCH-047): 5个旧Streamlit页面(fitness_functions/gate_statistics/knowledge_overview/olap_trend/task_progress)迁移至Panel; 新建app_panel.py主应用入口(pn.Tabs组装10个Tab); ChartFactory新增make_gate_chart/make_trend_line; 仪表盘可运行(panel serve --show)。"
tags: [human-ai-interface, l08, dashboard, panel, holoviz, plotly, notification, approval, backtest-visualization, real-trading-panel]
priority: P1
runtime_plane: warm
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-INF-FLE
    at: "§10"
    why: "FitnessFunctionFramework + FitnessInputs"
  - target: MOD-DATABASE
    at: "§10"
    why: "TaskRepository"
  - target: "MOD-BT-001"
    at: "§4.1"
    why: "v2.2.0新增: backtest_results/tick_replay组件消费D_BACKTEST回测结果与Tick回放数据(BacktestResult/CTR-P1-016)"
  - target: "MOD-L06-001"
    at: "§4.1"
    why: "v2.2.0新增: trade_panel/position_monitor组件调用D_EX_CORE ExecutionEngine.execute_order(broker_id='miniqmt')触发实盘下单, MiniQmtBroker.get_positions()展示实盘持仓"
  - target: "MOD-L00-001"
    at: "§16.7.1"
    why: "v2.2.0新增: order_book组件调用D_DATA MiniQmtProvider.get_order_book()展示5档盘口"
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture_model\\layers\\l08_human_ai_interface.yaml"
    section: ""
    why: "架构层YAML真源"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_backtest\\blueprint.md"
    section: "§4.1 / §16.7"
    why: "BacktestResult(CTR-P1-016) + tick_replay规格, backtest_results/tick_replay组件数据源"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_execution_core\\blueprint.md"
    section: "§4.1 / §16.7.1"
    why: "ExecutionEngine.execute_order + MiniQmtBroker.get_positions, trade_panel/position_monitor组件调用接口"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_data\\blueprint.md"
    section: "§16.7.1"
    why: "MiniQmtProvider.get_order_book(5档盘口), order_book组件数据源"
codification_level: L1
codification_at: "2026-05-15"
responsibility_domain: 
build_status: generated
design_maturity: design
---

> ✅ **C轨业务层已开放，可施工**
>
> C轨业务层已解除占位禁令[ARCH-045 P0]。AI 可自主施工。
> 当前 construction_progress = partially_implemented，可继续业务代码实现。

> module_id: MOD-L08-001 | version: 3.1.0 | status: active | domain: frontend
> actual_disk_path: src/zephyr/frontend/ | generation: 2 | construction_progress: partially_implemented
> v2.2.0新增: 5个交易/回测组件(backtest_results/tick_replay/order_book/position_monitor/trade_panel), 对接D_BACKTEST/D_EX_CORE/D_DATA, 支持joinquant/Qbot风格仪表盘+实盘交易面板
> v3.0.0(#ARCH-047): Streamlit→Panel+HoloViz+Plotly+plotly_resampler+Lightweight Charts; 新增ChartFactory(callback仅编排); 5组件已迁移
> v3.1.0(#ARCH-047): 5旧页面迁移至Panel; 新建app_panel.py主入口(pn.Tabs 10 Tab); ChartFactory新增make_gate_chart/make_trend_line; 仪表盘可运行

# Human Machine Interface Core 蓝图+施工图 — 人机交互层

> **真源声明**：本蓝图是 ZephyrAlpha 人机交互层的唯一真源。

## 概述

本蓝图描述 ZephyrAlpha 人机交互层——它解决了系统与用户之间的标准化交互问题。核心职责包括：监控面板(DashboardBase)、通知分发(NotificationManagerBase)、人工审批(ApprovalGatewayBase)三个 OCP 扩展点，以及 Streamlit Dashboard 5 页面组件。当前规模 3 个 Base 类 + 5 个 Dashboard 组件已实现，DefaultNotificationManager 和 DefaultApprovalGateway 待施工。上游依赖 FLE Fitness Functions 和 TaskRepository，下游被 D_RISK 和 D_REPORTING 消费。

**v2.2.0 新增决策(2026-07-04)**：扩展现有 Streamlit Dashboard，新增 5 个交易/回测组件，支持 joinquant/Qbot 风格仪表盘 + 实盘交易面板：
1. **backtest_results.py**: 回测结果可视化——净值曲线/回撤/Sharpe/Sortino/MaxDD/IC/IR 图表 + 3阶段决策门控(IS→WFA→OOS)状态展示
2. **tick_replay.py**: Tick回放可视化——按时间戳逐Tick回放(支持real_time/fast_forward/max_speed)+5档盘口快照+做T场景(30秒/5秒冲高回落)标记
3. **order_book.py**: 5档盘口实时展示——askPrice[5档]/bidPrice[5档]/askVol[5档]/bidVol[5档]实时刷新+盘口压力可视化
4. **position_monitor.py**: 实盘持仓监控——实时持仓(可用/冻结/当日买入)+未实现盈亏+T+1锁定提示+账户资金
5. **trade_panel.py**: 实盘交易面板——下单表单(代码/方向/数量/价格/算法)+订单列表(状态机实时更新)+撤单按钮+风控提示

> **设计原则**: 5个新组件复用 DashboardBase OCP 扩展点, 不引入新的 Base 类, 保持架构一致性。组件采用 fetch+render 分离模式, 数据源(D_BACKTEST/D_EX_CORE/D_DATA)通过依赖注入传入, 不直接 import 业务层模块。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L08-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | interface_base.py | §3.1 | DashboardBase + NotificationManagerBase + ApprovalGatewayBase + Notification + ApprovalRequest + NotificationLevel + ApprovalAction | 已实现 |
| 2 | dashboard/app.py | §3.1 | 旧 Streamlit 入口（v3.1.0已弃用，见 app_panel.py；DashboardApp+create_app 保留供测试） | 已实现 |
| 3 | dashboard/components/fitness_functions.py | §3.1 | Fitness Functions 组件 | 已实现 |
| 4 | dashboard/components/gate_statistics.py | §3.1 | 门禁统计组件 | 已实现 |
| 5 | dashboard/components/knowledge_overview.py | §3.1 | 知识库概览组件 | 已实现 |
| 6 | dashboard/components/olap_trend.py | §3.1 | OLAP 趋势组件 | 已实现 |
| 7 | dashboard/components/task_progress.py | §3.1 | 任务进度组件 | 已实现 |
| 8 | dashboard/components/backtest_results.py | §16.7.1 | **v3.0.0迁移** 回测结果可视化(净值曲线/回撤/Sharpe/IC/IR/3阶段门控) | 已实现 |
| 9 | dashboard/components/tick_replay.py | §16.7.2 | **v3.0.0迁移** Tick回放可视化(逐Tick回放/5档盘口快照/做T场景标记) | 已实现 |
| 10 | dashboard/components/order_book.py | §16.7.3 | **v3.0.0迁移** 5档盘口实时展示(askPrice/bidPrice/askVol/bidVol) | 已实现 |
| 11 | dashboard/components/position_monitor.py | §16.7.4 | **v3.0.0迁移** 实盘持仓监控(可用/冻结/当日买入/未实现盈亏) | 已实现 |
| 12 | dashboard/components/trade_panel.py | §16.7.5 | **v3.0.0迁移** 实盘交易面板(下单表单/订单列表/撤单/风控提示) | 已实现 |
| 13 | dashboard/components/chart_factory.py | §3.1 | **v3.0.0新增** 图表统一工厂(make_equity/make_drawdown/make_kline/make_tick/make_heatmap/make_orderbook/make_position/make_orderflow + v3.1.0 make_gate_chart/make_trend_line) | 已实现 |
| 14 | dashboard/app_panel.py | §3.1 | **v3.1.0新增** Panel 主应用入口(pn.Tabs组装10 Tab, pn.serve+.servable) | 已实现 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 部分组件已实现，业务逻辑待填充 | `ls src/zephyr/frontend/` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| §0.1 已实现文件全部存在 | 逐文件 `ls` | ☐ |
| §0.1 未实现文件确实不存在 | 逐文件 `ls` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | DashboardBase, NotificationManagerBase, ApprovalGatewayBase, DashboardApp, 5 个组件 | DefaultNotificationManager, DefaultApprovalGateway | C轨禁止施工 |
| v2.0.0 (模板重构) | 同 v1.0.0 + 结构重组 | DefaultNotificationManager, DefaultApprovalGateway | C轨禁止施工 |
| v2.1.0 (回填+禁止施工) | 同 v2.0.0 + 接口契约与代码对齐 | DefaultNotificationManager, DefaultApprovalGateway | C轨禁止施工 |
| v2.2.0 (交易/回测组件规划) | 同 v2.1.0 | DefaultNotificationManager, DefaultApprovalGateway, 5个交易/回测组件(backtest_results/tick_replay/order_book/position_monitor/trade_panel) | 规划5个新组件规格(§16.7.1~§16.7.5), 对接D_BACKTEST/D_EX_CORE/D_DATA, 待施工 |
| v3.0.0 (Panel技术栈切换) | 同 v2.1.0 + 5个交易/回测组件迁移 + ChartFactory | DefaultNotificationManager, DefaultApprovalGateway | #ARCH-047: Streamlit→Panel+HoloViz+Plotly+plotly_resampler; 5组件(backtest_results/tick_replay/order_book/position_monitor/trade_panel)迁移; 新增ChartFactory(8工厂方法) |
| v3.1.0 (仪表盘可运行化) | 同 v3.0.0 + 5旧页面迁移 + app_panel主入口 | DefaultNotificationManager, DefaultApprovalGateway | #ARCH-047: 5旧Streamlit页面(fitness_functions/gate_statistics/knowledge_overview/olap_trend/task_progress)迁移至Panel; 新建app_panel.py主入口(pn.Tabs 10 Tab); ChartFactory新增make_gate_chart/make_trend_line |

---

## §1 设计背景与目标

### 1.1 背景

C轨人机交互层是系统与用户之间的桥梁。当前B轨治理基础设施已稳定运行，但C轨业务层尚未开放施工（ARB-11裁定：T0先行层需等待B轨容量升级完成）。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 监控面板标准化 | DashboardBase OCP 扩展点可用 |
| 2 | ✅ 包含 | 通知分发标准化 | NotificationManagerBase OCP 扩展点可用 |
| 3 | ✅ 包含 | 人工审批标准化 | ApprovalGatewayBase OCP 扩展点可用 |
| 4 | ✅ 包含 | Streamlit Dashboard | 5 页面可渲染 |
| 5 | ✅ 包含 | Fitness Functions 展示 | EXT-DASHBOARD-FLE-001 消费 FLE Facade |
| 6 | ✅ 包含 | **v2.2.0新增** 回测结果可视化 | backtest_results组件消费D_BACKTEST BacktestResult(CTR-P1-016), 净值曲线/回撤/Sharpe/IC/IR |
| 7 | ✅ 包含 | **v2.2.0新增** Tick回放可视化 | tick_replay组件消费D_BACKTEST tick_replay引擎, 逐Tick回放+5档盘口快照 |
| 8 | ✅ 包含 | **v2.2.0新增** 5档盘口实时展示 | order_book组件消费D_DATA MiniQmtProvider.get_order_book() |
| 9 | ✅ 包含 | **v2.2.0新增** 实盘持仓监控 | position_monitor组件消费D_EX_CORE MiniQmtBroker.get_positions() |
| 10 | ✅ 包含 | **v2.2.0新增** 实盘交易面板 | trade_panel组件调用D_EX_CORE ExecutionEngine.execute_order(broker_id="miniqmt") |
| 11 | ❌ 排除 | 风险计算 | D_RISK |
| 12 | ❌ 排除 | 归因分析 | D_REPORTING |
| 13 | ❌ 排除 | 数据采集 | D_DATA |
| 14 | ❌ 排除 | 回测执行 | D_BACKTEST 职责, backtest_results仅展示结果 |
| 15 | ❌ 排除 | 实盘撮合 | D_EX_CORE MiniQmtBroker 职责, trade_panel仅触发下单 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| Streamlit 为可选依赖 | import 失败时降级为 CLI 输出 |
| Dashboard 组件独立可渲染 | 每个组件 fetch+render 分离 |
| OLAPEngine 可能不可用 | 门禁统计/OLAP 趋势组件返回空 dataclass |
| C轨已解除 | 业务代码可施工 |
| **v2.2.0新增**: 5个新组件依赖D_BACKTEST/D_EX_CORE/D_DATA未施工 | 数据源未就绪时组件返回空dataclass, 待上游施工后填充 |
| **v2.2.0新增**: 实盘交易面板需风控确认 | trade_panel下单前MUST显示风控提示, human_gated(实盘交易需Owner审批) |
| **v2.2.0新增**: Tick回放大数据量 | 单标的1年Tick数据可能>1GB, tick_replay组件MUST支持分页加载+虚拟滚动 |
| **v2.2.0新增**: 5档盘口实时刷新 | order_book组件MUST支持100ms级刷新, 避免Streamlit重渲染卡顿(rerun策略) |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策+施工审批 | 设计+施工 | C轨开放审批权 |
| D_RISK | 风险仪表盘数据消费 | 集成 | CTR-P1-008 |
| D_REPORTING | 归因报告数据消费 | 集成 | CTR-P1-009 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 通知渠道 | 0 实现 | 3 渠道 | 无 DefaultNotificationManager | P1 |
| 审批流程 | 0 实现 | 5 流程 | 无 DefaultApprovalGateway | P1 |
| C轨集成 | active | active | B轨容量升级未完成（C轨占位已解除[ARCH-045 P0]） | P0 |
| **v2.2.0**: 回测可视化 | 0 | backtest_results组件 | 缺组件, **规格已就绪(§16.7.1), 待施工** | P1 |
| **v2.2.0**: Tick回放可视化 | 0 | tick_replay组件 | 缺组件, **规格已就绪(§16.7.2), 待施工** | P1 |
| **v2.2.0**: 5档盘口 | 0 | order_book组件 | 缺组件, **规格已就绪(§16.7.3), 待施工** | P1 |
| **v2.2.0**: 实盘持仓监控 | 0 | position_monitor组件 | 缺组件, **规格已就绪(§16.7.4), 待施工** | P1 |
| **v2.2.0**: 实盘交易面板 | 0 | trade_panel组件 | 缺组件, **规格已就绪(§16.7.5), 待施工** | P1 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| Dashboard 查看任务进度 | 用户打开 Dashboard | DashboardApp.get_task_progress() → fetch_task_progress(task_repo) → render | TaskProgressData |
| 风控硬限审批 | D_PORTFOLIO_CORE/D_EXECUTION_CORE 触达风控硬限 | ApprovalGatewayBase.submit(request) → 人工查看 → decide(approve/reject) | 审批结果写回 |
| 告警通知 | 系统异常/SLI越界 | NotificationManagerBase.send(notification, channels) → 多渠道分发 | 通知送达确认 |
| **v2.2.0**: 查看回测结果 | 用户选择回测任务 | backtest_results.fetch(backtest_result) → render(净值曲线+回撤+Sharpe+3阶段门控) | BacktestResultVisualization |
| **v2.2.0**: Tick回放分析 | 用户选择历史时段+标的 | tick_replay.fetch(tick_data) → render(逐Tick回放+5档盘口快照+做T标记) | TickReplayVisualization |
| **v2.2.0**: 查看5档盘口 | 用户输入标的代码 | order_book.fetch(miniqmt_provider.get_order_book) → render(askPrice/bidPrice/askVol/bidVol) | OrderBookVisualization |
| **v2.2.0**: 查看实盘持仓 | 用户打开持仓页 | position_monitor.fetch(miniqmt_broker.get_positions) → render(持仓+盈亏+T+1提示) | PositionSnapshot |
| **v2.2.0**: 实盘下单 | 用户填写下单表单+确认 | trade_panel.submit(order) → ExecutionEngine.execute_order(broker_id="miniqmt") → render(订单状态) | Order + Fill |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 监控面板 | DashboardBase + DashboardApp (Streamlit) | 本模块 |
| 2 | ✅ 包含 | 通知分发 | NotificationManagerBase | 本模块 |
| 3 | ✅ 包含 | 人工审批 | ApprovalGatewayBase | 本模块 |
| 4 | ✅ 包含 | 任务进度看板 | TaskProgressData + fetch_task_progress | 本模块 |
| 5 | ✅ 包含 | 知识库概览 | KnowledgeOverviewData + fetch_knowledge_overview | 本模块 |
| 6 | ✅ 包含 | 门禁统计 | GateStatisticsData + fetch_gate_statistics | 本模块 |
| 7 | ✅ 包含 | Fitness Functions 仪表盘 | FitnessDashboardData + fetch_fitness_data | 本模块 |
| 8 | ✅ 包含 | OLAP 趋势 | OLAPTrendData + fetch_olap_trends | 本模块 |
| 9 | ❌ 排除 | 风险计算 | D_RISK | D_RISK |
| 10 | ❌ 排除 | 绩效归因 | D_REPORTING | D_REPORTING |
| 11 | ❌ 排除 | Fitness Functions 计算 | feedback_loop/fitness_functions.py | MOD-FEEDBACK_LOOP |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | DashboardBase | 面板 OCP 扩展点（render/refresh） | — | 同步调用 |
| 2 | NotificationManagerBase | 通知 OCP 扩展点（send/channels） | — | 同步调用 |
| 3 | ApprovalGatewayBase | 审批 OCP 扩展点（submit/decide/pending） | — | 同步调用 |
| 4 | DashboardPanelApp | Panel 主应用入口 (v3.1.0新建, #ARCH-047; 旧 DashboardApp 在 app.py 已弃用) | 10组件+ChartFactory | 组合 |
| 5 | Dashboard 组件(5 个, v2.1.0) | 独立可渲染面板 | DashboardApp | 组合 |
| 6 | Notification | 通知消息 dataclass | — | 数据传递 |
| 7 | ApprovalRequest | 审批请求 dataclass | — | 数据传递 |
| 8 | **backtest_results** (v3.0.0) | 回测结果可视化组件 | D_BACKTEST BacktestResult | fetch+render |
| 9 | **tick_replay** (v3.0.0) | Tick回放可视化组件 | D_BACKTEST tick_replay引擎 | fetch+render |
| 10 | **order_book** (v3.0.0) | 5档盘口实时展示组件 | D_DATA MiniQmtProvider | fetch+render |
| 11 | **position_monitor** (v3.0.0) | 实盘持仓监控组件 | D_EX_CORE MiniQmtBroker | fetch+render |
| 12 | **trade_panel** (v3.0.0) | 实盘交易面板组件 | D_EX_CORE ExecutionEngine | submit+render |
| 13 | **ChartFactory** (v3.0.0, v3.1.0扩展) | 图表统一工厂(make_equity/make_drawdown/make_kline/make_tick/make_heatmap/make_orderbook/make_position/make_orderflow + v3.1.0新增 make_gate_chart/make_trend_line) | HoloViews/Plotly/plotly_resampler | 工厂模式 |
| 14 | **app_panel** (v3.1.0) | Panel主应用入口(pn.Tabs组装10 Tab, pn.serve+.servable) | 10组件+ChartFactory | 组合 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | FLE Fitness Functions | fetch → render | 用户 | FitnessDashboardData |
| 2 | TaskRepository | fetch → render | 用户 | TaskProgressData |
| 3 | KbRepo | fetch → render | 用户 | KnowledgeOverviewData |
| 4 | OLAPEngine | fetch → render | 用户 | GateStatisticsData / OLAPTrendData |
| 5 | D_RISK | CTR-P1-008 消费 | Dashboard | RiskDashboardSnapshot |
| 6 | D_REPORTING | CTR-P1-009 消费 | Dashboard | PerformanceAttributionReport |
| 7 | **D_BACKTEST BacktestResult** (v2.2.0) | fetch → render | 用户 | BacktestResultVisualization(净值/回撤/Sharpe/IC/IR/3阶段门控) |
| 8 | **D_BACKTEST tick_replay** (v2.2.0) | fetch → render | 用户 | TickReplayVisualization(逐Tick+5档盘口快照+做T标记) |
| 9 | **D_DATA MiniQmtProvider** (v2.2.0) | fetch → render | 用户 | OrderBookVisualization(askPrice/bidPrice/askVol/bidVol 5档) |
| 10 | **D_EX_CORE MiniQmtBroker** (v2.2.0) | fetch → render | 用户 | PositionSnapshot(持仓/盈亏/T+1提示) |
| 11 | **D_EX_CORE ExecutionEngine** (v2.2.0) | submit → render | 用户 | Order+Fill(下单+订单状态实时更新) |

### 3.3 状态生命周期

本模块无状态机。

---

## §4 接口契约

> ⚠️ 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。
> 本模块 interface_base.py 中 Notification/ApprovalRequest 使用 `@dataclass(frozen=True)` 是历史遗留，新模型 MUST 使用 Pydantic BaseModel。

### 4.1 公共 API

```python
from zephyr.frontend.interface_base import (
    DashboardBase, NotificationManagerBase, ApprovalGatewayBase,
    Notification, ApprovalRequest, NotificationLevel, ApprovalAction,
)

class DashboardBase:
    """面板 OCP 扩展点——新面板类型继承此类"""
    def render(self, data: dict[str, Any]) -> None: ...
    def refresh(self, interval_s: float = 5.0) -> dict[str, Any]: ...

class NotificationManagerBase:
    """通知 OCP 扩展点——新通知渠道继承此类"""
    def send(self, notification: Notification, channels: list[str] | None = None) -> bool: ...
    def channels(self) -> list[str]: ...

class ApprovalGatewayBase:
    """审批 OCP 扩展点——新审批流程继承此类"""
    def submit(self, request: ApprovalRequest) -> str: ...
    def decide(self, request_id: str, action: ApprovalAction, comment: str = "") -> bool: ...
    def pending(self) -> list[ApprovalRequest]: ...
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum

class NotificationLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ApprovalAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    DELEGATE = "delegate"
    ESCALATE = "escalate"

class TaskProgressData(BaseModel):
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float = Field(..., description="进度百分比")

class FitnessDashboardData(BaseModel):
    metric_name: str = Field(..., description="度量名称")
    value: float = Field(..., description="度量值")
    trend: str = Field(default="stable", description="趋势")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `send()` | `notification` | ✅ | Notification 实例 |
| `send()` | `channels` | ❌ | list[str] 或 None |
| `submit()` | `request` | ✅ | ApprovalRequest 实例 |
| `decide()` | `request_id` | ✅ | 非空字符串 |
| `decide()` | `action` | ✅ | ApprovalAction 枚举 |
| `decide()` | `comment` | ❌ | 字符串 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `send()` | `bool (True)` | `NotificationError` |
| `channels()` | `list[str]` | — |
| `submit()` | `request_id: str` | `ApprovalError` |
| `decide()` | `bool` | `ApprovalNotFoundError` |
| `pending()` | `list[ApprovalRequest]` | — |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 Base 子类 | ✅ 向后兼容 | OCP 扩展 |
| Dashboard 组件新增 | ✅ 向后兼容 | 不影响已有组件 |
| 删除/重命名 Base 方法 | ❌ 破坏性 | 需 Owner 审批+迁移方案 |

**变更通知**：破坏性变更→Owner 审批+蓝图 minor+1。兼容性变更→AI 自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | DashboardBase 为 OCP 扩展点 | 新面板类型只加不改 |
| 2 | NotificationManagerBase 为 OCP 扩展点 | 新通知渠道只加不改 |
| 3 | ApprovalGatewayBase 为 OCP 扩展点 | 新审批流程只加不改 |
| 4 | Dashboard 组件独立可渲染 | fetch+render 分离 |
| 5 | Streamlit 为可选依赖 | import 失败时降级为 CLI |
| 6 | C轨已解除 | 可施工 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| Dashboard 页面数 | 5 | 10 | 无上限 | ✅ | 组件化扩展 |
| 通知渠道数 | 0 (待实现) | 3 | 无上限 | ✅ | OCP 扩展 |
| 审批流程数 | 0 (待实现) | 5 | 无上限 | ✅ | OCP 扩展 |

### 5.3 迁移

本蓝图不涉及迁移。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | Dashboard 可渲染率 | 99% | 页面加载测试 | 渲染成功率 | 99% | 每月允许1次不可用 | 连续2次不可用 |
| 可维护性 | 新组件接入时间 | <30min | 开发记录 | — | — | — | — |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 直接 import streamlit 在 interface_base.py | dashboard/app.py 内部 import | Streamlit 为可选依赖 |
| 2 | 导入源 | from zephyr.l04_* 直接调用 | 通过 CTR-P1-008 契约消费 | 分层约束 |
| 3 | 编码模式 | 在 Base 类中写业务逻辑 | Base 类只定义抽象接口 | OCP 扩展点约束 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Streamlit 未安装 | ImportError | 降级为 CLI 输出 | Dashboard 不可用 |
| 2 | OLAPEngine 不可用 | 连接异常 | 组件返回空 dataclass | 门禁统计/OLAP 趋势为空 |
| 3 | KbRepo 不可用 | 连接异常 | 组件返回空 dataclass | 知识库概览为空 |
| 4 | FLE Facade 不可用 | 连接异常 | Fitness 组件显示错误状态 | Fitness 仪表盘不可用 |
| 5 | 未知页面名 | render_page default | 返回 {"error": "Unknown page: ..."} | 单页面不可用 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| dashboard_render_success_rate | Gauge | 自动埋点 | <95% | P2 |
| notification_send_latency_ms | Histogram | 手动上报 | >5000ms | P2 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| Streamlit | CLI 输出 | Dashboard 渲染 | 降级为 CLI | Streamlit 安装 |
| OLAPEngine | 其他4页面 | 门禁统计/OLAP趋势 | 返回空 dataclass | OLAPEngine 恢复 |
| KbRepo | 其他4页面 | 知识库概览 | 返回空 dataclass | KbRepo 恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 审批绕过 | 高 | ApprovalGatewayBase 强制审批流 | 单元测试验证审批不可跳过 |
| 2 | 通知信息泄露 | 中 | 敏感信息脱敏后发送 | 扫描脚本检测 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | DashboardBase/组件 | fetch 返回正确 dataclass | 覆盖率>80% |
| 2 | 单元测试 | NotificationManagerBase | send 返回 bool | 覆盖率>80% |
| 3 | 单元测试 | ApprovalGatewayBase | submit/decide/pending 返回正确类型 | 覆盖率>80% |
| 4 | 集成测试 | DashboardApp + 数据源 | 5 页面端到端渲染 | 端到端通过 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| feedback_loop/fitness_functions | 必须 | FitnessFunctionFramework + FitnessInputs | — | `D:\ZephyrAlpha\src\zephyr\feedback_loop\fitness_functions.py` |
| db/task_repo | 必须 | TaskRepository | — | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` |
| db/kb_repo | 可选 | KbRepo | — | `D:\ZephyrAlpha\src\zephyr\db\kb_repo.py` |
| db/olap_engine | 可选 | OLAPEngine | — | `D:\ZephyrAlpha\src\zephyr\db\olap_engine.py` |
| MOD-L04-001 Risk Management | 可选 | CTR-P1-008 RiskDashboardSnapshot | — | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\risk-core\blueprint.md` |
| MOD-L07-001 Post-Trade Analytics | 可选 | CTR-P1-009 PerformanceAttributionReport | — | `D:\ZephyrAlpha\docs\03_modules\_domain_reporting\blueprint.md` |
| MOD-INF-035 系统大脑 | 可选 | 运维可视化 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-INF-015 系统遥测 | 可选 | 告警通道 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\system_telemetry\blueprint.md` |
| MOD-GATE_ENGINE 门禁引擎 | 可选 | 人机协同 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| **MOD-BT-001** (v2.2.0) | 必须 | BacktestResult(CTR-P1-016) + tick_replay引擎 | v1.1.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_backtest\blueprint.md` |
| **MOD-L06-001** (v2.2.0) | 必须 | ExecutionEngine.execute_order + MiniQmtBroker.get_positions | v2.2.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_execution_core\blueprint.md` |
| **MOD-L00-001** (v2.2.0) | 必须 | MiniQmtProvider.get_order_book(5档盘口) | v4.0.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_data\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐状态 | 说明 |
|---|--------|:---:|------|
| 1 | §10.1 依赖声明 ↔ dependency_path_panorama.md §3.7 | 已对齐 | D_FRONTEND 3子模块+Manifest额外资产+消费契约一致 |
| 2 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 未对齐 | C轨DEP待注册(ARB-15) |
| 3 | §10.1 依赖声明 ↔ 各依赖蓝图 §4 契约 | 未对齐 | CTR-P1-008/009待验证 |

### 10.3 内部依赖图

**执行顺序依赖**：无内部依赖

**数据流依赖**

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| interface_base.py | dashboard/app.py | DashboardBase/NotificationManagerBase/ApprovalGatewayBase | 函数调用 |
| dashboard/components/*.py | dashboard/app.py | 各组件 Data + render 函数 | 函数调用 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 模块简单 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | C轨DEP注册盲区 | CI门禁 | validate_path_alignment.py | C轨未注册 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 不适用 | — | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | C轨开放后需验证 | pytest+ruff | pytest | C轨已解除 | CI pipeline | 代码提交时 |

---

## §11 产出物

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_frontend\hmi_core\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\frontend\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\frontend\` | 测试用例 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| FLE Fitness Functions | EXT-DASHBOARD-FLE-001 消费 | Dashboard 可展示 Fitness 度量 | Dashboard 可渲染 |
| TaskRepository | 直接查询 | 任务进度看板可渲染 | 看板可渲染 |
| KbRepo | 直接查询 | 知识库概览可渲染 | 概览可渲染 |
| OLAPEngine | 直接查询 | 门禁统计+OLAP 趋势可渲染 | 统计可渲染 |
| D_RISK | CTR-P1-008 消费 | 风险仪表盘可展示 | 风险面板可渲染 |
| MOD-INF-035 系统大脑 | 运维可视化 | Dashboard 嵌入系统大脑 | Dashboard 可渲染 |
| MOD-INF-015 系统遥测 | 告警通道 | 通知推送 | 通知可达 |
| MOD-GATE_ENGINE 门禁引擎 | 人机协同 | CLI 命令交互 | CLI 可执行 |
| **D_BACKTEST** (v2.2.0) | 数据消费 | backtest_results+tick_replay组件展示回测结果与Tick回放 | 组件可渲染(待上游施工) |
| **D_EX_CORE** (v2.2.0) | 接口调用 | trade_panel+position_monitor组件调用ExecutionEngine+MiniQmtBroker | 组件可渲染+下单链路通(待上游施工) |
| **D_DATA** (v2.2.0) | 数据消费 | order_book组件展示5档盘口 | 组件可渲染(待上游施工) |

### 12.1 域契约锚点

本模块无域治理集成契约。

---

## §13 需要更新

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress 更新为 partially_implemented | C轨已解除 |
| 2 | 架构层 YAML | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\layers\l08_human_ai_interface.yaml` | module id 统一为 hmi_core (ARB-21) | 命名统一 |

---

## §14 风险

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | Streamlit 未安装 | 中 | Dashboard 无法渲染 | import 降级为 CLI 输出 | 风险 |
| 2 | YAML module id 不一致 | 低 | 发现困难 | ARB-21 统一为 hmi_core | 风险 |
| 3 | OLAPEngine 不可用 | 中 | 门禁统计/OLAP 趋势为空 | 组件返回空 dataclass | 风险 |
| 4 | KbRepo 不可用 | 中 | 知识库概览为空 | 组件返回空 dataclass | 风险 |
| 5 | C轨已开放[ARCH-045 P0]，蓝图与代码可同步 | 低 | 历史遗留蓝图标注与代码不同步 | 蓝图明确标注已实现代码范围 | 风险 |
| 6 | 新渠道需实现对应 Base 类 | — | 中 | OCP 扩展点文档 + 示例 | 负面后果 |
| 7 | 依赖 Streamlit 运行时 | — | 中 | 可选依赖 + CLI 降级 | 负面后果 |

---

## §16 施工指引

> ✅ **C轨业务层可施工**——开工条件已满足[ARCH-045 P0]。

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§10 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 4 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 5 | C轨已开放施工（construction_progress ≠ not_started） | 检查 frontmatter | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 扩展 |
| 核心风险 | Dashboard 数据源稳定性 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2（模板 v4.1 重构） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | DashboardBase 定义 | hard | 已实现 | ✅ |
| 2 | NotificationManagerBase 定义 | hard | 已实现 | ✅ |
| 3 | ApprovalGatewayBase 定义 | hard | 已实现 | ✅ |
| 4 | TaskRepository | hard | 已实现 | ✅ |
| 5 | FitnessFunctionFramework | hard | 已实现 | ✅ |
| 6 | C轨开放施工 | hard | ✅ active | ✅ |

### 16.3 实施步骤

#### 步骤 1：实现 DefaultNotificationManager

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 NotificationManagerBase |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\default_notification_manager.py` |
| 验收标准 | import 成功，send 返回 bool，channels 返回 list[str] |
| 验证命令 | `python -c "from zephyr.frontend.implementations.default_notification_manager import DefaultNotificationManager"` |
| G7 检查项 | 上游 interface_base.py 存在，下游可调用 |
| AI 自治范围 | human_gated |
| 检查点 | 文件存在且非空 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-L08-001 | default_notification_manager.py | code | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\default_notification_manager.py` |

#### 步骤 2：实现 DefaultApprovalGateway

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 ApprovalGatewayBase |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\default_approval_gateway.py` |
| 验收标准 | import 成功，submit 返回 request_id，decide 返回 bool，pending 返回 list |
| 验证命令 | `python -c "from zephyr.frontend.implementations.default_approval_gateway import DefaultApprovalGateway"` |
| G7 检查项 | 上游 interface_base.py 存在，下游可调用 |
| AI 自治范围 | human_gated |
| 检查点 | 文件存在且非空 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-L08-001 | default_approval_gateway.py | code | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\default_approval_gateway.py` |

#### 步骤 3：接入 CTR-P1-008/P1-009

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 DashboardBase |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\dashboard\app.py` |
| 验收标准 | 新增风险/归因 Dashboard 页面，D_RISK/D_REPORTING 数据可展示 |
| 验证命令 | `python -m pytest tests/frontend/ -k dashboard` |
| G7 检查项 | 下游 D_RISK/D_REPORTING 数据可消费 |
| AI 自治范围 | ai_modifiable |
| 检查点 | Dashboard 6 页面可渲染 |

#### 步骤 4：实现 backtest_results 回测结果可视化组件（v2.2.0新增）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §16.7.1 backtest_results规格 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\dashboard\components\backtest_results.py` |
| 验收标准 | (a) fetch(backtest_result) 返回 BacktestResultData; (b) render 展示净值曲线/回撤/Sharpe/Sortino/MaxDD/IC/IR; (c) 3阶段门控(IS→WFA→OOS)状态展示; (d) 不直接import D_BACKTEST, 通过依赖注入 |
| 验证命令 | `python -m pytest tests/frontend/test_backtest_results.py -v` |
| G7 检查项 | (1) fetch+render分离? (2) 不直接import业务层? (3) BacktestResult字段全填充(CTR-P1-016)? |
| AI 自治范围 | ai_modifiable |
| 检查点 | backtest_results.py 存在且非空 + Mock BacktestResult测试通过 |

**状态**：待施工（v2.2.0规划，规格已就绪于§16.7.1）

#### 步骤 5：实现 tick_replay Tick回放可视化组件（v2.2.0新增）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §16.7.2 tick_replay规格 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\dashboard\components\tick_replay.py` |
| 验收标准 | (a) fetch(tick_data) 返回 TickReplayData; (b) render 支持real_time/fast_forward/max_speed三种回放速度; (c) 5档盘口快照展示; (d) 做T场景(30秒/5秒冲高回落)标记; (e) 分页加载+虚拟滚动(避免大数据卡顿) |
| 验证命令 | `python -m pytest tests/frontend/test_tick_replay.py -v` |
| G7 检查项 | (1) 大数据量分页? (2) 5档盘口正确展示? (3) 回放速度可控? (4) 做T标记准确? |
| AI 自治范围 | ai_modifiable |
| 检查点 | tick_replay.py 存在且非空 + Mock Tick数据测试通过 |

**状态**：待施工（v2.2.0规划，规格已就绪于§16.7.2）

#### 步骤 6：实现 order_book 5档盘口展示组件（v2.2.0新增）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §16.7.3 order_book规格 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\dashboard\components\order_book.py` |
| 验收标准 | (a) fetch(miniqmt_provider) 返回 OrderBookData; (b) render 展示askPrice[5档]/bidPrice[5档]/askVol[5档]/bidVol[5档]; (c) 100ms级刷新(rerun策略优化); (d) 盘口压力可视化(买卖力量对比) |
| 验证命令 | `python -m pytest tests/frontend/test_order_book.py -v` |
| G7 检查项 | (1) 刷新无卡顿? (2) 5档数据完整? (3) 盘口压力可视化正确? |
| AI 自治范围 | ai_modifiable |
| 检查点 | order_book.py 存在且非空 + Mock 5档数据测试通过 |

**状态**：待施工（v2.2.0规划，规格已就绪于§16.7.3）

#### 步骤 7：实现 position_monitor 实盘持仓监控组件（v2.2.0新增）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §16.7.4 position_monitor规格 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\dashboard\components\position_monitor.py` |
| 验收标准 | (a) fetch(miniqmt_broker) 返回 PositionMonitorData; (b) render 展示持仓(可用/冻结/当日买入)+未实现盈亏+T+1锁定提示+账户资金; (c) T+1当日买入股票标记不可卖 |
| 验证命令 | `python -m pytest tests/frontend/test_position_monitor.py -v` |
| G7 检查项 | (1) T+1标记正确? (2) 盈亏计算正确? (3) 持仓数据完整? |
| AI 自治范围 | ai_modifiable |
| 检查点 | position_monitor.py 存在且非空 + Mock PositionSnapshot测试通过 |

**状态**：待施工（v2.2.0规划，规格已就绪于§16.7.4）

#### 步骤 8：实现 trade_panel 实盘交易面板组件（v2.2.0新增）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §16.7.5 trade_panel规格 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\dashboard\components\trade_panel.py` |
| 验收标准 | (a) 下单表单(代码/方向/数量/价格/算法TWAP/VWAP/MARKET); (b) 提交前显示风控提示+二次确认; (c) 订单列表实时更新状态机(PENDING→SUBMITTED→ACCEPTED→FILLED); (d) 撤单按钮(cancel_order); (e) 调用ExecutionEngine.execute_order(broker_id="miniqmt") |
| 验证命令 | `python -m pytest tests/frontend/test_trade_panel.py -v` |
| G7 检查项 | (1) 风控提示强制显示? (2) 二次确认? (3) 订单状态实时更新? (4) 撤单链路通? (5) human_gated(实盘交易需Owner审批)? |
| AI 自治范围 | human_gated——实盘交易面板接入需Owner审批 |
| 检查点 | trade_panel.py 存在且非空 + Mock ExecutionEngine测试通过 + 小资金实盘验证(100股) |

**状态**：待施工（v2.2.0规划，规格已就绪于§16.7.5）

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | DefaultNotificationManager 实现失败 | 还原 implementations/ |
| 2 | DefaultApprovalGateway 实现失败 | 还原 implementations/ |
| 3 | Dashboard 页面接入失败 | 还原 dashboard/app.py |
| 4 (v2.2.0) | backtest_results 组件实现失败 | 删除 backtest_results.py, 还原 app.py 路由 |
| 5 (v2.2.0) | tick_replay 组件实现失败(大数据卡顿) | 删除 tick_replay.py, 还原 app.py 路由 |
| 6 (v2.2.0) | order_book 组件实现失败(刷新卡顿) | 删除 order_book.py, 还原 app.py 路由 |
| 7 (v2.2.0) | position_monitor 组件实现失败 | 删除 position_monitor.py, 还原 app.py 路由 |
| 8 (v2.2.0) | trade_panel 组件实现失败(实盘风险) | 删除 trade_panel.py, 还原 app.py 路由, 立即停止实盘交易 |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | DefaultNotificationManager 存在 | `ls` exit 0 | 完成 | ☐ |
| 2 | DefaultApprovalGateway 存在 | `ls` exit 0 | 完成 | ☐ |
| 3 | DashboardApp 6 页面可渲染 | pytest 通过 | 完成 | ☐ |
| 4 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 5 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 6 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | partially_implemented | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | DashboardApp 页面路由 | 算法 | page_name → fetch_{page}() → render_{page}() | dashboard/app.py |
| 2 | **backtest_results规格** (v2.2.0) | 协议 | fetch(BacktestResult)→BacktestResultData; render: 净值曲线+回撤+Sharpe+Sortino+MaxDD+IC+IR+3阶段门控(IS→WFA→OOS) — 见§16.7.1 | backtest_results.py(待施工) |
| 3 | **tick_replay规格** (v2.2.0) | 协议 | fetch(TickData)→TickReplayData; render: 逐Tick回放(real_time/fast_forward/max_speed)+5档盘口快照+做T标记 — 见§16.7.2 | tick_replay.py(待施工) |
| 4 | **order_book规格** (v2.2.0) | 协议 | fetch(MiniQmtProvider.get_order_book)→OrderBookData; render: 5档askPrice/bidPrice/askVol/bidVol+盘口压力 — 见§16.7.3 | order_book.py(待施工) |
| 5 | **position_monitor规格** (v2.2.0) | 协议 | fetch(MiniQmtBroker.get_positions)→PositionMonitorData; render: 持仓+盈亏+T+1提示+账户资金 — 见§16.7.4 | position_monitor.py(待施工) |
| 6 | **trade_panel规格** (v2.2.0) | 协议 | submit(Order)→ExecutionEngine.execute_order(broker_id="miniqmt"); render: 下单表单+订单状态机+撤单+风控提示 — 见§16.7.5 | trade_panel.py(待施工) |

### §16.7.1 backtest_results 回测结果可视化组件规格（v2.2.0新增）

> **真源声明**：本规格是 backtest_results 组件的唯一真源。

#### A. 组件元数据

| 字段 | 值 | 说明 |
|------|-----|------|
| 组件名 | backtest_results | Panel 页面组件 (v3.0.0技术栈切换) |
| 数据源 | D_BACKTEST BacktestResult(CTR-P1-016) | 通过依赖注入传入, 禁止直接import D_BACKTEST |
| 页面路由 | /backtest-results | DashboardApp 路由 |
| 渲染依赖 | HoloViews(净值曲线)+plotly_resampler(回撤)+Lightweight Charts(K线, HTML Pane+原生JS) | 不依赖Python封装包, 直接用pn.pane.HTML+lightweight-charts.js |
| callback约束 | Panel callback仅编排, 业务逻辑独立为纯函数 | fetch→ChartFactory.make_xxx()→callback, G1升级时fetch可直接包装为FastAPI路由 |

#### B. BacktestResultData 数据模型

```python
class BacktestResultData(BaseModel):
    """回测结果可视化数据模型"""
    backtest_id: str = Field(..., description="回测任务ID")
    net_value_curve: list[float] = Field(..., description="净值曲线序列")
    drawdown_curve: list[float] = Field(..., description="回撤曲线序列(负数)")
    timestamps: list[str] = Field(..., description="时间戳序列")
    metrics: BacktestMetrics = Field(..., description="绩效指标")
    gate_status: GateStatus = Field(..., description="3阶段门控状态")

class BacktestMetrics(BaseModel):
    sharpe: float = Field(..., description="Sharpe比率(已修正)")
    sortino: float = Field(..., description="Sortino比率")
    max_drawdown: float = Field(..., description="最大回撤")
    ic: float = Field(..., description="信息系数")
    ir: float = Field(..., description="信息比率")
    win_rate: float = Field(..., description="胜率")
    annual_return: float = Field(..., description="年化收益率")

class GateStatus(BaseModel):
    is_passed: bool = Field(..., description="IS(样本内)阶段是否通过")
    wfa_passed: bool = Field(..., description="WFA(Walk-Forward)阶段是否通过")
    oos_passed: bool = Field(..., description="OOS(样本外)阶段是否通过")
```

#### C. fetch + render 接口

```python
def fetch_backtest_results(backtest_result: BacktestResult) -> BacktestResultData:
    """从D_BACKTEST BacktestResult提取可视化数据. 
    输入: BacktestResult(CTR-P1-016, 11个必填字段全填充)
    输出: BacktestResultData(净值/回撤/指标/门控状态)
    """
    ...

def render_backtest_results(data: BacktestResultData) -> None:
    """Panel+HoloViz渲染 (v3.0.0, #ARCH-047). 
    布局: 
      - 顶部: 关键指标卡片(Sharpe/Sortino/MaxDD/IC/IR/胜率/年化)
      - 中部: 净值曲线(HoloViews)+回撤曲线(plotly_resampler双轴图)
      - 底部: 3阶段门控状态(IS→WFA→OOS, 绿色=通过/红色=未通过)
    K线图: 用pn.pane.HTML+lightweight-charts.js原生渲染, 不依赖Python封装包.
    callback: Panel callback仅编排, 图表生成委托ChartFactory.make_equity/make_drawdown.
    """
    ...
```

### §16.7.2 tick_replay Tick回放可视化组件规格（v2.2.0新增）

> **真源声明**：本规格是 tick_replay 组件的唯一真源。

#### A. 组件元数据

| 字段 | 值 | 说明 |
|------|-----|------|
| 组件名 | tick_replay | Panel 页面组件 (v3.0.0技术栈切换) |
| 数据源 | D_BACKTEST tick_replay引擎 | TickReplayEngine.replay() 产出的Tick序列 |
| 页面路由 | /tick-replay | DashboardApp 路由 |
| 渲染依赖 | Plotly+plotly_resampler默认 / Datashader阈值触发(>50万点) | MVP全用Plotly, 真实数据量超阈值时自动切换Datashader |
| callback约束 | Panel callback仅编排, 业务逻辑独立为纯函数 | fetch→ChartFactory.make_tick()→callback |

#### B. TickReplayData 数据模型

```python
class TickReplayData(BaseModel):
    """Tick回放可视化数据模型"""
    symbol: str = Field(..., description="标的代码")
    ticks: list[TickSnapshot] = Field(..., description="Tick序列(分页加载)")
    replay_speed: ReplaySpeed = Field(..., description="回放速度")
    t_scenario_marks: list[TScenarioMark] = Field(default=[], description="做T场景标记")

class TickSnapshot(BaseModel):
    timestamp: str
    last_price: float
    ask_price: list[float] = Field(..., description="5档卖价")
    bid_price: list[float] = Field(..., description="5档买价")
    ask_vol: list[int] = Field(..., description="5档卖量")
    bid_vol: list[int] = Field(..., description="5档买量")
    volume: int
    amount: float

class ReplaySpeed(str, Enum):
    REAL_TIME = "real_time"       # 实时(1x)
    FAST_FORWARD = "fast_forward" # 快进(10x)
    MAX_SPEED = "max_speed"       # 最大(无延迟)

class TScenarioMark(BaseModel):
    """做T场景标记(30秒冲高回落/5秒级)"""
    timestamp: str
    scenario_type: str  # "30s_spike_drop" / "5s_spike"
    description: str
```

#### C. fetch + render 接口

```python
def fetch_tick_replay(tick_data: list, symbol: str, 
                     page: int = 1, page_size: int = 1000) -> TickReplayData:
    """从D_BACKTEST tick_replay引擎获取Tick数据. 
    分页加载: 单页1000 Tick, 避免大数据卡顿.
    做T场景识别: 自动标记30秒冲高回落/5秒级快照.
    """
    ...

def render_tick_replay(data: TickReplayData) -> None:
    """Panel+HoloViz渲染 (v3.0.0, #ARCH-047). 
    布局:
      - 顶部: 控制栏(回放速度选择/上一页/下一页/跳转时间)
      - 中部: Tick价格图+成交量(Plotly+plotly_resampler, 支持zoom; 数据量>50万点自动切换Datashader)
      - 中下: 5档盘口快照(Bokeh WebSocket实时推送, ask红/bid绿)
      - 底部: 做T场景标记(垂直线+标注)
    渲染策略: MVP全用Plotly+plotly_resampler(10万级降采样), Datashader仅阈值触发(>50万点百万级渲染).
    callback: Panel callback仅编排, 图表生成委托ChartFactory.make_tick().
    """
    ...
```

### §16.7.3 order_book 5档盘口展示组件规格（v2.2.0新增）

> **真源声明**：本规格是 order_book 组件的唯一真源。

#### A. 组件元数据

| 字段 | 值 | 说明 |
|------|-----|------|
| 组件名 | order_book | Panel 页面组件 (v3.0.0技术栈切换) |
| 数据源 | D_DATA MiniQmtProvider.get_order_book() | 5档盘口实时数据 |
| 页面路由 | /order-book | DashboardApp 路由 |
| 刷新策略 | 100ms Bokeh WebSocket推送 | 原生WebSocket, 无rerun开销 |
| callback约束 | Panel callback仅编排, 业务逻辑独立为纯函数 | fetch→ChartFactory.make_orderbook()→callback |

#### B. OrderBookData 数据模型

```python
class OrderBookData(BaseModel):
    """5档盘口数据模型"""
    symbol: str
    timestamp: str
    ask_price: list[float] = Field(..., description="5档卖价[ask1~ask5]")
    bid_price: list[float] = Field(..., description="5档买价[bid1~bid5]")
    ask_vol: list[int] = Field(..., description="5档卖量[askVol1~askVol5]")
    bid_vol: list[int] = Field(..., description="5档买量[bidVol1~bidVol5]")
    pressure_ratio: float = Field(..., description="盘口压力比=bid_vol_total/ask_vol_total")
```

#### C. fetch + render 接口

```python
def fetch_order_book(miniqmt_provider, symbol: str) -> OrderBookData:
    """从D_DATA MiniQmtProvider获取5档盘口. 
    输入: MiniQmtProvider实例(依赖注入), 标的代码
    输出: OrderBookData(5档ask/bid price/vol + 压力比)
    """
    ...

def render_order_book(data: OrderBookData) -> None:
    """Panel+HoloViz渲染 (v3.0.0, #ARCH-047). 
    布局:
      - 左侧: 5档卖盘(红色, 价格降序ask5→ask1)
      - 中间: 最新价+压力比仪表盘
      - 右侧: 5档买盘(绿色, 价格降序bid1→bid5)
    刷新: Bokeh WebSocket 100ms推送, 仅更新盘口数据, 无全页重渲染.
    callback: Panel callback仅编排, 图表生成委托ChartFactory.make_orderbook().
    """
    ...
```

### §16.7.4 position_monitor 实盘持仓监控组件规格（v2.2.0新增）

> **真源声明**：本规格是 position_monitor 组件的唯一真源。

#### A. 组件元数据

| 字段 | 值 | 说明 |
|------|-----|------|
| 组件名 | position_monitor | Panel 页面组件 (v3.0.0技术栈切换) |
| 数据源 | D_EX_CORE MiniQmtBroker.get_positions() | 实盘持仓快照 |
| 页面路由 | /position-monitor | DashboardApp 路由 |
| 刷新策略 | 1s Bokeh WebSocket推送 | 持仓1秒刷新一次 |
| callback约束 | Panel callback仅编排, 业务逻辑独立为纯函数 | fetch→ChartFactory.make_position()→callback |

#### B. PositionMonitorData 数据模型

```python
class PositionMonitorData(BaseModel):
    """实盘持仓监控数据模型"""
    account_id: str
    total_asset: float = Field(..., description="总资产")
    available_cash: float = Field(..., description="可用资金")
    positions: list[PositionItem] = Field(..., description="持仓列表")

class PositionItem(BaseModel):
    symbol: str
    name: str = Field(..., description="证券名称")
    quantity: int = Field(..., description="总持仓")
    available_quantity: int = Field(..., description="可用数量(扣除冻结)")
    frozen_quantity: int = Field(..., description="冻结数量")
    today_bought: int = Field(..., description="当日买入(T+1锁定)")
    cost_price: float = Field(..., description="成本价")
    last_price: float = Field(..., description="最新价")
    unrealized_pnl: float = Field(..., description="未实现盈亏")
    unrealized_pnl_pct: float = Field(..., description="未实现盈亏百分比")
    is_t_plus_1_locked: bool = Field(..., description="T+1锁定(当日买入不可卖)")
```

#### C. fetch + render 接口

```python
def fetch_position_monitor(miniqmt_broker) -> PositionMonitorData:
    """从D_EX_CORE MiniQmtBroker获取持仓. 
    输入: MiniQmtBroker实例(依赖注入)
    输出: PositionMonitorData(持仓+盈亏+T+1标记)
    T+1标记: today_bought > 0 → is_t_plus_1_locked=True
    """
    ...

def render_position_monitor(data: PositionMonitorData) -> None:
    """Panel+HoloViz渲染 (v3.0.0, #ARCH-047). 
    布局:
      - 顶部: 账户资金卡片(总资产/可用资金/当日盈亏)
      - 中部: 持仓表格(symbol/名称/持仓/可用/冻结/成本/最新价/盈亏/盈亏%/T+1标记)
      - T+1锁定行: 红色背景标记, 鼠标悬停提示"当日买入, 次日可卖"
    刷新: Bokeh WebSocket 1s推送, 持仓实时更新.
    callback: Panel callback仅编排, 图表生成委托ChartFactory.make_position().
    """
    ...
```

### §16.7.5 trade_panel 实盘交易面板组件规格（v2.2.0新增）

> **真源声明**：本规格是 trade_panel 组件的唯一真源。**human_gated**: 实盘交易面板接入需 Owner 审批。

#### A. 组件元数据

| 字段 | 值 | 说明 |
|------|-----|------|
| 组件名 | trade_panel | Panel 页面组件 (v3.0.0技术栈切换) |
| 数据源 | D_EX_CORE ExecutionEngine.execute_order() | 实盘下单接口 |
| 页面路由 | /trade-panel | DashboardApp 路由 |
| 风控 | human_gated + 二次确认 | 下单前MUST显示风控提示+二次确认弹窗(Panel modal) |
| callback约束 | Panel callback仅编排, 业务逻辑独立为纯函数 | submit→ChartFactory.make_orderflow()→callback |

#### B. TradePanelData 数据模型

```python
class TradePanelData(BaseModel):
    """实盘交易面板数据模型"""
    orders: list[OrderItem] = Field(..., description="订单列表(实时状态更新)")
    account_summary: AccountSummary = Field(..., description="账户摘要(资金/持仓)")

class OrderItem(BaseModel):
    order_id: str
    symbol: str
    side: str  # "buy" / "sell"
    quantity: int
    price: float
    order_type: str  # "market" / "limit" / "twap" / "vwap"
    status: str  # PENDING/SUBMITTED/ACCEPTED/PARTIALLY_FILLED/FILLED/CANCELLED/REJECTED/EXPIRED
    filled_quantity: int = Field(default=0, description="已成交数量")
    avg_fill_price: float = Field(default=0.0, description="平均成交价")
    timestamp: str
    error_message: str = Field(default="", description="错误信息(REJECTED时)")

class OrderSubmission(BaseModel):
    """下单表单数据"""
    symbol: str
    side: str  # "buy" / "sell"
    quantity: int = Field(..., ge=100, description="数量(≥100, A股1手起)")
    price: float = Field(..., gt=0, description="价格")
    order_type: str  # "market" / "limit" / "twap" / "vwap"
    broker_id: str = Field(default="miniqmt", description="券商ID(默认MiniQMT)")
```

#### C. submit + render 接口

```python
def submit_order(execution_engine, order_submission: OrderSubmission) -> str:
    """提交订单到D_EX_CORE ExecutionEngine. 
    输入: ExecutionEngine实例(依赖注入), OrderSubmission
    前置校验: 
      (1) 显示风控提示(预估金额/持仓影响)
      (2) 二次确认弹窗(Panel modal, pn.widgets.Button+pn.Modal)
      (3) 调用ExecutionEngine.execute_order(order, broker_id="miniqmt")
    输出: order_id
    """
    ...

def render_trade_panel(data: TradePanelData) -> None:
    """Panel+HoloViz渲染 (v3.0.0, #ARCH-047). 
    布局:
      - 顶部: 下单表单(代码/方向/数量/价格/算法TWAP/VWAP/MARKET, pn.widgets.Form)
      - 中部: 风控提示+二次确认按钮(预估金额/持仓影响/T+1提示, Panel modal)
      - 底部: 订单列表(实时状态更新, 支持撤单按钮, Lightweight Charts订单流HTML Pane)
    状态机: PENDING→SUBMITTED→ACCEPTED→FILLED 实时更新, 状态用颜色标记.
    撤单: 每个非终态订单行显示"撤单"按钮, 调用cancel_order.
    callback: Panel callback仅编排, 图表生成委托ChartFactory.make_orderflow().
    """
    ...
```

#### D. 安全约束

| 约束 | 说明 |
|------|------|
| human_gated | 实盘交易面板接入需Owner审批 |
| 二次确认 | 下单前MUST弹窗确认(避免误操作) |
| 风控提示 | 下单前MUST显示预估金额/持仓影响/T+1提示 |
| 小资金灰度 | 首次部署MUST用1万元做100股测试, 验证成交回报/持仓更新/T+1校验正确后再放量 |
| 紧急停止 | trade_panel顶部MUST有"紧急停止"按钮, 点击后立即停止所有新订单+撤单所有未完成订单 |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `streamlit run src/zephyr/frontend/dashboard/app.py` | 启动 Dashboard | — | Streamlit Web UI |
| 2 | 命令 | `python -m pytest tests/frontend/` | 运行测试 | `-k {pattern}` | pytest 输出 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 运行 | Streamlit 启动失败 | ImportError | `pip install streamlit` | Dashboard 可用 | 重新启动 |
| 2 | 运行 | 数据源不可用 | 连接异常 | 检查 SQLite/DuckDB 路径 | 组件返回空 dataclass | 数据源恢复 |
| 3 | 运行 | 紧急冻结 | 安全事件 | 冻结写入+只读 | — | 威胁解除 |

### 16.12 并发操作模型

本模块无并发操作。

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| Dashboard 页面数 | 5 | 组件计数 |
| 通知渠道数 | 0 | NotificationManagerBase 子类计数 |
| 审批流程数 | 0 | ApprovalGatewayBase 子类计数 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L08-001 | 无通知渠道实现 | 实现 DefaultNotificationManager | P1 | 通知需求>0 | v2.1.0 | 待施工 |
| GAP-L08-002 | 无审批流程实现 | 实现 DefaultApprovalGateway | P1 | 审批需求>0 | v2.1.0 | 待施工 |
| **GAP-L08-003** (v2.2.0) | 无回测可视化 | 实现 backtest_results组件 | P1 | 回测引擎v1.1.0+就绪 | v2.2.0 | 待施工(规格已就绪) |
| **GAP-L08-004** (v2.2.0) | 无Tick回放可视化 | 实现 tick_replay组件 | P1 | Tick回放引擎就绪 | v2.2.0 | 待施工(规格已就绪) |
| **GAP-L08-005** (v2.2.0) | 无5档盘口展示 | 实现 order_book组件 | P1 | MiniQmtProvider就绪 | v2.2.0 | 待施工(规格已就绪) |
| **GAP-L08-006** (v2.2.0) | 无实盘持仓监控 | 实现 position_monitor组件 | P1 | MiniQmtBroker就绪 | v2.2.0 | 待施工(规格已就绪) |
| **GAP-L08-007** (v2.2.0) | 无实盘交易面板 | 实现 trade_panel组件 | P1 | MiniQmtBroker就绪+Owner审批 | v2.2.0 | 待施工(规格已就绪) |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | DashboardBase+NotificationManagerBase+ApprovalGatewayBase+5 组件 | ⚠️ |
| v2.0.0 | 2 | 模板重构 | 章节重排+新增概述+frontmatter 补全 | ⚠️ |
| v2.1.0 | 2 | 回填+禁止施工 | 接口契约与代码对齐+模板回填+禁止施工标注 | ⚠️ |
| v2.2.0 | 2 | 交易/回测组件规划 | 新增5个交易/回测组件规格(§16.7.1~§16.7.5)+对接D_BACKTEST/D_EX_CORE/D_DATA | ⚠️(规格已就绪, 代码待施工) |
| v3.0.0 | 3 | 技术栈切换(#ARCH-047) | Streamlit→Panel+HoloViz+Plotly+plotly_resampler+Lightweight Charts(HTML Pane+原生JS); 新增ChartFactory(make_equity/drawdown/kline/tick/heatmap/orderbook/position/orderflow); callback仅编排约束; Datashader阈值触发(>50万点); 5组件迁移完成(backtest_results/tick_replay/order_book/position_monitor/trade_panel) | ✅(代码已施工, 2026-07-05) |
| v3.1.0 | 3 | 仪表盘可运行化(#ARCH-047) | 5个旧Streamlit页面(fitness_functions/gate_statistics/knowledge_overview/olap_trend/task_progress)迁移至Panel; 新建app_panel.py主应用入口(pn.Tabs组装10 Tab); ChartFactory新增make_gate_chart/make_trend_line; 仪表盘可运行(panel serve --show) | ✅(代码已施工, 2026-07-05) |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工 Phase | 状态 |
|--------|---------|---------|----------|:---:|
| DefaultNotificationManager | GAP-L08-001 | default_notification_manager.py | Phase 1 | 待施工 |
| DefaultApprovalGateway | GAP-L08-002 | default_approval_gateway.py | Phase 2 | 待施工 |
| **backtest_results** | GAP-L08-003 | backtest_results.py | Phase 1.5 | ✅v3.0.0已迁移(Panel+HoloViz) |
| **tick_replay** | GAP-L08-004 | tick_replay.py | Phase 1.5 | ✅v3.0.0已迁移(Panel+HoloViz) |
| **order_book** | GAP-L08-005 | order_book.py | Phase 1.5 | ✅v3.0.0已迁移(Panel+HoloViz) |
| **position_monitor** | GAP-L08-006 | position_monitor.py | Phase 1.5 | ✅v3.0.0已迁移(Panel+HoloViz) |
| **trade_panel** | GAP-L08-007 | trade_panel.py | Phase 1.5 | ✅v3.0.0已迁移(Panel+HoloViz) |
| **fitness_functions** (v3.1.0) | — | fitness_functions.py | Phase 2.5 | ✅v3.1.0已迁移(Panel) |
| **gate_statistics** (v3.1.0) | — | gate_statistics.py | Phase 2.5 | ✅v3.1.0已迁移(Panel+ChartFactory.make_gate_chart) |
| **knowledge_overview** (v3.1.0) | — | knowledge_overview.py | Phase 2.5 | ✅v3.1.0已迁移(Panel) |
| **olap_trend** (v3.1.0) | — | olap_trend.py | Phase 2.5 | ✅v3.1.0已迁移(Panel+ChartFactory.make_trend_line) |
| **task_progress** (v3.1.0) | — | task_progress.py | Phase 2.5 | ✅v3.1.0已迁移(Panel) |
| **app_panel** (v3.1.0) | — | app_panel.py | Phase 2.5 | ✅v3.1.0已迁移(Panel主入口, pn.Tabs 10 Tab) |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L08-01 | C轨占位策略 | A: 完整蓝图 / B: 占位蓝图 | B | ARB-11裁定C轨blocked（已解除，见ARCH-045 P0） | 2026-05-05 |
| 2 | D-L08-02 | Streamlit 可选依赖 | A: 必选 / B: 可选+CLI降级 | B | 1人运维约束(ARB-3) | 2026-05-05 |
| 3 | D-L08-03 | OCP 扩展点设计 | A: 具体实现 / B: 抽象基类+注册表 | B | 开闭原则+多渠道扩展 | 2026-05-05 |
| 4 | D-L08-04 | Notification/Approval 使用 dataclass | A: Pydantic BaseModel / B: dataclass(frozen=True) | B | 历史遗留；新模型MUST用Pydantic(KBG-0040) | 2026-05-05 |
| 5 | D-L08-05 | 模板v4.1升级 | A: 保持v3.3 / B: 按v4.1升级 | B | v4.1模板合规 | 2026-05-15 |
| 6 | D-L08-06 | v2.2.0仪表盘方案 | A:新建D_FRONTEND域 / B:扩展现有D_FRONTEND | B | 复用DashboardBase OCP扩展点, 不引入新Base类, 架构一致 | 2026-07-04 |
| 7 | D-L08-07 | v2.2.0交易/回测组件数 | A:3个(仅交易) / B:5个(交易+回测+盘口) | B | joinquant/Qbot风格仪表盘+实盘交易面板+Tick回放全场景覆盖 | 2026-07-04 |
| 8 | D-L08-08 | v2.2.0组件数据源接入 | A:直接import业务层 / B:依赖注入传入 | B | 分层约束+Streamlit可选依赖, 组件不直接import业务层模块 | 2026-07-04 |
| 9 | D-L08-09 | v2.2.0实盘交易面板风控 | A:无风控直接下单 / B:human_gated+二次确认+紧急停止 | B | 实盘交易安全, 避免误操作, Owner审批+小资金灰度 | 2026-07-04 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| OCP 扩展点 | 开闭原则扩展点——Base 抽象类，新类型继承扩展，不修改已有代码 | 插件 | 插件可独立加载；OCP扩展点需继承Base |
| C轨 | C-Track，业务价值线（L00-L13） | B轨 | B轨=基础设施治理线；C轨=业务交易线 |
| partially_implemented | 部分实现——代码骨架已就位，业务逻辑待填充 | design_only | design_only=仅设计未施工；blocked=有设计但被外部条件阻断 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | Notification/Approval 使用 dataclass 而非 Pydantic BaseModel | 中 | 历史遗留 | 新模型MUST用Pydantic；旧模型待迁移 | §4 | 待解决 |
| 2 | CTR-P1-008/009 契约未注册到 cross-module-dependency-registry.yaml | 中 | C轨DEP注册盲区(ARB-15) | C轨开放时补注册 | §10.2 | 待解决 |
| 3 | §0.1 已实现文件缺少 implementations/ 目录 | 低 | Default 实现未施工 | C轨开放后施工 | §16.3 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ✅ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | C轨开放+Default实现完成 | OCP扩展点设计稳定 |
| 接口契约 | stable | 高 | Default实现验证通过 | Base类接口与代码对齐 |
| 数据模型 | evolving | 中 | 迁移dataclass→Pydantic | 历史遗留dataclass |
| 施工步骤 | evolving | 中 | C轨开放 | active状态（C轨占位已解除[ARCH-045 P0]） |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 蓝图 | — | 已完成 |
| v1.0.0 | Base类+5组件实现 | v0.1.0 | 已完成 |
| v2.0.0 | 模板重构+压缩 | v1.0.0 | 已完成 |
| v2.1.0 | 回填+禁止施工标注+接口对齐 | v2.0.0 | 已完成 |
| v2.2.0 | 5个交易/回测组件规格(backtest_results/tick_replay/order_book/position_monitor/trade_panel) | v2.1.0 | 待施工(规格已就绪, 对接D_BACKTEST/D_EX_CORE/D_DATA) |
| v2.3.0 | DefaultNotificationManager+DefaultApprovalGateway | v2.2.0 | 待施工(C轨开放后) |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 路径错误 |
| 2 | 必备链接不可省略 | 关键信息缺失 |
| 3 | 蓝图必须是最终设计结果 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含 | 上下文缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败 |
| 13 | 已实现代码不在蓝图中重复 | 蓝图与代码漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定 | 职责混淆 |
| 16 | 术语表不可省略 | 术语理解漂移 |
| 17 | 参考实现规格 vs 已实现代码重复 | 逻辑实现错误/双源漂移 |
| 18 | 对标验证表格 vs 对标散文 | 丢表格/留散文 |
| 19 | SLO 必须定义 | 容错策略凭空猜测 |
| 20 | 可观测性不可省略 | 上线后黑盒 |
| 21 | 退化矩阵必须声明 | 部分失败时行为不可预测 |

---

## 蓝图拆分判定标准

### 判定流程

| 步骤 | 判定问题 | 判定结果 | 行动 |
|------|---------|---------|------|
| 1 | 拟新增/修改的内容与当前蓝图的职责是否相同？ | 相同 → 继续；不同 → 步骤 2 | 职责相同→原地升级 |
| 2 | 不同职责的内容是否有独立的上游/下游依赖链？ | 有 → 步骤 3；无 → 原地升级 | 无独立依赖→原地升级 |
| 3 | 拆分后两个蓝图是否各自自包含？ | 是 → 拆分；否 → 原地升级 | 自包含→拆分独立蓝图 |

### 判定示例

| 场景 | 职责相同？ | 独立依赖链？ | 各自自包含？ | 判定 |
|------|:---:|:---:|:---:|------|
| D_FRONTEND 新增通知渠道实现 | ✅ 相同 | — | — | 原地升级 |
| D_FRONTEND 新增数据采集模块 | ❌ 不同 | ✅ 有 | ✅ 是 | 拆分独立蓝图 |
| D_FRONTEND 新增风控计算逻辑 | ❌ 不同 | ✅ 有 | ✅ 是 | 拆分独立蓝图(D_RISK已覆盖) |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。人机交互层为纯新增/扩展型模块，无废弃/迁移文件。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type 词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

无。

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | interface_base.py | `D:\ZephyrAlpha\src\zephyr\frontend\interface_base.py` | 读取 | 无变更 |
| 2 | dashboard/ | `D:\ZephyrAlpha\src\zephyr\frontend\dashboard\` | 修改 | 完善组件 |
| 3 | implementations/ | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\` | 新建 | 默认实现(C轨开放后) |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 本蓝图的核心架构设计 | **本文档 §1-§10** | 已被取代的旧蓝图 |
| 本模块的施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 本模块的接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | FLE Fitness Functions | §4 接口契约、§10 依赖关系 |
| Tier 2 | D_RISK | CTR-P1-008 RiskDashboardSnapshot |
| Tier 2 | D_REPORTING | CTR-P1-009 PerformanceAttributionReport |
| Tier 2 | MOD-INF-035 系统大脑 | 运维可视化 |
| Tier 2 | MOD-INF-015 系统遥测 | 告警通道 |
| Tier 2 | MOD-GATE_ENGINE 门禁引擎 | 人机协同 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| Base 类接口变更 | 需 Owner 审批+通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| Dashboard 组件变更 | AI 可自主修改 | — | 更新配置文件 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI 可自主修改 | — | — |
| 非关键补充 | AI 可自主修改 | — | — |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |
