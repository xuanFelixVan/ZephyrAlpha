---
doc_type: architecture_view
title: D_EX_CORE 执行核心架构文档
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 44_d_ex_core / 执行核心域 / Execution Core

> **功能简介 / Overview**: 执行核心，负责订单执行引擎、执行策略和执行管理

> **文档作用 / Purpose**: 展示 执行核心（D_EX_CORE）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/44_d_ex_core.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 44 | Number | 44 |
| 域ID | D_EX_CORE | Domain ID | D_EX_CORE |
| 域名称 | 执行核心 | Domain Name | Execution Core |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 41 | Module Count | 41 |
| 域内依赖 | 32 | Internal Dependencies | 32 |
| 跨域入边 | 10 | Cross-domain Incoming | 10 |
| 跨域出边 | 68 | Cross-domain Outgoing | 68 |
| 设计态模块 | 23 | Design Modules | 23 |
| 生产态模块 | 18 | Production Modules | 18 |
| 容量 | 18/150 (正常) | Capacity | 18/150 (正常) |
| 描述 | 执行核心，负责订单执行引擎、执行策略和执行管理 | Description | 执行核心，负责订单执行引擎、执行策略和执行管理 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 41 个模块（生产态 18 + 设计态 23），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_ex_core_adapters_init_py["ex_core/adapters 包入口<br/>adapters 包入口，整合接口适配相关模块<br/>文件: adapters/__init__.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_aggregate_root_manager_py["Aggregate根入口管理器<br/>D_EX_CORE — Aggregate Root Manager<br/>(执行域聚合根管理器)<br/>文件: ex_core/aggregate_root_manager.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_auction_deviation_executor_py["拍卖偏差执行器<br/>执行核心的执行器，执行具体操作（auction<br/>deviation executor）<br/>⛔ 门禁:实盘交易环境+集合竞价数据源+miniQMT实盘AP<br/>I(D-EX-CORE-32)<br/>auction_deviation_executor<br/>文件: ex_core/auction_deviation_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_audit_journal_init_py["Execution Audit Journal 包<br/>D_EXECUTION_CORE — Execution Audit Journal 包<br/>Init<br/>文件: audit_journal/__init__.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_batch_executor_py["批次执行器<br/>执行核心的执行器，执行具体操作（batch executor）<br/>⛔ 门禁:实盘交易环境+A股Tick数据源+miniQMT实盘API<br/>(D-EX-CORE-30)<br/>batch_executor<br/>文件: ex_core/batch_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_batch_take_profit_executor_py["批次止盈利润执行器<br/>执行核心的执行器，执行具体操作（batch take<br/>profit executor）<br/>⛔ 门禁:实盘交易环境+A股Tick数据源+miniQMT实盘API<br/>(D-EX-CORE-31)<br/>batch_take_profit_executor<br/>文件: ex_core/batch_take_profit_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_blueprint_implementer_py["蓝图Implementer<br/>ex core包的blueprint_implementer模块<br/>⛔ 门禁:依赖模块(OMS+引擎+路由+报告)全部就绪<br/>(D-EX-CORE-37)<br/>Blueprint Implementer<br/>文件: ex_core/blueprint_implementer.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_conditional_order_manager_py["conditional订单管理器<br/>ex_core的管理器，统一管理一类资源的生命周期<br/>⛔ 门禁:EX-SOR算法路由就绪(D-EX-CORE-42)<br/>conditional_order_manager<br/>文件: ex_core/conditional_order_manager.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_deployment_consistency_manager_py["部署一致性管理器<br/>ex core包的deployment_consistency_manager模块<br/>⛔ 门禁:CI/CD灰度发布基础设施✅已就绪(MOD-CD-001<br/>shadow_canary_deploy,2026-08-03);实盘环境⏳待Owne<br/>r决策开通实盘账户+选定券商通道(D-EX-CORE-21)<br/>Deployment Consistency Manager<br/>文件: ex_core/deployment_consistency_manager.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_engine_py["执行引擎<br/>本模块内 ``ExecutionEngineRunRecord``<br/>为引擎内部聚合快照，非 CTR-P1-007；<br/>D_EXECUTION_CORE — Execution Engine<br/>文件: ex_core/execution_engine.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_execution_mcp_server_py["执行MCP服务端<br/>ex_core的服务端，接收并处理请求<br/>⛔ 门禁:MCP协议安全生态未成熟;开通需OAuth+RBAC+审<br/>计+沙箱+AI置信度>=95%稳定6月+渗透测试<br/>(D-EX-CORE-59)<br/>execution_mcp_server<br/>文件: ex_core/execution_mcp_server.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_risk_gate_py["执行风险门禁<br/>ex core包的execution_risk_gate模块<br/>⛔ 门禁:D-RISK域L04-limits就绪+风控规则引擎可调用<br/>(D-EX-CORE-07)<br/>Execution Risk Gate<br/>文件: ex_core/execution_risk_gate.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_tca_py["执行交易成本分析<br/>ex core包的execution_tca模块<br/>⛔ 门禁:历史执行数据>=30天+滑点模型参数可获取<br/>(D-EX-CORE-12)<br/>Execution Tca<br/>文件: ex_core/execution_tca.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_factory_py["工厂<br/>ex core包的factory模块<br/>文件: ex_core/factory.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_live_simulation_switcher_py["实盘仿真切换器<br/>支撑交易核心流程（live simulation switcher）<br/>⛔ 门禁:实盘券商连接(OKX/XTP/CTP)就绪<br/>(D-EX-CORE-35)<br/>live_simulation_switcher<br/>文件: ex_core/live_simulation_switcher.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_microstructure_modeler_py["微观结构建模器<br/>ex core包的microstructure_modeler模块<br/>⛔ 门禁:订单簿Level-2数据可获取+VPIN计算引擎就绪+<br/>LOB快照频率>=1秒(D-EX-CORE-61)<br/>Microstructure Modeler<br/>文件: ex_core/microstructure_modeler.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_miniqmt_channel_manager_py["MiniqmtChannel管理器<br/>ex core包的miniqmt_channel_manager模块<br/>Miniqmt Channel Manager<br/>文件: ex_core/miniqmt_channel_manager.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_multi_contract_adapter_py["多契约适配器<br/>D_EX_CORE — Multi-Contract Adapter<br/>(多契约生产适配器)<br/>Multi Contract Adapter<br/>文件: ex_core/multi_contract_adapter.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_order_execution_saga_py["下单执行 Saga 编排器<br/>Order Execution Saga — 下单执行 Saga 编排器<br/>(MOD-EX-057 / D-EX-CORE-57)<br/>文件: ex_core/order_execution_saga.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_performance_monitor_py["性能监控器<br/>ex core包的performance_monitor模块<br/>⛔ 门禁:生产环境APM基础设施(D-EX-CORE-36)<br/>Performance Monitor<br/>文件: ex_core/performance_monitor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_pre_execution_checker_py["Pre执行检查器<br/>ex core包的pre_execution_checker模块<br/>⛔ 门禁:D-RISK风控参数就绪+市场状态实时数据源<br/>(D-EX-CORE-24)<br/>Pre Execution Checker<br/>文件: ex_core/pre_execution_checker.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_redis_idempotency["redis幂等性<br/>执行核心的子目录，归集相关子模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: redis_idempotency/<br/>(设计态 / design)"]
    src_zephyr_ex_core_sell_priority_scheduler_py["卖出优先级调度器<br/>卖priority调度器，ex_core的调度器，按时间或优先<br/>级安排任务执行。<br/>⛔ 门禁:实盘交易环境+miniQMT实盘API(D-EX-CORE-33)<br/>sell_priority_scheduler<br/>文件: ex_core/sell_priority_scheduler.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_services_live_portfolio_py["实时组合<br/>支撑交易核心流程（live portfolio）<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>live_portfolio<br/>文件: services/live_portfolio.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_signal_providers_py["信号提供器<br/>D_EXECUTION_CORE — 信号源 / 价格源 callable 工厂<br/>signal_providers<br/>文件: ex_core/signal_providers.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_stop_loss_take_profit_executor_py["停止亏损止盈利润执行器<br/>执行核心的执行器，执行具体操作（stop loss take<br/>profit executor）<br/>⛔ 门禁:实盘交易环境+A股Tick数据源+miniQMT实盘API<br/>(D-EX-CORE-29)<br/>stop_loss_take_profit_executor<br/>文件: ex_core/stop_loss_take_profit_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_trading_session_py["交易会话<br/>D_EXECUTION_CORE — TradingSession<br/>盘中实时调仓编排器<br/>trading_session<br/>文件: ex_core/trading_session.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_value_objects_py["值对象<br/>ex core包的value_objects模块<br/>Value Objects<br/>文件: ex_core/value_objects.py<br/>(设计态 / design)"]
    src_zephyr_governance_escalation_order_state_escalator_py["订单状态escalator<br/>Order State Escalator — v0.10.0<br/>订单状态机升级器。<br/>order_state_escalator<br/>文件: escalation/order_state_escalator.py<br/>(生产态 / production)"]
    tests_ex_core_test_position_reconciler_py["D-EX-CORE-56 盘中持仓对账器<br/>PositionReconciler 单元测试 — D-EX-CORE-56<br/>盘中持仓对账器。<br/>Test Position Reconciler<br/>文件: ex_core/test_position_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_init_py ~~~ src_zephyr_ex_core_aggregate_root_manager_py
    src_zephyr_ex_core_aggregate_root_manager_py ~~~ src_zephyr_ex_core_auction_deviation_executor_py
    src_zephyr_ex_core_auction_deviation_executor_py ~~~ src_zephyr_ex_core_audit_journal_init_py
    src_zephyr_ex_core_audit_journal_init_py ~~~ src_zephyr_ex_core_batch_executor_py
    src_zephyr_ex_core_batch_executor_py ~~~ src_zephyr_ex_core_batch_take_profit_executor_py
    src_zephyr_ex_core_batch_take_profit_executor_py ~~~ src_zephyr_ex_core_blueprint_implementer_py
    src_zephyr_ex_core_blueprint_implementer_py ~~~ src_zephyr_ex_core_conditional_order_manager_py
    src_zephyr_ex_core_conditional_order_manager_py ~~~ src_zephyr_ex_core_deployment_consistency_manager_py
    src_zephyr_ex_core_deployment_consistency_manager_py ~~~ src_zephyr_ex_core_execution_engine_py
    src_zephyr_ex_core_execution_engine_py ~~~ src_zephyr_ex_core_execution_mcp_server_py
    src_zephyr_ex_core_execution_mcp_server_py ~~~ src_zephyr_ex_core_execution_risk_gate_py
    src_zephyr_ex_core_execution_risk_gate_py ~~~ src_zephyr_ex_core_execution_tca_py
    src_zephyr_ex_core_execution_tca_py ~~~ src_zephyr_ex_core_factory_py
    src_zephyr_ex_core_factory_py ~~~ src_zephyr_ex_core_live_simulation_switcher_py
    src_zephyr_ex_core_live_simulation_switcher_py ~~~ src_zephyr_ex_core_microstructure_modeler_py
    src_zephyr_ex_core_microstructure_modeler_py ~~~ src_zephyr_ex_core_miniqmt_channel_manager_py
    src_zephyr_ex_core_miniqmt_channel_manager_py ~~~ src_zephyr_ex_core_multi_contract_adapter_py
    src_zephyr_ex_core_multi_contract_adapter_py ~~~ src_zephyr_ex_core_order_execution_saga_py
    src_zephyr_ex_core_order_execution_saga_py ~~~ src_zephyr_ex_core_performance_monitor_py
    src_zephyr_ex_core_performance_monitor_py ~~~ src_zephyr_ex_core_pre_execution_checker_py
    src_zephyr_ex_core_pre_execution_checker_py ~~~ src_zephyr_ex_core_redis_idempotency
    src_zephyr_ex_core_redis_idempotency ~~~ src_zephyr_ex_core_sell_priority_scheduler_py
    src_zephyr_ex_core_sell_priority_scheduler_py ~~~ src_zephyr_ex_core_services_live_portfolio_py
    src_zephyr_ex_core_services_live_portfolio_py ~~~ src_zephyr_ex_core_signal_providers_py
    src_zephyr_ex_core_signal_providers_py ~~~ src_zephyr_ex_core_stop_loss_take_profit_executor_py
    src_zephyr_ex_core_stop_loss_take_profit_executor_py ~~~ src_zephyr_ex_core_trading_session_py
    src_zephyr_ex_core_trading_session_py ~~~ src_zephyr_ex_core_value_objects_py
    src_zephyr_ex_core_value_objects_py ~~~ src_zephyr_governance_escalation_order_state_escalator_py
    src_zephyr_governance_escalation_order_state_escalator_py ~~~ tests_ex_core_test_position_reconciler_py
    src_zephyr_ex_core_adapters_miniqmt_broker_py["miniqmt券商<br/>MiniQMT 实盘券商适配器（对接<br/>xttrader，A股实盘交易）<br/>miniqmt_broker<br/>文件: adapters/miniqmt_broker.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_audit_journal_auditor_py["执行审计记录器<br/>Execution Audit Logger — 执行审计记录器<br/>(MOD-EX-003 / D-EX-CORE-15)<br/>Auditor<br/>文件: audit_journal/auditor.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_fill_handler_py["部分成交处理器<br/>是成交回报的账房先生——每次券商回报一笔成交Fill它<br/>就累加到对应订单上更新已成交数量重新计算加权均价<br/>累计佣金判断订单是否已全部成交一笔大单分3次成交<br/>它就记3笔最后算总账任何时刻都能回答这单成交了多<br/>少还剩多少均价多少<br/>文件: ex_core/fill_handler.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_position_reconciler_py["盘中持仓对账器<br/>D_EXECUTION_CORE — 盘中持仓对账器 (Position<br/>Reconciler)<br/>文件: ex_core/position_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_repository_interface_py["Repository接口<br/>D_EX_CORE — Repository Interface<br/>(执行域仓储接口)<br/>文件: ex_core/repository_interface.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_rl_optimal_executor_py["Rl最优执行器<br/>ex core包的rl_optimal_executor模块<br/>⛔ 门禁:RL训练基础设施+历史执行数据>=90天+Almgren<br/>-Chriss基线可运行+RL偏差阈值可配置(D-EX-CORE-60)<br/>Rl Optimal Executor<br/>文件: ex_core/rl_optimal_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_adapters_miniqmt_broker_py ~~~ src_zephyr_ex_core_audit_journal_auditor_py
    src_zephyr_ex_core_audit_journal_auditor_py ~~~ src_zephyr_ex_core_fill_handler_py
    src_zephyr_ex_core_fill_handler_py ~~~ src_zephyr_ex_core_position_reconciler_py
    src_zephyr_ex_core_position_reconciler_py ~~~ src_zephyr_ex_core_repository_interface_py
    src_zephyr_ex_core_repository_interface_py ~~~ src_zephyr_ex_core_rl_optimal_executor_py
    src_zephyr_ex_core_order_splitter_py["订单拆分器<br/>支撑交易核心流程（order splitter）<br/>⛔ 门禁:TCA<br/>(D-EX-CORE-12)就绪+订单簿深度数据可获取<br/>(D-EX-CORE-14)<br/>order_splitter<br/>文件: ex_core/order_splitter.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_position_tracker_init_py["Position Tracker 包<br/>D_EXECUTION_CORE — Position Tracker 包<br/>Init<br/>文件: position_tracker/__init__.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_order_splitter_py ~~~ src_zephyr_ex_core_position_tracker_init_py
    src_zephyr_ex_core_fill_processor_py["成交处理器<br/>执行核心的处理器，处理加工数据<br/>⛔ 门禁:Broker<br/>Adapter回报回调稳定+佣金费率表数据源就绪<br/>(D-EX-CORE-08)<br/>fill_processor<br/>文件: ex_core/fill_processor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_position_tracker_tracker_py["跟踪器<br/>D_EXECUTION_CORE — Position Tracker (持仓跟踪器)<br/>文件: position_tracker/tracker.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_fill_processor_py ~~~ src_zephyr_ex_core_position_tracker_tracker_py
    src_zephyr_ex_core_order_manager_py["订单管理器<br/>管理订单全生命周期：创建->风控校验->路由->状态跟<br/>踪<br/>D_EXECUTION_CORE — Order Manager<br/>文件: ex_core/order_manager.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| src_zephyr_ex_core_adapters_miniqmt_broker_py
    src_zephyr_ex_core_fill_processor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_order_splitter_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_stop_loss_take_profit_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_batch_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_batch_take_profit_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_auction_deviation_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_sell_priority_scheduler_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_live_simulation_switcher_py -.->|runtime / runtime| src_zephyr_ex_core_adapters_miniqmt_broker_py
    src_zephyr_ex_core_conditional_order_manager_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_execution_mcp_server_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_rl_optimal_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_splitter_py
    src_zephyr_ex_core_microstructure_modeler_py -.->|data / data| src_zephyr_ex_core_order_splitter_py
    src_zephyr_ex_core_microstructure_modeler_py -.->|data / data| src_zephyr_ex_core_rl_optimal_executor_py
    src_zephyr_ex_core_aggregate_root_manager_py -->|导入依赖 / import_depends| src_zephyr_ex_core_fill_handler_py
    src_zephyr_ex_core_aggregate_root_manager_py -->|导入依赖 / import_depends| src_zephyr_ex_core_repository_interface_py
    src_zephyr_ex_core_aggregate_root_manager_py -->|导入依赖 / import_depends| src_zephyr_ex_core_position_tracker_tracker_py
    src_zephyr_ex_core_execution_engine_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_fill_handler_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_order_execution_saga_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_order_execution_saga_py -->|导入依赖 / import_depends| src_zephyr_ex_core_audit_journal_auditor_py
    src_zephyr_ex_core_order_execution_saga_py -->|导入依赖 / import_depends| src_zephyr_ex_core_position_tracker_tracker_py
    src_zephyr_ex_core_position_reconciler_py -->|data / data| src_zephyr_ex_core_position_tracker_init_py
    src_zephyr_ex_core_repository_interface_py -->|runtime / runtime| src_zephyr_ex_core_position_tracker_init_py
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_adapters_init_py -->|导入依赖 / import_depends| src_zephyr_ex_core_adapters_miniqmt_broker_py
    src_zephyr_ex_core_audit_journal_init_py -->|导入依赖 / import_depends| src_zephyr_ex_core_audit_journal_auditor_py
    src_zephyr_ex_core_position_tracker_init_py -.->|runtime / runtime| src_zephyr_ex_core_fill_processor_py
    src_zephyr_ex_core_position_tracker_init_py -->|导入依赖 / import_depends| src_zephyr_ex_core_position_tracker_tracker_py
    tests_ex_core_test_position_reconciler_py -->|测试依赖 / test_depends| src_zephyr_ex_core_position_reconciler_py
    tests_ex_core_test_position_reconciler_py -->|测试依赖 / test_depends| src_zephyr_ex_core_position_tracker_tracker_py
    D_BACKTEST["回测<br/>回测，负责历史数据回测、回测引擎和回测报告<br/>Backtest<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| D_BACKTEST
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| D_TRADING
    D_PF_CORE["组合核心<br/>组合核心，负责投资组合构建、持仓管理和组合优化<br/>Portfolio Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| D_PF_CORE
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| D_BACKTEST
    D_SELL_DECISION["卖出决策<br/>卖出决策，负责卖出信号生成、卖出时机判断和退出策<br/>略<br/>Sell Decision<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    src_zephyr_ex_core_stop_loss_take_profit_executor_py -.->|runtime / runtime| D_SELL_DECISION
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| D_TRADING
    src_zephyr_ex_core_trading_session_py -->|contract / contract| D_TRADING
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_trading_session_py -->|contract / contract| D_GOVERNANCE
    src_zephyr_ex_core_trading_session_py -->|contract / contract| D_GOVERNANCE
    D_RISK["风控<br/>风控，负责风险指标计算、风险限额管理和风险预警<br/>Risk Control<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_live_simulation_switcher_py -.->|runtime / runtime| D_RISK
    src_zephyr_ex_core_sell_priority_scheduler_py -.->|runtime / runtime| D_SELL_DECISION
    src_zephyr_ex_core_stop_loss_take_profit_executor_py -.->|runtime / runtime| D_SELL_DECISION
    src_zephyr_ex_core_sell_priority_scheduler_py -.->|runtime / runtime| D_SELL_DECISION
    src_zephyr_ex_core_adapters_miniqmt_broker_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_BACKTEST -->|导入依赖 / import_depends| src_zephyr_ex_core_adapters_miniqmt_broker_py
    D_TRADING -->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    D_EX_SOR["执行路由<br/>执行路由，负责订单路由、智能拆单和执行场所选择<br/>Execution Routing<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_EX_SOR -->|导入依赖 / import_depends| src_zephyr_ex_core_execution_engine_py
    D_TRADING -->|import / import| src_zephyr_ex_core_fill_handler_py
    D_SELL_DECISION -.->|导入依赖 / import_depends| src_zephyr_ex_core_services_live_portfolio_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_ex_core_order_manager_py
    D_REPORTING["报告<br/>报告，负责投资报告、风险报告和合规报告的生成与分<br/>发<br/>Reporting<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_REPORTING -->|导入依赖 / import_depends| src_zephyr_ex_core_position_tracker_tracker_py
    D_REPORTING -->|测试依赖 / test_depends| src_zephyr_ex_core_position_tracker_tracker_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_ex_core_order_manager_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_ex_core_execution_engine_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_ex_core_adapters_init_py,src_zephyr_ex_core_adapters_miniqmt_broker_py,src_zephyr_ex_core_aggregate_root_manager_py,src_zephyr_ex_core_audit_journal_init_py,src_zephyr_ex_core_audit_journal_auditor_py,src_zephyr_ex_core_execution_engine_py,src_zephyr_ex_core_fill_handler_py,src_zephyr_ex_core_multi_contract_adapter_py,src_zephyr_ex_core_order_execution_saga_py,src_zephyr_ex_core_order_manager_py,src_zephyr_ex_core_position_reconciler_py,src_zephyr_ex_core_position_tracker_init_py,src_zephyr_ex_core_position_tracker_tracker_py,src_zephyr_ex_core_repository_interface_py,src_zephyr_ex_core_signal_providers_py,src_zephyr_ex_core_trading_session_py,src_zephyr_governance_escalation_order_state_escalator_py,tests_ex_core_test_position_reconciler_py production
    class src_zephyr_ex_core_auction_deviation_executor_py,src_zephyr_ex_core_batch_executor_py,src_zephyr_ex_core_batch_take_profit_executor_py,src_zephyr_ex_core_blueprint_implementer_py,src_zephyr_ex_core_conditional_order_manager_py,src_zephyr_ex_core_deployment_consistency_manager_py,src_zephyr_ex_core_execution_mcp_server_py,src_zephyr_ex_core_execution_risk_gate_py,src_zephyr_ex_core_execution_tca_py,src_zephyr_ex_core_factory_py,src_zephyr_ex_core_fill_processor_py,src_zephyr_ex_core_live_simulation_switcher_py,src_zephyr_ex_core_microstructure_modeler_py,src_zephyr_ex_core_miniqmt_channel_manager_py,src_zephyr_ex_core_order_splitter_py,src_zephyr_ex_core_performance_monitor_py,src_zephyr_ex_core_pre_execution_checker_py,src_zephyr_ex_core_redis_idempotency,src_zephyr_ex_core_rl_optimal_executor_py,src_zephyr_ex_core_sell_priority_scheduler_py,src_zephyr_ex_core_services_live_portfolio_py,src_zephyr_ex_core_stop_loss_take_profit_executor_py,src_zephyr_ex_core_value_objects_py design
    class D_BACKTEST,D_TRADING,D_PF_CORE,D_GOVERNANCE,D_RISK,D_EX_SOR,D_REPORTING external_prod
    class D_SELL_DECISION external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 18 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_ex_core_adapters_init_py["ex_core/adapters 包入口<br/>adapters 包入口，整合接口适配相关模块<br/>文件: adapters/__init__.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_aggregate_root_manager_py["Aggregate根入口管理器<br/>D_EX_CORE — Aggregate Root Manager<br/>(执行域聚合根管理器)<br/>文件: ex_core/aggregate_root_manager.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_audit_journal_init_py["Execution Audit Journal 包<br/>D_EXECUTION_CORE — Execution Audit Journal 包<br/>Init<br/>文件: audit_journal/__init__.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_execution_engine_py["执行引擎<br/>本模块内 ``ExecutionEngineRunRecord``<br/>为引擎内部聚合快照，非 CTR-P1-007；<br/>D_EXECUTION_CORE — Execution Engine<br/>文件: ex_core/execution_engine.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_multi_contract_adapter_py["多契约适配器<br/>D_EX_CORE — Multi-Contract Adapter<br/>(多契约生产适配器)<br/>Multi Contract Adapter<br/>文件: ex_core/multi_contract_adapter.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_order_execution_saga_py["下单执行 Saga 编排器<br/>Order Execution Saga — 下单执行 Saga 编排器<br/>(MOD-EX-057 / D-EX-CORE-57)<br/>文件: ex_core/order_execution_saga.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_signal_providers_py["信号提供器<br/>D_EXECUTION_CORE — 信号源 / 价格源 callable 工厂<br/>signal_providers<br/>文件: ex_core/signal_providers.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_trading_session_py["交易会话<br/>D_EXECUTION_CORE — TradingSession<br/>盘中实时调仓编排器<br/>trading_session<br/>文件: ex_core/trading_session.py<br/>(生产态 / production)"]
    src_zephyr_governance_escalation_order_state_escalator_py["订单状态escalator<br/>Order State Escalator — v0.10.0<br/>订单状态机升级器。<br/>order_state_escalator<br/>文件: escalation/order_state_escalator.py<br/>(生产态 / production)"]
    tests_ex_core_test_position_reconciler_py["D-EX-CORE-56 盘中持仓对账器<br/>PositionReconciler 单元测试 — D-EX-CORE-56<br/>盘中持仓对账器。<br/>Test Position Reconciler<br/>文件: ex_core/test_position_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_init_py ~~~ src_zephyr_ex_core_aggregate_root_manager_py
    src_zephyr_ex_core_aggregate_root_manager_py ~~~ src_zephyr_ex_core_audit_journal_init_py
    src_zephyr_ex_core_audit_journal_init_py ~~~ src_zephyr_ex_core_execution_engine_py
    src_zephyr_ex_core_execution_engine_py ~~~ src_zephyr_ex_core_multi_contract_adapter_py
    src_zephyr_ex_core_multi_contract_adapter_py ~~~ src_zephyr_ex_core_order_execution_saga_py
    src_zephyr_ex_core_order_execution_saga_py ~~~ src_zephyr_ex_core_signal_providers_py
    src_zephyr_ex_core_signal_providers_py ~~~ src_zephyr_ex_core_trading_session_py
    src_zephyr_ex_core_trading_session_py ~~~ src_zephyr_governance_escalation_order_state_escalator_py
    src_zephyr_governance_escalation_order_state_escalator_py ~~~ tests_ex_core_test_position_reconciler_py
    src_zephyr_ex_core_adapters_miniqmt_broker_py["miniqmt券商<br/>MiniQMT 实盘券商适配器（对接<br/>xttrader，A股实盘交易）<br/>miniqmt_broker<br/>文件: adapters/miniqmt_broker.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_audit_journal_auditor_py["执行审计记录器<br/>Execution Audit Logger — 执行审计记录器<br/>(MOD-EX-003 / D-EX-CORE-15)<br/>Auditor<br/>文件: audit_journal/auditor.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_fill_handler_py["部分成交处理器<br/>是成交回报的账房先生——每次券商回报一笔成交Fill它<br/>就累加到对应订单上更新已成交数量重新计算加权均价<br/>累计佣金判断订单是否已全部成交一笔大单分3次成交<br/>它就记3笔最后算总账任何时刻都能回答这单成交了多<br/>少还剩多少均价多少<br/>文件: ex_core/fill_handler.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_position_reconciler_py["盘中持仓对账器<br/>D_EXECUTION_CORE — 盘中持仓对账器 (Position<br/>Reconciler)<br/>文件: ex_core/position_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_repository_interface_py["Repository接口<br/>D_EX_CORE — Repository Interface<br/>(执行域仓储接口)<br/>文件: ex_core/repository_interface.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_miniqmt_broker_py ~~~ src_zephyr_ex_core_audit_journal_auditor_py
    src_zephyr_ex_core_audit_journal_auditor_py ~~~ src_zephyr_ex_core_fill_handler_py
    src_zephyr_ex_core_fill_handler_py ~~~ src_zephyr_ex_core_position_reconciler_py
    src_zephyr_ex_core_position_reconciler_py ~~~ src_zephyr_ex_core_repository_interface_py
    src_zephyr_ex_core_order_manager_py["订单管理器<br/>管理订单全生命周期：创建->风控校验->路由->状态跟<br/>踪<br/>D_EXECUTION_CORE — Order Manager<br/>文件: ex_core/order_manager.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_position_tracker_init_py["Position Tracker 包<br/>D_EXECUTION_CORE — Position Tracker 包<br/>Init<br/>文件: position_tracker/__init__.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_order_manager_py ~~~ src_zephyr_ex_core_position_tracker_init_py
    src_zephyr_ex_core_position_tracker_tracker_py["跟踪器<br/>D_EXECUTION_CORE — Position Tracker (持仓跟踪器)<br/>文件: position_tracker/tracker.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_aggregate_root_manager_py -->|导入依赖 / import_depends| src_zephyr_ex_core_fill_handler_py
    src_zephyr_ex_core_aggregate_root_manager_py -->|导入依赖 / import_depends| src_zephyr_ex_core_repository_interface_py
    src_zephyr_ex_core_aggregate_root_manager_py -->|导入依赖 / import_depends| src_zephyr_ex_core_position_tracker_tracker_py
    src_zephyr_ex_core_execution_engine_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_fill_handler_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_order_execution_saga_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_order_execution_saga_py -->|导入依赖 / import_depends| src_zephyr_ex_core_audit_journal_auditor_py
    src_zephyr_ex_core_order_execution_saga_py -->|导入依赖 / import_depends| src_zephyr_ex_core_position_tracker_tracker_py
    src_zephyr_ex_core_position_reconciler_py -->|data / data| src_zephyr_ex_core_position_tracker_init_py
    src_zephyr_ex_core_repository_interface_py -->|runtime / runtime| src_zephyr_ex_core_position_tracker_init_py
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_adapters_init_py -->|导入依赖 / import_depends| src_zephyr_ex_core_adapters_miniqmt_broker_py
    src_zephyr_ex_core_audit_journal_init_py -->|导入依赖 / import_depends| src_zephyr_ex_core_audit_journal_auditor_py
    src_zephyr_ex_core_position_tracker_init_py -->|导入依赖 / import_depends| src_zephyr_ex_core_position_tracker_tracker_py
    tests_ex_core_test_position_reconciler_py -->|测试依赖 / test_depends| src_zephyr_ex_core_position_reconciler_py
    tests_ex_core_test_position_reconciler_py -->|测试依赖 / test_depends| src_zephyr_ex_core_position_tracker_tracker_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_ex_core_adapters_init_py,src_zephyr_ex_core_adapters_miniqmt_broker_py,src_zephyr_ex_core_aggregate_root_manager_py,src_zephyr_ex_core_audit_journal_init_py,src_zephyr_ex_core_audit_journal_auditor_py,src_zephyr_ex_core_execution_engine_py,src_zephyr_ex_core_fill_handler_py,src_zephyr_ex_core_multi_contract_adapter_py,src_zephyr_ex_core_order_execution_saga_py,src_zephyr_ex_core_order_manager_py,src_zephyr_ex_core_position_reconciler_py,src_zephyr_ex_core_position_tracker_init_py,src_zephyr_ex_core_position_tracker_tracker_py,src_zephyr_ex_core_repository_interface_py,src_zephyr_ex_core_signal_providers_py,src_zephyr_ex_core_trading_session_py,src_zephyr_governance_escalation_order_state_escalator_py,tests_ex_core_test_position_reconciler_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 23 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_ex_core_auction_deviation_executor_py["拍卖偏差执行器<br/>执行核心的执行器，执行具体操作（auction<br/>deviation executor）<br/>⛔ 门禁:实盘交易环境+集合竞价数据源+miniQMT实盘AP<br/>I(D-EX-CORE-32)<br/>auction_deviation_executor<br/>文件: ex_core/auction_deviation_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_batch_executor_py["批次执行器<br/>执行核心的执行器，执行具体操作（batch executor）<br/>⛔ 门禁:实盘交易环境+A股Tick数据源+miniQMT实盘API<br/>(D-EX-CORE-30)<br/>batch_executor<br/>文件: ex_core/batch_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_batch_take_profit_executor_py["批次止盈利润执行器<br/>执行核心的执行器，执行具体操作（batch take<br/>profit executor）<br/>⛔ 门禁:实盘交易环境+A股Tick数据源+miniQMT实盘API<br/>(D-EX-CORE-31)<br/>batch_take_profit_executor<br/>文件: ex_core/batch_take_profit_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_blueprint_implementer_py["蓝图Implementer<br/>ex core包的blueprint_implementer模块<br/>⛔ 门禁:依赖模块(OMS+引擎+路由+报告)全部就绪<br/>(D-EX-CORE-37)<br/>Blueprint Implementer<br/>文件: ex_core/blueprint_implementer.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_conditional_order_manager_py["conditional订单管理器<br/>ex_core的管理器，统一管理一类资源的生命周期<br/>⛔ 门禁:EX-SOR算法路由就绪(D-EX-CORE-42)<br/>conditional_order_manager<br/>文件: ex_core/conditional_order_manager.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_deployment_consistency_manager_py["部署一致性管理器<br/>ex core包的deployment_consistency_manager模块<br/>⛔ 门禁:CI/CD灰度发布基础设施✅已就绪(MOD-CD-001<br/>shadow_canary_deploy,2026-08-03);实盘环境⏳待Owne<br/>r决策开通实盘账户+选定券商通道(D-EX-CORE-21)<br/>Deployment Consistency Manager<br/>文件: ex_core/deployment_consistency_manager.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_mcp_server_py["执行MCP服务端<br/>ex_core的服务端，接收并处理请求<br/>⛔ 门禁:MCP协议安全生态未成熟;开通需OAuth+RBAC+审<br/>计+沙箱+AI置信度>=95%稳定6月+渗透测试<br/>(D-EX-CORE-59)<br/>execution_mcp_server<br/>文件: ex_core/execution_mcp_server.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_risk_gate_py["执行风险门禁<br/>ex core包的execution_risk_gate模块<br/>⛔ 门禁:D-RISK域L04-limits就绪+风控规则引擎可调用<br/>(D-EX-CORE-07)<br/>Execution Risk Gate<br/>文件: ex_core/execution_risk_gate.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_tca_py["执行交易成本分析<br/>ex core包的execution_tca模块<br/>⛔ 门禁:历史执行数据>=30天+滑点模型参数可获取<br/>(D-EX-CORE-12)<br/>Execution Tca<br/>文件: ex_core/execution_tca.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_factory_py["工厂<br/>ex core包的factory模块<br/>文件: ex_core/factory.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_fill_processor_py["成交处理器<br/>执行核心的处理器，处理加工数据<br/>⛔ 门禁:Broker<br/>Adapter回报回调稳定+佣金费率表数据源就绪<br/>(D-EX-CORE-08)<br/>fill_processor<br/>文件: ex_core/fill_processor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_live_simulation_switcher_py["实盘仿真切换器<br/>支撑交易核心流程（live simulation switcher）<br/>⛔ 门禁:实盘券商连接(OKX/XTP/CTP)就绪<br/>(D-EX-CORE-35)<br/>live_simulation_switcher<br/>文件: ex_core/live_simulation_switcher.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_microstructure_modeler_py["微观结构建模器<br/>ex core包的microstructure_modeler模块<br/>⛔ 门禁:订单簿Level-2数据可获取+VPIN计算引擎就绪+<br/>LOB快照频率>=1秒(D-EX-CORE-61)<br/>Microstructure Modeler<br/>文件: ex_core/microstructure_modeler.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_miniqmt_channel_manager_py["MiniqmtChannel管理器<br/>ex core包的miniqmt_channel_manager模块<br/>Miniqmt Channel Manager<br/>文件: ex_core/miniqmt_channel_manager.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_performance_monitor_py["性能监控器<br/>ex core包的performance_monitor模块<br/>⛔ 门禁:生产环境APM基础设施(D-EX-CORE-36)<br/>Performance Monitor<br/>文件: ex_core/performance_monitor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_pre_execution_checker_py["Pre执行检查器<br/>ex core包的pre_execution_checker模块<br/>⛔ 门禁:D-RISK风控参数就绪+市场状态实时数据源<br/>(D-EX-CORE-24)<br/>Pre Execution Checker<br/>文件: ex_core/pre_execution_checker.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_redis_idempotency["redis幂等性<br/>执行核心的子目录，归集相关子模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: redis_idempotency/<br/>(设计态 / design)"]
    src_zephyr_ex_core_sell_priority_scheduler_py["卖出优先级调度器<br/>卖priority调度器，ex_core的调度器，按时间或优先<br/>级安排任务执行。<br/>⛔ 门禁:实盘交易环境+miniQMT实盘API(D-EX-CORE-33)<br/>sell_priority_scheduler<br/>文件: ex_core/sell_priority_scheduler.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_services_live_portfolio_py["实时组合<br/>支撑交易核心流程（live portfolio）<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>live_portfolio<br/>文件: services/live_portfolio.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_stop_loss_take_profit_executor_py["停止亏损止盈利润执行器<br/>执行核心的执行器，执行具体操作（stop loss take<br/>profit executor）<br/>⛔ 门禁:实盘交易环境+A股Tick数据源+miniQMT实盘API<br/>(D-EX-CORE-29)<br/>stop_loss_take_profit_executor<br/>文件: ex_core/stop_loss_take_profit_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_value_objects_py["值对象<br/>ex core包的value_objects模块<br/>Value Objects<br/>文件: ex_core/value_objects.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_auction_deviation_executor_py ~~~ src_zephyr_ex_core_batch_executor_py
    src_zephyr_ex_core_batch_executor_py ~~~ src_zephyr_ex_core_batch_take_profit_executor_py
    src_zephyr_ex_core_batch_take_profit_executor_py ~~~ src_zephyr_ex_core_blueprint_implementer_py
    src_zephyr_ex_core_blueprint_implementer_py ~~~ src_zephyr_ex_core_conditional_order_manager_py
    src_zephyr_ex_core_conditional_order_manager_py ~~~ src_zephyr_ex_core_deployment_consistency_manager_py
    src_zephyr_ex_core_deployment_consistency_manager_py ~~~ src_zephyr_ex_core_execution_mcp_server_py
    src_zephyr_ex_core_execution_mcp_server_py ~~~ src_zephyr_ex_core_execution_risk_gate_py
    src_zephyr_ex_core_execution_risk_gate_py ~~~ src_zephyr_ex_core_execution_tca_py
    src_zephyr_ex_core_execution_tca_py ~~~ src_zephyr_ex_core_factory_py
    src_zephyr_ex_core_factory_py ~~~ src_zephyr_ex_core_fill_processor_py
    src_zephyr_ex_core_fill_processor_py ~~~ src_zephyr_ex_core_live_simulation_switcher_py
    src_zephyr_ex_core_live_simulation_switcher_py ~~~ src_zephyr_ex_core_microstructure_modeler_py
    src_zephyr_ex_core_microstructure_modeler_py ~~~ src_zephyr_ex_core_miniqmt_channel_manager_py
    src_zephyr_ex_core_miniqmt_channel_manager_py ~~~ src_zephyr_ex_core_performance_monitor_py
    src_zephyr_ex_core_performance_monitor_py ~~~ src_zephyr_ex_core_pre_execution_checker_py
    src_zephyr_ex_core_pre_execution_checker_py ~~~ src_zephyr_ex_core_redis_idempotency
    src_zephyr_ex_core_redis_idempotency ~~~ src_zephyr_ex_core_sell_priority_scheduler_py
    src_zephyr_ex_core_sell_priority_scheduler_py ~~~ src_zephyr_ex_core_services_live_portfolio_py
    src_zephyr_ex_core_services_live_portfolio_py ~~~ src_zephyr_ex_core_stop_loss_take_profit_executor_py
    src_zephyr_ex_core_stop_loss_take_profit_executor_py ~~~ src_zephyr_ex_core_value_objects_py
    src_zephyr_ex_core_rl_optimal_executor_py["Rl最优执行器<br/>ex core包的rl_optimal_executor模块<br/>⛔ 门禁:RL训练基础设施+历史执行数据>=90天+Almgren<br/>-Chriss基线可运行+RL偏差阈值可配置(D-EX-CORE-60)<br/>Rl Optimal Executor<br/>文件: ex_core/rl_optimal_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_order_splitter_py["订单拆分器<br/>支撑交易核心流程（order splitter）<br/>⛔ 门禁:TCA<br/>(D-EX-CORE-12)就绪+订单簿深度数据可获取<br/>(D-EX-CORE-14)<br/>order_splitter<br/>文件: ex_core/order_splitter.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_rl_optimal_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_splitter_py
    src_zephyr_ex_core_microstructure_modeler_py -.->|data / data| src_zephyr_ex_core_order_splitter_py
    src_zephyr_ex_core_microstructure_modeler_py -.->|data / data| src_zephyr_ex_core_rl_optimal_executor_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_ex_core_auction_deviation_executor_py,src_zephyr_ex_core_batch_executor_py,src_zephyr_ex_core_batch_take_profit_executor_py,src_zephyr_ex_core_blueprint_implementer_py,src_zephyr_ex_core_conditional_order_manager_py,src_zephyr_ex_core_deployment_consistency_manager_py,src_zephyr_ex_core_execution_mcp_server_py,src_zephyr_ex_core_execution_risk_gate_py,src_zephyr_ex_core_execution_tca_py,src_zephyr_ex_core_factory_py,src_zephyr_ex_core_fill_processor_py,src_zephyr_ex_core_live_simulation_switcher_py,src_zephyr_ex_core_microstructure_modeler_py,src_zephyr_ex_core_miniqmt_channel_manager_py,src_zephyr_ex_core_order_splitter_py,src_zephyr_ex_core_performance_monitor_py,src_zephyr_ex_core_pre_execution_checker_py,src_zephyr_ex_core_redis_idempotency,src_zephyr_ex_core_rl_optimal_executor_py,src_zephyr_ex_core_sell_priority_scheduler_py,src_zephyr_ex_core_services_live_portfolio_py,src_zephyr_ex_core_stop_loss_take_profit_executor_py,src_zephyr_ex_core_value_objects_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | miniqmt券商 / miniqmt_broker (adapters/miniqmt_broker.py) | → | D_BACKTEST 回测: 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 导入依赖 / import_depends |
| 2 | 实时组合 / live_portfolio (services/live_portfolio.py) | → | D_BACKTEST 回测: 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 导入依赖 / import_depends |
| 3 | 实时组合 / live_portfolio (services/live_portfolio.py) | → | D_BACKTEST 回测: 回测持仓管理模块 / portfolio (core/portfolio.py) | 导入依赖 / import_depends |
| 4 | 信号提供器 / signal_providers (ex_core/signal_providers.py) | → | D_FACTOR 因子: D-FACTOR-ANA-10 多因子合成——将多个因子值合成为综合信号... | 导入依赖 / import_depends |
| 5 | 信号提供器 / signal_providers (ex_core/signal_providers.py) | → | D_FACTOR 因子: D-FACTOR-03 因子评估回测运行器——端到端因子评估。 / back... | 导入依赖 / import_depends |
| 6 | 信号提供器 / signal_providers (ex_core/signal_providers.py) | → | D_FACTOR 因子: 因子基类 / ZephyrAlpha — D_FACTOR Alpha Factor Layer (fa... | 导入依赖 / import_depends |
| 7 | 包入口 / __init__ (adapters/__init__.py) | → | D_GOVERNANCE 生命周期管理: 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | 导入依赖 / import_depends |
| 8 | 包入口 / __init__ (adapters/__init__.py) | → | D_GOVERNANCE 生命周期管理: 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | 导入依赖 / import_depends |
| 9 | 执行引擎 / D_EXECUTION_CORE — Execution Engine (ex_core/... | → | D_GOVERNANCE 生命周期管理: 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | 导入依赖 / import_depends |
| 10 | 下单执行 Saga 编排器 / Order Execution Saga (ex_core/orde... | → | D_GOVERNANCE 生命周期管理: 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | 导入依赖 / import_depends |
| 11 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_GOVERNANCE 生命周期管理: 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | contract / contract |
| 12 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_GOVERNANCE 生命周期管理: 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | 导入依赖 / import_depends |
| 13 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_GOVERNANCE 生命周期管理: 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | 导入依赖 / import_depends |
| 14 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_GOVERNANCE 生命周期管理: 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | contract / contract |
| 15 | Aggregate根入口管理器 / Aggregate Root Manager (ex_core/a... | → | D_INFRASTRUCTURE 跨层契约基础设施: Fill (contracts/fill.py) | 导入依赖 / import_depends |
| 16 | Aggregate根入口管理器 / Aggregate Root Manager (ex_core/a... | → | D_INFRASTRUCTURE 跨层契约基础设施: 订单 / Order (contracts/order.py) | 导入依赖 / import_depends |
| 17 | Aggregate根入口管理器 / Aggregate Root Manager (ex_core/a... | → | D_INFRASTRUCTURE 跨层契约基础设施: 持仓 / Position (contracts/position.py) | 导入依赖 / import_depends |
| 18 | 执行引擎 / D_EXECUTION_CORE — Execution Engine (ex_core/... | → | D_INFRASTRUCTURE 跨层契约基础设施: 订单 / Order (contracts/order.py) | 导入依赖 / import_depends |
| 19 | 执行引擎 / D_EXECUTION_CORE — Execution Engine (ex_core/... | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险Limits / Risk Limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 20 | 部分成交处理器 (ex_core/fill_handler.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: Fill (contracts/fill.py) | 导入依赖 / import_depends |
| 21 | 部分成交处理器 (ex_core/fill_handler.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 订单 / Order (contracts/order.py) | 导入依赖 / import_depends |
| 22 | 下单执行 Saga 编排器 / Order Execution Saga (ex_core/orde... | → | D_INFRASTRUCTURE 跨层契约基础设施: Fill (contracts/fill.py) | 导入依赖 / import_depends |
| 23 | 下单执行 Saga 编排器 / Order Execution Saga (ex_core/orde... | → | D_INFRASTRUCTURE 跨层契约基础设施: 订单 / Order (contracts/order.py) | 导入依赖 / import_depends |
| 24 | 下单执行 Saga 编排器 / Order Execution Saga (ex_core/orde... | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险Limits / Risk Limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 25 | 订单管理器 / D_EXECUTION_CORE — Order Manager (ex_core/o... | → | D_INFRASTRUCTURE 跨层契约基础设施: Fill (contracts/fill.py) | 导入依赖 / import_depends |
| 26 | 订单管理器 / D_EXECUTION_CORE — Order Manager (ex_core/o... | → | D_INFRASTRUCTURE 跨层契约基础设施: 订单 / Order (contracts/order.py) | 导入依赖 / import_depends |
| 27 | 盘中持仓对账器 / Position Reconciler (ex_core/position_re... | → | D_INFRASTRUCTURE 跨层契约基础设施: 持仓 / Position (contracts/position.py) | 导入依赖 / import_depends |
| 28 | 跟踪器 / Tracker (position_tracker/tracker.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: Fill (contracts/fill.py) | 导入依赖 / import_depends |
| 29 | 跟踪器 / Tracker (position_tracker/tracker.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 持仓 / Position (contracts/position.py) | 导入依赖 / import_depends |
| 30 | Repository接口 / Repository Interface (ex_core/repository... | → | D_INFRASTRUCTURE 跨层契约基础设施: 订单 / Order (contracts/order.py) | 导入依赖 / import_depends |
| 31 | Repository接口 / Repository Interface (ex_core/repository... | → | D_INFRASTRUCTURE 跨层契约基础设施: 持仓 / Position (contracts/position.py) | 导入依赖 / import_depends |
| 32 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: Fill (contracts/fill.py) | 导入依赖 / import_depends |
| 33 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 订单 / Order (contracts/order.py) | 导入依赖 / import_depends |
| 34 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 持仓 / Position (contracts/position.py) | 导入依赖 / import_depends |
| 35 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险Limits / Risk Limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 36 | D-EX-CORE-56 盘中持仓对账器 / Test Position Reconciler (e... | → | D_INFRASTRUCTURE 跨层契约基础设施: Fill (contracts/fill.py) | 测试依赖 / test_depends |
| 37 | D-EX-CORE-56 盘中持仓对账器 / Test Position Reconciler (e... | → | D_INFRASTRUCTURE 跨层契约基础设施: 持仓 / Position (contracts/position.py) | 测试依赖 / test_depends |
| 38 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_PF_CORE 组合核心: StrategyRunner 策略运行器 / Strategy Runner (strategy_eng... | 导入依赖 / import_depends |
| 39 | 实盘仿真切换器 / live_simulation_switcher (ex_core/live_s... | → | D_RISK 风控: 风险验证器 / Risk Validator (risk/risk_validator.py) | runtime / runtime |
| 40 | 卖出优先级调度器 / sell_priority_scheduler (ex_core/sell_... | → | D_SELL_DECISION 卖出决策: 持仓Triage / Position Triage (core/position_triage.py) | runtime / runtime |
| 41 | 卖出优先级调度器 / sell_priority_scheduler (ex_core/sell_... | → | D_SELL_DECISION 卖出决策: 持仓Triage / Position Triage (core/position_triage.py) | runtime / runtime |
| 42 | 停止亏损止盈利润执行器 / stop_loss_take_profit_executor (... | → | D_SELL_DECISION 卖出决策: 持仓Triage / Position Triage (core/position_triage.py) | runtime / runtime |
| 43 | 停止亏损止盈利润执行器 / stop_loss_take_profit_executor (... | → | D_SELL_DECISION 卖出决策: 持仓Triage / Position Triage (core/position_triage.py) | runtime / runtime |
| 44 | miniqmt券商 / miniqmt_broker (adapters/miniqmt_broker.py) | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 45 | Aggregate根入口管理器 / Aggregate Root Manager (ex_core/a... | → | D_SHARED 共享服务: 交易枚举真源 / Order Enums (enums/order_enums.py) | 导入依赖 / import_depends |
| 46 | Aggregate根入口管理器 / Aggregate Root Manager (ex_core/a... | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |
| 47 | 执行审计记录器 / Auditor (audit_journal/auditor.py) | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |
| 48 | 部分成交处理器 (ex_core/fill_handler.py) | → | D_SHARED 共享服务: 交易枚举真源 / Order Enums (enums/order_enums.py) | 导入依赖 / import_depends |
| 49 | 部分成交处理器 (ex_core/fill_handler.py) | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |
| 50 | 多契约适配器 / Multi Contract Adapter (ex_core/multi_cont... | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |
| 51 | 下单执行 Saga 编排器 / Order Execution Saga (ex_core/orde... | → | D_SHARED 共享服务: 交易枚举真源 / Order Enums (enums/order_enums.py) | 导入依赖 / import_depends |
| 52 | 订单管理器 / D_EXECUTION_CORE — Order Manager (ex_core/o... | → | D_SHARED 共享服务: 交易枚举真源 / Order Enums (enums/order_enums.py) | 导入依赖 / import_depends |
| 53 | 跟踪器 / Tracker (position_tracker/tracker.py) | → | D_SHARED 共享服务: 交易枚举真源 / Order Enums (enums/order_enums.py) | 导入依赖 / import_depends |
| 54 | Repository接口 / Repository Interface (ex_core/repository... | → | D_SHARED 共享服务: 交易枚举真源 / Order Enums (enums/order_enums.py) | 导入依赖 / import_depends |
| 55 | Repository接口 / Repository Interface (ex_core/repository... | → | D_SHARED 共享服务: ZephyrAlpha 所有业务异常的根 / Errors (foundation/errors.py) | 导入依赖 / import_depends |
| 56 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_SHARED 共享服务: 交易枚举真源 / Order Enums (enums/order_enums.py) | 导入依赖 / import_depends |
| 57 | D-EX-CORE-56 盘中持仓对账器 / Test Position Reconciler (e... | → | D_SHARED 共享服务: 交易枚举真源 / Order Enums (enums/order_enums.py) | 测试依赖 / test_depends |
| 58 | 包入口 / __init__ (adapters/__init__.py) | → | D_TRADING 交易运营: 经纪商接口 / Broker Interface (trading_contracts/broker_i... | 导入依赖 / import_depends |
| 59 | miniqmt券商 / miniqmt_broker (adapters/miniqmt_broker.py) | → | D_TRADING 交易运营: 经纪商接口 / Broker Interface (trading_contracts/broker_i... | 导入依赖 / import_depends |
| 60 | miniqmt券商 / miniqmt_broker (adapters/miniqmt_broker.py) | → | D_TRADING 交易运营: Fill 真源在 zephyr.shared.contracts.fill / Fill (executio... | 导入依赖 / import_depends |
| 61 | miniqmt券商 / miniqmt_broker (adapters/miniqmt_broker.py) | → | D_TRADING 交易运营: Order 真源在 zephyr.shared.contracts.order / Order (execu... | 导入依赖 / import_depends |
| 62 | miniqmt券商 / miniqmt_broker (adapters/miniqmt_broker.py) | → | D_TRADING 交易运营: PositionSnapshot 真源在 zephyr.shared.contracts.position ... | 导入依赖 / import_depends |
| 63 | 下单执行 Saga 编排器 / Order Execution Saga (ex_core/orde... | → | D_TRADING 交易运营: 经纪商接口 / Broker Interface (trading_contracts/broker_i... | 导入依赖 / import_depends |
| 64 | 订单管理器 / D_EXECUTION_CORE — Order Manager (ex_core/o... | → | D_TRADING 交易运营: 经纪商接口 / Broker Interface (trading_contracts/broker_i... | 导入依赖 / import_depends |
| 65 | 实时组合 / live_portfolio (services/live_portfolio.py) | → | D_TRADING 交易运营: PositionSnapshot 真源在 zephyr.shared.contracts.position ... | 导入依赖 / import_depends |
| 66 | 实时组合 / live_portfolio (services/live_portfolio.py) | → | D_TRADING 交易运营: 风险Limits / Risk Limits (risk/risk_limits.py) | 导入依赖 / import_depends |
| 67 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_TRADING 交易运营: 经纪商接口 / Broker Interface (trading_contracts/broker_i... | 导入依赖 / import_depends |
| 68 | 交易会话 / trading_session (ex_core/trading_session.py) | → | D_TRADING 交易运营: 经纪商接口 / Broker Interface (trading_contracts/broker_i... | contract / contract |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_BACKTEST 回测: 事件driven引擎 / event_driven_engine (implementations/eve... | → | miniqmt券商 / miniqmt_broker (adapters/miniqmt_broker.py) | 导入依赖 / import_depends |
| 2 | D_EX_SOR 执行路由: 经纪人适配器管理器 / broker_adapter_manager (core/broker_... | → | 执行引擎 / D_EXECUTION_CORE — Execution Engine (ex_core/... | 导入依赖 / import_depends |
| 3 | D_GOVERNANCE 生命周期管理: 端到端管道测试 / Test E2e Pipeline (trading/test_e2e_pipe... | → | 执行引擎 / D_EXECUTION_CORE — Execution Engine (ex_core/... | 测试依赖 / test_depends |
| 4 | D_GOVERNANCE 生命周期管理: 端到端管道测试 / Test E2e Pipeline (trading/test_e2e_pipe... | → | 订单管理器 / D_EXECUTION_CORE — Order Manager (ex_core/o... | 测试依赖 / test_depends |
| 5 | D_GOVERNANCE 生命周期管理: 阶段EMain流测试 / Test Phase E Main Flow (trading/test_ph... | → | 订单管理器 / D_EXECUTION_CORE — Order Manager (ex_core/o... | 测试依赖 / test_depends |
| 6 | D_REPORTING 报告: RealtimePnl仪表盘 / Realtime Pnl Dashboard (reporting/rea... | → | 跟踪器 / Tracker (position_tracker/tracker.py) | 导入依赖 / import_depends |
| 7 | D_REPORTING 报告: MOD-RPT-004 Real-time P&L Dashboard 单元测试. / Test Real... | → | 跟踪器 / Tracker (position_tracker/tracker.py) | 测试依赖 / test_depends |
| 8 | D_SELL_DECISION 卖出决策: T交易协调器 / T Trade Coordinator (core/t_trade_coordinat... | → | 实时组合 / live_portfolio (services/live_portfolio.py) | 导入依赖 / import_depends |
| 9 | D_TRADING 交易运营: Pnl计算器 / Pnl Calculator (trading/pnl_calculator.py) | → | 部分成交处理器 (ex_core/fill_handler.py) | import / import |
| 10 | D_TRADING 交易运营: Settlement Reconciliation (trading/settlement_reconciliat... | → | 订单管理器 / D_EXECUTION_CORE — Order Manager (ex_core/o... | runtime / runtime |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 11 个外部域直接连接（出边 68 条 + 入边 10 条 = 78 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_SELL_DECISION["D_SELL_DECISION<br/>卖出决策"]
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_FACTOR["D_FACTOR<br/>因子"]
    D_RISK["D_RISK<br/>风控"]
    D_PF_CORE["D_PF_CORE<br/>组合核心"]
    D_REPORTING["D_REPORTING<br/>报告"]
    D_EX_SOR["D_EX_SOR<br/>执行路由"]
    D_EX_CORE -->|23条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRASTRUCTURE
    D_EX_CORE -->|14条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SHARED
    D_EX_CORE -->|11条 contract / contract, 导入依赖 / import_depends| D_TRADING
    D_EX_CORE -->|8条 contract / contract, 导入依赖 / import_depends| D_GOVERNANCE
    D_EX_CORE -->|4条 runtime / runtime| D_SELL_DECISION
    D_EX_CORE -->|3条 导入依赖 / import_depends| D_BACKTEST
    D_EX_CORE -->|3条 导入依赖 / import_depends| D_FACTOR
    D_EX_CORE -->|1条 runtime / runtime| D_RISK
    D_EX_CORE -->|1条 导入依赖 / import_depends| D_PF_CORE
    D_GOVERNANCE -->|3条 测试依赖 / test_depends| D_EX_CORE
    D_REPORTING -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_EX_CORE
    D_TRADING -->|2条 import / import, runtime / runtime| D_EX_CORE
    D_BACKTEST -->|1条 导入依赖 / import_depends| D_EX_CORE
    D_EX_SOR -->|1条 导入依赖 / import_depends| D_EX_CORE
    D_SELL_DECISION -->|1条 导入依赖 / import_depends| D_EX_CORE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
