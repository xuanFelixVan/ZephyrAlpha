---
module_id: KE-1806
status: active
title: 2.228 Decision Entropy Monitor - decision_entropy_monitor.py (🆕 v0.21.0 - 盲点277
category: module_blueprint
---

# 2.228 Decision Entropy Monitor - decision_entropy_monitor.py (🆕 v0.21.0 - 盲点277

2.228 Decision Entropy Monitor - decision_entropy_monitor.py (🆕 v0.21.0 - 盲点277 — FLE决策输出的信息熵监测)

**致命问题**：ZombieDetector检测"0异常天数"（极端情况），但不检测"FLE每天在输出决策，但全都是同一种回答"的中间态。如果FLE对50个不同的anomaly signature都输出完全相同的DIAGNOSE("CPU_LOAD_REDUCE")→决策分布熵=0→要么系统真的只有一种问题要么FLE的诊断引擎已退化到单模式。这在氛围编程中尤其危险——某次prompt调整可能让FLE的DIAGNOSE输出坍缩到几个template模式。
**对标**：Shannon Information Theory + Datadog Watchdog Anomaly Distribution + GPT Output Diversity Monitoring

```python
class DecisionEntropyMonitor:
    MIN_ENTROPY_ALERT: float = 1.5       # bits, <1.5→输出多样性不足
    CRITICAL_ENTROPY: float = 0.5         # bits, <0.5→几乎单一输出
    SLIDING_WINDOW_DECISIONS: int = 100

    async def monitor_decision_entropy(self) -> EntropyReport:
        recent = await self._load_recent_decisions(self.SLIDING_WINDOW_DECISIONS)
        # 计算Shannon entropy: H = -Σ p(x_i) * log2(p(x_i))
        type_counts = Counter(d.action_type for d in recent)
        total = len(recent)
        entropy = -sum((c/total) * math.log2(c/total)
                       for c in type_counts.values() if c > 0)
        # Per-stage entropy
        diagnose_entropy = self._compute_entropy([d.diagnosis_type for d in recent])
        repair_entropy = self._compute_entropy([d.repair_type for d in recent
                                                  if d.repair_type])
        if entropy < self.CRITICAL_ENTROPY:
            top_action = type_counts.most_common(1)[0]
            self.FLE.notify_owner("DECISION_ENTROPY_COLLAPSE",
                f"FLE decision entropy={entropy:.2f}bits (<{self.CRITICAL_ENTROPY}). "
                f"FLE is producing nearly identical decisions: "
                f"{top_action[0]} accounts for {top_action[1]/total:.0%} of last {total}. "
                f"This suggests: diagnostic engine degradation, prompt mode collapse, "
                f"or genuinely uniform system behavior. "
                f"Recommend: inject synthetic diverse anomalies→test FLE response diversity.")
            await self._inject_synthetic_diversity_test()
        elif entropy < self.MIN_ENTROPY_ALERT:
            self.FLE.notify_owner("DECISION_ENTROPY_LOW",
                f"FLE decision entropy={entropy:.2f}bits—below diversity threshold. "
                f"Diagnose entropy={diagnose_entropy:.2f}, Repair entropy={repair_entropy:.2f}.")
        return EntropyReport(overall_entropy=entropy,
            diagnose_entropy=diagnose_entropy, repair_entropy=repair_entropy)
```
