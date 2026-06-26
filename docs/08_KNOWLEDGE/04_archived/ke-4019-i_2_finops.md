---
module_id: KE-3866--------2-------finops--000
title: 13.10 I. 成本与资源（2个）——对标 FinOps FOCUS + ML Observability
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 13.10 I. 成本与资源（2个）——对标 FinOps FOCUS + ML Observability

13.10 I. 成本与资源（2个）——对标 FinOps FOCUS + ML Observability

> **现状**：蓝图无任何资源消耗追踪。在 1人+AI 模式下，成本透明是生存底线。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 30 | **V-VMS-430** | **无 Embedding 耗时/资源追踪**——每次 embed 调用耗时多少？BGE-M3 vs bge-small 实际延迟差异？是 CPU 瓶颈还是内存瓶颈？需要 Per-Collection 级别的 embedding latency histogram | 2 | 2 | 3 | 12 🟡 | 性能调优 |
| 31 | **V-VMS-431** | **无 VMS 存储增长预测**——基于过去 30 天的写入速率，预测 30/60/90 天后各 Collection 的预估大小。对标 AWS S3 的 storage class analysis。这是 "什么时候磁盘会满" 的底线预测 | 2 | 2 | 3 | 12 🟡 | 长期运行 |
