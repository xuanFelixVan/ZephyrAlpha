---
ttl: task_bound
---
# vhdx 季度压缩预检单（自动生成·提醒条目）

```json
{
 "date": "2026-10-09T15:55:42.404964",
 "due": false,
 "in_quarter_start_window": false,
 "days_since_last_compaction": 9.4,
 "days_since_source_note": "ok",
 "vm_internal_free_gb": 173.2,
 "vm_internal_total_gb": 631.9,
 "vhdx_size_gb": 586.5,
 "d_free_gb": 59.75,
 "vhdx_delta_gb": 0.0,
 "d_red_line_gb": 50.0,
 "d_below_red_line": false,
 "ch_chain_fresh": true,
 "ch_chain_note": "CH 链新鲜 1h (system.backups) + verified",
 "backup_flag_overall": "failed (last_backup_status=failed)",
 "ready_for_owner_window": true,
 "blocking_items": [
  "overall_backup_flag: last_backup_status=failed（注=整轮旗含非 CH 阶段，非 CH 链判据，见 ch_chain_note）"
 ],
 "note": "提醒条目——绝不自动执行压缩；实际停机压缩等 Owner 点名（裁定#380④/#381）。排窗须按实测增速与回收量（5.5/42.16 GiB 两次实跑、停机 4.3-4.8h），勿用 guest 空闲空间倒推收益，勿用本单旧口径'60-120 分钟'。"
}
```

CH 链新鲜时呈 Owner 点名压缩（全局冻结档）。**停机窗请按实跑口径 4.3-4.8 小时排**（09-28=17440s／09-30=15373s），勿用旧文案 60-120 分钟；回收量按 5.5~42 GiB 区间保守排，勿用 guest 空闲空间倒推。
