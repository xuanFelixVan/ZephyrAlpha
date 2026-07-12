---
module_id: MOD-INF-024
submodule_path: src/zephyr/governance/budget_engine.py
title: Token/Cost/Time 三维预算强制执行蓝图 — 七级预算 + 全生命周期 + 信任根 + 抗对抗
doc_type: blueprint
status: Active
version: 0.7.0
layer: L0_infrastructure
functional_domain: budget_enforcement
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: 2026-05-05
valid_from: 2026-05-05
ttl: permanent
construction_progress: partially_implemented
belongs_to: MOD-MASTER_BLUEPRINT
summary: ZephyrAlpha Token/Cost/Time 三维预算强制执行蓝图 v0.7.0——终极取证补丁。前6轮补齐68项功能性盲点，本轮补充3个结构面缺陷：①信任根——AI构建的Budget Enforcer谁来审计？引入Runtime Trust Rings（Ring 0-3）+ Tamper-Evident Audit Trail（append-only hash chain）+ Budget Policy Signing；②抗对抗——前6轮假设agents是合作的，Forcepoint X-Labs 2026披露10种IPI攻击载荷可在<300ms绕过guardrails。引入IPI-Aware Budget Defense + Cold Start Anti-Abuse + Adversarial Testing Mandate；③故障模式——Budget Enforcer崩溃时fail-open还是fail-closed？引入Formal Fail-Mode Specification + Bootstrapping Calibration Phase（Day 0→30渐进收紧）。对标补充：Forcepoint X-Labs IPI十大攻击载荷 (2026.4) + Oktsec Kill Chain (2026.3) + Okta Agent Bypass研究 (2026.5) + Microsoft Agent Governance Toolkit Runtime Rings + Gravitee AI Agent Security 2026。v0.3.0 20+v0.4.0 23+v0.5.0 13+v0.6.0 12+v0.7.0 10=78项盲点全量补齐。这并不是增加更多功能——而是补上'一个AI构建的系统如何可信地约束AI'这个根本性问题。
tags: [budget, token, cost, time, enforcement, degradation, infrastructure, pre-flight, in-flight, self-budget, model-router, cache, burn-rate, roi, chargeback, loop-detection, pricing-sync, stream-abort, quality-gate, env-profile, agent-sub-pool, policy-sandbox, waste-detection, batch-routing, model-discovery, timeout-guard, instruction-bloat, history-tax, provider-tier, cost-spiral, cross-provider, narrow-reroute, spiral-ews, poison-cascade, parent-child-attribution, workflow-budget, resume-cost, think-time, guard-efficiency, trust-ring, tamper-evident, fail-mode, bootstrapping, ipi-defense, anti-abuse, adversarial-testing, supply-chain-isolation]
priority: P2
activation_phase: current
runtime_plane: hot
depends_on:
- {target: MOD-LLM_SECURITY", at: "§2", why: "LLM Security Gateway——IPI检测 + 策略文件签名验证 + Trust Ring 隔离"}
responsibility_domain: 
design_maturity: design
build_status: generated
---
ssot_claims:
  - claim: "Token/Cost/Time 三维预算策略唯一真源"
    scope: "config/budget_policy.yaml + src/zephyr/governance/budget_engine.py"
    negative: "MOD-INF-001 token_budget.yaml 为 deprecated 引用，非 SSoT"
  - claim: "预算降级链唯一执行者"
    scope: "degradation_manager.py + pre_flight_gate.py"
    negative: "其他模块不得自行实现降级逻辑"
  - claim: "模型成本路由唯一决策者"
    scope: "model_router.py + cost_router.py"
    negative: "MOD-RESOURCE_OPTIMIZATION_ENGINE Resource Optimization 管 CPU/Memory，不管 Token/Cost"
consumer_registry:
  - tier: "hard"
    consumers: ["MOD-INF-022 Escalation", "MOD-INF-001 Capacity Assurance", "MOD-LLM_SECURITY LLM Security"]
  - tier: "soft"
    consumers: ["MOD-CONTEXT_ENGINE Context Engine", "MOD-TASK_SYSTEM Task System", "MOD-INF-015 System Telemetry"]
  - tier: "optional"
    consumers: ["MOD-RESOURCE_OPTIMIZATION_ENGINE Resource Optimization", "MOD-INF-034 Model Capability Exam"]
actual_disk_path: "src/zephyr/governance/budget_engine.py"
last_updated: "2026-05-18"
last_verified: "2026-05-18"
generation: 3
stability: evolving
---

## MOD-GOVERNANCE 集成契约锚点

> 权威定义见 [`../../_domain_governance/blueprint.md`](../../_domain_governance/blueprint.md) §3。

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-006 | 产出方（预算事件 → Escalation） | MOD-INF-022 |

# Token/Cost/Time 三维预算强制执行蓝图 — 七级预算 + 全生命周期 + 信任根

> **module_id**: MOD-INF-024 | **version**: 0.7.0 | **status**: draft | **layer**: cross_layer

> **对标**：Forcepoint X-Labs IPI (2026.4) | Oktsec Kill Chain (2026.3) | Okta Agent Bypass (2026.5) | Microsoft Runtime Rings | SUPERVISORAGENT (ICLR 2026) | TechAhead Guardrails | Gravitee AI Security 2026 | Oracle Budget Guardrails | AgentGuard | Stanford Token Economics | TokenFence | Anthropic 4-Tier | Boris Cherny Claude Anatomy

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-024 |
| 代码落位 | `src/zephyr/governance/budget_engine.py` |
| 运行时平面 | Hot memory（Pre-flight Gate + In-flight Stream Abort Guard + 调用后 Runtime Enforcer——覆盖调用前→调用中→调用后全生命周期） |
| 核心职责 | 强制执行 Token/Cost 预算——超预算自动降级，零人工介入；事后成本归因 + ROI 分析 |

### 1.2 核心职能（一句话）

**Budget Enforcer 是系统的财务总监 + 采购经理**——AI 不能无限消耗 token，超预算自动降级；同时在多个模型和供应商之间智能路由，以最低成本完成任务。全程自动，不需要 Owner 介入。

### 1.3 v0.7.0 升级摘要（终极取证补丁）

| 版本 | 信任模型 | 抗对抗 | 故障模式 | 审计完整性 |
|------|------|:---:|------|:---:|
| v0.6.0 | 无条件信任Budget Enforcer | ❌ 假设agents合作 | ❌ 未定义 | 明文JSONL可篡改 |
| **v0.7.0** | **Runtime Trust Rings(0-3)** | **IPI Defense + Cold Start Anti-Abuse + Adversarial Test** | **Formal Fail-Open/Closed** | **Tamper-Evident hash chain** |

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-024`

| 文件 | 蓝图章节 | 存在性 | 归属 |
|------|---------|--------|------|
| `budget_engine.py` | §2.1-2.4 | ✅ 已实现 | 核心 |
| `budget_tracker.py` | §2.1 | ✅ 已实现 | 核心 |
| `budget_models.py` | §2.1 | ✅ 已实现 | 数据模型 |
| `budget_profile_manager.py` | §2.15 | ✅ 已实现 | 配置 |
| `token_budget.py` | §2.1 | ✅ 已实现 | 三维预算 |
| `cost_budget.py` | §2.1 | ✅ 已实现 | 三维预算 |
| `context_budget.py` | §2.1 | ✅ 已实现 | 三维预算 |
| `degradation_manager.py` | §2.4 | ✅ 已实现 | 降级 |
| `model_router.py` | §2.3 | ✅ 已实现 | 路由 |
| `cost_router.py` | §2.3 | ✅ 已实现 | 成本路由 |
| `pre_flight_gate.py` | §2.2 | ✅ 已实现 | 门控 |
| `timeout_guard.py` | §2.20 | ✅ 已实现 | 守卫 |
| `stream_abort_guard.py` | §2.13 | ✅ 已实现 | 守卫 |
| `output_quality_gate.py` | §2.14 | ✅ 已实现 | 守卫 |
| `burn_rate_monitor.py` | §2.9 | ✅ 已实现 | 监控 |
| `spiral_ews.py` | §2.22 | ✅ 已实现 | 监控 |
| `action_history.py` | §2.5 | ✅ 已实现 | 去重 |
| `semantic_cache.py` | §2.6 | ✅ 已实现 | 缓存 |
| `cost_attributor.py` | §2.7 | ✅ 已实现 | 归因 |
| `parent_child_attributor.py` | §2.24 | ✅ 已实现 | 归因 |
| `roi_calculator.py` | §2.8 | ✅ 已实现 | ROI |
| `pricing_sync.py` | §2.11 | ✅ 已实现 | 定价 |
| `policy_sandbox.py` | §2.16 | ✅ 已实现 | 策略 |
| `context_waste_detector.py` | §2.17 | ✅ 已实现 | 检测 |
| `conversation_tax_detector.py` | §2.19 | ✅ 已实现 | 检测 |
| `instruction_bloat_detector.py` | §2.18 | ✅ 已实现 | 检测 |
| `think_time_model.py` | §2.25 | ✅ 已实现 | 推理成本 |
| `self_budget_tracker.py` | §2.21 | ✅ 已实现 | 自预算 |
| `trust_ring_manager.py` | §2.26 | ✅ 已实现 | 信任环 |
| `tamper_evident_log.py` | §2.27 | ✅ 已实现 | 防篡改 |
| `ipi_defense.py` | §2.28 | ✅ 已实现 | IPI防御 |
| `poison_cascade_detector.py` | §2.23 | ✅ 已实现 | 投毒检测 |
| `fail_mode_manager.py` | §2.29 | ✅ 已实现 | 故障模式 |
| `bootstrapping_calibrator.py` | §2.30 | ✅ 已实现 | 校准 |
| `adversarial_tester.py` | §2.29 | ✅ 已实现 | 对抗测试 |
| `alerts.py` | §2.9 | ✅ 已实现 | 告警模型 |
| `bridges/alerts.py` | G-CT-006 | ✅ 已实现 | 契约桥接 |
| `bridges/rbac_bridge.py` | G-CT-007 | ✅ 已实现 | 契约桥接 |
| `tco_model.py` | §2.7 | ✅ 已实现 | TCO |
| `bandwidth_optimizer.py` | §2.17 | ✅ 已实现 | 带宽优化 |
| `context_manager.py` | §2.17 | ✅ 已实现 | 上下文常量 |
| `context_recycling.py` | §2.17 | ✅ 已实现 | 上下文回收 |
| `daily_ops.py` | §3 | ✅ 已实现 | 日常操作 |
| `ops_foundation.py` | §3 | ✅ 已实现 | 运维基础 |
| `time_sync.py` | §2.20 | ✅ 已实现 | 时间同步 |
| `rbac_bridge.py` | G-CT-007 | ✅ 已实现 | RBAC桥接(旧版) |
| `config/budget_policy.yaml` | §2.1 | ✅ 已实现 | SSoT配置 |

### §0.4 SSoT 与责任唯一性

| SSoT 声明 | 真源位置 | 冲突方 | 裁定 |
|-----------|---------|--------|------|
| Token/Cost/Time 预算策略 | `config/budget_policy.yaml` | `已删除`(MOD-INF-001) | **024 为 SSoT**，001 已标记 deprecated |
| 预算降级执行 | `degradation_manager.py` | 无冲突 | — |
| 模型成本路由 | `model_router.py` + `cost_router.py` | 无冲突 | — |

---

## §1 设计背景与目标

### §1.1 背景

AI Agent 系统中，LLM API 调用是主要成本驱动因素。无预算控制→成本失控→系统不可持续。Solo Maintainer 场景下，无人值守时预算超限=直接经济损失。

### §1.2 目标范围

| 包含 | 排除 |
|------|------|
| Token/Cost/Time 三维预算策略定义与执行 | CPU/Memory/Disk 资源预算 |
| 五级预算体系 + 七级降级链 | 容量规划（MOD-INF-001） |
| Pre-flight Gate 事前拦截 | LLM 调用安全（MOD-LLM_SECURITY） |
| Model Router 成本路由 | 模型能力评测（MOD-INF-034） |
| Stream Abort Guard 事中控制 | 上下文压缩策略（MOD-CONTEXT_ENGINE） |
| Trust Ring + Tamper-Evident Audit | RBAC 权限控制（MOD-INF-018） |

### §1.7 典型场景

| 场景 | 触发 | 预算行为 |
|------|------|---------|
| 日常 AI Session | session_startup | 加载策略→pre-flight check |
| 批量治理脚本 | Phase Manager gate | per-script budget gate |
| Agent 委托链 | A2A Protocol | per-agent sub-pool + parent-child attribution |
| 预算超限 | record_consumption | 降级链推进→Escalation 通知 |
| IPI 攻击 | ipi_defense 检测 | 阻断→审计→Trust Ring 隔离 |

---

## §2 模块边界

### §2.1 职责边界

| 包含（本模块负责） | 排除（本模块不负责） | 归属 |
|-------------------|---------------------|------|
| Token/Cost/Time 三维预算策略定义与执行 | CPU/Memory/Disk/Process 资源预算 | MOD-RESOURCE_OPTIMIZATION_ENGINE |
| 五级预算体系 (Global→Session→Task→Turn→Request) | 容量规划与容量保障 | MOD-INF-001 |
| 六级降级链 (L0→L6) 自动执行 | 升级/委托决策 | MOD-INF-022 |
| Pre-flight Gate 事前拦截 | LLM 调用安全（注入检测/内容过滤） | MOD-LLM_SECURITY |
| Model Router 成本路由 | 模型能力评测 | MOD-INF-034 |
| Stream Abort Guard 事中控制 | 上下文压缩策略 | MOD-CONTEXT_ENGINE |
| Burn Rate 监控 | 系统遥测指标聚合 | MOD-INF-015 |
| 成本归因 + ROI | 审计日志存储 | MOD-INF-020 |
| Trust Ring 信任分级 | RBAC 权限控制 | MOD-INF-018 |
| Tamper-Evident Audit | 审计编排 | MOD-INF-020 |

### 职责唯一性声明

| 声明 | 判定 |
|------|------|
| 本模块是 Token/Cost/Time 预算执行的唯一真源 | ✅ 无其他模块实现同等功能 |
| 本模块的降级链是预算降级的唯一执行路径 | ✅ 其他模块通过 G-CT-006 契约调用 |
| config/budget_policy.yaml 是预算策略的唯一配置源 | ✅ token_budget.yaml 已标记 deprecated |

---

## §3 架构设计

### §3.2 数据流

| 上游 | 数据 | 处理 | 下游 |
|------|------|------|------|
| LLM API 调用请求 | estimated_tokens/cost/time | PreFlightGate 三维检查 | ALLOW/WARN/DENY |
| LLM API 响应 | actual_tokens/cost/time | record_consumption 累加 | BurnRateMonitor + DegradationManager |
| DegradationManager | usage_ratio > threshold | advance_degradation | Escalation(G-CT-006) + AuditTrail |
| PricingSync | LiteLLM price data | sync_from_litellm | model_pricing.yaml |
| IPI Defense | 外部输入文本 | regex+semantic scan | BLOCK/ALLOW + TrustRing |

### §3.3 状态生命周期

| 状态 | 进入条件 | 退出条件 | 降级动作 |
|------|---------|---------|---------|
| L0_NORMAL | usage < 50% | usage ≥ 50% | — |
| L1_NOTIFY | usage ≥ 50% | usage < 50% 持续 cooldown | 通知 |
| L2_WARNING | usage ≥ 70% | usage < 50% 持续 cooldown | 告警+模型切换准备 |
| L3_MODEL_SWITCH | usage ≥ 80% | usage < 50% 持续 cooldown | 切换到低 Tier 模型 |
| L4_COMPRESS | usage ≥ 85% | usage < 50% 持续 cooldown | 压缩上下文 |
| L5_MINIMAL | usage ≥ 95% | usage < 50% 持续 cooldown | 最小化输出 |
| L6_HALT | usage ≥ 100% | Owner 手动恢复 | 全局熔断+Kill Switch |

---

## §8 安全考量

| 威胁 | 影响 | 缓解 | 验证 |
|------|------|------|------|
| IPI 注入攻击 | 绕过预算控制 | IPIDefense 6类模式+0.75阈值 | adversarial_tester |
| 预算策略篡改 | 提高限额 | TrustRing(Ring0=Owner签名)+Ed25519 | tamper_evident_log |
| 审计日志篡改 | 掩盖超限 | SHA-256 hash chain+启动自检 | tamper_evident_log.verify() |
| Cold Start 滥用 | 重启绕过限制 | 1h内≤3 Session+27500 token上限 | adversarial_tester |
| 委托链无限递归 | 预算耗尽 | max_depth=5+bottleneck检测 | parent_child_attributor |
| 流式输出绕过 | 超预算输出 | 每500token checkpoint+微交易 | stream_abort_guard |

---

## §9 测试策略

| 测试类型 | 覆盖范围 | 通过标准 |
|---------|---------|---------|
| 单元测试 | BudgetEngine/BudgetTracker/DegradationManager/ModelRouter/PreFlightGate/CostBudget/ContextBudget/PricingSync | tests/governance/test_budget_enforcer_submodules.py |
| 集成测试 | G-CT-006 Escalation桥接 + G-CT-007 RBAC桥接 | check_budget_health.py exit 0 |
| 对抗测试 | 5项：IPI注入/cold_start/delegation_chain/stream_abort/race_condition | adversarial_tester.run_all() 全部 PASS |
| 健康检查 | 8项：engine/pre_flight/dimensions/policy/escalation/degradation/tamper/burn_rate | check_budget_health.py HEALTHY |
| 蓝图对齐 | API签名/依赖/版本/时态内容 | check_blueprint_code_alignment.py --warn-only |

---

## 2. 核心架构

### 2.1 五级预算体系（Token + Cost + Time 三维）

> **决策 D-024-02（v0.5.0 修订）**：从 Token/Cost 双维升级为 Token/Cost/Time 三维。Stanford Token Economics 论文 (2026.4) 验证——wall-clock 时间和 token 消耗仅呈弱相关，必须独立监控。Oracle Runtime Budget Guardrails 明确提出 "given elapsed time, observed cost, and remaining work estimate, decide to continue/narrow/reroute/escalate/stop"。

```yaml
budget_levels:
  global_level: { soft: 500000, hard: 750000, on_soft: "全局通知+建议暂停", on_hard: "只读模式", borrow_pool: true }
  session_level: { soft: 8000, hard: 12000, on_soft: "WARNING+/compact", on_hard: "降级最小上下文" }
  task_level: { soft: 4000, hard: 6000, on_soft: "暂停+建议拆分", on_hard: "委托新会话", pool_share: true }
  turn_level: { soft: 1500, hard: 2500, on_soft: "检查循环+简化", on_hard: "强制终止+循环指纹" }
  request_level: { input_limit: 32000, output_limit: 4096, reasoning_limit: 8000, tool_calls_limit: 10, on_exceed: "截断+拆分" }
time_budget:
  dimensions: { request_timeout: 120, turn_timeout: 300, task_timeout: 3600, session_timeout: 28800 }
  enforcement: "Timeout Guard（§2.20）"
  visualization: "⏱任务:23min/60min(38%) | 💰Token:42K/100K(42%)"
```

### 2.2 Pre-flight Gate（事前拦截门）

> **决策 D-024-03**：专业机构要求 pre-request blocking——在 tokens 被实际消耗之前就拦截。Pre-flight Gate 是 v0.3.0 新增的核心组件，位于每次 API 调用的咽喉位置。

| 参数 | 值 | 约束 |
|------|-----|------|
| checks | global: soft剩余<预估×1.2→DENY; session: hard剩余<预估→DEGRADE; task: hard剩余<预估→DEGRADE; turn: soft剩余<预估→WARN; request_size: input>limit→DENY; cost: 单次>$0.50→DEGRADE | Owner临时提额令可覆盖DENY |
| verdicts | ALLOW / WARN / DEGRADE / DENY / BORROW | — |
| borrow | max_ratio: 0.20; payback: 下次任务少分30% | enabled: true |
| estimator | TikToken + model-specific tokenizer | 误差<10% |

### 2.3 模型路由升级（Model Router）

> **决策 D-024-04（v0.4.0 修订）**：模型路由方向反转——从"默认用高→预算紧张降级到低"改为"默认最低→质量不达标才升级"。专业机构实践（Cost Engineering for Agents, 2025）+ Vibe Coding 社区模型组合拳（需求理解用弱模型→代码生成用强模型→Lint 用免费模型）降本 80%+。

| 参数 | 值 | 约束 |
|------|-----|------|
| strategy | cheapest_first_escalate_on_quality_fail | 默认最低Tier，质量不达标才升级 |
| escalation_chain | tier_0→tier_1(质量不达标, max_cost:$0.01)→tier_2(深度推理, max_cost:$0.05)→tier_3(终审裁决, requires_owner_approval) | v0.4.0方向反转 |
| degradation_override | tier_3→tier_2(global>60%)→tier_1(>80%)→tier_0(>95%) | 预算紧张时压降覆盖升级 |
| batch_routing | 非实时任务走Batch API 50%折扣; max_latency: 24h; eligible: 周报/归因/Lint/格式化/ROI | task.urgency=low→自动batch |
| vendor_fallback | anthropic→openai→google→deepseek→ollama(local) | — |
| cross_provider_least_cost | 同Tier内min(cost) WHERE availability=UP AND quality>=0.7; tie_break: 最高rate limit; quality_weighted: true; refresh: 300s | — |
| long_context_pricing | anthropic: >200K→1.5-2×溢价; openai: >128K potential_trap; action: 成本预估自动纳入 | v0.5.0新增 |

### 2.4 六级自适应降级链

> **决策 D-024-05（v0.4.0 修订）**：新增 L1.5 沉没成本干预——当 Cost-to-Completion Ratio 异常时主动建议放弃。新增预算耗尽用户沟通协议。

| 参数 | 值 | 约束 |
|------|-----|------|
| L0_notify | session>50% OR burn_rate>3×→INFO+显示剩余预算 | auto |
| L1_warning | >70% OR turn soft_limit接近→WARNING+budget_watch | auto |
| L1.5_sunk_cost | cost_to_completion>3× AND 产出<20%→告警建议放弃 | auto; ratio=budget_consumed/output_completion |
| L2_model_switch | >80% OR 单次>$0.50→自动降级Tier-1 | auto; 最高优先——在压缩上下文之前 |
| L3_compress | >85%→DocCompressor aggressive | auto; 联动MOD-CONTEXT_ENGINE |
| L4_minimal | >95%→仅AGENTS.md+当前蓝图§3 | auto |
| L5_halt | >100% hard_limit→只读+审计; 沟通协议: 保存进度+resume checkpoint | auto; ProvenanceStandard |
| L6_kill_switch | 单日>$100 OR 连续5 DENY OR runaway→全局熔断 | auto; 联动MOD-INF-001; 30min自动尝试解除 |
| auto_recovery | burn_rate<1× AND budget<soft×0.6→回升一级; max_recovery: L1; 新会话→完全重置 | anti_spiral: max 1/min; cooldown: 180s |
| narrow_scope | task_budget>70% AND progress<30%→仅完成核心20% | reversible |
| reroute | model_switch≥2次 OR per-request>3×avg→Pipeline模式拆分 | — |
| global_timeout_kill | task/session timeout→IMMEDIATE_ABORT+save checkpoint | 联动§2.20 |

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

| 参数 | 值 | 约束 |
|------|-----|------|
| backend | ChromaDB（复用已有向量库） | 零新增依赖 |
| layer_1_prompt_cache | exact_hash; ttl: 3600s; AES-256 at rest; hit_ratio_target: 0.40 | — |
| layer_2_tool_cache | param_hash; ttl: 300s; hit_ratio_target: 0.30 | — |
| layer_3_embedding_cache | content_hash; ttl: 86400s | 文档嵌入去重 |
| observability | cache_hit_rate / cache_saved_tokens / cache_saved_cost | 每次cache hit写入audit trail |

### 2.7 成本归因体系（Cost Attribution）

> **决策 D-024-08（v0.4.0 修订）**：不知道钱花在哪里的 Budget Enforcer 只做了一半工作。v0.4.0 新增 Outcome 维度（成功/失败/部分分离）——失败消耗和成功消耗的 ROI 完全不同。

| 参数 | 值 | 约束 |
|------|-----|------|
| dimensions | entity_level(agent_id/module_id/phase); tool_level(tool_name/call_count/api_cost/passthrough_cost); feature_level(activity_type/output_files/loc); outcome_level(success\|partial\|failed\|rejected, retry_count, error_category) | v0.4.0新增outcome+passthrough |
| judge_cost | LLM-as-Judge独立子预算; 不计入Task预算; >总成本15%→告警 | v0.4.0新增 |
| showback | 每周自动Markdown报告→docs/_working/audit/cost_reports/; 含Top3 Agent/Tool/Activity/失败消耗/ROI/预测 | — |
| data_retention | raw: 30天(JSONL); aggregated: 12个月(按周SQLite); archival: 年度gzip; cleanup: 每周日03:00 UTC | v0.4.0新增 |
| storage | data/audit/cost-attribution.jsonl（按天切分） | — |

### 2.8 Token ROI 模型

| 参数 | 值 | 约束 |
|------|-----|------|
| outcome_metrics | lines_of_code_per_1k_tokens; files_completed_per_1k_tokens; blueprint_sections_per_1k_tokens; debug_rounds_per_task | Week 1 建立基线 |
| trend_alert | ROI 下降 30% 以上→告警 Owner '施工效率下降，建议检查 Prompt 质量' | — |
| integration | 与 Session Log（docs/_working/audit/session_logs/）联动，自动计算 | — |

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

| 参数 | 值 | 约束 |
|------|-----|------|
| source | LiteLLM model_prices_and_context_window.json | daily 02:00 UTC; 3天同步失败→告警 |
| new_model_discovery | 检测新model_id→拉取能力画像→成本排名→写周摘要; auto_adopt: false | Owner审阅后手动更新 |
| token_normalization | base: cl100k_base; anthropic: 1.05×; gemini: 0.92×; deepseek: 0.98× | 跨模型成本对比前先归一化 |
| long_context_pricing | anthropic: >200K→1.5-2×溢价; openai: >128K potential_trap; action: 成本预估自动纳入 | v0.5.0新增 |

### 2.12 计划消耗 vs 实际消耗偏差

| 参数 | 值 | 约束 |
|------|-----|------|
| workflow | task_start→AI提交plan_estimated_tokens→task_end→对比actual→偏差>30%→写入deviation_events | — |
| calibration | 每模型独立偏差校正系数; 每周基于最近20任务自动更新 | — |

### 2.13 事中控制——Stream Abort Guard

> **决策 D-024-11（🆕 v0.4.0）**：Pre-flight Gate 只能管输入端。流式输出中途无法拦截——如果模型开始输出大量无意义内容，预算已被烧掉。Stream Abort Guard 对流式输出做中间 checkpoint（每 500 token）预算二次确认。

| 参数 | 值 | 约束 |
|------|-----|------|
| lifecycle_position | in_flight（Pre-flight和Post-flight之间） | — |
| checkpoints | 每500 output token检查: 剩余预算<预估完成成本→IMMEDIATE_ABORT; quality<0.3 AND tokens>200→ABORT_AND_RETRY(便宜模型); token>expected×3→ABORT_WITH_WARNING | — |
| partial_output | abort→保存partial_response; 下次调用append到system prompt | — |
| provider_integration | anthropic: stop_reason=max_tokens; openai: finish_reason=length; google: finishReason=MAX_TOKENS; deepseek: 同OpenAI | — |

### 2.14 事中控制——Output Quality Gate

> **决策 D-024-12（🆕 v0.4.0）**：Token ROI 只统计事后产出。但需要实时质量信号——如果 LLM 的前 200 token 输出明显是垃圾（格式错误/幻觉/不相关），应立即 abort + 切模型重试，而不是等到 4000 token 输出完了再判断。

| 参数 | 值 | 约束 |
|------|-----|------|
| lifecycle_position | in_flight | — |
| format_check | first 200 tokens: JSON/XML/代码块/markdown语法→fail→ABORT+追加纠正prompt | — |
| relevance_check | first 300 tokens: embedding similarity(partial, task_prompt)<0.4→ABORT+L1_warning | — |
| hallucination_check | full response: 引用验证(file_path/module_id是否真实)→MARK_FAILED+不计入ROI | — |
| auto_retry | max_retries: 2; attempt_1: same model+'be accurate'; attempt_2: 升级到下一Tier | — |

### 2.15 环境感知预算 Profile

> **决策 D-024-13（🆕 v0.4.0）**：业界标准实践——dev 环境永远只用最便宜模型，prod 才开全能力。Solo maintainer 最容易在 dev 调试时不小心烧掉一周预算。

| 参数 | 值 | 约束 |
|------|-----|------|
| detection | $ZEPHYR_ENV 或自动检测(IDE→dev, CI/CD→staging, deployed→prod) | — |
| development | default: tier_0_free; max: tier_1; daily_cap: $1; task_cap: $0.10; cache: on; audit: minimal | 绝不用付费模型除非显式/switch-model |
| staging | default: tier_1; max: tier_2; daily_cap: $5; task_cap: $0.50; cache: on; audit: standard | — |
| production | default: tier_1; max: tier_3; daily_cap: $10; task_cap: $1.00; cache: on; audit: full | 全能力可用，仍有硬顶 |
| dev_trap_protection | 每次新Task自动重置到Profile default; 持久覆盖需`zephyr env override-production`(二次确认) | — |

### 2.16 预算策略沙盘 + 策略版本管理

> **决策 D-024-14（🆕 v0.4.0）**：你怎么知道五级预算+六级降级不会把系统卡死？预算策略需要在不上线的情况下验证——dry-run 模拟路径。策略变更需要版本管理——改坏了可以回滚。

| 参数 | 值 | 约束 |
|------|-----|------|
| sandbox_trigger | budget_policy.yaml变更后自动执行 OR `zephyr budget sandbox --scenario <name>` | — |
| scenarios | low_complexity(20 lint_fix→全tier_0); medium_load(50 mixed→45/3/2 tier分配); budget_exhaustion(100 heavy→降级链不spiral); runaway_agent(10→sub-pool触顶+spillover截断) | — |
| sandbox_output | budget_sandbox_report.md(通过/警告/失败checklist) | — |
| policy_versioning | storage: config/budget_policy_history/{version}/; auto_version: git commit pre-commit hook; rollback: `zephyr budget policy rollback --version v{N}`; diff: `--v1 v2` | — |

### 2.17 辅助能力——上下文浪费检测 + 冷启动豁免 + 自托管模型成本模型

> **决策 D-024-15（🆕 v0.4.0）**：补充三个之前被忽略的辅助能力——它们不影响核心逻辑，但在 solo maintainer 场景下持续性产生隐性成本。

| 参数 | 值 | 约束 |
|------|-----|------|
| context_waste_detector | metric: referenced_chars/total_context_chars; waste>0.60持续5请求→建议/compact; 联动Context Engine DocCompressor | — |
| cold_start_allowance | 固定入场费: 读蓝图3000+索引2000+policy500=5500 token/session; 计入session预算但不计入task_budget; overridable: true | — |
| local_model_cost_model | electricity: $0.12/kWh; gpu: 200W; throughput: 50 tok/s; cost≈$0.13/MTok; 记为local_cost非api_cost; tier: tier_local | — |

### 2.18 指令膨胀检测（Instruction Bloat Detector）

> **决策 D-024-16（🆕 v0.5.0）**：Boris Cherny 400 小时 Claude 使用分析——14% 的 token 浪费来自膨胀的 CLAUDE.md/AI 指令文件。我们的 Context Waste Detector (§2.17) 追踪 "sent vs referenced"，但指令文件是被动的——它总是被发送但永远不会被"引用"，仅跟踪 referenced 比例会误报。

| 参数 | 值 | 约束 |
|------|-----|------|
| targets | AGENTS.md / budget_policy.yaml / 所有*blueprint.md §1-§2 | — |
| metrics | instruction_token_count; growth_rate_weekly(>20%告警); per_turn_instruction_overhead | — |
| alerts | oversized: >session_budget×0.25; growing: weekly>20%; dominance: overhead>productive_tokens | — |
| auto_compact | enabled: false; suggest: 检测30天未遵守段落→建议删除 | 不自动压缩（可能删有用规则） |

### 2.19 对话历史税检测（Conversation History Tax Detector）

> **决策 D-024-17（🆕 v0.5.0）**：Boris Cherny 数据——13% 的 token 浪费来自对话历史重读。长对话中，历史即使全部压缩后仍占上下文大头。Context Engine 的压缩解决"大小"但没解决"价值"——压缩后的历史 tokens 中可能 80% 对当前任务无价值。

| 参数 | 值 | 约束 |
|------|-----|------|
| tracking | total_history_tokens_sent / history_tokens_referenced / history_tax_ratio(=sent/referenced) | — |
| alert | tax_ratio>5×→WARN+建议/compact-aggressive(仅保留最近3轮摘要) | — |
| decay_model | last_3_turns: 1.0(全保留); turns_4_10: 0.3(仅决策+异常); turns_11+: 0.05(仅摘要) | 联动Context Engine DocCompressor |

### 2.20 Timeout Guard（并行监控线程）

> **决策 D-024-18（🆕 v0.5.0）**：AgentGuard (2026.4) 三大 guard 之一——Timeout Guard = wall-clock kill switch。这是一个独立于预算链的并行线程——不依赖 L0-L6 降级或 Pre-flight Gate，一旦触发即强行 abort。

| 参数 | 值 | 约束 |
|------|-----|------|
| implementation | asyncio独立task→每个Session启动daemon timer | 不经过降级协商流程 |
| session_timer | 28800s(8h)→FORCE_ABORT+保存Action History+resume checkpoint+audit | — |
| task_timer | 3600s(1h)→FORCE_ABORT当前Task+自动委托新Task | — |
| request_timer | 120s(2min)→CANCEL streaming SSE+ABORT; auto_retry: true(不同Provider或模型) | — |

### 2.21 Self-Budget——Budget Enforcer 自身运营成本管控

> **决策 D-024-19（🆕 v0.6.0）**：SUPERVISORAGENT (ICLR 2026) 引入 LLM-free 自适应触发——传统 guards 自身消耗 token 来评估 token 消耗，形成悖论。Budget Enforcer 自身的运作成本（Output Quality Gate 的 LLM 调用、Instruction Bloat 的语义分析、Conversation Tax 的引用追踪）必须被预算。

| 参数 | 值 | 约束 |
|------|-----|------|
| daily_cap | 50000 token | Budget Enforcer自身每日上限 |
| llm_free_guards | format_check(regex) / action_history.dedup(hash) / timeout_guard(timer) / context_waste.sent_count / burn_rate(EMA) | 零成本，优先使用 |
| llm_dependent_guards | relevance_check(tier_0, 500/call) / hallucination_check(tier_0, 1000/call) / bloat_suggest(tier_0, 2000/day) / tax_analysis(tier_0, 1500/day) | 有成本，需配额控制 |
| guard_efficiency | metric: tokens_saved/tokens_consumed; auto_disable: <0.5(花2省1→关闭); weekly_report: true | — |
| self_budget_exceeded | HALT→所有LLM-dependent guards降级为LLM-free仅warn不block | — |

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

| 参数 | 值 | 约束 |
|------|-----|------|
| fact_contradiction | agent输出声称事实vs workspace index/file system矛盾→MARK potentially_poisoned+注入warning到下游agent system prompt | — |
| chain_of_faith | 构建observation provenance DAG; 同一不实引用链1h内触发级联熔断; TTL: 3600s | — |
| cascade_cost_tracker | metric: tokens_spent_on_fixing_poisoned/total; >15% total→WARN建议重启Session | — |
| auto_isolation | 检测到级联→清除potentially_poisoned上下文片段+重新生成 | — |

### 2.24 Hierarchical Parent-Child Agent 成本归因

> **决策 D-024-22（🆕 v0.6.0）**：现代 MAS 中一个 coordinator 可能委托多个 child agents。扁平 entity-level 归因无法展示"哪个 coordinator 的委托模式最贵"。

| 参数 | 值 | 约束 |
|------|-----|------|
| delegation_tree | 每个agent call记录parent_agent_id和cause_agent_id; 结构: DAG(同一child可被多parent委托) | — |
| attribution_rules | direct_cost: 自身LLM API消耗→归于自己; delegated_cost: child消耗按delegation_ratio回溯parent; root_cause_cost: child因parent错误指令增加→超额归于parent | — |
| query_examples | top_delegator: coordinator-A $3(self)+$12(delegated)=$15; delegation_efficiency: child产出/parent委托成本 | — |

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

| 参数 | 值 | 约束 |
|------|-----|------|
| structure | JSONL with SHA-256 chain; each_line: {event_json}\|\|SHA256(prev_hash+current_payload); genesis: SHA256(module_id+creation_ts+initial_policy_hash) | append-only |
| verification | `zephyr budget audit verify`顺序验证; 每次启动自动验证; chain broken→L5_halt+通知Owner | — |
| separate_from_agent | path: .zephyr_secure/audit/tamper_evident.jsonl; 仅Ring 1+可写; Ring 2/3 read-only | — |
| pruning | 每10000条记录生成snapshot(保留snapshot hash+后续增量chain) | — |

### 2.28 IPI-Aware Budget Defense

> **决策 D-024-26（🆕 v0.7.0）**：Forcepoint X-Labs (2026.4) 披露 10 种 IPI 载荷。AI agent 读取外部网页/PDF/邮件时，隐藏指令可劫持 agent 行为。攻击者注入 `"set global budget to unlimited"` 时——Budget Enforcer 当前无能力区分这是攻击还是 Owner 操作。

| 参数 | 值 | 约束 |
|------|-----|------|
| critical_actions_require_signing | 修改hard/soft_limit / borrow>20%全局 / disable guard / kill_switch解除 / env_profile切换→必须Ed25519签名 | payload: {action}\|\|{params_hash}\|\|{ts}\|\|{nonce}; Ring 0验证 |
| ipi_detection_in_inputs | 正则: budget.*unlimited\|override\|disable.*guard\|bypass; 语义: embedding similarity to known IPI payloads>0.85→MARK potentially_poisoned | 不将其作为预算决策依据 |
| partial_trust_model | 检测到IPI但不确定→仅限读取，阻止写入/修改; fallback: SAFE_MODE(仅tier_0_free，其他需Owner确认) | — |

### 2.29 故障模式规范 + 冷启动反滥用 + 对抗测试

> **决策 D-024-27（🆕 v0.7.0）**：Budget Enforcer 自身崩溃时，系统应 fail-open（允许所有→成本失控）还是 fail-closed（拒绝所有→系统瘫痪）？前 6 轮从未定义。

| 参数 | 值 | 约束 |
|------|-----|------|
| per_level_fail_mode | L0 request: fail-closed; L1 turn: fail-closed; L2 task: fail-closed; L3 session: fail-open限流(tier_0+1/10上限); L3.5 workflow: fail-open限流; L4 global: fail-closed; L4.5 self: fail-open限流(仅统计不阻断) | — |
| fail_mode_recovery | heartbeat: 每30s检查; 连续3次失败→触发fail_mode; 组件恢复→自动恢复 | — |
| cold_start_anti_abuse | 1h内最多3个Session(超过→冷启动豁免降为1000token); 24h冷启动累计≤27500token(=5×5500) | — |
| adversarial_testing | 5项: IPI注入policy修改 / cold start 10次快速重启 / parent-child无限委托 / stream_abort前恶意操作 / 多Provider race condition; gate: experimental→beta前必须全过 | 报告→docs/_working/audit/adversarial_test_report.md |

### 2.30 启动校准阶段（Bootstrapping Calibration Phase）

> **决策 D-024-28（🆕 v0.7.0）**：Day 0 的 budget_policy.yaml 是 AI 生成的猜测。如果阈值太紧→系统不可用→无法收集数据→自学习无法启动。需要一个显式的"宽限期"。

| 参数 | 值 | 约束 |
|------|-----|------|
| duration | 30 days or 100 tasks completed(whichever first) | — |
| calibration_profile | hard_limit ×3; enforcement: ALL→warn-only(不DENY不HALT); exceptions: loop_detection和kill_switch保持生效 | — |
| exit_criteria | min_data_points: 100; convergence: 预估偏差<20%连续10任务; auto_exit: 满足后自动切换; manual_exit: `zephyr budget exit-calibration` | — |
| post_calibration | auto_tune: 基于P95消耗值调整soft/hard_limit; report: 各模型/任务P50/P75/P95/P99; human_review: 调整后阈值需Owner签名确认 | — |

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
      output: "docs/_working/audit/cost_reports/weekly-{date}.md"
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
| MOD-CONTEXT_ENGINE Context Engine | 上下文压缩 + 浪费检测联动 | L3 compress + waste_ratio > 60% | DocCompressor aggressive 模式 / 优化选择策略 |
| MOD-TASK_SYSTEM Task System | 任务预算字段 + 状态机预算联动 | 任务预算/状态变更 | 读取任务预算 + 状态联动 |
| MOD-INF-020 Audit Trail | 审计写入 | 每次降级/熔断/Borrow/Abort | 写入审计事件 |
| MOD-INF-022 Escalation | 升级 | 硬停止 + Kill Switch | 触发升级通知 Owner |
| **MOD-INF-023 Drift Detector**（🆕 v0.4.0） | 漂移预算信号 | 配置漂移对预算的影响 | 调用漂移检测 + 预算影响评估 |
| **MOD-MASTER_BLUEPRINT 任务系统**（🆕 v0.4.0） | Batch 路由 | task.urgency=low | 自动标记走 Batch API |
| **Git Pre-commit Hook**（🆕 v0.4.0） | 策略快照 | git commit | 自动快照 budget_policy.yaml 到版本历史 |
| **LiteLLM Registry**（🆕 v0.4.0） | 新模型发现 + 定价同步 | daily sync 发现新 model_id | 评估 + 写摘要 + 通知 Owner |
| **LiteLLM Pricing Strategy Sync**（🆕 v0.5.0） | 长上下文定价策略同步 | daily sync 检测 pricing strategy 变化 | 更新 non-linear pricing threshold |
| **Context Engine v2**（🆕 v0.5.0） | 历史税加权衰减 + 指令膨胀精简 | history_tax_ratio > 5× OR instruction_growth > 20% | DocCompressor 加权衰减 + 生成精简建议 |
| **SUPERVISORAGENT LLM-Free Filter**（🆕 v0.6.0） | LLM-free 触发——仅在必要时升级 LLM-dependent | budget_policy LLM-free 阶段提升 | guard 类型从 LLM-dependent → LLM-free |
| **Provenance DAG**（🆕 v0.6.0） | 幻觉信息源链追踪——dependency graph | agent output 包含 claim 时 | 追加到 observation provenance DAG |
| **Agent Delegation Registry**（🆕 v0.6.0） | 记录 parent-child 委托关系 | 每次 agent-to-agent call | 记录 delegation edge + 写入 attribution |
| **MOD-LLM_SECURITY LLM Security Gateway**（🆕 v0.7.0） | IPI 检测 + 策略文件签名验证 + Trust Ring 隔离 | IPI pattern detected / policy modification attempt | 签名验证网关 + Ring escalation |

---

## §4 接口契约

### §4.1 公共 API

| 类 | 方法 | 签名 | 执行流程 |
|----|------|------|---------|
| `BudgetEngine` | `pre_flight_check` | `(estimated_tokens, estimated_cost, estimated_time) → GateResult` | 加载策略→检查三维预算→返回 ALLOW/WARN/DEGRADE/DENY/BORROW |
| `BudgetEngine` | `record_consumption` | `(policy_id, tokens, cost, time_minutes) → None` | 累加消耗→检查阈值→触发降级/告警 |
| `BudgetEngine` | `try_claim_budget` | `(tokens, cost, time) → claim_id` | 乐观锁预留→返回 claim_id |
| `BudgetEngine` | `commit_claim` | `(claim_id) → None` | 确认消耗→写入审计 |
| `BudgetEngine` | `rollback_claim` | `(claim_id) → None` | 释放预留→回退配额 |
| `BudgetEngine` | `advance_degradation` | `(reason) → BudgetLevel` | 推进降级→写入审计→通知 Escalation |
| `BudgetEngine` | `retreat_degradation` | `() → BudgetLevel` | 检查恢复条件→回升一级 |
| `BudgetTracker` | `open_scope` | `(scope: TrackerScope, scope_id: str) → BudgetSnapshot` | 开启预算作用域 |
| `BudgetTracker` | `record_request` | `(scope, scope_id, tokens_in, tokens_out, cost_usd, wall_time) → BudgetSnapshot` | 记录请求级消耗 |
| `PreFlightGate` | `gate` | `(estimated_tokens, estimated_cost, estimated_time, policy?) → PreFlightReport` | 三维预算门控 |
| `DegradationManager` | `evaluate` | `(usage_ratio: float, dimension: BudgetDimension, current_tier?) → DegradationAction` | 检查阈值→推进降级 |
| `ModelRouter` | `route` | `(task_complexity, budget_remaining) → RoutingDecision` | 成本感知路由 |
| `CostBudget` | `record_usage` | `(provider, model, input_tokens, output_tokens, cached_input_tokens?) → float` | 记录API调用消费 |
| `TimeoutGuard` | `watch` | `(scope_id, timeout_seconds) → None` | 启动超时监控 |
| `TimeoutGuard` | `unwatch` | `(scope_id) → None` | 取消超时监控 |

### §4.2 数据模型

| 模型 | 字段 | SSoT |
|------|------|------|
| `BudgetDimension` | TOKEN / COST / TIME | `budget_models.py` |
| `BudgetLevel` | L0_NORMAL→L6_KILL_SWITCH | `budget_models.py` |
| `GateDecision` | ALLOW / WARN / DEGRADE / DENY / BORROW / NARROW | `budget_models.py` |
| `ModelTier` | PREMIUM / STANDARD / ECONOMY / MINIMAL | `budget_models.py` |
| `GateResult` | request_id, decision, reason, budget_level, model_tier, estimated_tokens, estimated_cost, remaining_daily, remaining_hourly | `budget_models.py` |
| `BudgetAlert` | alert_id, budget_type, burn_rate, severity | `alerts.py` |

---

## §5 约束条件

### §5.1 技术约束

| 约束 | 值 | 原因 |
|------|-----|------|
| Python 版本 | ≥3.11 | 使用 `str` 类型别名、`match` 语句 |
| 依赖 | Pydantic V2, asyncio | 数据模型 + 超时守卫 |
| 存储 | JSONL + YAML + SQLite | 审计日志 + 策略 + 聚合 |
| 并发模型 | asyncio + ThreadPoolExecutor | I/O 密集型操作 |

### §5.4 非功能需求与 SLI/SLO

| SLI | SLO | 告警阈值 | 采集方式 |
|-----|-----|---------|---------|
| pre_flight_check 延迟 | P99 < 5ms | P99 > 10ms | 代码埋点 |
| 预算检查准确率 | > 95% | < 90% | 预估 vs 实际偏差 |
| 降级触发及时性 | < 1s | > 3s | 事件时间戳 |
| Tamper-Evident chain 完整性 | 100% | chain broken | 启动自检 |

### §5.5 自动化触发机制

| 操作 | 触发方式 | 自动化程度 |
|------|---------|-----------|
| Pre-flight Gate | 每次 LLM API 调用前自动触发 | ✅ 全自动 |
| 降级链推进 | `record_consumption()` 内自动检查阈值 | ✅ 全自动 |
| Burn Rate 告警 | 4 窗口滑动监控自动触发 | ✅ 全自动 |
| Timeout Guard | asyncio daemon timer 自动触发 | ✅ 全自动 |
| Stream Abort Guard | 每 500 token checkpoint 自动触发 | ✅ 全自动 |
| 健康检查 | `check_budget_health.py` 需手动运行 | ⚠️ 半自动 |
| 定价同步 | cron/daily 02:00 UTC | ⚠️ 需外部调度 |
| 周报生成 | cron/weekly | ⚠️ 需外部调度 |
| 对抗测试 | Phase transition gate 触发 | ⚠️ 需手动触发 |

### §5.7 禁止模式

| 禁止 | 原因 | 替代 |
|------|------|------|
| 直接修改 `budget_policy.yaml` 不走签名验证 | 绕过 Trust Ring | `PolicySandbox.propose_change()` + Ed25519 签名 |
| 在 `budget_enforcer` 外部实现降级逻辑 | 职责分裂 | 通过 G-CT-006 契约调用 |
| 硬编码模型价格 | 价格动态变化 | `PricingSync` + LiteLLM Registry |
| 跳过 Pre-flight Gate 直接调用 LLM | 绕过预算控制 | 所有 LLM 调用必须经过 `pre_flight_check()` |

---

## §6 错误处理

| 异常 | 触发条件 | 处理 | 降级 |
|------|---------|------|------|
| `CostBudgetExceededError` | 消费超过 hard_limit | 记录→降级→审计 | L2_model_switch |
| `TimeoutError` | wall-clock 超时 | 保存状态→abort→审计 | FORCE_ABORT |
| `TamperEvidentChainBroken` | hash chain 验证失败 | L5_halt→通知Owner | 全局只读 |
| `IPIPatternDetected` | IPI 攻击模式匹配 | 标记→限制→审计 | SAFE_MODE |
| `FailModeTriggered` | 组件连续3次失败 | per-level fail-open/closed | 按级别 |
| `BootstrappingNotConverged` | 30天未达100数据点 | 延长校准期 | warn-only |

### §6.1 可观测性

| 指标 | 类型 | 采集 | 告警阈值 |
|------|------|------|---------|
| `budget_utilization_ratio` | gauge | 每次消费后 | >0.8 WARNING, >0.95 CRITICAL |
| `burn_rate_10min` | gauge | 10min窗口 | >10× CRITICAL |
| `degradation_level` | state | 降级事件 | L4+ CRITICAL |
| `cache_hit_rate` | gauge | 每次缓存查询 | <0.2 WARNING |
| `guard_efficiency_ratio` | gauge | 每日统计 | <0.5 auto_disable |
| `tamper_chain_length` | counter | 每次append | chain broken→CRITICAL |

---

## §16 施工指引

### §16.1 施工策略

| Phase | 策略 | 当前状态 |
|-------|------|---------|
| sandbox | 策略沙盘验证 | 📋 Backlog |
| scaffold | 核心骨架（BudgetEngine+Tracker+Gate+Timeout） | ✅ 已完成 |
| experimental | 路由+降级+缓存+检测 | 📋 Backlog |
| beta | 归因+ROI+周报+Burn Rate | 📋 Backlog |
| stable | 自学习+Anti-Spiral+储蓄 | 📋 Backlog |
| self_calibrating | 自适应校准 | 📋 Backlog |

### §16.2 前置条件

| 条件 | 状态 | 阻塞原因 |
|------|------|---------|
| Pydantic V2 已安装 | ✅ | — |
| budget_policy.yaml 已创建 | ✅ | — |
| G-CT-006 契约已注册 | ✅ | — |
| MOD-INF-022 Escalation 可达 | ⚠️ | escalation check failed: LSG blocked |
| MOD-INF-015 Telemetry 桥接 | ⚠️ | 需验证 |

### §16.3 实施步骤（读→做→产→检）

| 步骤 | 读 | 做 | 产 | 检 |
|------|-----|----|----|-----|
| 1 | 读 budget_policy.yaml | 实例化 BudgetEngine | GateResult | `check_budget_health.py` exit 0 |
| 2 | 读 G-CT-006 契约 | 集成 Escalation | 升级事件 | escalation bridge OK |
| 3 | 读 §2.3 Model Router | 集成 cost_router | 路由决策 | 路由测试通过 |
| 4 | 读 §2.4 降级链 | 集成 degradation_manager | 降级事件 | 降级测试通过 |
| 5 | 读 §2.9 Burn Rate | 集成 burn_rate_monitor | 告警 | 告警测试通过 |

### §16.4 回滚方案

| 场景 | 回滚操作 | 验证 |
|------|---------|------|
| BudgetEngine 异常 | `fail_mode_manager` 自动 fail-closed | heartbeat 恢复 |
| 策略变更导致卡死 | `zephyr budget policy rollback --version v{N}` | sandbox dry-run |
| 降级螺旋 | anti_spiral max 1/min + cooldown 180s | 恢复到 L1 |

### §16.5 完成与就绪标准

| 标准 | 判定 |
|------|------|
| scaffold 完成 | ✅ BudgetEngine+Tracker+Gate+Timeout 可运行 |
| experimental 就绪 | ❌ 路由+降级+缓存集成测试未通过 |
| beta 就绪 | ❌ 对抗测试5项未通过 |
| stable 就绪 | ❌ 自学习阈值未校准 |

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖 | 类型 | 方向 | 硬/软 |
|------|------|------|-------|
| MOD-CONTEXT_ENGINE Context Engine | 数据消费 | 024→008 | soft |
| MOD-INF-020 Audit Trail | 事件写入 | 024→020 | hard |
| MOD-INF-022 Escalation | 事件触发 | 024→022 | hard |
| MOD-INF-001 Capacity Assurance | Kill Switch 联动 | 024↔001 | hard |
| MOD-TASK_SYSTEM Task System | 预算字段读取 | 024→006 | soft |
| MOD-INF-023 Drift Detector | 漂移信号 | 023→024 | soft |
| MOD-LLM_SECURITY LLM Security | IPI 检测 | 014→024 | hard |
| MOD-INF-015 System Telemetry | metrics 聚合 | 024→015 | soft |
| MOD-INF-016 Shared Core | BudgetEngine 基类 | 024→016 | hard |
| MOD-INF-034 Model Exam | 评测数据 | 034→024 | soft |

### §10.6 依赖链风险评级

| 风险 | 评级 | 缓解 |
|------|------|------|
| 022↔024 双向依赖 (C24) | **中** | 024→022 为事件驱动（非同步调用），022→024 为查询驱动；Escalation `escalation_loop_detector.py` 已实现循环检测+冷却期；**非真环**——运行时不会死循环 |
| 022→024→025→022 三节点环 (C25) | **低** | 024→025 为单向消费（A2A 读 Budget 池），025→022 为事件驱动（仲裁失败升级）；三边均为异步/事件驱动，无同步调用链；**裁定：伪环，保留现状** |
| 024 依赖深度 5 级 | **高** | circuit breaker + 本地缓存 fallback + FailModeManager |

**C24/C25 裁定**：022↔024 和三节点环均为**伪环**（事件/查询驱动，非同步递归），运行时不会死循环。保留现状，依赖 Escalation 的 `escalation_loop_detector` 作为安全网。

| 依赖图条目 | 蓝图 depends_on | 对齐 |
|-----------|----------------|------|
| 022→024 (Escalation→Budget) | ✅ | 对齐 |
| 024→025 (Budget→A2A) | ✅ §9 | 对齐 |
| 024→015 (Budget→Telemetry) | ✅ §10.1 | 对齐 |
| 024→016 (Budget→Shared Core) | ✅ §10.1 | **新增对齐** |
| 024→034 (Budget→Model Exam) | ✅ §10.1 | **新增对齐** |
| Context Engine→024 | ✅ §9 | 对齐 |
| LLM Security→024 | ✅ §9 | 对齐 |

### §10.5 概念重叠声明

| 概念 | 本模块 | 重叠模块 | 边界 |
|------|--------|---------|------|
| Token Budget | 五级预算执行 | MOD-INF-001 容量规划 | 024 执行，001 规划 |
| Cost Budget | 三维预算+降级 | MOD-RESOURCE_OPTIMIZATION_ENGINE 资源优化 | 024 管 Token/Cost/Time，032 管 CPU/Memory/Disk |
| Kill Switch | L6 全局熔断 | MOD-INF-001 容量保障 | 024 触发，001 执行 |
| Budget Alert | 预算告警模型 | MOD-INF-020 审计 | 024 产生告警，020 存储 |

---

## §13 需要更新的相关内容

| 修改本蓝图 | 必须同步更新 |
|-----------|-------------|
| §2.1 预算阈值 | `config/budget_policy.yaml` + `已删除`(deprecated 标记) |
| §2.3 模型路由 | `model_provider_data.py` + `cost_router.py` |
| §4.1 公共 API | `budget_models.py` + `__init__.py` 导出 |
| §9 跨模块集成 | 对端蓝图 §10 依赖声明 |
| G-CT-006 契约 | `bridges/alerts.py` + MOD-INF-022 蓝图 |

---

## 术语表

| 术语 | 定义 | 易混淆 |
|------|------|--------|
| Budget Dimension | Token/Cost/Time 三维预算维度 | ≠ Resource Dimension(CPU/Memory/Disk) |
| Budget Level | L0-L6 降级级别 | ≠ Budget Scope(Global/Session/Task/Turn/Request) |
| Gate Decision | Pre-flight 门控决策 | ≠ Degradation Level |
| Model Tier | PREMIUM/STANDARD/ECONOMY/MINIMAL | ≠ Provider Tier(Anthropic 4-Tier) |
| Burn Rate | 消耗速率(4窗口) | ≠ Spiral Score(结构扩张模式) |
| Trust Ring | Ring 0-3 信任分级 | ≠ RBAC Role |

---

## 变更记录

| 版本 | 关键变更 | 盲点数 |
|------|---------|:------:|
| 0.7.0 | Trust Rings(0-3) + Tamper-Evident hash chain + IPI Defense + Fail-Mode Spec + Bootstrapping Calibration + Adversarial Testing | 78 |
| 0.6.0 | Self-Budget + Spiral EWS + Poison Cascade + Parent-Child Attribution + Think-Time Model + LLM-Free Guard 升级路径 | 68 |
| 0.5.0 | 三维(Token/Cost/Time) + Timeout Guard + Action History Dedup + Instruction Bloat + Conversation Tax + 跨Session储蓄 | 56 |
| 0.4.0 | 模型路由反转 + Stream Abort + Output Quality Gate + ENV Profile + Agent子池 + Policy Sandbox + 新模型发现 | 43 |
| 0.3.0 | 五级预算 + Pre-flight Gate + Model Router + 六级降级 + 语义缓存 + 成本归因 + Burn Rate + Budget Pool | 20 |
| 0.2.0 | D-024-01 四级自动降级 + JSONL审计 | — |
| 0.1.0 | 三级预算体系 + 降级策略 | — |


---

## 施工落盘确认（2026-05-08 审计修正 · P0/P1 修复完成）
| 维度 | 状态 |
|------|------|
| construction_progress | phase_1_partial→phase_1_加固中（Phase 0 Skeleton + Phase 1 治理桥接已通过，P1 核心模块 4/4 已落盘，Phase 1.5/2 待施工） |
| 源码路径 | `src/zephyr/governance/budget_engine.py` |
| 源码文件数 | **11 个 .py**（蓝图 §4 计划 31 文件，完成率 **35.5%** ← 修复前 22.6%） |
| 新增 P1 模块 | `budget_tracker.py`, `degradation_manager.py`, `model_router.py`, `timeout_guard.py` |
| 配置文件 | `已删除`（Capacity Assurance——**deprecated，SSoT 已迁移至 024**）+ ✅ `config/budget_policy.yaml`（Budget Policy SSoT 种子版 v0.1.0-seed） |
| 门禁 | ✅ GCT-024 `gates/gct-024-budget-enforcer.yaml`（7 checks: 硬4 + 软2 + info1） |
| 关键入口 | `governance/budget_engine.py` |


## Consumers
- zephyr.governance.budget_engine (internal)
