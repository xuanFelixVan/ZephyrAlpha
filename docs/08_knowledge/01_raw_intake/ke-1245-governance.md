---
module_id: KE-1158---------9-000
status: active
title: IRN-009：双工具互斥（铁律9）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# IRN-009：双工具互斥（铁律9）

IRN-009：双工具互斥（铁律9）

禁止在 Cursor 和 Trae 中同时打开同一文件编辑。同一时间只允许一个 IDE 操作同一文件。

- 验证方法：流程纪律为主（Windows 下无统一跨 IDE 文件锁机制），技术锁为辅
- 违反后果：两个 IDE 互相覆盖写入，文件内容损坏不可恢复
