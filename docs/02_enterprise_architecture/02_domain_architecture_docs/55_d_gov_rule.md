---
doc_type: architecture_view
title: D_GOV_RULE 规则治理架构文档
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# 55_d_gov_rule / 规则治理 / Rule Governance

> **功能简介 / Overview**: 规则治理，负责规则注册、规则版本和规则依赖管理

> **文档作用 / Purpose**: 展示 规则治理（D_GOV_RULE）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 55 | Number | 55 |
| 域ID | D_GOV_RULE | Domain ID | D_GOV_RULE |
| 域名称 | 规则治理 | Domain Name | Rule Governance |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 35 | Module Count | 35 |
| 域内依赖 | 12 | Internal Dependencies | 12 |
| 跨域入边 | 29 | Cross-domain Incoming | 29 |
| 跨域出边 | 32 | Cross-domain Outgoing | 32 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 35 | Production Modules | 35 |
| 容量 | 35/150 (正常) | Capacity | 35/150 (正常) |
| 描述 | 规则配置管理 | Description | 规则配置管理 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 35 个模块 / 35 modules）。

### L2 领域层 / Domain Layer (35 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | scripts/governance/generators/generate_script_manifest.py | generate_script_manifest.py — 脚本清单自动生成器 | 生产态 / production |  |
| 2 | src/zephyr/gov_enforcement/rule_enforcement/adaptive_thre... | 自适应阈值——双模式：概率型（PASS/FAIL outcome 调节）+ 次数型（EWMA 基线 × ... | 生产态 / production |  |
| 3 | src/zephyr/gov_enforcement/rule_enforcement/adversarial_s... | 对抗样本生成器——5 种攻击策略用于门禁验证（Adversarial sample generator with... | 生产态 / production |  |
| 4 | src/zephyr/gov_enforcement/rule_enforcement/ai_capability... | AI 能力边界守卫——@require_capability 装饰器运行时检查（AI capability bounda... | 生产态 / production |  |
| 5 | src/zephyr/gov_enforcement/rule_enforcement/anti_pattern_... | Anti-Patterns 防护引擎（Anti-Pattern Guard） | 生产态 / production |  |
| 6 | src/zephyr/gov_enforcement/rule_enforcement/can_i_deploy.py | Can-I-Deploy 预部署门禁（GATE-CDC-1） | 生产态 / production |  |
| 7 | src/zephyr/gov_enforcement/rule_enforcement/capability_ch... | 能力检查器（Capability Checker） | 生产态 / production |  |
| 8 | src/zephyr/gov_enforcement/rule_enforcement/cbac_matrix.py | CBAC 能力矩阵（Capability-Based Access Control Matrix — CT-CBAC-001） | 生产态 / production |  |
| 9 | src/zephyr/gov_enforcement/rule_enforcement/cdc_broker.py | CDC 契约经纪人（Consumer-Driven Contract Broker — CT-CDC-001） | 生产态 / production |  |
| 10 | src/zephyr/gov_enforcement/rule_enforcement/circuit_break... | CircuitBreakerGateway (CBG) — 模块间调用单向熔断器 | 生产态 / production |  |
| 11 | src/zephyr/gov_enforcement/rule_enforcement/contract_temp... | 契约模板管理器——管理 MCP 工具契约模板（Contract template manager for MCP to... | 生产态 / production |  |
| 12 | src/zephyr/gov_enforcement/rule_enforcement/end_to_end_wa... | 端到端场景走查验证器（End-to-End Walkthrough Validator）。 | 生产态 / production |  |
| 13 | src/zephyr/gov_enforcement/rule_enforcement/gate_engine/_... | gate_engine package — 门禁引擎模块集合（ARCH-042 阶段1 拆分产物）。 | 生产态 / production |  |
| 14 | src/zephyr/gov_enforcement/rule_enforcement/gate_engine/a... | 对抗验证门禁——验证输出对抗对抗性攻击（AdversarialValidationGate: validates ... | 生产态 / production |  |
| 15 | src/zephyr/gov_enforcement/rule_enforcement/gate_engine/g... | 门禁上下文传播——GateContext 构建/序列化/跨模块注入（beta） | 生产态 / production |  |
| 16 | src/zephyr/gov_enforcement/rule_enforcement/gate_engine/g... | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-G12 门禁裁决引擎（T-2-17） | 生产态 / production |  |
| 17 | src/zephyr/gov_enforcement/rule_enforcement/gate_engine/g... | Owner 紧急旁路——时间限定的门禁临时绕过 + 审计追踪（beta） | 生产态 / production |  |
| 18 | src/zephyr/gov_enforcement/rule_enforcement/gate_engine/g... | 门禁评估管线——排序解析、组合逻辑（AND/OR/NOT）、并行调度（beta） | 生产态 / production |  |
| 19 | src/zephyr/gov_enforcement/rule_enforcement/gate_engine/g... | 门禁模拟器——dry-run 全链路门禁演练，不修改任何状态（beta） | 生产态 / production |  |
| 20 | src/zephyr/gov_enforcement/rule_enforcement/gate_types.py | 门禁类型定义——GateType 枚举与 gate 相关 dataclass（GateContext/GateResult 等）。 | 生产态 / production |  |
| 21 | src/zephyr/gov_enforcement/rule_enforcement/integration_t... | 集成测试运行器（Integration Test Runner） | 生产态 / production |  |
| 22 | src/zephyr/gov_enforcement/rule_enforcement/invariants/en... | EN-001 循环依赖扫描器——Kahn 拓扑排序检测模块导入环（Circular Dependency Sca... | 生产态 / production |  |
| 23 | src/zephyr/gov_enforcement/rule_enforcement/invariants/en... | EN-003 契约兼容性检查器——字段/类型/必填对齐差异比对（Contract Compatibility... | 生产态 / production |  |
| 24 | src/zephyr/gov_enforcement/rule_enforcement/invariants/en... | EN-process-lifecycle-gateway — 进程创建入口校验门禁 | 生产态 / production |  |
| 25 | src/zephyr/gov_enforcement/rule_enforcement/invariants/ze... | 零残留检查器——验证治理操作后无残留文件/目录/引用。 | 生产态 / production |  |
| 26 | src/zephyr/gov_enforcement/rule_enforcement/kiss_enforcer.py | KISS 约束执行器（CT-KISS-001）——AI产出复杂度检测+bloat check。 | 生产态 / production |  |
| 27 | src/zephyr/gov_enforcement/rule_enforcement/risk_ssot.py | risk_ssot — 从 ``config/risk_params.yaml`` 加载风险真源（INV-002 等） | 生产态 / production |  |
| 28 | src/zephyr/gov_enforcement/rule_enforcement/rule_engine/_... | rule_engine package — 规则引擎模块集合（ARCH-042 阶段1 拆分产物）。 | 生产态 / production |  |
| 29 | src/zephyr/gov_enforcement/rule_enforcement/rule_engine/r... | RuleLoader — 规则加载核心 API | 生产态 / production |  |
| 30 | src/zephyr/gov_enforcement/rule_enforcement/secrets_guard.py | Secrets 守护（CT-SECRETS-001）——.env校验+git log扫描+日志脱敏。 | 生产态 / production |  |
| 31 | src/zephyr/gov_enforcement/rule_enforcement/task_completi... | TaskCompletionGate: scan for residual files outside files_in_scope | 生产态 / production |  |
| 32 | src/zephyr/gov_enforcement/rule_enforcement/task_types.py | 任务类型定义——Task model 是任务卡字段的 SSoT（SQLite tasks 表对齐）。 | 生产态 / production |  |
| 33 | src/zephyr/gov_enforcement/rule_enforcement/triple_alignm... | G-TRIPLE-ALIGN: 蓝图↔代码↔依赖图三方对齐门禁 | 生产态 / production |  |
| 34 | src/zephyr/gov_rule/__init__.py | gov_rule domain package — rule governance (D_GOV_RULE). | 生产态 / production |  |
| 35 | src/zephyr/gov_rule/constitutional_update/constitutional_... | constitutional_update.py —— 宪法自愈（Phase 14 | 盲点 B27） | 生产态 / production |  |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分三个视图：合并全景图、运营态子图、设计态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 35 个模块（生产态 35 + 设计态 0），标签标注成熟度。

#### 第 1 页 / 共 2 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_generators_generate_script_manifest_py["(生产态 / production) generate_script_manifest.py — 脚本清单自动生成器<br/>文件: generators/generate_script_manifest.py"]
    src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py["(生产态 / production) 自适应阈值——双模式：概率型（PASS/FAIL outcome 调节）+ 次数型（EWMA 基线 × ...<br/>文件: rule_enforcement/adaptive_threshold.py"]
    src_zephyr_gov_enforcement_rule_enforcement_adversarial_strategies_py["(生产态 / production) 对抗样本生成器——5 种攻击策略用于门禁验证（Adversarial sample generator with...<br/>文件: rule_enforcement/adversarial_strategies.py"]
    src_zephyr_gov_enforcement_rule_enforcement_ai_capability_guard_py["(生产态 / production) AI 能力边界守卫——@require_capability 装饰器运行时检查（AI capability bounda...<br/>文件: rule_enforcement/ai_capability_guard.py"]
    src_zephyr_gov_enforcement_rule_enforcement_anti_pattern_guard_py["(生产态 / production) Anti-Patterns 防护引擎（Anti-Pattern Guard）<br/>文件: rule_enforcement/anti_pattern_guard.py"]
    src_zephyr_gov_enforcement_rule_enforcement_can_i_deploy_py["(生产态 / production) Can-I-Deploy 预部署门禁（GATE-CDC-1）<br/>文件: rule_enforcement/can_i_deploy.py"]
    src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py["(生产态 / production) 能力检查器（Capability Checker）<br/>文件: rule_enforcement/capability_checker.py"]
    src_zephyr_gov_enforcement_rule_enforcement_cdc_broker_py["(生产态 / production) CDC 契约经纪人（Consumer-Driven Contract Broker — CT-CDC-001）<br/>文件: rule_enforcement/cdc_broker.py"]
    src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py["(生产态 / production) 契约模板管理器——管理 MCP 工具契约模板（Contract template manager for MCP to...<br/>文件: rule_enforcement/contract_template_manager.py"]
    src_zephyr_gov_enforcement_rule_enforcement_end_to_end_walkthrough_py["(生产态 / production) 端到端场景走查验证器（End-to-End Walkthrough Validator）。<br/>文件: rule_enforcement/end_to_end_walkthrough.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py["(生产态 / production) gate_engine package — 门禁引擎模块集合（ARCH-042 阶段1 拆分产物）。<br/>文件: gate_engine/__init__.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_adversarial_validation_py["(生产态 / production) 对抗验证门禁——验证输出对抗对抗性攻击（AdversarialValidationGate: validates ...<br/>文件: gate_engine/adversarial_validation.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py["(生产态 / production) GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-G12 门禁裁决引擎（T-2-17）<br/>文件: gate_engine/gate_engine.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py["(生产态 / production) Owner 紧急旁路——时间限定的门禁临时绕过 + 审计追踪（beta）<br/>文件: gate_engine/gate_override.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py["(生产态 / production) 门禁模拟器——dry-run 全链路门禁演练，不修改任何状态（beta）<br/>文件: gate_engine/gate_simulator.py"]
    src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py["(生产态 / production) 集成测试运行器（Integration Test Runner）<br/>文件: rule_enforcement/integration_test_runner.py"]
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_process_lifecycle_gateway_py["(生产态 / production) EN-process-lifecycle-gateway — 进程创建入口校验门禁<br/>文件: invariants/en_process_lifecycle_gateway.py"]
    src_zephyr_gov_enforcement_rule_enforcement_kiss_enforcer_py["(生产态 / production) KISS 约束执行器（CT-KISS-001）——AI产出复杂度检测+bloat check。<br/>文件: rule_enforcement/kiss_enforcer.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_init_py["(生产态 / production) rule_engine package — 规则引擎模块集合（ARCH-042 阶段1 拆分产物）。<br/>文件: rule_engine/__init__.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py["(生产态 / production) RuleLoader — 规则加载核心 API<br/>文件: rule_engine/rule_engine.py"]
    src_zephyr_gov_enforcement_rule_enforcement_secrets_guard_py["(生产态 / production) Secrets 守护（CT-SECRETS-001）——.env校验+git log扫描+日志脱敏。<br/>文件: rule_enforcement/secrets_guard.py"]
    scripts_governance_generators_generate_script_manifest_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py
    src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_adversarial_strategies_py
    src_zephyr_gov_enforcement_rule_enforcement_adversarial_strategies_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_ai_capability_guard_py
    src_zephyr_gov_enforcement_rule_enforcement_ai_capability_guard_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_anti_pattern_guard_py
    src_zephyr_gov_enforcement_rule_enforcement_anti_pattern_guard_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_can_i_deploy_py
    src_zephyr_gov_enforcement_rule_enforcement_can_i_deploy_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py
    src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_cdc_broker_py
    src_zephyr_gov_enforcement_rule_enforcement_cdc_broker_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py
    src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_end_to_end_walkthrough_py
    src_zephyr_gov_enforcement_rule_enforcement_end_to_end_walkthrough_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_adversarial_validation_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_adversarial_validation_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py
    src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_invariants_en_process_lifecycle_gateway_py
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_process_lifecycle_gateway_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_kiss_enforcer_py
    src_zephyr_gov_enforcement_rule_enforcement_kiss_enforcer_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_init_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_init_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_secrets_guard_py
    src_zephyr_gov_enforcement_rule_enforcement_cbac_matrix_py["(生产态 / production) CBAC 能力矩阵（Capability-Based Access Control Matrix — CT-CBAC-001）<br/>文件: rule_enforcement/cbac_matrix.py"]
    src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py["(生产态 / production) CircuitBreakerGateway (CBG) — 模块间调用单向熔断器<br/>文件: rule_enforcement/circuit_breaker.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py["(生产态 / production) 门禁评估管线——排序解析、组合逻辑（AND/OR/NOT）、并行调度（beta）<br/>文件: gate_engine/gate_pipeline.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_types_py["(生产态 / production) 门禁类型定义——GateType 枚举与 gate 相关 dataclass（GateContext/GateResult 等）。<br/>文件: rule_enforcement/gate_types.py"]
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py["(生产态 / production) EN-001 循环依赖扫描器——Kahn 拓扑排序检测模块导入环（Circular Dependency Sca...<br/>文件: invariants/en_001_circular_dependency.py"]
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py["(生产态 / production) EN-003 契约兼容性检查器——字段/类型/必填对齐差异比对（Contract Compatibility...<br/>文件: invariants/en_003_contract_compatibility.py"]
    src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py["(生产态 / production) 零残留检查器——验证治理操作后无残留文件/目录/引用。<br/>文件: invariants/zero_residue_check.py"]
    src_zephyr_gov_enforcement_rule_enforcement_risk_ssot_py["(生产态 / production) risk_ssot — 从 ``config/risk_params.yaml`` 加载风险真源（INV-002 等）<br/>文件: rule_enforcement/risk_ssot.py"]
    src_zephyr_gov_enforcement_rule_enforcement_cbac_matrix_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py
    src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_types_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py
    src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_risk_ssot_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py["(生产态 / production) 门禁上下文传播——GateContext 构建/序列化/跨模块注入（beta）<br/>文件: gate_engine/gate_context.py"]
    src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_cbac_matrix_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_risk_ssot_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py -->|config_depends / config_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT 审计追踪"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE 生命周期管理"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_SHARED["(生产态 / production) D_SHARED 共享服务"]
    src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_DRIFT["(生产态 / production) D_GOV_DRIFT 漂移检测"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RECOVERY["(生产态 / production) D_INFRA_RECOVERY 回滚恢复"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_INFRA_RECOVERY
    src_zephyr_gov_enforcement_rule_enforcement_gate_types_py -->|导入依赖 / import_depends| D_SHARED
    D_INTELLIGENCE["(生产态 / production) D_INTELLIGENCE 上下文管理"]
    D_INTELLIGENCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    D_GOV_SCRIPTS["(生产态 / production) D_GOV_SCRIPTS 脚本治理"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    D_GOV_AUDIT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION 管线路由"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    D_SECURITY["(生产态 / production) D_SECURITY 对抗验证"]
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    D_GOV_OPS_RESILIENCE["(生产态 / production) D_GOV_OPS_RESILIENCE 运维弹性治理"]
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE 自治核心"]
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class scripts_governance_generators_generate_script_manifest_py,src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py,src_zephyr_gov_enforcement_rule_enforcement_adversarial_strategies_py,src_zephyr_gov_enforcement_rule_enforcement_ai_capability_guard_py,src_zephyr_gov_enforcement_rule_enforcement_anti_pattern_guard_py,src_zephyr_gov_enforcement_rule_enforcement_can_i_deploy_py,src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py,src_zephyr_gov_enforcement_rule_enforcement_cbac_matrix_py,src_zephyr_gov_enforcement_rule_enforcement_cdc_broker_py,src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py,src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py,src_zephyr_gov_enforcement_rule_enforcement_end_to_end_walkthrough_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_adversarial_validation_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py,src_zephyr_gov_enforcement_rule_enforcement_gate_types_py,src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py,src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py,src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py,src_zephyr_gov_enforcement_rule_enforcement_invariants_en_process_lifecycle_gateway_py,src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py,src_zephyr_gov_enforcement_rule_enforcement_kiss_enforcer_py,src_zephyr_gov_enforcement_rule_enforcement_risk_ssot_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_init_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py,src_zephyr_gov_enforcement_rule_enforcement_secrets_guard_py production
    class D_GOV_AUDIT,D_GOVERNANCE,D_SHARED,D_GOV_DRIFT,D_INFRA_RECOVERY,D_INTELLIGENCE,D_GOV_SCRIPTS,D_INTEGRATION,D_SECURITY,D_GOV_OPS_RESILIENCE,D_AUTONOMY_CORE external_prod
```

#### 第 2 页 / 共 2 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_gov_enforcement_rule_enforcement_task_completion_gate_py["(生产态 / production) TaskCompletionGate: scan for residual files outside files_in_scope<br/>文件: rule_enforcement/task_completion_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_task_types_py["(生产态 / production) 任务类型定义——Task model 是任务卡字段的 SSoT（SQLite tasks 表对齐）。<br/>文件: rule_enforcement/task_types.py"]
    src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py["(生产态 / production) G-TRIPLE-ALIGN: 蓝图↔代码↔依赖图三方对齐门禁<br/>文件: rule_enforcement/triple_alignment.py"]
    src_zephyr_gov_rule_init_py["(生产态 / production) gov_rule domain package — rule governance (D_GOV_RULE).<br/>文件: gov_rule/__init__.py"]
    src_zephyr_gov_rule_constitutional_update_constitutional_update_py["(生产态 / production) constitutional_update.py —— 宪法自愈（Phase 14 / 盲点 B27）<br/>文件: constitutional_update/constitutional_update.py"]
    src_zephyr_gov_enforcement_rule_enforcement_task_completion_gate_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    src_zephyr_gov_enforcement_rule_enforcement_task_types_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py
    src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py ~~~ src_zephyr_gov_rule_init_py
    src_zephyr_gov_rule_init_py ~~~ src_zephyr_gov_rule_constitutional_update_constitutional_update_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME 运行时集成"]
    src_zephyr_gov_enforcement_rule_enforcement_task_completion_gate_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SHARED["(生产态 / production) D_SHARED 共享服务"]
    src_zephyr_gov_enforcement_rule_enforcement_task_types_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_rule_constitutional_update_constitutional_update_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_rule_constitutional_update_constitutional_update_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE 生命周期管理"]
    src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_task_types_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_task_types_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION 管线路由"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_GOV_SCRIPTS["(生产态 / production) D_GOV_SCRIPTS 脚本治理"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py
    D_SECURITY["(生产态 / production) D_SECURITY 对抗验证"]
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_SHARED -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_gov_enforcement_rule_enforcement_task_completion_gate_py,src_zephyr_gov_enforcement_rule_enforcement_task_types_py,src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py,src_zephyr_gov_rule_init_py,src_zephyr_gov_rule_constitutional_update_constitutional_update_py production
    class D_INFRA_RUNTIME,D_SHARED,D_GOVERNANCE,D_INTEGRATION,D_GOV_SCRIPTS,D_SECURITY external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 35 个，12 条域内依赖）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_generators_generate_script_manifest_py["(生产态 / production) generate_script_manifest.py — 脚本清单自动生成器<br/>文件: generators/generate_script_manifest.py"]
    src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py["(生产态 / production) 自适应阈值——双模式：概率型（PASS/FAIL outcome 调节）+ 次数型（EWMA 基线 × ...<br/>文件: rule_enforcement/adaptive_threshold.py"]
    src_zephyr_gov_enforcement_rule_enforcement_adversarial_strategies_py["(生产态 / production) 对抗样本生成器——5 种攻击策略用于门禁验证（Adversarial sample generator with...<br/>文件: rule_enforcement/adversarial_strategies.py"]
    src_zephyr_gov_enforcement_rule_enforcement_ai_capability_guard_py["(生产态 / production) AI 能力边界守卫——@require_capability 装饰器运行时检查（AI capability bounda...<br/>文件: rule_enforcement/ai_capability_guard.py"]
    src_zephyr_gov_enforcement_rule_enforcement_anti_pattern_guard_py["(生产态 / production) Anti-Patterns 防护引擎（Anti-Pattern Guard）<br/>文件: rule_enforcement/anti_pattern_guard.py"]
    src_zephyr_gov_enforcement_rule_enforcement_can_i_deploy_py["(生产态 / production) Can-I-Deploy 预部署门禁（GATE-CDC-1）<br/>文件: rule_enforcement/can_i_deploy.py"]
    src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py["(生产态 / production) 能力检查器（Capability Checker）<br/>文件: rule_enforcement/capability_checker.py"]
    src_zephyr_gov_enforcement_rule_enforcement_cdc_broker_py["(生产态 / production) CDC 契约经纪人（Consumer-Driven Contract Broker — CT-CDC-001）<br/>文件: rule_enforcement/cdc_broker.py"]
    src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py["(生产态 / production) 契约模板管理器——管理 MCP 工具契约模板（Contract template manager for MCP to...<br/>文件: rule_enforcement/contract_template_manager.py"]
    src_zephyr_gov_enforcement_rule_enforcement_end_to_end_walkthrough_py["(生产态 / production) 端到端场景走查验证器（End-to-End Walkthrough Validator）。<br/>文件: rule_enforcement/end_to_end_walkthrough.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py["(生产态 / production) gate_engine package — 门禁引擎模块集合（ARCH-042 阶段1 拆分产物）。<br/>文件: gate_engine/__init__.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_adversarial_validation_py["(生产态 / production) 对抗验证门禁——验证输出对抗对抗性攻击（AdversarialValidationGate: validates ...<br/>文件: gate_engine/adversarial_validation.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py["(生产态 / production) GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-G12 门禁裁决引擎（T-2-17）<br/>文件: gate_engine/gate_engine.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py["(生产态 / production) Owner 紧急旁路——时间限定的门禁临时绕过 + 审计追踪（beta）<br/>文件: gate_engine/gate_override.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py["(生产态 / production) 门禁模拟器——dry-run 全链路门禁演练，不修改任何状态（beta）<br/>文件: gate_engine/gate_simulator.py"]
    src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py["(生产态 / production) 集成测试运行器（Integration Test Runner）<br/>文件: rule_enforcement/integration_test_runner.py"]
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_process_lifecycle_gateway_py["(生产态 / production) EN-process-lifecycle-gateway — 进程创建入口校验门禁<br/>文件: invariants/en_process_lifecycle_gateway.py"]
    src_zephyr_gov_enforcement_rule_enforcement_kiss_enforcer_py["(生产态 / production) KISS 约束执行器（CT-KISS-001）——AI产出复杂度检测+bloat check。<br/>文件: rule_enforcement/kiss_enforcer.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_init_py["(生产态 / production) rule_engine package — 规则引擎模块集合（ARCH-042 阶段1 拆分产物）。<br/>文件: rule_engine/__init__.py"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py["(生产态 / production) RuleLoader — 规则加载核心 API<br/>文件: rule_engine/rule_engine.py"]
    src_zephyr_gov_enforcement_rule_enforcement_secrets_guard_py["(生产态 / production) Secrets 守护（CT-SECRETS-001）——.env校验+git log扫描+日志脱敏。<br/>文件: rule_enforcement/secrets_guard.py"]
    src_zephyr_gov_enforcement_rule_enforcement_task_completion_gate_py["(生产态 / production) TaskCompletionGate: scan for residual files outside files_in_scope<br/>文件: rule_enforcement/task_completion_gate.py"]
    src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py["(生产态 / production) G-TRIPLE-ALIGN: 蓝图↔代码↔依赖图三方对齐门禁<br/>文件: rule_enforcement/triple_alignment.py"]
    src_zephyr_gov_rule_init_py["(生产态 / production) gov_rule domain package — rule governance (D_GOV_RULE).<br/>文件: gov_rule/__init__.py"]
    src_zephyr_gov_rule_constitutional_update_constitutional_update_py["(生产态 / production) constitutional_update.py —— 宪法自愈（Phase 14 / 盲点 B27）<br/>文件: constitutional_update/constitutional_update.py"]
    scripts_governance_generators_generate_script_manifest_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py
    src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_adversarial_strategies_py
    src_zephyr_gov_enforcement_rule_enforcement_adversarial_strategies_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_ai_capability_guard_py
    src_zephyr_gov_enforcement_rule_enforcement_ai_capability_guard_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_anti_pattern_guard_py
    src_zephyr_gov_enforcement_rule_enforcement_anti_pattern_guard_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_can_i_deploy_py
    src_zephyr_gov_enforcement_rule_enforcement_can_i_deploy_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py
    src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_cdc_broker_py
    src_zephyr_gov_enforcement_rule_enforcement_cdc_broker_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py
    src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_end_to_end_walkthrough_py
    src_zephyr_gov_enforcement_rule_enforcement_end_to_end_walkthrough_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_adversarial_validation_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_adversarial_validation_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py
    src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_invariants_en_process_lifecycle_gateway_py
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_process_lifecycle_gateway_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_kiss_enforcer_py
    src_zephyr_gov_enforcement_rule_enforcement_kiss_enforcer_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_init_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_init_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_secrets_guard_py
    src_zephyr_gov_enforcement_rule_enforcement_secrets_guard_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_task_completion_gate_py
    src_zephyr_gov_enforcement_rule_enforcement_task_completion_gate_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py
    src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py ~~~ src_zephyr_gov_rule_init_py
    src_zephyr_gov_rule_init_py ~~~ src_zephyr_gov_rule_constitutional_update_constitutional_update_py
    src_zephyr_gov_enforcement_rule_enforcement_cbac_matrix_py["(生产态 / production) CBAC 能力矩阵（Capability-Based Access Control Matrix — CT-CBAC-001）<br/>文件: rule_enforcement/cbac_matrix.py"]
    src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py["(生产态 / production) CircuitBreakerGateway (CBG) — 模块间调用单向熔断器<br/>文件: rule_enforcement/circuit_breaker.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py["(生产态 / production) 门禁评估管线——排序解析、组合逻辑（AND/OR/NOT）、并行调度（beta）<br/>文件: gate_engine/gate_pipeline.py"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_types_py["(生产态 / production) 门禁类型定义——GateType 枚举与 gate 相关 dataclass（GateContext/GateResult 等）。<br/>文件: rule_enforcement/gate_types.py"]
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py["(生产态 / production) EN-001 循环依赖扫描器——Kahn 拓扑排序检测模块导入环（Circular Dependency Sca...<br/>文件: invariants/en_001_circular_dependency.py"]
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py["(生产态 / production) EN-003 契约兼容性检查器——字段/类型/必填对齐差异比对（Contract Compatibility...<br/>文件: invariants/en_003_contract_compatibility.py"]
    src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py["(生产态 / production) 零残留检查器——验证治理操作后无残留文件/目录/引用。<br/>文件: invariants/zero_residue_check.py"]
    src_zephyr_gov_enforcement_rule_enforcement_risk_ssot_py["(生产态 / production) risk_ssot — 从 ``config/risk_params.yaml`` 加载风险真源（INV-002 等）<br/>文件: rule_enforcement/risk_ssot.py"]
    src_zephyr_gov_enforcement_rule_enforcement_task_types_py["(生产态 / production) 任务类型定义——Task model 是任务卡字段的 SSoT（SQLite tasks 表对齐）。<br/>文件: rule_enforcement/task_types.py"]
    src_zephyr_gov_enforcement_rule_enforcement_cbac_matrix_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py
    src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_types_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py
    src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py
    src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_risk_ssot_py
    src_zephyr_gov_enforcement_rule_enforcement_risk_ssot_py ~~~ src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py["(生产态 / production) 门禁上下文传播——GateContext 构建/序列化/跨模块注入（beta）<br/>文件: gate_engine/gate_context.py"]
    src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_cbac_matrix_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_risk_ssot_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py -->|config_depends / config_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT 审计追踪"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE 生命周期管理"]
    src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_SHARED["(生产态 / production) D_SHARED 共享服务"]
    src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME 运行时集成"]
    src_zephyr_gov_enforcement_rule_enforcement_task_completion_gate_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_task_types_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_rule_constitutional_update_constitutional_update_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_DRIFT["(生产态 / production) D_GOV_DRIFT 漂移检测"]
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    D_INTELLIGENCE["(生产态 / production) D_INTELLIGENCE 上下文管理"]
    D_INTELLIGENCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_GOV_SCRIPTS["(生产态 / production) D_GOV_SCRIPTS 脚本治理"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION 管线路由"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    D_GOV_AUDIT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py
    D_SECURITY["(生产态 / production) D_SECURITY 对抗验证"]
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_types_py
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_task_types_py
    D_GOV_OPS_RESILIENCE["(生产态 / production) D_GOV_OPS_RESILIENCE 运维弹性治理"]
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE 自治核心"]
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class scripts_governance_generators_generate_script_manifest_py,src_zephyr_gov_enforcement_rule_enforcement_adaptive_threshold_py,src_zephyr_gov_enforcement_rule_enforcement_adversarial_strategies_py,src_zephyr_gov_enforcement_rule_enforcement_ai_capability_guard_py,src_zephyr_gov_enforcement_rule_enforcement_anti_pattern_guard_py,src_zephyr_gov_enforcement_rule_enforcement_can_i_deploy_py,src_zephyr_gov_enforcement_rule_enforcement_capability_checker_py,src_zephyr_gov_enforcement_rule_enforcement_cbac_matrix_py,src_zephyr_gov_enforcement_rule_enforcement_cdc_broker_py,src_zephyr_gov_enforcement_rule_enforcement_circuit_breaker_py,src_zephyr_gov_enforcement_rule_enforcement_contract_template_manager_py,src_zephyr_gov_enforcement_rule_enforcement_end_to_end_walkthrough_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_init_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_adversarial_validation_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_context_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_engine_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_override_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_pipeline_py,src_zephyr_gov_enforcement_rule_enforcement_gate_engine_gate_simulator_py,src_zephyr_gov_enforcement_rule_enforcement_gate_types_py,src_zephyr_gov_enforcement_rule_enforcement_integration_test_runner_py,src_zephyr_gov_enforcement_rule_enforcement_invariants_en_001_circular_dependency_py,src_zephyr_gov_enforcement_rule_enforcement_invariants_en_003_contract_compatibility_py,src_zephyr_gov_enforcement_rule_enforcement_invariants_en_process_lifecycle_gateway_py,src_zephyr_gov_enforcement_rule_enforcement_invariants_zero_residue_check_py,src_zephyr_gov_enforcement_rule_enforcement_kiss_enforcer_py,src_zephyr_gov_enforcement_rule_enforcement_risk_ssot_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_init_py,src_zephyr_gov_enforcement_rule_enforcement_rule_engine_rule_engine_py,src_zephyr_gov_enforcement_rule_enforcement_secrets_guard_py,src_zephyr_gov_enforcement_rule_enforcement_task_completion_gate_py,src_zephyr_gov_enforcement_rule_enforcement_task_types_py,src_zephyr_gov_enforcement_rule_enforcement_triple_alignment_py,src_zephyr_gov_rule_init_py,src_zephyr_gov_rule_constitutional_update_constitutional_update_py production
    class D_GOV_AUDIT,D_GOVERNANCE,D_SHARED,D_INFRA_RUNTIME,D_GOV_DRIFT,D_INTELLIGENCE,D_GOV_SCRIPTS,D_INTEGRATION,D_SECURITY,D_GOV_OPS_RESILIENCE,D_AUTONOMY_CORE external_prod
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | RuleLoader — 规则加载核心 API (rule_engine/rul... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (governanc... | 导入依赖 / import_depends |
| 2 | RuleLoader — 规则加载核心 API (rule_engine/rul... | → | D_GOVERNANCE 生命周期管理: pg_wrapper.py — psycopg2 connection 的 sqlite3... | 导入依赖 / import_depends |
| 3 | G-TRIPLE-ALIGN: 蓝图↔代码↔依赖图三方对齐门禁 ... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (governanc... | 导入依赖 / import_depends |
| 4 | 能力检查器（Capability Checker） (rule_enforcem... | → | D_GOV_AUDIT 审计追踪: gov_audit/bridge.py | 导入依赖 / import_depends |
| 5 | Owner 紧急旁路——时间限定的门禁临时绕过 + 审计... | → | D_GOV_AUDIT 审计追踪: gov_audit/bridge.py | 导入依赖 / import_depends |
| 6 | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | → | D_GOV_DRIFT 漂移检测: Drift Detector 基础设施 — drift_infrastructure... | 导入依赖 / import_depends |
| 7 | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | → | D_GOV_DRIFT 漂移检测: EN-002 — Enforcement Mode Validator (invariant... | 导入依赖 / import_depends |
| 8 | rule_engine package — 规则引擎模块集合（ARCH-0... | → | D_GOV_ENFORCEMENT 规则执行: Rule Canary Manager — v0.10.0 规则金丝雀: 1%用... | config_depends / config_depends |
| 9 | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | → | D_INFRA_RECOVERY 回滚恢复: CT-RBK-GATE-001 集成契约落地——Rollback System... | 导入依赖 / import_depends |
| 10 | TaskCompletionGate: scan for residual files out... | → | D_INFRA_RUNTIME 运行时集成: Task Lifecycle Manager — G0-G7 任务生命周期门... | 导入依赖 / import_depends |
| 11 | AI 能力边界守卫——@require_capability 装饰器运... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 12 | CircuitBreakerGateway (CBG) — 模块间调用单向熔... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 13 | CircuitBreakerGateway (CBG) — 模块间调用单向熔... | → | D_SHARED 共享服务: CBAC 能力检查器 (Capability-Based Access Contro... | 导入依赖 / import_depends |
| 14 | CircuitBreakerGateway (CBG) — 模块间调用单向熔... | → | D_SHARED 共享服务: db_utils.py — SQLite 连接公共 API（SSoT: zephy... | 导入依赖 / import_depends |
| 15 | 契约模板管理器——管理 MCP 工具契约模板（Contra... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 16 | 契约模板管理器——管理 MCP 工具契约模板（Contra... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 17 | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | → | D_SHARED 共享服务: io_cache.py - File-level I/O cache with LRU evi... | 导入依赖 / import_depends |
| 18 | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 19 | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | → | D_SHARED 共享服务: db_utils.py — SQLite 连接公共 API（SSoT: zephy... | 导入依赖 / import_depends |
| 20 | 门禁类型定义——GateType 枚举与 gate 相关 datac... | → | D_SHARED 共享服务: schema/schemas.py | 导入依赖 / import_depends |
| 21 | 集成测试运行器（Integration Test Runner） (rule... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 22 | EN-001 循环依赖扫描器——Kahn 拓扑排序检测模块... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 23 | EN-003 契约兼容性检查器——字段/类型/必填对齐差... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 24 | EN-process-lifecycle-gateway — 进程创建入口校... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 25 | 零残留检查器——验证治理操作后无残留文件/目录/... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 26 | 零残留检查器——验证治理操作后无残留文件/目录/... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 27 | 任务类型定义——Task model 是任务卡字段的 SSoT... | → | D_SHARED 共享服务: schema/base_config.py | 导入依赖 / import_depends |
| 28 | 任务类型定义——Task model 是任务卡字段的 SSoT... | → | D_SHARED 共享服务: schema/execution_model.py | 导入依赖 / import_depends |
| 29 | 任务类型定义——Task model 是任务卡字段的 SSoT... | → | D_SHARED 共享服务: schema/severity_types.py | 导入依赖 / import_depends |
| 30 | G-TRIPLE-ALIGN: 蓝图↔代码↔依赖图三方对齐门禁 ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 31 | constitutional_update.py —— 宪法自愈（Phase 1... | → | D_SHARED 共享服务: file_utils.py —— 安全文件操作工具（Phase 3 新... | 导入依赖 / import_depends |
| 32 | constitutional_update.py —— 宪法自愈（Phase 1... | → | D_SHARED 共享服务: session_audit.py —— Session 审计轨迹（Phase 1... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: skills/skill_executor.py | → | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 2 | D_GOVERNANCE 生命周期管理: transition — 状态机转换 Mixin（从 task_repo.py... | → | 门禁类型定义——GateType 枚举与 gate 相关 datac... | 导入依赖 / import_depends |
| 3 | D_GOVERNANCE 生命周期管理: transition — 状态机转换 Mixin（从 task_repo.py... | → | 任务类型定义——Task model 是任务卡字段的 SSoT... | 导入依赖 / import_depends |
| 4 | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1... | → | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1... | → | 门禁类型定义——GateType 枚举与 gate 相关 datac... | 导入依赖 / import_depends |
| 6 | D_GOV_AUDIT 审计追踪: 审计链验证工具——独立重放门禁判定+Hash链完整性... | → | 门禁上下文传播——GateContext 构建/序列化/跨模... | 导入依赖 / import_depends |
| 7 | D_GOV_AUDIT 审计追踪: commit_gateway_abuse_monitor_reconciler.py — c... | → | 自适应阈值——双模式：概率型（PASS/FAIL outcome... | 导入依赖 / import_depends |
| 8 | D_GOV_AUDIT 审计追踪: test_p3_integration_smoke.py — Phase 3 全链路... | → | 自适应阈值——双模式：概率型（PASS/FAIL outcome... | 测试依赖 / test_depends |
| 9 | D_GOV_OPS_RESILIENCE 运维弹性治理: G2 Triage 门禁 — 知识分类评分（T-2-13-B） (esc... | → | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 10 | D_GOV_OPS_RESILIENCE 运维弹性治理: G2 Triage 门禁 — 知识分类评分（T-2-13-B） (esc... | → | 门禁类型定义——GateType 枚举与 gate 相关 datac... | 导入依赖 / import_depends |
| 11 | D_GOV_SCRIPTS 脚本治理: CBG 熔断器重置 CLI (CircuitBreakerGateway Reset... | → | CircuitBreakerGateway (CBG) — 模块间调用单向熔... | 导入依赖 / import_depends |
| 12 | D_GOV_SCRIPTS 脚本治理: CBG 熔断器重置 CLI (CircuitBreakerGateway Reset... | → | CircuitBreakerGateway (CBG) — 模块间调用单向熔... | 导入依赖 / import_depends |
| 13 | D_GOV_SCRIPTS 脚本治理: create_task_from_finding.py — Finding → 任务... | → | 任务类型定义——Task model 是任务卡字段的 SSoT... | 导入依赖 / import_depends |
| 14 | D_GOV_SCRIPTS 脚本治理: Gate Engine Bootstrap Self-Check — Quis custod... | → | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 15 | D_GOV_SCRIPTS 脚本治理: validate_gate_engine_external.py — Gate Engine... | → | CircuitBreakerGateway (CBG) — 模块间调用单向熔... | 导入依赖 / import_depends |
| 16 | D_GOV_SCRIPTS 脚本治理: validate_gate_engine_external.py — Gate Engine... | → | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 17 | D_INFRA_RUNTIME 运行时集成: Task Lifecycle Manager — G0-G7 任务生命周期门... | → | 任务类型定义——Task model 是任务卡字段的 SSoT... | 导入依赖 / import_depends |
| 18 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | G-TRIPLE-ALIGN: 蓝图↔代码↔依赖图三方对齐门禁 ... | 导入依赖 / import_depends |
| 19 | D_INFRA_RUNTIME 运行时集成: trading/boot_hooks.py | → | G-TRIPLE-ALIGN: 蓝图↔代码↔依赖图三方对齐门禁 ... | 导入依赖 / import_depends |
| 20 | D_INFRA_RUNTIME 运行时集成: trading/work_orchestrator.py | → | 任务类型定义——Task model 是任务卡字段的 SSoT... | 导入依赖 / import_depends |
| 21 | D_INTEGRATION 管线路由: ZephyrAlpha MCP Task Manager Server (mcp/task_m... | → | 任务类型定义——Task model 是任务卡字段的 SSoT... | 导入依赖 / import_depends |
| 22 | D_INTEGRATION 管线路由: Structural Protocol interfaces for cross-module... | → | 门禁类型定义——GateType 枚举与 gate 相关 datac... | 导入依赖 / import_depends |
| 23 | D_INTELLIGENCE 上下文管理: G4 Activate 门禁 — 人工激活（T-2-13-D） (model... | → | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 24 | D_INTELLIGENCE 上下文管理: G4 Activate 门禁 — 人工激活（T-2-13-D） (model... | → | 门禁类型定义——GateType 枚举与 gate 相关 datac... | 导入依赖 / import_depends |
| 25 | D_SECURITY 对抗验证: orphan_judge/judge.py | → | 门禁类型定义——GateType 枚举与 gate 相关 datac... | 导入依赖 / import_depends |
| 26 | D_SECURITY 对抗验证: adversarial_validation/constitution_guard.py | → | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 27 | D_SECURITY 对抗验证: adversarial_validation/defense_runner.py | → | GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 28 | D_SECURITY 对抗验证: adversarial_validation/defense_runner.py | → | 任务类型定义——Task model 是任务卡字段的 SSoT... | 导入依赖 / import_depends |
| 29 | D_SHARED 共享服务: A2A Coordination — shared interface definition... | → | 任务类型定义——Task model 是任务卡字段的 SSoT... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 13 个外部域直接连接（出边 32 条 + 入边 29 条 = 61 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_GOV_RULE -->|22条 导入依赖 / import_depends| D_SHARED
    D_GOV_RULE -->|3条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_RULE -->|2条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_RULE -->|2条 导入依赖 / import_depends| D_GOV_DRIFT
    D_GOV_RULE -->|1条 config_depends / config_depends| D_GOV_ENFORCEMENT
    D_GOV_RULE -->|1条 导入依赖 / import_depends| D_INFRA_RECOVERY
    D_GOV_RULE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_SCRIPTS -->|6条 导入依赖 / import_depends| D_GOV_RULE
    D_GOVERNANCE -->|4条 导入依赖 / import_depends| D_GOV_RULE
    D_SECURITY -->|4条 导入依赖 / import_depends| D_GOV_RULE
    D_INFRA_RUNTIME -->|4条 导入依赖 / import_depends| D_GOV_RULE
    D_GOV_AUDIT -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_RULE
    D_INTELLIGENCE -->|2条 导入依赖 / import_depends| D_GOV_RULE
    D_INTEGRATION -->|2条 导入依赖 / import_depends| D_GOV_RULE
    D_GOV_OPS_RESILIENCE -->|2条 导入依赖 / import_depends| D_GOV_RULE
    D_SHARED -->|1条 导入依赖 / import_depends| D_GOV_RULE
    D_AUTONOMY_CORE -->|1条 导入依赖 / import_depends| D_GOV_RULE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
