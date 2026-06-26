---
module_id: KE-1769
title: 2.2 shared-infra（共享基础设施）
category: module_blueprint
ttl: permanent
---

# 2.2 shared-infra（共享基础设施）

2.2 shared-infra（共享基础设施）

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
