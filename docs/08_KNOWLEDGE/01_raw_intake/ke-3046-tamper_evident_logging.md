---
module_id: KE-2945
status: active
title: 防篡改日志（Tamper-Evident Logging）
category: module_blueprint
ttl: permanent
---

# 防篡改日志（Tamper-Evident Logging）

防篡改日志（Tamper-Evident Logging）

```
HMAC Chain 防篡改:
  每条 JSONL log line 增加 integrity 字段:
    {
      "...": "...",
      "integrity": {
        "hmac_sha256": "base64(HMAC-SHA256(secret, line_index + prev_hmac + log_body))",
        "line_index": 123456
      }
    }
  → 链式 HMAC：修改任一行 → 后续所有行的 HMAC 失效
  → 每 24h 自动校验 integrity chain → 发现断裂 → P1 安全事件
  → 校验通过率 < 99.9% → 自动从 archive replay 重建
  → HMAC secret 独立于 DB key，从环境变量 TELEMETRY_HMAC_SECRET 读取
```
