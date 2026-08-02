---
doc_type: architecture_view
title: D_SIMULATION 仿真架构文档
version: "1.0"
status: active
date: 2026-08-03
owner: auto-generator
ttl: permanent
---

# 70_d_simulation / 仿真域 / Simulation

> **功能简介 / Overview**: 仿真，负责市场仿真、模拟撮合和仿真环境管理

> **文档作用 / Purpose**: 展示 仿真（D_SIMULATION）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/70_d_simulation.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 70 | Number | 70 |
| 域ID | D_SIMULATION | Domain ID | D_SIMULATION |
| 域名称 | 仿真 | Domain Name | Simulation |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 15 | Module Count | 15 |
| 域内依赖 | 15 | Internal Dependencies | 15 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 9 | Cross-domain Outgoing | 9 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 15 | Production Modules | 15 |
| 容量 | 15/150 (正常) | Capacity | 15/150 (正常) |
| 描述 | 仿真，负责市场仿真、模拟撮合和仿真环境管理 | Description | 仿真，负责市场仿真、模拟撮合和仿真环境管理 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 15 个模块（生产态 15 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_simulation_implementations_default_experiment_pipeline_py["默认实验管线<br/>simulation implementations<br/>包入口，整合implementations相关子模块导出<br/>default_experiment_pipeline<br/>文件: implementations<br/>/default_experiment_pipeline.py<br/>(生产态 / production)"]
    src_zephyr_simulation_result_analyzer_py["仿真结果分析器<br/>对多个策略仿真结果执行跨场景聚合统计(均值<br/>/标准差/分位数<br/>/置信区间)、收益率分布Jarque-Bera正态性检验和可<br/>视化数据准备,产出含摘要的分析报告<br/>文件: simulation/result_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_scenario_generator_py["场景生成器<br/>给仿真造市场行情的工厂——三种模式:蒙特卡洛用几何<br/>布朗运动随机生成一条价格路径,历史模式从真实数据<br/>切一段下来,自定义模式让你指定在某几根K线上插个涨<br/>跌冲击。跑完吐出一个场景包<br/>(含OHLCV数据+参数快照),喂给策略仿真器看策略在这<br/>种假设行情下会怎样。<br/>Scenario Generator<br/>文件: simulation/scenario_generator.py<br/>(生产态 / production)"]
    tests_simulation_test_deflated_sharpe_calculator_py["simulation/test_deflated_sharpe_calculator<br/>MOD-SIM-024 Deflated Sharpe Ratio Calculator<br/>单元测试.<br/>文件: simulation<br/>/test_deflated_sharpe_calculator.py<br/>(生产态 / production)"]
    tests_simulation_test_look_ahead_bias_detector_py["simulation/test_look_ahead_bias_detector<br/>MOD-SIM-022 Look-Ahead Bias Detector 单元测试.<br/>文件: simulation<br/>/test_look_ahead_bias_detector.py<br/>(生产态 / production)"]
    tests_simulation_test_parameter_robustness_tester_py["simulation/test_parameter_robustness_tester<br/>MOD-SIM-021 Parameter Robustness Tester<br/>单元测试.<br/>文件: simulation<br/>/test_parameter_robustness_tester.py<br/>(生产态 / production)"]
    tests_simulation_test_risk_simulator_py["simulation/test_risk_simulator<br/>MOD-SIM-003 Risk Simulator 单元测试.<br/>文件: simulation/test_risk_simulator.py<br/>(生产态 / production)"]
    tests_simulation_test_sharpe_calculator_fixer_py["simulation/test_sharpe_calculator_fixer<br/>MOD-SIM-023 Sharpe Calculator Fixer 单元测试.<br/>文件: simulation/test_sharpe_calculator_fixer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_implementations_default_experiment_pipeline_py ~~~ src_zephyr_simulation_result_analyzer_py
    src_zephyr_simulation_result_analyzer_py ~~~ src_zephyr_simulation_scenario_generator_py
    src_zephyr_simulation_scenario_generator_py ~~~ tests_simulation_test_deflated_sharpe_calculator_py
    tests_simulation_test_deflated_sharpe_calculator_py ~~~ tests_simulation_test_look_ahead_bias_detector_py
    tests_simulation_test_look_ahead_bias_detector_py ~~~ tests_simulation_test_parameter_robustness_tester_py
    tests_simulation_test_parameter_robustness_tester_py ~~~ tests_simulation_test_risk_simulator_py
    tests_simulation_test_risk_simulator_py ~~~ tests_simulation_test_sharpe_calculator_fixer_py
    src_zephyr_simulation_pipeline_base_py["管线基类<br/>仿真相关功能（pipeline base）<br/>pipeline_base<br/>文件: simulation/pipeline_base.py<br/>(生产态 / production)"]
    src_zephyr_simulation_risk_simulator_py["风控仿真器<br/>给定一段收益率数据,算出最坏情况下可能亏多少<br/>(VaR)和亏的时候平均亏多少<br/>(CVaR),再模拟最大回撤有多大/多久能恢复<br/>/是否触发熔断阈值。纯数学计算,不决定买卖。<br/>Risk Simulator<br/>文件: simulation/risk_simulator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_strategy_simulator_py["策略仿真器<br/>给策略搭一个隔离沙箱——喂进去模拟行情和一个策略函<br/>数,它就逐根K线模拟这个策略会怎么发信号、怎么建仓<br/>、最后赚多少亏多少,跑完吐出净值曲线和交易记录,方<br/>便分析策略在假设行情下表现如何。策略本身由调用方<br/>注入,仿真器只管调度和记账,不掺和策略决策。<br/>Strategy Simulator<br/>文件: simulation/strategy_simulator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_pipeline_base_py ~~~ src_zephyr_simulation_risk_simulator_py
    src_zephyr_simulation_risk_simulator_py ~~~ src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_look_ahead_bias_detector_py["lookaheadbias检测器<br/>模拟的检测器，检测特定模式或异常情况<br/>look_ahead_bias_detector<br/>文件: simulation/look_ahead_bias_detector.py<br/>(生产态 / production)"]
    src_zephyr_simulation_parameter_robustness_tester_py["参数鲁棒性测试器<br/>模拟的测试器，测试验证功能<br/>parameter_robustness_tester<br/>文件: simulation/parameter_robustness_tester.py<br/>(生产态 / production)"]
    src_zephyr_simulation_sharpe_calculator_fixer_py["夏普计算器修复器<br/>模拟的计算器，计算得出结果（sharpe calculator<br/>fixer）<br/>sharpe_calculator_fixer<br/>文件: simulation/sharpe_calculator_fixer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_look_ahead_bias_detector_py ~~~ src_zephyr_simulation_parameter_robustness_tester_py
    src_zephyr_simulation_parameter_robustness_tester_py ~~~ src_zephyr_simulation_sharpe_calculator_fixer_py
    src_zephyr_simulation_deflated_sharpe_calculator_py["缩水夏普计算器<br/>模拟的计算器，计算得出结果（deflated sharpe<br/>calculator）<br/>deflated_sharpe_calculator<br/>文件: simulation/deflated_sharpe_calculator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|导入依赖 / import_depends| src_zephyr_simulation_deflated_sharpe_calculator_py
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|data / data| src_zephyr_simulation_deflated_sharpe_calculator_py
    src_zephyr_simulation_result_analyzer_py -->|runtime / runtime| src_zephyr_simulation_risk_simulator_py
    src_zephyr_simulation_result_analyzer_py -->|runtime / runtime| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_result_analyzer_py -->|导入依赖 / import_depends| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_scenario_generator_py -->|data / data| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_implementations_default_experiment_pipeline_py -->|导入依赖 / import_depends| src_zephyr_simulation_pipeline_base_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_parameter_robustness_tester_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_sharpe_calculator_fixer_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_look_ahead_bias_detector_py
    tests_simulation_test_look_ahead_bias_detector_py -->|测试依赖 / test_depends| src_zephyr_simulation_look_ahead_bias_detector_py
    tests_simulation_test_deflated_sharpe_calculator_py -->|测试依赖 / test_depends| src_zephyr_simulation_deflated_sharpe_calculator_py
    tests_simulation_test_parameter_robustness_tester_py -->|测试依赖 / test_depends| src_zephyr_simulation_parameter_robustness_tester_py
    tests_simulation_test_risk_simulator_py -->|测试依赖 / test_depends| src_zephyr_simulation_risk_simulator_py
    tests_simulation_test_sharpe_calculator_fixer_py -->|测试依赖 / test_depends| src_zephyr_simulation_sharpe_calculator_fixer_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_simulation_scenario_generator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_result_analyzer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_parameter_robustness_tester_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_look_ahead_bias_detector_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_strategy_simulator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_risk_simulator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_deflated_sharpe_calculator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRASTRUCTURE["跨层契约基础设施<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理<br/>和契约校验<br/>Cross-Layer Contract Infrastructure<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_simulation_pipeline_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_simulation_deflated_sharpe_calculator_py,src_zephyr_simulation_implementations_default_experiment_pipeline_py,src_zephyr_simulation_look_ahead_bias_detector_py,src_zephyr_simulation_parameter_robustness_tester_py,src_zephyr_simulation_pipeline_base_py,src_zephyr_simulation_result_analyzer_py,src_zephyr_simulation_risk_simulator_py,src_zephyr_simulation_scenario_generator_py,src_zephyr_simulation_sharpe_calculator_fixer_py,src_zephyr_simulation_strategy_simulator_py,tests_simulation_test_deflated_sharpe_calculator_py,tests_simulation_test_look_ahead_bias_detector_py,tests_simulation_test_parameter_robustness_tester_py,tests_simulation_test_risk_simulator_py,tests_simulation_test_sharpe_calculator_fixer_py production
    class D_SHARED,D_INFRASTRUCTURE external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 15 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_simulation_implementations_default_experiment_pipeline_py["默认实验管线<br/>simulation implementations<br/>包入口，整合implementations相关子模块导出<br/>default_experiment_pipeline<br/>文件: implementations<br/>/default_experiment_pipeline.py<br/>(生产态 / production)"]
    src_zephyr_simulation_result_analyzer_py["仿真结果分析器<br/>对多个策略仿真结果执行跨场景聚合统计(均值<br/>/标准差/分位数<br/>/置信区间)、收益率分布Jarque-Bera正态性检验和可<br/>视化数据准备,产出含摘要的分析报告<br/>文件: simulation/result_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_scenario_generator_py["场景生成器<br/>给仿真造市场行情的工厂——三种模式:蒙特卡洛用几何<br/>布朗运动随机生成一条价格路径,历史模式从真实数据<br/>切一段下来,自定义模式让你指定在某几根K线上插个涨<br/>跌冲击。跑完吐出一个场景包<br/>(含OHLCV数据+参数快照),喂给策略仿真器看策略在这<br/>种假设行情下会怎样。<br/>Scenario Generator<br/>文件: simulation/scenario_generator.py<br/>(生产态 / production)"]
    tests_simulation_test_deflated_sharpe_calculator_py["simulation/test_deflated_sharpe_calculator<br/>MOD-SIM-024 Deflated Sharpe Ratio Calculator<br/>单元测试.<br/>文件: simulation<br/>/test_deflated_sharpe_calculator.py<br/>(生产态 / production)"]
    tests_simulation_test_look_ahead_bias_detector_py["simulation/test_look_ahead_bias_detector<br/>MOD-SIM-022 Look-Ahead Bias Detector 单元测试.<br/>文件: simulation<br/>/test_look_ahead_bias_detector.py<br/>(生产态 / production)"]
    tests_simulation_test_parameter_robustness_tester_py["simulation/test_parameter_robustness_tester<br/>MOD-SIM-021 Parameter Robustness Tester<br/>单元测试.<br/>文件: simulation<br/>/test_parameter_robustness_tester.py<br/>(生产态 / production)"]
    tests_simulation_test_risk_simulator_py["simulation/test_risk_simulator<br/>MOD-SIM-003 Risk Simulator 单元测试.<br/>文件: simulation/test_risk_simulator.py<br/>(生产态 / production)"]
    tests_simulation_test_sharpe_calculator_fixer_py["simulation/test_sharpe_calculator_fixer<br/>MOD-SIM-023 Sharpe Calculator Fixer 单元测试.<br/>文件: simulation/test_sharpe_calculator_fixer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_implementations_default_experiment_pipeline_py ~~~ src_zephyr_simulation_result_analyzer_py
    src_zephyr_simulation_result_analyzer_py ~~~ src_zephyr_simulation_scenario_generator_py
    src_zephyr_simulation_scenario_generator_py ~~~ tests_simulation_test_deflated_sharpe_calculator_py
    tests_simulation_test_deflated_sharpe_calculator_py ~~~ tests_simulation_test_look_ahead_bias_detector_py
    tests_simulation_test_look_ahead_bias_detector_py ~~~ tests_simulation_test_parameter_robustness_tester_py
    tests_simulation_test_parameter_robustness_tester_py ~~~ tests_simulation_test_risk_simulator_py
    tests_simulation_test_risk_simulator_py ~~~ tests_simulation_test_sharpe_calculator_fixer_py
    src_zephyr_simulation_pipeline_base_py["管线基类<br/>仿真相关功能（pipeline base）<br/>pipeline_base<br/>文件: simulation/pipeline_base.py<br/>(生产态 / production)"]
    src_zephyr_simulation_risk_simulator_py["风控仿真器<br/>给定一段收益率数据,算出最坏情况下可能亏多少<br/>(VaR)和亏的时候平均亏多少<br/>(CVaR),再模拟最大回撤有多大/多久能恢复<br/>/是否触发熔断阈值。纯数学计算,不决定买卖。<br/>Risk Simulator<br/>文件: simulation/risk_simulator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_strategy_simulator_py["策略仿真器<br/>给策略搭一个隔离沙箱——喂进去模拟行情和一个策略函<br/>数,它就逐根K线模拟这个策略会怎么发信号、怎么建仓<br/>、最后赚多少亏多少,跑完吐出净值曲线和交易记录,方<br/>便分析策略在假设行情下表现如何。策略本身由调用方<br/>注入,仿真器只管调度和记账,不掺和策略决策。<br/>Strategy Simulator<br/>文件: simulation/strategy_simulator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_pipeline_base_py ~~~ src_zephyr_simulation_risk_simulator_py
    src_zephyr_simulation_risk_simulator_py ~~~ src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_look_ahead_bias_detector_py["lookaheadbias检测器<br/>模拟的检测器，检测特定模式或异常情况<br/>look_ahead_bias_detector<br/>文件: simulation/look_ahead_bias_detector.py<br/>(生产态 / production)"]
    src_zephyr_simulation_parameter_robustness_tester_py["参数鲁棒性测试器<br/>模拟的测试器，测试验证功能<br/>parameter_robustness_tester<br/>文件: simulation/parameter_robustness_tester.py<br/>(生产态 / production)"]
    src_zephyr_simulation_sharpe_calculator_fixer_py["夏普计算器修复器<br/>模拟的计算器，计算得出结果（sharpe calculator<br/>fixer）<br/>sharpe_calculator_fixer<br/>文件: simulation/sharpe_calculator_fixer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_look_ahead_bias_detector_py ~~~ src_zephyr_simulation_parameter_robustness_tester_py
    src_zephyr_simulation_parameter_robustness_tester_py ~~~ src_zephyr_simulation_sharpe_calculator_fixer_py
    src_zephyr_simulation_deflated_sharpe_calculator_py["缩水夏普计算器<br/>模拟的计算器，计算得出结果（deflated sharpe<br/>calculator）<br/>deflated_sharpe_calculator<br/>文件: simulation/deflated_sharpe_calculator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|导入依赖 / import_depends| src_zephyr_simulation_deflated_sharpe_calculator_py
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|data / data| src_zephyr_simulation_deflated_sharpe_calculator_py
    src_zephyr_simulation_result_analyzer_py -->|runtime / runtime| src_zephyr_simulation_risk_simulator_py
    src_zephyr_simulation_result_analyzer_py -->|runtime / runtime| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_result_analyzer_py -->|导入依赖 / import_depends| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_scenario_generator_py -->|data / data| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_implementations_default_experiment_pipeline_py -->|导入依赖 / import_depends| src_zephyr_simulation_pipeline_base_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_parameter_robustness_tester_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_sharpe_calculator_fixer_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_look_ahead_bias_detector_py
    tests_simulation_test_look_ahead_bias_detector_py -->|测试依赖 / test_depends| src_zephyr_simulation_look_ahead_bias_detector_py
    tests_simulation_test_deflated_sharpe_calculator_py -->|测试依赖 / test_depends| src_zephyr_simulation_deflated_sharpe_calculator_py
    tests_simulation_test_parameter_robustness_tester_py -->|测试依赖 / test_depends| src_zephyr_simulation_parameter_robustness_tester_py
    tests_simulation_test_risk_simulator_py -->|测试依赖 / test_depends| src_zephyr_simulation_risk_simulator_py
    tests_simulation_test_sharpe_calculator_fixer_py -->|测试依赖 / test_depends| src_zephyr_simulation_sharpe_calculator_fixer_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_simulation_deflated_sharpe_calculator_py,src_zephyr_simulation_implementations_default_experiment_pipeline_py,src_zephyr_simulation_look_ahead_bias_detector_py,src_zephyr_simulation_parameter_robustness_tester_py,src_zephyr_simulation_pipeline_base_py,src_zephyr_simulation_result_analyzer_py,src_zephyr_simulation_risk_simulator_py,src_zephyr_simulation_scenario_generator_py,src_zephyr_simulation_sharpe_calculator_fixer_py,src_zephyr_simulation_strategy_simulator_py,tests_simulation_test_deflated_sharpe_calculator_py,tests_simulation_test_look_ahead_bias_detector_py,tests_simulation_test_parameter_robustness_tester_py,tests_simulation_test_risk_simulator_py,tests_simulation_test_sharpe_calculator_fixer_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 管线基类 / pipeline_base (simulation/pipeline_base.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 实验结果 / experiment_result (contracts/experiment_result... | 导入依赖 / import_depends |
| 2 | 缩水夏普计算器 / deflated_sharpe_calculator (simulation/d... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 3 | lookaheadbias检测器 / look_ahead_bias_detector (simulatio... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 4 | 参数鲁棒性测试器 / parameter_robustness_tester (simulatio... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 5 | 仿真结果分析器 (simulation/result_analyzer.py) | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 6 | 风控仿真器 / Risk Simulator (simulation/risk_simulator.py) | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 7 | 场景生成器 / Scenario Generator (simulation/scenario_gene... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 8 | 夏普计算器修复器 / sharpe_calculator_fixer (simulation/sh... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 9 | 策略仿真器 / Strategy Simulator (simulation/strategy_simu... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 2 个外部域直接连接（出边 9 条 + 入边 0 条 = 9 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_SIMULATION["D_SIMULATION<br/>仿真"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_SIMULATION -->|8条 导入依赖 / import_depends| D_SHARED
    D_SIMULATION -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
