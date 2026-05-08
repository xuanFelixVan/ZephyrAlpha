---
module_id: KE-module_blu-2_10-000
title: 2.10 置信度驱动的升级判定
category: module_blueprint
---

# 2.10 置信度驱动的升级判定

2.10 置信度驱动的升级判定

> **对标**：Rasa FallbackClassifier（置信度 < 0.7 → 自动升级为 nlu_fallback）。

```yaml
confidence_escalation:
  # === 置信度来源 ===
  confidence_sources:
    llm_self_assessment: "Agent 对自己的决策给出 0.0-1.0 的置信度评分"
    historical_accuracy: "同类操作的历史成功率（从审计日志统计）"
    task_complexity_score: "基于任务卡字段（depends_on数量/修改范围/涉及模块数）"

  # === 置信度阈值 ===
  thresholds:
    high_confidence: "≥ 0.85 → autonomous（直接执行）"
    medium_confidence: "0.7 - 0.85 → auto_guard（先干后验）"
    low_confidence: "< 0.7 → auto_guard + 委托复核（委托给更高能力Agent）"
    critical_low: "< 0.4 → blocked（AI不执行，直接通知Owner）"

  # === 置信度校准 ===
  calibration:
    method: "对比 Agent 自评置信度 vs 实际后验结果"
    adjustment: "每100次操作校准一次——Agent 高估→提高阈值，低估→降低阈值"
    target: "校准后 auto_guard 后验通过率 ≥ 90%"
```

---
