---
module_id: KE-governance-4___ai-003
title: §4 对 AI 的使用指引
category: governance
---

# §4 对 AI 的使用指引

§4 对 AI 的使用指引

每个新 AI session 进入本目录后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——了解全貌
2. **再读 secret-management-policy.md**——理解"密钥怎么管"（SEC-001~005）
3. **再读 access-control-policy.md**——理解"谁能访问什么"（ACS-001~005）
4. **最后读 security-incident-response-policy.md**——理解"出事了怎么办"（SIR-001~004）

所有文件均标记 `ai_autonomy: human_gated` —— AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

**安全事件分级速查**：
- P0（灾难）：密钥泄露 / 数据库对外暴露 / Kill Switch 触发
- P1（严重）：Azure Service Principal 泄露 / 第三方 API Key 泄露
- P2（重要）：写操作未留痕 / 高危命令未确认
- P3（一般）：非敏感数据泄露 / 读取类超额操作

---
