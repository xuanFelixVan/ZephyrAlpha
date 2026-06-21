---
module_id: KE-3520
title: 2.1 状态定义
category: governance_rule
---

# 2.1 状态定义

2.1 状态定义

| 状态 | 含义 | 可执行操作 |
|------|------|-----------|
| draft | 草稿，正在编写中 | 编辑、删除、提交审批 |
| active | 已生效，当前有效 | 引用、P1/P2/P3 变更 |
| deprecated | 已废弃，有替代品 | 只读引用、不可修改 |

> **archived 不是独立状态**：PS-STD-001 §4.1 裁定 archived 和 deprecated 对 AI 而言行为一致（都不再参考），归档是文件操作（git mv 到 archive/ 子目录），不是文档状态。deprecated 满 6 个月后执行文件物理迁移，但 status 字段保持 `deprecated` 不变。
