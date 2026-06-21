---
module_id: KE-1025
status: active
title: 8. 新增规则登记流程
category: governance_rule
---

# 8. 新增规则登记流程

8. 新增规则登记流程

1. 发现新规则时，确定其所属域（META/CODE/ARCH/DOC/AI/SCRIPT/TRAE/...）
2. 在对应域的表格中新增一行，登记号按序递增
3. 如果规则同时对应 ABS/COND/REC，填写对应编号
4. 如果规则是代码级强制，强制方式填 `code`，代码路径填完整路径 + 行号
5. 更新 §7 统计表

**特别条款：TRAE 域自动同步**

当 `.trae/rules/project_rules.md` 中新增任何 `RULE-*` 条目时：
- （A）MUST 在本登记表中新增对应的 TRAE-* 条目
- （B）可选运行自动同步脚本：`python scripts/governance/sync_rule_registry.py`（从 project_rules.md 提取所有 RULE-* 并对比登记表，报告差异）

---
