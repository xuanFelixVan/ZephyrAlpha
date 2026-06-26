---
module_id: KE-1724------meta-confidence-003
status: active
title: 2.16 升级引擎 Meta-Confidence —— 判定自身的置信度（决策 D-022-10）
category: module_blueprint
ttl: permanent
---

# 2.16 升级引擎 Meta-Confidence —— 判定自身的置信度（决策 D-022-10）

2.16 升级引擎 Meta-Confidence —— 判定自身的置信度（决策 D-022-10）

> **决策 D-022-10**：升级引擎对每一次判定输出附带 Meta-Confidence（自身对判定正确性的置信度）。Meta-Confidence < 0.7 时，判定需降级更保守方向。引擎定期自校准。
>
> **决策依据**：§2.10 定义了 Agent 的置信度阈值但缺失引擎自身的。不对称——要求 Agent 给出置信度但引擎自己不给→不安全。自指盲点。

```yaml
meta_confidence:
  # === Meta-Confidence 来源 ===
  sources:
    rule_match_strength: "规则匹配到操作的程度（完全匹配=1.0，模糊匹配=X）"
    historical_accuracy: "基于同类判定在审计中的正确率"
    context_ambiguity: "操作描述的歧义程度（越模糊→置信度越低）"

  # === 基于 Meta-Confidence 的决策修正 ===
  decision_correction:
    meta_confidence_high: "≥ 0.85 → 判定不变"
    meta_confidence_medium: "0.7-0.85 → 判定保留但标记 [LOW_CERTAINTY]"
    meta_confidence_low: "< 0.7 → 判定降级（向更保守方向移动一级）"
      # autonomous→auto_guard, auto_guard→blocked, blocked→keep blocked
    meta_confidence_critical: "< 0.4 → 无论原判定如何→blocked + Owner直接通知"

  # === 自校准 ===
  self_calibration:
    method: "对比引擎的 Meta-Confidence vs 操作最终结果（安全/有问题）"
    frequency: "每 100 次判定校准一次"
    target: "Meta-Confidence ≥ 0.7 时，实际正确率 ≥ 90%"
```

---
