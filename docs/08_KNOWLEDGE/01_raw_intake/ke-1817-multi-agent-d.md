---
module_id: KE-1726------------d--004
status: active
title: 2.16 Multi-Agent 共识与协商协议（决策 D-025-13）
category: module_blueprint
---

# 2.16 Multi-Agent 共识与协商协议（决策 D-025-13）

2.16 Multi-Agent 共识与协商协议（决策 D-025-13）

> **新增于 v0.6.0**。v0.5.0 只处理"2 个 Agent 冲突 → Coordinator 裁决"，但 3+ Agent 对同一决策有不同意见时，二元裁决模式失效。需要独立的共识协议层。

**对标**：Concordia Protocol（Google A2A 官方讨论 #1725, 2026-04）、Dialogue Diplomats (arXiv:2511.17654 — 94.2% 共识率，37.8% 更快决策)、Raft/Paxos/PBFT 经典共识算法。

```yaml
consensus_and_negotiation_layer:
  design_principle: "\"Coordinator 裁决\" 只适用于 2 方冲突。3+ 方冲突 → 走共识协议"
  relationship_to_coordinator: "Coordinator 是共识过程的\"主持人\"（Chair），不替代共识机制本身"

  # === 6 状态协商会话机（对标 Concordia Protocol） ===
  negotiation_session:
    states:
      PROPOSED: "提议已发出，等待各方确认收到"
      ACTIVE: "协商进行中——各方提案已收集"
      AGREED: "全体达成一致"
      REJECTED: "提议被否决（过半数反对或 Coordinator 否决）"
      EXPIRED: "超过 TTL 未达成一致，触发降级路径"
      DORMANT: "Agent 离线/无响应，协商暂停"

    offer_types:
      - type: "basic"
        desc: "简单提议——'我来做这个，用这个方案'"
      - type: "partial"
        desc: "部分接受——'接受你的框架，但实现细节改这样'"
      - type: "conditional"
        desc: "条件提议——'我做X，条件是你做Y'"
      - type: "bundle"
        desc: "打包提议——'X+Y+Z，全接受或全拒绝'"

    resolution_strategies:
      - name: "split_the_difference"
        when: "数值型分歧（资源分配、时间估算）"
        desc: "取中位值作为折中方案"
        example: "Agent A 估时 4h，Agent B 估时 8h → 协商结果 6h"

      - name: "pareto_tradeoff"
        when: "多维度分歧（时间 vs 质量 vs 范围）"
        desc: "寻找不损害任何一方的改进方案"
        example: "缩减 scope → 换取更快交付，质量不变"

      - name: "reasoning_based_persuasion"
        when: "方案分歧（架构选择、技术路线）"
        desc: "权重投票——每个 Agent 对其擅长领域有更高权重"
        example: "架构选择 → Architect Agent 权重 ×3，其他 Agent 权重 ×1"

  # === 投票/多数决协议 ===
  voting_protocol:
    modes:
      majority_vote:
        when: "3+ Agent 对同一决策有不同意见，且无明确领域专家"
        rule: "多数决——过半数即通过"
        tie_break: "Coordinator 打破平局（有最终裁量权但只能在平局时使用）"

      weighted_vote:
        when: "有领域专家 Agent"
        rule: "专家领域内权重 ×3，非专家 ×1"
        trust_decay: "连续失败 → 权重衰减（exponential backoff: weight *= 0.5^n_errors）"

      veto_power:
        when: "涉及安全/合规/数据完整性的决策"
        holder: "Coordinator + Security Advisor Agent"
        rule: "任一反对 → REJECTED"

    quorum:
      minimum: "3 个 Agent 参与时 2/3 达到法定人数，5+ Agent 时为 majority+1"

  # === 合谋检测 ===
  collusion_detection:  # 对标 "Agents of Chaos" 失败模式 #10
    signals:
      - "两个 Agent 在 3+ 次协商中始终给出相同的 vote 向量"
      - "Agent 之间\"独家\"委托——只发包给对方，拒绝其他 Agent 提议"
      - "互相评分始终高于均值 2σ"

    detection_algorithm:
      name: "Pairwise Vote Correlation + Jaccard 异常检测"
      threshold: "correlation > 0.95 AND mutual_handoff_ratio > 0.8"

    response:
      - "合谋标记 → 稀释双方在后续投票中的权重"
      - "连续 3 次合谋标记 → 冻结双方的委托权 24h"
      - "通知 Owner（在 1人+AI 场景下即使走到这步也不太可能）"

  # === 协商降级路径 ===
  negotiation_degradation:
    level_1: "缩小范围重试——去掉分歧最大的子任务，先达成部分共识"
    level_2: "委托次优 Agent——原定最优 Agent 的提议过于争议，换次优方案"
    level_3: "拆分子任务序列化——先让 Agent A 做第一步，结果出来后再让 B 做第二步"
    level_4: "Escalate to MOD-INF-022（但 A2A 升级 vs 普通升级不同——携带完整协商记录）"
```

---
