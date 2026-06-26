---
module_id: KE-1157--------8-000
status: active
title: IRN-008：先读后写（铁律8）
category: governance
ttl: permanent
---

# IRN-008：先读后写（铁律8）

IRN-008：先读后写（铁律8）

修改任何文件前，必须先 Read 该文件的当前内容。禁止凭记忆或推测直接写入。

- 验证方法：Session Log 审计（自动化脚本待开发——当前为规格占位）。check 每个 Write 前是否有对应的 Read 记录
- 违反后果：AI 凭过时记忆覆盖文件，导致内容回退或错乱
