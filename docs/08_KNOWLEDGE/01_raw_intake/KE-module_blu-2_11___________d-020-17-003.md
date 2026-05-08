---
module_id: KE-module_blu-2_11___________d-020-17-003
title: 2.11 渐进信任分数（决策 D-020-17）
category: module_blueprint
---

# 2.11 渐进信任分数（决策 D-020-17）

2.11 渐进信任分数（决策 D-020-17）

> **决策 D-020-17**（新增）：对标 ISACA "trust degrades without continued good behavior" + Microsoft AGT Trust Scoring。信任从离散 RBAC 角色扩展为连续浮点数 `trust_score: 0.0~1.0`。每个操作记录操作时的 trust_score。信任规则：(a) 每次成功操作 +0.001（缓慢上升），(b) 每次 anomaly -0.2（快速下降），(c) 每天无活动 -0.005（自然衰减），(d) trust_score < 0.5 → 自动降级权限级别。

```python
class TrustScoreEngine:
    DEFAULT_SCORE: float = 0.6
    SUCCESS_INCREMENT: float = 0.001
    ANOMALY_DECREMENT: float = 0.2
    DAILY_DECAY: float = 0.005
    DEMOTION_THRESHOLD: float = 0.5

    def update(self, agent_did: str, event: AuditEventType, anomaly_score: float | None) -> float: ...
    def current(self, agent_did: str) -> float: ...
    def trend(self, agent_did: str, days: int = 7) -> list[float]: ...
```
