---
task_id: "TASK-KB-0025"
source_blueprint: "MOD-KB-001"
source_section: "§9.2 混合检索(语义+BM25) + §9.3 查询改写(HyDE+) + §9.4 动态上下文预算"

title: "混合检索+查询改写+动态上下文预算——HyDE query→BM25名义词汇过滤 + 预算控制线性规划"
description: |
  实现蓝图 §9.2/§9.3/§9.4 定义的进阶检索技术：(1)§9.2 混合检索——BM25Tokens() 稀疏检索 + 语义向量 384d→加权组合(语义70%权重:BM25 30%)——BM25Okapi 反问query→提取关键词→给定 0.01-0.99 TF-IDF 分数；(2)§9.3 查询改写——HyDE+(query)→"hypothetical answer段落" + Query2Doc 关键词→ hysent_to_tok_expand 人工判断介入 + Optical反馈信号自动优化评估；(3)§9.4 动态上下文预算——context_budget = fixed_system_prompt + (task_complexity × 400 + category_density × 600) + 大结果集Truncation_short——complexity 判断为 P0=4倍/P1=3倍/P2=2倍/P3=1倍。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\hybrid_search.py"
    description: "新建——BM25Tokens() + weighted_combine(semantic_70pct + bm25_30pct)→List[KeEntry]"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\query_rewriter.py"
    description: "新建——HyDE+(query)→hypothetical_answer + hysent_to_tok_expand + 人工介入"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\context_budget.py"
    description: "新建——calculate_dinamic_budget(task_card)→budgetTokens + truncation_strategy"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\hybrid_search.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\query_rewriter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\context_budget.py"
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
    reason: "§9.2 混合检索 + §9.3 查询改写 + §9.4 动态上下文预算"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "hybrid_search.py BM25Tokens query→提取idf weight→与semantic KE list按0.7:0.3权重合并"
  - "query_rewriter.py HyDE+(query)→返回(expanded:str, hysent_src:bool)——耗时<0.6s"
  - "context_budget = system_prompt + (0.4 × complexity_mult + 0.6 × cat_density) max=8500T↔24K chars"
  - "Truncation→统一策略 长文本→按优先级截断——P0保留2800+、P1保留2000+、P2保留1500+、P3保留500+"
  - "manual override 防误判——budget 结果展示给sup_session→可手动调节+20%/-20%"

rollback_instructions: |
  1. 删除 src/zephyr/kb/hybrid_search.py, query_rewriter.py, context_budget.py

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
