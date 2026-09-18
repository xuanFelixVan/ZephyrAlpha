---
ttl: task_bound
completes_when: 全流通战役收口报告归档
---

# req_sentinel_02 · intraday_sector 五任务停档期 + 三个 disabled 事件表任务的台账归因

**事实（2026-09-18 亲验，只读）**
- `c1_market.kline_sector_intraday`：近端只有合成行——`data_source` 分布
  tdx 止于 **2026-09-10**（月内 2,274,652 行）、synth_sh 至 09-15（279,560 行）、
  synth_eq 至 09-14（139,780 行）；本表"看起来日更"完全由合成行撑起来。
- 5 个 `kline_sector_*min_incremental`（`schedule: intraday_sector`，*/5 9-15）仍在唤醒。
- `c3_fundamental.audit_opinion`（max announce=2026-05-29）与 `rights_issue`（2026-06-30）
  的增量任务均为 `extra.disabled: true`；`c3_fundamental.dividend` 旧 miniqmt 任务
  `schedule: disabled`（2026-09-09 方案D，字段名与东财 20 列 schema 不匹配）。
- 哨兵侧本车道已把三件事全部点亮：tdx 真值腿红（rows=0<100000）、dividend 业务腿红（79>30）、
  audit/rights 走 240 天跨披露季档（暂不红，但任务 disabled 这一事实调度侧由 catchup_guard 盯）。

**为何上裁**：停用盘中任务是**生产切换**（改变下游可见数据：合成分区若一并消失，
依赖它的板块分钟线消费方会拿空），不在哨兵车道权限内；三个 disabled 任务是"待替代"
还是"待退役"属数据源台账决定（且退役=条目净删=Owner 门位）。

**请裁**：
- 甲：批准停 5 个 intraday_sector 任务的档期（片段 ⑤ 原意），并明确合成行的去留口径；
- 乙：批准"不停任务、只把真值腿保持常红直到 mootdx/tdx 通道修复"，即本车道当前状态；
- 丙：`audit_opinion / rights_issue / dividend` 三任务替代方案（bdpan / akshare / 东财 20 列
  schema 对齐）由哪条车道立项。

**本车道未停等**：已按乙执行（哨兵常红 + 不动任务），并已在 dividend 上并入 akshare 承接任务
（`dividend_incremental_akshare`，schedule=weekend_calibration，实测该源 capability 在册、
写目标经 `get_registry().table("fund_dividend")=c3_fundamental.dividend` 与任务一致）。
