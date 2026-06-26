---
module_id: KE-1322
title: 1.3 责任范围（管什么）
category: module_blueprint
ttl: permanent
---

# 1.3 责任范围（管什么）

1.3 责任范围（管什么）

| 职责 | 内容 |
|------|------|
| **知识全生命周期** | 采集(G1)→分拣(G2)→分析(G3)→激活(G4)→提取(G5) 五门禁流水线 |
| **知识条目管理** | KE 的创建、状态流转（10状态机）、版本管理、过期检测 |
| **向量语义检索** | ChromaDB 4 Collection：ke_entries / vibe_rules / blueprints / failure_patterns |
| **跨Agent知识互通** | MCP 协议：4 Resource + 4 Tool，多模型（Claude/Kimi/Qwen/GLM）共享知识 |
| **审计与质量保障** | 四模型审计流水线（GLM扫描→Kimi根因→Qwen落地→Opus终审）+ 知识衰减/新鲜度管理 |
| **上下文注入** | 与 MOD-TASK_SYSTEM `context_assembler` 对接，AI session 启动时自动注入相关KE |
