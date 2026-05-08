---
module_id: KE-governance-15_1_ai-003
title: 15.1 AI 可直接执行的规则
category: governance
---

# 15.1 AI 可直接执行的规则

15.1 AI 可直接执行的规则

- **MRS-001 操作矩阵**：12 行 × 14 列的真值表——查表确定创建 X 后必须写哪些登记表
- **MRS-002 原子性**：所有 ✅ 目标必须在同一批 SearchReplace/Write 中完成
- **MRS-003 校验**：修改完成后自动执行对应的校验脚本
- **MRS-004 禁止行为**：#1~#6 每条有触发条件和后果
