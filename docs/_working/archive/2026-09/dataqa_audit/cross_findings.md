---
ttl: task_bound
session: st-dataqa-20260920
audit: dataqa_20260920
---

# R4 · 交叉发现与修复建议（2026-09-20）

> 汇总 R1（CH 全库体检）/R2（缺口注册表复核）/R3（测试健康度）交叉结论，按风险分级给出修复建议。
> **本班零修复零写库**：全部建议默认归后续工单（数据线/final3 W8/Owner 门位），
> 每条给出建议归属与预计工量，供 Owner 与在飞战役直接决策。

## 0. 交叉结论（R1×R2×R3 互证出的四条主线）

1. **"止血已落地"≠"病好了"（R2 核心）**：daily_valuation 价格腿写前携带、index_valuation_daily
   派生列携带，两处 09-18 复核结论都在 09-20 被实测推翻（非零率仍 0%、派生列 FINAL 100% NULL+132
   重复组复发）。共性根因=**多写者+无 version 列**的表结构病没治，止血配方盖不住所有写路径。
   → P0-1/P0-2。
2. **max-date 哨兵对"内部洞"与"半死管线"双盲（R1×R2 互证）**：tick_data 09-17 全黑日
   （表级 max=09-18 完全不可见）；alt_sz_reservoir/rate_decision（管线活/数据停）靠腿级配置才抓住；
   index_quote/news_sentiment_window/auction_snapshot/crypto_kline_daily 四表根本无哨兵行。
   → P1-1。
3. **miniQMT 退役（09-18）的尾巴还在掉血（R2 时间线证据）**：index_quote（09-16 停）、
   auction 桥派生（09-17 起 WinError 10038）、crypto_kline_daily（09-18 半日/09-19 全断）、
   tick 09-17 真空日——四个断点全部落在退役前后 48 小时窗口。建议做一次**退役波及面收口巡检**
   （把所有 source=miniqmt/xtdata/桥依赖的任务逐个点验）。→ P1-2。
4. **测试侧健康度高但账面漂移集中在治理门（R3）**：65,311 通过 / 84 失败错（0.13%），flaky 修正后：
   稳定真账约 32 条是治理门测试**正确地**抓到了未登记库/地图漂移/阈值过期（门在工作是好消息）；
   约 35 条环境资源/测试污染假红（复跑转绿，含 WinError 1455 全家族与 trading decision_map 7 条
   顺序敏感假红）；真疑似 bug/回归 14 条；并发会话漂移 5 条已由归属会话自愈闭合。→ P2-1/P2-2。

## 1. P0 数据正确性（金融字段消费禁用级）

| # | 发现 | 证据 | 修复建议 | 工量 | 归属建议 |
|---|------|------|---------|------|---------|
| P0-1 | index_valuation_daily 派生列（cape_5y/cape_5y_pct/pe_pct/erp/erp_pct/pb_mrq）FINAL 100% NULL（8125/8125）+同键双行 132 组复发；每日仍有新写入持续产 NULL 版本 | R2 §2.1；哨兵列填充率腿破防 | 结构治本三选一：①加 version 列单写者合并；②internal_compute 重算管道接电为唯一派生写入方；③akshare 原始行与派生行分表。修复前**估值分位/ERP 消费一律禁用**（S2/regime 消费方请自查） | 1-2 天 | 数据线正门工单；表结构变更过 Owner 门 |
| P0-2 | daily_valuation 价格腿（close/amount/turnover 等 9 列）非零率 0/271,266；09-16=2000/09-18=3674 部分写入；**09-19 周六写入 3674 行**（非交易日污染）；增量任务连日 mock rows=0 SUCCESS 假绿 | R2 §2.1/§5；哨兵破防 | 落地 A1/A2/A3 三选一裁定（A1 改 Nullable 推荐）+周六运行加交易日 gate+给"0 行成功"加告警。修复前市值/换手消费禁用（维持已登记口径） | 裁定 0.5 天+施工 1-2 天 | Owner 门位（A1/A2/A3）+数据线施工 |

## 2. P1 断供风险（新断供/哨兵盲区）

| # | 发现 | 修复建议 | 工量 | 归属建议 |
|---|------|---------|------|---------|
| P1-1 | 哨兵盲区：index_quote/news_sentiment_window/auction_snapshot/tick_data 无阈值行；max-date 原理性看不见内部洞（tick 09-17 实证） | data_supply_sentinel.yaml 补 4 行阈值；新增"日历逐日 diff"检查器（本班反查逻辑可固化：交易日历×表内日期集合差集），挂夜间审计 | 0.5-1 天 | 数据线（配置+检查器各一小件） |
| P1-2 | miniQMT 退役波及收口：index_quote EOD 停（09-16）、auction 桥派生坏（WinError 10038+CH 连接冷却，fetch_perf 09-17 实锤）、crypto_kline_daily 半死（09-19=0）、tick 09-17 真空 | ①逐任务点验 source=miniqmt/xtdata/桥依赖清单并挂桥或 akshare 替代；②auction 派生任务加 socket 自愈重试；③crypto 采集链排查（09-18 半日形态=任务级非源级） | 1-2 天 | 数据线；桥 capability 立项部分归 T4 工单 |
| P1-3 | tick_data 09-17 全天双通道黑（tick_depth_5 同日 0）+09-18 半日（13.6M/正常 30M）——QMT 历史下载已退役、bdpan 归档 07-03 停更=**永久缺口** | 登记进 known_data_gaps（不可回补留痕，同 07/08 月八日缺口先例）；评估 kline_1min 合成近似 tick（需 data_source=synth 标记，Owner 门） | 登记 0.5 天 | 数据线登记；合成方案 Owner 门 |
| P1-4 | news_sentiment_window 09-15 起断（schedule 槽在、调度进程活、无任何执行痕迹=静默失败） | 排查 run_nightly_sentiment 静默失败（建议：该任务接入 fetch_perf 或独立心跳日志——"内部函数直写无痕"正是盲区成因） | 0.5 天 | 数据线 |
| P1-5 | stock_indicator 09-18 半日（1,000/5,565；09-18 11:09 full_refresh 后未再跑） | 重跑 stock_indicator 刷新补齐 09-18；检查该任务为何 09-19/20 未触发 | 0.5 小时 | 数据线 |
| P1-6 | technical_indicator parts 碎片风险未解除：1339 parts 高位、dwm 回填正在飞（09-19 单日 +289 parts）；09-15 曾 Code 241 全库拒查 | 回填结束+每日量一次 parts（本日基线=R1 §3.1）+显著回落后跑 OPTIMIZE FINAL（凌晨窗+停其他 CH 负载）；回填单进程串行纪律重申（交接包 §3 已载明） | 观察+1 次维护窗 | tilib 清欠班收口时办 |

## 3. P2 卫生类

| # | 发现 | 修复建议 | 归属建议 |
|---|------|---------|---------|
| P2-1 | R3 测试：治理门抓到的账面漂移 ~32 条稳定真账（D38 三个未登记库 domain_responsibility_layer_mapping/fail_open_register/standard_family_registry、decision_map R1/R2/R3/R6/R41 校验+R24 因子欠账复发、battle_map 33 步拓扑 3 条、blueprint AGENTS §编号引用 3 条、resource_profile/api_server cron 断言过期 4 条等）——**门在工作，账没跟上**；另 ~9 条同族失败经复跑判为测试污染假红（trading decision_map 校验 7+blind_spot 1+path 1），修测试隔离即可 | 归 final3 W8/rule_audit 后续批逐单清账（本班避让清单已排除这些文件）；D38 三库二选一登记=0.5 天 | final3 W8-4 统一办 |
| P2-2 | R3 疑似真 bug 14 条：zephyr SCD2 闭行行为变化 4（index_constituent 新行带 valid_to+同日重跑闭旧批）、context 循环导入 1、trading agent_health_monitor 模块缺失 1、ex_sor 撮合价口径 3、position max_z 公式 1、phase_f 空跑被护栏拦截 1、f_lifecycle phase_check 子进程挂起 1（git 并发 1 条经复跑改判假红） | 逐条立小工单；SCD2 四条优先（数据正确性边缘） | 各域 owner；SCD2 建议数据线先认领 |
| P2-3 | CH 内 17 张备份/污染表 35.41 GB（news_data 旧态两张 25.8 GB、etf tz_bak 五张 8.11 GB 等） | etf tz_bak 保留至时区修复后月度复盘再清（删除=Owner 门）；news_data 两张确认无消费后归档清理 | Owner 门位+数据线 |
| P2-4 | 1970 哨兵行 18 表约 43.6 万行（restricted_shares 34.3 万最大头；convertible_bond_list 1,054 行未登记） | 逐表 PIT 关死或补真值（破坏性=Owner 门）；convertible_bond_list 先补登记进 known_data_gaps | Owner 门+数据线 |
| P2-5 | 小表 parts 爆炸 12 张（macro_credit_money/macro_price_gauge/macro_activity_gauge 三张 1 行/part 极端形态） | 写入端攒批（60s 窗）+择机 OPTIMIZE FINAL；不改 schema | 数据线小件 |
| P2-6 | 注册表漂移：CH 246 表中 77 张 live 表未登记 data_asset_registry；etf_list 84 行/index_list 22 行存活行 list_date=1970（与登记结论矛盾）；research_report hot_value 列已消失；consensus_daily_repaired 已被部分回填（2026 年 18.3 万行）而登记仍写"2022 起 0 行" | 生成器口径重建 registry 覆盖（禁手工）；known_data_gaps 五处改册清单已列 R2 §2.1/§3 | 治理线+数据线各 0.5 天 |
| P2-7 | sector_fund_flow 09-19 周六写 450 行（五时点任务未卡交易日）；daily_valuation 同病（09-19 写 3,674 行） | 两任务加交易日 gate（trade_calendar 判断） | 数据线小件 |
| P2-8 | stock_basic 09-16 快照缺失（已登记 accepted 家族新发一次） | 扩展 stock_basic_snapshot_days_missing 条目 end_date 或新条目 | 数据线改册 |

## 4. 明确不建议做的（负面清单）

1. **不要**为 tick 09-17/08-06 类永久缺口再尝试 QMT 通道（09-18 已退役，两度实证够不到）。
2. **不要**在 dwm 回填未停前对 technical_indicator 跑 OPTIMIZE FINAL（IO 对撞+内存风险，交接包 §0 判据未满足）。
3. **不要**物理 DELETE 任何 1970 行/墓碑行（禁裸 DELETE 铁律+PIT 关死先例）。
4. **不要**据本报告直接改 tasks.yaml/sentinel（本班避让清单；改册走数据线正门工单）。

## 5. 数字速查（三报告互引）

- CH：246 表 / 126.2 亿行 / 426.65 GB / 27,856 parts；1970 parts=49 全定位；备份污染表 35.41 GB。
- 缺口注册表：45 条复核=31 一致、8 实质变化、6 轻微口径；未登记新断供 7 项（N1-N7）+卫生 7 项（W1-W7）；哨兵 55 腿 9 破防、4 表无哨兵行。
- 测试：131 域（governance 拆 90 子域）/3,523 文件/65,311 passed/68f+16e/231 skipped；
  flaky 修正后：环境资源/测试污染假红约 35 条（复跑转绿）、稳定真账约 32 条、疑似 bug 14 条、并发会话漂移 5 条（已自愈闭合）。

## 6. 附 · CH live 未登记表清单（data_asset_registry 精确匹配缺失，77 张）

> 判定口径：entity_name==`库.表` 精确匹配；备份/污染表已先行分类不计入。

| 表 | 行数 | 引擎 |
|----|------|------|
| c1_backtest.crisis_gate_log | 0 | MergeTree |
| c1_backtest.decision_daily | 43 | MergeTree |
| c1_backtest.hypothesis_precheck | 58 | MergeTree |
| c1_backtest.regime_snapshot_history | 3,621 | MergeTree |
| c1_backtest.regime_state_anchored | 4,469 | ReplacingMergeTree |
| c1_backtest.sim_attribution_daily | 6 | ReplacingMergeTree |
| c1_backtest.sim_platform_journal | 8 | ReplacingMergeTree |
| c1_backtest.sim_pocket_daily | 68 | ReplacingMergeTree |
| c1_backtest.sim_trade_log | 17 | ReplacingMergeTree |
| c1_backtest.strategy_screen | 1,315 | MergeTree |
| c1_market.account_nav_daily | 0 | ReplacingMergeTree |
| c1_market.agri_wholesale_index | 11,638 | ReplacingMergeTree |
| c1_market.alt_fx_rate_ecb | 69 | ReplacingMergeTree |
| c1_market.board_index_1m | 0 | ReplacingMergeTree |
| c1_market.board_index_tick | 5,564 | ReplacingMergeTree |
| c1_market.cftc_positioning | 81,270 | ReplacingMergeTree |
| c1_market.commodity_futures_main | 126 | ReplacingMergeTree |
| c1_market.commodity_spot_price | 756 | ReplacingMergeTree |
| c1_market.daban_board_event | 936 | ReplacingMergeTree |
| c1_market.dividend_tax_node | 0 | View |
| c1_market.edb_data | 0 | ReplacingMergeTree |
| c1_market.etf_benchmark | 0 | ReplacingMergeTree |
| c1_market.execution_report | 1 | ReplacingMergeTree |
| c1_market.futures_warehouse_receipt | 2,900,636 | ReplacingMergeTree |
| c1_market.gold_etf_holdings | 2,871 | ReplacingMergeTree |
| c1_market.hl_funding_history | 4,660,219 | ReplacingMergeTree |
| c1_market.hl_liquidation_raw | 2 | ReplacingMergeTree |
| c1_market.hl_oi_snapshot_daily | 468 | ReplacingMergeTree |
| c1_market.hl_perp_snapshot_daily | 468 | ReplacingMergeTree |
| c1_market.index_adjustment | 14,763 | ReplacingMergeTree |
| c1_market.ipo_calendar | 7,608 | ReplacingMergeTree |
| c1_market.ipo_schedule | 0 | ReplacingMergeTree |
| c1_market.judgment_daily_plan | 2 | MergeTree |
| c1_market.judgment_intraday_market_state | 4 | MergeTree |
| c1_market.judgment_next_day_forecast | 3 | MergeTree |
| c1_market.judgment_plan_verification | 0 | MergeTree |
| c1_market.l2_tick | 0 | ReplacingMergeTree |
| c1_market.limit_up_pool | 855 | ReplacingMergeTree |
| c1_market.macro_activity_gauge | 436 | ReplacingMergeTree |
| c1_market.macro_credit_money | 584 | ReplacingMergeTree |
| c1_market.macro_daily_gauge | 4,685 | ReplacingMergeTree |
| c1_market.macro_pmi_gauge | 224 | ReplacingMergeTree |
| c1_market.macro_price_gauge | 496 | ReplacingMergeTree |
| c1_market.macro_trade_gauge | 224 | ReplacingMergeTree |
| c1_market.margin_target_adjustment | 0 | ReplacingMergeTree |
| c1_market.market_breadth_snapshot | 125 | ReplacingMergeTree |
| c1_market.market_cffex_member_ranking | 6,201 | ReplacingMergeTree |
| c1_market.market_china_bond_yield | 6,216 | ReplacingMergeTree |
| c1_market.market_convertible_bond_clause | 630 | ReplacingMergeTree |
| c1_market.market_etf_share_snapshot | 3,242 | ReplacingMergeTree |
| c1_market.market_fund_flow_daily | 120 | ReplacingMergeTree |
| c1_market.market_index_meta | 0 | ReplacingMergeTree |
| c1_market.market_pattern_certification | 66 | ReplacingMergeTree |
| c1_market.msci_adjustment | 0 | ReplacingMergeTree |
| c1_market.ndrc_fuel_price | 329 | ReplacingMergeTree |
| c1_market.news_sentiment_window | 19,811 | ReplacingMergeTree |
| c1_market.northbound_hold_snapshot | 57,083 | ReplacingMergeTree |
| c1_market.rate_decision_calendar | 3,086 | ReplacingMergeTree |
| c1_market.reconciliation_differences | 0 | ReplacingMergeTree |
| c1_market.road_freight_index | 86 | ReplacingMergeTree |
| c1_market.sector_constituent_snapshot | 190,248 | ReplacingMergeTree |
| c1_market.sector_fund_flow | 1,917 | ReplacingMergeTree |
| c1_market.stk_limit | 9,193,985 | ReplacingMergeTree |
| c1_market.stock_basic | 9,025,127 | ReplacingMergeTree |
| c1_market.stock_valuation | 0 | ReplacingMergeTree |
| c1_market.suspend | 0 | ReplacingMergeTree |
| c1_market.tick_depth_5 | 30,406,868 | ReplacingMergeTree |
| c1_market.us_futures_intraday | 563 | ReplacingMergeTree |
| c3_fundamental.dividend | 116,334 | ReplacingMergeTree |
| c3_fundamental.ex_dividend_event | 57,715 | ReplacingMergeTree |
| c3_fundamental.ir_activity_extracted | 30 | ReplacingMergeTree |
| c3_fundamental.ir_activity_record | 30 | ReplacingMergeTree |
| c3_fundamental.irm_interactive_extracted | 74 | ReplacingMergeTree |
| c3_fundamental.irm_interactive_qa | 500 | ReplacingMergeTree |
| c3_fundamental.news_data | 8,348,853 | ReplacingMergeTree |
| c3_fundamental.pdf_forecast_extracted | 192,365 | ReplacingMergeTree |
| c3_fundamental.repurchase | 10,936 | ReplacingMergeTree |
