---
doc_type: architecture_view
title: D_GOV_SCRIPTS 脚本治理架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 56_d_gov_scripts / 脚本治理域 / Script Governance

> **功能简介 / Overview**: 脚本治理，负责脚本生命周期管理和脚本质量门禁

> **文档作用 / Purpose**: 展示 脚本治理（D_GOV_SCRIPTS）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/56_d_gov_scripts.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 56 | Number | 56 |
| 域ID | D_GOV_SCRIPTS | Domain ID | D_GOV_SCRIPTS |
| 域名称 | 脚本治理 | Domain Name | Script Governance |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 391 | Module Count | 391 |
| 域内依赖 | 754 | Internal Dependencies | 754 |
| 跨域入边 | 72 | Cross-domain Incoming | 72 |
| 跨域出边 | 141 | Cross-domain Outgoing | 141 |
| 设计态模块 | 1 | Design Modules | 1 |
| 生产态模块 | 390 | Production Modules | 390 |
| 容量 | 390/150 (超容) | Capacity | 390/150 (超容) |
| 描述 | Phase Manager阶段管理 | Description | Phase Manager阶段管理 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 391 个模块（生产态 390 + 设计态 1），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_scripts_registry_yaml["脚本注册表<br/>scripts注册表，机器学习的注册表，登记和查询已注<br/>册的条目。<br/>scripts_registry<br/>文件: catalogs/scripts_registry.yaml<br/>(生产态 / production)"]
    scripts_archive_governance_dm106_p2b_verification_py["DM-106: P2-B 迁移全量验证脚本<br/>治理包的dm106_p2b_verification模块<br/>文件: governance/dm106_p2b_verification.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_audit_post_sync_commands_py["审计postsynccommands<br/>post_sync_standard 命令可执行性巡检（防幻觉<br/>/CLI漂移）<br/>audit_post_sync_commands<br/>文件: one_off/audit_post_sync_commands.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_check_exam_case_consistency_py["考试题库一致性检查——根因治本，防止'定义-注册脱钩<br/>'复发。<br/>1. 孤儿题：定义了但未注册到 ALL_EXAM_CASES 的<br/>ExamTestCase（死代码）<br/>check_exam_case_consistency<br/>文件: one_off/check_exam_case_consistency.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_create_alignment_tasks_py["创建对齐任务<br/>对齐任务批量创建器，为治理自动化与对齐工作流生成<br/>对齐任务卡片并写入任务仓库（已归档 one-off<br/>脚本）。<br/>文件: one_off/create_alignment_tasks.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_dm105_depgraph_triage_py["dm105depgraph分诊<br/>DM-105: depgraph 未分配节点三策略处理脚本<br/>dm105_depgraph_triage<br/>文件: one_off/dm105_depgraph_triage.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_fix_broken_post_sync_py["修复brokenpostsync<br/>批量修复历史 broken post_sync_standard 命令<br/>fix_broken_post_sync<br/>文件: one_off/fix_broken_post_sync.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_list_phase0_tasks_py["listphase0任务<br/>one off包的list_phase0_tasks模块<br/>文件: one_off/list_phase0_tasks.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_phase_a_backup_py["阶段a备份<br/>阶段A安全网 Tier0/Tier1 关键文件备份<br/>phase_a_backup<br/>文件: one_off/phase_a_backup.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_rename_kebab_to_snake_py["renamekebabtosnake.py — 全项目文件名/目录名 ke<br/>全项目文件名/目录名 kebab-case → snake_case<br/>批量重命名。<br/>rename_kebab_to_snake<br/>文件: one_off/rename_kebab_to_snake.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_rename_whitelist_cleanup_py["命名规范白名单清理 - 全文替换脚本。<br/>按施工方案 docs/_working/audit/research_notes<br/>/naming_whitelist_cleanup_plan.md Phase 3 执行。<br/>rename_whitelist_cleanup<br/>文件: one_off/rename_whitelist_cleanup.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_test_lock_scenarios_py["测试锁scenarios<br/>场景 B: 两个 AI 同时修改同一文件 → 后到者被阻塞<br/>test_lock_scenarios<br/>文件: one_off/test_lock_scenarios.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_verify_final_delivery_py["(INVARIANTS) 设计态节点数>=1128; 规则表各表>0<br/>§11最终交付验证<br/>verify_final_delivery<br/>文件: one_off/verify_final_delivery.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_verify_rule_yaml_migration_py["verify规则yamlmigration<br/>verify_rule_yaml_migration.py - 6-dimensional<br/>verification of rule YAML migra...<br/>文件: one_off/verify_rule_yaml_migration.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_adversarial_log_py["红白对抗闭环记录——攻击→根源分析→修复→回归验证→知<br/>识注入全链路追踪<br/>python scripts/governance/adversarial_log.py<br/>--list         # 列出所有对抗记录<br/>文件: prototype/adversarial_log.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_adversarial_sys_master_test_py["对抗sys主测试<br/>exit 0 = 所有攻击被防御系统检测到（预期行为）<br/>文件: prototype/adversarial_sys_master_test.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_changelog_py["changelog.py — 治理域变更日志生成/追加工具.<br/>prototype包的changelog模块<br/>文件: prototype/changelog.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_check_audit_rbac_isolation_py["check审计RBACisolation<br/>静态分析 audit-trail 是否直接 import agent-rbac.<br/>check_audit_rbac_isolation<br/>文件: prototype/check_audit_rbac_isolation.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_construction_gate_py["construction门禁<br/>Construction Gate — 施工前路径校验门禁<br/>construction_gate<br/>文件: prototype/construction_gate.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_generate_asset_index_py["全项目资产索引生成器<br/>RULE-NINE 合规：生成 unified-asset-index.yaml<br/>供新 AI session 冷启动时了解项目全盘资产规模。<br/>generate_asset_index<br/>文件: prototype/generate_asset_index.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_generate_nav_table_py["生成navtable<br/>全流程导航表自动生成器 v1.0.0<br/>generate_nav_table<br/>文件: prototype/generate_nav_table.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_rebuild_audit_index_py["rebuild审计索引<br/>python scripts/governance<br/>/rebuild_audit_index.py --warn-only  #<br/>重建+警告模式<br/>文件: prototype/rebuild_audit_index.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_scan_ground_truth_deps_py["扫描groundtruthdeps<br/>Ground truth<br/>依赖扫描器，为任务卡系统与架构重构扫描真实依赖关<br/>系作为基准数据（已归档原型）。<br/>文件: prototype/scan_ground_truth_deps.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_session_simulator_py["会话模拟器<br/>session_simulator — 30 个模拟开发 session<br/>的蓝图读取事件生成器<br/>文件: prototype/session_simulator.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_sync_blueprint_status_py["同步蓝图状态<br/>此脚本零人工介入。纯机械映射。<br/>sync_blueprint_status<br/>文件: prototype/sync_blueprint_status.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_ri_boundary_check_py["riboundary检查<br/>验证 15 RI 模块的边界声明与实际代码一致性<br/>ri_boundary_check<br/>文件: vms_ri/ri_boundary_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_blindspot_check_py["VMS 盲点闭合检查器 — MOD-INF-011 · R1(33) + R2(<br/>vms ri包的vms_blindspot_check模块<br/>文件: vms_ri/vms_blindspot_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_build_completion_check_py["vms构建completion检查<br/>vms ri包的vms_build_completion_check模块<br/>文件: vms_ri/vms_build_completion_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_cross_file_check_py["VMS 跨文件内容一致性检查器 — MOD-INF-011 ·<br/>TASK-INF<br/>VMS 跨文件内容一致性检查器，校验 12 个文件中<br/>Collection 列表、嵌入维度（1024d<br/>/512d）、chunk_strategy<br/>路由、导入路径四维度一致性（已归档版）。<br/>vms_cross_file_check<br/>文件: vms_ri/vms_cross_file_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_health_check_py["vms健康检查<br/>vms ri包的vms_health_check模块<br/>文件: vms_ri/vms_health_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_migrate_py["VMS Phase 2 数据迁移脚本 — MOD-INF-011<br/>vms ri包的vms_migrate模块<br/>文件: vms_ri/vms_migrate.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_migration_dry_run_py["vms迁移dry运行<br/>VMS 迁移 dry-run 脚本，预览 unified_memory<br/>topic 到 Collection 的映射，作为 Phase 2<br/>迁移前置检查（已归档版）。<br/>vms_migration_dry_run<br/>文件: vms_ri/vms_migration_dry_run.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_phase_rollback_py["vms阶段回滚<br/>vms ri包的vms_phase_rollback模块<br/>文件: vms_ri/vms_phase_rollback.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_version_sync_check_py["VMS 版本同步检查器 — MOD-INF-011 · TASK-INF-022<br/>vms ri包的vms_version_sync_check模块<br/>文件: vms_ri/vms_version_sync_check.py<br/>(生产态 / production)"]
    scripts_governance_shared_base_py["基类<br/>对标 SCRIPT-QUALITY-001 多项条款的根因修复：<br/>文件: _shared/base.py<br/>(生产态 / production)"]
    scripts_governance_sync_cleanup_p0_auto_bridged_py["清理历史 P0 自动桥接任务<br/>历史 P0 自动桥接任务清理器<br/>（一次性止血操作），把 tags 含 auto-bridged 的<br/>PENDING P0 任务降级为<br/>P1+COMPLETED，避免自动桥接 Finding<br/>阻塞人工队列。<br/>cleanup_p0_auto_bridged<br/>文件: _sync/cleanup_p0_auto_bridged.py<br/>(生产态 / production)"]
    scripts_governance_sync_cleanup_p0_ops_pending_py["清理p0运维待处理<br/>一次性：将所有 OPS-* P0+PENDING 任务降级+完成<br/>cleanup_p0_ops_pending<br/>文件: _sync/cleanup_p0_ops_pending.py<br/>(生产态 / production)"]
    scripts_governance_sync_fix_orphan_deps_py["修复孤儿deps<br/>一次性修复孤儿依赖引用<br/>fix_orphan_deps<br/>文件: _sync/fix_orphan_deps.py<br/>(生产态 / production)"]
    scripts_governance_tasks_list_phase0_tasks_py["listphase0任务<br/>tasks包的list_phase0_tasks模块<br/>文件: _tasks/list_phase0_tasks.py<br/>(生产态 / production)"]
    scripts_governance_tasks_task_show_py["任务show<br/>governance/task_show 脚本 — 任务卡详情查询 CLI。<br/>文件: _tasks/task_show.py<br/>(生产态 / production)"]
    scripts_governance_tasks_task_summary_py["任务摘要<br/>任务系统全局摘要 CLI<br/>task_summary<br/>文件: _tasks/task_summary.py<br/>(生产态 / production)"]
    scripts_governance_add_deferred_design_edges_py["新增deferred设计边<br/>为暂缓模块添加设计态依赖边<br/>（dep_maturity='design'）。<br/>add_deferred_design_edges<br/>文件: governance/add_deferred_design_edges.py<br/>(生产态 / production)"]
    scripts_governance_align_battle_map_py["governance/align_battle_map<br/>G-battle-map-align: 作战地图对齐检测器<br/>（battle_map_positioning.md §8.3）<br/>文件: governance/align_battle_map.py<br/>(生产态 / production)"]
    scripts_governance_apply_battle_map_py["governance/apply_battle_map<br/>(INVARIANTS) pg_advisory_lock 写锁;<br/>BM-INV-001~002 校验; 事务回滚<br/>文件: governance/apply_battle_map.py<br/>(生产态 / production)"]
    scripts_governance_apply_dataflowgraph_py["应用dataflowgraph<br/>dataflowgraph 变更写入工具（CLI）<br/>apply_dataflowgraph<br/>文件: governance/apply_dataflowgraph.py<br/>(生产态 / production)"]
    scripts_governance_apply_decisiongraph_py["应用decisiongraph<br/>(INVARIANTS) pg_advisory_lock 写锁;<br/>build_status 单调推进; DEC-INV-001~005 校验;<br/>事务回滚<br/>apply_decisiongraph<br/>文件: governance/apply_decisiongraph.py<br/>(生产态 / production)"]
    scripts_governance_apply_depgraph_py["(INVARIANTS) 原子写入<br/>（RULE-ONE）；变更前验证；禁止直接覆盖<br/>depgraph 变更写入工具（RULE-SIXTEEN 强制配套）<br/>apply_depgraph<br/>文件: governance/apply_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_architecture_health_dashboard_py["架构健康仪表盘<br/>架构健康度仪表盘（自动化检测基线）<br/>architecture_health_dashboard<br/>文件: governance<br/>/architecture_health_dashboard.py<br/>(生产态 / production)"]
    scripts_governance_ast_import_rewriter_py["ast导入rewriter<br/>AST 导入重写器，governance 目录迁移时用 ast<br/>模块精确重写 import 路径（from<br/>zephyr.governance.foo → from<br/>zephyr.governance.subdir.foo），非正则替换避免误<br/>伤。<br/>文件: governance/ast_import_rewriter.py<br/>(生产态 / production)"]
    scripts_governance_audit_return_contract_usage_py["审计returncontractusage<br/>返回契约 ok 键调用方审计<br/>audit_return_contract_usage<br/>文件: governance/audit_return_contract_usage.py<br/>(生产态 / production)"]
    scripts_governance_audit_worktree_ops_telemetry_py["审计worktree运维遥测<br/>主工作区文件级擦除操作遥测完整性审计<br/>audit_worktree_ops_telemetry<br/>文件: governance/audit_worktree_ops_telemetry.py<br/>(生产态 / production)"]
    scripts_governance_check_commit_message_py["检查提交message<br/>**治本动机**：原计划 server-side pre-receive<br/>hook 在 GitHub-hosted 仓库<br/>文件: governance/check_commit_message.py<br/>(生产态 / production)"]
    scripts_governance_check_ssot_gate_py["checkssot门禁<br/>SSoT 创建门禁（pre-commit hook 双保险）。<br/>check_ssot_gate<br/>文件: governance/check_ssot_gate.py<br/>(生产态 / production)"]
    scripts_governance_d10_performance_collect_system_threads_py["collect系统threads<br/>全系统线程数快照采集器<br/>collect_system_threads<br/>文件: d10_performance/collect_system_threads.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_audit_registration_py["审计registration<br/>孤儿注册检测（RULE-TWO 防线 2）<br/>audit_registration<br/>文件: d11_compliance/audit_registration.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_ci_self_check_py["ci自检查<br/>Tier 8 — 纯 stdlib 零依赖的完整性检查。<br/>ci_self_check<br/>文件: d11_compliance/ci_self_check.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_fix_shared_bypass_py["修复共享绕过<br/>检测赋值节点是否包含 Path(__file__).parents(N)<br/>模式（不限变量名）。<br/>文件: d11_compliance/fix_shared_bypass.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_g9_compliance_check_py["G9 四蓝图跨模块集成合规门禁执行器.<br/>机械执行 7 项检查，零人工介入。<br/>g9_compliance_check<br/>文件: d11_compliance/g9_compliance_check.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_task_self_check_py["任务自检查<br/>任务系统自身健康检查<br/>task_self_check<br/>文件: d11_compliance/task_self_check.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_commit_gateway_py["校验提交网关<br/>检测裸 git commit，强制走 GitCommitGateway<br/>（根治幽灵提交）。<br/>validate_commit_gateway<br/>文件: d11_compliance/validate_commit_gateway.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_commit_message_py["校验提交message<br/>检测 commit message 是否包含 AI 归因<br/>trailer，缺失时仅警告不阻断。<br/>validate_commit_message<br/>文件: d11_compliance/validate_commit_message.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_exit_codes_py["validate退出codes<br/>审计脚本退出码规范门禁<br/>validate_exit_codes<br/>文件: d11_compliance/validate_exit_codes.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_frozen_requirements_py["校验frozenrequirements<br/>依赖版本锁定与验证（蓝图 §34.2）<br/>validate_frozen_requirements<br/>文件: d11_compliance<br/>/validate_frozen_requirements.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_manifest_admission_py["validate清单admission<br/>Manifest<br/>准入校验器，检查清单文件是否符合准入标准，决定是<br/>否允许进入治理流水线。<br/>文件: d11_compliance<br/>/validate_manifest_admission.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_no_utf8_bom_py["校验noutf8bom<br/>扫描项目中所有 .yaml / .md / .py 文件，检测<br/>UTF-8 BOM (﻿) 的存在。<br/>validate_no_utf8_bom<br/>文件: d11_compliance/validate_no_utf8_bom.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_script_naming_py["校验scriptnaming<br/>审计脚本命名规范门禁<br/>validate_script_naming<br/>文件: d11_compliance/validate_script_naming.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_script_quality_py["validatescript质量<br/>治理脚本质量合规检查<br/>validate_script_quality<br/>文件: d11_compliance/validate_script_quality.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py["validatetaskdecomposition绕过<br/>检测 AI 是否通过将高危任务拆分为多个「安全」子任<br/>务来绕过门禁。<br/>validate_task_decomposition_bypass<br/>文件: d11_compliance<br/>/validate_task_decomposition_bypass.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_vocabulary_coverage_py["校验vocabularycoverage<br/>从 JSON Schema 中提取所有 oneOf+const<br/>模式的枚举字段。<br/>文件: d11_compliance<br/>/validate_vocabulary_coverage.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_verify_audit_integrity_py["校验审计完整性<br/>审计完整性零依赖独立验证器，纯标准库实现，只需<br/>events.jsonl<br/>即可验证哈希链与签名，任何环境都能直接运行。<br/>verify_audit_integrity<br/>文件: d11_compliance/verify_audit_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_verify_schema_health_py["校验模式健康<br/>(PostgreSQL) Schema 健康度校验门禁（#ARCH-016<br/>治本）<br/>verify_schema_health<br/>文件: d11_compliance/verify_schema_health.py<br/>(生产态 / production)"]
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py["check日志器kwargs<br/>病根（Root Cause）：项目存在双日志系统<br/>（structlog + 标准 logging），<br/>文件: d12_ai_hallucination<br/>/check_logger_kwargs.py<br/>(生产态 / production)"]
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py["校验门禁提示冲突<br/>检测门禁 YAML 规则与 AGENTS.md / 项目 Prompt<br/>指令之间的冲突。<br/>validate_gate_prompt_conflict<br/>文件: d12_ai_hallucination<br/>/validate_gate_prompt_conflict.py<br/>(生产态 / production)"]
    scripts_governance_d12_ai_hallucination_validate_session_budget_py["校验会话预算<br/>Session 操作预算校验（已废弃）<br/>validate_session_budget<br/>文件: d12_ai_hallucination<br/>/validate_session_budget.py<br/>(生产态 / production)"]
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py["校验会话门禁检查<br/>Session 门禁检查完整性校验<br/>validate_session_gate_check<br/>文件: d12_ai_hallucination<br/>/validate_session_gate_check.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_archive_drafts_zone_py["草稿区生命周期归档器——扫描 arbitrated 草稿，按<br/>age 判定 wa<br/>rn/archive/skip<br/>archive_drafts_zone<br/>文件: d1_structure/archive_drafts_zone.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_audit_config_format_py["审计配置format<br/>config/ 目录格式/注释/边界快速扫描<br/>audit_config_format<br/>文件: d1_structure/audit_config_format.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_audit_directory_integrity_py["审计directory完整性<br/>01_policies_and_standards/ 目录结构完整性审计<br/>audit_directory_integrity<br/>文件: d1_structure/audit_directory_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_audit_directory_scalability_py["审计directoryscalability<br/>- 物理结构可扩展性审计 (1500模块支撑能力检查)<br/>audit_directory_scalability<br/>文件: d1_structure<br/>/audit_directory_scalability.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_audit_findings_by_scope_py["审计findingsby作用域<br/>按目录范围筛选 Finding 报告<br/>audit_findings_by_scope<br/>文件: d1_structure/audit_findings_by_scope.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_batch_create_index_md_py["批次创建索引md<br/>Batch create index.md for all directories under<br/>docs/ that lack one<br/>文件: d1_structure/batch_create_index_md.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_cbg_reset_py["cbg重置<br/>d1 structure包的cbg_reset模块<br/>文件: d1_structure/cbg_reset.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_check_directory_contract_py["检查directory契约<br/>Consumes directory_contract.yaml<br/>（目录维度约束的唯一真源，合并原先分散在<br/>文件: d1_structure/check_directory_contract.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_check_handoff_manifests_py["检查handoffmanifests<br/>验证 .trae/session_state/ 目录下所有<br/>CT-*_progress.yaml 是否存在且不超过 30 天未更新.<br/>check_handoff_manifests<br/>文件: d1_structure/check_handoff_manifests.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_check_index_integrity_py["检查索引完整性<br/>对标：PS-STD-012 §7.3（index.md 清单 vs<br/>磁盘实际文件双向差集）<br/>check_index_integrity<br/>文件: d1_structure/check_index_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_cleanup_stash_py["清理stash<br/>对标：OPS-2026062501 病根3（stash<br/>堆积无清理机制）<br/>cleanup_stash<br/>文件: d1_structure/cleanup_stash.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_detect_orphan_py_py["detect孤儿py<br/>全库孤儿 .py 文件检测<br/>detect_orphan_py<br/>文件: d1_structure/detect_orphan_py.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_detect_residual_files_py["检测residualfiles<br/>对标：GOV- §4.3（残留物检测标准）<br/>detect_residual_files<br/>文件: d1_structure/detect_residual_files.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_detect_temp_files_py["检测tempfiles<br/>扫描临时文件与缓存目录，返回 (发现列表,<br/>已扫描文件数)。<br/>文件: d1_structure/detect_temp_files.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_drafts_zone_archiver_py["draftszone归档器<br/>草稿区生命周期归档器 (Drafts Zone Lifecycle<br/>Archiver · V-16)<br/>drafts_zone_archiver<br/>文件: d1_structure/drafts_zone_archiver.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_generate_missing_index_md_py["generatemissing索引md<br/>扫描目录树，为缺失 index.md<br/>的目录自动生成索引文件。<br/>generate_missing_index_md<br/>文件: d1_structure/generate_missing_index_md.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_reset_cbg_py["重置cbg<br/>d1 structure包的reset_cbg模块<br/>文件: d1_structure/reset_cbg.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_run_script_smoke_test_py["runscriptsmoke测试<br/>治理脚本冒烟测试运行器<br/>run_script_smoke_test<br/>文件: d1_structure/run_script_smoke_test.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_sync_index_from_manifest_py["sync索引from清单<br/>从 script_manifest.yaml (SSoT) 自动同步<br/>index.md 的脚本数量。<br/>sync_index_from_manifest<br/>文件: d1_structure/sync_index_from_manifest.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_sync_policies_index_py["同步策略索引<br/>从磁盘实际扫描，自动同步 PS-IDX-001 §二<br/>文件数量表格。<br/>sync_policies_index<br/>文件: d1_structure/sync_policies_index.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_config_integrity_py["校验配置完整性<br/>运行时配置完整性十一层纵深审计 + 自动同步检测<br/>validate_config_integrity<br/>文件: d1_structure/validate_config_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_d1_output_sanity_py["校验d1outputsanity<br/>D1 产出物合理性校验（蓝图 §31 B93）<br/>validate_d1_output_sanity<br/>文件: d1_structure/validate_d1_output_sanity.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_immutable_core_py["校验不可变核心<br/>对标：PS-STD-003 ABS-01（AI 不可改<br/>immutable_core 层）<br/>validate_immutable_core<br/>文件: d1_structure/validate_immutable_core.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_index_reality_py["validate索引reality<br/>索引真实性校验器，比对索引文件与磁盘实际文件，检<br/>测索引中记录但磁盘不存在（或反之）的偏移。<br/>文件: d1_structure/validate_index_reality.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_read_before_write_py["校验readbeforewrite<br/>先读后写校验（IRN-008）<br/>validate_read_before_write<br/>文件: d1_structure/validate_read_before_write.py<br/>(生产态 / production)"]
    scripts_governance_d2_links_audit_broken_links_py["检测文档/数据文件中的断链与幽灵引用。<br/>调研发现 AI 在 .md/.csv/.yaml<br/>中编造虚假文件引用（如 dom_gov_001<br/>虚假审计闭环：<br/>audit_broken_links<br/>文件: d2_links/audit_broken_links.py<br/>(生产态 / production)"]
    scripts_governance_d2_links_detect_relative_references_py["检测relativereferences<br/>相对路径引用检测<br/>detect_relative_references<br/>文件: d2_links/detect_relative_references.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_auto_generate_index_py["自动生成索引<br/>迁移历史：从 d5_architecture/generators/ 迁入<br/>d3_metadata/（本脚本是元数据校验器，<br/>文件: d3_metadata/auto_generate_index.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_backfill_doctype_metadata_py["backfilldoctype元数据<br/>批量回填 frontmatter doc_type 字段（doc_type<br/>存量治理 Stage 2.1）<br/>backfill_doctype_metadata<br/>文件: d3_metadata/backfill_doctype_metadata.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_backfill_ttl_metadata_py["backfill存活时间元数据<br/>批量回填/重判 ttl 字段（6 格式统一入口，GATE-15<br/>存量治理 + GATE-VOCAB-CHANGE 纠偏）<br/>backfill_ttl_metadata<br/>文件: d3_metadata/backfill_ttl_metadata.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_blueprint_compliance_py["(INVARIANTS) REQUIREDSECTIONS 必须与蓝图+施工图<br/>(INVARIANTS) REQUIRED_SECTIONS<br/>必须与蓝图+施工图模板 v2.1.0<br/>COMPLIANCE_CHECKLIST 一致<br/>check_blueprint_compliance<br/>文件: d3_metadata/check_blueprint_compliance.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_frontmatter_metadata_py["检查frontmatter元数据<br/>校验 .md 文档 frontmatter 的词表字段：<br/>check_frontmatter_metadata<br/>文件: d3_metadata/check_frontmatter_metadata.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_module_singlesource_py["检查模块singlesource<br/>GATE-SSOT-SINGLESOURCE: SSoT 单一真源门禁<br/>（Phase 7 治本防复发）。<br/>check_module_singlesource<br/>文件: d3_metadata/check_module_singlesource.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_naming_convention_py["GATE-11 命名规范门禁 — 全类型命名检测。<br/>N-01  文件名大写检测 + 白名单<br/>check_naming_convention<br/>文件: d3_metadata/check_naming_convention.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_registry_consistency_py["检查注册表一致性<br/>check_registry_consistency —<br/>跨登记表一致性校验。<br/>文件: d3_metadata/check_registry_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_schema_version_writes_py["check结构版本writes<br/>G_TRAE_059 验证脚本：_schema_version 写入保护 +<br/>版本一致性检查。<br/>check_schema_version_writes<br/>文件: d3_metadata/check_schema_version_writes.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_vocab_hardcode_py["检查vocabhardcode<br/>GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）<br/>check_vocab_hardcode<br/>文件: d3_metadata/check_vocab_hardcode.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_classify_ttl_by_content_py["基于内容关键词的 ttl 精细分类审查脚本。<br/>- backfill：按 decision_tree<br/>（路径+doc_type）自动回填 ttl——执行工具<br/>classify_ttl_by_content<br/>文件: d3_metadata/classify_ttl_by_content.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_deep_content_scanner_py["deep内容扫描器<br/>对标：PS-STD-012 §7.3（doc_type<br/>与正文关键词启发式不匹配）<br/>deep_content_scanner<br/>文件: d3_metadata/deep_content_scanner.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_generate_derived_files_py["生成derivedfiles<br/>枚举自动派生生成器（Level 3 终极防御）<br/>generate_derived_files<br/>文件: d3_metadata/generate_derived_files.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_generate_rule_catalog_py["生成规则目录<br/>Scan docs/01_policies_and_standards and emit<br/>_registry/catalogs/rule_catalog_registry.yaml<br/>文件: d3_metadata/generate_rule_catalog.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_migrate_illegal_doctype_py["批量迁移非法 doctype 值（doctype 存量治理 Stage<br/>2.<br/>批量迁移非法 doc_type 值（doc_type 存量治理<br/>Stage 2.2）<br/>migrate_illegal_doctype<br/>文件: d3_metadata/migrate_illegal_doctype.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_architecture_py["校验架构<br/>从 .md / .yaml 文件读取 frontmatter 字段<br/>（统一返回 dict）。<br/>文件: d3_metadata/validate_architecture.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_blueprint_provenance_py["校验蓝图溯源<br/>校验蓝图provenance。Blueprint Provenance Gate -<br/>V-12: validate provenance triples in blueprint<br/>frontmatter<br/>文件: d3_metadata<br/>/validate_blueprint_provenance.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_module_id_py["校验模块id<br/>GATE-MODULEID: Validate module_id uniqueness<br/>and index/file consistency<br/>文件: d3_metadata/validate_module_id.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_registry_master_index_py["校验注册表主索引<br/>登记表总索引自校验门禁 (Registry Master Index<br/>Self-Check Gate · V-18).<br/>validate_registry_master_index<br/>文件: d3_metadata<br/>/validate_registry_master_index.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_tool_contracts_consistency_py["validatetool契约consistency<br/>对比 tool-contracts.yaml 中 tool 的<br/>input_schema ↔ 代码中 handler 实际注册的参数。<br/>validate_tool_contracts_consistency<br/>文件: d3_metadata<br/>/validate_tool_contracts_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d4_paths_detect_deprecated_path_writes_py["检测废弃路径writes<br/>废弃路径写入检测<br/>detect_deprecated_path_writes<br/>文件: d4_paths/detect_deprecated_path_writes.py<br/>(生产态 / production)"]
    scripts_governance_d4_paths_detect_excessive_file_moves_py["检测excessive文件moves<br/>文件过度搬迁检测<br/>detect_excessive_file_moves<br/>文件: d4_paths/detect_excessive_file_moves.py<br/>(生产态 / production)"]
    scripts_governance_d4_paths_detect_ruins_references_py["检测ruinsreferences<br/>残骸/废弃路径引用检测<br/>detect_ruins_references<br/>文件: d4_paths/detect_ruins_references.py<br/>(生产态 / production)"]
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py["检测拆分删除ref提交<br/>删除引用分离提交检测<br/>detect_split_delete_ref_commit<br/>文件: d4_paths/detect_split_delete_ref_commit.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_analyze_change_impact_py["analyzechange冲击<br/>变更影响分析器，分析某次改动会波及哪些模块与依赖<br/>，产出影响范围报告供评审决策。<br/>文件: d5_architecture/analyze_change_impact.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py["analyzecontract冲击<br/>契约变更影响分析器<br/>analyze_contract_impact<br/>文件: analyzers/analyze_contract_impact.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py["审计dependsonchaindepth<br/>depends_on 依赖链路深度审计<br/>audit_depends_on_chain_depth<br/>文件: analyzers/audit_depends_on_chain_depth.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py["measure弃用级联<br/>废弃级联影响度量<br/>measure_deprecation_cascade<br/>文件: analyzers/measure_deprecation_cascade.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_audit_agent_spec_py["审计代理spec<br/>(INVARIANTS) agent-spec 审计完整性<br/>audit_agent_spec<br/>文件: d5_architecture/audit_agent_spec.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_check_budget_health_py["(INVARIANTS)<br/>预算健康检查不可跳过;检查结果必须可机器解析<br/>预算健康检查器，检查预算执行情况是否健康，结果必<br/>须可机器解析且不可跳过。<br/>check_budget_health<br/>文件: d5_architecture/check_budget_health.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_check_drift_e2e_py["检查漂移端到端<br/>Tier 8 — 每次 CI 全量回归时运行 drift E2E +<br/>自检 + 注册表一致性。<br/>文件: d5_architecture/check_drift_e2e.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py["检查架构门禁<br/>用途：验证架构终局完成度，作为进入 beta<br/>施工阶段的门禁。<br/>v2.4.0 — 2026-05-03<br/>文件: checkers/check_architecture_gates.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py["(INVARIANTS)<br/>蓝图§5.5自动化触发机制状态列必须与代码实际实现一<br/>致<br/>; ⚠️待实现但代码已实现=DRIFT;<br/>✅已实现但代码不存在=DRIFT<br/>check_blueprint_automation_sync<br/>文件: checkers<br/>/check_blueprint_automation_sync.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py["检查蓝图代码对齐<br/>(INVARIANTS)<br/>代码(BLUEPRINT)头部module_id必须与蓝图注册表一致<br/>; 蓝图§4已实现文件必须在磁盘存在;<br/>frontmatter.build_status 必须与 depgraph 聚合<br/>build_status<br/>check_blueprint_code_alignment<br/>文件: checkers/check_blueprint_code_alignment.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py["(INVARIANTS)<br/>蓝图模板合规检查不可绕过;52项检查全覆盖<br/>蓝图模板合规检查器，52<br/>项检查全覆盖，校验蓝图文件是否符合模板规范<br/>（GOV-DOC-011），不可绕过。<br/>check_blueprint_template_compliance<br/>文件: checkers<br/>/check_blueprint_template_compliance.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py["check规范yaml漂移<br/>安全加载 YAML，返回解析对象（dict/list）。<br/>文件: checkers/check_canonical_yaml_drift.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_code_duplication_py["check代码duplication<br/>(INVARIANTS) 扫描 src/zephyr/ 下所有包;<br/>检测跨包同名文件代码重复<br/>check_code_duplication<br/>文件: checkers/check_code_duplication.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py["检查契约代码漂移<br/>— 契约-代码双写漂移阻断（盲点 C2 修复）<br/>check_contract_code_drift<br/>文件: checkers/check_contract_code_drift.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py["检查契约physical路径<br/>检查单个 physical_path 是否含连字符目录段,<br/>返回违规信息列表.<br/>文件: checkers/check_contract_physical_path.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py["check依赖direction<br/>依赖方向校验（INJ-002/008）<br/>check_dependency_direction<br/>文件: checkers/check_dependency_direction.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py["检查g6ctr合规<br/>checkers包的check_g6_ctr_compliance模块<br/>文件: checkers/check_g6_ctr_compliance.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py["check孤儿outputs<br/>(INVARIANTS) 扫描蓝图 §11 产出物 consumer_min;<br/>检测零消费者孤儿产出物<br/>check_orphan_outputs<br/>文件: checkers/check_orphan_outputs.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py["检查precommitiduniqueness<br/>扫描 .pre-commit-config.yaml 文本,返回<br/>(line_no, hook_id, repo_url, repo_line) 列表。<br/>文件: checkers/check_precommit_id_uniqueness.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py["check规则fourway对齐<br/>— 规则四方对齐门禁（ARCH-020 补建）<br/>check_rule_four_way_alignment<br/>文件: checkers/check_rule_four_way_alignment.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py["检查ssotuniqueness<br/>(INVARIANTS) 扫描所有蓝图 ssot_claims 字段;<br/>检测跨蓝图 SSoT 冲突<br/>check_ssot_uniqueness<br/>文件: checkers/check_ssot_uniqueness.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py["check追踪上下文propagation<br/>TraceContext 传播强制执行 CI 检查<br/>check_trace_context_propagation<br/>文件: checkers<br/>/check_trace_context_propagation.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_vms_ssot_py["GATE-VMS-SSOT: VMS 单一真源门禁——三重检测。<br/>checkers包的check_vms_ssot模块<br/>文件: checkers/check_vms_ssot.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_dependency_graph_py["依赖图<br/>治理域有向依赖图 — 扫描 governance/ 下所有<br/>import 生成依赖图.<br/>dependency_graph<br/>文件: d5_architecture/dependency_graph.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detect_causal_conflicts_py["检测causalconflicts<br/>治本（2026-06-27）：删除 DEFAULT_DEPGRAPH_PATH<br/>= .../depgraph.db 常量（路径污染源）。<br/>文件: d5_architecture/detect_causal_conflicts.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detect_constraint_violations_py["detect约束violations<br/>G9-Detect: 架构约束违规检测器（对照 depgraph<br/>实际数据检测 6 类违规）<br/>detect_constraint_violations<br/>文件: d5_architecture<br/>/detect_constraint_violations.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py["analyzesamename模块relations<br/>analyze_same_name_module_relations.py ---<br/>同名模块语义关系分析<br/>文件: detectors<br/>/analyze_same_name_module_relations.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py["检测depends开cycles<br/>检测循环依赖<br/>detect_depends_on_cycles<br/>文件: detectors/detect_depends_on_cycles.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py["检测废弃adrreferences<br/>对标：COND-38（引用 Deprecated ADR<br/>作为当前决策依据为条件禁止）<br/>detect_deprecated_adr_references<br/>文件: detectors<br/>/detect_deprecated_adr_references.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py["detect重复modulenames<br/>detect_duplicate_module_names.py ---<br/>同名模块语义关系分析<br/>文件: detectors/detect_duplicate_module_names.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_diagnose_depgraph_py["diagnose依赖图<br/>找出图拓扑孤儿节点（无入边无出边）。<br/>文件: d5_architecture/diagnose_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_align_panoramas_py["G-panorama-align: 四图对齐检测器（ARCH-053 + ARC<br/>H-056 四图升级）<br/>align_panoramas<br/>文件: generators/align_panoramas.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py["生成资产目录<br/>G13: 从 depgraph (PostgreSQL) 生成资产清单全景图<br/>generate_asset_catalog<br/>文件: generators/generate_asset_catalog.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py["generators/generate_battle_map_diagram<br/>generate_battle_map_diagram.py —<br/>交易决策作战地图可视化生成器<br/>文件: generators/generate_battle_map_diagram.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py["generate蓝图panorama<br/>G-panorama-gen: 蓝图 §0.6 四图对齐视图生成器<br/>（ARCH-053 + ARCH-056 + 模板 v2.1.0）<br/>generate_blueprint_panorama<br/>文件: generators/generate_blueprint_panorama.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_candidate_module_report_py["generators/generate_candidate_module_report<br/>从 candidate_module_registry.yaml<br/>生成候选模块清单报告（分片：索引 + 每域一个...<br/>文件: generators<br/>/generate_candidate_module_report.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py["generate代码wikistats<br/>Code Wiki 统计数据生成器（半自动维护机制）。<br/>generate_code_wiki_stats<br/>文件: generators/generate_code_wiki_stats.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py["生成契约目录<br/>G12: 从 depgraph (PostgreSQL) 生成契约目录全景图<br/>generate_contract_catalog<br/>文件: generators/generate_contract_catalog.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_contracts_py["生成契约<br/>治理的生成器，按规则生成所需的数据或报告<br/>文件: generators/generate_contracts.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py["generate数据acquisition流程<br/>G-acqflow: 从 tasks.yaml 生成业务数据采集流图<br/>MD（人类可读版，内嵌 Mermaid）<br/>generate_data_acquisition_flow<br/>文件: generators<br/>/generate_data_acquisition_flow.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_data_inventory_py["generate数据inventory<br/>G-inventory: 扫描 ClickHouse 生成业务数据清单 MD<br/>generate_data_inventory<br/>文件: generators/generate_data_inventory.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py["生成dataflowdiagram<br/>G-dataflow: 从 dataflowgraph (PostgreSQL)<br/>生成数据流图 Markdown 文档（内嵌 Mermaid）<br/>generate_dataflow_diagram<br/>文件: generators/generate_dataflow_diagram.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py["generate决策diagram<br/>G-decision: 从 decisiongraph (PostgreSQL)<br/>生成决策流图(.md 文档，Mermaid 内嵌)<br/>generate_decision_diagram<br/>文件: generators/generate_decision_diagram.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py["generatepanorama注册表<br/>G-panorama-registry: 自动生成全景图清单总表<br/>generate_panorama_registry<br/>文件: generators/generate_panorama_registry.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_policies_py["生成策略<br/>遍历 data_sources，对每个有非空 policy<br/>的数据源，<br/>generate_policies<br/>文件: generators/generate_policies.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py["generate交易流程diagram<br/>G-trading-flow: 从 decisiongraph + 叙事YAML +<br/>候选库 生成交易决策架构视图(.md)<br/>generate_trading_flow_diagram<br/>文件: generators<br/>/generate_trading_flow_diagram.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_pre_delete_safety_check_py["安全删除门禁脚本——RULE-THREE 强制执行器。<br/>删除任何文件前 MUST 通过5项检查：<br/>pre_delete_safety_check<br/>文件: d5_architecture/pre_delete_safety_check.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_pre_write_gate_py["prewrite门禁<br/>AI写入前强制门禁钩子: lock协议检查+GateEngine<br/>Phase评估+注册完整性验证<br/>pre_write_gate<br/>文件: d5_architecture/pre_write_gate.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py["archiverationale日志<br/>将已完成 Stage 移至 archive/<br/>子目录，主文件仅保留最近 3 个 Stage。<br/>archive_rationale_log<br/>文件: syncers/archive_rationale_log.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py["mergereadmeto索引<br/>合并readmeto索引。Strategy:<br/>文件: syncers/merge_readme_to_index.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py["同步蓝图代码索引<br/>对标：AGENTS.md §6.1 蓝图-代码同步强制约定<br/>sync_blueprint_code_index<br/>文件: syncers/sync_blueprint_code_index.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py["sync注册表fromblueprints<br/>扫描 03_modules/**/blueprint.md 的<br/>frontmatter,与 registry 对账,生成 diff<br/>或写入更新<br/>sync_registry_from_blueprints<br/>文件: syncers/sync_registry_from_blueprints.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py["校验蓝图代码同步<br/>md §6.1 蓝图-代码同步强制约定的 CI 门禁脚本<br/>validate_blueprint_code_sync<br/>文件: blueprint/validate_blueprint_code_sync.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py["校验蓝图实现文档<br/>md 6.4 铁律五 +<br/>铁律六：蓝图中声称的文件路径必须在磁盘上真实存在<br/>validate_blueprint_implementation_docs<br/>文件: blueprint<br/>/validate_blueprint_implementation_docs.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py["校验蓝图路径一致性<br/>蓝图路径一致性校验器，检查蓝图内引用的路径与实际<br/>磁盘路径是否一致，防悬空引用。<br/>文件: blueprint<br/>/validate_blueprint_path_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py["validate蓝图placement<br/>蓝图物理位置与归属链完整性校验器 (Blueprint<br/>Placement & BelongsTo Validator)<br/>validate_blueprint_placement<br/>文件: blueprint/validate_blueprint_placement.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py["validate蓝图taguniqueness<br/>校验蓝图标签uniqueness。GATE-TAG-UNIQUE -<br/>Blueprint tag uniqueness validation gate.<br/>文件: blueprint<br/>/validate_blueprint_tag_uniqueness.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py["validate生命周期refs<br/>生命周期引用约束合规检查<br/>validate_lifecycle_refs<br/>文件: lifecycle/validate_lifecycle_refs.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py["校验模块生命周期<br/>模块生命周期校验<br/>validate_module_lifecycle<br/>文件: lifecycle/validate_module_lifecycle.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py["校验会话日志索引完整性<br/>会话日志索引完整性校验器，检查会话日志与其索引文<br/>件是否对齐，防索引丢失或日志孤立。<br/>文件: session<br/>/validate_session_log_index_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py["validate会话日志updated<br/>对标：PS-STD-003 COND-16（AI 施工 session<br/>结束后必须写 session log）<br/>validate_session_log_updated<br/>文件: session/validate_session_log_updated.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py["校验adrfrontmatter一致性<br/>根因（R6 审计 P1-11/P1-12/P2-11/P2-12）：ADR<br/>分三批次产出（早期 0001~0013、<br/>validate_adr_frontmatter_consistency<br/>文件: validators<br/>/validate_adr_frontmatter_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py["校验架构审查门禁<br/>架构评审门控校验<br/>validate_arch_review_gate<br/>文件: validators/validate_arch_review_gate.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py["校验架构契约内部<br/>GATE-CONTRACT: CI gate for<br/>architecture_contract.yaml internal consistency<br/>文件: validators<br/>/validate_architecture_contract_internal.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py["validateautonomy门禁<br/>变更级别 vs AI 自治权限交叉校验<br/>validate_autonomy_gate<br/>文件: validators/validate_autonomy_gate.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py["校验btrackpackages<br/>- 原实现：B_TRACK_DIRS 硬编码 kebab_case 集合<br/>（含幻影 'kb'），与 src/zephyr/<br/>validate_b_track_packages<br/>文件: validators/validate_b_track_packages.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py["校验盲点状态<br/>D_RISK 是否已有 VaR/CVaR 实现<br/>GATE-BS: Blind Spot Reality Check<br/>文件: validators/validate_blind_spot_status.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py["validate代码yaml对齐<br/>对标：GATE-A 代码↔YAML 对齐<br/>validate_code_yaml_alignment<br/>文件: validators/validate_code_yaml_alignment.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_cross_references_py["validate跨references<br/>架构模型 YAML + 治理文档跨引用完整性闸门<br/>validate_cross_references<br/>文件: validators/validate_cross_references.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py["(INVARIANTS) 治理脚本执行正确<br/>依赖图模板验证器，校验依赖图数据是否符合模板规范<br/>，保证治理脚本执行正确。<br/>validate_dependency_graph_template<br/>文件: validators<br/>/validate_dependency_graph_template.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py["校验depends开format<br/>depends_on 条目结构化格式校验<br/>validate_depends_on_format<br/>文件: validators/validate_depends_on_format.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py["校验废弃dependents<br/>废弃文件活跃引用检测<br/>validate_deprecated_dependents<br/>文件: validators<br/>/validate_deprecated_dependents.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_directory_structure_py["校验directorystructure<br/>目录结构校验器，检查项目目录结构是否符合规范，防<br/>目录层级错乱或命名违规。<br/>文件: validators/validate_directory_structure.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_field_ownership_py["校验字段ownership<br/>对标：PS-STD-003 ABS-19~20<br/>（不在非权威文件改权威字段 / 不重复定义<br/>PS-STD-001 字段）<br/>validate_field_ownership<br/>文件: validators/validate_field_ownership.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py["validate门禁yaml<br/>针对 MOD-GATE_ENGINE 门禁体系，检测 YAML<br/>配置文件与 gate_engine.py 代码之间的漂移。<br/>文件: validators/validate_gate_yaml.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_handoff_package_py["校验handoff包<br/>对标：COND-47（HandoffPackage 8<br/>必填字段缺失为条件禁止）<br/>validate_handoff_package<br/>文件: validators/validate_handoff_package.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py["校验接口契约<br/>对标：GOV-MOD-004 IFC-001~007<br/>（模块接口契约策略）<br/>validate_interface_contracts<br/>文件: validators/validate_interface_contracts.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py["校验加载路径完整性<br/>加载路径完整性校验器，检查模块加载路径是否完整有<br/>效，防 import 断链。<br/>文件: validators/validate_load_path_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_module_schema_py["校验模块模式<br/>对标：GOV-MOD-ALPHA_SIGNAL_DOMAIN INJ-003<br/>（契约已定义）、INJ-004（生命周期状态合法）、<br/>validate_module_schema<br/>文件: validators/validate_module_schema.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py["校验nestedflatdirs<br/>嵌套与扁平目录规范校验器，检查哪些目录应嵌套、哪<br/>些应扁平，防目录结构混乱。<br/>文件: validators/validate_nested_flat_dirs.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py["校验p0模块契约<br/>对标：MAD-005（P0 模块额外条件）<br/>validate_p0_module_contracts<br/>文件: validators/validate_p0_module_contracts.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py["validatestatic清单漂移<br/>GATE-21 静态清单漂移阻断<br/>validate_static_manifest_drift<br/>文件: validators<br/>/validate_static_manifest_drift.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_target_layer_py["校验目标层<br/>对标：target_layer_vocabulary.yaml<br/>v1.0.0——target_layer 字段值体系多真源不一致修复<br/>validate_target_layer<br/>文件: validators/validate_target_layer.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py["校验threeway一致性<br/>对标：AGENTS.md §6.2（原子事务模式）<br/>validate_three_way_consistency<br/>文件: validators<br/>/validate_three_way_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py["validatemdyamlnumber漂移<br/>MD 视图与 YAML SSoT 数字漂移检测闸门<br/>validate_md_yaml_number_drift<br/>文件: yaml_md/validate_md_yaml_number_drift.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py["校验yaml接口uniqueness<br/>YAML 模块接口唯一性闸门<br/>validate_yaml_interface_uniqueness<br/>文件: yaml_md<br/>/validate_yaml_interface_uniqueness.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py["校验yaml摘要<br/>GATE-A 代码↔YAML 对齐的根治层：<br/>v1.0.0 -- 2026-05-03<br/>文件: yaml_md/validate_yaml_summaries.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_check_protected_paths_py["检查protectedpaths<br/>受保护路径写入检查<br/>check_protected_paths<br/>文件: d6_security/check_protected_paths.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_anchor_file_deletion_py["检测anchor文件deletion<br/>锚点文件删除检测<br/>detect_anchor_file_deletion<br/>文件: d6_security/detect_anchor_file_deletion.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_git_dangerous_py["检测Gitdangerous<br/>对标：PS-STD-003 ABS-26（禁止 git push --force<br/>到保护分支）<br/>detect_git_dangerous<br/>文件: d6_security/detect_git_dangerous.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_keywords_in_logs_py["检测keywords入日志<br/>日志输出敏感关键词检测<br/>detect_keywords_in_logs<br/>文件: d6_security/detect_keywords_in_logs.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_permanent_file_deletion_py["检测permanent文件deletion<br/>永久文件删除检测<br/>detect_permanent_file_deletion<br/>文件: d6_security<br/>/detect_permanent_file_deletion.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_secrets_py["检测密钥<br/>密钥/Token/凭证硬编码检测<br/>detect_secrets<br/>文件: d6_security/detect_secrets.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_shell_dangerous_py["检测shelldangerous<br/>对标：PS-STD-003 ABS-38（禁止 rm -rf /<br/>无确认破坏性删除）<br/>detect_shell_dangerous<br/>文件: d6_security/detect_shell_dangerous.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_shell_true_py["检测shelltrue<br/>对标：PS-STD-003 ABS-43（禁止使用 shell=True<br/>执行子进程）<br/>detect_shell_true<br/>文件: d6_security/detect_shell_true.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_threading_lock_py["detectthreading锁<br/>对标：PS-STD-003 ABS-40（禁止<br/>threading.Lock——项目全局异步架构）<br/>detect_threading_lock<br/>文件: d6_security/detect_threading_lock.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_vague_terms_py["检测vagueterms<br/>模糊/不确定术语检测<br/>detect_vague_terms<br/>文件: d6_security/detect_vague_terms.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_retire_tmp_artifacts_py["retiretmpartifacts — tmp/ + logs/ 退役区<br/>retire_tmp_artifacts — tmp/ + logs/ 退役区 TTL<br/>执行器（AI-03 审计 P2/P3 治本）<br/>文件: d6_security/retire_tmp_artifacts.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_run_adversarial_checks_py["run对抗checks<br/>Tier 8 — 每次 CI 运行红蓝对抗：注入混沌漂移 →<br/>蓝队检测 → 裁判对比。<br/>文件: d6_security/run_adversarial_checks.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_scan_runtime_log_secrets_py["扫描运行时日志密钥<br/>'日志输出禁止包含密钥/Token/Secret 值'<br/>scan_runtime_log_secrets<br/>文件: d6_security/scan_runtime_log_secrets.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_scan_secret_leak_py["scan密钥leak<br/>周扫描全库 secret 泄漏，Finding 写 docs<br/>/_working/audit/findings/。<br/>scan_secret_leak<br/>文件: d6_security/scan_secret_leak.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_validate_gate_discipline_py["validate门禁discipline<br/>对标：COND-33~37（门禁级别动态升降/跳级<br/>/生产关闭门禁/AI自签豁免/Pydantic静默吞错）<br/>validate_gate_discipline<br/>文件: d6_security/validate_gate_discipline.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_any_type_inferrer_py["any类型inferrer<br/>裸 Any 类型推断辅助工具 —<br/>#ARCH-ANY-GOVERNANCE-001 Phase 1.<br/>any_type_inferrer<br/>文件: d7_code/any_type_inferrer.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_ai_capability_boundary_py["行为说明<br/>合并三类路径：merge-base...HEAD<br/>（若可解析）、工作区相对 HEAD、暂存区。<br/>check_ai_capability_boundary<br/>文件: d7_code/check_ai_capability_boundary.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_encoding_py["检查encoding<br/>编码合规校验（INJ-007）<br/>check_encoding<br/>文件: d7_code/check_encoding.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_idempotency_py["检查幂等性<br/>幂等性缺失检查（HC-9）<br/>check_idempotency<br/>文件: d7_code/check_idempotency.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_merge_conflict_py["检查合并冲突<br/>合并冲突标记检测（local 替代 external<br/>pre-commit-hooks）<br/>check_merge_conflict<br/>文件: d7_code/check_merge_conflict.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_no_tests_unit_py["检查notestsunit<br/>禁止 tests/unit/ 旧路径重引入检测（local 替代<br/>pygrep）<br/>check_no_tests_unit<br/>文件: d7_code/check_no_tests_unit.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_pit_compliance_py["检查pit合规<br/>对标：GOV-AI-009 HC-10（PIT<br/>铁律绕过——回测代码访问了未来数据）<br/>check_pit_compliance<br/>文件: d7_code/check_pit_compliance.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py["检测absolute路径hardcoding<br/>绝对路径硬编码检测（蓝图 §34.1 操作陷阱）<br/>detect_absolute_path_hardcoding<br/>文件: d7_code/detect_absolute_path_hardcoding.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_direct_llm_calls_py["检测directLLMcalls<br/>裸调 LLM API 检测门禁（GATE-20）<br/>detect_direct_llm_calls<br/>文件: d7_code/detect_direct_llm_calls.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_forward_reference_py["检测前reference<br/>detect_forward_reference — 前向引用检测扫描器。<br/>文件: d7_code/detect_forward_reference.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_missing_encoding_py["检测missingencoding<br/>对标：ABS-24（Python 写文件必须指定<br/>encoding='utf-8'）<br/>detect_missing_encoding<br/>文件: d7_code/detect_missing_encoding.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_private_key_py["检测私有密钥<br/>私钥意外提交检测（local 替代 external<br/>pre-commit-hooks）<br/>detect_private_key<br/>文件: d7_code/detect_private_key.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_pydantic_any_fields_py["检测pydanticanyfields<br/>对标：REC-11（Pydantic 模型禁止 Any 类型字段）<br/>detect_pydantic_any_fields<br/>文件: d7_code/detect_pydantic_any_fields.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_silent_degradation_py["检测silent退化<br/>对标：COND-45（服务降级不写入日志为条件禁止）<br/>detect_silent_degradation<br/>文件: d7_code/detect_silent_degradation.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n06_scope_py["修复n06作用域<br/>N-06 module_id scope 前缀检测修复脚本。<br/>fix_n06_scope<br/>文件: d7_code/fix_n06_scope.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n12_ke_naming_py["N-12 KE 条目命名格式批量修复脚本。<br/>2. 更新所有文件中对旧文件名的引用<br/>fix_n12_ke_naming<br/>文件: d7_code/fix_n12_ke_naming.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n13_snake_case_py["修复n13snakecase<br/>N-13 YAML/JSON/MD 文件名 snake_case<br/>批量修复脚本。<br/>fix_n13_snake_case<br/>文件: d7_code/fix_n13_snake_case.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n14_init_all_py["N-14 初始化.py 缺少 all 批量修复脚本。<br/>py 缺少 __all__ 批量修复脚本<br/>fix_n14_init_all<br/>文件: d7_code/fix_n14_init_all.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n15_blueprint_path_py["N-15 BLUEPRINT 头部路径不存在批量修复脚本。<br/>1. kebab-case 目录名 → snake_case（57<br/>种路径，2888 个违规）<br/>fix_n15_blueprint_path<br/>文件: d7_code/fix_n15_blueprint_path.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_naming_manual_py["修复naming手册<br/>fix_naming_manual — 手动修复少量命名违规(N-11<br/>/N-10/N-03/N-09/N-16)。<br/>文件: d7_code/fix_naming_manual.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_orphan_exports_py["修复孤儿exports<br/>批量修复孤儿模块导出（RULE-TWO 防线 2 修复器）<br/>fix_orphan_exports<br/>文件: d7_code/fix_orphan_exports.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_rewrite_imports_py["rewrite导入<br/>当文件从 old_path 移到 new_path 时，扫描所有<br/>.py 文件的 import 语句，<br/>rewrite_imports<br/>文件: d7_code/rewrite_imports.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_scan_complexity_py["扫描complexity<br/>全量循环复杂度扫描器 — §5.158 暗债监控<br/>（裁定#214 Phase 4 引入）。<br/>scan_complexity<br/>文件: d7_code/scan_complexity.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_scan_consumers_accuracy_py["扫描消费者accuracy<br/>Phase 1 治本——检测历史漂移（247 个文件）。<br/>scan_consumers_accuracy<br/>文件: d7_code/scan_consumers_accuracy.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_scan_debt_py["架构债务扫描器 — 5.96 维度防御门闸（R67 引入）。<br/>检测 3 类'AI 容易复发的代码异味'：<br/>scan_debt<br/>文件: d7_code/scan_debt.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_contracts_purity_py["validate契约purity<br/>对标：COND-32（contracts<br/>目录放业务逻辑为条件禁止）<br/>validate_contracts_purity<br/>文件: d7_code/validate_contracts_purity.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_docstring_coverage_py["校验docstringcoverage<br/>检查代码里 docstring 覆盖率是否达标，没写<br/>docstring<br/>的模块会被报告，确保每个模块都有功能说明供 AI<br/>理解。<br/>validate_docstring_coverage<br/>文件: d7_code/validate_docstring_coverage.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_fle_action_metadata_py["校验fle行为元数据<br/>对标：COND-44（FLE Action 不记录 effective_from<br/>+ ttl 为条件禁止）<br/>validate_fle_action_metadata<br/>文件: d7_code/validate_fle_action_metadata.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_fle_imports_py["校验fle导入<br/>对标：PS-STD-003 COND-43~45（FLE import 实现类<br/>/ CoVe 异构）<br/>validate_fle_imports<br/>文件: d7_code/validate_fle_imports.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_import_style_py["校验导入style<br/>导入风格一致性校验<br/>validate_import_style<br/>文件: d7_code/validate_import_style.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_init_all_py["校验初始化all.py — 初始化.py all<br/>__init__.py __all__ 完整性校验器，检测有 import<br/>语句的 __init__.py 是否定义了 __all__，骨架包<br/>（空文件）跳过，对标 PEP 8 显式公开接口。<br/>validate_init_all<br/>文件: d7_code/validate_init_all.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_kb_write_provenance_py["validate知识库write溯源<br/>对标：COND-46（知识库写入不传 provenance<br/>为条件禁止）<br/>validate_kb_write_provenance<br/>文件: d7_code/validate_kb_write_provenance.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_python_syntax_py["校验pythonsyntax<br/>对标：AUDIT-09 病根分析（连字符损坏 / 语法错误）<br/>validate_python_syntax<br/>文件: d7_code/validate_python_syntax.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_test_assertion_depth_py["validate测试assertiondepth<br/>测试断言深度校验<br/>validate_test_assertion_depth<br/>文件: d7_code/validate_test_assertion_depth.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_test_coverage_py["validate测试coverage<br/>测试覆盖率治理校验器<br/>validate_test_coverage<br/>文件: d7_code/validate_test_coverage.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_type_annotation_coverage_py["校验类型annotationcoverage<br/>类型注解覆盖率校验<br/>validate_type_annotation_coverage<br/>文件: d7_code<br/>/validate_type_annotation_coverage.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_unused_imports_py["validateunused导入<br/>PS-STD-003 COND-43（代码质量维度补全）<br/>validate_unused_imports<br/>文件: d7_code/validate_unused_imports.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py["全自动注册表同步器<br/>扫描变更→更新所有相关注册表→零孤儿<br/>auto_sync_all_registries<br/>文件: d8_doc_sync/auto_sync_all_registries.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py["detectaiproductsin文档<br/>对标：GOV-DOC-006 §六（AI 生成产物必须写入<br/>.audit_cache/，禁止写入 docs/）<br/>detect_ai_products_in_docs<br/>文件: d8_doc_sync/detect_ai_products_in_docs.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py["检测datedsnapshots<br/>带日期快照文件检测<br/>detect_dated_snapshots<br/>文件: d8_doc_sync/detect_dated_snapshots.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_sync_rule_registry_py["同步规则注册表<br/>Checks that every RULE-ZERO through RULE-N in<br/>.trae/rules/project_rules.md<br/>文件: d8_doc_sync/sync_rule_registry.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_update_progress_py["update进度<br/>从 domain_progress.json 批量更新施工进度.<br/>update_progress<br/>文件: d8_doc_sync/update_progress.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py["validatedocument生命周期<br/>文档生命周期校验<br/>validate_document_lifecycle<br/>文件: d8_doc_sync/validate_document_lifecycle.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_validate_document_ttl_py["校验document存活时间<br/>对标：GOV-DOC-006 §一（TTL 合法值从<br/>ttl_vocabulary.yaml 动态加载）/ §三（LATEST<br/>命名规范）<br/>validate_document_ttl<br/>文件: d8_doc_sync/validate_document_ttl.py<br/>(生产态 / production)"]
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py["检测duplicatednormativelanguage<br/>规范用语重复定义检测<br/>detect_duplicated_normative_language<br/>文件: d9_knowledge<br/>/detect_duplicated_normative_language.py<br/>(生产态 / production)"]
    scripts_governance_d9_knowledge_detect_orphan_documents_py["detect孤儿documents<br/>对标：DOC-008#4（自创建后 > 30 天无任何文件依赖<br/>/引用的文件应审查）<br/>detect_orphan_documents<br/>文件: d9_knowledge/detect_orphan_documents.py<br/>(生产态 / production)"]
    scripts_governance_data_quality_check_tick_duplication_py["check逐笔duplication<br/>tick_data 表真重复检查工具（RULE-DATA-OPS<br/>配套，TRAE-063 §invariants DATA-OPS-INV-002）.<br/>check_tick_duplication<br/>文件: data_quality/check_tick_duplication.py<br/>(生产态 / production)"]
    scripts_governance_extract_decisiongraph_py["提取decisiongraph<br/>决策图按需提取工具，支持 --summary/--layers<br/>/--track 等参数按层与按轨道提取 decisiongraph<br/>子集。<br/>文件: governance/extract_decisiongraph.py<br/>(生产态 / production)"]
    scripts_governance_extract_depgraph_py["提取依赖图<br/>(INVARIANTS) 禁止AI直接Read 157MB<br/>depgraph文件；提取输出必须可被AI安全消费<br/>extract_depgraph<br/>文件: governance/extract_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_generate_decision_graph_py["(INVARIANTS) YAML 是唯一真源; DB 为只读缓存;<br/>同步单向<br/>YAML→DB; 不变量校验前置<br/>generate_decision_graph<br/>文件: governance/generate_decision_graph.py<br/>(生产态 / production)"]
    scripts_governance_generate_project_depgraph_py["生成project依赖图<br/>Scan 结果缓存。线程安全（ThreadPoolExecutor<br/>并发 put）。<br/>文件: governance/generate_project_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_generate_project_path_tree_py["生成project路径树<br/>从磁盘扫描生成路径全景图的tree段<br/>（运营态目录结构）。<br/>generate_project_path_tree<br/>文件: governance/generate_project_path_tree.py<br/>(生产态 / production)"]
    scripts_governance_generators_check_gate_inventory_drift_py["check门禁inventory漂移<br/>commit_gates 模块清单漂移检测（ARCH-055 治本）<br/>check_gate_inventory_drift<br/>文件: generators/check_gate_inventory_drift.py<br/>(生产态 / production)"]
    scripts_governance_generators_fix_module_manifest_layout_py["修复module清单layout<br/>校正治理脚本模块 docstring 与 ``__manifest__``<br/>的顺序<br/>fix_module_manifest_layout<br/>文件: generators/fix_module_manifest_layout.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_gate_registry_py["生成门禁注册表<br/>门禁登记表自动生成器<br/>generate_gate_registry<br/>文件: generators/generate_gate_registry.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_importlinter_py["generators/generate_importlinter<br/>generate_importlinter.py — .importlinter<br/>forbidden_modules 自动生成器<br/>文件: generators/generate_importlinter.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_path_ownership_map_py["生成路径ownershipmap<br/>从蓝图§0.1聚合生成 path_ownership_map.yaml<br/>路径归属声明。<br/>generate_path_ownership_map<br/>文件: generators/generate_path_ownership_map.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_registry_master_index_py["生成注册表主索引<br/>登记表总索引自动生成器<br/>generate_registry_master_index<br/>文件: generators<br/>/generate_registry_master_index.py<br/>(生产态 / production)"]
    scripts_governance_generators_inject_manifests_py["injectmanifests.py — 清单 批量注入器<br/>从现有的 script_manifest.yaml（手工维护、117<br/>条目）提取元数据，<br/>inject_manifests<br/>文件: generators/inject_manifests.py<br/>(生产态 / production)"]
    scripts_governance_generators_refresh_master_entries_py["refresh主条目<br/>登记表总索引 entries 自动刷新器<br/>refresh_master_entries<br/>文件: generators/refresh_master_entries.py<br/>(生产态 / production)"]
    scripts_governance_generators_sync_audit_protocol_numbers_py["sync审计protocolnumbers<br/>从 SSoT 注册表自动同步审计协议中的硬编码数字。<br/>sync_audit_protocol_numbers<br/>文件: generators/sync_audit_protocol_numbers.py<br/>(生产态 / production)"]
    scripts_governance_git_health_smoke_py["Git健康smoke<br/>AI session 启动时运行的核心工具健康度检查。<br/>git_health_smoke<br/>文件: governance/git_health_smoke.py<br/>(生产态 / production)"]
    scripts_governance_harvest_candidates_from_drafts_py["governance/harvest_candidates_from_drafts<br/>从场外草稿 CSV 抓取候选模块入候选库（一次性<br/>harvest 脚本，不进 generators/）。<br/>文件: governance<br/>/harvest_candidates_from_drafts.py<br/>(生产态 / production)"]
    scripts_governance_meta_arbitrate_findings_py["arbitratefindings.py — Finding 仲裁器（跨脚本冲<br/>Finding 仲裁器（跨脚本冲突解决引擎）<br/>arbitrate_findings<br/>文件: meta/arbitrate_findings.py<br/>(生产态 / production)"]
    scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py["孤儿filewithoutmoduleregistration<br/>Benchmark<br/>测试夹具——未登记的孤儿文件，用于测试孤儿判定器能<br/>否识别未注册文件。<br/>文件: test_fixtures<br/>/orphan_file_without_module_registration.py<br/>(生产态 / production)"]
    scripts_governance_meta_compute_sla_metrics_py["computesla指标<br/>SLA/SLO 指标计算引擎（蓝图 §8.4）<br/>compute_sla_metrics<br/>文件: meta/compute_sla_metrics.py<br/>(生产态 / production)"]
    scripts_governance_meta_create_task_from_finding_py["创建任务from发现<br/>Finding → 任务卡自动创建引擎<br/>create_task_from_finding<br/>文件: meta/create_task_from_finding.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_config_deviation_py["检测配置偏差<br/>配置文件结构完整性检测（蓝图 §28 B65 + B87）<br/>detect_config_deviation<br/>文件: meta/detect_config_deviation.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_fix_oscillation_py["检测修复振荡<br/>自修复振荡检测（蓝图 §28 B64）<br/>detect_fix_oscillation<br/>文件: meta/detect_fix_oscillation.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_hallucinated_packages_py["检测hallucinatedpackages<br/>对标（Slopsquatting 防御）+ Socket.dev 205K<br/>幻觉包检测 + PyPI JSON API。<br/>detect_hallucinated_packages<br/>文件: meta/detect_hallucinated_packages.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_script_divergence_py["检测script散度<br/>脚本实现与蓝图规范分歧检测（蓝图 §27.3 B81）<br/>detect_script_divergence<br/>文件: meta/detect_script_divergence.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_script_rot_py["检测scriptrot<br/>（脚本静默失效）检测器<br/>detect_script_rot<br/>文件: meta/detect_script_rot.py<br/>(生产态 / production)"]
    scripts_governance_meta_env_check_py["环境检查<br/>环境就绪检查门禁 (Environment Readiness Gate)<br/>env_check<br/>文件: meta/env_check.py<br/>(生产态 / production)"]
    scripts_governance_meta_finding_state_machine_py["finding状态machine<br/>Finding 全生命周期状态机<br/>finding_state_machine<br/>文件: meta/finding_state_machine.py<br/>(生产态 / production)"]
    scripts_governance_meta_gate_engine_selfcheck_py["门禁引擎selfcheck<br/>独立脚本，验证 MOD-GATE_ENGINE Gate Engine<br/>自身的完整性。<br/>文件: meta/gate_engine_selfcheck.py<br/>(生产态 / production)"]
    scripts_governance_meta_governance_watchdog_py["治理watchdog<br/>BLUEPRINT 必须匹配 generate_project_depgraph.py<br/>L2755 正则 ^(MOD-/D-/SH-/SYS-/PLACEHOLDER)<br/>文件: meta/governance_watchdog.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_error_budget_py["管理错误预算<br/>管理可用性 Error Budget 和准确率 Error Budget<br/>的消耗/监控/冻结。<br/>manage_error_budget<br/>文件: meta/manage_error_budget.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_finding_timeseries_py["管理发现timeseries<br/>Finding 时序数据库 + 趋势分析引擎<br/>manage_finding_timeseries<br/>文件: meta/manage_finding_timeseries.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_script_ab_test_py["managescriptab测试<br/>对标（Script A/B 对照）+ Netflix Kayenta 自动<br/>Canary 分析。<br/>manage_script_ab_test<br/>文件: meta/manage_script_ab_test.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_script_retirement_py["管理scriptretirement<br/>脚本退役/废弃生命周期管理<br/>manage_script_retirement<br/>文件: meta/manage_script_retirement.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_shadow_mode_py["manage影子mode<br/>管理新脚本的 Phase1(Shadow)→Phase2(Warn)→Phase3<br/>(Active) 生命周期。<br/>manage_shadow_mode<br/>文件: meta/manage_shadow_mode.py<br/>(生产态 / production)"]
    scripts_governance_meta_mutation_test_post_sync_validator_py["mutation测试postsync校验器<br/>目的：机械注入源码变异到 post_sync_validator.py<br/>的副本，复用<br/>mutation_test_post_sync_validator<br/>文件: meta/mutation_test_post_sync_validator.py<br/>(生产态 / production)"]
    scripts_governance_meta_mutation_test_reconciliation_registry_py["mutation测试对账注册表<br/>目的：机械注入源码变异到<br/>``reconciliation_registry.py`` 的副本，复用<br/>mutation_test_reconciliation_registry<br/>文件: meta<br/>/mutation_test_reconciliation_registry.py<br/>(生产态 / production)"]
    scripts_governance_meta_phase_e_context_check_py["阶段e上下文检查<br/>Phase E: AI context injection verification<br/>script<br/>文件: meta/phase_e_context_check.py<br/>(生产态 / production)"]
    scripts_governance_meta_pre_op_check_py["AI操作前准入控制器 — 写/删文件前的机械门禁检查.<br/>本脚本是 RULE-ZERO~EIGHT 的代码级强制执行层。<br/>pre_op_check<br/>文件: meta/pre_op_check.py<br/>(生产态 / production)"]
    scripts_governance_meta_score_script_effectiveness_py["评分scripteffectiveness<br/>脚本有效性评分（蓝图 §27.12 B90）<br/>score_script_effectiveness<br/>文件: meta/score_script_effectiveness.py<br/>(生产态 / production)"]
    scripts_governance_meta_session_startup_check_py["会话启动检查<br/>Session 冷启动自检 — 运行 Phase 0 全部 14<br/>个检查并输出状态报告.<br/>session_startup_check<br/>文件: meta/session_startup_check.py<br/>(生产态 / production)"]
    scripts_governance_meta_trace_finding_lifecycle_py["追踪发现生命周期<br/>对标（C1→C5 全链路 Tracing）+ OpenTelemetry<br/>distributed tracing 概念。<br/>trace_finding_lifecycle<br/>文件: meta/trace_finding_lifecycle.py<br/>(生产态 / production)"]
    scripts_governance_meta_track_script_costs_py["trackscriptcosts.py — 脚本执行 AI 费用追踪<br/>track_script_costs.py — 脚本执行 AI 费用追踪<br/>文件: meta/track_script_costs.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_automation_boundary_py["validate自动化boundary<br/>自动化边界校验器，检查哪些操作应自动化、哪些应保<br/>留人工，防止越界自动化。<br/>文件: meta/validate_automation_boundary.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_cross_model_consensus_py["校验跨模型共识<br/>多AI模型共识验证引擎<br/>validate_cross_model_consensus<br/>文件: meta/validate_cross_model_consensus.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_dependency_chain_py["校验依赖链<br/>依赖链拓扑顺序验证<br/>validate_dependency_chain<br/>文件: meta/validate_dependency_chain.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_emergency_bypass_log_py["validateemergency绕过日志<br/>应急绕过审计脚本<br/>validate_emergency_bypass_log<br/>文件: meta/validate_emergency_bypass_log.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_end_to_end_benchmark_py["校验结束to结束基准<br/>对标（END-TO-END 基准测试）+ Kayenta Score<br/>Computation。<br/>validate_end_to_end_benchmark<br/>文件: meta/validate_end_to_end_benchmark.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_environment_health_py["校验环境健康<br/>脚本运行环境健康检查<br/>validate_environment_health<br/>文件: meta/validate_environment_health.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_false_negatives_py["校验falsenegatives<br/>维护一个'已知有缺陷的测试用例库'（golden<br/>set），定期验证脚本系统<br/>validate_false_negatives<br/>文件: meta/validate_false_negatives.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_gate_engine_external_py["校验门禁引擎外部<br/>独立的外部验证脚本，从进程外部确认 Gate Engine<br/>未被篡改/损坏。<br/>validate_gate_engine_external<br/>文件: meta/validate_gate_engine_external.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_mutation_testing_py["校验mutationtesting<br/>变异测试引擎（蓝图 §19.2 + B75）<br/>validate_mutation_testing<br/>文件: meta/validate_mutation_testing.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_rule_freshness_py["validate规则freshness<br/>AI Session 注入文件新鲜度检查（蓝图 §22.3 +<br/>B62）<br/>validate_rule_freshness<br/>文件: meta/validate_rule_freshness.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_rules_file_backdoor_py["校验rules文件backdoor<br/>AI 规则文件隐形投毒攻击。<br/>validate_rules_file_backdoor<br/>文件: meta/validate_rules_file_backdoor.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_rules_integrity_py["validaterules完整性<br/>规则文件完整性保护<br/>validate_rules_integrity<br/>文件: meta/validate_rules_integrity.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_script_onboarding_py["校验scriptonboarding<br/>执行 V1-V12 检查，返回通过/失败及逐项结果。<br/>文件: meta/validate_script_onboarding.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_script_provenance_py["validatescript溯源<br/>为每个治理脚本生成和维护起源元数据：<br/>validate_script_provenance<br/>文件: meta/validate_script_provenance.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_script_system_health_py["validatescript系统健康<br/>脚本系统健康自检（Meta 维度 / 第 13 维度）<br/>validate_script_system_health<br/>文件: meta/validate_script_system_health.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_threshold_changes_py["校验阈值changes<br/>阈值变更审计日志<br/>validate_threshold_changes<br/>文件: meta/validate_threshold_changes.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_trust_tier_py["校验信任层<br/>在 pre_commit 和 CI 中运行，检查当前变更是否与<br/>trust_tier_policy.yaml 定义<br/>validate_trust_tier<br/>文件: meta/validate_trust_tier.py<br/>(生产态 / production)"]
    scripts_governance_meta_verify_reconciliation_registry_py["校验对账注册表<br/>仿 ``post_sync_validator.py`` SSoT<br/>解耦模式），检查 8 项结构/行为不变量，打印<br/>verify_reconciliation_registry<br/>文件: meta/verify_reconciliation_registry.py<br/>(生产态 / production)"]
    scripts_governance_migrate_sqlite_to_pg_migrate_data_py["migrate数据<br/>SQLite → PostgreSQL 运营数据迁移脚本<br/>migrate_data<br/>文件: migrate_sqlite_to_pg/migrate_data.py<br/>(生产态 / production)"]
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py["种子fromyaml<br/>从 YAML 真源灌种子表（5.32.10<br/>治本：种子与迁移拆分）<br/>seed_from_yaml<br/>文件: migrate_sqlite_to_pg/seed_from_yaml.py<br/>(生产态 / production)"]
    scripts_governance_migrate_to_metadata_tables_py["migrateto元数据tables<br/>裁定#209 Stage 2 一次性迁移脚本<br/>migrate_to_metadata_tables<br/>文件: governance/migrate_to_metadata_tables.py<br/>(生产态 / production)"]
    scripts_governance_oneoff_data_domain_audit_query_py["数据域审计查询<br/>数据域设计态排查 - DB 现状查询（Phase<br/>2，只读不写）。<br/>data_domain_audit_query<br/>文件: oneoff/data_domain_audit_query.py<br/>(生产态 / production)"]
    scripts_governance_oneoff_data_domain_design_state_complete_py["数据域四图设计态补全——一次性执行脚本。<br/>Step 1: 补全 6 个数据域节点的 subdomain_id<br/>（扁平分组，不建子域幻影节点）<br/>⛔ 治理脚本域，设计已就绪，等待开发排期<br/>data_domain_design_state_complete<br/>文件: oneoff<br/>/data_domain_design_state_complete.py<br/>(设计态 / design)"]
    scripts_governance_query_module_panorama_py["查询modulepanorama<br/>模块全景查询入口（四图模块对齐 Step 5）<br/>query_module_panorama<br/>文件: governance/query_module_panorama.py<br/>(生产态 / production)"]
    scripts_governance_register_deferred_modules_py["注册deferredmodules<br/>将42项暂缓模块写入 depgraph<br/>设计态，含3图对齐设计。<br/>register_deferred_modules<br/>文件: governance/register_deferred_modules.py<br/>(生产态 / production)"]
    scripts_governance_repair_concurrent_commit_test_py["并发提交测试<br/>幽灵提交红蓝对抗脚本<br/>concurrent_commit_test<br/>文件: repair/concurrent_commit_test.py<br/>(生产态 / production)"]
    scripts_governance_run_all_py["run_all.py — 脚本系统统一入口脚本<br/>治理包的run_all模块<br/>文件: governance/run_all.py<br/>(生产态 / production)"]
    scripts_governance_run_gate_chain_py["运行门禁链<br/>顺序运行多个门禁脚本，任一失败即整体失败。<br/>run_gate_chain<br/>文件: governance/run_gate_chain.py<br/>(生产态 / production)"]
    scripts_governance_run_silent_failure_regression_py["runsilent故障regression<br/>silent-failure 回归套件一键执行入口<br/>run_silent_failure_regression<br/>文件: governance<br/>/run_silent_failure_regression.py<br/>(生产态 / production)"]
    scripts_governance_session_startup_health_check_py["会话启动健康检查<br/>AI session<br/>启动时运行的核心工具健康度检查。对应裁定  Phase<br/>6<br/>session_startup_health_check<br/>文件: governance/session_startup_health_check.py<br/>(生产态 / production)"]
    scripts_governance_status_py["状态<br/>审计系统状态仪表盘<br/>status<br/>文件: governance/status.py<br/>(生产态 / production)"]
    scripts_governance_verify_sync_integrity_py["校验同步完整性<br/>sync 完整性校验脚本：验证 YAML→DB 同步的一致性。<br/>verify_sync_integrity<br/>文件: governance/verify_sync_integrity.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_blindspot_check_py["VMS 盲点闭合检查器 — MOD-INF-011 · R1(33) + R2(<br/>vms包的vms_blindspot_check模块<br/>文件: vms/vms_blindspot_check.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_build_completion_check_py["vms构建completion检查<br/>vms包的vms_build_completion_check模块<br/>文件: vms/vms_build_completion_check.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_cron_monitor_py["vmscron监控器<br/>vms包的vms_cron_monitor模块<br/>文件: vms/vms_cron_monitor.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_cross_file_check_py["VMS 跨文件内容一致性检查器 — MOD-INF-011 ·<br/>TASK-INF<br/>VMS 跨文件内容一致性检查器，校验 12 个文件中<br/>Collection 列表、嵌入维度（1024d<br/>/512d）、chunk_strategy<br/>路由、导入路径四维度一致性。<br/>vms_cross_file_check<br/>文件: vms/vms_cross_file_check.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_health_check_py["vms健康检查<br/>vms包的vms_health_check模块<br/>文件: vms/vms_health_check.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_migrate_py["VMS Phase 2 数据迁移脚本 — MOD-INF-011<br/>vms包的vms_migrate模块<br/>文件: vms/vms_migrate.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_migration_dry_run_py["vms迁移dry运行<br/>VMS 迁移 dry-run 脚本，预览 unified_memory<br/>topic 到 Collection 的映射，作为 Phase 2<br/>迁移前置检查（R15 缓解）。<br/>vms_migration_dry_run<br/>文件: vms/vms_migration_dry_run.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_phase_rollback_py["vms阶段回滚<br/>vms包的vms_phase_rollback模块<br/>文件: vms/vms_phase_rollback.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_version_sync_check_py["VMS 版本同步检查器 — MOD-INF-011 · TASK-INF-022<br/>vms包的vms_version_sync_check模块<br/>文件: vms/vms_version_sync_check.py<br/>(生产态 / production)"]
    tests_governance_scripts_governance_test_any_type_inferrer_py["测试anytypeinferrer<br/>裸 Any 检测（与 check_any_abuse.py<br/>算法一致，回归测试）<br/>test_any_type_inferrer<br/>文件: scripts_governance<br/>/test_any_type_inferrer.py<br/>(生产态 / production)"]
    tests_governance_scripts_governance_test_check_canonical_yaml_drift_py["测试check规范yaml漂移<br/>覆盖 5 项断言（A1-A5）的核心场景，每项测 clean<br/>（通过）+ stale（检出）两路：<br/>test_check_canonical_yaml_drift<br/>文件: scripts_governance<br/>/test_check_canonical_yaml_drift.py<br/>(生产态 / production)"]
    tests_governance_scripts_governance_test_check_vocab_hardcode_py["测试checkvocabhardcode<br/>GATE-VOCAB 检测7 单元测试（2026-06-30 治本补全）<br/>test_check_vocab_hardcode<br/>文件: scripts_governance<br/>/test_check_vocab_hardcode.py<br/>(生产态 / production)"]
    tests_governance_scripts_governance_test_pre_write_gate_py["测试prewrite门禁<br/>_check_session_overlap 单元测试（claim<br/>前移协议防线）<br/>test_pre_write_gate<br/>文件: scripts_governance/test_pre_write_gate.py<br/>(生产态 / production)"]
    tests_governance_test_check_blueprint_code_alignment_py["测试检查蓝图代码对齐<br/>隔离 BLUEPRINTS_DIR 和<br/>REPO_ROOT，防止扫描真实项目文件。<br/>文件: governance<br/>/test_check_blueprint_code_alignment.py<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_scripts_registry_yaml ~~~ scripts_archive_governance_dm106_p2b_verification_py
    scripts_archive_governance_dm106_p2b_verification_py ~~~ scripts_governance_archive_one_off_audit_post_sync_commands_py
    scripts_governance_archive_one_off_audit_post_sync_commands_py ~~~ scripts_governance_archive_one_off_check_exam_case_consistency_py
    scripts_governance_archive_one_off_check_exam_case_consistency_py ~~~ scripts_governance_archive_one_off_create_alignment_tasks_py
    scripts_governance_archive_one_off_create_alignment_tasks_py ~~~ scripts_governance_archive_one_off_dm105_depgraph_triage_py
    scripts_governance_archive_one_off_dm105_depgraph_triage_py ~~~ scripts_governance_archive_one_off_fix_broken_post_sync_py
    scripts_governance_archive_one_off_fix_broken_post_sync_py ~~~ scripts_governance_archive_one_off_list_phase0_tasks_py
    scripts_governance_archive_one_off_list_phase0_tasks_py ~~~ scripts_governance_archive_one_off_phase_a_backup_py
    scripts_governance_archive_one_off_phase_a_backup_py ~~~ scripts_governance_archive_one_off_rename_kebab_to_snake_py
    scripts_governance_archive_one_off_rename_kebab_to_snake_py ~~~ scripts_governance_archive_one_off_rename_whitelist_cleanup_py
    scripts_governance_archive_one_off_rename_whitelist_cleanup_py ~~~ scripts_governance_archive_one_off_test_lock_scenarios_py
    scripts_governance_archive_one_off_test_lock_scenarios_py ~~~ scripts_governance_archive_one_off_verify_final_delivery_py
    scripts_governance_archive_one_off_verify_final_delivery_py ~~~ scripts_governance_archive_one_off_verify_rule_yaml_migration_py
    scripts_governance_archive_one_off_verify_rule_yaml_migration_py ~~~ scripts_governance_archive_prototype_adversarial_log_py
    scripts_governance_archive_prototype_adversarial_log_py ~~~ scripts_governance_archive_prototype_adversarial_sys_master_test_py
    scripts_governance_archive_prototype_adversarial_sys_master_test_py ~~~ scripts_governance_archive_prototype_changelog_py
    scripts_governance_archive_prototype_changelog_py ~~~ scripts_governance_archive_prototype_check_audit_rbac_isolation_py
    scripts_governance_archive_prototype_check_audit_rbac_isolation_py ~~~ scripts_governance_archive_prototype_construction_gate_py
    scripts_governance_archive_prototype_construction_gate_py ~~~ scripts_governance_archive_prototype_generate_asset_index_py
    scripts_governance_archive_prototype_generate_asset_index_py ~~~ scripts_governance_archive_prototype_generate_nav_table_py
    scripts_governance_archive_prototype_generate_nav_table_py ~~~ scripts_governance_archive_prototype_rebuild_audit_index_py
    scripts_governance_archive_prototype_rebuild_audit_index_py ~~~ scripts_governance_archive_prototype_scan_ground_truth_deps_py
    scripts_governance_archive_prototype_scan_ground_truth_deps_py ~~~ scripts_governance_archive_prototype_session_simulator_py
    scripts_governance_archive_prototype_session_simulator_py ~~~ scripts_governance_archive_prototype_sync_blueprint_status_py
    scripts_governance_archive_prototype_sync_blueprint_status_py ~~~ scripts_governance_archive_vms_ri_ri_boundary_check_py
    scripts_governance_archive_vms_ri_ri_boundary_check_py ~~~ scripts_governance_archive_vms_ri_vms_blindspot_check_py
    scripts_governance_archive_vms_ri_vms_blindspot_check_py ~~~ scripts_governance_archive_vms_ri_vms_build_completion_check_py
    scripts_governance_archive_vms_ri_vms_build_completion_check_py ~~~ scripts_governance_archive_vms_ri_vms_cross_file_check_py
    scripts_governance_archive_vms_ri_vms_cross_file_check_py ~~~ scripts_governance_archive_vms_ri_vms_health_check_py
    scripts_governance_archive_vms_ri_vms_health_check_py ~~~ scripts_governance_archive_vms_ri_vms_migrate_py
    scripts_governance_archive_vms_ri_vms_migrate_py ~~~ scripts_governance_archive_vms_ri_vms_migration_dry_run_py
    scripts_governance_archive_vms_ri_vms_migration_dry_run_py ~~~ scripts_governance_archive_vms_ri_vms_phase_rollback_py
    scripts_governance_archive_vms_ri_vms_phase_rollback_py ~~~ scripts_governance_archive_vms_ri_vms_version_sync_check_py
    scripts_governance_archive_vms_ri_vms_version_sync_check_py ~~~ scripts_governance_shared_base_py
    scripts_governance_shared_base_py ~~~ scripts_governance_sync_cleanup_p0_auto_bridged_py
    scripts_governance_sync_cleanup_p0_auto_bridged_py ~~~ scripts_governance_sync_cleanup_p0_ops_pending_py
    scripts_governance_sync_cleanup_p0_ops_pending_py ~~~ scripts_governance_sync_fix_orphan_deps_py
    scripts_governance_sync_fix_orphan_deps_py ~~~ scripts_governance_tasks_list_phase0_tasks_py
    scripts_governance_tasks_list_phase0_tasks_py ~~~ scripts_governance_tasks_task_show_py
    scripts_governance_tasks_task_show_py ~~~ scripts_governance_tasks_task_summary_py
    scripts_governance_tasks_task_summary_py ~~~ scripts_governance_add_deferred_design_edges_py
    scripts_governance_add_deferred_design_edges_py ~~~ scripts_governance_align_battle_map_py
    scripts_governance_align_battle_map_py ~~~ scripts_governance_apply_battle_map_py
    scripts_governance_apply_battle_map_py ~~~ scripts_governance_apply_dataflowgraph_py
    scripts_governance_apply_dataflowgraph_py ~~~ scripts_governance_apply_decisiongraph_py
    scripts_governance_apply_decisiongraph_py ~~~ scripts_governance_apply_depgraph_py
    scripts_governance_apply_depgraph_py ~~~ scripts_governance_architecture_health_dashboard_py
    scripts_governance_architecture_health_dashboard_py ~~~ scripts_governance_ast_import_rewriter_py
    scripts_governance_ast_import_rewriter_py ~~~ scripts_governance_audit_return_contract_usage_py
    scripts_governance_audit_return_contract_usage_py ~~~ scripts_governance_audit_worktree_ops_telemetry_py
    scripts_governance_audit_worktree_ops_telemetry_py ~~~ scripts_governance_check_commit_message_py
    scripts_governance_check_commit_message_py ~~~ scripts_governance_check_ssot_gate_py
    scripts_governance_check_ssot_gate_py ~~~ scripts_governance_d10_performance_collect_system_threads_py
    scripts_governance_d10_performance_collect_system_threads_py ~~~ scripts_governance_d11_compliance_audit_registration_py
    scripts_governance_d11_compliance_audit_registration_py ~~~ scripts_governance_d11_compliance_ci_self_check_py
    scripts_governance_d11_compliance_ci_self_check_py ~~~ scripts_governance_d11_compliance_fix_shared_bypass_py
    scripts_governance_d11_compliance_fix_shared_bypass_py ~~~ scripts_governance_d11_compliance_g9_compliance_check_py
    scripts_governance_d11_compliance_g9_compliance_check_py ~~~ scripts_governance_d11_compliance_task_self_check_py
    scripts_governance_d11_compliance_task_self_check_py ~~~ scripts_governance_d11_compliance_validate_commit_gateway_py
    scripts_governance_d11_compliance_validate_commit_gateway_py ~~~ scripts_governance_d11_compliance_validate_commit_message_py
    scripts_governance_d11_compliance_validate_commit_message_py ~~~ scripts_governance_d11_compliance_validate_exit_codes_py
    scripts_governance_d11_compliance_validate_exit_codes_py ~~~ scripts_governance_d11_compliance_validate_frozen_requirements_py
    scripts_governance_d11_compliance_validate_frozen_requirements_py ~~~ scripts_governance_d11_compliance_validate_manifest_admission_py
    scripts_governance_d11_compliance_validate_manifest_admission_py ~~~ scripts_governance_d11_compliance_validate_no_utf8_bom_py
    scripts_governance_d11_compliance_validate_no_utf8_bom_py ~~~ scripts_governance_d11_compliance_validate_script_naming_py
    scripts_governance_d11_compliance_validate_script_naming_py ~~~ scripts_governance_d11_compliance_validate_script_quality_py
    scripts_governance_d11_compliance_validate_script_quality_py ~~~ scripts_governance_d11_compliance_validate_task_decomposition_bypass_py
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py ~~~ scripts_governance_d11_compliance_validate_vocabulary_coverage_py
    scripts_governance_d11_compliance_validate_vocabulary_coverage_py ~~~ scripts_governance_d11_compliance_verify_audit_integrity_py
    scripts_governance_d11_compliance_verify_audit_integrity_py ~~~ scripts_governance_d11_compliance_verify_schema_health_py
    scripts_governance_d11_compliance_verify_schema_health_py ~~~ scripts_governance_d12_ai_hallucination_check_logger_kwargs_py
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py ~~~ scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py ~~~ scripts_governance_d12_ai_hallucination_validate_session_budget_py
    scripts_governance_d12_ai_hallucination_validate_session_budget_py ~~~ scripts_governance_d12_ai_hallucination_validate_session_gate_check_py
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py ~~~ scripts_governance_d1_structure_archive_drafts_zone_py
    scripts_governance_d1_structure_archive_drafts_zone_py ~~~ scripts_governance_d1_structure_audit_config_format_py
    scripts_governance_d1_structure_audit_config_format_py ~~~ scripts_governance_d1_structure_audit_directory_integrity_py
    scripts_governance_d1_structure_audit_directory_integrity_py ~~~ scripts_governance_d1_structure_audit_directory_scalability_py
    scripts_governance_d1_structure_audit_directory_scalability_py ~~~ scripts_governance_d1_structure_audit_findings_by_scope_py
    scripts_governance_d1_structure_audit_findings_by_scope_py ~~~ scripts_governance_d1_structure_batch_create_index_md_py
    scripts_governance_d1_structure_batch_create_index_md_py ~~~ scripts_governance_d1_structure_cbg_reset_py
    scripts_governance_d1_structure_cbg_reset_py ~~~ scripts_governance_d1_structure_check_directory_contract_py
    scripts_governance_d1_structure_check_directory_contract_py ~~~ scripts_governance_d1_structure_check_handoff_manifests_py
    scripts_governance_d1_structure_check_handoff_manifests_py ~~~ scripts_governance_d1_structure_check_index_integrity_py
    scripts_governance_d1_structure_check_index_integrity_py ~~~ scripts_governance_d1_structure_cleanup_stash_py
    scripts_governance_d1_structure_cleanup_stash_py ~~~ scripts_governance_d1_structure_detect_orphan_py_py
    scripts_governance_d1_structure_detect_orphan_py_py ~~~ scripts_governance_d1_structure_detect_residual_files_py
    scripts_governance_d1_structure_detect_residual_files_py ~~~ scripts_governance_d1_structure_detect_temp_files_py
    scripts_governance_d1_structure_detect_temp_files_py ~~~ scripts_governance_d1_structure_drafts_zone_archiver_py
    scripts_governance_d1_structure_drafts_zone_archiver_py ~~~ scripts_governance_d1_structure_generate_missing_index_md_py
    scripts_governance_d1_structure_generate_missing_index_md_py ~~~ scripts_governance_d1_structure_reset_cbg_py
    scripts_governance_d1_structure_reset_cbg_py ~~~ scripts_governance_d1_structure_run_script_smoke_test_py
    scripts_governance_d1_structure_run_script_smoke_test_py ~~~ scripts_governance_d1_structure_sync_index_from_manifest_py
    scripts_governance_d1_structure_sync_index_from_manifest_py ~~~ scripts_governance_d1_structure_sync_policies_index_py
    scripts_governance_d1_structure_sync_policies_index_py ~~~ scripts_governance_d1_structure_validate_config_integrity_py
    scripts_governance_d1_structure_validate_config_integrity_py ~~~ scripts_governance_d1_structure_validate_d1_output_sanity_py
    scripts_governance_d1_structure_validate_d1_output_sanity_py ~~~ scripts_governance_d1_structure_validate_immutable_core_py
    scripts_governance_d1_structure_validate_immutable_core_py ~~~ scripts_governance_d1_structure_validate_index_reality_py
    scripts_governance_d1_structure_validate_index_reality_py ~~~ scripts_governance_d1_structure_validate_read_before_write_py
    scripts_governance_d1_structure_validate_read_before_write_py ~~~ scripts_governance_d2_links_audit_broken_links_py
    scripts_governance_d2_links_audit_broken_links_py ~~~ scripts_governance_d2_links_detect_relative_references_py
    scripts_governance_d2_links_detect_relative_references_py ~~~ scripts_governance_d3_metadata_auto_generate_index_py
    scripts_governance_d3_metadata_auto_generate_index_py ~~~ scripts_governance_d3_metadata_backfill_doctype_metadata_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py ~~~ scripts_governance_d3_metadata_backfill_ttl_metadata_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py ~~~ scripts_governance_d3_metadata_check_blueprint_compliance_py
    scripts_governance_d3_metadata_check_blueprint_compliance_py ~~~ scripts_governance_d3_metadata_check_frontmatter_metadata_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py ~~~ scripts_governance_d3_metadata_check_module_singlesource_py
    scripts_governance_d3_metadata_check_module_singlesource_py ~~~ scripts_governance_d3_metadata_check_naming_convention_py
    scripts_governance_d3_metadata_check_naming_convention_py ~~~ scripts_governance_d3_metadata_check_registry_consistency_py
    scripts_governance_d3_metadata_check_registry_consistency_py ~~~ scripts_governance_d3_metadata_check_schema_version_writes_py
    scripts_governance_d3_metadata_check_schema_version_writes_py ~~~ scripts_governance_d3_metadata_check_vocab_hardcode_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py ~~~ scripts_governance_d3_metadata_classify_ttl_by_content_py
    scripts_governance_d3_metadata_classify_ttl_by_content_py ~~~ scripts_governance_d3_metadata_deep_content_scanner_py
    scripts_governance_d3_metadata_deep_content_scanner_py ~~~ scripts_governance_d3_metadata_generate_derived_files_py
    scripts_governance_d3_metadata_generate_derived_files_py ~~~ scripts_governance_d3_metadata_generate_rule_catalog_py
    scripts_governance_d3_metadata_generate_rule_catalog_py ~~~ scripts_governance_d3_metadata_migrate_illegal_doctype_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py ~~~ scripts_governance_d3_metadata_validate_architecture_py
    scripts_governance_d3_metadata_validate_architecture_py ~~~ scripts_governance_d3_metadata_validate_blueprint_provenance_py
    scripts_governance_d3_metadata_validate_blueprint_provenance_py ~~~ scripts_governance_d3_metadata_validate_module_id_py
    scripts_governance_d3_metadata_validate_module_id_py ~~~ scripts_governance_d3_metadata_validate_registry_master_index_py
    scripts_governance_d3_metadata_validate_registry_master_index_py ~~~ scripts_governance_d3_metadata_validate_tool_contracts_consistency_py
    scripts_governance_d3_metadata_validate_tool_contracts_consistency_py ~~~ scripts_governance_d4_paths_detect_deprecated_path_writes_py
    scripts_governance_d4_paths_detect_deprecated_path_writes_py ~~~ scripts_governance_d4_paths_detect_excessive_file_moves_py
    scripts_governance_d4_paths_detect_excessive_file_moves_py ~~~ scripts_governance_d4_paths_detect_ruins_references_py
    scripts_governance_d4_paths_detect_ruins_references_py ~~~ scripts_governance_d4_paths_detect_split_delete_ref_commit_py
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py ~~~ scripts_governance_d5_architecture_analyze_change_impact_py
    scripts_governance_d5_architecture_analyze_change_impact_py ~~~ scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py ~~~ scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py ~~~ scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py ~~~ scripts_governance_d5_architecture_audit_agent_spec_py
    scripts_governance_d5_architecture_audit_agent_spec_py ~~~ scripts_governance_d5_architecture_check_budget_health_py
    scripts_governance_d5_architecture_check_budget_health_py ~~~ scripts_governance_d5_architecture_check_drift_e2e_py
    scripts_governance_d5_architecture_check_drift_e2e_py ~~~ scripts_governance_d5_architecture_checkers_check_architecture_gates_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py ~~~ scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py ~~~ scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py ~~~ scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py
    scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py ~~~ scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py ~~~ scripts_governance_d5_architecture_checkers_check_code_duplication_py
    scripts_governance_d5_architecture_checkers_check_code_duplication_py ~~~ scripts_governance_d5_architecture_checkers_check_contract_code_drift_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py ~~~ scripts_governance_d5_architecture_checkers_check_contract_physical_path_py
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py ~~~ scripts_governance_d5_architecture_checkers_check_dependency_direction_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py ~~~ scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py ~~~ scripts_governance_d5_architecture_checkers_check_orphan_outputs_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py ~~~ scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py ~~~ scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py ~~~ scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py ~~~ scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py ~~~ scripts_governance_d5_architecture_checkers_check_vms_ssot_py
    scripts_governance_d5_architecture_checkers_check_vms_ssot_py ~~~ scripts_governance_d5_architecture_dependency_graph_py
    scripts_governance_d5_architecture_dependency_graph_py ~~~ scripts_governance_d5_architecture_detect_causal_conflicts_py
    scripts_governance_d5_architecture_detect_causal_conflicts_py ~~~ scripts_governance_d5_architecture_detect_constraint_violations_py
    scripts_governance_d5_architecture_detect_constraint_violations_py ~~~ scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py ~~~ scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py ~~~ scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py ~~~ scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py ~~~ scripts_governance_d5_architecture_diagnose_depgraph_py
    scripts_governance_d5_architecture_diagnose_depgraph_py ~~~ scripts_governance_d5_architecture_generators_align_panoramas_py
    scripts_governance_d5_architecture_generators_align_panoramas_py ~~~ scripts_governance_d5_architecture_generators_generate_asset_catalog_py
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py ~~~ scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py
    scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py ~~~ scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py ~~~ scripts_governance_d5_architecture_generators_generate_candidate_module_report_py
    scripts_governance_d5_architecture_generators_generate_candidate_module_report_py ~~~ scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py ~~~ scripts_governance_d5_architecture_generators_generate_contract_catalog_py
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py ~~~ scripts_governance_d5_architecture_generators_generate_contracts_py
    scripts_governance_d5_architecture_generators_generate_contracts_py ~~~ scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py ~~~ scripts_governance_d5_architecture_generators_generate_data_inventory_py
    scripts_governance_d5_architecture_generators_generate_data_inventory_py ~~~ scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py ~~~ scripts_governance_d5_architecture_generators_generate_decision_diagram_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py ~~~ scripts_governance_d5_architecture_generators_generate_panorama_registry_py
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py ~~~ scripts_governance_d5_architecture_generators_generate_policies_py
    scripts_governance_d5_architecture_generators_generate_policies_py ~~~ scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py
    scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py ~~~ scripts_governance_d5_architecture_pre_delete_safety_check_py
    scripts_governance_d5_architecture_pre_delete_safety_check_py ~~~ scripts_governance_d5_architecture_pre_write_gate_py
    scripts_governance_d5_architecture_pre_write_gate_py ~~~ scripts_governance_d5_architecture_syncers_archive_rationale_log_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py ~~~ scripts_governance_d5_architecture_syncers_merge_readme_to_index_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py ~~~ scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py ~~~ scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py ~~~ scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py ~~~ scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py ~~~ scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py ~~~ scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py ~~~ scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py ~~~ scripts_governance_d5_architecture_validators_validate_arch_review_gate_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py ~~~ scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py ~~~ scripts_governance_d5_architecture_validators_validate_autonomy_gate_py
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py ~~~ scripts_governance_d5_architecture_validators_validate_b_track_packages_py
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py ~~~ scripts_governance_d5_architecture_validators_validate_blind_spot_status_py
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py ~~~ scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py ~~~ scripts_governance_d5_architecture_validators_validate_cross_references_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py ~~~ scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py ~~~ scripts_governance_d5_architecture_validators_validate_depends_on_format_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py ~~~ scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py ~~~ scripts_governance_d5_architecture_validators_validate_directory_structure_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py ~~~ scripts_governance_d5_architecture_validators_validate_field_ownership_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py ~~~ scripts_governance_d5_architecture_validators_validate_gate_yaml_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py ~~~ scripts_governance_d5_architecture_validators_validate_handoff_package_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py ~~~ scripts_governance_d5_architecture_validators_validate_interface_contracts_py
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py ~~~ scripts_governance_d5_architecture_validators_validate_load_path_integrity_py
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py ~~~ scripts_governance_d5_architecture_validators_validate_module_schema_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py ~~~ scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py ~~~ scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py ~~~ scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py ~~~ scripts_governance_d5_architecture_validators_validate_target_layer_py
    scripts_governance_d5_architecture_validators_validate_target_layer_py ~~~ scripts_governance_d5_architecture_validators_validate_three_way_consistency_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py ~~~ scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py ~~~ scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py ~~~ scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py ~~~ scripts_governance_d6_security_check_protected_paths_py
    scripts_governance_d6_security_check_protected_paths_py ~~~ scripts_governance_d6_security_detect_anchor_file_deletion_py
    scripts_governance_d6_security_detect_anchor_file_deletion_py ~~~ scripts_governance_d6_security_detect_git_dangerous_py
    scripts_governance_d6_security_detect_git_dangerous_py ~~~ scripts_governance_d6_security_detect_keywords_in_logs_py
    scripts_governance_d6_security_detect_keywords_in_logs_py ~~~ scripts_governance_d6_security_detect_permanent_file_deletion_py
    scripts_governance_d6_security_detect_permanent_file_deletion_py ~~~ scripts_governance_d6_security_detect_secrets_py
    scripts_governance_d6_security_detect_secrets_py ~~~ scripts_governance_d6_security_detect_shell_dangerous_py
    scripts_governance_d6_security_detect_shell_dangerous_py ~~~ scripts_governance_d6_security_detect_shell_true_py
    scripts_governance_d6_security_detect_shell_true_py ~~~ scripts_governance_d6_security_detect_threading_lock_py
    scripts_governance_d6_security_detect_threading_lock_py ~~~ scripts_governance_d6_security_detect_vague_terms_py
    scripts_governance_d6_security_detect_vague_terms_py ~~~ scripts_governance_d6_security_retire_tmp_artifacts_py
    scripts_governance_d6_security_retire_tmp_artifacts_py ~~~ scripts_governance_d6_security_run_adversarial_checks_py
    scripts_governance_d6_security_run_adversarial_checks_py ~~~ scripts_governance_d6_security_scan_runtime_log_secrets_py
    scripts_governance_d6_security_scan_runtime_log_secrets_py ~~~ scripts_governance_d6_security_scan_secret_leak_py
    scripts_governance_d6_security_scan_secret_leak_py ~~~ scripts_governance_d6_security_validate_gate_discipline_py
    scripts_governance_d6_security_validate_gate_discipline_py ~~~ scripts_governance_d7_code_any_type_inferrer_py
    scripts_governance_d7_code_any_type_inferrer_py ~~~ scripts_governance_d7_code_check_ai_capability_boundary_py
    scripts_governance_d7_code_check_ai_capability_boundary_py ~~~ scripts_governance_d7_code_check_encoding_py
    scripts_governance_d7_code_check_encoding_py ~~~ scripts_governance_d7_code_check_idempotency_py
    scripts_governance_d7_code_check_idempotency_py ~~~ scripts_governance_d7_code_check_merge_conflict_py
    scripts_governance_d7_code_check_merge_conflict_py ~~~ scripts_governance_d7_code_check_no_tests_unit_py
    scripts_governance_d7_code_check_no_tests_unit_py ~~~ scripts_governance_d7_code_check_pit_compliance_py
    scripts_governance_d7_code_check_pit_compliance_py ~~~ scripts_governance_d7_code_detect_absolute_path_hardcoding_py
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py ~~~ scripts_governance_d7_code_detect_direct_llm_calls_py
    scripts_governance_d7_code_detect_direct_llm_calls_py ~~~ scripts_governance_d7_code_detect_forward_reference_py
    scripts_governance_d7_code_detect_forward_reference_py ~~~ scripts_governance_d7_code_detect_missing_encoding_py
    scripts_governance_d7_code_detect_missing_encoding_py ~~~ scripts_governance_d7_code_detect_private_key_py
    scripts_governance_d7_code_detect_private_key_py ~~~ scripts_governance_d7_code_detect_pydantic_any_fields_py
    scripts_governance_d7_code_detect_pydantic_any_fields_py ~~~ scripts_governance_d7_code_detect_silent_degradation_py
    scripts_governance_d7_code_detect_silent_degradation_py ~~~ scripts_governance_d7_code_fix_n06_scope_py
    scripts_governance_d7_code_fix_n06_scope_py ~~~ scripts_governance_d7_code_fix_n12_ke_naming_py
    scripts_governance_d7_code_fix_n12_ke_naming_py ~~~ scripts_governance_d7_code_fix_n13_snake_case_py
    scripts_governance_d7_code_fix_n13_snake_case_py ~~~ scripts_governance_d7_code_fix_n14_init_all_py
    scripts_governance_d7_code_fix_n14_init_all_py ~~~ scripts_governance_d7_code_fix_n15_blueprint_path_py
    scripts_governance_d7_code_fix_n15_blueprint_path_py ~~~ scripts_governance_d7_code_fix_naming_manual_py
    scripts_governance_d7_code_fix_naming_manual_py ~~~ scripts_governance_d7_code_fix_orphan_exports_py
    scripts_governance_d7_code_fix_orphan_exports_py ~~~ scripts_governance_d7_code_rewrite_imports_py
    scripts_governance_d7_code_rewrite_imports_py ~~~ scripts_governance_d7_code_scan_complexity_py
    scripts_governance_d7_code_scan_complexity_py ~~~ scripts_governance_d7_code_scan_consumers_accuracy_py
    scripts_governance_d7_code_scan_consumers_accuracy_py ~~~ scripts_governance_d7_code_scan_debt_py
    scripts_governance_d7_code_scan_debt_py ~~~ scripts_governance_d7_code_validate_contracts_purity_py
    scripts_governance_d7_code_validate_contracts_purity_py ~~~ scripts_governance_d7_code_validate_docstring_coverage_py
    scripts_governance_d7_code_validate_docstring_coverage_py ~~~ scripts_governance_d7_code_validate_fle_action_metadata_py
    scripts_governance_d7_code_validate_fle_action_metadata_py ~~~ scripts_governance_d7_code_validate_fle_imports_py
    scripts_governance_d7_code_validate_fle_imports_py ~~~ scripts_governance_d7_code_validate_import_style_py
    scripts_governance_d7_code_validate_import_style_py ~~~ scripts_governance_d7_code_validate_init_all_py
    scripts_governance_d7_code_validate_init_all_py ~~~ scripts_governance_d7_code_validate_kb_write_provenance_py
    scripts_governance_d7_code_validate_kb_write_provenance_py ~~~ scripts_governance_d7_code_validate_python_syntax_py
    scripts_governance_d7_code_validate_python_syntax_py ~~~ scripts_governance_d7_code_validate_test_assertion_depth_py
    scripts_governance_d7_code_validate_test_assertion_depth_py ~~~ scripts_governance_d7_code_validate_test_coverage_py
    scripts_governance_d7_code_validate_test_coverage_py ~~~ scripts_governance_d7_code_validate_type_annotation_coverage_py
    scripts_governance_d7_code_validate_type_annotation_coverage_py ~~~ scripts_governance_d7_code_validate_unused_imports_py
    scripts_governance_d7_code_validate_unused_imports_py ~~~ scripts_governance_d8_doc_sync_auto_sync_all_registries_py
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py ~~~ scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py ~~~ scripts_governance_d8_doc_sync_detect_dated_snapshots_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py ~~~ scripts_governance_d8_doc_sync_sync_rule_registry_py
    scripts_governance_d8_doc_sync_sync_rule_registry_py ~~~ scripts_governance_d8_doc_sync_update_progress_py
    scripts_governance_d8_doc_sync_update_progress_py ~~~ scripts_governance_d8_doc_sync_validate_document_lifecycle_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py ~~~ scripts_governance_d8_doc_sync_validate_document_ttl_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py ~~~ scripts_governance_d9_knowledge_detect_duplicated_normative_language_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py ~~~ scripts_governance_d9_knowledge_detect_orphan_documents_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py ~~~ scripts_governance_data_quality_check_tick_duplication_py
    scripts_governance_data_quality_check_tick_duplication_py ~~~ scripts_governance_extract_decisiongraph_py
    scripts_governance_extract_decisiongraph_py ~~~ scripts_governance_extract_depgraph_py
    scripts_governance_extract_depgraph_py ~~~ scripts_governance_generate_decision_graph_py
    scripts_governance_generate_decision_graph_py ~~~ scripts_governance_generate_project_depgraph_py
    scripts_governance_generate_project_depgraph_py ~~~ scripts_governance_generate_project_path_tree_py
    scripts_governance_generate_project_path_tree_py ~~~ scripts_governance_generators_check_gate_inventory_drift_py
    scripts_governance_generators_check_gate_inventory_drift_py ~~~ scripts_governance_generators_fix_module_manifest_layout_py
    scripts_governance_generators_fix_module_manifest_layout_py ~~~ scripts_governance_generators_generate_gate_registry_py
    scripts_governance_generators_generate_gate_registry_py ~~~ scripts_governance_generators_generate_importlinter_py
    scripts_governance_generators_generate_importlinter_py ~~~ scripts_governance_generators_generate_path_ownership_map_py
    scripts_governance_generators_generate_path_ownership_map_py ~~~ scripts_governance_generators_generate_registry_master_index_py
    scripts_governance_generators_generate_registry_master_index_py ~~~ scripts_governance_generators_inject_manifests_py
    scripts_governance_generators_inject_manifests_py ~~~ scripts_governance_generators_refresh_master_entries_py
    scripts_governance_generators_refresh_master_entries_py ~~~ scripts_governance_generators_sync_audit_protocol_numbers_py
    scripts_governance_generators_sync_audit_protocol_numbers_py ~~~ scripts_governance_git_health_smoke_py
    scripts_governance_git_health_smoke_py ~~~ scripts_governance_harvest_candidates_from_drafts_py
    scripts_governance_harvest_candidates_from_drafts_py ~~~ scripts_governance_meta_arbitrate_findings_py
    scripts_governance_meta_arbitrate_findings_py ~~~ scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py
    scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py ~~~ scripts_governance_meta_compute_sla_metrics_py
    scripts_governance_meta_compute_sla_metrics_py ~~~ scripts_governance_meta_create_task_from_finding_py
    scripts_governance_meta_create_task_from_finding_py ~~~ scripts_governance_meta_detect_config_deviation_py
    scripts_governance_meta_detect_config_deviation_py ~~~ scripts_governance_meta_detect_fix_oscillation_py
    scripts_governance_meta_detect_fix_oscillation_py ~~~ scripts_governance_meta_detect_hallucinated_packages_py
    scripts_governance_meta_detect_hallucinated_packages_py ~~~ scripts_governance_meta_detect_script_divergence_py
    scripts_governance_meta_detect_script_divergence_py ~~~ scripts_governance_meta_detect_script_rot_py
    scripts_governance_meta_detect_script_rot_py ~~~ scripts_governance_meta_env_check_py
    scripts_governance_meta_env_check_py ~~~ scripts_governance_meta_finding_state_machine_py
    scripts_governance_meta_finding_state_machine_py ~~~ scripts_governance_meta_gate_engine_selfcheck_py
    scripts_governance_meta_gate_engine_selfcheck_py ~~~ scripts_governance_meta_governance_watchdog_py
    scripts_governance_meta_governance_watchdog_py ~~~ scripts_governance_meta_manage_error_budget_py
    scripts_governance_meta_manage_error_budget_py ~~~ scripts_governance_meta_manage_finding_timeseries_py
    scripts_governance_meta_manage_finding_timeseries_py ~~~ scripts_governance_meta_manage_script_ab_test_py
    scripts_governance_meta_manage_script_ab_test_py ~~~ scripts_governance_meta_manage_script_retirement_py
    scripts_governance_meta_manage_script_retirement_py ~~~ scripts_governance_meta_manage_shadow_mode_py
    scripts_governance_meta_manage_shadow_mode_py ~~~ scripts_governance_meta_mutation_test_post_sync_validator_py
    scripts_governance_meta_mutation_test_post_sync_validator_py ~~~ scripts_governance_meta_mutation_test_reconciliation_registry_py
    scripts_governance_meta_mutation_test_reconciliation_registry_py ~~~ scripts_governance_meta_phase_e_context_check_py
    scripts_governance_meta_phase_e_context_check_py ~~~ scripts_governance_meta_pre_op_check_py
    scripts_governance_meta_pre_op_check_py ~~~ scripts_governance_meta_score_script_effectiveness_py
    scripts_governance_meta_score_script_effectiveness_py ~~~ scripts_governance_meta_session_startup_check_py
    scripts_governance_meta_session_startup_check_py ~~~ scripts_governance_meta_trace_finding_lifecycle_py
    scripts_governance_meta_trace_finding_lifecycle_py ~~~ scripts_governance_meta_track_script_costs_py
    scripts_governance_meta_track_script_costs_py ~~~ scripts_governance_meta_validate_automation_boundary_py
    scripts_governance_meta_validate_automation_boundary_py ~~~ scripts_governance_meta_validate_cross_model_consensus_py
    scripts_governance_meta_validate_cross_model_consensus_py ~~~ scripts_governance_meta_validate_dependency_chain_py
    scripts_governance_meta_validate_dependency_chain_py ~~~ scripts_governance_meta_validate_emergency_bypass_log_py
    scripts_governance_meta_validate_emergency_bypass_log_py ~~~ scripts_governance_meta_validate_end_to_end_benchmark_py
    scripts_governance_meta_validate_end_to_end_benchmark_py ~~~ scripts_governance_meta_validate_environment_health_py
    scripts_governance_meta_validate_environment_health_py ~~~ scripts_governance_meta_validate_false_negatives_py
    scripts_governance_meta_validate_false_negatives_py ~~~ scripts_governance_meta_validate_gate_engine_external_py
    scripts_governance_meta_validate_gate_engine_external_py ~~~ scripts_governance_meta_validate_mutation_testing_py
    scripts_governance_meta_validate_mutation_testing_py ~~~ scripts_governance_meta_validate_rule_freshness_py
    scripts_governance_meta_validate_rule_freshness_py ~~~ scripts_governance_meta_validate_rules_file_backdoor_py
    scripts_governance_meta_validate_rules_file_backdoor_py ~~~ scripts_governance_meta_validate_rules_integrity_py
    scripts_governance_meta_validate_rules_integrity_py ~~~ scripts_governance_meta_validate_script_onboarding_py
    scripts_governance_meta_validate_script_onboarding_py ~~~ scripts_governance_meta_validate_script_provenance_py
    scripts_governance_meta_validate_script_provenance_py ~~~ scripts_governance_meta_validate_script_system_health_py
    scripts_governance_meta_validate_script_system_health_py ~~~ scripts_governance_meta_validate_threshold_changes_py
    scripts_governance_meta_validate_threshold_changes_py ~~~ scripts_governance_meta_validate_trust_tier_py
    scripts_governance_meta_validate_trust_tier_py ~~~ scripts_governance_meta_verify_reconciliation_registry_py
    scripts_governance_meta_verify_reconciliation_registry_py ~~~ scripts_governance_migrate_sqlite_to_pg_migrate_data_py
    scripts_governance_migrate_sqlite_to_pg_migrate_data_py ~~~ scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py ~~~ scripts_governance_migrate_to_metadata_tables_py
    scripts_governance_migrate_to_metadata_tables_py ~~~ scripts_governance_oneoff_data_domain_audit_query_py
    scripts_governance_oneoff_data_domain_audit_query_py ~~~ scripts_governance_oneoff_data_domain_design_state_complete_py
    scripts_governance_oneoff_data_domain_design_state_complete_py ~~~ scripts_governance_query_module_panorama_py
    scripts_governance_query_module_panorama_py ~~~ scripts_governance_register_deferred_modules_py
    scripts_governance_register_deferred_modules_py ~~~ scripts_governance_repair_concurrent_commit_test_py
    scripts_governance_repair_concurrent_commit_test_py ~~~ scripts_governance_run_all_py
    scripts_governance_run_all_py ~~~ scripts_governance_run_gate_chain_py
    scripts_governance_run_gate_chain_py ~~~ scripts_governance_run_silent_failure_regression_py
    scripts_governance_run_silent_failure_regression_py ~~~ scripts_governance_session_startup_health_check_py
    scripts_governance_session_startup_health_check_py ~~~ scripts_governance_status_py
    scripts_governance_status_py ~~~ scripts_governance_verify_sync_integrity_py
    scripts_governance_verify_sync_integrity_py ~~~ scripts_governance_vms_vms_blindspot_check_py
    scripts_governance_vms_vms_blindspot_check_py ~~~ scripts_governance_vms_vms_build_completion_check_py
    scripts_governance_vms_vms_build_completion_check_py ~~~ scripts_governance_vms_vms_cron_monitor_py
    scripts_governance_vms_vms_cron_monitor_py ~~~ scripts_governance_vms_vms_cross_file_check_py
    scripts_governance_vms_vms_cross_file_check_py ~~~ scripts_governance_vms_vms_health_check_py
    scripts_governance_vms_vms_health_check_py ~~~ scripts_governance_vms_vms_migrate_py
    scripts_governance_vms_vms_migrate_py ~~~ scripts_governance_vms_vms_migration_dry_run_py
    scripts_governance_vms_vms_migration_dry_run_py ~~~ scripts_governance_vms_vms_phase_rollback_py
    scripts_governance_vms_vms_phase_rollback_py ~~~ scripts_governance_vms_vms_version_sync_check_py
    scripts_governance_vms_vms_version_sync_check_py ~~~ tests_governance_scripts_governance_test_any_type_inferrer_py
    tests_governance_scripts_governance_test_any_type_inferrer_py ~~~ tests_governance_scripts_governance_test_check_canonical_yaml_drift_py
    tests_governance_scripts_governance_test_check_canonical_yaml_drift_py ~~~ tests_governance_scripts_governance_test_check_vocab_hardcode_py
    tests_governance_scripts_governance_test_check_vocab_hardcode_py ~~~ tests_governance_scripts_governance_test_pre_write_gate_py
    tests_governance_scripts_governance_test_pre_write_gate_py ~~~ tests_governance_test_check_blueprint_code_alignment_py
    scripts_governance_archive_prototype_audit_domain_nodes_py["审计域节点<br/>P0-4升级：4类检测<br/>（跨域违规+容量超限+孤儿节点+层级违规）<br/>文件: prototype/audit_domain_nodes.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_ri_build_completion_check_py["ri构建completion检查<br/>蓝图 §7 · v5.0.1 · 验证 15 RI 模块 +<br/>Cross-Layer 依赖完整性<br/>ri_build_completion_check<br/>文件: vms_ri/ri_build_completion_check.py<br/>(生产态 / production)"]
    scripts_governance_shared_frontmatter_py["文件头部格式解析 SSoT（Single Source of Truth）<br/>6 种文件头部格式的统一解析入口（对标 trae_047<br/>GOV-ENG-002）：<br/>frontmatter<br/>文件: _shared/frontmatter.py<br/>(生产态 / production)"]
    scripts_governance_shared_libcst_docstring_adder_py["LibCSTdocstring添加器<br/>提供leaveModule等方法<br/>文件: _shared/libcst_docstring_adder.py<br/>(生产态 / production)"]
    scripts_governance_shared_module_translation_loader_py["moduletranslation加载器<br/>模块级翻译共享加载器（SSoT 真源）<br/>module_translation_loader<br/>文件: _shared/module_translation_loader.py<br/>(生产态 / production)"]
    scripts_governance_shared_registry_entry_count_py["注册表条目数量<br/>登记表主条目计数——与<br/>generate_registry_master_index 单一真源对齐。<br/>registry_entry_count<br/>文件: _shared/registry_entry_count.py<br/>(生产态 / production)"]
    scripts_governance_shared_terminology_loader_py["术语加载器<br/>架构文档术语词汇表共享加载器（SSoT 真源）<br/>terminology_loader<br/>文件: _shared/terminology_loader.py<br/>(生产态 / production)"]
    scripts_governance_shared_yaml_utils_py["yaml工具<br/>YAML 文件加载共享工具<br/>yaml_utils<br/>文件: _shared/yaml_utils.py<br/>(生产态 / production)"]
    scripts_governance_sync_check_p0_status_py["检查p0状态<br/>P0 优先级任务状态检查器，扫描任务仓库统计 P0<br/>级任务的待办与完成情况，为治理同步提供 P0<br/>状态快照。<br/>文件: _sync/check_p0_status.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_module_id_naming_py["校验模块idnaming<br/>module_id / domain_id / submodule_id<br/>格式校验真源（裁定#208 双轨制 + R2 治本修订）<br/>validate_module_id_naming<br/>文件: d3_metadata/validate_module_id_naming.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_common_py["生成器公共工具（向内收：消除重复）。<br/>当前提供 cleanup_stale_files<br/>()——治本修复'生成器只增不删'问题。<br/>_common<br/>文件: generators/_common.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_any_abuse_py["类型注解 Any 滥用扫描器 — 5.145 维度防御门闸<br/>（R70 引入，#AR<br/>CH-ANY-GOVERNANCE-001 Phase 3 升级为 commit<br/>阻断）<br/>check_any_abuse<br/>文件: d7_code/check_any_abuse.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_audit_rename_completeness_py["审计renamecompleteness<br/>改名完整性审计（裁定#207 R1）。<br/>audit_rename_completeness<br/>文件: d8_doc_sync/audit_rename_completeness.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py["同步yamlto依赖图<br/>(INVARIANTS) YAML→DB单向同步; 27项同步; try<br/>/finally恢复触发器<br/>sync_yaml_to_depgraph<br/>文件: d8_doc_sync/sync_yaml_to_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_meta_concurrency_py["并发<br/>L0 全局进程锁——基于 PID 文件的跨进程互斥锁。<br/>文件: meta/_concurrency.py<br/>(生产态 / production)"]
    scripts_governance_meta_backup_runtime_state_py["备份运行时状态<br/>运行时状态备份（蓝图 §33 灾备）<br/>backup_runtime_state<br/>文件: meta/backup_runtime_state.py<br/>(生产态 / production)"]
    scripts_governance_meta_benchmark_test_fixtures_bad_imports_py["无效导入<br/>（bad_imports.py）<br/>文件: test_fixtures/bad_imports.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_baseline_py["管理基线<br/>保存/加载/对比 Finding<br/>基线快照，将当前扫描结果与上次 approved<br/>baseline 对比，<br/>manage_baseline<br/>文件: meta/manage_baseline.py<br/>(生产态 / production)"]
    scripts_governance_sync_panorama_module_py["同步panorama模块<br/>四图模块同步引擎<br/>sync_panorama_module<br/>文件: governance/sync_panorama_module.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_audit_domain_nodes_py ~~~ scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_ri_build_completion_check_py ~~~ scripts_governance_shared_frontmatter_py
    scripts_governance_shared_frontmatter_py ~~~ scripts_governance_shared_libcst_docstring_adder_py
    scripts_governance_shared_libcst_docstring_adder_py ~~~ scripts_governance_shared_module_translation_loader_py
    scripts_governance_shared_module_translation_loader_py ~~~ scripts_governance_shared_registry_entry_count_py
    scripts_governance_shared_registry_entry_count_py ~~~ scripts_governance_shared_terminology_loader_py
    scripts_governance_shared_terminology_loader_py ~~~ scripts_governance_shared_yaml_utils_py
    scripts_governance_shared_yaml_utils_py ~~~ scripts_governance_sync_check_p0_status_py
    scripts_governance_sync_check_p0_status_py ~~~ scripts_governance_d3_metadata_validate_module_id_naming_py
    scripts_governance_d3_metadata_validate_module_id_naming_py ~~~ scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_common_py ~~~ scripts_governance_d7_code_check_any_abuse_py
    scripts_governance_d7_code_check_any_abuse_py ~~~ scripts_governance_d8_doc_sync_audit_rename_completeness_py
    scripts_governance_d8_doc_sync_audit_rename_completeness_py ~~~ scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py
    scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py ~~~ scripts_governance_meta_concurrency_py
    scripts_governance_meta_concurrency_py ~~~ scripts_governance_meta_backup_runtime_state_py
    scripts_governance_meta_backup_runtime_state_py ~~~ scripts_governance_meta_benchmark_test_fixtures_bad_imports_py
    scripts_governance_meta_benchmark_test_fixtures_bad_imports_py ~~~ scripts_governance_meta_manage_baseline_py
    scripts_governance_meta_manage_baseline_py ~~~ scripts_governance_sync_panorama_module_py
    scripts_governance_archive_vms_ri_vms_cron_monitor_py["vmscron监控器<br/>vms ri包的vms_cron_monitor模块<br/>文件: vms_ri/vms_cron_monitor.py<br/>(生产态 / production)"]
    scripts_governance_shared_encoding_py["encoding.py — UTF-8 编码安全工具<br/>UTF-8 编码安全工具，统一文件读写编码标准，防止<br/>Windows 下 GBK 与 UTF-8 混用导致中文乱码。<br/>文件: _shared/encoding.py<br/>(生产态 / production)"]
    scripts_governance_shared_file_utils_py["文件工具<br/>原子写入共享工具<br/>file_utils<br/>文件: _shared/file_utils.py<br/>(生产态 / production)"]
    scripts_governance_shared_thresholds_py["thresholds.py — 阈值集中配置加载器<br/>shared包的thresholds模块<br/>文件: _shared/thresholds.py<br/>(生产态 / production)"]
    scripts_governance_shared_walk_py["walk.py — 目录遍历共享工具<br/>shared包的walk模块<br/>文件: _shared/walk.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py["蓝图frontmatter对账器<br/>蓝图 frontmatter 核心字段对齐（ARCH-056 Phase<br/>3）<br/>blueprint_frontmatter_reconciler<br/>文件: syncers<br/>/blueprint_frontmatter_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py["incomplete模块<br/>Benchmark<br/>测试夹具——故意不完整的模块，用于测试检测器能否识<br/>别不合规模块。<br/>文件: test_fixtures/incomplete_module.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_cron_monitor_py ~~~ scripts_governance_shared_encoding_py
    scripts_governance_shared_encoding_py ~~~ scripts_governance_shared_file_utils_py
    scripts_governance_shared_file_utils_py ~~~ scripts_governance_shared_thresholds_py
    scripts_governance_shared_thresholds_py ~~~ scripts_governance_shared_walk_py
    scripts_governance_shared_walk_py ~~~ scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py ~~~ scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py
    scripts_governance_shared_constants_py["常量<br/>审计脚本共享常量<br/>constants<br/>文件: _shared/constants.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_panorama_common_py["panorama通用<br/>四图投票共享工具（ARCH-056 引擎加固）<br/>panorama_common<br/>文件: d5_architecture/panorama_common.py<br/>(生产态 / production)"]
    scripts_governance_shared_constants_py ~~~ scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_apply_battle_map_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_align_battle_map_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_align_battle_map_py -->|导入依赖 / import_depends| scripts_governance_shared_module_translation_loader_py
    scripts_governance_apply_dataflowgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_sync_panorama_module_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_d3_metadata_validate_module_id_naming_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_d8_doc_sync_audit_rename_completeness_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_meta_backup_runtime_state_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_apply_decisiongraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_check_commit_message_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_extract_decisiongraph_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_ast_import_rewriter_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_decision_graph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_decision_graph_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generate_project_depgraph_py -->|导入依赖 / import_depends| scripts_governance_sync_panorama_module_py
    scripts_governance_generate_project_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_project_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_check_ssot_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_project_path_tree_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_extract_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_extract_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_query_module_panorama_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_migrate_to_metadata_tables_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_run_gate_chain_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_status_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_status_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_meta_concurrency_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_sync_panorama_module_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_sync_panorama_module_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py
    scripts_governance_sync_panorama_module_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_verify_sync_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_audit_registration_py -->|导入依赖 / import_depends| scripts_governance_meta_manage_baseline_py
    scripts_governance_d11_compliance_audit_registration_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d11_compliance_audit_registration_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d10_performance_collect_system_threads_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_ci_self_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_fix_shared_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_fix_shared_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_g9_compliance_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_task_self_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_frozen_requirements_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_frozen_requirements_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_exit_codes_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_exit_codes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_commit_gateway_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_manifest_admission_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_commit_message_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_commit_message_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_libcst_docstring_adder_py
    scripts_governance_d11_compliance_verify_audit_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_no_utf8_bom_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_no_utf8_bom_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_script_naming_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_script_naming_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_archive_drafts_zone_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_archive_drafts_zone_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_validate_session_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_validate_session_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_verify_schema_health_py -->|导入依赖 / import_depends| scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py
    scripts_governance_d11_compliance_verify_schema_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_config_format_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_config_format_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_config_format_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_audit_directory_scalability_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_directory_scalability_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_directory_scalability_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d1_structure_batch_create_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_cbg_reset_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_cbg_reset_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_findings_by_scope_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_findings_by_scope_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_directory_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_directory_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_directory_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_cleanup_stash_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_check_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_check_directory_contract_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_directory_contract_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_check_directory_contract_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_detect_temp_files_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_detect_temp_files_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_temp_files_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_detect_orphan_py_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_detect_orphan_py_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_handoff_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_residual_files_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_detect_residual_files_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_residual_files_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_drafts_zone_archiver_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_drafts_zone_archiver_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_drafts_zone_archiver_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_sync_policies_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_sync_policies_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_sync_policies_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_sync_index_from_manifest_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_sync_index_from_manifest_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_sync_index_from_manifest_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_reset_cbg_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_reset_cbg_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d1_structure_run_script_smoke_test_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_run_script_smoke_test_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d1_structure_validate_d1_output_sanity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_d1_output_sanity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_index_reality_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_read_before_write_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_read_before_write_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_auto_generate_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d3_metadata_auto_generate_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_auto_generate_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d2_links_audit_broken_links_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d2_links_detect_relative_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d2_links_detect_relative_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d2_links_detect_relative_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_check_blueprint_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_check_module_singlesource_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_check_naming_convention_py -->|导入依赖 / import_depends| scripts_governance_d3_metadata_validate_module_id_naming_py
    scripts_governance_d3_metadata_check_naming_convention_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_schema_version_writes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_validate_blueprint_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_blueprint_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_classify_ttl_by_content_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_classify_ttl_by_content_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_generate_derived_files_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_generate_derived_files_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_generate_derived_files_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_validate_architecture_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_architecture_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_architecture_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_validate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_registry_entry_count_py
    scripts_governance_d3_metadata_validate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_validate_module_id_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_module_id_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_module_id_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d4_paths_detect_deprecated_path_writes_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_deprecated_path_writes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_tool_contracts_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_excessive_file_moves_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_excessive_file_moves_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_audit_agent_spec_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_check_drift_e2e_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyze_change_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_analyze_change_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_ruins_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_ruins_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_ruins_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_dependency_graph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_check_budget_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detect_causal_conflicts_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_detect_causal_conflicts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detect_constraint_violations_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_diagnose_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_diagnose_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_pre_write_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_pre_delete_safety_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_code_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_code_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_vms_ssot_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_generators_align_panoramas_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_d5_architecture_generators_align_panoramas_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_align_panoramas_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_module_translation_loader_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_candidate_module_report_py -->|导入依赖 / import_depends| scripts_governance_shared_module_translation_loader_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_generators_generate_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_generators_generate_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_generators_generate_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_policies_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_target_layer_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_target_layer_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d6_security_detect_anchor_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_anchor_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_check_protected_paths_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_check_protected_paths_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_git_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_git_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_git_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d6_security_detect_keywords_in_logs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_keywords_in_logs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_keywords_in_logs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_permanent_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_permanent_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_secrets_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_shell_true_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_shell_true_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_shell_true_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_shell_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_shell_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_shell_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_retire_tmp_artifacts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_retire_tmp_artifacts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_run_adversarial_checks_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_scan_runtime_log_secrets_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_scan_runtime_log_secrets_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_validate_gate_discipline_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_validate_gate_discipline_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_validate_gate_discipline_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_threading_lock_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_threading_lock_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_threading_lock_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_any_type_inferrer_py -->|导入依赖 / import_depends| scripts_governance_d7_code_check_any_abuse_py
    scripts_governance_d7_code_any_type_inferrer_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_vague_terms_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_vague_terms_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_vague_terms_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_check_ai_capability_boundary_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_ai_capability_boundary_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_merge_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_no_tests_unit_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_idempotency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_idempotency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_pit_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_pit_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_direct_llm_calls_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_direct_llm_calls_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_direct_llm_calls_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_detect_missing_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_missing_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_missing_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_detect_pydantic_any_fields_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_pydantic_any_fields_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_pydantic_any_fields_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_detect_forward_reference_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_private_key_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n06_scope_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n12_ke_naming_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_silent_degradation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_silent_degradation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_silent_degradation_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_fix_n13_snake_case_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n14_init_all_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_orphan_exports_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d7_code_fix_orphan_exports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_naming_manual_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_rewrite_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d7_code_rewrite_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_scan_consumers_accuracy_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n15_blueprint_path_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_scan_debt_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_import_style_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_import_style_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_fle_action_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_fle_action_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_fle_action_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_fle_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_fle_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_fle_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_scan_complexity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_docstring_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_docstring_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_contracts_purity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_contracts_purity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_contracts_purity_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_kb_write_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_kb_write_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_kb_write_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_init_all_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_init_all_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_type_annotation_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_type_annotation_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_unused_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_unused_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_python_syntax_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_python_syntax_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_test_assertion_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_test_assertion_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_test_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_test_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_audit_rename_completeness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_sync_rule_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_sync_rule_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_update_progress_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_data_quality_check_tick_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_data_quality_check_tick_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_check_gate_inventory_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_generators_fix_module_manifest_layout_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_fix_module_manifest_layout_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_fix_module_manifest_layout_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_registry_entry_count_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generators_generate_importlinter_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_importlinter_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_generate_importlinter_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generators_generate_path_ownership_map_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_path_ownership_map_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_sync_audit_protocol_numbers_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_sync_audit_protocol_numbers_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_registry_entry_count_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_fix_oscillation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_detect_fix_oscillation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_arbitrate_findings_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_compute_sla_metrics_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_compute_sla_metrics_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_compute_sla_metrics_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_backup_runtime_state_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_backup_runtime_state_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_create_task_from_finding_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_create_task_from_finding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_create_task_from_finding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_config_deviation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_detect_config_deviation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_script_rot_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_env_check_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_env_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_finding_state_machine_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_finding_state_machine_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_finding_state_machine_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_detect_hallucinated_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_detect_hallucinated_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_gate_engine_selfcheck_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_gate_engine_selfcheck_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_meta_detect_script_divergence_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_detect_script_divergence_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_baseline_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_baseline_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_governance_watchdog_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_governance_watchdog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_governance_watchdog_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_manage_error_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_error_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_error_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_manage_script_retirement_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_script_retirement_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_finding_timeseries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_mutation_test_reconciliation_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_script_ab_test_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_script_ab_test_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_pre_op_check_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_pre_op_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_mutation_test_post_sync_validator_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_trace_finding_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_shadow_mode_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_shadow_mode_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_score_script_effectiveness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_score_script_effectiveness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_session_startup_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_track_script_costs_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_track_script_costs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_automation_boundary_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_cross_model_consensus_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_emergency_bypass_log_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_emergency_bypass_log_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_dependency_chain_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_dependency_chain_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_false_negatives_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_false_negatives_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_rule_freshness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_rule_freshness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_rules_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_rules_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_meta_validate_end_to_end_benchmark_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_end_to_end_benchmark_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_mutation_testing_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_mutation_testing_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_environment_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_rules_file_backdoor_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_script_system_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_script_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_script_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_script_onboarding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_threshold_changes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_benchmark_test_fixtures_bad_imports_py -->|config_depends / config_depends| scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py
    scripts_governance_meta_validate_trust_tier_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_verify_reconciliation_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_concurrency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_concurrency_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py -->|导入依赖 / import_depends| scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py -->|config_depends / config_depends| scripts_governance_meta_benchmark_test_fixtures_bad_imports_py
    scripts_governance_migrate_sqlite_to_pg_migrate_data_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_vms_vms_version_sync_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_audit_post_sync_commands_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_check_exam_case_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_list_phase0_tasks_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_dm105_depgraph_triage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_fix_broken_post_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_phase_a_backup_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_rename_kebab_to_snake_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_test_lock_scenarios_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_audit_domain_nodes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_rename_whitelist_cleanup_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_verify_final_delivery_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_adversarial_log_py -->|config_depends / config_depends| scripts_governance_archive_prototype_audit_domain_nodes_py
    scripts_governance_archive_one_off_verify_rule_yaml_migration_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_check_audit_rbac_isolation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_changelog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_adversarial_sys_master_test_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_construction_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_generate_asset_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_rebuild_audit_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_generate_nav_table_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_archive_prototype_generate_nav_table_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_generate_nav_table_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_archive_vms_ri_ri_build_completion_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_vms_cron_monitor_py
    scripts_governance_archive_prototype_session_simulator_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_archive_prototype_session_simulator_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_scan_ground_truth_deps_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_vms_ri_vms_blindspot_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_ri_boundary_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_prototype_sync_blueprint_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_vms_ri_vms_cross_file_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_vms_build_completion_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_shared_base_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_shared_base_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_base_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_archive_vms_ri_vms_phase_rollback_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_vms_version_sync_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_file_utils_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_terminology_loader_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_walk_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_module_translation_loader_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_libcst_docstring_adder_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_shared_libcst_docstring_adder_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_libcst_docstring_adder_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_sync_check_p0_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_yaml_utils_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_sync_cleanup_p0_auto_bridged_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_sync_fix_orphan_deps_py -->|config_depends / config_depends| scripts_governance_sync_check_p0_status_py
    scripts_governance_sync_cleanup_p0_ops_pending_py -->|config_depends / config_depends| scripts_governance_sync_check_p0_status_py
    scripts_governance_tasks_task_show_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_tasks_task_summary_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_tasks_list_phase0_tasks_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_archive_governance_dm106_p2b_verification_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    tests_governance_scripts_governance_test_check_vocab_hardcode_py -->|测试依赖 / test_depends| scripts_governance_shared_constants_py
    tests_governance_scripts_governance_test_check_vocab_hardcode_py -->|测试依赖 / test_depends| scripts_governance_shared_yaml_utils_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_module_singlesource_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_schema_version_writes_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_DATA["数据接入层<br/>数据接入层，负责数据源接入、数据集成和数据标准化<br/>Data Access Layer<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| D_DATA
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| D_DATA
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_apply_battle_map_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_align_battle_map_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_align_battle_map_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_align_battle_map_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_align_battle_map_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_add_deferred_design_edges_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_apply_dataflowgraph_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["规则执行<br/>规则执行，负责治理规则执行和门禁拦截<br/>Rule Enforcement<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| scripts_governance_architecture_health_dashboard_py
    D_GOVERNANCE -->|导入依赖 / import_depends| scripts_governance_d3_metadata_check_naming_convention_py
    D_GOV_AUDIT["审计追踪<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>Audit Trail<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_AUDIT -->|导入依赖 / import_depends| scripts_governance_d3_metadata_validate_module_id_naming_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| scripts_governance_generators_check_gate_inventory_drift_py
    D_GOVERNANCE -->|测试依赖 / test_depends| scripts_governance_generators_generate_gate_registry_py
    D_AUTONOMY_PERM["自治保护<br/>自治保护，负责 AI 自治行为的权限控制和安全边界<br/>Autonomy Protection<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_AUTONOMY_PERM -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    D_GOV_RULE["规则治理<br/>规则治理，负责规则注册、规则版本和规则依赖管理<br/>Rule Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_RULE -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    D_OPS["反馈循环<br/>反馈循环，负责系统运行反馈、性能监控和自动调优闭<br/>环<br/>Feedback Loop<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_OPS -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    D_GOVERNANCE -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    D_GOVERNANCE -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    D_GOV_DRIFT["漂移检测<br/>漂移检测，负责架构漂移检测和漂移告警<br/>Drift Detection<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_DRIFT -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    D_GOV_RULE -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    D_GOVERNANCE -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_scripts_registry_yaml,scripts_archive_governance_dm106_p2b_verification_py,scripts_governance_archive_one_off_audit_post_sync_commands_py,scripts_governance_archive_one_off_check_exam_case_consistency_py,scripts_governance_archive_one_off_create_alignment_tasks_py,scripts_governance_archive_one_off_dm105_depgraph_triage_py,scripts_governance_archive_one_off_fix_broken_post_sync_py,scripts_governance_archive_one_off_list_phase0_tasks_py,scripts_governance_archive_one_off_phase_a_backup_py,scripts_governance_archive_one_off_rename_kebab_to_snake_py,scripts_governance_archive_one_off_rename_whitelist_cleanup_py,scripts_governance_archive_one_off_test_lock_scenarios_py,scripts_governance_archive_one_off_verify_final_delivery_py,scripts_governance_archive_one_off_verify_rule_yaml_migration_py,scripts_governance_archive_prototype_adversarial_log_py,scripts_governance_archive_prototype_adversarial_sys_master_test_py,scripts_governance_archive_prototype_audit_domain_nodes_py,scripts_governance_archive_prototype_changelog_py,scripts_governance_archive_prototype_check_audit_rbac_isolation_py,scripts_governance_archive_prototype_construction_gate_py,scripts_governance_archive_prototype_generate_asset_index_py,scripts_governance_archive_prototype_generate_nav_table_py,scripts_governance_archive_prototype_rebuild_audit_index_py,scripts_governance_archive_prototype_scan_ground_truth_deps_py,scripts_governance_archive_prototype_session_simulator_py,scripts_governance_archive_prototype_sync_blueprint_status_py,scripts_governance_archive_vms_ri_ri_boundary_check_py,scripts_governance_archive_vms_ri_ri_build_completion_check_py,scripts_governance_archive_vms_ri_vms_blindspot_check_py,scripts_governance_archive_vms_ri_vms_build_completion_check_py,scripts_governance_archive_vms_ri_vms_cron_monitor_py,scripts_governance_archive_vms_ri_vms_cross_file_check_py,scripts_governance_archive_vms_ri_vms_health_check_py,scripts_governance_archive_vms_ri_vms_migrate_py,scripts_governance_archive_vms_ri_vms_migration_dry_run_py,scripts_governance_archive_vms_ri_vms_phase_rollback_py,scripts_governance_archive_vms_ri_vms_version_sync_check_py,scripts_governance_shared_base_py,scripts_governance_shared_constants_py,scripts_governance_shared_encoding_py,scripts_governance_shared_file_utils_py,scripts_governance_shared_frontmatter_py,scripts_governance_shared_libcst_docstring_adder_py,scripts_governance_shared_module_translation_loader_py,scripts_governance_shared_registry_entry_count_py,scripts_governance_shared_terminology_loader_py,scripts_governance_shared_thresholds_py,scripts_governance_shared_walk_py,scripts_governance_shared_yaml_utils_py,scripts_governance_sync_check_p0_status_py,scripts_governance_sync_cleanup_p0_auto_bridged_py,scripts_governance_sync_cleanup_p0_ops_pending_py,scripts_governance_sync_fix_orphan_deps_py,scripts_governance_tasks_list_phase0_tasks_py,scripts_governance_tasks_task_show_py,scripts_governance_tasks_task_summary_py,scripts_governance_add_deferred_design_edges_py,scripts_governance_align_battle_map_py,scripts_governance_apply_battle_map_py,scripts_governance_apply_dataflowgraph_py,scripts_governance_apply_decisiongraph_py,scripts_governance_apply_depgraph_py,scripts_governance_architecture_health_dashboard_py,scripts_governance_ast_import_rewriter_py,scripts_governance_audit_return_contract_usage_py,scripts_governance_audit_worktree_ops_telemetry_py,scripts_governance_check_commit_message_py,scripts_governance_check_ssot_gate_py,scripts_governance_d10_performance_collect_system_threads_py,scripts_governance_d11_compliance_audit_registration_py,scripts_governance_d11_compliance_ci_self_check_py,scripts_governance_d11_compliance_fix_shared_bypass_py,scripts_governance_d11_compliance_g9_compliance_check_py,scripts_governance_d11_compliance_task_self_check_py,scripts_governance_d11_compliance_validate_commit_gateway_py,scripts_governance_d11_compliance_validate_commit_message_py,scripts_governance_d11_compliance_validate_exit_codes_py,scripts_governance_d11_compliance_validate_frozen_requirements_py,scripts_governance_d11_compliance_validate_manifest_admission_py,scripts_governance_d11_compliance_validate_no_utf8_bom_py,scripts_governance_d11_compliance_validate_script_naming_py,scripts_governance_d11_compliance_validate_script_quality_py,scripts_governance_d11_compliance_validate_task_decomposition_bypass_py,scripts_governance_d11_compliance_validate_vocabulary_coverage_py,scripts_governance_d11_compliance_verify_audit_integrity_py,scripts_governance_d11_compliance_verify_schema_health_py,scripts_governance_d12_ai_hallucination_check_logger_kwargs_py,scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py,scripts_governance_d12_ai_hallucination_validate_session_budget_py,scripts_governance_d12_ai_hallucination_validate_session_gate_check_py,scripts_governance_d1_structure_archive_drafts_zone_py,scripts_governance_d1_structure_audit_config_format_py,scripts_governance_d1_structure_audit_directory_integrity_py,scripts_governance_d1_structure_audit_directory_scalability_py,scripts_governance_d1_structure_audit_findings_by_scope_py,scripts_governance_d1_structure_batch_create_index_md_py,scripts_governance_d1_structure_cbg_reset_py,scripts_governance_d1_structure_check_directory_contract_py,scripts_governance_d1_structure_check_handoff_manifests_py,scripts_governance_d1_structure_check_index_integrity_py,scripts_governance_d1_structure_cleanup_stash_py,scripts_governance_d1_structure_detect_orphan_py_py,scripts_governance_d1_structure_detect_residual_files_py,scripts_governance_d1_structure_detect_temp_files_py,scripts_governance_d1_structure_drafts_zone_archiver_py,scripts_governance_d1_structure_generate_missing_index_md_py,scripts_governance_d1_structure_reset_cbg_py,scripts_governance_d1_structure_run_script_smoke_test_py,scripts_governance_d1_structure_sync_index_from_manifest_py,scripts_governance_d1_structure_sync_policies_index_py,scripts_governance_d1_structure_validate_config_integrity_py,scripts_governance_d1_structure_validate_d1_output_sanity_py,scripts_governance_d1_structure_validate_immutable_core_py,scripts_governance_d1_structure_validate_index_reality_py,scripts_governance_d1_structure_validate_read_before_write_py,scripts_governance_d2_links_audit_broken_links_py,scripts_governance_d2_links_detect_relative_references_py,scripts_governance_d3_metadata_auto_generate_index_py,scripts_governance_d3_metadata_backfill_doctype_metadata_py,scripts_governance_d3_metadata_backfill_ttl_metadata_py,scripts_governance_d3_metadata_check_blueprint_compliance_py,scripts_governance_d3_metadata_check_frontmatter_metadata_py,scripts_governance_d3_metadata_check_module_singlesource_py,scripts_governance_d3_metadata_check_naming_convention_py,scripts_governance_d3_metadata_check_registry_consistency_py,scripts_governance_d3_metadata_check_schema_version_writes_py,scripts_governance_d3_metadata_check_vocab_hardcode_py,scripts_governance_d3_metadata_classify_ttl_by_content_py,scripts_governance_d3_metadata_deep_content_scanner_py,scripts_governance_d3_metadata_generate_derived_files_py,scripts_governance_d3_metadata_generate_rule_catalog_py,scripts_governance_d3_metadata_migrate_illegal_doctype_py,scripts_governance_d3_metadata_validate_architecture_py,scripts_governance_d3_metadata_validate_blueprint_provenance_py,scripts_governance_d3_metadata_validate_module_id_py,scripts_governance_d3_metadata_validate_module_id_naming_py,scripts_governance_d3_metadata_validate_registry_master_index_py,scripts_governance_d3_metadata_validate_tool_contracts_consistency_py,scripts_governance_d4_paths_detect_deprecated_path_writes_py,scripts_governance_d4_paths_detect_excessive_file_moves_py,scripts_governance_d4_paths_detect_ruins_references_py,scripts_governance_d4_paths_detect_split_delete_ref_commit_py,scripts_governance_d5_architecture_analyze_change_impact_py,scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py,scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py,scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py,scripts_governance_d5_architecture_audit_agent_spec_py,scripts_governance_d5_architecture_check_budget_health_py,scripts_governance_d5_architecture_check_drift_e2e_py,scripts_governance_d5_architecture_checkers_check_architecture_gates_py,scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py,scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py,scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py,scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py,scripts_governance_d5_architecture_checkers_check_code_duplication_py,scripts_governance_d5_architecture_checkers_check_contract_code_drift_py,scripts_governance_d5_architecture_checkers_check_contract_physical_path_py,scripts_governance_d5_architecture_checkers_check_dependency_direction_py,scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py,scripts_governance_d5_architecture_checkers_check_orphan_outputs_py,scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py,scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py,scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py,scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py,scripts_governance_d5_architecture_checkers_check_vms_ssot_py,scripts_governance_d5_architecture_dependency_graph_py,scripts_governance_d5_architecture_detect_causal_conflicts_py,scripts_governance_d5_architecture_detect_constraint_violations_py,scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py,scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py,scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py,scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py,scripts_governance_d5_architecture_diagnose_depgraph_py,scripts_governance_d5_architecture_generators_common_py,scripts_governance_d5_architecture_generators_align_panoramas_py,scripts_governance_d5_architecture_generators_generate_asset_catalog_py,scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py,scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py,scripts_governance_d5_architecture_generators_generate_candidate_module_report_py,scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py,scripts_governance_d5_architecture_generators_generate_contract_catalog_py,scripts_governance_d5_architecture_generators_generate_contracts_py,scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py,scripts_governance_d5_architecture_generators_generate_data_inventory_py,scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py,scripts_governance_d5_architecture_generators_generate_decision_diagram_py,scripts_governance_d5_architecture_generators_generate_panorama_registry_py,scripts_governance_d5_architecture_generators_generate_policies_py,scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py,scripts_governance_d5_architecture_panorama_common_py,scripts_governance_d5_architecture_pre_delete_safety_check_py,scripts_governance_d5_architecture_pre_write_gate_py,scripts_governance_d5_architecture_syncers_archive_rationale_log_py,scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py,scripts_governance_d5_architecture_syncers_merge_readme_to_index_py,scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py,scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py,scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py,scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py,scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py,scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py,scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py,scripts_governance_d5_architecture_validators_validate_arch_review_gate_py,scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py,scripts_governance_d5_architecture_validators_validate_autonomy_gate_py,scripts_governance_d5_architecture_validators_validate_b_track_packages_py,scripts_governance_d5_architecture_validators_validate_blind_spot_status_py,scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py,scripts_governance_d5_architecture_validators_validate_cross_references_py,scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py,scripts_governance_d5_architecture_validators_validate_depends_on_format_py,scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py,scripts_governance_d5_architecture_validators_validate_directory_structure_py,scripts_governance_d5_architecture_validators_validate_field_ownership_py,scripts_governance_d5_architecture_validators_validate_gate_yaml_py,scripts_governance_d5_architecture_validators_validate_handoff_package_py,scripts_governance_d5_architecture_validators_validate_interface_contracts_py,scripts_governance_d5_architecture_validators_validate_load_path_integrity_py,scripts_governance_d5_architecture_validators_validate_module_schema_py,scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py,scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py,scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py,scripts_governance_d5_architecture_validators_validate_target_layer_py,scripts_governance_d5_architecture_validators_validate_three_way_consistency_py,scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py,scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py,scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py,scripts_governance_d6_security_check_protected_paths_py,scripts_governance_d6_security_detect_anchor_file_deletion_py,scripts_governance_d6_security_detect_git_dangerous_py,scripts_governance_d6_security_detect_keywords_in_logs_py,scripts_governance_d6_security_detect_permanent_file_deletion_py,scripts_governance_d6_security_detect_secrets_py,scripts_governance_d6_security_detect_shell_dangerous_py,scripts_governance_d6_security_detect_shell_true_py,scripts_governance_d6_security_detect_threading_lock_py,scripts_governance_d6_security_detect_vague_terms_py,scripts_governance_d6_security_retire_tmp_artifacts_py,scripts_governance_d6_security_run_adversarial_checks_py,scripts_governance_d6_security_scan_runtime_log_secrets_py,scripts_governance_d6_security_scan_secret_leak_py,scripts_governance_d6_security_validate_gate_discipline_py,scripts_governance_d7_code_any_type_inferrer_py,scripts_governance_d7_code_check_ai_capability_boundary_py,scripts_governance_d7_code_check_any_abuse_py,scripts_governance_d7_code_check_encoding_py,scripts_governance_d7_code_check_idempotency_py,scripts_governance_d7_code_check_merge_conflict_py,scripts_governance_d7_code_check_no_tests_unit_py,scripts_governance_d7_code_check_pit_compliance_py,scripts_governance_d7_code_detect_absolute_path_hardcoding_py,scripts_governance_d7_code_detect_direct_llm_calls_py,scripts_governance_d7_code_detect_forward_reference_py,scripts_governance_d7_code_detect_missing_encoding_py,scripts_governance_d7_code_detect_private_key_py,scripts_governance_d7_code_detect_pydantic_any_fields_py,scripts_governance_d7_code_detect_silent_degradation_py,scripts_governance_d7_code_fix_n06_scope_py,scripts_governance_d7_code_fix_n12_ke_naming_py,scripts_governance_d7_code_fix_n13_snake_case_py,scripts_governance_d7_code_fix_n14_init_all_py,scripts_governance_d7_code_fix_n15_blueprint_path_py,scripts_governance_d7_code_fix_naming_manual_py,scripts_governance_d7_code_fix_orphan_exports_py,scripts_governance_d7_code_rewrite_imports_py,scripts_governance_d7_code_scan_complexity_py,scripts_governance_d7_code_scan_consumers_accuracy_py,scripts_governance_d7_code_scan_debt_py,scripts_governance_d7_code_validate_contracts_purity_py,scripts_governance_d7_code_validate_docstring_coverage_py,scripts_governance_d7_code_validate_fle_action_metadata_py,scripts_governance_d7_code_validate_fle_imports_py,scripts_governance_d7_code_validate_import_style_py,scripts_governance_d7_code_validate_init_all_py,scripts_governance_d7_code_validate_kb_write_provenance_py,scripts_governance_d7_code_validate_python_syntax_py,scripts_governance_d7_code_validate_test_assertion_depth_py,scripts_governance_d7_code_validate_test_coverage_py,scripts_governance_d7_code_validate_type_annotation_coverage_py,scripts_governance_d7_code_validate_unused_imports_py,scripts_governance_d8_doc_sync_audit_rename_completeness_py,scripts_governance_d8_doc_sync_auto_sync_all_registries_py,scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py,scripts_governance_d8_doc_sync_detect_dated_snapshots_py,scripts_governance_d8_doc_sync_sync_rule_registry_py,scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py,scripts_governance_d8_doc_sync_update_progress_py,scripts_governance_d8_doc_sync_validate_document_lifecycle_py,scripts_governance_d8_doc_sync_validate_document_ttl_py,scripts_governance_d9_knowledge_detect_duplicated_normative_language_py,scripts_governance_d9_knowledge_detect_orphan_documents_py,scripts_governance_data_quality_check_tick_duplication_py,scripts_governance_extract_decisiongraph_py,scripts_governance_extract_depgraph_py,scripts_governance_generate_decision_graph_py,scripts_governance_generate_project_depgraph_py,scripts_governance_generate_project_path_tree_py,scripts_governance_generators_check_gate_inventory_drift_py,scripts_governance_generators_fix_module_manifest_layout_py,scripts_governance_generators_generate_gate_registry_py,scripts_governance_generators_generate_importlinter_py,scripts_governance_generators_generate_path_ownership_map_py,scripts_governance_generators_generate_registry_master_index_py,scripts_governance_generators_inject_manifests_py,scripts_governance_generators_refresh_master_entries_py,scripts_governance_generators_sync_audit_protocol_numbers_py,scripts_governance_git_health_smoke_py,scripts_governance_harvest_candidates_from_drafts_py,scripts_governance_meta_concurrency_py,scripts_governance_meta_arbitrate_findings_py,scripts_governance_meta_backup_runtime_state_py,scripts_governance_meta_benchmark_test_fixtures_bad_imports_py,scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py,scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py,scripts_governance_meta_compute_sla_metrics_py,scripts_governance_meta_create_task_from_finding_py,scripts_governance_meta_detect_config_deviation_py,scripts_governance_meta_detect_fix_oscillation_py,scripts_governance_meta_detect_hallucinated_packages_py,scripts_governance_meta_detect_script_divergence_py,scripts_governance_meta_detect_script_rot_py,scripts_governance_meta_env_check_py,scripts_governance_meta_finding_state_machine_py,scripts_governance_meta_gate_engine_selfcheck_py,scripts_governance_meta_governance_watchdog_py,scripts_governance_meta_manage_baseline_py,scripts_governance_meta_manage_error_budget_py,scripts_governance_meta_manage_finding_timeseries_py,scripts_governance_meta_manage_script_ab_test_py,scripts_governance_meta_manage_script_retirement_py,scripts_governance_meta_manage_shadow_mode_py,scripts_governance_meta_mutation_test_post_sync_validator_py,scripts_governance_meta_mutation_test_reconciliation_registry_py,scripts_governance_meta_phase_e_context_check_py,scripts_governance_meta_pre_op_check_py,scripts_governance_meta_score_script_effectiveness_py,scripts_governance_meta_session_startup_check_py,scripts_governance_meta_trace_finding_lifecycle_py,scripts_governance_meta_track_script_costs_py,scripts_governance_meta_validate_automation_boundary_py,scripts_governance_meta_validate_cross_model_consensus_py,scripts_governance_meta_validate_dependency_chain_py,scripts_governance_meta_validate_emergency_bypass_log_py,scripts_governance_meta_validate_end_to_end_benchmark_py,scripts_governance_meta_validate_environment_health_py,scripts_governance_meta_validate_false_negatives_py,scripts_governance_meta_validate_gate_engine_external_py,scripts_governance_meta_validate_mutation_testing_py,scripts_governance_meta_validate_rule_freshness_py,scripts_governance_meta_validate_rules_file_backdoor_py,scripts_governance_meta_validate_rules_integrity_py,scripts_governance_meta_validate_script_onboarding_py,scripts_governance_meta_validate_script_provenance_py,scripts_governance_meta_validate_script_system_health_py,scripts_governance_meta_validate_threshold_changes_py,scripts_governance_meta_validate_trust_tier_py,scripts_governance_meta_verify_reconciliation_registry_py,scripts_governance_migrate_sqlite_to_pg_migrate_data_py,scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py,scripts_governance_migrate_to_metadata_tables_py,scripts_governance_oneoff_data_domain_audit_query_py,scripts_governance_query_module_panorama_py,scripts_governance_register_deferred_modules_py,scripts_governance_repair_concurrent_commit_test_py,scripts_governance_run_all_py,scripts_governance_run_gate_chain_py,scripts_governance_run_silent_failure_regression_py,scripts_governance_session_startup_health_check_py,scripts_governance_status_py,scripts_governance_sync_panorama_module_py,scripts_governance_verify_sync_integrity_py,scripts_governance_vms_vms_blindspot_check_py,scripts_governance_vms_vms_build_completion_check_py,scripts_governance_vms_vms_cron_monitor_py,scripts_governance_vms_vms_cross_file_check_py,scripts_governance_vms_vms_health_check_py,scripts_governance_vms_vms_migrate_py,scripts_governance_vms_vms_migration_dry_run_py,scripts_governance_vms_vms_phase_rollback_py,scripts_governance_vms_vms_version_sync_check_py,tests_governance_scripts_governance_test_any_type_inferrer_py,tests_governance_scripts_governance_test_check_canonical_yaml_drift_py,tests_governance_scripts_governance_test_check_vocab_hardcode_py,tests_governance_scripts_governance_test_pre_write_gate_py,tests_governance_test_check_blueprint_code_alignment_py production
    class scripts_governance_oneoff_data_domain_design_state_complete_py design
    class D_SHARED,D_GOVERNANCE,D_DATA,D_GOV_ENFORCEMENT,D_GOV_AUDIT,D_AUTONOMY_PERM,D_GOV_RULE,D_OPS,D_GOV_DRIFT external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 390 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_scripts_registry_yaml["脚本注册表<br/>scripts注册表，机器学习的注册表，登记和查询已注<br/>册的条目。<br/>scripts_registry<br/>文件: catalogs/scripts_registry.yaml<br/>(生产态 / production)"]
    scripts_archive_governance_dm106_p2b_verification_py["DM-106: P2-B 迁移全量验证脚本<br/>治理包的dm106_p2b_verification模块<br/>文件: governance/dm106_p2b_verification.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_audit_post_sync_commands_py["审计postsynccommands<br/>post_sync_standard 命令可执行性巡检（防幻觉<br/>/CLI漂移）<br/>audit_post_sync_commands<br/>文件: one_off/audit_post_sync_commands.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_check_exam_case_consistency_py["考试题库一致性检查——根因治本，防止'定义-注册脱钩<br/>'复发。<br/>1. 孤儿题：定义了但未注册到 ALL_EXAM_CASES 的<br/>ExamTestCase（死代码）<br/>check_exam_case_consistency<br/>文件: one_off/check_exam_case_consistency.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_create_alignment_tasks_py["创建对齐任务<br/>对齐任务批量创建器，为治理自动化与对齐工作流生成<br/>对齐任务卡片并写入任务仓库（已归档 one-off<br/>脚本）。<br/>文件: one_off/create_alignment_tasks.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_dm105_depgraph_triage_py["dm105depgraph分诊<br/>DM-105: depgraph 未分配节点三策略处理脚本<br/>dm105_depgraph_triage<br/>文件: one_off/dm105_depgraph_triage.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_fix_broken_post_sync_py["修复brokenpostsync<br/>批量修复历史 broken post_sync_standard 命令<br/>fix_broken_post_sync<br/>文件: one_off/fix_broken_post_sync.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_list_phase0_tasks_py["listphase0任务<br/>one off包的list_phase0_tasks模块<br/>文件: one_off/list_phase0_tasks.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_phase_a_backup_py["阶段a备份<br/>阶段A安全网 Tier0/Tier1 关键文件备份<br/>phase_a_backup<br/>文件: one_off/phase_a_backup.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_rename_kebab_to_snake_py["renamekebabtosnake.py — 全项目文件名/目录名 ke<br/>全项目文件名/目录名 kebab-case → snake_case<br/>批量重命名。<br/>rename_kebab_to_snake<br/>文件: one_off/rename_kebab_to_snake.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_rename_whitelist_cleanup_py["命名规范白名单清理 - 全文替换脚本。<br/>按施工方案 docs/_working/audit/research_notes<br/>/naming_whitelist_cleanup_plan.md Phase 3 执行。<br/>rename_whitelist_cleanup<br/>文件: one_off/rename_whitelist_cleanup.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_test_lock_scenarios_py["测试锁scenarios<br/>场景 B: 两个 AI 同时修改同一文件 → 后到者被阻塞<br/>test_lock_scenarios<br/>文件: one_off/test_lock_scenarios.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_verify_final_delivery_py["(INVARIANTS) 设计态节点数>=1128; 规则表各表>0<br/>§11最终交付验证<br/>verify_final_delivery<br/>文件: one_off/verify_final_delivery.py<br/>(生产态 / production)"]
    scripts_governance_archive_one_off_verify_rule_yaml_migration_py["verify规则yamlmigration<br/>verify_rule_yaml_migration.py - 6-dimensional<br/>verification of rule YAML migra...<br/>文件: one_off/verify_rule_yaml_migration.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_adversarial_log_py["红白对抗闭环记录——攻击→根源分析→修复→回归验证→知<br/>识注入全链路追踪<br/>python scripts/governance/adversarial_log.py<br/>--list         # 列出所有对抗记录<br/>文件: prototype/adversarial_log.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_adversarial_sys_master_test_py["对抗sys主测试<br/>exit 0 = 所有攻击被防御系统检测到（预期行为）<br/>文件: prototype/adversarial_sys_master_test.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_changelog_py["changelog.py — 治理域变更日志生成/追加工具.<br/>prototype包的changelog模块<br/>文件: prototype/changelog.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_check_audit_rbac_isolation_py["check审计RBACisolation<br/>静态分析 audit-trail 是否直接 import agent-rbac.<br/>check_audit_rbac_isolation<br/>文件: prototype/check_audit_rbac_isolation.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_construction_gate_py["construction门禁<br/>Construction Gate — 施工前路径校验门禁<br/>construction_gate<br/>文件: prototype/construction_gate.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_generate_asset_index_py["全项目资产索引生成器<br/>RULE-NINE 合规：生成 unified-asset-index.yaml<br/>供新 AI session 冷启动时了解项目全盘资产规模。<br/>generate_asset_index<br/>文件: prototype/generate_asset_index.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_generate_nav_table_py["生成navtable<br/>全流程导航表自动生成器 v1.0.0<br/>generate_nav_table<br/>文件: prototype/generate_nav_table.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_rebuild_audit_index_py["rebuild审计索引<br/>python scripts/governance<br/>/rebuild_audit_index.py --warn-only  #<br/>重建+警告模式<br/>文件: prototype/rebuild_audit_index.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_scan_ground_truth_deps_py["扫描groundtruthdeps<br/>Ground truth<br/>依赖扫描器，为任务卡系统与架构重构扫描真实依赖关<br/>系作为基准数据（已归档原型）。<br/>文件: prototype/scan_ground_truth_deps.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_session_simulator_py["会话模拟器<br/>session_simulator — 30 个模拟开发 session<br/>的蓝图读取事件生成器<br/>文件: prototype/session_simulator.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_sync_blueprint_status_py["同步蓝图状态<br/>此脚本零人工介入。纯机械映射。<br/>sync_blueprint_status<br/>文件: prototype/sync_blueprint_status.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_ri_boundary_check_py["riboundary检查<br/>验证 15 RI 模块的边界声明与实际代码一致性<br/>ri_boundary_check<br/>文件: vms_ri/ri_boundary_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_blindspot_check_py["VMS 盲点闭合检查器 — MOD-INF-011 · R1(33) + R2(<br/>vms ri包的vms_blindspot_check模块<br/>文件: vms_ri/vms_blindspot_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_build_completion_check_py["vms构建completion检查<br/>vms ri包的vms_build_completion_check模块<br/>文件: vms_ri/vms_build_completion_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_cross_file_check_py["VMS 跨文件内容一致性检查器 — MOD-INF-011 ·<br/>TASK-INF<br/>VMS 跨文件内容一致性检查器，校验 12 个文件中<br/>Collection 列表、嵌入维度（1024d<br/>/512d）、chunk_strategy<br/>路由、导入路径四维度一致性（已归档版）。<br/>vms_cross_file_check<br/>文件: vms_ri/vms_cross_file_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_health_check_py["vms健康检查<br/>vms ri包的vms_health_check模块<br/>文件: vms_ri/vms_health_check.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_migrate_py["VMS Phase 2 数据迁移脚本 — MOD-INF-011<br/>vms ri包的vms_migrate模块<br/>文件: vms_ri/vms_migrate.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_migration_dry_run_py["vms迁移dry运行<br/>VMS 迁移 dry-run 脚本，预览 unified_memory<br/>topic 到 Collection 的映射，作为 Phase 2<br/>迁移前置检查（已归档版）。<br/>vms_migration_dry_run<br/>文件: vms_ri/vms_migration_dry_run.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_phase_rollback_py["vms阶段回滚<br/>vms ri包的vms_phase_rollback模块<br/>文件: vms_ri/vms_phase_rollback.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_version_sync_check_py["VMS 版本同步检查器 — MOD-INF-011 · TASK-INF-022<br/>vms ri包的vms_version_sync_check模块<br/>文件: vms_ri/vms_version_sync_check.py<br/>(生产态 / production)"]
    scripts_governance_shared_base_py["基类<br/>对标 SCRIPT-QUALITY-001 多项条款的根因修复：<br/>文件: _shared/base.py<br/>(生产态 / production)"]
    scripts_governance_sync_cleanup_p0_auto_bridged_py["清理历史 P0 自动桥接任务<br/>历史 P0 自动桥接任务清理器<br/>（一次性止血操作），把 tags 含 auto-bridged 的<br/>PENDING P0 任务降级为<br/>P1+COMPLETED，避免自动桥接 Finding<br/>阻塞人工队列。<br/>cleanup_p0_auto_bridged<br/>文件: _sync/cleanup_p0_auto_bridged.py<br/>(生产态 / production)"]
    scripts_governance_sync_cleanup_p0_ops_pending_py["清理p0运维待处理<br/>一次性：将所有 OPS-* P0+PENDING 任务降级+完成<br/>cleanup_p0_ops_pending<br/>文件: _sync/cleanup_p0_ops_pending.py<br/>(生产态 / production)"]
    scripts_governance_sync_fix_orphan_deps_py["修复孤儿deps<br/>一次性修复孤儿依赖引用<br/>fix_orphan_deps<br/>文件: _sync/fix_orphan_deps.py<br/>(生产态 / production)"]
    scripts_governance_tasks_list_phase0_tasks_py["listphase0任务<br/>tasks包的list_phase0_tasks模块<br/>文件: _tasks/list_phase0_tasks.py<br/>(生产态 / production)"]
    scripts_governance_tasks_task_show_py["任务show<br/>governance/task_show 脚本 — 任务卡详情查询 CLI。<br/>文件: _tasks/task_show.py<br/>(生产态 / production)"]
    scripts_governance_tasks_task_summary_py["任务摘要<br/>任务系统全局摘要 CLI<br/>task_summary<br/>文件: _tasks/task_summary.py<br/>(生产态 / production)"]
    scripts_governance_add_deferred_design_edges_py["新增deferred设计边<br/>为暂缓模块添加设计态依赖边<br/>（dep_maturity='design'）。<br/>add_deferred_design_edges<br/>文件: governance/add_deferred_design_edges.py<br/>(生产态 / production)"]
    scripts_governance_align_battle_map_py["governance/align_battle_map<br/>G-battle-map-align: 作战地图对齐检测器<br/>（battle_map_positioning.md §8.3）<br/>文件: governance/align_battle_map.py<br/>(生产态 / production)"]
    scripts_governance_apply_battle_map_py["governance/apply_battle_map<br/>(INVARIANTS) pg_advisory_lock 写锁;<br/>BM-INV-001~002 校验; 事务回滚<br/>文件: governance/apply_battle_map.py<br/>(生产态 / production)"]
    scripts_governance_apply_dataflowgraph_py["应用dataflowgraph<br/>dataflowgraph 变更写入工具（CLI）<br/>apply_dataflowgraph<br/>文件: governance/apply_dataflowgraph.py<br/>(生产态 / production)"]
    scripts_governance_apply_decisiongraph_py["应用decisiongraph<br/>(INVARIANTS) pg_advisory_lock 写锁;<br/>build_status 单调推进; DEC-INV-001~005 校验;<br/>事务回滚<br/>apply_decisiongraph<br/>文件: governance/apply_decisiongraph.py<br/>(生产态 / production)"]
    scripts_governance_apply_depgraph_py["(INVARIANTS) 原子写入<br/>（RULE-ONE）；变更前验证；禁止直接覆盖<br/>depgraph 变更写入工具（RULE-SIXTEEN 强制配套）<br/>apply_depgraph<br/>文件: governance/apply_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_architecture_health_dashboard_py["架构健康仪表盘<br/>架构健康度仪表盘（自动化检测基线）<br/>architecture_health_dashboard<br/>文件: governance<br/>/architecture_health_dashboard.py<br/>(生产态 / production)"]
    scripts_governance_ast_import_rewriter_py["ast导入rewriter<br/>AST 导入重写器，governance 目录迁移时用 ast<br/>模块精确重写 import 路径（from<br/>zephyr.governance.foo → from<br/>zephyr.governance.subdir.foo），非正则替换避免误<br/>伤。<br/>文件: governance/ast_import_rewriter.py<br/>(生产态 / production)"]
    scripts_governance_audit_return_contract_usage_py["审计returncontractusage<br/>返回契约 ok 键调用方审计<br/>audit_return_contract_usage<br/>文件: governance/audit_return_contract_usage.py<br/>(生产态 / production)"]
    scripts_governance_audit_worktree_ops_telemetry_py["审计worktree运维遥测<br/>主工作区文件级擦除操作遥测完整性审计<br/>audit_worktree_ops_telemetry<br/>文件: governance/audit_worktree_ops_telemetry.py<br/>(生产态 / production)"]
    scripts_governance_check_commit_message_py["检查提交message<br/>**治本动机**：原计划 server-side pre-receive<br/>hook 在 GitHub-hosted 仓库<br/>文件: governance/check_commit_message.py<br/>(生产态 / production)"]
    scripts_governance_check_ssot_gate_py["checkssot门禁<br/>SSoT 创建门禁（pre-commit hook 双保险）。<br/>check_ssot_gate<br/>文件: governance/check_ssot_gate.py<br/>(生产态 / production)"]
    scripts_governance_d10_performance_collect_system_threads_py["collect系统threads<br/>全系统线程数快照采集器<br/>collect_system_threads<br/>文件: d10_performance/collect_system_threads.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_audit_registration_py["审计registration<br/>孤儿注册检测（RULE-TWO 防线 2）<br/>audit_registration<br/>文件: d11_compliance/audit_registration.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_ci_self_check_py["ci自检查<br/>Tier 8 — 纯 stdlib 零依赖的完整性检查。<br/>ci_self_check<br/>文件: d11_compliance/ci_self_check.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_fix_shared_bypass_py["修复共享绕过<br/>检测赋值节点是否包含 Path(__file__).parents(N)<br/>模式（不限变量名）。<br/>文件: d11_compliance/fix_shared_bypass.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_g9_compliance_check_py["G9 四蓝图跨模块集成合规门禁执行器.<br/>机械执行 7 项检查，零人工介入。<br/>g9_compliance_check<br/>文件: d11_compliance/g9_compliance_check.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_task_self_check_py["任务自检查<br/>任务系统自身健康检查<br/>task_self_check<br/>文件: d11_compliance/task_self_check.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_commit_gateway_py["校验提交网关<br/>检测裸 git commit，强制走 GitCommitGateway<br/>（根治幽灵提交）。<br/>validate_commit_gateway<br/>文件: d11_compliance/validate_commit_gateway.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_commit_message_py["校验提交message<br/>检测 commit message 是否包含 AI 归因<br/>trailer，缺失时仅警告不阻断。<br/>validate_commit_message<br/>文件: d11_compliance/validate_commit_message.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_exit_codes_py["validate退出codes<br/>审计脚本退出码规范门禁<br/>validate_exit_codes<br/>文件: d11_compliance/validate_exit_codes.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_frozen_requirements_py["校验frozenrequirements<br/>依赖版本锁定与验证（蓝图 §34.2）<br/>validate_frozen_requirements<br/>文件: d11_compliance<br/>/validate_frozen_requirements.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_manifest_admission_py["validate清单admission<br/>Manifest<br/>准入校验器，检查清单文件是否符合准入标准，决定是<br/>否允许进入治理流水线。<br/>文件: d11_compliance<br/>/validate_manifest_admission.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_no_utf8_bom_py["校验noutf8bom<br/>扫描项目中所有 .yaml / .md / .py 文件，检测<br/>UTF-8 BOM (﻿) 的存在。<br/>validate_no_utf8_bom<br/>文件: d11_compliance/validate_no_utf8_bom.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_script_naming_py["校验scriptnaming<br/>审计脚本命名规范门禁<br/>validate_script_naming<br/>文件: d11_compliance/validate_script_naming.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_script_quality_py["validatescript质量<br/>治理脚本质量合规检查<br/>validate_script_quality<br/>文件: d11_compliance/validate_script_quality.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py["validatetaskdecomposition绕过<br/>检测 AI 是否通过将高危任务拆分为多个「安全」子任<br/>务来绕过门禁。<br/>validate_task_decomposition_bypass<br/>文件: d11_compliance<br/>/validate_task_decomposition_bypass.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_validate_vocabulary_coverage_py["校验vocabularycoverage<br/>从 JSON Schema 中提取所有 oneOf+const<br/>模式的枚举字段。<br/>文件: d11_compliance<br/>/validate_vocabulary_coverage.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_verify_audit_integrity_py["校验审计完整性<br/>审计完整性零依赖独立验证器，纯标准库实现，只需<br/>events.jsonl<br/>即可验证哈希链与签名，任何环境都能直接运行。<br/>verify_audit_integrity<br/>文件: d11_compliance/verify_audit_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d11_compliance_verify_schema_health_py["校验模式健康<br/>(PostgreSQL) Schema 健康度校验门禁（#ARCH-016<br/>治本）<br/>verify_schema_health<br/>文件: d11_compliance/verify_schema_health.py<br/>(生产态 / production)"]
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py["check日志器kwargs<br/>病根（Root Cause）：项目存在双日志系统<br/>（structlog + 标准 logging），<br/>文件: d12_ai_hallucination<br/>/check_logger_kwargs.py<br/>(生产态 / production)"]
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py["校验门禁提示冲突<br/>检测门禁 YAML 规则与 AGENTS.md / 项目 Prompt<br/>指令之间的冲突。<br/>validate_gate_prompt_conflict<br/>文件: d12_ai_hallucination<br/>/validate_gate_prompt_conflict.py<br/>(生产态 / production)"]
    scripts_governance_d12_ai_hallucination_validate_session_budget_py["校验会话预算<br/>Session 操作预算校验（已废弃）<br/>validate_session_budget<br/>文件: d12_ai_hallucination<br/>/validate_session_budget.py<br/>(生产态 / production)"]
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py["校验会话门禁检查<br/>Session 门禁检查完整性校验<br/>validate_session_gate_check<br/>文件: d12_ai_hallucination<br/>/validate_session_gate_check.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_archive_drafts_zone_py["草稿区生命周期归档器——扫描 arbitrated 草稿，按<br/>age 判定 wa<br/>rn/archive/skip<br/>archive_drafts_zone<br/>文件: d1_structure/archive_drafts_zone.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_audit_config_format_py["审计配置format<br/>config/ 目录格式/注释/边界快速扫描<br/>audit_config_format<br/>文件: d1_structure/audit_config_format.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_audit_directory_integrity_py["审计directory完整性<br/>01_policies_and_standards/ 目录结构完整性审计<br/>audit_directory_integrity<br/>文件: d1_structure/audit_directory_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_audit_directory_scalability_py["审计directoryscalability<br/>- 物理结构可扩展性审计 (1500模块支撑能力检查)<br/>audit_directory_scalability<br/>文件: d1_structure<br/>/audit_directory_scalability.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_audit_findings_by_scope_py["审计findingsby作用域<br/>按目录范围筛选 Finding 报告<br/>audit_findings_by_scope<br/>文件: d1_structure/audit_findings_by_scope.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_batch_create_index_md_py["批次创建索引md<br/>Batch create index.md for all directories under<br/>docs/ that lack one<br/>文件: d1_structure/batch_create_index_md.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_cbg_reset_py["cbg重置<br/>d1 structure包的cbg_reset模块<br/>文件: d1_structure/cbg_reset.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_check_directory_contract_py["检查directory契约<br/>Consumes directory_contract.yaml<br/>（目录维度约束的唯一真源，合并原先分散在<br/>文件: d1_structure/check_directory_contract.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_check_handoff_manifests_py["检查handoffmanifests<br/>验证 .trae/session_state/ 目录下所有<br/>CT-*_progress.yaml 是否存在且不超过 30 天未更新.<br/>check_handoff_manifests<br/>文件: d1_structure/check_handoff_manifests.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_check_index_integrity_py["检查索引完整性<br/>对标：PS-STD-012 §7.3（index.md 清单 vs<br/>磁盘实际文件双向差集）<br/>check_index_integrity<br/>文件: d1_structure/check_index_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_cleanup_stash_py["清理stash<br/>对标：OPS-2026062501 病根3（stash<br/>堆积无清理机制）<br/>cleanup_stash<br/>文件: d1_structure/cleanup_stash.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_detect_orphan_py_py["detect孤儿py<br/>全库孤儿 .py 文件检测<br/>detect_orphan_py<br/>文件: d1_structure/detect_orphan_py.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_detect_residual_files_py["检测residualfiles<br/>对标：GOV- §4.3（残留物检测标准）<br/>detect_residual_files<br/>文件: d1_structure/detect_residual_files.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_detect_temp_files_py["检测tempfiles<br/>扫描临时文件与缓存目录，返回 (发现列表,<br/>已扫描文件数)。<br/>文件: d1_structure/detect_temp_files.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_drafts_zone_archiver_py["draftszone归档器<br/>草稿区生命周期归档器 (Drafts Zone Lifecycle<br/>Archiver · V-16)<br/>drafts_zone_archiver<br/>文件: d1_structure/drafts_zone_archiver.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_generate_missing_index_md_py["generatemissing索引md<br/>扫描目录树，为缺失 index.md<br/>的目录自动生成索引文件。<br/>generate_missing_index_md<br/>文件: d1_structure/generate_missing_index_md.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_reset_cbg_py["重置cbg<br/>d1 structure包的reset_cbg模块<br/>文件: d1_structure/reset_cbg.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_run_script_smoke_test_py["runscriptsmoke测试<br/>治理脚本冒烟测试运行器<br/>run_script_smoke_test<br/>文件: d1_structure/run_script_smoke_test.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_sync_index_from_manifest_py["sync索引from清单<br/>从 script_manifest.yaml (SSoT) 自动同步<br/>index.md 的脚本数量。<br/>sync_index_from_manifest<br/>文件: d1_structure/sync_index_from_manifest.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_sync_policies_index_py["同步策略索引<br/>从磁盘实际扫描，自动同步 PS-IDX-001 §二<br/>文件数量表格。<br/>sync_policies_index<br/>文件: d1_structure/sync_policies_index.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_config_integrity_py["校验配置完整性<br/>运行时配置完整性十一层纵深审计 + 自动同步检测<br/>validate_config_integrity<br/>文件: d1_structure/validate_config_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_d1_output_sanity_py["校验d1outputsanity<br/>D1 产出物合理性校验（蓝图 §31 B93）<br/>validate_d1_output_sanity<br/>文件: d1_structure/validate_d1_output_sanity.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_immutable_core_py["校验不可变核心<br/>对标：PS-STD-003 ABS-01（AI 不可改<br/>immutable_core 层）<br/>validate_immutable_core<br/>文件: d1_structure/validate_immutable_core.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_index_reality_py["validate索引reality<br/>索引真实性校验器，比对索引文件与磁盘实际文件，检<br/>测索引中记录但磁盘不存在（或反之）的偏移。<br/>文件: d1_structure/validate_index_reality.py<br/>(生产态 / production)"]
    scripts_governance_d1_structure_validate_read_before_write_py["校验readbeforewrite<br/>先读后写校验（IRN-008）<br/>validate_read_before_write<br/>文件: d1_structure/validate_read_before_write.py<br/>(生产态 / production)"]
    scripts_governance_d2_links_audit_broken_links_py["检测文档/数据文件中的断链与幽灵引用。<br/>调研发现 AI 在 .md/.csv/.yaml<br/>中编造虚假文件引用（如 dom_gov_001<br/>虚假审计闭环：<br/>audit_broken_links<br/>文件: d2_links/audit_broken_links.py<br/>(生产态 / production)"]
    scripts_governance_d2_links_detect_relative_references_py["检测relativereferences<br/>相对路径引用检测<br/>detect_relative_references<br/>文件: d2_links/detect_relative_references.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_auto_generate_index_py["自动生成索引<br/>迁移历史：从 d5_architecture/generators/ 迁入<br/>d3_metadata/（本脚本是元数据校验器，<br/>文件: d3_metadata/auto_generate_index.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_backfill_doctype_metadata_py["backfilldoctype元数据<br/>批量回填 frontmatter doc_type 字段（doc_type<br/>存量治理 Stage 2.1）<br/>backfill_doctype_metadata<br/>文件: d3_metadata/backfill_doctype_metadata.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_backfill_ttl_metadata_py["backfill存活时间元数据<br/>批量回填/重判 ttl 字段（6 格式统一入口，GATE-15<br/>存量治理 + GATE-VOCAB-CHANGE 纠偏）<br/>backfill_ttl_metadata<br/>文件: d3_metadata/backfill_ttl_metadata.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_blueprint_compliance_py["(INVARIANTS) REQUIREDSECTIONS 必须与蓝图+施工图<br/>(INVARIANTS) REQUIRED_SECTIONS<br/>必须与蓝图+施工图模板 v2.1.0<br/>COMPLIANCE_CHECKLIST 一致<br/>check_blueprint_compliance<br/>文件: d3_metadata/check_blueprint_compliance.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_frontmatter_metadata_py["检查frontmatter元数据<br/>校验 .md 文档 frontmatter 的词表字段：<br/>check_frontmatter_metadata<br/>文件: d3_metadata/check_frontmatter_metadata.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_module_singlesource_py["检查模块singlesource<br/>GATE-SSOT-SINGLESOURCE: SSoT 单一真源门禁<br/>（Phase 7 治本防复发）。<br/>check_module_singlesource<br/>文件: d3_metadata/check_module_singlesource.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_naming_convention_py["GATE-11 命名规范门禁 — 全类型命名检测。<br/>N-01  文件名大写检测 + 白名单<br/>check_naming_convention<br/>文件: d3_metadata/check_naming_convention.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_registry_consistency_py["检查注册表一致性<br/>check_registry_consistency —<br/>跨登记表一致性校验。<br/>文件: d3_metadata/check_registry_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_schema_version_writes_py["check结构版本writes<br/>G_TRAE_059 验证脚本：_schema_version 写入保护 +<br/>版本一致性检查。<br/>check_schema_version_writes<br/>文件: d3_metadata/check_schema_version_writes.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_vocab_hardcode_py["检查vocabhardcode<br/>GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）<br/>check_vocab_hardcode<br/>文件: d3_metadata/check_vocab_hardcode.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_classify_ttl_by_content_py["基于内容关键词的 ttl 精细分类审查脚本。<br/>- backfill：按 decision_tree<br/>（路径+doc_type）自动回填 ttl——执行工具<br/>classify_ttl_by_content<br/>文件: d3_metadata/classify_ttl_by_content.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_deep_content_scanner_py["deep内容扫描器<br/>对标：PS-STD-012 §7.3（doc_type<br/>与正文关键词启发式不匹配）<br/>deep_content_scanner<br/>文件: d3_metadata/deep_content_scanner.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_generate_derived_files_py["生成derivedfiles<br/>枚举自动派生生成器（Level 3 终极防御）<br/>generate_derived_files<br/>文件: d3_metadata/generate_derived_files.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_generate_rule_catalog_py["生成规则目录<br/>Scan docs/01_policies_and_standards and emit<br/>_registry/catalogs/rule_catalog_registry.yaml<br/>文件: d3_metadata/generate_rule_catalog.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_migrate_illegal_doctype_py["批量迁移非法 doctype 值（doctype 存量治理 Stage<br/>2.<br/>批量迁移非法 doc_type 值（doc_type 存量治理<br/>Stage 2.2）<br/>migrate_illegal_doctype<br/>文件: d3_metadata/migrate_illegal_doctype.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_architecture_py["校验架构<br/>从 .md / .yaml 文件读取 frontmatter 字段<br/>（统一返回 dict）。<br/>文件: d3_metadata/validate_architecture.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_blueprint_provenance_py["校验蓝图溯源<br/>校验蓝图provenance。Blueprint Provenance Gate -<br/>V-12: validate provenance triples in blueprint<br/>frontmatter<br/>文件: d3_metadata<br/>/validate_blueprint_provenance.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_module_id_py["校验模块id<br/>GATE-MODULEID: Validate module_id uniqueness<br/>and index/file consistency<br/>文件: d3_metadata/validate_module_id.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_registry_master_index_py["校验注册表主索引<br/>登记表总索引自校验门禁 (Registry Master Index<br/>Self-Check Gate · V-18).<br/>validate_registry_master_index<br/>文件: d3_metadata<br/>/validate_registry_master_index.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_tool_contracts_consistency_py["validatetool契约consistency<br/>对比 tool-contracts.yaml 中 tool 的<br/>input_schema ↔ 代码中 handler 实际注册的参数。<br/>validate_tool_contracts_consistency<br/>文件: d3_metadata<br/>/validate_tool_contracts_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d4_paths_detect_deprecated_path_writes_py["检测废弃路径writes<br/>废弃路径写入检测<br/>detect_deprecated_path_writes<br/>文件: d4_paths/detect_deprecated_path_writes.py<br/>(生产态 / production)"]
    scripts_governance_d4_paths_detect_excessive_file_moves_py["检测excessive文件moves<br/>文件过度搬迁检测<br/>detect_excessive_file_moves<br/>文件: d4_paths/detect_excessive_file_moves.py<br/>(生产态 / production)"]
    scripts_governance_d4_paths_detect_ruins_references_py["检测ruinsreferences<br/>残骸/废弃路径引用检测<br/>detect_ruins_references<br/>文件: d4_paths/detect_ruins_references.py<br/>(生产态 / production)"]
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py["检测拆分删除ref提交<br/>删除引用分离提交检测<br/>detect_split_delete_ref_commit<br/>文件: d4_paths/detect_split_delete_ref_commit.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_analyze_change_impact_py["analyzechange冲击<br/>变更影响分析器，分析某次改动会波及哪些模块与依赖<br/>，产出影响范围报告供评审决策。<br/>文件: d5_architecture/analyze_change_impact.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py["analyzecontract冲击<br/>契约变更影响分析器<br/>analyze_contract_impact<br/>文件: analyzers/analyze_contract_impact.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py["审计dependsonchaindepth<br/>depends_on 依赖链路深度审计<br/>audit_depends_on_chain_depth<br/>文件: analyzers/audit_depends_on_chain_depth.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py["measure弃用级联<br/>废弃级联影响度量<br/>measure_deprecation_cascade<br/>文件: analyzers/measure_deprecation_cascade.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_audit_agent_spec_py["审计代理spec<br/>(INVARIANTS) agent-spec 审计完整性<br/>audit_agent_spec<br/>文件: d5_architecture/audit_agent_spec.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_check_budget_health_py["(INVARIANTS)<br/>预算健康检查不可跳过;检查结果必须可机器解析<br/>预算健康检查器，检查预算执行情况是否健康，结果必<br/>须可机器解析且不可跳过。<br/>check_budget_health<br/>文件: d5_architecture/check_budget_health.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_check_drift_e2e_py["检查漂移端到端<br/>Tier 8 — 每次 CI 全量回归时运行 drift E2E +<br/>自检 + 注册表一致性。<br/>文件: d5_architecture/check_drift_e2e.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py["检查架构门禁<br/>用途：验证架构终局完成度，作为进入 beta<br/>施工阶段的门禁。<br/>v2.4.0 — 2026-05-03<br/>文件: checkers/check_architecture_gates.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py["(INVARIANTS)<br/>蓝图§5.5自动化触发机制状态列必须与代码实际实现一<br/>致<br/>; ⚠️待实现但代码已实现=DRIFT;<br/>✅已实现但代码不存在=DRIFT<br/>check_blueprint_automation_sync<br/>文件: checkers<br/>/check_blueprint_automation_sync.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py["检查蓝图代码对齐<br/>(INVARIANTS)<br/>代码(BLUEPRINT)头部module_id必须与蓝图注册表一致<br/>; 蓝图§4已实现文件必须在磁盘存在;<br/>frontmatter.build_status 必须与 depgraph 聚合<br/>build_status<br/>check_blueprint_code_alignment<br/>文件: checkers/check_blueprint_code_alignment.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py["(INVARIANTS)<br/>蓝图模板合规检查不可绕过;52项检查全覆盖<br/>蓝图模板合规检查器，52<br/>项检查全覆盖，校验蓝图文件是否符合模板规范<br/>（GOV-DOC-011），不可绕过。<br/>check_blueprint_template_compliance<br/>文件: checkers<br/>/check_blueprint_template_compliance.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py["check规范yaml漂移<br/>安全加载 YAML，返回解析对象（dict/list）。<br/>文件: checkers/check_canonical_yaml_drift.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_code_duplication_py["check代码duplication<br/>(INVARIANTS) 扫描 src/zephyr/ 下所有包;<br/>检测跨包同名文件代码重复<br/>check_code_duplication<br/>文件: checkers/check_code_duplication.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py["检查契约代码漂移<br/>— 契约-代码双写漂移阻断（盲点 C2 修复）<br/>check_contract_code_drift<br/>文件: checkers/check_contract_code_drift.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py["检查契约physical路径<br/>检查单个 physical_path 是否含连字符目录段,<br/>返回违规信息列表.<br/>文件: checkers/check_contract_physical_path.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py["check依赖direction<br/>依赖方向校验（INJ-002/008）<br/>check_dependency_direction<br/>文件: checkers/check_dependency_direction.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py["检查g6ctr合规<br/>checkers包的check_g6_ctr_compliance模块<br/>文件: checkers/check_g6_ctr_compliance.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py["check孤儿outputs<br/>(INVARIANTS) 扫描蓝图 §11 产出物 consumer_min;<br/>检测零消费者孤儿产出物<br/>check_orphan_outputs<br/>文件: checkers/check_orphan_outputs.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py["检查precommitiduniqueness<br/>扫描 .pre-commit-config.yaml 文本,返回<br/>(line_no, hook_id, repo_url, repo_line) 列表。<br/>文件: checkers/check_precommit_id_uniqueness.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py["check规则fourway对齐<br/>— 规则四方对齐门禁（ARCH-020 补建）<br/>check_rule_four_way_alignment<br/>文件: checkers/check_rule_four_way_alignment.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py["检查ssotuniqueness<br/>(INVARIANTS) 扫描所有蓝图 ssot_claims 字段;<br/>检测跨蓝图 SSoT 冲突<br/>check_ssot_uniqueness<br/>文件: checkers/check_ssot_uniqueness.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py["check追踪上下文propagation<br/>TraceContext 传播强制执行 CI 检查<br/>check_trace_context_propagation<br/>文件: checkers<br/>/check_trace_context_propagation.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_checkers_check_vms_ssot_py["GATE-VMS-SSOT: VMS 单一真源门禁——三重检测。<br/>checkers包的check_vms_ssot模块<br/>文件: checkers/check_vms_ssot.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_dependency_graph_py["依赖图<br/>治理域有向依赖图 — 扫描 governance/ 下所有<br/>import 生成依赖图.<br/>dependency_graph<br/>文件: d5_architecture/dependency_graph.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detect_causal_conflicts_py["检测causalconflicts<br/>治本（2026-06-27）：删除 DEFAULT_DEPGRAPH_PATH<br/>= .../depgraph.db 常量（路径污染源）。<br/>文件: d5_architecture/detect_causal_conflicts.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detect_constraint_violations_py["detect约束violations<br/>G9-Detect: 架构约束违规检测器（对照 depgraph<br/>实际数据检测 6 类违规）<br/>detect_constraint_violations<br/>文件: d5_architecture<br/>/detect_constraint_violations.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py["analyzesamename模块relations<br/>analyze_same_name_module_relations.py ---<br/>同名模块语义关系分析<br/>文件: detectors<br/>/analyze_same_name_module_relations.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py["检测depends开cycles<br/>检测循环依赖<br/>detect_depends_on_cycles<br/>文件: detectors/detect_depends_on_cycles.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py["检测废弃adrreferences<br/>对标：COND-38（引用 Deprecated ADR<br/>作为当前决策依据为条件禁止）<br/>detect_deprecated_adr_references<br/>文件: detectors<br/>/detect_deprecated_adr_references.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py["detect重复modulenames<br/>detect_duplicate_module_names.py ---<br/>同名模块语义关系分析<br/>文件: detectors/detect_duplicate_module_names.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_diagnose_depgraph_py["diagnose依赖图<br/>找出图拓扑孤儿节点（无入边无出边）。<br/>文件: d5_architecture/diagnose_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_align_panoramas_py["G-panorama-align: 四图对齐检测器（ARCH-053 + ARC<br/>H-056 四图升级）<br/>align_panoramas<br/>文件: generators/align_panoramas.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py["生成资产目录<br/>G13: 从 depgraph (PostgreSQL) 生成资产清单全景图<br/>generate_asset_catalog<br/>文件: generators/generate_asset_catalog.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py["generators/generate_battle_map_diagram<br/>generate_battle_map_diagram.py —<br/>交易决策作战地图可视化生成器<br/>文件: generators/generate_battle_map_diagram.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py["generate蓝图panorama<br/>G-panorama-gen: 蓝图 §0.6 四图对齐视图生成器<br/>（ARCH-053 + ARCH-056 + 模板 v2.1.0）<br/>generate_blueprint_panorama<br/>文件: generators/generate_blueprint_panorama.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_candidate_module_report_py["generators/generate_candidate_module_report<br/>从 candidate_module_registry.yaml<br/>生成候选模块清单报告（分片：索引 + 每域一个...<br/>文件: generators<br/>/generate_candidate_module_report.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py["generate代码wikistats<br/>Code Wiki 统计数据生成器（半自动维护机制）。<br/>generate_code_wiki_stats<br/>文件: generators/generate_code_wiki_stats.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py["生成契约目录<br/>G12: 从 depgraph (PostgreSQL) 生成契约目录全景图<br/>generate_contract_catalog<br/>文件: generators/generate_contract_catalog.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_contracts_py["生成契约<br/>治理的生成器，按规则生成所需的数据或报告<br/>文件: generators/generate_contracts.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py["generate数据acquisition流程<br/>G-acqflow: 从 tasks.yaml 生成业务数据采集流图<br/>MD（人类可读版，内嵌 Mermaid）<br/>generate_data_acquisition_flow<br/>文件: generators<br/>/generate_data_acquisition_flow.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_data_inventory_py["generate数据inventory<br/>G-inventory: 扫描 ClickHouse 生成业务数据清单 MD<br/>generate_data_inventory<br/>文件: generators/generate_data_inventory.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py["生成dataflowdiagram<br/>G-dataflow: 从 dataflowgraph (PostgreSQL)<br/>生成数据流图 Markdown 文档（内嵌 Mermaid）<br/>generate_dataflow_diagram<br/>文件: generators/generate_dataflow_diagram.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py["generate决策diagram<br/>G-decision: 从 decisiongraph (PostgreSQL)<br/>生成决策流图(.md 文档，Mermaid 内嵌)<br/>generate_decision_diagram<br/>文件: generators/generate_decision_diagram.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py["generatepanorama注册表<br/>G-panorama-registry: 自动生成全景图清单总表<br/>generate_panorama_registry<br/>文件: generators/generate_panorama_registry.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_policies_py["生成策略<br/>遍历 data_sources，对每个有非空 policy<br/>的数据源，<br/>generate_policies<br/>文件: generators/generate_policies.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py["generate交易流程diagram<br/>G-trading-flow: 从 decisiongraph + 叙事YAML +<br/>候选库 生成交易决策架构视图(.md)<br/>generate_trading_flow_diagram<br/>文件: generators<br/>/generate_trading_flow_diagram.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_pre_delete_safety_check_py["安全删除门禁脚本——RULE-THREE 强制执行器。<br/>删除任何文件前 MUST 通过5项检查：<br/>pre_delete_safety_check<br/>文件: d5_architecture/pre_delete_safety_check.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_pre_write_gate_py["prewrite门禁<br/>AI写入前强制门禁钩子: lock协议检查+GateEngine<br/>Phase评估+注册完整性验证<br/>pre_write_gate<br/>文件: d5_architecture/pre_write_gate.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py["archiverationale日志<br/>将已完成 Stage 移至 archive/<br/>子目录，主文件仅保留最近 3 个 Stage。<br/>archive_rationale_log<br/>文件: syncers/archive_rationale_log.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py["mergereadmeto索引<br/>合并readmeto索引。Strategy:<br/>文件: syncers/merge_readme_to_index.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py["同步蓝图代码索引<br/>对标：AGENTS.md §6.1 蓝图-代码同步强制约定<br/>sync_blueprint_code_index<br/>文件: syncers/sync_blueprint_code_index.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py["sync注册表fromblueprints<br/>扫描 03_modules/**/blueprint.md 的<br/>frontmatter,与 registry 对账,生成 diff<br/>或写入更新<br/>sync_registry_from_blueprints<br/>文件: syncers/sync_registry_from_blueprints.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py["校验蓝图代码同步<br/>md §6.1 蓝图-代码同步强制约定的 CI 门禁脚本<br/>validate_blueprint_code_sync<br/>文件: blueprint/validate_blueprint_code_sync.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py["校验蓝图实现文档<br/>md 6.4 铁律五 +<br/>铁律六：蓝图中声称的文件路径必须在磁盘上真实存在<br/>validate_blueprint_implementation_docs<br/>文件: blueprint<br/>/validate_blueprint_implementation_docs.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py["校验蓝图路径一致性<br/>蓝图路径一致性校验器，检查蓝图内引用的路径与实际<br/>磁盘路径是否一致，防悬空引用。<br/>文件: blueprint<br/>/validate_blueprint_path_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py["validate蓝图placement<br/>蓝图物理位置与归属链完整性校验器 (Blueprint<br/>Placement & BelongsTo Validator)<br/>validate_blueprint_placement<br/>文件: blueprint/validate_blueprint_placement.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py["validate蓝图taguniqueness<br/>校验蓝图标签uniqueness。GATE-TAG-UNIQUE -<br/>Blueprint tag uniqueness validation gate.<br/>文件: blueprint<br/>/validate_blueprint_tag_uniqueness.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py["validate生命周期refs<br/>生命周期引用约束合规检查<br/>validate_lifecycle_refs<br/>文件: lifecycle/validate_lifecycle_refs.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py["校验模块生命周期<br/>模块生命周期校验<br/>validate_module_lifecycle<br/>文件: lifecycle/validate_module_lifecycle.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py["校验会话日志索引完整性<br/>会话日志索引完整性校验器，检查会话日志与其索引文<br/>件是否对齐，防索引丢失或日志孤立。<br/>文件: session<br/>/validate_session_log_index_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py["validate会话日志updated<br/>对标：PS-STD-003 COND-16（AI 施工 session<br/>结束后必须写 session log）<br/>validate_session_log_updated<br/>文件: session/validate_session_log_updated.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py["校验adrfrontmatter一致性<br/>根因（R6 审计 P1-11/P1-12/P2-11/P2-12）：ADR<br/>分三批次产出（早期 0001~0013、<br/>validate_adr_frontmatter_consistency<br/>文件: validators<br/>/validate_adr_frontmatter_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py["校验架构审查门禁<br/>架构评审门控校验<br/>validate_arch_review_gate<br/>文件: validators/validate_arch_review_gate.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py["校验架构契约内部<br/>GATE-CONTRACT: CI gate for<br/>architecture_contract.yaml internal consistency<br/>文件: validators<br/>/validate_architecture_contract_internal.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py["validateautonomy门禁<br/>变更级别 vs AI 自治权限交叉校验<br/>validate_autonomy_gate<br/>文件: validators/validate_autonomy_gate.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py["校验btrackpackages<br/>- 原实现：B_TRACK_DIRS 硬编码 kebab_case 集合<br/>（含幻影 'kb'），与 src/zephyr/<br/>validate_b_track_packages<br/>文件: validators/validate_b_track_packages.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py["校验盲点状态<br/>D_RISK 是否已有 VaR/CVaR 实现<br/>GATE-BS: Blind Spot Reality Check<br/>文件: validators/validate_blind_spot_status.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py["validate代码yaml对齐<br/>对标：GATE-A 代码↔YAML 对齐<br/>validate_code_yaml_alignment<br/>文件: validators/validate_code_yaml_alignment.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_cross_references_py["validate跨references<br/>架构模型 YAML + 治理文档跨引用完整性闸门<br/>validate_cross_references<br/>文件: validators/validate_cross_references.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py["(INVARIANTS) 治理脚本执行正确<br/>依赖图模板验证器，校验依赖图数据是否符合模板规范<br/>，保证治理脚本执行正确。<br/>validate_dependency_graph_template<br/>文件: validators<br/>/validate_dependency_graph_template.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py["校验depends开format<br/>depends_on 条目结构化格式校验<br/>validate_depends_on_format<br/>文件: validators/validate_depends_on_format.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py["校验废弃dependents<br/>废弃文件活跃引用检测<br/>validate_deprecated_dependents<br/>文件: validators<br/>/validate_deprecated_dependents.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_directory_structure_py["校验directorystructure<br/>目录结构校验器，检查项目目录结构是否符合规范，防<br/>目录层级错乱或命名违规。<br/>文件: validators/validate_directory_structure.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_field_ownership_py["校验字段ownership<br/>对标：PS-STD-003 ABS-19~20<br/>（不在非权威文件改权威字段 / 不重复定义<br/>PS-STD-001 字段）<br/>validate_field_ownership<br/>文件: validators/validate_field_ownership.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py["validate门禁yaml<br/>针对 MOD-GATE_ENGINE 门禁体系，检测 YAML<br/>配置文件与 gate_engine.py 代码之间的漂移。<br/>文件: validators/validate_gate_yaml.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_handoff_package_py["校验handoff包<br/>对标：COND-47（HandoffPackage 8<br/>必填字段缺失为条件禁止）<br/>validate_handoff_package<br/>文件: validators/validate_handoff_package.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py["校验接口契约<br/>对标：GOV-MOD-004 IFC-001~007<br/>（模块接口契约策略）<br/>validate_interface_contracts<br/>文件: validators/validate_interface_contracts.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py["校验加载路径完整性<br/>加载路径完整性校验器，检查模块加载路径是否完整有<br/>效，防 import 断链。<br/>文件: validators/validate_load_path_integrity.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_module_schema_py["校验模块模式<br/>对标：GOV-MOD-ALPHA_SIGNAL_DOMAIN INJ-003<br/>（契约已定义）、INJ-004（生命周期状态合法）、<br/>validate_module_schema<br/>文件: validators/validate_module_schema.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py["校验nestedflatdirs<br/>嵌套与扁平目录规范校验器，检查哪些目录应嵌套、哪<br/>些应扁平，防目录结构混乱。<br/>文件: validators/validate_nested_flat_dirs.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py["校验p0模块契约<br/>对标：MAD-005（P0 模块额外条件）<br/>validate_p0_module_contracts<br/>文件: validators/validate_p0_module_contracts.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py["validatestatic清单漂移<br/>GATE-21 静态清单漂移阻断<br/>validate_static_manifest_drift<br/>文件: validators<br/>/validate_static_manifest_drift.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_target_layer_py["校验目标层<br/>对标：target_layer_vocabulary.yaml<br/>v1.0.0——target_layer 字段值体系多真源不一致修复<br/>validate_target_layer<br/>文件: validators/validate_target_layer.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py["校验threeway一致性<br/>对标：AGENTS.md §6.2（原子事务模式）<br/>validate_three_way_consistency<br/>文件: validators<br/>/validate_three_way_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py["validatemdyamlnumber漂移<br/>MD 视图与 YAML SSoT 数字漂移检测闸门<br/>validate_md_yaml_number_drift<br/>文件: yaml_md/validate_md_yaml_number_drift.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py["校验yaml接口uniqueness<br/>YAML 模块接口唯一性闸门<br/>validate_yaml_interface_uniqueness<br/>文件: yaml_md<br/>/validate_yaml_interface_uniqueness.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py["校验yaml摘要<br/>GATE-A 代码↔YAML 对齐的根治层：<br/>v1.0.0 -- 2026-05-03<br/>文件: yaml_md/validate_yaml_summaries.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_check_protected_paths_py["检查protectedpaths<br/>受保护路径写入检查<br/>check_protected_paths<br/>文件: d6_security/check_protected_paths.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_anchor_file_deletion_py["检测anchor文件deletion<br/>锚点文件删除检测<br/>detect_anchor_file_deletion<br/>文件: d6_security/detect_anchor_file_deletion.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_git_dangerous_py["检测Gitdangerous<br/>对标：PS-STD-003 ABS-26（禁止 git push --force<br/>到保护分支）<br/>detect_git_dangerous<br/>文件: d6_security/detect_git_dangerous.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_keywords_in_logs_py["检测keywords入日志<br/>日志输出敏感关键词检测<br/>detect_keywords_in_logs<br/>文件: d6_security/detect_keywords_in_logs.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_permanent_file_deletion_py["检测permanent文件deletion<br/>永久文件删除检测<br/>detect_permanent_file_deletion<br/>文件: d6_security<br/>/detect_permanent_file_deletion.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_secrets_py["检测密钥<br/>密钥/Token/凭证硬编码检测<br/>detect_secrets<br/>文件: d6_security/detect_secrets.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_shell_dangerous_py["检测shelldangerous<br/>对标：PS-STD-003 ABS-38（禁止 rm -rf /<br/>无确认破坏性删除）<br/>detect_shell_dangerous<br/>文件: d6_security/detect_shell_dangerous.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_shell_true_py["检测shelltrue<br/>对标：PS-STD-003 ABS-43（禁止使用 shell=True<br/>执行子进程）<br/>detect_shell_true<br/>文件: d6_security/detect_shell_true.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_threading_lock_py["detectthreading锁<br/>对标：PS-STD-003 ABS-40（禁止<br/>threading.Lock——项目全局异步架构）<br/>detect_threading_lock<br/>文件: d6_security/detect_threading_lock.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_detect_vague_terms_py["检测vagueterms<br/>模糊/不确定术语检测<br/>detect_vague_terms<br/>文件: d6_security/detect_vague_terms.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_retire_tmp_artifacts_py["retiretmpartifacts — tmp/ + logs/ 退役区<br/>retire_tmp_artifacts — tmp/ + logs/ 退役区 TTL<br/>执行器（AI-03 审计 P2/P3 治本）<br/>文件: d6_security/retire_tmp_artifacts.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_run_adversarial_checks_py["run对抗checks<br/>Tier 8 — 每次 CI 运行红蓝对抗：注入混沌漂移 →<br/>蓝队检测 → 裁判对比。<br/>文件: d6_security/run_adversarial_checks.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_scan_runtime_log_secrets_py["扫描运行时日志密钥<br/>'日志输出禁止包含密钥/Token/Secret 值'<br/>scan_runtime_log_secrets<br/>文件: d6_security/scan_runtime_log_secrets.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_scan_secret_leak_py["scan密钥leak<br/>周扫描全库 secret 泄漏，Finding 写 docs<br/>/_working/audit/findings/。<br/>scan_secret_leak<br/>文件: d6_security/scan_secret_leak.py<br/>(生产态 / production)"]
    scripts_governance_d6_security_validate_gate_discipline_py["validate门禁discipline<br/>对标：COND-33~37（门禁级别动态升降/跳级<br/>/生产关闭门禁/AI自签豁免/Pydantic静默吞错）<br/>validate_gate_discipline<br/>文件: d6_security/validate_gate_discipline.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_any_type_inferrer_py["any类型inferrer<br/>裸 Any 类型推断辅助工具 —<br/>#ARCH-ANY-GOVERNANCE-001 Phase 1.<br/>any_type_inferrer<br/>文件: d7_code/any_type_inferrer.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_ai_capability_boundary_py["行为说明<br/>合并三类路径：merge-base...HEAD<br/>（若可解析）、工作区相对 HEAD、暂存区。<br/>check_ai_capability_boundary<br/>文件: d7_code/check_ai_capability_boundary.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_encoding_py["检查encoding<br/>编码合规校验（INJ-007）<br/>check_encoding<br/>文件: d7_code/check_encoding.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_idempotency_py["检查幂等性<br/>幂等性缺失检查（HC-9）<br/>check_idempotency<br/>文件: d7_code/check_idempotency.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_merge_conflict_py["检查合并冲突<br/>合并冲突标记检测（local 替代 external<br/>pre-commit-hooks）<br/>check_merge_conflict<br/>文件: d7_code/check_merge_conflict.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_no_tests_unit_py["检查notestsunit<br/>禁止 tests/unit/ 旧路径重引入检测（local 替代<br/>pygrep）<br/>check_no_tests_unit<br/>文件: d7_code/check_no_tests_unit.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_pit_compliance_py["检查pit合规<br/>对标：GOV-AI-009 HC-10（PIT<br/>铁律绕过——回测代码访问了未来数据）<br/>check_pit_compliance<br/>文件: d7_code/check_pit_compliance.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py["检测absolute路径hardcoding<br/>绝对路径硬编码检测（蓝图 §34.1 操作陷阱）<br/>detect_absolute_path_hardcoding<br/>文件: d7_code/detect_absolute_path_hardcoding.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_direct_llm_calls_py["检测directLLMcalls<br/>裸调 LLM API 检测门禁（GATE-20）<br/>detect_direct_llm_calls<br/>文件: d7_code/detect_direct_llm_calls.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_forward_reference_py["检测前reference<br/>detect_forward_reference — 前向引用检测扫描器。<br/>文件: d7_code/detect_forward_reference.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_missing_encoding_py["检测missingencoding<br/>对标：ABS-24（Python 写文件必须指定<br/>encoding='utf-8'）<br/>detect_missing_encoding<br/>文件: d7_code/detect_missing_encoding.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_private_key_py["检测私有密钥<br/>私钥意外提交检测（local 替代 external<br/>pre-commit-hooks）<br/>detect_private_key<br/>文件: d7_code/detect_private_key.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_pydantic_any_fields_py["检测pydanticanyfields<br/>对标：REC-11（Pydantic 模型禁止 Any 类型字段）<br/>detect_pydantic_any_fields<br/>文件: d7_code/detect_pydantic_any_fields.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_detect_silent_degradation_py["检测silent退化<br/>对标：COND-45（服务降级不写入日志为条件禁止）<br/>detect_silent_degradation<br/>文件: d7_code/detect_silent_degradation.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n06_scope_py["修复n06作用域<br/>N-06 module_id scope 前缀检测修复脚本。<br/>fix_n06_scope<br/>文件: d7_code/fix_n06_scope.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n12_ke_naming_py["N-12 KE 条目命名格式批量修复脚本。<br/>2. 更新所有文件中对旧文件名的引用<br/>fix_n12_ke_naming<br/>文件: d7_code/fix_n12_ke_naming.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n13_snake_case_py["修复n13snakecase<br/>N-13 YAML/JSON/MD 文件名 snake_case<br/>批量修复脚本。<br/>fix_n13_snake_case<br/>文件: d7_code/fix_n13_snake_case.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n14_init_all_py["N-14 初始化.py 缺少 all 批量修复脚本。<br/>py 缺少 __all__ 批量修复脚本<br/>fix_n14_init_all<br/>文件: d7_code/fix_n14_init_all.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_n15_blueprint_path_py["N-15 BLUEPRINT 头部路径不存在批量修复脚本。<br/>1. kebab-case 目录名 → snake_case（57<br/>种路径，2888 个违规）<br/>fix_n15_blueprint_path<br/>文件: d7_code/fix_n15_blueprint_path.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_naming_manual_py["修复naming手册<br/>fix_naming_manual — 手动修复少量命名违规(N-11<br/>/N-10/N-03/N-09/N-16)。<br/>文件: d7_code/fix_naming_manual.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_fix_orphan_exports_py["修复孤儿exports<br/>批量修复孤儿模块导出（RULE-TWO 防线 2 修复器）<br/>fix_orphan_exports<br/>文件: d7_code/fix_orphan_exports.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_rewrite_imports_py["rewrite导入<br/>当文件从 old_path 移到 new_path 时，扫描所有<br/>.py 文件的 import 语句，<br/>rewrite_imports<br/>文件: d7_code/rewrite_imports.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_scan_complexity_py["扫描complexity<br/>全量循环复杂度扫描器 — §5.158 暗债监控<br/>（裁定#214 Phase 4 引入）。<br/>scan_complexity<br/>文件: d7_code/scan_complexity.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_scan_consumers_accuracy_py["扫描消费者accuracy<br/>Phase 1 治本——检测历史漂移（247 个文件）。<br/>scan_consumers_accuracy<br/>文件: d7_code/scan_consumers_accuracy.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_scan_debt_py["架构债务扫描器 — 5.96 维度防御门闸（R67 引入）。<br/>检测 3 类'AI 容易复发的代码异味'：<br/>scan_debt<br/>文件: d7_code/scan_debt.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_contracts_purity_py["validate契约purity<br/>对标：COND-32（contracts<br/>目录放业务逻辑为条件禁止）<br/>validate_contracts_purity<br/>文件: d7_code/validate_contracts_purity.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_docstring_coverage_py["校验docstringcoverage<br/>检查代码里 docstring 覆盖率是否达标，没写<br/>docstring<br/>的模块会被报告，确保每个模块都有功能说明供 AI<br/>理解。<br/>validate_docstring_coverage<br/>文件: d7_code/validate_docstring_coverage.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_fle_action_metadata_py["校验fle行为元数据<br/>对标：COND-44（FLE Action 不记录 effective_from<br/>+ ttl 为条件禁止）<br/>validate_fle_action_metadata<br/>文件: d7_code/validate_fle_action_metadata.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_fle_imports_py["校验fle导入<br/>对标：PS-STD-003 COND-43~45（FLE import 实现类<br/>/ CoVe 异构）<br/>validate_fle_imports<br/>文件: d7_code/validate_fle_imports.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_import_style_py["校验导入style<br/>导入风格一致性校验<br/>validate_import_style<br/>文件: d7_code/validate_import_style.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_init_all_py["校验初始化all.py — 初始化.py all<br/>__init__.py __all__ 完整性校验器，检测有 import<br/>语句的 __init__.py 是否定义了 __all__，骨架包<br/>（空文件）跳过，对标 PEP 8 显式公开接口。<br/>validate_init_all<br/>文件: d7_code/validate_init_all.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_kb_write_provenance_py["validate知识库write溯源<br/>对标：COND-46（知识库写入不传 provenance<br/>为条件禁止）<br/>validate_kb_write_provenance<br/>文件: d7_code/validate_kb_write_provenance.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_python_syntax_py["校验pythonsyntax<br/>对标：AUDIT-09 病根分析（连字符损坏 / 语法错误）<br/>validate_python_syntax<br/>文件: d7_code/validate_python_syntax.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_test_assertion_depth_py["validate测试assertiondepth<br/>测试断言深度校验<br/>validate_test_assertion_depth<br/>文件: d7_code/validate_test_assertion_depth.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_test_coverage_py["validate测试coverage<br/>测试覆盖率治理校验器<br/>validate_test_coverage<br/>文件: d7_code/validate_test_coverage.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_type_annotation_coverage_py["校验类型annotationcoverage<br/>类型注解覆盖率校验<br/>validate_type_annotation_coverage<br/>文件: d7_code<br/>/validate_type_annotation_coverage.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_validate_unused_imports_py["validateunused导入<br/>PS-STD-003 COND-43（代码质量维度补全）<br/>validate_unused_imports<br/>文件: d7_code/validate_unused_imports.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py["全自动注册表同步器<br/>扫描变更→更新所有相关注册表→零孤儿<br/>auto_sync_all_registries<br/>文件: d8_doc_sync/auto_sync_all_registries.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py["detectaiproductsin文档<br/>对标：GOV-DOC-006 §六（AI 生成产物必须写入<br/>.audit_cache/，禁止写入 docs/）<br/>detect_ai_products_in_docs<br/>文件: d8_doc_sync/detect_ai_products_in_docs.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py["检测datedsnapshots<br/>带日期快照文件检测<br/>detect_dated_snapshots<br/>文件: d8_doc_sync/detect_dated_snapshots.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_sync_rule_registry_py["同步规则注册表<br/>Checks that every RULE-ZERO through RULE-N in<br/>.trae/rules/project_rules.md<br/>文件: d8_doc_sync/sync_rule_registry.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_update_progress_py["update进度<br/>从 domain_progress.json 批量更新施工进度.<br/>update_progress<br/>文件: d8_doc_sync/update_progress.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py["validatedocument生命周期<br/>文档生命周期校验<br/>validate_document_lifecycle<br/>文件: d8_doc_sync/validate_document_lifecycle.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_validate_document_ttl_py["校验document存活时间<br/>对标：GOV-DOC-006 §一（TTL 合法值从<br/>ttl_vocabulary.yaml 动态加载）/ §三（LATEST<br/>命名规范）<br/>validate_document_ttl<br/>文件: d8_doc_sync/validate_document_ttl.py<br/>(生产态 / production)"]
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py["检测duplicatednormativelanguage<br/>规范用语重复定义检测<br/>detect_duplicated_normative_language<br/>文件: d9_knowledge<br/>/detect_duplicated_normative_language.py<br/>(生产态 / production)"]
    scripts_governance_d9_knowledge_detect_orphan_documents_py["detect孤儿documents<br/>对标：DOC-008#4（自创建后 > 30 天无任何文件依赖<br/>/引用的文件应审查）<br/>detect_orphan_documents<br/>文件: d9_knowledge/detect_orphan_documents.py<br/>(生产态 / production)"]
    scripts_governance_data_quality_check_tick_duplication_py["check逐笔duplication<br/>tick_data 表真重复检查工具（RULE-DATA-OPS<br/>配套，TRAE-063 §invariants DATA-OPS-INV-002）.<br/>check_tick_duplication<br/>文件: data_quality/check_tick_duplication.py<br/>(生产态 / production)"]
    scripts_governance_extract_decisiongraph_py["提取decisiongraph<br/>决策图按需提取工具，支持 --summary/--layers<br/>/--track 等参数按层与按轨道提取 decisiongraph<br/>子集。<br/>文件: governance/extract_decisiongraph.py<br/>(生产态 / production)"]
    scripts_governance_extract_depgraph_py["提取依赖图<br/>(INVARIANTS) 禁止AI直接Read 157MB<br/>depgraph文件；提取输出必须可被AI安全消费<br/>extract_depgraph<br/>文件: governance/extract_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_generate_decision_graph_py["(INVARIANTS) YAML 是唯一真源; DB 为只读缓存;<br/>同步单向<br/>YAML→DB; 不变量校验前置<br/>generate_decision_graph<br/>文件: governance/generate_decision_graph.py<br/>(生产态 / production)"]
    scripts_governance_generate_project_depgraph_py["生成project依赖图<br/>Scan 结果缓存。线程安全（ThreadPoolExecutor<br/>并发 put）。<br/>文件: governance/generate_project_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_generate_project_path_tree_py["生成project路径树<br/>从磁盘扫描生成路径全景图的tree段<br/>（运营态目录结构）。<br/>generate_project_path_tree<br/>文件: governance/generate_project_path_tree.py<br/>(生产态 / production)"]
    scripts_governance_generators_check_gate_inventory_drift_py["check门禁inventory漂移<br/>commit_gates 模块清单漂移检测（ARCH-055 治本）<br/>check_gate_inventory_drift<br/>文件: generators/check_gate_inventory_drift.py<br/>(生产态 / production)"]
    scripts_governance_generators_fix_module_manifest_layout_py["修复module清单layout<br/>校正治理脚本模块 docstring 与 ``__manifest__``<br/>的顺序<br/>fix_module_manifest_layout<br/>文件: generators/fix_module_manifest_layout.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_gate_registry_py["生成门禁注册表<br/>门禁登记表自动生成器<br/>generate_gate_registry<br/>文件: generators/generate_gate_registry.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_importlinter_py["generators/generate_importlinter<br/>generate_importlinter.py — .importlinter<br/>forbidden_modules 自动生成器<br/>文件: generators/generate_importlinter.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_path_ownership_map_py["生成路径ownershipmap<br/>从蓝图§0.1聚合生成 path_ownership_map.yaml<br/>路径归属声明。<br/>generate_path_ownership_map<br/>文件: generators/generate_path_ownership_map.py<br/>(生产态 / production)"]
    scripts_governance_generators_generate_registry_master_index_py["生成注册表主索引<br/>登记表总索引自动生成器<br/>generate_registry_master_index<br/>文件: generators<br/>/generate_registry_master_index.py<br/>(生产态 / production)"]
    scripts_governance_generators_inject_manifests_py["injectmanifests.py — 清单 批量注入器<br/>从现有的 script_manifest.yaml（手工维护、117<br/>条目）提取元数据，<br/>inject_manifests<br/>文件: generators/inject_manifests.py<br/>(生产态 / production)"]
    scripts_governance_generators_refresh_master_entries_py["refresh主条目<br/>登记表总索引 entries 自动刷新器<br/>refresh_master_entries<br/>文件: generators/refresh_master_entries.py<br/>(生产态 / production)"]
    scripts_governance_generators_sync_audit_protocol_numbers_py["sync审计protocolnumbers<br/>从 SSoT 注册表自动同步审计协议中的硬编码数字。<br/>sync_audit_protocol_numbers<br/>文件: generators/sync_audit_protocol_numbers.py<br/>(生产态 / production)"]
    scripts_governance_git_health_smoke_py["Git健康smoke<br/>AI session 启动时运行的核心工具健康度检查。<br/>git_health_smoke<br/>文件: governance/git_health_smoke.py<br/>(生产态 / production)"]
    scripts_governance_harvest_candidates_from_drafts_py["governance/harvest_candidates_from_drafts<br/>从场外草稿 CSV 抓取候选模块入候选库（一次性<br/>harvest 脚本，不进 generators/）。<br/>文件: governance<br/>/harvest_candidates_from_drafts.py<br/>(生产态 / production)"]
    scripts_governance_meta_arbitrate_findings_py["arbitratefindings.py — Finding 仲裁器（跨脚本冲<br/>Finding 仲裁器（跨脚本冲突解决引擎）<br/>arbitrate_findings<br/>文件: meta/arbitrate_findings.py<br/>(生产态 / production)"]
    scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py["孤儿filewithoutmoduleregistration<br/>Benchmark<br/>测试夹具——未登记的孤儿文件，用于测试孤儿判定器能<br/>否识别未注册文件。<br/>文件: test_fixtures<br/>/orphan_file_without_module_registration.py<br/>(生产态 / production)"]
    scripts_governance_meta_compute_sla_metrics_py["computesla指标<br/>SLA/SLO 指标计算引擎（蓝图 §8.4）<br/>compute_sla_metrics<br/>文件: meta/compute_sla_metrics.py<br/>(生产态 / production)"]
    scripts_governance_meta_create_task_from_finding_py["创建任务from发现<br/>Finding → 任务卡自动创建引擎<br/>create_task_from_finding<br/>文件: meta/create_task_from_finding.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_config_deviation_py["检测配置偏差<br/>配置文件结构完整性检测（蓝图 §28 B65 + B87）<br/>detect_config_deviation<br/>文件: meta/detect_config_deviation.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_fix_oscillation_py["检测修复振荡<br/>自修复振荡检测（蓝图 §28 B64）<br/>detect_fix_oscillation<br/>文件: meta/detect_fix_oscillation.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_hallucinated_packages_py["检测hallucinatedpackages<br/>对标（Slopsquatting 防御）+ Socket.dev 205K<br/>幻觉包检测 + PyPI JSON API。<br/>detect_hallucinated_packages<br/>文件: meta/detect_hallucinated_packages.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_script_divergence_py["检测script散度<br/>脚本实现与蓝图规范分歧检测（蓝图 §27.3 B81）<br/>detect_script_divergence<br/>文件: meta/detect_script_divergence.py<br/>(生产态 / production)"]
    scripts_governance_meta_detect_script_rot_py["检测scriptrot<br/>（脚本静默失效）检测器<br/>detect_script_rot<br/>文件: meta/detect_script_rot.py<br/>(生产态 / production)"]
    scripts_governance_meta_env_check_py["环境检查<br/>环境就绪检查门禁 (Environment Readiness Gate)<br/>env_check<br/>文件: meta/env_check.py<br/>(生产态 / production)"]
    scripts_governance_meta_finding_state_machine_py["finding状态machine<br/>Finding 全生命周期状态机<br/>finding_state_machine<br/>文件: meta/finding_state_machine.py<br/>(生产态 / production)"]
    scripts_governance_meta_gate_engine_selfcheck_py["门禁引擎selfcheck<br/>独立脚本，验证 MOD-GATE_ENGINE Gate Engine<br/>自身的完整性。<br/>文件: meta/gate_engine_selfcheck.py<br/>(生产态 / production)"]
    scripts_governance_meta_governance_watchdog_py["治理watchdog<br/>BLUEPRINT 必须匹配 generate_project_depgraph.py<br/>L2755 正则 ^(MOD-/D-/SH-/SYS-/PLACEHOLDER)<br/>文件: meta/governance_watchdog.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_error_budget_py["管理错误预算<br/>管理可用性 Error Budget 和准确率 Error Budget<br/>的消耗/监控/冻结。<br/>manage_error_budget<br/>文件: meta/manage_error_budget.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_finding_timeseries_py["管理发现timeseries<br/>Finding 时序数据库 + 趋势分析引擎<br/>manage_finding_timeseries<br/>文件: meta/manage_finding_timeseries.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_script_ab_test_py["managescriptab测试<br/>对标（Script A/B 对照）+ Netflix Kayenta 自动<br/>Canary 分析。<br/>manage_script_ab_test<br/>文件: meta/manage_script_ab_test.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_script_retirement_py["管理scriptretirement<br/>脚本退役/废弃生命周期管理<br/>manage_script_retirement<br/>文件: meta/manage_script_retirement.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_shadow_mode_py["manage影子mode<br/>管理新脚本的 Phase1(Shadow)→Phase2(Warn)→Phase3<br/>(Active) 生命周期。<br/>manage_shadow_mode<br/>文件: meta/manage_shadow_mode.py<br/>(生产态 / production)"]
    scripts_governance_meta_mutation_test_post_sync_validator_py["mutation测试postsync校验器<br/>目的：机械注入源码变异到 post_sync_validator.py<br/>的副本，复用<br/>mutation_test_post_sync_validator<br/>文件: meta/mutation_test_post_sync_validator.py<br/>(生产态 / production)"]
    scripts_governance_meta_mutation_test_reconciliation_registry_py["mutation测试对账注册表<br/>目的：机械注入源码变异到<br/>``reconciliation_registry.py`` 的副本，复用<br/>mutation_test_reconciliation_registry<br/>文件: meta<br/>/mutation_test_reconciliation_registry.py<br/>(生产态 / production)"]
    scripts_governance_meta_phase_e_context_check_py["阶段e上下文检查<br/>Phase E: AI context injection verification<br/>script<br/>文件: meta/phase_e_context_check.py<br/>(生产态 / production)"]
    scripts_governance_meta_pre_op_check_py["AI操作前准入控制器 — 写/删文件前的机械门禁检查.<br/>本脚本是 RULE-ZERO~EIGHT 的代码级强制执行层。<br/>pre_op_check<br/>文件: meta/pre_op_check.py<br/>(生产态 / production)"]
    scripts_governance_meta_score_script_effectiveness_py["评分scripteffectiveness<br/>脚本有效性评分（蓝图 §27.12 B90）<br/>score_script_effectiveness<br/>文件: meta/score_script_effectiveness.py<br/>(生产态 / production)"]
    scripts_governance_meta_session_startup_check_py["会话启动检查<br/>Session 冷启动自检 — 运行 Phase 0 全部 14<br/>个检查并输出状态报告.<br/>session_startup_check<br/>文件: meta/session_startup_check.py<br/>(生产态 / production)"]
    scripts_governance_meta_trace_finding_lifecycle_py["追踪发现生命周期<br/>对标（C1→C5 全链路 Tracing）+ OpenTelemetry<br/>distributed tracing 概念。<br/>trace_finding_lifecycle<br/>文件: meta/trace_finding_lifecycle.py<br/>(生产态 / production)"]
    scripts_governance_meta_track_script_costs_py["trackscriptcosts.py — 脚本执行 AI 费用追踪<br/>track_script_costs.py — 脚本执行 AI 费用追踪<br/>文件: meta/track_script_costs.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_automation_boundary_py["validate自动化boundary<br/>自动化边界校验器，检查哪些操作应自动化、哪些应保<br/>留人工，防止越界自动化。<br/>文件: meta/validate_automation_boundary.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_cross_model_consensus_py["校验跨模型共识<br/>多AI模型共识验证引擎<br/>validate_cross_model_consensus<br/>文件: meta/validate_cross_model_consensus.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_dependency_chain_py["校验依赖链<br/>依赖链拓扑顺序验证<br/>validate_dependency_chain<br/>文件: meta/validate_dependency_chain.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_emergency_bypass_log_py["validateemergency绕过日志<br/>应急绕过审计脚本<br/>validate_emergency_bypass_log<br/>文件: meta/validate_emergency_bypass_log.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_end_to_end_benchmark_py["校验结束to结束基准<br/>对标（END-TO-END 基准测试）+ Kayenta Score<br/>Computation。<br/>validate_end_to_end_benchmark<br/>文件: meta/validate_end_to_end_benchmark.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_environment_health_py["校验环境健康<br/>脚本运行环境健康检查<br/>validate_environment_health<br/>文件: meta/validate_environment_health.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_false_negatives_py["校验falsenegatives<br/>维护一个'已知有缺陷的测试用例库'（golden<br/>set），定期验证脚本系统<br/>validate_false_negatives<br/>文件: meta/validate_false_negatives.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_gate_engine_external_py["校验门禁引擎外部<br/>独立的外部验证脚本，从进程外部确认 Gate Engine<br/>未被篡改/损坏。<br/>validate_gate_engine_external<br/>文件: meta/validate_gate_engine_external.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_mutation_testing_py["校验mutationtesting<br/>变异测试引擎（蓝图 §19.2 + B75）<br/>validate_mutation_testing<br/>文件: meta/validate_mutation_testing.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_rule_freshness_py["validate规则freshness<br/>AI Session 注入文件新鲜度检查（蓝图 §22.3 +<br/>B62）<br/>validate_rule_freshness<br/>文件: meta/validate_rule_freshness.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_rules_file_backdoor_py["校验rules文件backdoor<br/>AI 规则文件隐形投毒攻击。<br/>validate_rules_file_backdoor<br/>文件: meta/validate_rules_file_backdoor.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_rules_integrity_py["validaterules完整性<br/>规则文件完整性保护<br/>validate_rules_integrity<br/>文件: meta/validate_rules_integrity.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_script_onboarding_py["校验scriptonboarding<br/>执行 V1-V12 检查，返回通过/失败及逐项结果。<br/>文件: meta/validate_script_onboarding.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_script_provenance_py["validatescript溯源<br/>为每个治理脚本生成和维护起源元数据：<br/>validate_script_provenance<br/>文件: meta/validate_script_provenance.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_script_system_health_py["validatescript系统健康<br/>脚本系统健康自检（Meta 维度 / 第 13 维度）<br/>validate_script_system_health<br/>文件: meta/validate_script_system_health.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_threshold_changes_py["校验阈值changes<br/>阈值变更审计日志<br/>validate_threshold_changes<br/>文件: meta/validate_threshold_changes.py<br/>(生产态 / production)"]
    scripts_governance_meta_validate_trust_tier_py["校验信任层<br/>在 pre_commit 和 CI 中运行，检查当前变更是否与<br/>trust_tier_policy.yaml 定义<br/>validate_trust_tier<br/>文件: meta/validate_trust_tier.py<br/>(生产态 / production)"]
    scripts_governance_meta_verify_reconciliation_registry_py["校验对账注册表<br/>仿 ``post_sync_validator.py`` SSoT<br/>解耦模式），检查 8 项结构/行为不变量，打印<br/>verify_reconciliation_registry<br/>文件: meta/verify_reconciliation_registry.py<br/>(生产态 / production)"]
    scripts_governance_migrate_sqlite_to_pg_migrate_data_py["migrate数据<br/>SQLite → PostgreSQL 运营数据迁移脚本<br/>migrate_data<br/>文件: migrate_sqlite_to_pg/migrate_data.py<br/>(生产态 / production)"]
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py["种子fromyaml<br/>从 YAML 真源灌种子表（5.32.10<br/>治本：种子与迁移拆分）<br/>seed_from_yaml<br/>文件: migrate_sqlite_to_pg/seed_from_yaml.py<br/>(生产态 / production)"]
    scripts_governance_migrate_to_metadata_tables_py["migrateto元数据tables<br/>裁定#209 Stage 2 一次性迁移脚本<br/>migrate_to_metadata_tables<br/>文件: governance/migrate_to_metadata_tables.py<br/>(生产态 / production)"]
    scripts_governance_oneoff_data_domain_audit_query_py["数据域审计查询<br/>数据域设计态排查 - DB 现状查询（Phase<br/>2，只读不写）。<br/>data_domain_audit_query<br/>文件: oneoff/data_domain_audit_query.py<br/>(生产态 / production)"]
    scripts_governance_query_module_panorama_py["查询modulepanorama<br/>模块全景查询入口（四图模块对齐 Step 5）<br/>query_module_panorama<br/>文件: governance/query_module_panorama.py<br/>(生产态 / production)"]
    scripts_governance_register_deferred_modules_py["注册deferredmodules<br/>将42项暂缓模块写入 depgraph<br/>设计态，含3图对齐设计。<br/>register_deferred_modules<br/>文件: governance/register_deferred_modules.py<br/>(生产态 / production)"]
    scripts_governance_repair_concurrent_commit_test_py["并发提交测试<br/>幽灵提交红蓝对抗脚本<br/>concurrent_commit_test<br/>文件: repair/concurrent_commit_test.py<br/>(生产态 / production)"]
    scripts_governance_run_all_py["run_all.py — 脚本系统统一入口脚本<br/>治理包的run_all模块<br/>文件: governance/run_all.py<br/>(生产态 / production)"]
    scripts_governance_run_gate_chain_py["运行门禁链<br/>顺序运行多个门禁脚本，任一失败即整体失败。<br/>run_gate_chain<br/>文件: governance/run_gate_chain.py<br/>(生产态 / production)"]
    scripts_governance_run_silent_failure_regression_py["runsilent故障regression<br/>silent-failure 回归套件一键执行入口<br/>run_silent_failure_regression<br/>文件: governance<br/>/run_silent_failure_regression.py<br/>(生产态 / production)"]
    scripts_governance_session_startup_health_check_py["会话启动健康检查<br/>AI session<br/>启动时运行的核心工具健康度检查。对应裁定  Phase<br/>6<br/>session_startup_health_check<br/>文件: governance/session_startup_health_check.py<br/>(生产态 / production)"]
    scripts_governance_status_py["状态<br/>审计系统状态仪表盘<br/>status<br/>文件: governance/status.py<br/>(生产态 / production)"]
    scripts_governance_verify_sync_integrity_py["校验同步完整性<br/>sync 完整性校验脚本：验证 YAML→DB 同步的一致性。<br/>verify_sync_integrity<br/>文件: governance/verify_sync_integrity.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_blindspot_check_py["VMS 盲点闭合检查器 — MOD-INF-011 · R1(33) + R2(<br/>vms包的vms_blindspot_check模块<br/>文件: vms/vms_blindspot_check.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_build_completion_check_py["vms构建completion检查<br/>vms包的vms_build_completion_check模块<br/>文件: vms/vms_build_completion_check.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_cron_monitor_py["vmscron监控器<br/>vms包的vms_cron_monitor模块<br/>文件: vms/vms_cron_monitor.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_cross_file_check_py["VMS 跨文件内容一致性检查器 — MOD-INF-011 ·<br/>TASK-INF<br/>VMS 跨文件内容一致性检查器，校验 12 个文件中<br/>Collection 列表、嵌入维度（1024d<br/>/512d）、chunk_strategy<br/>路由、导入路径四维度一致性。<br/>vms_cross_file_check<br/>文件: vms/vms_cross_file_check.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_health_check_py["vms健康检查<br/>vms包的vms_health_check模块<br/>文件: vms/vms_health_check.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_migrate_py["VMS Phase 2 数据迁移脚本 — MOD-INF-011<br/>vms包的vms_migrate模块<br/>文件: vms/vms_migrate.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_migration_dry_run_py["vms迁移dry运行<br/>VMS 迁移 dry-run 脚本，预览 unified_memory<br/>topic 到 Collection 的映射，作为 Phase 2<br/>迁移前置检查（R15 缓解）。<br/>vms_migration_dry_run<br/>文件: vms/vms_migration_dry_run.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_phase_rollback_py["vms阶段回滚<br/>vms包的vms_phase_rollback模块<br/>文件: vms/vms_phase_rollback.py<br/>(生产态 / production)"]
    scripts_governance_vms_vms_version_sync_check_py["VMS 版本同步检查器 — MOD-INF-011 · TASK-INF-022<br/>vms包的vms_version_sync_check模块<br/>文件: vms/vms_version_sync_check.py<br/>(生产态 / production)"]
    tests_governance_scripts_governance_test_any_type_inferrer_py["测试anytypeinferrer<br/>裸 Any 检测（与 check_any_abuse.py<br/>算法一致，回归测试）<br/>test_any_type_inferrer<br/>文件: scripts_governance<br/>/test_any_type_inferrer.py<br/>(生产态 / production)"]
    tests_governance_scripts_governance_test_check_canonical_yaml_drift_py["测试check规范yaml漂移<br/>覆盖 5 项断言（A1-A5）的核心场景，每项测 clean<br/>（通过）+ stale（检出）两路：<br/>test_check_canonical_yaml_drift<br/>文件: scripts_governance<br/>/test_check_canonical_yaml_drift.py<br/>(生产态 / production)"]
    tests_governance_scripts_governance_test_check_vocab_hardcode_py["测试checkvocabhardcode<br/>GATE-VOCAB 检测7 单元测试（2026-06-30 治本补全）<br/>test_check_vocab_hardcode<br/>文件: scripts_governance<br/>/test_check_vocab_hardcode.py<br/>(生产态 / production)"]
    tests_governance_scripts_governance_test_pre_write_gate_py["测试prewrite门禁<br/>_check_session_overlap 单元测试（claim<br/>前移协议防线）<br/>test_pre_write_gate<br/>文件: scripts_governance/test_pre_write_gate.py<br/>(生产态 / production)"]
    tests_governance_test_check_blueprint_code_alignment_py["测试检查蓝图代码对齐<br/>隔离 BLUEPRINTS_DIR 和<br/>REPO_ROOT，防止扫描真实项目文件。<br/>文件: governance<br/>/test_check_blueprint_code_alignment.py<br/>(生产态 / production)"]
    docs_01_policies_and_standards_registry_catalogs_scripts_registry_yaml ~~~ scripts_archive_governance_dm106_p2b_verification_py
    scripts_archive_governance_dm106_p2b_verification_py ~~~ scripts_governance_archive_one_off_audit_post_sync_commands_py
    scripts_governance_archive_one_off_audit_post_sync_commands_py ~~~ scripts_governance_archive_one_off_check_exam_case_consistency_py
    scripts_governance_archive_one_off_check_exam_case_consistency_py ~~~ scripts_governance_archive_one_off_create_alignment_tasks_py
    scripts_governance_archive_one_off_create_alignment_tasks_py ~~~ scripts_governance_archive_one_off_dm105_depgraph_triage_py
    scripts_governance_archive_one_off_dm105_depgraph_triage_py ~~~ scripts_governance_archive_one_off_fix_broken_post_sync_py
    scripts_governance_archive_one_off_fix_broken_post_sync_py ~~~ scripts_governance_archive_one_off_list_phase0_tasks_py
    scripts_governance_archive_one_off_list_phase0_tasks_py ~~~ scripts_governance_archive_one_off_phase_a_backup_py
    scripts_governance_archive_one_off_phase_a_backup_py ~~~ scripts_governance_archive_one_off_rename_kebab_to_snake_py
    scripts_governance_archive_one_off_rename_kebab_to_snake_py ~~~ scripts_governance_archive_one_off_rename_whitelist_cleanup_py
    scripts_governance_archive_one_off_rename_whitelist_cleanup_py ~~~ scripts_governance_archive_one_off_test_lock_scenarios_py
    scripts_governance_archive_one_off_test_lock_scenarios_py ~~~ scripts_governance_archive_one_off_verify_final_delivery_py
    scripts_governance_archive_one_off_verify_final_delivery_py ~~~ scripts_governance_archive_one_off_verify_rule_yaml_migration_py
    scripts_governance_archive_one_off_verify_rule_yaml_migration_py ~~~ scripts_governance_archive_prototype_adversarial_log_py
    scripts_governance_archive_prototype_adversarial_log_py ~~~ scripts_governance_archive_prototype_adversarial_sys_master_test_py
    scripts_governance_archive_prototype_adversarial_sys_master_test_py ~~~ scripts_governance_archive_prototype_changelog_py
    scripts_governance_archive_prototype_changelog_py ~~~ scripts_governance_archive_prototype_check_audit_rbac_isolation_py
    scripts_governance_archive_prototype_check_audit_rbac_isolation_py ~~~ scripts_governance_archive_prototype_construction_gate_py
    scripts_governance_archive_prototype_construction_gate_py ~~~ scripts_governance_archive_prototype_generate_asset_index_py
    scripts_governance_archive_prototype_generate_asset_index_py ~~~ scripts_governance_archive_prototype_generate_nav_table_py
    scripts_governance_archive_prototype_generate_nav_table_py ~~~ scripts_governance_archive_prototype_rebuild_audit_index_py
    scripts_governance_archive_prototype_rebuild_audit_index_py ~~~ scripts_governance_archive_prototype_scan_ground_truth_deps_py
    scripts_governance_archive_prototype_scan_ground_truth_deps_py ~~~ scripts_governance_archive_prototype_session_simulator_py
    scripts_governance_archive_prototype_session_simulator_py ~~~ scripts_governance_archive_prototype_sync_blueprint_status_py
    scripts_governance_archive_prototype_sync_blueprint_status_py ~~~ scripts_governance_archive_vms_ri_ri_boundary_check_py
    scripts_governance_archive_vms_ri_ri_boundary_check_py ~~~ scripts_governance_archive_vms_ri_vms_blindspot_check_py
    scripts_governance_archive_vms_ri_vms_blindspot_check_py ~~~ scripts_governance_archive_vms_ri_vms_build_completion_check_py
    scripts_governance_archive_vms_ri_vms_build_completion_check_py ~~~ scripts_governance_archive_vms_ri_vms_cross_file_check_py
    scripts_governance_archive_vms_ri_vms_cross_file_check_py ~~~ scripts_governance_archive_vms_ri_vms_health_check_py
    scripts_governance_archive_vms_ri_vms_health_check_py ~~~ scripts_governance_archive_vms_ri_vms_migrate_py
    scripts_governance_archive_vms_ri_vms_migrate_py ~~~ scripts_governance_archive_vms_ri_vms_migration_dry_run_py
    scripts_governance_archive_vms_ri_vms_migration_dry_run_py ~~~ scripts_governance_archive_vms_ri_vms_phase_rollback_py
    scripts_governance_archive_vms_ri_vms_phase_rollback_py ~~~ scripts_governance_archive_vms_ri_vms_version_sync_check_py
    scripts_governance_archive_vms_ri_vms_version_sync_check_py ~~~ scripts_governance_shared_base_py
    scripts_governance_shared_base_py ~~~ scripts_governance_sync_cleanup_p0_auto_bridged_py
    scripts_governance_sync_cleanup_p0_auto_bridged_py ~~~ scripts_governance_sync_cleanup_p0_ops_pending_py
    scripts_governance_sync_cleanup_p0_ops_pending_py ~~~ scripts_governance_sync_fix_orphan_deps_py
    scripts_governance_sync_fix_orphan_deps_py ~~~ scripts_governance_tasks_list_phase0_tasks_py
    scripts_governance_tasks_list_phase0_tasks_py ~~~ scripts_governance_tasks_task_show_py
    scripts_governance_tasks_task_show_py ~~~ scripts_governance_tasks_task_summary_py
    scripts_governance_tasks_task_summary_py ~~~ scripts_governance_add_deferred_design_edges_py
    scripts_governance_add_deferred_design_edges_py ~~~ scripts_governance_align_battle_map_py
    scripts_governance_align_battle_map_py ~~~ scripts_governance_apply_battle_map_py
    scripts_governance_apply_battle_map_py ~~~ scripts_governance_apply_dataflowgraph_py
    scripts_governance_apply_dataflowgraph_py ~~~ scripts_governance_apply_decisiongraph_py
    scripts_governance_apply_decisiongraph_py ~~~ scripts_governance_apply_depgraph_py
    scripts_governance_apply_depgraph_py ~~~ scripts_governance_architecture_health_dashboard_py
    scripts_governance_architecture_health_dashboard_py ~~~ scripts_governance_ast_import_rewriter_py
    scripts_governance_ast_import_rewriter_py ~~~ scripts_governance_audit_return_contract_usage_py
    scripts_governance_audit_return_contract_usage_py ~~~ scripts_governance_audit_worktree_ops_telemetry_py
    scripts_governance_audit_worktree_ops_telemetry_py ~~~ scripts_governance_check_commit_message_py
    scripts_governance_check_commit_message_py ~~~ scripts_governance_check_ssot_gate_py
    scripts_governance_check_ssot_gate_py ~~~ scripts_governance_d10_performance_collect_system_threads_py
    scripts_governance_d10_performance_collect_system_threads_py ~~~ scripts_governance_d11_compliance_audit_registration_py
    scripts_governance_d11_compliance_audit_registration_py ~~~ scripts_governance_d11_compliance_ci_self_check_py
    scripts_governance_d11_compliance_ci_self_check_py ~~~ scripts_governance_d11_compliance_fix_shared_bypass_py
    scripts_governance_d11_compliance_fix_shared_bypass_py ~~~ scripts_governance_d11_compliance_g9_compliance_check_py
    scripts_governance_d11_compliance_g9_compliance_check_py ~~~ scripts_governance_d11_compliance_task_self_check_py
    scripts_governance_d11_compliance_task_self_check_py ~~~ scripts_governance_d11_compliance_validate_commit_gateway_py
    scripts_governance_d11_compliance_validate_commit_gateway_py ~~~ scripts_governance_d11_compliance_validate_commit_message_py
    scripts_governance_d11_compliance_validate_commit_message_py ~~~ scripts_governance_d11_compliance_validate_exit_codes_py
    scripts_governance_d11_compliance_validate_exit_codes_py ~~~ scripts_governance_d11_compliance_validate_frozen_requirements_py
    scripts_governance_d11_compliance_validate_frozen_requirements_py ~~~ scripts_governance_d11_compliance_validate_manifest_admission_py
    scripts_governance_d11_compliance_validate_manifest_admission_py ~~~ scripts_governance_d11_compliance_validate_no_utf8_bom_py
    scripts_governance_d11_compliance_validate_no_utf8_bom_py ~~~ scripts_governance_d11_compliance_validate_script_naming_py
    scripts_governance_d11_compliance_validate_script_naming_py ~~~ scripts_governance_d11_compliance_validate_script_quality_py
    scripts_governance_d11_compliance_validate_script_quality_py ~~~ scripts_governance_d11_compliance_validate_task_decomposition_bypass_py
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py ~~~ scripts_governance_d11_compliance_validate_vocabulary_coverage_py
    scripts_governance_d11_compliance_validate_vocabulary_coverage_py ~~~ scripts_governance_d11_compliance_verify_audit_integrity_py
    scripts_governance_d11_compliance_verify_audit_integrity_py ~~~ scripts_governance_d11_compliance_verify_schema_health_py
    scripts_governance_d11_compliance_verify_schema_health_py ~~~ scripts_governance_d12_ai_hallucination_check_logger_kwargs_py
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py ~~~ scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py ~~~ scripts_governance_d12_ai_hallucination_validate_session_budget_py
    scripts_governance_d12_ai_hallucination_validate_session_budget_py ~~~ scripts_governance_d12_ai_hallucination_validate_session_gate_check_py
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py ~~~ scripts_governance_d1_structure_archive_drafts_zone_py
    scripts_governance_d1_structure_archive_drafts_zone_py ~~~ scripts_governance_d1_structure_audit_config_format_py
    scripts_governance_d1_structure_audit_config_format_py ~~~ scripts_governance_d1_structure_audit_directory_integrity_py
    scripts_governance_d1_structure_audit_directory_integrity_py ~~~ scripts_governance_d1_structure_audit_directory_scalability_py
    scripts_governance_d1_structure_audit_directory_scalability_py ~~~ scripts_governance_d1_structure_audit_findings_by_scope_py
    scripts_governance_d1_structure_audit_findings_by_scope_py ~~~ scripts_governance_d1_structure_batch_create_index_md_py
    scripts_governance_d1_structure_batch_create_index_md_py ~~~ scripts_governance_d1_structure_cbg_reset_py
    scripts_governance_d1_structure_cbg_reset_py ~~~ scripts_governance_d1_structure_check_directory_contract_py
    scripts_governance_d1_structure_check_directory_contract_py ~~~ scripts_governance_d1_structure_check_handoff_manifests_py
    scripts_governance_d1_structure_check_handoff_manifests_py ~~~ scripts_governance_d1_structure_check_index_integrity_py
    scripts_governance_d1_structure_check_index_integrity_py ~~~ scripts_governance_d1_structure_cleanup_stash_py
    scripts_governance_d1_structure_cleanup_stash_py ~~~ scripts_governance_d1_structure_detect_orphan_py_py
    scripts_governance_d1_structure_detect_orphan_py_py ~~~ scripts_governance_d1_structure_detect_residual_files_py
    scripts_governance_d1_structure_detect_residual_files_py ~~~ scripts_governance_d1_structure_detect_temp_files_py
    scripts_governance_d1_structure_detect_temp_files_py ~~~ scripts_governance_d1_structure_drafts_zone_archiver_py
    scripts_governance_d1_structure_drafts_zone_archiver_py ~~~ scripts_governance_d1_structure_generate_missing_index_md_py
    scripts_governance_d1_structure_generate_missing_index_md_py ~~~ scripts_governance_d1_structure_reset_cbg_py
    scripts_governance_d1_structure_reset_cbg_py ~~~ scripts_governance_d1_structure_run_script_smoke_test_py
    scripts_governance_d1_structure_run_script_smoke_test_py ~~~ scripts_governance_d1_structure_sync_index_from_manifest_py
    scripts_governance_d1_structure_sync_index_from_manifest_py ~~~ scripts_governance_d1_structure_sync_policies_index_py
    scripts_governance_d1_structure_sync_policies_index_py ~~~ scripts_governance_d1_structure_validate_config_integrity_py
    scripts_governance_d1_structure_validate_config_integrity_py ~~~ scripts_governance_d1_structure_validate_d1_output_sanity_py
    scripts_governance_d1_structure_validate_d1_output_sanity_py ~~~ scripts_governance_d1_structure_validate_immutable_core_py
    scripts_governance_d1_structure_validate_immutable_core_py ~~~ scripts_governance_d1_structure_validate_index_reality_py
    scripts_governance_d1_structure_validate_index_reality_py ~~~ scripts_governance_d1_structure_validate_read_before_write_py
    scripts_governance_d1_structure_validate_read_before_write_py ~~~ scripts_governance_d2_links_audit_broken_links_py
    scripts_governance_d2_links_audit_broken_links_py ~~~ scripts_governance_d2_links_detect_relative_references_py
    scripts_governance_d2_links_detect_relative_references_py ~~~ scripts_governance_d3_metadata_auto_generate_index_py
    scripts_governance_d3_metadata_auto_generate_index_py ~~~ scripts_governance_d3_metadata_backfill_doctype_metadata_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py ~~~ scripts_governance_d3_metadata_backfill_ttl_metadata_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py ~~~ scripts_governance_d3_metadata_check_blueprint_compliance_py
    scripts_governance_d3_metadata_check_blueprint_compliance_py ~~~ scripts_governance_d3_metadata_check_frontmatter_metadata_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py ~~~ scripts_governance_d3_metadata_check_module_singlesource_py
    scripts_governance_d3_metadata_check_module_singlesource_py ~~~ scripts_governance_d3_metadata_check_naming_convention_py
    scripts_governance_d3_metadata_check_naming_convention_py ~~~ scripts_governance_d3_metadata_check_registry_consistency_py
    scripts_governance_d3_metadata_check_registry_consistency_py ~~~ scripts_governance_d3_metadata_check_schema_version_writes_py
    scripts_governance_d3_metadata_check_schema_version_writes_py ~~~ scripts_governance_d3_metadata_check_vocab_hardcode_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py ~~~ scripts_governance_d3_metadata_classify_ttl_by_content_py
    scripts_governance_d3_metadata_classify_ttl_by_content_py ~~~ scripts_governance_d3_metadata_deep_content_scanner_py
    scripts_governance_d3_metadata_deep_content_scanner_py ~~~ scripts_governance_d3_metadata_generate_derived_files_py
    scripts_governance_d3_metadata_generate_derived_files_py ~~~ scripts_governance_d3_metadata_generate_rule_catalog_py
    scripts_governance_d3_metadata_generate_rule_catalog_py ~~~ scripts_governance_d3_metadata_migrate_illegal_doctype_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py ~~~ scripts_governance_d3_metadata_validate_architecture_py
    scripts_governance_d3_metadata_validate_architecture_py ~~~ scripts_governance_d3_metadata_validate_blueprint_provenance_py
    scripts_governance_d3_metadata_validate_blueprint_provenance_py ~~~ scripts_governance_d3_metadata_validate_module_id_py
    scripts_governance_d3_metadata_validate_module_id_py ~~~ scripts_governance_d3_metadata_validate_registry_master_index_py
    scripts_governance_d3_metadata_validate_registry_master_index_py ~~~ scripts_governance_d3_metadata_validate_tool_contracts_consistency_py
    scripts_governance_d3_metadata_validate_tool_contracts_consistency_py ~~~ scripts_governance_d4_paths_detect_deprecated_path_writes_py
    scripts_governance_d4_paths_detect_deprecated_path_writes_py ~~~ scripts_governance_d4_paths_detect_excessive_file_moves_py
    scripts_governance_d4_paths_detect_excessive_file_moves_py ~~~ scripts_governance_d4_paths_detect_ruins_references_py
    scripts_governance_d4_paths_detect_ruins_references_py ~~~ scripts_governance_d4_paths_detect_split_delete_ref_commit_py
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py ~~~ scripts_governance_d5_architecture_analyze_change_impact_py
    scripts_governance_d5_architecture_analyze_change_impact_py ~~~ scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py ~~~ scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py ~~~ scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py ~~~ scripts_governance_d5_architecture_audit_agent_spec_py
    scripts_governance_d5_architecture_audit_agent_spec_py ~~~ scripts_governance_d5_architecture_check_budget_health_py
    scripts_governance_d5_architecture_check_budget_health_py ~~~ scripts_governance_d5_architecture_check_drift_e2e_py
    scripts_governance_d5_architecture_check_drift_e2e_py ~~~ scripts_governance_d5_architecture_checkers_check_architecture_gates_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py ~~~ scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py ~~~ scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py ~~~ scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py
    scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py ~~~ scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py ~~~ scripts_governance_d5_architecture_checkers_check_code_duplication_py
    scripts_governance_d5_architecture_checkers_check_code_duplication_py ~~~ scripts_governance_d5_architecture_checkers_check_contract_code_drift_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py ~~~ scripts_governance_d5_architecture_checkers_check_contract_physical_path_py
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py ~~~ scripts_governance_d5_architecture_checkers_check_dependency_direction_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py ~~~ scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py ~~~ scripts_governance_d5_architecture_checkers_check_orphan_outputs_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py ~~~ scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py ~~~ scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py ~~~ scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py ~~~ scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py ~~~ scripts_governance_d5_architecture_checkers_check_vms_ssot_py
    scripts_governance_d5_architecture_checkers_check_vms_ssot_py ~~~ scripts_governance_d5_architecture_dependency_graph_py
    scripts_governance_d5_architecture_dependency_graph_py ~~~ scripts_governance_d5_architecture_detect_causal_conflicts_py
    scripts_governance_d5_architecture_detect_causal_conflicts_py ~~~ scripts_governance_d5_architecture_detect_constraint_violations_py
    scripts_governance_d5_architecture_detect_constraint_violations_py ~~~ scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py ~~~ scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py ~~~ scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py ~~~ scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py ~~~ scripts_governance_d5_architecture_diagnose_depgraph_py
    scripts_governance_d5_architecture_diagnose_depgraph_py ~~~ scripts_governance_d5_architecture_generators_align_panoramas_py
    scripts_governance_d5_architecture_generators_align_panoramas_py ~~~ scripts_governance_d5_architecture_generators_generate_asset_catalog_py
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py ~~~ scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py
    scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py ~~~ scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py ~~~ scripts_governance_d5_architecture_generators_generate_candidate_module_report_py
    scripts_governance_d5_architecture_generators_generate_candidate_module_report_py ~~~ scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py ~~~ scripts_governance_d5_architecture_generators_generate_contract_catalog_py
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py ~~~ scripts_governance_d5_architecture_generators_generate_contracts_py
    scripts_governance_d5_architecture_generators_generate_contracts_py ~~~ scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py ~~~ scripts_governance_d5_architecture_generators_generate_data_inventory_py
    scripts_governance_d5_architecture_generators_generate_data_inventory_py ~~~ scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py ~~~ scripts_governance_d5_architecture_generators_generate_decision_diagram_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py ~~~ scripts_governance_d5_architecture_generators_generate_panorama_registry_py
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py ~~~ scripts_governance_d5_architecture_generators_generate_policies_py
    scripts_governance_d5_architecture_generators_generate_policies_py ~~~ scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py
    scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py ~~~ scripts_governance_d5_architecture_pre_delete_safety_check_py
    scripts_governance_d5_architecture_pre_delete_safety_check_py ~~~ scripts_governance_d5_architecture_pre_write_gate_py
    scripts_governance_d5_architecture_pre_write_gate_py ~~~ scripts_governance_d5_architecture_syncers_archive_rationale_log_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py ~~~ scripts_governance_d5_architecture_syncers_merge_readme_to_index_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py ~~~ scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py ~~~ scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py ~~~ scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py ~~~ scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py ~~~ scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py ~~~ scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py ~~~ scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py ~~~ scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py ~~~ scripts_governance_d5_architecture_validators_validate_arch_review_gate_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py ~~~ scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py ~~~ scripts_governance_d5_architecture_validators_validate_autonomy_gate_py
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py ~~~ scripts_governance_d5_architecture_validators_validate_b_track_packages_py
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py ~~~ scripts_governance_d5_architecture_validators_validate_blind_spot_status_py
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py ~~~ scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py ~~~ scripts_governance_d5_architecture_validators_validate_cross_references_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py ~~~ scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py ~~~ scripts_governance_d5_architecture_validators_validate_depends_on_format_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py ~~~ scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py ~~~ scripts_governance_d5_architecture_validators_validate_directory_structure_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py ~~~ scripts_governance_d5_architecture_validators_validate_field_ownership_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py ~~~ scripts_governance_d5_architecture_validators_validate_gate_yaml_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py ~~~ scripts_governance_d5_architecture_validators_validate_handoff_package_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py ~~~ scripts_governance_d5_architecture_validators_validate_interface_contracts_py
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py ~~~ scripts_governance_d5_architecture_validators_validate_load_path_integrity_py
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py ~~~ scripts_governance_d5_architecture_validators_validate_module_schema_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py ~~~ scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py ~~~ scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py ~~~ scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py ~~~ scripts_governance_d5_architecture_validators_validate_target_layer_py
    scripts_governance_d5_architecture_validators_validate_target_layer_py ~~~ scripts_governance_d5_architecture_validators_validate_three_way_consistency_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py ~~~ scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py ~~~ scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py ~~~ scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py ~~~ scripts_governance_d6_security_check_protected_paths_py
    scripts_governance_d6_security_check_protected_paths_py ~~~ scripts_governance_d6_security_detect_anchor_file_deletion_py
    scripts_governance_d6_security_detect_anchor_file_deletion_py ~~~ scripts_governance_d6_security_detect_git_dangerous_py
    scripts_governance_d6_security_detect_git_dangerous_py ~~~ scripts_governance_d6_security_detect_keywords_in_logs_py
    scripts_governance_d6_security_detect_keywords_in_logs_py ~~~ scripts_governance_d6_security_detect_permanent_file_deletion_py
    scripts_governance_d6_security_detect_permanent_file_deletion_py ~~~ scripts_governance_d6_security_detect_secrets_py
    scripts_governance_d6_security_detect_secrets_py ~~~ scripts_governance_d6_security_detect_shell_dangerous_py
    scripts_governance_d6_security_detect_shell_dangerous_py ~~~ scripts_governance_d6_security_detect_shell_true_py
    scripts_governance_d6_security_detect_shell_true_py ~~~ scripts_governance_d6_security_detect_threading_lock_py
    scripts_governance_d6_security_detect_threading_lock_py ~~~ scripts_governance_d6_security_detect_vague_terms_py
    scripts_governance_d6_security_detect_vague_terms_py ~~~ scripts_governance_d6_security_retire_tmp_artifacts_py
    scripts_governance_d6_security_retire_tmp_artifacts_py ~~~ scripts_governance_d6_security_run_adversarial_checks_py
    scripts_governance_d6_security_run_adversarial_checks_py ~~~ scripts_governance_d6_security_scan_runtime_log_secrets_py
    scripts_governance_d6_security_scan_runtime_log_secrets_py ~~~ scripts_governance_d6_security_scan_secret_leak_py
    scripts_governance_d6_security_scan_secret_leak_py ~~~ scripts_governance_d6_security_validate_gate_discipline_py
    scripts_governance_d6_security_validate_gate_discipline_py ~~~ scripts_governance_d7_code_any_type_inferrer_py
    scripts_governance_d7_code_any_type_inferrer_py ~~~ scripts_governance_d7_code_check_ai_capability_boundary_py
    scripts_governance_d7_code_check_ai_capability_boundary_py ~~~ scripts_governance_d7_code_check_encoding_py
    scripts_governance_d7_code_check_encoding_py ~~~ scripts_governance_d7_code_check_idempotency_py
    scripts_governance_d7_code_check_idempotency_py ~~~ scripts_governance_d7_code_check_merge_conflict_py
    scripts_governance_d7_code_check_merge_conflict_py ~~~ scripts_governance_d7_code_check_no_tests_unit_py
    scripts_governance_d7_code_check_no_tests_unit_py ~~~ scripts_governance_d7_code_check_pit_compliance_py
    scripts_governance_d7_code_check_pit_compliance_py ~~~ scripts_governance_d7_code_detect_absolute_path_hardcoding_py
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py ~~~ scripts_governance_d7_code_detect_direct_llm_calls_py
    scripts_governance_d7_code_detect_direct_llm_calls_py ~~~ scripts_governance_d7_code_detect_forward_reference_py
    scripts_governance_d7_code_detect_forward_reference_py ~~~ scripts_governance_d7_code_detect_missing_encoding_py
    scripts_governance_d7_code_detect_missing_encoding_py ~~~ scripts_governance_d7_code_detect_private_key_py
    scripts_governance_d7_code_detect_private_key_py ~~~ scripts_governance_d7_code_detect_pydantic_any_fields_py
    scripts_governance_d7_code_detect_pydantic_any_fields_py ~~~ scripts_governance_d7_code_detect_silent_degradation_py
    scripts_governance_d7_code_detect_silent_degradation_py ~~~ scripts_governance_d7_code_fix_n06_scope_py
    scripts_governance_d7_code_fix_n06_scope_py ~~~ scripts_governance_d7_code_fix_n12_ke_naming_py
    scripts_governance_d7_code_fix_n12_ke_naming_py ~~~ scripts_governance_d7_code_fix_n13_snake_case_py
    scripts_governance_d7_code_fix_n13_snake_case_py ~~~ scripts_governance_d7_code_fix_n14_init_all_py
    scripts_governance_d7_code_fix_n14_init_all_py ~~~ scripts_governance_d7_code_fix_n15_blueprint_path_py
    scripts_governance_d7_code_fix_n15_blueprint_path_py ~~~ scripts_governance_d7_code_fix_naming_manual_py
    scripts_governance_d7_code_fix_naming_manual_py ~~~ scripts_governance_d7_code_fix_orphan_exports_py
    scripts_governance_d7_code_fix_orphan_exports_py ~~~ scripts_governance_d7_code_rewrite_imports_py
    scripts_governance_d7_code_rewrite_imports_py ~~~ scripts_governance_d7_code_scan_complexity_py
    scripts_governance_d7_code_scan_complexity_py ~~~ scripts_governance_d7_code_scan_consumers_accuracy_py
    scripts_governance_d7_code_scan_consumers_accuracy_py ~~~ scripts_governance_d7_code_scan_debt_py
    scripts_governance_d7_code_scan_debt_py ~~~ scripts_governance_d7_code_validate_contracts_purity_py
    scripts_governance_d7_code_validate_contracts_purity_py ~~~ scripts_governance_d7_code_validate_docstring_coverage_py
    scripts_governance_d7_code_validate_docstring_coverage_py ~~~ scripts_governance_d7_code_validate_fle_action_metadata_py
    scripts_governance_d7_code_validate_fle_action_metadata_py ~~~ scripts_governance_d7_code_validate_fle_imports_py
    scripts_governance_d7_code_validate_fle_imports_py ~~~ scripts_governance_d7_code_validate_import_style_py
    scripts_governance_d7_code_validate_import_style_py ~~~ scripts_governance_d7_code_validate_init_all_py
    scripts_governance_d7_code_validate_init_all_py ~~~ scripts_governance_d7_code_validate_kb_write_provenance_py
    scripts_governance_d7_code_validate_kb_write_provenance_py ~~~ scripts_governance_d7_code_validate_python_syntax_py
    scripts_governance_d7_code_validate_python_syntax_py ~~~ scripts_governance_d7_code_validate_test_assertion_depth_py
    scripts_governance_d7_code_validate_test_assertion_depth_py ~~~ scripts_governance_d7_code_validate_test_coverage_py
    scripts_governance_d7_code_validate_test_coverage_py ~~~ scripts_governance_d7_code_validate_type_annotation_coverage_py
    scripts_governance_d7_code_validate_type_annotation_coverage_py ~~~ scripts_governance_d7_code_validate_unused_imports_py
    scripts_governance_d7_code_validate_unused_imports_py ~~~ scripts_governance_d8_doc_sync_auto_sync_all_registries_py
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py ~~~ scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py ~~~ scripts_governance_d8_doc_sync_detect_dated_snapshots_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py ~~~ scripts_governance_d8_doc_sync_sync_rule_registry_py
    scripts_governance_d8_doc_sync_sync_rule_registry_py ~~~ scripts_governance_d8_doc_sync_update_progress_py
    scripts_governance_d8_doc_sync_update_progress_py ~~~ scripts_governance_d8_doc_sync_validate_document_lifecycle_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py ~~~ scripts_governance_d8_doc_sync_validate_document_ttl_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py ~~~ scripts_governance_d9_knowledge_detect_duplicated_normative_language_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py ~~~ scripts_governance_d9_knowledge_detect_orphan_documents_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py ~~~ scripts_governance_data_quality_check_tick_duplication_py
    scripts_governance_data_quality_check_tick_duplication_py ~~~ scripts_governance_extract_decisiongraph_py
    scripts_governance_extract_decisiongraph_py ~~~ scripts_governance_extract_depgraph_py
    scripts_governance_extract_depgraph_py ~~~ scripts_governance_generate_decision_graph_py
    scripts_governance_generate_decision_graph_py ~~~ scripts_governance_generate_project_depgraph_py
    scripts_governance_generate_project_depgraph_py ~~~ scripts_governance_generate_project_path_tree_py
    scripts_governance_generate_project_path_tree_py ~~~ scripts_governance_generators_check_gate_inventory_drift_py
    scripts_governance_generators_check_gate_inventory_drift_py ~~~ scripts_governance_generators_fix_module_manifest_layout_py
    scripts_governance_generators_fix_module_manifest_layout_py ~~~ scripts_governance_generators_generate_gate_registry_py
    scripts_governance_generators_generate_gate_registry_py ~~~ scripts_governance_generators_generate_importlinter_py
    scripts_governance_generators_generate_importlinter_py ~~~ scripts_governance_generators_generate_path_ownership_map_py
    scripts_governance_generators_generate_path_ownership_map_py ~~~ scripts_governance_generators_generate_registry_master_index_py
    scripts_governance_generators_generate_registry_master_index_py ~~~ scripts_governance_generators_inject_manifests_py
    scripts_governance_generators_inject_manifests_py ~~~ scripts_governance_generators_refresh_master_entries_py
    scripts_governance_generators_refresh_master_entries_py ~~~ scripts_governance_generators_sync_audit_protocol_numbers_py
    scripts_governance_generators_sync_audit_protocol_numbers_py ~~~ scripts_governance_git_health_smoke_py
    scripts_governance_git_health_smoke_py ~~~ scripts_governance_harvest_candidates_from_drafts_py
    scripts_governance_harvest_candidates_from_drafts_py ~~~ scripts_governance_meta_arbitrate_findings_py
    scripts_governance_meta_arbitrate_findings_py ~~~ scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py
    scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py ~~~ scripts_governance_meta_compute_sla_metrics_py
    scripts_governance_meta_compute_sla_metrics_py ~~~ scripts_governance_meta_create_task_from_finding_py
    scripts_governance_meta_create_task_from_finding_py ~~~ scripts_governance_meta_detect_config_deviation_py
    scripts_governance_meta_detect_config_deviation_py ~~~ scripts_governance_meta_detect_fix_oscillation_py
    scripts_governance_meta_detect_fix_oscillation_py ~~~ scripts_governance_meta_detect_hallucinated_packages_py
    scripts_governance_meta_detect_hallucinated_packages_py ~~~ scripts_governance_meta_detect_script_divergence_py
    scripts_governance_meta_detect_script_divergence_py ~~~ scripts_governance_meta_detect_script_rot_py
    scripts_governance_meta_detect_script_rot_py ~~~ scripts_governance_meta_env_check_py
    scripts_governance_meta_env_check_py ~~~ scripts_governance_meta_finding_state_machine_py
    scripts_governance_meta_finding_state_machine_py ~~~ scripts_governance_meta_gate_engine_selfcheck_py
    scripts_governance_meta_gate_engine_selfcheck_py ~~~ scripts_governance_meta_governance_watchdog_py
    scripts_governance_meta_governance_watchdog_py ~~~ scripts_governance_meta_manage_error_budget_py
    scripts_governance_meta_manage_error_budget_py ~~~ scripts_governance_meta_manage_finding_timeseries_py
    scripts_governance_meta_manage_finding_timeseries_py ~~~ scripts_governance_meta_manage_script_ab_test_py
    scripts_governance_meta_manage_script_ab_test_py ~~~ scripts_governance_meta_manage_script_retirement_py
    scripts_governance_meta_manage_script_retirement_py ~~~ scripts_governance_meta_manage_shadow_mode_py
    scripts_governance_meta_manage_shadow_mode_py ~~~ scripts_governance_meta_mutation_test_post_sync_validator_py
    scripts_governance_meta_mutation_test_post_sync_validator_py ~~~ scripts_governance_meta_mutation_test_reconciliation_registry_py
    scripts_governance_meta_mutation_test_reconciliation_registry_py ~~~ scripts_governance_meta_phase_e_context_check_py
    scripts_governance_meta_phase_e_context_check_py ~~~ scripts_governance_meta_pre_op_check_py
    scripts_governance_meta_pre_op_check_py ~~~ scripts_governance_meta_score_script_effectiveness_py
    scripts_governance_meta_score_script_effectiveness_py ~~~ scripts_governance_meta_session_startup_check_py
    scripts_governance_meta_session_startup_check_py ~~~ scripts_governance_meta_trace_finding_lifecycle_py
    scripts_governance_meta_trace_finding_lifecycle_py ~~~ scripts_governance_meta_track_script_costs_py
    scripts_governance_meta_track_script_costs_py ~~~ scripts_governance_meta_validate_automation_boundary_py
    scripts_governance_meta_validate_automation_boundary_py ~~~ scripts_governance_meta_validate_cross_model_consensus_py
    scripts_governance_meta_validate_cross_model_consensus_py ~~~ scripts_governance_meta_validate_dependency_chain_py
    scripts_governance_meta_validate_dependency_chain_py ~~~ scripts_governance_meta_validate_emergency_bypass_log_py
    scripts_governance_meta_validate_emergency_bypass_log_py ~~~ scripts_governance_meta_validate_end_to_end_benchmark_py
    scripts_governance_meta_validate_end_to_end_benchmark_py ~~~ scripts_governance_meta_validate_environment_health_py
    scripts_governance_meta_validate_environment_health_py ~~~ scripts_governance_meta_validate_false_negatives_py
    scripts_governance_meta_validate_false_negatives_py ~~~ scripts_governance_meta_validate_gate_engine_external_py
    scripts_governance_meta_validate_gate_engine_external_py ~~~ scripts_governance_meta_validate_mutation_testing_py
    scripts_governance_meta_validate_mutation_testing_py ~~~ scripts_governance_meta_validate_rule_freshness_py
    scripts_governance_meta_validate_rule_freshness_py ~~~ scripts_governance_meta_validate_rules_file_backdoor_py
    scripts_governance_meta_validate_rules_file_backdoor_py ~~~ scripts_governance_meta_validate_rules_integrity_py
    scripts_governance_meta_validate_rules_integrity_py ~~~ scripts_governance_meta_validate_script_onboarding_py
    scripts_governance_meta_validate_script_onboarding_py ~~~ scripts_governance_meta_validate_script_provenance_py
    scripts_governance_meta_validate_script_provenance_py ~~~ scripts_governance_meta_validate_script_system_health_py
    scripts_governance_meta_validate_script_system_health_py ~~~ scripts_governance_meta_validate_threshold_changes_py
    scripts_governance_meta_validate_threshold_changes_py ~~~ scripts_governance_meta_validate_trust_tier_py
    scripts_governance_meta_validate_trust_tier_py ~~~ scripts_governance_meta_verify_reconciliation_registry_py
    scripts_governance_meta_verify_reconciliation_registry_py ~~~ scripts_governance_migrate_sqlite_to_pg_migrate_data_py
    scripts_governance_migrate_sqlite_to_pg_migrate_data_py ~~~ scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py ~~~ scripts_governance_migrate_to_metadata_tables_py
    scripts_governance_migrate_to_metadata_tables_py ~~~ scripts_governance_oneoff_data_domain_audit_query_py
    scripts_governance_oneoff_data_domain_audit_query_py ~~~ scripts_governance_query_module_panorama_py
    scripts_governance_query_module_panorama_py ~~~ scripts_governance_register_deferred_modules_py
    scripts_governance_register_deferred_modules_py ~~~ scripts_governance_repair_concurrent_commit_test_py
    scripts_governance_repair_concurrent_commit_test_py ~~~ scripts_governance_run_all_py
    scripts_governance_run_all_py ~~~ scripts_governance_run_gate_chain_py
    scripts_governance_run_gate_chain_py ~~~ scripts_governance_run_silent_failure_regression_py
    scripts_governance_run_silent_failure_regression_py ~~~ scripts_governance_session_startup_health_check_py
    scripts_governance_session_startup_health_check_py ~~~ scripts_governance_status_py
    scripts_governance_status_py ~~~ scripts_governance_verify_sync_integrity_py
    scripts_governance_verify_sync_integrity_py ~~~ scripts_governance_vms_vms_blindspot_check_py
    scripts_governance_vms_vms_blindspot_check_py ~~~ scripts_governance_vms_vms_build_completion_check_py
    scripts_governance_vms_vms_build_completion_check_py ~~~ scripts_governance_vms_vms_cron_monitor_py
    scripts_governance_vms_vms_cron_monitor_py ~~~ scripts_governance_vms_vms_cross_file_check_py
    scripts_governance_vms_vms_cross_file_check_py ~~~ scripts_governance_vms_vms_health_check_py
    scripts_governance_vms_vms_health_check_py ~~~ scripts_governance_vms_vms_migrate_py
    scripts_governance_vms_vms_migrate_py ~~~ scripts_governance_vms_vms_migration_dry_run_py
    scripts_governance_vms_vms_migration_dry_run_py ~~~ scripts_governance_vms_vms_phase_rollback_py
    scripts_governance_vms_vms_phase_rollback_py ~~~ scripts_governance_vms_vms_version_sync_check_py
    scripts_governance_vms_vms_version_sync_check_py ~~~ tests_governance_scripts_governance_test_any_type_inferrer_py
    tests_governance_scripts_governance_test_any_type_inferrer_py ~~~ tests_governance_scripts_governance_test_check_canonical_yaml_drift_py
    tests_governance_scripts_governance_test_check_canonical_yaml_drift_py ~~~ tests_governance_scripts_governance_test_check_vocab_hardcode_py
    tests_governance_scripts_governance_test_check_vocab_hardcode_py ~~~ tests_governance_scripts_governance_test_pre_write_gate_py
    tests_governance_scripts_governance_test_pre_write_gate_py ~~~ tests_governance_test_check_blueprint_code_alignment_py
    scripts_governance_archive_prototype_audit_domain_nodes_py["审计域节点<br/>P0-4升级：4类检测<br/>（跨域违规+容量超限+孤儿节点+层级违规）<br/>文件: prototype/audit_domain_nodes.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_ri_build_completion_check_py["ri构建completion检查<br/>蓝图 §7 · v5.0.1 · 验证 15 RI 模块 +<br/>Cross-Layer 依赖完整性<br/>ri_build_completion_check<br/>文件: vms_ri/ri_build_completion_check.py<br/>(生产态 / production)"]
    scripts_governance_shared_frontmatter_py["文件头部格式解析 SSoT（Single Source of Truth）<br/>6 种文件头部格式的统一解析入口（对标 trae_047<br/>GOV-ENG-002）：<br/>frontmatter<br/>文件: _shared/frontmatter.py<br/>(生产态 / production)"]
    scripts_governance_shared_libcst_docstring_adder_py["LibCSTdocstring添加器<br/>提供leaveModule等方法<br/>文件: _shared/libcst_docstring_adder.py<br/>(生产态 / production)"]
    scripts_governance_shared_module_translation_loader_py["moduletranslation加载器<br/>模块级翻译共享加载器（SSoT 真源）<br/>module_translation_loader<br/>文件: _shared/module_translation_loader.py<br/>(生产态 / production)"]
    scripts_governance_shared_registry_entry_count_py["注册表条目数量<br/>登记表主条目计数——与<br/>generate_registry_master_index 单一真源对齐。<br/>registry_entry_count<br/>文件: _shared/registry_entry_count.py<br/>(生产态 / production)"]
    scripts_governance_shared_terminology_loader_py["术语加载器<br/>架构文档术语词汇表共享加载器（SSoT 真源）<br/>terminology_loader<br/>文件: _shared/terminology_loader.py<br/>(生产态 / production)"]
    scripts_governance_shared_yaml_utils_py["yaml工具<br/>YAML 文件加载共享工具<br/>yaml_utils<br/>文件: _shared/yaml_utils.py<br/>(生产态 / production)"]
    scripts_governance_sync_check_p0_status_py["检查p0状态<br/>P0 优先级任务状态检查器，扫描任务仓库统计 P0<br/>级任务的待办与完成情况，为治理同步提供 P0<br/>状态快照。<br/>文件: _sync/check_p0_status.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_validate_module_id_naming_py["校验模块idnaming<br/>module_id / domain_id / submodule_id<br/>格式校验真源（裁定#208 双轨制 + R2 治本修订）<br/>validate_module_id_naming<br/>文件: d3_metadata/validate_module_id_naming.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_generators_common_py["生成器公共工具（向内收：消除重复）。<br/>当前提供 cleanup_stale_files<br/>()——治本修复'生成器只增不删'问题。<br/>_common<br/>文件: generators/_common.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_any_abuse_py["类型注解 Any 滥用扫描器 — 5.145 维度防御门闸<br/>（R70 引入，#AR<br/>CH-ANY-GOVERNANCE-001 Phase 3 升级为 commit<br/>阻断）<br/>check_any_abuse<br/>文件: d7_code/check_any_abuse.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_audit_rename_completeness_py["审计renamecompleteness<br/>改名完整性审计（裁定#207 R1）。<br/>audit_rename_completeness<br/>文件: d8_doc_sync/audit_rename_completeness.py<br/>(生产态 / production)"]
    scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py["同步yamlto依赖图<br/>(INVARIANTS) YAML→DB单向同步; 27项同步; try<br/>/finally恢复触发器<br/>sync_yaml_to_depgraph<br/>文件: d8_doc_sync/sync_yaml_to_depgraph.py<br/>(生产态 / production)"]
    scripts_governance_meta_concurrency_py["并发<br/>L0 全局进程锁——基于 PID 文件的跨进程互斥锁。<br/>文件: meta/_concurrency.py<br/>(生产态 / production)"]
    scripts_governance_meta_backup_runtime_state_py["备份运行时状态<br/>运行时状态备份（蓝图 §33 灾备）<br/>backup_runtime_state<br/>文件: meta/backup_runtime_state.py<br/>(生产态 / production)"]
    scripts_governance_meta_benchmark_test_fixtures_bad_imports_py["无效导入<br/>（bad_imports.py）<br/>文件: test_fixtures/bad_imports.py<br/>(生产态 / production)"]
    scripts_governance_meta_manage_baseline_py["管理基线<br/>保存/加载/对比 Finding<br/>基线快照，将当前扫描结果与上次 approved<br/>baseline 对比，<br/>manage_baseline<br/>文件: meta/manage_baseline.py<br/>(生产态 / production)"]
    scripts_governance_sync_panorama_module_py["同步panorama模块<br/>四图模块同步引擎<br/>sync_panorama_module<br/>文件: governance/sync_panorama_module.py<br/>(生产态 / production)"]
    scripts_governance_archive_prototype_audit_domain_nodes_py ~~~ scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_ri_build_completion_check_py ~~~ scripts_governance_shared_frontmatter_py
    scripts_governance_shared_frontmatter_py ~~~ scripts_governance_shared_libcst_docstring_adder_py
    scripts_governance_shared_libcst_docstring_adder_py ~~~ scripts_governance_shared_module_translation_loader_py
    scripts_governance_shared_module_translation_loader_py ~~~ scripts_governance_shared_registry_entry_count_py
    scripts_governance_shared_registry_entry_count_py ~~~ scripts_governance_shared_terminology_loader_py
    scripts_governance_shared_terminology_loader_py ~~~ scripts_governance_shared_yaml_utils_py
    scripts_governance_shared_yaml_utils_py ~~~ scripts_governance_sync_check_p0_status_py
    scripts_governance_sync_check_p0_status_py ~~~ scripts_governance_d3_metadata_validate_module_id_naming_py
    scripts_governance_d3_metadata_validate_module_id_naming_py ~~~ scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_common_py ~~~ scripts_governance_d7_code_check_any_abuse_py
    scripts_governance_d7_code_check_any_abuse_py ~~~ scripts_governance_d8_doc_sync_audit_rename_completeness_py
    scripts_governance_d8_doc_sync_audit_rename_completeness_py ~~~ scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py
    scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py ~~~ scripts_governance_meta_concurrency_py
    scripts_governance_meta_concurrency_py ~~~ scripts_governance_meta_backup_runtime_state_py
    scripts_governance_meta_backup_runtime_state_py ~~~ scripts_governance_meta_benchmark_test_fixtures_bad_imports_py
    scripts_governance_meta_benchmark_test_fixtures_bad_imports_py ~~~ scripts_governance_meta_manage_baseline_py
    scripts_governance_meta_manage_baseline_py ~~~ scripts_governance_sync_panorama_module_py
    scripts_governance_archive_vms_ri_vms_cron_monitor_py["vmscron监控器<br/>vms ri包的vms_cron_monitor模块<br/>文件: vms_ri/vms_cron_monitor.py<br/>(生产态 / production)"]
    scripts_governance_shared_encoding_py["encoding.py — UTF-8 编码安全工具<br/>UTF-8 编码安全工具，统一文件读写编码标准，防止<br/>Windows 下 GBK 与 UTF-8 混用导致中文乱码。<br/>文件: _shared/encoding.py<br/>(生产态 / production)"]
    scripts_governance_shared_file_utils_py["文件工具<br/>原子写入共享工具<br/>file_utils<br/>文件: _shared/file_utils.py<br/>(生产态 / production)"]
    scripts_governance_shared_thresholds_py["thresholds.py — 阈值集中配置加载器<br/>shared包的thresholds模块<br/>文件: _shared/thresholds.py<br/>(生产态 / production)"]
    scripts_governance_shared_walk_py["walk.py — 目录遍历共享工具<br/>shared包的walk模块<br/>文件: _shared/walk.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py["蓝图frontmatter对账器<br/>蓝图 frontmatter 核心字段对齐（ARCH-056 Phase<br/>3）<br/>blueprint_frontmatter_reconciler<br/>文件: syncers<br/>/blueprint_frontmatter_reconciler.py<br/>(生产态 / production)"]
    scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py["incomplete模块<br/>Benchmark<br/>测试夹具——故意不完整的模块，用于测试检测器能否识<br/>别不合规模块。<br/>文件: test_fixtures/incomplete_module.py<br/>(生产态 / production)"]
    scripts_governance_archive_vms_ri_vms_cron_monitor_py ~~~ scripts_governance_shared_encoding_py
    scripts_governance_shared_encoding_py ~~~ scripts_governance_shared_file_utils_py
    scripts_governance_shared_file_utils_py ~~~ scripts_governance_shared_thresholds_py
    scripts_governance_shared_thresholds_py ~~~ scripts_governance_shared_walk_py
    scripts_governance_shared_walk_py ~~~ scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py ~~~ scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py
    scripts_governance_shared_constants_py["常量<br/>审计脚本共享常量<br/>constants<br/>文件: _shared/constants.py<br/>(生产态 / production)"]
    scripts_governance_d5_architecture_panorama_common_py["panorama通用<br/>四图投票共享工具（ARCH-056 引擎加固）<br/>panorama_common<br/>文件: d5_architecture/panorama_common.py<br/>(生产态 / production)"]
    scripts_governance_shared_constants_py ~~~ scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_apply_battle_map_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_align_battle_map_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_align_battle_map_py -->|导入依赖 / import_depends| scripts_governance_shared_module_translation_loader_py
    scripts_governance_apply_dataflowgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_sync_panorama_module_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_d3_metadata_validate_module_id_naming_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_d8_doc_sync_audit_rename_completeness_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_meta_backup_runtime_state_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_apply_decisiongraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_check_commit_message_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_extract_decisiongraph_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_ast_import_rewriter_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_decision_graph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_decision_graph_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generate_project_depgraph_py -->|导入依赖 / import_depends| scripts_governance_sync_panorama_module_py
    scripts_governance_generate_project_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_project_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_check_ssot_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_project_path_tree_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_extract_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_extract_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_query_module_panorama_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_migrate_to_metadata_tables_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_run_gate_chain_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_status_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_status_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_meta_concurrency_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_sync_panorama_module_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_sync_panorama_module_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py
    scripts_governance_sync_panorama_module_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_verify_sync_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_audit_registration_py -->|导入依赖 / import_depends| scripts_governance_meta_manage_baseline_py
    scripts_governance_d11_compliance_audit_registration_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d11_compliance_audit_registration_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d10_performance_collect_system_threads_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_ci_self_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_fix_shared_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_fix_shared_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_g9_compliance_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_task_self_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_frozen_requirements_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_frozen_requirements_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_exit_codes_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_exit_codes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_commit_gateway_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_manifest_admission_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_commit_message_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_commit_message_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_libcst_docstring_adder_py
    scripts_governance_d11_compliance_verify_audit_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_no_utf8_bom_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_no_utf8_bom_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_script_naming_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_script_naming_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_archive_drafts_zone_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_archive_drafts_zone_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_validate_session_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_validate_session_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_verify_schema_health_py -->|导入依赖 / import_depends| scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py
    scripts_governance_d11_compliance_verify_schema_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_config_format_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_config_format_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_config_format_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_audit_directory_scalability_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_directory_scalability_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_directory_scalability_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d1_structure_batch_create_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_cbg_reset_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_cbg_reset_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_findings_by_scope_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_findings_by_scope_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_directory_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_directory_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_directory_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_cleanup_stash_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_check_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_check_directory_contract_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_directory_contract_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_check_directory_contract_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_detect_temp_files_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_detect_temp_files_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_temp_files_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_detect_orphan_py_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_detect_orphan_py_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_handoff_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_residual_files_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_detect_residual_files_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_residual_files_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_drafts_zone_archiver_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_drafts_zone_archiver_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_drafts_zone_archiver_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_sync_policies_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_sync_policies_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_sync_policies_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_sync_index_from_manifest_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_sync_index_from_manifest_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_sync_index_from_manifest_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_reset_cbg_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_reset_cbg_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d1_structure_run_script_smoke_test_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_run_script_smoke_test_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d1_structure_validate_d1_output_sanity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_d1_output_sanity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_index_reality_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_read_before_write_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_read_before_write_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_auto_generate_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d3_metadata_auto_generate_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_auto_generate_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d2_links_audit_broken_links_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d2_links_detect_relative_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d2_links_detect_relative_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d2_links_detect_relative_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_check_blueprint_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_check_module_singlesource_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_check_naming_convention_py -->|导入依赖 / import_depends| scripts_governance_d3_metadata_validate_module_id_naming_py
    scripts_governance_d3_metadata_check_naming_convention_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_schema_version_writes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_validate_blueprint_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_blueprint_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_classify_ttl_by_content_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_classify_ttl_by_content_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_generate_derived_files_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_generate_derived_files_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_generate_derived_files_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_validate_architecture_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_architecture_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_architecture_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_validate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_registry_entry_count_py
    scripts_governance_d3_metadata_validate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_validate_module_id_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_module_id_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_module_id_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d4_paths_detect_deprecated_path_writes_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_deprecated_path_writes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_tool_contracts_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_excessive_file_moves_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_excessive_file_moves_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_audit_agent_spec_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_check_drift_e2e_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyze_change_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_analyze_change_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_ruins_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_ruins_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_ruins_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_dependency_graph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_check_budget_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detect_causal_conflicts_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_detect_causal_conflicts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detect_constraint_violations_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_diagnose_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_diagnose_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_pre_write_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_pre_delete_safety_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_code_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_code_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_vms_ssot_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_generators_align_panoramas_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_d5_architecture_generators_align_panoramas_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_align_panoramas_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_module_translation_loader_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_candidate_module_report_py -->|导入依赖 / import_depends| scripts_governance_shared_module_translation_loader_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_generators_generate_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_generators_generate_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_generators_generate_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_policies_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_target_layer_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_target_layer_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d6_security_detect_anchor_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_anchor_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_check_protected_paths_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_check_protected_paths_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_git_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_git_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_git_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d6_security_detect_keywords_in_logs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_keywords_in_logs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_keywords_in_logs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_permanent_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_permanent_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_secrets_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_shell_true_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_shell_true_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_shell_true_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_shell_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_shell_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_shell_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_retire_tmp_artifacts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_retire_tmp_artifacts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_run_adversarial_checks_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_scan_runtime_log_secrets_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_scan_runtime_log_secrets_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_validate_gate_discipline_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_validate_gate_discipline_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_validate_gate_discipline_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_threading_lock_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_threading_lock_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_threading_lock_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_any_type_inferrer_py -->|导入依赖 / import_depends| scripts_governance_d7_code_check_any_abuse_py
    scripts_governance_d7_code_any_type_inferrer_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_vague_terms_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_vague_terms_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_vague_terms_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_check_ai_capability_boundary_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_ai_capability_boundary_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_merge_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_no_tests_unit_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_idempotency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_idempotency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_pit_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_pit_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_direct_llm_calls_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_direct_llm_calls_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_direct_llm_calls_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_detect_missing_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_missing_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_missing_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_detect_pydantic_any_fields_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_pydantic_any_fields_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_pydantic_any_fields_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_detect_forward_reference_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_private_key_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n06_scope_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n12_ke_naming_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_silent_degradation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_silent_degradation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_silent_degradation_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_fix_n13_snake_case_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n14_init_all_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_orphan_exports_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d7_code_fix_orphan_exports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_naming_manual_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_rewrite_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d7_code_rewrite_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_scan_consumers_accuracy_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n15_blueprint_path_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_scan_debt_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_import_style_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_import_style_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_fle_action_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_fle_action_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_fle_action_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_fle_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_fle_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_fle_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_scan_complexity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_docstring_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_docstring_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_contracts_purity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_contracts_purity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_contracts_purity_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_kb_write_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_kb_write_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_kb_write_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_init_all_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_init_all_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_type_annotation_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_type_annotation_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_unused_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_unused_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_python_syntax_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_python_syntax_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_test_assertion_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_test_assertion_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_test_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_test_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_audit_rename_completeness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_sync_rule_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_sync_rule_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_update_progress_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_data_quality_check_tick_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_data_quality_check_tick_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_check_gate_inventory_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_generators_fix_module_manifest_layout_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_fix_module_manifest_layout_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_fix_module_manifest_layout_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_registry_entry_count_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generators_generate_importlinter_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_importlinter_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_generate_importlinter_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generators_generate_path_ownership_map_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_path_ownership_map_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_sync_audit_protocol_numbers_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_sync_audit_protocol_numbers_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_registry_entry_count_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_fix_oscillation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_detect_fix_oscillation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_arbitrate_findings_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_compute_sla_metrics_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_compute_sla_metrics_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_compute_sla_metrics_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_backup_runtime_state_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_backup_runtime_state_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_create_task_from_finding_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_create_task_from_finding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_create_task_from_finding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_config_deviation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_detect_config_deviation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_script_rot_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_env_check_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_env_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_finding_state_machine_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_finding_state_machine_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_finding_state_machine_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_detect_hallucinated_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_detect_hallucinated_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_gate_engine_selfcheck_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_gate_engine_selfcheck_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_meta_detect_script_divergence_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_detect_script_divergence_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_baseline_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_baseline_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_governance_watchdog_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_governance_watchdog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_governance_watchdog_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_manage_error_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_error_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_error_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_manage_script_retirement_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_script_retirement_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_finding_timeseries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_mutation_test_reconciliation_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_script_ab_test_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_script_ab_test_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_pre_op_check_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_pre_op_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_mutation_test_post_sync_validator_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_trace_finding_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_shadow_mode_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_shadow_mode_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_score_script_effectiveness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_score_script_effectiveness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_session_startup_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_track_script_costs_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_track_script_costs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_automation_boundary_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_cross_model_consensus_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_emergency_bypass_log_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_emergency_bypass_log_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_dependency_chain_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_dependency_chain_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_false_negatives_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_false_negatives_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_rule_freshness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_rule_freshness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_rules_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_rules_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_meta_validate_end_to_end_benchmark_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_end_to_end_benchmark_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_mutation_testing_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_mutation_testing_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_environment_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_rules_file_backdoor_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_script_system_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_script_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_script_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_script_onboarding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_threshold_changes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_benchmark_test_fixtures_bad_imports_py -->|config_depends / config_depends| scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py
    scripts_governance_meta_validate_trust_tier_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_verify_reconciliation_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_concurrency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_concurrency_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py -->|导入依赖 / import_depends| scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py -->|config_depends / config_depends| scripts_governance_meta_benchmark_test_fixtures_bad_imports_py
    scripts_governance_migrate_sqlite_to_pg_migrate_data_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_vms_vms_version_sync_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_audit_post_sync_commands_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_check_exam_case_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_list_phase0_tasks_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_dm105_depgraph_triage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_fix_broken_post_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_phase_a_backup_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_rename_kebab_to_snake_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_test_lock_scenarios_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_audit_domain_nodes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_rename_whitelist_cleanup_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_verify_final_delivery_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_adversarial_log_py -->|config_depends / config_depends| scripts_governance_archive_prototype_audit_domain_nodes_py
    scripts_governance_archive_one_off_verify_rule_yaml_migration_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_check_audit_rbac_isolation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_changelog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_adversarial_sys_master_test_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_construction_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_generate_asset_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_rebuild_audit_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_generate_nav_table_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_archive_prototype_generate_nav_table_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_generate_nav_table_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_archive_vms_ri_ri_build_completion_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_vms_cron_monitor_py
    scripts_governance_archive_prototype_session_simulator_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_archive_prototype_session_simulator_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_scan_ground_truth_deps_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_vms_ri_vms_blindspot_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_ri_boundary_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_prototype_sync_blueprint_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_vms_ri_vms_cross_file_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_vms_build_completion_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_shared_base_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_shared_base_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_base_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_archive_vms_ri_vms_phase_rollback_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_vms_version_sync_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_file_utils_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_terminology_loader_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_walk_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_module_translation_loader_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_libcst_docstring_adder_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_shared_libcst_docstring_adder_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_libcst_docstring_adder_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_sync_check_p0_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_yaml_utils_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_sync_cleanup_p0_auto_bridged_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_sync_fix_orphan_deps_py -->|config_depends / config_depends| scripts_governance_sync_check_p0_status_py
    scripts_governance_sync_cleanup_p0_ops_pending_py -->|config_depends / config_depends| scripts_governance_sync_check_p0_status_py
    scripts_governance_tasks_task_show_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_tasks_task_summary_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_tasks_list_phase0_tasks_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_archive_governance_dm106_p2b_verification_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    tests_governance_scripts_governance_test_check_vocab_hardcode_py -->|测试依赖 / test_depends| scripts_governance_shared_constants_py
    tests_governance_scripts_governance_test_check_vocab_hardcode_py -->|测试依赖 / test_depends| scripts_governance_shared_yaml_utils_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_scripts_registry_yaml,scripts_archive_governance_dm106_p2b_verification_py,scripts_governance_archive_one_off_audit_post_sync_commands_py,scripts_governance_archive_one_off_check_exam_case_consistency_py,scripts_governance_archive_one_off_create_alignment_tasks_py,scripts_governance_archive_one_off_dm105_depgraph_triage_py,scripts_governance_archive_one_off_fix_broken_post_sync_py,scripts_governance_archive_one_off_list_phase0_tasks_py,scripts_governance_archive_one_off_phase_a_backup_py,scripts_governance_archive_one_off_rename_kebab_to_snake_py,scripts_governance_archive_one_off_rename_whitelist_cleanup_py,scripts_governance_archive_one_off_test_lock_scenarios_py,scripts_governance_archive_one_off_verify_final_delivery_py,scripts_governance_archive_one_off_verify_rule_yaml_migration_py,scripts_governance_archive_prototype_adversarial_log_py,scripts_governance_archive_prototype_adversarial_sys_master_test_py,scripts_governance_archive_prototype_audit_domain_nodes_py,scripts_governance_archive_prototype_changelog_py,scripts_governance_archive_prototype_check_audit_rbac_isolation_py,scripts_governance_archive_prototype_construction_gate_py,scripts_governance_archive_prototype_generate_asset_index_py,scripts_governance_archive_prototype_generate_nav_table_py,scripts_governance_archive_prototype_rebuild_audit_index_py,scripts_governance_archive_prototype_scan_ground_truth_deps_py,scripts_governance_archive_prototype_session_simulator_py,scripts_governance_archive_prototype_sync_blueprint_status_py,scripts_governance_archive_vms_ri_ri_boundary_check_py,scripts_governance_archive_vms_ri_ri_build_completion_check_py,scripts_governance_archive_vms_ri_vms_blindspot_check_py,scripts_governance_archive_vms_ri_vms_build_completion_check_py,scripts_governance_archive_vms_ri_vms_cron_monitor_py,scripts_governance_archive_vms_ri_vms_cross_file_check_py,scripts_governance_archive_vms_ri_vms_health_check_py,scripts_governance_archive_vms_ri_vms_migrate_py,scripts_governance_archive_vms_ri_vms_migration_dry_run_py,scripts_governance_archive_vms_ri_vms_phase_rollback_py,scripts_governance_archive_vms_ri_vms_version_sync_check_py,scripts_governance_shared_base_py,scripts_governance_shared_constants_py,scripts_governance_shared_encoding_py,scripts_governance_shared_file_utils_py,scripts_governance_shared_frontmatter_py,scripts_governance_shared_libcst_docstring_adder_py,scripts_governance_shared_module_translation_loader_py,scripts_governance_shared_registry_entry_count_py,scripts_governance_shared_terminology_loader_py,scripts_governance_shared_thresholds_py,scripts_governance_shared_walk_py,scripts_governance_shared_yaml_utils_py,scripts_governance_sync_check_p0_status_py,scripts_governance_sync_cleanup_p0_auto_bridged_py,scripts_governance_sync_cleanup_p0_ops_pending_py,scripts_governance_sync_fix_orphan_deps_py,scripts_governance_tasks_list_phase0_tasks_py,scripts_governance_tasks_task_show_py,scripts_governance_tasks_task_summary_py,scripts_governance_add_deferred_design_edges_py,scripts_governance_align_battle_map_py,scripts_governance_apply_battle_map_py,scripts_governance_apply_dataflowgraph_py,scripts_governance_apply_decisiongraph_py,scripts_governance_apply_depgraph_py,scripts_governance_architecture_health_dashboard_py,scripts_governance_ast_import_rewriter_py,scripts_governance_audit_return_contract_usage_py,scripts_governance_audit_worktree_ops_telemetry_py,scripts_governance_check_commit_message_py,scripts_governance_check_ssot_gate_py,scripts_governance_d10_performance_collect_system_threads_py,scripts_governance_d11_compliance_audit_registration_py,scripts_governance_d11_compliance_ci_self_check_py,scripts_governance_d11_compliance_fix_shared_bypass_py,scripts_governance_d11_compliance_g9_compliance_check_py,scripts_governance_d11_compliance_task_self_check_py,scripts_governance_d11_compliance_validate_commit_gateway_py,scripts_governance_d11_compliance_validate_commit_message_py,scripts_governance_d11_compliance_validate_exit_codes_py,scripts_governance_d11_compliance_validate_frozen_requirements_py,scripts_governance_d11_compliance_validate_manifest_admission_py,scripts_governance_d11_compliance_validate_no_utf8_bom_py,scripts_governance_d11_compliance_validate_script_naming_py,scripts_governance_d11_compliance_validate_script_quality_py,scripts_governance_d11_compliance_validate_task_decomposition_bypass_py,scripts_governance_d11_compliance_validate_vocabulary_coverage_py,scripts_governance_d11_compliance_verify_audit_integrity_py,scripts_governance_d11_compliance_verify_schema_health_py,scripts_governance_d12_ai_hallucination_check_logger_kwargs_py,scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py,scripts_governance_d12_ai_hallucination_validate_session_budget_py,scripts_governance_d12_ai_hallucination_validate_session_gate_check_py,scripts_governance_d1_structure_archive_drafts_zone_py,scripts_governance_d1_structure_audit_config_format_py,scripts_governance_d1_structure_audit_directory_integrity_py,scripts_governance_d1_structure_audit_directory_scalability_py,scripts_governance_d1_structure_audit_findings_by_scope_py,scripts_governance_d1_structure_batch_create_index_md_py,scripts_governance_d1_structure_cbg_reset_py,scripts_governance_d1_structure_check_directory_contract_py,scripts_governance_d1_structure_check_handoff_manifests_py,scripts_governance_d1_structure_check_index_integrity_py,scripts_governance_d1_structure_cleanup_stash_py,scripts_governance_d1_structure_detect_orphan_py_py,scripts_governance_d1_structure_detect_residual_files_py,scripts_governance_d1_structure_detect_temp_files_py,scripts_governance_d1_structure_drafts_zone_archiver_py,scripts_governance_d1_structure_generate_missing_index_md_py,scripts_governance_d1_structure_reset_cbg_py,scripts_governance_d1_structure_run_script_smoke_test_py,scripts_governance_d1_structure_sync_index_from_manifest_py,scripts_governance_d1_structure_sync_policies_index_py,scripts_governance_d1_structure_validate_config_integrity_py,scripts_governance_d1_structure_validate_d1_output_sanity_py,scripts_governance_d1_structure_validate_immutable_core_py,scripts_governance_d1_structure_validate_index_reality_py,scripts_governance_d1_structure_validate_read_before_write_py,scripts_governance_d2_links_audit_broken_links_py,scripts_governance_d2_links_detect_relative_references_py,scripts_governance_d3_metadata_auto_generate_index_py,scripts_governance_d3_metadata_backfill_doctype_metadata_py,scripts_governance_d3_metadata_backfill_ttl_metadata_py,scripts_governance_d3_metadata_check_blueprint_compliance_py,scripts_governance_d3_metadata_check_frontmatter_metadata_py,scripts_governance_d3_metadata_check_module_singlesource_py,scripts_governance_d3_metadata_check_naming_convention_py,scripts_governance_d3_metadata_check_registry_consistency_py,scripts_governance_d3_metadata_check_schema_version_writes_py,scripts_governance_d3_metadata_check_vocab_hardcode_py,scripts_governance_d3_metadata_classify_ttl_by_content_py,scripts_governance_d3_metadata_deep_content_scanner_py,scripts_governance_d3_metadata_generate_derived_files_py,scripts_governance_d3_metadata_generate_rule_catalog_py,scripts_governance_d3_metadata_migrate_illegal_doctype_py,scripts_governance_d3_metadata_validate_architecture_py,scripts_governance_d3_metadata_validate_blueprint_provenance_py,scripts_governance_d3_metadata_validate_module_id_py,scripts_governance_d3_metadata_validate_module_id_naming_py,scripts_governance_d3_metadata_validate_registry_master_index_py,scripts_governance_d3_metadata_validate_tool_contracts_consistency_py,scripts_governance_d4_paths_detect_deprecated_path_writes_py,scripts_governance_d4_paths_detect_excessive_file_moves_py,scripts_governance_d4_paths_detect_ruins_references_py,scripts_governance_d4_paths_detect_split_delete_ref_commit_py,scripts_governance_d5_architecture_analyze_change_impact_py,scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py,scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py,scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py,scripts_governance_d5_architecture_audit_agent_spec_py,scripts_governance_d5_architecture_check_budget_health_py,scripts_governance_d5_architecture_check_drift_e2e_py,scripts_governance_d5_architecture_checkers_check_architecture_gates_py,scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py,scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py,scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py,scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py,scripts_governance_d5_architecture_checkers_check_code_duplication_py,scripts_governance_d5_architecture_checkers_check_contract_code_drift_py,scripts_governance_d5_architecture_checkers_check_contract_physical_path_py,scripts_governance_d5_architecture_checkers_check_dependency_direction_py,scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py,scripts_governance_d5_architecture_checkers_check_orphan_outputs_py,scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py,scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py,scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py,scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py,scripts_governance_d5_architecture_checkers_check_vms_ssot_py,scripts_governance_d5_architecture_dependency_graph_py,scripts_governance_d5_architecture_detect_causal_conflicts_py,scripts_governance_d5_architecture_detect_constraint_violations_py,scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py,scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py,scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py,scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py,scripts_governance_d5_architecture_diagnose_depgraph_py,scripts_governance_d5_architecture_generators_common_py,scripts_governance_d5_architecture_generators_align_panoramas_py,scripts_governance_d5_architecture_generators_generate_asset_catalog_py,scripts_governance_d5_architecture_generators_generate_battle_map_diagram_py,scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py,scripts_governance_d5_architecture_generators_generate_candidate_module_report_py,scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py,scripts_governance_d5_architecture_generators_generate_contract_catalog_py,scripts_governance_d5_architecture_generators_generate_contracts_py,scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py,scripts_governance_d5_architecture_generators_generate_data_inventory_py,scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py,scripts_governance_d5_architecture_generators_generate_decision_diagram_py,scripts_governance_d5_architecture_generators_generate_panorama_registry_py,scripts_governance_d5_architecture_generators_generate_policies_py,scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py,scripts_governance_d5_architecture_panorama_common_py,scripts_governance_d5_architecture_pre_delete_safety_check_py,scripts_governance_d5_architecture_pre_write_gate_py,scripts_governance_d5_architecture_syncers_archive_rationale_log_py,scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py,scripts_governance_d5_architecture_syncers_merge_readme_to_index_py,scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py,scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py,scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py,scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py,scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py,scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py,scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py,scripts_governance_d5_architecture_validators_validate_arch_review_gate_py,scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py,scripts_governance_d5_architecture_validators_validate_autonomy_gate_py,scripts_governance_d5_architecture_validators_validate_b_track_packages_py,scripts_governance_d5_architecture_validators_validate_blind_spot_status_py,scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py,scripts_governance_d5_architecture_validators_validate_cross_references_py,scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py,scripts_governance_d5_architecture_validators_validate_depends_on_format_py,scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py,scripts_governance_d5_architecture_validators_validate_directory_structure_py,scripts_governance_d5_architecture_validators_validate_field_ownership_py,scripts_governance_d5_architecture_validators_validate_gate_yaml_py,scripts_governance_d5_architecture_validators_validate_handoff_package_py,scripts_governance_d5_architecture_validators_validate_interface_contracts_py,scripts_governance_d5_architecture_validators_validate_load_path_integrity_py,scripts_governance_d5_architecture_validators_validate_module_schema_py,scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py,scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py,scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py,scripts_governance_d5_architecture_validators_validate_target_layer_py,scripts_governance_d5_architecture_validators_validate_three_way_consistency_py,scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py,scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py,scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py,scripts_governance_d6_security_check_protected_paths_py,scripts_governance_d6_security_detect_anchor_file_deletion_py,scripts_governance_d6_security_detect_git_dangerous_py,scripts_governance_d6_security_detect_keywords_in_logs_py,scripts_governance_d6_security_detect_permanent_file_deletion_py,scripts_governance_d6_security_detect_secrets_py,scripts_governance_d6_security_detect_shell_dangerous_py,scripts_governance_d6_security_detect_shell_true_py,scripts_governance_d6_security_detect_threading_lock_py,scripts_governance_d6_security_detect_vague_terms_py,scripts_governance_d6_security_retire_tmp_artifacts_py,scripts_governance_d6_security_run_adversarial_checks_py,scripts_governance_d6_security_scan_runtime_log_secrets_py,scripts_governance_d6_security_scan_secret_leak_py,scripts_governance_d6_security_validate_gate_discipline_py,scripts_governance_d7_code_any_type_inferrer_py,scripts_governance_d7_code_check_ai_capability_boundary_py,scripts_governance_d7_code_check_any_abuse_py,scripts_governance_d7_code_check_encoding_py,scripts_governance_d7_code_check_idempotency_py,scripts_governance_d7_code_check_merge_conflict_py,scripts_governance_d7_code_check_no_tests_unit_py,scripts_governance_d7_code_check_pit_compliance_py,scripts_governance_d7_code_detect_absolute_path_hardcoding_py,scripts_governance_d7_code_detect_direct_llm_calls_py,scripts_governance_d7_code_detect_forward_reference_py,scripts_governance_d7_code_detect_missing_encoding_py,scripts_governance_d7_code_detect_private_key_py,scripts_governance_d7_code_detect_pydantic_any_fields_py,scripts_governance_d7_code_detect_silent_degradation_py,scripts_governance_d7_code_fix_n06_scope_py,scripts_governance_d7_code_fix_n12_ke_naming_py,scripts_governance_d7_code_fix_n13_snake_case_py,scripts_governance_d7_code_fix_n14_init_all_py,scripts_governance_d7_code_fix_n15_blueprint_path_py,scripts_governance_d7_code_fix_naming_manual_py,scripts_governance_d7_code_fix_orphan_exports_py,scripts_governance_d7_code_rewrite_imports_py,scripts_governance_d7_code_scan_complexity_py,scripts_governance_d7_code_scan_consumers_accuracy_py,scripts_governance_d7_code_scan_debt_py,scripts_governance_d7_code_validate_contracts_purity_py,scripts_governance_d7_code_validate_docstring_coverage_py,scripts_governance_d7_code_validate_fle_action_metadata_py,scripts_governance_d7_code_validate_fle_imports_py,scripts_governance_d7_code_validate_import_style_py,scripts_governance_d7_code_validate_init_all_py,scripts_governance_d7_code_validate_kb_write_provenance_py,scripts_governance_d7_code_validate_python_syntax_py,scripts_governance_d7_code_validate_test_assertion_depth_py,scripts_governance_d7_code_validate_test_coverage_py,scripts_governance_d7_code_validate_type_annotation_coverage_py,scripts_governance_d7_code_validate_unused_imports_py,scripts_governance_d8_doc_sync_audit_rename_completeness_py,scripts_governance_d8_doc_sync_auto_sync_all_registries_py,scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py,scripts_governance_d8_doc_sync_detect_dated_snapshots_py,scripts_governance_d8_doc_sync_sync_rule_registry_py,scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py,scripts_governance_d8_doc_sync_update_progress_py,scripts_governance_d8_doc_sync_validate_document_lifecycle_py,scripts_governance_d8_doc_sync_validate_document_ttl_py,scripts_governance_d9_knowledge_detect_duplicated_normative_language_py,scripts_governance_d9_knowledge_detect_orphan_documents_py,scripts_governance_data_quality_check_tick_duplication_py,scripts_governance_extract_decisiongraph_py,scripts_governance_extract_depgraph_py,scripts_governance_generate_decision_graph_py,scripts_governance_generate_project_depgraph_py,scripts_governance_generate_project_path_tree_py,scripts_governance_generators_check_gate_inventory_drift_py,scripts_governance_generators_fix_module_manifest_layout_py,scripts_governance_generators_generate_gate_registry_py,scripts_governance_generators_generate_importlinter_py,scripts_governance_generators_generate_path_ownership_map_py,scripts_governance_generators_generate_registry_master_index_py,scripts_governance_generators_inject_manifests_py,scripts_governance_generators_refresh_master_entries_py,scripts_governance_generators_sync_audit_protocol_numbers_py,scripts_governance_git_health_smoke_py,scripts_governance_harvest_candidates_from_drafts_py,scripts_governance_meta_concurrency_py,scripts_governance_meta_arbitrate_findings_py,scripts_governance_meta_backup_runtime_state_py,scripts_governance_meta_benchmark_test_fixtures_bad_imports_py,scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py,scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py,scripts_governance_meta_compute_sla_metrics_py,scripts_governance_meta_create_task_from_finding_py,scripts_governance_meta_detect_config_deviation_py,scripts_governance_meta_detect_fix_oscillation_py,scripts_governance_meta_detect_hallucinated_packages_py,scripts_governance_meta_detect_script_divergence_py,scripts_governance_meta_detect_script_rot_py,scripts_governance_meta_env_check_py,scripts_governance_meta_finding_state_machine_py,scripts_governance_meta_gate_engine_selfcheck_py,scripts_governance_meta_governance_watchdog_py,scripts_governance_meta_manage_baseline_py,scripts_governance_meta_manage_error_budget_py,scripts_governance_meta_manage_finding_timeseries_py,scripts_governance_meta_manage_script_ab_test_py,scripts_governance_meta_manage_script_retirement_py,scripts_governance_meta_manage_shadow_mode_py,scripts_governance_meta_mutation_test_post_sync_validator_py,scripts_governance_meta_mutation_test_reconciliation_registry_py,scripts_governance_meta_phase_e_context_check_py,scripts_governance_meta_pre_op_check_py,scripts_governance_meta_score_script_effectiveness_py,scripts_governance_meta_session_startup_check_py,scripts_governance_meta_trace_finding_lifecycle_py,scripts_governance_meta_track_script_costs_py,scripts_governance_meta_validate_automation_boundary_py,scripts_governance_meta_validate_cross_model_consensus_py,scripts_governance_meta_validate_dependency_chain_py,scripts_governance_meta_validate_emergency_bypass_log_py,scripts_governance_meta_validate_end_to_end_benchmark_py,scripts_governance_meta_validate_environment_health_py,scripts_governance_meta_validate_false_negatives_py,scripts_governance_meta_validate_gate_engine_external_py,scripts_governance_meta_validate_mutation_testing_py,scripts_governance_meta_validate_rule_freshness_py,scripts_governance_meta_validate_rules_file_backdoor_py,scripts_governance_meta_validate_rules_integrity_py,scripts_governance_meta_validate_script_onboarding_py,scripts_governance_meta_validate_script_provenance_py,scripts_governance_meta_validate_script_system_health_py,scripts_governance_meta_validate_threshold_changes_py,scripts_governance_meta_validate_trust_tier_py,scripts_governance_meta_verify_reconciliation_registry_py,scripts_governance_migrate_sqlite_to_pg_migrate_data_py,scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py,scripts_governance_migrate_to_metadata_tables_py,scripts_governance_oneoff_data_domain_audit_query_py,scripts_governance_query_module_panorama_py,scripts_governance_register_deferred_modules_py,scripts_governance_repair_concurrent_commit_test_py,scripts_governance_run_all_py,scripts_governance_run_gate_chain_py,scripts_governance_run_silent_failure_regression_py,scripts_governance_session_startup_health_check_py,scripts_governance_status_py,scripts_governance_sync_panorama_module_py,scripts_governance_verify_sync_integrity_py,scripts_governance_vms_vms_blindspot_check_py,scripts_governance_vms_vms_build_completion_check_py,scripts_governance_vms_vms_cron_monitor_py,scripts_governance_vms_vms_cross_file_check_py,scripts_governance_vms_vms_health_check_py,scripts_governance_vms_vms_migrate_py,scripts_governance_vms_vms_migration_dry_run_py,scripts_governance_vms_vms_phase_rollback_py,scripts_governance_vms_vms_version_sync_check_py,tests_governance_scripts_governance_test_any_type_inferrer_py,tests_governance_scripts_governance_test_check_canonical_yaml_drift_py,tests_governance_scripts_governance_test_check_vocab_hardcode_py,tests_governance_scripts_governance_test_pre_write_gate_py,tests_governance_test_check_blueprint_code_alignment_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 1 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_oneoff_data_domain_design_state_complete_py["数据域四图设计态补全——一次性执行脚本。<br/>Step 1: 补全 6 个数据域节点的 subdomain_id<br/>（扁平分组，不建子域幻影节点）<br/>⛔ 治理脚本域，设计已就绪，等待开发排期<br/>data_domain_design_state_complete<br/>文件: oneoff<br/>/data_domain_design_state_complete.py<br/>(设计态 / design)"]
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_oneoff_data_domain_design_state_complete_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | generate代码wikistats / generate_code_wiki_stats (generat... | → | D_DATA 数据接入层: table注册表 / table_registry (data/table_registry.py) | 导入依赖 / import_depends |
| 2 | generate数据inventory / generate_data_inventory (generato... | → | D_DATA 数据接入层: 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 3 | generate数据inventory / generate_data_inventory (generato... | → | D_DATA 数据接入层: ch读取器 / ch_reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 4 | check逐笔duplication / check_tick_duplication (data_quali... | → | D_DATA 数据接入层: 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 5 | check逐笔duplication / check_tick_duplication (data_quali... | → | D_DATA 数据接入层: ch读取器 / ch_reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 6 | 审计postsynccommands / audit_post_sync_commands (one_off/... | → | D_GOVERNANCE 生命周期管理: 提交同步校验器 / post_sync_validator (architecture_govern... | 导入依赖 / import_depends |
| 7 | 创建对齐任务 / # [BLUEPRINT] MOD-INF-005 | scripts/govern... | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 8 | 修复brokenpostsync / fix_broken_post_sync (one_off/fix_br... | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 9 | construction门禁 / construction_gate (prototype/construct... | → | D_GOVERNANCE 生命周期管理: 路径解析器 / path_resolver (architecture_governance/path_... | 导入依赖 / import_depends |
| 10 | 常量 / constants (_shared/constants.py) | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 11 | 任务show / task_show (_tasks/task_show.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 12 | 任务show / task_show (_tasks/task_show.py) | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 13 | 任务摘要 / task_summary (_tasks/task_summary.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 14 | 任务摘要 / task_summary (_tasks/task_summary.py) | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 15 | 新增deferred设计边 / add_deferred_design_edges (governanc... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 16 | G-battle-map-align: 作战地图对齐检测器（battle_map_positi... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 17 | G-battle-map-align: 作战地图对齐检测器（battle_map_positi... | → | D_GOVERNANCE 生命周期管理: battle_map_reader.py — 作战地图数据库只读查询工具模块 (p... | 导入依赖 / import_depends |
| 18 | G-battle-map-align: 作战地图对齐检测器（battle_map_positi... | → | D_GOVERNANCE 生命周期管理: dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 19 | G-battle-map-align: 作战地图对齐检测器（battle_map_positi... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 20 | [INVARIANTS] pg_advisory_lock 写锁; BM-INV-001~002 校验; ... | → | D_GOVERNANCE 生命周期管理: battlemap Schema DDL + 不变量声明 (persistence/battlemap_... | 导入依赖 / import_depends |
| 21 | 应用dataflowgraph / apply_dataflowgraph (governance/apply... | → | D_GOVERNANCE 生命周期管理: dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 22 | 应用decisiongraph / apply_decisiongraph (governance/apply... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 23 | checkssot门禁 / check_ssot_gate (governance/check_ssot_ga... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 24 | 任务自检查 / task_self_check (d11_compliance/task_self_ch... | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 25 | 任务自检查 / task_self_check (d11_compliance/task_self_ch... | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 26 | 校验模式健康 / verify_schema_health (d11_compliance/verif... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 27 | 校验模式健康 / verify_schema_health (d11_compliance/verif... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 28 | check结构版本writes / check_schema_version_writes (d3_met... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 29 | analyzechange冲击 / Module docstring — see module-level ... | → | D_GOVERNANCE 生命周期管理: LLM冲击分析器 / llm_impact_analyzer (architecture_governa... | 导入依赖 / import_depends |
| 30 | G-panorama-align: 四图对齐检测器（ARCH-053 + ARC / align_... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 31 | G-panorama-align: 四图对齐检测器（ARCH-053 + ARC / align_... | → | D_GOVERNANCE 生命周期管理: dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 32 | G-panorama-align: 四图对齐检测器（ARCH-053 + ARC / align_... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 33 | generate_battle_map_diagram.py — 交易决策作战地图可视化... | → | D_GOVERNANCE 生命周期管理: 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 34 | generate_battle_map_diagram.py — 交易决策作战地图可视化... | → | D_GOVERNANCE 生命周期管理: battle_map_reader.py — 作战地图数据库只读查询工具模块 (p... | 导入依赖 / import_depends |
| 35 | generate_battle_map_diagram.py — 交易决策作战地图可视化... | → | D_GOVERNANCE 生命周期管理: depgraph读取器 / depgraph_reader (persistence/depgraph_re... | 导入依赖 / import_depends |
| 36 | generate蓝图panorama / generate_blueprint_panorama (gener... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 37 | generate蓝图panorama / generate_blueprint_panorama (gener... | → | D_GOVERNANCE 生命周期管理: dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 38 | generate蓝图panorama / generate_blueprint_panorama (gener... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 39 | generate数据acquisition流程 / generate_data_acquisition_f... | → | D_GOVERNANCE 生命周期管理: 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 40 | 生成dataflowdiagram / generate_dataflow_diagram (generato... | → | D_GOVERNANCE 生命周期管理: 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 41 | 生成dataflowdiagram / generate_dataflow_diagram (generato... | → | D_GOVERNANCE 生命周期管理: dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 42 | generate决策diagram / generate_decision_diagram (generato... | → | D_GOVERNANCE 生命周期管理: 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 43 | generate决策diagram / generate_decision_diagram (generato... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 44 | generate交易流程diagram / generate_trading_flow_diagram (... | → | D_GOVERNANCE 生命周期管理: 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html ... | 导入依赖 / import_depends |
| 45 | generate交易流程diagram / generate_trading_flow_diagram (... | → | D_GOVERNANCE 生命周期管理: 决策graph读取器 / decision_graph_reader (persistence/deci... | 导入依赖 / import_depends |
| 46 | 蓝图frontmatter对账器 / blueprint_frontmatter_reconciler ... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 47 | 同步yamlto依赖图 / sync_yaml_to_depgraph (d8_doc_sync/syn... | → | D_GOVERNANCE 生命周期管理: dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 48 | 提取decisiongraph / extract_decisiongraph - decisiongraph... | → | D_GOVERNANCE 生命周期管理: 决策graph读取器 / decision_graph_reader (persistence/deci... | 导入依赖 / import_depends |
| 49 | 提取decisiongraph / extract_decisiongraph - decisiongraph... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 50 | [INVARIANTS] YAML 是唯一真源; DB 为只读缓存; 同步单向  / ... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 51 | 生成project依赖图 / # [BLUEPRINT] MOD-INF-005 | scripts/g... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 52 | 生成路径ownershipmap / generate_path_ownership_map (gener... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 53 | 生成路径ownershipmap / generate_path_ownership_map (gener... | → | D_GOVERNANCE 生命周期管理: 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 54 | 备份运行时状态 / backup_runtime_state (meta/backup_runtim... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 55 | 创建任务from发现 / create_task_from_finding (meta/create_... | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 56 | 创建任务from发现 / create_task_from_finding (meta/create_... | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 57 | migrateto元数据tables / migrate_to_metadata_tables (gover... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 58 | 数据域审计查询 / data_domain_audit_query (oneoff/data_dom... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 59 | 查询modulepanorama / query_module_panorama (governance/qu... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 60 | 查询modulepanorama / query_module_panorama (governance/qu... | → | D_GOVERNANCE 生命周期管理: dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 61 | 查询modulepanorama / query_module_panorama (governance/qu... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 62 | 注册deferredmodules / register_deferred_modules (governan... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 63 | 同步panorama模块 / sync_panorama_module (governance/sync_... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 64 | 同步panorama模块 / sync_panorama_module (governance/sync_... | → | D_GOVERNANCE 生命周期管理: dataflowgraph结构 / dataflowgraph_schema (persistence/dat... | 导入依赖 / import_depends |
| 65 | 同步panorama模块 / sync_panorama_module (governance/sync_... | → | D_GOVERNANCE 生命周期管理: decisiongraph结构 / decisiongraph_schema (persistence/dec... | 导入依赖 / import_depends |
| 66 | 对抗sys主测试 / Red/Blue Team Adversarial Test v3: SYS-MA... | → | D_GOV_AUDIT 审计追踪: sys主合规 / SYS-MASTER-001 Compliance Checker (rule_enfor... | 导入依赖 / import_depends |
| 67 | rebuild审计索引 / rebuild_audit_index (prototype/rebuild_... | → | D_GOV_AUDIT 审计追踪: 索引重建结果——治本（裁定#18 G5）：对齐 testa / indexer ... | 导入依赖 / import_depends |
| 68 | 架构健康仪表盘 / architecture_health_dashboard (governanc... | → | D_GOV_AUDIT 审计追踪: 运行时违规快照 / runtime_violation_snapshot (audit/runtim... | 导入依赖 / import_depends |
| 69 | 会话启动健康检查 / session_startup_health_check (governan... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 70 | 扫描消费者accuracy / scan_consumers_accuracy (d7_code/sca... | → | D_GOV_CODE_QUALITY 代码质量治理: 差异辅助 / _diff_helpers (commit_gates/_diff_helpers.py) | 导入依赖 / import_depends |
| 71 | 扫描消费者accuracy / scan_consumers_accuracy (d7_code/sca... | → | D_GOV_CODE_QUALITY 代码质量治理: consumersaccuracy门禁 / consumers_accuracy_gate (commit_g... | 导入依赖 / import_depends |
| 72 | 并发提交测试 / concurrent_commit_test (repair/concurrent_... | → | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | 导入依赖 / import_depends |
| 73 | 会话启动检查 / session_startup_check (meta/session_startu... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段检查注册表 / phase_check_registry (ops_governance/pha... | 导入依赖 / import_depends |
| 74 | 会话启动检查 / session_startup_check (meta/session_startu... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段管理器 / phase_manager (ops_governance/phase_manager.py) | 导入依赖 / import_depends |
| 75 | [INVARIANTS] 预算健康检查不可跳过;检查结果必须可机器解析 ... | → | D_GOV_REPAIR 治理修复: 预算执行 / budget_enforcement (financial_governance/budge... | 导入依赖 / import_depends |
| 76 | cbg重置 / cbg_reset (d1_structure/cbg_reset.py) | → | D_GOV_RULE 规则治理: 单向熔断器 / Circuit Breaker (rule_enforcement/circuit_br... | 导入依赖 / import_depends |
| 77 | 重置cbg / reset_cbg (d1_structure/reset_cbg.py) | → | D_GOV_RULE 规则治理: 单向熔断器 / Circuit Breaker (rule_enforcement/circuit_br... | 导入依赖 / import_depends |
| 78 | 创建任务from发现 / create_task_from_finding (meta/create_... | → | D_GOV_RULE 规则治理: 任务类型定义 / Task Types (rule_enforcement/task_types.py) | 导入依赖 / import_depends |
| 79 | 门禁引擎selfcheck / Gate Engine Bootstrap Self-Check — Q... | → | D_GOV_RULE 规则治理: 门禁裁决引擎 / Gate Engine (gate_engine/gate_engine.py) | 导入依赖 / import_depends |
| 80 | 校验门禁引擎外部 / validate_gate_engine_external (meta/va... | → | D_GOV_RULE 规则治理: 单向熔断器 / Circuit Breaker (rule_enforcement/circuit_br... | 导入依赖 / import_depends |
| 81 | 校验门禁引擎外部 / validate_gate_engine_external (meta/va... | → | D_GOV_RULE 规则治理: 门禁裁决引擎 / Gate Engine (gate_engine/gate_engine.py) | 导入依赖 / import_depends |
| 82 | 会话模拟器 / session_simulator (prototype/session_simulat... | → | D_INFRA_RUNTIME 运行时集成: 蓝图指标 / blueprint_metrics (metrics/blueprint_metrics.py) | 导入依赖 / import_depends |
| 83 | 基类 / base (_shared/base.py) | → | D_INFRA_RUNTIME 运行时集成: 发现 / finding (script_system/finding.py) | 导入依赖 / import_depends |
| 84 | 检查注册表一致性 / check_registry_consistency (d3_metadat... | → | D_INFRA_RUNTIME 运行时集成: 发现 / finding (script_system/finding.py) | 导入依赖 / import_depends |
| 85 | finding状态machine / finding_state_machine (meta/finding_... | → | D_INFRA_RUNTIME 运行时集成: 发现 / finding (script_system/finding.py) | 导入依赖 / import_depends |
| 86 | validateemergency绕过日志 / validate_emergency_bypass_log... | → | D_INFRA_RUNTIME 运行时集成: 发现 / finding (script_system/finding.py) | 导入依赖 / import_depends |
| 87 | run_all.py — 脚本系统统一入口脚本 / run_all (governance/... | → | D_INFRA_RUNTIME 运行时集成: 发现任务桥接 / finding_task_bridge (infrastructure/findin... | 导入依赖 / import_depends |
| 88 | run_all.py — 脚本系统统一入口脚本 / run_all (governance/... | → | D_INFRA_RUNTIME 运行时集成: 发现 / finding (script_system/finding.py) | 导入依赖 / import_depends |
| 89 | vmscron监控器 / vms_cron_monitor (vms_ri/vms_cron_monitor... | → | D_INTEGRATION 管线路由: 收集管理器 / collection_manager (vector_memory/collection... | 导入依赖 / import_depends |
| 90 | vmscron监控器 / vms_cron_monitor (vms_ri/vms_cron_monitor... | → | D_INTEGRATION 管线路由: 索引健康监控 / index_health_monitor (vector_memory/index_... | 导入依赖 / import_depends |
| 91 | vms健康检查 / vms_health_check (vms_ri/vms_health_check.py) | → | D_INTEGRATION 管线路由: 收集管理器 / collection_manager (vector_memory/collection... | 导入依赖 / import_depends |
| 92 | vms健康检查 / vms_health_check (vms_ri/vms_health_check.py) | → | D_INTEGRATION 管线路由: 索引健康监控 / index_health_monitor (vector_memory/index_... | 导入依赖 / import_depends |
| 93 | VMS Phase 2 数据迁移脚本 — MOD-INF-011 / vms_migrate (vm... | → | D_INTEGRATION 管线路由: 桥接层 / bridge_layer (vector_memory/bridge_layer.py) | 导入依赖 / import_depends |
| 94 | VMS Phase 2 数据迁移脚本 — MOD-INF-011 / vms_migrate (vm... | → | D_INTEGRATION 管线路由: 收集管理器 / collection_manager (vector_memory/collection... | 导入依赖 / import_depends |
| 95 | vms迁移dry运行 / vms_migration_dry_run (vms_ri/vms_migrat... | → | D_INTEGRATION 管线路由: 桥接层 / bridge_layer (vector_memory/bridge_layer.py) | 导入依赖 / import_depends |
| 96 | vmscron监控器 / vms_cron_monitor (vms/vms_cron_monitor.py) | → | D_INTEGRATION 管线路由: 收集管理器 / collection_manager (vector_memory/collection... | 导入依赖 / import_depends |
| 97 | vmscron监控器 / vms_cron_monitor (vms/vms_cron_monitor.py) | → | D_INTEGRATION 管线路由: 索引健康监控 / index_health_monitor (vector_memory/index_... | 导入依赖 / import_depends |
| 98 | vms健康检查 / vms_health_check (vms/vms_health_check.py) | → | D_INTEGRATION 管线路由: 收集管理器 / collection_manager (vector_memory/collection... | 导入依赖 / import_depends |
| 99 | vms健康检查 / vms_health_check (vms/vms_health_check.py) | → | D_INTEGRATION 管线路由: 索引健康监控 / index_health_monitor (vector_memory/index_... | 导入依赖 / import_depends |
| 100 | VMS Phase 2 数据迁移脚本 — MOD-INF-011 / vms_migrate (vm... | → | D_INTEGRATION 管线路由: 桥接层 / bridge_layer (vector_memory/bridge_layer.py) | 导入依赖 / import_depends |
| 101 | VMS Phase 2 数据迁移脚本 — MOD-INF-011 / vms_migrate (vm... | → | D_INTEGRATION 管线路由: 收集管理器 / collection_manager (vector_memory/collection... | 导入依赖 / import_depends |
| 102 | vms迁移dry运行 / vms_migration_dry_run (vms/vms_migration... | → | D_INTEGRATION 管线路由: 桥接层 / bridge_layer (vector_memory/bridge_layer.py) | 导入依赖 / import_depends |
| 103 | 考试题库一致性检查——根因治本，防止"定义-注册脱钩"复发。... | → | D_INTELLIGENCE 上下文管理: exam测试cases / exam_test_cases (model_profiling/exam_tes... | 导入依赖 / import_depends |
| 104 | 检查handoffmanifests / check_handoff_manifests (d1_struct... | → | D_ORCHESTRATOR 代理编排器: 契约注册表 / contract_registry (contracts/contract_regist... | 导入依赖 / import_depends |
| 105 | prewrite门禁 / pre_write_gate (d5_architecture/pre_write_... | → | D_SECURITY 对抗验证: 会话并发 / session_concurrency (access_control/session_co... | 导入依赖 / import_depends |
| 106 | DM-106: P2-B 迁移全量验证脚本 / dm106_p2b_verification (g... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 107 | 审计postsynccommands / audit_post_sync_commands (one_off/... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 108 | dm105depgraph分诊 / dm105_depgraph_triage (one_off/dm105_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 109 | 常量 / constants (_shared/constants.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 110 | 文件工具 / file_utils (_shared/file_utils.py) | → | D_SHARED 共享服务: 文件工具 / file_utils (io/file_utils.py) | 导入依赖 / import_depends |
| 111 | yaml工具 / yaml_utils (_shared/yaml_utils.py) | → | D_SHARED 共享服务: yaml工具 / yaml_utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 112 | 应用decisiongraph / apply_decisiongraph (governance/apply... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 113 | [INVARIANTS] 原子写入（RULE-ONE）；变更前验证；禁止直接覆... | → | D_SHARED 共享服务: 环境 / env (foundation/env.py) | 导入依赖 / import_depends |
| 114 | [INVARIANTS] 原子写入（RULE-ONE）；变更前验证；禁止直接覆... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 115 | [INVARIANTS] 原子写入（RULE-ONE）；变更前验证；禁止直接覆... | → | D_SHARED 共享服务: yaml工具 / yaml_utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 116 | checkssot门禁 / check_ssot_gate (governance/check_ssot_ga... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 117 | 检查模块singlesource / check_module_singlesource (d3_meta... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 118 | diagnose依赖图 / # [BLUEPRINT] MOD-INF-005 | scripts/gove... | → | D_SHARED 共享服务: yaml工具 / yaml_utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 119 | G-panorama-align: 四图对齐检测器（ARCH-053 + ARC / align_... | → | D_SHARED 共享服务: 转换器 / converters (utils/converters.py) | 导入依赖 / import_depends |
| 120 | 生成资产目录 / generate_asset_catalog (generators/generat... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 121 | 从 candidate_module_registry.yaml 生成候选模块清单报告（... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 122 | generate代码wikistats / generate_code_wiki_stats (generat... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 123 | 生成契约目录 / generate_contract_catalog (generators/gene... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 124 | 生成契约 / generate_contracts.py -- SSoT to Codegen pipel... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 125 | generatepanorama注册表 / generate_panorama_registry (gene... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 126 | 校验模块生命周期 / validate_module_lifecycle (lifecycle/v... | → | D_SHARED 共享服务: yaml工具 / yaml_utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 127 | 校验接口契约 / validate_interface_contracts (validators/v... | → | D_SHARED 共享服务: yaml工具 / yaml_utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 128 | 提取decisiongraph / extract_decisiongraph - decisiongraph... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 129 | 提取依赖图 / extract_depgraph (governance/extract_depgrap... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 130 | [INVARIANTS] YAML 是唯一真源; DB 为只读缓存; 同步单向  / ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 131 | 生成project依赖图 / # [BLUEPRINT] MOD-INF-005 | scripts/g... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 132 | 生成project依赖图 / # [BLUEPRINT] MOD-INF-005 | scripts/g... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 133 | 生成project依赖图 / # [BLUEPRINT] MOD-INF-005 | scripts/g... | → | D_SHARED 共享服务: yaml工具 / yaml_utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 134 | check门禁inventory漂移 / check_gate_inventory_drift (gene... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 135 | 从场外草稿 CSV 抓取候选模块入候选库（一次性 harvest 脚本... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 136 | 并发 / Module docstring — see module-level docstring for... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 137 | 创建任务from发现 / create_task_from_finding (meta/create_... | → | D_SHARED 共享服务: 模型 / models (foundation/models.py) | 导入依赖 / import_depends |
| 138 | 创建任务from发现 / create_task_from_finding (meta/create_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 139 | migrate数据 / migrate_data (migrate_sqlite_to_pg/migrate_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 140 | 并发提交测试 / concurrent_commit_test (repair/concurrent_... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 141 | 同步panorama模块 / sync_panorama_module (governance/sync_... | → | D_SHARED 共享服务: 转换器 / converters (utils/converters.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_PERM 自治保护: 检查终止开关latency / check_kill_switch_latency (fitness_... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 2 | D_AUTONOMY_PERM 自治保护: 管理终止开关 / manage_kill_switch (meta/manage_kill_switc... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 3 | D_AUTONOMY_PERM 自治保护: 管理终止开关 / manage_kill_switch (meta/manage_kill_switc... | → | 文件工具 / file_utils (_shared/file_utils.py) | 导入依赖 / import_depends |
| 4 | D_GOVERNANCE 生命周期管理: 架构ssot / _arch_ssot (arch_guard/_arch_ssot.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: buildocp清单 / build_ocp_manifest (_tools/build_ocp_manif... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: inject幂等性 / inject_idempotency (_tools/inject_idempote... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: 补丁p1paths / patch_p1_paths (_tools/patch_p1_paths.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 8 | D_GOVERNANCE 生命周期管理: 检查aclboundary / check_acl_boundary (arch_guard/check_ac... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 9 | D_GOVERNANCE 生命周期管理: check跨planecommunication / check_cross_plane_communicati... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 10 | D_GOVERNANCE 生命周期管理: 检查feaclboundary / check_fe_acl_boundary (arch_guard/che... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 11 | D_GOVERNANCE 生命周期管理: 检查hot路径purity / check_hot_path_purity (arch_guard/che... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 12 | D_GOVERNANCE 生命周期管理: checkscaffold退出门禁 / check_scaffold_exit_gates (arch_g... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 13 | D_GOVERNANCE 生命周期管理: checkscaffold退出门禁 / check_scaffold_exit_gates (arch_g... | → | yaml工具 / yaml_utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 14 | D_GOVERNANCE 生命周期管理: 检查模式一致性 / check_schema_consistency (arch_guard/che... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 15 | D_GOVERNANCE 生命周期管理: 检查aisg网关 / check_aisg_gateway (fitness_functions/chec... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 16 | D_GOVERNANCE 生命周期管理: check审计日志immutability / check_audit_log_immutability ... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 17 | D_GOVERNANCE 生命周期管理: checkdaily损失limit / check_daily_loss_limit (fitness_fun... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 18 | D_GOVERNANCE 生命周期管理: 检查hotwarmipc / check_hot_warm_ipc (fitness_functions/ch... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 19 | D_GOVERNANCE 生命周期管理: 检查幂等性密钥 / check_idempotency_key (fitness_functions... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 20 | D_GOVERNANCE 生命周期管理: check日志密钥leak / check_log_secret_leak (fitness_functi... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 21 | D_GOVERNANCE 生命周期管理: checkno跨planemutable状态 / check_no_cross_plane_mutable_... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 22 | D_GOVERNANCE 生命周期管理: 检查ocpsignatures / check_ocp_signatures (fitness_functio... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 23 | D_GOVERNANCE 生命周期管理: 检查pit合规 / check_pit_compliance (fitness_functions/che... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 24 | D_GOVERNANCE 生命周期管理: 检查持仓限制 / check_position_limit (fitness_functions/ch... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 25 | D_GOVERNANCE 生命周期管理: check风险paramsconsistency / check_risk_params_consistenc... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 26 | D_GOVERNANCE 生命周期管理: checkwarm冷异步 / check_warm_cold_async (fitness_function... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 27 | D_GOVERNANCE 生命周期管理: 重置测试任务 / reset_test_task (construction/reset_test_t... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 28 | D_GOVERNANCE 生命周期管理: 启动brain / start_brain (construction/start_brain.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 29 | D_GOVERNANCE 生命周期管理: dm90971add测试headers / DM-90971: Batch add module_id sco... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 30 | D_GOVERNANCE 生命周期管理: 修复孤儿all / fix_orphan_all (scripts/fix_orphan_all.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 31 | D_GOVERNANCE 生命周期管理: 修复孤儿all / fix_orphan_all (scripts/fix_orphan_all.py) | → | 文件工具 / file_utils (_shared/file_utils.py) | 导入依赖 / import_depends |
| 32 | D_GOVERNANCE 生命周期管理: generatepathway注册表 / generate_pathway_registry (script... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 33 | D_GOVERNANCE 生命周期管理: 检查pureshim / check_pure_shim (d7_code/check_pure_shim.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 34 | D_GOVERNANCE 生命周期管理: 检查pureshim / check_pure_shim (d7_code/check_pure_shim.py) | → | encoding.py — UTF-8 编码安全工具 / encoding (_shared/enc... | 导入依赖 / import_depends |
| 35 | D_GOVERNANCE 生命周期管理: generate规则aiperception索引 / generate_rule_ai_perceptio... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 36 | D_GOVERNANCE 生命周期管理: 自动handoff日志 / auto_handoff_log (hooks/auto_handoff_lo... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 37 | D_GOVERNANCE 生命周期管理: 生成ide配置 / generate_ide_config (mcp/generate_ide_confi... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 38 | D_GOVERNANCE 生命周期管理: MCP DAG 编排启动器（MOD-INF-013 §14 拓扑排序 + Pro / lau... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 39 | D_GOVERNANCE 生命周期管理: 启动all / start_all (mcp/start_all.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 40 | D_GOVERNANCE 生命周期管理: 停止all / stop_all (mcp/stop_all.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 41 | D_GOVERNANCE 生命周期管理: dm311autonomy核心split / dm311_autonomy_core_split (migra... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 42 | D_GOVERNANCE 生命周期管理: dm314基础设施运维拆分 / dm314_infra_ops_split (migration/... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 43 | D_GOVERNANCE 生命周期管理: 文件头部完整性校验（6 格式统一入口） / verify_header_comp... | → | 文件头部格式解析 SSoT（Single Source of Truth） / frontma... | 导入依赖 / import_depends |
| 44 | D_GOVERNANCE 生命周期管理: verify去重 / verify_dedup (pre_commit/verify_dedup.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 45 | D_GOVERNANCE 生命周期管理: scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TW / scaffo... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 46 | D_GOVERNANCE 生命周期管理: scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TW / scaffo... | → | yaml工具 / yaml_utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 47 | D_GOVERNANCE 生命周期管理: scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TW / scaffo... | → | GATE-11 命名规范门禁 — 全类型命名检测。 / check_naming_c... | 导入依赖 / import_depends |
| 48 | D_GOVERNANCE 生命周期管理: 测试生成门禁注册表 / test_generate_gate_registry (generat... | → | 生成门禁注册表 / generate_gate_registry (generators/gener... | 测试依赖 / test_depends |
| 49 | D_GOV_AUDIT 审计追踪: 审计designcompleteness / audit_design_completeness (repai... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 50 | D_GOV_AUDIT 审计追踪: [INVARIANTS] 20项红蓝对抗测试 / red_blue_test (repair/red... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 51 | D_GOV_AUDIT 审计追踪: 回滚依赖图 / rollback_depgraph (repair/rollback_depgraph.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 52 | D_GOV_AUDIT 审计追踪: 测试修复进度smoke / test_remediation_progress_smoke (gove... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 53 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | 校验模块idnaming / validate_module_id_naming (d3_metadata... | 导入依赖 / import_depends |
| 54 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | check门禁inventory漂移 / check_gate_inventory_drift (gene... | 导入依赖 / import_depends |
| 55 | D_GOV_CODE_QUALITY 代码质量治理: 检查模块id一致性 / check_module_id_consistency (d7_code/c... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 56 | D_GOV_DOCS 架构文档治理: 测试guc触发器fix.py — GUC 触发器缺陷修复的端到 / test_gu... | → | 常量 / constants (_shared/constants.py) | 测试依赖 / test_depends |
| 57 | D_GOV_DOCS 架构文档治理: 测试syncsavepointisolation / test_sync_savepoint_isolatio... | → | 常量 / constants (_shared/constants.py) | 测试依赖 / test_depends |
| 58 | D_GOV_DRIFT 漂移检测: validate蓝图overlap / Module docstring — see module-leve... | → | 文件头部格式解析 SSoT（Single Source of Truth） / frontma... | 导入依赖 / import_depends |
| 59 | D_GOV_DRIFT 漂移检测: validatetruth数据源级联 / validate_truth_source_cascade (... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 60 | D_GOV_DRIFT 漂移检测: validatetruth数据源级联 / validate_truth_source_cascade (... | → | 文件头部格式解析 SSoT（Single Source of Truth） / frontma... | 导入依赖 / import_depends |
| 61 | D_GOV_DRIFT 漂移检测: 校验ssot / validate_ssot (validators/validate_ssot.py) | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 62 | D_GOV_DRIFT 漂移检测: 校验ssot / validate_ssot (validators/validate_ssot.py) | → | encoding.py — UTF-8 编码安全工具 / encoding (_shared/enc... | 导入依赖 / import_depends |
| 63 | D_GOV_DRIFT 漂移检测: 校验ssot / validate_ssot (validators/validate_ssot.py) | → | 文件头部格式解析 SSoT（Single Source of Truth） / frontma... | 导入依赖 / import_depends |
| 64 | D_GOV_DRIFT 漂移检测: 校验ssot / validate_ssot (validators/validate_ssot.py) | → | yaml工具 / yaml_utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 65 | D_GOV_ENFORCEMENT 规则执行: 指标数量漂移协调器 / metric_count_drift_reconciler (d8_do... | → | 架构健康仪表盘 / architecture_health_dashboard (governanc... | 导入依赖 / import_depends |
| 66 | D_GOV_ENFORCEMENT 规则执行: 会话worktreecli / session_worktree_cli (governance/sessio... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 67 | D_GOV_RULE 规则治理: 脚本清单自动生成器 / Script Manifest Generator (generator... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 68 | D_GOV_RULE 规则治理: 脚本清单自动生成器 / Script Manifest Generator (generator... | → | encoding.py — UTF-8 编码安全工具 / encoding (_shared/enc... | 导入依赖 / import_depends |
| 69 | D_GOV_RULE 规则治理: 脚本清单自动生成器 / Script Manifest Generator (generator... | → | 文件工具 / file_utils (_shared/file_utils.py) | 导入依赖 / import_depends |
| 70 | D_GOV_RULE 规则治理: 脚本清单自动生成器 / Script Manifest Generator (generator... | → | yaml工具 / yaml_utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 71 | D_OPS 反馈循环: 门禁缓存 / Module docstring — see module-level docstring... | → | 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 72 | D_OPS 反馈循环: 门禁缓存 / Module docstring — see module-level docstring... | → | 文件工具 / file_utils (_shared/file_utils.py) | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 18 个外部域直接连接（出边 141 条 + 入边 72 条 = 213 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_GOV_REPAIR["D_GOV_REPAIR<br/>治理修复"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_AUTONOMY_PERM["D_AUTONOMY_PERM<br/>自治保护"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_GOV_DOCS["D_GOV_DOCS<br/>架构文档治理"]
    D_GOV_SCRIPTS -->|60条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_SCRIPTS -->|36条 导入依赖 / import_depends| D_SHARED
    D_GOV_SCRIPTS -->|14条 导入依赖 / import_depends| D_INTEGRATION
    D_GOV_SCRIPTS -->|7条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_SCRIPTS -->|6条 导入依赖 / import_depends| D_GOV_RULE
    D_GOV_SCRIPTS -->|5条 导入依赖 / import_depends| D_DATA
    D_GOV_SCRIPTS -->|4条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_SCRIPTS -->|2条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOV_SCRIPTS -->|2条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_GOV_REPAIR
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_INTELLIGENCE
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_SECURITY
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE -->|45条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_SCRIPTS
    D_GOV_DRIFT -->|7条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_AUDIT -->|6条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_RULE -->|4条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_AUTONOMY_PERM -->|3条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_OPS -->|2条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_DOCS -->|2条 测试依赖 / test_depends| D_GOV_SCRIPTS
    D_GOV_ENFORCEMENT -->|2条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_GOV_SCRIPTS
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
