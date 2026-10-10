---
ttl: task_bound
title: T4 夜矿断供补级联小批验门方案
session: st-datalane-20261010
completes_when: 五门放行+逐门实测入附录
---

# T4 夜矿断供补·表族级联小批验门方案（sid=st-datalane-20261010）

> 开班令 T4：后复权价/技术指标/情绪指数断在 2026-09-30（普通日线到 10-09）；等在跑回填
> 收官后单开；先出本方案再跑。断供窗实测=OD-9（交易日历该窗 2 个交易日：10-09+1）。

## 〇、断供链定位（勘察结论）

- 根：`c1_market.kline_daily_hfq` 停在 09-30。daily 指标源已切 hfq（B4-M2，tasks.yaml 语义
  变更点），故 technical_indicator max=09-30 是 hfq 断供的**下游投影**，非独立断点。
- hfq 供给链=`kline_daily_hfq_incremental`（integrator 任务，DAG：adj_factor→kline_daily_hfq；
  akshare_provider._fetch_kline_daily_hfq 实现腿）。停更根因待诊断（任务日志/调度在册性）。
- 周月级联：`kline_weekly_hfq/kline_monthly_hfq` 的增量任务仍挂 miniQMT 旧基座（WO-004 判错
  基座；chiefc R14"miniqmt 悬空→internal"申请包**待批未执行**）——周月线断供更早且源悬空。
- 情绪指数：`c1_market.emotion_index` close_final 10 月 0 行（快照器 T5 镜像到 10-09 时点
  max_trade_date=10-09 只含 pre_open 行，close_final 仍止 09-30）。

## 一、小批验门方案（先门后量）

**门 1（hfq 日线，2 标的小批）**：`kline_daily_hfq_incremental` 限 2 标的（如 000001/600519）
补 10-01..10-09 窗 → 验收=①行数与交易日历一致（该窗 2 交易日）②lineage=recalc_raw_x_adjfactor
（B4-M2 血统标记）③抽 1 键对拍 raw×adj_factor 逐位（±1e-9）④与 09-30 末bar 链续（昨收衔接）。

**门 2（全市场放量）**：门 1 全绿→同任务去标的限全市场同窗 → 验收=行数=2 交易日×在册 A 股
数（对齐 kline_daily 同窗 distinct symbol±0.5%），零空洞。

**门 3（TI daily 级联）**：`backfill_technical_indicator_dwm --periods daily
--start-daily 2026-09-30`（收官后单开；T1 停算已生效=退役列不写）→ 验收=max(trade_date)
到 10-09、单趟行数量级 ≈2 日×全市场、10-09 行的 hfq 源指标抽样对拍本地复算。

**门 4（周月跟不跟的口径声明）**：**跟，但走 WO-004 级联路径不跑 miniQMT 旧基座**——
用 recalc_hfq_cascade 同构聚合（ISO 周/自然月窗）只重算受影响 ISO 周（10-05..10-11 所在周）
与 10 月自然月：先 `--create` 影子分片→对拍（周↔日/volume 守恒/覆盖不缩水）→ 受影响分区
swap。禁直接跑 `kline_weekly_hfq_incremental`（旧基座续算是 WO-004 判死路径）。
若 R14 申请包在本班在途获批，改走其正门并回填本节。

**门 5（情绪指数）**：emotion builder 腿（internal_compute_provider._fetch_emotion_index 路由）
补 10-09（+缺的另一交易日）→ 验收=close_final 当日行存在且快照器（T5）镜像可见。

## 二、执行序（全部排在 53472/34644 收官确认后，禁双开）

1. 收官确认：进程表零 dwm/backfill 腿 + TI 表 max(ingest_ts) 静默 ≥30min。
2. 门 1→门 2→门 3→门 4→门 5 顺序放行，任一门红即停手上报（推翻总指挥令=正常）。
3. 逐门实测数进台账 §四；完成后 10 月 OOS 面解锁（凡 OOS 伸到 10 月的考试卡不再判死），
   通知面随 99_delivery。

## 附录：实测记录（滚动）

- [待腿收官后填]
