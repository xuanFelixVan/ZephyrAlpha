---
module_id: KE-module_blu-6_1___________d-020-11-000
title: 6.1 隐私脱敏策略（决策 D-020-11）
category: module_blueprint
---

# 6.1 隐私脱敏策略（决策 D-020-11）

6.1 隐私脱敏策略（决策 D-020-11）

> **决策 D-020-11**（新增）：审计日志虽不可变，但敏感字段在写入时即脱敏——路径含密钥名 → hash、个人信息 → mask。脱敏不可逆——原始值不存储在审计日志中。

```yaml
privacy:
  pii_detection:
    enabled: true
    patterns:
      - "file_path 含 .env / secrets / credentials / key / token → hash 存储"
      - "file_path 含 邮箱/手机号/身份证 → mask('***')"
      - "agent_id 含真实姓名 → hash 存储"

  redaction_policy:
    none: "无敏感信息"
    masked: "局部掩码——如 file_path: 'src/**/secrets/***.py'"
    hashed: "完全替换为 SHA-256——不可逆"

  access_control:
    query_audit_log: "仅 Auditor + Owner 角色（GOV-CMP-002 AUD-003）"
    query_with_pii: "仅 Owner + 需 2FA 验证"
```
