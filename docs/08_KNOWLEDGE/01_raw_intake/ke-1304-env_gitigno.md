---
module_id: KE-1217---env----------gitigno-003
title: SEC-003：`.env` 文件必须在 `.gitignore` 中
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# SEC-003：`.env` 文件必须在 `.gitignore` 中

SEC-003：`.env` 文件必须在 `.gitignore` 中

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| SEC-003 | `.env` 文件必须在 `.gitignore` 中排除，禁止提交到版本控制 | 立即从 git 历史中清除；轮换所有泄露密钥 |
