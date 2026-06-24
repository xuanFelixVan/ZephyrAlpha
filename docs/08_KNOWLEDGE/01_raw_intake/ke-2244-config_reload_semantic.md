---
module_id: KE-2150
status: active
title: 3.8 #32: ConfigReloadSemantic
category: module_blueprint
---

# 3.8 #32: ConfigReloadSemantic

3.8 #32: ConfigReloadSemantic

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\config_reload_semantic.py`

实现 `ConfigReloadSemantic` 类（蓝图 L3114-3144）：
- 两种生效模式：`deferred_生效`（等待当前任务完成）/ `immediate_生效`（强制终止当前任务）
- `apply_config_change(config_path, mode) -> bool`
