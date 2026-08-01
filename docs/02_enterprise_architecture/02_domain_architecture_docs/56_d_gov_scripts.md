---
doc_type: architecture_view
title: D_GOV_SCRIPTS 脚本治理架构文档
version: "1.0"
status: active
date: 2026-08-01
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
| 模块数 | 385 | Module Count | 385 |
| 域内依赖 | 744 | Internal Dependencies | 744 |
| 跨域入边 | 72 | Cross-domain Incoming | 72 |
| 跨域出边 | 127 | Cross-domain Outgoing | 127 |
| 设计态模块 | 1 | Design Modules | 1 |
| 生产态模块 | 384 | Production Modules | 384 |
| 容量 | 384/150 (超容) | Capacity | 384/150 (超容) |
| 描述 | Phase Manager阶段管理 | Description | Phase Manager阶段管理 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。全景图用颜色区分运营态/设计态，不再分页/拆子图。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景依赖图（全部模块，颜色区分运营态/设计态）

> 展示全部 385 个模块（生产态 384 + 设计态 1），节点含成熟度+中英文名+大白话+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_01_policies_and_standards_registry_catalogs_scripts_registry_yaml["(生产态 / production)<br/>文件: catalogs/scripts_registry.yaml"]
    scripts_archive_governance_dm106_p2b_verification_py["(生产态 / production) dm106p2b验证 / Dm106 P2b Verification<br/>DM-106: P2-B 迁移全量验证脚本<br/>文件: governance/dm106_p2b_verification.py"]
    scripts_governance_archive_one_off_audit_post_sync_commands_py["(生产态 / production) 审计后同步commands / Audit Post Sync Commands<br/>audit_post_sync_commands.py — post_sync_standard 命令可执行性巡检（防幻觉/CL...<br/>文件: one_off/audit_post_sync_commands.py"]
    scripts_governance_archive_one_off_check_exam_case_consistency_py["(生产态 / production) 检查examcase一致性 / Check Exam Case Consistency<br/>考试题库一致性检查——根因治本，防止'定义-注册脱钩'复发。<br/>文件: one_off/check_exam_case_consistency.py"]
    scripts_governance_archive_one_off_create_alignment_tasks_py["(生产态 / production) create对齐任务 / Create Alignment Tasks<br/># (BLUEPRINT) MOD-INF-005 / scripts/governance/create_alignment_tasks.py / §7<br/>文件: one_off/create_alignment_tasks.py"]
    scripts_governance_archive_one_off_dm105_depgraph_triage_py["(生产态 / production) dm105depgraphtriage / Dm105 Depgraph Triage<br/>DM-105: depgraph 未分配节点三策略处理脚本<br/>文件: one_off/dm105_depgraph_triage.py"]
    scripts_governance_archive_one_off_fix_broken_post_sync_py["(生产态 / production) 修复broken后同步 / Fix Broken Post Sync<br/>fix_broken_post_sync.py — 批量修复历史 broken post_sync_standard 命令<br/>文件: one_off/fix_broken_post_sync.py"]
    scripts_governance_archive_one_off_list_phase0_tasks_py["(生产态 / production) listphase0任务 / List Phase0 Tasks<br/>(INVARIANTS) 仅查询不修改; 连接失败→exit 1<br/>文件: one_off/list_phase0_tasks.py"]
    scripts_governance_archive_one_off_phase_a_backup_py["(生产态 / production) phaseabackup / Phase A Backup<br/>phase_a_backup.py — 阶段A安全网 Tier0/Tier1 关键文件备份<br/>文件: one_off/phase_a_backup.py"]
    scripts_governance_archive_one_off_rename_kebab_to_snake_py["(生产态 / production) renamekebab转snake / Rename Kebab To Snake<br/>rename_kebab_to_snake.py — 全项目文件名/目录名 kebab-case → snake_case 批量...<br/>文件: one_off/rename_kebab_to_snake.py"]
    scripts_governance_archive_one_off_rename_whitelist_cleanup_py["(生产态 / production) renamewhitelist清理 / Rename Whitelist Cleanup<br/>命名规范白名单清理 - 全文替换脚本。<br/>文件: one_off/rename_whitelist_cleanup.py"]
    scripts_governance_archive_one_off_test_lock_scenarios_py["(生产态 / production) 测试lockscenarios / Test Lock Scenarios<br/>test_lock_scenarios.py — RULE-ZERO 锁协议场景 B/C 验证<br/>文件: one_off/test_lock_scenarios.py"]
    scripts_governance_archive_one_off_verify_final_delivery_py["(生产态 / production) verifyfinaldelivery / Verify Final Delivery<br/>(INVARIANTS) 设计态节点数>=1128; 规则表各表>0<br/>文件: one_off/verify_final_delivery.py"]
    scripts_governance_archive_one_off_verify_rule_yaml_migration_py["(生产态 / production) verify规则yaml迁移 / Verify Rule Yaml Migration<br/>verify_rule_yaml_migration.py - 6-dimensional verification of rule YAML migra...<br/>文件: one_off/verify_rule_yaml_migration.py"]
    scripts_governance_archive_prototype_adversarial_log_py["(生产态 / production) 对抗log / Adversarial Log<br/>红白对抗闭环记录——攻击→根源分析→修复→回归验证→知识注入全链路追踪<br/>文件: prototype/adversarial_log.py"]
    scripts_governance_archive_prototype_adversarial_sys_master_test_py["(生产态 / production) 对抗sysmaster测试 / Adversarial Sys Master Test<br/>Red/Blue Team Adversarial Test v3: SYS-MASTER-001 + MOD-MASTER_BLUEPRINT Inte...<br/>文件: prototype/adversarial_sys_master_test.py"]
    scripts_governance_archive_prototype_audit_domain_nodes_py["(生产态 / production) 审计domainnodes / Audit Domain Nodes<br/>SRC-100200: Audit 13 over-capacity domains granularity distribution.<br/>文件: prototype/audit_domain_nodes.py"]
    scripts_governance_archive_prototype_changelog_py["(生产态 / production) 变更日志 / Changelog<br/>changelog.py — 治理域变更日志生成/追加工具.<br/>文件: prototype/changelog.py"]
    scripts_governance_archive_prototype_construction_gate_py["(生产态 / production) construction门禁 / Construction Gate<br/>Construction Gate — 施工前路径校验门禁<br/>文件: prototype/construction_gate.py"]
    scripts_governance_archive_prototype_generate_asset_index_py["(生产态 / production) generateasset索引 / Generate Asset Index<br/>全项目资产索引生成器<br/>文件: prototype/generate_asset_index.py"]
    scripts_governance_archive_prototype_generate_nav_table_py["(生产态 / production) generatenavtable / Generate Nav Table<br/>generate_nav_table.py — 全流程导航表自动生成器 v1.0.0<br/>文件: prototype/generate_nav_table.py"]
    scripts_governance_archive_prototype_rebuild_audit_index_py["(生产态 / production) rebuild审计索引 / Rebuild Audit Index<br/>scripts/governance/rebuild_audit_index.py — 重建 audit-trail SQLite 派生索引<br/>文件: prototype/rebuild_audit_index.py"]
    scripts_governance_archive_prototype_scan_ground_truth_deps_py["(生产态 / production) scangroundtruthdeps / Scan Ground Truth Deps<br/># (BLUEPRINT) MOD-INF-005 / scripts/governance/scan_ground_truth_deps.py / §7<br/>文件: prototype/scan_ground_truth_deps.py"]
    scripts_governance_archive_prototype_session_simulator_py["(生产态 / production) 会话simulator / Session Simulator<br/>session_simulator — 30 个模拟开发 session 的蓝图读取事件生成器<br/>文件: prototype/session_simulator.py"]
    scripts_governance_archive_prototype_sync_blueprint_status_py["(生产态 / production) 同步蓝图status / Sync Blueprint Status<br/>机械强制：construction_plan=phase_2_complete → blueprint.status=Active.<br/>文件: prototype/sync_blueprint_status.py"]
    scripts_governance_archive_vms_ri_vms_blindspot_check_py["(生产态 / production) VMSblindspot检查 / VMS Blindspot Check<br/>VMS 盲点闭合检查器 — MOD-INF-011 · R1(33) + R2(22) + R4(6)<br/>文件: vms_ri/vms_blindspot_check.py"]
    scripts_governance_archive_vms_ri_vms_build_completion_check_py["(生产态 / production) VMSbuildcompletion检查 / VMS Build Completion Check<br/>VMS Build Completion Check — MOD-INF-011 · TASK-INF-0217<br/>文件: vms_ri/vms_build_completion_check.py"]
    scripts_governance_archive_vms_ri_vms_cron_monitor_py["(生产态 / production) VMScron监控器 / VMS Cron Monitor<br/>VMS Cron 监控器 — MOD-INF-011 · TASK-INF-0224<br/>文件: vms_ri/vms_cron_monitor.py"]
    scripts_governance_archive_vms_ri_vms_cross_file_check_py["(生产态 / production) VMS跨文件检查 / VMS Cross File Check<br/>VMS 跨文件内容一致性检查器 — MOD-INF-011 · TASK-INF-0211<br/>文件: vms_ri/vms_cross_file_check.py"]
    scripts_governance_archive_vms_ri_vms_health_check_py["(生产态 / production) VMS健康检查 / VMS Health Check<br/>VMS Health Check 脚本 — MOD-INF-011 · Phase 3 运维自动化<br/>文件: vms_ri/vms_health_check.py"]
    scripts_governance_archive_vms_ri_vms_migrate_py["(生产态 / production) VMSmigrate / VMS Migrate<br/>VMS Phase 2 数据迁移脚本 — MOD-INF-011<br/>文件: vms_ri/vms_migrate.py"]
    scripts_governance_archive_vms_ri_vms_migration_dry_run_py["(生产态 / production) VMS迁移dryrun / VMS Migration Dry Run<br/>VMS 迁移 dry-run 脚本 — MOD-INF-011 Phase 2 前置检查<br/>文件: vms_ri/vms_migration_dry_run.py"]
    scripts_governance_archive_vms_ri_vms_phase_rollback_py["(生产态 / production) VMSphaserollback / VMS Phase Rollback<br/>VMS Phase 回滚方案 — MOD-INF-011 · TASK-INF-0217<br/>文件: vms_ri/vms_phase_rollback.py"]
    scripts_governance_archive_vms_ri_vms_version_sync_check_py["(生产态 / production) VMS版本同步检查 / VMS Version Sync Check<br/>VMS 版本同步检查器 — MOD-INF-011 · TASK-INF-0222<br/>文件: vms_ri/vms_version_sync_check.py"]
    scripts_governance_shared_base_py["(生产态 / production) 基础 / Base<br/>base.py — 审计脚本基类<br/>文件: _shared/base.py"]
    scripts_governance_shared_module_translation_loader_py["(生产态 / production) 模块translation加载器 / Module Translation Loader<br/>module_translation_loader.py — 模块级翻译共享加载器（SSoT 真源）<br/>文件: _shared/module_translation_loader.py"]
    scripts_governance_sync_cleanup_p0_auto_bridged_py["(生产态 / production) 清理p0自动bridged / Cleanup P0 Auto Bridged<br/>清理历史 P0 自动桥接任务<br/>文件: _sync/cleanup_p0_auto_bridged.py"]
    scripts_governance_sync_cleanup_p0_ops_pending_py["(生产态 / production) 清理p0运维pending / Cleanup P0 Ops Pending<br/>cleanup_p0_ops_pending.py - 一次性：将所有 OPS-* P0+PENDING 任务降级+完成<br/>文件: _sync/cleanup_p0_ops_pending.py"]
    scripts_governance_sync_fix_orphan_deps_py["(生产态 / production) 修复orphandeps / Fix Orphan Deps<br/>fix_orphan_deps.py — 一次性修复孤儿依赖引用<br/>文件: _sync/fix_orphan_deps.py"]
    scripts_governance_tasks_list_phase0_tasks_py["(生产态 / production) listphase0任务 / List Phase0 Tasks<br/>(INVARIANTS) 仅查询不修改; 连接失败→exit 1<br/>文件: _tasks/list_phase0_tasks.py"]
    scripts_governance_tasks_task_show_py["(生产态 / production) 任务show / Task Show<br/>governance/task_show 脚本 — 任务卡详情查询 CLI。<br/>文件: _tasks/task_show.py"]
    scripts_governance_tasks_task_summary_py["(生产态 / production) 任务summary / Task Summary<br/>task_summary.py — 任务系统全局摘要 CLI<br/>文件: _tasks/task_summary.py"]
    scripts_governance_add_deferred_design_edges_py["(生产态 / production) adddeferred设计edges / Add Deferred Design Edges<br/>为暂缓模块添加设计态依赖边（dep_maturity='design'）。<br/>文件: governance/add_deferred_design_edges.py"]
    scripts_governance_apply_dataflowgraph_py["(生产态 / production) applydataflowgraph / Apply Dataflowgraph<br/>apply_dataflowgraph.py — dataflowgraph 变更写入工具（CLI）<br/>文件: governance/apply_dataflowgraph.py"]
    scripts_governance_apply_decisiongraph_py["(生产态 / production) applydecisiongraph / Apply Decisiongraph<br/>(INVARIANTS) pg_advisory_lock 写锁; build_status 单调推进; DEC-INV-001~005 校...<br/>文件: governance/apply_decisiongraph.py"]
    scripts_governance_apply_depgraph_py["(生产态 / production) applydepgraph / Apply Depgraph<br/>(INVARIANTS) 原子写入（RULE-ONE）；变更前验证；禁止直接覆盖<br/>文件: governance/apply_depgraph.py"]
    scripts_governance_architecture_health_dashboard_py["(生产态 / production) 架构健康仪表板 / Architecture Health Dashboard<br/>architecture_health_dashboard.py — 架构健康度仪表盘（自动化检测基线）<br/>文件: governance/architecture_health_dashboard.py"]
    scripts_governance_ast_import_rewriter_py["(生产态 / production) ast导入rewriter / Ast Import Rewriter<br/>AST-based import rewriter for governance directory migration.<br/>文件: governance/ast_import_rewriter.py"]
    scripts_governance_audit_return_contract_usage_py["(生产态 / production) 审计returncontractusage / Audit Return Contract Usage<br/>audit_return_contract_usage.py — 返回契约 ok 键调用方审计（P2-5，2026-07-19）<br/>文件: governance/audit_return_contract_usage.py"]
    scripts_governance_audit_worktree_ops_telemetry_py["(生产态 / production) 审计worktree运维遥测 / Audit Worktree Ops Telemetry<br/>audit_worktree_ops_telemetry.py — 主工作区文件级擦除操作遥测完整性审计（P2-6）<br/>文件: governance/audit_worktree_ops_telemetry.py"]
    scripts_governance_check_commit_message_py["(生产态 / production) 检查commitmessage / Check Commit Message<br/>check_commit_message.py — GitHub Actions PR commit message guard (P4-3).<br/>文件: governance/check_commit_message.py"]
    scripts_governance_check_ssot_gate_py["(生产态 / production) 检查ssot门禁 / Check Ssot Gate<br/>GATE-SSOT: SSoT 创建门禁（pre-commit hook 双保险）。<br/>文件: governance/check_ssot_gate.py"]
    scripts_governance_d10_performance_collect_system_threads_py["(生产态 / production) 收集系统threads / Collect System Threads<br/>collect_system_threads.py — 全系统线程数快照采集器<br/>文件: d10_performance/collect_system_threads.py"]
    scripts_governance_d11_compliance_audit_registration_py["(生产态 / production) 审计registration / Audit Registration<br/>audit_registration.py — 孤儿注册检测（RULE-TWO 防线 2）<br/>文件: d11_compliance/audit_registration.py"]
    scripts_governance_d11_compliance_ci_self_check_py["(生产态 / production) ci自我检查 / Ci Self Check<br/>CI Entry: Self-Check — Drift Detector 自身完整性验证<br/>文件: d11_compliance/ci_self_check.py"]
    scripts_governance_d11_compliance_fix_shared_bypass_py["(生产态 / production) 修复shared旁路 / Fix Shared Bypass<br/>fix_shared_bypass.py - D-D-07 auto-fix tool (validate_script_quality.py --fix...<br/>文件: d11_compliance/fix_shared_bypass.py"]
    scripts_governance_d11_compliance_g9_compliance_check_py["(生产态 / production) g9合规检查 / G9 Compliance Check<br/>G9 四蓝图跨模块集成合规门禁执行器.<br/>文件: d11_compliance/g9_compliance_check.py"]
    scripts_governance_d11_compliance_task_self_check_py["(生产态 / production) 任务自我检查 / Task Self Check<br/>task_self_check.py — 任务系统自身健康检查<br/>文件: d11_compliance/task_self_check.py"]
    scripts_governance_d11_compliance_validate_commit_gateway_py["(生产态 / production) validatecommitgateway / Validate Commit Gateway<br/>validate_commit_gateway.py — GATE-COMMIT-GW 门禁（OPS-2026062513）<br/>文件: d11_compliance/validate_commit_gateway.py"]
    scripts_governance_d11_compliance_validate_commit_message_py["(生产态 / production) validatecommitmessage / Validate Commit Message<br/>validate_commit_message.py — Conventional Commits 校验（commit-msg hook）+ A...<br/>文件: d11_compliance/validate_commit_message.py"]
    scripts_governance_d11_compliance_validate_exit_codes_py["(生产态 / production) validateexit代码 / Validate Exit Codes<br/>validate_exit_codes.py — 审计脚本退出码规范门禁<br/>文件: d11_compliance/validate_exit_codes.py"]
    scripts_governance_d11_compliance_validate_frozen_requirements_py["(生产态 / production) validatefrozenrequirements / Validate Frozen Requirements<br/>validate_frozen_requirements.py — 依赖版本锁定与验证（蓝图 §34.2）<br/>文件: d11_compliance/validate_frozen_requirements.py"]
    scripts_governance_d11_compliance_validate_manifest_admission_py["(生产态 / production) validate清单准入 / Validate Manifest Admission<br/>Module docstring — see module-level docstring for details.<br/>文件: d11_compliance/validate_manifest_admission.py"]
    scripts_governance_d11_compliance_validate_no_utf8_bom_py["(生产态 / production) validatenoutf8bom / Validate No Utf8 Bom<br/>validate_no_utf8_bom.py — UTF-8 BOM 检测门禁<br/>文件: d11_compliance/validate_no_utf8_bom.py"]
    scripts_governance_d11_compliance_validate_script_naming_py["(生产态 / production) validatescript命名 / Validate Script Naming<br/>validate_script_naming.py — 审计脚本命名规范门禁<br/>文件: d11_compliance/validate_script_naming.py"]
    scripts_governance_d11_compliance_validate_script_quality_py["(生产态 / production) validatescript质量 / Validate Script Quality<br/>validate_script_quality.py — 治理脚本质量合规检查<br/>文件: d11_compliance/validate_script_quality.py"]
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py["(生产态 / production) validate任务decomposition旁路 / Validate Task Decomposition Bypass<br/>validate_task_decomposition_bypass.py — Task Decomposition Bypass 检测<br/>文件: d11_compliance/validate_task_decomposition_bypass.py"]
    scripts_governance_d11_compliance_validate_vocabulary_coverage_py["(生产态 / production) validatevocabularycoverage / Validate Vocabulary Coverage<br/>Module docstring — see module-level docstring for details.<br/>文件: d11_compliance/validate_vocabulary_coverage.py"]
    scripts_governance_d11_compliance_verify_audit_integrity_py["(生产态 / production) verify审计完整性 / Verify Audit Integrity<br/>verify_audit_integrity.py — MOD-INF-020 · 零依赖外部独立验证器<br/>文件: d11_compliance/verify_audit_integrity.py"]
    scripts_governance_d11_compliance_verify_schema_health_py["(生产态 / production) verifyschema健康 / Verify Schema Health<br/>verify_schema_health.py — depgraph (PostgreSQL) Schema 健康度校验门禁（#ARCH...<br/>文件: d11_compliance/verify_schema_health.py"]
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py["(生产态 / production) 检查日志器kwargs / Check Logger Kwargs<br/>========================================================<br/>文件: d12_ai_hallucination/check_logger_kwargs.py"]
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py["(生产态 / production) validate门禁提示词conflict / Validate Gate Prompt Conflict<br/>validate_gate_prompt_conflict.py — Gate-Prompt 冲突检测<br/>文件: d12_ai_hallucination/validate_gate_prompt_conflict.py"]
    scripts_governance_d12_ai_hallucination_validate_session_budget_py["(生产态 / production) validate会话预算 / Validate Session Budget<br/>validate_session_budget.py — Session 操作预算校验（已废弃）<br/>文件: d12_ai_hallucination/validate_session_budget.py"]
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py["(生产态 / production) validate会话门禁检查 / Validate Session Gate Check<br/>validate_session_gate_check.py — Session 门禁检查完整性校验<br/>文件: d12_ai_hallucination/validate_session_gate_check.py"]
    scripts_governance_d1_structure_archive_drafts_zone_py["(生产态 / production) archivedraftszone / Archive Drafts Zone<br/>草稿区生命周期归档器——扫描 arbitrated 草稿，按 age 判定 warn/archive/skip。<br/>文件: d1_structure/archive_drafts_zone.py"]
    scripts_governance_d1_structure_audit_config_format_py["(生产态 / production) 审计配置format / Audit Config Format<br/>audit_config_format.py — config/ 目录格式/注释/边界快速扫描<br/>文件: d1_structure/audit_config_format.py"]
    scripts_governance_d1_structure_audit_directory_integrity_py["(生产态 / production) 审计directory完整性 / Audit Directory Integrity<br/>audit_directory_integrity.py — 01_policies_and_standards/ 目录结构完整性审计<br/>文件: d1_structure/audit_directory_integrity.py"]
    scripts_governance_d1_structure_audit_directory_scalability_py["(生产态 / production) 审计directoryscalability / Audit Directory Scalability<br/>audit_directory_scalability.py -- 物理结构可扩展性审计 (1500模块支撑能力检查)<br/>文件: d1_structure/audit_directory_scalability.py"]
    scripts_governance_d1_structure_audit_findings_by_scope_py["(生产态 / production) 审计findingsbyscope / Audit Findings By Scope<br/>audit_findings_by_scope.py — 按目录范围筛选 Finding 报告<br/>文件: d1_structure/audit_findings_by_scope.py"]
    scripts_governance_d1_structure_batch_create_index_md_py["(生产态 / production) 批次create索引md / Batch Create Index Md<br/>Batch create index.md for all directories under docs/ that lack one.<br/>文件: d1_structure/batch_create_index_md.py"]
    scripts_governance_d1_structure_cbg_reset_py["(生产态 / production) cbg重置 / Cbg Reset<br/>CBG 熔断器重置 CLI (CircuitBreakerGateway Reset Command)<br/>文件: d1_structure/cbg_reset.py"]
    scripts_governance_d1_structure_check_directory_contract_py["(生产态 / production) 检查directorycontract / Check Directory Contract<br/>GATE-DIRECTORY-CONTRACT: Directory Contract validation gate.<br/>文件: d1_structure/check_directory_contract.py"]
    scripts_governance_d1_structure_check_handoff_manifests_py["(生产态 / production) 检查handoffmanifests / Check Handoff Manifests<br/>check_handoff_manifests.py — AI Session Handoff Manifest 完整性校验.<br/>文件: d1_structure/check_handoff_manifests.py"]
    scripts_governance_d1_structure_check_index_integrity_py["(生产态 / production) 检查索引完整性 / Check Index Integrity<br/>check_index_integrity.py — 索引完整性校验<br/>文件: d1_structure/check_index_integrity.py"]
    scripts_governance_d1_structure_cleanup_stash_py["(生产态 / production) 清理stash / Cleanup Stash<br/>cleanup_stash.py — git stash 堆积治理（OPS-2026062501 治本）<br/>文件: d1_structure/cleanup_stash.py"]
    scripts_governance_d1_structure_detect_orphan_py_py["(生产态 / production) 检测orphanpy / Detect Orphan Py<br/>detect_orphan_py.py — 全库孤儿 .py 文件检测<br/>文件: d1_structure/detect_orphan_py.py"]
    scripts_governance_d1_structure_detect_residual_files_py["(生产态 / production) 检测residualfiles / Detect Residual Files<br/>detect_residual_files.py — 残留物检测<br/>文件: d1_structure/detect_residual_files.py"]
    scripts_governance_d1_structure_detect_temp_files_py["(生产态 / production) 检测tempfiles / Detect Temp Files<br/>Module docstring — see module-level docstring for details.<br/>文件: d1_structure/detect_temp_files.py"]
    scripts_governance_d1_structure_drafts_zone_archiver_py["(生产态 / production) draftszonearchiver / Drafts Zone Archiver<br/>草稿区生命周期归档器 (Drafts Zone Lifecycle Archiver · V-16)<br/>文件: d1_structure/drafts_zone_archiver.py"]
    scripts_governance_d1_structure_generate_missing_index_md_py["(生产态 / production) generatemissing索引md / Generate Missing Index Md<br/>generate_missing_index_md.py — 扫描目录树，为缺失 index.md 的目录自动生成索...<br/>文件: d1_structure/generate_missing_index_md.py"]
    scripts_governance_d1_structure_reset_cbg_py["(生产态 / production) 重置cbg / Reset Cbg<br/>CBG 熔断器重置 CLI (CircuitBreakerGateway Reset Command)<br/>文件: d1_structure/reset_cbg.py"]
    scripts_governance_d1_structure_run_script_smoke_test_py["(生产态 / production) runscriptsmoke测试 / Run Script Smoke Test<br/>run_script_smoke_test.py — 治理脚本冒烟测试运行器<br/>文件: d1_structure/run_script_smoke_test.py"]
    scripts_governance_d1_structure_sync_index_from_manifest_py["(生产态 / production) 同步索引from清单 / Sync Index From Manifest<br/>sync_index_from_manifest.py — 从 script_manifest.yaml (SSoT) 自动同步 index....<br/>文件: d1_structure/sync_index_from_manifest.py"]
    scripts_governance_d1_structure_sync_policies_index_py["(生产态 / production) 同步policies索引 / Sync Policies Index<br/>sync_policies_index.py — 从磁盘实际扫描，自动同步 PS-IDX-001 §二 文件数量表格。<br/>文件: d1_structure/sync_policies_index.py"]
    scripts_governance_d1_structure_validate_config_integrity_py["(生产态 / production) validate配置完整性 / Validate Config Integrity<br/>validate_config_integrity.py — 运行时配置完整性十一层纵深审计 + 自动同步检测<br/>文件: d1_structure/validate_config_integrity.py"]
    scripts_governance_d1_structure_validate_d1_output_sanity_py["(生产态 / production) validated1输出sanity / Validate D1 Output Sanity<br/>validate_d1_output_sanity.py — D1 产出物合理性校验（蓝图 §31 B93）<br/>文件: d1_structure/validate_d1_output_sanity.py"]
    scripts_governance_d1_structure_validate_immutable_core_py["(生产态 / production) validateimmutable核心 / Validate Immutable Core<br/>validate_immutable_core.py — immutable_core 文件修改检测<br/>文件: d1_structure/validate_immutable_core.py"]
    scripts_governance_d1_structure_validate_index_reality_py["(生产态 / production) validate索引reality / Validate Index Reality<br/>Module docstring — see module-level docstring for details.<br/>文件: d1_structure/validate_index_reality.py"]
    scripts_governance_d1_structure_validate_read_before_write_py["(生产态 / production) validatereadbeforewrite / Validate Read Before Write<br/>validate_read_before_write.py — 先读后写校验（IRN-008）<br/>文件: d1_structure/validate_read_before_write.py"]
    scripts_governance_d2_links_audit_broken_links_py["(生产态 / production) 审计brokenlinks / Audit Broken Links<br/>检测文档/数据文件中的断链与幽灵引用。<br/>文件: d2_links/audit_broken_links.py"]
    scripts_governance_d2_links_detect_relative_references_py["(生产态 / production) 检测relativereferences / Detect Relative References<br/>detect_relative_references.py — 相对路径引用检测<br/>文件: d2_links/detect_relative_references.py"]
    scripts_governance_d3_metadata_auto_generate_index_py["(生产态 / production) 自动generate索引 / Auto Generate Index<br/>GATE-INDEX: Validate and auto-fix index.md factual accuracy.<br/>文件: d3_metadata/auto_generate_index.py"]
    scripts_governance_d3_metadata_backfill_doctype_metadata_py["(生产态 / production) backfilldoctypemetadata / Backfill Doctype Metadata<br/>批量回填 frontmatter doc_type 字段（doc_type 存量治理 Stage 2.1）<br/>文件: d3_metadata/backfill_doctype_metadata.py"]
    scripts_governance_d3_metadata_backfill_ttl_metadata_py["(生产态 / production) backfillTTLmetadata / Backfill TTL Metadata<br/>批量回填/重判 ttl 字段（6 格式统一入口，GATE-15 存量治理 + GATE-VOCAB-CHANGE ...<br/>文件: d3_metadata/backfill_ttl_metadata.py"]
    scripts_governance_d3_metadata_check_blueprint_compliance_py["(生产态 / production) 检查蓝图合规 / Check Blueprint Compliance<br/>(INVARIANTS) REQUIRED_SECTIONS 必须与蓝图+施工图模板 v2.1.0 COMPLIANCE_CHECKL...<br/>文件: d3_metadata/check_blueprint_compliance.py"]
    scripts_governance_d3_metadata_check_frontmatter_metadata_py["(生产态 / production) 检查frontmattermetadata / Check Frontmatter Metadata<br/>GATE-15: Frontmatter metadata validation（ttl + doc_type 字段校验）<br/>文件: d3_metadata/check_frontmatter_metadata.py"]
    scripts_governance_d3_metadata_check_module_singlesource_py["(生产态 / production) 检查模块singlesource / Check Module Singlesource<br/>GATE-SSOT-SINGLESOURCE: SSoT 单一真源门禁（Phase 7 治本防复发）。<br/>文件: d3_metadata/check_module_singlesource.py"]
    scripts_governance_d3_metadata_check_naming_convention_py["(生产态 / production) 检查命名约定 / Check Naming Convention<br/>GATE-11 命名规范门禁 — 全类型命名检测。<br/>文件: d3_metadata/check_naming_convention.py"]
    scripts_governance_d3_metadata_check_registry_consistency_py["(生产态 / production) 检查注册表一致性 / Check Registry Consistency<br/>check_registry_consistency — 跨登记表一致性校验。<br/>文件: d3_metadata/check_registry_consistency.py"]
    scripts_governance_d3_metadata_check_schema_version_writes_py["(生产态 / production) 检查schema版本writes / Check Schema Version Writes<br/>G_TRAE_059 验证脚本：_schema_version 写入保护 + 版本一致性检查。<br/>文件: d3_metadata/check_schema_version_writes.py"]
    scripts_governance_d3_metadata_check_vocab_hardcode_py["(生产态 / production) 检查vocabhardcode / Check Vocab Hardcode<br/>GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）<br/>文件: d3_metadata/check_vocab_hardcode.py"]
    scripts_governance_d3_metadata_classify_ttl_by_content_py["(生产态 / production) classifyTTLbycontent / Classify TTL By Content<br/>基于内容关键词的 ttl 精细分类审查脚本。<br/>文件: d3_metadata/classify_ttl_by_content.py"]
    scripts_governance_d3_metadata_deep_content_scanner_py["(生产态 / production) 深度contentscanner / Deep Content Scanner<br/>deep_content_scanner.py — 深度内容扫描器<br/>文件: d3_metadata/deep_content_scanner.py"]
    scripts_governance_d3_metadata_generate_derived_files_py["(生产态 / production) generatederivedfiles / Generate Derived Files<br/>generate_derived_files.py — 枚举自动派生生成器（Level 3 终极防御）<br/>文件: d3_metadata/generate_derived_files.py"]
    scripts_governance_d3_metadata_generate_rule_catalog_py["(生产态 / production) generate规则catalog / Generate Rule Catalog<br/>Scan docs/01_policies_and_standards and emit _registry/catalogs/rule_catalog_...<br/>文件: d3_metadata/generate_rule_catalog.py"]
    scripts_governance_d3_metadata_migrate_illegal_doctype_py["(生产态 / production) migrateillegaldoctype / Migrate Illegal Doctype<br/>批量迁移非法 doc_type 值（doc_type 存量治理 Stage 2.2）<br/>文件: d3_metadata/migrate_illegal_doctype.py"]
    scripts_governance_d3_metadata_validate_architecture_py["(生产态 / production) validate架构 / Validate Architecture<br/>validate_architecture.py - Validate rule files against architecture_contract....<br/>文件: d3_metadata/validate_architecture.py"]
    scripts_governance_d3_metadata_validate_blueprint_provenance_py["(生产态 / production) validate蓝图溯源 / Validate Blueprint Provenance<br/>Blueprint Provenance Gate - V-12: validate provenance triples in blueprint fr...<br/>文件: d3_metadata/validate_blueprint_provenance.py"]
    scripts_governance_d3_metadata_validate_module_id_py["(生产态 / production) validate模块id / Validate Module Id<br/>GATE-MODULEID: Validate module_id uniqueness and index/file consistency.<br/>文件: d3_metadata/validate_module_id.py"]
    scripts_governance_d3_metadata_validate_registry_master_index_py["(生产态 / production) validate注册表master索引 / Validate Registry Master Index<br/>登记表总索引自校验门禁 (Registry Master Index Self-Check Gate · V-18).<br/>文件: d3_metadata/validate_registry_master_index.py"]
    scripts_governance_d3_metadata_validate_tool_contracts_consistency_py["(生产态 / production) validatetool契约一致性 / Validate Tool Contracts Consistency<br/>Tool Contract 一致性校验脚本（MOD-INF-013 §9 R3）。<br/>文件: d3_metadata/validate_tool_contracts_consistency.py"]
    scripts_governance_d4_paths_detect_deprecated_path_writes_py["(生产态 / production) 检测deprecated路径writes / Detect Deprecated Path Writes<br/>detect_deprecated_path_writes.py — 废弃路径写入检测<br/>文件: d4_paths/detect_deprecated_path_writes.py"]
    scripts_governance_d4_paths_detect_excessive_file_moves_py["(生产态 / production) 检测excessive文件moves / Detect Excessive File Moves<br/>detect_excessive_file_moves.py — 文件过度搬迁检测<br/>文件: d4_paths/detect_excessive_file_moves.py"]
    scripts_governance_d4_paths_detect_ruins_references_py["(生产态 / production) 检测ruinsreferences / Detect Ruins References<br/>detect_ruins_references.py — 残骸/废弃路径引用检测<br/>文件: d4_paths/detect_ruins_references.py"]
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py["(生产态 / production) 检测splitdeleterefcommit / Detect Split Delete Ref Commit<br/>detect_split_delete_ref_commit.py — 删除引用分离提交检测<br/>文件: d4_paths/detect_split_delete_ref_commit.py"]
    scripts_governance_d5_architecture_analyze_change_impact_py["(生产态 / production) analyzechangeimpact / Analyze Change Impact<br/>Module docstring — see module-level docstring for details.<br/>文件: d5_architecture/analyze_change_impact.py"]
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py["(生产态 / production) analyzecontractimpact / Analyze Contract Impact<br/>analyze_contract_impact.py — 契约变更影响分析器<br/>文件: analyzers/analyze_contract_impact.py"]
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py["(生产态 / production) 审计dependson链depth / Audit Depends On Chain Depth<br/>audit_depends_on_chain_depth.py — depends_on 依赖链路深度审计<br/>文件: analyzers/audit_depends_on_chain_depth.py"]
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py["(生产态 / production) measuredeprecation级联 / Measure Deprecation Cascade<br/>measure_deprecation_cascade.py — 废弃级联影响度量<br/>文件: analyzers/measure_deprecation_cascade.py"]
    scripts_governance_d5_architecture_audit_agent_spec_py["(生产态 / production) 审计代理规格 / Audit Agent Spec<br/>(INVARIANTS) agent-spec 审计完整性<br/>文件: d5_architecture/audit_agent_spec.py"]
    scripts_governance_d5_architecture_check_budget_health_py["(生产态 / production) 检查预算健康 / Check Budget Health<br/>(INVARIANTS) 预算健康检查不可跳过;检查结果必须可机器解析<br/>文件: d5_architecture/check_budget_health.py"]
    scripts_governance_d5_architecture_check_drift_e2e_py["(生产态 / production) 检查漂移端到端 / Check Drift E2E<br/>CI Entry: Drift Detector E2E Pipeline Check<br/>文件: d5_architecture/check_drift_e2e.py"]
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py["(生产态 / production) 检查架构门禁 / Check Architecture Gates<br/>v2.4.0 — 2026-05-03<br/>文件: checkers/check_architecture_gates.py"]
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py["(生产态 / production) 检查蓝图automation同步 / Check Blueprint Automation Sync<br/>(INVARIANTS) 蓝图§5.5自动化触发机制状态列必须与代码实际实现一致; ⚠️待实现...<br/>文件: checkers/check_blueprint_automation_sync.py"]
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py["(生产态 / production) 检查蓝图代码对齐 / Check Blueprint Code Alignment<br/>(INVARIANTS) 代码(BLUEPRINT)头部module_id必须与蓝图注册表一致; 蓝图§4已实现...<br/>文件: checkers/check_blueprint_code_alignment.py"]
    scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py["(生产态 / production) 检查蓝图模板合规 / Check Blueprint Template Compliance<br/>(INVARIANTS) 蓝图模板合规检查不可绕过;52项检查全覆盖<br/>文件: checkers/check_blueprint_template_compliance.py"]
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py["(生产态 / production) 检查canonicalyaml漂移 / Check Canonical Yaml Drift<br/>check_canonical_yaml_drift.py — GATE-CANONICAL-YAML-DRIFT<br/>文件: checkers/check_canonical_yaml_drift.py"]
    scripts_governance_d5_architecture_checkers_check_code_duplication_py["(生产态 / production) 检查代码duplication / Check Code Duplication<br/>(INVARIANTS) 扫描 src/zephyr/ 下所有包; 检测跨包同名文件代码重复<br/>文件: checkers/check_code_duplication.py"]
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py["(生产态 / production) 检查contract代码漂移 / Check Contract Code Drift<br/>check_contract_code_drift.py —— 契约-代码双写漂移阻断（盲点 C2 修复）<br/>文件: checkers/check_contract_code_drift.py"]
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py["(生产态 / production) 检查contractphysical路径 / Check Contract Physical Path<br/>check_contract_physical_path.py — GATE-CONTRACT-PHYSICAL-PATH<br/>文件: checkers/check_contract_physical_path.py"]
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py["(生产态 / production) 检查依赖direction / Check Dependency Direction<br/>check_dependency_direction.py — 依赖方向校验（INJ-002/008）<br/>文件: checkers/check_dependency_direction.py"]
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py["(生产态 / production) 检查g6ctr合规 / Check G6 Ctr Compliance<br/>check_g6_ctr_compliance.py - G6 CTR Contract Compliance Gate Engine<br/>文件: checkers/check_g6_ctr_compliance.py"]
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py["(生产态 / production) 检查orphanoutputs / Check Orphan Outputs<br/>(INVARIANTS) 扫描蓝图 §11 产出物 consumer_min; 检测零消费者孤儿产出物<br/>文件: checkers/check_orphan_outputs.py"]
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py["(生产态 / production) 检查precommitiduniqueness / Check Precommit Id Uniqueness<br/>check_precommit_id_uniqueness.py — GATE-ID-UNIQ<br/>文件: checkers/check_precommit_id_uniqueness.py"]
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py["(生产态 / production) 检查规则fourway对齐 / Check Rule Four Way Alignment<br/>check_rule_four_way_alignment.py —— 规则四方对齐门禁（ARCH-020 补建）<br/>文件: checkers/check_rule_four_way_alignment.py"]
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py["(生产态 / production) 检查ssotuniqueness / Check Ssot Uniqueness<br/>(INVARIANTS) 扫描所有蓝图 ssot_claims 字段; 检测跨蓝图 SSoT 冲突<br/>文件: checkers/check_ssot_uniqueness.py"]
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py["(生产态 / production) 检查追踪上下文propagation / Check Trace Context Propagation<br/>check_trace_context_propagation.py — TraceContext 传播强制执行 CI 检查<br/>文件: checkers/check_trace_context_propagation.py"]
    scripts_governance_d5_architecture_checkers_check_vms_ssot_py["(生产态 / production) 检查VMSssot / Check VMS Ssot<br/>GATE-VMS-SSOT: VMS 单一真源门禁——三重检测。<br/>文件: checkers/check_vms_ssot.py"]
    scripts_governance_d5_architecture_dependency_graph_py["(生产态 / production) 依赖graph / Dependency Graph<br/>治理域有向依赖图 — 扫描 governance/ 下所有 import 生成依赖图.<br/>文件: d5_architecture/dependency_graph.py"]
    scripts_governance_d5_architecture_detect_causal_conflicts_py["(生产态 / production) 检测causalconflicts / Detect Causal Conflicts<br/>Module docstring — see module-level docstring for details.<br/>文件: d5_architecture/detect_causal_conflicts.py"]
    scripts_governance_d5_architecture_detect_constraint_violations_py["(生产态 / production) 检测约束violations / Detect Constraint Violations<br/>G9-Detect: 架构约束违规检测器（对照 depgraph 实际数据检测 6 类违规）<br/>文件: d5_architecture/detect_constraint_violations.py"]
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py["(生产态 / production) analyzesamename模块relations / Analyze Same Name Module Relations<br/>analyze_same_name_module_relations.py --- 同名模块语义关系分析<br/>文件: detectors/analyze_same_name_module_relations.py"]
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py["(生产态 / production) 检测dependsoncycles / Detect Depends On Cycles<br/>detect_depends_on_cycles.py - depends_on 环检测.<br/>文件: detectors/detect_depends_on_cycles.py"]
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py["(生产态 / production) 检测deprecatedadrreferences / Detect Deprecated Adr References<br/>detect_deprecated_adr_references.py — 废弃 ADR 引用检测<br/>文件: detectors/detect_deprecated_adr_references.py"]
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py["(生产态 / production) 检测duplicate模块names / Detect Duplicate Module Names<br/>detect_duplicate_module_names.py --- 同名模块语义关系分析<br/>文件: detectors/detect_duplicate_module_names.py"]
    scripts_governance_d5_architecture_diagnose_depgraph_py["(生产态 / production) diagnosedepgraph / Diagnose Depgraph<br/># (BLUEPRINT) MOD-INF-005 / scripts/governance/diagnose_depgraph.py / §7<br/>文件: d5_architecture/diagnose_depgraph.py"]
    scripts_governance_d5_architecture_generators_align_panoramas_py["(生产态 / production) alignpanoramas / Align Panoramas<br/>G-panorama-align: 四图对齐检测器（ARCH-053 + ARCH-056 四图升级）<br/>文件: generators/align_panoramas.py"]
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py["(生产态 / production) generateassetcatalog / Generate Asset Catalog<br/>G13: 从 depgraph (PostgreSQL) 生成资产清单全景图<br/>文件: generators/generate_asset_catalog.py"]
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py["(生产态 / production) generate蓝图panorama / Generate Blueprint Panorama<br/>G-panorama-gen: 蓝图 §0.6 四图对齐视图生成器（ARCH-053 + ARCH-056 + 模板 v2....<br/>文件: generators/generate_blueprint_panorama.py"]
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py["(生产态 / production) generate代码wikistats / Generate Code Wiki Stats<br/>Code Wiki 统计数据生成器（半自动维护机制）。<br/>文件: generators/generate_code_wiki_stats.py"]
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py["(生产态 / production) generatecontractcatalog / Generate Contract Catalog<br/>G12: 从 depgraph (PostgreSQL) 生成契约目录全景图<br/>文件: generators/generate_contract_catalog.py"]
    scripts_governance_d5_architecture_generators_generate_contracts_py["(生产态 / production) generate契约 / Generate Contracts<br/>generate_contracts.py -- SSoT to Codegen pipeline<br/>文件: generators/generate_contracts.py"]
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py["(生产态 / production) generate数据acquisition流 / Generate Data Acquisition Flow<br/>G-acqflow: 从 tasks.yaml 生成业务数据采集流图 MD（人类可读版，内嵌 Mermaid）<br/>文件: generators/generate_data_acquisition_flow.py"]
    scripts_governance_d5_architecture_generators_generate_data_inventory_py["(生产态 / production) generate数据inventory / Generate Data Inventory<br/>G-inventory: 扫描 ClickHouse 生成业务数据清单 MD<br/>文件: generators/generate_data_inventory.py"]
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py["(生产态 / production) generatedataflowdiagram / Generate Dataflow Diagram<br/>G-dataflow: 从 dataflowgraph (PostgreSQL) 生成数据流图 Markdown 文档（内嵌 Me...<br/>文件: generators/generate_dataflow_diagram.py"]
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py["(生产态 / production) generate决策diagram / Generate Decision Diagram<br/>G-decision: 从 decisiongraph (PostgreSQL) 生成决策流图(.md 文档，Mermaid 内嵌)<br/>文件: generators/generate_decision_diagram.py"]
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py["(生产态 / production) generatepanorama注册表 / Generate Panorama Registry<br/>G-panorama-registry: 自动生成全景图清单总表<br/>文件: generators/generate_panorama_registry.py"]
    scripts_governance_d5_architecture_generators_generate_policies_py["(生产态 / production) generatepolicies / Generate Policies<br/>#183: 从 data_sources_registry.yaml 派生 policies.yaml<br/>文件: generators/generate_policies.py"]
    scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py["(生产态 / production) generatetrading流diagram / Generate Trading Flow Diagram<br/>G-trading-flow: 从 decisiongraph + 叙事YAML + 候选库 生成交易决策架构视图(.md)<br/>文件: generators/generate_trading_flow_diagram.py"]
    scripts_governance_d5_architecture_pre_delete_safety_check_py["(生产态 / production) 预delete安全检查 / Pre Delete Safety Check<br/>安全删除门禁脚本——RULE-THREE 强制执行器。<br/>文件: d5_architecture/pre_delete_safety_check.py"]
    scripts_governance_d5_architecture_pre_write_gate_py["(生产态 / production) 预write门禁 / Pre Write Gate<br/>AI写入前强制门禁钩子: lock协议检查+GateEngine Phase评估+注册完整性验证<br/>文件: d5_architecture/pre_write_gate.py"]
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py["(生产态 / production) archiverationalelog / Archive Rationale Log<br/>对标 HDEBT-01：rationale-log.md 体积 >150KB / 行数 >300 时，<br/>文件: syncers/archive_rationale_log.py"]
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py["(生产态 / production) mergereadme转索引 / Merge Readme To Index<br/>Strategy:<br/>文件: syncers/merge_readme_to_index.py"]
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py["(生产态 / production) 同步蓝图代码索引 / Sync Blueprint Code Index<br/>对标：AGENTS.md §6.1 蓝图-代码同步强制约定<br/>文件: syncers/sync_blueprint_code_index.py"]
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py["(生产态 / production) 同步注册表fromblueprints / Sync Registry From Blueprints<br/>sync_registry_from_blueprints.py -- 从 blueprint.md frontmatter 同步 blueprin...<br/>文件: syncers/sync_registry_from_blueprints.py"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py["(生产态 / production) validate蓝图代码同步 / Validate Blueprint Code Sync<br/>AGENTS.md §6.1 蓝图-代码同步强制约定的 CI 门禁脚本。<br/>文件: blueprint/validate_blueprint_code_sync.py"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py["(生产态 / production) validate蓝图implementationdocs / Validate Blueprint Implementation Docs<br/>AGENTS.md 6.4 铁律五 + 铁律六：蓝图中声称的文件路径必须在磁盘上真实存在。<br/>文件: blueprint/validate_blueprint_implementation_docs.py"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py["(生产态 / production) validate蓝图路径一致性 / Validate Blueprint Path Consistency<br/>Module docstring — see module-level docstring for details.<br/>文件: blueprint/validate_blueprint_path_consistency.py"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py["(生产态 / production) validate蓝图placement / Validate Blueprint Placement<br/>蓝图物理位置与归属链完整性校验器 (Blueprint Placement & BelongsTo Validator)<br/>文件: blueprint/validate_blueprint_placement.py"]
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py["(生产态 / production) validate蓝图标签uniqueness / Validate Blueprint Tag Uniqueness<br/>GATE-TAG-UNIQUE - Blueprint tag uniqueness validation gate.<br/>文件: blueprint/validate_blueprint_tag_uniqueness.py"]
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py["(生产态 / production) validate生命周期refs / Validate Lifecycle Refs<br/>validate_lifecycle_refs.py — 生命周期引用约束合规检查<br/>文件: lifecycle/validate_lifecycle_refs.py"]
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py["(生产态 / production) validate模块生命周期 / Validate Module Lifecycle<br/>validate_module_lifecycle.py — 模块生命周期校验<br/>文件: lifecycle/validate_module_lifecycle.py"]
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py["(生产态 / production) validate会话log索引完整性 / Validate Session Log Index Integrity<br/>Module docstring — see module-level docstring for details.<br/>文件: session/validate_session_log_index_integrity.py"]
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py["(生产态 / production) validate会话logupdated / Validate Session Log Updated<br/>validate_session_log_updated.py — Session Log 更新状态校验<br/>文件: session/validate_session_log_updated.py"]
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py["(生产态 / production) validateadrfrontmatter一致性 / Validate Adr Frontmatter Consistency<br/>validate_adr_frontmatter_consistency.py — ADR frontmatter 一致性闸门（GATE-A...<br/>文件: validators/validate_adr_frontmatter_consistency.py"]
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py["(生产态 / production) validate架构审查门禁 / Validate Arch Review Gate<br/>validate_arch_review_gate.py — 架构评审门控校验<br/>文件: validators/validate_arch_review_gate.py"]
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py["(生产态 / production) validate架构contractinternal / Validate Architecture Contract Internal<br/>GATE-CONTRACT: CI gate for architecture_contract.yaml internal consistency.<br/>文件: validators/validate_architecture_contract_internal.py"]
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py["(生产态 / production) validateautonomy门禁 / Validate Autonomy Gate<br/>validate_autonomy_gate.py — 变更级别 vs AI 自治权限交叉校验<br/>文件: validators/validate_autonomy_gate.py"]
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py["(生产态 / production) validatebtrackpackages / Validate B Track Packages<br/>validate_b_track_packages.py — B 轨 b_track 一致性校验<br/>文件: validators/validate_b_track_packages.py"]
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py["(生产态 / production) validate盲点点status / Validate Blind Spot Status<br/>GATE-BS: Blind Spot Reality Check<br/>文件: validators/validate_blind_spot_status.py"]
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py["(生产态 / production) validate代码yaml对齐 / Validate Code Yaml Alignment<br/>validate_code_yaml_alignment.py — GATE-A: 实际代码 ↔ YAML SSoT 对账<br/>文件: validators/validate_code_yaml_alignment.py"]
    scripts_governance_d5_architecture_validators_validate_cross_references_py["(生产态 / production) validate跨references / Validate Cross References<br/>validate_cross_references.py — 架构模型 YAML + 治理文档跨引用完整性闸门（GAT...<br/>文件: validators/validate_cross_references.py"]
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py["(生产态 / production) validate依赖graph模板 / Validate Dependency Graph Template<br/>(INVARIANTS) 治理脚本执行正确<br/>文件: validators/validate_dependency_graph_template.py"]
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py["(生产态 / production) validatedependsonformat / Validate Depends On Format<br/>validate_depends_on_format.py — depends_on 条目结构化格式校验<br/>文件: validators/validate_depends_on_format.py"]
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py["(生产态 / production) validatedeprecateddependents / Validate Deprecated Dependents<br/>validate_deprecated_dependents.py — 废弃文件活跃引用检测<br/>文件: validators/validate_deprecated_dependents.py"]
    scripts_governance_d5_architecture_validators_validate_directory_structure_py["(生产态 / production) validatedirectorystructure / Validate Directory Structure<br/>Module docstring — see module-level docstring for details.<br/>文件: validators/validate_directory_structure.py"]
    scripts_governance_d5_architecture_validators_validate_field_ownership_py["(生产态 / production) validatefieldownership / Validate Field Ownership<br/>validate_field_ownership.py — frontmatter 字段归属校验<br/>文件: validators/validate_field_ownership.py"]
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py["(生产态 / production) validate门禁yaml / Validate Gate Yaml<br/>Module docstring — see module-level docstring for details.<br/>文件: validators/validate_gate_yaml.py"]
    scripts_governance_d5_architecture_validators_validate_handoff_package_py["(生产态 / production) validatehandoffpackage / Validate Handoff Package<br/>validate_handoff_package.py — HandoffPackage 完整性校验<br/>文件: validators/validate_handoff_package.py"]
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py["(生产态 / production) validateinterface契约 / Validate Interface Contracts<br/>validate_interface_contracts.py — 接口契约校验<br/>文件: validators/validate_interface_contracts.py"]
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py["(生产态 / production) validateload路径完整性 / Validate Load Path Integrity<br/>Module docstring — see module-level docstring for details.<br/>文件: validators/validate_load_path_integrity.py"]
    scripts_governance_d5_architecture_validators_validate_module_schema_py["(生产态 / production) validate模块schema / Validate Module Schema<br/>validate_module_schema.py — 模块 Schema 校验（INJ-003/004/005/006）<br/>文件: validators/validate_module_schema.py"]
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py["(生产态 / production) validatenestedflatdirs / Validate Nested Flat Dirs<br/>Module docstring — see module-level docstring for details.<br/>文件: validators/validate_nested_flat_dirs.py"]
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py["(生产态 / production) validatep0模块契约 / Validate P0 Module Contracts<br/>validate_p0_module_contracts.py — P0 模块契约校验<br/>文件: validators/validate_p0_module_contracts.py"]
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py["(生产态 / production) validatestatic清单漂移 / Validate Static Manifest Drift<br/>validate_static_manifest_drift.py — GATE-21 静态清单漂移阻断<br/>文件: validators/validate_static_manifest_drift.py"]
    scripts_governance_d5_architecture_validators_validate_target_layer_py["(生产态 / production) validatetarget层 / Validate Target Layer<br/>对标：target_layer_vocabulary.yaml v1.0.0——target_layer 字段值体系多真源不...<br/>文件: validators/validate_target_layer.py"]
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py["(生产态 / production) validatethreeway一致性 / Validate Three Way Consistency<br/>validate_three_way_consistency.py — 三方一致性检查<br/>文件: validators/validate_three_way_consistency.py"]
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py["(生产态 / production) validatemdyamlnumber漂移 / Validate Md Yaml Number Drift<br/>validate_md_yaml_number_drift.py — MD 视图与 YAML SSoT 数字漂移检测闸门（GAT...<br/>文件: yaml_md/validate_md_yaml_number_drift.py"]
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py["(生产态 / production) validateyamlinterfaceuniqueness / Validate Yaml Interface Uniqueness<br/>validate_yaml_interface_uniqueness.py — YAML 模块接口唯一性闸门（GATE-IFACE-...<br/>文件: yaml_md/validate_yaml_interface_uniqueness.py"]
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py["(生产态 / production) validateyamlsummaries / Validate Yaml Summaries<br/>v1.0.0 -- 2026-05-03<br/>文件: yaml_md/validate_yaml_summaries.py"]
    scripts_governance_d6_security_check_protected_paths_py["(生产态 / production) 检查protectedpaths / Check Protected Paths<br/>check_protected_paths.py — 受保护路径写入检查（IRN-010）<br/>文件: d6_security/check_protected_paths.py"]
    scripts_governance_d6_security_detect_anchor_file_deletion_py["(生产态 / production) 检测anchor文件deletion / Detect Anchor File Deletion<br/>detect_anchor_file_deletion.py — 锚点文件删除检测<br/>文件: d6_security/detect_anchor_file_deletion.py"]
    scripts_governance_d6_security_detect_git_dangerous_py["(生产态 / production) 检测gitdangerous / Detect Git Dangerous<br/>detect_git_dangerous.py — 危险 Git 命令检测<br/>文件: d6_security/detect_git_dangerous.py"]
    scripts_governance_d6_security_detect_keywords_in_logs_py["(生产态 / production) 检测keywordsinlogs / Detect Keywords In Logs<br/>detect_keywords_in_logs.py — 日志输出敏感关键词检测<br/>文件: d6_security/detect_keywords_in_logs.py"]
    scripts_governance_d6_security_detect_permanent_file_deletion_py["(生产态 / production) 检测permanent文件deletion / Detect Permanent File Deletion<br/>detect_permanent_file_deletion.py — 永久文件删除检测<br/>文件: d6_security/detect_permanent_file_deletion.py"]
    scripts_governance_d6_security_detect_secrets_py["(生产态 / production) 检测密钥 / Detect Secrets<br/>detect_secrets.py — 密钥/Token/凭证硬编码检测<br/>文件: d6_security/detect_secrets.py"]
    scripts_governance_d6_security_detect_shell_dangerous_py["(生产态 / production) 检测shelldangerous / Detect Shell Dangerous<br/>detect_shell_dangerous.py — 危险 Shell 命令检测<br/>文件: d6_security/detect_shell_dangerous.py"]
    scripts_governance_d6_security_detect_shell_true_py["(生产态 / production) 检测shelltrue / Detect Shell True<br/>detect_shell_true.py — shell=True 调用检测<br/>文件: d6_security/detect_shell_true.py"]
    scripts_governance_d6_security_detect_threading_lock_py["(生产态 / production) 检测threadinglock / Detect Threading Lock<br/>detect_threading_lock.py — threading.Lock 导入检测<br/>文件: d6_security/detect_threading_lock.py"]
    scripts_governance_d6_security_detect_vague_terms_py["(生产态 / production) 检测vagueterms / Detect Vague Terms<br/>detect_vague_terms.py — 模糊/不确定术语检测<br/>文件: d6_security/detect_vague_terms.py"]
    scripts_governance_d6_security_retire_tmp_artifacts_py["(生产态 / production) retiretmpartifacts / Retire Tmp Artifacts<br/>retire_tmp_artifacts — tmp/ + logs/ 退役区 TTL 执行器（AI-03 审计 P2/P3 治本）<br/>文件: d6_security/retire_tmp_artifacts.py"]
    scripts_governance_d6_security_run_adversarial_checks_py["(生产态 / production) run对抗checks / Run Adversarial Checks<br/>CI Entry: Adversarial Validation — Red-Blue Drift Test<br/>文件: d6_security/run_adversarial_checks.py"]
    scripts_governance_d6_security_scan_runtime_log_secrets_py["(生产态 / production) scan运行时log密钥 / Scan Runtime Log Secrets<br/>对标 architecture_principles.md §2bis R2 安全红线：<br/>文件: d6_security/scan_runtime_log_secrets.py"]
    scripts_governance_d6_security_scan_secret_leak_py["(生产态 / production) scansecretleak / Scan Secret Leak<br/>对标 06-security_architecture.md §6.3 L3-Audit：<br/>文件: d6_security/scan_secret_leak.py"]
    scripts_governance_d6_security_validate_gate_discipline_py["(生产态 / production) validate门禁discipline / Validate Gate Discipline<br/>validate_gate_discipline.py — 门禁纪律校验<br/>文件: d6_security/validate_gate_discipline.py"]
    scripts_governance_d7_code_any_type_inferrer_py["(生产态 / production) anytypeinferrer / Any Type Inferrer<br/>裸 Any 类型推断辅助工具 — #ARCH-ANY-GOVERNANCE-001 Phase 1.<br/>文件: d7_code/any_type_inferrer.py"]
    scripts_governance_d7_code_check_ai_capability_boundary_py["(生产态 / production) 检查AI能力boundary / Check AI Capability Boundary<br/>行为说明<br/>文件: d7_code/check_ai_capability_boundary.py"]
    scripts_governance_d7_code_check_encoding_py["(生产态 / production) 检查encoding / Check Encoding<br/>check_encoding.py — 编码合规校验（INJ-007）<br/>文件: d7_code/check_encoding.py"]
    scripts_governance_d7_code_check_idempotency_py["(生产态 / production) 检查idempotency / Check Idempotency<br/>check_idempotency.py — 幂等性缺失检查（HC-9）<br/>文件: d7_code/check_idempotency.py"]
    scripts_governance_d7_code_check_merge_conflict_py["(生产态 / production) 检查mergeconflict / Check Merge Conflict<br/>check_merge_conflict.py — 合并冲突标记检测（local 替代 external pre-commit-h...<br/>文件: d7_code/check_merge_conflict.py"]
    scripts_governance_d7_code_check_no_tests_unit_py["(生产态 / production) 检查notestsunit / Check No Tests Unit<br/>check_no_tests_unit.py — 禁止 tests/unit/ 旧路径重引入检测（local 替代 pygrep）<br/>文件: d7_code/check_no_tests_unit.py"]
    scripts_governance_d7_code_check_pit_compliance_py["(生产态 / production) 检查pit合规 / Check Pit Compliance<br/>check_pit_compliance.py — PIT 合规检查（HC-10）<br/>文件: d7_code/check_pit_compliance.py"]
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py["(生产态 / production) 检测absolute路径hardcoding / Detect Absolute Path Hardcoding<br/>detect_absolute_path_hardcoding.py — 绝对路径硬编码检测（蓝图 §34.1 操作陷阱）<br/>文件: d7_code/detect_absolute_path_hardcoding.py"]
    scripts_governance_d7_code_detect_direct_llm_calls_py["(生产态 / production) 检测directLLMcalls / Detect Direct LLM Calls<br/>detect_direct_llm_calls.py — 裸调 LLM API 检测门禁（GATE-20）<br/>文件: d7_code/detect_direct_llm_calls.py"]
    scripts_governance_d7_code_detect_forward_reference_py["(生产态 / production) 检测forwardreference / Detect Forward Reference<br/>detect_forward_reference — 前向引用检测扫描器。<br/>文件: d7_code/detect_forward_reference.py"]
    scripts_governance_d7_code_detect_missing_encoding_py["(生产态 / production) 检测missingencoding / Detect Missing Encoding<br/>detect_missing_encoding.py — open() 缺 encoding 检测<br/>文件: d7_code/detect_missing_encoding.py"]
    scripts_governance_d7_code_detect_private_key_py["(生产态 / production) 检测privatekey / Detect Private Key<br/>detect_private_key.py — 私钥意外提交检测（local 替代 external pre-commit-hooks）<br/>文件: d7_code/detect_private_key.py"]
    scripts_governance_d7_code_detect_pydantic_any_fields_py["(生产态 / production) 检测pydanticanyfields / Detect Pydantic Any Fields<br/>detect_pydantic_any_fields.py — Pydantic Any 类型字段检测<br/>文件: d7_code/detect_pydantic_any_fields.py"]
    scripts_governance_d7_code_detect_silent_degradation_py["(生产态 / production) 检测silent降级 / Detect Silent Degradation<br/>detect_silent_degradation.py — 静默降级检测<br/>文件: d7_code/detect_silent_degradation.py"]
    scripts_governance_d7_code_fix_n06_scope_py["(生产态 / production) 修复n06scope / Fix N06 Scope<br/>N-06 module_id scope 前缀检测修复脚本。<br/>文件: d7_code/fix_n06_scope.py"]
    scripts_governance_d7_code_fix_n12_ke_naming_py["(生产态 / production) 修复n12ke命名 / Fix N12 Ke Naming<br/>N-12 KE 条目命名格式批量修复脚本。<br/>文件: d7_code/fix_n12_ke_naming.py"]
    scripts_governance_d7_code_fix_n13_snake_case_py["(生产态 / production) 修复n13snakecase / Fix N13 Snake Case<br/>N-13 YAML/JSON/MD 文件名 snake_case 批量修复脚本。<br/>文件: d7_code/fix_n13_snake_case.py"]
    scripts_governance_d7_code_fix_n14_init_all_py["(生产态 / production) 修复n14init全量 / Fix N14 Init All<br/>N-14 __init__.py 缺少 __all__ 批量修复脚本。<br/>文件: d7_code/fix_n14_init_all.py"]
    scripts_governance_d7_code_fix_n15_blueprint_path_py["(生产态 / production) 修复n15蓝图路径 / Fix N15 Blueprint Path<br/>N-15 BLUEPRINT 头部路径不存在批量修复脚本。<br/>文件: d7_code/fix_n15_blueprint_path.py"]
    scripts_governance_d7_code_fix_naming_manual_py["(生产态 / production) 修复命名手册 / Fix Naming Manual<br/>fix_naming_manual — 手动修复少量命名违规(N-11/N-10/N-03/N-09/N-16)。<br/>文件: d7_code/fix_naming_manual.py"]
    scripts_governance_d7_code_fix_orphan_exports_py["(生产态 / production) 修复orphanexports / Fix Orphan Exports<br/>fix_orphan_exports.py — 批量修复孤儿模块导出（RULE-TWO 防线 2 修复器）<br/>文件: d7_code/fix_orphan_exports.py"]
    scripts_governance_d7_code_rewrite_imports_py["(生产态 / production) rewriteimports / Rewrite Imports<br/>rewrite_imports.py — 批量重写 Python import 路径（AST-based）<br/>文件: d7_code/rewrite_imports.py"]
    scripts_governance_d7_code_scan_complexity_py["(生产态 / production) scancomplexity / Scan Complexity<br/>全量循环复杂度扫描器 — §5.158 暗债监控（裁定#214 Phase 4 引入）。<br/>文件: d7_code/scan_complexity.py"]
    scripts_governance_d7_code_scan_consumers_accuracy_py["(生产态 / production) scanconsumersaccuracy / Scan Consumers Accuracy<br/>scan_consumers_accuracy.py — CONSUMERS 字段准确性 baseline-scan 脚本<br/>文件: d7_code/scan_consumers_accuracy.py"]
    scripts_governance_d7_code_scan_debt_py["(生产态 / production) scandebt / Scan Debt<br/>架构债务扫描器 — 5.96 维度防御门闸（R67 引入）。<br/>文件: d7_code/scan_debt.py"]
    scripts_governance_d7_code_validate_contracts_purity_py["(生产态 / production) validate契约purity / Validate Contracts Purity<br/>validate_contracts_purity.py — 契约纯度校验<br/>文件: d7_code/validate_contracts_purity.py"]
    scripts_governance_d7_code_validate_docstring_coverage_py["(生产态 / production) validatedocstringcoverage / Validate Docstring Coverage<br/>validate_docstring_coverage.py — Docstring 覆盖率校验<br/>文件: d7_code/validate_docstring_coverage.py"]
    scripts_governance_d7_code_validate_fle_action_metadata_py["(生产态 / production) validatefle动作metadata / Validate Fle Action Metadata<br/>validate_fle_action_metadata.py — FLE Action 元数据校验<br/>文件: d7_code/validate_fle_action_metadata.py"]
    scripts_governance_d7_code_validate_fle_imports_py["(生产态 / production) validatefleimports / Validate Fle Imports<br/>validate_fle_imports.py — FLE import 接口合规检测<br/>文件: d7_code/validate_fle_imports.py"]
    scripts_governance_d7_code_validate_import_style_py["(生产态 / production) validate导入style / Validate Import Style<br/>validate_import_style.py — 导入风格一致性校验<br/>文件: d7_code/validate_import_style.py"]
    scripts_governance_d7_code_validate_init_all_py["(生产态 / production) validateinit全量 / Validate Init All<br/>validate_init_all.py — __init__.py __all__ 完整性校验<br/>文件: d7_code/validate_init_all.py"]
    scripts_governance_d7_code_validate_kb_write_provenance_py["(生产态 / production) validate知识库write溯源 / Validate KB Write Provenance<br/>validate_kb_write_provenance.py — 知识库写入 provenance 校验<br/>文件: d7_code/validate_kb_write_provenance.py"]
    scripts_governance_d7_code_validate_python_syntax_py["(生产态 / production) validatepythonsyntax / Validate Python Syntax<br/>validate_python_syntax.py — Python 语法完整性校验<br/>文件: d7_code/validate_python_syntax.py"]
    scripts_governance_d7_code_validate_test_assertion_depth_py["(生产态 / production) validate测试assertiondepth / Validate Test Assertion Depth<br/>validate_test_assertion_depth.py — 测试断言深度校验<br/>文件: d7_code/validate_test_assertion_depth.py"]
    scripts_governance_d7_code_validate_test_coverage_py["(生产态 / production) validate测试coverage / Validate Test Coverage<br/>validate_test_coverage.py — 测试覆盖率治理校验器<br/>文件: d7_code/validate_test_coverage.py"]
    scripts_governance_d7_code_validate_type_annotation_coverage_py["(生产态 / production) validatetypeannotationcoverage / Validate Type Annotation Coverage<br/>validate_type_annotation_coverage.py — 类型注解覆盖率校验<br/>文件: d7_code/validate_type_annotation_coverage.py"]
    scripts_governance_d7_code_validate_unused_imports_py["(生产态 / production) validateunusedimports / Validate Unused Imports<br/>validate_unused_imports.py — 未使用导入检测<br/>文件: d7_code/validate_unused_imports.py"]
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py["(生产态 / production) 自动同步全量registries / Auto Sync All Registries<br/>全自动注册表同步器<br/>文件: d8_doc_sync/auto_sync_all_registries.py"]
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py["(生产态 / production) 检测AIproductsindocs / Detect AI Products In Docs<br/>detect_ai_products_in_docs.py — AI 产物位置检测<br/>文件: d8_doc_sync/detect_ai_products_in_docs.py"]
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py["(生产态 / production) 检测datedsnapshots / Detect Dated Snapshots<br/>detect_dated_snapshots.py — 带日期快照文件检测<br/>文件: d8_doc_sync/detect_dated_snapshots.py"]
    scripts_governance_d8_doc_sync_sync_rule_registry_py["(生产态 / production) 同步规则注册表 / Sync Rule Registry<br/>Checks that every RULE-ZERO through RULE-N in .trae/rules/project_rules.md<br/>文件: d8_doc_sync/sync_rule_registry.py"]
    scripts_governance_d8_doc_sync_update_progress_py["(生产态 / production) updateprogress / Update Progress<br/>update_progress.py — 从 domain_progress.json 批量更新施工进度.<br/>文件: d8_doc_sync/update_progress.py"]
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py["(生产态 / production) validatedocument生命周期 / Validate Document Lifecycle<br/>validate_document_lifecycle.py — 文档生命周期校验<br/>文件: d8_doc_sync/validate_document_lifecycle.py"]
    scripts_governance_d8_doc_sync_validate_document_ttl_py["(生产态 / production) validatedocumentTTL / Validate Document TTL<br/>validate_document_ttl.py — 文档 TTL 过期检测<br/>文件: d8_doc_sync/validate_document_ttl.py"]
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py["(生产态 / production) 检测duplicatednormativelanguage / Detect Duplicated Normative Language<br/>detect_duplicated_normative_language.py — 规范用语重复定义检测<br/>文件: d9_knowledge/detect_duplicated_normative_language.py"]
    scripts_governance_d9_knowledge_detect_orphan_documents_py["(生产态 / production) 检测orphandocuments / Detect Orphan Documents<br/>detect_orphan_documents.py — 孤立文档检测<br/>文件: d9_knowledge/detect_orphan_documents.py"]
    scripts_governance_data_quality_check_tick_duplication_py["(生产态 / production) 检查tickduplication / Check Tick Duplication<br/>tick_data 表真重复检查工具（RULE-DATA-OPS 配套，TRAE-063 §invariants DATA-OP...<br/>文件: data_quality/check_tick_duplication.py"]
    scripts_governance_extract_decisiongraph_py["(生产态 / production) extractdecisiongraph / Extract Decisiongraph<br/>extract_decisiongraph - decisiongraph on-demand extraction tool<br/>文件: governance/extract_decisiongraph.py"]
    scripts_governance_extract_depgraph_py["(生产态 / production) extractdepgraph / Extract Depgraph<br/>(INVARIANTS) 禁止AI直接Read 157MB depgraph文件；提取输出必须可被AI安全消费<br/>文件: governance/extract_depgraph.py"]
    scripts_governance_generate_decision_graph_py["(生产态 / production) generate决策graph / Generate Decision Graph<br/>(INVARIANTS) YAML 是唯一真源; DB 为只读缓存; 同步单向 YAML→DB; 不变量校验前置<br/>文件: governance/generate_decision_graph.py"]
    scripts_governance_generate_project_depgraph_py["(生产态 / production) generateprojectdepgraph / Generate Project Depgraph<br/># (BLUEPRINT) MOD-INF-005 / scripts/governance/generate_project_depgraph.py / §7<br/>文件: governance/generate_project_depgraph.py"]
    scripts_governance_generate_project_path_tree_py["(生产态 / production) generateproject路径tree / Generate Project Path Tree<br/>从磁盘扫描生成路径全景图的tree段（运营态目录结构）。<br/>文件: governance/generate_project_path_tree.py"]
    scripts_governance_generators_check_gate_inventory_drift_py["(生产态 / production) 检查门禁inventory漂移 / Check Gate Inventory Drift<br/>check_gate_inventory_drift.py — commit_gates 模块清单漂移检测（ARCH-055 治本）<br/>文件: generators/check_gate_inventory_drift.py"]
    scripts_governance_generators_fix_module_manifest_layout_py["(生产态 / production) 修复模块清单layout / Fix Module Manifest Layout<br/>fix_module_manifest_layout.py — 校正治理脚本模块 docstring 与 ``__manifest__...<br/>文件: generators/fix_module_manifest_layout.py"]
    scripts_governance_generators_generate_gate_registry_py["(生产态 / production) generate门禁注册表 / Generate Gate Registry<br/>generate_gate_registry.py — 门禁登记表自动生成器<br/>文件: generators/generate_gate_registry.py"]
    scripts_governance_generators_generate_path_ownership_map_py["(生产态 / production) generate路径ownershipmap / Generate Path Ownership Map<br/>从蓝图§0.1聚合生成 path_ownership_map.yaml 路径归属声明。<br/>文件: generators/generate_path_ownership_map.py"]
    scripts_governance_generators_generate_registry_master_index_py["(生产态 / production) generate注册表master索引 / Generate Registry Master Index<br/>generate_registry_master_index.py — 登记表总索引自动生成器<br/>文件: generators/generate_registry_master_index.py"]
    scripts_governance_generators_inject_manifests_py["(生产态 / production) injectmanifests / Inject Manifests<br/>inject_manifests.py — __manifest__ 批量注入器<br/>文件: generators/inject_manifests.py"]
    scripts_governance_generators_refresh_master_entries_py["(生产态 / production) refreshmasterentries / Refresh Master Entries<br/>refresh_master_entries.py — 登记表总索引 entries 自动刷新器<br/>文件: generators/refresh_master_entries.py"]
    scripts_governance_generators_sync_audit_protocol_numbers_py["(生产态 / production) 同步审计协议numbers / Sync Audit Protocol Numbers<br/>sync_audit_protocol_numbers.py — 从 SSoT 注册表自动同步审计协议中的硬编码数字。<br/>文件: generators/sync_audit_protocol_numbers.py"]
    scripts_governance_git_health_smoke_py["(生产态 / production) git健康smoke / Git Health Smoke<br/>git_health_smoke.py — Git 健康度 smoke test（ARCH-GIT-CALL-BUDGET P3.2）<br/>文件: governance/git_health_smoke.py"]
    scripts_governance_meta_arbitrate_findings_py["(生产态 / production) arbitratefindings / Arbitrate Findings<br/>arbitrate_findings.py — Finding 仲裁器（跨脚本冲突解决引擎）<br/>文件: meta/arbitrate_findings.py"]
    scripts_governance_meta_benchmark_test_fixtures_bad_imports_py["(生产态 / production) badimports / Bad Imports<br/>Module docstring — see module-level docstring for details.<br/>文件: test_fixtures/bad_imports.py"]
    scripts_governance_meta_compute_sla_metrics_py["(生产态 / production) computesla指标 / Compute Sla Metrics<br/>compute_sla_metrics.py — SLA/SLO 指标计算引擎（蓝图 §8.4）<br/>文件: meta/compute_sla_metrics.py"]
    scripts_governance_meta_create_task_from_finding_py["(生产态 / production) create任务from发现 / Create Task From Finding<br/>create_task_from_finding.py — Finding → 任务卡自动创建引擎<br/>文件: meta/create_task_from_finding.py"]
    scripts_governance_meta_detect_config_deviation_py["(生产态 / production) 检测配置deviation / Detect Config Deviation<br/>detect_config_deviation.py — 配置文件结构完整性检测（蓝图 §28 B65 + B87）<br/>文件: meta/detect_config_deviation.py"]
    scripts_governance_meta_detect_fix_oscillation_py["(生产态 / production) 检测修复oscillation / Detect Fix Oscillation<br/>detect_fix_oscillation.py — 自修复振荡检测（蓝图 §28 B64）<br/>文件: meta/detect_fix_oscillation.py"]
    scripts_governance_meta_detect_hallucinated_packages_py["(生产态 / production) 检测hallucinatedpackages / Detect Hallucinated Packages<br/>detect_hallucinated_packages.py — 幻觉包（Slopsquatting）防御引擎<br/>文件: meta/detect_hallucinated_packages.py"]
    scripts_governance_meta_detect_script_divergence_py["(生产态 / production) 检测scriptdivergence / Detect Script Divergence<br/>detect_script_divergence.py — 脚本实现与蓝图规范分歧检测（蓝图 §27.3 B81）<br/>文件: meta/detect_script_divergence.py"]
    scripts_governance_meta_detect_script_rot_py["(生产态 / production) 检测scriptrot / Detect Script Rot<br/>detect_script_rot.py — Script Rot（脚本静默失效）检测器<br/>文件: meta/detect_script_rot.py"]
    scripts_governance_meta_env_check_py["(生产态 / production) 环境检查 / Env Check<br/>env_check.py — 环境就绪检查门禁 (Environment Readiness Gate)<br/>文件: meta/env_check.py"]
    scripts_governance_meta_finding_state_machine_py["(生产态 / production) 发现状态machine / Finding State Machine<br/>finding_state_machine.py — Finding 全生命周期状态机<br/>文件: meta/finding_state_machine.py"]
    scripts_governance_meta_gate_engine_selfcheck_py["(生产态 / production) 门禁引擎selfcheck / Gate Engine Selfcheck<br/>Gate Engine Bootstrap Self-Check — Quis custodiet ipsos custodes?<br/>文件: meta/gate_engine_selfcheck.py"]
    scripts_governance_meta_governance_watchdog_py["(生产态 / production) 治理watchdog / Governance Watchdog<br/>Module docstring — see module-level docstring for details.<br/>文件: meta/governance_watchdog.py"]
    scripts_governance_meta_manage_error_budget_py["(生产态 / production) manage错误预算 / Manage Error Budget<br/>manage_error_budget.py — Error Budget + Burn Rate 管理引擎<br/>文件: meta/manage_error_budget.py"]
    scripts_governance_meta_manage_finding_timeseries_py["(生产态 / production) manage发现timeseries / Manage Finding Timeseries<br/>manage_finding_timeseries.py — Finding 时序数据库 + 趋势分析引擎<br/>文件: meta/manage_finding_timeseries.py"]
    scripts_governance_meta_manage_script_ab_test_py["(生产态 / production) managescriptab测试 / Manage Script Ab Test<br/>manage_script_ab_test.py — 脚本 A/B 对照模式 (Kayenta-style)<br/>文件: meta/manage_script_ab_test.py"]
    scripts_governance_meta_manage_script_retirement_py["(生产态 / production) managescriptretirement / Manage Script Retirement<br/>manage_script_retirement.py — 脚本退役/废弃生命周期管理<br/>文件: meta/manage_script_retirement.py"]
    scripts_governance_meta_manage_shadow_mode_py["(生产态 / production) manageshadow模式 / Manage Shadow Mode<br/>manage_shadow_mode.py — Shadow Mode 渐进激活管理<br/>文件: meta/manage_shadow_mode.py"]
    scripts_governance_meta_mutation_test_post_sync_validator_py["(生产态 / production) mutation测试后同步校验器 / Mutation Test Post Sync Validator<br/>mutation_test_post_sync_validator.py — SSoT 变异测试（独立 oracle）<br/>文件: meta/mutation_test_post_sync_validator.py"]
    scripts_governance_meta_mutation_test_reconciliation_registry_py["(生产态 / production) mutation测试对账注册表 / Mutation Test Reconciliation Registry<br/>mutation_test_reconciliation_registry.py — ReconciliationRegistry SSoT 变异...<br/>文件: meta/mutation_test_reconciliation_registry.py"]
    scripts_governance_meta_phase_e_context_check_py["(生产态 / production) phasee上下文检查 / Phase E Context Check<br/>Phase E: AI context injection verification script<br/>文件: meta/phase_e_context_check.py"]
    scripts_governance_meta_pre_op_check_py["(生产态 / production) 预op检查 / Pre Op Check<br/>AI操作前准入控制器 — 写/删文件前的机械门禁检查.<br/>文件: meta/pre_op_check.py"]
    scripts_governance_meta_score_script_effectiveness_py["(生产态 / production) scorescripteffectiveness / Score Script Effectiveness<br/>score_script_effectiveness.py — 脚本有效性评分（蓝图 §27.12 B90）<br/>文件: meta/score_script_effectiveness.py"]
    scripts_governance_meta_session_startup_check_py["(生产态 / production) 会话启动检查 / Session Startup Check<br/>Session 冷启动自检 — 运行 Phase 0 全部 14 个检查并输出状态报告.<br/>文件: meta/session_startup_check.py"]
    scripts_governance_meta_trace_finding_lifecycle_py["(生产态 / production) 追踪发现生命周期 / Trace Finding Lifecycle<br/>trace_finding_lifecycle.py — Finding C1→C5 全链路追踪引擎<br/>文件: meta/trace_finding_lifecycle.py"]
    scripts_governance_meta_track_script_costs_py["(生产态 / production) trackscriptcosts / Track Script Costs<br/>track_script_costs.py — 脚本执行 AI 费用追踪<br/>文件: meta/track_script_costs.py"]
    scripts_governance_meta_validate_automation_boundary_py["(生产态 / production) validateautomationboundary / Validate Automation Boundary<br/>Module docstring — see module-level docstring for details.<br/>文件: meta/validate_automation_boundary.py"]
    scripts_governance_meta_validate_cross_model_consensus_py["(生产态 / production) validate跨模型共识 / Validate Cross Model Consensus<br/>validate_cross_model_consensus.py — 多AI模型共识验证引擎<br/>文件: meta/validate_cross_model_consensus.py"]
    scripts_governance_meta_validate_dependency_chain_py["(生产态 / production) validate依赖链 / Validate Dependency Chain<br/>validate_dependency_chain.py — 依赖链拓扑顺序验证<br/>文件: meta/validate_dependency_chain.py"]
    scripts_governance_meta_validate_emergency_bypass_log_py["(生产态 / production) validateemergency旁路log / Validate Emergency Bypass Log<br/>validate_emergency_bypass_log.py — 应急绕过审计脚本<br/>文件: meta/validate_emergency_bypass_log.py"]
    scripts_governance_meta_validate_end_to_end_benchmark_py["(生产态 / production) validateend转end基准 / Validate End To End Benchmark<br/>validate_end_to_end_benchmark.py — END-TO-END 基准测试引擎<br/>文件: meta/validate_end_to_end_benchmark.py"]
    scripts_governance_meta_validate_environment_health_py["(生产态 / production) validate环境健康 / Validate Environment Health<br/>validate_environment_health.py — 脚本运行环境健康检查<br/>文件: meta/validate_environment_health.py"]
    scripts_governance_meta_validate_false_negatives_py["(生产态 / production) validatefalsenegatives / Validate False Negatives<br/>validate_false_negatives.py — 假阴性检测引擎 (Fitness Functions)<br/>文件: meta/validate_false_negatives.py"]
    scripts_governance_meta_validate_gate_engine_external_py["(生产态 / production) validate门禁引擎external / Validate Gate Engine External<br/>validate_gate_engine_external.py — Gate Engine 外部完整性验证<br/>文件: meta/validate_gate_engine_external.py"]
    scripts_governance_meta_validate_mutation_testing_py["(生产态 / production) validatemutationtesting / Validate Mutation Testing<br/>validate_mutation_testing.py — 变异测试引擎（蓝图 §19.2 + B75）<br/>文件: meta/validate_mutation_testing.py"]
    scripts_governance_meta_validate_rule_freshness_py["(生产态 / production) validate规则freshness / Validate Rule Freshness<br/>validate_rule_freshness.py — AI Session 注入文件新鲜度检查（蓝图 §22.3 + B62）<br/>文件: meta/validate_rule_freshness.py"]
    scripts_governance_meta_validate_rules_file_backdoor_py["(生产态 / production) validaterules文件backdoor / Validate Rules File Backdoor<br/>validate_rules_file_backdoor.py — Rules File Backdoor 检测器<br/>文件: meta/validate_rules_file_backdoor.py"]
    scripts_governance_meta_validate_rules_integrity_py["(生产态 / production) validaterules完整性 / Validate Rules Integrity<br/>validate_rules_integrity.py — 规则文件完整性保护<br/>文件: meta/validate_rules_integrity.py"]
    scripts_governance_meta_validate_script_onboarding_py["(生产态 / production) validatescriptonboarding / Validate Script Onboarding<br/>Module docstring — see module-level docstring for details.<br/>文件: meta/validate_script_onboarding.py"]
    scripts_governance_meta_validate_script_provenance_py["(生产态 / production) validatescript溯源 / Validate Script Provenance<br/>validate_script_provenance.py — 脚本 Provenance 溯源链<br/>文件: meta/validate_script_provenance.py"]
    scripts_governance_meta_validate_script_system_health_py["(生产态 / production) validatescript系统健康 / Validate Script System Health<br/>validate_script_system_health.py — 脚本系统健康自检（Meta 维度 / 第 13 维度）<br/>文件: meta/validate_script_system_health.py"]
    scripts_governance_meta_validate_threshold_changes_py["(生产态 / production) validatethresholdchanges / Validate Threshold Changes<br/>validate_threshold_changes.py — 阈值变更审计日志<br/>文件: meta/validate_threshold_changes.py"]
    scripts_governance_meta_validate_trust_tier_py["(生产态 / production) validate信任tier / Validate Trust Tier<br/>validate_trust_tier.py — Trust-Tier 门禁执行器<br/>文件: meta/validate_trust_tier.py"]
    scripts_governance_meta_verify_reconciliation_registry_py["(生产态 / production) verify对账注册表 / Verify Reconciliation Registry<br/>verify_reconciliation_registry.py — ReconciliationRegistry 轻量结构 audit（P...<br/>文件: meta/verify_reconciliation_registry.py"]
    scripts_governance_migrate_sqlite_to_pg_migrate_data_py["(生产态 / production) migrate数据 / Migrate Data<br/>SQLite → PostgreSQL 运营数据迁移脚本<br/>文件: migrate_sqlite_to_pg/migrate_data.py"]
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py["(生产态 / production) seedfromyaml / Seed From Yaml<br/>seed_from_yaml.py — 从 YAML 真源灌种子表（5.32.10 治本：种子与迁移拆分）<br/>文件: migrate_sqlite_to_pg/seed_from_yaml.py"]
    scripts_governance_migrate_to_metadata_tables_py["(生产态 / production) migrate转metadatatables / Migrate To Metadata Tables<br/>migrate_to_metadata_tables.py — 裁定#209 Stage 2 一次性迁移脚本<br/>文件: governance/migrate_to_metadata_tables.py"]
    scripts_governance_oneoff_data_domain_audit_query_py["(生产态 / production) 数据domain审计query / Data Domain Audit Query<br/>数据域设计态排查 - DB 现状查询（Phase 2，只读不写）。<br/>文件: oneoff/data_domain_audit_query.py"]
    scripts_governance_oneoff_data_domain_design_state_complete_py["(设计态 / design) 数据domain设计状态complete / Data Domain Design State Complete<br/>数据域四图设计态补全——一次性执行脚本。<br/>文件: oneoff/data_domain_design_state_complete.py"]
    scripts_governance_query_module_panorama_py["(生产态 / production) query模块panorama / Query Module Panorama<br/>query_module_panorama.py — 模块全景查询入口（四图模块对齐 Step 5）<br/>文件: governance/query_module_panorama.py"]
    scripts_governance_register_deferred_modules_py["(生产态 / production) registerdeferredmodules / Register Deferred Modules<br/>将42项暂缓模块写入 depgraph 设计态，含3图对齐设计。<br/>文件: governance/register_deferred_modules.py"]
    scripts_governance_repair_concurrent_commit_test_py["(生产态 / production) concurrentcommit测试 / Concurrent Commit Test<br/>concurrent_commit_test.py — 幽灵提交红蓝对抗脚本（OPS-2026062514）<br/>文件: repair/concurrent_commit_test.py"]
    scripts_governance_run_all_py["(生产态 / production) run全量 / Run All<br/>run_all.py — 脚本系统统一入口脚本<br/>文件: governance/run_all.py"]
    scripts_governance_run_gate_chain_py["(生产态 / production) run门禁链 / Run Gate Chain<br/>run_gate_chain.py — 顺序运行多个门禁脚本，任一失败即整体失败。<br/>文件: governance/run_gate_chain.py"]
    scripts_governance_run_silent_failure_regression_py["(生产态 / production) runsilentfailureregression / Run Silent Failure Regression<br/>run_silent_failure_regression.py — silent-failure 回归套件一键执行入口（P3-2...<br/>文件: governance/run_silent_failure_regression.py"]
    scripts_governance_session_startup_health_check_py["(生产态 / production) 会话启动健康检查 / Session Startup Health Check<br/>session_startup_health_check.py — AI session 启动健康度自检（ARCH-TOOL-HEALT...<br/>文件: governance/session_startup_health_check.py"]
    scripts_governance_status_py["(生产态 / production) status / Status<br/>status.py — 审计系统状态仪表盘<br/>文件: governance/status.py"]
    scripts_governance_verify_sync_integrity_py["(生产态 / production) verify同步完整性 / Verify Sync Integrity<br/>sync 完整性校验脚本：验证 YAML→DB 同步的一致性。<br/>文件: governance/verify_sync_integrity.py"]
    scripts_governance_vms_vms_blindspot_check_py["(生产态 / production) VMSblindspot检查 / VMS Blindspot Check<br/>VMS 盲点闭合检查器 — MOD-INF-011 · R1(33) + R2(22) + R4(6)<br/>文件: vms/vms_blindspot_check.py"]
    scripts_governance_vms_vms_build_completion_check_py["(生产态 / production) VMSbuildcompletion检查 / VMS Build Completion Check<br/>VMS Build Completion Check — MOD-INF-011 · TASK-INF-0217<br/>文件: vms/vms_build_completion_check.py"]
    scripts_governance_vms_vms_cron_monitor_py["(生产态 / production) VMScron监控器 / VMS Cron Monitor<br/>VMS Cron 监控器 — MOD-INF-011 · TASK-INF-0224<br/>文件: vms/vms_cron_monitor.py"]
    scripts_governance_vms_vms_cross_file_check_py["(生产态 / production) VMS跨文件检查 / VMS Cross File Check<br/>VMS 跨文件内容一致性检查器 — MOD-INF-011 · TASK-INF-0211<br/>文件: vms/vms_cross_file_check.py"]
    scripts_governance_vms_vms_health_check_py["(生产态 / production) VMS健康检查 / VMS Health Check<br/>VMS Health Check 脚本 — MOD-INF-011 · Phase 3 运维自动化<br/>文件: vms/vms_health_check.py"]
    scripts_governance_vms_vms_migrate_py["(生产态 / production) VMSmigrate / VMS Migrate<br/>VMS Phase 2 数据迁移脚本 — MOD-INF-011<br/>文件: vms/vms_migrate.py"]
    scripts_governance_vms_vms_migration_dry_run_py["(生产态 / production) VMS迁移dryrun / VMS Migration Dry Run<br/>VMS 迁移 dry-run 脚本 — MOD-INF-011 Phase 2 前置检查<br/>文件: vms/vms_migration_dry_run.py"]
    scripts_governance_vms_vms_phase_rollback_py["(生产态 / production) VMSphaserollback / VMS Phase Rollback<br/>VMS Phase 回滚方案 — MOD-INF-011 · TASK-INF-0217<br/>文件: vms/vms_phase_rollback.py"]
    scripts_governance_vms_vms_version_sync_check_py["(生产态 / production) VMS版本同步检查 / VMS Version Sync Check<br/>VMS 版本同步检查器 — MOD-INF-011 · TASK-INF-0222<br/>文件: vms/vms_version_sync_check.py"]
    tests_governance_scripts_governance_test_any_type_inferrer_py["(生产态 / production) 测试anytypeinferrer / Test Any Type Inferrer<br/>test_any_type_inferrer.py — any_type_inferrer.py 单元测试。<br/>文件: scripts_governance/test_any_type_inferrer.py"]
    tests_governance_scripts_governance_test_check_canonical_yaml_drift_py["(生产态 / production) 测试检查canonicalyaml漂移 / Test Check Canonical Yaml Drift<br/>test_check_canonical_yaml_drift.py — GATE-CANONICAL-YAML-DRIFT 单元测试（Pha...<br/>文件: scripts_governance/test_check_canonical_yaml_drift.py"]
    tests_governance_scripts_governance_test_check_vocab_hardcode_py["(生产态 / production) 测试检查vocabhardcode / Test Check Vocab Hardcode<br/>test_check_vocab_hardcode.py — GATE-VOCAB 检测7 单元测试（2026-06-30 治本补全）<br/>文件: scripts_governance/test_check_vocab_hardcode.py"]
    tests_governance_scripts_governance_test_pre_write_gate_py["(生产态 / production) 测试预write门禁 / Test Pre Write Gate<br/>test_pre_write_gate.py — _check_session_overlap 单元测试（claim 前移协议防线）<br/>文件: scripts_governance/test_pre_write_gate.py"]
    tests_governance_test_check_blueprint_code_alignment_py["(生产态 / production) 测试检查蓝图代码对齐 / Test Check Blueprint Code Alignment<br/>tests for check_blueprint_code_alignment.py — ARCH-FRONTMATTER-STATE-001 Pha...<br/>文件: governance/test_check_blueprint_code_alignment.py"]
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
    scripts_governance_archive_prototype_adversarial_sys_master_test_py ~~~ scripts_governance_archive_prototype_audit_domain_nodes_py
    scripts_governance_archive_prototype_audit_domain_nodes_py ~~~ scripts_governance_archive_prototype_changelog_py
    scripts_governance_archive_prototype_changelog_py ~~~ scripts_governance_archive_prototype_construction_gate_py
    scripts_governance_archive_prototype_construction_gate_py ~~~ scripts_governance_archive_prototype_generate_asset_index_py
    scripts_governance_archive_prototype_generate_asset_index_py ~~~ scripts_governance_archive_prototype_generate_nav_table_py
    scripts_governance_archive_prototype_generate_nav_table_py ~~~ scripts_governance_archive_prototype_rebuild_audit_index_py
    scripts_governance_archive_prototype_rebuild_audit_index_py ~~~ scripts_governance_archive_prototype_scan_ground_truth_deps_py
    scripts_governance_archive_prototype_scan_ground_truth_deps_py ~~~ scripts_governance_archive_prototype_session_simulator_py
    scripts_governance_archive_prototype_session_simulator_py ~~~ scripts_governance_archive_prototype_sync_blueprint_status_py
    scripts_governance_archive_prototype_sync_blueprint_status_py ~~~ scripts_governance_archive_vms_ri_vms_blindspot_check_py
    scripts_governance_archive_vms_ri_vms_blindspot_check_py ~~~ scripts_governance_archive_vms_ri_vms_build_completion_check_py
    scripts_governance_archive_vms_ri_vms_build_completion_check_py ~~~ scripts_governance_archive_vms_ri_vms_cron_monitor_py
    scripts_governance_archive_vms_ri_vms_cron_monitor_py ~~~ scripts_governance_archive_vms_ri_vms_cross_file_check_py
    scripts_governance_archive_vms_ri_vms_cross_file_check_py ~~~ scripts_governance_archive_vms_ri_vms_health_check_py
    scripts_governance_archive_vms_ri_vms_health_check_py ~~~ scripts_governance_archive_vms_ri_vms_migrate_py
    scripts_governance_archive_vms_ri_vms_migrate_py ~~~ scripts_governance_archive_vms_ri_vms_migration_dry_run_py
    scripts_governance_archive_vms_ri_vms_migration_dry_run_py ~~~ scripts_governance_archive_vms_ri_vms_phase_rollback_py
    scripts_governance_archive_vms_ri_vms_phase_rollback_py ~~~ scripts_governance_archive_vms_ri_vms_version_sync_check_py
    scripts_governance_archive_vms_ri_vms_version_sync_check_py ~~~ scripts_governance_shared_base_py
    scripts_governance_shared_base_py ~~~ scripts_governance_shared_module_translation_loader_py
    scripts_governance_shared_module_translation_loader_py ~~~ scripts_governance_sync_cleanup_p0_auto_bridged_py
    scripts_governance_sync_cleanup_p0_auto_bridged_py ~~~ scripts_governance_sync_cleanup_p0_ops_pending_py
    scripts_governance_sync_cleanup_p0_ops_pending_py ~~~ scripts_governance_sync_fix_orphan_deps_py
    scripts_governance_sync_fix_orphan_deps_py ~~~ scripts_governance_tasks_list_phase0_tasks_py
    scripts_governance_tasks_list_phase0_tasks_py ~~~ scripts_governance_tasks_task_show_py
    scripts_governance_tasks_task_show_py ~~~ scripts_governance_tasks_task_summary_py
    scripts_governance_tasks_task_summary_py ~~~ scripts_governance_add_deferred_design_edges_py
    scripts_governance_add_deferred_design_edges_py ~~~ scripts_governance_apply_dataflowgraph_py
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
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py ~~~ scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py ~~~ scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py
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
    scripts_governance_generators_generate_gate_registry_py ~~~ scripts_governance_generators_generate_path_ownership_map_py
    scripts_governance_generators_generate_path_ownership_map_py ~~~ scripts_governance_generators_generate_registry_master_index_py
    scripts_governance_generators_generate_registry_master_index_py ~~~ scripts_governance_generators_inject_manifests_py
    scripts_governance_generators_inject_manifests_py ~~~ scripts_governance_generators_refresh_master_entries_py
    scripts_governance_generators_refresh_master_entries_py ~~~ scripts_governance_generators_sync_audit_protocol_numbers_py
    scripts_governance_generators_sync_audit_protocol_numbers_py ~~~ scripts_governance_git_health_smoke_py
    scripts_governance_git_health_smoke_py ~~~ scripts_governance_meta_arbitrate_findings_py
    scripts_governance_meta_arbitrate_findings_py ~~~ scripts_governance_meta_benchmark_test_fixtures_bad_imports_py
    scripts_governance_meta_benchmark_test_fixtures_bad_imports_py ~~~ scripts_governance_meta_compute_sla_metrics_py
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
    scripts_governance_archive_prototype_check_audit_rbac_isolation_py["(生产态 / production) 检查审计RBACisolation / Check Audit RBAC Isolation<br/>check_audit_rbac_isolation.py — 静态分析 audit-trail 是否直接 import agent-rbac.<br/>文件: prototype/check_audit_rbac_isolation.py"]
    scripts_governance_archive_vms_ri_ri_build_completion_check_py["(生产态 / production) ribuildcompletion检查 / Ri Build Completion Check<br/>Runtime Integration Phase 2 完工验证 — MOD-INF-002<br/>文件: vms_ri/ri_build_completion_check.py"]
    scripts_governance_shared_frontmatter_py["(生产态 / production) frontmatter / Frontmatter<br/>文件头部格式解析 SSoT（Single Source of Truth）<br/>文件: _shared/frontmatter.py"]
    scripts_governance_shared_libcst_docstring_adder_py["(生产态 / production) libcstdocstringadder / Libcst Docstring Adder<br/>libcst_docstring_adder.py — Lossless docstring addition using LibCST.<br/>文件: _shared/libcst_docstring_adder.py"]
    scripts_governance_shared_registry_entry_count_py["(生产态 / production) 注册表entrycount / Registry Entry Count<br/>登记表主条目计数——与 generate_registry_master_index 单一真源对齐。<br/>文件: _shared/registry_entry_count.py"]
    scripts_governance_shared_terminology_loader_py["(生产态 / production) terminology加载器 / Terminology Loader<br/>terminology_loader.py — 架构文档术语词汇表共享加载器（SSoT 真源）<br/>文件: _shared/terminology_loader.py"]
    scripts_governance_shared_yaml_utils_py["(生产态 / production) yamlutils / Yaml Utils<br/>_shared/yaml_utils.py — YAML 文件加载共享工具<br/>文件: _shared/yaml_utils.py"]
    scripts_governance_sync_check_p0_status_py["(生产态 / production) 检查p0status / Check P0 Status<br/>Module docstring — see module-level docstring for details.<br/>文件: _sync/check_p0_status.py"]
    scripts_governance_d3_metadata_validate_module_id_naming_py["(生产态 / production) validate模块id命名 / Validate Module Id Naming<br/>module_id / domain_id / submodule_id 格式校验真源（裁定#208 双轨制 + R2 治本...<br/>文件: d3_metadata/validate_module_id_naming.py"]
    scripts_governance_d5_architecture_generators_common_py["(生产态 / production) common / Common<br/>生成器公共工具（向内收：消除重复）。<br/>文件: generators/_common.py"]
    scripts_governance_d7_code_check_any_abuse_py["(生产态 / production) 检查anyabuse / Check Any Abuse<br/>类型注解 Any 滥用扫描器 — 5.145 维度防御门闸（R70 引入，...<br/>文件: d7_code/check_any_abuse.py"]
    scripts_governance_d8_doc_sync_audit_rename_completeness_py["(生产态 / production) 审计renamecompleteness / Audit Rename Completeness<br/>audit_rename_completeness.py — 改名完整性审计（裁定#207 R1）。<br/>文件: d8_doc_sync/audit_rename_completeness.py"]
    scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py["(生产态 / production) 同步yaml转depgraph / Sync Yaml To Depgraph<br/>(INVARIANTS) YAML→DB单向同步; 27项同步; try/finally恢复触发器<br/>文件: d8_doc_sync/sync_yaml_to_depgraph.py"]
    scripts_governance_meta_concurrency_py["(生产态 / production) concurrency / Concurrency<br/>Module docstring — see module-level docstring for details.<br/>文件: meta/_concurrency.py"]
    scripts_governance_meta_backup_runtime_state_py["(生产态 / production) backup运行时状态 / Backup Runtime State<br/>backup_runtime_state.py — 运行时状态备份（蓝图 §33 灾备）<br/>文件: meta/backup_runtime_state.py"]
    scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py["(生产态 / production) orphan文件without模块registration / Orphan File Without Module Registration<br/>Module docstring — see module-level docstring for details.<br/>文件: test_fixtures/orphan_file_without_module_registration.py"]
    scripts_governance_meta_manage_baseline_py["(生产态 / production) manage基线 / Manage Baseline<br/>manage_baseline.py — Finding 基线快照管理<br/>文件: meta/manage_baseline.py"]
    scripts_governance_sync_panorama_module_py["(生产态 / production) 同步panorama模块 / Sync Panorama Module<br/>sync_panorama_module.py — 四图模块同步引擎（ARCH-056）<br/>文件: governance/sync_panorama_module.py"]
    scripts_governance_archive_prototype_check_audit_rbac_isolation_py ~~~ scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_ri_build_completion_check_py ~~~ scripts_governance_shared_frontmatter_py
    scripts_governance_shared_frontmatter_py ~~~ scripts_governance_shared_libcst_docstring_adder_py
    scripts_governance_shared_libcst_docstring_adder_py ~~~ scripts_governance_shared_registry_entry_count_py
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
    scripts_governance_meta_backup_runtime_state_py ~~~ scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py
    scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py ~~~ scripts_governance_meta_manage_baseline_py
    scripts_governance_meta_manage_baseline_py ~~~ scripts_governance_sync_panorama_module_py
    scripts_governance_archive_vms_ri_ri_boundary_check_py["(生产态 / production) riboundary检查 / Ri Boundary Check<br/>Runtime Integration 边界验证脚本 — MOD-INF-002<br/>文件: vms_ri/ri_boundary_check.py"]
    scripts_governance_shared_encoding_py["(生产态 / production) encoding / Encoding<br/>encoding.py — UTF-8 编码安全工具<br/>文件: _shared/encoding.py"]
    scripts_governance_shared_file_utils_py["(生产态 / production) 文件utils / File Utils<br/>_shared/file_utils.py — 原子写入共享工具（ARCH-036 P1-1）<br/>文件: _shared/file_utils.py"]
    scripts_governance_shared_thresholds_py["(生产态 / production) thresholds / Thresholds<br/>thresholds.py — 阈值集中配置加载器<br/>文件: _shared/thresholds.py"]
    scripts_governance_shared_walk_py["(生产态 / production) walk / Walk<br/>walk.py — 目录遍历共享工具<br/>文件: _shared/walk.py"]
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py["(生产态 / production) 蓝图frontmatterreconciler / Blueprint Frontmatter Reconciler<br/>blueprint_frontmatter_reconciler.py — 蓝图 frontmatter 核心字段对齐（ARCH-05...<br/>文件: syncers/blueprint_frontmatter_reconciler.py"]
    scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py["(生产态 / production) incomplete模块 / Incomplete Module<br/>Module docstring — see module-level docstring for details.<br/>文件: test_fixtures/incomplete_module.py"]
    scripts_governance_archive_vms_ri_ri_boundary_check_py ~~~ scripts_governance_shared_encoding_py
    scripts_governance_shared_encoding_py ~~~ scripts_governance_shared_file_utils_py
    scripts_governance_shared_file_utils_py ~~~ scripts_governance_shared_thresholds_py
    scripts_governance_shared_thresholds_py ~~~ scripts_governance_shared_walk_py
    scripts_governance_shared_walk_py ~~~ scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py ~~~ scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py
    scripts_governance_shared_constants_py["(生产态 / production) constants / Constants<br/>constants.py — 审计脚本共享常量<br/>文件: _shared/constants.py"]
    scripts_governance_d5_architecture_panorama_common_py["(生产态 / production) panoramacommon / Panorama Common<br/>panorama_common.py — 四图投票共享工具（ARCH-056 引擎加固）<br/>文件: d5_architecture/panorama_common.py"]
    scripts_governance_shared_constants_py ~~~ scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_apply_dataflowgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_ast_import_rewriter_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_apply_decisiongraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_sync_panorama_module_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_d3_metadata_validate_module_id_naming_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_d8_doc_sync_audit_rename_completeness_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_meta_backup_runtime_state_py
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_check_commit_message_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_check_ssot_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_decision_graph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_decision_graph_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_extract_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_extract_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generate_project_path_tree_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_extract_decisiongraph_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generate_project_depgraph_py -->|导入依赖 / import_depends| scripts_governance_sync_panorama_module_py
    scripts_governance_generate_project_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generate_project_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_query_module_panorama_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_migrate_to_metadata_tables_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_run_gate_chain_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_meta_concurrency_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_run_all_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_sync_panorama_module_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_sync_panorama_module_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py
    scripts_governance_sync_panorama_module_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_audit_registration_py -->|导入依赖 / import_depends| scripts_governance_meta_manage_baseline_py
    scripts_governance_d11_compliance_audit_registration_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_audit_registration_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d10_performance_collect_system_threads_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_verify_sync_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_task_self_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_status_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_status_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d11_compliance_fix_shared_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_fix_shared_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_ci_self_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_g9_compliance_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_commit_gateway_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_exit_codes_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_exit_codes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_no_utf8_bom_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_no_utf8_bom_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_libcst_docstring_adder_py
    scripts_governance_d11_compliance_validate_script_quality_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d11_compliance_validate_manifest_admission_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_script_naming_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_script_naming_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_frozen_requirements_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_frozen_requirements_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_commit_message_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_commit_message_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_verify_audit_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d11_compliance_validate_task_decomposition_bypass_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d11_compliance_verify_schema_health_py -->|导入依赖 / import_depends| scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py
    scripts_governance_d11_compliance_verify_schema_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_check_logger_kwargs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_validate_session_gate_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_validate_session_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_validate_session_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_audit_config_format_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_config_format_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_config_format_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d1_structure_audit_directory_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_directory_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_audit_directory_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_archive_drafts_zone_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_archive_drafts_zone_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_findings_by_scope_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_findings_by_scope_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_directory_scalability_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_audit_directory_scalability_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_audit_directory_scalability_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d1_structure_batch_create_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_cbg_reset_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_cbg_reset_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_cleanup_stash_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_orphan_py_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_detect_orphan_py_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_directory_contract_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_check_directory_contract_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_directory_contract_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_check_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_check_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_check_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_detect_residual_files_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_detect_residual_files_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_residual_files_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_check_handoff_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_temp_files_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_detect_temp_files_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_detect_temp_files_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_drafts_zone_archiver_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_drafts_zone_archiver_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_drafts_zone_archiver_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_reset_cbg_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_reset_cbg_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_run_script_smoke_test_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_run_script_smoke_test_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_sync_index_from_manifest_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_sync_index_from_manifest_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_sync_index_from_manifest_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_validate_config_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d1_structure_sync_policies_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_sync_policies_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_sync_policies_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_generate_missing_index_md_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d1_structure_validate_index_reality_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_d1_output_sanity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_d1_output_sanity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d2_links_audit_broken_links_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d2_links_detect_relative_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d2_links_detect_relative_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d2_links_detect_relative_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d1_structure_validate_immutable_core_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_auto_generate_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_auto_generate_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_auto_generate_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d1_structure_validate_read_before_write_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d1_structure_validate_read_before_write_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_backfill_ttl_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_check_module_singlesource_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_backfill_doctype_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_frontmatter_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_check_blueprint_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_naming_convention_py -->|导入依赖 / import_depends| scripts_governance_d3_metadata_validate_module_id_naming_py
    scripts_governance_d3_metadata_check_naming_convention_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_schema_version_writes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_registry_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_classify_ttl_by_content_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_classify_ttl_by_content_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_migrate_illegal_doctype_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_check_vocab_hardcode_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_deep_content_scanner_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d3_metadata_generate_rule_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d3_metadata_generate_derived_files_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_generate_derived_files_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_generate_derived_files_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d3_metadata_validate_blueprint_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_blueprint_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_module_id_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_module_id_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_validate_module_id_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_architecture_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_architecture_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d3_metadata_validate_architecture_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_tool_contracts_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_excessive_file_moves_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_excessive_file_moves_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_deprecated_path_writes_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_deprecated_path_writes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d3_metadata_validate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d3_metadata_validate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_registry_entry_count_py
    scripts_governance_d4_paths_detect_ruins_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_ruins_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d4_paths_detect_ruins_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d4_paths_detect_split_delete_ref_commit_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_dependency_graph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyze_change_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyze_change_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_audit_agent_spec_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_check_drift_e2e_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_diagnose_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_diagnose_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_detect_causal_conflicts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detect_causal_conflicts_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_check_budget_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detect_constraint_violations_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_pre_delete_safety_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_pre_write_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_checkers_check_architecture_gates_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_code_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_code_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_contract_physical_path_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_orphan_outputs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_checkers_check_dependency_direction_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_contract_code_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_checkers_check_vms_ssot_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_asset_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_align_panoramas_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_d5_architecture_generators_align_panoramas_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_align_panoramas_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_contract_catalog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_generators_generate_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_decision_diagram_py -->|导入依赖 / import_depends| scripts_governance_shared_terminology_loader_py
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_generators_generate_panorama_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_policies_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_generators_common_py
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py -->|导入依赖 / import_depends| scripts_governance_d5_architecture_panorama_common_py
    scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_archive_rationale_log_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_merge_readme_to_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_arch_review_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_b_track_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_autonomy_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_blind_spot_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_directory_structure_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_validators_validate_depends_on_format_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_cross_references_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_gate_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_field_ownership_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_handoff_package_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_interface_contracts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_load_path_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_three_way_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_validate_module_schema_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_validate_target_layer_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_target_layer_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d6_security_check_protected_paths_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_check_protected_paths_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_permanent_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_permanent_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_secrets_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_keywords_in_logs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_keywords_in_logs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_keywords_in_logs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_anchor_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_anchor_file_deletion_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_git_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_git_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_git_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_shell_true_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_shell_true_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_shell_true_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_shell_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_shell_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_shell_dangerous_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_retire_tmp_artifacts_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_retire_tmp_artifacts_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_scan_runtime_log_secrets_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_scan_runtime_log_secrets_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_vague_terms_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_vague_terms_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_vague_terms_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_detect_threading_lock_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_detect_threading_lock_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_detect_threading_lock_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_run_adversarial_checks_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d6_security_scan_secret_leak_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d6_security_validate_gate_discipline_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d6_security_validate_gate_discipline_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d6_security_validate_gate_discipline_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_any_type_inferrer_py -->|导入依赖 / import_depends| scripts_governance_d7_code_check_any_abuse_py
    scripts_governance_d7_code_any_type_inferrer_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_ai_capability_boundary_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_ai_capability_boundary_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_encoding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_merge_conflict_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_no_tests_unit_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_absolute_path_hardcoding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_check_idempotency_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_check_idempotency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
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
    scripts_governance_d7_code_fix_n12_ke_naming_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_forward_reference_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_private_key_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_silent_degradation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_detect_silent_degradation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_detect_silent_degradation_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_fix_n06_scope_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n15_blueprint_path_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n13_snake_case_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_n14_init_all_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_rewrite_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_rewrite_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d7_code_fix_naming_manual_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_scan_complexity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_scan_consumers_accuracy_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d7_code_fix_orphan_exports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_fix_orphan_exports_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d7_code_validate_docstring_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_docstring_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_scan_debt_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_contracts_purity_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_contracts_purity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_contracts_purity_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_fle_action_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_fle_action_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_fle_action_metadata_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_fle_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_fle_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_fle_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_test_assertion_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_test_assertion_depth_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_import_style_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_import_style_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_python_syntax_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_python_syntax_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_init_all_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_init_all_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_kb_write_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_kb_write_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_kb_write_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_test_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_test_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d7_code_validate_unused_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_unused_imports_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d7_code_validate_type_annotation_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d7_code_validate_type_annotation_coverage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_audit_rename_completeness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_detect_dated_snapshots_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_auto_sync_all_registries_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_d8_doc_sync_sync_rule_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_sync_rule_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_update_progress_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_validate_document_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d8_doc_sync_validate_document_ttl_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d9_knowledge_detect_duplicated_normative_language_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_d9_knowledge_detect_orphan_documents_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_data_quality_check_tick_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_data_quality_check_tick_duplication_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_check_gate_inventory_drift_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_gate_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generators_fix_module_manifest_layout_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_fix_module_manifest_layout_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_fix_module_manifest_layout_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_path_ownership_map_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_path_ownership_map_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_registry_entry_count_py
    scripts_governance_generators_generate_registry_master_index_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generators_sync_audit_protocol_numbers_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_sync_audit_protocol_numbers_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_arbitrate_findings_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_inject_manifests_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_generators_refresh_master_entries_py -->|导入依赖 / import_depends| scripts_governance_shared_registry_entry_count_py
    scripts_governance_meta_backup_runtime_state_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_backup_runtime_state_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_compute_sla_metrics_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_compute_sla_metrics_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_compute_sla_metrics_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_detect_fix_oscillation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_detect_fix_oscillation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_create_task_from_finding_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_create_task_from_finding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_create_task_from_finding_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_detect_config_deviation_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_detect_config_deviation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_script_divergence_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_detect_script_divergence_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_script_rot_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_env_check_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_env_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_hallucinated_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_detect_hallucinated_packages_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_finding_state_machine_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_finding_state_machine_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_finding_state_machine_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_manage_error_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_error_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_error_budget_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_manage_baseline_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_baseline_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_script_ab_test_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_script_ab_test_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_manage_finding_timeseries_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_governance_watchdog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_governance_watchdog_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_governance_watchdog_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_meta_gate_engine_selfcheck_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_gate_engine_selfcheck_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_meta_mutation_test_post_sync_validator_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_script_retirement_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_script_retirement_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_mutation_test_reconciliation_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_shadow_mode_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_manage_shadow_mode_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_pre_op_check_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_pre_op_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_track_script_costs_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_track_script_costs_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_session_startup_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_score_script_effectiveness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_score_script_effectiveness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_cross_model_consensus_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_environment_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_trace_finding_lifecycle_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_emergency_bypass_log_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_emergency_bypass_log_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_automation_boundary_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_dependency_chain_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_dependency_chain_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_mutation_testing_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_mutation_testing_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_end_to_end_benchmark_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_end_to_end_benchmark_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_gate_engine_external_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_meta_validate_rules_file_backdoor_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_false_negatives_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_false_negatives_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_script_onboarding_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_script_system_health_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_rule_freshness_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_meta_validate_rule_freshness_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_trust_tier_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_script_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_script_provenance_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_rules_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_validate_rules_integrity_py -->|导入依赖 / import_depends| scripts_governance_shared_file_utils_py
    scripts_governance_meta_validate_threshold_changes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_verify_reconciliation_registry_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_concurrency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_concurrency_py -->|导入依赖 / import_depends| scripts_governance_shared_thresholds_py
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py -->|导入依赖 / import_depends| scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py
    scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py -->|config_depends / config_depends| scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py
    scripts_governance_migrate_sqlite_to_pg_migrate_data_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_meta_benchmark_test_fixtures_bad_imports_py -->|config_depends / config_depends| scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py
    scripts_governance_vms_vms_version_sync_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_dm105_depgraph_triage_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_check_exam_case_consistency_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_audit_post_sync_commands_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_list_phase0_tasks_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_fix_broken_post_sync_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_rename_kebab_to_snake_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_phase_a_backup_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_test_lock_scenarios_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_rename_whitelist_cleanup_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_one_off_verify_final_delivery_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_adversarial_log_py -->|config_depends / config_depends| scripts_governance_archive_prototype_check_audit_rbac_isolation_py
    scripts_governance_archive_one_off_verify_rule_yaml_migration_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_check_audit_rbac_isolation_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_adversarial_sys_master_test_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_audit_domain_nodes_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_changelog_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_construction_gate_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_generate_nav_table_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_archive_prototype_generate_nav_table_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_generate_nav_table_py -->|导入依赖 / import_depends| scripts_governance_shared_yaml_utils_py
    scripts_governance_archive_prototype_sync_blueprint_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_generate_asset_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_rebuild_audit_index_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_prototype_scan_ground_truth_deps_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_vms_ri_ri_build_completion_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_boundary_check_py
    scripts_governance_archive_vms_ri_vms_build_completion_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_vms_blindspot_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_prototype_session_simulator_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_archive_prototype_session_simulator_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_vms_ri_vms_cross_file_check_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_archive_vms_ri_vms_version_sync_check_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_archive_vms_ri_vms_phase_rollback_py -->|config_depends / config_depends| scripts_governance_archive_vms_ri_ri_build_completion_check_py
    scripts_governance_shared_base_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_shared_base_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_base_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_shared_file_utils_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_libcst_docstring_adder_py -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    scripts_governance_shared_libcst_docstring_adder_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_libcst_docstring_adder_py -->|导入依赖 / import_depends| scripts_governance_shared_walk_py
    scripts_governance_shared_walk_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_yaml_utils_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_terminology_loader_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_sync_check_p0_status_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_sync_cleanup_p0_ops_pending_py -->|config_depends / config_depends| scripts_governance_sync_check_p0_status_py
    scripts_governance_sync_cleanup_p0_auto_bridged_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_tasks_list_phase0_tasks_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_sync_fix_orphan_deps_py -->|config_depends / config_depends| scripts_governance_sync_check_p0_status_py
    scripts_governance_tasks_task_summary_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_tasks_task_show_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_archive_governance_dm106_p2b_verification_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    scripts_governance_shared_module_translation_loader_py -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    tests_governance_scripts_governance_test_check_vocab_hardcode_py -->|测试依赖 / test_depends| scripts_governance_shared_constants_py
    tests_governance_scripts_governance_test_check_vocab_hardcode_py -->|测试依赖 / test_depends| scripts_governance_shared_yaml_utils_py
    D_GOV_AUDIT["(生产态 / production) 审计追踪 / Audit Trail<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>跨域节点 / cross-domain"]
    scripts_governance_session_startup_health_check_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    scripts_governance_d3_metadata_check_module_singlesource_py -->|导入依赖 / import_depends| D_SHARED
    D_DATA["(生产态 / production) 数据接入层 / Data Access Layer<br/>数据接入层，负责数据源接入、数据集成和数据标准化<br/>跨域节点 / cross-domain"]
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| D_DATA
    scripts_governance_d5_architecture_generators_generate_data_inventory_py -->|导入依赖 / import_depends| D_DATA
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle Management<br/>生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    scripts_governance_archive_one_off_create_alignment_tasks_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_add_deferred_design_edges_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_apply_dataflowgraph_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_apply_decisiongraph_py -->|导入依赖 / import_depends| D_GOVERNANCE
    scripts_governance_apply_decisiongraph_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_architecture_health_dashboard_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_apply_depgraph_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_check_ssot_gate_py -->|导入依赖 / import_depends| D_SHARED
    scripts_governance_check_ssot_gate_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["(生产态 / production) 规则执行 / Rule Enforcement<br/>规则执行，负责治理规则执行和门禁拦截<br/>跨域节点 / cross-domain"]
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| scripts_governance_architecture_health_dashboard_py
    D_GOVERNANCE -->|导入依赖 / import_depends| scripts_governance_d3_metadata_check_naming_convention_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| scripts_governance_d3_metadata_validate_module_id_naming_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| scripts_governance_generators_check_gate_inventory_drift_py
    D_GOVERNANCE -->|测试依赖 / test_depends| scripts_governance_generators_generate_gate_registry_py
    D_GOV_RULE["(生产态 / production) 规则治理 / Rule Governance<br/>规则治理，负责规则注册、规则版本和规则依赖管理<br/>跨域节点 / cross-domain"]
    D_GOV_RULE -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    D_GOVERNANCE -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    D_GOV_DRIFT["(生产态 / production) 漂移检测 / Drift Detection<br/>漂移检测，负责架构漂移检测和漂移告警<br/>跨域节点 / cross-domain"]
    D_GOV_DRIFT -->|导入依赖 / import_depends| scripts_governance_shared_encoding_py
    D_GOV_DRIFT -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    D_GOV_DRIFT -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    D_GOV_DRIFT -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    D_GOVERNANCE -->|导入依赖 / import_depends| scripts_governance_shared_frontmatter_py
    D_GOV_DOCS["(生产态 / production) 架构文档治理 / Architecture Docs Governance<br/>架构文档治理，负责架构文档生成、一致性和版本管理<br/>跨域节点 / cross-domain"]
    D_GOV_DOCS -->|测试依赖 / test_depends| scripts_governance_shared_constants_py
    D_GOVERNANCE -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    D_GOVERNANCE -->|导入依赖 / import_depends| scripts_governance_shared_constants_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_scripts_registry_yaml,scripts_archive_governance_dm106_p2b_verification_py,scripts_governance_archive_one_off_audit_post_sync_commands_py,scripts_governance_archive_one_off_check_exam_case_consistency_py,scripts_governance_archive_one_off_create_alignment_tasks_py,scripts_governance_archive_one_off_dm105_depgraph_triage_py,scripts_governance_archive_one_off_fix_broken_post_sync_py,scripts_governance_archive_one_off_list_phase0_tasks_py,scripts_governance_archive_one_off_phase_a_backup_py,scripts_governance_archive_one_off_rename_kebab_to_snake_py,scripts_governance_archive_one_off_rename_whitelist_cleanup_py,scripts_governance_archive_one_off_test_lock_scenarios_py,scripts_governance_archive_one_off_verify_final_delivery_py,scripts_governance_archive_one_off_verify_rule_yaml_migration_py,scripts_governance_archive_prototype_adversarial_log_py,scripts_governance_archive_prototype_adversarial_sys_master_test_py,scripts_governance_archive_prototype_audit_domain_nodes_py,scripts_governance_archive_prototype_changelog_py,scripts_governance_archive_prototype_check_audit_rbac_isolation_py,scripts_governance_archive_prototype_construction_gate_py,scripts_governance_archive_prototype_generate_asset_index_py,scripts_governance_archive_prototype_generate_nav_table_py,scripts_governance_archive_prototype_rebuild_audit_index_py,scripts_governance_archive_prototype_scan_ground_truth_deps_py,scripts_governance_archive_prototype_session_simulator_py,scripts_governance_archive_prototype_sync_blueprint_status_py,scripts_governance_archive_vms_ri_ri_boundary_check_py,scripts_governance_archive_vms_ri_ri_build_completion_check_py,scripts_governance_archive_vms_ri_vms_blindspot_check_py,scripts_governance_archive_vms_ri_vms_build_completion_check_py,scripts_governance_archive_vms_ri_vms_cron_monitor_py,scripts_governance_archive_vms_ri_vms_cross_file_check_py,scripts_governance_archive_vms_ri_vms_health_check_py,scripts_governance_archive_vms_ri_vms_migrate_py,scripts_governance_archive_vms_ri_vms_migration_dry_run_py,scripts_governance_archive_vms_ri_vms_phase_rollback_py,scripts_governance_archive_vms_ri_vms_version_sync_check_py,scripts_governance_shared_base_py,scripts_governance_shared_constants_py,scripts_governance_shared_encoding_py,scripts_governance_shared_file_utils_py,scripts_governance_shared_frontmatter_py,scripts_governance_shared_libcst_docstring_adder_py,scripts_governance_shared_module_translation_loader_py,scripts_governance_shared_registry_entry_count_py,scripts_governance_shared_terminology_loader_py,scripts_governance_shared_thresholds_py,scripts_governance_shared_walk_py,scripts_governance_shared_yaml_utils_py,scripts_governance_sync_check_p0_status_py,scripts_governance_sync_cleanup_p0_auto_bridged_py,scripts_governance_sync_cleanup_p0_ops_pending_py,scripts_governance_sync_fix_orphan_deps_py,scripts_governance_tasks_list_phase0_tasks_py,scripts_governance_tasks_task_show_py,scripts_governance_tasks_task_summary_py,scripts_governance_add_deferred_design_edges_py,scripts_governance_apply_dataflowgraph_py,scripts_governance_apply_decisiongraph_py,scripts_governance_apply_depgraph_py,scripts_governance_architecture_health_dashboard_py,scripts_governance_ast_import_rewriter_py,scripts_governance_audit_return_contract_usage_py,scripts_governance_audit_worktree_ops_telemetry_py,scripts_governance_check_commit_message_py,scripts_governance_check_ssot_gate_py,scripts_governance_d10_performance_collect_system_threads_py,scripts_governance_d11_compliance_audit_registration_py,scripts_governance_d11_compliance_ci_self_check_py,scripts_governance_d11_compliance_fix_shared_bypass_py,scripts_governance_d11_compliance_g9_compliance_check_py,scripts_governance_d11_compliance_task_self_check_py,scripts_governance_d11_compliance_validate_commit_gateway_py,scripts_governance_d11_compliance_validate_commit_message_py,scripts_governance_d11_compliance_validate_exit_codes_py,scripts_governance_d11_compliance_validate_frozen_requirements_py,scripts_governance_d11_compliance_validate_manifest_admission_py,scripts_governance_d11_compliance_validate_no_utf8_bom_py,scripts_governance_d11_compliance_validate_script_naming_py,scripts_governance_d11_compliance_validate_script_quality_py,scripts_governance_d11_compliance_validate_task_decomposition_bypass_py,scripts_governance_d11_compliance_validate_vocabulary_coverage_py,scripts_governance_d11_compliance_verify_audit_integrity_py,scripts_governance_d11_compliance_verify_schema_health_py,scripts_governance_d12_ai_hallucination_check_logger_kwargs_py,scripts_governance_d12_ai_hallucination_validate_gate_prompt_conflict_py,scripts_governance_d12_ai_hallucination_validate_session_budget_py,scripts_governance_d12_ai_hallucination_validate_session_gate_check_py,scripts_governance_d1_structure_archive_drafts_zone_py,scripts_governance_d1_structure_audit_config_format_py,scripts_governance_d1_structure_audit_directory_integrity_py,scripts_governance_d1_structure_audit_directory_scalability_py,scripts_governance_d1_structure_audit_findings_by_scope_py,scripts_governance_d1_structure_batch_create_index_md_py,scripts_governance_d1_structure_cbg_reset_py,scripts_governance_d1_structure_check_directory_contract_py,scripts_governance_d1_structure_check_handoff_manifests_py,scripts_governance_d1_structure_check_index_integrity_py,scripts_governance_d1_structure_cleanup_stash_py,scripts_governance_d1_structure_detect_orphan_py_py,scripts_governance_d1_structure_detect_residual_files_py,scripts_governance_d1_structure_detect_temp_files_py,scripts_governance_d1_structure_drafts_zone_archiver_py,scripts_governance_d1_structure_generate_missing_index_md_py,scripts_governance_d1_structure_reset_cbg_py,scripts_governance_d1_structure_run_script_smoke_test_py,scripts_governance_d1_structure_sync_index_from_manifest_py,scripts_governance_d1_structure_sync_policies_index_py,scripts_governance_d1_structure_validate_config_integrity_py,scripts_governance_d1_structure_validate_d1_output_sanity_py,scripts_governance_d1_structure_validate_immutable_core_py,scripts_governance_d1_structure_validate_index_reality_py,scripts_governance_d1_structure_validate_read_before_write_py,scripts_governance_d2_links_audit_broken_links_py,scripts_governance_d2_links_detect_relative_references_py,scripts_governance_d3_metadata_auto_generate_index_py,scripts_governance_d3_metadata_backfill_doctype_metadata_py,scripts_governance_d3_metadata_backfill_ttl_metadata_py,scripts_governance_d3_metadata_check_blueprint_compliance_py,scripts_governance_d3_metadata_check_frontmatter_metadata_py,scripts_governance_d3_metadata_check_module_singlesource_py,scripts_governance_d3_metadata_check_naming_convention_py,scripts_governance_d3_metadata_check_registry_consistency_py,scripts_governance_d3_metadata_check_schema_version_writes_py,scripts_governance_d3_metadata_check_vocab_hardcode_py,scripts_governance_d3_metadata_classify_ttl_by_content_py,scripts_governance_d3_metadata_deep_content_scanner_py,scripts_governance_d3_metadata_generate_derived_files_py,scripts_governance_d3_metadata_generate_rule_catalog_py,scripts_governance_d3_metadata_migrate_illegal_doctype_py,scripts_governance_d3_metadata_validate_architecture_py,scripts_governance_d3_metadata_validate_blueprint_provenance_py,scripts_governance_d3_metadata_validate_module_id_py,scripts_governance_d3_metadata_validate_module_id_naming_py,scripts_governance_d3_metadata_validate_registry_master_index_py,scripts_governance_d3_metadata_validate_tool_contracts_consistency_py,scripts_governance_d4_paths_detect_deprecated_path_writes_py,scripts_governance_d4_paths_detect_excessive_file_moves_py,scripts_governance_d4_paths_detect_ruins_references_py,scripts_governance_d4_paths_detect_split_delete_ref_commit_py,scripts_governance_d5_architecture_analyze_change_impact_py,scripts_governance_d5_architecture_analyzers_analyze_contract_impact_py,scripts_governance_d5_architecture_analyzers_audit_depends_on_chain_depth_py,scripts_governance_d5_architecture_analyzers_measure_deprecation_cascade_py,scripts_governance_d5_architecture_audit_agent_spec_py,scripts_governance_d5_architecture_check_budget_health_py,scripts_governance_d5_architecture_check_drift_e2e_py,scripts_governance_d5_architecture_checkers_check_architecture_gates_py,scripts_governance_d5_architecture_checkers_check_blueprint_automation_sync_py,scripts_governance_d5_architecture_checkers_check_blueprint_code_alignment_py,scripts_governance_d5_architecture_checkers_check_blueprint_template_compliance_py,scripts_governance_d5_architecture_checkers_check_canonical_yaml_drift_py,scripts_governance_d5_architecture_checkers_check_code_duplication_py,scripts_governance_d5_architecture_checkers_check_contract_code_drift_py,scripts_governance_d5_architecture_checkers_check_contract_physical_path_py,scripts_governance_d5_architecture_checkers_check_dependency_direction_py,scripts_governance_d5_architecture_checkers_check_g6_ctr_compliance_py,scripts_governance_d5_architecture_checkers_check_orphan_outputs_py,scripts_governance_d5_architecture_checkers_check_precommit_id_uniqueness_py,scripts_governance_d5_architecture_checkers_check_rule_four_way_alignment_py,scripts_governance_d5_architecture_checkers_check_ssot_uniqueness_py,scripts_governance_d5_architecture_checkers_check_trace_context_propagation_py,scripts_governance_d5_architecture_checkers_check_vms_ssot_py,scripts_governance_d5_architecture_dependency_graph_py,scripts_governance_d5_architecture_detect_causal_conflicts_py,scripts_governance_d5_architecture_detect_constraint_violations_py,scripts_governance_d5_architecture_detectors_analyze_same_name_module_relations_py,scripts_governance_d5_architecture_detectors_detect_depends_on_cycles_py,scripts_governance_d5_architecture_detectors_detect_deprecated_adr_references_py,scripts_governance_d5_architecture_detectors_detect_duplicate_module_names_py,scripts_governance_d5_architecture_diagnose_depgraph_py,scripts_governance_d5_architecture_generators_common_py,scripts_governance_d5_architecture_generators_align_panoramas_py,scripts_governance_d5_architecture_generators_generate_asset_catalog_py,scripts_governance_d5_architecture_generators_generate_blueprint_panorama_py,scripts_governance_d5_architecture_generators_generate_code_wiki_stats_py,scripts_governance_d5_architecture_generators_generate_contract_catalog_py,scripts_governance_d5_architecture_generators_generate_contracts_py,scripts_governance_d5_architecture_generators_generate_data_acquisition_flow_py,scripts_governance_d5_architecture_generators_generate_data_inventory_py,scripts_governance_d5_architecture_generators_generate_dataflow_diagram_py,scripts_governance_d5_architecture_generators_generate_decision_diagram_py,scripts_governance_d5_architecture_generators_generate_panorama_registry_py,scripts_governance_d5_architecture_generators_generate_policies_py,scripts_governance_d5_architecture_generators_generate_trading_flow_diagram_py,scripts_governance_d5_architecture_panorama_common_py,scripts_governance_d5_architecture_pre_delete_safety_check_py,scripts_governance_d5_architecture_pre_write_gate_py,scripts_governance_d5_architecture_syncers_archive_rationale_log_py,scripts_governance_d5_architecture_syncers_blueprint_frontmatter_reconciler_py,scripts_governance_d5_architecture_syncers_merge_readme_to_index_py,scripts_governance_d5_architecture_syncers_sync_blueprint_code_index_py,scripts_governance_d5_architecture_syncers_sync_registry_from_blueprints_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_code_sync_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_implementation_docs_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_path_consistency_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_placement_py,scripts_governance_d5_architecture_validators_blueprint_validate_blueprint_tag_uniqueness_py,scripts_governance_d5_architecture_validators_lifecycle_validate_lifecycle_refs_py,scripts_governance_d5_architecture_validators_lifecycle_validate_module_lifecycle_py,scripts_governance_d5_architecture_validators_session_validate_session_log_index_integrity_py,scripts_governance_d5_architecture_validators_session_validate_session_log_updated_py,scripts_governance_d5_architecture_validators_validate_adr_frontmatter_consistency_py,scripts_governance_d5_architecture_validators_validate_arch_review_gate_py,scripts_governance_d5_architecture_validators_validate_architecture_contract_internal_py,scripts_governance_d5_architecture_validators_validate_autonomy_gate_py,scripts_governance_d5_architecture_validators_validate_b_track_packages_py,scripts_governance_d5_architecture_validators_validate_blind_spot_status_py,scripts_governance_d5_architecture_validators_validate_code_yaml_alignment_py,scripts_governance_d5_architecture_validators_validate_cross_references_py,scripts_governance_d5_architecture_validators_validate_dependency_graph_template_py,scripts_governance_d5_architecture_validators_validate_depends_on_format_py,scripts_governance_d5_architecture_validators_validate_deprecated_dependents_py,scripts_governance_d5_architecture_validators_validate_directory_structure_py,scripts_governance_d5_architecture_validators_validate_field_ownership_py,scripts_governance_d5_architecture_validators_validate_gate_yaml_py,scripts_governance_d5_architecture_validators_validate_handoff_package_py,scripts_governance_d5_architecture_validators_validate_interface_contracts_py,scripts_governance_d5_architecture_validators_validate_load_path_integrity_py,scripts_governance_d5_architecture_validators_validate_module_schema_py,scripts_governance_d5_architecture_validators_validate_nested_flat_dirs_py,scripts_governance_d5_architecture_validators_validate_p0_module_contracts_py,scripts_governance_d5_architecture_validators_validate_static_manifest_drift_py,scripts_governance_d5_architecture_validators_validate_target_layer_py,scripts_governance_d5_architecture_validators_validate_three_way_consistency_py,scripts_governance_d5_architecture_validators_yaml_md_validate_md_yaml_number_drift_py,scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_interface_uniqueness_py,scripts_governance_d5_architecture_validators_yaml_md_validate_yaml_summaries_py,scripts_governance_d6_security_check_protected_paths_py,scripts_governance_d6_security_detect_anchor_file_deletion_py,scripts_governance_d6_security_detect_git_dangerous_py,scripts_governance_d6_security_detect_keywords_in_logs_py,scripts_governance_d6_security_detect_permanent_file_deletion_py,scripts_governance_d6_security_detect_secrets_py,scripts_governance_d6_security_detect_shell_dangerous_py,scripts_governance_d6_security_detect_shell_true_py,scripts_governance_d6_security_detect_threading_lock_py,scripts_governance_d6_security_detect_vague_terms_py,scripts_governance_d6_security_retire_tmp_artifacts_py,scripts_governance_d6_security_run_adversarial_checks_py,scripts_governance_d6_security_scan_runtime_log_secrets_py,scripts_governance_d6_security_scan_secret_leak_py,scripts_governance_d6_security_validate_gate_discipline_py,scripts_governance_d7_code_any_type_inferrer_py,scripts_governance_d7_code_check_ai_capability_boundary_py,scripts_governance_d7_code_check_any_abuse_py,scripts_governance_d7_code_check_encoding_py,scripts_governance_d7_code_check_idempotency_py,scripts_governance_d7_code_check_merge_conflict_py,scripts_governance_d7_code_check_no_tests_unit_py,scripts_governance_d7_code_check_pit_compliance_py,scripts_governance_d7_code_detect_absolute_path_hardcoding_py,scripts_governance_d7_code_detect_direct_llm_calls_py,scripts_governance_d7_code_detect_forward_reference_py,scripts_governance_d7_code_detect_missing_encoding_py,scripts_governance_d7_code_detect_private_key_py,scripts_governance_d7_code_detect_pydantic_any_fields_py,scripts_governance_d7_code_detect_silent_degradation_py,scripts_governance_d7_code_fix_n06_scope_py,scripts_governance_d7_code_fix_n12_ke_naming_py,scripts_governance_d7_code_fix_n13_snake_case_py,scripts_governance_d7_code_fix_n14_init_all_py,scripts_governance_d7_code_fix_n15_blueprint_path_py,scripts_governance_d7_code_fix_naming_manual_py,scripts_governance_d7_code_fix_orphan_exports_py,scripts_governance_d7_code_rewrite_imports_py,scripts_governance_d7_code_scan_complexity_py,scripts_governance_d7_code_scan_consumers_accuracy_py,scripts_governance_d7_code_scan_debt_py,scripts_governance_d7_code_validate_contracts_purity_py,scripts_governance_d7_code_validate_docstring_coverage_py,scripts_governance_d7_code_validate_fle_action_metadata_py,scripts_governance_d7_code_validate_fle_imports_py,scripts_governance_d7_code_validate_import_style_py,scripts_governance_d7_code_validate_init_all_py,scripts_governance_d7_code_validate_kb_write_provenance_py,scripts_governance_d7_code_validate_python_syntax_py,scripts_governance_d7_code_validate_test_assertion_depth_py,scripts_governance_d7_code_validate_test_coverage_py,scripts_governance_d7_code_validate_type_annotation_coverage_py,scripts_governance_d7_code_validate_unused_imports_py,scripts_governance_d8_doc_sync_audit_rename_completeness_py,scripts_governance_d8_doc_sync_auto_sync_all_registries_py,scripts_governance_d8_doc_sync_detect_ai_products_in_docs_py,scripts_governance_d8_doc_sync_detect_dated_snapshots_py,scripts_governance_d8_doc_sync_sync_rule_registry_py,scripts_governance_d8_doc_sync_sync_yaml_to_depgraph_py,scripts_governance_d8_doc_sync_update_progress_py,scripts_governance_d8_doc_sync_validate_document_lifecycle_py,scripts_governance_d8_doc_sync_validate_document_ttl_py,scripts_governance_d9_knowledge_detect_duplicated_normative_language_py,scripts_governance_d9_knowledge_detect_orphan_documents_py,scripts_governance_data_quality_check_tick_duplication_py,scripts_governance_extract_decisiongraph_py,scripts_governance_extract_depgraph_py,scripts_governance_generate_decision_graph_py,scripts_governance_generate_project_depgraph_py,scripts_governance_generate_project_path_tree_py,scripts_governance_generators_check_gate_inventory_drift_py,scripts_governance_generators_fix_module_manifest_layout_py,scripts_governance_generators_generate_gate_registry_py,scripts_governance_generators_generate_path_ownership_map_py,scripts_governance_generators_generate_registry_master_index_py,scripts_governance_generators_inject_manifests_py,scripts_governance_generators_refresh_master_entries_py,scripts_governance_generators_sync_audit_protocol_numbers_py,scripts_governance_git_health_smoke_py,scripts_governance_meta_concurrency_py,scripts_governance_meta_arbitrate_findings_py,scripts_governance_meta_backup_runtime_state_py,scripts_governance_meta_benchmark_test_fixtures_bad_imports_py,scripts_governance_meta_benchmark_test_fixtures_incomplete_module_py,scripts_governance_meta_benchmark_test_fixtures_orphan_file_without_module_registration_py,scripts_governance_meta_compute_sla_metrics_py,scripts_governance_meta_create_task_from_finding_py,scripts_governance_meta_detect_config_deviation_py,scripts_governance_meta_detect_fix_oscillation_py,scripts_governance_meta_detect_hallucinated_packages_py,scripts_governance_meta_detect_script_divergence_py,scripts_governance_meta_detect_script_rot_py,scripts_governance_meta_env_check_py,scripts_governance_meta_finding_state_machine_py,scripts_governance_meta_gate_engine_selfcheck_py,scripts_governance_meta_governance_watchdog_py,scripts_governance_meta_manage_baseline_py,scripts_governance_meta_manage_error_budget_py,scripts_governance_meta_manage_finding_timeseries_py,scripts_governance_meta_manage_script_ab_test_py,scripts_governance_meta_manage_script_retirement_py,scripts_governance_meta_manage_shadow_mode_py,scripts_governance_meta_mutation_test_post_sync_validator_py,scripts_governance_meta_mutation_test_reconciliation_registry_py,scripts_governance_meta_phase_e_context_check_py,scripts_governance_meta_pre_op_check_py,scripts_governance_meta_score_script_effectiveness_py,scripts_governance_meta_session_startup_check_py,scripts_governance_meta_trace_finding_lifecycle_py,scripts_governance_meta_track_script_costs_py,scripts_governance_meta_validate_automation_boundary_py,scripts_governance_meta_validate_cross_model_consensus_py,scripts_governance_meta_validate_dependency_chain_py,scripts_governance_meta_validate_emergency_bypass_log_py,scripts_governance_meta_validate_end_to_end_benchmark_py,scripts_governance_meta_validate_environment_health_py,scripts_governance_meta_validate_false_negatives_py,scripts_governance_meta_validate_gate_engine_external_py,scripts_governance_meta_validate_mutation_testing_py,scripts_governance_meta_validate_rule_freshness_py,scripts_governance_meta_validate_rules_file_backdoor_py,scripts_governance_meta_validate_rules_integrity_py,scripts_governance_meta_validate_script_onboarding_py,scripts_governance_meta_validate_script_provenance_py,scripts_governance_meta_validate_script_system_health_py,scripts_governance_meta_validate_threshold_changes_py,scripts_governance_meta_validate_trust_tier_py,scripts_governance_meta_verify_reconciliation_registry_py,scripts_governance_migrate_sqlite_to_pg_migrate_data_py,scripts_governance_migrate_sqlite_to_pg_seed_from_yaml_py,scripts_governance_migrate_to_metadata_tables_py,scripts_governance_oneoff_data_domain_audit_query_py,scripts_governance_query_module_panorama_py,scripts_governance_register_deferred_modules_py,scripts_governance_repair_concurrent_commit_test_py,scripts_governance_run_all_py,scripts_governance_run_gate_chain_py,scripts_governance_run_silent_failure_regression_py,scripts_governance_session_startup_health_check_py,scripts_governance_status_py,scripts_governance_sync_panorama_module_py,scripts_governance_verify_sync_integrity_py,scripts_governance_vms_vms_blindspot_check_py,scripts_governance_vms_vms_build_completion_check_py,scripts_governance_vms_vms_cron_monitor_py,scripts_governance_vms_vms_cross_file_check_py,scripts_governance_vms_vms_health_check_py,scripts_governance_vms_vms_migrate_py,scripts_governance_vms_vms_migration_dry_run_py,scripts_governance_vms_vms_phase_rollback_py,scripts_governance_vms_vms_version_sync_check_py,tests_governance_scripts_governance_test_any_type_inferrer_py,tests_governance_scripts_governance_test_check_canonical_yaml_drift_py,tests_governance_scripts_governance_test_check_vocab_hardcode_py,tests_governance_scripts_governance_test_pre_write_gate_py,tests_governance_test_check_blueprint_code_alignment_py production
    class scripts_governance_oneoff_data_domain_design_state_complete_py design
    class D_GOV_AUDIT,D_SHARED,D_DATA,D_GOVERNANCE,D_GOV_ENFORCEMENT,D_GOV_RULE,D_GOV_DRIFT,D_GOV_DOCS external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | generate代码wikistats / Generate Code Wiki Stats (generat... | → | D_DATA 数据接入层: table注册表 / Table Registry (data/table_registry.py) | 导入依赖 / import_depends |
| 2 | generate数据inventory / Generate Data Inventory (generato... | → | D_DATA 数据接入层: 数据接入层域包 / Data Domain Package (data/__init__.py) | 导入依赖 / import_depends |
| 3 | generate数据inventory / Generate Data Inventory (generato... | → | D_DATA 数据接入层: chreader / Ch Reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 4 | 检查tickduplication / Check Tick Duplication (data_qualit... | → | D_DATA 数据接入层: 数据接入层域包 / Data Domain Package (data/__init__.py) | 导入依赖 / import_depends |
| 5 | 检查tickduplication / Check Tick Duplication (data_qualit... | → | D_DATA 数据接入层: chreader / Ch Reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 6 | 审计后同步commands / Audit Post Sync Commands (one_off/au... | → | D_GOVERNANCE 生命周期管理: 后同步校验器 / Post Sync Validator (architecture_governan... | 导入依赖 / import_depends |
| 7 | create对齐任务 / Create Alignment Tasks (one_off/create_a... | → | D_GOVERNANCE 生命周期管理: 任务repo / Task Repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 8 | 修复broken后同步 / Fix Broken Post Sync (one_off/fix_brok... | → | D_GOVERNANCE 生命周期管理: 任务repo / Task Repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 9 | construction门禁 / Construction Gate (prototype/construct... | → | D_GOVERNANCE 生命周期管理: 路径resolver / Path Resolver (architecture_governance/pat... | 导入依赖 / import_depends |
| 10 | constants / Constants (_shared/constants.py) | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 11 | 任务show / Task Show (_tasks/task_show.py) | → | D_GOVERNANCE 生命周期管理: sqliteschema / Sqlite Schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 12 | 任务show / Task Show (_tasks/task_show.py) | → | D_GOVERNANCE 生命周期管理: 任务repo / Task Repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 13 | 任务summary / Task Summary (_tasks/task_summary.py) | → | D_GOVERNANCE 生命周期管理: sqliteschema / Sqlite Schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 14 | 任务summary / Task Summary (_tasks/task_summary.py) | → | D_GOVERNANCE 生命周期管理: 任务repo / Task Repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 15 | adddeferred设计edges / Add Deferred Design Edges (governa... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 16 | applydataflowgraph / Apply Dataflowgraph (governance/appl... | → | D_GOVERNANCE 生命周期管理: dataflowgraphschema / Dataflowgraph Schema (persistence/d... | 导入依赖 / import_depends |
| 17 | applydecisiongraph / Apply Decisiongraph (governance/appl... | → | D_GOVERNANCE 生命周期管理: decisiongraphschema / Decisiongraph Schema (persistence/d... | 导入依赖 / import_depends |
| 18 | 检查ssot门禁 / Check Ssot Gate (governance/check_ssot_gat... | → | D_GOVERNANCE 生命周期管理: 能力lookup / Capability Lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 19 | 任务自我检查 / Task Self Check (d11_compliance/task_self_... | → | D_GOVERNANCE 生命周期管理: sqliteschema / Sqlite Schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 20 | 任务自我检查 / Task Self Check (d11_compliance/task_self_... | → | D_GOVERNANCE 生命周期管理: 任务repo / Task Repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 21 | verifyschema健康 / Verify Schema Health (d11_compliance/v... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 22 | verifyschema健康 / Verify Schema Health (d11_compliance/v... | → | D_GOVERNANCE 生命周期管理: decisiongraphschema / Decisiongraph Schema (persistence/d... | 导入依赖 / import_depends |
| 23 | 检查schema版本writes / Check Schema Version Writes (d3_me... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 24 | analyzechangeimpact / Analyze Change Impact (d5_architect... | → | D_GOVERNANCE 生命周期管理: LLMimpact分析器 / LLM Impact Analyzer (architecture_gover... | 导入依赖 / import_depends |
| 25 | alignpanoramas / Align Panoramas (generators/align_panora... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 26 | alignpanoramas / Align Panoramas (generators/align_panora... | → | D_GOVERNANCE 生命周期管理: dataflowgraphschema / Dataflowgraph Schema (persistence/d... | 导入依赖 / import_depends |
| 27 | alignpanoramas / Align Panoramas (generators/align_panora... | → | D_GOVERNANCE 生命周期管理: decisiongraphschema / Decisiongraph Schema (persistence/d... | 导入依赖 / import_depends |
| 28 | generate蓝图panorama / Generate Blueprint Panorama (gener... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 29 | generate蓝图panorama / Generate Blueprint Panorama (gener... | → | D_GOVERNANCE 生命周期管理: dataflowgraphschema / Dataflowgraph Schema (persistence/d... | 导入依赖 / import_depends |
| 30 | generate蓝图panorama / Generate Blueprint Panorama (gener... | → | D_GOVERNANCE 生命周期管理: decisiongraphschema / Decisiongraph Schema (persistence/d... | 导入依赖 / import_depends |
| 31 | generatedataflowdiagram / Generate Dataflow Diagram (gene... | → | D_GOVERNANCE 生命周期管理: dataflowgraphschema / Dataflowgraph Schema (persistence/d... | 导入依赖 / import_depends |
| 32 | generate决策diagram / Generate Decision Diagram (generato... | → | D_GOVERNANCE 生命周期管理: decisiongraphschema / Decisiongraph Schema (persistence/d... | 导入依赖 / import_depends |
| 33 | generatetrading流diagram / Generate Trading Flow Diagram ... | → | D_GOVERNANCE 生命周期管理: 决策graphreader / Decision Graph Reader (persistence/deci... | 导入依赖 / import_depends |
| 34 | 蓝图frontmatterreconciler / Blueprint Frontmatter Reconci... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 35 | 同步yaml转depgraph / Sync Yaml To Depgraph (d8_doc_sync/s... | → | D_GOVERNANCE 生命周期管理: dataflowgraphschema / Dataflowgraph Schema (persistence/d... | 导入依赖 / import_depends |
| 36 | extractdecisiongraph / Extract Decisiongraph (governance/... | → | D_GOVERNANCE 生命周期管理: 决策graphreader / Decision Graph Reader (persistence/deci... | 导入依赖 / import_depends |
| 37 | extractdecisiongraph / Extract Decisiongraph (governance/... | → | D_GOVERNANCE 生命周期管理: decisiongraphschema / Decisiongraph Schema (persistence/d... | 导入依赖 / import_depends |
| 38 | generate决策graph / Generate Decision Graph (governance/g... | → | D_GOVERNANCE 生命周期管理: decisiongraphschema / Decisiongraph Schema (persistence/d... | 导入依赖 / import_depends |
| 39 | generateprojectdepgraph / Generate Project Depgraph (gove... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 40 | generate路径ownershipmap / Generate Path Ownership Map (g... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 41 | generate路径ownershipmap / Generate Path Ownership Map (g... | → | D_GOVERNANCE 生命周期管理: 规则patterns / Rule Patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 42 | backup运行时状态 / Backup Runtime State (meta/backup_runt... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 43 | create任务from发现 / Create Task From Finding (meta/creat... | → | D_GOVERNANCE 生命周期管理: sqliteschema / Sqlite Schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 44 | create任务from发现 / Create Task From Finding (meta/creat... | → | D_GOVERNANCE 生命周期管理: 任务repo / Task Repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 45 | migrate转metadatatables / Migrate To Metadata Tables (gov... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 46 | 数据domain审计query / Data Domain Audit Query (oneoff/dat... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 47 | query模块panorama / Query Module Panorama (governance/que... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 48 | query模块panorama / Query Module Panorama (governance/que... | → | D_GOVERNANCE 生命周期管理: dataflowgraphschema / Dataflowgraph Schema (persistence/d... | 导入依赖 / import_depends |
| 49 | query模块panorama / Query Module Panorama (governance/que... | → | D_GOVERNANCE 生命周期管理: decisiongraphschema / Decisiongraph Schema (persistence/d... | 导入依赖 / import_depends |
| 50 | registerdeferredmodules / Register Deferred Modules (gove... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 51 | 同步panorama模块 / Sync Panorama Module (governance/sync_... | → | D_GOVERNANCE 生命周期管理: depgraphschema / Depgraph Schema (governance/depgraph_sch... | 导入依赖 / import_depends |
| 52 | 同步panorama模块 / Sync Panorama Module (governance/sync_... | → | D_GOVERNANCE 生命周期管理: dataflowgraphschema / Dataflowgraph Schema (persistence/d... | 导入依赖 / import_depends |
| 53 | 同步panorama模块 / Sync Panorama Module (governance/sync_... | → | D_GOVERNANCE 生命周期管理: decisiongraphschema / Decisiongraph Schema (persistence/d... | 导入依赖 / import_depends |
| 54 | 对抗sysmaster测试 / Adversarial Sys Master Test (prototyp... | → | D_GOV_AUDIT 审计追踪: sysmaster合规 / Sys Master Compliance (rule_enforcement/s... | 导入依赖 / import_depends |
| 55 | rebuild审计索引 / Rebuild Audit Index (prototype/rebuild_... | → | D_GOV_AUDIT 审计追踪: indexer / Indexer (gov_audit/indexer.py) | 导入依赖 / import_depends |
| 56 | 架构健康仪表板 / Architecture Health Dashboard (governanc... | → | D_GOV_AUDIT 审计追踪: 运行时违规snapshot / Runtime Violation Snapshot (audit/ru... | 导入依赖 / import_depends |
| 57 | 会话启动健康检查 / Session Startup Health Check (governan... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 58 | scanconsumersaccuracy / Scan Consumers Accuracy (d7_code/... | → | D_GOV_CODE_QUALITY 代码质量治理: 差异helpers / Diff Helpers (commit_gates/_diff_helpers.py) | 导入依赖 / import_depends |
| 59 | scanconsumersaccuracy / Scan Consumers Accuracy (d7_code/... | → | D_GOV_CODE_QUALITY 代码质量治理: consumersaccuracy门禁 / Consumers Accuracy Gate (commit_g... | 导入依赖 / import_depends |
| 60 | concurrentcommit测试 / Concurrent Commit Test (repair/con... | → | D_GOV_ENFORCEMENT 规则执行: gitcommitgateway / Git Commit Gateway (rule_bridge/git_co... | 导入依赖 / import_depends |
| 61 | 会话启动检查 / Session Startup Check (meta/session_startu... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: phase检查注册表 / Phase Check Registry (ops_governance/ph... | 导入依赖 / import_depends |
| 62 | 会话启动检查 / Session Startup Check (meta/session_startu... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: phase管理器 / Phase Manager (ops_governance/phase_manager... | 导入依赖 / import_depends |
| 63 | 检查预算健康 / Check Budget Health (d5_architecture/check... | → | D_GOV_REPAIR 治理修复: 预算enforcement / Budget Enforcement (financial_governanc... | 导入依赖 / import_depends |
| 64 | cbg重置 / Cbg Reset (d1_structure/cbg_reset.py) | → | D_GOV_RULE 规则治理: 单向熔断器 / Circuit Breaker (rule_enforcement/circuit_br... | 导入依赖 / import_depends |
| 65 | 重置cbg / Reset Cbg (d1_structure/reset_cbg.py) | → | D_GOV_RULE 规则治理: 单向熔断器 / Circuit Breaker (rule_enforcement/circuit_br... | 导入依赖 / import_depends |
| 66 | create任务from发现 / Create Task From Finding (meta/creat... | → | D_GOV_RULE 规则治理: 任务类型定义 / Task Types (rule_enforcement/task_types.py) | 导入依赖 / import_depends |
| 67 | 门禁引擎selfcheck / Gate Engine Selfcheck (meta/gate_engi... | → | D_GOV_RULE 规则治理: 门禁裁决引擎 / Gate Engine (gate_engine/gate_engine.py) | 导入依赖 / import_depends |
| 68 | validate门禁引擎external / Validate Gate Engine External ... | → | D_GOV_RULE 规则治理: 单向熔断器 / Circuit Breaker (rule_enforcement/circuit_br... | 导入依赖 / import_depends |
| 69 | validate门禁引擎external / Validate Gate Engine External ... | → | D_GOV_RULE 规则治理: 门禁裁决引擎 / Gate Engine (gate_engine/gate_engine.py) | 导入依赖 / import_depends |
| 70 | 会话simulator / Session Simulator (prototype/session_simu... | → | D_INFRA_RUNTIME 运行时集成: 蓝图指标 / Blueprint Metrics (metrics/blueprint_metrics.py) | 导入依赖 / import_depends |
| 71 | 基础 / Base (_shared/base.py) | → | D_INFRA_RUNTIME 运行时集成: 发现 / Finding (script_system/finding.py) | 导入依赖 / import_depends |
| 72 | 检查注册表一致性 / Check Registry Consistency (d3_metadat... | → | D_INFRA_RUNTIME 运行时集成: 发现 / Finding (script_system/finding.py) | 导入依赖 / import_depends |
| 73 | 发现状态machine / Finding State Machine (meta/finding_sta... | → | D_INFRA_RUNTIME 运行时集成: 发现 / Finding (script_system/finding.py) | 导入依赖 / import_depends |
| 74 | validateemergency旁路log / Validate Emergency Bypass Log ... | → | D_INFRA_RUNTIME 运行时集成: 发现 / Finding (script_system/finding.py) | 导入依赖 / import_depends |
| 75 | run全量 / Run All (governance/run_all.py) | → | D_INFRA_RUNTIME 运行时集成: 发现任务桥接 / Finding Task Bridge (infrastructure/findin... | 导入依赖 / import_depends |
| 76 | run全量 / Run All (governance/run_all.py) | → | D_INFRA_RUNTIME 运行时集成: 发现 / Finding (script_system/finding.py) | 导入依赖 / import_depends |
| 77 | VMScron监控器 / VMS Cron Monitor (vms_ri/vms_cron_monitor... | → | D_INTEGRATION 管线路由: 集合管理器 / Collection Manager (vector_memory/collection... | 导入依赖 / import_depends |
| 78 | VMScron监控器 / VMS Cron Monitor (vms_ri/vms_cron_monitor... | → | D_INTEGRATION 管线路由: 索引健康监控器 / Index Health Monitor (vector_memory/inde... | 导入依赖 / import_depends |
| 79 | VMS健康检查 / VMS Health Check (vms_ri/vms_health_check.py) | → | D_INTEGRATION 管线路由: 集合管理器 / Collection Manager (vector_memory/collection... | 导入依赖 / import_depends |
| 80 | VMS健康检查 / VMS Health Check (vms_ri/vms_health_check.py) | → | D_INTEGRATION 管线路由: 索引健康监控器 / Index Health Monitor (vector_memory/inde... | 导入依赖 / import_depends |
| 81 | VMSmigrate / VMS Migrate (vms_ri/vms_migrate.py) | → | D_INTEGRATION 管线路由: 桥接层 / Bridge Layer (vector_memory/bridge_layer.py) | 导入依赖 / import_depends |
| 82 | VMSmigrate / VMS Migrate (vms_ri/vms_migrate.py) | → | D_INTEGRATION 管线路由: 集合管理器 / Collection Manager (vector_memory/collection... | 导入依赖 / import_depends |
| 83 | VMS迁移dryrun / VMS Migration Dry Run (vms_ri/vms_migrati... | → | D_INTEGRATION 管线路由: 桥接层 / Bridge Layer (vector_memory/bridge_layer.py) | 导入依赖 / import_depends |
| 84 | VMScron监控器 / VMS Cron Monitor (vms/vms_cron_monitor.py) | → | D_INTEGRATION 管线路由: 集合管理器 / Collection Manager (vector_memory/collection... | 导入依赖 / import_depends |
| 85 | VMScron监控器 / VMS Cron Monitor (vms/vms_cron_monitor.py) | → | D_INTEGRATION 管线路由: 索引健康监控器 / Index Health Monitor (vector_memory/inde... | 导入依赖 / import_depends |
| 86 | VMS健康检查 / VMS Health Check (vms/vms_health_check.py) | → | D_INTEGRATION 管线路由: 集合管理器 / Collection Manager (vector_memory/collection... | 导入依赖 / import_depends |
| 87 | VMS健康检查 / VMS Health Check (vms/vms_health_check.py) | → | D_INTEGRATION 管线路由: 索引健康监控器 / Index Health Monitor (vector_memory/inde... | 导入依赖 / import_depends |
| 88 | VMSmigrate / VMS Migrate (vms/vms_migrate.py) | → | D_INTEGRATION 管线路由: 桥接层 / Bridge Layer (vector_memory/bridge_layer.py) | 导入依赖 / import_depends |
| 89 | VMSmigrate / VMS Migrate (vms/vms_migrate.py) | → | D_INTEGRATION 管线路由: 集合管理器 / Collection Manager (vector_memory/collection... | 导入依赖 / import_depends |
| 90 | VMS迁移dryrun / VMS Migration Dry Run (vms/vms_migration_... | → | D_INTEGRATION 管线路由: 桥接层 / Bridge Layer (vector_memory/bridge_layer.py) | 导入依赖 / import_depends |
| 91 | 检查examcase一致性 / Check Exam Case Consistency (one_off... | → | D_INTELLIGENCE 上下文管理: exam测试cases / Exam Test Cases (model_profiling/exam_tes... | 导入依赖 / import_depends |
| 92 | 检查handoffmanifests / Check Handoff Manifests (d1_struct... | → | D_ORCHESTRATOR 代理编排器: contract注册表 / Contract Registry (contracts/contract_re... | 导入依赖 / import_depends |
| 93 | 预write门禁 / Pre Write Gate (d5_architecture/pre_write_g... | → | D_SECURITY 对抗验证: 会话concurrency / Session Concurrency (access_control/ses... | 导入依赖 / import_depends |
| 94 | dm106p2b验证 / Dm106 P2b Verification (governance/dm106_p... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 95 | 审计后同步commands / Audit Post Sync Commands (one_off/au... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 96 | dm105depgraphtriage / Dm105 Depgraph Triage (one_off/dm10... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 97 | constants / Constants (_shared/constants.py) | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 98 | 文件utils / File Utils (_shared/file_utils.py) | → | D_SHARED 共享服务: 文件utils / File Utils (io/file_utils.py) | 导入依赖 / import_depends |
| 99 | yamlutils / Yaml Utils (_shared/yaml_utils.py) | → | D_SHARED 共享服务: yamlutils / Yaml Utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 100 | applydecisiongraph / Apply Decisiongraph (governance/appl... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 101 | applydepgraph / Apply Depgraph (governance/apply_depgraph... | → | D_SHARED 共享服务: 环境 / Env (foundation/env.py) | 导入依赖 / import_depends |
| 102 | applydepgraph / Apply Depgraph (governance/apply_depgraph... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 103 | applydepgraph / Apply Depgraph (governance/apply_depgraph... | → | D_SHARED 共享服务: yamlutils / Yaml Utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 104 | 检查ssot门禁 / Check Ssot Gate (governance/check_ssot_gat... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 105 | 检查模块singlesource / Check Module Singlesource (d3_meta... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 106 | diagnosedepgraph / Diagnose Depgraph (d5_architecture/dia... | → | D_SHARED 共享服务: yamlutils / Yaml Utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 107 | alignpanoramas / Align Panoramas (generators/align_panora... | → | D_SHARED 共享服务: converters / Converters (utils/converters.py) | 导入依赖 / import_depends |
| 108 | generateassetcatalog / Generate Asset Catalog (generators... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 109 | generate代码wikistats / Generate Code Wiki Stats (generat... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 110 | generatecontractcatalog / Generate Contract Catalog (gene... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 111 | generate契约 / Generate Contracts (generators/generate_co... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 112 | generatepanorama注册表 / Generate Panorama Registry (gene... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 113 | validate模块生命周期 / Validate Module Lifecycle (lifecyc... | → | D_SHARED 共享服务: yamlutils / Yaml Utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 114 | validateinterface契约 / Validate Interface Contracts (val... | → | D_SHARED 共享服务: yamlutils / Yaml Utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 115 | extractdecisiongraph / Extract Decisiongraph (governance/... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 116 | extractdepgraph / Extract Depgraph (governance/extract_de... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 117 | generate决策graph / Generate Decision Graph (governance/g... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 118 | generateprojectdepgraph / Generate Project Depgraph (gove... | → | D_SHARED 共享服务: process池 / Process Pool (infra/process_pool.py) | 导入依赖 / import_depends |
| 119 | generateprojectdepgraph / Generate Project Depgraph (gove... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 120 | generateprojectdepgraph / Generate Project Depgraph (gove... | → | D_SHARED 共享服务: yamlutils / Yaml Utils (io/yaml_utils.py) | 导入依赖 / import_depends |
| 121 | 检查门禁inventory漂移 / Check Gate Inventory Drift (gener... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 122 | concurrency / Concurrency (meta/_concurrency.py) | → | D_SHARED 共享服务: process池 / Process Pool (infra/process_pool.py) | 导入依赖 / import_depends |
| 123 | create任务from发现 / Create Task From Finding (meta/creat... | → | D_SHARED 共享服务: 模型 / Models (foundation/models.py) | 导入依赖 / import_depends |
| 124 | create任务from发现 / Create Task From Finding (meta/creat... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 125 | migrate数据 / Migrate Data (migrate_sqlite_to_pg/migrate_... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 126 | concurrentcommit测试 / Concurrent Commit Test (repair/con... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 127 | 同步panorama模块 / Sync Panorama Module (governance/sync_... | → | D_SHARED 共享服务: converters / Converters (utils/converters.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_PERM 自治保护: 检查killswitchlatency / Check Kill Switch Latency (fitnes... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 2 | D_AUTONOMY_PERM 自治保护: managekillswitch / Manage Kill Switch (meta/manage_kill_s... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 3 | D_AUTONOMY_PERM 自治保护: managekillswitch / Manage Kill Switch (meta/manage_kill_s... | → | 文件utils / File Utils (_shared/file_utils.py) | 导入依赖 / import_depends |
| 4 | D_GOVERNANCE 生命周期管理: 架构ssot / Arch Ssot (arch_guard/_arch_ssot.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: buildocp清单 / Build Ocp Manifest (_tools/build_ocp_manif... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: injectidempotency / Inject Idempotency (_tools/inject_ide... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: patchp1paths / Patch P1 Paths (_tools/patch_p1_paths.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 8 | D_GOVERNANCE 生命周期管理: 检查aclboundary / Check Acl Boundary (arch_guard/check_ac... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 9 | D_GOVERNANCE 生命周期管理: 检查跨planecommunication / Check Cross Plane Communicatio... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 10 | D_GOVERNANCE 生命周期管理: 检查feaclboundary / Check Fe Acl Boundary (arch_guard/che... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 11 | D_GOVERNANCE 生命周期管理: 检查hot路径purity / Check Hot Path Purity (arch_guard/che... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 12 | D_GOVERNANCE 生命周期管理: 检查scaffoldexit门禁 / Check Scaffold Exit Gates (arch_gu... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 13 | D_GOVERNANCE 生命周期管理: 检查scaffoldexit门禁 / Check Scaffold Exit Gates (arch_gu... | → | yamlutils / Yaml Utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 14 | D_GOVERNANCE 生命周期管理: 检查schema一致性 / Check Schema Consistency (arch_guard/c... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 15 | D_GOVERNANCE 生命周期管理: 检查aisggateway / Check Aisg Gateway (fitness_functions/c... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 16 | D_GOVERNANCE 生命周期管理: 检查审计logimmutability / Check Audit Log Immutability (f... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 17 | D_GOVERNANCE 生命周期管理: 检查日常loss限制 / Check Daily Loss Limit (fitness_functi... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 18 | D_GOVERNANCE 生命周期管理: 检查hotwarmipc / Check Hot Warm Ipc (fitness_functions/ch... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 19 | D_GOVERNANCE 生命周期管理: 检查idempotencykey / Check Idempotency Key (fitness_funct... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 20 | D_GOVERNANCE 生命周期管理: 检查logsecretleak / Check Log Secret Leak (fitness_functi... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 21 | D_GOVERNANCE 生命周期管理: 检查no跨planemutable状态 / Check No Cross Plane Mutable S... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 22 | D_GOVERNANCE 生命周期管理: 检查ocpsignatures / Check Ocp Signatures (fitness_functio... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 23 | D_GOVERNANCE 生命周期管理: 检查pit合规 / Check Pit Compliance (fitness_functions/che... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 24 | D_GOVERNANCE 生命周期管理: 检查position限制 / Check Position Limit (fitness_function... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 25 | D_GOVERNANCE 生命周期管理: 检查风险params一致性 / Check Risk Params Consistency (fit... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 26 | D_GOVERNANCE 生命周期管理: 检查warm冷异步 / Check Warm Cold Async (fitness_functions... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 27 | D_GOVERNANCE 生命周期管理: 重置测试任务 / Reset Test Task (construction/reset_test_t... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 28 | D_GOVERNANCE 生命周期管理: 启动brain / Start Brain (construction/start_brain.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 29 | D_GOVERNANCE 生命周期管理: dm90971add测试headers / Dm90971 Add Test Headers (scripts... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 30 | D_GOVERNANCE 生命周期管理: 修复orphan全量 / Fix Orphan All (scripts/fix_orphan_all.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 31 | D_GOVERNANCE 生命周期管理: 修复orphan全量 / Fix Orphan All (scripts/fix_orphan_all.py) | → | 文件utils / File Utils (_shared/file_utils.py) | 导入依赖 / import_depends |
| 32 | D_GOVERNANCE 生命周期管理: generatepathway注册表 / Generate Pathway Registry (script... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 33 | D_GOVERNANCE 生命周期管理: 检查pureshim / Check Pure Shim (d7_code/check_pure_shim.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 34 | D_GOVERNANCE 生命周期管理: 检查pureshim / Check Pure Shim (d7_code/check_pure_shim.py) | → | encoding / Encoding (_shared/encoding.py) | 导入依赖 / import_depends |
| 35 | D_GOVERNANCE 生命周期管理: generate规则AIperception索引 / Generate Rule AI Perceptio... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 36 | D_GOVERNANCE 生命周期管理: 自动handofflog / Auto Handoff Log (hooks/auto_handoff_log... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 37 | D_GOVERNANCE 生命周期管理: generateide配置 / Generate Ide Config (mcp/generate_ide_c... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 38 | D_GOVERNANCE 生命周期管理: launcher / Launcher (mcp/launcher.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 39 | D_GOVERNANCE 生命周期管理: 启动全量 / Start All (mcp/start_all.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 40 | D_GOVERNANCE 生命周期管理: stop全量 / Stop All (mcp/stop_all.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 41 | D_GOVERNANCE 生命周期管理: dm311autonomy核心split / Dm311 Autonomy Core Split (migra... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 42 | D_GOVERNANCE 生命周期管理: dm314infra运维split / Dm314 Infra Ops Split (migration/dm... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 43 | D_GOVERNANCE 生命周期管理: verifyheadercompleteness / Verify Header Completeness (op... | → | frontmatter / Frontmatter (_shared/frontmatter.py) | 导入依赖 / import_depends |
| 44 | D_GOVERNANCE 生命周期管理: verifydedup / Verify Dedup (pre_commit/verify_dedup.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 45 | D_GOVERNANCE 生命周期管理: scaffold / Scaffold (scripts/scaffold.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 46 | D_GOVERNANCE 生命周期管理: scaffold / Scaffold (scripts/scaffold.py) | → | yamlutils / Yaml Utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 47 | D_GOVERNANCE 生命周期管理: scaffold / Scaffold (scripts/scaffold.py) | → | 检查命名约定 / Check Naming Convention (d3_metadata/check... | 导入依赖 / import_depends |
| 48 | D_GOVERNANCE 生命周期管理: 测试generate门禁注册表 / Test Generate Gate Registry (gen... | → | generate门禁注册表 / Generate Gate Registry (generators/g... | 测试依赖 / test_depends |
| 49 | D_GOV_AUDIT 审计追踪: 审计设计completeness / Audit Design Completeness (repair/... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 50 | D_GOV_AUDIT 审计追踪: redblue测试 / Red Blue Test (repair/red_blue_test.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 51 | D_GOV_AUDIT 审计追踪: rollbackdepgraph / Rollback Depgraph (repair/rollback_dep... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 52 | D_GOV_AUDIT 审计追踪: 测试remediationprogresssmoke / Test Remediation Progress ... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 53 | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | → | validate模块id命名 / Validate Module Id Naming (d3_metada... | 导入依赖 / import_depends |
| 54 | D_GOV_AUDIT 审计追踪: 对账注册表 / Reconciliation Registry (audit/reconciliatio... | → | 检查门禁inventory漂移 / Check Gate Inventory Drift (gener... | 导入依赖 / import_depends |
| 55 | D_GOV_CODE_QUALITY 代码质量治理: 检查模块id一致性 / Check Module Id Consistency (d7_code/c... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 56 | D_GOV_DOCS 架构文档治理: 测试guc触发器修复 / Test Guc Trigger Fix (d8_doc_sync/tes... | → | constants / Constants (_shared/constants.py) | 测试依赖 / test_depends |
| 57 | D_GOV_DOCS 架构文档治理: 测试同步savepointisolation / Test Sync Savepoint Isolatio... | → | constants / Constants (_shared/constants.py) | 测试依赖 / test_depends |
| 58 | D_GOV_DRIFT 漂移检测: validate蓝图overlap / Validate Blueprint Overlap (d11_com... | → | frontmatter / Frontmatter (_shared/frontmatter.py) | 导入依赖 / import_depends |
| 59 | D_GOV_DRIFT 漂移检测: validatetruth源级联 / Validate Truth Source Cascade (d11_... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 60 | D_GOV_DRIFT 漂移检测: validatetruth源级联 / Validate Truth Source Cascade (d11_... | → | frontmatter / Frontmatter (_shared/frontmatter.py) | 导入依赖 / import_depends |
| 61 | D_GOV_DRIFT 漂移检测: validatessot / Validate Ssot (validators/validate_ssot.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 62 | D_GOV_DRIFT 漂移检测: validatessot / Validate Ssot (validators/validate_ssot.py) | → | encoding / Encoding (_shared/encoding.py) | 导入依赖 / import_depends |
| 63 | D_GOV_DRIFT 漂移检测: validatessot / Validate Ssot (validators/validate_ssot.py) | → | frontmatter / Frontmatter (_shared/frontmatter.py) | 导入依赖 / import_depends |
| 64 | D_GOV_DRIFT 漂移检测: validatessot / Validate Ssot (validators/validate_ssot.py) | → | yamlutils / Yaml Utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 65 | D_GOV_ENFORCEMENT 规则执行: metriccount漂移reconciler / Metric Count Drift Reconciler... | → | 架构健康仪表板 / Architecture Health Dashboard (governanc... | 导入依赖 / import_depends |
| 66 | D_GOV_ENFORCEMENT 规则执行: 会话worktree命令行 / Session Worktree CLI (governance/ses... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 67 | D_GOV_RULE 规则治理: 脚本清单自动生成器 / Script Manifest Generator (generator... | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 68 | D_GOV_RULE 规则治理: 脚本清单自动生成器 / Script Manifest Generator (generator... | → | encoding / Encoding (_shared/encoding.py) | 导入依赖 / import_depends |
| 69 | D_GOV_RULE 规则治理: 脚本清单自动生成器 / Script Manifest Generator (generator... | → | 文件utils / File Utils (_shared/file_utils.py) | 导入依赖 / import_depends |
| 70 | D_GOV_RULE 规则治理: 脚本清单自动生成器 / Script Manifest Generator (generator... | → | yamlutils / Yaml Utils (_shared/yaml_utils.py) | 导入依赖 / import_depends |
| 71 | D_OPS 反馈循环: 门禁缓存 / Gate Cache (observability/gate_cache.py) | → | constants / Constants (_shared/constants.py) | 导入依赖 / import_depends |
| 72 | D_OPS 反馈循环: 门禁缓存 / Gate Cache (observability/gate_cache.py) | → | 文件utils / File Utils (_shared/file_utils.py) | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 18 个外部域直接连接（出边 127 条 + 入边 72 条 = 199 条）。只显示直接连接的域，不展开具体节点。

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
    D_GOV_SCRIPTS -->|48条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_SCRIPTS -->|34条 导入依赖 / import_depends| D_SHARED
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
