---
module_id: KE-4132
title: 5.1 源码文件
category: module_blueprint
---

# 5.1 源码文件

5.1 源码文件

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
| `src/zephyr/shared/idempotency.py` | ✅ 已实现 | Phase 8 新增：幂等性 infrastructure——Stripe 24h TTL
