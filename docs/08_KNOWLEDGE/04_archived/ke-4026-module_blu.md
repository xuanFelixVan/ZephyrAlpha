---
module_id: KE-3873
title: 13.2 注册登记清单（盘点系统必须登记到的位置）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 13.2 注册登记清单（盘点系统必须登记到的位置）

13.2 注册登记清单（盘点系统必须登记到的位置）

> **对标 RULE-TWO 强制集成清单**——每项产出必须注册，否则 = 孤儿。

| # | 登记位置 | 条目 | 状态 |
|---|---------|------|:--:|
| 1 | `module-registry.yaml` | `MOD-INF-026: asset-inventory` | ✅ 已登记 |
| 2 | `blueprint_registry.yaml` | 自动同步自 blueprint.md frontmatter | ✅ 已同步 |
| 3 | `registry_of_registries.yaml` | 新增 REG-INV-001 域（资产盘点注册表域） | ✅ 已登记 |
| 4 | `project_rules.md` 冷启动序列 | STEP 4.5: 读 unified-asset-index.yaml | ✅ 已实施 |
| 5 | `phase_manager.py` Phase 1 | `gate_asset_inventory` 检查 | ✅ 已实施 |
| 6 | `risk-register.yaml` | R17~R19：盘点系统运营风险 | ✅ 已登记 |
| 7 | `_index.yaml` TRAE 域 | TRAE-010：冷启动 STEP 4.5 规则登记 | ✅ 已登记 |
| 8 | `SessionContinuity.print_restore_summary()` | 资产摘要注入恢复上下文 | ⬜ 待 Phase 2 |
| 9 | `AGENTS.md` | 新能力声明：资产盘点查询 | ⬜ 待 Phase 2 |
| 10 | `scripts/script-manifest.yaml` | `generate_asset_index.py` 等盘点脚本 | ⬜ 待 Phase 1 |
