---
module_id: KE-2396---------d-0-000
status: active
title: 6.5 Knowledge Base 投毒防护（决策 D-020-28）
category: module_blueprint
---

# 6.5 Knowledge Base 投毒防护（决策 D-020-28）

6.5 Knowledge Base 投毒防护（决策 D-020-28）

> **决策 D-020-28**（新增）：审计数据被喂入 Knowledge Base 前进行安全过滤。(a) 标记 `KB_POISONING_ATTEMPT` 的条目永久排黑，(b) 审计数据进入 KB 前经过 provenance 评分——仅 `trust_score >= 0.5` 的 Agent 产生的数据可被 KB 接受，(c) 投毒检测：异常高 confidence（0.99+）+ 异常低 anomaly_score（0.0）= 潜在构造数据。

```python
class KBAuditGate:
    """Knowledge Base 审计门禁——防止审计数据投毒 KB"""

    def filter_before_kb_ingest(self, entries: list[AuditEntryV1]) -> list[AuditEntryV1]:
        """过滤不适合进入 KB 的审计条目——POISONING_ATTEMPT / anomaly_score > 0.5 / confidence < 0.3"""

    def score_for_kb_trust(self, entry: AuditEntryV1) -> float:
        """评估单条审计记录对 KB 的 trustworthiness——0.0~1.0"""

    def detect_constructed_pattern(self, entries: list[AuditEntryV1]) -> bool:
        """检测人工构造的审计模式——confidence 异常高 + anomaly_score 异常低"""
```

---
