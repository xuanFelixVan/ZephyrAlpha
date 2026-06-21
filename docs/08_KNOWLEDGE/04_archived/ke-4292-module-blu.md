---
module_id: KE-4133
title: 5.1 职责
category: module_blueprint
---

# 5.1 职责

5.1 职责

System Prompt 与用户输入/外部数据的隔离，防止 System Prompt 泄露，控制对话话题范围。**当前 L2 (process_sandbox.py) 负责 subprocess 沙箱**——在本八层架构中，原 L2 的进程沙箱功能迁移至 L3 输出安全层的代码执行沙箱子模块。
