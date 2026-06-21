---
module_id: KE-4051
title: 3. 技术选型
category: module_blueprint
---

# 3. 技术选型

3. 技术选型

| 维度 | 选择 | 理由 |
|------|------|------|
| 向量数据库 | ChromaDB 0.6 | 本地嵌入式，Python原生，零运维。PersistentClient = SQLite + HNSW 向量文件 |
| 主嵌入模型 | BGE-M3 ONNX | 1024维，中文双语，本地推理免API费。适用：decisions/lessons/knowledge/rules/code_context |
| 轻量嵌入模型 | bge-small-zh-v1.5 | 512维，300MB，查询快 3×。适用：blueprints/session_snapshots/execution_traces |
| 推理方式 | ONNX Runtime | 免GPU，CPU可跑。BGE-M3 延迟 <50ms/条，bge-small <10ms/条 |
| 批量大小 | 16（1024d） / 32（512d） | 按维度差异分配，控制内存 |
| 距离度量 | cosine | ChromaDB 默认，语义相似标准度量 |
| 混合检索 | Vector(HNSW) + BM25 + RRF融合 | 向量近似召回 ×3 → BM25关键词 → RRF加权合并 → score threshold 过滤 |
| 分块路由 | ChunkStrategyRouter | Collection 级分块策略：AST-aware / heading-aware / time-window / section-aware |
