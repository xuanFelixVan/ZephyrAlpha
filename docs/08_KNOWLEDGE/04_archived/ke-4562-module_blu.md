---
module_id: KE-4397
title: Phase 1：基础设施对齐
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# Phase 1：基础设施对齐

Phase 1：基础设施对齐

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §6 架构分层——ProvenanceEnforcer / EmbeddingRouter / ChunkStrategyRouter / IndexHealthMonitor / CacheLayer / BridgeLayer |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\vector-memory\` 下 6 个模块文件 |
| 验收标准 | 1) ProvenanceEnforcer 可校验 WriteTrace 2) EmbeddingRouter 可按 Collection 路由到不同模型 3) BridgeLayer 可同时检索 kb/ 和 VMS |
| G7 检查项 | 蓝图漂移自检通过？双模型加载正常？BridgeLayer 双读测试通过？ |
