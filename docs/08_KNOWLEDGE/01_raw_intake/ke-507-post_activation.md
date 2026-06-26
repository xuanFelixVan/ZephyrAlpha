---
module_id: KE-456
title: 6.2 Post-Activation 拓扑概要
category: documentation
ttl: permanent
---

# 6.2 Post-Activation 拓扑概要

6.2 Post-Activation 拓扑概要

> 激活触发：接入真实资金 / 外部投资人 / 多账户 / SRE 抽屉激活。

| 维度 | experimental（当前） | Post-Activation |
|------|----------------|----------------|
| 运行环境 | Windows 本地单机 | Linux 云端 / 容器化（Q5-5） |
| 数据存储 | PostgreSQL + TimescaleDB (primary) + DuckDB (analytics) + Parquet (archive) | 云端 DB + 对象存储 |
| 可观测性 | 本地日志文件 | OTel Collector + Prometheus + Grafana |
| 调度 | 手动 / 简单 cron | Airflow / Prefect（Q5-2） |
| CI/CD | GitHub Actions（lint/audit） | 完整 CI/CD Pipeline + 回滚 |
