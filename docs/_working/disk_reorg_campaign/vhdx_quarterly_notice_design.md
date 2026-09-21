---
ttl: task_bound
completes_when: Owner 点名压缩执行后本稿归档（排班条目转入执行）
session: st-disk-ch-20260921
issue: VHDX-NOTICE-DESIGN-20260920
---

# vhdx 季度压缩排班条目 + 到点通知机制设计稿（裁定#380④ 唯一点名项）

> 铁律先行：**本机制只提醒、不执行**。vhdx 压缩=全项目唯一"数据面停机"操作（全局冻结档，
> 甲丙全停），属宪法 §5 high 域 Owner 门位——到点后等 Owner 点名排期，绝不自动停机（裁定#381：
> 全场唯一需 Owner 点名的动作=vhdx 压缩）。

## 1. 排班条目

| 项 | 值 |
|---|---|
| 条目名 | vhdx 季度压缩预检（提醒条目） |
| 节奏 | 每季度首月前 7 天触发检查；另加触发式：距上次成功压缩 ≥90 天 |
| 载体 | backup.ps1 STAGE 4b（备份成功事件链——禁 cron 红线合规，复用既有每日 06:00 兜底任务，零新增 schtasks） |
| 实现 | `python scripts/ch/rolling_archive_reconciler.py --precheck`（已实现，2026-09-20 实跑验证） |
| 产物 | `docs/_working/disk_reorg_campaign/vhdx_precheck_YYYYMMDD.md`（五项指标预检单） |
| 执行 | **不执行**。Owner 看到预检单后点名，才按全局冻结档排停机窗 |

## 2. 预检单五项指标（季初自动采集）

1. VM 内部空闲（实测 2026-09-20：154.7G，红线 ≥150G）
2. vhdx 文件体积（实测 599.0G；压缩目标 ≤450G）
3. 备份新鲜度（backup_state 双状态）
4. 距上次成功压缩天数（state 文件 `last_vhdx_compaction`，压缩执行后回写）
5. 触发类型（季初窗 / 90 天触发式）

## 3. 到点通知机制（设计稿，形式暂定=裁定④）

**通知形式（暂定，不实现弹窗）**：
- **每日晨报一行**：预检单到期未处置期间，晨报固定输出一行
  `[vhdx-precheck] 季度压缩预检单已生成（<日期>），待 Owner 点名排窗`——挂每日晨报生成器的待办段（下次晨报改造批顺手接入，接口=读 vhdx_precheck_*.md 最新件是否 7 天内未读）。
- **仪表盘横幅**：services_registry 增加一个 `vhdx_precheck` 探测器（type: file_fresh，
  dir=预检单目录，fresh 窗=季度首 14 天），dashboard 顶部横幅区显示"待 Owner 处置"黄条。
  前端渲染改动归前端负责人会话排期（本稿只出接口约定）。
- **弹窗**：不实现（裁定④明示）。

## 4. 压缩执行剧本（Owner 点名后，全局冻结档）

```
F 新鲜备份前置（backup.ps1 -Force 实跑 ok）
→ 声明板登记全局冻结窗（甲丙全停确认：SessionRegistry 无活跃会话）
→ 停 VM（Get-VM zephyr-ch | Stop-VM -SaveState 备选 ShutDown）
→ 管理员 Optimize-VHD -Path D:\HyperV\VMs\zephyr-ch\data.vhdx -Mode Full（60-120 分钟）
→ 起 VM → CH 复活探针（uptime/version/表数/tick 抽查一条）
→ 全链健康探针（ch_parts_monitor 无告警 + dashboard 全绿）
→ 当日备份补跑 ok + state 回写 last_vhdx_compaction
→ 验收：vhdx ≤450G；D 盘剩余显著回升；VM 内部空闲维持 ≥150G
```

## 5. 2026-09-20 首张预检单

已生成：`vhdx_precheck_20260920.md`（触发=距上次压缩从未记录；内部空闲 154.7G 绿；
vhdx 599G；备份新鲜绿）。**状态=待 Owner 点名**。
