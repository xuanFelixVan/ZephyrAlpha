---
module_id: KE-640
status: active
title: Step 0：安全审查
category: documentation
---

# Step 0：安全审查

Step 0：安全审查

新连接器上线前必须通过以下安全检查：

1. 确认无硬编码凭据（参见 DOM-L00-001 §3 ABS-002）
2. 确认连接使用加密传输（TLS 1.3 或更高）
3. 确认凭据已注册到密钥管理服务，且遵循最小权限原则
4. 如未通过安全审查，禁止进入后续步骤
