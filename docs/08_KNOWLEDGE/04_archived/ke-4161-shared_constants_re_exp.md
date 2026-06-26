---
module_id: KE-4005----re-exp-000
title: 2.4 shared-constants（集中 re-export）
category: module_blueprint
ttl: permanent
---

# 2.4 shared-constants（集中 re-export）

2.4 shared-constants（集中 re-export）

> **修复散落枚举问题**——此前 AI 需要到 instrument.py / order.py / observer.py / schemas.py 四处找枚举。

| 文件 | 职责 |
|------|------|
| `constants.py` | 所有共享枚举集中 re-export——AssetClass / OrderSide / EventType / TaskStatus / KeCategory 等 22 个枚举/常量 |
