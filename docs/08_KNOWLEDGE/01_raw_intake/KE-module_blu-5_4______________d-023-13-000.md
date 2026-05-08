---
module_id: KE-module_blu-5_4______________d-023-13-000
title: 5.4 告警路由与疲劳管理（决策 D-023-13）
category: module_blueprint
---

# 5.4 告警路由与疲劳管理（决策 D-023-13）

5.4 告警路由与疲劳管理（决策 D-023-13）

> **决策 D-023-13**：定义告警路由策略——不同严重度、不同模块优先级的漂移走不同通知渠道。引入智能去重和聚合，避免告警风暴。
>
> **决策依据**：1人维护场景下，告警疲劳是最大的 operational risk。需要分级路由 + 自动聚合摘要。

```yaml
alert_routing:
  channels:
    P0_CRITICAL:
      description: "P0 模块漂移预算耗尽 / 自漂移检测失败 / 回滚验证失败"
      channel: "即时通知（Feishu @owner + 终端告警）"
      ack_required: true
      ack_timeout: "30min 未确认 → 升级（重复通知）"

    P0:
      description: "HIGH severity 漂移（AI 幻觉 import / 契约破坏 / SSoT 不一致）"
      channel: "Feishu 群消息（非 @）"
      ack_required: false
      aggregation: "每小时聚合一次 → 发送摘要（非逐条）"

    P1:
      description: "MEDIUM severity + 趋势告警"
      channel: "每日摘要报告（Feishu 定时推送）"
      ack_required: false

    P2:
      description: "LOW severity + 信息类"
      channel: "不推送——仅在 dashboard 可见"
      ack_required: false

  deduplication:
    - method: "同一 (module_id, detector_id, drift_dimension) 组合在 6h 内只告警一次"
    - method: "若同一漂移在连续 3 次 scan 中均出现 → 聚合为 persistent_alert"

  grouping:
    - method: "同一 scan 周期内 > 10 个漂移 → 聚合为 batch_alert（列出 TOP 3 + 总计 N）"
    - method: "同一根因（correlation engine 发现）→ 聚合为 causal_group_alert"

  silence_policy:
    - "夜间（22:00-08:00）→ 仅 P0_CRITICAL 通知"
    - "周末 → 仅 P0_CRITICAL + P0 聚合摘要（每条延迟到周一）"
    - "Owner 可声明 focus_time（2h 免打扰窗口）"
```
