# [A_module] module_id=MOD-INF_db | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-012 | docs/03_modules/_cross_layer/database/blueprint.md | §
"""zephyr.infrastructure.db — 元数据持久化层（SQLite + DuckDB 双引擎）与原子事务管理 v2.0。

本包封装 experimental 元数据层（见 ADR-0030：SQLite 作为任务 / 事件 / 知识 / 门禁的
本地元数据存储）的底层读写，并提供跨 SQLite + 文件系统的原子事务管理器（ATM）。

模块清单（MOD-INF-012 v2.0）：

- ``atomic_transaction_manager``  —  ATM v2.0：SQLite BEGIN/COMMIT/ROLLBACK
  + 文件系统 "temp → fsync → rename" 两阶段提交 + tx_idempotency 幂等去重
  + compensating_transaction 补偿事件 + 事务超时控制
- ``sqlite_schema``               —  SQLite DDL Schema 定义（版本化迁移框架 v1–v8）
- ``task_repo``                   —  任务卡 CRUD 仓库（软删除 + ON CONFLICT upsert + JSON1 查询）
- ``database_manager``            —  数据库管理器（连接池 / 健康检查 / 自动备份 / WAL checkpoint）
- ``olap_engine``                 —  DuckDB OLAP 分析引擎（sqlite_scanner + Parquet 归档 + 统一查询）
- ``audit_schema``                —  审计视图与查询入口（CLI 审计面板 / compliance 报告）
- ``query_metrics``               —  SQL 查询性能监控（P50/P95/P99 百分位 + slow_queries 表）
"""
from __future__ import annotations

import importlib as _importlib

def __getattr__(name):
    if name == "query":
        return _importlib.import_module(f"{__name__}.query")
    if name == "transition":
        return _importlib.import_module(f"{__name__}.transition")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'atomic_transaction_manager',
    'audit_schema',
    'base_repo',
    'circuit_breaker_repo',
    'circuit_breaker_types',
    'database_manager',
    'gate_repo',
    'olap_engine',
    'query',
    'query_metrics',
    'sqlite_schema',
    'task_repo',
    'transition',
]
