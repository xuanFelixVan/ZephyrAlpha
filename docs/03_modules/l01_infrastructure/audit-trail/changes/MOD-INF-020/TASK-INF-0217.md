---
task_id: "TASK-INF-0217"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §6.4 Git 隔离（决策 D-020-27）"

title: "实现审计日志 Git 隔离——data/audit/ 加入 .gitignore + 独立备份策略文档"
description: |
  实现审计日志的 Git 隔离：
  1. 更新 .gitignore——添加 data/audit/ 目录
  2. 从 git tracking 中移除已跟踪的 data/audit/ 文件——git rm --cached
  3. 创建 data/audit/ 目录结构：hot/ warm/ cold/ merkle/
  4. 实现 data/audit/.gitkeep 占位——各子目录保留
  5. 独立备份策略声明：每日 rsync → backup disk / 每周 snapshot
  6. Phase 1 迁移——现有 data/audit/audit-trail.jsonl 从 git 工作区移除
  落地决策 D-020-27。覆盖风险 R21。覆盖盲点 B22。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\.gitignore"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\.gitignore"
    description: "追加 data/audit/ 条目"
  - path: "D:\\ZephyrAlpha\\data\\audit\\hot\\.gitkeep"
    description: "热存储占位"
  - path: "D:\\ZephyrAlpha\\data\\audit\\warm\\.gitkeep"
    description: "温存储占位"
  - path: "D:\\ZephyrAlpha\\data\\audit\\cold\\.gitkeep"
    description: "冷存储占位"
  - path: "D:\\ZephyrAlpha\\data\\audit\\merkle\\.gitkeep"
    description: "Merkle 根存储占位"

allowed_touch:
  - "D:\\ZephyrAlpha\\.gitignore"
  - "D:\\ZephyrAlpha\\data\\audit\\**\\.gitkeep"
forbidden_touch:
  - "D:\\ZephyrAlpha\\data\\audit\\**\\*.jsonl"
  - "D:\\ZephyrAlpha\\data\\audit\\**\\*.db"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "data/ 目录合规"
  - module_id: "GOV-CMP-002"
    section: "AUD-004"
    reason: "审计日志存储隔离规则"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§6.4——Git 隔离设计 + D-020-27 决策"
  - file_path: "D:\\ZephyrAlpha\\.gitignore"
    reason: "需追加 data/audit/ 条目"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 2000
timeout_minutes: 10

acceptance_criteria:
  - ".gitignore 含 data/audit/ 行"
  - "data/audit/hot/ warm/ cold/ merkle/ 目录存在——各含 .gitkeep"
  - "git status 显示 data/audit/ 不会出现在 untracked 中"
  - "从 git index 中移除已跟踪的 audit JSONL 文件（git rm --cached）"

rollback_instructions: |
  1. 从 .gitignore 中移除 data/audit/ 行
  2. git add data/audit/ 重新纳入追踪
  3. 从 .gitkeep 文件中移除因回滚产生的变更

depends_on: []
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
