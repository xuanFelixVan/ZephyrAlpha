---
module_id: KE-4197----readers-000
title: 7.2 下游 Readers
category: module_blueprint
---

# 7.2 下游 Readers

7.2 下游 Readers

| 读取方 | 用途 | 调用方式 |
|--------|------|---------|
| **Context Engine**（主消费者） | 组装 Agent 上下文 | `await vm.multi_search(query, collections, merge_strategy="rrf")` |
| MCP `knowledge_base_server.py` | Cursor/Claude 的 MCP 工具 | `await vm.search(...)` / `multi_search(...)` |
| Dashboard `knowledge_overview.py` | 可视化统计 | `await vm.stats()` |
| 4 验收脚本 | 合规检查（是否全量入库） | `await vm.stats()` vs 源文件数 |
