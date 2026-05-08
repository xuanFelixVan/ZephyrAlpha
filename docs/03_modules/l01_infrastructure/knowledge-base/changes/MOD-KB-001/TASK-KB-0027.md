---
task_id: "TASK-KB-0027"
source_blueprint: "MOD-KB-001"
source_section: "§9.9 基于聚类去重 + §9.10 Token预算与节流阀"

title: "聚类去重引擎 + Token月度预算与优先级队列降级——HDBSCAN聚类→Kimi K2.6摘要→Owner审批 + ¥5/月硬预算+P0-P3降级"
description: |
  实现蓝图 §9.9-§9.10 定义的去重与节流机制：(1)§9.9 聚类去重——每30天APScheduler cron自动触发：S1从ChromaDB批量读出所有ACTIVE KE embedding构建(N×768d)矩阵 → S2 UMAP降维768d→50d + HDBSCAN(min_cluster_size=2,min_samples=1)聚类 → S3每个cluster中≥3条KE→Kimi K2.6生成cluster summary(列出每条KE的subtopic+建议合并为parent+child结构)→推送Owner审批(merge/keep/supersede三选一)→执行merge保留高质量KE + report(before/after counts+coverage)；(2)§9.10 Token月度预算与优先级队列降级——月度预算¥5.00(以Kimi K2.6计价约¥1.20/百万token，月均~327,500 token≈¥0.40) + 超80%(¥4.00)时WARN日志+降级策略：P0永不降级(轨道1 Session提取+轨道2 CI阻断) / P1 80%时降级(轨道5周巡检+Multi-Query+HyDE) / P2 >100%时降级(四模型审计→仅V-12快速通道) / P3 >120%时降级(轨道4外部注入→暂停)；LLM API 429 Rate Limit时同样触发优先级队列降级；KE级成本归因Phase 5预留(ke_maintenance_cost_ytd)。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\cluster_dedup.py"
    description: "新建——HDBSCAN+UMAP聚类→Kimi K2.6 cluster summary→Owner审批(merge/keep/supersede)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\token_budget.py"
    description: "新建——月度¥5.00硬预算+80%降级策略(P0-P3)+429背压+ke_maintenance_cost_ytd Phase5预留"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\cluster_dedup.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\token_budget.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§9.9 聚类去重 + §9.10 Token预算节流"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "cluster_dedup.py——每30天cron触发：S1 ChromaDB→(N×768d)矩阵 → S2 UMAP 768→50d + HDBSCAN(min_cluster_size=2,min_samples=1) → S3 cluster≥3 KE→Kimi K2.6 summary→Owner审批"
  - "merge/keep/supersede 三选一——选择后执行merge保留高质量KE + report(before/after counts)"
  - "token_budget.py——月度¥5.00硬预算 + 超80%→P1降级(周巡检+Multi-Query+HyDE关闭) + >100%→P2降级(审计→V-12快速通道) + >120%→P3降级(外部注入暂停)"
  - "P0永不降级(轨道1+轨道2) + LLM API 429同样触发优先级队列降级"
  - "ke_maintenance_cost_ytd Phase5预留字段"

rollback_instructions: |
  1. 删除 src/zephyr/kb/cluster_dedup.py, token_budget.py

depends_on: ["TASK-KB-0021"]
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
