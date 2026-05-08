---
module_id: KE-module_blu-7_2-000
title: 7.2 事件流
category: module_blueprint
---

# 7.2 事件流

7.2 事件流

```
scaffold.py → asset.created
                  ↓
            AssetInventory.on_asset_created()
                  ↓
            ┌─────────────────┐
            │ 1. 分类         │
            │ 2. 写索引       │  ← unified_asset_index.yaml
            │ 3. 触发审计     │  → MOD-INF-020: FileAuditDetail(CREATE)
            │ 4. 发送遥测     │  → MOD-INF-015: asset_count +1
            └─────────────────┘

定时扫描 → asset.discovered
                ↓
          分类引擎 → asset.classified
                ↓
          对账引擎 → asset.orphan / asset.ghost / asset.drift
                ↓
          reconciliation_report.md + unified_asset_index.yaml 更新
```

---
