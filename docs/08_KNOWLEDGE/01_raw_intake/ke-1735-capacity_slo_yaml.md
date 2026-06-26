---
module_id: KE-1645---------capacity-slo-yaml-000
status: active
title: 2.1 创建 / 更新 capacity_slo.yaml
category: module_blueprint
ttl: permanent
---

# 2.1 创建 / 更新 capacity_slo.yaml

2.1 创建 / 更新 capacity_slo.yaml

创建 `D:\ZephyrAlpha\config\capacity\capacity_slo.yaml`，包含完整 SLI 定义：

```yaml
version: "2.6.0"
module_id: MOD-INF-001
slis:
  - id: CAP-001
    name: "AI 审计覆盖完整率"
    metric: "ai_provenance_coverage_ratio"
    target: 0.999
    window: "7d"
    severity: critical
    burn_rate_thresholds:
      fast_cycle: {threshold: 14.4, window: "1h"}
      medium_cycle: {threshold: 6.0, window: "6h"}
      slow_cycle: {threshold: 3.0, window: "24h"}
    instrumentation:
      enabled: true
      insert_timing: true
      correction_latency: true

  - id: CAP-002
    name: "容量 SLO 达标率"
    metric: "capacity_slo_attainment_ratio"
    target: 0.995
    window: "7d"
    severity: critical
    burn_rate_thresholds:
      fast_cycle: {threshold: 14.4, window: "1h"}
      medium_cycle: {threshold: 3.0, window: "6h"}
      slow_cycle: {threshold: 1.0, window: "24h"}
    instrumentation:
      enabled: true

  - id: CAP-003
    name: "ContractBus 校验通过率"
    metric: "contract_bus_validation_ratio"
    target: 0.999
    window: "30d"
    severity: high
    burn_rate_thresholds:
      fast_cycle: {threshold: 14.4, window: "1h"}
      medium_cycle: {threshold: 6.0, window: "6h"}
    instrumentation:
      enabled: true
      validation_timing: true

  - id: CAP-004
    name: "Kill Switch 响应时间"
    metric: "kill_switch_response_seconds"
    target: 5.0
    window: "30d"
    severity: critical
    instrumentation:
      enabled: true

  - id: CAP-005
    name: "Token Budget 准确性"
    metric: "token_budget_accuracy_ratio"
    target: 0.1
    window: "7d"
    severity: high
    instrumentation:
      enabled: true

  - id: CAP-006
    name: "Sandbox 隔离有效性"
    metric: "sandbox_breach_count"
    target: 0
    window: "30d"
    severity: critical
    instrumentation:
      enabled: true

  - id: CAP-007
    name: "Error Budget 消耗告警准确率"
    metric: "error_budget_alert_accuracy"
    target: 0.95
    window: "30d"
    severity: medium
    instrumentation:
      enabled: true

  - id: CAP-008
    name: "Graceful Degradation 切换时间"
    metric: "degradation_switch_seconds"
    target: 2.0
    window: "30d"
    severity: high
    instrumentation:
      enabled: true

  - id: CAP-010-context-injection-size
    description: "每次 AI session 启动注入的上下文 token 数"
    target: 32000
    instrumentation:
      hook_point: "context-engine.ContextInjector.inject.exit"
      measurement: "token_counter on assembled context string"
      aggregation: "p50 + p99"
    degradation_alert: "p50 > 40000 for 3 consecutive sessions"

  - id: CAP-011-spiral-detection-rate
    description: "退化螺旋检测——同一任务连续门禁驳回 ≥3 次的事件率"
    target: "< 1 / week"
    instrumentation:
      hook_point: "DegradationSpiralDetector.detect.exit"
      measurement: "events per week"
      aggregation: "count"
    critical_threshold: "> 3 / week"
    critical_action: "auto_trigger_blueprint_audit + notify_owner"

  - id: CAP-012-write-buffer-lag
    description: "容量指标写入缓冲刷新延迟 P99"
    target: 100
    ins
