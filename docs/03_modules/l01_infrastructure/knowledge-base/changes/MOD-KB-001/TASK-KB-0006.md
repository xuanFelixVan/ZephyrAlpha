---
task_id: "TASK-KB-0006"
source_blueprint: "MOD-KB-001"
source_section: "§3.7 KE 运行时反馈字段 + §3.2 动态 quality_score 公式"

title: "KE 运行时反馈字段实现——usage_count/adoption_count/helpfulness_score/last_used_at 字段落地 + learn() 五种事件类型扩展 + 动态 quality_score 公式"
description: |
  实现蓝图 §3.7 定义的运行时反馈字段与动态学习机制：(1)四个反馈字段——usage_count/adoption_count/helpfulness_score/last_used_at 写入 SQLite schema——KE 每次被检索/采纳时自动递增或刷新；(2)学习事件系统——`learn()` 扩展——新增 5 种 event_type 枚举：ke_retrieved(KE被检索出库→usage_count++/last_used_at UPDATE)/ke_adopted(AI实际采纳了KE→adoption_count++/helpfulness_score+0.05)/ke_ignored(AI未引用→helpfulness_score-0.03)/task_outcome(任务成功后溯源贡献→helpfulness_score+0.15)/ke_contradiction(新KE与已有冲突→quality_score*0.70+触发§9.17裁决)——对接到 RI-02 unified_memory_api.record_event(event_type, ke_id, outcome={success,failure,partial})；(3)动态 quality_score——实现动态质量分公式：quality_score = quality_score_static*0.4 + adoption_rate*0.3 + helpfulness_score*0.2 + freshness*0.1 其中 freshness 为§3.5半衰期模型衰减值(0-1)，当 quality_score<0.3 自动流转向 DEPRECATED 提议。usage_count/log 记入 ke_usage_log 保证 0 Owner 操作。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
    description: "扩展 learn()——五种事件类型 ke_adoption/ke_helpfulness/ke_deprecation/ke_contradiction/ke_merge + 动态 quality_score 公式"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\feedback_collector.py"
    description: "新建——门禁阻断/验证失败/幻觉事件自动收集器"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
    description: "追加 knowledge_entries 表四字段 migration + 动态 quality_score 计算"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\feedback_collector.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\**\\*.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "新建 .py 路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§3.7 运行时反馈字段+五种事件类型(ke_retrieved/ke_adopted/ke_ignored/task_outcome/ke_contradiction)+动态quality_score公式"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 50

acceptance_criteria:
  - "SQLite knowledge_entries 表新增 usage_count/adoption_count/helpfulness_score/last_used_at 四列"
  - "learn() event_type 枚举支持 ke_retrieved(usage_count++)/ke_adopted(adoption_count++/+0.05)/ke_ignored(-0.03)/task_outcome(+0.15)/ke_contradiction(×0.70)"
  - "动态 quality_score = quality_score_static*0.4 + adoption_rate*0.3 + helpfulness_score*0.2 + freshness*0.1——quality_score<0.3→DEPRECATED"
  - "feedback_collector.py 能够从 pre-commit stderr 自动提取失败模式并生成 FeedbackEvent"
  - "mypy 类型检查通过"
  - "tests/unit/test_unified_memory_api.py 新增 learn() 五种事件类型测试"

rollback_instructions: |
  1. git checkout -- src/zephyr/kb/unified_memory_api.py
  2. git checkout -- src/zephyr/kb/kb_repo.py
  3. 删除 src/zephyr/kb/feedback_collector.py
  4. SQLite: ALTER TABLE knowledge_entries DROP COLUMN IF EXISTS（若 schema migration 已执行需手动回退）

depends_on: ["TASK-KB-0003", "TASK-KB-0004"]
blocked_by: []
status: "done"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
