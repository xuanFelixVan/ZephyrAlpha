---
doc_type: architecture_view
title: D_GOVERNANCE 生命周期管理架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 49_d_governance / 生命周期管理域 / Lifecycle Management

> **功能简介 / Overview**: 生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理

> **文档作用 / Purpose**: 展示 生命周期管理（D_GOVERNANCE）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/49_d_governance.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 49 | Number | 49 |
| 域ID | D_GOVERNANCE | Domain ID | D_GOVERNANCE |
| 域名称 | 生命周期管理 | Domain Name | Lifecycle Management |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 224 | Module Count | 224 |
| 域内依赖 | 47 | Internal Dependencies | 47 |
| 跨域入边 | 144 | Cross-domain Incoming | 144 |
| 跨域出边 | 207 | Cross-domain Outgoing | 207 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 224 | Production Modules | 224 |
| 容量 | 224/150 (超容) | Capacity | 224/150 (超容) |
| 描述 | 注册表总索引(registry_of_registries) | Description | 注册表总索引(registry_of_registries) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 224 个模块（生产态 224 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_rule_registry_collection_yaml["规则注册表收集<br/>catalogs包的rule_registry_collection模块<br/>文件: catalogs/rule_registry_collection.yaml<br/>(生产态 / production)"]
    scripts_a2a_full_verification_py["A2Afull验证<br/>A2A Protocol 全链路满分验证脚本<br/>a2a_full_verification<br/>文件: scripts/a2a_full_verification.py<br/>(生产态 / production)"]
    scripts_arch_guard_tools_build_ocp_manifest_py["buildocp清单<br/>从 cross_layer_contracts.yaml 生成 OCP<br/>冻结契约指纹（INV-009）。<br/>build_ocp_manifest<br/>文件: _tools/build_ocp_manifest.py<br/>(生产态 / production)"]
    scripts_arch_guard_tools_inject_idempotency_py["inject幂等性<br/>为所有 P0/P1 契约添加 idempotency_key<br/>字段——状态感知版本。<br/>inject_idempotency<br/>文件: _tools/inject_idempotency.py<br/>(生产态 / production)"]
    scripts_arch_guard_tools_patch_p1_paths_py["补丁p1paths<br/>一次性工具——为 9 个 P1 契约补齐 physical_path<br/>并运行 codegen。<br/>patch_p1_paths<br/>文件: _tools/patch_p1_paths.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_acl_boundary_py["检查aclboundary<br/>Broker ACL 边界强制执行<br/>check_acl_boundary<br/>文件: arch_guard/check_acl_boundary.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_cross_plane_communication_py["check跨planecommunication<br/>INV-011 拓扑 + 静态越界 import 嗅探<br/>check_cross_plane_communication<br/>文件: arch_guard<br/>/check_cross_plane_communication.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_fe_acl_boundary_py["检查feaclboundary<br/>INV-006 前端 ACL（仓库内有前端树则启用）<br/>check_fe_acl_boundary<br/>文件: arch_guard/check_fe_acl_boundary.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_hot_path_purity_py["检查hot路径purity<br/>INV-012 Hot 路径 Python 禁 asyncio（配置驱动）<br/>check_hot_path_purity<br/>文件: arch_guard/check_hot_path_purity.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_scaffold_exit_gates_py["checkscaffold退出门禁<br/>scaffold→experimental 安全门禁检查<br/>check_scaffold_exit_gates<br/>文件: arch_guard/check_scaffold_exit_gates.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_schema_consistency_py["检查模式一致性<br/>INV-010 契约物理路径存在性（Schema canonical<br/>基线）<br/>check_schema_consistency<br/>文件: arch_guard/check_schema_consistency.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_aisg_gateway_py["检查aisg网关<br/>AISG 拦截门禁 (INV-015) Phase B 升级<br/>check_aisg_gateway<br/>文件: fitness_functions/check_aisg_gateway.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_audit_log_immutability_py["check审计日志immutability<br/>审计日志不可篡改检查<br/>check_audit_log_immutability<br/>文件: fitness_functions<br/>/check_audit_log_immutability.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_capacity_slo_ssot_py["check容量slossot<br/>yaml 注册表 + 与 invariants 数字对齐（SSoT<br/>闭环）<br/>check_capacity_slo_ssot<br/>文件: fitness_functions<br/>/check_capacity_slo_ssot.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_daily_loss_limit_py["checkdaily损失limit<br/>日损失限额自动暂停<br/>check_daily_loss_limit<br/>文件: fitness_functions<br/>/check_daily_loss_limit.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_hot_warm_ipc_py["检查hotwarmipc<br/>INV-018 Hot↔Warm IPC 协议检查<br/>check_hot_warm_ipc<br/>文件: fitness_functions/check_hot_warm_ipc.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_idempotency_key_py["检查幂等性密钥<br/>幂等 Key 字段存在性检查<br/>check_idempotency_key<br/>文件: fitness_functions/check_idempotency_key.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_log_secret_leak_py["check日志密钥leak<br/>R2 日志不写 secret 适应度函数<br/>check_log_secret_leak<br/>文件: fitness_functions/check_log_secret_leak.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_no_cross_plane_mutable_state_py["checkno跨planemutable状态<br/>INV-020 跨平面共享可变状态检查<br/>check_no_cross_plane_mutable_state<br/>文件: fitness_functions<br/>/check_no_cross_plane_mutable_state.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_ocp_signatures_py["检查ocpsignatures<br/>OCP 冻结契约指纹校验<br/>check_ocp_signatures<br/>文件: fitness_functions/check_ocp_signatures.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_pit_compliance_py["检查pit合规<br/>（Point-in-Time）铁律强制执行<br/>check_pit_compliance<br/>文件: fitness_functions/check_pit_compliance.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_position_limit_py["检查持仓限制<br/>单一持仓限制 ≤ 5% NAV<br/>check_position_limit<br/>文件: fitness_functions/check_position_limit.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_risk_params_consistency_py["check风险paramsconsistency<br/>风控参数真源 (INV-013) + 与 INV-002 声明对齐<br/>check_risk_params_consistency<br/>文件: fitness_functions<br/>/check_risk_params_consistency.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_survivorship_bias_py["检查survivorshipbias<br/>Survivorship 策略门禁<br/>check_survivorship_bias<br/>文件: fitness_functions<br/>/check_survivorship_bias.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_warm_cold_async_py["checkwarm冷异步<br/>INV-019 Warm→Cold 异步通信检查<br/>check_warm_cold_async<br/>文件: fitness_functions/check_warm_cold_async.py<br/>(生产态 / production)"]
    scripts_arch_guard_run_all_py["运行all<br/>Architecture Guard 编排器<br/>run_all<br/>文件: arch_guard/run_all.py<br/>(生产态 / production)"]
    scripts_construction_e2e_check_py["端到端检查<br/>construction包的e2e_check模块<br/>_e2e_check<br/>文件: construction/_e2e_check.py<br/>(生产态 / production)"]
    scripts_construction_e2e_deep_py["端到端deep<br/>依赖检查statuses工作<br/>_e2e_deep<br/>文件: construction/_e2e_deep.py<br/>(生产态 / production)"]
    scripts_construction_check_transition_code_py["检查转换代码<br/>construction包的check_transition_code模块<br/>文件: construction/check_transition_code.py<br/>(生产态 / production)"]
    scripts_construction_d_init_task_system_py["初始化任务系统数据库 +<br/>创建任务系统自身的施工任务卡（吃狗粮）<br/>construction包的d_init_task_system模块<br/>文件: construction/d_init_task_system.py<br/>(生产态 / production)"]
    scripts_construction_demo_a2a_chat_py["A2A 多 Agent 聊天演示 - Alpha 和 Beta<br/>讨论项目评估<br/>construction包的demo_a2a_chat模块<br/>文件: construction/demo_a2a_chat.py<br/>(生产态 / production)"]
    scripts_construction_demo_a2a_coordination_py["A2A 协议协调任务演示<br/>construction包的demo_a2a_coordination模块<br/>文件: construction/demo_a2a_coordination.py<br/>(生产态 / production)"]
    scripts_construction_demo_e2e_pipeline_py["demoe2e管线<br/>C-track 端到端演示 —— 全流水线一次性运行<br/>demo_e2e_pipeline<br/>文件: construction/demo_e2e_pipeline.py<br/>(生产态 / production)"]
    scripts_construction_finalize_tasks_py["finalize任务<br/>依赖任务repo、sqlite模式、包入口工作<br/>finalize_tasks<br/>文件: construction/finalize_tasks.py<br/>(生产态 / production)"]
    scripts_construction_local_layer_daemon_py["本地层daemon<br/>L2 本地模型层守护进程（薄包装，DEPRECATED）<br/>local_layer_daemon<br/>文件: construction/local_layer_daemon.py<br/>(生产态 / production)"]
    scripts_construction_reset_test_task_py["重置测试任务<br/>依赖sqlite模式工作<br/>reset_test_task<br/>文件: construction/reset_test_task.py<br/>(生产态 / production)"]
    scripts_construction_start_brain_py["启动brain<br/>ZephyrAlpha 系统大脑一键启动<br/>start_brain<br/>文件: construction/start_brain.py<br/>(生产态 / production)"]
    scripts_construction_test_event_hook_py["测试事件钩子<br/>construction的事件，定义和分发事件<br/>test_event_hook<br/>文件: construction/test_event_hook.py<br/>(生产态 / production)"]
    scripts_context_generate_architecture_context_py["生成架构上下文<br/>预编译架构上下文包生成器<br/>generate_architecture_context<br/>文件: context/generate_architecture_context.py<br/>(生产态 / production)"]
    scripts_diagnose_breadth_failed_py["diagnosebreadth失败<br/>诊断 breadth_failed 能力的根因。<br/>diagnose_breadth_failed<br/>文件: scripts/diagnose_breadth_failed.py<br/>(生产态 / production)"]
    scripts_dm90971_add_test_headers_py["dm90971add测试headers<br/>dm90971新增测试headers。DM-90971: Batch add<br/>module_id scope prefix + governance anchor<br/>headers to test files.<br/>文件: scripts/dm90971_add_test_headers.py<br/>(生产态 / production)"]
    scripts_fix_freeze_manifest_py["修复freeze清单<br/>修复freezemanifest。Fix freezemanifest.yaml -<br/>comprehensive repair of all corrupted desc<br/>fields.<br/>文件: scripts/fix_freeze_manifest.py<br/>(生产态 / production)"]
    scripts_fix_orphan_all_py["修复孤儿all<br/>自动修复 __init__.py __all__ 孤儿模块<br/>fix_orphan_all<br/>文件: scripts/fix_orphan_all.py<br/>(生产态 / production)"]
    scripts_generate_manifest_py["generate清单<br/>生成manifest。Generate complete<br/>script_manifest.yaml from scripts/ tree scan.<br/>文件: scripts/generate_manifest.py<br/>(生产态 / production)"]
    scripts_generate_pathway_registry_py["generatepathway注册表<br/>从所有 MOD 蓝图的 §路径索引 章节自动生成<br/>system-pathway-registry.yaml。<br/>generate_pathway_registry<br/>文件: scripts/generate_pathway_registry.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_zoomable_html_py["可缩放 Mermaid HTML 生成器（共享模块）。<br/>生成器包的zoomable_html模块<br/>文件: generators/zoomable_html.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_pure_shim_py["检查pureshim<br/>GATE-NO-PURE-SHIM 检测器（治本漏洞1 2026-06-29）<br/>check_pure_shim<br/>文件: d7_code/check_pure_shim.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_rule_ai_perception_index_py["generate规则aiperception索引<br/>规则AI感知索引生成器<br/>（#ARCH-GOV-CONVERGENCE-META Phase 3.2a）<br/>generate_rule_ai_perception_index<br/>文件: generators<br/>/generate_rule_ai_perception_index.py<br/>(生产态 / production)"]
    scripts_hooks_auto_handoff_log_py["自动handoff日志<br/>执行 git 命令并返回 stdout（UTF-8 解码）。<br/>auto_handoff_log<br/>文件: hooks/auto_handoff_log.py<br/>(生产态 / production)"]
    scripts_lock_files_py["锁files<br/>— AI 对话文件锁协议（硬规则执行工具）<br/>lock_files<br/>文件: scripts/lock_files.py<br/>(生产态 / production)"]
    scripts_mcp_launcher_py["MCP DAG 编排启动器（MOD-INF-013 §14 拓扑排序 +<br/>Pro<br/>cessLifecycleGateway 管理）<br/>launcher<br/>文件: mcp/launcher.py<br/>(生产态 / production)"]
    scripts_mcp_start_all_py["启动all<br/>MCP 全 Server 启动脚本 — DEPRECATED.<br/>start_all<br/>文件: mcp/start_all.py<br/>(生产态 / production)"]
    scripts_mcp_status_all_py["状态all<br/>MCP 全 Server 状态检查脚本（MOD-INF-013 §14）。<br/>status_all<br/>文件: mcp/status_all.py<br/>(生产态 / production)"]
    scripts_mcp_stop_all_py["停止all<br/>MCP 全 Server 停止脚本（MOD-INF-013 §14）。<br/>stop_all<br/>文件: mcp/stop_all.py<br/>(生产态 / production)"]
    scripts_migration_dm314_infra_ops_split_py["dm314基础设施运维拆分<br/>DM-314: infra_ops/ 拆分迁移执行脚本。<br/>dm314_infra_ops_split<br/>文件: migration/dm314_infra_ops_split.py<br/>(生产态 / production)"]
    scripts_migration_governance_root_split_py["治理根拆分<br/>ARCH-031: governance/ root flat-files split<br/>migration orchestrator<br/>文件: migration/governance_root_split.py<br/>(生产态 / production)"]
    scripts_ops_verify_header_completeness_py["文件头部完整性校验（6 格式统一入口）<br/>运维包的verify_header_completeness模块<br/>文件: ops/verify_header_completeness.py<br/>(生产态 / production)"]
    scripts_post_checkout_guard_py["postcheckout守卫<br/>Post-checkout Guard — 事后检测 checkout<br/>是否覆盖了其他 session 的文件锁。<br/>post_checkout_guard<br/>文件: scripts/post_checkout_guard.py<br/>(生产态 / production)"]
    scripts_pre_commit_verify_dedup_py["verify去重<br/>pre_commit 验证脚本 — 委托给 code-dedup-engine<br/>CLI verify 子命令.<br/>verify_dedup<br/>文件: pre_commit/verify_dedup.py<br/>(生产态 / production)"]
    scripts_rollback_py["回滚<br/>Rollback System CLI — MOD-INF-021 v0.10.0<br/>Git-native+SQLite Checkpoint 操作入口。<br/>文件: scripts/rollback.py<br/>(生产态 / production)"]
    scripts_run_deepseek_v4_exam_py["运行deepseekv4exam<br/>DeepSeek V4 入职考试运行脚本<br/>run_deepseek_v4_exam<br/>文件: scripts/run_deepseek_v4_exam.py<br/>(生产态 / production)"]
    scripts_run_ollama_exam_py["运行ollamaexam<br/>Ollama 入职考试运行脚本<br/>run_ollama_exam<br/>文件: scripts/run_ollama_exam.py<br/>(生产态 / production)"]
    scripts_scaffold_py["scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TW<br/>ZephyrAlpha 唯一创建入口（RULE-TWO 强制执行器）<br/>文件: scripts/scaffold.py<br/>(生产态 / production)"]
    scripts_setup_git_guard_aliases_py["setupGit守卫aliases<br/>Setup/Remove Git Aliases for Git Guard —<br/>自动化集成入口。<br/>setup_git_guard_aliases<br/>文件: scripts/setup_git_guard_aliases.py<br/>(生产态 / production)"]
    src_zephyr_governance_a2a_init_py["governance/a2a 包入口<br/>管理governance.a2a子包的加载和懒导入<br/>文件: a2a/__init__.py<br/>(生产态 / production)"]
    src_zephyr_governance_adapters_risk_validation_bridge_py["风险验证桥接<br/>D_EXECUTION_CORE — Risk Validation Bridge<br/>(DW-239)<br/>文件: adapters/risk_validation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_governance_adapters_simulation_broker_py["仿真经纪人<br/>D_EXECUTION_CORE — Simulation Broker Adapter<br/>文件: adapters/simulation_broker.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_spec_init_py["governance/agent-spec 包入口<br/>管理governance.agent-spec子包的加载和懒导入<br/>文件: agent-spec/__init__.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_spec_a2a_failure_py["A2A故障<br/>G-CT-008 消费端 — Escalation.on_a2a_failure()<br/>跨 agent 通信失败升级.<br/>文件: agent_spec/a2a_failure.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_spec_rbac_bridge_py["RBAC桥接<br/>G-CT-007 契约：Budget -> RBAC 配额限制.<br/>rbac_bridge<br/>文件: agent_spec/rbac_bridge.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_spec_registry_py["注册表<br/>G-CT-003 契约：Agent Spec -> RBAC 能力检查.<br/>registry<br/>文件: agent_spec/registry.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_architecture_contracts_py["架构契约<br/>治理/architecture<br/>governance包的architecture_contracts模块<br/>文件: architecture_governance<br/>/architecture_contracts.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_architecture_principles_py["装饰器：为函数标记适用的架构原则。<br/>治理/architecture<br/>governance包的architecture_principles模块<br/>文件: architecture_governance<br/>/architecture_principles.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_blueprint_bloat_monitor_py["蓝图bloat监控器<br/>Blueprint Bloat Monitor — v0.11.0<br/>蓝图膨胀监控器。<br/>blueprint_bloat_monitor<br/>文件: architecture_governance<br/>/blueprint_bloat_monitor.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_blueprint_code_consistency_py["蓝图代码一致性<br/>Blueprint-Code Consistency Gate — MOD-INF-022<br/>文件: architecture_governance<br/>/blueprint_code_consistency.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_blueprint_reconciler_py["蓝图协调器<br/>Blueprint Reconciler — v0.10.0<br/>蓝图实现一致性校验器。<br/>blueprint_reconciler<br/>文件: architecture_governance<br/>/blueprint_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_construction_verifier_py["construction验证器<br/>Construction Verifier — 施工验证器:<br/>任务卡完成度+蓝图一致性检查。<br/>construction_verifier<br/>文件: architecture_governance<br/>/construction_verifier.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_cross_env_consistency_py["跨环境一致性<br/>治理/architecture<br/>governance包的cross_env_consistency模块<br/>文件: architecture_governance<br/>/cross_env_consistency.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_dependency_manager_py["依赖管理器<br/>治理子系统的依赖关系管理工具<br/>dependency_manager<br/>文件: architecture_governance<br/>/dependency_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_formal_verifier_py["formal验证器<br/>Formal Verifier — v0.6.0 形式验证器:<br/>升级规则形式化验证->一致性+完备性检测。<br/>formal_verifier<br/>文件: architecture_governance/formal_verifier.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_gap_analyzer_py["gap分析器<br/>Gap Analyzer — v0.8.0 间隙分析器:<br/>escalation覆盖缺口扫描+新操作类型识别。<br/>gap_analyzer<br/>文件: architecture_governance/gap_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_llm_impact_analyzer_py["LLM冲击分析器<br/>LLMImpactAnalyzer — LLM-based commit<br/>语义影响分析器。<br/>llm_impact_analyzer<br/>文件: architecture_governance<br/>/llm_impact_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_local_first_arch_py["本地首架构<br/>治理/architecture<br/>governance包的local_first_arch模块<br/>文件: architecture_governance<br/>/local_first_arch.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_path_resolver_py["路径解析器<br/>PathResolver — 模块路径解析器<br/>path_resolver<br/>文件: architecture_governance/path_resolver.py<br/>(生产态 / production)"]
    src_zephyr_governance_bridges_alerts_py["告警<br/>依赖预算告警工作<br/>文件: bridges/alerts.py<br/>(生产态 / production)"]
    src_zephyr_governance_bridges_spec_auditor_py["spec审计器<br/>治理/bridges包的spec_auditor模块<br/>文件: bridges/spec_auditor.py<br/>(生产态 / production)"]
    src_zephyr_governance_compliance_gate_a6_compliance_manager_py["合规管理器<br/>ZephyrAlpha — D_COMPLIANCE Compliance Layer —<br/>合规规则管理器接口<br/>compliance_manager<br/>文件: compliance_gate_a6/compliance_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_compliance_gate_a6_compliance_mapper_py["合规mapper<br/>Compliance Mapper — D-022-13 合规映射器:<br/>操作->法规(SOX/GDPR/MiFID)映射+审计迹。<br/>compliance_mapper<br/>文件: compliance_gate_a6/compliance_mapper.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_command_chain_length_gate_py["命令链长度门禁<br/>Command Chain Length Gate — v0.13.0<br/>命令体积Deny退化防御器。<br/>command_chain_length_gate<br/>文件: context_governance<br/>/command_chain_length_gate.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_budget_py["上下文预算<br/>— 上下文预算管理与超预算截断（Phase 11 / 盲点<br/>B28）<br/>context_budget<br/>文件: context_governance/context_budget.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_manager_py["上下文管理器<br/>治理的管理器，统一管理资源生命周期<br/>context_manager<br/>文件: context_governance/context_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_package_py["上下文包<br/>Context Package — D-022-08 委托上下文包:<br/>升级原因+证据链+历史try_trace。<br/>context_package<br/>文件: context_governance/context_package.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_recycling_py["上下文recycling<br/>主要提供is验证等功能<br/>context_recycling<br/>文件: context_governance/context_recycling.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_switch_governor_py["上下文switchgovernor<br/>Context Switch Governor — v0.11.0<br/>Owner上下文切换预算管理器。<br/>context_switch_governor<br/>文件: context_governance<br/>/context_switch_governor.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_waste_detector_py["上下文waste检测器<br/>治理的报告器，汇总数据生成报告<br/>context_waste_detector<br/>文件: context_governance<br/>/context_waste_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_conversation_tax_detector_py["conversationtax检测器<br/>治理/context<br/>governance包的conversation_tax_detector模块<br/>文件: context_governance<br/>/conversation_tax_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_instruction_bloat_detector_py["instructionbloat检测器<br/>InstructionBloatDetector — 指令膨胀检测<br/>instruction_bloat_detector<br/>文件: context_governance<br/>/instruction_bloat_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_multi_turn_intent_analyzer_py["多turnintent分析器<br/>Multi-Turn Intent Analyzer — v0.13.0<br/>多轮分布式意图分析器。<br/>multi_turn_intent_analyzer<br/>文件: context_governance<br/>/multi_turn_intent_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_prompt_lifecycle_py["提示生命周期<br/>治理/context governance包的prompt_lifecycle模块<br/>文件: context_governance/prompt_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_protocol_self_context_py["协议自上下文<br/>Protocol Self Context — v0.10.0<br/>协议自维护上下文管理器。<br/>protocol_self_context<br/>文件: context_governance<br/>/protocol_self_context.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_think_time_model_py["thinktime模型<br/>治理/context governance包的think_time_model模块<br/>文件: context_governance/think_time_model.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_classification_py["数据分类<br/>检查 self_level 是否有权限访问 target_level<br/>的数据。<br/>data_classification<br/>文件: data_governance/data_classification.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_lifecycle_py["数据生命周期<br/>治理/data governance包的data_lifecycle模块<br/>文件: data_governance/data_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_pipeline_guard_py["数据管线守卫<br/>Data Pipeline Guard — v0.10.0<br/>数据管道完整性防护: schema validation+row count<br/>check+checksum verify。<br/>data_pipeline_guard<br/>文件: data_governance/data_pipeline_guard.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_quality_py["数据质量<br/>治理/data governance包的data_quality模块<br/>文件: data_governance/data_quality.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_source_reliability_py["数据源可靠性<br/>治理/data<br/>governance包的data_source_reliability模块<br/>文件: data_governance/data_source_reliability.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_exchange_partition_detector_py["交易所partition检测器<br/>Exchange Partition Detector — v0.12.0<br/>交易所网络分区检测器。<br/>exchange_partition_detector<br/>文件: data_governance<br/>/exchange_partition_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_exchange_reg_monitor_py["交易所reg监控器<br/>Exchange Reg Monitor — v0.11.0<br/>交易所规则变更监控器。<br/>exchange_reg_monitor<br/>文件: data_governance/exchange_reg_monitor.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_miniqmt_provider_py["miniqmt提供器<br/>MiniQMT 实盘行情 Provider（Tick + 5档盘口）<br/>miniqmt_provider<br/>文件: data_governance/miniqmt_provider.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_pricing_sync_py["pricing同步<br/>治理/data governance包的pricing_sync模块<br/>文件: data_governance/pricing_sync.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_realtime_streaming_py["实时流式<br/>治理/data governance包的realtime_streaming模块<br/>文件: data_governance/realtime_streaming.py<br/>(生产态 / production)"]
    src_zephyr_governance_evidence_pack_py["证据包<br/>主要提供pack、验证、列表packs等功能，供audit-orc<br/>hestrator.integrity; 使用<br/>evidence_pack<br/>文件: governance/evidence_pack.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_arbitrage_asymmetry_detector_py["arbitrageasymmetry检测器<br/>Arbitrage Asymmetry Detector — v0.11.0<br/>跨交易所套利不对称检测器。<br/>arbitrage_asymmetry_detector<br/>文件: financial_governance<br/>/arbitrage_asymmetry_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_atomic_transaction_manager_py["atomic交易管理器<br/>AtomicTransactionManager — SQLite +<br/>文件系统的跨介质原子事务管理器 v2.0（ATM）。<br/>atomic_transaction_manager<br/>文件: financial_governance<br/>/atomic_transaction_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_flash_crash_guard_py["flashcrash守卫<br/>Flash Crash Guard — v0.12.0 闪崩双轨熔断器。<br/>flash_crash_guard<br/>文件: financial_governance/flash_crash_guard.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_fsm_verifier_py["fsm验证器<br/>治理/financial governance包的fsm_verifier模块<br/>文件: financial_governance/fsm_verifier.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_instrument_py["financial_governance/instrument<br/>治理/financial governance包的instrument模块<br/>文件: financial_governance/instrument.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_microstructure_defense_py["microstructure防御<br/>治理/financial<br/>governance包的microstructure_defense模块<br/>文件: financial_governance<br/>/microstructure_defense.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_oms_risk_engine_py["oms风险引擎<br/>治理/financial governance包的oms_risk_engine模块<br/>文件: financial_governance/oms_risk_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_risk_matrix_py["风险矩阵<br/>治理/financial governance包的risk_matrix模块<br/>文件: financial_governance/risk_matrix.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_strategy_portfolio_py["策略组合<br/>治理/financial<br/>governance包的strategy_portfolio模块<br/>文件: financial_governance/strategy_portfolio.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_strategy_scoper_py["策略scoper<br/>Strategy Scoper — v0.6.0 策略范围隔离器: SIG<br/>/Strat/Capital多层策略隔离。<br/>strategy_scoper<br/>文件: financial_governance/strategy_scoper.py<br/>(生产态 / production)"]
    src_zephyr_governance_implementations_default_experiment_pipeline_py["默认实验管线<br/>治理/implementations包的default_experiment_pipel<br/>ine模块<br/>文件: implementations<br/>/default_experiment_pipeline.py<br/>(生产态 / production)"]
    src_zephyr_governance_implementations_default_security_gateway_py["默认安全网关<br/>治理的门禁，在关键节点检查是否放行<br/>default_security_gateway<br/>文件: implementations<br/>/default_security_gateway.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_agent_debate_py["代理debate<br/>治理的核心类，封装DebateVerdict相关逻辑<br/>agent_debate<br/>文件: intelligence_governance/agent_debate.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_ai_self_diagnosis_py["AI自诊断<br/>治理/intelligence<br/>governance包的ai_self_diagnosis模块<br/>文件: intelligence_governance<br/>/ai_self_diagnosis.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_aisg_sandbox_py["aisg沙箱<br/>AISG Sandbox Testing — AI Security Gateway<br/>沙箱验证 (INV-015 升级)<br/>aisg_sandbox<br/>文件: intelligence_governance/aisg_sandbox.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_autonomy_dashboard_py["autonomy仪表盘<br/>Autonomy Dashboard — AI 自主感知健康仪表。<br/>autonomy_dashboard<br/>文件: intelligence_governance<br/>/autonomy_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_confidence_estimator_py["confidence估算器<br/>Confidence Estimator — D-022-05 置信度评估器:<br/>certainty×evidence×risk三维评估。<br/>confidence_estimator<br/>文件: intelligence_governance<br/>/confidence_estimator.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_confidence_quantifier_py["ConfidenceQuantifier — AI 置信度量化。<br/>治理/intelligence<br/>governance包的confidence_quantifier模块<br/>文件: intelligence_governance<br/>/confidence_quantifier.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_continuous_trust_py["continuous信任<br/>Continuous Trust Ledger — 持续信任评估引擎。<br/>continuous_trust<br/>文件: intelligence_governance<br/>/continuous_trust.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_cross_agent_conflict_detector_py["跨代理冲突检测器<br/>CrossAgentConflictDetector — 多 Agent<br/>并发冲突检测。<br/>cross_agent_conflict_detector<br/>文件: intelligence_governance<br/>/cross_agent_conflict_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_cross_assistant_adapter_py["跨assistant适配器<br/>Cross-Assistant Adapter — v0.6.0 Trae/Cursor<br/>/Windsurf/Codex/Wedata统一升级接口。<br/>cross_assistant_adapter<br/>文件: intelligence_governance<br/>/cross_assistant_adapter.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_delegation_manager_py["delegation管理器<br/>Delegation Manager — D-022-02 自动委托协议。<br/>delegation_manager<br/>文件: intelligence_governance<br/>/delegation_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_memory_provider_py["记忆提供器<br/>D_DATA — Memory Provider<br/>文件: intelligence_governance/memory_provider.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_meta_confidence_py["元confidence<br/>Meta-Confidence — D-022-10<br/>Agent对自身判定置信度的自评+历史校准。<br/>meta_confidence<br/>文件: intelligence_governance/meta_confidence.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_model_provider_data_py["模型提供器数据<br/>治理的模型，定义数据结构和字段<br/>model_provider_data<br/>文件: intelligence_governance<br/>/model_provider_data.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_model_router_py["模型路由器<br/>依赖预算模型、提供器数据、resultswriter工作<br/>model_router<br/>文件: intelligence_governance/model_router.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_model_version_detector_py["模型版本检测器<br/>Model Version Detector — v0.10.0<br/>模型版本突变检测: model version<br/>change->degraded auto_guard。<br/>model_version_detector<br/>文件: intelligence_governance<br/>/model_version_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_multi_model_consensus_py["多模型共识<br/>治理/intelligence<br/>governance包的multi_model_consensus模块<br/>文件: intelligence_governance<br/>/multi_model_consensus.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_mvep_orchestrator_py["mvep编排器<br/>MVEP Orchestrator — v0.11.0 Minimum Viable<br/>Escalation Protocol调度器。<br/>mvep_orchestrator<br/>文件: intelligence_governance<br/>/mvep_orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_provider_failover_py["提供器故障切换<br/>Provider Failover — v0.7.0 多LLM Provider容灾:<br/>deepseek->claude->gpt fallback链。<br/>provider_failover<br/>文件: intelligence_governance<br/>/provider_failover.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_self_benchmark_py["自基准<br/>(W3-7) — 5 组已知对自验证 + 引擎退化告警<br/>self_benchmark<br/>文件: intelligence_governance/self_benchmark.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_self_test_py["自测试<br/>Escalation Protocol Self-Test — MOD-INF-022<br/>文件: intelligence_governance/self_test.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_self_validator_py["自校验器<br/>Self Validator — v0.10.0 升级协议自验证器:<br/>protocol自身规则+代码一致性自检。<br/>self_validator<br/>文件: intelligence_governance/self_validator.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_subagent_hook_propagator_py["subagent钩子propagator<br/>Subagent Hook Propagator — v0.13.0 子Agent<br/>Hook旁路防护器。<br/>subagent_hook_propagator<br/>文件: intelligence_governance<br/>/subagent_hook_propagator.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_api_lifecycle_py["API生命周期<br/>治理/lifecycle governance包的api_lifecycle模块<br/>文件: lifecycle_governance/api_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_migration_strategy_py["迁移策略<br/>治理/lifecycle<br/>governance包的migration_strategy模块<br/>文件: lifecycle_governance/migration_strategy.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_paper_live_transition_py["paper实盘转换<br/>检查是否可跳Phase——不可跳, 只允许顺序next。<br/>paper_live_transition<br/>文件: lifecycle_governance<br/>/paper_live_transition.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_post_live_verification_py["提交实时验证<br/>治理/lifecycle<br/>governance包的post_live_verification模块<br/>文件: lifecycle_governance<br/>/post_live_verification.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_transition_py["转换<br/>transition — 状态机转换 Mixin（从 task_repo.py<br/>拆分，SRC-0066）<br/>文件: lifecycle_governance/transition.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_analytics_base_py["analytics基类<br/>Re-export wrapper: analytics_base canonical at<br/>zephyr.reporting.analytics_base<br/>文件: observability_governance/analytics_base.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_objective_tracker_py["objective追踪器<br/>Objective Tracker — v0.9.0 目标漂移检测器:<br/>agent目标函数稳定性+变更检测+rollback。<br/>objective_tracker<br/>文件: observability_governance<br/>/objective_tracker.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_battle_map_reader_py["persistence/battle_map_reader<br/>battle_map_reader.py —<br/>作战地图数据库只读查询工具模块<br/>文件: persistence/battle_map_reader.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_database_manager_py["数据库管理器<br/>DatabaseManager — 连接池 + 健康检查 + 自动备份<br/>+ WAL checkpoint（SH-DB-001 v2.0）<br/>database_manager<br/>文件: persistence/database_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_database_service_py["数据库服务<br/>DatabaseService 真源收敛（AI-14 审计 P1 修复）<br/>database_service<br/>文件: persistence/database_service.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_dataflowgraph_schema_py["dataflowgraph结构<br/>dataflowgraph Schema DDL + 连接入口<br/>dataflowgraph_schema<br/>文件: persistence/dataflowgraph_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_decision_graph_reader_py["决策graph读取器<br/>决策流图数据库只读查询工具模块<br/>decision_graph_reader<br/>文件: persistence/decision_graph_reader.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_depgraph_reader_py["depgraph读取器<br/>依赖图数据库查询工具模块<br/>depgraph_reader<br/>文件: persistence/depgraph_reader.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_protocol_state_store_py["协议状态存储<br/>Protocol State Store — v0.10.0<br/>协议运行时状态持久化: JSON snapshot+recovery<br/>state+crash恢复。<br/>protocol_state_store<br/>文件: persistence/protocol_state_store.py<br/>(生产态 / production)"]
    src_zephyr_governance_services_adapter_py["适配器<br/>Escalation Adapter — MOD-INF-022 统一集成入口.<br/>文件: services/adapter.py<br/>(生产态 / production)"]
    src_zephyr_governance_services_cross_session_correlator_py["跨会话关联器<br/>Cross-Session Correlator — v0.9.0<br/>跨会话Coreset关联器:<br/>多session行为模式+异常跨session模式检测。<br/>cross_session_correlator<br/>文件: services/cross_session_correlator.py<br/>(生产态 / production)"]
    src_zephyr_governance_services_memory_provenance_py["记忆溯源<br/>Memory Provenance — v0.9.0 记忆溯源追踪:<br/>每条memory record的来源agent+timestamp+hash链。<br/>memory_provenance<br/>文件: services/memory_provenance.py<br/>(生产态 / production)"]
    src_zephyr_governance_strategies_strategy_registry_py["策略注册表<br/>StrategyRegistry 卫星模块（OCP-002）<br/>strategy_registry<br/>文件: strategies/strategy_registry.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_base_server_py["基类服务端<br/>主要提供注册tool、处理请求等功能<br/>_base_server<br/>文件: governance/_base_server.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_audit_logger_py["审计日志器<br/>主要提供日志、查询、数量等功能<br/>audit_logger<br/>文件: governance/audit_logger.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_auditor_py["审计器<br/>G-CT-008 契约：A2A -> Audit 审计 Agent 间通信.<br/>auditor<br/>文件: governance/auditor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_error_codes_py["错误codes<br/>治理的异常，定义本模块的异常类型<br/>error_codes<br/>文件: governance/error_codes.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_governance_adapter_py["治理适配器<br/>A2A GovernanceAdapter — Phase 4 治理集成桥接器<br/>governance_adapter<br/>文件: governance/governance_adapter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_phase_hold_py["阶段hold<br/>基础设施/治理包的phase_hold模块<br/>文件: governance/phase_hold.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_policy_engine_py["策略引擎<br/>主要提供评估、新增策略、移除策略等功能<br/>policy_engine<br/>文件: governance/policy_engine.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_protocol_py["协议<br/>G-CT-008 — A2ACommunication Pydantic V2<br/>BaseModel agent-to-agent 通信数据结构.<br/>protocol<br/>文件: governance/protocol.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_rate_limiter_py["速率限制器<br/>Sliding window 速率限制器，支持 per-key 分桶。<br/>rate_limiter<br/>文件: governance/rate_limiter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_session_manager_py["会话管理器<br/>主要提供创建会话、获取会话、结束会话等功能<br/>session_manager<br/>文件: governance/session_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py["治理集成<br/>基础设施/layer3<br/>coordination包的governance_integration模块<br/>文件: layer3_coordination<br/>/_governance_integration.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch2_governance_py["batch2治理<br/>Batch2 治理层契约 — 15条 Pydantic v2 Schema<br/>（Provenance/AI审计守卫/TechStackValidator<br/>/Governance Loop/Sandbox资源限制）.<br/>batch2_governance<br/>文件: contracts/batch2_governance.py<br/>(生产态 / production)"]
    src_zephyr_integration_mcp_governance_server_py["治理服务端<br/>GovernanceServer: 治理域统一MCP入口<br/>governance_server<br/>文件: mcp/governance_server.py<br/>(生产态 / production)"]
    src_zephyr_shared_capacity_governance_capacity_governance_loop_py["容量治理循环<br/>容量治理loop，容量治理的循环，循环执行的流程。<br/>capacity_governance_loop<br/>文件: capacity_governance<br/>/capacity_governance_loop.py<br/>(生产态 / production)"]
    src_zephyr_shared_protocols_a2a_a2a_governance_py["A2A治理<br/>A2A Governance — shared interface definitions<br/>for governance layer<br/>文件: a2a/a2a_governance.py<br/>(生产态 / production)"]
    tests_agent_rbac_test_session_aware_stash_red_blue_py["测试会话感知stashredblue<br/>会话 隔离 stash 红蓝对抗极限测试。<br/>test_session_aware_stash_red_blue<br/>文件: agent_rbac<br/>/test_session_aware_stash_red_blue.py<br/>(生产态 / production)"]
    tests_git_test_git_commit_concurrent_py["测试Git提交并发<br/>幽灵提交红蓝对抗测试<br/>test_git_commit_concurrent<br/>文件: git/test_git_commit_concurrent.py<br/>(生产态 / production)"]
    tests_git_test_git_commit_extreme_py["测试Gitcommitextreme<br/>GitCommitGateway 极端故障注入测试<br/>test_git_commit_extreme<br/>文件: git/test_git_commit_extreme.py<br/>(生产态 / production)"]
    tests_git_test_git_commit_gateway_py["测试Git提交网关<br/>GitCommitGateway 单元测试（OPS-2026062512 验收）<br/>test_git_commit_gateway<br/>文件: git/test_git_commit_gateway.py<br/>(生产态 / production)"]
    tests_git_test_reconciler_verify_autosync_py["测试对账器verifyautosync<br/>--reconciler-verify auto-sync 产物豁免测试。<br/>test_reconciler_verify_autosync<br/>文件: git/test_reconciler_verify_autosync.py<br/>(生产态 / production)"]
    tests_governance_generators_test_check_gate_inventory_drift_py["测试check门禁inventory漂移<br/>commit_gates 模块清单漂移检测脚本单元测试<br/>test_check_gate_inventory_drift<br/>文件: generators<br/>/test_check_gate_inventory_drift.py<br/>(生产态 / production)"]
    tests_governance_generators_test_generate_gate_registry_py["测试生成门禁注册表<br/>py 单元测试（CommitGate 同步治本 2026-07-17）<br/>test_generate_gate_registry<br/>文件: generators/test_generate_gate_registry.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_worktree_lifecycle_py["测试worktree生命周期<br/>#ARCH-WORKTREE-LIFECYCLE-001 状态机测试<br/>test_worktree_lifecycle<br/>文件: rule_bridge/test_worktree_lifecycle.py<br/>(生产态 / production)"]
    tests_governance_test_ast_import_rewriter_py["测试astimportrewriter<br/>提供testexactmatch、testnomatch、testprefixmatch<br/>等方法<br/>文件: governance/test_ast_import_rewriter.py<br/>(生产态 / production)"]
    tests_io_test_depgraph_schema_py["测试依赖图模式<br/>py DDL 真源与迁移框架单元测试<br/>test_depgraph_schema<br/>文件: io/test_depgraph_schema.py<br/>(生产态 / production)"]
    tests_io_test_verify_schema_health_py["测试校验模式健康<br/>py 门禁可靠性单元测试<br/>test_verify_schema_health<br/>文件: io/test_verify_schema_health.py<br/>(生产态 / production)"]
    tests_rollback_test_concurrency_guard_red_blue_py["测试并发守卫redblue<br/>红蓝对抗极端测试 — git_guard +<br/>concurrency_guard 端到端防护能力验证。<br/>test_concurrency_guard_red_blue<br/>文件: rollback<br/>/test_concurrency_guard_red_blue.py<br/>(生产态 / production)"]
    tests_rollback_test_concurrent_mv_guard_py["并发红蓝极限对抗测试 — 多 AI 并发执行 git mv<br/>时的防护能力验证。<br/>rollback包的test_concurrent_mv_guard模块<br/>文件: rollback/test_concurrent_mv_guard.py<br/>(生产态 / production)"]
    tests_task_test_task_repo_gateway_e2e_py["测试taskrepogatewaye2e<br/>端到端链路测试<br/>test_task_repo_gateway_e2e<br/>文件: task/test_task_repo_gateway_e2e.py<br/>(生产态 / production)"]
    tests_test_align_panoramas_py["测试alignpanoramas<br/>tests包的test_align_panoramas模块<br/>文件: tests/test_align_panoramas.py<br/>(生产态 / production)"]
    tests_test_dataflow_design_layout_py["测试dataflowdesignlayout<br/>设计态数据流文档视觉风格测试<br/>test_dataflow_design_layout<br/>文件: tests/test_dataflow_design_layout.py<br/>(生产态 / production)"]
    tests_test_generate_dataflow_diagram_py["测试generatedataflowdiagram<br/>tests包的test_generate_dataflow_diagram模块<br/>文件: tests/test_generate_dataflow_diagram.py<br/>(生产态 / production)"]
    tests_test_generate_decision_diagram_py["测试generate决策diagram<br/>tests包的test_generate_decision_diagram模块<br/>文件: tests/test_generate_decision_diagram.py<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_rule_registry_collection_yaml ~~~ scripts_a2a_full_verification_py
    scripts_a2a_full_verification_py ~~~ scripts_arch_guard_tools_build_ocp_manifest_py
    scripts_arch_guard_tools_build_ocp_manifest_py ~~~ scripts_arch_guard_tools_inject_idempotency_py
    scripts_arch_guard_tools_inject_idempotency_py ~~~ scripts_arch_guard_tools_patch_p1_paths_py
    scripts_arch_guard_tools_patch_p1_paths_py ~~~ scripts_arch_guard_check_acl_boundary_py
    scripts_arch_guard_check_acl_boundary_py ~~~ scripts_arch_guard_check_cross_plane_communication_py
    scripts_arch_guard_check_cross_plane_communication_py ~~~ scripts_arch_guard_check_fe_acl_boundary_py
    scripts_arch_guard_check_fe_acl_boundary_py ~~~ scripts_arch_guard_check_hot_path_purity_py
    scripts_arch_guard_check_hot_path_purity_py ~~~ scripts_arch_guard_check_scaffold_exit_gates_py
    scripts_arch_guard_check_scaffold_exit_gates_py ~~~ scripts_arch_guard_check_schema_consistency_py
    scripts_arch_guard_check_schema_consistency_py ~~~ scripts_arch_guard_fitness_functions_check_aisg_gateway_py
    scripts_arch_guard_fitness_functions_check_aisg_gateway_py ~~~ scripts_arch_guard_fitness_functions_check_audit_log_immutability_py
    scripts_arch_guard_fitness_functions_check_audit_log_immutability_py ~~~ scripts_arch_guard_fitness_functions_check_capacity_slo_ssot_py
    scripts_arch_guard_fitness_functions_check_capacity_slo_ssot_py ~~~ scripts_arch_guard_fitness_functions_check_daily_loss_limit_py
    scripts_arch_guard_fitness_functions_check_daily_loss_limit_py ~~~ scripts_arch_guard_fitness_functions_check_hot_warm_ipc_py
    scripts_arch_guard_fitness_functions_check_hot_warm_ipc_py ~~~ scripts_arch_guard_fitness_functions_check_idempotency_key_py
    scripts_arch_guard_fitness_functions_check_idempotency_key_py ~~~ scripts_arch_guard_fitness_functions_check_log_secret_leak_py
    scripts_arch_guard_fitness_functions_check_log_secret_leak_py ~~~ scripts_arch_guard_fitness_functions_check_no_cross_plane_mutable_state_py
    scripts_arch_guard_fitness_functions_check_no_cross_plane_mutable_state_py ~~~ scripts_arch_guard_fitness_functions_check_ocp_signatures_py
    scripts_arch_guard_fitness_functions_check_ocp_signatures_py ~~~ scripts_arch_guard_fitness_functions_check_pit_compliance_py
    scripts_arch_guard_fitness_functions_check_pit_compliance_py ~~~ scripts_arch_guard_fitness_functions_check_position_limit_py
    scripts_arch_guard_fitness_functions_check_position_limit_py ~~~ scripts_arch_guard_fitness_functions_check_risk_params_consistency_py
    scripts_arch_guard_fitness_functions_check_risk_params_consistency_py ~~~ scripts_arch_guard_fitness_functions_check_survivorship_bias_py
    scripts_arch_guard_fitness_functions_check_survivorship_bias_py ~~~ scripts_arch_guard_fitness_functions_check_warm_cold_async_py
    scripts_arch_guard_fitness_functions_check_warm_cold_async_py ~~~ scripts_arch_guard_run_all_py
    scripts_arch_guard_run_all_py ~~~ scripts_construction_e2e_check_py
    scripts_construction_e2e_check_py ~~~ scripts_construction_e2e_deep_py
    scripts_construction_e2e_deep_py ~~~ scripts_construction_check_transition_code_py
    scripts_construction_check_transition_code_py ~~~ scripts_construction_d_init_task_system_py
    scripts_construction_d_init_task_system_py ~~~ scripts_construction_demo_a2a_chat_py
    scripts_construction_demo_a2a_chat_py ~~~ scripts_construction_demo_a2a_coordination_py
    scripts_construction_demo_a2a_coordination_py ~~~ scripts_construction_demo_e2e_pipeline_py
    scripts_construction_demo_e2e_pipeline_py ~~~ scripts_construction_finalize_tasks_py
    scripts_construction_finalize_tasks_py ~~~ scripts_construction_local_layer_daemon_py
    scripts_construction_local_layer_daemon_py ~~~ scripts_construction_reset_test_task_py
    scripts_construction_reset_test_task_py ~~~ scripts_construction_start_brain_py
    scripts_construction_start_brain_py ~~~ scripts_construction_test_event_hook_py
    scripts_construction_test_event_hook_py ~~~ scripts_context_generate_architecture_context_py
    scripts_context_generate_architecture_context_py ~~~ scripts_diagnose_breadth_failed_py
    scripts_diagnose_breadth_failed_py ~~~ scripts_dm90971_add_test_headers_py
    scripts_dm90971_add_test_headers_py ~~~ scripts_fix_freeze_manifest_py
    scripts_fix_freeze_manifest_py ~~~ scripts_fix_orphan_all_py
    scripts_fix_orphan_all_py ~~~ scripts_generate_manifest_py
    scripts_generate_manifest_py ~~~ scripts_generate_pathway_registry_py
    scripts_generate_pathway_registry_py ~~~ scripts_governance_d5_architecture_generators_zoomable_html_py
    scripts_governance_d5_architecture_generators_zoomable_html_py ~~~ scripts_governance_d7_code_check_pure_shim_py
    scripts_governance_d7_code_check_pure_shim_py ~~~ scripts_governance_generators_generate_rule_ai_perception_index_py
    scripts_governance_generators_generate_rule_ai_perception_index_py ~~~ scripts_hooks_auto_handoff_log_py
    scripts_hooks_auto_handoff_log_py ~~~ scripts_lock_files_py
    scripts_lock_files_py ~~~ scripts_mcp_launcher_py
    scripts_mcp_launcher_py ~~~ scripts_mcp_start_all_py
    scripts_mcp_start_all_py ~~~ scripts_mcp_status_all_py
    scripts_mcp_status_all_py ~~~ scripts_mcp_stop_all_py
    scripts_mcp_stop_all_py ~~~ scripts_migration_dm314_infra_ops_split_py
    scripts_migration_dm314_infra_ops_split_py ~~~ scripts_migration_governance_root_split_py
    scripts_migration_governance_root_split_py ~~~ scripts_ops_verify_header_completeness_py
    scripts_ops_verify_header_completeness_py ~~~ scripts_post_checkout_guard_py
    scripts_post_checkout_guard_py ~~~ scripts_pre_commit_verify_dedup_py
    scripts_pre_commit_verify_dedup_py ~~~ scripts_rollback_py
    scripts_rollback_py ~~~ scripts_run_deepseek_v4_exam_py
    scripts_run_deepseek_v4_exam_py ~~~ scripts_run_ollama_exam_py
    scripts_run_ollama_exam_py ~~~ scripts_scaffold_py
    scripts_scaffold_py ~~~ scripts_setup_git_guard_aliases_py
    scripts_setup_git_guard_aliases_py ~~~ src_zephyr_governance_a2a_init_py
    src_zephyr_governance_a2a_init_py ~~~ src_zephyr_governance_adapters_risk_validation_bridge_py
    src_zephyr_governance_adapters_risk_validation_bridge_py ~~~ src_zephyr_governance_adapters_simulation_broker_py
    src_zephyr_governance_adapters_simulation_broker_py ~~~ src_zephyr_governance_agent_spec_init_py
    src_zephyr_governance_agent_spec_init_py ~~~ src_zephyr_governance_agent_spec_a2a_failure_py
    src_zephyr_governance_agent_spec_a2a_failure_py ~~~ src_zephyr_governance_agent_spec_rbac_bridge_py
    src_zephyr_governance_agent_spec_rbac_bridge_py ~~~ src_zephyr_governance_agent_spec_registry_py
    src_zephyr_governance_agent_spec_registry_py ~~~ src_zephyr_governance_architecture_governance_architecture_contracts_py
    src_zephyr_governance_architecture_governance_architecture_contracts_py ~~~ src_zephyr_governance_architecture_governance_architecture_principles_py
    src_zephyr_governance_architecture_governance_architecture_principles_py ~~~ src_zephyr_governance_architecture_governance_blueprint_bloat_monitor_py
    src_zephyr_governance_architecture_governance_blueprint_bloat_monitor_py ~~~ src_zephyr_governance_architecture_governance_blueprint_code_consistency_py
    src_zephyr_governance_architecture_governance_blueprint_code_consistency_py ~~~ src_zephyr_governance_architecture_governance_blueprint_reconciler_py
    src_zephyr_governance_architecture_governance_blueprint_reconciler_py ~~~ src_zephyr_governance_architecture_governance_construction_verifier_py
    src_zephyr_governance_architecture_governance_construction_verifier_py ~~~ src_zephyr_governance_architecture_governance_cross_env_consistency_py
    src_zephyr_governance_architecture_governance_cross_env_consistency_py ~~~ src_zephyr_governance_architecture_governance_dependency_manager_py
    src_zephyr_governance_architecture_governance_dependency_manager_py ~~~ src_zephyr_governance_architecture_governance_formal_verifier_py
    src_zephyr_governance_architecture_governance_formal_verifier_py ~~~ src_zephyr_governance_architecture_governance_gap_analyzer_py
    src_zephyr_governance_architecture_governance_gap_analyzer_py ~~~ src_zephyr_governance_architecture_governance_llm_impact_analyzer_py
    src_zephyr_governance_architecture_governance_llm_impact_analyzer_py ~~~ src_zephyr_governance_architecture_governance_local_first_arch_py
    src_zephyr_governance_architecture_governance_local_first_arch_py ~~~ src_zephyr_governance_architecture_governance_path_resolver_py
    src_zephyr_governance_architecture_governance_path_resolver_py ~~~ src_zephyr_governance_bridges_alerts_py
    src_zephyr_governance_bridges_alerts_py ~~~ src_zephyr_governance_bridges_spec_auditor_py
    src_zephyr_governance_bridges_spec_auditor_py ~~~ src_zephyr_governance_compliance_gate_a6_compliance_manager_py
    src_zephyr_governance_compliance_gate_a6_compliance_manager_py ~~~ src_zephyr_governance_compliance_gate_a6_compliance_mapper_py
    src_zephyr_governance_compliance_gate_a6_compliance_mapper_py ~~~ src_zephyr_governance_context_governance_command_chain_length_gate_py
    src_zephyr_governance_context_governance_command_chain_length_gate_py ~~~ src_zephyr_governance_context_governance_context_budget_py
    src_zephyr_governance_context_governance_context_budget_py ~~~ src_zephyr_governance_context_governance_context_manager_py
    src_zephyr_governance_context_governance_context_manager_py ~~~ src_zephyr_governance_context_governance_context_package_py
    src_zephyr_governance_context_governance_context_package_py ~~~ src_zephyr_governance_context_governance_context_recycling_py
    src_zephyr_governance_context_governance_context_recycling_py ~~~ src_zephyr_governance_context_governance_context_switch_governor_py
    src_zephyr_governance_context_governance_context_switch_governor_py ~~~ src_zephyr_governance_context_governance_context_waste_detector_py
    src_zephyr_governance_context_governance_context_waste_detector_py ~~~ src_zephyr_governance_context_governance_conversation_tax_detector_py
    src_zephyr_governance_context_governance_conversation_tax_detector_py ~~~ src_zephyr_governance_context_governance_instruction_bloat_detector_py
    src_zephyr_governance_context_governance_instruction_bloat_detector_py ~~~ src_zephyr_governance_context_governance_multi_turn_intent_analyzer_py
    src_zephyr_governance_context_governance_multi_turn_intent_analyzer_py ~~~ src_zephyr_governance_context_governance_prompt_lifecycle_py
    src_zephyr_governance_context_governance_prompt_lifecycle_py ~~~ src_zephyr_governance_context_governance_protocol_self_context_py
    src_zephyr_governance_context_governance_protocol_self_context_py ~~~ src_zephyr_governance_context_governance_think_time_model_py
    src_zephyr_governance_context_governance_think_time_model_py ~~~ src_zephyr_governance_data_governance_data_classification_py
    src_zephyr_governance_data_governance_data_classification_py ~~~ src_zephyr_governance_data_governance_data_lifecycle_py
    src_zephyr_governance_data_governance_data_lifecycle_py ~~~ src_zephyr_governance_data_governance_data_pipeline_guard_py
    src_zephyr_governance_data_governance_data_pipeline_guard_py ~~~ src_zephyr_governance_data_governance_data_quality_py
    src_zephyr_governance_data_governance_data_quality_py ~~~ src_zephyr_governance_data_governance_data_source_reliability_py
    src_zephyr_governance_data_governance_data_source_reliability_py ~~~ src_zephyr_governance_data_governance_exchange_partition_detector_py
    src_zephyr_governance_data_governance_exchange_partition_detector_py ~~~ src_zephyr_governance_data_governance_exchange_reg_monitor_py
    src_zephyr_governance_data_governance_exchange_reg_monitor_py ~~~ src_zephyr_governance_data_governance_miniqmt_provider_py
    src_zephyr_governance_data_governance_miniqmt_provider_py ~~~ src_zephyr_governance_data_governance_pricing_sync_py
    src_zephyr_governance_data_governance_pricing_sync_py ~~~ src_zephyr_governance_data_governance_realtime_streaming_py
    src_zephyr_governance_data_governance_realtime_streaming_py ~~~ src_zephyr_governance_evidence_pack_py
    src_zephyr_governance_evidence_pack_py ~~~ src_zephyr_governance_financial_governance_arbitrage_asymmetry_detector_py
    src_zephyr_governance_financial_governance_arbitrage_asymmetry_detector_py ~~~ src_zephyr_governance_financial_governance_atomic_transaction_manager_py
    src_zephyr_governance_financial_governance_atomic_transaction_manager_py ~~~ src_zephyr_governance_financial_governance_flash_crash_guard_py
    src_zephyr_governance_financial_governance_flash_crash_guard_py ~~~ src_zephyr_governance_financial_governance_fsm_verifier_py
    src_zephyr_governance_financial_governance_fsm_verifier_py ~~~ src_zephyr_governance_financial_governance_instrument_py
    src_zephyr_governance_financial_governance_instrument_py ~~~ src_zephyr_governance_financial_governance_microstructure_defense_py
    src_zephyr_governance_financial_governance_microstructure_defense_py ~~~ src_zephyr_governance_financial_governance_oms_risk_engine_py
    src_zephyr_governance_financial_governance_oms_risk_engine_py ~~~ src_zephyr_governance_financial_governance_risk_matrix_py
    src_zephyr_governance_financial_governance_risk_matrix_py ~~~ src_zephyr_governance_financial_governance_strategy_portfolio_py
    src_zephyr_governance_financial_governance_strategy_portfolio_py ~~~ src_zephyr_governance_financial_governance_strategy_scoper_py
    src_zephyr_governance_financial_governance_strategy_scoper_py ~~~ src_zephyr_governance_implementations_default_experiment_pipeline_py
    src_zephyr_governance_implementations_default_experiment_pipeline_py ~~~ src_zephyr_governance_implementations_default_security_gateway_py
    src_zephyr_governance_implementations_default_security_gateway_py ~~~ src_zephyr_governance_intelligence_governance_agent_debate_py
    src_zephyr_governance_intelligence_governance_agent_debate_py ~~~ src_zephyr_governance_intelligence_governance_ai_self_diagnosis_py
    src_zephyr_governance_intelligence_governance_ai_self_diagnosis_py ~~~ src_zephyr_governance_intelligence_governance_aisg_sandbox_py
    src_zephyr_governance_intelligence_governance_aisg_sandbox_py ~~~ src_zephyr_governance_intelligence_governance_autonomy_dashboard_py
    src_zephyr_governance_intelligence_governance_autonomy_dashboard_py ~~~ src_zephyr_governance_intelligence_governance_confidence_estimator_py
    src_zephyr_governance_intelligence_governance_confidence_estimator_py ~~~ src_zephyr_governance_intelligence_governance_confidence_quantifier_py
    src_zephyr_governance_intelligence_governance_confidence_quantifier_py ~~~ src_zephyr_governance_intelligence_governance_continuous_trust_py
    src_zephyr_governance_intelligence_governance_continuous_trust_py ~~~ src_zephyr_governance_intelligence_governance_cross_agent_conflict_detector_py
    src_zephyr_governance_intelligence_governance_cross_agent_conflict_detector_py ~~~ src_zephyr_governance_intelligence_governance_cross_assistant_adapter_py
    src_zephyr_governance_intelligence_governance_cross_assistant_adapter_py ~~~ src_zephyr_governance_intelligence_governance_delegation_manager_py
    src_zephyr_governance_intelligence_governance_delegation_manager_py ~~~ src_zephyr_governance_intelligence_governance_memory_provider_py
    src_zephyr_governance_intelligence_governance_memory_provider_py ~~~ src_zephyr_governance_intelligence_governance_meta_confidence_py
    src_zephyr_governance_intelligence_governance_meta_confidence_py ~~~ src_zephyr_governance_intelligence_governance_model_provider_data_py
    src_zephyr_governance_intelligence_governance_model_provider_data_py ~~~ src_zephyr_governance_intelligence_governance_model_router_py
    src_zephyr_governance_intelligence_governance_model_router_py ~~~ src_zephyr_governance_intelligence_governance_model_version_detector_py
    src_zephyr_governance_intelligence_governance_model_version_detector_py ~~~ src_zephyr_governance_intelligence_governance_multi_model_consensus_py
    src_zephyr_governance_intelligence_governance_multi_model_consensus_py ~~~ src_zephyr_governance_intelligence_governance_mvep_orchestrator_py
    src_zephyr_governance_intelligence_governance_mvep_orchestrator_py ~~~ src_zephyr_governance_intelligence_governance_provider_failover_py
    src_zephyr_governance_intelligence_governance_provider_failover_py ~~~ src_zephyr_governance_intelligence_governance_self_benchmark_py
    src_zephyr_governance_intelligence_governance_self_benchmark_py ~~~ src_zephyr_governance_intelligence_governance_self_test_py
    src_zephyr_governance_intelligence_governance_self_test_py ~~~ src_zephyr_governance_intelligence_governance_self_validator_py
    src_zephyr_governance_intelligence_governance_self_validator_py ~~~ src_zephyr_governance_intelligence_governance_subagent_hook_propagator_py
    src_zephyr_governance_intelligence_governance_subagent_hook_propagator_py ~~~ src_zephyr_governance_lifecycle_governance_api_lifecycle_py
    src_zephyr_governance_lifecycle_governance_api_lifecycle_py ~~~ src_zephyr_governance_lifecycle_governance_migration_strategy_py
    src_zephyr_governance_lifecycle_governance_migration_strategy_py ~~~ src_zephyr_governance_lifecycle_governance_paper_live_transition_py
    src_zephyr_governance_lifecycle_governance_paper_live_transition_py ~~~ src_zephyr_governance_lifecycle_governance_post_live_verification_py
    src_zephyr_governance_lifecycle_governance_post_live_verification_py ~~~ src_zephyr_governance_lifecycle_governance_transition_py
    src_zephyr_governance_lifecycle_governance_transition_py ~~~ src_zephyr_governance_observability_governance_analytics_base_py
    src_zephyr_governance_observability_governance_analytics_base_py ~~~ src_zephyr_governance_observability_governance_objective_tracker_py
    src_zephyr_governance_observability_governance_objective_tracker_py ~~~ src_zephyr_governance_persistence_battle_map_reader_py
    src_zephyr_governance_persistence_battle_map_reader_py ~~~ src_zephyr_governance_persistence_database_manager_py
    src_zephyr_governance_persistence_database_manager_py ~~~ src_zephyr_governance_persistence_database_service_py
    src_zephyr_governance_persistence_database_service_py ~~~ src_zephyr_governance_persistence_dataflowgraph_schema_py
    src_zephyr_governance_persistence_dataflowgraph_schema_py ~~~ src_zephyr_governance_persistence_decision_graph_reader_py
    src_zephyr_governance_persistence_decision_graph_reader_py ~~~ src_zephyr_governance_persistence_depgraph_reader_py
    src_zephyr_governance_persistence_depgraph_reader_py ~~~ src_zephyr_governance_persistence_protocol_state_store_py
    src_zephyr_governance_persistence_protocol_state_store_py ~~~ src_zephyr_governance_services_adapter_py
    src_zephyr_governance_services_adapter_py ~~~ src_zephyr_governance_services_cross_session_correlator_py
    src_zephyr_governance_services_cross_session_correlator_py ~~~ src_zephyr_governance_services_memory_provenance_py
    src_zephyr_governance_services_memory_provenance_py ~~~ src_zephyr_governance_strategies_strategy_registry_py
    src_zephyr_governance_strategies_strategy_registry_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_base_server_py
    src_zephyr_infrastructure_a2a_protocol_governance_base_server_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_audit_logger_py
    src_zephyr_infrastructure_a2a_protocol_governance_audit_logger_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_auditor_py
    src_zephyr_infrastructure_a2a_protocol_governance_auditor_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_error_codes_py
    src_zephyr_infrastructure_a2a_protocol_governance_error_codes_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_governance_adapter_py
    src_zephyr_infrastructure_a2a_protocol_governance_governance_adapter_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_phase_hold_py
    src_zephyr_infrastructure_a2a_protocol_governance_phase_hold_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_policy_engine_py
    src_zephyr_infrastructure_a2a_protocol_governance_policy_engine_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_protocol_py
    src_zephyr_infrastructure_a2a_protocol_governance_protocol_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_rate_limiter_py
    src_zephyr_infrastructure_a2a_protocol_governance_rate_limiter_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_session_manager_py
    src_zephyr_infrastructure_a2a_protocol_governance_session_manager_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py ~~~ src_zephyr_infrastructure_capacity_assurance_contracts_batch2_governance_py
    src_zephyr_infrastructure_capacity_assurance_contracts_batch2_governance_py ~~~ src_zephyr_integration_mcp_governance_server_py
    src_zephyr_integration_mcp_governance_server_py ~~~ src_zephyr_shared_capacity_governance_capacity_governance_loop_py
    src_zephyr_shared_capacity_governance_capacity_governance_loop_py ~~~ src_zephyr_shared_protocols_a2a_a2a_governance_py
    src_zephyr_shared_protocols_a2a_a2a_governance_py ~~~ tests_agent_rbac_test_session_aware_stash_red_blue_py
    tests_agent_rbac_test_session_aware_stash_red_blue_py ~~~ tests_git_test_git_commit_concurrent_py
    tests_git_test_git_commit_concurrent_py ~~~ tests_git_test_git_commit_extreme_py
    tests_git_test_git_commit_extreme_py ~~~ tests_git_test_git_commit_gateway_py
    tests_git_test_git_commit_gateway_py ~~~ tests_git_test_reconciler_verify_autosync_py
    tests_git_test_reconciler_verify_autosync_py ~~~ tests_governance_generators_test_check_gate_inventory_drift_py
    tests_governance_generators_test_check_gate_inventory_drift_py ~~~ tests_governance_generators_test_generate_gate_registry_py
    tests_governance_generators_test_generate_gate_registry_py ~~~ tests_governance_rule_bridge_test_worktree_lifecycle_py
    tests_governance_rule_bridge_test_worktree_lifecycle_py ~~~ tests_governance_test_ast_import_rewriter_py
    tests_governance_test_ast_import_rewriter_py ~~~ tests_io_test_depgraph_schema_py
    tests_io_test_depgraph_schema_py ~~~ tests_io_test_verify_schema_health_py
    tests_io_test_verify_schema_health_py ~~~ tests_rollback_test_concurrency_guard_red_blue_py
    tests_rollback_test_concurrency_guard_red_blue_py ~~~ tests_rollback_test_concurrent_mv_guard_py
    tests_rollback_test_concurrent_mv_guard_py ~~~ tests_task_test_task_repo_gateway_e2e_py
    tests_task_test_task_repo_gateway_e2e_py ~~~ tests_test_align_panoramas_py
    tests_test_align_panoramas_py ~~~ tests_test_dataflow_design_layout_py
    tests_test_dataflow_design_layout_py ~~~ tests_test_generate_dataflow_diagram_py
    tests_test_generate_dataflow_diagram_py ~~~ tests_test_generate_decision_diagram_py
    scripts_arch_guard_arch_ssot_py["架构ssot<br/>arch_guard 共享：仓库根路径、capacity_slo /<br/>invariants / contracts 装载。<br/>_arch_ssot<br/>文件: arch_guard/_arch_ssot.py<br/>(生产态 / production)"]
    scripts_check_naming_convention_py["检查namingconvention<br/>scripts的检查器，检查某项条件是否满足<br/>check_naming_convention<br/>文件: scripts/check_naming_convention.py<br/>(生产态 / production)"]
    scripts_construction_check_statuses_py["检查statuses<br/>construction包的check_statuses模块<br/>文件: construction/check_statuses.py<br/>(生产态 / production)"]
    scripts_git_commit_py["Git提交<br/>GitCommitGateway CLI 封装<br/>git_commit<br/>文件: scripts/git_commit.py<br/>(生产态 / production)"]
    scripts_git_guard_py["Git守卫<br/>Git Guard — 拦截危险 git 命令，防止破坏其他<br/>session 的文件锁。<br/>git_guard<br/>文件: scripts/git_guard.py<br/>(生产态 / production)"]
    scripts_mcp_generate_ide_config_py["生成ide配置<br/>从 config/mcp.json 生成各 IDE MCP 配置文件<br/>（MOD-INF-013 §5.3 Step 2）。<br/>generate_ide_config<br/>文件: mcp/generate_ide_config.py<br/>(生产态 / production)"]
    scripts_migration_dm311_autonomy_core_split_py["dm311autonomy核心split<br/>DM-311: autonomy_core/ 拆分迁移执行脚本。<br/>dm311_autonomy_core_split<br/>文件: migration/dm311_autonomy_core_split.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py["worktree生命周期<br/>WorktreeLifecycle — worktree 生命周期状态机<br/>（5态 + 8转换）<br/>worktree_lifecycle<br/>文件: rule_bridge/worktree_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_governance_capability_lookup_py["能力lookup<br/>CapabilityLookup —<br/>能力->真源文件反查注册表的查询 API + 扫描<br/>/派生逻辑（合一）<br/>capability_lookup<br/>文件: governance/capability_lookup.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_akshare_provider_py["akshare提供器<br/>D_DATA — Akshare Data Provider<br/>文件: data_governance/akshare_provider.py<br/>(生产态 / production)"]
    src_zephyr_governance_engine_pipeline_base_py["管线基类<br/>治理/engine包的pipeline_base模块<br/>文件: engine/pipeline_base.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_delegation_engine_py["delegation引擎<br/>Delegation Engine — MOD-INF-022<br/>文件: intelligence_governance<br/>/delegation_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_query_metrics_py["查询指标<br/>QueryMetrics — SQL 查询性能监控装饰器<br/>（SH-DB-001 v2.0）<br/>query_metrics<br/>文件: observability_governance/query_metrics.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_base_repo_py["基类repo<br/>base_repo — 异常类、状态机常量、工具函数（从<br/>task_repo.py 拆分，SRC-0066）<br/>文件: persistence/base_repo.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_battlemap_schema_py["persistence/battlemap_schema<br/>battlemap Schema DDL + 不变量声明<br/>文件: persistence/battlemap_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_decisiongraph_schema_py["decisiongraph结构<br/>decisiongraph Schema DDL + 不变量声明<br/>decisiongraph_schema<br/>文件: persistence/decisiongraph_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_pg_wrapper_py["pg包装<br/>psycopg2 connection 的 sqlite3 兼容 execute()<br/>包装器（单一规范副本）。<br/>pg_wrapper<br/>文件: persistence/pg_wrapper.py<br/>(生产态 / production)"]
    src_zephyr_governance_rule_patterns_py["规则模式<br/>治理规则正则 + 安全审计模式唯一真源 (SSoT)<br/>rule_patterns<br/>文件: governance/rule_patterns.py<br/>(生产态 / production)"]
    src_zephyr_governance_strategies_strategy_base_py["策略基类<br/>D_PORTFOLIO_CORE — StrategyBase + StrategyMeta<br/>+ StrategyRegistry<br/>文件: strategies/strategy_base.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py["A2A治理适配器<br/>A2A 治理适配器 — 连接 A2A 协议与 Governance 层<br/>a2a_governance_adapter<br/>文件: layer3_coordination<br/>/a2a_governance_adapter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_registry_governance_py["注册表治理<br/>Registry Governance — MOD-INF-037<br/>文件: infrastructure/registry_governance.py<br/>(生产态 / production)"]
    scripts_arch_guard_arch_ssot_py ~~~ scripts_check_naming_convention_py
    scripts_check_naming_convention_py ~~~ scripts_construction_check_statuses_py
    scripts_construction_check_statuses_py ~~~ scripts_git_commit_py
    scripts_git_commit_py ~~~ scripts_git_guard_py
    scripts_git_guard_py ~~~ scripts_mcp_generate_ide_config_py
    scripts_mcp_generate_ide_config_py ~~~ scripts_migration_dm311_autonomy_core_split_py
    scripts_migration_dm311_autonomy_core_split_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py
    src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py ~~~ src_zephyr_governance_capability_lookup_py
    src_zephyr_governance_capability_lookup_py ~~~ src_zephyr_governance_data_governance_akshare_provider_py
    src_zephyr_governance_data_governance_akshare_provider_py ~~~ src_zephyr_governance_engine_pipeline_base_py
    src_zephyr_governance_engine_pipeline_base_py ~~~ src_zephyr_governance_intelligence_governance_delegation_engine_py
    src_zephyr_governance_intelligence_governance_delegation_engine_py ~~~ src_zephyr_governance_observability_governance_query_metrics_py
    src_zephyr_governance_observability_governance_query_metrics_py ~~~ src_zephyr_governance_persistence_base_repo_py
    src_zephyr_governance_persistence_base_repo_py ~~~ src_zephyr_governance_persistence_battlemap_schema_py
    src_zephyr_governance_persistence_battlemap_schema_py ~~~ src_zephyr_governance_persistence_decisiongraph_schema_py
    src_zephyr_governance_persistence_decisiongraph_schema_py ~~~ src_zephyr_governance_persistence_pg_wrapper_py
    src_zephyr_governance_persistence_pg_wrapper_py ~~~ src_zephyr_governance_rule_patterns_py
    src_zephyr_governance_rule_patterns_py ~~~ src_zephyr_governance_strategies_strategy_base_py
    src_zephyr_governance_strategies_strategy_base_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py ~~~ src_zephyr_infrastructure_registry_governance_py
    src_zephyr_governance_depgraph_schema_py["依赖图模式<br/>depgraph Schema DDL + 版本化迁移框架<br/>depgraph_schema<br/>文件: governance/depgraph_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_provider_base_py["提供器基类<br/>D_DATA — Data Source Layer<br/>文件: intelligence_governance/provider_base.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_task_repo_py["任务repo<br/>TaskRepository — 任务登记表 CRUD + 状态机<br/>（T-1-04）<br/>task_repo<br/>文件: persistence/task_repo.py<br/>(生产态 / production)"]
    src_zephyr_governance_depgraph_schema_py ~~~ src_zephyr_governance_intelligence_governance_provider_base_py
    src_zephyr_governance_intelligence_governance_provider_base_py ~~~ src_zephyr_governance_persistence_task_repo_py
    src_zephyr_governance_architecture_governance_post_sync_validator_py["提交同步校验器<br/>post_sync_validator — post_sync_standard<br/>命令校验逻辑的唯一真源（SSoT）。<br/>文件: architecture_governance<br/>/post_sync_validator.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_projection_engine_py["projection引擎<br/>ProjectionEngine — 事件折叠为当前状态（DW-0003）<br/>projection_engine<br/>文件: observability_governance<br/>/projection_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_sqlite_schema_py["sqlite结构<br/>SQLite 元数据层 Schema DDL + 版本化迁移框架<br/>（T-1-02 + SH-DB-001 v2.0）<br/>sqlite_schema<br/>文件: persistence/sqlite_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_post_sync_validator_py ~~~ src_zephyr_governance_observability_governance_projection_engine_py
    src_zephyr_governance_observability_governance_projection_engine_py ~~~ src_zephyr_governance_persistence_sqlite_schema_py
    src_zephyr_governance_data_governance_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_governance_intelligence_governance_provider_base_py
    src_zephyr_governance_data_governance_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_governance_intelligence_governance_provider_base_py
    src_zephyr_governance_implementations_default_experiment_pipeline_py -->|导入依赖 / import_depends| src_zephyr_governance_engine_pipeline_base_py
    src_zephyr_governance_intelligence_governance_self_test_py -->|导入依赖 / import_depends| src_zephyr_governance_intelligence_governance_delegation_engine_py
    src_zephyr_governance_lifecycle_governance_transition_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_base_repo_py
    src_zephyr_governance_persistence_database_manager_py -->|导入依赖 / import_depends| src_zephyr_governance_observability_governance_query_metrics_py
    src_zephyr_governance_persistence_database_manager_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    src_zephyr_governance_persistence_battlemap_schema_py -->|导入依赖 / import_depends| src_zephyr_governance_depgraph_schema_py
    src_zephyr_governance_persistence_dataflowgraph_schema_py -->|导入依赖 / import_depends| src_zephyr_governance_depgraph_schema_py
    src_zephyr_governance_persistence_decisiongraph_schema_py -->|导入依赖 / import_depends| src_zephyr_governance_depgraph_schema_py
    src_zephyr_governance_persistence_battle_map_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_battlemap_schema_py
    src_zephyr_governance_persistence_battle_map_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_pg_wrapper_py
    src_zephyr_governance_persistence_decision_graph_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_decisiongraph_schema_py
    src_zephyr_governance_persistence_decision_graph_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_pg_wrapper_py
    src_zephyr_governance_persistence_depgraph_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_depgraph_schema_py
    src_zephyr_governance_persistence_depgraph_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_pg_wrapper_py
    src_zephyr_governance_persistence_task_repo_py -->|导入依赖 / import_depends| src_zephyr_governance_architecture_governance_post_sync_validator_py
    src_zephyr_governance_persistence_task_repo_py -->|导入依赖 / import_depends| src_zephyr_governance_observability_governance_projection_engine_py
    src_zephyr_governance_persistence_task_repo_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    src_zephyr_governance_strategies_strategy_registry_py -->|导入依赖 / import_depends| src_zephyr_governance_strategies_strategy_base_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py
    scripts_generate_pathway_registry_py -->|导入依赖 / import_depends| src_zephyr_governance_rule_patterns_py
    scripts_lock_files_py -->|导入依赖 / import_depends| scripts_check_naming_convention_py
    scripts_scaffold_py -->|导入依赖 / import_depends| src_zephyr_governance_capability_lookup_py
    scripts_scaffold_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_registry_governance_py
    scripts_arch_guard_check_cross_plane_communication_py -->|导入依赖 / import_depends| scripts_arch_guard_arch_ssot_py
    scripts_arch_guard_check_hot_path_purity_py -->|导入依赖 / import_depends| scripts_arch_guard_arch_ssot_py
    scripts_arch_guard_check_schema_consistency_py -->|导入依赖 / import_depends| scripts_arch_guard_arch_ssot_py
    scripts_construction_check_statuses_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    scripts_construction_check_statuses_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_construction_demo_a2a_chat_py -->|config_depends / config_depends| scripts_construction_check_statuses_py
    scripts_construction_check_transition_code_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_construction_finalize_tasks_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    scripts_construction_finalize_tasks_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_construction_demo_e2e_pipeline_py -->|导入依赖 / import_depends| src_zephyr_governance_data_governance_akshare_provider_py
    scripts_construction_test_event_hook_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    scripts_construction_test_event_hook_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_construction_d_init_task_system_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    scripts_construction_d_init_task_system_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_mcp_status_all_py -->|config_depends / config_depends| scripts_mcp_generate_ide_config_py
    scripts_migration_governance_root_split_py -->|config_depends / config_depends| scripts_migration_dm311_autonomy_core_split_py
    tests_git_test_reconciler_verify_autosync_py -->|测试依赖 / test_depends| scripts_git_commit_py
    tests_governance_rule_bridge_test_worktree_lifecycle_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py
    tests_io_test_verify_schema_health_py -->|测试依赖 / test_depends| src_zephyr_governance_persistence_decisiongraph_schema_py
    tests_rollback_test_concurrent_mv_guard_py -->|测试依赖 / test_depends| scripts_git_guard_py
    tests_rollback_test_concurrency_guard_red_blue_py -->|测试依赖 / test_depends| scripts_git_guard_py
    tests_task_test_task_repo_gateway_e2e_py -->|测试依赖 / test_depends| src_zephyr_governance_persistence_task_repo_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_miniqmt_provider_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_A2A["A2A通信<br/>Agent 与 Agent 之间的通信协议层，负责 AI<br/>代理间的消息传递、请求路由和协议适配<br/>A2A Communication<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py -->|导入依赖 / import_depends| D_INFRA_A2A
    D_GOV_SCRIPTS["脚本治理<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>Script Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_arch_guard_tools_build_ocp_manifest_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    src_zephyr_governance_persistence_base_repo_py -->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["对抗验证<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验<br/>证<br/>Adversarial Validation<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_integration_mcp_governance_server_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_governance_observability_governance_query_metrics_py -->|导入依赖 / import_depends| D_SHARED
    scripts_arch_guard_tools_inject_idempotency_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    src_zephyr_integration_mcp_governance_server_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_persistence_decisiongraph_schema_py -->|导入依赖 / import_depends| D_SHARED
    scripts_arch_guard_fitness_functions_check_log_secret_leak_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    D_RISK["风控<br/>风控，负责风险指标计算、风险限额管理和风险预警<br/>Risk Control<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_construction_demo_e2e_pipeline_py -->|导入依赖 / import_depends| D_RISK
    scripts_arch_guard_arch_ssot_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_RULE["规则治理<br/>规则治理，负责规则注册、规则版本和规则依赖管理<br/>Rule Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_task_repo_py -->|导入依赖 / import_depends| D_GOV_RULE
    scripts_arch_guard_fitness_functions_check_ocp_signatures_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    scripts_arch_guard_tools_patch_p1_paths_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    D_EX_CORE["执行核心<br/>执行核心，负责订单执行引擎、执行策略和执行管理<br/>Execution Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_EX_CORE -->|contract / contract| src_zephyr_governance_adapters_risk_validation_bridge_py
    D_EX_CORE -->|contract / contract| src_zephyr_governance_strategies_strategy_base_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_governance_adapters_risk_validation_bridge_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_governance_strategies_strategy_base_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_persistence_battlemap_schema_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_zoomable_html_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_zoomable_html_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_zoomable_html_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_persistence_dataflowgraph_schema_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_persistence_decisiongraph_schema_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_persistence_battle_map_reader_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_persistence_depgraph_reader_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_persistence_battle_map_reader_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_depgraph_schema_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_persistence_decisiongraph_schema_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_rule_registry_collection_yaml,scripts_a2a_full_verification_py,scripts_arch_guard_arch_ssot_py,scripts_arch_guard_tools_build_ocp_manifest_py,scripts_arch_guard_tools_inject_idempotency_py,scripts_arch_guard_tools_patch_p1_paths_py,scripts_arch_guard_check_acl_boundary_py,scripts_arch_guard_check_cross_plane_communication_py,scripts_arch_guard_check_fe_acl_boundary_py,scripts_arch_guard_check_hot_path_purity_py,scripts_arch_guard_check_scaffold_exit_gates_py,scripts_arch_guard_check_schema_consistency_py,scripts_arch_guard_fitness_functions_check_aisg_gateway_py,scripts_arch_guard_fitness_functions_check_audit_log_immutability_py,scripts_arch_guard_fitness_functions_check_capacity_slo_ssot_py,scripts_arch_guard_fitness_functions_check_daily_loss_limit_py,scripts_arch_guard_fitness_functions_check_hot_warm_ipc_py,scripts_arch_guard_fitness_functions_check_idempotency_key_py,scripts_arch_guard_fitness_functions_check_log_secret_leak_py,scripts_arch_guard_fitness_functions_check_no_cross_plane_mutable_state_py,scripts_arch_guard_fitness_functions_check_ocp_signatures_py,scripts_arch_guard_fitness_functions_check_pit_compliance_py,scripts_arch_guard_fitness_functions_check_position_limit_py,scripts_arch_guard_fitness_functions_check_risk_params_consistency_py,scripts_arch_guard_fitness_functions_check_survivorship_bias_py,scripts_arch_guard_fitness_functions_check_warm_cold_async_py,scripts_arch_guard_run_all_py,scripts_check_naming_convention_py,scripts_construction_e2e_check_py,scripts_construction_e2e_deep_py,scripts_construction_check_statuses_py,scripts_construction_check_transition_code_py,scripts_construction_d_init_task_system_py,scripts_construction_demo_a2a_chat_py,scripts_construction_demo_a2a_coordination_py,scripts_construction_demo_e2e_pipeline_py,scripts_construction_finalize_tasks_py,scripts_construction_local_layer_daemon_py,scripts_construction_reset_test_task_py,scripts_construction_start_brain_py,scripts_construction_test_event_hook_py,scripts_context_generate_architecture_context_py,scripts_diagnose_breadth_failed_py,scripts_dm90971_add_test_headers_py,scripts_fix_freeze_manifest_py,scripts_fix_orphan_all_py,scripts_generate_manifest_py,scripts_generate_pathway_registry_py,scripts_git_commit_py,scripts_git_guard_py,scripts_governance_d5_architecture_generators_zoomable_html_py,scripts_governance_d7_code_check_pure_shim_py,scripts_governance_generators_generate_rule_ai_perception_index_py,scripts_hooks_auto_handoff_log_py,scripts_lock_files_py,scripts_mcp_generate_ide_config_py,scripts_mcp_launcher_py,scripts_mcp_start_all_py,scripts_mcp_status_all_py,scripts_mcp_stop_all_py,scripts_migration_dm311_autonomy_core_split_py,scripts_migration_dm314_infra_ops_split_py,scripts_migration_governance_root_split_py,scripts_ops_verify_header_completeness_py,scripts_post_checkout_guard_py,scripts_pre_commit_verify_dedup_py,scripts_rollback_py,scripts_run_deepseek_v4_exam_py,scripts_run_ollama_exam_py,scripts_scaffold_py,scripts_setup_git_guard_aliases_py,src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py,src_zephyr_governance_a2a_init_py,src_zephyr_governance_adapters_risk_validation_bridge_py,src_zephyr_governance_adapters_simulation_broker_py,src_zephyr_governance_agent_spec_init_py,src_zephyr_governance_agent_spec_a2a_failure_py,src_zephyr_governance_agent_spec_rbac_bridge_py,src_zephyr_governance_agent_spec_registry_py,src_zephyr_governance_architecture_governance_architecture_contracts_py,src_zephyr_governance_architecture_governance_architecture_principles_py,src_zephyr_governance_architecture_governance_blueprint_bloat_monitor_py,src_zephyr_governance_architecture_governance_blueprint_code_consistency_py,src_zephyr_governance_architecture_governance_blueprint_reconciler_py,src_zephyr_governance_architecture_governance_construction_verifier_py,src_zephyr_governance_architecture_governance_cross_env_consistency_py,src_zephyr_governance_architecture_governance_dependency_manager_py,src_zephyr_governance_architecture_governance_formal_verifier_py,src_zephyr_governance_architecture_governance_gap_analyzer_py,src_zephyr_governance_architecture_governance_llm_impact_analyzer_py,src_zephyr_governance_architecture_governance_local_first_arch_py,src_zephyr_governance_architecture_governance_path_resolver_py,src_zephyr_governance_architecture_governance_post_sync_validator_py,src_zephyr_governance_bridges_alerts_py,src_zephyr_governance_bridges_spec_auditor_py,src_zephyr_governance_capability_lookup_py,src_zephyr_governance_compliance_gate_a6_compliance_manager_py,src_zephyr_governance_compliance_gate_a6_compliance_mapper_py,src_zephyr_governance_context_governance_command_chain_length_gate_py,src_zephyr_governance_context_governance_context_budget_py,src_zephyr_governance_context_governance_context_manager_py,src_zephyr_governance_context_governance_context_package_py,src_zephyr_governance_context_governance_context_recycling_py,src_zephyr_governance_context_governance_context_switch_governor_py,src_zephyr_governance_context_governance_context_waste_detector_py,src_zephyr_governance_context_governance_conversation_tax_detector_py,src_zephyr_governance_context_governance_instruction_bloat_detector_py,src_zephyr_governance_context_governance_multi_turn_intent_analyzer_py,src_zephyr_governance_context_governance_prompt_lifecycle_py,src_zephyr_governance_context_governance_protocol_self_context_py,src_zephyr_governance_context_governance_think_time_model_py,src_zephyr_governance_data_governance_akshare_provider_py,src_zephyr_governance_data_governance_data_classification_py,src_zephyr_governance_data_governance_data_lifecycle_py,src_zephyr_governance_data_governance_data_pipeline_guard_py,src_zephyr_governance_data_governance_data_quality_py,src_zephyr_governance_data_governance_data_source_reliability_py,src_zephyr_governance_data_governance_exchange_partition_detector_py,src_zephyr_governance_data_governance_exchange_reg_monitor_py,src_zephyr_governance_data_governance_miniqmt_provider_py,src_zephyr_governance_data_governance_pricing_sync_py,src_zephyr_governance_data_governance_realtime_streaming_py,src_zephyr_governance_depgraph_schema_py,src_zephyr_governance_engine_pipeline_base_py,src_zephyr_governance_evidence_pack_py,src_zephyr_governance_financial_governance_arbitrage_asymmetry_detector_py,src_zephyr_governance_financial_governance_atomic_transaction_manager_py,src_zephyr_governance_financial_governance_flash_crash_guard_py,src_zephyr_governance_financial_governance_fsm_verifier_py,src_zephyr_governance_financial_governance_instrument_py,src_zephyr_governance_financial_governance_microstructure_defense_py,src_zephyr_governance_financial_governance_oms_risk_engine_py,src_zephyr_governance_financial_governance_risk_matrix_py,src_zephyr_governance_financial_governance_strategy_portfolio_py,src_zephyr_governance_financial_governance_strategy_scoper_py,src_zephyr_governance_implementations_default_experiment_pipeline_py,src_zephyr_governance_implementations_default_security_gateway_py,src_zephyr_governance_intelligence_governance_agent_debate_py,src_zephyr_governance_intelligence_governance_ai_self_diagnosis_py,src_zephyr_governance_intelligence_governance_aisg_sandbox_py,src_zephyr_governance_intelligence_governance_autonomy_dashboard_py,src_zephyr_governance_intelligence_governance_confidence_estimator_py,src_zephyr_governance_intelligence_governance_confidence_quantifier_py,src_zephyr_governance_intelligence_governance_continuous_trust_py,src_zephyr_governance_intelligence_governance_cross_agent_conflict_detector_py,src_zephyr_governance_intelligence_governance_cross_assistant_adapter_py,src_zephyr_governance_intelligence_governance_delegation_engine_py,src_zephyr_governance_intelligence_governance_delegation_manager_py,src_zephyr_governance_intelligence_governance_memory_provider_py,src_zephyr_governance_intelligence_governance_meta_confidence_py,src_zephyr_governance_intelligence_governance_model_provider_data_py,src_zephyr_governance_intelligence_governance_model_router_py,src_zephyr_governance_intelligence_governance_model_version_detector_py,src_zephyr_governance_intelligence_governance_multi_model_consensus_py,src_zephyr_governance_intelligence_governance_mvep_orchestrator_py,src_zephyr_governance_intelligence_governance_provider_base_py,src_zephyr_governance_intelligence_governance_provider_failover_py,src_zephyr_governance_intelligence_governance_self_benchmark_py,src_zephyr_governance_intelligence_governance_self_test_py,src_zephyr_governance_intelligence_governance_self_validator_py,src_zephyr_governance_intelligence_governance_subagent_hook_propagator_py,src_zephyr_governance_lifecycle_governance_api_lifecycle_py,src_zephyr_governance_lifecycle_governance_migration_strategy_py,src_zephyr_governance_lifecycle_governance_paper_live_transition_py,src_zephyr_governance_lifecycle_governance_post_live_verification_py,src_zephyr_governance_lifecycle_governance_transition_py,src_zephyr_governance_observability_governance_analytics_base_py,src_zephyr_governance_observability_governance_objective_tracker_py,src_zephyr_governance_observability_governance_projection_engine_py,src_zephyr_governance_observability_governance_query_metrics_py,src_zephyr_governance_persistence_base_repo_py,src_zephyr_governance_persistence_battle_map_reader_py,src_zephyr_governance_persistence_battlemap_schema_py,src_zephyr_governance_persistence_database_manager_py,src_zephyr_governance_persistence_database_service_py,src_zephyr_governance_persistence_dataflowgraph_schema_py,src_zephyr_governance_persistence_decision_graph_reader_py,src_zephyr_governance_persistence_decisiongraph_schema_py,src_zephyr_governance_persistence_depgraph_reader_py,src_zephyr_governance_persistence_pg_wrapper_py,src_zephyr_governance_persistence_protocol_state_store_py,src_zephyr_governance_persistence_sqlite_schema_py,src_zephyr_governance_persistence_task_repo_py,src_zephyr_governance_rule_patterns_py,src_zephyr_governance_services_adapter_py,src_zephyr_governance_services_cross_session_correlator_py,src_zephyr_governance_services_memory_provenance_py,src_zephyr_governance_strategies_strategy_base_py,src_zephyr_governance_strategies_strategy_registry_py,src_zephyr_infrastructure_a2a_protocol_governance_base_server_py,src_zephyr_infrastructure_a2a_protocol_governance_audit_logger_py,src_zephyr_infrastructure_a2a_protocol_governance_auditor_py,src_zephyr_infrastructure_a2a_protocol_governance_error_codes_py,src_zephyr_infrastructure_a2a_protocol_governance_governance_adapter_py,src_zephyr_infrastructure_a2a_protocol_governance_phase_hold_py,src_zephyr_infrastructure_a2a_protocol_governance_policy_engine_py,src_zephyr_infrastructure_a2a_protocol_governance_protocol_py,src_zephyr_infrastructure_a2a_protocol_governance_rate_limiter_py,src_zephyr_infrastructure_a2a_protocol_governance_session_manager_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch2_governance_py,src_zephyr_infrastructure_registry_governance_py,src_zephyr_integration_mcp_governance_server_py,src_zephyr_shared_capacity_governance_capacity_governance_loop_py,src_zephyr_shared_protocols_a2a_a2a_governance_py,tests_agent_rbac_test_session_aware_stash_red_blue_py,tests_git_test_git_commit_concurrent_py,tests_git_test_git_commit_extreme_py,tests_git_test_git_commit_gateway_py,tests_git_test_reconciler_verify_autosync_py,tests_governance_generators_test_check_gate_inventory_drift_py,tests_governance_generators_test_generate_gate_registry_py,tests_governance_rule_bridge_test_worktree_lifecycle_py,tests_governance_test_ast_import_rewriter_py,tests_io_test_depgraph_schema_py,tests_io_test_verify_schema_health_py,tests_rollback_test_concurrency_guard_red_blue_py,tests_rollback_test_concurrent_mv_guard_py,tests_task_test_task_repo_gateway_e2e_py,tests_test_align_panoramas_py,tests_test_dataflow_design_layout_py,tests_test_generate_dataflow_diagram_py,tests_test_generate_decision_diagram_py production
    class D_SHARED,D_INFRA_A2A,D_GOV_SCRIPTS,D_SECURITY,D_RISK,D_GOV_RULE,D_EX_CORE external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 224 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_rule_registry_collection_yaml["规则注册表收集<br/>catalogs包的rule_registry_collection模块<br/>文件: catalogs/rule_registry_collection.yaml<br/>(生产态 / production)"]
    scripts_a2a_full_verification_py["A2Afull验证<br/>A2A Protocol 全链路满分验证脚本<br/>a2a_full_verification<br/>文件: scripts/a2a_full_verification.py<br/>(生产态 / production)"]
    scripts_arch_guard_tools_build_ocp_manifest_py["buildocp清单<br/>从 cross_layer_contracts.yaml 生成 OCP<br/>冻结契约指纹（INV-009）。<br/>build_ocp_manifest<br/>文件: _tools/build_ocp_manifest.py<br/>(生产态 / production)"]
    scripts_arch_guard_tools_inject_idempotency_py["inject幂等性<br/>为所有 P0/P1 契约添加 idempotency_key<br/>字段——状态感知版本。<br/>inject_idempotency<br/>文件: _tools/inject_idempotency.py<br/>(生产态 / production)"]
    scripts_arch_guard_tools_patch_p1_paths_py["补丁p1paths<br/>一次性工具——为 9 个 P1 契约补齐 physical_path<br/>并运行 codegen。<br/>patch_p1_paths<br/>文件: _tools/patch_p1_paths.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_acl_boundary_py["检查aclboundary<br/>Broker ACL 边界强制执行<br/>check_acl_boundary<br/>文件: arch_guard/check_acl_boundary.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_cross_plane_communication_py["check跨planecommunication<br/>INV-011 拓扑 + 静态越界 import 嗅探<br/>check_cross_plane_communication<br/>文件: arch_guard<br/>/check_cross_plane_communication.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_fe_acl_boundary_py["检查feaclboundary<br/>INV-006 前端 ACL（仓库内有前端树则启用）<br/>check_fe_acl_boundary<br/>文件: arch_guard/check_fe_acl_boundary.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_hot_path_purity_py["检查hot路径purity<br/>INV-012 Hot 路径 Python 禁 asyncio（配置驱动）<br/>check_hot_path_purity<br/>文件: arch_guard/check_hot_path_purity.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_scaffold_exit_gates_py["checkscaffold退出门禁<br/>scaffold→experimental 安全门禁检查<br/>check_scaffold_exit_gates<br/>文件: arch_guard/check_scaffold_exit_gates.py<br/>(生产态 / production)"]
    scripts_arch_guard_check_schema_consistency_py["检查模式一致性<br/>INV-010 契约物理路径存在性（Schema canonical<br/>基线）<br/>check_schema_consistency<br/>文件: arch_guard/check_schema_consistency.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_aisg_gateway_py["检查aisg网关<br/>AISG 拦截门禁 (INV-015) Phase B 升级<br/>check_aisg_gateway<br/>文件: fitness_functions/check_aisg_gateway.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_audit_log_immutability_py["check审计日志immutability<br/>审计日志不可篡改检查<br/>check_audit_log_immutability<br/>文件: fitness_functions<br/>/check_audit_log_immutability.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_capacity_slo_ssot_py["check容量slossot<br/>yaml 注册表 + 与 invariants 数字对齐（SSoT<br/>闭环）<br/>check_capacity_slo_ssot<br/>文件: fitness_functions<br/>/check_capacity_slo_ssot.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_daily_loss_limit_py["checkdaily损失limit<br/>日损失限额自动暂停<br/>check_daily_loss_limit<br/>文件: fitness_functions<br/>/check_daily_loss_limit.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_hot_warm_ipc_py["检查hotwarmipc<br/>INV-018 Hot↔Warm IPC 协议检查<br/>check_hot_warm_ipc<br/>文件: fitness_functions/check_hot_warm_ipc.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_idempotency_key_py["检查幂等性密钥<br/>幂等 Key 字段存在性检查<br/>check_idempotency_key<br/>文件: fitness_functions/check_idempotency_key.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_log_secret_leak_py["check日志密钥leak<br/>R2 日志不写 secret 适应度函数<br/>check_log_secret_leak<br/>文件: fitness_functions/check_log_secret_leak.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_no_cross_plane_mutable_state_py["checkno跨planemutable状态<br/>INV-020 跨平面共享可变状态检查<br/>check_no_cross_plane_mutable_state<br/>文件: fitness_functions<br/>/check_no_cross_plane_mutable_state.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_ocp_signatures_py["检查ocpsignatures<br/>OCP 冻结契约指纹校验<br/>check_ocp_signatures<br/>文件: fitness_functions/check_ocp_signatures.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_pit_compliance_py["检查pit合规<br/>（Point-in-Time）铁律强制执行<br/>check_pit_compliance<br/>文件: fitness_functions/check_pit_compliance.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_position_limit_py["检查持仓限制<br/>单一持仓限制 ≤ 5% NAV<br/>check_position_limit<br/>文件: fitness_functions/check_position_limit.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_risk_params_consistency_py["check风险paramsconsistency<br/>风控参数真源 (INV-013) + 与 INV-002 声明对齐<br/>check_risk_params_consistency<br/>文件: fitness_functions<br/>/check_risk_params_consistency.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_survivorship_bias_py["检查survivorshipbias<br/>Survivorship 策略门禁<br/>check_survivorship_bias<br/>文件: fitness_functions<br/>/check_survivorship_bias.py<br/>(生产态 / production)"]
    scripts_arch_guard_fitness_functions_check_warm_cold_async_py["checkwarm冷异步<br/>INV-019 Warm→Cold 异步通信检查<br/>check_warm_cold_async<br/>文件: fitness_functions/check_warm_cold_async.py<br/>(生产态 / production)"]
    scripts_arch_guard_run_all_py["运行all<br/>Architecture Guard 编排器<br/>run_all<br/>文件: arch_guard/run_all.py<br/>(生产态 / production)"]
    scripts_construction_e2e_check_py["端到端检查<br/>construction包的e2e_check模块<br/>_e2e_check<br/>文件: construction/_e2e_check.py<br/>(生产态 / production)"]
    scripts_construction_e2e_deep_py["端到端deep<br/>依赖检查statuses工作<br/>_e2e_deep<br/>文件: construction/_e2e_deep.py<br/>(生产态 / production)"]
    scripts_construction_check_transition_code_py["检查转换代码<br/>construction包的check_transition_code模块<br/>文件: construction/check_transition_code.py<br/>(生产态 / production)"]
    scripts_construction_d_init_task_system_py["初始化任务系统数据库 +<br/>创建任务系统自身的施工任务卡（吃狗粮）<br/>construction包的d_init_task_system模块<br/>文件: construction/d_init_task_system.py<br/>(生产态 / production)"]
    scripts_construction_demo_a2a_chat_py["A2A 多 Agent 聊天演示 - Alpha 和 Beta<br/>讨论项目评估<br/>construction包的demo_a2a_chat模块<br/>文件: construction/demo_a2a_chat.py<br/>(生产态 / production)"]
    scripts_construction_demo_a2a_coordination_py["A2A 协议协调任务演示<br/>construction包的demo_a2a_coordination模块<br/>文件: construction/demo_a2a_coordination.py<br/>(生产态 / production)"]
    scripts_construction_demo_e2e_pipeline_py["demoe2e管线<br/>C-track 端到端演示 —— 全流水线一次性运行<br/>demo_e2e_pipeline<br/>文件: construction/demo_e2e_pipeline.py<br/>(生产态 / production)"]
    scripts_construction_finalize_tasks_py["finalize任务<br/>依赖任务repo、sqlite模式、包入口工作<br/>finalize_tasks<br/>文件: construction/finalize_tasks.py<br/>(生产态 / production)"]
    scripts_construction_local_layer_daemon_py["本地层daemon<br/>L2 本地模型层守护进程（薄包装，DEPRECATED）<br/>local_layer_daemon<br/>文件: construction/local_layer_daemon.py<br/>(生产态 / production)"]
    scripts_construction_reset_test_task_py["重置测试任务<br/>依赖sqlite模式工作<br/>reset_test_task<br/>文件: construction/reset_test_task.py<br/>(生产态 / production)"]
    scripts_construction_start_brain_py["启动brain<br/>ZephyrAlpha 系统大脑一键启动<br/>start_brain<br/>文件: construction/start_brain.py<br/>(生产态 / production)"]
    scripts_construction_test_event_hook_py["测试事件钩子<br/>construction的事件，定义和分发事件<br/>test_event_hook<br/>文件: construction/test_event_hook.py<br/>(生产态 / production)"]
    scripts_context_generate_architecture_context_py["生成架构上下文<br/>预编译架构上下文包生成器<br/>generate_architecture_context<br/>文件: context/generate_architecture_context.py<br/>(生产态 / production)"]
    scripts_diagnose_breadth_failed_py["diagnosebreadth失败<br/>诊断 breadth_failed 能力的根因。<br/>diagnose_breadth_failed<br/>文件: scripts/diagnose_breadth_failed.py<br/>(生产态 / production)"]
    scripts_dm90971_add_test_headers_py["dm90971add测试headers<br/>dm90971新增测试headers。DM-90971: Batch add<br/>module_id scope prefix + governance anchor<br/>headers to test files.<br/>文件: scripts/dm90971_add_test_headers.py<br/>(生产态 / production)"]
    scripts_fix_freeze_manifest_py["修复freeze清单<br/>修复freezemanifest。Fix freezemanifest.yaml -<br/>comprehensive repair of all corrupted desc<br/>fields.<br/>文件: scripts/fix_freeze_manifest.py<br/>(生产态 / production)"]
    scripts_fix_orphan_all_py["修复孤儿all<br/>自动修复 __init__.py __all__ 孤儿模块<br/>fix_orphan_all<br/>文件: scripts/fix_orphan_all.py<br/>(生产态 / production)"]
    scripts_generate_manifest_py["generate清单<br/>生成manifest。Generate complete<br/>script_manifest.yaml from scripts/ tree scan.<br/>文件: scripts/generate_manifest.py<br/>(生产态 / production)"]
    scripts_generate_pathway_registry_py["generatepathway注册表<br/>从所有 MOD 蓝图的 §路径索引 章节自动生成<br/>system-pathway-registry.yaml。<br/>generate_pathway_registry<br/>文件: scripts/generate_pathway_registry.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_zoomable_html_py["可缩放 Mermaid HTML 生成器（共享模块）。<br/>生成器包的zoomable_html模块<br/>文件: generators/zoomable_html.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_pure_shim_py["检查pureshim<br/>GATE-NO-PURE-SHIM 检测器（治本漏洞1 2026-06-29）<br/>check_pure_shim<br/>文件: d7_code/check_pure_shim.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_rule_ai_perception_index_py["generate规则aiperception索引<br/>规则AI感知索引生成器<br/>（#ARCH-GOV-CONVERGENCE-META Phase 3.2a）<br/>generate_rule_ai_perception_index<br/>文件: generators<br/>/generate_rule_ai_perception_index.py<br/>(生产态 / production)"]
    scripts_hooks_auto_handoff_log_py["自动handoff日志<br/>执行 git 命令并返回 stdout（UTF-8 解码）。<br/>auto_handoff_log<br/>文件: hooks/auto_handoff_log.py<br/>(生产态 / production)"]
    scripts_lock_files_py["锁files<br/>— AI 对话文件锁协议（硬规则执行工具）<br/>lock_files<br/>文件: scripts/lock_files.py<br/>(生产态 / production)"]
    scripts_mcp_launcher_py["MCP DAG 编排启动器（MOD-INF-013 §14 拓扑排序 +<br/>Pro<br/>cessLifecycleGateway 管理）<br/>launcher<br/>文件: mcp/launcher.py<br/>(生产态 / production)"]
    scripts_mcp_start_all_py["启动all<br/>MCP 全 Server 启动脚本 — DEPRECATED.<br/>start_all<br/>文件: mcp/start_all.py<br/>(生产态 / production)"]
    scripts_mcp_status_all_py["状态all<br/>MCP 全 Server 状态检查脚本（MOD-INF-013 §14）。<br/>status_all<br/>文件: mcp/status_all.py<br/>(生产态 / production)"]
    scripts_mcp_stop_all_py["停止all<br/>MCP 全 Server 停止脚本（MOD-INF-013 §14）。<br/>stop_all<br/>文件: mcp/stop_all.py<br/>(生产态 / production)"]
    scripts_migration_dm314_infra_ops_split_py["dm314基础设施运维拆分<br/>DM-314: infra_ops/ 拆分迁移执行脚本。<br/>dm314_infra_ops_split<br/>文件: migration/dm314_infra_ops_split.py<br/>(生产态 / production)"]
    scripts_migration_governance_root_split_py["治理根拆分<br/>ARCH-031: governance/ root flat-files split<br/>migration orchestrator<br/>文件: migration/governance_root_split.py<br/>(生产态 / production)"]
    scripts_ops_verify_header_completeness_py["文件头部完整性校验（6 格式统一入口）<br/>运维包的verify_header_completeness模块<br/>文件: ops/verify_header_completeness.py<br/>(生产态 / production)"]
    scripts_post_checkout_guard_py["postcheckout守卫<br/>Post-checkout Guard — 事后检测 checkout<br/>是否覆盖了其他 session 的文件锁。<br/>post_checkout_guard<br/>文件: scripts/post_checkout_guard.py<br/>(生产态 / production)"]
    scripts_pre_commit_verify_dedup_py["verify去重<br/>pre_commit 验证脚本 — 委托给 code-dedup-engine<br/>CLI verify 子命令.<br/>verify_dedup<br/>文件: pre_commit/verify_dedup.py<br/>(生产态 / production)"]
    scripts_rollback_py["回滚<br/>Rollback System CLI — MOD-INF-021 v0.10.0<br/>Git-native+SQLite Checkpoint 操作入口。<br/>文件: scripts/rollback.py<br/>(生产态 / production)"]
    scripts_run_deepseek_v4_exam_py["运行deepseekv4exam<br/>DeepSeek V4 入职考试运行脚本<br/>run_deepseek_v4_exam<br/>文件: scripts/run_deepseek_v4_exam.py<br/>(生产态 / production)"]
    scripts_run_ollama_exam_py["运行ollamaexam<br/>Ollama 入职考试运行脚本<br/>run_ollama_exam<br/>文件: scripts/run_ollama_exam.py<br/>(生产态 / production)"]
    scripts_scaffold_py["scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TW<br/>ZephyrAlpha 唯一创建入口（RULE-TWO 强制执行器）<br/>文件: scripts/scaffold.py<br/>(生产态 / production)"]
    scripts_setup_git_guard_aliases_py["setupGit守卫aliases<br/>Setup/Remove Git Aliases for Git Guard —<br/>自动化集成入口。<br/>setup_git_guard_aliases<br/>文件: scripts/setup_git_guard_aliases.py<br/>(生产态 / production)"]
    src_zephyr_governance_a2a_init_py["governance/a2a 包入口<br/>管理governance.a2a子包的加载和懒导入<br/>文件: a2a/__init__.py<br/>(生产态 / production)"]
    src_zephyr_governance_adapters_risk_validation_bridge_py["风险验证桥接<br/>D_EXECUTION_CORE — Risk Validation Bridge<br/>(DW-239)<br/>文件: adapters/risk_validation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_governance_adapters_simulation_broker_py["仿真经纪人<br/>D_EXECUTION_CORE — Simulation Broker Adapter<br/>文件: adapters/simulation_broker.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_spec_init_py["governance/agent-spec 包入口<br/>管理governance.agent-spec子包的加载和懒导入<br/>文件: agent-spec/__init__.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_spec_a2a_failure_py["A2A故障<br/>G-CT-008 消费端 — Escalation.on_a2a_failure()<br/>跨 agent 通信失败升级.<br/>文件: agent_spec/a2a_failure.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_spec_rbac_bridge_py["RBAC桥接<br/>G-CT-007 契约：Budget -> RBAC 配额限制.<br/>rbac_bridge<br/>文件: agent_spec/rbac_bridge.py<br/>(生产态 / production)"]
    src_zephyr_governance_agent_spec_registry_py["注册表<br/>G-CT-003 契约：Agent Spec -> RBAC 能力检查.<br/>registry<br/>文件: agent_spec/registry.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_architecture_contracts_py["架构契约<br/>治理/architecture<br/>governance包的architecture_contracts模块<br/>文件: architecture_governance<br/>/architecture_contracts.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_architecture_principles_py["装饰器：为函数标记适用的架构原则。<br/>治理/architecture<br/>governance包的architecture_principles模块<br/>文件: architecture_governance<br/>/architecture_principles.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_blueprint_bloat_monitor_py["蓝图bloat监控器<br/>Blueprint Bloat Monitor — v0.11.0<br/>蓝图膨胀监控器。<br/>blueprint_bloat_monitor<br/>文件: architecture_governance<br/>/blueprint_bloat_monitor.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_blueprint_code_consistency_py["蓝图代码一致性<br/>Blueprint-Code Consistency Gate — MOD-INF-022<br/>文件: architecture_governance<br/>/blueprint_code_consistency.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_blueprint_reconciler_py["蓝图协调器<br/>Blueprint Reconciler — v0.10.0<br/>蓝图实现一致性校验器。<br/>blueprint_reconciler<br/>文件: architecture_governance<br/>/blueprint_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_construction_verifier_py["construction验证器<br/>Construction Verifier — 施工验证器:<br/>任务卡完成度+蓝图一致性检查。<br/>construction_verifier<br/>文件: architecture_governance<br/>/construction_verifier.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_cross_env_consistency_py["跨环境一致性<br/>治理/architecture<br/>governance包的cross_env_consistency模块<br/>文件: architecture_governance<br/>/cross_env_consistency.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_dependency_manager_py["依赖管理器<br/>治理子系统的依赖关系管理工具<br/>dependency_manager<br/>文件: architecture_governance<br/>/dependency_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_formal_verifier_py["formal验证器<br/>Formal Verifier — v0.6.0 形式验证器:<br/>升级规则形式化验证->一致性+完备性检测。<br/>formal_verifier<br/>文件: architecture_governance/formal_verifier.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_gap_analyzer_py["gap分析器<br/>Gap Analyzer — v0.8.0 间隙分析器:<br/>escalation覆盖缺口扫描+新操作类型识别。<br/>gap_analyzer<br/>文件: architecture_governance/gap_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_llm_impact_analyzer_py["LLM冲击分析器<br/>LLMImpactAnalyzer — LLM-based commit<br/>语义影响分析器。<br/>llm_impact_analyzer<br/>文件: architecture_governance<br/>/llm_impact_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_local_first_arch_py["本地首架构<br/>治理/architecture<br/>governance包的local_first_arch模块<br/>文件: architecture_governance<br/>/local_first_arch.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_path_resolver_py["路径解析器<br/>PathResolver — 模块路径解析器<br/>path_resolver<br/>文件: architecture_governance/path_resolver.py<br/>(生产态 / production)"]
    src_zephyr_governance_bridges_alerts_py["告警<br/>依赖预算告警工作<br/>文件: bridges/alerts.py<br/>(生产态 / production)"]
    src_zephyr_governance_bridges_spec_auditor_py["spec审计器<br/>治理/bridges包的spec_auditor模块<br/>文件: bridges/spec_auditor.py<br/>(生产态 / production)"]
    src_zephyr_governance_compliance_gate_a6_compliance_manager_py["合规管理器<br/>ZephyrAlpha — D_COMPLIANCE Compliance Layer —<br/>合规规则管理器接口<br/>compliance_manager<br/>文件: compliance_gate_a6/compliance_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_compliance_gate_a6_compliance_mapper_py["合规mapper<br/>Compliance Mapper — D-022-13 合规映射器:<br/>操作->法规(SOX/GDPR/MiFID)映射+审计迹。<br/>compliance_mapper<br/>文件: compliance_gate_a6/compliance_mapper.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_command_chain_length_gate_py["命令链长度门禁<br/>Command Chain Length Gate — v0.13.0<br/>命令体积Deny退化防御器。<br/>command_chain_length_gate<br/>文件: context_governance<br/>/command_chain_length_gate.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_budget_py["上下文预算<br/>— 上下文预算管理与超预算截断（Phase 11 / 盲点<br/>B28）<br/>context_budget<br/>文件: context_governance/context_budget.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_manager_py["上下文管理器<br/>治理的管理器，统一管理资源生命周期<br/>context_manager<br/>文件: context_governance/context_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_package_py["上下文包<br/>Context Package — D-022-08 委托上下文包:<br/>升级原因+证据链+历史try_trace。<br/>context_package<br/>文件: context_governance/context_package.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_recycling_py["上下文recycling<br/>主要提供is验证等功能<br/>context_recycling<br/>文件: context_governance/context_recycling.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_switch_governor_py["上下文switchgovernor<br/>Context Switch Governor — v0.11.0<br/>Owner上下文切换预算管理器。<br/>context_switch_governor<br/>文件: context_governance<br/>/context_switch_governor.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_context_waste_detector_py["上下文waste检测器<br/>治理的报告器，汇总数据生成报告<br/>context_waste_detector<br/>文件: context_governance<br/>/context_waste_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_conversation_tax_detector_py["conversationtax检测器<br/>治理/context<br/>governance包的conversation_tax_detector模块<br/>文件: context_governance<br/>/conversation_tax_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_instruction_bloat_detector_py["instructionbloat检测器<br/>InstructionBloatDetector — 指令膨胀检测<br/>instruction_bloat_detector<br/>文件: context_governance<br/>/instruction_bloat_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_multi_turn_intent_analyzer_py["多turnintent分析器<br/>Multi-Turn Intent Analyzer — v0.13.0<br/>多轮分布式意图分析器。<br/>multi_turn_intent_analyzer<br/>文件: context_governance<br/>/multi_turn_intent_analyzer.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_prompt_lifecycle_py["提示生命周期<br/>治理/context governance包的prompt_lifecycle模块<br/>文件: context_governance/prompt_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_protocol_self_context_py["协议自上下文<br/>Protocol Self Context — v0.10.0<br/>协议自维护上下文管理器。<br/>protocol_self_context<br/>文件: context_governance<br/>/protocol_self_context.py<br/>(生产态 / production)"]
    src_zephyr_governance_context_governance_think_time_model_py["thinktime模型<br/>治理/context governance包的think_time_model模块<br/>文件: context_governance/think_time_model.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_classification_py["数据分类<br/>检查 self_level 是否有权限访问 target_level<br/>的数据。<br/>data_classification<br/>文件: data_governance/data_classification.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_lifecycle_py["数据生命周期<br/>治理/data governance包的data_lifecycle模块<br/>文件: data_governance/data_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_pipeline_guard_py["数据管线守卫<br/>Data Pipeline Guard — v0.10.0<br/>数据管道完整性防护: schema validation+row count<br/>check+checksum verify。<br/>data_pipeline_guard<br/>文件: data_governance/data_pipeline_guard.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_quality_py["数据质量<br/>治理/data governance包的data_quality模块<br/>文件: data_governance/data_quality.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_data_source_reliability_py["数据源可靠性<br/>治理/data<br/>governance包的data_source_reliability模块<br/>文件: data_governance/data_source_reliability.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_exchange_partition_detector_py["交易所partition检测器<br/>Exchange Partition Detector — v0.12.0<br/>交易所网络分区检测器。<br/>exchange_partition_detector<br/>文件: data_governance<br/>/exchange_partition_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_exchange_reg_monitor_py["交易所reg监控器<br/>Exchange Reg Monitor — v0.11.0<br/>交易所规则变更监控器。<br/>exchange_reg_monitor<br/>文件: data_governance/exchange_reg_monitor.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_miniqmt_provider_py["miniqmt提供器<br/>MiniQMT 实盘行情 Provider（Tick + 5档盘口）<br/>miniqmt_provider<br/>文件: data_governance/miniqmt_provider.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_pricing_sync_py["pricing同步<br/>治理/data governance包的pricing_sync模块<br/>文件: data_governance/pricing_sync.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_realtime_streaming_py["实时流式<br/>治理/data governance包的realtime_streaming模块<br/>文件: data_governance/realtime_streaming.py<br/>(生产态 / production)"]
    src_zephyr_governance_evidence_pack_py["证据包<br/>主要提供pack、验证、列表packs等功能，供audit-orc<br/>hestrator.integrity; 使用<br/>evidence_pack<br/>文件: governance/evidence_pack.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_arbitrage_asymmetry_detector_py["arbitrageasymmetry检测器<br/>Arbitrage Asymmetry Detector — v0.11.0<br/>跨交易所套利不对称检测器。<br/>arbitrage_asymmetry_detector<br/>文件: financial_governance<br/>/arbitrage_asymmetry_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_atomic_transaction_manager_py["atomic交易管理器<br/>AtomicTransactionManager — SQLite +<br/>文件系统的跨介质原子事务管理器 v2.0（ATM）。<br/>atomic_transaction_manager<br/>文件: financial_governance<br/>/atomic_transaction_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_flash_crash_guard_py["flashcrash守卫<br/>Flash Crash Guard — v0.12.0 闪崩双轨熔断器。<br/>flash_crash_guard<br/>文件: financial_governance/flash_crash_guard.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_fsm_verifier_py["fsm验证器<br/>治理/financial governance包的fsm_verifier模块<br/>文件: financial_governance/fsm_verifier.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_instrument_py["financial_governance/instrument<br/>治理/financial governance包的instrument模块<br/>文件: financial_governance/instrument.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_microstructure_defense_py["microstructure防御<br/>治理/financial<br/>governance包的microstructure_defense模块<br/>文件: financial_governance<br/>/microstructure_defense.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_oms_risk_engine_py["oms风险引擎<br/>治理/financial governance包的oms_risk_engine模块<br/>文件: financial_governance/oms_risk_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_risk_matrix_py["风险矩阵<br/>治理/financial governance包的risk_matrix模块<br/>文件: financial_governance/risk_matrix.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_strategy_portfolio_py["策略组合<br/>治理/financial<br/>governance包的strategy_portfolio模块<br/>文件: financial_governance/strategy_portfolio.py<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_strategy_scoper_py["策略scoper<br/>Strategy Scoper — v0.6.0 策略范围隔离器: SIG<br/>/Strat/Capital多层策略隔离。<br/>strategy_scoper<br/>文件: financial_governance/strategy_scoper.py<br/>(生产态 / production)"]
    src_zephyr_governance_implementations_default_experiment_pipeline_py["默认实验管线<br/>治理/implementations包的default_experiment_pipel<br/>ine模块<br/>文件: implementations<br/>/default_experiment_pipeline.py<br/>(生产态 / production)"]
    src_zephyr_governance_implementations_default_security_gateway_py["默认安全网关<br/>治理的门禁，在关键节点检查是否放行<br/>default_security_gateway<br/>文件: implementations<br/>/default_security_gateway.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_agent_debate_py["代理debate<br/>治理的核心类，封装DebateVerdict相关逻辑<br/>agent_debate<br/>文件: intelligence_governance/agent_debate.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_ai_self_diagnosis_py["AI自诊断<br/>治理/intelligence<br/>governance包的ai_self_diagnosis模块<br/>文件: intelligence_governance<br/>/ai_self_diagnosis.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_aisg_sandbox_py["aisg沙箱<br/>AISG Sandbox Testing — AI Security Gateway<br/>沙箱验证 (INV-015 升级)<br/>aisg_sandbox<br/>文件: intelligence_governance/aisg_sandbox.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_autonomy_dashboard_py["autonomy仪表盘<br/>Autonomy Dashboard — AI 自主感知健康仪表。<br/>autonomy_dashboard<br/>文件: intelligence_governance<br/>/autonomy_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_confidence_estimator_py["confidence估算器<br/>Confidence Estimator — D-022-05 置信度评估器:<br/>certainty×evidence×risk三维评估。<br/>confidence_estimator<br/>文件: intelligence_governance<br/>/confidence_estimator.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_confidence_quantifier_py["ConfidenceQuantifier — AI 置信度量化。<br/>治理/intelligence<br/>governance包的confidence_quantifier模块<br/>文件: intelligence_governance<br/>/confidence_quantifier.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_continuous_trust_py["continuous信任<br/>Continuous Trust Ledger — 持续信任评估引擎。<br/>continuous_trust<br/>文件: intelligence_governance<br/>/continuous_trust.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_cross_agent_conflict_detector_py["跨代理冲突检测器<br/>CrossAgentConflictDetector — 多 Agent<br/>并发冲突检测。<br/>cross_agent_conflict_detector<br/>文件: intelligence_governance<br/>/cross_agent_conflict_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_cross_assistant_adapter_py["跨assistant适配器<br/>Cross-Assistant Adapter — v0.6.0 Trae/Cursor<br/>/Windsurf/Codex/Wedata统一升级接口。<br/>cross_assistant_adapter<br/>文件: intelligence_governance<br/>/cross_assistant_adapter.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_delegation_manager_py["delegation管理器<br/>Delegation Manager — D-022-02 自动委托协议。<br/>delegation_manager<br/>文件: intelligence_governance<br/>/delegation_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_memory_provider_py["记忆提供器<br/>D_DATA — Memory Provider<br/>文件: intelligence_governance/memory_provider.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_meta_confidence_py["元confidence<br/>Meta-Confidence — D-022-10<br/>Agent对自身判定置信度的自评+历史校准。<br/>meta_confidence<br/>文件: intelligence_governance/meta_confidence.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_model_provider_data_py["模型提供器数据<br/>治理的模型，定义数据结构和字段<br/>model_provider_data<br/>文件: intelligence_governance<br/>/model_provider_data.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_model_router_py["模型路由器<br/>依赖预算模型、提供器数据、resultswriter工作<br/>model_router<br/>文件: intelligence_governance/model_router.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_model_version_detector_py["模型版本检测器<br/>Model Version Detector — v0.10.0<br/>模型版本突变检测: model version<br/>change->degraded auto_guard。<br/>model_version_detector<br/>文件: intelligence_governance<br/>/model_version_detector.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_multi_model_consensus_py["多模型共识<br/>治理/intelligence<br/>governance包的multi_model_consensus模块<br/>文件: intelligence_governance<br/>/multi_model_consensus.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_mvep_orchestrator_py["mvep编排器<br/>MVEP Orchestrator — v0.11.0 Minimum Viable<br/>Escalation Protocol调度器。<br/>mvep_orchestrator<br/>文件: intelligence_governance<br/>/mvep_orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_provider_failover_py["提供器故障切换<br/>Provider Failover — v0.7.0 多LLM Provider容灾:<br/>deepseek->claude->gpt fallback链。<br/>provider_failover<br/>文件: intelligence_governance<br/>/provider_failover.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_self_benchmark_py["自基准<br/>(W3-7) — 5 组已知对自验证 + 引擎退化告警<br/>self_benchmark<br/>文件: intelligence_governance/self_benchmark.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_self_test_py["自测试<br/>Escalation Protocol Self-Test — MOD-INF-022<br/>文件: intelligence_governance/self_test.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_self_validator_py["自校验器<br/>Self Validator — v0.10.0 升级协议自验证器:<br/>protocol自身规则+代码一致性自检。<br/>self_validator<br/>文件: intelligence_governance/self_validator.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_subagent_hook_propagator_py["subagent钩子propagator<br/>Subagent Hook Propagator — v0.13.0 子Agent<br/>Hook旁路防护器。<br/>subagent_hook_propagator<br/>文件: intelligence_governance<br/>/subagent_hook_propagator.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_api_lifecycle_py["API生命周期<br/>治理/lifecycle governance包的api_lifecycle模块<br/>文件: lifecycle_governance/api_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_migration_strategy_py["迁移策略<br/>治理/lifecycle<br/>governance包的migration_strategy模块<br/>文件: lifecycle_governance/migration_strategy.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_paper_live_transition_py["paper实盘转换<br/>检查是否可跳Phase——不可跳, 只允许顺序next。<br/>paper_live_transition<br/>文件: lifecycle_governance<br/>/paper_live_transition.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_post_live_verification_py["提交实时验证<br/>治理/lifecycle<br/>governance包的post_live_verification模块<br/>文件: lifecycle_governance<br/>/post_live_verification.py<br/>(生产态 / production)"]
    src_zephyr_governance_lifecycle_governance_transition_py["转换<br/>transition — 状态机转换 Mixin（从 task_repo.py<br/>拆分，SRC-0066）<br/>文件: lifecycle_governance/transition.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_analytics_base_py["analytics基类<br/>Re-export wrapper: analytics_base canonical at<br/>zephyr.reporting.analytics_base<br/>文件: observability_governance/analytics_base.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_objective_tracker_py["objective追踪器<br/>Objective Tracker — v0.9.0 目标漂移检测器:<br/>agent目标函数稳定性+变更检测+rollback。<br/>objective_tracker<br/>文件: observability_governance<br/>/objective_tracker.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_battle_map_reader_py["persistence/battle_map_reader<br/>battle_map_reader.py —<br/>作战地图数据库只读查询工具模块<br/>文件: persistence/battle_map_reader.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_database_manager_py["数据库管理器<br/>DatabaseManager — 连接池 + 健康检查 + 自动备份<br/>+ WAL checkpoint（SH-DB-001 v2.0）<br/>database_manager<br/>文件: persistence/database_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_database_service_py["数据库服务<br/>DatabaseService 真源收敛（AI-14 审计 P1 修复）<br/>database_service<br/>文件: persistence/database_service.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_dataflowgraph_schema_py["dataflowgraph结构<br/>dataflowgraph Schema DDL + 连接入口<br/>dataflowgraph_schema<br/>文件: persistence/dataflowgraph_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_decision_graph_reader_py["决策graph读取器<br/>决策流图数据库只读查询工具模块<br/>decision_graph_reader<br/>文件: persistence/decision_graph_reader.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_depgraph_reader_py["depgraph读取器<br/>依赖图数据库查询工具模块<br/>depgraph_reader<br/>文件: persistence/depgraph_reader.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_protocol_state_store_py["协议状态存储<br/>Protocol State Store — v0.10.0<br/>协议运行时状态持久化: JSON snapshot+recovery<br/>state+crash恢复。<br/>protocol_state_store<br/>文件: persistence/protocol_state_store.py<br/>(生产态 / production)"]
    src_zephyr_governance_services_adapter_py["适配器<br/>Escalation Adapter — MOD-INF-022 统一集成入口.<br/>文件: services/adapter.py<br/>(生产态 / production)"]
    src_zephyr_governance_services_cross_session_correlator_py["跨会话关联器<br/>Cross-Session Correlator — v0.9.0<br/>跨会话Coreset关联器:<br/>多session行为模式+异常跨session模式检测。<br/>cross_session_correlator<br/>文件: services/cross_session_correlator.py<br/>(生产态 / production)"]
    src_zephyr_governance_services_memory_provenance_py["记忆溯源<br/>Memory Provenance — v0.9.0 记忆溯源追踪:<br/>每条memory record的来源agent+timestamp+hash链。<br/>memory_provenance<br/>文件: services/memory_provenance.py<br/>(生产态 / production)"]
    src_zephyr_governance_strategies_strategy_registry_py["策略注册表<br/>StrategyRegistry 卫星模块（OCP-002）<br/>strategy_registry<br/>文件: strategies/strategy_registry.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_base_server_py["基类服务端<br/>主要提供注册tool、处理请求等功能<br/>_base_server<br/>文件: governance/_base_server.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_audit_logger_py["审计日志器<br/>主要提供日志、查询、数量等功能<br/>audit_logger<br/>文件: governance/audit_logger.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_auditor_py["审计器<br/>G-CT-008 契约：A2A -> Audit 审计 Agent 间通信.<br/>auditor<br/>文件: governance/auditor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_error_codes_py["错误codes<br/>治理的异常，定义本模块的异常类型<br/>error_codes<br/>文件: governance/error_codes.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_governance_adapter_py["治理适配器<br/>A2A GovernanceAdapter — Phase 4 治理集成桥接器<br/>governance_adapter<br/>文件: governance/governance_adapter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_phase_hold_py["阶段hold<br/>基础设施/治理包的phase_hold模块<br/>文件: governance/phase_hold.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_policy_engine_py["策略引擎<br/>主要提供评估、新增策略、移除策略等功能<br/>policy_engine<br/>文件: governance/policy_engine.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_protocol_py["协议<br/>G-CT-008 — A2ACommunication Pydantic V2<br/>BaseModel agent-to-agent 通信数据结构.<br/>protocol<br/>文件: governance/protocol.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_rate_limiter_py["速率限制器<br/>Sliding window 速率限制器，支持 per-key 分桶。<br/>rate_limiter<br/>文件: governance/rate_limiter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_governance_session_manager_py["会话管理器<br/>主要提供创建会话、获取会话、结束会话等功能<br/>session_manager<br/>文件: governance/session_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py["治理集成<br/>基础设施/layer3<br/>coordination包的governance_integration模块<br/>文件: layer3_coordination<br/>/_governance_integration.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_capacity_assurance_contracts_batch2_governance_py["batch2治理<br/>Batch2 治理层契约 — 15条 Pydantic v2 Schema<br/>（Provenance/AI审计守卫/TechStackValidator<br/>/Governance Loop/Sandbox资源限制）.<br/>batch2_governance<br/>文件: contracts/batch2_governance.py<br/>(生产态 / production)"]
    src_zephyr_integration_mcp_governance_server_py["治理服务端<br/>GovernanceServer: 治理域统一MCP入口<br/>governance_server<br/>文件: mcp/governance_server.py<br/>(生产态 / production)"]
    src_zephyr_shared_capacity_governance_capacity_governance_loop_py["容量治理循环<br/>容量治理loop，容量治理的循环，循环执行的流程。<br/>capacity_governance_loop<br/>文件: capacity_governance<br/>/capacity_governance_loop.py<br/>(生产态 / production)"]
    src_zephyr_shared_protocols_a2a_a2a_governance_py["A2A治理<br/>A2A Governance — shared interface definitions<br/>for governance layer<br/>文件: a2a/a2a_governance.py<br/>(生产态 / production)"]
    tests_agent_rbac_test_session_aware_stash_red_blue_py["测试会话感知stashredblue<br/>会话 隔离 stash 红蓝对抗极限测试。<br/>test_session_aware_stash_red_blue<br/>文件: agent_rbac<br/>/test_session_aware_stash_red_blue.py<br/>(生产态 / production)"]
    tests_git_test_git_commit_concurrent_py["测试Git提交并发<br/>幽灵提交红蓝对抗测试<br/>test_git_commit_concurrent<br/>文件: git/test_git_commit_concurrent.py<br/>(生产态 / production)"]
    tests_git_test_git_commit_extreme_py["测试Gitcommitextreme<br/>GitCommitGateway 极端故障注入测试<br/>test_git_commit_extreme<br/>文件: git/test_git_commit_extreme.py<br/>(生产态 / production)"]
    tests_git_test_git_commit_gateway_py["测试Git提交网关<br/>GitCommitGateway 单元测试（OPS-2026062512 验收）<br/>test_git_commit_gateway<br/>文件: git/test_git_commit_gateway.py<br/>(生产态 / production)"]
    tests_git_test_reconciler_verify_autosync_py["测试对账器verifyautosync<br/>--reconciler-verify auto-sync 产物豁免测试。<br/>test_reconciler_verify_autosync<br/>文件: git/test_reconciler_verify_autosync.py<br/>(生产态 / production)"]
    tests_governance_generators_test_check_gate_inventory_drift_py["测试check门禁inventory漂移<br/>commit_gates 模块清单漂移检测脚本单元测试<br/>test_check_gate_inventory_drift<br/>文件: generators<br/>/test_check_gate_inventory_drift.py<br/>(生产态 / production)"]
    tests_governance_generators_test_generate_gate_registry_py["测试生成门禁注册表<br/>py 单元测试（CommitGate 同步治本 2026-07-17）<br/>test_generate_gate_registry<br/>文件: generators/test_generate_gate_registry.py<br/>(生产态 / production)"]
    tests_governance_rule_bridge_test_worktree_lifecycle_py["测试worktree生命周期<br/>#ARCH-WORKTREE-LIFECYCLE-001 状态机测试<br/>test_worktree_lifecycle<br/>文件: rule_bridge/test_worktree_lifecycle.py<br/>(生产态 / production)"]
    tests_governance_test_ast_import_rewriter_py["测试astimportrewriter<br/>提供testexactmatch、testnomatch、testprefixmatch<br/>等方法<br/>文件: governance/test_ast_import_rewriter.py<br/>(生产态 / production)"]
    tests_io_test_depgraph_schema_py["测试依赖图模式<br/>py DDL 真源与迁移框架单元测试<br/>test_depgraph_schema<br/>文件: io/test_depgraph_schema.py<br/>(生产态 / production)"]
    tests_io_test_verify_schema_health_py["测试校验模式健康<br/>py 门禁可靠性单元测试<br/>test_verify_schema_health<br/>文件: io/test_verify_schema_health.py<br/>(生产态 / production)"]
    tests_rollback_test_concurrency_guard_red_blue_py["测试并发守卫redblue<br/>红蓝对抗极端测试 — git_guard +<br/>concurrency_guard 端到端防护能力验证。<br/>test_concurrency_guard_red_blue<br/>文件: rollback<br/>/test_concurrency_guard_red_blue.py<br/>(生产态 / production)"]
    tests_rollback_test_concurrent_mv_guard_py["并发红蓝极限对抗测试 — 多 AI 并发执行 git mv<br/>时的防护能力验证。<br/>rollback包的test_concurrent_mv_guard模块<br/>文件: rollback/test_concurrent_mv_guard.py<br/>(生产态 / production)"]
    tests_task_test_task_repo_gateway_e2e_py["测试taskrepogatewaye2e<br/>端到端链路测试<br/>test_task_repo_gateway_e2e<br/>文件: task/test_task_repo_gateway_e2e.py<br/>(生产态 / production)"]
    tests_test_align_panoramas_py["测试alignpanoramas<br/>tests包的test_align_panoramas模块<br/>文件: tests/test_align_panoramas.py<br/>(生产态 / production)"]
    tests_test_dataflow_design_layout_py["测试dataflowdesignlayout<br/>设计态数据流文档视觉风格测试<br/>test_dataflow_design_layout<br/>文件: tests/test_dataflow_design_layout.py<br/>(生产态 / production)"]
    tests_test_generate_dataflow_diagram_py["测试generatedataflowdiagram<br/>tests包的test_generate_dataflow_diagram模块<br/>文件: tests/test_generate_dataflow_diagram.py<br/>(生产态 / production)"]
    tests_test_generate_decision_diagram_py["测试generate决策diagram<br/>tests包的test_generate_decision_diagram模块<br/>文件: tests/test_generate_decision_diagram.py<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_rule_registry_collection_yaml ~~~ scripts_a2a_full_verification_py
    scripts_a2a_full_verification_py ~~~ scripts_arch_guard_tools_build_ocp_manifest_py
    scripts_arch_guard_tools_build_ocp_manifest_py ~~~ scripts_arch_guard_tools_inject_idempotency_py
    scripts_arch_guard_tools_inject_idempotency_py ~~~ scripts_arch_guard_tools_patch_p1_paths_py
    scripts_arch_guard_tools_patch_p1_paths_py ~~~ scripts_arch_guard_check_acl_boundary_py
    scripts_arch_guard_check_acl_boundary_py ~~~ scripts_arch_guard_check_cross_plane_communication_py
    scripts_arch_guard_check_cross_plane_communication_py ~~~ scripts_arch_guard_check_fe_acl_boundary_py
    scripts_arch_guard_check_fe_acl_boundary_py ~~~ scripts_arch_guard_check_hot_path_purity_py
    scripts_arch_guard_check_hot_path_purity_py ~~~ scripts_arch_guard_check_scaffold_exit_gates_py
    scripts_arch_guard_check_scaffold_exit_gates_py ~~~ scripts_arch_guard_check_schema_consistency_py
    scripts_arch_guard_check_schema_consistency_py ~~~ scripts_arch_guard_fitness_functions_check_aisg_gateway_py
    scripts_arch_guard_fitness_functions_check_aisg_gateway_py ~~~ scripts_arch_guard_fitness_functions_check_audit_log_immutability_py
    scripts_arch_guard_fitness_functions_check_audit_log_immutability_py ~~~ scripts_arch_guard_fitness_functions_check_capacity_slo_ssot_py
    scripts_arch_guard_fitness_functions_check_capacity_slo_ssot_py ~~~ scripts_arch_guard_fitness_functions_check_daily_loss_limit_py
    scripts_arch_guard_fitness_functions_check_daily_loss_limit_py ~~~ scripts_arch_guard_fitness_functions_check_hot_warm_ipc_py
    scripts_arch_guard_fitness_functions_check_hot_warm_ipc_py ~~~ scripts_arch_guard_fitness_functions_check_idempotency_key_py
    scripts_arch_guard_fitness_functions_check_idempotency_key_py ~~~ scripts_arch_guard_fitness_functions_check_log_secret_leak_py
    scripts_arch_guard_fitness_functions_check_log_secret_leak_py ~~~ scripts_arch_guard_fitness_functions_check_no_cross_plane_mutable_state_py
    scripts_arch_guard_fitness_functions_check_no_cross_plane_mutable_state_py ~~~ scripts_arch_guard_fitness_functions_check_ocp_signatures_py
    scripts_arch_guard_fitness_functions_check_ocp_signatures_py ~~~ scripts_arch_guard_fitness_functions_check_pit_compliance_py
    scripts_arch_guard_fitness_functions_check_pit_compliance_py ~~~ scripts_arch_guard_fitness_functions_check_position_limit_py
    scripts_arch_guard_fitness_functions_check_position_limit_py ~~~ scripts_arch_guard_fitness_functions_check_risk_params_consistency_py
    scripts_arch_guard_fitness_functions_check_risk_params_consistency_py ~~~ scripts_arch_guard_fitness_functions_check_survivorship_bias_py
    scripts_arch_guard_fitness_functions_check_survivorship_bias_py ~~~ scripts_arch_guard_fitness_functions_check_warm_cold_async_py
    scripts_arch_guard_fitness_functions_check_warm_cold_async_py ~~~ scripts_arch_guard_run_all_py
    scripts_arch_guard_run_all_py ~~~ scripts_construction_e2e_check_py
    scripts_construction_e2e_check_py ~~~ scripts_construction_e2e_deep_py
    scripts_construction_e2e_deep_py ~~~ scripts_construction_check_transition_code_py
    scripts_construction_check_transition_code_py ~~~ scripts_construction_d_init_task_system_py
    scripts_construction_d_init_task_system_py ~~~ scripts_construction_demo_a2a_chat_py
    scripts_construction_demo_a2a_chat_py ~~~ scripts_construction_demo_a2a_coordination_py
    scripts_construction_demo_a2a_coordination_py ~~~ scripts_construction_demo_e2e_pipeline_py
    scripts_construction_demo_e2e_pipeline_py ~~~ scripts_construction_finalize_tasks_py
    scripts_construction_finalize_tasks_py ~~~ scripts_construction_local_layer_daemon_py
    scripts_construction_local_layer_daemon_py ~~~ scripts_construction_reset_test_task_py
    scripts_construction_reset_test_task_py ~~~ scripts_construction_start_brain_py
    scripts_construction_start_brain_py ~~~ scripts_construction_test_event_hook_py
    scripts_construction_test_event_hook_py ~~~ scripts_context_generate_architecture_context_py
    scripts_context_generate_architecture_context_py ~~~ scripts_diagnose_breadth_failed_py
    scripts_diagnose_breadth_failed_py ~~~ scripts_dm90971_add_test_headers_py
    scripts_dm90971_add_test_headers_py ~~~ scripts_fix_freeze_manifest_py
    scripts_fix_freeze_manifest_py ~~~ scripts_fix_orphan_all_py
    scripts_fix_orphan_all_py ~~~ scripts_generate_manifest_py
    scripts_generate_manifest_py ~~~ scripts_generate_pathway_registry_py
    scripts_generate_pathway_registry_py ~~~ scripts_governance_d5_architecture_generators_zoomable_html_py
    scripts_governance_d5_architecture_generators_zoomable_html_py ~~~ scripts_governance_d7_code_check_pure_shim_py
    scripts_governance_d7_code_check_pure_shim_py ~~~ scripts_governance_generators_generate_rule_ai_perception_index_py
    scripts_governance_generators_generate_rule_ai_perception_index_py ~~~ scripts_hooks_auto_handoff_log_py
    scripts_hooks_auto_handoff_log_py ~~~ scripts_lock_files_py
    scripts_lock_files_py ~~~ scripts_mcp_launcher_py
    scripts_mcp_launcher_py ~~~ scripts_mcp_start_all_py
    scripts_mcp_start_all_py ~~~ scripts_mcp_status_all_py
    scripts_mcp_status_all_py ~~~ scripts_mcp_stop_all_py
    scripts_mcp_stop_all_py ~~~ scripts_migration_dm314_infra_ops_split_py
    scripts_migration_dm314_infra_ops_split_py ~~~ scripts_migration_governance_root_split_py
    scripts_migration_governance_root_split_py ~~~ scripts_ops_verify_header_completeness_py
    scripts_ops_verify_header_completeness_py ~~~ scripts_post_checkout_guard_py
    scripts_post_checkout_guard_py ~~~ scripts_pre_commit_verify_dedup_py
    scripts_pre_commit_verify_dedup_py ~~~ scripts_rollback_py
    scripts_rollback_py ~~~ scripts_run_deepseek_v4_exam_py
    scripts_run_deepseek_v4_exam_py ~~~ scripts_run_ollama_exam_py
    scripts_run_ollama_exam_py ~~~ scripts_scaffold_py
    scripts_scaffold_py ~~~ scripts_setup_git_guard_aliases_py
    scripts_setup_git_guard_aliases_py ~~~ src_zephyr_governance_a2a_init_py
    src_zephyr_governance_a2a_init_py ~~~ src_zephyr_governance_adapters_risk_validation_bridge_py
    src_zephyr_governance_adapters_risk_validation_bridge_py ~~~ src_zephyr_governance_adapters_simulation_broker_py
    src_zephyr_governance_adapters_simulation_broker_py ~~~ src_zephyr_governance_agent_spec_init_py
    src_zephyr_governance_agent_spec_init_py ~~~ src_zephyr_governance_agent_spec_a2a_failure_py
    src_zephyr_governance_agent_spec_a2a_failure_py ~~~ src_zephyr_governance_agent_spec_rbac_bridge_py
    src_zephyr_governance_agent_spec_rbac_bridge_py ~~~ src_zephyr_governance_agent_spec_registry_py
    src_zephyr_governance_agent_spec_registry_py ~~~ src_zephyr_governance_architecture_governance_architecture_contracts_py
    src_zephyr_governance_architecture_governance_architecture_contracts_py ~~~ src_zephyr_governance_architecture_governance_architecture_principles_py
    src_zephyr_governance_architecture_governance_architecture_principles_py ~~~ src_zephyr_governance_architecture_governance_blueprint_bloat_monitor_py
    src_zephyr_governance_architecture_governance_blueprint_bloat_monitor_py ~~~ src_zephyr_governance_architecture_governance_blueprint_code_consistency_py
    src_zephyr_governance_architecture_governance_blueprint_code_consistency_py ~~~ src_zephyr_governance_architecture_governance_blueprint_reconciler_py
    src_zephyr_governance_architecture_governance_blueprint_reconciler_py ~~~ src_zephyr_governance_architecture_governance_construction_verifier_py
    src_zephyr_governance_architecture_governance_construction_verifier_py ~~~ src_zephyr_governance_architecture_governance_cross_env_consistency_py
    src_zephyr_governance_architecture_governance_cross_env_consistency_py ~~~ src_zephyr_governance_architecture_governance_dependency_manager_py
    src_zephyr_governance_architecture_governance_dependency_manager_py ~~~ src_zephyr_governance_architecture_governance_formal_verifier_py
    src_zephyr_governance_architecture_governance_formal_verifier_py ~~~ src_zephyr_governance_architecture_governance_gap_analyzer_py
    src_zephyr_governance_architecture_governance_gap_analyzer_py ~~~ src_zephyr_governance_architecture_governance_llm_impact_analyzer_py
    src_zephyr_governance_architecture_governance_llm_impact_analyzer_py ~~~ src_zephyr_governance_architecture_governance_local_first_arch_py
    src_zephyr_governance_architecture_governance_local_first_arch_py ~~~ src_zephyr_governance_architecture_governance_path_resolver_py
    src_zephyr_governance_architecture_governance_path_resolver_py ~~~ src_zephyr_governance_bridges_alerts_py
    src_zephyr_governance_bridges_alerts_py ~~~ src_zephyr_governance_bridges_spec_auditor_py
    src_zephyr_governance_bridges_spec_auditor_py ~~~ src_zephyr_governance_compliance_gate_a6_compliance_manager_py
    src_zephyr_governance_compliance_gate_a6_compliance_manager_py ~~~ src_zephyr_governance_compliance_gate_a6_compliance_mapper_py
    src_zephyr_governance_compliance_gate_a6_compliance_mapper_py ~~~ src_zephyr_governance_context_governance_command_chain_length_gate_py
    src_zephyr_governance_context_governance_command_chain_length_gate_py ~~~ src_zephyr_governance_context_governance_context_budget_py
    src_zephyr_governance_context_governance_context_budget_py ~~~ src_zephyr_governance_context_governance_context_manager_py
    src_zephyr_governance_context_governance_context_manager_py ~~~ src_zephyr_governance_context_governance_context_package_py
    src_zephyr_governance_context_governance_context_package_py ~~~ src_zephyr_governance_context_governance_context_recycling_py
    src_zephyr_governance_context_governance_context_recycling_py ~~~ src_zephyr_governance_context_governance_context_switch_governor_py
    src_zephyr_governance_context_governance_context_switch_governor_py ~~~ src_zephyr_governance_context_governance_context_waste_detector_py
    src_zephyr_governance_context_governance_context_waste_detector_py ~~~ src_zephyr_governance_context_governance_conversation_tax_detector_py
    src_zephyr_governance_context_governance_conversation_tax_detector_py ~~~ src_zephyr_governance_context_governance_instruction_bloat_detector_py
    src_zephyr_governance_context_governance_instruction_bloat_detector_py ~~~ src_zephyr_governance_context_governance_multi_turn_intent_analyzer_py
    src_zephyr_governance_context_governance_multi_turn_intent_analyzer_py ~~~ src_zephyr_governance_context_governance_prompt_lifecycle_py
    src_zephyr_governance_context_governance_prompt_lifecycle_py ~~~ src_zephyr_governance_context_governance_protocol_self_context_py
    src_zephyr_governance_context_governance_protocol_self_context_py ~~~ src_zephyr_governance_context_governance_think_time_model_py
    src_zephyr_governance_context_governance_think_time_model_py ~~~ src_zephyr_governance_data_governance_data_classification_py
    src_zephyr_governance_data_governance_data_classification_py ~~~ src_zephyr_governance_data_governance_data_lifecycle_py
    src_zephyr_governance_data_governance_data_lifecycle_py ~~~ src_zephyr_governance_data_governance_data_pipeline_guard_py
    src_zephyr_governance_data_governance_data_pipeline_guard_py ~~~ src_zephyr_governance_data_governance_data_quality_py
    src_zephyr_governance_data_governance_data_quality_py ~~~ src_zephyr_governance_data_governance_data_source_reliability_py
    src_zephyr_governance_data_governance_data_source_reliability_py ~~~ src_zephyr_governance_data_governance_exchange_partition_detector_py
    src_zephyr_governance_data_governance_exchange_partition_detector_py ~~~ src_zephyr_governance_data_governance_exchange_reg_monitor_py
    src_zephyr_governance_data_governance_exchange_reg_monitor_py ~~~ src_zephyr_governance_data_governance_miniqmt_provider_py
    src_zephyr_governance_data_governance_miniqmt_provider_py ~~~ src_zephyr_governance_data_governance_pricing_sync_py
    src_zephyr_governance_data_governance_pricing_sync_py ~~~ src_zephyr_governance_data_governance_realtime_streaming_py
    src_zephyr_governance_data_governance_realtime_streaming_py ~~~ src_zephyr_governance_evidence_pack_py
    src_zephyr_governance_evidence_pack_py ~~~ src_zephyr_governance_financial_governance_arbitrage_asymmetry_detector_py
    src_zephyr_governance_financial_governance_arbitrage_asymmetry_detector_py ~~~ src_zephyr_governance_financial_governance_atomic_transaction_manager_py
    src_zephyr_governance_financial_governance_atomic_transaction_manager_py ~~~ src_zephyr_governance_financial_governance_flash_crash_guard_py
    src_zephyr_governance_financial_governance_flash_crash_guard_py ~~~ src_zephyr_governance_financial_governance_fsm_verifier_py
    src_zephyr_governance_financial_governance_fsm_verifier_py ~~~ src_zephyr_governance_financial_governance_instrument_py
    src_zephyr_governance_financial_governance_instrument_py ~~~ src_zephyr_governance_financial_governance_microstructure_defense_py
    src_zephyr_governance_financial_governance_microstructure_defense_py ~~~ src_zephyr_governance_financial_governance_oms_risk_engine_py
    src_zephyr_governance_financial_governance_oms_risk_engine_py ~~~ src_zephyr_governance_financial_governance_risk_matrix_py
    src_zephyr_governance_financial_governance_risk_matrix_py ~~~ src_zephyr_governance_financial_governance_strategy_portfolio_py
    src_zephyr_governance_financial_governance_strategy_portfolio_py ~~~ src_zephyr_governance_financial_governance_strategy_scoper_py
    src_zephyr_governance_financial_governance_strategy_scoper_py ~~~ src_zephyr_governance_implementations_default_experiment_pipeline_py
    src_zephyr_governance_implementations_default_experiment_pipeline_py ~~~ src_zephyr_governance_implementations_default_security_gateway_py
    src_zephyr_governance_implementations_default_security_gateway_py ~~~ src_zephyr_governance_intelligence_governance_agent_debate_py
    src_zephyr_governance_intelligence_governance_agent_debate_py ~~~ src_zephyr_governance_intelligence_governance_ai_self_diagnosis_py
    src_zephyr_governance_intelligence_governance_ai_self_diagnosis_py ~~~ src_zephyr_governance_intelligence_governance_aisg_sandbox_py
    src_zephyr_governance_intelligence_governance_aisg_sandbox_py ~~~ src_zephyr_governance_intelligence_governance_autonomy_dashboard_py
    src_zephyr_governance_intelligence_governance_autonomy_dashboard_py ~~~ src_zephyr_governance_intelligence_governance_confidence_estimator_py
    src_zephyr_governance_intelligence_governance_confidence_estimator_py ~~~ src_zephyr_governance_intelligence_governance_confidence_quantifier_py
    src_zephyr_governance_intelligence_governance_confidence_quantifier_py ~~~ src_zephyr_governance_intelligence_governance_continuous_trust_py
    src_zephyr_governance_intelligence_governance_continuous_trust_py ~~~ src_zephyr_governance_intelligence_governance_cross_agent_conflict_detector_py
    src_zephyr_governance_intelligence_governance_cross_agent_conflict_detector_py ~~~ src_zephyr_governance_intelligence_governance_cross_assistant_adapter_py
    src_zephyr_governance_intelligence_governance_cross_assistant_adapter_py ~~~ src_zephyr_governance_intelligence_governance_delegation_manager_py
    src_zephyr_governance_intelligence_governance_delegation_manager_py ~~~ src_zephyr_governance_intelligence_governance_memory_provider_py
    src_zephyr_governance_intelligence_governance_memory_provider_py ~~~ src_zephyr_governance_intelligence_governance_meta_confidence_py
    src_zephyr_governance_intelligence_governance_meta_confidence_py ~~~ src_zephyr_governance_intelligence_governance_model_provider_data_py
    src_zephyr_governance_intelligence_governance_model_provider_data_py ~~~ src_zephyr_governance_intelligence_governance_model_router_py
    src_zephyr_governance_intelligence_governance_model_router_py ~~~ src_zephyr_governance_intelligence_governance_model_version_detector_py
    src_zephyr_governance_intelligence_governance_model_version_detector_py ~~~ src_zephyr_governance_intelligence_governance_multi_model_consensus_py
    src_zephyr_governance_intelligence_governance_multi_model_consensus_py ~~~ src_zephyr_governance_intelligence_governance_mvep_orchestrator_py
    src_zephyr_governance_intelligence_governance_mvep_orchestrator_py ~~~ src_zephyr_governance_intelligence_governance_provider_failover_py
    src_zephyr_governance_intelligence_governance_provider_failover_py ~~~ src_zephyr_governance_intelligence_governance_self_benchmark_py
    src_zephyr_governance_intelligence_governance_self_benchmark_py ~~~ src_zephyr_governance_intelligence_governance_self_test_py
    src_zephyr_governance_intelligence_governance_self_test_py ~~~ src_zephyr_governance_intelligence_governance_self_validator_py
    src_zephyr_governance_intelligence_governance_self_validator_py ~~~ src_zephyr_governance_intelligence_governance_subagent_hook_propagator_py
    src_zephyr_governance_intelligence_governance_subagent_hook_propagator_py ~~~ src_zephyr_governance_lifecycle_governance_api_lifecycle_py
    src_zephyr_governance_lifecycle_governance_api_lifecycle_py ~~~ src_zephyr_governance_lifecycle_governance_migration_strategy_py
    src_zephyr_governance_lifecycle_governance_migration_strategy_py ~~~ src_zephyr_governance_lifecycle_governance_paper_live_transition_py
    src_zephyr_governance_lifecycle_governance_paper_live_transition_py ~~~ src_zephyr_governance_lifecycle_governance_post_live_verification_py
    src_zephyr_governance_lifecycle_governance_post_live_verification_py ~~~ src_zephyr_governance_lifecycle_governance_transition_py
    src_zephyr_governance_lifecycle_governance_transition_py ~~~ src_zephyr_governance_observability_governance_analytics_base_py
    src_zephyr_governance_observability_governance_analytics_base_py ~~~ src_zephyr_governance_observability_governance_objective_tracker_py
    src_zephyr_governance_observability_governance_objective_tracker_py ~~~ src_zephyr_governance_persistence_battle_map_reader_py
    src_zephyr_governance_persistence_battle_map_reader_py ~~~ src_zephyr_governance_persistence_database_manager_py
    src_zephyr_governance_persistence_database_manager_py ~~~ src_zephyr_governance_persistence_database_service_py
    src_zephyr_governance_persistence_database_service_py ~~~ src_zephyr_governance_persistence_dataflowgraph_schema_py
    src_zephyr_governance_persistence_dataflowgraph_schema_py ~~~ src_zephyr_governance_persistence_decision_graph_reader_py
    src_zephyr_governance_persistence_decision_graph_reader_py ~~~ src_zephyr_governance_persistence_depgraph_reader_py
    src_zephyr_governance_persistence_depgraph_reader_py ~~~ src_zephyr_governance_persistence_protocol_state_store_py
    src_zephyr_governance_persistence_protocol_state_store_py ~~~ src_zephyr_governance_services_adapter_py
    src_zephyr_governance_services_adapter_py ~~~ src_zephyr_governance_services_cross_session_correlator_py
    src_zephyr_governance_services_cross_session_correlator_py ~~~ src_zephyr_governance_services_memory_provenance_py
    src_zephyr_governance_services_memory_provenance_py ~~~ src_zephyr_governance_strategies_strategy_registry_py
    src_zephyr_governance_strategies_strategy_registry_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_base_server_py
    src_zephyr_infrastructure_a2a_protocol_governance_base_server_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_audit_logger_py
    src_zephyr_infrastructure_a2a_protocol_governance_audit_logger_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_auditor_py
    src_zephyr_infrastructure_a2a_protocol_governance_auditor_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_error_codes_py
    src_zephyr_infrastructure_a2a_protocol_governance_error_codes_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_governance_adapter_py
    src_zephyr_infrastructure_a2a_protocol_governance_governance_adapter_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_phase_hold_py
    src_zephyr_infrastructure_a2a_protocol_governance_phase_hold_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_policy_engine_py
    src_zephyr_infrastructure_a2a_protocol_governance_policy_engine_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_protocol_py
    src_zephyr_infrastructure_a2a_protocol_governance_protocol_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_rate_limiter_py
    src_zephyr_infrastructure_a2a_protocol_governance_rate_limiter_py ~~~ src_zephyr_infrastructure_a2a_protocol_governance_session_manager_py
    src_zephyr_infrastructure_a2a_protocol_governance_session_manager_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py ~~~ src_zephyr_infrastructure_capacity_assurance_contracts_batch2_governance_py
    src_zephyr_infrastructure_capacity_assurance_contracts_batch2_governance_py ~~~ src_zephyr_integration_mcp_governance_server_py
    src_zephyr_integration_mcp_governance_server_py ~~~ src_zephyr_shared_capacity_governance_capacity_governance_loop_py
    src_zephyr_shared_capacity_governance_capacity_governance_loop_py ~~~ src_zephyr_shared_protocols_a2a_a2a_governance_py
    src_zephyr_shared_protocols_a2a_a2a_governance_py ~~~ tests_agent_rbac_test_session_aware_stash_red_blue_py
    tests_agent_rbac_test_session_aware_stash_red_blue_py ~~~ tests_git_test_git_commit_concurrent_py
    tests_git_test_git_commit_concurrent_py ~~~ tests_git_test_git_commit_extreme_py
    tests_git_test_git_commit_extreme_py ~~~ tests_git_test_git_commit_gateway_py
    tests_git_test_git_commit_gateway_py ~~~ tests_git_test_reconciler_verify_autosync_py
    tests_git_test_reconciler_verify_autosync_py ~~~ tests_governance_generators_test_check_gate_inventory_drift_py
    tests_governance_generators_test_check_gate_inventory_drift_py ~~~ tests_governance_generators_test_generate_gate_registry_py
    tests_governance_generators_test_generate_gate_registry_py ~~~ tests_governance_rule_bridge_test_worktree_lifecycle_py
    tests_governance_rule_bridge_test_worktree_lifecycle_py ~~~ tests_governance_test_ast_import_rewriter_py
    tests_governance_test_ast_import_rewriter_py ~~~ tests_io_test_depgraph_schema_py
    tests_io_test_depgraph_schema_py ~~~ tests_io_test_verify_schema_health_py
    tests_io_test_verify_schema_health_py ~~~ tests_rollback_test_concurrency_guard_red_blue_py
    tests_rollback_test_concurrency_guard_red_blue_py ~~~ tests_rollback_test_concurrent_mv_guard_py
    tests_rollback_test_concurrent_mv_guard_py ~~~ tests_task_test_task_repo_gateway_e2e_py
    tests_task_test_task_repo_gateway_e2e_py ~~~ tests_test_align_panoramas_py
    tests_test_align_panoramas_py ~~~ tests_test_dataflow_design_layout_py
    tests_test_dataflow_design_layout_py ~~~ tests_test_generate_dataflow_diagram_py
    tests_test_generate_dataflow_diagram_py ~~~ tests_test_generate_decision_diagram_py
    scripts_arch_guard_arch_ssot_py["架构ssot<br/>arch_guard 共享：仓库根路径、capacity_slo /<br/>invariants / contracts 装载。<br/>_arch_ssot<br/>文件: arch_guard/_arch_ssot.py<br/>(生产态 / production)"]
    scripts_check_naming_convention_py["检查namingconvention<br/>scripts的检查器，检查某项条件是否满足<br/>check_naming_convention<br/>文件: scripts/check_naming_convention.py<br/>(生产态 / production)"]
    scripts_construction_check_statuses_py["检查statuses<br/>construction包的check_statuses模块<br/>文件: construction/check_statuses.py<br/>(生产态 / production)"]
    scripts_git_commit_py["Git提交<br/>GitCommitGateway CLI 封装<br/>git_commit<br/>文件: scripts/git_commit.py<br/>(生产态 / production)"]
    scripts_git_guard_py["Git守卫<br/>Git Guard — 拦截危险 git 命令，防止破坏其他<br/>session 的文件锁。<br/>git_guard<br/>文件: scripts/git_guard.py<br/>(生产态 / production)"]
    scripts_mcp_generate_ide_config_py["生成ide配置<br/>从 config/mcp.json 生成各 IDE MCP 配置文件<br/>（MOD-INF-013 §5.3 Step 2）。<br/>generate_ide_config<br/>文件: mcp/generate_ide_config.py<br/>(生产态 / production)"]
    scripts_migration_dm311_autonomy_core_split_py["dm311autonomy核心split<br/>DM-311: autonomy_core/ 拆分迁移执行脚本。<br/>dm311_autonomy_core_split<br/>文件: migration/dm311_autonomy_core_split.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py["worktree生命周期<br/>WorktreeLifecycle — worktree 生命周期状态机<br/>（5态 + 8转换）<br/>worktree_lifecycle<br/>文件: rule_bridge/worktree_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_governance_capability_lookup_py["能力lookup<br/>CapabilityLookup —<br/>能力->真源文件反查注册表的查询 API + 扫描<br/>/派生逻辑（合一）<br/>capability_lookup<br/>文件: governance/capability_lookup.py<br/>(生产态 / production)"]
    src_zephyr_governance_data_governance_akshare_provider_py["akshare提供器<br/>D_DATA — Akshare Data Provider<br/>文件: data_governance/akshare_provider.py<br/>(生产态 / production)"]
    src_zephyr_governance_engine_pipeline_base_py["管线基类<br/>治理/engine包的pipeline_base模块<br/>文件: engine/pipeline_base.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_delegation_engine_py["delegation引擎<br/>Delegation Engine — MOD-INF-022<br/>文件: intelligence_governance<br/>/delegation_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_query_metrics_py["查询指标<br/>QueryMetrics — SQL 查询性能监控装饰器<br/>（SH-DB-001 v2.0）<br/>query_metrics<br/>文件: observability_governance/query_metrics.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_base_repo_py["基类repo<br/>base_repo — 异常类、状态机常量、工具函数（从<br/>task_repo.py 拆分，SRC-0066）<br/>文件: persistence/base_repo.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_battlemap_schema_py["persistence/battlemap_schema<br/>battlemap Schema DDL + 不变量声明<br/>文件: persistence/battlemap_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_decisiongraph_schema_py["decisiongraph结构<br/>decisiongraph Schema DDL + 不变量声明<br/>decisiongraph_schema<br/>文件: persistence/decisiongraph_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_pg_wrapper_py["pg包装<br/>psycopg2 connection 的 sqlite3 兼容 execute()<br/>包装器（单一规范副本）。<br/>pg_wrapper<br/>文件: persistence/pg_wrapper.py<br/>(生产态 / production)"]
    src_zephyr_governance_rule_patterns_py["规则模式<br/>治理规则正则 + 安全审计模式唯一真源 (SSoT)<br/>rule_patterns<br/>文件: governance/rule_patterns.py<br/>(生产态 / production)"]
    src_zephyr_governance_strategies_strategy_base_py["策略基类<br/>D_PORTFOLIO_CORE — StrategyBase + StrategyMeta<br/>+ StrategyRegistry<br/>文件: strategies/strategy_base.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py["A2A治理适配器<br/>A2A 治理适配器 — 连接 A2A 协议与 Governance 层<br/>a2a_governance_adapter<br/>文件: layer3_coordination<br/>/a2a_governance_adapter.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_registry_governance_py["注册表治理<br/>Registry Governance — MOD-INF-037<br/>文件: infrastructure/registry_governance.py<br/>(生产态 / production)"]
    scripts_arch_guard_arch_ssot_py ~~~ scripts_check_naming_convention_py
    scripts_check_naming_convention_py ~~~ scripts_construction_check_statuses_py
    scripts_construction_check_statuses_py ~~~ scripts_git_commit_py
    scripts_git_commit_py ~~~ scripts_git_guard_py
    scripts_git_guard_py ~~~ scripts_mcp_generate_ide_config_py
    scripts_mcp_generate_ide_config_py ~~~ scripts_migration_dm311_autonomy_core_split_py
    scripts_migration_dm311_autonomy_core_split_py ~~~ src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py
    src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py ~~~ src_zephyr_governance_capability_lookup_py
    src_zephyr_governance_capability_lookup_py ~~~ src_zephyr_governance_data_governance_akshare_provider_py
    src_zephyr_governance_data_governance_akshare_provider_py ~~~ src_zephyr_governance_engine_pipeline_base_py
    src_zephyr_governance_engine_pipeline_base_py ~~~ src_zephyr_governance_intelligence_governance_delegation_engine_py
    src_zephyr_governance_intelligence_governance_delegation_engine_py ~~~ src_zephyr_governance_observability_governance_query_metrics_py
    src_zephyr_governance_observability_governance_query_metrics_py ~~~ src_zephyr_governance_persistence_base_repo_py
    src_zephyr_governance_persistence_base_repo_py ~~~ src_zephyr_governance_persistence_battlemap_schema_py
    src_zephyr_governance_persistence_battlemap_schema_py ~~~ src_zephyr_governance_persistence_decisiongraph_schema_py
    src_zephyr_governance_persistence_decisiongraph_schema_py ~~~ src_zephyr_governance_persistence_pg_wrapper_py
    src_zephyr_governance_persistence_pg_wrapper_py ~~~ src_zephyr_governance_rule_patterns_py
    src_zephyr_governance_rule_patterns_py ~~~ src_zephyr_governance_strategies_strategy_base_py
    src_zephyr_governance_strategies_strategy_base_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py ~~~ src_zephyr_infrastructure_registry_governance_py
    src_zephyr_governance_depgraph_schema_py["依赖图模式<br/>depgraph Schema DDL + 版本化迁移框架<br/>depgraph_schema<br/>文件: governance/depgraph_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_intelligence_governance_provider_base_py["提供器基类<br/>D_DATA — Data Source Layer<br/>文件: intelligence_governance/provider_base.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_task_repo_py["任务repo<br/>TaskRepository — 任务登记表 CRUD + 状态机<br/>（T-1-04）<br/>task_repo<br/>文件: persistence/task_repo.py<br/>(生产态 / production)"]
    src_zephyr_governance_depgraph_schema_py ~~~ src_zephyr_governance_intelligence_governance_provider_base_py
    src_zephyr_governance_intelligence_governance_provider_base_py ~~~ src_zephyr_governance_persistence_task_repo_py
    src_zephyr_governance_architecture_governance_post_sync_validator_py["提交同步校验器<br/>post_sync_validator — post_sync_standard<br/>命令校验逻辑的唯一真源（SSoT）。<br/>文件: architecture_governance<br/>/post_sync_validator.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_projection_engine_py["projection引擎<br/>ProjectionEngine — 事件折叠为当前状态（DW-0003）<br/>projection_engine<br/>文件: observability_governance<br/>/projection_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_persistence_sqlite_schema_py["sqlite结构<br/>SQLite 元数据层 Schema DDL + 版本化迁移框架<br/>（T-1-02 + SH-DB-001 v2.0）<br/>sqlite_schema<br/>文件: persistence/sqlite_schema.py<br/>(生产态 / production)"]
    src_zephyr_governance_architecture_governance_post_sync_validator_py ~~~ src_zephyr_governance_observability_governance_projection_engine_py
    src_zephyr_governance_observability_governance_projection_engine_py ~~~ src_zephyr_governance_persistence_sqlite_schema_py
    src_zephyr_governance_data_governance_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_governance_intelligence_governance_provider_base_py
    src_zephyr_governance_data_governance_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_governance_intelligence_governance_provider_base_py
    src_zephyr_governance_implementations_default_experiment_pipeline_py -->|导入依赖 / import_depends| src_zephyr_governance_engine_pipeline_base_py
    src_zephyr_governance_intelligence_governance_self_test_py -->|导入依赖 / import_depends| src_zephyr_governance_intelligence_governance_delegation_engine_py
    src_zephyr_governance_lifecycle_governance_transition_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_base_repo_py
    src_zephyr_governance_persistence_database_manager_py -->|导入依赖 / import_depends| src_zephyr_governance_observability_governance_query_metrics_py
    src_zephyr_governance_persistence_database_manager_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    src_zephyr_governance_persistence_battlemap_schema_py -->|导入依赖 / import_depends| src_zephyr_governance_depgraph_schema_py
    src_zephyr_governance_persistence_dataflowgraph_schema_py -->|导入依赖 / import_depends| src_zephyr_governance_depgraph_schema_py
    src_zephyr_governance_persistence_decisiongraph_schema_py -->|导入依赖 / import_depends| src_zephyr_governance_depgraph_schema_py
    src_zephyr_governance_persistence_battle_map_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_battlemap_schema_py
    src_zephyr_governance_persistence_battle_map_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_pg_wrapper_py
    src_zephyr_governance_persistence_decision_graph_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_decisiongraph_schema_py
    src_zephyr_governance_persistence_decision_graph_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_pg_wrapper_py
    src_zephyr_governance_persistence_depgraph_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_depgraph_schema_py
    src_zephyr_governance_persistence_depgraph_reader_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_pg_wrapper_py
    src_zephyr_governance_persistence_task_repo_py -->|导入依赖 / import_depends| src_zephyr_governance_architecture_governance_post_sync_validator_py
    src_zephyr_governance_persistence_task_repo_py -->|导入依赖 / import_depends| src_zephyr_governance_observability_governance_projection_engine_py
    src_zephyr_governance_persistence_task_repo_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    src_zephyr_governance_strategies_strategy_registry_py -->|导入依赖 / import_depends| src_zephyr_governance_strategies_strategy_base_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py
    scripts_generate_pathway_registry_py -->|导入依赖 / import_depends| src_zephyr_governance_rule_patterns_py
    scripts_lock_files_py -->|导入依赖 / import_depends| scripts_check_naming_convention_py
    scripts_scaffold_py -->|导入依赖 / import_depends| src_zephyr_governance_capability_lookup_py
    scripts_scaffold_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_registry_governance_py
    scripts_arch_guard_check_cross_plane_communication_py -->|导入依赖 / import_depends| scripts_arch_guard_arch_ssot_py
    scripts_arch_guard_check_hot_path_purity_py -->|导入依赖 / import_depends| scripts_arch_guard_arch_ssot_py
    scripts_arch_guard_check_schema_consistency_py -->|导入依赖 / import_depends| scripts_arch_guard_arch_ssot_py
    scripts_construction_check_statuses_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    scripts_construction_check_statuses_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_construction_demo_a2a_chat_py -->|config_depends / config_depends| scripts_construction_check_statuses_py
    scripts_construction_check_transition_code_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_construction_finalize_tasks_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    scripts_construction_finalize_tasks_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_construction_demo_e2e_pipeline_py -->|导入依赖 / import_depends| src_zephyr_governance_data_governance_akshare_provider_py
    scripts_construction_test_event_hook_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    scripts_construction_test_event_hook_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_construction_d_init_task_system_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_sqlite_schema_py
    scripts_construction_d_init_task_system_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_task_repo_py
    scripts_mcp_status_all_py -->|config_depends / config_depends| scripts_mcp_generate_ide_config_py
    scripts_migration_governance_root_split_py -->|config_depends / config_depends| scripts_migration_dm311_autonomy_core_split_py
    tests_git_test_reconciler_verify_autosync_py -->|测试依赖 / test_depends| scripts_git_commit_py
    tests_governance_rule_bridge_test_worktree_lifecycle_py -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py
    tests_io_test_verify_schema_health_py -->|测试依赖 / test_depends| src_zephyr_governance_persistence_decisiongraph_schema_py
    tests_rollback_test_concurrent_mv_guard_py -->|测试依赖 / test_depends| scripts_git_guard_py
    tests_rollback_test_concurrency_guard_red_blue_py -->|测试依赖 / test_depends| scripts_git_guard_py
    tests_task_test_task_repo_gateway_e2e_py -->|测试依赖 / test_depends| src_zephyr_governance_persistence_task_repo_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_rule_registry_collection_yaml,scripts_a2a_full_verification_py,scripts_arch_guard_arch_ssot_py,scripts_arch_guard_tools_build_ocp_manifest_py,scripts_arch_guard_tools_inject_idempotency_py,scripts_arch_guard_tools_patch_p1_paths_py,scripts_arch_guard_check_acl_boundary_py,scripts_arch_guard_check_cross_plane_communication_py,scripts_arch_guard_check_fe_acl_boundary_py,scripts_arch_guard_check_hot_path_purity_py,scripts_arch_guard_check_scaffold_exit_gates_py,scripts_arch_guard_check_schema_consistency_py,scripts_arch_guard_fitness_functions_check_aisg_gateway_py,scripts_arch_guard_fitness_functions_check_audit_log_immutability_py,scripts_arch_guard_fitness_functions_check_capacity_slo_ssot_py,scripts_arch_guard_fitness_functions_check_daily_loss_limit_py,scripts_arch_guard_fitness_functions_check_hot_warm_ipc_py,scripts_arch_guard_fitness_functions_check_idempotency_key_py,scripts_arch_guard_fitness_functions_check_log_secret_leak_py,scripts_arch_guard_fitness_functions_check_no_cross_plane_mutable_state_py,scripts_arch_guard_fitness_functions_check_ocp_signatures_py,scripts_arch_guard_fitness_functions_check_pit_compliance_py,scripts_arch_guard_fitness_functions_check_position_limit_py,scripts_arch_guard_fitness_functions_check_risk_params_consistency_py,scripts_arch_guard_fitness_functions_check_survivorship_bias_py,scripts_arch_guard_fitness_functions_check_warm_cold_async_py,scripts_arch_guard_run_all_py,scripts_check_naming_convention_py,scripts_construction_e2e_check_py,scripts_construction_e2e_deep_py,scripts_construction_check_statuses_py,scripts_construction_check_transition_code_py,scripts_construction_d_init_task_system_py,scripts_construction_demo_a2a_chat_py,scripts_construction_demo_a2a_coordination_py,scripts_construction_demo_e2e_pipeline_py,scripts_construction_finalize_tasks_py,scripts_construction_local_layer_daemon_py,scripts_construction_reset_test_task_py,scripts_construction_start_brain_py,scripts_construction_test_event_hook_py,scripts_context_generate_architecture_context_py,scripts_diagnose_breadth_failed_py,scripts_dm90971_add_test_headers_py,scripts_fix_freeze_manifest_py,scripts_fix_orphan_all_py,scripts_generate_manifest_py,scripts_generate_pathway_registry_py,scripts_git_commit_py,scripts_git_guard_py,scripts_governance_d5_architecture_generators_zoomable_html_py,scripts_governance_d7_code_check_pure_shim_py,scripts_governance_generators_generate_rule_ai_perception_index_py,scripts_hooks_auto_handoff_log_py,scripts_lock_files_py,scripts_mcp_generate_ide_config_py,scripts_mcp_launcher_py,scripts_mcp_start_all_py,scripts_mcp_status_all_py,scripts_mcp_stop_all_py,scripts_migration_dm311_autonomy_core_split_py,scripts_migration_dm314_infra_ops_split_py,scripts_migration_governance_root_split_py,scripts_ops_verify_header_completeness_py,scripts_post_checkout_guard_py,scripts_pre_commit_verify_dedup_py,scripts_rollback_py,scripts_run_deepseek_v4_exam_py,scripts_run_ollama_exam_py,scripts_scaffold_py,scripts_setup_git_guard_aliases_py,src_zephyr_gov_enforcement_rule_bridge_worktree_lifecycle_py,src_zephyr_governance_a2a_init_py,src_zephyr_governance_adapters_risk_validation_bridge_py,src_zephyr_governance_adapters_simulation_broker_py,src_zephyr_governance_agent_spec_init_py,src_zephyr_governance_agent_spec_a2a_failure_py,src_zephyr_governance_agent_spec_rbac_bridge_py,src_zephyr_governance_agent_spec_registry_py,src_zephyr_governance_architecture_governance_architecture_contracts_py,src_zephyr_governance_architecture_governance_architecture_principles_py,src_zephyr_governance_architecture_governance_blueprint_bloat_monitor_py,src_zephyr_governance_architecture_governance_blueprint_code_consistency_py,src_zephyr_governance_architecture_governance_blueprint_reconciler_py,src_zephyr_governance_architecture_governance_construction_verifier_py,src_zephyr_governance_architecture_governance_cross_env_consistency_py,src_zephyr_governance_architecture_governance_dependency_manager_py,src_zephyr_governance_architecture_governance_formal_verifier_py,src_zephyr_governance_architecture_governance_gap_analyzer_py,src_zephyr_governance_architecture_governance_llm_impact_analyzer_py,src_zephyr_governance_architecture_governance_local_first_arch_py,src_zephyr_governance_architecture_governance_path_resolver_py,src_zephyr_governance_architecture_governance_post_sync_validator_py,src_zephyr_governance_bridges_alerts_py,src_zephyr_governance_bridges_spec_auditor_py,src_zephyr_governance_capability_lookup_py,src_zephyr_governance_compliance_gate_a6_compliance_manager_py,src_zephyr_governance_compliance_gate_a6_compliance_mapper_py,src_zephyr_governance_context_governance_command_chain_length_gate_py,src_zephyr_governance_context_governance_context_budget_py,src_zephyr_governance_context_governance_context_manager_py,src_zephyr_governance_context_governance_context_package_py,src_zephyr_governance_context_governance_context_recycling_py,src_zephyr_governance_context_governance_context_switch_governor_py,src_zephyr_governance_context_governance_context_waste_detector_py,src_zephyr_governance_context_governance_conversation_tax_detector_py,src_zephyr_governance_context_governance_instruction_bloat_detector_py,src_zephyr_governance_context_governance_multi_turn_intent_analyzer_py,src_zephyr_governance_context_governance_prompt_lifecycle_py,src_zephyr_governance_context_governance_protocol_self_context_py,src_zephyr_governance_context_governance_think_time_model_py,src_zephyr_governance_data_governance_akshare_provider_py,src_zephyr_governance_data_governance_data_classification_py,src_zephyr_governance_data_governance_data_lifecycle_py,src_zephyr_governance_data_governance_data_pipeline_guard_py,src_zephyr_governance_data_governance_data_quality_py,src_zephyr_governance_data_governance_data_source_reliability_py,src_zephyr_governance_data_governance_exchange_partition_detector_py,src_zephyr_governance_data_governance_exchange_reg_monitor_py,src_zephyr_governance_data_governance_miniqmt_provider_py,src_zephyr_governance_data_governance_pricing_sync_py,src_zephyr_governance_data_governance_realtime_streaming_py,src_zephyr_governance_depgraph_schema_py,src_zephyr_governance_engine_pipeline_base_py,src_zephyr_governance_evidence_pack_py,src_zephyr_governance_financial_governance_arbitrage_asymmetry_detector_py,src_zephyr_governance_financial_governance_atomic_transaction_manager_py,src_zephyr_governance_financial_governance_flash_crash_guard_py,src_zephyr_governance_financial_governance_fsm_verifier_py,src_zephyr_governance_financial_governance_instrument_py,src_zephyr_governance_financial_governance_microstructure_defense_py,src_zephyr_governance_financial_governance_oms_risk_engine_py,src_zephyr_governance_financial_governance_risk_matrix_py,src_zephyr_governance_financial_governance_strategy_portfolio_py,src_zephyr_governance_financial_governance_strategy_scoper_py,src_zephyr_governance_implementations_default_experiment_pipeline_py,src_zephyr_governance_implementations_default_security_gateway_py,src_zephyr_governance_intelligence_governance_agent_debate_py,src_zephyr_governance_intelligence_governance_ai_self_diagnosis_py,src_zephyr_governance_intelligence_governance_aisg_sandbox_py,src_zephyr_governance_intelligence_governance_autonomy_dashboard_py,src_zephyr_governance_intelligence_governance_confidence_estimator_py,src_zephyr_governance_intelligence_governance_confidence_quantifier_py,src_zephyr_governance_intelligence_governance_continuous_trust_py,src_zephyr_governance_intelligence_governance_cross_agent_conflict_detector_py,src_zephyr_governance_intelligence_governance_cross_assistant_adapter_py,src_zephyr_governance_intelligence_governance_delegation_engine_py,src_zephyr_governance_intelligence_governance_delegation_manager_py,src_zephyr_governance_intelligence_governance_memory_provider_py,src_zephyr_governance_intelligence_governance_meta_confidence_py,src_zephyr_governance_intelligence_governance_model_provider_data_py,src_zephyr_governance_intelligence_governance_model_router_py,src_zephyr_governance_intelligence_governance_model_version_detector_py,src_zephyr_governance_intelligence_governance_multi_model_consensus_py,src_zephyr_governance_intelligence_governance_mvep_orchestrator_py,src_zephyr_governance_intelligence_governance_provider_base_py,src_zephyr_governance_intelligence_governance_provider_failover_py,src_zephyr_governance_intelligence_governance_self_benchmark_py,src_zephyr_governance_intelligence_governance_self_test_py,src_zephyr_governance_intelligence_governance_self_validator_py,src_zephyr_governance_intelligence_governance_subagent_hook_propagator_py,src_zephyr_governance_lifecycle_governance_api_lifecycle_py,src_zephyr_governance_lifecycle_governance_migration_strategy_py,src_zephyr_governance_lifecycle_governance_paper_live_transition_py,src_zephyr_governance_lifecycle_governance_post_live_verification_py,src_zephyr_governance_lifecycle_governance_transition_py,src_zephyr_governance_observability_governance_analytics_base_py,src_zephyr_governance_observability_governance_objective_tracker_py,src_zephyr_governance_observability_governance_projection_engine_py,src_zephyr_governance_observability_governance_query_metrics_py,src_zephyr_governance_persistence_base_repo_py,src_zephyr_governance_persistence_battle_map_reader_py,src_zephyr_governance_persistence_battlemap_schema_py,src_zephyr_governance_persistence_database_manager_py,src_zephyr_governance_persistence_database_service_py,src_zephyr_governance_persistence_dataflowgraph_schema_py,src_zephyr_governance_persistence_decision_graph_reader_py,src_zephyr_governance_persistence_decisiongraph_schema_py,src_zephyr_governance_persistence_depgraph_reader_py,src_zephyr_governance_persistence_pg_wrapper_py,src_zephyr_governance_persistence_protocol_state_store_py,src_zephyr_governance_persistence_sqlite_schema_py,src_zephyr_governance_persistence_task_repo_py,src_zephyr_governance_rule_patterns_py,src_zephyr_governance_services_adapter_py,src_zephyr_governance_services_cross_session_correlator_py,src_zephyr_governance_services_memory_provenance_py,src_zephyr_governance_strategies_strategy_base_py,src_zephyr_governance_strategies_strategy_registry_py,src_zephyr_infrastructure_a2a_protocol_governance_base_server_py,src_zephyr_infrastructure_a2a_protocol_governance_audit_logger_py,src_zephyr_infrastructure_a2a_protocol_governance_auditor_py,src_zephyr_infrastructure_a2a_protocol_governance_error_codes_py,src_zephyr_infrastructure_a2a_protocol_governance_governance_adapter_py,src_zephyr_infrastructure_a2a_protocol_governance_phase_hold_py,src_zephyr_infrastructure_a2a_protocol_governance_policy_engine_py,src_zephyr_infrastructure_a2a_protocol_governance_protocol_py,src_zephyr_infrastructure_a2a_protocol_governance_rate_limiter_py,src_zephyr_infrastructure_a2a_protocol_governance_session_manager_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_governance_integration_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_governance_adapter_py,src_zephyr_infrastructure_capacity_assurance_contracts_batch2_governance_py,src_zephyr_infrastructure_registry_governance_py,src_zephyr_integration_mcp_governance_server_py,src_zephyr_shared_capacity_governance_capacity_governance_loop_py,src_zephyr_shared_protocols_a2a_a2a_governance_py,tests_agent_rbac_test_session_aware_stash_red_blue_py,tests_git_test_git_commit_concurrent_py,tests_git_test_git_commit_extreme_py,tests_git_test_git_commit_gateway_py,tests_git_test_reconciler_verify_autosync_py,tests_governance_generators_test_check_gate_inventory_drift_py,tests_governance_generators_test_generate_gate_registry_py,tests_governance_rule_bridge_test_worktree_lifecycle_py,tests_governance_test_ast_import_rewriter_py,tests_io_test_depgraph_schema_py,tests_io_test_verify_schema_health_py,tests_rollback_test_concurrency_guard_red_blue_py,tests_rollback_test_concurrent_mv_guard_py,tests_task_test_task_repo_gateway_e2e_py,tests_test_align_panoramas_py,tests_test_dataflow_design_layout_py,tests_test_generate_dataflow_diagram_py,tests_test_generate_decision_diagram_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | demoe2e管线 / demo_e2e_pipeline (construction/demo_e2e_pi... | → | D_DATA 数据接入层: 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 2 | 记忆提供器 / D_DATA — Memory Provider (intelligence_gove... | → | D_DATA 数据接入层: 策略注册表 / policy_registry (data/policy_registry.py) | 导入依赖 / import_depends |
| 3 | 记忆提供器 / D_DATA — Memory Provider (intelligence_gove... | → | D_DATA 数据接入层: 提供器基类 / provider_base (data/provider_base.py) | 导入依赖 / import_depends |
| 4 | demoe2e管线 / demo_e2e_pipeline (construction/demo_e2e_pi... | → | D_FUNDAMENTAL_SIGNAL 基本面信号: 基本面信号域包 / Fundamental Signal Domain Package (signa... | 导入依赖 / import_depends |
| 5 | Git提交 / git_commit (scripts/git_commit.py) | → | D_GOV_AUDIT 审计追踪: 工作区hygiene对账器 / workspace_hygiene_reconciler (audit... | 导入依赖 / import_depends |
| 6 | projection引擎 / projection_engine (observability_governa... | → | D_GOV_AUDIT 审计追踪: 事件存储 / event_store (gov_audit/event_store.py) | 导入依赖 / import_depends |
| 7 | 数据库管理器 / database_manager (persistence/database_man... | → | D_GOV_AUDIT 审计追踪: 审计模式 / audit_schema (gov_audit/audit_schema.py) | 导入依赖 / import_depends |
| 8 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_GOV_AUDIT 审计追踪: 不可变审计写入器——JSONL 追加 + SHA-256 哈 / writer (gov... | 导入依赖 / import_depends |
| 9 | 自基准 / self_benchmark (intelligence_governance/self_ben... | → | D_GOV_CODE_QUALITY 代码质量治理: ast比较器 / ast_comparator (code_dedup/ast_comparator.py) | 导入依赖 / import_depends |
| 10 | 自基准 / self_benchmark (intelligence_governance/self_ben... | → | D_GOV_CODE_QUALITY 代码质量治理: behavioral采样器 / behavioral_sampler (code_dedup/behavio... | 导入依赖 / import_depends |
| 11 | 自基准 / self_benchmark (intelligence_governance/self_ben... | → | D_GOV_CODE_QUALITY 代码质量治理: microclone检测器 / micro_clone_detector (code_dedup/micro... | 导入依赖 / import_depends |
| 12 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_GOV_DRIFT 漂移检测: 漂移引擎 / drift_engine (gov_drift/drift_engine.py) | 导入依赖 / import_depends |
| 13 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_GOV_DRIFT 漂移检测: 漂移基础设施 / drift_infrastructure (gov_drift/drift_infr... | 导入依赖 / import_depends |
| 14 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_GOV_DRIFT 漂移检测: 漂移模型 / drift_models (gov_drift/drift_models.py) | 导入依赖 / import_depends |
| 15 | Git提交 / git_commit (scripts/git_commit.py) | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 导入依赖 / import_depends |
| 16 | 合规管理器 / compliance_manager (compliance_gate_a6/compl... | → | D_GOV_ENFORCEMENT 规则执行: 合规规则 / compliance_rule (rule_enforcement/compliance_r... | 导入依赖 / import_depends |
| 17 | 任务repo / task_repo (persistence/task_repo.py) | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 导入依赖 / import_depends |
| 18 | 测试会话感知stashredblue / test_session_aware_stash_red_b... | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 测试依赖 / test_depends |
| 19 | 测试Git提交并发 / test_git_commit_concurrent (git/test_gi... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 测试依赖 / test_depends |
| 20 | 测试Git提交并发 / test_git_commit_concurrent (git/test_gi... | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 测试依赖 / test_depends |
| 21 | 测试Gitcommitextreme / test_git_commit_extreme (git/test_... | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 测试依赖 / test_depends |
| 22 | 测试Git提交网关 / test_git_commit_gateway (git/test_git_c... | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 测试依赖 / test_depends |
| 23 | 测试taskrepogatewaye2e / test_task_repo_gateway_e2e (task... | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 测试依赖 / test_depends |
| 24 | A2A故障 / a2a_failure (agent_spec/a2a_failure.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 契约 / contracts (escalation/contracts.py) | 导入依赖 / import_depends |
| 25 | 默认安全网关 / default_security_gateway (implementations/... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 默认安全网关 / default_security_gateway (security_governa... | 导入依赖 / import_depends |
| 26 | delegation引擎 / Delegation Engine — MOD-INF-022 (intell... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级模型 / Escalation Protocol data models — MOD-INF-022... | 导入依赖 / import_depends |
| 27 | 自测试 / Escalation Protocol Self-Test — MOD-INF-022. (i... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级引擎 / Escalation Engine — MOD-INF-022 (escalation/e... | 导入依赖 / import_depends |
| 28 | 自测试 / Escalation Protocol Self-Test — MOD-INF-022. (i... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级模型 / Escalation Protocol data models — MOD-INF-022... | 导入依赖 / import_depends |
| 29 | 自测试 / Escalation Protocol Self-Test — MOD-INF-022. (i... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 熔断断路器 / Circuit Breaker — MOD-INF-022 (resilience_g... | 导入依赖 / import_depends |
| 30 | 转换 / transition (lifecycle_governance/transition.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 事件钩子 / event_hook (ops_governance/event_hook.py) | 导入依赖 / import_depends |
| 31 | 任务repo / task_repo (persistence/task_repo.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 事件钩子 / event_hook (ops_governance/event_hook.py) | 导入依赖 / import_depends |
| 32 | 适配器 / adapter (services/adapter.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级引擎 / Escalation Engine — MOD-INF-022 (escalation/e... | 导入依赖 / import_depends |
| 33 | 适配器 / adapter (services/adapter.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级模型 / Escalation Protocol data models — MOD-INF-022... | 导入依赖 / import_depends |
| 34 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级引擎 / Escalation Engine — MOD-INF-022 (escalation/e... | 导入依赖 / import_depends |
| 35 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级模型 / Escalation Protocol data models — MOD-INF-022... | 导入依赖 / import_depends |
| 36 | 转换 / transition (lifecycle_governance/transition.py) | → | D_GOV_RULE 规则治理: 门禁类型定义 / Gate Types (rule_enforcement/gate_types.py) | 导入依赖 / import_depends |
| 37 | 转换 / transition (lifecycle_governance/transition.py) | → | D_GOV_RULE 规则治理: 任务类型定义 / Task Types (rule_enforcement/task_types.py) | 导入依赖 / import_depends |
| 38 | 任务repo / task_repo (persistence/task_repo.py) | → | D_GOV_RULE 规则治理: 门禁裁决引擎 / Gate Engine (gate_engine/gate_engine.py) | 导入依赖 / import_depends |
| 39 | 任务repo / task_repo (persistence/task_repo.py) | → | D_GOV_RULE 规则治理: 门禁类型定义 / Gate Types (rule_enforcement/gate_types.py) | 导入依赖 / import_depends |
| 40 | 架构ssot / _arch_ssot (arch_guard/_arch_ssot.py) | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 41 | buildocp清单 / build_ocp_manifest (_tools/build_ocp_manif... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 42 | inject幂等性 / inject_idempotency (_tools/inject_idempote... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 43 | 补丁p1paths / patch_p1_paths (_tools/patch_p1_paths.py) | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 44 | 检查aclboundary / check_acl_boundary (arch_guard/check_ac... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 45 | check跨planecommunication / check_cross_plane_communicati... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 46 | 检查feaclboundary / check_fe_acl_boundary (arch_guard/che... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 47 | 检查hot路径purity / check_hot_path_purity (arch_guard/che... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 48 | checkscaffold退出门禁 / check_scaffold_exit_gates (arch_g... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 49 | checkscaffold退出门禁 / check_scaffold_exit_gates (arch_g... | → | D_GOV_SCRIPTS 脚本治理: yaml工具 / yaml_utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 50 | 检查模式一致性 / check_schema_consistency (arch_guard/che... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 51 | 检查aisg网关 / check_aisg_gateway (fitness_functions/chec... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 52 | check审计日志immutability / check_audit_log_immutability ... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 53 | checkdaily损失limit / check_daily_loss_limit (fitness_fun... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 54 | 检查hotwarmipc / check_hot_warm_ipc (fitness_functions/ch... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 55 | 检查幂等性密钥 / check_idempotency_key (fitness_functions... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 56 | check日志密钥leak / check_log_secret_leak (fitness_functi... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 57 | checkno跨planemutable状态 / check_no_cross_plane_mutable_... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 58 | 检查ocpsignatures / check_ocp_signatures (fitness_functio... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 59 | 检查pit合规 / check_pit_compliance (fitness_functions/che... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 60 | 检查持仓限制 / check_position_limit (fitness_functions/ch... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 61 | check风险paramsconsistency / check_risk_params_consistenc... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 62 | checkwarm冷异步 / check_warm_cold_async (fitness_function... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 63 | 重置测试任务 / reset_test_task (construction/reset_test_t... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 64 | 启动brain / start_brain (construction/start_brain.py) | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 65 | dm90971add测试headers / DM-90971: Batch add module_id sco... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 66 | 修复孤儿all / fix_orphan_all (scripts/fix_orphan_all.py) | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 67 | 修复孤儿all / fix_orphan_all (scripts/fix_orphan_all.py) | → | D_GOV_SCRIPTS 脚本治理: 文件工具 / file_utils (_shared/file_utils.py) | 导入依赖 / import_depends |
| 68 | generatepathway注册表 / generate_pathway_registry (script... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 69 | 检查pureshim / check_pure_shim (d7_code/check_pure_shim.py) | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 70 | 检查pureshim / check_pure_shim (d7_code/check_pure_shim.py) | → | D_GOV_SCRIPTS 脚本治理: encoding.py — UTF-8 编码安全工具 / encoding (_shared/enc... | 导入依赖 / import_depends |
| 71 | generate规则aiperception索引 / generate_rule_ai_perceptio... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 72 | 自动handoff日志 / auto_handoff_log (hooks/auto_handoff_lo... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 73 | 生成ide配置 / generate_ide_config (mcp/generate_ide_confi... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 74 | MCP DAG 编排启动器（MOD-INF-013 §14 拓扑排序 + Pro / lau... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 75 | 启动all / start_all (mcp/start_all.py) | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 76 | 停止all / stop_all (mcp/stop_all.py) | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 77 | dm311autonomy核心split / dm311_autonomy_core_split (migra... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 78 | dm314基础设施运维拆分 / dm314_infra_ops_split (migration/... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 79 | 文件头部完整性校验（6 格式统一入口） / verify_header_comp... | → | D_GOV_SCRIPTS 脚本治理: 文件头部格式解析 SSoT（Single Source of Truth） / frontma... | 导入依赖 / import_depends |
| 80 | verify去重 / verify_dedup (pre_commit/verify_dedup.py) | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 81 | scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TW / scaffo... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 82 | scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TW / scaffo... | → | D_GOV_SCRIPTS 脚本治理: yaml工具 / yaml_utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 83 | scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TW / scaffo... | → | D_GOV_SCRIPTS 脚本治理: GATE-11 命名规范门禁 — 全类型命名检测。 / check_naming_c... | 导入依赖 / import_depends |
| 84 | 测试生成门禁注册表 / test_generate_gate_registry (generat... | → | D_GOV_SCRIPTS 脚本治理: 生成门禁注册表 / generate_gate_registry (generators/gener... | 测试依赖 / test_depends |
| 85 | A2Afull验证 / a2a_full_verification (scripts/a2a_full_ver... | → | D_INFRASTRUCTURE 跨层契约基础设施: 包入口 / __init__ (config/__init__.py) | 导入依赖 / import_depends |
| 86 | 本地层daemon / local_layer_daemon (construction/local_lay... | → | D_INFRASTRUCTURE 跨层契约基础设施: 包入口 / __init__ (config/__init__.py) | 导入依赖 / import_depends |
| 87 | 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 88 | 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | → | D_INFRASTRUCTURE 跨层契约基础设施: 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 89 | 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | → | D_INFRASTRUCTURE 跨层契约基础设施: 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 90 | 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | → | D_INFRASTRUCTURE 跨层契约基础设施: 持仓 / position (contracts/position.py) | 导入依赖 / import_depends |
| 91 | 治理集成 / Re-export bridge for layer3_coordination gover... | → | D_INFRA_A2A A2A通信: A2A仪表盘 / a2a_dashboard (layer3_coordination/a2a_dashbo... | 导入依赖 / import_depends |
| 92 | 治理集成 / Re-export bridge for layer3_coordination gover... | → | D_INFRA_A2A A2A通信: A2A 形式化验证 — 协议属性模型检查 / a2a_formal_verificat... | 导入依赖 / import_depends |
| 93 | 治理集成 / Re-export bridge for layer3_coordination gover... | → | D_INFRA_A2A A2A通信: A2A帧negotiation / a2a_frame_negotiation (layer3_coordina... | 导入依赖 / import_depends |
| 94 | 治理集成 / Re-export bridge for layer3_coordination gover... | → | D_INFRA_A2A A2A通信: A2A协议网关 / a2a_protocol_gateway (layer3_coordination/a... | 导入依赖 / import_depends |
| 95 | 治理集成 / Re-export bridge for layer3_coordination gover... | → | D_INFRA_A2A A2A通信: A2A 分布式追踪 — 跨 Agent 请求链追踪 (Span-based) / a2a_... | 导入依赖 / import_depends |
| 96 | 治理集成 / Re-export bridge for layer3_coordination gover... | → | D_INFRA_A2A A2A通信: spec同步 / spec_sync (layer3_coordination/spec_sync.py) | 导入依赖 / import_depends |
| 97 | 回滚 / rollback (scripts/rollback.py) | → | D_INFRA_RECOVERY 回滚恢复: 回滚执行器 / rollback_executor (rollback/rollback_executo... | 导入依赖 / import_depends |
| 98 | 回滚 / rollback (scripts/rollback.py) | → | D_INFRA_RECOVERY 回滚恢复: 回滚验证器 / rollback_verifier (rollback/rollback_verifie... | 导入依赖 / import_depends |
| 99 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_INFRA_RECOVERY 回滚恢复: 回滚执行器 / rollback_executor (rollback/rollback_executo... | 导入依赖 / import_depends |
| 100 | 启动brain / start_brain (construction/start_brain.py) | → | D_INFRA_RUNTIME 运行时集成: 自动运行时核心 / auto_runtime_core (trading/auto_runtime_... | 导入依赖 / import_depends |
| 101 | 启动brain / start_brain (construction/start_brain.py) | → | D_INFRA_RUNTIME 运行时集成: 自动任务生成器 / auto_task_generator (trading/auto_task_g... | 导入依赖 / import_depends |
| 102 | Git守卫 / git_guard (scripts/git_guard.py) | → | D_INFRA_RUNTIME 运行时集成: 并发守卫 / concurrency_guard (runtime/concurrency_guard.py) | 导入依赖 / import_depends |
| 103 | postcheckout守卫 / post_checkout_guard (scripts/post_chec... | → | D_INFRA_RUNTIME 运行时集成: 并发守卫 / concurrency_guard (runtime/concurrency_guard.py) | 导入依赖 / import_depends |
| 104 | 上下文预算 / context_budget (context_governance/context_b... | → | D_INFRA_RUNTIME 运行时集成: 令牌预算 / token_budget (capacity_assurance/token_budget.py) | 导入依赖 / import_depends |
| 105 | miniqmt提供器 / miniqmt_provider (data_governance/miniqmt... | → | D_INFRA_RUNTIME 运行时集成: 数据库服务 / database_service (infrastructure/database_se... | 导入依赖 / import_depends |
| 106 | 自基准 / self_benchmark (intelligence_governance/self_ben... | → | D_INFRA_RUNTIME 运行时集成: 扫描器 / scanner (asset_inventory/scanner.py) | 导入依赖 / import_depends |
| 107 | 数据库服务 / database_service (persistence/database_servi... | → | D_INFRA_RUNTIME 运行时集成: 数据库服务 / database_service (infrastructure/database_se... | 导入依赖 / import_depends |
| 108 | 测试并发守卫redblue / test_concurrency_guard_red_blue (ro... | → | D_INFRA_RUNTIME 运行时集成: 并发守卫 / concurrency_guard (runtime/concurrency_guard.py) | 测试依赖 / test_depends |
| 109 | 本地层daemon / local_layer_daemon (construction/local_lay... | → | D_INTEGRATION 管线路由: 本地模型调度器 / local_model_scheduler (local_model/local... | 导入依赖 / import_depends |
| 110 | 启动brain / start_brain (construction/start_brain.py) | → | D_INTEGRATION 管线路由: 运行时类型定义 / runtime_types (contracts/runtime_types.py) | 导入依赖 / import_depends |
| 111 | 运行ollamaexam / run_ollama_exam (scripts/run_ollama_exam... | → | D_INTEGRATION 管线路由: OllamaChat — 通过 Ollama HTTP API 进行本地 LLM / ollama_... | 导入依赖 / import_depends |
| 112 | spec审计器 / spec_auditor (bridges/spec_auditor.py) | → | D_INTEGRATION 管线路由: 协议 / Structural Protocol interfaces for cross-module co... | 导入依赖 / import_depends |
| 113 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_INTEGRATION 管线路由: 基类服务端 / _base_server (mcp/_base_server.py) | 导入依赖 / import_depends |
| 114 | demoe2e管线 / demo_e2e_pipeline (construction/demo_e2e_pi... | → | D_INTELLIGENCE 上下文管理: 默认推理引擎 / D_ML_TRAIN — Default Inference Engine (im... | 导入依赖 / import_depends |
| 115 | diagnosebreadth失败 / diagnose_breadth_failed (scripts/di... | → | D_INTELLIGENCE 上下文管理: DeepSeekV4Chat --- DeepSeek V4 系列模型 API  / deepseek_v... | 导入依赖 / import_depends |
| 116 | diagnosebreadth失败 / diagnose_breadth_failed (scripts/di... | → | D_INTELLIGENCE 上下文管理: exam编排器 / exam_orchestrator (model_profiling/exam_orch... | 导入依赖 / import_depends |
| 117 | diagnosebreadth失败 / diagnose_breadth_failed (scripts/di... | → | D_INTELLIGENCE 上下文管理: exam测试cases / exam_test_cases (model_profiling/exam_tes... | 导入依赖 / import_depends |
| 118 | 运行deepseekv4exam / run_deepseek_v4_exam (scripts/run_de... | → | D_INTELLIGENCE 上下文管理: DeepSeekV4Chat --- DeepSeek V4 系列模型 API  / deepseek_v... | 导入依赖 / import_depends |
| 119 | 运行deepseekv4exam / run_deepseek_v4_exam (scripts/run_de... | → | D_INTELLIGENCE 上下文管理: exam编排器 / exam_orchestrator (model_profiling/exam_orch... | 导入依赖 / import_depends |
| 120 | 运行ollamaexam / run_ollama_exam (scripts/run_ollama_exam... | → | D_INTELLIGENCE 上下文管理: exam编排器 / exam_orchestrator (model_profiling/exam_orch... | 导入依赖 / import_depends |
| 121 | 模型路由器 / model_router (intelligence_governance/model_... | → | D_INTELLIGENCE 上下文管理: 提供器数据 / provider_data (model_profiling/provider_data... | 导入依赖 / import_depends |
| 122 | 模型路由器 / model_router (intelligence_governance/model_... | → | D_INTELLIGENCE 上下文管理: results写入器 / results_writer (model_profiling/results_w... | 导入依赖 / import_depends |
| 123 | 模型提供器数据 / model_provider_data (intelligence_govern... | → | D_OPS 反馈循环: 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 124 | 模型路由器 / model_router (intelligence_governance/model_... | → | D_OPS 反馈循环: 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 125 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_OPS 反馈循环: 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 126 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_OPS 反馈循环: 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 127 | analytics基类 / Re-export wrapper: analytics_base canonic... | → | D_REPORTING 报告: analytics基类 / D_REPORTING — Post-Trade Analytics Layer... | 导入依赖 / import_depends |
| 128 | demoe2e管线 / demo_e2e_pipeline (construction/demo_e2e_pi... | → | D_RISK 风控: 风控管理器 / risk_manager (risk/risk_manager.py) | 导入依赖 / import_depends |
| 129 | demoe2e管线 / demo_e2e_pipeline (construction/demo_e2e_pi... | → | D_RISK 风控: 停止亏损 / stop_loss (risk/stop_loss.py) | 导入依赖 / import_depends |
| 130 | Git提交 / git_commit (scripts/git_commit.py) | → | D_SECURITY 对抗验证: 会话并发 / session_concurrency (access_control/session_co... | 导入依赖 / import_depends |
| 131 | RBAC桥接 / rbac_bridge (agent_spec/rbac_bridge.py) | → | D_SECURITY 对抗验证: 权限守卫 / permission_guard (guards/permission_guard.py) | 导入依赖 / import_depends |
| 132 | delegation引擎 / Delegation Engine — MOD-INF-022 (intell... | → | D_SECURITY 对抗验证: 网关 / gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 133 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_SECURITY 对抗验证: 冷启动 / cold_start (gov_drift/cold_start.py) | 导入依赖 / import_depends |
| 134 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_SECURITY 对抗验证: 权限守卫 / permission_guard (guards/permission_guard.py) | 导入依赖 / import_depends |
| 135 | 测试会话感知stashredblue / test_session_aware_stash_red_b... | → | D_SECURITY 对抗验证: 会话并发 / session_concurrency (access_control/session_co... | 测试依赖 / test_depends |
| 136 | 端到端检查 / _e2e_check (construction/_e2e_check.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 137 | 端到端deep / _e2e_deep (construction/_e2e_deep.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 138 | 初始化任务系统数据库 + 创建任务系统自身的施工任务卡（吃狗... | → | D_SHARED 共享服务: 模型 / models (foundation/models.py) | 导入依赖 / import_depends |
| 139 | 重置测试任务 / reset_test_task (construction/reset_test_t... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 140 | 生成架构上下文 / generate_architecture_context (context/g... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 141 | diagnosebreadth失败 / diagnose_breadth_failed (scripts/di... | → | D_SHARED 共享服务: 密钥 / secrets (security/secrets.py) | 导入依赖 / import_depends |
| 142 | 锁files / lock_files (scripts/lock_files.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 143 | 锁files / lock_files (scripts/lock_files.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 144 | MCP DAG 编排启动器（MOD-INF-013 §14 拓扑排序 + Pro / lau... | → | D_SHARED 共享服务: 进程生命周期网关 / process_lifecycle_gateway (infra/proce... | 导入依赖 / import_depends |
| 145 | 文件头部完整性校验（6 格式统一入口） / verify_header_comp... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 146 | 运行deepseekv4exam / run_deepseek_v4_exam (scripts/run_de... | → | D_SHARED 共享服务: 密钥 / secrets (security/secrets.py) | 导入依赖 / import_depends |
| 147 | worktree生命周期 / worktree_lifecycle (rule_bridge/worktr... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 148 | worktree生命周期 / worktree_lifecycle (rule_bridge/worktr... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 149 | worktree生命周期 / worktree_lifecycle (rule_bridge/worktr... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 150 | RBAC桥接 / rbac_bridge (agent_spec/rbac_bridge.py) | → | D_SHARED 共享服务: 代理identity / agent_identity (identity/agent_identity.py) | 导入依赖 / import_depends |
| 151 | 注册表 / registry (agent_spec/registry.py) | → | D_SHARED 共享服务: 技能协议 / skill_protocol (contracts/skill_protocol.py) | 导入依赖 / import_depends |
| 152 | LLM冲击分析器 / llm_impact_analyzer (architecture_governa... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 153 | LLM冲击分析器 / llm_impact_analyzer (architecture_governa... | → | D_SHARED 共享服务: 异步工具 / async_utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 154 | 路径解析器 / path_resolver (architecture_governance/path_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 155 | 提交同步校验器 / post_sync_validator (architecture_govern... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 156 | 告警 / G-CT-006 — BudgetAlert re-exported from shared.co... | → | D_SHARED 共享服务: 预算告警 / budget_alert (escalation/budget_alert.py) | 导入依赖 / import_depends |
| 157 | 能力lookup / capability_lookup (governance/capability_loo... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 158 | 能力lookup / capability_lookup (governance/capability_loo... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 159 | 上下文包 / context_package (context_governance/context_pa... | → | D_SHARED 共享服务: A2A模式 / A2A data structure contracts — Message, Task, ... | 导入依赖 / import_depends |
| 160 | miniqmt提供器 / miniqmt_provider (data_governance/miniqmt... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 161 | pricing同步 / pricing_sync (data_governance/pricing_sync.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 162 | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 163 | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 164 | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | → | D_SHARED 共享服务: 密钥 / secrets (security/secrets.py) | 导入依赖 / import_depends |
| 165 | 管线基类 / pipeline_base (engine/pipeline_base.py) | → | D_SHARED 共享服务: 实验结果 / experiment_result (experiment/experiment_resul... | 导入依赖 / import_depends |
| 166 | 证据包 / evidence_pack (governance/evidence_pack.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 167 | atomic交易管理器 / atomic_transaction_manager (financial_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 168 | atomic交易管理器 / atomic_transaction_manager (financial_... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 169 | aisg沙箱 / aisg_sandbox (intelligence_governance/aisg_san... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 170 | 跨代理冲突检测器 / cross_agent_conflict_detector (intelli... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 171 | delegation引擎 / Delegation Engine — MOD-INF-022 (intell... | → | D_SHARED 共享服务: 异步工具 / async_utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 172 | 自基准 / self_benchmark (intelligence_governance/self_ben... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 173 | projection引擎 / projection_engine (observability_governa... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 174 | 查询指标 / query_metrics (observability_governance/query_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 175 | 查询指标 / query_metrics (observability_governance/query_... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 176 | 查询指标 / query_metrics (observability_governance/query_... | → | D_SHARED 共享服务: sqlite工厂 / sqlite_factory (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 177 | 基类repo / base_repo (persistence/base_repo.py) | → | D_SHARED 共享服务: sqlite工厂 / sqlite_factory (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 178 | 基类repo / base_repo (persistence/base_repo.py) | → | D_SHARED 共享服务: 任务类型定义 / task_types (schema/task_types.py) | 导入依赖 / import_depends |
| 179 | 基类repo / base_repo (persistence/base_repo.py) | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 180 | 数据库管理器 / database_manager (persistence/database_man... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 181 | 数据库管理器 / database_manager (persistence/database_man... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 182 | 数据库管理器 / database_manager (persistence/database_man... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 183 | decisiongraph结构 / decisiongraph_schema (persistence/dec... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 184 | decisiongraph结构 / decisiongraph_schema (persistence/dec... | → | D_SHARED 共享服务: yaml工具 / yaml_utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 185 | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 186 | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | → | D_SHARED 共享服务: sqlite工厂 / sqlite_factory (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 187 | 任务repo / task_repo (persistence/task_repo.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 188 | 任务repo / task_repo (persistence/task_repo.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 189 | 任务repo / task_repo (persistence/task_repo.py) | → | D_SHARED 共享服务: severity类型 / severity_types (schema/severity_types.py) | 导入依赖 / import_depends |
| 190 | 任务repo / task_repo (persistence/task_repo.py) | → | D_SHARED 共享服务: 任务类型定义 / task_types (schema/task_types.py) | 导入依赖 / import_depends |
| 191 | 任务repo / task_repo (persistence/task_repo.py) | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 192 | 适配器 / adapter (services/adapter.py) | → | D_SHARED 共享服务: 事件总线 / event_bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 193 | 治理适配器 / governance_adapter (governance/governance_ad... | → | D_SHARED 共享服务: 安全决策 / security_decision (security/security_decision.py) | 导入依赖 / import_depends |
| 194 | 治理适配器 / governance_adapter (governance/governance_ad... | → | D_SHARED 共享服务: 异步工具 / async_utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 195 | 协议 / protocol (governance/protocol.py) | → | D_SHARED 共享服务: A2A协议 / Core A2A Protocol interface and governance data... | 导入依赖 / import_depends |
| 196 | A2A治理适配器 / a2a_governance_adapter (layer3_coordinati... | → | D_SHARED 共享服务: 安全决策 / security_decision (security/security_decision.py) | 导入依赖 / import_depends |
| 197 | A2A治理适配器 / a2a_governance_adapter (layer3_coordinati... | → | D_SHARED 共享服务: 异步工具 / async_utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 198 | 注册表治理 / Registry Governance — MOD-INF-037 (infrastr... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 199 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_SHARED 共享服务: 代理identity / agent_identity (identity/agent_identity.py) | 导入依赖 / import_depends |
| 200 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_SHARED 共享服务: 技能协议 / skill_protocol (contracts/skill_protocol.py) | 导入依赖 / import_depends |
| 201 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 202 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 203 | 治理服务端 / governance_server (mcp/governance_server.py) | → | D_SHARED 共享服务: 异步工具 / async_utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 204 | 测试Gitcommitextreme / test_git_commit_extreme (git/test_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 测试依赖 / test_depends |
| 205 | 测试依赖图模式 / test_depgraph_schema (io/test_depgraph_s... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 测试依赖 / test_depends |
| 206 | 测试校验模式健康 / test_verify_schema_health (io/test_ver... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 测试依赖 / test_depends |
| 207 | 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | → | D_TRADING 交易运营: 经纪人接口 / D_EXECUTION_CORE — BrokerInterface (trading... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_BACKTEST 回测: decisiongraph适配器 / decisiongraph_adapter (io/decisiong... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 2 | D_EX_CORE 执行核心: 包入口 / __init__ (adapters/__init__.py) | → | 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | 导入依赖 / import_depends |
| 3 | D_EX_CORE 执行核心: 包入口 / __init__ (adapters/__init__.py) | → | 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | 导入依赖 / import_depends |
| 4 | D_EX_CORE 执行核心: 风控验证桥接 / risk_validation_bridge (adapters/risk_vali... | → | 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | 导入依赖 / import_depends |
| 5 | D_EX_CORE 执行核心: 模拟经纪人 / simulation_broker (adapters/simulation_broke... | → | 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | 导入依赖 / import_depends |
| 6 | D_EX_CORE 执行核心: 执行引擎 / D_EXECUTION_CORE — Execution Engine (ex_core/... | → | 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | 导入依赖 / import_depends |
| 7 | D_EX_CORE 执行核心: 交易会话 / trading_session (ex_core/trading_session.py) | → | 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | contract / contract |
| 8 | D_EX_CORE 执行核心: 交易会话 / trading_session (ex_core/trading_session.py) | → | 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | 导入依赖 / import_depends |
| 9 | D_EX_CORE 执行核心: 交易会话 / trading_session (ex_core/trading_session.py) | → | 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | contract / contract |
| 10 | D_EX_CORE 执行核心: 交易会话 / trading_session (ex_core/trading_session.py) | → | 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | 导入依赖 / import_depends |
| 11 | D_FEEDBACK_LOOP 反馈循环引擎: alert分发器 / alert_dispatcher (feedback_loop/alert_dispa... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 12 | D_FEEDBACK_LOOP 反馈循环引擎: 数据库桥接 / db_bridge (feedback_loop/db_bridge.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 13 | D_FEEDBACK_LOOP 反馈循环引擎: db写入器 / db_writer (feedback_loop/db_writer.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 14 | D_FEEDBACK_LOOP 反馈循环引擎: 指标收集器 / MetricsCollector: append-only metrics record... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 15 | D_FRONTEND 前端: 应用面板 / app_panel (dashboard/app_panel.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 16 | D_FRONTEND 前端: 应用面板 / app_panel (dashboard/app_panel.py) | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 17 | D_GOV_AUDIT 审计追踪: 审计模式 / audit_schema (gov_audit/audit_schema.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 18 | D_GOV_AUDIT 审计追踪: 审计信任桥接 / audit_trust_bridge (bridges/audit_trust_br... | → | continuous信任 / continuous_trust (intelligence_governanc... | 导入依赖 / import_depends |
| 19 | D_GOV_AUDIT 审计追踪: 事件存储 / event_store (gov_audit/event_store.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 20 | D_GOV_AUDIT 审计追踪: 证据包 / evidence_pack (gov_audit/evidence_pack.py) | → | 证据包 / evidence_pack (governance/evidence_pack.py) | 导入依赖 / import_depends |
| 21 | D_GOV_AUDIT 审计追踪: 知识库门禁 / kb_gate (gov_audit/kb_gate.py) | → | 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 22 | D_GOV_AUDIT 审计追踪: 审计轨迹·隐私模块 / privacy (gov_audit/privacy.py) | → | 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 23 | D_GOV_AUDIT 审计追踪: spec审计器 / spec_auditor (gov_audit/spec_auditor.py) | → | 注册表 / registry (agent_spec/registry.py) | 导入依赖 / import_depends |
| 24 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 25 | D_GOV_AUDIT 审计追踪: 快照管理器 / snapshot_manager (audit/snapshot_manager.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 26 | D_GOV_AUDIT 审计追踪: 知识库门禁 / kb_gate (semantic_audit/kb_gate.py) | → | 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 27 | D_GOV_AUDIT 审计追踪: 审计轨迹·隐私模块 / privacy (semantic_audit/privacy.py) | → | 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 28 | D_GOV_CODE_QUALITY 代码质量治理: 命令行 / cli (code_dedup/cli.py) | → | 自基准 / self_benchmark (intelligence_governance/self_ben... | 导入依赖 / import_depends |
| 29 | D_GOV_CODE_QUALITY 代码质量治理: capabilityoverlap门禁 / capability_overlap_gate (commit_g... | → | 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 30 | D_GOV_CODE_QUALITY 代码质量治理: 创建守卫 / create_guard (commit_gates/create_guard.py) | → | 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 31 | D_GOV_CODE_QUALITY 代码质量治理: 创建守卫 / create_guard (commit_gates/create_guard.py) | → | 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 32 | D_GOV_CODE_QUALITY 代码质量治理: 新文件依赖图门禁 / new_file_depgraph_gate (commit_gates/n... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 33 | D_GOV_CODE_QUALITY 代码质量治理: renamedepgraphsync门禁 / rename_depgraph_sync_gate (commi... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 34 | D_GOV_CODE_QUALITY 代码质量治理: ssotredefinition门禁 / ssot_redefinition_gate (commit_gat... | → | 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 35 | D_GOV_CODE_QUALITY 代码质量治理: 测试syncyamltodepgraphsmoke / test_sync_yaml_to_depgraph_... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 测试依赖 / test_depends |
| 36 | D_GOV_DRIFT 漂移检测: 相关性引擎 / Correlation Engine — correlation_engine.py ... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 37 | D_GOV_DRIFT 漂移检测: 仪表盘 / Coverage Dashboard — dashboard.py (gov_drift/da... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 38 | D_GOV_DRIFT 漂移检测: 漂移引擎 / drift_engine (gov_drift/drift_engine.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 39 | D_GOV_DRIFT 漂移检测: 漂移结果类型定义 / drift_result_types (gov_drift/drift_re... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 40 | D_GOV_DRIFT 漂移检测: 门禁持久化 / Gate Persistence — gate_persistence.py (gov... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 41 | D_GOV_DRIFT 漂移检测: tamperproof审计 / tamper_proof_audit (gov_drift/tamper_pr... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 42 | D_GOV_DRIFT 漂移检测: 趋势分析器 / Trend Analyzer — trend_analyzer.py (gov_dri... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 43 | D_GOV_ENFORCEMENT 规则执行: 包入口 / __init__ (behavioral_admission/__init__.py) | → | worktree生命周期 / worktree_lifecycle (rule_bridge/worktr... | 导入依赖 / import_depends |
| 44 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 45 | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | → | 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 46 | D_GOV_OPS_RESILIENCE 运维弹性治理: 自动运行器 / auto_runner (ops_governance/auto_runner.py) | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 47 | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段检查注册表 / phase_check_registry (ops_governance/pha... | → | 自测试 / Escalation Protocol Self-Test — MOD-INF-022. (i... | 导入依赖 / import_depends |
| 48 | D_GOV_OPS_RESILIENCE 运维弹性治理: 服务registration / service_registration (ops_governance/s... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 49 | D_GOV_OPS_RESILIENCE 运维弹性治理: 服务registration / service_registration (ops_governance/s... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 50 | D_GOV_OPS_RESILIENCE 运维弹性治理: f5启动集成 / f5_boot_integration (resilience_governance/f... | → | delegation引擎 / Delegation Engine — MOD-INF-022 (intell... | 导入依赖 / import_depends |
| 51 | D_GOV_OPS_RESILIENCE 运维弹性治理: f5事件订阅器 / f5_event_subscriber (resilience_governance... | → | 适配器 / adapter (services/adapter.py) | 导入依赖 / import_depends |
| 52 | D_GOV_OPS_RESILIENCE 运维弹性治理: f5关机管理器 / f5_shutdown_manager (resilience_governance... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 53 | D_GOV_OPS_RESILIENCE 运维弹性治理: 默认安全网关 / default_security_gateway (security_governa... | → | aisg沙箱 / aisg_sandbox (intelligence_governance/aisg_san... | 导入依赖 / import_depends |
| 54 | D_GOV_REPAIR 治理修复: 预算执行 / budget_enforcement (financial_governance/budge... | → | 模型路由器 / model_router (intelligence_governance/model_... | 导入依赖 / import_depends |
| 55 | D_GOV_RULE 规则治理: 规则加载器 / Rule Loader (rule_engine/rule_engine.py) | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 56 | D_GOV_RULE 规则治理: 规则加载器 / Rule Loader (rule_engine/rule_engine.py) | → | pg包装 / pg_wrapper (persistence/pg_wrapper.py) | 导入依赖 / import_depends |
| 57 | D_GOV_RULE 规则治理: 三方对齐门禁 / Triple Alignment (rule_enforcement/triple_... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 58 | D_GOV_SCRIPTS 脚本治理: 审计postsynccommands / audit_post_sync_commands (one_off/... | → | 提交同步校验器 / post_sync_validator (architecture_govern... | 导入依赖 / import_depends |
| 59 | D_GOV_SCRIPTS 脚本治理: 创建对齐任务 / # [BLUEPRINT] MOD-INF-005 | scripts/govern... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 60 | D_GOV_SCRIPTS 脚本治理: 修复brokenpostsync / fix_broken_post_sync (one_off/fix_br... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 61 | D_GOV_SCRIPTS 脚本治理: construction门禁 / construction_gate (prototype/construct... | → | 路径解析器 / path_resolver (architecture_governance/path_... | 导入依赖 / import_depends |
| 62 | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 63 | D_GOV_SCRIPTS 脚本治理: 任务show / task_show (_tasks/task_show.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 64 | D_GOV_SCRIPTS 脚本治理: 任务show / task_show (_tasks/task_show.py) | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 65 | D_GOV_SCRIPTS 脚本治理: 任务摘要 / task_summary (_tasks/task_summary.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 66 | D_GOV_SCRIPTS 脚本治理: 任务摘要 / task_summary (_tasks/task_summary.py) | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 67 | D_GOV_SCRIPTS 脚本治理: 新增deferred设计边 / add_deferred_design_edges (governanc... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 68 | D_GOV_SCRIPTS 脚本治理: G-battle-map-align: 作战地图对齐检测器（battle_map_positi... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 69 | D_GOV_SCRIPTS 脚本治理: G-battle-map-align: 作战地图对齐检测器（battle_map_positi... | → | battle_map_reader.py — 作战地图数据库只读查询工具模块 (p... | 导入依赖 / import_depends |
| 70 | D_GOV_SCRIPTS 脚本治理: G-battle-map-align: 作战地图对齐检测器（battle_map_positi... | → | dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 71 | D_GOV_SCRIPTS 脚本治理: G-battle-map-align: 作战地图对齐检测器（battle_map_positi... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 72 | D_GOV_SCRIPTS 脚本治理: [INVARIANTS] pg_advisory_lock 写锁; BM-INV-001~002 校验; ... | → | battlemap Schema DDL + 不变量声明 (persistence/battlemap_... | 导入依赖 / import_depends |
| 73 | D_GOV_SCRIPTS 脚本治理: 应用dataflowgraph / apply_dataflowgraph (governance/apply... | → | dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 74 | D_GOV_SCRIPTS 脚本治理: 应用decisiongraph / apply_decisiongraph (governance/apply... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 75 | D_GOV_SCRIPTS 脚本治理: checkssot门禁 / check_ssot_gate (governance/check_ssot_ga... | → | 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 76 | D_GOV_SCRIPTS 脚本治理: 任务自检查 / task_self_check (d11_compliance/task_self_ch... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 77 | D_GOV_SCRIPTS 脚本治理: 任务自检查 / task_self_check (d11_compliance/task_self_ch... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 78 | D_GOV_SCRIPTS 脚本治理: 校验模式健康 / verify_schema_health (d11_compliance/verif... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 79 | D_GOV_SCRIPTS 脚本治理: 校验模式健康 / verify_schema_health (d11_compliance/verif... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 80 | D_GOV_SCRIPTS 脚本治理: check结构版本writes / check_schema_version_writes (d3_met... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 81 | D_GOV_SCRIPTS 脚本治理: analyzechange冲击 / Module docstring — see module-level ... | → | LLM冲击分析器 / llm_impact_analyzer (architecture_governa... | 导入依赖 / import_depends |
| 82 | D_GOV_SCRIPTS 脚本治理: G-panorama-align: 四图对齐检测器（ARCH-053 + ARC / align_... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 83 | D_GOV_SCRIPTS 脚本治理: G-panorama-align: 四图对齐检测器（ARCH-053 + ARC / align_... | → | dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 84 | D_GOV_SCRIPTS 脚本治理: G-panorama-align: 四图对齐检测器（ARCH-053 + ARC / align_... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 85 | D_GOV_SCRIPTS 脚本治理: generate_battle_map_diagram.py — 交易决策作战地图可视化... | → | 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 86 | D_GOV_SCRIPTS 脚本治理: generate_battle_map_diagram.py — 交易决策作战地图可视化... | → | battle_map_reader.py — 作战地图数据库只读查询工具模块 (p... | 导入依赖 / import_depends |
| 87 | D_GOV_SCRIPTS 脚本治理: generate_battle_map_diagram.py — 交易决策作战地图可视化... | → | depgraph读取器 / depgraph_reader (persistence/depgraph_re... | 导入依赖 / import_depends |
| 88 | D_GOV_SCRIPTS 脚本治理: generate蓝图panorama / generate_blueprint_panorama (gener... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 89 | D_GOV_SCRIPTS 脚本治理: generate蓝图panorama / generate_blueprint_panorama (gener... | → | dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 90 | D_GOV_SCRIPTS 脚本治理: generate蓝图panorama / generate_blueprint_panorama (gener... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 91 | D_GOV_SCRIPTS 脚本治理: generate数据acquisition流程 / generate_data_acquisition_f... | → | 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 92 | D_GOV_SCRIPTS 脚本治理: 生成dataflowdiagram / generate_dataflow_diagram (generato... | → | 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 93 | D_GOV_SCRIPTS 脚本治理: 生成dataflowdiagram / generate_dataflow_diagram (generato... | → | dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 94 | D_GOV_SCRIPTS 脚本治理: generate决策diagram / generate_decision_diagram (generato... | → | 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 95 | D_GOV_SCRIPTS 脚本治理: generate决策diagram / generate_decision_diagram (generato... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 96 | D_GOV_SCRIPTS 脚本治理: generate交易流程diagram / generate_trading_flow_diagram (... | → | 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 97 | D_GOV_SCRIPTS 脚本治理: generate交易流程diagram / generate_trading_flow_diagram (... | → | 决策graph读取器 / decision_graph_reader (persistence/deci... | 导入依赖 / import_depends |
| 98 | D_GOV_SCRIPTS 脚本治理: 蓝图frontmatter对账器 / blueprint_frontmatter_reconciler ... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 99 | D_GOV_SCRIPTS 脚本治理: 同步yamlto依赖图 / sync_yaml_to_depgraph (d8_doc_sync/syn... | → | dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 100 | D_GOV_SCRIPTS 脚本治理: 提取decisiongraph / extract_decisiongraph - decisiongraph... | → | 决策graph读取器 / decision_graph_reader (persistence/deci... | 导入依赖 / import_depends |
| 101 | D_GOV_SCRIPTS 脚本治理: 提取decisiongraph / extract_decisiongraph - decisiongraph... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 102 | D_GOV_SCRIPTS 脚本治理: [INVARIANTS] YAML 是唯一真源; DB 为只读缓存; 同步单向  / ... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 103 | D_GOV_SCRIPTS 脚本治理: 生成project依赖图 / # [BLUEPRINT] MOD-INF-005 | scripts/g... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 104 | D_GOV_SCRIPTS 脚本治理: 生成路径ownershipmap / generate_path_ownership_map (gener... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 105 | D_GOV_SCRIPTS 脚本治理: 生成路径ownershipmap / generate_path_ownership_map (gener... | → | 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 106 | D_GOV_SCRIPTS 脚本治理: 备份运行时状态 / backup_runtime_state (meta/backup_runtim... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 107 | D_GOV_SCRIPTS 脚本治理: 创建任务from发现 / create_task_from_finding (meta/create_... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 108 | D_GOV_SCRIPTS 脚本治理: 创建任务from发现 / create_task_from_finding (meta/create_... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 109 | D_GOV_SCRIPTS 脚本治理: migrateto元数据tables / migrate_to_metadata_tables (gover... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 110 | D_GOV_SCRIPTS 脚本治理: 数据域审计查询 / data_domain_audit_query (oneoff/data_dom... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 111 | D_GOV_SCRIPTS 脚本治理: 查询modulepanorama / query_module_panorama (governance/qu... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 112 | D_GOV_SCRIPTS 脚本治理: 查询modulepanorama / query_module_panorama (governance/qu... | → | dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 113 | D_GOV_SCRIPTS 脚本治理: 查询modulepanorama / query_module_panorama (governance/qu... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 114 | D_GOV_SCRIPTS 脚本治理: 注册deferredmodules / register_deferred_modules (governan... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 115 | D_GOV_SCRIPTS 脚本治理: 同步panorama模块 / sync_panorama_module (governance/sync_... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 116 | D_GOV_SCRIPTS 脚本治理: 同步panorama模块 / sync_panorama_module (governance/sync_... | → | dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 117 | D_GOV_SCRIPTS 脚本治理: 同步panorama模块 / sync_panorama_module (governance/sync_... | → | decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 118 | D_INFRA_RUNTIME 运行时集成: 仪表盘 / dashboard (asset_inventory/dashboard.py) | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 119 | D_INFRA_RUNTIME 运行时集成: 升级桥接 / escalation_bridge (auto_fix_engine/escalation_... | → | 适配器 / adapter (services/adapter.py) | 导入依赖 / import_depends |
| 120 | D_INFRA_RUNTIME 运行时集成: RBAC桥接 / rbac_bridge (budget_enforcement/rbac_bridge.py) | → | RBAC桥接 / rbac_bridge (agent_spec/rbac_bridge.py) | 导入依赖 / import_depends |
| 121 | D_INFRA_RUNTIME 运行时集成: 契约总线 / contract_bus (contracts/contract_bus.py) | → | batch2治理 / batch2_governance (contracts/batch2_governan... | 导入依赖 / import_depends |
| 122 | D_INFRA_RUNTIME 运行时集成: 数据库服务 / database_service (infrastructure/database_se... | → | 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 123 | D_INFRA_RUNTIME 运行时集成: 数据库服务 / database_service (infrastructure/database_se... | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 124 | D_INFRA_RUNTIME 运行时集成: preemption管理器 / preemption_manager (pipeline/preemptio... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 125 | D_INFRA_RUNTIME 运行时集成: 自动运行时核心 / auto_runtime_core (trading/auto_runtime_... | → | 模型路由器 / model_router (intelligence_governance/model_... | 导入依赖 / import_depends |
| 126 | D_INFRA_RUNTIME 运行时集成: 自动运行时核心 / auto_runtime_core (trading/auto_runtime_... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 127 | D_INFRA_RUNTIME 运行时集成: 自动运行时核心 / auto_runtime_core (trading/auto_runtime_... | → | 适配器 / adapter (services/adapter.py) | 导入依赖 / import_depends |
| 128 | D_INFRA_RUNTIME 运行时集成: 启动钩子 / boot_hooks (trading/boot_hooks.py) | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 129 | D_INFRA_RUNTIME 运行时集成: 资源优化 / resource_optimization.py - MAPE-K autonomic re... | → | 容量治理循环 / capacity_governance_loop (capacity_governa... | 导入依赖 / import_depends |
| 130 | D_INTEGRATION 管线路由: 基类服务端 / _base_server (mcp/_base_server.py) | → | RBAC桥接 / rbac_bridge (agent_spec/rbac_bridge.py) | 导入依赖 / import_depends |
| 131 | D_INTEGRATION 管线路由: 网关服务端 / gateway_server (mcp/gateway_server.py) | → | 治理服务端 / governance_server (mcp/governance_server.py) | 导入依赖 / import_depends |
| 132 | D_INTEGRATION 管线路由: 任务管理器服务端 / ZephyrAlpha MCP Task Manager Server (m... | → | 路径解析器 / path_resolver (architecture_governance/path_... | 导入依赖 / import_depends |
| 133 | D_INTEGRATION 管线路由: 管线编排器 / pipeline_orchestrator (integration/pipeline_... | → | RBAC桥接 / rbac_bridge (agent_spec/rbac_bridge.py) | 导入依赖 / import_depends |
| 134 | D_OPS 反馈循环: 预算处理器 / budget_handler (ops_governance/budget_handle... | → | 适配器 / adapter (services/adapter.py) | 导入依赖 / import_depends |
| 135 | D_ORCHESTRATOR 代理编排器: 告警处理器 / alert_handler (contracts/alert_handler.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 136 | D_ORCHESTRATOR 代理编排器: 告警处理器 / alert_handler (contracts/alert_handler.py) | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 137 | D_ORCHESTRATOR 代理编排器: CT-ORC-SCRIPT-001 运行时桥接 / finding_bridge (contracts/... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 138 | D_PF_ALLOC 组合分配: 默认权益策略 / D_PORTFOLIO_CORE — Default Equity Long-On... | → | 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | 导入依赖 / import_depends |
| 139 | D_PF_CORE 组合核心: 策略运行器 / strategy_runner (strategy_engine/strategy_ru... | → | 策略基类 / D_PORTFOLIO_CORE — StrategyBase + StrategyMet... | 导入依赖 / import_depends |
| 140 | D_SECURITY 对抗验证: 数据库 / db (orphan_judge/db.py) | → | sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 141 | D_TRADING 交易运营: 自动分发器 / auto_dispatcher (trading/auto_dispatcher.py) | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 142 | D_TRADING 交易运营: AutoPilot — AI session 自动找活干、认领任务。 / autopilo... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 143 | D_TRADING 交易运营: Conductor — AI session 全自动指挥官。 / conductor (tradi... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 144 | D_TRADING 交易运营: ide健康daemon / ide_health_daemon (trading/ide_health_dae... | → | 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 29 个外部域直接连接（出边 207 条 + 入边 144 条 = 351 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_INFRA_A2A["D_INFRA_A2A<br/>A2A通信"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_RISK["D_RISK<br/>风控"]
    D_REPORTING["D_REPORTING<br/>报告"]
    D_FUNDAMENTAL_SIGNAL["D_FUNDAMENTAL_SIGNAL<br/>基本面信号"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_FRONTEND["D_FRONTEND<br/>前端"]
    D_GOV_REPAIR["D_GOV_REPAIR<br/>治理修复"]
    D_PF_CORE["D_PF_CORE<br/>组合核心"]
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_PF_ALLOC["D_PF_ALLOC<br/>组合分配"]
    D_GOVERNANCE -->|71条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SHARED
    D_GOVERNANCE -->|45条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_SCRIPTS
    D_GOVERNANCE -->|12条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOVERNANCE -->|9条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRA_RUNTIME
    D_GOVERNANCE -->|9条 导入依赖 / import_depends| D_INTELLIGENCE
    D_GOVERNANCE -->|9条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE -->|6条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOVERNANCE -->|6条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SECURITY
    D_GOVERNANCE -->|6条 导入依赖 / import_depends| D_INFRA_A2A
    D_GOVERNANCE -->|5条 导入依赖 / import_depends| D_INTEGRATION
    D_GOVERNANCE -->|4条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOVERNANCE -->|4条 导入依赖 / import_depends| D_GOV_RULE
    D_GOVERNANCE -->|4条 导入依赖 / import_depends| D_OPS
    D_GOVERNANCE -->|3条 导入依赖 / import_depends| D_DATA
    D_GOVERNANCE -->|3条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOVERNANCE -->|3条 导入依赖 / import_depends| D_GOV_DRIFT
    D_GOVERNANCE -->|3条 导入依赖 / import_depends| D_INFRA_RECOVERY
    D_GOVERNANCE -->|2条 导入依赖 / import_depends| D_RISK
    D_GOVERNANCE -->|1条 导入依赖 / import_depends| D_REPORTING
    D_GOVERNANCE -->|1条 导入依赖 / import_depends| D_FUNDAMENTAL_SIGNAL
    D_GOVERNANCE -->|1条 导入依赖 / import_depends| D_TRADING
    D_GOV_SCRIPTS -->|60条 导入依赖 / import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME -->|12条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_AUDIT -->|11条 导入依赖 / import_depends| D_GOVERNANCE
    D_EX_CORE -->|9条 contract / contract, 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_CODE_QUALITY -->|8条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_OPS_RESILIENCE -->|8条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_DRIFT -->|7条 导入依赖 / import_depends| D_GOVERNANCE
    D_FEEDBACK_LOOP -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_INTEGRATION -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_TRADING -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_RULE -->|3条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT -->|3条 导入依赖 / import_depends| D_GOVERNANCE
    D_ORCHESTRATOR -->|3条 导入依赖 / import_depends| D_GOVERNANCE
    D_FRONTEND -->|2条 导入依赖 / import_depends| D_GOVERNANCE
    D_OPS -->|1条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_REPAIR -->|1条 导入依赖 / import_depends| D_GOVERNANCE
    D_PF_CORE -->|1条 导入依赖 / import_depends| D_GOVERNANCE
    D_SECURITY -->|1条 导入依赖 / import_depends| D_GOVERNANCE
    D_BACKTEST -->|1条 导入依赖 / import_depends| D_GOVERNANCE
    D_PF_ALLOC -->|1条 导入依赖 / import_depends| D_GOVERNANCE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
