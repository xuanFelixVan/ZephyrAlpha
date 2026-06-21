---
module_id: KE-1851
status: active
title: 2.29 故障模式规范 + 冷启动反滥用 + 对抗测试
category: module_blueprint
---

# 2.29 故障模式规范 + 冷启动反滥用 + 对抗测试

2.29 故障模式规范 + 冷启动反滥用 + 对抗测试

> **决策 D-024-27（🆕 v0.7.0）**：Budget Enforcer 自身崩溃时，系统应 fail-open（允许所有→成本失控）还是 fail-closed（拒绝所有→系统瘫痪）？前 6 轮从未定义。

```yaml
fail_mode_specification:
  description: "Budget Enforcer 在每个 level 的故障模式——并非一刀切 fail-open 或 fail-closed"

  per_level_fail_mode:
    l0_request: "fail-closed"     # 单次请求故障→拒绝该请求（影响最小）
    l1_turn: "fail-closed"        # 单轮故障→拒绝该轮（用户可重试）
    l2_task: "fail-closed"        # 任务级故障→拒绝任务（拆分或重试）
    l3_session: "fail-open限流"   # Session 故障→允许调用但限制在 tier_0_free + 1/10 上限
    l3_5_workflow: "fail-open限流"# Workflow 故障→同上
    l4_global: "fail-closed"      # 全局故障→硬拒绝（安全优先于可用性）
    l4_5_self: "fail-open限流"    # Self-Budget 故障→降级为仅统计不阻断

  fail_mode_recovery:
    heartbeat: "每 30s 检查各组件健康——连续 3 次 heartbeat 失败触发对应 fail_mode"
    auto_recovery: "组件恢复后自动从 fail_mode 恢复正常模式"
