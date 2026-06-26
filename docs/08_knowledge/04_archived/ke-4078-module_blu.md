---
module_id: KE-3924
title: 15.4 文档同步策略
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 15.4 文档同步策略

15.4 文档同步策略

| 本蓝图声称 | 检查机制 | 频率 |
|------|------|:---:|
| 所有代码路径存在 | `scripts/governance/verify_file_paths.py`（待新增） | pre-commit |
| tool-contracts.yaml 无漂移 | 契约对比脚本（待新增） | pre-commit |
| AGENTS.md 包含 MCP 硬约束 | 手动检查 §8.2 任务菜单 | 每周 |
