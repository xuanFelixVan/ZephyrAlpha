---
module_id: KE-3148
status: active
title: Bug #4: AISGSandbox.scan_content() 返回 `list[str]` 而非 `list[dict]`
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# Bug #4: AISGSandbox.scan_content() 返回 `list[str]` 而非 `list[dict]`

Bug #4: AISGSandbox.scan_content() 返回 `list[str]` 而非 `list[dict]`
- **位置**: [default_security_gateway.py](file:///d:/ZephyrAlpha/src/zephyr/compliance/default_security_gateway.py#L187-L196)
- **现象**: `AttributeError: 'str' object has no attribute 'get'`
- **根因**: AISGSandbox.scan_content() 返回 `list[str]`（如 `["动态代码执行", "子进程调用"]`），代码按 dict 调用 `.get()`
- **修复**: 将每个字符串作为 message 内容，使用 `AISG-DANGER-001` 作为统一 rule_id
