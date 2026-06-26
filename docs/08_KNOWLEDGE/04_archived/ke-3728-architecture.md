---
module_id: KE-3728
title: 4.1 A 家族：机构标配（21 个）
category: governance
ttl: permanent
---

# 4.1 A 家族：机构标配（21 个）

4.1 A 家族：机构标配（21 个）

| ID | 系统名 | 主层 | 次层 | 激活 Sprint |
|---|---|---|---|---|
| A-01 | ADR 架构决策治理 | Policy | — | 已就位 |
| A-02 | folder-charters 目录契约 | Policy | — | 已就位 |
| A-03 | index.md 索引治理 | Policy | (Runtime 孤儿检查) | Sprint 9（F21）|
| A-04 | Frontmatter schema | Policy | (Factory 编译) | 已就位 |
| A-05 | 编码规范（ruff/mypy/bandit）| Factory | (Runtime pre-commit/CI) | Sprint 9（L3）|
| A-06 | 架构守卫（import-linter）| Factory | (Runtime CI) | Sprint 9（L4）|
| A-07 | Fitness Functions 25 条 | Factory | (Runtime CI) | Sprint 9（L4，OQ-027）|
| A-08 | Pre-commit hooks | Runtime | — | Sprint 9 |
| A-09 | CI workflows | Runtime | — | Sprint 9 |
| A-10 | Audit log（append-only）| Runtime | — | Sprint 10（L10）|
| A-11 | Decision provenance | Runtime | — | Sprint 10（F25）|
| A-12 | Policy-as-Code（OPA）| Runtime | (Factory Rego 编译) | Sprint 11（L6）|
| A-13 | SBOM（供应链）| Factory | (Runtime 扫描) | **T4 触发**（L7）|
| A-14 | Kill switch | Runtime | — | Sprint 9（compliance）|
| A-15 | OCP 契约冻结 | Policy | (Factory 签名, Runtime 守卫) | Sprint 10（L5，F24）|
| A-16 | 跨层依赖治理 | Factory | (Runtime CI) | Sprint 9 |
| A-17 | 目录预算 | Policy | (Factory) | Sprint 9 |
| A-18 | 文件名治理 | Factory | (Runtime) | Sprint 9（F22）|
| A-19 | ADR 14 天实现 Gate | Factory | (Runtime) | Sprint 10（F23）|
| A-20 | 状态快照治理 | Runtime | — | Sprint 10 |
| A-21 | 报告归档 | Runtime | — | Sprint 9 |
