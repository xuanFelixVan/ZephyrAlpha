---
module_id: "MOD-INF-016"
title: "Shared + Core 蓝图 — 跨层共享基础设施"
doc_type: blueprint
status: Active
version: "0.14.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: phase_14_tested_and_audited（Phase 0-14 全部完成 + 544测试通过含48对抗审计含孤儿链验证；Phase 15-20 planned）
belongs_to: "MOD-MASTER-001"
summary: "ZephyrAlpha Shared + Core 蓝图 v0.15.0——Shared: 跨层数据契约 + Task基座（31字段） + 事件总线 + 能力定义 + 内容指纹 + DOS启动器 + 路径/时间/Token/Frontmatter SSoT + API索引 + 统一错误层次 + 枚举集中re-export + 事件体Schema + 韧性基座(重试/熔断/降级) + 生命周期钩子 + FeatureFlag + 类型别名 + diff/patch工具 + 安全文件操作(原子写/备份/rollback) + 配置加载校验 + 结构化日志(ZephyrLogger/trace_id传播) + AI快速参考(SHARED-QUICKREF) + 测试夹具/工厂(testing) + Schema迁移系统(migration) + API废弃策略(deprecation) + 死信队列(dlq) + 版本协商(__version__) + 健康聚合(health) + 统一序列化(serialization) + API Client基类(api_client) + Secrets管理(secrets) + 缓存抽象(cache) + 速率限制器(limiter) + 幂等性(idempotency) + 上下文传播(context) + Metrics收集(metrics) + 分页工具(pagination) + 时间工具(time_utils) + 环境检测(env) + 分布式锁(lock) + Outbox模式(outbox) + Schema Registry(schema_registry) + 蓝图路由评分(blueprint_scorer) + 全部10个early-bird已落盘已测试已审计(cost_budget/context_budget/evals/session_audit/durable_execution/post_process/constitutional_update/multi_agent/skill_registry/version_negotiation)。Core: BlueprintDecomposer + models.py v0.3.0（继承Task 31字段全链路贯通）。2 子系统 61 已跟踪文件已落盘（49 Phase 0-10 + 10 Phase 11-14 已测试 + 2 core）+ 44 orphan 已分类注册（3在§5.1 + 41在§5.1b）。施工 Phase 1-14 完成 + 测试完成。TD-SHARED-001（34对发散副本）已全部解决为 re-export wrapper。8轮审计 + 1轮红队对抗审计（48对抗测试全通过含A11孤儿链验证）。544 全量测试通过。"
tags: [shared, core, cross-layer, contracts, ssot-guard, event-bus, blueprint-decomposer, infrastructure, v0.14.0, production-ready, phase-10-complete, audit-complete, blueprint-complete]
priority: P1
depends_on:
  - {target: "architecture-model/layers/b_shared.yaml", at: "全篇", why: "Shared YAML SSoT——本蓝图真源"}
  - {target: "architecture-model/layers/b_core.yaml", at: "全篇", why: "Core YAML SSoT——本蓝图真源"}
---

# Shared + Core 蓝图

> **module_id**: MOD-INF-016 | **version**: 0.14.0 | **status**: active | **layer**: cross_layer

> **真源声明**：Shared canon SSoT 为 [b_shared.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_shared.yaml)；
> Core canon SSoT 为 [b_core.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_core.yaml)。
> Shared + Core 合并为一个蓝图（两者均为跨层基础设施，且体积较小）。

> **对标**：Google Monorepo `shared/` 模式 + DDD Shared Kernel（跨限界上下文共享领域模型）。

---

## 1. 概述

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-016 |
| 涵盖 | Shared (`src/zephyr/shared/`) + Core (`src/zephyr/core/`) |
| 文件数 | Shared 49 文件(Phase 0-10 已审计) + 10 early-bird(Phase 11-14) + Core 2 文件 = 61 已跟踪文件（另有 ~43 orphan 待分类） |
| 核心职责 | 提供所有系统共用的数据模型、基础设施、工具函数 |

---

## 2. Shared 模块（9 子模块, 59 文件——49 Phase 0-10 + 10 Phase 11-14 early-bird）

## §2 子模块与职责

| 序号 | 子模块 | 职责 | 文件数 |
|------|--------|------|--------|
| §2.1 | 数据契约（contracts） | 跨层 Pydantic models SSoT + 输入/输出契约装饰器 | 5 |
| §2.2 | 事件总线（events） | 异步 Observer Pub/Sub + 事件体 schema + 死信队列(DLQ) | 6 |
| §2.3 | 核心能力（core） | Task核心模型 (31字段基座) + BlueprintDecomposer | 2 |
| §2.4 | 韧性组件（resilience） | CircuitBreaker + Retry + FallbackChain | 4 |
| §2.5 | 生命周期（lifecycle） | 模块 start/stop/health_check 钩子 + 优雅关闭 | 3 |
| §2.6 | 配置管理（config） | YAML 配置加载 + 校验 | 3 |
| §2.7 | 通用工具（utilities） | 类型别名 + diff/patch + 文件操作 + 常量 + FeatureFlag + 能力 + API索引 + 错误层次 + 枚举 + 日志 + SHARED-QUICKREF + 测试夹具 + Schema迁移 + 废弃策略 + 版本协商 + 健康聚合 | 24 |
| §2.8 | 生产基础设施（production） | 序列化 + API Client + Secrets + 缓存 + 速率限制 + 幂等性 + 上下文 + Metrics + 分页 + 时间工具 + 环境检测 + 分布式锁 + Outbox + Schema Registry | 14 |
| §2.9 | AI 专属基础设施（planned） | AI 成本预算与熔断 + Token/上下文预算管理 + Evals 框架 + Durable Execution + 后处理管道 + Session 审计轨迹 + Multi-Agent 编排 + Skill/Prompt 注册表 + Model Provider 抽象 + 上下文压缩 + 输出质量评分 + 宪法自更新 + DI 容器 + 代码沙箱 + 配置覆盖链 | 0（待施工） |

### 2.1 shared-contracts（跨层数据契约）

| 文件 | 职责 |
|------|------|
| `instrument.py` | 金融 Instrument 模型（symbol/name/asset_type）|
| `money.py` | 货币金额模型 + 汇兑 |
| `timestamp.py` | 时间戳模型（ISO 8601 含时区）|
| `runtime_plane_tag.py` | 运行时平面标签（cold/warm/hot）|

### 2.2 shared-infra（共享基础设施）

| 文件 | 职责 |
|------|------|
| `schemas.py` | **Task 31字段 Pydantic V2 模型**——TaskCard 基座 |
| `ssot_guard.py` | SSoT 守卫——防止多个文件定义同一概念 |
| `observer.py` | 观察者事件总线——系统间松耦合消息通知 |
| `capability.py` | 能力定义——系统能力注册与发现 |
| `content_fingerprint.py` | 内容指纹——文件内容哈希去重 |
| `dos_launcher.py` | DOS 启动器——Windows 兼容性工具 |
| `paths.py` | 项目路径常量 SSoT——REPO_ROOT/DB_PATH/缓存目录等集中定义 |
| `time_utils.py` | 时间工具 SSoT——utc_now/now_iso/default_now 唯一入口 |
| `token_utils.py` | Token 估算 SSoT——estimate_tokens 统一入口（1 token ≈ 4 字符）|
| `frontmatter_utils.py` | Markdown/YAML frontmatter 解析 SSoT——parse/extract 统一接口 |
| `API_INDEX.py` | Shared API 索引——AI 冷启动时的"员工通讯录"，列出所有 shared 公开符号 |
| `logging.py` | **结构化日志系统**——ZephyrLogger + contextvars trace_id 传播 + 双模式输出（控制台人类可读 / 文件 JSON） |
| `SHARED-QUICKREF.yml` | **AI 零歧义快速参考**——按消费场景组织的 YAML canonical 索引 |
| `testing.py` | **测试夹具/工厂**——Make valid Task/AuditReport/KnowledgeEntry/FailurePattern/HandoffPackage。AI 无需记忆必填字段 |
| `migration.py` | **Schema 版本化迁移**——BFS 最短路径自动迁移 Task dict 版本链 + 双向支持 |
| `deprecation.py` | **API 废弃策略**——@deprecated 装饰器 + warn/strict/silent 三模式 |
| `events/dlq.py` | **死信队列**——拦截 observer 失败事件 → SQLite 持久化 → 定时重试 |
| `__version__.py` | **版本常量**——PEP 440 __version__ + check_shared_version() 运行时校验 |
| `health.py` | **聚合健康检查**——AggregateHealth + ALL_HEALTHY/DEGRADED/UNHEALTHY + JSON 可序列化 |

### 2.3 shared-errors（统一错误层次）

> **补全 ssot_guard.py:L103 标记的「尚未完成的 ZephyrBaseError 体系」。**
> 与 contracts/errors/ 的区别：contracts/errors/ 是 dataclass 值对象（跨层结构化错误传递），
> 本子模块是 Python Exception 继承树（throw/catch 统一入口）。

| 文件 | 职责 |
|------|------|
| `errors.py` | **ZephyrBaseError** + 12 子类——ConfigError / ContractError / SecurityError / ValidationError / TaskError / PipelineError / GateError / ContextError / FeedbackError / DataError / IOError / UnimplementedError |

### 2.4 shared-constants（集中 re-export）

> **修复散落枚举问题**——此前 AI 需要到 instrument.py / order.py / observer.py / schemas.py 四处找枚举。

| 文件 | 职责 |
|------|------|
| `constants.py` | 所有共享枚举集中 re-export——AssetClass / OrderSide / EventType / TaskStatus / KeCategory 等 22 个枚举/常量 |

### 2.5 shared-events（事件体 Schema）

> **修复 B6/B10 盲点**——observer.py 的 emit() 接受裸 dict，消费者不知道 payload 结构。

| 文件 | 职责 |
|------|------|
| `events/event_schemas.py` | **5 个 EventType 对应的 Pydantic V2 frozen Schema** + EVENT_PAYLOAD_MAP |

### 2.6 shared-resilience（韧性基座）

> **盲点 B6/B9/B15 修复**——统一重试/熔断/降级策略，零依赖基类。
> 与 gates/circuit_breaker.py 互补——本模块纯内存，gates 版 SQLite 持久化 + 门禁集成。

| 文件 | 职责 |
|------|------|
| `resilience/retry.py` | **async_retry 装饰器**——指数退避 + jitter + 异常白名单/黑名单 |
| `resilience/circuit_breaker.py` | **CircuitBreaker 状态机**——CLOSED/OPEN/HALF_OPEN 三态，线程安全，零持久化 |
| `resilience/fallback.py` | **FallbackChain 降级链**——按序尝试 fallback 函数，全部失败抛 FallbackExhaustedError |

### 2.7 shared-lifecycle（模块生命周期）

> **盲点 B8 修复**——统一模块初始化/启动/关闭/健康检查契约。

| 文件 | 职责 |
|------|------|
| `lifecycle/hooks.py` | **LifecycleAware Protocol** + **LifecycleManager 编排器**——on_init/on_startup/on_shutdown/health_check |

### 2.8 shared-feature-flags（功能开关）

> **盲点 B7/B10 修复**——100% AI 施工下的 AI 行为开关，配置驱动。

| 文件 | 职责 |
|------|------|
| `flags.py` | **FeatureFlag + FlagRegistry**——三态开关 ALWAYS_ON/CONDITIONAL/ALWAYS_OFF + 按 module_id/agent_id 灰度 |

### 2.9 shared-utilities（通用工具层）

> **盲点 #5/#14/#15/#3 修复**——类型安全 + diff/patch + 安全I/O + 配置加载四大缺口。

| 文件 | 职责 |
|------|------|
| `types.py` | **13 个语义化 NewType 别名**——TaskId / ModuleId / FilePath / SessionId / AgentId / ... |
| `diff_utils.py` | **compute_diff + apply_patch**——统一 diff 格式 + patch 干跑检测 |
| `file_utils.py` | **atomic_write + backup_and_rollback**——POSIX 原子写入 + 自动备份回滚 |
| `config/loader.py` | **load_yaml_config + Pydantic 校验**——三段式 YAML 加载（parse→merge→validate）|

---

## 3. Core 模块（1 子模块, 2 文件）

| 文件 | 职责 |
|------|------|
| `blueprint_decomposer.py` | 蓝图分解器——蓝图.md → 多个 TaskCard |
| `models.py` | 核心数据模型 v0.3.0——继承 schemas.py Task（31字段：28业务+3 DB追踪），全链路贯通 |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | 全部 29 文件已实现 | ✅ implemented |
| experimental | models.py 升级到 v0.3.0（继承 schemas.py Task 31字段）| ✅ completed |
| phase_4 | 可观测 & 契约安全——结构化日志 + 契约测试 + AI 快速参考 | ✅ completed |
| phase_5 | 演化安全——测试夹具/工厂 + Schema 迁移 + 废弃策略 | ✅ completed |
| phase_6 | 韧性增强——死信队列 + 版本协商 + 健康聚合 | ✅ completed |
| phase_7 | 生产基础 1——序列化 + API Client + Secrets 管理 | ✅ completed |
| phase_8 | 生产基础 2——缓存 + 速率限制 + 幂等性 + 上下文传播 | ✅ completed |
| phase_9 | 可观测增强 —— Metrics + 分页 + 时间工具 + 环境检测 + SemVer | ✅ completed |
| phase_10 | 进阶架构 —— 分布式锁 + Outbox 模式 + Schema Registry | ✅ completed |
| phase_11 | AI 成本可控 —— 成本预算熔断 + 上下文预算管理（B26, B28） | ✨ early-bird（cost_budget 208行3类9函 + context_budget 259行4类17函，已落盘已导入，缺单元测试） |
| phase_12 | AI 质量可控 —— Evals 框架 + Session 审计轨迹（B29, B32） | ✨ early-bird（evals 258行7类14函 + session_audit 315行8类19函，已落盘已导入，缺单元测试） |
| phase_13 | AI 流程可控 —— Durable Execution + 后处理管道（B30, B31） | ✨ early-bird（durable_execution 335行6类19函 + post_process 289行5类9函，已落盘已导入，缺单元测试） |
| phase_14 | AI 团队可控 —— 宪法自愈 + Multi-Agent 编排 + Skill 注册表（B27, B33, B34）+ 版本协商 | ✨ early-bird（constitutional_update 225行3类7函 + multi_agent 272行7类13函 + skill_registry 194行6类2函 + version_negotiation 174行6类8函，已落盘已导入，缺单元测试） |
| phase_15 | AI 架构可控 —— Provider 抽象 + 上下文压缩 + 输出评分 + DI 容器 + 沙箱 + 配置链（B35-B40） | ⬜ planned |
| phase_16 | AI 溯源可控 —— AIBOM 物料清单 + Memory Bank 持久记忆（B41, B42） | ⬜ planned |
| phase_17 | AI 安全可控 —— DSPy 声明式优化 + Structured Concurrency + Dry-run 模式（B43, B44, B45） | ⬜ planned |
| phase_18 | AI 韧性可控 —— Backpressure + Quota 配额 + Degradation Matrix + KG 接口 + Drift 检测（B46-B50） | ⬜ planned |
| phase_19 | AI 安全纵深 —— Prompt 注入防御 + 结构化输出强制保障 + LLM API 专属限流（B51-B53） | ⬜ planned |
| phase_20 | AI 校验护盾 —— 工具调用参数护栏 + Prompt 缓存策略 + 多 Provider 语义降级（B54-B56） | ⬜ planned |

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 共享+核心——61 已跟踪文件（49 Phase 0-10 + 10 Phase 11-14 early-bird + 2 core）已落盘 + ~43 未跟踪孤儿文件待分类

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/shared/API_INDEX.py` | ✅ 已实现 | |
| `src/zephyr/shared/capability.py` | ✅ 已实现 | |
| `src/zephyr/shared/content_fingerprint.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/market/instrument.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/portfolio/money.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/core/runtime_plane_tag.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/core/timestamp.py` | ✅ 已实现 | |
| `src/zephyr/shared/dos_launcher.py` | ✅ 已实现 | |
| `src/zephyr/shared/frontmatter_utils.py` | ✅ 已实现 | |
| `src/zephyr/shared/observer.py` | ✅ 已实现 | |
| `src/zephyr/shared/paths.py` | ✅ 已实现 | |
| `src/zephyr/shared/schemas.py` | ✅ 已实现 | |
| `src/zephyr/shared/ssot_guard.py` | ✅ 已实现 | |
| `src/zephyr/shared/time_utils.py` | ✅ 已实现 | |
| `src/zephyr/shared/token_utils.py` | ✅ 已实现 | |
| `src/zephyr/shared/constants.py` | ✅ 已实现 | Phase 1 新增：共享枚举集中 re-export |
| `src/zephyr/shared/errors.py` | ✅ 已实现 | Phase 1 新增：ZephyrBaseError + 12 子类 |
| `src/zephyr/shared/events/event_schemas.py` | ✅ 已实现 | Phase 1 新增：Observer 事件体 Pydantic Schema |
| `src/zephyr/shared/resilience/retry.py` | ✅ 已实现 | Phase 2 新增：async_retry 重试装饰器 |
| `src/zephyr/shared/resilience/circuit_breaker.py` | ✅ 已实现 | Phase 2 新增：轻量熔断器三态状态机 |
| `src/zephyr/shared/resilience/fallback.py` | ✅ 已实现 | Phase 2 新增：FallbackChain 降级策略链 |
| `src/zephyr/shared/lifecycle/hooks.py` | ✅ 已实现 | Phase 2 新增：模块生命周期钩子 + 健康检查 |
| `src/zephyr/shared/flags.py` | ✅ 已实现 | Phase 2 新增：FeatureFlag 功能开关系统 |
| `src/zephyr/shared/types.py` | ✅ 已实现 | Phase 3 新增：13 个语义化 NewType |
| `src/zephyr/shared/diff_utils.py` | ✅ 已实现 | Phase 3 新增：diff/patch 统一工具 |
| `src/zephyr/shared/file_utils.py` | ✅ 已实现 | Phase 3 新增：原子写/备份/rollback |
| `src/zephyr/shared/config/loader.py` | ✅ 已实现 | Phase 3 新增：YAML加载+Pydantic校验 |
| `src/zephyr/shared/logging.py` | ✅ 已实现 | Phase 4 新增：结构化日志 ZephyrLogger + trace_id 传播 |
| `src/zephyr/shared/SHARED-QUICKREF.yml` | ✅ 已实现 | Phase 4 新增：AI 零歧义快速参考 canonical YAML |
| `src/zephyr/shared/testing.py` | ✅ 已实现 | Phase 5 新增：测试夹具/工厂——7个工厂函数 |
| `src/zephyr/shared/migration.py` | ✅ 已实现 | Phase 5 新增：版本化 Schema 迁移系统 |
| `src/zephyr/shared/deprecation.py` | ✅ 已实现 | Phase 5 新增：@deprecated 装饰器 + 三模式 |
| `src/zephyr/shared/events/dlq.py` | ✅ 已实现 | Phase 6 新增：死信队列——SQLite 持久化 + 定时重试 |
| `src/zephyr/shared/__version__.py` | ✅ 已实现 | Phase 6 新增：PEP 440 版本常量 + 运行时校验 |
| `src/zephyr/shared/health.py` | ✅ 已实现 | Phase 6 新增：聚合健康检查 + JSON 可序列化 |
| `src/zephyr/shared/serialization.py` | ✅ 已实现 | Phase 7 新增：统一序列化——Decimal/str, datetime→ISO 8601 |
| `src/zephyr/shared/api_client.py` | ✅ 已实现 | Phase 7 新增：统一 API Client 基类——超时/重试/熔断/metrics |
| `src/zephyr/shared/secrets.py` | ✅ 已实现 | Phase 7 新增：Secrets 管理——Env/DotEnv Provider + sanitize |
| `src/zephyr/shared/cache.py` | ✅ 已实现 | Phase 8 新增：缓存抽象——TTL + LRU 驱逐 + 最大容量 |
| `src/zephyr/shared/limiter.py` | ✅ 已实现 | Phase 8 新增：Token Bucket 速率限制器 |
| `src/zephyr/shared/idempotency.py` | ✅ 已实现 | Phase 8 新增：幂等性 infrastructure——Stripe 24h TTL 对齐 |
| `src/zephyr/shared/context.py` | ✅ 已实现 | Phase 8 新增：结构化 RequestContext——trace_id/span_id/tenant/agent |
| `src/zephyr/shared/metrics.py` | ✅ 已实现 | Phase 9 新增：Metrics Registry——Counter/Gauge/Histogram + Prometheus text |
| `src/zephyr/shared/pagination.py` | ✅ 已实现 | Phase 9 新增：统一分页工具——Page[T]/CursorPage[T] |
| `src/zephyr/shared/time_utils.py` | ✅ 已实现 | Phase 9 新增：时间工具——now_utc/freeze_time/parse_iso |
| `src/zephyr/shared/env.py` | ✅ 已实现 | Phase 9 新增：环境检测——is_dev/is_prod/is_test |
| `src/zephyr/shared/lock.py` | ✅ 已实现 | Phase 10 新增：分布式锁抽象——MemoryLock + async context manager |
| `src/zephyr/shared/outbox.py` | ✅ 已实现 | Phase 10 新增：事务性 Outbox——polling publisher + at-least-once |
| `src/zephyr/shared/schema_registry.py` | ✅ 已实现 | Phase 10 新增：Schema Registry——集中式版本编目 + 兼容性查询 |
| `src/zephyr/core/blueprint_decomposer.py` | ✅ 已实现 | |
| `src/zephyr/core/models.py` | ✅ 已实现 | v0.3.0 — 继承Task 31字段全链路贯通 |
| `src/zephyr/shared/tracing.py` | ✅ 已实现 | Phase 6 新增：OpenTelemetry 兼容 tracing context |
| `src/zephyr/shared/cost_budget.py` | ✨ early-bird | Phase 11 (B26)：AI 成本预算熔断——208行 3类 9函 |
| `src/zephyr/shared/context_budget.py` | ✨ early-bird | Phase 11 (B28)：上下文预算管理——259行 4类 17函 |
| `src/zephyr/shared/evals.py` | ✨ early-bird | Phase 12 (B29)：Evals 评估框架——258行 7类 14函 |
| `src/zephyr/shared/session_audit.py` | ✨ early-bird | Phase 12 (B32)：Session 审计轨迹——315行 8类 19函 |
| `src/zephyr/shared/durable_execution.py` | ✨ early-bird | Phase 13 (B30)：Durable Execution——335行 6类 19函 |
| `src/zephyr/shared/post_process.py` | ✨ early-bird | Phase 13 (B31)：后处理管道——289行 5类 9函 |
| `src/zephyr/shared/constitutional_update.py` | ✨ early-bird | Phase 14 (B27)：宪法自更新——225行 3类 7函 |
| `src/zephyr/shared/multi_agent.py` | ✨ early-bird | Phase 14 (B33)：Multi-Agent 编排——272行 7类 13函 |
| `src/zephyr/shared/skill_registry.py` | ✨ early-bird | Phase 14 (B34)：Skill/Prompt 注册表——194行 6类 2函 |
| `src/zephyr/shared/version_negotiation.py` | ✨ early-bird | Phase 14：版本协商——174行 6类 8函 |
| `src/zephyr/shared/path_resolver.py` | ✅ 已实现 | Phase 10 补注册：路径解析器——261行2类7函。消费者：mcp/task_manager_server.py |
| `src/zephyr/shared/contract_bus.py` | ✅ 已实现 | Phase 10 补注册：契约总线——140行6类14函。消费者：contract_tester.py |
| `src/zephyr/shared/event_bus.py` | ✅ 已实现 | Phase 10 补注册：共享事件总线——124行3类7函（与core/events/event_bus独立） |

### 5.1b 待集成文件（orphan-classified — 已落盘，功能完整，缺调用入口与单元测试）

| 文件 | 集群 | 规模 | 用途 |
|------|------|------|------|
| `adaptive_sampler.py` | 资源管控 | 59行1类4函 | 自适应采样——系统负载感知降采样 |
| `ai_audit_guard.py` | 安全审计 | 171行7类5函 | AI修改审计守卫——变更前合规检查 |
| `ai_understandability_constraint.py` | 质量约束 | 64行1类2函 | AI输出可理解性约束强制执行 |
| `alert_escalation.py` | 告警治理 | 70行3类4函 | 告警升级——未处理告警自动升级 |
| `alert_manager.py` | 告警治理 | 110行3类5函 | 告警收敛管理——去重+分组 |
| `alert_precision_tracker.py` | 告警治理 | 50行1类5函 | 告警精度追踪——准确率统计 |
| `blueprint_code_auditor.py` | 质量审计 | 60行1类2函 | 蓝图-代码一致性审计 |
| `budget_aware_prompt.py` | 成本控制 | 51行2类3函 | 预算感知提示生成 |
| `capacity_calibrator.py` | 容量治理 | 67行2类5函 | 容量校准器——预测准确率提升 |
| `capacity_digital_twin.py` | 容量治理 | 42行1类3函 | 容量数字孪生——模拟测算 |
| `capacity_fingerprint.py` | 容量治理 | 58行2类4函 | 容量指纹——负载特征识别 |
| `capacity_governance_loop.py` | 容量治理 | 222行3类5函 | 容量治理闭环——规划→执行→验证 |
| `capacity_runbook_generator.py` | 容量治理 | 59行2类3函 | 容量Runbook自动生成 |
| `code_economy_analyzer.py` | 成本控制 | 61行1类4函 | 代码经济效益分析 |
| `combinatorial_gate.py` | 质量门禁 | 58行1类3函 | 组合门禁——多条件AND/OR |
| `config_validator.py` | 配置治理 | 91行2类5函 | 配置校验器——Schema检查 |
| `contract_tester.py` | 契约测试 | 69行2类7函 | 契约合规测试——运行时校验 |
| `core_integrity_guard.py` | 安全审计 | 65行1类3函 | 核心完整性守卫 |
| `cost_estimator.py` | 成本控制 | 135行3类8函 | 成本估算器——Token/API成本预测 |
| `degradation_chain.py` | 韧性基座 | 197行5类8函 | 退化链追踪——级联故障分析 |
| `dependency_capacity_guard.py` | 容量治理 | 40行1类5函 | 依赖容量守卫——跨模块容量检查 |
| `dual_channel_alert.py` | 告警治理 | 73行2类2函 | 双通道告警——冗余通知 |
| `error_budget_tracker.py` | 成本控制 | 152行3类4函 | 错误预算追踪器——SLO余量管理 |
| `event_bus_upgrade.py` | 事件系统 | 76行3类7函 | 事件总线升级——v1→v2迁移 |
| `fault_isolator.py` | 韧性基座 | 92行3类6函 | 故障隔离器——组件级熔断 |
| `heartbeat_server.py` | 基础设施 | 68行2类8函 | 心跳服务器——健康端点 |
| `kill_switch.py` | 韧性基座 | 139行3类8函 | Kill Switch——紧急停止机制 |
| `longevity_monitor.py` | 容量治理 | 68行1类3函 | 长时运行监控——内存/连接泄漏检测 |
| `model_capacity_probe.py` | 容量治理 | 67行2类3函 | 模型容量探针——负载极限探测 |
| `module_birth_registry.py` | 注册治理 | 61行2类4函 | 模块出生注册表——创建时自动登记 |
| `owner_trust_gauge.py` | 安全审计 | 60行2类5函 | 信任度量——Agent行为信誉评分 |
| `pydantic_v2_migrator.py` | 迁移工具 | 77行1类3函 | Pydantic v1→v2迁移助手 |
| `reasoning_spans.py` | 可观测性 | 90行1类5函 | 推理跨度追踪——AI推理步骤记录 |
| `sandbox_executor.py` | 安全执行 | 158行4类8函 | 沙箱执行器——隔离代码执行 |
| `semantic_cache.py` | 缓存优化 | 166行2类7函 | 语义缓存——相似查询复用 |
| `slo_review_assistant.py` | 质量审计 | 59行2类3函 | SLO审查助手——合规检查 |
| `task_heartbeat.py` | 基础设施 | 57行2类5函 | 任务心跳——长任务存活检测 |
| `ttl_cleanup_engine.py` | 基础设施 | 117行1类5函 | TTL清理引擎——过期资源回收 |
| `vibe_experiment_tracker.py` | 实验追踪 | 55行1类4函 | 实验追踪——A/B实验结果记录 |
| `warm_hot_gate.py` | 性能优化 | 98行3类6函 | 冷热路径门禁——低延迟路由 |
| `zephyr_logger.py` | 可观测性 | 124行2类7函 | ZephyrLogger——结构化日志独立实现 |

> **状态**: 已落盘，功能实现完整，Python自动发现可导入。**阻塞项**: (1) 无调用入口——未被任何模块import (2) 无单元测试 (3) 未在 project_rules.md 冷启动序列中引用。**下一步**: 按集群分配给对应施工 Phase 选定集成入口 → 接入调用链 → 补充测试。

### 5.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_schemas.py` | ✅ 已实现 | |
| `tests/unit/test_ssot_guard.py` | ✅ 已实现 | |
| `tests/unit/test_capability.py` | ✅ 已实现 | |
| `tests/unit/test_money.py` | ✅ 已实现 | |
| `tests/unit/test_instrument.py` | ✅ 已实现 | |
| `tests/contract/test_import_chain.py` | ✅ 已实现 | Phase 10：8 直接消费者导入链路契约验证（Phase 4 初始 6 → Phase 10 扩展至 8，移除 4 间接消费者） |
| `tests/contract/test_schema_stability.py` | ✅ 已实现 | Phase 4 新增：Task 31字段快照 + TaskCard继承 + 错误层次 + 类型别名 |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 6. 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared-core\blueprint.md` | 本文件 |
| Shared 代码 | `D:\ZephyrAlpha\src\zephyr\shared\` | 跨层共享模型/工具 |
| Core 代码 | `D:\ZephyrAlpha\src\zephyr\core\` | 核心基础设施 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\test_shared.py` + `test_core.py` | 单元测试 |

---

## 7. 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| 所有 L01 模块 | shared 模型引用 | `from zephyr.shared.models import ...` | 所有模块可 import shared 模型 |
| Agent RBAC (MOD-INF-018) | AgentIdentity 模型 | `shared/models.py` → `AgentIdentity` | RBAC 可使用 AgentIdentity |
| Audit Trail (MOD-INF-020) | AuditEvent 模型 | `shared/models.py` → `AuditEvent` | Audit Trail 可使用 AuditEvent |
| Event Bus | 事件总线 | `core/event_bus.py` | 模块间事件通信 |

### 7.1 反向依赖索引 —— 谁依赖 Shared+Core

> 本节是 **AI 施工安全护栏**。修改 shared/core 任一文件前，AI MUST 对照此表确认影响范围。
> 每次新增模块依赖 shared/core 时，MUST 更新此表。

| 消费方 module_id | 消费方名称 | 导入的 shared/core 文件 | 导入量 | 关键依赖点 |
|------|------|------|:---:|------|
| MOD-INF-012 | Database | `schemas.py` (Task/TaskStatus), `paths.py` (DB_PATH/REPO_ROOT) | 2 文件 | SQLite CRUD 继承 Task 模型；DB 路径从 paths SSoT 获取 |
| MOD-INF-008 | Context Engine | `schemas.py`, `paths.py`, `token_utils.py`, `time_utils.py`, `frontmatter_utils.py` | 9 文件 | 上下文装配、Token 预算、时间戳、frontmatter 解析全链路依赖 |
| MOD-INF-009 | Pipeline | `schemas.py`, `paths.py`, `time_utils.py` | 2 文件 | 管线调度器依赖 Task 状态模型 + 路由模型 |
| MOD-INF-007 | Gate Engine | `schemas.py`, `paths.py`, `time_utils.py`, `frontmatter_utils.py` | 3 文件 | 门禁判决依赖 TaskStatus/CheckResult；熔断器依赖配置路径 |
| MOD-INF-010 | Feedback Loop | `schemas.py`, `paths.py`, `time_utils.py`, `observer.py` | 3 文件 | 自进化引擎依赖事件总线 + 指标采集模型 |
| MOD-KB-001 | Knowledge Base | `schemas.py` (KnowledgeEntry/KeCategory), `paths.py`, `content_fingerprint.py`, `frontmatter_utils.py` | 10 文件 | KE 生命周期全链路——ingest/extract/activate/analyze 全部依赖 shared 模型 |
| MOD-INF-013 | MCP Servers | `schemas.py`, `paths.py`, `time_utils.py` | 3 文件 | task_manager/doc_guard/gate_engine 三个 MCP Server 均对接 shared 模型 |
| MOD-INF-014 | LLM Security | `schemas.py`, `paths.py`, `time_utils.py` | 1 文件 | 安全审计日志依赖 AuditEvent 模型 |
| MOD-INF-002 | Runtime Integration | `schemas.py`, `paths.py`, `observer.py`, `capability.py`, `dos_launcher.py` | 5 文件 | 跨层集成——事件总线、能力管控、指令加载、任务调度全链路 |
| MOD-INF-017 | Code Dedup Engine | `paths.py`, `content_fingerprint.py`, `frontmatter_utils.py` | — | 蓝图声明 `depends_on: MOD-INF-016` |
| MOD-INF-019 | Agent Spec | `schemas.py`, `frontmatter_utils.py` | — | Skill 加载器依赖蓝图 frontmatter 解析 |
| — | shared/contracts/ 扩展文件 | `schemas.py`, `paths.py`, `time_utils.py`, `portfolio/money.py`, `market/instrument.py` | 20+ 文件 | backpressure/errors/enforcer/registry 等 20+ 契约文件全部 import shared 基础设施 |

> **AI 安全规则**：修改 `schemas.py` 的 Task 类 → 影响 **至少 10 个消费者模块**（全部 L01 基础设施）。
> 修改 `paths.py` 的路径常量 → 影响 **所有 src/zephyr/ 下代码**。
> 修改 `errors.py` 的异常层次 → 影响 **所有模块的异常处理链**（新增子类安全，修改已有子类谨慎）。
> 修改 `event_schemas.py` 的 Schema → 影响 **所有 observer.emit() 调用点的 payload 结构**。
> 修改 `resilience/retry.py` 的 RetryConfig → 影响 **所有使用 @async_retry 的调用点**。
> 修改 `lifecycle/hooks.py` 的 LifecycleAware Protocol → 影响 **所有实现该 Protocol 的模块**。
> 修改 `flags.py` 的 FeatureFlag 状态 → **AI 不可修改**——运维手动操作 config/。
> 修改 `types.py` 的 NewType → 影响 **所有使用这些别名的函数签名**（mypy 会报错）。
> 修改 `config/loader.py` 的加载逻辑 → 影响 **所有模块的配置加载链路**。
> 修改 `logging.py` 的 ZephyrLogger 接口 → 影响 **所有使用 get_logger() 的模块**。新增日志方法安全，修改/删除已有方法谨慎。
> 修改 `SHARED-QUICKREF.yml` → **AI 可自由更新**——本文件是 AI 导航用的派生文件，无消费者依赖。
> 修改 `testing.py` 工厂函数签名 → 影响 **所有使用工厂函数的测试**。新增参数需向后兼容（keyword-only + 默认值）。
> 修改 `migration.py` 迁移路径 → 影响 **所有依赖 migrate_task() 的模块**。必须注册双向迁移 + 更新 latest_schema_version。
> 修改 `deprecation.py` 的 DeprecatedAPIError → 异常层次变更，影响 **所有 catch 该异常的地方**。
> 修改 `events/dlq.py` 的 DeadLetter 结构 → 影响 **所有依赖 DLQ 的模块**。新增字段安全，修改/删除字段谨慎。
> 修改 `__version__.py` → 影响 **所有调用 check_shared_version() 的模块**。版本号递增安全，格式变更谨慎。
> 修改 `health.py` 的 HealthStatus 枚举 → 影响 **所有 health check consumer**。新增状态值安全，删除/重命名谨慎。

---

## 8. 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 版本号+完整度 | 蓝图补全后更新 |
| 2 | models.py | `D:\ZephyrAlpha\src\zephyr\shared\models.py` | 新增 AgentIdentity/AuditEvent 模型 | MOD-INF-018/020 实现后需新增模型 |

---

## 9. 已知风险与缓解

| # | 风险 | 概率 | 影响 | 缓解策略 |
|---|------|:---:|:---:|---------|
| R1 | models.py 膨胀——所有模块的共享模型集中在一个文件 | 高 | 中 | 按域拆分：models_rbac.py / models_audit.py / models_task.py |
| R2 | 循环依赖——shared ↔ core ↔ 业务模块 | 中 | 高 | 依赖方向严格单向：业务 → shared → core |
| R3 | ~~models.py v0.3.0 破坏性变更——影响所有模块~~ | ~~中~~ | ~~高~~ | ✅ 已解决——v0.4.0 TaskCard 继承 Task 31字段全链路贯通，零破坏 |

---

## 10. 后果（Consequences）

**正面后果**：
- 统一模型定义——所有模块共享同一套 Pydantic 模型，消除类型不一致
- 事件总线——模块间松耦合通信
- 核心基础设施复用——避免每个模块重复实现

**负面后果**：
- shared 模块成为依赖瓶颈——修改 models.py 影响所有模块
- 循环依赖风险——如果依赖方向不严格
- 迁移成本——models.py 破坏性变更需要全项目适配

---

## 11. 施工指引

### 11.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 2 个 Phase（Phase 0 + experimental 已完成） |
| 施工模式 | 扩展（已有 shared + core 基础设施） |
| 核心风险 | ✅ 已消除——models.py v0.3.0 升级完成，零破坏 |

### 11.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | shared/models.py 已实现 | hard | ✅ | ✅ |
| 2 | core/event_bus.py 已实现 | hard | ✅ | ✅ |
| 3 | MOD-INF-018 AgentIdentity 模型定义 | soft | ☐ | ☐ |

### 11.3 实施步骤

#### 步骤 1：✅ models.py v0.3.0 升级（已完成）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3 Core 模块 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\core\models.py` |
| 验收标准 | TaskCard 继承 schemas.py Task（31字段：28业务+3 DB追踪）全链路贯通 |
| G7 检查项 | ✅ 所有现有模块 import 不受影响（17/17 测试通过） |

#### 步骤 2：按域拆分 models

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §9 R1 缓解 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\shared\models_rbac.py` 等 |
| 验收标准 | models.py 仅做 re-export，实际定义在域文件中 |
| G7 检查项 | 所有现有 import 路径不受影响？ |

### 11.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| ~~1~~ | ~~models.py v0.3.0 破坏现有模块~~ | ✅ 已完成，无需回滚——17/17 测试通过，零破坏 |
| 2 | 域拆分导致 import 失败 | 回退到单文件 models.py |

### 11.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 |
|---|--------|---------------|:---:|:---:|
| 1 | ~~models.py v0.3.0~~ | `D:\ZephyrAlpha\src\zephyr\core\models.py` | ✅ | ✅ |
| 2 | models_rbac.py | `D:\ZephyrAlpha\src\zephyr\shared\models_rbac.py` | ☐ | ☐ |
| 3 | models_audit.py | `D:\ZephyrAlpha\src\zephyr\shared\models_audit.py` | ☐ | ☐ |

---

## 12. 已发现未修复盲点（第四轮审计 | 2026-05-05）

> **审计基线**: v0.10.0（48 文件，221 导出）
> **审计语境**: 100% AI 施工 + 1人 + AI 维护 | 依赖氛围编程
> **新增研究来源**: PydanticAI、AgentBudget、LLMCore、Azure AI Agent Server、Boris Cherny 工作流、2026 多智能体编程全景

### 12.1 盲点总览（15 项，4 个优先级）

| 优先级 | 盲点 ID | 缺失能力 | 对应 Phase | 专业对标 |
|:---:|:---:|------|:---:|------|
| 🔴 | B26 | **AI 成本预算与强制熔断**——LLM API 调用无硬性成本限制。Agent 异常循环可在 10 分钟内刷光 $200 配额。`metrics.py` 只有 technical metrics（latency/count），零成本感知 | 11 | AgentBudget、PydanticAI Logfire |
| 🔴 | B27 | **AI 上下文文件自更新基础设施**——AGENTS.md 是静态的，AI 无法把"犯错-学到"写回宪法。Boris Cherny 的 CLAUDE.md 每周更新多次，所有 AI session 共享学习 | 14 | Claude Code CLAUDE.md、@.claude PR review |
| 🔴 | B28 | **Token 计数与上下文预算管理**——`token_utils.py` 已存在于 shared/ 但未被 `__init__.py` 导出。缺少上下文配额分配、预算追踪器、超预算截断策略 | 11 | OpenAI tiktoken、LangChain token counter |
| 🟠 | B29 | **Evals 框架**——有 contract tests（代码正确性），缺 Agent 输出质量系统评估。需要结构化 eval 用例定义、评分 rubrics、回归检测 | 12 | PydanticAI Evals、LangChain eval harness |
| 🟠 | B30 | **Durable Execution（断点续跑）**——长流程 AI task 可能运行数小时。进程崩溃后从头重跑 → 浪费全部已消耗的 token 和成本 | 13 | PydanticAI Durable Execution、Temporal.io |
| 🟠 | B31 | **AI 输出后处理管道**——Boris Cherny 的核心技巧：AI 生成代码后自动跑 lint/format/typecheck，修复最后 10% 质量问题 | 13 | Claude Code PostToolUse hooks、pre-commit |
| 🟠 | B32 | **AI Session 完整审计轨迹**——每次 AI session 的记录（prompts、decisions、tool calls、costs、errors、outcomes）。1人+AI 维护下唯一的学习来源 | 12 | PydanticAI Logfire audit、AgentBudget webhooks |
| 🟡 | B33 | **Multi-Agent 团队编排基座**——Agent role 定义 + task dispatch + result merge。Boris Cherny 三阶段流水线：Opus 规划→Sonnet 实现→Haiku 验证。**2026 深化**: A2A Protocol v1.0（Google Cloud 发起，50+ 合作伙伴）为生产级 agent-to-agent 通信标准——Agent Card 能力发现 + Task 生命周期 + Signed Agent Cards 密码学验证 | 14 | Claude Code Agent Teams、BridgeSwarm、A2A v1.0 |
| 🟡 | B34 | **Agent Skill/Prompt 注册表（共享层）**——`prompt_registry.py` 在 `context_engine/` 而非 shared/。共享层应提供通用 PromptTemplate + Skill 注册接口 | 14 | PydanticAI Agent Skills、MCP prompts |
| 🟡 | B35 | **Model Provider 抽象层**——`api_client.py` 有 HTTP 层统一 client，缺模型语义层（pricing-aware provider、自动 fallback、capability 查询） | 15 | PydanticAI model-agnostic providers、LiteLLM |
| 🟡 | B36 | **上下文窗口压缩/截断策略**——当上下文接近模型上限时，需智能压缩（摘要旧消息、保留关键决策）。共享层应有 TruncationStrategy 接口 | 15 | LangChain summarization、Claude prompt caching |
| 🔵 | B37 | **结构化 Agent 输出质量评分**——不仅是"对不对"，而是"好不好"。Relevance/Accuracy/Completeness 三维评分 + 自动回归 | 15 | PydanticAI Evals scoring rubrics |
| 🔵 | B38 | **配置覆盖链（环境 > YAML > 默认）**——1人+AI 维护时需要清晰的配置优先级 | 15 | Spring Profiles、12-Factor §III |
| 🔵 | B39 | **依赖注入容器**——AI agent 组件化：constructor injection → 组件可替换 → 测试可隔离 | 15 | Spring DI、FastAPI Depends |
| 🔵 | B40 | **AI 代码生成沙箱（共享层统一接口）**——`process_sandbox.py` 在 `llm_security/`，shared/ 应有沙箱接口抽象 | 15 | LLMCore sandboxed execution |

### 12.2 关键洞察

| 维度 | 前三轮盲点 (B1-B25) | 本轮盲点 (B26-B40) |
|------|--------------------|--------------------|
| **关注层** | 通用软件工程基础设施 | **AI 专属工程基础设施** |
| **驱动问题** | "这段逻辑是否可观测/可重试/可迁移？" | **"这个 AI agent 的行为是否可预测/可控制/可审计？"** |
| **对标源** | Google/Netflix/Spring/K8s | **PydanticAI/AgentBudget/Boris Cherny 工作流** |
| **缺失后果** | 代码质量下降、运维困难 | **成本失控、AI 行为不可预测、session 知识丢失** |

### 12.3 能力成熟度阶梯

```
Lv.1 软件工程级 (v0.10.0 ✓):   类型安全 + 错误传播 + 韧性 + 可观测性 + 生产基础
Lv.2 AI 成本可控 (Phase 11):    + B26 成本熔断 + B28 上下文预算
Lv.3 AI 质量可控 (Phase 12):    + B29 Evals框架 + B32 Session审计
Lv.4 AI 流程可控 (Phase 13):    + B30 断点续跑 + B31 后处理管道
Lv.5 AI 团队可控 (Phase 14):    + B27 宪法自愈 + B33 多Agent编排 + B34 Skill注册
Lv.6 AI 架构可控 (Phase 15):    + B35 Provider抽象 + B36 上下文压缩 + B37 输出评分 + B38 配置链 + B39 DI容器 + B40 沙箱
Lv.7 AI 溯源可控 (Phase 16):    + B41 AIBOM + B42 Memory Bank
Lv.8 AI 安全可控 (Phase 17):    + B43 DSPy优化 + B44 StructuredConcurrency + B45 DryRun
Lv.9 AI 韧性可控 (Phase 18):    + B46 Backpressure + B47 Quota + B48 Degradation + B49 KG + B50 Drift
Lv.10 AI 安全纵深 (Phase 19):   + B51 注入防御 + B52 结构化输出 + B53 LLM限流
Lv.11 AI 校验护盾 (Phase 20):   + B54 参数护栏 + B55 缓存策略 + B56 语义降级
```

---

## 13. 已发现未修复盲点（第五轮审计 | 2026-05-05）

> **审计基线**: v0.11.0（49 文件，223 导出）
> **审计语境**: 100% AI 施工 + 1人 + AI 维护 | 依赖氛围编程
> **新增研究来源**: Cisco AIBOM、Trusera ai-bom、DSPy 3.0、Mem0/Memori Memory Bank、Claude Code auto-memory、Azure Multi-Agent Patterns、LangSmith/Galileo LLMOps

### 13.1 盲点总览（10 项）

| 优先级 | 盲点 ID | 缺失能力 | 对应 Phase | 专业对标 |
|:---:|:---:|------|:---:|------|
| 🔴 | B41 | **AIBOM — AI 物料清单与代码溯源** | 16 | Cisco AIBOM v0.5.2、Trusera ai-bom v3.6.0、SPDX 3.0 AI 扩展 |
| 🔴 | B42 | **Memory Bank — Agent 跨会话持久记忆** | 16 | Claude Code auto-memory、Mem0、Memori |
| 🟠 | B43 | **DSPy 风格声明式 Prompt 优化** | 17 | DSPy 3.0、MIPROv2、BetterTogether |
| 🟠 | B44 | **Structured Concurrency — 结构化并发** | 17 | anyio.TaskGroup、trio.Nursery |
| 🟠 | B45 | **Dry-run / Simulation Mode** | 17 | Claude Code /dry-run |
| 🟡 | B46 | **Backpressure Protocol** | 18 | Reactive Streams、RxPY |
| 🟡 | B47 | **Quota Management — 资源配额** | 18 | K8s ResourceQuota |
| 🟡 | B48 | **Graceful Degradation Matrix** | 18 | Netflix Hystrix |
| 🟡 | B49 | **Knowledge Graph Interface** | 18 | Mem0 Graph Memory、Neo4j |
| 🟡 | B50 | **Data Drift Detection** | 18 | Evidently AI、NannyML |

---

## 14. 已发现未修复盲点（第六轮审计 | 2026-05-05）

> **审计基线**: v0.12.0（49 文件，223 导出）
> **审计方法**: 定向探索前几轮未触及维度——AI 安全纵深防御 / LLM 结构化输出强制保障 / LLM API 专属基础设施
> **新增研究来源**: Microsoft FIDES、Entra AI Gateway、Galileo Runtime Protection、Instructor/PydanticAI、Temporal Durable AI Agents、Anthropic prompt caching

### 14.1 盲点总览（6 项）

| 优先级 | 盲点 ID | 缺失能力 | 对应 Phase | 专业对标 |
|:---:|:---:|------|:---:|------|
| 🔴 | B51 | **Prompt Injection Defense — 标签式信任传播** | 19 | Microsoft FIDES (2026.4)、Entra AI Gateway |
| 🔴 | B52 | **Structured Output Guarantee — LLM 输出强制校验+自动重试** | 19 | Instructor、PydanticAI |
| 🟠 | B53 | **LLM API 专属速率限制 + Provider 降级** | 19 | OpenAI tiers、LiteLLM router |
| 🟠 | B54 | **Tool Call Parameter Validation — 工具调用参数护栏** | 20 | agent_rbac input_guard |
| 🟡 | B55 | **Prompt Caching Strategy — 上下文缓存策略** | 20 | Anthropic/OpenAI prompt caching |
| 🟡 | B56 | **Multi-Provider Semantic Equivalence Fallback** | 20 | LiteLLM、OpenRouter |

### 14.2 六轮审计全景

```
轮次1: ████████████ B1-B9   ——大量空白（日志/契约/测试/迁移）
轮次2: ████████     B10-B16 ——中等空白（DLQ/版本/健康）
轮次3: ██████       B17-B25 ——生产缺口（序列化/缓存/幂等）
轮次4: ██████████   B26-B40 ——AI 专属新范式（成本/评估/编排）
轮次5: ████         B41-B50 ——AI 前沿长尾（溯源/记忆/优化）
轮次6: ██           B51-B56 ——安全/校验/API 专项切面
合计:  56 项盲点，25 项已实现 (Phase 0-10)，31 项 planned (Phase 11-20)
```

### 14.3 Shared 层准入边界规则

> 为防止 shared/ 膨胀为垃圾场，新增模块进入 shared/ 必须同时满足：
> 1. 被 ≥2 个 L01 模块消费（或预期会被消费）
> 2. 不绑定任何特定业务域
> 3. 接口粒度 ≤ Protocol/dataclass/Enum（不包含重量级实现）

---

## 15. 第七轮审计结论 —— 审计已达终点（2026-05-05）

> **审计方法**: 三方向最终交叉验证——A2A v1.0 Agent 间通信 / OPA Policy as Code 声明式治理 / Agent CI/CD Evaluation Pipeline
> **核心结论**: 无新增独立盲点

### 15.1 三个维度的诚实判断

| 探索维度 | 2026 行业实况 | 是否新盲点？ | 判断理由 |
|------|------|:---:|------|
| **A2A Protocol v1.0** | Google Cloud 发起，8 大公司技术委员会，50+ 技术合作伙伴。生产就绪 Agent Card 能力发现 + Task 生命周期 + Signed Agent Cards | **否——B33 深化** | B33 已 planned Phase 14。A2A v1.0 是 B33 实现时的具体对标标准，已写入 B33 备注 |
| **OPA Policy as Code** | CNCF 毕业项目，Rego 声明式策略语言。策略决策与执行解耦 | **否——实现选择** | agent_rbac 模块已有七层 PermissionGuard。OPA 是具体技术选项，非 shared/ 层抽象 |
| **Agent CI/CD Eval Pipeline** | Galileo 2026：40% agentic AI 项目因缺评估基础设施被取消。三阶段质量门 | **否——B29 延伸** | 先有 Evals 框架（B29 Phase 12）才能谈 CI/CD 集成。是 Phase 22+ 的自然延伸 |

### 15.2 七轮审计全景终局

```
轮次1: ████████████ B1-B9   ——大量空白（日志/契约/测试/迁移）
轮次2: ████████     B10-B16 ——中等空白（DLQ/版本/健康）
轮次3: ██████       B17-B25 ——生产缺口（序列化/缓存/幂等）
轮次4: ██████████   B26-B40 ——AI 专属新范式（成本/评估/编排）
轮次5: ████         B41-B50 ——AI 前沿长尾（溯源/记忆/优化）
轮次6: ██           B51-B56 ——安全/校验切面（注入防御/输出保障）
轮次7: ·            ——边际确认（无新增——已有盲点深化）
合计:  56 项盲点，25 项已实现 (Phase 0-10)，31 项 planned (Phase 11-20)
```

### 15.3 审计终局声明

> **七轮审计后，MOD-INF-016 Shared+Core 蓝图已达到氛围编程语境下的顶尖水准。**
>
> 对标三维交集——Google Monorepo shared/ 基础设施层 × DDD Shared Kernel × 2026 AI 工程前沿——56 项盲点全覆盖。
>
> **剩余的不是"盲点"，而是实现深度问题**: 把 31 项 planned 盲点从 Phase 11 推进到 Phase 20。
>
> **下一步建议**: 停止审计，开始施工 Phase 11。

---

## 16. ADR — 架构决策记录（Architecture Decision Records）

> 本节记录 Shared+Core 的关键架构决策及其 trade-off。AD 格式参照 adr.github.io。

### AD-001: Pydantic V2 作为跨层数据契约基座

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | 所有跨层数据模型使用 Pydantic V2 BaseModel，不用 Python dataclasses 或 raw dict |
| **原因** | ① 自动序列化/反序列化（to_dict/from_dict 由 serialization.py 统一；Decimal→str 自动处理）② 运行时类型校验（避免 dict key typo 在生产崩掉）③ 与 FastAPI/ShieldLM/PydanticAI 生态正交兼容 ④ AI 施工友好——Pydantic schema 即文档，AI 不需要额外查字段含义 |
| **代价** | ① Pydantic V2 导入约增加 50ms 冷启动 ② 跨模块模型耦合（改 Task 影响 10+ 消费者——已由 §7.1 反向依赖索引缓解）③ Pydantic 版本升级可能 BREAKING——由 `check_shared_version()` 运行时版本协商兜底 |
| **替代方案** | Python dataclasses（缺自动校验 / JSON 序列化需手写）；TypedDict（缺校验 / 工具链支持弱）；Protocol Buffers（过度工程 / 无生产需求） |

### AD-002: Shared + Core 合并为单一蓝图

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | MOD-INF-016 同时涵盖 `src/zephyr/shared/` 和 `src/zephyr/core/`，不拆分为两个独立蓝图 |
| **原因** | ① 两者体积均较小（shared 46 文件 + core 3 文件 = 49 文件——独立蓝图的最低门槛是 30+ 文件）② 强耦合——core/models.py 继承 shared/schemas.py，拆分后 AI 需同时读两份蓝图做 cross-reference ③ 两者均为跨层基础设施，功能域一致 |
| **拆分触发条件** | shared 文件数 >80 或 core 模块独立形成 3+ 个子系统——届时拆分 |
| **替代方案** | 独立两个蓝图（当前体积下 over-engineering——AI session 冷启动需多读一份 blueprint.md + 多维护一份 registry entry） |

### AD-003: Resilience 组件使用纯内存（非 SQLite 持久化）

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | `shared/resilience/` 的 CircuitBreaker/Retry/FallbackChain 全部纯内存，不持久化 |
| **原因** | ① 持久化版在 `gates/circuit_breaker.py`——SQLite + 门禁集成。两版分工：shared 版给 AI agent 内部重试（零依赖、快速恢复），gates 版给生产请求门禁（持久化、可审计）② 纯内存避免依赖 SQLite——shared 是最底层，不应有 DB 依赖 ③ 熔断状态半衰期短（30s）——持久化收益低 |
| **代价** | 进程重启 → 熔断状态丢失 → burst 期间可能重复请求已熔断的服务（由 retry + timeout 兜底） |

### AD-004: Prompt/Skill 注册表不在 shared/ 而在 context_engine/

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | B34 标记的 Skill/Prompt 注册表缺在 shared/——但当前 `prompt_registry.py` 放在 `context_engine/` 是合理的设计决策，非盲点 |
| **原因** | ① Prompt 模板与业务语义紧耦合（"为 Task 生成执行计划" vs "为 KB entry 生成摘要"）——不适合作为 shared/ 通用抽象 ② Skill 注册与 Agent Identity 强绑定——归属 agent_rbac 或 context_engine ③ shared/ 只提供通用 PromplTemplate/Skill Schema（Pydantic 模型），具体注册表由业务模块承载 |
| **shared/ 职责** | 当 context_engine 和 agent_rbac 和 feedback_loop 三个模块都需要 `PromptTemplate` / `SkillDefinition` 数据模型时，将其提升到 shared/ |

### AD-005: SHARED-QUICKREF.yml 是 AI 派生文件（非 SSoT）

| 项目 | 内容 |
|------|------|
| **状态** | accepted |
| **决策** | `SHARED-QUICKREF.yml` 是从 `__init__.py` `__all__` 派生出的 AI 快速导航文件，无消费者依赖 |
| **原因** | ① AI session 冷启动时读 QUICKREF 比 grep `__all__` 快 ② 包含 anti_patterns / entry_point 等 AI 专属信息——`__all__` 不承载 ③ 是 blueprint.md 的速览版本——AI 读完 blueprint 后对照 QUICKREF 快速定位 |
| **更新策略** | 每次新增 shared/ 模块 → `__init__.py` `__all__` → QUICKREF（两步更新）。QUICKREF 落后 `__all__` ≤1 个 session 可接受（AI 查 QUICKREF 后仍会 verify `__init__.py`） |

---

## 17. Consumer Onboarding Guide — 新模块接入指南

> **面向**: 下一个 AI session 冷启动 + 新 L01 模块接入 shared/

### 17.1 最小接入（3 行 import 即用）

```python
from zephyr.shared.schemas import Task, TaskStatus       # 所有模块都需要
from zephyr.shared.paths import REPO_ROOT, DB_PATH       # 路径从 SSoT 获取
from zephyr.shared.logging import get_logger             # 结构化日志 + trace_id 传播

logger = get_logger(__name__)
```

### 17.2 shared/ 按消费场景的分层

| 层级 | 模块 | 适用场景 | 示例 |
|:---:|------|------|------|
| L0 必选 | schemas, paths, logging | 所有模块 | `from zephyr.shared.schemas import Task` |
| L1 常用 | time_utils, token_utils, frontmatter_utils, errors, types | 需要时间/Token/Frontmatter/异常/类型安全的模块 | `from zephyr.shared.time_utils import now_utc` |
| L2 生产 | serialization, api_client, secrets, cache, limiter, idempotency, context, metrics, pagination, env, lock, outbox, schema_registry | 对外 API / 持久化 / 性能敏感的模块 | `from zephyr.shared.cache import MemoryCache` |
| L3 韧性 | resilience/*, lifecycle/* | 需要重试/熔断/生命周期管理的模块 | `from zephyr.shared.resilience.retry import async_retry` |
| L4 AI 专属 | （Phase 11-20 施工完成后） | AI agent 模块 | `from zephyr.shared.cost_budget import CostBudget` |
| facade | contracts/* | 需要跨层结构化数据交换的模块 | `from zephyr.shared.contracts.market.instrument import Instrument` |

### 17.3 不做什么（Anti-patterns）

| ❌ 不要 | ✅ 应该 |
|------|------|
| `from zephyr.shared import *` | 显式 import 需要的符号——AI session 和 mypy 都需要知道 "这个模块用了 shared 的哪些" |
| 直接修改 `task.status = TaskStatus.DONE` | 用 `task.mark_completed()` 等语义化方法——由 models.py v0.4.0 提供 |
| `datetime.utcnow()` 裸用 | `from zephyr.shared.time_utils import now_utc`——唯一 UTC 入口，可测试 |
| 在模块中定义自己的路径常量 | `from zephyr.shared.paths import REPO_ROOT, DB_PATH`——paths.py 是 SSoT |
| 在模块中自己写 `logger = logging.getLogger()` | `from zephyr.shared.logging import get_logger`——trace_id 自动传播 |

### 17.4 版本兼容性策略

| shared/ 版本变更类型 | 影响 | 消费者需做什么 |
|------|------|------|
| PATCH (0.14.X) | 新增文件/新增导出/修复 bug——完全向后兼容 | 无需操作 |
| MINOR (0.X.0) | 新增文件≥5 / 新增子模块——向后兼容，新增可选符号 | AI session 可选择性采用新模块 |
| MAJOR (X.0.0) | 破坏 Task 31字段 / 删除导出 / 重命名模块 | 全部 L01 模块 MUST 同步升级——check_shared_version() 运行时阻断不兼容版本 |

---

## 18. Blueprint Quality Self-Assessment — 蓝图质量自评

> **评估标准**: 蓝图作为 AI 独立施工规格说明书的质量。100% AI 施工 + 1人+AI 维护语境。

### 18.1 可实施性评分（每个 planned phase）

| Phase | 盲点 | 蓝图细节完备度 | AI 独立施工评分 | 缺口 |
|:---:|------|:---:|:---:|------|
| 11 | B26, B28 | 🟢 详细 | 8/10 | B28 token_utils.py 已存在——施工复杂度低。B26 成本预算需明确 provider 定价数据来源 |
| 12 | B29, B32 | 🟢 详细 | 8/10 | B29 Evals 框架需定义 eval 用例格式。B32 Session audit 需明确 JSONL 格式 |
| 13 | B30, B31 | 🟡 中等 | 7/10 | B30 Durable Execution 需明确 Worker/Activity 抽象层。B31 后处理管道需 hook 点设计 |
| 14 | B27, B33, B34 | 🟡 中等 | 6/10 | B33 Multi-Agent 编排最复杂——需在蓝图补充 AgentCard / TaskDispatch / ResultMerge 三个 Protocol |
| 15 | B35-B40 | 🟡 中等 | 7/10 | 6 项规模适中，但 B39 DI 容器需 explicit constructor injection 约定 |
| 16 | B41, B42 | 🟢 详细 | 8/10 | AIBOM/Memory Bank 均为接口定义级——200-300 行 Protocol + dataclass |
| 17 | B43-B45 | 🟡 中等 | 7/10 | B43 DSPy 声明式优化——声明式 Signature 语法设计是关键决策 |
| 18 | B46-B50 | 🟡 中等 | 7/10 | 5 项但 KG 接口 + Drift 检测可能不满足 shared/ 准入规则——需再判断 |
| 19 | B51-B53 | 🟡 中等 | 7/10 | B51 Prompt 注入防御——IFC 标签系统需 Microsoft FIDES 参考实现 |
| 20 | B54-B56 | 🟢 详细 | 8/10 | 3 项均为薄封装（100-200 行接口定义）|

### 18.2 蓝图漂移风险自评

| 风险 | 当前评分 | 缓解 |
|------|:---:|------|
| 蓝图声称的 49 文件 vs 磁盘实际 | 🟢 低 | §5 文件清单 49 文件全 ✅，IC1/IC2 已修复 |
| `__all__` 导出数 vs QUICKREF | 🟢 低 | 当前 223 导出——Phase 11-20 新增后需同步更新 |
| Phase 0-10 代码 vs Phase 11-20 planned | N/A | planned phases 无磁盘代码——零漂移风险 |
| blueprint.md vs SSoT YAML (b_shared.yaml/b_core.yaml) | 🟡 中 | blueprint.md 是真源派生的施工文档——YAML 是 canon。两者版本号应同步 |

### 18.3 蓝图完整度矩阵

| 维度 | 状态 | 评分 |
|------|:---:|:---:|
| 文件清单（§5） | ✅ 49 文件全部 indexed | 10/10 |
| 盲点覆盖（§12-§15） | ✅ 56 盲点 + 审计终局 | 10/10 |
| 施工阶段（§4） | ✅ Phase 0-20 全部 planned | 10/10 |
| 依赖追踪（§7.1） | ✅ 12 消费者模块全部 traced | 9/10 |
| AI 安全护栏（§7.1 底部） | ✅ 按文件/子模块粒度 | 10/10 |
| 架构决策（§16 ADR） | 🟢 新增——5项 AD | 7/10 ← 尚缺 |
| 消费者指南（§17 Onboarding） | 🟢 新增 | 7/10 ← 尚缺 |
| 蓝图质量自评（§18 本节） | 🟢 新增 | 6/10 ← 需每个 Phase 施工后更新 |
| 测试策略（§19 待施工） | 🟡 待补充 | — |

---

## 19. Shared Layer Testing Strategy — 共享层测试策略

> **目标**: shared/ 作为全系统基础设施，其测试覆盖直接影响所有 L01 模块的施工信心。

### 19.1 测试分层

| 层 | 范围 | 目标覆盖率 | 当前状态 |
|:---:|------|:---:|:---:|
| **单元测试** | 每个 shared/*.py 的纯函数/类——不依赖外部（无 DB、无 HTTP、无文件系统） | ≥90% | 7 文件已测试（schemas/ssot_guard/capability/money/instrument + contract tests）——**缺 42 文件** |
| **集成测试** | shared/ 子模块间的交互——e.g., `context.py` + `logging.py` trace_id 传播 → 日志输出包含 trace_id | ≥70% | 未开始 |
| **契约测试** | 6 消费者模块 import shared → 所有符号可成功 import + Task 31字段稳定性快照 | 100% | ✅ 29/29 通过（§5.2）。每次新增 shared 符号 MUST 更新 `test_import_chain.py` |
| **性能回归测试** | cache/limiter/serializer 的操作耗时基准——e.g., `MemoryCache.put()` < 10µs、`to_json()` 100KB < 50ms | P95 不退化 | 未开始 |
| **漂移检测** | 蓝图 §5 声称的 49 文件 vs 磁盘实际 vs `__init__.py` `__all__` | 三者一致 | ✅ 本轮修复 IC1/IC2 后一致 |

### 19.2 单元测试优先级（TOP 10 缺测试文件）

> 按"被消费者引用次数"×"修改频率"排序

| 优先级 | 文件 | 被引用次数 | 建议第一个测试 |
|:---:|------|:---:|------|
| 1 | `cache.py` | — | `test_cache_ttl_expiry()` |
| 2 | `limiter.py` | — | `test_token_bucket_consume()` |
| 3 | `serialization.py` | — | `test_to_dict_decimal_handling()` |
| 4 | `idempotency.py` | — | `test_idempotency_key_determinism()` |
| 5 | `context.py` | — | `test_contextvars_propagation()` |
| 6 | `metrics.py` | — | `test_counter_thread_safety()` |
| 7 | `api_client.py` | — | `test_timeout_retry_composition()` |
| 8 | `pagination.py` | — | `test_cursor_pagination()` |
| 9 | `lock.py` | — | `test_memory_lock_lease_expiry()` |
| 10 | `outbox.py` | — | `test_outbox_polling_publisher()` |

### 19.3 性能回归基准（建议值）

| 操作 | P50 | P95 | P99 |
|------|-----|-----|-----|
| `MemoryCache.put()` | <5µs | <10µs | <20µs |
| `TokenBucketLimiter.consume()` | <1µs | <5µs | <10µs |
| `to_json(obj, 100KB)` | <10ms | <50ms | <100ms |
| `IdempotencyStore.start(key)` | <5µs | <10µs | <15µs |
| `MetricsRegistry.get_or_create_counter()` | <1µs | <3µs | <5µs |

### 19.4 测试维护策略

| 触发事件 | 操作 |
|------|------|
| 新增共享模块 | 新增单元测试 + 更新 `test_import_chain.py` + 更新 QUICKREF |
| 修改已有模块签名 | MUST 运行 `test_import_chain.py`（跨模块 import）+ `test_schema_stability.py`（Task 31字段快照） |
| 性能敏感模块变更（cache/limiter/serializer） | MUST 运行性能回归 + 比较 P50/P95 |
| 蓝图 Phase 11-20 每完成一个 | MUST 新增对应测试 + 更新 §19.2 优先级表 + 更新蓝图完整度矩阵（§18.3）

---

## 附录 A：版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.1.0 | 2026-05-03 | 初版：12文件清单，Shared+Core合并蓝图 |
| 0.1.1 | 2026-05-05 | Phase 0 蓝图漂移修正：12→17文件、§2 补全5文件职责描述、paths.py DB_PATH 迁移至 data/、§7.1 新增反向依赖索引 |
| 0.1.2 | 2026-05-05 | Phase 1 施工：新建 errors.py（ZephyrBaseError+12子类）、constants.py（22枚举集中re-export）、events/event_schemas.py（5事件体Pydantic Schema）|
| 0.2.0 | 2026-05-05 | Phase 2 施工：新建 resilience/(retry/circuit_breaker/fallback)、lifecycle/hooks.py、flags.py。韧性基座+生命周期+FeatureFlag 三大体系。25文件清单。 |
| 0.3.0 | 2026-05-05 | Phase 3 施工：新建 types.py（13 NewType）、diff_utils.py、file_utils.py（原子写+备份+rollback）、config/loader.py（YAML + Pydantic 校验）。29文件清单。 |
| 0.4.0 | 2026-05-05 | 🎉 Backlog 清零：models.py v0.3.0 升级完成——TaskCard 继承 schemas.py Task（31字段：28业务+3 DB追踪）全链路贯通。17/17 测试通过，零破坏。construction_progress → completed，完整度 100%。 |
| 0.5.0 | 2026-05-05 | Phase 4 施工：新建 logging.py（结构化日志 ZephyrLogger + trace_id 传播）、SHARED-QUICKREF.yml（AI 零歧义快速参考）、tests/contract/（契约测试框架——6 消费者导入验证 + Schema 稳定性快照）。31 文件清单。29/29 契约测试通过。 |
| 0.6.0 | 2026-05-05 | Phase 5 施工：新建 testing.py（7 工厂函数——Task/AuditReport/KnowledgeEntry/FailurePattern/HandoffPackage）、migration.py（BFS 最短路径版本化迁移）、deprecation.py（@deprecated 装饰器 + warn/strict/silent 三模式）。34 文件清单。 |
| 0.7.0 | 2026-05-05 | Phase 6 施工：新建 events/dlq.py（死信队列——SQLite 持久化 + 定时重试 + 保留策略）、__version__.py（PEP 440 版本常量 + check_shared_version() 运行时校验）、health.py（聚合健康检查——ALL_HEALTHY/DEGRADED/UNHEALTHY + JSON 可序列化）。37 文件清单。 |
| 0.10.0 | 2026-05-05 | Phases 7-10 施工：新建 serialization.py（统一序列化——Decimal→str, datetime→ISO 8601）、api_client.py（统一API Client——超时/重试/熔断/metrics）、secrets.py（Secrets管理——Env/DotEnv Provider + sanitize）、cache.py（缓存抽象——TTL+LRU驱逐）、limiter.py（Token Bucket速率限制器）、idempotency.py（幂等性infrastructure——Stripe 24h TTL对齐）、context.py（结构化RequestContext——trace_id/span_id/tenant/agent）、metrics.py（Metrics Registry——Counter/Gauge/Histogram+Prometheus text）、pagination.py（统一分页——Page[T]/CursorPage[T]）、time_utils.py（时间工具——now_utc/freeze_time/parse_iso）、env.py（环境检测——is_dev/is_prod/is_test）、lock.py（分布式锁——MemoryLock+async context manager）、outbox.py（事务性Outbox——polling publisher+at-least-once）、schema_registry.py（Schema Registry——集中式版本编目+兼容性查询）。48 文件清单。 |
| 0.10.1 | 2026-05-05 | 第四轮盲点审计：发现 15 项 AI 专属基础设施盲点（B26-B40）。新增 §12 盲点清单 + §2.9 AI 基础设施 planning + §4 Phases 11-15 planned。 |
| 0.11.0 | 2026-05-05 | 第五轮盲点审计：发现 10 项 AI 工程前沿盲点（B41-B50）。新增 §13 盲点清单 + §4 Phases 16-18 planned。修复蓝图漂移：blueprint_scorer.py 入场（49文件清单）+ SHARED-QUICKREF v0.11.0 全量更新。新增 Shared 层准入边界规则。 |
| 0.12.0 | 2026-05-05 | 第六轮盲点审计：发现 6 项 AI 安全/校验专项盲点（B51-B56）。新增 §14 盲点清单 + §4 Phases 19-20 planned + 能力成熟度阶梯 Lv.10-11。修复前后轮间 stale 值漂移。 |
| 0.13.0 | 2026-05-05 | 第七轮审计结论——审计已达终点。三方向交叉验证（A2A v1.0 / OPA / Agent CI/CD Eval Pipeline）确认无新增独立盲点。B33 深化为 A2A v1.0 标准。新增 §15 审计终局声明。七轮全景总览。 |
| 0.14.0 | 2026-05-05 | 第八轮审计——蓝图结构补充。新增 §16 ADR（5 项架构决策记录）+ §17 Consumer Onboarding Guide（消费者接入指南）+ §18 Blueprint Quality Self-Assessment（蓝图质量自评）+ §19 Testing Strategy（共享层测试策略）。修复 IC1（§2 标题 8→9 子模块, 45→46 文件）+ IC2（§5 标题 48→49 文件）。蓝图从"代码盲点全覆盖"升级为"蓝图文档结构化完整"。 |

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.14.0 | 第八轮蓝图结构补充：§16 ADR + §17 Onboarding + §18 质量自评 + §19 测试策略。修复 IC1+IC2。蓝图结构化完整。 |
| 2026-05-05 | 0.13.0 | 第七轮审计终点：三方向验证无新盲点。B33 深化 A2A v1.0。§15 审计终局声明。建议停止审计开始施工。 |
| 2026-05-05 | 0.12.0 | 第六轮审计：发现 B51-B56（6 项 AI 安全/校验盲点）。§14 盲点清单 + Phases 19-20 planned。 |
| 2026-05-05 | 0.11.0 | 第五轮审计：发现 B41-B50（10 项 AI 前沿盲点）。§13 盲点清单 + Phases 16-18 planned。漂移修复+准入规则。 |
| 2026-05-05 | 0.10.1 | 第四轮审计：发现 B26-B40（15 项 AI 专属盲点）。§12 盲点清单 + Phases 11-15 planned。 |
| 2026-05-05 | 0.10.0 | Phases 7-10 完成：11新模块(序列化/API Client/Secrets/缓存/速率限制/幂等/上下文/Metrics/分页/时间/环境/锁/Outbox/Schema Registry)，37→48文件。 |
| 2026-05-05 | 0.7.0 | Phase 6 完成：dlq + __version__ + health。37文件。 |
| 2026-05-05 | 0.6.0 | Phase 5 完成：testing + migration + deprecation。34文件。 |
| 2026-05-05 | 0.5.0 | Phase 4 完成：logging + SHARED-QUICKREF + 契约测试。31文件。29/29通过。 |
| 2026-05-05 | 0.4.0 | 🎉 Backlog 清零：models.py v0.3.0 升级完成。17/17 测试通过。100% 完成。 |
| 2026-05-05 | 0.3.0 | Phase 3 施工：新建 types/diff/file_utils/config。29文件清单。 |
| 2026-05-05 | 0.2.0 | Phase 2 施工：新建 resilience、lifecycle、flags。25文件清单。+ 补全标准模板六项。 |
| 2026-05-05 | 0.1.2 | Phase 1 施工：新建 errors.py、constants.py、events/event_schemas.py。20文件清单。 |
| 2026-05-05 | 0.1.1 | Phase 0 蓝图漂移修正。 |
| 2026-05-03 | 0.1.0 | 初始创建——合并 Shared YAML + Core YAML。 |


---

## 施工落盘确认（2026-05-07 审计）
| 维度 | 状态 |
|------|------|
| construction_progress | phase_10_complete（Phase 1-10 全部完成，49文件已实现） |
| 源码路径 | `src/zephyr/shared/ + src/zephyr/core/` |
| 源码文件数 | 190 个 .py/.yaml |
| 测试路径 | `tests/unit/ (shared+core) + tests/architecture/` |
| 配置文件 | `config/capabilities.yaml + config/ai_capability_matrix.yaml` |
| 关键入口 | `shared.protocols.* + core.models.* + core.config.*` |

## 已知技术债务（2026-05-08 审计 · Session-20260508-001）

### TD-SHARED-001: 37文件发散副本（Phase 11 待修）

**问题**: `src/zephyr/shared/` 下 37 个模块同时存在于顶层目录和子目录，
且内容是**不同（发散）副本**，非 byte-identical 也非 re-export wrapper。

**风险**:
- 修改一个版本时另一个不会同步 → 行为不一致
- 新 AI 不知道该用哪个路径 → 认知混乱
- 典型案例: `shared/cache.py`(5595B) ≠ `shared/infra/cache.py`(5560B)

**规范路径策略（Phase 11 施行）**:
| 顶层文件 | 规范子目录路径 | 处置 |
|----------|--------------|------|
| `cache.py` | `infra/cache.py` | 顶层改为 re-export wrapper |
| `metrics.py` | `observability/metrics.py` | 顶层改为 re-export wrapper |
| `logging.py` | `observability/logging.py` | 顶层改为 re-export wrapper |
| `health.py` | `observability/health.py` | 顶层改为 re-export wrapper |
| `token_utils.py` | `observability/token_utils.py` | 顶层改为 re-export wrapper |
| `tracing.py` | `observability/tracing.py` | 顶层改为 re-export wrapper |
| `idempotency.py` | `infra/idempotency.py` | 顶层改为 re-export wrapper |
| `limiter.py` | `infra/limiter.py` | 顶层改为 re-export wrapper |
| `lock.py` | `infra/lock.py` | 顶层改为 re-export wrapper |
| `observer.py` | `infra/observer.py` | 顶层改为 re-export wrapper |
| `outbox.py` | `infra/outbox.py` | 顶层改为 re-export wrapper |
| `serialization.py` | `io/serialization.py` | 顶层改为 re-export wrapper |
| `content_fingerprint.py` | `io/content_fingerprint.py` | 顶层改为 re-export wrapper |
| `file_utils.py` | `io/file_utils.py` | 顶层改为 re-export wrapper |
| `frontmatter_utils.py` | `io/frontmatter_utils.py` | 顶层改为 re-export wrapper |
| `paths.py` | `io/paths.py` | 顶层改为 re-export wrapper |
| `errors.py` | `foundation/errors.py` | 顶层改为 re-export wrapper |
| `constants.py` | `foundation/constants.py` | 顶层改为 re-export wrapper |
| `flags.py` | `foundation/flags.py` | 顶层改为 re-export wrapper |
| `types.py` | `foundation/types.py` | 顶层改为 re-export wrapper |
| `deprecation.py` | `foundation/deprecation.py` | 顶层改为 re-export wrapper |
| `env.py` | `foundation/env.py` | 顶层改为 re-export wrapper |
| `secrets.py` | `security/secrets.py` | 顶层改为 re-export wrapper |
| `capability.py` | `security/capability.py` | 顶层改为 re-export wrapper |
| `ssot_guard.py` | `security/ssot_guard.py` | 顶层改为 re-export wrapper |
| `migration.py` | `utils/migration.py` | 顶层改为 re-export wrapper |
| `pagination.py` | `utils/pagination.py` | 顶层改为 re-export wrapper |
| `time_utils.py` | `utils/time_utils.py` | 顶层改为 re-export wrapper |
| `context.py` | `utils/context.py` | 顶层改为 re-export wrapper |
| `testing.py` | `utils/testing.py` | 顶层改为 re-export wrapper |
| `diff_utils.py` | `utils/diff_utils.py` | 顶层改为 re-export wrapper |
| `blueprint_scorer.py` | `utils/blueprint_scorer.py` | 顶层改为 re-export wrapper |
| `schemas.py` | `schema/schemas.py` | 顶层改为 re-export wrapper |
| `schema_registry.py` | `schema/schema_registry.py` | 顶层改为 re-export wrapper |
| `api_client.py` | `api/api_client.py` | 顶层改为 re-export wrapper |
| `dos_launcher.py` | `api/dos_launcher.py` | 顶层改为 re-export wrapper |

**施行方法**: 每个顶层文件替换为 `from zephyr.shared.<subdir>.<module> import *` wrapper。
**不影响消费者**: 316 处现有引用全部保持兼容。

### TD-SHARED-002: `__init__.py` 导入路径不一致（已部分修复）

`__init__.py` 中 ~33 个 import 使用顶层路径（`from zephyr.shared.cache import`），
~16 个使用规范子目录路径（`from zephyr.shared.api.api_client import`）。
TD-SHARED-001 修复完成后，统一改为子目录路径。
