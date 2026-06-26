---
module_id: KE-3574
title: 4. 消费者注册表
category: governance
ttl: permanent
---

# 4. 消费者注册表

4. 消费者注册表

以下文件直接依赖本文档——本标准规则变更时必须同步更新：

| 消费者 | 文件 | Tier | 依赖内容 |
|--------|------|:---:|---------|
| check_registry_consistency.py | `scripts/governance/` | 1 | §7 校验步骤——校验脚本的执行流程引用 MRS-003 |
| run_all.py | `scripts/governance/` | 2 | 审计脚本编排——需将 check_registry_consistency.py 纳入 40 步编排 |
| document-metadata-index-registry.yaml | `_registry/catalogs/` | 1 | MRS-001 规则行——创建/修改规则文档时的登记要求 |
| document-metadata-index-registry.yaml（原 master-document-inventory-registry.md 已废弃） | `_registry/catalogs/` | 1 | MRS-001 文档行——创建任何文档时必须登记 |
| module-registry.yaml | `03_modules/` | 1 | MRS-001 模块行——模块操作的登记要求 |
| blueprint_registry.yaml | `03_modules/` | 1 | MRS-001 模块行 |
| script-health-registry.md | `_registry/catalogs/` | 1 | MRS-001 脚本行 |
| adr-status-registry.yaml（冻结壳） | `_registry/catalogs/` | 1 | MRS-001 ADR 行（占位对账；活跃决策不在此表逐条维护） |
| directory-registry.md | `_registry/catalogs/` | 1 | MRS-001 目录行 |
| gate-registry.md | `_registry/catalogs/` | 2 | MRS-001 门禁行 |
| knowledge-article-registry.md | `_registry/catalogs/` | 2 | MRS-001 知识条目行 |

---
