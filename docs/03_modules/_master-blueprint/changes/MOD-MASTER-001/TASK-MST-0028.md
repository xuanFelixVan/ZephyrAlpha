---
task_id: "TASK-MST-0028"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §三十一 Prompt 版本控制——CT-PROMPT-VERSION-001 + §三十二 Session 冲突预防——CT-SESSION-CONFLICT-001"

title: "实现 AI Prompt 版本控制 + Session 冲突预防契约"
description: |
  实现 §三十一 CT-PROMPT-VERSION-001 的 Prompt 可审计版本追踪 +
  §三十二 CT-SESSION-CONFLICT-001 的多 AI Session 冲突预防。
  Prompt 版本控制：(1)所有 CT-* ai_prompt 字段纳入 .prompts/{CT_ID}_v{hash8}.yaml + version_history 表；
  (2)谁改的(who)、什么时候(when)、diff是什么、改了哪个 CT-*、原因+预期→审计链条完整；
  (3)prompt_regression 检测：AI Quality、G0-G7 门禁通过率 → shift>20%→反常 → 检查+rollback。
  Session 冲突预防：(1)Session 启动→评估已在途哪些→硬冲突(目标文件重叠)→QUEUE排队；
  (2)软冲突(工作重叠)→通知双方→异步进行→合并请求协调→"last writer" d i f f merge→reconcile；
  (3)文件锁文件定向——按被触及文件列表评估——乘客Session←检出→.ailocks→自生成 soft_conflict_detect.py；
  (4)1小时WATCHDOG_FILE超时→Deadman检测override。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\orchestrator\prompt_version.py"
    description: "Prompt版本控制器——CT-PROMPT-VERSION-001——prompts/*.yaml+version_history+prompt_regression"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\session_conflict.py"
    description: "Session冲突预防器——CT-SESSION-CONFLICT-001——hard/soft_conflict+soft_conflict_detect.py"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\soft_conflict_detect.py"
    description: "软冲突检测脚本——分析重叠文件→生成评估报告"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_prompt_versioner.py"
    description: "Prompt版本器单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_session_conflict.py"
    description: "Session冲突预防单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\prompt_versioner.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\session_conflict.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\soft_conflict_detect.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_prompt_versioner.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_session_conflict.py"

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
    reason: "§三十一——CT-PROMPT-VERSION-001 + §三十二——CT-SESSION-CONFLICT-001 完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "prompt_versioner.py 实现 .prompts/{CT_ID}_v{hash8}.yaml + version_history 表(who/when/diff/CT-ID/reason)"
  - "prompt_regression 检测: AI Quality/G0-G7 pass→shift>20%→check+ rollback prompt"
  - "session_conflict.py 硬冲突检测→目标文件重叠→延迟队列→QUEUE+ Owner choose priority"
  - "软冲突→通知双方→ auto_create soft_conflict_detect.py→评估→reconcile"
  - "1h WATCHDOG_FILE timeout→ Deadman override"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除新增的 3 个源码/脚本文件
  2. 删除新增的测试文件
  3. 如有创建 prompt version_history 表 → DROP TABLE prompt_version_history

depends_on: ["TASK-MST-0017"]
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
