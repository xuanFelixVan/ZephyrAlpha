---
module_id: KE-1741
status: active
title: 2.19 Agent 身份验证
category: module_blueprint
ttl: permanent
---

# 2.19 Agent 身份验证

2.19 Agent 身份验证

> **对标**：OAuth 2.0 client credentials + SPIFFE (Secure Production Identity Framework for Everyone)。

```yaml
agent_identity_verification:
  # === 身份模型 ===
  identity:
    format: "spiffe://zephyr-alpha.local/agent/{agent_type}/{agent_id}"
    agent_type: "architect | implementer | governor | orchestrator"
    agent_id: "UUID v7（时间排序）"
    session_id: "当前对话 session token"

  # === 身份令牌 ===
  token:
    format: "JWT (RS256签名——非对称，防伪造)"
    claims: ["agent_id", "agent_type", "session_id", "issued_at", "expires_at"]
    ttl: "24h → 过期需重新认证"
    storage: "内存存储→不写入文件系统（防AI读取伪造）"

  # === 委托身份验证 ===
  delegation_auth:
    rule: "接收委托的Agent必须验证发起方的JWT token"
    check: ["签名有效性", "agent_type匹配声称的能力", "token未过期"]
    failure: "身份验证失败→拒绝委托 + 安全事件 + 发起方升级为blocked"

  # === 克隆检测 ===
  clone_detection:
    rule: "同一 agent_id 不能同时在多个 session 中活跃"
    detection: "session注册表——同一agent_id入第二个session→标记为克隆嫌疑"
    action: "新session拒绝接入 + 通知Owner"
```

---
