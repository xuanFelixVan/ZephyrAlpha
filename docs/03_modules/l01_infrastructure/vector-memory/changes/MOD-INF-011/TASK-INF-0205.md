---
task_id: "TASK-INF-0205"
source_blueprint: "MOD-INF-011"
source_section: "§3.1 双嵌入维度路由策略"

title: "双嵌入维度路由策略实现——EmbeddingRouter 降级链 + ONNX 预热 + 模型健康自检"
description: |
  实现蓝图 §3.1 定义的双嵌入维度路由策略的完整运行时逻辑：
  1. 路由决策：collection ∈ {decisions, lessons, knowledge, rules, code_context} → BGE-M3 1024d / collection ∈ {blueprints, session_snapshots, execution_traces} → bge-small-zh-v1.5 512d
  2. 路由依据：从 Collection 元数据的 embedding_model 字段读取（非硬编码路由表）
  3. ONNX 冷启动预热（V-VMS-507）：启动时用 "hello world" 做 warm-up inference，区分首次推理（200-500ms）与后续推理（<50ms）的超时阈值
  4. 降级策略：BGE-M3 加载失败 → 全局降级为 bge-small 512d；bge-small 也失败 → InMemory backend（零向量 placeholder——标记 degraded=True）
  5. 模型健康自检（V-VMS-428）：启动时用已知文本 embed → 验证输出维度正确 + 范数 > 0 + 无 NaN/Inf
  6. 向量 L2 归一化（V-VMS-506）：所有 VMS 外部消费端统一读取后归一化——cosine 需 L2 归一化向量
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
    description: "追加降级链逻辑——_try_bge_m3() → _try_bge_small() → _in_memory_fallback() + warm_up() + health_check() + l2_normalize()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_memory_memory_backend.py"
    description: "InMemoryMemoryBackend 降级兜底类——零向量 placeholder + degraded=True 标记"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_memory_memory_backend.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"

applicable_rules:
  - module_id: "ADR-0016"
    section: "§3"
    reason: "BGE-M3 ONNX 嵌入输出规范——1024d 向量 shape 断言"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——DegradationEvent 模型"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§3.1 双嵌入维度路由策略完整定义——路由表 + 降级策略 + InMemory backend"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
    reason: "当前 EmbeddingRouter 实现——在其上追加降级链 + 预热 + 健康自检"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "EmbeddingRouter.embed('test', 'rules') 路由到 BGE-M3 → 返回 1024d 向量"
  - "EmbeddingRouter.embed('test', 'blueprints') 路由到 bge-small → 返回 512d 向量"
  - "BGE-M3 模型文件不存在时 → 自动降级到 bge-small 512d + 日志记录降级事件"
  - "BGE-M3 和 bge-small 均不可用时 → InMemory backend 返回全零向量 + degraded=True 标记"
  - "warm_up() 在首次查询前完成——消除 ONNX 首次推理 200-500ms 冷启动延迟"
  - "health_check() 验证：输出维度正确 + L2 范数 > 0 + 无 NaN/Inf + 模型文件 SHA256 校验"
  - "l2_normalize(ndarray) → 归一化后 L2 范数 ≈ 1.0（容差 ±1e-4）"

rollback_instructions: |
  1. 如果降级链导致所有嵌入失败 → 手动指定 VMS_EMBEDDING_MODEL=bge-small 环境变量（跳过 BGE-M3）
  2. 如果 warm-up 导致启动超时 → 将 warm-up 超时设为 5s（市级短超时，失败后跳过预热）
  3. 还原 D:\ZephyrAlpha\src\zephyr\vector_memory\embedding_router.py 至 TASK-INF-0204 完成后的版本
  4. 删除 D:\ZephyrAlpha\src\zephyr\vector_memory\in_memory_memory_backend.py

depends_on:
  - "TASK-INF-0204"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "data"
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
