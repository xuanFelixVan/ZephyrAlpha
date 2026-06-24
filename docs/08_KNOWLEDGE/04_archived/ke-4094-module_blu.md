---
module_id: KE-3940
title: 16.4 待施工任务
category: module_blueprint
---

# 16.4 待施工任务

16.4 待施工任务

| # | 任务 | 优先级 | 预估工时 | 依赖 |
|---|------|:---:|:---:|------|
| T-DB-001 | 补全 `test_database_manager.py`——连接池/健康检查/备份/恢复/WAL checkpoint | P1 | 2h | 无 |
| T-DB-002 | 补全 `test_audit_schema.py`——AuditQuery/补偿事件/Schema漂移检测 | P1 | 1.5h | 无 |
| T-DB-003 | 补全 `test_query_metrics.py`——PercentileTracker/track装饰器/slow_query/单例 | P2 | 1h | 无 |
| T-DB-004 | 修复 b_db.yaml SSoT 漂移——增补3个缺失文件(database_manager/audit_schema/query_metrics) | P1 | 0.5h | 无 |
| T-DB-005 | `database_manager` 增加 `verify_backup()`——定期测试恢复能力 | P2 | 1h | T-DB-001 |
| T-DB-006 | `database_manager` 增加 `dead_letter_queue`——失败的写入入队重试 | P2 | 2h | 无 |
| T-DB-007 | `query_metrics` 增加 `EXPLAIN QUERY PLAN` 记录——用于慢查询优化 | P2 | 1h | 无 |
| T-DB-008 | `sqlite_schema` 增加 `migration_dry_run`——迁移预览模式（不实际执行） | P2 | 1h | 无 |
| T-DB-009 | `database_manager` 增加 Prometheus/OpenTelemetry metrics 导出 | P2 | 2h | MOD-INF-015 |
| T-DB-010 | `task_repo` 增加 FTS5 全文搜索——任务描述/标题搜索 | P3 | 3h | 无 |
| T-DB-011 | `database_manager` 增加 `connection_leak_detector`——检测未归还的连接 | P2 | 1.5h | 无 |
