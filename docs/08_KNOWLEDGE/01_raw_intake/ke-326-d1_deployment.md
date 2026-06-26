---
module_id: KE-326
status: active
title: §3 D1 — Deployment / 部署域
category: documentation
ttl: permanent
---

# §3 D1 — Deployment / 部署域

§3 D1 — Deployment / 部署域

**职责**：管理软件版本从开发到生产的全生命周期发布流程。

当前状态：
- 单人本地开发环境（localhost），无 CI/CD Pipeline
- 代码通过 git 管理，部署 = `git pull` + 手动启动脚本
- 版本号遵循项目 CHANGELOG 约定

> 🚧 **占位**：CI/CD Pipeline（GitHub Actions / 本地 Makefile）、蓝绿部署 / 金丝雀发布策略、版本回滚 Runbook 待激活后设计。
>
> **关联**：`technology_architecture.md §6`（部署图）

---
