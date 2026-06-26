---
module_id: KE-1879--------bootstrapping-cali-000
status: active
title: 2.30 启动校准阶段（Bootstrapping Calibration Phase）
category: module_blueprint
ttl: permanent
---

# 2.30 启动校准阶段（Bootstrapping Calibration Phase）

2.30 启动校准阶段（Bootstrapping Calibration Phase）

> **决策 D-024-28（🆕 v0.7.0）**：Day 0 的 budget_policy.yaml 是 AI 生成的猜测。如果阈值太紧→系统不可用→无法收集数据→自学习无法启动。需要一个显式的"宽限期"。

```yaml
bootstrapping_calibration:
  description: "新部署的前 30 天为校准模式——阈值宽松，侧重数据收集而非严格执法"
  duration: "30 days or 100 tasks completed（whichever first）"

  calibration_profile:
    description: "所有 hard_limit 临时 ×3，soft_limit 仅告警不阻断"
    hard_limit_multiplier: 3.0
    enforcement: "ALL actions → warn-only（不 DENY，不 HALT）"
    exceptions: "loop_detection 和 kill_switch 这两个安全熔断保持生效"

  exit_criteria:
    min_data_points: 100            # 至少收集 100 个任务的消耗数据
    convergence: "预算预估偏差 < 20%（连续 10 个任务）"
    auto_exit: "满足条件后自动切换到正常 enforcement 模式"
    manual_exit: "Owner 可随时执行 `zephyr budget exit-calibration` 提前结束"

  post_calibration:
    auto_tune: "基于收集的 100 个任务数据，自动调整 soft_limit/hard_limit 为 P95 消耗值"
    report: "校准报告——各模型/任务类型的 P50/P75/P95/P99 消耗分布"
    human_review: "自动调整后的阈值需 Owner 签名确认方可生效"
```

---
