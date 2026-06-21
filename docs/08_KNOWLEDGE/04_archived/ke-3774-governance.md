---
module_id: KE-3623
title: 7.2 审计判定速查表
category: governance_rule
---

# 7.2 审计判定速查表

7.2 审计判定速查表

| 发现内容 | doc_type 声称为 | 实际内容为 | 判定 | 操作 |
|---------|:---:|---------|------|------|
| 蓝图（模块架构设计） | `policy` | 蓝图 | 🔴 标签+位置均错误 | 搬到 `03_modules/l*/模块名/blueprint.md` |
| 施工图（实施步骤） | `operational_rule` | 模块施工图 | 🔴 内容非操作规则 | 搬到 `03_modules/l*/模块名/construction-plan.md` |
| ADR 讨论稿 | `protocol` | 讨论草稿 | 🔴 内容类型错误 | 迁入 **`KB:decisions`** namespace（Git-backed）；若以 Markdown 草稿承载则在 `_development_workspace/` 或仓库批准的草稿路径撰写——禁止写入已删除的旧 `docs/02_enterprise_architecture/adr/` 树 |
| 路线图 | `standard` | 路线图 | 🔴 内容类型错误 | 搬到 `02_enterprise_architecture/` 或归档 |
| 会话日志 | `policy` | 会话记录 | 🔴 | 搬到 `session_logs/` |
| 声明式规则 | `policy`/`standard`/`protocol` | 确实是规则 | ✅ | 原地不动 |
| 过程式步骤 | `operational_rule` | 确实是操作流程 | ✅ | 原地不动 |
