---
module_id: KE-module_blu-2_28____________d-025-25-001
title: 2.28 上下文腐烂防护（决策 D-025-25）
category: module_blueprint
---

# 2.28 上下文腐烂防护（决策 D-025-25）

2.28 上下文腐烂防护（决策 D-025-25）

> **新增于 v0.8.0**。v0.7.0 §2.11 的上下文管理聚焦于"溢出"（token limit exceeded）。上下文腐烂 (Context Rot) 是更隐蔽的问题——**容量还在，但质量已降**。在 200K 上下文窗口中，Agent 推理质量从 50K tokens 处就开始显著下降。对长对话的多 Agent 协作场景，每个 Agent 都会累积大量对话历史。

**对标**：Context Rot 研究 (2026-04 — Transformer 三缺陷：注意力稀释 + 位置编码漂移 + 检索噪声累积）、ACON (ICLR 2026 — Failure-Driven Compression, -26-54% memory）、Focus Architecture (-22.7% Token）。

```yaml
context_rot_prevention:

  design_principle: "不是'窗口满了才压缩'——是'推理质量开始下降就主动压缩'。关键词：主动、预测性、失败驱动。"

  # === 上下文腐烂的三个机制 ===
  rot_mechanisms:

    attention_dilution:
      name: "注意力稀释"
      desc: "上下文越长，attention 权重分布越平。关键信息被淹没在噪声中。"
      onset: "一般在上下文使用 25%（50K/200K tokens）处开始显现"
      detection: "追踪 per-step token 的 attention entropy；entropy 上升 → 稀释进行中"
      mitigation: "主动压缩不如完整的上下文——用 LLM 摘要替代原始对话历史"

    positional_encoding_drift:
      name: "位置编码漂移"
      desc: "长期依赖的 tokens 的位置编码随时间偏离原始表示"
      onset: "复杂——取决于序列长度和位置编码方法 (RoPE vs ALiBi)"
      detection: "间接检测——当 Agent 开始'忘记'早期约束时"
      mitigation: "周期性 context refresh: 每 30min 或 50 轮交换后重建上下文"

    retrieval_noise_accumulation:
      name: "检索噪声累积"
      desc: "RAG 检索可能带回不相关信息，累积的噪声干扰决策"
      onset: "每个检索 step 都有少量噪声，线性累积"
      detection: "检索结果的相关性评分分布 → abnormal spike of low-relevance results"
      mitigation: "检索结果去噪门禁: relevance_score < 0.3 → discard"

  # === 主动上下文压缩 ===
  proactive_compaction:
    trigger: "不是满了才压——在 85% 阈值之前就开始检测腐烂信号"
    signals:
      - "Agent 开始重复提问（同一个 clarify 被问了 2+ 次）"
      - "生成的代码开始偏离 project conventions (检测 living spec violations)"
      - "attention_entropy 超过基线 2σ"
      - "Token 消耗速率突然加速（Agent 在做无效循环）"

    compaction_strategy:
      phase_1_summary: "用 LLM 生成结构化摘要替代原始对话（保留：约束、关键决策、问题上下文）"
      phase_2_context_refresh: "丢弃摘要以下的旧消息，从摘要 + System Prompt 重建上下文"
      phase_3_hot_memory: "保留最近 5 轮交换 + 关键文件内容——其他全部进摘要"

  # === ACON：失败驱动的上下文压缩 ===
  acon_approach:
    insight: "不是在'压缩多少'上优化——而是在'full context success vs compressed context failure'的对偶轨迹上学习"
    method:
      - "运行 paired trajectories: 一次 full context（成功），一次 compressed context（失败）"
      - "LLM 分析压缩失败的原因"
      - "更新压缩指南"
    distilled: "优化后的 LLM 压缩器蒸馏到更小的模型，减少 overhead"
    result: "-26-54% 峰值内存，保持 >95% 任务准确性"

  # === ZephyrAlpha 三层上下文架构 ===
  three_layer_context:
    hot_memory_constitution:
      scope: "System Prompt + Project Architecture + Conventions = 不可压缩的'宪法'层"
      content: "项目架构、命名规范、安全约束——所有 Agent 共享"
      update: "人工审阅后更新，通过 AGENTS.md a2a_context 字段注入"

    domain_expert_agent:
      scope: "每个 Agent 的专属领域知识——Agent Card skill 的详细规范"
      content: "代码模式、架构决策记录、API 契约"
      update: "Living Spec 同步 (§2.6) + auto-generated from passing tests"

    cold_memory_knowledge_base:
      scope: "历史交互归档——任务完成记录、已解决冲突的解决方案"
      content: "矢量化的历史记录 + RAG 检索"
      update: "自动归档，通过 relevance-gated RAG (§2.11) 按需加载"

  # === 1人+AI 简化 ===
  simplified_for_solo:
    note: "ACON 的 failure-driven optimization 需要大量 paired trajectories。对 1人+AI 场景用更简单的策略"
    strategy:
      - "每 20min 或有 50+ 轮交换 
