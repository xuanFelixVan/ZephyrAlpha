---
task_id: "TASK-INF-0204"
source_blueprint: "MOD-INF-011"
source_section: "§3 技术选型"

title: "技术选型落地——ChromaDB 0.6 PersistentClient + 双嵌入模型 ONNX 加载 + 配置基线"
description: |
  实现蓝图 §3 的完整技术选型基础设施：
  1. ChromaDB 0.6 PersistentClient 单例创建（指向 data/vector_db/）→ 用于所有 Collection 操作
  2. BGE-M3 ONNX 嵌入模型加载——1024 维，本地推理，批量大小 16，延迟 <50ms/条
  3. bge-small-zh-v1.5 轻量模型加载——512 维，300MB，查询快 3×（<10ms/条），批量大小 32
  4. 距离度量统一为 cosine
  5. ONNX Runtime 配置——免 GPU，CPU 可跑
  6. 嵌入模型缓存路径配置（models/bge-m3/ 和 models/bge-small-zh-v1.5/）
  7. ChromaDB anonymized_telemetry 显式禁用（V-VMS-503 盲点要求）
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\paths.py"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "InProcessVectorMemory 单例——ChromaDB PersistentClient 创建 + 双模型加载 + 关闭"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"
    description: "EmbeddingRouter 类——embed(text, collection_name) → ndarray，按 Collection 路由到 BGE-M3 或 bge-small"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\embedding_router.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\paths.py"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

applicable_rules:
  - module_id: "ADR-0031"
    section: "§4.2"
    reason: "ChromaDB 基线选型——PersistentClient 配置依据"
  - module_id: "ADR-0016"
    section: "§3"
    reason: "BGE-M3 ONNX 生产级嵌入契约——1024d 向量输出规范"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§3 技术选型——ChromaDB 0.6 + BGE-M3 ONNX + bge-small-zh-v1.5 + cosine + ONNX Runtime 完整参数"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
    reason: "现有 ChromaDB PersistentClient 实现——参考 PersistentClient 创建模式"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "PersistentClient 单例指向 D:\\ZephyrAlpha\\data\\vector_db\\，启动时可正常创建"
  - "BGE-M3 ONNX 模型从 models/bge-m3/ 加载成功且输出 shape=(1024,)"
  - "bge-small-zh-v1.5 模型从 models/bge-small-zh-v1.5/ 加载成功且输出 shape=(512,)"
  - "EmbeddingRouter.embed('test', 'rules') → BGE-M3 1024d 向量"
  - "EmbeddingRouter.embed('test', 'blueprints') → bge-small 512d 向量"
  - "ChromaDB anonymized_telemetry 显式设为 False"
  - "cosine 距离度量为所有 Collection 默认度量"
  - "BGE-M3 单条推理延迟 ≤50ms（在开发机上测量）"
  - "bge-small 单条推理延迟 ≤10ms（在开发机上测量）"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\vector_memory\embedding_router.py
  2. 从 InProcessVectorMemory 中移除 ChromaDB PersistentClient 和双模型加载代码
  3. 确保 ChromaDB PersistentClient 实例已正确关闭（.close()）——否则 SQLite WAL 文件残留
  4. 删除 data/vector_db/ 下测试产生的新 SQLite 文件

depends_on:
  - "TASK-INF-0201"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
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
