---
module_id: KE-1913---------action-history-wit-003
status: active
title: 2.5 动作历史与去重（Action History with Dedup）
category: module_blueprint
ttl: permanent
---

# 2.5 动作历史与去重（Action History with Dedup）

2.5 动作历史与去重（Action History with Dedup）

> **决策 D-024-06（v0.5.0 修订）**：简单指纹匹配→结构化动作历史 + 签名去重。Stanford/MIT 论文 (2026.4) 发现 50% 的高成本运行中的文件读写是重复的——不是传统意义上的"循环"（参数不同但结果等价），需要更智能的检测。TokenFence 和 AgentGuard 均采用 action-level dedup 而非 fingerprint matching。

```yaml
action_history:
  description: "记录每个 Agent Action 的签名——不是简单的 fingerprint，而是结构化的 action 语义指纹"
  storage: "环形缓冲区——保留最近 50 个 action"

  action_signature:
    fields:
      - "tool_name"
      - "tool_params_hash"           # 参数哈希
      - "tool_params_semantic_hash"  # v0.5.0 新增：语义等价参数哈希（文件名换但逻辑相同→同一签名）
      - "output_effect_hash"         # v0.5.0 新增：输出副作用哈希（读/写了哪些行/文件）
      - "timestamp"
      - "cost_incurred"

  dedup_rules:
    identical_action_3x:
      threshold: 3                   # 完全相同的 action 连续 3 次
      action: "WARN + 写入 budget_enforcer_loop_events"
      auto: true

    identical_action_5x:
      threshold: 5
      action: "BLOCK——拒绝执行 + 返回 '检测到重复动作循环: {action_signature}'"
      auto: true

    # ── v0.5.0 新增：输出无差异去重 ──
    no_effect_chain:
      description: "连续 N 个 action 对输出无任何差异——修改了文件但 diff 为空的无效操作"
      threshold: 3
      action: "WARN '检测到无效果动作链——建议跳过后续同类操作'"

    # ── v0.5.0 新增：自修复螺旋检测 ──
    self_correction_spiral:
      description: "Agent 连续修改同一段代码→新增 bug→再修改→再新增 bug——自修复成本螺旋"
      detection: "同一文件同一区域被修改 > 5 次且每次修改后 lint error_count > previous"
      threshold: 5
      action: "HALT——系统介入 '检测到自修复螺旋——建议人工介入后重新开始'"
      auto: true

    semantic_duplicate_10x:
      threshold: 10
      action: "TRIGGER_KILL_SWITCH——疑似 runaway agent"
      auto: true
      trigger_kill_switch: true

  # 指纹过期
  action_ttl: 300                     # 5 分钟窗口（仅统计窗口内 action）
```
