---
task_id: "TASK-KB-0012"
source_blueprint: "MOD-KB-001"
source_section: "§5.7 检索与注入流程 + §5.9 两阶段检索与重排序(含 §7.4 Reranker选型)"

title: "两阶段检索实现——recall() 升级 + reranker.py Cross-Encoder 重排序层 + 检索约束落地"
description: |
  将 unified_memory_api.recall() 从单阶段纯向量检索升级为两阶段检索：(1)实验阶段粗筛——ChromaDB 向量语义检索→Top 50 + 标签过滤(SQLite)；(2)Beta阶段精排——reranker.py 实现 BGE-reranker-v2-m3 Cross-Encoder 逐对打分(query, each KE)→Top 10 + 新鲜度排序；(3)检索约束落地——Top-K≤10 + 总注入token≤2000 + 新鲜度<50%标注`⚠️ 此知识已超过半衰期` + 仅注入status≥INDEXED 的KE；(4)BGE-reranker-v2-m3 选型落地——~200MB模型+sentence-transformers依赖+~4ms/pair×50≈200ms延迟；(5)降级策略——模型下载失败→纯ChromaDB Top-10（当前行为）+重排>1s→跳过重排。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\config\\embedding_model_registry.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\reranker.py"
    description: "新建——CrossEncoder 包装层：load_model() + rerank(query,ke_list)→top_k"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
    description: "升级 recall()——两阶段：粗筛(Top-50)+精排(reranker.py)→Top-10"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_reranker.py"
    description: "新增——reranker 单元测试：mock model→验证 Top-K 排序+降级逻辑"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\reranker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_reranker.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "RerankResult Pydantic V2 模型"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "新建文件路径合规"
  - module_id: "PS-STD-001"
    section: "§6.12"
    reason: "新 .py 注册到 script_manifest.yaml"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§5.9 完整定义两阶段检索 + §7.4 Reranker选型 + §5.7 检索约束"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "reranker.py 实现 CrossEncoder 包装——__init__(model_name)→.rerank(query,doc_list)→List[(doc,score)]"
  - "recall() 升级为两阶段——粗筛(ChromaDB vector)→reranker.rerank()→Top-10"
  - "若 sentence-transformers 不可用→降级为纯 ChromaDB Top-10 + WARN 日志"
  - "重排延迟>1s→跳过重排+WARN日志"
  - "Top-K≤10 硬约束——即使输入 max_results>10 也被截断"
  - "注入前过滤 status<INDEXED 的 KE"
  - "新鲜度<50% 的 KE 附带过时警告标注"

rollback_instructions: |
  1. 删除 src/zephyr/kb/reranker.py
  2. 删除 tests/unit/test_reranker.py
  3. git checkout -- src/zephyr/kb/unified_memory_api.py
  4. 运行 pytest tests/unit/test_unified_memory_api.py 确认恢复

depends_on: ["TASK-KB-0011"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
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
