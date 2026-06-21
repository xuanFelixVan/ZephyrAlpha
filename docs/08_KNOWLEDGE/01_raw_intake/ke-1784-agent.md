---
module_id: KE-1693----------agent-002
status: active
title: 2.11 上下文管理——跨 Agent 传递
category: module_blueprint
---

# 2.11 上下文管理——跨 Agent 传递

2.11 上下文管理——跨 Agent 传递

> **对标**：MOD-INF-022 §2.8 委托上下文包 + KBG-0041 §4.3 P0-P3 压缩策略。

```yaml
context_management:
  # === 上下文传递策略 ===
  propagation:
    full_context: "传递完整的 HandoffPackage 8 字段——仅限委托深度=1 的首轮"
    compressed: "传递 ≤ 500 tokens 摘要（LLM 压缩）——用于委托深度 ≥ 2"
    reference_only: "仅传递 task_id + storage_path——接收方自行拉取"

  # === 上下文新鲜度 ===
  freshness:
    ttl: "共享知识 TTL = 当日会话内有效——跨天需重新验证"
    staleness_check: "Agent 消费上下文前检查 timestamp——过期 > TTL → 丢弃 + 向 Coordinator 请求最新版"

  # === 上下文污染检测 ===
  poisoning_defense:
    threat: "OWASP ASI06 — 被污染的上下文从一个 Agent 传播到另一个"
    detection: "Agent 产出物 vs 上下文声称的事实——一致性校验"
    example: "Agent A 声称 'module X 使用 SQLite'，Agent B 实际运行时发现 X 使用 PostgreSQL → 标记上下文异常"

  # === 上下文溯源 ===
  provenance:
    tracking: "每个上下文条目附带 origin_agent_id + evidence_path + generated_at"
    chain: "上下文→决策→产出的全链路溯源——对标 MOD-INF-022 §2.15 反谄媚"
```
