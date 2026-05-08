---
module_id: KE-module_blu-2_36_agent____________________-000
title: 2.36 Agent 失败归因与因果溯源——从"可观测"到"可归因"（决策 D-025-37~38）
category: module_blueprint
---

# 2.36 Agent 失败归因与因果溯源——从"可观测"到"可归因"（决策 D-025-37~38）

2.36 Agent 失败归因与因果溯源——从"可观测"到"可归因"（决策 D-025-37~38）

> **新增于 v0.10.0**。v0.9.0 §2.15 有分布式追踪（trace_id/span_id + token 核算 + 异常检测），但那是"什么顺序发生了什么"——缺少"**为什么**发生"的因果模型和"**谁负责**"的归因引擎。在多 Agent 系统中，5 个 Agent 不是 5 倍失败模式，而是 ~17 倍——因为每种 Agent 间交互都创建了新的失败模式（Telephone Game / Confidence Cascade / Ghost Handoff / Tools Gone Wild / Conga Line）。

**对标**：CTEGs (arXiv:2604.17557, 2026-04 — Causal-Temporal Event Graphs: 递归 Agent 执行的因果事件图模型 + Merkle tree commitments 防篡改验证）、DebugABot (DebugABot Research Initiative, 2026-04 — 九大调试原语 + 三阶段 Identify/Diagnose/Intervene + Blame Attribution Engine (Merkle hash chains + W3C PROV model) + 加密模型指纹 + 硬件 Kill Switch)、17x Error Trap (AgentCenter, 2026-03 — 多 Agent 失败模式的组合爆炸 + 五种跨 Agent 失败模式)、Traceability paper (Oakland University, 2025-10 — Planner→Executor→Critic pipeline blame function + repair/harm rates)、Sentry Multi-Agent Observability (2026-04 — 生产级"Agent 间空间"调试)、Systematic Error Analysis (Panaversity AgentFactory — spreadsheet method + span-level root cause)。

```yaml
agent_blame_attribution_and_causal_trace:

  design_principle: "可观测 ≠ 可归因。你看到了 Agent A 输出 X、Agent B 输出 Y、最终结果 Z 是错的——但你仍然不知道: (1) 根源是 A 还是 B？(2) 是 A 的输入就错了还是 A 自己推理错了？(3) B 有没有机会修复 A 的错误但没修复？归因引擎需要回答这三个问题。"

  # === 17x Error Trap: 五种跨 Agent 失败模式 ===
  cross_agent_failure_modes:
    telephone_game:
      desc: "信息在 Agent 间逐级退化——每个 Agent 微误解+摘要上一步输出→最终输出与原始意图几无关联"
      example: "PM Agent 定义需求→Dev Agent 实现→QA Agent 测试; QA 的理解已严重偏离 PM 的原始意图"
      detection: "对链中每个 handoff point 做语义一致性检查: cosine_sim(original_intent, current_interpretation)"
      fix: "在每个 handoff 中附带原始需求文本——不仅是上游 Agent 的输出"

    confidence_cascade:
      desc: "上游 Agent 出错但自信陈述→下游 Agent 基于错误但'高置信'的输入做推理→错误被放大且滴水不漏"
      example: "Research Agent 引用错误数据→Writing Agent 据此撰写'深度分析'→Review Agent 仅查语法→产出高度自信的错误报告"
      detection: "track confidence_calibration: predicted_confidence vs actual_correctness per span"
      fix: "每个 Agent 在输出中标注 certainty_level + 证据质量"

    ghost_handoff:
      desc: "Agent A 完成任务→Agent B 从未收到/只收到部分/收到但格式错误→静默失败"
      example: "Coordinator 派发 task 到 Executor→消息在传输中截断→Executor 基于不完整信息工作→产出语义错误"
      detection: "handoff_completion_check: ACK + content_hash + size_verification at each handoff boundary"
      fix: "Reception ACK 协议: 每个 handoff 需要 explicit ACK + content fingerprint"

    tools_gone_wild:
      desc: "Agent 的工具调用返回低质量但格式正确的输出→下游 Agent 无区别消费→决策被污染"
      example: "Skeptic Agent 的 web_search 返回弱结果→Synthesizer 基于不对称信息做偏置综合"
      detection: "per-span quality_score (not just format validity, but content richness + source diversity)"
      fix: "工具调用→标记 quality_metadata→下游 Agent 在推理中考虑输入质量权重"

    conga_line:
      desc: "链式 Agent 的最末 Agent 被中间环节的累积噪声淹没——即使前 N-1 个都'正确'"
      example: "10 Agent 链, 每个有 2% 的近似误差→最终输出 ≈ exp(-0.02×10) = 82% 语义保真"
      detection: "chain_semantic_fidelity = ∏ cosine_sim(step(i), step(i-1))"
      fix: "链深度上限 (§2.5 delegation_limit) + 中间 checkpoints 重新对齐 original intent"

  # === CTEGs: 因果事件图模型 ===
  causal_trace_model:
    concept: "从'线性
