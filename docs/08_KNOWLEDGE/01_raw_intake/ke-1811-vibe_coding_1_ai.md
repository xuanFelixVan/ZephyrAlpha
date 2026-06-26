---
module_id: KE-1720---1--ai-------005
status: active
title: 2.15 Vibe Coding / 1人+AI 专属优化（决策 D-025-12）
category: module_blueprint
ttl: permanent
---

# 2.15 Vibe Coding / 1人+AI 专属优化（决策 D-025-12）

2.15 Vibe Coding / 1人+AI 专属优化（决策 D-025-12）

> **决策 D-025-12**：在当前（及可预见的）1人+AI 维护语境下，A2A 协议做以下专属优化——这些优化在企业级多 Agent 系统中可能是"反模式"，但在个人 Vibe Coding 场景下是"最优解"。
>
> **决策依据**：1人+AI 场景的三重特殊性——① 单 Owner 意味着无多租户隔离需求，简化但安全不可退让；② 100% AI 施工意味着自指悖论是真实威胁（非学术假设）；③ 10+ 并发对话 + 3 IDE 意味着即使"单 Agent"，跨会话上下文一致性已是真实痛点。

```yaml
vibe_coding_optimizations:
  # === 优化 1：发现入口 = AGENTS.md ===
  discovery_entry:
    mechanism: "AGENTS.md 中 a2a_agents: 字段"
    not: "独立的 well-known URI 或 Consul/etcd 服务发现"
    reason: "TRAE/Cursor/RooCode 都读 AGENTS.md——减少 1 个需要维护的配置文件"

  # === 优化 2：消息格式 = YAML ===
  message_format:
    format: "YAML（Pydantic 校验 + 人类可读）"
    not: "JSON-RPC 2.0（Google A2A 默认）"
    reason: "1人维护需要能肉眼看懂 Agent 间的通信——社区调试地狱的根本原因就是日志不可读"

  # === 优化 3：Coordinator = 规则驱动 ===
  coordinator_implementation:
    type: "Rule Engine（Python if-else + YAML config）"
    not: "LLM Agent（Anthropic Team Lead 模式）"
    reason: "① 零 Token 成本——经济护栏的硬需求；② 确定性——不会被 prompt 操纵；③ 轻量——个人场景不需要 K8s 级别的调度器"

  # === 优化 4：冲突预防 > 冲突解决 ===
  conflict_priority:
    order:
      - "1. Living Spec 同步（事前——Agent 开工前对齐接口）"
      - "2. spec-scoped 任务分解（事中——Coordinator 确保子任务互不重叠）"
      - "3. git worktree 隔离（事中——Agent 在独立 worktree 中操作）"
      - "4. 语义冲突检测（事后——发现并裁决）"
    not: "单一的 git merge conflict（事后、仅文本）"

  # === 优化 5：最小化的元数据开销 ===
  metadata_minimization:
    rule: "Agent Card 只包含"分配任务所必需"的字段——跳过 Google A2A 中的 provider URL / license / documentation URL 等企业元数据"
    rationale: "1人场景下，Agent 提供者只有一个（你自己），不需要企业级元数据"

  # === 优化 6：与已有基础设施对齐 ===
  infrastructure_alignment:
    - target: "KBG-0032 AgentOrchestrator"
      alignment: "A2A Coordinator 复用 AgentRouter 的 6 角色 × 10 域矩阵做能力匹配"
      not: "重复实现在 KBG-0017 中已有的 TaskState——A2A Task 是 Agent-间粒度"

    - target: "MOD-INF-019 Skill Pack"
      alignment: "Agent Card capabilities 自动从 Skill Pack 的 trigger_keywords 派生"
      not: "手动维护两套能力描述"
```

---
