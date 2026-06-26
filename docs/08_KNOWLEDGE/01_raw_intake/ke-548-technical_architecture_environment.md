---
module_id: KE-496--------04-ta--9-environmen-000
title: 7.3 环境矩阵（与 04-TA §9 Environment Matrix 对齐）
category: documentation
ttl: permanent
---

# 7.3 环境矩阵（与 04-TA §9 Environment Matrix 对齐）

7.3 环境矩阵（与 04-TA §9 Environment Matrix 对齐）

| 环境 | 前端部署方式 | API Base | Auth | Feature Flags |
|------|-------------|---------|------|---------------|
| Dev | 本机 `vite dev` | `http://localhost:8000` | Bypass / Mock JWT | all-on |
| UAT | 临时 CDN / Netlify preview | `https://uat-api.zephyr.local` | Mock OIDC | staged |
| Staging | 生产同构 CDN | `https://staging-api.zephyr.local` | 真 OIDC | canary |
| Prod | 生产 CDN + 灰度 | `https://api.zephyr.local` | 真 OIDC | prod-only |
