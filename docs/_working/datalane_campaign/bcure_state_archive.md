---
ttl: task_bound
title: bcure 链 state 归档证据单（T7 收官，2026-10-10）
session: st-datalane-20261010
completes_when: 追加令 T7 关账（进程停止+归档落冷库+使命归属结论入台账 §十）
---

# bcure 链 state 归档证据单（T7，2026-10-10 16:1x）

- **原始归档（8 件全量，逐件 sha256 见包内 SHA256SUMS.txt）**：
  `F:/zephyr_cold/50_archive/by_project/zephyralpha/bcure_state_archive_20261010/`
  （唯一冷储；docs/_working 目录契约禁 .log/.py，故册内只留本证据单）。
- **包内容**：`shard_done.txt`（完成月账：201906/201911/202103/202104/202107 共 5/93）、
  `ti_shard_selfheal.log`（自愈驱动主日志，停点实录"内存闸等 10min"段在尾）、
  `ti_shard_selfheal_driver.py`（驱动本体）、`ti_monthly_shard_driver.py`、
  `ti_daily_full_driver.py`、`ti_monthly_shard.log`、`ti_daily_full.log`、`ti_full_refresh.log`。
- **停止证据**：Stop-Process 26768 后进程表复核=0；停点=内存闸等待期（无月 INSERT 半程）。
- **使命归属结论**：夜跑新码（T1 停算+P1 闭环）结构性取代其 2019-2021 月粒度重算使命
  （追加令裁定已下）；已完 5 个月保留生效，2021-08+ 月份由夜跑 nightly 全史腿逐日覆盖。
