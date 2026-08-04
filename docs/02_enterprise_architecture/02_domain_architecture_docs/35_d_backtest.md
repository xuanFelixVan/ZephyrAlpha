---
doc_type: architecture_view
title: D_BACKTEST 回测架构文档
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 35_d_backtest / 回测域 / Backtest

> **功能简介 / Overview**: 回测，负责历史数据回测、回测引擎和回测报告

> **文档作用 / Purpose**: 展示 回测（D_BACKTEST）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/35_d_backtest.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 35 | Number | 35 |
| 域ID | D_BACKTEST | Domain ID | D_BACKTEST |
| 域名称 | 回测 | Domain Name | Backtest |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 42 | Module Count | 42 |
| 域内依赖 | 58 | Internal Dependencies | 58 |
| 跨域入边 | 14 | Cross-domain Incoming | 14 |
| 跨域出边 | 20 | Cross-domain Outgoing | 20 |
| 设计态模块 | 1 | Design Modules | 1 |
| 生产态模块 | 41 | Production Modules | 41 |
| 容量 | 41/150 (正常) | Capacity | 41/150 (正常) |
| 描述 | 回测，负责历史数据回测、回测引擎和回测报告 | Description | 回测，负责历史数据回测、回测引擎和回测报告 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 42 个模块（生产态 41 + 设计态 1），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_backtest_io_result_repository_py["结果仓库<br/>result_repository · 回测产物持久化/检索模块<br/>（v1.3.0 新增，#ARCH-047）<br/>文件: io/result_repository.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_result_deployer_py["结果deployer<br/>回测的结果，封装操作结果的数据结构<br/>⛔ 受限：涉及实盘安全，需D-EX-CORE执行域就绪<br/>result_deployer<br/>文件: services/result_deployer.py<br/>(设计态 / design)"]
    tests_backtest_test_anomaly_diagnoser_py["backtest/test_anomaly_diagnoser<br/>MOD-BT-023 Anomaly Diagnoser 单元测试.<br/>文件: backtest/test_anomaly_diagnoser.py<br/>(生产态 / production)"]
    tests_backtest_test_cache_manager_py["backtest/test_cache_manager<br/>MOD-BT-020 Backtest Cache Manager 单元测试.<br/>文件: backtest/test_cache_manager.py<br/>(生产态 / production)"]
    tests_backtest_test_data_handler_pit_py["backtest/test_data_handler_pit<br/>BacktestDataHandler PIT 财务数据合并测试<br/>（#ARCH-CH-021 P0-5）。<br/>文件: backtest/test_data_handler_pit.py<br/>(生产态 / production)"]
    tests_backtest_test_data_quality_checker_py["backtest/test_data_quality_checker<br/>DataQualityChecker (MOD-BT-022) 测试套件。<br/>文件: backtest/test_data_quality_checker.py<br/>(生产态 / production)"]
    tests_backtest_test_decay_monitor_py["backtest/test_decay_monitor<br/>DecayMonitor (MOD-BT-018) 测试套件。<br/>文件: backtest/test_decay_monitor.py<br/>(生产态 / production)"]
    tests_backtest_test_nan_processor_py["backtest/test_nan_processor<br/>NaNProcessor (MOD-BT-026) 测试套件。<br/>文件: backtest/test_nan_processor.py<br/>(生产态 / production)"]
    tests_backtest_test_param_analyzer_py["backtest/test_param_analyzer<br/>MOD-BT-021 Parameter Analyzer 单元测试.<br/>文件: backtest/test_param_analyzer.py<br/>(生产态 / production)"]
    tests_backtest_test_report_generator_py["backtest/test_report_generator<br/>MOD-BT-019 Backtest Report Generator 单元测试.<br/>文件: backtest/test_report_generator.py<br/>(生产态 / production)"]
    tests_backtest_test_result_comparator_py["backtest/test_result_comparator<br/>MOD-BT-024 Result Comparator —<br/>回测结果比较器单元测试。<br/>文件: backtest/test_result_comparator.py<br/>(生产态 / production)"]
    tests_backtest_test_scheduler_py["backtest/test_scheduler<br/>D-BACKTEST BT-17 回测自动调度器测试——使用 Mock<br/>引擎（无 IO 依赖）。<br/>文件: backtest/test_scheduler.py<br/>(生产态 / production)"]
    tests_factor_test_backtest_factor_e2e_py["factor/test_backtest_factor_e2e<br/>T7 跨域端到端集成测试——D-FACTOR → D-BACKTEST<br/>数据流验证。<br/>文件: factor/test_backtest_factor_e2e.py<br/>(生产态 / production)"]
    tests_factor_test_evaluation_backtest_py["factor/test_evaluation_backtest<br/>D-FACTOR-03<br/>因子评估回测运行器测试——backtest.py。<br/>文件: factor/test_evaluation_backtest.py<br/>(生产态 / production)"]
    tests_test_backtest_decisiongraph_adapter_py["tests/test_backtest_decisiongraph_adapter<br/>test_backtest_decisiongraph_adapter —<br/>BacktestResult→decisiongraph 适配器单...<br/>文件: tests<br/>/test_backtest_decisiongraph_adapter.py<br/>(生产态 / production)"]
    tests_test_event_driven_engine_py["tests/test_event_driven_engine<br/>event_driven_engine 正式测试（原 scripts/tests/<br/>临时验证脚本转正）<br/>文件: tests/test_event_driven_engine.py<br/>(生产态 / production)"]
    tests_test_matching_engine_py["tests/test_matching_engine<br/>matching_engine + matching_logic + portfolio<br/>正式测试（原 scripts/tests/ 临时...<br/>文件: tests/test_matching_engine.py<br/>(生产态 / production)"]
    tests_test_tick_replay_data_handler_py["tests/test_tick_replay_data_handler<br/>tick_replay + data_handler 正式测试（原 scripts<br/>/tests/ 临时验证脚本转正）<br/>文件: tests/test_tick_replay_data_handler.py<br/>(生产态 / production)"]
    src_zephyr_backtest_io_result_repository_py ~~~ src_zephyr_backtest_services_result_deployer_py
    src_zephyr_backtest_services_result_deployer_py ~~~ tests_backtest_test_anomaly_diagnoser_py
    tests_backtest_test_anomaly_diagnoser_py ~~~ tests_backtest_test_cache_manager_py
    tests_backtest_test_cache_manager_py ~~~ tests_backtest_test_data_handler_pit_py
    tests_backtest_test_data_handler_pit_py ~~~ tests_backtest_test_data_quality_checker_py
    tests_backtest_test_data_quality_checker_py ~~~ tests_backtest_test_decay_monitor_py
    tests_backtest_test_decay_monitor_py ~~~ tests_backtest_test_nan_processor_py
    tests_backtest_test_nan_processor_py ~~~ tests_backtest_test_param_analyzer_py
    tests_backtest_test_param_analyzer_py ~~~ tests_backtest_test_report_generator_py
    tests_backtest_test_report_generator_py ~~~ tests_backtest_test_result_comparator_py
    tests_backtest_test_result_comparator_py ~~~ tests_backtest_test_scheduler_py
    tests_backtest_test_scheduler_py ~~~ tests_factor_test_backtest_factor_e2e_py
    tests_factor_test_backtest_factor_e2e_py ~~~ tests_factor_test_evaluation_backtest_py
    tests_factor_test_evaluation_backtest_py ~~~ tests_test_backtest_decisiongraph_adapter_py
    tests_test_backtest_decisiongraph_adapter_py ~~~ tests_test_event_driven_engine_py
    tests_test_event_driven_engine_py ~~~ tests_test_matching_engine_py
    tests_test_matching_engine_py ~~~ tests_test_tick_replay_data_handler_py
    src_zephyr_backtest_core_data_handler_py["数据处理器<br/>回测数据处理器模块（v1.1.0 扩展：多源化 +<br/>ClickHouse 实现 + Tick 源）<br/>data_handler<br/>文件: core/data_handler.py<br/>(生产态 / production)"]
    src_zephyr_backtest_implementations_event_driven_engine_py["事件driven引擎<br/>事件驱动回测引擎（v1.1.0 新增，Tick 级回测核心）<br/>event_driven_engine<br/>文件: implementations/event_driven_engine.py<br/>(生产态 / production)"]
    src_zephyr_backtest_io_backtest_result_sink_py["回测结果sink<br/>回测结果汇 · 回测结果数据落地模块（v1.3.0<br/>新增，#ARCH-047）<br/>backtest_result_sink<br/>文件: io/backtest_result_sink.py<br/>(生产态 / production)"]
    src_zephyr_backtest_io_decisiongraph_adapter_py["decisiongraph适配器<br/>将 BacktestResult（CTR-P1-016，15<br/>字段冻结契约）映射为 decisiongraph<br/>decisiongraph_adapter<br/>文件: io/decisiongraph_adapter.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_anomaly_diagnoser_py["回测异常诊断器<br/>给定回测结果,检查Sharpe是不是太高(可能过拟合)<br/>/胜率是不是太离谱(可能用了未来数据)<br/>/回撤是不是太深/交易次数够不够<br/>/回测时间够不够长等,发现问题就给出修复建议。纯阈<br/>值判定,不改输入。<br/>Anomaly Diagnoser<br/>文件: services/anomaly_diagnoser.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_decay_monitor_py["decay监控器<br/>decay监控，回测的监控器，持续监视某项指标，异常<br/>时上报。<br/>decay_monitor<br/>文件: services/decay_monitor.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_nan_processor_py["nan处理器<br/>服务的处理器，处理加工数据<br/>nan_processor<br/>文件: services/nan_processor.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_param_analyzer_py["参数优化结果分析器<br/>给定一组用不同参数跑出来的回测结果,找出哪组参数<br/>最好,每个参数对结果影响有多大<br/>(敏感度),样本内外差距是不是太大<br/>(过拟合),以及排名靠前的结果是不是稳定。纯统计分<br/>析,不改输入。<br/>Parameter Analyzer<br/>文件: services/param_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_report_generator_py["回测报告生成器<br/>给定回测结果数据,生成一份能直接打开看的HTML报告,<br/>里面有收益/Sharpe/回撤<br/>/胜率等指标表,可选画权益曲线和列交易明细。纯字符<br/>串模板渲染,不需要装额外库。<br/>Backtest Report Generator<br/>文件: services/report_generator.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_result_comparator_py["回测结果比较器<br/>给两组回测结果做差异对比——逐项比较年化收益、Shar<br/>pe、最大回撤等指标,算出候选比基线好多少差多少,再<br/>用统计检验判断差异是真显著还是碰巧,最后生成一张<br/>对比表方便人判断该不该换策略。<br/>Result Comparator<br/>文件: services/result_comparator.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_scheduler_py["D-BACKTEST BT-17<br/>回测自动调度器——批量+参数网格+队列管理+结<br/>- 参数网格展开：将 {param: (v1, v2, ...)}<br/>展开为所有组合<br/>scheduler<br/>文件: services/scheduler.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_data_handler_py ~~~ src_zephyr_backtest_implementations_event_driven_engine_py
    src_zephyr_backtest_implementations_event_driven_engine_py ~~~ src_zephyr_backtest_io_backtest_result_sink_py
    src_zephyr_backtest_io_backtest_result_sink_py ~~~ src_zephyr_backtest_io_decisiongraph_adapter_py
    src_zephyr_backtest_io_decisiongraph_adapter_py ~~~ src_zephyr_backtest_services_anomaly_diagnoser_py
    src_zephyr_backtest_services_anomaly_diagnoser_py ~~~ src_zephyr_backtest_services_decay_monitor_py
    src_zephyr_backtest_services_decay_monitor_py ~~~ src_zephyr_backtest_services_nan_processor_py
    src_zephyr_backtest_services_nan_processor_py ~~~ src_zephyr_backtest_services_param_analyzer_py
    src_zephyr_backtest_services_param_analyzer_py ~~~ src_zephyr_backtest_services_report_generator_py
    src_zephyr_backtest_services_report_generator_py ~~~ src_zephyr_backtest_services_result_comparator_py
    src_zephyr_backtest_services_result_comparator_py ~~~ src_zephyr_backtest_services_scheduler_py
    src_zephyr_backtest_core_pit_manager_py["pit管理器<br/>(Point-In-Time)铁律管理器模块<br/>pit_manager<br/>文件: core/pit_manager.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_tick_replay_py["逐笔replay<br/>Tick 回放引擎模块（v1.1.0 新增，秒级做T专用）<br/>tick_replay<br/>文件: core/tick_replay.py<br/>(生产态 / production)"]
    src_zephyr_backtest_implementations_vectorized_engine_py["vectorized引擎<br/>回测引擎具体实现。实现<br/>BacktestEngineBase，支持向量化回测。<br/>L_BACKTEST — Vectorized Backtest Engine<br/>文件: implementations/vectorized_engine.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_cache_manager_py["回测缓存管理器<br/>给定回测参数(策略ID+参数+日期范围),算出缓存键,把<br/>回测结果存进内存缓存。下次相同参数来查直接返回缓<br/>存结果不用重算,满了按LRU淘汰最久没用的。纯内存管<br/>理,不依赖数据库。<br/>Backtest Cache Manager<br/>文件: services/cache_manager.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_data_quality_checker_py["数据质量检查器<br/>回测的检查器，检查某项条件是否满足<br/>data_quality_checker<br/>文件: services/data_quality_checker.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_pit_manager_py ~~~ src_zephyr_backtest_core_tick_replay_py
    src_zephyr_backtest_core_tick_replay_py ~~~ src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_implementations_vectorized_engine_py ~~~ src_zephyr_backtest_services_cache_manager_py
    src_zephyr_backtest_services_cache_manager_py ~~~ src_zephyr_backtest_services_data_quality_checker_py
    src_zephyr_backtest_core_decision_gate_py["3阶段决策门控模块(IS->WFA->OOS)<br/>- IS(In-Sample)阶段:样本内Sharpe准入<br/>(>0.5)+参数稳定性门控(避悬崖型参数)<br/>decision_gate<br/>文件: core/decision_gate.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_engine_base_py["引擎基类<br/>回测引擎层。负责离线研究、回测、策略孵化与知识沉<br/>淀。<br/>L_BACKTEST — Backtest Engine Layer<br/>文件: core/engine_base.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_matching_engine_py["matching引擎<br/>回测撮合引擎模块（v1.1.0 重构：委托<br/>MatchingLogic 保证回测=实盘一致性）<br/>matching_engine<br/>文件: core/matching_engine.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_metrics_py["回测绩效指标计算模块<br/>- 计算回测绩效指标:总收益率/年化收益率/Sharpe<br/>/Sortino/最大回撤/胜率<br/>metrics<br/>文件: core/metrics.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_walk_forward_py["walk前<br/>Walk-Forward分析与多重比较偏差校正模块<br/>walk_forward<br/>文件: core/walk_forward.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_decision_gate_py ~~~ src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_core_engine_base_py ~~~ src_zephyr_backtest_core_matching_engine_py
    src_zephyr_backtest_core_matching_engine_py ~~~ src_zephyr_backtest_core_metrics_py
    src_zephyr_backtest_core_metrics_py ~~~ src_zephyr_backtest_core_walk_forward_py
    src_zephyr_backtest_core_matching_logic_py["共享撮合逻辑模块（回测=实盘一致性核心）<br/>- 提供纯函数式撮合逻辑，被 D_BACKTEST<br/>matching_engine(回测) 和<br/>matching_logic<br/>文件: core/matching_logic.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_overfitting_detector_py["过拟合检测模块(三维度 + 三层)<br/>- 过拟合检测三维度(D-FACTOR-03):<br/>overfitting_detector<br/>文件: core/overfitting_detector.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_portfolio_py["回测持仓管理模块<br/>- 持仓管理(买入/卖出/更新市值)<br/>portfolio<br/>文件: core/portfolio.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_matching_logic_py ~~~ src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_core_overfitting_detector_py ~~~ src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_core_matching_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_logic_py
    src_zephyr_backtest_core_matching_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_core_data_handler_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_pit_manager_py
    src_zephyr_backtest_core_decision_gate_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_core_tick_replay_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_logic_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_engine_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_decision_gate_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_metrics_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_walk_forward_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_io_decisiongraph_adapter_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_engine_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_decision_gate_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_metrics_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_tick_replay_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_walk_forward_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_io_backtest_result_sink_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_io_result_repository_py -->|导入依赖 / import_depends| src_zephyr_backtest_io_backtest_result_sink_py
    src_zephyr_backtest_services_anomaly_diagnoser_py -->|import / import| src_zephyr_backtest_services_data_quality_checker_py
    src_zephyr_backtest_services_anomaly_diagnoser_py -->|导入依赖 / import_depends| src_zephyr_backtest_services_data_quality_checker_py
    src_zephyr_backtest_services_scheduler_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_services_scheduler_py -->|导入依赖 / import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_services_param_analyzer_py -->|导入依赖 / import_depends| src_zephyr_backtest_services_cache_manager_py
    src_zephyr_backtest_services_param_analyzer_py -->|import / import| src_zephyr_backtest_services_cache_manager_py
    tests_test_backtest_decisiongraph_adapter_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_engine_base_py
    tests_test_backtest_decisiongraph_adapter_py -->|测试依赖 / test_depends| src_zephyr_backtest_io_decisiongraph_adapter_py
    tests_test_event_driven_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_engine_base_py
    tests_test_event_driven_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_tick_replay_py
    tests_test_event_driven_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    tests_test_event_driven_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_implementations_event_driven_engine_py
    tests_test_matching_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_matching_engine_py
    tests_test_matching_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_matching_logic_py
    tests_test_matching_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_portfolio_py
    tests_test_tick_replay_data_handler_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_data_handler_py
    tests_test_tick_replay_data_handler_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_matching_logic_py
    tests_test_tick_replay_data_handler_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_tick_replay_py
    tests_backtest_test_anomaly_diagnoser_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_anomaly_diagnoser_py
    tests_backtest_test_anomaly_diagnoser_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_data_quality_checker_py
    tests_backtest_test_decay_monitor_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_decay_monitor_py
    tests_backtest_test_param_analyzer_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_cache_manager_py
    tests_backtest_test_param_analyzer_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_param_analyzer_py
    tests_backtest_test_cache_manager_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_cache_manager_py
    tests_backtest_test_nan_processor_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_nan_processor_py
    tests_backtest_test_data_handler_pit_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_data_handler_py
    tests_backtest_test_data_quality_checker_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_data_quality_checker_py
    tests_backtest_test_report_generator_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_report_generator_py
    tests_backtest_test_result_comparator_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_result_comparator_py
    tests_backtest_test_scheduler_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_engine_base_py
    tests_backtest_test_scheduler_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_scheduler_py
    tests_factor_test_backtest_factor_e2e_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_engine_base_py
    tests_factor_test_backtest_factor_e2e_py -->|测试依赖 / test_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    tests_factor_test_backtest_factor_e2e_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_scheduler_py
    D_EX_CORE["执行核心<br/>执行核心，负责订单执行引擎、执行策略和执行管理<br/>Execution Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| D_EX_CORE
    D_FACTOR["因子<br/>因子，负责因子计算、因子库管理和因子评价<br/>Factor<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    tests_factor_test_backtest_factor_e2e_py -->|测试依赖 / test_depends| D_FACTOR
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_backtest_services_anomaly_diagnoser_py -->|导入依赖 / import_depends| D_SHARED
    D_DATA["数据接入层<br/>数据接入层，负责数据源接入、数据集成和数据标准化<br/>Data Access Layer<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_backtest_core_data_handler_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_backtest_core_engine_base_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_backtest_services_nan_processor_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_backtest_services_data_quality_checker_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME["运行时集成<br/>运行时集成，负责组件生命周期编排、启动钩子和运行<br/>时上下文管理<br/>Runtime Integration<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_backtest_core_data_handler_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_backtest_services_report_generator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_backtest_core_data_handler_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_backtest_services_param_analyzer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_backtest_services_decay_monitor_py -->|导入依赖 / import_depends| D_SHARED
    tests_factor_test_backtest_factor_e2e_py -->|测试依赖 / test_depends| D_FACTOR
    src_zephyr_backtest_io_result_repository_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_backtest_io_decisiongraph_adapter_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_logic_py
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_backtest_core_portfolio_py
    D_PF_CORE["组合核心<br/>组合核心，负责投资组合构建、持仓管理和组合优化<br/>Portfolio Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_PF_CORE -->|测试依赖 / test_depends| src_zephyr_backtest_core_matching_logic_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_logic_py
    D_PF_CORE -->|测试依赖 / test_depends| src_zephyr_backtest_core_matching_logic_py
    D_PF_CORE -->|测试依赖 / test_depends| src_zephyr_backtest_core_matching_logic_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_backtest_core_tick_replay_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_backtest_core_tick_replay_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_backtest_core_tick_replay_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_backtest_core_tick_replay_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_backtest_implementations_event_driven_engine_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_backtest_core_data_handler_py,src_zephyr_backtest_core_decision_gate_py,src_zephyr_backtest_core_engine_base_py,src_zephyr_backtest_core_matching_engine_py,src_zephyr_backtest_core_matching_logic_py,src_zephyr_backtest_core_metrics_py,src_zephyr_backtest_core_overfitting_detector_py,src_zephyr_backtest_core_pit_manager_py,src_zephyr_backtest_core_portfolio_py,src_zephyr_backtest_core_tick_replay_py,src_zephyr_backtest_core_walk_forward_py,src_zephyr_backtest_implementations_event_driven_engine_py,src_zephyr_backtest_implementations_vectorized_engine_py,src_zephyr_backtest_io_backtest_result_sink_py,src_zephyr_backtest_io_decisiongraph_adapter_py,src_zephyr_backtest_io_result_repository_py,src_zephyr_backtest_services_anomaly_diagnoser_py,src_zephyr_backtest_services_cache_manager_py,src_zephyr_backtest_services_data_quality_checker_py,src_zephyr_backtest_services_decay_monitor_py,src_zephyr_backtest_services_nan_processor_py,src_zephyr_backtest_services_param_analyzer_py,src_zephyr_backtest_services_report_generator_py,src_zephyr_backtest_services_result_comparator_py,src_zephyr_backtest_services_scheduler_py,tests_backtest_test_anomaly_diagnoser_py,tests_backtest_test_cache_manager_py,tests_backtest_test_data_handler_pit_py,tests_backtest_test_data_quality_checker_py,tests_backtest_test_decay_monitor_py,tests_backtest_test_nan_processor_py,tests_backtest_test_param_analyzer_py,tests_backtest_test_report_generator_py,tests_backtest_test_result_comparator_py,tests_backtest_test_scheduler_py,tests_factor_test_backtest_factor_e2e_py,tests_factor_test_evaluation_backtest_py,tests_test_backtest_decisiongraph_adapter_py,tests_test_event_driven_engine_py,tests_test_matching_engine_py,tests_test_tick_replay_data_handler_py production
    class src_zephyr_backtest_services_result_deployer_py design
    class D_EX_CORE,D_FACTOR,D_SHARED,D_DATA,D_INFRA_RUNTIME,D_GOVERNANCE,D_PF_CORE external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 41 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_backtest_io_result_repository_py["结果仓库<br/>result_repository · 回测产物持久化/检索模块<br/>（v1.3.0 新增，#ARCH-047）<br/>文件: io/result_repository.py<br/>(生产态 / production)"]
    tests_backtest_test_anomaly_diagnoser_py["backtest/test_anomaly_diagnoser<br/>MOD-BT-023 Anomaly Diagnoser 单元测试.<br/>文件: backtest/test_anomaly_diagnoser.py<br/>(生产态 / production)"]
    tests_backtest_test_cache_manager_py["backtest/test_cache_manager<br/>MOD-BT-020 Backtest Cache Manager 单元测试.<br/>文件: backtest/test_cache_manager.py<br/>(生产态 / production)"]
    tests_backtest_test_data_handler_pit_py["backtest/test_data_handler_pit<br/>BacktestDataHandler PIT 财务数据合并测试<br/>（#ARCH-CH-021 P0-5）。<br/>文件: backtest/test_data_handler_pit.py<br/>(生产态 / production)"]
    tests_backtest_test_data_quality_checker_py["backtest/test_data_quality_checker<br/>DataQualityChecker (MOD-BT-022) 测试套件。<br/>文件: backtest/test_data_quality_checker.py<br/>(生产态 / production)"]
    tests_backtest_test_decay_monitor_py["backtest/test_decay_monitor<br/>DecayMonitor (MOD-BT-018) 测试套件。<br/>文件: backtest/test_decay_monitor.py<br/>(生产态 / production)"]
    tests_backtest_test_nan_processor_py["backtest/test_nan_processor<br/>NaNProcessor (MOD-BT-026) 测试套件。<br/>文件: backtest/test_nan_processor.py<br/>(生产态 / production)"]
    tests_backtest_test_param_analyzer_py["backtest/test_param_analyzer<br/>MOD-BT-021 Parameter Analyzer 单元测试.<br/>文件: backtest/test_param_analyzer.py<br/>(生产态 / production)"]
    tests_backtest_test_report_generator_py["backtest/test_report_generator<br/>MOD-BT-019 Backtest Report Generator 单元测试.<br/>文件: backtest/test_report_generator.py<br/>(生产态 / production)"]
    tests_backtest_test_result_comparator_py["backtest/test_result_comparator<br/>MOD-BT-024 Result Comparator —<br/>回测结果比较器单元测试。<br/>文件: backtest/test_result_comparator.py<br/>(生产态 / production)"]
    tests_backtest_test_scheduler_py["backtest/test_scheduler<br/>D-BACKTEST BT-17 回测自动调度器测试——使用 Mock<br/>引擎（无 IO 依赖）。<br/>文件: backtest/test_scheduler.py<br/>(生产态 / production)"]
    tests_factor_test_backtest_factor_e2e_py["factor/test_backtest_factor_e2e<br/>T7 跨域端到端集成测试——D-FACTOR → D-BACKTEST<br/>数据流验证。<br/>文件: factor/test_backtest_factor_e2e.py<br/>(生产态 / production)"]
    tests_factor_test_evaluation_backtest_py["factor/test_evaluation_backtest<br/>D-FACTOR-03<br/>因子评估回测运行器测试——backtest.py。<br/>文件: factor/test_evaluation_backtest.py<br/>(生产态 / production)"]
    tests_test_backtest_decisiongraph_adapter_py["tests/test_backtest_decisiongraph_adapter<br/>test_backtest_decisiongraph_adapter —<br/>BacktestResult→decisiongraph 适配器单...<br/>文件: tests<br/>/test_backtest_decisiongraph_adapter.py<br/>(生产态 / production)"]
    tests_test_event_driven_engine_py["tests/test_event_driven_engine<br/>event_driven_engine 正式测试（原 scripts/tests/<br/>临时验证脚本转正）<br/>文件: tests/test_event_driven_engine.py<br/>(生产态 / production)"]
    tests_test_matching_engine_py["tests/test_matching_engine<br/>matching_engine + matching_logic + portfolio<br/>正式测试（原 scripts/tests/ 临时...<br/>文件: tests/test_matching_engine.py<br/>(生产态 / production)"]
    tests_test_tick_replay_data_handler_py["tests/test_tick_replay_data_handler<br/>tick_replay + data_handler 正式测试（原 scripts<br/>/tests/ 临时验证脚本转正）<br/>文件: tests/test_tick_replay_data_handler.py<br/>(生产态 / production)"]
    src_zephyr_backtest_io_result_repository_py ~~~ tests_backtest_test_anomaly_diagnoser_py
    tests_backtest_test_anomaly_diagnoser_py ~~~ tests_backtest_test_cache_manager_py
    tests_backtest_test_cache_manager_py ~~~ tests_backtest_test_data_handler_pit_py
    tests_backtest_test_data_handler_pit_py ~~~ tests_backtest_test_data_quality_checker_py
    tests_backtest_test_data_quality_checker_py ~~~ tests_backtest_test_decay_monitor_py
    tests_backtest_test_decay_monitor_py ~~~ tests_backtest_test_nan_processor_py
    tests_backtest_test_nan_processor_py ~~~ tests_backtest_test_param_analyzer_py
    tests_backtest_test_param_analyzer_py ~~~ tests_backtest_test_report_generator_py
    tests_backtest_test_report_generator_py ~~~ tests_backtest_test_result_comparator_py
    tests_backtest_test_result_comparator_py ~~~ tests_backtest_test_scheduler_py
    tests_backtest_test_scheduler_py ~~~ tests_factor_test_backtest_factor_e2e_py
    tests_factor_test_backtest_factor_e2e_py ~~~ tests_factor_test_evaluation_backtest_py
    tests_factor_test_evaluation_backtest_py ~~~ tests_test_backtest_decisiongraph_adapter_py
    tests_test_backtest_decisiongraph_adapter_py ~~~ tests_test_event_driven_engine_py
    tests_test_event_driven_engine_py ~~~ tests_test_matching_engine_py
    tests_test_matching_engine_py ~~~ tests_test_tick_replay_data_handler_py
    src_zephyr_backtest_core_data_handler_py["数据处理器<br/>回测数据处理器模块（v1.1.0 扩展：多源化 +<br/>ClickHouse 实现 + Tick 源）<br/>data_handler<br/>文件: core/data_handler.py<br/>(生产态 / production)"]
    src_zephyr_backtest_implementations_event_driven_engine_py["事件driven引擎<br/>事件驱动回测引擎（v1.1.0 新增，Tick 级回测核心）<br/>event_driven_engine<br/>文件: implementations/event_driven_engine.py<br/>(生产态 / production)"]
    src_zephyr_backtest_io_backtest_result_sink_py["回测结果sink<br/>回测结果汇 · 回测结果数据落地模块（v1.3.0<br/>新增，#ARCH-047）<br/>backtest_result_sink<br/>文件: io/backtest_result_sink.py<br/>(生产态 / production)"]
    src_zephyr_backtest_io_decisiongraph_adapter_py["decisiongraph适配器<br/>将 BacktestResult（CTR-P1-016，15<br/>字段冻结契约）映射为 decisiongraph<br/>decisiongraph_adapter<br/>文件: io/decisiongraph_adapter.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_anomaly_diagnoser_py["回测异常诊断器<br/>给定回测结果,检查Sharpe是不是太高(可能过拟合)<br/>/胜率是不是太离谱(可能用了未来数据)<br/>/回撤是不是太深/交易次数够不够<br/>/回测时间够不够长等,发现问题就给出修复建议。纯阈<br/>值判定,不改输入。<br/>Anomaly Diagnoser<br/>文件: services/anomaly_diagnoser.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_decay_monitor_py["decay监控器<br/>decay监控，回测的监控器，持续监视某项指标，异常<br/>时上报。<br/>decay_monitor<br/>文件: services/decay_monitor.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_nan_processor_py["nan处理器<br/>服务的处理器，处理加工数据<br/>nan_processor<br/>文件: services/nan_processor.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_param_analyzer_py["参数优化结果分析器<br/>给定一组用不同参数跑出来的回测结果,找出哪组参数<br/>最好,每个参数对结果影响有多大<br/>(敏感度),样本内外差距是不是太大<br/>(过拟合),以及排名靠前的结果是不是稳定。纯统计分<br/>析,不改输入。<br/>Parameter Analyzer<br/>文件: services/param_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_report_generator_py["回测报告生成器<br/>给定回测结果数据,生成一份能直接打开看的HTML报告,<br/>里面有收益/Sharpe/回撤<br/>/胜率等指标表,可选画权益曲线和列交易明细。纯字符<br/>串模板渲染,不需要装额外库。<br/>Backtest Report Generator<br/>文件: services/report_generator.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_result_comparator_py["回测结果比较器<br/>给两组回测结果做差异对比——逐项比较年化收益、Shar<br/>pe、最大回撤等指标,算出候选比基线好多少差多少,再<br/>用统计检验判断差异是真显著还是碰巧,最后生成一张<br/>对比表方便人判断该不该换策略。<br/>Result Comparator<br/>文件: services/result_comparator.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_scheduler_py["D-BACKTEST BT-17<br/>回测自动调度器——批量+参数网格+队列管理+结<br/>- 参数网格展开：将 {param: (v1, v2, ...)}<br/>展开为所有组合<br/>scheduler<br/>文件: services/scheduler.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_data_handler_py ~~~ src_zephyr_backtest_implementations_event_driven_engine_py
    src_zephyr_backtest_implementations_event_driven_engine_py ~~~ src_zephyr_backtest_io_backtest_result_sink_py
    src_zephyr_backtest_io_backtest_result_sink_py ~~~ src_zephyr_backtest_io_decisiongraph_adapter_py
    src_zephyr_backtest_io_decisiongraph_adapter_py ~~~ src_zephyr_backtest_services_anomaly_diagnoser_py
    src_zephyr_backtest_services_anomaly_diagnoser_py ~~~ src_zephyr_backtest_services_decay_monitor_py
    src_zephyr_backtest_services_decay_monitor_py ~~~ src_zephyr_backtest_services_nan_processor_py
    src_zephyr_backtest_services_nan_processor_py ~~~ src_zephyr_backtest_services_param_analyzer_py
    src_zephyr_backtest_services_param_analyzer_py ~~~ src_zephyr_backtest_services_report_generator_py
    src_zephyr_backtest_services_report_generator_py ~~~ src_zephyr_backtest_services_result_comparator_py
    src_zephyr_backtest_services_result_comparator_py ~~~ src_zephyr_backtest_services_scheduler_py
    src_zephyr_backtest_core_pit_manager_py["pit管理器<br/>(Point-In-Time)铁律管理器模块<br/>pit_manager<br/>文件: core/pit_manager.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_tick_replay_py["逐笔replay<br/>Tick 回放引擎模块（v1.1.0 新增，秒级做T专用）<br/>tick_replay<br/>文件: core/tick_replay.py<br/>(生产态 / production)"]
    src_zephyr_backtest_implementations_vectorized_engine_py["vectorized引擎<br/>回测引擎具体实现。实现<br/>BacktestEngineBase，支持向量化回测。<br/>L_BACKTEST — Vectorized Backtest Engine<br/>文件: implementations/vectorized_engine.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_cache_manager_py["回测缓存管理器<br/>给定回测参数(策略ID+参数+日期范围),算出缓存键,把<br/>回测结果存进内存缓存。下次相同参数来查直接返回缓<br/>存结果不用重算,满了按LRU淘汰最久没用的。纯内存管<br/>理,不依赖数据库。<br/>Backtest Cache Manager<br/>文件: services/cache_manager.py<br/>(生产态 / production)"]
    src_zephyr_backtest_services_data_quality_checker_py["数据质量检查器<br/>回测的检查器，检查某项条件是否满足<br/>data_quality_checker<br/>文件: services/data_quality_checker.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_pit_manager_py ~~~ src_zephyr_backtest_core_tick_replay_py
    src_zephyr_backtest_core_tick_replay_py ~~~ src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_implementations_vectorized_engine_py ~~~ src_zephyr_backtest_services_cache_manager_py
    src_zephyr_backtest_services_cache_manager_py ~~~ src_zephyr_backtest_services_data_quality_checker_py
    src_zephyr_backtest_core_decision_gate_py["3阶段决策门控模块(IS->WFA->OOS)<br/>- IS(In-Sample)阶段:样本内Sharpe准入<br/>(>0.5)+参数稳定性门控(避悬崖型参数)<br/>decision_gate<br/>文件: core/decision_gate.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_engine_base_py["引擎基类<br/>回测引擎层。负责离线研究、回测、策略孵化与知识沉<br/>淀。<br/>L_BACKTEST — Backtest Engine Layer<br/>文件: core/engine_base.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_matching_engine_py["matching引擎<br/>回测撮合引擎模块（v1.1.0 重构：委托<br/>MatchingLogic 保证回测=实盘一致性）<br/>matching_engine<br/>文件: core/matching_engine.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_metrics_py["回测绩效指标计算模块<br/>- 计算回测绩效指标:总收益率/年化收益率/Sharpe<br/>/Sortino/最大回撤/胜率<br/>metrics<br/>文件: core/metrics.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_walk_forward_py["walk前<br/>Walk-Forward分析与多重比较偏差校正模块<br/>walk_forward<br/>文件: core/walk_forward.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_decision_gate_py ~~~ src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_core_engine_base_py ~~~ src_zephyr_backtest_core_matching_engine_py
    src_zephyr_backtest_core_matching_engine_py ~~~ src_zephyr_backtest_core_metrics_py
    src_zephyr_backtest_core_metrics_py ~~~ src_zephyr_backtest_core_walk_forward_py
    src_zephyr_backtest_core_matching_logic_py["共享撮合逻辑模块（回测=实盘一致性核心）<br/>- 提供纯函数式撮合逻辑，被 D_BACKTEST<br/>matching_engine(回测) 和<br/>matching_logic<br/>文件: core/matching_logic.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_overfitting_detector_py["过拟合检测模块(三维度 + 三层)<br/>- 过拟合检测三维度(D-FACTOR-03):<br/>overfitting_detector<br/>文件: core/overfitting_detector.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_portfolio_py["回测持仓管理模块<br/>- 持仓管理(买入/卖出/更新市值)<br/>portfolio<br/>文件: core/portfolio.py<br/>(生产态 / production)"]
    src_zephyr_backtest_core_matching_logic_py ~~~ src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_core_overfitting_detector_py ~~~ src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_core_matching_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_logic_py
    src_zephyr_backtest_core_matching_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_core_data_handler_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_pit_manager_py
    src_zephyr_backtest_core_decision_gate_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_core_tick_replay_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_logic_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_engine_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_decision_gate_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_metrics_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_walk_forward_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_io_decisiongraph_adapter_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_matching_engine_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_decision_gate_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_metrics_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_tick_replay_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_walk_forward_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_implementations_event_driven_engine_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_io_backtest_result_sink_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_io_result_repository_py -->|导入依赖 / import_depends| src_zephyr_backtest_io_backtest_result_sink_py
    src_zephyr_backtest_services_anomaly_diagnoser_py -->|import / import| src_zephyr_backtest_services_data_quality_checker_py
    src_zephyr_backtest_services_anomaly_diagnoser_py -->|导入依赖 / import_depends| src_zephyr_backtest_services_data_quality_checker_py
    src_zephyr_backtest_services_scheduler_py -->|导入依赖 / import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_services_scheduler_py -->|导入依赖 / import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_services_param_analyzer_py -->|导入依赖 / import_depends| src_zephyr_backtest_services_cache_manager_py
    src_zephyr_backtest_services_param_analyzer_py -->|import / import| src_zephyr_backtest_services_cache_manager_py
    tests_test_backtest_decisiongraph_adapter_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_engine_base_py
    tests_test_backtest_decisiongraph_adapter_py -->|测试依赖 / test_depends| src_zephyr_backtest_io_decisiongraph_adapter_py
    tests_test_event_driven_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_engine_base_py
    tests_test_event_driven_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_tick_replay_py
    tests_test_event_driven_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    tests_test_event_driven_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_implementations_event_driven_engine_py
    tests_test_matching_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_matching_engine_py
    tests_test_matching_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_matching_logic_py
    tests_test_matching_engine_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_portfolio_py
    tests_test_tick_replay_data_handler_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_data_handler_py
    tests_test_tick_replay_data_handler_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_matching_logic_py
    tests_test_tick_replay_data_handler_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_tick_replay_py
    tests_backtest_test_anomaly_diagnoser_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_anomaly_diagnoser_py
    tests_backtest_test_anomaly_diagnoser_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_data_quality_checker_py
    tests_backtest_test_decay_monitor_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_decay_monitor_py
    tests_backtest_test_param_analyzer_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_cache_manager_py
    tests_backtest_test_param_analyzer_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_param_analyzer_py
    tests_backtest_test_cache_manager_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_cache_manager_py
    tests_backtest_test_nan_processor_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_nan_processor_py
    tests_backtest_test_data_handler_pit_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_data_handler_py
    tests_backtest_test_data_quality_checker_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_data_quality_checker_py
    tests_backtest_test_report_generator_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_report_generator_py
    tests_backtest_test_result_comparator_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_result_comparator_py
    tests_backtest_test_scheduler_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_engine_base_py
    tests_backtest_test_scheduler_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_scheduler_py
    tests_factor_test_backtest_factor_e2e_py -->|测试依赖 / test_depends| src_zephyr_backtest_core_engine_base_py
    tests_factor_test_backtest_factor_e2e_py -->|测试依赖 / test_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    tests_factor_test_backtest_factor_e2e_py -->|测试依赖 / test_depends| src_zephyr_backtest_services_scheduler_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_backtest_core_data_handler_py,src_zephyr_backtest_core_decision_gate_py,src_zephyr_backtest_core_engine_base_py,src_zephyr_backtest_core_matching_engine_py,src_zephyr_backtest_core_matching_logic_py,src_zephyr_backtest_core_metrics_py,src_zephyr_backtest_core_overfitting_detector_py,src_zephyr_backtest_core_pit_manager_py,src_zephyr_backtest_core_portfolio_py,src_zephyr_backtest_core_tick_replay_py,src_zephyr_backtest_core_walk_forward_py,src_zephyr_backtest_implementations_event_driven_engine_py,src_zephyr_backtest_implementations_vectorized_engine_py,src_zephyr_backtest_io_backtest_result_sink_py,src_zephyr_backtest_io_decisiongraph_adapter_py,src_zephyr_backtest_io_result_repository_py,src_zephyr_backtest_services_anomaly_diagnoser_py,src_zephyr_backtest_services_cache_manager_py,src_zephyr_backtest_services_data_quality_checker_py,src_zephyr_backtest_services_decay_monitor_py,src_zephyr_backtest_services_nan_processor_py,src_zephyr_backtest_services_param_analyzer_py,src_zephyr_backtest_services_report_generator_py,src_zephyr_backtest_services_result_comparator_py,src_zephyr_backtest_services_scheduler_py,tests_backtest_test_anomaly_diagnoser_py,tests_backtest_test_cache_manager_py,tests_backtest_test_data_handler_pit_py,tests_backtest_test_data_quality_checker_py,tests_backtest_test_decay_monitor_py,tests_backtest_test_nan_processor_py,tests_backtest_test_param_analyzer_py,tests_backtest_test_report_generator_py,tests_backtest_test_result_comparator_py,tests_backtest_test_scheduler_py,tests_factor_test_backtest_factor_e2e_py,tests_factor_test_evaluation_backtest_py,tests_test_backtest_decisiongraph_adapter_py,tests_test_event_driven_engine_py,tests_test_matching_engine_py,tests_test_tick_replay_data_handler_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 1 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_backtest_services_result_deployer_py["结果deployer<br/>回测的结果，封装操作结果的数据结构<br/>⛔ 受限：涉及实盘安全，需D-EX-CORE执行域就绪<br/>result_deployer<br/>文件: services/result_deployer.py<br/>(设计态 / design)"]
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_backtest_services_result_deployer_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 数据处理器 / data_handler (core/data_handler.py) | → | D_DATA 数据接入层: 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 2 | 数据处理器 / data_handler (core/data_handler.py) | → | D_DATA 数据接入层: ch读取器 / ch_reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 3 | 数据处理器 / data_handler (core/data_handler.py) | → | D_DATA 数据接入层: pit查询 / pit_query (data/pit_query.py) | 导入依赖 / import_depends |
| 4 | 事件driven引擎 / event_driven_engine (implementations/eve... | → | D_EX_CORE 执行核心: miniqmt券商 / miniqmt_broker (adapters/miniqmt_broker.py) | 导入依赖 / import_depends |
| 5 | BacktestDataHandler PIT 财务数据合并测试（#ARCH-CH-021 P0... | → | D_FACTOR 因子: 价值因子 / D_FACTOR — Value Factor (factor/value_factor.py) | 测试依赖 / test_depends |
| 6 | T7 跨域端到端集成测试——D-FACTOR → D-BACKTEST 数据流验... | → | D_FACTOR 因子: D-FACTOR-03 因子评估指标——纯函数模块（无 IO 依赖）。 / ... | 测试依赖 / test_depends |
| 7 | T7 跨域端到端集成测试——D-FACTOR → D-BACKTEST 数据流验... | → | D_FACTOR 因子: 因子基类 / ZephyrAlpha — D_FACTOR Alpha Factor Layer (fa... | 测试依赖 / test_depends |
| 8 | decisiongraph适配器 / decisiongraph_adapter (io/decisiong... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 9 | 数据处理器 / data_handler (core/data_handler.py) | → | D_INFRA_RUNTIME 运行时集成: DatabaseService: 统一管理数据库的连接池、生命周期、健康检... | 导入依赖 / import_depends |
| 10 | 引擎基类 / L_BACKTEST — Backtest Engine Layer (core/engi... | → | D_SHARED 共享服务: core/trace_context.py | 导入依赖 / import_depends |
| 11 | 结果仓库 / result_repository (io/result_repository.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 12 | 结果仓库 / result_repository (io/result_repository.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 13 | 回测异常诊断器 / Anomaly Diagnoser (services/anomaly_diag... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 14 | 回测缓存管理器 / Backtest Cache Manager (services/cache_m... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 15 | 数据质量检查器 / data_quality_checker (services/data_qual... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 16 | decay监控器 / decay_monitor (services/decay_monitor.py) | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 17 | nan处理器 / nan_processor (services/nan_processor.py) | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 18 | 参数优化结果分析器 / Parameter Analyzer (services/param_a... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 19 | 回测报告生成器 / Backtest Report Generator (services/repo... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 20 | 回测结果比较器 / Result Comparator (services/result_compa... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_EX_CORE 执行核心: miniqmt券商 / miniqmt_broker (adapters/miniqmt_broker.py) | → | 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 导入依赖 / import_depends |
| 2 | D_EX_CORE 执行核心: 实时组合 / live_portfolio (services/live_portfolio.py) | → | 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 导入依赖 / import_depends |
| 3 | D_EX_CORE 执行核心: 实时组合 / live_portfolio (services/live_portfolio.py) | → | 回测持仓管理模块 / portfolio (core/portfolio.py) | 导入依赖 / import_depends |
| 4 | D_GOVERNANCE 生命周期管理: E2E 集成测试：全流水线贯通测试 (trading/test_e2e_pipeline... | → | vectorized引擎 / L_BACKTEST — Vectorized Backtest Engine... | 测试依赖 / test_depends |
| 5 | D_PF_CORE 组合核心: D_PORTFOLIO_CORE — 30秒冲高回落做T策略（路径 B 示例策略... | → | 逐笔replay / tick_replay (core/tick_replay.py) | 导入依赖 / import_depends |
| 6 | D_PF_CORE 组合核心: D_PORTFOLIO_CORE — 盘口失衡反转做T策略（路径 B 策略） (p... | → | 逐笔replay / tick_replay (core/tick_replay.py) | 导入依赖 / import_depends |
| 7 | D_PF_CORE 组合核心: D_PORTFOLIO_CORE — StrategyRunner 策略运行器（胶水层） (... | → | 引擎基类 / L_BACKTEST — Backtest Engine Layer (core/engi... | 导入依赖 / import_depends |
| 8 | D_PF_CORE 组合核心: D_PORTFOLIO_CORE — StrategyRunner 策略运行器（胶水层） (... | → | 事件driven引擎 / event_driven_engine (implementations/eve... | 导入依赖 / import_depends |
| 9 | D_PF_CORE 组合核心: D_PORTFOLIO_CORE — StrategyRunner 策略运行器（胶水层） (... | → | vectorized引擎 / L_BACKTEST — Vectorized Backtest Engine... | 导入依赖 / import_depends |
| 10 | D_PF_CORE 组合核心: D_PORTFOLIO_CORE — TickStrategyBase + TickStrategyRegist... | → | 逐笔replay / tick_replay (core/tick_replay.py) | 导入依赖 / import_depends |
| 11 | D_PF_CORE 组合核心: D_PORTFOLIO_CORE — VWAP 回归做T策略（路径 B 策略） (pf_c... | → | 逐笔replay / tick_replay (core/tick_replay.py) | 导入依赖 / import_depends |
| 12 | D_PF_CORE 组合核心: IntradaySurgeFallStrategy 单元测试（路径 B 示例策略）。 (... | → | 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 测试依赖 / test_depends |
| 13 | D_PF_CORE 组合核心: OrderBookImbalanceStrategy 单元测试（路径 B 盘口失衡反转... | → | 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 测试依赖 / test_depends |
| 14 | D_PF_CORE 组合核心: VWAPReversionStrategy 单元测试（路径 B 均值回归策略）。 (... | → | 共享撮合逻辑模块（回测=实盘一致性核心） / matching_logic ... | 测试依赖 / test_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 7 个外部域直接连接（出边 20 条 + 入边 14 条 = 34 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_FACTOR["D_FACTOR<br/>因子"]
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_PF_CORE["D_PF_CORE<br/>组合核心"]
    D_BACKTEST -->|11条 导入依赖 / import_depends| D_SHARED
    D_BACKTEST -->|3条 导入依赖 / import_depends| D_DATA
    D_BACKTEST -->|3条 测试依赖 / test_depends| D_FACTOR
    D_BACKTEST -->|1条 导入依赖 / import_depends| D_EX_CORE
    D_BACKTEST -->|1条 导入依赖 / import_depends| D_GOVERNANCE
    D_BACKTEST -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_PF_CORE -->|10条 导入依赖 / import_depends, 测试依赖 / test_depends| D_BACKTEST
    D_EX_CORE -->|3条 导入依赖 / import_depends| D_BACKTEST
    D_GOVERNANCE -->|1条 测试依赖 / test_depends| D_BACKTEST
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
