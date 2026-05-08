---
module_id: KE-module_blu-2_18________saga_______d-025-1-000
title: 2.18 分布式事务与 Saga 回滚（决策 D-025-15）
category: module_blueprint
---

# 2.18 分布式事务与 Saga 回滚（决策 D-025-15）

2.18 分布式事务与 Saga 回滚（决策 D-025-15）

> **新增于 v0.6.0**。v0.5.0 假设 Agent 操作是原子的——一个 Task 要么成功要么失败。实际上，Agent A 的操作会影响后续 Agent B 的状态。如果 Agent C 失败了，A 和 B 已提交的工作需要回滚。这是经典的分布式事务问题。

**对标**：SagaLLM (Stanford, PVLDB 2025 — 多 Agent 工作流的形式化事务与回滚)、LangChain Compensation v0.5.8 (Saga Pattern for Agents)、Saga 设计模式（每步 LT 配一个 CT）。

```yaml
saga_and_rollback:

  # === Saga 事务注册模型 ===
  saga_registration:
    principle: "每个 Agent 操作在提交前必须注册对应的补偿事务 (CT)"
    format:
      logical_transaction:        # LT = 业务操作
        agent_id: "Architect"
        action: "design_database_schema"
        target: "docs/schema_v2.sql"
      compensation_transaction:  # CT = 回滚操作
        agent_id: "Architect"
        action: "revert_database_schema_to_v1"
        target: "docs/schema_v1.sql"  # 基线快照
      idempotency_key: "saga_20260505_schema_v2_uuid"  # 保证 CT 幂等

    compensation_type:
      undo: "反转操作——git revert / db rollback"
      compensate: "替代操作——不撤销原操作但做补充纠正"
      notify: "通知下游——上游回滚了，下游需要知道"

  # === 分布式检查点 ===
  checkpoint:
    granularity: "per agent——每个 Agent 在自己的 worktree 中有独立检查点"
    content: "worktree snapshot + Agent internal state（conversation summary + 已完成子任务列表）"
    coordination: "Coordinator 持有全局检查点目录——track 所有 Agent 的检查点位置"

    recovery:
      partial_failure: "Agent C 执行 50% 后崩溃 → 从最近的检查点恢复，不重做已完成步骤"
      full_rollback: "Agent D 失败 → A/B/C/D 全部回滚到基线 → 检查点回退链"

  # === 幂等性门禁 ===
  idempotency_gate:
    layer_1: "Task-level——同一 Task ID 在 5min 内重复提交 → rejected（去重）"
    layer_2: "Operation-level——同一文件 + 同一操作类型在 10min 内重复执行 → rejected"
    layer_3: "Git-level——检查目标文件 hash 是否一致，不一致 → abort"

  # === 1人+AI 简化实现策略 ===
  simplified_implementation:
    note: "Saga 的完整形式（LT/CT 配对 + 检查点 + 幂等性门禁 + 补偿编排）对于 1人+AI 场景过重。"
    simplifications:
      - "利用 git revert / git reset 作为天然的 rollback 机制"
      - "Agent worktree 隔离（v0.5.0 优化 3）天然提供检查点"
      - "幂等性通过 git 天然提供——同一 commit 重复 apply → no-op"
    recommendation: "Phase 1 使用简化版（git revert + Agent Card 操作日志），Phase 5+ 升级到完整 Saga。"
```

---
