---
module_id: KE-3987--------4-000
title: 2.1 快速取证补充（4项）
category: module_blueprint
---

# 2.1 快速取证补充（4项）

2.1 快速取证补充（4项）

| 取证 | 发现 | 方案 |
|------|------|------|
| 快速取证A | SLO的"后见之明偏差"——SLO目标系统性乐观 | §5 SLO Review中已部分覆盖，施工期需替代机制 |
| 快速取证B | Windows崩溃转储二次伤害——8GB .dmp填满磁盘 | 部署脚本 Disable-WERCrashDump |
| 快速取证C | Python atexit 与 Kill Switch 竞态 | graceful_shutdown import必须在Kill Switch就绪前完成 |
| 快速取证D | "影子测试"幽灵——AI可能优化掉测试 | Kill Switch/ErrorBudget Tracker测试也加入IMMUTABLE_CORE |
