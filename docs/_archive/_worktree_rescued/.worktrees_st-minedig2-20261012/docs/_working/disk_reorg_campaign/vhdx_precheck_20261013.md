---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
---
# vhdx 季度压缩预检单（自动生成·提醒条目）

```json
{
 "date": "2026-10-13T06:04:40.044314",
 "due": true,
 "in_quarter_start_window": false,
 "days_since_last_compaction": null,
 "days_since_source_note": "无 last_vhdx_compaction_result=ok 记录",
 "vm_internal_free_gb": 208.1,
 "vm_internal_total_gb": 631.9,
 "vhdx_size_gb": 560.9,
 "d_free_gb": 65.75,
 "vhdx_delta_gb": -25.6,
 "d_red_line_gb": 50.0,
 "d_below_red_line": false,
 "ch_chain_fresh": false,
 "ch_chain_note": "CH 链 5h 内新鲜但 last_ch_backup_verified 非真",
 "backup_flag_overall": "failed (backup_state.json 不可读)",
 "ready_for_owner_window": false,
 "blocking_items": [
  "ch_chain: CH 链 5h 内新鲜但 last_ch_backup_verified 非真",
  "overall_backup_flag: backup_state.json 不可读（注=整轮旗含非 CH 阶段，非 CH 链判据，见 ch_chain_note）"
 ],
 "note": "提醒条目——绝不自动执行压缩；实际停机压缩等 Owner 点名（裁定#380④/#381）。排窗须按实测增速与回收量（5.5/42.16 GiB 两次实跑、停机 4.3-4.8h），勿用 guest 空闲空间倒推收益，勿用本单旧口径'60-120 分钟'。"
}
```

CH 链新鲜时呈 Owner 点名压缩（全局冻结档）。**停机窗请按实跑口径 4.3-4.8 小时排**（09-28=17440s／09-30=15373s），勿用旧文案 60-120 分钟；回收量按 5.5~42 GiB 区间保守排，勿用 guest 空闲空间倒推。
