---
module_id: KE-2583----v2-0-0----003
status: active
title: capacity_slo.yaml 示例（v2.0.0 含 Saturation 四黄金信号）
category: module_blueprint
ttl: permanent
---

# capacity_slo.yaml 示例（v2.0.0 含 Saturation 四黄金信号）

capacity_slo.yaml 示例（v2.0.0 含 Saturation 四黄金信号）
slo_registry:
  - id: CAP-001-startup-time
    description: "97 模块启动时间 P99"
    target: 2000
    measurement: pytest 基准测试
    golden_signal: latency
    governance_layer: GOV-P1
    runtime_plane: RP-2
  - id: CAP-002-event-throughput
    description: "事件总线吞吐量"
    target: 1000
    measurement: msg/s 压力测试
    golden_signal: traffic
    governance_layer: GOV-P1
    runtime_plane: RP-1
  - id: CAP-003-error-rate
    description: "模块间调用错误率"
    target: 0.001
    measurement: circuit_breaker 统计
    golden_signal: errors
    governance_layer: GOV-P1
    runtime_plane: RP-1
  - id: CAP-004-memory-saturation
    description: "内存饱和度"
    target: 0.8
    measurement: psutil 内存监控
    golden_signal: saturation
    governance_layer: GOV-P1
    runtime_plane: RP-2
  - id: CAP-005-cpu-saturation
    description: "CPU 饱和度"
    target: 0.7
    measurement: psutil CPU 监控
    golden_signal: saturation
    governance_layer: GOV-P1
    runtime_plane: RP-2
  - id: CAP-006-queue-depth-saturation
    description: "事件队列深度饱和度"
    target: 500
    measurement: asyncio.Queue.qsize()
    golden_signal: saturation
    governance_layer: GOV-P1
    runtime_plane: RP-1
  - id: CAP-007-type-check-time
    description: "类型检查时间 P99"
    target: 30000
    measurement: dmypy 基准测试
    golden_signal: latency
    governance_layer: GOV-P2
    runtime_plane: RP-3
  - id: CAP-008-config-check-time
    description: "配置一致性检查时间 P99"
    target: 10000
    measurement: validate_ssot.py 计时
    golden_signal: latency
    governance_layer: GOV-P2
    runtime_plane: RP-3
```

---
