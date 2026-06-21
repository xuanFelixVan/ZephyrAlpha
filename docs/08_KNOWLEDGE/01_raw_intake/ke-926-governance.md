---
module_id: KE-848
status: active
title: §3 跨域依赖关系速览
category: governance
---

# §3 跨域依赖关系速览

§3 跨域依赖关系速览

```
architecture/ ←→ security/     (架构评审门控 ←→ 密钥泄露触发安全事件)
    │                │
    └──── data/ ←────┘          (架构版本化 ←→ 数据质量依赖)
              │
         compliance/            (审计追踪引用数据保留期限+访问控制)
              │
         ai/                    (AI日志保留 → data/数据保留策略)
```

关键跨域引用链：
- `compliance/audit-trail → data/retention → ai/session-log-schema`（审计→保留→日志，3 域链）
- `security/access-control → ai/autonomy-registry`（访问控制 → AI 代理权限注册表）

---
