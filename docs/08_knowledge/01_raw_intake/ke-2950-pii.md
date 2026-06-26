---
module_id: KE-2850
status: active
title: PII 字段级脱敏扩展
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# PII 字段级脱敏扩展

PII 字段级脱敏扩展

```
日志脱敏规则扩展（§5 现有 PII masking 的增强）:
  - email: user@domain.com → u***@domain.com
  - API key: sk-abc123... → sk-**** (保留前缀以区分来源)
  - IP address: 192.168.1.1 → 192.168.*.* (保留 /24 网段)
  - file path: 保持功能路径但脱敏用户名（如 C:\Users\johndoe\... → C:\Users\****\...）
  - phone/card/SSN: 完全删除或替换为 [REDACTED]
```
