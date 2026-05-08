---
task_id: "TASK-MST-0016"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §十七 SLO/SLI 服务等级目标——CT-SLO-001"

title: "实现 SLO/SLI 服务等级目标与 Error Budget 管理器(CT-SLO-001)"
description: |
  实现 §十七 定义的每条 CT-* 契约的服务等级目标(SLO)与指标(SLI)：
  14 条 CT-* 的 p95/p99 目标 + 告警阈值。
  Error Budget 机制：(1)monthly budget = 1% of total operations = 43.8min downtime/month；
  (2)burn rate > 10x → FLE ESCALATE；
  (3)budget exhausted → halt feature velocity → all resources to reliability。
  SLO 矩阵覆盖：CT-ORC-SCRIPT-001(p95<3600s)/CT-ORC-CE-001(p95<3s)/CT-CE-VMS-001(p99<500ms)/
  CT-ORC-VMS-001(p99<1s)/CT-ORC-GATE-001(p99<50ms)/CT-SCRIPT-GATE-001(p95<30s)/
  CT-CE-LSG-001(p99<100ms+false_positive<5%)/CT-KB-VMS-001(p99<5s)/CT-FLE-ORC-001(p95<30s+false_positive<10%)。
  核心：(1)Telemetry 采集 metrics → FLE 计算 burn rate → 触发 ESCALATE；
  (2)Error Budget 状态管理——burn_rate + budget_remaining + exhaust_policy。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\metrics_collector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\fle_core.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\slo_manager.py"
    description: "SLO/SLI 管理器——14条CT-*目标定义 + Error Budget + burn rate"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\error_budget.py"
    description: "Error Budget 状态机——budget_remaining + burn_rate + exhaust_policy"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_slo_manager.py"
    description: "SLO 管理器单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_error_budget.py"
    description: "Error Budget 单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\slo_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\error_budget.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_slo_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_error_budget.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\metrics_collector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\fle_core.py"

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
    reason: "§十七——CT-SLO-001 14条CT-* SLO矩阵 + Error Budget定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "slo_manager.py 定义 14 条 CT-* 的 p95/p99 目标 + 告警阈值"
  - "error_budget.py 实现 monthly budget=1% → burn_rate > 10x → ESCALATE"
  - "budget exhausted → halt feature velocity → 阻止非P0 LLM调用"
  - "FLE 每 60s 计算 burn rate → 判断是否超过阈值"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\feedback_loop\slo_manager.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\feedback_loop\error_budget.py
  3. 删除新增的测试文件

depends_on: []
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
