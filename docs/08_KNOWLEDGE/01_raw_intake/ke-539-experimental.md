---
module_id: KE-487
status: active
title: 7.1 experimental 简化模型（单人）
category: documentation
ttl: permanent
---

# 7.1 experimental 简化模型（单人）

7.1 experimental 简化模型（单人）

**现状**：单人开发，单机运行，**无多用户 IAM 需求**。

**最小约束**：

- 操作系统用户：Windows 本机用户一人
- 本地服务（Ollama / ChromaDB）：仅绑定 `127.0.0.1`，拒绝外网
- API Key 即身份：所有外部调用的授权来源
