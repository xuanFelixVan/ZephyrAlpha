---
module_id: KE-3420
title: 9.2 不应激活的反信号
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 9.2 不应激活的反信号

9.2 不应激活的反信号

| 信号 | 含义 | 正确动作 |
|------|------|---------|
| "想做 UI 但说不出第一个用户是谁" | 业务需求未成熟 | 继续停留 G0，用 CLI / Feishu 验证需求 |
| "Cursor / Copilot 生成了一个页面要不要留" | 代码先于架构 | 先让它过 §1-§7 原则审核；不过则舍弃，不做"临时方案" |
| "交易信号页面嵌到 L05 里" | 违反 KBG-0007 + FE-P1/FE-P2 | 强制踢回 G0 或 G1，不允许临时破例 |
| "搭个后台管理页改数据库" | 违反 FE-P2 + 安全原则 | 改用后端 admin CLI 或 Feishu Bot 工具，不要为此开 G1 |
