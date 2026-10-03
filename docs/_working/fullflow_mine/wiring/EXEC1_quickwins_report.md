---
ttl: task_bound
title: "速赢批执行报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# EXEC-1 断供速赢批执行报告（2026-10-04）

> 工单=断供速赢批 7 项；会话=st-datasop-20260930；CH 核验全部只读（ch_config reader 配方）。
> 互斥禁碰清单（A 队文件/config/*map*.yaml/trading_decision_map.yaml）零触碰。

## 逐项处置

### 1. cftc_positioning 刷新任务 — 落（转正，非 disabled 态）
- CH 实测：max(report_date)=2026-09-08 停更（周频 COT，哨兵行 12 天档长期真红无自愈腿=任务缺挂）。
- 源验证（当日实测）：`akshare macro_usa_cftc_c_holding` 返回 1938 行（≥3 期新周报待拉），源活。
- tasks.yaml 补 `cftc_positioning_refresh`（source: akshare_alt / schedule: daily_capital /
  incremental: false 全量幂等 4.1s / date_col: report_date），provider 能力 2026-09-18 已在
  （akshare_alt_provider `_fetch_cftc_positioning`），无需代码改动。

### 2. gold_etf_holdings 补挂任务 — 落（转正）
- CH 实测：max(trade_date)=2026-09-17 停更（零调度）。
- 源验证（当日实测）：`akshare macro_cons_gold` 返回 2881 行（CH 存量 2871，10 行新数据待拉）。
- tasks.yaml 补 `gold_etf_holdings_refresh`（akshare_alt / daily_capital / incremental: false
  全量幂等 ~59s 源限速 / date_col: trade_date）。

### 3. emotion_index auction 段挂 post_auction 槽 — 跳（无生产者，硬挂=假通道）
- CH 实测：emotion_index stage='auction' 存量 17 行至 09-23（v0.1.0，ts 恒 09:26）。
- 产线核实：`emotion_index_builder` 仅导出 STAGE_CLOSE_FINAL/STAGE_PRE_OPEN；
  `internal_compute_provider._fetch_emotion_index` 对其他 stage 显式 raise ValueError。
  auction 存量行=st-emomine-20260923 战役期手工产物，无生产代码路径。
- 结论：绑槽或补任务都会制造 R-021 假通道（首跑即 ValueError）。留待 builder 扩 auction
  stage 后再挂 post_auction 槽（槽位本身 09-23 已建好，无需动 schedule.yaml）。

### 4. market_etf_share_snapshot 快照任务复活 — 跳（任务在岗，断因=源死）
- 任务核实：`etf_share_snapshot_refresh` 在册且未 disabled（daily_capital 槽）。
- integrator_progress.db 实测：任务每日在跑、持续 FAILED——最近 2026-10-02 21:32 UTC，
  error=`fund_etf_spot_em 失败: Connection aborted / RemoteDisconnected`。
- 当日复测源：`push2delay.eastmoney.com` 连接被拒，源仍死。快照积累制 09-19 起断档不可回补
  （差分基线断档），哨兵 5 天档行（190 行）已持续真红——检测面已覆盖，无 config 侧可修项。
- 遗留：源恢复后任务自愈续写；东财 push2 族整站故障属 known_data_gaps 台账范畴（本批未登记，
  避免净零增量的重复条目——哨兵红即事实台账）。

### 5. market_signal_history 写侧挂钩 — 登记 manual-only（无 integrator 化任务形态）
- 表实测：329 行止 09-04；两管道全停（source=factor_synth 止 09-01，strategy_weight 止 09-04）。
- 生产代码核实：唯一落表写入器=`zephyr.signal_ashare.signal_history_writer`；生产任务名=
  `scripts/compute_signals.py`（管道 B，factor_composite_v1），其头注自 declared
  `[STARTUP] manual` + "[CONSUMERS] APScheduler 16:30 槽位（日循环自动化后挂接）"=接线规划中未落地。
- 无法入 tasks.yaml：compute_signals 是独立脚本（自读 CH 因子面板→自行落表），无
  provider capability 形态；硬造 capability=代施工越界。定性=manual-only（api_server
  /api/signal-run 可手动触发），登记即本报告。

### 6. supply_sentinel 阈值行补登 — 落（4 行）
- 工单 6 表中 road_freight_index（35 天档 136 行）/market_etf_share_snapshot（5 天档 190 行）/
  cftc_positioning（12 天档 266 行）/gold_etf_holdings（5 天档 273 行）**已有阈值行**，不重复登记。
- data_supply_sentinel.yaml 补 4 行（当日 CH 只读实测锚，reservoir 行范式）：
  | 表 | date_col | 档位 | 依据 |
  |---|---|---|---|
  | alt_sz_port_monthly | month | 45 天（月频） | max(month)=2025-07 但 ingest 09-30 在写=任务活源停发，点亮即真红 |
  | alt_sz_stat_monthly | report_date | 45 天（月频） | 同上（max=2025-06） |
  | futures_position | trade_date | trading_days/3 | 日频口径；实测停 09-23，点亮即真红 |
  | hog_spot_index | trade_date | 12 天（周频档） | distinct 周连续至 09-28，CFTC 周频档先例 |
- 真红两条（port/stat/futures 三行今日即红）属对的方向：红指向源端/通道停更，禁掰档过检。

### 7. a50_futures_daily 通道核验启用 — 落（翻转+注释更新）
- 语义核实：`overnight_boundary_reviser.py:211 enable_a50_channel` 全仓 grep 仅定义处+
  DEFAULT_CONFIG 构造，**无任何读取点**（inert 预留接口）；本模块 A50 消费实为规则自算交割日
  权重（L515-522），表数据消费在 intraday_l1_tracker（无条件直读，不经本开关）。
- 实弹嫌疑排除：模块产出 OvernightRevision 档位修正建议（final_shift→scenario_planner，
  观察记录链路），零下单语义。
- 处置：False→True，注释同步（原"数据源未接入默认关闭"前提已失效：a50_futures_daily_incremental
  任务在册 pre_market 槽、数据鲜至 2026-10-02）。翻转零行为增量，仅声明通道可用性成立。

## 改动文件
- `src/zephyr/data/config/tasks.yaml`（+33 行：cftc_positioning_refresh / gold_etf_holdings_refresh）
- `src/zephyr/data/config/data_supply_sentinel.yaml`（+37 行：4 张表阈值行）
- `src/zephyr/plan_engine/overnight_boundary_reviser.py`（+6/-1：a50 开关翻转+注释）
- 本报告（docs/_working/fullflow_mine/wiring/EXEC1_quickwins_report.md）

## 验证留痕
- tasks.yaml / data_supply_sentinel.yaml：yaml.safe_load 通过；tasks 总数 273，新增无重复
  （存量 `cohort_ledger_daily` 重复 1 处系改动前已有，他会话在途不代修）。
- overnight_boundary_reviser.py：py_compile 通过。
- 互斥清单零触碰；git 提交走 git_commit.py 单批 --files 显式清单。
