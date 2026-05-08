---
module_id: KE-documentat-unknown-005
title: 受保护字段
category: documentation
---

# 受保护字段

受保护字段

```yaml
protected_field: adr_reference
authority_file: KB:namespace=decisions
check_rule: >
  任何文件引用 ADR-XXX 时，该 ADR 的 status 必须与权威来源一致。
  不得引用 Deprecated ADR 作为当前决策依据。
violation_severity: P1
```

---
