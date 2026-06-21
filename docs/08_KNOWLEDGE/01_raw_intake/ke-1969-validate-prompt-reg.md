---
module_id: KE-1878--------prompt-reg-000
status: active
title: 2.3 Validate（安全校验）— prompt_registry.py + pattern_library.py
category: module_blueprint
---

# 2.3 Validate（安全校验）— prompt_registry.py + pattern_library.py

2.3 Validate（安全校验）— prompt_registry.py + pattern_library.py

CE 通过 CT-CE-LSG-001 契约调用 LSG 进行安全校验：
- 检查注入内容是否含恶意指令（prompt injection）
- 检查是否含项目敏感信息泄露
- 检查是否含危险工具调用建议

LSG 拒绝的块 → 移除 → 重新 compress → 再送 LSG → 最多 3 次
