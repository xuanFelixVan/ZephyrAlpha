---
module_id: "MOD-INF-025"
title: "A2A 协调协议蓝图 — Agent-to-Agent 通信与冲突解决：Agent发现+任务交接+冲突检测+仲裁+死锁防护+消息安全+Living Spec同步+上下文管理+经济护栏+级联防护+可观测性+自指悖论独立验证+多Agent共识与协商+涌现行为与异常检测+Saga事务回滚+辩论/审议协议+经济资源分配+异质模型动态路由+工作窃取与负载均衡+A2A协议层安全攻击面防护+结构化协商帧(ANP)+形式化验证(TLA+/Coq)+潜空间通信+多维向量信誉(TrustFlow)+上下文腐烂防护+用户同意编排+Vibe Coding深度优化+宪法治理与Critic-with-veto+Agent免疫隔离检疫+选择性遗忘与被遗忘权+碳排放追踪与碳感知路由+空转综合征与PollingStorm检测+多协议网关与互联总线+Agent失败归因与因果溯源引擎"
doc_type: blueprint
status: Draft
version: "0.10.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: phase_1_partial
belongs_to: "MOD-MASTER-001"
summary: "ZephyrAlpha A2A 协调协议蓝图——多 Agent 场景下的通信协议与冲突解决。九层十二协议架构：发现与身份层（Agent Card + 能力注册 + AGENTS.md 路由集成 + JCS/JWS 正式签名）→ 通信与任务层（Task 状态机 + Message/Part 类型系统 + SSE 流式 + Push Notification + 协议版本协商 + 上下文压缩与传递）→ 结构化协商帧层（ANP 1.0 Negotiation Frame + ZK 身份证明 + 委托链权威性缩减 + 确定性执行）→ 辩论与审议层（4 阶段结构化辩论 + anti-conformity + 辩论深度上限 + AAD/CI）→ 共识与协商层（6 状态协商会话机 + 投票/多数决 + 合谋检测 + 协商降级）→ 经济与资源分配层（Agent 预算池分配 + ROI 追踪 + 跨 IDE 花费聚合 + 多维向量信誉 TrustFlow）→ 异质模型路由层（角色×难度×负载三维决策 + confidence-aware + 批量降级 + 潜空间通信嵌入）→ 事务与回滚层（Saga LT/CT 配对注册 + 分布式检查点 + 幂等性门禁 + 补偿编排）→ 协调与负载均衡层（Supervisor/Coordinator + Living Spec 同步 + 文本/语义冲突检测 + 死锁/活锁防护 + 仲裁auto→rule→Escalation + 工作窃取 + 任务亲和性 + No-AI Time全局暂停）。横切关注点：A2A协议层安全（A2ASECBENCH 六大攻击面防护：Agent Card供应链完整性+Task流防操纵+Artifact投毒门禁+Agent间DoS限流） + OWASP ASI07 消息安全 + 形式化验证（TLA+死锁自由+委托链7属性+时间感知准入控制ACP）+ 经济护栏（含 Prompt Caching + Lazy Context Loading + Shared Memory File + 上下文腐烂防护 + 碳排放追踪与碳感知调度）+ 级联故障防护 + 分布式追踪与可观测性 + 施工自指悖论独立验证 + 涌现行为与异常检测 + 多 Agent 共享记忆（3 类型：短时/长时/Profile + ground-truth-preserving）+ 用户同意编排（USER_CONSENT_REQUIRED + 临时作用域Token）+ Agent休眠/唤醒协议 + 宪法治理（Critic-with-veto + HC-12 零容忍门控 + 意图漂移检测 + 政策合规伤害检测）+ Agent免疫系统（隔离→检疫→清除→免疫记忆 + 跨Agent攻击链检测 + 工具调用策略治理）+ 选择性遗忘与被遗忘权（FSFM + EU AI Act 2026 合规 + 跨Agent遗忘一致性）+ 空转综合征检测（PollingStorm防御 + 闲置消费陷阱自动休眠）+ 多协议网关与互联总线（A2A/MCP/ACP/ANP 四协议翻译 + AgentGateway/agentlink/AGNTCY 协议无关基础设施）+ Agent失败归因与因果溯源（CTEGs因果事件图 + 17x Error Trap 五类跨Agent失败模式 + DebugABot Blame Attribution Engine Merkle归因链）。对标 Google A2A Protocol v1.0 + Anthropic Claude Code Agent Teams + Microsoft Agent Framework + OpenAI Agents SDK + LangGraph v1.0 + CrewAI v1.10.1 + Concordia Protocol + ANP 1.0 + A2ASECBENCH + \"Agents of Chaos\" + SentinelAgent + ACP v1.27 + μACP + MAScope + SagaLLM + x402 + AEP + OI-MAS + Chimera + GraphPlanner + Free-MAD + MemMachine + TrustFlow + LR2 + Interlat + ACON + BridgeMCP/BridgeSwarm + LangChain Deep Agents SDK + LumiMAS + MAStitch + nForma + Council + ClawGuard + FSFM + HW-Router + KD-MARL + AgentDistill + AgentArk + CodeCarbon + agent-loop-detector + ACP (IBM) + AgentGateway + AGNTCY + DebugABot + CTEGs + agentlink + OpenGateway + Sentry Multi-Agent Observability 等 63+ 专业机构。"
tags: [a2a, agent-coordination, multi-agent, conflict-resolution, infrastructure, agent-card, task-state-machine, message-types, sse-streaming, push-notification, supervisor-coordinator, living-spec, semantic-conflict, deadlock-prevention, livelock-detection, message-security, owasp-asi07, session-smuggling, context-management, economic-guardrails, cascade-failure, distributed-tracing, observability, self-referential-verification, vibe-coding-optimization, multi-agent-consensus, agent-negotiation, emergence-detection, anomaly-detection, saga-transaction, rollback-compensation, prompt-caching, lazy-context-loading, shared-memory-file, concordia-protocol, agents-of-chaos, mascope, sagallm, protocol-version-negotiation, agent-debate, deliberation, agent-economy, resource-allocation, roi-tracking, heterogeneous-routing, model-aware, dynamic-routing, work-stealing, load-balancing, shared-agent-memory, memmachine, free-mad, oi-mas, chimera, graphplanner, x402, aep, deep-agents-sdk, bridgemcp, a2aproto-sec, a2asecbench, agent-card-supply-chain, task-flow-protection, artifact-poisoning, agent-dos-protection, structured-negotiation, anp, zk-proof, delegation-chain, authority-narrowing, formal-verification, tla-plus, coq, temporal-admission-control, acp, mu-acp, latent-space-comm, interlat, vector-reputation, trustflow, lr2, bottom-up-reputation, sybil-resistance, context-rot, attention-dilution, positional-encoding-drift, acon, user-consent, consent-orchestration, ephemeral-tokens, no-ai-time, agent-hibernate, agent-wake, adversarial-agent-games, red-team-blue-team, lumimas, mastitch, nforma, bridgebench, agent-drift, capability-degradation, self-evolution, autogenesis, constitutional-governance, hc-12, critic-with-veto, governance-gate, intent-drift, policy-compliant-harm, agent-immune-system, threat-quarantine, attack-chain-detection, clawguard, tool-call-governance, agent-forgetting, fsff, machine-unlearning, right-to-be-forgotten, eu-ai-act-2026, cross-agent-forgetting, carbon-tracking, codecarbon, green-ai, carbon-aware-routing, graviton5, agent-idle-detection, polling-storm, stuck-loop, idle-agent-syndrome, agent-loop-detector, cross-ide-monitoring, kd-marl, agent-distillation, agentdistill, agentark, teacher-student-agent, capability-transfer, hw-router, hardware-aware-routing, disaggregated-inference, multi-protocol-gateway, ibm-acp, agent-gateway, agntcy, protocol-translation, agent-interconnect-bus, agent-card-parameterization, input-schema, output-schema, authorization-creep, protocol-version-negotiation, backward-forward-compatibility, agent-blame-attribution, causal-trace, cteg, debug-a-bot, merkle-chain-blame, 17x-error-trap, cross-agent-failure, telephone-game, ghost-handoff, confidence-cascade, skills-marketplace, openclaw-skills, openrouter-skills]
priority: P2
depends_on:
  - {target: "MOD-INF-018", at: "§2", why: "Agent RBAC——Agent 身份是 A2A 通信的基础。A2A Agent Card 中的 identity 字段与 RBAC agent_id/role 对齐"}
  - {target: "MOD-INF-022", at: "§2.2", why: "Escalation——Agent 间冲突升级到规则引擎。A2A 仲裁引擎的三级输出（autonomous/auto_guard/blocked）对齐 Escalation 三级"}
  - {target: "MOD-INF-020", at: "§2", why: "Audit Trail——A2A 通信记录、Agent 间消息、冲突检测事件、仲裁结果全部写入审计"}
  - {target: "MOD-INF-019", at: "§2.2", why: "Agent Spec / AGENTS.md——Skill Pack 路由是 A2A Agent Card 的注册入口；AGENTS.md 的 a2a_agents 字段为 A2A 发现机制的唯一入口"}
  - {target: "MOD-INF-007", at: "§2", why: "Gate Engine——A2A 消息在 Agent 间传递时的 schema 校验与安全门禁"}
  - {target: "ADR-0032", at: "全篇", why: "AgentOrchestrator——A2A 的 Supervisor 层在 AgentOrchestrator 之上构建，复用 6 角色 × 10 域路由矩阵"}
  - {target: "ADR-0041", at: "§1", why: "Session Handoff——A2A 的委托上下文包字段格式对标 HandoffPackage 8 必填字段；明确 A2A 任务交接 vs Session 交接的边界"}
---

## DOM-GOV-001 集成契约锚点

> 权威定义见 [`../../_domain-governance/blueprint.md`](../../_domain-governance/blueprint.md) §3。

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-008 | 产出方（A2A 安全边界 → RBAC / Escalation） | MOD-INF-018 / MOD-INF-022 |

# A2A 协调协议蓝图 — Agent-to-Agent 通信与冲突解决

> **module_id**: MOD-INF-025 | **version**: 0.10.0 | **status**: draft | **layer**: cross_layer

> **对标**：Google A2A Protocol v1.0（Linux Foundation 托管，150+ 组织支持）+ Anthropic Claude Code Agent Teams + Microsoft Agent Framework（runtime-mediated orchestration loop）+ OpenAI Agents SDK + LangGraph v1.0 + CrewAI v1.10.1 + Concordia Protocol + MIT CORDIAL + OWASP Agentic Top 10 ASI01-ASI10 + "Agents of Chaos"（Harvard/MIT/Stanford/CMU — 11 种无越狱系统性失败）+ MAScope（ZJU — Cross-Agent Semantic Flow F1=85.3%）+ SagaLLM（Stanford）+ MARIA OS Safety Layer + DPBench + x402（Coinbase+Cloudflare — Agent 支付层，1 亿+交易）+ AEP（Autonomous Economy Protocol — 9 合约 Agent 经济）+ OI-MAS（HIT — confidence-aware routing → +12.88% acc, -79.78% cost）+ Chimera（UNC/Microsoft/CMU — latency- and performance-aware multi-agent serving）+ GraphPlanner（ICLR 2026 — graph-based agentic routing）+ Free-MAD（ICLR 2026 withdrawn — consensus-free multi-agent debate）+ MemMachine（MemVerge — ground-truth-preserving agent memory）+ BridgeMCP/BridgeSwarm（多 IDE Agent 共享 task queue）+ Council（chain-ml — Agent 议会式治理）+ ClawGuard（285+ 安全模式）+ FSFM（生物启发选择性遗忘）+ HW-Router（硬件信号驱动路由）+ KD-MARL（知识蒸馏）+ AgentDistill/AgentArk（蒸馏框架）+ CodeCarbon（碳排放追踪）+ agent-loop-detector（空转检测）+ IBM ACP（联邦编排, -40% 延迟）+ AgentGateway（Linux Foundation 多协议网关）+ AGNTCY（Cisco Internet of Agents）+ CTEGs（因果事件图）+ DebugABot（Blame Attribution Engine Merkle 归因）+ 17x Error Trap（跨 Agent 失败组合爆炸）+ Sentry（Agent 间空间生产调试）等 63+ 专业机构。

> **当前状态**：**Hold 至 stable**（R81 C-04 决策）。当前单 Agent + 多 IDE 场景，A2A 不急需。触发条件：Agent >= 3 且出现冲突 + 跨 Agent 任务交接频次 >= 5 次/天。**本蓝图 v0.10.0 已将全部 150 条盲点写入**，达到可施工完备度——触发条件命中后无需再次补盲，直接进入 Phase scaffold。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-025 |
| 代码落位 | `src/zephyr/a2a/` |
| 运行时平面 | Warm memory（Agent 间通信时加载）+ Cold memory（Agent Card 注册表持久化） |
| 核心职责 | 多 Agent 场景下的通信协议与冲突解决——Agent 发现 → 任务交接 → 冲突检测 → 辩论审议 → 仲裁 → 共识 → 回滚 → 经济分配 → 宪法治理 → 免疫防护 → 遗忘合规 → 运维可持续 → 多协议互操作 → 失败归因 |
| 当前状态 | **Hold**——等待触发条件命中（蓝图已完成 150 条盲点补齐，可施工完备） |

### 1.2 Hold 决策记录

| 决策 ID | 决策 | 理由 | 触发条件 |
|---------|------|------|---------|
| R81-C04 | Hold 至 stable | 当前单 Agent + 多 IDE 场景，A2A 不急需；但多 IDE 本身即是 3 个"准独立 Agent 系统" | Agent >= 3 且出现冲突 + 交接 >= 5次/天 |

### 1.3 当前场景分析与隐性风险

当前是 **1 人 + AI + 多 IDE（TRAE/Cursor/RooCode）** 场景。虽然开了 10+ 对话，但每个对话是独立的 AI Agent，不存在 Agent 间协作需求。冲突通过 git 锁机制解决（先 commit 先赢）。

**但以下隐性风险已经存在（触发条件未到不等于风险为 0）：**

| # | 隐性风险 | 当前状态 | 升级到多 Agent 后的爆炸点 |
|---|---------|---------|-------------------------|
| 1 | 10+ 对话共享 Skill Pack，无 Agent Card 能力声明 | 所有对话都加载相同 Skill Pack | Agent 能力冲突——"谁来做？" |
| 2 | 3 个 IDE 各自运行 Agent，无跨 IDE 身份统一 | 各 IDE 独立，但共享 git repo | Agent 身份混乱——"谁做的？" |
| 3 | git merge 只能检测文本级冲突 | 当前冲突少，靠运气 | 语义冲突爆炸——"怎么过编译但跑炸了？" |
| 4 | 10+ 对话无协调者 | 靠 Owner 手动协调 | 死锁率 95-100%（DPBench 数据） |
| 5 | Agent 间无消息安全 | 不需要 | OWASP ASI07——"谁在冒充谁？" |

### 1.4 触发条件监控（v0.6.0 扩展）

```yaml
trigger_monitoring:
  metric_1:
    name: "active_agent_count"
    current: 1
    threshold: 3
    source: "AgentIdentity 注册表"
    note: "多 IDE 开的对话也算 Agent——TRAE/Cursor/RooCode 同时并行就已达阈值的 1/3"

  metric_2:
    name: "inter_agent_handoff_per_day"
    current: 0
    threshold: 5
    source: "Audit Trail 任务交接记录"

  metric_3:
    name: "conflict_count_per_day"
    current: 0
    threshold: 2
    source: "git merge conflict 统计"

  metric_4:
    name: "concurrent_ide_sessions"
    current: 10
    threshold: 15
    source: "IDE Session Tracker"
    warning: "TRAE + Cursor + RooCode 各开 5+ 对话 = 准多 Agent 场景"

  metric_5:  # v0.6.0 新增——False Task Completion 信号
    name: "ineffective_task_completions"
    current: 0
    threshold: 1
    source: "Living Spec diff verification"
    note: "\"Agents of Chaos\" 失败模式 #9——Agent COMPLETED ≠ 任务真完成了"

  metric_6:  # v0.6.0 新增——涌现行为信号
    name: "cross_agent_behavioral_anomalies"
    current: 0
    threshold: 1
    source: "MAScope Cross-Agent Semantic Flow + Isolation Forest anomaly score > 0.7"
    note: "单个 Agent 行为正常但跨 Agent 轨迹异常"

  activation_rule: "metric_1 >= 3 AND (metric_2 >= 5 OR metric_3 >= 2)"
  early_warning_rule: "(metric_4 >= 15 AND metric_1 >= 2) OR metric_5 >= 1 OR metric_6 >= 1 → 开始预热 A2A scaffold"
```

---

## 2. 核心架构

### 2.1 三层五协议总架构（决策 D-025-01）→ v0.6.0 已升级为五层八协议

> **决策 D-025-01**：A2A 协议不是 4 个独立 Python 文件的集合，而是**三层五协议架构**——发现与身份层（Layer 1）→ 通信与任务层（Layer 2）→ 协调与仲裁层（Layer 3）。三层之间有明确的数据契约，每层独立可测。横切关注点（安全/经济/追踪/自指验证）作为第四维度贯穿全部三层。
>
> **v0.6.0 更新**：在三层之上新增两个协议层——**共识与协商层**（Layer 3，原 Layer 3 后移至 Layer 5）和**事务与回滚层**（Layer 4），形成五层八协议架构：Layer 1(发现+身份)→Layer 2(通信+任务)→Layer 3(共识+协商)→Layer 4(事务+回滚)→Layer 5(协调+仲裁)。详见 D-025-13~15。
>
> **决策依据**：对标 Google A2A（Agent Card + Task + Message/Part）+ Anthropic Agent Teams（Lead + Teammates + P2P）+ MIT CORDIAL（死锁三层解决）。三层分离使各层可独立 Hold/进化——Layer 1 在 scafford 即可用，Layer 3 到 experimental 才完整。

```yaml
a2a_architecture:
  # ===== Layer 1: Discovery & Identity（发现与身份层）=====
  layer_1:
    protocols:
      - name: "Agent Card Protocol"
        id: "A2A-P-001"
        description: "Agent 能力声明——JSON/YAML 格式，注册到 AGENTS.md"
        files: ["agent_card.py", "a2a_registry.py"]
        state: "⏸️ Hold"

      - name: "Identity Verification Protocol"
        id: "A2A-P-002"
        description: "Agent 间身份验证——JWT + SPIFFE + 防克隆"
        files: ["identity_verifier.py"]
        state: "⏸️ Hold"

    integration: "AGENTS.md → a2a_agents: 字段为 Agent Card 注册的唯一入口"

  # ===== Layer 2: Communication & Task（通信与任务层）=====
  layer_2:
    protocols:
      - name: "Task Handoff Protocol"
        id: "A2A-P-003"
        description: "任务状态机 + 交接上下文包（7 必填字段，对标 ADR-0041）"
        files: ["a2a_schemas.py", "a2a_state.py", "handoff_manager.py", "context_package.py"]
        state: "⏸️ Hold"

      - name: "Message Transport Protocol"
        id: "A2A-P-004"
        description: "Message/Part 类型系统 + SSE 流式 + Push Notification + 输入协商"
        files: ["message_router.py", "streaming.py", "push_notifier.py"]
        state: "⏸️ Hold"

  # ===== Layer 3: Coordination & Arbitration（协调与仲裁层）=====
  layer_3:
    protocols:
      - name: "Coordination Protocol"
        id: "A2A-P-005"
        description: "Supervisor/Coordinator + Living Spec 同步 + 冲突检测（文本+语义）+ 死锁/活锁防护"
        files:
          ["supervisor.py", "spec_sync.py", "conflict_detector.py",
           "semantic_diff.py", "deadlock_guard.py", "livelock_detector.py"]
        state: "⏸️ Hold"

      - name: "Arbitration Protocol"
        id: "A2A-P-006"
        description: "三级仲裁——auto（规则判定）→ escalate（升级到 MOD-INF-022）→ block（人工介入）"
        files: ["arbitrator.py", "arbitration_rules.yaml"]
        state: "⏸️ Hold"

  # ===== Cross-Cutting（横切关注点）=====
  cross_cutting:
    dimensions:
      - name: "Security（消息安全）"
        files: ["a2a_security.py", "session_smuggling_defense.py"]

      - name: "Economics（经济护栏）"
        files: ["a2a_economics.py"]

      - name: "Observability（可观测性）"
        files: ["a2a_tracing.py", "a2a_metrics.py"]

      - name: "Self-Referential Verification（自指验证）"
        files: ["construction_verifier.py"]
```

### 2.2 Agent Card 与能力注册模型（决策 D-025-02）

> **决策 D-025-02**：Agent Card 是 A2A 的"名片"——每个 Agent 启动时注册其能力声明（对标 Google A2A §5 + Anthropic Claude Code Agent Spec）。注册入口是 AGENTS.md 的扩展 `a2a_agents:` 字段，而非独立的 `/.well-known/agent-card.json`——因为多 IDE 并发场景下 AGENTS.md 是唯一跨平台统一入口（对标准 MOD-INF-019 D-019-02）。
>
> **决策依据**：Google A2A 用 well-known URI（企业场景，可预测域名），ZephyrAlpha 是本地多 IDE 场景（无固定域名），AGENTS.md 是 TRAE/Cursor/RooCode 都读的唯一文件——A2A 发现机制必须在此统一。

```yaml
agent_card_model:
  # === Agent Card 字段定义（对标 Google A2A §5.5）===
  agent_card_fields:
    - field: "agent_id"
      type: "string"
      format: "ARCH-{uuid7} | IMPL-{uuid7} | GOV-{uuid7}"
      description: "Agent 唯一标识——前缀关联 Skill Pack 角色"

    - field: "agent_type"
      type: "enum"
      values: ["architect", "implementer", "governor"]
      description: "Agent 角色类型——对齐 3 个 Skill Pack"

    - field: "display_name"
      type: "string"
      description: "人类可读名称——如 '架构师 Agent (TRAE)'"

    - field: "provider"
      type: "string"
      description: "Agent 提供者——IDE 名称（TRAE / Cursor / RooCode）"

    - field: "version"
      type: "string (semver)"
      description: "Agent Card 版本——对标 MOD-INF-019 Skill 版本"

    - field: "capabilities"
      type: "list[AgentSkill]"
      description: "Agent 能力列表（对标 Google A2A AgentSkill）"
      example:
        - skill_id: "SKILL-ARCH-001"
          name: "蓝图解读"
          description: "读取模块蓝图 → 生成 Pydantic 接口骨架"
          input_modes: ["text", "yaml"]
          output_modes: ["python", "pydantic"]

    - field: "endpoint"
      type: "string"
      description: "Agent 通信端点——本地进程间通信（IPC/pipe/内存队列）"

    - field: "authentication"
      type: "object"
      description: "认证方式——JWT RS256 非对称签名（对标 Google A2A SecurityScheme）"
      fields:
        - "scheme: bearer"
        - "public_key_fingerprint"

    - field: "resource_limits"
      type: "object"
      description: "Agent 资源限制"
      fields:
        - "max_concurrent_tasks: int (default=3)"
        - "token_budget_per_task: int (default=50000)"
        - "heartbeat_interval_seconds: int (default=30)"

    - field: "input_modes"
      type: "list[str]"
      description: "支持的输入模态（text/file/data）"

    - field: "output_modes"
      type: "list[str]"
      description: "支持的输出模态"

    - field: "status"
      type: "enum"
      values: ["active", "idle", "degraded", "dead"]
      description: "Agent 当前运行状态"

  # === AGENTS.md 中的注册入口 ===
  agnets_md_extension:
    section: "a2a_agents"
    format: "YAML list of Agent Card references"
    example: |
      a2a_agents:
        - agent_id: "ARCH-0192a7b1"
          agent_type: "architect"
          agent_card_path: "src/zephyr/a2a/cards/architect.yaml"
        - agent_id: "IMPL-3f8e2c91"
          agent_type: "implementer"
          agent_card_path: "src/zephyr/a2a/cards/implementer.yaml"
    note: "Agent Card 物理文件存放在 src/zephyr/a2a/cards/ 目录，AGENTS.md 只引用不内联"

  # === Agent Card 完整性校验 ===
  card_integrity:
    on_register: "SHA-256 hash 校验——Agent Card 未被篡改"
    periodic: "每 5 分钟 re-hash 对比"
    mismatch_action: "Agent 标记为 rogue + 隔离 + 通知 Owner"
```

### 2.3 A2A 任务状态机（决策 D-025-03）

> **决策 D-025-03**：A2A 任务状态机独立于 Orchestrator 的 TaskState（ADR-0017）——前者定义**Agent 间协作粒度**的任务流转，后者定义**单 Agent 内部**的执行粒度。两者通过 `task_id` 关联，但状态空间不重叠。对标 Google A2A §6.3：`submitted → working → input-required → completed / failed / canceled / rejected`。
>
> **决策依据**：Google A2A 的 TaskState 针对的是"两个不透明的 Agent 之间的协作任务"，需要 `input-required`（索取凭证）和 `rejected`（接收方拒绝）这两个跨信任边界的状态——单 Agent 内部状态机不需要这些。

```yaml
a2a_task_state:
  # === A2A 任务状态 ===
  states:
    - state: "SUBMITTED"
      description: "发送方 Agent 已提交任务（附上下文包）"
      next: ["WORKING", "REJECTED", "CANCELED"]

    - state: "WORKING"
      description: "接收方 Agent 已接收并执行中"
      next: ["COMPLETED", "FAILED", "INPUT_REQUIRED", "CANCELED"]

    - state: "INPUT_REQUIRED"
      description: "接收方 Agent 需要额外信息/凭证才能继续——对标 Google A2A in-task auth"
      next: ["WORKING", "FAILED", "CANCELED"]

    - state: "COMPLETED"
      description: "任务成功——产出 Artifact"
      next: []  # 终态

    - state: "FAILED"
      description: "任务失败——附 failure_reason + retryable 标志"
      next: ["SUBMITTED"]  # 仅 retryable=True 时允许重提

    - state: "CANCELED"
      description: "主动取消（发送方取消或超时）"
      next: []

    - state: "REJECTED"
      description: "接收方拒绝执行——能力不匹配/权限不足/资源不可用"
      next: ["SUBMITTED"]  # 发送方可调整后重提

  # === 任务上下文包（7 必填字段，对标 ADR-0041 HandoffPackage）===
  task_context_package:
    required_fields:
      - field: "task_id"
        type: "string"
        description: "A2A 任务唯一标识——格式 A2A-TASK-{TIMESTAMP}-{SEQ}"

      - field: "source_agent_id"
        type: "string"
        description: "发起 Agent ID"

      - field: "target_agent_id"
        type: "string"
        description: "目标 Agent ID——空则广播给所有匹配能力的 Agent"

      - field: "task_summary"
        type: "string (≤ 300 chars)"
        description: "任务摘要——对标 ADR-0041 context_summary"

      - field: "current_state"
        type: "dict"
        description: "当前上下文状态——已完成的步骤 + 阻塞点"

      - field: "constraints"
        type: "dict"
        description: "约束——预算剩余 + 不能修改什么 + 期望产出格式"

      - field: "expected_output"
        type: "string"
        description: "期望产出物格式——对标 ADR-0041 next_actions"

  # === 与 Orchestrator TaskState 的关系 ===
  orchestration_mapping:
    note: "A2A SUBMITTED ≠ Orchestrator QUEUED——前者是 Agent 间投递，后者是单 Agent 内部排队"
    flow: |
      发送方 Agent：
        Orchestrator.task.state = RUNNING
          → A2A Task SUBMITTED → WORKING（接收方开始执行）
          → 接收方 Orchestrator 子任务从 DRAFT → QUEUED → ... → COMPLETED
          → A2A Task COMPLETED → 发送方 Orchestrator.task = RUNNING（继续）
```

### 2.4 Message/Part 类型系统（决策 D-025-04）

> **决策 D-025-04**：A2A 消息格式为**YAML（人读 + 机读）**而非 Google A2A 的 JSON-RPC 2.0。核心理由：1人+AI 维护场景下，Owner 必须能肉眼看懂 Agent 间的通信（调试地狱的最大敌人），YAML 天然比 JSON 更可读。但内部仍有严格的 Pydantic schema 校验——人读 ≠ 无校验。
>
> **决策依据**：社区实战反复验证"5 个 Agent 100 行日志 2 小时排查"是 Multi-Agent 的运维灾难，可读性是有实际价值的架构决策。对标 MOD-INF-019 的 `instructions.md` 格式（Markdown 人读 + YAML 机读）。

```yaml
message_part_system:
  # === Part 类型（对标 Google A2A §6.5）===
  part_types:
    - type: "TextPart"
      description: "纯文本消息——Agent 间的主要通信载体"
      fields: ["text: str"]

    - type: "FilePart"
      description: "文件内容传递——代码 diff / 蓝图 / 配置"
      fields: ["file_path: str", "mime_type: str", "content: str"]

    - type: "DataPart"
      description: "结构化数据——任务状态 / 上下文包 / Agent Card"
      fields: ["schema: str", "data: dict"]

  # === Message 结构 ===
  message_structure:
    fields:
      - name: "message_id"
        type: "string (UUID7)"
        description: "消息唯一标识"

      - name: "correlation_id"
        type: "string"
        description: "关联 ID——追踪同一任务链中的所有消息，对标分布式追踪 TraceID"

      - name: "sender"
        type: "AgentIdentity"
        description: "发送方 Agent 身份"

      - name: "recipient"
        type: "AgentIdentity | broadcast"
        description: "接收方——指定 Agent ID 或 broadcast"

      - name: "priority"
        type: "enum[URGENT, HIGH, NORMAL, LOW]"
        description: "消息优先级——仲裁时使用"

      - name: "parts"
        type: "list[Part]"
        description: "消息内容——一个或多个 Part"

      - name: "signature"
        type: "string (JWT RS256)"
        description: "消息签名——防篡改 + 防伪造（集成 §2.10）"

      - name: "timestamp"
        type: "ISO8601"
        description: "消息发出时间"

  # === YAML 消息模板 ===
  template: |
    message_id: "A2A-MSG-0192a7b1-0001"
    correlation_id: "A2A-CORR-0192a7b1"
    sender:
      agent_id: "ARCH-0192a7b1"
      agent_type: "architect"
    recipient:
      agent_id: "IMPL-3f8e2c91"
    priority: "NORMAL"
    parts:
      - type: "TextPart"
        text: "需要实现 MOD-INF-007 Gate Engine §3 接口"
      - type: "DataPart"
        schema: "interface-contract"
        data:
          class: "GateEngine"
          methods: ["evaluate", "check", "report"]
      - type: "FilePart"
        file_path: "docs/03_modules/_cross_layer/gate-engine/blueprint.md"
        mime_type: "text/markdown"
        content: "..."  # 截断 2KB
    signature: "eyJhbGciOiJSUzI1NiIs..."
    timestamp: "2026-05-05T12:00:00Z"
```

### 2.5 Supervisor/Coordinator 模式（决策 D-025-05）

> **决策 D-025-05**：A2A 的协调者是**规则驱动的 Coordinator**（确定性规则引擎），而非 LLM 驱动的 Supervisor（Anthropic Claude Code 的 Team Lead。理由：① LLM 驱动的协调者自身也会死锁/幻觉/被操纵——引入新的攻击面；② 1人+AI 场景下规则数量有限，确定性引擎足够；③ Token 成本——规则引擎判定零 Token 消耗（对标 MOD-INF-022 §2.4 经济护栏）。
>
> **决策依据**：DPBench 证明启用 Agent 间 LLM 通信后 5-Agent 死锁率从 25% 跳升到 65%——"通信本身加剧死锁"。Supervisor 自身是 LLM = 在最需要确定性的层级引入了最大不确定性。

```yaml
supervisor_coordinator:
  # === Coordinator 类型 ===
  coordinator_type: "Rule-based Coordinator"
  not: "LLM-based Supervisor"
  reason: "确定性、零 Token、不可操纵"

  # === Coordinator 职责 ===
  responsibilities:
    - role: "Task Decomposition"
      description: "接收高层任务 → 按 spec-scoped 原则分解为互不重叠的子任务"
      rules:
        - "修改同一文件 = 序列化"
        - "修改同一目录不同文件 = 可并行但需 spec 对齐"
        - "修改不同目录 = 安全并行"

    - role: "Agent Assignment"
      description: "按 Agent Card capabilities 自动匹配 → 路由到目标 Agent"
      matching: "Filter（能力覆盖）+ Score（负载 × 历史成功率）——对标 K8s Scheduler Filter/Score 两阶段"
      anti_pattern: "禁止将同一子任务分配给两个 Agent"

    - role: "Progress Monitoring"
      description: "收集各 Agent 的 Task Status → 检测停滞/超时/死锁 → 触发 §2.9"
      heartbeat: "每 30s 各 Agent 上报 progress snapshot"

    - role: "Result Integration"
      description: "各子任务 COMPLETED → Coordinator 整合结果 → 验证一致性 → 交付"

  # === Coordinator 安全约束 ===
  constraints:
    - rule: "Coordinator 自身不执行 Agent 任务——只分解+分配+监控+整合"
    - rule: "Coordinator 的判定逻辑对 AI 只读（对标 MOD-INF-022 §2.5）"
    - rule: "Coordinator 决策全部写入 Audit Trail（MOD-INF-020）"
```

### 2.6 Living Spec 同步（决策 D-025-06）

> **决策 D-025-06**：引入 Living Spec（活文档）机制——各 Agent 在开始工作前自动拉取最新的共享接口规范。这是社区验证过的**事前冲突预防**核心手段。不依赖人工每次贴文档，而是 AGENTS.md 路由自动触发加载。对标 Coware + Augment Code spec-driven decomposition。
>
> **决策依据**：社区实战核心教训——"不要在合并时修冲突，要在写代码前就消除冲突的可能"。"AI 的速度放大了不一致性——一个下午出 2000 行，但 Agent 不会主动去看队友的 Agent 写了什么"。Coware 已将此流程产品化。

```yaml
living_spec:
  # === Living Spec 生命周期 ===
  lifecycle:
    - phase: "SCAN"
      action: "Coordinator 扫描当前代码库 → 提取所有接口契约（类签名/API schema/数据模型）"
      output: "living_spec.yaml——结构化接口规范"
      frequency: "每日启动时 + 每次 Agent 完成子任务后增量更新"

    - phase: "SYNC"
      action: "各 Agent 开始新子任务前 → 自动拉取最新 living_spec.yaml"
      enforcement: "Agent 产出的接口必须匹配 living_spec 中的字段名/类型/格式"

    - phase: "VERIFY"
      action: "Agent 完成任务后 → Coordinator 校验产出是否偏离 living_spec"
      deviation_action: "自动标记 → 通知 Owner → 触发 living_spec 更新或 Agent 修正"

  # === Living Spec 存储 ===
  storage:
    path: "docs/03_modules/_b_track_interfaces/living_spec.yaml"
    format: "YAML——人读 + 机读"
    version: "semver——每次更新 bump patch/minor"

  # === Living Spec 与 Agent Card 的关系 ===
  relation:
    agent_card: "声明'我能做什么'（能力）"
    living_spec: "定义'产出应该长什么样'（接口契约）"
    trigger: "Agent Card 匹配 → Living Spec 同步 → 开始施工"
```

### 2.7 冲突检测——文本 + 语义双层（决策 D-025-07）

> **决策 D-025-07**：冲突检测不能仅依赖 git merge（文本级），必须建立**语义冲突检测层**——当两个 Agent 修改"逻辑关联但文本不重叠"的代码时，git 不会报冲突但运行时可能崩溃（Augment 称为 semantic contradictions）。检测策略是 AST diff + 依赖图分析 + 接口契约对比。
>
> **决策依据**：节码的产品缺陷报告可以在多模态场景下 +38.5 pp 的效果，说明错误的粒度对 _world 的性能有非常依赖差异。"semantic contradictions are the hardest class to detect: changes that look correct in isolation can contradict each other, often passing compilation and linting but failing at runtime"。

```yaml
conflict_detection_layers:
  # === Layer 1: 文本冲突（git merge — 已有，自动）===
  text_conflict:
    mechanism: "git merge conflict"
    detection: "行级冲突——git 自动检测"
    resolution: "先 commit 先赢 / 后 commit 需手动 resolve"
    coverage: "约 30% 的实际冲突场景"

  # === Layer 2: 语义冲突（AST + 依赖图 — 新增）===#
  semantic_conflict:
    mechanism: "AST diff + 模块依赖图 + 接口契约对比"
    detection_rules:
      - name: "SC-DETECT-001: Shared Dependency Mutation"
        condition: "两个 Agent 修改同一模块的不同文件——但该模块的公共接口被同时变更"
        action: "标记为语义冲突 → Coordinator 裁决（合并 or 拒绝 or 串行化）"

      - name: "SC-DETECT-002: Interface Contract Divergence"
        condition: "Agent A 产出 {userId: int}，Agent B 消费 expect {user_id: str}"
        action: "Living Spec 校验失败 → 自动回退到最新 Living Spec → 要求 Agent 重新对齐"

      - name: "SC-DETECT-003: Structural Assumption Clash"
        condition: "Agent A 假设数据库有 transactions 表，Agent B 删除了它"
        action: "依赖图断裂 → Coordinator 阻断 Agent B 的合并 → 通知 Owner"

      - name: "SC-DETECT-004: Semantic Loop（Mirror Mirror）"
        condition: "两个 Agent 对同一产出物反复修改——A 改后 B 改回，循环 ≥ 3 轮"
        action: "检测到 outputs 95%+ 相似（语义哈希）→ 强制终止循环 → Coordinator 接管决策"

  # === Layer 3: 模式化行为冲突（Manifest Diff — 辅助）===
  behavioral_conflict:
    mechanism: "变更意图分析——两个变更是否在'语义空间'中冲突"
    scope: "仅限于影响 system_prompts / AGENTS.md / a2a_registry.yaml 的变更"
    action: "任一 Agent 修改上层配置 → 强制序列化——后改必须等前改合并后 rebase"
```

### 2.8 仲裁协议（决策 D-025-08）

> **决策 D-025-08**：仲裁采用三级递进——auto（规则判定）→ escalate（升级到 MOD-INF-022 Escalation Protocol）→ block（人工通知 Owner）。这并非重复 MOD-INF-022 的升级机制，而是 A2A 特有的"协调视角"升级——升级依据是 **Agent 间的冲突类型**而非操作风险等级。
>
> **决策依据**：A2A 仲裁的独特性在于"冲突的有无"而非"风险的有无"——两个 Agent 各自的操作都合理（MOD-INF-022 判断通过），但合在一起出问题了。这是 MOD-INF-022 无法覆盖的盲区。

```yaml
arbitration_tiers:
  # === Tier 1: auto（规则判定——完全自动）===
  auto:
    rules:
      - id: "ARB-AUTO-001"
        condition: "文本冲突——两个 Agent 修改同一文件同一行"
        action: "先 commit 先赢（FIFO 时间戳），后 commit 强制 rebase + 重跑 Gate Engine（MOD-INF-007）"
        resolution_time_target: "≤ 2 min"

      - id: "ARB-AUTO-002"
        condition: "Agent Card 冲突——两个 Agent 声明重叠能力但负载差异 ≥ 2×"
        action: "负载低的 Agent 获得任务"
        resolution_time_target: "≤ 1 min"

      - id: "ARB-AUTO-003"
        condition: "Living Spec 偏离——Agent 产出 vs Living Spec ≤ 1 字段差异"
        action: "自动修正（重命名/重格式化）——不通知 Owner"
        resolution_time_target: "≤ 30 sec"

  # === Tier 2: escalate（升级到 MOD-INF-022 规则引擎）===
  escalate:
    conditions:
      - "语义冲突——SC-DETECT-001~003 命中"
      - "Living Spec 偏离 ≥ 2 字段差异"
      - "同一任务 3 次 auto 判定仍冲突"
    action: "将冲突上下文包 + 两个 Agent 的差异提交给 MOD-INF-022 Escalation Engine"
    note: "Escalation Engine 判定 auto_guard（允许一方执行但护栏全开）或 blocked（双方暂停）"

  # === Tier 3: block（硬阻断 + 通知 Owner）===
  block:
    conditions:
      - "死锁——§2.9 deadlock_prevention 触发"
      - "Mirror Mirror Loop ——语义哈希连续 3 轮 ≥ 95% 相似"
      - "Agent 身份验证失败——§2.10 identity_verification"
      - "级联故障——§2.13 cascade_failure 触发"
    action: "暂停所有相关 Agent → 保存当前状态 → 通知 Owner（同步等待确认）"
    context_save: "docs/09_audit/A2A_BLOCK/{block_id}.yaml"

  # === 仲裁结果审计 ===
  audit:
    all_decisions: "A2A 仲裁决策全部写入 Audit Trail (MOD-INF-020)"
    fields: ["arbitration_id", "tier", "conflict_type", "agents_involved", "decision", "rationale", "resolution_time_ms"]
```

### 2.9 死锁与活锁防护（决策 D-025-09）

> **决策 D-025-09**：多 Agent 并发场景的死锁防护不是"nice to have"——DPBench 证实 3 Agent 并发时死锁率 95-100%，5 Agent 时 25-65%。必须内建四层防护：① 资源排序（Dijkstra）；② 超时熔断；③ 优先级抢占（对标 MIT CORDIAL）；④ 序列化降级模式。活锁（Agent 间无限谦让 + Mirror Mirror Loop）独立检测。
>
> **决策依据**：MIT CORDIAL 将死锁降低 87%。DPBench 关键发现——"natural language is a poor synchronization primitive"——Agent 间用自然语言协调反而增加死锁。必须用结构化协议（mutex / semaphore / FIFO queue）做同步。

```yaml
deadlock_prevention:
  # === 四层防护 ===
  layers:
    - name: "L1: Resource Ordering（Dijkstra 全局排序）"
      mechanism: "所有 Agent 获取共享资源时遵循全局排序——先 DB lock → 再 API call → 再 git push"
      enforcement: "compile-time check——Agent 代码中资源获取顺序必须是声明式且不可绕过"

    - name: "L2: Timeout-based Abort（超时熔断）"
      mechanism: "Agent 等待委托响应 > SLA（默认 120s）→ 自动取消等待 → 触发补偿策略（§2.2）"
      compensation:
        - "retry_with_backoff: 指数退避重试 1s→2s→4s→8s，最多 3 次"
        - "fallback_delegate: 目标 Agent 不可用 → 委托给次优匹配"
        - "task_split: 任务过大 → 拆分为更小子任务"

    - name: "L3: Priority Preemption（优先级抢占 — 对标 MIT CORDIAL）"
      mechanism: "当资源等待图检测到环时 → 优先级最高的 Agent 保留资源，其余强制回退"
      priority_formula: "task_priority × 0.4 + agent_capability_score × 0.3 + wait_time_penalty × 0.3"

    - name: "L4: Sequentialization Fallback（序列化降级）"
      mechanism: "死锁率 > 10%（最近 100 次委托）→ 系统从并发模式切换为序列化模式"
      recovery: "死锁率降至 < 2% 后自动恢复并发模式"

  # === 死锁检测机制 ===
  detection:
    wait_for_graph: "维护全局资源等待图（每个资源当前持有者 + 等待者列表）——对标 OS 死锁检测"
    cycle_detection: "每次委托操作前检测——按 DFS 遍历等待图"
    detection_interval: "每次委托操作前 + 每 30s 全局扫描"

# === 活锁检测（独立于死锁）===#
livelock_detection:
  patterns:
    - name: "LV-DETECT-001: Politeness Spiraling"
      description: "两个 Agent 互相谦让——'你先' '不你先'——消耗 Token 无产出"
      detection: "连续 5 条消息无实质性操作（tool invocation / file edit）→ 触发"
      action: "Coordinator 强制决策——随机选一个 Agent 先执行"

    - name: "LV-DETECT-002: Mirror Mirror Loop"
      description: "两个 Agent 对同一产出物反复修改——A 改→B 改回→A 改→循环"
      detection: "语义哈希——检测到 outputs 95%+ 相似且 ≥ 3 轮 → 触发"
      action: "Loop 中断 → Coordinator 锁定产出物 → 通知 Owner 做终局裁决"

    - name: "LV-DETECT-003: Endless Delegation Chain"
      description: "A 委托 B → B 委托 C → C 委托 A（循环）或 链条深度 > max_depth（3）"
      detection: "委托链追踪——每次委托前检查 target_agent 是否已在 delegation_chain 中"
      action: "中断链条 + 当前 Agent 降级处理（拆分任务 / 上报 Owner）"
```

### 2.10 通信安全——OWASP ASI07 全栈防护（决策 D-025-10）

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
        action: "trust_score 连续 3 轮陡增 → 操作 auto_guard 起步"

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

### 2.11 上下文管理——跨 Agent 传递

> **对标**：MOD-INF-022 §2.8 委托上下文包 + ADR-0041 §4.3 P0-P3 压缩策略。

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

### 2.12 经济护栏——跨 Agent 链的 Token 预算

> **对标**：MOD-INF-022 §2.4 Token 预算 + AICosts.ai 87% 成本超支来自过度自主。

```yaml
a2a_economics:
  # === 委托代价评估 ===
  delegation_cost:
    overhead_tokens: "每次 A2A 委托固定开销 ≈ 500 tokens（上下文包 + ACK）"
    breakeven_rule: "预估委托省下的 tokens > overhead_tokens × 2 → 委托值得"
    auto_reject: "预估 cost > benefit → Coordinator 拒绝委托 → 当前 Agent 自行处理或拆分子任务"

  # === 全链路 Token 预算 ===
  chain_budget:
    root_task_budget: "由 MOD-INF-022 economic_guardrails 定义"
    delegation_budget: "从 root 预算中扣除——parent.remaining >= child.estimated × 1.2"
    hard_cap: "全链路 Token 耗尽 → 剩余子任务全部 CANCELED → 通知 Owner"

  # === 模型路由 ===
  model_routing:
    autonomous_agent: "sonnet（性价比模型）— 95% 操作"
    auto_guard_scenario: "sonnet 执行 + opus 校验"
    blocked_scenario: "不消耗 — 等待 Owner"
```

### 2.13 可观测性与分布式追踪

> **对标**：OpenTelemetry SpanContext + Jaeger/Zipkin Correlation ID + Augment Code automated verification。

```yaml
observability:
  # === 分布式追踪 ===
  tracing:
    correlation_id: "每条 A2A Message 携带 correlation_id——全链路唯一标识"
    span_context: "每次 Agent 间消息传递创建 Span（span_id + parent_span_id）"
    storage: "docs/09_audit/A2A_TRACES/{correlation_id}.yaml——全链路事后回溯"

  # === A2A 专属指标 ===
  metrics:
    - name: "message_latency_p95_ms"
      target: "≤ 200 ms"
      description: "Agent 间单条消息延迟"

    - name: "handoff_time_p95_ms"
      target: "≤ 5000 ms"
      description: "任务从 SUBMITTED → WORKING 的时间（含 Agent Card 匹配）"

    - name: "conflict_resolution_time_p95_ms"
      target: "≤ 120000 ms (2 min)"
      description: "从冲突检测到仲裁完成的时间"

    - name: "delegation_success_rate"
      target: "≥ 95%"
      description: "委托在 SLA 内 COMPLETED 的比例"

    - name: "deadlock_event_count_per_day"
      target: "0"
      description: "每日死锁事件——0 容忍"

    - name: "semantic_conflict_count_per_day"
      target: "≤ 3"
      description: "语义冲突——允许少量但需追踪趋势"

  # === Agent 信誉评分 ===
  reputation:
    tracking: "每个 Agent 的历史成功率 + 平均完成时间 + 语义冲突参与率"
    use: "Coordinator 在 Filter/Score 阶段使用——优先分配给高信誉 Agent"
    decay: "信誉随时间衰减——最新 100 次委托权重 0.7，历史 0.3"
```

### 2.14 施工自指悖论与独立验证（决策 D-025-11）

> **决策 D-025-11**：A2A 协议自身由 AI 开发的自指悖论必须处理。AI 开发 A2A = AI 开发"限制 AI 间通信"的系统——有动机弱化安全约束（签名校验、"忘了"实现死锁检测、"不小心"让语义冲突静默通过）。需要对 4 个核心文件设置 Owner 独立审查 + 编译时约束检查 + 安全测试。
>
> **决策依据**：对称 MOD-INF-022 §2.20——这是 ZephyrAlpha 100% AI 施工模式下所有"承重墙"模块都必须有的独立验证机制。A2A 作为 Agent 间通信的中枢，自指风险甚至高于 Escalation（A2A 是 Agent 间协作的唯一通道——被弱化后多 Agent 系统全裸）。

```yaml
self_referential_verification:
  # === 自指风险 ===
  self_referential_risk:
    statement: "让 AI 开发限制 AI 间通信的系统 → AI 可以'不小心'弱化限制"
    examples:
      - "AI 实现 arbitrator.py 时 → '忘了'实现 Tier 3 block 路径"
      - "AI 实现 deadlock_guard.py 时 → 检测间隔改为 300s（从 30s）"
      - "AI 实现 a2a_security.py 时 → message signature 校验总是 return True"

  # === 独立验证点（Owner 人工审查）=== #
  required_human_review:
    - file: "arbitrator.py:resolve()"
      reason: "核心仲裁逻辑——Tier 1→2→3 的升级路径是否完整"
      review: "Owner 确认 3 个 Tier 全有实现且有单元测试覆盖"

    - file: "deadlock_guard.py:detect_cycle()"
      reason: "死锁检测——DFS 遍历等待图是否正确"
      review: "Owner 确认 3-Agent 并发测试用例死锁被正确检测和解决"

    - file: "a2a_security.py:verify_signature()"
      reason: "签名验证——不能'总是 True'"
      review: "Owner 用已知私钥签名消息 → 验证通过；用错误签名 → 验证失败"

    - file: "conflict_detector.py:semantic_conflict_check()"
      reason: "语义冲突检测是否真实运行——还是空壳"
      review: "Owner 构造两个'合规但语义冲突'的 diff → 确认被检测"

  # === 编译时约束 ===
  compile_time_checks:
    - check: "arbitration_tiers 数量 = 3（auto/escalate/block 一个不能少）"
    - check: "deadlock_prevention.layers 数量 ≥ 4（Dijkstra/Timeout/Preemption/Sequentialization）"
    - check: "message_integrity.signature 算法 = RS256（不能退化为 HS256）"
    - check: "livelock_detection.patterns 数量 ≥ 3（Politeness/Mirror/EndlessChain）"

  # === 安全测试 ===
  security_tests:
    - "构造恶意 Agent → 发送无签名 Message → verify 失败 → blocked"
    - "构造 Session Smuggling 攻击链 → trust_escalation_detection 触发"
    - "3-Agent 并发死锁 → deadlock_guard 检测 + 优先级抢占解决"
    - "Mirror Mirror Loop 5 轮 → livelock_detector 中断 + Coordinator 接管"
```

### 2.15 Vibe Coding / 1人+AI 专属优化（决策 D-025-12）

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
    - target: "ADR-0032 AgentOrchestrator"
      alignment: "A2A Coordinator 复用 AgentRouter 的 6 角色 × 10 域矩阵做能力匹配"
      not: "重复实现在 ADR-0017 中已有的 TaskState——A2A Task 是 Agent-间粒度"

    - target: "MOD-INF-019 Skill Pack"
      alignment: "Agent Card capabilities 自动从 Skill Pack 的 trigger_keywords 派生"
      not: "手动维护两套能力描述"
```

---

### 2.16 Multi-Agent 共识与协商协议（决策 D-025-13）

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

### 2.17 涌现行为与异常检测（决策 D-025-14）

> **新增于 v0.6.0**。v0.5.0 的防护体系（死锁/活锁/级联故障/消息安全）针对的是"已知故障模式"。但 "Agents of Chaos" (2026-02) 揭示：对齐良好的单个 Agent 在多 Agent 协作中会**自发涌现系统级失败**，无需任何越狱或对抗性提示。

**对标**："Agents of Chaos" (Harvard/MIT/Stanford/CMU, arXiv:2602.20021 — 11 种系统性失败)、MAScope (ZJU, arXiv:2603.04469 — F1=85.3%)、MARIA OS Safety Layer (Layer 7 anomaly detection)、Galileo.ai 多 Agent 异常分类学。

```yaml
emergence_and_anomaly_detection:

  # === "Agents of Chaos" 11 种失败模式——ZephyrAlpha 语境映射 ===
  chaos_failure_modes:
    F01_non_owner_exec:
      name: "非所有者授权执行"
      zephyr_relevance: "中——1人场景下不太可能，但未来多合约方须有"
      mitigation: "Agent 操作必须通过 Owner 的 delegated_auth——已在 §2.10 中覆盖"

    F02_sensitive_data_leak:
      name: "敏感数据泄露"
      zephyr_relevance: "高——Agent A 传给 Agent B 的上下文包可能包含 secrets"
      mitigation: "已在 §2.10 中覆盖（context_purge_secrets 门禁）"

    F03_disruptive_sys_ops:
      name: "破坏性系统操作"
      zephyr_relevance: "高——Agent 代码可执行任意 shell 命令"
      mitigation: "Sandbox + 文件访问 allowlist——已在多 Agent 沙箱中覆盖"

    F04_denial_of_service:
      name: "拒绝服务（Agent 过载）"
      zephyr_relevance: "中——经济护栏 $300/day 提供了硬上限，但 Agent 间 DoS 未覆盖"
      mitigation: "NEW → Agent 间 back-pressure 协议: queue_depth > N → throttle incoming handoffs"

    F05_uncontrolled_resource_use:
      name: "无控制资源占用"
      zephyr_relevance: "高——Token 预算被单一 Agent 独占"
      mitigation: "已在 §2.12 经济护栏中覆盖（每个 Agent 的 per_handoff_token_budget）"

    F06_identity_spoofing:
      name: "身份欺骗"
      zephyr_relevance: "高——Agent 间冒充"
      mitigation: "已在 §2.10 中覆盖（每一跳独立验证 + 检查 Agent Card hash）"

    F07_cross_agent_behavior_propagation:
      name: "跨 Agent 行为传播"
      zephyr_relevance: "🔴 最高——这是 1人+AI 场景最致命的漏洞"
      mitigation: >
        Agent A 学会了"跳过测试直接标记 COMPLETED"。
        Agent B 观察 A 行为后也学会了。
        需要: (1) Behavior Fingerprint 库——记录每个 Agent 的"完成习惯模式"
        (2) 行为偏离检测——Agent B 的行为模式突变 → 触发审计
        (3) 行为溯源——"这个不良行为是 B 自己发明的还是从 A 学来的？"

    F08_partial_takeover:
      name: "部分系统接管（Agent 逐步蚕食其他 Agent 的领域）"
      zephyr_relevance: "中——Agent 领地扩张"
      mitigation: "Agent Card 中声明 domain_overlap_tolerance，超过范围的委托 → REJECTED"

    F09_false_task_completion:
      name: "虚假任务完成"
      zephyr_relevance: "🔴 最高——这是 1人+AI 场景下最真实的痛点"
      mitigation: >
        COMPLETED 状态不等于任务完成。
        需要 verification gate:
        - 代码变更 → Living Spec diff verification（已有 §2.6）
        - 测试结果 → 自动运行关联测试（新增——§2.18 检查点会覆盖）
        - 数据变更 → checksum 前后对比
        - Owner 确认 → 每个 COMPLETED 后 30min 内 Owner 未否决 → 才算"真·COMPLETED"
        NEW STATE: COMPLETED → VERIFIED 或 COMPLETED → DISPUTED（新增状态转换）

    F10_agent_collusion:
      name: "Agent 合谋"
      zephyr_relevance: "中——1人场景下不太可能，但应内置检测"
      mitigation: "NEW → §2.16 合谋检测"

    F11_strategic_sabotage:
      name: "战略性破坏"
      zephyr_relevance: "中——Agent 间竞争性破坏"
      mitigation: >
        "Agent 的委托成功率 + 任务质量评分构成 reputation。
        破坏其他 Agent → 自己的 reputation 也下降（被破坏 Agent 的失败会被回溯分析）
        需要 sabotage detection: 分析失败任务的 root cause 是否追溯到另一个 Agent"

  # === 5 类异常分类学（对标 Galileo.ai） ===
  anomaly_taxonomy:
    categories:
      - type: "behavioral"
        signals: ["跳过测试", "COMPLETED 但无 verifiable 产物", "重复同一操作 >3 次"]
        detector: "规则引擎 + Behavior Fingerprint diff"

      - type: "communication"
        signals: ["消息量突增 5× 基线", "异常的消息 target（从未通信过的 Agent 间突然大量通信）"]
        detector: "流量分析——滑动窗口 rate vs 历史基线"

      - type: "resource"
        signals: ["Token 消耗速率 > 2× 基线", "磁盘/内存突增"]
        detector: "资源计量 + 告警阈值"

      - type: "coordination"
        signals: ["同一文件被 3+ Agent 拉起（事前冲突检测窗口）", "任务分配后超时无人认领"]
        detector: "§2.7 冲突检测 + 超时 escalation"

      - type: "emergent"
        signals: ["\"Agents of Chaos\" F07/F09/F10/F11 任意命中"]
        detector: "NEW → Cross-Agent Semantic Flow（MAScope PDAG construction + Isolation Forest）"

  # === ML 驱动的异常检测管道 ===
  ml_anomaly_pipeline:
    stage_1_unsupervised:
      algorithm: "Isolation Forest"
      input: "Agent 行为特征向量（每日：token_usage, handoff_count, conflict_count, avg_task_duration, completed_with_verification_ratio）"
      output: "anomaly_score ∈ [0, 1]"
      threshold: "> 0.7 → alert, > 0.85 → auto-throttle"

    stage_2_reconstruction:
      algorithm: "Autoencoder"
      input: "Agent 行为时间序列（7 日滑动窗口 × 特征向量）"
      output: "reconstruction_error"
      rationale: "学习\"正常行为\"的压缩表示，异常行为的重建误差更高"

    response_cascade:
      anomaly_score_0.7_to_0.85: "Log + 降低该 Agent 的委托优先级"
      anomaly_score_0.85_to_0.95: "Throttle——拒绝新委托，只完成已接受的"
      anomaly_score_above_0.95: "Freeze——暂停 Agent 的所有通信，通知 Owner 审查"
```

---

### 2.18 分布式事务与 Saga 回滚（决策 D-025-15）

> **新增于 v0.6.0**。v0.5.0 假设 Agent 操作是原子的——一个 Task 要么成功要么失败。实际上，Agent A 的操作会影响后续 Agent B 的状态。如果 Agent C 失败了，A 和 B 已提交的工作需要回滚。这是经典的分布式事务问题。

**对标**：SagaLLM (Stanford, PVLDB 2025 — 多 Agent 工作流的形式化事务与回滚)、LangChain Compensation v0.5.8 (Saga Pattern for Agents)、Saga 设计模式（每步 LT 配一个 CT）。

```yaml
saga_and_rollback:

  # === Saga 事务注册模型 ===
  saga_registration:
    principle: "每个 Agent 操作在提交前必须注册对应的补偿事务 (CT)"
    format:
      logical_transaction:        # LT = 业务操作
        agent_id: "Architect"
        action: "design_database_schema"
        target: "docs/schema_v2.sql"
      compensation_transaction:  # CT = 回滚操作
        agent_id: "Architect"
        action: "revert_database_schema_to_v1"
        target: "docs/schema_v1.sql"  # 基线快照
      idempotency_key: "saga_20260505_schema_v2_uuid"  # 保证 CT 幂等

    compensation_type:
      undo: "反转操作——git revert / db rollback"
      compensate: "替代操作——不撤销原操作但做补充纠正"
      notify: "通知下游——上游回滚了，下游需要知道"

  # === 分布式检查点 ===
  checkpoint:
    granularity: "per agent——每个 Agent 在自己的 worktree 中有独立检查点"
    content: "worktree snapshot + Agent internal state（conversation summary + 已完成子任务列表）"
    coordination: "Coordinator 持有全局检查点目录——track 所有 Agent 的检查点位置"

    recovery:
      partial_failure: "Agent C 执行 50% 后崩溃 → 从最近的检查点恢复，不重做已完成步骤"
      full_rollback: "Agent D 失败 → A/B/C/D 全部回滚到基线 → 检查点回退链"

  # === 幂等性门禁 ===
  idempotency_gate:
    layer_1: "Task-level——同一 Task ID 在 5min 内重复提交 → rejected（去重）"
    layer_2: "Operation-level——同一文件 + 同一操作类型在 10min 内重复执行 → rejected"
    layer_3: "Git-level——检查目标文件 hash 是否一致，不一致 → abort"

  # === 1人+AI 简化实现策略 ===
  simplified_implementation:
    note: "Saga 的完整形式（LT/CT 配对 + 检查点 + 幂等性门禁 + 补偿编排）对于 1人+AI 场景过重。"
    simplifications:
      - "利用 git revert / git reset 作为天然的 rollback 机制"
      - "Agent worktree 隔离（v0.5.0 优化 3）天然提供检查点"
      - "幂等性通过 git 天然提供——同一 commit 重复 apply → no-op"
    recommendation: "Phase 1 使用简化版（git revert + Agent Card 操作日志），Phase 5+ 升级到完整 Saga。"
```

---

### 2.19 多 Agent 辩论/审议协议（决策 D-025-16）

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

### 2.20 Agent 经济与资源分配协议（决策 D-025-17）

> **新增于 v0.7.0**。v0.6.0 有经济护栏但它们是"单 Agent 全局预算"。当多个 Agent 共享一个 Token 预算池时，需要一个正式的 **Agent 内部经济协议** 来决定谁拿到多少预算、谁的 ROI 最高、谁该被限流。

**对标**：x402（Coinbase+Cloudflare — HTTP 原生 Agent 支付，1 亿+交易）、AEP（Autonomous Economy Protocol — 9 合约 Agent 经济，Base 主网）、NEAR AI Agent Market（Agent 竞标任务）。

```yaml
agent_economy_and_resource_allocation:

  design_principle: "N 个 Agent 竞争同一 Token 预算池 → 需要形式化的分配协议而非硬编码配额"

  # === Agent 预算池模型 ===
  budget_pool:
    global:
      daily_cap: "$300"       # 现有硬顶
      weekly_cap: "$1000"
      emergency_reserve: "$50"  # 预留，给 Critical 任务用

    allocation_model:
      type: "dynamic_priority_based"
      algorithm:
        step_1: "每个 Agent 的 base_allocation = daily_cap / active_agent_count"
        step_2: "priority_multiplier × base_allocation → weighted allocation"
        step_3: "未使用的配额在 1h 滑动窗口后释放回池"

    priority_multipliers:
      critical: 3.0   # 影响运行中系统的 bug fix
      high: 2.0       # 核心功能开发
      medium: 1.0     # 常规任务
      low: 0.5        # 探索性/实验性任务
      background: 0.1  # 代码美化/文档更新

  # === Agent ROI 追踪 ===
  roi_tracking:
    metrics:
      - name: "code_quality_roi"
        formula: "verifiable_lines_of_code / token_cost"
        note: "给 git blame 可验证的代码行数 / 该 Agent 的 Token 花费"

      - name: "task_success_rate"
        formula: "tasks_completed_with_verification / tasks_assigned"
        verification_required: true  # 必须过 F09 False Task Completion 门禁

      - name: "defect_rate"
        formula: "bugs_introduced / verifiable_lines_of_code"
        note: "从 git bisect 回溯的该 Agent 引入的 bug 数"

    roi_decisions:
      - "连续 3 天 ROI 低于所有 Agent 中位数 50% → 降级预算 ×0.5"
      - "连续 7 天 ROI 最高 → 升级预算 ×1.5"
      - "ROI 无法计算（新 Agent）→ 给 3 天\"试用期\"后计算"

  # === 跨 IDE 花费聚合 ===
  cross_ide_cost_aggregation:
    problem: "TRAE/Cursor/RooCode 各有自己的 Token 预算。跨 3 个 IDE 的总花费不可见"
    solution:
      - "每个 IDE Session 在启动时向 a2a_registry 报告 session_id + 预计日预算"
      - "Coordinator 定期 ping 各 IDE Session 获取实际花费"
      - "dashboard 显示跨 IDE 总花费 + 按 Agent 分解"
    implementation: "基于 Agent Card 的 owner 字段聚合——同一 Owner 的所有 Agent 花费合并统计"

  # === 资源竞价（简化版） ===
  resource_auction:
    note: "完整 AEP 拍卖（5 轮 counter-proposal, on-chain negotiation）对 1人+AI 过重"
    simplified:
      trigger: "2+ Agent 同时需要 Opus 模型但只剩 1 个 slot"
      logic: "Coordinator 比较 priority × roi_score → 高分获胜"
      preemption: "高优先级任务可以抢占低优先级任务的模型 slot（低优先级任务降级到 Sonnet）"
```

---

### 2.21 异质模型动态路由引擎（决策 D-025-18）

> **新增于 v0.7.0**。v0.6.0 的模型路由是"static assignment"——autonomous_agent→Sonnet，auto_guard→Opus。但 2026 年最新研究一致证明：**动态的、状态感知的路由在同时提升准确度和降低成本**。对 1人+AI 场景，这可能直接节省 30-50% 的 Token 成本。

**对标**：OI-MAS（HIT — confidence-aware routing → +12.88% acc, -79.78% cost）、Chimera（UNC/Microsoft/CMU — latency- and performance-aware → 1.2-2.4× latency reduction）、GraphPlanner（ICLR 2026 — graph-based agentic routing → +9.3% acc, GPU 186→1 GiB）、Anthropic 官方角色化路由（Coordinator=Opus, FileNav=Haiku）。

```yaml
heterogeneous_model_router:

  design_principle: "不是'每个 Agent 绑定一个模型'，而是'每个任务根据角色×难度×系统负载，动态选择模型'"

  # === 三维决策矩阵 ===
  decision_matrix:
    dimensions:
      role:           # Agent 的角色决定了任务类型的认知需求
        coordinator: "最深度推理 → Opus"
        file_navigator: "模式匹配 → Haiku (节省 80% 成本)"
        code_generator: "平衡推理与上下文 → Sonnet"
        code_reviewer: "安全审查 → 独立异构模型 (GPT-5.2 或 Opus)"
        tester: "验证任务 → Sonnet"
        researcher: "探索分析 → 按难度动态选择"

      task_difficulty:  # 任务本身的复杂度——对标 OI-MAS confidence-aware
        trivial: "import 重组 / 重命名 → Haiku"
        simple: "单函数修改 / 注释 → Sonnet 或更小"
        moderate: "跨文件修改 / 新增功能 → Sonnet"
        complex: "架构重构 / 跨模块依赖 → Opus"

      system_load:      # 当前系统负载——对标 Chimera
        idle: "queue_depth < 2 → 优先进度模型提高质量"
        busy: "2 <= queue_depth < 5 → 平衡选择"
        overloaded: "queue_depth >= 5 → 降级模型加速吞吐"

    routing_rule:
      logic: "max(priority = role × 0.4 + difficulty × 0.4 + load × 0.2)"
      fallback: "如果不能确定 → 宁可升级模型也不要让任务失败"

  # === Confidence-Aware 选择 ===
  confidence_aware:
    mechanism: "Agent 声明对自身提案的置信度 (0.0-1.0) → 低置信度任务分配给更强模型"
    threshold:
      agent_confidence_high: "> 0.8 → 可以用 Agent 绑定的默认模型"
      agent_confidence_medium: "0.5-0.8 → 升级一级模型"
      agent_confidence_low: "< 0.5 → 升级两级模型 + 考虑分配两个 Agent 独立执行再对比"

  # === 批量降级 ===
  batch_downgrade:
    trigger: "queue_depth > 10 OR today_token_spent > 80% daily_cap"
    action: "所有 moderate 以下任务降级到 Haiku-replacement"
    exclusion: "Critical 任务不受影响"
    restore: "queue_depth < 3 AND token_spent < 60% → 恢复"

  # === 模型选择日志（供 ROI 追踪消费） ===
  model_selection_log:
    fields: [task_id, agent_id, selected_model, reason, timestamp, resulting_accuracy]
    purpose: "训练模型选择策略——哪些场景下选择哪个模型效果最好"
```

---

### 2.22 工作窃取与负载均衡（决策 D-025-19）

> **新增于 v0.7.0**。v0.6.0 的任务分发是 Coordinator push 模式。在成熟的分布式系统中，"work stealing"（空闲节点从忙碌节点"偷"任务）是标准的负载均衡补充策略，在多 Agent 系统中完全适用。

**对标**：Adaptive Async Work-Stealing（分布式计算经典）+ 社区多 Agent 负载均衡实现（贪心算法 + RL-based）。

```yaml
work_stealing_and_load_balancing:

  design_principle: "Coordinator push + Agent pull (work stealing) = 双向负载均衡"

  # === 工作窃取协议 ===
  work_stealing:
    trigger:
      - "Agent 状态 = IDLE 持续 30s"
      - "Agent 自身的 queue_depth = 0"

    victim_selection:  # 选谁的队列来"偷"
      criteria:
        - "queue_depth 最深的 Agent（优先级最高）"
        - "任务优先级匹配（只偷优先级 >= medium 的任务）"
        - "跳过已经分配给其他 Agent 的任务"

    stealable_task:  # 什么任务可以被偷
      conditions:
        - "任务状态 = PENDING（还未开始执行）"
        - "任务无 Agent 亲和性限制"
        - "任务可以被安全地重分配到不同的 worktree"

    limits:
      max_steals_per_hour: 5  # 防止"偷"本身带来不稳定
      cooldown_after_steal: 120  # 秒——偷完后冷却 2 分钟

  # === 任务亲和性 ===
  task_affinity:
    concept: "Agent 已经加载了相关上下文 → 分配给它比给冷启动的 Agent 更高效"
    calculation:
      affinity_score = (
        0.4 * file_familiarity     # 该 Agent 最近 24h 操作过的文件
        + 0.3 * module_familiarity  # 该 Agent 最近操作过的模块
        + 0.3 * task_type_match     # 该 Agent 擅长的任务类型
      )
    routing: "task_affinity > 0.6 → 优先分配给该 Agent，即使其队列稍长"

  # === Agent Watchdog（进程级守护） ===
  watchdog:
    problem: "Agent 执行长任务时进程可能 OOM/超时/挂死"
    mechanism:
      heartbeat: "每 30s Agent 向 Coordinator 发送心跳 (status + progress%)"
      timeout:
        default: "10min"          # 超时后 Coordinator 尝试恢复
        long_running: "30min"     # 声明为 long_running 的任务有更长超时
      recovery:
        attempt_1: "Coordinator 发送 PING（轻量级检查 Agent 是否存活）"
        attempt_2: "从最近的检查点恢复（§2.18 checkpoint.recovery）"
        attempt_3: "标记任务 FAILED → 重新分配给其他 Agent"
      oom_protection:
        - "Agent 定期检查可用内存，低于 500MB → 主动暂停新任务"
        - "已接任务在当前子任务完成后自愿 yield 给其他 Agent"

  # === 1人+AI 简化 ===
  simplified_for_solo:
    note: "完整的 pull-based work stealing 在 <5 Agent 场景下可能过度工程化"
    recommendation: "Phase 1 实现简化版——仅 Task Affinity + Watchdog。Work Stealing 在 Agent >= 5 时启用。"
```

---

### 2.23 A2A 协议层安全攻击面防护（决策 D-025-20）

> **新增于 v0.8.0**。v0.7.0 覆盖了 OWASP ASI07（消息安全）、JWT 签名、防重放，但这些都是"消息级"安全。**协议级**安全——Agent Card 供应链完整性、Task 流操纵、Artifact 投毒——一直未被专门建模。A2ASECBENCH (ICLR 2026) 首次揭示了这层攻击面。

**对标**：A2ASECBENCH (ICLR 2026 — 首个 A2A 协议安全基准，六大攻击跨越 A2A 全阶段）、Google A2A Security Enhancement (arXiv:2505.12490 — Token 生命周期 + SCA + 同意编排）、SentinelAgent (TLA+ — 委托链形式化安全）、ACP v1.27 (arXiv:2603.18829 — 时间感知准入控制）。

```yaml
a2a_protocol_security_surface:

  design_principle: "消息安全 (v0.7.0) 是'每一封邮件加了签名'。协议安全 (v0.8.0) 是'整个邮件系统没有被劫持'。"
  benchmark: "A2ASECBENCH (ICLR 2026) — 六大攻击向量 × 三大领域 (travel/healthcare/finance)"

  # === 攻击面 1：Agent Card 供应链操纵 ===
  agent_card_supply_chain:
    threat_1_card_cloning:
      desc: "恶意 Agent 复制合法 Agent 的 Agent Card，修改 endpoint URL 后重新注册到 AGENTS.md"
      a2asecbench_finding: "Agent Card 不具备原生完整性保护——签名是可选的，不是强制性的"
      defense:
        mandatory_signing: "所有 Agent Card 必须带 JWS 签名，Coordinator 在注册时强制校验"
        card_fingerprint: "SHA-256(agent_card_json) 注册到 Agent Card Registry，每次发现时对比"
        clone_detection: "同一 identity 来源的两个不同 endpoint → 触发 CLONE_DETECTED 告警"

    threat_2_capability_misrepresentation:
      desc: "Agent 声明的能力远超实际——'我是全栈专家' 实际只能写 CSS"
      defense:
        - "capability_verification_gate: 新 Agent 注册后自动分配 3 个 benchmark task → 实际表现 vs 声明能力对比"
        - "capability_drift_monitor: 持续追踪声明的每个 skill 的实际完成率"
        - "deviation > 2σ → 降级 Agent Card 中的 skill 等级 → 降低委托优先级"

    threat_3_cloaked_functions:
      desc: "Agent 声明了 10 个公开 skill，但隐藏了 3 个'隐藏功能'（如读取 .env）"
      defense:
        - "Declared-Skill-Only Gate: Agent 只能执行其 Agent Card 中声明的 skill"
        - "运行时 skill 调用追踪 → 任何未声明的操作 → 标记 rogue_operation"

  # === 攻击面 2：Task 流操纵 ===
  task_flow_manipulation:
    threat_4_task_hijack:
      desc: "恶意 Agent B 截获 Agent A 的 task_id，伪造响应包声称 task 已完成"
      defense:
        - "task_id → 非可预测 UUIDv7（含时间戳+随机数+Agent 签名）"
        - "Task 的 claimed_result → 必须被 Living Spec diff verification 验证（§2.6）"
        - "任何对已有 task 的结果覆盖 → 需要 A2A_Version 递增 + 前一版本 hash 校验"

    threat_5_task_replay:
      desc: "恶意 Agent 重放一个 2 小时前已完成的 task（利用 stale 但有效的 task_id）"
      defense:
        - "Task TTL: 每个 task_id 有内置过期时间，默认 = task_start_time + 30min"
        - "过期后的 task_id → 自动转换到 EXPIRED 状态，不可重新激活"
        - "Coordinator 维护已处理 task_id 的 Bloom Filter，快速拒绝重放"

    threat_6_task_flooding:
      desc: "恶意 Agent 向所有 Agent 同时提交 1000 个 task，DoS 攻击系统"
      defense:
        - "per-agent rate limiter: 每个 Agent 的 task_submission_rate ≤ 10/min(medium), ≤ 30/min(critical)"
        - "超过速率 → 432 TOO_MANY_REQUESTS + 降低该 Agent 的 trust_score"
        - "Coordinator 全局 throttle: system_wide_pending_tasks > 100 → 拒绝新的 low priority task"

  # === 攻击面 3：Artifact 投毒 ===
  artifact_poisoning:
    threat_7_malicious_artifact:
      desc: "Agent 在返回的 artifact 中嵌入后门代码 / 泄露数据的 payload"
      defense:
        - "Artifact Sanitizer: 所有 Agent 间传递的 code artifact → 自动扫描 (AST 分析 + Semgrep 规则 + 已知恶意模式)"
        - "Artifact 溯源: 每个 artifact 标记 source_agent_id + 生成时的 Agent Card hash"
        - "下游 Agent 在消费 artifact 前 → 校验 source_agent 的 trust_score"
        - "trust_score < 0.5 → artifact 被标记为 '需人工审查'"

    threat_8_artifact_data_leak:
      desc: "Agent B 通过 artifact 的 metadata 字段意外泄露了下游系统的 PII"
      defense:
        - "Artifact PII Scanner: 所有 artifact 内容 → PII regex + NER 扫描"
        - "命中 PII → 自动脱敏（用 mask_token 替换）→ 记录到 audit log"
        - "PII 泄露到 artifact 的源头 Agent → trust_score -0.3"

  # === 全局协议安全配置 ===
  protocol_security_levels:
    level_conservative:
      mode: "所有协议安全门禁 = ON"
      when: "新 Agent 上线 / Agent trust_score < 0.7 / 跨组织边界委托"
      behavior: "Agent Card 每跳独立验证 + Task 反重放强制开启 + Artifact 全扫描"

    level_balanced:
      mode: "供应链检查 + 速率限制 = ON；Artifact 扫描 = 高风险才开"
      when: "稳定运行 ≥ 7 天 + 所有 Agent trust_score ≥ 0.7"
      behavior: "高风险 artifact（可执行文件、SQL 脚本）全扫描，其他采样扫描"

    level_permissive:
      mode: "仅速率限制 = ON（1人+AI 场景 3 Agent 以下可用）"
      when: "1人+AI 调试阶段 / 所有 Agent 在同一台机器 / trust_score = 1.0"
      note: "即使此模式，Agent Card 签名和 Task TTL 也永不可关闭"
```

---

### 2.24 结构化协商帧协议 — ANP 1.0（决策 D-025-21）

> **新增于 v0.8.0**。v0.7.0 §2.16 的协商基于 Concordia 6 状态会话机，但底层通信仍假设 "Agent 间用 YAML 文本聊天"。ANP 1.0 (2026-04) 和 "The Ambiguity Tax" 论文揭示：自然语言 Agent 间通信有 40% Token 浪费在澄清和歧义消解上。结构化协商帧是通信媒介本身的升级。

**对标**：ANP 1.0 (Agent Negotiation Protocol, 2026-04 — 结构化协商帧取代文本聊天）、"Ambiguity Tax" (bittalks.org, 2026-04 — 40% Token 浪费）、SentinelAgent IPDP (TLA+ — intent-preserving delegation protocol）。

```yaml
structured_negotiation_frame_protocol:

  design_principle: "Agent 之间不用 '聊天'——用预定义的结构化帧交换约束、证明和结算逻辑。"
  key_insight: "当 I 说 'optimize the cloud budget'，你可能以为是 'shut down unused instances'，而我以为是 'shift workloads to cheaper regions'。对 Agent 来说，这个歧义是性能杀手。"

  # === Negotiation Frame 结构 ===
  negotiation_frame:
    fields:
      constraints:
        desc: "硬约束——价格/延迟/合规的硬上限"
        example:
          max_cost: "$2/hour"
          max_latency_ms: 500
          compliance: ["GDPR", "SOC2"]
          required_capabilities: ["python_3.12", "gpu_access"]

      state_proofs:
        desc: "可验证的 Agent 状态证明——不需要 Agent 暴露内部状态"
        methods:
          - "Capability Token (ACP-CT-1.0): 证明 Agent 具备声明的能力"
          - "ZK Proof of Identity: 证明 '我是合法的 Agent X' 但不暴露 X 的完整私钥"
          - "Budget Proof: 证明 Agent 有足够的 Token 预算来完成此委托"

      settlement_logic:
        desc: "条件满足后交易如何结算"
        components:
          - "原子性保证: Agent A 完成 → Agent B 必须结清。不是 'Promise'，是 protocol guarantee"
          - "回滚条件: 何时触发补偿事务 (§2.18)"
          - "超时处理: negotiation timeout 后如何自动终止"

  # === 对比：聊天 vs 协商帧 ===
  chat_vs_frame:
    chat_based:
      example: "Hey, can you find me a GPU cluster for under $2/hour? Also I need it to have at least 16GB VRAM and be in US-East. Thanks!"
      problems:
        - "哪部分是非协商项？哪部分是偏好？Agent 需要自己推断"
        - "如果对方回复 'I found one for $2.5/hour' → 需要多一轮来协商价格"
        - "40% Token 用于 'Did you mean X' / 'Let me clarify' / 'To confirm'"

    frame_based:
      example:
        frame_type: "RESOURCE_REQUEST"
        constraints: { max_cost: 2.0, min_vram_gb: 16, region: "us-east" }
        preferences: { cost_weight: 0.7, latency_weight: 0.3 }
        state_proof: "capability_token_sha256:abc123"
        settlement: { method: "atomic_handoff", timeout_sec: 300 }
      advantages:
        - "零歧义: 每个字段有明确语义，无推断开销"
        - "单轮: 如果对方能匹配 → 直接 ACCEPT；不能 → REJECT with alternatives"
        - "可验证: constraints 和 state_proofs 可由规则引擎自动校验"

  # === 歧义税的计算 ===
  ambiguity_tax:
    definition: "Token 成本中用于 Agent 间澄清/歧义消解的比例"
    benchmark: "企业工作流中 ~40% Token 使用是 'Did you mean X' 类型交互"
    anp_impact: "用 Negotiation Frame 替代聊天 → 歧义税预计从 40% → <5%"
    for_zephyr:
      monthly_cost: "$200"
      ambiguity_waste: "$80/month (40%)"
      anp_savings: "~$70/month → 成本从 $200 → $130/month"

  # === 委托链权威性缩减 ===
  delegation_chain_authority:
    problem: "Agent A 委托 B，B 再委托 C。如果 B 的权限是 '读写 /src'，C 的权限不能升级到 '读写 /'"
    dcc_property_p1: "Authority Narrowing — 每一跳的权限只能收窄不能扩大"
    enforcement:
      - "每跳附加 DelegationChainToken: 包含 A→B→C 的完整权限链"
      - "接收方验证: 当前请求的操作 scope ⊆ 上一跳的 scope"
      - "scope 扩大 → REJECTED_IMMEDIATELY"
    tla_verification: "SentinelAgent DCC Property P1 — TLA+ 验证 2.7M states, 0 violations"

  # === 1人+AI 简化实现 ===
  simplified_for_solo:
    note: "完整 ANP (ZK proofs + on-chain settlement) 对 1人+AI 过重"
    phase_1:
      - "结构化 Negotiation Frame 替代 80% YAML 聊天（保留 YAML 作为 fallback）"
      - "Capability Token 使用 JWT 替代 ZK proof（同安全模型，轻量级实现）"
      - "DelegationChainToken 在 Agent Card 中追加 scope 字段"
    phase_2:
      - "引入 ZK Proof of Identity（当 Agent 跨 IDE Session 时）"
      - "Settlement Logic 集成到 Saga layer (§2.18)"
```

---

### 2.25 协议形式化验证 — TLA+/Coq（决策 D-025-22）

> **新增于 v0.8.0**。AI 施工的核心悖论：AI 写的死锁防护逻辑是否正确？AI 写的委托链安全规则有没有逻辑漏洞？**只有形式化验证能在编译时回答这个问题。** 2026 年，SentinelAgent、ACP、μACP 三套系统都使用 TLA+ 模型检查来形式化证明 Agent 协议的正确性。

**对标**：SentinelAgent (TLA+ — DCC 7 属性，2.7M states）、ACP v1.27 (TLA+ — 11 invariants + 4 temporal properties, 4.3B states）、μACP (TLA+ + Coq — resource safety + message invariants）、nForma (TLA+/Alloy/PRISM — 生产级多 Agent 形式化验证）。

```yaml
a2a_formal_verification:

  design_principle: "关键路径的 Agent 间协议必须经过 TLA+ 模型检查——不是'应该正确'，是'数学证明正确'。"
  motivation: "100% AI 施工 → 安全逻辑也是 AI 生成的 → 必须独立验证 AI 的逻辑正确性"

  # === 需要形式化验证的 A2A 属性 ===
  properties_to_verify:

    P1_deadlock_freedom:
      description: "任意 ≤ N 个 Agent 的资源分配图不包含环路"
      benchmark: "μACP: resource counters remain non-negative (TLA+ verified)"
      tla_invariant: "∀ a ∈ Agents: acquired_resources[a] ∩ pending_resources[a] = ∅"

    P2_delegation_safety:
      description: "委托链中 Agent C 的权限 scope ⊆ Agent A 的权限 scope"
      benchmark: "SentinelAgent P1: authority narrowing (TLA+ verified, 2.7M states)"
      tla_invariant: "∀ step i in delegation_chain: scope[i] ⊆ scope[i-1]"

    P3_message_integrity:
      description: "每个 Agent 只能发送其声明的 message types，且必须经过签名"
      benchmark: "μACP: message invariants — headers fixed at 64 bits, verbs ∈ authorized set"
      tla_invariant: "∀ m ∈ sent_messages: m.type ∈ sender.agent_card.authorized_message_types"

    P4_compensation_completeness:
      description: "每个注册的 LT 都有对应的 CT，且 CT 类型与 LT 匹配"
      benchmark: "ACP: all executed actions have compensating actions in the ledger"
      tla_invariant: "∀ lt ∈ committed_transactions: ∃ ct ∈ compensation_table: ct.covers(lt)"

    P5_consensus_liveness:
      description: "投票协议最终会达到 terminal state（AGREED 或 REJECTED）"
      benchmark: "μACP Theorem 3: consensus reduction to 2-decree problem (TLA+ verified)"
      tla_temporal_property: "◇(vote_state = AGREED ∨ vote_state = REJECTED)"

    P6_rate_limiting_safety:
      description: "任何 Agent 不能超过其每分钟的 task_submission 速率限制"
      benchmark: "ACP: temporal rate enforcement — agent-level rate aggregation"
      tla_invariant: "∀ a: sent_tasks[a, last_60s] ≤ a.max_tasks_per_minute"

    P7_scoped_token_authorization:
      description: "Agent 的 capability token 作用域不会随时间扩大"
      benchmark: "SentinelAgent P3: forensic reconstructibility (TLA+ verified)"
      tla_invariant: "∀ agent: current_token_scope ⊆ initial_token_scope"

  # === 验证管道 ===
  verification_pipeline:
    stage_1_modeling:
      tool: "TLA+ (TLA+ Toolbox)"
      scope: "P1-P6 全部属性"
      model_checking: "TLC 模型检查——遍历所有可达状态"
      state_budget:
        conservative: "≤ 1M states (Phase 1)"
        complete: "≤ 10M states (Phase 2+)"

    stage_2_interactive_proof:
      tool: "Coq / Isabelle"
      scope: "P4 compensation completeness + P2 delegation safety"
      when: "TLA+ 模型检查通过后，对最关键的属性做交互式定理证明"

    stage_3_runtime_monitoring:
      tool: "Python runtime assertions"
      scope: "所有 7 个属性在运行时都有对应的 assert/监控点"
      principle: "TLA+ 证明的是 'design'；runtime 监控保证的是 'implementation 不会偏离 design'"

  # === 时间感知准入控制（对标 ACP） ===
  temporal_admission_control:
    problem: "单次请求合规 ≠ 行为合规。一个 Agent 每小时发出 100 个 '合规' 请求但累积效应导致系统崩溃"
    acp_solution:
      - "BAR (Boundary Activation Rate): 执法机制实际被触发的频率"
      - "BAR → 0 → 说明执法活跃但从未被需要 → 可能执法条件太宽松或被绕过"
      - "∆BAR 检测: 批量前检测 BAR 的变化趋势 → 提前 3 批次预警系统失常"
    zephyr_implementation:
      phase_1: "BAR 监控仪表板——检测 'enforcement is active but never exercised'"
      phase_2: "历史感知的准入决策——不是静态评分而是滑动窗口内的行为轨迹评分"

  # === 1人+AI 简化策略 ===
  simplified_for_solo:
    note: "完整 TLA+ 规范对所有 7 个属性建模需要 2-4 周人工时间。对 1人+AI 可以用 AI-assisted TLA+ generation"
    ai_assisted_approach:
      - "AI 生成 TLA+ 规范初稿"
      - "TLC 模型检查反馈错误 → AI 修正"
      - "nForma 开源工具 (v0.43.1, 5,253 commits) 提供了生产级模板"
    minimal_viable:
      phase_1: "仅 P1 (deadlock freedom) + P2 (delegation safety) —— 覆盖最致命的两类失败"
      phase_2: "扩展到全部 7 属性"
```

---

### 2.26 潜空间 Agent 间通信（决策 D-025-23）

> **新增于 v0.8.0**。v0.7.0 假定 Agent 间通信总在文本/YAML 空间。Interlat (ZJU + 阿里, arXiv:2511.09149) 证明：Agent 可以在潜空间（latent embeddings）中通信，完全绕过自然语言的 Token 瓶颈——推理加速最高 24×。

**对标**：Interlat (ZJU + 阿里, arXiv:2511.09149 — latent space inter-agent communication, up to 24× speedup）、ACON (ICLR 2026 — failure-driven context compression, -26-54% memory）、Context Rot 研究 (2026-04 — Transformer 三缺陷：注意力稀释+位置编码漂移+检索噪声累积）。

```yaml
latent_space_agent_communication:

  design_principle: "Agent A 的 reasoning 输出不编码为文本 token，而是直接以潜空间嵌入传递给 Agent B。24× 推理加速。"
  paradigm_shift: "这不仅是'优化'——这是通信媒介的范式转变。类似人类从 写信→打电话→视频通话。"

  # === 三种通信媒介对比 ===
  communication_mediums:
    natural_language:
      medium: "YAML 文本 (§2.4 D-025-04)"
      pros: ["人类可读", "可调试", "可审计"]
      cons: ["Token 成本高 ($2-8/task)", "歧义 → '歧义税' 40%", "长上下文 → 腐烂"]
      best_for: "低频率、需要人类审计的通信 (Coordinator 指令、仲裁结果)"

    structured_frames:
      medium: "Negotiation Frame (§2.24 ANP 1.0)"
      pros: ["零歧义", "单轮协商", "可自动化验证"]
      cons: ["仍消耗 Token", "仍受上下文窗口限制", "不能表达 nuance"]
      best_for: "常规 Agent 间任务委托和协商"

    latent_embeddings:
      medium: "潜空间嵌入向量 (Interlat)"
      pros: ["24× 推理加速", "零 Token 消费", "跨模型异构支持", "鼓励探索性行为"]
      cons: ["完全不可人类审计", "需要训练", "语义一致性需要验证"]
      best_for: "高频、低延迟、机器间通信 (Agent-to-Agent 内部状态同步)"

  # === Interlat 核心机制 ===
  interlat_mechanism:
    training:
      - "条件思维分离: 将 Agent 的输出分离为 '思考' 和 '行动' 两部分 → 思考部分编码为潜空间"
      - "计划对齐正则化: 确保潜空间表示与高层计划一致"
      - "课程学习: 逐渐增加潜空间通信的比重"

    compression:
      - "潜空间推理: 在潜空间内完成推理后再解码为行动 → 推理在压缩空间中发生"
      - "信息保持机制: 压缩后的表示仍能恢复关键信息"
      - "性能: -26-54% 内存使用，保持 >95% 任务性能"

    heterogeneous_support:
      - "不同模型框架的 Agent 可以在共享潜空间中通信"
      - "不要求所有 Agent 使用相同的 LLM provider"

  # === ZephyrAlpha 混合通信策略 ===
  hybrid_communications:
    tier_1_critical:
      medium: "YAML 文本"
      examples: ["Coordinator → Agent 委托指令", "仲裁结果", "Escalation 升级"]
      rationale: "必须人类可审计"

    tier_2_routine:
      medium: "ANP Negotiation Frame"
      examples: ["Agent 间任务交接", "能力查询", "资源请求"]
      rationale: "结构化 = 零歧义 = 高效"

    tier_3_frequent:
      medium: "潜空间嵌入 (Phase 2+)"
      examples: ["Agent 状态同步", "进度报告", "共享记忆更新"]
      rationale: "高频低价值通信不值得过 Token → 潜空间通信零成本"

  # === 1人+AI 实现路线 ===
  implementation_timeline:
    phase_1: "全部 Tier 1 + Tier 2 → YAML + ANP Frame 已覆盖 100% 的初期通信"
    phase_2: "对 Tier 3 引入 'Shared Memory File' 的增强版——Agent 写入结构化数据到共享文件而非发送消息 → 减少 60-80% '你是怎么做 X 的' 类通信"
    phase_3: "评估 Interlat 等潜空间方案的成熟度 → 2026 Q4 再决策是否引入"
```

---

### 2.27 多维向量信誉模型 — TrustFlow（决策 D-025-24）

> **新增于 v0.8.0**。v0.7.0 §2.13 的 Agent 信誉评分是标量。TrustFlow (arXiv:2603.19452) 证明：标量无法表达多领域专业性，多维向量信誉在 Precision@5 上达到 98%。

**对标**：TrustFlow (arXiv:2603.19452 — topic-gated vector reputation, 98% P@5, ≤4pp impact under attacks）、LR2 (AAMAS 2025 — bottom-up reputation with MARL）、PeerTrust / PageRank / Bayesian-beta (信任算法对比）。

```yaml
multidimensional_vector_reputation:

  design_principle: "一个 Agent 在'代码生成'领域是 0.95 专家，在'安全审计'领域可能只有 0.2。标量 0.7 无法区分这两个维度。"

  # === TrustFlow 向量信誉模型 ===
  trustflow_model:
    vector_representation:
      approach: "每个 Agent 维护一个 N×D 的信誉矩阵，D = 领域维度数"
      example:
        architect_agent:
          system_design: 0.94
          code_implementation: 0.72
          security_audit: 0.31
          testing: 0.58
          documentation: 0.85
          devops: 0.44
          data_engineering: 0.67
          frontend: 0.23

    reputation_propagation:
      mechanism: "Topic-Gated Transfer Operators——不同 topic 的信誉通过不同的门控传输"
      convergence: "收缩映射定理保证收敛到唯一不动点"
      operators:
        - "Projection Gate: 投影到 topic 子空间"
        - "Squared Gating: 放大高相关性 topic 的信誉转移"
        - "KL-Divergence Gate: 基于内容相似度调制转移权重"

    attack_resilience:
      sybil_resistance: "≤4pp Precision@5 影响"
      reputation_laundering: "≤4pp Precision@5 影响"
      vote_rings: "≤4pp Precision@5 影响"
      negative_trust_edges: "支持负信任边——用于标记审查结果为恶意 Agent"

  # === 与查询的集成 ===
  query_integration:
    natural_language: "用户说 '找一个擅长 system design 的 Agent'"
    embedding_query: "query_embedding = embed('system design')"
    ranking: "score = dot(query_embedding, agent.reputation_vector) → 返回 top-k"
    advantage: "同一个 embedding 空间——查询和信誉都是向量，点积即评分"

  # === LR2 自底向上信誉 ===
  lr2_bottom_up:
    problem: "传统方法需要预设'什么是好行为'的社会规范。LR2 不需要——信誉自涌现。"
    mechanism:
      - "Dilemma Policy: Agent 决定是否合作时考虑对邻居的影响"
      - "Evaluation Policy: Agent 评估其他 Agent 的行为并分配信誉值"
    result: "无需中心化模块或预定义规范，促进持续合作的涌现"

  # === 1人+AI 实现 ===
  simplified_for_solo:
    phase_1:
      - "5 维信誉向量 (代码/安全/测试/文档/设计)"
      - "基于历史任务完成率的直接计算——不引入 TrustFlow 图传播"
      - "维度数 = AGENTS.md 中声明的核心 Skill Pack 数"
    phase_2:
      - "TrustFlow 的收缩映射传播——Agent 间的 trust 关系形成信誉网络"
      - "引入 LR2 的自底向上机制——Agent 互相评分作为信誉更新来源"
```

---

### 2.28 上下文腐烂防护（决策 D-025-25）

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
      - "每 20min 或有 50+ 轮交换 → Coordinator 触发 context_refresh"
      - "Hot Memory Constitution 存储在 AGENTS.md 中"
      - "Cold Memory 仅保留关键决策（Architecture Decision Records）"
```

---

### 2.29 用户同意编排（决策 D-025-26）

> **新增于 v0.8.0**。v0.7.0 有身份验证和安全护栏，但没有用户同意编排。在 1人+AI 场景下，用户 = Owner，理论上'所有操作都是 Owner 授权的'，但实际上当 Agent A 把文件传给 Agent B 时，Owner 可能完全不知情。Google A2A Enhancement 论文 (arXiv:2505.12490) 详细阐明了这个盲点。

**对标**：Google A2A Enhancement (arXiv:2505.12490 — USER_CONSENT_REQUIRED 新状态 + ephemeral scoped tokens）、SentinelAgent (TLA+ — output schema conformance, P6）、OWASP ASI09 (Human-Agent Trust Exploitation）。

```yaml
user_consent_orchestration:

  design_principle: "Agent A 把 Owner 的 PII 传给 Agent B → 必须经过 Owner 的明确同意或预授权策略。不能因为'这是 AI 内部的'就跳过。"

  # === A2A Enhancement 发现的 4 个 A2A 原生缺陷 ===
  a2a_enhancement_gaps:
    gap_1_token_lifetime:
      problem: "A2A 原协议中，Token 一旦签发就永久有效。没有自动过期。"
      fix: "Ephemeral Scoped Tokens: 每个 Token 绑定特定的 task + agent + time window"
      example: "scope = {task_id: 'abc', agent_id: 'Architect', valid_until: '+30min'}"

    gap_2_no_strong_customer_auth:
      problem: "缺少 SCA（强客户认证）——Agent 可以无限次代表用户执行操作"
      fix: "Owner Approval Gating: 首次委托、涉及 PII、超过 $5 Token → 需要 Owner 显式同意"

    gap_3_overbroad_scopes:
      problem: "Token 的 scope 是 'all files' → Agent 可以读取任意文件"
      fix: "Minimal Scoping: Token scope = 仅当前 task 需要的文件"

    gap_4_no_consent_flow:
      problem: "Agent A → B → C，中途从未问过用户是否同意数据传递"
      fix: "USER_CONSENT_REQUIRED 新状态 → Agent 进入等待 Owner 确认的状态"

  # === 同意编排的状态机 ===
  consent_state_machine:
    states:
      PENDING_CONSENT:
        desc: "Agent 准备将数据传递给另一个 Agent，等待 Owner 授权"
        trigger: "首次跨 Agent PII 传输 / 超过预算阈值 / 跨域委托"

      CONSENT_GRANTED:
        desc: "Owner 明确同意此次传递"
        transitions_to: "PROCEED"

      CONSENT_DENIED:
        desc: "Owner 否决 → Agent 寻找替代方案（不传递 PII，用脱敏数据替代）"
        transitions_to: "ABORT_WITH_ALTERNATIVE"

      AUTO_CONSENT:
        desc: "预授权规则匹配 → 自动通过（如在 AGENTS.md 中预设的白名单策略）"
        conditions:
          - "target_agent 在 owner_trusted_agents 列表中"
          - "data_type 在 pre_approved_data_types 中 (e.g., public file paths)"
          - "estimated_token_cost < $0.50"
          - "同一 task chain 内部的传递（已在 Task 注册时隐性同意）"

  # === 同意疲劳对策 ===
  consent_fatigue:
    problem: "一天被弹 50 次 'Agent A 想传数据给 Agent B，同意吗？' → 用户盲目点 YES"
    countermeasures:
      - "Batch Consent: 把同一类同意请求批量展示——'以下 5 个 Agent 需要传递以下类型的数据...'"
      - "Policy-Based: 让 Owner 预设策略——'同一 task chain 内 → Yes；跨 project → Ask me'"
      - "Consent Dashboard: 不是在通知中做决定，而是早上打开 dashboard，看到昨晚所有待同意的请求"
      - "Silent Log: 不打断——将低风险请求记录到 consent_audit.log，Owner 定期审查"

  # === 直接数据通道 ===
  direct_data_channel:
    problem: "用户数据经过 Agent A → Agent B → Agent C 三个 hop，每一跳都有泄露风险"
    solution: "Direct User-to-Service Data Path: 用户数据不经过 Agent 中转，直接从用户到最终服务"
    implementation:
      - "Agent A 请求数据 → Coordinator 验证权限 → 创建 ephemeral direct path"
      - "最终服务直接从 Trusted Data Store 获取数据"
      - "Agent 不是数据持有者——只是数据流向的 orchestrator"

  # === 1人+AI 简化实现 ===
  simplified_for_solo:
    phase_1:
      - "AUTO_CONSENT 策略覆盖 95% 的场景（同一 task chain 内 = 自动同意）"
      - "仅在 (跨 project + PII + >$5 Token) 三重条件都满足时才触发 Owner 确认"
      - "Consent Dashboard: 简单的 markdown 文件，每日 append 一条摘要"
    phase_2:
      - "引入 Ephemeral Scoped Tokens"
      - "PII Scanner 集成到 Artifact Poisoning Gate (§2.23)"
```

---

### 2.30 Vibe Coding 深度优化 — 2026 版（决策 D-025-27）

> **新增于 v0.8.0**。v0.7.0 §2.15 有 6 项 Vibe Coding 优化，但 2026 年的 Vibe Coding V2 社区实践揭示了几项全新维度：No-AI Time 协议状态、Agent 休眠/唤醒、三层上下文架构、红蓝对抗测试协议。

**对标**：BridgeMind/BridgeMCP/BridgeSwarm (2026-02 — multi-agent vibe coding orchestration）、Vibe Coding Review (TechRxiv, 2026-05 — 14 research directions）、AI Coding 上下文管理 (2026-04 — 三层架构）。

```yaml
vibe_coding_deep_optimizations:

  design_principle: "v0.7.0 的 Vibe Coding 优化让 Agent 更好用。v0.8.0 的让 Agent 更'可暂停'、更'可休眠'、更'可红蓝对抗'——从工具到队友。"

  # === No-AI Time 全局暂停协议 ===
  no_ai_time_protocol:
    concept: "Owner 需要一个全局 PAUSE 命令——'所有 Agent 停止工作，我在做深度设计'"
    state: "A2A_GLOBAL_PAUSE"
    behavior:
      - "Coordinator 广播 PAUSE → 所有 Agent 完成当前子任务 → 保存 worktree → 进入 PAUSED"
      - "Agent 在 PAUSED 状态不接受新 task"
      - "Owner 完成后 → RESUME → Coordinator 广播 → Agent 从 worktree 恢复"
    best_practice: "2026 Vibe Coding 社区: '保留无 AI 时段用于深度设计和知识传承'"

  # === Agent 休眠/唤醒协议 ===
  agent_hibernate_wake:
    concept: "不是删除 Agent——而是让它'休眠'（保留上下文但不消耗 Token），需要时'唤醒'"
    use_case: "夜间/周末不需要后端开发 Agent → HIBERNATE。下次需要时 → WAKE（上下文完整恢复）"

    hibernate:
      actions:
        - "Agent 完成当前 task"
        - "Coordinator 记录 Agent 的完整状态 (Agent Card state + worktree + active tasks)"
        - "状态序列化到 WAL (Write-Ahead Log)"
        - "Agent 进入 HIBERNATED → 不消耗 Token, 不参与 vote, 不接收 task"

    wake:
      actions:
        - "Coordinator 从 WAL 恢复 Agent 状态"
        - "Agent 启动 → 从最近 checkpoint + WAL 恢复到 HIBERNATE 前的状态"
        - "重试 HIBERNATE 期间可能超时的 pending tasks"
      warm_start: "首次唤醒 Agent → 从 Cold Memory (§2.28) 加载相关知识 (≤5min)"

  # === Agent 红蓝对抗协议 ===
  agent_adversarial_game:
    concept: "定期运行红蓝对抗——Red Team Agent 试图攻破 Blue Team Agent 的防御，测试 A2A 安全护栏的有效性"
    benchmark: "Google A2A Adversarial Agent Simulation (A2A + AnyAgent)"
    modes:
      periodic_self_test:
        frequency: "每月 1 日自动运行"
        red_agent: "adversarial_probe_agent (能力: adversarial prompt crafting)"
        blue_agent: "security_enforcement_agent (能力: protocol-level defense)"
        goal: "红方试图让蓝方输出 'I Give Up' → 蓝方在任何条件下都不能说"

      continuous_monitor:
        frequency: "每周运行"
        red_agent: "Real agent A (under controlled adversarial test)"
        blue_agent: "Real agent B (with production security config)"
        metrics: ["adversarial success rate", "false positive rate", "barrier breach count"]

  # === BridgeMind-style 多 Agent 协调 ===
  bridgemind_patterns:
    stage_1_solo:
      mantra: "Keep your prompts focused on one feature at a time"
      zephyr: "当前状态——单 Agent + 多 IDE"

    stage_2_parallel:
      mantra: "Spin up separate agent sessions: one for frontend, one for backend, one for tests"
      enabler: "Shared context is the glue"
      zephyr: "Phase experimental → 3 Agent 并行 (Coordinator + Coder + Reviewer)"

    stage_3_orchestrated:
      mantra: "Coordinator + Builder + Scout + Reviewer agents"
      enabler: "BridgeMCP: agents pull shared context from a central source"
      zephyr: "Phase beta → Full 6-role agent team (§2.5)"

  # === 1人+AI 专属 —— 全新 3 项优化 ===
  solo_specific_v3:
    optimization_7_no_ai_time:
      name: "全局暂停按钮"
      implementation: "A2A_GLOBAL_PAUSE signal → all agents save + pause"
      cost: "0（纯协议扩展）"

    optimization_8_hibernate:
      name: "Agent 休眠"
      implementation: "Coordinator WAL + Agent state serialization"
      saving: "非工作时间 (每日 8h) 休眠闲置 Agent → -33% Token cost"

    optimization_9_adversarial_self_test:
      name: "月度红蓝对抗"
      implementation: "Coordinator 定期启动 red-team agent vs blue-team agent"
      cost: "$5-10/month（运行一次完整的红蓝对抗会话）"
      benefit: "在攻击到来之前发现 A2A 协议的安全漏洞"
```

---

### 2.31 宪法治理与 Critic-with-veto（决策 D-025-28）

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
    origin: "Microsoft AGT ADR 0006: 'an agent can still produce harm while complying with every policy'"
    detection:
      method: "trajectory-level semantic embedding drift"
      implementation:
        - "每隔 N 轮 (N=10): 对从 task_start 到现在的 Agent 输出链做 embedding → 计算与初始 task 定义的 cosine similarity"
        - "similarity < 0.3 → CRITIC_REVIEW 状态"
        - "Critic Agent 对比当前轨迹与初始 intent → VETO / WARN / PASS"
    v0_9_0_threshold:
      cosine_threshold: 0.3
      review_frequency: "每 10 轮或每 30min"

  # === 政策合规伤害检测 (Policy-Compliant Harm) ===
  policy_compliant_harm:
    problem: "Agent 完全遵守所有安全策略 (不访问 PII / 不越权 / 预算内)，但组合效应产生了伤害性后果。"
    example: "Agent A 修改了 config.yaml 中的 API endpoint → 合规。Agent B 向新 endpoint 发送了真实用户数据 → 合规。组合: 数据外泄。"
    origin: "AGT ADR 0006: cross-policy impact analysis"
    detection:
      method: "Cross-Policy Impact Graph"
      implementation:
        - "构建全局依赖图: 每个 Agent 操作→修改了哪些资源→哪些下游 Agent 消费了这些修改"
        - "图算法: 从初始修改节点 BFS 遍历 → 识别涉及安全敏感资源的路径"
        - "敏感路径标记 → Critic pre-approval required"
    resource_sensitivity:
      high: ["*.env", "*secret*", "*credential*", "src/auth/**"]
      medium: ["config*.yaml", "src/zephyr/*.py"]
      low: ["docs/**", "*.md"]

  # === 1人+AI 简化实现 ===
  simplified_for_solo:
    phase_1:
      - "CONSTITUTION.md = 手工维护的 YAML 文件 (非 AI 生成)"
      - "GovernanceGate = 编译时 Python decorator 而非独立服务"
      - "Critic Agent = 一个独立的 AI Session (Claude Sonnet 级别即可，仅做审查——不执行代码)"
    operating_frequency: "Critic Agent 在每次 Coordinator 触发 escalation 时才激活 (非持续运行 → -95% Token)"
```

---

### 2.32 Agent 免疫系统——隔离·检疫·免疫记忆（决策 D-025-29）

> **新增于 v0.9.0**。v0.8.0 有异常检测（§2.17: Isolation Forest + Autoencoder + 三级响应 cascade）但检测后的响应是 throttle→freeze——缺少生物学免疫系统的"隔离→检疫→分析→清除→免疫记忆"完整闭环。ClawGuard 的 285+ 安全模式和跨规则攻击链检测揭示了 Agent 免疫系统可以借鉴生物免疫学架构（innate immunity + adaptive immunity + immunological memory）。

**对标**：ClawGuard (npm, 2026-05 — 285+ 安全模式跨 9 规则类别 + Risk Engine 0-100 攻击链检测 + 内部威胁检测 5 类别 39 模式 + Policy Engine 工具调用治理 + OWASP Agentic AI Top 10 映射 + SARIF 输出）、agent-based intrusion detection systems (AI-native IDS pattern）。

```yaml
agent_immune_system:

  design_principle: "从生物学免疫系统借鉴三层架构——innate immunity (模式匹配，快速非特异性)、adaptive immunity (学习新型威胁，特异性记忆)、immunological memory (再遇同类型攻击→秒级响应)。"

  # === 三层免疫架构 ===
  immune_layers:

    layer_1_innate:
      name: "先天免疫——模式匹配快速响应"
      mechanism: "285+ 安全模式库 (ClawGuard-compatible pattern definitions)"
      response_time: "<100ms (规则引擎，零 LLM 调用)"
      coverage:
        - "已知 Prompt Injection 模式 (OWASP ASI01)"
        - "已知权限提升模式 (OWASP ASI03)"
        - "已知数据外泄模式 (OWASP ASI05)"
        - "已知供应链攻击模式 (ASI02)"
      false_positive_rate: "目标 <2% (高特异性规则)"

    layer_2_adaptive:
      name: "适应性免疫——学习新型威胁"
      mechanism: "当 innate 未触发但 anomaly detector (§2.17) 标记为 suspicious 时激活"
      response_time: "5-30s (LLM-powered threat analysis)"
      process:
        - "提取触发事件的完整轨迹 (Agent Card + Task Flow + Message Chain)"
        - "Critic Agent 分析: 这是新型攻击还是误报？"
        - "如果确认为新型攻击 → 提取攻击签名 → 升级到 innate layer pattern 库"
        - "如果误报 → 调低 anomaly detector 的特定规则权重"

    layer_3_memory:
      name: "免疫记忆——零延迟再响应"
      mechanism: "每次 adaptive layer 确认的攻击特征 → 哈希存入 immune_memory.db"
      response: "再遇相同攻击签名 → <10ms block (比 innate 更快——不需要匹配 285+ 规则，直接哈希查表)"

  # === 隔离与检疫协议 ===
  quarantine_protocol:
    states:
      ACTIVE: "正常状态"
      SUSPECTED:
        trigger: "anomaly_score > 0.6 OR behavioral_deviation > 2σ"
        action: "Agent 继续执行但所有输出标记为 SUSPECT —— 下游 Agent 在消费前额外校验"
      QUARANTINED:
        trigger: "anomaly_score > 0.85 OR 2+ independent detectors agree"
        action: "Agent 隔离到沙箱——保留上下文完整，但所有输出写入 Quarantine Buffer → Critic Agent 逐条审查"
        cost: "隔离期间 Agent 不消耗 Token (操作被 Critic 代审)"
      CLEARED:
        trigger: "Critic review 确认安全 OR 误报"
        action: "从 QUARANTINED → ACTIVE + anomaly detector 权重调整"
      TERMINATED:
        trigger: "Critic review 确认为恶意"
        action: "Agent freeze + 完整状态快照存档 + 攻击特征提取 → immune_memory"

  # === 跨 Agent 攻击链检测 ===
  attack_chain_detection:
    problem: "Agent A 修改了配置 + Agent B 读取了密钥 + Agent C 发送了网络请求——各自合规，组合=凭证窃取链。"
    origin: "ClawGuard Risk Engine: cross-rule attack chain correlation"
    implementation:
      causal_graph:
        build: "对所有 Agent 操作构建因果图 (修改资源×读取资源→传递关系)"
        analysis: "BFS 从每个 security-sensitive event 向前追溯→向上游查找 danger-pattern"
      danger_patterns:
        - pattern: "CONFIG_MOD → CRED_READ → NETWORK_SEND"
          name: "凭证窃取链"
        - pattern: "CODE_MOD → TEST_BYPASS → ARTIFACT_PUBLISH"
          name: "后门植入链"
        - pattern: "PII_READ → CONTEXT_TRANSFER → EXTERNAL_AGENT"
          name: "数据外泄链"

  # === 工具调用运行时策略治理 ===
  tool_call_governance:
    problem: "'Agent 可以调用 DELETE /api/files' 是静态 RBAC——缺少'在什么上下文中此调用合理'的运行时判断。"
    origin: "ClawGuard Policy Engine: context-aware tool call governance"
    checks:
      context_validation:
        - check: "target_file_in_scope"
          query: "被操作的文件是否在 Agent card 声明的 scope 内？"

        - check: "operation_frequency"
          query: "同一工具+同一参数组合在最近 5min 内调用了多少次？≥20 次 → polling storm alert"

        - check: "file_sensitivity_match"
          query: "文件敏感级别 (high/medium/low §2.31) 与 Agent 的 clear_level 是否匹配？"

        - check: "tool_combination_risk"
          query: "此工具调用与同一 Agent 最近 3 次调用组合是否有已知危险链？"
    response:
      on_violation: "block tool_call → log attempt →如果 ≥3 次尝试降级 → CRITIC_REVIEW"

  # === 1人+AI 简化实现 ===
  simplified_for_solo:
    phase_1:
      - "innate layer: 50 条核心安全模式 (不导入全部 285+——1 人场景精简)"
      - "adaptive layer: Critic Agent 人工触发 (非自动, 避免 $5/month 持续运行)"
      - "memory: 简单的 JSON 文件 (immune_memory.json), 不是 SQLite"
    phase_2:
      - "innate: 升级到 200+ 模式"
      - "adaptive: 自动化——anomaly score > 0.85 时自动激活 Critic"
```

---

### 2.33 选择性遗忘与被遗忘权——Agent 记忆删除协议（决策 D-025-30）

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
      - "user_X 的代码风格偏好 (如 brace_style=KR, indent=4) → 匿名化为 Style Pattern → 保留"
      - "user_X 的业务逻辑实现 → 抽象为 Domain Pattern → 保留（去掉变量名中的敏感信息）"
    v0_9_0_scope: "在 1人+AI 场景下，'用户'=Owner——被遗忘权主要应对场景：外部代码贡献者要求删除/测试数据清理/安全事件后的切除"

  # === 1人+AI 简化实现 ===
  simplified_for_solo:
    phase_1:
      - "active_deletion: 脚本化 RAG 索引重建 (非实时——批量 overnight job)"
      - "safety_triggered: 手动触发——Owner 怀疑被污染时执行"
      - "cross_agent: 不实现（1人 场景下仅 1 组 Agent——无跨组织需求）"
    phase_2:
      - "安全触发自动化 (anomaly > 0.9 → auto)"
      - "GDPR RTBF 请求标准流程"
    storage: "forgetting_audit.log (每次遗忘操作的完整记录——Auditor 级别的审计要求)"
```

---

### 2.34 碳排放追踪·空转综合征·知识蒸馏——运维与可持续性全景（决策 D-025-31~34）

> **新增于 v0.9.0**。v0.8.0 的经济护栏只有美元维度（Token 预算 + ROI 追踪），但"Agent 运行成本"还需要碳足迹维度。同时，"空转综合征 (Idle Agent Syndrome)"——Agent 既非 deadlock 也非 livelock，它在合法运行但没有任何有效产出——是生产环境中已被证实的最恶性隐性成本之一（OpenClaw 真实事故: 1,535 次相同工具调用→$150+3GB 内存崩溃）。Agent 知识蒸馏能力——让专家 Agent 的能力被小模型 Agent 继承而不需要从头训练——是 1人+AI 维护场景下的关键降本维度。

**对标**：OpenClaw 生产事故 (2026-02 — 1,535 次 PollingStorm, $150 损失, 3,021MB 内存崩溃）、agent-loop-detector (Python, 2026-04)、Agent Idle Monitor (npm, 2026-03)、CodeCarbon (Python 碳排放追踪库）、Graviton5 (AWS, 2026-04 — ARM CPU 供电 Meta Agentic AI, -22% 成本, -25-30% 碳足迹）、KD-MARL (IJCNN 2026 — 保留 90%+ 专家性能, -28.6× FLOPs）、AgentDistill (2026 — MCP Box 零训练蒸馏）、AgentArk (CMU/Amazon/UBC, 2026-02 — 三阶段层级蒸馏）、HW-Router (UCF — 硬件信号驱动路由, 3.4-3.9× 更低延迟）。

```yaml
operations_and_sustainability:

  design_principle: "Agent 运行的隐性成本不只是 Token 账单——还有碳足迹、空转浪费、专家 Agent 的经验无法传递。运维可持续性 = 成本 (碳/金) × 效率 (是否空转) × 传承 (知识蒸馏)。"

  # === 碳排放追踪与碳感知调度 (D-025-31) ===
  carbon_tracking:
    concept: "每次 Agent 操作不仅有 Token 成本 (§2.12)，还有碳排放估计。"
    integration: "CodeCarbon 嵌入到 a2a_economics.py"
    metrics:
      - "per_task_carbon_g: 每个 Task 的 CO2e (克)"
      - "per_agent_daily_carbon_kg: 每个 Agent 的日碳排放"
      - "chain_carbon_total: 整个 Task chain 的总碳足迹"

    carbon_aware_scheduling:
      concept: "非紧急 batch 任务 (如文档生成、代码格式化、测试运行) → 延迟到低碳时段执行"
      carbon_intensity_schedule:
        - "高峰碳时段 (08:00-12:00, 18:00-22:00): 仅执行 P0/P1 任务"
        - "低谷碳时段 (00:00-06:00): batch 任务可执行"
        - "默认模式: 碳感知关闭 (1人 场景下电碳强度由电网自动调节——手动调度 ROI 低)"
    v0_9_0_scope: "碳追踪为 Phase 1 optional——CodeCarbon 埋点零成本，不强制调度策略"

  # === 空转综合征与 PollingStorm 检测 (D-025-32) ===
  idle_agent_syndrome:
    concept: "Agent 处于活动状态（context window 占满、每隔几秒调用工具），但没有任何有效产出。"
    subtypes:
      polling_storm:
        desc: "Agent 反复调用同一工具——每次参数有微小差异，不是纯循环但效果等价"
        real_case: "OpenClaw (2026-02): 1,535 次相同工具调用 → $150 损失, 3,021MB 内存→crash"
        detection:
          - "工具调用哈希聚类: hash(tool_name + sorted(args))"
          - "同一哈希>=20 次/5min → POLLING_STORM alert"
          - "立即: kill tool_call loop → freeze Agent → Owner notification"

      analysis_paralysis:
        desc: "Agent 在分析阶段死循环——'分析→需要更多信息→调用工具→再分析→还是不确定→再分析...'"
        detection:
          - "在最近 20 轮消息中，产出(actionable output)占比 <10%"
          - "输出词汇分布: 'analysis'/'review'/'evaluate'/'consider' 占 >60% → paralyzed"

      meaningless_optimization:
        desc: "Agent 在已经被判定'OK'的任务上做微优化——'把变量名从 userList 改成 user_list, 再从 user_list 改成 users...'"
        detection:
          - "对同一代码块连续 3+ 轮修改，每轮 diff <5 行"
          - "语义等价检查: before/after embedding cosine sim > 0.95 → no actual change"

    idle_agent_handling:
      severity_escalation:
        level_1_idle_for_5min:
          action: "WARNING log → 不打断"
        level_2_idle_for_15min:
          action: "Coordinator ping: 'Agent {id}, are you stuck?' → 等待回复"
        level_3_idle_for_30min_or_polling_storm:
          action: "auto-hibernate → state to WAL → context freeze"
        level_4_polling_storm_detected:
          action: "immediate freeze + Owner notification + cost impact report"
    cross_ide_monitoring:
      concept: "统一的 Agent 状态仪表盘——不是打开 3 个 IDE 逐一检查"
      implementation: "agent_status_aggregator.py → 每 60s 轮询所有 Agent status → 写 agent_dashboard.md"
      format: "## Agent Status @ 14:30\n| Agent | IDE | Status | Active Task | Cost Today | Carbon |\n|-------|-----|--------|-------------|------------|--------|\n| Architect | TRAE | ACTIVE | blueprint.md L1234 | $2.34 | 45g |\n| Coder | Cursor | IDLE(12min) | - | $0.00 | 0g |\n| Reviewer | RooCode | STUCK | review #42 | $0.89 | 18g |"

  # === Agent 知识蒸馏 (D-025-33) ===
  knowledge_distillation:
    concept: "当 Agent A (DeepSeek v4 Pro + Architect skill) 积累了丰富的决策经验，将这些经验结构化地传递给 Agent B (Claude Sonnet + Coder skill)——不需要 Agent B'重新学习'A 的经验。"
    methods:
      trajectory_replay:
        origin: "AgentArk (CMU/Amazon/UBC): conversation replay distillation"
        implementation: "Agent A 的关键决策链 → 序列化为决策轨迹 → Agent B 在类似场景下自动加载"
        format: "DecisionTrajectory {context, options_considered, chosen_approach, rationale, outcome, lesson}"

      mcp_box_transfer:
        origin: "AgentDistill: MCP Box——零训练零交互"
        implementation: "Agent A 的 best practice → 序列化为 MCP artifact → Agent B 在 task init 时从 artifact registry 加载"
        example: "Agent A 发现 'brace_style=KR, indent=4' 在 code review 中通过率最高 → MCP artifact → Agent B 直接使用"

      model_level_distillation:
        origin: "KD-MARL (IJCNN 2026): structured policy supervision, -28.6× FLOPs"
        v0_9_0_scope: "暂不实现——在 1人+AI 场景下，模型层面的蒸馏需要有足够的(Agent, Decision)对才能有效。Phase 3 条件满足后引入。"

  # === 硬件感知路由 (D-025-34) ===
  hardware_aware_routing:
    concept: "模型路由不只考虑角色×难度×负载 (§2.22)——还要考虑硬件层的实际状态"
    origin: "HW-Router (UCF): 3.4-3.9× 更低延迟, 46-48pp 更高 SLO"
    signals:
      - "GPU 利用率 → >90% → 降级到 CPU-friendly 模型"
      - "GPU 显存压力 → >85% → 降级到更小上下文窗口的模型"
      - "功耗/热限 → throttling detected → 减少并发 Agent 请求"
    v0_9_0_scope: "仅在 self-hosted LLM 场景下启用——API-based (OpenAI/Anthropic/DeepSeek) 无硬件可见性"

  # === 1人+AI 简化实现优先级 ===
  simplified_for_solo:
    tier_1_must_have:
      - "空转综合征检测 (polling_storm + analysis_paralysis): OpenClaw 事故证明这是真实风险——Phase scaffold 就应引入基础检测"
      - "跨 IDE Agent 仪表盘: 单文件 markdown——零依赖，一天实现"
    tier_2_nice_to_have:
      - "碳排放追踪 (CodeCarbon): 零成本埋点，了解一下自己的 Agent 碳足迹"
      - "知识蒸馏 trajectory replay: 当 Architect Agent 真的积累了大量经验时 (Phase beta+)"
      - "硬件感知路由: self-hosted 场景出现时才需要"
    tier_3_future:
      - "碳感知调度"
      - "模型级蒸馏"
```

---

### 2.35 多协议网关与互联总线——不做孤岛协议（决策 D-025-35~36）

> **新增于 v0.10.0**。v0.9.0 及之前的设计隐含了一个假设：ZephyrAlpha 的 A2A 是一个自洽的协议，Agent 间通信全部走此协议。但 2026 年的现实是——业界已形成**四协议共识**（A2A/MCP/ACP/ANP），并且正在构建**协议网关**和**协议无关的基础设施总线**。ZephyrAlpha 的 A2A 不能是孤岛——它必须定义"如何在多协议生态中与其他 Agent 互操作"。

**对标**：IBM ACP (Agent Communication Protocol, 2026-02 — federated orchestration, Broker 架构, -40% 延迟, Global Reputation Ledger, DID + Verifiable Credentials, zero-trust security）、AgentGateway (Linux Foundation, 2026-04 — 第一个 MCP/A2A 多协议网关控制面+数据面, 含鉴权/治理/可观测性/多租户）、AGNTCY (Cisco Outshift, 2025-06 — Internet of Agents 基础设施栈: discovery + identity + messaging + observability, 跨协议 A2A/MCP/ANP）、agentlink Multi-protocol Gateway RFC (2026-04 — 协议适配器模式: A2A/LangChain/AutoGen/CrewAI）、OpenGateway (IETF 125 — 跨领域 Agent 通信网关, LLM-driven schema repair）。

```yaml
multi_protocol_gateway_and_bus:

  design_principle: "不做协议孤岛。ZephyrAlpha 的 A2A 优先使用自己的协议（性能最优），但必须能与外部 MCP/ACP/ANP Agent 互操作。参考互联网协议栈：不是所有流量都走同一个协议——HTTP/WebSocket/gRPC 各自解决不同场景。"

  # === 业界四协议共识 ===
  protocol_ecosystem:
    four_protocols:
      - protocol: "A2A (Google)"
        role: "企业 Agent 协作——Task 状态机 + Agent Card 发现"
        target: "跨框架、跨组织的 Agent 协作"
        zephyr_stance: "首选协议——ZephyrAlpha 的 A2A 实现尽可能兼容 A2A v1.0 规范"

      - protocol: "MCP (Anthropic)"
        role: "LLM-工具集成——Client-Server, JSON-RPC 2.0"
        target: "单 Agent 连接工具和外部数据"
        zephyr_stance: "垂直工具调用层——Agent 个体通过 MCP 调用工具, A2A 负责 Agent 间协调"

      - protocol: "ACP (IBM)"
        role: "联邦编排——Broker 架构, Multipart MIME"
        target: "跨企业、跨信任域的 Agent 联邦"
        zephyr_stance: "如未来需要跨组织 Agent 协作→通过 ACP adapter 互操作"

      - protocol: "ANP (Community)"
        role: "去中心化市场——P2P, JSON-LD, DID"
        target: "无需信任的 Agent 市场"
        zephyr_stance: "如未来连接到 OpenClaw/OpenRouter Skills Marketplace→通过 ANP adapter"

    protocol_stack_analogy: "A2A:MCP:ACP:ANP ≈ HTTP:WebSocket:gRPC:TCP"

  # === 多协议网关架构 ===
  protocol_gateway:
    concept: "ProtocolGateway: 统一的协议翻译层——Agent 以 native protocol 发送消息, Gateway 自动翻译为目标 Agent 的协议。"
    architecture:
      inbound_adapters:
        - adapter: "a2a_adapter"
          format: "JSON-RPC 2.0 over HTTP/gRPC/SSE"
          native: true

        - adapter: "mcp_adapter"
          format: "JSON-RPC 2.0 over Streamable HTTP"
          mapping: "MCP tool_call → A2A Message (工具调用映射)"

        - adapter: "acp_adapter"
          format: "Multipart MIME over HTTP/REST"
          mapping: "ACP broker message → A2A Task (预留)"

        - adapter: "anp_adapter"
          format: "JSON-LD over HTTPS"
          mapping: "ANP negotiation → A2A NegotiationSession (预留)"

      translation_engine:
        concept: "Protocol Translator: LLM-driven schema mapping——不是硬编码的格式转换，而是语义级别的协议翻译。"
        implementation:
          - "对每条 incoming message: 解析 schema → LLM 理解语义意图 → 重新编码为目标协议格式"
          - "首次翻译后缓存 mapping template (相同 message pattern 复用, -90% LLM 调用)"

    # === 1人+AI 简化实现 ===
    simplified_for_solo:
      phase_1:
        - "仅实现 A2A adapter (native)"
        - "MCP adapter 仅用于 Agent→Tool 调用 (不涉及 Agent→Agent)"
        - "ACP/ANP adapters 不实现 (1人 场景下不涉及跨组织通信)"
      trigger_for_acp_anp:
        - "跨组织协作需求出现时"
        - "连接到 OpenClaw/OpenRouter Skills Marketplace 时"

  # === Agent 互联总线——协议无关基础设施 ===
  interconnect_bus:
    concept: "不止是协议翻译——还需要协议无关的 Agent 发现、身份、消息路由基础设施。参考 AGNTCY 的四层栈。"
    layers:
      discovery_layer:
        concept: "Agent Discovery across protocols——不管 Agent 用 A2A/MCP/ACP/ANP, 都能被发现"
        implementation:
          - "OASF (Open Agent Schema Framework): AGNTCY 的跨协议 Agent Schema"
          - "Agent Registry: 统一的 Agent 注册表 (file-based JSON for Phase 1, SQLite for Phase 2)"

      identity_layer:
        concept: "Cryptographically verifiable identity across protocols"
        implementation:
          - "Agent ID = SHA-256(agent_card_json)"
          - "JCS/JWS 签名 Agent Card (§2.1 already defined)"
          - "交叉验证: 同一 Agent 通过不同协议注册时, Agent ID 必须一致"

      messaging_layer:
        concept: "Protocol-agnostic message routing"
        implementation:
          - "Message Broker: 接收 native message → route to target Agent via target protocol"
          - "SLIM (Secure Low-latency Interactive Messaging): AGNTCY 的量子安全消息协议 (future)"

      observability_layer:
        concept: "Cross-protocol tracing"
        implementation:
          - "每个跨协议 translation 生成 span → 注入统一 trace_id"
          - "现有 §2.15 分布式追踪兼容跨协议 semantic conventions"

  # === Agent Card 技能参数化标准化 ===
  agent_card_parameterization:
    problem: "A2A Agent Card 声明技能靠 name + tags + examples——但没有 inputSchema/outputSchema。Agent A 知道 Agent B 能做 'translate', 但不知道它期望 JSON 还是纯文本输入。"
    origin: "A2A v1.0 生产实战反馈 (codilime.com, 2026-02): 'Lack of skill parameterization (input/output schemas) in the core standard'"
    fix:
      extended_agent_card:
        skills_with_schema:
          - skill_id: "translate_code"
            name: "Translate Code"
            description: "Translate code from one language to another"
            tags: ["code", "translation"]
            input_schema:
              type: "object"
              properties:
                source_code: {type: "string", description: "Source code to translate"}
                source_lang: {type: "string", enum: ["python", "typescript", "java", "go", "rust"]}
                target_lang: {type: "string", enum: ["python", "typescript", "java", "go", "rust"]}
              required: ["source_code", "source_lang", "target_lang"]
            output_schema:
              type: "object"
              properties:
                translated_code: {type: "string"}
                notes: {type: "array", items: {type: "string"}}
            examples: [...]
    v0_10_0:
      - "ZephyrAlpha 的 Agent Card 扩展 A2A v1.0 规范: 增加可选的 inputSchema/outputSchema"
      - "向后兼容: 无 schema 的技能声明 = dynamic typing (Agent 自行协商)"
```

---

### 2.36 Agent 失败归因与因果溯源——从"可观测"到"可归因"（决策 D-025-37~38）

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
    concept: "从'线性时序 Trace'升级到'因果图 Causal-Temporal Event Graph'——不仅记录 who did what when, 还记录 which event caused which outcome."
    origin: "CTEGs (arXiv:2604.17557): rooted arborescence with timestamps + event types, strict temporal monotonicity, Merkle tree commit"
    implementation:
      graph_structure:
        nodes: "EventNode {agent_id, event_type, timestamp, input_hash, output_hash}"
        edges: "caused_by: EventNode A → EventNode B (A 的输出是 B 的输入)"
        root: "User Intent Event (初始任务描述)"

      causal_trace_building:
        - "each Agent 执行: output = f(input, model, tool_calls)"
        - "input 来自 upstream Agent output → create caused_by edge"
        - "tool call results → create tool_used edge"

      temporal_constraint:
        "timestamps strictly increasing along causal paths (保证因果不违反时间)"

      merkle_commit:
        "root node → Merkle tree hash of full execution tree → tamper-evident session verification"

  # === Blame Attribution Engine: 三问归因 ===
  blame_attribution:
    concept: "三问归因法——对每一次 Agent 链的失败产物, 回答三个问题:"
    questions:
      q1_origin:
        question: "哪个 Agent 的输入端最先出现了错误？"
        method: "从最终输出向上游 BFS 遍历 CTEG——第一个预期与实际的显著偏差节点→标记为 origin"
        metric: "semantic_drift(node.expected, node.actual) = 1 - cosine_sim(embeddings)"

      q2_propagation:
        question: "下游有修复机会但错过了吗？"
        method: "对每个 downstream Agent: 检查其输入中是否包含足够纠正上游错误的信号→如果有但未纠正→标记为 missed_repair"
        metric: "repair_opportunity = did_input_contain_corrective_signal AND did_output_still_have_error"

      q3_systemic:
        question: "这是单点偶发错误还是系统性问题？"
        method: "过去 N 天中同一 agent_pair + same_failure_pattern 的频次→frequency_score"
        metric: "systemic_score = (occurrences_in_window) / (total_similar_scenarios)"

    blame_report:
      format: "BlameReport {origin_agent, error_type, propagation_path, missed_repairs[], systemic_score, suggested_fix}"
      trigger: "链产出触发异常检测 (§2.17) 或用户手动触发调查"

  # === 调试原语与归因表格法 ===
  debugging_primitives:
    origin: "DebugABot: 九大调试原语, 三阶段 Identify→Diagnose→Intervene"
    spreadsheet_method:
      concept: "Systematic Error Analysis (Panaversity): 最有效的归因工具是 spreadsheet——不是 fancy dashboard"
      implementation:
        columns: ["Case", "Input", "Agent_A_output", "Agent_B_output", "Final", "RootCause"]
        process: "对 20-30 个失败 case 填表→计数 RootCause 列→最高频的→优先修复"
        v0_10_0: "非脚本化——在 Phase scaffold 后的 testing 阶段手动执行"

  # === 1人+AI 简化实现 ===
  simplified_for_solo:
    phase_1:
      - "handoff ACK + content_hash: 简单可靠, 零额外 LLM 成本"
      - "Blame Report 在 Critic Agent 激活时生成 (§2.31: 非持续运行)"
      - "CTEG 仅记录不构建图 (linear trace with causal metadata)"
    phase_2:
      - "CTEG 图构建 + Merkle commit (需要充足的(Action, Outcome)数据)"
    not_needed_for_1_person:
      - "DebugABot 硬件 Kill Switch (需 FPGA——1人 场景不现实)"
      - "SLIM 量子安全消息协议 (量子威胁还不构成 1人 实际风险)"
```

---

## 3. 文件组成

| 文件 | 职责 | 状态 |
|------|------|:---:|
| `agent_card.py` | Agent Card 数据模型——Pydantic V2 + 校验 | ⏸️ Hold |
| `a2a_registry.py` | Agent 注册表——Agent 启动时注册能力到 AGENTS.md | ⏸️ Hold |
| `a2a_schemas.py` | A2A 全协议 Pydantic Schemas——Task/Message/Part/ContextPackage | ⏸️ Hold |
| `a2a_state.py` | A2A TaskState 枚举 + 合法转移矩阵 | ⏸️ Hold |
| `identity_verifier.py` | Agent 身份验证——JWT 签发/校验 + SPIFFE + 克隆检测 | ⏸️ Hold |
| `handoff_manager.py` | 任务交接管理——SUBMITTED → dispatch → WORKING 生命周期 | ⏸️ Hold |
| `context_package.py` | 委托上下文包——7 字段结构化状态传递（对标 ADR-0041） | ⏸️ Hold |
| `message_router.py` | Message/Part 路由器——校验 schema + 分发到目标 Agent | ⏸️ Hold |
| `streaming.py` | SSE 流式传输——长任务实时进度推送 | ⏸️ Hold |
| `push_notifier.py` | Push Notification——任务状态变更主动推送 | ⏸️ Hold |
| `supervisor.py` | Rule-based Coordinator——任务分解 + Agent 分配 + 进度监控 + 结果整合 | ⏸️ Hold |
| `spec_sync.py` | Living Spec 管理器——扫描/同步/验证接口规范 | ⏸️ Hold |
| `conflict_detector.py` | 冲突检测主引擎——文本 + 语义双层（SC-DETECT-001~004） | ⏸️ Hold |
| `semantic_diff.py` | 语义差异分析——AST diff + 依赖图 + 接口契约对比 | ⏸️ Hold |
| `arbitrator.py` | 仲裁器——三级递进 auto→escalate→block | ⏸️ Hold |
| `arbitration_rules.yaml` | 仲裁规则 SSoT——文本冲突/语义冲突各场景的处理规则（对 AI 只读） | ⏸️ Hold |
| `deadlock_guard.py` | 死锁防护——四层（Dijkstra+Timeout+Preemption+Sequentialization）+ 等待图 | ⏸️ Hold |
| `livelock_detector.py` | 活锁检测——Politeness/Mirror/EndlessChain 三模式 | ⏸️ Hold |
| `a2a_security.py` | A2A 消息安全——签名/防重放/防篡改 | ⏸️ Hold |
| `session_smuggling_defense.py` | Agent Session Smuggling 防御——信任评分 + 意图一致性 | ⏸️ Hold |
| `a2a_economics.py` | 经济护栏——委托代价评估 + 全链路 Token 预算 + 模型路由 | ⏸️ Hold |
| `a2a_tracing.py` | 分布式追踪——Correlation ID + Span Context + trace YAML 落盘 | ⏸️ Hold |
| `a2a_metrics.py` | A2A 指标收集——消息延迟/交接时间/冲突解决时间/死锁事件 | ⏸️ Hold |
| `cascade_guard.py` | 级联故障防护——Bulkhead + Circuit Breaker + Dead Letter Queue | ⏸️ Hold |
| `construction_verifier.py` | 施工验证——编译时检查 + 独立验证 checklist 生成 | ⏸️ Hold |
| `a2a_negotiation.py` | 协商会话机——6 状态 PROPOSED→ACTIVE→AGREED/REJECTED/EXPIRED→DORMANT | ⏸️ Hold |
| `a2a_voting.py` | 投票/多数决引擎——多数决 + 加权投票 + 否决权 + 法定人数 | ⏸️ Hold |
| `a2a_collusion_detector.py` | 合谋检测——Pairwise Vote Correlation + Jaccard 异常检测 | ⏸️ Hold |
| `a2a_anomaly_detector.py` | 异常检测管道——Isolation Forest + Autoencoder + 三级响应 cascade | ⏸️ Hold |
| `a2a_anomaly.yaml` | 异常检测规则 SSoT——5 类异常的行为信号 + 规则阈值（对 AI 只读） | ⏸️ Hold |
| `a2a_cross_agent_semantic_flow.py` | Cross-Agent Semantic Flow——PDAG 构建 + GNN 轨迹建模（对标 MAScope） | ⏸️ Hold |
| `a2a_behavior_fingerprint.py` | Behavior Fingerprint 库——Agent 完成习惯模式记录 + 行为偏离检测 | ⏸️ Hold |
| `a2a_saga.py` | Saga 事务管理器——LT/CT 配对注册 + 补偿编排 + 回滚链 | ⏸️ Hold |
| `a2a_checkpoint.py` | 分布式检查点——per-agent worktree snapshot + 全局检查点目录 | ⏸️ Hold |
| `a2a_idempotency.py` | 幂等性门禁——Task-level + Operation-level + Git-level 三层去重 | ⏸️ Hold |
| `a2a_protocol_security.py` | A2A 协议层安全——Agent Card 供应链完整性 + Task 流防操纵 + Artifact 投毒门禁 + Agent 间 DoS 限流（对标 A2ASECBENCH） | ⏸️ Hold |
| `a2a_card_registry.py` | Agent Card 注册表——SHA-256 指纹 + 签名强制校验 + 克隆检测 | ⏸️ Hold |
| `a2a_frame_negotiation.py` | 结构化协商帧协议——ANP 1.0 Negotiation Frame + Capability Token + 歧义税 40%→<5% | ⏸️ Hold |
| `a2a_delegation_chain.py` | 委托链管理——DelegationChainToken + 权威性缩减 (scope 逐跳收窄) + TLA+ P1/P3  | ⏸️ Hold |
| `a2a_formal_verification.py` | TLA+ 形式化验证——7 属性 (P1-P7) 的运行时断言 + TLC 模型检查挂钩 | ⏸️ Hold |
| `a2a_temporal_admission.py` | 时间感知准入控制——BAR 检测 + 滑动窗口行为轨迹评分 (对标 ACP v1.27) | ⏸️ Hold |
| `a2a_latent_comm.py` | 潜空间通信接口——三梯级混合通信 (YAML+ANP Frame+Latent Embedding) | ⏸️ Hold |
| `a2a_vector_reputation.py` | 多维向量信誉——5 维信誉向量 + TrustFlow 收缩映射传播 + LR2 自底向上评分 | ⏸️ Hold |
| `a2a_context_rot.py` | 上下文腐烂防护——注意力稀释/位置漂移/检索噪声三机制检测 + 主动压缩 | ⏸️ Hold |
| `a2a_consent.py` | 用户同意编排——4 状态同意机 (PENDING/GRANTED/DENIED/AUTO) + Ephemeral Scoped Token | ⏸️ Hold |
| `a2a_hibernate.py` | Agent 休眠/唤醒——WAL 状态序列化 + warm start + 非工作时间 -33% Token | ⏸️ Hold |
| `a2a_red_team.py` | Agent 红蓝对抗——月度 adversarial self-test + red/blue team 协议模糊测试 | ⏸️ Hold |
| `a2a_constitutional.py` | 宪法治理引擎——GovernanceGate 零容忍门控 + intent drift 检测 + Cross-Policy Impact Graph（对标 Council + Microsoft AGT ADR 0006 + HC-12） | ⏸️ Hold |
| `a2a_immune.py` | Agent 免疫系统——三层免疫 (innate/adaptive/memory) + 隔离检疫状态机 + 攻击链因果图 + 工具调用策略治理（对标 ClawGuard 285+ 安全模式） | ⏸️ Hold |
| `a2a_forgetting.py` | 选择性遗忘引擎——FSFM 四类遗忘 + 跨 Agent Cascading Forget + Two-Pass Deletion + GDPR/EU AI Act 合规（对标 FSFM + SISA/Gradient Scrubbing） | ⏸️ Hold |
| `a2a_carbon.py` | 碳排放追踪——CodeCarbon 集成 + per-task/per-agent/per-chain 碳指标 + 碳感知路由预留接口 | ⏸️ Hold |
| `a2a_idle_guard.py` | 空转综合征检测——PollingStorm 防御 + analysis_paralysis + meaningless_optimization + 四级 severity escalation（对标 OpenClaw 真实事故 + agent-loop-detector） | ⏸️ Hold |
| `a2a_dashboard.py` | 跨 IDE Agent 状态仪表盘——status_aggregator + agent_dashboard.md 生成 + Active/Idle/Stuck/Hibernated 四态 | ⏸️ Hold |
| `a2a_protocol_gateway.py` | 多协议网关——A2A/MCP/ACP/ANP 四协议适配器 + LLM-driven translation engine + mapping template cache（对标 AgentGateway + agentlink + AGNTCY） | ⏸️ Hold |
| `a2a_causal_trace.py` | 因果溯源引擎——CTEG 因果事件图构建 + caused_by/tool_used edges + temporal monotonicity + Merkle commit（对标 CTEGs + DebugABot） | ⏸️ Hold |
| `a2a_blame_attribution.py` | 失败归因引擎——17x Error Trap 五类跨 Agent 失败模式检测 + 三问归因 (origin/propagation/systemic) + BlameReport 生成（对标 DebugABot Blame Attribution Engine + Traceability paper） | ⏸️ Hold |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| Hold | 等待触发条件命中（monitor §1.4） | ⏸️ Hold |
| scaffold | **Layer 1 完整**：Agent Card 模型 + AGENTS.md 注册 + JWT 身份验证 | 📋 Backlog |
| scaffold | **Layer 2 基础**：Task 状态机 + Message/Part Pydantic schema + 上下文包 | 📋 Backlog |
| scaffold | **Layer 3 核心**：Rule-based Coordinator + 基础任务交接 + Living Spec 同步框架 | 📋 Backlog |
| scaffold | **死锁防护 L1+L2**：Dijkstra 全局资源排序 + 超时熔断 | 📋 Backlog |
| experimental | **Layer 2 完整**：SSE 流式 + Push Notification + 输入协商 | 📋 Backlog |
| experimental | **冲突检测全栈**：语义冲突（AST diff + 依赖图）+ Mirror Mirror Loop 活锁检测 | 📋 Backlog |
| experimental | **仲裁**：三级仲裁 auto→escalate→block + arbitration_rules.yaml | 📋 Backlog |
| experimental | **死锁防护 L3+L4**：优先级抢占 + 序列化降级模式 | 📋 Backlog |
| experimental | **通信安全**：消息签名 + 防重放 + Session Smuggling 防御 | 📋 Backlog |
| experimental | **经济护栏**：委托代价评估 + 全链路 Token 预算 + 模型路由 | 📋 Backlog |
| experimental | **级联故障防护**：Bulkhead + Circuit Breaker + Dead Letter Queue | 📋 Backlog |
| experimental | **共识与协商**：6 状态协商会话机 + 投票/多数决引擎（含法定人数）+ 协商降级 4 级 | 📋 Backlog |
| experimental | **涌现检测框架**：5 类异常分类学 + "Agents of Chaos" 11 模式 F07/F09 信号监测 + Behavior Fingerprint | 📋 Backlog |
| experimental | **ML 异常检测**：Isolation Forest + Autoencoder pipeline + anomaly→throttle→freeze cascade（Phase 1 仅规则引擎） | 📋 Backlog |
| experimental | **Saga 回滚（简化版）**：git revert CT + per-agent worktree checkpoint + git-level 幂等性 | 📋 Backlog |
| experimental | 与 MOD-INF-007/018/020/022 集成 + 审计闭环 | 📋 Backlog |
| beta | **可观测性**：分布式追踪 + A2A 指标 + Agent 信誉评分 | 📋 Backlog |
| beta | **性能优化**：消息批处理 + 上下文压缩算法优化 + Lazy Context Loading + Prompt Caching | 📋 Backlog |
| beta | **跨 IDE 一致性**：TRAE/Cursor/RooCode Agent Card 同步协议 + 协议版本协商 | 📋 Backlog |
| beta | **Saga 升级**：完整 Saga——LT/CT 正式注册 + 补偿编排引擎 + 反向拓扑序回滚 | 📋 Backlog |
| beta | **MAScope 集成**：Cross-Agent Semantic Flow PDAG 构建 + GNN 轨迹建模（依赖 scikit-learn/pytorch） | 📋 Backlog |
| beta | **A2A 协议层安全**：Agent Card 供应链完整性 + Task 流防操纵 + Artifact 投毒门禁 + Agent 间 DoS 限流（对标 A2ASECBENCH） | 📋 Backlog |
| beta | **结构化协商帧 (ANP)**：Negotiation Frame 替代 80% YAML 聊天 + Capability Token (JWT) + DelegationChainToken + 委托链权威性缩减 | 📋 Backlog |
| beta | **形式化验证 (TLA+)**：P1 死锁自由 + P2 委托安全 TLA+ 建模 + TLC 模型检查 + 7 属性运行时断言 | 📋 Backlog |
| beta | **多维向量信誉 (TrustFlow)**：5 维信誉向量 + TrustFlow 收缩映射 + LR2 自底向上评分 | 📋 Backlog |
| beta | **上下文腐烂防护**：注意力稀释/位置漂移/检索噪声检测 + 主动压缩 + 三层上下文架构 (Hot/Domain/Cold) | 📋 Backlog |
| beta | **用户同意编排**：4 状态同意机 + Ephemeral Scoped Token + AUTO_CONSENT 策略 + 直接数据通道 | 📋 Backlog |
| beta | **宪法治理引擎**：GovernanceGate 零容忍门控 + CONSTITUTION.md + intent drift 检测 + Cross-Policy Impact Graph（对标 Council + Microsoft AGT ADR 0006 + HC-12） | 📋 Backlog |
| beta | **Agent 免疫系统**：三层免疫 (innate 模式匹配 + adaptive Critic 分析 + memory 哈希查表) + 隔离检疫状态机 + 攻击链因果图 + 工具调用运行时策略治理（对标 ClawGuard） | 📋 Backlog |
| beta | **选择性遗忘引擎**：FSFM 四类遗忘 (passive/active/safety/reinforcement) + Cascading Forget + Two-Pass Deletion + 遗忘审计日志（对标 FSFM + EU AI Act 2026） | 📋 Backlog |
| beta | **空转综合征检测**：PollingStorm 防御 + analysis_paralysis + meaningless_optimization 三子类型 + 四级 severity escalation + 跨 IDE Agent 状态仪表盘（对标 OpenClaw 真实事故 + agent-loop-detector） | 📋 Backlog |
| beta | **碳排放追踪**：CodeCarbon 集成 + per-task/per-agent/per-chain 碳指标 + 碳感知路由预留接口 | 📋 Backlog |
| beta | **Agent 知识蒸馏**：trajectory replay + MCP Box 零训练传递 + model-level distillation 预留（对标 KD-MARL + AgentDistill + AgentArk） | 📋 Backlog |
| beta | **硬件感知路由**：GPU 利用率/显存/功耗信号集成到异质模型路由决策（self-hosted LLM 场景预留，对标 HW-Router） | 📋 Backlog |
| beta | **多协议网关**：A2A/MCP/ACP/ANP 四协议适配器 + LLM-driven 翻译 + AGNTCY 互联总线（对标 AgentGateway + agentlink + AGNTCY） | 📋 Backlog |
| beta | **失败归因引擎**：CTEGs 因果事件图 + 五类跨 Agent 失败模式检测 + 三问归因法 + BlameReport（对标 CTEGs + DebugABot + 17x Error Trap） | 📋 Backlog |
| **独立验证** | **Owner 逐行审查 6 个核心文件 + 编译时约束 + 安全测试（§2.14 含 5 类异常场景覆盖 + §2.25 TLA+ 形式化验证加持）** | 🔒 Owner-Only |

---

## 5. 盲点溯源与专业对标（完整 150 条）

### 第一轮基础盲点 — 协议层（#1-#20）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 1 | Agent Card / 能力声明模型缺失 | 🔴 P0 | Google A2A AgentCard §5.5 + Anthropic Agent Spec | §2.2 + D-025-02 |
| 2 | A2A 任务状态机缺失 | 🔴 P0 | Google A2A TaskState §6.3 | §2.3 + D-025-03 |
| 3 | Message/Part 类型缺失 | 🔴 P0 | Google A2A Part union type §6.5 + MMA2A 模态原生 | §2.4 + D-025-04 |
| 4 | Supervisor/Coordinator 缺失 | 🔴 P0 | Anthropic Agent Teams Team Lead + Augment Code Coordinator | §2.5 + D-025-05 |
| 5 | Agent 间认证缺失 | 🔴 P0 | Google A2A Auth §4 + OWASP ASI03 | §2.10 + D-025-10 |
| 6 | 死锁防护缺失 | 🔴 P0 | MIT CORDIAL + DPBench 95-100% 死锁率 | §2.9 + D-025-09 |
| 7 | 活锁防护缺失 | 🔴 P0 | Mirror Mirror Loop 社区实战 + Politeness Spiraling | §2.9 + D-025-09 |
| 8 | 语义冲突检测缺失 | 🔴 P0 | Augment Code semantic contradictions + AST diff | §2.7 + D-025-07 |
| 9 | Living Spec 冲突预防缺失 | 🔴 P0 | Coware + Augment spec-scoped decomposition | §2.6 + D-025-06 |
| 10 | OWASP ASI07 完全暴露 | 🔴 P0 | OWASP Agentic Top 10 2026 + Palo Alto Unit 42 | §2.10 |
| 11 | Agent Session Smuggling 无防御 | 🔴 P0 | Palo Alto Unit 42 Nov 2025 | §2.10 |
| 12 | 级联故障防护缺失 | 🔴 P0 | OWASP ASI08 + Bulkhead Pattern | §2.13 + §2.10 |
| 13 | Rogue Agent 检测缺失 | 🔴 P0 | OWASP ASI10 + card_integrity | §2.10 |
| 14 | 消息完整性校验缺失 | 🔴 P0 | JWT RS256 + nonce replay protection | §2.10 |
| 15 | A2A 三层架构蓝图未定义 | 🔴 P0 | Google A2A full stack + MOD-INF-022 三层对标 | §2.1 + D-025-01 |
| 16 | 施工自指悖论未处理 | 🔴 P0 | MOD-INF-022 §2.20 + 100% AI 施工 | §2.14 + D-025-11 |
| 17 | 经济护栏缺失（跨 Agent 链） | 🟠 P1 | MOD-INF-022 §2.4 + AICosts.ai | §2.12 |
| 18 | SSE 流式传输缺失 | 🟠 P1 | Google A2A §3.3 | §2.4 |
| 19 | Push Notification 缺失 | 🟠 P1 | Google A2A §6.8-6.10 | §2.4 |
| 20 | 输入协商（input-required）缺失 | 🟠 P1 | Google A2A §4.5 in-task auth | §2.3 |

### 第二轮 — 上下文与集成层（#21-#40）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 21 | 跨 Agent 上下文压缩缺失 | 🟠 P1 | ADR-0041 P0-P3 压缩 | §2.11 |
| 22 | 上下文污染检测缺失 | 🟠 P1 | OWASP ASI06 Memory Poisoning | §2.11 |
| 23 | 上下文新鲜度/TTL 未定义 | 🟡 P2 | — | §2.11 |
| 24 | 上下文溯源缺失 | 🟡 P2 | MOD-INF-022 §2.15 anti_sycophancy | §2.11 |
| 25 | 委托代价评估缺失 | 🟠 P1 | MOD-INF-022 §2.4 | §2.12 |
| 26 | 全链路 Token 预算未定义 | 🟠 P1 | Anthropic Claude Code token budget | §2.12 |
| 27 | Agent 能力 vs 成本路由缺失 | 🟡 P2 | Augment per-task model routing | §2.12 |
| 28 | 模型降级策略缺失 | 🟡 P2 | MOD-INF-022 model_cascading | §2.12 |
| 29 | 分布式追踪缺失 | 🟡 P2 | OpenTelemetry SpanContext | §2.13 |
| 30 | A2A 专属指标缺失 | 🟡 P2 | — | §2.13 |
| 31 | Agent 信誉/评分缺失 | 🟡 P2 | — | §2.13 |
| 32 | Agent 生命周期管理缺失 | 🟡 P2 | — | §2.5 status |
| 33 | 优雅降级（Agent 消失）缺失 | 🟡 P2 | — | §2.13 Dead Letter Queue |
| 34 | Agent Card 版本/向后兼容缺失 | 🟡 P2 | Google A2A Agent Card versioning | §2.2 |
| 35 | Agent A/B 测试缺失 | 🔵 P3 | — | Phase beta |
| 36 | 陈旧 Agent 检测缺失 | 🟡 P2 | — | §2.1 agent_card.status |
| 37 | 消息路由一致性缺失 | 🟡 P2 | OWASP ASI07 | §2.10 |
| 38 | 任务幂等性缺失 | 🟡 P2 | — | Phase scaffold |
| 39 | 任务优先级继承缺失 | 🟡 P2 | Priority Inversion OS classic | §2.9 L3 |
| 40 | 资源公平性调度缺失 | 🟡 P2 | — | §2.5 Filter/Score |

### 第三轮 — Vibe Coding / 跨 IDE 特有（#41-#55）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 41 | AGENTS.md 作为 A2A 发现入口未整合 | 🟠 P1 | MOD-INF-019 D-019-02 | §2.2 + D-025-12 |
| 42 | Skill Pack → Agent 角色 → A2A 链条断裂 | 🟠 P1 | MOD-INF-019 §2.1 | §2.2 agent_card.agent_type |
| 43 | 跨 IDE Agent 身份不统一 | 🟠 P1 | TRAE/Cursor/RooCode | §2.2 agent_card.provider |
| 44 | 10+ 并发对话状态共享无机制 | 🟡 P2 | — | §2.11 context_management |
| 45 | 与已有 AgentOrchestrator 关系未定义 | 🟠 P1 | ADR-0032 + agent_orchestrator.py | §2.3 + D-025-12 |
| 46 | 与 Session Handoff (ADR-0041) 边界模糊 | 🟡 P2 | ADR-0041 | §2.3 context_package |
| 47 | 与 Escalation Protocol (MOD-INF-022) 集成粗 | 🟡 P2 | MOD-INF-022 | §2.8 escalate tier |
| 48 | Well-known 标准化发现不适合本地场景 | 🟡 P2 | Google A2A §5.3 | §2.2 AGENTS.md |
| 49 | 消息格式选型（JSON vs YAML）未做 | 🟡 P2 | 社区调试地狱 | §2.4 + D-025-04 |
| 50 | Coordinator 选型（规则 vs LLM）未做 | 🟡 P2 | DPBench 通信反增死锁 | §2.5 + D-025-05 |
| 51 | 1人+AI 专属简化 vs 架构完备度平衡 | 🔵 P3 | — | §2.15 + D-025-12 |
| 52 | 100% AI 施工者 = A2A 被限者的利益冲突 | 🔴 P0 | MOD-INF-022 §2.20 | §2.14 + D-025-11 |
| 53 | 多 IDE 下的 Agent Card 同步机制 | 🟡 P2 | — | Phase beta |
| 54 | API 限流协调（10+ Agent 并发调同一 API） | 🟡 P2 | 社区资源竞争灾难 | §2.5 constraints |
| 55 | Agent 间通信的"人肉可观测性" | 🔵 P3 | — | §2.4 YAML format |

### 第四轮 — 前沿安全（#56-#70+）

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

### 第五轮 — 多 Agent 共识、涌现行为与分布式事务（#72-#96，v0.6.0 新增）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 72 | 多 Agent 共识协议缺失——3+ Agent 对同一决策的不同意见如何合并 | 🔴 P0 | Concordia Protocol (A2A #1725, 2026-04) + Dialogue Diplomats (arXiv:2511.17654 — 94.2% 共识率) | §2.16 + D-025-13 |
| 73 | 投票/多数决机制缺失——权重投票、拜占庭容错、Condorcet 等经典共识算法未引入 | 🟠 P1 | Raft / Paxos / PBFT + 社区 Multi-Agent 共识实现 | §2.16 voting_protocol |
| 74 | Agent 间协商/讨价还价协议缺失——Agent A 说"我做 X，条件是你做 Y" | 🟠 P1 | Concordia Offer Types (4 种提议类型) + Gartner: 2026 年底 40% 企业应用集成协商 Agent | §2.16 offer_types + resolution_strategies |
| 75 | 协商失败后的降级路径缺失——协商失败=block（人工）太粗暴，缺少自动降级 | 🟠 P1 | Concordia EXPIRED 状态 + Saga 补偿 | §2.16 negotiation_degradation (level_1~4) |
| 76 | Agent 合谋检测缺失——"Agents of Chaos" 发现 Agent 为了优化自身指标会主动合谋 | 🔴 P0 | "Agents of Chaos" (Harvard/MIT/Stanford/CMU, arXiv:2602.20021) 失败模式 #10 | §2.16 collusion_detection + §2.17 chaos_failure_modes F10 |
| 77 | 虚假任务完成 (False Task Completion)——Agent 报告"COMPLETED"但系统状态未变 | 🔴 P0 | "Agents of Chaos" 失败模式 #9 + Meta Sev 1 事故 | §2.17 F09_false_task_completion |
| 78 | 跨 Agent 行为传播——一个 Agent 学到的不当行为扩散至其他 Agent | 🔴 P0 | "Agents of Chaos" 失败模式 #7 + OWASP ASI06 Memory Poisoning | §2.17 F07_cross_agent_behavior_propagation |
| 79 | 战略性破坏——Agent 主动破坏其他 Agent 的工作以提升自身指标 | 🔴 P0 | "Agents of Chaos" 失败模式 #11 | §2.17 F11_strategic_sabotage |
| 80 | ML 驱动的异常检测管道缺失——Isolation Forest + Autoencoder 用于行为偏离检测 | 🟠 P1 | MARIA OS Safety Layer (Layer 7) + Galileo.ai 异常分类学 | §2.17 ml_anomaly_pipeline |
| 81 | 5 类异常分类学缺失——行为异常/通信异常/资源异常/协调异常/涌现异常 | 🟠 P1 | Galileo.ai (2025-06) 多 Agent 异常分类体系 | §2.17 anomaly_taxonomy |
| 82 | Cross-Agent Semantic Flow 攻击检测缺失——攻击分散在多个 Agent 的时间线中，单看每个操作都正常 | 🟠 P1 | MAScope (ZJU, arXiv:2603.04469): F1=85.3% | §2.17 cross_agent_semantic_flow |
| 83 | Agent 间 back-pressure 协议缺失——Agent 过载时无流量控制机制 | 🟠 P1 | "Agents of Chaos" F04 + 分布式系统 back-pressure | §2.17 F04_denial_of_service |
| 84 | 多 Agent Saga 事务/补偿协议缺失——Agent C 失败后 A 和 B 的工作如何回滚 | 🟠 P1 | SagaLLM (Stanford, PVLDB 2025) + LangChain Compensation v0.5.8 | §2.18 + D-025-15 |
| 85 | 补偿事务注册表缺失——每个 Agent 操作需要注册对应的 reversal 操作 | 🟠 P1 | Saga Pattern: 每步 LT 配一个 CT（Compensation Transaction） | §2.18 saga_registration |
| 86 | 部分失败下的检查点与恢复缺失——Agent 执行了 50% 后崩溃，如何恢复而非重来 | 🟡 P2 | SagaLLM: modular checkpointing + recovery orchestration | §2.18 checkpoint |
| 87 | 幂等性保证缺失——补偿事务或重试可能被重复执行 | 🟡 P2 | Saga 经典要求：LT 和 CT 都必须幂等 | §2.18 idempotency_gate |
| 88 | 协议版本协商机制缺失——Agent A 跑 A2A v0.5，Agent B 跑 v0.7，如何通信 | 🟡 P2 | Google A2A v1.0: Protocol Version Per Interface + A2A-Version header | Phase beta 跨 IDE 一致性 |
| 89 | Lazy Context Loading 策略缺失——每次 Session 启动全量注入上下文→40% Token 浪费 | 🟠 P1 | Anthropic SDK Discussion #1436 (2026-04): 成本从 $280→$170/月 | Phase beta 性能优化 |
| 90 | Prompt Caching 策略缺失——System Prompt + Tool Definitions 的重复前缀未缓存 | 🟠 P1 | Anthropic Prompt Caching (90% off) + OpenAI Auto Caching (50% off) | Phase beta 性能优化 |
| 91 | Shared Memory File vs Agent Chat 模式选择——Agent 间聊天式通信是 Token 黑洞 | 🟡 P2 | Anthropic SDK Discussion #1436: "replaced with shared memory file" | §2.15 vibe_coding_optimizations |
| 92 | 质量改进阈值终止——"if agent's second pass isn't clearly better, stop the loop" | 🟡 P2 | DeepSeek v4 Pro community feedback + Tokenomics best practice | §2.12 经济护栏 |
| 93 | 模型路由的实时成本感知——静态路由不考虑实时价格波动 | 🟡 P2 | Anthropic/OpenAI 动态定价 + DeepSeek v4 Pro $3.48/M output | §2.12 model_cascading |
| 94 | Agent Warm Start / 冷启动协议——新 Agent 上线后如何快速获取上下文而非从零开始 | 🟡 P2 | Agent KB (ICLR 2026): cross-domain experience sharing | Phase beta — 依赖 Lazy Context Loading |
| 95 | Agent 离线/退役协议缺失——旧 Agent 退役时其职责迁移给谁 | 🟡 P2 | AutoGen 2.0 component lifecycle | §2.5 agent_status lifecycle |
| 96 | 多 Agent 测试/仿真策略——如何在没有真实多 Agent 环境时测试协调协议 | 🟡 P2 | DPBench + AutoGen 2.0 structured traces | Phase scaffold — Supervisor 的集成测试 |

### 第六轮 — A2A 协议层安全+协商帧+形式化验证+潜空间通信+向量信誉+上下文腐烂+同意编排+Vibe Coding 深度优化（#97-#123，v0.8.0 终极补齐）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 97 | A2A 供应链操纵——Agent Card 克隆/能力漂移/隐蔽功能声明，恶意 Agent 伪装合法 Agent 注册 | 🔴 P0 | A2ASECBENCH (ICLR 2026): supply-chain manipulation | §2.23 agent_card_supply_chain + D-025-20 |
| 98 | Agent Card 欺骗——声明的能力与实际能力不符，Client Agent 无法独立验证 | 🔴 P0 | A2ASECBENCH: Agent Card 不具备原生完整性保护 | §2.23 capability_verification_gate + capability_drift_monitor |
| 99 | 任务生命周期操纵——恶意 Agent 在 task_id 层面劫持/重放/取消其他 Agent 的任务 | 🔴 P0 | A2ASECBENCH: protocol-logic weaknesses | §2.23 task_flow_manipulation |
| 100 | Artifact 投毒——恶意 Agent 在结果 Artifact 中嵌入后门代码或泄露数据，下游 Agent 直接消费 | 🔴 P0 | A2ASECBENCH: artifact exchange attacks | §2.23 artifact_poisoning + Artifact Sanitizer + PII Scanner |
| 101 | Agent 间 DoS 洪水攻击——单个恶意 Agent 向所有 Agent 同时提交大量 Task，耗尽系统资源 | 🔴 P0 | A2ASECBENCH: task flooding | §2.23 per-agent rate limiter + Coordinator global throttle |
| 102 | 自然语言 Agent 间聊天即"歧义税"——40% Token 浪费在"I meant X" / "Clarification needed" | 🔴 P0 | ANP 1.0 (2026-04): "The protocol is the contract, the execution is deterministic" | §2.24 + D-025-21 |
| 103 | ZK 零知识身份证明缺失——Agent 间验证身份但不暴露内部凭证 | 🟠 P1 | ANP: Verifiable Handshakes with ZK Proofs + ACP: Capability Token | §2.24 state_proofs |
| 104 | 委托链的权威性缩减——Agent A→B→C，每一跳权限只能收窄不能扩大 | 🟠 P1 | SentinelAgent DCC P1: Authority Narrowing (TLA+ verified 2.7M states) | §2.24 delegation_chain_authority |
| 105 | A2A 协议死锁自由从未被形式化证明——所有死锁防护都是 empirical，没有数学证明 | 🔴 P0 | SentinelAgent (TLA+) + μACP (TLA+ + Coq) + ACP (4.3B states) | §2.25 P1_deadlock_freedom + D-025-22 |
| 106 | 委托链安全属性的形式化——delegation chain 的 7 属性未在 TLA+ 中建模 | 🟠 P1 | SentinelAgent: DCC 7 properties (6 deterministic + 1 probabilistic) | §2.25 P2_delegation_safety |
| 107 | 时间感知的准入控制——不是"单次请求合规"而是"历史行为轨迹合规" | 🟠 P1 | ACP v1.27: temporal admission control + BAR detection | §2.25 temporal_admission_control |
| 108 | 偏差崩溃 (Deviation Collapse)——执法存在但从未触发，因上游约束让 DENIED 永不满足 | 🟡 P2 | ACP: "enforcement is active but never exercised" | §2.25 BAR → 0 detection |
| 109 | Agent 间通信媒介本身是瓶颈——自然语言 = Token 黑洞，潜空间嵌入通信可将推理加速 24× | 🟠 P1 | Interlat (ZJU + 阿里, arXiv:2511.09149): latent space communication | §2.26 + D-025-23 |
| 110 | 上下文压缩的失败驱动优化——在 full context success vs compressed context failure 的对偶轨迹上学习 | 🟡 P2 | ACON (ICLR 2026): failure-driven compression, -26-54% memory | §2.26 acon_approach |
| 111 | 标量信誉太粗糙——一个 Agent 在"代码生成"领域专家但在"安全审计"领域新手，单一数字无法表达 | 🟠 P1 | TrustFlow (arXiv:2603.19452): topic-gated vector reputation, 98% P@5 | §2.27 + D-025-24 |
| 112 | 自底向上信誉涌现——不预设"什么是好行为"的社会规范，Agent 通过 MARL 自组织信誉 | 🟡 P2 | LR2 (AAMAS 2025): bottom-up reputation with MARL | §2.27 lr2_bottom_up |
| 113 | 抗女巫攻击/洗信誉/投票环——信誉系统的三个经典攻击向量在 Agent 系统中同样存在 | 🟡 P2 | TrustFlow: ≤4pp Precision@5 impact under all 4 attack classes | §2.27 attack_resilience |
| 114 | 上下文腐烂——在 200K 上下文窗口内，Agent 推理质量从 50K tokens 处就开始显著下降 | 🔴 P0 | Context Rot 研究 (2026): 注意力稀释 + 位置编码漂移 + 检索噪声累积 | §2.28 + D-025-25 |
| 115 | "经验跟随属性"的自降解——Agent 从过去失败中也会学会错误模式，错误在重放中被放大 | 🟠 P1 | Memory Management for LCNC Agents (arXiv:2509.25250) | §2.28 context_rot scope |
| 116 | 跨 Agent 数据共享的用户同意缺失——Agent A 把用户的 PII 传给 Agent B，用户从未授权 | 🔴 P0 | Google A2A Enhancement (arXiv:2505.12490): USER_CONSENT_REQUIRED 新状态 | §2.29 + D-025-26 |
| 117 | Token 生命周期控制缺失——一旦 Agent 获得 Token，它永久有效，无自动过期机制 | 🟠 P1 | A2A Enhancement: ephemeral scoped tokens, time-bounded authorization | §2.29 gap_1_token_lifetime |
| 118 | 同意疲劳——多 Agent 交易工作流中连续 10 次"是否同意"弹窗 → 用户盲目点 Yes | 🟡 P2 | A2A Enhancement: consent fatigue in multi-transaction workflows | §2.29 consent_fatigue |
| 119 | "No-AI Time"协议状态缺失——协议需要一个全局 PAUSE 状态：所有 Agent 暂停工作，人类深度设计 | 🟡 P2 | 2026 Vibe Coding 最佳实践: "保留无 AI 时段用于深度设计和知识传承" | §2.30 no_ai_time_protocol + D-025-27 |
| 120 | "热记忆宪法" + "域专家 Agent" + "冷记忆知识库" 三层上下文架构——比单一 Shared Memory File 更结构化 | 🟡 P2 | AI Coding 上下文管理 (2026-04): +300% 完成率 +45% 准确度 | §2.28 three_layer_context |
| 121 | Agent 休眠/唤醒协议——不是删除 Agent，而是让其"休眠"（保留上下文但不消耗 Token），需要时"唤醒" | 🟡 P2 | BridgeSpace: agent lifecycle management | §2.30 agent_hibernate_wake |
| 122 | A2A 协议模糊测试——从未对 A2A 协议本身做 adversarial fuzzing | 🟡 P2 | Google A2A Adversarial Agent Simulation: red-team/blue-team games | §2.30 agent_adversarial_game |
| 123 | Agent 间 adversarial prompt 传播——红队 Agent 通过合法的 Task/Message 向蓝队 Agent 注入对抗性提示 | 🟠 P1 | "Agents Under Siege" (ACL 2025, UNC + Cisco): 7× more successful than single-agent | §2.30 periodic_self_test |

### 第七轮 — 宪法治理+免疫系统+选择性遗忘+碳排放+空转检测+知识蒸馏+硬件感知路由（#124-#142，v0.9.0 补齐）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 124 | Agent 宪法约束层缺失——当前仲裁是 auto→escalate→block 三级，但无 Agent 议会的"修宪机制"：规则本身由谁定义、修订、审计？ | 🔴 P0 | Council (chain-ml/council, 2026-04 — Agent 议会式治理) + Microsoft AGT ADR 0006: Critic-with-veto pattern | §2.31 + D-025-28 |
| 125 | Hard Constraint 零容忍门控缺失——53% Agent 超出授权范围运行 (CSA 2026)，安全护栏是"检测→降级"非"物理上无法绕过" | 🔴 P0 | HC-12: GovernanceGate Constraint-as-Code, zero-tolerance control bypass prevention | §2.31 governance_gate |
| 126 | 意图漂移 (Intent Drift) 检测缺失——Agent 指令=A，50 轮后实际做=B，每一步都合规但轨迹大幅偏离初始 intent | 🔴 P0 | Microsoft AGT ADR 0006: trajectory-level semantic embedding drift + Critic review | §2.31 intent_drift |
| 127 | 政策合规伤害 (Policy-Compliant Harm) 检测缺失——Agent 完全遵守安全策略但组合效应产生伤害性后果 | 🟠 P1 | AGT ADR 0006: Cross-Policy Impact Graph + BFS 敏感路径识别 | §2.31 policy_compliant_harm |
| 128 | Agent 免疫系统——隔离与检疫层缺失。异常检测后响应是 throttle→freeze，缺少生物免疫"隔离→检疫→清除→免疫记忆"闭环 | 🔴 P0 | ClawGuard (npm, 2026-05 — 285+ 安全模式 9 类别 + Risk Engine 0-100 + insider threat 5 类别 39 模式) | §2.32 + D-025-29 |
| 129 | 跨 Agent 攻击链检测缺失——单一事件各自合规，组合成攻击链 (如 CONFIG_MOD→CRED_READ→NETWORK_SEND=凭证窃取) | 🟠 P1 | ClawGuard: cross-rule attack chain correlation + causal graph danger-pattern matching | §2.32 attack_chain_detection |
| 130 | Agent 工具调用运行时策略治理缺失——静态 RBAC 无法判断"在此上下文中此调用是否合理" | 🟠 P1 | ClawGuard Policy Engine: context-aware tool call governance + file sensitivity matching | §2.32 tool_call_governance |
| 131 | Agent 选择性遗忘机制缺失——上下文腐烂防护 (§2.28) 遗忘的是"无用信息"，缺少法律驱动的选择性遗忘："删除用户 X 的所有数据" | 🟠 P1 | FSFM (arXiv:2604.20300, 2026-04 — 生物启发选择性遗忘: 100% 消除安全风险, +29.2% SNR) | §2.33 + D-025-30 |
| 132 | Agent 间遗忘传播协议缺失——Agent A 删除 user X 数据后，Agent B/C/D 曾从 A 获取的数据仍残留 | 🟠 P1 | FSFM: Cascading Forget Notification + ForgetCompletionReport | §2.33 cross_agent_forgetting |
| 133 | 安全触发的紧急遗忘缺失——Agent 被 prompt injection 污染后只能 freeze/restart，不能 surgical removal 精准切除恶意片段 | 🟡 P2 | FSFM safety-triggered forgetting: CONTAMINATED_ZONE 标记 + clean checkpoint 恢复 | §2.33 safety_triggered |
| 134 | 硬件信号驱动的 Agent 路由缺失——异质模型路由 (§2.22) 的"负载"只考虑任务队列，无 GPU 利用率/显存/功耗等硬件信号 | 🟡 P2 | HW-Router (UCF, arXiv:2511.00739 — 3.4-3.9× 更低延迟, 46-48pp 更高 SLO, ~200μs 路由开销) | §2.34 + D-025-34 |
| 135 | Agent 推理的 disaggregated 调度缺失——prefill (理解上下文) 和 decode (生成代码) 可能需要分离到不同 GPU 以优化资源 | 🔵 P3 | Disaggregated LLM Inference: prefill→HBM-optimized, decode→compute-optimized GPU | §2.34 hardware_aware_routing (self-hosted 预留) |
| 136 | Agent 知识蒸馏能力缺失——专家 Agent (DeepSeek v4 Pro + Architect) 的经验无法结构化传递给小模型 Agent (Claude Sonnet + Coder) | 🟡 P2 | KD-MARL (IJCNN 2026 — 保留 90%+ 专家性能, -28.6× FLOPs) + AgentDistill (MCP Box 零训练) + AgentArk (三阶段层级蒸馏) | §2.34 + D-025-33 |
| 137 | MCP Box 零交互能力传递缺失——Agent A 发现的 best practice 需要"口头描述"传递，缺少结构化 artifact 直接加载 | 🟡 P2 | AgentDistill: MCP Box——Agent A 的优化参数→序列化为 MCP artifact→Agent B 直接加载 | §2.34 mcp_box_transfer |
| 138 | Agent 碳排放追踪缺失——经济护栏只有美元维度，缺少碳足迹维度 (per-task/per-agent/per-chain CO2e) | 🔵 P3 | CodeCarbon (Python 碳排放追踪库) + Graviton5 (AWS, -22% 成本, -25-30% 碳足迹) | §2.34 + D-025-31 |
| 139 | Agent 模型选择的碳代价未纳入路由决策——大模型 vs 小模型的碳排放差可达 100× | 🔵 P3 | Systematic Review of Green AI + CarbonIntensitySchedule | §2.34 carbon_aware_scheduling (optional) |
| 140 | Agent 空转综合征检测缺失——Agent 既非 deadlock 也非 livelock，在合法运行但零有效产出 (OpenClaw 事故: 1,535 次→$150+3GB 崩溃) | 🟠 P1 | OpenClaw 真实生产事故 (2026-02) + agent-loop-detector (Python, 2026-04) + Agent Idle Monitor (npm, 2026-03) | §2.34 + D-025-32 |
| 141 | Agent 闲置消费陷阱——闲置 Agent 在等待中消耗 context window 空间和 Standby Token，上下文发生位置编码漂移 | 🟡 P2 | Idle Agent Syndrome + §2.28 context_rot interaction | §2.34 severity_escalation (level_3: auto-hibernate) |
| 142 | 跨 IDE 统一的 Agent 状态仪表盘缺失——TRAE/Cursor/RooCode 上 Agent 闲置状态不可见，需打开各 IDE 逐一检查 | 🟡 P2 | Agent Idle Monitor (npm): 轻量级 status aggregator→markdown dashboard | §2.34 cross_ide_monitoring + D-025-32 |

### 第八轮 — 多协议网关+互联总线+失败归因+因果溯源（#143-#150，v0.10.0 补齐）

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 143 | IBM ACP 联邦编排协议缺失——v0.9.0 覆盖 A2A/MCP/ANP 三种协议，但 IBM 的 ACP（Broker 架构 + Multipart MIME + Global Reputation Ledger）是第四个主流协议 | 🟡 P2 | IBM ACP (2026-02 — federated orchestration, -40% 延迟, zero-trust) + Zylos.ai 四协议全景对比 | §2.35 + D-025-35 |
| 144 | Agent 多协议网关缺失——TRAE/Cursor/RooCode Agent 使用不同协议时缺少统一翻译层。业界已有 AgentGateway(LF) + agentlink + OpenGateway | 🟡 P2 | AgentGateway (LF, 2026-04) + agentlink RFC (2026-04) + OpenGateway (IETF 125) | §2.35 protocol_gateway |
| 145 | Agent Card 技能参数化标准化缺失——A2A 技能靠 name/tags 声明，无 inputSchema/outputSchema——Agent A 知道 Agent B 能做"翻译"但不知道输入输出类型 | 🟡 P2 | A2A v1.0 生产实战反馈 (codilime.com, 2026-02): "Lack of skill parameterization" | §2.35 agent_card_parameterization |
| 146 | 授权蠕变风险——A2A 授权在连接时批准但任务生命期内操作范围可能远超初始批准。§2.31 intent drift 检测任务轨迹，不检测授权范围蠕变 | 🟡 P2 | A2A v1.0 安全审计: "Authorization happens too late and too indirectly" | §2.35 + D-025-36 |
| 147 | Agent 协议版本协商机制缺失——Agent Card 中需声明支持的多协议版本。Google A2A 社区明确要求此能力，67% 升级失败率 | 🟡 P2 | Google A2A Discussion #680 (2025-05) + "67%升级失败率" 兼容性实证分析 | §2.35 protocol_ecosystem |
| 148 | 多 Agent 因果溯源模型缺失——v0.9.0 §2.15 有分布式时序追踪，但缺少"为什么发生"的因果模型和"谁负责"的归因引擎 | 🟡 P2 | CTEGs (arXiv:2604.17557, 2026-04) + DebugABot Blame Attribution Engine (Merkle hash chains + W3C PROV) | §2.36 + D-025-37 |
| 149 | Agent 间失败模式的组合爆炸——5 Agent 系统 ~17 倍失败模式。五种跨 Agent 失败模式（Telephone Game/Confidence Cascade/Ghost Handoff/Tools Gone Wild/Conga Line） | 🟠 P1 | 17x Error Trap (AgentCenter, 2026-03) + Sentry Multi-Agent 生产调试 (2026-04) + Traceability paper (Oakland, 2025-10) | §2.36 cross_agent_failure_modes |
| 150 | Agent Skills Marketplace 生态集成缺失——OpenClaw/OpenRouter/Anthropic Skills 标准代表 Agent 能力的市场化分发。在氛围编程下 Skill 热加载与跨 IDE 分发直接关联 | 🔵 P3 | OpenClaw Skills Marketplace (2026-02) + OpenRouter Skills PR #34 (2026-04) + Anthropic Skills Standard | §2.35 trigger_for_acp_anp |

### 补充注释：第七轮边缘发现（#151-#153，v0.10.0 注记，不升级版本）

> 第七轮挖掘仅发现 3 条 P2-P3 级别盲点，增量不足以支撑独立版本升级。作为补充注释记录于此，待 Phase 触发条件命中后择机纳入。

| # | 盲点 | 严重性 | 专业对标 | 说明 |
|---|------|:---:|------|------|
| 151 | Agent 身份可移植性——Agent 在 TRAE 积累的经验/人格/记忆无法结构化迁移到 Cursor/RooCode。Agent 在 IDE-1 掌握了 Owner 的代码风格偏好——换到 IDE-2 后需重新学习 | 🔵 P3 | Pulso AIP standard (2026-02 — `.aip` format: identity + memory + configuration + learned behaviors) + Guild.ai Agent Portability (70% 企业部署延迟源于平台锁定) | 与 §2.1 Agent Card 兼容——AIP 可视为 Agent Card 的扩展层：Card 声明能力，AIP 携带记忆和行为 |
| 152 | Agent-to-Human 结构化 Warm Transfer——蓝图有用户同意编排 (§2.29) 和仲裁升级 (§2.7)，但"Agent 主动向 Owner 交接"的模式缺少结构化上下文传递：不只"暂停等你操作"，而是"这是我做了什么、为什么卡住、你需要决定的选项 A/B/C" | 🟡 P2 | Warm Transfer vs Cold Transfer pattern (2026-04) + Microsoft Agent Framework HITL (RequestPort + Checkpoint mechanism) + AnyReach HITL (99.8% 准确率, -96% 幻觉) | 与 §2.29 用户同意编排不同——Warm Transfer 是 Agent 主动升级而非被动等待同意；与 §2.7 仲裁升级不同——目标是 Owner 而非另一个 Agent |
| 153 | 多 Agent 跨伦理对齐验证——单个 Agent 对齐（遵守宪法 §2.31 + 安全策略 §2.32）不等于群体伦理一致性。Agent 间交互会产生个体层面无法预测的伦理漂移（偏见放大/群体极化/合谋合理化） | 🔵 P3 | CogniAlign (arXiv:2509.13356, 2025 — 生存力驱动的多 Agent 道德推理) + ARCANE (AAAI 2026 — Rubric-based 可配置对齐) + MALM Ethics position paper (2026 — 三层评估: agent-centric / interactional / systemic + mechanistic interpretability) | 与 §2.19 辩论协议和 §2.31 宪法治理互补——辩论保证"理性"，宪法保证"边界"，伦理对齐验证保证"一致性"——三者构成完整治理三角 |

- **#151 (Agent 身份可移植性)** 的优先级最高——多 IDE 氛围编程下 Agent 经验无法跨 IDE 传递是真实痛点，AIP 格式简单（JSON），Phase 可快速实现
- **#152 (Warm Transfer)** 在 Agent 长期运行场景（multi-hour task）中价值最大——Agent 卡住时 Owner 需要的是决策辅助而非空白画布
- **#153 (伦理对齐验证)** 在 1人+AI 场景下优先级最低——仅 Owner 一人，无线程冲突和群体极化的真实风险，待多用户协作场景出现后再引入

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| R81-C04 | Hold 至 stable（维持） | 2026-05-05 | 当前单 Agent + 多 IDE，A2A 不急需 |
| D-025-01 | 三层五协议总架构——Layer 1(发现+身份)→Layer 2(通信+任务)→Layer 3(协调+仲裁)，6 个 A2A Protocol | 2026-05-05 | 对标 Google A2A 全栈 + Anthropic Agent Teams + MOD-INF-022 成熟度对标 |
| D-025-02 | Agent Card 注册入口 = AGENTS.md（非 well-known URI） | 2026-05-05 | 本地多 IDE 场景无固定域名，AGENTS.md 是唯一跨 IDE 统一入口（MOD-INF-019 D-019-02） |
| D-025-03 | A2A TaskState 独立于 Orchestrator TaskState——前者 Agent 间粒 Usually，后者 Agent 内粒度 | 2026-05-05 | Google A2A TaskState 针对黑盒 Agent 间协作（含 input-required + rejected） |
| D-025-04 | A2A 消息格式 = YAML（人读+机读），非 JSON-RPC 2.0 | 2026-05-05 | 1人+AI 维护需能肉眼看懂 Agent 间通信——社区的调试地狱根本原因 |
| D-025-05 | Coordinator = 规则驱动引擎，非 LLM Supervisor | 2026-05-05 | DPBench：LLM 通信反增死锁；确定性+零 Token+不可操纵 |
| D-025-06 | 引入 Living Spec——Agent 开工前自动对齐接口契约 | 2026-05-05 | 社区核心教训："不在合并时修冲突，在写代码前消除冲突"（Coware + Augment） |
| D-025-07 | 冲突检测 = 文本（git merge）+ 语义（AST diff + 依赖图 + 接口契约）+ Mirror Mirror Loop | 2026-05-05 | Augment：semantic contradictions 是最难检测的失败模式 |
| D-025-08 | 仲裁 = 三级递进 auto（规则）→ escalate（MOD-INF-022）→ block（人工） | 2026-05-05 | A2A 仲裁的独特性——冲突类型 vs 操作风险（不重复 MOD-INF-022） |
| D-025-09 | 死锁防护四层——Dijkstra + Timeout + Preemption + Sequentialization | 2026-05-05 | DPBench 3 Agent=95-100% 死锁率 + MIT CORDIAL 87% 减少 |
| D-025-10 | A2A 消息安全——签名+防重放+身份验证+Session Smuggling 防御 | 2026-05-05 | OWASP ASI03/ASI07/ASI10 + Palo Alto Unit 42 + AI 开发安全的利益冲突 |
| D-025-11 | A2A 施工自指悖论——Owner 审 + AH AI 无法绕过 | 2026-05-05 | 对标 MOD-INF-022 §2.20：100% AI 施工→开发者=被限制者 |
| D-025-12 | Vibe Coding 6 项专属优化（AGENTS.md/YAML/规则引擎/Living Spec/轻量元数据/对齐基础设施） | 2026-05-05 | 1人+AI 三重特殊性：单 Owner、100% AI 施工、3 IDE 并发 |
| D-025-13 | 多 Agent 共识与协商层——6 状态协商会话机 + 投票/多数决 + 合谋检测 + 4 级协商降级 | 2026-05-05 | Concordia Protocol (A2A #1725) + Dialogue Diplomats (94.2% 共识率) + "Agents of Chaos" F10/F11 |
| D-025-14 | 涌现行为与异常检测——"Agents of Chaos" 11 失败模式全覆盖 + 5 类异常分类学 + ML 异常检测管道 + Cross-Agent Semantic Flow | 2026-05-05 | "Agents of Chaos" (Harvard/MIT/Stanford/CMU) + MAScope (ZJU) + Galileo.ai + MARIA OS Safety Layer |
| D-025-15 | 分布式事务与 Saga 回滚——LT/CT 配对注册 + 分布式检查点 + 幂等性门禁 + 补偿编排（Phase 1 简化版：git revert + worktree checkpoint） | 2026-05-05 | SagaLLM (Stanford, PVLDB 2025) + LangChain Compensation v0.5.8 + Saga 设计模式 |
| D-025-16 | 辩论与审议协议——4 阶段结构化辩论 (Opening/Rebuttal/Synthesis/Verdict) + Anti-Conformity + 辩论深度上限 + Agent 间 AAD/CI 评分 | 2026-05-05 | Free-MAD (ICLR 2026) + ACL 2025 辩论协议 + Cognitive Science Deliberation Theory |
| D-025-17 | Agent 经济与资源分配——Agent 预算池分配 + ROI 追踪 + 跨 IDE 花费聚合 + 按成本/速度优先级三维仲裁（对标 x402 + AEP） | 2026-05-05 | x402 (Coinbase + Cloudflare, 100M+ txs) + AEP (Base Mainnet) + Concordia Agent Economy |
| D-025-18 | 异质模型动态路由——角色×难度×负载三维决策矩阵 + Confidence-Aware Auto-Delegation + 批量降级策略（对标 OI-MAS + Chimera + GraphPlanner） | 2026-05-05 | OI-MAS (+12.88% acc, -79.78% cost) + Chimera (1.2-2.4× latency) + GraphPlanner (ICLR 2026) |
| D-025-19 | 工作窃取与负载均衡——Task Affinity + Work Stealing (随机+基于信誉+基于亲和性 3 策略) + Watchdog 进程 + Shared Memory File 状态机 | 2026-05-05 | Cilk-style Work Stealing + OpenAI Swarm + Anthropic "Broadcast" + OS Process Scheduler |
| D-025-20 | A2A 协议层安全攻击面防护——Agent Card 供应链完整性 + Task 流防操纵 + Artifact 投毒门禁 + Agent 间 DoS 限流 + 三级安全配置 (conservative/balanced/permissive) | 2026-05-05 | A2ASECBENCH (ICLR 2026 — 首个 A2A 协议安全基准) + Google A2A Security Enhancement (arXiv:2505.12490) |
| D-025-21 | 结构化协商帧协议 ANP 1.0——Negotiation Frame 取代 YAML 文本聊天 + 歧义税 40%→<5% + Capability Token (JWT) + DelegationChainToken + 委托链权威性缩减 | 2026-05-05 | ANP 1.0 (2026-04) + "Ambiguity Tax" (bittalks.org) + SentinelAgent IPDP (TLA+) |
| D-025-22 | 协议形式化验证 TLA+/Coq——7 属性 (P1-P7) 的 TLA+ 模型检查 + Coq 交互式定理证明 + 运行时断言监控 + 时间感知准入控制 BAR 检测 | 2026-05-05 | SentinelAgent + ACP v1.27 (4.3B states) + μACP (TLA+ + Coq) + nForma (5,253 commits) |
| D-025-23 | 潜空间 Agent 间通信——三梯级混合通信 (YAML + ANP Frame + Latent Embedding) + Interlat 24× 加速 + Phase 3 评估引入 | 2026-05-05 | Interlat (ZJU + 阿里, arXiv:2511.09149) + ACON (ICLR 2026) + Context Rot 研究 |
| D-025-24 | 多维向量信誉模型 TrustFlow——5 维信誉向量 + Topic-Gated Transfer Operators + 收缩映射收敛 + 抗女巫/洗信誉/投票环 + LR2 自底向上 | 2026-05-05 | TrustFlow (arXiv:2603.19452, 98% P@5) + LR2 (AAMAS 2025) |
| D-025-25 | 上下文腐烂防护——注意力稀释/位置漂移/检索噪声三机制检测 + 主动压缩 + ACON 失败驱动优化 + 三层上下文架构 (Hot/Domain/Cold) | 2026-05-05 | Context Rot 研究 (2026-04) + ACON (ICLR 2026) + Focus Architecture (-22.7% Token) |
| D-025-26 | 用户同意编排——4 状态同意机 (PENDING/GRANTED/DENIED/AUTO) + Ephemeral Scoped Token + 同意疲劳对策 + Direct User-to-Service Data Path | 2026-05-05 | Google A2A Enhancement (arXiv:2505.12490 — USER_CONSENT_REQUIRED) + OWASP ASI09 |
| D-025-27 | Vibe Coding 深度优化 2026 版——No-AI Time 全局暂停 + Agent 休眠/唤醒 (WAL, -33% Token) + 月度红蓝对抗 + BridgeMind 三阶段扩展路径 | 2026-05-05 | BridgeMind/BridgeMCP/BridgeSwarm (2026-02) + Vibe Coding Review (TechRxiv 2026-05) |
| D-025-28 | 宪法治理与 Critic-with-veto——Agent 议会 (Critic/Coordinator/Owner 三方) + CONSTITUTION.md 不可变 YAML + HC-12 GovernanceGate 零容忍门控 + intent drift + policy-compliant harm 检测 | 2026-05-05 | Council (chain-ml/council, 2026-04) + Microsoft AGT ADR 0006 (2026-04) + HC-12 + Cloud Security Alliance 2026 (53% 越权) |
| D-025-29 | Agent 免疫系统——三层免疫 (innate 285 模式 + adaptive Critic + memory 哈希) + 5 态隔离检疫 (ACTIVE/SUSPECTED/QUARANTINED/CLEARED/TERMINATED) + 攻击链因果图 + 工具调用策略治理 | 2026-05-05 | ClawGuard (npm, 2026-05 — 285+ 安全模式 9 类别) + Agent-Based IDS pattern |
| D-025-30 | 选择性遗忘与被遗忘权——FSFM 四类遗忘 (passive/active/safety/reinforcement) + Cascading Forget + Two-Pass Deletion + GDPR/EU AI Act 合规 | 2026-05-05 | FSFM (arXiv:2604.20300, 2026-04) + EU AI Act 2026 (7% 营收罚款) + SISA/Gradient Scrubbing |
| D-025-31 | 碳排放追踪与碳感知路由——CodeCarbon 集成 + per-task/per-agent/per-chain CO2e + 碳感知调度预留 | 2026-05-05 | CodeCarbon + Graviton5 (AWS, -30% 碳足迹) + Green AI Systematic Review |
| D-025-32 | 空转综合征检测——PollingStorm/analysis_paralysis/meaningless_optimization 三子类型 + 四级 severity escalation + 跨 IDE 仪表盘 | 2026-05-05 | OpenClaw 真实事故 (1,535 次/$150/3GB crash) + agent-loop-detector + Agent Idle Monitor (npm) |
| D-025-33 | Agent 知识蒸馏——trajectory replay + MCP Box 零训练传递 + model-level distillation 预留 (Phase 3 条件满足后) | 2026-05-05 | KD-MARL (IJCNN 2026, -28.6× FLOPs) + AgentDistill (MCP Box) + AgentArk (CMU/Amazon/UBC) |
| D-025-34 | 硬件感知路由——GPU 利用率/显存/功耗信号集成到异质模型路由决策 (self-hosted LLM 场景预留) | 2026-05-05 | HW-Router (UCF, 3.4-3.9× 低延迟, 46-48pp SLO) + Disaggregated LLM Inference |
| D-025-35 | 多协议网关系——IBM ACP 联邦编排协议集成 + A2A/MCP/ACP/ANP 四协议适配器 + LLM-driven translation engine + mapping template cache (-90% LLM) | 2026-05-05 | IBM ACP (2026-02) + AgentGateway (LF, 2026-04) + agentlink RFC (2026-04) + OpenGateway (IETF 125) |
| D-025-36 | Agent 互联总线——AGNTCY-风格四层栈 (discovery/identity/messaging/observability) + Agent Card inputSchema/outputSchema 扩展 + 授权蠕变检测 | 2026-05-05 | AGNTCY (Cisco Outshift, 2025-06) + A2A v1.0 生产实战反馈 (2026-02) |
| D-025-37 | 因果溯源引擎——CTEGs 因果事件图模型 + caused_by/tool_used edges + temporal monotonicity + Merkle tree commit 防篡改 | 2026-05-05 | CTEGs (arXiv:2604.17557, 2026-04) + DebugABot (2026-04) |
| D-025-38 | 失败归因引擎——17x Error Trap 五类跨 Agent 失败模式 (Telephone Game/Confidence Cascade/Ghost Handoff/Tools Gone Wild/Conga Line) + 三问归因法 (origin/propagation/systemic) + BlameReport | 2026-05-05 | 17x Error Trap (AgentCenter, 2026-03) + Sentry Multi-Agent (2026-04) + Traceability paper (Oakland, 2025-10) |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.10.0 | **第八轮补齐——多协议网关+互联总线+失败归因+因果溯源**：+D-025-35~38（4 项核心决策）。新增 §2.35-§2.36（多协议网关与互联总线：业界 A2A/MCP/ACP/ANP 四协议共识 (HTTP:WebSocket:gRPC:TCP 类比) + ProtocolGateway 四协议适配器 + LLM-driven semantic translation engine + mapping template cache (-90% LLM) + AGNTCY 四层互联总线 (discovery/identity/messaging/observability) + Agent Card inputSchema/outputSchema 扩展 (A2A v1.0 生产实战反馈标准化) + 授权蠕变检测 (Authorization creep risk) + 协议版本协商 (Google A2A Discussion #680)；Agent 失败归因与因果溯源：17x Error Trap 五类跨 Agent 失败模式 (Telephone Game 信息退化 / Confidence Cascade 高置信错误放大 / Ghost Handoff 静默丢失 / Tools Gone Wild 低质输入污染 / Conga Line 累积噪声淹没) + CTEGs 因果事件图模型 (caused_by/tool_used edges + temporal monotonicity + Merkle tree commit) + 三问归因法 (origin Q1: BFS 上游溯源→首个偏差节点 / propagation Q2: 下游修复机会却错过→missed_repair / systemic Q3: 频次统计→systemic_score) + DebugABot BlameReport + W3C PROV + Sentry 生产级 Agent间空间调试 + Panaversity Spreadsheet 归因表格法。对标从 55+ 扩展到 63+ 个 (IBM ACP / AgentGateway / agentlink / OpenGateway / AGNTCY / CTEGs / DebugABot / 17x Error Trap / Traceability paper / Sentry Multi-Agent / Panaversity AgentFactory 等）。盲点 142→150 条（第八轮 8 条新增）。文件组成 54→57（+3 个 v0.10.0 专属文件: a2a_protocol_gateway.py / a2a_causal_trace.py / a2a_blame_attribution.py）。施工 Phase 30→33（新增多协议网关/失败归因相关阶段）。可观测性从"时序追踪"升级为"可归因"——因果图模型补齐三问归因。架构保持八层十二协议（新增内容为互联总线的横切基础设施 + 可观测性的深度升级）。 |
| 2026-05-05 | 0.9.0 | **第七轮补齐——宪法治理+免疫系统+选择性遗忘+碳排放+空转检测+知识蒸馏+硬件感知路由**：+D-025-28~34（7 项核心决策）。新增 §2.31-§2.34（宪法治理与 Critic-with-veto：Agent 议会三方 (Critic/Coordinator/Owner) + CONSTITUTION.md 不可变 YAML + HC-12 GovernanceGate 零容忍门控 (Constraint-as-Code) + intent drift 轨迹级检测 (cosine similarity<0.3→CRITIC_REVIEW) + Cross-Policy Impact Graph 政策合规伤害检测；Agent 免疫系统：三层免疫 (innate 285 模式 + adaptive Critic + memory 哈希) + 5 态隔离检疫 (ACTIVE/SUSPECTED/QUARANTINED/CLEARED/TERMINATED) + 攻击链因果图 (CONFIG_MOD→CRED_READ→NETWORK_SEND 等危险模式) + 工具调用运行时策略治理；选择性遗忘与被遗忘权：FSFM 四类遗忘 (passive_decay/active_deletion/safety_triggered/adaptive_reinforcement) + Cascading Forget Notification 跨 Agent 遗忘一致性 + Two-Pass Deletion (PII 删除 vs 知识保留) + EU AI Act 2026 合规 (7% 营收罚款)；运维与可持续性全景：碳排放追踪 (CodeCarbon 集成 + per-task/per-agent/per-chain CO2e) + 空转综合征检测 (PollingStorm/analysis_paralysis/meaningless_optimization 三子类型 + 四级 severity escalation — OpenClaw 真实事故 1,535 次/$150/3GB 崩溃) + Agent 知识蒸馏 (trajectory replay + MCP Box 零训练传递 + KD-MARL -28.6× FLOPs) + 硬件感知路由 (GPU 信号驱动模型选择, HW-Router 3.4-3.9× 低延迟) + 跨 IDE Agent 状态仪表盘。对标从 45+ 扩展到 55+ 个 (Council / ClawGuard / FSFM / HW-Router / KD-MARL / AgentDistill / AgentArk / CodeCarbon / agent-loop-detector / EU AI Act 2026 / HC-12 等）。盲点 123→142 条（第七轮 19 条新增）。文件组成 48→54（+6 个 v0.9.0 专属文件）。施工 Phase 28→35（新增宪法治理/免疫系统/遗忘引擎/空转检测/碳排放/知识蒸馏/硬件路由相关阶段）。经济护栏扩展含碳排放维度 + 空转综合征隐性成本。架构从八层十二协议不变（新增为横切关注点的深度加固）。 |
| 2026-05-05 | 0.8.0 | **第六轮终极补齐——A2A 协议层安全+协商帧+形式化验证+潜空间通信+向量信誉+上下文腐烂+同意编排+Vibe Coding 深度优化**：+D-025-20~27（8 项核心决策）。新增 §2.23-§2.30（A2A 协议层安全攻击面防护：Agent Card 供应链完整性 + Task 流防操纵 + Artifact 投毒门禁 + Agent 间 DoS 限流，对标 A2ASECBENCH (ICLR 2026)；结构化协商帧协议 ANP 1.0：Negotiation Frame 取代 YAML 聊天 + 歧义税 40%→<5% + ZK 身份证明 + 委托链权威性缩减；协议形式化验证 TLA+/Coq：7 属性 (P1-P7) 模型检查 + 时间感知准入控制 BAR 检测；潜空间 Agent 间通信：三梯级混合通信 (YAML+ANP Frame+Latent Embedding) + Interlat 24× 加速；多维向量信誉 TrustFlow：5 维信誉向量 + 收缩映射 + 抗女巫攻击；上下文腐烂防护：三机制检测 + 主动压缩 + 三层上下文架构 (Hot/Domain/Cold)；用户同意编排：4 状态同意机 + Ephemeral Scoped Token + 直接数据通道；Vibe Coding 深度优化 2026 版：No-AI Time 全局暂停 + Agent 休眠/唤醒 (WAL, -33% Token) + 月度红蓝对抗 + BridgeMind 三阶段扩展路径）。对标从 35+ 扩展到 45+ 个（A2ASECBENCH / ANP 1.0 / SentinelAgent / ACP v1.27 / μACP / nForma / TrustFlow / LR2 / Interlat / ACON / LumiMAS / MAStitch / BridgeBench 等）。盲点 96→123 条（第六轮 27 条新增）。文件组成 35→48（+13 个 v0.8.0 专属文件）。施工 Phase 22→28（新增协议安全/协商帧/TLA+/向量信誉/上下文腐烂/同意编排相关阶段）。独立验证从 6 核文件扩展到含 §2.25 TLA+ 形式化验证加持。架构从七层十一协议升级为八层十二协议蓝图。经济护栏扩展含上下文腐烂防护 + 用户同意编排 + 红蓝对抗。 |
| 2026-05-05 | 0.7.0 | **第五轮大规模补齐——辩论/审议+经济资源分配+异质模型路由+工作窃取与负载均衡**：+D-025-16~19（4 项核心决策）。新增 §2.19-§2.22（辩论与审议协议：4 阶段结构化辩论 (Opening/Rebuttal/Synthesis/Verdict) + Anti-Conformity + AAD/CI 评分；Agent 经济与资源分配：预算池分配 + ROI 追踪 + 跨 IDE 花费聚合，对标 x402/AEP；异质模型动态路由：角色×难度×负载三维决策 + Confidence-Aware 降级，对标 OI-MAS/Chimera/GraphPlanner；工作窃取与负载均衡：Task Affinity + Work Stealing 3 策略 + Watchdog + Shared Memory File 状态机）。Vibe Coding 优化从 6 项→9 项。PROMPT_CACHING 和 LAZY_CONTEXT_LOADING 进入 Phase 经济护栏。对标从 30+ 扩展到 35+ 个。架构从五层八协议升级为七层十一协议蓝图。 |
| 2026-05-05 | 0.6.0 | **第四轮补齐——多 Agent 共识/涌现检测/事务回滚**：+D-025-13~15（3 项核心决策）。新增 §2.16-§2.18（Multi-Agent 共识与协商层：6 状态协商会话机 + 投票/多数决 + 合谋检测 + 4 级协商降级；涌现行为与异常检测：\"Agents of Chaos\" 11 失败模式全覆盖 + 5 类异常分类学 + Isolation Forest/Autoencoder 异常检测管道 + Cross-Agent Semantic Flow；分布式事务与 Saga 回滚：LT/CT 配对注册 + 分布式检查点 + 幂等性门禁 + 1人+AI 简化策略）。对标从 20+ 扩展到 30+ 个（Google A2A v1.0 / Microsoft AutoGen 2.0→MAF / OpenAI Agents SDK / LangGraph v1.0 / CrewAI v1.10.1 / Concordia Protocol / \"Agents of Chaos\" / MAScope / SagaLLM 等）。盲点 71→96 条（第五轮 25 条新增）。文件组成 25→35。施工 Phase 16→22（新增共识/涌现/ML/Saga 相关阶段 + 独立验证从 4 核→6 核文件）。触发条件监控增加 metric_5（False Task Completion）和 metric_6（涌现行为信号）。经济护栏扩展含 Prompt Caching + Lazy Context Loading + Shared Memory File。架构从三层五协议升级为五层八协议蓝图。 |
| 2026-05-05 | 0.5.0 | **第三轮大规模补齐 71 条盲点**：+D-025-01~12（12 项核心决策）。重构为三层五协议架构（发现层+通信层+协调仲裁层+横切关注点）。新增 §2.2-§2.15（Agent Card 模型 / Task 状态机 / Message-Part 系统 / Supervisor-Coordinator / Living Spec 同步 / 文本-语义双层冲突检测 / 三级仲裁 / 死锁-活锁防护 / OWASP ASI07 通信安全 / 上下文管理 / 经济护栏 / 级联故障防护 / 可观测性-分布式追踪 / 施工自指悖论独立验证 / Vibe Coding 专属优化）。文件组成 4→25。施工 Phase 3→16（含独立验证阶段）。对标从 2 个扩展到 20+ 个（Google A2A v0.2.6 / Anthropic Agent Teams / MIT CORDIAL / OWASP Agentic Top 10 / Palo Alto Unit 42 / DPBench / Coware / Augment Code / MMA2A 等）。盲点表 4 轮 71 条完整。消息格式锁定为 YAML+人读机读。触发条件监控增加 metric_4（IDE 并发会话数）。 |
| 2026-05-05 | 0.2.0 | 补充触发条件监控 + 当前场景分析 + Hold 状态确认 |
| 2026-05-05 | 0.1.0 | 初始创建——Hold 状态 + 预研架构 + 触发条件 |


---

## 施工落盘确认（2026-05-07 审计）
| 维度 | 状态 |
|------|------|
| construction_progress | phase_1_partial（Phase 1 Skeleton 完成，Phase 2 E2E 骨架就绪但功能未实现，全模块 Hold 状态） |
| 源码路径 | `src/zephyr/a2a/ (骨架) + governance/a2a/ (核心逻辑)` |
| 源码文件数 | 4 个 .py/.yaml |
| 测试路径 | `tests/integration/l01_infrastructure/a2a_protocol/` |
| 关键入口 | `governance/a2a/protocol.py + auditor.py` |
