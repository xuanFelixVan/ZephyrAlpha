---
module_id: KE-2866----security-000
status: active
title: rbac_roles.yaml 新增 security 维度的角色
category: module_blueprint
---

# rbac_roles.yaml 新增 security 维度的角色

rbac_roles.yaml 新增 security 维度的角色
roles:
  security:
    identity_verifier:
      description: "Agent RBAC内部使用的身份验证器——非Agent角色，是系统组件"
      permissions:
        - "verify_session_token"       # 验证Session Token签名
        - "detect_identity_mismatch"   # 检测身份声明与实际不符
        - "block_forged_agent"         # 阻断伪造身份的Agent
```

---
