---
module_id: KE-2420---------------shared-core-005
status: active
title: 7.1 反向依赖索引 —— 谁依赖 Shared+Core
category: module_blueprint
ttl: permanent
---

# 7.1 反向依赖索引 —— 谁依赖 Shared+Core

7.1 反向依赖索引 —— 谁依赖 Shared+Core

> 本节是 **AI 施工安全护栏**。修改 shared/core 任一文件前，AI MUST 对照此表确认影响范围。
> 每次新增模块依赖 shared/core 时，MUST 更新此表。

| 消费方 module_id | 消费方名称 | 导入的 shared/core 文件 | 导入量 | 关键依赖点 |
|------|------|------|:---:|------|
| MOD-DATABASE | Database | `schemas.py` (Task/TaskStatus), `paths.py` (DB_PATH/REPO_ROOT) | 2 文件 | SQLite CRUD 继承 Task 模型；DB 路径从 paths SSoT 获取 |
| MOD-CONTEXT_ENGINE | Context Engine | `schemas.py`, `paths.py`, `token_utils.py`, `time_utils.py`, `frontmatter_utils.py` | 9 文件 | 上下文装配、Token 预算、时间戳、frontmatter 解析全链路依赖 |
| MOD-INF-009 | Pipeline | `schemas.py`, `paths.py`, `time_utils.py` | 2 文件 | 管线调度器依赖 Task 状态模型 + 路由模型 |
| MOD-GATE_ENGINE | Gate Engine | `schemas.py`, `paths.py`, `time_utils.py`, `frontmatter_utils.py` | 3 文件 | 门禁判决依赖 TaskStatus/CheckResult；熔断器依赖配置路径 |
| MOD-FEEDBACK_LOOP | Feedback Loop | `schemas.py`, `paths.py`, `time_utils.py`, `observer.py` | 3 文件 | 自进化引擎依赖事件总线 + 指标采集模型 |
| MOD-KB-001 | Knowledge Base | `schemas.py` (KnowledgeEntry/KeCategory), `paths.py`, `content_fingerprint.py`, `frontmatter_utils.py` | 10 文件 | KE 生命周期全链路——ingest/extract/activate/analyze 全部依赖 shared 模型 |
| MOD-INF-013 | MCP Servers | `schemas.py`, `paths.py`, `time_utils.py` | 3 文件 | task_manager/doc_guard/gate_engine 三个 MCP Server 均对接 shared 模型 |
| MOD-LLM_SECURITY | LLM Security | `schemas.py`, `paths.py`, `time_utils.py` | 1 文件 | 安全审计日志依赖 AuditEvent 模型 |
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
> 修改 `events/dlq.py` 的 DeadLetter
