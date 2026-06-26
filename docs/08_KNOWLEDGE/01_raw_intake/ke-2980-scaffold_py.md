---
module_id: KE-2880
status: active
title: scaffold.py 中追加
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# scaffold.py 中追加

scaffold.py 中追加
from zephyr.asset_inventory import AssetInventory
inventory = AssetInventory()
inventory.on_asset_created(
    absolute_path=str(file_path),
    asset_type=inferred_type,
    registered_by="scaffold.py"
)
```
