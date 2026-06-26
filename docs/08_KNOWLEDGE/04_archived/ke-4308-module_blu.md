---
module_id: KE-4149
title: 第四轮 — 前沿安全（#56-#70+）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 第四轮 — 前沿安全（#56-#70+）

第四轮 — 前沿安全（#56-#70+）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 56 | Prompt Injection 通过 A2A 跨 Agent 传播 | 🔴 P0 | OWASP ASI01 + EchoLeak CVE-2025-32711 | §2.10 owasp_coverage |
| 57 | Agent 冒充（naming collision） | 🔴 P0 | OWASP ASI03 | §2.10 identity_verification |
| 58 | 消息重放攻击 | 🔴 P0 | Network replay classic | §2.10 replay_protection |
| 59 | Agent Card 篡改 | 🔴 P0 | — | §2.2 card_integrity |
| 60 | 委托链中的权限泄露 | 🔴 P0 | OWASP ASI03 privilege escalation | §2.10 owasp_coverage |
| 61 | 跨协议攻击（MCP + A2A 组合利用） | 🟠 P1 | Cross-Protocol Interaction Risks | Phase beta |
| 62 | 仲裁规则被 AI 弱化 | 🔴 P0 | MOD-INF-022 §2.5 不可变性 | §2.8 + D-025-11 |
| 63 | 上下文包中的"隐藏指令" | 🟠 P1 | Indirect Prompt Injection | §2.11 context_poisoning |
| 64 | 模态原生路由的安全性（MMA2A 启发） | 🟡 P2 | MMA2A §2.3 | §2.4 Part types |
| 65 | OWASP ASI09 Human-Agent Trust Exploitation | 🟠 P1 | Human in A2A loop | §2.8 block tier |
| 66 | Agent 心跳伪造 | 🟡 P2 | — | §2.10 identity_verification |
| 67 | 系统时间操纵绕过 TTL | 🟡 P2 | Time-of-check time-of-use | §2.11 freshness |
| 68 | AI 生成的安全测试"恰好"绕过了自己留的后门 | 🟡 P2 | Harvard AI 识别安全测试研究 | §2.14 security_tests |
| 69 | 仲裁日志被篡改 | 🟡 P2 | — | MOD-INF-020 audit |
| 70 | Agent Card 能力声明与实际能力不一致（Capability Drift） | 🟠 P1 | — | §2.2 card_integrity |
| 71 | "1 人+多 IDE"场景下 IDE 崩溃后 Agent 状态恢复 | 🟡 P2 | — | §2.13 Dead Letter Queue |
