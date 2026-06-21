---
module_id: KE-186-------beta-002
status: active
title: 2.3 零信任原则（beta 起启用）
category: documentation
---

# 2.3 零信任原则（beta 起启用）

2.3 零信任原则（beta 起启用）

**experimental 简化**：D-INT / D-STORE 之间不强制边界校验（单进程、单机、单人）。

**beta 及以后**：接入真实券商后，必须升级为零信任：

- 每次 API 调用都带显式 scope（最小权限）
- 所有密钥都有过期时间（短 TTL）
- 所有跨服务调用都带 `request_id` 和来源鉴证

---
