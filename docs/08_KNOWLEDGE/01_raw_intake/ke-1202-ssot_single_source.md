---
module_id: KE-1116----single-source--004
status: active
title: DOC-001：SSoT 唯一（Single Source of Truth）
category: governance
---

# DOC-001：SSoT 唯一（Single Source of Truth）

DOC-001：SSoT 唯一（Single Source of Truth）

每个架构事实有且仅有一份权威来源文件。禁止同一内容存在于两个文件中。

- **规则**：任何规则、数据、流程定义只能在一个文件中定义。其他文件只能引用，不能重复定义。
- **违反后果**：AI 按错误版本执行，治理信号矛盾
- **验证方式**：`check_ssot_conflicts.py`；人工查重审查
- **专业参考**：ISO 27001 Annex A → Information Management
