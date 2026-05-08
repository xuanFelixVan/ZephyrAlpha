---
task_id: "TASK-INF-0203"
source_blueprint: "MOD-INF-011"
source_section: "§2.1 Collection 设计原则"

title: "Collection 设计原则强制执行器——五条铁律落地"
description: |
  实现蓝图 §2.1 定义的五条 Collection 设计原则的运行时强制执行机制：
  1. 按访问模式分不按数据来源分——高频热数据(rules/decisions)与低频冷数据(blueprints/execution_traces)分离索引
  2. 嵌入维度按精度需求分配——1024d 用于精确语义匹配(decisions/lessons/knowledge/rules/code_context)，512d 用于量大体(blueprints/session_snapshots/execution_traces)
  3. 分块策略 Collection 级差异化——代码用 AST-aware，文档用 heading-aware/section-aware，日志用 time-window，不可混用
  4. TTL 强制——execution_traces 30d / code_context 90d / session_snapshots 90d 自动清理
  5. Provenance 每条必带——继承 unified_memory_api 的 WriteTrace（origin/audit_chain/arbitration 三位一体）
  在 CollectionManager 的 create_collection() 和写入操作中硬编码这些原则的校验逻辑。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
    description: "追加 design_principles_enforcer——在 create_collection() 和 add() 方法中嵌入五条设计原则校验"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

applicable_rules:
  - module_id: "ADR-0016"
    section: "§3"
    reason: "BGE-M3 嵌入维度契约——1024d 路径 Collection 不可降维为 512d"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——设计原则校验错误类型使用 BaseModel"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§2.1 五条设计原则完整定义——维度分配/分块策略/访问模式/TTL/Provenance 强制真源"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\collection_manager.py"
    reason: "CollectionManager 当前实现——在其上追加设计原则校验层"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
    reason: "WriteTrace 三字段(origin/audit_chain/arbitration)——ProvenanceEnforcer 校验依据"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 7000
timeout_minutes: 30

acceptance_criteria:
  - "create_collection('foo', dim=256) → 抛出 DesignPrincipleError——维度不在 {512, 1024} 白名单中"
  - "create_collection('foo', dim=512, chunk_strategy='ast_aware') 但不在 documents 类 Collection → 警告日志（不阻止）"
  - "向 rules Collection 写入数据时不带 WriteTrace provenance → 拒绝写入 + 抛出 ProvenanceMissingError"
  - "向 execution_traces Collection 写入数据时 TTL 不是 30d → 拒绝创建或告警"
  - "向 code_context Collection 传入 token-level chunker 而非 AST-aware → 警告日志"
  - "hot_separation 校验：不允许在 execution_traces 上使用 heading-aware chunker"
  - "所有校验错误类型继承自 VMSError 基类"

rollback_instructions: |
  1. 如果校验逻辑过于严格导致无法创建任何 Collection → 将 strict_mode 参数设为 False（临时降级）
  2. 还原 D:\ZephyrAlpha\src\zephyr\vector_memory\collection_manager.py 至 TASK-INF-0202 完成后的版本
  3. 逐条禁用有问题的设计原则校验规则（通过 feature flag 控制）

depends_on:
  - "TASK-INF-0202"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "governance"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-011"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
