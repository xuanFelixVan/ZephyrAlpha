---
module_id: KE-1886-------------agent---------008
status: active
title: 2.33 选择性遗忘与被遗忘权——Agent 记忆删除协议（决策 D-025-30）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.33 选择性遗忘与被遗忘权——Agent 记忆删除协议（决策 D-025-30）

2.33 选择性遗忘与被遗忘权——Agent 记忆删除协议（决策 D-025-30）

> **新增于 v0.9.0**。v0.8.0 §2.28 有上下文腐烂防护（主动压缩 + ACON 失败驱动优化 + 三层上下文架构），但那是"遗忘无用信息以提升推理质量"——缺少法律驱动的选择性遗忘："从 Agent 记忆中删除用户 X 的所有信息"。EU AI Act 2026 将机器遗忘作为强制执行要求（违规=7% 全球营收），被遗忘权不再是可选功能——是合规底线。

**对标**：FSFM (arXiv:2604.20300, 2026-04 — 生物启发的选择性遗忘: 100% 消除安全风险, +29.2% 信噪比, +8.49% 访问效率, 4 类遗忘分类学）、EU AI Act 2026 (machine unlearning 强制执行, 7% 全球营收罚款）、SISA/Gradient Scrubbing/Influence Functions/Differential Privacy (经典机器遗忘技术）。

```yaml
agent_forgetting:

  design_principle: "'遗忘'不能只是删除文件——因为 Agent 的推理权重和上下文记忆已经吸收了信息。需要在 Agent memory layer (RAG 索引 + Vector Store + context_history) 层面做 targeted removal，同时保证遗忘后 Agent 功能的完整性。"

  # === FSFM 四类遗忘分类学 ===
  forgetting_taxonomy:
    passive_decay:
      concept: "时间驱动的自然衰减——低价值信息随 TTL 过期自动忘记"
      implementation: "§2.28 context_rot 已覆盖 (TTL + staleness_score)"
      analogy: "人类自然遗忘——不是删除，是不再检索"

    active_deletion:
      concept: "法律/合规驱动的精确删除——'删除所有关于 user_id=X 的数据'"
      trigger: "GDPR Article 17 RTBF request / EU AI Act unlearning mandate"
      implementation:
        - "在 RAG 索引中搜索所有含 user_id=X 的 chunk → 删除"
        - "在 conversation_history 中搜索所有含 user_id=X 的消息 → 删除"
        - "重建受影响的 vector embeddings (删除后需要重新索引)"
      verification: "pre-delete/post-delete 对比: 0 条含 user_id=X 的记录"

    safety_triggered:
      concept: "安全驱动的紧急遗忘——Agent 被 prompt injection 污染时，精准切除恶意指令"
      trigger: "OWASP ASI01 detection (Prompt Injection) + anomaly_score > 0.9"
      implementation:
        - "定位 contaminated message 在对话史中的位置"
        - "从此消息到 current_message 的完整链路 → 标记为 CONTAMINATED_ZONE"
        - "切除 CONTAMINATED_ZONE 而不是重置整个 Session"
        - "从最近的 clean checkpoint 重新加载 + 注入'以下安全事件已发生，已切除...'说明"
      analogy: "手术切除——精准切除肿瘤，不截肢"
      origin: "FSFM: 100% 安全风险消除, safety-triggered forgetting"

    adaptive_reinforcement:
      concept: "不遗忘——反而强化。重要决策/关键教训 → 永久保留"
      implementation: "§2.28 三层上下文的 Cold Memory (ADR + key decisions)"
      analogy: "不会忘记怎么骑自行车"

  # === 跨 Agent 遗忘一致性协议 ===
  cross_agent_forgetting:
    problem: "Agent A 被要求忘记 user X 的数据 → 但 Agent B/C/D 之前从 A 获取过 user X 的数据→数据残留。"
    protocol: "Cascading Forget Notification"
    steps:
      - "1. Agent A 执行 active_deletion → 完成后生成 ForgetNotice {subject: user_X, forget_id: uuid, timestamp}"
      - "2. Coordinator 广播 ForgetNotice 到所有曾与 Agent A 有过 user_X 相关 task 交互的 Agent"
      - "3. 每个接收 Agent 检查自己的 memory → 如有 user_X 数据 → 执行 active_deletion"
      - "4. 所有 Agent 完成后 → Coordinator 生成 ForgetCompletionReport → 审计日志"
    verification: "Coordinator 对所有 Agent 做 spot check: 'search for user_X in your memory'"

  # === 遗忘 vs 知识保留的平衡 ===
  forgetting_balance:
    problem: "Agent 从 user_X 的代码中学到的通用编程模式 (与 user_X 个人数据无关) → 不能一并删除"
    solution: "Two-Pass Deletion:"
    pass_1_identify_pii:
      - "正则匹配: email/phone/API key/password/token/IP address/真实姓名"
      - "NER 实体识别: PERSON/ORG/GPE 等"
      - "上述匹配到的 → active_deletion"
    pass_2_anonymize_pattern:
      - "user_X 的代码风格偏好 (如 brace_style=KR, indent=4) → 匿名化为
