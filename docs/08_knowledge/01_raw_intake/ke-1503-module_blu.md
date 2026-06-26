---
module_id: KE-1413
title: 12. 关联蓝图与文档
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 12. 关联蓝图与文档

12. 关联蓝图与文档

| 模块 | 关系 |
|------|------|
| [MOD-INF-020 audit-trail](../audit-trail/blueprint.md) | **兄弟模块**——本模块产出资产事件，MOD-INF-020 做不可变审计记录 |
| [MOD-DATABASE database](../../_cross_layer/database/blueprint.md) | **存储依赖**——资产索引的对账结果写入 SQLite |
| [MOD-INF-016 shared-core](../../_cross_layer/shared-core/blueprint.md) | **Schema 依赖**——AssetEntry/AssetScan 等 Pydantic V2 模型 |
| [MOD-INF-005 script-system](../script_system/blueprint.md) | **调度依赖**——`generate_asset_index.py` 作为治理脚本 |
| [MOD-GATE_ENGINE gate-engine](../../_cross_layer/gate-engine/blueprint.md) | **门禁集成**——`G_asset_inventory` CI 阻断孤儿超标 |
| [MOD-INF-015 system-telemetry](../system-telemetry/blueprint.md) | **遥测上报**——资产指标写入遥测通道 |
| [GOV-CMP-003 审计协议](../../../01_policies_and_standards/governance/compliance/audit-protocol.md) | **治理依赖**——盘点结果纳入 12 维度审计清单 |

---
