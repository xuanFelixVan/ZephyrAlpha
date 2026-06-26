---
module_id: KE-1242
title: 核心原则
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 核心原则

核心原则

| # | 原则 | 说明 |
|---|------|------|
| 1 | **零自主创建权** | AI 永远不能自行决定新目录的层级结构——必须有索引授权或 Owner 批准 |
| 2 | **先查索引，再行动** | 所有路径操作前强制查询 GOV-DOC-002 §5.1.2 + registry-master-index.yaml |
| 3 | **新结构必须登记** | 任何经批准的新增目录创建后，必须在同一 session 内同步更新三个索引文件 |
| 4 | **临时文件也守规矩** | 即使是 `sketches_and_drafts/` 下的临时文件，也必须放在规定的草案目录下——禁止在根目录或其他非草案目录创建临时文件 |
| 5 | **目录存在性前置检查** | 写入文件前，先检查 `os.path.exists(os.path.dirname(path))`——不存在则走三步流程，不直接 `mkdir` |
