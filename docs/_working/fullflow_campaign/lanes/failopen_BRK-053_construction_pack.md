---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# BRK-053 施工包 · 遥测归档 not_started 而 flag 在册

> 车道 `st-ff-failopen-20260918` 只出包不翻 flag。

## 1. 现状

`config/flags.yaml` §`flags.archive`：
`{"enabled": false, "description": "遥测数据归档 (未实现，保留flag)", "retention_days": 30, "compression": "gzip", "implementation_status": "not_started"}`

`implementation_status: "not_started"` **而 `retention_days: 30` 已在册** = 注册表承认一个
不存在的保留策略。比 052/054 略轻（`enabled=false`，不假装在跑），危害在于
**下游把"30 天保留"当既成事实** → FF-12 长周期（跨月）归因实际无历史可查。

## 2. 缺哪几件实现

| # | 缺件 | 说明 |
|---|---|---|
| A-1 | 归档触发器 | 事件触发（遥测分区封闭事件），宪法 §9.3 禁 cron/Timer |
| A-2 | gzip 归档 + 校验和 | 归档件带 `content_sha256` 并可回读逐位对比（六向③"落盘必须读盘"） |
| A-3 | 恢复路径 | 只归档不可恢复 = 冷存储假象；必须有 `restore` 且被至少一条测试真跑 |
| A-4 | 保留策略与实现对齐 | 让 `retention_days` 成为**被实现读取的真源**，不是散文数字 |
| A-5 | 自动关闭四要素 | 归档批的孤儿进程/临时文件自清（宪法 §9.3） |

## 3. 验收判据

1. 造一段遥测 → 触发归档 → 读回归档案逐位对比；
2. `restore` 真跑并产出可读原样；
3. 断归档写盘（`tmp_path` 真 IO 故障）→ 必须报红且**不推进游标**（否则下轮静默跳段）；
4. 任何写盘/`notify` 返回值都必须被检查（本车道 #1 教训的普适化）。

## 4. 风险与回滚 / 翻 flag 前置

- 风险：归档吞盘。缓解：A-2 前置容量核对——`infrastructure/hot_plane_budget.py` 在册但
  BRK-006 记其零消费，须一并接线，否则容量闸不生效。
- 回滚：`enabled=false`（现状即回滚态）。
- 前置：A-1..A-5 齐 + §3 四条实测。`implementation_status` 改为 `implemented` 属实现事实登记，
  **不等于**翻 `enabled` flag（后者是 Owner 门位）。
