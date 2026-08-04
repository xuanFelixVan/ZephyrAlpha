---
doc_type: architecture_view
title: D_PF_CORE 组合核心架构文档
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 63_d_pf_core / 组合核心域 / Portfolio Core

> **功能简介 / Overview**: 组合核心，负责投资组合构建、持仓管理和组合优化

> **文档作用 / Purpose**: 展示 组合核心（D_PF_CORE）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/63_d_pf_core.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 63 | Number | 63 |
| 域ID | D_PF_CORE | Domain ID | D_PF_CORE |
| 域名称 | 组合核心 | Domain Name | Portfolio Core |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 16 | Module Count | 16 |
| 域内依赖 | 22 | Internal Dependencies | 22 |
| 跨域入边 | 1 | Cross-domain Incoming | 1 |
| 跨域出边 | 44 | Cross-domain Outgoing | 44 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 16 | Production Modules | 16 |
| 容量 | 16/150 (正常) | Capacity | 16/150 (正常) |
| 描述 | 组合核心，负责投资组合构建、持仓管理和组合优化 | Description | 组合核心，负责投资组合构建、持仓管理和组合优化 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 16 个模块（生产态 16 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_pf_core_core_performance_attribution_engine_py["性能Attribution引擎<br/>Performance Attribution Engine — 绩效归因引擎<br/>(MOD-PF-007 / PC-10)<br/>文件: core/performance_attribution_engine.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_rebalance_scheduler_py["Rebalance调度器<br/>Rebalance Scheduler — 再平衡调度器 (MOD-PF-003)<br/>文件: core/rebalance_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_topn_momentum_strategy_py["TopN 动量等权策略<br/>D_PORTFOLIO_CORE — TopN 动量等权策略<br/>Topn Momentum Strategy<br/>文件: pf_core/topn_momentum_strategy.py<br/>(生产态 / production)"]
    tests_pf_core_test_intraday_surge_fall_strategy_py["IntradaySurgeFallStrategy 单元测试<br/>（路径 B 示例策略）<br/>Test Intraday Surge Fall Strategy<br/>文件: pf_core<br/>/test_intraday_surge_fall_strategy.py<br/>(生产态 / production)"]
    tests_pf_core_test_orderbook_imbalance_strategy_py["OrderBookImbalanceStrategy 单元测试<br/>（路径 B 盘口失衡反转策略）<br/>Test Orderbook Imbalance Strategy<br/>文件: pf_core<br/>/test_orderbook_imbalance_strategy.py<br/>(生产态 / production)"]
    tests_pf_core_test_strategy_runner_tick_py["StrategyRunner.run_tick_backtest 单元测试<br/>（路径 A：日频信号 × tick 撮合）<br/>Test Strategy Runner Tick<br/>文件: pf_core/test_strategy_runner_tick.py<br/>(生产态 / production)"]
    tests_pf_core_test_vwap_reversion_strategy_py["VWAPReversionStrategy 单元测试<br/>（路径 B 均值回归策略）<br/>Test Vwap Reversion Strategy<br/>文件: pf_core/test_vwap_reversion_strategy.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_performance_attribution_engine_py ~~~ src_zephyr_pf_core_core_rebalance_scheduler_py
    src_zephyr_pf_core_core_rebalance_scheduler_py ~~~ src_zephyr_pf_core_topn_momentum_strategy_py
    src_zephyr_pf_core_topn_momentum_strategy_py ~~~ tests_pf_core_test_intraday_surge_fall_strategy_py
    tests_pf_core_test_intraday_surge_fall_strategy_py ~~~ tests_pf_core_test_orderbook_imbalance_strategy_py
    tests_pf_core_test_orderbook_imbalance_strategy_py ~~~ tests_pf_core_test_strategy_runner_tick_py
    tests_pf_core_test_strategy_runner_tick_py ~~~ tests_pf_core_test_vwap_reversion_strategy_py
    src_zephyr_pf_core_core_portfolio_optimizer_py["组合优化方法<br/>Portfolio Optimizer — 组合优化器 (MOD-PF-002)<br/>文件: core/portfolio_optimizer.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_constraint_solver_py["约束不可满足<br/>Constraint Solver — 约束求解器 (MOD-PF-006)<br/>文件: core/constraint_solver.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_strategy_engine_py["策略生命周期状态<br/>Strategy Engine — 策略引擎 (MOD-PF-001)<br/>文件: core/strategy_engine.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_strategy_engine_init_py["pf_core/strategy_engine 包入口<br/>D_PORTFOLIO_CORE — Portfolio Construction<br/>Strategies<br/>Init<br/>文件: strategy_engine/__init__.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_constraint_solver_py ~~~ src_zephyr_pf_core_core_strategy_engine_py
    src_zephyr_pf_core_core_strategy_engine_py ~~~ src_zephyr_pf_core_strategy_engine_init_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py["StrategyRunner 策略运行器<br/>D_PORTFOLIO_CORE — StrategyRunner 策略运行器<br/>（胶水层）<br/>Strategy Runner<br/>文件: strategy_engine/strategy_runner.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_intraday_surge_fall_strategy_py["30秒冲高回落做T策略<br/>D_PORTFOLIO_CORE — 30秒冲高回落做T策略（路径 B<br/>示例策略）<br/>Intraday Surge Fall Strategy<br/>文件: pf_core/intraday_surge_fall_strategy.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_orderbook_imbalance_strategy_py["盘口失衡反转做T策略<br/>D_PORTFOLIO_CORE — 盘口失衡反转做T策略（路径 B<br/>策略）<br/>Orderbook Imbalance Strategy<br/>文件: pf_core/orderbook_imbalance_strategy.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_vwap_reversion_strategy_py["VWAP 回归做T策略<br/>D_PORTFOLIO_CORE — VWAP 回归做T策略（路径 B<br/>策略）<br/>Vwap Reversion Strategy<br/>文件: pf_core/vwap_reversion_strategy.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_intraday_surge_fall_strategy_py ~~~ src_zephyr_pf_core_orderbook_imbalance_strategy_py
    src_zephyr_pf_core_orderbook_imbalance_strategy_py ~~~ src_zephyr_pf_core_vwap_reversion_strategy_py
    src_zephyr_pf_core_strategy_engine_tick_strategy_base_py["Tick策略基础<br/>D_PORTFOLIO_CORE — TickStrategyBase +<br/>TickStrategyRegistry（路径 B：tick 级...<br/>Tick Strategy Base<br/>文件: strategy_engine/tick_strategy_base.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_vwap_reversion_strategy_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    src_zephyr_pf_core_intraday_surge_fall_strategy_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    src_zephyr_pf_core_orderbook_imbalance_strategy_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    src_zephyr_pf_core_core_rebalance_scheduler_py -->|import / import| src_zephyr_pf_core_core_strategy_engine_py
    src_zephyr_pf_core_core_rebalance_scheduler_py -->|导入依赖 / import_depends| src_zephyr_pf_core_core_portfolio_optimizer_py
    src_zephyr_pf_core_core_rebalance_scheduler_py -->|import / import| src_zephyr_pf_core_core_portfolio_optimizer_py
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|导入依赖 / import_depends| src_zephyr_pf_core_core_constraint_solver_py
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|import / import| src_zephyr_pf_core_core_constraint_solver_py
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|import / import| src_zephyr_pf_core_core_strategy_engine_py
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_init_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| src_zephyr_pf_core_vwap_reversion_strategy_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| src_zephyr_pf_core_intraday_surge_fall_strategy_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| src_zephyr_pf_core_orderbook_imbalance_strategy_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    src_zephyr_pf_core_strategy_engine_init_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_strategy_runner_py
    tests_pf_core_test_intraday_surge_fall_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_intraday_surge_fall_strategy_py
    tests_pf_core_test_intraday_surge_fall_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    tests_pf_core_test_orderbook_imbalance_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_orderbook_imbalance_strategy_py
    tests_pf_core_test_orderbook_imbalance_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    tests_pf_core_test_vwap_reversion_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_vwap_reversion_strategy_py
    tests_pf_core_test_vwap_reversion_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    tests_pf_core_test_strategy_runner_tick_py -->|测试依赖 / test_depends| src_zephyr_pf_core_strategy_engine_strategy_runner_py
    D_RISK["风控<br/>风控，负责风险指标计算、风险限额管理和风险预警<br/>Risk Control<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_strategy_engine_py -->|导入依赖 / import_depends| D_RISK
    D_POSITION["仓位管理<br/>仓位管理，负责持仓跟踪、仓位计算和盈亏分析<br/>Position Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_rebalance_scheduler_py -->|导入依赖 / import_depends| D_POSITION
    src_zephyr_pf_core_core_constraint_solver_py -->|contract / contract| D_RISK
    D_INFRASTRUCTURE["跨层契约基础设施<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理<br/>和契约校验<br/>Cross-Layer Contract Infrastructure<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_strategy_engine_py -->|contract / contract| D_INFRASTRUCTURE
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|contract / contract| D_INFRASTRUCTURE
    D_PF_ALLOC["组合分配<br/>组合分配，负责资产配置、权重分配和再平衡<br/>Portfolio Allocation<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_constraint_solver_py -->|导入依赖 / import_depends| D_PF_ALLOC
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|导入依赖 / import_depends| D_RISK
    src_zephyr_pf_core_core_rebalance_scheduler_py -->|导入依赖 / import_depends| D_POSITION
    src_zephyr_pf_core_core_rebalance_scheduler_py -->|导入依赖 / import_depends| D_POSITION
    D_FACTOR["因子<br/>因子，负责因子计算、因子库管理和因子评价<br/>Factor<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| D_FACTOR
    D_BACKTEST["回测<br/>回测，负责历史数据回测、回测引擎和回测报告<br/>Backtest<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    tests_pf_core_test_orderbook_imbalance_strategy_py -->|测试依赖 / test_depends| D_BACKTEST
    tests_pf_core_test_vwap_reversion_strategy_py -->|测试依赖 / test_depends| D_BACKTEST
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| D_FACTOR
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_pf_core_core_strategy_engine_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_EX_CORE["执行核心<br/>执行核心，负责订单执行引擎、执行策略和执行管理<br/>Execution Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_strategy_runner_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_pf_core_core_constraint_solver_py,src_zephyr_pf_core_core_performance_attribution_engine_py,src_zephyr_pf_core_core_portfolio_optimizer_py,src_zephyr_pf_core_core_rebalance_scheduler_py,src_zephyr_pf_core_core_strategy_engine_py,src_zephyr_pf_core_intraday_surge_fall_strategy_py,src_zephyr_pf_core_orderbook_imbalance_strategy_py,src_zephyr_pf_core_strategy_engine_init_py,src_zephyr_pf_core_strategy_engine_strategy_runner_py,src_zephyr_pf_core_strategy_engine_tick_strategy_base_py,src_zephyr_pf_core_topn_momentum_strategy_py,src_zephyr_pf_core_vwap_reversion_strategy_py,tests_pf_core_test_intraday_surge_fall_strategy_py,tests_pf_core_test_orderbook_imbalance_strategy_py,tests_pf_core_test_strategy_runner_tick_py,tests_pf_core_test_vwap_reversion_strategy_py production
    class D_RISK,D_POSITION,D_INFRASTRUCTURE,D_PF_ALLOC,D_FACTOR,D_BACKTEST,D_EX_CORE external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 16 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_pf_core_core_performance_attribution_engine_py["性能Attribution引擎<br/>Performance Attribution Engine — 绩效归因引擎<br/>(MOD-PF-007 / PC-10)<br/>文件: core/performance_attribution_engine.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_rebalance_scheduler_py["Rebalance调度器<br/>Rebalance Scheduler — 再平衡调度器 (MOD-PF-003)<br/>文件: core/rebalance_scheduler.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_topn_momentum_strategy_py["TopN 动量等权策略<br/>D_PORTFOLIO_CORE — TopN 动量等权策略<br/>Topn Momentum Strategy<br/>文件: pf_core/topn_momentum_strategy.py<br/>(生产态 / production)"]
    tests_pf_core_test_intraday_surge_fall_strategy_py["IntradaySurgeFallStrategy 单元测试<br/>（路径 B 示例策略）<br/>Test Intraday Surge Fall Strategy<br/>文件: pf_core<br/>/test_intraday_surge_fall_strategy.py<br/>(生产态 / production)"]
    tests_pf_core_test_orderbook_imbalance_strategy_py["OrderBookImbalanceStrategy 单元测试<br/>（路径 B 盘口失衡反转策略）<br/>Test Orderbook Imbalance Strategy<br/>文件: pf_core<br/>/test_orderbook_imbalance_strategy.py<br/>(生产态 / production)"]
    tests_pf_core_test_strategy_runner_tick_py["StrategyRunner.run_tick_backtest 单元测试<br/>（路径 A：日频信号 × tick 撮合）<br/>Test Strategy Runner Tick<br/>文件: pf_core/test_strategy_runner_tick.py<br/>(生产态 / production)"]
    tests_pf_core_test_vwap_reversion_strategy_py["VWAPReversionStrategy 单元测试<br/>（路径 B 均值回归策略）<br/>Test Vwap Reversion Strategy<br/>文件: pf_core/test_vwap_reversion_strategy.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_performance_attribution_engine_py ~~~ src_zephyr_pf_core_core_rebalance_scheduler_py
    src_zephyr_pf_core_core_rebalance_scheduler_py ~~~ src_zephyr_pf_core_topn_momentum_strategy_py
    src_zephyr_pf_core_topn_momentum_strategy_py ~~~ tests_pf_core_test_intraday_surge_fall_strategy_py
    tests_pf_core_test_intraday_surge_fall_strategy_py ~~~ tests_pf_core_test_orderbook_imbalance_strategy_py
    tests_pf_core_test_orderbook_imbalance_strategy_py ~~~ tests_pf_core_test_strategy_runner_tick_py
    tests_pf_core_test_strategy_runner_tick_py ~~~ tests_pf_core_test_vwap_reversion_strategy_py
    src_zephyr_pf_core_core_portfolio_optimizer_py["组合优化方法<br/>Portfolio Optimizer — 组合优化器 (MOD-PF-002)<br/>文件: core/portfolio_optimizer.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_constraint_solver_py["约束不可满足<br/>Constraint Solver — 约束求解器 (MOD-PF-006)<br/>文件: core/constraint_solver.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_strategy_engine_py["策略生命周期状态<br/>Strategy Engine — 策略引擎 (MOD-PF-001)<br/>文件: core/strategy_engine.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_strategy_engine_init_py["pf_core/strategy_engine 包入口<br/>D_PORTFOLIO_CORE — Portfolio Construction<br/>Strategies<br/>Init<br/>文件: strategy_engine/__init__.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_core_constraint_solver_py ~~~ src_zephyr_pf_core_core_strategy_engine_py
    src_zephyr_pf_core_core_strategy_engine_py ~~~ src_zephyr_pf_core_strategy_engine_init_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py["StrategyRunner 策略运行器<br/>D_PORTFOLIO_CORE — StrategyRunner 策略运行器<br/>（胶水层）<br/>Strategy Runner<br/>文件: strategy_engine/strategy_runner.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_intraday_surge_fall_strategy_py["30秒冲高回落做T策略<br/>D_PORTFOLIO_CORE — 30秒冲高回落做T策略（路径 B<br/>示例策略）<br/>Intraday Surge Fall Strategy<br/>文件: pf_core/intraday_surge_fall_strategy.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_orderbook_imbalance_strategy_py["盘口失衡反转做T策略<br/>D_PORTFOLIO_CORE — 盘口失衡反转做T策略（路径 B<br/>策略）<br/>Orderbook Imbalance Strategy<br/>文件: pf_core/orderbook_imbalance_strategy.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_vwap_reversion_strategy_py["VWAP 回归做T策略<br/>D_PORTFOLIO_CORE — VWAP 回归做T策略（路径 B<br/>策略）<br/>Vwap Reversion Strategy<br/>文件: pf_core/vwap_reversion_strategy.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_intraday_surge_fall_strategy_py ~~~ src_zephyr_pf_core_orderbook_imbalance_strategy_py
    src_zephyr_pf_core_orderbook_imbalance_strategy_py ~~~ src_zephyr_pf_core_vwap_reversion_strategy_py
    src_zephyr_pf_core_strategy_engine_tick_strategy_base_py["Tick策略基础<br/>D_PORTFOLIO_CORE — TickStrategyBase +<br/>TickStrategyRegistry（路径 B：tick 级...<br/>Tick Strategy Base<br/>文件: strategy_engine/tick_strategy_base.py<br/>(生产态 / production)"]
    src_zephyr_pf_core_vwap_reversion_strategy_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    src_zephyr_pf_core_intraday_surge_fall_strategy_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    src_zephyr_pf_core_orderbook_imbalance_strategy_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    src_zephyr_pf_core_core_rebalance_scheduler_py -->|import / import| src_zephyr_pf_core_core_strategy_engine_py
    src_zephyr_pf_core_core_rebalance_scheduler_py -->|导入依赖 / import_depends| src_zephyr_pf_core_core_portfolio_optimizer_py
    src_zephyr_pf_core_core_rebalance_scheduler_py -->|import / import| src_zephyr_pf_core_core_portfolio_optimizer_py
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|导入依赖 / import_depends| src_zephyr_pf_core_core_constraint_solver_py
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|import / import| src_zephyr_pf_core_core_constraint_solver_py
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|import / import| src_zephyr_pf_core_core_strategy_engine_py
    src_zephyr_pf_core_core_portfolio_optimizer_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_init_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| src_zephyr_pf_core_vwap_reversion_strategy_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| src_zephyr_pf_core_intraday_surge_fall_strategy_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| src_zephyr_pf_core_orderbook_imbalance_strategy_py
    src_zephyr_pf_core_strategy_engine_strategy_runner_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    src_zephyr_pf_core_strategy_engine_init_py -->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_strategy_runner_py
    tests_pf_core_test_intraday_surge_fall_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_intraday_surge_fall_strategy_py
    tests_pf_core_test_intraday_surge_fall_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    tests_pf_core_test_orderbook_imbalance_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_orderbook_imbalance_strategy_py
    tests_pf_core_test_orderbook_imbalance_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    tests_pf_core_test_vwap_reversion_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_vwap_reversion_strategy_py
    tests_pf_core_test_vwap_reversion_strategy_py -->|测试依赖 / test_depends| src_zephyr_pf_core_strategy_engine_tick_strategy_base_py
    tests_pf_core_test_strategy_runner_tick_py -->|测试依赖 / test_depends| src_zephyr_pf_core_strategy_engine_strategy_runner_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_pf_core_core_constraint_solver_py,src_zephyr_pf_core_core_performance_attribution_engine_py,src_zephyr_pf_core_core_portfolio_optimizer_py,src_zephyr_pf_core_core_rebalance_scheduler_py,src_zephyr_pf_core_core_strategy_engine_py,src_zephyr_pf_core_intraday_surge_fall_strategy_py,src_zephyr_pf_core_orderbook_imbalance_strategy_py,src_zephyr_pf_core_strategy_engine_init_py,src_zephyr_pf_core_strategy_engine_strategy_runner_py,src_zephyr_pf_core_strategy_engine_tick_strategy_base_py,src_zephyr_pf_core_topn_momentum_strategy_py,src_zephyr_pf_core_vwap_reversion_strategy_py,tests_pf_core_test_intraday_surge_fall_strategy_py,tests_pf_core_test_orderbook_imbalance_strategy_py,tests_pf_core_test_strategy_runner_tick_py,tests_pf_core_test_vwap_reversion_strategy_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 30秒冲高回落做T策略 / Intraday Surge Fall Strategy (pf_co... | → | D_BACKTEST 回测: 逐笔replay / tick_replay (core/tick_replay.py) | 导入依赖 / import_depends |
| 2 | 盘口失衡反转做T策略 / Orderbook Imbalance Strategy (pf_co... | → | D_BACKTEST 回测: 逐笔replay / tick_replay (core/tick_replay.py) | 导入依赖 / import_depends |
| 3 | StrategyRunner 策略运行器 / Strategy Runner (strategy_eng... | → | D_BACKTEST 回测: 引擎基类 / L_BACKTEST — Backtest Engine Layer (core/engi... | 导入依赖 / import_depends |
| 4 | StrategyRunner 策略运行器 / Strategy Runner (strategy_eng... | → | D_BACKTEST 回测: 事件driven引擎 / event_driven_engine (implementations/eve... | 导入依赖 / import_depends |
| 5 | StrategyRunner 策略运行器 / Strategy Runner (strategy_eng... | → | D_BACKTEST 回测: vectorized引擎 / L_BACKTEST — Vectorized Backtest Engine... | 导入依赖 / import_depends |
| 6 | Tick策略基础 / Tick Strategy Base (strategy_engine/tick_s... | → | D_BACKTEST 回测: 逐笔replay / tick_replay (core/tick_replay.py) | 导入依赖 / import_depends |
| 7 | VWAP 回归做T策略 / Vwap Reversion Strategy (pf_core/vwap_... | → | D_BACKTEST 回测: 逐笔replay / tick_replay (core/tick_replay.py) | 导入依赖 / import_depends |
| 8 | IntradaySurgeFallStrategy 单元测试 / Test Intraday Surge ... | → | D_BACKTEST 回测: 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 测试依赖 / test_depends |
| 9 | OrderBookImbalanceStrategy 单元测试 / Test Orderbook Imba... | → | D_BACKTEST 回测: 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 测试依赖 / test_depends |
| 10 | VWAPReversionStrategy 单元测试 / Test Vwap Reversion Stra... | → | D_BACKTEST 回测: 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 测试依赖 / test_depends |
| 11 | StrategyRunner 策略运行器 / Strategy Runner (strategy_eng... | → | D_FACTOR 因子: D-FACTOR-ANA-10 多因子合成——将多个因子值合成为综合信号... | 导入依赖 / import_depends |
| 12 | StrategyRunner 策略运行器 / Strategy Runner (strategy_eng... | → | D_FACTOR 因子: D-FACTOR-03 因子评估回测运行器——端到端因子评估。 / back... | 导入依赖 / import_depends |
| 13 | StrategyRunner 策略运行器 / Strategy Runner (strategy_eng... | → | D_FACTOR 因子: 因子基类 / ZephyrAlpha — D_FACTOR Alpha Factor Layer (fa... | 导入依赖 / import_depends |
| 14 | 策略生命周期状态 / Strategy Engine (core/strategy_engine.py) | → | D_GOVERNANCE 生命周期管理: 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | 导入依赖 / import_depends |
| 15 | 策略生命周期状态 / Strategy Engine (core/strategy_engine.py) | → | D_GOVERNANCE 生命周期管理: 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | 导入依赖 / import_depends |
| 16 | StrategyRunner 策略运行器 / Strategy Runner (strategy_eng... | → | D_GOVERNANCE 生命周期管理: 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | 导入依赖 / import_depends |
| 17 | TopN 动量等权策略 / Topn Momentum Strategy (pf_core/topn_... | → | D_GOVERNANCE 生命周期管理: 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | 导入依赖 / import_depends |
| 18 | 约束不可满足 / Constraint Solver (core/constraint_solver.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险Limits / Risk Limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 19 | 性能Attribution引擎 / Performance Attribution Engine (cor... | → | D_INFRASTRUCTURE 跨层契约基础设施: 性能Attribution报告 / Performance Attribution Report (con... | 导入依赖 / import_depends |
| 20 | 组合优化方法 / Portfolio Optimizer (core/portfolio_optimi... | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险Limits / Risk Limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 21 | 组合优化方法 / Portfolio Optimizer (core/portfolio_optimi... | → | D_INFRASTRUCTURE 跨层契约基础设施: 目标投资组合 / Target Portfolio (contracts/target_portfol... | 导入依赖 / import_depends |
| 22 | 组合优化方法 / Portfolio Optimizer (core/portfolio_optimi... | → | D_INFRASTRUCTURE 跨层契约基础设施: 目标投资组合 / Target Portfolio (contracts/target_portfol... | contract / contract |
| 23 | Rebalance调度器 / Rebalance Scheduler (core/rebalance_sch... | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险Limits / Risk Limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 24 | Rebalance调度器 / Rebalance Scheduler (core/rebalance_sch... | → | D_INFRASTRUCTURE 跨层契约基础设施: 目标投资组合 / Target Portfolio (contracts/target_portfol... | 导入依赖 / import_depends |
| 25 | 策略生命周期状态 / Strategy Engine (core/strategy_engine.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 策略生命周期事件 / Strategy Lifecycle Event (contracts/st... | contract / contract |
| 26 | 策略生命周期状态 / Strategy Engine (core/strategy_engine.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 策略生命周期事件 / Strategy Lifecycle Event (contracts/st... | 导入依赖 / import_depends |
| 27 | 约束不可满足 / Constraint Solver (core/constraint_solver.py) | → | D_PF_ALLOC 组合分配: 门禁裁决级别 / Strategy Correlation Gate (core/strategy_c... | 导入依赖 / import_depends |
| 28 | 性能Attribution引擎 / Performance Attribution Engine (cor... | → | D_PF_ALLOC 组合分配: 门禁裁决级别 / Strategy Correlation Gate (core/strategy_c... | 导入依赖 / import_depends |
| 29 | 包入口 / Init (strategy_engine/__init__.py) | → | D_PF_ALLOC 组合分配: 默认Equity策略 / Default Equity Strategy (pf_core/default... | 导入依赖 / import_depends |
| 30 | Rebalance调度器 / Rebalance Scheduler (core/rebalance_sch... | → | D_POSITION 仓位管理: 漂移检测范围 / Position Drift Monitor (core/position_drif... | 导入依赖 / import_depends |
| 31 | Rebalance调度器 / Rebalance Scheduler (core/rebalance_sch... | → | D_POSITION 仓位管理: 再平衡触发类型 / Rebalance Engine (core/rebalance_engine.py) | 导入依赖 / import_depends |
| 32 | Rebalance调度器 / Rebalance Scheduler (core/rebalance_sch... | → | D_POSITION 仓位管理: 事件驱动 / Position Reconciler (position/position_reconci... | 导入依赖 / import_depends |
| 33 | 性能Attribution引擎 / Performance Attribution Engine (cor... | → | D_REPORTING 报告: 单笔成交的 TCA 分析，返回执行报告 / Analytics Base (repor... | 导入依赖 / import_depends |
| 34 | 约束不可满足 / Constraint Solver (core/constraint_solver.py) | → | D_RISK 风控: 风险Limits / Risk Limits (risk/risk_limits.py) | contract / contract |
| 35 | 性能Attribution引擎 / Performance Attribution Engine (cor... | → | D_RISK 风控: 风险分解输入数据非法 / Risk Decomposition (core/risk_deco... | 导入依赖 / import_depends |
| 36 | 组合优化方法 / Portfolio Optimizer (core/portfolio_optimi... | → | D_RISK 风控: 风险预算输入数据非法 / Risk Budget Allocator (core/risk_b... | 导入依赖 / import_depends |
| 37 | 组合优化方法 / Portfolio Optimizer (core/portfolio_optimi... | → | D_RISK 风控: 风险预算输入数据非法 / Risk Budget Allocator (core/risk_b... | 导入依赖 / import_depends |
| 38 | 组合优化方法 / Portfolio Optimizer (core/portfolio_optimi... | → | D_RISK 风控: 风险分解输入数据非法 / Risk Decomposition (core/risk_deco... | 导入依赖 / import_depends |
| 39 | 策略生命周期状态 / Strategy Engine (core/strategy_engine.py) | → | D_RISK 风控: 风险Limits / Risk Limits (risk/risk_limits.py) | 导入依赖 / import_depends |
| 40 | 约束不可满足 / Constraint Solver (core/constraint_solver.py) | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |
| 41 | 性能Attribution引擎 / Performance Attribution Engine (cor... | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |
| 42 | 组合优化方法 / Portfolio Optimizer (core/portfolio_optimi... | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |
| 43 | Rebalance调度器 / Rebalance Scheduler (core/rebalance_sch... | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |
| 44 | 策略生命周期状态 / Strategy Engine (core/strategy_engine.py) | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_EX_CORE 执行核心: 交易会话 / trading_session (ex_core/trading_session.py) | → | StrategyRunner 策略运行器 / Strategy Runner (strategy_eng... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 10 个外部域直接连接（出边 44 条 + 入边 1 条 = 45 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_PF_CORE["D_PF_CORE<br/>组合核心"]
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_RISK["D_RISK<br/>风控"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_PF_ALLOC["D_PF_ALLOC<br/>组合分配"]
    D_POSITION["D_POSITION<br/>仓位管理"]
    D_FACTOR["D_FACTOR<br/>因子"]
    D_REPORTING["D_REPORTING<br/>报告"]
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_PF_CORE -->|10条 导入依赖 / import_depends, 测试依赖 / test_depends| D_BACKTEST
    D_PF_CORE -->|9条 contract / contract, 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_PF_CORE -->|6条 contract / contract, 导入依赖 / import_depends| D_RISK
    D_PF_CORE -->|5条 导入依赖 / import_depends| D_SHARED
    D_PF_CORE -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_PF_CORE -->|3条 导入依赖 / import_depends| D_PF_ALLOC
    D_PF_CORE -->|3条 导入依赖 / import_depends| D_POSITION
    D_PF_CORE -->|3条 导入依赖 / import_depends| D_FACTOR
    D_PF_CORE -->|1条 导入依赖 / import_depends| D_REPORTING
    D_EX_CORE -->|1条 导入依赖 / import_depends| D_PF_CORE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
