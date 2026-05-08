---
module_id: KE-module_blu-2_1_3_status-000
title: 2.1.3 status（资产状态——五态 + 三种偏移）
category: module_blueprint
---

# 2.1.3 status（资产状态——五态 + 三种偏移）

2.1.3 status（资产状态——五态 + 三种偏移）

```python
class AssetStatus(str, Enum):
    # 正常态
    ACTIVE = "active"              # 活跃——磁盘存在 + 至少一个注册表登记
    INACTIVE = "inactive"          # 不活跃——磁盘存在但 30d 无修改且无引用
    # 偏移态（需处置）
    ORPHAN = "orphan"              # 孤儿——磁盘存在但零注册表登记
    GHOST = "ghost"                # 幽灵——注册表登记但磁盘不存在
    DRIFT = "drift"                # 漂移——注册信息（SHA256/大小/mtime）与实际不一致
    # 终态
    ARCHIVED = "archived"          # 已归档——移至 archive/ 或 99_archive/
    UNKNOWN = "unknown"            # 无法判定
```
