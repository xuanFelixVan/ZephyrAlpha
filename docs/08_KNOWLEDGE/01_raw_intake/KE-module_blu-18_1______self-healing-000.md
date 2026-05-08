---
module_id: KE-module_blu-18_1______self-healing-000
title: 18.1 自愈设计（Self-Healing）
category: module_blueprint
---

# 18.1 自愈设计（Self-Healing）

18.1 自愈设计（Self-Healing）

| 场景 | 自动检测 | 自动修复 | 人工介入条件 |
|------|:---:|:---:|------|
| WAL 文件无限增长 | wal_autocheckpoint=4096 | PostgreSQL式自动checkpoint | WAL > 100MB 触发告警 |
| 数据库文件损坏 | PRAGMA integrity_check（health_check 每60s） | 自动从最新备份恢复 | 恢复失败 → escalation:owner |
| 连接泄漏 | ✅ connection_leak_detector（对话#02） | 自动关闭超时连接 | 泄漏 > 10个 → escalation:owner |
| 慢查询积累 | query_metrics 自动检测 >500ms | 写入 slow_queries 表供 AI 分析 | 单日 > 20条 → escalation:owner |
| 磁盘空间不足 | ✅ disk_monitor（对话#02） | 自动清理过期备份 + WAL TRUNCATE | 剩余 < 0.5GB → escalation:owner |
| 事务死锁/超时 | ATM tx_timeout 30s 自动 ROLLBACK | 自动释放写锁 | 连续超时 3 次 → escalation:owner |
| Schema 版本落后 | schema_version() < MIGRATIONS max | init_db() 自动补齐迁移 | 迁移失败 → escalation:owner |
