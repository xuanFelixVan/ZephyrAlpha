---
module_id: KE-3173--------phase-transi-003
title: 10.1 Phase 对齐表（配合 phase-transition-protocol.md）
category: documentation
ttl: permanent
---

# 10.1 Phase 对齐表（配合 phase-transition-protocol.md）

10.1 Phase 对齐表（配合 phase-transition-protocol.md）

| Phase | 阶段名 | D6 目标分 | 本视图必交付 |
|:-----:|-------|:--------:|-------------|
| scaffold | 基础奠基 | 2.2 → 3.5 | §6 L1+L2（.env + git-secrets）+ §9 SQLite audit schema |
| experimental | 核心服务上线 | 3.5 → 5.5 | §4 LSG + §5 Agent Sandbox + §6 L3 + §9 Session Log |
| beta | 接入真实券商 | 5.5 → 7.0 | §7 RBAC 启用 + §6 1Password 迁移 + §8 数据分级落地 + 合规审计 |
| beta | 多用户/部分自动化 | 7.0 → 8.0 | 零信任 + OIDC + WAF + 多区审计 |
| stable | 机构级/全自动 | 8.0 → 9.0+ | SOC2/ISO27001 合规 + 专职安全团队 |
