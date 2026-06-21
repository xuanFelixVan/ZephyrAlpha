---
module_id: KE-2051
status: active
title: 3.11 #35: WinFSDefense
category: module_blueprint
---

# 3.11 #35: WinFSDefense

3.11 #35: WinFSDefense

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\winfs_defense.py`

实现 `WinFSDefense` 类（蓝图 L3308-3345）：
- `validate_path_length(path, max_chars=255)`：路径截断检测
- `check_handle_count()`：句柄泄漏追踪
- `sanitize_filename(name)`：过滤 Windows 非法字符
- `check_volume_space(path)`：Magic Volume 磁盘空间监控
