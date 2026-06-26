---
module_id: KE-443
title: 6.1 当前资产清单
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 6.1 当前资产清单

6.1 当前资产清单

| 密钥类型 | 来源 | 存储位置 | 轮换频率 | experimental 保护 |
|---------|------|---------|:--------:|-------------|
| LLM API Key（Anthropic/OpenAI/DeepSeek 等）| 官网 | `.env` | 90 天 | .gitignore + git-secrets |
| Broker API Key（未来）| 券商 | `.env`（experimental 不用）| N/A | — |
| Feishu Bot Token | 飞书 | `.env` | 180 天 | .gitignore |
| 1Password Service Account Token | 1Password | OS Keychain | 1 年 | 不落文件 |
