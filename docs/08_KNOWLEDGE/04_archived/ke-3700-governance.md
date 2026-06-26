---
module_id: KE-3553
title: 20. 可验证性标注
category: governance_rule
ttl: permanent
---

# 20. 可验证性标注

20. 可验证性标注

| 条目 | 可验证性 | 验证方式 |
|------|:-------:|---------|
| 领域受控词表合规 | A | check_frontmatter_metadata.py 校验 |
| Layer 与 doc_type 一致性 | A | check_frontmatter_metadata.py 校验 |
| Scope 受控词表合规 | A | check_frontmatter_metadata.py 校验 |
| Stability 受控词表合规 | A | check_frontmatter_metadata.py 校验 |
| Stability 与 ai_autonomy 一致性 | A | check_frontmatter_metadata.py 校验 |
| 规则画像与实际一致 | M | 人工审查 |
| 推导链一致性（stability→layer→scope→Owner） | A | check_frontmatter_metadata.py 校验 |

---
