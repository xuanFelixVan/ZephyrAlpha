---
module_id: KE-4108
title: 4.2 容量估算
category: module_blueprint
---

# 4.2 容量估算

4.2 容量估算

| 维度 | 当前 | 峰值 | 极限 | 够用？ |
|------|:--:|:--:|:--:|:--:|
| 蓝图 | 6（含 deprecated） | 200+ | 无上限 | ✅ |
| 任务卡(SQLite) | 当前 task_metadata.db | 2000+ | 10000/域 | ✅ |
| Change Folder(.md) | 1 | 200+ | 文件系统 | ✅ |
| SQLite | <100MB | <100MB | ~281TB | ✅ |
| M 模块 | 11 | 20 | 30+ | ✅ |
| 模型 | 3 | 8 | 受控词表可扩展 | ✅ |
