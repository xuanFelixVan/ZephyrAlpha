---
task_id: "TASK-MST-0009"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §八 施工指南 + §九 设计决策集中表 DD-1~DD-14"

title: "实现设计决策表(DD-1~DD-14)与施工指南——14条架构决策 + mock策略 + 替代方案追踪"
description: |
  实现 §九 设计决策集中表的 14 条关键设计决策及 §八 施工指南。
  每条 DD 包含：决策内容、替代方案、选择理由、重评条件(re-evaluate when)、影响范围。
  施工指南：(1) Phase A→D 每个 CT-* 的 mock 实现策略（stub/partial/full）；
  (2) 禁止在未完成 Phase 0 context check 的情况下进入后续 Phase；
  (3) Mock 模式：开发环境使用 cheap_fast 模型、低 token 预算、跳过飞书通知。
  设计决策包括：
  DD1(总蓝图只定义"之间"不管"内部")、DD2(YAML结构化契约)、DD3(fail-closed优先于availability)、
  DD4(circuit_breaker每条CT-*独立配置)、DD5(FLE无异常也记录)、DD6(KE更新→新embedding非覆写)、
  DD7(故障传播方向内→外)、DD8(M1-M11双zone不交叉)、DD9(三态HealthCheck)、
  DD10(DLQ用SQLite)、DD11(CDC用本地SQLite简化版)、DD12(Telemetry push)、
  DD13(stub/mock必须在契约文件内定义——蓝图标注为 DD9 重复)、
  DD14(契约编号CT-{A}-{B}固定——蓝图标注为 DD10 重复)。
  注：蓝图 §九 声明"当前10条关键架构决策"但实际列出14行，DD9和DD10编号出现两次（蓝图自身编号不一致）。
  本任务卡以14条决策为准。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\design_decisions.py"
    description: "设计决策注册表——DD-1~DD-14 决策记录 + 重评条件检查"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\construction_guide.py"
    description: "施工指南引擎——CT-* mock 策略 + Phase 0 context check 强制执行"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_design_decisions.py"
    description: "设计决策注册表单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\design_decisions.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\construction_guide.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_design_decisions.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-MST-NNNN"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§八施工指南 + §九设计决策DD-1~DD-14完整定义（含DD9/DD10重复编号）"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "design_decisions.py 注册全部 14 条设计决策(DD-1~DD-14)，每条含替代方案+重评条件"
  - "construction_guide.py 实现 CT-* mock 三级策略(stub/partial/full)"
  - "每次施工前强制运行 Phase 0 context check（phase_e_context_check.py）"
  - "代码更改违反 DD 决策→CI WARN + 要求要么遵守 DD 要么更新 DD 表"
  - "DD13(stub/mock在契约文件内定义——DD9重复) + DD14(CT-*编号固定——DD10重复) 正确注册"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\design_decisions.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\construction_guide.py
  3. 删除新增的测试文件

depends_on: ["TASK-MST-0007"]
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
