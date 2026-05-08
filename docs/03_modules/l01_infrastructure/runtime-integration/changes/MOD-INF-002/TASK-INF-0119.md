---
task_id: "TASK-INF-0119"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §10 关键关联——15项关联文档 + §11 代码路径索引 + §11.2 配置文件清单"
title: "§10 关键关联依赖验证 + §11 代码路径索引对齐——15项关联文档交叉验证 + 13项配置文件创建"
description: |
  验证蓝图 §10 的 15 项关键关联文档交叉引用+ §11 代码文件路径索引落地。
  §10 关联验证：
  ① shared-core MOD-INF-016（承载10个RI基座）+
  ② capacity-assurance MOD-INF-001（容量SLO约束）+
  ③ gate-engine MOD-INF-007（任务门禁对齐）+
  ④ audit-trail MOD-INF-020（审计追踪消费方）+
  ⑤ rollback-system MOD-INF-021（session-level回滚）+
  ⑥ drift-detector MOD-INF-023（配置漂移增强）+
  ⑦ llm-security MOD-INF-014（Fail-Closed原则对齐）+
  ⑧ agent-rbac MOD-INF-018（审批门权限层级）+
  ⑨ a2a-protocol MOD-INF-025（Agent通信协议）+
  ⑩ knowledge-base MOD-KB-001（AutoDiagnostics→KB补充）+
  ⑪ escalation-protocol MOD-INF-022（升级链）+
  ⑫ budget-enforcer MOD-INF-024（CostTracker消费降级）+
  ⑬ shared/production/limiter.py MOD-INF-016+ 
  ⑭ distributed_lock.py MOD-INF-016+ 
  ⑮ 跨层缺口审计 RL-001~048。
  §11.1 源码文件索引：10个✅(由MOD-INF-016承载)+di_container.py❌+auto_diagnostics.py❌+event_store.py❌+dry_run_simulator.py❌+cost_tracker.py❌
  §11.2 配置文件：event_bus.yaml/resilience_guard.yaml/secrets_policy.yaml/health_check.yaml/telemetry_collector.yaml/cache_layer.yaml/runbooks/llm_pricing.yaml/dry_run_policy.yaml/flag_interaction_matrix.yaml/schema_evolution_policy.yaml/owner_notification_tiers.yaml/trust_decay_policy.yaml——共13项，全部❌待创建。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\cross_reference_validation.md"
    description: "§10 15项关联文档交叉验证报告——逐项检查引用模块文件是否存在+接口是否对齐"
  - path: "D:\\ZephyrAlpha\\config\\config_files_inventory.yaml"
    description: "§11.2 13项配置文件汇总清单——每项标注名称/目标路径/实现状态/对应任务卡ID"
allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\cross_reference_validation.md"
  - "D:\\ZephyrAlpha\\config\\config_files_inventory.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
  - "D:\\ZephyrAlpha\\config\\event_bus.yaml"
  - "D:\\ZephyrAlpha\\config\\resilience_guard.yaml"
applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "所有路径必须与路径映射一致——验证关联文档路径在磁盘上存在"
  - module_id: "MOD-INF-002"
    section: "§10"
    reason: "15项关键关联——逐条验证目标模块blueprint.md 存在"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§10 关键关联表 + §11 代码索引表 + §11.2 配置文件清单"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 45
acceptance_criteria:
  - "§10: 15项关联文档逐条验证——目标路径是否存在、对应模块是否是本蓝图声明的接口"
  - "§10: 所依赖的MOD-INF-016 shared/ 下10个已实现文件路径在磁盘上存在"
  - "§11.1: 15个源码文件路径——逐条标注当前实现状态（✅/❌/N/A）"
  - "§11.1: di_container.py 标注为 MOD-INF-016 planned §2.9 → TASK-INF-0102 覆盖"
  - "§11.2: 13项配置文件——逐条标注目标路径/实现状态/对应任务卡ID"
rollback_instructions: |
  1. 删除 cross_reference_validation.md
  2. 删除 config/config_files_inventory.yaml
depends_on: []
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
