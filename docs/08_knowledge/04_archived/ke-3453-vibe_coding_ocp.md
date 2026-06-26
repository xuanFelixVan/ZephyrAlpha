---
module_id: KE-3322-------v2-1-0-003
title: 4A.4 OCP 扩展点新增（v2.1.0）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4A.4 OCP 扩展点新增（v2.1.0）

4A.4 OCP 扩展点新增（v2.1.0）

除原有 L02/L05/L06 三个 OCP 扩展点外，**6 大核心服务均通过 Protocol 抽象基类暴露扩展点**：

| Protocol | 扩展场景 | experimental 实现 | beta+ 实现 |
|----------|---------|-------------|--------------|
| `VectorMemoryProtocol` | 替换向量库 | `InProcessVectorMemory` (ChromaDB) | `RemoteVectorMemory` (HTTP Client) |
| `ContextEngineProtocol` | 替换 CE 实现 | `InProcessContextEngine` | `RemoteContextEngine` |
| `OrchestratorProtocol` | 替换任务队列 | `InProcessOrchestrator` (SQLite + asyncio) | `RemoteOrchestrator` (NATS) |
| `FeedbackLoopProtocol` | 替换时序存储 | `InProcessFeedbackLoop` (SQLite) | `RemoteFeedbackLoop` (InfluxDB) |
| `LLMSecurityProtocol` | 替换 LSG 实现 | `LocalLLMSecurityGateway` (Pydantic + 规则) | `RemoteLLMSecurityGateway` + 专用模型 |
