---
module_id: KE-session_lo-unknown-006
title: 变更的文件
category: session_log
---

# 变更的文件

变更的文件

| 操作 | 文件路径 | 说明 |
|------|---------|------|
| 新建 | scripts/governance/adr_to_kb_migration.py | ADR → KB 迁移脚本（322 行） |
| 删除 | docs/02_enterprise_architecture/adr/ | 33 个 ADR + index.md |
| 删除 | docs/01_policies_and_standards/_registry/catalogs/adr-status-registry.yaml | 状态登记表 |
| 删除 | docs/01_policies_and_standards/templates/adr-template.md | ADR 模板 |
| 删除 | docs/01_policies_and_standards/governance/architecture/adr-protocol.md | ADR 协议 |
| 删除 | src/zephyr/kb/adr_ingest.py | ADR 批量摄入脚本 |
| 编辑 | docs/01_policies_and_standards/_registry/schemas/session-log-schema.yaml | decisions 字段升级 |
| 编辑 | docs/01_policies_and_standards/meta/metadata-registry.md | 删除 ADR 命名空间行 |
| 编辑 | docs/03_modules/l01_infrastructure/database/blueprint.md | ADR-0030 路径更新 |
| 编辑 | docs/03_modules/l01_infrastructure/llm-security/blueprint.md | ADR-0020 路径更新 |
| 编辑 | src/zephyr/db/atomic_transaction_manager.py | 测试路径替换 |
| 编辑 | tests/unit/test_file_task_mapper.py | 测试路径替换 |
| 编辑 | tests/unit/test_gate11_naming_convention.py | 测试路径替换 |
| 编辑 | docs/01_policies_and_standards/_registry/catalogs/registry-master-index.yaml | PS-REG-015 标记 migrated |
| 编辑 | docs/01_policies_and_standards/_registry/catalogs/rule-catalog.yaml | ADR 条目标记 deleted |
| 编辑 | docs/01_policies_and_standards/_registry/catalogs/document-metadata-index.yaml | ADR 条目标记 deleted |
| 编辑 | docs/02_enterprise_architecture/target-architecture/architecture-model/module-id-registry.yaml | PS-REG-015 标记 migrated |
| 编辑 | docs/01_policies_and_standards/governance/module/multi-registry-synchronization-standard.md | ADR 行更新 |
| 编辑 | docs/01_policies_and_standards/index.md | 模板目录数 11→10 |
| 编辑 | docs/01_policies_and_standards/templates/index.md | 删除 ADR 行 |
| 编辑 | docs/01_policies_and_standards/_registry/catalogs/index.md | 删除 ADR 行 |
| 编辑 | src/zephyr/shared/contracts/synthesized_signal.py | 字段排序修复 |
| 编辑 | src/zephyr/shared/contracts/experiment_result.py | 字段排序修复 |
| 编辑 | src/zephyr/shared/contracts/system_configuration.py | 字段排序修复 |
| 编辑 | src/zephyr/shared/contracts/telemetry_emitter.py | 字段排序修复 |
