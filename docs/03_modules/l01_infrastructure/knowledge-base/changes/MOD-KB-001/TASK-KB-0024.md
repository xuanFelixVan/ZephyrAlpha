---
task_id: "TASK-KB-0024"
source_blueprint: "MOD-KB-001"
source_section: "§9.1 检索质量度量体系 + §9.1.1 KE_vs_reality 外部真值对照检查"

title: "RAG 质量度量评估体系实现——4项RAGAS指标 + KE_vs_reality 外部真值自验证"
description: |
  实现蓝图 §9.1 定义的检索质量度量体系：(1)4项RAGAS指标自动计算（对标 §9.1 四维质量指标表）——Context Precision(正确定位比例 > 0.75)、Context Recall(遗漏率 < 0.30即Recall>0.70)、Faithfulness(无虚构 > 0.90)、Answer Relevance(回答溯源率 > 0.80)；(2)biweekly 自动评估脚本 assess_kb_quality()→SQLite kb_quality_history 表 → 趋势 (plot→保存到 docs/metrics/kb_quality_history.png)；(3)告警——Precision<0.50→EMAIL + start_sessions_engaged_LEAN_CASH_COW→10会话内0/10均<0.70→KB全面改造决策；(4)§9.1.1 KE_vs_reality——KE内容 vs pyproject.toml/justfile 中的实际依赖——MISMATCH→标记 fresh_ke_revision→推送 (a)更新KE (b)该KE已过时→rerank priority 降低 KE ×0.5权重。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\rag_evaluator.py"
    description: "新建——4项RAGAS指标(CP/CR/FF/AR) + plot_quality_trends() + generate_improvement_plan()——对标 §9.1 四维表"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ke_vs_reality.py"
    description: "新建——KE内容 vs pyproject.toml/justfile→verdict(M/MATCH)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
    description: "追加 kb_quality_history 表 schema"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\rag_evaluator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ke_vs_reality.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§9.1 4项RAGAS指标+biweekly评估 + §9.1.1 KE_vs_reality"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "rag_evaluator.py 计算出4项指标——CP(>0.75)/CR(>0.70)/FF(>0.90)/AR(>0.80)——各有 formula 实现——对应 §9.1 四维表目标值"
  - "kb_quality_history 表插入记录——每次评估自动追加"
  - "Precision<0.50→推 Email + sessions monitor"
  - "ke_vs_reality.py self_verification_baseline(n_recent_ke=10)→对比 pyproject.toml→MISMATCH→推送 Owner"
  - "KE_vs_reality 的重排 priority ×0.5 降权实现正确"

rollback_instructions: |
  1. 删除 src/zephyr/kb/rag_evaluator.py, ke_vs_reality.py
  2. git checkout -- src/zephyr/kb/kb_repo.py（如修改了kb_quality_history）
  3. 若 kb_quality_history 表已建→DROP TABLE IF EXISTS kb_quality_history

depends_on: ["TASK-KB-0012"]
blocked_by: []
status: "created"
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
