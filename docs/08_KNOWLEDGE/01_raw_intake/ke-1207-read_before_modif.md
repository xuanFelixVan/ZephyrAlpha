---
module_id: KE-1121------read-before-modif-003
status: active
title: DOC-006：先读后改（Read-Before-Modify）
category: governance
ttl: permanent
---

# DOC-006：先读后改（Read-Before-Modify）

DOC-006：先读后改（Read-Before-Modify）

任何文件操作（修改、删除、扩展）之前，必须先读取该文件及其 `depends_on` 中声明的所有依赖文件的完整内容。禁止凭记忆或猜测操作。

- **规则**：
  1. 操作前必须读取目标文件全文
  2. 操作前必须读取目标文件 `depends_on` 中列出的所有文件
  3. 如果操作涉及交叉引用，也必须读取被引用文件的相关章节
  4. 读取完成后才能执行修改/删除
- **违反后果**：基于过时或不完整的信息操作，产生逻辑矛盾；已有的交叉引用被破坏
- **验证方式**：操作完成后检查是否所有被引用文件的当前内容与修改一致
- **专业参考**：Anthropic Claude Code 官方指南 → "Never speculate about code you have not opened" / ISO 9001 §7.5 → Document Review Before Change
