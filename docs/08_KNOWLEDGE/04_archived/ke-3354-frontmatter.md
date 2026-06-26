---
module_id: KE-3233
title: 2.8 frontmatter 禁止行为
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.8 frontmatter 禁止行为

2.8 frontmatter 禁止行为

| # | 禁止 | 原因 |
|---|------|------|
| 1 | 禁止 `doc_type` 与 `rule_form` 矛盾（如 policy 配 procedural、operational_rule 配 declarative） | 全部约束见 §3.6 #5（跨域禁止 §2.8 与领域专属禁止 §3.6 互补不重叠） |
| 2 | 禁止 `stability: frozen` 配 `ai_autonomy: ai_modifiable` | 冻结文件 AI 不可修改 |
| 3 | 禁止省略 `rule_form` 字段（Active 状态以上） | rule_form 是 Active+ 必填字段 |
| 4 | 禁止使用未在 §2.1 注册的字段名 | 所有字段必须先注册再使用 |
| 5 | 禁止 `scope` 与 `layer` 矛盾 | `scope: layer` 时 `layer` 不能是 `cross_layer` |
| 6 | 禁止 `verifiability: inspection` 配 `doc_type: operational_rule` | 操作规程必须可自动或手动验证，不能只靠目视检查 |

---
