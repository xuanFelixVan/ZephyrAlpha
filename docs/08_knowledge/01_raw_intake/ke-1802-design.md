---
module_id: KE-1711---------------------d-023-003
status: active
title: 2.14 自动学习——假阳性模式识别与抑制（决策 D-023-21）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.14 自动学习——假阳性模式识别与抑制（决策 D-023-21）

2.14 自动学习——假阳性模式识别与抑制（决策 D-023-21）

> **决策 D-023-21**：同一 (detector, pattern) 组合被多次标记为 FALSE_POSITIVE 后，自动学习该模式——在后续扫描中静默抑制，转为 shadow 观测。若抑制后漂移模式发生变化（可能假阳性变成真漂移），自动解除抑制。
>
> **决策依据**：1人维护下，反复手动标记假阳性是不可持续的。需要检测器具备自适应能力。

```yaml
auto_learning:
  false_positive_learning:
    trigger: "同一 (detector_id, module_id, pattern_hash) 组合被标记 FALSE_POSITIVE ≥ 3 次"
    action: "自动创建 suppression_rule → 后续匹配时自动抑制 + shadow 观测"
    shadow_mode: |
      抑制的漂移仍然在后台检测——每次 scan 对比 suppression_rule 创建时的 pattern 与当前 pattern。
      若 pattern 发生变化（如：之前误报是因为路径 A 匹配，现在路径 A 真的不存在了）→ 解除抑制 → 重新标记 DETECTED。

  pattern_hash:
    description: "漂移的归一化指纹——用于判断'同一模式'"
    composition:
      - "detector_id: 哪个检测器"
      - "drift_dimension: 哪个维度"
      - "diff_signature: 差异的结构化摘要（非精确文本匹配，而是结构匹配）"
    example: |
      蓝图路径不一致检测器 对 module_X 误报了 3 次
      → pattern_hash = SHA256(detector=blueprint_code_sync + dim=D5-BP-SYNC + diff_type=path_missing)
      → 自动抑制该组合

  suppression_review:
    frequency: "每 30 天自动提示 Owner review 所有活跃的 suppression_rule"
    metric: "每个 rule 的 shadow 命中次数 / 总 scan 次数"
    stale_rule: "若 rule 在 30 天内 shadow 命中次数 = 0 → 建议删除（模式可能已不存在）"
```
