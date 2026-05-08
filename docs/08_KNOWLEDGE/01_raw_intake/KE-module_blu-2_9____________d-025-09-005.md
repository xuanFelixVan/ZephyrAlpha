---
module_id: KE-module_blu-2_9____________d-025-09-005
title: 2.9 死锁与活锁防护（决策 D-025-09）
category: module_blueprint
---

# 2.9 死锁与活锁防护（决策 D-025-09）

2.9 死锁与活锁防护（决策 D-025-09）

> **决策 D-025-09**：多 Agent 并发场景的死锁防护不是"nice to have"——DPBench 证实 3 Agent 并发时死锁率 95-100%，5 Agent 时 25-65%。必须内建四层防护：① 资源排序（Dijkstra）；② 超时熔断；③ 优先级抢占（对标 MIT CORDIAL）；④ 序列化降级模式。活锁（Agent 间无限谦让 + Mirror Mirror Loop）独立检测。
>
> **决策依据**：MIT CORDIAL 将死锁降低 87%。DPBench 关键发现——"natural language is a poor synchronization primitive"——Agent 间用自然语言协调反而增加死锁。必须用结构化协议（mutex / semaphore / FIFO queue）做同步。

```yaml
deadlock_prevention:
  # === 四层防护 ===
  layers:
    - name: "L1: Resource Ordering（Dijkstra 全局排序）"
      mechanism: "所有 Agent 获取共享资源时遵循全局排序——先 DB lock → 再 API call → 再 git push"
      enforcement: "compile-time check——Agent 代码中资源获取顺序必须是声明式且不可绕过"

    - name: "L2: Timeout-based Abort（超时熔断）"
      mechanism: "Agent 等待委托响应 > SLA（默认 120s）→ 自动取消等待 → 触发补偿策略（§2.2）"
      compensation:
        - "retry_with_backoff: 指数退避重试 1s→2s→4s→8s，最多 3 次"
        - "fallback_delegate: 目标 Agent 不可用 → 委托给次优匹配"
        - "task_split: 任务过大 → 拆分为更小子任务"

    - name: "L3: Priority Preemption（优先级抢占 — 对标 MIT CORDIAL）"
      mechanism: "当资源等待图检测到环时 → 优先级最高的 Agent 保留资源，其余强制回退"
      priority_formula: "task_priority × 0.4 + agent_capability_score × 0.3 + wait_time_penalty × 0.3"

    - name: "L4: Sequentialization Fallback（序列化降级）"
      mechanism: "死锁率 > 10%（最近 100 次委托）→ 系统从并发模式切换为序列化模式"
      recovery: "死锁率降至 < 2% 后自动恢复并发模式"

  # === 死锁检测机制 ===
  detection:
    wait_for_graph: "维护全局资源等待图（每个资源当前持有者 + 等待者列表）——对标 OS 死锁检测"
    cycle_detection: "每次委托操作前检测——按 DFS 遍历等待图"
    detection_interval: "每次委托操作前 + 每 30s 全局扫描"
