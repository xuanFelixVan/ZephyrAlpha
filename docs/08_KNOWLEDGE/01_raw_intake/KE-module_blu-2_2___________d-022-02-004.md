---
module_id: KE-module_blu-2_2___________d-022-02-004
title: 2.2 自动委托协议（决策 D-022-02）
category: module_blueprint
---

# 2.2 自动委托协议（决策 D-022-02）

2.2 自动委托协议（决策 D-022-02）

> **决策 D-022-02**：委托由能力自动匹配，不依赖人工指定。当 Agent 不具备某项能力时，自动委托给具备该能力的 Skill Pack（架构师/实现者/治理员）。**新增四级安全约束——自委托禁止、循环检测、深度上限、SLA超时**。
>
> **决策依据**：1人+AI场景，委托应该是自动的能力匹配，不是人工的任务分配。对标 K8s scheduler 自动调度 + Filter/Score 两阶段匹配。但多Agent并发场景下 25-95% 会产生死锁（DPBench/MIT 研究），安全约束不是可选项。

```yaml
delegation_rules:
  # === 委托触发规则 ===
  capability_mismatch:
    trigger: "当前 Skill Pack 不覆盖所需能力"
    action: "自动切换到覆盖该能力的 Skill Pack"
    example: "实现者 Skill Pack 遇到架构设计任务 → 自动委托给架构师 Skill Pack"

  capacity_exceeded:
    trigger: "当前对话 token 预算超限"
    action: "将剩余子任务 + 上下文包委托给新对话"
    context_package: "§2.8 委托上下文包（7必填字段）"

  specialist_required:
    trigger: "任务涉及安全/合规/审计"
    action: "自动委托给治理员 Skill Pack"

  confidence_low:
    trigger: "Agent 对决策置信度 < 阈值（默认 0.7）"
    action: "委托给更高能力的 Skill Pack 复核"

  # === 四级安全约束（硬阻断，不可绕过） ===
  safety_constraints:
    - id: "DEL-SAFE-001"
      rule: "自委托禁止"
      check: "target_agent != current_agent"
      violation_action: "硬拒绝 + 审计记录"

    - id: "DEL-SAFE-002"
      rule: "循环委托检测"
      check: "target_agent not in delegation_chain"
      violation_action: "硬拒绝 + 审计告警 + 通知Owner"

    - id: "DEL-SAFE-003"
      rule: "委托深度上限"
      check: "len(delegation_chain) <= max_depth (default=3)"
      violation_action: "硬拒绝 + 当前Agent降级处理（拆分/上报）"

    - id: "DEL-SAFE-004"
      rule: "SLA超时熔断"
      check: "delegation_wait_time <= timeout (default=120s)"
      violation_action: "取消委托 + 启动补偿策略"

  # === 委托失败补偿策略 ===
  compensation_strategies:
    retry_with_backoff:
      when: "超时"
      strategy: "指数退避重试（1s→2s→4s→8s），最多3次"
    fallback_delegate:
      when: "目标Agent不可用"
      strategy: "委托给次优匹配的 Skill Pack"
    task_split:
      when: "任务过大导致超时"
      strategy: "拆分为更小子任务，逐一委托"
    final_escalate:
      when: "所有补偿策略耗尽"
      strategy: "升级为 blocked + 通知Owner"

```
