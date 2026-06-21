---
module_id: KE-060-------safety-red-lines-006
title: 1. 安全红线（Safety Red Lines / 不可撤销原则）
category: documentation
---

# 1. 安全红线（Safety Red Lines / 不可撤销原则）

1. 安全红线（Safety Red Lines / 不可撤销原则）

以下 4 条原则是系统最高优先级约束，**任何架构决策、代码变更、AI 自治行为不得违反**。违反任一红线视为 P0 阻断。

| # | 原则 | 大白话 | 执行机制 |
|---|------|--------|----------|
| **R1** | **键盘不录 key** | API 密钥、数据库密码等秘密信息只能通过环境变量/密钥管理器注入，绝不手动键入 | pre-commit 检测 `key=` / `password=` / `secret=` 字面量 |
| **R2** | **日志不写 secret** | 任何日志系统（structlog/logging/print）的输出中不得包含密钥、token、私钥 | CI 门禁正则扫描 log 输出 |
| **R3** | **金融不盲信任 AI** | AI 生成的交易决策、风控参数、金额计算必须经过人工确认或确定性规则校验后才生效 | L04 风控层 hard check before L06 执行 |
| **R4** | **PRD 永远不改** | 生产数据库（PRD）永远不做 DDL 变更/手动 UPDATE/DELETE；所有变更走迁移脚本 + 审计日志 | DB 权限只读连接 + 迁移脚本强制记录 |
