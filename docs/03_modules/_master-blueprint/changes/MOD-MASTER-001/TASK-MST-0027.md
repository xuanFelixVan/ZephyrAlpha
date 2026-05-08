---
task_id: "TASK-MST-0027"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §三十 AI Agent 质量循环——CT-AGENT-QUALITY-001"

title: "实现 AI Agent 质量反馈闭环——自省缺陷库 + multi_attempt + model_decision_audit"
description: |
  实现 §三十 CT-AGENT-QUALITY-001 的 AI Agent 质量反馈闭环：
  (1)缺陷库(defect library)自动从 L3 snoop 提取防御规则——FLE→Orc→自动创建 Finding→生成 TaskCard 添加防御规则；
  (2)Quality scoring——每任务×3维度(correctness_score 1-10+gates_pass_ratio+drift_distance)→存档 self_audit.json；
  (3)multi_attempt 重新生成——AI Quality score<6→自动附 prev_attempt+缺陷库规则→重新执行(max 2次)；
  (4)model_decision_audit——记录每步 AI 决策的 CT-* 调用路径+模型名+能力声明+结果→awareness_breadcrumbs 表；
  (5)Quality reports——daily quality summary(30d avg/trend/缺陷库新增) + weekly anomaly report；
  (6)缺陷库防止重复认识缺陷——"上次修复忘记X→但在 self_audit.json 学懂了→但仍重复犯错"=蓄意bug→引入 multi_attempt。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\ai_quality_loop.py"
    description: "AI质量闭环——CT-AGENT-QUALITY-001——缺陷库+multi_attempt+model_decision_audit+daily report"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\awareness_breadcrumbs.py"
    description: "awareness_breadcrumbs 表管理——每次LLM调用的决策raft记录"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\quality_scorer.py"
    description: "质量打分器——correctness_score+gates_pass_ratio+drift_distance→self_audit.json"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_ai_quality_loop.py"
    description: "AI质量闭环单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\ai_quality_loop.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\awareness_breadcrumbs.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\quality_scorer.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_ai_quality_loop.py"

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
    reason: "§三十——CT-AGENT-QUALITY-001 完整定义——缺陷库+multi_attempt+model_decision_audit+daily report"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "ai_quality_loop.py 实现 FLE→Orc 自动创建 Finding 并通过缺陷库提取防御规则"
  - "quality_scorer.py 3 维度评分 correctness_score(1-10)+gates_pass_ratio+drift_distance → <6 触发 multi_attempt"
  - "multi_attempt: 附 prev_attempt + 缺陷库规则 → max 2 attempts → 全失败→Orc human review"
  - "model_decision_audit: 记录每步 CT-* 调用路径+模型名+能力声明+结果+tokens_cost → awareness_breadcrumbs 表"
  - "daily_quality_summary: 过去30天 avg correctness_score/trend/FLE_created/缺陷库新增"
  - "weekly anomaly report: 质量突然下降的系统/task_type + 模型 list_diff causes"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除新增的 3 个源码文件
  2. 删除新增的测试文件
  3. 如有创建 awareness_breadcrumbs 表 → DROP TABLE awareness_breadcrumbs
  4. 如有 self_audit.json → 删除

depends_on: []
blocked_by: []

status: "created"

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
