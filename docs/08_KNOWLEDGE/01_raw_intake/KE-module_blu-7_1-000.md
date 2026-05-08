---
module_id: KE-module_blu-7_1-000
title: 7.1 核心事件
category: module_blueprint
---

# 7.1 核心事件

7.1 核心事件

```python
class AssetEventType(str, Enum):
    ASSET_CREATED = "asset.created"              # scaffold 创建文件
    ASSET_DISCOVERED = "asset.discovered"        # 扫描器首次发现
    ASSET_CLASSIFIED = "asset.classified"        # 分类引擎打标签
    ASSET_REGISTERED = "asset.registered"        # 写入 unified_asset_index
    ASSET_MODIFIED = "asset.modified"            # SHA256 变化
    ASSET_DELETED = "asset.deleted"              # 文件物理删除
    ASSET_ORPHAN_DETECTED = "asset.orphan"       # 对账发现孤儿
    ASSET_GHOST_DETECTED = "asset.ghost"         # 对账发现幽灵
    ASSET_DRIFT_DETECTED = "asset.drift"         # 对账发现漂移
    ASSET_DEPRECATED = "asset.deprecated"        # Owner 标记废弃
    ASSET_RETIRED = "asset.retired"              # 移入 archive/
    ASSET_ARCHIVED = "asset.archived"            # 终态
    RECONCILIATION_STARTED = "reconciliation.started"
    RECONCILIATION_COMPLETED = "reconciliation.completed"
    SCAN_STARTED = "scan.started"
    SCAN_COMPLETED = "scan.completed"
```
