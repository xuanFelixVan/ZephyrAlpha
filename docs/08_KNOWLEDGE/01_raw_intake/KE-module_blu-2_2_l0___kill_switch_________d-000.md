---
module_id: KE-module_blu-2_2_l0___kill_switch_________d-000
title: 2.2 L0 — Kill Switch 全局熔断（决策 D-018-05）
category: module_blueprint
---

# 2.2 L0 — Kill Switch 全局熔断（决策 D-018-05）

2.2 L0 — Kill Switch 全局熔断（决策 D-018-05）

> **决策 D-018-05**：建立全局 Kill Switch——当 Agent 行为模式触发危险阈值时，自动熔断所有 Agent 操作。
>
> **决策依据**：CSA Agentic Trust Framework Incident Response 要素——"What if you go rogue?"必须有答案。对标 K8s Circuit Breaker + 交易系统熔断。

```yaml
kill_switch:
  # ─── 自动熔断触发器 ───
  auto_triggers:
    - trigger: "rapid_file_deletion"
      condition: "同一 Agent 在 5 秒内删除 >= 3 个非 temporary 文件"
      action: "立即阻断该 Agent + 全局 warning"
      cooldown: "30 秒后自动解除（Owner 可手动延长）"

    - trigger: "permission_boundary_probe"
      condition: "同一 Agent 在 2 分钟内触发 >= 5 次 BLOCKED 判定"
      action: "立即阻断该 Agent + P0 审计告警"
      cooldown: "Owner 手动解除"

    - trigger: "suspicious_sequence"
      condition: "L4 Sequence Guard 在 1 分钟内触发 >= 2 次"
      action: "立即阻断该 Agent + 安全事件记录"
      cooldown: "Owner 手动解除"

    - trigger: "off_hours_destructive"
      condition: "非工作时间（22:00-06:00）执行 auto_guard 级别操作"
      action: "操作降级为 blocked，需 Owner 确认"
      cooldown: "工作时间自动解除"

    - trigger: "config_file_blitz"
      condition: "同一 Agent 在 60 秒内修改 >= 10 个 YAML 文件"
      action: "全局熔断——所有 Agent 暂停写操作"
      cooldown: "Owner 手动解除"

    # ─── v0.4.0 新增熔断触发器 ───
    - trigger: "signal_noise_attack"
      condition: "L6 异常告警密度在 5 分钟内 > 历史基线 P99 * 10（噪音攻击——Agent在攻击前淹没告警系统）"
      action: "告警系统进入高敏感模式 + 所有 Agent 操作降级为 auto_guard"
      cooldown: "告警密度回归正常后自动解除"

    - trigger: "sensitivity_label_blitz"
      condition: "同一 Agent 在 60 秒内修改 >= 5 个文件的 sensitivity frontmatter 标签"
      action: "立即阻断该 Agent + 所有被修改文件的 sensitivity 锁定为修改前值"
      cooldown: "Owner 手动解除"

    - trigger: "agent_spawn_storm"
      condition: "同一父 Agent 在 5 分钟内创建 >= 3 个子 Agent"
      action: "阻断父 Agent + 立即终止所有子 Agent"
      cooldown: "Owner 手动解除"

  # ─── v0.4.0 熔断源隔离策略 ───
  isolation_policy:
    single_agent_trigger: "仅阻断触发 Agent，不全局熔断——防止恶意Agent通过制造异常来DDoS合法Agent"
    multi_agent_trigger: ">= 2 个不同 Agent 在同一时间段触发同类熔断 → 升级为全局熔断"
    degradation_attack_protection: "如果同一 Agent 触发的降级导致该Agent所在层崩溃 → 该Agent立即BLOCKED（而非降级为partial_failure放行）"

  # ─── 手动熔断（Owner 随时执行）───
  manual_triggers:
    - "全局紧急熔断——终止所有 Agent 写操作"
    - "单 Agent 熔断——终止指定 Agent 的所有操作"

  # ─── 熔断状态记录 ───
  state_persistence: "SQLite circuit_breaker_state 表（已有 GateEngine 实现）"
  audit: "每次熔断触发/解除均写入不可变审计日志"
```
