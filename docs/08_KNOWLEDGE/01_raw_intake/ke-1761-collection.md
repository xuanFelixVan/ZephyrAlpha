---
module_id: KE-1670
title: 2.1 Collection 设计原则
category: module_blueprint
ttl: permanent
---

# 2.1 Collection 设计原则

2.1 Collection 设计原则

| 原则 | 说明 |
|------|------|
| **按访问模式分，不按数据来源分** | 高频热数据（rules/decisions）与低频冷数据（blueprints/execution_traces）分离索引 |
| **嵌入维度按精度需求分配** | 1024d 用于精确语义匹配（决策、规则、教训），512d 用于量大体（蓝图、日志、会话） |
| **分块策略 Collection 级差异化** | 代码用 AST-aware，文档用 heading-aware，日志用 time-window——不可混用 |
| **TTL 强制（冷数据自动过期）** | `execution_traces` 30d、`code_context` 和 `session_snapshots` 90d 自动清理 |
| **Provenance 每条必带** | 继承 unified_memory_api 的 WriteTrace——origin / audit_chain / arbitration 三位一体 |

---
