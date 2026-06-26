---
module_id: KE-295
title: 3.6 密钥与凭证安全
category: documentation
ttl: permanent
---

# 3.6 密钥与凭证安全

3.6 密钥与凭证安全

> **对标**：SOC 2 CC6.1/CC6.7、OWASP LLM Top 10 #6、GitHub Copilot secret scanning、量化机构密钥管理实践。

| #      | 禁止行为                        | 原因                                            | 替代方案                                                   | 来源                                   |
| ------ | --------------------------- | --------------------------------------------- | ------------------------------------------------------ | ------------------------------------ |
| ABS-29 | 将密钥/API Key/Token/密码提交到版本控制 | 密钥泄露是 P0 级安全事件，一旦进入 git 历史无法彻底清除              | 使用环境变量或密钥管理服务，pre-commit 集成 git-secrets/detect-secrets | SOC 2 CC6.1, git-secrets             |
| ABS-30 | AI 读取并输出密钥内容到响应或日志          | AI 可在 session 中读取 .env 等文件并将密钥内容输出，泄露到日志或对话记录 | AI 遇到疑似密钥内容时用 `<REDACTED>` 替代，不得原样输出                   | OWASP LLM #6, Claude Code guardrails |
| ABS-31 | 在日志中记录密钥                    | 日志可能被多人访问，密钥出现在日志中等于泄露                        | 日志写入前过滤密钥模式（正则匹配 API key/secret/token）                 | SOC 2 CC6.7                          |
| ABS-32 | 在源代码中硬编码密钥                  | 硬编码密钥无法轮换，且随代码分发扩散                            | 使用环境变量、配置文件（不入库）或密钥管理服务                                | SOC 2 CC6.1, FINRA Rule 4512         |
