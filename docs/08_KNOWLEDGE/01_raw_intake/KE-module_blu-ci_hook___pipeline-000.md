---
module_id: KE-module_blu-ci_hook___pipeline-000
title: CI Hook：检测Pipeline蓝图变更→自动触发联动文件同步检查
category: module_blueprint
---

# CI Hook：检测Pipeline蓝图变更→自动触发联动文件同步检查

CI Hook：检测Pipeline蓝图变更→自动触发联动文件同步检查
def check_cross_module_sync():
    if blueprint_changed("pipeline"):
        for sync_file in CROSS_MODULE_SYNC:
            if not is_synced(sync_file, blueprint):
                raise SyncCheckFailed(f"{sync_file.path} 需要更新")
```
