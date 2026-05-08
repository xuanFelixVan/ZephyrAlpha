---
task_id: "DB-025-0080"
namespace: "OPS"
seq: 80
title: "自愈设计 §18.1——7 类故障自愈能力实现验证"
tags: ["fn:self_healing", "ly:cross_layer"]
depends_on: ["DB-025-0026"]
upstream_files:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\olap_engine.py"
acceptance_criteria:
  - "1.WAL文件无限增长→wal_autocheckpoint=4096自动checkpoint，WAL>100MB触发告警"
  - "2.数据库文件损坏→PRAGMA integrity_check(health_check每60s)，自动从最新备份恢复，恢复失败→escalation:owner"
  - "3.连接泄漏→❌待实现(T-DB-011)自动关闭超时连接，泄漏>10个→escalation:owner"
  - "4.慢查询积累→query_metrics自动检测>500ms，写入slow_queries表供AI分析，单日>20条→escalation:owner"
  - "5.磁盘空间不足→❌待实现DatabaseManager监控，自动清理过期备份+触发Parquet归档，剩余<1GB→escalation:owner"
  - "6.事务死锁/超时→ATM tx_timeout 30s自动ROLLBACK，自动释放写锁，连续超时3次→escalation:owner"
  - "7.Schema版本落后→schema_version()<MIGRATIONS max，init_db()自动补齐迁移，迁移失败→escalation:owner"
rollback_instructions: "自愈缺口 → §20 R*"
---

# DB-025-0080：自愈设计 §18.1——7 类故障

§18.1: 连接/WAL/磁盘/DuckDB/迁移/慢查询/备份 7 类自愈。
