---
module_id: KE-1367
title: 10.4 4 类问题模式修复对照
category: module_blueprint
---

# 10.4 4 类问题模式修复对照

10.4 4 类问题模式修复对照

| 问题模式 | experimental 根因 | beta 修复 |
|------|------|------|
| Gate Engine 40% WARNING | 关键字不精准（"校验"匹配脚本系统） | 新增 gate_engine/G1~G5/cooldown/YAML parse/gates/ 等 12 个精准关键字 |
| "YAML parse bug" 路由到 Script System | "parse"/"bug" 无 Gate Engine 专属匹配 | 新增 "YAML parse"/"门禁bug"/"gate bug" 关键字，Gate Engine 优先级 92 > Script 88 |
| 跨模块 50% 不合规 | AI 只读 1 份蓝图就停止 | MCP 返回 top-3 + cross_read_hints；hint 语言从 "SHOULD" 升级为 "MUST" |
| 边界模糊任务 | fail-closed 同时属 Gate Engine + Security | 两条路由均含 "fail-closed" 关键字 → MCP 返回两者；cross_read_hint 互引 |
