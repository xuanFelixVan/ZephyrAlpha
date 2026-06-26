---
module_id: KE-1535
status: active
title: 15.2 自举触发器（不需要人决定）
category: module_blueprint
ttl: permanent
---

# 15.2 自举触发器（不需要人决定）

15.2 自举触发器（不需要人决定）

```python
def determine_bootstrap_level() -> BootstrapLevel:
    """纯机械判定——检查产出文件的存在性"""
    if not unified-asset-index.exists():
        if not classified-assets.exists():
            if not raw-asset-scan.exists():
                return BootstrapLevel.LEVEL_0  # 裸盘
            return BootstrapLevel.LEVEL_1      # 有扫描无分类
        return BootstrapLevel.LEVEL_2          # 有分类无对账
    return BootstrapLevel.LEVEL_3              # 完整
```
