---
module_id: KE-4056
title: 3.13 #67: 启动顺序强制执行
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.13 #67: 启动顺序强制执行

3.13 #67: 启动顺序强制执行

`graceful_shutdown.py` 的 import 必须在 Kill Switch 就绪**之前**完成——启动顺序强制执行。
