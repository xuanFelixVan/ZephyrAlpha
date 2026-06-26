---
module_id: KE-2082
status: active
title: 3.2 契约定义
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.2 契约定义

3.2 契约定义

- **契约 SSoT**：`src/zephyr/mcp/tool-contracts.yaml`
- **版本**：1.2.0
- **工具命名约定**：`{server_id}.{action}`（如 `task_manager.decompose_blueprint`）
- **工具稳定性生命周期**：experimental → beta → stable → frozen
- **safety_level**：L/M/H 三级访问控制（定义在 YAML，`_handle_tools_call` 中强制执行）
