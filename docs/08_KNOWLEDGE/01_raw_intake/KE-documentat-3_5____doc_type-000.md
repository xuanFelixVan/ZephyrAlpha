---
module_id: KE-documentat-3_5____doc_type-000
title: 3.5 新增 doc_type 的流程
category: documentation
---

# 3.5 新增 doc_type 的流程

3.5 新增 doc_type 的流程

1. 在实际使用中发现现有 27 种无法覆盖的文档类型
2. 提交决策记录（MOD-KB-001 §3.9.5），说明：新类型名称、与现有类型的区别、为什么不能归入现有类型
3. 决策记录审批通过后，**仅更新 `_registry/vocabularies/doc_type-vocabulary.yaml`**（canonical SSoT）——本文件 §3.2 为速查引用、§3.4 为派生表，不需要手动同步
4. 校验器 `check_frontmatter_metadata.py` 从 YAML 动态加载合法值——无需修改校验代码
5. 同步更新 `frontmatter-schema.json`（自动生成）
5. 在下一个 pre-commit 版本中纳入新值的校验
