---
task_id: "TASK-INF-0131"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §18 Blueprint Quality Self-Assessment + §15 第七轮审计"

title: "§18 蓝图质量自评维护——QualityScore Dashboard + 审计终局验收"
description: |
  按蓝图 §18 的 Blueprint Quality Self-Assessment + §15 的第七轮审计结论进行质量维护。
  蓝图自评 8 维度每项 ≥7/10 为 Pass。
  八个维度：分层合理性(Category)、结构完整性(BlueprintStructure)、深度(Depth)、
  核心经验(Core XP)、盲点防护(Blindspot Prevention)、决策用例(Decision Case)、
  施工可追踪性(Construction Traceability)、AI受众(AI Audience)。
  实现要求：
  1. 每次蓝图变更后刷新 §18 的自评分数。
  2. §15 的审计结论（审计终局 555.0h 投入）更新至最新状态。
  3. 分数保持 ≥7/10——任一维度跌破 7 必须开 ISSUE 补充。
  4. 自评数据源——来自 contract_auto_tester + anti_pattern_guard + policy_drift_detector。
  5. §15.2 审计终局信息——2026-03-31 之后无新增盲点。
  专业对标：Google SRE Workbook Service Scorecard + ZephyrAlpha Audit Governance。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contract_auto_maintainer.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\anti_pattern_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\blueprint_quality_score.py"
    description: "blueprint_quality_score——8 维度自评自动化 + QualityDashboard"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    description: "§18 自评分数更新——基于最新变更状态"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\blueprint_quality_score.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§6.12"
    reason: "AI受众优先——QualityScore Dashboard 输出格式优先让AI零歧义消费"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §18——自评 8 维度定义与 §15 审计终局"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 8000
timeout_minutes: 20

acceptance_criteria:
  - "blueprint_quality_score.py: score_blueprint(blueprint_path) → 8 维度 ScoreCard JSON"
  - "每个维度 0-10 分——基于客观数据源（文件数/文件行/盲点数/契约数/AD 数）"
  - "§18 分数更新——最低维度 ≥7/10（Category 最高 9/10）"
  - "§15.2 审计终局时间更新——2026-03-31 → 2026-05-06"
  - "QualityDashboard 输出 pub/sub JSON（AI Consumption 友好）"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\blueprint_quality_score.py
  2. git checkout -- docs/03_modules/_cross_layer/shared-core/blueprint.md

depends_on: ["TASK-INF-0126", "TASK-INF-0130"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
