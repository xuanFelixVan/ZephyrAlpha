---
module_id: KE-module_blu-2_22______________d-025-19-000
title: 2.22 工作窃取与负载均衡（决策 D-025-19）
category: module_blueprint
---

# 2.22 工作窃取与负载均衡（决策 D-025-19）

2.22 工作窃取与负载均衡（决策 D-025-19）

> **新增于 v0.7.0**。v0.6.0 的任务分发是 Coordinator push 模式。在成熟的分布式系统中，"work stealing"（空闲节点从忙碌节点"偷"任务）是标准的负载均衡补充策略，在多 Agent 系统中完全适用。

**对标**：Adaptive Async Work-Stealing（分布式计算经典）+ 社区多 Agent 负载均衡实现（贪心算法 + RL-based）。

```yaml
work_stealing_and_load_balancing:

  design_principle: "Coordinator push + Agent pull (work stealing) = 双向负载均衡"

  # === 工作窃取协议 ===
  work_stealing:
    trigger:
      - "Agent 状态 = IDLE 持续 30s"
      - "Agent 自身的 queue_depth = 0"

    victim_selection:  # 选谁的队列来"偷"
      criteria:
        - "queue_depth 最深的 Agent（优先级最高）"
        - "任务优先级匹配（只偷优先级 >= medium 的任务）"
        - "跳过已经分配给其他 Agent 的任务"

    stealable_task:  # 什么任务可以被偷
      conditions:
        - "任务状态 = PENDING（还未开始执行）"
        - "任务无 Agent 亲和性限制"
        - "任务可以被安全地重分配到不同的 worktree"

    limits:
      max_steals_per_hour: 5  # 防止"偷"本身带来不稳定
      cooldown_after_steal: 120  # 秒——偷完后冷却 2 分钟

  # === 任务亲和性 ===
  task_affinity:
    concept: "Agent 已经加载了相关上下文 → 分配给它比给冷启动的 Agent 更高效"
    calculation:
      affinity_score = (
        0.4 * file_familiarity     # 该 Agent 最近 24h 操作过的文件
        + 0.3 * module_familiarity  # 该 Agent 最近操作过的模块
        + 0.3 * task_type_match     # 该 Agent 擅长的任务类型
      )
    routing: "task_affinity > 0.6 → 优先分配给该 Agent，即使其队列稍长"

  # === Agent Watchdog（进程级守护） ===
  watchdog:
    problem: "Agent 执行长任务时进程可能 OOM/超时/挂死"
    mechanism:
      heartbeat: "每 30s Agent 向 Coordinator 发送心跳 (status + progress%)"
      timeout:
        default: "10min"          # 超时后 Coordinator 尝试恢复
        long_running: "30min"     # 声明为 long_running 的任务有更长超时
      recovery:
        attempt_1: "Coordinator 发送 PING（轻量级检查 Agent 是否存活）"
        attempt_2: "从最近的检查点恢复（§2.18 checkpoint.recovery）"
        attempt_3: "标记任务 FAILED → 重新分配给其他 Agent"
      oom_protection:
        - "Agent 定期检查可用内存，低于 500MB → 主动暂停新任务"
        - "已接任务在当前子任务完成后自愿 yield 给其他 Agent"

  # === 1人+AI 简化 ===
  simplified_for_solo:
    note: "完整的 pull-based work stealing 在 <5 Agent 场景下可能过度工程化"
    recommendation: "Phase 1 实现简化版——仅 Task Affinity + Watchdog。Work Stealing 在 Agent >= 5 时启用。"
```

---
