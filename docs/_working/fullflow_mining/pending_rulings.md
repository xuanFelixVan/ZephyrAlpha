---
ttl: task_bound
creation_token: m5-sched-pending-rulings-20260925
---

# M5 车道 pending_rulings（Owner 待裁项台账；一行一案，裁决后移出）

- [S2 收尾·PROTECTED-PATHS 门位] tilib 夜跑链收编受阻待批：`backfill_night.bat`（计划任务 tilib_indicator_backfill_nightly Execute 真实指向件，现 live 版引用已灭的 `.runtime/tmp/tilib-probe/` 夜夜 exit 1=04 册 S2 根因）须 `.gitignore` 加 `!scripts/data/backfill_night.bat` 白名单方可入库，但 `.gitignore` 系 PROTECTED-PATHS（ARCH-MODEL-LIFECYCLE-001）——无 [ARCH-APPROVAL] 可引登记 issue、无 active 裁定 approved_paths 覆盖（全册仅 #410 覆盖 rules/）。bat+gitignore 改动已备妥 worktree csx-m5s1（bat=委托 tracked ps1 链 ruling #399 分片 runner+日志落 data\runtime\tilib_nightly\，实测干跑全链 exit 0；ps1 净化件已单独入队 qid 0041）。请 Owner 裁：①批 .gitignore 白名单行（新登记裁定或 approved_paths）→ 本车道即补队提交；或 ②Owner 直接重注册任务 Execute 指向 backfill_night.ps1（同为 Owner 门位）→ bat 收编作废、live 链即修复。裁定登记同 commit 原子（RULE-RULING）。
