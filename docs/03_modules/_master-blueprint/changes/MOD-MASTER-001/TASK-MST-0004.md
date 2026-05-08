---
task_id: "TASK-MST-0004"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §二 集成契约注册表——13 条核心 CT-* 契约"

title: "实现 13 条核心跨系统集成契约的契约注册与运行时调用路由"
description: |
  实现 §二 定义的 13 条核心 CT-* 集成契约的注册表与调用路由：
  CT-ORC-SCRIPT-001(Task Blocking+Finding→Task创建)、CT-ORC-CE-001(Session Context请求)、
  CT-SCRIPT-KB-001(Finding→KE入库)、CT-FLE-ORC-001(异常检测→调度调整)、
  CT-CE-VMS-001(Context→Vector Search)、CT-PIPE-ORC-001(Task→Pipeline路由)、
  CT-SCRIPT-GATE-001(Script Exit Code→Gate决策)、CT-ORC-VMS-001(Task Output→Vector Memory)、
  CT-ORC-GATE-001(Task Lifecycle Gate)、CT-CE-LSG-001(Context Injection Safety)、
  CT-KB-VMS-001(KB→Vector)、CT-FLE-DB-001(FLE Metrics→DB)、CT-TELE-FLE-001(Telemetry→FLE)。
  每条契约包含：触发条件、输入Schema、输出Schema、telemetry RED/USE指标、ai_prompt。
  实现 ai_read_only_hint 字段强制检查：DO_NOT_CALL→拒绝、IMPL_REQUIRED→拒绝、CAUTION_STUB→warn、SAFE→允许。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"
    description: "契约注册表——13 条核心 CT-* 的注册、查询、ai_read_only_hint 检查"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_router.py"
    description: "契约路由——根据 CT-* 编号路由到对应的系统调用"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_contract_registry.py"
    description: "契约注册表单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_contract_router.py"
    description: "契约路由单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_router.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_contract_registry.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_contract_router.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

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
    reason: "§二——13条核心CT-*契约的完整YAML定义 + ai_read_only_hint字段"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    reason: "TaskCard/Finding/KE Schema——契约输入输出类型定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "contract_registry.py 注册全部 13 条核心 CT-* 契约（§二 §2.1-§2.13）"
  - "contract_router.py 根据 CT-* 编号路由调用到目标系统（Orc→CE, Orc→Gates, Script→KB 等）"
  - "ai_read_only_hint=DO_NOT_CALL 时拒绝调用并报告'契约不存在'"
  - "ai_read_only_hint=IMPL_REQUIRED 时拒绝调用并报告'需先完成实现'"
  - "ai_read_only_hint=CAUTION_STUB 时允许调用但 w a r n 消费者'仅部分功能可用'"
  - "每条契约包含 telemetry RED(rate/error/duration) 或 USE(utilization/saturation/error) 指标"
  - "Pydantic V2 BaseModel 实现——所有 Schema 类型检查通过"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\contract_registry.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\contract_router.py
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
