---
module_id: KE-2048
status: active
title: 3.10 #48: DependencyCapacityGuard
category: module_blueprint
---

# 3.10 #48: DependencyCapacityGuard

3.10 #48: DependencyCapacityGuard

文件：`D:\ZephyrAlpha\src\zephyr\shared\dependency_capacity_guard.py`

- `guard_pip_operation(operation, packages)`: Sandbox中先跑→前后容量快照
- 内存增长>100MB → BLOCK + 回滚命令
- 导入时间增加>500ms → BLOCK
