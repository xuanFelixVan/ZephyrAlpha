"""zephyr.db — 元数据持久化层（SQLite）与原子事务管理。

本包封装 experimental 元数据层（见 ADR-0030：SQLite 作为任务 / 事件 / 知识 / 门禁的
本地元数据存储）的底层读写，并提供跨 SQLite + 文件系统的原子事务管理器（ATM）。

模块清单：

- ``atomic_transaction_manager``  ——  ATM：SQLite BEGIN/COMMIT/ROLLBACK
  + 文件系统 "temp → fsync → rename" 两阶段提交 + 路径白名单（委托
  ``zephyr.llm_security.input_sanitizer.InputSanitizer``）。
- ``sqlite_schema``               —  SQLite DDL Schema 定义（experimental 元数据表 CREATE TABLE）
- ``task_repo``                   —  任务卡 CRUD 仓库（TaskCard 的完整生命周期读写）
- ``database_manager``            —  数据库管理器（连接池 / 热备份 / 迁移编排）
"""

from __future__ import annotations

__all__ = [
    "atomic_transaction_manager",
    "olap_engine",
    "sqlite_schema",
    "task_repo",
]
