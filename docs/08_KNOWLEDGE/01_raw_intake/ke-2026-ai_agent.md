---
module_id: KE-1935------1--ai-000
status: active
title: 2.7 自监控——1人+AI 维护的刚需
category: module_blueprint
ttl: permanent
---

# 2.7 自监控——1人+AI 维护的刚需

2.7 自监控——1人+AI 维护的刚需

审计系统无人运维 → 必须自监控。对标 Goldman SecDB Prometheus probing + PagerDuty escalation。

```yaml
self_monitoring:
  heartbeat:
    interval: "60s"
    check: "写入 1 条 heartbeat 条目 → 读回验证哈希链 → 延迟 < 5ms"
    on_failure: "连续 3 次失败 → P0 audit_system_down 告警 → 写入 emergency fallback log"

  health_metrics:
    - name: "write_latency_p99_ms"
      threshold: "5 ms"
      alert: "> 10 ms P99 → P1"
    - name: "disk_usage_pct"
      threshold: "80%"
      alert: "> 80% → P1，> 90% → P0"
    - name: "jsonl_file_count"
      threshold: "每 IDE ≤ 365 文件"
      alert: "超过 → P2"
    - name: "hash_chain_integrity"
      threshold: "100% pass"
      alert: "任一 fail → 立即 P0 阻断"
    - name: "hmac_validity_rate"
      threshold: "100% pass"
      alert: "任一 fail → 立即 P0 阻断"
    - name: "sqlite_index_health"
      threshold: "online"
      alert: "offline > 60s → P1 + auto-rebuild"
    - name: "agent_signature_validity_rate"
      threshold: "100% pass"
      alert: "任一 fail → 立即 P0 阻断"
    - name: "delegation_chain_validity"
      threshold: "100% pass"
      alert: "链断裂或权限放大 → P0"
    - name: "trust_score_trend"
      threshold: "下降 > 0.3 / 7d"
      alert: "P1——Agent 行为趋势恶化"
    - name: "cross_ide_consistency"
      threshold: "100% pass"
      alert: "不一致 > 0 → P1"
