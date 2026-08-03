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
    src_zephyr_simulation_implementations_default_experiment_pipeline_py["implementations/default_experiment_pipeline<br/>实验 — Default Experiment Pipeline<br/>文件: implementations<br/>/default_experiment_pipeline.py<br/>(生产态 / production)"]
    src_zephyr_simulation_result_analyzer_py["simulation/result_analyzer<br/>D_SIMULATION — Simulation Result Analyzer<br/>(仿真结果分析器)<br/>文件: simulation/result_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_scenario_generator_py["simulation/scenario_generator<br/>D_SIMULATION — Scenario Generator (场景生成器)<br/>文件: simulation/scenario_generator.py<br/>(生产态 / production)"]
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
    src_zephyr_simulation_pipeline_base_py["simulation/pipeline_base<br/>实验 — Experimentation Pipeline Layer<br/>文件: simulation/pipeline_base.py<br/>(生产态 / production)"]
    src_zephyr_simulation_risk_simulator_py["simulation/risk_simulator<br/>D_SIMULATION — Risk Simulator (风控仿真器)<br/>文件: simulation/risk_simulator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_strategy_simulator_py["simulation/strategy_simulator<br/>D_SIMULATION — Strategy Simulator (策略仿真器<br/>/策略沙箱)<br/>文件: simulation/strategy_simulator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_pipeline_base_py ~~~ src_zephyr_simulation_risk_simulator_py
    src_zephyr_simulation_risk_simulator_py ~~~ src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_look_ahead_bias_detector_py["simulation/look_ahead_bias_detector<br/>D_SIMULATION — Look-Ahead Bias Detector<br/>(未来函数风险检测器)<br/>文件: simulation/look_ahead_bias_detector.py<br/>(生产态 / production)"]
    src_zephyr_simulation_parameter_robustness_tester_py["simulation/parameter_robustness_tester<br/>D_SIMULATION — Parameter Robustness Tester<br/>(参数鲁棒性测试器)<br/>文件: simulation/parameter_robustness_tester.py<br/>(生产态 / production)"]
    src_zephyr_simulation_sharpe_calculator_fixer_py["simulation/sharpe_calculator_fixer<br/>D_SIMULATION — Sharpe Calculator Fixer (Sharpe<br/>计算修正器)<br/>文件: simulation/sharpe_calculator_fixer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_look_ahead_bias_detector_py ~~~ src_zephyr_simulation_parameter_robustness_tester_py
    src_zephyr_simulation_parameter_robustness_tester_py ~~~ src_zephyr_simulation_sharpe_calculator_fixer_py
    src_zephyr_simulation_deflated_sharpe_calculator_py["simulation/deflated_sharpe_calculator<br/>D_SIMULATION — Deflated Sharpe Ratio Calculator<br/>(DSR 计算器)<br/>文件: simulation/deflated_sharpe_calculator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|导入依赖 / import_depends| src_zephyr_simulation_deflated_sharpe_calculator_py
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|data / data| src_zephyr_simulation_deflated_sharpe_calculator_py
    src_zephyr_simulation_result_analyzer_py -->|runtime / runtime| src_zephyr_simulation_risk_simulator_py
    src_zephyr_simulation_result_analyzer_py -->|导入依赖 / import_depends| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_result_analyzer_py -->|runtime / runtime| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_scenario_generator_py -->|data / data| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_parameter_robustness_tester_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_look_ahead_bias_detector_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_sharpe_calculator_fixer_py
    src_zephyr_simulation_implementations_default_experiment_pipeline_py -->|导入依赖 / import_depends| src_zephyr_simulation_pipeline_base_py
    tests_simulation_test_deflated_sharpe_calculator_py -->|测试依赖 / test_depends| src_zephyr_simulation_deflated_sharpe_calculator_py
    tests_simulation_test_look_ahead_bias_detector_py -->|测试依赖 / test_depends| src_zephyr_simulation_look_ahead_bias_detector_py
    tests_simulation_test_parameter_robustness_tester_py -->|测试依赖 / test_depends| src_zephyr_simulation_parameter_robustness_tester_py
    tests_simulation_test_risk_simulator_py -->|测试依赖 / test_depends| src_zephyr_simulation_risk_simulator_py
    tests_simulation_test_sharpe_calculator_fixer_py -->|测试依赖 / test_depends| src_zephyr_simulation_sharpe_calculator_fixer_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_simulation_parameter_robustness_tester_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_deflated_sharpe_calculator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_look_ahead_bias_detector_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_result_analyzer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_risk_simulator_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRASTRUCTURE["跨层契约基础设施<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理<br/>和契约校验<br/>Cross-Layer Contract Infrastructure<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_simulation_pipeline_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_simulation_scenario_generator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_simulation_strategy_simulator_py -->|导入依赖 / import_depends| D_SHARED
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
    src_zephyr_simulation_implementations_default_experiment_pipeline_py["implementations/default_experiment_pipeline<br/>实验 — Default Experiment Pipeline<br/>文件: implementations<br/>/default_experiment_pipeline.py<br/>(生产态 / production)"]
    src_zephyr_simulation_result_analyzer_py["simulation/result_analyzer<br/>D_SIMULATION — Simulation Result Analyzer<br/>(仿真结果分析器)<br/>文件: simulation/result_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_scenario_generator_py["simulation/scenario_generator<br/>D_SIMULATION — Scenario Generator (场景生成器)<br/>文件: simulation/scenario_generator.py<br/>(生产态 / production)"]
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
    src_zephyr_simulation_pipeline_base_py["simulation/pipeline_base<br/>实验 — Experimentation Pipeline Layer<br/>文件: simulation/pipeline_base.py<br/>(生产态 / production)"]
    src_zephyr_simulation_risk_simulator_py["simulation/risk_simulator<br/>D_SIMULATION — Risk Simulator (风控仿真器)<br/>文件: simulation/risk_simulator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_strategy_simulator_py["simulation/strategy_simulator<br/>D_SIMULATION — Strategy Simulator (策略仿真器<br/>/策略沙箱)<br/>文件: simulation/strategy_simulator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_pipeline_base_py ~~~ src_zephyr_simulation_risk_simulator_py
    src_zephyr_simulation_risk_simulator_py ~~~ src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_look_ahead_bias_detector_py["simulation/look_ahead_bias_detector<br/>D_SIMULATION — Look-Ahead Bias Detector<br/>(未来函数风险检测器)<br/>文件: simulation/look_ahead_bias_detector.py<br/>(生产态 / production)"]
    src_zephyr_simulation_parameter_robustness_tester_py["simulation/parameter_robustness_tester<br/>D_SIMULATION — Parameter Robustness Tester<br/>(参数鲁棒性测试器)<br/>文件: simulation/parameter_robustness_tester.py<br/>(生产态 / production)"]
    src_zephyr_simulation_sharpe_calculator_fixer_py["simulation/sharpe_calculator_fixer<br/>D_SIMULATION — Sharpe Calculator Fixer (Sharpe<br/>计算修正器)<br/>文件: simulation/sharpe_calculator_fixer.py<br/>(生产态 / production)"]
    src_zephyr_simulation_look_ahead_bias_detector_py ~~~ src_zephyr_simulation_parameter_robustness_tester_py
    src_zephyr_simulation_parameter_robustness_tester_py ~~~ src_zephyr_simulation_sharpe_calculator_fixer_py
    src_zephyr_simulation_deflated_sharpe_calculator_py["simulation/deflated_sharpe_calculator<br/>D_SIMULATION — Deflated Sharpe Ratio Calculator<br/>(DSR 计算器)<br/>文件: simulation/deflated_sharpe_calculator.py<br/>(生产态 / production)"]
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|导入依赖 / import_depends| src_zephyr_simulation_deflated_sharpe_calculator_py
    src_zephyr_simulation_sharpe_calculator_fixer_py -->|data / data| src_zephyr_simulation_deflated_sharpe_calculator_py
    src_zephyr_simulation_result_analyzer_py -->|runtime / runtime| src_zephyr_simulation_risk_simulator_py
    src_zephyr_simulation_result_analyzer_py -->|导入依赖 / import_depends| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_result_analyzer_py -->|runtime / runtime| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_scenario_generator_py -->|data / data| src_zephyr_simulation_strategy_simulator_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_parameter_robustness_tester_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_look_ahead_bias_detector_py
    src_zephyr_simulation_strategy_simulator_py -->|data / data| src_zephyr_simulation_sharpe_calculator_fixer_py
    src_zephyr_simulation_implementations_default_experiment_pipeline_py -->|导入依赖 / import_depends| src_zephyr_simulation_pipeline_base_py
    tests_simulation_test_deflated_sharpe_calculator_py -->|测试依赖 / test_depends| src_zephyr_simulation_deflated_sharpe_calculator_py
    tests_simulation_test_look_ahead_bias_detector_py -->|测试依赖 / test_depends| src_zephyr_simulation_look_ahead_bias_detector_py
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
| 1 | 实验 — Experimentation Pipeline Layer (simulation/pipeli... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/experiment_result.py | 导入依赖 / import_depends |
| 2 | D_SIMULATION — Deflated Sharpe Ratio Calculator (DSR 计... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 3 | D_SIMULATION — Look-Ahead Bias Detector (未来函数风险检... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 4 | D_SIMULATION — Parameter Robustness Tester (参数鲁棒性测... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 5 | D_SIMULATION — Simulation Result Analyzer (仿真结果分析... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 6 | D_SIMULATION — Risk Simulator (风控仿真器) (simulation/r... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 7 | D_SIMULATION — Scenario Generator (场景生成器) (simulati... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 8 | D_SIMULATION — Sharpe Calculator Fixer (Sharpe 计算修正... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 9 | D_SIMULATION — Strategy Simulator (策略仿真器/策略沙箱) ... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |

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
