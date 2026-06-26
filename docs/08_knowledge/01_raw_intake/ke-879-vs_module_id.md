---
module_id: KE-801-----vs-module-id-002
title: 2.2.3 文件名 vs module_id 的正交性
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 2.2.3 文件名 vs module_id 的正交性

2.2.3 文件名 vs module_id 的正交性

| 维度 | 文件名 | module_id |
|---|---|---|
| 大小写 | 小写 `adr-nnnn-*` | 大写 `ADR-NNNN` |
| 编号位数 | 4 位，零填充 | 4 位，零填充 |
| 语义 | 人类友好路径 | 机器可检索 ID |
| 作用域前缀 | 无 | 无 |
| 标题 | 必须带 kebab-case 尾缀 | 不带 |
