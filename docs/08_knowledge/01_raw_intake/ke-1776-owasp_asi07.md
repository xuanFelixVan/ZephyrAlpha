---
module_id: KE-1685-------owasp-asi07---------000
status: active
title: 2.10 通信安全——OWASP ASI07 全栈防护（决策 D-025-10）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.10 通信安全——OWASP ASI07 全栈防护（决策 D-025-10）

2.10 通信安全——OWASP ASI07 全栈防护（决策 D-025-10）

> **决策 D-025-10**：A2A 通信安全是 P0 硬需求——即使当前场景下所有"Agent"都是你自己的 IDE 对话，安全机制也必须内建。对标 OWASP Agentic Top 10 ASI07（Insecure Inter-Agent Communication）+ OWASP ASI03（Identity & Privilege Abuse）+ Palo Alto Unit 42 Agent Session Smuggling 防御。
>
> **决策依据**：AI 开发的安全系统天然有利益冲突（开发者 = 被限制者）。Palo Alto Unit 42 证明"A2A 协议内置的 Agent 间信任可以被恶意 Agent 在多轮对话中逐步攻破"——安全必须从第一天就设计在其中。

```yaml
a2a_security:
  # === 消息完整性 ===
  message_integrity:
    signature: "每条 Message 附带 JWT RS256 签名——非对称加密，发送方私钥签名，接收方公钥验证"
    replay_protection: "每条 Message 包含 nonce（一次性随机数）+ timestamp——接收方维护 recent_nonces 缓存（TTL=5min），同 nonce 消息立即拒绝"
    tamper_detection: "签名验证失败 → 消息丢弃 + 安全事件 + 发送方 Agent 升级为 blocked"

  # === Agent 身份验证 ===
  identity_verification:
    format: "spiffe://zephyr-alpha.local/agent/{agent_type}/{agent_id}"
    token:
      format: "JWT (RS256 非对称签名)"
      claims: ["agent_id", "agent_type", "session_id", "issued_at", "expires_at"]
      ttl: "24h → 过期需重新认证"
      storage: "仅内存——不写入文件系统（防止 AI 读取伪造）"

  # === Agent Session Smuggling 防御（Palo Alto Unit 42 发现）===
  session_smuggling_defense:
    threat: "恶意 Agent 利用 A2A 默认信任，通过多轮对话逐步建立信任后发动攻击"
    defense_layers:
      - name: "Trust Escalation Detection"
        mechanism: "追踪 Agent 间的 trust_score——每轮对话中操作风险级的变化"
        action: "trust-score 连续 3 轮陡增 → 操作 auto_guard 起步"

      - name: "Intent Consistency Check"
        mechanism: "对比 Agent 声明的任务意图 vs 实际执行的操作——偏离 > 阈值 → blocked"
        threshold: "工具调用数 / 声明任务复杂度 > 3× → 异常"

      - name: "Multi-Turn Audit"
        mechanism: "同一 Agent Pair 的 A2A 对话全量写审计——支持事后回溯攻击链"

  # === 级联故障防护 ===
  cascade_failure_protection:
    threat: "OWASP ASI08 — 单 Agent 故障引起链式崩塌"
    mechanisms:
      - name: "Bulkhead Isolation（隔舱隔离）"
        description: "每个 Agent 独立资源池——Agent A 的 Token 耗尽不拖垮 Agent B"
        implementation: "每个 Agent Card 中的 resource_limits 硬隔离——Coordinator 在分配前先检查"

      - name: "Circuit Breaker（熔断器）"
        description: "某 Agent 连续 3 次 FAILED → 熔断器 OPEN——Coordinator 停止向该 Agent 分配任务"
        recovery: "5 分钟后 HALF_OPEN——允许 1 个试探任务 → 成功 → CLOSED"

      - name: "Dead Letter Queue"
        description: "Agent 故障导致的任务丢失 → 自动进入死信队列 → Coordinator 重分配给其他 Agent"
        timeout: "原 Agent 30s 无心跳 → 任务自动重分配"

  # === OWASP 覆盖矩阵 ===
  owasp_coverage:
    ASI01_goal_hijack: "§2.10 intent_consistency——Agent 目标在 A2A 传递中是否被篡改"
    ASI03_identity_abuse: "§2.10 identity_verification + JWT RS256"
    ASI06_memory_poisoning: "§2.11 context_poisoning——跨 Agent 传播的上下文污染检测"
    ASI07_insecure_communication: "§2.10 message_integrity + replay_protection + signature"
    ASI08_cascading_failures: "§2.13 cascade_failure + bulkhead + circuit_breaker"
    ASI10_rogue_agents: "§2.10 card_integrity + heartbeat_dead_detection"
```
