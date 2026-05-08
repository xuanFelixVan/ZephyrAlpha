---
module_id: "MOD-INF-024"
title: "Token/Cost/Time 三维预算强制执行蓝图 — 七级预算 + 全生命周期 + 信任根 + 抗对抗"
doc_type: blueprint
status: Draft
version: "0.7.0"
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
summary: "ZephyrAlpha Token/Cost/Time 三维预算强制执行蓝图 v0.7.0——终极取证补丁。前6轮补齐68项功能性盲点，本轮补充3个结构面缺陷：①信任根——AI构建的Budget Enforcer谁来审计？引入Runtime Trust Rings（Ring 0-3）+ Tamper-Evident Audit Trail（append-only hash chain）+ Budget Policy Signing；②抗对抗——前6轮假设agents是合作的，Forcepoint X-Labs 2026披露10种IPI攻击载荷可在<300ms绕过guardrails。引入IPI-Aware Budget Defense + Cold Start Anti-Abuse + Adversarial Testing Mandate；③故障模式——Budget Enforcer崩溃时fail-open还是fail-closed？引入Formal Fail-Mode Specification + Bootstrapping Calibration Phase（Day 0→30渐进收紧）。对标补充：Forcepoint X-Labs IPI十大攻击载荷 (2026.4) + Oktsec Kill Chain (2026.3) + Okta Agent Bypass研究 (2026.5) + Microsoft Agent Governance Toolkit Runtime Rings + Gravitee AI Agent Security 2026。v0.3.0 20+v0.4.0 23+v0.5.0 13+v0.6.0 12+v0.7.0 10=78项盲点全量补齐。这并不是增加更多功能——而是补上'一个AI构建的系统如何可信地约束AI'这个根本性问题。"
tags: [budget, token, cost, time, enforcement, degradation, infrastructure, pre-flight, in-flight, self-budget, model-router, cache, burn-rate, roi, chargeback, loop-detection, pricing-sync, stream-abort, quality-gate, env-profile, agent-sub-pool, policy-sandbox, waste-detection, batch-routing, model-discovery, timeout-guard, instruction-bloat, history-tax, provider-tier, cost-spiral, cross-provider, narrow-reroute, spiral-ews, poison-cascade, parent-child-attribution, workflow-budget, resume-cost, think-time, guard-efficiency, trust-ring, tamper-evident, fail-mode, bootstrapping, ipi-defense, anti-abuse, adversarial-testing, supply-chain-isolation]
priority: P2
depends_on:
  - {target: "MOD-INF-008", at: "§2", why: "Context Engine——token 预算分配的消费者 + 上下文压缩 + 历史税检测联动"}
  - {target: "MOD-INF-020", at: "§2", why: "Audit Trail——预算超限事件写入审计 + v0.7.0 Tamper-Evident hash chain"}
  - {target: "MOD-INF-022", at: "§2", why: "Escalation——预算超限触发升级"}
  - {target: "MOD-INF-001", at: "§2", why: "Capacity Assurance——Token Budget 多级体系 + Kill Switch + Fail-Mode 联动"}
  - {target: "MOD-INF-006", at: "§2", why: "Task System——任务预算字段 + 状态机预算联动"}
  - {target: "MOD-INF-023", at: "§2", why: "Drift Detector——漂移预算信号 + 配置漂移对预算的影响"}
  - {target: "MOD-INF-014", at: "§2", why: "LLM Security Gateway——IPI检测 + 策略文件签名验证 + Trust Ring 隔离"}
---

## DOM-GOV-001 集成契约锚点

> 权威定义见 [`../../_domain-governance/blueprint.md`](../../_domain-governance/blueprint.md) §3。

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-006 | 产出方（预算事件 → Escalation） | MOD-INF-022 |

# Token/Cost/Time 三维预算强制执行蓝图 — 七级预算 + 全生命周期 + 信任根

> **module_id**: MOD-INF-024 | **version**: 0.7.0 | **status**: draft | **layer**: cross_layer

> **对标**：Forcepoint X-Labs IPI十大攻击载荷 (2026.4) + Oktsec 7-Stage Kill Chain (2026.3) + Okta Agent Guardrail Bypass (2026.5) + Microsoft Agent Governance Toolkit Runtime Rings + SUPERVISORAGENT (ICLR 2026) + TechAhead 3层Guardrails + Vibe Coding 2026成本现实 + Gravitee AI Agent Security 2026 + Oracle Runtime Budget Guardrails + AgentGuard + Stanford Token Economics + TokenFence + Anthropic 4-Tier + Boris Cherny Claude成本解剖。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-024 |
| 代码落位 | `src/zephyr/budget_enforcer/` |
| 运行时平面 | Hot memory（Pre-flight Gate + In-flight Stream Abort Guard + 调用后 Runtime Enforcer——覆盖调用前→调用中→调用后全生命周期） |
| 核心职责 | 强制执行 Token/Cost 预算——超预算自动降级，零人工介入；事后成本归因 + ROI 分析 |

### 1.2 核心职能（一句话）

**Budget Enforcer 是系统的财务总监 + 采购经理**——AI 不能无限消耗 token，超预算自动降级；同时在多个模型和供应商之间智能路由，以最低成本完成任务。全程自动，不需要 Owner 介入。

### 1.3 v0.7.0 升级摘要（终极取证补丁）

> 前6轮共补齐68项功能性盲点。v0.7.0 **不增加新功能**——从一个外部取证专家的视角，回答一个根本问题：**"一个100% AI构建的系统，凭什么相信它能可信地约束AI？"** 发现3个结构面缺陷，补齐10项。

| 版本 | 信任模型 | 抗对抗 | 故障模式 | 审计完整性 |
|------|------|:---:|------|:---:|
| v0.6.0 | 无条件信任Budget Enforcer | ❌ 假设agents合作 | ❌ 未定义 | 明文JSONL可篡改 |
| **v0.7.0** | **Runtime Trust Rings(0-3)** | **IPI Defense + Cold Start Anti-Abuse + Adversarial Test** | **Formal Fail-Open/Closed** | **Tamper-Evident hash chain** |

---

## 2. 核心架构

### 2.1 五级预算体系（Token + Cost + Time 三维）

> **决策 D-024-02（v0.5.0 修订）**：从 Token/Cost 双维升级为 Token/Cost/Time 三维。Stanford Token Economics 论文 (2026.4) 验证——wall-clock 时间和 token 消耗仅呈弱相关，必须独立监控。Oracle Runtime Budget Guardrails 明确提出 "given elapsed time, observed cost, and remaining work estimate, decide to continue/narrow/reroute/escalate/stop"。

```yaml
budget_levels:
  # ── Level 5: 最粗粒度 ──
  global_level:
    description: "全局周预算（solo maintainer 场景 weekly 粒度比 daily 更合理）"
    soft_limit: 500000           # tokens/week，约 $3-5/week（按 GPT-4o 价格）
    hard_limit: 750000
    action_on_soft_exceed: "全局通知 + 建议暂停非关键任务"
    action_on_hard_exceed: "全局只读模式"
    reset: "每周一 00:00 UTC"
    borrow_pool: true            # 允许跨周借用（最多预支下周 20%）

  # ── Level 4 ──
  session_level:
    description: "单次会话预算（一次施工对话的累计消耗）"
    soft_limit: 8000             # tokens，到达触发通知
    hard_limit: 12000            # tokens，到达触发降级
    action_on_soft_exceed: "WARNING 日志 + 建议 /compact"
    action_on_hard_exceed: "降级到最小上下文"
    reset: "会话结束"

  # ── Level 3 ──
  task_level:
    description: "单任务预算（一个蓝图层/一个Phase的施工）"
    soft_limit: 4000
    hard_limit: 6000
    action_on_soft_exceed: "暂停任务 + 建议拆分"
    action_on_hard_exceed: "暂停任务 + 委托给新会话"
    pool_share: true             # 同一 Session 内的 Task 之间弹性共享预算

  # ── Level 2: token spiral 锚点 ──
  turn_level:
    description: "单轮 ReAct 迭代预算（一次 think→act→observe 循环）"
    soft_limit: 1500
    hard_limit: 2500
    action_on_soft_exceed: "检查是否陷入循环 + 建议简化工具调用"
    action_on_hard_exceed: "强制终止本轮 + 返回部分结果 + 循环指纹记录"

  # ── Level 1: 最细粒度 ──
  request_level:
    description: "单次 API 调用预算"
    input_limit: 32000           # max input tokens per request
    output_limit: 4096           # max output tokens per request
    reasoning_limit: 8000        # reasoning tokens 专项预算（reasoning models 的 thinking 不可见但计费）
    tool_calls_limit: 10         # max tool calls per request
    action_on_exceed: "截断输出 + 建议拆分请求"
```

```yaml
# ── v0.5.0 新增：Time Budget 三维预算体系 ──
time_budget:
  description: "Wall-clock 时间预算——token 消耗少但耗时极长的任务（死循环/慢模型/网络抖动）是三维预算必须独立追踪的原因"
  # Stanford 论文数据：相同任务在不同模型间执行时间差异可达 10x，与 token 消耗无关
  dimensions:
    request_timeout: 120           # 单次 API 调用 2 分钟超时
    turn_timeout: 300              # 单轮 ReAct 循环 5 分钟超时
    task_timeout: 3600             # 单个施工任务 1 小时超时
    session_timeout: 28800         # 单个 Session 8 小时超时
  enforcement: "Timeout Guard（§2.20）——硬超时即刻 abort + 保存 partial state + Action History checkpoint"
  visualization: "终端显示 '⏱ 任务: 23min/60min (38%) | 💰 Token: 42K/100K (42%)'"
```

### 2.2 Pre-flight Gate（事前拦截门）

> **决策 D-024-03**：专业机构要求 pre-request blocking——在 tokens 被实际消耗之前就拦截。Pre-flight Gate 是 v0.3.0 新增的核心组件，位于每次 API 调用的咽喉位置。

```yaml
pre_flight_gate:
  position: "每次 API 调用前，在任何 token 消耗之前执行"
  checks:
    - check_id: "global_budget_check"
      rule: "本周 global soft_limit 剩余 < 预估消耗 × 1.2"
      on_fail: "DENY → 建议推迟到下周"
      exception: "Owner 临时提额令可覆盖"

    - check_id: "session_budget_check"
      rule: "会话 hard_limit 剩余 < 预估消耗"
      on_fail: "DEGRADE → 强制 /compact 后再试"

    - check_id: "task_budget_check"
      rule: "任务 hard_limit 剩余 < 预估消耗"
      on_fail: "DEGRADE → 任务拆分 + 委托子任务到新对话"

    - check_id: "turn_budget_check"
      rule: "本轮 soft_limit 剩余 < 预估消耗"
      on_fail: "WARN → 检查循环指纹 + 建议跳过冗余工具调用"

    - check_id: "request_size_check"
      rule: "预估 input_tokens > request_level.input_limit"
      on_fail: "DENY → 请求太大，建议拆分"

    - check_id: "cost_threshold_check"
      rule: "预估单次调用成本 > $0.50"
      on_fail: "DEGRADE → 自动切换到 Tier-1 模型"

  estimator: "TikToken-based + model-specific tokenizer，误差 < 10%"
  decision_outcomes: ["ALLOW", "WARN", "DEGRADE", "DENY", "BORROW"]

  # Borrow 机制：从 Budget Pool 临时借用
  borrow:
    enabled: true
    max_borrow_ratio: 0.20       # 最多借 20% 其他任务预算
    payback: "同 Session 下次任务少分 30% 直到还清"
```

### 2.3 模型路由升级（Model Router）

> **决策 D-024-04（v0.4.0 修订）**：模型路由方向反转——从"默认用高→预算紧张降级到低"改为"默认最低→质量不达标才升级"。专业机构实践（Cost Engineering for Agents, 2025）+ Vibe Coding 社区模型组合拳（需求理解用弱模型→代码生成用强模型→Lint 用免费模型）降本 80%+。

```yaml
model_tier_routing:
  description: "按任务复杂度自动选择最优成本模型——默认最低 Tier，质量不达标才升级"
  strategy: "cheapest_first_escalate_on_quality_fail"

  # ── 模型升级路径（v0.4.0 反转）──
  escalation_chain:
    - from: "tier_0_free"
      to: "tier_1_cheap"
      trigger: "tier_0 返回质量不达标（output_validator 评分 < 阈值）OR 任务复杂度 > tier_0.max_complexity"
      max_escalation_cost: 0.01      # 升级一次的成本上限

    - from: "tier_1_cheap"
      to: "tier_2_standard"
      trigger: "tier_1 返回质量不达标 OR 任务需要深度推理（架构设计/多文件重构）"
      max_escalation_cost: 0.05

    - from: "tier_2_standard"
      to: "tier_3_premium"
      trigger: "tier_2 返回质量不达标 AND 任务为终审裁决/安全审计"
      requires_owner_approval: true    # Tier-3 使用需要 Owner 信号

  # ── 预算紧张时的降级覆盖（保留旧路径作为反向压降）──
  degradation_override:
    - from: "tier_3_premium"
      to: "tier_2_standard"
      trigger: "global_budget_used > 60%"

    - from: "tier_2_standard"
      to: "tier_1_cheap"
      trigger: "global_budget_used > 80%"

    - from: "tier_1_cheap"
      to: "tier_0_free"
      trigger: "global_budget_used > 95%"

  # ── 分析：何时升级 vs 降级 ──
  decision_matrix:
    normal_state: "escalation_chain 生效——默认 tier_0，质量驱动升级"
    budget_tight: "degradation_override 优先——预算紧张时压降覆盖升级"

  # ── 批次路由（v0.4.0 新增）──
  batch_routing:
    description: "非实时任务走 Batch API（Anthropic/OpenAI Batch API 50% 折扣）"
    eligible_tasks:
      - "周报生成"
      - "成本归因分析"
      - "批量 Lint 修复"
      - "文档批量格式化"
      - "ROI 计算"
    max_latency: "24h"            # Batch 任务最大延迟容忍
    cost_saving: "50%"            # Batch API 折扣
    integration: "任务系统（MOD-MASTER-001）标记 task.urgency=low → 自动走 batch"

  # ── 厂商风险对冲 ──
  vendor_fallback:
    anthropic_unavailable: "→ OpenAI equivalent tier"
    openai_unavailable: "→ Google equivalent tier"
    google_unavailable: "→ DeepSeek equivalent tier"
    all_unavailable: "→ local free model (Ollama)"

  # ── v0.5.0 新增：多Provider同Tier内least-cost路由 ──
  cross_provider_least_cost:
    description: "同一 Tier 内部存在多个 Provider 的等效模型——自动选最便宜的"
    example:
      tier_2_standard:
        candidates:
          - provider: "anthropic"
            model: "claude-sonnet-4"
            cost_per_1m_input: $3.00
          - provider: "openai"
            model: "gpt-4o"
            cost_per_1m_input: $2.50
          - provider: "google"
            model: "gemini-2.0-pro"
            cost_per_1m_input: $1.25
        selection: "min(cost_per_1m_input) WHERE availability=UP AND quality_score >= 0.7"
        tie_break: "prefer provider with highest remaining rate limit capacity"
    quality_weighted: true          # 不纯按价格——质量太差的便宜模型不选
    refresh_interval: 300           # 每 5 分钟刷新一次最低价路由表

### 2.4 六级自适应降级链

> **决策 D-024-05（v0.4.0 修订）**：新增 L1.5 沉没成本干预——当 Cost-to-Completion Ratio 异常时主动建议放弃。新增预算耗尽用户沟通协议。

```yaml
degradation_strategy:
  level_0_notify:
    trigger: "session_budget_used > 50% OR burn_rate_1h > 3× normal"
    action: "INFO 日志 + 会话内显示剩余预算 + 建议 /compact 时机"
    auto: true
    visualization: "终端显示 '💰 预算: 4,200/8,000 tokens (52.5%)'"

  level_1_warning:
    trigger: "预算使用 > 70% OR 单轮 Turn soft_limit 接近"
    action: "WARNING 日志 + 通知附录建议减少上下文 + 标记当前任务为 'budget_watch'"
    auto: true

  # ── v0.4.0 新增：沉没成本干预 ──
  level_1_5_sunk_cost_warn:
    trigger: "cost_to_completion_ratio > 3× AND 任务产出 < 20%"
    action: "主动告警 '预算已消耗 80% 但产出仅 10%——建议放弃当前任务，重启更有效'"
    auto: true
    rationale: "再试一次就好了 是成本超支的核心心理陷阱——系统必须主动干预"
    cost_to_completion_ratio: "budget_consumed_ratio / output_completion_ratio"

  level_2_model_switch:
    trigger: "预算使用 > 80% OR 单次调用预估成本 > $0.50"
    action: "自动降级到 Tier-1 模型——这是成本最低且效果最好的降级手段"
    auto: true
    priority: "最高——在压缩上下文之前执行"

  level_3_compress:
    trigger: "预算使用 > 85%"
    action: "强制压缩上下文——DocCompressor aggressive 模式"
    auto: true
    integration: "Context Engine (MOD-INF-008)"

  level_4_minimal:
    trigger: "预算使用 > 95%"
    action: "最小上下文——仅保留 AGENTS.md + 当前蓝图 §3"
    auto: true

  level_5_halt:
    trigger: "预算使用 > 100%（hard_limit）"
    action: "硬停止——仅允许只读操作 + 审计告警"
    auto: true
    audit_level: "ProvenanceStandard"
    # ── v0.4.0 新增：预算耗尽用户沟通协议 ──
    user_communication:
      template: >
        ⚠️ 预算已耗尽（{level}: {used}/{limit} tokens）。
        当前任务的已完成部分已保存至 {output_path}。
        建议：1) 等待下周预算重置  2) 使用 `--override-budget` 临时提额
        诊断命令：`zephyr budget status --detail`
      fallback_action: "自动保存当前进度 + 生成 resume checkpoint"

  level_6_kill_switch:
    trigger: "单日成本 > $100 OR 连续 5 个请求被 DENY OR 检测到 runaway loop"
    action: "全局熔断——所有 AI 调用暂停，保留修复通道（允许 Owner 执行诊断命令）"
    auto: true
    integration: "Capacity Assurance Kill Switch (MOD-INF-001)"
    recovery: "熔断后 30 分钟自动尝试解除 + Owner 手动解除"

  # ── 成本感知自动回升 ──
  auto_recovery:
    enabled: true
    rules:
      - condition: "连续 3 个请求 burn_rate_10min < 1× normal AND budget_used < soft_limit × 0.6"
        action: "回升一级（L4→L3, L3→L2, L2→L1, L1.5→L1）"
        max_recovery: "L1"        # 不自动回到 L0（需要新的会话）
      - condition: "新会话开始"
        action: "完全重置到 L0"
    anti_spiral:
      max_degradation_per_minute: 1
      recovery_cooldown: 180
```

```yaml
# ── v0.5.0 新增：额外的自适应干预动作（Oracle Runtime Budget Guardrails 对标）──
adaptive_interventions:
  description: "在传统的 degrade/stop 二元模型之外，Oracle 2026 论文明确了 Narrow 和 Reroute 两种轻量干预"

  narrow_scope:
    description: "预算紧张时收窄任务范围——不是降级，而是只做最关键的 20%"
    trigger: "task_budget_used > 70% AND task_progress < 30%"
    action: "自动注入 system prompt '你的预算已消耗 70% 但产出仅 30%——请仅完成核心子任务，跳过优化/美化/文档'"
    visual: "终端显示 '🎯 范围收窄——仅完成核心逻辑，跳过: [单元测试, 文档, 格式化]'"
    reversible: true              # 预算恢复后可自动解除

  reroute_strategy:
    description: "当前策略消耗过高时切换执行路径——不是换模型，而是换方法"
    trigger: "同一 task 内 model_switch 发生 2 次以上 OR per-request cost > 3× running_average"
    action: "切换到 'pipeline 模式'（拆分成多个小请求逐段处理）而非 '一次性大请求'"
    visual: "终端显示 '🔄 策略切换——Pipeline 模式（将任务拆分为 {n} 段逐段处理）'"

  global_timeout_kill:
    description: "当 wall-clock 时间预算耗尽时触发——token 少但耗时长的任务在此被拦截"
    trigger: "task_timeout OR session_timeout reached"
    action: "IMMEDIATE_ABORT + 保存 Action History checkpoint + 写入 resume 文件"
    integration: "Timeout Guard（§2.20）——独立于 token/price 预算链的并行监控线程"
```

### 2.5 动作历史与去重（Action History with Dedup）

> **决策 D-024-06（v0.5.0 修订）**：简单指纹匹配→结构化动作历史 + 签名去重。Stanford/MIT 论文 (2026.4) 发现 50% 的高成本运行中的文件读写是重复的——不是传统意义上的"循环"（参数不同但结果等价），需要更智能的检测。TokenFence 和 AgentGuard 均采用 action-level dedup 而非 fingerprint matching。

```yaml
action_history:
  description: "记录每个 Agent Action 的签名——不是简单的 fingerprint，而是结构化的 action 语义指纹"
  storage: "环形缓冲区——保留最近 50 个 action"

  action_signature:
    fields:
      - "tool_name"
      - "tool_params_hash"           # 参数哈希
      - "tool_params_semantic_hash"  # v0.5.0 新增：语义等价参数哈希（文件名换但逻辑相同→同一签名）
      - "output_effect_hash"         # v0.5.0 新增：输出副作用哈希（读/写了哪些行/文件）
      - "timestamp"
      - "cost_incurred"

  dedup_rules:
    identical_action_3x:
      threshold: 3                   # 完全相同的 action 连续 3 次
      action: "WARN + 写入 budget_enforcer_loop_events"
      auto: true

    identical_action_5x:
      threshold: 5
      action: "BLOCK——拒绝执行 + 返回 '检测到重复动作循环: {action_signature}'"
      auto: true

    # ── v0.5.0 新增：输出无差异去重 ──
    no_effect_chain:
      description: "连续 N 个 action 对输出无任何差异——修改了文件但 diff 为空的无效操作"
      threshold: 3
      action: "WARN '检测到无效果动作链——建议跳过后续同类操作'"

    # ── v0.5.0 新增：自修复螺旋检测 ──
    self_correction_spiral:
      description: "Agent 连续修改同一段代码→新增 bug→再修改→再新增 bug——自修复成本螺旋"
      detection: "同一文件同一区域被修改 > 5 次且每次修改后 lint error_count > previous"
      threshold: 5
      action: "HALT——系统介入 '检测到自修复螺旋——建议人工介入后重新开始'"
      auto: true

    semantic_duplicate_10x:
      threshold: 10
      action: "TRIGGER_KILL_SWITCH——疑似 runaway agent"
      auto: true
      trigger_kill_switch: true

  # 指纹过期
  action_ttl: 300                     # 5 分钟窗口（仅统计窗口内 action）
```

### 2.6 语义缓存（Semantic Cache）

> **决策 D-024-07**：缓存是最便宜的性能优化。对齐 Anthropic cache-aware token management——对高频相同/相似请求自动缓存，hit 后零新增 token 消耗。

```yaml
semantic_cache:
  description: "嵌入向量相似度匹配的语义缓存——不仅缓存完全相同的请求，也缓存语义相似的请求"
  backend: "ChromaDB（复用已有向量库，零新增依赖）"
  cache_layers:

    layer_1_prompt_cache:
      description: "System prompt + 上下文哈希 → 缓存 completion"
      strategy: "exact_hash"     # 精确哈希匹配
      ttl: 3600                  # 1 小时
      encryption: "AES-256 at rest"
      hit_ratio_target: 0.40

    layer_2_tool_cache:
      description: "工具调用（API 查询/文件读取等）结果缓存"
      strategy: "param_hash"     # 参数哈希匹配
      ttl: 300                   # 5 分钟
      hit_ratio_target: 0.30

    layer_3_embedding_cache:
      description: "文档嵌入去重——两个 chunk 哈希相同则复用向量"
      strategy: "content_hash"
      ttl: 86400                 # 24 小时

  observability:
    metrics: ["cache_hit_rate", "cache_saved_tokens", "cache_saved_cost"]
    audit: "每次 cache hit 写入 audit trail——证明敏感数据在缓存中加密且按时过期"
```

### 2.7 成本归因体系（Cost Attribution）

> **决策 D-024-08（v0.4.0 修订）**：不知道钱花在哪里的 Budget Enforcer 只做了一半工作。v0.4.0 新增 Outcome 维度（成功/失败/部分分离）——失败消耗和成功消耗的 ROI 完全不同。

```yaml
cost_attribution:
  dimensions:

    entity_level:
      description: "按 Agent/模块归因"
      fields:
        - "agent_id"
        - "module_id"
        - "phase"
      query_example: "agent_id='code-generator' 本月消耗 $12.50，占总成本 65%"

    tool_level:
      description: "按工具/API 归因——含第三方 API 直接调用费用"
      fields:
        - "tool_name"
        - "tool_call_count"
        - "tool_api_cost"
        - "tool_prompt_tokens"
        - "tool_result_tokens"
        - "passthrough_cost"        # v0.4.0 新增：Web Search/Code Exec/DB Query 等服务自身的费用
      query_example: "tool_name='web_search' 调用 320 次，API 费用 $1.60 + token 费用 $8.40"

    feature_level:
      description: "按产品功能/施工活动归因"
      fields:
        - "activity_type"
        - "output_files_created"
        - "lines_of_code"
      query_example: "activity_type='debug' 占本月 45% 成本——debug 效率需优化"

    # ── v0.4.0 新增：产出结果维度 ──
    outcome_level:
      description: "按 API 调用结果分离成本——成功/失败/部分/拒止"
      fields:
        - "outcome"                  # "success" | "partial" | "failed" | "rejected"
        - "retry_count"
        - "error_category"           # "rate_limit" | "timeout" | "hallucination" | "validation_fail"
      query_example: "outcome='failed' 本月消耗 $4.20，占总成本 22%——失败重试是最大浪费源"

    # ── v0.4.0 新增：LLM-as-Judge 独立核算 ──
    judge_cost:
      description: "LLM 审查 LLM 的 Judge 模式消耗——这是二次消耗，不是直接产出"
      tracking: "独立子预算——不计入 Task 预算，走 Judge 专用预算池"
      alert: "Judge 成本 > 总成本 15% → 告警 '审查成本过高，建议简化审查逻辑'"

  showback:
    description: "每周自动生成归因摘要"
    format: "自然语言 Markdown 报告 → `docs/09_audit/cost_reports/weekly-{date}.md`"
    content:
      - "本周总消耗：X tokens / $Y"
      - "Top 3 消耗 Agent：[agent_id] $X (占比%)"
      - "Top 3 消耗工具：[tool_name] $X (占比%)"
      - "Top 3 消耗活动：[activity_type] $X (占比%)"
      - "失败消耗：$X (占比%)——含 top failure reason"
      - "本周异常：[超过预算的事件列表]"
      - "ROI 估算：[token 产出效率 vs 上周]"
      - "预测下周：[基于 4 周趋势的预测]"

  data_retention:
    description: "v0.4.0 新增——成本数据不会无限增长"
    raw_data: "30 天保留（JSONL）"
    aggregated: "12 个月保留（按周聚合 SQLite）"
    archival: "每年自动归档上一年度数据为 gzip JSON"
    cleanup: "每周日 03:00 UTC 自动执行过期策略"

  storage: "JSONL——data/audit/cost-attribution.jsonl（按天切分）"
```

### 2.8 Token ROI 模型

```yaml
token_roi:
  description: "不只算花了多少 token——算这些 token 产出了什么。Token 价值归因是 FinOps for AI 的核心。"
  outcome_metrics:
    - metric: "lines_of_code_per_1k_tokens"
      description: "每 1000 token 产出的代码行数"
      baseline_week_1: null     # Week 1 建立基线

    - metric: "files_completed_per_1k_tokens"
      description: "每 1000 token 完成的文件数"

    - metric: "blueprint_sections_per_1k_tokens"
      description: "每 1000 token 产出的蓝图章节数"

    - metric: "debug_rounds_per_task"
      description: "每任务的 debug 轮次——越高说明首次生成质量越差"

  trend_alert:
    roi_drop_30_percent: "ROI 下降 30% 以上 → 告警 Owner '施工效率下降，建议检查 Prompt 质量'"

  integration: "与 Session Log（docs/09_audit/session_logs/）联动，自动计算"
```

### 2.9 Burn Rate 多窗口监控

> **决策 D-024-09（v0.4.0 修订）**：Google SRE 标准——不是"用了多少"，而是"在以多快的速度烧预算"。v0.4.0 新增 Distribution Shift 检测——结构异常往往先于总量异常出现。

```yaml
burn_rate_monitor:
  windows:
    window_10min:
      description: "10 分钟消耗速率"
      critical_threshold: "> 10× normal burn rate"
      action: "立即触发 L3_compress"
      purpose: "捕捉 runaway agent"

    window_1h:
      description: "1 小时消耗速率"
      critical_threshold: "> 5× normal burn rate"
      action: "触发 L2_model_switch"
      purpose: "捕捉短期异常"

    window_6h:
      description: "6 小时消耗速率"
      critical_threshold: "> 3× normal burn rate"
      action: "通知 Owner + 触发 L1_warning"
      purpose: "捕捉施工效率下降"

    window_24h:
      description: "24 小时消耗趋势"
      critical_threshold: "> 2× normal burn rate"
      action: "每日摘要中包含预警"
      purpose: "捕捉渐进式成本膨胀"

  # normal burn rate = 过去 7 天的同时段平均消耗速率
  baseline: "7d_moving_average"
  alert_cooldown: 300            # 同一 burn rate 告警 5 分钟内不重复

  # ── v0.4.0 新增：使用结构分布偏移检测 ──
  distribution_shift:
    description: "检测 token 消耗结构的异常变化——结构异常往往比总量异常更早出现"
    dimensions:
      - "by_model"              # 某模型消耗比例突变
      - "by_tool"               # 某工具消耗比例突变
      - "by_agent"              # 某 Agent 消耗比例突变
      - "by_outcome"            # 失败消耗比例突变
    detection: "Jensen-Shannon divergence vs 7 天滑动窗口基线"
    alert_threshold: "JS divergence > 0.3"
    action: "INFO 日志 '检测到消耗结构偏移——[dimension] 异常增长，可能原因：[suggestion]'"

  # ── v0.4.0 新增：被限流的浪费追踪 ──
  rate_limit_impact:
    description: "被厂商限流后的重试消耗是纯浪费——需要独立追踪"
    tracking:
      - "rate_limit_hit_count"
      - "retry_tokens_wasted"
      - "retry_cost_wasted"
    alert: "限流浪费 > $1.00/天 → 建议调整并发数或升级 Tier"

  # ── v0.5.0 新增：Provider Tier 感知 ──
  provider_tier_awareness:
    description: "Anthropic 4-Tier 限额体系——每 Tier 有不同的 RPM/TPM 上限，超限后请求被拒"
    tiers:
      tier_1: { rpm: 50, tpm: 100000 }        # 刚注册
      tier_2: { rpm: 500, tpm: 500000 }        # 消费 > $50
      tier_3: { rpm: 2000, tpm: 2000000 }      # 消费 > $200
      tier_4: { rpm: 5000, tpm: 5000000 }      # 消费 > $1000
    tracking: "实时追踪当前 Tier 的剩余 RPM/TPM——在路由决策中纳入容量约束"
    alert: "RPM 剩余 < 20% → 自动切换到备用 Provider 的同 Tier 模型"
```

### 2.10 Budget Pool 弹性共享 + Agent 子池隔离

```yaml
budget_pool:
  description: "Session 内多个 Task 之间弹性共享预算——不是固定切分"
  strategy: "adaptive_weighted"

  initial_allocation:
    method: "complexity_weighted"
    reserve_buffer: 0.15        # 保留 15% 作为合成缓冲区（解决 multi-agent synthesis 的额外消耗）

  dynamic_rebalance:
    trigger: "任一 Task 消耗 > 80% 且存在其他 Task < 40%"
    action: "从低消耗 Task 转移 20% 预算到高消耗 Task"
    max_transfer_per_hour: 2    # 防止频繁震荡

  cross_session_borrow:
    enabled: false               # Solo maintainer 下跨会话借用无意义，Session 粒度已足够

  # ── v0.5.0 新增：跨 Session 预算储蓄 ──
  cross_session_savings:
    description: "轻量 Session 未用完的预算自动储蓄到下周——不是借用，是储蓄"
    bank_rate: 0.30              # 节约的 30% 进入储蓄池（其余回归全局 pool）
    max_savings: "20% * global_weekly_budget"  # 储蓄池上限
    usage: "储蓄池仅在全局预算紧张时（global_used > 80%）自动释放"
    visual: "终端显示 '🏦 储蓄池: 12.5K tokens (可救急)'"

  # ── v0.4.0 新增：Agent 级子池隔离 ──
  per_agent_sub_pool:
    description: "多 Agent 场景下，每个 Agent（或 Agent 类别）有独立子池——防止一个失控 Agent 烧掉所有预算"
    isolation_level: "soft"      # soft=子池用尽可从全局池借用, hard=子池用尽即 halt
    default_sub_pool_ratio: 0.25 # 默认每个 Agent 最多占全局预算的 25%
    categories:
      - name: "code_generation"
        max_share: 0.50          # 代码生成 Agent（群）最多占 50%
        agents: ["code-generator", "refactoring-agent"]
      - name: "analysis"
        max_share: 0.30          # 分析类 Agent 最多占 30%
        agents: ["blueprint-analyzer", "roi-calculator", "audit-agent"]
      - name: "operations"
        max_share: 0.20          # 运维类 Agent 最多占 20%
        agents: ["linter", "formatter", "test-runner"]
    spillover:
      enabled: true               # 子池外溢允许从全局池借用
      limit: "2× sub_pool"       # 最多借 2 倍子池额度
    alert: "任一 Agent 消耗 > 子池 80% → L1_warning"

### 2.11 厂商价格自动同步 + 新模型发现

```yaml
pricing_sync:
  description: "模型价格是动态变化的——不能硬编码。从 LiteLLM 每日拉取最新定价。"
  source: "LiteLLM model_prices_and_context_window.json"
  sync_frequency: "daily at 02:00 UTC"
  fallback: "使用本地缓存的上一次成功同步数据"
  alert: "连续 3 天同步失败 → 通知 Owner"

  local_cache: ".audit_cache/model_pricing_cache.json"
  ttl: 86400

  # ── v0.4.0 新增：新模型自动发现 ──
  new_model_discovery:
    description: "检测到 LiteLLM registry 中出现新模型——自动评估是否适合现有 Tier 体系"
    trigger: "sync 检测到本地缓存中不存在的 model_id"
    evaluation:
      - step: "拉取模型能力画像（context_window, max_output, capabilities）"
      - step: "计算预估成本排名（vs 现有同 Tier 模型）"
      - step: "生成 '新模型评估建议' 写入本周摘要"
    action: "INFO '发现新模型 {model_id}: 价格 {price}/MTok, 同样能力的模型比现有便宜 {saving}%'"
    auto_adopt: false            # 不自动替换——由 Owner 审阅后手动更新 budget_policy.yaml

  # ── v0.4.0 新增：Provider Token 计数差异归一化 ──
  token_normalization:
    description: "不同厂商 token 定义不同——不做归一化无法真正 apples-to-apples 成本对比"
    base_tokenizer: "cl100k_base"        # 以 OpenAI 分词为基准
    normalization_factors:
      anthropic_custom: 1.05             # Anthropic token ≈ 1.05× OpenAI token
      google_gemini: 0.92                # Google token ≈ 0.92× OpenAI token
      deepseek: 0.98                     # DeepSeek token ≈ 0.98× OpenAI token
    application: "所有跨模型成本对比前先归一化到 cl100k_base 等效 token 数"

  # ── v0.5.0 新增：长上下文隐藏定价感知 ──
  long_context_pricing:
    description: "部分 Provider 在超过某个 context 阈值后触发更高定价——不被同步的静默成本杀手"
    known_traps:
      anthropic_1m:
        threshold: 200000               # 超过 200K input 后价格翻倍（2026 早期定价策略）
        multiplier: "1.5× - 2×"         # 不同模型的溢价因子不同
        detection: "Pre-flight 时检查 estimated_input_tokens——超过阈值则计入溢价成本预估"
      openai_128k:
        threshold: 128000
        potential_trap: true            # OpenAI 目前无差异定价但历史上出现过
    action: "成本预估自动纳入 context-length-based pricing tier"
    visual: "终端显示 '⚠ 长上下文溢价: +50% (320K > 200K 阈值)'"
```

### 2.12 计划消耗 vs 实际消耗偏差

```yaml
consumption_deviation:
  description: "AI 在施工前应该给出'计划消耗预估'——施工后对比实际消耗。偏差 > 30% 说明 AI 对自身消耗缺乏认知。"
  workflow:
    - step: "task_start"
      action: "AI 提交 plan_estimated_tokens（规划阶段预估）"
    - step: "task_end"
      action: "对比 actual_tokens vs plan_estimated_tokens"
    - step: "deviation_alert"
      condition: "abs(actual - plan) / plan > 0.30"
      action: "写入 budget_enforcer_deviation_events + 建议 AI 自我校准预估模型"

  calibration:
    method: "每个模型维护独立的预估偏差校正系数"
    update: "每周基于最近 20 个任务的实际偏差自动更新"
```

### 2.13 事中控制——Stream Abort Guard

> **决策 D-024-11（🆕 v0.4.0）**：Pre-flight Gate 只能管输入端。流式输出中途无法拦截——如果模型开始输出大量无意义内容，预算已被烧掉。Stream Abort Guard 对流式输出做中间 checkpoint（每 500 token）预算二次确认。

```yaml
stream_abort_guard:
  description: "流式输出中途预算二次确认——Pre-flight 场景的缺失互补"
  lifecycle_position: "in_flight"   # 位于 Pre-flight（事前）和 Post-flight（事后）之间

  checkpoints:
    frequency: 500                   # 每 500 output token 做一次预算检查
    checks:
      - condition: "remaining_budget - estimated_completion_cost < 0"
        action: "IMMEDIATE_ABORT——发送 abort signal 给 provider + 记录 partial output"
      - condition: "output_quality_gate.score < 0.3 AND tokens_emitted > 200"
        action: "ABORT_AND_RETRY——切回 input 用更便宜模型重试"
      - condition: "cumulative_response_too_verbose（token_count > expected × 3）"
        action: "ABORT_WITH_WARNING——日志 '响应过于冗长，建议添加 'be concise' 指令'"

  partial_output_handling:
    on_abort: "保存已输出的 partial_response 到 context_budget_tracker"
    resume_strategy: "下次调用时 append partial_response 到 system prompt '之前的回答在 [X] token 处中断'"

  provider_integration:
    anthropic: "streaming SSE — 监听 stop_reason='max_tokens'"
    openai: "streaming SSE — 监听 finish_reason='length'"
    google: "streaming SSE — 监听 finishReason='MAX_TOKENS'"
    deepseek: "streaming SSE — 同 OpenAI 协议"
```

### 2.14 事中控制——Output Quality Gate

> **决策 D-024-12（🆕 v0.4.0）**：Token ROI 只统计事后产出。但需要实时质量信号——如果 LLM 的前 200 token 输出明显是垃圾（格式错误/幻觉/不相关），应立即 abort + 切模型重试，而不是等到 4000 token 输出完了再判断。

```yaml
output_quality_gate:
  description: "输出前 N token 的快速质量校验——在浪费大量预算前发现问题"
  lifecycle_position: "in_flight"

  # 与 MOD-INF-023 Drift Detector 联动
  validator: "output_validator.early_quality_check()"

  early_signals:
    format_check:
      trigger: "first 200 output tokens"
      rules:
        - "JSON/XML 格式正确性"
        - "代码块完整性（``` 是否闭合）"
        - "markdown 语法正确性"
      fail_action: "ABORT + 追加 '你的输出格式有误，请重新生成' 到下一轮 prompt"

    relevance_check:
      trigger: "first 300 output tokens"
      method: "Fast embedding similarity(partial_output, task_prompt)"
      threshold: "similarity < 0.4"
      fail_action: "ABORT + L1_warning '输出与任务无关——可能上下文污染'"

    hallucination_check:
      trigger: "full response received"
      method: "引用验证——输出中声称的 file_path / module_id 是否真实存在"
      fail_action: "MARK_FAILED + 不计入 ROI + 写入 audit trail"

  auto_retry:
    max_retries: 2
    retry_model_escalation:
      attempt_1: "same model + extra 'be accurate' prompt"
      attempt_2: "升級到下一個 Tier 模型"
```

### 2.15 环境感知预算 Profile

> **决策 D-024-13（🆕 v0.4.0）**：业界标准实践——dev 环境永远只用最便宜模型，prod 才开全能力。Solo maintainer 最容易在 dev 调试时不小心烧掉一周预算。

```yaml
env_aware_budget_profiles:
  description: "根据环境自动切换预算策略——不需要手动切换 model/router 配置"
  detection: "环境变量 ZEPHYR_ENV 或自动检测（IDE 集成 → development, CI/CD → staging, deployed → production）"

  profiles:
    development:
      default_model_tier: "tier_0_free"
      max_model_tier: "tier_1_cheap"
      daily_cost_cap: "$1.00"
      task_cost_cap: "$0.10"
      cache_enabled: true
      audit_level: "minimal"
      notes: "调试/实验环境——绝不用付费模型，除非 Owner 显式 /switch-model"

    staging:
      default_model_tier: "tier_1_cheap"
      max_model_tier: "tier_2_standard"
      daily_cost_cap: "$5.00"
      task_cost_cap: "$0.50"
      cache_enabled: true
      audit_level: "standard"
      notes: "集成测试/预发——允许标准模型做质量验证"

    production:
      default_model_tier: "tier_1_cheap"
      max_model_tier: "tier_3_premium"
      daily_cost_cap: "$10.00"
      task_cost_cap: "$1.00"
      cache_enabled: true
      audit_level: "full"
      notes: "正式施工——全能力可用，但仍有日/任务成本硬顶"

  dev_trap_protection:
    description: "防止在 development 环境手动切换到 Tier-3 后忘记切回"
    auto_revert: "每次新 Task 开始时重置到当前 Profile 的 default_model_tier"
    persistent_override: "通过 `zephyr env override-production` 显式命令切换（需二次确认）"
```

### 2.16 预算策略沙盘 + 策略版本管理

> **决策 D-024-14（🆕 v0.4.0）**：你怎么知道五级预算+六级降级不会把系统卡死？预算策略需要在不上线的情况下验证——dry-run 模拟路径。策略变更需要版本管理——改坏了可以回滚。

```yaml
policy_sandbox:
  description: "预算策略的 dry-run 模拟环境——不实际调用 AI，模拟预算消耗路径"
  trigger: "budget_policy.yaml 变更后自动执行 OR `zephyr budget sandbox --scenario aggressive`"

  scenarios:
    low_complexity:
      tasks: 20
      task_type: "lint_fix"
      simulation: "模拟单天 20 个 Lint 修复任务——验证 tier_0_free 是否被正确路由"
      expected: "全部走 tier_0，零成本"

    medium_load:
      tasks: 50
      task_type: "mixed"
      simulation: "模拟中等施工量——50 个混合任务中包含 5 个需要升级到 tier_2 的复杂任务"
      expected: "tier_0 处理 45 个，tier_1 处理 3 个，tier_2 处理 2 个"

    budget_exhaustion:
      tasks: 100
      task_type: "heavy_refactor"
      simulation: "模拟预算耗尽场景——连续大规模重构直到触发 L5_halt"
      expected: "系统正确执行降级链且不进入 spiral"

    runaway_agent:
      tasks: 10
      task_type: "runaway_simulation"
      simulation: "模拟一个 Agent 在单个 Task 上持续重试——触发 per-agent sub-pool 限制"
      expected: "sub-pool 触顶后 spillover 被全局池 60% 总预算限制截断"

  output: "sandbox 执行后生成 `budget_sandbox_report.md`——包括通过/警告/失败的 checklist"

policy_versioning:
  description: "budget_policy.yaml 的版本管理——改坏了可以回滚"
  storage: "config/budget_policy_history/{version}/budget_policy.yaml"
  auto_version: "每次 git commit 时在 pre-commit hook 中快照当前 policy"
  rollback: "zephyr budget policy rollback --version v{N}"
  diff: "zephyr budget policy diff --v1 v2 — 对比两个版本的策略差异"
```

### 2.17 辅助能力——上下文浪费检测 + 冷启动豁免 + 自托管模型成本模型

> **决策 D-024-15（🆕 v0.4.0）**：补充三个之前被忽略的辅助能力——它们不影响核心逻辑，但在 solo maintainer 场景下持续性产生隐性成本。

```yaml
context_waste_detector:
  description: "你控制了预算上限，但不知道塞进上下文的材料里有多少是 LLM 实际没看的"
  tracking: "每次 LLM 调用后分析 response 中实际引用到的上下文片段"
  metric: "referenced_chars / total_context_chars"
  alert: "waste_ratio > 0.60 持续 5 个请求 → 建议 /compact 或精简 AGENTS.md"
  integration: "Context Engine 的 DocCompressor 根据 waste 数据优化选择策略"

cold_start_allowance:
  description: "每个 Session 初始阶段（读蓝图、索引文件、建立上下文）有固定'入场费'——不应计入任务预算"
  fixed_cost:
    - step: "读取 AGENTS.md + 核心蓝图"
      estimated_tokens: 3000
    - step: "建立 workspace index"
      estimated_tokens: 2000
    - step: "加载 budget_policy.yaml"
      estimated_tokens: 500
  total_cold_start: 5500             # 每个 Session 默认豁免
  accounting: "cold_start_tokens 计入 session 级预算但不计入任何任务的 task_budget"
  overridable: true                   # 复杂项目可以调整

local_model_cost_model:
  description: "蓝图假设全走 API。但如果你跑了本地模型（Ollama），'成本'怎么算？"
  cost_model:
    electricity: "$0.12/kWh"
    gpu_power: "200W"                   # 单 GPU 功耗
    tokens_per_second: 50              # 本地模型吞吐量（因模型而异）
    cost_per_1m_tokens: "electricity / (tokens_per_second × 3600) × 1,000,000 ≈ $0.13/MTok"
  accounting: "local tokens 记为 'local_cost' 而非 'api_cost'——在 showback 中分开展示"
  model_assignment: "tier_local（独立于 API Tier 体系）"
```

### 2.18 指令膨胀检测（Instruction Bloat Detector）

> **决策 D-024-16（🆕 v0.5.0）**：Boris Cherny 400 小时 Claude 使用分析——14% 的 token 浪费来自膨胀的 CLAUDE.md/AI 指令文件。我们的 Context Waste Detector (§2.17) 追踪 "sent vs referenced"，但指令文件是被动的——它总是被发送但永远不会被"引用"，仅跟踪 referenced 比例会误报。

```yaml
instruction_bloat_detector:
  description: "专门检测 AGENTS.md/CLAUDE.md/system_prompt 等指令文件的膨胀——这些文件每个 turn 都被发送，膨胀的边际成本极大"
  targets:
    - "AGENTS.md"
    - "budget_policy.yaml"
    - "所有 *blueprint.md 的 §1-§2（设计理念部分）"
  metrics:
    - "instruction_token_count"
    - "instruction_growth_rate_weekly"      # 每周增长率（超过 20% 告警）
    - "per_turn_instruction_overhead"       # 每轮的平均指令 token 开销
  alerts:
    instruction_oversized: "instruction_token_count > session_budget × 0.25"
    instruction_growing: "growth_rate_weekly > 20% → WARN '指令文件正在膨胀——建议精简冗余规则'"
    instruction_dominance: "per_turn_instruction_overhead > productive_tokens → 指令比产出还多"
  auto_compact:
    enabled: false                  # 不自动压缩（可能删除有用规则）
    suggest: "生成精简建议——检测哪个段落过去 30 天没被遵守过 → 建议删除"
  visual: "终端显示 '📋 指令: 3.2K (占预算 8%) | 本周增长 +5%'"
```

### 2.19 对话历史税检测（Conversation History Tax Detector）

> **决策 D-024-17（🆕 v0.5.0）**：Boris Cherny 数据——13% 的 token 浪费来自对话历史重读。长对话中，历史即使全部压缩后仍占上下文大头。Context Engine 的压缩解决"大小"但没解决"价值"——压缩后的历史 tokens 中可能 80% 对当前任务无价值。

```yaml
conversation_history_tax_detector:
  description: "跟踪对话历史中实际被当前 turn 使用的比例——未被引用的历史就是浪费"
  tracking:
    - "total_history_tokens_sent"
    - "history_tokens_referenced"            # LLM 在 response 中实际引用到的历史片段
    - "history_tax_ratio"                    # = sent / referenced
  alert:
    threshold: "history_tax_ratio > 5×"      # 5 倍浪费——发 5000 token 历史只用了 1000 token
    action: "WARN + 建议 /compact-aggressive（仅保留最近 3 轮的失败/上下文/决策摘要）"
  decay_model:
    description: "越远的 turn 价值越低——加权衰减而非均匀压缩"
    weights:
      last_3_turns: 1.0                      # 全部保留
      turns_4_10: 0.3                        # 仅保留决策 + 异常
      turns_11_plus: 0.05                    # 仅保留摘要
  synergy: "联动 Context Engine (MOD-INF-008) 的 DocCompressor 加权衰减策略"
  visual: "终端显示 '📜 历史: 12K/15K (80%) | 有效引用: 仅 22%'"
```

### 2.20 Timeout Guard（并行监控线程）

> **决策 D-024-18（🆕 v0.5.0）**：AgentGuard (2026.4) 三大 guard 之一——Timeout Guard = wall-clock kill switch。这是一个独立于预算链的并行线程——不依赖 L0-L6 降级或 Pre-flight Gate，一旦触发即强行 abort。

```yaml
timeout_guard:
  description: "独立并行线程——wall-clock 超时即 abort，不经过降级协商流程"
  lifecycle_position: "in_flight（与 Stream Abort Guard 并行运行）"
  implementation: "asyncio 独立 task → 每个 Session 启动一个 daemon timer"

  session_timer:
    countdown: 28800              # 8 小时（来自 §2.1 time_budget）
    on_expiry:
      action: "FORCE_ABORT——所有活跃请求立即终止"
      pre_action: "保存 Action History + 生成 resume checkpoint + 写入 audit trail"
      message: "⏰ Session 时间预算已耗尽（8h）——当前进度已保存。下次启动自动恢复。"

  task_timer:
    countdown: 3600               # 1 小时
    on_expiry:
      action: "FORCE_ABORT 当前 Task + 自动委托到新 Task"
      message: "⏰ 任务超时（1h）——已自动拆分并委托剩余工作到新任务"

  request_timer:
    countdown: 120                # 2 分钟
    on_expiry:
      action: "CANCEL streaming SSE + ABORT"
      auto_retry: true            # 自动重试一次（不同 Provider 或模型）
```

### 2.21 Self-Budget——Budget Enforcer 自身运营成本管控

> **决策 D-024-19（🆕 v0.6.0）**：SUPERVISORAGENT (ICLR 2026) 引入 LLM-free 自适应触发——传统 guards 自身消耗 token 来评估 token 消耗，形成悖论。Budget Enforcer 自身的运作成本（Output Quality Gate 的 LLM 调用、Instruction Bloat 的语义分析、Conversation Tax 的引用追踪）必须被预算。

```yaml
self_budget:
  description: "Budget Enforcer 不是免费的——自身 guards/detectors/analyzers 消耗的 token 需要独立上限"
  # SUPERVISORAGENT 原则：guards 应该是 LLM-free 的 trigger，仅在必要时升级到 LLM evaluation
  daily_cap: 50000                # Budget Enforcer 自身每日 token 上限

  components:
    # ── LLM-Free triggers（零成本，应优先使用）──
    llm_free:
      - "format_check (regex-based)"
      - "action_history.dedup_rules (hash-based)"
      - "timeout_guard (timer-based)"
      - "context_waste_detector.sent_count (non-LLM)"
      - "burn_rate_monitor (EMA-based)"

    # ── LLM-Dependent triggers（有成本，需配额控制）──
    llm_dependent:
      - name: "output_quality_gate.relevance_check"
        model: "tier_0_free"      # 强制用免费模型
        cap_per_call: 500
      - name: "output_quality_gate.hallucination_check"
        model: "tier_0_free"
        cap_per_call: 1000
      - name: "instruction_bloat_detector.auto_compact_suggest"
        model: "tier_0_free"
        cap_per_day: 2000
      - name: "conversation_tax_detector.reference_analysis"
        model: "tier_0_free"
        cap_per_day: 1500

  guard_efficiency:
    description: "Guards 的收益-成本比——如果 guard 自身消耗超过它节省的 token，关闭该 guard"
    metric: "tokens_saved_by_guard / tokens_consumed_by_guard"
    auto_disable_threshold: "< 0.5"  # guard 每花 2 token 才省 1 token → 关闭
    weekly_efficiency_report: true

  self_budget_exceeded:
    action: "HALT——所有 LLM-dependent guards 降级为 LLM-free 模式仅 warn 不 block"
    visual: "终端显示 '🛡 Self-Budget: 18K/50K (36%) | Guard 效率: 1:4.2 (省 budget:guard cost)'"
```

### 2.22 Token Spiral 早期预警系统（Token Spiral EWS）

> **决策 D-024-20（🆕 v0.6.0）**：TechAhead 2026 描述 token spiral 为"一个任务变成 47 次 API 调用"。传统的 Burn Rate 监控总速率——Spiral EWS 专门检测**每次调用都在放大下一步的调用量**的结构性扩张模式。

```yaml
token_spiral_ews:
  description: "检测请求量指数增长的螺旋模式——与 Burn Rate（总速率）互补"
  # Burn Rate 说"烧得快"；Spiral EWS 说"每一个请求让下一个请求更大/更多"

  spiral_markers:
    expanding_context:
      description: "每次 LLM 调用的 input token 比上次更大——可能是 context 积聚"
      detection: "last_5_inputs 呈递增趋势（Pearson r > 0.7）"
      action: "WARN '上下文在膨胀——建议立即 /compact'"

    multiplying_tool_calls:
      description: "每次 LLM 响应的 tool_call 数量递增——ReAct 循环失控前兆"
      detection: "last_5_turns 的 tool_call count 单调递增"
      action: "WARN '工具调用链在扩张——可能陷入 ReAct loop'"
      escalate: "连续 3 次递增 → L3_compress"

    depth_explosion:
      description: "agent-to-agent 委托深度超过安全阈值"
      detection: "delegation_depth > 4"
      action: "HALT delegation + 扁平化处理（不委托，直接执行）"

    time_per_turn_growth:
      description: "每轮耗时递增——模型在处理越来越复杂的问题"
      detection: "last_5_turns duration 单调递增"
      action: "WARN + 建议 Narrow Scope 或拆分任务"

  spiral_score:
    description: "综合螺旋风险得分 0-100"
    formula: "weighted_sum(expanding_context, multiplying_tool_calls, depth_explosion, time_growth)"
    thresholds:
      score_30: "L1_warning"
      score_60: "L3_compress + auto_narrow"
      score_80: "L6_kill_switch——强制中断 spiral"
```

### 2.23 Context Poisoning Cascade 检测

> **决策 D-024-21（🆕 v0.6.0）**：SUPERVISORAGENT (ICLR 2026) 的核心贡献——MAS 中一个 agent 的幻觉输出被下游 agent 当作事实，会产生指数级成本放大。单点的 bad observation 可以导致整个 pipeline 的 token 消耗翻倍。

```yaml
poisoning_cascade_detector:
  description: "检测上游 agent 的错误输出被下游 agent 继承放大的级联效应"
  # 典型场景：Agent-A 说 'config/file.yaml 不存在'（幻觉）→ Agent-B 开始造那个文件（浪费）
  #           → Agent-C 开始引用那个假文件 → 成本指数放大

  detection_layers:
    fact_contradiction:
      description: "Agent 输出声称的事实与系统已知状态矛盾"
      method: "cross-reference agent output claims vs workspace index / file system state"
      example: "Agent says 'module X has rate limit 100' but config says 50"
      action: "MARK as potentially_poisoned + 注入 warning 到下游 agent 的 system prompt"

    chain_of_faith:
      description: "追踪信息源链——如果 Agent-C 引用 Agent-B 引用 Agent-A 且 Agent-A 被纠正过"
      method: "构建 observation provenance DAG"
      ttl: "3600s（1h 内同一不实引用链触发级联熔断）"

    cascade_cost_tracker:
      description: "量化下中游因上游错误而浪费的 token"
      metric: "tokens_spent_on_fixing_poisoned_context / total_tokens"
      alert: "cascade_cost > 15% total → WARN '上下文中毒成本过高——建议重启 Session'"

  auto_isolation:
    description: "检测到级联时自动隔离可疑 agent 的中间输出"
    action: "清除被标记为 potentially_poisoned 的上下文片段 + 重新生成"
```

### 2.24 Hierarchical Parent-Child Agent 成本归因

> **决策 D-024-22（🆕 v0.6.0）**：现代 MAS 中一个 coordinator 可能委托多个 child agents。扁平 entity-level 归因无法展示"哪个 coordinator 的委托模式最贵"。

```yaml
parent_child_attribution:
  description: "追踪 agent 委托链的树状成本结构——parent 承担 child 的成本但有 governance 杠杆"

  delegation_tree:
    description: "每个 agent call 记录 parent_agent_id 和 cause_agent_id"
    structure: "DAG（同一 child 可被多个 parent 委托）"

  attribution_rules:
    direct_cost: "agent 自己的 LLM API 消耗 → 归于自己"
    delegated_cost: "child agent 的消耗 → 按 delegation_ratio 回溯到各 parent"
    root_cause_cost: "如果 child 因 parent 的错误指令增加了成本 → 超额部分归于 parent"

  query_examples:
    top_delegator: "coordinator-A 直接消耗 $3 + 委托链总成本 $12 → 真实影响 $15"
    delegation_efficiency: "child 产出 / parent 委托成本 → 低效委托被标记"

  visual: "终端显示 '🌳 coordinator-A: $3(self) + $12(delegated) = $15 total | 委托比 4:1'"
```

### 2.25 推理模型 Think-Time 成本感知 + LLM-Free Guard 升级路径

> **决策 D-024-23（🆕 v0.6.0）**：Reasoning token 的价格是 output token 的 2-3x 且不可见的 think-time 消耗也是成本。v0.5.0 有 reasoning_limit 但没建立 think-time 成本模型。

```yaml
think_time_cost_model:
  description: "Reasoning tokens 和 think-time latency 的量化成本模型"

  providers:
    anthropic_extended_thinking:
      thinking_tokens: "$1-3/MTok (≈ output price × 0.5)"
      budget_tip: "thinking_tokens > task_output_tokens → 思考比产出还贵 → 切换模型"
    openai_o1_o3:
      reasoning_tokens: "隐藏（不返回，但计入 pricing）"
      detection: "actual_charges / visible_tokens → 推算 reasoning token 占比"
      budget_tip: "o1/o3 调用尽量走 batch 路由（batch 价格 50% off）"

  auto_switch:
    trigger: "thinking_tokens > 2× output_tokens AND task 非终审/审计类"
    action: "自动切到 tier_0 或 tier_1 非推理模型"

# ── v0.6.0 Guard 升级路径：从 LLM-dependent → LLM-free 的渐进优化 ──
guard_upgrade_path:
  description: "SUPERVISORAGENT (ICLR 2026) LLM-free 原则——在 scaffold 先用 LLM-based 验证逻辑正确性，stable 后逐步替换为 LLM-free 方案降本"
  phases:
    scaffold: "所有 guard 用 LLM-dependent 先验证逻辑——容忍 100% guard 开销"
    experimental: "format_check → regex-based LLM-free（最大降本点）"
    beta: "relevance_check → embedding similarity LLM-free（仅需一次 embedding 计算）"
    stable: "hallucination_check → 仅 10% 采样 + cached validation → LLM-free"
    self_calibrating: "> 80% guard 调用为 LLM-free | guard_efficiency ratio > 10:1"
```

### 2.26 Runtime Trust Rings——Budget Enforcer 自身的执行信任分级

> **决策 D-024-24（🆕 v0.7.0）**：Microsoft Agent Governance Toolkit 引入 Runtime Rings——不同信任级别的代码在不同 Ring 中执行。100% AI 构建的系统中，Budget Enforcer 自身是 AI 生成的 untrusted 代码——它凭什么能做"最终裁决"？

```yaml
runtime_trust_rings:
  description: "Budget Enforcer 内部组件按信任级别运行在不同的 Ring 中——Ring 0 仅限人类 Owner 或签名代码"
  # 核心原则：AI 生成的代码最高只能到 Ring 2——Ring 0/1 必须是 human-signed 或 bootstrapper 代码

  ring_0_kernel:
    description: "Root of Trust——不可被任何 AI agent 修改"
    components:
      - "budget_policy_signing_verifier"  # 验证 budget_policy.yaml 的 Ed25519 签名
      - "tamper_evident_log_writer"       # append-only hash chain 写入器
      - "fail_mode_enforcer"              # 强制 fail-open/fail-closed 模式
    trust_source: "Ed25519 密钥对——私钥离线存储于 Owner 的 1Password/YubiKey"
    modification: "仅 Owner 物理操作 + 签名验证"

  ring_1_system:
    description: "System-critical but can be AI-reviewed (AI可建议，人类审批)"
    components:
      - "budget_policy_implementation"    # 不修改策略文件本身，仅执行签名已验证的策略
      - "pre_flight_gate"                 # 执行预算检查——但不修改预算值本身
      - "kill_switch"                     # 熔断触发

  ring_2_agent_space:
    description: "AI-generated runtime guards——可被 AI 修改但受 Ring 1 监控"
    components:
      - "stream_abort_guard"
      - "output_quality_gate"
      - "spiral_ews"
      - "instruction_bloat_detector"
      - "conversation_tax_detector"
      - "poison_cascade_detector"

  ring_3_untrusted:
    description: "受控的受预算约束的 agent 执行——Budget Enforcer 在此层施加约束"
    components:
      - "all budgeted agent calls"

  enforcement:
    ring_escalation: "Ring 3 agent 不能调用 Ring 2 接口修改 budget policy；Ring 2 guard 不能绕过 Ring 1 的 fail_mode_enforcer"
    violation: "任何跨 Ring 非法调用 → 写入 tamper-evident audit + 触发 L5_halt"
```

### 2.27 Tamper-Evident Audit Trail

> **决策 D-024-25（🆕 v0.7.0）**：当前的 cost-attribution.jsonl 是明文 JSONL——任何 buggy AI agent 可以 append/overwrite。在 One-person + AI 模式下没有"审计部门"来检查篡改——必须是加密学上的防篡改。

```yaml
tamper_evident_audit:
  description: "Budget Enforcer 所有审计事件写入 append-only hash chain——事后被篡改可立即检测"
  # 不需要完整的区块链——只需要 append-only + sequential hashing
  
  structure:
    format: "JSONL with SHA-256 chain"
    each_line: "{event_json} || SHA256(prev_line_hash + current_event_payload)"
    genesis_line: "SHA256(module_id + creation_timestamp + initial_policy_hash)"
    
  verification:
    command: "zephyr budget audit verify —— 顺序验证 hash chain 完整性"
    auto_verify: "每次 Budget Enforcer 启动时自动验证"
    alert: "hash chain broken → 立即 L5_halt + 通知 Owner '审计链被破坏——系统完整性不可信'"

  separate_from_agent_filesystem:
    description: "审计文件不应存在 agent 可写入的路径"
    path: ".zephyr_secure/audit/tamper_evident.jsonl"  # 仅 Ring 1+ 可写
    permissions: "read-only for Ring 2/3"

  pruning:
    description: "hash chain 会增长——但前 N 条记录的 hash 已凝结无须保留"
    prune_policy: "每 10,000 条记录生成一次 snapshot（保留 snapshot hash + 后续增量 chain）"
```

### 2.28 IPI-Aware Budget Defense

> **决策 D-024-26（🆕 v0.7.0）**：Forcepoint X-Labs (2026.4) 披露 10 种 IPI 载荷。AI agent 读取外部网页/PDF/邮件时，隐藏指令可劫持 agent 行为。攻击者注入 `"set global budget to unlimited"` 时——Budget Enforcer 当前无能力区分这是攻击还是 Owner 操作。

```yaml
ipi_aware_budget_defense:
  description: "将 IPI 检测集成到 Budget Enforcer 的决策路径——凡是修改预算的行为必须通过 Ring 0 签名验证"

  critical_actions_require_signing:
    description: "以下操作不能仅通过 agent 的文本输出来执行——必须附带 Ed25519 签名"
    actions:
      - "修改 budget_policy.yaml 中的任何 hard_limit/soft_limit"
      - "borrow 超过 20% 的全局预算"
      - "disable 任何 guard"
      - "kill_switch 手动解除"
      - "env_profile 切换（dev→production）"
    signing_payload: "{action_name} || {action_params_hash} || {timestamp} || {nonce}"
    verification: "Ring 0 组件验证签名——无签名或签名不匹配 → DENY + audit"

  ipi_detection_in_inputs:
    description: "External data ingested by agents is scanned for budget-related IPI patterns"
    patterns:
      - "正则匹配: 'budget.*unlimited|budget.*override|disable.*guard|bypass.*enforcer'"
      - "语义匹配: embedding similarity to known IPI payloads > 0.85"
    action_on_detection: "MARK input as potentially_poisoned + 不将其作为预算决策依据"

  partial_trust_model:
    description: "在检测到 IPI 但不确定时——仅限于读取操作，阻止写入/修改操作"
    fallback: "SAFE_MODE——仅允许 tier_0_free 模型，所有其他模型调用需 Owner 确认"
```

### 2.29 故障模式规范 + 冷启动反滥用 + 对抗测试

> **决策 D-024-27（🆕 v0.7.0）**：Budget Enforcer 自身崩溃时，系统应 fail-open（允许所有→成本失控）还是 fail-closed（拒绝所有→系统瘫痪）？前 6 轮从未定义。

```yaml
fail_mode_specification:
  description: "Budget Enforcer 在每个 level 的故障模式——并非一刀切 fail-open 或 fail-closed"

  per_level_fail_mode:
    l0_request: "fail-closed"     # 单次请求故障→拒绝该请求（影响最小）
    l1_turn: "fail-closed"        # 单轮故障→拒绝该轮（用户可重试）
    l2_task: "fail-closed"        # 任务级故障→拒绝任务（拆分或重试）
    l3_session: "fail-open限流"   # Session 故障→允许调用但限制在 tier_0_free + 1/10 上限
    l3_5_workflow: "fail-open限流"# Workflow 故障→同上
    l4_global: "fail-closed"      # 全局故障→硬拒绝（安全优先于可用性）
    l4_5_self: "fail-open限流"    # Self-Budget 故障→降级为仅统计不阻断

  fail_mode_recovery:
    heartbeat: "每 30s 检查各组件健康——连续 3 次 heartbeat 失败触发对应 fail_mode"
    auto_recovery: "组件恢复后自动从 fail_mode 恢复正常模式"

# ── v0.7.0 冷启动反滥用 ──
cold_start_anti_abuse:
  description: "§2.17 冷启动豁免 5500 token/session——可被 agent 通过频繁重启利用"
  rate_limit: "同一 Owner 1 小时内最多 3 个 Session（超过则冷启动豁免降为 1000 token）"
  daily_cap: "24 小时内冷启动豁免累计不超过 27,500 token（= 5 × 5500）"
  detection: "超过速率限制 → WARN '检测到频繁 Session 重启——冷启动豁免已缩容'"

# ── v0.7.0 对抗测试强制要求 ──
adversarial_testing_mandate:
  description: "Oktsec 报告——88% 组织遭遇 AI agent 安全事件。Budget Enforcer 上线前必须通过对抗测试"
  test_vectors:
    - "IPI 注入 budget_policy.yaml 修改尝试"
    - "Agent 尝试利用 cold_start_allowance 通过 10 次快速重启"
    - "Agent 尝试通过 parent-child 委托链无限代理消耗预算"
    - "Agent 尝试在 stream_abort_guard 触发前完成恶意操作"
    - "Agent 尝试通过多 Provider 切换触发 race condition"
  gate: "Phase experimental→beta 前必须通过全部 5 项对抗测试"
  report: "对抗测试报告写入 docs/09_audit/adversarial_test_report.md"
```

### 2.30 启动校准阶段（Bootstrapping Calibration Phase）

> **决策 D-024-28（🆕 v0.7.0）**：Day 0 的 budget_policy.yaml 是 AI 生成的猜测。如果阈值太紧→系统不可用→无法收集数据→自学习无法启动。需要一个显式的"宽限期"。

```yaml
bootstrapping_calibration:
  description: "新部署的前 30 天为校准模式——阈值宽松，侧重数据收集而非严格执法"
  duration: "30 days or 100 tasks completed（whichever first）"

  calibration_profile:
    description: "所有 hard_limit 临时 ×3，soft_limit 仅告警不阻断"
    hard_limit_multiplier: 3.0
    enforcement: "ALL actions → warn-only（不 DENY，不 HALT）"
    exceptions: "loop_detection 和 kill_switch 这两个安全熔断保持生效"

  exit_criteria:
    min_data_points: 100            # 至少收集 100 个任务的消耗数据
    convergence: "预算预估偏差 < 20%（连续 10 个任务）"
    auto_exit: "满足条件后自动切换到正常 enforcement 模式"
    manual_exit: "Owner 可随时执行 `zephyr budget exit-calibration` 提前结束"

  post_calibration:
    auto_tune: "基于收集的 100 个任务数据，自动调整 soft_limit/hard_limit 为 P95 消耗值"
    report: "校准报告——各模型/任务类型的 P50/P75/P95/P99 消耗分布"
    human_review: "自动调整后的阈值需 Owner 签名确认方可生效"
```

---

## 3. Solo Maintainer 特异性设计

> **决策 D-024-10（v0.7.0 修订）**：系统面向"1人+AI维护"运行。v0.7.0 核心补丁：作为唯一的人类 Owner，你持有的 Ed25519 密钥是 **整个预算体系的信任根**——没有你的签名，任何 AI agent 都不能修改预算策略、解除熔断、或绕过 fail_mode。这是"一个人的治理委员会"。

```yaml
solo_maintainer_optimizations:

  zero_toil:
    self_learning_thresholds:
      description: "预算阈值不是人工调的——基于过去 30 天的消耗自动调整"
      update_frequency: "每周一自动计算新阈值"
      method: "30d P90 × 安全系数 1.3"
      manual_override: "config/budget_overrides.yaml（Owner 手动锁定时读取）"

    auto_silence_alerts:
      description: "同类超预算告警 1 小时内最多发 1 次"
      grouping_key: "{budget_level}_{event_type}"
      cooldown: 3600

    weekly_auto_summary:
      description: "每周自动生成自然语言摘要——Owner 不需要读 JSONL"
      output: "docs/09_audit/cost_reports/weekly-{date}.md"
      language: "zh"
      sections:
        - "总览：本周花了多少、比上周多还是少"
        - "异常：哪些时刻触发了降级/熔断"
        - "归因：钱花在了哪里（Agent/Tool/Activity/Outcome Top 3）"
        - "ROI：效率变化趋势"
        - "预测：下周预计消耗"
        - "建议：需要 Owner 关注的配置变更建议"
        - "新模型：本周发现的新模型及其性价比评估（v0.4.0 新增）"

  affordability_first:
    free_model_preference:
      description: "能用 Trae CN 免费模型完成的就不调付费 API——v0.4.0 模型路由反转后此为默认行为"
      tier_0_first: true
      escalate_rule: "仅当 tier_0 返回质量不达标（通过 output_validator 检测）才升级到 tier_1"

    cost_cap_per_task:
      description: "每任务最高成本硬封顶"
      default: "$0.50/task"      # solo maintainer 可承受的单任务成本
      overridable: true

    # ── v0.4.0 新增：环境感知 ──
    env_awareness:
      profile: "$ZEPHYR_ENV"      # development | staging | production
      dev_safety: "development 环境自动锁定在 tier_0_free，防止调试时烧预算"
      auto_revert_to_dev: "每次 IDE 重启后自动重置为 development profile"

  weekly_rhythm:
    description: "每周 2-5 小时施工 → 周预算比日预算更合理"
    budget_granularity: "weekly"
    daily_only_alert: "单日超过周预算 40% 时提醒"

  one_person_maintenance:
    description: "v0.4.0 新增——1 人维护下最需要自动化的事情"
    new_model_notification: "新模型出现时自动通知——你不会主动关注模型市场"
    cost_anomaly_highlights: "每周摘要中高亮最值得关注的 3 个异常——不需要手动翻日志"
    one_click_rollback: "zephyr budget policy rollback——策略改错了可以一键回滚"
    sandbox_guard: "修改 budget_policy.yaml 后自动 dry-run——上线前就知道有没有问题"
    data_auto_cleanup: "成本日志自动归档过期——不需要手动清理磁盘"
```

---

## 4. 文件组成

| 文件 | 职责 | v0.5.0 变更 |
|------|------|:---:|
| `budget_tracker.py` | 预算追踪器——五级 Token+Cost+Time 三维消耗统计 + TTL 管理 | 🔄 三维 |
| `budget_enforcer.py` | 预算执行器——全生命周期（事前+事中+事后）+ Pre-flight Gate + In-flight Guards | 🔄 Narrow/Reroute 决策 |
| `degradation_manager.py` | 降级管理器——六级降级链 + Narrow/Reroute + Global Timeout + 回升 + 反螺旋 | 🔄 新增 Narrow/Reroute/Timeout |
| `model_router.py` | 模型路由器——Tier 路由 + 多Provider least-cost + Batch + Provider Tier + 长上下文溢价 | 🔄 多Provider + Tier感知 + 长上下文溢价 |
| `pre_flight_gate.py` | 事前拦截门——调用前三维预算预估 + ALLOW/DEGRADE/DENY/BORROW/NARROW | 🔄 三维 + 长上下文 + NARROW |
| `action_history.py` | 动作历史去重——结构化 action 签名 + semantic_hash + 效果去重 + 自修复螺旋 | 🆕 |
| `timeout_guard.py` | 并行超时守卫——独立 asyncio daemon timer，wall-clock 超时即 abort + resume | 🆕 |
| `instruction_bloat_detector.py` | 指令膨胀检测——AGENTS.md/budget_policy 等膨胀监控 + 精简建议 | 🆕 |
| `conversation_tax_detector.py` | 对话历史税检测——加权衰减策略 + 有效引用率追踪 | 🆕 |
| `stream_abort_guard.py` | 流式中断守卫——流式输出中途三维预算二次确认 | — |
| `output_quality_gate.py` | 输出质量门——前 N token 快速质量校验 | — |
| `context_waste_detector.py` | 上下文浪费检测——sent vs referenced 比例 | — |
| `policy_sandbox.py` | 预算策略沙盘——dry-run 模拟 + 场景验证 | — |
| `budget_profile_manager.py` | ENV Profile 管理器——dev/staging/prod 自动切换 | — |
| `semantic_cache.py` | 语义缓存——三层缓存 | — |
| `cost_attributor.py` | 成本归因——四级归因 + Showback + 数据生命周期 | — |
| `roi_calculator.py` | ROI 计算器 | — |
| `pricing_sync.py` | 价格同步 + 新模型发现 + Token 归一化 + 长上下文定价 | — |
| `config/budget_policy.yaml` | Budget Policy as Code | — |
| `config/budget_policy_history/` | 策略版本历史 | — |
| `self_budget_tracker.py` | Self-Budget 追踪器——guards 自身消耗独立跟踪 + guard_efficiency 比 | 🆕 v0.6.0 |
| `spiral_ews.py` | Token Spiral EWS——上下文膨胀/工具链扩张/委托深度爆炸检测 | 🆕 v0.6.0 |
| `poison_cascade_detector.py` | Context Poisoning Cascade——幻觉级联污染检测 + provenance DAG | 🆕 v0.6.0 |
| `parent_child_attributor.py` | Hierarchical Parent-Child 归因——委托链树状成本归因 | 🆕 v0.6.0 |
| `think_time_model.py` | Reasoning Think-Time 成本模型——推理 token 隐藏成本量化 | 🆕 v0.6.0 |
| `trust_ring_manager.py` | Runtime Trust Ring 管理器——Ring 0-3 隔离 + 跨 Ring 调用鉴权 | 🆕 v0.7.0 |
| `tamper_evident_log.py` | Tamper-Evident Audit——append-only SHA-256 hash chain 写入与验证 | 🆕 v0.7.0 |
| `ipi_defense.py` | IPI-Aware Defense——预算相关 IPI 模式检测 + 签名验证网关 | 🆕 v0.7.0 |
| `fail_mode_manager.py` | Fail-Mode Manager——per-level fail-open/closed 决策 + heartbeat | 🆕 v0.7.0 |
| `bootstrapping_calibrator.py` | Bootstrapping Calibrator——Day 0→30 渐进收紧 + P95 自动调参 | 🆕 v0.7.0 |
| `adversarial_tester.py` | Adversarial Test Runner——5 项对抗测试自动执行 | 🆕 v0.7.0 |

---

## 5. 施工 Phase 规划

| Phase | 任务 | 状态 | 产出 |
|:---:|------|:---:|------|
| sandbox | 🆕 v0.5.0：三维 Budget Policy Sandbox（dry-run 4场景含 Time Budget 验证）+ Policy Versioning + 自修复螺旋检测沙盘 | 📋 Backlog | 策略三维验证全覆盖 |
| scaffold | BudgetTracker（五级三维含Self-Budget）+ BudgetPolicy YAML + Pre-flight Gate（三维+长上下文+Self-Budget check）+ Action History with Dedup + Stream Abort Guard 骨架 + Timeout Guard + Spiral EWS 骨架 | 📋 Backlog | 全生命周期+三维+Self-Budget 核心可运行 |
| experimental | Model Router（多Provider least-cost + Batch + Provider Tier感知+长上下文溢价+Think-time路由）+ Degradation Manager（六级+Narrow/Reroute/Timeout+回升）+ Semantic Cache + 价格同步 + ENV Profile Manager + Poison Cascade Detector 骨架 | 📋 Backlog | 完整的降级+路由+安全+环境适配 |
| beta | Cost Attributor（含Outcome/Judge/Parent-Child）+ ROI Calculator + Weekly Auto-Summary + Burn Rate面板 + Context Waste Detector + Instruction Bloat Detector + Conversation Tax Detector + Guard Efficiency Report | 📋 Backlog | 全量归因+检测+审计+Self-Budget |
| stable | 自学习阈值 + Anti-Spiral 验证 + 自修复螺旋检测 + Budget Savings 储蓄验证 + 新模型发现 + Budget Policy Sandbox 全场景验证 | 📋 Backlog | Solo maintainer 全能力验证 |
| self_calibrating | 计划 vs 实际三维偏差校准 + 模型路由质量反馈闭环 + Distribution Shift + 对话历史税自适应权重 + 指令膨胀持续监控 | 📋 Backlog | 自适应进化 |

---

## 6. 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-024-01 | 四级自动降级，不需要 Owner 介入 | 2026-05-05 | 预算超限是技术问题不是审批问题，自动降级更及时 |
| D-024-02 | 三级→五级预算体系（Request→Turn→Task→Session→Global） | 2026-05-05 | 专业机构 4 级实践 + Turn 级是 token spiral 锚点 |
| D-024-03 | Pre-flight Gate 事前拦截——调用前预估+拦截，不再纯事后反应 | 2026-05-05 | Google Adaptive Budgeting / kagenti pre-request blocking |
| D-024-04 | 🆕 v0.4.0 模型路由方向反转——默认最低→质量不达标才升级 + Batch 路由（50% 折扣） | 2026-05-05 | Cost Engineering for Agents + Vibe Coding 模型组合拳 |
| D-024-05 | 🆕 v0.4.0：六级降级链新增 L1.5 沉没成本干预 + 预算耗尽用户沟通协议 | 2026-05-05 | 再试一次就好了 是成本超支的心理陷阱——系统必须主动干预 |
| D-024-06 | Loop Detector：工具调用指纹匹配 + 3/5/10 三级阈值 | 2026-05-05 | 87% 成本超支来自过度自治 + AICosts.ai real-world disasters |
| D-024-07 | Semantic Cache：三层缓存（Prompt/Tool/Embedding）+ 可观测 | 2026-05-05 | Anthropic cache-aware + Agent 成本控制实战（缓存降本 30-50%） |
| D-024-08 | 🆕 v0.4.0：Cost Attribution 新增 Outcome（成功/失败/部分）维度 + LLM-as-Judge 独立核算 + 数据生命周期 | 2026-05-05 | FinOps for AI chargeback + 失败消耗和成功消耗的 ROI 完全不同 |
| D-024-09 | 🆕 v0.4.0：Burn Rate 新增 Distribution Shift 检测 + Rate Limit 浪费追踪 | 2026-05-05 | 结构异常往往先于总量异常 + 被限流的重试是纯浪费 |
| D-024-10 | 🆕 v0.4.0：Solo Maintainer 扩展——ENV Profile + 新模型发现 + 一键回滚 + 沙盘守卫 + 数据自动清理 | 2026-05-05 | 1人+AI维护的零运维需求 |
| D-024-11 | 🆕 v0.4.0：Stream Abort Guard——流式输出中途二次预算确认（每 500 token checkpoint） | 2026-05-05 | Pre-flight 只能管输入，in-flight 缺失导致 87% 成本超支发生在输出阶段 |
| D-024-12 | 🆕 v0.4.0：Output Quality Gate——前 200/300 token 快速质量校验（格式/相关性/幻觉） | 2026-05-05 | 实时质量信号比事后 ROI 分析更有成本控制价值 |
| D-024-13 | 🆕 v0.4.0：ENV Profile——dev/staging/prod 三套预算策略 + dev 环境永远锁在免费模型 | 2026-05-05 | 调试时不小心烧预算是一人维护模式的最大风险 |
| D-024-14 | 🆕 v0.4.0：Budget Policy Sandbox——dry-run 模拟（4 场景）+ Policy Versioning（回滚/diff） | 2026-05-05 | 预算策略上线前不验证 = 拿生产环境当试验田 |
| D-024-15 | 🆕 v0.4.0：辅助能力——上下文浪费检测 + 冷启动豁免 + 自托管模型成本模型 | 2026-05-05 | 隐性成本在 solo 语境下持续累积至不可忽略 |
| D-024-16 | 🆕 v0.5.0：Instruction Bloat Detector——检测 AGENTS.md/指令文件膨胀（Boris Cherny 数据：14% 浪费） | 2026-05-05 | 指令文件每 turn 都被发送——膨胀的边际成本极大 |
| D-024-17 | 🆕 v0.5.0：Conversation History Tax Detector——对话历史加权衰减 + 有效引用率（Boris Cherny 数据：13% 浪费） | 2026-05-05 | 压缩解决大小不解决价值——80% 压缩后历史仍无价值 |
| D-024-18 | 🆕 v0.5.0：Timeout Guard——独立 asyncio daemon timer，wall-clock 超时即 abort（AgentGuard 三大 guard 之一） | 2026-05-05 | 存在 token 少但耗时极长的任务——仅 token/cost 预算无法覆盖 |
| D-024-19 | 🆕 v0.6.0：Self-Budget——Budget Enforcer 自身运营成本管控（GUARDS 不是免费的） | 2026-05-05 | SUPERVISORAGENT (ICLR 2026) LLM-free trigger 原则——传统 guards 自身消耗 token 评估 token |
| D-024-20 | 🆕 v0.6.0：Token Spiral EWS——上下文膨胀/工具链扩张/委托深度爆炸/时间递增四维检测 | 2026-05-05 | TechAhead 2026——1 task → 47 API calls spiral pattern |
| D-024-21 | 🆕 v0.6.0：Context Poisoning Cascade——幻觉 upstream 输出指数污染 downstream agents | 2026-05-05 | SUPERVISORAGENT——单点 hallucination → pipeline 级成本放大 |
| D-024-22 | 🆕 v0.6.0：Hierarchical Parent-Child Agent 成本归因——委托链树状成本 | 2026-05-05 | MAS coordinator 委托模式需要归因到 delegation pattern 级别 |
| D-024-23 | 🆕 v0.6.0：Think-Time Cost 模型 + LLM-Free Guard 升级路径——推理 token 隐藏成本 + 渐进降本 | 2026-05-05 | Reasoning tokens 2-3x price + SUPERVISORAGENT scaffold→stable 优化路径 |
| D-024-24 | 🆕 v0.7.0：Runtime Trust Rings——Budget Enforcer 内部 Ring 0-3 信任分级（Microsoft Agent Governance Toolkit 对表） | 2026-05-05 | AI 生成的 Budget Enforcer 代码最高 Ring 2——Ring 0 仅限 Owner Ed25519 签名 |
| D-024-25 | 🆕 v0.7.0：Tamper-Evident Audit Trail——append-only SHA-256 hash chain | 2026-05-05 | 明文 JSONL 审计日志可被 buggy AI agent 篡改——加密学防篡改是信任的基础 |
| D-024-26 | 🆕 v0.7.0：IPI-Aware Budget Defense——Forcepoint X-Labs 10 种 IPI 载荷防御 + 签名网关 | 2026-05-05 | 外部注入 "set budget to unlimited"——系统必须区分 IPI 攻击 vs Owner 操作 |
| D-024-27 | 🆕 v0.7.0：Formal Fail-Mode Spec + Cold Start Anti-Abuse + Adversarial Testing Mandate | 2026-05-05 | Budget Enforcer 崩溃时 fail-open/fail-closed 从未定义——这是 an incident waiting to happen |
| D-024-28 | 🆕 v0.7.0：Bootstrapping Calibration Phase——Day 0→30 渐进收紧 + P95 自动调参 | 2026-05-05 | Day 0 阈值是 AI 猜测——太紧→系统卡死→自学习无法启动（bootstrap paradox） |

---

## 7. 风险登记

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|:---:|------|------|
| 五级预算过度限流 | 中 | AI 频繁被拦截→施工效率下降 | 每级独立配置 + Borrow 机制 + Tier-0 永远可用 |
| **Stream Abort 过于激进**（🆕 v0.4.0） | 中 | 正常长输出被误中断→任务无法完成 | 仅当 `quality_score < 0.3 AND output_fragment_unusual` 才 abort；正常超长输出仅 warn |
| Burn Rate 误报 | 低 | 频繁触发不必要的降级 | 7 天基线自适应 + 告警冷却 |
| 循环检测误杀正常重试 | 低 | 正常的 3 次重试被阻断 | 阈值 ≥ 3 + fingerprint_ttl 5 分钟 |
| 语义缓存污染 | 低 | 过期数据被返回 | 审计每条 hit + TTL 强制过期 + 加密 |
| LiteLLM 定价同步失败 | 低 | 价格失真→预算控制不准 | 本地缓存 + 3 天同步失败告警 |
| 降级螺旋 | 中 | 连续降级导致系统不可用 | Anti-spiral max 1/min + recovery cooldown |
| **ENV Profile 切换错误**（🆕 v0.4.0） | 中 | dev 环境误用 production profile→浪费预算 | 每次新 Task 自动重置 + `ZEPHYR_ENV` 显式设置 + dev 环境永久哨兵检查 |
| **策略沙盘 vs 实际不一致**（🆕 v0.4.0） | 低 | dry-run 通过但上线后卡住 | Sandbox 使用真实历史数据回放 + Score differential alert |
| **上下文浪费检测自身开销**（🆕 v0.4.0） | 低 | 每次调用后额外 LLM 校验增加成本 | waste 检测只在 10% 采样执行 + 仅 warn 模式 |
| **新模型自动发现被忽略**（🆕 v0.4.0） | 高 | Owner 不知道有更便宜的模型可用→持续多付钱 | 每周摘要置顶新模型发现 + 月度备忘提醒 |
| **Timeout Guard 误杀长构建**（🆕 v0.5.0） | 中 | 大型重构/测试需要 > 1h 但被 timeout 截断 | sidestep 机制：显式标记 `--no-timeout` 可绕过单次任务超时 |
| **指令膨胀检测误报**（🆕 v0.5.0） | 低 | 合理的大型 AGENTS.md 被标记为膨胀 | 仅超过 `session_budget × 0.25` 才告警——正常 2000 字指令不会触发 |
| **自修复螺旋误杀**（🆕 v0.5.0） | 低 | 正常的迭代调试被当作螺旋 | 仅 lint_error_count 增长才触发——功能改进不会被拦截 |
| **长上下文定价 drifts**（🆕 v0.5.0） | 中 | Provider 默默调整溢价阈值→系统仍用旧阈值 | 价格同步中也同步定价策略（非仅价格数字） |
| **预算储蓄被 exploit**（🆕 v0.5.0） | 低 | Agent 故意用最便宜模型以储蓄→影响产出质量 | 储蓄池仅在预算紧张时自动释放——不鼓励行为 |
| **Self-Budget 自身触发熔断**（🆕 v0.6.0） | 中 | Budget Enforcer 自身用光预算→所有 guard 降级为 warn-only | 同行无解——这是终极防线挑战。用 LLM-free guard 逐步替换来降低概率 |
| **Spiral EWS 入报警阈值不准**（🆕 v0.6.0） | 中 | 正常多步推理被误判为 spiral | 阈值为 Pearson r > 0.7（强相关才触发）+ 需要 5 轮趋势确认 |
| **Poison Cascade DAG 开销自噬**（🆕 v0.6.0） | 低 | provenance DAG 自身数据量随调用增加而膨胀 | TTL 1h 过期 + 仅保留 contradiction 节点 |
| **Parent-Child 归因循环引用**（🆕 v0.6.0） | 低 | A委托B委托C委托A 形成循环归因 | DAG cycle detection + max_depth=4 |
| **Think-Time 成本模型滞后**（🆕 v0.6.0） | 中 | Provider 暗改推理价格→模型失真 | 通过 actual_charges 异常检测（> 20% deviation → 强制重新校准） |
| **Ed25519 密钥丢失**（🆕 v0.7.0） | 高 | 私钥丢失→所有预算策略锁定，无法修改 | 密钥存储于1Password/YubiKey + 纸质备份 + 紧急恢复流程文档 |
| **Trust Ring 自身崩溃**（🆕 v0.7.0） | 高 | Ring 0 组件崩溃→签名验证失败→所有写操作被误判为非法 | Triple-modular redundancy：Ring 0 至少 3 个独立进程验证（agree≥2 才通过） |
| **Tamper-Evident chain 被 DoS**（🆕 v0.7.0） | 低 | 恶意 agent 制造海量审计事件撑爆 hash chain | 审计事件 rate limit——每秒最多 100 条；超过则降级为统计聚合 |
| **Bootstrapping 卡在 calibrated 出不来的状态**（🆕 v0.7.0） | 中 | 30 天内未收集到 100 个任务→永远不退出校准模式 | Owner 手动 exit-calibration + 使用 default 保守阈值（非 P95） |
| **信任根悖论**（🆕 v0.7.0 不可修复） | — | 整个系统是 AI 构建的——Ring 0 代码也是 AI 生成的。谁保证 Ring 0 代码没有 bug？ | **哲学上限**——100% AI 施工体系无法自证正确性。缓解：Ring 0 代码量最小化（< 200 行），Owner 逐行审计，Hash 冻结后不可再改 |

---

## 8. 盲点全量清单（20+23+13+12+10 = 78 全量）

### 8.1 v0.3.0（#1—#20） | ### 8.2 v0.4.0（#21—#43） | ### 8.3 v0.5.0（#44—#56） | ### 8.4 v0.6.0（#57—#68）

（详见上文各版本对应章节）

### 8.1 v0.3.0 已补齐（#1—#20）

| # | 优先级 | 盲点 | v0.2.0 | v0.3.0 落位 |
|---|:---:|------|:---:|------|
| 1 | 🔴 | Turn/Round 级预算 | ❌ | §2.1 turn_level |
| 2 | 🔴 | Pre-flight 事前拦截 | ❌ | §2.2 Pre-flight Gate |
| 3 | 🔴 | 多模型成本感知路由 | ❌ | §2.3 Model Router |
| 4 | 🔴 | Entity 级成本归因 | ❌ | §2.7 Cost Attribution |
| 5 | 🔴 | Budget Policy as Code | ❌ | §4 config/budget_policy.yaml |
| 6 | 🟠 | Burn Rate 多窗口监控 | ❌ | §2.9 Burn Rate Monitor |
| 7 | 🟠 | 预算可视化/用量焦虑治理 | ❌ | §2.4 L0_notify |
| 8 | 🟠 | 语义缓存层 | ❌ | §2.6 Semantic Cache |
| 9 | 🟠 | Tool/API 级别成本追踪 | ❌ | §2.7 tool_level |
| 10 | 🟠 | 预算回滚/修复通道 | ❌ | §2.4 auto_recovery + §2.2 borrow |
| 11 | 🟠 | Token 价值 ROI | ❌ | §2.8 Token ROI |
| 12 | 🟠 | 厂商价格自动同步 | ❌ | §2.11 Pricing Sync |
| 13 | 🟡 | Reasoning Token 专项预算 | ❌ | §2.1 request_level.reasoning_limit |
| 14 | 🟡 | 循环检测 | ❌ | §2.5→v0.5.0 §2.5 Action History |
| 15 | 🟡 | Budget Pool 弹性共享 | ❌ | §2.10 Budget Pool + §2.1 task_level.pool_share |
| 16 | 🟡 | Forecast vs Actual 偏差分析 | ❌ | §2.12 Consumption Deviation |
| 17 | 🟡 | Soft/Hard 双轨阈值分离 | ❌ | §2.1 五级均为 soft_limit + hard_limit 双轨 |
| 18 | 🟡 | 成本感知自动回升 | ❌ | §2.4 auto_recovery + §2.3 auto_recovery |
| 19 | 🟡 | 模型剩余容量/可用性感知 | ❌ | §2.3 vendor_fallback |
| 20 | 🟡 | 计划消耗 vs 实际消耗偏差 | ❌ | §2.12 Consumption Deviation |

### 8.2 v0.4.0 新补齐（#21—#43）

| # | 优先级 | 盲点 | v0.3.0 | v0.4.0 落位 |
|---|:---:|------|:---:|------|
| 21 | 🔴 | 流式输出事中成本控制（Stream Abort Guard） | ❌ | §2.13 stream_abort_guard |
| 22 | 🔴 | 沉没成本干预（Sunk Cost Intervention） | ❌ | §2.4 L1.5_sunk_cost_warn |
| 23 | 🔴 | Agent 级预算隔离沙箱（per-agent sub-pool） | ❌ | §2.10 per_agent_sub_pool |
| 24 | 🔴 | 环境感知预算 Profile（dev/staging/prod） | ❌ | §2.15 env_aware_budget_profiles |
| 25 | 🔴 | 失败模式的成本独立核算（Outcome Segmentation） | ❌ | §2.7 outcome_level |
| 26 | 🔴 | 输出质量感知的成本决策（Output Quality Gate） | ❌ | §2.14 output_quality_gate |
| 27 | 🔴 | 预算策略可测试性（Policy Sandbox） | ❌ | §2.16 policy_sandbox |
| 28 | 🔴 | 新模型自动发现 + 成本对比通知 | ❌ | §2.11 new_model_discovery |
| 29 | 🟠 | 上下文浪费检测（Context Waste Detection） | ❌ | §2.17 context_waste_detector |
| 30 | 🟠 | 批次处理预算折扣路由（Batch Routing） | ❌ | §2.3 batch_routing |
| 31 | 🟠 | 模型级联方向修正（最低优先→质量不达标才升级） | ❌ | §2.3 escalation_chain |
| 32 | 🟠 | Provider Token 计数差异归一化 | ❌ | §2.11 token_normalization |
| 33 | 🟠 | Owner 临时提额令协议（Override Protocol） | ❌ | §3 one_person_maintenance.one_click_rollback |
| 34 | 🟠 | 成本数据生命周期管理（Data Retention） | ❌ | §2.7 data_retention |
| 35 | 🟠 | Rate Limit / 429 响应的浪费追踪 | ❌ | §2.9 rate_limit_impact |
| 36 | 🟠 | 预算耗尽用户沟通协议 | ❌ | §2.4 L5_halt.user_communication |
| 37 | 🟡 | 冷启动成本 vs 稳态成本分离 | ❌ | §2.17 cold_start_allowance |
| 38 | 🟡 | Token 使用结构异常检测（Distribution Shift） | ❌ | §2.9 distribution_shift |
| 39 | 🟡 | 第三方 API Passthrough 成本聚合 | ❌ | §2.7 tool_level.passthrough_cost |
| 40 | 🟡 | 预算策略版本管理与回滚 | ❌ | §2.16 policy_versioning |
| 41 | 🟡 | LLM-as-Judge 预算独立核算 | ❌ | §2.7 judge_cost |
| 42 | 🟡 | 自托管/本地模型混合预算模型 | ❌ | §2.17 local_model_cost_model |
| 43 | 🟡 | 多Provider同Tier内least-cost路由 | ❌ | §2.3 cross_provider_least_cost |

### 8.3 v0.5.0 新补齐（#44—#56）

| # | 优先级 | 盲点 | v0.4.0 | v0.5.0 落位 |
|---|:---:|------|:---:|------|
| 44 | 🔴 | **Time Budget 三维——独立 wall-clock 预算（Oracle Runtime Budget Guardrails）** | ❌ | §2.1 time_budget |
| 45 | 🔴 | **Narrow/Reroute 自适应干预（Oracle 2026——非 degrade/stop 二元）** | ❌ | §2.4 adaptive_interventions |
| 46 | 🔴 | **自修复成本螺旋检测（self-correction spiral——自治编码最大隐性风险）** | ❌ | §2.5 self_correction_spiral |
| 47 | 🔴 | **Timeout Guard——独立 asyncio daemon timer（AgentGuard 三大 guard）** | ❌ | §2.20 timeout_guard |
| 48 | 🔴 | **指令膨胀检测——AGENTS.md/blueprint 被动膨胀（Boris Cherny 14%）** | ❌ | §2.18 instruction_bloat_detector |
| 49 | 🔴 | **对话历史税检测——加权衰减 + 有效引用率（Boris Cherny 13%）** | ❌ | §2.19 conversation_history_tax_detector |
| 50 | 🟠 | **Provider Tier 容量感知——Anthropic 4-Tier RPM/TPM 约束路由** | ❌ | §2.9 provider_tier_awareness |
| 51 | 🟠 | **长上下文隐藏定价感知——超过阈值自动溢价计入成本预估** | ❌ | §2.11 long_context_pricing |
| 52 | 🟠 | **Loop Detector→Action History with Dedup——语义指纹 + 效果去重** | ❌ | §2.5 action_history |
| 53 | 🟠 | **跨 Session 预算储蓄——轻量周省的钱可救急重周** | ❌ | §2.10 cross_session_savings |
| 54 | 🟡 | **输出无差异去重——修改文件但 diff 为空的无效操作** | ❌ | §2.5 no_effect_chain |
| 55 | 🟡 | **成本-延迟 Tradeoff（Latency Budget）** | ❌ | §8.4 纳入 v0.6.0 评估——需要延迟监控基建 |
| 56 | 🟡 | **多 Provider 归属记账——同一 Tier 内哪个 Provider 花得最多** | ❌ | §2.3 cross_provider + §2.7 attribution |

### 8.4 v0.6.0 新补齐（#57—#68）

| # | 优先级 | 盲点 | v0.5.0 | v0.6.0 落位 |
|---|:---:|------|:---:|------|
| 57 | 🔴 | **Self-Budget——Budget Enforcer 自身运营成本从未被预算（SUPERVISORAGENT LLM-free）** | ❌ | §2.21 self_budget |
| 58 | 🔴 | **Token Spiral EWS——上下文膨胀/工具链扩张/深度爆炸/时间递增四维早期预警** | ❌ | §2.22 token_spiral_ews |
| 59 | 🔴 | **MAS Context Poisoning Cascade——上游幻觉→下游指数成本放大** | ❌ | §2.23 poisoning_cascade_detector |
| 60 | 🔴 | **Hierarchical Parent-Child Agent 成本归因——委托链树状成本** | ❌ | §2.24 parent_child_attribution |
| 61 | 🔴 | **Reasoning Think-Time 成本感知——推理 token 不可见但可计费** | ❌ | §2.25 think_time_cost_model |
| 62 | 🔴 | **Workflow-Level Budget Cap——跨Session workflow 独立预算** | ❌ | §2.1 L3.5 workflow_level |
| 63 | 🟠 | **LLM-Free Guard 升级路径——scaffold→stable 渐进降本** | ❌ | §2.25 guard_upgrade_path |
| 64 | 🟠 | **Guard Efficiency Ratio——guard 自耗 vs 节省 token 比** | ❌ | §2.21 guard_efficiency |
| 65 | 🟠 | **Graceful Narrow 恢复成本追踪——跳过 80% 后恢复的成本** | ❌ | §2.4 Narrow 的 resume_cost 字段 |
| 66 | 🟠 | **Spiral Score 综合评分——Pearson r + 单调递增加权** | ❌ | §2.22 spiral_score |
| 67 | 🟡 | **Observation Provenance DAG——幻觉信息源链追踪** | ❌ | §2.23 chain_of_faith |
| 68 | 🟡 | **Human Checkpoint Budget 强制——里程碑审查点预算执行** | ❌ | §8.5 纳入 v0.7.0评估 |

### 8.5 v0.7.0 新补齐（#69—#78）——信任根 & 抗对抗

| # | 优先级 | 盲点 | v0.6.0 | v0.7.0 落位 |
|---|:---:|------|:---:|------|
| 69 | 🔴 | **Runtime Trust Rings——Budget Enforcer 内部信任分级（Microsoft Agent Governance Toolkit）** | ❌ | §2.26 runtime_trust_rings |
| 70 | 🔴 | **Tamper-Evident Audit Trail——append-only SHA-256 hash chain** | ❌ | §2.27 tamper_evident_audit |
| 71 | 🔴 | **IPI-Aware Budget Defense——Forcepoint X-Labs 10 种 IPI 载荷防御** | ❌ | §2.28 ipi_aware_budget_defense |
| 72 | 🔴 | **Formal Fail-Mode Specification——Budget Enforcer 崩溃时的行为定义** | ❌ | §2.29 fail_mode_specification |
| 73 | 🔴 | **Bootstrapping Calibration Phase——Day 0→30 渐进收紧（避免 bootstrap paradox）** | ❌ | §2.30 bootstrapping_calibration |
| 74 | 🟠 | **Cold Start Anti-Abuse——Session 重启速率限制** | ❌ | §2.29 cold_start_anti_abuse |
| 75 | 🟠 | **Adversarial Testing Mandate——5 项对抗测试必须通过** | ❌ | §2.29 adversarial_testing_mandate |
| 76 | 🟠 | **Budget Policy Signing——Ed25519 签名验证写操作** | ❌ | §2.28 critical_actions_require_signing |
| 77 | 🟡 | **Supply Chain Budget Isolation——第三方工具独立预算子池** | ❌ | §8.6 纳入 v0.8.0 评估 |
| 78 | 🟡 | **Trust Ring Redundancy——Ring 0 triple-modular redundancy** | ❌ | §2.26 间接覆盖（见风险登记缓解） |

### 8.6 暂缓能力（哲学上限——无法在当前范式下 100% 解决）

| # | 能力 | 暂缓原因 |
|---|------|---------|
| 79 | **信任根悖论**——AI 构建的 Ring 0 代码如何自证正确性 | 哲学上限：100% AI 施工体系无法自证正确性。缓解：Ring 0 代码量最小化（< 200行），Owner 逐行审计，Hash 冻结 |
| 80 | Latency Budget（成本-延迟 Tradeoff） | 需要延迟监控基建 |
| 81 | Human Checkpoint Budget Enforcement | 需要 task lifecycle 框架配合 |
| 82 | Multi-Provider 实时竞价路由 | 单人场景用量不足以谈判 |
| 83 | Agent Credential Exposure Budget | 需要 credential lifecycle 框架配合 |

---

## 9. 跨模块集成

| 联动模块 | 关系 | 触发条件 | 动作 |
|---------|------|------|------|
| MOD-INF-001 Capacity Assurance | Kill Switch 联动 + Degradation 联动 | L6 kill_switch 触发 / 降级链执行 | 调用全局熔断 / 调用 degradation_chain |
| MOD-INF-008 Context Engine | 上下文压缩 + 浪费检测联动 | L3 compress + waste_ratio > 60% | DocCompressor aggressive 模式 / 优化选择策略 |
| MOD-INF-006 Task System | 任务预算字段 + 状态机预算联动 | 任务预算/状态变更 | 读取任务预算 + 状态联动 |
| MOD-INF-020 Audit Trail | 审计写入 | 每次降级/熔断/Borrow/Abort | 写入审计事件 |
| MOD-INF-022 Escalation | 升级 | 硬停止 + Kill Switch | 触发升级通知 Owner |
| **MOD-INF-023 Drift Detector**（🆕 v0.4.0） | 漂移预算信号 | 配置漂移对预算的影响 | 调用漂移检测 + 预算影响评估 |
| **MOD-MASTER-001 任务系统**（🆕 v0.4.0） | Batch 路由 | task.urgency=low | 自动标记走 Batch API |
| **Git Pre-commit Hook**（🆕 v0.4.0） | 策略快照 | git commit | 自动快照 budget_policy.yaml 到版本历史 |
| **LiteLLM Registry**（🆕 v0.4.0） | 新模型发现 + 定价同步 | daily sync 发现新 model_id | 评估 + 写摘要 + 通知 Owner |
| **LiteLLM Pricing Strategy Sync**（🆕 v0.5.0） | 长上下文定价策略同步 | daily sync 检测 pricing strategy 变化 | 更新 non-linear pricing threshold |
| **Context Engine v2**（🆕 v0.5.0） | 历史税加权衰减 + 指令膨胀精简 | history_tax_ratio > 5× OR instruction_growth > 20% | DocCompressor 加权衰减 + 生成精简建议 |
| **SUPERVISORAGENT LLM-Free Filter**（🆕 v0.6.0） | LLM-free 触发——仅在必要时升级 LLM-dependent | budget_policy LLM-free 阶段提升 | guard 类型从 LLM-dependent → LLM-free |
| **Provenance DAG**（🆕 v0.6.0） | 幻觉信息源链追踪——dependency graph | agent output 包含 claim 时 | 追加到 observation provenance DAG |
| **Agent Delegation Registry**（🆕 v0.6.0） | 记录 parent-child 委托关系 | 每次 agent-to-agent call | 记录 delegation edge + 写入 attribution |
| **MOD-INF-014 LLM Security Gateway**（🆕 v0.7.0） | IPI 检测 + 策略文件签名验证 + Trust Ring 隔离 | IPI pattern detected / policy modification attempt | 签名验证网关 + Ring escalation |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | **0.7.0** | **终极取证补丁——信任根 + 抗对抗 + 故障模式**：这是与 v0.6.0 性质完全不同的升级——不是增加功能，而是回答根本问题："一个100%AI构建的系统，凭什么相信它能可信地约束AI？" ①信任根——引入 Runtime Trust Rings（Ring 0-3）：Budget Enforcer 内部组件按信任级别分级执行，Ring 0 仅限 Owner Ed25519 签名代码（kernel 级不可被 AI 修改），Ring 2 为 AI 生成 guards，Ring 3 为受约束的 agent 执行空间；引入 Tamper-Evident Audit Trail——append-only SHA-256 hash chain替代明文 JSONL，每次启动自动验证完整性，hash chain 断裂→系统进入不可信状态并 HALT；引入 Budget Policy Signing——修改 hard_limit/soft_limit、borrow 20%+ 全局预算、解除熔断等写操作必须附带 Ed25519 签名；②抗对抗——引入 IPI-Aware Budget Defense（Forcepoint X-Labs 2026.4 10 种 IPI 载荷防御）：外部数据中检测 budget-related IPI patterns（正则+语义双重匹配），预算关键操作通过签名验证网关；引入 Cold Start Anti-Abuse——Session 重启速率限制（1h 内最多 3 个 Session）+ 日累计冷启动豁免上限 27,500 token；引入 Adversarial Testing Mandate——5 项对抗测试（IPI 注入/cold start abuse/parent-child infinite delegation/stream abort bypass/provider race），Phase experimental→beta 前必须全部通过；③故障模式——引入 Formal Fail-Mode Specification：Budget Enforcer 崩溃时 per-level 的 fail-open/fail-closed 定义（L0 request fail-closed / L4 global fail-closed / L3 session fail-open 限流）+ heartbeat 监控 + 自动恢复；引入 Bootstrapping Calibration Phase——新部署前 30 天为校准期，所有 hard_limit ×3 宽松执行仅告警不阻断，收集 100 任务数据后 P95 自动调参，解决"Day 0 阈值是 AI 猜测→太紧→系统卡死→自学习无法启动"的 bootstrap paradox；新增 6 个文件（trust_ring_manager/tamper_evident_log/ipi_defense/fail_mode_manager/bootstrapping_calibrator/adversarial_tester）；风险登记新增 6 条（含不可修复的"信任根悖论"——AI 构建的 Ring 0 代码如何自证正确性——这是 100% AI 施工体系的哲学上限）；10 项新盲点全量补齐→共 78 项；对标新增 Forcepoint X-Labs/Oktsec/Okta/Microsoft/Gravitee |

| 2026-05-05 | 0.6.0 | **Self-Budget 自耗管控 + 多层安全 + 委托归因升级**：预算级数从五级→七级（新增 L3.5 Workflow 级跨Session workflow 独立预算 + L4.5 Self-Budget 级——Budget Enforcer 自身运营成本上限）；新增 Self-Budget——guards 自身消耗独立追踪 + guard_efficiency ratio（省 token:guard 自耗 < 0.5→自动关闭）+ 每日上限 50K token；新增 Token Spiral EWS——四维早期预警（expanding_context/multiplying_tool_calls/depth_explosion/time_per_turn_growth）+ spiral_score 综合评分（Pearson r + 单调递增）+ 阈值 30/60/80 三级联动降级/Kill；新增 Context Poisoning Cascade Detection——fact_contradiction 交叉引用 + chain_of_faith provenance DAG + cascade_cost_tracker + auto_isolation；新增 Hierarchical Parent-Child Agent 成本归因——delegation_tree DAG + attribution_rules（direct/delegated/root_cause）+ delegation_efficiency 指标；新增 Reasoning Think-Time Cost Model——Anthropic extended thinking + OpenAI o1/o3 hidden reasoning token 推算 + auto_switch when thinking > 2× output；新增 LLM-Free Guard 升级路径——scaffold→experimental→beta→stable→self_calibrating 五阶段渐进 LLM-free 降本（对标 SUPERVISORAGENT ICLR 2026）；12 项新盲点全量补齐 → 共 68 项盲点全量覆盖；对标更新（SUPERVISORAGENT + TechAhead + Vibe Coding 2026 costs） |
| 2026-05-05 | **0.5.0** | **三维升级——Token/Cost→Token/Cost/Time 三维预算**：预算体系从 Token/Cost 双维升级为三维——新增 Time Budget（Request 2min/Turn 5min/Task 1h/Session 8h 独立 wall-clock 预算）+ Timeout Guard（独立 asyncio daemon timer——AgentGuard 2026 三大 guard 之一）；降级链从六级增强为八级：新增 Narrow Scope（预算紧张时收窄任务范围只做核心 20%）+ Reroute Strategy（策略重定向——Pipeline 模式而非一次性大请求）+ Global Timeout Kill（wall-clock 超时熔断）；循环检测全面升级为 Action History with Dedup——新增 semantic_hash/effect_hash/自修复螺旋检测/输出无差异去重（对标 Stanford/MIT Token Economics 论文发现：50% 高成本运行中的文件读写是重复的）；新增 Instruction Bloat Detector——检测 AGENTS.md/budget_policy.yaml 等指令文件膨胀（Boris Cherny 400h Claude 分析：14% token 浪费在指令膨胀上）；新增 Conversation History Tax Detector——对话历史加权衰减 + 有效引用率追踪（Boris Cherny 数据：13% token 浪费在历史税上）；模型路由新增多Provider同Tier内least-cost路由 + Provider Tier 容量感知（Anthropic 4-Tier RPM/TPM）；价格同步新增长上下文隐藏定价感知——超过 200K context 自动计入溢价成本预估；Budget Pool 新增跨 Session 预算储蓄——轻量周省的钱自动入储蓄池救急重周；13 项新盲点全量补齐 → 共 56 项盲点全量覆盖；对标更新（Oracle Runtime Budget Guardrails + AgentGuard + Stanford Token Economics + TokenFence + Boris Cherny Claude Anatomy）|
| 2026-05-05 | 0.4.0 | **补完升级——全生命周期控制**：模型路由方向反转（默认 tier_0 免费→质量不达标才升级）+ Batch 路由（非实时任务自动走 Batch API 享 50% 折扣）；六级降级链新增 L1.5 沉没成本干预 + 预算耗尽用户沟通协议；新增 Stream Abort Guard（流式输出中途每 500 token 预算二次确认 + 部分响应保存）；新增 Output Quality Gate（前 200/300 token 快速质量校验——格式/相关性/幻觉）；新增 ENV Profile（dev/staging/prod 三套预算策略——dev 永远锁在免费模型）；新增 Agent 级子池隔离（per-agent sub-pool——防止失控 Agent 烧掉全部预算）；新增 Budget Policy Sandbox（dry-run 模拟 4 场景 + Policy Versioning/回滚/diff）；新增新模型自动发现（LiteLLM sync 检测 + 自动评估 + 周摘要置顶）；新增上下文浪费检测（sent vs referenced 比例）；新增 Outcome 维度成本归因（成功/失败/部分分离 + LLM-as-Judge 独立核算）；新增 Provider Token 归一化（cl100k_base 基准）；新增 Rate Limit 浪费追踪 + Distribution Shift 结构异常检测；新增冷启动成本豁免 + 自托管模型成本模型 + 数据生命周期管理 + 第三方 API Passthrough 聚合；跨模块联动扩展（Output Validator/任务系统/LiteLLM Registry/Git hook）；风险登记更新 5 条；23 项新增盲点全量补齐 → 共 43 项盲点全量覆盖 |
| 2026-05-05 | 0.3.0 | **全量重构**：三级→五级预算体系（新增 Request/Turn 级）；新增 Pre-flight Gate 事前拦截门；新增 Model Router（Tier 0→3 成本感知路由+厂商故障切换）；四级→六级降级链（新增模型切换+Kill Switch+成本感知回升+反螺旋）；新增循环检测器（工具调用指纹）；新增语义缓存（Prompt/Tool/Embedding 三层）；新增成本归因（Entity/Tool/Feature 三级+Weekly Showback）；新增 Token ROI 模型；新增 Burn Rate 多窗口监控；新增 Budget Pool 弹性共享；新增厂商价格自动同步；新增计划vs实际消耗偏差校准；Solo Maintainer 特异性优化（自学习阈值/自静默告警/周自动摘要）；Budget Policy as Code（独立 YAML）；软硬双轨阈值分离；20 项盲点全量补齐 |
| 2026-05-05 | 0.2.0 | 决策写入：D-024-01 四级自动降级；成本审计改为 JSONL |
| 2026-05-05 | 0.1.0 | 初始创建——三级预算体系 + 降级策略 + 预算执行器 |


---

## 施工落盘确认（2026-05-08 审计修正 · P0/P1 修复完成）
| 维度 | 状态 |
|------|------|
| construction_progress | phase_1_partial→phase_1_加固中（Phase 0 Skeleton + Phase 1 治理桥接已通过，P1 核心模块 4/4 已落盘，Phase 1.5/2 待施工） |
| 源码路径 | `src/zephyr/budget_enforcer/ (8 文件) + governance/budget_enforcer/ (3 文件)` |
| 源码文件数 | **11 个 .py**（蓝图 §4 计划 31 文件，完成率 **35.5%** ← 修复前 22.6%） |
| 新增 P1 模块 | `budget_tracker.py`, `degradation_manager.py`, `model_router.py`, `timeout_guard.py` |
| 配置文件 | `config/capacity/token_budget.yaml`（Capacity Assurance SSoT）+ ✅ `config/budget_policy.yaml`（Budget Policy SSoT 种子版 v0.1.0-seed） |
| 门禁 | ✅ GCT-024 `gates/gct_024_budget_enforcer.yaml`（7 checks: 硬4 + 软2 + info1） |
| 关键入口 | `governance/budget_enforcer/alerts.py` |
