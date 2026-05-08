---
task_id: "TASK-MST-0015"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §十六 CDC + Can-I-Deploy + DLQ 体系——CT-CDC-001/CT-DLQ-001/CT-RECONCILE-001/CT-STARTUP-001/CT-TEARDOWN-001"

title: "实现 CDC 消费者驱动契约 + Can-I-Deploy 预部署门禁 + DLQ 死信队列体系"
description: |
  实现 §十六 定义的完整 CDC 体系：
  (1)CT-CDC-001 CDC 契约经纪人(Pact Broker 本地 SQLite 简化版)——3步生命周期；
  (2)GATE-CDC-1 Can-I-Deploy 预部署门禁——4项检查（consumer_expectations/schema_version/contract_consistency/health）；
  (3)CT-DLQ-001 死信队列统一契约——SQLite dlq_messages 表 + chronological_ordered replay + max 3 attempts；
  (4)CT-RECONCILE-001 Reconciliation Loop(K8s Controller Pattern)——每30s调和5项invariants；
  (5)CT-STARTUP-001 冷启动契约——5层启动顺序 + 120s全局超时；
  (6)CT-TEARDOWN-001 资源清理契约——TaskCard CANCELLED/FAILED→7系统资源清理。
  Pact Broker 使用本地 SQLite(.audit_cache/cdc_broker.db)存储 consumer expectations。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\cdc_broker.py"
    description: "CDC 契约经纪人——Pact Broker 本地 SQLite 简化版"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\can_i_deploy.py"
    description: "Can-I-Deploy 预部署门禁——4项检查 + GATE-CDC-1"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\dlq_manager.py"
    description: "DLQ 管理器——dlq_messages 表 + chronological replay + circuit breaker"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\reconciliation_loop.py"
    description: "调和循环——CT-RECONCILE-001——5项 invariants 每30s检查"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\startup_sequencer.py"
    description: "冷启动序列器——CT-STARTUP-001——5层启动顺序"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\teardown_manager.py"
    description: "资源清理管理器——CT-TEARDOWN-001——CANCELLED/FAILED 任务跨系统清理"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_cdc_broker.py"
    description: "CDC Broker 单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_can_i_deploy.py"
    description: "Can-I-Deploy 单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_dlq_manager.py"
    description: "DLQ 管理器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\cdc_broker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\can_i_deploy.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\dlq_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\reconciliation_loop.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\startup_sequencer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\teardown_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_cdc_broker.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_can_i_deploy.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_dlq_manager.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§十六——CDC+Can-I-Deploy+DLQ+Reconciliation+Startup+Teardown 6份契约完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 120

acceptance_criteria:
  - "cdc_broker.py 实现 Pact Broker 简化版——consumer defines → provider verifies → can_i_deploy"
  - "can_i_deploy.py 实现 GATE-CDC-1——4项检查全部 PASS 才允许部署"
  - "dlq_manager.py 创建 dlq_messages 表 + chronological replay + max 3 attempts + 72h max age"
  - "reconciliation_loop.py 每 30s 检查 5 项 invariants（TaskCard/Gates/VMS/FLE/DLQ 状态一致性）"
  - "startup_sequencer.py 实现 5 层 boot_order(layer_0→layer_4) + 120s global timeout"
  - "teardown_manager.py 实现 CANCELLED/FAILED 时 7 系统资源清理 + 10s cleanup timeout"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除新增的 6 个源码文件（cdc_broker/can_i_deploy/dlq_manager/reconciliation_loop/startup_sequencer/teardown_manager）
  2. 删除新增的测试文件
  3. 如有创建的 dlq_messages 表——DROP TABLE dlq_messages
  4. 如有创建的 cdc_broker.db——删除 .audit_cache/cdc_broker.db

depends_on: ["TASK-MST-0004"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
