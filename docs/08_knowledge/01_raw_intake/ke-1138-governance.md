---
module_id: KE-1053
status: active
title: ABS-001：所有数据源连接必须认证
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# ABS-001：所有数据源连接必须认证

ABS-001：所有数据源连接必须认证

任何数据源连接必须使用认证凭据，禁止匿名连接。

- 认证方式：API Key + Secret / OAuth Token / 证书双向认证
- 凭据存储：必须存储在密钥管理服务中（参见 `../../../governance/security/secret-management-policy.md` GOV-SEC-001 ABS-002）
- 凭据轮换：至少每 90 天轮换一次（参见 GOV-SEC-001 COND-001）。轮换期间旧凭据保留 24 小时宽限期以确保无缝切换，宽限期后旧凭据立即吊销。
