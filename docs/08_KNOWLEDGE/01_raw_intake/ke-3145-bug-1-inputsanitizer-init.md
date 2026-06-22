---
module_id: KE-3145
status: active
title: Bug #1: InputSanitizer.__init__() 缺少 `root` 参数
category: session_log
---

# Bug #1: InputSanitizer.__init__() 缺少 `root` 参数

Bug #1: InputSanitizer.__init__() 缺少 `root` 参数
- **位置**: [default_security_gateway.py](file:///d:/ZephyrAlpha/src/zephyr/compliance/default_security_gateway.py#L127)
- **现象**: `TypeError: InputSanitizer.__init__() missing 1 required positional argument: 'root'`
- **修复**: 在 `DefaultSecurityGateway.__init__()` 增加 `project_root` 参数，传递给 `InputSanitizer(root=project_root)`
