---
module_id: KE-866----3-000
status: active
title: 3.4 路径 3：工具搜索 [兜底]
category: governance
ttl: permanent
---

# 3.4 路径 3：工具搜索 [兜底]

3.4 路径 3：工具搜索 [兜底]

**可用工具**：

| 工具 | 适用场景 | 示例 |
|------|---------|------|
| `grep` / Grep | 搜索文件内容中的关键字或 module_id | `grep "GOV-DOC-010" --files-with-matches` |
| SearchCodebase | 自然语言搜索代码和文档 | "文档发现机制" |
| Glob | 按文件命名模式搜索 | `Glob "**/document-discovery*"` |
| `dir /s` 或 `find` | 按文件名搜索 | `dir /s /b *discovery*` |

**操作流程**：

```
1. 优先搜索 module_id（精确匹配）
   └── grep "GOV-DOC-010" -r --files-with-matches
2. 如果 module_id 未知，搜索关键字
   └── grep "文档发现" -r -l
3. 搜到结果 → 验证 frontmatter module_id → 确认是否正确文件
4. 搜索无结果 → 走三级"不存在"判定
```
