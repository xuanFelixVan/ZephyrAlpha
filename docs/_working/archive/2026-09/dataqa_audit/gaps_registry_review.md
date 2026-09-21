---
ttl: task_bound
session: st-dataqa-20260920
audit: dataqa_20260920
---

# R2 · 缺口注册表现状复核 + 未登记断供反查（2026-09-20）

> 执行：st-dataqa-20260920（通宵总令·分包B）。纯只读，零修复零写库（含**不改** known_data_gaps.yaml——
> 本报告即改册依据，落册归数据线/final3 W8-4）。
> 真源：`src/zephyr/data/config/known_data_gaps.yaml`（1133 行，45 条目，last_updated 2026-09-19）。
> 探针：`.runtime/tmp/dataqa/probe_r2.py` / `.runtime/tmp/dataqa/probe_r2b.py` / `.runtime/tmp/dataqa/probe_r2c.py`（DatabaseService reader，轻查询）。
> 输出：`.runtime/tmp/dataqa/out/r2_checks.json` / `.runtime/tmp/dataqa/out/r2_followup.json` / `.runtime/tmp/dataqa/out/r2_final.json` / `.runtime/tmp/dataqa/out/r2_sentinel.json`。
> 证据等级：未标注者均 **[亲验]**（2026-09-20 15:40-16:20 窗口实测）；fetch_perf 归因=[亲验-日志]。

## 0. 一页结论（TL;DR）

**A. 注册表 45 条逐条复核：31 条现状与登记一致；8 条有实质变化需改册（其中 3 条恶化、2 条过时、
3 条有新进展）；6 条轻微口径修正。详见 §2/§3。**

**B. 反查发现 7 项未登记的新断供/复发（本报告最高价值项）**——全部发生在 2026-09-14 之后，
注册表与哨兵均未覆盖：

| # | 表 | 症状 | 归因（fetch_perf/进程取证） | 建议级别 |
|---|----|------|------------------------------|---------|
| N1 | c1_market.index_valuation_daily | 派生列（cape_5y/pe_pct/erp）FINAL **100% NULL 复发**+同键双行 **132 组复发**（09-18 复核时尚为 0 组） | 双写者无 version 列结构病未治；止血（写前携带）未拦住 09-17 的 4 行双写 | **P0** |
| N2 | c1_market.daily_valuation | close/amount/turnover 非零率仍 **0/270,260**；09-16=2000、09-18=3674 部分写入；**09-19 周六写 3674 行**（非交易日污染）；增量任务连日 source=mock rows=0 SUCCESS 空转 | 行情腿写前携带止血无效；"0 行成功不告警"未修 | **P0** |
| N3 | c1_market.tick_data + tick_depth_5 | **09-17 双通道全黑**（tick_data=0 且 tick_depth_5=0 行，交易日）；09-18 tick_data 半日 1364 万行（桥切换） | miniQMT 收摊与桥接管之间的真空日；QMT 历史下载已随 9/18 退役=**永久缺口** | P1 |
| N4 | c1_market.index_quote | max 停在 09-16（修复后曾恢复 240 点/日，现 09-17/18=0） | fetch_perf 09-16 后无任何 index_quote 记录；ZephyrAlpha_IndexMinuteEOD（xtdata）随 miniQMT 退役死亡 | P1 |
| N5 | c1_market.news_sentiment_window | max window_date=09-14，09-15 起连缺 4 个交易日 | schedule.yaml:169 槽位在（cron 20 8 * * *）、调度进程活、fetch_perf 无痕（内部函数直写无记录）——需查 run_nightly_sentiment 静默失败 | P1 |
| N6 | c1_market.auction_snapshot / auction_book | max 停在 09-16（此前"桥派生持续累积"） | fetch_perf 09-17 实锤：`qmt_bridge auction 派生失败 [WinError 10038] 非套接字操作` + `ch_writer get_client() 返回 None（连接冷却期）` | P1 |
| N7 | c1_market.crypto_kline_daily | 108 行/日 → 09-18 只 51 行、**09-19=0**（7×24 资产） | daily_crypto 任务半死（09-18 半日+09-19 全断）；与 miniQMT 退役时点吻合需排查依赖 | P1 |

**C. 哨兵实测**：`supply_sentinel.check_tables()` 09-20 实跑 checked=55 / breached=9（§4）。
9 破防全部与上表/注册表对得上——哨兵列填充率新腿成功抓住 N1/N2；但 **index_quote/news_sentiment_window/
auction_snapshot/tick_data 四张无哨兵行**（盲区），且 tick_data 09-17 属**内部洞**（max-date 哨兵原理性不可见）。

**D. 其他卫生发现**：stock_basic 09-16 快照缺失（已登记 accepted 家族新发一次）；stock_indicator 09-18
半日 1000/5565；sector_fund_flow 09-19 周六快照 450 行（调度未卡交易日）；etf_list 84 行存活行
list_date=1970（与"墓碑清零"结论矛盾）；index_list 22 行存活行 1970；consensus_daily_repaired
已被部分回填（2026 年 18.3 万行出现，2022-2025 仍缺）；research_report 的 hot_value 列已不存在（登记口径过时）。

## 1. 复核方法

1. monitoring / open / reopened / no_source 全部条目逐条实跑验证 SQL（轻查询，FINAL 视角+raw 视角双口径）；
   resolved/completed/accepted 条目抽 24 条重点复核（历史行数/关键日期/修复断言）。
2. **反查**：R1 全库 246 表 max(业务日期) vs 交易日历（trade_calendar max_le_today=2026-09-18），
   滞后表先对照 known_data_gaps 已登记集合，剩余为"未登记候选"，逐个用 fetch_perf 日志+
   调度进程取证归因（§0.B 表即成果）。
3. 哨兵实测：直接调用 `zephyr.data.supply_sentinel.check_tables()`（只读）。

## 2. monitoring / open / reopened 条目逐条现状（8 条实质变化 + 一致项）

### 2.1 有实质变化（需改册）

| 条目 id | 注册状态 | 09-20 实测 | 判定 | 建议新状态 |
|---------|---------|-----------|------|-----------|
| index_valuation_daily_duplicate_rows | monitoring | FINAL 8125 行中 cape_5y/erp NULL **8125/8125=100%**；raw 8257 行、同键双行 **132 组**（000300/000905 于 08-28/08-31/09-17 等）；每日仍有 2 行新写入（09-17 写了 4 行=双写同日） | **恶化**：09-18 复核"dup=0+止血落地"结论失效，缺口期<3 天 | 退回 **open**（结构根因=无 version 列双写者，止血配方对该路径无效） |
| daily_valuation_2026_09_10_missing | reopened | FINAL 268,260 行；非零率仍 0%；09-16=2000、09-18=3674 部分写入；**09-19（周六）3674 行**；增量连日 mock rows=0 SUCCESS | **恶化**：行数恢复但数值腿全零未愈+周末污染新形态 | 维持 reopened 并追加 09-16/18/19 三日新证据 |
| daily_valuation_price_legs_zero_mislabeled | open | close/amount/turnover 非零 0/270,260；data_source 100% local_valuation（真实写者 akshare）。**红蓝复跑（当晚）：raw 已涨至 271,266（周日仍 +1,006 行）——零值污染仍在活体增长** | **未愈**：写前携带止血未生效（与上条同根）+写入方周日仍在跑 | 维持 open；A1/A2/A3 三选一裁定仍待 Owner |
| etf_minute_tz_split_pre_202607 | monitoring（等 Owner 批 --execute） | 5 张 `*_tz_bak_20260918` 全在；live 表旧纪元行（hour∈[1,7] 且 ≤06-30）= **0**（bak 表=303,422,787）→**修复已执行** | **过时**：登记写"待批"，实际已换名修复（禁裸判谁执行——但 bak 表名与修复件设计完全一致） | 改 **completed（已执行）**+记回滚窗口（5 张 bak 共 440,481,332 行/8.11 GB，见 R1 §5） |
| consensus_daily_value_cols_pit_broken | open（repaired 2022 起 0 行断供） | repaired 现 **1,655,363 行**（登记时 343,838）：2017=300,566/2018=349,219 新出现，**2026 年=182,734 行（max 09-15）新出现**；2022-2025 仍全缺 | **部分好转**：断供段被部分回填（2017-2018+2026），2022-2025 仍断 | 更新 root_cause 数据面；open 维持（2022-2025 待回补） |
| research_report_hot_value_rating_change_empty | open | `hot_value` 列**已不存在**（system.columns 实测无此列；rating_change 在） | **口径过时** | 更新登记：hot_value 已随 schema 变更消失（或查 schema 变更记录），rating_change 空列维持 |
| reservoir_level_source_stale | monitoring | max(tdate)=07-31（lag 51 天）、max(ingest_ts)=09-18（采集活）；09-15 单日拉 66.7M 行也只到 07-28 | **一致**（半死管线持续） | 维持 monitoring |
| technical_indicator_duplicate_rows_ingest_ts | monitoring | 仅 2026-08 单月即 109,309 个 (symbol,trade_date) 重复组（月行数 3515 万）；**且 dwm 回填正在飞**（PID 30160） | **一致**（重复持续累积；argMax 口径仍是必须） | 维持 monitoring；注记回填期重复会进一步增多 |

### 2.2 现状与登记一致（抽验全对上，维持原状态）

| 条目 | 实测锚点 |
|------|---------|
| tushare_hk_hold_2026q2_code_collision (monitoring) | FINAL 30,574 = uniqExact 30,574；Q2 4,065/4,065 唯一 ✓ 拦截件在位 |
| index_constituent_snapshot_gaps (monitoring) | 近 7 交易日 7,721-7,722 行/日 ✓；08-31 半截 300 行仍在（PIT 关死择期） |
| kline_etf_60min_depth_windows (monitoring) | 近 6 交易日覆盖 1,656→1,673 只/日 ✓（历史深窗工单仍挂） |
| futures_warehouse_receipt_shfe_archive_cap (no_source) | CZCE 1,998,725 行至 09-18 活；SHFE 901,911 行停 2025-11-17 ✓ |
| rate_decision_calendar_jin10_retired (no_source) | max(decision_date)=2025-10-30 ✓（管线日更活：670 parts 佐证） |
| dividend_plan_miniqmt_retired (no_source) | 2026-08/09 = 0/0 行（7 月仅 43 行）✓ |
| hl_liquidation_raw_empty (open) | 2 行（净增 1 行仍为测试行）✓ |
| top10_shareholders_incremental_starved (resolved) | 20260630=55,591 行 ✓ X-7 修复保持 |
| kline_etf_daily_shallow_depth (open) | 95,864 行/1,675 只、max 09-18 ✓（弃用判定+1min 聚合替代口径维持） |
| weather_data_sparse_31_days (accepted) | 31 记录日/9,073 行 ✓ 逐日积累中 |
| tick_coverage_etf_sparse_and_2022_2024_missing (open) | 2022-2024 年行数=0 ✓（但见 §0.B N3 新洞） |
| edb_data_ifind_quota_exhausted (accepted) | 0 行 ✓ |
| l2_tick_permission_required (accepted) | 0 行 ✓ |
| hk_connect_flow ×2 (accepted) | max 2024-08-16 / 4,052 行 ✓ |
| alt_movie_boxoffice_source_dead (open) | 表不存在 ✓（留痕口径正确） |
| kline_sector_concept_shrinking (mitigated) | 09-16..18 uniq(code)=594 稳定 ✓（串行错峰修复保持） |
| stock_basic_no_bse_universe (resolved) | 09-17/18 快照 5,565 只含北交所 344 ✓ |
| kline_minute_no_bse_universe (resolved) | kline_1min 近 4 日 9 开头=343/344 ✓ |
| kline_sector_intraday_tdx_dead (accepted) | 09-10 后 tdx 零行、synth_sh/eq 行在 ✓（合成冒充真值风险维持登记） |
| stock_indicator_circ_mv_outage + boundary_redup_wipe (resolved) | 09-15/16/17 circ_mv 非空 100% ✓（**但 09-18 半日 1,000/5,565，见 §3**） |
| kline_index_399106_breadth_stale (accepted) | 近 7 日 advance_count 非零=0 ✓ 结构性断供维持 |
| auction_window_pre_202606_gap（历史段部分） | FINAL 251,598 行/47 密集日 ✓（但前向累积已断，见 N6） |
| cold_archive_minute_kline_e_drive (open) | `E:/zephyr_cold_archive` 实体在盘 ✓（挂回工单 #367 仍待执行） |
| bt_trade_log_attribution_fields_missing (no_source) | 引擎级登记，本次不涉及 DB，维持 |

## 3. 反查新发现的其他卫生项（未登记，低-中危）

| # | 发现 | 证据 | 级别 |
|---|------|------|------|
| W1 | stock_basic **09-16 快照整日缺失**（09-15 双份 11,124、09-17/18 正常 5,565） | by_day 实测 | 已登记 accepted 家族（stock_basic_snapshot_days_missing）新发一次，建议扩 end_date 或加新条目 |
| W2 | stock_indicator **09-18 半日 1,000/5,565 行**（data_source=akshare；09-18 11:09 full_refresh 写 18,270 行后未再跑） | by_day + fetch_perf | P1 候选登记（fresh 缺口，周一 09-21 盘前消费受影响） |
| W3 | sector_fund_flow **09-19 周六写 450 行**（五时点任务未卡交易日历） | by_day | P2 卫生（周末快照入库，下游需过滤） |
| W4 | etf_list **84 行存活行 list_date=1970**（valid_to IS NULL；登记称"墓碑 0/list_date 全真值"） | FINAL countIf | P2 改册（月度刷新带回归或首跑漏段，82 只旧段+新 2 只待查） |
| W5 | index_list **22 行存活行 list_date=1970**（1,700 墓碑为设计内） | FINAL+valid_to 过滤 | P2 改册（新指数进料带哨兵日期） |
| W6 | judgment_* 判定台账四表近乎全空（0/2/3/4 行；sentinel 破防 judgment_plan_verification empty） | 实测 | P2 活性观察（与"98 黄灯接电"旧账同源，非新病） |
| W7 | c1_backtest.sim_* 平台族 max=09-17（sim 批作业随 final3 收口停滞） | R1 新鲜度 | P2 观察（归 final3 W8 眼界） |

## 4. 哨兵实测（supply_sentinel，55 腿 9 破防）

破防清单（全部复核为真阳性）：

| 表 | date_col | max | lag | 阈值 | 对应 |
|----|----------|-----|-----|------|------|
| alt_sz_reservoir_level | tdate | 07-31 | 51d | 5d | 注册表 monitoring ✓ |
| rate_decision_calendar | decision_date | 2025-10-30 | 325d | 75d | no_source ✓ |
| rate_decision_calendar（pboc 腿） | decision_date | 2019-11-20 | 2,496d | 90d | 同上维度腿 |
| futures_warehouse_receipt | trade_date | 2025-11-17 | 307d | 10d | SHFE 维度腿 ✓ |
| daily_valuation | trade_date | 09-19 | 低填充列 close/amount/turnover=0.0 | — | N2（列填充率腿抓到）✓ |
| index_valuation_daily | trade_date | 09-17 | 低填充列 cape_5y/pe_pct/erp=0.0 | — | N1（列填充率腿抓到）✓ |
| kline_sector_intraday | trade_date | 09-10 | 10d+行数地板 | 5d/10万 | accepted ✓ |
| dividend | announce_date | 07-01 | 81d | 30d | no_source ✓ |
| judgment_plan_verification | verified_at | 空表 | — | — | W6 |

**盲区（建议补哨兵行）**：index_quote、news_sentiment_window、auction_snapshot、tick_data
（四表无阈值行）；且 tick_data 09-17 洞证明 max-date 哨兵对**内部洞**原理性失明——需要
"日历逐日 diff"类检查（本班反查逻辑可固化为该检查：`generate_expected_dates vs actual`）。

## 5. fetch_perf 归因速查（09-16→09-20）

| 任务族 | 09-16 | 09-17 | 09-18 | 09-19 | 09-20 | 结论 |
|--------|-------|-------|-------|-------|-------|------|
| index_quote_snapshot(miniqmt) | 10 次 SUCCESS | 0 | 0 | 0 | 0 | 随 miniQMT 死，替代 EOD 任务无记录（N4） |
| auction_*(qmt_bridge) | 132 次 | 5 次 FAILED(10038/连接冷却) | 6 次 FAILED | 0 | 0 | 派生链坏（N6） |
| nightly_sentiment | —（无痕，内部直写） | 表停 09-14 | 停 | 停 | 停 | 静默失败（N5） |
| daily_valuation_incremental | mock×8 rows=0 | mock×7 | mock×4 | mock×3 | — | 空转假绿（N2） |
| stock_indicator_full_refresh(akshare) | — | 1 | 1（18,270 行，11:09） | 0 | 0 | 09-18 后未再跑（W2） |
| news_* 8 族 | 全活 | 全活 | 全活 | 全活 | 活 | 对照组：新闻管线健康 |

## 6. 复验命令示例

```bash
# N1 复验（FINAL 派生列全零）
# SELECT countIf(cape_5y IS NULL), countIf(erp IS NULL), count() FROM c1_market.index_valuation_daily FINAL
# N3 复验（09-17 双黑）
# SELECT trade_date, count() FROM c1_market.tick_data WHERE trade_date='2026-09-17'          -- 0
# SELECT count() FROM c1_market.tick_depth_5 WHERE trade_date='2026-09-17'                   -- 0
# 哨兵复验
python -c "import sys; sys.path.insert(0,r'D:\ZephyrAlpha\src'); \
from zephyr.data.supply_sentinel import check_tables; \
r=check_tables(); print(r['checked'], r['breached'])"
```

## 7. 未覆盖与原因

- tasks.yaml 逐任务启停核对（避让清单禁改 tasks.yaml；读也未逐条做——归因已用 fetch_perf 侧写）。
- resolved/completed 条目中 21 条仅做弱抽验（历史口径已在 09-18 st-ff-datagap 全量复核过，
  本班按"两天窗口内无新写异常"原则降频，不重复他人亲验）。
- 消费端影响量化（哪些因子/策略吃到 N1/N2 脏数）——属下游排查，本班只标"金融字段消费禁用"提示。
