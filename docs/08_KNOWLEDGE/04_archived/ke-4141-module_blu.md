---
module_id: KE-3986
title: 2. 域内模块清单
category: module_blueprint
ttl: permanent
---

# 2. 域内模块清单

2. 域内模块清单

| module_id | 名称 | 优先级 | 施工进度 | 核心职责 |
|-----------|------|:---:|:---:|------|
| MOD-INF-018 | Agent RBAC | P0 | phase_2_complete | 七层纵深防御+六横切面运行时权限执行 |
| MOD-INF-019 | Agent Spec | P0 | phase_2_complete | 蓝图→可加载 Skill 升级引擎 |
| MOD-INF-020 | Audit Trail | P0 | phase_2_complete | 不可变审计追踪+密码学Provenance+Agent签名 |
| MOD-INF-021 | Rollback System | P1 | phase_2_complete | Git-native + SQLite Checkpoint 智能回滚 |
| MOD-INF-022 | Escalation Protocol | P1 | phase_2_complete | 规则驱动升级+自动委托+五层防御架构（引擎: v0.14.0） |
| MOD-INF-023 | Drift Detector | P1 | completed | Git-native 运行时漂移检测+自动对账 |
| MOD-INF-024 | Budget Enforcer | P2 | phase_2_complete | Token/Cost/Time 三维预算强制执行（引擎: v0.7.0） |
| MOD-INF-025 | A2A Protocol | P2 | phase_2_complete (Phase 4 Hold) | 多Agent通信协议+冲突仲裁（引擎: v0.10.0，Phase 4 激活） |
