---
module_id: KE-module_blu-3_8__46__longevitymonitor__m-3-000
title: 3.8 #46: LongevityMonitor (M-39)
category: module_blueprint
---

# 3.8 #46: LongevityMonitor (M-39)

3.8 #46: LongevityMonitor (M-39)

文件：`D:\ZephyrAlpha\src\zephyr\shared\longevity_monitor.py`

- `monthly_check()`: 对比月初快照 vs 当前状态
- 监控指标：python_gc_time / sqlite_wal_size / chromadb_pending_persist / open_file_handles / avg_import_time
- 月内增长>50%→告警+建议操作
