---
ttl: task_bound
title: E-1 备份晨报判读表 v2（三态制，st-backfix-20261010 T3）
session: st-backfix-20261010
completes_when: T1 影子链晋升生产判读表时本件升格并入备份 SOP，随批归档
---

# E-1 备份晨报判读表 v2（三态制）

- 版本: v2（st-backfix-20261010，修复令 T3）
- 取代: `docs/_working/disk_reorg_campaign/LEDGER_final.md` 收口段两态表（报告绿+G mtime 前进+F 不存在 ⇔ 仍死）与
  `docs/_working/final4_campaign/99_delivery.md` §五两态判读（该表缺"仍在跑/迟到"格，08:34 案例被迫"不勾任何栏"）。
- 结构性假红病灶（两态制）: 读数时点早于完成时点 ⇒ 既非绿也非死 ⇒ 两态表无格可勾，或被误勾"仍死"触发不必要的三处留痕定位。

## 口径勘误（读数锚点）

**旧锚点错误**："06:05 三绿终验"——06:00 起跑的备份正常时长 2h20m~3h+（历史报告 duration_seconds=8434.5s=2h20m34s），06:05 必然读到"无"。
**v2 锚点**：`起跑时刻（06:00）+ 判读窗`。判读窗默认=**上轮成功报告 duration 的 1.5 倍，下限 3h，上限 6h**（无历史时取 3h）。
到点才读，不到点属第三态，不属未做。

## 三态判定表（按序判定，先 1 后 2）

### 第 1 格（分岔键）：持锁进程活否

`Get-Process -Id <backup.lock 内 PID>`（锁格式 `PID:<n> START:<iso>`；PID 读不出则按 START 时间+4h 兜底）。

| 读数 | 判定 | 动作 |
|---|---|---|
| **活**（powershell 存活且 StartTime 与锁 START 吻合 ±5min） | **第三态：在跑/迟到** | 禁判红禁判绿。已跑时长 vs 判读窗：窗内=正常等待；超窗=升级"卡死分支"（记录 stage_timeline/子进程指纹，转备份班），仍不是"死" |
| **死**（进程不存在；或 PID 复用 StartTime 不吻合） | 进入第 2 格 | 锁残留≠在跑（持锁者死⇒接管，production ps1 已有该分支；影子链 LOCK_TAKEOVER 同语义） |

### 第 2 格（死局面）：证据面读数

| 证据组合 | 判定 | 动作 |
|---|---|---|
| 当日 report json 存在 + state `last_backup_status`/`last_attempt_status` 回写 | **绿（完整轮）** | 验收销账；仍按六要素记录关键数字 |
| 无 report，但 **checkpoint 面**（影子链 backup_state_shadow.json `stages`）当窗 stage_ok | **影子绿（被杀但有据）** | 按 stage 记账已做工作；凶手线索=常驻陷阱 procstart_trap_standing.log 案发前 5 分钟 START 行（T5 流程） |
| 无 report 且无 checkpoint（生产现状，影子未晋升前） | **红（病灶③形态）** | 死于 STAGE4 前+状态永不回写；记录 lock_skip 数与 CH 侧 `system.backups` 当窗 BACKUP_CREATED 替代证据（替代口径三绿：CH BACKUP_CREATED 时刻｜G mtime 前进｜F 不存在），并触发修复班流程 |

### 替代口径三绿（CH 真值面，任何一格都可引用）

CH `system.backups` 当窗 `BACKUP_CREATED`（真值不受 ps1 死亡影响）｜G 盘备份产物 mtime 当日前进｜F 盘不该存在的复生标志不存在。
三绿齐而 report 缺席=**绿受损**（记账但不判死）——这正是病灶③的读数面形态。

## 晨报六要素（沿用 a1_ledger 先例）

1. 完成了什么 2. 关键数字 3. 新发现/风险 4. 待 Owner/总指挥 5. 证据指针 6. 交接/下一步。

## 判读纪律

- 两态表时代的历史判读（08:34 案例"不勾任何栏"）按本表追溯=第三态，非失职。
- 生产面在影子晋升前，第 2 格"影子绿"行依赖影子链在跑；影子不在跑时该行按"红（病灶③形态）"读。
- 本表随 T1 影子链晋升而升格为生产判读表；晋升前与 LEDGER_final 收口段并读，以本表为准。
