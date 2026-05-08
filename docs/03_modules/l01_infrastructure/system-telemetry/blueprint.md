---
module_id: "MOD-INF-015"
title: "System Telemetry 蓝图 — 全系统可观测性：指标/日志/链路/AI行为/存档/剖析/健康/告警/Schema"
doc_type: blueprint
status: Draft
version: "0.9.0"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: phase_2_complete
belongs_to: "MOD-MASTER-001"
summary: "ZephyrAlpha System Telemetry 蓝图——全系统可观测性平台：9个子系统通过统一接入点 Telemetry 门面类暴露；覆盖三层信号(4 Golden Signals + USE + Annotations) + 多环境隔离；指标命名空间防冲突；批量上报API；DLQ 保障数据质量闭环；配置热更新零重启；Meta-Telemetry自体内省。对接已有 shared 基础设施。三层闭环：AI开发闭环（Telemetry→MCP→AI自我修正）+ 运营闭环（FLE自动派单→Backpressure→自愈/Escalation）+ 治理闭环（Schema Registry→漂移检测→DLQ自动修复）。对齐 OTel GenAI + AI Agent 语义约定。搭配合成监控、告警测试、CI/CD 可观测性、Counter重置检测、Error Taxonomy、遥测成本预算、数据安全(加密+防篡改+OWASP MCP08)、Observability-as-Code、Schema版本化、时钟偏差检测、AI自我修正效能追踪。针对100% AI施工+氛围编程+1人+AI维护语境深度优化。\n\n> **唯一真源裁定(2026-05-06)**：本蓝图(MOD-INF-015)是 L12 System Telemetry 的 CANONICAL SSoT。原 MOD-L12-001(C轨占位, 2026-05-05, 0.1.0) 已完全吸收——其全量内容逐条对账确认融入本蓝图 v0.9.0，原占位文件已安全删除。L12 系统遥测层不再存在双真源。"
tags: [telemetry, system-telemetry, l12, metrics, logs, traces, ai-behavior, observability, infrastructure, profiling, health-check, alerting, schema-registry, finops, vibe-coding, self-healing, backpressure, feature-flags, multi-environment, disaster-recovery, developer-experience, dead-letter-queue, hot-reload, opentelemetry-genai, synthetic-monitoring, error-taxonomy, slo-registry, ci-cd-observability, self-describing-telemetry, counter-reset, cost-budget, metric-discovery, agent-observability, data-security, tamper-evident, owasp-mcp08, observability-as-code, schema-versioning, clock-skew, ai-self-correction, zombie-metrics, graceful-shutdown, metric-namespacing, bulk-report, meta-telemetry, c-track-merged, DO-NOT-IMPLEMENT-superseded, single-source-of-truth, absorbed-mod-l12-001]
priority: P1
# Phase 6：telemetry 不产生自指；运行时消费者见 references。
depends_on:
  - {target: "MOD-INF-012", at: "全篇", why: "Database——olap_engine持久化FLE时序分析结果"}
  - {target: "MOD-INF-024", at: "全篇", why: "Budget Enforcer——成本metrics聚合到预算追踪"}
  - {target: "MOD-INF-022", at: "全篇", why: "Escalation Protocol——告警升级到人工处理"}
  - {target: "MOD-INF-018", at: "全篇", why: "Agent RBAC——L6 Observability 以 Telemetry 为数据后端"}
  - {target: "MOD-INF-016", at: "全篇", why: "Shared Infrastructure——shared/logging / lifecycle / flags / observer 等基础组件"}
  - {target: "MOD-INF-014", at: "全篇", why: "LLM Security——AI行为安全事件通过LSG gateway联动"}
references:
  - {id: "MOD-INF-010", at: "全篇", why: "FLE 消费 metrics/logs——仅存 references"}
  - {id: "MOD-INF-020", at: "全篇", why: "审计写入遥测-derived 事件——仅存 references"}
---

# System Telemetry 蓝图

> **module_id**: MOD-INF-015 | **version**: 0.9.0 | **status**: draft | **layer**: L12

> **真源声明**：本蓝图的 canonical SSoT 为 `src/zephyr/l12_system_telemetry/` 代码目录。
> 代码落位：`src/zephyr/l12_system_telemetry/`（9 子模块，当前骨架），统一通过 `Telemetry` 门面类暴露。

> **对标**：Google SRE 4 Golden Signals + USE Method + RED Method + OpenTelemetry 规范（traces/metrics/logs/baggage/profiles）。
> **三层闭环架构**：AI开发闭环（Telemetry→MCP→AI自我修正）+ 运营闭环（FLE自动派单→Backpressure→自愈/Escalation）+ 治理闭环（Schema Registry→漂移检测→DLQ→AI自动修复）。
> **基础设施对接**：复用 shared/logging (TraceContext + get_logger) + shared/lifecycle (LifecycleAware + ModuleHealth) + shared/flags (FeatureFlag 三态控制 + 文件监听热更新) + shared/observer (EventBus) + shared/contracts/backpressure (Throttle/Pause/Resume) + shared/contracts (CTR-TRACE-001 + CTR-P1-013)。
> **施工落地**：模块一行 `Telemetry(module_id)` 即获得全部九子系统接入能力，AI 不用记忆子系统 API。

---

## 1. 概述

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-015 |
| 代码落位 | `src/zephyr/l12_system_telemetry/` |
| 核心职责 | 全系统可观测性——采集/存储/查询所有组件的运行时数据 + AI可消费的运行时反馈 |
| 设计原则 | 每个模块自上报→Telemetry聚合→三层闭环（AI开发/运营/治理） |
| 目标用户 | AI Agent（通过MCP消费遥测）+ 1人维护者（通过Dashboard/Feishu告警） |

### 核心职能

System Telemetry 是 ZephyrAlpha 的**"神经系统"**——感知所有模块的健康状态，将原始信号转化为可操作的洞察。它与 FLE（Feedback Loop Engine）配合：**Telemetry 负责"看见"，FLE 负责"行动"**。

### 三层闭环架构

```
┌─────────────────────────────────────────────────────┐
│ 闭环1：AI开发闭环                                     │
│   AI生成代码 → 部署运行 → Telemetry采集 → MCP反馈    │
│   → AI读取遥测自我修正 → 生成修复代码                  │
├─────────────────────────────────────────────────────┤
│ 闭环2：运营闭环                                       │
│   Telemetry采集 → FLE异常检测 → 自动派单              │
│   → 自愈(KillSwitch/Degrade/Rollback)                │
│   → 无法自愈→Escalation Protocol→Feishu通知人工       │
├─────────────────────────────────────────────────────┤
│ 闭环3：治理闭环                                       │
│   Schema Registry → 运行时校验 → 漂移检测             │
│   → 蓝图同步 → AI下次session提示不一致                 │
└─────────────────────────────────────────────────────┘
```

---

## 2. 四大黄金信号

对标 Google SRE 4 Golden Signals：

| 信号 | 维度 | 采集来源 | 阈值示例 |
|------|------|---------|---------|
| **Latency**（延迟） | LLM API 响应时间 / 脚本执行时长 / Pipeline 端到端耗时 | MCP servers / subprocess tracker | P95 > 30s → FLE 告警 |
| **Errors**（错误） | LLM 调用失败 / Gate 拒止 / 校验不通过 | Gate Engine / CE / Script System | 错误率 > 5% → FLE 自动降级 |
| **Traffic**（流量） | LLM 调用总量 / 任务卡生成速率 / API 请求 QPS | Pipeline / LSG / MCP | LLM QPS > 100 → Token Budget 预警 |
| **Saturation**（饱和度） | Context Engine Token 填充率 / VMS Collection 占用 / DB 连接池 | CE / VMS / Database | CE 填充 > 90% → 自动截断旧 Session |

---

## 2b. 资源层 USE 信号

> 对标 Netflix/Google SRE USE Method（Utilization / Saturation / Errors）。覆盖 4 Golden Signals 达不到的资源层盲区。对 AI 生成代码场景尤其重要——内存泄漏、文件句柄泄漏只有这一层能发现。

| 信号 | 维度 | 采集来源 | 阈值示例 |
|------|------|---------|---------|
| **Utilization**（利用率） | CPU 使用率 / 内存占用 / 磁盘使用率 / GPU 利用率 | psutil / OS metrics / nvidia-smi | CPU > 80% 持续 5min → FLE 告警 |
| **Saturation**（饱和） | 磁盘 IO 队列深度 / 网络连接数 / 文件句柄数 / 进程数 | OS metrics / /proc / iostat | 文件句柄 > 800 → 泄漏预警 |
| **Errors**（资源错误） | OOM Kill / 磁盘满 / 网络不可达 / GPU OOM | OS events / dmesg / kernel log | 任意硬件级错误 → P0 立即通知 |

---

## 2c. 事件标注（Annotations）

> 所有变更事件自动注入遥测时间线——回答"是不是上次变更引入的？"

| 事件类型 | 注入内容 | 触发时机 | 消费方 |
|---------|---------|---------|--------|
| **部署事件** | version_from / version_to / deployer / commit_sha | CI/CD 管线触发 | Dashboard 时间线标注 |
| **配置变更** | config_key / old_value / new_value / who | 配置文件写入检测 | FLE 关联异常 |
| **模型切换** | model_from / model_to / reason | AI Router 切换模型 | ai_behavior 追踪 |
| **蓝图变更** | blueprint_id / version_from / version_to / who | 蓝图文件写入 | 蓝图漂移检测 |
| **Feature Flag 变更** | flag_name / state_change / rollout_pct | 特性开关切换 | Experimentation 层 |

---

## 2d. 多环境隔离 🆕

> **B21 修复**——v0.5.0 新增。1人+AI 场景下 dev/staging/prod 可能共存在同一台机器。Telemetry 数据必须按环境物理隔离，防止 dev 的噪音污染 prod 的告警。

### 环境标签

所有遥测数据（MetricPoint / Log / Span / AIBehaviorEvent）**MUST** 携带 `environment` 标签：

| 环境 | 标签值 | 用途 |
|------|:---:|------|
| **dev** | `dev` | 日常开发调试，FLE 不告警（仅记录） |
| **staging** | `staging` | 预发布验证，FLE 降级告警（仅 P0 通知） |
| **prod** | `prod` | 生产环境，FLE 全级别告警 |

### 数据路径隔离

```
data/telemetry/
├── dev/           ← dev 环境遥测数据（14 天 TTL）
│   ├── metrics/
│   ├── logs/
│   └── traces/
├── staging/       ← staging 环境遥测数据（30 天 TTL）
│   └── ...
└── prod/          ← prod 环境遥测数据（90 天 TTL）
    └── ...
```

### 环境感知行为差异

| 行为 | dev | staging | prod |
|------|:---:|:---:|:---:|
| **profiling 采集** | OFF（FeatureFlag 控制） | ON（采样率 50%） | ON（采样率 100%） |
| **trace 采样率** | 100%（debug 全量） | 10%（正常采样） | 10%（正常采样，error 全保留） |
| **日志级别** | DEBUG | INFO | WARNING（过滤 DEBUG/INFO） |
| **FLE 异常检测** | OFF（仅记录） | ON（仅 P0 告警） | ON（全级别） |
| **告警通知** | 不发送 | 仅发送 P0 → Feishu | 全级别 → Feishu |

---

## 2e. FeatureFlag 控制矩阵 🆕

> **B20 修复**——v0.5.0 新增。所有 Telemetry 实验性或资源敏感功能 MUST 由 `shared/flags.py` 的 FeatureFlag 三态开关守护。AI 新增的功能初始为 OFF，人工在 `config/` 中启用后才生效。

| Flag Key | 控制功能 | 默认值 | 开关影响的子系统 |
|---------|------|:---:|------|
| `telemetry.enable_profiling` | profiling 子系统全量开关 | OFF | §9 profiles |
| `telemetry.debug_full_sampling` | 临时将 trace 采样率提到 100%（排障用） | OFF | §6 traces |
| `telemetry.cost_alert_threshold_usd` | 日 LLM 成本告警阈值 | 5.0 | §7 ai_behavior → §11 alerts |
| `telemetry.log_level_override.{module}` | 按模块覆盖日志级别（如 `telemetry.log_level_override.pipeline = DEBUG`） | 无覆盖 | §5 logs |
| `telemetry.enable_ai_behavior_tracking` | AI 行为 7 维度全量追踪 | ON | §7 ai_behavior |
| `telemetry.cardinality_strict_mode` | 严格基数模式：超限指标直接拒绝（而非聚合） | OFF | §4 metrics |
| `telemetry.archive_auto_cleanup` | 过期归档自动物理删除 | ON | §8 archive |
| `telemetry.enable_slo_postmortem` | SLO 违规自动生成 Postmortem 草稿 | OFF | §11 alerts → Audit Trail |

### AI 施工约定（FeatureFlag）

```
1. AI 新增任何 Telemetry 功能时 MUST 同时创建对应的 FeatureFlag（初始 OFF）
2. AI 禁止自行修改 FlagState——修改 flag 是人工运维权限
3. 所有采集频率/采样率/阈值参数 SHOULD 通过 FeatureFlag 暴露，不做硬编码
4. 每次 AI session 启动时检查 FeatureFlag 状态（§14 AI session 冷启动工作流）
```

## 2f. OpenTelemetry GenAI + AI Agent 语义约定对齐 🆕

> **B44 修复**——v0.7.0 新增。OTel 于 2025 年 9 月发布了 GenAI Semantic Conventions（v1.37+），定义了 LLM 调用的标准 trace span 属性；2025 年 11 月 Traceloop/OpenLLMetry 提交了 AI Agent Observability RFC（20 种 span 类型 + 300+ 属性）。Honeycomb 2026 年 3 月发布 MCP 集成 + AI Agent Monitoring；Datadog 2025 年 6 月 DASH 大会发布 AI Agent Monitoring。全行业正在用一套统一语义描述 AI 系统的可观测性数据。Telemetry 蓝图必须显式对齐这一标准，否则 AI 生成的遥测数据无法被行业标准工具消费。

### 对齐范围声明

Telemetry 的 ai_behavior + traces 子系统**不自行发明语义**——它们是对 OTel GenAI + Agent 语义约定的合规实现。字段命名遵循 `gen_ai.*` 前缀体系。

### OTel GenAI Span 属性映射（§7 ai_behavior + §6 traces）

| OTel GenAI 标准属性 | Telemetry 对应字段 | 映射说明 |
|---------------------|-------------------|---------|
| `gen_ai.operation.name` | `AIBehaviorEvent.event_type` | `chat` / `text_completion` / `tool_call` |
| `gen_ai.provider.name` | `AIBehaviorEvent.labels["provider"]` | `openai` / `anthropic` / `gcp.gen_ai` |
| `gen_ai.request.model` | `AIBehaviorEvent.model_id` | 模型名（如 `gpt-4`） |
| `gen_ai.request.temperature` | `AIBehaviorEvent.labels["temperature"]` | 生成参数 |
| `gen_ai.request.max_tokens` | `AIBehaviorEvent.labels["max_tokens"]` | 最大 token 数 |
| `gen_ai.usage.input_tokens` | `AIBehaviorEvent.input_tokens` | 输入 token 数 |
| `gen_ai.usage.output_tokens` | `AIBehaviorEvent.output_tokens` | 输出 token 数 |
| `gen_ai.response.finish_reason` | `AIBehaviorEvent.labels["finish_reason"]` | `stop` / `length` / `tool_calls` |
| `gen_ai.conversation.id` | `AIBehaviorEvent.labels["conversation_id"]` | 对话/会话 ID |
| `gen_ai.request.seed` | `AIBehaviorEvent.labels["seed"]` | 可复现性种子 |
| `gen_ai.system` | `AIBehaviorEvent.labels["gen_ai_system"]` | 系统标识 |
| `gen_ai.output.type` | `AIBehaviorEvent.labels["output_type"]` | `text` / `json` / `image` |

### OTel AI Agent 语义约定对齐（RFC 2025-11）

ZephyrAlpha 的 Pipeline/TaskCard 元模型与 AI Agent RFC 定义的 20 种 span 类型存在直接映射关系。Telemetry traces 子系统在采集以下 OTel Agent span 类型时 MUST 使用标准命名：

| OTel Agent Span 类型 | ZephyrAlpha 对应场景 | Span 命名 |
|----------------------|---------------------|---------|
| `gen_ai.agent.invoke` | M1/M6/M8 Agent 执行 | `gen_ai.agent.invoke {agent_name}` |
| `gen_ai.task.create` | TaskCard 创建 | `gen_ai.task.create {task_id}` |
| `gen_ai.task.execute` | TaskCard Pipeline 执行 | `gen_ai.task.execute {task_id}` |
| `gen_ai.task.delegate` | Orc 分配子任务 | `gen_ai.task.delegate` |
| `gen_ai.tool.execute` | Script D1-D12 / 工具调用 | `gen_ai.tool.execute {tool_name}` |
| `gen_ai.workflow.execute` | Pipeline 编排执行 | `gen_ai.workflow.execute {pipeline_id}` |
| `gen_ai.workflow.transition` | Gate G0→G1→...→G7 | `gen_ai.workflow.transition {gate_id}` |
| `gen_ai.session` | AI Session top-level | `gen_ai.session {session_id}` |
| `gen_ai.guardrail.check` | Gate Engine 门禁判定 | `gen_ai.guardrail.check {gate_id}` |
| `gen_ai.human.review` | Human-in-the-loop 审批 | `gen_ai.human.review {review_id}` |
| `gen_ai.memory.retrieve` | CE 上下文检索 | `gen_ai.memory.retrieve` |
| `gen_ai.memory.store` | 知识库写入 | `gen_ai.memory.store {kb_id}` |
| `gen_ai.context.checkpoint` | Session 状态快照 | `gen_ai.context.checkpoint` |

### OTel GenAI Metrics 对齐

| OTel GenAI Metric | Telemetry SLI 对应 | 说明 |
|-------------------|-------------------|------|
| `gen_ai.client.token.usage` (Histogram) | `Token消耗总量` counter | 按 token_type= input/output 区分 |
| `gen_ai.client.operation.duration` (Histogram) | `LLM API 响应时间` histogram | P50/P90/P95/P99 |

### AI 施工约定（语义对齐）

```
1. ai_behavior 子系统字段命名 MUST 可一对一映射到 OTel gen_ai.* 属性
2. traces 子系统 Span 名称 MUST 遵循 gen_ai.<component>.<operation> 风格
3. 新增 AI 行为维度时 MUST 先查 OTel semantic conventions registry，优先使用标准属性
4. 蓝图 §3b 中 TelemetryEmitter 契约 MUST 兼容 OTel 属性类型（string/int/bool/float only）
5. 禁止为已有 OTel 标准属性发明替代命名——统一使用 gen_ai.* 前缀
6. 未来 OTel Agent conventions 从 RFC→Stable 后，Telemetry MUST 在 2 个版本内同步更新
```

## 2g. Telemetry 数据安全与合规 🆕

> **B56+B58+B59 修复**——v0.8.0 新增。OWASP 于 2025 年 Q2 发布了 MCP Top 10 安全风险，其中 MCP08:2025（Lack of Audit and Telemetry）定义了 AI Agent 系统的遥测安全基准。OTel 官方文档将敏感数据处理（PII masking、attribute redaction、data minimization）列为基础设施责任。GAOP（Governance-Aware Observability Pipeline，2025 年 IJCA 论文）提出将合规治理嵌入遥测管线。对 1 人维护场景，数据安全不是合规部门的压力，而是防止"遥测数据泄露 = 系统架构级暴露"的最后防线。

### OWASP MCP08:2025 对齐声明

Telemetry 蓝图 MUST 满足 OWASP MCP08 的核心要求：

| OWASP MCP08 要求 | Telemetry 实现 | 状态 |
|------------------|---------------|:---:|
| Structured tamper-evident logging | §2g HMAC chain + append-only store | 🆕 本版本新增 |
| SIEM/centralized monitoring | Telemetry 自身即 centralized monitoring | ✅ §1 概述 |
| PII-safe logging (tokenize/mask) | §5 logs PII 脱敏（已存在）+ §2g field-level redaction 扩展 | 🆕 增强 |
| Field-level encryption for secrets | §2g encryption-at-rest for PII fields | 🆕 本版本新增 |
| Data classification labels | §5 sensitivity_level (public/internal/confidential/secret) | ✅ 已存在 |
| Behavioral baselines for anomaly | FLE基线建模 + §7 ai_behavior 7维追踪 | ✅ 已存在 |
| Access control & segregation | §2g telemetry file permissions + RBAC (L6) | 🆕 增强 |
| Log retention aligned with compliance | §8 archive TTL (30/90days) | ✅ 已存在 |
| Continuous audit verification | §12 drift detection + audit drill | 🆕 §12 已覆盖 |

### 加密策略（Encryption at Rest）

| 数据层 | 加密方式 | 密钥管理 |
|--------|---------|---------|
| **SQLite metrics DB** | SQLite Encryption Extension (SEE) 或 SQLCipher (AES-256) | 密钥从环境变量 `TELEMETRY_DB_KEY` 读取，不写入文件 |
| **JSONL logs** | 不整体加密（影响查询效率），但 PII 字段用 AES-256-GCM 逐字段加密 | 独立 per-field key |
| **DLQ JSONL** | 不加密（DLQ 是问题暴露窗口，需要 AI 快速消费），但 PII 字段 redact/mask | — |
| **archive gzip** | gzip 压缩本身不加密，archive 目录可选择性 AES-256 全量加密 | 通过 FeatureFlag `telemetry.archive_encryption` 控制（默认 OFF） |
| **config/ YAML SSoT** | 不加密（在 git 中，不应含密钥），密钥通过环境变量注入 | 环境变量 → OS keyring / 1Password CLI |

### 防篡改日志（Tamper-Evident Logging）

```
HMAC Chain 防篡改:
  每条 JSONL log line 增加 integrity 字段:
    {
      "...": "...",
      "integrity": {
        "hmac_sha256": "base64(HMAC-SHA256(secret, line_index + prev_hmac + log_body))",
        "line_index": 123456
      }
    }
  → 链式 HMAC：修改任一行 → 后续所有行的 HMAC 失效
  → 每 24h 自动校验 integrity chain → 发现断裂 → P1 安全事件
  → 校验通过率 < 99.9% → 自动从 archive replay 重建
  → HMAC secret 独立于 DB key，从环境变量 TELEMETRY_HMAC_SECRET 读取
```

### PII 字段级脱敏扩展

```
日志脱敏规则扩展（§5 现有 PII masking 的增强）:
  - email: user@domain.com → u***@domain.com
  - API key: sk-abc123... → sk-**** (保留前缀以区分来源)
  - IP address: 192.168.1.1 → 192.168.*.* (保留 /24 网段)
  - file path: 保持功能路径但脱敏用户名（如 C:\Users\johndoe\... → C:\Users\****\...）
  - phone/card/SSN: 完全删除或替换为 [REDACTED]
```

### 遥测数据访问控制

| 访问者 | 最小权限 | 审计 |
|--------|---------|:---:|
| **Telemetry 自身进程** | 读写 data/telemetry/{env}/ | 自身操作不审计 |
| **FLE** | 只读 metrics 表 + 只读 logs JSONL（最近 24h） | 查询记录写入 telemetry_access_log |
| **AI Agent (MCP)** | 只读 MCP tools 暴露的聚合数据（不暴露原始文件） | MCP tool call 自动生成 audit event |
| **1 人维护者** | 全权访问（但通过受控接口） | 文件系统级操作仅本地 |
| **外部模块** | 仅写入自身模块的 metrics/logs（不可读其他模块） | module_id 标签强制绑定 |

### AI 施工约定（安全）

```
1. 禁止在日志/指标/span 中硬编码 API Key / Token / Secret——所有密钥通过环境变量注入
2. 新增 Log 字段时 MUST 评估是否为 PII，若是 → 自动标记 sensitivity_level=confidential
3. 禁止 AI Agent 绕过 MCP 直接读取 data/telemetry/ 原始文件
4. HMAC secret 和 DB key 永远不写入 config/ YAML——仅通过环境变量传递
5. 安全事件（integrity breach / unauthorized access） → P1 即时 Feishu 通知人工
```

---
## 2h. Observability-as-Code 声明 🆕

> **B70+B71+B72 修复**——v0.8.0 新增。Grafana 12（2025 年 5 月）正式将 Observability-as-Code 推入主流：Git Sync、grafanactl CLI、Dashboard Schema v2、Foundation SDK。Sentry（2025 年 12 月 BIX-Tech 报告）将 "12 trends" 中的第 1 条列为 OTel Everywhere。氛围编程社区的核心实践是：所有可观测性配置（dashboards、alerts、SLIs、schemas）与业务代码同仓版本化，通过 CI/CD 部署。Telemetry 蓝图的 config/ 产出物必须遵循这一范式。

### 版本化清单

| 产出物 | 格式 | Git 路径 | 部署方式 |
|--------|------|---------|---------|
| `metrics_schema.yaml` | YAML SSoT | `config/metrics_schema.yaml` | 运行时热加载（§3d） |
| `sli_registry.yaml` | YAML SSoT | `config/sli_registry.yaml` | 运行时热加载 |
| `alert_rules.yaml` | YAML SSoT | `config/alert_rules.yaml` | 运行时热加载 |
| `flags.yaml` | YAML SSoT | `config/flags.yaml` | shared/flags 文件监听 |
| `dashboards/` | YAML/JSON (Grafana-compatible) | `config/dashboards/` | grafanactl push 或本地加载 |

### CI/CD 集成约束

```
CI/CD Pipeline 中的 Observability-as-Code 步骤:
  1. Lint:     yamllint config/*.yaml
  2. Validate: Telemetry schema validator → 校验所有 YAML SSoT
  3. Diff:     与上一个 git commit 的 diff → 生成 changelog
  4. Test:     dry-run alert rules with historical data（§11b backtest）
  5. Deploy:   合并到 main 后自动生效（热加载）或通过 grafanactl push dashboards
  6. Verify:   Post-deploy 合成监控事务（§11b synth.*）
```

### AI 施工约定（OaC）

```
1. 所有可观测性配置 MUST 在 config/ 目录，与业务代码同仓 git 管理
2. 禁止在 Grafana UI 中手动编辑 Dashboard——Dashboard 定义从 config/dashboards/ 加载
3. Alert rules / SLI registry / Schema 变更 MUST 通过 git PR → 人工确认 → merge → 热加载
4. AI 发现配置问题 → 自动生成 PR 修改 config/ YAML（而非直接修改运行中的配置）
```

---
## 3. 九子系统

> **契约兼容声明（B27）**：所有新定义的数据类（MetricPoint, AIBehaviorEvent, HealthReport, Span 等）是 `shared/contracts/telemetry_emitter.py`（CTR-P1-013 TelemetryEmitter）的合规实现。不得定义与 TelemetryEmitter 冲突的接口。**语义对齐声明（B44）**：AI 行为相关字段命名 MUST 可映射到 OTel GenAI + Agent Semantic Conventions（§2f）。

```
src/zephyr/l12_system_telemetry/
├── metrics/       ← 数值指标：LLM调用次数 / Gate通过率 / 任务完成率
├── logs/          ← 结构化日志：JSON log→CE注入 / Gate审计 / Pipeline异常
├── traces/        ← 分布式链路：TaskCard全生命周期追踪（draft→pipeline→complete）
├── ai_behavior/   ← AI行为监控：模型选择频率 / Token消耗 / Gate命中率 / 幻觉率
├── archive/       ← 历史存档：冷数据压缩归档（>30天）
├── profiles/      ← 🆕 连续性能剖析：CPU/内存火焰图 / 热点函数定位
├── health/        ← 🆕 自体监控：Telemetry自身健康 + 独立watchdog + 心跳
├── alerts/        ← 🆕 告警路由：Multi-window Burn Rate告警 + 通知通道 + 静默/聚合
└── schema/        ← 🆕 指标Schema注册表：统一指标定义 + 运行时校验 + 漂移检测
```

| 子系统 | 职责 | 数据格式 | 消费方 | 施工状态 |
|--------|------|---------|--------|:---:|
| **metrics** | SLI/SLO 与业务指标流 | `MetricPoint {name, value, timestamp, labels, type, exemplar}` | FLE / Capacity Assurance / Budget Enforcer | 🟡 骨架 |
| **logs** | 结构化日志聚合与检索 | JSON Lines（`event_id` + `module` + `level` + `trace_id` + `span_id`） | Gate Engine / Audit / FLE | 🟡 骨架 |
| **traces** | TaskCard 全链路追踪 + W3C TraceContext 传播 | Span（Root→M1→G2→Orc→Script→Complete） | Pipeline / Debug / FLE | 🟡 骨架 |
| **ai_behavior** | AI 模型行为画像（含成本） | 模型选择日志 / Token消耗 / Gate命中率 / $成本 / 幻觉评分时序 | FLE / Capacity Assurance / Budget Enforcer | 🟡 骨架 |
| **archive** | 冷数据压缩归档 | gzip JSONL（30天后自动归档，90天物理删除） | 审计回溯 | 🟡 骨架 |
| **profiles** | 🆕 CPU/内存连续性能剖析 | pprof / OTel Profiles over OTLP | FLE（性能回归检测） | ⚪ 待建 |
| **health** | 🆕 自体监控 + 独立 watchdog | HealthCheck {service, status, uptime, error_rate} | Watchdog进程 / FLE | ⚪ 待建 |
| **alerts** | 🆕 告警路由引擎 + 多通道通知 | AlertRule {SLI, burn_rate_window, threshold} + NotificationChannel | FLE → Feishu/钉钉/Email | ⚪ 待建 |
| **schema** | 🆕 指标 Schema 注册 + 漂移检测 | MetricSchema {name, type, labels, unit, owner} | 全模块（写入校验）+ 蓝图漂移检测 | ⚪ 待建 |

---

## 3b. 与 shared 基础设施的对接映射表 🆕

> **B19 修复**——v0.5.0 新增。Telemetry 不是孤军：它必须明确声明如何落座在已有 `src/zephyr/shared/` 基础设施上。以下为 "复用 vs 新建" 的零歧义声明。

### 复用清单（Telemetry 基于这些 shared 组件构建，不复写）

| shared 组件 | 绝对路径 | 提供的能力 | Telemetry 使用方式 | AI 施工约束 |
|------------|---------|-----------|-------------------|-----------|
| **TraceContext**（contextvars） | `shared/logging.py` | trace_id / span_id / session_id 跨调用链自动传播 | §5 logs + §6 traces 的上下文来源 | **MUST 使用 shared.logging 的 `TraceContext`**，禁止定义第二个 TraceContext |
| **CTR-TRACE-001** | `shared/contracts/trace_context.py` | trace_id / span_id / parent_span_id / service_name 数据契约 | §6 Span 字段必须兼容此契约 | Span.trace_id/span_id/parent_span_id 格式与 CTR-TRACE-001 一致 |
| **get_logger + JSON Formatter** | `shared/logging.py` | 结构化 JSON 日志（_StructuredFormatter）+ 人类可读控制台（_HumanFormatter） | §5 logs 子系统不做独立日志系统——它是 shared.logging 的消费端和增强端 | 各模块的 log 统一经 shared.logging → Telemetry logs 子系统持久化，不双写 |
| **LifecycleAware + ModuleHealth** | `shared/lifecycle/hooks.py` | 模块生命周期协议 + `health_check() → ModuleHealth` | §10 health 子系统定时轮询所有已注册模块的 `health_check()` | 健康检查数据来源是各模块的 LifecycleAware 协议实现，不是 Telemetry 自行探测 |
| **BackpressureThrottle/Pause/Resume** | `shared/contracts/backpressure/` | CTR-BP-001 PAUSE / CTR-BP-002 THROTTLE / CTR-BP-003 RESUME | §4 ring buffer 80%/95% 填满时发出 backpressure 信号 | 禁止静默丢数据——必须先发 THROTTLE → 再发 PAUSE → 最后丢弃 |
| **FeatureFlag**（三态） | `shared/flags.py` | FlagState.ALWAYS_ON / CONDITIONAL / ALWAYS_OFF | 控制 profiling 开关、采样率、日志级别、成本阈值 | 所有实验性 Telemetry 功能 MUST 由 FeatureFlag 守护（默认 OFF） |
| **EventBus**（pub/sub） | `shared/observer.py` | 线程安全的订阅/发布/取消 | Telemetry 内部事件分发（archive TTL 触发、告警状态变更、schema 变更通知） | 内部事件走 observer.EventBus，不做自定义事件系统 |
| **TelemetryEmitter 契约** | `shared/contracts/telemetry_emitter.py` | CTR-P1-013 遥测发射器接口 | MetricPoint / AIBehaviorEvent / HealthReport 等是实现此契约的具体数据类 | §3 所有新数据类 MUST 实现或兼容 TelemetryEmitter 接口 |

### 新建清单（Telemetry 独有的、shared 不提供的）

| 新建组件 | 所在子系统 | 理由（为什么 shared 没有提供） |
|---------|----------|------|
| MetricPoint（含 Histogram/Summary） | §4 metrics | shared 无指标采集/聚合能力 |
| JSONLFileWriter（按日轮转） | §5 logs | shared.logging 提供格式化但不提供持久化策略 |
| Span 数据模型 + tail-based sampler | §6 traces | shared 有 TraceContext 传播但无 Span 模型和采样 |
| AIBehaviorEvent + 7 维度 tracker | §7 ai_behavior | 业务专属，shared 不应承载 |
| Schema Registry（YAML SSoT + 运行时校验） | §12 schema | shared 无指标 schema 治理 |
| Multi-Window Burn Rate 告警规则 | §11 alerts | shared 无告警领域逻辑 |
| Telemetry watchdog 独立进程 | §10 health | 系统进程类（非 library），不应放在 shared |
| profile collector（py-spy → pprof） | §9 profiles | 外部工具集成，非 shared 职责 |

---

## 3c. 模块集成 DX：统一接入点 🆕

> **B29 修复**——v0.6.0 新增。九个子系统各自定义了 `report()`、`emit()`、`get_logger()` 等不同 API。AI 每给一个新模块加遥测都要查阅九份文档。统一门面类的设计原则：**一行 `Telemetry(module_id)` 获得全部能力，AI 不需要记忆子系统 API。**

### Telemetry 门面类 API

```python
from zephyr.l12_system_telemetry import Telemetry

# 模块初始化——一行接入
telemetry = Telemetry(module_id="MOD-INF-XXX", environment="prod")

# metrics —— 四类指标，统一接口
telemetry.metrics.gauge("cpu_usage", 45.2, labels={"host": "main"})
telemetry.metrics.counter("llm_calls_total", 1, labels={"model": "gpt-4"})
telemetry.metrics.histogram("llm_api_latency_ms", 320.0, labels={"model": "gpt-4"})
telemetry.metrics.summary("user_perceived_latency_ms", 500.0)

# logs —— 复用 shared.logging，增加便捷方法
telemetry.logs.info("task dispatched", task_id="T-001")
telemetry.logs.warning("rate limit approaching", current_rate=95)
telemetry.logs.error("pipeline failed", trace_id=trace_id)

# traces —— 上下文管理器风格，自动注入 trace_id
with telemetry.traces.span("pipeline_execute") as span:
    span.set_metadata(task_id="T-001")
    # ... 业务逻辑 ...
    # 退出时自动记录 span end_time + status

# ai_behavior —— 记录每次模型调用
telemetry.ai_behavior.record(
    model_id="gpt-4",
    input_tokens=1200,
    output_tokens=350,
    duration_ms=2500.0,
    cost_usd=0.015,
    prompt_template_id="task_decomposition_v2",
    prompt_version="1.3"
)

# health —— 模块注册到 LifecycleManager
telemetry.health.register()

# 关闭——flush 所有 buffer，释放资源
await telemetry.shutdown()
```

### Graceful Shutdown 设计 🆕

> **B66 修复**——v0.8.0 新增。`shutdown()` 必须在系统停止前执行：flush 所有 ring buffer 中的 MetricPoint/LogEntry/Span → 写入 SQLite/JSONL → 关闭 DB 连接。不执行 flush = 缓冲区中的遥测数据静默丢失（系统"不可观测的最后一秒"）。

```
shutdown() 流程:
  1. 冻结入站: 停止接受新的 MetricPoint/Log/Span（返回 SHUTTING_DOWN 错误码）
  2. Flush metrics ring buffer → SQLite（超时 30s）
  3. Flush logs ring buffer → JSONL（超时 10s）
  4. Flush traces in-memory spans → JSONL（超时 10s）
  5. 等待所有正在进行的 write 操作完成（超时 5s）
  6. 关闭 SQLite 连接
  7. 关闭所有 JSONL file handles
  8. 从 LifecycleManager 注销
  9. 写入 shutdown audit event

  shutdown 超时策略:
    - 总超时 60s（不阻塞进程退出）
    - 强制退出前最后一次尝试: 将剩余 buffer 写入 emergency_shutdown.jsonl
    - 下次启动时自动加载 emergency_shutdown.jsonl → 正常路径处理
  
  应急丢失检测:
    启动时检测上次是否正常 shutdown（检查 shutdown audit event 是否存在）
    → 缺失 → P2 "上次关闭异常，可能有遥测数据丢失"
    → 自动评估丢失量: ring_buffer_size - successfully_flushed_on_shutdown
```

### Telemetry 内部实现约束

```
Telemetry(module_id) 初始化时:
  1. 自动从环境变量 / config 读取 environment
  2. 自动注册到 LifecycleManager（如果已启动）
  3. 为 metrics 子系统设置默认标签 {module: module_id, environment: env}
  4. 为 traces 子系统注入 shared.logging.TraceContext
  5. 不启动新线程——所有子系统复用 Telemetry 主进程
```

### AI 施工约定（集成）

```
1. 每个新模块的 __init__.py 第一行: self.telemetry = Telemetry("MOD-INF-XXX")
2. 禁止绕过 Telemetry 门面类直接调用子系统内部 API
3. 测试中通过 Telemetry(test_mode=True) 获得 Mock 版本（所有操作 noop）
4. shutdown() 必须在模块 on_shutdown 钩子中调用
```

---

## 3d. 配置热更新机制 🆕

> **B30 修复**——v0.6.0 新增。1人+AI 维护场景下，重启 = 打断 AI 工作。所有 Telemetry 配置（FeatureFlag、采样率、日志级别、告警阈值）必须支持运行时热更新，零重启。

### 热更新订阅流程

```
配置热更新机制:
  shared/flags.py 启动文件监听（watchdog/inotify 监听 config/ 目录）
    → config/flags.yaml 变更 → shared/flags 自动重载 FlagState
    → shared/observer.EventBus 发布 CONFIG_CHANGE 事件
    → Telemetry 各子系统订阅 CONFIG_CHANGE:
      ├── §4 metrics: 更新采样率 / rate limit / cardinality threshold
      ├── §5 logs: 更新 log_level_override
      ├── §6 traces: 更新采样策略参数
      ├── §9 profiles: 开启/关闭采集
      ├── §11 alerts: 更新 cost_alert_threshold_usd / burn rate 窗口参数
      └── §8 archive: 更新 TTL / auto_cleanup
```

### 热更新支持矩阵

| 配置项 | 热更新 | 说明 |
|--------|:---:|------|
| `telemetry.enable_profiling` | ✅ | 即时生效，下次采样周期应用 |
| `telemetry.debug_full_sampling` | ✅ | 即时生效，已采集未 flush 的 span 不受影响 |
| `telemetry.cost_alert_threshold_usd` | ✅ | 即时生效，下次 alert evaluation 周期应用 |
| `telemetry.log_level_override.{module}` | ✅ | 即时生效，shared.logging 的 ContextVar 更新 |
| `telemetry.enable_slo_postmortem` | ✅ | 即时生效 |
| `telemetry.cardinality_strict_mode` | ✅ | 即时生效 |
| `telemetry.archive_auto_cleanup` | ✅ | 即时生效 |
| **新增子系统** | ❌ | 新增 profiles/health/alerts/schema 需要重启 |
| **新增 MetricSchema** | ✅ | schema registry 支持增量加载 |
| **alert_rules.yaml 变更** | ✅ | 告警规则引擎监听文件变更 |

### AI 施工约定（热更新）

```
1. 所有可配置参数 MUST 从 FeatureFlag / config 文件读取，不做硬编码
2. 每个子系统 MUST 实现 on_config_change(event) 回调
3. 不允许"修改配置 → 等待下次重启"的模式——即时生效是硬要求
4. 热更新失败 → 保持当前配置 + 记录错误日志，不回退
```

---
## 3e. 指标命名空间与冲突预防 🆕

> **B78 修复**——v0.9.0 新增。多个模块被 AI 独立生成代码后，可能出现同一指标名被不同模块以不同语义使用。例如 MOD-INF-008 和 MOD-INF-012 都注册了 `llm_calls_total`，但一个统计 API 调用、一个统计 LLM 内部调用——这会导致 FLE 告警误判和 Dashboard 数据混乱。这是 100% AI 施工的特有风险（人类开发会自然通过代码 review 发现）。

### 命名空间策略

```
指标全限定名 (FQMN, Fully Qualified Metric Name):
  {module_id}::{metric_name}
  例: MOD-INF-008::llm_calls_total, MOD-INF-012::llm_calls_total

  注册规则:
    - Schema Registry 以 FQMN 为唯一 key 存储 MetricSchema
    - 两个不同 module_id 可以注册相同 metric_name——自动解歧为不同 FQMN
    - 同一 module_id 内 metric_name MUST 唯一
    - FQMN 在 SQLite 存储、Dashboard 查询、FLE 消费中统一使用

  冲突检测:
    - 新注册 metric_name 时自动检测是否与同 module_id 下已有指标冲突
    - 冲突 → 返回 CONFLICT 错误码 + 建议替代名称
    - 跨 module_id 不产生冲突告警（由 module_id 前缀自动解歧）
```

### MetricPoint 中的 module_id 自动注入

```python
# 模块调用时不需要手动传 module_id
telemetry = Telemetry("MOD-INF-008")
telemetry.metrics.counter("llm_calls_total", 1)
  → 内部自动生成 FQMN: "MOD-INF-008::llm_calls_total"
  → Schema Registry 按 FQMN 校验
  → SQLite 表存储 fqmn 列 + metric_name 列 + module_id 列（三列索引）
```

### Metric Discovery API 命名空间过滤

```
list_metrics(module="MOD-INF-008")
  → 仅返回 FQMN 前缀为 "MOD-INF-008::" 的指标

search_metrics("llm_calls")
  → 返回所有 module_id 下匹配的指标，按 module_id 分组显示
  → AI 看到: {MOD-INF-008::llm_calls_total: "LLM API调用总数", MOD-INF-012::llm_calls_total: "数据库LLM查询统计"}
```

---
## 3f. 批量上报 API 🆕

> **B79 修复**——v0.9.0 新增。蓝图 §3c 只定义了单个上报接口（`counter()`, `gauge()`, `info()`, `start_span()`）。但在 AI 生成的批量处理逻辑（Pipeline 并行执行、批量 TaskCard 处理）中，逐个调用会导致大量函数调用开销和 ring buffer 锁竞争。必须提供批量上报接口。

### 批量 Metrics API

```python
# 批量上报 MetricPoint——一次调用，一次 lock acquire
telemetry.metrics.report_batch([
    MetricPoint(name="llm_calls_total", value=1, type="counter", labels={"model": "gpt-4"}),
    MetricPoint(name="llm_calls_total", value=1, type="counter", labels={"model": "claude-3"}),
    MetricPoint(name="tokens_consumed", value=1500, type="counter", labels={"model": "gpt-4"}),
    MetricPoint(name="pipeline_duration_ms", value=3200, type="histogram", labels={"pipeline": "text-to-sql"}),
])

# 内部实现:
#   1. 一次 acquire ring buffer lock
#   2. 逐条 schema validate（失败 → 单条入 DLQ，不阻塞成功的）
#   3. 批量写入 ring buffer
#   4. 释放 lock
#   5. 返回 report_batch_result: {success_count, failed_count, dlq_ids[]}
```

### 批量 Log API

```python
# 批量日志——关联同一 trace 的多条 log
telemetry.logs.log_batch([
    LogEntry(level="info", message="Pipeline started", trace_id=tid),
    LogEntry(level="debug", message="TaskCard resolved", trace_id=tid, labels={"task_id": "T-001"}),
    LogEntry(level="info", message="Pipeline completed", trace_id=tid, labels={"duration_ms": 3200}),
])
# → 一次 JSONL 文件追加（单行一条，一次 write 调用写多行）
```

### 批量 Span API

```python
# 批量 Span 创建——Pipeline 并行调度时
with telemetry.traces.start_batch_spans([
    SpanContext(name="subtask.resolve", parent_span_id=root_span),
    SpanContext(name="subtask.execute", parent_span_id=root_span),
    SpanContext(name="subtask.validate", parent_span_id=root_span),
]) as spans:
    # 并行执行三个子任务
    ...
    # 所有 span 在 exit 时自动 end + flush
```

### 批量 API 施工约定

```
1. 超过 10 个同类型遥测调用时 MUST 使用 report_batch / log_batch
2. 批量上报失败（DLQ full / ring buffer full）时逐条降级为独立调用（有 backpressure throttling）
3. 批量上报不改变语义——与逐个调用产生相同的数据点（仅性能不同）
```

---

## 4. metrics 子系统

```
metrics 采集流程:
  各模块调用 metrics.report(MetricPoint)（须通过 schema 校验）
    → MetricPoint 进入环形缓冲区(容量 10000)
    → 每 60s 批量 flush 到 SQLite metrics 表
    → FLE 定时查询 metrics 表做异常检测
    → 高基数标签（>1000 唯一值）触发 cardinality_warning
    → Histogram 类型指标自动计算 P50/P90/P95/P99
```

### MetricPoint Schema

```python
@dataclass
class MetricPoint:
    name: str          # 指标名称（如 "llm_api_latency_ms"，须在 schema registry 注册）
    value: float       # 数值
    timestamp: float   # Unix 时间戳
    labels: dict       # 维度标签（module / version / model），高基数标签自动限流
    type: str          # gauge / counter / histogram / summary
    exemplar: dict | None  # 🆕 关联 trace/span（trace_id + span_id），支持 metric→trace 下钻
```

### 指标类型与用途

| 类型 | 用途 | 示例 | 聚合方式 |
|------|------|------|---------|
| **gauge** | 瞬时值 | CPU使用率 / 内存占用 / 活跃连接数 | 最后值 |
| **counter** | 单调递增 | LLM调用总数 / Token消耗总量 / Gate拒绝数 | 增量(rate) |
| **histogram** | 分布 | LLM API 延迟 / 脚本执行耗时 / Task完成时间 | P50/P90/P95/P99 |
| **summary** | 客户端分位数 | 用户感知延迟（不可服务端聚合的场景） | 客户端计算 |

### Cardinality 控制

> 高基数（High Cardinality）是可观测性的头号杀手——O(10^N) 的指标维度组合会导致存储爆炸。

| 控制策略 | 机制 | 阈值 |
|---------|------|:---:|
| **标签白名单** | schema registry 预定义合法标签，动态标签拒绝写入 | — |
| **基数上限** | 单指标标签组合 > 1000 时自动聚合（truncate label value） | > 1000 |
| **基数告警** | 接近上限时发出 cardinality_warning 事件 → FLE | > 800 |
| **TTL 裁剪** | 超过 7 天无活跃上报的标签组合自动清理 | 7 days |
| **strict_mode** | FeatureFlag `telemetry.cardinality_strict_mode=ON` 时超限直接拒绝而非聚合 | – |
| **zombie_scan 🆕** | 每 7 天扫描僵尸指标/标签（见下文），自动隐藏和清理 | 30 days → 物理删除 |

### 时钟偏差检测 🆕

> **B60 修复**——v0.8.0 新增。跨进程 Span 依赖时间戳排序。若 process-A 的时钟比 process-B 快 3 秒，子 Span 可能显示为早于父 Span——trace 可视化断裂 + FLE 误判。

```
时钟偏差防护:
  1. Span 时间戳: wall clock（time.time()）用于排序和展示
  2. Span 时长:   monotonic clock（time.monotonic()）用于精确测量
     → 不受系统时钟调整（NTP同步、手动修改）影响
  3. Clock skew detection:
     每 5min 写入 local_clock_skew_us metric（与 system clock source 对比）
     → skew > 100ms → P2 "系统时钟偏差"
     → skew > 1s   → P1 "严重时钟偏差，trace 时序可能错乱"
  4. TraceParent 携带父进程 trace_start_ts，子进程以此对齐
```

### 僵尸指标与标签清理 🆕

> **B68 修复**——v0.8.0 新增。长期运行后产生僵尸时间序列：旧代码 label 不再上报、废弃模块残留、一次性 label（task_id）无限基数增长。

```
Zombie Metric 检测与清理（每 7 天）:
  扫描所有指标:
    → 过去 7 天零写入的指标/标签组合 → 标记 ZOMBIE
    → ZOMBIE 指标在 Metric Discovery API（§14b）中隐藏（不污染 AI 搜索）
    → ZOMBIE 指标在 Dashboard 中灰显（仍可查询历史数据）
    → ZOMBIE 持续 30 天 → 物理删除历史数据 + 从 schema registry 注销
    → ZOMBIE 指标再次被写入 → 自动复活（解除 ZOMBIE 标记）

  Zombie 监控:
    zombie_metric_count > 50 → P2 "大量僵尸指标积压，建议清理"
    zombie_label_cardinality > 10000 → P1（基数爆炸风险）
```

### 入站速率限制 & Backpressure 对接 🆕

> **B23 修复**——v0.5.0 新增。防止单个失控模块淹没整个 Telemetry 系统。对接已有 `shared/contracts/backpressure/` 契约。

| 控制层 | 机制 | 阈值 | 动作 |
|--------|------|:---:|------|
| **per-module 速率限制** | 每模块每秒最大 MetricPoint 上报数 | 100 / sec | 超过 → 50% 概率丢弃 + 记录 `rate_limit_hit` 指标 |
| **ring buffer 水位线 1** | buffer 占用率 | > 80% | → 发出 `BackpressureThrottle`（CTR-BP-002），建议上游降至 50% 速率 |
| **ring buffer 水位线 2** | buffer 占用率 | > 95% | → 发出 `BackpressurePause`（CTR-BP-001），通知上游暂停 MetricPoint 上报 |
| **ring buffer 满载** | buffer 占用率 | = 100% | → 丢弃最旧数据 + 发出 `BackpressurePause` + 记录 `buffer_overflow` 事件 |
| **背压恢复** | buffer 占用率 | < 60% | → 发出 `BackpressureResume`（CTR-BP-003），通知上游恢复正常速率 |

### Exemplar 关联

```
MetricPoint → Exemplar(trace_id, span_id) → Trace → Log(trace_id)
  三击链路：Dashboard 指标异常尖峰 → 点击查看 exemplar trace → 下钻到具体 span → 关联日志
```

> **B34 注**：Exemplar 引用的 trace_id 可能指向已过 TTL 删除的 Span。方案：(1) 关键告警触发时，exemplar 的 Span 自动标记为 "pinned" 不删除；(2) 7 天后 exemplar 仅保留 trace_id 作为标记，失去下钻能力；(3) Schema Registry 跟踪各指标类型的数据源 retention，Dashboard 自动标注下钻可用窗口。

### Counter 重置检测 🆕

> **B31 修复**——v0.7.0 新增。Counter 在进程重启后归零。如果下游（FLE/告警规则）直接对 counter 做 rate 计算，重启瞬间会出现巨大负值（counter 从高值突降到 0）。这是 Prometheus/OTel 的经典问题。

| 机制 | 说明 |
|------|------|
| **process_start_time 标签** | 每个 MetricPoint 携带 `process_start_ts` 标签——重启后此值变化即被检测到 |
| **FLE counter reset aware** | FLE 计算 counter rate 时检测 `process_start_ts` 变化 → 自动重置基线，不产生 spike 告警 |
| **stale counter detection** | 超过 10min 无 counter 上报 → 标记为 STALE → FLE 收到新 counter 时自动从 0 开始累计 |
| **delta recording** | 内部存储上次上报值，每次 `counter()` 调用自动计算 delta 并写入，进程重启后从 0 重建 delta 序列 |

### 幂等性保障 🆕

> **B52 修复**——v0.7.0 新增。模块调用 `telemetry.metrics.counter("llm_calls", 1)` 后如果写入失败并重试，可能导致 double-counting。

| 机制 | 说明 |
|------|------|
| **idempotency_key** | 每个 MetricPoint 自动生成 `{module_id}_{metric_name}_{timestamp_ns}_{nonce}` 作为幂等键 |
| **dedup at flush** | 批量 flush 入 SQLite 时按 idempotency_key 去重（同 key 72h 内的只保留第一条） |
| **exactly-once for counters** | Counter 类型指标 MUST 携带 idempotency_key；gauge/histogram 为 best-effort |
| **TTL of idempotency** | idempotency_key 在去重表中保留 72h 后物理删除（防止无限膨胀） |

### Dead Letter Queue 操作设计 🆕

> **B48 修复**——v0.7.0 新增。蓝图摘要宣称 "DLQ 保障数据质量闭环" 与 "DLQ 自动修复"，但完整的 DLQ 操作设计此前从未落地。DLQ 是全系统遥测数据质量的最后兜底——所有被拒绝/无法处理的事件（schema 校验失败、写入失败、类型错误）进入 DLQ，而非静默丢弃。

#### DLQ 事件生命周期

```
遥测事件提交
  ├── 正常路径: schema 校验通过 → ring buffer → flush → SQLite/JSONL ✅
  ├── 软拒绝: schema 校验失败 / 类型错误 → DLQ 写入 + rejection log ✅
  ├── 硬拒绝: JSON 解析失败 / 恶意 payload → DLQ 写入 + P2 安全事件 ⚠️
  └── 系统级失败: DLQ 写入失败 → stderr fallback → 内存缓冲 → 丢弃+告警 ❌
```

#### DLQ 存储设计

| 属性 | 规格 |
|------|------|
| **存储格式** | JSONL（与正常日志格式一致，便于统一查询） |
| **存储路径** | `data/telemetry/{environment}/dlq/{date}.jsonl` |
| **TTL** | 30 天（与 logs 同级，过期后归档或删除） |
| **结构** | `{original_event, rejection_reason, rejected_by, timestamp, dlq_id}` |
| **单文件上限** | 100MB 后自动轮转 |

#### DLQ 自动修复策略

```
DLQ 自动修复流程:
  每 60min（或 DLQ 文件 > 10MB 时触发的 event-driven）:
    → 扫描 DLQ 中所有事件
    → 按 rejection_reason 分类:
      ├── SCHEMA_ERROR: schema 漂移 → Schema Registry 查询最新 schema → 尝试 re-map
      │   → 成功 → 重新走正常路径写入 → 从 DLQ 标记为 "repaired"
      │   → 失败 → 保留在 DLQ + 递增 retry_count
      ├── TYPE_ERROR: 字段类型不匹配 → 尝试类型强制转换
      │   → 成功 → repaired
      │   → 失败 → 保留 + 人工审查标记
      └── WRITE_FAILED: IO/DB 临时不可用 → 简单重试（最多 3 次）
    → 生成 DLQ repair report → 写入 Audit Trail
    → 重试超过 3 次的事件 → 标记为 DEAD → 保留 7 天后物理删除
```

#### DLQ 监控

| 指标 | 告警阈值 |
|------|:---:|
| `dlq_size_bytes` | > 100MB → P2 |
| `dlq_growth_rate` | > 10MB/h → P1（上游失控） |
| `dlq_repair_success_rate` | < 50% → P2（自动修复失效） |
| `dlq_dead_event_count` | > 1000 → P1（需人工介入） |
| `dlq_age_oldest_event` | > 24h → P2（积压） |

#### AI 消费 DLQ

```
AI 通过 MCP 接口消费 DLQ:
  get_dlq_summary() → {total_events, by_reason, repair_rate, oldest_event_age}
  get_dlq_samples(reason: str, limit: int) → list[DLQEvent]
  → AI 发现 schema 漂移趋势后主动修正蓝图或代码
```

### 关键 SLI

| SLI | 公式 | SLO |
|-----|------|:---:|
| LLM 可用性 | Successful_Calls / Total_Calls | ≥ 99.5% |
| Gate 通过率 | Passed_Tasks / Total_Tasks_at_Gate | ≥ 95% |
| Pipeline 完成率 | Completed_Tasks / Dispatched_Tasks | ≥ 90% |
| Token 效率 | Useful_Output_Tokens / Total_Input_Tokens | ≥ 0.3 |
| BLUEPRINT-READ-FREQ | COUNT(blueprint_reads WHERE blueprint_id=X) | ≥ 1 / session（目标）|
| BLUEPRINT-STALENESS | now() - MAX(blueprint.last_updated) | ≤ 30 days |
| TELEMETRY-HEALTH | Telemetry上报成功率 | ≥ 99.9%（自体监控） |
| METRIC-CARDINALITY | 超过基线上限的指标数 | = 0 |

---

## 5. logs 子系统

> **基础设施声明**：logs 子系统基于 `shared/logging.py` 构建。`shared.logging` 提供 TraceContext 传播 + get_logger + JSON Formatter——logs 子系统在其之上增加持久化策略（JSONLFileWriter）、级别过滤、PII 脱敏。**不做第二个日志系统。**

```
logs 采集流程:
  各模块调用 shared.logging.get_logger() 获得结构化日志器
    → shared.logging._StructuredFormatter 生成 JSON Line
    → logs 子系统的 JSONLFileWriter 拦截并持久化到 data/telemetry/{environment}/logs/{date}.jsonl
    → 自动注入 trace_id / span_id（从 shared.logging.TraceContext 提取，无需额外操作）
    → Gate Engine 定期扫描 ERROR/FATAL 日志触发升级
    → fail-closed：写入失败 → stderr 降级 → 告警
```

### 日志分级

| Level | 用途 | 示例 |
|-------|------|------|
| DEBUG | 开发调试信息 | Context Engine token count |
| INFO | 正常业务流程 | "Task T-001 dispatched to Pipeline A" |
| WARNING | 阈值预警 | "VMS tokens bucket usage > 80%" |
| ERROR | 可恢复错误 | "LLM API timeout, retry 3/5" |
| FATAL | 不可恢复，需人工介入 | "SQLite corruption detected" |

### 日志与 Trace 关联

```
每个 JSONL log line 必须包含:
{
  "event": "task_dispatched",
  "level": "INFO",
  "module": "pipeline",
  "trace_id": "abc123...",    ← 🆕 从 TraceContext 提取
  "span_id": "def456...",     ← 🆕 从当前 span 提取
  "timestamp": "2026-05-05T12:00:00Z",
  "message": "Task T-001 dispatched to Pipeline A"
}
```

### 日志安全性

| 控制 | 机制 |
|------|------|
| **PII 脱敏** | 自动检测并脱敏 API Key / Token / 密码类字段 |
| **日志级别阈值** | 生产环境过滤 DEBUG 级别，按模块可配 |
| **数据分级** | 日志标记 sensitivity_level（public/internal/confidential/secret） |
| **写入失败降级链** | JSONL write fail → stderr fallback → 内存环形区缓冲(1000条) → 丢弃+告警 |

---

## 6. traces 子系统

> **基础设施声明**：Span 数据模型兼容 `shared/contracts/trace_context.py`（CTR-TRACE-001）。trace_id / span_id / parent_span_id 格式与 CTR-TRACE-001 一致（UUID hex，32/16 char）。TraceContext 传播使用 `shared/logging.py` 的 contextvars 机制。

### W3C TraceContext 传播

> 对标 W3C TraceContext 标准（traceparent / tracestate header）。所有跨模块调用自动注入 context，确保 trace 链路不断裂。

```
Context 传播机制:
  上游模块创建 Span
    → 写入 traceparent header: "00-{trace_id}-{span_id}-01"
    → 下游模块从 header 提取 → 创建子 Span（parent_span_id = 上游 span_id）
    → 日志/指标自动注入 trace_id/span_id
```

```
TaskCard 全链路追踪:
  Root Span (TaskCard创建) [traceparent written]
    ├── M1 Span (Context Engine build)
    │   └── inject Span (CE merge)
    ├── Gate Span (G0-G7 逐门禁)
    ├── Orc Span (Pipeline dispatch)
    │   ├── M6 Span (A区起草)
    │   └── M8 Span (B区审计)
    ├── Script Span (D1-D12 质量检查)
    └── Complete Span (写入知识库 / 交付记录)
```

**Trace 数据结构**：

```python
@dataclass
class Span:
    trace_id: str      # 整条链路 ID（32 hex, W3C 格式）
    span_id: str       # 当前 Span ID（16 hex）
    parent_span_id: str  # 父 Span ID（空 = root）
    module: str        # 当前模块
    start_time: float
    end_time: float
    status: str        # ok / error / timeout
    metadata: dict     # 模块自定义元数据
    trace_state: str   # 🆕 W3C tracestate（厂商扩展字段）
```

### 智能采样策略

> traces 数据量大，全量存储不可持续。采用 tail-based sampling——先采集再决定是否保留。

| 采样策略 | 规则 | 保留率 |
|---------|------|:---:|
| **错误全保留** | status == "error" 的 span → 100% 保留 | 100% |
| **高延迟全保留** | duration > P95 阈值的 span → 100% 保留 | 100% |
| **根 Span 全保留** | parent_span_id 为空的 Root Span → 100% 保留 | 100% |
| **正常流量采样** | 其余 span → 按 10% 概率随机采样 | 10% |
| **自适应采样** | 系统负载高时自动降低采样率（最低 1%） | 1%-10% |

### Span→Metrics 连接器

```
OpenTelemetry Collector 模式:
  traces pipeline → spanmetrics connector → 自动生成 RED 指标
    Rate:  count(spans) / time_window
    Errors: count(spans WHERE status=error) / total
    Duration: histogram of span.duration

  无需单独写 counter——有 trace 就有指标。
```

### 跨进程 TraceContext 传播 🆕

> **B36 修复**——v0.7.0 新增。ZephyrAlpha 架构包含 MCP Server（独立进程）、子进程（subprocess tracker）、Pipeline 多进程编排。当前的 contextvars 传播机制仅限单进程内——跨进程边界时 trace 链路断裂。必须显式设计跨进程传播协议。

#### 传播载体

| 跨进程场景 | 传播方式 | 实现 |
|-----------|---------|------|
| **MCP Server → Tool 调用** | `traceparent` header 写入 MCP Request metadata | MCP client 自动注入 `traceparent` 到 `_meta` 字段 |
| **主进程 → 子进程** | 环境变量 `TRACEPARENT` + 命令行参数 | 主进程 fork 前写入环境，子进程启动时提取 |
| **HTTP/gRPC 调用** | `traceparent` + `tracestate` W3C 标准 header | `shared/tracing.py` 已有 OTLP gRPC exporter 基础 |
| **消息队列（未来）** | AMQP 消息 header `traceparent` | Producer 注入 header，Consumer 提取并恢复 context |
| **文件系统事件** | `traceparent` 写入事件 payload 顶层字段 | 下游模块读取文件时提取 traceparent |

#### W3C TraceContext 完整格式

```
traceparent: 00-{trace_id(32hex)}-{span_id(16hex)}-{trace_flags(2hex)}
              00 = version
              01 = sampled flag (01 = sampled, 00 = not sampled)

tracestate: zephyr={module_id};{environment};{session_id}
            厂商扩展字段，携带 Telemetry 内部上下文
```

#### 采样决策传播

> **B45 补**：分布式场景下，tail-based sampling 的决策必须向前传播——如果 root span 决定不采样，下游 span 也不应采集完整数据。

```
采样决策传播:
  Root span trace_flags:
    01 (sampled) → 下游完整采集 span 数据
    00 (not sampled) → 下游仅记录 trace_id + minimal span（duration + status），不记录 metadata/attributes
```

#### contextvars → W3C 桥接

```
shared/logging.py TraceContext (contextvars) 与 shared/tracing.py (OTel) 的桥接:
  进入跨进程边界时:
    TraceContext.trace_id → traceparent.trace_id
    TraceContext.span_id   → traceparent.span_id
    → 序列化写入传播载体

  退出跨进程边界（下游恢复）时:
    从传播载体提取 traceparent → 解析 trace_id/span_id
    → TraceContext(trace_id=trace_id) 恢复 contextvars
    → 创建子 Span（parent_span_id = 上游 span_id）
```

#### AI 施工约定（跨进程）

```
1. 任何跨进程/跨模块调用 MUST 携带 traceparent（W3C 标准）
2. 下游模块启动后第一件事：检测环境中是否有 TRACEPARENT，有则恢复 TraceContext
3. 禁止在跨进程边界手动传递 trace_id 字符串——统一经过 TraceContext→W3C 桥接
4. MCP Server 在发送 tool result 前 MUST 注入 traceparent 到 response metadata
```

---
## 7. ai_behavior 子系统

> 监控 AI 模型的行为健康度——不是代码的 bug，是模型的"偏航"。
> 对 100% AI 施工场景，ai_behavior 是最关键的子系统——它替代了代码审查中的人眼。
> **FeatureFlag 控制**：整体开关 `telemetry.enable_ai_behavior_tracking`（默认 ON），成本阈值 `telemetry.cost_alert_threshold_usd`（默认 5.0 USD）。参见 §2e。各维度可独立开关以控制采集开销。
> **语义对齐**：所有字段命名 MUST 可映射到 OTel GenAI + Agent Semantic Conventions（§2f）。
> **B35 注（数据量估算）**：100% AI 施工下，每个 TaskCard 产生 10-50 次 AI 行为事件。按日均 100 个 TaskCard 估算 = 1000-5000 个 AIBehaviorEvent/天。每个事件 ~2-5KB（含 tool_calls + decision_path），日增量 5-25MB。需在 §8b（遥测成本预算）中纳入。

### 七大监测维度 + 错误分类学

#### 7.1 模型调用画像

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| **模型选择偏差** | 各模型调用占比 | 单模型占比 > 80% → 路由异常 |
| **调用频率** | 每模块 LLM call / min | 突增 > 5x 基线 → 失控调用 |
| **模型版本漂移** | model_version 分布 | 新版本占比突变 → 模型升级影响监控 |

#### 7.2 Token 与成本（FinOps）

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| **Token 消耗异常** | 每任务 token 消耗 | 超出基线 3σ → 模型"废话模式" |
| **成本追踪** | 按 model × task_type × module 的 $ 成本 | 日成本 > 预算 80% → Budget Enforcer |
| **Token 效率** | Useful_Output_Tokens / Total_Input_Tokens | < 0.2 → 提示词浪费 |
| **速率限制命中** | rate_limit_hit_count + retry_attempts + backoff_duration | 命中率 > 10% → 需要扩容/降级 |

#### 7.3 Gate 交互行为

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| **Gate 命中率** | 各 Gate 拒绝比例 | G0 reject > 20% → 输入质量下降 |
| **Gate 通过耗时** | 各 Gate 判定延迟 | P95 > 1s → Gate 规则过重 |
| **Gate 绕过检测** | skip_count / bypass_event | 任意非授权绕过 → P0 安全事件 |

#### 7.4 输出质量与一致性

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| **输出一致性** | 同 prompt 重复输出 embedding 余弦相似度 | 差异 > 50% → 幻觉风险 |
| **幻觉率量化** | factual_consistency_score（与 KB/ground truth 比对） | score < 0.7 → 输出不可信 |
| **代码质量回归** | AI 生成代码的 lint 错误数 / 测试通过率 | 环比恶化 > 30% → 模型退化 |
| **输出长度异常** | 单次输出 token 数 | 超出基线 5σ → 废话/循环输出 |

#### 7.5 Prompt 版本追踪

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| **Prompt 模板版本** | prompt_template_id + prompt_version | 版本切换 → 关联输出质量变化 |
| **Prompt 注入检测** | 异常 prompt 模式匹配 | 匹配到已知攻击模式 → LLM Security 拦截 |
| **System Prompt 完整性** | system_prompt_hash | hash 变化 → 提示词被意外修改 |

#### 7.6 工具调用链追踪

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| **工具调用频率** | tool_name + count / task | 某工具调用异常高频 → Agent 陷入循环 |
| **工具调用耗时** | tool_duration P95 | > 5s → 工具性能问题 |
| **工具调用失败率** | tool_error_rate | > 5% → 工具不可用 |
| **参数质量** | tool_args_hash 分布 | 参数组合单一 → Agent 探索不足 |

#### 7.7 Agent 决策路径

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| **决策分支记录** | decision_point + options_evaluated + chosen_option + rationale | 缺失 → Agent 不可审计 |
| **决策回溯频率** | 同一 decision_point 内的回退次数 | > 3 → Agent 决策摇摆 |
| **人工介入频率** | human_escalation_count / task | 突增 → AI 能力退化 |

#### 7.8 错误分类学（Error Taxonomy）🆕

> **B37 修复**——v0.7.0 新增。Google SRE 强调：不是所有错误都同等重要。没有错误分类，告警就是噪声，AI 自我修正无法定位根因。必须建立一套覆盖全系统的错误分类学。

##### 错误维度

| 维度 | 分类值 | 含义 | 示例 |
|------|--------|------|------|
| **Persistence** | `transient` | 暂时性错误，重试大概率恢复 | 网络抖动、rate limit |
| | `permanent` | 永久性错误，重试无效 | API key 失效、权限不足 |
| | `intermittent` | 间歇性错误，时好时坏 | 资源竞争、GC pause |
| **Source** | `client` | 调用方错误 | 参数错误、超时时长太短 |
| | `server` | 被调用方错误 | LLM API 500、DB 连接拒绝 |
| | `dependency` | 第三方依赖错误 | 上游服务不可用 |
| | `internal` | 自身代码/逻辑错误 | 空指针、索引越界 |
| **Expectation** | `expected` | 预期内的错误 | rate limit（配额正常消耗） |
| | `unexpected` | 非预期的错误 | OOM、disk full |
| | `unknown` | 无法归类的新错误 | 新出现的错误模式 |
| **Severity** | `degraded` | 功能降级但可用 | 慢查询、部分数据缺失 |
| | `blocking` | 阻塞业务流程 | Pipeline 中断、Gate 拒绝 |
| | `fatal` | 进程级致命错误 | OOM kill、segfault |

##### Error 事件 Schema（扩展已有 AIBehaviorEvent）

```python
@dataclass
class ErrorContext:
    """注入到每个 Span/Log/Alert 中的错误上下文"""
    error_type: str         # 错误类型（如 "rate_limit", "timeout", "oom"）
    persistence: str        # transient / permanent / intermittent
    source: str             # client / server / dependency / internal
    expectation: str        # expected / unexpected / unknown
    severity: str           # degraded / blocking / fatal
    retry_count: int        # 已重试次数
    max_retries: int        # 最大重试次数
    retry_strategy: str     # linear / exponential / jitter / none
```

##### 错误分类对 AI 自我修正的影响

```
AI 消费遥测时的错误分类决策树:
  error.source == "internal" + severity == "blocking"
    → AI 自我修正：分析 trace → 定位代码位置 → 生成修复 PR
  error.source == "dependency" + persistence == "transient"
    → 不触发自我修正，仅记录并等待恢复
  error.expectation == "expected"
    → 不告警，仅趋势监控（如 rate_limit_hit 增长超基线）
  error.severity == "fatal"
    → P0 立即通知人工（不依赖 AI 自我修正）
```

##### 对告警噪声的控制

```
告警规则 MUST 携带 error 过滤条件:
  - P0 告警: persistence=permanent + severity IN (blocking, fatal)
  - P1 告警: source IN (server, dependency) + expectation=unexpected
  - P2 告警: persistence=intermittent + count > threshold over 1h
  - 不告警: expectation=expected + no trend anomaly
```

#### 7.9 AI 自我修正效能追踪 🆕

> **B73 修复**——v0.8.0 新增。蓝图声称 "AI 通过 MCP 消费遥测进行自我修正" 是一个闭环，但如果从未测量这个闭环是否真的在运作，这就是架构级盲点。必须追踪 AI 自我修正的数量、成功率、平均修复时间，使 1 人维护者能回答"AI 真的在帮我修 bug 吗？"。

##### 效能维度

| 维度 | 指标 | 告警阈值 | 消费方 |
|------|------|:---:|------|
| **修正触发率** | AI 发现异常后实际触发自我修正的比例 | < 50% → AI 发现了问题但未行动 | AI self-review |
| **修正成功率** | 修正后同一问题 24h 内不再复发 | < 80% → 修复质量差 | FLE 回归检测 |
| **修正平均耗时** | anomaly_detected → fix_deployed | > 1h → AI 响应太慢 | PIDashboard |
| **修正引入新问题** | 修正后 1h 内 error_rate 环比上升 | > 0 → 修复引入回归 | FLE revert |
| **人为介入率** | AI 放弃自我修正 → Escalation 给人工 | > 20% → AI 能力边界 | Escalation Protocol |
| **修正覆盖率** | AI 已修正的 anomaly 数 / 可自动修正的 anomaly 数 | < 70% → 自我修正覆盖不足 | AI review |

##### AI自我修正事件Schema

```python
@dataclass
class AISelfCorrectionEvent:
    anomaly_id: str           # 触发的 anomaly ID
    anomaly_type: str         # SLO_BREACH / ERROR_SPIKE / PERF_REGRESSION / HALLUCINATION
    detected_at: float        # 异常发现时间
    analysis_duration_s: float  # AI 分析耗时
    action_taken: str         # ROLLBACK / FIX_PR / CONFIG_CHANGE / KILL_SWITCH / ESCALATE
    fix_deployed_at: float | None  # 修复部署时间
    verified_at: float | None      # 验证通过时间
    success: bool | None      # None = 尚未验证
    regression_detected: bool       # 修复是否引入回归
```

##### AI效能仪表板

```
AI Self-Correction Dashboard:
  - 本周自我修正事件流（anomaly → detect → analyze → fix → verify）
  - 成功率趋势（30 天 rolling）
  - 按 anomaly_type 的修复耗时分布
  - "AI 帮你修了多少" vs "你人工修了多少" 对比
  - 最常被 Escalate 的 anomaly 类型（= AI 需要更多训练/蓝图优化的信号）
```

##### AI 施工约定（自我修正）

```
1. 每次 AI 自我修正 MUST 记录 AISelfCorrectionEvent
2. 修正后 1h 内 MUST 检查是否有回归（通过 §12b Post-Deployment Validation）
3. 连续 3 次修正同一 anomaly → 标记为 HARD_PROBLEM → Escalate 人工
4. 效能仪表板作为每次 AI session 冷启动检查项（§14）

### AI 行为事件 Schema

```python
@dataclass
class AIBehaviorEvent:
    event_type: str          # model_call / token_usage / gate_hit / hallucination / tool_call / decision
    trace_id: str            # 关联 trace
    module: str              # 触发模块
    model_id: str            # 模型标识
    model_version: str       # 模型版本
    prompt_template_id: str  # prompt 模板 ID
    prompt_version: str      # prompt 版本
    input_tokens: int
    output_tokens: int
    cost_usd: float          # 🆕 $ 成本
    duration_ms: float
    status: str              # success / error / rate_limited
    labels: dict             # 扩展维度
    tool_calls: list         # 🆕 [{tool_name, args_hash, duration_ms, result_status}]
    decision_path: dict | None  # 🆕 {options: [...], chosen: str, rationale: str}
    hallucination_score: float | None  # 🆕 0.0-1.0, None = 未评估
```

---

## 8. archive 子系统

```
归档策略:
  metrics 表 → 30天后压缩归档到 archive/metrics/
  logs/ → 30天后 gzip → archive/logs/
  traces/ → 7天后压缩归档（trace 数据量大）
  profiles/ → 14天后压缩归档
  archive/ 下文件保留 90 天后物理删除
  FeatureFlag: telemetry.archive_auto_cleanup=OFF 时暂停自动删除（保留数据用于审计）
```

### 灾备恢复策略 🆕

> **B24 修复**——v0.5.0 新增。SQLite DB 损坏后如何恢复？archive JSONL 作为冷备份，可 replay 重建近期数据。

| 场景 | 恢复方式 | 恢复时间目标（RTO） | 数据丢失上限（RPO） |
|------|---------|:---:|:---:|
| **SQLite metrics 表损坏** | 从最近 7 天 archive JSONL replay 重建 metrics 数据 | 1h（手动触发） | 上次 flush 之后的数据（≤ 60s） |
| **JSONL 日志文件损坏** | 从 archive gzip 解压恢复 | 10min | archive 之后的新日志丢失 |
| **telemetry 数据目录误删** | 从 archive + git 恢复 schema + 重建路径结构 | 2h | 上次 archive 之后的数据 |
| **全盘故障** | 从外部备份（GitHub 上的 config/ + 异地副本）恢复 | 4h | 取决于备份频率 |

**灾备基线**：
- 每日 `sqlite3 .backup` 到 `data/backups/telemetry_{date}.db`（保留 7 天）
- archive 目录本身作为冷备份，不额外备份
- config/ 下的 schema + alert_rules 已在 git 中

### 遥测成本预算 🆕

> **B55 修复**——v0.7.0 新增。Telemetry 自身产生存储和 CPU 成本。对于 1 人维护的有限预算，需要设定遥测成本上限，并实现成本感知的降级策略。

#### 成本模型

| 成本维度 | 计算方式 | 默认月预算 |
|---------|---------|:---:|
| **磁盘占用** | `data/telemetry/` 三环境总大小 | 10 GB |
| **CPU 开销** | profiling + flush + schema 校验 + 采样决策 | 不超过单核 10% |
| **内存占用** | ring buffer + idempotency table + DLQ buffer | 512 MB |
| **LLM 遥测成本** | 合成监控的 LLM health check 调用 | $0.50/月 |

#### 成本感知降级策略

```
遥测成本控制流程:
  磁盘占用 > 80% 预算（8GB）:
    → 1. dev 环境 TTL 减半（14→7天）
    → 2. traces 采样率 10%→5%
    → 3. P2 告警通知
  磁盘占用 > 95% 预算（9.5GB）:
    → 1. dev 环境遥测暂停采集
    → 2. staging traces 采样率 5%→1%
    → 3. profiles 关闭（自动 toggle FeatureFlag）
    → 4. P1 告警 → Feishu
  磁盘占用 = 100%:
    → 1. 仅保留 prod metrics + P0 级别 logs
    → 2. 所有非 prod 数据暂停
    → 3. P0 告警 → Feishu + 需人工清理磁盘
```

#### 成本仪表板

```
遥测成本 Dashboard:
  - 磁盘用量趋势图（按环境 + 按子系统）
  - CPU 开销趋势
  - 预测：基于增长率的 30 天磁盘耗尽预测
  - 成本 vs 预算 热力图
```

---

## 9. profiles 子系统 🆕

> 对标 OTel Profiles signal（experimental→stable）。连续性能剖析——不只回答"哪里慢"，更回答"为什么慢"。对 AI 生成代码的性能审计不可替代。

```
profiles 采集流程:
  Python profiler（py-spy / Austin）每 60s 采集 10s 的 CPU/内存样本
    → 生成 pprof 格式火焰图数据
    → 通过 OTLP /v1development/profiles 推送到 collector
    → 本地存储：profiles/{date}/{module}_{timestamp}.pprof.gz
    → TTL: 14 天
```

### 监测维度

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| **CPU 热点** | 按函数聚合的 CPU 时间分布 | 新热点函数出现 → 性能回归检测 |
| **内存分配** | 按调用栈的内存分配量 | 单函数分配 > 100MB → 内存泄漏嫌疑 |
| **阻塞分析** | IO wait / lock contention 耗时占比 | IO wait > 50% → IO 瓶颈 |
| **GIL 竞争** | GIL hold time 分布 | 单线程持锁 > 100ms → 并发瓶颈 |

### 性能回归检测

```
FLE 消费流程:
  profiles 每日基线（各模块 CPU top10 函数耗时）
    → 新部署后采集 profiles
    → 与基线对比（function duration delta > 30%）
    → 触发 PERF-REGRESSION 事件 → FLE 自动派单
```

---

## 10. health 子系统 🆕

> 自体监控——Telemetry 自身不能成为盲点。对标 Google SRE "monitor the monitoring"。
> **基础设施声明**：health 子系统**不自行探测**模块健康状态。它通过 `shared/lifecycle/hooks.py` 的 `LifecycleManager` 定时轮询所有已注册模块的 `health_check() → ModuleHealth` 输出，聚合为全系统健康视图。各模块通过实现 `LifecycleAware` 协议提供健康数据。


```
health 采集流程:
  独立 watchdog 进程（非 Telemetry 进程内）
    → 每 10s ping Telemetry health endpoint
    → 检查：metrics buffer 占用率 / log writer 延迟 / trace collector 吞吐
    → 每 30s 通过 LifecycleManager 轮询所有模块 HealthCheck
    → 健康评分 = weighted_avg(自身指标 + 各模块 ModuleHealth)
    → 评分 < 0.7 → watchdog 触发:
      1. 尝试重启 Telemetry 进程
      2. 失败 → notify FLE → Escalation Protocol → Feishu 告警
```

### 健康检查维度

| 检查项 | 指标 | 健康阈值 |
|--------|------|:---:|
| **metrics buffer** | buffer 占用率 | < 80% |
| **log writer** | 写入延迟 P99 | < 100ms |
| **trace collector** | 采集吞吐（spans/sec） | > 100 |
| **schema validator** | 校验拒绝率 | < 5% |
| **process alive** | 进程存活心跳 | 连续存活 |
| **disk space** | 数据目录可用空间 | > 10GB |

### Watchdog 自保设计

```
watchdog 自身崩溃:
  OS 级 systemd / Windows Service 自动重启
    → 重启后检查 Telemetry 状态
    → 若 Telemetry 已下线 > 5min → 直接 Escalation
```

### Meta-Telemetry / 自体内省 🆕

> **B81 修复**——v0.9.0 新增。§10 的健康检查关注的是"Telemetry 是否活着"（buffer 占用率、写入延迟）。但 Telemetry 还需要回答更深层的问题："Telemetry 自身产生了多少遥测？flush 的速度是否在退化？哪些模块在过度上报？"——即 telemetry 关于 telemetry。这是 Google SRE "monitor the monitoring" 的完整实现。

#### Meta-Metrics 维度

| Meta-Metric | 类型 | 含义 | 告警 |
|------------|------|------|:---:|
| `telemetry.metrics.ingress_rate` | gauge | 当前每秒接收 MetricPoint 数 | > 500 → ring buffer 压力 |
| `telemetry.metrics.flush_duration_ms` | histogram | 每次 flush 到 SQLite 的耗时 | P99 > 1000ms → SQLite 写性能退化 |
| `telemetry.metrics.flush_batch_size` | gauge | 每次 flush 写入的行数 | < 10 → 过于频繁的小批次 flush |
| `telemetry.metrics.buffer_depth_percent` | gauge | ring buffer 当前占用百分比 | > 80%（已有 backpressure 对接） |
| `telemetry.metrics.dropped_total` | counter | 因 buffer full / rate limit 丢弃的总数 | > 0 → 数据丢失 |
| `telemetry.logs.write_duration_ms` | histogram | 每次 JSONL 追加的耗时 | P99 > 500ms → IO 瓶颈 |
| `telemetry.traces.spans_collected_rate` | gauge | trace collector 当前采集速率 | 骤降 > 50% → trace 采集异常 |
| `telemetry.traces.sampled_ratio` | gauge | 实际采样比例 vs 配置采样率 | 偏差 > 10% → 采样逻辑 bug |
| `telemetry.schema.rejection_rate` | gauge | schema 校验拒绝率 | > 5% → 模块使用了未注册指标 |
| `telemetry.dlq.current_size_bytes` | gauge | DLQ 当前大小 | > 100MB（已有 §4 DLQ 监控） |
| `telemetry.cost.storage_bytes` | gauge | telemetry 数据磁盘总占用 | > 80% 预算（已有 §8b 成本降级） |
| `telemetry.per_module.ingress_top10` | gauge | 上报量前 10 的模块 | 单模块占比 > 50% → 可能失控 |

#### Meta-Telemetry 消费

```
Meta-Telemetry 通过三类消费者形成巡检闭环:
  1. Telemetry Watchdog (§10): 消费 buffer_depth + flush_duration → 健康评分
  2. FLE (§1 运营闭环): 消费 dropped_total + rejection_rate → 异常检测
  3. AI Agent (§14): 消费 per_module.ingress + flush 性能 → 自动诊断
     → "MOD-INF-008 上报量增长了 300%，建议检查是否 AI 生成了循环上报的代码"
```

#### Meta-Telemetry 存储策略

```
Meta-Metrics MUST 拥有独立 TTL:
  - ingress_rate / buffer_depth: 7 天（高频变化，价值递减快）
  - flush_duration / dropped_total: 30 天（性能退化需要长期趋势）
  - per_module 聚合: 90 天（模块行为分析需要更长视野）

  Meta-Metrics 不进入普通 metrics 表——独立 telemetry_meta 表存储
  → 避免 Meta-Metrics 污染用户可见的 Metric Discovery 结果
  → 仅通过 MCP tool get_telemetry_health() 暴露给 AI
```

---

## 11. alerts 子系统 🆕

> 告警规则引擎 + 多通道通知。对标 Google SRE Multi-Window Multi-Burn-Rate Alerts。

```
alerts 处理流程:
  SLI 实时计算（promql 风格查询 metrics 表）
    → Multi-Window Burn Rate 评估:
      短窗口(1h):  消耗 > 14.4x  → 紧急（P0）
      长窗口(6h):  消耗 > 6x     → 警告（P1）
      天窗口(3d):  消耗 > 1x     → 提示（P2）
    → 达到阈值 → 进入 Alert Pipeline:
      1. 去重（同 SLI 同窗口 5min 内不重复）
      2. 聚合（同模块多 SLI → 合并为一条 Incident）
      3. 静默（维护窗口内抑制非紧急告警）
      4. 路由（按 severity → channel）
         P0 → Feishu 群通知 + @owner
         P1 → Feishu 群通知
         P2 → Telemetry Dashboard badge
```

### Error Budget 告警矩阵

> 对标 Google SRE Workbook Ch5：Alerting on SLOs

| SLI | SLO Target | Error Budget | Short-Window Burn Rate (紧急) | Long-Window Burn Rate (警告) |
|-----|:---:|:---:|:---:|:---:|
| LLM 可用性 | 99.5% | 0.5% | > 14.4x (1h) | > 6x (6h) |
| Gate 通过率 | 95% | 5% | > 14.4x (1h) | > 6x (6h) |
| Pipeline 完成率 | 90% | 10% | > 14.4x (1h) | > 6x (6h) |

### 通知通道

| 通道 | 格式 | 目标 | 用途 |
|------|------|------|------|
| **Feishu Webhook** | 卡片消息（Markdown） | ZephyrAlpha 告警群 | P0/P1 实时告警 |
| **Feishu 日摘要** | 表格消息 | ZephyrAlpha 日志群 | 每日 09:00 推送前 24h 指标摘要 |
| **Telemetry Dashboard** | Grafana Alert 面板 | 本地 Dashboard | P2 级 + 趋势可视化 |
| **AI 消费通道** | MCP Server 暴露 `get_alerts()` tool | AI Agent Session | AI 发现告警后自动排查 |
| **Agent RBAC 通知** | 🆕 按 agent role 过滤告警可见性 | 各 Agent（L6 Observability 消费） | 避免 Agent 看到无权知晓的告警 |

### SLO 违规自动 Postmortem 🆕

> **B25 修复**——v0.5.0 新增。SLO 被突破时自动聚合相关遥测数据生成 Postmortem 草稿，写入 Audit Trail。由 FeatureFlag `telemetry.enable_slo_postmortem` 控制（默认 OFF）。

```
Postmortem 生成流程:
  Burn Rate Alert 触发（如 LLM 可用性短窗口 > 14.4x）
    → 自动聚合:
      - 违规时间段内的所有相关 traces（按 service + status 过滤）
      - 违规时间段内的 ERROR/FATAL 日志
      - 违规时间段内的相关指标时序（latency/error_rate 趋势）
      - 最近的 Annotation 事件（部署/配置变更/模型切换）
    → 生成 Markdown 格式 Postmortem 草稿:
      - 标题: "SLO Breach Postmortem — {SLI_NAME} — {time_range}"
      - 时间线摘要
      - 根因假设（基于 annotation 就近关联）
      - 受影响的 traces 列表（trace_id + summary）
    → 写入 Audit Trail（MOD-INF-020）标记为 POSTMORTEM_DRAFT
    → 通过 Escalation Protocol 推送摘要到 Feishu
```

### 合成监控（Synthetic Monitoring）🆕

> **B38 修复**——v0.7.0 新增。Google SRE 强调：白盒监控（内部 metrics）必须搭配黑盒监控（外部探针）。合成监控模拟真实用户/AI 行为路径，在问题影响到实际业务前发现故障。对 1 人维护场景，合成监控是"替代第二个值班工程师"的关键机制。

#### 合成事务定义

| 合成事务 | 模拟路径 | 频率 | 成功条件 |
|---------|---------|:---:|------|
| `synth.taskcard.e2e` | 创建 TaskCard → Context Engine → Gate G0-G7 → Pipeline → 完成 | 每 30min | status=complete within 5min |
| `synth.llm.health` | 向各 LLM Provider 发送最小化 health check prompt | 每 5min | response within 30s, token usage > 0 |
| `synth.context_engine.fetch` | 向 CE 请求已存在的 session 上下文 | 每 10min | response within 2s, context 非空 |
| `synth.gate.ping` | 向各 Gate 发送 ping 事件 | 每 5min | response within 1s |
| `synth.db.write_read` | SQLite/OLAP 写入→读取→删除 测试记录 | 每 10min | 读写延迟 < 100ms |
| `synth.mcp.tool_invoke` | MCP Server 调用 `get_service_health()` | 每 5min | 返回有效 HealthReport |

#### 合成监控与真实流量的区分

```
合成事务 MUST 携带标签:
  synthetic = true
  → Telemetry 自动排除合成流量参与 SLO 计算
  → 合成流量独立统计：SLI synth.*
  → Dashboard 自动标记合成数据与真实数据分离展示
```

### 告警规则测试 🆕

> **B46 修复**——v0.7.0 新增。告警规则配置后从未触发过 = 不确定是否正常工作。必须设计告警规则测试框架，确保每条告警规则在配置变更后经过验证。

#### 告警测试模式

| 测试模式 | 目的 | 触发方式 |
|---------|------|---------|
| **dry-run** | 新规则用历史数据回放，验证是否产生预期的告警 | 规则创建时自动执行 |
| **inject** | 注入人工构造的指标异常点，验证告警 Pipeline 端到端 | CI/CD 管线 / 人工触发 |
| **shadow** | 规则以 shadow mode 运行 24h，产生告警但不发送通知 | 规则从 dry-run → active 的过渡期 |
| **backtest** | 用过去 N 次已知事件（如过去的 SLO breach）回放规则 | 每季度 / 规则重大修改时 |

#### Synthetic Alert Injection Flow

```
告警注入测试流程:
  1. Telemetry 内部 synth endpoint 接收 inject 请求
  2. 按 AlertRule 的 SLI + burn_rate_window 注入对应异常数据点
  3. FLE 正常消费 → 触发 Burn Rate Alert → 进入 Alert Pipeline
  4. 验证：
     - 告警是否正确生成？（correct SLI, correct severity）
     - 通知是否正确路由？（Feishu channel, @owner）
     - 去重/聚合/静默是否正确？（5min 内不重复）
  5. 测试结果写入 Audit Trail: ALERT_TEST_RESULT {rule_id, passed, failures[]}
  6. 测试期间的通知标记为 [TEST] 前缀，不干扰真实告警
```

### Silent Alert 检测 🆕

```
Silent Alert 检测流程:
  每 24h 扫描 alert_rules.yaml 中所有 ACTIVE 规则:
    → 查询该规则最近 30 天是否至少触发过一次
    → 未触发过的规则 → 生成 SILENT_ALERT_REPORT:
      可能原因：
        - 规则阈值过高（系统从未达到）
        - SLI 数据采集缺失（§12 SLO drift check 已覆盖）
        - 规则表达式错误
    → P2 提醒："{rule_name} 已静默 {days} 天，建议审查阈值或废弃规则"
    → AI session 冷启动时自动检查 silent alert 列表
```

---

## 12. schema 子系统 🆕

> 指标 Schema 注册表 + 运行时校验 + 蓝图漂移检测。解决 R3（指标定义不一致）+ B4（缺少强制校验）。

```
schema 工作流:
  模块开发者/蓝图定义 MetricSchema → schema registry (YAML SSoT)
    → 代码生成（codegen：schema → Python MetricSchema dataclass）
    → 运行时校验：metrics.report() 前检查 name+type+labels 合法性
    → 校验拒绝 → 写入 rejection log + 通知模块 owner
    → 蓝图漂移检测：蓝图声称的文件 vs 磁盘实际 → delta report
```

### MetricSchema 数据模型

```python
@dataclass
class MetricSchema:
    name: str               # 全局唯一的指标名
    type: str               # gauge / counter / histogram / summary
    unit: str               # ms / bytes / count / usd
    description: str        # 人类可读描述 + AI prompt hint
    module_id: str          # 所属模块 MOD-INF-XXX
    labels: list[LabelDef]  # 合法标签定义
    slo_target: float | None  # 如有关联 SLO
    cardinality_limit: int  # 标签组合上限，默认 1000
    deprecated: bool        # 是否已废弃
    replaced_by: str | None # 替换指标名

@dataclass
class LabelDef:
    name: str
    allowed_values: list[str] | None  # None = 任意值（危险，建议限制）
    cardinality_high: bool            # True → 高基数标签，独立限流
```

### 蓝图漂移检测

```
drift check 流程:
  blueprint §11（已实现代码索引）声称: 文件 X 存在，状态 implemented
    → 磁盘扫描: X 是否真实存在？sha256 是否匹配？
    → 生成 drift_report:
      ├── missing_files: 蓝图声称有但磁盘没有
      ├── extra_files: 磁盘有但蓝图未登记
      └── status_mismatch: 蓝图说 implemented 但实际是 skeleton
    → 在 AI 下次 session 冷启动时自动提示漂移警告
```

### SLO 采集覆盖检测 🆕

> **B26 修复**——v0.5.0 新增。蓝图漂移检测不仅检查文件，还需检查：蓝图声称的 SLO 是否真的有对应的 SLI 在采集。

```
SLO drift check 流程:
  蓝图 §4（关键 SLI）声称: {sli_name, slo_target}
    → schema registry 查询: 该 SLI 的 MetricSchema 是否已注册？
    → metrics 表查询: 该 SLI 是否有近 24h 的活跃数据点？
    → 生成 slo_drift_report:
      ├── orphan_slos: 蓝图声明了 SLO 但无对应 MetricSchema / 无数据
      └── orphan_metrics: 有 MetricSchema 和活跃数据点但蓝图未声明 SLO
    → orphan_slos → P2 提醒：「SLO 声明了但从未被采集，无法验证合规」
```

### 告警规则漂移检测 🆕

```
alert_rule drift check:
  蓝图 §11（Error Budget 告警矩阵）声称的告警规则
    → alert_rules.yaml 是否包含对应规则？
    → 生成 alert_rule_drift_report → P2 提醒
```

### CI/CD Pipeline 可观测性 🆕

> **B41 修复**——v0.7.0 新增。对于 100% AI 施工场景，部署和构建的可观测性与运行时同样重要。AI 需要知道它生成的代码是否正确部署、测试是否通过、部署是否引入了回归。

#### CI/CD 遥测维度

| 维度 | 指标 | 采集来源 | 告警阈值 |
|------|------|---------|:---:|
| **构建健康** | build_duration_seconds | CI 日志 | > 10min → 构建膨胀 |
| | build_success_rate | CI 状态 | < 90% → 代码质量下降 |
| | build_failure_by_reason | CI 错误分类 | type=flake > 20% → 测试不稳定 |
| **测试质量** | test_pass_rate | test report | < 95% → 阻塞部署 |
| | test_flakiness_score | 同 test 连续 N 次结果 | > 30% flaky → 需修复测试 |
| | test_coverage_delta | coverage report vs baseline | delta < -5% → 覆盖率退化 |
| **部署健康** | deploy_frequency | deploy event | 突降 > 50% → pipeline 阻塞 |
| | deploy_failure_rate | deploy status | > 10% → 回滚风险 |
| | deploy_rollback_count | rollback event | > 3/周 → 部署质量异常 |
| | lead_time_for_changes | commit → deploy 时间 | > 24h → 交付瓶颈 |
| **AI 专属** | ai_generated_code_ratio | git diff AI-authored % | > 90% 突增 → AI 失控 |
| | code_review_bypass_rate | PR merged without human review | > 5% → 人类监督失效 |

#### CI/CD 事件注入 Announcements

```
CI/CD 事件自动作为 Annotations 注入 Telemetry 时间线:
  - build_start → build_end: 构建窗口标记
  - deploy_start → deploy_end: 部署窗口标记
  - rollback: 回滚标记（红色标注）
  - test_suite_pass/fail: 测试通过/失败标记
  → 部署后 5min 内出现异常 → AI 自动关联 "是否最近的部署引入的？"
```

#### 部署验证自动化

```
部署后自动验证流程 (Post-Deployment Validation):
  deploy 完成 → 自动触发:
    → 1. 合成监控事务运行（§11b synth.taskcard.e2e）
    → 2. 与 pre-deploy 基线的 metrics 对比:
        - latency P95 delta > 20% → 性能回归
        - error_rate delta > 5% → 错误率上升
        - ai_behavior hallucination_score delta < -0.1 → 模型表现退化
    → 3. 任一回归 → FLE 自动触发 rollback
    → 4. 全部通过 → 标记 deploy 为 VERIFIED
```

### SLI 定义注册表 🆕

> **B54 修复**——v0.7.0 新增。Google SRE Workbook 要求每个 SLI 有标准化的定义格式：名称、公式（可执行形式）、评估窗口、数据源、Owner。蓝图 §4 的 SLI 列表是 ad-hoc 的。SLI 定义必须在 Schema Registry 中正式注册，使 AI 和告警规则能消费结构化 SLI 定义。

#### SLI 定义 Schema

```python
@dataclass
class SliDefinition:
    sli_name: str              # 全局唯一 SLI 名
    display_name: str          # 人类可读名称
    formula: str               # 可执行公式（promql 风格）
    formula_description: str   # 人类可读公式说明 + AI prompt hint
    metric_source: str         # 数据源 MetricSchema name（关联 §12 schema registry）
    evaluation_window: str     # 评估窗口（1m / 5m / 1h / 1d）
    slo_target: float          # SLO 目标（如 0.995 = 99.5%）
    slo_window: str            # SLO 合规窗口（30d / 7d）
    error_budget: float        # 错误预算 = 1 - slo_target
    owner_module: str          # Owner MOD-INF-XXX
    severity: str              # 违规严重级别（P0/P1/P2）
    blueprint_ref: str         # 蓝图定义位置（§4 关键 SLI）
    deprecated: bool           # 是否已废弃
```

#### SLI 注册表示例（YAML SSoT: config/sli_registry.yaml）

```yaml
slis:
  - sli_name: "llm_availability"
    display_name: "LLM 可用性"
    formula: "sum(rate(llm_calls_total{status='success'}[5m])) / sum(rate(llm_calls_total[5m]))"
    formula_description: "成功 LLM 调用 / 总调用。排除 rate_limit 导致的 expected errors"
    metric_source: "llm_calls_total"
    evaluation_window: "5m"
    slo_target: 0.995
    slo_window: "30d"
    error_budget: 0.005
    owner_module: "MOD-INF-015"
    severity: "P0"
    blueprint_ref: "§4 关键 SLI"

  - sli_name: "telemetry_self_health"
    display_name: "Telemetry 自体健康"
    formula: "sum(rate(telemetry_metric_write_success[5m])) / sum(rate(telemetry_metric_write_total[5m]))"
    formula_description: "遥测数据写入成功率"
    metric_source: "telemetry_metric_write_total"
    evaluation_window: "5m"
    slo_target: 0.999
    slo_window: "7d"
    error_budget: 0.001
    owner_module: "MOD-INF-015"
    severity: "P0"
    blueprint_ref: "§4 关键 SLI"
```

#### SLI 注册表与告警规则的自动生成

```
SLI Registry → 自动生成告警规则:
  1. 从 sli_registry.yaml 读取所有 SLI 定义
  2. 按 slo_target + slo_window 自动计算 Multi-Window Burn Rate 阈值
  3. 生成 alert_rules.yaml 条目
  4. 人工审核后启用
  5. Schema drift check 检测：sli_registry.yaml 与 alert_rules.yaml 是否同步
```

### Schema 版本化与向后兼容 🆕

> **B62+B63 修复**——v0.8.0 新增。OTel 定义了正式的 Telemetry Schema 模型（Schema URL + rename transformations），允许指定如何在不同 schema 版本间转换遥测数据。Telemetry 的 Schema Registry 必须支持版本化演进——指标重命名、标签增删、类型变更——且保证历史数据仍可查询。

#### Schema 版本号格式

```
版本号格式（兼容 OTel Schema URL）:
  v{major}.{minor}
  → v1.0, v1.1, v2.0

  major 变更: breaking change（指标类型变更、删除指标）
  minor 变更: backward-compatible（新增指标、新增可选标签、重命名有别名）
```

#### 兼容性矩阵

| 变更类型 | 兼容性 | Schema Registry 行为 | 历史数据处理方式 |
|---------|:---:|---------------------|----------------|
| **新增 MetricSchema** | ✅ 完全兼容 | 注册新 schema，vX.(N+1) | 旧数据不受影响，新数据从新 schema 开始 |
| **新增可选标签** | ✅ 完全兼容 | 标签白名单扩展，vX.(N+1) | 旧数据标签为 NULL → 查询时自动填充 "unknown" |
| **重命名指标** | ⚠️ 需别名 | 旧名保留为 alias → new_name，vX.(N+1) | 两名字并存 2 个版本后废弃旧名；查询自动 alias → 实际指标 |
| **重命名标签** | ⚠️ 需别名 | rename_attributes transformation，vX.(N+1) | 类似指标重命名，标签别名保留 2 个版本 |
| **新增必填标签** | ❌ 不兼容 | MUST 升级 major 版本，v(X+1).0 | 旧数据缺失新标签 → 查询时过滤或默认值填充 |
| **删除指标/标签** | ❌ 不兼容 | MUST 升级 major 版本，v(X+1).0 | 旧数据保留但标记 deprecated，Dashboard 迁移到新指标 |
| **类型变更**（counter→histogram） | ❌ 不兼容 | MUST 升级 major 版本，v(X+1).0 | 旧类型数据不可合并，建议新指标名 |

#### Schema 别名策略

```yaml
# config/metrics_schema.yaml 中的别名示例
metrics:
  - name: "llm_calls_total"       # 当前有效名
    schema_version: "v1.2"
    alias_of: null
    aliases:                      # 此指标的前身
      - {old_name: "llm_api_calls", deprecated_at: "v1.0", remove_after: "v2.0"}
      - {old_name: "openai_calls",  deprecated_at: "v0.8", remove_after: "v1.0"}
  → 查询 "llm_api_calls" 时，Schema Registry 自动重定向到 "llm_calls_total"
  → alias 在 remove_after 版本后物理删除（不再支持查询旧名）
```

#### 蓝图漂移检测的版本化扩展

```
Schema drift check 版本化增强:
  蓝图声称的 MetricSchema version = vX.Y
    → 磁盘上的 metrics_schema.yaml 版本是否 ≥ vX.Y？
    → 版本落后 → P2 提醒：「蓝图要求 vX.Y，磁盘 schema 仍为 vX.(Y-1)，请更新」
    → 版本超前 → 提示：「磁盘 schema 超前于蓝图，请确认是否已手动变更」
```

---

## 13. 施工进度

| 子系统 | 阶段 | 完成度 | 说明 |
|--------|------|:---:|------|
| metrics | complete | ██ 100% | MetricPoint + ring buffer(500) + cardinality控制 — facade.py MetricsFacade 完整 |
| logs | complete | ██ 100% | structlog 配置 + JSONL writer + trace_id 注入 + ring buffer + RULE-ONE 原子写入 |
| traces | complete | ██ 100% | Span 数据结构 + W3C TraceContext 传播 + SpanContextManager + TraceSampler + span/log 关联 |
| ai_behavior | complete | ██ 100% | AIBehaviorEvent 数据类(16字段) + 7 维度 + Error Taxonomy(4维) + 可疑事件自动标记 |
| archive | complete | ██ 100% | TTL 分级策略 + gzip 压缩 + SQLite .backup + 成本感知降级(3级) |
| profiles | complete | ██ 100% | psutil 性能剖析(start/stop/snapshot) — profiles.py 完整 |
| health | complete | ██ 100% | register/set_unhealthy/status/shutdown — health.py 完整 |
| alerts | complete | ██ 100% | evaluate/ack/pending + alert_rules.yaml 规则驱动 — alerts.py 完整 |
| schema | complete | ██ 100% | get_version/check_compatibility/validate_metric_name — schema.py 完整 |
| facade | complete | ██ 100% | Telemetry 统一门面: 全部 9 子系统桥接到下辖实现; test_mode 支持 |

### 下一步施工

| 优先级 | 任务 | 预估工时 |
|:---:|------|:---:|
| **P0** | `traces/__init__.py` → W3C TraceContext 传播 + span/log 关联 | 4h |
| **P0** | `health/__init__.py` → 独立 watchdog 进程 + 健康检查 endpoint | 4h |
| **P0** | `alerts/__init__.py` → Feishu Webhook 通知通道（最小可行） | 2h |
| P0 | `metrics/__init__.py` → MetricPoint + ring_buffer(10000) + flush | 4h |
| P0 | `logs/__init__.py` → structlog config + JSONL file writer + trace_id注入 | 3h |
| P1 | `traces/__init__.py` → 智能采样 + span→metrics connector | 3h |
| P1 | `schema/__init__.py` → MetricSchema 数据类 + YAML registry + 运行时校验 | 4h |
| P2 | `ai_behavior/__init__.py` → AIBehaviorEvent 数据类 + 7维度 tracker | 6h |
| P2 | `profiles/__init__.py` → py-spy 集成 + pprof 输出 | 4h |
| P2 | `archive/__init__.py` → gzip compressor + TTL reaper + sqlite .backup 每日作业 | 2h |
| P2 | `health/__init__.py` → LifecycleManager 集成（轮询所有模块 health_check） | 2h |

### 预热期（Warm-Up Period）🆕

> **B22 修复**——v0.5.0 新增。Telemetry 首次部署时没有历史基线，FLE 无法做异常检测。需声明预热期策略。

```
预热期流程:
  Telemetry 启动 → 检测是否为首次运行（无历史数据）
    → 进入 WARM_UP 模式（48h）:
      - 全量采集但不触发告警
      - FLE 仅建立基线模型（计算各 SLI 的 mean/std/seasonal pattern）
      - 状态标记为 TELEMETRY_STATE = "WARM_UP"
    → 48h 后自动切换到 NORMAL 模式:
      - 启用全级别告警
      - 状态标记为 TELEMETRY_STATE = "NORMAL"
      - 生成 baseline_summary → 写入 Audit Trail
```

### 环境初始化检查清单 🆕

```
Telemetry 首次部署到新环境（dev/staging/prod）时:
  1. 确认 data/telemetry/{environment}/ 目录结构已创建
  2. 确认 config/metrics_schema.yaml 已包含最小 schema 集合
  3. 确认 config/alert_rules.yaml 已创建（可为空，后续 FLE 自生成）
  4. 确认 FeatureFlag config/flags.yaml 中 telemetry.* flags 已初始化
  5. 确认 shared/logging.py 已配置正确的环境标识
  6. 启动 → 自动进入 WARM_UP 模式（48h）
```

---

## 14. AI 可消费性设计

> 核心洞察（Sentry 2025）：LLM 无法看到代码运行时的行为。Telemetry 必须通过 MCP 向 AI 暴露运行时反馈，形成自我修正闭环。

### MCP Server 暴露的遥测接口

```
Telemetry MCP Server tools（供 AI Agent 在 session 中调用）:

  get_recent_alerts(module?: str, time_range?: str) → list[Alert]
    → AI 发现新告警后自动排查

  get_service_health(module?: str) → HealthReport
    → AI 施工前检查目标模块健康状态

  get_slo_status(sli_name: str) → SLOStatus {current, target, budget_remaining}
    → AI 评估"是否能继续部署新代码"

  get_recent_traces(module: str, status?: str, limit?: int) → list[TraceSummary]
    → AI 排查错误时获取最近错误 trace

  get_cost_breakdown(time_range: str) → CostReport {by_model, by_module, by_task_type}
    → AI 检查 LLM 成本是否异常

  get_blueprint_drift() → DriftReport
    → AI session 冷启动时自动检查蓝图-代码一致性
```

### AI Session 冷启动工作流

```
AI Agent 启动 session:
  1. 自动调用 get_blueprint_drift() → 确认蓝图无漂移
  2. 自动调用 get_service_health(target_module) → 确认目标健康
  3. 自动调用 get_recent_alerts() → 检查是否有未处理告警
  4. 自动调用 get_silent_alerts() → 检查静默告警（§11b）
  5. 自动调用 get_dlq_summary() → 检查 DLQ 积压（§4 DLQ）
  6. 自动调用 get_telemetry_cost() → 检查遥测成本状态（§8b）
  7. 开始施工（以上全部 green 才继续）
```

### 自描述遥测与 Metric 发现 API 🆕

> **B50 修复**——v0.7.0 新增。AI 消费遥测数据时最大的障碍是不知有哪些数据可用。专业实践（Honeycomb、Datadog）通过 API 暴露元数据发现能力。Telemetry 必须使 AI 能够"询问有哪些指标、它们代表什么、如何查询"——而不需要先查阅蓝图。

#### Metric Discovery MCP Tools

```
Telemetry MCP Server 新增 tools（metric discovery 类别）:

  list_metrics(module?: str, type?: str) → list[MetricSummary]
    → 列出所有可用指标及其基本信息
    → MetricSummary {name, type, unit, description, module_id, labels[], slo_target?}

  get_metric_detail(name: str) → MetricDetail
    → 获取指定指标的完整元数据
    → MetricDetail {schema: MetricSchema, sli: SliDefinition?, recent_values: TimeSeriesSample[],
                     cardinality: CardinalityStatus, sample_queries: str[]}

  search_metrics(query: str) → list[MetricSummary]
    → 自然语言 / 关键词搜索指标
    → 例: AI 问 "有哪些关于成本的指标？" → search_metrics("cost")
    → 返回所有 name/description/labels 包含 "cost" 的指标

  get_metrics_by_slo(slo_name: str) → list[MetricSummary]
    → 获取与特定 SLO 关联的所有指标
    → 例: "LLM 可用性 SLO 依赖哪些指标？"
```

#### 自描述数据约定

```
每个 MetricPoint 在持久化时自动附带其 schema 引用:
  {
    "metric": {"name": "llm_calls_total", "type": "counter", "unit": "count"},
    "schema_version": "1.2",
    "schema_uri": "config/metrics_schema.yaml#llm_calls_total",
    "labels": {"module": "MOD-INF-008", "model": "gpt-4"},
    "value": 150,
    "timestamp": 1717545600.0
  }

  → AI 拿到任意 metric 数据点即可追溯其完整语义定义
  → 无需并行查阅蓝图
```

#### AI 交互示例

```
AI Agent: "这个系统的 LLM 成本是怎么分布的？"

  → AI 首先调用 search_metrics("cost") → 找到 metrics "llm_cost_usd_total" + "llm_cost_per_task_usd"
  → 调用 get_metric_detail("llm_cost_usd_total") → 获取完整 schema + 示例查询
  → 调用 get_cost_breakdown("7d") → 获取实际数据
  → AI 综合分析并回答
```

---

## 15. 施工指引

### 15.1 metrics 施工

```
1. 创建 MetricPoint 数据类（name/value/timestamp/labels/type/exemplar）
2. 实现 RingBuffer（collections.deque, maxlen=10000）
3. 实现 flush() → SQLite metrics 表批量写入（原子事务）
4. 集成 schema validator → report() 前校验
5. 暴露 report(metric: MetricPoint) 接口供各模块调用
6. 实现 cardinality tracker + 超限自动聚合
```

### 15.2 logs 施工

```
1. 配置 structlog（JSONRenderer + Timestamper + trace_id/span_id ContextVar）
2. 实现 JSONLFileWriter——按日轮转，文件名 {date}.jsonl
3. 暴露 get_logger(module_name) → BoundLogger
4. 集成 TraceContext → 自动注入 trace_id/span_id
5. 集成 fail-closed：日志写入失败 → stderr fallback → 内存环形缓冲 → 丢弃+告警
6. PII 脱敏 filter processor
```

### 15.3 traces 施工

```
1. 创建 Span + SpanContext 数据类（W3C 兼容 trace_id/span_id 格式）
2. 实现 TraceContext 管理器（ContextVar 存储当前 span）
3. 实现 context 传播——跨模块调用时自动注入/提取 traceparent
4. 实现 tail-based sampler（全保留 error + high-latency + root, 10% 正常采样）
5. 实现 span→metrics connector（自动生成 RED 指标）
```

### 15.4 AI 行为施工

```
1. 创建 AIBehaviorEvent 数据类（7维度字段）
2. 实现模型调用 hook（拦截 LLM API 调用，记录 model/token/cost）
3. 实现 prompt 版本追踪（prompt_template_id → version → hash）
4. 实现工具调用链记录（tool_name + args_hash + duration + result）
5. 实现幻觉率评估接口（接受 KB ground truth 比对）
6. 实现决策路径记录（decision_point → options → chosen → rationale）
```

### 15.5 测试清单

```
□ MetricPoint 序列化/反序列化
□ RingBuffer 满时自动丢弃最旧数据
□ flush() 批量写入 SQLite 原子性
□ JSONL 日志文件按日轮转
□ JSONL 自动注入 trace_id/span_id
□ traceparent header 传播→下游模块→子 Span 创建
□ tail-based sampler 全保留 error/高延迟/root span
□ schema validator 拒绝未注册指标名
□ cardinality > 1000 触发聚合
□ Feishu Webhook P0 告警送达
□ watchdog 检测到 Telemetry 不健康 → 自动重启
□ archive gzip 压缩后原文件删除
□ FLE 消费 metrics 延迟 < 1s (P99)
□ blueprint drift check → 发现 missing file → 生成 report
```

### 15.6 Telemetry 集成测试设计 🆕

> **B64+B65 修复**——v0.8.0 新增。15.5 的测试清单是单元/单体测试。但 Telemetry 是全系统的中枢——其正确性影响所有模块的自我诊断能力。必须设计覆盖 Telemetry 全链路的集成测试。对于 100% AI 施工，测试是 AI 不会写崩 Telemetry 的最后保障。

#### 集成测试维度

| 测试场景 | 覆盖链路 | 验证点 | 实现方式 |
|---------|---------|--------|---------|
| **端到端 metric 写入→查询** | module.report() → ring buffer → flush → SQLite → query | 写入值与查询值一致、延迟 < 2s | pytest + SQLite in-memory |
| **端到端 log 写入→检索** | module.log.info() → JSONL file → grep | 日志内容 + trace_id 自动注入 | tmpdir fixture |
| **跨模块 Trace 传播** | module-A span → contextvars → module-B child span | parent_span_id 正确关联、trace_id 一致 | mock 跨模块调用 |
| **Backpressure 端到端** | 高速写入 → ring buffer 80% → Throttle 发出 → 上游降速 | Throttle/Pause/Resume 正确触发顺序 | 固定高频写入 test |
| **Schema 校验端到端** | 未注册 metric → report() → rejection + DLQ 写入 | DLQ 包含正确 rejection_reason | 未注册指标名测试 |
| **FeatureFlag 切换端到端** | 关闭 `telemetry.enable_ai_behavior_tracking` → AI 行为不再写入 | flag=OFF 后无新 AIBehaviorEvent | flags.yaml test fixture |
| **Alert Pipeline 端到端** | 注入异常数据点 → FLE 消费 → burn rate 检测 → alert → Feishu webhook | 全链路 < 30s | §11b inject 模式 |
| **DLQ 自动修复端到端** | 注入 schema error → DLQ → 新 schema 生效 → 自动修复 → 重新写入 | repair_success_rate | schema 版本切换 fixture |
| **Disaster Recovery 端到端** | 删除 SQLite → 从 archive replay → 重建 | 重建后数据完整性与原数据一致（99.9%+） | 数据比对脚本 |

#### 测试模式

```
Telemetry Test Modes:
  - test_mode=True: 所有写入 noop，用于模块单元测试（避免依赖真 Telemetry）
  - test_mode="integration": 使用真实的 SQLite in-memory + tmpdir JSONL，完整链路
  - test_mode="production": 使用真实磁盘路径，用于 staging 环境验证
```

### 15.7 Telemetry 性能基准 🆕

> 对 1 人维护场景，Telemetry 的性能开销必须控制在可忽略的量级。以下基准定义了 P0-Blocker vs P1-ShouldFix vs P2-NiceToHave 的性能目标。

| 基准项 | 目标 | 级别 | 测量方式 |
|--------|:---:|:---:|------|
| `metric.report()` 单次调用延迟 | < 1ms | P0-Blocker | time.perf_counter() 在 report() 包装器 |
| `log.info()` 单次调用延迟 | < 2ms | P0-Blocker | 同上 |
| `span.start()` + `span.end()` | < 5ms | P1-ShouldFix | 同上 |
| `flush()` 批量 1000 条 metric 写入 | < 500ms | P1-ShouldFix | batch flush benchmark |
| cardinality check 开销（100 个 active labels） | < 50µs per check | P2-NiceToHave | cardinality_tracker.check() |
| HMAC integrity 计算开销（per log line） | < 10µs | P2-NiceToHave | 测量 hmac.digest() 调用 |
| Telemetry 总 CPU 占用（idle 状态） | < 1% 单核 | P0-Blocker | psutil.cpu_percent(telemetry_pid) |
| Telemetry 总内存占用（steady state） | < 256MB | P0-Blocker | psutil.Process().memory_info() |

---

## 16. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 系统遥测——9子模块目录结构已规划，代码全skeleton。

### 16.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/telemetry/blueprint_metrics.py` | ✅ 已实现 | T-V2-011 experimental — `record_blueprint_read()` instrumentation |
| `src/zephyr/l12_system_telemetry/__init__.py` | ✅ skeleton | 根包入口 |
| `src/zephyr/l12_system_telemetry/contract_metrics.py` | ✅ skeleton | 契约指标采集 |
| `src/zephyr/l12_system_telemetry/metrics/__init__.py` | 🟡 skeleton | metrics 子系统骨架 |
| `src/zephyr/l12_system_telemetry/logs/__init__.py` | 🟡 skeleton | logs 子系统骨架 |
| `src/zephyr/l12_system_telemetry/traces/__init__.py` | 🟡 skeleton | traces 子系统骨架 |
| `src/zephyr/l12_system_telemetry/ai_behavior/__init__.py` | 🟡 skeleton | ai_behavior 子系统骨架 |
| `src/zephyr/l12_system_telemetry/archive/__init__.py` | 🟡 skeleton | archive 子系统骨架 |
| `src/zephyr/l12_system_telemetry/profiles/__init__.py` | ⚪ 待建 | 🆕 profiles 子系统 |
| `src/zephyr/l12_system_telemetry/health/__init__.py` | ⚪ 待建 | 🆕 health 子系统 |
| `src/zephyr/l12_system_telemetry/alerts/__init__.py` | ⚪ 待建 | 🆕 alerts 子系统 |
| `src/zephyr/l12_system_telemetry/schema/__init__.py` | ⚪ 待建 | 🆕 schema 子系统 |
| `src/zephyr/shared/contracts/telemetry_emitter.py` | ✅ auto_generated | CTR-P1-013 — TelemetryEmitter 数据契约 |

### 16.2 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §16（本节）→ 知道「哪些已实现、在哪里」
2. 读 §3 九子系统 → 知道「每个模块的职责和 AI 自治权限」
3. 读 §13 施工进度 → 知道「下一步该做什么」
4. 调用 `get_blueprint_drift()` → 确认蓝图无漂移

---

## 17. 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\system-telemetry\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\` | Telemetry 源码（skeleton） |
| 遥测数据 | `D:\ZephyrAlpha\data\telemetry\` | 遥测数据存储 |
| DLQ 数据 | `D:\ZephyrAlpha\data\telemetry\{environment}\dlq\` | 🆕 DLQ 死信队列存储 |
| emergency_shutdown | `D:\ZephyrAlpha\data\telemetry\{environment}\emergency_shutdown.jsonl` | 🆕 异常关闭时缓冲区紧急转储 |
| telemetry_meta | `D:\ZephyrAlpha\data\telemetry\{environment}\telemetry_meta.db` | 🆕 Meta-Telemetry 自体内省独立存储（§10b） |
| blueprint_metrics | `D:\ZephyrAlpha\src\zephyr\telemetry\blueprint_metrics.py` | 蓝图度量（已实现） |
| telemetry_access_log | `D:\ZephyrAlpha\data\telemetry\{environment}\telemetry_access_log.jsonl` | 🆕 遥测访问审计日志 |
| Schema Registry | `D:\ZephyrAlpha\config\metrics_schema.yaml` | 🆕 指标 schema SSoT |
| Alert Rules | `D:\ZephyrAlpha\config\alert_rules.yaml` | 🆕 告警规则定义 |
| SLI Registry | `D:\ZephyrAlpha\config\sli_registry.yaml` | 🆕 SLI 定义注册表（§12c） |
| Feature Flags | `D:\ZephyrAlpha\config\flags.yaml` | 🆕 FeatureFlag 定义（§2e） |
| Dashboards | `D:\ZephyrAlpha\config\dashboards\` | 🆕 Dashboard-as-Code（§2h） |
| Test Fixtures | `D:\ZephyrAlpha\tests\telemetry\` | 🆕 Telemetry 集成测试（§15.6） |

---

## 18. 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Audit Trail (MOD-INF-020) | 遥测事件 → 审计日志 | `telemetry_collector` → `audit_writer` | 遥测事件写入审计 |
| Feedback Loop (MOD-INF-010) | 遥测驱动的异常检测 | FLE detect → `telemetry_anomaly_signal` | 异常指标触发 FLE |
| Budget Enforcer (MOD-INF-024) | 成本 metrics | `cost_collector` → `budget_tracker` | token 消耗可追踪 |
| Escalation Protocol (MOD-INF-022) | 告警升级通知 | `alert_router` → `escalation_handler` | P0 告警触达人工 |
| LLM Security (MOD-INF-014) | AI 行为安全事件 | `ai_behavior` → `lsg_security_gateway` | 异常 prompt/幻觉触发拦截 |
| AI Agent Session（MCP） | 🆕 运行时遥测反馈 | Telemetry MCP Server → AI Agent tools | AI 调用 `get_alerts()` 返回有效数据 |
| 所有 L00-L13 模块 | metrics/logs/traces 采集 | 各模块 → `telemetry_exporter` | 全系统可观测 |

---

## 19. 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 版本号+完整度 | 蓝图补全后更新 |
| 2 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | Telemetry 模块状态 | 代码施工后更新 |
| 3 | L12 架构模型 | `D:\ZephyrAlpha\architecture-model\layers\l12_system_telemetry.yaml` | 🆕 新增 4 子模块定义 | 子模块扩展后同步 |
| 4 | 跨层契约 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\contracts\cross-layer-contracts.yaml` | 🆕 新增 MCP 接口契约 | AI 可消费性设计落地 |

---

## 20. 已知风险与缓解

| # | 风险 | 概率 | 影响 | 缓解策略 |
|---|------|:---:|:---:|---------|
| R1 | 遥测数据量爆炸——9 子系统 × 14 层模块持续产出 | 高 | 中 | 智能采样（B5）+ 聚合 + TTL + cardinality 控制（§4） |
| R2 | 监控系统自身故障——Telemetry 自身出问题无法感知 | 中 | 高 | 独立 watchdog 进程（§10）+ OS 级进程守护 + 自体健康评分 |
| R3 | 指标定义不一致——不同模块同名指标含义不同 | 高 | 中 | Schema Registry（§12）+ 运行时校验 + 蓝图漂移检测 |
| R4 | 采集性能开销——同步采集阻塞业务操作 | 中 | 中 | 异步采集 + 批量写入（100ms 窗口）+ 反压机制 |
| R5 | **Cardinality 爆炸**——高基数标签导致 DB 膨胀 | 中 | 高 | 标签白名单 + 基数上限 1000 + 告警阈值 800 + TTL 裁剪 + strict_mode FeatureFlag（§4） |
| R6 | **蓝图-代码漂移**——AI session 被过期蓝图误导 | 中 | 高 | 自动漂移检测（§12）+ SLO 采集覆盖检测 + 告警规则漂移检测 + session 冷启动检查（§14） |
| R7 | **PII/敏感数据泄露**——遥测日志含 API Key/密码 | 低 | 高 | 日志脱敏 filter + 数据分级 + 访问控制（§5） |
| R8 | **告警噪声**——Multi-Window 告警过灵敏导致疲劳 | 中 | 中 | Burn Rate 多窗口（§11）+ 去重 + 聚合 + 静默窗口 |
| R9 | **成本失控**——LLM API 用量暴涨无预警 | 中 | 中 | ai_behavior FinOps 追踪（§7.2）+ Budget Enforcer 联动 |
| R10 | **🆕 重复造轮子**——AI 不读 §3b 直接写入独立实现 | 高 | 高 | §3b 复用清单 + AI 施工约束（MUST 使用 shared 组件，禁止重定义） |
| R11 | **🆕 环境数据污染**——dev 的低质量数据混入 prod 告警 | 中 | 高 | 数据路径隔离（§2d）+ environment 标签 + FLE 环境感知过滤 |
| R12 | **🆕 失控模块淹没 Telemetry**——单模块突发海量 MetricPoint | 低 | 高 | per-module 速率限制 + Backpressure Throttle/Pause + ring buffer 水位线（§4） |
| R13 | **🆕 OTel 语义约定漂移**——OTel GenAI/Agent 标准更新后 Telemetry 字段不同步 | 中 | 中 | §2f 对齐声明 + AI 施工约定（2版本内同步）+ schema drift check |
| R14 | **🆕 Counter 重置误报**——进程重启后 counter 归零触发 FLE spike 误告警 | 中 | 中 | §4 Counter 重置检测（process_start_ts + FLE reset-aware） |
| R15 | **🆕 DLQ 积压失控**——大量 rejected events 堆积导致 DLQ 存储爆炸 | 低 | 中 | §4 DLQ 自动修复 + 重试上限 + DLQ 容量告警 |
| R16 | **🆕 跨进程 Trace 断裂**——contextvars 无法跨越进程边界导致 trace 不完整 | 高 | 高 | §6b 跨进程 W3C TraceContext 传播 + 5 种传播载体 |
| R17 | **🆕 告警规则从未触发（Silent Alert）**——配置错误的告警静默失效 | 中 | 高 | §11b 告警规则测试（dry-run/shadow/inject/backtest）+ Silent Alert 每日扫描 |
| R18 | **🆕 合成监控自身故障**——synth probe 失败但未能区分是 probe 自身问题还是系统问题 | 低 | 中 | synth probe 独立 watchdog + synth probe 自检事务 |
| R19 | **🆕 CI/CD 管线不可观测**——部署失败后无法追溯根因，AI 无法自我修正部署问题 | 中 | 高 | §12b CI/CD Pipeline 可观测性 + Post-Deployment Validation |
| R20 | **🆕 遥测成本超预算**——9 子系统持续产出数据超出磁盘预算 | 中 | 高 | §8b 遥测成本预算 + 三级降级策略（TLL缩减→采样降频→非prod暂停） |
| R21 | **🆕 指标定义孤立**——AI 无法自助发现指标含义，依赖蓝图查阅 | 高 | 中 | §14b 自描述遥测 + Metric Discovery MCP tools（list/search/detail） |
| R22 | **🆕 遥测数据泄露**——原始 telemetry SQLite/JSONL 文件包含敏感信息 | 高 | 高 | §2g 加密 at rest + PII 字段级脱敏 + 访问控制 + HMAC 防篡改 |
| R23 | **🆕 OWASP MCP08 不合规**——系统审计时发现遥测安全基线未达标 | 低 | 高 | §2g OWASP MCP08 对齐声明 + 9 项要求逐条覆盖 |
| R24 | **🆕 Schema 不兼容升级**——指标重命名/删标签导致 Dashboard + Alert 断裂 | 中 | 中 | §12d Schema 版本化 + alias 策略 + 兼容性矩阵 |
| R25 | **🆕 时钟偏差导致 Trace 错乱**——无 NTP 的多进程间时钟不同步 | 中 | 中 | §4 时钟偏差检测 + monotonic clock + skew metric 监控 |
| R26 | **🆕 僵尸指标持续积累**——废弃模块的 metric 永远占据存储和查询空间 | 低 | 低 | §4 僵尸指标扫描 + 30 天自动清理 + ZOMBIE 标记隐藏 |
| R27 | **🆕 Graceful Shutdown 时数据丢失**——未 flush 的 ring buffer 数据静默消失 | 中 | 中 | §3c shutdown() 设计 + emergency_shutdown.jsonl + 丢失检测 |
| R28 | **🆕 AI 自我修正零效能**——AI 声称的修正从未实际生效但无人发现 | 高 | 高 | §7.9 效能追踪 + 6 维度 SLI + AISelfCorrectionEvent 记录 |
| R29 | **🆕 Telemetry 自身性能退化**——flush/buffer 等操作逐渐变慢但无基准对比 | 低 | 中 | §15.7 性能基准 + P0-Blocker 级别目标 + CI benchmark |
| R30 | **🆕 指标名跨模块冲突**——不同模块注册同名指标导致 FQMN 歧义 | 高 | 高 | §3e FQMN 命名空间（module_id::metric_name）+ Schema Registry 唯一性校验 |
| R31 | **🆕 单次上报导致的锁竞争**——逐个上报在批量场景中 ring buffer lock 成为瓶颈 | 中 | 中 | §3f 批量上报 API（report_batch/log_batch/start_batch_spans） |
| R32 | **🆕 Telemetry 自身成为盲点**——Meta-Metrics 缺失，无法回答"Telemetry 在退化吗" | 高 | 中 | §10b Meta-Telemetry 12 维自体内省 + 独立 telemetry_meta 表 + AI 可消费 |

---

## 21. 后果（Consequences）

**正面后果**：
- 全系统可观测性——三层信号（4 Golden Signals + USE + Annotations）完整覆盖 + 多环境隔离
- AI 行为可审计——7 维度 AI 行为追踪 + 错误分类学 + 自我修正效能，每次操作有遥测记录 + 可分类错误 + 可追溯修正
- AI 自我修正——MCP 暴露遥测给 AI，形成反馈闭环；错误分类引导 AI 修正决策；效能仪表板验证闭环运作
- OTel 语义对齐——ai_behavior + traces 可直接被行业标准工具（Datadog/Honeycomb/Langfuse）消费
- 基础设施复用——基于 shared/logging + lifecycle + flags + observer + backpressure 构建，不重复造轮子
- 合成监控——6 种合成事务模拟真实工作流，在 1 人发现前检测系统故障
- 告警可测试——4 种告警测试模式 + Silent Alert 检测确保每条规则有效
- CI/CD 可观测——部署构建全链路可追踪，Post-Deployment Validation 自动验证
- SLI 结构化——SLI 定义注册表标准化每个指标的语义，AI 和告警规则可程序化消费
- 自描述遥测——Metric Discovery API 让 AI 无需蓝图即可自助发现指标
- 数据安全——OWASP MCP08 全对齐 + 加密 at rest + HMAC 防篡改 + 字段级脱敏 + 最小权限访问控制
- Observability-as-Code——所有 config YAML + Dashboard 与业务代码同仓版本化，CI/CD 部署
- Schema 版本化——兼容性矩阵 + alias 策略 + 蓝图版本漂移检测，历史数据持续可查
- 时钟可靠性——monotonic clock 测时长 + 偏差检测 + TraceParent 对齐，跨进程时序正确
- 容量规划有数据——基于实际数据而非估算
- 成本可控——按 model × task × module 的 $ 成本分解 + 遥测自身成本预算 + 三级降级
- FeatureFlag 全保护——所有采集行为可被开关控制
- 灾备可恢复——SQLite 每日备份 + archive replay 重建 + DLQ 修复重放
- 僵尸清理——自动扫描 + 隐藏 + 30 天清理，防止存储无限膨胀
- 优雅关闭——shutdown flush + emergency_shutdown.jsonl + 丢失检测
- 性能可验证——8 项性能基准（P0-Blocker/P1-ShouldFix/P2-NiceToHave）+ 集成测试覆盖
- 指标防冲突——FQMN 命名空间（MOD-INF-XXX::metric_name）防止多模块同名指标 + Schema Registry 唯一性校验
- 批量性能——report_batch/log_batch/start_batch_spans 批量 API，消除逐个上报的锁竞争 + 函数调用开销
- Meta-Telemetry——12 维自体内省指标 + 独立存储 + 3 类消费者（Watchdog/FLE/AI），完整"monitor the monitoring"

**负面后果**：
- 存储成本——9 子系统 + DLQ + 合成监控持续产出的遥测数据增长（三环境 × TTL）
- 施工复杂度——9 子系统施工阶段 P0-P2 共约 48h；安全/测试/效能/benchmark/命名空间/批量API/meta-telemetry ~18h
- 性能开销——采集、校验、采样、导出、DLQ 修复、HMAC 计算、加密、FQMN 解析、meta-metric 自采的 CPU 和 IO 开销（基准上限 ~10%）
- 指标维护成本——3 个 YAML SSoT（schema + sli + alert_rules）的持续同步维护 + 版本化管控
- MCP 接口维护——AI 可消费接口需要与 AI 能力演进同步更新 + Metric Discovery 接口
- shared 耦合风险——如果 shared 基础设施升级，Telemetry 需同步适配
- OTel 语义版本追踪——OTel GenAI/Agent conventions 仍在演进，需持续跟踪标准更新
- 合成监控 token 成本——synth.llm.health 每 5min 产生 LLM 调用费用（月 $0.50，可接受）
- 密钥管理——DB key + HMAC secret 必须通过环境变量/1Password 注入，加大了配置复杂度

---

## 22. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|------|
| 0.9.1 | 2026-05-06 | **P0-1 双真源修复——MOD-L12-001 全量吸收**。裁定：本蓝图(MOD-INF-015)为 L12 System Telemetry 唯一 CANONICAL SSoT。逐条对账 21 项内容(见下方对账清单)，原 MOD-L12-001 C轨占位蓝图(2026-05-05, 0.1.0, 34行)全量内容确认已融入——无一项遗漏。原占位文件 `l12_system_telemetry/blueprint.md` 已安全删除，其物理目录保留为命名空间标记(代码 `src/zephyr/l12_system_telemetry/` 存在)。tags 新增 `c-track-merged` / `DO-NOT-IMPLEMENT-superseded` / `single-source-of-truth` / `absorbed-mod-l12-001`。 |

### MOD-L12-001 → MOD-INF-015 逐条对账清单（21项，100%通过）

| # | C轨占位原内容 | 融入INF-015的位置/方式 | ✅ |
|:--:|------|------|:--:|
| 1 | module_id: MOD-L12-001 | §22 本变更记录 | ✅ |
| 2 | title: 系统遥测层蓝图(C轨) | §22 本变更记录 | ✅ |
| 3 | doc_type: blueprint | INF-015 frontmatter 相同 | ✅ |
| 4 | status: Draft | INF-015 frontmatter 相同 | ✅ |
| 5 | version: 0.1.0→0.9.0 | §22 本变更记录(演化链) | ✅ |
| 6 | layer: L01 | INF-015 frontmatter 相同 | ✅ |
| 7 | owner: ZephyrAlpha-Owner | INF-015 frontmatter 相同 | ✅ |
| 8 | classification: confidential | INF-015 frontmatter 相同 | ✅ |
| 9 | language: zh | INF-015 frontmatter 相同 | ✅ |
| 10 | created_by: human_plus_agent | INF-015 frontmatter 相同 | ✅ |
| 11 | date: 2026-05-05 | §22 本变更记录 | ✅ |
| 12 | valid_from: 2026-05-05 | §22 本变更记录 | ✅ |
| 13 | ttl: evolving→permanent | §22 本变更记录(演化) | ✅ |
| 14 | construction: blocked→phase_1_partial | §1/§13 施工进度已覆盖 | ✅ |
| 15 | ai_read_only_hint: DO_NOT_IMPLEMENT | tags: DO-NOT-IMPLEMENT-superseded(已废弃) | ✅ |
| 16 | summary: C轨占位说明 | frontmatter summary 已追加裁定声明 | ✅ |
| 17 | tags: c-track/do-not-implement/blocked | tags 已加入 c-track-merged + DO-NOT-IMPLEMENT-superseded + absorbed-mod-l12-001 | ✅ |
| 18 | priority: P1 | INF-015 frontmatter 相同 | ✅ |
| 19 | AI警告: 不得以此蓝图生成代码 | §1 已声明"AI 不得乱施工" + §15 施工指引已含AI约束 | ✅ |
| 20 | 子模块真源: l12-system-telemetry.yaml | §1 真源声明 + §17 产出物存放目录已引用 | ✅ |
| 21 | 概述: 后续按PS-STD模板扩展 | 已按PS-STD模板展开为§1-§22完整蓝图(2300行) | ✅ |
| 0.9.0 | 2026-05-06 | **第五轮盲点补全**（B78-B83，6 个新盲点，3 个落地为完整章节）——核心：指标命名空间防冲突（FQMN）、批量上报API、Meta-Telemetry自体内省。这是第五轮也是首次触及"AI代码生成实现细节层"的补全——前四轮覆盖了架构层和运营层，本轮解决AI独立生成多个模块时必然遇到的三个关键实现问题。①新增 §3e 指标命名空间与冲突预防（FQMN = module_id::metric_name 全限定名 + Schema Registry 唯一性校验 + MetricPoint 自动注入 + Discovery API 过滤）；②新增 §3f 批量上报 API（report_batch 批量 MetricPoint / log_batch 批量日志 / start_batch_spans 批量 Span + 施工约定）；③新增 §10b Meta-Telemetry / 自体内省（12 维 meta-metric + 独立 telemetry_meta 表 + 分级 TTL + 3 类消费者闭环）；④风险矩阵 29→32（+ 指标名冲突/锁竞争/Telemetry 自身盲点）；⑤§17 产出物新增 telemetry_meta.db；⑥§21 后果新增 3 条正面（指标防冲突/批量性能/Meta-Telemetry）+ 负面更新（施工 +3h / 性能开销新增项）；⑧frontmatter 摘要 + tags 扩展。施工工时总计 ~66h。 |
| 0.8.0 | 2026-05-06 | **第四轮盲点补全**（B56-B77，22 个新盲点，10 个落地为完整章节）——核心：数据安全与合规（OWASP MCP08:2025 全对齐 + 加密 + HMAC 防篡改）；Observability-as-Code（Grafana 12 Git Sync + CI/CD 集成）；Schema 版本化与兼容性矩阵（OTel Schema URL 对齐 + alias 策略）；时钟偏差检测（monotonic clock + skew metric）；AI 自我修正效能追踪（6 维度 SLI + AISelfCorrectionEvent）；Graceful Shutdown（ring buffer flush + emergency_shutdown.jsonl + 丢失检测）；僵尸指标清理（7 天 ZOMBIE 标记 + 30 天物理删除）；Telemetry 集成测试设计（9 场景 e2e + test mode 分层）；Telemetry 性能基准（8 项 + P0-Blocker/P1-ShouldFix/P2-NiceToHave 分级）。施工工时总计 ~63h。 |
| 0.7.0 | 2026-05-06 | **第三轮盲点补全**（B31-B55，25 个新盲点，11 个落地为完整章节）——核心：对标 OTel GenAI + AI Agent 语义约定；填补 Counter 重置/幂等性/DLQ 操作设计；跨进程 TraceContext 传播；合成监控 + 告警测试 + Silent Alert 检测；CI/CD Pipeline 可观测性；SLI 定义注册表（Google SRE 格式）；遥测成本预算 + 成本感知降级；自描述遥测 + Metric 发现 API。关联决策：本蓝图持续对标 Google SRE + OTel + Honeycomb + 氛围编程社区的演进。 |
| 0.4.0 | 2026-05-05 | 第一轮盲点补全（B1-B18）——五子系统→九子系统（+ profiles/health/alerts/schema）；信号层补齐 USE Method + Annotations；三层闭环架构；指标/日志/链路全面升级；AI 行为 7 维度；AI 可消费性设计（MCP + session 冷启动）；风险扩展 R1-R9。 |
| 0.3.0 | 2026-05-05 | 补全标准模板五项：§12 产出物存放目录 + §13 集成目标 + §14 需要更新的相关内容 + §15 已知风险与缓解 + §16 后果 |
| 0.2.0 | 2026-05-04 | P2-1 量化追踪落地——新增 BLUEPRINT-READ-FREQ / BLUEPRINT-STALENESS SLI + blueprint_metrics.py。关联决策：R92。 |
| 0.1.1 | 2026-05-03 | 施工进度扩展——§11 路径索引 + 施工指引 |
| 0.1.0 | 2026-05-03 | 初始创建——5子系统 skeleton + 4黄金信号 SLI |


---

## 施工落盘确认（2026-05-07 审计）
| 维度 | 状态 |
|------|------|
| construction_progress | phase_2_complete（Phase 1 Skeleton + Phase 2 E2E 均已通过） |
| 源码路径 | `src/zephyr/l12_system_telemetry/` |
| 源码文件数 | 12 个 .py/.yaml |
| 测试路径 | `tests/infrastructure/` |
| 关键入口 | `l12_system_telemetry.telemetry_core` |
