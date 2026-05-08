---
task_id: "TASK-MST-0014"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §十五 CBAC 能力访问控制矩阵——CT-CBAC-001"

title: "实现 CBAC 能力访问控制矩阵(CT-CBAC-001)——12×12 系统授权声明"
description: |
  实现 §十五 定义的 CBAC(Capability-Based Access Control)能力矩阵：
  12 系统×12 系统的完整授权关系——18 条精确的 capability 声明。
  核心：(1)每个系统仅拥有执行其 CT-* 合同所需的 capabilities（最小权限原则）；
  (2)启动时计算 capability_matrix 的 checksum → 运行时每次 capability_check() 校验 checksum；
  (3)checksum 不一致 → ALERT + 拒绝调用（防运行时篡改）；
  (4)离线更新流程(Offline Update T)——Owner 修改 YAML → 重新计算 checksum → CI 校验 → 重启后生效；
  (5)违规响应：LOG + ALERT + DENY → 写入 audit_log；
  (6)Orc 特权声明——Orc 可以编排但不能直接调用 LSG/Script System/修改 Gate 阈值。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\cbac_matrix.py"
    description: "CBAC 能力矩阵——12×12 授权声明 + checksum 防篡改"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\capability_checker.py"
    description: "能力检查器——runtime capability_check() + checksum 校验"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_cbac_matrix.py"
    description: "CBAC 矩阵单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_capability_checker.py"
    description: "能力检查器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\cbac_matrix.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\capability_checker.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_cbac_matrix.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_capability_checker.py"

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
    reason: "§十五——CT-CBAC-001 完整定义——18条capability声明 + checksum + Orc特权声明"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "cbac_matrix.py 注册 18 条精确的 capability 声明（caller→target→actions→auth）"
  - "capability_checker.py 每次调用前校验 caller 是否有对应 action 的 auth token"
  - "启动时计算 checksum → runtime capability_check() 校验 checksum → 不一致=ALERT+拒绝"
  - "未授权访问 → LOG(CRITICAL) + ALERT + DENY → 写入 audit_log 表"
  - "Orc 不能直连 LSG(via CE only)/Script System(via Gates only)/修改 Gate 阈值(FLE only)"
  - "Offline Update T: Owner 修改 YAML → checksum → CI verify → merge → 重启生效"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\gates\cbac_matrix.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\gates\capability_checker.py
  3. 删除新增的测试文件

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
