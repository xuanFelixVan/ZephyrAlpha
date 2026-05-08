---
task_id: "TASK-KB-0029"
source_blueprint: "MOD-KB-001"
source_section: "§9.12 三级记忆模型(Hot/Warm/Cold) + §9.13 检索自反思(Self-RAG) + §9.14 知识效果A/B测试"

title: "三级记忆分层实现(Hot/Warm/Cold Temperature Tiers) + Self-RAG检索自反思 + KE有效性A/B测试"
description: |
  实现蓝图 §9.12-§9.14 定义的记忆分层与检索质量验证：(1)§9.12 三级记忆模型(Hot/Warm/Cold)——Hot层：进程内存(dict) ≤20 KE <1ms，存放Track C + 当前session活跃KE + task_type相关Top-K；Warm层：SQLite定时refresh 全量ACTIVE KE metadata <10ms；Cold层：ChromaDB语义检索 全量KE body+embedding <200ms。Warm→Hot预热规则：S1加载Hot Cache(Track C 3 KE + 上次session活跃KE ≤5) → S2按task_type从Warm预取 → S3 session结束时引用≥3保留Hot、其余退回Warm、Track C永驻Hot。API增强：unified_memory_api.recall_with_tier(query, task_type, hot_cache, warm_cache, cold_fallback=True)——优先Hot→未命中Warm→未命中Cold回退；(2)§9.13 检索自反思(Self-RAG)——Self-Reflection Gate(Kimi K2.6)：逐条KE判定is_relevant YES/NO + relevance_reason，≥3条relevant→正常生成，<3条→触发§9.3 HyDE重试或标记answer_unsupported。退化检测(盲点#18)：被评估KE的extraction_generation≥3时追加判定→SEMANTICALLY_STABLE/SLIGHT_DRIFT(quality_score×0.90)/SIGNIFICANT_DRIFT(STATUS→NEEDS_REVIEW+推Owner复查原始session log)。反馈写入ke_usage_log.reflection_result；(3)§9.14 知识效果A/B测试——每周采样5个典型task(覆盖不同task_type)，Group A：注入全部Top-K KE，Group B：Top-K随机移除1条KE，Delta分析对比答案完整性+正确性+Token效率。Δ<0.05→标记low_effectiveness→DEPRECATED或删除；Δ>0.15→helpfulness_score+0.1。月度KE Effectiveness Report(Top 3/Bottom 3+建议动作)。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\three_tier_memory.py"
    description: "新建——Hot/Warm/Cold三层内存 + Warm→Hot预热规则 + recall_with_tier() API"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\self_rag.py"
    description: "新建——Self-Reflection Gate(Kimi K2.6逐条is_relevant判定) + 退化检测(extraction_generation≥3 → STABLE/SLIGHT_DRIFT/SIGNIFICANT_DRIFT)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ke_ab_test.py"
    description: "新建——每周5 task A/B Split → Delta分析(完整性/正确性/Token效率) → Δ<0.05降级/Δ>0.15提升 → 月度Effectiveness Report"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\three_tier_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\self_rag.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ke_ab_test.py"
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
    reason: "§9.12 三级记忆(Hot/Warm/Cold) + §9.13 Self-RAG + §9.14 A/B测试"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 35

acceptance_criteria:
  - "three_tier_memory.py——Hot≤20 KE(dict<1ms)/Warm metadata(SQLite<10ms)/Cold ChromaDB(<200ms)——recall_with_tier()优先Hot→Warm→Cold回退"
  - "three_tier_memory.py——Warm→Hot预热：S1 Track C+上次活跃KE → S2 task_type预取 → S3 session结束引用≥3保留/Track C永驻Hot"
  - "self_rag.py——Self-Reflection Gate：Kimi K2.6逐条KE判定is_relevant YES/NO ≥3条正常/<3条HyDE重试或answer_unsupported"
  - "self_rag.py——退化检测：extraction_generation≥3时追加判定→STABLE/SLIGHT_DRIFT(quality×0.90)/SIGNIFICANT_DRIFT(NEEDS_REVIEW+推Owner)"
  - "ke_ab_test.py——每周5 task A/B split→Delta分析(完整性/正确性/Token效率)→Δ<0.05→low_effectiveness降级/Δ>0.15→helpfulness_score+0.1"
  - "月度KE Effectiveness Report输出——Top 3/Bottom 3+建议动作"

rollback_instructions: |
  1. 删除 src/zephyr/kb/three_tier_memory.py, self_rag.py, ke_ab_test.py

depends_on: ["TASK-KB-0024"]
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
