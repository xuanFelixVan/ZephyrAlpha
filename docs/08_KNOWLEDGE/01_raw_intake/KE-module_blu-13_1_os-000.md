---
module_id: KE-module_blu-13_1_os-000
title: 13.1 OS 级进程隔离
category: module_blueprint
---

# 13.1 OS 级进程隔离

13.1 OS 级进程隔离

- 每个 MCP Server 为独立 Python 进程
- stdio 管道隔离——无网络暴露
- 单进程崩溃不影响其他 Server
