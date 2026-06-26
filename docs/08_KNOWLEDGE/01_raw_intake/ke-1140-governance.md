---
module_id: KE-1055
status: active
title: ABS-002：禁止硬编码连接凭据
category: governance
ttl: permanent
---

# ABS-002：禁止硬编码连接凭据

ABS-002：禁止硬编码连接凭据

数据源连接字符串中的密码/Token 禁止硬编码在代码或配置文件中。本条为 `../../../governance/security/secret-management-policy.md`（GOV-SEC-001）ABS-001 在数据源领域的具体应用。

- 必须通过环境变量或密钥管理服务注入
- 违反此规则等同于密钥泄露
