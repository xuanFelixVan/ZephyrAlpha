---
module_id: KE-module_blu-4__lock_ttl______b167-000
title: 4. Lock TTL 过期机制（B167）
category: module_blueprint
---

# 4. Lock TTL 过期机制（B167）

4. Lock TTL 过期机制（B167）

- 默认 `lock_ttl_s=300s`（5分钟）
- 获取锁时写入 owner + PID + timestamp
- 释放锁时自动清理
- Stale 检测：锁超过 TTL 或 PID 不存在→自动释放
