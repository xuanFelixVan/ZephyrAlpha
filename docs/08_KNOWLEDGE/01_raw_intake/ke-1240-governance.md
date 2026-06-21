---
module_id: KE-1153--------4-000
status: active
title: IRN-004：断链清零（铁律4）
category: governance
---

# IRN-004：断链清零（铁律4）

IRN-004：断链清零（铁律4）

删除或移动文件后，必须在同一 commit 中更新所有引用，禁止分两次 commit。

- 验证方法：`check_dead_links.py`
- 违反后果：断链累积，治理信号失真
