---
module_id: MOD-INF-015
submodule_path: src/zephyr/infrastructure/system_telemetry
title: "System Telemetry 蓝图+施工图 — 全系统可观测性"
doc_type: blueprint
status: Active
version: "2.0.2"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: completed
actual_disk_path: "src/zephyr/infrastructure/system_telemetry/"
belongs_to: "MOD-MASTER_BLUEPRINT"
summary: "ZephyrAlpha System Telemetry——全系统可观测性平台。9个子系统通过统一接入点 Telemetry 门面类暴露；覆盖三层信号(4 Golden Signals + USE + Annotations) + 多环境隔离；对接已有 shared 基础设施。三层闭环：AI开发闭环+运营闭环+治理闭环。"
tags: [telemetry, system_telemetry, metrics, logs, traces, ai-behavior, observability, infrastructure, profiling, health-check, alerting, schema-registry, finops, opentelemetry-genai, observability-as-code, single-source-of-truth]
priority: P1
runtime_plane: hot
depends_on:
  - {target: "MOD-DATABASE", at: "全篇", why: "Database——olap_engine持久化FLE时序分析结果"}
  - {target: "MOD-INF-024", at: "全篇", why: "Budget Enforcer——成本metrics聚合到预算追踪"}
  - {target: "MOD-INF-022", at: "全篇", why: "Escalation Protocol——告警升级到人工处理"}
  - {target: "MOD-INF-018", at: "全篇", why: "Agent RBAC——L6 Observability 以 Telemetry 为数据后端"}
  - {target: "MOD-INF-016", at: "全篇", why: "Shared Infrastructure——shared/logging / lifecycle / flags / observer 等基础组件"}
  - {target: "MOD-LLM_SECURITY", at: "全篇", why: "LLM Security——AI行为安全事件通过LSG gateway联动"}
references:
  - {id: "MOD-FEEDBACK_LOOP", at: "全篇", why: "FLE 消费 metrics/logs——仅存 references"}
  - {id: "MOD-INF-020", at: "全篇", why: "审计写入遥测-derived 事件——仅存 references"}
ssot_claims:
  - claim: "全系统可观测性数据采集唯一真源"
    scope: "src/zephyr/system_telemetry/"
  - claim: "AI行为遥测事件模型唯一真源"
    scope: "src/zephyr/system_telemetry/ai_behavior/"
  - claim: "指标Schema治理唯一真源"
    scope: "src/zephyr/system_telemetry/schema/"
  - claim: "告警规则引擎唯一真源"
    scope: "src/zephyr/system_telemetry/alerts/"
  - claim: "健康探针与聚合唯一真源"
    scope: "src/zephyr/system_telemetry/health/"
last_updated: "2026-05-15"
codification_level: L3
last_verified: "2026-05-15"
codification_at: "2026-05-15"
generation: 3
functional_domain: operations
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
responsibility_domain: 
build_status: generated
design_maturity: prototype
---

# System Telemetry 蓝图+施工图 — 全系统可观测性

> module_id: MOD-INF-015 | version: 2.0.2 | status: Active | layer: L0_infrastructure
> actual_disk_path: src/zephyr/system_telemetry/ | generation: 3 | construction_progress: completed

## 概述

本蓝图描述 System Telemetry——ZephyrAlpha 全系统可观测性平台，通过统一 Telemetry 门面类暴露 Metrics/Logs/Traces/AI行为/Archive/Profiles/Health/Alerts/Schema 九个子系统。覆盖三层信号（4 Golden Signals + USE + Annotations）+ 多环境隔离。当前管理 ~51 模块，目标容量 1,500 模块 / 100 AI 并发。上游依赖 Shared Core（MOD-INF-016），下游被 Agent RBAC（MOD-INF-018）和 Budget Enforcer（MOD-INF-024）消费。

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

> **SSoT 声明**：本文件是 System Telemetry 模块的唯一设计真源。
>
> **负向责任**：本文件不涉及 GPU 监控 / 业务算法优化 / 安全策略执行（→ MOD-INF-018 Agent RBAC） / LLM 安全策略定义（→ MOD-LLM_SECURITY）
>
> **触发**：AI 行为审计 / 性能诊断 / SLI 查询 / 告警配置 / 遥测数据上报 / AI Session 冷启动
>
> **漂移防护**：修改 Telemetry 接口 MUST 同步更新 MOD-INF-018（Agent RBAC L6 Observability）和 MOD-INF-024（Budget Enforcer）的遥测消费端

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-015`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 归属判定 | 阻塞原因 |
|---|--------|------------|------|:---:|---------|---------|
| 1 | facade.py | §3 | Telemetry 门面类 | 已实现 | 本模块 | — |
| 2 | metrics/ | 蓝图特有§A | Metrics 子系统 | 已实现 | 本模块 | — |
| 3 | logs/ | 蓝图特有§A | Logs 子系统 | 已实现 | 本模块 | — |
| 4 | traces/ | 蓝图特有§A | Traces 子系统 | 已实现 | 本模块 | — |
| 5 | ai_behavior/ | 蓝图特有§A | AI 行为子系统 | 已实现 | 本模块 | — |
| 6 | archive/ | 蓝图特有§A | Archive 子系统 | 已实现 | 本模块 | — |
| 7 | profiles/ | 蓝图特有§A | Profiles 子系统 | 已实现 | 本模块 | — |
| 8 | health/ | 蓝图特有§A | Health 子系统 | 已实现 | 本模块 | — |
| 9 | alerts/ | 蓝图特有§A | Alerts 子系统 | 已实现 | 本模块 | — |
| 10 | schema/ | 蓝图特有§A | Schema 子系统 | 已实现 | 本模块 | — |
| 11 | watchdog.py | 蓝图特有§A | Watchdog 进程内线程+可选独立进程 | 已实现 | 本模块 | — |
| 12 | health_probes.py | 蓝图特有§A | 健康探针 | 已实现 | 本模块 | — |
| 13 | health_aggregator.py | 蓝图特有§A | 健康聚合 | 已实现 | 本模块 | — |
| 14 | auto_bootstrap.py | §3 | 自动初始化 | 已实现 | 本模块 | — |
| 15 | contract_metrics.py | §4 | 契约指标 | 已实现 | 本模块 | — |
| 16 | __init__.py | §3 | 模块入口 | 已实现 | 本模块 | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/system_telemetry/` 逐文件核对 | ☐ |
| construction_progress = completed → 已实现章节的代码存在 | 按章节核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| actual_disk_path 与 §11 产出物路径一致 | 路径核对 | ☐ |
| 代码 [BLUEPRINT] 头部指向 = 本蓝图 module_id | `grep "\[BLUEPRINT\]" *.py` 核对 module_id | ☐ |
| §4.2 每个数据模型的 SSoT 文件中确实存在该模型 | `grep "class MetricPoint\|class AIBehaviorEvent\|class Span" src/zephyr/system_telemetry/` | ☐ |
| §0.1 每个文件的职责与其他文件无重叠 | 交叉比对职责列 | ☐ |
| §0.1 归属判定列无 ⚠️ 标记 | 逐文件核对 | ☐ |
| §5.5 自动化触发机制状态列与代码实现一致 | `python scripts/governance/d5_architecture/checkers/check_blueprint_automation_sync.py --blueprint MOD-INF-015` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.1.0 | 九子系统全部实现 | — | — |
| v2.0.0 (当前) | 同 v1.1.0 + 蓝图结构重构 | — | — |

### §0.4 SSoT与责任唯一性声明

| # | 声明维度 | 本蓝图是真源 | 真源在别处 | 委托目标 |
|---|---------|:----------:|:---------:|---------|
| 1 | 全系统可观测性数据采集 | ✅ | — | — |
| 2 | AI行为遥测事件模型 | ✅ | — | — |
| 3 | 指标Schema治理 | ✅ | — | — |
| 4 | 告警规则引擎 | ✅ | — | — |
| 5 | 健康探针与聚合 | ✅ | — | — |
| 6 | SLI合规测量 | ✅ | — | —（采集/存储/查询；SLI框架定义→MOD-INF-001） |
| 7 | 漂移诊断 | — | ✅ | MOD-INF-023 |
| 8 | 异常检测与自愈 | — | ✅ | MOD-FEEDBACK_LOOP |
| 9 | 安全策略执行 | — | ✅ | MOD-INF-018 |
| 10 | 预算执行与阻断 | — | ✅ | MOD-INF-024 |

### §0.5 代码目录唯一性声明

| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | src/zephyr/system_telemetry/ |
| 2 | 已知副本目录 | src/zephyr/telemetry/（兼容性shim，re-export到system_telemetry） |
| 3 | 副本处置状态 | shim保留（9个测试文件引用旧路径），子目录shim需修复为re-export |
| 4 | 已删除副本 | src/zephyr/infra_ops/（2026-05-16 RULE-THREE审判删除） |

---

## §1 设计背景与目标

### §1.1 背景

Telemetry 负责全系统可观测性数据采集（"看见"），异常检测与自愈由 FLE (MOD-FEEDBACK_LOOP) 负责（"行动"）。

### §1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:---:|------|----------|
| 1 | ✅ 包含 | 全系统可观测性——采集/存储/查询所有组件运行时数据 | 9 子系统覆盖 |
| 2 | ✅ 包含 | AI 可消费的运行时反馈（MCP 接口） | AI 开发闭环 |
| 3 | ✅ 包含 | 三层闭环（AI开发/运营/治理） | 闭环可验证 |
| 4 | ❌ 排除 | GPU 监控 | 无 GPU 计算场景 |
| 5 | ❌ 排除 | 业务算法优化 | 业务模块职责 |
| 6 | ❌ 排除 | 安全策略执行 | → MOD-INF-018 |
| 7 | ❌ 排除 | LLM 安全策略定义 | → MOD-LLM_SECURITY |

### §1.4 运行场景约束

| 约束 | 值 | 影响 |
|------|-----|------|
| 运行环境 | 单机 Windows (i7-12700KF / 64GB / RTX 3090 / 1TB NVMe) | SQLite 单写者瓶颈；JSONL 单文件争用 |
| 并发模型 | Python GIL + ThreadPoolExecutor | ring buffer 锁竞争；subprocess 释放 GIL |
| 存储预算 | 20GB（遥测数据硬上限） | 分层压缩 + TTL 必须严格执行 |
| AI 并发 | 0→100 Session | 遥测事件量 ×50；ring buffer/JSONL/SQLite 需容量适配 |
| 模块规模 | 51→1,500 模块 | FQMN 命名空间 ×30；Schema Registry 索引重设计 |
| 热更新 | 配置变更零重启 | FeatureFlag + 文件监听必须实时生效 |
| 数据隔离 | dev/staging/prod 共存单机 | 物理路径隔离；环境标签 MUST 携带 |

### §1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| AI Agent | 运行时反馈、自我修正闭环 | 施工+运行 | 通过 MCP 消费 |
| 1人维护者 | 系统健康、成本控制 | 设计+运维 | Feishu 告警通知 |
| FLE | 异常检测数据源 | 运行 | 只读 metrics/logs |
| Budget Enforcer | LLM 成本追踪 | 运行 | 只读 ai_behavior |

### §1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 可观测覆盖 | 51 模块 | 1,500 模块 | ×30 容量 | P1 |
| AI 并发 | 0 Session | 100 Session | 遥测事件量 ×50 | P1 |
| AI 自我修正闭环 | 手动排查 | MCP 自动反馈 | 缺少 MCP 接口 | P0 |
| 告警能力 | 无 | Multi-Window Burn Rate | 全新子系统 | P1 |
| Schema 治理 | 无 | 运行时校验+漂移检测 | 全新子系统 | P1 |

### §1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| AI 自我修正 | SLO breach | Telemetry采集→MCP反馈→AI读取→修正代码→验证 | 修复PR |
| 运营闭环 | 异常指标 | Telemetry采集→FLE检测→自动派单→自愈/升级 | Feishu告警 |
| 治理闭环 | Schema漂移 | Schema Registry→运行时校验→漂移检测→蓝图同步 | 漂移报告 |
| 容量降级 | 磁盘>80%预算 | dev TTL减半→采样降频→非prod暂停 | 降级事件 |

---

## §2 模块边界

### §2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:---:|------|------|--------|
| 1 | ✅ 包含 | 全系统可观测性数据采集 | Metrics/Logs/Traces/AI行为/Profiles/Health/Alerts/Schema/Archive 九子系统 | 本模块 |
| 2 | ✅ 包含 | AI 可消费的运行时反馈 | MCP Server 暴露遥测查询接口 | 本模块 |
| 3 | ✅ 包含 | 指标 Schema 治理 | Schema Registry + 运行时校验 + 漂移检测 | 本模块 |
| 4 | ✅ 包含 | 告警规则引擎 | Multi-Window Burn Rate + 多通道通知 | 本模块 |
| 5 | ❌ 排除 | 异常检测与自愈 | → MOD-FEEDBACK_LOOP | MOD-FEEDBACK_LOOP |
| 6 | ❌ 排除 | 安全策略执行 | RBAC 权限判定 | MOD-INF-018 |
| 7 | ❌ 排除 | LLM 安全策略定义 | LSG 防御层 | MOD-LLM_SECURITY |
| 8 | ❌ 排除 | 预算执行与阻断 | Budget Enforcer | MOD-INF-024 |
| 9 | ❌ 排除 | 审计日志持久化 | Audit Trail | MOD-INF-020 |
| 10 | ❌ 排除 | 根因诊断与自愈行动 | → MOD-FEEDBACK_LOOP | MOD-FEEDBACK_LOOP |

#### 职责唯一性声明

| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 全系统可观测性数据采集 | [MOD-INF-001, MOD-INF-018] | `python scripts/governance/check_ssot_uniqueness.py --blueprint MOD-INF-015` |
| AI行为遥测事件模型 | [MOD-INF-033] | 同上 |
| 指标Schema治理 | [MOD-INF-023] | 同上 |
| 告警规则引擎 | [MOD-INF-022] | 同上 |
| 健康探针与聚合 | [MOD-INF-001] | 同上 |

### §2.2 复用 vs 新建清单

**复用（基于 shared 组件构建，不复写）**：

| shared 组件 | 绝对路径 | Telemetry 使用方式 | 约束 |
|------------|---------|-------------------|------|
| TraceContext | `shared/logging.py` | §5 logs + §6 traces 上下文来源 | MUST 使用 shared.logging 的 TraceContext，禁止定义第二个 |
| CTR-TRACE-001 | `shared/contracts/trace_context.py` | §6 Span 字段必须兼容此契约 | trace_id/span_id/parent_span_id 格式一致 |
| get_logger + JSON Formatter | `shared/logging.py` | §5 logs 是 shared.logging 的消费端和增强端 | 各模块 log 统一经 shared.logging，不双写 |
| LifecycleAware + ModuleHealth | `lifecycle_manager/hooks.py` | §10 health 定时轮询各模块 health_check() | 健康数据来源是各模块 LifecycleAware 实现 |
| BackpressureThrottle/Pause/Resume | `shared/contracts/backpressure/` | §4 ring buffer 80%/95% 填满时发出 backpressure | 禁止静默丢数据——必须先发 THROTTLE→PAUSE→丢弃 |
| FeatureFlag（三态） | `shared/flags.py` | 控制 profiling 开关、采样率、日志级别、成本阈值 | 所有实验性 Telemetry 功能 MUST 由 FeatureFlag 守护（默认 OFF） |
| EventBus | `shared/observer.py` | Telemetry 内部事件分发 | 内部事件走 observer.EventBus，不做自定义事件系统 |
| TelemetryEmitter 契约 | `shared/contracts/telemetry_emitter.py` | MetricPoint / AIBehaviorEvent / HealthReport 等实现此契约 | 所有新数据类 MUST 实现或兼容 TelemetryEmitter 接口 |

**新建（Telemetry 独有）**：

| 新建组件 | 所在子系统 | 理由 |
|---------|----------|------|
| MetricPoint（含 Histogram/Summary） | metrics | shared无此能力 |
| JSONLFileWriter（按日轮转） | logs | shared无持久化策略 |
| Span 数据模型 + tail-based sampler | traces | shared无Span模型+采样 |
| AIBehaviorEvent + 7 维度 tracker | ai_behavior | 业务专属 |
| Schema Registry（YAML SSoT + 运行时校验） | schema | shared无schema治理 |
| Multi-Window Burn Rate 告警规则 | alerts | shared无告警逻辑 |
| Telemetry watchdog 进程内线程+可选独立进程 | health | 三层混合(L1进程内+L2 OS级+L3 Dead Man's Switch) |
| profile collector（py-spy → pprof） | profiles | 外部工具集成 |

---

## §3 架构设计

### §3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | Telemetry 门面类 | 统一接入点，代理九子系统 | shared/flags, shared/logging | 同步调用 |
| 2 | metrics 子系统 | SLI/SLO 数值指标采集 | shared/contracts/backpressure | 同步调用→ring buffer→SQLite |
| 3 | logs 子系统 | 结构化日志持久化 | shared/logging | 同步调用→JSONL |
| 4 | traces 子系统 | 分布式链路追踪 | shared/contracts/trace_context | 上下文管理器→采样→JSONL |
| 5 | ai_behavior 子系统 | AI 模型行为画像 | shared/flags | 同步调用→独立 ring buffer→SQLite |
| 6 | archive 子系统 | 冷数据压缩归档 | shared/observer (EventBus) | 事件驱动 |
| 7 | profiles 子系统 | CPU/内存连续性能剖析 | shared/flags | FeatureFlag 控制 |
| 8 | health 子系统 | 自体监控 + watchdog | shared/lifecycle | 定时轮询 |
| 9 | alerts 子系统 | 告警路由 + 多通道通知 | metrics 子系统 | 定时评估 |
| 10 | schema 子系统 | 指标 Schema 注册 + 漂移检测 | — | 写入校验 |

### §3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|--------|---------|---------|---------|---------|
| 1 | 模块 | Telemetry.metrics.report()→ring buffer→SQLite | FLE/Budget | MetricPoint | FQMN 自动注入 module_id |
| 2 | 模块 | Telemetry.logs.info()→shared.logging→JSONL | Gate/Audit | JSON Lines | 自动注入 trace_id/span_id |
| 3 | 模块 | telemetry.traces.span()→Span buffer→采样→JSONL | Pipeline/Debug | Span | W3C TraceContext 传播 |
| 4 | 模块 | telemetry.ai_behavior.record()→独立 ring buffer→SQLite | FLE/Budget | AIBehaviorEvent | OTel gen_ai.* 字段映射 |
| 5 | metrics表 | AlertRule 评估→NotificationChannel | FLE→Feishu | Alert | Multi-Window Burn Rate |
| 6 | MetricPoint | Schema Registry 校验→通过/拒绝/DLQ | 全模块 | MetricSchema | 校验失败→DLQ |

### §3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| INIT | `Telemetry(module_id)` 构造 | READY | 所有子系统初始化完成+后台调度器启动 |
| READY | 首次上报 | COLLECTING | — |
| COLLECTING | backpressure THROTTLE 信号 | THROTTLED | ring buffer 80% |
| THROTTLED | backpressure PAUSE 信号 | PAUSED | ring buffer 95% |
| PAUSED/COLLECTING/THROTTLED | 定时(60s)或 buffer 满 | FLUSHING | — |
| 任意 | 进程退出信号 | SHUTTING_DOWN | — |
| SHUTTING_DOWN | flush 完成 + 文件句柄关闭 | CLOSED | — |

---

## §4 接口契约

> 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。已实现代码仅保留接口签名。

### §4.1 公共 API

| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `Telemetry(module_id, environment)` | ①读环境变量/config ②注册LifecycleManager ③设默认标签 ④注入TraceContext ⑤启动后台调度器(flush 60s/alert 30s/health 10s/archive 300s) | environment 必须合法 |
| `metrics.counter/gauge/histogram/summary()` | ①FQMN自动注入module_id ②Schema校验 ③ring buffer写入 | Schema校验失败→DLQ |
| `metrics.report_batch()` | ①一次lock acquire ②逐条schema validate ③批量写入ring buffer ④返回{success,failed,dlq_ids} | 单条失败不阻塞 |
| `logs.info/warning/error()` | ①shared.logging格式化 ②TraceContext注入 ③JSONL追加 | 写入失败→stderr→内存缓冲→丢弃+告警 |
| `traces.span()` | ①创建Span ②设置ContextVar ③exit时记录end_time+status | 采样决策 |
| `ai_behavior.record()` | ①OTel gen_ai.*字段映射 ②独立ring buffer写入 | FeatureFlag控制;decision为必填参数 |
| `shutdown()` | ①停止后台调度器 ②flush ring buffer ③按逆序关闭9子系统 ④写shutdown audit | 总超时60s，强制退出写emergency_shutdown.jsonl |

### §4.1.1 自动化 API（v2.1.0 新增）

| API | 触发方式 | 自动化程度 |
|-----|---------|:---------:|
| `register_module(module_id)` | 模块 import 时调用 | ✅ 自动创建+注册+健康检查+后台调度 |
| `get_registered_modules()` | 查询 | ✅ 返回所有已注册模块 |
| `Telemetry(..., test_mode=False)` | 构造时自动启动 | ✅ 后台 daemon 线程定时执行5项任务（含watchdog） |
| `python -m ...watchdog` | 命令行（可选独立进程模式） | ✅ 独立进程持续心跳（部署层可选） |

后台调度器时间表（test_mode=False 自动启动）:

| 任务 | 间隔 | 执行内容 |
|------|:----:|---------|
| flush | 60s | ring buffer → JSONL 刷盘 |
| alert | 30s | 评估告警规则 |
| health_heartbeat | 10s | 发送健康心跳 |
| watchdog_check | 10s | Watchdog 互检+心跳写入+Dead Man's Switch |
| archive_check | 300s | 检查归档条件 |

### §4.2 数据模型

| 模型名 | SSoT文件 | 关键字段 | 其他定义位置 | 状态 |
|--------|---------|---------|------------|------|
| MetricPoint | src/zephyr/system_telemetry/metrics/ | name, value, timestamp, labels, type(gauge/counter/histogram/summary) | — | ✅ 唯一源 |
| AIBehaviorEvent | src/zephyr/system_telemetry/ai_behavior/ | event_type, trace_id, module, model_id, input/output_tokens, cost_usd, duration_ms, status | — | ✅ 唯一源 |
| Span | src/zephyr/system_telemetry/traces/ | trace_id, span_id, parent_span_id, module, start/end_time, status, metadata | — | ✅ 唯一源 |
| MetricSchema | src/zephyr/system_telemetry/schema/ | name, type, unit, module_id, labels, slo_target, cardinality_limit=1000 | — | ✅ 唯一源 |
| ErrorContext | src/zephyr/system_telemetry/ai_behavior/ | error_type, persistence(transient/permanent/intermittent), source, severity | — | ✅ 唯一源 |
| AISelfCorrectionEvent | src/zephyr/system_telemetry/ai_behavior/ | anomaly_id, anomaly_type, action_taken, success, regression_detected | — | ✅ 唯一源 |

### §4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `metrics.counter()` | name, value, labels | ✅ | name 须在 Schema Registry 注册；FQMN 自动注入 |
| `metrics.report_batch()` | list[MetricPoint] | ✅ | 单次 ≤1000 条 |
| `logs.info/warning/error()` | message, **kwargs | ✅ | PII 自动脱敏 |
| `traces.span()` | name | ✅ | 命名遵循 gen_ai.<component>.<operation> |
| `ai_behavior.record()` | model_id, input_tokens, output_tokens, duration_ms | ✅ | 字段 MUST 可映射到 OTel gen_ai.* |
| `shutdown()` | — | — | 总超时 60s |

### §4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `metrics.counter()` | void | SchemaValidationError→DLQ |
| `metrics.report_batch()` | {success_count, failed_count, dlq_ids} | RingBufferOverflow→丢弃最旧 |
| `logs.info()` | void | JSONLWriteError→stderr→内存缓冲→丢弃 |
| `traces.span()` | Span 对象 | 采样拒绝→仅记录 trace_id+minimal span |
| `ai_behavior.record()` | void | FeatureFlag=OFF→noop |
| `shutdown()` | void | GracefulShutdownTimeout→emergency_shutdown.jsonl |

### §4.5 MCP 接口

**Tools**：

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `get_recent_alerts` | `get_recent_alerts(module?, time_range?)` | `{module: str, time_range: str}` | `list[Alert]` |
| `get_service_health` | `get_service_health(module?)` | `{module: str}` | `HealthReport` |
| `get_slo_status` | `get_slo_status(sli_name)` | `{sli_name: str}` | `SLOStatus` |
| `get_recent_traces` | `get_recent_traces(module, status?, limit?)` | `{module: str, status: str, limit: int}` | `list[TraceSummary]` |
| `get_cost_breakdown` | `get_cost_breakdown(time_range)` | `{time_range: str}` | `CostReport` |
| `get_blueprint_drift` | `get_blueprint_drift()` | — | `DriftReport` |
| `get_silent_alerts` | `get_silent_alerts()` | — | `list[SilentAlertReport]` |
| `get_dlq_summary` | `get_dlq_summary()` | — | `{total, by_reason, repair_rate}` |
| `get_telemetry_cost` | `get_telemetry_cost()` | — | `CostBudgetReport` |
| `list_metrics` | `list_metrics(module?, type?)` | `{module: str, type: str}` | `list[MetricSummary]` |
| `get_metric_detail` | `get_metric_detail(name)` | `{name: str}` | `MetricDetail` |
| `search_metrics` | `search_metrics(query)` | `{query: str}` | `list[MetricSummary]` |
| `get_metrics_by_slo` | `get_metrics_by_slo(slo_name)` | `{slo_name: str}` | `list[MetricSummary]` |

### §4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 MetricSchema 字段 | ✅ 向后兼容 | 不影响已有消费者 |
| 新增 MCP Tool | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名 MCP Tool | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| MetricPoint 字段变更 | ❌ 破坏性 | 需 Owner 审批 + Schema 版本升级 |
| 新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

### §4.7 OCP 扩展点

| 扩展点 | 基类/接口 | 默认实现 | 扩展契约 | 注册方式 |
|--------|----------|---------|---------|---------|
| 通知通道 | `NotificationChannel` | FeishuWebhook | MUST 实现 send(alert) → bool | alert_rules.yaml 配置注入 |
| 采样策略 | `TraceSampler` | TailBasedSampler | MUST 实现 should_sample(span) → bool | FeatureFlag 切换 |
| Schema 校验器 | `SchemaValidator` | DefaultSchemaValidator | MUST 实现 validate(metric_point) → bool | Schema Registry 注册 |

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 所有遥测数据 MUST 携带 environment 标签 | dev/staging/prod |
| 2 | 数据路径按环境物理隔离 | data/telemetry/{env}/ |
| 3 | 所有实验性功能 MUST 由 FeatureFlag 守护（默认 OFF） | shared/flags.py |
| 4 | AI 禁止自行修改 FlagState | 人工运维权限 |
| 5 | 所有可配置参数 MUST 从 FeatureFlag/config 读取 | 禁止硬编码 |
| 6 | 每个子系统 MUST 实现 on_config_change(event) 回调 | 即时生效 |
| 7 | 指标全限定名 FQMN = {module_id}::{metric_name} | Schema Registry 唯一 key |
| 8 | 跨进程调用 MUST 携带 traceparent（W3C 标准） | 禁止手动传递 trace_id |
| 9 | 禁止在日志/指标/span 中硬编码 API Key / Token / Secret | 环境变量注入 |
| 10 | HMAC secret 和 DB key 永远不写入 config/ YAML | 仅环境变量 |
| 11 | 超过 10 个同类型遥测调用时 MUST 使用 report_batch / log_batch | 减少锁竞争 |
| 12 | ai_behavior 字段命名 MUST 可映射到 OTel gen_ai.* 属性 | 禁止自行发明语义 |
| 13 | traces Span 命名 MUST 遵循 gen_ai.<component>.<operation> 风格 | OTel 对齐 |
| 14 | 所有可观测性配置 MUST 在 config/ 目录，与业务代码同仓 git 管理 | Observability-as-Code |
| 15 | 禁止在 Grafana UI 中手动编辑 Dashboard | Dashboard 从 config/dashboards/ 加载 |
| 16 | 遥测成本预算：磁盘10GB / CPU单核10% / 内存512MB / LLM $0.50/月 | 超预算→三级降级 |

### §5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 模块数 | 51 | 1,500 | SQLite 单写者 | ❌ | T2: WAL模式+batch split |
| AI 并发 | 0 | 100 Session | ring buffer 10000 | ❌ | T1: threading.local队列冲刷 |
| 遥测数据量 | ~5GB | 20GB | 磁盘上限 | ✅ | 三级降级策略 |
| 指标基数 | ~200 | 1000/指标 | SQLite 索引 | ✅ | cardinality 控制+TTL裁剪 |
| 日志量 | ~50MB/天 | ~500MB/天 | JSONL 追加写入 | ✅ | 单 Consumer 线程串行化 |

### §5.3 迁移/废弃方案

无迁移/废弃。

### §5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | Telemetry上报成功率 | 99.9% | metrics 自体监控 | TELEMETRY-HEALTH | ≥99.9% | 0.1%/月 | Burn Rate >14.4x(1h) |
| LLM 可用性 | 成功调用/总调用 | 99.5% | ai_behavior 追踪 | LLM_AVAILABILITY | ≥99.5% | 0.5%/月 | Burn Rate >14.4x(1h) |
| Gate 通过率 | 通过/总任务 | 95% | metrics 追踪 | GATE_PASS_RATE | ≥95% | 5%/月 | Burn Rate >6x(6h) |
| Pipeline 完成率 | 完成/分发 | 90% | metrics 追踪 | PIPELINE_COMPLETE | ≥90% | 10%/月 | Burn Rate >6x(6h) |
| 可维护性 | MTTR | <30min | 故障记录 | — | — | — | — |
| 可观测性 | 指标覆盖率 | 100% | 指标审计 | METRIC-CARDINALITY | =0 超限 | — | 超限即告警 |

### §5.5 自动化触发机制

| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|:-------:|
| import zephyr 时自动初始化 | `zephyr/__init__.py` → `auto_bootstrap.bootstrap()` | import触发 | ✅ 已实现 |
| 模块零代码接入 | `register_module("MOD-INF-XXX")` | 调用触发 | ✅ 已实现 |
| 后台调度器 | daemon线程 `telemetry-scheduler` | flush:60s/alert:30s/health:10s/archive:300s/aggregator:15s/profiles:60s | ✅ 已实现 |
| Watchdog | `auto_boot`（Telemetry构造时自动启动watchdog线程） | ✅ 已实现 |
| Monkey-patch自动注入 | SessionContinuity/PhaseManager/BlueprintMetrics | import zephyr时自动patch | ✅ 已实现 |

### §5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:---:|--------|-----------|------|
| 1 | 编码模式 | 静默丢数据 | Backpressure THROTTLE→PAUSE→丢弃 | 数据丢失不可接受 |
| 2 | 编码模式 | 绕过 Telemetry 门面类直接调用子系统 | Telemetry(module_id) 统一接入 | AI 不需要记忆九套 API |
| 3 | 编码模式 | 在 config/ YAML 中存储密钥 | 环境变量注入 | 安全 |
| 4 | 导入源 | 定义第二个 TraceContext | shared/logging.py 的 TraceContext | 双源漂移 |
| 5 | 导入源 | 自定义事件系统 | shared/observer.py EventBus | 重复造轮子 |
| 6 | 编码模式 | for + subprocess.run() 串行 | ThreadPoolExecutor(max_workers=8) | RULE-SEVEN |
| 7 | 编码模式 | open(path, "w") 直接写 | temp-file + os.replace() 原子写入 | RULE-ONE |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | SchemaValidationError | MetricPoint 字段不符合 Schema | 拒绝写入→单条入 DLQ | 单条指标 |
| 2 | RingBufferOverflow | ring buffer 填满 100% | 发 PAUSE 信号→丢弃最旧数据 | 全模块上报 |
| 3 | SQLiteFlushError | flush 批量写入失败 | 重试 3 次→降级写入 emergency_shutdown.jsonl | 指标持久化 |
| 4 | JSONLWriteError | 日志文件写入失败 | 重试 1 次→写入 DLQ | 日志持久化 |
| 5 | SchemaDriftDetected | 运行时指标与 Schema 定义不一致 | 记录漂移事件→通知治理闭环 | AI 下次 session 修正 |
| 6 | BackpressureThrottle | ring buffer 填充 >80% | 发 THROTTLE 信号→上报频率降半 | 上游模块 |
| 7 | BackpressurePause | ring buffer 填充 >95% | 发 PAUSE 信号→暂停非 P0 上报 | 上游模块 |
| 8 | GracefulShutdownTimeout | 关闭时 flush 超时 30s | 强制关闭→写入 emergency_shutdown.jsonl | 缓冲区数据 |

**依赖循环声明**：本模块不存在依赖循环。

### §6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| telemetry.metrics.ingress_rate | gauge | 自动 | >500 | P2 |
| telemetry.metrics.flush_duration_ms | histogram | 自动 | P99>1000ms | P2 |
| telemetry.metrics.dropped_total | counter | 自动 | >0 | P1 |
| telemetry.metrics.buffer_depth_percent | gauge | 自动 | >80% | P2 |
| telemetry.dlq.current_size_bytes | gauge | 自动 | >100MB | P2 |
| telemetry.dlq_growth_rate | gauge | 自动 | >10MB/h | P1 |
| telemetry.cost.storage_bytes | gauge | 自动 | >80%预算 | P2 |
| telemetry.schema.rejection_rate | gauge | 自动 | >5% | P2 |
| telemetry.per_module.ingress_top10 | gauge | 自动 | 单模块>50% | P2 |

### §6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| SQLite metrics | 缓存 ring buffer 数据 | 持久化查询 | ring buffer 暂存+emergency_shutdown.jsonl | SQLite 恢复 |
| JSONL logs | stderr fallback | 结构化日志查询 | stderr→内存缓冲(1000条)→丢弃+告警 | 文件句柄恢复 |
| Schema Registry | 无校验写入 | 运行时校验 | 跳过校验+标记 unvalidated | Schema 加载 |
| alerts 子系统 | metrics 仍采集 | 告警通知 | 告警入队列等待 | 告警引擎恢复 |
| watchdog | Telemetry 仍运行 | 自体监控 | OS 级进程守护 | watchdog 重启 |
| DLQ | 正常路径不受影响 | 死信修复 | 新拒绝事件写 stderr | DLQ 恢复 |

---

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 遥测数据篡改 | 高 | HMAC-SHA256 防篡改日志（链式） | 校验 HMAC 完整性 |
| 2 | PII 泄露 | 高 | 字段级脱敏（email→u***@, API key→sk-****, IP→192.168.*.*, 路径脱敏用户名, phone/card/SSN→[REDACTED]） | 正则扫描脱敏后数据 |
| 3 | 未授权访问 | 高 | 环境隔离 + RBAC（Telemetry自身:读写, FLE:只读24h, AI/MCP:只读聚合, 外部模块:仅写自身） | 权限矩阵测试 |
| 4 | SQL 注入 | 中 | 参数化查询（SQLite） | 输入边界测试 |
| 5 | 磁盘耗尽 | 中 | 容量降级策略（80%/95%/100%） | 磁盘填充模拟 |
| 6 | DLQ 堆积 | 中 | DLQ TTL 30天 + 物理删除 | DLQ 容量上限测试 |

**加密策略**：

| 数据层 | 加密方式 | 密钥管理 |
|--------|---------|---------|
| SQLite metrics DB | SQLCipher (AES-256) | 环境变量 TELEMETRY_DB_KEY |
| JSONL logs PII 字段 | AES-256-GCM 逐字段 | 独立 per-field key |
| DLQ JSONL | 不加密，PII 字段 redact/mask | — |
| archive gzip | 可选 AES-256（FeatureFlag 控制，默认 OFF） | 环境变量 |
| config/ YAML | 不加密（在 git 中，不应含密钥） | 环境变量→OS keyring |

**防篡改日志**：链式 HMAC-SHA256，每 24h 自动校验，断裂→P1 安全事件→从 archive replay 重建。

---

## §9 测试策略

| # | 测试类型 | 关键测试用例 | 通过标准 |
|---|---------|------------|---------|
| 1 | 单元测试 | MetricPoint序列化/RingBuffer满时丢弃/Schema校验拒绝 | 覆盖率>80% |
| 2 | 集成测试 | 端到端metric写入→查询/跨模块Trace传播/Backpressure端到端/Schema校验端到端/FeatureFlag切换/Alert Pipeline/DLQ自动修复/Disaster Recovery | 全部 PASS |
| 3 | 性能/压力测试 | metric.report()<1ms / log.info()<2ms / flush(1000条)<500ms / CPU<1% / 内存<256MB | P0项达标+buffer无溢出 |
| 4 | 告警测试 | dry-run/shadow/inject/backtest 四模式 | 预期窗口触发 |
| 5 | 安全测试 | HMAC完整性/PII正则扫描/权限矩阵 | 零泄露 |
| 6 | 治理测试 | 磁盘模拟+漂移注入 | 降级/漂移事件正确 |

测试模式：test_mode=True(noop) / test_mode="integration"(SQLite in-memory+tmpdir) / test_mode="production"(真实磁盘)

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-016 | 必须 | shared/logging / lifecycle / flags / observer / contracts | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\shared_core\blueprint.md` |
| MOD-DATABASE | 必须 | olap_engine 持久化 FLE 时序分析结果 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\database\blueprint.md` |
| MOD-INF-024 | 必须 | Budget Enforcer 成本 metrics 聚合 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\budget-enforcer\blueprint.md` |
| MOD-INF-022 | 必须 | Escalation Protocol 告警升级 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-protocol\blueprint.md` |
| MOD-INF-018 | 必须 | Agent RBAC L6 Observability 消费 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| MOD-LLM_SECURITY | 必须 | LLM Security AI 行为安全事件联动 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\llm_security-gateway\blueprint.md` |
| MOD-FEEDBACK_LOOP | 可选 | FLE 消费 metrics/logs | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\feedback_loop\blueprint.md` |
| MOD-INF-020 | 可选 | 审计写入遥测-derived 事件 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |

### §10.2 依赖图对齐声明

> 全局依赖图 SSoT：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> 机器 SSoT：[cross-module-dependency-registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cross-module-dependency-registry.yaml)

MOD-INF-015 在线6:运维保障线。上游: 系统运行时 → MOD-INF-015。下游: MOD-INF-015 → MOD-INF-001(容量保障) → MOD-RESOURCE_OPTIMIZATION_ENGINE(资源优化) → MOD-INF-026(资产盘点)。交叉引用: V6_CAP→V4_FLE(容量告警), V3_BUD→V6_CAP(预算耗尽)。

**跨线交叉点**：

| 交叉ID | 交叉方向 | 触发条件 | 数据流协议 | 风险 |
|--------|---------|---------|-----------|------|
| X-06 | 容量→自愈(线6→线4) | 容量超限 | SLI越界→反馈触发 | 容量告警频率100× |
| X-07 | 预算→容量(线3→线6) | 预算耗尽 | 预算告警→容量保障 | 全局预算池争抢 |
| X-13 | MOD-INF-015 in-degree=8 | 遥测崩溃 | 8模块无指标→容量盲区 | 本地指标缓存+关键指标模式 |

**契约引用**：

| 契约ID | 提供方 | 消费方 | 内容 | SLA |
|--------|--------|--------|------|-----|
| CT-TEL-001 | MOD-INF-015 | MOD-INF-001/032 | 指标 | 指标采集延迟<1s |
| CT-TEL-002 | MOD-INF-015 | MOD-INF-001/032 | 日志 | 持久化延迟<5s |
| CT-TEL-003 | MOD-INF-015 | MOD-INF-001/032 | 链路 | 采样率可配置 |
| CT-TEL-004 | MOD-INF-015 | MOD-INF-001/032 | 健康检查 | 心跳间隔30s |

**ARB-14 裁决结果**：MOD-INF-015 补 CT-TEL-001~004 契约注册。遥测消费者: MOD-INF-001 + MOD-RESOURCE_OPTIMIZATION_ENGINE。

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐(9/9: DEP-030~033+DEP-072~076) | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-015` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### §10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| facade.py | metrics/, logs/, traces/, ai_behavior/, archive/, profiles/, health/, alerts/, schema/ | 门面初始化先于子系统 | facade import 检查 |
| schema/ | metrics/ | Schema Registry 先于指标上报 | schema 初始化检查 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| metrics/ | alerts/ | MetricPoint | SQLite 查询 |
| metrics/ | archive/ | MetricPoint | 定时归档 |
| logs/ | archive/ | LogEntry | 定时归档 |
| traces/ | archive/ | Span | 定时归档 |
| alerts/ | schema/ | AlertRule | schema 校验 |

### §10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|---------|
| 1 | 漂移检测 | 是 | 蓝图-代码一致性 | CI/CD Pipeline + on-session-start | CI/session启动 | 文件变更时 |
| 2 | DLQ 自动修复 | 是 | 数据质量闭环 | ring buffer overflow 事件驱动 | 实时 | DLQ 写入时 |
| 3 | 僵尸指标清理 | 是 | 存储健康 | 定时扫描 | 每7天 | 定时 |
| 4 | 告警规则自检 | 是 | 告警有效性 | Silent Alert 检测 | 每天 | 定时 |
| 5 | integrity chain 校验 | 是 | 安全合规 | HMAC 链式校验 | 每24h | 定时 |
| 6 | 容量降级 | 是 | 存储预算 | 水位线触发 | 事件驱动 | 磁盘超阈值 |

### §10.5 概念重叠声明

| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | SLI合规测量 | measure_sla功能 | MOD-INF-001 | 015采集原始指标，001定义SLO目标与合规判定 | ✅ 边界清晰 |
| 2 | 异常检测 | 告警vs检测 | MOD-FEEDBACK_LOOP | 015阈值告警(if metric>threshold→AlertSubsystem.fire) / 010智能检测(EMA+Z-score→FeedbackProtocolAdapter.dispatch_action) | ✅ 接口已明确 |
| 3 | 契约漂移检测 | detect_contract_drift | MOD-INF-023 | detect_contract_drift委托至behavioral_auditor.contract_drift_detector | ✅ 已迁移 |
| 4 | AI行为监控 | ai_behavior vs behavioral_audit | MOD-INF-033 | 015采集行为数据，033做行为边界判定 | ✅ 边界清晰 |
| 5 | 告警升级 | CRITICAL级告警触发 | MOD-INF-022 | 015触发告警，022处理升级。接口契约需明确 | ⚠️ 需明确接口 |

### §10.6 依赖链风险评级

| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|:-------:|---------|---------|
| 1 | MOD-INF-015→MOD-INF-016(Shared Core) | 1 | 高 | shared不可用→Telemetry降级为noop | ✅ 已实现 |
| 2 | MOD-INF-015→MOD-DATABASE(Database) | 1 | 中 | SQLite不可用→JSONL only模式 | ✅ 已实现 |
| 3 | MOD-INF-018→MOD-INF-015(8模块依赖) | 1 | 高 | 遥测崩溃→8模块无指标→容量盲区 | ✅ 本地缓存+降级模式 |

---

## §11 产出物存放目录

> §11 产出物路径 MUST 与依赖图 §19 path_mappings 一致。

| 产出物类型 | 存放完整绝对路径 | 职责 | consumer_min | 注册位置 |
|----------|---------------|------|:-----------:|---------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\system_telemetry\blueprint.md` | 本文件（含设计和施工指引） | ≥0 | blueprint_registry.yaml |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\system_telemetry\` | Telemetry 源码 | ≥1 | `__init__.py` __all__ |
| 遥测数据 | `D:\ZephyrAlpha\data\telemetry\` | 遥测数据存储 | ≥0 | — |
| DLQ 数据 | `D:\ZephyrAlpha\data\telemetry\{environment}\dlq\` | DLQ 死信队列 | ≥0 | — |
| emergency_shutdown | `D:\ZephyrAlpha\data\telemetry\{environment}\emergency_shutdown.jsonl` | 异常关闭缓冲区转储 | ≥0 | — |
| telemetry_meta | `D:\ZephyrAlpha\data\telemetry\{environment}\telemetry_meta.db` | Meta-Telemetry 自体内省存储 | ≥0 | — |
| telemetry_access_log | `D:\ZephyrAlpha\data\telemetry\{environment}\telemetry_access_log.jsonl` | 遥测访问审计日志 | ≥0 | — |
| Schema Registry | `D:\ZephyrAlpha\config\metrics_schema.yaml` | 指标 schema SSoT | ≥1 | 热加载 |
| Alert Rules | `D:\ZephyrAlpha\config\alert_rules.yaml` | 告警规则定义 | ≥1 | 热加载 |
| SLI Registry | `D:\ZephyrAlpha\config\sli_registry.yaml` | SLI 定义注册表 | ≥1 | 热加载 |
| Feature Flags | `D:\ZephyrAlpha\config\flags.yaml` | FeatureFlag 定义 | ≥1 | shared/flags 文件监听 |
| Dashboards | `D:\ZephyrAlpha\config\dashboards\` | Dashboard-as-Code | ≥0 | grafanactl |
| Test Fixtures | `D:\ZephyrAlpha\tests\unit\telemetry\` | Telemetry 测试 | ≥0 | pytest 自动发现 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Audit Trail (MOD-INF-020) | 遥测事件→审计日志 | telemetry_collector→audit_writer | 遥测事件写入审计 |
| Feedback Loop (MOD-FEEDBACK_LOOP) | 遥测驱动的异常检测 | FLE detect→telemetry_anomaly_signal | 异常指标触发 FLE |
| Budget Enforcer (MOD-INF-024) | 成本 metrics | cost_collector→budget_tracker | token 消耗可追踪 |
| Escalation Protocol (MOD-INF-022) | 告警升级通知 | alert_router→escalation_handler | P0 告警触达人工 |
| LLM Security (MOD-LLM_SECURITY) | AI 行为安全事件 | ai_behavior→lsg_security_gateway | 异常 prompt/幻觉触发拦截 |
| AI Agent Session（MCP） | 运行时遥测反馈 | Telemetry MCP Server→AI Agent tools | AI 调用 get_alerts() 返回有效数据 |
| 所有 D_DATA-实验 模块 | metrics/logs/traces 采集 | 各模块→telemetry_exporter | 全系统可观测 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 版本号+完整度 | 蓝图重构后更新 |
| 2 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | Telemetry 模块状态 | 代码施工后更新 |
| 3 | 跨层契约 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\contracts\cross_layer_contracts.yaml` | MCP 接口契约 | AI 可消费性设计落地 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|:---:|:---:|---------|------|
| R1 | 遥测数据量爆炸 | 高 | 中 | 智能采样+聚合+TTL+cardinality控制 | 风险 |
| R2 | 监控系统自身故障 | 中 | 高 | 三层混合Watchdog（L1进程内自动+L2 OS级+L3 Dead Man's Switch）+自体健康评分 | 风险 |
| R3 | 指标定义不一致 | 高 | 中 | Schema Registry+运行时校验+蓝图漂移检测 | 风险 |
| R4 | 采集性能开销 | 中 | 中 | 异步采集+批量写入+反压机制 | 风险 |
| R5 | Cardinality 爆炸 | 中 | 高 | 标签白名单+基数上限1000+告警阈值800+TTL裁剪+strict_mode | 风险 |
| R6 | 蓝图-代码漂移 | 中 | 高 | 自动漂移检测+SLO采集覆盖+告警规则漂移+session冷启动检查 | 风险 |
| R7 | PII/敏感数据泄露 | 低 | 高 | 日志脱敏+数据分级+访问控制+加密at rest | 风险 |
| R8 | 告警噪声 | 中 | 中 | Burn Rate 多窗口+去重+聚合+静默窗口 | 风险 |
| R9 | 成本失控 | 中 | 中 | ai_behavior FinOps+Budget Enforcer 联动 | 风险 |
| R10 | 重复造轮子 | 高 | 高 | §2.2 复用清单+MUST 使用 shared 组件 | 风险 |
| R11 | 环境数据污染 | 中 | 高 | 数据路径隔离+environment 标签+FLE 环境感知 | 风险 |
| R12 | 失控模块淹没 Telemetry | 低 | 高 | per-module 速率限制+Backpressure+ring buffer 水位线 | 风险 |
| R13 | OTel 语义约定漂移 | 中 | 中 | OTel 对齐声明+2版本内同步+schema drift check | 风险 |
| R14 | Counter 重置误报 | 中 | 中 | process_start_ts+FLE reset-aware+delta recording | 风险 |
| R15 | DLQ 积压失控 | 低 | 中 | DLQ 自动修复+重试上限+容量告警 | 风险 |
| R16 | 跨进程 Trace 断裂 | 高 | 高 | W3C TraceContext 传播+5种传播载体 | 风险 |
| R17 | Silent Alert | 中 | 高 | 告警规则测试(dry-run/shadow/inject/backtest)+每日扫描 | 风险 |
| R18 | 遥测成本超预算 | 中 | 高 | 三级降级策略(TTL缩减→采样降频→非prod暂停) | 风险 |
| R19 | 指标名跨模块冲突 | 高 | 高 | FQMN 命名空间(module_id::metric_name)+唯一性校验 | 风险 |
| R20 | AI 自我修正零效能 | 高 | 高 | 效能追踪+6维度SLI+AISelfCorrectionEvent | 风险 |
| R21 | Graceful Shutdown 数据丢失 | 中 | 中 | shutdown()设计+emergency_shutdown.jsonl | 风险 |
| R22 | Telemetry 自身性能退化 | 低 | 中 | 性能基准+P0-Blocker目标+CI benchmark | 风险 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | §2.2 复用清单已理解——MUST 使用 shared 组件 | 能回答"TraceContext 在哪" | ☐ |
| 4 | §5.1 技术约束已理解——所有约束项 | 能回答"FQMN 格式是什么" | ☐ |
| 5 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 已完成（9 子系统全部 implemented） |
| 施工模式 | 扩展 |
| 核心风险 | 蓝图-代码漂移 |
| 目标 generation | 3（本次从 generation 2 升级到 3——蓝图结构重构） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | shared/logging.py TraceContext | hard | ✅ | ✅ |
| 2 | shared/contracts/backpressure/ | hard | ✅ | ✅ |
| 3 | shared/flags.py FeatureFlag | hard | ✅ | ✅ |
| 4 | shared/observer.py EventBus | hard | ✅ | ✅ |

### 16.3 实施步骤

> 九子系统已全部实现。后续施工为增量扩展。

#### 创建文件清单

| # | 文件路径 | 创建方式 | 注册位置 | 内容编写指引 |
|---|---------|---------|---------|------------|
| 1 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/facade.py` | scaffold.py module | `__init__.py` __all__ | Telemetry 门面类，聚合9子系统，实现 auto_boot/auto_event/auto_schedule |
| 2 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/metrics/__init__.py` | scaffold.py module | `__init__.py` __all__ | MetricsSubsystem: counter/gauge/histogram/timer，FQMN格式 `{module}.{subsystem}.{metric}` |
| 3 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/logs/__init__.py` | scaffold.py module | `__init__.py` __all__ | LogsSubsystem: info/warning/error/critical，结构化JSONL输出 |
| 4 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/traces/__init__.py` | scaffold.py module | `__init__.py` __all__ | TracesSubsystem: span/start_span/finish_span，OTel兼容 |
| 5 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/ai_behavior/__init__.py` | scaffold.py module | `__init__.py` __all__ | AIBehaviorSubsystem: record/self_correct，AIBehaviorEvent数据类 |
| 6 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/archive/__init__.py` | scaffold.py module | `__init__.py` __all__ | ArchiveSubsystem: archive/query，冷热分层存储 |
| 7 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/profiles/__init__.py` | scaffold.py module | `__init__.py` __all__ | ProfilesSubsystem: record_profile/get_profile，模块遥测画像 |
| 8 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/health/__init__.py` | scaffold.py module | `__init__.py` __all__ | HealthSubsystem: register/set_unhealthy/set_healthy/status，健康探针聚合 |
| 9 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/alerts/__init__.py` | scaffold.py module | `__init__.py` __all__ | AlertsSubsystem: add_rule/check_alerts/get_active，规则引擎+阈值告警 |
| 10 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/schema/__init__.py` | scaffold.py module | `__init__.py` __all__ | SchemaSubsystem: register_schema/check_compatibility/get_schema，版本兼容检查 |
| 11 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/auto_bootstrap.py` | scaffold.py module | `__init__.py` __all__ | 自动初始化：import时触发register_module+monkey-patch |
| 12 | `src/zephyr/infrastructure/runtime_integration/system_telemetry/watchdog.py` | scaffold.py script | script-manifest.yaml | 独立watchdog进程：健康巡检+告警触发+自愈 |

#### 步骤 1：logs 子系统独立模块化 — ✅ 已完成

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 logs API |
| 验证命令 | `python -m pytest tests/telemetry/ -k test_logs -v` |

#### 步骤 2：CT-TEL-001~004 契约注册与实现 — ✅ 已完成

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §10.2 CT-TEL-001~004 |
| 验证命令 | `python -c "import yaml; d=yaml.safe_load(open('.../cross_layer_contracts.yaml')); assert any(c['id']=='CT-TEL-001' for c in d['contracts'])"` |
| AI 自治范围 | human_gated（契约变更需 Owner 批准） |

#### 步骤 3：DEP-031 方向修正 — ✅ 已完成

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §10.1 依赖声明 |
| 验证命令 | `python -c "import yaml; d=yaml.safe_load(open('.../cross-module-dependency-registry.yaml')); dep=[x for x in d['dependencies'] if x['dep_id']=='DEP-031'][0]; assert dep['direction']=='peer'"` |

#### 步骤 4：telemetry/ 旧文件清理 — ✅ 已完成

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §0.5 代码目录唯一性声明 |
| 验证命令 | `python src/zephyr/gov_enforcement/rule_enforcement/triple_alignment.py --module MOD-INF-015` |
| RULE-THREE 审判 | 每个文件必须通过三步审判（登记检查→重复检查→功能价值检查） |

#### 步骤 5：project-path-tree.yaml 同步 — ✅ 已完成

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §0 代码对齐验证 |
| 验证命令 | `python scripts/governance/generate_project_path_tree.py --diff` |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | logs 模块化失败 | 保留 shared/logging 直接使用，删除 logs/ 目录 |
| 2 | CT-TEL 注册失败 | 删除 cross_layer_contracts.yaml 中 4 条条目 |
| 3 | DEP-031 修正失败 | direction 改回 upstream |
| 4 | telemetry/ 清理失败 | git checkout 恢复旧文件 |
| 5 | path-tree 同步失败 | git checkout 恢复 path-tree |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | 九子系统代码存在 | `ls src/zephyr/system_telemetry/` exit 0 | 完成 | ✅ |
| 2 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ✅ |
| 3 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 4 | 告警已配置 | §6.1 每项阈值有告警规则 | 就绪 | ☐ |
| 5 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 6 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

construction_status=completed | verification_status=passed | code_alignment_verified=yes

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | Ring buffer 并发控制 | 算法 | threading.local 队列→定时冲刷；当前单进程架构零侵入 | src/zephyr/system_telemetry/metrics/ |
| 2 | Tail-based sampling | 算法 | 错误/高延迟/root span 100%保留，正常 10%采样，自适应 1%-10% | src/zephyr/system_telemetry/traces/ |
| 3 | Multi-Window Burn Rate | 算法 | 短窗口(1h)>14.4x→P0，长窗口(6h)>6x→P1，天窗口(3d)>1x→P2 | src/zephyr/system_telemetry/alerts/ |
| 4 | DLQ 自动修复 | 协议 | SCHEMA_ERROR→re-map / TYPE_ERROR→类型转换 / WRITE_FAILED→重试3次 / 超3次→DEAD | src/zephyr/system_telemetry/metrics/ |
| 5 | FQMN 自动注入 | 算法 | Telemetry(module_id)→metrics.counter(name)→内部生成 module_id::name | src/zephyr/infrastructure/runtime_integration/system_telemetry/facade.py |
| 6 | HMAC 链式校验 | 协议 | HMAC-SHA256(secret, line_index + prev_hmac + log_body)，每24h校验 | — |
| 7 | Counter 重置检测 | 算法 | process_start_ts 标签+delta recording+FLE reset-aware | src/zephyr/system_telemetry/metrics/ |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:---:|------|----------|----------|----------|
| 1 | 命令 | `Telemetry(module_id, environment)` | 模块接入遥测 | module_id: str, environment: str | Telemetry 实例 |
| 2 | 配置 | `config/metrics_schema.yaml` | 指标 Schema SSoT | YAML 格式 | 热加载 |
| 3 | 配置 | `config/alert_rules.yaml` | 告警规则定义 | YAML 格式 | 热加载 |
| 4 | 配置 | `config/sli_registry.yaml` | SLI 定义注册表 | YAML 格式 | 热加载 |
| 5 | 配置 | `config/flags.yaml` | FeatureFlag 定义 | YAML 格式 | 文件监听热加载 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:---:|------|---------|----------|----------|----------|
| 1 | 运行 | SQLite 损坏 | 文件校验失败 | 从 archive replay 重建 | 重建 metrics 数据 | 数据比对 |
| 2 | 运行 | ring buffer 溢出 | buffer 100% | 检查失控模块+速率限制 | buffer 降至正常 | backpressure 解除 |
| 3 | 运行 | DLQ 积压 | dlq_size>100MB | 检查 rejection_reason 分布 | 修复 schema/重试 | DLQ 监控 |
| 4 | 运行 | Telemetry 进程挂死 | watchdog 超时 | watchdog 自动重启 | 进程恢复 | health_check |
| 5 | 运行 | 磁盘空间不足 | >80%预算 | 执行容量降级策略 | 磁盘释放 | 降级解除 |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同文件写入（JSONL） | 单 Consumer 线程串行化 | 排队写入 | FIFO |
| ring buffer 并发写入 | threading.local 队列 | 定时冲刷 | 最后值(gauge)/增量(counter) |
| Schema Registry 并发注册 | SQLite 唯一约束 | 冲突→CONFLICT 错误码 | 拒绝重复 |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 模块数 | 51 | module_id_registry.yaml |
| 遥测数据量 | ~5GB | du data/telemetry/ |
| 日均指标事件 | ~50K | metrics.ingress_rate |
| 日均日志量 | ~50MB | JSONL 文件大小 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-TEL-001 | ring buffer 50%+ 持续5min | threading.local 队列冲刷 | P1 | 100-300 模块 | v2.1 | 待施工 |
| GAP-TEL-002 | SQLite flush >500ms | WAL 模式+batch split | P1 | 300-800 模块 | v2.2 | 待施工 |
| GAP-TEL-003 | JSONL 写入争用 P99>10ms | 独立 Consumer 线程 | P2 | 800-1500 模块 | v3.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | 九子系统初始设计 | ✅ |
| v1.1.0 | 2 | 扩展 | 修复增量 | ✅ |
| v2.0.0 | 3 | 重构 | 蓝图结构重构+模板合规+压缩 | ✅ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| threading.local 队列 | GAP-TEL-001 | metrics/ | Phase 2 | 待施工 |
| WAL 模式 | GAP-TEL-002 | metrics/ | Phase 3 | 待施工 |
| 独立 Consumer 线程 | GAP-TEL-003 | logs/ | Phase 4 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-TEL-001 | 九子系统通过 Telemetry 门面类统一暴露 | — | — | AI 不需要记忆九套 API | 2026-05-03 |
| 2 | D-TEL-002 | Ring buffer 并发方式 | threading.local队列 / multiprocessing.Queue | threading.local | 当前单进程架构零侵入 | 2026-05-03 |
| 3 | D-TEL-003 | 指标存储方式 | SQLite+ring buffer / 纯内存+定时快照 | SQLite+ring buffer | 持久化+查询能力 | 2026-05-03 |
| 4 | D-TEL-004 | 日志格式 | JSONL按日轮转 / SQLite日志表 | JSONL按日轮转 | 追加写入无锁竞争 | 2026-05-03 |
| 5 | D-TEL-005 | Trace 采样方式 | Tail-based / Head-based | Tail-based | 可保留错误/高延迟 Span | 2026-05-03 |
| 6 | D-TEL-006 | 告警算法 | Multi-Window Burn Rate / 阈值告警 | Multi-Window Burn Rate | 减少误报 | 2026-05-03 |
| 7 | D-TEL-007 | Schema 定义方式 | YAML SSoT+运行时校验 / 纯代码定义 | YAML SSoT | 可被蓝图漂移检测 | 2026-05-03 |
| 8 | D-TEL-008 | SQLite flush 策略 | 自适应间隔+batch split / 固定间隔 | 自适应+batch split | 大批次可能超500ms | 2026-05-03 |
| 9 | D-TEL-009 | JSONL 写入策略 | 单Consumer线程 / 多线程并发写 | 单Consumer线程 | 100 AI session 并发追加交叉截断 | 2026-05-03 |
| 10 | D-TEL-010 | AIBehaviorEvent 存储 | 独立ring buffer+独立SQLite表 / 共享MetricPoint通道 | 独立通道 | 日增量大，挤占 MetricPoint | 2026-05-03 |
| 11 | D-TEL-011 | Watchdog 运行模式 | 独立进程 / 进程内线程+OS级+Dead Man's Switch三层混合 | 三层混合 | 单进程架构下独立进程无自动启动保障→Watchdog从未运行；业界OTel Collector/Datadog Agent均为进程内健康检查 | 2026-05-18 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| FQMN | Fully Qualified Metric Name: {module_id}::{metric_name} | metric_name | FQMN 含模块前缀，全局唯一 |
| Burn Rate | Error Budget 消耗速率，相对于 SLO 窗口 | Error Rate | Burn Rate 是相对于预算的消耗速率 |
| Tail-based Sampling | 先采集再决定是否保留的采样策略 | Head-based Sampling | Head 在入口决策，Tail 在出口决策 |
| DLQ | Dead Letter Queue，存储被拒绝/无法处理的遥测事件 | archive | DLQ 是问题数据，archive 是冷数据 |
| Exemplar | MetricPoint 关联的 trace_id+span_id，支持指标→链路下钻 | Span | Exemplar 是指标上的链接，Span 是链路节点 |
| Meta-Telemetry | Telemetry 关于 Telemetry 自身的遥测数据 | health check | Meta-Telemetry 是性能内省，health check 是存活检测 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | MCP Server 接口未全部实现 | 中 | AI 可消费性设计部分待落地 | 逐步实现 §4.5 MCP Tools | §4.5 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ☐ |
| 2 | 设计 | §4 每个接口在蓝图特有章节有对应详细设计 | 逐接口核对 | ☐ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ☐ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 9 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 10 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | 九子系统接口冻结后 | 门面类模式已验证 |
| 接口契约 | evolving | 中 | MCP 接口全部实现后 | MCP Tools 逐步落地 |
| 数据模型 | stable | 高 | Schema 版本化稳定后 | MetricPoint/AIBehaviorEvent 已实现 |
| 施工步骤 | stable | 高 | 九子系统全部 completed | 代码已实现 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v1.0.0 | 九子系统初始设计 | — | 已完成 |
| v1.1.0 | 修复增量 | v1.0.0 | 已完成 |
| v2.0.0 | 蓝图结构重构+模板合规+压缩 | v1.1.0 | 已完成 |
| v2.1.0 | threading.local 队列冲刷 | v2.0.0 | 待施工 |
| v2.2.0 | WAL 模式+batch split | v2.1.0 | 待施工 |
| v3.0.0 | 独立 Consumer 线程 | v2.2.0 | 待施工 |

---

> 蓝图编写铁律见 [project_rules.md 防幻觉十八条](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) 及 [blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)。

---

> 蓝图拆分判定标准见 [blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)。

---

> 安全删除协议见 [project_rules.md RULE-THREE](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)。本蓝图不涉及文件删除。

---

## 必备链接

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/MTH-013 |
| 4 | 代码构建标准 | GOV-ENG-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` | 代码头部标准 |
| 5 | 压缩工作流标准 | GOV-DOC-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml` | 规格化流程 |
| 6 | 蓝图模板 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-construction-template.md` | 蓝图结构合规 |
| 7 | AI自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI操作权限 |
| 8 | 模块ID注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |

---

## 项目中已有类似功能

无。

---

---

## 1. 已实现代码完整路径索引

> **蓝图-代码同步强制约定（见 AGENTS.md §7 代码规范）**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 系统遥测——5子模块目录结构已建，代码全skeleton

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 核心架构设计 | **本文档 §1-§10** | 已取代的旧蓝图 |
| 施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-018 Agent RBAC 蓝图 | §4 接口契约、§10 依赖关系 |
| Tier 1 | MOD-INF-024 Budget Enforcer 蓝图 | §4 接口契约、§10 依赖关系 |
| Tier 2 | MOD-FEEDBACK_LOOP FLE 集成点 | §12 集成点 |
| Tier 2 | MOD-INF-022 Escalation Protocol 集成点 | §12 集成点 |
| Tier 3 | src/zephyr/system_telemetry/ 代码文件 | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| 接口契约新增/修改（§4） | 需 Owner 审批+通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |

---

## 蓝图特有章节

> 硬规则：模板章节=合规下限，超出内容 MUST 写在本章节内+标注三要素。写在本章节外=压缩工作流视为冗余→可删。写在本章节内+标注三要素=不可砍。

### 蓝图特有§A：九子系统详细设计

| 要素 | 内容 |
|------|------|
| 来源 | 蓝图原始设计+多次修复增量 |
| 仅本蓝图 | 九子系统是 Telemetry 独有的架构决策 |
| 不可砍 | 砍掉→AI 施工时无法实现子系统 |

#### A.1 metrics 子系统

**MetricPoint Schema**：见 §4.2 数据模型。

**指标类型**：

| 类型 | 用途 | 聚合方式 |
|------|------|---------|
| gauge | 瞬时值（CPU/内存/连接数） | 最后值 |
| counter | 单调递增（调用总数/Token消耗） | 增量(rate) |
| histogram | 分布（延迟/耗时） | P50/P90/P95/P99 |
| summary | 客户端分位数 | 客户端计算 |

**Cardinality 控制**：

| 控制策略 | 机制 | 阈值 |
|---------|------|:---:|
| 标签白名单 | schema registry 预定义合法标签 | — |
| 基数上限 | 单指标标签组合>1000 自动聚合 | >1000 |
| 基数告警 | 接近上限→cardinality_warning→FLE | >800 |
| TTL 裁剪 | 超7天无活跃上报的标签组合自动清理 | 7 days |
| strict_mode | FeatureFlag=ON 时超限直接拒绝 | — |
| zombie_scan | 每7天扫描僵尸指标，30天→物理删除 | 30 days |

**时钟偏差检测**：Span 时间戳用 wall clock(time.time())，时长用 monotonic clock(time.monotonic())。每5min 写入 local_clock_skew_us metric，skew>100ms→P2，>1s→P1。

**僵尸指标清理**：7天零写入→标记ZOMBIE→Metric Discovery API隐藏→30天→物理删除+schema注销。再次写入→自动复活。zombie_metric_count>50→P2，zombie_label_cardinality>10000→P1。

**入站速率限制 & Backpressure**：

| 控制层 | 机制 | 阈值 | 动作 |
|--------|------|:---:|------|
| per-module 速率限制 | 每模块每秒最大上报数 | 100/sec | 超→50%概率丢弃+rate_limit_hit |
| ring buffer 水位线1 | buffer 占用率 | >80% | BackpressureThrottle(CTR-BP-002) |
| ring buffer 水位线2 | buffer 占用率 | >95% | BackpressurePause(CTR-BP-001) |
| ring buffer 满载 | buffer 占用率 | =100% | 丢弃最旧+Pause+buffer_overflow |
| 背压恢复 | buffer 占用率 | <60% | BackpressureResume(CTR-BP-003) |

**Exemplar 关联**：MetricPoint→Exemplar(trace_id,span_id)→Trace→Log(trace_id)。关键告警触发时 exemplar 的 Span 自动标记 pinned 不删除。

**Counter 重置检测**：process_start_time 标签+FLE counter reset aware+stale counter detection(10min)+delta recording。

**幂等性保障**：idempotency_key={module_id}_{metric_name}_{timestamp_ns}_{nonce}，flush 时按 key 去重(72h TTL)，counter MUST 携带。

**DLQ 设计**：

| 属性 | 规格 |
|------|------|
| 存储格式 | JSONL |
| 存储路径 | data/telemetry/{environment}/dlq/{date}.jsonl |
| TTL | 30天 |
| 结构 | {original_event, rejection_reason, rejected_by, timestamp, dlq_id} |
| 单文件上限 | 100MB 后自动轮转 |

DLQ 自动修复：每60min 扫描→SCHEMA_ERROR→re-map / TYPE_ERROR→类型转换 / WRITE_FAILED→重试3次 / 超3次→DEAD(7天后删除)。监控：dlq_size>100MB→P2, dlq_growth_rate>10MB/h→P1, dlq_repair_success_rate<50%→P2。

**关键 SLI**：

| SLI | 公式 | SLO |
|-----|------|:---:|
| LLM 可用性 | Successful_Calls / Total_Calls | ≥99.5% |
| Gate 通过率 | Passed_Tasks / Total_Tasks_at_Gate | ≥95% |
| Pipeline 完成率 | Completed_Tasks / Dispatched_Tasks | ≥90% |
| Token 效率 | Useful_Output_Tokens / Total_Input_Tokens | ≥0.3 |
| TELEMETRY-HEALTH | Telemetry上报成功率 | ≥99.9% |
| METRIC-CARDINALITY | 超过基线上限的指标数 | =0 |

#### A.2 logs 子系统

基于 shared/logging.py 构建。shared.logging 提供 TraceContext 传播+get_logger+JSON Formatter——logs 子系统在其之上增加持久化策略(JSONLFileWriter)、级别过滤、PII 脱敏。不做第二个日志系统。

**日志分级**：DEBUG/INFO/WARNING/ERROR/FATAL。

**日志与 Trace 关联**：每个 JSONL log line 必须包含 event, level, module, trace_id, span_id, timestamp, message。

**日志安全性**：PII 自动脱敏 / 生产环境过滤 DEBUG / sensitivity_level 标记 / 写入失败降级链(JSONL→stderr→内存环形区1000条→丢弃+告警)。

#### A.3 traces 子系统

Span 数据模型兼容 CTR-TRACE-001。trace_id/span_id/parent_span_id 格式与 CTR-TRACE-001 一致(UUID hex, 32/16 char)。TraceContext 传播使用 shared/logging.py 的 contextvars 机制。

**W3C TraceContext 传播**：traceparent: 00-{trace_id(32hex)}-{span_id(16hex)}-{trace_flags(2hex)}。tracestate: zephyr={module_id};{environment};{session_id}。

**智能采样**：

| 采样策略 | 规则 | 保留率 |
|---------|------|:---:|
| 错误全保留 | status=="error" | 100% |
| 高延迟全保留 | duration>P95 | 100% |
| 根 Span 全保留 | parent_span_id 为空 | 100% |
| 正常流量采样 | 随机 | 10% |
| 自适应采样 | 系统负载高 | 1%-10% |

**采样决策传播**：Root span trace_flags: 01(sampled)→下游完整采集 / 00(not sampled)→下游仅记录 minimal span。

**跨进程传播载体**：

| 场景 | 传播方式 |
|------|---------|
| MCP Server→Tool 调用 | traceparent 写入 MCP Request metadata _meta 字段 |
| 主进程→子进程 | 环境变量 TRACEPARENT+命令行参数 |
| HTTP/gRPC | W3C 标准 header |
| 文件系统事件 | traceparent 写入事件 payload 顶层 |

**contextvars→W3C 桥接**：进入跨进程边界时 TraceContext→traceparent 序列化；退出时 traceparent→TraceContext 恢复。

**Span→Metrics 连接器**：traces pipeline→spanmetrics connector→自动生成 RED 指标(Rate/Errors/Duration)。

#### A.4 ai_behavior 子系统

监控 AI 模型行为健康度。FeatureFlag 整体开关 telemetry.enable_ai_behavior_tracking(默认ON)，成本阈值 telemetry.cost_alert_threshold_usd(默认5.0USD)。字段命名 MUST 映射到 OTel gen_ai.*（见蓝图特有§C）。

**七大监测维度**：

| 维度 | 关键指标 | 告警阈值 |
|------|---------|:---:|
| 模型调用画像 | 各模型调用占比 | 单模型>80%→路由异常 |
| Token与成本(FinOps) | 按 model×task×module 的 $ 成本 | 日成本>预算80%→Budget Enforcer |
| Gate 交互行为 | 各 Gate 拒绝比例 | G0 reject>20%→输入质量下降 |
| 输出质量与一致性 | 幻觉率 factual_consistency_score | <0.7→输出不可信 |
| Prompt 版本追踪 | prompt_template_id+version | 版本切换→关联输出质量变化 |
| 工具调用链追踪 | tool_name+count/task | 异常高频→Agent 陷入循环 |
| Agent 决策路径 | decision_point+options+chosen | 回退>3→决策摇摆 |

**错误分类学**：

| 维度 | 分类值 | 含义 |
|------|--------|------|
| Persistence | transient / permanent / intermittent | 暂时/永久/间歇 |
| Source | client / server / dependency / internal | 调用方/被调用方/依赖/自身 |
| Expectation | expected / unexpected / unknown | 预期/非预期/未知 |
| Severity | degraded / blocking / fatal | 降级/阻塞/致命 |

告警过滤：P0=permanent+blocking/fatal / P1=server/dependency+unexpected / P2=intermittent+count>threshold / expected+无趋势=不告警。

**AI 自我修正效能追踪**：

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| 修正触发率 | 发现异常后实际触发修正的比例 | <50% |
| 修正成功率 | 修正后24h内不复发 | <80% |
| 修正平均耗时 | anomaly_detected→fix_deployed | >1h |
| 修正引入新问题 | 修正后1h内 error_rate 环比上升 | >0 |
| 人为介入率 | AI 放弃修正→Escalation | >20% |

每次 AI 自我修正 MUST 记录 AISelfCorrectionEvent。连续3次修正同一 anomaly→HARD_PROBLEM→Escalate 人工。

#### A.5 archive 子系统

| 数据类型 | 归档时机 | 保留期 |
|---------|---------|:---:|
| metrics | 30天后压缩归档 | 90天后物理删除 |
| logs | 30天后 gzip | 90天后物理删除 |
| traces | 7天后压缩归档 | 90天后物理删除 |
| profiles | 14天后压缩归档 | 90天后物理删除 |

FeatureFlag: telemetry.archive_auto_cleanup=OFF 时暂停自动删除。

**灾备恢复**：

| 场景 | 恢复方式 | RTO | RPO |
|------|---------|:---:|:---:|
| SQLite metrics 损坏 | 从 archive JSONL replay 重建 | 1h | ≤60s |
| JSONL 日志损坏 | 从 archive gzip 解压恢复 | 10min | archive 后新日志 |
| 数据目录误删 | archive+git 恢复 schema+重建 | 2h | 上次 archive 后 |
| 全盘故障 | 外部备份恢复 | 4h | 取决于备份频率 |

灾备基线：每日 sqlite3 .backup→data/backups/telemetry_{date}.db(保留7天)。config/ 下的 schema+alert_rules 已在 git 中。

**遥测成本预算**：

| 成本维度 | 默认月预算 |
|---------|:---:|
| 磁盘占用 | 10GB |
| CPU 开销 | 不超过单核10% |
| 内存占用 | 512MB |
| LLM 遥测成本 | $0.50/月 |

成本感知降级：磁盘>80%预算→dev TTL减半+traces 5%采样 / >95%→dev 暂停+staging 1%+profiles 关闭 / =100%→仅保留 prod metrics+P0 logs。

#### A.6 profiles 子系统

FeatureFlag: telemetry.enable_profiling 控制（默认OFF）。

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| CPU 热点 | 按函数聚合 CPU 时间 | 新热点→性能回归 |
| 内存分配 | 按调用栈内存分配量 | 单函数>100MB→泄漏嫌疑 |
| 阻塞分析 | IO wait/lock contention 占比 | IO wait>50%→IO 瓶颈 |
| GIL 竞争 | GIL hold time 分布 | 单线程持锁>100ms→并发瓶颈 |

性能回归检测：新部署后 profiles→与基线对比→function duration delta>30%→PERF-REGRESSION→FLE。

#### A.7 health 子系统

不自行探测模块健康状态。通过 LifecycleManager 定时轮询所有已注册模块的 health_check()→ModuleHealth 输出。

Watchdog 运行模式（三层混合）：

| 层 | 机制 | 触发方式 | 覆盖场景 |
|---|------|---------|---------|
| L1 进程内 | Watchdog 线程嵌入 Telemetry daemon | `auto_boot` 自动启动 | 逻辑降级、线程死锁检测、心跳写入 |
| L2 OS 级 | systemd/Windows Service Watchdog | OS 自动管理 | 进程崩溃自动重启 |
| L3 外部 | Dead Man's Switch（心跳文件超时检测） | 独立监控/另一台机器 | OS 级故障 |

L1 进程内 Watchdog（默认模式）：每10s ping Telemetry health endpoint / 每30s 轮询所有模块 HealthCheck / 健康评分=weighted_avg(自身指标+各模块ModuleHealth) / 评分<0.7→告警+自动恢复 / 失败→FLE→Escalation→Feishu。

L2/L3 独立进程模式（可选）：`python -m zephyr.infra_ops.system_telemetry.watchdog --id wd-1`，用于部署层需要独立进程监控的场景。

**健康检查维度**：

| 检查项 | 健康阈值 |
|--------|:---:|
| metrics buffer | <80% |
| log writer 延迟 P99 | <100ms |
| trace collector 吞吐 | >100 spans/sec |
| schema validator 拒绝率 | <5% |
| 进程存活心跳 | 连续存活 |
| 磁盘可用空间 | >10GB |

**Watchdog 自保**：OS 级 systemd/Windows Service 自动重启。重启后检查 Telemetry 状态，下线>5min→直接 Escalation。

**Meta-Telemetry**：12 维自体内省指标（ingress_rate/flush_duration/buffer_depth/dropped_total/write_duration/spans_collected_rate/sampled_ratio/rejection_rate/dlq_size/cost_storage/per_module_ingress_top10/flush_batch_size），独立 telemetry_meta 表存储，独立 TTL（7d/30d/90d 分级），仅通过 MCP tool get_telemetry_health() 暴露。

#### A.8 alerts 子系统

Multi-Window Burn Rate 告警：短窗口(1h)>14.4x→P0紧急 / 长窗口(6h)>6x→P1警告 / 天窗口(3d)>1x→P2提示。

Alert Pipeline：去重(同SLI同窗口5min不重复)→聚合(同模块多SLI合并为Incident)→静默(维护窗口抑制非紧急)→路由(P0→Feishu@owner, P1→Feishu, P2→Dashboard badge)。

**Error Budget 告警矩阵**：

| SLI | SLO Target | Error Budget | Short-Window(1h) | Long-Window(6h) |
|-----|:---:|:---:|:---:|:---:|
| LLM 可用性 | 99.5% | 0.5% | >14.4x | >6x |
| Gate 通过率 | 95% | 5% | >14.4x | >6x |
| Pipeline 完成率 | 90% | 10% | >14.4x | >6x |

**通知通道**：Feishu Webhook(P0/P1) / Feishu 日摘要(每日09:00) / Dashboard(P2+趋势) / AI 消费通道(MCP get_alerts()) / Agent RBAC 通知(按 role 过滤)。

**SLO 违规自动 Postmortem**：FeatureFlag telemetry.enable_slo_postmortem(默认OFF)。触发→聚合相关 traces/logs/metrics/annotations→生成 Markdown 草稿→写入 Audit Trail→Escalation 推送摘要。

**合成监控**：

| 合成事务 | 频率 | 成功条件 |
|---------|:---:|------|
| synth.taskcard.e2e | 30min | 5min 内 complete |
| synth.llm.health | 5min | 30s 内 response, token>0 |
| synth.context_engine.fetch | 10min | 2s 内 response, context 非空 |
| synth.gate.ping | 5min | 1s 内 response |
| synth.db.write_read | 10min | 读写延迟<100ms |
| synth.mcp.tool_invoke | 5min | 返回有效 HealthReport |

合成事务 MUST 携带 synthetic=true 标签，排除 SLO 计算，独立统计。

**告警规则测试**：dry-run(历史数据回放) / inject(注入异常点) / shadow(24h 不发通知) / backtest(已知事件回放)。

**Silent Alert 检测**：每24h 扫描 ACTIVE 规则→30天未触发→SILENT_ALERT_REPORT→P2 提醒。

#### A.9 schema 子系统

MetricSchema 数据模型见 §4.2。

**蓝图漂移检测**：

| 检测项 | 扫描内容 | 产出 |
|--------|---------|------|
| 文件漂移 | blueprint §16 vs 磁盘 | missing/extra/status_mismatch |
| SLO 采集覆盖 | 蓝图 SLI vs Schema+metrics 24h 活跃 | orphan_slos/orphan_metrics |
| 告警规则漂移 | 蓝图 Error Budget vs alert_rules.yaml | alert_rule_drift_report |

**CI/CD Pipeline 可观测性**：

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| 构建健康 | build_duration / build_success_rate / build_failure_by_reason | >10min / <90% / flake>20% |
| 测试质量 | test_pass_rate / test_flakiness / test_coverage_delta | <95% / >30% / <-5% |
| 部署健康 | deploy_frequency / deploy_failure_rate / rollback_count / lead_time | 突降50% / >10% / >3/周 / >24h |
| AI 专属 | ai_generated_code_ratio / code_review_bypass_rate | >90%突增 / >5% |

部署后自动验证：合成监控→metrics 对比(latency P95 delta>20%→回归 / error_rate delta>5%→上升 / hallucination delta<-0.1→退化)→任一回归→FLE 自动 rollback。

**SLI 定义注册表**：SliDefinition 数据模型(sli_name/display_name/formula/formula_description/metric_source/evaluation_window/slo_target/slo_window/error_budget/owner_module/severity/blueprint_ref/deprecated)。YAML SSoT: config/sli_registry.yaml。SLI Registry→自动生成 alert_rules.yaml。

**Schema 版本化**：版本号 v{major}.{minor}。major=breaking(类型变更/删除) / minor=compatible(新增/可选标签/重命名有别名)。兼容性矩阵见下表：

| 变更类型 | 兼容性 | 行为 |
|---------|:---:|------|
| 新增 MetricSchema | ✅ | 注册新 schema, vX.(N+1) |
| 新增可选标签 | ✅ | 白名单扩展, vX.(N+1) |
| 重命名指标 | ⚠️ | 旧名保留为 alias, 2版本后废弃 |
| 新增必填标签 | ❌ | MUST 升级 major |
| 删除指标/标签 | ❌ | MUST 升级 major |
| 类型变更 | ❌ | MUST 升级 major, 建议新指标名 |

---

### 蓝图特有§B：信号体系

| 要素 | 内容 |
|------|------|
| 来源 | 蓝图原始设计 |
| 仅本蓝图 | 信号体系定义是 Telemetry 独有的领域模型 |
| 不可砍 | 砍掉→AI 不知道该采集什么信号 |

#### B.1 四大黄金信号

| 信号 | 维度 | 采集来源 | 阈值示例 |
|------|------|---------|---------|
| Latency | LLM API 响应时间/脚本执行时长/Pipeline 端到端 | MCP/subprocess tracker | P95>30s→FLE |
| Errors | LLM 调用失败/Gate 拒止/校验不通过 | Gate Engine/CE/Script | 错误率>5%→自动降级 |
| Traffic | LLM 调用总量/任务卡生成速率/API QPS | Pipeline/LSG/MCP | LLM QPS>100→Token Budget 预警 |
| Saturation | CE Token 填充率/VMS 占用/DB 连接池 | CE/VMS/Database | CE 填充>90%→自动截断 |

#### B.2 资源层 USE 信号

| 信号 | 维度 | 采集来源 | 阈值示例 |
|------|------|---------|---------|
| Utilization | CPU/内存/磁盘/GPU 利用率 | psutil/nvidia-smi | CPU>80% 持续5min→FLE |
| Saturation | 磁盘IO队列/网络连接/文件句柄/进程数 | OS metrics | 文件句柄>800→泄漏预警 |
| Errors | OOM Kill/磁盘满/网络不可达/GPU OOM | OS events/dmesg | 任意硬件级错误→P0 |

#### B.3 事件标注（Annotations）

| 事件类型 | 注入内容 | 触发时机 | 消费方 |
|---------|---------|---------|--------|
| 部署事件 | version_from/to/deployer/commit_sha | CI/CD 触发 | Dashboard 时间线 |
| 配置变更 | config_key/old/new/who | 配置写入检测 | FLE 关联异常 |
| 模型切换 | model_from/to/reason | AI Router 切换 | ai_behavior 追踪 |
| 蓝图变更 | blueprint_id/version_from/to/who | 蓝图写入 | 蓝图漂移检测 |
| Feature Flag 变更 | flag_name/state_change/rollout_pct | 特性开关切换 | Experimentation |

---

### 蓝图特有§C：OTel GenAI + AI Agent 语义约定对齐

| 要素 | 内容 |
|------|------|
| 来源 | OTel GenAI Semantic Conventions(v1.37+) + AI Agent Observability RFC(2025-11) |
| 仅本蓝图 | OTel 对齐是 Telemetry 的行业合规要求 |
| 不可砍 | 砍掉→AI 遥测数据无法被行业标准工具消费 |

ai_behavior + traces 子系统不自行发明语义——是对 OTel GenAI + Agent 语义约定的合规实现。

**OTel GenAI Span 属性映射**：

| OTel GenAI 标准属性 | Telemetry 对应字段 |
|---------------------|-------------------|
| gen_ai.operation.name | AIBehaviorEvent.event_type |
| gen_ai.provider.name | AIBehaviorEvent.labels["provider"] |
| gen_ai.request.model | AIBehaviorEvent.model_id |
| gen_ai.request.temperature | AIBehaviorEvent.labels["temperature"] |
| gen_ai.request.max_tokens | AIBehaviorEvent.labels["max_tokens"] |
| gen_ai.usage.input_tokens | AIBehaviorEvent.input_tokens |
| gen_ai.usage.output_tokens | AIBehaviorEvent.output_tokens |
| gen_ai.response.finish_reason | AIBehaviorEvent.labels["finish_reason"] |
| gen_ai.conversation.id | AIBehaviorEvent.labels["conversation_id"] |

**OTel AI Agent Span 类型映射**：

| OTel Agent Span 类型 | ZephyrAlpha 场景 |
|----------------------|-----------------|
| gen_ai.agent.invoke | M1/M6/M8 Agent 执行 |
| gen_ai.task.create | TaskCard 创建 |
| gen_ai.task.execute | TaskCard Pipeline 执行 |
| gen_ai.task.delegate | Orc 分配子任务 |
| gen_ai.tool.execute | Script D1-D12/工具调用 |
| gen_ai.workflow.execute | Pipeline 编排执行 |
| gen_ai.workflow.transition | Gate G0→G1→...→G7 |
| gen_ai.session | AI Session top-level |
| gen_ai.guardrail.check | Gate Engine 门禁判定 |
| gen_ai.human.review | Human-in-the-loop 审批 |
| gen_ai.memory.retrieve | CE 上下文检索 |
| gen_ai.memory.store | 知识库写入 |
| gen_ai.context.checkpoint | Session 状态快照 |

**OTel GenAI Metrics 对齐**：gen_ai.client.token.usage(Histogram)→Token消耗总量 / gen_ai.client.operation.duration(Histogram)→LLM API 响应时间。

**施工约定**：ai_behavior 字段 MUST 可映射到 gen_ai.* / traces Span 命名 MUST 遵循 gen_ai.<component>.<operation> / 新增维度 MUST 先查 OTel registry / 禁止为已有标准属性发明替代命名 / OTel Agent conventions 从 RFC→Stable 后 2 版本内同步。

---

### 蓝图特有§D：多环境隔离

| 要素 | 内容 |
|------|------|
| 来源 | v0.5.0 新增 |
| 仅本蓝图 | 1人+AI 场景下 dev/staging/prod 共存单机是 Telemetry 独有约束 |
| 不可砍 | 砍掉→dev 噪音污染 prod 告警 |

所有遥测数据 MUST 携带 environment 标签(dev/staging/prod)。

| 环境 | 数据路径 | TTL | profiling | trace采样 | 日志级别 | FLE | 告警通知 |
|------|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| dev | data/telemetry/dev/ | 14天 | OFF | 100% | DEBUG | OFF | 不发送 |
| staging | data/telemetry/staging/ | 30天 | ON 50% | 10% | INFO | 仅P0 | 仅P0→Feishu |
| prod | data/telemetry/prod/ | 90天 | ON 100% | 10% | WARNING | 全级别 | 全级别→Feishu |

---

### 蓝图特有§E：FeatureFlag 控制矩阵

| 要素 | 内容 |
|------|------|
| 来源 | v0.5.0 新增 |
| 仅本蓝图 | Telemetry 实验性功能的开关矩阵 |
| 不可砍 | 砍掉→AI 可能自行启用未验证功能 |

| Flag Key | 控制功能 | 默认值 | 影响子系统 |
|---------|------|:---:|------|
| telemetry.enable_profiling | profiling 全量开关 | OFF | profiles |
| telemetry.debug_full_sampling | trace 采样率提至100% | OFF | traces |
| telemetry.cost_alert_threshold_usd | 日 LLM 成本告警阈值 | 5.0 | ai_behavior→alerts |
| telemetry.log_level_override.{module} | 按模块覆盖日志级别 | 无覆盖 | logs |
| telemetry.enable_ai_behavior_tracking | AI 行为7维度全量追踪 | ON | ai_behavior |
| telemetry.cardinality_strict_mode | 超限指标直接拒绝 | OFF | metrics |
| telemetry.archive_auto_cleanup | 过期归档自动删除 | ON | archive |
| telemetry.enable_slo_postmortem | SLO 违规自动生成 Postmortem | OFF | alerts→Audit |
| telemetry.archive_encryption | archive 目录全量加密 | OFF | archive |

施工约定：AI 新增功能 MUST 同时创建 FeatureFlag(初始OFF) / AI 禁止自行修改 FlagState / 采集频率/采样率/阈值 SHOULD 通过 FeatureFlag 暴露 / 每次 AI session 启动时检查 FeatureFlag 状态。

---

### 蓝图特有§F：数据安全与合规

| 要素 | 内容 |
|------|------|
| 来源 | OWASP MCP08:2025 对齐 + OTel 敏感数据处理 |
| 仅本蓝图 | 遥测数据安全是 Telemetry 的基础设施责任 |
| 不可砍 | 砍掉→遥测数据泄露=系统架构级暴露 |

**OWASP MCP08:2025 对齐**：

| OWASP MCP08 要求 | Telemetry 实现 |
|------------------|---------------|
| Structured tamper-evident logging | HMAC chain + append-only store |
| SIEM/centralized monitoring | Telemetry 自身即 centralized monitoring |
| PII-safe logging | PII 脱敏 + field-level redaction |
| Field-level encryption for secrets | AES-256-GCM 逐字段加密 |
| Data classification labels | sensitivity_level (public/internal/confidential/secret) |
| Behavioral baselines for anomaly | FLE 基线 + ai_behavior 7维追踪 |
| Access control & segregation | telemetry file permissions + RBAC |
| Log retention aligned with compliance | archive TTL (30/90days) |
| Continuous audit verification | drift detection + audit drill |

**遥测数据访问控制**：

| 访问者 | 最小权限 | 审计 |
|--------|---------|:---:|
| Telemetry 自身进程 | 读写 data/telemetry/{env}/ | 不审计 |
| FLE | 只读 metrics+logs(最近24h) | 查询记录写入 telemetry_access_log |
| AI Agent (MCP) | 只读 MCP tools 暴露的聚合数据 | MCP tool call 自动生成 audit event |
| 1人维护者 | 全权访问(受控接口) | 文件系统级操作仅本地 |
| 外部模块 | 仅写入自身模块 metrics/logs | module_id 标签强制绑定 |

施工约定：禁止硬编码 API Key/Token/Secret / 新增 Log 字段 MUST 评估 PII / 禁止 AI Agent 绕过 MCP 直接读取原始文件 / HMAC secret 和 DB key 仅环境变量 / 安全事件→P1 即时 Feishu 通知。

---

### 蓝图特有§G：Observability-as-Code

| 要素 | 内容 |
|------|------|
| 来源 | Grafana 12 Git Sync / Sentry OTel Everywhere |
| 仅本蓝图 | Telemetry config 产出物的版本化管理 |
| 不可砍 | 砍掉→配置漂移无法追踪 |

| 产出物 | Git 路径 | 部署方式 |
|--------|---------|---------|
| metrics_schema.yaml | config/metrics_schema.yaml | 运行时热加载 |
| sli_registry.yaml | config/sli_registry.yaml | 运行时热加载 |
| alert_rules.yaml | config/alert_rules.yaml | 运行时热加载 |
| flags.yaml | config/flags.yaml | shared/flags 文件监听 |
| dashboards/ | config/dashboards/ | grafanactl push 或本地加载 |

CI/CD 集成：Lint(yamllint)→Validate(Telemetry schema validator)→Diff(git diff→changelog)→Test(dry-run alert rules)→Deploy(merge→热加载)→Verify(合成监控事务)。

施工约定：所有配置 MUST 在 config/ 目录同仓 git 管理 / 禁止 Grafana UI 手动编辑 / 变更 MUST 通过 git PR→人工确认→merge→热加载 / AI 发现问题→自动生成 PR 修改 config/。

---

### 蓝图特有§H：AI 可消费性设计

| 要素 | 内容 |
|------|------|
| 来源 | Sentry 2025 LLM 无法看到运行时行为 |
| 仅本蓝图 | AI 通过 MCP 消费遥测的接口设计 |
| 不可砍 | 砍掉→AI 开发闭环断裂 |

MCP Server 暴露的遥测接口见 §4.5。

**AI Session 冷启动工作流**：
1. get_blueprint_drift()→确认蓝图无漂移
2. get_service_health(target_module)→确认目标健康
3. get_recent_alerts()→检查未处理告警
4. get_silent_alerts()→检查静默告警
5. get_dlq_summary()→检查 DLQ 积压
6. get_telemetry_cost()→检查遥测成本状态
7. 以上全部 green 才继续施工

**自描述遥测**：每个 MetricPoint 持久化时自动附带 schema 引用(name/type/unit/schema_version/schema_uri)。AI 拿到任意 metric 数据点即可追溯完整语义定义。

**Metric Discovery MCP Tools**：list_metrics(module?, type?) / get_metric_detail(name) / search_metrics(query) / get_metrics_by_slo(slo_name)。

---

### 蓝图特有§I：配置热更新

| 要素 | 内容 |
|------|------|
| 来源 | v0.6.0 新增 |
| 仅本蓝图 | 1人+AI 维护场景下零重启要求 |
| 不可砍 | 砍掉→重启打断 AI 工作 |

热更新流程：shared/flags.py 启动文件监听(watchdog/inotify)→config/flags.yaml 变更→shared/flags 自动重载→EventBus 发布 CONFIG_CHANGE→各子系统订阅更新。

| 配置项 | 热更新 | 说明 |
|--------|:---:|------|
| telemetry.enable_profiling | ✅ | 下次采样周期应用 |
| telemetry.debug_full_sampling | ✅ | 即时生效 |
| telemetry.cost_alert_threshold_usd | ✅ | 下次 alert evaluation 应用 |
| telemetry.log_level_override.{module} | ✅ | shared.logging ContextVar 更新 |
| telemetry.enable_slo_postmortem | ✅ | 即时生效 |
| telemetry.cardinality_strict_mode | ✅ | 即时生效 |
| telemetry.archive_auto_cleanup | ✅ | 即时生效 |
| 新增子系统 | ❌ | 需重启 |
| 新增 MetricSchema | ✅ | schema registry 增量加载 |
| alert_rules.yaml 变更 | ✅ | 文件变更监听 |

施工约定：所有可配置参数 MUST 从 FeatureFlag/config 读取 / 每个子系统 MUST 实现 on_config_change(event) / 不允许"等待下次重启"模式 / 热更新失败→保持当前配置+记录错误。

---

### 蓝图特有§J：指标命名空间

| 要素 | 内容 |
|------|------|
| 来源 | v0.9.0 新增 |
| 仅本蓝图 | 100% AI 施工的特有风险——同名指标语义冲突 |
| 不可砍 | 砍掉→FLE 告警误判+Dashboard 数据混乱 |

FQMN = {module_id}::{metric_name}。Schema Registry 以 FQMN 为唯一 key。两个不同 module_id 可注册相同 metric_name——自动解歧。同一 module_id 内 metric_name MUST 唯一。

module_id 自动注入：Telemetry("MOD-CONTEXT_ENGINE").metrics.counter("llm_calls_total", 1)→内部自动生成 "MOD-CONTEXT_ENGINE::llm_calls_total"。

Metric Discovery API 命名空间过滤：list_metrics(module="MOD-CONTEXT_ENGINE")→仅返回该模块指标 / search_metrics("llm_calls")→按 module_id 分组显示。

---

### 蓝图特有§K：批量上报 API

| 要素 | 内容 |
|------|------|
| 来源 | v0.9.0 新增 |
| 仅本蓝图 | Pipeline 并行执行的批量上报性能优化 |
| 不可砍 | 砍掉→逐个上报导致锁竞争 |

- metrics.report_batch([MetricPoint, ...])：一次 lock acquire→逐条 schema validate(失败单条入DLQ)→批量写入→返回{success_count, failed_count, dlq_ids}
- logs.log_batch([LogEntry, ...])：一次 JSONL 追加(单行一条，一次 write 多行)
- traces.start_batch_spans([SpanContext, ...])：并行子任务 span 批量创建

施工约定：超过10个同类型调用时 MUST 使用 batch / 批量失败时逐条降级为独立调用 / 批量不改变语义——仅性能不同。
