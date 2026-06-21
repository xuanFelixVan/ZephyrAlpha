---
module_id: KE-1687--------agent-000
status: active
title: 2.10 Budget Pool 弹性共享 + Agent 子池隔离
category: module_blueprint
---

# 2.10 Budget Pool 弹性共享 + Agent 子池隔离

2.10 Budget Pool 弹性共享 + Agent 子池隔离

```yaml
budget_pool:
  description: "Session 内多个 Task 之间弹性共享预算——不是固定切分"
  strategy: "adaptive_weighted"

  initial_allocation:
    method: "complexity_weighted"
    reserve_buffer: 0.15        # 保留 15% 作为合成缓冲区（解决 multi-agent synthesis 的额外消耗）

  dynamic_rebalance:
    trigger: "任一 Task 消耗 > 80% 且存在其他 Task < 40%"
    action: "从低消耗 Task 转移 20% 预算到高消耗 Task"
    max_transfer_per_hour: 2    # 防止频繁震荡

  cross_session_borrow:
    enabled: false               # Solo maintainer 下跨会话借用无意义，Session 粒度已足够

  # ── v0.5.0 新增：跨 Session 预算储蓄 ──
  cross_session_savings:
    description: "轻量 Session 未用完的预算自动储蓄到下周——不是借用，是储蓄"
    bank_rate: 0.30              # 节约的 30% 进入储蓄池（其余回归全局 pool）
    max_savings: "20% * global_weekly_budget"  # 储蓄池上限
    usage: "储蓄池仅在全局预算紧张时（global_used > 80%）自动释放"
    visual: "终端显示 '🏦 储蓄池: 12.5K tokens (可救急)'"

  # ── v0.4.0 新增：Agent 级子池隔离 ──
  per_agent_sub_pool:
    description: "多 Agent 场景下，每个 Agent（或 Agent 类别）有独立子池——防止一个失控 Agent 烧掉所有预算"
    isolation_level: "soft"      # soft=子池用尽可从全局池借用, hard=子池用尽即 halt
    default_sub_pool_ratio: 0.25 # 默认每个 Agent 最多占全局预算的 25%
    categories:
      - name: "code_generation"
        max_share: 0.50          # 代码生成 Agent（群）最多占 50%
        agents: ["code-generator", "refactoring-agent"]
      - name: "analysis"
        max_share: 0.30          # 分析类 Agent 最多占 30%
        agents: ["blueprint-analyzer", "roi-calculator", "audit-agent"]
      - name: "operations"
        max_share: 0.20          # 运维类 Agent 最多占 20%
        agents: ["linter", "formatter", "test-runner"]
    spillover:
      enabled: true               # 子池外溢允许从全局池借用
      limit: "2× sub_pool"       # 最多借 2 倍子池额度
    alert: "任一 Agent 消耗 > 子池 80% → L1_warning"
