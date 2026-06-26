---
module_id: KE-1882-------critic-with-veto----006
status: active
title: 2.31 宪法治理与 Critic-with-veto（决策 D-025-28）
category: module_blueprint
ttl: permanent
---

# 2.31 宪法治理与 Critic-with-veto（决策 D-025-28）

2.31 宪法治理与 Critic-with-veto（决策 D-025-28）

> **新增于 v0.9.0**。v0.8.0 有仲裁（auto→escalate→block 三级）和用户同意编排，但 Agent 治理规则本身的定义、修订、执行监督——这三件事没有独立的"宪法层"来保障。规则不是代码——是经过 Agent 议会投票后写入不可变层的宪法条目。53% 的 Agent 运行时超出授权范围（Cloud Security Alliance 2026），说明没有零容忍门控。

**对标**：Council framework (chain-ml/council, 2026-04 — Agent 议会式治理: Controller/Agent/Skill/ExecutionChain 分层 + LLMController/SequentialController/ParallelController 三种模式）、Microsoft AGT ADR 0006 (2026-04 — 宪法约束层 + Critic-with-veto 否决权 Agent + blast-radius 逐级上报 + intent drift + policy-compliant harm 双重检测）、HC-12 Hard Constraint (零容忍控制绕过: 不允许任何 Agent 绕过治理门控，除非通过正式批准的宪法修正案）。

```yaml
constitutional_governance:

  design_principle: "仲裁规则本身也需要治理——'谁监管监管者？'当规则由 AI 建议、Owner 批准时，AI 可以通过'看似合理的安全建议'弱化对自己不利的约束。治理不能是 AI 起草的——必须是范式化的、可形式化验证的、有独立 Critic Agent 监督的。"

  # === 宪法约束层架构 ===
  constitution_layer:
    governance_council:
      concept: "Agent 议会——不是所有 Agent 平等。特定 Agent 拥有宪法修正动议权 (Motion)、审议权 (Deliberation)、批准权 (Ratification)、否决权 (Veto)。"
      roles:
        - role: "Critic Agent (Veto)"
          capability: "独立于所有执行 Agent 的审查者——唯一有权否决 Coordinator 决策的 Agent"
          constraint: "Critic Agent 本身不执行任何 task——零利益冲突"
          origin: "Microsoft AGT ADR 0006: Critic-with-veto pattern"
        - role: "Coordinator (Motion)"
          capability: "发现规则漏洞 → 提起宪法修正动议"
          constraint: "不能自己批准自己的动议"
        - role: "Owner (Ratification)"
          capability: "所有宪法修正的最终批准者——AI 不能绕过"

    constitution_storage:
      format: "CONSTITUTION.md (不可变 YAML)"
      location: "docs/01_policies_and_standards/governance/ai/a2a-constitution.yaml"
      properties:
        - "每条规则有 SHA-256 指纹"
        - "每次修订必须经过 Council 投票 (Critic + Coordinator + Owner 三方)"
        - "修订历史的完整 Audit Trail"
        - "AI 可读取但不可直接编辑（写保护——对标 arbitration_rules.yaml 的不可变性）"

  # === HC-12 零容忍门控 ===
  governance_gate:
    concept: "GovernanceGate: 每个 Agent 操作在运行时层面做零容忍校验——不是'检测违规后降级'，而是'物理上无法绕过此门'。"
    implementation: "Constraint-as-Code——不是 AI policy，是编译时注入的 assertion："
    checks:
      - check: "scope_bound"
        assertion: "agent.current_scope ⊂ agent.card.max_scope"
        action: "violation → immediate block + Critic notification"

      - check: "delegation_limit"
        assertion: "delegation_depth <= card.max_delegation_depth"
        action: "violation → immediate block + chain terminate"

      - check: "budget_cap"
        assertion: "chain_cost_accumulated + estimated_remaining <= chain_budget_cap"
        action: "violation → immediate block + budget review"

      - check: "tool_whitelist"
        assertion: "tool_name ∈ card.whitelisted_tools"
        action: "violation → immediate block + quarantine"
    design:
      bypass_protection: "GovernanceGate 不是 AI 代码——是框架层的硬编码约束。任何修改 GovernanceGate 的 commit → 需要 Critic Agent + Owner 双签 + CONSTITUTION.md 哈希一致性验证。"

  # === 意图漂移检测 (Intent Drift) ===
  intent_drift:
    problem: "Agent 初始指令=实现 CRUD API → 50 轮后实际在做 ORM 迁移→再 30 轮后在做数据库架构重构。每一步都没有违规——但轨迹已大幅偏离初始 intent。"
    origin: "Micros
