---
module_id: KE-3426
title: 9.4 日志消费者
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 9.4 日志消费者

9.4 日志消费者

| 消费者 | 用途 | 访问模式 |
|--------|------|---------|
| Feedback Loop Engine | 异常检测 + 自调节 | 流式读 |
| Session Carryover | 下次 IDE 会话恢复上下文 | 批读 |
| 人工审计 / 合规 | 事件回溯 | SQL 查询 |
| ML 模型训练（beta+）| 异常模式学习 | 历史回放 |

---
