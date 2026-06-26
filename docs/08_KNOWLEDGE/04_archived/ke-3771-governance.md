---
module_id: KE-3620
title: 7. 违规处理
category: governance
ttl: permanent
---

# 7. 违规处理

7. 违规处理

| 违规级别 | 情形 | 处理 |
|---------|------|------|
| WARNING | 任务报告未提及清扫结果 | 下次 session 补扫 |
| ERROR | 发现 temp_*/backup 残留 | 立即删除，session log 记录 |
| CRITICAL | 产出物不在 deliverables 内且未声明 | 任务标记为需返工 |
