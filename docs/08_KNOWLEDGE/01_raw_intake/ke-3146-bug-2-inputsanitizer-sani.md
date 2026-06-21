---
module_id: KE-3146
status: active
title: Bug #2: InputSanitizer 无 `sanitize()` 方法和 `is_clean` 属性
category: session_log
---

# Bug #2: InputSanitizer 无 `sanitize()` 方法和 `is_clean` 属性

Bug #2: InputSanitizer 无 `sanitize()` 方法和 `is_clean` 属性
- **位置**: [default_security_gateway.py](file:///d:/ZephyrAlpha/src/zephyr/compliance/default_security_gateway.py#L154-L165)
- **现象**: `AttributeError: 'InputSanitizer' object has no attribute 'sanitize'`
- **修复**: 替换为 try/except 包裹 `validate_llm_context()` 调用，手动追踪 `self._l1_clean` bool 状态
