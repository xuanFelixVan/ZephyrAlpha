---
module_id: KE-3142
title: 6.6.5 生成文件豁免
category: agent_instruction
---

# 6.6.5 生成文件豁免

6.6.5 生成文件豁免

带有 `generated_at` 字段的自动生成文件（如 `document-metadata-index-registry.yaml`）不参与 frontmatter 必填字段校验——其内容由生成脚本保证一致性，不要求手写完整 frontmatter。
