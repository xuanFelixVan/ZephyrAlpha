---
module_id: KE-3274
title: 3.6 doc_type 禁止行为
category: documentation
ttl: permanent
---

# 3.6 doc_type 禁止行为

3.6 doc_type 禁止行为

| # | 禁止 | 原因 |
|---|------|------|
| 1 | 禁止在 `governance/` 下使用 `operational_rule` | governance/ 只放声明式，operational_rule 是过程式 |
| 2 | 禁止在 `operational/` 下使用 `policy` 或 `standard` | operational/ 只放过程式，policy/standard 是声明式 |
| 3 | 禁止使用旧长名（`governance_standard`、`governance_registry` 等） | 已迁移到短名，旧长名不再合法 |
| 4 | 禁止使用未在本文件 §3.2 注册的 doc_type | 所有 doc_type 必须先注册再使用 |
| 5 | 禁止 `doc_type` 与 `rule_form` 矛盾 | 声明式 doc_type 不能配过程式 rule_form，反之亦然 |

---
