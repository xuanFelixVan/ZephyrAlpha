---
module_id: KE-3417
title: 9.1 激活档位表
category: documentation
---

# 9.1 激活档位表

9.1 激活档位表

| 档位 | 名称 | 触发条件（任一即可）| 激活动作 | 预计工作量 |
|------|------|-------------------|---------|-----------|
| **G0** | 当前态（未激活）| — | 无前端代码；CLI + Cursor + Feishu bot 满足所有交互 | 0 |
| **G1** | 最小 dashboard | 外部干系人（非本人 Owner）看报表/监控的需求 ≥ 2 周/次 | 搭 `frontend/` 骨架 + 1 个 App（risk-dashboard 或 monitoring-center）+ 最小 packages（ui-kit / data-client）+ tools | 5-8 天 |
| **G2** | 2-3 App 平台 | (a) G1 已运行且稳定 ≥ 1 个月 & (b) 第 2 个 App 的业务需求成熟 | 启动 Module Federation（方案 B：Vite-native MF）+ platform/ 骨架 + 第 2/3 App | 8-12 天 |
| **G3** | 团队级平台 | (a) App ≥ 3 & (b) 出现第 2 个前端开发者（人或 AI Operator）| 切换到 Webpack MF（方案 A）+ 私有 NPM + CI gate + Design System v2 | 10-15 天 |
| **G4** | AI Operator 集成 | OQ-063 F-1/F-2/F-3 AI Operator 启用到 frontend 域 | 新建 `frontend/apps/ai-cockpit` + `packages/kbar-actions` AI 指令协议 + 自动化测试增强 | 8-12 天 |
| **G5** | 外部租户 | 多账户 / 多机构需求浮出 | 主题 Token 多租户化 + Auth 升级到企业 OIDC + 权限 RBAC/ABAC 细粒度化 | 12-20 天 |
| **G6** | 移动原生端 | (a) 盯盘 / 风控告警移动端需求 & (b) PWA 不满足 | React Native 新分支（不进 web monorepo）or Capacitor PWA | 视需求定 |
