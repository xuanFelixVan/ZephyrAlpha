---
module_id: KE-802-------------append-only-002
status: active
title: 2.2.4 编号空间铁律（扁平 + append-only）
category: governance
---

# 2.2.4 编号空间铁律（扁平 + append-only）

2.2.4 编号空间铁律（扁平 + append-only）

1. **扁平编号**：所有 ADR 共享同一个 4 位数字序列（`0001~9999`）
2. **禁止嵌套编号**：不得创建 `ADR-NNN-MMM` 子编号空间（原 `KBG-011-*` 12 个子决策已于 Stage F 合并至扁平序列 `0030~0041`）
3. **关联关系靠字段**：用 frontmatter `refines: [ADR-NNNN]` / `supersedes: ADR-NNNN` / `superseded_by: ADR-NNNN` 表达，**不**用编号承载语义
4. **append-only**：编号**永不回收、不回填、不重编**
5. **跳号**：`status: skipped`（意外产生的空号，如 KBG-0006）
6. **保留号**：`status: reserved`（有意识留空，如 KBG-0023~0029）
7. **新决策编号选取**：取**当前最大编号 + 1**，不得回填 skipped/reserved
