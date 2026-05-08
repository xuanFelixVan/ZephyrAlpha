---
module_id: KE-module_blu-11__l2a-001
title: 11. L2a — 进程沙箱（保留为独立模块）
category: module_blueprint
---

# 11. L2a — 进程沙箱（保留为独立模块）

11. L2a — 进程沙箱（保留为独立模块）

> **说明**：原 L2 ProcessSandbox (`process_sandbox.py`) 的 subprocess 沙箱功能保留为独立模块 `L2aSandbox`，
> 在八层架构中被 L3 输出安全层（子层3B）和 L4 Agent安全层消费。
> 它本身是一个可独立运行的沙箱服务，不限于LLM场景。
