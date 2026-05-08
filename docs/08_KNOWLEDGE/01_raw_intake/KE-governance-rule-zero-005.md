---
module_id: KE-governance-rule-zero-005
title: 与 RULE-ZERO 的关系
category: governance_rule
---

# 与 RULE-ZERO 的关系

与 RULE-ZERO 的关系

| | RULE-ZERO（锁协议） | RULE-ONE（并发写入） |
|---|---|---|
| **适用场景** | AI 用 IDE 工具直接改源文件 | Python 脚本产出文件 |
| **触发条件** | Write/SearchReplace 操作 | `open(path, "w")` / `write_text()` |
| **粒度** | 每个目标文件一个锁 | 每个脚本自己管理 |
| **解决问题** | 防止两个 AI 同时编辑同一文件 | 防止脚本多实例互斥卡死 |

两者互补，不可互相替代。新建脚本 MUST 同时遵守两条规则。

---
