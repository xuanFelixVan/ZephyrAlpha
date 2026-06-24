---
module_id: KE-4350
title: 加密策略（Encryption at Rest）
category: module_blueprint
---

# 加密策略（Encryption at Rest）

加密策略（Encryption at Rest）

| 数据层 | 加密方式 | 密钥管理 |
|--------|---------|---------|
| **SQLite metrics DB** | SQLite Encryption Extension (SEE) 或 SQLCipher (AES-256) | 密钥从环境变量 `TELEMETRY_DB_KEY` 读取，不写入文件 |
| **JSONL logs** | 不整体加密（影响查询效率），但 PII 字段用 AES-256-GCM 逐字段加密 | 独立 per-field key |
| **DLQ JSONL** | 不加密（DLQ 是问题暴露窗口，需要 AI 快速消费），但 PII 字段 redact/mask | — |
| **archive gzip** | gzip 压缩本身不加密，archive 目录可选择性 AES-256 全量加密 | 通过 FeatureFlag `telemetry.archive_encryption` 控制（默认 OFF） |
| **config/ YAML SSoT** | 不加密（在 git 中，不应含密钥），密钥通过环境变量注入 | 环境变量 → OS keyring / 1Password CLI |
