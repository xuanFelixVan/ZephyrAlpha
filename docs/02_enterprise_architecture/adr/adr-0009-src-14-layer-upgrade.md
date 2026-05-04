---
module_id: ADR-0009
title: src/zephyr/ 从 11 业务层升级至 14 业务层 + shared 深化 + 工程基础设施补齐
doc_type: adr
status: active
version: 1.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-18
accepted_at: 2026-04-19
superseded_by: null
supersedes: null
related_rationale:
- R29
- R30
- R31
- R32
- R67
related_open_questions:
- OQ-021
- OQ-022
- OQ-047
- OQ-068
- OQ-073
tags:
- adr
- src-layer
- l12-telemetry
- l13-experiment
- l11-ml-platform
- shared
- infrastructure
- engineering-blindspots
- errata-v1.1.0
summary: '确认 `src/zephyr/` 从 11 业务层升级至 **14 业务层（L00-L13）+ shared 横切目录 = 15 个物理顶级目录**；

  同时系统性补齐 17 项工程基础设施盲点（Event Bus / State Machine / Resilience / Dynamic Config / Scheduler
  / Secrets /

  Health Check / Idempotency / Concurrency / Lifecycle / Flow Control / Layer Validation
  / Trading Calendar / Feature Flag /

  Streaming 预留 / Semantic Code Graph 预留），分布在 shared/ + l01/ + l00/ + l10/ 四层深化。

  v1.1.0 依据 OQ-073（会话 12）做口径澄清：L11 命名锁定 `l11_ml_platform`（不是 `l11_ml_platform`），

  strategic_decision 下沉至 `l05_portfolio_construction/strategic/`；并澄清 "14 业务层 vs 15
  物理目录" 两种计数方式。

  '
date: '2026-04-22'
ttl: permanent
---

# ADR-0009：src/ 11→14 业务层升级 + 工程基础设施系统性补齐

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-18（v1.0.0 proposed，由 Opus 47 在会话 10 起草）
- **拍板日期**：2026-04-19（v1.1.0 升格 accepted，批次 J0）
- **被谁取代**：无
- **取代了谁**：无
- **升格路径**：`19_development_workspace/adr-drafts/ADR-DRAFT-0009-src-15-layer-upgrade.md` v1.0.0 proposed
  → 本文件 v1.1.0 accepted（口径澄清 + 升格）

---

## 2. 上下文（Context）

### 2.1 层升级来源

`zephyr-src-gap-analysis.pdf`（5 AI 共识）明确诊断：现有 11 层（shared + L00-L10）缺失 L12 系统遥测和 L13 实验流水线。没有 L12，AI 自治等于盲人开车；没有 L13，闭环愿景无法工程化。

### 2.2 工程基础设施盲点来源

会话 10 Opus 系统性盲点扫描发现：之前所有 gap 文档聚焦**业务功能模块**，但**跨层通用工程基础设施**被系统性遗漏。对标 Bloomberg / Refinitiv / Two Sigma / Citadel / IBKR / QuantConnect 六家机构，识别 17 项盲点（B1-B16, B18），用户全部确认加入。

### 2.3 会话 12 的两项命名校准（v1.1.0 新增 context）

**OQ-073 closed（2026-04-18 会话 12 后段）两项关键决策**：

1. **strategic_decision 不独立成层**（R31 = P1 BlackRock 模式）：业界无任何顶级机构将 strategic_decision 列为独立顶层；BlackRock Aladdin 把 strategic asset allocation 当作 portfolio construction 的长周期版本。结论：`l11_ml_platform` 取消，strategic 下沉到 `l05_portfolio_construction/strategic/` 子模块。
2. **L10 命名**（R32 = B3 compliance）：Goldman/Citadel/Two Sigma/BlackRock/JPM/Bloomberg 业界共识 L10 叫 `compliance`；`governance` 概念另放 `docs/07/META_GOVERNANCE/` + `scripts/governance/`。

**结论**：本 ADR v1.1.0 修正两处：L11 命名 `strategic_decision` → `ml_platform`，L10 命名 `governance_compliance` → `compliance`。

---

## 3. 决策（Decision）

### 3.1 新增独立层

| 新层 | 命名 | 昵称 | 子模块（P0） |
|------|------|------|-------------|
| **L11** | `l11_ml_platform/` | AI 的大脑 | training/ · inference/ · model_registry/ · hyperparameter_tuning/（v1.1.0 命名校准，原 DRAFT 稿为 strategic_decision）|
| **L12** | `l12_system_telemetry/` | AI 的眼睛 | metrics/ · factor_health/ · drift_detection/ · ai_cost_tracker/ · execution_feedback/ |
| **L13** | `l13_experiment_pipeline/` | 闭环发动机 | shadow_oms/ · ab_framework/ · hypothesis_engine/ · promotion_gate/ · rollback_watchdog/ |

**升级后 `src/zephyr/` 的物理结构**：
- **14 个业务层**（L00-L13，即 l-prefixed 目录）
- **+ 1 个 shared 横切目录**
- **= 15 个物理顶级目录**

> ⚠️ **计数口径澄清（v1.1.0 新增）**：
> - **对外官方口径**使用 **"14 业务层"** 对齐业界（Goldman/JPM/Two Sigma/Citadel/BlackRock 皆按业务层计数）
> - **物理容量规划 / CI 层级校验 / 目录预算**使用 **"15 个物理目录"**（含 shared）
> - 原 v1.0.0 标题"11→15 层"属歧义口径，v1.1.0 统一改为"11→14 业务层 + shared"
> - 详见 §8 Errata

### 3.2 shared/ 深化（6 个新子模块）

| 盲点 ID | 子模块 | 用途 | 对标 |
|---------|--------|------|------|
| B5 | `shared/state_machine/` | 通用 FSM 引擎（StateMachine + Transition + Guard + Hook），订单/因子/策略/Agent 任务 5+ 生命周期共用 | Bloomberg EMSX StateMachine |
| B6 | `shared/resilience/` | RetryPolicy + CircuitBreaker + RateLimiter + Bulkhead（Python 装饰器形式），保护所有外部 API 调用 | Netflix Resilience4j / tenacity |
| B9 | `shared/concurrency/` | DistributedLock 抽象（file-based 实现，预留 Redis/etcd adapter），解决多 Agent 并发写入竞态 | Citadel Lock Service |
| B4 | `shared/idempotency/` | IdempotencyKey 生成器 + 去重存储 + 事务幂等装饰器，防止订单重复提交 | 交易系统资金安全红线 |
| B12 | `shared/contracts/validators/` | Pydantic 层间数据运行时 schema 校验 + 违规自动告警到 L12 | MLOps 标配 pandera/pydantic |
| B14 | `shared/calendar/` | TradingCalendar + A 股假日 + TradingSession 时间窗口，因子/回测/交易三层共用 | QuantConnect TradingCalendar / Zipline |

### 3.3 l01_infrastructure/ 深化（5 个新子模块 + runtime 增强）

| 盲点 ID | 子模块 | 用途 | 对标 |
|---------|--------|------|------|
| B1 | `l01/event_bus/` | 进程内 EventEmitter（pub/sub 模式），预留 Kafka adapter。L12 遥测/L13 实验/L08 Agent 三者的公共异步通信基础 | Two Sigma Kafka / QuantConnect Event Emitter |
| B2+B15 | `l01/dynamic_config/` | 热更新配置中心（风控限额/策略权重/因子阈值运行时可调）+ Feature Toggle 系统 | Goldman Parameter Store |
| B3 | `l01/scheduler/` | Cron 式定时 + 事件触发 + 依赖链式任务调度 | Lean ScheduledUniverseSelection |
| B8 | `l01/secrets/` | SecretProvider 抽象 + 环境变量 fallback + HashiCorp Vault adapter 预留 | 机构标配 Vault/AWS Secrets Manager |
| B10+B11 | `l01/health/` + `l01/runtime/` lifecycle hooks | HealthCheck 注册表 + Liveness/Readiness 探针 + on_startup/on_shutdown/on_signal 优雅关停 | K8s 标配 + IBKR TWS shutdown hook |

### 3.4 l00_data_source/ 深化

| 盲点 ID | 子模块 | 用途 | 对标 |
|---------|--------|------|------|
| B13 | `l00/flow_control/` | 背压控制（bounded buffer + drop/backpressure/sample 三策略），防行情 tick 风暴打爆内存 | Refinitiv Elektron flow control |

### 3.5 l10_compliance/ 深化（v1.1.0 命名校准：原 l10_compliance）

| 盲点 ID | 子模块 | 用途 | 状态 |
|---------|--------|------|------|
| B7 | `l10/audit_trail/` 实质化 | AuditEvent 结构化 Schema + append-only storage + CausalityChainId 因果链 | P0 合规红线 |
| B17 | `l10/policy_engine/` 技术选型 | OQ-047 讨论中（方案 A Python 自研 + OPA 预留 vs 方案 B 直接上 OPA） | 待用户拍板 |
| — | `l10/ai_security/` （J0-a 预留）| AISG（AI Security Gateway）落地位置，详细设计已吸收进 `06-security-architecture.md` v1.0.0 + `llm-security-gateway-interface.md` v1.0.0，源设计稿归档 `archive/reorg-2026-04-24/absorbed-into-view/working-designs/ai-security-gateway-design.md`（ARC-20260424-005）| v1.1.0 新增预留（OQ-076）|

### 3.6 超前预留（P3 级 Architecture Runway）

| 盲点 ID | 位置 | 用途 | 激活条件 |
|---------|------|------|---------|
| B16 | `shared/streaming/` | Streaming-first 架构预留（Flink/Kafka Streams adapter 接口） | 实时行情处理延迟 < 100ms 需求出现 |
| B18 | `shared/code_graph/` | 语义代码图谱预留（AST 解析 + 因子/策略语义依赖图） | AI 自动修改代码功能激活（L13 hypothesis_engine 投产后） |

---

## 4. 升级后完整分层体系（v1.1.0 修正版）

```
src/zephyr/                              # 14 业务层 + shared = 15 个物理顶级目录
├── shared/                              # 跨层公共（v1.5.0 新增 6 个子模块）
│   ├── contracts/ + validators/  [B12]
│   ├── utils/
│   ├── exceptions/
│   ├── types/
│   ├── state_machine/            [B5]   ← NEW
│   ├── resilience/               [B6]   ← NEW
│   ├── concurrency/              [B9]   ← NEW
│   ├── idempotency/              [B4]   ← NEW
│   ├── calendar/                 [B14]  ← NEW
│   ├── streaming/                [B16]  ← RUNWAY
│   └── code_graph/               [B18]  ← RUNWAY
├── l00_data_source/                     # + flow_control/ [B13]
├── l01_infrastructure/                  # + event_bus/ [B1] + dynamic_config/ [B2+B15]
│                                        #   + scheduler/ [B3] + secrets/ [B8]
│                                        #   + health/ [B10] + runtime lifecycle [B11]
├── l02_alpha_factor/                    # + lifecycle/ (已在 Q4.2)
├── l03_signal_generation/
├── l04_risk_management/
├── l05_portfolio_construction/          # + meta_router/ (OQ-023) + strategic/ (R31/OQ-073)
├── l06_trade_execution/
├── l07_post_trade_analytics/
├── l08_human_ai_interface/              # + api_gateway/ (ADR-0007) + Agent 升级 (Q2)
├── l09_research_innovation/             # + sandbox/ (已在 Q4.1)
├── l10_compliance/                      # v1.1.0 改名（原 l10_compliance），R32/OQ-073
│                                        # + audit_trail 实质化 [B7] + policy_engine [B17]
│                                        # + ai_security/（J0-a 预留，OQ-076）
├── l11_ml_platform/                     # v1.1.0 改名（原 l11_ml_platform），R31/OQ-073
│                                        # training/ · inference/ · model_registry/ · hyperparameter_tuning/
├── l12_system_telemetry/         [NEW]  # AI 的眼睛
└── l13_experiment_pipeline/      [NEW]  # 闭环发动机
```

---

## 5. 后果（Consequences）

### 5.1 收益

- **14 业务层覆盖量化投资全价值链**：从数据到因子到信号到风控到组合到交易到归因到 AI 自治
- **工程基础设施不再是盲点**：17 项盲点全部有架构位置和实现路线
- **对标专业机构完整性**：Bloomberg/Refinitiv/Two Sigma/Citadel/BlackRock 级别的工程成熟度
- **L11 命名对齐业界**：ml_platform 与 Two Sigma/BlackRock Aladdin 对位（原 strategic_decision 无任何顶级机构采用）

### 5.2 代价

- 子模块总数从 ~45 增加到 ~75（+30），实现工作量增加
- shared/ 膨胀，需要更严格的内部分包治理（Import-Linter 规则）
- **strategic_decision 下沉代价**：原规划的 strategic 功能（长周期资产配置、IC 决策流程）需作为 `l05/strategic/` 子模块重新设计，后续施工时新增 ADR 覆盖（R31 已留尾）

### 5.3 关键约束

- L12/L13 的依赖方向：L12 被所有层依赖（横切），L13 依赖 L12 + L05 + L06
- L11 ml_platform 依赖 L12（需要 telemetry 数据训练）+ L02/L03/L05（训练对象）
- B1 Event Bus 是 L12/L13/L08 的公共前置，必须先实现
- B5 State Machine 是 L06 OMS / L02 Factor Lifecycle / L13 Promotion Gate 的公共前置

---

## 6. 回滚条件（Rollback）

L12/L13/L11 作为独立层一旦被其他模块依赖即不可回滚。但 shared/ 的新子模块可以按需延后实现（保留目录 + `__init__.py` 占位即可）。

---

## 7. 修订记录

| 日期 | 版本 | 状态 | 说明 |
|------|------|------|------|
| 2026-04-18 | 1.0.0 | proposed | 初版。会话 10（Opus 47）AX-3 确认 + 系统性盲点扫描 17 项。标题为 "11→15 层升级"，内文 §3.1 同时存在 "14 个 l-prefixed 层 + shared = 15 层" 表述。|
| 2026-04-19 | 1.1.0 | **accepted** | **J0-b 升格**。采用 IETF RFC / ISO 标准 **"Retitle + Errata"** 做法（见 §8）。本次修订**决策本身未变**，仅做三项口径澄清：(1) 标题统一改为 "11→14 业务层升级 + shared 深化"；(2) L11 命名校准（OQ-073 R31，strategic_decision → ml_platform）；(3) L10 命名校准（OQ-073 R32，governance_compliance → compliance）。文件从 `adr-drafts/ADR-DRAFT-0009-src-15-layer-upgrade.md` 升格到 `adr/adr-0009-src-14-layer-upgrade.md`，原 DRAFT 物理删除（git 历史保留）。

---

## 8. Errata（勘误记录）

本节记录 v1.0.0 → v1.1.0 升格时的**口径澄清**（非决策变更），对标 IETF RFC Errata 机制。

### E-1：标题歧义

| 位置 | v1.0.0 原文 | v1.1.0 更正 | 原因 |
|------|-------------|-------------|------|
| frontmatter title | `src/zephyr/ 从 11 层升级至 15 层 + shared 深化 + 工程基础设施补齐` | `src/zephyr/ 从 11 业务层升级至 14 业务层 + shared 深化 + 工程基础设施补齐` | 消除"15 层 = 业务层"的歧义。业务层数 = 14（L00-L13），15 是含 shared 的物理目录总数。 |
| §3.1 末 | `升级后 src/zephyr/ 包含 **14 个 `l`-prefixed 层 + shared = 15 层**` | `升级后 src/zephyr/ 包含 **14 个业务层（L00-L13）+ shared 横切目录 = 15 个物理顶级目录**` | 统一用"业务层"和"物理目录"两个词分开指代两种计数 |
| 文件名 | `ADR-DRAFT-0009-src-15-layer-upgrade.md` | `adr-0009-src-14-layer-upgrade.md` | 与标题同步；升格时同时修正文件名 |

### E-2：L11 命名冲突

| 位置 | v1.0.0 原文 | v1.1.0 更正 | 原因 |
|------|-------------|-------------|------|
| §4 层体系图 | `l11_ml_platform` | `l11_ml_platform` | OQ-073 closed（会话 12）拍板 R31 = P1 BlackRock 模式。业界无任何顶级机构把 strategic_decision 作为独立顶层。`strategic_decision` 原规划功能下沉到 `l05_portfolio_construction/strategic/` 子模块。 |
| §3（新增 L11 条目）| v1.0.0 无 L11 子模块规划 | v1.1.0 §3.1 新增 L11 条目（training/inference/model_registry/hyperparameter_tuning）| 与 OQ-069（GPU 集群 / 模型训练定位）+ OQ-073 R31 同步 |

### E-3：L10 命名校准

| 位置 | v1.0.0 原文 | v1.1.0 更正 | 原因 |
|------|-------------|-------------|------|
| §3.5 章节标题 | `l10_compliance/ 深化` | `l10_compliance/ 深化` | OQ-073 R32 = B3 模式。Goldman/Citadel/Two Sigma/BlackRock/JPM/Bloomberg 业界共识 L10 叫 `compliance`，`governance` 概念另放 docs 和 scripts。 |

### E-4：历史计数段追溯

**为什么历史上说过"11 层"和"12 层"**？

| 时期 | 数值 | 含义 |
|------|------|------|
| Sprint 1-5（2026-03 ~ 04 上旬）| **11 业务层** | 原始规划 L00-L10（含 l10_compliance）|
| 会话 10（2026-04-18）| **13 业务层 + shared = 14 目录** | 加 L12/L13 后短期中间态 |
| ADR-DRAFT-0009 v1.0.0（2026-04-18 会话 10 后段）| **14 l-prefixed + shared = 15 目录** | 加 l11_ml_platform 后 |
| OQ-073 closed（2026-04-18 会话 12）| **14 业务层 + shared = 15 目录** | L11 改名 ml_platform，业务层数不变 |
| 本 ADR v1.1.0（2026-04-19）| **14 业务层 + shared = 15 物理目录** | 最终锁定，官方口径 |

所有历史数字都是**同一架构的不同阶段/不同计数方式**，不存在实质冲突。

---

## 9. 业界对标证据（v1.1.0 补充，对应 OQ-068 closed）

| 机构 | 业务层数 | 关键对位 | 印证本 ADR |
|------|---------|---------|-----------|
| Goldman Sachs SecDB | 12-14 | L10 = compliance，无独立 strategic_decision 层 | ✅ |
| JPMorgan Athena | 10-13 | 缺 ML Platform / Experiment 独立层（2024 才补）| ✅ 我们先行 |
| Two Sigma | 12-14 | Telemetry 层（=L12）和 Experimentation 层（=L13）均独立 | ✅ 强对位 |
| Citadel | 8-12 | compliance_lab 对应 L10，风控拆子层不增顶层 | ✅ |
| BlackRock Aladdin | ~14 | strategic 作为 portfolio construction 子模块（印证 R31）；ML Engine 对应 L11，Monitoring 对应 L12 | ✅ 完美对位 |

**综合结论（OQ-068 closed）**：14 业务层架构足够且对标业界顶级量化机构，不需要新增顶层。核心价值链覆盖度 100%，横向支撑层覆盖度 100%。

---

## 10. 相关文档

- **升格前身**：`19_development_workspace/adr-drafts/ADR-DRAFT-0009-src-15-layer-upgrade.md` v1.0.0 proposed（已删除，git 历史保留）
- **命名校准来源**：`open-questions-register.md` OQ-073 closed（2026-04-18 会话 12）
- **业界对标**：`open-questions-register.md` OQ-068 closed（2026-04-19 S14 Phase 1）
- **GPU/训练定位**：`open-questions-register.md` OQ-069 closed（L11 ml_platform + L01 compute_cluster 双子模块承载）
- **AISG 预留**：源设计已吸收进 `target-architecture/06-security-architecture.md` v1.0.0 + `03_modules/_b_track_interfaces/llm-security-gateway-interface.md` v1.0.0；源稿归档 `archive/reorg-2026-04-24/absorbed-into-view/working-designs/ai-security-gateway-design.md`（ARC-20260424-005，OQ-076，l10_compliance/ai_security/ 子目录）
- **应用架构视图**：`target-architecture/03-application-architecture.md` §4.1（L11/L12/L13 分层说明）
- **rationale-log**：R29/R30（层升级决策）+ R31/R32（OQ-073 命名校准）+ R67（J0-b 升格记录）
