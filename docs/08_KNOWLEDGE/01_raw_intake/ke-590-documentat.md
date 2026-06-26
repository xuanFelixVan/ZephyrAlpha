---
module_id: KE-531
title: 8.3 数据保留与销毁
category: documentation
ttl: permanent
---

# 8.3 数据保留与销毁

8.3 数据保留与销毁

| 数据 | 保留期 | 销毁策略 |
|------|:------:|---------|
| Session Log | 180 天 | 90 天后归档 .gz，180 天后删除 |
| 向量库（VMS）| 永久 | 手动 TTL（个人系统无合规销毁要求）|
| Broker 交易日志（未来）| 7 年 | 合规要求（beta 定）|
| Audit Finding | 2 年 | 压缩归档 |

---
