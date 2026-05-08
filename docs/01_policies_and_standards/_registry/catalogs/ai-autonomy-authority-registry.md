---
module_id: GOV-AI-001
title: AI 自治权限登记表（全模块权限终表）
doc_type: register
status: active
version: 1.3.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
date: "2026-05-03"
valid_from: "2026-05-01"
ttl: permanent
summary: ZephyrAlpha 全部模块的 AI 自治权限单一真源。覆盖 Immutable Core / Human-Gated / AI-Modifiable 三层权限的横向汇总，是终审兜底缺口 V-11 的产出。v1.1.0（Wave 1 R84）增补 §2.9 RI-01~07 运行时集成模块 + §2.10 CBAC/CBG/AlignmentMonitor 三件套 + §2.11 CL-017~021 基础设施缺口组件，并修正 RI-02/RI-03/RI-04/RI-07 权限误标。v1.2.2（2026-05-02）修复 F-A5 kb 模块内部权限矛盾（§2.2 AI-Modifiable vs §2.3 Human-Gated → 去重 + 子模块拆分 + §4.3 路径唯一性约束）。v1.3.0：从 governance/ai/ 迁移至 _registry/catalogs/。
tags: [ai-governance, autonomy, registry, authority, immutable-core, human-gated, vibe-coding]
rule_form: data
supersedes:
  - path: "governance/ai/ai-autonomy-authority-registry.md"
    version: "1.2.2"
    reason: "文件从 governance/ai/ 迁移至 _registry/catalogs/（物理位置变更，内容不变）"
depends_on:
  - "governance/module/ai-behavior-iron-policy.md"
  - "governance/module/module-admission-policy.md"
provenance:
  version: 1.0.0
  origin_drafts:
    - 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/capacity-assurance-construction-plan.md
    - 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/vibe-coding-architecture-overview.md
    - 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/vibe-coding-script-system-design.md
    - 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/vibe-coding-infrastructure-7-modules-design.md
    - 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/vibe-coding-principles-and-positioning.md
    - 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/vibe-coding-two-pipelines-design.md
    - 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/vibe-coding-task-card-and-knowledge-base-design.md
  audit_chain:
    - {round: 1, model: GLM-5.1, date: '2026-04-25', source: 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/}
    - {round: 2, model: Kimi-K2.6, date: '2026-04-26', source: 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/}
    - {round: 3, model: Qwen-3.6-Plus, date: '2026-04-26', source: 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/}
  arbitration:
    model: Claude-Opus-4.7
    date: '2026-04-27'
    rationale_log: R-74
    drafts_zone_source: 19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/
  arbitration_wave1:
    model: Claude-Opus-4.7
    date: '2026-04-27'
    rationale_log: R-84
    drafts_zone_source: 19_development_workspace/drafts-and-audits/2026-04-27-runtime-integration-meta-system/
related_rationale:
  - R-74-ai-autonomy-authority-registry
  - R-80-merge-ab-zones-into-drafts-zone
  - R-81-wave1-five-disputes-arbitrated
  - R-83-runtime-integration-construction-plan
  - R-84-g1-registry-add-ri-and-cbac-cbg
---

# AI 自治权限注册表

> **本注册表是 ZephyrAlpha 全模块 AI 自治权限的唯一真源**。任何模块的权限判定必须以本表为准。前三轮审计在 8 份文档中各自标注权限导致 25-30% 错误率，根因正是"没有横向汇总"——本表通过 Wave 0 终审兜底缺口 V-11 解决该问题。

---

## 一、三层权限模型（来自 ADR-0010）

| 层级 | 语义 | AI 自主修改权限 | 修改流程 |
|------|------|----------------|---------|
| **Immutable Core** | 系统宪法层 / 风控核心 / 审计基础设施 | 禁止 AI 自主修改 | Owner 直接审批 + ADR/rationale-log 记录 |
| **Human-Gated** | 业务规则 / 阈值 / 评估标准 / 治理参数 | 修改前必须 Owner 审批 | request_change() + approve_change() + Provenance Chain |
| **AI-Modifiable** | 算法实现 / 性能优化 / 日志级别 | AI 可自主修改 | 每次修改写入 Provenance Chain，可被回溯 |

---

## 二、全模块权限终表

### 2.1 业务核心层（C 轨 14 层）

| 模块 | 路径 | 权限 | 判定理由 | 审批要求 |
|------|------|------|---------|---------|
| L00 数据接入 | `src/zephyr/l00_data_source/` | Human-Gated | 数据源连接参数影响数据完整性 | Owner 审批连接配置 |
| L01 基础设施 | `src/zephyr/l01_infrastructure/` | Human-Gated | 基础设施变更影响所有上层 | Owner 审批 |
| L02 Alpha 因子 | `src/zephyr/l02_alpha_factor/` | AI-Modifiable | 因子算法可自主优化 | 写 Provenance |
| L03 信号生成 | `src/zephyr/l03_signal_generation/` | AI-Modifiable | 信号生成算法 | 写 Provenance |
| **L04 风险管理** | `src/zephyr/l04_risk_management/` | **Immutable Core** | 风控是量化系统不可变层 | Owner + ADR |
| L05 组合构建 | `src/zephyr/l05_portfolio_construction/` | Human-Gated | 组合策略影响资金分配 | Owner 审批策略修改 |
| L06 交易执行 | `src/zephyr/l06_trade_execution/` | Human-Gated | 执行参数影响成交质量 | Owner 审批 |
| **L06 风控参数（限额）** | 同上 子模块 | **Immutable Core** | 限额参数不可 AI 改 | Owner + ADR |
| L07 归因分析 | `src/zephyr/l07_post_trade_analytics/` | Human-Gated（**修正**：原 GLM 标 AI-Modifiable 偏松） | L7 风控关联 | Owner 审批 |
| L08 人机界面 | `src/zephyr/l08_human_ai_interface/` | AI-Modifiable | UI 实现 | 写 Provenance |
| L09 研究创新 | `src/zephyr/l09_research_innovation/` | AI-Modifiable | 实验性研究 | 写 Provenance |
| **L10 合规** | `src/zephyr/l10_compliance/` | **Immutable Core** | 合规规则刚性 | Owner + ADR |
| L11 ML 平台 | `src/zephyr/l11_ml_platform/` | AI-Modifiable | 模型训练实现 | 写 Provenance |
| L12 系统遥测 | `src/zephyr/l12_system_telemetry/` | AI-Modifiable | 日志实现 | 写 Provenance |
| L12 采样率 | 同上 子模块 | Human-Gated（**修正**） | 采样率影响审计完整性 | Owner 审批 |
| L13 实验平台 | `src/zephyr/l13_experimentation/` | AI-Modifiable | 实验框架 | 写 Provenance |

### 2.2 平台能力层（B 轨横切）

| 模块 | 路径 | 权限 | 判定理由 |
|------|------|------|---------|
| llm_security | `src/zephyr/llm_security/` | Immutable Core | 安全网关核心 |
| vector_memory | `src/zephyr/vector_memory/` | Human-Gated | 检索阈值影响召回 |
| context_engine | `src/zephyr/context_engine/` | Human-Gated | 上下文预算影响所有 AI 调用 |
| orchestrator | `src/zephyr/orchestrator/` | Human-Gated | 路由策略影响 Agent 行为 |
| feedback_loop | `src/zephyr/feedback_loop/` | Human-Gated | 进化策略影响系统演化方向 |
| gates | `src/zephyr/gates/` | Immutable Core | 合规门禁不可由 AI 禁用 |
| db | `src/zephyr/db/` | Human-Gated | Schema 修改需审批 |
| mcp | `src/zephyr/mcp/` | Human-Gated | 协议版本锁定 |
| shared | `src/zephyr/shared/` | Human-Gated | 共享契约修改影响多层 |

### 2.3 Vibe Coding 基础设施模块（M1-M11，本次终审产出）

| 模块 | 组件 | 权限 | 判定理由 |
|------|------|------|---------|
| **M1 上下文引擎** | context_budget_tracker / prompt_registry | Human-Gated | 预算变更影响所有 AI 调用 |
| **M2 记忆系统** | vector_memory / decisions store | Human-Gated | 检索影响 Agent 决策质量 |
| **M2 kb 基础设施** | kb/kb_repo.py / kb/chromadb_init.py | Human-Gated | 存储层与 Schema 影响记忆完整性 |
| **M2 kb 加工链** | kb/（ingest / extract / analyze / triage / activate / batch_ingest / graph_validator / embedding_migrate） | AI-Modifiable | 数据加工流水线可 AI 优化 |
| **M2 Provenance Chain** | provenance_logger.py | **Immutable Core** | 审计记录不可被 AI 修改 |
| **M3 Agent 编排** | orchestrator / AgentRouter | Human-Gated | 路由策略 |
| **M4-A 反馈闭环 决策引擎** | evolution_engine.py | Human-Gated | 评估标准影响所有质量门禁 |
| **M4-B 自动修复执行器** | auto_fixer.py | **Immutable Core**（**修正**：原 Human-Gated 偏低） | 执行器直接改代码，核心逻辑不可 AI 自主决策 |
| **M5 LLM 安全网关** | llm_security / input_sanitizer | Immutable Core | 安全网关 |
| **M5 Provenance Chain** | （集成 M2）| Immutable Core | 审计记录 |
| **M6 Session 接力** | session_carryover.py | Human-Gated | 必须含 agent_role + task_id |
| **M7 漂移检测算法** | drift_detector.py | AI-Modifiable | 算法可优化 |
| **M7 漂移检测阈值** | drift_thresholds.yaml | Human-Gated（**修正**） | 阈值影响审计 |
| **M8 代码健康度验证器** | code_health_validator.py | AI-Modifiable | 评分算法可 AI 优化 |
| **M8 代码健康度阈值** | health_thresholds.yaml | Human-Gated | 阈值变更需审批 |
| **M9 审计链** | provenance_chain.py | Immutable Core | 审计记录不可 AI 改 |
| **M10 Kill Switch** | kill_switch.py | Immutable Core | 触发/恢复需 Owner 确认 |
| **M11 不变量守卫** | invariant_rules.py | Immutable Core | 修改需 Owner + rationale-log |

### 2.4 容量保障组件（B3 施工图产出）

| 组件 | 权限 | 判定理由 |
|------|------|---------|
| `ai_audit_guard.py` 自身 | Immutable Core | 自身代码变更需 Owner 审批 |
| `audit_rules.yaml` | Human-Gated | 修改需 who/when/why 记录 |
| `capacity_slo.yaml` | Human-Gated | SLO 是治理"宪法" |
| `capacity_governance_loop.py` | AI-Modifiable | 每次执行记录指标 |
| `ai_provenance` 表 | Immutable Core | 只追加 + hash 链完整性 |
| `capacity_metrics` 表 | AI-Modifiable | 可追加可更新，留存 7 天 |
| `lazy_loader` | Human-Gated（**修正**：原 AI-Modifiable）| 影响启动顺序 |
| `config_validator` | Human-Gated（**修正**） | AI 改验证规则 = AI 定义合法 |
| `ZephyrLogger` 采样率 | Human-Gated（**修正**） | 影响审计完整性 |
| `ZephyrLogger` 日志级别 | AI-Modifiable | 实现细节 |

### 2.5 脚本系统组件（B4 施工图产出）

| 组件 | 权限 | 判定理由 |
|------|------|---------|
| AuditFinding Pydantic 模型 | Human-Gated | Schema 是契约可经审批后修改 |
| isolation_guard 装饰器 | Immutable Core | 阻断逻辑不可被绕过 |
| audit_rules.yaml | Immutable Core | 必须经 request_change + approve_change |
| meta_auditor.py 基础版 | Human-Gated | 抽样率变更需审批 |
| provenance_logger.py | Immutable Core | 审计日志不可删/改 |
| audit_rule_guard.py 钩子 | Immutable Core | pre-commit 不可跳过 |
| D12 幻觉检测参数（**修正**） | Human-Gated | 阈值影响安全判定 |
| AUD-SEC bandit 规则（**修正**） | Human-Gated | 安全策略可经审批新增 |
| C5 知识沉淀器 | AI-Modifiable + 隔离闸约束 | 闸已阻断闭环 |

### 2.6 双管线组件（B4 施工图产出）

| 组件 | 权限 | 判定理由 |
|------|------|---------|
| A3 ClarifyEngine | Human-Gated（**修正**：原 AI-Modifiable） | 制定规则边界 |
| B2 风控参数（Kill Switch / 熔断） | Immutable Core | 风控写入 Immutable，AI 不可改 |
| HallucinationDetector 阈值 | Human-Gated（**修正**） | 影响审计通过率 |
| CompletionAuditor 指标公式 | Human-Gated | 验收公式变更需 Owner |
| ExecutionCircuitBreaker Breaker Switch | Immutable Core | 不可由 AI 禁用 |

### 2.7 任务卡 / 知识库组件（B5 施工图产出）

| 组件 | 权限 | 判定理由 |
|------|------|---------|
| TagSchemaRegistry | Immutable Core | 元规则锁定，schema 变更走 rationale-log |
| InvariantGuard | Immutable Core | 不变量定义不可运行时改 |
| ProvenanceLogger | Immutable Core | 自身变更需走流程 |
| TagEngine | AI-Modifiable | 每次标签变更必须写 Provenance |
| AutoCleanScheduler（**修正**：原 Human-Gated） | **Immutable Core** | 删除规则不可改 |
| EpicAggregator / EpicVirtualRegistry（**修正**） | **Human-Gated** | Epic 创建涉及架构层级变更 |
| DomainLayerMapper | Human-Gated | 映射表修改需 Owner |
| KBCrawler | AI-Modifiable + 约束 | 输出只能写 quarantine |

### 2.9 运行时集成层（RI-01~07，**Wave 1 R83/R84 增补**）

> 来源：B6 施工图 `construction-plan-runtime-integration-and-cl-gaps.md`。**Wave 1 修正**项以加粗标注。

| 模块 | 路径 | 权限 | 判定理由 | 审批要求 |
|------|------|------|---------|---------|
| RI-01 ContextEngineRuntime | `src/zephyr/context_engine/runtime_integration.py` | Human-Gated | 上下文预算影响所有 AI 调用 | Owner 审批 |
| **RI-02 UnifiedMemoryAPI** | `src/zephyr/kb/unified_memory_api.py` | **Human-Gated**（**Wave 1 修正**：原草稿 AI-Modifiable 偏松）| 检索阈值影响 Agent 决策质量 | Owner 审批 |
| **RI-03 FileWatchRouter** | `src/zephyr/orchestrator/trigger_router.py` | **Human-Gated**（**Wave 1 修正**：原草稿 AI-Modifiable 偏松）| 路由策略影响 Agent 行为 | Owner 审批 |
| RI-04 FeedbackEngine M4-A decide | `src/zephyr/feedback_loop/decision_engine.py` | Human-Gated | 评估标准影响所有质量门禁 | Owner 审批 |
| **RI-04 FeedbackEngine M4-B auto_repair** | `src/zephyr/feedback_loop/auto_repair.py` | **Immutable Core**（Wave 0 R76 已锁，Wave 1 维持）| Self-Modification 递归风险 | Owner + R-XXX |
| RI-05 ProcessSandbox（L2a）| `src/zephyr/llm_security/process_sandbox.py` | Immutable Core | 安全核心 | Owner + R-XXX |
| RI-05 OutputValidator（L3 schema）| `src/zephyr/llm_security/output_validator.py` | Human-Gated | schema 可演进 | Owner 审批 |
| RI-05 EditorConfigGate（CL-021）| `src/zephyr/llm_security/editor_config_gate.py` | Immutable Core | 编码规则核心 | Owner + R-XXX |
| RI-06 HandoffAutoLoader | `src/zephyr/mcp/handoff_auto_loader.py` | Human-Gated | Session 状态管理 | Owner 审批 |
| **RI-07 DriftDetector 算法** | `src/zephyr/gates/drift_detector.py` | AI-Modifiable（**Wave 1 修正**：原整体 Human-Gated 偏紧，需拆分） | 算法可优化 | 写 Provenance |
| **RI-07 DriftDetector 阈值** | `config/drift_thresholds.yaml` | Human-Gated（**Wave 1 修正**） | 阈值影响审计 | Owner 审批 |

### 2.10 三件套新组件（CBAC / CBG / AlignmentMonitor，**Wave 1 R83/R84 增补**）

| 组件 | 路径 | 权限 | 判定理由 | 审批要求 |
|------|------|------|---------|---------|
| CBACRegistry / capabilities.yaml | `config/capabilities.yaml` | **Immutable Core** | 注册表 schema 是治理"宪法"，AI 不可改 | Owner + R-XXX |
| CapabilityChecker | `src/zephyr/shared/capability.py` | Immutable Core | 校验逻辑核心 | Owner + R-XXX |
| CircuitBreakerGateway | `src/zephyr/gates/circuit_breaker.py` | Immutable Core | 熔断不可由 AI 禁用 | Owner + R-XXX |
| circuit_breaker_state 表 | `data/circuit_breaker.db` | Immutable Core（追加专用） | 状态历史不可改写 | Owner |
| AlignmentMonitor| `src/zephyr/feedback_loop/alignment_monitor.py` | Human-Gated | 评估算法可演进，阈值需审批 | Owner 审批 |
| L2b 沙箱 ACL（ADR-0018）| 项目外 OS 级 | Immutable Core | OS 级 ACL 不由 RI 改（**Wave 1 C-03 裁决**）| Owner |

### 2.11 基础设施缺口组件（CL-017~021，**Wave 1 R83/R84 增补**）

| 组件 | 路径 | 权限 | 判定理由 |
|------|------|------|---------|
| CL-017 system_snapshot() | `src/zephyr/context_engine/system_snapshot.py` | Human-Gated | snapshot 输出影响 AI 决策起点 |
| CL-018 DocCompressor | `src/zephyr/context_engine/doc_compressor.py` | Human-Gated | 压缩规则需审批 |
| **CL-018 CompressionPolicy YAML** | `config/compression/policy.yaml` | **Immutable Core**（**Wave 1 V-14 兜底**：防 Self-Modification）| 规则不可由 AI 改 |
| CL-019 ai-onboarding-guide.md 核心思想章 | `docs/01_policies_and_standards/ai-onboarding-guide.md` | Human-Gated | 文档可演进 |
| CL-020 master-registry-index| `docs/01_policies_and_standards/master-registry-index.md` | Human-Gated | 注册表 schema 演进 |
| CL-021 EditorConfigGate（同 RI-05）| 见 §2.9 | Immutable Core | 编码规则核心 |
| **Wave 1 V-14 BlueprintOverlapMergeGate** | `scripts/governance/validate_blueprint_overlap.py` | Immutable Core（**Wave 1 兜底**）| 治理门禁，自身不可被绕过 |
| **Wave 1 V-15 TruthSourceCascadeValidator** | `scripts/governance/validate_truth_source_cascade.py` | AI-Modifiable（**Wave 1 兜底**）| 追踪报告，需 Owner 审批同步 |
| **Wave 1 V-16 DraftsZoneLifecycleArchiver** | `scripts/governance/archive_drafts_zone.py` | Human-Gated（**Wave 1 兜底**）| 归档触发需 Owner 确认 |

### 2.8 元层（治理 / 文档 / 协议）

| 模块 | 权限 | 判定理由 |
|------|------|---------|
| 原则文档（vibe-coding-principles）| Immutable Core | 治理"宪法" |
| capacity-assurance 施工图 | Human-Gated（**修正**：原 Immutable Core） | 施工图可演进非"宪法" |
| handoff-protocol.md | Immutable Core | Session 交接协议宪法 |
| ai-autonomy-authority-registry.md（本文件）| Immutable Core | 权限注册表，自身变更需 Owner |
| directory-structure-standard.md | Human-Gated | 可演进 |
| architecture-rationale-log.md | Immutable Core（追加专用） | 历史记录不可改写 |

---

## 三、权限错误率统计与修正

| 来源文档 | GLM 权限错误数 | 修正后 |
|----------|---------------|-------|
| script-system-design | 3 处（30%） | 已修正 |
| infrastructure-7-modules | 2 处（20%）+ 缺标注 | 已修正 |
| principles-and-positioning | 4 处（含 Provenance Chain 缺失）| 已修正 |
| two-pipelines-design | 2 处（15%） | 已修正 |
| task-card-knowledge-base | 2 处严重错误（25%）| 已修正 |
| **合计** | **13 处错误** | **本表已全部修正** |

---

## 四、变更流程

### 4.1 修改本注册表
1. 提交 PR 修改本文件
2. Owner 直接审批
3. 同 commit 追加 R-XXX 到 architecture-rationale-log.md
4. 同 commit 更新所有相关模块代码注释

### 4.2 修改某模块的权限标注
- 不修改本表 = 错误。所有权限变更**必须先改本表**，再改代码注释

### 4.3 新增模块时
- 必须在本表登记权限层级
- 未登记 = pre-commit 拒绝
- **路径唯一性约束**：同一路径不得在多个节中出现——若模块同时属于业务层（§2.1/§2.2）与基础设施层（§2.3），仅在最能代表其核心职责的节中登记。发现重复路径 = 注册表腐败（对标 ITIL SACM CMDB corruption → 同一 CI 两条矛盾记录）

---

## 五、与已有规范的关系

- ADR-0010：定义三层权限语义（本表是其执行层）
- ADR-0022：LPC 双轨治理

---

## 六、版本历史

- v1.0.0（2026-04-27）：Wave 0 终审兜底缺口 V-11 产出，覆盖全 60+ 模块/组件，修正 13 处权限错误
- **v1.1.0（2026-04-27 Wave 1 R84）**：增补 §2.9 RI-01~07 运行时集成模块（11 行）+ §2.10 CBAC/CBG/AlignmentMonitor 三件套（6 行）+ §2.11 CL-017~021 基础设施缺口组件（9 行）；修正 4 处 Wave 1 草稿权限误标（RI-02 偏松→Human-Gated / RI-03 偏松→Human-Gated / RI-04 拆分缺失→M4-A/M4-B 分层 / RI-07 偏紧→算法/阈值拆分）；引入 Wave 1 兜底 V-14/V-15/V-16 三个治理组件权限。frontmatter 同步追加 arbitration_wave1 块（Claude-Opus-4.7 / R-84）。
- **v1.2.0（2026-04-30 beta）**：新增 §七 dev/prod 双模式权限表，区分开发环境与生产环境的 AI 自治权限差异。
- **v1.2.1（2026-05-01 Phase 5）**：date/valid_from→2026-05-01；depends_on 补 ADR-0010（三层权限语义来源）。
- **v1.2.2（2026-05-02）**：修复 F-A5 注册表内部冲突——kb 模块在 §2.2（AI-Modifiable）与 §2.3 M2（Human-Gated）权限矛盾。§2.2 删除 kb 行（过渡期知识库实现 → 已收敛至 §2.3 M2）；§2.3 M2 按子模块拆分 kb（基础设施 Human-Gated / 加工链 AI-Modifiable）；§4.3 新增路径唯一性约束（对标 ITIL SACM CMDB corruption → 同一路径双重登记 = 腐败）。

---

## 七、dev/prod 双模式权限表

> 本章节定义 AI 在开发环境（dev）与生产环境（prod）下的自治权限差异。
> 核心原则：**dev 宽松、prod 严格**——dev 允许试错，prod 零容忍。

### 7.1 环境判定规则

| 判定条件 | 环境 |
|---------|------|
| 文件路径包含 `drafts-and-audits/` | dev |
| 文件 status 为 `draft` | dev |
| 文件路径在 `docs/` 且 status 为 `active` | prod |
| 文件路径在 `src/zephyr/` 且已部署到生产服务器 | prod |
| 无法判定时 | **默认 prod**（安全优先） |

### 7.2 双模式权限对照表

| 操作类型 | dev 权限 | prod 权限 | 差异说明 |
|---------|---------|----------|---------|
| 创建新文件 | AI-Modifiable | Human-Gated | prod 必须 Owner 审批 |
| 修改 frontmatter | AI-Modifiable | Human-Gated | prod 修改元数据需审批 |
| 修改规则内容（ABS） | Human-Gated | Immutable Core | prod ABS 规则不可修改 |
| 修改规则内容（COND） | AI-Modifiable | Human-Gated | prod COND 规则需审批 |
| 删除文件 | Human-Gated | Immutable Core | prod 禁止删除，只能 deprecated |
| 执行交易操作 | 禁止 | Human-Gated | dev 禁止交易，prod 需审批 |
| 修改风控参数 | AI-Modifiable（测试值） | Immutable Core | prod 风控参数不可 AI 修改 |
| 修改数据源配置 | AI-Modifiable（测试源） | Human-Gated | prod 数据源需审批 |
| 运行回测 | AI-Modifiable | AI-Modifiable | 两环境均可 |
| 生成报告 | AI-Modifiable | AI-Modifiable | 两环境均可 |
| 触发 kill switch | AI-Modifiable | AI-Modifiable | 两环境均可（紧急安全） |
| 修改 kill switch 规则 | Human-Gated | Immutable Core | prod 不可修改 |

### 7.3 环境切换规则

- 从 dev 切换到 prod：必须通过 Phase Gate 检查（参见 GOV-MOD-002 铁律8）
- 任何文件从 `draft` 变为 `active` 时，该文件的 AI 自治权限自动从 dev 模式切换到 prod 模式
- 禁止在 prod 环境下使用 dev 权限操作
