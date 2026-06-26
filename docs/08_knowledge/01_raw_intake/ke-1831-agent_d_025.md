---
module_id: KE-1740---agent------------d-025--005
status: active
title: 2.19 多 Agent 辩论/审议协议（决策 D-025-16）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.19 多 Agent 辩论/审议协议（决策 D-025-16）

2.19 多 Agent 辩论/审议协议（决策 D-025-16）

> **新增于 v0.7.0**。v0.6.0 §2.16 的投票/共识机制是"决策模式"，但辩论/审议是"通信模式"——Agent 如何在投票前**充分交换观点**，这是 A2A 协议中一个新的消息交换范式。

**对标**：ACL 2025 "Voting or Consensus"（7 种决策协议对比）、Free-MAD（ICLR 2026 — consensus-free debate, score-based trajectory evaluation）、All-Agents Drafting (AAD) + Collective Improvement (CI)（+3.3% 和 +7.4% 准确度提升）。

```yaml
debate_and_deliberation_protocol:

  design_principle: "辩论不是 random chat。需要在协议层定义结构化流程、反从众机制、深度上限。"

  # === 4 阶段结构化辩论流程 ===
  debate_phases:
    phase_1_proposal:
      name: "独立提案"
      desc: "每个 Agent 独立起草方案，不互相参考"
      rationale: "防止锚定效应——第一个发言的 Agent 会锚定后续讨论"
      method: "All-Agents Drafting (AAD) —— 对标 ACL 2025"

    phase_2_cross_examination:
      name: "交叉质询"
      desc: "每个 Agent 对其他 Agent 的提案提出 1-3 个质询"
      rules:
        - "质询必须具体——不能是 '我觉得不对'，必须是 '你的方案在 X 场景下会失败'"
        - "每个 Agent 必须回答所有质询"

    phase_3_revision:
      name: "修订提案"
      desc: "基于质询反馈修订方案"
      method: "Collective Improvement (CI) —— 迭代精炼但限制通信防止偏见"
      max_rounds: 3  # ACL 2025: 更多轮次反而降低性能

    phase_4_voting:
      name: "最终投票"
      desc: "用修订后的方案进行投票（走 §2.16 voting_protocol）"

  # === Anti-Conformity 机制（对标 Free-MAD） ===
  anti_conformity:
    problem: "由于 LLM 的从众倾向，正确的少数派 Agent 会在辩论中被错误的多数派带偏"
    free_mad_solution: "Score-based decision mechanism——评估整个辩论轨迹而非只依赖最后一轮"

    zephyr_implementation:
      conformity_discount:
        desc: "当多数派 > 66% 时，多数派每个 Agent 的发言权重 ×0.7"
        rationale: "平衡从众倾向——少数派的观点可能被过度压制"

      trajectory_scoring:
        desc: "投票时不只看最后一轮方案，而是给整个辩论过程中始终一致的观点更高分"
        rationale: "始终一致的观点 = 经过多轮考验 = 更可信"
        weight_formula: "consistency_score = num_rounds_same_position / total_rounds"

      confidence_tracking:
        desc: "每个 Agent 对自己提案的置信度声明——若 Agent 在质询后降低了自身置信度，该提案自动降权"
        rationale: "自我怀疑是有价值的信号"

  # === 辩论深度上限 ===
  debate_depth:
    max_total_rounds: 5  # Phase1-3 合计不超过 5 轮
    early_termination:
      - "全体一致同意 → 跳过投票，直接 AGREED"
      - "连续 2 轮无实质新信息 → 直接进入投票"
      - "Token 消耗超过辩论预算 → 直接进入投票"
    debate_budget: "min(20% * per_handoff_token_budget, $5)"

  # === 群体盲区防护 ===
  group_blindspot_protection:
    problem: "多数 Agent 在同一处出现逻辑谬误 → 辩论放大错误"
    detector:
      - "3+ Agent 独立提案中在同一个子问题上出现相同结论 → 触发\"群体盲区\"标记"
      - "该子问题 → 强制引入外部验证（运行实际测试/查文档/代码验证）再讨论"
    escalation: "群体盲区标记 → 升级到 MOD-INF-022，附加辩论记录"
```

---
