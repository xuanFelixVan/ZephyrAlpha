---
ttl: task_bound
completes_when: 三线终验红蓝通过（本板归档）
session: st-unified-plan-20260920
issue: UNIFIED-CAMPAIGN-001-V1-TIMING
---

# 停机干预窗声明板（裁定#378③ 协议载体——乙线声明、甲丙遵守、全员可读）

## 协议（三句话）

1. **乙线**：任何 CH 重启/停机/OPTIMIZE 独占窗开工前 ≥30 分钟在下方表格追加一行；完工改 `状态=done`；实际执行偏离声明窗 ±15 分钟以上须在备注补记原因。
2. **甲线**：任何 >30 分钟批次（回填/重跑）启动前读本板，禁止横跨 `active` 状态窗；冲突=改期或拆片。
3. **冲突仲裁**：同档按登记序；跨档按 全局冻结>独占窗>闪断，低档让高档。

## 声明台账（追加行，禁删改他人行）

| 登记时间 | 日期 | 起-止 | 档位 | 操作 | 影响面 | 声明会话 | 状态 | 备注 |
|---|---|---|---|---|---|---|---|---|
| （示例）2026-09-21 01:30 | 2026-09-21 | 02:00-05:00 | 独占窗 | 乙W1 尸体表 export+drop（签字单①批后） | CH 重 IO；甲禁大查询/回填 | st-disk-ch-20260921 | planned | 首窗 12 张实测仲裁 |
| （示例）2026-09-21 14:00 | 2026-09-21 | 14:30-14:35 | 闪断 | 乙W2 CH 重启（text_log TTL 落地） | 分钟级断连；甲避让在途批 | st-disk-ch-20260921 | planned | 避开 02:30 夜跑带 |

## 已知固定窗（非声明也须避让）

- **00:00-05:00 计划任务带**：02:30 tilib_indicator_backfill_nightly（dwm 回填，修复 C-5 前在飞）+晨间数据任务族；乙闪断/独占窗插入时逐个查 `schtasks /query` 实况。
- **06:00 backup.ps1 兜底窗**（post-commit 事件触发为主）；乙 W4 调换前显式暂停并登记本板。
- **周休窗**：Owner 已裁周日 ≥09:00 才允许计划关机；夜班窗 23:00-09:00 打折使用。
| 2026-09-20 22:34 | 2026-09-20 | 23:05-23:30 | 闪断 | 乙分包1 CH 重启（text_log level=information+系统日志 TTL 落地，WO-5） | 分钟级断连；甲无在途批（未注册）；丙不碰 CH；避开 02:30 夜跑带 | st-disk-ch-20260921 | done | 实际 23:05:33 执行 23:05:36 复活（秒级）；TTL 8 表全绿+level=information 生效；重启后暴露 hyperliquid NaN+中信期货 TSV 解析既有重试风暴（~31 err/min，归甲 WO-2 A4/A7，非本次变更引入） |
| 2026-09-21 00:20 | 2026-09-21 | 00:30-05:30 | 独占窗（盘间） | 乙分包5 F→G 兜底镜像 710G（robocopy /MIR，盘间搬运无 CH 干预）+暂停 ZephyrAlpha-DailyBackup 至镜像完成 | F/G 盘重 IO；CH 零影响；甲线未注册；02:30 tilib 夜跑不涉 F/G | st-disk-ch-20260921 | done | 五目标全 ok（ch_vm 592G/offrepo 137G/zephyr_cold 137G/db_dumps/git_bundles）；计划任务已恢复 Ready；backup.ps1 实跑全链完成含 CH 增量 ok；ZephyrAlpha-DailyBackup Ready |
| 2026-09-21 11:40 | 2026-09-21 | 11:40-23:59 | 独占窗（盘间+VM窗另报） | 乙追加令v2 阶段4 备份总仓落G（working_vault 种子 53G/115万件+db_dumps/git/offrepo 迁移+冷储镜像改名址）；期间暂停 ZephyrAlpha-DailyBackup | F/G 盘重 IO；CH 零影响（4.7 VM 窗另行单独声明）；甲线大批让 F/G 无涉 | st-disk-ch-20260921 | planned | 完成后恢复任务+backup.ps1 换G实跑 |
| 2026-09-21 11:55 | 2026-09-21 | 12:00-14:00 | 独占窗（CH 中度 IO） | 乙追加令v2 阶段3.2 冷线欠账有界归档（reconciler full_auto×12 轮，批≤3分区≤30G；TI 已排除无同表冲突；news/etf 过线分区 export→verify→双副本→drop） | CH 读为主；甲 >30min 大批请查本行错峰；批10 回填不受影响（非 TI） | st-disk-ch-20260921 | planned | 每轮独立 manifest；失败即熔断停 |
| 2026-09-21 14:20 | 2026-09-21 | 14:30-15:30 | VM 窗（4.7 双写第二链） | 乙追加令v2 阶段4.7：G:\ch_backup_disk2.vhdx 创建+SCSI 热挂（优先免停机；失败则停 VM≤6 分钟全局冻结甲丙挂起）+VM 内格式化挂载 /mnt/chbackup2+CH 备份双写第二链 | CH 断连风险仅限停机回退路径；甲在途批将断连后幂等 resume | st-disk-ch-20260921 | planned | 挂载前核实 system.processes=0 |
| 2026-09-22 04:12 | 2026-09-22 | 04:40-07:30 | 独占窗 | 乙·磁盘清偿终局班 st-disk-final-20260922：裁定#399 废表 17 张验证→DROP+TI 瘦身 OPTIMIZE | CH 重 IO+删表；甲禁横跨本窗大批（批10 回填开工前必读本行错峰）；丙不碰 CH | st-disk-final-20260922 | done | 执行令 02:00-05:00 超窗顺延补记；17/17 DROP 04:41 完成；TI OPTIMIZE FINAL 整表打法触发清理饥饿有控熔断，改分区分批 05:30-07:1x 达成（parts 1299→821）；07:30 收窗 |
| 2026-09-22 04:20 | 2026-09-22 | 04:20-05:45 | 盘间 | 乙3d 手工冷库镜像首灌仍在飞（robocopy /MIR 137G 增量+25 万文件比对，G HDD 慢），再禁 DailyBackup 一晚防 06:00 撞同目标；完成后恢复 | G 盘 IO；CH 零影响 | st-disk-ch-20260921 | done | 05:45 收敛（97,718 文件双侧零差）；任务已恢复 Ready；F 活靶滞后=每夜 /MIR 收敛设计口径 |
