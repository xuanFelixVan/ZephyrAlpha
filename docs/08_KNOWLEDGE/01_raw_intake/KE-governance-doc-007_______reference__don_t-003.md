---
module_id: KE-governance-doc-007_______reference__don_t-003
title: DOC-007：引用不复制（Reference, Don't Duplicate）
category: governance
---

# DOC-007：引用不复制（Reference, Don't Duplicate）

DOC-007：引用不复制（Reference, Don't Duplicate）

两个文件之间传递信息只能使用引用，禁止将内容从一个文件复制粘贴到另一个文件中。即使措辞不同，只要表达的是同一个含义，也必须改为引用。

- **规则**：
  1. 如果需要引用另一个文件的规则/定义/数据 → 使用完整路径引用（遵循 DOC-004）
  2. 禁止在新文件中重新声明已有文件中定义过的规则
  3. 即使措辞不同，只要表达的是同一个含义，也必须改为引用
  4. 如果需要补充/细化 → 在原文件中扩展，然后在其他文件中引用扩展后的章节
- **违反后果**：产生隐形重复——后续修改原文件时副本不同步，形成信息分叉
- **验证方式**：任何新增段落如果包含"必须"、"禁止"、"应当"等规范用语，检查该规范是否已在其他文件中定义过
- **专业参考**：Cursor 官方 Rules 指南 → "Reference files instead of copying content into rules" / DRY（Don't Repeat Yourself）原则
