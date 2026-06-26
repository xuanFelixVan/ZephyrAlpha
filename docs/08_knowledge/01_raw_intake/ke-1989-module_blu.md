---
module_id: KE-1898
status: active
title: 2.4 六级自适应降级链
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.4 六级自适应降级链

2.4 六级自适应降级链

> **决策 D-024-05（v0.4.0 修订）**：新增 L1.5 沉没成本干预——当 Cost-to-Completion Ratio 异常时主动建议放弃。新增预算耗尽用户沟通协议。

```yaml
degradation_strategy:
  level_0_notify:
    trigger: "session_budget_used > 50% OR burn_rate_1h > 3× normal"
    action: "INFO 日志 + 会话内显示剩余预算 + 建议 /compact 时机"
    auto: true
    visualization: "终端显示 '💰 预算: 4,200/8,000 tokens (52.5%)'"

  level_1_warning:
    trigger: "预算使用 > 70% OR 单轮 Turn soft_limit 接近"
    action: "WARNING 日志 + 通知附录建议减少上下文 + 标记当前任务为 'budget_watch'"
    auto: true

  # ── v0.4.0 新增：沉没成本干预 ──
  level_1_5_sunk_cost_warn:
    trigger: "cost_to_completion_ratio > 3× AND 任务产出 < 20%"
    action: "主动告警 '预算已消耗 80% 但产出仅 10%——建议放弃当前任务，重启更有效'"
    auto: true
    rationale: "再试一次就好了 是成本超支的核心心理陷阱——系统必须主动干预"
    cost_to_completion_ratio: "budget_consumed_ratio / output_completion_ratio"

  level_2_model_switch:
    trigger: "预算使用 > 80% OR 单次调用预估成本 > $0.50"
    action: "自动降级到 Tier-1 模型——这是成本最低且效果最好的降级手段"
    auto: true
    priority: "最高——在压缩上下文之前执行"

  level_3_compress:
    trigger: "预算使用 > 85%"
    action: "强制压缩上下文——DocCompressor aggressive 模式"
    auto: true
    integration: "Context Engine (MOD-CONTEXT_ENGINE)"

  level_4_minimal:
    trigger: "预算使用 > 95%"
    action: "最小上下文——仅保留 AGENTS.md + 当前蓝图 §3"
    auto: true

  level_5_halt:
    trigger: "预算使用 > 100%（hard_limit）"
    action: "硬停止——仅允许只读操作 + 审计告警"
    auto: true
    audit_level: "ProvenanceStandard"
    # ── v0.4.0 新增：预算耗尽用户沟通协议 ──
    user_communication:
      template: >
        ⚠️ 预算已耗尽（{level}: {used}/{limit} tokens）。
        当前任务的已完成部分已保存至 {output_path}。
        建议：1) 等待下周预算重置  2) 使用 `--override-budget` 临时提额
        诊断命令：`zephyr budget status --detail`
      fallback_action: "自动保存当前进度 + 生成 resume checkpoint"

  level_6_kill_switch:
    trigger: "单日成本 > $100 OR 连续 5 个请求被 DENY OR 检测到 runaway loop"
    action: "全局熔断——所有 AI 调用暂停，保留修复通道（允许 Owner 执行诊断命令）"
    auto: true
    integration: "Capacity Assurance Kill Switch (MOD-INF-001)"
    recovery: "熔断后 30 分钟自动尝试解除 + Owner 手动解除"

  # ── 成本感知自动回升 ──
  auto_recovery:
    enabled: true
    rules:
      - condition: "连续 3 个请求 burn_rate_10min < 1× normal AND budget_used < soft_limit × 0.6"
        action: "回升一级（L4→L3, L3→L2, L2→L1, L1.5→L1）"
        max_recovery: "L1"        # 不自动回到 L0（需要新的会话）
      - condition: "新会话开始"
        action: "完全重置到 L0"
    anti_spiral:
      max_degradation_per_minute: 1
      recovery_cooldown: 180
```

```yaml
