---
module_id: KE-2217
status: active
title: 4.1 设计原则
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4.1 设计原则

4.1 设计原则

对标 AGENTS.md §6.5（脚本自创入库强制约定）：
- **触发条件**：AI 创建任何 `.py` 文件（行为触发，非语义分类）
- **合法落位**：只有三个去处——`scripts/governance/` / `src/zephyr/` / `tests/`
- **三件套缺一不可**：缺任何一项视为未完成入库
