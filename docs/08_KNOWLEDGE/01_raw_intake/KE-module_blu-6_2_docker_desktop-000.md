---
module_id: KE-module_blu-6_2_docker_desktop-000
title: 6.2 Docker Desktop 沙箱（升级路径）
category: module_blueprint
---

# 6.2 Docker Desktop 沙箱（升级路径）

6.2 Docker Desktop 沙箱（升级路径）

触发条件：需要完整 syscall 隔离 / CI 环境 / 不信任的第三方 Agent

- 挂载 repo 为只读 bind mount
- `writable_paths` 作为可写 tmpfs overlay
- `--network=none` 默认
- 资源限制：`--memory`, `--cpus`, `--pids-limit`
