---
task_id: "TASK-MST-0008"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §七 Anti-Patterns——AP1~AP8 八条 AI 绝对禁止的集成行为"

title: "实现 Anti-Patterns(AP1~AP8)运行时防护——AI 集成行为框架"
description: |
  实现 §七 Anti-Patterns 定义的 8 条 AI 集成行为禁止规则的运行时强制执行：
  AP1(绕过集成契约)——未登记 CT-* 的跨系统调用→拒绝；AP2(静默吞异常)——degrade 路径必须记录 audit_log；
  AP3(忽略熔断器)——circuit_breaker OPEN时强制停止调用；AP4(文档代码不一致时以代码为准)——反 Tier 0；
  AP5(修改上游蓝图以修复不一致)——必须先创建 Finding；AP6(跨系统共享可变状态)——禁止非 CT-* 路径共享状态；
  AP7(忽略门禁裁决)——G0-G7 门禁 FAIL→阻止执行；AP8(跨 Session 遗留在途任务)——Session 结束前必须清理。
  每条 AP 实现为 Gate Engine 的独立 check 方法。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\gate_engine.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\anti_pattern_guard.py"
    description: "Anti-Patterns 防护引擎——AP1~AP8 运行时强制执行"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_anti_pattern_guard.py"
    description: "Anti-Patterns 防护单元测试——逐条验证 AP1~AP8"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\anti_pattern_guard.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_anti_pattern_guard.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\gate_engine.py"
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
    reason: "§七——AP1~AP8 完整定义 + 每条 AP 的违反示例"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "anti_pattern_guard.py 实现 AP1~AP8 全部 8 条运行时检查方法"
  - "AP1: 未登记 CT-* 的跨系统调用→记录 audit_log + 返回 CALL_REJECTED"
  - "AP2: 异常静默吞没→自动记录 audit_log（即使 degrade 路径执行）"
  - "AP3: circuit_breaker OPEN→强制停止+通知消费者"
  - "AP4: 文档代码不一致时→返回 Tier 0 为准而非代码为准"
  - "AP5: 修改上游蓝图→自动创建 DOC_INCONSISTENCY Finding"
  - "AP6: 跨系统共享可变状态→检测到非 CT-* 路径→拒绝"
  - "AP7: G0-G7 门禁 FAIL→阻止 TaskCard 状态推进"
  - "AP8: Session 结束仍有 IN_PROGRESS→自动 PAUSED + Handoff Manifest 更新"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\gates\anti_pattern_guard.py
  2. 删除 D:\ZephyrAlpha\tests\unit\test_anti_pattern_guard.py

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
