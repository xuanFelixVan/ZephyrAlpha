---
module_id: KE-4003
title: 2.3 与已有类似功能的区别
category: module_blueprint
ttl: permanent
---

# 2.3 与已有类似功能的区别

2.3 与已有类似功能的区别

| 已有模块 | 重叠点 | 为什么不能复用 |
|---------|--------|-------------|
| MOD-INF-004 vibe-coding-pipelines | 脚本系统被提及 | MOD-INF-004 管"怎么跑管线"，本系统管"怎么审计产出物"——独立职责，独立架构 |
| MOD-TASK_SYSTEM task-system | 任务管线里有审计 | MOD-TASK_SYSTEM 的任务管线审计是"内嵌审计"——只审计自己管线产出。本系统是"系统级审计"——横切全局 |

---
