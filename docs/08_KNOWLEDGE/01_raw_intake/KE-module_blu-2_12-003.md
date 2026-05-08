---
module_id: KE-module_blu-2_12-003
title: 2.12 可观测性与指标
category: module_blueprint
---

# 2.12 可观测性与指标

2.12 可观测性与指标

> **对标**：Anthropic 自动化行为审计 + AICosts.ai 实时成本追踪。

```yaml
observability:
  # === 核心指标 ===
  metrics:
    escalation_rate:
      description: "触发 auto_guard / blocked 的操作占比"
      target: "auto_guard ≤ 5%, blocked ≤ 1%"

    false_positive_rate:
      description: "auto_guard 后验证实不需要升级的比例"
      target: "≤ 20%"

    false_negative_rate:
      description: "本应升级但被列为 autonomous 的操作比例"
      target: "≤ 0.1%"  # 极低容忍

    delegation_success_rate:
      description: "委托在 SLA 内完成的比例"
      target: "≥ 95%"

    deadlock_events:
      description: "检测到的死锁次数"
      target: "0（生产环境）"

    decision_latency:
      description: "升级判定耗时 P50/P99"
      target: "P50 ≤ 5ms, P99 ≤ 50ms"

    cost_per_decision:
      description: "每次升级判定消耗的 Token 成本"
      target: "≤ $0.0001"

  # === 通知分级 ===
  notifications:
    INFO:
      level: "auto_guard 后验通过（正常流程）"
      channel: "IDE 静默标记"
      aggregation: "批量汇总（非实时）"

    WARN:
      level: "auto_guard 后验失败 1-2 次 / 预算消耗 > 80% / 委托超时"
      channel: "IDE 提示 + 终端输出"
      aggregation: "每 5 分钟汇总一次"

    CRITICAL:
      level: "blocked / 引擎故障 / 死锁检测 / 规则篡改告警"
      channel: "IDE 醒目通知 + 终端输出 + 审计日志文件标记"
      require_ack: "是（Owner在IDE中确认收到）"

  # === 仪表盘 ===
  dashboard:
    scope: "1人维护场景——简单文本报告即可"
    format: "Markdown 周报（AI自动生成）+ 实时 JSONL 查询"
    content: ["升级率趋势", "Token消耗Top10任务", "死锁事件日志", "假阳性Top规则"]
```

---
