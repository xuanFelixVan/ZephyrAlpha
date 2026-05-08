---
task_id: "TASK-MST-0026"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §二十八 全局降级级联预防——CT-DEGRADE-CASCADE-001 + §二十九 Owner 缺位自治——CT-AUTONOMY-001"

title: "实现全局降级级联预防 + Owner 缺位分级自治运行"
description: |
  实现 §二十八 CT-DEGRADE-CASCADE-001 + §二十九 CT-AUTONOMY-001。
  级联模型：(1)signal_propagation——VMS慢→CE慢→Orc假死的传播链；
  (2)degradation_weight: 每个系统 degraded=+1 weight → cumulative weight≥3→cascade_protection激活；
  (3)3级防护：weight=3暂停非P0/weight=4断开degraded系统/weight=5 Panic Mode；
  (4)Overload shedding: CE p99>8s→主动 429→Orc QUEUE 而非硬塞。
  Owner 缺位自治：(1)full_auto(6类action自动执行)——定时GC/Backup/KE自动入库/自动修复/model fallback；
  (2)supervised(24h无回复→自动执行)——OPS任务创建/非BREAKING变更/DLQ replay；
  (3)manual_only(Owner必须确认)——BREAKING Schema/Gate阈值/AI prompt/Panic Mode解除/成本预算调整。
  absence levels: 12h→通知/24h→supervised auto-exec/72h→task freeze/168h→紧急联系人。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\degrade_cascade.py"
    description: "级联预防管理器——CT-DEGRADE-CASCADE-001——degradation weight+3级防护+shedding"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\autonomy_manager.py"
    description: "自治管理器——CT-AUTONOMY-001——3级自治+absence detection+autonomy_log表"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_degrade_cascade.py"
    description: "级联预防单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_autonomy_manager.py"
    description: "自治管理器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\degrade_cascade.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\autonomy_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_degrade_cascade.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_autonomy_manager.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

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
    reason: "§二十八——CT-DEGRADE-CASCADE-001 + §二十九——CT-AUTONOMY-001 完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "degrade_cascade.py 追踪 signal_propagation 链(VMS→CE→Orc→Gates+FLE→Panic Mode)"
  - "cumulative weight≥3 → auto activate cascade_protection / weight≥4→断开degraded / weight≥5→Panic Mode"
  - "CE overload detection → HTTP 429 → Orc QUEUE(不丢任务) → 等待恢复 → auto retry"
  - "autonomy_manager.py 实现 3 级自治(full_auto/supervised/manual_only) 对应不同 action 类别"
  - "absence detection: 12h→飞书通知→24h→supervised auto_exec→72h→freeze→168h→紧急联系人"
  - "autonomy_log 表(autonomy_actions)不可篡改——timestamp/action/level/absent_hours/auto_executed/outcome"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\degrade_cascade.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\autonomy_manager.py
  3. 删除新增的测试文件
  4. 如有创建 autonomy_actions 表 → DROP TABLE autonomy_actions

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
