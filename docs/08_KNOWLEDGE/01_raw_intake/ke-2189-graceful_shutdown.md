---
module_id: KE-2096
status: active
title: 3.3 #28: GracefulShutdown (M-32)
category: module_blueprint
ttl: permanent
---

# 3.3 #28: GracefulShutdown (M-32)

3.3 #28: GracefulShutdown (M-32)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\graceful_shutdown.py`

实现 `GracefulShutdown` 类（蓝图 L2866-2935）：
- `register_signal_handlers()`：注册 SIGTERM/SIGINT
- `save_state_snapshot(path=".audit_cache/shutdown_state.json")`：1750ms deadline 内保存
- `restore_on_boot()`：启动时恢复上次状态
- 蓝图 L2880-2935 代码完整实现
