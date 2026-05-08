---
module_id: KE-module_blu-2_9_l6___observability________-003
title: 2.9 L6 — Observability 可观测性（决策 D-018-11）
category: module_blueprint
---

# 2.9 L6 — Observability 可观测性（决策 D-018-11）

2.9 L6 — Observability 可观测性（决策 D-018-11）

> **决策 D-018-11**：权限系统自身必须具备完整的可观测性——权限决策耗时、异常行为模式、权限变更审计。没有可观测性 = 不知道有没有被绕过。
>
> **决策依据**：D2 Telemetry & Observability 模式 + OpenTelemetry 标准。对标 CSA ATF Behavior 要素。

```yaml
observability:
  # ─── OpenTelemetry 指标 ───
  metrics:
    - metric: "agent_rbac.decision.total"
      type: Counter
      labels: [agent_id, agent_type, ide_source, tool_id, decision, layer]
      description: "各层权限判定计数"

    - metric: "agent_rbac.decision.latency_us"
      type: Histogram
      buckets: [50, 100, 200, 500, 1000, 2000]  # 微秒级
      description: "单层/总权限判定耗时"

    - metric: "agent_rbac.sequence.violation"
      type: Counter
      labels: [agent_id, sequence_name]
      description: "L4 序列护栏触发次数"

    - metric: "agent_rbac.kill_switch.state"
      type: Gauge
      values: [0=normal, 1=agent_blocked, 2=global_blocked]
      description: "Kill Switch 当前状态"

    - metric: "agent_rbac.engine.degraded"
      type: Gauge
      values: [0=full, 1=partial, 2=blocked_all]
      description: "Engine 降级状态"

    - metric: "agent_rbac.policy.bundle.age_seconds"
      type: Gauge
      description: "当前权限配置年龄——检测配置更新延迟"

  # ─── 行为异常检测规则 ───
  anomaly_detection:
    rules:
      - name: "unusual_tool_frequency"
        description: "Agent 在短时间内调用某 Tool 的次数远超历史基线"
        detection: "当前窗口调用次数 > 历史 P99 * 3"

      - name: "unusual_decision_pattern"
        description: "Agent 被 BLOCKED 的比例突然升高"
        detection: "5 分钟内 BLOCKED 率 > 20%"

      - name: "new_tool_first_use"
        description: "Agent 首次调用新的敏感 Tool"
        detection: "Agent 历史中无此 Tool + Tool 属于 auto_guard 级别"

    action: "触发告警 → 写入审计日志 → 不自动阻断（需要上下文判断），但累计触发 L0 Kill Switch"

  # ─── 权限变更审计 ───
  policy_audit:
    tracked_changes:
      - "rbac_roles.yaml 的任何修改"
      - "GOV-AI-001 的任何修改"
      - "L0 immutable_core 路径列表的任何修改"
    audit_fields: [who, what, when, why, diff, approved_by]
    storage: "不可变审计日志 + Git commit 关联"
```

---
