---
doc_type: architecture_view
title: D_SELL_DECISION 卖出决策架构文档
version: "1.0"
status: active
date: 2026-08-03
owner: auto-generator
ttl: permanent
---

# 67_d_sell_decision / 卖出决策域 / Sell Decision

> **功能简介 / Overview**: 卖出决策，负责卖出信号生成、卖出时机判断和退出策略

> **文档作用 / Purpose**: 展示 卖出决策（D_SELL_DECISION）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/67_d_sell_decision.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 67 | Number | 67 |
| 域ID | D_SELL_DECISION | Domain ID | D_SELL_DECISION |
| 域名称 | 卖出决策 | Domain Name | Sell Decision |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 26 | Module Count | 26 |
| 域内依赖 | 15 | Internal Dependencies | 15 |
| 跨域入边 | 4 | Cross-domain Incoming | 4 |
| 跨域出边 | 3 | Cross-domain Outgoing | 3 |
| 设计态模块 | 18 | Design Modules | 18 |
| 生产态模块 | 8 | Production Modules | 8 |
| 容量 | 8/150 (正常) | Capacity | 8/150 (正常) |
| 描述 | 卖出决策，负责卖出信号生成、卖出时机判断和退出策略 | Description | 卖出决策，负责卖出信号生成、卖出时机判断和退出策略 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 26 个模块（生产态 8 + 设计态 18），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_sell_decision_init_py["zephyr/sell_decision 包入口<br/>sell_decision的包入口，把这一层的子模块归到一起<br/>统一管理，用到谁才加载谁，避免一次性全加载拖慢启<br/>动。<br/>文件: sell_decision/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_extensions_init_py["sell_decision/_extensions 包入口<br/>卖出决策/扩展 包入口，整合扩展相关子模块导出<br/>文件: _extensions/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_api_init_py["sell_decision/api 包入口<br/>卖出决策/接口 包入口，整合接口相关子模块导出<br/>文件: api/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_core_breakout_failure_detector_py["突破故障检测器<br/>突破failure检测器，core的检测器，检测特定模式或<br/>异常情况。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>breakout_failure_detector<br/>文件: core/breakout_failure_detector.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_position_triage_py["持仓分诊<br/>器，按规则对持仓分类并标记处置优先级<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>position_triage<br/>文件: core/position_triage.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_replacement_rebalance_sell_py["replacementrebalance卖出<br/>替代再平衡卖出策略，当标的被更好的替代品取代时触<br/>发卖出并再平衡组合。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>replacement_rebalance_sell<br/>文件: core/replacement_rebalance_sell.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_replacement_rebalance_seller_py["置换与再平衡卖出<br/>两种被动卖出驱动: ① 机会成本驱动(置换):<br/>候选池有更优标的 → 卖A买B(REPLACE) ②<br/>组合再平衡驱动: 权重偏离 > 阈值 →<br/>被动卖出超配标的(REDUCE)<br/>Replacement & Rebalance Seller<br/>文件: core/replacement_rebalance_seller.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_core_sell_conflict_arbitrator_py["买卖冲突仲裁器<br/>同标的同时存在买入+卖出信号 → 卖出优先<br/>(保守原则) + 冲突等级分类 + 审计追溯<br/>Sell Conflict Arbitrator<br/>文件: core/sell_conflict_arbitrator.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py["卖出信号准确率监控器<br/>统计每类卖出信号触发后N天的准确率，分析假阳性<br/>(卖了又涨=止损过紧)和假阴性<br/>(没卖继续跌=信号漏判)，按信号类型和策略类型分组<br/>，动态调整信号权重让准的信号更重、不准的更轻。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>文件: core/sell_signal_accuracy_monitor.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_urgency_scorer_py["卖出urgency评分器<br/>Sell Urgency Scorer — 卖出紧迫度评分器<br/>(MOD-SELL-009)<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>sell_urgency_scorer<br/>文件: core/sell_urgency_scorer.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_stop_hunting_protector_py["止损猎杀防护器<br/>防护做市商/HFT 主动猎杀止损位: ① 止损位偏移:<br/>不精确设在技术位, 偏移 1-2% 防猎杀 ②<br/>软止损模式: 到达止损位→不立即执行→进入<br/>OBSERVING 观察期 → 观察期确认跌破<br/>(收盘价<止损位)→执行 → 观察期收回<br/>(价格回升)→解除(CLEARED)<br/>Stop-Hunting Protector<br/>文件: core/stop_hunting_protector.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_strategy_specific_stop_framework_py["策略specific止损framework<br/>策略专属止损框架，按各策略特性定制止损规则。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>strategy_specific_stop_framework<br/>文件: core/strategy_specific_stop_framework.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_take_profit_strategy_py["止盈利润策略<br/>核心逻辑（take profit strategy）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>take_profit_strategy<br/>文件: core/take_profit_strategy.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_infrastructure_init_py["sell_decision/infrastructure 包入口<br/>卖出决策/基础设施<br/>包入口，整合基础设施相关子模块导出<br/>文件: infrastructure/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_models_init_py["sell_decision/models 包入口<br/>卖出决策/模型 包入口，整合模型相关子模块导出<br/>文件: models/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_services_init_py["sell_decision/services 包入口<br/>卖出决策/服务 包入口，整合服务相关子模块导出<br/>文件: services/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_init_py ~~~ src_zephyr_sell_decision_extensions_init_py
    src_zephyr_sell_decision_extensions_init_py ~~~ src_zephyr_sell_decision_api_init_py
    src_zephyr_sell_decision_api_init_py ~~~ src_zephyr_sell_decision_core_breakout_failure_detector_py
    src_zephyr_sell_decision_core_breakout_failure_detector_py ~~~ src_zephyr_sell_decision_core_position_triage_py
    src_zephyr_sell_decision_core_position_triage_py ~~~ src_zephyr_sell_decision_core_replacement_rebalance_sell_py
    src_zephyr_sell_decision_core_replacement_rebalance_sell_py ~~~ src_zephyr_sell_decision_core_replacement_rebalance_seller_py
    src_zephyr_sell_decision_core_replacement_rebalance_seller_py ~~~ src_zephyr_sell_decision_core_sell_conflict_arbitrator_py
    src_zephyr_sell_decision_core_sell_conflict_arbitrator_py ~~~ src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py
    src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py ~~~ src_zephyr_sell_decision_core_sell_urgency_scorer_py
    src_zephyr_sell_decision_core_sell_urgency_scorer_py ~~~ src_zephyr_sell_decision_core_stop_hunting_protector_py
    src_zephyr_sell_decision_core_stop_hunting_protector_py ~~~ src_zephyr_sell_decision_core_strategy_specific_stop_framework_py
    src_zephyr_sell_decision_core_strategy_specific_stop_framework_py ~~~ src_zephyr_sell_decision_core_take_profit_strategy_py
    src_zephyr_sell_decision_core_take_profit_strategy_py ~~~ src_zephyr_sell_decision_infrastructure_init_py
    src_zephyr_sell_decision_infrastructure_init_py ~~~ src_zephyr_sell_decision_models_init_py
    src_zephyr_sell_decision_models_init_py ~~~ src_zephyr_sell_decision_services_init_py
    src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py["买入卖出冲突仲裁器<br/>（buy_sell_conflict_arbitrator.py）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>文件: core/buy_sell_conflict_arbitrator.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_exit_scenario_planner_py["退出场景规划器<br/>卖出决策的规划器，规划执行方案<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>exit_scenario_planner<br/>文件: core/exit_scenario_planner.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_scaling_out_architect_py["scaling出architect<br/>分批减仓架构师，按计划分多批逐步减仓，控制单次冲<br/>击与滑点。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>scaling_out_architect<br/>文件: core/scaling_out_architect.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_execution_quality_tracker_py["卖出执行质量追踪器<br/>追踪每笔卖出执行的滑点、冲击成本、执行延迟、分批<br/>执行效果，计算执行质量评分反馈给卖出执行策略，让<br/>下次卖得更便宜更快。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>文件: core/sell_execution_quality_tracker.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_strategy_ab_tester_py["卖出策略A/B测试器<br/>把不同止盈线(8%vs10%)、止损范式<br/>(移动vs固定)、退出方式(分批vs一次性)做A<br/>/B对照实验，统计显著性检验后产出参数调整建议，让<br/>卖出策略参数靠数据说话而非拍脑袋。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>文件: core/sell_strategy_ab_tester.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_stop_loss_strategy_py["停止亏损策略<br/>核心逻辑（stop loss strategy）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>stop_loss_strategy<br/>文件: core/stop_loss_strategy.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py ~~~ src_zephyr_sell_decision_core_exit_scenario_planner_py
    src_zephyr_sell_decision_core_exit_scenario_planner_py ~~~ src_zephyr_sell_decision_core_scaling_out_architect_py
    src_zephyr_sell_decision_core_scaling_out_architect_py ~~~ src_zephyr_sell_decision_core_sell_execution_quality_tracker_py
    src_zephyr_sell_decision_core_sell_execution_quality_tracker_py ~~~ src_zephyr_sell_decision_core_sell_strategy_ab_tester_py
    src_zephyr_sell_decision_core_sell_strategy_ab_tester_py ~~~ src_zephyr_sell_decision_core_stop_loss_strategy_py
    src_zephyr_sell_decision_core_sell_signal_fusion_engine_py["卖信号融合引擎<br/>core的引擎，执行核心逻辑的处理引擎（sell signal<br/>fusion）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>sell_signal_fusion_engine<br/>文件: core/sell_signal_fusion_engine.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_signal_scorer_py["卖信号评分器<br/>核心逻辑（sell signal scorer）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>sell_signal_scorer<br/>文件: core/sell_signal_scorer.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_t_trade_coordinator_py["t交易协调器<br/>卖出决策<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>t_trade_coordinator<br/>文件: core/t_trade_coordinator.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_signal_scorer_py ~~~ src_zephyr_sell_decision_core_t_trade_coordinator_py
    src_zephyr_sell_decision_core_sell_signal_collector_py["卖信号收集器<br/>core的采集器，从多处收集数据<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>sell_signal_collector<br/>文件: core/sell_signal_collector.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_position_triage_py -.->|event / event| src_zephyr_sell_decision_core_sell_signal_fusion_engine_py
    src_zephyr_sell_decision_core_position_triage_py -.->|data / data| src_zephyr_sell_decision_core_exit_scenario_planner_py
    src_zephyr_sell_decision_core_sell_signal_scorer_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_collector_py
    src_zephyr_sell_decision_core_breakout_failure_detector_py -.->|data / data| src_zephyr_sell_decision_core_sell_signal_scorer_py
    src_zephyr_sell_decision_core_take_profit_strategy_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_scorer_py
    src_zephyr_sell_decision_core_stop_loss_strategy_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_scorer_py
    src_zephyr_sell_decision_core_replacement_rebalance_sell_py -.->|data / data| src_zephyr_sell_decision_core_sell_signal_fusion_engine_py
    src_zephyr_sell_decision_core_sell_signal_fusion_engine_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_scorer_py
    src_zephyr_sell_decision_core_sell_signal_fusion_engine_py -.->|data / data| src_zephyr_sell_decision_core_t_trade_coordinator_py
    src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_fusion_engine_py
    src_zephyr_sell_decision_core_sell_urgency_scorer_py -.->|runtime / runtime| src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py
    src_zephyr_sell_decision_core_sell_urgency_scorer_py -.->|data / data| src_zephyr_sell_decision_core_scaling_out_architect_py
    src_zephyr_sell_decision_core_strategy_specific_stop_framework_py -.->|data / data| src_zephyr_sell_decision_core_stop_loss_strategy_py
    src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py -.->|import / import| src_zephyr_sell_decision_core_sell_strategy_ab_tester_py
    src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py -.->|import / import| src_zephyr_sell_decision_core_sell_execution_quality_tracker_py
    D_POSITION["仓位管理<br/>仓位管理，负责持仓跟踪、仓位计算和盈亏分析<br/>Position Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_sell_decision_core_sell_signal_fusion_engine_py -.->|runtime / runtime| D_POSITION
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_sell_decision_core_replacement_rebalance_seller_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_sell_decision_core_sell_conflict_arbitrator_py -->|导入依赖 / import_depends| D_SHARED
    D_EX_CORE["执行核心<br/>执行核心，负责订单执行引擎、执行策略和执行管理<br/>Execution Core<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_EX_CORE -.->|runtime / runtime| src_zephyr_sell_decision_core_position_triage_py
    D_EX_CORE -.->|runtime / runtime| src_zephyr_sell_decision_core_position_triage_py
    D_EX_CORE -.->|runtime / runtime| src_zephyr_sell_decision_core_position_triage_py
    D_EX_CORE -.->|runtime / runtime| src_zephyr_sell_decision_core_position_triage_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_sell_decision_init_py,src_zephyr_sell_decision_extensions_init_py,src_zephyr_sell_decision_api_init_py,src_zephyr_sell_decision_core_replacement_rebalance_seller_py,src_zephyr_sell_decision_core_sell_conflict_arbitrator_py,src_zephyr_sell_decision_infrastructure_init_py,src_zephyr_sell_decision_models_init_py,src_zephyr_sell_decision_services_init_py production
    class src_zephyr_sell_decision_core_breakout_failure_detector_py,src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py,src_zephyr_sell_decision_core_exit_scenario_planner_py,src_zephyr_sell_decision_core_position_triage_py,src_zephyr_sell_decision_core_replacement_rebalance_sell_py,src_zephyr_sell_decision_core_scaling_out_architect_py,src_zephyr_sell_decision_core_sell_execution_quality_tracker_py,src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py,src_zephyr_sell_decision_core_sell_signal_collector_py,src_zephyr_sell_decision_core_sell_signal_fusion_engine_py,src_zephyr_sell_decision_core_sell_signal_scorer_py,src_zephyr_sell_decision_core_sell_strategy_ab_tester_py,src_zephyr_sell_decision_core_sell_urgency_scorer_py,src_zephyr_sell_decision_core_stop_hunting_protector_py,src_zephyr_sell_decision_core_stop_loss_strategy_py,src_zephyr_sell_decision_core_strategy_specific_stop_framework_py,src_zephyr_sell_decision_core_t_trade_coordinator_py,src_zephyr_sell_decision_core_take_profit_strategy_py design
    class D_POSITION,D_SHARED external_prod
    class D_EX_CORE external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 8 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_sell_decision_init_py["zephyr/sell_decision 包入口<br/>sell_decision的包入口，把这一层的子模块归到一起<br/>统一管理，用到谁才加载谁，避免一次性全加载拖慢启<br/>动。<br/>文件: sell_decision/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_extensions_init_py["sell_decision/_extensions 包入口<br/>卖出决策/扩展 包入口，整合扩展相关子模块导出<br/>文件: _extensions/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_api_init_py["sell_decision/api 包入口<br/>卖出决策/接口 包入口，整合接口相关子模块导出<br/>文件: api/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_core_replacement_rebalance_seller_py["置换与再平衡卖出<br/>两种被动卖出驱动: ① 机会成本驱动(置换):<br/>候选池有更优标的 → 卖A买B(REPLACE) ②<br/>组合再平衡驱动: 权重偏离 > 阈值 →<br/>被动卖出超配标的(REDUCE)<br/>Replacement & Rebalance Seller<br/>文件: core/replacement_rebalance_seller.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_core_sell_conflict_arbitrator_py["买卖冲突仲裁器<br/>同标的同时存在买入+卖出信号 → 卖出优先<br/>(保守原则) + 冲突等级分类 + 审计追溯<br/>Sell Conflict Arbitrator<br/>文件: core/sell_conflict_arbitrator.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_infrastructure_init_py["sell_decision/infrastructure 包入口<br/>卖出决策/基础设施<br/>包入口，整合基础设施相关子模块导出<br/>文件: infrastructure/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_models_init_py["sell_decision/models 包入口<br/>卖出决策/模型 包入口，整合模型相关子模块导出<br/>文件: models/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_services_init_py["sell_decision/services 包入口<br/>卖出决策/服务 包入口，整合服务相关子模块导出<br/>文件: services/__init__.py<br/>(生产态 / production)"]
    src_zephyr_sell_decision_init_py ~~~ src_zephyr_sell_decision_extensions_init_py
    src_zephyr_sell_decision_extensions_init_py ~~~ src_zephyr_sell_decision_api_init_py
    src_zephyr_sell_decision_api_init_py ~~~ src_zephyr_sell_decision_core_replacement_rebalance_seller_py
    src_zephyr_sell_decision_core_replacement_rebalance_seller_py ~~~ src_zephyr_sell_decision_core_sell_conflict_arbitrator_py
    src_zephyr_sell_decision_core_sell_conflict_arbitrator_py ~~~ src_zephyr_sell_decision_infrastructure_init_py
    src_zephyr_sell_decision_infrastructure_init_py ~~~ src_zephyr_sell_decision_models_init_py
    src_zephyr_sell_decision_models_init_py ~~~ src_zephyr_sell_decision_services_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_sell_decision_init_py,src_zephyr_sell_decision_extensions_init_py,src_zephyr_sell_decision_api_init_py,src_zephyr_sell_decision_core_replacement_rebalance_seller_py,src_zephyr_sell_decision_core_sell_conflict_arbitrator_py,src_zephyr_sell_decision_infrastructure_init_py,src_zephyr_sell_decision_models_init_py,src_zephyr_sell_decision_services_init_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 18 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_sell_decision_core_breakout_failure_detector_py["突破故障检测器<br/>突破failure检测器，core的检测器，检测特定模式或<br/>异常情况。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>breakout_failure_detector<br/>文件: core/breakout_failure_detector.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_position_triage_py["持仓分诊<br/>器，按规则对持仓分类并标记处置优先级<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>position_triage<br/>文件: core/position_triage.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_replacement_rebalance_sell_py["replacementrebalance卖出<br/>替代再平衡卖出策略，当标的被更好的替代品取代时触<br/>发卖出并再平衡组合。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>replacement_rebalance_sell<br/>文件: core/replacement_rebalance_sell.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py["卖出信号准确率监控器<br/>统计每类卖出信号触发后N天的准确率，分析假阳性<br/>(卖了又涨=止损过紧)和假阴性<br/>(没卖继续跌=信号漏判)，按信号类型和策略类型分组<br/>，动态调整信号权重让准的信号更重、不准的更轻。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>文件: core/sell_signal_accuracy_monitor.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_urgency_scorer_py["卖出urgency评分器<br/>Sell Urgency Scorer — 卖出紧迫度评分器<br/>(MOD-SELL-009)<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>sell_urgency_scorer<br/>文件: core/sell_urgency_scorer.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_stop_hunting_protector_py["止损猎杀防护器<br/>防护做市商/HFT 主动猎杀止损位: ① 止损位偏移:<br/>不精确设在技术位, 偏移 1-2% 防猎杀 ②<br/>软止损模式: 到达止损位→不立即执行→进入<br/>OBSERVING 观察期 → 观察期确认跌破<br/>(收盘价<止损位)→执行 → 观察期收回<br/>(价格回升)→解除(CLEARED)<br/>Stop-Hunting Protector<br/>文件: core/stop_hunting_protector.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_strategy_specific_stop_framework_py["策略specific止损framework<br/>策略专属止损框架，按各策略特性定制止损规则。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>strategy_specific_stop_framework<br/>文件: core/strategy_specific_stop_framework.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_take_profit_strategy_py["止盈利润策略<br/>核心逻辑（take profit strategy）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>take_profit_strategy<br/>文件: core/take_profit_strategy.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_breakout_failure_detector_py ~~~ src_zephyr_sell_decision_core_position_triage_py
    src_zephyr_sell_decision_core_position_triage_py ~~~ src_zephyr_sell_decision_core_replacement_rebalance_sell_py
    src_zephyr_sell_decision_core_replacement_rebalance_sell_py ~~~ src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py
    src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py ~~~ src_zephyr_sell_decision_core_sell_urgency_scorer_py
    src_zephyr_sell_decision_core_sell_urgency_scorer_py ~~~ src_zephyr_sell_decision_core_stop_hunting_protector_py
    src_zephyr_sell_decision_core_stop_hunting_protector_py ~~~ src_zephyr_sell_decision_core_strategy_specific_stop_framework_py
    src_zephyr_sell_decision_core_strategy_specific_stop_framework_py ~~~ src_zephyr_sell_decision_core_take_profit_strategy_py
    src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py["买入卖出冲突仲裁器<br/>（buy_sell_conflict_arbitrator.py）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>文件: core/buy_sell_conflict_arbitrator.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_exit_scenario_planner_py["退出场景规划器<br/>卖出决策的规划器，规划执行方案<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>exit_scenario_planner<br/>文件: core/exit_scenario_planner.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_scaling_out_architect_py["scaling出architect<br/>分批减仓架构师，按计划分多批逐步减仓，控制单次冲<br/>击与滑点。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>scaling_out_architect<br/>文件: core/scaling_out_architect.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_execution_quality_tracker_py["卖出执行质量追踪器<br/>追踪每笔卖出执行的滑点、冲击成本、执行延迟、分批<br/>执行效果，计算执行质量评分反馈给卖出执行策略，让<br/>下次卖得更便宜更快。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>文件: core/sell_execution_quality_tracker.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_strategy_ab_tester_py["卖出策略A/B测试器<br/>把不同止盈线(8%vs10%)、止损范式<br/>(移动vs固定)、退出方式(分批vs一次性)做A<br/>/B对照实验，统计显著性检验后产出参数调整建议，让<br/>卖出策略参数靠数据说话而非拍脑袋。<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>文件: core/sell_strategy_ab_tester.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_stop_loss_strategy_py["停止亏损策略<br/>核心逻辑（stop loss strategy）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>stop_loss_strategy<br/>文件: core/stop_loss_strategy.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py ~~~ src_zephyr_sell_decision_core_exit_scenario_planner_py
    src_zephyr_sell_decision_core_exit_scenario_planner_py ~~~ src_zephyr_sell_decision_core_scaling_out_architect_py
    src_zephyr_sell_decision_core_scaling_out_architect_py ~~~ src_zephyr_sell_decision_core_sell_execution_quality_tracker_py
    src_zephyr_sell_decision_core_sell_execution_quality_tracker_py ~~~ src_zephyr_sell_decision_core_sell_strategy_ab_tester_py
    src_zephyr_sell_decision_core_sell_strategy_ab_tester_py ~~~ src_zephyr_sell_decision_core_stop_loss_strategy_py
    src_zephyr_sell_decision_core_sell_signal_fusion_engine_py["卖信号融合引擎<br/>core的引擎，执行核心逻辑的处理引擎（sell signal<br/>fusion）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>sell_signal_fusion_engine<br/>文件: core/sell_signal_fusion_engine.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_signal_scorer_py["卖信号评分器<br/>核心逻辑（sell signal scorer）<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>sell_signal_scorer<br/>文件: core/sell_signal_scorer.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_t_trade_coordinator_py["t交易协调器<br/>卖出决策<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>t_trade_coordinator<br/>文件: core/t_trade_coordinator.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_sell_signal_scorer_py ~~~ src_zephyr_sell_decision_core_t_trade_coordinator_py
    src_zephyr_sell_decision_core_sell_signal_collector_py["卖信号收集器<br/>core的采集器，从多处收集数据<br/>⛔ 卖出决策域，设计已就绪，等待开发排期<br/>sell_signal_collector<br/>文件: core/sell_signal_collector.py<br/>(设计态 / design)"]
    src_zephyr_sell_decision_core_position_triage_py -.->|event / event| src_zephyr_sell_decision_core_sell_signal_fusion_engine_py
    src_zephyr_sell_decision_core_position_triage_py -.->|data / data| src_zephyr_sell_decision_core_exit_scenario_planner_py
    src_zephyr_sell_decision_core_sell_signal_scorer_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_collector_py
    src_zephyr_sell_decision_core_breakout_failure_detector_py -.->|data / data| src_zephyr_sell_decision_core_sell_signal_scorer_py
    src_zephyr_sell_decision_core_take_profit_strategy_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_scorer_py
    src_zephyr_sell_decision_core_stop_loss_strategy_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_scorer_py
    src_zephyr_sell_decision_core_replacement_rebalance_sell_py -.->|data / data| src_zephyr_sell_decision_core_sell_signal_fusion_engine_py
    src_zephyr_sell_decision_core_sell_signal_fusion_engine_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_scorer_py
    src_zephyr_sell_decision_core_sell_signal_fusion_engine_py -.->|data / data| src_zephyr_sell_decision_core_t_trade_coordinator_py
    src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py -.->|runtime / runtime| src_zephyr_sell_decision_core_sell_signal_fusion_engine_py
    src_zephyr_sell_decision_core_sell_urgency_scorer_py -.->|runtime / runtime| src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py
    src_zephyr_sell_decision_core_sell_urgency_scorer_py -.->|data / data| src_zephyr_sell_decision_core_scaling_out_architect_py
    src_zephyr_sell_decision_core_strategy_specific_stop_framework_py -.->|data / data| src_zephyr_sell_decision_core_stop_loss_strategy_py
    src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py -.->|import / import| src_zephyr_sell_decision_core_sell_strategy_ab_tester_py
    src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py -.->|import / import| src_zephyr_sell_decision_core_sell_execution_quality_tracker_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_sell_decision_core_breakout_failure_detector_py,src_zephyr_sell_decision_core_buy_sell_conflict_arbitrator_py,src_zephyr_sell_decision_core_exit_scenario_planner_py,src_zephyr_sell_decision_core_position_triage_py,src_zephyr_sell_decision_core_replacement_rebalance_sell_py,src_zephyr_sell_decision_core_scaling_out_architect_py,src_zephyr_sell_decision_core_sell_execution_quality_tracker_py,src_zephyr_sell_decision_core_sell_signal_accuracy_monitor_py,src_zephyr_sell_decision_core_sell_signal_collector_py,src_zephyr_sell_decision_core_sell_signal_fusion_engine_py,src_zephyr_sell_decision_core_sell_signal_scorer_py,src_zephyr_sell_decision_core_sell_strategy_ab_tester_py,src_zephyr_sell_decision_core_sell_urgency_scorer_py,src_zephyr_sell_decision_core_stop_hunting_protector_py,src_zephyr_sell_decision_core_stop_loss_strategy_py,src_zephyr_sell_decision_core_strategy_specific_stop_framework_py,src_zephyr_sell_decision_core_t_trade_coordinator_py,src_zephyr_sell_decision_core_take_profit_strategy_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 卖信号融合引擎 / sell_signal_fusion_engine (core/sell_sig... | → | D_POSITION 仓位管理: 卖出持仓链接 / sell_position_link (core/sell_position_lin... | runtime / runtime |
| 2 | 置换与再平衡卖出 / Replacement & Rebalance Seller (core/r... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 3 | 买卖冲突仲裁器 / Sell Conflict Arbitrator (core/sell_conf... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_EX_CORE 执行核心: 卖出优先级调度器 / sell_priority_scheduler (ex_core/sell_... | → | 持仓分诊 / position_triage (core/position_triage.py) | runtime / runtime |
| 2 | D_EX_CORE 执行核心: 卖出优先级调度器 / sell_priority_scheduler (ex_core/sell_... | → | 持仓分诊 / position_triage (core/position_triage.py) | runtime / runtime |
| 3 | D_EX_CORE 执行核心: 停止亏损止盈利润执行器 / stop_loss_take_profit_executor (... | → | 持仓分诊 / position_triage (core/position_triage.py) | runtime / runtime |
| 4 | D_EX_CORE 执行核心: 停止亏损止盈利润执行器 / stop_loss_take_profit_executor (... | → | 持仓分诊 / position_triage (core/position_triage.py) | runtime / runtime |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 3 个外部域直接连接（出边 3 条 + 入边 4 条 = 7 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_SELL_DECISION["D_SELL_DECISION<br/>卖出决策"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_POSITION["D_POSITION<br/>仓位管理"]
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_SELL_DECISION -->|2条 导入依赖 / import_depends| D_SHARED
    D_SELL_DECISION -->|1条 runtime / runtime| D_POSITION
    D_EX_CORE -->|4条 runtime / runtime| D_SELL_DECISION
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
