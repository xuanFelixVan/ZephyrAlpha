---
module_id: KE-module_blu-3_2_execution_dependencies-000
title: 3.2 Execution Dependencies（执行依赖）
category: module_blueprint
---

# 3.2 Execution Dependencies（执行依赖）

3.2 Execution Dependencies（执行依赖）

| 依赖 | 具体对象 | 路径 |
|------|---------|------|
| ChromaDB语义缓存 | Agent成本控制 | `src/zephyr/shared/semantic_cache.py` |
| Behavior Audit Logger | 合规审计文件 | `src/zephyr/llm_security/behavior_audit_logger.py` |
| Atomic Tx Manager (ATM) | SQLite Transaction | `src/zephyr/db/atomic_transaction_manager.py` |
| External Watchdog | 心跳服务器 | `src/zephyr/shared/heartbeat_server.py` |
| WinFS Defense | Windows FS segment | `src/zephyr/shared/winfs_defense.py` |
