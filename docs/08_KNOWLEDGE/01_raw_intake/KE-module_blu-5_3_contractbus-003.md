---
module_id: KE-module_blu-5_3_contractbus-003
title: 5.3 ContractBus 分三批迁移
category: module_blueprint
---

# 5.3 ContractBus 分三批迁移

5.3 ContractBus 分三批迁移

44 份 ContractBus 文件分三批迁移到 Pydantic v2 Schema Enforcement：

| 批次 | 文件数 | 触发条件 | 验收标准 |
|------|-------|---------|---------|
| 批 1 | 15 | experimental 起步 | mypy 100% + ruff 0 + 单测 ≥80% |
| 批 2 | 15 | 批 1 验收 + 7 天稳定 | 同上 + 集成测试 |
| 批 3 | 14 | 批 2 验收 + 14 天稳定 | 同上 + 跨批契约一致性 |

搬迁追踪器：`19_development_workspace/structure-and-mapping/contractbus-migration-tracker.yaml`，校验脚本：`scripts/governance/contractbus_migration_check.py`。

---
