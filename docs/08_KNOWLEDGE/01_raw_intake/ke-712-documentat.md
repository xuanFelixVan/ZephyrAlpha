---
module_id: KE-637
status: active
title: Stage 8：从"机构标准确认"到"元数据契约与触发机制细化"
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# Stage 8：从"机构标准确认"到"元数据契约与触发机制细化"

Stage 8：从"机构标准确认"到"元数据契约与触发机制细化"

本轮讨论进一步确认了组织记忆系统专题设计稿（`organizational-memory-system-design.md`）中已有的机构级标准：

1. **元数据契约（envelope）**：7 大类字段（Identity / Lifecycle / Provenance / Scope & Impact / Retrieval / Security & Privacy / Content）已是完整机构标准，无需额外修正。
2. **异步流水线**：专业机构采用"主对话模型不负责记忆整理，后台异步处理"的分层架构，避免高耗 token 和上下文挤占。
3. **知识边界分层**：明确"知识库存全文，记忆系统存索引"的分层策略，避免双真源问题。

本轮同时暴露一个新未决问题：
