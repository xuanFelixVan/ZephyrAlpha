---
module_id: KE-4436
title: 0. 读者指南
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# 0. 读者指南

0. 读者指南

| 章节 | 内容 | 主要读者 |
|------|------|----------|
| §1 | 设计动机：为什么需要 Session Carryover | 架构师、用户 |
| §2 | Schema 完整定义（JSON Schema + Pydantic）| 开发者 |
| §3 | 字段详细说明 | 开发者 |
| §4 | 写入时机（Session 结束前）| Context Engine 实现者 |
| §5 | 读取时机（Session 启动后）| Context Engine 实现者 |
| §6 | 与 Context Engine 的集成点 | CE 实现者 |
| §7 | 示例：一个完整的 `session_carryover.json` | 所有读者 |
| §8 | 演化策略（schema_version 管理）| 架构师 |
