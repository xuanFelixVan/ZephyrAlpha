---
module_id: KE-2372
title: 6.2 状态转换映射
category: module_blueprint
ttl: permanent
---

# 6.2 状态转换映射

6.2 状态转换映射

| 脚本系统输出 | 任务系统状态 | 说明 |
|-----------|:---:|------|
| exit 0（全通过） | 任务状态不变 | 正常流程 |
| exit 1（警告） | 任务 → `⚠️ WARNING` | 不阻塞，日志记录 |
| exit 2（错误） | 关联任务 → `BLOCKED` | Finding 必须修复才能解除阻塞 |
| exit 3（崩溃） | **所有活跃任务** → `BLOCKED` | 门禁自身故障=系统不可信 |
