---
module_id: KE-3655
title: 六、AI 生成产物的特殊规则
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 六、AI 生成产物的特殊规则

六、AI 生成产物的特殊规则

> **旧体系教训**：AI 生成的扫描报告、分析产物直接写入 `docs/` 受版本控制目录，污染版本历史。

| 规则 | 内容 |
|------|------|
| AI 生成产物写入位置 | **必须写入 `.audit_cache/`**（已 gitignored），禁止写入受版本控制目录 |
| AI 生成文件 frontmatter | 必须包含 `created_by: agent` 和 `ttl: 7d` 或 `ttl: 30d` |
| AI 生成产物提升为正式文档 | 需要 Owner 审查后手动移入正式目录，并更新 frontmatter |
