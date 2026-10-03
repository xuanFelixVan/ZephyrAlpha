---
ttl: task_bound
title: "速赢批执行报告r"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# EXEC-1r 断供速赢批重派执行报告（2026-10-04）

> 重派背景：前手 EXEC-1 超时阵亡，但其成果已先行落地 commit `2f9caef0ac`（cftc/gold 两任务
> +哨兵补盲 4 行+a50 通道翻转+前份报告 EXEC1_quickwins_report.md）。本重派（EXEC-1r）对工单
> 六项逐一**独立复核**（非抄前手结论），结论：4 项已在库、2 项按 manual-only/无生产者跳。
> 生产配置文件本批**零新增改动**（前手已提交）；本批交付=本报告+提交核实。
> 互斥禁碰清单（A 队文件/config/*map*.yaml/trading_decision_map.yaml）零触碰。

## 逐项处置（独立复核结论）

### 1. cftc_positioning 补 incremental 任务 — 已落（前手 commit 2f9caef0ac，本批复核通过）
- tasks.yaml `cftc_positioning_refresh`：source=akshare_alt（macro_usa_cftc_* 四报表宽转长）、
  schedule=daily_capital（既有资金面槽族，hog 同式）、incremental=false（全量幂等 4.1s/轮，
  四报表 81,270 行宽转长不宜增量）、date_col=report_date（PIT 锚）。
- 源态：2026-10-04 实测 macro_usa_cftc_c_holding 返 1938 行（≥3 期新周报待拉）→ active 态
  合规（源当日可验证，不落 disabled+reason 降级态）。停更 09-08 根因=零任务挂载，已治。

### 2. gold_etf_holdings 补挂任务 — 已落（同 commit，复核通过）
- tasks.yaml `gold_etf_holdings_refresh`：akshare_alt macro_cons_gold、daily_capital、
  incremental=false（2004-11 起 ~2,881 行全量，源端限速 59s 日度可承受）、date_col=trade_date。
- 源态：实测返 2881 行 vs CH 存量 2871 → 源活。停 09-17 根因同上，已治。

### 3. emotion_index auction 段挂 post_auction 槽 — 跳（无生产者，防假通道）
- 独立验证：`grep auction src/zephyr/alt_data/emotion_index_builder.py
  src/zephyr/data/providers/internal_compute_provider.py` = **零命中**（builder 仅
  close_final/pre_open 两 stage，tasks.yaml 亦仅此两任务）；schedule.yaml `post_auction` 槽
  在 tasks.yaml 与 src/**/*.py 均**零引用**。
- 挂槽即造"每日常态 fetch 失败"的假通道（fetch 必失败空挂任务=R-021 假任务形态），
  与全流通战役片段处置先例（"未验真的 source 落进来就是假任务"）同判。维持跳过；
  待情绪链真有 auction 段生产者（builder 增 stage+provider 增 fetch 面）再挂。

### 4. market_etf_share_snapshot 任务复活 — 已合规（任务在岗，零改动）
- tasks.yaml `etf_share_snapshot_refresh` 在库且**无 disabled 位**：source=akshare
  fund_etf_spot_em（全市场 ~1600 只单次快照）、daily_capital、incremental=false
  （快照积累制，相邻日差分=净申赎）。
- "09-18 首日即停"的旧源=fund_etf_scale_sse（实测仅 2025-01-15 单日，源退化）已在
  fallback_sources 注释登记弃用；现任务挂东财 spot_em 活源，首日停更根因=旧源死而非任务缺位。
  无 disabled 补 reason 义务、无补任务义务。

### 5. market_signal_history 写侧挂钩 — 跳（manual-only 性质确认，本报告即登记）
- 生产者实勘（grep 全仓）：写侧仅 `src/zephyr/signal_ashare/signal_history_writer.py`
  （模块头 [CONSUMERS] 自证）两触发点=**scripts/tasks/run/run_backtest.py（管道 A
  strategy_weight，BTRUN 回测出权重面板）+ scripts/compute_signals.py（管道 B
  factor_synth，日频多因子合成截面）**——均为脚本入口手动/批量触发，不在数据调度面
  （tasks.yaml/schedule.yaml 语义）内。
- 消费侧：dashboard api_server 只读两接口；framework_composer.py 模块头显式声明
  "不写 market_signal_history（管道 A 语义=子策略权重，禁污染）"。
- 结论：manual-only 性质成立，挂调度任务=错面接线；本登记即工单要求之"登记说明不做任务"。

### 6. supply_sentinel 阈值行补登（六表） — 已落（4 行前手 commit+2 行既有，复核通过）
六表全在库 `src/zephyr/data/config/data_supply_sentinel.yaml`，皆 reservoir 行范式
（注释带 CH 只读实测锚，禁为过检掰档位）：
| 表 | 档位 | 来源 |
|---|---|---|
| alt_sz_port_monthly | 45d（月频档） | 前手补盲（实测任务活、源端 15 个月未发新月报，真红指向发布侧） |
| alt_sz_stat_monthly | 45d（月频档） | 前手补盲（同上型） |
| road_freight_index | 35d | 既有行（源端 2026-08-21 后周报暂停仅月报在发，实测放宽至月度档） |
| futures_position | trading_days/3 | 前手补盲（日频口径：连续 4 交易日零行即红，周末长假不假红） |
| hog_spot_index | 12d | 前手补盲（周度数据日度拉取，一个发布周期+余量，日历日口径） |
| gold_etf_holdings | 5d | 既有行（美东工作日日频档+断供即差分基线断档注记） |
- 口径核对：日频>3 天（futures_position=3 交易日档合规；gold_etf_holdings=5 日历日档，
  美东发布节奏+周末跨度防假红，档位注释已自证）、月频>45 天（两 monthly=45 合规）。

## a50 通道翻转 — 本批不做（工单口径），但前手已翻：报 Owner 知悉
- 工单明示"a50 通道翻转不做，留 Owner 晨报裁定"；然前手阵亡前已在 `2f9caef0ac` 将
  overnight_boundary_reviser.enable_a50_channel False→True（其理由：任务在册+数据鲜至
  10-02+开关全仓零读取点=inert 预留接口零行为增量）。本批不回滚不扩大（回滚属 Owner
  裁定权），**仅在晨报单列此事实**供裁定追认或 revert。

## 本批改动与核实
- 生产文件改动：**零**（六项中 4 项前手已提交、2 项跳过有据）。
- 新增：本报告 `docs/_working/fullflow_mine/wiring/EXEC1r_quickwins.md`。
- yaml.safe_load 核验：tasks.yaml / data_supply_sentinel.yaml / schedule.yaml 解析通过
  （schedule.yaml 含 EXEC-2b 车道未提交 nightly_news_score 在途面，本批未吸收未触碰）。
- 前手成果 commit：`2f9caef0ac`；本报告 commit：见 git log（EXEC1r）。
