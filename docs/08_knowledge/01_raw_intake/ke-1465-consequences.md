---
module_id: KE-1375-----consequences-004
status: active
title: 11. 后果（Consequences）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 11. 后果（Consequences）

11. 后果（Consequences）

**正面后果**：
- AI Agent 获得语义检索能力——从"精确匹配"升级为"语义相似"，大幅提升上下文质量
- 跨 session 记忆——AI 可以检索历史决策和失败模式，避免重复犯错（session_snapshots 冷启动 1 次查询复原状态）
- 统一向量存储——8 Collection 覆盖全系统知识类型，消除信息孤岛，治理规则独立高优检索
- 双嵌入维度策略——高频精度域 1024d + 量大体轻量 512d，成本与质量的帕累托最优
- 可审计溯源——每条向量带 WriteTrace（origin/audit_chain/arbitration），满足单人+AI 维护的治理底线
- 检索质量闭环——FLE 直接消费 VMS 检索反馈信号，形成自我优化的正反馈回路
- 索引自愈——HealthMonitor 自动检测漂移 + 损坏，减少 Owner 手动维护负担

**负面后果**：
- 引入 ChromaDB + BGE-M3 + bge-small 三依赖——部署复杂度增加
- 向量检索不确定性——语义相似 ≠ 语义相同，可能返回不相关结果（混合检索 + RRF 缓解）
- BGE-M3 ONNX 约 2GB 内存 + bge-small 约 300MB——双模型增加资源占用
- 8 Collection 架构复杂度 > 5 Collection——Phase 1 基础设施对齐工作量增加约 50%

---
