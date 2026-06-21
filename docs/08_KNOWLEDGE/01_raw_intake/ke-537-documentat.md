---
module_id: KE-485
title: 7.1 环境判定规则
category: documentation
---

# 7.1 环境判定规则

7.1 环境判定规则

| 判定条件 | 环境 |
|---------|------|
| 文件路径包含 `drafts-and-audits/` | dev |
| 文件 status 为 `draft` | dev |
| 文件路径在 `docs/` 且 status 为 `active` | prod |
| 文件路径在 `src/zephyr/` 且已部署到生产服务器 | prod |
| 无法判定时 | **默认 prod**（安全优先） |
