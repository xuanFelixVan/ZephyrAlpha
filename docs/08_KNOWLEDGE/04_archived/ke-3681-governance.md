---
module_id: KE-3534
title: 2.2 5 级门禁属性表
category: governance
ttl: permanent
---

# 2.2 5 级门禁属性表

2.2 5 级门禁属性表

| Gate | 机读名 | 人类可读 | 触发时机 | 执行者 | 产物 |
|:----:|-------|---------|---------|-------|------|
| **G1** | `ingest` | G1 Ingest Gate | 文档被吸入管道（task `PENDING→IN_PROGRESS`）| `GateEngine.evaluate(task, "G1")` | `gates` 表 + `deferred_queue`（失败时）|
| **G2** | `triage` | G2 Triage Gate | 文档已分类并准备进入评估（`IN_PROGRESS→COMPLETED`）| `GateEngine.evaluate(task, "G2")` | `gates` 表 + 分类失败报告 |
| **G3** | `evaluate` | G3 Evaluate Gate | 价值打分完成，准备进入激活（`COMPLETED→VERIFIED`）| `GateEngine.evaluate(task, "G3")` | `gates` 表 + 评分详情 |
| **G4** | `activate` | G4 Activate Gate | KE 对象即将写入知识库前（KMS 管道独立动作）| `GateEngine.evaluate(task, "G4")` | `gates` 表 + `deferred_queue`（依赖未就绪时）|
| **G5** | `extract` | G5 Extract Gate | 实际执行知识条目文件写入前 | `GateEngine.evaluate(task, "G5")` | `gates` 表 + 提取产物路径 |
