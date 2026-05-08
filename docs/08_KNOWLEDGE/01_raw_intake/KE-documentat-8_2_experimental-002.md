---
module_id: KE-documentat-8_2_experimental-002
title: 8.2 experimental 关键约束
category: documentation
---

# 8.2 experimental 关键约束

8.2 experimental 关键约束

- **所有外部 API 调用强制 HTTPS/TLS 1.3**；证书校验不得禁用
- **静止数据不入 git**：`.runtime/`、`*.db`、`*.parquet`、`*.env` 均在 `.gitignore`
- **PII 豁免**：当前系统无用户 PII；未来接入 KYC 数据时触发 beta 升级
